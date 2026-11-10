"""Export Drupal issues to CSV and Excel XML (.xls) formats."""

from __future__ import annotations

import csv
import html
import io
from typing import Any

CSV_COLUMNS = (
    ("id", "Issue ID"),
    ("title", "Title"),
    ("status", "Status"),
    ("priority", "Priority"),
    ("project_id", "Project ID"),
    ("url", "URL"),
    ("summary", "Summary"),
)

# Cells starting with these characters are interpreted as formulas by spreadsheet apps.
_FORMULA_PREFIXES = ("=", "+", "-", "@", "\t", "\r")


def _csv_cell(value: Any) -> str:
    text = str(value or "")
    return f"'{text}" if text.startswith(_FORMULA_PREFIXES) else text


def issues_to_csv(items: list[dict[str, Any]]) -> str:
    """Generate a CSV string (with header row) from an issues list."""
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow([header for _, header in CSV_COLUMNS])
    for item in items:
        writer.writerow([_csv_cell(item.get(key)) for key, _ in CSV_COLUMNS])
    return buf.getvalue()


