"""Shadow comparison of the offer checker (hooks/approval.py) with today's gate (hooks/phase_gate.py), ticket T15 of
docs/plans/2026-11-15-workflow-redesign (REDESIGN.md §14 checkpoint 5).

Each scenario is one owner/agent exchange told twice: in the legacy form (a PLAN.md `Approval:` line and a plan
presentation, as the gate tests build it) and in the offer form (an offer record and its presentation). Both hooks
run as processes on their own temporary repository, and the outcome pair must equal the expected-outcome table
below. Every difference is classified there: a repaired false refusal, or a protection the offer model adds, each
with its contract ID. An unclassified difference fails the test. Synthetic transcripts only; no session content.
"""
from __future__ import annotations

import os
import unittest

import test_approval_hook as new
import test_gate_regressions as old
from test_phase_gate_hook import APPROVED, ROUTER, say, user
from test_session_failures import AGREED, NO_REPORT_APPROVAL, chat_plan

TASK, OTHER = new.TASK, "2026-11-15-other"
NOT_APPROVED = "- Approval: not approved; revision r1 proposed"


def harness(base):
    """A set-up case of the other test module, used only as a harness (built here so discovery never runs it)."""
    case = type("Harness", (base,), {"runTest": lambda self: None})()
    case.setUp()
    return case


def outcome(reason) -> str:
    return "deny" if reason else "allow"


# Each scenario: (legacy(case) -> rows, tool, data), (offer(case) -> rows, tool, data)

def approved_legacy(c, *after, write_paths=None):
    c.task(TASK, APPROVED, write_paths=write_paths)
    return [ROUTER] + c.approval(TASK) + [user(a) for a in after]


def offered(c, *turns, before=()):
    """The owner's messages `before`, the offer presented, then the turns: owner messages, or agent text when
    prefixed with "agent: "."""
    rows = new.Rows().router()
    for text in before:
        rows.owner(text)
    c.presented(rows)
    for turn in turns:
        if turn.startswith("agent: "):
            rows.say(turn[len("agent: "):])
        else:
            rows.owner(turn)
    return rows


def approved_offer(c, *after):
    return offered(c, "yes", *after)


def record_write(rows, c, task):
    rows.append({"type": "assistant", "uuid": rows.uid(), "message": {"content": [{"type": "tool_use", "name": "Write",
                 "input": {"file_path": str(c.repo / "docs/plans" / task / "TODO.md"), "content": "x"}}]}})
    return rows


def plain():
    rows = new.Rows()
    rows.owner("just edit it")
    return rows


def edit(c, rel="src/vat.ts"):
    return {"file_path": str(c.repo / rel), "old_string": "1", "new_string": "2"}


