"""The offer checker: PreToolUse hook of the redesign (REDESIGN.md §3.4, §3.6, §7; contracts C-OFFER-2..7, C-CSS-1/2,
C-RULES-1, C-SAFE-1). It replaces the approval forensics of phase_gate.py at the cutover (T17).

A project write is allowed when an **approved offer** (skills/workflow/scripts/offers.py) covers it. Approval is
proven from the host transcript, never from a stored flag:

- **Presentation** of offer #N is the exact text `record.py offer present` prints (offers.presentation, format 2):
  it names the offer, its hash, its task and its workspace, so identical offers in two tasks or checkouts never
  share consent. It (or its `--question` variant) counts as the end of a visible assistant message (nothing that
  could hide it before it), or as
  the text of one question of a question-tool call (`--question`); then only that question's answer counts. The
  frozen format 1 block (offers.rendering) still counts anywhere in a message, for offers shown before format 2.
  An edited or stale presentation is none. The display-only CSS line is outside it.
- **The answer** is the first real owner turn after the latest presentation: the question's "Approve from this
  summary" (or "Approve"; a button may end in "(Recommended)"), `/approve <N>`, or a whole message that is one of:
  approve, approved, yes, ok, okay, go, ja, akkoord, doe maar, or, after a presentation in text (either variant), a
  typed "Approve from this summary" with its surrounding punctuation and emphasis ignored. "Show review.html first",
  "show report" or `/report <N>` approves nothing yet: the next approval counts only
  after a message names the task's existing report, in a later session too. Anything else, a qualified "yes but ..."
  included, approves nothing: the agent writes a narrowed offer.
- **After approval:** a later owner message that withdraws it ("revoke", "not approved") ends it; one that may narrow
  it (but, except, only, without ...) suspends it until a narrowed offer is approved; a stop pauses all writes until
  the owner asks to continue, and the approval then holds again. Approving a presented offer continues too: the
  approve button on its question, or `/approve <N>` as the answer to its presentation (paused()).
- **`/wait-what`** is a non-answer: only a re-presentation can be answered after it.
- **History across sessions:** the project's transcripts are the history; nothing else is recorded, so no failed
  note can hide a withdrawal. Each transcript changed since the offer was made yields timed facts (decide); fold()
  orders all of them, this session's included, and the state that results decides. Another session's messages count
  only after it first names the task. An unreadable transcript refuses. The offer's decision reference only caches
  the approval that holds (for child offers).
- **Offer files** change only through `record.py offer`; a direct write to docs/plans/<task>/offers/ is refused.

Operations (git writes, MCP tools) are allowed when an approved offer lists them exactly ("git commit", the MCP tool
name). Kept safeguards from phase_gate.py: package installs need the owner's latest words, bulk deletes under
.artifacts and `git clean` are refused, unresolvable shell targets are refused. Styling writes also need the machine
CSS switch (settings.py; off by default) and no `css: never` in the project's DESIGN.md. Changing the switch needs the
owner's Yes to the question naming that exact setting and value, once. An open rules question pauses every write.
Task records and .artifacts stay writable. Errors fail closed for every recognised write.
"""
from __future__ import annotations

import json
import os
import sys

FAST_PROGRAMS = {"ls", "cat", "head", "tail", "grep", "rg", "find", "wc", "pwd", "dir", "get-childitem", "gci",
                 "get-content", "gc", "select-string", "sls", "test-path", "get-item", "get-location", "resolve-path"}
FAST_GIT = {"status", "log", "diff", "show", "rev-parse", "ls-files"}
FAST_BRANCH_LIST = {"--list", "-l", "-a", "--all", "-r", "--remotes", "-v", "-vv", "--verbose", "--show-current",
                    "--no-color"}
FAST_UNSAFE = set("><|;&$`(){}\\\n\r")
FAST_NAMES = ("record.py", "settings.py", "legacy_inventory", "render_report", "worktree", "install")
FAST_FIND_WRITES = ("-exec", "-ok", "-delete", "-fprint", "-fls")


def read_only_command(command: str) -> bool:
    lowered = command.lower()
    if not command.strip() or any(c in FAST_UNSAFE for c in command) or any(n in lowered for n in FAST_NAMES):
        return False
    words = [w.replace('"', "").replace("'", "") for w in lowered.split()]
    program, args = words[0], words[1:]
    if program == "git":
        if not args or any(a.startswith("--output") for a in args):
            return False
        if args[0] == "branch":
            return all(a in FAST_BRANCH_LIST for a in args[1:])
        return args[0] in FAST_GIT
    if program == "find" and any(a.startswith(FAST_FIND_WRITES) for a in args):
        return False
    if program == "rg" and any(a.startswith("--pre") for a in args):
        return False
    return program in FAST_PROGRAMS


def fast_allow(raw: str) -> bool:
    try:
        event = json.loads(raw)
    except ValueError:
        return True
    if not isinstance(event, dict) or event.get("hook_event_name", "PreToolUse") != "PreToolUse" \
            or not event.get("transcript_path"):
        return True
    data = event.get("tool_input")
    command = data.get("command") if isinstance(data, dict) else None
    if event.get("tool_name") not in ("Bash", "PowerShell") or not isinstance(command, str) \
            or not read_only_command(command):
        return False
    try:
        open(str(event["transcript_path"]), "rb").close()
    except FileNotFoundError:
        return True
    except (OSError, ValueError):
        return False
    return True


if __name__ == "__main__":
    HOOK_INPUT = sys.stdin.read()
    if fast_allow(HOOK_INPUT):
        sys.exit(0)
    import io
    sys.stdin = io.StringIO(HOOK_INPUT)

import glob
import importlib.util
import shlex
import re
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent / "skills" / "workflow" / "scripts"
APPROVE_WORDS = {"approve", "approved", "yes", "ok", "okay", "go", "ja", "akkoord", "doe maar"}
YES_WORDS = {"yes", "ja", "y", "ok", "okay"}
APPROVE_BUTTONS = {"approve from this summary", "approve"}
REPORT_BUTTONS = {"show review.html first", "show review.html before i decide", "show report", "show the report"}
LABEL_EDGES = " \t.!?,;:\"'*_`-"
RECOMMENDED = re.compile(r"\s*\(recommended\)$")
SLASH = re.compile(r"^/(approve|report)\s+#?(\d+)$")
SETTINGS_QUESTION = re.compile(r"\bturn\s+css\s+(on|off)\b", re.I)
SETTINGS_RUN = re.compile(r"settings\.py[\"']?\s+(?:--file\s+\S+\s+)?css\s+(on|off)\b", re.I)
WRITE_TOOLS = ("Edit", "Write", "MultiEdit", "NotebookEdit", "Bash", "PowerShell")


def _load(name: str, path: Path):
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        try:
            spec.loader.exec_module(module)
        except BaseException:  # never keep a half-loaded module: the next use would hide the real error
            sys.modules.pop(name, None)
            raise
    return sys.modules[name]


def gate():
    return _load("workflow_axa_phase_gate", HERE / "phase_gate.py")


def offers():
    return _load("workflow_axa_offers", SCRIPTS / "offers.py")


def settings():
    return _load("workflow_axa_settings", SCRIPTS / "settings.py")


def inventory():
    return _load("workflow_axa_legacy_inventory", SCRIPTS / "legacy_inventory.py")


INVENTORY_RUN = re.compile(r"legacy_inventory\.py\b[^\n;&|]*?\s--(?:apply|replace)\b")  # owner-only (C-LEG-1)
LEGACY = object()  # problem_for's answer when the legacy checker decides this call


# The transcript as the few events the offer checker needs

@dataclass
class Event:
    kind: str  # text | question | answer | user | task (the session moved to the task named in `text`)
    uuid: str
    text: str = ""
    tool_id: str = ""
    questions: list = field(default_factory=list)  # question: the payload's questions, each {"question": ..., ...}
    answers: dict = field(default_factory=dict)  # answer: question text -> chosen value
    time: str = ""  # the host's timestamp, to order events across sessions


OFFER_TASK = re.compile(r"--- workflow-axa offer #(\d+) \([0-9a-f]+\) · task (\S+) · ")
OFFER_FOOTER = re.compile(r"\n`+ ?Offer #(\d+) · [0-9a-f]+ · task (\S+)(?: · [^\n]*)? ?`+[ \t\n]*\Z")
ANY_FOOTER = re.compile(r"Offer #\d+ · [0-9a-f]+ · task ")


@dataclass(frozen=True)
class Shown:
    """The accepted presentations of one offer: the format 2 message (offers.presentation), whose two variants each
    count as the end of the assistant's text and whose question variant also counts as a question's own text, and, for an
    offer recorded before format 2 only, the frozen format 1 block anywhere in a message, as before."""
    legacy: str
    text: str
    question: str

    def in_text(self, message: str, before: str = "") -> bool:
        return bool(self.legacy) and self.legacy in message or ends_with(before + message, self.text) \
            or ends_with(before + message, self.question)

    def in_question(self, question: dict) -> bool:
        return bool(self.legacy) and self.legacy in strings(question) \
            or ends_with(str(question.get("question", "")), self.question)


def ends_with(message: str, presentation: str) -> bool:
    """Format 2 counts only as the end of a message: at its start or after a blank line, nothing but whitespace after
    it, and nothing before it that could hide or garble it (any `<`, `$$`, or a run of three backticks or tildes)."""
    message = message.replace("\r\n", "\n")
    start = message.find(presentation)
    while start >= 0:
        before, after = message[:start], message[start + len(presentation):]
        if (not before or before.endswith("\n\n")) and not after.strip(" \t\n") and "<" not in before \
                and not re.search(r"`{3,}|~{3,}|\$\$", before):
            return True
        start = message.find(presentation, start + 1)
    return False


