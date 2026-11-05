"""HTML rendering for the issues list."""

from __future__ import annotations

import html
import re
from string import Template
from typing import Any

from drupal_issues_viewer.config import TEMPLATE_PATH

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


def render_frontend(data: dict[str, Any], template_path=TEMPLATE_PATH) -> str:
    template = Template(template_path.read_text(encoding="utf-8"))
    page = data["page"]
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
        items_html="".join(cards) or "<p>No issues found.</p>",
        prev_link=_nav_link("Previous", f"/?page={page - 1}" if page > 0 else None),
        next_link=_nav_link("Next", f"/?page={page + 1}" if data["has_next"] else None),
    )
