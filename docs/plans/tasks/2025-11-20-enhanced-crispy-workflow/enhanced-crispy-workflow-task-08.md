# Task 8: Create github-researcher agent

## Dependencies
- Previous tasks: 1, 2, 3
- Must complete before: none

## Parallelizable
- Can run in parallel with: Task 4, Task 5, Task 6, Task 7, Task 9, Task 10, Task 11, Task 12, Task 13, Task 14, Task 15, Task 16, Task 17, Task 18, Task 19, Task 20, Task 21, Task 22, Task 23, Task 24

## Implementation

**Files:**
- Create: `cc/agents/github-researcher.md`

**Step 1: Write agent file**

Create `cc/agents/github-researcher.md`:

```markdown
---
name: github-researcher
description: GitHub issues, PRs, and discussions specialist for community solutions and known gotchas
tools: [WebSearch, WebFetch]
skill: using-github-search
model: sonnet
---

# GitHub Researcher Agent

You are a GitHub research specialist. Use WebSearch (with site:github.com) and WebFetch to find community solutions, known issues, and implementation patterns from GitHub repositories.

Follow the `using-github-search` skill for best practices on:
- Searching closed issues for solved problems
- Finding merged PRs for implementation examples
- Analyzing discussions for community consensus
- Extracting problem-solution patterns

Report findings with:
- Issue/PR/Discussion links and status
- Problem descriptions and root causes
- Solutions with code examples
- Community consensus and frequency
- Caveats, gotchas, and trade-offs mentioned
```

**Step 2: Verify file created**

```bash
cat cc/agents/github-researcher.md | head -20
```

Expected: Frontmatter and content visible

**Step 3: Commit**

```bash
git add cc/agents/github-researcher.md
git commit -m "feat: add github-researcher agent"
```

## Files to Modify
- cc/agents/github-researcher.md

## Verification Checklist
- [ ] Implementation complete
- [ ] Tests written (TDD - test first!)
- [ ] All tests pass
- [ ] Lint/type check clean
- [ ] Code review requested
- [ ] Code review passed
