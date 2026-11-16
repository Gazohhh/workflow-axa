"""Offers: the one approval record of the redesign (REDESIGN.md §3.4, contracts C-OFFER-1, -6). Run as `record.py offer`.

An offer is what the agent proposes to change, under an id that never changes. Its **canonical fields** authorise:
behaviour, paths, operations, delegable paths and operations (what a child may receive), exclusions, conditions,
required checks, and, for a child, its parent offer and the parent's approval provenance. Changing any canonical field
means a new offer that supersedes the old one; the display text can change freely.

Stored as `<task folder>/offers/offer-<id>.json`. `state` is a cache, never proof: `draft` (written; it becomes
pending only when the hook sees a verified presentation), `approved` (with its decision reference, which the hook
re-validates against the transcript whenever it relies on it), `superseded` or `revoked`.

usage (via record.py):
  record.py offer create    <task-folder> <offer.json | ->     new draft offer; prints its id and hash
  record.py offer revise    <task-folder> <id> <offer.json | -> new offer replacing <id>, which becomes superseded
  record.py offer derive    <task-folder> <parent-id> <child.json | ->   child offer, checked against the parent
  record.py offer present   <task-folder> <id> [--root PROJECT] [--question]   print the presentation to show the owner
  record.py offer presentation <task-folder> <id> asked|html-first|chat   the owner's choice of the one question
  record.py offer approve   <task-folder> <id> --session S --turn T --presentation P   record the decision reference
  record.py offer revoke    <task-folder> <id>
  record.py offer show      <task-folder> <id>
  record.py offer list      <task-folder>
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import importlib.util
import json
import pathlib
import re
import sys
import unicodedata

LISTS = ("paths", "operations", "delegable_paths", "delegable_operations", "exclusions", "conditions", "checks")
CANONICAL = ("behaviour",) + LISTS + ("parent", "parent_provenance")
STATES = ("draft", "approved", "superseded", "revoked")
DECISIONS = ("asked", "html-first", "chat")
OFFER_FILE = re.compile(r"^offer-(\d+)\.json$")


class OfferError(ValueError):
    """A refusal; nothing was written."""


def _record():
    """record.py next to this file: its lock and atomic write keep offers as safe as the other records."""
    name = "workflow_axa_record"
    if name not in sys.modules:
        spec = importlib.util.spec_from_file_location(name, pathlib.Path(__file__).with_name("record.py"))
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
    return sys.modules[name]


def _root_relative(entry: str) -> bool:
    parts = entry.rstrip("/").split("/")
    return bool(entry) and entry == entry.strip() and "\\" not in entry and not entry.startswith(("/", "~")) \
        and not re.match(r"^[A-Za-z]:", entry) and all(part not in ("", ".", "..") for part in parts)


def canonical_fields(data: dict) -> dict:
    """The canonical part of an input, validated: behaviour is text, the lists are lists of text, paths are
    root-relative (a folder ends with `/`, `*` and `**` are globs)."""
    if not isinstance(data, dict):
        raise OfferError("an offer is a JSON object")
    unknown = set(data) - set(CANONICAL) - {"display"}
    if unknown:
        raise OfferError(f"unknown offer fields: {', '.join(sorted(unknown))}")
    behaviour = data.get("behaviour")
    if not isinstance(behaviour, str) or not behaviour.strip():
        raise OfferError("behaviour must say, in words, what changes")
    out = {"behaviour": behaviour.strip()}
    for key in LISTS:
        value = data.get(key, [])
        if not isinstance(value, list) or not all(isinstance(v, str) and v.strip() for v in value):
            raise OfferError(f"{key} must be a list of text")
        out[key] = sorted(dict.fromkeys(v.strip() for v in value))
    for key in ("paths", "delegable_paths"):
        bad = [p for p in out[key] if not _root_relative(p)]
        if bad:
            raise OfferError(f"{key} must be root-relative: {', '.join(bad)}")
    if not out["paths"] and not out["operations"]:
        raise OfferError("an offer names the paths or operations it allows")
    out["parent"] = data.get("parent")
    out["parent_provenance"] = data.get("parent_provenance")
    return out


def offer_hash(canonical: dict) -> str:
    """SHA-256 of the canonical fields only (sorted JSON): display text, state and the CSS line never change it."""
    return hashlib.sha256(json.dumps(canonical, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()[:16]


def folder_of(task: str) -> pathlib.Path:
    folder = pathlib.Path(task)
    if not folder.is_dir():
        raise OfferError(f"task folder {folder} does not exist")
    return folder


def offer_path(folder: pathlib.Path, offer_id: int) -> pathlib.Path:
    return folder / "offers" / f"offer-{offer_id}.json"


def load(folder: pathlib.Path, offer_id: int) -> dict:
    try:
        offer = json.loads(offer_path(folder, offer_id).read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise OfferError(f"offer #{offer_id} does not exist in {folder}") from None
    except ValueError as exc:
        raise OfferError(f"offer #{offer_id} is not valid JSON ({exc})") from None
    if offer_hash(offer.get("canonical", {})) != offer.get("hash"):
        raise OfferError(f"offer #{offer_id} was edited by hand: its canonical fields no longer match its hash")
    return offer


def all_offers(folder: pathlib.Path) -> list[dict]:
    found = []
    for path in sorted((folder / "offers").glob("offer-*.json")) if (folder / "offers").is_dir() else []:
        if OFFER_FILE.match(path.name):
            found.append(load(folder, int(OFFER_FILE.match(path.name)[1])))
    return sorted(found, key=lambda o: o["id"])


def task_lock(folder: pathlib.Path):
    """One lock per task's offers, held around every read-validate-write, so two transitions never interleave (a
    stale approval can't overwrite a revocation, two creates can't take the same id)."""
    (folder / "offers").mkdir(exist_ok=True)
    return _record().locked(folder / "offers" / "offers")


def save(folder: pathlib.Path, offer: dict, new: bool) -> None:
    """Write one offer; callers hold task_lock and loaded the offer inside it."""
    path = offer_path(folder, offer["id"])
    data = (json.dumps(offer, indent=2, ensure_ascii=False) + "\n").encode("utf-8")
    record = _record()
    if new:
        record.write_safely(path, data)
    else:
        record.write_safely(path, data, hashlib.sha256(path.read_bytes()).hexdigest())


def now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def new_offer(folder: pathlib.Path, canonical: dict, display: str, supersedes: int | None = None) -> dict:
    ids = [o["id"] for o in all_offers(folder)]
    offer = {"schema": 1, "presentation_format": 2, "id": (max(ids) + 1) if ids else 1, "task": folder.resolve().name, "created": now(),
             "canonical": canonical, "hash": offer_hash(canonical), "display": display, "state": "draft",
             "presentation_decision": None, "decision": None, "supersedes": supersedes, "superseded_by": None}
    save(folder, offer, new=True)
    return offer


def create(folder: pathlib.Path, data: dict) -> dict:
    if data.get("parent") is not None or data.get("parent_provenance") is not None:
        raise OfferError("a child offer is made with `offer derive`, which checks it against its parent")
    canonical = canonical_fields(data)
    with task_lock(folder):
        return new_offer(folder, canonical, str(data.get("display", "")))


def revise(folder: pathlib.Path, old_id: int, data: dict) -> dict:
    with task_lock(folder):
        old = load(folder, old_id)
        if old["state"] in ("superseded", "revoked"):
            raise OfferError(f"offer #{old_id} is {old['state']}; revise the current offer")
        parent_id = old["canonical"]["parent"]
        canonical = canonical_fields({**data, "parent": None, "parent_provenance": None})
        if parent_id is not None:  # a child's revision gets exactly the checks and inheritance of derive
            canonical = child_canonical(load(folder, parent_id), canonical)
        if offer_hash(canonical) == old["hash"]:
            raise OfferError(f"the canonical fields are unchanged; offer #{old_id} still stands (edit display text only)")
        offer = new_offer(folder, canonical, str(data.get("display", "")), supersedes=old_id)
        old.update(state="superseded", superseded_by=offer["id"])
        save(folder, old, new=False)
        return offer


def _covers(scope: str, entry: str) -> bool:
    """Whether one delegable path entry covers a child entry: the same path, a folder (`dir/`) containing it, or a
    glob matching it. A child glob or folder must sit inside a parent folder or be the same text."""
    if scope == entry:
        return True
    if scope.endswith("/"):
        return entry.startswith(scope)
    if "*" in scope or "?" in scope:
        if "*" in entry or "?" in entry or entry.endswith("/"):
            return False
        pattern = re.escape(scope).replace(r"\*\*", "\0").replace(r"\*", "[^/]*").replace(r"\?", "[^/]").replace("\0", ".*")
        return re.fullmatch(pattern, entry) is not None
    return False


def subset_problem(parent: dict, child: dict) -> str | None:
    """C-OFFER-6: why the child's paths and operations are not inside what the parent lists as delegable, or why
    the child would pass on more than it received itself."""
    canon = parent["canonical"]
    paths = [p for p in child["paths"] if not any(_covers(s, p) for s in canon["delegable_paths"])]
    if paths:
        return f"paths outside the parent's delegable paths: {', '.join(paths)}"
    operations = [o for o in child["operations"] if o not in canon["delegable_operations"]]
    if operations:
        return f"operations the parent does not delegate: {', '.join(operations)}"
    bad = [p for p in child["delegable_paths"] if not any(_covers(s, p) for s in child["paths"])]
    bad += [o for o in child["delegable_operations"] if o not in child["operations"]]
    if bad:
        return f"the child would delegate more than it received: {', '.join(bad)}"
    return None


def child_canonical(parent: dict, child: dict) -> dict:
    """The child's canonical fields after the checks: inside the parent's delegable scope, with the parent's
    exclusions, conditions and checks inherited (a child may only add), and the parent's approval provenance."""
    if parent["state"] != "approved" or not parent.get("decision"):
        raise OfferError(f"offer #{parent['id']} is not approved; a child can only derive from an approved offer")
    problem = subset_problem(parent, child)
    if problem:
        raise OfferError(f"the child offer is not a subset of offer #{parent['id']}: {problem}")
    canon = parent["canonical"]
    child = dict(child)
    for key in ("exclusions", "conditions", "checks"):
        child[key] = sorted(set(child[key]) | set(canon[key]))
    child["parent"] = parent["id"]
    child["parent_provenance"] = parent["decision"]
    return child


