"""The approval failures of the owner's real session (2026-11-14, rc.39) and the interim relief of ticket T7.

Ticket T1 of docs/plans/2026-11-15-workflow-redesign added the three reproductions; T7 fixed them in today's gate
(REDESIGN.md §14 checkpoint 3: zero extra owner messages). No private session content is copied: each transcript is
built from the shape of the session's events. Task names and file names are invented. Each relief comes with a guard
test showing what it must not allow.
"""
from __future__ import annotations

import unittest

from test_gate_regressions import GateCase, write_rows
from test_phase_gate_hook import APPROVED, ROUTER, say, user

A, B = "2026-11-14-docs-change", "2026-11-14-other-task"
AGREED = "- Agreement (gate one): agreed 2026-11-14"
NO_REPORT_APPROVAL = '- Approval (gate two): r1 approved, 2026-11-14, no report: "Approve"'


def chat_plan(name, revision="r1"):
    """A plan shown in chat, the way the session's agent did it: the word plan, the task path, the revision."""
    rev = f" {revision}" if revision else ""
    return say(f"**Plan{rev}** for docs/plans/{name}/TODO.md: one ticket, docs and AGENTS.md only. Approve?")


class SessionFailures(GateCase):
    """The three session failures: each must now pass with no further owner message."""

    def test_a_no_report_waiver_given_before_the_plan_counts_for_the_approval(self):
        """P1/P2. Session 00:01-00:25: "Agree no need for report just docs and agents.md", the plan in chat, then
        "Approve". The gate demanded an HTML report; the owner had to answer twice more."""
        self.task(A, AGREED, NO_REPORT_APPROVAL, report=None)
        rows = [ROUTER, self.records(A), user("Agree no need for report just docs and agents.md"),
                chat_plan(A), user("Approve")]
        self.assertIsNone(self.fire(rows, "Edit", self.code("docs/guide.md")))

    def test_a_chat_plan_without_its_revision_number_is_still_the_plan_that_was_approved(self):
        """P3. Session 01:05-01:10: the only pending plan was shown without the literal "r4"."""
        self.task(A, AGREED, "- Plan: r4 proposed", '- Approval (gate two): r4 approved, 2026-11-14, no report: '
                  '"approve r4, no report"', report=None)
        rows = [ROUTER, self.records(A), chat_plan(A, revision=None), user("approve r4, no report")]
        self.assertIsNone(self.fire(rows, "Edit", self.code("docs/guide.md")))

    def test_a_record_written_to_another_task_does_not_change_the_task_a_commit_belongs_to(self):
        """N4. Session 01:34-01:39: after "commit it" for task A, a note was written to task B (already in the
        session), and `git commit` was refused as a task switch."""
        self.task(A, APPROVED)
        self.task(B, APPROVED)
        rows = [ROUTER] + self.approval(B) + self.approval(A) + [user("commit it"), self.records(B)]
        self.assertIsNone(self.fire(rows, "Bash", {"command": "git commit -m docs"}))


class ReliefGuards(GateCase):
    """What each relief must not allow."""

    def test_a_waiver_in_another_tasks_message_does_not_apply(self):
        self.task(A, AGREED, NO_REPORT_APPROVAL, report=None)
        self.task(B, "- Status: other")
        rows = [ROUTER, self.records(B), user("no need for report for this one"), self.records(A),
                chat_plan(A), user("Approve")]
        self.assertEqual(self.decision(rows, "Edit", self.code("docs/guide.md")), "deny")

    def test_a_waiver_sent_before_any_task_applies_only_when_one_task_follows(self):
        self.task(A, AGREED, NO_REPORT_APPROVAL, report=None)
        self.task(B, "- Status: other")
        early = [ROUTER, user("no need for report")]
        one = early + [self.records(A), chat_plan(A), user("Approve")]
        self.assertIsNone(self.fire(one, "Edit", self.code("docs/guide.md")))
        two = early + [self.records(B), self.records(A), chat_plan(A), user("Approve")]
        self.assertEqual(self.decision(two, "Edit", self.code("docs/guide.md")), "deny")

    def test_declining_a_code_review_is_not_a_report_waiver(self):
        self.task(A, AGREED, NO_REPORT_APPROVAL, report=None)
        rows = [ROUTER, self.records(A), user("no code review needed"), chat_plan(A), user("Approve")]
        self.assertEqual(self.decision(rows, "Edit", self.code("docs/guide.md")), "deny")

    def test_the_waiver_still_needs_a_real_answer_after_the_plan(self):
        self.task(A, AGREED, NO_REPORT_APPROVAL, report=None)
        rows = [ROUTER, self.records(A), user("Approve"), user("no need for report"), chat_plan(A)]
        self.assertEqual(self.decision(rows, "Edit", self.code("docs/guide.md")), "deny")

    def test_an_unnumbered_plan_does_not_count_when_the_task_has_several_revisions(self):
        """P3 guard and N1: with r3 and r4 in the checkpoint, the gate can't tell which plan was shown, and says so."""
        self.task(A, AGREED, "- Plan: r3 superseded, r4 proposed", '- Approval (gate two): r4 approved, 2026-11-14, '
                  'no report: "approve r4, no report"', report=None)
        rows = [ROUTER, self.records(A), chat_plan(A, revision=None), user("approve r4, no report")]
        out = self.fire(rows, "Edit", self.code("docs/guide.md"))
        self.assertEqual(out and out["permissionDecision"], "deny")
        self.assertIn("named no revision", out["permissionDecisionReason"])
        self.assertIn("r4", out["permissionDecisionReason"])

    def test_a_task_first_recorded_after_the_owners_message_still_stops_git(self):
        """N4 guard: new work started after the owner's last message is not judged by the earlier task."""
        self.task(A, APPROVED)
        self.task(B, "- Approval: not approved; revision r1 proposed")
        rows = [ROUTER] + self.approval(A) + [user("now also add an export button"), self.records(B)]
        self.assertEqual(self.decision(rows, "Bash", {"command": "git commit -m x"}), "deny")

    def test_a_file_write_after_a_note_to_another_task_keeps_the_stop(self):
        """N4 guard: only git writes follow the task at the owner's message; a file write could belong to the note's
        task."""
        self.task(A, APPROVED)
        self.task(B, APPROVED)
        rows = [ROUTER] + self.approval(B) + self.approval(A) + [user("go on"), self.records(B)]
        out = self.fire(rows, "Edit", self.code("src/a.ts"))
        self.assertEqual(out and out["permissionDecision"], "deny")
        self.assertIn(f"changed to {B}", out["permissionDecisionReason"])


