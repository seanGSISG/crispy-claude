# Task 23: Update executing-plans skill

## Dependencies
- Previous tasks: none
- Must complete before: none

## Parallelizable
- Can run in parallel with: Task 1, Task 2, Task 3, Task 4, Task 5, Task 6, Task 7, Task 8, Task 9, Task 10, Task 11, Task 12, Task 13, Task 14, Task 15, Task 16, Task 17, Task 18, Task 19, Task 20, Task 21, Task 22, Task 24

## Implementation

**Files:**
- Modify: `cc/skills/executing-plans/SKILL.md`

**Step 1: Read current skill**

```bash
head -100 cc/skills/executing-plans/SKILL.md
```

Expected: See beginning of executing-plans skill

**Step 2: Update execution strategy section**

Find the execution strategy section and update it to:

```markdown
## Execution Strategy

This skill checks for decomposition and chooses execution method:

### Detection

Check for manifest file before choosing execution:

\`\`\`bash
if [[ -f "docs/plans/tasks/YYYY-MM-DD-<feature>/manifest.json" ]]; then
  # Manifest exists → Use parallel execution
  EXECUTION_MODE="parallel"
else
  # No manifest → Use sequential execution
  EXECUTION_MODE="sequential"
fi
\`\`\`

### Parallel Execution (manifest exists)

**When:** \`manifest.json\` found in tasks directory

**Process:**
1. Load plan manifest from \`docs/plans/tasks/YYYY-MM-DD-<feature>/manifest.json\`
2. Invoke \`parallel-subagent-driven-development\` skill with manifest
3. Execute tasks in parallel batches (up to 2 concurrent subagents)
4. Code review gate after each batch
5. Continue until all tasks complete

**Benefits:**
- Up to 2 tasks run concurrently per batch
- ~40% faster for parallelizable plans
- 90% context reduction per task

### Sequential Execution (no manifest)

**When:** No \`manifest.json\` found

**Process:**
1. Load monolithic plan from \`docs/plans/YYYY-MM-DD-<feature>.md\`
2. Invoke \`subagent-driven-development\` skill
3. Execute tasks sequentially (one at a time)
4. Code review gate after each task
5. Continue until all tasks complete

**Use case:**
- Simple plans (1-3 tasks)
- Sequential work that can't parallelize
- Prefer simplicity over speed

### CRITICAL Constraint

⚠️ **Cannot use parallel-subagent-driven-development without manifest.json**

If manifest does not exist → MUST use sequential mode (subagent-driven-development)

### Recommendation

Always decompose plans with 4+ tasks to enable parallel execution.
Run \`/cc:parse-plan\` to create manifest before execution.
```

**Step 3: Read file to find execution strategy section**

```bash
grep -n "Execution Strategy" cc/skills/executing-plans/SKILL.md
```

**Step 4: Read file to prepare for edit**

```bash
cat cc/skills/executing-plans/SKILL.md
```

**Step 5: Commit**

```bash
git add cc/skills/executing-plans/SKILL.md
git commit -m "feat: update executing-plans to detect and use parallel/sequential"
```

## Files to Modify
- cc/skills/executing-plans/SKILL.md

## Verification Checklist
- [ ] Implementation complete
- [ ] Tests written (TDD - test first!)
- [ ] All tests pass
- [ ] Lint/type check clean
- [ ] Code review requested
- [ ] Code review passed
