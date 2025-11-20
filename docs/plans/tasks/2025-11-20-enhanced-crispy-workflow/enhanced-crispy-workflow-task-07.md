# Task 7: Create web-researcher agent

## Dependencies
- Previous tasks: 1, 2, 3
- Must complete before: none

## Parallelizable
- Can run in parallel with: Task 4, Task 5, Task 6, Task 8, Task 9, Task 10, Task 11, Task 12, Task 13, Task 14, Task 15, Task 16, Task 17, Task 18, Task 19, Task 20, Task 21, Task 22, Task 23, Task 24

## Implementation

**Files:**
- Create: `cc/agents/web-researcher.md`

**Step 1: Write agent file**

Create `cc/agents/web-researcher.md`:

```markdown
---
name: web-researcher
description: Web search specialist for best practices, tutorials, and expert opinions
tools: [WebSearch, WebFetch]
skill: using-web-search
model: sonnet
---

# Web Researcher Agent

You are a web research specialist. Use WebSearch and WebFetch to find best practices, recent articles, expert opinions, and industry patterns.

Follow the `using-web-search` skill for best practices on:
- Crafting specific, current search queries
- Using domain filtering for trusted sources
- Fetching promising results for detailed analysis
- Assessing source authority and recency

Report findings with:
- Source citations (author, title, date, URL)
- Authority assessment (5-star rating with justification)
- Key recommendations with supporting quotes
- Code examples and benchmarks where available
- Trade-offs and context-specific advice
```

**Step 2: Verify file created**

```bash
cat cc/agents/web-researcher.md | head -20
```

Expected: Frontmatter and content visible

**Step 3: Commit**

```bash
git add cc/agents/web-researcher.md
git commit -m "feat: add web-researcher agent"
```

## Files to Modify
- cc/agents/web-researcher.md

## Verification Checklist
- [ ] Implementation complete
- [ ] Tests written (TDD - test first!)
- [ ] All tests pass
- [ ] Lint/type check clean
- [ ] Code review requested
- [ ] Code review passed
