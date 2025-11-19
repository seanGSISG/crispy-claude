# Task 1: Implement User Model

## Dependencies
- Previous tasks: none
- Must complete before: 3

## Parallelizable
- Can run in parallel with: Task 2, Task 4, Task 5

## Implementation

Create the user model with validation and password hashing.

**Files to create/modify:**
- `src/models/user.ts` - User interface and schema
- `src/models/user.test.ts` - User model tests

**Requirements:**
- User interface with id, email, password fields
- Password hashing using bcrypt
- Email validation
- Timestamps (createdAt, updatedAt)

**Tests:**
- User creation with valid data
- Password hashing on save
- Email validation rejects invalid emails
- Timestamps are automatically set

**Independent task - can run in parallel with other setup tasks**

## Files to Modify
- src/models/user.ts

## Verification Checklist
- [ ] Implementation complete
- [ ] Tests written (TDD - test first!)
- [ ] All tests pass
- [ ] Lint/type check clean
- [ ] Code review requested
- [ ] Code review passed
