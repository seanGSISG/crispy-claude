---
date: 2025-11-20T01:20:59+00:00
git_commit: e24f6bf633e4bb6aba9d6f9fc643f3f7d7806a30
branch: main
repository: superpowers
topic: "Enhanced CrispyClaude Workflow Design Review Session"
tags: [design-review, brainstorming, crispy-claude, workflow-enhancement]
status: complete
last_updated: 2025-11-20
type: planning
---

# Design Review Session: Enhanced CrispyClaude Workflow

## Session Overview

Conducted comprehensive review of `docs/plans/2025-11-19-enhanced-crispy-workflow-design.md` using the brainstorming skill to identify gaps in logic and implementation instructions.

## Key Deliverable

Created detailed task breakdown document: `docs/plans/2025-11-20-design-update-tasks.md`

This document provides 15+ actionable tasks organized into 5 phases for updating the design document across multiple sessions.

## Critical Gaps Identified

### 1. Namespace Inconsistency 🔴 CRITICAL

**Issue**: Design uses `superpowers:` prefix throughout, but correct namespace is `cc:`

**Impact**: All skill references are incorrect, would cause confusion during implementation

**Fix**: Global find/replace `superpowers:` → `cc:` in ~8-10 locations

### 2. Execution Flow Logic Gap 🔴 CRITICAL

**Issue**: Design doesn't explain that decomposition is optional and affects execution choice

**Key clarifications needed**:
- Decomposition is OPTIONAL (not mandatory)
- `parallel-subagent-driven-development` REQUIRES decomposition (manifest.json)
- Without decomposition, MUST use `subagent-driven-development`
- Decomposition highly recommended for 4+ tasks

**Impact**: Without this, implementers won't understand when to use which execution skill

**Fix**: Add "Execution Flow Decision Tree" section showing both paths

### 3. Stage Detection Algorithm Missing 🔴 CRITICAL

**Issue**: `/cc:save` is described as "context-aware" but no algorithm for detecting stage

**Key questions unanswered**:
- How to detect if in research vs planning vs execution vs complete stage?
- What file/context checks to perform?
- How to handle ambiguity?

**Impact**: Cannot implement `/cc:save` command without this logic

**Fix**: Add detailed stage detection algorithm with file checks, TodoWrite checks, git status

### 4. Automatic vs Manual Saves Unclear

**Issue**: Design doesn't distinguish which saves are automatic vs manual

**Clarification**:
- **Automatic**: research (after subagents), complete (after execution)
- **Manual**: planning, execution (user runs `/cc:save`)

**Impact**: Confusion about when saves happen

**Fix**: Add "Save Behavior" section clarifying automatic vs manual

### 5. Research Subagent Selection Logic Missing

**Issue**: Design says "analyzes brainstorm context to suggest researchers" but no algorithm

**Key questions**:
- How to determine which researchers to enable by default?
- What keywords trigger each researcher?
- How to present checkboxes to user?

**Impact**: Cannot implement intelligent research selection

**Fix**: Add selection algorithm with keyword triggers and checkbox presentation

### 6. Agent File Format Unspecified

**Issue**: Design mentions agents have "frontmatter" but doesn't show format

**Missing**:
- Frontmatter field definitions
- Example agent file
- Invocation pattern

**Impact**: Cannot create agent files without specification

**Fix**: Add agent file format section with complete example

### 7. Resume Behavior Too Generic

**Issue**: Shows generic resume format but not stage-specific options

**Missing**: What options to present when resuming from each stage

**Fix**: Add stage-specific resume options (4 different presentations)

### 8. executing-plans Logic Incorrect

**Issue**: Says skill "ALWAYS uses parallel-subagent-driven-development" 

**Correct behavior**: Should conditionally use parallel only if manifest.json exists

**Impact**: Would break for non-decomposed plans

**Fix**: Update to show conditional logic based on manifest.json existence

## User Corrections

