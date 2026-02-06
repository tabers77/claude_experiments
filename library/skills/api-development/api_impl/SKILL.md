# Skill: api_impl

**Purpose**: Implement inference endpoints consistently

**Use when**:
- Adding new API endpoints
- Need consistent patterns (models, errors, logging, config)
- Docker/runtime requirements apply

---

## Process

When implementing an inference endpoint:

1) **Ask for required information**:
   - Route path
   - Request schema
   - Response schema
   - Latency budget
   - Model/service location

2) **Ensure implementation includes**:
   - Request/response Pydantic models
   - Input validation + clear error messages
   - Structured logs + trace IDs
   - Timeouts, retries if calling downstream services
   - Health check consideration

3) **Provide deliverables**:
   - Handler code
   - Unit tests
   - Update to OpenAPI/docs
   - Docker/runtime notes if needed

4) **End with "how to test locally" commands**

---

## Output Format

```
## API Implementation: [Route]

### Specification
- **Route**: [METHOD /path]
- **Request**: [schema summary]
- **Response**: [schema summary]
- **Latency budget**: [target]

### Models

```python
# Request model
class [Name]Request(BaseModel):
    ...

# Response model
class [Name]Response(BaseModel):
    ...
```

### Handler

```python
@router.[method]("[path]")
async def [handler_name](...):
    ...
```

### Tests

```python
def test_[name]_success():
    ...

def test_[name]_validation_error():
    ...
```

### OpenAPI Update
[Any documentation changes needed]

### Runtime Notes
- [Docker considerations]
- [Environment variables]
- [Dependencies]

### Test Locally
```bash
# Start server
[command]

# Test endpoint
curl -X [METHOD] http://localhost:8000/[path] ...
```
```

---

## Example Usage

```
/api_impl
Route: /predict/sentiment
Request: {"text": str}
Response: {"sentiment": str, "confidence": float}
Latency: <200ms p95
```

Or:

```
/api_impl
Route: POST /api/v1/embeddings
Request: {"texts": list[str], "model": str}
Response: {"embeddings": list[list[float]]}
Latency: <500ms for batch of 10
```
