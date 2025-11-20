# Task 14: Create /cc:research command

## Dependencies
- Previous tasks: none
- Must complete before: none

## Parallelizable
- Can run in parallel with: Task 1, Task 2, Task 3, Task 4, Task 5, Task 6, Task 7, Task 8, Task 9, Task 10, Task 11, Task 12, Task 13, Task 15, Task 16, Task 17, Task 18, Task 19, Task 20, Task 21, Task 22, Task 23, Task 24

## Implementation

**Files:**
- Create: `cc/commands/cc/research.md`

**Step 1: Ensure directory exists**

```bash
ls -la cc/commands/cc/
```

Expected: Directory exists (created in earlier tasks)

**Step 2: Write command file**

Create `cc/commands/cc/research.md`:

```markdown
Use the research-orchestration skill to spawn parallel research subagents and synthesize findings.

**Prerequisites:**
- Brainstorm completed
- Feature concept defined

**What this does:**
1. Analyzes brainstorm context
2. Suggests researchers (Codebase, Library docs, Web, GitHub)
3. Allows user to adjust selection
4. Spawns up to 4 subagents in parallel
5. Synthesizes findings
6. Automatically saves to \`YYYY-MM-DD-<feature>-research.md\`

**Next step:** Writing implementation plan with research context
```

**Step 3: Verify file created**

```bash
cat cc/commands/cc/research.md
```

Expected: Command content visible

**Step 4: Commit**

```bash
git add cc/commands/cc/research.md
git commit -m "feat: add /cc:research command"
```

## Files to Modify
- cc/commands/cc/research.md

## Verification Checklist
- [ ] Implementation complete
- [ ] Tests written (TDD - test first!)
- [ ] All tests pass
- [ ] Lint/type check clean
- [ ] Code review requested
- [ ] Code review passed
