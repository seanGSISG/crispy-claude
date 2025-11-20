# Superpowers Improvement Plan: Parallel Execution & Plan Decomposition

**Date:** 2025-01-18
**Status:** Proposed
**Priority:** High

## Problem Statement

Current superpowers workflow has two inefficiencies:

1. **Context waste**: Each subagent reads entire monolithic plan (5k+ tokens) when they only need their specific task (~500 tokens)
2. **Time waste**: Tasks execute sequentially even when they could run in parallel

## Current Workflow

```
/brainstorm → /write-plan → /execute-plan (sequential, manual)
                         OR
                         → subagent-driven-development (sequential, one task at a time)
```

**Issues:**
- Monolithic plan file read by every subagent (wasteful)
- No parallelization of independent tasks
- Subagents must parse entire plan to find their task

## Proposed Solution

### Architecture Overview

```
/brainstorm
    ↓
/write-plan (creates monolithic plan in docs/plans/YYYY-MM-DD-feature.md)
    ↓
/decompose-plan (NEW - creates task files + manifest)
    ↓
parallel-subagent-driven-development (NEW - executes with up to 2 parallel subagents)
```

### New Components

#### 1. decomposing-plans Skill

**Location:** `superpowers/skills/decomposing-plans/SKILL.md`

**Frontmatter:**
```yaml
---
name: decomposing-plans
description: Use after writing-plans to decompose monolithic plan into individual task files and identify tasks that can run in parallel (up to 2 subagents simultaneously)
allowed-tools: [Read, Write, Bash]
---
```

**Functionality:**
1. Read monolithic plan from `docs/plans/YYYY-MM-DD-feature.md`
2. Analyze task structure and dependencies
3. Create individual task files: `docs/plans/tasks/feature-task-NN.md`
4. Generate execution manifest: `docs/plans/tasks/feature-manifest.json`
5. Call Python helper script for analysis
6. Report parallelization opportunities

**Task File Format:**
```markdown
# Task NN: [Task Name]

## Dependencies
- Previous tasks: [list or "none"]
- Files required: [list]
- Must complete before: [list or "none"]

## Parallelizable
- Can run in parallel with: [task numbers or "none"]

## Implementation Steps
[Specific steps for THIS task only - extracted from monolithic plan]

## Files to Modify
[Exact file paths]

## Verification Checklist
- [ ] Tests pass
- [ ] Lint clean
- [ ] Code review complete
```

**Manifest Format:**
```json
{
  "plan": "docs/plans/2025-01-18-feature.md",
  "feature": "feature-name",
  "created": "2025-01-18T10:00:00Z",
  "total_tasks": 5,
  "tasks": [
    {
      "id": 1,
      "title": "Task title",
      "file": "docs/plans/tasks/feature-task-01.md",
      "dependencies": [],
      "blocks": [3],
      "files": ["src/foo.ts"],
      "status": "pending"
    }
  ],
  "parallel_batches": [
    [1, 2],  // Tasks 1 and 2 can run together
    [3, 4],  // Tasks 3 and 4 can run together
    [5]      // Task 5 must run alone
  ]
}
```

#### 2. decompose-plan.py Script

**Location:** `superpowers/skills/decomposing-plans/decompose-plan.py`

**Core Algorithm:**

```python
class PlanDecomposer:
    def parse_tasks():
        # Extract tasks from monolithic plan
        # Regex patterns: "## Task N:", "### N.", "**Task N:**"

    def analyze_dependencies():
        # For each task:
        #   1. Extract file paths mentioned (file_pattern regex)
        #   2. Check for explicit task mentions ("task 3", etc.)
        #   3. Default: depends on previous task
        #   4. File conflicts = forced sequential dependency

    def identify_parallel_batches():
        # Constraint: MAX 2 tasks per batch
        # Algorithm:
        #   1. Find tasks with no unsatisfied dependencies
        #   2. Group up to 2 tasks with:
        #      - No mutual dependencies
        #      - No shared files
        #   3. Create batch
        #   4. Repeat until all tasks scheduled

    def write_task_files():
        # Generate individual markdown files

    def write_manifest():
        # Generate JSON manifest with batches
```

