# Orchestrator Token Optimization Plan

**Created:** 2025-11-20
**Status:** Planning
**Goal:** Reduce orchestrator token usage by 10-30k per execution session

## Problem Statement

Current workflow wastes 10-30k tokens because the orchestrator reads all task files before deploying subagents, then passes that content to subagents who could read the files themselves.

## Fundamental Orchestrator Principle

### The Meta-Problem

This optimization plan itself was created inefficiently. During the planning session, the orchestrator read 519 lines of skill files to analyze them, when it should have deployed a subagent with the instruction "read and analyze the skill files." This is exactly the anti-pattern we're trying to fix.

### The Core Rule

**Orchestrators must NEVER read files themselves (except manifests and memory files). ALL file reading, analysis, and work must be delegated to subagents.**

This is not a suggestion or optimization - it is a fundamental architectural constraint. Violating this principle wastes tokens, bloats context, and defeats the purpose of the orchestrator pattern.

### Orchestrator Responsibilities

**What Orchestrators SHOULD Do:**
- Read manifests only
- Read memory files only
- Deploy subagents with clear instructions
- Track progress with TodoWrite
- Update manifests with task status
- Coordinate dependencies and batching

**What Orchestrators MUST NEVER Do:**
- Read task files
- Read code files
- Read skill files
- Read documentation files
- Perform analysis themselves
- Do implementation work

### The Pattern

**BAD (Current Anti-Pattern):**
```
1. Read file myself (500-2000 tokens)
2. Analyze content in my context
3. Deploy subagent with my analysis
```

**GOOD (Correct Pattern):**
```
1. Deploy subagent with instruction: "Read file X and analyze Y"
2. Subagent reads and analyzes in their fresh context
3. Subagent reports back with findings
```

### Where to Enforce

This principle must be enforced at multiple levels:

1. **In executing-plans skill:** Add as hard requirement with explicit checks
2. **In parallel-subagent-driven-development skill:** Document and enforce
3. **In system instructions:** Make it part of orchestrator identity
4. **In workflow structure:** Make it structurally impossible to violate

The orchestrator should treat non-manifest files like they don't exist. If the orchestrator needs information from a file, it must deploy a subagent to get it.

### Implementation Impact

This principle should be added as Task 5 to update all orchestrator skills with this hard requirement. The skills should not just document this principle - they should enforce it through workflow design.

**Current (Inefficient):**
```typescript
// Orchestrator reads everything
manifest = read('manifest.json')          // ~2k tokens
taskContents = []
for each task in manifest.tasks {
  content = read(task.file)               // ~500-2000 tokens each
  taskContents.push(content)              // WASTE: 20-30k tokens total
}

// Deploy subagents with content
for each task {
  Task({
    prompt: `Here's what to do: ${taskContents[i]}`  // Redundant!
  })
}
```

**Optimized (Target):**
```typescript
// Orchestrator reads ONLY manifest
manifest = read('manifest.json')          // ~2k tokens
                                          // SAVED: 20-30k tokens!

// Deploy subagents with file path
for each task in manifest.tasks {
  Task({
    subagent_type: task.agent_type,      // From manifest
    model: task.model,                    // From manifest
    prompt: `Read and execute: ${task.file}`  // Subagent reads itself
  })
}
```

## Solution Architecture

### Phase 1: Enhance Manifest Schema

Add execution metadata to manifest so orchestrator has everything it needs without reading task files.

**New manifest fields:**
```json
{
  "id": 1,
  "title": "Implement user model",
  "file": "docs/plans/tasks/feature-task-01.md",
  "dependencies": [2],
  "blocks": [3],
  "files": ["src/models/user.ts"],
  "status": "pending",

  // NEW FIELDS FOR TOKEN OPTIMIZATION
  "agent_type": "general-purpose",       // Which subagent to use
  "model": "haiku",                       // Which model (sonnet/haiku/opus)
  "complexity": "simple",                 // Optional: simple/medium/complex -- directly determines what model to use  haiku = simple, sonnet = medium or complex, opus = complex but has much shorter context window
  "estimated_tokens": 500                 // Optional: for planning
}
```

**Agent type inference rules:**
```typescript
// Based on task content and files
if (files.some(f => f.endsWith('.ts') || f.endsWith('.tsx'))) {
  if (task.includes('implement') || task.includes('refactor')) {
    agent_type = 'typescript-implementer'
  }
}
else if (files.some(f => f.endsWith('.py'))) {
  agent_type = 'python-implementer'
}
else if (files.some(f => f.endsWith('.md'))) {
  agent_type = 'general-purpose'
}
else {
  agent_type = 'general-purpose'  // Default
}
```
## note, we should think of some more basic agents to bake in

**Model inference rules:**
```typescript
// Based on complexity
if (complexity === 'simple' || task.includes('create file')) {
  model = 'haiku'     // Fast, cheap for simple tasks
}
else if (complexity === 'complex' || files.length > 3) {
  model = 'sonnet'    // Smart, for complex tasks
}
else {
  model = 'sonnet'    // Default to quality
}
```

**Complexity inference rules:**
```typescript
// Based on various signals
let complexity_score = 0

