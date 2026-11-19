#!/usr/bin/env python3
"""Measure what a workflow-axa tree costs an agent: words read, hook process time and owner stops."""

from __future__ import annotations

import argparse
import datetime as dt
import importlib.util
import json
import os
import re
import shlex
import statistics
import subprocess
import sys
import tempfile
import time
from pathlib import Path

DEFAULT_ROOT = Path(__file__).resolve().parents[1]

ROUTER = ("workflow/SKILL.md", "workflow/flows/INDEX.md")
RULES = ("rule-maker/rules/START.md", "rule-maker/rules/CORE.md", "rule-maker/rules/READINESS.md",
         "rule-maker/rules/OPERATIONS.md")
ENTRIES = {
    "router": ROUTER,
    "bug": ROUTER + RULES + ("workflow/flows/bug.md", "workflow-clarify/SKILL.md", "grilling/SKILL.md",
                             "workflow-specify/SKILL.md", "workflow-execute/SKILL.md", "tdd/SKILL.md",
                             "code-review/SKILL.md", "workflow-deliver/SKILL.md"),
    "lightweight": ROUTER + RULES + ("workflow-specify/SKILL.md", "workflow-execute/SKILL.md",
                                     "code-review/SKILL.md", "workflow-deliver/SKILL.md"),
}
AFTER_CODE = ("code-review/SKILL.md", "workflow-deliver/SKILL.md")
ENTRIES["bug_before_code"] = tuple(e for e in ENTRIES["bug"] if e not in AFTER_CODE)
EXCLUDED = {"bug_before_code": AFTER_CODE}

READ_VERB = re.compile(r"(?:^|[:;,|]\s*|\b(?:and|then|first|now)\s+)"
                       r"(?:(?:read|follow|apply)\b(?!-)|run the [\w\s,-]*?\bcheck\b)", re.I)
CONDITION = re.compile(r"\b(?:when|whenever|unless|only|optional|optionally|needed|requested|asked|missing"
                       r"|conflict\w*|contradict\w*)\b|(?<!even )\bif\b", re.I)
UI_CONDITION = re.compile(r"\bUI\b")
OPENER = re.compile(r"^(?:When|Whenever|If|Unless|Only|While|For|UI|Run this step when)\b")
SENTENCE = re.compile(r"(?<=[.!?])\s+(?=[A-Z*`\[(])")
LIST_MARK = re.compile(r"^\s*(?:[-*>]|\d+\.)\s+")
LINK = re.compile(r"\]\(([^)#\s]+)(?:#[^)]*)?\)")
CODE_PATH = re.compile(r"`([^`\s]+(?:\.md|/))`")
BARE_NAME = re.compile(r"(?<![\w/.-])([A-Z][A-Z0-9-]*\.md)\b")
ALWAYS_HEADING = re.compile(r"^##\s+Always\s*$")

STOPS = (
    ("rules readiness: Set up rules now or Skip for this task", "rule-maker/rules/READINESS.md",
     "*Set up rules now*", None),
    ("agreement: Does this describe what should be built?", "workflow-clarify/SKILL.md",
     "Does this describe what should be built?", r"one ticket.*without the question above"),
    ("offer: the one question (Show review.html first, Approve from this summary, Change something)",
     "workflow-specify/SKILL.md", "the one question", None),
    ("owner acceptance at delivery", "workflow-deliver/SKILL.md", "still need to accept", None),
)

HOOK_CALLS = {
    "bash_read_only": (("PreToolUse", "Bash"), ("PostToolUse", "Bash")),
    "read": (("PostToolUse", "Read"),),
    "edit": (("PreToolUse", "Edit"), ("PostToolUse", "Edit")),
}
TASK = "2026-11-19-measure"

