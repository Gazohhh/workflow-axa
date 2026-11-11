"""Sourced task content for schema-2 reports; no execution or approval authority."""
from __future__ import annotations

import html
import re


PHASES = {"planning", "progress", "delivery"}
CHECK_STATES = {"passed", "failed", "red", "stale", "limited", "blocked", "not-run"}  # red: failed before the change, as planned
RESULT_STATES = {"verified", "partial", "failed", "unverified", "waived", "superseded"}
AGREEMENT_STATES = {"approved", "waived", "legacy", "not-required", "not-approved", "unknown"}
RECORDED = {"approved", "waived"}  # an exact revision and the real response are required
AUTHORITY = RECORDED | {"legacy", "not-required"}  # cite the record; no invented response
TERMINAL_TASKS = {"verified", "removed", "superseded", "not-applicable"}
SECTIONS = {"request", "agreement", "goals", "non-goals", "specification", "decisions", "risks", "testing", "milestones", "delivery"}


def fields(value, name, required, optional=()):
    if not isinstance(value, dict):
        raise ValueError(f"{name} must be an object")
    unknown = set(value) - set(required) - set(optional)
    if unknown:
        raise ValueError(f"Unknown {name} fields: {', '.join(sorted(unknown))}")
    missing = set(required) - set(value)
    if missing:
        raise ValueError(f"Missing {name} fields: {', '.join(sorted(missing))}")


def sourced(row, sources, api, name):
    api.text(row.get("source"), f"{name}.source", 48)
    if row.get("source") not in sources:
        raise ValueError(f"{name}.source must name a supplied source")
    api.text(row.get("locator"), f"{name}.locator")


