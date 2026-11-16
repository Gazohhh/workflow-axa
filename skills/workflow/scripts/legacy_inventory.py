"""The frozen list of tasks approved before the offer model (contract C-LEG-1, ticket T16 of
docs/plans/2026-11-15-workflow-redesign).

At the cutover the owner runs `legacy_inventory.py --apply <workspace>`, in the same step as the hooks switch. It
records every task folder of that workspace whose checkpoint has an `Approval:` line and no offers/ folder: the
task name and the SHA-256 of that line. The offer checker (hooks/approval.py) then sends a session on such a task to
the legacy checker, and nothing else: no inventory means offers only, and an Approval line added or changed later is
not in the list. The checker never writes the inventory, and agents can't (the folder is protected).

  legacy_inventory.py <workspace>...            preview (writes nothing)
  legacy_inventory.py --apply <workspace>...    write the inventory; refuses to replace one
  legacy_inventory.py --apply --replace <ws>    replace it (the owner's explicit statement that the listed Approval
                                                lines are pre-offer approvals)

The folder is ~/.workflow-axa/legacy/, or $WORKFLOW_AXA_HOME/legacy/ (tests and staging).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from pathlib import Path

APPROVAL = re.compile(r"^[ \t]*[-*][ \t]*Approval\b[^\n]*$", re.M | re.I)
CHECKPOINT = re.compile(r"^(#{1,6})[ \t]+Current checkpoint\b[^\n]*$", re.M | re.I)


def home() -> Path:
    return Path(os.environ.get("WORKFLOW_AXA_HOME") or Path.home() / ".workflow-axa")


def folder() -> Path:
    return home() / "legacy"


def inventory_path(root: Path) -> Path:
    return folder() / f"{hashlib.sha256(str(Path(root).resolve()).lower().encode('utf-8')).hexdigest()[:24]}.json"


def approval_line(task: Path) -> str | None:
    """The checkpoint's Approval line, stripped; None without one."""
    try:
        plan = (task / "PLAN.md").read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None
    found = CHECKPOINT.search(plan)
    if found:
        end = re.compile(r"^#{1,%d}[ \t]" % len(found.group(1)), re.M).search(plan, found.end())
        plan = plan[found.end():end.start() if end else len(plan)]
    line = APPROVAL.search(plan)
    return line.group(0).strip() if line else None


def digest(line: str) -> str:
    return hashlib.sha256(line.encode("utf-8")).hexdigest()


def build(root: Path) -> dict:
    tasks = {}
    plans = Path(root) / "docs" / "plans"
    for task in sorted(plans.iterdir()) if plans.is_dir() else []:
        line = approval_line(task) if task.is_dir() and not (task / "offers").exists() else None
        if line:
            tasks[task.name] = digest(line)
    return {"schema": 1, "workspace": str(Path(root).resolve()), "tasks": tasks}


def load(root: Path) -> dict | None:
    """The workspace's inventory, or None when there is none or it can't be read (offers only then)."""
    try:
        data = json.loads(inventory_path(root).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not isinstance(data, dict) or not isinstance(data.get("tasks"), dict) \
            or str(data.get("workspace", "")).lower() != str(Path(root).resolve()).lower():
        return None
    return data


def is_legacy(root: Path, task: str) -> bool:
    """A task approved before the offer model: listed, its Approval line unchanged, and still without offers."""
    data = load(root)
    folder_ = Path(root) / "docs" / "plans" / task
    if not data or task not in data["tasks"] or (folder_ / "offers").exists():
        return False
    line = approval_line(folder_)
    return bool(line) and digest(line) == data["tasks"][task]


def write(root: Path, replace: bool) -> Path:
    path = inventory_path(root)
    if path.exists() and not replace:
        raise FileExistsError(f"{path} already exists; pass --replace to replace it")
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(build(root), indent=2) + "\n", encoding="utf-8", newline="\n")
    os.replace(temporary, path)
    return path


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("workspaces", nargs="+")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--replace", action="store_true")
    args = parser.parse_args(argv)
    status = 0
    for workspace in args.workspaces:
        root = Path(workspace)
        tasks = build(root)["tasks"]
        print(f"{root}: {len(tasks)} legacy task(s): {', '.join(tasks) or 'none'}")
        if args.apply:
            try:
                print(f"  written: {write(root, args.replace)}")
            except FileExistsError as exc:
                print(f"  refused: {exc}")
                status = 1
    return status


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
