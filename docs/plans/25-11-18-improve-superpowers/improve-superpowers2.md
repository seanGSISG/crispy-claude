 Proposed Solution: Plan Decomposition & Parallel Execution

  1. New Skill: decomposing-plans

  Purpose: Run immediately after /write-plan to break monolithic plan into individual task files and identify parallelizable tasks.

  Location: superpowers/skills/decomposing-plans/SKILL.md

  ---
  name: decomposing-plans
  description: Use after writing-plans to decompose monolithic plan into individual task files and identify tasks that can run in parallel (up to 2 subagents simultaneously)
  allowed-tools: [Read, Write, Bash]
  ---

  # Decomposing Plans for Parallel Execution

  ## When to Use
  Run immediately after `/write-plan` when you have a monolithic implementation plan and want to:
  - Split it into individual task files (saves context tokens for subagents)
  - Identify which tasks can run in parallel (up to 2 simultaneous subagents)
  - Prepare for parallel subagent-driven development

  ## Process

  ### Step 1: Read the Monolithic Plan
  Read the plan file from `docs/plans/YYYY-MM-DD-<feature-name>.md`

  ### Step 2: Analyze Task Dependencies
  For each task in the plan:
  - Identify what it depends on (files, other tasks)
  - Identify what depends on it
  - Mark as "parallelizable" if no dependencies on other tasks

  ### Step 3: Create Task Files
  For each task, create: `docs/plans/tasks/<feature-name>-task-NN.md`

  **Task file format:**
  ```markdown
  # Task NN: [Task Name]

  ## Dependencies
  - Previous tasks: [list or "none"]
  - Files required: [list]
  - Must complete before: [list or "none"]

  ## Parallelizable
  - Can run in parallel with: [task numbers or "none"]

  ## Implementation Steps
  [Specific steps for THIS task only]

  ## Files to Modify
  [Exact file paths]

  ## Verification
  - [ ] Tests pass
  - [ ] Lint clean
  - [ ] Code review complete

  Step 4: Create Execution Manifest

  Create docs/plans/tasks/<feature-name>-manifest.json:

  {
    "plan": "docs/plans/YYYY-MM-DD-feature-name.md",
    "tasks": [
      {
        "id": 1,
        "file": "docs/plans/tasks/feature-name-task-01.md",
        "dependencies": [],
        "parallelizable_with": [2],
        "status": "pending"
      },
      {
        "id": 2,
        "file": "docs/plans/tasks/feature-name-task-02.md",
        "dependencies": [],
        "parallelizable_with": [1],
        "status": "pending"
      },
      {
        "id": 3,
        "file": "docs/plans/tasks/feature-name-task-03.md",
        "dependencies": [1, 2],
        "parallelizable_with": [],
        "status": "pending"
      }
    ],
    "parallel_batches": [
      [1, 2],  // Tasks 1 and 2 can run together
      [3]      // Task 3 must wait for 1 and 2
    ]
  }

  Step 5: Use Helper Script

  Run: python superpowers/skills/decomposing-plans/decompose-plan.py <plan-file>

  This script:
  - Parses the monolithic plan
  - Identifies task boundaries
  - Analyzes dependencies
  - Creates individual task files
  - Generates manifest.json
  - Reports parallelization opportunities

  Step 6: Review and Adjust

  Review the generated tasks and manifest:
  - Verify dependency analysis is correct
  - Confirm parallel batches make sense
  - Adjust task boundaries if needed

  Output

  Tell the user:
  - Number of tasks created
  - Number of parallel batches identified
  - Estimated time savings with parallel execution
  - Next step: Run enhanced subagent-driven-development

  ---

  ### 2. Helper Script: `decompose-plan.py`

  **Location:** `superpowers/skills/decomposing-plans/decompose-plan.py`

  ```python
  #!/usr/bin/env python3
  """
  Decompose monolithic implementation plans into individual task files
  with dependency analysis and parallelization identification.
  """

  import argparse
  import json
  import re
  from pathlib import Path
  from typing import List, Dict, Set, Tuple
  from datetime import datetime


  class Task:
      """Represents a single task from the plan."""

      def __init__(self, id: int, title: str, content: str):
          self.id = id
          self.title = title
          self.content = content
          self.dependencies: Set[int] = set()
          self.files_to_modify: Set[str] = set()
          self.blocks: Set[int] = set()  # Tasks that depend on this one

      def extract_file_dependencies(self) -> None:
          """Extract file paths mentioned in the task."""
          # Match file paths like src/foo/bar.ts or ./config.json
          file_pattern = r'(?:src/|\./)[\w\-/]+\.[\w]+'
          self.files_to_modify = set(re.findall(file_pattern, self.content))

      def to_markdown(self, all_tasks: List['Task']) -> str:
          """Generate markdown for this task file."""
          # Find tasks this can run parallel with
          parallel_with = []
          for other in all_tasks:
              if other.id == self.id:
                  continue
              # Can run parallel if no dependency relationship
              if (self.id not in other.dependencies and
                  other.id not in self.dependencies and
                  self.id not in other.blocks and
                  other.id not in self.blocks):
                  # Also check for file conflicts
                  if not self.files_to_modify.intersection(other.files_to_modify):
                      parallel_with.append(other.id)

          deps_str = ", ".join(str(d) for d in sorted(self.dependencies)) or "none"
          blocks_str = ", ".join(str(b) for b in sorted(self.blocks)) or "none"
          parallel_str = ", ".join(f"Task {p}" for p in sorted(parallel_with)) or "none"
          files_str = "\n".join(f"- {f}" for f in sorted(self.files_to_modify)) or "- none"

          return f"""# Task {self.id}: {self.title}

  ## Dependencies
  - Previous tasks: {deps_str}
  - Must complete before: {blocks_str}

  ## Parallelizable
  - Can run in parallel with: {parallel_str}

  ## Implementation

  {self.content}

  ## Files to Modify
  {files_str}

  ## Verification Checklist
  - [ ] Implementation complete
  - [ ] Tests written (TDD - test first!)
  - [ ] All tests pass
  - [ ] Lint/type check clean
  - [ ] Code review requested
  - [ ] Code review passed
  """


  class PlanDecomposer:
      """Decomposes monolithic plans into individual tasks."""

      def __init__(self, plan_path: Path):
          self.plan_path = plan_path
          self.plan_content = plan_path.read_text()
          self.tasks: List[Task] = []

      def parse_tasks(self) -> None:
          """Parse tasks from the monolithic plan."""
          # Common patterns for task sections
          # Pattern 1: "## Task N: Title" or "### Task N: Title"
          # Pattern 2: "## N. Title" or "### N. Title"
          # Pattern 3: "**Task N:** Title"

          sections = re.split(r'\n##+ (?:Task )?(\d+)[.:] (.+?)\n', self.plan_content)

          # sections will be: [preamble, task1_num, task1_title, task1_content, task2_num, ...]
          if len(sections) < 4:
              # Try alternative pattern
              sections = re.split(r'\n(?:\*\*Task (\d+):\*\*|##+ (\d+)\.) (.+?)\n', self.plan_content)

          i = 1  # Skip preamble
          while i < len(sections) - 2:
              task_num = int(sections[i] or sections[i+1])
              task_title = sections[i+1] if sections[i] else sections[i+2]
              task_content = sections[i+2] if sections[i] else sections[i+3]

              task = Task(task_num, task_title.strip(), task_content.strip())
              task.extract_file_dependencies()
              self.tasks.append(task)

              i += 3

      def analyze_dependencies(self) -> None:
          """Analyze dependencies between tasks."""
          for i, task in enumerate(self.tasks):
              # Tasks depend on all previous tasks by default
              # unless explicitly marked as independent
              if i > 0:
                  # Check if task mentions it's independent
                  if "independent" in task.content.lower() or "parallel" in task.content.lower():
                      # Only depends on explicitly mentioned tasks
                      for j in range(i):
                          if f"task {j+1}" in task.content.lower():
                              task.dependencies.add(j + 1)
                              self.tasks[j].blocks.add(task.id)
                  else:
                      # Depends on immediately previous task
                      task.dependencies.add(i)
                      self.tasks[i-1].blocks.add(task.id)

              # Check for file-based dependencies
              for other in self.tasks[:i]:
                  if task.files_to_modify.intersection(other.files_to_modify):
                      # Same files = sequential dependency
                      task.dependencies.add(other.id)
                      other.blocks.add(task.id)

      def identify_parallel_batches(self) -> List[List[int]]:
          """Identify batches of tasks that can run in parallel (max 2)."""
          batches: List[List[int]] = []
          remaining = set(t.id for t in self.tasks)

          while remaining:
              # Find tasks with no unsatisfied dependencies
              ready = [
                  tid for tid in remaining
                  if all(dep not in remaining for t in self.tasks if t.id == tid for dep in t.dependencies)
              ]

              if not ready:
                  raise ValueError("Circular dependency detected!")

              # Create batches of up to 2 parallel tasks
              batch = []
              for task_id in ready[:2]:  # Max 2 at a time
                  if not batch:
                      batch.append(task_id)
                  else:
                      # Check if can run parallel with first task in batch
                      task = next(t for t in self.tasks if t.id == task_id)
                      other_task = next(t for t in self.tasks if t.id == batch[0])

                      # Can run parallel if no dependency and no file conflicts
                      if (task_id not in other_task.dependencies and
                          batch[0] not in task.dependencies and
                          not task.files_to_modify.intersection(other_task.files_to_modify)):
                          batch.append(task_id)
                      else:
                          # Add to next batch
                          batches.append([task_id])
                          remaining.remove(task_id)
                          break

              if batch:
                  batches.append(batch)
                  for tid in batch:
                      remaining.discard(tid)

          return batches

      def write_task_files(self, output_dir: Path) -> None:
          """Write individual task files."""
          output_dir.mkdir(parents=True, exist_ok=True)

          feature_name = self.plan_path.stem.split('-', 3)[-1]  # Extract from YYYY-MM-DD-feature-name.md

          for task in self.tasks:
              task_file = output_dir / f"{feature_name}-task-{task.id:02d}.md"
              task_file.write_text(task.to_markdown(self.tasks))

      def write_manifest(self, output_dir: Path) -> Path:
          """Write execution manifest JSON."""
          feature_name = self.plan_path.stem.split('-', 3)[-1]
          manifest_file = output_dir / f"{feature_name}-manifest.json"

          parallel_batches = self.identify_parallel_batches()

          manifest = {
              "plan": str(self.plan_path),
              "feature": feature_name,
              "created": datetime.now().isoformat(),
              "total_tasks": len(self.tasks),
              "tasks": [
                  {
                      "id": task.id,
                      "title": task.title,
                      "file": str(output_dir / f"{feature_name}-task-{task.id:02d}.md"),
                      "dependencies": sorted(list(task.dependencies)),
                      "blocks": sorted(list(task.blocks)),
                      "files": sorted(list(task.files_to_modify)),
                      "status": "pending"
                  }
                  for task in self.tasks
              ],
              "parallel_batches": parallel_batches
          }

          manifest_file.write_text(json.dumps(manifest, indent=2))
          return manifest_file

      def decompose(self, output_dir: Path) -> Dict:
          """Main decomposition process."""
          print(f"📖 Reading plan: {self.plan_path}")
          self.parse_tasks()
          print(f"✓ Found {len(self.tasks)} tasks")

          print("🔍 Analyzing dependencies...")
          self.analyze_dependencies()

          print("⚡ Identifying parallelization opportunities...")
          parallel_batches = self.identify_parallel_batches()

          print(f"📝 Writing {len(self.tasks)} task files to {output_dir}/")
          self.write_task_files(output_dir)

          print("📋 Writing execution manifest...")
          manifest_path = self.write_manifest(output_dir)

          # Calculate stats
          parallel_pairs = sum(1 for batch in parallel_batches if len(batch) == 2)
          sequential_tasks = sum(1 for batch in parallel_batches if len(batch) == 1)

          return {
              "total_tasks": len(self.tasks),
              "parallel_batches": len(parallel_batches),
              "parallel_pairs": parallel_pairs,
              "sequential_tasks": sequential_tasks,
              "manifest": str(manifest_path),
              "estimated_speedup": f"{(parallel_pairs / len(self.tasks) * 100):.1f}%"
          }


  def main():
      parser = argparse.ArgumentParser(
          description="Decompose monolithic implementation plan into parallel tasks"
      )
      parser.add_argument("plan_file", type=Path, help="Path to monolithic plan markdown file")
      parser.add_argument(
          "--output-dir",
          type=Path,
          help="Output directory for task files (default: docs/plans/tasks/)"
      )

      args = parser.parse_args()

      if not args.plan_file.exists():
          print(f"❌ Error: Plan file not found: {args.plan_file}")
          return 1

      output_dir = args.output_dir or args.plan_file.parent / "tasks"

      decomposer = PlanDecomposer(args.plan_file)
      stats = decomposer.decompose(output_dir)

      print("\n" + "="*60)
      print("✅ Plan decomposition complete!")
      print("="*60)
      print(f"Total tasks: {stats['total_tasks']}")
      print(f"Parallel batches: {stats['parallel_batches']}")
      print(f"  - Pairs (2 parallel): {stats['parallel_pairs']}")
      print(f"  - Sequential: {stats['sequential_tasks']}")
      print(f"Estimated speedup: {stats['estimated_speedup']}")
      print(f"\nManifest: {stats['manifest']}")
      print(f"\nNext: Use parallel-subagent-driven-development skill")

      return 0


  if __name__ == "__main__":
      exit(main())

  ---
  3. Enhanced Skill: parallel-subagent-driven-development

  Location: superpowers/skills/parallel-subagent-driven-development/SKILL.md

  ---
  name: parallel-subagent-driven-development
  description: Use after decomposing-plans to execute tasks with up to 2 subagents simultaneously, with code review between batches
  allowed-tools: [Read, Write, Task, TodoWrite]
  ---

  # Parallel Subagent-Driven Development

  ## When to Use
  After running `decomposing-plans` skill, use this to execute tasks with up to 2 parallel subagents.

  ## Prerequisites
  - Monolithic plan decomposed via `decomposing-plans`
  - Manifest file exists: `docs/plans/tasks/<feature>-manifest.json`
  - Individual task files created

  ## Process

  ### Step 1: Load Manifest
  Read `docs/plans/tasks/<feature>-manifest.json` to get parallel batches.

  ### Step 2: Create TodoWrite Checklist
  For each batch in manifest:
  - Execute batch N (tasks X, Y)
  - Review batch N results

  ### Step 3: Execute Each Batch
  For each parallel batch:

  **If batch has 1 task:**
  Use Task tool with single typescript-implementer/python-implementer:
  - Read ONLY the specific task file (not monolithic plan)
  - Implement following TDD
  - Run tests and verification

  **If batch has 2 tasks:**
  Use Task tool TWICE in SINGLE message (parallel execution):
  - Subagent 1: Task X task file
  - Subagent 2: Task Y task file
  - Both follow TDD independently
  - Both run tests independently

  **Critical:** Send BOTH Task tool calls in ONE message to run truly parallel.

  ### Step 4: Review Batch Results
  After each batch completes:
  Use Task tool with code-reviewer agent:
  - Review BOTH implementations together
  - Check for integration issues
  - Verify both followed plan
  - Check for conflicts between parallel changes

  ### Step 5: Update Manifest
  Mark completed tasks as "done" in manifest.json:
  ```json
  {
    "id": 1,
    "status": "done",
    "completed_at": "2025-01-18T10:30:00Z"
  }

  Step 6: Repeat

  Move to next batch until all complete.

  Example: Parallel Execution

  I'm executing batch 1 with 2 parallel tasks:
  - Task 1: Implement user authentication
  - Task 2: Implement logging service

  These can run in parallel because:
  - No shared file dependencies
  - No task dependencies
  - Different components

  Launching 2 subagents simultaneously...

  Then make TWO Task tool calls in ONE message:
  - Task 1 for typescript-implementer with task-01.md
  - Task 2 for typescript-implementer with task-02.md

  Benefits

  - Context efficiency: Each subagent reads ~500 tokens (task file) vs ~5000 tokens (monolithic plan)
  - Time savings: Parallel tasks complete in time of slowest, not sum
  - Clear scope: Each subagent has focused, bounded work
  - Review quality: Batch review catches integration issues

  Integration

  REQUIRED SUB-SKILL:
  - superpowers:test-driven-development - Each subagent MUST follow TDD
  - superpowers:requesting-code-review - After each batch

  REQUIRED BACKGROUND:
  - superpowers:decomposing-plans - Must run first to create task files

  ---

  ### 4. New Slash Command: `/decompose-plan`

  **Location:** `superpowers/commands/decompose-plan.md`

  ```yaml
  ---
  description: Decompose monolithic plan into parallel task files
  argument-hint: "<plan-file>"
  allowed-tools: [Bash, Read, Write]
  ---

  Use the decomposing-plans skill exactly as written to break up the monolithic plan into individual task files and identify parallelization opportunities.

  The plan file should be: docs/plans/YYYY-MM-DD-<feature-name>.md

  ---
  Implementation Plan

● Perfect! This aligns exactly with what the Claude Code documentation recommends:

  From /docs:
  "Launch multiple agents concurrently whenever possible, to maximize performance; to do that, use a single message with multiple tool uses"

  Your workflow improvement addresses two key inefficiencies:
  1. Context waste: Each subagent reading 5k+ token monolithic plan when they need ~500 tokens
  2. Time waste: Sequential execution when tasks could run parallel

  Shall I implement this? I'll create:

  1. ✅ decomposing-plans skill
  2. ✅ decompose-plan.py Python script with dependency analyzer
  3. ✅ parallel-subagent-driven-development skill (enhanced version)
  4. ✅ /decompose-plan slash command

  The workflow will be:
  /brainstorm → /write-plan → /decompose-plan → parallel-subagent-driven-development