def derive(folder: pathlib.Path, parent_id: int, data: dict) -> dict:
    child = canonical_fields({**data, "parent": None, "parent_provenance": None})
    with task_lock(folder):
        canonical = child_canonical(load(folder, parent_id), child)
        return new_offer(folder, canonical, str(data.get("display", "")))


def workspace_of(folder: pathlib.Path) -> str:
    """The project root a task folder belongs to (<root>/docs/plans/<task>), as a forward-slash path."""
    return folder.resolve().parents[2].as_posix() if len(folder.resolve().parents) > 2 else folder.resolve().as_posix()


def rendering(offer: dict, folder: pathlib.Path | None = None) -> str:
    """Format 1, frozen: the hook still accepts it for offers shown before format 2 (presentation). Every canonical field, in a fixed order, with the hash, the task and
    the workspace (so identical offers in two tasks or two checkouts are different presentations). Each value is
    JSON-encoded, so supplied text (a newline, a field label, the delimiter) can never pose as another field or end
    the block. The hook compares a shown block byte for byte with this text."""
    c = offer["canonical"]
    value = lambda v: json.dumps(v, ensure_ascii=False)
    where = f" · task {offer['task']} · {workspace_of(folder)}" if folder is not None else f" · task {offer['task']}"
    lines = [f"--- workflow-axa offer #{offer['id']} ({offer['hash']}){where} ---",
             f"Behaviour: {value(c['behaviour'])}",
             f"Paths: {value(c['paths'])}",
             f"Operations: {value(c['operations'])}",
             f"Delegable paths: {value(c['delegable_paths'])}",
             f"Delegable operations: {value(c['delegable_operations'])}",
             f"Excludes: {value(c['exclusions'])}",
             f"Conditions: {value(c['conditions'])}",
             f"Checks: {value(c['checks'])}",
             f"Parent: {value(c['parent'])}",
             f"Parent provenance: {value(c['parent_provenance'])}",
             f"--- end offer #{offer['id']} ---"]
    return "\n".join(lines)


