# Task 3: Add User Validation Layer

## Dependencies
- Previous tasks: 1
- Must complete before: none

## Parallelizable
- Can run in parallel with: Task 2, Task 4, Task 5

## Implementation

After task 1 completes, add comprehensive validation to the user model.

**Depends on Task 1** (requires user model to exist)

**Files to modify:**
- `src/models/user.ts` - Add validation methods
- `src/models/user.test.ts` - Add validation tests

**Requirements:**
- Email format validation
- Password strength validation (min 8 chars, special char, number)
- Username validation (alphanumeric, 3-20 chars)
- Duplicate email detection

**Tests:**
- Rejects weak passwords
- Rejects invalid email formats
- Rejects invalid usernames
- Prevents duplicate emails

## Files to Modify
- src/models/user.ts

## Verification Checklist
- [ ] Implementation complete
- [ ] Tests written (TDD - test first!)
- [ ] All tests pass
- [ ] Lint/type check clean
- [ ] Code review requested
- [ ] Code review passed