def shown(folder: Path, offer: dict) -> Shown:
    o = offers()
    legacy = o.rendering(offer, folder) if offer.get("presentation_format", 1) == 1 else ""
    return Shown(legacy, o.presentation(offer, folder), o.presentation(offer, folder, question=True))


def named_offers(text: str, question: dict | None = None) -> list[tuple[int, str, bool]]:
    named = [(int(i), t, False) for i, t in OFFER_TASK.findall(text)]
    own = str(question.get("question", "")) if question is not None else text
    footer = OFFER_FOOTER.search(own.replace("\r\n", "\n"))
    return named + ([(int(footer[1]), footer[2], True)] if footer else [])


def offer_tasks(text: str, root: Path | None, before: str = "", question: dict | None = None,
                named: list | None = None) -> list[tuple[str, bool, int]]:
    """The tasks a presentation moves the session to, each with whether it was format 2 and the offer's id: only an offer recorded in
    that task of this project, shown exactly as its approval needs (format 2 visibly at the end of its block, after
    `before`, or as a question's own text; format 1 only for an offer recorded before format 2), so a made-up or
    hidden offer never moves the session. `question` is the question-tool question whose strings are `text`; `named`
    is named_offers() of them when already known."""
    if root is None:
        return []
    own = str(question.get("question", "")) if question is not None else text
    tasks = []
    for offer_id, task, format_2 in (named_offers(text, question) if named is None else named):
        folder = root / "docs" / "plans" / task
        try:
            view = shown(folder, offers().load(folder, offer_id))
        except (offers().OfferError, OSError, ValueError):
            continue
        if not format_2:
            ok = bool(view.legacy) and view.legacy in text
        elif question is not None:
            ok = ends_with(own, view.question)
        else:
            ok = ends_with(before + text, view.text) or ends_with(before + text, view.question)
        if ok:
            tasks.append((task, format_2, offer_id))
    return tasks


def read_events(path: Path, root: Path | None = None) -> list[Event]:
    """The events of a main transcript. Task transitions are the owner naming a task and a presentation of one of the
    task's offers (in visible text or a question, as offer_tasks validates it). A format 2 presentation in text moves
    the session only when the owner's next turn answers it with no assistant text after it, as approval requires. The
    agent's own record writes never move the session (REDESIGN §3.4, N4): bookkeeping must not decide which offer a
    later withdrawal, narrowing, stop or resume applies to. The transcript's lines are parsed once (entries()); the
    offers they name are checked against the files at every call."""
    events: list[Event] = []
    visible_block: list[str] = []
    awaiting_answer: list[Event] = []
    calls: dict[str, list] = {}
    for kind, uuid, time, *rest in entries(path, root):
        uuid = uuid or f"line{len(events)}"
        if kind == "typed":
            typed, tasks = rest
            events += awaiting_answer
            awaiting_answer = []
            events += [Event("task", uuid, task, time=time) for task in tasks]
            events.append(Event("user", uuid, typed, time=time))
            visible_block = []
        elif kind == "answer":
            tool_ids, answers = rest
            events += awaiting_answer
            awaiting_answer = []
            events += [Event("answer", uuid, tool_id=tool_id, answers=answers, questions=calls.get(tool_id, []),
                             time=time) for tool_id in tool_ids]
            visible_block = []
        else:
            visible, named, tool, asks, carried = rest
            found = offer_tasks(visible, root, "".join(text + "\n\n" for text in visible_block),
                                named=[tuple(n) for n in named]) if named else []
            if visible.strip():
                awaiting_answer = []
            if any(not format_2 for _, format_2, _ in found):
                awaiting_answer = []
            for task, format_2, _ in found:
                (awaiting_answer if format_2 else events).append(Event("task", uuid, task, time=time))
            if visible.strip():
                events.append(Event("text", uuid, visible, time=time))
                visible_block.append(visible)
            events += [Event("offer_shown", uuid, str(offer_id), time=time) for _, _, offer_id in found]
            if tool:
                events.append(Event("tool", uuid, carried, time=time))
                visible_block = []
            for tool_id, questions, named_each in asks:
                asked = [(q, t) for q, named in zip(questions, named_each) if named
                         for t, _, _ in offer_tasks(strings(q), root, question=q, named=[tuple(n) for n in named])]
                if asked:
                    awaiting_answer = []
                for _, task in asked:
                    events.append(Event("task", uuid, task, time=time))
                calls[tool_id] = questions
                events.append(Event("question", uuid, tool_id=tool_id, questions=questions, time=time))
                if asked:
                    events.append(Event("offer_asked", uuid, tool_id=tool_id, questions=[q for q, _ in asked],
                                        time=time))
    return events


ENTRIES_VERSION = 3


def entry_of(line: str) -> list | None:
    g = gate()
    try:
        entry = json.loads(line)
    except ValueError:
        return None
    if not isinstance(entry, dict) or entry.get("isSidechain"):
        return None
    uuid = str(entry["uuid"]) if entry.get("uuid") else None
    time = str(entry.get("timestamp") or "")
    content = (entry.get("message") or {}).get("content")
    typed = g.queued_text(entry) if entry.get("type") == "attachment" else g.user_text(entry)
    if typed is not None:
        return ["typed", uuid, time, typed, [a or b for a, b in g.TASK_NAMED.findall(g.slash(typed))]]
    result = entry.get("toolUseResult")
    if entry.get("type") == "user" and isinstance(result, dict) and isinstance(result.get("answers"), dict) \
            and isinstance(content, list) and not entry.get("isMeta"):
        tool_ids = [str(block.get("tool_use_id")) for block in content
                    if isinstance(block, dict) and block.get("type") == "tool_result" and not block.get("is_error")]
        return ["answer", uuid, time, tool_ids, result["answers"]]
    if entry.get("type") == "assistant" and isinstance(content, list):
        visible = "\n".join(str(b.get("text", "")) for b in content if isinstance(b, dict) and b.get("type") == "text")
        others = [strings(b.get("input")) for b in content if isinstance(b, dict) and b.get("type") == "tool_use"
                  and b.get("name") != "AskUserQuestion"]
        tool = bool(others)
        carried = "\n".join(t for t in others if "--- workflow-axa offer #" in t or ANY_FOOTER.search(t))
        asks = []
        for block in content:
            if isinstance(block, dict) and block.get("type") == "tool_use" and block.get("name") == "AskUserQuestion":
                data = block.get("input") or {}
                questions = [q for q in data.get("questions", []) if isinstance(q, dict)] if isinstance(data, dict) else []
                asks.append([str(block.get("id")), questions, [named_offers(strings(q), q) for q in questions]])
        return ["assistant", uuid, time, visible, named_offers(visible), tool, asks, carried]
    return None


def entries(path: Path, root: Path | None) -> list[list]:
    g = gate()
    data = path.read_bytes()
    cache = g.CACHE_DIR / "events" / f"{g.digest(f'{path.resolve()}|{root}'.encode('utf-8'))}.json"
    try:
        state = json.loads(cache.read_text(encoding="utf-8"))
        offset = state["offset"]
        if state["v"] != ENTRIES_VERSION or not isinstance(offset, int) or not 0 <= offset <= len(data) \
                or (offset and data[offset - 1:offset] != b"\n") or not isinstance(state["entries"], list) \
                or state["head"] != g.digest(data[:min(4096, offset)]) \
                or state["mark"] != g.digest(data[max(0, offset - 4096):offset]):
            raise ValueError("stale")
    except (OSError, ValueError, KeyError, TypeError):
        state = {"v": ENTRIES_VERSION, "offset": 0, "entries": []}
    end = data.rfind(b"\n") + 1

    def parsed(chunk: bytes) -> list[list]:
        return [found for found in map(entry_of, chunk.decode("utf-8", errors="replace").splitlines()) if found]

    if end > state["offset"]:
        state["entries"] += parsed(data[state["offset"]:end])
        state.update(offset=end, head=g.digest(data[:min(4096, end)]), mark=g.digest(data[max(0, end - 4096):end]))
        try:
            cache.parent.mkdir(parents=True, exist_ok=True)
            temporary = cache.with_suffix(f".{os.getpid()}.tmp")
            temporary.write_text(json.dumps(state), encoding="utf-8")
            os.replace(temporary, cache)
            old = time.time() - g.CACHE_DAYS * 86400
            for stale in cache.parent.glob("*.json"):
                if stale.stat().st_mtime < old:
                    stale.unlink()
        except OSError:
            pass
    return state["entries"] + parsed(data[end:])


def answer_to(event: Event, question: str) -> str:
    """The answer to one asked question. A host may key it by the question without its surrounding whitespace (T3
    Code drops a final line break); any other difference, two keys that both match, or two questions of the same
    call that both match, finds nothing."""
    alike = [q for q in event.questions if str(q.get("question", "")).strip() == question.strip()]
    if len(alike) > 1:
        return ""
    found = [value for key, value in event.answers.items() if isinstance(key, str) and key.strip() == question.strip()]
    return str(found[0]) if len(found) == 1 else ""


def strings(value) -> str:
    """Every string inside one question (its text, options and descriptions), joined."""
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        return "\n".join(strings(v) for v in value.values())
    if isinstance(value, list):
        return "\n".join(strings(v) for v in value)
    return ""


def words(text: str) -> str:
    g = gate()
    return g.bare(g.clean(text))


def command(text: str) -> tuple[str, str] | None:
    """A typed slash command (`/approve 3`) or the host's command form (<command-name>/approve</command-name>)."""
    found = re.search(r"<command-name>/?([\w:-]+)</command-name>", text)
    if found:
        args = re.search(r"<command-args>(.*?)</command-args>", text, re.S)
        return found[1].split(":")[-1].lower(), (args[1].strip() if args else "")
    found = re.match(r"^\s*/([\w-]+)\b\s*(.*)$", text, re.S)
    return (found[1].lower(), found[2].strip()) if found else None


