"""Isolated sandboxes for the live host tests of docs/plans/2026-11-15-workflow-redesign (T16, T26). Disposable:
removed after the T26 pilot. Its `package` command ended at the T17 cutover, which applied the candidate blocks
(candidates/OFFER-INSTRUCTIONS.md, still read by `blocks` for the test that they stay applied).

  stage_candidate.py sandbox <out> <package> [--hooks <home>]
                                               a test repository that loads only the staged package's instructions:
                                               project settings exclude the user's CLAUDE.md and its imported rules,
                                               disable the installed workflow-axa plugin, and import the staged rules

It refuses to replace a folder it didn't make (it holds .staged-by-workflow-axa). Nothing outside <out> changes.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import stat
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CANDIDATES = ROOT / "docs/plans/2026-11-15-workflow-redesign/candidates/OFFER-INSTRUCTIONS.md"
MARKER = ".staged-by-workflow-axa"
BLOCK = re.compile(r"^### (\S+)\n+```old\n(.*?)\n```\n+```new\n(.*?)\n```", re.M | re.S)
INSTALLED_PLUGIN = "workflow-axa@gazohhh"


def blocks(text: str) -> list[tuple[str, str, str]]:
    return [(m[1], m[2], m[3]) for m in BLOCK.finditer(text.replace("\r\n", "\n"))]


def fresh(out: Path) -> None:
    if out.exists():
        if not (out / MARKER).is_file():
            raise SystemExit(f"stage_candidate: {out} exists and wasn't made by this tool; choose another folder")
        def writable(func, path, _):  # git keeps its objects read-only on Windows
            os.chmod(path, stat.S_IWRITE)
            func(path)
        shutil.rmtree(out, onexc=writable)
    out.mkdir(parents=True)
    (out / MARKER).write_text("disposable; removed after the T26 pilot\n", encoding="utf-8")


def stage_sandbox(out: Path, package: Path, hooks_home: Path | None = None) -> None:
    fresh(out)
    home = Path.home()
    rules = package / "skills/rule-maker/rules"
    excluded = [home / ".claude/CLAUDE.md", home / ".workflow-axa/ARTIFACTS.md",
                home / ".agents/skills/rule-maker/rules/START.md", home / ".agents/skills/rule-maker/rules/CORE.md"]
    excluded += [parent / "CLAUDE.md" for parent in out.parents]  # the host also loads CLAUDE.md of parent folders
    (out / ".claude").mkdir()
    settings = {"claudeMdExcludes": [p.as_posix() for p in excluded], "enabledPlugins": {INSTALLED_PLUGIN: False}}
    if hooks_home:  # hosts without --plugin-dir (a T3 thread): the staged checker registered by absolute path
        settings["env"] = {"WORKFLOW_AXA_SETTINGS": (hooks_home / "settings.json").as_posix(),
                           "WORKFLOW_AXA_HOME": hooks_home.as_posix(),
                           "WORKFLOW_AXA_GATE_CACHE": (hooks_home / "cache").as_posix()}
        checker = (package / "hooks/approval.py").as_posix()
        settings["hooks"] = {"PreToolUse": [{"matcher": "Edit|Write|MultiEdit|NotebookEdit|Bash|PowerShell|mcp__.*",
                                             "hooks": [{"type": "command", "timeout": 20,
                                                        "command": f'python -X utf8 -I "{checker}"'}]}]}
    (out / ".claude/settings.json").write_text(json.dumps(settings, indent=2) + "\n", encoding="utf-8", newline="\n")
    shutil.copytree(rules, out / ".axa-rules")  # imports from outside the project need approval -p can't give
    (out / "CLAUDE.md").write_text("# Sandbox for the workflow-axa candidate host tests\n\n"
                                   "@.axa-rules/START.md\n@.axa-rules/CORE.md\n", encoding="utf-8", newline="\n")
    task = out / "docs/plans/2026-11-15-vat"
    task.mkdir(parents=True)
    (task / "PLAN.md").write_text("# VAT rate\n\n## Current checkpoint\n- Status: tickets written; awaiting the offer\n"
                                  "- Agreement: agreed 2026-11-15 (sandbox)\n\n## Goal\nThe VAT rate becomes 0.22.\n",
                                  encoding="utf-8", newline="\n")
    (task / "TODO.md").write_text("# Tickets\n\n| ID | Ticket | Files | Check |\n|---|---|---|---|\n"
                                  "| T1 | VAT rate 0.21 -> 0.22 | src/vat.ts | read the file back |\n",
                                  encoding="utf-8", newline="\n")
    (out / "AGENTS.md").write_text("# Sandbox\n\nTest repository; any change here is disposable.\n", encoding="utf-8",
                                   newline="\n")
    (out / "src").mkdir()
    (out / "src/vat.ts").write_text("export const vat = (amount: number) => amount * 0.21;\n", encoding="utf-8",
                                    newline="\n")
    (out / "src/page.html").write_text('<main class="page"><h1 class="title">VAT</h1></main>\n', encoding="utf-8",
                                       newline="\n")
    for args in (["init", "-q"], ["add", "-A"], ["-c", "user.name=sandbox", "-c", "user.email=sandbox@example.invalid",
                                                 "commit", "-q", "-m", "sandbox"]):
        subprocess.run(["git", "-C", str(out), *args], check=True, capture_output=True)
    print(f"sandbox: {out}")


def main(argv: list[str]) -> int:
    if len(argv) >= 3 and argv[0] == "sandbox":
        home = Path(argv[argv.index("--hooks") + 1]).resolve() if "--hooks" in argv else None
        stage_sandbox(Path(argv[1]).resolve(), Path(argv[2]).resolve(), home)
    else:
        print(__doc__)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
