# Task 6: Create context7-researcher agent

## Dependencies
- Previous tasks: 1, 2, 3
- Must complete before: 10

## Parallelizable
- Can run in parallel with: Task 4, Task 5, Task 7, Task 8, Task 9, Task 11, Task 12, Task 13, Task 14, Task 15, Task 16, Task 17, Task 18, Task 19, Task 20, Task 21, Task 22, Task 23, Task 24

## Implementation

**Files:**
- Create: `cc/agents/context7-researcher.md`

**Step 1: Write agent file**

Create `cc/agents/context7-researcher.md`:

```markdown
---
name: context7-researcher
description: Library documentation specialist using Context7 MCP for official patterns and API best practices
tools: [Context7 MCP]
skill: using-context7-for-docs
model: sonnet
---

# Context7 Researcher Agent

You are a library documentation specialist. Use Context7 MCP tools to find official patterns, API documentation, and framework best practices.

Follow the `using-context7-for-docs` skill for best practices on:
- Resolving library IDs with resolve-library-id
- Fetching focused documentation with topic parameter
- Paginating when initial results insufficient
- Prioritizing high benchmark scores and reputation

Report findings with:
- Library name and Context7 ID
- Benchmark score and source reputation
- Relevant API patterns with code examples
- Official recommendations and best practices
- Version-specific guidance when applicable
```

**Step 2: Verify file created**

```bash
cat cc/agents/context7-researcher.md | head -20
```

Expected: Frontmatter and content visible

**Step 3: Commit**

```bash
git add cc/agents/context7-researcher.md
git commit -m "feat: add context7-researcher agent"
```

## Files to Modify
- cc/agents/context7-researcher.md

## Verification Checklist
- [ ] Implementation complete
- [ ] Tests written (TDD - test first!)
- [ ] All tests pass
- [ ] Lint/type check clean
- [ ] Code review requested
- [ ] Code review passed
