# Drupal Issues Viewer

A small Python HTTP server that fetches public project issues from [Drupal.org](https://www.drupal.org/) and serves them as a paginated HTML page and a JSON API.

It calls the Drupal.org REST endpoint (`/api-d7/node.json`), normalizes each issue (id, title, status, priority, summary, URL), then renders cards in the browser.

## Features

- HTML frontend at `/` with previous/next paging
- JSON REST endpoint at `/api/issues`
- Excel spreadsheet export at `/export/issues.xls`
- CSV download at `/export/issues.csv`
- Health check at `/health`
- In-memory TTL caching (default: 60s, configurable via `DRUPAL_CACHE_TTL`)
- Status and priority filtering and text search
- Status and priority labels mapped from Drupal field IDs
- Short HTML-stripped summaries for each issue

## Requirements

- Python 3.10+
- [`requests`](https://pypi.org/project/requests/)

## Setup

```bash
python3 -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Run

```bash
python drupal_issues.py
# or
python -m drupal_issues_viewer
```

Then open [http://127.0.0.1:8000](http://127.0.0.1:8000). Stop the server with `Ctrl+C`.

Optional flags:

```bash
python -m drupal_issues_viewer --host 127.0.0.1 --port 8000 --log-level INFO
```

`HOST` and `PORT` environment variables are also accepted.

## Tests

```bash
python -m unittest discover -s tests -v
```

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | HTML list of issues. Query: `?page=1&status=8&priority=400&q=keyword` |
| `GET` | `/api/issues` | JSON list of issues. Query: `?page=1&status=8&priority=400&q=keyword` |
| `GET` | `/export/issues.xls` | Download filtered issues as Excel (.xls). Query: `?page=1` |
| `GET` | `/export/issues.csv` | Download filtered issues as CSV. Query: `?page=1&status=8&priority=400&q=keyword` |
| `GET` | `/health` | Liveness probe |

### Filters

- `page`: Page number (starts at `1`)
- `status`: Drupal issue status ID (e.g. `8` for *needs review*, `13` for *needs work*, `1` for *active*)
- `priority`: Drupal issue priority ID (e.g. `400` for *critical*, `300` for *major*, `200` for *normal*)
- `q`: Keyword search across issue title and summary text

### JSON example

```http
GET /api/issues?page=1
```

```json
{
  "page": 1,
  "count": 50,
  "has_next": true,
  "items": [
    {
      "id": "123456",
      "title": "Example issue",
      "url": "https://www.drupal.org/project/drupal/issues/123456",
      "status": "needs review",
      "priority": "normal",
      "project_id": "3060",
      "summary": "Short description of the issue…"
    }
  ]
}
```

Unknown paths return `404` with `{"error": "Endpoint not found"}`. Failures talking to Drupal.org return `502`.

## Project layout

```
drupal-issues-viewer/
├── drupal_issues.py              # convenience launcher
├── drupal_issues_viewer/         # application package
│   ├── client.py                 # Drupal.org fetch + normalize
│   ├── config.py
│   ├── mappings.py
│   ├── render.py
│   └── server.py
├── templates/
│   └── index.html
├── tests/
├── pyproject.toml
├── requirements.txt
└── README.md
```

## License

Use and modify freely for your own projects.