def validate(data, sources, api):
    report = data["task_report"]
    fields(report, "task_report", ("phase", "agreement", "sections", "tickets", "checks", "acceptance_results"), ("completion", "screen_change", "attention"))
    api.text(report["phase"], "task_report.phase", 30)
    if report["phase"] not in PHASES:
        raise ValueError("task_report.phase is invalid")
    # Design retro: a plan copied a sibling report without ui_review and asked approval for a visible change.
    screen = report.get("screen_change")
    if screen is None and (data["state"] in {"awaiting-approval", "approved"} or report["phase"] == "planning"):
        raise ValueError('task_report.screen_change is required: "visible" when users see any change on screen '
                         '(order, text, which rows show, layout), otherwise "none"')
    if screen is not None and screen not in {"visible", "none"}:
        raise ValueError('task_report.screen_change must be "visible" or "none"')
    ui = data.get("ui_review")
    if screen == "visible" and not (isinstance(ui, dict) and ui.get("kind") == "application"):
        raise ValueError("A change users can see needs its screen diagram: add ui_review (kind application) "
                         "with current and proposed screens; see UI-FLOW.md and ui-design step 3")
    agreement = report["agreement"]
    fields(agreement, "agreement", ("status", "summary"), ("revision", "response", "source", "locator"))
    api.text(agreement["summary"], "agreement.summary")
    api.text(agreement["status"], "agreement.status", 30)
    if agreement["status"] not in AGREEMENT_STATES:
        raise ValueError("agreement.status is invalid")
    if agreement["status"] in RECORDED:
        for key in ("revision", "response"):
            api.text(agreement.get(key), f"agreement.{key}")
        sourced(agreement, sources, api, "agreement")
    elif "response" in agreement or ("revision" in agreement and agreement["status"] not in AUTHORITY):
        raise ValueError("Only an approved or waived agreement records a response; others cannot claim an approved revision or response")
    elif agreement["status"] in AUTHORITY:
        if "revision" in agreement:
            api.text(agreement["revision"], "agreement.revision")
        sourced(agreement, sources, api, "agreement")
    elif "source" in agreement or "locator" in agreement:
        sourced(agreement, sources, api, "agreement")
    if data["state"] in {"awaiting-approval", "approved"} and agreement["status"] not in AUTHORITY:
        raise ValueError("An approval-ready implementation plan needs recorded behavior agreement")

    sections = api.indexed(report["sections"], "task_report.sections", empty=False)
    if set(sections) - SECTIONS:
        raise ValueError("Unknown task_report section id")
    needed = {"request", "specification", "decisions", "risks", "testing"}
    if report["phase"] == "delivery":
        needed.add("delivery")
    # Goals and non-goals (design-doc layout) replace the older single agreement section; never both.
    goals = {"goals", "non-goals"} & set(sections)
    if goals and "agreement" in sections:
        raise ValueError("Use the goals and non-goals sections or the older agreement section, not both")
    if len(goals) == 1:
        raise ValueError("goals and non-goals come together: add the missing one")
    if not goals:
        needed.add("agreement")
    if needed - set(sections):
        raise ValueError("task_report needs request, agreement (or goals and non-goals), specification, decisions, risks and testing sections; delivery also needs its summary")
    for row in sections.values():
        fields(row, "section", ("id", "title", "text", "source", "locator"))
        api.text(row["title"], "section.title", 100)
        api.text(row["text"], "section.text", 20000)
        sourced(row, sources, api, "section")

    # What the owner must read before approving: one short sourced line each, shown beside the status.
    for row in api.rows(report.get("attention", []), "task_report.attention"):
        fields(row, "attention", ("text", "source", "locator"))
        api.text(row["text"], "attention.text", 300)
        sourced(row, sources, api, "attention")
    if len(report.get("attention", [])) > 3:
        raise ValueError("At most three attention lines: the header names surprises, the sections explain them")

    tasks = {row["id"] for row in data["tasks"]}
    ticket_ids = set()
    for row in api.rows(report["tickets"], "task_report.tickets"):
        fields(row, "ticket specification", ("task", "specification", "expected", "source", "locator"))
        api.text(row["task"], "ticket.task", 48)
        if row["task"] not in tasks or row["task"] in ticket_ids:
            raise ValueError("Ticket specifications must reference unique known tasks")
        ticket_ids.add(row["task"])
        api.text(row["specification"], "ticket.specification", 12000)
        api.text(row["expected"], "ticket.expected", 4000)
        sourced(row, sources, api, "ticket")
    if ticket_ids != tasks:
        raise ValueError("A central report needs a specification for every task")

    checks = api.indexed(report["checks"], "task_report.checks")
    for row in checks.values():
        fields(row, "check", ("id", "title", "kind", "status", "expected", "actual", "limits", "source", "locator"), ("command",))
        api.text(row["kind"], "check.kind", 30)
        api.text(row["status"], "check.status", 30)
        if row["kind"] not in {"test", "review", "inspection"} or row["status"] not in CHECK_STATES:
            raise ValueError("Invalid check kind or status")
        for key in ("title", "expected", "actual", "limits"):
            api.text(row[key], f"check.{key}")
        if "command" in row:
            api.text(row["command"], "check.command", 4000)
        sourced(row, sources, api, "check")

    acceptance = {row["id"] for row in data["acceptance"]}
    result_ids = set()
    for row in api.rows(report["acceptance_results"], "task_report.acceptance_results"):
        fields(row, "acceptance result", ("acceptance", "status", "checks", "note", "source", "locator"))
        key = row["acceptance"]
        api.text(key, "acceptance result.acceptance", 48)
        api.text(row["status"], "acceptance result.status", 30)
        if key not in acceptance or key in result_ids:
            raise ValueError("Acceptance results must reference unique known criteria")
        result_ids.add(key)
        if row["status"] not in RESULT_STATES:
            raise ValueError("Invalid acceptance result status")
        api.text(row["note"], "acceptance result.note")
        sourced(row, sources, api, "acceptance result")
        refs = api.references(row["checks"], checks, "acceptance result.checks", required=row["status"] == "verified")
        if row["status"] == "verified" and any(checks[ref]["status"] != "passed" for ref in refs):
            raise ValueError("Verified acceptance requires passed evidence")
        if row["status"] == "failed" and not any(checks[ref]["status"] == "failed" for ref in refs):
            raise ValueError("Failed acceptance needs a failed check")
        if row["status"] == "superseded" and refs:
            raise ValueError("A superseded criterion cites its decision in note/source, not checks")

    if report["phase"] == "delivery":
        if data.get("report_kind") != "task-overview":
            raise ValueError("Delivery is a sourced task-overview, not a new approval request")
        if result_ids != acceptance:
            raise ValueError("Delivery must account for every acceptance criterion")
        api.text(report.get("completion"), "task_report.completion", 30)
        if report["completion"] not in {"complete", "partial", "blocked"}:
            raise ValueError("Delivery needs explicit completion state")
        if report["completion"] == "complete":
            checkpoint = data["checkpoint"]
            covered = {req for row in data["acceptance"] for req in row["requirements"]}
            results = report["acceptance_results"]
            failed = [message for broken, message in (
                (not acceptance or any(row["status"] not in {"verified", "superseded"} for row in results)
                 or not any(row["status"] == "verified" for row in results), "every acceptance verified or superseded, at least one verified"),
                (not checks or any(row["status"] not in ("passed", "red") for row in checks.values()), "every check passed (red only before the change)"),
                (not any(row["kind"] == "review" for row in checks.values()), "a review among the checks"),
                (any(row.get("outcome") not in TERMINAL_TASKS for row in data["tasks"]),
                 "every task outcome verified/removed/superseded/not-applicable"),
                ({row["id"] for row in data["requirements"]} - covered, "every requirement covered by an acceptance item"),
                (data["open_decisions"], "no open decision"),
                (checkpoint["verification"]["status"] != "passed", "checkpoint verification passed"),
                (checkpoint["implementation"]["status"] != "implemented", "checkpoint implementation implemented"),
                (checkpoint["approval"]["status"] not in AUTHORITY or agreement["status"] not in AUTHORITY,
                 "agreement and approval recorded")) if broken]
            if failed:  # name what failed (round 7: the agent read the renderer source to find out)
                raise ValueError("A complete delivery needs: " + "; ".join(failed) + ". Otherwise use partial.")
    elif "completion" in report:
        raise ValueError("completion belongs only to delivery")




