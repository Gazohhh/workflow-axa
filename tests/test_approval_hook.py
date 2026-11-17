"""hooks/approval.py, the offer checker (T14 of docs/plans/2026-11-15-workflow-redesign; contracts C-OFFER-2..7,
C-CSS-1/2, C-SAFE-1). Each test runs the hook as a process on a synthetic transcript, as the gate tests do."""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import datetime as dt
import itertools
import tempfile
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOOK = ROOT / "hooks/approval.py"
spec = importlib.util.spec_from_file_location("workflow_axa_offers", ROOT / "skills/workflow/scripts/offers.py")
offers = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = offers
spec.loader.exec_module(offers)
CACHE = tempfile.TemporaryDirectory()
TASK = "2026-11-15-vat"
OFFER = {"behaviour": "Round VAT per line", "paths": ["src/vat.ts", "tests/vat.spec.ts", "src/styles/"],
         "operations": ["git commit"], "checks": ["npm test"]}


def load_hook():
    """The hook as a module, for the pure functions (decide, fold) and main()."""
    spec = importlib.util.spec_from_file_location("approval_under_test", HOOK)
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module  # its dataclasses look their module up while it loads
    spec.loader.exec_module(module)
    return module


def tearDownModule():
    CACHE.cleanup()


START = time.time() + 600  # transcript times run a little ahead of the files' real change times
CLOCK = itertools.count()