MARKDOWN_SPECIAL = set("\\`*_[]<>&|~")
LINK_LIKE = re.compile(r"://|www\.|@", re.IGNORECASE)
ANSWER_LINE = ("Reply **approve** to approve from this summary, **show report** to see review.html first, or tell me "
               "what to change. (`/approve {id}`, `/report {id}`, yes, ok, go, ja, akkoord and doe maar work too.)")
QUESTION_LINE = "How would you like to proceed: Show review.html first, Approve from this summary, or Change something?"


def _visible(value: str) -> str:
    """One line in which every control, format or separator character, and every backslash, is spelled out, so nothing
    in a value can break the line, hide text or pose as an escape the renderer made."""
    out = []
    for ch in value:
        if ch == "\\":
            out.append("\\\\")
        elif ch in "\n\r\t":
            out.append({"\n": "\\n", "\r": "\\r", "\t": "\\t"}[ch])
        elif unicodedata.category(ch) in ("Cc", "Cf", "Cs", "Zl", "Zp"):
            out.append(f"\\u{ord(ch):04x}" if ord(ch) <= 0xFFFF else f"\\U{ord(ch):08x}")
        else:
            out.append(ch)
    return "".join(out)


def _code(value: str) -> str:
    """A code span that shows `value` literally, whatever backticks it contains (CommonMark code spans)."""
    text = _visible(value)
    longest = max((len(run) for run in re.findall(r"`+", text)), default=0)
    fence = "`" * (longest + 1)
    pad = " " if text[:1] in ("`", " ") or text[-1:] in ("`", " ") else ""
    return f"{fence}{pad}{text}{pad}{fence}"