// File count
if (files.length === 1) complexity_score += 0
if (files.length === 2-3) complexity_score += 1
if (files.length > 3) complexity_score += 2

// Keywords
if (task.includes('refactor')) complexity_score += 2
if (task.includes('implement')) complexity_score += 1
if (task.includes('create file')) complexity_score += 0
if (task.includes('update')) complexity_score += 1

// Verification steps
verification_steps = count_checklist_items(task)
if (verification_steps > 5) complexity_score += 1

// Result
if (complexity_score <= 2) complexity = 'simple'
else if (complexity_score <= 4) complexity = 'medium'
else complexity = 'complex'
```

### Phase 2: Update decomposing-plans Skill

Modify the Python decomposition script to generate enhanced manifests.

**File:** `superpowers/skills/decomposing-plans/decompose-plan.py`

**Changes:**

1. **Add agent type inference:**
```python
def infer_agent_type(task_content: str, files: List[str]) -> str:
    """Infer which agent type should execute this task."""

    # Check file extensions
    ts_files = [f for f in files if f.endswith(('.ts', '.tsx', '.js', '.jsx'))]
    py_files = [f for f in files if f.endswith('.py')]
    md_files = [f for f in files if f.endswith('.md')]

    # TypeScript/JavaScript tasks
    if ts_files and ('implement' in task_content.lower() or
                     'refactor' in task_content.lower()):
        return 'typescript-implementer'

    # Python tasks
    if py_files and ('implement' in task_content.lower() or
                     'refactor' in task_content.lower()):
        return 'python-implementer'

    # Markdown/documentation tasks
    if md_files or 'create file' in task_content.lower():
        return 'general-purpose'

    # Default
    return 'general-purpose'
```

2. **Add model recommendation:**
```python
def recommend_model(task_content: str, complexity: str, files: List[str]) -> str:
    """Recommend model based on task complexity."""

    # Simple file creation = haiku
    if complexity == 'simple' and 'create file' in task_content.lower():
        return 'haiku'

    # Complex refactoring = sonnet
    if complexity == 'complex' or len(files) > 3:
        return 'sonnet'

    # Agent-specific rules
    if 'review' in task_content.lower() or 'analyze' in task_content.lower():
        return 'sonnet'  # Analysis needs intelligence

    # Default
    return 'sonnet'
```

# There is also Opus, which should be rarely used but is good for one-shot complex situations that require higher thinking levels, yet also has a slightly lower context window as sonnet.  

3. **Add complexity estimation:**
```python
def estimate_complexity(task_content: str, files: List[str]) -> str:
    """Estimate task complexity: simple, medium, complex."""

    score = 0

    # File count
    score += min(len(files), 3)

    # Keywords
    if 'refactor' in task_content.lower(): score += 2
    if 'implement' in task_content.lower(): score += 1
    if 'create file' in task_content.lower(): score += 0
    if 'update' in task_content.lower(): score += 1

    # Verification steps
    checklist_items = task_content.count('- [ ]')
    if checklist_items > 5: score += 1

    # Result
    if score <= 2: return 'simple'
    elif score <= 4: return 'medium'
    else: return 'complex'
```
# this should be reviewed and researched with anthropic suggestions for when to use haiku etc

4. **Update manifest generation:**
```python
def create_manifest(plan_file, tasks, parallel_batches):
    manifest = {
        "plan": plan_file,
        "feature": extract_feature_name(plan_file),
        "created": datetime.now().isoformat(),
        "total_tasks": len(tasks),
        "tasks": []
    }

    for task in tasks:
        complexity = estimate_complexity(task['content'], task['files'])

        manifest['tasks'].append({
            "id": task['id'],
            "title": task['title'],
            "file": task['file'],
            "dependencies": task['dependencies'],
            "blocks": task['blocks'],
            "files": task['files'],
            "status": "pending",

            # NEW: Execution metadata
            "agent_type": infer_agent_type(task['content'], task['files']),
            "model": recommend_model(task['content'], complexity, task['files']),
            "complexity": complexity,
            "estimated_tokens": estimate_token_count(task['content'])
        })

    manifest['parallel_batches'] = parallel_batches
    return manifest
```

### Phase 3: Update Execution Skills

Modify execution skills to use manifest-only pattern.

**File:** `cc/skills/parallel-subagent-driven-development/SKILL.md` (or executing-plans)

**Changes:**

**Before (reads all task files):**
```python
# Load manifest
manifest = read('manifest.json')