def stamp(seconds: float) -> str:
    return dt.datetime.fromtimestamp(seconds, dt.timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


class Rows:
    """Transcript rows with stable uuids and host timestamps that keep rising across sessions."""

    def __init__(self):
        self.n = 0
        self.rows = []

    def uid(self):
        self.n += 1
        return f"u{self.n}"

    def append(self, row):
        row["timestamp"] = stamp(START + next(CLOCK))
        self.rows.append(row)

    def router(self):
        self.append({"type": "user", "uuid": self.uid(), "message": {"role": "user", "content": "/workflow-axa:workflow fix vat"}})
        return self

    def say(self, text):
        self.append({"type": "assistant", "uuid": self.uid(), "message": {"content": [{"type": "text", "text": text}]}})
        return self

    def owner(self, text):
        self.append({"type": "user", "uuid": self.uid(), "message": {"role": "user", "content": text}})
        return self.rows[-1]["uuid"]

    def ask(self, question, options):
        tool_id = f"q{self.n}"
        self.append({"type": "assistant", "uuid": self.uid(), "message": {"content": [{"type": "tool_use",
                          "id": tool_id, "name": "AskUserQuestion", "input": {"questions": [{"question": question,
                          "options": [{"label": o} for o in options]}]}}]}})
        return tool_id

    def answer(self, tool_id, question, value):
        self.append({"type": "user", "uuid": self.uid(), "toolUseResult": {"answers": {question: value}},
                          "message": {"role": "user", "content": [{"type": "tool_result", "tool_use_id": tool_id,
                                                                    "content": value}]}})

    def edit(self, file_path: str):
        """The agent edits a file (for example another task's record)."""
        self.append({"type": "assistant", "uuid": self.uid(), "message": {"content": [{"type": "tool_use",
                     "id": f"e{self.n}", "name": "Edit", "input": {"file_path": file_path, "old_string": "a",
                                                                    "new_string": "b"}}]}})

    def write(self, path: Path):
        path.write_text("\n".join(json.dumps(r) for r in self.rows), encoding="utf-8")


class ApprovalHookCase(unittest.TestCase):

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.base = Path(tmp.name)
        self.repo = self.base / "repo"
        (self.repo / ".git").mkdir(parents=True)
        (self.repo / "src/styles").mkdir(parents=True)
        (self.repo / "src/vat.ts").write_text("export const vat = 1;\n", encoding="utf-8")
        self.folder = self.repo / "docs/plans" / TASK
        self.folder.mkdir(parents=True)
        (self.folder / "PLAN.md").write_text("# VAT\n\n## Current checkpoint\n- Status: x\n", encoding="utf-8")
        self.sessions = self.base / "sessions"
        self.sessions.mkdir()
        self.path = self.sessions / "s-now.jsonl"
        self.settings = self.base / "settings.json"
        self.offer = self.recorded_as(offers.create(self.folder, OFFER), format_1=True)
        self.cache = CACHE.name

    def recorded_as(self, offer, format_1, folder=None):
        """Most cases here keep testing an offer recorded before format 2, whose format 1 block still counts."""
        path = (folder or self.folder) / "offers" / f"offer-{offer['id']}.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        data.pop("presentation_format", None) if format_1 else data.update(presentation_format=2)
        path.write_text(json.dumps(data, indent=2), encoding="utf-8")
        return data

    def rendering(self, offer=None):
        return offers.rendering(offer or offers.load(self.folder, self.offer["id"]), self.folder)

    def readable_question(self):
        return offers.presentation(offers.load(self.folder, self.offer["id"]), self.folder, question=True)

    def presented(self, rows=None, offer=None):
        rows = rows or Rows().router()
        offer = offer or offers.load(self.folder, self.offer["id"])
        if offer.get("presentation_format", 1) != 1:
            rows.say("Here is the offer.\n\n" + offers.presentation(offer, self.folder))
            return rows
        rows.say("Here is the offer:\n\n```\n" + self.rendering(offer) + "\n```\n\nShow review.html first · Approve "
                 "from this summary · Change something?")
        return rows

    def event(self, rows: Rows, tool="Edit", data=None, path=None):
        target = path or self.path
        rows.write(target)
        return {"hook_event_name": "PreToolUse", "tool_name": tool,
                "tool_input": data if data is not None else {"file_path": str(self.repo / "src/vat.ts"),
                                                             "old_string": "1", "new_string": "2"},
                "cwd": str(self.repo), "transcript_path": str(target)}

    def start(self, event: dict) -> subprocess.Popen:
        process = subprocess.Popen([sys.executable, "-X", "utf8", "-I", str(HOOK)], stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8",
                                   env={**os.environ, "WORKFLOW_AXA_GATE_CACHE": self.cache,
                                        "WORKFLOW_AXA_SETTINGS": str(self.settings),
                                        "WORKFLOW_AXA_HOME": str(self.base / "axa-home")})
        process.stdin.write(json.dumps(event))
        process.stdin.close()
        return process

    def finish(self, process: subprocess.Popen):
        with process:
            out, err = process.stdout.read(), process.stderr.read()
        self.assertEqual(process.returncode, 0, err)
        return json.loads(out)["hookSpecificOutput"]["permissionDecisionReason"] if out.strip() else None

    def run_hook(self, rows: Rows, **kwargs):
        return self.finish(self.start(self.event(rows, **kwargs)))

    def allowed(self, rows, **kwargs):
        self.assertIsNone(self.run_hook(rows, **kwargs))

    def denied(self, rows, *fragments, **kwargs):
        reason = self.run_hook(rows, **kwargs)
        self.assertIsNotNone(reason, "expected a refusal")
        for fragment in fragments:
            self.assertIn(fragment, reason)
        return reason


class PresentationAndAnswers(ApprovalHookCase):
    """C-OFFER-2, -3, -4: presentation is the exact rendering; the answer forms are closed."""

    def test_without_any_offer_the_refusal_says_how_to_create_one(self):
        # T26 F2 (live run r20): the agent wrote an offer in its own words. The refusal is what every agent sees, so
        # it names the way to create a real offer, not only how to present one.
        import shutil
        shutil.rmtree(self.folder / "offers")
        rows = Rows().router()
        rows.say("Offer: change src/vat.ts. Go ahead with this?")
        rows.owner("yes")
        self.denied(rows, "This project has no offers yet.", "Create one through `workflow-specify` step 5",
                    "`record.py offer create`", "the one question", "An offer in your own words can't be approved")

    def test_a_shown_offer_and_a_plain_yes_allow_only_the_files_it_lists(self):
        rows = self.presented()
        rows.owner("yes")
        self.allowed(rows)
        self.denied(rows, "needs an approved offer that lists src/other.ts",
                    data={"file_path": str(self.repo / "src/other.ts"), "old_string": "a", "new_string": "b"})

    def test_every_fixed_approval_word_counts_and_nothing_else_does(self):
        for word in ("Approve", "approved.", "OK", "go", "ja", "akkoord", "doe maar", "**yes**"):
            with self.subTest(word=word):
                rows = self.presented()
                rows.owner(word)
                self.allowed(rows)
        for word in ("yes but don't touch the database", "approve both", "sounds good", "do it later"):
            with self.subTest(word=word):
                rows = self.presented()
                rows.owner(word)
                self.denied(rows, "not one of the approval forms")

    def test_show_report_typed_or_a_recommended_button_means_the_same_as_its_plain_form(self):
        for typed in ("show report", "Show report.", "**show report**", "show the report"):
            with self.subTest(typed=typed):
                rows = self.presented()
                rows.owner(typed)
                rows.owner("yes")
                self.denied(rows, "the owner asked to see review.html first")
        question = "Offer:\n" + self.rendering()
        for button, allowed in (("Show review.html first (Recommended)", False),
                                ("Approve from this summary (Recommended)", True)):
            with self.subTest(button=button):
                rows = Rows().router()
                tool = rows.ask(question, [button, "Change something"])
                rows.answer(tool, question, button)
                self.allowed(rows) if allowed else self.denied(rows, "the owner asked to see review.html first")

    def test_an_edited_or_partial_block_is_no_presentation(self):
        rows = Rows().router().say(self.rendering().replace("Round VAT per line", "Round VAT per invoice"))
        rows.owner("yes")
        self.denied(rows)
        rows = Rows().router().say(self.rendering().split("\n", 3)[3])  # the header is missing
        rows.owner("yes")
        self.denied(rows)

    def test_the_answer_must_come_after_the_presentation(self):
        rows = Rows().router()
        rows.owner("yes")
        self.presented(rows)
        self.denied(rows, "no owner answer came after it")

    def test_slash_approve_names_the_offer(self):
        rows = self.presented()
        rows.owner(f"/approve {self.offer['id']}")
        self.allowed(rows)
        rows = self.presented()
        rows.owner(f"/approve {self.offer['id'] + 5}")
        self.denied(rows)

    def test_report_first_then_the_question_again(self):
        rows = self.presented()
        rows.owner(f"/report {self.offer['id']}")
        self.denied(rows, "review.html first")
        self.presented(rows)
        rows.owner("approve")
        self.denied(rows, "show the report, then ask again")  # re-asked without showing the report
        (self.folder / "reviews").mkdir()
        (self.folder / "reviews/plan-r1.html").write_text("<!DOCTYPE html>", encoding="utf-8")
        rows.say(f"Report: docs/plans/{TASK}/reviews/plan-r1.html")
        self.presented(rows)
        rows.owner("approve")
        self.allowed(rows)
        rows = self.presented()
        rows.owner(f"/report {self.offer['id']}")
        self.presented(rows)
        rows.owner(f"/approve {self.offer['id']}")  # an approval form is no change of the presentation choice
        self.denied(rows, "show the report, then ask again")

    def test_the_question_tool_carries_presentation_and_answer(self):
        rows = Rows().router()
        question = "Offer:\n" + self.rendering() + "\nHow do you want to decide?"
        tool = rows.ask(question, ["Show review.html first", "Approve from this summary", "Change something"])
        rows.answer(tool, question, "Approve from this summary")
        self.allowed(rows)

    def test_an_answer_keyed_without_the_questions_surrounding_whitespace_still_counts(self):
        for asked in ("Offer:\n" + self.rendering() + "\n", "\n  Offer:\n" + self.rendering() + " \r\n"):
            with self.subTest(asked=repr(asked[-6:])):
                rows = Rows().router()
                tool = rows.ask(asked, ["Show review.html first", "Approve from this summary", "Change something"])
                rows.answer(tool, asked.strip(), "Approve from this summary (Recommended)")
                self.allowed(rows)

    def test_an_answer_keyed_by_any_other_text_still_counts_for_nothing(self):
        asked = "Offer:\n" + self.rendering() + "\n"
        for key in (asked.strip() + ".", asked.strip().replace("Offer:", "Offer: "), asked.strip()[:-1]):
            with self.subTest(key=repr(key[-6:])):
                rows = Rows().router()
                tool = rows.ask(asked, ["Show review.html first", "Approve from this summary", "Change something"])
                rows.answer(tool, key, "Approve from this summary")
                self.denied(rows)
        with self.subTest("two keys that differ only in surrounding whitespace: ambiguous, so nothing"):
            rows = Rows().router()
            tool = rows.ask(asked, ["Show review.html first", "Approve from this summary", "Change something"])
            rows.answer(tool, asked, "Approve from this summary")
            rows.rows[-1]["toolUseResult"]["answers"][asked.strip()] = "Change something"
            self.denied(rows)
        with self.subTest("two asked questions that differ only in surrounding whitespace, one answer: nothing"):
            rows = Rows().router()
            tool = rows.ask(asked, ["Show review.html first", "Approve from this summary", "Change something"])
            rows.rows[-1]["message"]["content"][0]["input"]["questions"].append(
                {"question": asked.strip(), "options": [{"label": "Approve from this summary"}]})
            rows.answer(tool, asked.strip(), "Approve from this summary")
            self.denied(rows)
        with self.subTest("the same, while a stop pauses the session"):
            rows = Rows().router()
            rows.owner("Do not implement until I approve the plan.")
            tool = rows.ask(asked, ["Approve from this summary", "Change something"])
            rows.rows[-1]["message"]["content"][0]["input"]["questions"].append(
                {"question": asked.strip(), "options": [{"label": "Approve from this summary"}]})
            rows.answer(tool, asked.strip(), "Approve from this summary")
            self.denied(rows)

    def test_a_question_answered_with_the_report_then_approve(self):
        rows = Rows().router()
        question = "Offer:\n" + self.rendering()
        tool = rows.ask(question, ["Show review.html first", "Approve from this summary", "Change something"])
        rows.answer(tool, question, "Show review.html first")
        self.denied(rows, "review.html first")
        (self.folder / "plan-r1.html").write_text("<!DOCTYPE html>", encoding="utf-8")
        rows.say(f"Here it is: docs/plans/{TASK}/plan-r1.html")
        again = rows.ask(question + "\n(report shown)", ["Approve", "Change something"])
        rows.answer(again, question + "\n(report shown)", "Approve")
        self.allowed(rows)

    def test_an_answer_counts_only_for_the_question_that_carried_the_offer(self):
        rows = Rows().router()
        offer_q, other_q = "Offer:\n" + self.rendering(), "Shall I also update the docs?"
        tool = rows.ask(offer_q, ["Approve from this summary", "Change something"])
        rows.rows[-1]["message"]["content"][0]["input"]["questions"].append({"question": other_q, "options": []})
        rows.answer(tool, offer_q, "Change something")
        rows.rows[-1]["toolUseResult"]["answers"][other_q] = "Approve"
        self.denied(rows, "not an approval")

    def test_identical_offers_in_another_task_or_checkout_never_share_consent(self):
        other = self.repo / "docs/plans/2026-11-15-other"
        other.mkdir()
        twin = offers.create(other, OFFER)  # same id, fields and hash, another task
        self.assertEqual(twin["hash"], self.offer["hash"])
        rows = Rows().router().say(offers.rendering(twin, other))
        rows.owner("yes")
        offers.revoke(other, twin["id"])  # without the twin's own approval, only this task's offer could authorise
        self.denied(rows, "2026-11-15-vat): it was never presented")
        copy = self.base / "copy/docs/plans" / TASK
        copy.mkdir(parents=True)
        rows = Rows().router().say(offers.rendering(offers.create(copy, OFFER), copy))  # same task name, other checkout
        rows.owner("yes")
        self.denied(rows)

    def test_an_unanswered_or_cancelled_question_is_not_approval(self):
        rows = Rows().router()
        rows.ask("Offer:\n" + self.rendering(), ["Approve from this summary"])
        self.denied(rows, "has no answer yet")

    def test_wait_what_neither_approves_nor_lets_the_next_yes_count_without_a_new_presentation(self):
        rows = self.presented()
        rows.owner("/wait-what")
        rows.say("In short: ...")
        rows.owner("yes")
        self.denied(rows)
        rows = self.presented()
        rows.owner("<command-name>/wait-what</command-name>")
        self.presented(rows)  # the re-explanation ends with the unchanged offer
        rows.owner("yes")
        self.allowed(rows)


class FormatTwoPresentation(ApprovalHookCase):
    """The readable presentation counts only as the generated text, at the end of the message, with nothing that can
    hide it before it; format 1 keeps counting for the same offer."""

    def setUp(self):
        super().setUp()
        self.offer = self.recorded_as(self.offer, format_1=False)

    def readable(self, question=False):
        return offers.presentation(offers.load(self.folder, self.offer["id"]), self.folder, question=question)

    def test_the_readable_message_with_context_above_it_and_a_yes_approves(self):
        for prefix in ("", "CSS: off (machine setting; display only)\n\n",
                       "Revision 6 is unchanged. Agreement 9 is still open; answer it separately.\n\n"):
            with self.subTest(prefix=prefix):
                rows = Rows().router().say(prefix + self.readable() + "\n")
                rows.owner("/approve 1")
                self.allowed(rows)

    def test_anything_that_could_hide_or_contradict_it_is_no_presentation(self):
        for message in ("<!--\n\n" + self.readable() + "\n-->", "<details>\n\n" + self.readable(),
                        "```\n" + self.readable() + "\n```", "Context\n\n```\nold\n```\n\n" + self.readable(),
                        self.readable() + "\n\nActually this also deletes the database.",
                        "Inline " + self.readable(),
                        self.readable().replace("- `git commit`", "- `git status`"), self.readable(question=True)):
            with self.subTest(message=message[:40]):
                rows = Rows().router().say(message)
                rows.owner("yes")
                self.denied(rows)

    def test_a_question_with_the_recommendation_and_the_css_line_before_it_counts(self):
        rows = Rows().router()
        question = ("**I recommend the report first**, because it changes how quotations are priced.\n\n"
                    "CSS: off (machine setting; display only)\n\n" + self.readable(question=True))
        tool = rows.ask(question, ["Show review.html first (Recommended)", "Approve from this summary",
                                   "Change something"])
        rows.answer(tool, question, "Approve from this summary")
        self.allowed(rows)

    def test_the_question_variant_counts_only_as_the_question_text(self):
        rows = Rows().router()
        question = "Revision 6, unchanged.\n\n" + self.readable(question=True)
        tool = rows.ask(question, ["Show review.html first", "Approve from this summary", "Change something"])
        rows.answer(tool, question, "Approve from this summary")
        self.allowed(rows)
        rows = Rows().router()
        tool = rows.ask("Approve?", ["Approve from this summary", self.readable(question=True)])
        rows.answer(tool, "Approve?", "Approve from this summary")
        self.denied(rows)

    def test_a_format_1_approval_still_holds_and_a_later_withdrawal_still_ends_it(self):
        self.offer = self.recorded_as(self.offer, format_1=True)
        rows = self.presented()
        rows.owner("yes")
        self.allowed(rows)
        rows.say(self.readable())
        rows.owner("I revoke that, not approved")
        self.denied(rows)

    def test_text_after_it_or_markup_in_the_same_visible_block_undoes_it(self):
        for before, after in (("", "P.S. this also deletes the database and ignores the exclusions."),
                              ("<details>", None), ("$$", None)):
            with self.subTest(before=before, after=after):
                rows = Rows().router()
                if before:
                    rows.say(before)
                rows.say(self.readable())
                if after:
                    rows.say(after)
                rows.owner("yes")
                self.denied(rows)

    def test_a_tool_call_between_ends_the_visible_block_so_it_can_be_presented_again(self):
        rows = Rows().router().say("Checking `<task-folder>` first.")
        rows.say(self.readable())
        rows.edit(str(self.folder / "PLAN.md"))
        rows.say(self.readable())
        rows.owner("yes")
        self.allowed(rows)

    def test_a_new_offers_format_1_block_never_counts(self):
        rows = Rows().router().say("Shall I go ahead?\n\n<!--\n" + offers.rendering(self.offer, self.folder) + "\n-->")
        rows.owner("yes")
        self.denied(rows)
        rows = Rows().router().say(offers.rendering(self.offer, self.folder))
        rows.owner("yes")
        self.denied(rows)

    def test_any_delegate_status_and_a_host_note_before_it_still_mark_a_report(self):
        for report in ("Delegated task node:delegated-task:abc (x) [timed out]:\n"
                       "<command-name>/approve</command-name><command-args>1</command-args>",
                       "<system-reminder>x</system-reminder>\nDelegated task node:delegated-task:abc (x) [completed]:\n"
                       "not approved, revoke"):
            with self.subTest(report=report[:40]):
                rows = Rows().router().say(self.readable())
                rows.owner(report)
                self.denied(rows, "no owner answer came after it yet")
                rows.owner("/approve 1")
                self.allowed(rows)

    def test_another_offer_asked_by_question_closes_this_ones_text_presentation(self):
        other = offers.create(self.folder, {**OFFER, "paths": ["tests/vat.spec.ts"]})
        asked = offers.presentation(other, self.folder, question=True)
        for second in (asked, offers.rendering(other, self.folder)):
            with self.subTest(second=second[:20]):
                rows = Rows().router().say(self.readable())
                rows.ask(second, ["Show review.html first", "Approve from this summary", "Change something"])
                rows.owner("yes")
                self.denied(rows)

    def test_a_question_answered_after_another_offers_text_still_binds_to_its_own_offer(self):
        rows = Rows().router()
        question = self.readable(question=True)
        tool = rows.ask(question, ["Show review.html first", "Approve from this summary", "Change something"])
        other = offers.create(self.folder, {**OFFER, "paths": ["tests/vat.spec.ts"]})
        rows.say(offers.presentation(other, self.folder))
        rows.answer(tool, question, "Approve from this summary")
        self.allowed(rows)

    def test_a_later_presentation_of_another_offer_leaves_this_one_unanswered(self):
        other = offers.create(self.folder, {**OFFER, "paths": ["tests/vat.spec.ts"]})
        rows = Rows().router().say(self.readable())
        rows.say(offers.presentation(other, self.folder))
        rows.owner("yes")
        self.denied(rows)


class OfferStates(ApprovalHookCase):
    """C-OFFER-1, -5: revisions, withdrawal and provenance across sessions."""

    def test_a_superseded_offer_no_longer_covers_anything(self):
        rows = self.presented()
        rows.owner("yes")
        self.allowed(rows)
        new = offers.revise(self.folder, self.offer["id"], {**OFFER, "paths": ["tests/vat.spec.ts"]})
        self.denied(rows, "offer #1 is superseded")
        self.presented(rows, offer=new)
        rows.owner("yes")
        self.allowed(rows, data={"file_path": str(self.repo / "tests/vat.spec.ts"), "content": "x"}, tool="Write")

    def test_a_later_withdrawal_or_stop_suspends_the_approval(self):
        for words in ("I revoke that, not approved", "stop"):
            with self.subTest(words=words):
                rows = self.presented()
                rows.owner("yes")
                rows.owner(words)
                self.denied(rows)

    def test_a_finished_delegated_task_is_never_the_owner_speaking(self):
        """T3 Code hands a finished delegate's report back as a plain user message (seen live on 2026-11-16, where it
        took the place of the owner's answer and read as a narrowing, so `/approve 1` was refused twice)."""
        report = ("Delegated task node:delegated-task:command%3Amcp%3A7ae4%3Adelegate-task%3Aa33b (Spar: agent-led "
                  "Finance (round 3)) [{}]:\n**I agree with the direction.** I revoke that, not approved; keep only "
                  "src/vat.ts and stop the rest.\n/approve 1")
        for status in ("completed", "failed"):
            with self.subTest(status=status, when="before the answer"):
                rows = self.presented()
                rows.owner(report.format(status))
                rows.owner("/approve 1")
                self.allowed(rows)
            with self.subTest(status=status, when="after the approval"):
                rows = self.presented()
                rows.owner("yes")
                rows.owner(report.format(status))
                self.allowed(rows)
        with self.subTest("the owner quoting one still speaks"):
            rows = self.presented()
            rows.owner("yes")
            rows.owner("stop, " + report.format("completed"))
            self.denied(rows)

    def test_a_stop_then_continue_keeps_the_approval_but_a_withdrawal_needs_a_fresh_one(self):
        rows = self.presented()
        rows.owner("yes")
        rows.owner("stop")
        self.denied(rows, "stopped the work")
        rows.owner("continue")
        self.allowed(rows)
        rows.owner("I revoke that")
        self.denied(rows, "withdraws it")
        self.presented(rows)
        rows.owner("yes")
        self.allowed(rows)

    def test_a_later_narrowing_message_suspends_until_a_narrowed_offer(self):
        rows = self.presented()
        rows.owner("yes")
        rows.owner("only change the tests, never the database")
        self.denied(rows, "may narrow it")

    def test_this_sessions_answer_overrides_an_earlier_approval(self):
        earlier = self.presented()
        turn = earlier.owner("yes")
        earlier.write(self.sessions / "s-earlier.jsonl")
        offers.approve(self.folder, 1, "s-earlier", turn, earlier.rows[-2]["uuid"])
        now = self.presented()
        now.owner("Show review.html first")
        self.denied(now, "review.html first")

    def test_an_earlier_sessions_approval_holds_through_its_decision_reference(self):
        earlier = self.presented()
        turn = earlier.owner("yes")
        earlier.write(self.sessions / "s-earlier.jsonl")
        offers.approve(self.folder, 1, "s-earlier", turn, earlier.rows[-2]["uuid"])
        self.allowed(Rows().router())  # a new session: the reference re-checks in s-earlier

    def earlier_approval(self, stem="s-earlier", then=()):
        earlier = self.presented()
        turn = earlier.owner("yes")
        presentation = earlier.rows[-2]["uuid"]
        for text in then:
            earlier.owner(text)
        earlier.write(self.sessions / f"{stem}.jsonl")
        offers.approve(self.folder, 1, stem, turn, presentation)

    def test_this_sessions_withdrawal_or_narrowing_ends_a_resumed_approval(self):
        self.earlier_approval()
        rows = Rows().router()
        self.allowed(rows)
        rows.owner("I revoke that")
        self.denied(rows, "withdraws it")
        rows = Rows().router()
        rows.owner("only change the tests")
        self.denied(rows, "may narrow it")

    def test_an_earlier_unresumed_stop_holds_until_the_owner_continues(self):
        self.earlier_approval(then=("stop",))
        rows = Rows().router()
        self.denied(rows, "stopped the work in an earlier session")
        rows.owner("continue")
        self.allowed(rows)

    def session(self, stem, *messages, task=TASK):
        """Another session of the project in which nothing was written: no hook ever ran there. It works on `task`."""
        rows = Rows().router()
        rows.owner(f"pick up docs/plans/{task}")  # the owner names the task: a trusted task transition
        for text in messages:
            rows.owner(text)
        rows.write(self.sessions / f"{stem}.jsonl")
        return rows

    def test_a_session_between_that_withdrew_or_narrowed_counts_without_any_record(self):
        for words, why in (("I revoke that", "withdraws it"), ("only change the tests", "may narrow it")):
            with self.subTest(words=words):
                self.setUp()
                self.earlier_approval()
                self.session("s-between", words)
                self.denied(Rows().router(), why)

    def test_messages_in_a_session_about_other_work_never_touch_the_offer(self):
        self.earlier_approval()
        self.session("s-other", "only update the README", "stop", task="2026-11-16-readme")
        unrelated = Rows().router()
        unrelated.owner("I revoke that")  # before this other session ever names the task
        unrelated.say(f"Now docs/plans/{TASK}")
        unrelated.write(self.sessions / "s-later-mention.jsonl")
        self.allowed(Rows().router())

    def test_switching_to_another_task_ends_what_messages_can_touch(self):
        self.earlier_approval()
        self.session("s-switched", "now work on docs/plans/2026-11-16-readme", "only update the README",
                                "stop")
        self.allowed(Rows().router())  # the narrowing and stop were about the other task
        rows = self.presented()  # the current session: on this task, then on another one
        rows.owner("yes")
        rows.owner("now work on docs/plans/2026-11-16-readme")
        rows.owner("only update the README")
        self.allowed(rows)
        rows.owner(f"back to docs/plans/{TASK}")
        rows.owner("only change the tests")
        self.denied(rows, "may narrow it")

    def test_a_record_write_to_another_task_never_moves_the_owners_withdrawal(self):
        # REDESIGN §3.4 (N4), T24: the agent's bookkeeping must not decide which offer the owner's words apply to.
        # Before T24 the write below made the session "on" the other task, so the withdrawal was ignored.
        rows = self.presented()
        rows.owner("yes")
        self.allowed(rows)
        rows.edit(str(self.repo / "docs/plans/2026-11-16-readme/PLAN.md"))
        rows.owner("I revoke that")
        self.denied(rows, "withdraws it")

    def test_a_record_write_in_another_session_never_moves_its_stop(self):
        # Astra (T24 plan): across sessions too, so the session-wide stop of the current session can't mask it.
        self.earlier_approval()
        other = Rows().router()
        other.owner(f"pick up docs/plans/{TASK}")
        other.edit(str(self.repo / "docs/plans/2026-11-16-readme/PLAN.md"))
        other.owner("stop")
        other.write(self.sessions / "s-other.jsonl")
        self.denied(Rows().router(), "stopped the work in an earlier session")

    def test_a_made_up_or_hidden_footer_never_moves_a_session_away_from_its_withdrawal(self):
        real = offers.presentation(offers.load(self.folder, 1), self.folder)
        made_up = "`Offer #9 · 0123456789abcdef · task nonexistent · D:/elsewhere`"
        for say in ("Notes\n\n" + made_up, "<!--\n\n" + real + "\n\n" + made_up, "<!--\n\n" + real):
            with self.subTest(say=say[:30]):
                self.setUp()
                self.earlier_approval(then=())
                earlier = Rows().router()
                earlier.owner(f"pick up docs/plans/{TASK}")
                earlier.say(say)
                earlier.owner("I revoke that, not approved")
                earlier.write(self.sessions / "s-between.jsonl")
                self.denied(Rows().router(), "withdraws it")

    def test_another_tasks_offer_hidden_in_the_visible_block_never_moves_the_session(self):
        other = self.repo / "docs/plans/2026-11-16-readme"
        other.mkdir(parents=True)
        new = offers.create(other, {**OFFER, "paths": ["README.md"]})
        old = self.recorded_as(offers.create(other, {**OFFER, "paths": ["CHANGES.md"]}), format_1=True, folder=other)
        for hidden in (offers.presentation(new, other), offers.rendering(new, other)):
            with self.subTest(hidden=hidden[:20]):
                rows = self.presented()
                rows.owner("yes")
                rows.say("<details>")
                rows.say(hidden)
                rows.owner("I revoke that, not approved")
                self.denied(rows, "withdraws it")
        rows = self.presented()
        rows.owner("yes")
        rows.say(offers.rendering(old, other))
        rows.owner("I revoke that, not approved")
        self.allowed(rows)

    def test_the_session_follows_a_question_approval_but_not_a_presentation_text_undid(self):
        other = self.repo / "docs/plans/2026-11-16-readme"
        other.mkdir(parents=True)
        b = offers.create(other, {**OFFER, "paths": ["README.md"]})
        readme = {"file_path": str(self.repo / "README.md"), "content": "x"}
        for crlf in (False, True):
            with self.subTest(crlf=crlf, case="question"):
                rows = self.presented()
                rows.owner("yes")
                question = offers.presentation(b, other, question=True)
                question = question.replace("\n", "\r\n") if crlf else question
                tool = rows.ask(question, ["Show review.html first", "Approve from this summary", "Change something"])
                rows.answer(tool, question, "Approve from this summary")
                rows.owner("I revoke that, not approved")
                self.denied(rows, tool="Write", data=readme)
        with self.subTest(case="a newer question replaces a text presentation awaiting its answer"):
            a = offers.create(self.folder, {**OFFER, "paths": ["src/a.ts"]})
            rows = self.presented()
            rows.owner("yes")
            rows.say(offers.presentation(a, self.folder))
            question = offers.presentation(b, other, question=True)
            tool = rows.ask(question, ["Show review.html first", "Approve from this summary", "Change something"])
            rows.answer(tool, question, "Approve from this summary")
            rows.owner("I revoke that, not approved")
            self.denied(rows, tool="Write", data=readme)
        with self.subTest(case="one message: another offer as text, then this offer's question"):
            rows = self.presented()
            rows.owner("yes")
            question = self.readable_question()
            rows.append({"type": "assistant", "uuid": rows.uid(), "message": {"content": [
                {"type": "text", "text": offers.presentation(b, other)},
                {"type": "tool_use", "id": "q-both", "name": "AskUserQuestion", "input": {"questions": [
                    {"question": question, "options": [{"label": "Approve from this summary"}]}]}}]}})
            rows.answer("q-both", question, "Approve from this summary")
            rows.owner("I revoke that, not approved")
            self.denied(rows)
        rows = self.presented()
        rows.owner("yes")
        rows.say(offers.presentation(b, other))
        rows.say("P.S. I also delete the database.")
        rows.owner("I revoke that, not approved")
        self.denied(rows, "withdraws it")

    def test_a_stop_in_this_session_pauses_every_write_whatever_the_task(self):
        rows = self.presented()
        rows.owner("yes")
        rows.owner("now work on docs/plans/2026-11-16-readme")
        rows.owner("stop")
        self.denied(rows, "stopped the work")  # within one session a stop is never task-bound: continue lifts it
        rows.owner("continue")
        self.allowed(rows)

    def test_an_offer_approved_by_button_or_slash_command_lifts_the_pause(self):
        """Live 2026-11-17: "Do not implement until I approve" paused the session, the owner approved the offer with the
        question tool's button, and every write stayed refused, because only a typed message could lift the pause."""
        hold = "Do not implement until I approve the plan."
        question = self.readable_question()
        for button in ("Approve from this summary", "Approve from this summary (Recommended)"):
            with self.subTest(button=button):
                rows = Rows().router()
                rows.owner(hold)
                tool = rows.ask(question, [button, "Change something"])
                rows.answer(tool, question, button)
                self.allowed(rows)
        with self.subTest("the host keyed the answer without the question's final line break"):
            rows = Rows().router()
            rows.owner(hold)
            tool = rows.ask(question + "\n", ["Approve from this summary", "Change something"])
            rows.answer(tool, question, "Approve from this summary")
            self.allowed(rows)
        with self.subTest("typed /approve <N> after a text presentation"):
            rows = Rows().router()
            rows.owner(hold)
            self.presented(rows)
            rows.owner("/approve 1")
            self.allowed(rows)
        with self.subTest("a stop after the approval, then the offer approved again by button"):
            rows = self.presented()
            rows.owner("yes")
            rows.owner("stop")
            self.denied(rows, "stopped the work")
            tool = rows.ask(question, ["Approve from this summary", "Change something"])
            rows.answer(tool, question, "Approve from this summary")
            self.allowed(rows)

    def test_answers_that_approve_no_offer_never_lift_the_pause(self):
        hold = "Do not implement until I approve the plan."
        question = self.readable_question()
        for asked, answer in ((question, "Change something"), (question, "Show review.html first"),
                              ("Shall I also update the docs?", "Approve")):
            with self.subTest(answer=answer, asked=asked[:20]):
                rows = self.presented()
                rows.owner("yes")
                rows.owner(hold)
                tool = rows.ask(asked, ["Approve", "Approve from this summary", "Change something",
                                        "Show review.html first"])
                rows.answer(tool, asked, answer)
                self.denied(rows, "stopped the work")
        with self.subTest("approve on a second question in the same call, change on the offer's"):
            rows = self.presented()
            rows.owner("yes")
            rows.owner(hold)
            tool = rows.ask(question, ["Approve from this summary", "Change something"])
            rows.rows[-1]["message"]["content"][0]["input"]["questions"].append(
                {"question": "Shall I also update the docs?", "options": [{"label": "Approve"}]})
            rows.answer(tool, question, "Change something")
            rows.rows[-1]["toolUseResult"]["answers"]["Shall I also update the docs?"] = "Approve"
            self.denied(rows, "stopped the work")
        with self.subTest("an unanswered offer question"):
            rows = self.presented()
            rows.owner("yes")
            rows.owner(hold)
            rows.ask(question, ["Approve from this summary"])
            self.denied(rows, "stopped the work")
        with self.subTest("/approve naming another offer number"):
            rows = self.presented()
            rows.owner("yes")
            rows.owner(hold)
            rows.owner("/approve 7")
            self.denied(rows, "stopped the work")

    def test_lifting_the_pause_never_revives_a_withdrawn_approval(self):
        other = offers.create(self.folder, {**OFFER, "paths": ["tests/vat.spec.ts"]})
        question = offers.presentation(other, self.folder, question=True)
        rows = self.presented()
        rows.owner("yes")
        rows.owner("I revoke that, not approved")
        rows.owner("stop")
        tool = rows.ask(question, ["Approve from this summary", "Change something"])
        rows.answer(tool, question, "Approve from this summary")
        self.allowed(rows, data={"file_path": str(self.repo / "tests/vat.spec.ts"), "content": "x"}, tool="Write")
        self.denied(rows, "withdraws it")

    def test_a_made_up_offer_marker_never_lifts_a_stop(self):
        fake = "`Offer #7 · 0123456789abcdef · task fake · D:/elsewhere`"
        with self.subTest("a fake footer in an option description, then Approve"):
            rows = self.presented()
            rows.owner("yes")
            rows.owner("stop")
            tool = rows.ask("Shall I also update the docs?", ["Approve"])
            rows.rows[-1]["message"]["content"][0]["input"]["questions"][0]["options"][0]["description"] = fake
            rows.answer(tool, "Shall I also update the docs?", "Approve")
            self.denied(rows, "stopped the work")
        with self.subTest("a fake footer in text, then /approve 7"):
            rows = self.presented()
            rows.owner("yes")
            rows.owner("stop")
            rows.say("Here it is.\n\n" + fake)
            rows.owner("/approve 7")
            self.denied(rows, "stopped the work")
        with self.subTest("/approve typed after the text offer was replaced by its question"):
            other = self.repo / "docs/plans/2026-11-16-readme"
            other.mkdir(parents=True)
            b = offers.create(other, {**OFFER, "paths": ["README.md"]})
            rows = self.presented()
            rows.owner("yes")
            rows.owner(f"pick up docs/plans/2026-11-16-readme")
            rows.owner("stop")
            rows.say(offers.presentation(b, other))
            asked = offers.presentation(b, other, question=True)
            rows.ask(asked, ["Approve from this summary", "Change something"])
            rows.owner("/approve 1")
            self.denied(rows, "stopped the work")
        with self.subTest("/approve 1 without a fresh presentation"):
            rows = self.presented()
            rows.owner("yes")
            rows.owner("stop")
            rows.owner("/approve 1")
            self.denied(rows, "stopped the work")

    def stamped(self, stem, stamp, *messages):
        rows = self.session(stem, *messages)
        for row in rows.rows:
            row["timestamp"] = stamp
        rows.write(self.sessions / f"{stem}.jsonl")

    def approved_at(self) -> float:
        last = json.loads((self.sessions / "s-earlier.jsonl").read_text(encoding="utf-8").splitlines()[-1])
        return dt.datetime.fromisoformat(last["timestamp"].replace("Z", "+00:00")).timestamp()

    def test_an_undated_withdrawal_is_placed_by_its_files_last_change(self):
        self.earlier_approval()
        self.stamped("s-undated", "", "I revoke that")
        undated = self.sessions / "s-undated.jsonl"
        os.utime(undated, (time.time(), START - 1))  # it ended before the approval: provably earlier
        self.allowed(Rows().router())
        os.utime(undated, (time.time(), self.approved_at() + 100))  # still changing after the approval
        self.denied(Rows().router(), "can't be established")
        global CLOCK
        CLOCK = itertools.count(int(self.approved_at() - START) + 200)  # the owner approves again, after it ended
        rows = self.presented()
        rows.owner("yes")
        self.allowed(rows)
        rows.owner("only change the tests")  # restrictions after the recovery still count
        self.denied(rows, "may narrow it")

    def test_two_sessions_at_the_same_instant_need_a_fresh_approval(self):
        self.earlier_approval()
        self.stamped("s-tied", stamp(self.approved_at()), "I revoke that")
        self.denied(Rows().router(), "can't be established")
        rows = self.presented()
        rows.owner("yes")
        self.allowed(rows)  # dated after both, so the tie no longer decides

    def test_timestamps_in_other_zones_order_by_their_real_instant(self):
        self.earlier_approval()
        five = dt.timezone(dt.timedelta(hours=5))
        before = dt.datetime.fromtimestamp(self.approved_at() - 3600, five).isoformat()  # "+05:00"
        self.stamped("s-zone-before", before, "I revoke that")
        self.allowed(Rows().router())
        after = dt.datetime.fromtimestamp(self.approved_at() + 1, five).isoformat()
        self.stamped("s-zone-after", after, "I revoke that")
        self.denied(Rows().router(), "withdraws it")

    def test_an_unordered_fact_holds_back_everything_inside_its_window(self):
        module = load_hook()
        undated = module.Facts(facts=[["", "revoke", "i revoke that", None, None]], end=100.0)  # anywhere in 0..100
        dated = module.Facts(facts=[["t", "approve", ["t1", "p1"], 10.0, 10.0], ["t", "approve", ["t2", "p2"], 20.0, 20.0]])
        state = module.fold({"a": undated, "b": dated})
        self.assertFalse(state.approved)  # the approval at 20 may still precede the withdrawal
        fresh = module.Facts(facts=[["t", "approve", ["t3", "p3"], 150.0, 150.0]])
        state = module.fold({"a": undated, "b": dated, "c": fresh})
        self.assertEqual((state.approved, state.reference), (True, ("c", "t3", "p3")))

    def test_a_question_tool_presentation_puts_the_session_on_the_task(self):
        asked = Rows().router()
        asked.owner("now work on docs/plans/2026-11-16-readme")
        question = "Offer:\n" + self.rendering()
        tool = asked.ask(question, ["Show review.html first", "Approve from this summary", "Change something"])
        asked.answer(tool, question, "Approve from this summary")
        asked.owner("I revoke that")
        asked.write(self.sessions / "s-asked.jsonl")
        self.denied(Rows().router(), "withdraws it")

    def test_returning_to_the_approving_session_still_sees_a_later_withdrawal(self):
        approving = self.presented()
        approving.owner("yes")
        self.allowed(approving)  # approved in s-now, and recorded
        self.session("s-between", "I revoke that")
        self.denied(approving, "withdraws it")  # back in s-now: the withdrawal elsewhere still counts

    def test_a_refused_early_approval_keeps_the_report_owed(self):
        asked = self.presented()
        asked.owner("Show review.html first")
        self.presented(asked)
        asked.owner("approve")  # refused: the report wasn't shown
        asked.write(self.sessions / "s-asked.jsonl")
        rows = self.presented()
        rows.owner("approve")
        self.denied(rows, "show the report, then ask again")

    def test_unreadable_history_refuses_even_with_a_fresh_approval(self):
        (self.sessions / "s-broken.jsonl").mkdir()  # a transcript that can't be read
        rows = self.presented()
        rows.owner("yes")
        self.denied(rows, "session history can't be read")

    def test_stops_and_continues_across_sessions_apply_in_time_order(self):
        self.earlier_approval()
        self.session("s-paused", "stop")
        self.denied(Rows().router(), "stopped the work in an earlier session")
        self.session("s-resumed", "continue")
        self.allowed(Rows().router())

    def test_report_first_survives_into_a_new_session(self):
        typed = self.presented()
        typed.owner("Show review.html first")
        typed.write(self.sessions / "s-asked.jsonl")  # the session ended there; nothing was written
        rows = self.presented()
        rows.owner("approve")
        self.denied(rows, "show the report, then ask again")
        (self.folder / "plan-r1.html").write_text("<!DOCTYPE html>", encoding="utf-8")
        rows.say(f"Report: docs/plans/{TASK}/plan-r1.html")
        self.presented(rows)
        rows.owner("approve")
        self.allowed(rows)

    def test_a_report_button_answer_survives_into_a_new_session(self):
        asked = Rows().router()
        question = "Offer:\n" + self.rendering()
        tool = asked.ask(question, ["Show review.html first", "Approve from this summary", "Change something"])
        asked.answer(tool, question, "Show review.html first")
        asked.write(self.sessions / "s-asked.jsonl")
        rows = Rows().router()
        again = rows.ask(question, ["Show review.html first", "Approve from this summary", "Change something"])
        rows.answer(again, question, "Approve from this summary")
        self.denied(rows, "show the report, then ask again")

    def test_a_fresh_approval_after_a_withdrawal_replaces_the_reference(self):
        self.earlier_approval()
        now = Rows().router()
        now.owner("I revoke that")
        self.denied(now, "withdraws it")
        self.presented(now)
        turn = now.owner("yes")
        self.allowed(now)
        decision = offers.load(self.folder, 1)["decision"]
        self.assertEqual((decision["session"], decision["turn"]), (self.path.stem, turn))
        self.allowed(Rows().router(), path=self.sessions / "s-later.jsonl")  # the next session re-checks s-now

    def test_a_reference_that_does_not_validate_is_not_approval(self):
        earlier = self.presented()
        earlier.owner("yes but only the tests")
        earlier.write(self.sessions / "s-earlier.jsonl")
        offers.approve(self.folder, 1, "s-earlier", earlier.rows[-1]["uuid"], earlier.rows[-2]["uuid"])
        self.denied(Rows().router(), "doesn't validate in session s-earlier")
        offers.revoke(self.folder, 1)
        self.denied(Rows().router(), "offer #1 is revoked")


class ChildrenAndRules(ApprovalHookCase):
    """C-OFFER-6 (children carry the parent's approval) and C-RULES-1 (an open rules question pauses writes)."""

    def test_a_derived_child_offer_needs_no_new_answer_while_its_parent_holds(self):
        parent = offers.create(self.folder, {**OFFER, "delegable_paths": ["tests/"], "paths": ["src/vat.ts", "tests/"]})
        rows = self.presented(offer=parent)
        turn = rows.owner("yes")
        rows.write(self.path)
        offers.approve(self.folder, parent["id"], self.path.stem, turn, rows.rows[-2]["uuid"])
        offers.derive(self.folder, parent["id"], {"behaviour": "write the VAT test", "paths": ["tests/vat.spec.ts"]})
        child_write = {"file_path": str(self.repo / "tests/vat.spec.ts"), "content": "test"}
        self.allowed(rows, tool="Write", data=child_write)
        offers.revoke(self.folder, parent["id"])
        self.denied(rows, "is not approved", tool="Write", data=child_write)

    def test_deriving_a_child_records_the_parents_approval_first(self):
        """Host test R10 (T16): the approval was only recorded when a write used it, so `offer derive` found a draft."""
        parent = offers.create(self.folder, {**OFFER, "delegable_paths": ["tests/"], "paths": ["src/vat.ts", "tests/"]})
        command = (f'python -X utf8 -I "{ROOT / "skills/workflow/scripts/record.py"}" offer derive '
                   f'"{self.folder}" {parent["id"]} child.json')
        self.denied(Rows().router(), "needs an approved parent", tool="Bash", data={"command": command})
        rows = self.presented(offer=parent)
        rows.owner("approve")
        self.assertEqual(offers.load(self.folder, parent["id"])["state"], "draft")
        self.allowed(rows, tool="Bash", data={"command": command})
        self.assertEqual(offers.load(self.folder, parent["id"])["state"], "approved")  # recorded before derive runs

    def test_an_open_rules_question_pauses_only_writes(self):
        (self.folder / "PLAN.md").write_text("# VAT\n\n## Current checkpoint\n- Rules: NEEDS_SETUP (no test command)\n",
                                             encoding="utf-8")
        rows = self.presented()
        rows.owner("yes")
        self.denied(rows, "waits for the rules question")
        self.allowed(rows, tool="Bash", data={"command": "git status"})  # reading continues
        (self.folder / "PLAN.md").write_text("# VAT\n\n## Current checkpoint\n- Rules: skipped for this task "
                                             "(gaps: no test command)\n", encoding="utf-8")
        self.allowed(rows)


class ProtectedOperations(ApprovalHookCase):
    """C-SAFE-1 and C-CSS-1/2."""

    def approved(self):
        rows = self.presented()
        rows.owner("yes")
        return rows

    def test_git_writes_need_the_operation_in_an_approved_offer(self):
        self.allowed(self.approved(), tool="Bash", data={"command": "git commit -m vat"})
        self.denied(self.approved(), 'no approved offer lists "git push"', tool="Bash", data={"command": "git push"})

    def test_operations_match_exactly(self):
        offers.revise(self.folder, self.offer["id"], {**OFFER, "operations": ["do not git push", "git commits"]})
        rows = self.presented(offer=offers.load(self.folder, 2))
        rows.owner("yes")
        self.denied(rows, tool="Bash", data={"command": "git push"})
        self.denied(rows, tool="Bash", data={"command": "git commit -m x"})

    def test_an_open_rules_question_also_pauses_git_writes(self):
        (self.folder / "PLAN.md").write_text("# VAT\n\n## Current checkpoint\n- Rules: NEEDS_SETUP\n", encoding="utf-8")
        self.denied(self.approved(), "waits for the rules question", tool="Bash", data={"command": "git commit -m x"})

    def test_restyling_counts_even_when_nothing_is_added(self):
        (self.repo / "src/styles/vat.css").write_text(".vat { color: red; }\n", encoding="utf-8")
        change = {"file_path": str(self.repo / "src/styles/vat.css"), "old_string": "red", "new_string": "blue"}
        self.denied(self.approved(), "changes styling", data=change)
        shell = {"command": f"echo '.x{{}}' > {self.repo / 'src/styles/extra.css'}"}
        self.denied(self.approved(), "changes styling", tool="Bash", data=shell)

    def test_styling_is_judged_on_the_whole_file_not_the_fragment(self):
        (self.repo / "src/vat.ts").write_text('<b style="color: red; margin: 0">x</b>\n'
                                              'const Box = styled.div`\n  padding: 4px;\n  color: red;\n`;\n'
                                              'const a = 1;\n', encoding="utf-8")
        for old, new in (("red;", "blue;"), ("padding: 4px", "padding: 8px")):
            with self.subTest(old=old):
                change = {"file_path": str(self.repo / "src/vat.ts"), "old_string": old, "new_string": new}
                self.denied(self.approved(), "changes styling", data=change)
        multi = {"file_path": str(self.repo / "src/vat.ts"), "edits": [
            {"old_string": "const a = 1", "new_string": "const a = 2"}, {"old_string": "margin: 0", "new_string": "margin: 2px"}]}
        self.denied(self.approved(), "changes styling", tool="MultiEdit", data=multi)
        logic = {"file_path": str(self.repo / "src/vat.ts"), "old_string": "const a = 1", "new_string": "const a = 2"}
        self.allowed(self.approved(), data=logic)
        whole = (self.repo / "src/vat.ts").read_text(encoding="utf-8").replace("color: red; margin", "color: red; gap")
        self.denied(self.approved(), "changes styling", tool="Write",
                    data={"file_path": str(self.repo / "src/vat.ts"), "content": whole})  # against the current file

    def test_offer_files_change_only_through_record_py(self):
        target = str(self.folder / "offers/offer-1.json")
        self.denied(self.approved(), "offers change only through", tool="Write", data={"file_path": target, "content": "{}"})
        self.denied(Rows().router(), "offers change only through", tool="Bash", data={"command": f"echo x > {target}"})

    def test_value_only_and_framework_styling_counts(self):
        cases = {
            "inline value": ('<b style="color:red">', '<b style="color:blue">'),
            "runtime value": ("el.style.color = 'red'", "el.style.color = 'blue'"),
            "visual prop": ('<Button color="red">', '<Button color="blue">'),
            "custom property": ("const a = 1", "const theme = `--brand: #f00;`"),
            "new utility classes": ("<b>", '<b className="bg-red-500 p-4">'),
            "removed inline style": ('<b style="color:red">', "<b>"),
        }
        for name, (old, new) in cases.items():
            with self.subTest(name):
                change = {"file_path": str(self.repo / "src/vat.ts"), "old_string": old, "new_string": new}
                self.denied(self.approved(), "changes styling", data=change)
        tokens = {"file_path": str(self.repo / "src/styles/theme/tokens.json"), "content": '{"brand": "#f00"}'}
        self.denied(self.approved(), "changes styling", tool="Write", data=tokens)
        text = {"file_path": str(self.repo / "src/vat.ts"), "old_string": "<b>x</b>", "new_string": "<b>y</b>"}
        self.allowed(self.approved(), data=text)  # text only

    def test_reusing_an_existing_class_combination_is_not_styling(self):
        (self.repo / ".git").rmdir()
        (self.repo / "src/card.tsx").write_text('<div className="bg-red-500 p-4">a</div>\n', encoding="utf-8")
        for args in (["init", "-q"], ["add", "src/card.tsx"]):
            subprocess.run(["git", "-C", str(self.repo), *args], check=True, capture_output=True)
        reuse = {"file_path": str(self.repo / "src/vat.ts"), "old_string": "1",
                 "new_string": '<div className="bg-red-500 p-4">b</div>'}
        self.allowed(self.approved(), data=reuse)
        other = {**reuse, "new_string": '<div className="bg-red-600">b</div>'}
        self.denied(self.approved(), "changes styling", data=other)

    def test_the_offer_commands_need_no_offer(self):
        """Host test R2 (T16): the very first `record.py offer create` was refused as a write to a file "create"."""
        record = ROOT / "skills/workflow/scripts/record.py"
        for verb in ("create", "present", "revise", "derive", "presentation"):
            with self.subTest(verb=verb):
                command = f'python -X utf8 -I "{record}" offer {verb} docs/plans/{TASK} offer.json'
                self.allowed(Rows().router(), tool="Bash", data={"command": command})
        self.denied(Rows().router(), tool="Bash",
                    data={"command": f'python -X utf8 -I "{record}" offer create docs/plans/{TASK} x && echo y > src/vat.ts'})

    def test_installs_and_bulk_deletes_keep_their_safeguards(self):
        self.denied(self.approved(), "installs packages", tool="Bash", data={"command": "npm install left-pad"})
        self.denied(self.approved(), tool="Bash", data={"command": "git clean -fdx"})

    def test_task_records_and_reads_need_no_offer(self):
        self.allowed(Rows().router(), tool="Bash", data={"command": "git status"})
        self.allowed(Rows().router(), tool="Write", data={"file_path": str(self.folder / "notes.md"), "content": "x"})

    def test_a_spar_record_needs_no_offer_but_nothing_else_beside_it(self):
        spar = self.repo / "docs/spar/2026-11-17-idea"
        self.allowed(Rows().router(), tool="Write", data={"file_path": str(spar / "SPAR.md"), "content": "# Spar"})
        for other in (spar / "run.py", spar / "notes.md", self.repo / "docs/spar/SPAR.md",
                      spar / "deeper/SPAR.md"):
            with self.subTest(other=other):
                self.denied(Rows().router(), tool="Write", data={"file_path": str(other), "content": "x"})

    def test_a_spar_record_reached_through_a_link_is_not_a_record(self):
        alias = self.repo / "docs/spar/alias"
        alias.parent.mkdir(parents=True, exist_ok=True)
        if os.name == "nt":
            subprocess.run(["cmd", "/c", "mklink", "/J", str(alias), str(self.repo / "src")], check=True,
                           capture_output=True)
        else:
            alias.symlink_to(self.repo / "src", target_is_directory=True)
        self.denied(Rows().router(), tool="Write", data={"file_path": str(alias / "SPAR.md"), "content": "x"})
        linked = self.repo / "docs/spar/2026-11-17-hard"
        linked.mkdir(parents=True)
        os.link(self.repo / "src/vat.ts", linked / "SPAR.md")
        self.denied(Rows().router(), data={"file_path": str(linked / "SPAR.md"), "old_string": "1",
                                           "new_string": "2"})

    def test_styling_needs_the_css_switch(self):
        css = {"file_path": str(self.repo / "src/styles/vat.css"), "content": ".vat { color: red; }\n"}
        inline = {"file_path": str(self.repo / "src/vat.ts"), "old_string": "1",
                  "new_string": "el.style.color = 'red'"}
        self.denied(self.approved(), "CSS is off here", tool="Write", data=css)  # no settings file: off
        self.settings.write_text('{"css": "on"}', encoding="utf-8")
        self.allowed(self.approved(), tool="Write", data=css)
        (self.repo / "DESIGN.md").write_text("css: never\n", encoding="utf-8")
        self.denied(self.approved(), "CSS is off here", tool="Write", data=css)
        (self.repo / "DESIGN.md").unlink()
        self.settings.write_text('{"css": "off"}', encoding="utf-8")
        self.denied(self.approved(), "CSS is off here", data=inline)

    def test_changing_the_switch_needs_a_yes_to_that_exact_question(self):
        run_on = {"command": "python ~/.agents/skills/workflow/scripts/settings.py css on"}
        rows = Rows().router()
        self.denied(rows, "protected operation", tool="Bash", data=run_on)
        rows.say("Turn CSS on for every project on this machine? Yes / No")
        rows.owner("no")
        self.denied(rows, tool="Bash", data=run_on)
        rows.say("Turn CSS off for every project on this machine? Yes / No")
        rows.owner("yes")
        self.denied(rows, tool="Bash", data=run_on)  # a Yes to the opposite value
        rows.say("Turn CSS on for every project on this machine? Yes / No")
        rows.owner("yes")
        self.allowed(rows, tool="Bash", data=run_on)
        rows.say("Shall I run the tests?")
        rows.owner("yes")
        self.denied(rows, tool="Bash", data=run_on)  # the latest Yes answered another question
        edit = {"file_path": str(self.settings), "content": '{"css": "on"}'}
        self.denied(rows, tool="Write", data=edit)

    def test_a_css_yes_by_button_survives_a_trimmed_key(self):
        asked = "Turn CSS on for every project on this machine?\n"
        rows = Rows().router()
        tool = rows.ask(asked, ["Yes", "No"])
        rows.answer(tool, asked.strip(), "Yes")
        self.allowed(rows, tool="Bash", data={"command": "python settings.py css on"})

    def test_a_css_yes_by_button_never_answers_two_lookalike_questions(self):
        run_on = {"command": "python settings.py css on"}
        asked = "Turn CSS on for every project on this machine?\n"
        rows = Rows().router()
        tool = rows.ask(asked, ["Yes", "No"])
        rows.rows[-1]["message"]["content"][0]["input"]["questions"].append({"question": asked.strip(), "options": []})
        rows.answer(tool, asked.strip(), "Yes")
        self.denied(rows, tool="Bash", data=run_on)

    def test_a_settings_yes_is_used_once_and_never_waves_other_commands_through(self):
        rows = Rows().router()
        rows.say("Turn CSS on for every project on this machine? Yes / No")
        rows.owner("yes")
        self.denied(rows, "needs an approved offer", tool="Bash",
                    data={"command": f"python settings.py css on && echo x > {self.repo / 'src/vat.ts'}"})
        self.allowed(rows, tool="Bash", data={"command": "python settings.py css on"})
        self.denied(rows, "each Yes allows one change", tool="Bash", data={"command": "python settings.py css on"})
        fresh = Rows().router()
        self.denied(fresh, "protected operation", tool="Bash",
                    data={"command": f"echo '{{\"css\": \"on\"}}' > {self.settings}"})

    def test_one_yes_never_covers_two_switch_changes_in_one_call(self):
        for command in ("python settings.py css on && python settings.py css off",
                        f"python settings.py css on; echo '{{\"css\": \"off\"}}' > {self.settings}"):
            with self.subTest(command=command):
                rows = Rows().router()
                rows.say("Turn CSS on for every project on this machine? Yes / No")
                rows.owner("yes")
                self.denied(rows, "at most once", tool="Bash", data={"command": command})

    def test_a_yes_is_consumed_atomically_and_a_damaged_store_refuses(self):
        rows = Rows().router()
        rows.say("Turn CSS on for every project on this machine? Yes / No")
        rows.owner("yes")
        event = self.event(rows, tool="Bash", data={"command": "python settings.py css on"})
        results = [self.finish(p) for p in [self.start(event) for _ in range(4)]]
        self.assertEqual(sum(r is None for r in results), 1, results)  # four concurrent calls, one Yes, one change
        damaged = tempfile.TemporaryDirectory()
        self.addCleanup(damaged.cleanup)
        (Path(damaged.name) / "settings-consent").write_text("not a folder", encoding="utf-8")
        self.cache = damaged.name
        rows.say("Turn CSS on for every project on this machine? Yes / No")
        rows.owner("yes")
        self.denied(rows, "can't be recorded as used", tool="Bash", data={"command": "python settings.py css on"})

    def test_mixed_question_answers_bind_to_their_own_question(self):
        rows = Rows().router()
        setting, other = "Turn CSS on for every project on this machine?", "Run the tests now?"
        tool = rows.ask(setting, ["Yes", "No"])
        rows.rows[-1]["message"]["content"][0]["input"]["questions"].append({"question": other, "options": []})
        rows.answer(tool, setting, "No")
        rows.rows[-1]["toolUseResult"]["answers"][other] = "Yes"
        self.denied(rows, tool="Bash", data={"command": "python settings.py css on"})

    def test_the_switch_question_through_the_question_tool(self):
        rows = Rows().router()
        question = "Turn CSS on for every project on this machine?"
        tool = rows.ask(question, ["Yes", "No"])
        rows.answer(tool, question, "Yes")
        self.allowed(rows, tool="Bash", data={"command": "python settings.py css on"})


def git(cwd: Path, *args: str):
    subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", "-c", "core.autocrlf=false", *args],
                   cwd=cwd, check=True, capture_output=True)


