"""Stop hook: one correction for missing required evidence/reads, never a punctuation-only retry.

Style guidance remains in WRITING/simple-english. This hook does not prove comprehension or completed review.
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


READ_VERB = re.compile(r"^\s*(?:cat|type|get-content|gc|more|less|bat)\b", re.I)
PARTIAL = re.compile(r"\b(?:head|tail)\b|\bsed\s+-n\b|-totalcount|-tail\b|\bselect-object\s+-first", re.I)


def whole_reads(block: dict) -> str:
    """The paths a tool call read whole: Read without a line limit, or a cat-like shell segment not cut by head,
    tail or sed -n (round v2: `wc -c` on a required file counted as reading it)."""
    data = block.get("input") or {}
    if block.get("name") == "Read":
        return "" if data.get("limit") else str(data.get("file_path", "")).replace("\\", "/")
    if block.get("name") not in ("Bash", "PowerShell"):
        return ""
    pipelines = re.split(r"&&|\|\||;|\n", str(data.get("command", "")))
    read = [p for p in pipelines if READ_VERB.match(p) and not PARTIAL.search(p)]
    return "\n".join(read).replace("\\", "/")


def unread_files(path: Path) -> dict[str, list[str]]:
    """For each workflow phase loaded in the session, the required files not opened in the current context.
    A read counts from the last compaction on, also before the phase loaded (round 22: the router's reads were
    demanded again). UI files count only when the session worked on a visible change (round 17)."""
    reads, ui_files = phase_reads_table()
    loaded: set[str] = set()
    inputs: list[str] = []
    visible = False
    tdd = False
    code = False
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            entry = json.loads(line)
        except ValueError:
            continue
        content = (entry.get("message") or {}).get("content")
        if entry.get("type") == "system" and entry.get("subtype") == "compact_boundary":
            inputs = []  # the summary does not carry the files' text
        if entry.get("type") == "user":
            text = json.dumps(content)
            for name in reads:
                if f"/workflow-axa:{name}" in text or f"/{name}<" in text:
                    loaded.add(name)
        if entry.get("type") != "assistant" or not isinstance(content, list):
            continue
        for block in content:
            if not isinstance(block, dict) or block.get("type") != "tool_use":
                continue
            data = json.dumps(block.get("input", {})).replace("\\\\", "/").replace("\\", "/")
            if block.get("name") == "Skill":
                skill = str((block.get("input") or {}).get("skill", "")).split(":")[-1]
                if skill in reads:
                    loaded.add(skill)
            if block.get("name") == "Read":
                # E5: the router's fallback, "or read its SKILL.md in full", loads the phase too.
                read = whole_reads(block)
                if read and not (block.get("input") or {}).get("offset"):
                    loaded.update(name for name in reads if read.endswith(f"/{name}/SKILL.md"))
            # Detect explicit task metadata, not the mere presence of "screen_change": "not-needed".
            plain = json.dumps(block.get("input", {})).replace('\\"', '"')
            if re.search(r'"screen_change"\s*:\s*"visible"|"ui_review"\s*:\s*\{', plain):
                visible = True
            if re.search(r'"tdd"\s*:\s*(?:true|"yes")|\bTDD:\s*yes\b', plain, re.I):
                tdd = True
            target = str((block.get("input") or {}).get("file_path", "")).replace("\\", "/")
            if block.get("name") in ("Edit", "Write", "MultiEdit", "NotebookEdit") and target \
                    and not re.search(r'(?:^|/)(?:docs/plans|\.artifacts)/', target) \
                    and Path(target).suffix not in ('.md', '.txt', '.html', '.json'):
                code = True
            inputs.append(whole_reads(block))
    missing = {}
    opened = "\n".join(inputs)
    for phase in loaded:
        needed = [rel for rel in reads[phase]
                  if (visible or rel not in ui_files)
                  and (tdd or rel != 'tdd/SKILL.md')
                  and (code or rel != 'code-review/SKILL.md')]
        gone = [rel for rel in needed if rel not in opened]
        if gone:
            missing[phase] = gone
    return missing


def unsaid_behind(path: Path) -> str | None:
    """The project version from a BEHIND rules stamp that no later reply mentioned (round v1: Altinstar)."""
    pending = None
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            entry = json.loads(line)
        except ValueError:
            continue
        content = (entry.get("message") or {}).get("content")
        if not isinstance(content, list):
            continue
        for block in content:
            if not isinstance(block, dict):
                continue
            if block.get("type") == "tool_result":
                found = re.search(r"STATE: BEHIND project (\d+\.\d+\.\d+)", json.dumps(block.get("content")))
                if found:
                    pending = found.group(1)
            elif entry.get("type") == "assistant" and block.get("type") == "text" and pending \
                    and pending in block.get("text", ""):
                pending = None
    return pending


EDIT_TOOLS = ("Edit", "Write", "MultiEdit", "NotebookEdit")
RECORD_PATH = re.compile(r"(?:^|/)(?:docs/plans|\.artifacts)/", re.I)
DONE = re.compile(r"\*\*Done\b|^Done\.?$", re.M)
REVIEW = re.compile(r"\breview", re.I)  # review, reviewer, code-review; not preview


def review_ran(block: dict) -> bool:
    """An Agent call whose description or subagent_type names a review, or a load or whole read of code-review.
    The prompt text does not count: a builder's prompt often says "then ask for a review"."""
    data = block.get("input") or {}
    if block.get("name") == "Agent":
        return bool(REVIEW.search(f"{data.get('description', '')} {data.get('subagent_type', '')}"))
    if block.get("name") == "Skill":
        return str(data.get("skill", "")).split(":")[-1] == "code-review"
    if block.get("name") == "Read" and not data.get("offset"):
        return whole_reads(block).endswith("/code-review/SKILL.md")
    return False