PLAIN_WORDS = re.compile(r"\b(ensure|leverage|utilize|robust|seamless(?:ly)?|comprehensive|crucial|simply)\b", re.I)
# Audit E16: these words carry uncertainty, permission or a proposal. Replacing or deleting them can turn
# "it could be the cache" into a false certainty, so they get a note that keeps the meaning, not a problem.
MEANING_WORDS = re.compile(r"\b(should|would|may|might|could)\b", re.I)
MEANING_NOTE = ("keep each word that states uncertainty, permission or a proposal. Rewrite only empty hedging, "
                "and never just delete the word")
CONTRACTION = re.compile(r"\b\w+['’](?:t|ve|re|ll|d|m)\b", re.I)
# Quoted user words and code keep their exact wording, including punctuation such as semicolons.
QUOTED = re.compile(r'"[^"\n]*"|“[^”\n]*”|`[^`\n]*`')


def prose_fields(data):
    """(JSON path, text) for the prose a reader sees, in every report kind."""
    report = data.get("task_report") if isinstance(data.get("task_report"), dict) else {}
    fields = [("understanding", data.get("understanding", ""))]
    if report:
        fields.append(("task_report.agreement.summary", (report.get("agreement") or {}).get("summary", "")))
    fields += [(f'task_report.sections[{row["id"]}].text', row["text"]) for row in report.get("sections", [])]
    fields += [(f'task_report.attention[{i}].text', row.get("text", "")) for i, row in enumerate(report.get("attention", []))]
    fields += [(f'task_report.tickets[{row["task"]}].{key}', row[key]) for row in report.get("tickets", []) for key in ("specification", "expected")]
    fields += [(f'task_report.checks[{row["id"]}].{key}', row[key]) for row in report.get("checks", []) for key in ("expected", "actual", "limits")]
    fields += [(f'task_report.acceptance_results[{row["acceptance"]}].note', row["note"]) for row in report.get("acceptance_results", [])]
    # Round 15: other text the page shows kept semicolons.
    fields += [(f'boundaries[{i}]', text) for i, text in enumerate(data.get("boundaries", []))]
    fields += [(f'open_decisions[{i}]', text) for i, text in enumerate(data.get("open_decisions", []))]
    fields += [(f'tasks[{row["id"]}].outcome_note', row.get("outcome_note", "")) for row in data.get("tasks", [])]
    # Round 17: requirements, ticket reasons, comparison rows and acceptance text kept semicolons too.
    fields += [(f'tasks[{row["id"]}].{key}', row.get(key, "")) for row in data.get("tasks", []) for key in ("title", "reason")]
    fields += [(f'requirements[{row["id"]}].text', row.get("text", "")) for row in data.get("requirements", [])]
    fields += [(f'acceptance[{row["id"]}].{key}', row.get(key, "")) for row in data.get("acceptance", []) for key in ("text", "verification")]
    fields += [(f'comparison[{i}].{key}', row.get(key, "")) for i, row in enumerate(data.get("comparison", []))
               for key in ("label", "current", "proposed")]
    fields += [(f'graphs[{g["id"]}].{key}', g.get(key, "")) for g in data.get("graphs", []) for key in ("title", "description")]
    if isinstance(data.get("checkpoint"), dict):
        fields.append(("checkpoint.next_action", data["checkpoint"].get("next_action", "")))
    ui = data.get("ui_review") or {}
    fields += [(f'ui_review.{key}', ui.get(key, "")) for key in ("summary", "limit")]
    fields += [(f'ui_review.screens[{s.get("id")}].description', s.get("description", "")) for s in ui.get("screens", [])]
    return [(path, QUOTED.sub("quote", text)) for path, text in fields if isinstance(text, str) and not text.startswith("FILL: ")]


def prose_notes(data):
    """Advisory notes for words that may carry meaning: (JSON path, note). Never a problem to fix."""
    notes = []
    for path, text in prose_fields(data):
        words = sorted({m.group(0).lower() for m in MEANING_WORDS.finditer(text)})
        if words:
            notes.append((path, f'{", ".join(words)}: {MEANING_NOTE}'))
    return notes


def prose_issues(data):
    """Simple English checks on the report's prose fields: (JSON path, problem). Advice, not a validation error."""
    issues = []
    for path, text in prose_fields(data):
        found = []
        if ";" in text:
            found.append("semicolon (write two sentences)")
        if "—" in text:
            found.append("em-dash (name the relation or write two sentences)")
        if "**" in text:
            found.append("bold markup")
        words = sorted({m.group(0).lower() for m in PLAIN_WORDS.finditer(text)})
        if words:
            found.append("words to replace: " + ", ".join(words))
        if CONTRACTION.search(text):
            found.append("contraction")
        for paragraph in text.split("\n\n"):
            sentences = [s for s in re.split(r"(?<=[.!?])\s+", paragraph.strip()) if s]
            long = [s for s in sentences if len(s.split()) > 25]
            if long:
                found.append(f"{len(long)} sentence(s) over 25 words")
            if len(sentences) > 6:
                found.append(f"paragraph of {len(sentences)} sentences (6 at most)")
        issues += [(path, problem) for problem in found]
    return issues


def paragraphs(value):
    return "".join("<p>" + html.escape(part).replace("\n", "<br>") + "</p>" for part in value.split("\n\n"))


