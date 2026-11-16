"""The offer checker: PreToolUse hook of the redesign (REDESIGN.md §3.4, §3.6, §7; contracts C-OFFER-2..7, C-CSS-1/2,
C-RULES-1, C-SAFE-1). It replaces the approval forensics of phase_gate.py at the cutover (T17).

A project write is allowed when an **approved offer** (skills/workflow/scripts/offers.py) covers it. Approval is
proven from the host transcript, never from a stored flag:

- **Presentation** of offer #N is its canonical rendering (`record.py offer present`) byte for byte: it names the
  offer, its hash, its task and its workspace, so identical offers in two tasks or checkouts never share consent. It
  counts in visible assistant text, or in one question of a question-tool call; then only that question's answer
  counts. An edited or stale block is no presentation. The display-only CSS line is outside the rendering.
- **The answer** is the first real owner turn after the latest presentation: the question's "Approve from this
  summary" (or "Approve"), `/approve <N>`, or a whole message that is one of: approve, approved, yes, ok, okay, go,
  ja, akkoord, doe maar. "Show review.html first" or `/report <N>` approves nothing yet: the next approval counts only
  after a message names the task's existing report, in a later session too. Anything else, a qualified "yes but ..."
  included, approves nothing: the agent writes a narrowed offer.
- **After approval:** a later owner message that withdraws it ("revoke", "not approved") ends it; one that may narrow
  it (but, except, only, without ...) suspends it until a narrowed offer is approved; a stop pauses all writes until
  the owner asks to continue, and the approval then holds again.
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

import importlib.util
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

HERE = Path(__file__).resolve().parent
SCRIPTS = HERE.parent / "skills" / "workflow" / "scripts"
APPROVE_WORDS = {"approve", "approved", "yes", "ok", "okay", "go", "ja", "akkoord", "doe maar"}
YES_WORDS = {"yes", "ja", "y", "ok", "okay"}
APPROVE_BUTTONS = {"approve from this summary", "approve"}
REPORT_BUTTONS = {"show review.html first", "show review.html before i decide"}
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


OFFER_TASK = re.compile(r"--- workflow-axa offer #\d+ \([0-9a-f]+\) · task (\S+) · ")


def read_events(path: Path) -> list[Event]:
    """The events of a main transcript. Task transitions are the owner naming a task and a presentation of one of the
    task's offers (in visible text or a question). The agent's own record writes never move the session (REDESIGN
    §3.4, N4): bookkeeping must not decide which offer a later withdrawal, narrowing, stop or resume applies to."""
    g = gate()
    events: list[Event] = []
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        try:
            entry = json.loads(line)
        except ValueError:
            continue
        if not isinstance(entry, dict) or entry.get("isSidechain"):
            continue
        uuid = str(entry.get("uuid") or f"line{len(events)}")
        time = str(entry.get("timestamp") or "")
        content = (entry.get("message") or {}).get("content")
        typed = g.queued_text(entry) if entry.get("type") == "attachment" else g.user_text(entry)
        if typed is not None:
            for a, b in g.TASK_NAMED.findall(g.slash(typed)):
                events.append(Event("task", uuid, a or b, time=time))
            events.append(Event("user", uuid, typed, time=time))
            continue
        result = entry.get("toolUseResult")
        if entry.get("type") == "user" and isinstance(result, dict) and isinstance(result.get("answers"), dict) \
                and isinstance(content, list) and not entry.get("isMeta"):
            for block in content:
                if isinstance(block, dict) and block.get("type") == "tool_result" and not block.get("is_error"):
                    events.append(Event("answer", uuid, tool_id=str(block.get("tool_use_id")), answers=result["answers"], time=time))
            continue
        if entry.get("type") == "assistant" and isinstance(content, list):
            visible = "\n".join(str(b.get("text", "")) for b in content if isinstance(b, dict) and b.get("type") == "text")
            for task in OFFER_TASK.findall(visible):
                events.append(Event("task", uuid, task, time=time))
            if visible.strip():
                events.append(Event("text", uuid, visible, time=time))
            for block in content:
                if isinstance(block, dict) and block.get("type") == "tool_use" and block.get("name") == "AskUserQuestion":
                    data = block.get("input") or {}
                    questions = [q for q in data.get("questions", []) if isinstance(q, dict)] if isinstance(data, dict) else []
                    for task in OFFER_TASK.findall(strings(questions)):
                        events.append(Event("task", uuid, task, time=time))
                    events.append(Event("question", uuid, tool_id=str(block.get("id")), questions=questions, time=time))
    return events


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


def decide(events: list[Event], rendering: str, offer_id: int, report_shown, task: str, here: bool = False) -> Facts:
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
    for index, event in enumerate(events):
        if len(at_event) < len(out.facts):
            at_event += [index - 1] * (len(out.facts) - len(at_event))
        if event.kind == "task":
            on = event.text
        elif event.kind == "text":
            if rendering in event.text:
                presented, last_presented = event.uuid, offer_id
                out.reason = "it was presented, but no owner answer came after it yet"
            elif "--- workflow-axa offer #" in event.text:
                last_presented = None
            if report_shown(event.text):
                out.facts.append([event.time, "shown", ""])
        elif event.kind == "question":
            carrier = next((q.get("question", "") for q in event.questions if rendering in strings(q)), None)
            if carrier is not None:
                asked[event.tool_id] = (event.uuid, str(carrier))
                presented, last_presented = None, None
                out.reason = "it was asked, but the question has no answer yet"
        elif event.kind == "answer" and event.tool_id in asked:
            at, question = asked.pop(event.tool_id)
            value = str(event.answers.get(question, "")).strip().lower()
            kind = "approve" if value in APPROVE_BUTTONS else "report" if value in REPORT_BUTTONS else "other"
            out.facts.append([event.time, kind, [event.uuid, at] if kind == "approve" else
                              f"the answer \"{value[:60]}\" to its question is not an approval; write a narrowed offer"])
        elif event.kind == "user":
            said, slash = words(event.text), command(event.text)
            if slash and slash[0] == "wait-what":
                presented = None
                continue
            if presented is not None and last_presented == offer_id:
                typed = SLASH.match(f"/{slash[0]} {slash[1]}") if slash else None
                if (typed and typed[1] == "approve" and int(typed[2]) == offer_id) or said in APPROVE_WORDS:
                    out.facts.append([event.time, "approve", [event.uuid, presented]])
                elif (typed and typed[1] == "report" and int(typed[2]) == offer_id) or said in REPORT_BUTTONS:
                    out.facts.append([event.time, "report", ""])
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

def project_offers(root: Path) -> list[tuple[Path, dict]]:
    found = []
    for folder in sorted((root / "docs" / "plans").glob("*")) if (root / "docs" / "plans").is_dir() else []:
        if (folder / "offers").is_dir():
            try:
                found += [(folder, offer) for offer in offers().all_offers(folder)]
            except offers().OfferError:
                continue  # a hand-edited offer is simply not usable
    return found


def report_check(folder: Path):
    """Whether a message names an existing plan report of this task (docs/plans/<task>/[reviews/]<file>.html)."""
    task = folder.name

    def shown(text: str) -> bool:
        for name in re.findall(rf"docs/plans/{re.escape(task)}/(?:reviews/)?([\w.-]+\.html)\b", text.replace("\\", "/")):
            if (folder / name).is_file() or (folder / "reviews" / name).is_file():
                return True
        return False
    return shown


def other_sessions(folder: Path, offer: dict, rendering: str, transcript: Path) -> dict[str, Facts]:
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
        key = g.digest(f"facts-3|{path.resolve()}|{stat.st_size}|{stat.st_mtime_ns}|{rendering}".encode("utf-8"))
        cache = g.CACHE_DIR / "offer-history" / f"{key}.json"
        try:
            found[path.stem] = Facts(**json.loads(cache.read_text(encoding="utf-8")))
            continue
        except (OSError, ValueError, TypeError):
            pass
        found[path.stem] = decide(read_events(path), rendering, offer["id"], report_check(folder), folder.name)
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
    rendering = offers().rendering(offer, folder)
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
    """An unresumed stop in this session pauses every write; continuing restores the approvals."""
    g, state = gate(), False
    for event in current:
        if event.kind == "user":
            intent = g.control_intent(event.text)
            state = True if intent == "pause" else False if intent == "resume" else state
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
                value_given = str(event.answers.get(question[2], "")).strip().lower()
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
    current = read_events(transcript)
    targets = offer_command_targets(event, g.targets_of(event))
    parent = derive_problem(event, project, transcript, current)
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


OFFER_COMMAND = re.compile(r"record\.py[\"']?\s+offer\s+([\w-]+)\b")


def offer_command_targets(event: dict, targets: list) -> list:
    """`record.py offer <verb> <task-folder> ...` writes only that task's offers/ (offers.py checks it); the gate's
    record.py parser reads the verb as the file written (host test R2 of T16), so that target is dropped."""
    verbs = set(OFFER_COMMAND.findall(str((event.get("tool_input") or {}).get("command", ""))))
    return [t for t in targets if not (t[0] == "path" and t[2].startswith("`record.py` writing ")
                                        and Path(t[1]).name in verbs)]


DERIVE = re.compile(r"record\.py[\"']?\s+offer\s+derive\s+(\"[^\"]+\"|'[^']+'|\S+)\s+#?(\d+)")


def derive_problem(event: dict, project, transcript: Path, current: list[Event]) -> str | None:
    """`record.py offer derive <task> <parent>` needs the parent's approval on record, but approvals are recorded when
    a write first relies on them (host test R10 of T16). So before the command runs, the parent is validated from the
    conversation, which records it, or the command is refused with the reason."""
    for folder_text, parent_id in DERIVE.findall(str((event.get("tool_input") or {}).get("command", ""))):
        folder = Path(folder_text.strip("\"'"))
        folder = folder if folder.is_absolute() else Path(project.cwd) / folder
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
    targets = [t for t in targets if t[0] != "path" or (project.contains(t[1]) and not project.is_record(t[1]))]
    if not targets:
        return None
    if paused(current):
        return ("workflow-axa: the owner stopped the work in this session; no write starts until they ask to "
                "continue. Task records stay writable for the handoff.")
    root = Path(project.root or project.cwd)
    usable, why = [], []
    for folder, offer in project_offers(root):
        ok, reason = validated(folder, offer, transcript, current)
        if ok:
            usable.append(offer)
        else:
            why.append(f"#{offer['id']} ({offer['task']}): {reason}")
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
                return no_offer(label, rel, why, usable)
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
                        "operations. Add it to the offer and ask the owner, or ask them for this one step.")
        else:
            name = str(tool)
            authority = [o for o in usable if names_operation(o, name)]
            if not authority:
                return f"workflow-axa: {label} has no approved offer that lists {name} among its operations."
        waiting = [o for o in authority if rules_open(root / "docs" / "plans" / o["task"])]
        if waiting:
            return (f"workflow-axa: {label} waits for the rules question of task {waiting[0]['task']} (its checkpoint "
                    "says Rules: NEEDS_SETUP). Read-only work continues; ask the owner to set up rules now or skip "
                    "them for this task, and record the answer.")
    return None


def no_offer(label: str, rel: str, why: list[str], usable: list[dict]) -> str:
    parts = [f"approved #{o['id']} ({o['task']}) lists {', '.join(o['canonical']['paths']) or 'no paths'}"
             for o in usable[:3]]
    parts += why[:3]
    if parts:
        first = f" Offers here: {'; '.join(parts)}. Present the offer that should cover it (`record.py offer present`),"
    else:
        first = (" This project has no offers yet. Create one through `workflow-specify` step 5 (`record.py offer "
                 "create`), present its block (`record.py offer present`),")
    return (f"workflow-axa: {label} needs an approved offer that lists {rel}.{first} ask the one question (Show "
            "review.html first · Approve from this summary · Change something), and retry after the owner's answer. "
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