def unreviewed_code(path: Path, reply: str, cwd: str = "") -> list[str]:
    """Code files changed after the last review and with no delivery, when the reply ends as Done.

    Loop w2/w3 (Altinstar): a comment-only change was edited, closed and called done with no review and no
    deliver short form, although the router requires both even for a lightweight edit."""
    if not DONE.search(reply):
        return []
    root = cwd.replace("\\", "/").rstrip("/").lower()
    changed: list[str] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            entry = json.loads(line)
        except ValueError:
            continue
        content = (entry.get("message") or {}).get("content")
        if entry.get("type") != "assistant" or not isinstance(content, list):
            continue
        for block in content:
            if not isinstance(block, dict) or block.get("type") != "tool_use":
                continue
            data = block.get("input") or {}
            if block.get("name") in EDIT_TOOLS:
                target = str(data.get("file_path") or data.get("notebook_path") or "").replace("\\", "/")
                inside = not root or target.lower().startswith(root + "/")  # loop w5: scratchpad helpers outside
                if target and inside and not RECORD_PATH.search(target) and target not in changed:
                    changed.append(target)
            elif review_ran(block):
                changed = []  # a review ran after these edits
            elif block.get("name") == "Skill" and str(data.get("skill", "")).endswith("workflow-deliver"):
                changed = []
    return changed


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
    if not isinstance(event, dict) or event.get("stop_hook_active"):
        return 0  # one substantive correction at most; never loop
    # A direct stop must not cause another round of reading, reviewing or implementation.
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location('phase_gate_stop', Path(__file__).with_name('phase_gate.py'))
        gate = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(gate)
        state = gate.scan(Path(event.get('transcript_path', '')), str(event.get('cwd') or ''))
        task = state['tasks'][-1][0] if state['tasks'] else '*'
        if task in state.get('paused_tasks', {}) or '*' in state.get('paused_tasks', {}):
            return 0
    except (OSError, ValueError, KeyError, TypeError):
        pass
    try:
        reply, used = last_reply_and_usage(Path(event.get("transcript_path", "")))
    except OSError:
        return 0
    found = problems(reply) if used else []
    try:
        unread = unread_files(Path(event.get("transcript_path", ""))) if used else {}
    except (OSError, ValueError, AttributeError):
        unread = {}
    try:
        behind = unsaid_behind(Path(event.get("transcript_path", ""))) if used else None
    except OSError:
        behind = None
    try:
        unreviewed = unreviewed_code(Path(event.get("transcript_path", "")), reply, str(event.get("cwd") or "")) if used else []
    except OSError:
        unreviewed = []
    reasons = []
    if unreviewed:
        reasons.append(f"workflow-axa: you changed {len(unreviewed)} file(s) ({', '.join(unreviewed[:3])}) but no "
                       "review ran after the last change and no delivery was recorded, yet you report Done. Run the "
                       "independent review the router and workflow-execute require (one fresh reviewer; a lightweight "
                       "edit gets one review too), then workflow-deliver (its short form for a lightweight edit). If "
                       "the owner stopped the task, record it as stopped and partial instead of Done.")
    if behind:
        reasons.append(f"workflow-axa: rules_stamp.py said this project's rules were checked against {behind}, which is "
                       "older than the installed rules, and you have not told the owner. Add its SAY sentence (the "
                       "rules audit offer) to your reply once. It does not block the task.")
    if unread:
        listing = "; ".join(f"{phase}: {', '.join(files)}" for phase, files in unread.items())
        reasons.append("workflow-axa: these required files were not opened in this context: " + listing +
                       ". Read them now (whole), check your work and records against them, correct anything they change, "
                       "and name only files you actually opened.")
    if found and reasons:
        reasons.append("workflow-axa simple-english: your last message has " + " and ".join(found) + ". Send it again "
                       "with full forms (\"do not\", \"I am\"), two sentences instead of a semicolon or dash, and the same "
                       "facts. Code, paths and quoted text stay as they are.")
    if reasons:
        print(json.dumps({"decision": "block", "reason": " ".join(reasons)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
