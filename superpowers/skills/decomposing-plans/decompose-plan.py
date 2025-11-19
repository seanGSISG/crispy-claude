#!/usr/bin/env python3
"""
Decompose monolithic implementation plans into individual task files
with dependency analysis and parallelization identification.

Usage:
    python decompose-plan.py <plan-file> [--output-dir DIR] [--verbose]
"""

import argparse
import json
import re
import sys
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
        # Match common file path patterns
        patterns = [
            r'`([a-zA-Z0-9_\-./]+\.[a-zA-Z0-9]+)`',  # `src/foo.ts`
            r'(?:src/|\./)[\w\-/]+\.[\w]+',           # src/foo.ts or ./config.json
            r'[\w\-/]+/[\w\-/]+\.[\w]+'               # path/to/file.ts
        ]

        for pattern in patterns:
            matches = re.findall(pattern, self.content)
            for match in matches:
                # Clean up the match
                if isinstance(match, tuple):
                    match = match[0]
                # Filter out obvious non-paths
                if not any(skip in match.lower() for skip in ['http', 'npm', 'yarn', 'test', 'spec']):
                    self.files_to_modify.add(match)

    def extract_task_dependencies(self, all_tasks: List['Task']) -> None:
        """Extract explicit task dependencies from content."""
        content_lower = self.content.lower()

        # Check for "independent" or "parallel" markers
        if 'independent' in content_lower or 'in parallel' in content_lower:
            # Task explicitly says it's independent
            return

        # Look for explicit task mentions
        for other in all_tasks:
            if other.id >= self.id:
                continue  # Only look at previous tasks

            # Patterns for task mentions
            patterns = [
                rf'task {other.id}\b',
                rf'step {other.id}\b',
                rf'after task {other.id}',
                rf'depends on task {other.id}',
                rf'requires task {other.id}'
            ]

            for pattern in patterns:
                if re.search(pattern, content_lower):
                    self.dependencies.add(other.id)
                    other.blocks.add(self.id)
                    break

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
        files_str = "\n".join(f"- {f}" for f in sorted(self.files_to_modify)) or "- (none identified)"

        return f"""# Task {self.id}: {self.title}

## Dependencies
- Previous tasks: {deps_str}
- Must complete before: {blocks_str}

## Parallelizable
- Can run in parallel with: {parallel_str}

## Implementation

{self.content.strip()}

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

    def __init__(self, plan_path: Path, verbose: bool = False):
        self.plan_path = plan_path
        self.plan_content = plan_path.read_text()
        self.tasks: List[Task] = []
        self.verbose = verbose

    def log(self, message: str) -> None:
        """Log message if verbose mode enabled."""
        if self.verbose:
            print(f"[DEBUG] {message}")

    def parse_tasks(self) -> None:
        """Parse tasks from the monolithic plan."""
        self.log(f"Parsing tasks from {len(self.plan_content)} characters")

        # Try multiple patterns for task sections
        patterns = [
            # Pattern 1: "## Task N: Title" or "### Task N: Title"
            (r'\n##+ Task (\d+):\s*(.+?)\n', "## Task N: Title"),
            # Pattern 2: "## N. Title" or "### N. Title"
            (r'\n##+ (\d+)\.\s*(.+?)\n', "## N. Title"),
            # Pattern 3: "**Task N:** Title"
            (r'\n\*\*Task (\d+):\*\*\s*(.+?)\n', "**Task N:** Title"),
        ]

        tasks_found = False
        for pattern, pattern_name in patterns:
            self.log(f"Trying pattern: {pattern_name}")
            sections = re.split(pattern, self.plan_content)

            if len(sections) >= 4:  # Found at least one task
                self.log(f"Pattern matched! Found {(len(sections) - 1) // 3} sections")
                tasks_found = True

                # sections will be: [preamble, task1_num, task1_title, task1_content, task2_num, ...]
                i = 1  # Skip preamble
                while i < len(sections) - 2:
                    try:
                        task_num = int(sections[i])
                        task_title = sections[i+1].strip()
                        task_content = sections[i+2].strip() if i+2 < len(sections) else ""

                        task = Task(task_num, task_title, task_content)
                        task.extract_file_dependencies()
                        self.tasks.append(task)
                        self.log(f"  Task {task_num}: {task_title[:50]}...")

                        i += 3
                    except (ValueError, IndexError) as e:
                        self.log(f"Error parsing task at index {i}: {e}")
                        i += 3

                break

        if not tasks_found:
            print("❌ Error: Could not find tasks in plan file")
            print("\nExpected task format (one of):")
            print("  ## Task 1: Title")
            print("  ## 1. Title")
            print("  **Task 1:** Title")
            print("\nPlease ensure your plan uses one of these formats.")
            sys.exit(1)

    def analyze_dependencies(self) -> None:
        """Analyze dependencies between tasks."""
        self.log("Analyzing dependencies...")

        for i, task in enumerate(self.tasks):
            self.log(f"  Task {task.id}:")

            # First check for explicit task dependencies
            task.extract_task_dependencies(self.tasks)

            # If no explicit dependencies and not marked independent,
            # default to depending on previous task
            if i > 0 and not task.dependencies:
                content_lower = task.content.lower()
                if 'independent' not in content_lower and 'parallel' not in content_lower:
                    # Default: depends on immediately previous task
                    prev_task = self.tasks[i-1]
                    task.dependencies.add(prev_task.id)
                    prev_task.blocks.add(task.id)
                    self.log(f"    Added default dependency on task {prev_task.id}")

            # Check for file-based dependencies
            for j, other in enumerate(self.tasks[:i]):
                if task.files_to_modify.intersection(other.files_to_modify):
                    # Same files = forced sequential dependency
                    if other.id not in task.dependencies:
                        task.dependencies.add(other.id)
                        other.blocks.add(task.id)
                        shared = task.files_to_modify.intersection(other.files_to_modify)
                        self.log(f"    Added file-based dependency on task {other.id} (shared: {shared})")

            if not task.dependencies:
                self.log(f"    No dependencies")
            else:
                self.log(f"    Dependencies: {task.dependencies}")

    def identify_parallel_batches(self) -> List[List[int]]:
        """Identify batches of tasks that can run in parallel (max 2)."""
        self.log("Identifying parallel batches...")

        batches: List[List[int]] = []
        remaining = set(t.id for t in self.tasks)

        while remaining:
            # Find tasks with no unsatisfied dependencies
            ready = []
            for tid in remaining:
                task = next(t for t in self.tasks if t.id == tid)
                unsatisfied_deps = [dep for dep in task.dependencies if dep in remaining]
                if not unsatisfied_deps:
                    ready.append(tid)

            if not ready:
                print("❌ Error: Circular dependency detected!")
                print(f"Remaining tasks: {remaining}")
                for tid in remaining:
                    task = next(t for t in self.tasks if t.id == tid)
                    print(f"  Task {tid} depends on: {task.dependencies & remaining}")
                sys.exit(1)

            self.log(f"  Ready tasks: {ready}")

            # Create batches of up to 2 parallel tasks
            batch = []
            for task_id in ready:
                if len(batch) == 0:
                    batch.append(task_id)
                elif len(batch) == 1:
                    # Check if can run parallel with first task in batch
                    task = next(t for t in self.tasks if t.id == task_id)
                    other_task = next(t for t in self.tasks if t.id == batch[0])

                    # Can run parallel if no dependency and no file conflicts
                    if (task_id not in other_task.dependencies and
                        batch[0] not in task.dependencies and
                        task_id not in other_task.blocks and
                        batch[0] not in task.blocks and
                        not task.files_to_modify.intersection(other_task.files_to_modify)):
                        batch.append(task_id)
                        self.log(f"  Paired task {task_id} with task {batch[0]}")
                    else:
                        # Can't pair, will go in next batch
                        self.log(f"  Task {task_id} can't pair with {batch[0]}")
                        break
                else:
                    # Batch already has 2, stop
                    break

            # Add batch and remove tasks from remaining
            batches.append(batch)
            for tid in batch:
                remaining.remove(tid)
            self.log(f"  Created batch: {batch}")

            # Add any remaining ready tasks to next batch
            # (tasks that couldn't be paired)
            for task_id in ready:
                if task_id in remaining:
                    batches.append([task_id])
                    remaining.remove(task_id)
                    self.log(f"  Created single-task batch: {[task_id]}")

        return batches

    def write_task_files(self, output_dir: Path) -> None:
        """Write individual task files."""
        output_dir.mkdir(parents=True, exist_ok=True)

        # Extract feature name from plan filename
        # Format: YYYY-MM-DD-feature-name.md
        parts = self.plan_path.stem.split('-', 3)
        if len(parts) >= 4:
            feature_name = parts[3]
        else:
            feature_name = self.plan_path.stem

        for task in self.tasks:
            task_file = output_dir / f"{feature_name}-task-{task.id:02d}.md"
            task_file.write_text(task.to_markdown(self.tasks))
            print(f"  ✓ {task_file.name}")

    def write_manifest(self, output_dir: Path) -> Path:
        """Write execution manifest JSON."""
        # Extract feature name
        parts = self.plan_path.stem.split('-', 3)
        if len(parts) >= 4:
            feature_name = parts[3]
        else:
            feature_name = self.plan_path.stem

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

        print("\n🔍 Analyzing dependencies...")
        self.analyze_dependencies()
        for task in self.tasks:
            if task.dependencies:
                deps_str = ", ".join(str(d) for d in sorted(task.dependencies))
                print(f"  Task {task.id}: Depends on {deps_str}")
                if task.files_to_modify:
                    files_str = ", ".join(list(task.files_to_modify)[:2])
                    if len(task.files_to_modify) > 2:
                        files_str += f", ... ({len(task.files_to_modify)} total)"
                    print(f"    Files: {files_str}")
            else:
                print(f"  Task {task.id}: No dependencies")

        print("\n⚡ Identifying parallelization opportunities...")
        parallel_batches = self.identify_parallel_batches()
        for i, batch in enumerate(parallel_batches, 1):
            if len(batch) == 2:
                print(f"  Batch {i}: Tasks {batch[0]}, {batch[1]} (parallel)")
            else:
                print(f"  Batch {i}: Task {batch[0]} (sequential)")

        print(f"\n📝 Writing {len(self.tasks)} task files to {output_dir}/")
        self.write_task_files(output_dir)

        print("\n📋 Writing execution manifest...")
        manifest_path = self.write_manifest(output_dir)
        print(f"  ✓ {manifest_path.name}")

        # Calculate stats
        parallel_pairs = sum(1 for batch in parallel_batches if len(batch) == 2)
        sequential_tasks = sum(1 for batch in parallel_batches if len(batch) == 1)
        estimated_speedup = (parallel_pairs / len(self.tasks) * 100) if self.tasks else 0

        return {
            "total_tasks": len(self.tasks),
            "parallel_batches": len(parallel_batches),
            "parallel_pairs": parallel_pairs,
            "sequential_tasks": sequential_tasks,
            "manifest": str(manifest_path),
            "estimated_speedup": estimated_speedup
        }


def main():
    parser = argparse.ArgumentParser(
        description="Decompose monolithic implementation plan into parallel tasks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python decompose-plan.py docs/plans/2025-01-18-user-auth.md
  python decompose-plan.py plan.md --output-dir ./tasks
  python decompose-plan.py plan.md --verbose
"""
    )
    parser.add_argument(
        "plan_file",
        type=Path,
        help="Path to monolithic plan markdown file"
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        help="Output directory for task files (default: docs/plans/tasks/)"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose debug output"
    )

    args = parser.parse_args()

    if not args.plan_file.exists():
        print(f"❌ Error: Plan file not found: {args.plan_file}")
        return 1

    # Default output dir: docs/plans/tasks/<plan-name>/
    if args.output_dir:
        output_dir = args.output_dir
    else:
        # Create subfolder with plan filename (including date)
        # e.g., docs/plans/tasks/2025-01-18-test-user-auth/
        plan_name = args.plan_file.stem  # Gets "2025-01-18-test-user-auth" from "2025-01-18-test-user-auth.md"
        output_dir = args.plan_file.parent / "tasks" / plan_name

    try:
        decomposer = PlanDecomposer(args.plan_file, verbose=args.verbose)
        stats = decomposer.decompose(output_dir)

        print("\n" + "="*60)
        print("✅ Plan decomposition complete!")
        print("="*60)
        print(f"Total tasks: {stats['total_tasks']}")
        print(f"Parallel batches: {stats['parallel_batches']}")
        print(f"  - Pairs (2 parallel): {stats['parallel_pairs']}")
        print(f"  - Sequential: {stats['sequential_tasks']}")
        print(f"Estimated speedup: {stats['estimated_speedup']:.1f}%")
        print(f"\nManifest: {stats['manifest']}")
        print(f"\nNext: Use parallel-subagent-driven-development skill")

        return 0
    except Exception as e:
        print(f"\n❌ Error during decomposition: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