HELP = """\
words: for each path, start from its entry files and add every Markdown file that a read instruction in an
  already counted file names, transitively, counting each file once (whitespace-separated words).
  Entry files (under skills/):
    router      workflow/SKILL.md, workflow/flows/INDEX.md (the recipe table read at every change entry)
    bug         router + rule-maker/rules START, CORE, READINESS, OPERATIONS + workflow/flows/bug.md +
                SKILL.md of workflow-clarify, grilling, workflow-specify, workflow-execute, tdd, code-review,
                workflow-deliver
    lightweight router + the four rule-maker files + SKILL.md of workflow-specify, workflow-execute,
                code-review, workflow-deliver (minimal offer, one pass, one review, short delivery)
    bug_before_code  the bug path without code-review and workflow-deliver: those two SKILL.md files are
                never counted or followed, so a file only they name drops out (what is read before code)
  Read instruction: a sentence (lines split at . ! ?) with an imperative read/follow/apply or "run the ...
  check" (at the sentence start or after : ; , | and/then/first/now), or any sentence inside a "## Always"
  section. It does not count when the sentence holds a condition word (when, whenever, if but not "even if",
  unless, only, optional, needed, requested, asked, missing, conflict..., contradict..., UI) or its line opens
  with When/Whenever/If/Unless/Only/While/For/UI/"Run this step when".
  Names followed: Markdown link targets, backticked paths ending in .md or / (a folder means its SKILL.md)
  and bare upper-case NAME.md words; resolved from the file's folder, then from skills/. Unresolved names are
  skipped. Limits: a sentence-level heuristic; conditions phrased without those words still count, and
  instructions without those verbs ("owns", "see") are not followed.
hooks: per --sizes, a synthetic transcript (the router prompt, an approved offer made with the tree's own
  offers.py, then assistant text, tool_use and tool_result rows) and a temp repo with .git and
  docs/plans/<task>/PLAN.md. Each kind runs every hook command hooks/hooks.json registers for its calls
  (matchers read from the file): bash_read_only = PreToolUse+PostToolUse Bash "git status"; read =
  PostToolUse Read; edit = PreToolUse+PostToolUse Edit of src/vat.ts. Every run gets its own empty
  WORKFLOW_AXA_GATE_CACHE, settings file and WORKFLOW_AXA_HOME in a temp folder; the hooks run once to fill the
  cache and the timed run follows (steady state: nothing new since the last call). cold_median_ms is that
  first call. Times are wall-clock per kind (all its processes in turn).
stops: owner-facing questions on a one-ticket bug, from a fixed table of (question, file, phrase, skip): a
  stop counts when its phrase is in the file and its skip pattern is not. Limits: phrase presence, not
  behaviour; the readiness question is asked only when rules have gaps; conditional questions (classification,
  grilling, report review) are left out.
"""


def word_count(path: Path) -> int:
    return len(path.read_text(encoding="utf-8", errors="replace").split())


def resolve(name: str, here: Path, skills: Path) -> Path | None:
    for base in (here, skills):
        candidate = (base / name).resolve()
        if candidate.is_dir():
            candidate = candidate / "SKILL.md"
        if candidate.is_file() and candidate.suffix == ".md" and candidate.is_relative_to(skills.resolve()):
            return candidate
    return None


def instructed_names(text: str) -> list[str]:
    names, in_always = [], False
    for raw in text.splitlines():
        if raw.startswith("#"):
            in_always = bool(ALWAYS_HEADING.match(raw))
            continue
        line = LIST_MARK.sub("", raw).replace("**", "").strip()
        if not line or OPENER.match(line):
            continue
        for sentence in SENTENCE.split(line):
            if CONDITION.search(sentence) or UI_CONDITION.search(sentence):
                continue
            if in_always or READ_VERB.search(sentence):
                names += LINK.findall(sentence) + CODE_PATH.findall(sentence) + BARE_NAME.findall(sentence)
    return names


def reading_set(root: Path, entries: tuple[str, ...], excluded: tuple[str, ...] = ()) -> list[Path]:
    skills = (root / "skills").resolve()
    skipped = {(skills / e).resolve() for e in excluded}
    queue = [skills / e for e in entries if (skills / e).is_file()]
    seen: list[Path] = []
    while queue:
        path = queue.pop(0).resolve()
        if path in seen or path in skipped:
            continue
        seen.append(path)
        for name in instructed_names(path.read_text(encoding="utf-8", errors="replace")):
            found = resolve(name, path.parent, skills)
            if found and found not in seen:
                queue.append(found)
    return seen


