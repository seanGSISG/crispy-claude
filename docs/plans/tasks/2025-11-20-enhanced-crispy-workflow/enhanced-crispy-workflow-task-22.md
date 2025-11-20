# Task 22: Update decomposing-plans skill

## Dependencies
- Previous tasks: none
- Must complete before: none

## Parallelizable
- Can run in parallel with: Task 1, Task 2, Task 3, Task 4, Task 5, Task 6, Task 7, Task 8, Task 9, Task 10, Task 11, Task 12, Task 13, Task 14, Task 15, Task 16, Task 17, Task 18, Task 19, Task 20, Task 21, Task 23, Task 24

## Implementation

**Files:**
- Modify: `cc/skills/decomposing-plans/SKILL.md`

**Step 1: Read current skill**

```bash
cat cc/skills/decomposing-plans/SKILL.md | tail -50
```

Expected: See end of decomposing-plans skill

**Step 2: Add review prompt at the end**

Add this section at the very end of the skill file:

```markdown
## After Decomposition

After decomposition completes successfully, prompt user:

\`\`\`
Plan decomposed into X tasks across Y parallel batches.

Manifest: \`docs/plans/tasks/YYYY-MM-DD-<feature>/manifest.json\`
Tasks: \`docs/plans/tasks/YYYY-MM-DD-<feature>/<task-files>\`

Options:
A) Review the plan with plan-review
B) Execute immediately with parallel-subagent-driven-development
C) Save and exit (resume later with /cc:resume)

Choose: (A/B/C)
\`\`\`

**If user chooses A:**
- Invoke \`plan-review\` skill
- After review completes and plan approved
- Return to this prompt (offer B or C)

**If user chooses B:**
- Proceed directly to \`parallel-subagent-driven-development\` skill
- Begin executing tasks in parallel batches

**If user chooses C:**
- Invoke \`state-persistence\` skill to save execution checkpoint
- Save as \`YYYY-MM-DD-<feature>-execution.md\` with:
  - Plan reference and manifest location
  - Status: ready to execute, 0 tasks complete
  - Next step: Resume with \`/cc:resume\` and execute
- Exit workflow after save completes
```

**Step 3: Read file to prepare for edit**

```bash
cat cc/skills/decomposing-plans/SKILL.md
```

**Step 4: Commit**

```bash
git add cc/skills/decomposing-plans/SKILL.md
git commit -m "feat: update decomposing-plans to prompt for review or execute"
```

## Files to Modify
- cc/skills/decomposing-plans/SKILL.md

## Verification Checklist
- [ ] Implementation complete
- [ ] Tests written (TDD - test first!)
- [ ] All tests pass
- [ ] Lint/type check clean
- [ ] Code review requested
- [ ] Code review passed