class SmallChangeRelief(GateCase):
    """P5 (a small change asked again in every session) and P10 (no regression test file in a small change)."""

    SMALL_YES = '- Approval: small change approved 2026-11-14: "yes, go ahead"'

    def setUp(self):
        super().setUp()
        for name in ("src/a.ts", "tests/.keep"):
            (self.repo / name).parent.mkdir(parents=True, exist_ok=True)
            (self.repo / name).write_text("x\n", encoding="utf-8")

    def offer(self, files):
        return say(f"Here is the change.\n\nSmall change: {files} — fix the VAT label\n\nApprove?")

    def line(self, files):
        self.task(A, f"- Small change: {files} — fix the VAT label", self.SMALL_YES, report=None)

    def test_a_small_change_approved_in_an_earlier_session_carries_over(self):
        self.line("src/a.ts")
        write_rows(self.sessions / "earlier.jsonl", [ROUTER, self.records(A), self.offer("src/a.ts"), user("yes, go ahead")])
        self.assertIsNone(self.fire([ROUTER, self.records(A)], "Edit", self.code("src/a.ts")))

    def test_a_withdrawal_in_the_earlier_session_still_stops_it(self):
        self.line("src/a.ts")
        write_rows(self.sessions / "earlier.jsonl", [ROUTER, self.records(A), self.offer("src/a.ts"),
                                                     user("yes, go ahead"), user("I revoke that, not approved")])
        self.assertEqual(self.decision([ROUTER, self.records(A)], "Edit", self.code("src/a.ts")), "deny")

    def test_an_earlier_yes_to_a_different_file_list_does_not_carry_over(self):
        self.line("src/a.ts")
        write_rows(self.sessions / "earlier.jsonl", [ROUTER, self.records(A), self.offer("src/b.ts"), user("yes, go ahead")])
        self.assertEqual(self.decision([ROUTER, self.records(A)], "Edit", self.code("src/a.ts")), "deny")

    def test_an_earlier_offer_in_another_checkout_does_not_carry_over(self):
        self.line("src/a.ts")
        other = self.base / "other-checkout"
        (other / ".git").mkdir(parents=True)
        offer = dict(self.offer("src/a.ts"), cwd=str(other))  # the same task name and files, shown in another checkout
        write_rows(self.sessions / "earlier.jsonl", [ROUTER, self.records(A), offer, user("yes, go ahead")])
        self.assertEqual(self.decision([ROUTER, self.records(A)], "Edit", self.code("src/a.ts")), "deny")

    def test_a_yes_given_after_switching_to_another_task_does_not_approve_the_offer(self):
        self.line("src/a.ts")
        self.task(B, "- Status: other")
        rows = [ROUTER, self.records(A), self.offer("src/a.ts"), self.records(B), user("yes, go ahead"), self.records(A)]
        self.assertEqual(self.decision(rows, "Edit", self.code("src/a.ts")), "deny")
        write_rows(self.sessions / "earlier.jsonl", rows)  # the same through an earlier session
        self.assertEqual(self.decision([ROUTER, self.records(A)], "Edit", self.code("src/a.ts")), "deny")

    def test_a_small_change_may_add_its_listed_new_test_file(self):
        self.line("src/a.ts, tests/vat.test.ts")
        rows = [ROUTER, self.records(A), self.offer("src/a.ts, tests/vat.test.ts"), user("yes, go ahead")]
        self.assertIsNone(self.fire(rows, "Write", self.code("tests/vat.test.ts")))
        self.assertIsNone(self.fire(rows, "Edit", self.code("src/a.ts")))

    def test_a_small_change_still_adds_no_other_new_file(self):
        self.line("src/a.ts, src/new.ts")  # not a test file and not existing: the line is invalid, so no small route
        rows = [ROUTER, self.records(A), self.offer("src/a.ts, src/new.ts"), user("yes, go ahead")]
        self.assertEqual(self.decision(rows, "Write", self.code("src/new.ts")), "deny")
        self.line("src/a.ts, tests/vat.test.ts")
        rows = [ROUTER, self.records(A), self.offer("src/a.ts, tests/vat.test.ts"), user("yes, go ahead")]
        self.assertEqual(self.decision(rows, "Write", self.code("tests/other.test.ts")), "deny")  # not listed


if __name__ == "__main__":
    unittest.main()
