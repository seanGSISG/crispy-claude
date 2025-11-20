---
date: 2025-11-20T03:45:00+00:00
git_commit: 93f9cdd
branch: main
repository: crispy-claude
topic: "Orchestrator Token Optimization - Meta-Insight Session"
tags: [optimization, orchestrator, token-efficiency, meta-learning]
status: planning
last_updated: 2025-11-20
type: research
---

# Session Summary: Orchestrator Token Optimization Discovery

## Context

Session started with continuation of Enhanced CrispyClaude Workflow execution (24/24 tasks completed). During execution review, discovered critical optimization opportunity.

## Key Discovery

**Problem Identified:** Orchestrators waste 10-30k tokens by reading all task files before deploying subagents, when subagents could read the files themselves.

**Current Anti-Pattern:**
```typescript
// Orchestrator reads everything (WASTEFUL)
manifest = read('manifest.json')        // 2k tokens
for each task:
  content = read(task.file)             // 500-2000 tokens each
  deploy subagent with content          // Waste: 20-30k tokens
```

**Optimized Pattern:**
```typescript
// Orchestrator reads only manifest (EFFICIENT)
manifest = read('manifest.json')        // 2k tokens only
for each task:
  deploy subagent with file path        // Subagent reads itself
  // Saved: 20-30k tokens!
```

## Meta-Insight

**The Critical Realization:** Even while documenting this optimization, I violated the principle by reading 519 lines of skill files instead of deploying a subagent to analyze them.

**The Fundamental Rule:**
> Orchestrators must NEVER read files themselves (except manifests and memory files). ALL file reading, analysis, and work must be delegated to subagents.

This is not a suggestion - it's an architectural constraint that must be enforced structurally.

## Solution Designed

**Created Plan:** `docs/plans/2025-11-20-orchestrator-token-optimization.md`

### Phase 1: Enhanced Manifest Schema

Add execution metadata so orchestrator has everything needed without reading task files:

```json
{
  "agent_type": "general-purpose",  // Which subagent to use
  "model": "haiku",                 // Which model
  "complexity": "simple",           // Task complexity
  "estimated_tokens": 500           // Planning estimate
}
```

### Phase 2: Automated Inference

Decompose-plan.py script will automatically infer:
- **Agent type:** From file extensions and task keywords
- **Model:** From complexity (haiku=simple, sonnet=complex)
- **Complexity:** From file count, keywords, verification steps

### Phase 3: Manifest-Only Execution

Update executing-plans and parallel-subagent-driven-development skills to:
- Read ONLY manifest.json
- Deploy subagents with task file path (not content)
- Let subagents read their own task files

### Phase 4: Structural Enforcement

Add Task 5 to enforcement the principle in all orchestrator skills:
- Hard requirement in executing-plans
- Hard requirement in parallel-subagent-driven-development
- Update system instructions
- Make violation structurally impossible

## Token Savings Analysis

**This Session (24 tasks):**
- Current: ~14k tokens (manifest + task files)
- Optimized: ~2k tokens (manifest only)
- Savings: ~12k tokens (85% reduction)

**Projected (larger plans):**
- 50 tasks: ~25k tokens saved
- 100 tasks: ~50k tokens saved
- Enables much larger plan executions within context limits

## Implementation Tasks

5 tasks identified in plan:

1. **Update decompose-plan.py** - Add inference functions for agent_type, model, complexity
2. **Update decomposing-plans skill** - Document new manifest fields and inference rules
3. **Update execution skills** - Implement manifest-only pattern
4. **Create test case** - Validate token savings on sample plan
5. **Enforce principle** - Add hard requirements to all orchestrator skills

## Orchestrator Responsibilities (The Rule)

**MUST DO:**
- ✅ Read manifests only
- ✅ Read memory files only
- ✅ Deploy subagents with clear instructions
- ✅ Track progress with TodoWrite
- ✅ Update manifests with task status
- ✅ Coordinate dependencies and batching

**MUST NEVER DO:**
- ❌ Read task files
- ❌ Read code files
- ❌ Read skill files
- ❌ Read documentation files
- ❌ Perform analysis themselves
- ❌ Do implementation work

## Why This Matters

1. **Token Efficiency:** Saves 10-30k tokens per execution session
2. **Scalability:** Enables larger plans within context limits
3. **Clarity:** Clear separation of orchestrator (coordinate) vs. subagent (execute)
4. **Architectural Integrity:** Enforces proper abstraction boundaries

## Pattern Recognition

This optimization applies to ANY orchestrator pattern:
- Plan execution (executing-plans)
- Parallel execution (parallel-subagent-driven-development)
- Research orchestration (research-orchestration)
- Any workflow that coordinates multiple subagents

**Universal Principle:** Orchestrators coordinate, subagents execute. Never mix roles.

## Next Steps

1. Review and approve optimization plan
2. Execute 5 implementation tasks
3. Validate with real-world plan execution
4. Measure actual token savings
5. Iterate based on results

## Files Created This Session

**Planning:**
- `docs/plans/2025-11-20-orchestrator-token-optimization.md` (16KB comprehensive plan)

**Memory:**
- `2025-11-20-enhanced-crispy-workflow-execution.md` (completion memory from earlier)
- `2025-11-20-session-orchestrator-optimization-insight.md` (this file)

## Key Learnings

1. **Self-Discovery:** The best insights come from observing our own inefficiencies
2. **Meta-Learning:** Documenting a problem often reveals you're still doing it
3. **Structural Enforcement:** Principles must be enforced structurally, not just documented
4. **Token Consciousness:** Every file read has a cost - be intentional

## For Future Sessions

When resuming orchestrator optimization work:
- Start with plan: `docs/plans/2025-11-20-orchestrator-token-optimization.md`
- Refer to this memory for context and rationale
- Remember: Deploy subagents for ALL file reading and analysis
- Test token savings on real plans before marking complete

## Session Statistics

- Duration: ~2 hours (workflow execution + optimization discovery)
- Tasks completed: 24/24 (enhanced workflow) + 1 planning task
- Files created: 28 total (24 workflow + 1 plan + 3 memories)
- Token usage: ~108k tokens (would have been ~92k with optimization)
- Key insight: Orchestrator token efficiency principle

## Quote of the Session

> "We need a way to make it so the primary orchestrator (you) do not have to read any files to get context. You should simply know what agent to call, what task file to point them to... all YOU should do is just read the manifest.json then deploy." - User insight that sparked this optimization
