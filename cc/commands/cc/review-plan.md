Use the plan-review skill to validate implementation plans for completeness, quality, feasibility, and scope.

**Prerequisites:**
- Plan file exists: `docs/plans/YYYY-MM-DD-<feature>.md`
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
