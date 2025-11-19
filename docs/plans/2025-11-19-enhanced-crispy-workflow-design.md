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

## State Persistence (Save/Resume)

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

This skill ALWAYS uses `parallel-subagent-driven-development` for execution.

When invoked:
1. Load the plan manifest from `docs/plans/tasks/YYYY-MM-DD-<feature>/manifest.json`
2. Invoke parallel-subagent-driven-development with the manifest
3. Execute tasks in parallel batches (up to 2 concurrent subagents)
4. Code review gate after each batch
5. Continue until all tasks complete

Note: The sequential execution mode is deprecated. All plans execute with parallelization.
```

### 3. `decomposing-plans/SKILL.md`

Add prompt at the end:

```markdown
After decomposition completes, prompt user:

"Plan decomposed into X tasks across Y parallel batches.
Ready to A) review the plan or B) execute immediately?"
```

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
