"""Fetch and normalize Drupal.org project issues."""

from __future__ import annotations

import html
import logging
import re
import threading
import time
from typing import Any

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from drupal_issues_viewer.config import (
    CACHE_TTL,
    DRUPAL_ISSUES_URL,
    REQUEST_TIMEOUT,
    SUMMARY_LIMIT,
    USER_AGENT,
)
from drupal_issues_viewer.mappings import ISSUE_PRIORITY, ISSUE_STATUS, label

logger = logging.getLogger(__name__)

_TAG_RE = re.compile(r"<[^>]+>")


def create_session() -> requests.Session:
    session = requests.Session()
    retry = Retry(
        total=3,
        backoff_factor=0.4,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=frozenset({"GET"}),
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    session.headers.update(
        {
            "User-Agent": USER_AGENT,
            "Accept": "application/json",
        }
    )
    return session


_session = create_session()


class TTLCache:
    """Thread-safe in-memory cache with time-to-live expiration."""

    def __init__(self, ttl: int = CACHE_TTL) -> None:
        self.ttl = ttl
        self._cache: dict[tuple[Any, ...], tuple[float, dict[str, Any]]] = {}
        self._lock = threading.Lock()

    def get(self, key: tuple[Any, ...]) -> dict[str, Any] | None:
        with self._lock:
            entry = self._cache.get(key)
            if entry is None:
                return None
            timestamp, data = entry
            if time.time() - timestamp > self.ttl:
                del self._cache[key]
                return None
            return data

    def set(self, key: tuple[Any, ...], data: dict[str, Any]) -> None:
        with self._lock:
            self._cache[key] = (time.time(), data)

    def clear(self) -> None:
        with self._lock:
            self._cache.clear()


_cache = TTLCache()


def clear_cache() -> None:
    """Clear in-memory cache entries."""
    _cache.clear()


def summarize(body: object, limit: int = SUMMARY_LIMIT) -> str:
    if not isinstance(body, dict):
        return ""
    text = body.get("value") or body.get("summary") or ""
    if not isinstance(text, str):
        return ""
    text = html.unescape(text)
    text = _TAG_RE.sub(" ", text)
    compact = " ".join(text.split())
    if len(compact) > limit:
        return compact[:limit].rstrip() + "…"
    return compact


def normalize_issue(node: dict[str, Any]) -> dict[str, Any]:
    """Turn one Drupal node into a small, frontend-friendly dict."""
    project = node.get("field_project") or {}
    project_id = project.get("id") if isinstance(project, dict) else None
    return {
        "id": node.get("nid"),
        "title": node.get("title") or "Untitled",
        "url": node.get("url") or "",
        "status": label(ISSUE_STATUS, node.get("field_issue_status")),
        "priority": label(ISSUE_PRIORITY, node.get("field_issue_priority")),
        "project_id": project_id,
        "summary": summarize(node.get("body")),
    }


def fetch_issues(
    page: int = 1,
    status: str | None = None,
    priority: str | None = None,
    query: str | None = None,
    session: requests.Session | None = None,
    use_cache: bool = True,
) -> dict[str, Any]:
    """GET Drupal issues for a single page with optional status, priority, and keyword filters."""
    normalized_q = query.strip() if query else None
    cache_key = (page, status, priority, normalized_q)
    if use_cache:
        cached = _cache.get(cache_key)
        if cached is not None:
            logger.debug("Cache hit for key=%s", cache_key)
            return cached

    http = session or _session
    logger.info("Fetching Drupal issues page=%s status=%s priority=%s query=%s", page, status, priority, normalized_q)
    drupal_page = max(page - 1, 0)
    params: dict[str, Any] = {"type": "project_issue", "page": drupal_page}
    if status:
        params["field_issue_status"] = status
    if priority:
        params["field_issue_priority"] = priority

    response = http.get(
        DRUPAL_ISSUES_URL,
        params=params,
        timeout=REQUEST_TIMEOUT,
    )
    response.raise_for_status()
    payload = response.json()

    items = [normalize_issue(node) for node in payload.get("list") or []]
    if normalized_q:
        needle = normalized_q.lower()
        items = [
            it for it in items
            if needle in str(it.get("title", "")).lower() or needle in str(it.get("summary", "")).lower()
        ]

    result = {
        "page": page,
        "count": len(items),
        "has_next": bool(payload.get("next")),
        "status": status or "",
        "priority": priority or "",
        "query": normalized_q or "",
        "items": items,
    }
    if use_cache:
        _cache.set(cache_key, result)
    return result
