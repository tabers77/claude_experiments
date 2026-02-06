# Security Rules

## Secrets Management
- Never commit secrets to git
- Use environment variables for sensitive data
- Reference secrets via `CLAUDE.local.md`, not `CLAUDE.md`

## Input Validation
- Validate all external input
- Use Pydantic models for request validation
- Sanitize before database queries

## Authentication/Authorization
- Auth checks at API boundary
- Principle of least privilege
- Log auth failures

## Sensitive Paths
The following paths require extra review:
- `src/auth/` - Authentication logic
- `src/*/middleware/` - Request processing
- `migrations/` - Database changes
- `config/` - Configuration files

## Before Merging
- [ ] No hardcoded secrets
- [ ] Input validation present
- [ ] Auth checks verified
- [ ] Logging doesn't leak sensitive data