@dataclass
class Facts:
    """What one transcript says about one offer, in order: [time, kind, detail, lo, hi] with kind approve (detail:
    [turn, presentation]), report, shown (a message named an existing report), other (an answer that isn't an
    approval), revoke, restrict, pause or resume. lo..hi is when it happened, in seconds: its own timestamp, or for an
    undated fact the dated events around it in the transcript (hi None: no dated event after it, so the file's last
    change, `end`, bounds it). And the reason to give when nothing was decided in it."""
    facts: list = field(default_factory=list)
    reason: str = "it was never presented in this session"
    end: float | None = None


def decide(events: list[Event], rendering: Shown, offer_id: int, report_shown, task: str, here: bool = False) -> Facts:
    """Pair each presentation of the offer with its answer, and collect the owner's withdrawals, narrowings, stops and
    continues while the session is on the offer's task (task transitions follow the session through switches). In the
    current session (`here`) a message before any task transition counts too: this write ties it to the offer.
    The order of facts across transcripts is settled by fold()."""
    g = gate()
    out = Facts()
    at_event: list[int] = []  # the event index of each fact, for its time bounds
    on = None  # the task the session is on
    presented = None  # uuid of the open visible presentation
    asked: dict[str, tuple[str, str]] = {}  # question tool id -> (event uuid, the question text that carries it)
    last_presented = None  # the offer the latest rendering in visible text belongs to (typed answers go to it)
    visible_block: list[str] = []
    open_is_format_2 = False
    footer = rendering.question.rstrip().splitlines()[-1] if rendering.question.strip() else "\0"
    for index, event in enumerate(events):
        if len(at_event) < len(out.facts):
            at_event += [index - 1] * (len(out.facts) - len(at_event))
        if event.kind in ("tool", "user", "answer"):
            visible_block = []
        if event.kind == "task":
            on = event.text
        elif event.kind == "tool" and presented is None and carries(event.text, rendering, footer):
            out.reason = ("the offer text was not in your reply text (a tool call such as a message tool is not a "
                          "presentation)")
        elif event.kind == "text":
            before = "".join(text + "\n\n" for text in visible_block)
            if rendering.in_text(event.text, before):
                presented, last_presented = event.uuid, offer_id
                open_is_format_2 = not (rendering.legacy and rendering.legacy in event.text)
                out.reason = "it was presented, but no owner answer came after it yet"
            elif "--- workflow-axa offer #" in event.text or ANY_FOOTER.search(event.text):
                last_presented = None
                if rendering.text in event.text or rendering.question in event.text:
                    out.reason = ("its presentation was not the end of the agent's text, or something before it could "
                                  "hide it (`<`, `$$` or a fenced block); after a tool call, present it again")
                elif footer in event.text:
                    out.reason = ("the presented text differs from the `record.py offer present` output "
                                  f"({difference(event.text, rendering)})")
            elif presented is not None and open_is_format_2:
                presented, last_presented = None, None
                out.reason = "more text followed its presentation; present it again as the end of the reply"
            visible_block.append(event.text)
            if report_shown(event.text):
                out.facts.append([event.time, "shown", ""])
        elif event.kind == "question":
            carrier = next((q for q in event.questions if rendering.in_question(q)), None)
            if carrier is not None:
                asked[event.tool_id] = (event.uuid, str(carrier.get("question", "")))
                presented, last_presented = None, None
                out.reason = "it was asked, but the question has no answer yet"
            elif "--- workflow-axa offer #" in strings(event.questions) or ANY_FOOTER.search(strings(event.questions)):
                last_presented = None
                if footer in strings(event.questions):
                    out.reason = ("a question carried this offer's footer, but its text is not exactly the output of "
                                  "`record.py offer present <task-folder> <id> --question`; ask again with that output "
                                  "unchanged, nothing added after the footer")
        elif event.kind == "answer" and event.tool_id not in asked and presented is not None \
                and last_presented == offer_id and any(
                    RECOMMENDED.sub("", str(v).strip().lower()) in APPROVE_BUTTONS for v in event.answers.values()):
            out.reason = ("the owner clicked approve on a question that did not contain this offer; ask with the "
                          "output of `record.py offer present <task-folder> <id> --question` as the question's own "
                          "text, or let the owner type approve after the offer shown as text")
        elif event.kind == "answer" and event.tool_id in asked:
            at, question = asked.pop(event.tool_id)
            value = RECOMMENDED.sub("", answer_to(event, question).strip().lower())
            kind = "approve" if value in APPROVE_BUTTONS else "report" if value in REPORT_BUTTONS else "other"
            out.facts.append([event.time, kind, [event.uuid, at] if kind == "approve" else
                              f"the answer \"{value[:60]}\" to its question is not an approval; write a narrowed offer"])
        elif event.kind == "user":
            said, slash = words(event.text), command(event.text)
            label = said.strip(LABEL_EDGES)
            if slash and slash[0] == "wait-what":
                presented = None
                continue
            if presented is not None and last_presented == offer_id:
                typed = SLASH.match(f"/{slash[0]} {slash[1]}") if slash else None
                if (typed and typed[1] == "approve" and int(typed[2]) == offer_id) or said in APPROVE_WORDS \
                        or label in APPROVE_BUTTONS:
                    out.facts.append([event.time, "approve", [event.uuid, presented]])
                elif (typed and typed[1] == "report" and int(typed[2]) == offer_id) or said in REPORT_BUTTONS \
                        or label in REPORT_BUTTONS:
                    out.facts.append([event.time, "report", ""])
                elif slash and slash[0] == "approve" and re.match(rf"#?{offer_id}\s+\S", slash[1]):
                    out.facts.append([event.time, "other", f"\"/approve {offer_id}\" had more text after it, and extra "
                                      "words may narrow the approval; after the next presentation the owner sends "
                                      f"\"/approve {offer_id}\" alone or clicks the approve button"])
                else:
                    out.facts.append([event.time, "other", f"the owner's answer \"{said[:80]}\" is not one of the "
                                      "approval forms; a conditional answer needs a narrowed offer, presented again"])
                presented = None
            intent = g.control_intent(event.text)
            kind = "pause" if intent == "pause" else "resume" if intent == "resume" else \
                "revoke" if g.REVOKED.search(said) else "restrict" if g.RESTRICTS.search(said) else None
            if kind and (on == task or (on is None and here)):
                out.facts.append([event.time, kind, said[:80]])
    at_event += [len(events) - 1] * (len(out.facts) - len(at_event))
    seconds = [instant(e.time) for e in events]
    seconds = [t.timestamp() if t else None for t in seconds]
    for fact, index in zip(out.facts, at_event):
        own = seconds[index]
        before = next((t for t in reversed(seconds[:index]) if t is not None), None)
        after = next((t for t in seconds[index + 1:] if t is not None), None)
        fact += [own, own] if own is not None else [before, after]
    return out


def carries(text: str, rendering: Shown, footer: str) -> bool:
    return bool(text) and (footer in text or rendering.text in text or rendering.question in text
                           or bool(rendering.legacy) and rendering.legacy in text)


def difference(text: str, rendering: Shown) -> str:
    shown = text.replace("\r\n", "\n").splitlines()
    best = None
    for variant in (rendering.text, rendering.question):
        wanted = variant.splitlines()
        start = shown.index(wanted[0]) if wanted and wanted[0] in shown else 0
        got = shown[start:]
        same = next((i for i, (a, b) in enumerate(zip(got, wanted)) if a != b), min(len(got), len(wanted)))
        if best is None or same > best[0]:
            best = (same, wanted)
    same, wanted = best
    if same >= len(wanted):
        return "more text follows it"
    return f'line {same + 1} should be "{wanted[same][:160]}"'


@dataclass
class Status:
    approved: bool = False
    reference: tuple = ()  # (session, turn, presentation) of the approval that holds
    reason: str = ""
    suspended: str = ""
    stopped: bool = False


def instant(stamp: str):
    """A host timestamp as an aware UTC time; None when missing, unparseable or without a zone."""
    import datetime as dt
    try:
        value = dt.datetime.fromisoformat(str(stamp).replace("Z", "+00:00"))
    except ValueError:
        return None
    return value.astimezone(dt.timezone.utc) if value.tzinfo else None


UNORDERED = ("the order of this offer's events across sessions can't be established (a missing timestamp while that "
             "session was still changing, or two sessions at the same instant); present it again and approve it in "
             "this session, after the other session has ended")


def timeline(sessions: dict[str, Facts]) -> list:
    """All facts in one order, as (session, fact) or ("?", [facts]) for a group whose order can't be known. Each
    transcript keeps its own order; across transcripts a fact comes first when it surely ended before the others
    began (its lo..hi interval). Facts of two transcripts whose intervals overlap and that differ in kind form a group:
    the order there is unknown, and fold() treats it as unresolved. A later dated fact still orders after it, so a
    fresh approval in this session, once the other session has ended, resolves it."""
    queues = {stem: [[f[3] if f[3] is not None else float("-inf"),
                      f[4] if f[4] is not None else (found.end if found.end is not None else float("inf")), f]
                     for f in found.facts] for stem, found in sessions.items() if found.facts}
    out = []
    while queues:
        stem = min(queues, key=lambda k: queues[k][0][1])
        lo, hi, fact = queues[stem][0]
        rivals = [k for k in queues if k != stem and queues[k][0][0] <= hi and queues[k][0][2][1] != fact[1]]
        if not rivals:
            out.append((stem, queues[stem].pop(0)[2]))
        else:  # the group grows while any transcript's next fact may still lie inside its window
            group, window, grew = [], hi, True
            while grew:
                grew = False
                for k in queues:
                    while queues[k] and queues[k][0][0] <= window:
                        _, end, taken = queues[k].pop(0)
                        group.append(taken)
                        window, grew = max(window, end), True
            out.append(("?", group))
        for k in [k for k in queues if not queues[k]]:
            del queues[k]
    return out