class ApprovalsStayInTheirWorktree(ApprovalHookCase):
    """F4 of docs/plans/2026-11-17-approval-button-unpause: an offer approved in one worktree of a repository never
    authorises a write in another; the session's own worktree works as before."""

    def setUp(self):
        super().setUp()
        (self.repo / ".git").rmdir()
        git(self.repo, "init", "-q")
        git(self.repo, "add", "-A")
        git(self.repo, "commit", "-qm", "base")
        self.linked = self.base / "linked"
        git(self.repo, "worktree", "add", "-q", "--detach", str(self.linked))
        self.session = self.repo

    def event(self, rows: Rows, tool="Edit", data=None, path=None):
        found = super().event(rows, tool=tool, data=data, path=path)
        found["cwd"] = str(self.session)
        return found

    def approved(self):
        rows = self.presented()
        rows.owner("yes")
        return rows

    def edit(self, tree: Path, name="src/vat.ts"):
        return {"file_path": str(tree / name), "old_string": "1", "new_string": "2"}

    def test_an_approval_in_the_main_checkout_still_covers_the_main_checkout(self):
        self.allowed(self.approved(), data=self.edit(self.repo))
        self.allowed(self.approved(), tool="Bash", data={"command": f"git -C {self.repo} commit -m vat"})

    def test_an_approval_in_the_main_checkout_never_covers_a_linked_worktree(self):
        for data in (self.edit(self.linked), {"content": "x", "file_path": str(self.linked / "src/vat.ts")}):
            with self.subTest(data=data):
                reason = self.denied(self.approved(), "another worktree", self.linked.as_posix(), self.repo.as_posix(),
                                     tool="Write" if "content" in data else "Edit", data=data)
                self.assertIn("start", reason)

    def test_a_git_command_in_a_linked_worktree_is_refused(self):
        self.denied(self.approved(), "another worktree", tool="Bash",
                    data={"command": f"git -C {self.linked} commit -m vat"})
        self.denied(self.approved(), "another worktree", tool="Bash",
                    data={"command": f"cd {self.linked} && git commit -m vat"})

    def test_one_call_that_writes_in_both_checkouts_is_refused_as_a_whole(self):
        both = f"echo 1 > {self.repo / 'src/vat.ts'} && echo 2 > {self.linked / 'src/vat.ts'}"
        self.denied(self.approved(), "another worktree", tool="Bash", data={"command": both})

    def test_a_session_in_the_linked_worktree_uses_its_own_offer_and_stays_there(self):
        self.session = self.linked
        self.folder = self.linked / "docs/plans" / TASK
        self.allowed(self.approved(), data=self.edit(self.linked))
        self.denied(self.approved(), "another worktree", data=self.edit(self.repo))

    def test_git_options_that_point_elsewhere_are_refused(self):
        gitdir = self.repo / ".git/worktrees/linked"
        for command in (f'git --git-dir="{gitdir}" commit --allow-empty -m x', f"git --git-dir {gitdir} commit -m x",
                        f"git --work-tree {self.linked} restore src/vat.ts", f"GIT_DIR={gitdir} git commit -m x",
                        f"GIT_WORK_TREE={self.linked} git checkout -- src/vat.ts"):
            with self.subTest(command=command):
                self.denied(self.approved(), "git -C", tool="Bash", data={"command": command})

    def link(self, alias: Path, target: Path):
        alias.parent.mkdir(parents=True, exist_ok=True)
        if os.name == "nt":
            subprocess.run(["cmd", "/c", "mklink", "/J", str(alias), str(target)], check=True, capture_output=True)
        else:
            alias.symlink_to(target, target_is_directory=True)

    def test_a_link_never_carries_a_write_into_a_linked_worktree(self):
        self.link(self.repo / ".artifacts/alias", self.linked / "src")
        self.link(self.repo / "src/alias", self.linked / "src")
        for path in (self.repo / ".artifacts/alias/vat.ts", self.repo / "src/alias/vat.ts"):
            with self.subTest(path=path):
                self.denied(self.approved(), "another worktree", tool="Write",
                            data={"file_path": str(path), "content": "x"})

    def test_quoted_git_options_and_other_shells_are_refused_too(self):
        gitdir = self.repo / ".git/worktrees/linked"
        for tool, command in (("Bash", f'git "--git-dir={gitdir}" commit --allow-empty -m x'),
                              ("Bash", f'git --git-"dir"={gitdir} commit -m x'),
                              ("Bash", f"sh -c 'git --git-dir={gitdir} commit -m x'"),
                              ("PowerShell", f"git --git-dir={gitdir} commit --allow-empty -m x")):
            with self.subTest(tool=tool, command=command):
                self.denied(self.approved(), "git -C", tool=tool, data={"command": command})

    def test_a_session_started_through_a_link_is_still_this_checkout(self):
        alias = self.base / "alias"
        self.link(alias, self.repo)
        self.session = alias
        self.denied(self.approved(), "another worktree", data=self.edit(self.linked))

    def test_a_link_made_in_the_same_command_cannot_carry_a_write_elsewhere(self):
        future = self.repo / ".artifacts/future"
        for tool, command in (("PowerShell", f'cmd /c mklink /J "{future}" "{self.linked / "src"}"; '
                                             f'Set-Content "{future / "vat.ts"}" changed'),
                              ("Bash", f"ln -s {self.linked / 'src'} {future} && echo x > {future / 'vat.ts'}")):
            with self.subTest(tool=tool):
                self.denied(self.approved(), "another worktree", tool=tool, data={"command": command})

    def test_changing_the_set_of_worktrees_needs_its_own_approval(self):
        moved = f"{self.linked}-moved"
        for command in (f'git worktree move "{self.linked}" "{moved}"', f"git worktree remove {self.linked}",
                        "git worktree prune"):
            with self.subTest(command=command):
                self.denied(self.approved(), tool="Bash", data={"command": command})

    def test_a_write_to_a_place_known_only_at_run_time_is_refused(self):
        target = (self.linked / "src/vat.ts").as_posix()
        for tool, command in (("Bash", f'p=$(printf "%s" "{target}"); echo cross > "$p"'),
                              ("PowerShell", f'$env:TARGET="{target}"; Set-Content $env:TARGET changed')):
            with self.subTest(tool=tool):
                self.denied(self.approved(), "explicit path", tool=tool, data={"command": command})

    def test_writes_the_checker_cannot_place_are_refused_with_several_worktrees(self):
        linked = (self.linked / "src/vat.ts").as_posix()
        for tool, command in (("Bash", 'sed -i s/1/2/ "$p"'), ("Bash", 'truncate -s 0 "$p"'),
                              ("PowerShell", 'cmd /c "echo changed > .artifacts/%TARGET%/src/vat.ts"'),
                              ("Bash", "echo changed > .artifacts/`cat target.txt`/src/vat.ts"),
                              ("Bash", f"printf '%s\\n' {linked} | xargs rm"),
                              ("Bash", f"find {self.linked.as_posix()}/src -name vat.ts -exec rm {{}} \\;"),
                              ("Bash", "printf 'echo x > y\\n' > .artifacts/run.sh; bash .artifacts/run.sh"),
                              ("Bash", "python -c \"from pathlib import Path; Path('..','linked','src/vat.ts')"
                                       ".write_text('x')\"")):
            with self.subTest(command=command):
                self.denied(self.approved(), tool=tool, data={"command": command})

    def test_a_variable_that_is_only_read_still_works(self):
        for tool, command in (("Bash", 'cp "$SRC" src/vat.ts'), ("Bash", 'sed -n "$EXPR" src/vat.ts'),
                              ("Bash", "printf x | xargs echo"), ("PowerShell", "Set-Content src/vat.ts $value")):
            with self.subTest(command=command):
                self.allowed(self.approved(), tool=tool, data={"command": command})

    def test_git_in_a_folder_known_only_at_run_time_is_refused(self):
        for command in ('git -C "$DEST" commit -m x', 'cd "$DEST" && git commit -m x',
                        'command touch "$DEST"', '/usr/bin/touch "$DEST"'):
            with self.subTest(command=command):
                self.denied(self.approved(), tool="Bash", data={"command": command})

    def test_a_wildcard_cannot_reach_another_worktree(self):
        base = self.base.as_posix()
        for command in (f"echo changed > {base}/lin*/src/extra.ts", f"shopt -s globstar; echo x > {base}/**/vat.ts",
                        f"echo x > {base}/{{linked,other}}/src/vat.ts"):
            with self.subTest(command=command):
                self.denied(self.approved(), "another worktree", tool="Bash", data={"command": command})

    def test_quoted_programs_and_options_are_read_as_written(self):
        for command in ('git "-C" "$DEST" commit -m x', '"git" -C "$DEST" commit -m x', '"touch" "$DEST"',
                        'sed -ni s/1/2/ "$DEST"', 'env -i touch "$DEST"'):
            with self.subTest(command=command):
                self.denied(self.approved(), tool="Bash", data={"command": command})
        self.denied(self.approved(), tool="PowerShell", data={"command": "Set-Content -Path:$DEST -Value x"})

    def test_a_wildcard_through_a_link_cannot_reach_another_worktree(self):
        nested = self.base / "deep/a/b/nested"
        git(self.repo, "worktree", "add", "-q", "--detach", str(nested))
        alias = self.repo / ".artifacts/alias"
        self.link(alias, self.base / "deep")
        command = f"shopt -s globstar; echo x > {alias.as_posix()}/**/src/vat.ts"
        self.denied(self.approved(), "another worktree", tool="Bash", data={"command": command})

    def test_a_quoted_value_with_spaces_hides_nothing(self):
        self.denied(self.approved(), tool="Bash", data={"command": 'git -c user.name="A B" -C "$DEST" commit -m x'})

    def test_a_run_time_value_that_is_not_a_destination_still_works(self):
        for command in ('git -C "$DEST" status', "python -c \"print('write')\"", 'sed -i "$EXPR" src/vat.ts',
                        'truncate -s "$SIZE" src/vat.ts', 'sed -i -e "$EXPR" src/vat.ts',
                        'cd "$DEST" && git status'):
            with self.subTest(command=command):
                self.allowed(self.approved(), tool="Bash", data={"command": command})

    def test_ordinary_git_settings_still_work(self):
        self.allowed(self.approved(), tool="Bash", data={"command": "GIT_EDITOR=true git commit -m vat"})

    def test_with_one_worktree_a_run_time_place_keeps_its_old_handling(self):
        git(self.repo, "worktree", "remove", "--force", str(self.linked))
        self.allowed(self.approved(), tool="Bash", data={"command": 'p=src/vat.ts; echo 2 > "$p"'})

    def test_escaped_git_options_and_git_state_overrides_are_refused(self):
        gitdir = (self.repo / ".git/worktrees/linked").as_posix()
        for tool, command in (("Bash", f"git --git-\\dir={gitdir} commit --allow-empty -m x"),
                              ("Bash", f"GIT_INDEX_FILE={gitdir}/index git add src/vat.ts"),
                              ("PowerShell", f'$env:GIT_INDEX_FILE="{gitdir}/index"; git add src/vat.ts'),
                              ("Bash", f"git -c core.worktree={self.linked.as_posix()} add src/vat.ts")):
            with self.subTest(tool=tool, command=command):
                self.denied(self.approved(), "git -C", tool=tool, data={"command": command})

    def test_an_extended_length_session_path_is_still_this_checkout(self):
        if os.name != "nt":
            self.skipTest("extended-length paths are a Windows form")
        self.session = "\\\\?\\" + str(self.repo)
        self.denied(self.approved(), "another worktree", tool="Write",
                    data={"file_path": str(self.linked / "src/vat.ts"), "content": "x"})

    def test_an_independent_repository_keeps_its_old_handling(self):
        fixture = self.repo / ".artifacts/fixture"
        fixture.mkdir(parents=True)
        git(fixture, "init", "-q")
        self.allowed(self.approved(), tool="Bash", data={"command": f"git -C {fixture} commit --allow-empty -m x"})
        self.allowed(self.approved(), tool="Write", data={"file_path": str(fixture / "a.txt"), "content": "x"})

    def test_records_and_unapproved_work_behave_as_before(self):
        output = {"file_path": str(self.linked / ".artifacts" / TASK / "run.log"), "content": "x"}
        self.allowed(self.presented(), tool="Write", data=output)
        self.denied(self.presented(), "no owner answer", data=self.edit(self.repo))


