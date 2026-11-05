"""Runtime configuration. Environment variables override defaults."""

from __future__ import annotations

import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_PATH = Path(
    os.environ.get("DRUPAL_TEMPLATE_PATH", BASE_DIR / "templates" / "index.html")
)
DRUPAL_ISSUES_URL = os.environ.get(
    "DRUPAL_ISSUES_URL", "https://www.drupal.org/api-d7/node.json"
)
REQUEST_TIMEOUT = int(os.environ.get("DRUPAL_TIMEOUT", "20"))
HOST = os.environ.get("HOST", "127.0.0.1")
PORT = int(os.environ.get("PORT", "8000"))
USER_AGENT = os.environ.get("DRUPAL_USER_AGENT", "drupal-issues-viewer/1.0")
SUMMARY_LIMIT = int(os.environ.get("DRUPAL_SUMMARY_LIMIT", "220"))