**Dependency Analysis Rules:**
1. **Explicit dependencies**: Task mentions "task N" → depends on task N
2. **File-based dependencies**: Tasks modifying same file → sequential
3. **Default sequential**: Task N depends on task N-1 (unless marked independent)
4. **Parallelization**: Tasks with no dependency relationship AND no file conflicts

**Example Dependency Analysis:**
```
Task 1: "Implement user model (src/models/user.ts)"
Task 2: "Implement logger (src/utils/logger.ts)"
Task 3: "Add user validation (src/models/user.ts)"

Analysis:
- Task 1 & 2: Different files, no mentions → PARALLEL
- Task 1 & 3: Same file (user.ts) → SEQUENTIAL
- Task 2 & 3: Different files, but 3 depends on 1 → SEQUENTIAL

Batches: [[1, 2], [3]]
```

#### 3. parallel-subagent-driven-development Skill

**Location:** `superpowers/skills/parallel-subagent-driven-development/SKILL.md`

**Frontmatter:**
```yaml
---
name: parallel-subagent-driven-development
description: Use after decomposing-plans to execute tasks with up to 2 subagents simultaneously, with code review between batches
allowed-tools: [Read, Write, Task, TodoWrite] <-- include morphllm for writing to files, serena for precise location of files>
---
```

**Process:**

```
Step 1: Load manifest.json

Step 2: Create TodoWrite checklist
  - [ ] Execute batch 1 (tasks X, Y)
  - [ ] Review batch 1
  - [ ] Execute batch 2 (task Z)
  - [ ] Review batch 2
  ...

Step 3: For each batch:

  IF batch has 1 task:
    - Single Task tool call
    - Subagent reads task-NN.md only

  IF batch has 2 tasks:
    - TWO Task tool calls in SINGLE message (parallel)
    - Subagent 1 reads task-NN.md
    - Subagent 2 reads task-MM.md
    - Both execute independently

Step 4: After batch completes:
  - Use code-reviewer agent
  - Review BOTH implementations
  - Check for integration issues
  - Verify no conflicts

Step 5: Update manifest
  - Mark tasks as "done"
  - Add completion timestamp

Step 6: Repeat for next batch
```

**Key Implementation Detail - Parallel Execution:**

Per Claude Code documentation:
> "Launch multiple agents concurrently whenever possible, to maximize performance; to do that, use a single message with multiple tool uses"

**Example parallel execution:**
```xml
<function_calls>
  <invoke name="Task">
    <parameter name="subagent_type">typescript-implementer</parameter>
    <parameter name="description">Implement task 1</parameter>
    <parameter name="prompt">Read docs/plans/tasks/feature-task-01.md and implement exactly as specified. Follow TDD: write test first, watch it fail, then implement.</parameter>
  </invoke>
  <invoke name="Task">
    <parameter name="subagent_type">typescript-implementer</parameter>
    <parameter name="description">Implement task 2</parameter>
    <parameter name="prompt">Read docs/plans/tasks/feature-task-02.md and implement exactly as specified. Follow TDD: write test first, watch it fail, then implement.</parameter>
  </invoke>
</function_calls>
```

**Critical:** Both Task tools called in SINGLE message = true parallel execution.

#### 4. /decompose-plan Slash Command

**Location:** `superpowers/commands/decompose-plan.md`

```yaml
---
description: Decompose monolithic plan into parallel task files
argument-hint: "<plan-file>"
allowed-tools: [Bash, Read, Write]
---

Use the decomposing-plans skill exactly as written to break up the monolithic plan into individual task files and identify parallelization opportunities.

The plan file should be: docs/plans/YYYY-MM-DD-<feature-name>.md
```

## Benefits Analysis

### Context Efficiency

**Before:**
- Monolithic plan: ~5000 tokens
- 5 tasks × 5000 tokens each = 25,000 tokens wasted
- Each subagent must parse entire plan

**After:**
- Individual task file: ~500 tokens
- 5 tasks × 500 tokens each = 2,500 tokens total
- **Savings: 90% context reduction**

### Time Efficiency

**Before (Sequential):**
```
Task 1: 10 min
Task 2: 10 min
Task 3: 10 min
Task 4: 10 min
Task 5: 10 min
Total: 50 minutes
```

**After (Parallel - 2 at a time):**
```
Batch 1 (Tasks 1 & 2): 10 min (parallel)
Batch 2 (Tasks 3 & 4): 10 min (parallel)
Batch 3 (Task 5): 10 min
Total: 30 minutes
```

