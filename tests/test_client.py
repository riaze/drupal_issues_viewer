import unittest

from drupal_issues_viewer.client import normalize_issue, summarize
from drupal_issues_viewer.mappings import ISSUE_STATUS, label
from drupal_issues_viewer.render import render_frontend
from drupal_issues_viewer.server import parse_page


class LabelTests(unittest.TestCase):
    def test_known_status(self):
        self.assertEqual(label(ISSUE_STATUS, "8"), "needs review")

    def test_none_falls_back(self):
        self.assertEqual(label(ISSUE_STATUS, None), "unknown")

    def test_unknown_keeps_raw_value(self):
        self.assertEqual(label(ISSUE_STATUS, "99"), "99")


class SummarizeTests(unittest.TestCase):
    def test_strips_tags_and_collapses_space(self):
        body = {"value": "<p>Hello<br/>world</p>"}
        self.assertEqual(summarize(body), "Hello world")

    def test_truncates(self):
        body = {"value": "a" * 50}
        self.assertEqual(summarize(body, limit=10), "aaaaaaaaaa…")

    def test_missing_body(self):
        self.assertEqual(summarize(None), "")


class NormalizeTests(unittest.TestCase):
    def test_maps_fields(self):
        node = {
            "nid": "42",
            "title": "Broken form",
            "url": "https://www.drupal.org/node/42",
            "field_issue_status": "13",
            "field_issue_priority": "400",
            "field_project": {"id": "3060"},
            "body": {"value": "<p>Something broke.</p>"},
        }
        self.assertEqual(
            normalize_issue(node),
            {
                "id": "42",
                "title": "Broken form",
                "url": "https://www.drupal.org/node/42",
                "status": "needs work",
                "priority": "critical",
                "project_id": "3060",
                "summary": "Something broke.",
            },
        )

    def test_untitled_when_title_missing(self):
        self.assertEqual(normalize_issue({})["title"], "Untitled")


class ParsePageTests(unittest.TestCase):
    def test_default_is_zero(self):
        self.assertEqual(parse_page({}), 0)

    def test_negative_clamped(self):
        self.assertEqual(parse_page({"page": ["-3"]}), 0)

    def test_invalid_is_zero(self):
        self.assertEqual(parse_page({"page": ["abc"]}), 0)


class RenderTests(unittest.TestCase):
    def test_pager_appears_in_header_and_footer(self):
        html = render_frontend(
            {
                "page": 2,
                "count": 1,
                "has_next": True,
                "items": [
                    {
                        "id": "1",
                        "title": "One",
                        "url": "https://example.com/1",
                        "status": "needs review",
                        "priority": "normal",
                        "summary": "Hi",
                    }
                ],
            }
        )
        self.assertEqual(html.count('href="/?page=1"'), 2)
        self.assertEqual(html.count('href="/?page=3"'), 2)
        self.assertIn("Footer pagination", html)


if __name__ == "__main__":
    unittest.main()
