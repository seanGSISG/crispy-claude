---
description: Load saved workflow state from memory and continue from checkpoint
argument-hint: "[memory-file]"
---

Load saved workflow state from Serena MCP memory and continue from checkpoint.

**Usage:** `/cc:resume <memory-file>`

**Example:** `/cc:resume 2025-11-20-user-auth-execution.md`

**Prerequisites:**
- Valid memory file exists: `YYYY-MM-DD-<feature>-<stage>.md`
- Memory has required frontmatter metadata

**What this does:**

**Load & Parse:**
1. Read memory file from Serena MCP
2. Parse frontmatter (status, type, branch)
3. Load full content into conversation context

**Analyze Progress:**
- Based on type (research, planning, execution, complete)
- Check status (in-progress, complete, blocked)
- Determine what's done vs. remaining

**Present Assessment:**

```
Loaded: ${filename}
Status: ${status}
Branch: ${branch}
Last updated: ${date}

${stage-specific-summary}

Next step in crispy workflow: ${recommended-next-step}

Options:
A) ${primary-next-action}
B) ${alternative-action}
C) ${another-alternative}
D) Skip to different workflow step
```

**Stage-Specific Options:**

**From research.md:**
- A) Write plan with research context
- B) Re-run specific research subagent
- C) Do additional research

**From planning.md:**
- A) Continue writing plan
- B) Review draft with plan-review
- C) Start over with new brainstorm

**From execution.md:**
- A) Continue execution from current task
- B) Review completed work
- C) Adjust remaining tasks

**From complete.md:**
- A) Create PR
- B) Make additional changes
- C) Review implementation

**Flexible Continuation:**
- User can continue crispy workflow
- Or run any individual command
- Context fully restored
