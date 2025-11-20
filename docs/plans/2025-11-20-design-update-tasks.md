# Update Tasks for Enhanced CrispyClaude Workflow Design

**Target Document**: `docs/plans/2025-11-19-enhanced-crispy-workflow-design.md`
**Created**: 2025-11-20
**Purpose**: Detailed task breakdown for updating the design document

---

## Task Overview

This document provides actionable tasks for updating the Enhanced CrispyClaude Workflow Design document. Each task can be completed independently across multiple sessions.

**Priority Levels**:
- 🔴 **CRITICAL** - Blockers affecting core logic
- 🟡 **HIGH** - Important clarifications for implementation
- 🟢 **MEDIUM** - Helpful clarity improvements

---

## PHASE 1: Global Corrections

### Task 1.1: Global Namespace Replacement 🔴 CRITICAL

**Objective**: Replace all `superpowers:` with `cc:`

**Reason**: Namespace changed from superpowers to cc

**Search for**: `superpowers:` (appears ~8-10 times)

**Locations**:
- Line 36: Plan header template
- Lines 49, 106, 180, 280: finishing-a-development-branch
- Lines 110-116: writing-plans execution choice
- Lines 412-428: brainstorming skill updates
- Lines 432-448: executing-plans skill updates

**Find/Replace**:
```
superpowers:subagent-driven-development → cc:subagent-driven-development
superpowers:executing-plans → cc:executing-plans
superpowers:parallel-subagent-driven-development → cc:parallel-subagent-driven-development
superpowers:finishing-a-development-branch → cc:finishing-a-development-branch
```

**Verification**: Search doc for "superpowers:" should return 0 results

---

### Task 1.2: Add Command Naming Convention Section 🟡 HIGH

**Location**: After line 23, before "## New Commands & Skills"

**Add new section**:

```markdown
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
```

---

## PHASE 2: Execution Flow Clarifications

### Task 2.1: Add Execution Flow Decision Tree 🔴 CRITICAL

**Location**: After Task 1.2, before "## New Commands & Skills"

**Reason**: Design doesn't explain:
- Decomposition is optional
- Parallel execution REQUIRES decomposition
- Without decomposition, must use sequential

**Add new major section** (see full content in detailed notes below)

Key points to include:
- **Path 1**: With decomposition → parallel execution (4+ tasks)
- **Path 2**: Without decomposition → sequential execution (1-3 tasks)
- **Critical constraint**: parallel-subagent-driven-development REQUIRES manifest.json
- **Recommendation**: Always decompose for 4+ tasks

---

### Task 2.2: Fix executing-plans Skill Instructions 🔴 CRITICAL

**Location**: Lines 431-448

**Problem**: Says "ALWAYS uses parallel" but should be conditional

**Replace section 2 under "Updates to Existing Skills"**:

Change from:
```
This skill ALWAYS uses parallel-subagent-driven-development
```

Change to:
```
This skill checks for decomposition and chooses execution method:

If manifest.json exists:
  → Use parallel-subagent-driven-development

If manifest.json does NOT exist:
  → Use subagent-driven-development

Detection: Check for manifest.json file before choosing
```

---

### Task 2.3: Update writing-plans Instructions 🟡 HIGH

**Location**: Add as item #4 in "Updates to Existing Skills"

**Add new section** explaining writing-plans should present decomposition option

Key changes:
- Mention `/cc:parse-plan` as recommended next step
- Present two execution paths (with/without decomposition)
- Clarify decomposition recommended for 4+ tasks

---

## PHASE 3: State Persistence

### Task 3.1: Add Automatic vs Manual Saves 🟡 HIGH

**Location**: After line 134, before "Memory File Format"

**Add new subsection**:

Clarify:
- **Automatic saves**: research (after subagents finish), complete (after execution)
- **Manual saves**: planning, execution (user runs `/cc:save`)
- When each type happens and what triggers them

---

### Task 3.2: Add Stage Detection Algorithm 🔴 CRITICAL

**Location**: After Task 3.1, before "Memory File Format"

**Add new subsection**: `/cc:save Stage Detection Algorithm`