def _prose(value: str) -> str:
    """Plain text that renders as itself: Markdown punctuation escaped, a link-like value shown as code instead."""
    text = _visible(value)
    if LINK_LIKE.search(text):
        return _code(value)
    escaped = "".join("\\" + ch if ch in MARKDOWN_SPECIAL else ch for ch in text)
    if escaped[:1] in ("#", "+", "-", "="):
        return "\\" + escaped
    return re.sub(r"^(\d+)([.)])", r"\1\\\2", escaped)


def presentation(offer: dict, folder: pathlib.Path | None = None, question: bool = False) -> str:
    """Format 2: the offer as a readable message, generated so the agent only copies it. Every canonical field is shown
    (empty lists as "None."; delegation and parent sections only when set), values escaped so they render as written,
    then the one question, the answer forms (not in the question tool's variant) and a footer that names the offer,
    its hash, its task and its workspace. The hook compares it exactly; `rendering()` stays the frozen format 1."""
    c = offer["canonical"]

    def section(title: str, items: list[str]) -> list[str]:
        return [f"### {title}", ""] + ([f"- {item}" for item in items] or ["- None."]) + [""]

    lines = [f"## Offer #{offer['id']}", ""]
    lines += section("What will change", [_prose(c["behaviour"])])
    lines += section("Files allowed to change", [_code(p) for p in c["paths"]])
    lines += section("Protected actions", [_code(o) for o in c["operations"]])
    if c["delegable_paths"]:
        lines += section("Delegable files", [_code(p) for p in c["delegable_paths"]])
    if c["delegable_operations"]:
        lines += section("Delegable protected actions", [_code(o) for o in c["delegable_operations"]])
    lines += section("Excluded", [_prose(e) for e in c["exclusions"]])
    lines += section("Conditions", [_prose(e) for e in c["conditions"]])
    lines += section("Required checks", [_prose(e) for e in c["checks"]])
    for key, title in (("parent", "Parent offer"), ("parent_provenance", "Parent approval provenance")):
        if c[key] is not None:
            lines += section(title, [_code(json.dumps(c[key], ensure_ascii=False, sort_keys=True, separators=(",", ":")))])
    lines += [QUESTION_LINE, ""]
    if not question:
        lines += [ANSWER_LINE.format(id=offer["id"]), ""]
    where = f" · {workspace_of(folder)}" if folder is not None else ""
    lines.append(_code(f"Offer #{offer['id']} · {offer['hash']} · task {offer['task']}{where}"))
    return "\n".join(lines)


def css_line(root: pathlib.Path | None) -> str:
    """Display only, outside the rendering and its hash (C-OFFER-2): switching CSS never invalidates an offer."""
    spec = importlib.util.spec_from_file_location("workflow_axa_settings", pathlib.Path(__file__).with_name("settings.py"))
    settings = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(settings)
    allowed = settings.css_allowed(root)
    return f"CSS: {'on' if allowed else 'off'} (machine setting{', project says never' if root and settings.project_never(root) else ''}; display only)"


def set_presentation(folder: pathlib.Path, offer_id: int, decision: str) -> dict:
    if decision not in DECISIONS:
        raise OfferError(f"the presentation decision is one of {', '.join(DECISIONS)}")
    with task_lock(folder):
        offer = load(folder, offer_id)
        if offer["state"] in ("superseded", "revoked"):
            raise OfferError(f"offer #{offer_id} is {offer['state']}")
        offer["presentation_decision"] = decision
        save(folder, offer, new=False)
        return offer


