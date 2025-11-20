# Enhanced CrispyClaude Workflow Design

**Date:** 2025-11-19
**Status:** Approved
**Type:** Feature Enhancement

## Overview

Enhance CrispyClaude with a complete, opinionated workflow from ideation to PR creation. The core enhancement adds:

1. **Research capabilities** - MCP-powered subagents (Serena, Context7, WebSearch, GitHub) that gather both internal codebase knowledge and external best practices
2. **Plan validation** - Interactive review process that checks completeness, quality, feasibility, and scope creep
3. **State persistence** - Save/resume functionality using Serena MCP memory at any workflow stage
4. **PR automation** - Smart PR creation with auto-generated descriptions from plans and execution context

The workflow becomes: `brainstorm → (optional research) → write-plan → parse-plan → (optional review) → execute → save → pr`

Users get two modes:
- **Individual commands** - Run each step independently for flexibility
- **`/cc:crispy` orchestrator** - Full automated workflow with approval gates

All execution defaults to parallel subagent execution (up to 2 concurrent tasks), and state can be saved/resumed at any point using stage-specific memory files (`YYYY-MM-DD-<feature>-<stage>.md`).

## Command & Skill Structure

Commands follow this pattern:
- File: `cc/commands/cc/<name>.md`
- Usage: `/cc:<name>`
- Example: `cc/commands/cc/save.md` → `/cc:save`

Skills are referenced by name only:
- File: `cc/skills/<skill-name>/SKILL.md`
- Reference: "Use the <skill-name> skill"
- Example: "Use the parallel-subagent-driven-development skill"
  refers to `cc/skills/parallel-subagent-driven-development/SKILL.md`

Key: Commands are slash commands for users. Skills are instructions for Claude.

## Execution Flow Decision Tree

After writing a plan, execution approach depends on whether you decompose.

### Path 1: With Decomposition (Recommended for 4+ tasks)

**When**: Plans with 4+ tasks, parallelizable work, need speed

**Flow**:
1. `/cc:write-plan` → `docs/plans/YYYY-MM-DD-<feature>.md`
2. `/cc:parse-plan` → Task files + `manifest.json`
3. Optional: `/cc:review-plan`
4. Execute with `cc/skills/parallel-subagent-driven-development/SKILL.md`

**Requirements**:
- Must have `manifest.json` from decomposition
- Task files in `docs/plans/tasks/YYYY-MM-DD-<feature>/`

**Benefits**:
- Up to 2 tasks in parallel per batch
- ~40% faster for parallelizable plans
- 90% context reduction per task

### Path 2: Without Decomposition (For simple 1-3 task plans)

**When**: Simple plans, sequential work, prefer simplicity

**Flow**:
1. `/cc:write-plan` → `docs/plans/YYYY-MM-DD-<feature>.md`
2. Skip `/cc:parse-plan`
3. Execute with `cc/skills/subagent-driven-development/SKILL.md`

**Requirements**:
- Just the monolithic plan file

**Benefits**:
- Simpler flow, no decomposition overhead
- Works for small sequential plans

### CRITICAL Constraint

⚠️ You CANNOT use parallel-subagent-driven-development without decomposition.

If manifest.json does not exist → MUST use subagent-driven-development

### Recommendation

Always decompose for plans with 4+ tasks to enable parallel execution.

### /cc:crispy Behavior

The `/cc:crispy` orchestrator ALWAYS decomposes (Step 4), enabling parallel execution.

Individual command users can skip decomposition for simple plans.

## New Commands & Skills

### New Commands

1. **`/cc:research`** - Spawns parallel research subagents (serena-explorer, context7-researcher, web-researcher, github-researcher)
2. **`/cc:parse-plan`** - Decomposes plan into parallel task files (wraps existing decomposing-plans skill)
3. **`/cc:review-plan`** - Interactive plan validation focused on completeness, quality, feasibility, scope creep
4. **`/cc:save`** - Context-aware state persistence to Serena memory (works at any workflow stage)
5. **`/cc:resume <path>`** - Loads saved state and continues from checkpoint
6. **`/cc:pr`** - Creates PR with auto-generated description (verifies branch, pushes, creates PR)
7. **`/cc:crispy`** - Full workflow orchestrator with approval gates

