# [Project Name]

## Purpose
[One-line description of what this project does]

## How to Run

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt

# Run the server
uvicorn src.main:app --reload

# Run tests
pytest

# Run linter
ruff check src/

# Run type checker
mypy src/
```

## Project Structure

```
src/
├── main.py           # FastAPI entrypoint
├── api/
│   ├── routes/       # Endpoint handlers
│   └── middleware/   # Request processing
├── core/
│   ├── config.py     # Configuration
│   └── security.py   # Auth utilities
├── db/
│   ├── models.py     # Database models
│   └── database.py   # Connection handling
└── utils/            # Helper functions
```

## Conventions

### API
- Routes follow REST conventions
- All responses use standard format
- Errors include error codes

### Code Style
- Type hints required
- Docstrings for public functions
- Run ruff before committing

### Testing
- Tests mirror src structure
- Use pytest fixtures
- Mock external services

## Invariants

1. **API contracts** - Don't change response schemas without versioning
2. **Auth required** - All endpoints except health check require auth
3. **Logging** - All errors must be logged with request context

## See Also
- `.claude/rules/api.md` - API conventions
- `.claude/rules/security.md` - Security rules
