"""Questions to the owner lead with their meaning; codes are only references after it
(docs/plans/2026-11-17-plain-owner-questions R5, T6)."""
from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("offers_for_questions", ROOT / "skills/workflow/scripts/offers.py")
offers = importlib.util.module_from_spec(spec)
spec.loader.exec_module(offers)

RUN5_QUESTION = "O1 Confirm D31 (a spar held during a task hands off by continuing that task's clarify), or choose a new task instead."
PLAIN_QUESTION = ("If a spar starts in the middle of a task, should its result continue that task's clarify step, or start "
                  "a new task? (see D31)")


def offer_input(behaviour: str) -> dict:
    return {"behaviour": behaviour, "paths": ["src/a.py"], "operations": [], "delegable_paths": [],
            "delegable_operations": [], "exclusions": [], "conditions": [], "checks": ["the tests pass"]}


class CodesComeAfterTheMeaning(unittest.TestCase):
    def test_a_question_that_starts_with_a_code_is_flagged(self):
        for text, code in ((RUN5_QUESTION, "O1"),
                           ("Agreement 7 (D35, R41-R44) on top of offer #7: a start card.", "Agreement 7"),
                           ("Offer #2 with the operation names the hook matches.", "Offer #2"),
                           ("T1: one rule set in WRITING.md.", "T1"),
                           ("C-OFFER-8 applies to this checkout.", "C-OFFER-8"),
                           ("S2 is accepted with the decisions of T2.", "S2")):
            with self.subTest(text=text[:30]):
                self.assertEqual(offers.id_first(text), code)

    def test_meaning_first_with_a_trailing_reference_passes(self):
        for text in (PLAIN_QUESTION, "Every question leads with its meaning (R5).",
                     "Move the writing rules into one file, WRITING.md.", "CSS stays off on this machine."):
            with self.subTest(text=text[:30]):
                self.assertIsNone(offers.id_first(text))

    def test_an_offer_whose_change_starts_with_a_code_is_refused(self):
        for text in ("Agreement 7 (D35, R41-R44) on top of offer #7: a start card.", "Offer #2 with the operation names.",
                     "C-OFFER-8 applies to this checkout.", "T1: one rule set in WRITING.md.", "R41-R44 add a start card."):
            with self.subTest(text=text[:30]), self.assertRaisesRegex(offers.OfferError, "meaning first"):
                offers.canonical_fields(offer_input(text))
        for text in ("Add a start card to /spar (agreement 7).", "S3 uploads keep their metadata.",
                     "EC2 instances restart at night (see D31).", "UTF-8 output stays readable.",
                     "Run 3 retries before failing.", "H1 headings get anchors.", "IE11 support is dropped."):
            with self.subTest(text=text[:30]):
                self.assertEqual(offers.canonical_fields(offer_input(text))["behaviour"], text)

    def test_a_new_offer_page_opens_with_its_meaning(self):
        import tempfile
        with tempfile.TemporaryDirectory() as tmp:
            task = Path(tmp) / "docs/plans/2026-11-17-x"
            task.mkdir(parents=True)
            offer = offers.create(task, offer_input("Round VAT per line, not per invoice."))
            for variant in (False, True):
                shown = offers.presentation(offer, question=variant)
                self.assertTrue(shown.startswith("## What you are asked to approve\n"), shown[:60])
                self.assertNotIn("## Offer #", shown)
                self.assertIn("`Offer #1 · ", shown)
            older = dict(offer, presentation_format=2)
            self.assertTrue(offers.presentation(older).startswith("## Offer #1\n"))

    def test_grilling_and_spar_say_so(self):
        grilling = " ".join((ROOT / "skills/grilling/SKILL.md").read_text(encoding="utf-8").split())
        ask = grilling.split("### How to ask", 1)[1]
        self.assertIn("The title and first sentence carry the meaning", ask)
        self.assertIn("still makes sense with every code removed", ask)
        self.assertIn("A fact or access request is asked plainly", grilling)
        spar_file = " ".join((ROOT / "skills/spar/SPAR-FILE.md").read_text(encoding="utf-8").split())
        self.assertIn("asked through grilling's \"How to ask\", never as a list of labels such as \"O1-O5\"", spar_file)


class RewriteRequestsUseTheRules(unittest.TestCase):
    """R7 and owner Q2 (pstack L5): a request to write, rewrite or simplify text, with no code change, reaches
    WRITING.md and creates nothing else."""

    def test_the_workflow_starts_on_a_rewrite_request_and_stays_read_only(self):
        skill = (ROOT / "skills/workflow/SKILL.md").read_text(encoding="utf-8")
        description = skill.split("description:", 1)[1].split("\n", 1)[0]
        self.assertIn("write, rewrite or simplify text a person reads", description)
        intents = " ".join(skill.split("2. Intent:", 1)[1].split("\n3.", 1)[0].split())
        for phrase in ("**Write**", "read `WRITING.md`", "no task records, offer or gates",
                       "compare the rewrite with the source", "\"may skip\" stays \"may skip\""):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, intents)

    def test_ordinary_chat_is_not_a_write_request(self):
        intents = " ".join((ROOT / "skills/workflow/SKILL.md").read_text(encoding="utf-8")
                           .split("2. Intent:", 1)[1].split("\n3.", 1)[0].split())
        self.assertIn("A question or a chat message is not a Write request", intents)


class SmallOnlyAfterNamingWhatDependsOnIt(unittest.TestCase):
    """R8 (pstack L6): an edit is lightweight only after its one-line why names what outside the diff reads what
    changes; replacing a function its callers use is never lightweight; a docs fix only tests read still is."""

    def test_the_lightweight_rule_asks_for_the_safety_assumption(self):
        rule = " ".join((ROOT / "skills/workflow/SKILL.md").read_text(encoding="utf-8")
                        .split("**Lightweight edit**:", 1)[1].split("\n", 1)[0].split())
        self.assertIn("Before an edit is called lightweight, its one-line why names what outside the diff reads what "
                      "changes, or \"nothing\", checked against that trigger list", rule)
        self.assertIn("a docs fix whose text only tests read stays lightweight", rule)

    def test_the_minimal_offer_shows_it_and_step_4b_names_private_callers(self):
        specify = " ".join((ROOT / "skills/workflow-specify/SKILL.md").read_text(encoding="utf-8").split())
        self.assertIn("a one-line why that names what outside the diff reads what changes, or \"nothing\"", specify)
        review = " ".join((ROOT / "skills/code-review/SKILL.md").read_text(encoding="utf-8").split())
        self.assertIn("deleting or replacing a function its callers use, private ones included", review)


if __name__ == "__main__":
    unittest.main()
