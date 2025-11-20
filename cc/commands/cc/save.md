Use the state-persistence skill to save workflow state to Serena MCP memory.

**Prerequisites:** At least one of:
- Brainstorm + research completed
- Plan file exists
- Execution in progress
- Execution complete

**What this does:**

**Stage Detection (automatic):**
- Analyzes current workflow state
- Determines stage: research, planning, execution, or complete
- Extracts feature name from plan or brainstorm
- Collects git metadata (commit, branch)

**Saves to:** `YYYY-MM-DD-<feature-name>-<stage>.md`

**Stage-specific content:**

**research.md** - After research completes
- Brainstorm summary
- Codebase findings (Serena)
- Library docs (Context7)
- Web research
- GitHub research

**planning.md** - During plan writing
- Design decisions
- Alternatives considered
- Plan draft
- Open questions

**execution.md** - During implementation
- Progress summary (X/Y tasks complete)
- Completed tasks
- Current task state
- Blockers/issues

**complete.md** - After workflow completion
- What was built
- Key learnings and gotchas
- Files modified
- Patterns introduced
- Recommendations

**Resume later with:** `/cc:resume <filename>`