**Savings: 40% time reduction** (for highly parallelizable plans)

### Clarity Benefits

- Each subagent has focused scope
- No ambiguity about which task to implement
- Clear dependencies documented
- Verification checklist per task
- Progress tracking via manifest

## Implementation Checklist

### Phase 1: Core Components
- [ ] Create `superpowers/skills/decomposing-plans/SKILL.md`
- [ ] Create `superpowers/skills/decomposing-plans/decompose-plan.py`
  - [ ] Task parser with regex patterns
  - [ ] Dependency analyzer
  - [ ] File conflict detector
  - [ ] Parallel batch identifier (max 2)
  - [ ] Task file generator
  - [ ] Manifest generator
- [ ] Create `superpowers/skills/parallel-subagent-driven-development/SKILL.md`
- [ ] Create `superpowers/commands/decompose-plan.md`

### Phase 2: Testing
- [ ] Test decompose-plan.py with sample monolithic plan
- [ ] Verify dependency analysis accuracy
- [ ] Verify parallel batch identification
- [ ] Test parallel subagent execution
- [ ] Test code review integration
- [ ] Test manifest updates

### Phase 3: Documentation
- [ ] Update README with new workflow
- [ ] Update `using-superpowers` skill with workflow
- [ ] Create examples in skill directories
- [ ] Add troubleshooting guide

### Phase 4: Integration
- [ ] Test complete workflow: brainstorm → plan → decompose → execute
- [ ] Test with TypeScript project
- [ ] Test with Python project
- [ ] Gather user feedback
- [ ] Iterate based on feedback

## Technical References

### Claude Code Documentation
From official docs:

**Parallel Agent Execution:**
> "Launch multiple agents concurrently whenever possible, to maximize performance; to do that, use a single message with multiple tool uses"

**Tool Access:**
> "When the tools field is omitted, subagents inherit all tools from the main thread (default), including MCP tools."

**Best Practices:**
- Use focused system prompts per agent
- Limit tool access to what's needed
- Use task-specific models (Haiku for simple, Sonnet for complex)

## Success Metrics

### Quantitative
1. **Context usage**: Measure tokens used per task execution
2. **Time to completion**: Compare sequential vs parallel
3. **Accuracy**: Verify correct dependency analysis
4. **Success rate**: Tasks completed without errors

### Qualitative
1. **Developer experience**: Easier to understand workflow?
2. **Debug ease**: Easier to track which task failed?
3. **Flexibility**: Can handle various plan formats?

## Risks & Mitigations

### Risk: Incorrect Dependency Analysis
**Mitigation:**
- Manual review of generated manifest before execution
- Conservative defaults (sequential if uncertain)
- Clear documentation of dependency rules

### Risk: Parallel Tasks Create Conflicts
**Mitigation:**
- File-based dependency detection
- Code review after each batch
- Rollback capability via git

### Risk: Script Parsing Failures
**Mitigation:**
- Multiple regex patterns for different plan formats
- Graceful degradation to sequential execution
- Clear error messages for manual intervention

## Future Enhancements

### Phase 2 Features
1. **Smart batching**: ML-based prediction of task duration to optimize batch sizes
2. **Dynamic parallelism**: Adjust from 2 to 3+ based on task complexity
3. **Interactive manifest editing**: UI for adjusting dependencies
4. **Metrics dashboard**: Track speedups and efficiency gains

### Phase 3 Features
1. **Auto-merge**: Automatic PR creation after all tasks complete
2. **Rollback automation**: One-command rollback of failed batches
3. **Resource optimization**: Haiku for simple tasks, Sonnet for complex
4. **Cross-project learning**: Learn optimal batching from historical data

## References

- Current `subagent-driven-development` skill: `/workspaces/superpowers/superpowers/skills/subagent-driven-development/SKILL.md`
- Current `writing-plans` skill: `/workspaces/superpowers/superpowers/skills/writing-plans/SKILL.md`
- Claude Code parallel execution docs: Retrieved via /docs
- Superpowers architecture: `/workspaces/superpowers/superpowers/README.md`

---

**Next Steps:**
1. Review and approve this plan
2. Begin Phase 1 implementation
3. Test with real-world plan
4. Iterate based on results
