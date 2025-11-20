# Task 5: Create serena-explorer agent

## Dependencies
- Previous tasks: 1, 2, 3, 4
- Must complete before: 10, 12

## Parallelizable
- Can run in parallel with: Task 6, Task 7, Task 8, Task 9, Task 11, Task 13, Task 14, Task 15, Task 16, Task 17, Task 18, Task 19, Task 20, Task 21, Task 22, Task 23, Task 24

## Implementation

**Files:**
- Create: `cc/agents/serena-explorer.md`

**Step 1: Create agents directory**

```bash
mkdir -p cc/agents
```

**Step 2: Write agent file**

Create `cc/agents/serena-explorer.md`:

```markdown
---
name: serena-explorer
description: Codebase exploration specialist using Serena MCP for architectural understanding and pattern discovery
tools: [Serena MCP]
skill: using-serena-for-exploration
model: sonnet
---

# Serena Explorer Agent

You are a codebase exploration specialist. Use Serena MCP tools to understand architecture, find similar implementations, and trace dependencies.

Follow the `using-serena-for-exploration` skill for best practices on:
- Using find_symbol for targeted code discovery
- Using search_for_pattern for broader searches
- Using get_symbols_overview for file structure understanding
- Providing file:line references in all findings

Report findings with:
- File paths and line numbers
- Architectural patterns discovered
- Integration points identified
- Relevant code snippets with context
```

**Step 3: Verify file created**

```bash
cat cc/agents/serena-explorer.md | head -20
```

Expected: Frontmatter and content visible

**Step 4: Commit**

```bash
git add cc/agents/serena-explorer.md
git commit -m "feat: add serena-explorer research agent"
```

## Files to Modify
- cc/agents/serena-explorer.md

## Verification Checklist
- [ ] Implementation complete
- [ ] Tests written (TDD - test first!)
- [ ] All tests pass
- [ ] Lint/type check clean
- [ ] Code review requested
- [ ] Code review passed
