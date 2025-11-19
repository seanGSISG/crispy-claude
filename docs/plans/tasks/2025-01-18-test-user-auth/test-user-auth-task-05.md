# Task 5: Implement Authentication Endpoints

## Dependencies
- Previous tasks: 4
- Must complete before: none

## Parallelizable
- Can run in parallel with: Task 1, Task 2, Task 3

## Implementation

Requires tasks 1, 3, and 4 to be complete.

**Depends on Tasks 1, 3, and 4** (needs user model, validation, and JWT service)

**Files to create/modify:**
- `src/routes/auth.ts` - Authentication routes
- `src/routes/auth.test.ts` - Route tests
- `src/middleware/auth.ts` - Authentication middleware

**Requirements:**
- POST /auth/register - Register new user
- POST /auth/login - Login with email/password
- POST /auth/logout - Logout user
- GET /auth/me - Get current user (requires auth)
- Middleware to protect routes

**Tests:**
- Register creates new user
- Login returns JWT token
- Login fails with wrong password
- Protected routes require valid token
- Logout invalidates token

## Verification

After all tasks complete:
- [ ] All tests pass
- [ ] Lint/type check clean
- [ ] Manual testing: register → login → access protected route → logout
- [ ] Code review passed
- [ ] Documentation updated

## Files to Modify
- src/middleware/auth.ts
- src/routes/auth.ts

## Verification Checklist
- [ ] Implementation complete
- [ ] Tests written (TDD - test first!)
- [ ] All tests pass
- [ ] Lint/type check clean
- [ ] Code review requested
- [ ] Code review passed