class LegacyDispatch(ApprovalHookCase):
    """C-LEG-1: a session on a task in the frozen inventory goes to the legacy checker; nothing else ever does."""

    LEGACY = "2026-11-01-legacy"

    def setUp(self):
        super().setUp()
        from test_phase_gate_hook import APPROVED
        self.task_folder = self.repo / "docs/plans" / self.LEGACY
        (self.task_folder / "reviews").mkdir(parents=True)
        (self.task_folder / "reviews/plan-r1.html").write_text("<!DOCTYPE html>", encoding="utf-8")
        (self.task_folder / "PLAN.md").write_text(f"# Legacy\n\n## Current checkpoint\n- Status: x\n{APPROVED}\n",
                                                 encoding="utf-8")
        spec = importlib.util.spec_from_file_location("legacy_inventory_under_test",
                                                      ROOT / "skills/workflow/scripts/legacy_inventory.py")
        self.inventory = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.inventory)
        os.environ["WORKFLOW_AXA_HOME"] = str(self.base / "axa-home")
        self.addCleanup(os.environ.pop, "WORKFLOW_AXA_HOME", None)

    def legacy_rows(self, answer="Yes to both"):
        """The legacy approval as phase_gate's tests build it: a record write (the task), the report, the answer."""
        from test_phase_gate_hook import ROUTER, hooked, say, tool, user
        rows = [ROUTER, tool("Write", file_path=str(self.task_folder / "TODO.md"), content="x"),
                say(f"Plan report: {self.task_folder / 'reviews/plan-r1.html'}. Approve?"), user(answer)]

        class Plain(Rows):
            def write(self, path):
                path.write_text("\n".join(json.dumps(r) for r in hooked(rows, self_repo)), encoding="utf-8")
        self_repo = self.repo
        return Plain()

    def write_ts(self):
        return {"file_path": str(self.repo / "src/vat.ts"), "old_string": "1", "new_string": "2"}

    def test_a_listed_task_even_uncommitted_is_decided_by_the_legacy_checker(self):
        self.inventory.write(self.repo, replace=False)
        self.allowed(self.legacy_rows(), data=self.write_ts())
        reason = self.denied(self.legacy_rows("hmm"), data=self.write_ts())
        self.assertNotIn("approved offer", reason)  # phase_gate's refusal, not the offer checker's

    def test_no_inventory_or_an_unlisted_task_means_offers_only(self):
        self.denied(self.legacy_rows(), "needs an approved offer", data=self.write_ts())  # no inventory at all
        (self.task_folder.parent / "2026-11-20-new").mkdir()
        self.inventory.write(self.repo, replace=False)  # listed: only the tasks that existed
        self.assertNotIn("2026-11-20-new", self.inventory.load(self.repo)["tasks"])

    def test_an_approval_line_changed_after_the_inventory_is_not_legacy(self):
        self.inventory.write(self.repo, replace=False)
        plan = self.task_folder / "PLAN.md"
        plan.write_text(plan.read_text(encoding="utf-8").replace("2026-11-03", "2026-11-21"), encoding="utf-8")
        self.denied(self.legacy_rows(), "needs an approved offer", data=self.write_ts())

    def test_a_listed_task_that_gains_offers_goes_to_the_offer_checker(self):
        self.inventory.write(self.repo, replace=False)
        (self.task_folder / "offers").mkdir()
        self.denied(self.legacy_rows(), "needs an approved offer", data=self.write_ts())

    def test_agents_cannot_run_the_inventory_or_write_offers_on_the_legacy_route(self):
        self.inventory.write(self.repo, replace=False)
        script = ROOT / "skills/workflow/scripts/legacy_inventory.py"
        for command in (f'python -X utf8 -I "{script}" --apply "{self.repo}"',
                        f'git status && python "{script}" "{self.repo}" --replace --apply'):
            with self.subTest(command=command):
                self.denied(self.legacy_rows(), "only the owner runs it", tool="Bash", data={"command": command})
        self.allowed(self.legacy_rows(), tool="Bash", data={"command": f'python "{script}" "{self.repo}"'})  # preview
        self.denied(self.legacy_rows(), "offers change only through", tool="Write",
                    data={"file_path": str(self.folder / "offers/offer-1.json"), "content": "{}"})

    def test_the_inventory_is_owner_only(self):
        path = self.inventory.write(self.repo, replace=False)
        with self.assertRaises(FileExistsError):
            self.inventory.write(self.repo, replace=False)
        self.inventory.write(self.repo, replace=True)
        self.denied(self.legacy_rows(), "frozen list of pre-offer approvals", tool="Write",
                    data={"file_path": str(path), "content": "{}"})
        self.denied(self.legacy_rows(), "frozen list of pre-offer approvals", tool="Bash",
                    data={"command": f"echo x > {path}"})