### New Skills

1. **`using-serena-for-exploration`** - Best practices for Serena MCP codebase analysis
2. **`using-context7-for-docs`** - Effective library documentation research patterns
3. **`using-web-search`** - Web research strategies for best practices
4. **`using-github-search`** - GitHub issue/PR/discussion discovery techniques
5. **`research-orchestration`** - Manages parallel research subagents, synthesis of findings
6. **`plan-review`** - Comprehensive plan validation with interactive refinement
7. **`state-persistence`** - Save/resume mechanics using Serena memory
8. **`pr-creation`** - Smart PR generation from context

## Complete Workflow (`/cc:crispy`)

### Step 1: Brainstorm
- Runs existing `brainstorming` skill
- At completion, prompts: "Ready to A) write the plan or B) research?"

### Step 2: Research (Optional)
- If user selects B:
  - Analyzes brainstorm context to suggest researchers: `[✓] Codebase [✓] Library docs [✓] Web [ ] GitHub`
  - User can adjust selection
  - Spawns up to 4 subagents in parallel (each using their specialized skill)
  - Main agent synthesizes findings: "I have new research and am ready to write the plan"
  - **Automatically saves to:** `YYYY-MM-DD-<feature>-research.md`

### Step 3: Write Plan
- Runs existing `writing-plans` skill
- Incorporates research findings if available
- Outputs plan to `docs/plans/YYYY-MM-DD-<feature>.md`

### Step 4: Parse Plan
- Runs existing `decomposing-plans` skill
- Creates task files in `docs/plans/tasks/YYYY-MM-DD-<feature>/`
- Generates manifest with parallel batches
- Prompts: "Ready to A) review the plan or B) execute immediately?"

### Step 5: Review Plan (Optional)
- If user selects A:
  - Single reviewer checks completeness, quality, feasibility, scope creep
  - If major issues found, spawns specialized validators
  - Interactive refinement until approved
  - Updates plan if changes made

### Step 6: Execute Plan
- Runs `parallel-subagent-driven-development` skill (always the default)
- Executes tasks in parallel batches (up to 2 concurrent subagents)
- Code review gate after each batch
- Handles failures with existing resilience mechanisms

### Step 7: Save Memory
- Runs automatically at completion with `type=complete`
- Captures: implementation learnings, patterns discovered, gotchas, decisions made
- **Saves to:** `YYYY-MM-DD-<feature>-complete.md`
- Can also be run manually at ANY point via `/cc:save`

### Step 8: Create PR
- Runs `pr-creation` skill
- Verifies on feature branch (not main/master)
- Generates PR description from plan, execution context, and memory
- Pushes branch to remote
- Creates PR with auto-generated description

**Throughout workflow:**
- User can run `/cc:save` at any point (research, planning, execution stages)
- Creates stage-specific memory: `YYYY-MM-DD-<feature>-{research|planning|execution|complete}.md`
- Later run `/cc:resume path/to/memory.md` to continue from that point

## Research Subagent Architecture

Each research subagent is:
- A specialized agent type (defined in agent metadata with frontmatter)
- Backed by a skill that encodes MCP usage best practices
- Focused on a specific knowledge domain

### Research Subagent Selection Algorithm

When user chooses "B) research", intelligently select researchers.

#### Default Selection

**serena-explorer** [✓ ALWAYS]
- Always need codebase understanding

**context7-researcher** [✓ if library mentioned]
- Select if: new library, framework, official docs needed
- Keywords: "using React", "integrate X", "best practices"

**web-researcher** [✓ if patterns mentioned]
- Select if: best practices, tutorials, modern approaches
- Keywords: "industry standard", "common pattern", "how to"

**github-researcher** [☐ usually OFF]
- Select if: known issues, community solutions, similar features
- Keywords: "GitHub issue", "others solved", "similar to X"

