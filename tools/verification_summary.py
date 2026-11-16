#!/usr/bin/env python3
"""Write VALIDATION.md's "Current verification" section from real command output.

By default it runs no checks: pass the saved output and exit code of a test run
(`unittest -v`) and of tools/validate.py, each with the tree identity it ran on
(`--identity` prints it). With --run it runs both itself. It always reads the source
commit, a hash of the uncommitted changes, and the OS, Python and Git versions.
Browser, visual and host-discovery results are PASS, FAIL or NOT_RUN as you state
them; a check without evidence is NOT_RUN.

Exit status (G1): non-zero when any reported check failed, or a log came from another
tree (stale) or names no tree. `--check VALIDATION.md` writes nothing: it exits
non-zero when that file's current section is stale for this tree or records a failure.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import platform
import re
import subprocess
import sys
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HEADING = "## Current verification"
HISTORY = "\n## History"
TEST_COMMAND = 'python -X utf8 -m unittest discover -s tests -p "test_*.py" -v'
VALIDATE_COMMAND = "python -X utf8 -I tools/validate.py"
EXTRA_CHECKS = ("Browser suites", "Visual regression", "Host discovery")
STATES = ("PASS", "FAIL", "NOT_RUN")
OWN_FILE = "VALIDATION.md"  # excluded from the tree identity: writing it must not change the identity it records


@dataclass(frozen=True)
class CommandResult:
    command: str
    exit_code: int
    output: str
    source: str | None = None  # the tree identity the command ran on; None for an imported log that names none


@dataclass(frozen=True)
class TestTotals:
    ran: int
    passed: int
    skipped: int
    failed: int
    skip_reasons: dict[str, int] = field(default_factory=dict)


def parse_unittest(output: str) -> TestTotals | None:
    """Totals from unittest's summary; None when the output holds no summary."""
    ran = re.search(r"^Ran (\d+) tests? in ", output, re.M)
    status = re.search(r"^(OK|FAILED)(?: \(([^)]*)\))?\s*$", output, re.M)
    if not ran or not status:
        return None
    # unittest's labels contain spaces ("expected failures=3", "unexpected successes=1"): split on the commas, so
    # "failures" inside "expected failures" is never read as failures.
    counts = {}
    for part in (status[2] or "").split(","):
        if "=" in part:
            key, value = part.rsplit("=", 1)
            if value.strip().isdigit():
                counts[key.strip()] = int(value)
    total = int(ran[1])
    failed = counts.get("failures", 0) + counts.get("errors", 0) + counts.get("unexpected successes", 0)
    skipped = counts.get("skipped", 0)
    passed = total - failed - skipped - counts.get("expected failures", 0)
    # unittest prints repr(reason): single quotes, or double quotes when the reason contains one.
    # The exception detail after ": [" (e.g. "[WinError 1314] ... 'C:\\Users\\...'") holds machine paths; drop it.
    reasons = Counter(m[2].split(": [", 1)[0] for m in re.finditer(r"\.\.\. skipped (['\"])(.*)\1\s*$", output, re.M))
    return TestTotals(total, passed, skipped, failed, dict(reasons))


def _run(args: list[str], cwd: Path) -> str:
    try:
        done = subprocess.run(args, cwd=cwd, capture_output=True, text=True, encoding="utf-8",
                              errors="replace", timeout=60)
    except (OSError, subprocess.SubprocessError):
        return ""
    return done.stdout.strip() if done.returncode == 0 else ""


def _run_bytes(args: list[str], cwd: Path) -> bytes | None:
    try:
        done = subprocess.run(args, cwd=cwd, capture_output=True, timeout=60)
    except (OSError, subprocess.SubprocessError):
        return None
    return done.stdout if done.returncode == 0 else None


def tree_identity(root: Path) -> str:
    """`<commit>+clean`, or `<commit>+<hash>` of the uncommitted changes (tracked diffs and untracked, not-ignored
    files, VALIDATION.md excluded). `unknown` outside a Git checkout."""
    commit = _run(["git", "rev-parse", "HEAD"], root)
    if not commit:
        return "unknown"
    diff = _run_bytes(["git", "diff", "HEAD", "--binary", "--", ".", f":(exclude){OWN_FILE}"], root)
    listed = _run_bytes(["git", "ls-files", "--others", "--exclude-standard", "-z"], root)
    if diff is None or listed is None:
        return "unknown"
    untracked = sorted(name for name in listed.decode("utf-8", "replace").split("\0") if name and name != OWN_FILE)
    if not diff and not untracked:
        return f"{commit}+clean"
    digest = hashlib.sha256(diff)
    for name in untracked:
        digest.update(name.encode("utf-8") + b"\0")
        try:
            digest.update((root / name).read_bytes())
        except OSError:
            return "unknown"  # an unreadable change can't be fingerprinted, so the tree can't be identified
    return f"{commit}+{digest.hexdigest()[:16]}"


def bound(source: str | None, identity: str | None) -> bool:
    """Evidence counts only when it names this tree and the tree is identified: `unknown` never matches."""
    return bool(source) and source == identity and identity != "unknown"