SCENARIOS = {
    "approved write inside the scope": (
        lambda c: (approved_legacy(c), "Edit", c.code("src/vat.ts")),
        lambda c: (approved_offer(c), "Edit", edit(c))),
    "nothing approved": (
        lambda c: (c.task(TASK, NOT_APPROVED) and [ROUTER, c.records(TASK)], "Edit", c.code("src/vat.ts")),
        lambda c: (c.presented(), "Edit", edit(c))),
    "a file outside the approved scope": (
        lambda c: (approved_legacy(c, write_paths=["src/vat.ts"]), "Edit", c.code("src/other.ts")),
        lambda c: (approved_offer(c), "Edit", edit(c, "src/other.ts"))),
    "a stop after the approval": (
        lambda c: (approved_legacy(c, "stop"), "Edit", c.code("src/vat.ts")),
        lambda c: (approved_offer(c, "stop"), "Edit", edit(c))),
    "a stop, then continue": (
        lambda c: (approved_legacy(c, "stop", "continue"), "Edit", c.code("src/vat.ts")),
        lambda c: (approved_offer(c, "stop", "continue"), "Edit", edit(c))),
    "a later withdrawal": (
        lambda c: (approved_legacy(c, "I revoke that, not approved"), "Edit", c.code("src/vat.ts")),
        lambda c: (approved_offer(c, "I revoke that, not approved"), "Edit", edit(c))),
    "a later narrowing message": (
        lambda c: (approved_legacy(c, "only change the tests"), "Edit", c.code("src/vat.ts")),
        lambda c: (approved_offer(c, "only change the tests"), "Edit", edit(c))),
    "a qualified yes": (
        lambda c: (c.task(TASK, '- Approval: revision r1 approved by the owner 2026-11-03: "yes but not the database" '
                          '(report `reviews/plan-r1.html`).') and
                   [ROUTER] + c.approval(TASK, "yes but not the database"), "Edit", c.code("src/vat.ts")),
        lambda c: (offered(c, "yes but not the database"), "Edit", edit(c))),
    "/wait-what, then yes without a new presentation": (
        lambda c: (c.task(TASK, APPROVED) and [ROUTER, c.records(TASK), c.present(TASK), user("/wait-what"),
                                                say("In short: one ticket."), user("Yes to both")],
                   "Edit", c.code("src/vat.ts")),
        lambda c: (offered(c, "/wait-what", "agent: In short: one ticket.", "yes"), "Edit", edit(c))),
    "git commit the owner asked for": (
        lambda c: (approved_legacy(c, "commit it"), "Bash", {"command": "git commit -m vat"}),
        lambda c: (approved_offer(c, "commit it"), "Bash", {"command": "git commit -m vat"})),
    "git push nobody approved": (
        lambda c: (approved_legacy(c), "Bash", {"command": "git push"}),
        lambda c: (approved_offer(c), "Bash", {"command": "git push"})),
    "a package install": (
        lambda c: (approved_legacy(c), "Bash", {"command": "npm install left-pad"}),
        lambda c: (approved_offer(c), "Bash", {"command": "npm install left-pad"})),
    "git clean": (
        lambda c: (approved_legacy(c), "Bash", {"command": "git clean -fdx"}),
        lambda c: (approved_offer(c), "Bash", {"command": "git clean -fdx"})),
    "a task record without any approval": (
        lambda c: (c.task(TASK, NOT_APPROVED) and [ROUTER], "Write",
                   {"file_path": str(c.repo / "docs/plans" / TASK / "notes.md"), "content": "x"}),
        lambda c: (new.Rows().router(), "Write", {"file_path": str(c.folder / "notes.md"), "content": "x"})),
    "a session without the workflow": (
        lambda c: ([user("just edit it")], "Edit", c.code("src/vat.ts")),
        lambda c: (plain(), "Edit", edit(c))),
    "inline styling while the CSS switch is off": (
        lambda c: (approved_legacy(c), "Edit", {**c.code("src/vat.ts"), "old_string": "1",
                                                "new_string": "el.style.color = 'red'"}),
        lambda c: (approved_offer(c), "Edit", {**edit(c), "new_string": "el.style.color = 'red'"})),
    "turning the CSS switch on without the owner's Yes": (
        lambda c: (approved_legacy(c), "Bash", {"command": "python settings.py css on"}),
        lambda c: (approved_offer(c), "Bash", {"command": "python settings.py css on"})),
    "a direct write to an offer record": (
        lambda c: (approved_legacy(c), "Write", {"file_path": str(c.repo / "docs/plans" / TASK / "offers/offer-1.json"),
                                                 "content": "{}"}),
        lambda c: (approved_offer(c), "Write", {"file_path": str(c.folder / "offers/offer-1.json"), "content": "{}"})),
    "P1: a report waiver before the plan, then Approve": (
        lambda c: (c.task(TASK, AGREED, NO_REPORT_APPROVAL, report=None) and
                   [ROUTER, c.records(TASK), user("Agree no need for report just docs and agents.md"), chat_plan(TASK),
                    user("Approve")], "Edit", c.code("src/vat.ts")),
        lambda c: (offered(c, "Approve", before=["Agree no need for report just docs and agents.md"]), "Edit",
                   edit(c))),
    "P3: the plan shown without its revision, then 'approve r4, no report'": (
        lambda c: (c.task(TASK, AGREED, "- Plan: r4 proposed", '- Approval (gate two): r4 approved, 2026-11-14, no '
                          'report: "approve r4, no report"', report=None) and
                   [ROUTER, c.records(TASK), chat_plan(TASK, revision=None), user("approve r4, no report")],
                   "Edit", c.code("src/vat.ts")),
        lambda c: (offered(c, "approve r4, no report"), "Edit", edit(c))),
    "N4: a record written to another task before the asked-for commit": (
        lambda c: (c.task(TASK, APPROVED) and c.task(OTHER, APPROVED) and
                   [ROUTER] + c.approval(OTHER) + c.approval(TASK) + [user("commit it"), c.records(OTHER)],
                   "Bash", {"command": "git commit -m vat"}),
        lambda c: (record_write(approved_offer(c, "commit it"), c, OTHER), "Bash", {"command": "git commit -m vat"})),
    "E10: the offer shown as text, then the typed answer 'Approve from this summary'": (
        lambda c: (c.task(TASK, '- Approval: revision r1 approved by the owner 2026-11-19: "Approve from this '
                          'summary" (report `reviews/plan-r1.html`).') and
                   [ROUTER] + c.approval(TASK, "Approve from this summary"), "Edit", c.code("src/vat.ts")),
        lambda c: (offered(c, "Approve from this summary"), "Edit", edit(c))),
}