# Load all task files (WASTEFUL!)
task_contents = {}
for task in manifest.tasks:
    content = read(task.file)  # 500-2000 tokens each
    task_contents[task.id] = content

# Deploy subagents
for batch in manifest.parallel_batches:
    for task_id in batch:
        task = find_task(task_id)
        Task({
            subagent_type: 'general-purpose',  # Hardcoded
            prompt: f"Execute this task:\n\n{task_contents[task_id]}"
        })
```

**After (reads only manifest):**
```python
# Load manifest ONLY
manifest = read('manifest.json')

# Deploy subagents (no task file reads!)
for batch in manifest.parallel_batches:
    for task_id in batch:
        task = find_task(task_id)

        Task({
            subagent_type: task.agent_type,  # From manifest
            model: task.model,                # From manifest
            description: task.title,
            prompt: f"""
Read and execute the task file: {task.file}

Follow all instructions in the task file exactly.
Commit with the message specified in the task.
Report back with:
- Confirmation of completion
- Commit hash
- Any issues encountered
"""
        })
```

**Token savings:**
- Before: 2k (manifest) + 20k (task files) = 22k tokens
- After: 2k (manifest) only = 2k tokens
- **Saved: 20k tokens (90% reduction)**

### Phase 4: Update Skills Documentation

Update skill documentation to reflect new pattern.

**Files to update:**
1. `cc/skills/decomposing-plans/SKILL.md` - Document new manifest fields
2. `cc/skills/executing-plans/SKILL.md` - Document manifest-only pattern
3. `cc/skills/parallel-subagent-driven-development/SKILL.md` - Update execution logic

## Implementation Tasks

### Task 1: Update decompose-plan.py Script

**Files:**
- `superpowers/skills/decomposing-plans/decompose-plan.py`

**Changes:**
1. Add `infer_agent_type()` function
2. Add `recommend_model()` function
3. Add `estimate_complexity()` function
4. Add `estimate_token_count()` function
5. Update `create_manifest()` to include new fields

**Verification:**
- Run script on existing plan
- Verify manifest has agent_type, model, complexity fields
- Verify inference makes sense for different task types

### Task 2: Update decomposing-plans Skill Documentation

**Files:**
- `cc/skills/decomposing-plans/SKILL.md`

**Changes:**
1. Update manifest format section to show new fields
2. Add "Agent Type Inference" section explaining rules
3. Add "Model Recommendation" section explaining rules
4. Add "Complexity Estimation" section explaining rules

**Verification:**
- Skill documentation is clear and complete
- Examples show new manifest format

### Task 3: Update Execution Skills

**Files:**
- `cc/skills/executing-plans/SKILL.md`
- `cc/skills/parallel-subagent-driven-development/SKILL.md` (create if needed)

**Changes:**
1. Update to manifest-only pattern
2. Remove task file reading logic
3. Use agent_type and model from manifest
4. Update examples to show optimized pattern

**Verification:**
- Skill uses manifest-only pattern
- No task file reads in orchestrator
- Subagents receive task file path, not content

### Task 4: Create Example/Test

**Files:**
- `docs/plans/2025-11-20-test-optimization.md` (test plan)

**Changes:**
1. Create small test plan (3-5 tasks)
2. Decompose with updated script
3. Verify manifest has new fields
4. Execute with updated execution skill
5. Measure token savings

**Verification:**
- Manifest has correct agent_type and model
- Execution uses manifest-only pattern
- Token usage reduced by 10-30k

### Task 5: Enforce Orchestrator Token Efficiency Principle

**Files:**
- `cc/skills/using-crispyclaude/SKILL.md` <-- this is injected into every session
- `cc/skills/executing-plans/SKILL.md`
- `cc/skills/parallel-subagent-driven-development/SKILL.md`
- Any system instructions or orchestrator context files

**Changes:**
1. Add "Fundamental Orchestrator Principle" section to both skills
2. Make manifest-only pattern a hard requirement (not optional)
3. Add explicit prohibition against reading task files
4. Update workflow instructions to enforce this structurally
5. Add examples showing correct vs. incorrect patterns
6. Update any orchestrator system prompts to include this principle

**Key Requirements to Add:**
- "NEVER read task files - only read manifests"
- "Deploy subagents with task file paths, not content"
- "If you need information from a file, deploy a subagent to read it"
- "Treat all non-manifest files as inaccessible from orchestrator context"

**Verification:**
- Skills explicitly forbid orchestrator file reading
- Workflow makes it structurally difficult to violate principle
- Examples clearly show manifest-only pattern
- No ambiguity about what orchestrators can/cannot read

## Success Criteria

### Quantitative

1. **Token reduction:** Orchestrator uses 10-30k fewer tokens per execution
2. **Manifest completeness:** 100% of tasks have agent_type and model
3. **Inference accuracy:** 95%+ of agent_type/model recommendations are appropriate

### Qualitative

1. **Orchestrator simplicity:** Orchestrator code is simpler (no task file reads)
2. **Subagent clarity:** Subagents get clear, self-contained instructions
3. **Maintainability:** Easy to add new agent types and models

## Risks and Mitigations

### Risk 1: Inference Errors

**Risk:** Agent type or model inference is wrong for some tasks

**Mitigation:**
- Allow manual override in manifest
- Log inference decisions for debugging
- Test on diverse task types
- Iterate on inference rules

### Risk 2: Backward Compatibility

**Risk:** Existing manifests don't have new fields

**Mitigation:**
- Provide defaults (agent_type='general-purpose', model='sonnet')
- Update execution skills to handle old manifests
- Document migration path

### Risk 3: Subagent Context

**Risk:** Subagents might need more context than just task file

**Mitigation:**
- Ensure task files are self-contained
- Allow orchestrator to pass additional context if needed
- Monitor subagent success rates

## Rollout Plan

### Phase 1: Development (2-3 hours)
1. Update decompose-plan.py with inference logic
2. Test on sample plans
3. Verify manifest quality

### Phase 2: Documentation (1 hour)
1. Update skill documentation
2. Add examples
3. Document inference rules

### Phase 3: Integration (1 hour)
1. Update execution skills
2. Test end-to-end workflow
3. Measure token savings

### Phase 4: Validation (1 hour)
1. Run on real plans
2. Verify token savings
3. Check inference accuracy
4. Iterate if needed

## Future Enhancements

### Enhancement 1: Smart Model Selection

Based on actual execution data:
- Track which models work best for which task types
- Use historical data to improve recommendations
- Adapt to new model releases

### Enhancement 2: Parallel Batch Optimization

Enhance parallel batch detection:
- Consider agent type (don't mix different agent types in batch)
- Consider model (group by model for better batching)
- Consider estimated tokens (balance batch sizes)

### Enhancement 3: Cost Optimization

Add cost awareness:
- Estimate cost per task (tokens × model price)
- Optimize for cost vs. speed trade-offs
- Track actual costs vs. estimates

## Appendix A: Manifest Schema v2

```typescript
interface Task {
  id: number
  title: string
  file: string                    // Path to task file
  dependencies: number[]
  blocks: number[]
  files: string[]                 // Files this task modifies
  status: 'pending' | 'in_progress' | 'done' | 'blocked'
  completed_at?: string