#### User Presentation

```
Based on brainstorm, I recommend:

[✓] Codebase (serena-explorer)
[✓] Library docs (context7-researcher) - React patterns
[✓] Web (web-researcher) - Auth best practices
[ ] GitHub (github-researcher)

Adjust? (Y/n)
```

If Y: Let user toggle with letters (C/L/W/G)
If n: Use defaults

#### Spawning

- Up to 4 in parallel
- Each uses specialized skill
- Synthesize after all complete
- Auto-save to research.md

### 1. serena-explorer
- **Skill:** `using-serena-for-exploration`
- **Tools:** Serena MCP (find_symbol, search_for_pattern, get_symbols_overview, etc.)
- **Purpose:** Understand current codebase architecture, find similar implementations, trace dependencies
- **Output:** File paths with line numbers, architectural patterns, integration points

### 2. context7-researcher
- **Skill:** `using-context7-for-docs`
- **Tools:** Context7 MCP (resolve-library-id, get-library-docs)
- **Purpose:** Official library documentation, framework best practices, version-specific patterns
- **Output:** API usage examples, official patterns, migration guides

### 3. web-researcher
- **Skill:** `using-web-search`
- **Tools:** WebSearch, WebFetch
- **Purpose:** Best practices, tutorials, recent articles, expert opinions
- **Output:** Curated articles with quotes, publication dates, authority assessment

### 4. github-researcher
- **Skill:** `using-github-search`
- **Tools:** WebSearch (with site:github.com), WebFetch
- **Purpose:** Related issues, PRs, discussions, community solutions
- **Output:** Relevant GitHub links, problem-solution patterns, common gotchas

### Agent File Format

Research agents are defined in `cc/agents/*.md` with frontmatter metadata.

#### Frontmatter Structure

```yaml
---
name: serena-explorer
description: Codebase exploration specialist using Serena MCP
tools: [Serena MCP]
skill: using-serena-for-exploration
model: sonnet
---
```

**Fields**:
- `name` - Agent identifier (matches filename)
- `description` - What the agent does (1-2 sentences)
- `tools` - List of MCP servers or tool categories used
- `skill` - Reference to skill file that defines behavior
- `model` - Claude model to use (sonnet/opus/haiku)

#### Complete Example: serena-explorer.md

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

#### Other Agent Files Needed

- `context7-researcher.md` - Library documentation specialist
- `web-researcher.md` - Web search and best practices specialist
- `github-researcher.md` - GitHub issues/PRs/discussions specialist
- `completeness-checker.md` - Plan completeness validator (for plan-review)
- `feasibility-analyzer.md` - Plan feasibility checker (for plan-review)
- `scope-creep-detector.md` - Scope validation specialist (for plan-review)
- `quality-validator.md` - Plan quality checker (for plan-review)

### How to Invoke Research Agents

Research agents are spawned using the Task tool with agent reference:

```typescript
// From research-orchestration skill
await Task({
  subagent_type: "serena-explorer",
  description: "Explore codebase for auth patterns",
  prompt: `
    Analyze the current authentication implementation.

    Find:
    - Existing auth files and their structure
    - Similar authentication patterns in codebase
    - Integration points for new auth features

    Provide file:line references for all findings.
  `
})
```

**Key points**:
- `subagent_type` matches agent name from frontmatter
- `description` is short summary (3-5 words)
- `prompt` includes specific research objectives
- Agent automatically uses its configured skill and tools
- Results returned to main agent for synthesis

## State Persistence (Save/Resume)

### Automatic vs Manual Saves

The workflow includes both automatic and manual save points:

**Automatic Saves** (no user action required):
- **After research completes** - Saves to `YYYY-MM-DD-<feature>-research.md`
  - Triggered when all research subagents finish
  - Includes brainstorm summary, codebase findings, library docs, web research
  - Happens automatically before proceeding to write-plan

- **After workflow completion** - Saves to `YYYY-MM-DD-<feature>-complete.md`
  - Triggered when execution finishes
  - Includes implementation learnings, patterns discovered, gotchas, decisions
  - Happens automatically before PR creation

