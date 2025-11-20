# Task 17: Create /cc:save command

## Dependencies
- Previous tasks: 1, 2, 3
- Must complete before: none

## Parallelizable
- Can run in parallel with: Task 4, Task 5, Task 6, Task 7, Task 8, Task 9, Task 10, Task 11, Task 12, Task 13, Task 14, Task 15, Task 16, Task 18, Task 19, Task 20, Task 21, Task 22, Task 23, Task 24

## Implementation

**Files:**
- Create: `cc/commands/cc/save.md`

**Step 1: Write command file**

Create `cc/commands/cc/save.md`:

```markdown
Use the state-persistence skill to save workflow state to Serena MCP memory.

**Prerequisites:** At least one of:
- Brainstorm + research completed
- Plan file exists
- Execution in progress
- Execution complete

**What this does:**

**Stage Detection (automatic):**
- Analyzes current workflow state
- Determines stage: research, planning, execution, or complete
- Extracts feature name from plan or brainstorm
- Collects git metadata (commit, branch)

**Saves to:** \`YYYY-MM-DD-<feature-name>-<stage>.md\`

**Stage-specific content:**

**research.md** - After research completes
- Brainstorm summary
- Codebase findings (Serena)
- Library docs (Context7)
- Web research
- GitHub research

**planning.md** - During plan writing
- Design decisions
- Alternatives considered
- Plan draft
- Open questions

**execution.md** - During implementation
- Progress summary (X/Y tasks complete)
- Completed tasks
- Current task state
- Blockers/issues

**complete.md** - After workflow completion
- What was built
- Key learnings and gotchas
- Files modified
- Patterns introduced
- Recommendations

**Resume later with:** \`/cc:resume <filename>\`
```

**Step 2: Verify file created**

```bash
cat cc/commands/cc/save.md
```

Expected: Command content visible

**Step 3: Commit**

```bash
git add cc/commands/cc/save.md
git commit -m "feat: add /cc:save command"
```

## Files to Modify
- cc/commands/cc/save.md

## Verification Checklist
- [ ] Implementation complete
- [ ] Tests written (TDD - test first!)
- [ ] All tests pass
- [ ] Lint/type check clean
- [ ] Code review requested
- [ ] Code review passed