def fold(sessions: dict[str, Facts]) -> Status:
    """The offer's state after every relevant transcript of the project, the current one included, in order: an
    approval holds until a withdrawal, a narrowing or another answer to the offer; "show the report first" stays owed
    until a message names an existing report, however many sessions and refused approvals come between. A group of
    unordered facts leaves it unapproved, the report owed if one asked for it, and stopped if one stopped."""
    s, owed = Status(), False
    for stem, item in timeline(sessions):
        if stem == "?":
            kinds = {f[1] for f in item}
            owed = owed or "report" in kinds
            s = Status(False, reason=UNORDERED, stopped=s.stopped or "pause" in kinds)
            continue
        kind, detail = item[1], item[2]
        if kind == "report":
            owed, s.approved, s.reason = True, False, "the owner asked to see review.html first"
        elif kind == "shown":
            owed = False
        elif kind == "approve" and owed:
            s.reason = "the owner asked to see review.html first; show the report, then ask again"
        elif kind == "approve":
            s = Status(True, (stem, *detail))
        elif kind == "other":
            s.approved, s.reason = False, detail
        elif kind == "revoke" and s.approved:
            s.approved, s.reason = False, (f"a later owner message withdraws it (\"{detail}\"); present it again for "
                                           "a fresh approval")
        elif kind == "restrict" and s.approved:
            s.suspended = f"a later owner message may narrow it (\"{detail}\"); write the narrowed offer and ask again"
        elif kind in ("pause", "resume"):
            s.stopped = kind == "pause"
    return s


# Offers on disk and their validated approval

def project_offers(root: Path) -> tuple[list[tuple[Path, dict]], list[tuple[str, str]]]:
    """Every offer of the project that loads, and (task, reason) for each offer file that doesn't. A file edited by
    hand approves nothing, but the other offers of its task stay usable."""
    found, broken = [], []
    plans = root / "docs" / "plans"
    for folder in sorted(plans.glob("*")) if plans.is_dir() else []:
        names = [p.name for p in (folder / "offers").glob("*")] if (folder / "offers").is_dir() else []
        ids = sorted(int(m[1]) for m in map(offers().OFFER_FILE.match, names) if m)
        for offer_id in ids:
            try:
                found.append((folder, offers().load(folder, offer_id)))
            except offers().OfferError as exc:
                broken.append((folder.name, f"#{offer_id} ({folder.name}): offers/offer-{offer_id}.json is unusable "
                                            f"({exc}); it approves nothing until the owner puts it back as it was"))
    return found, broken


def session_task(current: list[Event]) -> str | None:
    """The task this session is on: the latest task the owner named or whose offer was presented."""
    return next((e.text for e in reversed(current) if e.kind == "task"), None)


def nearest_first(items: list[tuple], task: str | None) -> list:
    """The values of (task, value) pairs: the session's own task first, then the other tasks newest first (task
    folders start with their date)."""
    items = sorted(items, key=lambda item: item[0], reverse=True)
    return [value for _, value in sorted(items, key=lambda item: item[0] != task)]


def report_check(folder: Path):
    """Whether a message names an existing plan report of this task (docs/plans/<task>/[reviews/]<file>.html)."""
    task = folder.name

    def shown(text: str) -> bool:
        for name in re.findall(rf"docs/plans/{re.escape(task)}/(?:reviews/)?([\w.-]+\.html)\b", text.replace("\\", "/")):
            if (folder / name).is_file() or (folder / "reviews" / name).is_file():
                return True
        return False
    return shown


def other_sessions(folder: Path, offer: dict, rendering: Shown, transcript: Path) -> dict[str, Facts]:
    """This offer through every other main transcript of the project (the host keeps one folder per project) changed
    since the offer was made. Nothing is recorded for this: the transcripts are the history, so a session that
    wrote nothing, or whose hook failed, still counts. Each result is cached by file size and time; any read
    failure raises, and the caller refuses."""
    g = gate()
    made = instant(str(offer.get("created") or ""))
    created = made.timestamp() if made else 0.0  # unknown: every transcript counts
    found = {}
    for path in sorted(transcript.parent.glob("*.jsonl")):
        if path.name == transcript.name:
            continue
        stat = path.stat()
        if stat.st_mtime < created - 60:
            continue  # last changed before the offer existed
        key = g.digest(f"facts-9|{path.resolve()}|{stat.st_size}|{stat.st_mtime_ns}|{rendering.legacy}|{rendering.text}|"
                       f"{rendering.question}".encode("utf-8"))
        cache = g.CACHE_DIR / "offer-history" / f"{key}.json"
        try:
            found[path.stem] = Facts(**json.loads(cache.read_text(encoding="utf-8")))
            continue
        except (OSError, ValueError, TypeError):
            pass
        found[path.stem] = decide(read_events(path, folder.resolve().parents[2]), rendering, offer["id"], report_check(folder), folder.name)
        found[path.stem].end = stat.st_mtime  # no fact in it is later than its last change
        try:
            cache.parent.mkdir(parents=True, exist_ok=True)
            temporary = cache.with_suffix(f".{os.getpid()}.tmp")
            temporary.write_text(json.dumps(found[path.stem].__dict__), encoding="utf-8")
            os.replace(temporary, cache)
        except OSError:
            pass  # only the next call gets slower
    return found


def validated(folder: Path, offer: dict, transcript: Path, current: list[Event]) -> tuple[bool, str]:
    """Whether this offer is approved now, from evidence: every relevant transcript of the project, this one included,
    folded in time order. The stored decision reference is a cache of the approval that holds (for child offers and
    readers); it never approves anything by itself."""
    if offer["state"] in ("superseded", "revoked"):
        return False, f"offer #{offer['id']} is {offer['state']}"
    parent_id = offer["canonical"].get("parent")
    if parent_id is not None:  # C-OFFER-6: a child carries its parent's approval; it never asks the owner again
        try:
            parent = offers().load(folder, parent_id)
        except offers().OfferError as exc:
            return False, f"its parent offer can't be read ({exc})"
        ok, reason = validated(folder, parent, transcript, current)
        if not ok:
            return False, f"its parent offer #{parent_id} is not approved ({reason})"
        if offer["canonical"].get("parent_provenance") != offers().load(folder, parent_id).get("decision"):
            return False, f"it was derived from an earlier approval of offer #{parent_id}, not the current one"
        return True, ""
    rendering = shown(folder, offer)
    try:
        others = other_sessions(folder, offer, rendering, transcript)
    except OSError as exc:
        return False, (f"the project's session history can't be read ({exc}); writes under this offer wait until it "
                       "can, because a withdrawal there could not be seen")
    here = decide(current, rendering, offer["id"], report_check(folder), folder.name, here=True)
    state = fold({**others, transcript.stem: here})  # this session's undated facts are bounded by its last dated one
    if state.suspended:
        return False, state.suspended
    if not state.approved:
        reason = state.reason or here.reason
        stored = offer.get("decision") or {}
        given = [stored.get("turn"), stored.get("presentation")]
        if stored.get("session") and not any(f[1] == "approve" and f[2] == given
                                             for f in ({**others, transcript.stem: here}.get(stored["session"]) or
                                                       Facts()).facts):
            return False, f"its recorded approval doesn't validate in session {stored['session']} ({reason})"
        return False, reason
    if state.stopped:
        return False, "the owner stopped the work in an earlier session and hasn't asked to continue since"
    session, turn, presentation = state.reference
    stored = offer.get("decision") or {}
    if (stored.get("session"), stored.get("turn"), stored.get("presentation")) != (session, turn, presentation):
        try:  # cache the reference of the approval that holds
            if offer["state"] == "draft":
                offers().approve(folder, offer["id"], session, turn, presentation)
            else:
                offers().reapprove(folder, offer["id"], session, turn, presentation)
        except Exception as exc:
            return False, f"its approval can't be recorded ({exc}); retry"
    return True, ""


def paused(current: list[Event]) -> bool:
    """An unresumed stop in this session pauses every write; continuing restores the approvals. Approving a presented
    offer continues as a typed "approve" does: the approve button on the question that carries a validated offer
    presentation (read_events' offer_asked), or a typed `/approve <N>` as the answer to offer N's validated presentation
    (offer_shown, still open: no assistant text and no owner turn since). Any other answer lifts nothing."""
    g, state = gate(), False
    open_ids: set[int] = set()
    asked: dict[str, list[str]] = {}
    for event in current:
        if event.kind == "text":
            open_ids = set()
        elif event.kind == "offer_shown":
            open_ids.add(int(event.text))
        elif event.kind == "offer_asked":
            open_ids = set()
            asked[event.tool_id] = [str(q.get("question", "")) for q in event.questions]
        elif event.kind == "answer":
            open_ids = set()
            values = {RECOMMENDED.sub("", answer_to(event, q).strip().lower())
                      for q in asked.get(event.tool_id, [])}
            state = False if values & APPROVE_BUTTONS else state
        elif event.kind == "user":
            slash = command(event.text)
            typed = SLASH.match(f"/{slash[0]} {slash[1]}") if slash else None
            if typed and typed[1] == "approve" and int(typed[2]) in open_ids:
                state = False
            else:
                intent = g.control_intent(event.text)
                state = True if intent == "pause" else False if intent == "resume" else state
            open_ids = set()
    return state


def covers(offer: dict, rel: str) -> bool:
    return any(offers()._covers(scope, rel) for scope in offer["canonical"]["paths"])


