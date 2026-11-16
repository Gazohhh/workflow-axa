"""Was every change of this task reviewed in the exact form it now has? (ticket T18 of
docs/plans/2026-11-15-workflow-redesign; it replaces the Stop hook's "Done without review" check.)

  completion_check.py baseline <root> <task-folder>          at the start of execution: the commit and the paths
                                                              already changed (the owner's or earlier work)
  completion_check.py snapshot <root> <task-folder> <path>…  before a review: the reviewed bytes, as S<n>
  completion_check.py check    <root> <task-folder>          before Done: exit 0 when every changed path is covered

The record is <task-folder>/completion.json, written only by this script: the baseline is never overwritten and a
snapshot never changes. The review result is one FINDINGS.md line per review:

  - Review S<n>: <reviewer> (independent|self) <passed|failed|pending>: <scope>

For each snapshot the latest such line counts; only `passed` covers it, and a self-review is named as such.
`check` exits 1 listing what isn't covered, and 2 when it can't decide (no baseline, no git).
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import time
from contextlib import contextmanager
from pathlib import Path

RECORD = "completion.json"
EXCLUDED = ("docs/plans/", ".artifacts/")
REVIEW = re.compile(r"^\s*[-*]\s*Review\s+(S\d+):\s*(.+?)\s+\((independent|self)\)\s+(passed|failed|pending)\b",
                    re.M | re.I)


class Unknown(Exception):
    """The check can't decide (exit 2)."""


def git(root: Path, *args: str) -> str:
    done = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, encoding="utf-8",
                          errors="replace")
    if done.returncode != 0:
        raise Unknown(f"git {' '.join(args)} failed: {done.stderr.strip()[:200]}")
    return done.stdout


def digest(root: Path, rel: str) -> str:
    try:
        return hashlib.sha256((root / rel).read_bytes()).hexdigest()[:16]
    except FileNotFoundError:
        return "deleted"


def counted(rel: str) -> bool:
    return not rel.startswith(EXCLUDED)


def dirty(root: Path) -> set[str]:
    """Paths changed in the working tree or index, untracked files included (renames: both paths)."""
    out, parts = set(), git(root, "status", "--porcelain", "-z", "--untracked-files=all").split("\0")
    i = 0
    while i < len(parts):
        entry = parts[i]
        if len(entry) > 3:
            out.add(entry[3:])
            if entry[0] in "RC":  # the original path follows as its own field
                i += 1
                out.add(parts[i])
        i += 1
    return {p for p in out if p}


def since(root: Path, base: str) -> set[str]:
    """Paths whose content differs from the base commit (committed or not), renames as both paths, plus untracked."""
    out, parts = set(), git(root, "diff", "-M", "--name-status", "-z", base).split("\0")
    i = 0
    while i < len(parts) - 1:
        status = parts[i]
        if status[:1] in "RC":
            out.update((parts[i + 1], parts[i + 2]))
            i += 3
        else:
            out.add(parts[i + 1])
            i += 2
    out.update(p for p in git(root, "ls-files", "--others", "--exclude-standard", "-z").split("\0") if p)
    return out


@contextmanager
def locked(task: Path, wait: float = 10.0):
    """One writer at a time per task: every read-validate-write of the record holds this lock."""
    lock = task / (RECORD + ".lock")
    deadline = time.monotonic() + wait
    while True:
        try:
            os.close(os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY))
            break
        except FileExistsError:
            if time.monotonic() > deadline:
                raise Unknown(f"{lock} is held by another call; retry, or remove it if no call is running")
            time.sleep(0.05)
        except OSError as exc:
            raise Unknown(f"can't lock {task} ({exc})")
    try:
        yield
    finally:
        try:
            os.remove(lock)
        except OSError:
            pass


