"""HTML rendering for the issues list."""

from __future__ import annotations

import html
import re
from string import Template
from typing import Any
from urllib.parse import urlencode

from drupal_issues_viewer.config import TEMPLATE_PATH
from drupal_issues_viewer.mappings import ISSUE_PRIORITY, ISSUE_STATUS

_SLUG_RE = re.compile(r"[^a-z0-9]+")

_CARD = Template(
    """
            <article class="issue">
              <div class="issue-meta">
                <span class="tag id">#$issue_id</span>
                <span class="tag status status-$status_slug">$status</span>
                <span class="tag priority priority-$priority_slug">$priority</span>
              </div>
              <h2><a href="$url" target="_blank" rel="noopener">$title</a></h2>
              <p class="summary">$summary</p>
            </article>
    """
)


def _slug(value: str) -> str:
    return _SLUG_RE.sub("-", value.lower()).strip("-") or "unknown"


def _nav_link(label: str, href: str | None) -> str:
    safe_label = html.escape(label)
    if href:
        return (
            f'<a class="btn" href="{html.escape(href, quote=True)}">'
            f"{safe_label}</a>"
        )
    return f'<span class="btn" aria-disabled="true">{safe_label}</span>'


def _options(mapping: dict[str, str], selected: str | None) -> str:
    parts = ['<option value="">All</option>']
    for key, val in mapping.items():
        is_sel = ' selected' if selected and str(selected) == str(key) else ''
        parts.append(f'<option value="{html.escape(key)}"{is_sel}>{html.escape(val)}</option>')
    return "\n".join(parts)


def render_frontend(data: dict[str, Any], template_path=TEMPLATE_PATH) -> str:
    template = Template(template_path.read_text(encoding="utf-8"))
    page = data["page"]
    status = data.get("status") or ""
    priority = data.get("priority") or ""
    query = data.get("query") or ""

    def make_url(p: int) -> str:
        q: dict[str, Any] = {"page": p}
        if status:
            q["status"] = status
        if priority:
            q["priority"] = priority
        if query:
            q["q"] = query
        return f"/?{urlencode(q)}"

    api_query = urlencode({k: v for k, v in [("page", page), ("status", status), ("priority", priority), ("q", query)] if v})

    cards = []
    for item in data["items"]:
        
        cards.append(
            _CARD.substitute(
                title=html.escape(str(item["title"])),
                url=html.escape(str(item["url"]), quote=True),
                status=html.escape(str(item["status"])),
                priority=html.escape(str(item["priority"])),
                summary=html.escape(str(item["summary"])),
                issue_id=html.escape(str(item["id"])),
                status_slug=_slug(str(item["status"])),
                priority_slug=_slug(str(item["priority"])),
            )
        )

    return template.safe_substitute(
        page=page,
        count=data["count"],
        status_options=_options(ISSUE_STATUS, status),
        priority_options=_options(ISSUE_PRIORITY, priority),
        query=html.escape(query, quote=True),
        api_query=api_query,
        items_html="".join(cards) or "<p>No issues found.</p>",
        prev_link=_nav_link("Previous", make_url(page - 1) if page > 1 else None),
        next_link=_nav_link("Next", make_url(page + 1) if data["has_next"] else None),
    )