# (legacy outcome, offer outcome, classification). "same" needs equal outcomes; any other entry names why they differ.
EXPECTED = {
    "approved write inside the scope": ("allow", "allow", "same"),
    "nothing approved": ("deny", "deny", "same"),
    "a file outside the approved scope": ("deny", "deny", "same"),
    "a stop after the approval": ("deny", "deny", "same"),
    "a stop, then continue": ("allow", "allow", "same"),
    "a later withdrawal": ("deny", "deny", "same"),
    "a later narrowing message": ("allow", "deny", "stricter: a message that may narrow an approval suspends it until a "
                                  "narrowed offer is approved (C-OFFER-3)"),
    "a qualified yes": ("allow", "deny", "stricter: a qualified answer never approves; the agent writes the narrowed "
                        "offer and asks once (C-OFFER-3)"),
    "/wait-what, then yes without a new presentation": ("allow", "deny", "stricter: /wait-what is a non-answer and only "
                                                        "a re-presentation can be answered after it (C-OFFER-7)"),
    "git commit the owner asked for": ("allow", "allow", "same"),
    "git push nobody approved": ("allow", "deny", "stricter: a git write needs its exact operation in the approved "
                                 "offer; the plan approval alone allowed a push (C-SAFE-1)"),
    "a package install": ("deny", "deny", "same"),
    "git clean": ("deny", "deny", "same"),
    "a task record without any approval": ("allow", "allow", "same"),
    "a session without the workflow": ("allow", "allow", "same"),
    "inline styling while the CSS switch is off": ("allow", "deny", "added: styling writes need the machine CSS "
                                                   "switch; the old gate only noted them (C-CSS-1)"),
    "turning the CSS switch on without the owner's Yes": ("allow", "deny", "added: the switch is a protected operation "
                                                          "needing a Yes to that exact question (C-CSS-2)"),
    "a direct write to an offer record": ("allow", "deny", "added: offer records change only through record.py, so the "
                                          "hashed fields and the reference can't be hand-edited (C-OFFER-1)"),
    "P1: a report waiver before the plan, then Approve": ("allow", "allow", "same"),
    "P3: the plan shown without its revision, then 'approve r4, no report'": (
        "allow", "deny", "stricter: offers have no revision numbers, and the typed words are a qualified answer, not "
        "one of the fixed forms; the owner answers the one question instead, Approve from this summary (P3, "
        "C-OFFER-3)"),
    "N4: a record written to another task before the asked-for commit": ("allow", "allow", "same"),
    "E10: the offer shown as text, then the typed answer 'Approve from this summary'": ("allow", "allow", "same"),
}


class ShadowComparison(unittest.TestCase):

    def pair(self, name):
        legacy_build, offer_build = SCENARIOS[name]
        legacy, offer = harness(old.GateCase), harness(new.ApprovalHookCase)
        self.addCleanup(legacy.doCleanups)
        self.addCleanup(offer.doCleanups)
        rows, tool, data = legacy_build(legacy)
        out = legacy.fire(rows, tool, data)
        before = "deny" if out and out.get("permissionDecision") == "deny" else "allow"
        rows, tool, data = offer_build(offer)
        after = outcome(offer.run_hook(rows, tool=tool, data=data))
        return before, after

    def test_every_scenario_matches_the_expected_outcome_table(self):
        self.assertEqual(set(SCENARIOS), set(EXPECTED), "every scenario has an expected outcome, and only those")
        for name, (before, after, why) in EXPECTED.items():
            with self.subTest(name):
                actual = self.pair(name)
                if os.environ.get("SHADOW_PRINT"):  # diagnostics only; the checks below still run
                    print(f"{name!r}: {actual}")
                self.assertEqual(actual, (before, after))
                if before == after:
                    self.assertEqual(why, "same")
                else:
                    self.assertRegex(why, r"^(repaired|added|stricter): .*\b(C-[A-Z]+-\d|[PN]\d+)\b",
                                     "a difference names its kind and a contract or finding ID")


if __name__ == "__main__":
    unittest.main()