import test_phase_gate_hook as gate_tests  # noqa: E402  (module import: its own classes aren't run twice)


class OfferRouteNeverUsesLegacyApproval(ApprovalHookCase):
    """T19: offers are decided without phase_gate's approval logic, which serves only inventoried legacy tasks."""

    def test_the_offer_route_never_calls_the_legacy_approval_functions(self):
        from unittest import mock
        module = load_hook()
        g = module.gate()

        def forbidden(*args, **kwargs):
            raise AssertionError("the offer route called legacy approval logic")
        patches = [mock.patch.object(g, name, forbidden)
                   for name in ("judge", "approval_problem", "small_approval_problem", "approved_write_paths")]
        patches += [mock.patch.dict(os.environ, {"WORKFLOW_AXA_SETTINGS": str(self.settings),
                                                 "WORKFLOW_AXA_HOME": str(self.base / "axa-home")})]
        for patch in patches:
            patch.start()
            self.addCleanup(patch.stop)
        approved = self.event(self.presented(), path=self.sessions / "s-unanswered.jsonl")
        self.assertIn("approved offer", module.problem_for(approved))
        rows = self.presented()
        rows.owner("yes")
        self.assertIsNone(module.problem_for(self.event(rows)))


class MissingReadEvidenceRefusesRendering(ApprovalHookCase):
    """T20 review: with hooks/read_evidence.py missing or broken, rendering a report is refused, never let through."""

    def test_a_missing_or_broken_library_refuses_the_render(self):
        import shutil
        plugin = self.base / "plugin"
        (plugin / "hooks").mkdir(parents=True)
        for name in ("approval.py", "phase_gate.py", "read_evidence.py"):
            shutil.copy(ROOT / "hooks" / name, plugin / "hooks" / name)
        shutil.copytree(ROOT / "skills", plugin / "skills")
        rows = Rows().router()
        rows.append({"type": "assistant", "uuid": rows.uid(), "message": {"content": [{"type": "tool_use",
                     "name": "Skill", "input": {"skill": "workflow-axa:workflow-specify"}}]}})
        render = {"command": f"python render_report.py --input p.json --output docs/plans/{TASK}/reviews/p.html"}
        for damage in ("missing", "broken"):
            with self.subTest(damage=damage):
                library = plugin / "hooks/read_evidence.py"
                if damage == "missing":
                    library.unlink()
                else:
                    library.write_text("def broken(:\n", encoding="utf-8")
                event = self.event(rows, tool="Bash", data=render)
                done = subprocess.run([sys.executable, "-X", "utf8", "-I", str(plugin / "hooks/approval.py")],
                                      input=json.dumps(event), capture_output=True, text=True, encoding="utf-8",
                                      env={**os.environ, "WORKFLOW_AXA_GATE_CACHE": self.cache,
                                           "WORKFLOW_AXA_SETTINGS": str(self.settings),
                                           "WORKFLOW_AXA_HOME": str(self.base / "axa-home")})
                self.assertEqual(done.returncode, 0, done.stderr)
                reason = json.loads(done.stdout)["hookSpecificOutput"]["permissionDecisionReason"]
                self.assertIn("read-evidence library", reason)