**Manual Saves** (user runs `/cc:save`):
- **During planning** - Saves to `YYYY-MM-DD-<feature>-planning.md`
  - User can save while drafting plan
  - Captures design decisions, alternatives considered, open questions

- **During execution** - Saves to `YYYY-MM-DD-<feature>-execution.md`
  - User can pause execution at any point
  - Captures progress summary, completed tasks, current task state, blockers

**Key principle**: Automatic saves happen at natural workflow boundaries (research → planning, execution → PR). Manual saves provide pause points within planning or execution stages.

### Memory File Format

**Naming:** `YYYY-MM-DD-<feature-name>-<stage>.md`

**Stages:**
- `research` - After research completes
- `planning` - During plan writing
- `execution` - During/pausing execution
- `complete` - After full workflow completion

### Metadata Structure

All memory files include frontmatter:

```markdown
---
date: [ISO 8601 with timezone]
git_commit: [current commit hash]
branch: [current branch name]
repository: crispy-claude
topic: "[Feature Name] Checkpoint"
tags: [checkpoint, relevant-tags]
status: [in-progress|complete|blocked]
last_updated: [YYYY-MM-DD]
type: [research|planning|execution|complete]
---
```

### /cc:save Stage Detection Algorithm

When `/cc:save` runs, detect current workflow stage to create correct memory file.

#### Detection Rules

**Research stage** if:
- ✅ Brainstorm completed
- ✅ Research subagents reported back
- ❌ No plan file in `docs/plans/`
- **Save as**: `YYYY-MM-DD-<feature>-research.md`

**Planning stage** if:
- ✅ Plan file exists: `docs/plans/YYYY-MM-DD-<feature>.md`
- ❌ No manifest.json
- ❌ No tasks in TodoWrite
- **Save as**: `YYYY-MM-DD-<feature>-planning.md`

**Execution stage** if:
- ✅ Plan exists AND (manifest.json OR TodoWrite has tasks)
- ✅ Uncommitted changes (work in progress)
- ❌ Not all tasks complete
- **Save as**: `YYYY-MM-DD-<feature>-execution.md`

**Complete stage** if:
- ✅ All tasks complete in TodoWrite
- ✅ Execution finished
- **Save as**: `YYYY-MM-DD-<feature>-complete.md`

#### Feature Name Extraction

- From plan filename if exists
- From brainstorm topic if early stage
- Ask user if ambiguous

#### Metadata Collection

```bash
git rev-parse HEAD           # commit hash
git branch --show-current    # branch name
date -Iseconds              # timestamp
```

#### Ambiguity Handling

If unclear, ask: "Save as: A) research B) planning C) execution D) complete?"

#### Example

```
User: /cc:save

Checks:
- ✅ Plan: docs/plans/2025-11-20-user-auth.md
- ❌ No manifest.json
- ❌ No TodoWrite tasks
- ❌ No uncommitted changes

→ Detected: planning stage
→ Save: 2025-11-20-user-auth-planning.md
```

### Stage-Specific Content

**`-research.md`** (saved after research completes):
```markdown
# Research: <feature-name>

## Brainstorm Summary
[Key decisions from brainstorm session]

## Codebase Findings (serena-explorer)
- Current architecture: [file:line references]
- Similar implementations: [patterns found]
- Integration points: [where to hook in]

## Library Documentation (context7-researcher)
- Relevant APIs: [official patterns]
- Best practices: [framework recommendations]

## Web Research (web-researcher)
- Best practices: [articles, quotes, dates]
- Expert opinions: [sources]

## GitHub Research (github-researcher)
- Related issues: [links, solutions]
- Common gotchas: [community learnings]

## Next Steps
Ready to write plan with research context
```

**`-planning.md`** (saved during plan writing):
```markdown
# Planning: <feature-name>

## Design Decisions
- Approach chosen: [with rationale]
- Alternatives considered: [trade-offs]

## Plan Draft
[Current plan state or link to plan file]

## Open Questions
[Unresolved items]

## Next Steps
[Parse plan / Continue planning]
```