def names_operation(offer: dict, operation: str) -> bool:
    """Exact operation identifiers ("git commit", an MCP tool name), case and spacing ignored; never a substring."""
    wanted = " ".join(operation.lower().split())
    return any(" ".join(op.lower().split()) == wanted for op in offer["canonical"]["operations"])


def rules_open(folder: Path) -> bool:
    """C-RULES-1: the task's checkpoint records an unanswered rules question (`- Rules: NEEDS_SETUP`)."""
    try:
        text = gate().checkpoint((folder / "PLAN.md").read_text(encoding="utf-8", errors="replace"))
    except OSError:
        return False
    return bool(re.search(r"^\s*[-*]\s*Rules\s*:\s*NEEDS_SETUP\b", text, re.M | re.I))


# Styling and the settings switch

STYLE_PATH = re.compile(r"\.(?:css|scss|sass|less|styl|uss)$|\.(?:tokens|theme)\.json$|(?:^|/)(?:tokens|theme|themes)/"
                        r"|(?:^|/)tailwind\.config\.\w+$", re.I)
VISUAL_PROP = re.compile(r"<[A-Za-z][^>]*\s(?:sx|css|color|colour|size|radius|rounded|shadow|spacing|padding|margin|"
                         r"gap|fontSize|background|bg|opacity|variant)\s*=", re.I)
CUSTOM_PROPERTY = re.compile(r"--[\w-]+\s*:|\bThemeProvider\b|\btheme\s*=\s*\{")
CLASS_VALUE = re.compile(r"""\b(?:class|className|:class|ngClass)\s*=\s*\{?\s*["'`]([^"'`]*)["'`]""")
UTILITY = re.compile(r"^(?:[\w-]+:)*-?(?:bg|text|font|p[xytrbl]?|m[xytrbl]?|w|h|min-[wh]|max-[wh]|gap|space-[xy]|"
                     r"rounded|shadow|border|ring|flex|grid|col|row|items|justify|leading|tracking|opacity|z|top|"
                     r"left|right|bottom|inset|translate|scale|rotate|transition|duration|ease|animate|fill|stroke|"
                     r"outline|divide|place|self|order|overflow|cursor|aspect|object|backdrop|blur|drop-shadow)"
                     r"(?:-[\w./\[\]#%()-]+)?$|\[[^\]]+\]")


STYLE_REGIONS = [re.compile(p, re.S | re.I) for p in (
    r"<style\b.*?</style\s*>",
    r"\b(?:styled(?:\.\w+|\([^)]*\))(?:\.attrs\([^)]*\))?|css|keyframes|createGlobalStyle|injectGlobal)\s*`[^`]*`",
    r"\b(?:style|sx|css)\s*=\s*\{\{.*?\}\}",
    r"\bstyle\s*=\s*([\"']).*?\1",
    r"\b(?:StyleSheet\.create|makeStyles|createStyles)\s*\(.*?\n\s*\}\s*\)+",
)]


def styled_lines(text: str) -> set[int]:
    """The numbers of the lines that carry style: a line with a style cue (inline/runtime style, CSS-in-JS, visual
    props, custom properties), and every line of a multi-line style region (a <style> block, a CSS-in-JS template, a
    style object, StyleSheet.create ...). DESIGN.md "What counts as styling"."""
    g = gate()
    cues = g.ui_cues()
    patterns = [cues[c] for c in g.STYLE_CUES if c in cues] + [VISUAL_PROP, CUSTOM_PROPERTY]
    lines = {n for n, line in enumerate(text.splitlines()) if any(p.search(line) for p in patterns)}
    for region in STYLE_REGIONS:
        for found in region.finditer(text):
            first = text.count("\n", 0, found.start())
            lines.update(range(first, first + found.group(0).count("\n") + 1))
    return lines


def proposed_texts(event: dict, path: str) -> tuple[str, str]:
    """The whole file before and after the call: the current file with the edit applied, or the Write's content
    against the current file. Only the fragments when the edit's text isn't in the file (the edit then fails anyway)."""
    data = event.get("tool_input") or {}
    tool = event.get("tool_name")
    try:
        current = Path(path).read_text(encoding="utf-8", errors="replace")
    except FileNotFoundError:
        current = ""
    if tool == "Write":
        return current, str(data.get("content") or "")
    edits = [data] if tool == "Edit" else [e for e in data.get("edits") or [] if isinstance(e, dict)] \
        if tool == "MultiEdit" else None
    if edits is None:
        return gate().edit_texts(event, path)
    new = current
    for edit in edits:
        old_s, new_s = str(edit.get("old_string") or ""), str(edit.get("new_string") or "")
        if not old_s or old_s not in new:
            return gate().edit_texts(event, path)
        new = new.replace(old_s, new_s) if edit.get("replace_all") else new.replace(old_s, new_s, 1)
    return current, new


def changes_style_lines(old: str, new: str) -> bool:
    """Whether a changed, added or removed line is a style line before or after the call."""
    import difflib
    a, b = old.splitlines(), new.splitlines()
    before, after = styled_lines(old), styled_lines(new)
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if tag == "equal":
            continue
        if before & set(range(i1, i2)) or after & set(range(j1, j2)):
            return True
    return False


def new_utility_classes(old: str, new: str, root: Path) -> bool:
    """A class value with utility-framework classes (Tailwind shape) that the file didn't have and the project's
    tracked files don't contain: reusing an existing combination is mirroring, a new one is styling."""
    added = {v.strip() for v in CLASS_VALUE.findall(new)} - {v.strip() for v in CLASS_VALUE.findall(old)}
    for value in added:
        if not any(UTILITY.match(c) for c in value.split()):
            continue
        try:
            found = subprocess.run(["git", "-C", str(root), "grep", "-q", "-F", "-e", value], capture_output=True,
                                     timeout=2)
        except (OSError, subprocess.SubprocessError):
            return True
        if found.returncode != 0:
            return True
    return False


def touches_styling(event: dict, path: str, rel: str, root: Path) -> bool:
    """Any change to style-bearing content: a style, theme or token file's text; a style-bearing line added, changed
    or removed; or a new utility-class combination. A shell write to a style file counts (its content can't be seen)."""
    g = gate()
    if event.get("tool_name") in g.SHELLS:
        return bool(STYLE_PATH.search(rel))
    old, new = proposed_texts(event, path)
    if old == new:
        return False
    if STYLE_PATH.search(rel):
        return True
    return changes_style_lines(old, new) or new_utility_classes(old, new, root)


def settings_answer(current: list[Event], value: str) -> str | None:
    """C-CSS-2: the uuid of the owner's latest answer when it is a Yes to the latest question naming exactly this
    setting and value ("Turn CSS on ..."), asked in visible text (answered by the next typed turn) or as one question
    of a question-tool call (answered by that question's own answer). None otherwise."""
    question = None  # (value it names, question tool id or "", that question's text)
    answer = None  # (value, yes, uuid) of the latest owner answer
    for event in current:
        if event.kind == "text":
            found = SETTINGS_QUESTION.search(event.text)
            question = (found[1].lower(), "", "") if found else None
            answer = None
        elif event.kind == "question":
            hit = next((q for q in event.questions if SETTINGS_QUESTION.search(strings(q))), None)
            question = (SETTINGS_QUESTION.search(strings(hit))[1].lower(), event.tool_id, str(hit.get("question", ""))) \
                if hit else None
            answer = None
        elif event.kind == "answer":
            if question and question[1] and event.tool_id == question[1]:
                value_given = answer_to(event, question[2]).strip().lower()
                answer = (question[0], value_given in YES_WORDS, event.uuid)
            else:
                answer = None
            question = None
        elif event.kind == "user":
            answer = (question[0], words(event.text) in YES_WORDS, event.uuid) if question and not question[1] else None
            question = None
    return answer[2] if answer and answer[:2] == (value, True) else None


def consumed_path(transcript: Path, uuid: str) -> Path:
    g = gate()
    session = g.digest(str(transcript.resolve()).encode("utf-8"))
    return g.CACHE_DIR / "settings-consent" / session / g.digest(uuid.encode("utf-8"))


def settings_problem(event: dict, current: list[Event], transcript: Path, targets: list) -> tuple[str | None, str | None]:
    """The CSS switch is protected: a settings.py set command or any write to the settings file needs one fresh Yes.
    Returns (refusal, the Yes to mark as used once the whole call is allowed)."""
    g = gate()
    data = event.get("tool_input") or {}
    file = settings().settings_path().resolve()
    runs = SETTINGS_RUN.findall(str(data.get("command", ""))) if event.get("tool_name") in g.SHELLS else []
    touched = [t for t in targets if t[0] == "path" and Path(t[1]).resolve() == file]
    if not runs and not touched:
        return None, None
    if len(runs) + len(touched) > 1:
        return ("workflow-axa: one call changes the CSS switch at most once; each change needs its own Yes. Split "
                "the command."), None
    value = runs[0].lower() if runs else _settings_value(data)
    uuid = settings_answer(current, value) if value else None
    if not uuid or consumed_path(transcript, uuid).exists():
        return ("workflow-axa: changing the CSS switch is a protected operation. Ask the owner one question that "
                f"names it, for example \"Turn CSS {value or 'on'} for every project on this machine? Yes / No\", "
                "and change it only after their Yes to that exact question (each Yes allows one change)."), None
    return None, uuid


