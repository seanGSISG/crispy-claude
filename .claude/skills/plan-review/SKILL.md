---
name: plan-review
description: Use after plan is written to validate implementation plans across completeness, quality, feasibility, and scope dimensions - spawns specialized validators for failed dimensions and refines plan interactively before execution
---

# Plan Review

Use this skill to validate implementation plans across completeness, quality, feasibility, and scope dimensions.

## When to Use

After plan is written and user selects "A) review the plan" option.

## Phase 1: Initial Assessment

Run automatic checks across 4 dimensions using simple validation logic (no subagents yet):

### Completeness Check

Scan plan for:
- ✅ All phases have success criteria section
- ✅ Commands for verification present (`make test-`, `pytest`, etc.)
- ✅ Rollback/migration strategy mentioned
- ✅ Edge cases section or error handling
- ✅ Testing strategy defined

**Scoring:**
- PASS: All criteria present
- WARN: 1-2 criteria missing
- FAIL: 3+ criteria missing

### Quality Check

Scan plan for:
- ✅ File paths with line numbers: `file.py:123`
- ✅ Specific function/class names
- ✅ Code examples are complete (not pseudocode)
- ✅ Success criteria are measurable
- ❌ Vague language: "properly", "correctly", "handle", "add validation" without specifics

**Scoring:**
- PASS: File paths present, code complete, criteria measurable, no vague language
- WARN: Some file paths missing or minor vagueness
- FAIL: No file paths, pseudocode only, vague criteria

### Feasibility Check

Basic checks (detailed check needs subagent):
- ✅ References to existing files/functions seem reasonable
- ✅ No obvious impossibilities
- ✅ Technology choices are compatible
- ✅ Libraries mentioned are standard/available

**Scoring:**
- PASS: Seems feasible on surface
- WARN: Some questionable assumptions
- FAIL: Obvious blockers or impossibilities

### Scope Creep Check

Requires research.md memory or brainstorm context:
- ✅ "What We're NOT Doing" section exists
- ✅ Features align with original brainstorm
- ❌ New features added without justification
- ❌ Gold-plating or over-engineering patterns

**Scoring:**
- PASS: Scope aligned with original decisions
- WARN: Minor scope expansion, can justify
- FAIL: Significant scope creep or gold-plating

## Phase 2: Escalation (If Needed)

If **any dimension scores FAIL**, spawn specialized validators:

```typescript
const failedDimensions = {
  completeness: score === 'FAIL',
  quality: score === 'FAIL',
  feasibility: score === 'FAIL',
  scope: score === 'FAIL'
}

// Spawn validators in parallel for failed dimensions
const validations = await Promise.all([
  ...(failedDimensions.completeness ? [Task({
    subagent_type: "completeness-checker",
    description: "Validate plan completeness",
    prompt: `
      Analyze this implementation plan for completeness.

      Plan file: ${planPath}

      Check for:
      - Success criteria (automated + manual)
      - Dependencies between phases
      - Rollback/migration strategy
      - Edge cases and error handling
      - Testing strategy

      Report issues and recommendations.
    `
  })] : []),

  ...(failedDimensions.feasibility ? [Task({
    subagent_type: "feasibility-analyzer",
    description: "Verify plan feasibility",
    prompt: `
      Verify this implementation plan is feasible.

      Plan file: ${planPath}

      Use Serena MCP to check:
      - All referenced files/functions exist
      - Libraries are in dependencies
      - Integration points match reality
      - No technical blockers

      Report what doesn't exist or doesn't match assumptions.
    `
  })] : []),

  ...(failedDimensions.scope ? [Task({
    subagent_type: "scope-creep-detector",
    description: "Check scope alignment",
    prompt: `
      Compare plan against original brainstorm for scope creep.

      Plan file: ${planPath}
      Research/brainstorm: ${researchMemoryPath}

      Check for:
      - Features not in original scope
      - Gold-plating or over-engineering
      - "While we're at it" additions
      - Violations of "What We're NOT Doing"

      Report scope expansions and recommend removals.
    `
  })] : []),

  ...(failedDimensions.quality ? [Task({
    subagent_type: "quality-validator",
    description: "Validate plan quality",
    prompt: `
      Check this implementation plan for quality issues.

      Plan file: ${planPath}

      Check for:
      - Vague language vs. specific actions
      - Missing file:line references
      - Untestable success criteria
      - Incomplete code examples

      Report specific quality issues and improvements.
    `
  })] : [])
])
```