**`-execution.md`** (saved during execution):
```markdown
# Execution: <feature-name>

## Plan Reference
Link to: docs/plans/YYYY-MM-DD-<feature>.md
Tasks directory: docs/plans/tasks/YYYY-MM-DD-<feature>/

## Progress Summary
- Total tasks: X
- Completed: Y
- In progress: Z
- Remaining: N

## Completed Tasks
- [Task 1]: ✓ Done - [summary of changes]
- [Task 2]: ✓ Done - [summary of changes]

## Current Task
- [Task N]: In progress - [current state, blockers]

## Blockers/Issues
[Any problems encountered]

## Next Steps
Continue execution from task N
```

**`-complete.md`** (saved at workflow completion):
```markdown
# Implementation Complete: <feature-name>

## What Was Built
[Summary of implementation]

## Key Learnings
- Pattern discovered: [what worked well]
- Gotcha encountered: [what to watch for]
- Trade-off made: [decision and reasoning]

## Codebase Updates
- Files modified: [major changes with file:line]
- New patterns introduced: [for future reference]
- Integration points: [where system connects]

## For Next Time
- What worked: [approaches to reuse]
- What didn't: [avoid in future]
- Suggestions: [improvements for similar tasks]

## PR Created
Link to PR: [URL]
```

### Resume Behavior

When running `/cc:resume path/to/YYYY-MM-DD-<feature>-<stage>.md`:

1. **Parse metadata** - Extract status, type, branch info
2. **Restore context** - Load all content into conversation
3. **Analyze progress** - Based on type and status, determine what's done vs. remaining
4. **Present assessment:**
   ```
   Loaded: user-authentication-execution.md
   Status: in-progress (3/5 tasks complete)
   Branch: feature/user-authentication
   Last updated: 2025-11-19

   Next step in crispy workflow: Continue execution

   Continue with execution? (Y/n/other)
   ```
5. **Flexible continuation** - User can continue crispy workflow or run different command

### Stage-Specific Resume Options

What gets presented depends on the memory file type:

**Resuming from -research.md**:
```
Loaded: user-auth-research.md
Status: complete

Research findings:
- Codebase: [summary of serena findings]
- Library docs: [summary of context7 findings]
- Web: [summary of web research]

Next step in crispy workflow: Write plan

Options:
A) Write plan with research context
B) Re-run specific research subagent
C) Do additional research
D) Skip to different workflow step
```

**Resuming from -planning.md**:
```
Loaded: user-auth-planning.md
Status: in-progress

Plan draft status: [summary of what's written]
Open questions: [list any unresolved items]

Next step in crispy workflow: Complete plan

Options:
A) Continue writing plan
B) Review draft with plan-review
C) Start over with new brainstorm
D) Skip to different workflow step
```

**Resuming from -execution.md**:
```
Loaded: user-auth-execution.md
Status: in-progress (3/5 tasks complete)
Branch: feature/user-auth

Completed: Task 1, Task 2, Task 3
In progress: Task 4
Remaining: Task 5

Next step in crispy workflow: Continue execution

Options:
A) Continue execution from Task 4
B) Review completed work
C) Adjust remaining tasks
D) Skip to different workflow step
```

**Resuming from -complete.md**:
```
Loaded: user-auth-complete.md
Status: complete

Implementation complete. All tasks finished.
Branch: feature/user-auth

Next step in crispy workflow: Create PR

Options:
A) Create PR
B) Make additional changes
C) Review implementation
D) Skip to different workflow step
```

## Plan Review Process

### Phase 1: Initial Assessment (Single Reviewer)

Runs automatic checks across 4 dimensions:

**Completeness Check:**
- All phases have clear success criteria (automated + manual)
- Dependencies between phases identified
- Rollback/migration strategy present
- Edge cases addressed
- Test strategy defined

**Quality Check:**
- Success criteria are measurable
- File paths and line numbers included
- Commands use `make` where possible
- Language is clear and actionable
- Code examples are specific