def use_answer(transcript: Path, uuid: str) -> str | None:
    """Mark a settings Yes as used, atomically: one marker file per answer, created exclusively, so two concurrent
    calls can't both use it. Any failure (taken, unwritable, damaged store) refuses the call; a fresh question and
    Yes is the way on."""
    marker = consumed_path(transcript, uuid)
    try:
        marker.parent.mkdir(parents=True, exist_ok=True)
    except OSError as exc:
        return (f"workflow-axa: the CSS switch change can't be recorded as used ({exc}), so it is refused. Ask the "
                "owner again once the gate cache is writable.")
    try:
        os.close(os.open(marker, os.O_CREAT | os.O_EXCL | os.O_WRONLY))
    except FileExistsError:
        return "workflow-axa: that Yes was already used for a CSS switch change; ask the owner again."
    except OSError as exc:
        return (f"workflow-axa: the CSS switch change can't be recorded as used ({exc}), so it is refused. Ask the "
                "owner again once the gate cache is writable.")
    return None


def _settings_value(data: dict) -> str | None:
    found = re.search(r'"css"\s*:\s*"(on|off)"', str(data.get("content") or data.get("new_string") or ""))
    return found[1] if found else None


# The decision for one tool call

def deny(reason: str) -> int:
    print(json.dumps({"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                             "permissionDecisionReason": reason}}))
    return 0


def problem_for(event: dict) -> str | None:
    g = gate()
    tool = event.get("tool_name") or ""
    transcript = Path(str(event.get("transcript_path") or ""))
    if not event.get("transcript_path"):
        return None  # no transcript: the checker is unavailable (SETUP.md); host permissions still apply
    kept = kept_gate_checks(event)
    if kept:
        return kept
    project = g.Project(str(event.get("cwd") or ""))
    try:
        state = g.scan(transcript, project.cwd)
    except FileNotFoundError:
        return None
    if not state["active"]:
        return None
    install = g.install_problem(event)
    if install:
        return install
    targets = g.targets_of(event)
    command = str((event.get("tool_input") or {}).get("command", ""))
    if targets or SETTINGS_RUN.search(command) or worktree_changes(event, project):
        current = read_events(transcript, Path(project.root or project.cwd))
    else:
        current = []
    parent = derive_problem(targets, transcript, current)
    if parent:
        return parent
    protected, consent = settings_problem(event, current, transcript, targets)
    if protected:
        return protected
    frozen = inventory().folder().resolve()
    for kind, where, label in targets:
        if kind == "path" and (Path(where).resolve() == frozen or frozen in Path(where).resolve().parents):
            return (f"workflow-axa: {label} is the frozen list of pre-offer approvals; only the owner changes it, "
                    "with `legacy_inventory.py --apply` (SETUP.md).")
    if INVENTORY_RUN.search(str((event.get("tool_input") or {}).get("command", ""))):
        return ("workflow-axa: `legacy_inventory.py --apply` writes the frozen list of pre-offer approvals; only the "
                "owner runs it, at the cutover (SETUP.md). Preview it without --apply.")
    for kind, where, label in targets:
        if kind == "path" and re.search(r"(?:^|/)docs/plans/[^/]+/offers(?:/|$)", where.replace("\\", "/")):
            return (f"workflow-axa: {label} is an offer record; offers change only through `record.py offer` "
                    "(create, revise, derive, presentation, revoke).")
    if not consent and legacy_session(state, project):
        return LEGACY  # C-LEG-1: chosen before any offer is looked at, and never as a fallback
    problem = rest_of_call(event, g, project, transcript, current, targets)
    if problem is None and consent:
        problem = use_answer(transcript, consent)  # the Yes is used only when the whole call is allowed
    return problem


def derive_problem(targets: list, transcript: Path, current: list[Event]) -> str | None:
    """`record.py offer derive <task> <parent>` needs the parent's approval on record, but approvals are recorded when
    a write first relies on them (host test R10 of T16). So before the command runs, the parent is validated from the
    conversation, which records it, or the command is refused with the reason. The call comes from the gate's own
    parse of the command; one whose folder or parent this checker can't read is refused."""
    g = gate()
    for kind, where, label in targets:
        call = g.derive_call(label)
        if call is None:
            continue
        if kind != "path" or not call[1].isdigit():
            return (f"workflow-axa: {label}: this checker can't read the task folder or the parent offer number, so "
                    "it can't check the parent's approval. Write both explicitly (`record.py offer derive "
                    "docs/plans/<task> <parent id> <file>`) and retry.")
        folder, parent_id = Path(where), call[1]
        try:
            parent = offers().load(folder, int(parent_id))
        except offers().OfferError as exc:
            return f"workflow-axa: the parent offer can't be read ({exc})."
        ok, reason = validated(folder, parent, transcript, current)
        if not ok:
            return f"workflow-axa: a child offer needs an approved parent; offer #{parent_id} is not ({reason})."
    return None


def kept_gate_checks(event: dict) -> str | None:
    """Checks phase_gate.py made in this hook place that are not about approval, kept unchanged at the cutover (T17):
    the report guides read before render_report.py, the required reads of a phase skill (Skill calls), and canonical
    task records (PLAN, TODO, FINDINGS, DECISIONS) written only through record.py in a workflow session."""
    g = gate()
    transcript = str(event.get("transcript_path") or "")
    reads = g.ReadEvidence(transcript)
    command = str((event.get("tool_input") or {}).get("command", "")) if event.get("tool_name") in g.SHELLS else ""
    if "render_report.py" in command and "--help" not in command:
        try:
            unread = g.unread_report_guides(Path(transcript), reads)
        except g.EvidenceUnavailable:
            return ("workflow-axa: the read-evidence library (hooks/read_evidence.py) is missing or broken, so the "
                    "report guides can't be checked before rendering. Repair the package, then render.")
        except (OSError, ValueError, AttributeError):
            unread = []
        if unread:
            return ("workflow-axa: read these whole before rendering the report, because they set its content and "
                    f"wording: {', '.join(unread)} (under the workflow-axa skills folder). Then render.")
    problem = g.required_read_problem(event, reads)
    if problem:
        return problem
    project = g.Project(str(event.get("cwd") or ""))
    direct = [t for t in g.targets_of(event)
              if event.get("tool_name") in ("Write", "Edit", "MultiEdit") and t[0] == "path" and project.contains(t[1])
              and re.fullmatch(r"docs/plans/[^/]+/(?:PLAN|TODO|FINDINGS|DECISIONS)\.md",
                               g.relative(t[1], project.root_of(t[1])), re.I)]
    if direct:
        try:
            active = g.scan(Path(transcript), project.cwd)["active"]
        except (OSError, ValueError):
            active = True  # can't tell: keep the records protected
        if active:
            return (f'workflow-axa: use python -X utf8 -I "{g.RECORD_TOOL}" for canonical task records (new, append, '
                    "batch, set-line or replace-section), not Write/Edit/MultiEdit.")
    return None


def legacy_session(state: dict, project) -> bool:
    """C-LEG-1: the session is on a task approved before the offer model (in the workspace's frozen inventory, its
    Approval line unchanged, no offers). The task is the one current at the owner's last message."""
    tasks = state.get("tasks") or []
    task = next((name for name, at in reversed(tasks) if at <= state.get("last_user", -1)), None) \
        or (tasks[-1][0] if tasks else None)
    return bool(task) and inventory().is_legacy(Path(project.root or project.cwd), task)


def run_legacy(event: dict) -> int:
    """The repaired legacy checker decides the whole call, in its own process, exactly as before the cutover."""
    done = subprocess.run([sys.executable, "-X", "utf8", "-I", str(HERE / "phase_gate.py"), "--hook-protocol=1"],
                          input=json.dumps(event), capture_output=True, text=True, encoding="utf-8", timeout=20)
    if done.returncode != 0:
        raise RuntimeError(f"the legacy checker exited with {done.returncode}: {done.stderr.strip()[-300:]}")
    sys.stdout.write(done.stdout)
    return 0


def rest_of_call(event: dict, g, project, transcript: Path, current: list[Event], targets: list) -> str | None:
    """Everything after the settings check: bulk deletes, records, the pause, and each target's authority."""
    tool = event.get("tool_name") or ""
    settings_file = settings().settings_path().resolve()
    targets = [t for t in targets if not (t[0] == "path" and Path(t[1]).resolve() == settings_file)]
    bulk = g.bulk_delete(event, targets, project)
    if bulk:
        return bulk
    redirected = git_elsewhere(event)
    if redirected:
        return redirected
    targets = targets + worktree_changes(event, project)
    elsewhere = another_worktree(event, targets, project, g)
    if elsewhere:
        return elsewhere
    targets = [t for t in targets if t[0] != "path" or (project.contains(t[1]) and not project.is_record(t[1]))]
    if not targets:
        return None
    if paused(current):
        return ("workflow-axa: the owner stopped the work in this session; no write starts until they ask to "
                "continue. Task records stay writable for the handoff.")
    root = Path(project.root or project.cwd)
    found, broken = project_offers(root)
    usable, why, unusable = [], list(broken), []
    for folder, offer in sorted(found, key=lambda pair: -pair[1]["id"]):
        ok, reason = validated(folder, offer, transcript, current)
        if ok:
            usable.append((folder.name, offer))
        else:
            if offer["state"] not in ("superseded", "revoked"):
                why.append((folder.name, f"#{offer['id']} ({offer['task']}): {reason}"))
            unusable.append((folder.name, (offer, reason)))
    task = session_task(current)
    usable, why, unusable = nearest_first(usable, task), nearest_first(why, task), nearest_first(unusable, task)
    for kind, where, label in targets:
        if kind == "refused":
            return label
        if kind == "ambiguous":
            return (f"workflow-axa: {label} is relative to a folder set by a shell variable this checker can't "
                    "resolve. Use an explicit path and retry.")
        if kind == "path":
            rel = g.relative(where, project.root_of(where))
            authority = [o for o in usable if covers(o, rel)]
            if not authority:
                return no_offer(label, rel, why, usable, bool(found))
            if not settings().css_allowed(Path(project.root_of(where))) \
                    and touches_styling(event, where, rel, Path(project.root_of(where))):
                return (f"workflow-axa: {label} changes styling, and CSS is off here (the machine switch in "
                        f"{settings_file} is off, or this project's DESIGN.md says css: never). Reuse an existing "
                        "class, or ask the owner which element to mimic (DESIGN.md).")
        elif kind == "git":
            if label.endswith(g.GIT_FILE_WRITE):
                continue  # the files it writes are path targets of their own, checked here too
            sub = re.search(r"git\s+([\w-]+)", label)
            name = f"git {sub[1]}" if sub else "git"
            authority = [o for o in usable if names_operation(o, name)]
            if not authority:
                return (f"workflow-axa: {label} is a protected operation; no approved offer lists \"{name}\" among its "
                        "operations." + operation_help(name, unusable))
        else:
            name = str(tool)
            authority = [o for o in usable if names_operation(o, name)]
            if not authority:
                return (f"workflow-axa: {label} has no approved offer that lists {name} among its operations."
                        + operation_help(name, unusable))
        waiting = [o for o in authority if rules_open(root / "docs" / "plans" / o["task"])]
        if waiting:
            return (f"workflow-axa: {label} waits for the rules question of task {waiting[0]['task']} (its checkpoint "
                    "says Rules: NEEDS_SETUP). Read-only work continues; ask the owner to set up rules now or skip "
                    "them for this task, and record the answer.")
    return None


SHELL_TOOLS = ("Bash", "PowerShell")
GIT_REDIRECT = re.compile(r'(?:^|[\s;&|(])(?:--git-dir|--work-tree)\b'
                          r'|\bGIT_(?:DIR|WORK_TREE|COMMON_DIR|INDEX_FILE|OBJECT_DIRECTORY|ALTERNATE_OBJECT_DIRECTORIES'
                          r'|NAMESPACE|CONFIG\w*)\s*=|-c\s*core\.(?:worktree|bare)\b', re.I)
RUN_TIME = r'(?:\$|%\w+%|`)'
RUN_TIME_REDIRECT = re.compile(r'>\s*\S*' + RUN_TIME)
WRAPPERS = re.compile(r'^(?:sudo|command|exec|env|nohup|time|builtin)$|^\w+=\S*$', re.I)
EVERY_ARGUMENT = {"rm", "rmdir", "truncate", "tee", "touch", "dd", "shred", "unlink", "chmod", "chown", "new-item",
                  "remove-item", "clear-content", "rename-item", "del", "erase", "rd", "mkdir", "md"}
LAST_ARGUMENT = {"cp", "mv", "install", "rsync", "ln", "mklink", "copy-item", "move-item", "copy", "move", "xcopy",
                 "robocopy"}
FIRST_ARGUMENT = {"set-content", "add-content", "out-file"}
FOLDER_ARGUMENT = {"cd", "pushd", "set-location", "push-location", "sl"}
WRITE_PROGRAMS = EVERY_ARGUMENT | LAST_ARGUMENT | FIRST_ARGUMENT | {"sed", "git", "bash", "sh", "pwsh", "powershell",
                                                                    "python", "python3", "py", "node", "perl", "ruby"}
VALUE_OPTIONS = {"sed": {"-e", "-f", "--expression", "--file"}, "truncate": {"-s", "--size", "-r", "--reference"}, "touch": {"-d", "-t", "-r", "--date", "--reference"},
                 "mkdir": {"-m", "--mode"}, "md": {"-m"}, "install": {"-m", "-o", "-g", "--mode", "--owner", "--group"}}
FIRST_IS_NOT_A_FILE = {"chmod", "chown"}
GIT_READS = {"status", "log", "diff", "show", "blame", "grep", "rev-parse", "ls-files", "ls-tree", "cat-file", "describe",
             "shortlog", "rev-list", "for-each-ref", "name-rev", "merge-base", "help", "version"}
INDIRECT_WRITE = re.compile(
    r'\b(?:bash|sh|zsh|dash|pwsh|powershell)(?:\.exe)?\s+(?:-\w+\s+)*[^\s;&|-]\S*\.(?:sh|ps1)\b'
    r'|(?:^|[;&|]\s*)(?:source\s+|\.\s+|&\s*)\S+\.(?:sh|ps1)\b'
    r'|\b(?:python3?|py|node|ruby|perl)(?:\.exe)?\b[^;&|\n]*\s-(?:c|e)\s[^\n]*'
    r'(?:\.write\(|write_text|write_bytes|writeFile|appendFile|open\([^)]*[\'"][wax+]|unlink|remove\(|rmdir|rename\(|'
    r'replace\(|shutil\.|rmSync|copyFile|truncate\(|File\.write|IO\.write)', re.I)


def shell_words(segment: str) -> list[str]:
    """The segment's words as a shell splits them: quoted spaces stay inside one word, quotes are removed, and
    backslashes stay (Windows paths). Unbalanced quotes fall back to splitting on spaces."""
    lexer = shlex.shlex(segment, posix=True, punctuation_chars=False)
    lexer.whitespace_split, lexer.escape = True, ""
    try:
        return list(lexer)
    except ValueError:
        return [re.sub(r'[\'"]', '', w) for w in segment.split()]


def program_and_arguments(segment: str) -> tuple[str, list[str]]:
    """The program a command segment runs and its arguments, quotes removed. Wrappers such as `command`, `env` or
    `sudo` and their options are skipped, and a full program path counts as its name."""
    words = shell_words(segment)
    while words and WRAPPERS.match(words[0]):
        words = words[1:]
        while words and words[0].startswith("-"):
            words = words[1:]
    if not words:
        return "", []
    return re.sub(r'\.exe$', '', words[0].replace("\\", "/").rsplit("/", 1)[-1].lower()), words[1:]


def operands(program: str, args: list[str]) -> list[str]:
    """The arguments that name files, with option values left out."""
    values = VALUE_OPTIONS.get(program, set())
    found, skip = [], False
    for arg in args:
        if skip:
            skip = False
        elif arg in values:
            skip = True
        elif not arg.startswith("-"):
            found.append(arg)
    return found[1:] if program in FIRST_IS_NOT_A_FILE else found


def sed_files(args: list[str]) -> list[str]:
    """sed's file operands: with -e or -f every operand is a file, else the first operand is the script."""
    found = operands("sed", args)
    scripted = any(re.match(r'^-[a-zA-Z]*[ef]$', a) or a.startswith(("--expression", "--file")) for a in args)
    return found if scripted else found[1:]


def git_subcommand(args: list[str]) -> str:
    skip = False
    for arg in args:
        if skip:
            skip = False
        elif arg in ("-C", "-c"):
            skip = True
        elif not arg.startswith("-"):
            return arg.lower()
    return ""


def git_folder_at_run_time(args: list[str]) -> bool:
    """git -C <folder> with a folder known only at run time, running a subcommand that may write."""
    folder = any(a == "-C" and i + 1 < len(args) and re.search(RUN_TIME, args[i + 1]) for i, a in enumerate(args))
    return bool(folder) and git_subcommand(args) not in GIT_READS


def cannot_place(command: str) -> bool:
    """A write the checker can't place: its destination is known only at run time, or another program performs it."""
    if RUN_TIME_REDIRECT.search(command) or INDIRECT_WRITE.search(command):
        return True
    segments = [program_and_arguments(s) for s in re.split(r'[;&|\n]+', command)]
    writes_later = False
    for program, args in reversed(segments):
        plain = [a for a in args if not a.startswith("-")]
        run_time = [bool(re.search(RUN_TIME, a)) for a in plain]
        files = operands(program, args)
        if program in EVERY_ARGUMENT and any(re.search(RUN_TIME, a) for a in files):
            return True
        if program == "sed" and any(re.match(r'^-[a-zA-Z]*i', a) or a.startswith("--in-place") for a in args) \
                and any(re.search(RUN_TIME, a) for a in sed_files(args)):
            return True
        if program in LAST_ARGUMENT and run_time and run_time[-1]:
            return True
        if program in FIRST_ARGUMENT:
            named = [args[i + 1] for i, a in enumerate(args[:-1]) if a.lower() in ("-path", "-literalpath", "-filepath")]
            named += [a.split(":", 1)[1] for a in args if re.match(r'^-(?:path|literalpath|filepath):', a, re.I)]
            if any(re.search(RUN_TIME, a) for a in (named or plain[:1])):
                return True
        if program == "git" and git_folder_at_run_time(args):
            return True
        if program in FOLDER_ARGUMENT and any(run_time) and writes_later:
            return True
        if program == "xargs" and plain and program_and_arguments(" ".join(plain))[0] in WRITE_PROGRAMS:
            return True
        if program == "find" and re.search(r'-(?:delete)\b', " ".join(args)):
            return True
        if program == "find":
            for i, a in enumerate(args):
                if a in ("-exec", "-execdir", "-ok") and i + 1 < len(args) and \
                        program_and_arguments(args[i + 1])[0] in WRITE_PROGRAMS:
                    return True
        reads_only = program == "git" and git_subcommand(args) in GIT_READS
        writes_later = writes_later or (program in WRITE_PROGRAMS and not reads_only)
    return False
WORKTREE_CHANGE = re.compile(r'\bgit\b[^;&|\n]*?\bworktree\s+(add|move|remove|prune|repair|lock|unlock)\b', re.I)
MAKES_LINK = re.compile(r'\bmklink\b|\bln\b|-ItemType\s+(?:Junction|SymbolicLink|HardLink)\b', re.I)
PATH_WORD = re.compile(r'''[^\s'"`;&|<>()=]+''')


def shell_command(event: dict) -> str:
    if (event.get("tool_name") or "") not in SHELL_TOOLS:
        return ""
    return str((event.get("tool_input") or {}).get("command") or "")


def unquoted(command: str) -> str:
    """The command with quote and escape characters removed, so `git "--git-dir=x"` reads as `git --git-dir=x`."""
    return re.sub(r'[\'"`^\\]', '', command)


def plain_path(path: str) -> str:
    """The same folder without the Windows extended-length prefix (\\\\?\\ or //?/), so both spellings compare equal."""
    text = path.replace("\\", "/")
    if text[:8].upper() == "//?/UNC/":
        return "//" + text[8:]
    return text[4:] if text.startswith("//?/") else text


def real_path(g, path: str) -> str:
    try:
        return plain_path(g.slash(os.path.realpath(plain_path(path))))
    except (OSError, ValueError):
        return plain_path(path)


def repository_worktrees(common: str) -> list[str]:
    """Every worktree of the repository: the main one beside the shared git folder, and each linked one it lists."""
    shared = Path(plain_path(common))
    found = [str(shared.parent)] if shared.name.lower() == ".git" else []
    listed = shared / "worktrees"
    for entry in (listed.iterdir() if listed.is_dir() else []):
        try:
            found.append(str(Path((entry / "gitdir").read_text(encoding="utf-8").strip()).parent))
        except OSError:
            continue
    return found


def wildcard_reaches(g, path: str, own_tree: str, common: str) -> str | None:
    """For a path with wildcards (or braces), another worktree inside its fixed part, or holding it."""
    parts = path.replace("\\", "/").split("/")
    wild = [i for i, part in enumerate(parts) if any(c in part for c in "*?[{")]
    if not wild:
        return None
    prefix = "/".join(parts[:wild[0]]) or "/"
    for fixed in {g.key(plain_path(prefix)), g.key(real_path(g, prefix))}:
        for tree in repository_worktrees(common):
            other = g.key(real_path(g, tree))
            if other != g.key(own_tree) and (other == fixed or other.startswith(fixed.rstrip("/") + "/")
                                             or fixed.startswith(other + "/")):
                return tree
    return None


def expanded(path: str) -> list[str]:
    """A path with wildcards, as every folder it can reach: the part up to the last wildcard folder is matched, the
    rest kept, so a file that doesn't exist yet is still placed."""
    parts = path.replace("\\", "/").split("/")
    wild = [i for i, part in enumerate(parts) if any(c in part for c in "*?[")]
    if not wild:
        return [path]
    head, tail = "/".join(parts[:wild[-1] + 1]), parts[wild[-1] + 1:]
    found = [m.replace("\\", "/") + "".join("/" + p for p in tail) for m in glob.glob(head)]
    return found + [path]


def same_common(g, one: str | None, other: str | None) -> bool:
    return bool(one and other) and g.key(plain_path(one)) == g.key(plain_path(other))


def other_worktrees_exist(own_tree: str, common: str) -> bool:
    """Linked worktrees are listed under the shared git folder; a linked session always has the main one beside it."""
    shared = Path(plain_path(common))
    listed = shared / "worktrees"
    return (listed.is_dir() and any(listed.iterdir())) or Path(own_tree, ".git").is_file()


def git_elsewhere(event: dict) -> str | None:
    """Git options that move the repository or work tree away from the folder the checker reads are refused (F4)."""
    command = unquoted(shell_command(event))
    if not re.search(r'\bgit\b', command, re.I) or not GIT_REDIRECT.search(command):
        return None
    return ("workflow-axa: this git command sets --git-dir, --work-tree or GIT_DIR/GIT_WORK_TREE, so the checker can't "
            "tell which checkout it changes. Use `git -C <folder>` (or run it from that folder) and retry.")


def worktree_changes(event: dict, project) -> list:
    """Adding, moving or removing worktrees changes which checkouts exist: a protected operation of its own."""
    found = WORKTREE_CHANGE.search(unquoted(shell_command(event)))
    return [("git", project.root or project.cwd, f"`git worktree {found[1].lower()}`")] if found else []


def another_worktree(event: dict, targets: list, project, g) -> str | None:
    """Offers are read from the session's worktree, so they authorise writes only there (F4). Every place is judged
    where it really lands (links resolved, the session's own folder too), and a shell command that writes is also
    judged by every path it names, since the checker can't follow every way a shell reaches a file. Records and output
    of another worktree stay writable when reached directly. Only worktrees of the session's own repository count."""
    if not project.root:
        return None
    own_root = real_path(g, project.root)
    own_tree = g.worktree(own_root) or own_root
    common = g.common_dir(own_tree)
    if not common:
        return None
    command = shell_command(event)
    if command and cannot_place(command) and other_worktrees_exist(own_tree, common):
        return ("workflow-axa: this command writes to a place known only while it runs (a variable, command output, "
                "xargs, find -exec, a script it runs or an inline program), so the checker can't tell which worktree "
                "it changes; this repository has more than one. Write each destination as an explicit path in a plain "
                "command and retry.")
    places = [(where, label, kind == "path") for kind, where, label in targets
              if kind in ("path", "git") and g.is_absolute(plain_path(where))]
    only_records = all(kind == "path" and project.is_record(where) for kind, where, _ in targets)
    if command and targets and (MAKES_LINK.search(command) or not only_records):
        cwd = str(event.get("cwd") or project.cwd)
        for word in PATH_WORD.findall(command):
            word = re.sub(r'^-[\w-]+:', '', word)
            if ('/' in word or '\\' in word) and '$' not in word:
                places.append((word if g.is_absolute(word) else g.absolute(word, cwd), f"`{word}` in this command",
                               False))
    for where, label, _ in places:
        tree = wildcard_reaches(g, where, own_tree, common)
        if tree:
            return (f"workflow-axa: {label} uses a wildcard that can reach another worktree ({tree}) than this "
                    f"session's ({project.root}); an approval given here doesn't cover it. Name the files explicitly, "
                    "or start the session in that worktree and retry.")
    places = [(each, label, may_be_record) for where, label, may_be_record in places for each in expanded(where)]
    for where, label, may_be_record in places:
        real = real_path(g, where)
        if may_be_record and g.key(real) == g.key(plain_path(where)) and project.is_record(where):
            continue
        tree = g.worktree(real)
        if tree and g.key(tree) != g.key(own_tree) and same_common(g, g.common_dir(tree), common):
            return (f"workflow-axa: {label} is in another worktree ({tree}) than this session's "
                    f"({project.root}); an approval given here doesn't cover it. To work there, start the session "
                    "in that worktree (or move into it, as EnterWorktree does), present its offer there and retry.")
    return None


def operation_help(name: str, unusable: list[tuple[dict, str]]) -> str:
    listing = [(offer, reason) for offer, reason in unusable if names_operation(offer, name)
               and offer.get("state") not in ("superseded", "revoked")]
    if listing:
        offer, reason = max(listing, key=lambda pair: (pair[0]["task"] == listing[0][0]["task"], pair[0]["id"]))
        task, number = f"docs/plans/{offer['task']}", offer["id"]
        first = f" Offer #{number} ({offer['task']}) lists it but is not approved: {reason}. Present it again:"
    else:
        task, number = "<task-folder>", "<id>"
        first = (" Add it to an offer (`record.py offer create`, or `record.py offer revise` for an existing one) and "
                 "present that offer:")
    return (f"{first} with the question tool (buttons), the output of `record.py offer present {task} {number} "
            f"--question` unchanged as the question's own text; or, only without a question tool, the exact "
            f"`record.py offer present {task} {number}` text as the end of your reply. A question in your own words, "
            "or the offer sent through a message tool, approves nothing.")


def no_offer(label: str, rel: str, why: list[str], usable: list[dict], any_offer: bool) -> str:
    """Live offers that failed to validate come first, newest first, because their reasons explain the refusal; then
    approved offers that cover other files. Superseded and revoked offers are left out."""
    parts = why[:3] + [f"approved #{o['id']} ({o['task']}) lists {', '.join(o['canonical']['paths']) or 'no paths'}"
                       for o in usable[:3]]
    if parts:
        first = f" Offers here: {'; '.join(parts)}. Present the offer that should cover it (`record.py offer present`),"
    elif any_offer:
        first = (" This project has no current offer (every offer is superseded or revoked). Create one through "
                 "`workflow-specify` step 5 (`record.py offer create`), present it (`record.py offer present`, as the "
                 "end of your reply),")
    else:
        first = (" This project has no offers yet. Create one through `workflow-specify` step 5 (`record.py offer "
                 "create`), present it (`record.py offer present`, as the end of your reply),")
    return (f"workflow-axa: {label} needs an approved offer that lists {rel}.{first} ask the one question (Show "
            "review.html first · Approve from this summary · Change something; a lightweight offer's is Approve · "
            "Change something), and retry after the owner's answer. "
            "An offer in your own words can't be approved. Task records stay writable.")


def is_write_tool(event: dict) -> bool:
    tool = str(event.get("tool_name") or "")
    if tool in WRITE_TOOLS:
        return True
    try:
        return tool.startswith("mcp__") and bool(gate().MCP_WRITE.search(tool.rsplit("__", 1)[-1]))
    except Exception:
        return tool.startswith("mcp__")  # can't tell: treat as a write


def main() -> int:
    try:
        event = json.load(sys.stdin)
    except ValueError:
        return 0
    if not isinstance(event, dict):
        return 0
    if event.get("hook_event_name", "PreToolUse") != "PreToolUse":
        return 0
    try:
        problem = problem_for(event)
        if problem is LEGACY:
            return run_legacy(event)
    except Exception as error:  # fail closed for every recognised write, with a diagnosis
        if is_write_tool(event):
            return deny(f"workflow-axa: the offer checker failed ({type(error).__name__}: {error}), so writes pause. "
                        "Reading stays available; an approval that still validates is not asked again once it works.")
        return 0
    return deny(problem) if problem else 0


if __name__ == "__main__":
    sys.exit(main())
