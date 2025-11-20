# Task 15: Create /cc:parse-plan command

## Dependencies
- Previous tasks: 1, 2, 3
- Must complete before: none

## Parallelizable
- Can run in parallel with: Task 4, Task 5, Task 6, Task 7, Task 8, Task 9, Task 10, Task 11, Task 12, Task 13, Task 14, Task 16, Task 17, Task 18, Task 19, Task 20, Task 21, Task 22, Task 23, Task 24

## Implementation

**Files:**
- Create: `cc/commands/cc/parse-plan.md`

**Step 1: Write command file**

Create `cc/commands/cc/parse-plan.md`:

```markdown
Use the decomposing-plans skill to break down a monolithic plan into parallel task files.

**Prerequisites:**
- Plan file exists: \`docs/plans/YYYY-MM-DD-<feature>.md\`
- Plan has 2+ tasks worth decomposing

**What this does:**
1. Reads the monolithic plan
2. Identifies parallelizable tasks
3. Creates task files in \`docs/plans/tasks/YYYY-MM-DD-<feature>/\`
4. Generates \`manifest.json\` with parallel batches
5. Prompts for next step: review or execute

**Output:**
- Task files: One per task
- Manifest: Defines batch execution order
- Enables parallel execution (up to 2 tasks per batch)

**Recommendation:** Always decompose plans with 4+ tasks for parallel execution.

**Next step:** Review plan or execute immediately
```

**Step 2: Verify file created**

```bash
cat cc/commands/cc/parse-plan.md
```

Expected: Command content visible

**Step 3: Commit**

```bash
git add cc/commands/cc/parse-plan.md
git commit -m "feat: add /cc:parse-plan command"
```

## Files to Modify
- cc/commands/cc/parse-plan.md

## Verification Checklist
- [ ] Implementation complete
- [ ] Tests written (TDD - test first!)
- [ ] All tests pass
- [ ] Lint/type check clean
- [ ] Code review requested
- [ ] Code review passed