**Feasibility Check:**
- Prerequisites exist in codebase
- Assumptions validated against research
- No obvious technical blockers
- Reasonable scope for time estimate

**Scope Creep Check:**
- Compare against original brainstorm decisions
- Check "What We're NOT Doing" section exists
- Flag features not in original scope
- Identify gold-plating or over-engineering

**Scoring:** Each dimension gets a score (pass/warn/fail)

### Phase 2: Escalation (If Needed)

If any dimension scores "fail", spawn specialized validators:

- **completeness-checker** - Deep dive on missing phases, success criteria gaps, edge cases
- **feasibility-analyzer** - Spawns serena-explorer to verify assumptions against actual codebase
- **scope-creep-detector** - Compares plan against research.md and original brainstorm context
- **quality-validator** - Checks for vague language, missing references, untestable criteria

Validators run in parallel, return detailed findings.

### Phase 3: Interactive Refinement

Present findings conversationally (like brainstorming):

```
I've reviewed the plan and found some areas to improve:

**Completeness (⚠️ Warning):**
- Phase 2 success criteria don't include database migration verification
- No rollback strategy if Phase 3 fails

**Scope Creep (❌ Issue):**
- Plan includes "admin dashboard" but brainstorm only mentioned "user dashboard"
- This looks like scope expansion

**Quality (✅ Pass)**
**Feasibility (✅ Pass)**

Let's address these issues. Starting with scope:

Q1: Should we remove the admin dashboard feature, or was this intentional expansion?
   A) Remove it (stick to original scope)
   B) Keep it (intentional addition)
   C) Split into separate plan
```

One question at a time, refine until all dimensions pass. Update plan with agreed changes, re-run assessment, iterate until approved.

## PR Creation Process

### Pre-flight Checks
1. Verify on feature branch (error if on main/master)
2. Check for uncommitted changes (warn if found, offer to commit)
3. Verify remote tracking exists (set up if needed)

### PR Description Generation

Auto-generates from multiple sources:

```markdown
## Summary
[Extracted from plan's Overview section]

## Implementation Details
[Synthesized from plan phases and execution memory]

### What Changed
- [Key changes from git diff --stat]
- [Major files modified with purpose]

### Approach
[From plan's "Implementation Approach" section]

## Testing
[From plan's "Testing Strategy" + execution verification results]

- ✅ All unit tests passing
- ✅ Integration tests passing
- ✅ Manual verification completed

## Key Learnings
[From complete.md memory if available]
- [Patterns discovered]
- [Gotchas encountered]

## References
- Implementation plan: docs/plans/YYYY-MM-DD-<feature>.md
- Tasks completed: docs/plans/tasks/YYYY-MM-DD-<feature>/

---
🔥 Generated with [CrispyClaude](https://github.com/seanGSISG/crispy-claude)
```

### Execution
1. Push branch to remote
2. Create PR using `gh pr create` with generated description
3. Output PR URL
4. Optionally save PR URL to complete.md memory

## Updates to Existing Skills

### 1. `brainstorming/SKILL.md`

Add at the end of "After the Design" section:

```markdown
**Next Steps:**
- Ask: "Ready to A) write the plan or B) research first?"
- If A: Proceed to writing-plans skill
- If B: Trigger research-orchestration skill:
  - Analyze brainstorm context
  - Suggest researchers: `[✓] Codebase [✓] Library docs [ ] Web [✓] GitHub`
  - Allow user to adjust selection
  - Spawn selected subagents (max 4 in parallel)
  - Synthesize findings
  - Report: "I have new research and am ready to write the plan"
  - Automatically save to YYYY-MM-DD-<feature>-research.md
  - Proceed to writing-plans skill
```

### 2. `executing-plans/SKILL.md`

Update to always use parallel execution:

