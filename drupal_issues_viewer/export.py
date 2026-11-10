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


def issues_to_xls(items: list[dict[str, Any]], page: int = 1) -> str:
    """Generate an Excel 2003 XML spreadsheet string from issues list."""
    rows = []
    # Header row
    rows.append(
        """      <Row ss:StyleID="Header">
        <Cell><Data ss:Type="String">Issue ID</Data></Cell>
        <Cell><Data ss:Type="String">Title</Data></Cell>
        <Cell><Data ss:Type="String">Status</Data></Cell>
        <Cell><Data ss:Type="String">Priority</Data></Cell>
        <Cell><Data ss:Type="String">Project ID</Data></Cell>
        <Cell><Data ss:Type="String">URL</Data></Cell>
        <Cell><Data ss:Type="String">Summary</Data></Cell>
      </Row>"""
    )

    for item in items:
        issue_id = html.escape(str(item.get("id") or ""))
        title = html.escape(str(item.get("title") or ""))
        status = html.escape(str(item.get("status") or ""))
        priority = html.escape(str(item.get("priority") or ""))
        project_id = html.escape(str(item.get("project_id") or ""))
        url = html.escape(str(item.get("url") or ""))
        summary = html.escape(str(item.get("summary") or ""))

        rows.append(
            f"""      <Row>
        <Cell><Data ss:Type="String">{issue_id}</Data></Cell>
        <Cell><Data ss:Type="String">{title}</Data></Cell>
        <Cell><Data ss:Type="String">{status}</Data></Cell>
        <Cell><Data ss:Type="String">{priority}</Data></Cell>
        <Cell><Data ss:Type="String">{project_id}</Data></Cell>
        <Cell><Data ss:Type="String">{url}</Data></Cell>
        <Cell><Data ss:Type="String">{summary}</Data></Cell>
      </Row>"""
        )

    rows_xml = "\n".join(rows)

    return f"""<?xml version="1.0" encoding="UTF-8"?>
        <?mso-application progid="Excel.Sheet"?>
        <Workbook xmlns="urn:schemas-microsoft-com:office:spreadsheet"
        xmlns:o="urn:schemas-microsoft-com:office:office"
        xmlns:x="urn:schemas-microsoft-com:office:excel"
        xmlns:ss="urn:schemas-microsoft-com:office:spreadsheet"
        xmlns:html="http://www.w3.org/TR/REC-html40">
        <Styles>
        <Style ss:ID="Default" ss:Name="Normal">
        <Alignment ss:Vertical="Center"/>
        <Borders/>
        <Font ss:FontName="Calibri" ss:Size="11" ss:Color="#000000"/>
        </Style>
        <Style ss:ID="Header">
        <Alignment ss:Vertical="Center" ss:Bold="1"/>
        <Interior ss:Color="#0678BE" ss:Pattern="Solid"/>
        <Font ss:FontName="Calibri" ss:Size="11" ss:Color="#FFFFFF" ss:Bold="1"/>
        </Style>
        </Styles>
        <Worksheet ss:Name="Page {page}">
        <Table>
        <Column ss:Width="70"/>
        <Column ss:Width="250"/>
        <Column ss:Width="100"/>
        <Column ss:Width="80"/>
        <Column ss:Width="80"/>
        <Column ss:Width="250"/>
        <Column ss:Width="300"/>
        {rows_xml}
        </Table>
        </Worksheet>
        </Workbook>"""  
