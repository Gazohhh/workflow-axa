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
        self.offer = offers.create(self.folder, OFFER)
        self.cache = CACHE.name

    def rendering(self, offer=None):
        return offers.rendering(offer or offers.load(self.folder, self.offer["id"]), self.folder)

    def presented(self, rows=None, offer=None):
        rows = rows or Rows().router()
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

    def test_a_stop_in_this_session_pauses_every_write_whatever_the_task(self):
        rows = self.presented()
        rows.owner("yes")
        rows.owner("now work on docs/plans/2026-11-16-readme")
        rows.owner("stop")
        self.denied(rows, "stopped the work")  # within one session a stop is never task-bound: continue lifts it
        rows.owner("continue")
        self.allowed(rows)

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