```markdown
## Execution Strategy

This skill checks for decomposition and chooses execution method:

If manifest.json exists:
  → Use parallel-subagent-driven-development

If manifest.json does NOT exist:
  → Use subagent-driven-development

Detection: Check for manifest.json file before choosing execution.

**If parallel execution (manifest exists)**:
1. Load the plan manifest from `docs/plans/tasks/YYYY-MM-DD-<feature>/manifest.json`
2. Invoke parallel-subagent-driven-development with the manifest
3. Execute tasks in parallel batches (up to 2 concurrent subagents)
4. Code review gate after each batch
5. Continue until all tasks complete

**If sequential execution (no manifest)**:
1. Load the monolithic plan from `docs/plans/YYYY-MM-DD-<feature>.md`
2. Invoke subagent-driven-development
3. Execute tasks sequentially
4. Code review gate after each task
5. Continue until all tasks complete
```

### 3. `decomposing-plans/SKILL.md`

Add prompt at the end:

```markdown
After decomposition completes, prompt user:

"Plan decomposed into X tasks across Y parallel batches.

Options:
A) Review the plan with plan-review
B) Execute immediately with parallel-subagent-driven-development
C) Save execution state to memory for later (save and exit)

Choose option (A/B/C):"

If user chooses:
- A: Proceed to plan-review skill
- B: Proceed directly to parallel-subagent-driven-development
- C: Use state-persistence skill to save execution.md memory with:
  - Plan reference and task manifest location
  - Current status (ready to execute, 0 tasks complete)
  - Recommendation to resume with `/cc:resume` and execute
  - Exit workflow after save completes
```

### 4. `writing-plans/SKILL.md`

Add guidance on execution options:

```markdown
## After Plan Completion

Present execution options to user:

**Recommended next step**: `/cc:parse-plan`

This decomposes the plan into parallel task files, enabling:
- Up to 2 tasks executing concurrently per batch
- ~40% faster execution for parallelizable plans
- 90% context reduction per task

**Alternative**: Execute directly without decomposition
- Best for simple plans (1-3 tasks)
- Uses sequential execution via subagent-driven-development
- Simpler flow, no decomposition overhead

**Note**: Decomposition is REQUIRED for parallel execution.
Always decompose plans with 4+ tasks to enable parallel-subagent-driven-development.
```

## Workflow Step Prerequisites

Each workflow step has prerequisites that must be satisfied:

### Brainstorm (`/cc:brainstorm`)
**Prerequisites**: None (starting point)

### Research (`/cc:research`)
**Prerequisites**:
- ✅ Brainstorm completed
- ✅ Feature concept defined

### Write Plan (`/cc:write-plan`)
**Prerequisites**:
- ✅ Brainstorm completed
- Optional: Research findings available

### Parse Plan (`/cc:parse-plan`)
**Prerequisites**:
- ✅ Plan file exists: `docs/plans/YYYY-MM-DD-<feature>.md`
- ✅ Plan has 2+ tasks worth decomposing

### Review Plan (`/cc:review-plan`)
**Prerequisites**:
- ✅ Plan file exists: `docs/plans/YYYY-MM-DD-<feature>.md`
- Optional: Plan decomposed (can review before or after decomposition)

### Execute Plan (via `executing-plans` skill)
**Prerequisites for parallel execution**:
- ✅ Plan file exists
- ✅ Manifest exists: `docs/plans/tasks/YYYY-MM-DD-<feature>/manifest.json`
- ✅ Task files exist in tasks directory

**Prerequisites for sequential execution**:
- ✅ Plan file exists
- ❌ No manifest (sequential mode)

### Save State (`/cc:save`)
**Prerequisites**: At least one of:
- ✅ Brainstorm + research completed (for research.md)
- ✅ Plan file exists (for planning.md)
- ✅ Execution in progress (for execution.md)
- ✅ Execution complete (for complete.md)

### Resume (`/cc:resume <path>`)
**Prerequisites**:
- ✅ Valid memory file: `YYYY-MM-DD-<feature>-<stage>.md`
- ✅ Memory file has required frontmatter metadata

### Create PR (`/cc:pr`)
**Prerequisites**:
- ✅ On feature branch (NOT main/master)
- ✅ Execution completed
- ✅ Changes committed to branch
- ✅ `gh` CLI installed and authenticated

