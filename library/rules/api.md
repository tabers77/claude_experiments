# API Rules

## Endpoint Conventions
- RESTful naming: `/api/v1/[resource]`
- Use proper HTTP methods (GET, POST, PUT, DELETE)
- Return appropriate status codes

## Request/Response
- Use Pydantic models for validation
- Consistent error response format:
  ```json
  {"error": {"code": "ERROR_CODE", "message": "Human readable"}}
  ```
- Include request IDs for tracing

## Documentation
- All endpoints must have docstrings
- OpenAPI schema must be accurate
- Include example requests/responses

## Error Handling
- Catch specific exceptions
- Log errors with context
- Don't leak internal details to clients

## Performance
- Set appropriate timeouts
- Use async where beneficial
- Consider pagination for list endpoints
