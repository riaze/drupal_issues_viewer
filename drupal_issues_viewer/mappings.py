"""Drupal.org field IDs for issue status and priority."""

ISSUE_STATUS = {
    "1": "active",
    "2": "fixed",
    "3": "closed (duplicate)",
    "4": "postponed",
    "5": "closed (won't fix)",
    "6": "closed (works as designed)",
    "7": "closed (fixed)",
    "8": "needs review",
    "13": "needs work",
    "14": "reviewed & tested",
    "15": "patch (to be ported)",
    "16": "needs more info",
    "17": "closed (outdated)",
    "18": "closed (cannot reproduce)",
}

ISSUE_PRIORITY = {
    "400": "critical",
    "300": "major",
    "200": "normal",
    "100": "minor",
}


def label(mapping: dict[str, str], value: object, fallback: str = "unknown") -> str:
    if value is None:
        return fallback
    return mapping.get(str(value), str(value))