def approve(folder: pathlib.Path, offer_id: int, session: str, turn: str, presentation: str | None) -> dict:
    """Record the decision reference: host session id, the user turn id of the answer and the presentation it
    answered. It is a cache: the hook re-validates it against the host transcript before relying on it."""
    if not session.strip() or not turn.strip() or not (presentation or "").strip():
        raise OfferError("the decision reference needs the session id, the user turn id and the presentation reference")
    with task_lock(folder):
        offer = load(folder, offer_id)
        if offer["state"] != "draft":
            raise OfferError(f"offer #{offer_id} is {offer['state']}; only a draft offer can be approved")
        offer.update(state="approved", decision={"session": session.strip(), "turn": turn.strip(),
                                                 "presentation": presentation.strip(), "recorded": now()})
        save(folder, offer, new=False)
        return offer


def reapprove(folder: pathlib.Path, offer_id: int, session: str, turn: str, presentation: str) -> dict:
    """A fresh approval of an already approved offer (after a withdrawal and a new presentation) replaces its decision
    reference. Children derived from the old one stop validating (their parent provenance no longer matches)."""
    if not session.strip() or not turn.strip() or not (presentation or "").strip():
        raise OfferError("the decision reference needs the session id, the user turn id and the presentation reference")
    with task_lock(folder):
        offer = load(folder, offer_id)
        if offer["state"] != "approved":
            raise OfferError(f"offer #{offer_id} is {offer['state']}; only an approved offer can be approved again")
        offer["decision"] = {"session": session.strip(), "turn": turn.strip(), "presentation": presentation.strip(),
                             "recorded": now()}
        save(folder, offer, new=False)
        return offer


def revoke(folder: pathlib.Path, offer_id: int) -> dict:
    with task_lock(folder):
        offer = load(folder, offer_id)
        if offer["state"] in ("superseded", "revoked"):
            raise OfferError(f"offer #{offer_id} is already {offer['state']}")
        offer["state"] = "revoked"
        save(folder, offer, new=False)
        return offer


def read_input(source: str) -> dict:
    raw = sys.stdin.buffer.read() if source == "-" else pathlib.Path(source).read_bytes()
    try:
        return json.loads(raw.decode("utf-8-sig"))
    except (UnicodeError, ValueError) as exc:
        raise OfferError(f"the offer input is not JSON ({exc})") from None


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(prog="record.py offer", description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("create", "list"):
        p = sub.add_parser(name)
        p.add_argument("task")
        if name == "create":
            p.add_argument("source")
    for name in ("revise", "derive"):
        p = sub.add_parser(name)
        p.add_argument("task")
        p.add_argument("id", type=int)
        p.add_argument("source")
    for name in ("present", "show", "revoke"):
        p = sub.add_parser(name)
        p.add_argument("task")
        p.add_argument("id", type=int)
        if name == "present":
            p.add_argument("--root", type=pathlib.Path)
            p.add_argument("--question", action="store_true", help="the variant for the question tool's text")
    p = sub.add_parser("presentation")
    p.add_argument("task")
    p.add_argument("id", type=int)
    p.add_argument("decision", choices=DECISIONS)
    p = sub.add_parser("approve")
    p.add_argument("task")
    p.add_argument("id", type=int)
    p.add_argument("--session", required=True)
    p.add_argument("--turn", required=True)
    p.add_argument("--presentation", required=True)
    args = parser.parse_args(argv)
    try:
        folder = folder_of(args.task)
        if args.command == "create":
            offer = create(folder, read_input(args.source))
        elif args.command == "revise":
            offer = revise(folder, args.id, read_input(args.source))
            print(f"offer #{args.id} superseded by #{offer['id']}")
        elif args.command == "derive":
            offer = derive(folder, args.id, read_input(args.source))
        elif args.command == "present":
            offer = load(folder, args.id)
            if offer["state"] in ("superseded", "revoked"):
                raise OfferError(f"offer #{args.id} is {offer['state']}; present the current offer")
            print(css_line(args.root))
            print()
            print(presentation(offer, folder, question=args.question))
            return 0
        elif args.command == "presentation":
            offer = set_presentation(folder, args.id, args.decision)
        elif args.command == "approve":
            offer = approve(folder, args.id, args.session, args.turn, args.presentation)
        elif args.command == "revoke":
            offer = revoke(folder, args.id)
        elif args.command == "show":
            print(json.dumps(load(folder, args.id), indent=2, ensure_ascii=False))
            return 0
        else:
            for offer in all_offers(folder):
                print(f"#{offer['id']} {offer['state']} {offer['hash']} {offer['canonical']['behaviour'][:80]}")
            return 0
        print(f"offer #{offer['id']} {offer['state']} ({offer['hash']})")
        return 0
    except OfferError as exc:
        print(f"BLOCKED: {exc}")
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