def attribution(row, api):
    return f'<small>Source: {api.links([row["source"]], "s")}, {html.escape(row["locator"])}</small>'


AGREEMENT_WORDS = {
    "approved": "Behavior agreed", "waived": "Behavior agreement waived by the owner",
    "legacy": "Behavior approved under the older single approval",
    "not-required": "No separate behavior agreement needed for this change",
    "not-approved": "Behavior not agreed yet", "unknown": "Behavior agreement not recorded",
}
PLAN_WORDS = {
    "awaiting-approval": "Waiting for your OK on this plan in the chat. The agent writes no code before you give it.",
    "draft": "Draft. The plan is not finished, so there is nothing to approve yet.",
    "superseded": "A newer plan replaced this one. Do not build from it.",
}
COMPLETION_WORDS = {
    "complete": "everything agreed is built and checked. You still need to accept it.",
    "partial": "some work or checks are still open. The sections below name them.",
    "blocked": "the work stopped. The sections below say why.",
}
RESULT_WORDS = {
    "verified": "Verified", "partial": "Partly verified", "failed": "Failed", "unverified": "Not verified",
    "waived": "Waived by the owner, not a pass", "superseded": "Removed from scope, not a pass",
}
CHECK_WORDS = {
    "passed": "Passed", "failed": "Failed", "red": "Failed before the change, as expected", "stale": "Stale: it passed on files that changed after the check",
    "limited": "Limited", "blocked": "Blocked", "not-run": "Not run",
}
# The page follows the design-doc order: context, goals, design, alternatives, concerns. The work comes last.
TOC = (("context", "Context and scope"), ("goals", "Goals and non-goals"), ("design", "The design"),
       ("alternatives", "Alternatives considered"), ("concerns", "Cross-cutting concerns"), ("the-work", "The work"))
# The visible label of each sourced section, for the "Where each part comes from" list.
SECTION_LABELS = {"request": "Context and scope", "goals": "Goals", "non-goals": "Non-goals", "agreement": "Agreed behavior",
                  "specification": "Overview", "decisions": "Alternatives considered", "risks": "Cross-cutting concerns",
                  "testing": "How it is tested", "milestones": "Order of the work", "delivery": "What was delivered"}


def bullets(value, style="list"):
    """One list item per paragraph of a sourced text."""
    items = "".join(f"<li>{html.escape(part).replace(chr(10), '<br>')}</li>" for part in value.split("\n\n") if part.strip())
    return f'<ul class="{style}">{items}</ul>'


def attention_html(data):
    """Header lines the owner reads before approving. Each points at the decisions that explain it."""
    rows = data["task_report"].get("attention", [])
    return "".join('<p class="status status--attention"><span class="status__tag">Read first</span>'
                   f'<span>{html.escape(row["text"])} <a href="#alternatives">See the decisions</a>.</span></p>' for row in rows)


def status_sentence(data):
    """One plain sentence pair: behaviour agreement and where the plan or delivery stands."""
    report = data["task_report"]
    agreement = report["agreement"]
    words = AGREEMENT_WORDS[agreement["status"]]
    if agreement.get("revision") and agreement["status"] != "not-required":
        words += f' ({agreement["revision"]})'
    words += "."
    checkpoint = data.get("checkpoint")
    if report["phase"] == "delivery":
        return f'Delivered: {report["completion"]}. {COMPLETION_WORDS[report["completion"]][0].upper()}{COMPLETION_WORDS[report["completion"]][1:]} {words}'
    if report["phase"] == "progress" or data.get("report_kind") == "task-overview":
        if checkpoint:
            impl = checkpoint["implementation"]["status"].replace("-", " ")
            ver = checkpoint["verification"]["status"].replace("-", " ")
            return f'{words} Work in progress: building {impl}, checks {ver}. Next: {checkpoint["next_action"]}'
        return f"{words} Work in progress."
    if data["state"] == "approved":
        return f'{words} Plan approved ({data["revision"]}). Read the task record before you continue.'
    if data["state"] == "draft" and agreement["status"] == "not-approved" and not data.get("open_decisions"):
        # Both gates in one message (VISUAL-REVIEW): nothing open, behaviour and plan shown together.
        return ("Waiting for your OK on the behavior and on this plan. Nothing is agreed, approved "
                "or built until you say yes to both.")
    return f'{words} {PLAN_WORDS.get(data["state"], PLAN_WORDS["draft"])}'


STATUS_TAGS = {"draft": "Draft", "awaiting-approval": "Waiting for you", "approved": "Approved",
               "superseded": "Replaced", "inspection": "Inspection"}
TICKET_STATES = {  # task outcome -> (label, ticket__status modifier)
    None: ("Planned", "requested"), "planned": ("Not started", "requested"), "in-progress": ("In progress", "in-progress"),
    "implemented": ("Built, not checked", "in-progress"), "verified": ("Verified", "done"), "blocked": ("Blocked", "blocked"),
    "removed": ("Removed", "requested"), "superseded": ("Replaced", "requested"), "not-applicable": ("Not applicable", "requested"),
}
STATE_CLASS = {"verified": "verified", "passed": "verified", "failed": "failed", "partial": "partial", "stale": "partial",
               "limited": "partial", "blocked": "failed"}