def gather_facts(root: Path) -> dict:
    plugin = json.loads((root / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
    rules = json.loads((root / "skills/rule-maker/rules/version.json").read_text(encoding="utf-8"))
    status = _run(["git", "status", "--porcelain"], root)
    return {
        "commit": _run(["git", "rev-parse", "HEAD"], root) or "unknown (not a Git checkout)",
        "dirty": bool(status),
        "date": dt.date.today().isoformat(),
        "os": platform.platform(),
        "python": platform.python_version(),
        "git": _run(["git", "--version"], root) or "not found",
        "package": plugin.get("version", "unknown"),
        "rules": rules.get("rules_version", "unknown"),
        "identity": tree_identity(root),
    }


def problems(facts: dict, tests: CommandResult | None, validate: CommandResult | None,
             extra: dict[str, str]) -> list[str]:
    """Why this summary must not count as a pass: a failed check, or evidence from another or an unstated tree."""
    found = []
    for label, result in (("unit tests", tests), ("validator", validate)):
        if result is None:
            continue
        if not bound(result.source, facts.get("identity")):
            found.append(f"{label}: stale or unbound log (ran on {result.source or 'an unstated tree'}, "
                         f"this tree is {facts.get('identity')})")
        if result.exit_code != 0:
            found.append(f"{label}: exit {result.exit_code}")
    if tests is not None:
        totals = parse_unittest(tests.output)
        if totals is None:
            found.append("unit tests: no unittest summary in the output")
        elif totals.ran == 0:
            found.append("unit tests: no tests ran")
        elif totals.failed:
            found.append(f"unit tests: {totals.failed} failed")
    found += [f"{name}: FAIL" for name, state in extra.items() if state == "FAIL"]
    return found


def _cell(text: str) -> str:
    return text.replace("|", "\\|").replace("\n", " ")


def _stale(result: CommandResult, facts: dict) -> str:
    return "" if bound(result.source, facts.get("identity")) else \
        f"STALE (ran on `{result.source or 'an unstated tree'}`); "


def render_block(facts: dict, tests: CommandResult | None, validate: CommandResult | None,
                 extra: dict[str, str]) -> str:
    tree = "uncommitted changes present" if facts["dirty"] else "clean"
    lines = [HEADING, "",
             "Generated by `tools/verification_summary.py` from the command output below. "
             "This is the only current evidence; everything under History is older.", "",
             "| Fact | Value |", "|---|---|",
             f"| Package | workflow-axa {facts['package']}, rules {facts['rules']} |",
             f"| Source commit | `{facts['commit']}` |",
             f"| Working tree | {tree} |",
             f"| Tree identity | `{facts.get('identity', 'unknown')}` |",
             f"| Date | {facts['date']} |",
             f"| OS | {_cell(facts['os'])} |",
             f"| Python | {facts['python']} |",
             f"| Git | {_cell(facts['git'])} |", "",
             "| Check | Command | Result |", "|---|---|---|"]
    if tests is None:
        lines.append(f"| Unit tests | `{TEST_COMMAND}` | NOT_RUN |")
    else:
        totals = parse_unittest(tests.output)
        if totals is None:
            summary = f"exit {tests.exit_code}; no unittest summary in the output"
        else:
            summary = (f"exit {tests.exit_code}; {totals.ran} ran, {totals.passed} passed, "
                       f"{totals.skipped} skipped, {totals.failed} failed")
        lines.append(f"| Unit tests | `{_cell(tests.command)}` | {_stale(tests, facts)}{summary} |")
        if totals and totals.skip_reasons:
            reasons = "; ".join(f"{reason} ({count})" for reason, count in sorted(totals.skip_reasons.items()))
            lines.append(f"| Skip reasons | | {_cell(reasons)} |")
    if validate is None:
        lines.append(f"| Validator | `{VALIDATE_COMMAND}` | NOT_RUN |")
    else:
        first = next((line for line in validate.output.splitlines() if line.strip()), "no output")
        lines.append(f"| Validator | `{_cell(validate.command)}` | {_stale(validate, facts)}"
                     f"exit {validate.exit_code}; {_cell(first)} |")
    for name in EXTRA_CHECKS:
        lines.append(f"| {name} | | {extra.get(name, 'NOT_RUN')} |")
    lines.append("")
    return "\n".join(lines)


def write_section(path: Path, block: str) -> None:
    """Replace the current section, or insert it after the title; history below stays untouched."""
    text = path.read_text(encoding="utf-8")
    history = text.find(HISTORY)
    if history < 0:
        raise ValueError(f"{path.name} needs a '## History' heading below the current section")
    start = text.find(HEADING)
    if start < 0 or start > history:
        title_end = text.find("\n\n") + 2 if text.startswith("# ") else 0
        start = title_end
    path.write_text(text[:start] + block + text[history:], encoding="utf-8", newline="")


def check_section(path: Path, root: Path) -> list[str]:
    """Why this VALIDATION.md's current section is not valid evidence for this tree; empty when it is."""
    text = path.read_text(encoding="utf-8")
    start, end = text.find(HEADING), text.find(HISTORY)
    current = text[start:end] if 0 <= start < end else ""
    if not current:
        return [f"{path.name} has no current section above its History"]
    found = []
    recorded = re.search(r"^\| Tree identity \| `([^`]*)` \|", current, re.M)
    identity = tree_identity(root)
    if not recorded or recorded[1] != identity or identity == "unknown":
        found.append(f"stale: it records {recorded[1] if recorded else 'no tree identity'}, this tree is {identity}")
    for label, passing in (("Unit tests", r"exit 0; [1-9]\d* ran, \d+ passed, \d+ skipped, 0 failed"),
                           ("Validator", r"exit 0; ")):
        row = re.search(rf"^\| {label} \|.*\| ([^|]*) \|$", current, re.M)
        result = row[1].strip() if row else "missing"
        if not re.match(passing, result):
            found.append(f"{label}: {result}")
    found += [f"{name}: FAIL" for name in EXTRA_CHECKS if re.search(rf"^\| {name} \| \| FAIL \|", current, re.M)]
    return found


def _read_result(command: str, log: Path | None, code: int | None, source: str | None) -> CommandResult | None:
    if log is None:
        return None
    if code is None:
        raise SystemExit(f"Give the exit code with the log for: {command}")
    return CommandResult(command, code, log.read_text(encoding="utf-8", errors="replace"), source)


def _execute(command: list[str], label: str, root: Path, source: str) -> CommandResult:
    done = subprocess.run(command, cwd=root, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return CommandResult(label, done.returncode, done.stdout + done.stderr, source)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--run", action="store_true", help="run the unit tests and validator now")
    parser.add_argument("--tests-log", type=Path)
    parser.add_argument("--tests-exit", type=int)
    parser.add_argument("--tests-command", default=TEST_COMMAND)
    parser.add_argument("--tests-source", help="the tree identity the tests log ran on (see --identity)")
    parser.add_argument("--validate-log", type=Path)
    parser.add_argument("--validate-exit", type=int)
    parser.add_argument("--validate-command", default=VALIDATE_COMMAND)
    parser.add_argument("--validate-source", help="the tree identity the validator log ran on (see --identity)")
    for name in EXTRA_CHECKS:
        parser.add_argument("--" + name.split()[0].lower(), choices=STATES, default="NOT_RUN", dest=name)
    parser.add_argument("--write", type=Path, help="update this VALIDATION.md instead of printing")
    parser.add_argument("--check", type=Path, help="exit non-zero when this VALIDATION.md is stale or records a failure")
    parser.add_argument("--identity", action="store_true", help="print this tree's identity and exit")
    args = parser.parse_args()
    root = args.root.resolve()
    if args.identity:
        print(tree_identity(root))
        return 0
    if args.check:
        if args.run or args.write:
            parser.error("--check writes nothing; use it without --run or --write")
        found = check_section(args.check, root)
        for problem in found:
            print(f"FAIL: {problem}", file=sys.stderr)
        if not found:
            print(f"CURRENT: {args.check} matches this tree and records no failure")
        return 1 if found else 0
    extra = {name: getattr(args, name) for name in EXTRA_CHECKS}
    facts = gather_facts(root)  # before any write, so the working-tree fact describes the tree that was checked
    if args.run and args.write:
        # The checks read VALIDATION.md themselves: refresh its current section first, so they never fail on the old
        # version line or on a failure message an earlier run copied into it (2026-11-12-gate-followups T2).
        try:
            write_section(args.write, render_block(facts, None, None, extra))
        except (ValueError, OSError) as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 1
    if args.run:
        tests = _execute([sys.executable, "-X", "utf8", "-m", "unittest", "discover", "-s", "tests",
                          "-p", "test_*.py", "-v"], TEST_COMMAND, root, facts["identity"])
        validate = _execute([sys.executable, "-X", "utf8", "-I", "tools/validate.py"], VALIDATE_COMMAND, root,
                            facts["identity"])
        after = tree_identity(root)
        if after != facts["identity"]:  # the tree changed while the checks ran: the results describe neither tree
            moved = f"a tree that changed during the run (now {after})"
            tests = CommandResult(tests.command, tests.exit_code, tests.output, moved)
            validate = CommandResult(validate.command, validate.exit_code, validate.output, moved)
    else:
        tests = _read_result(args.tests_command, args.tests_log, args.tests_exit, args.tests_source)
        validate = _read_result(args.validate_command, args.validate_log, args.validate_exit, args.validate_source)
    block = render_block(facts, tests, validate, extra)
    found = problems(facts, tests, validate, extra)
    if args.write:
        try:
            write_section(args.write, block)
        except (ValueError, OSError) as exc:
            print(f"ERROR: {exc}", file=sys.stderr)
            return 1
        print(f"Updated {args.write}")
    else:
        print(block)
    for problem in found:
        print(f"FAIL: {problem}", file=sys.stderr)
    return 1 if found else 0


if __name__ == "__main__":
    raise SystemExit(main())