class RequiredReadsThroughTheOfferChecker(gate_tests.RequiredReadTests):
    """T17: the required-read checks keep their place at the cutover; phase_gate's own cases, run against the
    registered PreToolUse hook (approval.py)."""

    def setUp(self):
        super().setUp()
        from unittest import mock
        patch = mock.patch.object(gate_tests, "HOOK", HOOK)
        patch.start()
        self.addCleanup(patch.stop)


class RecordWritesThroughTheOfferChecker(gate_tests.PhaseGateHookTests):
    """T17: canonical task records stay writable only through record.py; phase_gate's two cases, run against
    approval.py."""
    KEEP = ("test_direct_canonical_record_write_requires_helper", "test_direct_record_scope_and_transcript_limits",
            "test_report_render_waits_for_the_report_guides", "test_report_requires_flowchart_guide_for_render_and_preflight",
            "test_flowchart_guide_read_evidence_and_compaction")

    def setUp(self):
        super().setUp()
        from unittest import mock
        patch = mock.patch.object(gate_tests, "HOOK", HOOK)
        patch.start()
        self.addCleanup(patch.stop)


for _name in dir(RecordWritesThroughTheOfferChecker):
    if _name.startswith("test_") and _name not in RecordWritesThroughTheOfferChecker.KEEP:
        setattr(RecordWritesThroughTheOfferChecker, _name, None)  # only the record-write cases run here