def status_tag(data):
    """The short tag before the status sentence, and whether it reads as a good outcome."""
    report = data["task_report"]
    if report["phase"] == "delivery":
        return "Delivered", report["completion"] == "complete"  # the sentence already says complete/partial/blocked
    if report["phase"] == "progress" or data.get("report_kind") == "task-overview":
        return "In progress", False
    if data["state"] == "draft" and report["agreement"]["status"] == "not-approved" and not data.get("open_decisions"):
        return "Waiting for you", False  # both gates asked in one message (round 17: tag said Draft)
    return STATUS_TAGS.get(data["state"], "Draft"), data["state"] == "approved"


def facts(data, api):
    """The at-a-glance row under the title. No tile repeats the masthead or shows an empty value."""
    esc = html.escape
    report = data["task_report"]
    results = report["acceptance_results"]
    verified = sum(1 for row in results if row["status"] == "verified")
    open_count = len(data["open_decisions"])
    as_of = (data.get("checkpoint") or {}).get("as_of", "")
    items = [("Tickets", f'{len(report["tickets"])}'), ("Checks", f'{verified} of {len(data["acceptance"])} verified')]
    if open_count:
        items.append(("Open questions", f'<a href="#open-questions">{open_count} to answer</a>'))
    if as_of:
        items.append(("As of", esc(as_of)))
    attention = ' class="facts__value--attention"'
    cells = "".join(f'<div class="facts__item"><dt>{name}</dt><dd{attention if name == "Open questions" else ""}>{value}</dd></div>'
                    for name, value in items)
    return f'<dl class="facts" aria-label="At a glance">{cells}</dl>'


