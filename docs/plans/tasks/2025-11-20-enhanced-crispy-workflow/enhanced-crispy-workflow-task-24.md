# Task 24: Update writing-plans skill with execution guidance

## Dependencies
- Previous tasks: none
- Must complete before: none

## Parallelizable
- Can run in parallel with: Task 1, Task 2, Task 3, Task 4, Task 5, Task 6, Task 7, Task 8, Task 9, Task 10, Task 11, Task 12, Task 13, Task 14, Task 15, Task 16, Task 17, Task 18, Task 19, Task 20, Task 21, Task 22, Task 23

## Implementation

**Files:**
- Modify: `cc/skills/writing-plans/SKILL.md`

**Step 1: Read end of current skill**

```bash
tail -50 cc/skills/writing-plans/SKILL.md
```

Expected: See "Execution Handoff" section

**Step 2: Update Execution Handoff section**

Replace the "Execution Handoff" section with:

```markdown
## Execution Handoff

After saving the plan, present execution options:

\`\`\`
Plan complete and saved to \`docs/plans/${filename}.md\`.

## Recommended Next Step: /cc:parse-plan

Decompose this plan into parallel task files. This enables:
- Up to 2 tasks executing concurrently per batch
- ~40% faster execution for parallelizable plans
- 90% context reduction per task

**Best for:** Plans with 4+ tasks

## Alternative: Execute Without Decomposition

Use sequential execution via subagent-driven-development.
- Best for simple plans (1-3 tasks)
- Simpler flow, no decomposition overhead
- One task at a time

## Important

Decomposition is **REQUIRED** for parallel execution.
Always decompose plans with 4+ tasks to enable parallel-subagent-driven-development.

---

Which approach?
A) Decompose plan (/cc:parse-plan) - Recommended
B) Execute sequentially without decomposition
C) Exit (run manually later)
\`\`\`

**If user chooses A:**
- Invoke \`decomposing-plans\` skill
- Proceed with decomposition workflow

**If user chooses B:**
- Invoke \`subagent-driven-development\` skill
- Execute tasks sequentially from monolithic plan

**If user chooses C:**
- Exit workflow
- User can run \`/cc:parse-plan\` or execution commands later
```

**Step 3: Read file to find Execution Handoff section**

```bash
grep -n "Execution Handoff" cc/skills/writing-plans/SKILL.md
```

**Step 4: Read file to prepare for edit**

```bash
cat cc/skills/writing-plans/SKILL.md
```

**Step 5: Commit**

```bash
git add cc/skills/writing-plans/SKILL.md
git commit -m "feat: update writing-plans to recommend decomposition"
```

---

## Success Criteria

- ✅ All new commands accessible via `/cc:*` pattern
- ✅ Research subagents can run in parallel (max 4 concurrent)
- ✅ Memory files follow naming convention with frontmatter metadata
- ✅ `/cc:resume` can restore context from any stage
- ✅ `/cc:review-plan` validates across 4 dimensions
- ✅ `/cc:pr` generates comprehensive descriptions
- ✅ `/cc:crispy` orchestrates full workflow with approval gates
- ✅ Existing skills integrate seamlessly with new workflow

## Testing Plan

**Manual verification after implementation:**

1. **Test research flow:**
   - Run `/cc:brainstorm` → Choose research → Verify subagents spawn
   - Check research.md memory created with correct format

2. **Test plan decomposition:**
   - Create plan with 4+ tasks
   - Run `/cc:parse-plan` → Verify manifest.json and task files

3. **Test plan review:**
   - Run `/cc:review-plan` on a plan
   - Verify validation runs and interactive refinement works

4. **Test save/resume:**
   - Run `/cc:save` at different stages
   - Verify correct memory file created
   - Run `/cc:resume <file>` → Verify context restored

5. **Test PR creation:**
   - Complete execution
   - Run `/cc:pr` → Verify PR created with generated description

6. **Test full orchestrator:**
   - Run `/cc:crispy` from start
   - Verify all steps execute in order
   - Verify approval gates work

7. **Test parallel execution:**
   - Decompose plan with parallel batches
   - Execute → Verify 2 tasks run concurrently
   - Verify code review gates between batches

## Notes

- All agent files use frontmatter metadata for configuration
- Research subagents are defined in `cc/agents/*.md`
- Skills provide detailed instructions for MCP tool usage
- State persistence uses Serena MCP `write_memory`/`read_memory`
- PR creation uses GitHub CLI (`gh`)
- Workflow supports both automatic and manual saves
- Decomposition is REQUIRED for parallel execution

## Files to Modify
- cc/skills/writing-plans/SKILL.md

## Verification Checklist
- [ ] Implementation complete
- [ ] Tests written (TDD - test first!)
- [ ] All tests pass
- [ ] Lint/type check clean
- [ ] Code review requested
- [ ] Code review passed