### Full Workflow (`/cc:crispy`)
**Prerequisites**: None (orchestrates entire workflow from start)

## File Structure

```
cc/
├── commands/
│   ├── brainstorm.md (existing)
│   ├── write-plan.md (existing)
│   ├── execute-plan.md (existing)
│   ├── research.md (NEW)
│   ├── parse-plan.md (NEW)
│   ├── review-plan.md (NEW)
│   ├── save.md (NEW)
│   ├── resume.md (NEW)
│   ├── pr.md (NEW)
│   └── crispy.md (NEW - orchestrator)
│
├── skills/
│   ├── brainstorming/SKILL.md (UPDATED - add research prompt)
│   ├── writing-plans/SKILL.md (existing)
│   ├── decomposing-plans/SKILL.md (UPDATED - add review prompt)
│   ├── executing-plans/SKILL.md (UPDATED - always use parallel)
│   ├── parallel-subagent-driven-development/SKILL.md (existing)
│   │
│   ├── research-orchestration/ (NEW)
│   │   └── SKILL.md
│   ├── plan-review/ (NEW)
│   │   └── SKILL.md
│   ├── state-persistence/ (NEW)
│   │   └── SKILL.md
│   ├── pr-creation/ (NEW)
│   │   └── SKILL.md
│   │
│   ├── using-serena-for-exploration/ (NEW)
│   │   └── SKILL.md
│   ├── using-context7-for-docs/ (NEW)
│   │   └── SKILL.md
│   ├── using-web-search/ (NEW)
│   │   └── SKILL.md
│   └── using-github-search/ (NEW)
│       └── SKILL.md
│
└── agents/ (NEW directory)
    ├── serena-explorer.md
    ├── context7-researcher.md
    ├── web-researcher.md
    ├── github-researcher.md
    ├── completeness-checker.md
    ├── feasibility-analyzer.md
    ├── scope-creep-detector.md
    └── quality-validator.md
```

## Orchestrator Implementation

**Command file:** `cc/commands/crispy.md`

**Flow:**

```markdown
You are running the complete CrispyClaude workflow from ideation to PR.

## Step 1: Brainstorm
Invoke the brainstorming skill.

At completion, prompt:
"Ready to A) write the plan or B) research first?"

## Step 2: Research (Optional)
If user selects B:
- Invoke research-orchestration skill
- Skill handles subagent spawning and synthesis
- Automatically saves to YYYY-MM-DD-<feature>-research.md

## Step 3: Write Plan
Invoke writing-plans skill (incorporates research if available)

## Step 4: Parse Plan
Invoke decomposing-plans skill

At completion, prompt:
"Ready to A) review the plan or B) execute immediately?"

## Step 5: Review Plan (Optional)
If user selects A:
- Invoke plan-review skill
- Interactive refinement until approved

## Step 6: Execute
Invoke parallel-subagent-driven-development skill
Execution handles its own batch review gates

## Step 7: Save Memory
Invoke state-persistence skill with type=complete
Automatically saves to YYYY-MM-DD-<feature>-complete.md

## Step 8: Create PR
Invoke pr-creation skill
Outputs PR URL and completes workflow

Throughout: User can exit and run /cc:save at any point
```

**Approval gates:** At steps 2, 5 - user chooses A or B
**Automatic saves:** After research (step 2) and completion (step 7)
**Manual save:** User can run `/cc:save` anytime to pause

## Success Criteria

- All new commands are accessible via `/cc:*` pattern
- Research subagents can run in parallel (max 4 concurrent)
- Memory files follow naming convention and include metadata
- `/cc:resume` can restore context and continue from any stage
- `/cc:review-plan` catches completeness/quality/feasibility/scope issues
- `/cc:pr` generates comprehensive PR descriptions from context
- `/cc:crispy` orchestrates the full workflow with approval gates
- Existing skills (brainstorming, decomposing-plans, executing-plans) integrate seamlessly
