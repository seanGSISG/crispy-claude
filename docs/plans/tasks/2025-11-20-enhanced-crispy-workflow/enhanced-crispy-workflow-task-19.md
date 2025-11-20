# Task 19: Create /cc:pr command

## Dependencies
- Previous tasks: 1, 2, 3, 4, 13
- Must complete before: none

## Parallelizable
- Can run in parallel with: Task 5, Task 6, Task 7, Task 8, Task 9, Task 10, Task 11, Task 12, Task 14, Task 15, Task 16, Task 17, Task 18, Task 20, Task 21, Task 22, Task 23, Task 24

## Implementation

**Files:**
- Create: `cc/commands/cc/pr.md`

**Step 1: Write command file**

Create `cc/commands/cc/pr.md`:

```markdown
Use the pr-creation skill to create a pull request with auto-generated description.

**Prerequisites:**
- On feature branch (NOT main/master)
- Execution completed
- Changes committed to branch
- \`gh\` CLI installed and authenticated

**What this does:**

**Pre-flight Checks:**
1. Verify on feature branch (error if main/master)
2. Check for uncommitted changes (offer to commit)
3. Verify remote tracking (set up if needed)
4. Check GitHub CLI installed and authenticated

**Generate PR Description from:**
- Plan file: \`docs/plans/YYYY-MM-DD-<feature>.md\`
- Complete memory: \`YYYY-MM-DD-<feature>-complete.md\` (if exists)
- Git diff: Files changed summary
- Commit messages: Timeline context

**Description Structure:**
- Summary (from plan overview)
- What Changed (git diff stat)
- Approach (from plan architecture)
- Testing (from plan + verification results)
- Key Learnings (from complete.md)
- References (plan, tasks, research)

**Execute:**
1. Push branch to remote
2. Create PR using \`gh pr create\`
3. Output PR URL
4. Update complete.md with PR link

**Title Format:** \`feat: ${Feature Name}\`

**Example:**
\`\`\`
✅ Pull request created successfully!

PR: https://github.com/user/repo/pull/42
Branch: feature/user-authentication
Base: main

View PR: https://github.com/user/repo/pull/42
\`\`\`
```

**Step 2: Verify file created**

```bash
cat cc/commands/cc/pr.md
```

Expected: Command content visible

**Step 3: Commit**

```bash
git add cc/commands/cc/pr.md
git commit -m "feat: add /cc:pr command"
```

## Files to Modify
- //github.com
- cc/commands/cc/pr.md

## Verification Checklist
- [ ] Implementation complete
- [ ] Tests written (TDD - test first!)
- [ ] All tests pass
- [ ] Lint/type check clean
- [ ] Code review requested
- [ ] Code review passed