## Phase 3: Interactive Refinement

Present findings conversationally (like brainstorming skill):

```markdown
I've reviewed the plan. Here's what I found:

**Completeness: ${score}**
${if issues:}
- ${issue-1}
- ${issue-2}

**Quality: ${score}**
${if issues:}
- ${issue-1}
- ${issue-2}

**Feasibility: ${score}**
${if issues:}
- ${issue-1}
- ${issue-2}

**Scope: ${score}**
${if issues:}
- ${issue-1}
- ${issue-2}

${if any FAIL:}
Let's address these issues. Starting with ${most-critical-dimension}:

Q1: ${specific-question}
   A) ${option-1}
   B) ${option-2}
   C) ${option-3}
```

### Question Flow

Ask **one question at a time**, wait for answer, then next question.

For each issue:
1. Explain the problem clearly
2. Offer 2-4 concrete options
3. Allow "other" for custom response
4. Apply user's decision immediately
5. Update plan if changes agreed
6. Move to next issue

### Refinement Loop

After addressing all issues:
1. Update plan file with agreed changes
2. Re-run Phase 1 assessment
3. If still FAIL, spawn relevant validators again
4. Continue until all dimensions PASS or user approves WARN

### Approval

When all dimensions PASS or user accepts WARN:

```markdown
Plan review complete! ✅

**Final Scores:**
- Completeness: PASS
- Quality: PASS
- Feasibility: PASS
- Scope: PASS

The plan is ready for execution.
```

If user approved with WARN:

```markdown
Plan review complete with warnings.

**Final Scores:**
- Completeness: PASS
- Quality: WARN (minor file path gaps)
- Feasibility: PASS
- Scope: PASS

Warnings acknowledged. Proceeding with execution.
```

## Plan Updates

When making changes based on review:

1. Read current plan file
2. Apply specific edits using Edit tool
3. Preserve structure and formatting
4. Update only sections with issues
5. Verify changes with re-read

Don't rewrite entire plan - use targeted edits.

## Exit Conditions

**Success:** All PASS or user approves WARN
**Abort:** User requests to skip review and execute anyway
**Restart:** User requests major redesign (back to brainstorm)

## Example Session

```markdown
I've reviewed the plan. Here's what I found:

**Completeness: ⚠️ WARN**
- Phase 2 lacks automated success criteria

**Quality: ✅ PASS**

**Feasibility: ❌ FAIL**
- Plan assumes `src/auth/handler.py` exists - NOT FOUND

**Scope: ❌ FAIL**
- Plan includes "admin dashboard" but brainstorm only mentioned "user dashboard"

Let's address these issues. Starting with scope:

Q1: The plan includes an admin dashboard, but your brainstorm only mentioned a user dashboard. Should we:
   A) Remove admin dashboard (stick to original scope)
   B) Keep it (intentional expansion)
   C) Split admin dashboard into separate plan

User: A

Got it. I'll remove the admin dashboard from the plan.

[Updates plan, removes admin dashboard task]

Next, feasibility:

Q2: The plan references `src/auth/handler.py` but this file doesn't exist. I found `src/security/auth.py:45` with similar functionality. Should we:
   A) Create new `src/auth/handler.py` as planned
   B) Use existing `src/security/auth.py` instead
   C) Rename existing file to match plan

User: B

Makes sense. I'll update the plan to use `src/security/auth.py`.

[Updates plan with correct file paths]

Finally, completeness:

Q3: Phase 2 doesn't have automated success criteria. Should we add:
   A) `make test-auth` command to verify
   B) Specific pytest command
   C) Manual testing steps only

User: A

Perfect. I'll add `make test-auth` verification to Phase 2.

[Updates plan with verification command]

Re-checking plan with fixes...

**Final Scores:**
- Completeness: ✅ PASS
- Quality: ✅ PASS
- Feasibility: ✅ PASS
- Scope: ✅ PASS

Plan review complete! The plan is ready for execution.
```
