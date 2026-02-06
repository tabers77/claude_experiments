# Minimal API

A simple FastAPI application for practicing Claude Code features.

## Structure

```
minimal_api/
├── src/
│   ├── main.py           # FastAPI entrypoint
│   ├── api/
│   │   └── routes.py     # CRUD endpoints for items
│   └── utils/
│       └── helpers.py    # Utility functions
├── tests/
│   └── test_routes.py    # API tests
└── requirements.txt
```

## Setup

```bash
pip install -r requirements.txt
```

## Running

```bash
uvicorn src.main:app --reload
```

API will be available at http://localhost:8000

## Testing

```bash
pytest
```

## Endpoints

- `GET /` - Health check
- `GET /api/items` - List all items
- `GET /api/items/{id}` - Get item by ID
- `POST /api/items` - Create new item
- `DELETE /api/items/{id}` - Delete item