  // NEW: Execution metadata (v2)
  agent_type: 'general-purpose' | 'typescript-implementer' | 'python-implementer' | 'code-reviewer'
  model: 'sonnet' | 'haiku' | 'opus'
  complexity?: 'simple' | 'medium' | 'complex'
  estimated_tokens?: number
}

interface Manifest {
  plan: string
  feature: string
  created: string
  total_tasks: number
  tasks: Task[]
  parallel_batches: number[][]

  // Optional: Execution stats
  stats?: {
    total_estimated_tokens: number
    total_estimated_cost: number
    parallel_speedup_percent: number
  }
}
```

## Appendix B: Token Savings Analysis

### Current Session Analysis

**Session:** 2025-11-20 Enhanced CrispyClaude Workflow Execution

**Orchestrator reads:**
- manifest.json: ~2k tokens
- 24 task files: ~24 × 500 = 12k tokens (conservative estimate)
- **Total: ~14k tokens read by orchestrator**

**With optimization:**
- manifest.json: ~2k tokens
- task files: 0 tokens (subagents read their own)
- **Total: ~2k tokens**

**Savings:**
- Absolute: 12k tokens
- Percentage: 85% reduction
- Impact: More headroom for conversation, larger plans possible

**Projected savings for larger plans:**
- 50 tasks: ~25k tokens saved
- 100 tasks: ~50k tokens saved
- Enables much larger plan executions within context window

## Appendix C: Agent Type Reference

### general-purpose
- **Use for:** File creation, markdown editing, simple updates
- **Tools:** Read, Write, Edit, Bash, Grep, Glob
- **Best for:** Tasks that don't require language-specific expertise

### typescript-implementer
- **Use for:** TypeScript/JavaScript implementation
- **Tools:** Read, Write, MultiEdit, Bash, Grep
- **Best for:** Complex TS/JS code, refactoring, type-safe implementations

### python-implementer
- **Use for:** Python implementation
- **Tools:** Read, Write, MultiEdit, Bash, Grep
- **Best for:** Complex Python code, async patterns, type hints

### code-reviewer
- **Use for:** Code review after major implementations
- **Tools:** All tools
- **Best for:** Validation, quality checks, plan adherence

### Think of some more common Agent Types  (task reviewer? orchestrator helper?)

## Next Steps

1. Review this plan
2. Get approval for approach
3. Execute implementation tasks
4. Validate with real-world plans
5. Iterate based on results
