---
description: Run complete CrispyClaude workflow from brainstorm to PR creation
---

Run the complete CrispyClaude workflow from ideation to PR creation.

**Prerequisites:** None (orchestrates entire workflow from start)

**Complete Workflow:**

## Step 1: Brainstorm

Invoke the `brainstorming` skill.

At completion, prompt:
```
Ready to:
A) Write the plan
B) Research first

Choose: (A/B)
```

## Step 2: Research (Optional)

If user selects **B**:
- Invoke `research-orchestration` skill
- Skill analyzes brainstorm and suggests researchers
- User can adjust selection (Codebase, Library docs, Web, GitHub)
- Spawns up to 4 subagents in parallel
- Synthesizes findings
- **Automatically saves:** `YYYY-MM-DD-<feature>-research.md`

## Step 3: Write Plan

Invoke `writing-plans` skill.
- Incorporates research findings if available
- Outputs plan to `docs/plans/YYYY-MM-DD-<feature>.md`

## Step 4: Parse Plan

Invoke `decomposing-plans` skill (ALWAYS decompose in crispy workflow).
- Creates task files in `docs/plans/tasks/YYYY-MM-DD-<feature>/`
- Generates manifest with parallel batches

At completion, prompt:
```
Plan decomposed into X tasks across Y batches.

Ready to:
A) Review the plan
B) Execute immediately

Choose: (A/B)
```

## Step 5: Review Plan (Optional)

If user selects **A**:
- Invoke `plan-review` skill
- Validates completeness, quality, feasibility, scope
- Interactive refinement until approved
- Updates plan if changes made

## Step 6: Execute Plan

Invoke `parallel-subagent-driven-development` skill.
- Executes tasks in parallel batches (up to 2 concurrent)
- Code review gate after each batch
- Handles failures with resilience mechanisms

## Step 7: Save Memory

Invoke `state-persistence` skill with `type=complete`.
- Captures implementation learnings, patterns, gotchas
- **Automatically saves:** `YYYY-MM-DD-<feature>-complete.md`

## Step 8: Create PR

Invoke `pr-creation` skill.
- Verifies on feature branch
- Generates PR description from plan, execution, memory
- Pushes branch to remote
- Creates PR with `gh pr create`
- Outputs PR URL

**Workflow Complete!** 🎉

---

**Throughout Workflow:**
- User can run `/cc:save` at any point to pause
- Creates stage-specific memory file
- Later run `/cc:resume <file>` to continue

**Approval Gates:**
- Step 2: Research? (optional)
- Step 5: Review? (optional)

**Automatic Saves:**
- After Step 2: `-research.md`
- After Step 7: `-complete.md`

**Manual Saves:**
- User can `/cc:save` during Steps 3, 6
- Creates `-planning.md` or `-execution.md`