def load(task: Path) -> dict:
    try:
        data = json.loads((task / RECORD).read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise Unknown(f"no baseline in {task / RECORD}; run `completion_check.py baseline` when execution starts")
    except (OSError, ValueError) as exc:
        raise Unknown(f"{task / RECORD} can't be read ({exc})")
    if not (isinstance(data, dict) and isinstance(data.get("base"), str) and isinstance(data.get("dirty"), dict)
            and isinstance(data.get("snapshots"), dict)
            and all(isinstance(v, dict) for v in data["snapshots"].values())):
        raise Unknown(f"{task / RECORD} is damaged (not the structure this script writes)")
    return data


def save(task: Path, data: dict) -> None:
    path = task / RECORD
    temporary = path.with_suffix(f".{os.getpid()}.tmp")
    temporary.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8", newline="\n")
    os.replace(temporary, path)


def baseline(root: Path, task: Path) -> dict:
    with locked(task):
        if (task / RECORD).exists():
            raise Unknown(f"{task / RECORD} already has the baseline; it is never replaced")
        base = git(root, "rev-parse", "HEAD").strip()
        data = {"schema": 1, "base": base, "dirty": {p: digest(root, p) for p in sorted(dirty(root)) if counted(p)},
                "snapshots": {}}
        save(task, data)
        return data


def snapshot(root: Path, task: Path, paths: list[str]) -> str:
    with locked(task):
        return _snapshot(root, task, paths)


def _snapshot(root: Path, task: Path, paths: list[str]) -> str:
    data = load(task)
    rels = []
    for path in paths:
        rel = Path(os.path.relpath(Path(path).resolve() if Path(path).is_absolute() else (root / path).resolve(),
                                   root.resolve())).as_posix()
        if rel.startswith("../"):
            raise Unknown(f"{path} is outside {root}")
        rels.append(rel)
    sid = f"S{len(data['snapshots']) + 1}"
    data["snapshots"][sid] = {p: digest(root, p) for p in rels}
    save(task, data)
    return sid


def task_changes(root: Path, data: dict) -> dict[str, str]:
    """This task's changes: the paths now different from the base, and the paths dirty at the baseline whose bytes
    are no longer what they were then (restored or deleted included). The rest of the owner's edits are left out."""
    now = since(root, data["base"]) | set(data["dirty"])
    changed = {}
    for rel in sorted(p for p in now if counted(p)):
        current = digest(root, rel)
        if rel in data["dirty"]:
            if current != data["dirty"][rel]:
                changed[rel] = current
        else:
            changed[rel] = current
    return changed


def reviews(task: Path) -> dict[str, tuple[str, str, str]]:
    """The latest review line per snapshot: (reviewer, independent|self, passed|failed|pending)."""
    try:
        text = (task / "FINDINGS.md").read_text(encoding="utf-8")
    except FileNotFoundError:
        return {}
    except OSError as exc:
        raise Unknown(f"FINDINGS.md can't be read ({exc})")
    latest = {}
    for sid, reviewer, kind, result in REVIEW.findall(text):
        latest[sid.upper()] = (reviewer.strip(), kind.lower(), result.lower())
    return latest


def check(root: Path, task: Path) -> tuple[list[str], list[str]]:
    """(problems, self-only notes) for the task's current changes."""
    data = load(task)
    results = reviews(task)
    problems, notes = [], []
    order = sorted(data["snapshots"], key=lambda sid: int(sid[1:]))
    for rel, current in task_changes(root, data).items():
        holding = [sid for sid in order if data["snapshots"][sid].get(rel) == current]
        if holding:
            latest = holding[-1]  # the newest snapshot of this exact version decides, its review pending until recorded
            reviewer, kind, result = results.get(latest, ("", "", "pending"))
            if result == "passed":
                if kind == "self":
                    notes.append(f"{rel}: self-reviewed only ({latest})")
                continue
            state = result if latest in results else "has no review line yet"
            problems.append(f"{rel}: its newest snapshot of this version, {latest}, {state}; it needs a passed review")
        elif any(rel in hashes for hashes in data["snapshots"].values()):
            problems.append(f"{rel}: changed after its last review snapshot; snapshot it and review it again")
        else:
            problems.append(f"{rel}: changed by this task and never reviewed")
    return problems, notes


def main(argv: list[str]) -> int:
    if len(argv) < 3 or argv[0] not in ("baseline", "snapshot", "check"):
        print(__doc__)
        return 2
    root, task = Path(argv[1]), Path(argv[2])
    task = task if task.is_absolute() else root / task
    try:
        if argv[0] == "baseline":
            data = baseline(root, task)
            print(f"baseline {data['base'][:12]}; {len(data['dirty'])} path(s) already changed are left out")
        elif argv[0] == "snapshot":
            if len(argv) < 4:
                raise Unknown("name the files handed to the reviewer")
            sid = snapshot(root, task, argv[3:])
            print(f"{sid}: give the reviewer this id; record `- Review {sid}: <reviewer> (independent|self) "
                  "<passed|failed|pending>: <scope>` in FINDINGS.md")
        else:
            problems, notes = check(root, task)
            for line in notes:
                print(f"note: {line}")
            for line in problems:
                print(f"not covered: {line}")
            if problems:
                return 1
            print("every change of this task was reviewed in its current form")
    except (Unknown, OSError, ValueError, KeyError, TypeError) as exc:
        print(f"completion_check: can't decide: {exc}")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
