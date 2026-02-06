# Testing Rules

## Test Structure
- Unit tests in `tests/unit/`
- Integration tests in `tests/integration/`
- Test files named `test_*.py`

## Test Conventions
- One assertion concept per test
- Descriptive test names: `test_[what]_[condition]_[expected]`
- Use fixtures for common setup
- Mock external dependencies

## Coverage Expectations
- Critical paths: 90%+
- Happy paths: covered
- Error paths: covered
- Edge cases: documented if not tested

## Commands
```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src

# Run specific test file
pytest tests/test_[name].py
```