class Activation(ApprovalHookCase):

    def test_a_session_without_the_workflow_is_not_checked(self):
        rows = Rows()
        rows.owner("just edit it")
        self.allowed(rows)

    def test_a_broken_helper_module_is_named_with_its_own_error(self):
        """Host test R5 (T16): a broken offers.py was reported as a missing attribute of a half-loaded module."""
        module = load_hook()
        broken = self.base / "broken.py"
        broken.write_text('raise RuntimeError("deliberately broken")\n', encoding="utf-8")
        for _ in range(2):
            with self.assertRaisesRegex(RuntimeError, "deliberately broken"):
                module._load("approval_test_broken_helper", broken)

    def test_an_internal_error_fails_closed_for_writes(self):
        module = load_hook()
        import io
        from unittest import mock
        for tool in ("Edit", "Bash", "mcp__notion__create_page"):
            out = io.StringIO()
            with self.subTest(tool=tool), mock.patch.object(module, "problem_for", side_effect=RuntimeError("boom")), \
                    mock.patch("sys.stdin", io.StringIO(json.dumps({"tool_name": tool, "tool_input": {}}))), \
                    mock.patch("sys.stdout", out):
                module.main()
                self.assertIn("writes pause", out.getvalue())


if __name__ == "__main__":
    unittest.main()
