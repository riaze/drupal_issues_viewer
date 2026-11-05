"""HTTP server: HTML frontend on GET / and JSON REST on GET /api/issues."""

from __future__ import annotations

import json
import logging
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from typing import Any
from urllib.parse import parse_qs, urlparse

from drupal_issues_viewer.client import fetch_issues
from drupal_issues_viewer.render import render_frontend

logger = logging.getLogger(__name__)

_SECURITY_HEADERS = (
    ("X-Content-Type-Options", "nosniff"),
    ("X-Frame-Options", "DENY"),
    ("Referrer-Policy", "no-referrer"),
    ("Cache-Control", "no-store"),
)


def parse_page(query: dict[str, list[str]]) -> int:
    try:
        return max(int(query.get("page", ["0"])[0]), 0)
    except (ValueError, TypeError, IndexError):
        return 0


class DrupalIssuesHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        parsed = urlparse(self.path)
        page = parse_page(parse_qs(parsed.query))

        routes = {
            "/": self._handle_frontend,
            "/index.html": self._handle_frontend,
            "/api/issues": self._handle_issues_api,
            "/health": self._handle_health,
        }
        handler = routes.get(parsed.path)
        if handler is None:
            self._send_json(404, {"error": "Endpoint not found"})
            return
        handler(page)

    def _handle_health(self, _page: int) -> None:
        self._send_json(200, {"status": "ok"})

    def _handle_frontend(self, page: int) -> None:
        try:
            body = render_frontend(fetch_issues(page)).encode("utf-8")
        except Exception:
            logger.exception("Failed to render issues page=%s", page)
            self._send_json(502, {"error": "Failed to load issues"})
            return
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self._write_security_headers()
        self.end_headers()
        self.wfile.write(body)

    def _handle_issues_api(self, page: int) -> None:
        try:
            self._send_json(200, fetch_issues(page))
        except Exception:
            logger.exception("Failed to fetch issues page=%s", page)
            self._send_json(502, {"error": "Failed to load issues"})

    def _send_json(self, status_code: int, data: dict[str, Any]) -> None:
        body = json.dumps(data).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self._write_security_headers()
        self.end_headers()
        self.wfile.write(body)

    def _write_security_headers(self) -> None:
        for name, value in _SECURITY_HEADERS:
            self.send_header(name, value)

    def log_message(self, format: str, *args: Any) -> None:
        logger.info("%s - %s", self.client_address[0], format % args)


def serve(host: str, port: int) -> None:
    server = ThreadingHTTPServer((host, port), DrupalIssuesHandler)
    logger.info("Listening on http://%s:%s", host, port)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        logger.info("Shutting down")
    finally:
        server.server_close()
