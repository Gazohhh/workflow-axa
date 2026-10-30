#!/usr/bin/env python3
"""Preview, merge or check global artifact instructions. Never scans/deletes project output."""
from __future__ import annotations

import argparse
import hashlib
import os
import re
import stat
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

VERSION = "2.5.0"
SOURCE = Path(__file__).resolve().parents[1] / "ARTIFACTS.md"
START = "<!-- workflow-axa:artifacts:start -->"
END = "<!-- workflow-axa:artifacts:end -->"
HEADER = re.compile(rb"<!-- workflow-axa:artifact-policy version=(\d+\.\d+\.\d+) sha256=([a-f0-9]{64}) -->\n")


@dataclass(frozen=True)
class Change:
    path: Path
    before: bytes | None
    after: bytes
    role: str


def implicit_home() -> Path:
    """The user's home, resolved only when no explicit path was given."""
    try:
        return Path.home()
    except RuntimeError as exc:  # e.g. Windows with USERPROFILE/HOMEDRIVE unset
        raise ValueError("Cannot determine the home directory; pass --home (and --claude-dir/--codex-home) explicitly.") from exc


def safe_path(path: Path) -> Path:
    """Reject indirection rather than accidentally updating a linked project/config file."""
    path = path.expanduser()
    if not path.is_absolute():
        raise ValueError(f"Use an absolute configuration path: {path}")
    path = Path(os.path.abspath(path))
    if any(c in str(path) for c in "\r\n`"):
        raise ValueError("Configuration paths cannot contain newlines or backticks.")
    for item in (path, *path.parents):
        try:
            info = item.lstat()
        except FileNotFoundError:
            continue
        if stat.S_ISLNK(info.st_mode) or getattr(info, "st_file_attributes", 0) & 0x400:
            raise ValueError(f"Symlink/junction path requires a manual reviewed merge: {item}")
        if item != path and not stat.S_ISDIR(info.st_mode):
            raise ValueError(f"Configuration parent is not a directory: {item}")
    if path.exists():
        info = path.stat()
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
            raise ValueError(f"Expected an ordinary single-link file: {path}")
    return path


def read_existing(path: Path) -> bytes | None:
    safe_path(path)
    return path.read_bytes() if path.exists() else None


def block_text(host: str, policy: Path, digest: str) -> str:
    path = policy.as_posix()
    reference = ("@" + path.replace(" ", "\\ ") if host == "claude"
                 else f"Before generating test/build/device output, read `{path}`. This is a file to read, not an automatic Markdown import.")
    return f"""{START}
## Workflow AXA — test output (all projects)

{reference}

Apply the shared artifact policy even without `/workflow`. Reuse the task's output parent;
keep only necessary results; preserve active/protected/tool-owned output. Clean only your own
explicitly disposable output under that policy and stricter project rules. Never bulk-delete
older artifacts or create a new report just to record cleanup. Pass the same boundaries to
subagents. If the policy is missing or conflicts with local protections, disclose it; preserve
uncertain files rather than inventing deletion authority. Do not install anything automatically.

Policy source: workflow-axa {VERSION}; SHA-256 {digest}. Setup/check evidence is not proof of host loading.
{END}"""


def merge_block(before: bytes | None, block: str) -> bytes:
    raw = before or b""
    text = raw.decode("utf-8")  # Includes any BOM unchanged outside our block.
    a, b = text.count(START), text.count(END)
    if (a, b) not in {(0, 0), (1, 1)}:
        raise ValueError("Duplicate/incomplete workflow-axa block; review manually before merging.")
    newline = "\r\n" if "\r\n" in text else "\n"
    replacement = block.replace("\n", newline)
    if a:
        begin, finish = text.index(START), text.index(END)
        if finish < begin:
            raise ValueError("Reversed workflow-axa block markers; review manually.")
        return (text[:begin] + replacement + text[finish + len(END):]).encode("utf-8")
    prefix = text
    if prefix and not prefix.endswith(("\n", "\r")):
        prefix += newline
    if prefix and not prefix.endswith(newline * 2):
        prefix += newline
    return (prefix + replacement + newline).encode("utf-8")


def policy_bytes(source: bytes) -> bytes:
    digest = hashlib.sha256(source).hexdigest()
    return f"<!-- workflow-axa:artifact-policy version={VERSION} sha256={digest} -->\n".encode() + source


def validate_managed_policy(existing: bytes | None) -> None:
    if existing is None:
        return
    match = HEADER.match(existing)
    if not match or hashlib.sha256(existing[match.end():]).hexdigest().encode() != match[2]:
        raise ValueError("Existing global policy is unowned or modified; reconcile manually, do not overwrite.")
    installed = tuple(map(int, match[1].decode().split(".")))
    if installed > tuple(map(int, VERSION.split("."))):
        raise ValueError("Refusing to downgrade a newer global artifact policy.")