def measure_words(root: Path) -> dict:
    result = {}
    for name, entries in ENTRIES.items():
        files = reading_set(root, entries, EXCLUDED.get(name, ()))
        per_file = {p.relative_to(root.resolve()).as_posix(): word_count(p) for p in files}
        result[name] = {"files": list(per_file), "per_file": per_file, "total": sum(per_file.values())}
    return result


def measure_stops(root: Path) -> dict:
    questions = []
    for question, file, phrase, skip in STOPS:
        path = root / "skills" / file
        text = path.read_text(encoding="utf-8", errors="replace") if path.is_file() else ""
        if phrase in text and not (skip and re.search(skip, text)):
            questions.append(question)
    return {"one_ticket_bug": {"questions": questions, "count": len(questions)}}


def stamp(seconds: float) -> str:
    return dt.datetime.fromtimestamp(seconds, dt.timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def load_offers(root: Path):
    spec = importlib.util.spec_from_file_location(f"measured_offers_{abs(hash(str(root)))}",
                                                  root / "skills/workflow/scripts/offers.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def build_case(root: Path, base: Path, size: int) -> tuple[Path, Path]:
    repo = base / "repo"
    (repo / ".git").mkdir(parents=True)
    (repo / "src").mkdir()
    (repo / "src/vat.ts").write_text("export const vat = 1;\n", encoding="utf-8")
    folder = repo / "docs/plans" / TASK
    folder.mkdir(parents=True)
    (folder / "PLAN.md").write_text("# VAT\n\n## Current checkpoint\n- Status: executing\n", encoding="utf-8")
    clock = time.time() + 600
    rows: list[dict] = []

    def add(row: dict) -> None:
        row["uuid"] = f"u{len(rows) + 1}"
        row["timestamp"] = stamp(clock + len(rows))
        rows.append(row)

    add({"type": "user", "message": {"role": "user", "content": "/workflow-axa:workflow fix vat"}})
    try:
        offers = load_offers(root)
        offer = offers.create(folder, {"behaviour": "Round VAT per line", "paths": ["src/vat.ts"],
                                       "operations": [], "checks": ["npm test"]})
        add({"type": "assistant", "message": {"content": [{"type": "text", "text": "Here is the offer.\n\n"
                                                           + offers.presentation(offer, folder)}]}})
        add({"type": "user", "message": {"role": "user", "content": "yes"}})
    except Exception as error:
        print(f"note: no approved offer in the transcript ({error})", file=sys.stderr)
    tools = (("Read", {"file_path": str(repo / "src/vat.ts")}), ("Bash", {"command": "git status"}),
             ("Grep", {"pattern": "vat", "path": str(repo)}))
    n = 0
    while len(rows) < size:
        tool, data = tools[n % len(tools)]
        add({"type": "assistant", "message": {"content": [{"type": "text", "text": f"Step {n}: checking vat."}]}})
        add({"type": "assistant", "message": {"content": [{"type": "tool_use", "id": f"t{n}", "name": tool,
                                                           "input": data}]}})
        add({"type": "user", "message": {"role": "user", "content": [{"type": "tool_result", "tool_use_id": f"t{n}",
                                                                      "content": f"result {n}"}]}})
        n += 1
    transcript = base / "session.jsonl"
    transcript.write_text("\n".join(json.dumps(r) for r in rows), encoding="utf-8")
    return repo, transcript


def registered(root: Path, event: str, tool: str) -> list[list[str]]:
    config = json.loads((root / "hooks/hooks.json").read_text(encoding="utf-8"))
    commands = []
    for group in config.get("hooks", {}).get(event, []):
        matcher = group.get("matcher", "")
        if matcher in ("", "*") or re.fullmatch(matcher, tool):
            for hook in group.get("hooks", []):
                if hook.get("type") == "command":
                    line = hook["command"].replace("${CLAUDE_PLUGIN_ROOT}", root.as_posix())
                    argv = shlex.split(line)
                    commands.append([sys.executable if argv[0] in ("python", "python3") else argv[0], *argv[1:]])
    return commands


def event_for(kind_event: str, tool: str, repo: Path, transcript: Path) -> dict:
    target = str(repo / "src/vat.ts")
    data = {"Bash": {"command": "git status"}, "Read": {"file_path": target},
            "Edit": {"file_path": target, "old_string": "1", "new_string": "2"}}[tool]
    event = {"session_id": "measure", "hook_event_name": kind_event, "tool_name": tool, "tool_input": data,
             "cwd": str(repo), "transcript_path": str(transcript)}
    if kind_event == "PostToolUse":
        event["tool_response"] = {"Bash": {"stdout": "nothing to commit", "stderr": "", "interrupted": False},
                                  "Read": {"type": "text", "file": {"filePath": target,
                                                                    "content": "export const vat = 1;\n"}},
                                  "Edit": {"filePath": target, "oldString": "1", "newString": "2"}}[tool]
    return event


def run_calls(calls: list[tuple[list[str], dict]], env: dict) -> float:
    started = time.perf_counter()
    for argv, event in calls:
        done = subprocess.run(argv, input=json.dumps(event), capture_output=True, text=True, encoding="utf-8", env=env)
        if done.returncode != 0:
            print(f"note: {Path(argv[-1]).name if argv else '?'} exited {done.returncode}: {done.stderr[-300:]}",
                  file=sys.stderr)
    return (time.perf_counter() - started) * 1000


def measure_hooks(root: Path, sizes: list[int], repeat: int) -> dict:
    result = {kind: {} for kind in HOOK_CALLS}
    for size in sizes:
        with tempfile.TemporaryDirectory(prefix="measure-speed-") as tmp:
            base = Path(tmp)
            repo, transcript = build_case(root, base, size)
            for kind, calls in HOOK_CALLS.items():
                planned = [(argv, event_for(event, tool, repo, transcript))
                           for event, tool in calls for argv in registered(root, event, tool)]
                warm, cold = [], []
                for run in range(repeat if planned else 0):
                    state = base / f"state-{kind}-{run}"
                    state.mkdir()
                    env = {**os.environ, "CLAUDE_PLUGIN_ROOT": str(root), "WORKFLOW_AXA_GATE_CACHE": str(state / "cache"),
                           "WORKFLOW_AXA_SETTINGS": str(state / "settings.json"),
                           "WORKFLOW_AXA_HOME": str(state / "home")}
                    cold.append(run_calls(planned, env))
                    warm.append(run_calls(planned, env))
                result[kind][str(size)] = {"median_ms": round(statistics.median(warm), 1) if warm else 0.0,
                                           "cold_median_ms": round(statistics.median(cold), 1) if cold else 0.0,
                                           "processes": len(planned)}
    return result


def sizes_arg(text: str) -> list[int]:
    try:
        sizes = [int(part) for part in text.split(",") if part.strip()]
    except ValueError:
        raise argparse.ArgumentTypeError("sizes must be comma-separated integers")
    if not sizes or min(sizes) < 1:
        raise argparse.ArgumentTypeError("sizes must be positive")
    return sizes


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, epilog=HELP,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT, help="workflow-axa tree to measure")
    parser.add_argument("--json", action="store_true", help="print JSON with the keys words, hooks, stops")
    parser.add_argument("--sizes", type=sizes_arg, default=[1000, 5000, 20000], help="transcript rows, comma-separated")
    parser.add_argument("--repeat", type=int, default=5, help="timed runs per kind and size (median reported)")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    if not (root / "skills").is_dir() or not (root / "hooks/hooks.json").is_file():
        parser.error(f"{root} is not a workflow-axa tree (needs skills/ and hooks/hooks.json)")
    if args.repeat < 1:
        parser.error("--repeat must be at least 1")
    data = {"words": measure_words(root), "hooks": measure_hooks(root, args.sizes, args.repeat),
            "stops": measure_stops(root)}
    if args.json:
        print(json.dumps(data, indent=2))
        return 0
    for name, path in data["words"].items():
        print(f"words {name}: {path['total']} in {len(path['files'])} files")
    for kind, by_size in data["hooks"].items():
        for size, numbers in by_size.items():
            print(f"hooks {kind} {size} rows: {numbers['median_ms']} ms warm, {numbers['cold_median_ms']} ms cold, "
                  f"{numbers['processes']} processes")
    stops = data["stops"]["one_ticket_bug"]
    print(f"stops one_ticket_bug: {stops['count']}")
    for question in stops["questions"]:
        print(f"  - {question}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
