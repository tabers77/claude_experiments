# Style Rules

## Code Formatting
- Use project formatter (ruff/black)
- Line length: 88-100 characters
- Run formatter before commit

## Naming Conventions
- Functions/variables: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- Private: prefix with `_`

## Type Hints
- Required for function signatures
- Use `Optional[]` for nullable
- Use `list[]`, `dict[]` (Python 3.9+)

## Imports
- Standard library first
- Third-party second
- Local imports third
- Sorted alphabetically within groups

## Documentation
- Docstrings for public functions
- Comments for non-obvious logic
- Keep comments up to date with code

## File Organization
- One class per file (generally)
- Related functions grouped together
- Constants at top of file
