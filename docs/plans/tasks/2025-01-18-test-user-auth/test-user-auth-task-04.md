# Task 4: Implement JWT Service

## Dependencies
- Previous tasks: none
- Must complete before: 5

## Parallelizable
- Can run in parallel with: Task 1, Task 2, Task 3

## Implementation

Create JWT token generation and validation service.

**Files to create/modify:**
- `src/services/jwt.ts` - JWT service implementation
- `src/services/jwt.test.ts` - JWT service tests
- `src/config/auth.ts` - Auth configuration

**Requirements:**
- Generate JWT tokens with user payload
- Validate JWT tokens
- Token expiration (24 hours)
- Refresh token support
- Secret key from environment

**Tests:**
- Generates valid JWT tokens
- Validates correct tokens
- Rejects expired tokens
- Rejects tampered tokens

**Independent task - can run in parallel with task 2**

## Files to Modify
- src/config/auth.ts
- src/services/jwt.ts

## Verification Checklist
- [ ] Implementation complete
- [ ] Tests written (TDD - test first!)
- [ ] All tests pass
- [ ] Lint/type check clean
- [ ] Code review requested
- [ ] Code review passed
