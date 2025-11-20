# Task 21: Update brainstorming skill

## Dependencies
- Previous tasks: none
- Must complete before: none

## Parallelizable
- Can run in parallel with: Task 1, Task 2, Task 3, Task 4, Task 5, Task 6, Task 7, Task 8, Task 9, Task 10, Task 11, Task 12, Task 13, Task 14, Task 15, Task 16, Task 17, Task 18, Task 19, Task 20, Task 22, Task 23, Task 24

## Implementation

**Files:**
- Modify: `cc/skills/brainstorming/SKILL.md`

**Step 1: Read current skill**

```bash
cat cc/skills/brainstorming/SKILL.md | tail -50
```

Expected: See end of brainstorming skill

**Step 2: Add research prompt using Edit**

Add this section at the end of the "After the Design" section (before any final notes):

```markdown
### Next Steps

After design is complete, prompt user:

\`\`\`
Design complete! Ready to:
A) Write the plan
B) Research first (gather codebase insights, library docs, best practices)

Choose: (A/B)
\`\`\`

**If user chooses A:**
- Proceed directly to \`writing-plans\` skill

**If user chooses B:**
- Invoke \`research-orchestration\` skill
- Research skill will:
  - Analyze brainstorm context
  - Suggest researchers: \`[✓] Codebase [✓] Library docs [✓] Web [ ] GitHub\`
  - Allow user to adjust selection
  - Spawn selected subagents (max 4 in parallel)
  - Synthesize findings
  - Automatically save to \`YYYY-MM-DD-<feature>-research.md\`
  - Report: "Research complete. Ready to write the plan."
- Then proceed to \`writing-plans\` skill with research context
```

**Step 3: Locate insertion point**

```bash
grep -n "After the Design" cc/skills/brainstorming/SKILL.md
```

Expected: Find line number of "After the Design" section

**Step 4: Read section to find exact insertion point**

```bash
# Read the "After the Design" section
sed -n '/## After the Design/,/^## /p' cc/skills/brainstorming/SKILL.md
```

Expected: See the section content

**Step 5: Use Edit tool to add content**

Find the end of "After the Design" section and add the new "Next Steps" subsection there.

Note: This will require reading the full file first, then using Edit.

**Step 6: Read file to prepare for edit**

```bash
cat cc/skills/brainstorming/SKILL.md
```

**Step 7: Commit**

```bash
git add cc/skills/brainstorming/SKILL.md
git commit -m "feat: update brainstorming skill to prompt for research"
```

## Files to Modify
- cc/skills/brainstorming/SKILL.md

## Verification Checklist
- [ ] Implementation complete
- [ ] Tests written (TDD - test first!)
- [ ] All tests pass
- [ ] Lint/type check clean
- [ ] Code review requested
- [ ] Code review passed
