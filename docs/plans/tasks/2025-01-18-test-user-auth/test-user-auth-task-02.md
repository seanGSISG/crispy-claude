# Task 2: Implement Logger Service

## Dependencies
- Previous tasks: none
- Must complete before: none

## Parallelizable
- Can run in parallel with: Task 1, Task 3, Task 4, Task 5

## Implementation

Create a logging service for authentication events.

**Files to create/modify:**
- `src/services/logger.ts` - Logger implementation
- `src/services/logger.test.ts` - Logger tests

**Requirements:**
- Log levels: debug, info, warn, error
- Structured logging with timestamps
- Log authentication events (login, logout, failures)
- Environment-based log level configuration

**Tests:**
- Logs messages at different levels
- Includes timestamps in log output
- Respects configured log level

**Independent task - can run in parallel with task 1**

## Files to Modify
- src/services/logger.ts

## Verification Checklist
- [ ] Implementation complete
- [ ] Tests written (TDD - test first!)
- [ ] All tests pass
- [ ] Lint/type check clean
- [ ] Code review requested
- [ ] Code review passed
