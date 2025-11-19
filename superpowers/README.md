# Superpowers

A comprehensive skills library of proven techniques, patterns, and workflows for AI coding assistants.

## What You Get

- **Testing Skills** - TDD, async testing, anti-patterns
- **Debugging Skills** - Systematic debugging, root cause tracing, verification
- **Collaboration Skills** - Brainstorming, planning, code review, parallel agents
- **Development Skills** - Git worktrees, finishing branches, subagent workflows
- **Meta Skills** - Creating, testing, and sharing skills

Plus:
- **Slash Commands** - `/superpowers:brainstorm`, `/superpowers:write-plan`, `/superpowers:decompose-plan`
- **Parallel Execution** - Run up to 2 subagents simultaneously for independent tasks
- **Automatic Integration** - Skills activate automatically when relevant
- **Consistent Workflows** - Systematic approaches to common engineering tasks

## Learn More

Read the introduction: [Superpowers for Claude Code](https://blog.fsck.com/2025/10/09/superpowers/)

## Installation

### Claude Code (via Plugin Marketplace)

In Claude Code, register the marketplace first:

```bash
/plugin marketplace add obra/superpowers-marketplace
```

Then install the plugin from this marketplace:

```bash
/plugin install superpowers@superpowers-marketplace
```

### Verify Installation

Check that commands appear:

```bash
/help
```

```
# Should see:
# /superpowers:brainstorm - Interactive design refinement
# /superpowers:write-plan - Create implementation plan
# /superpowers:decompose-plan - Decompose plan for parallel execution
```

### Codex (Experimental)

**Note:** Codex support is experimental and may require refinement based on user feedback.

Tell Codex to fetch https://raw.githubusercontent.com/seanGSISG/crispy-claude/refs/heads/main/.codex/INSTALL.md and follow the instructions.

## Quick Start

### Standard Workflow (Parallel Execution)

**1. Brainstorm a design:**
```
/superpowers:brainstorm
```

**2. Create an implementation plan:**
```
/superpowers:write-plan
```

**3. Decompose plan for parallel execution:**
```
/superpowers:decompose-plan
```

**4. Execute with parallel subagents:**

After decomposition, use the `parallel-subagent-driven-development` skill to run up to 2 subagents simultaneously on independent tasks.

### Alternative: Sequential Execution

Use `/superpowers:execute-plan` for manual batch execution without parallelization.

### Automatic Skill Activation

Skills activate automatically when relevant. For example:
- `test-driven-development` activates when implementing features
- `systematic-debugging` activates when debugging issues
- `verification-before-completion` activates before claiming work is done

## What's Inside

### Skills Library

**Testing** (`skills/testing/`)
- **test-driven-development** - RED-GREEN-REFACTOR cycle
- **condition-based-waiting** - Async test patterns
- **testing-anti-patterns** - Common pitfalls to avoid

**Debugging** (`skills/debugging/`)
- **systematic-debugging** - 4-phase root cause process
- **root-cause-tracing** - Find the real problem
- **verification-before-completion** - Ensure it's actually fixed
- **defense-in-depth** - Multiple validation layers

**Collaboration** (`skills/collaboration/`)
- **brainstorming** - Socratic design refinement
- **writing-plans** - Detailed implementation plans
- **decomposing-plans** - Split plans into parallel task files (NEW!)
- **parallel-subagent-driven-development** - Execute with up to 2 parallel subagents (NEW!)
- **executing-plans** - Batch execution with checkpoints
- **subagent-driven-development** - Fast iteration with quality gates (sequential)
- **dispatching-parallel-agents** - Concurrent subagent workflows
- **requesting-code-review** - Pre-review checklist
- **receiving-code-review** - Responding to feedback
- **using-git-worktrees** - Parallel development branches
- **finishing-a-development-branch** - Merge/PR decision workflow

**Meta** (`skills/meta/`)
- **writing-skills** - Create new skills following best practices
- **sharing-skills** - Contribute skills back via branch and PR
- **testing-skills-with-subagents** - Validate skill quality
- **using-superpowers** - Introduction to the skills system

### Commands

All commands are thin wrappers that activate the corresponding skill:

- **brainstorm.md** - Activates the `brainstorming` skill
- **write-plan.md** - Activates the `writing-plans` skill
- **decompose-plan.md** - Activates the `decomposing-plans` skill (NEW!)
- **execute-plan.md** - Activates the `executing-plans` skill

## How It Works

1. **SessionStart Hook** - Loads the `using-superpowers` skill at session start
2. **Skills System** - Uses Claude Code's first-party skills system
3. **Automatic Discovery** - Claude finds and uses relevant skills for your task
4. **Mandatory Workflows** - When a skill exists for your task, using it becomes required

## Philosophy

- **Test-Driven Development** - Write tests first, always
- **Systematic over ad-hoc** - Process over guessing
- **Complexity reduction** - Simplicity as primary goal
- **Evidence over claims** - Verify before declaring success
- **Domain over implementation** - Work at problem level, not solution level

## Contributing

Skills live directly in this repository. To contribute:

1. Fork the repository
2. Create a branch for your skill
3. Follow the `writing-skills` skill for creating new skills
4. Use the `testing-skills-with-subagents` skill to validate quality
5. Submit a PR

See `skills/meta/writing-skills/SKILL.md` for the complete guide.

## Updating

Skills update automatically when you update the plugin:

```bash
/plugin update superpowers
```

## License

MIT License - see LICENSE file for details

## New Features: Parallel Execution

### What's New

**Decompose plans into parallel tasks:**
- Split monolithic plans into individual task files
- Automatic dependency analysis
- Identify tasks that can run in parallel

**Execute with parallel subagents:**
- Run up to 2 subagents simultaneously
- 90% context savings (task files vs monolithic plan)
- 40% time savings for parallelizable tasks
- Same quality gates (code review after each batch)

### Workflow Comparison

**Before (Sequential):**
```
/brainstorm → /write-plan → /execute-plan
- Manual batch execution
- One task at a time
- 5 tasks × 10 min = 50 min
```

**After (Parallel):**
```
/brainstorm → /write-plan → /decompose-plan → parallel-subagent-driven-development
- Automatic parallelization
- Up to 2 tasks simultaneously
- 3 batches × 10 min = 30 min (40% faster!)
```

### Example Output Structure

```
docs/plans/
├── 2025-01-18-user-auth.md          # Monolithic plan
└── tasks/
    └── 2025-01-18-user-auth/         # Plan-specific subfolder
        ├── user-auth-task-01.md      # Individual task files
        ├── user-auth-task-02.md
        ├── user-auth-task-03.md
        └── user-auth-manifest.json   # Parallel batches + dependencies
```

## Support

- **Repository**: https://github.com/seanGSISG/crispy-claude
- **Issues**: https://github.com/seanGSISG/crispy-claude/issues
