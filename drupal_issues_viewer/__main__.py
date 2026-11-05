"""CLI entry: python -m drupal_issues_viewer"""

from __future__ import annotations

import argparse
import logging

from drupal_issues_viewer.config import HOST, PORT
from drupal_issues_viewer.server import serve


def main() -> None:
    parser = argparse.ArgumentParser(description="Drupal.org issues viewer")
    parser.add_argument("--host", default=HOST, help="Bind address (default: %(default)s)")
    parser.add_argument("--port", type=int, default=PORT, help="Bind port (default: %(default)s)")
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=("DEBUG", "INFO", "WARNING", "ERROR"),
    )
    args = parser.parse_args()
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    serve(args.host, args.port)


if __name__ == "__main__":
    main()