User provided critical clarifications:

1. **Command structure**: `commands/cc/save.md` → `/cc:save` pattern
2. **Namespace**: All references should be `cc:` not `superpowers:`
3. **Decomposition**: Optional, but required for parallel execution
4. **Stage detection**: Needs specific algorithm
5. **Task 5.1 addition**: decompose-plan should offer option C to save memory for new session execution

## Task Document Structure

Created `docs/plans/2025-11-20-design-update-tasks.md` with:

### Phase 1: Global Corrections (2 tasks)
- Namespace replacement
- Command structure documentation

### Phase 2: Execution Flow (3 tasks) 🔴
- Execution flow decision tree
- executing-plans conditional logic
- writing-plans decomposition option

### Phase 3: State Persistence (3 tasks) 🔴
- Automatic vs manual saves
- Stage detection algorithm
- Resume behavior by stage

### Phase 4: Research Architecture (3 tasks)
- Subagent selection algorithm
- Agent file format
- Agent invocation guide

### Phase 5: Additional Updates (3 tasks)
- decomposing-plans options (including save for new session)
- Prerequisites checklist
- PR section verification

## Additional Requirements

User added at end of session:

1. **Update `cc/commands/README.md`**: Document what each command does for end users
2. **Update `/workspaces/superpowers/README.md`**: Reflect new framework capabilities

## Design Patterns Discovered

### Command vs Skill Distinction
- **Commands**: User-facing slash commands in `cc/commands/cc/*.md`
- **Skills**: Internal instructions in `cc/skills/*/SKILL.md`
- No namespace prefix for skills, just name reference

### Execution Paths
Two valid paths after write-plan:
1. **Decompose → Parallel**: For 4+ tasks, enables 2 concurrent subagents
2. **Direct → Sequential**: For 1-3 tasks, simpler flow

### Save Triggers
- **Automatic**: research-orchestration and workflow completion
- **Manual**: User runs `/cc:save` at any workflow stage

### Agent Architecture
- Defined in `cc/agents/*.md` with frontmatter
- Each backed by skill with MCP best practices
- Invoked via Task tool with skill reference

## Implementation Readiness

**Before implementation can begin**:
- ✅ Gaps identified and documented
- ✅ Task breakdown created
- ✅ Full content provided for major sections
- ⏳ Design document needs updates (15 tasks)
- ⏳ README files need updates

**After design updates complete**:
- Can begin implementing new commands
- Can create new skills
- Can define agent files
- Can update existing skills

## Files Modified This Session

1. Created: `docs/plans/2025-11-20-design-update-tasks.md`
   - Comprehensive task breakdown
   - 15 detailed tasks with locations and content
   - Session-independent execution support

2. User modified: `docs/plans/2025-11-20-design-update-tasks.md`
   - Added option C to Task 5.1 (save memory for new session)
   - Added note about README updates

## Key Takeaways

1. **Design documents need validation**: Even approved designs benefit from critical review
2. **Namespace matters**: Inconsistent references cause implementation confusion
3. **Optionality must be explicit**: Don't assume readers understand what's mandatory vs optional
4. **Algorithms need specification**: "Context-aware" needs concrete detection logic
5. **Examples are critical**: Agent format, invocation patterns need complete examples

## Next Steps

1. Use task document to update design across multiple sessions
2. After design updates complete, begin implementation
3. Update README files to document new framework
4. Test examples in design document before finalizing

## Session Context

- **Skill used**: brainstorming (for collaborative design review)
- **Mode**: Interactive refinement of design document
- **Approach**: Deep review of chat.txt conversation history
- **User involvement**: High (provided critical corrections and clarifications)
- **Outcome**: Actionable task list ready for execution

## Notes for Future Sessions

- Task document line numbers may shift as edits are made
- Use section headers as primary navigation
- Verify cross-references after each phase
- Test all examples before considering updates complete
- Maintain consistent terminology throughout updates