def render(data, api, parts):
    """Return (status sentence, facts HTML, body HTML) for a central task report; every data string is escaped."""
    esc = html.escape
    report = data["task_report"]
    sections = {row["id"]: row for row in report["sections"]}
    tasks = {row["id"]: row for row in data["tasks"]}
    acceptance = {row["id"]: row for row in data["acceptance"]}
    results = {row["acceptance"]: row for row in report["acceptance_results"]}
    checks = {row["id"]: row for row in report["checks"]}
    planning = report["phase"] == "planning"
    delivered = report["phase"] == "delivery"
    open_count = len(data["open_decisions"])

    def section(key, title, summary=""):
        lead = f'<p class="section__summary">{esc(summary)}</p>' if summary else ""
        return f'<section class="section" aria-labelledby="{key}"><h2 class="section__title" id="{key}">{esc(title)}</h2>{lead}'

    def block(key, label, anchor=""):
        if key not in sections:
            return ""
        mark = f' id="{anchor}"' if anchor else ""
        return f'<div class="block"{mark}><h3>{esc(label)}</h3>{paragraphs(sections[key]["text"])}</div>'

    flag = f'<span class="toc__flag">{open_count} open question{"s" if open_count != 1 else ""}</span>' if open_count else ""
    toc = "".join(f'<li><a class="toc__link" href="#{key}">{esc(title)}{flag if key == "concerns" else ""}</a></li>' for key, title in TOC)
    out = ['<div class="layout"><nav class="toc" aria-label="Contents"><p class="toc__title">Contents</p>'
           f'<ol class="toc__list">{toc}</ol><a class="toc__extra" href="#technical-details">Reference</a></nav>'
           '<div class="content" id="task-report">']

    # 1. Context and scope: the problem and the facts. No goals and no design here.
    out.append(section("context", "Context and scope", report["agreement"]["summary"]))
    out.append(paragraphs(sections["request"]["text"]))
    if open_count:
        out.append(f'<p class="note">{open_count} question{"s are" if open_count != 1 else " is"} still open. '
                   '<a href="#open-questions">See the open questions</a></p>')
    out.append("</section>")

    # 2. Goals and non-goals. Older reports carry one agreement text instead.
    out.append(section("goals", "Goals and non-goals"))
    if "goals" in sections:
        out.append(f'<div class="columns"><div><h3>Goals</h3>{bullets(sections["goals"]["text"])}</div>'
                   f'<div><h3>Non-goals</h3>{bullets(sections["non-goals"]["text"])}</div></div>')
    else:
        out.append(block("agreement", "What will happen" if planning else "Agreed behavior"))
    out.append("</section>")

    # 3. The design: overview, diagrams, before and after, constraints.
    fit = " review--fit" if parts.compact else ""
    out.append(section("design", "The design") + block("specification", "Overview") + parts.flow_context +
               f'<section class="review{fit}" aria-label="Design diagrams">{parts.controls}<div class="figures">{parts.figures}</div></section>')
    if data["comparison"]:
        before, after = ("Before", "After") if data.get("report_kind") == "task-overview" else ("Today", "After the change")
        rows = "".join(
            f'<tr><th scope="row">{esc(row["label"])}</th><td>{esc(row["current"])}</td><td class="after">{esc(row["proposed"])} '
            + ('<span class="tag">Unchanged</span>' if row["current"].strip() == row["proposed"].strip() else '')  # no guessed "Changed" tag
            + "</td></tr>" for row in data["comparison"])
        out.append('<div class="block" id="before-after"><h3>Before and after</h3><div class="table-scroll"><table class="compare"><thead><tr>'
                   f'<th scope="col">Situation</th><th scope="col">{before}</th><th scope="col">{after}</th></tr></thead>'
                   f'<tbody>{rows}</tbody></table></div></div>')
    if data["boundaries"]:
        bounds = "".join(f"<li>{esc(item)}</li>" for item in data["boundaries"])
        out.append(f'<div class="block" id="constraints"><h3>Constraints</h3><ul class="list--keep">{bounds}</ul></div>')
    out.append("</section>")

    # 4. Alternatives considered: one item per decision, with what it was chosen over and why.
    out.append(section("alternatives", "Alternatives considered") + bullets(sections["decisions"]["text"]) + "</section>")

    # 5. Cross-cutting concerns: risks, evidence limits and open questions. Nothing is shown for an empty list.
    out.append(section("concerns", "Cross-cutting concerns"))
    several = bool(parts.uncertainty or open_count)
    out.append(('<h3>Risks and limits</h3>' if several else '') + bullets(sections["risks"]["text"], "risks"))
    if parts.uncertainty:
        out.append('<h3>Evidence limits</h3><ul class="risks">' + "".join(f"<li>{esc(v)}</li>" for v in parts.uncertainty) + "</ul>")
    if open_count:
        questions = "".join(f'<li class="question" id="q-{i}"><p class="question__title"><span class="question__key">Q{i}</span> {esc(item)}</p></li>'
                            for i, item in enumerate(data["open_decisions"], 1))
        out.append('<div class="questions" id="open-questions"><div class="questions__head"><h3>Open questions</h3>'
                   f'<p>Work starts after these are answered.</p></div><ol class="question-list">{questions}</ol></div>')
    out.append("</section>")

    # 6. The work: how it is tested, then one card per ticket with its own checks.
    order = [row["task"] for row in report["tickets"]]
    linear = all(tasks[key]["depends_on"] == order[max(i - 1, 0):i] for i, key in enumerate(order))
    count = f'{len(order)} ticket{"s" if len(order) != 1 else ""}'
    summary = ""
    if planning:
        summary = f'The implementation plan: {count}, built after you approve.'
        if linear and len(order) > 1:
            summary += " They are built in this order. Each starts when the one before is verified."
    out.append(section("the-work", "The work", summary))
    out.append(block("delivery", "What was delivered") + block("testing", "How it was tested" if delivered else "How it is tested")
               + block("milestones", "Order of the work"))

    def check_item(key):
        row, result = acceptance[key], results.get(key)
        state = (f'<span class="state state--{STATE_CLASS.get(result["status"], "open")}" id="result-{esc(key)}" data-result="{esc(result["status"])}">'
                 f'{esc(RESULT_WORDS[result["status"]])}</span>' if result else '<span class="state">Not checked</span>')
        note = ""
        if result:
            refs = ", ".join(f'<a href="#check-{esc(ref)}">{esc(checks[ref]["title"])}</a> ({esc(CHECK_WORDS[checks[ref]["status"]])})'
                             for ref in result["checks"]) or "no check linked"
            note = f'<p class="check__how">{esc(result["note"])} Evidence: {refs}</p>'
        return (f'<li class="check" id="a-{esc(key)}"><span class="check__key">{esc(key)}</span>'
                f'<p class="check__expect">{esc(row["text"])}</p><p class="check__how">Checked by: {esc(row["verification"])}</p>{note}{state}</li>')

    shown = {}  # acceptance id -> the ticket that lists it in full; every check is stated once
    cards = []
    for row in report["tickets"]:
        key = row["task"]
        task = tasks[key]
        label, modifier = TICKET_STATES.get(task.get("outcome"), TICKET_STATES[None])
        items = []
        for item in task["acceptance"]:
            if item in shown:
                items.append(f'<li class="check check--ref"><span class="check__key">{esc(item)}</span><p class="check__how">Listed under '
                             f'<a href="#a-{esc(item)}">{esc(shown[item])}</a>. It applies to this ticket too.</p></li>')
            else:
                shown[item] = key
                items.append(check_item(item))
        done = f'<dt>Done when</dt><dd><ol class="checks">{"".join(items)}</ol></dd>' if items else ""
        deps = ""
        if not linear and task["depends_on"]:
            deps = "<dt>Depends on</dt><dd>" + " ".join(f'<a class="ticket-ref" href="#spec-{esc(dep)}">{esc(dep)}</a> {esc(tasks[dep]["title"])}'
                                                        for dep in task["depends_on"]) + "</dd>"
        touches = f'<dt>Touches</dt><dd><code>{esc(", ".join(task["areas"]))}</code></dd>' if task.get("areas") else ""
        outcome = f'<dt>Outcome</dt><dd>{parts.outcome(task)}</dd>' if "outcome" in task else ""
        cards.append(f'<article class="ticket" id="spec-{esc(key)}" aria-labelledby="spec-{esc(key)}-title">'
                     f'<p class="ticket__stub">Ticket <span class="ticket__key">{esc(key)}</span>'
                     f'<span class="ticket__status ticket__status--{modifier}">{esc(label)}</span></p>'
                     f'<div class="ticket__main"><h3 class="ticket__title" id="spec-{esc(key)}-title">{esc(task["title"])}</h3>'
                     f'{paragraphs(row["specification"])}{paragraphs(row["expected"])}</div>'
                     f'<dl class="ticket__facts">{deps}{done}{touches}{outcome}</dl></article>')
    out.append(f'<div class="tickets">{"".join(cards)}</div>')
    loose = [key for key in acceptance if key not in shown]
    if loose:
        out.append(f'<div class="block"><h3>Checks outside the tickets</h3><ol class="checks">{"".join(check_item(key) for key in loose)}</ol></div>')
    if checks:
        rows = []
        for row in checks.values():
            command = f'<p class="check__how">Command: <code>{esc(row["command"])}</code></p>' if "command" in row else ""
            rows.append(f'<li class="check" id="check-{esc(row["id"])}"><span class="check__key">{esc(row["id"])}</span>'
                        f'<p class="check__expect">{esc(row["title"])} <span class="muted">({esc(row["kind"])})</span></p>'
                        f'<p class="check__how">Expected: {esc(row["expected"])}</p><p class="check__how">Observed: {esc(row["actual"])}</p>'
                        f'<p class="check__how">Limits: {esc(row["limits"])}</p>{command}'
                        f'<span class="state state--{STATE_CLASS.get(row["status"], "open")}">{esc(CHECK_WORDS[row["status"]])}</span></li>')
        out.append(f'<div class="block"><h3>Checks and reviews</h3><ol class="checks">{"".join(rows)}</ol></div>')
    out.append("</section>")

    # 7. Reference: provenance, records and traceability. One requirements table carries the links.
    agreement = report["agreement"]
    record = [f'<p>Status: <strong>{esc(agreement["status"])}</strong>'
              + (f' · {esc(agreement["revision"])}' if agreement.get("revision") else "") + "</p>"]
    if "response" in agreement:
        record.append(f'<p>Recorded response:</p><blockquote>{esc(agreement["response"])}</blockquote>')
    if "source" in agreement:
        record.append(attribution(agreement, api))
    approval = ""
    if data["state"] == "approved" and isinstance(data.get("approval"), dict):
        approval = (f'<section><h2>Plan approval record</h2><p>{esc(data["approval"]["record"])}</p>'
                    f'<blockquote>{esc(data["approval"]["response"])}</blockquote></section>')
    requirement_rows = "".join(
        f'<tr id="r-{esc(row["id"])}"><td><strong>{esc(row["id"])}</strong></td><td>{esc(row["text"])}</td><td>{esc(row["origin"])}</td>'
        f'<td>{api.links([t["id"] for t in data["tasks"] if row["id"] in t["requirements"]], "spec")}<br>'
        f'{api.links([key for key, a in acceptance.items() if row["id"] in a["requirements"]], "a")}</td></tr>'
        for row in data["requirements"]) or '<tr><td colspan="4">No requirements recorded.</td></tr>'
    ticket_rows = "".join(
        f'<tr id="t-{esc(t["id"])}"><td><strong>{esc(t["id"])}</strong></td><td>{esc(t["kind"])}: {esc(t["reason"])}</td>'
        f'<td>{api.links(t["evidence"], "e")}</td><td>{api.links(t["depends_on"], "spec")}</td></tr>'
        for t in data["tasks"]) or '<tr><td colspan="4">No implementation tasks.</td></tr>'
    change_rows = "".join(f'<li><strong>{esc(row["label"])}</strong>: {api.links(row["evidence"], "e")}</li>' for row in data["comparison"])
    labels = {**SECTION_LABELS, "agreement": "What will happen" if planning else "Agreed behavior",
              "testing": "How it was tested" if delivered else "How it is tested"}
    origins = [(labels.get(row["id"], row["title"]), row) for row in report["sections"]]
    origins += [(f'Read first: {row["text"]}', row) for row in report.get("attention", [])]
    origins += [(f'Ticket {row["task"]}', row) for row in report["tickets"]]
    origins += [(f'Check {row["id"]}', row) for row in report["checks"]]
    origins += [(f'Result for {row["acceptance"]}', row) for row in report["acceptance_results"]]
    origin_html = "".join(f"<li>{esc(label)} {attribution(row, api)}</li>" for label, row in origins)
    out.append('<details class="appendix" id="technical-details"><summary>Reference: requirements, evidence and sources</summary><div class="appendix-body">'
               '<p class="muted">This page is generated from the task records. It approves nothing, it does not show who approved, '
               'and it does not prove that a check ran. Waived or unverified work is not a passed check.</p>'
               f'<section><h2>Behavior agreement record</h2>{"".join(record)}</section>{approval}{parts.checkpoint}{parts.history}'
               '<section><h2>Requirements</h2><div class="table-scroll"><table><thead><tr><th>ID</th><th>Requirement</th><th>Source</th>'
               f'<th>Covered by</th></tr></thead><tbody>{requirement_rows}</tbody></table></div></section>'
               '<section><h2>Tickets: reason and evidence</h2><div class="table-scroll"><table><thead><tr><th>Ticket</th><th>Why it is needed</th>'
               f'<th>Evidence</th><th>Depends on</th></tr></thead><tbody>{ticket_rows}</tbody></table></div></section>'
               + (f'<section><h2>Before and after: evidence</h2><ul class="plain">{change_rows}</ul></section>' if change_rows else '')
               + f'<section><h2>Where each part comes from</h2><ul class="plain">{origin_html}</ul></section>'
               f'<section><h2>Evidence and limits</h2>{parts.evidence}</section>{parts.graph_records}\n{parts.snapshot}\n</div></details>')
    out.append("</div></div>")
    return status_sentence(data), facts(data, api), "".join(out)