Explain how to detect which stage:
1. **Research**: After brainstorm, before plan exists
2. **Planning**: Plan exists, no manifest, no tasks
3. **Execution**: Manifest or tasks exist, not all complete
4. **Complete**: All tasks done, ready for PR

Include:
- File checks (plan exists? manifest exists?)
- TodoWrite checks (tasks in progress?)
- Git status checks (uncommitted changes?)
- Ambiguity handling (ask user if unclear)

---

### Task 3.3: Expand Resume Behavior Options 🟡 HIGH

**Location**: Lines 268-284, end of "Resume Behavior"

**Add new subsection**: Stage-Specific Resume Options

For each stage (-research, -planning, -execution, -complete), show:
- What info is displayed
- What options are presented (A/B/C/D/E)
- What each option does

---

## PHASE 4: Research Architecture

### Task 4.1: Add Subagent Selection Algorithm 🟡 HIGH

**Location**: Before individual subagent descriptions (before line 110)

**Add new subsection**: Research Subagent Selection Algorithm

Explain selection logic:
- **serena-explorer**: Always ON (always need codebase understanding)
- **context7-researcher**: ON if library/framework mentioned
- **web-researcher**: ON if best practices/patterns mentioned
- **github-researcher**: OFF unless specific community research needed

Show checkbox presentation and user adjustment flow

---

### Task 4.2: Add Agent File Format 🟡 HIGH

**Location**: After subagent descriptions (after line 133)

**Add new subsection**: Agent File Format

Show:
- Frontmatter structure (name, description, tools, skill, model)
- Complete example of serena-explorer.md
- List of other agent files needed

---

### Task 4.3: Add Agent Invocation Guide 🟢 MEDIUM

**Location**: After Task 4.2

**Add new subsection**: How to Invoke Research Agents

Show Task tool invocation pattern for spawning agents

---

## PHASE 5: Additional Updates

### Task 5.1: Update decomposing-plans Instructions 🟡 HIGH

**Location**: Lines 451-459

**Current**: Says "Ready to A) review  B) or Cexecute?"

**Add clarification**: After B is chosen, explain it uses parallel-subagent-driven-development, also offer an option C) to use Serena to save a memory so parallel-subagent-driven-development can be loaded then executed in a new session

---

### Task 5.2: Add Prerequisites Checklist 🟢 MEDIUM

**Location**: New section near end, before "File Structure"

**Add section**: Workflow Step Prerequisites

For each workflow step, list what must exist:
- Research: Requires brainstorm complete
- Parse-plan: Requires plan file
- Parallel execution: Requires manifest.json
- etc.

---

### Task 5.3: Verify PR Creation Section 🟢 MEDIUM

**Location**: Lines 359-409

**Check**: All skill paths use `cc:` not `superpowers:`

**Verify**: PR description generation references correct file paths

---

## Detailed Content for Major Sections

### Full Content for Task 2.1: Execution Flow Decision Tree

```markdown
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
```

### Full Content for Task 3.2: Stage Detection Algorithm

```markdown
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
```

### Full Content for Task 4.1: Selection Algorithm

```markdown
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
```

---

## Summary Checklist

Before considering updates complete, verify:

- [ ] All `superpowers:` replaced with `cc:`
- [ ] Command structure documented
- [ ] Execution flow decision tree added
- [ ] executing-plans conditional logic corrected
- [ ] Automatic vs manual saves clarified
- [ ] Stage detection algorithm added
- [ ] Resume options by stage added
- [ ] Research selection algorithm added
- [ ] Agent file format documented
- [ ] All line numbers verified (may shift after edits)

---

## Implementation Notes

**Session Management**:
- Each task can be done in separate session
- Use line numbers as approximate guides (will shift)
- Search for section headers to locate insertion points
- Test examples work before adding

**Validation**:
- After each phase, search for TODO/FIXME left in text
- Verify examples use correct paths
- Check cross-references still valid
- Ensure consistent terminology throughout

Extra Note:  update cc/commands/README.md for endusers to understand what each command does
update /workspaces/superpowers/README.md to reflect this new framework