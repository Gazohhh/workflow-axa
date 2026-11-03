"""Stop hook: in a session that used a workflow-axa skill, ask once for a rewrite when the last reply breaks
the simple-english reply rules (contractions, em-dashes, semicolons).

Retros found contractions in chat even after the wording rules said not to. The hook reads the transcript the
host passes, never blocks twice in a row (stop_hook_active), and exits 0 on any problem with its own input.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

CONTRACTION = re.compile(r"\b(?:[A-Za-z]+n['’]t|I['’]m|I['’]ve|I['’]ll|I['’]d|(?:you|we|they|it|that|there|here|what|who)['’](?:s|re|ve|ll|d))\b", re.I)
CODE = re.compile(r"```.*?```|`[^`\n]*`", re.S)


def last_reply_and_usage(path: Path) -> tuple[str, bool]:
    reply, used = "", False
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            entry = json.loads(line)
        except ValueError:
            continue
        message = entry.get("message") or {}
        content = message.get("content")
        if entry.get("type") == "assistant" and isinstance(content, list):
            texts = [block.get("text", "") for block in content if isinstance(block, dict) and block.get("type") == "text"]
            if texts:
                reply = "\n".join(texts)
            if any(isinstance(b, dict) and b.get("type") == "tool_use" and "workflow-axa" in json.dumps(b.get("input", {}))
                   for b in content):
                used = True
        elif entry.get("type") == "user" and "workflow-axa:" in json.dumps(content):
            used = True
    return reply, used


def phase_reads_table() -> dict:
    import importlib.util
    spec = importlib.util.spec_from_file_location('phase_reads', Path(__file__).with_name('phase_reads.py'))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.READS, set(module.UI)


def unread_files(path: Path) -> dict[str, list[str]]:
    """For each workflow phase loaded in the session, the required files not opened after its last load.
    UI files count only when the session worked on a visible change (round 17: reminders were ignored)."""
    reads, ui_files = phase_reads_table()
    loads: dict[str, int] = {}
    inputs: list[str] = []
    visible = False
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            entry = json.loads(line)
        except ValueError:
            continue
        content = (entry.get("message") or {}).get("content")
        if entry.get("type") == "user":
            text = json.dumps(content)
            for name in reads:
                if f"/workflow-axa:{name}" in text or f"/{name}<" in text:
                    loads[name] = len(inputs)
        if entry.get("type") != "assistant" or not isinstance(content, list):
            continue
        for block in content:
            if not isinstance(block, dict) or block.get("type") != "tool_use":
                continue
            data = json.dumps(block.get("input", {})).replace("\\\\", "/").replace("\\", "/")
            if block.get("name") == "Skill":
                skill = str((block.get("input") or {}).get("skill", "")).split(":")[-1]
                if skill in reads:
                    loads[skill] = len(inputs)
            if "ui_review" in data or "screen_change" in data:
                visible = True
            inputs.append(data)
    missing = {}
    for phase, start in loads.items():
        after = "\n".join(inputs[start:])
        needed = [rel for rel in reads[phase] if visible or rel not in ui_files]
        gone = [rel for rel in needed if rel not in after]
        if gone:
            missing[phase] = gone
    return missing


def problems(reply: str) -> list[str]:
    prose = CODE.sub("", reply)  # code, paths and quoted identifiers are exempt
    found = []
    words = sorted({m.group(0) for m in CONTRACTION.finditer(prose)})
    if words:
        found.append("contractions (" + ", ".join(words[:6]) + ")")
    if "—" in prose:
        found.append("em-dashes")
    if ";" in prose:
        found.append("semicolons")
    return found


def main() -> int:
    try:
        event = json.load(sys.stdin)
    except ValueError:
        return 0
    if event.get("stop_hook_active"):
        return 0  # one rewrite at most; never loop
    try:
        reply, used = last_reply_and_usage(Path(event.get("transcript_path", "")))
    except OSError:
        return 0
    found = problems(reply) if used else []
    try:
        unread = unread_files(Path(event.get("transcript_path", ""))) if used else {}
    except (OSError, ValueError, AttributeError):
        unread = {}
    reasons = []
    if unread:
        listing = "; ".join(f"{phase}: {', '.join(files)}" for phase, files in unread.items())
        reasons.append("workflow-axa: these required files were not opened after their phase loaded: " + listing +
                       ". Read them now (whole), check your work and records against them, correct anything they change, "
                       "and name only files you actually opened.")
    if found:
        reasons.append("workflow-axa simple-english: your last message has " + " and ".join(found) + ". Send it again "
                       "with full forms (\"do not\", \"I am\"), two sentences instead of a semicolon or dash, and the same "
                       "facts. Code, paths and quoted text stay as they are.")
    if reasons:
        print(json.dumps({"decision": "block", "reason": " ".join(reasons)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