FILL = 'FILL: '
STALE_WORDS = ('not yet', ' will ', 'at delivery', 'can reject', 'waits for')


def scaffold_delivery(review: dict) -> dict:
    """A valid delivery projection from an approved review JSON. Only the FILL texts need editing.

    The scaffold never claims a result: every acceptance starts unverified, completion starts partial,
    verification limited. Edit them from the records, adding checks with their real outcomes.
    """
    import copy
    data = copy.deepcopy(review)
    source = data['sources'][0]['id']
    where = {'source': source, 'locator': FILL + 'record heading'}
    data['report_kind'] = 'task-overview'
    data['state'] = 'draft'
    # Always a fresh checkpoint: the plan's said "not implemented" under "Delivered" (round-5 retro).
    data['checkpoint'] = ({
        'as_of': FILL + 'date of this delivery', 'source': source, 'locator': 'Current checkpoint',
        'approval': {'status': 'approved', 'revision': data['revision'], 'summary': FILL + 'who approved what, when'},
        'implementation': {'status': 'implemented', 'summary': FILL + 'what was built'},
        'verification': {'status': 'limited', 'summary': FILL + 'what was checked and what was not'},
        'next_action': FILL + 'next safe action'})
    # Round-6 retro: these were copied from the plan and said "Nothing was run" next to passed checks.
    if isinstance(data.get('snapshot'), dict):
        data['snapshot']['basis'] = FILL + 'what was run and read for this delivery'
    ui = data.get('ui_review')
    if isinstance(ui, dict) and isinstance(ui.get('preview'), dict):
        sketches_only = all(s.get('representation') != 'capture' for s in ui.get('screens', []))
        ui['preview'].update(status='not-needed' if sketches_only else ui['preview'].get('status'),
                             summary=FILL + 'how the screens were shown (kit screens, sketch or capture of the built result)')
    for task in data.get('tasks', []):  # round 7: the scaffold left these out; never claim more than implemented
        task.setdefault('outcome', 'implemented')
        task.setdefault('outcome_note', FILL + 'result and V-ID; set verified only with passing evidence')
    old = data.get('task_report', {})
    agreement = old.get('agreement') or {'status': 'unknown', 'summary': FILL + 'agreement status in plain words'}
    sections = {row['id']: dict(row) for row in old.get('sections', [])}
    for row in sections.values():  # round 14: plan-time wording ("not yet", "will") stayed in deliveries
        if any(word in row['text'].lower() for word in STALE_WORDS):
            row['text'] = FILL + 'rewrite in the past tense from the records: ' + row['text']
    behavior = () if 'goals' in sections else ('agreement',)  # goals and non-goals replace the agreement section
    for key in ('request', *behavior, 'specification', 'decisions', 'risks', 'testing', 'delivery'):
        sections.setdefault(key, {'id': key, 'title': key.title(), 'text': FILL + key, **where})
    tickets = {row['task']: row for row in old.get('tickets', [])}
    data['task_report'] = {
        'phase': 'delivery', 'completion': 'partial', 'agreement': agreement,
        **({'attention': old['attention']} if old.get('attention') else {}),
        'sections': list(sections.values()),
        'tickets': [tickets.get(t['id']) or {'task': t['id'], 'specification': FILL + 'what this ticket built',
                                               'expected': FILL + 'expected result', **where} for t in data['tasks']],
        'checks': old.get('checks', []),
        'acceptance_results': [{'acceptance': a['id'], 'status': 'unverified', 'checks': [],
                                'note': FILL + 'result and evidence', **where} for a in data['acceptance']],
    }
    return data


if __name__ == '__main__':
    import json
    import pathlib
    import sys
    if len(sys.argv) != 4 or sys.argv[1] != 'scaffold':
        print('usage: python -X utf8 -I task_report.py scaffold <approved-review.json> <new-delivery.json>\n'
              'Writes a valid delivery projection; edit every "FILL:" text from the records, then render it.')
        sys.exit(2)
    target = pathlib.Path(sys.argv[3])
    if target.exists():
        print(f'BLOCKED: {target} exists; never overwritten')
        sys.exit(2)
    review = json.loads(pathlib.Path(sys.argv[2]).read_text(encoding='utf-8'))
    target.write_text(json.dumps(scaffold_delivery(review), indent=1, ensure_ascii=False), encoding='utf-8')
    print(f'WROTE {target}; edit the FILL texts, then render with render_report.py')
