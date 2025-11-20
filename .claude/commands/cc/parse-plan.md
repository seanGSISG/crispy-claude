---
description: Decompose monolithic plan into parallel task files
argument-hint: "[plan-file]"
---

Use the decomposing-plans skill to break down a monolithic plan into parallel task files.

**Prerequisites:**
- Plan file exists: `docs/plans/YYYY-MM-DD-<feature>.md`
- Plan has 2+ tasks worth decomposing

**What this does:**
1. Reads the monolithic plan
2. Identifies parallelizable tasks
3. Creates task files in `docs/plans/tasks/YYYY-MM-DD-<feature>/`
4. Generates `manifest.json` with parallel batches
5. Prompts for next step: review or execute

**Output:**
- Task files: One per task
- Manifest: Defines batch execution order
- Enables parallel execution (up to 4 tasks per batch)

**Recommendation:** Always decompose plans with 4+ tasks for parallel execution.

**Next step:** Review plan or execute immediately