def build_plan(home: Path, claude_dir: Path, codex_home: Path, host: str) -> list[Change]:
    if not home.expanduser().is_absolute():
        raise ValueError("Home must be absolute.")
    policy = safe_path(home / ".workflow-axa" / "ARTIFACTS.md")
    source = SOURCE.read_bytes()
    source.decode("utf-8")
    before = read_existing(policy)
    validate_managed_policy(before)
    changes = [Change(policy, before, policy_bytes(source), "shared deployed policy")]
    digest = hashlib.sha256(source).hexdigest()
    targets = []
    if host in {"both", "claude"}:
        targets.append(("claude", claude_dir / "CLAUDE.md"))
    if host in {"both", "codex"}:
        targets.append(("codex", codex_home / "AGENTS.md"))
        override = safe_path(codex_home / "AGENTS.override.md")
        raw = read_existing(override)
        if raw is not None and raw.decode("utf-8-sig").strip():
            targets.append(("codex", override))
    for name, path in targets:
        path = safe_path(path)
        old = read_existing(path)
        new = merge_block(old, block_text(name, policy, digest))
        changes.append(Change(path, old, new, name + " global instructions"))
    if len({os.path.normcase(str(c.path)) for c in changes}) != len(changes):
        raise ValueError("Configuration targets must not overlap.")
    return changes


def apply_plan(changes: list[Change]) -> None:
    # Validate all inputs before the first write, then recheck each just before replacement.
    for change in changes:
        if read_existing(change.path) != change.before:
            raise ValueError(f"File changed after preview; rerun: {change.path}")
    completed = []
    try:
        for change in changes:
            if change.before == change.after:
                continue
            safe_path(change.path)
            change.path.parent.mkdir(parents=True, exist_ok=True)
            mode = stat.S_IMODE(change.path.stat().st_mode) if change.path.exists() else 0o600
            name = None
            try:
                with tempfile.NamedTemporaryFile(dir=change.path.parent, prefix=".workflow-axa-", delete=False) as stream:
                    name = stream.name
                    stream.write(change.after)
                    stream.flush()
                    os.fsync(stream.fileno())
                os.chmod(name, mode)
                if read_existing(change.path) != change.before:
                    raise ValueError(f"File changed during setup; rerun: {change.path}")
                os.replace(name, change.path)
                name = None
                completed.append(str(change.path))
            finally:
                if name and os.path.exists(name):
                    os.unlink(name)  # Only this operation's private temporary config file.
    except (OSError, ValueError) as exc:
        raise ValueError(f"Setup incomplete. Updated: {completed or 'none'}. Rerun --check. {exc}") from exc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--apply", action="store_true", help="Merge the reviewed managed blocks; no project mutations.")
    mode.add_argument("--check", action="store_true", help="Read-only comparison against the packaged policy and blocks.")
    parser.add_argument("--home", type=Path, help="Policy home; defaults to this user. Use absolute paths.")
    parser.add_argument("--claude-dir", type=Path, help="Actual Claude configuration directory; otherwise CLAUDE_CONFIG_DIR or HOME/.claude.")
    parser.add_argument("--codex-home", type=Path, help="Actual Codex home; otherwise CODEX_HOME or HOME/.codex.")
    parser.add_argument("--host", choices=("both", "claude", "codex"), default="both")
    args = parser.parse_args(argv)
    try:
        home = (args.home or implicit_home()).expanduser()
        claude = args.claude_dir or Path(os.environ.get("CLAUDE_CONFIG_DIR") or home / ".claude")
        codex = args.codex_home or Path(os.environ.get("CODEX_HOME") or home / ".codex")
        changes = build_plan(home, claude.expanduser(), codex.expanduser(), args.host)
        for change in changes:
            status = "MATCH" if change.before == change.after else "MISSING" if change.before is None else "UPDATE"
            print(f"{status}: {change.path} ({change.role})")
        if args.check:
            print("Disk check only. Confirm actual host loading in a fresh session; no files written.")
            return int(any(c.before != c.after for c in changes))
        if args.apply:
            apply_plan(changes)
            print("Applied managed policy/blocks. No project output was inspected or deleted. Start a fresh session and verify loading.")
        else:
            print("\nPREVIEW ONLY — no directories or files written. Proposed managed blocks:\n")
            for change in changes[1:]:
                text = change.after.decode("utf-8")
                print(str(change.path) + "\n" + text[text.index(START):text.index(END) + len(END)] + "\n")
            print("Review the packaged ARTIFACTS.md as well. Rerun with --apply to merge, or --check to inspect. Existing unrelated bytes are preserved.")
        return 0
    except (OSError, ValueError, UnicodeError, RuntimeError) as exc:  # RuntimeError: "~" with no home directory
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
