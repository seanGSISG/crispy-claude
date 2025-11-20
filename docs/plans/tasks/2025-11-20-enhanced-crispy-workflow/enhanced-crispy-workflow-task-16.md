# Task 16: Create /cc:review-plan command

## Dependencies
- Previous tasks: 1, 2, 3
- Must complete before: none

## Parallelizable
- Can run in parallel with: Task 4, Task 5, Task 6, Task 7, Task 8, Task 9, Task 10, Task 11, Task 12, Task 13, Task 14, Task 15, Task 17, Task 18, Task 19, Task 20, Task 21, Task 22, Task 23, Task 24

## Implementation

**Files:**
- Create: `cc/commands/cc/review-plan.md`

**Step 1: Write command file**

Create `cc/commands/cc/review-plan.md`:

```markdown
Use the plan-review skill to validate implementation plans for completeness, quality, feasibility, and scope.

**Prerequisites:**
- Plan file exists: \`docs/plans/YYYY-MM-DD-<feature>.md\`
- Optional: Plan decomposed (can review before or after)

**What this does:**

**Phase 1:** Initial assessment across 4 dimensions
- Completeness: Success criteria, rollback, edge cases
- Quality: File paths, specific references, measurable criteria
- Feasibility: Prerequisites exist, assumptions valid
- Scope: Aligned with brainstorm, no gold-plating

**Phase 2:** If any dimension fails, spawns specialized validators
- completeness-checker
- feasibility-analyzer (uses Serena to verify codebase)
- scope-creep-detector (compares to brainstorm/research)
- quality-validator

**Phase 3:** Interactive refinement
- Ask questions one at a time
- Offer concrete options
- Update plan with agreed changes
- Re-check until all pass or user approves warnings

**Exit:** Plan approved and ready for execution

**Next step:** Execute plan
```

**Step 2: Verify file created**

```bash
cat cc/commands/cc/review-plan.md
```

Expected: Command content visible

**Step 3: Commit**

```bash
git add cc/commands/cc/review-plan.md
git commit -m "feat: add /cc:review-plan command"
```

## Files to Modify
- cc/commands/cc/review-plan.md

## Verification Checklist
- [ ] Implementation complete
- [ ] Tests written (TDD - test first!)
- [ ] All tests pass
- [ ] Lint/type check clean
- [ ] Code review requested
- [ ] Code review passed
