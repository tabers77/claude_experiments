# Test Project

## Purpose

A minimal FastAPI application used to verify that library skills work correctly.

## How to Run

```bash
# Install
pip install -r requirements.txt

# Run server
uvicorn src.main:app --reload

# Run tests
pytest

# Run single test
pytest tests/test_routes.py -v
```

## Structure

```
test_project/
├── src/
│   ├── main.py           # FastAPI app
│   ├── api/routes.py     # CRUD endpoints
│   └── utils/helpers.py  # Utility functions
└── tests/
    └── test_routes.py    # API tests
```

## Endpoints

- `GET /` - Health check
- `GET /api/items` - List items
- `GET /api/items/{id}` - Get item
- `POST /api/items` - Create item
- `DELETE /api/items/{id}` - Delete item

## Invariants

1. All endpoints return JSON
2. 404 for missing items
3. 201 for created items

## Testing Skills

Use this project to test:
- `/arch` - Map the structure
- `/project_review` - Assess quality
- `/api_impl` - Add new endpoint
- `/refactor_safe` - Modify existing code
