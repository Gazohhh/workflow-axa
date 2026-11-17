"""The /spar skill's contract (docs/plans/2026-11-17-spar-skill, agreement 6, ticket T11: rebuilt around SPAR.md).

These checks pin what the skill text states. They do not show that a model follows it: live runs (T6) do that.
"""
from __future__ import annotations

import importlib.util
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/spar/SKILL.md"
T3 = ROOT / "skills/spar/T3.md"
FILE = ROOT / "skills/spar/SPAR-FILE.md"


def text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""


class Registration(unittest.TestCase):
    """One owner-started command in both hosts; the workflow knows it but never runs it."""

    def test_registered_and_user_invoked_in_both_hosts(self):
        plugin = json.loads(text(ROOT / ".claude-plugin/plugin.json"))
        self.assertIn("./skills/spar", plugin["skills"])
        front = text(SKILL).split("---")[1]
        self.assertIn("name: spar", front)
        self.assertIn("disable-model-invocation: true", front)
        self.assertIn("allow_implicit_invocation: false", text(ROOT / "skills/spar/agents/openai.yaml"))

    def test_the_workflow_knows_it_but_never_runs_it(self):
        specialists = text(ROOT / "skills/workflow/SPECIALISTS.md")
        self.assertIn("`spar` (`../spar/SKILL.md`)", specialists)
        self.assertIn("user-invoked; recommended for high-stakes choices, never run by the workflow", specialists)
        clarify = text(ROOT / "skills/workflow-clarify/SKILL.md")
        self.assertIn("when the task links a SPAR.md (`docs/spar/`), an Approach part from `/spar`: the Handoff brief of that SPAR.md", clarify)
        self.assertIn("**Spar**", text(ROOT / "CONTEXT.md"))
        self.assertIn("| spar |", text(ROOT / "docs/RULE-CONTRACTS.md"))

    def test_the_old_split_records_are_gone(self):
        for old in ("SAVE.md", "RESULT.md"):
            with self.subTest(old=old):
                self.assertFalse((ROOT / "skills/spar" / old).exists())


class Contract(unittest.TestCase):
    """Agreement 6, R31-R40, by the words the skill must state."""

    skill, t3, file = text(SKILL), text(T3), text(FILE)

    def has(self, *phrases, where=None):
        body = self.skill if where is None else where
        for phrase in phrases:
            with self.subTest(phrase=phrase[:60]):
                self.assertIn(phrase, body)

    def test_purpose_and_what_it_never_does(self):
        self.has("an idea or a decision", "until you can choose a next move", "`/workflow` plans how",
                 "/spar never implements: no application or test changes, tickets or offers",
                 "Read [T3.md](T3.md) and [SPAR-FILE.md](SPAR-FILE.md) now")

    def test_r31_spar_md_is_the_record(self):
        self.has("`docs/spar/<date>-<topic>/SPAR.md`", "\"conversation only\"", "/spar is its own skill, not part of the workflow", where=self.file)
        self.has("During a workflow task, a kept SPAR.md still lives in `docs/spar/`", "that links it", "Update it after", where=self.file)
        self.has("SPAR.md is written with the editor tools", where=self.file)

    def test_r32_its_sections(self):
        for heading in ("## Current position", "## Intent and boundaries", "## Evidence", "## Options considered",
                        "## What changed our thinking", "## Owner decisions", "## Open questions and dissent",
                        "## Handoff brief"):
            with self.subTest(heading=heading):
                self.assertIn(heading, self.file)
        self.has("never a transcript", "\"none identified\"", "Revision <n>", where=self.file)

    def test_r33_the_flow(self):
        self.has("## 1. Understand", "## 2. Explore", "## 3. Challenge", "## 4. Decide",
                 "## 5. Conclusion and handoff", "doing nothing, a simpler way, or whether the need is real",
                 "the few disagreements that could change the outcome", "a pre-mortem",
                 "the uncertainty most likely to change the decision", "the cheapest credible test",
                 "\"no material uncertainty\"")

    def test_r34_the_owner_is_asked_as_soon_as_a_choice_is_askable(self):
        self.has("as soon as it becomes askable", "never a questionnaire at the end",
                 "answered, delegated with limits, deferred by the owner, or blocking", "Research what is objective")

    def test_r35_the_coordinators_labelled_recommendation(self):
        self.has("labelled \"coordinator's synthesis\"", "An unreviewed synthesis stays labelled unreviewed")
        self.has("coordinator recommendation", "each debater's assessment", "owner decision", where=self.file)

    def test_r36_effort_is_a_budget(self):
        self.has("quick (openings and 1 exchange)", "normal (3)", "thorough (5)", "standard and deep mean normal and thorough", "an explicit launch limit",
                 "say which open issue it would settle", "a partial conclusion and a recommended next move",
                 "`spar_default_depth`")

    def test_r37_debaters_and_one_model(self):
        self.has("`orchestrator_capabilities`", "`delegate_task`", "`claudeAgent`", "ask the owner how to proceed",
                 "single model, fresh context, not cross-model", "Never substitute a model on your own",
                 "A failed check is a failure, never \"GPT absent\"", "**Spar with me only**",
                 "self-critique", where=self.t3)

    def test_r38_how_it_ends(self):
        self.has("Agreement: both debaters and the owner accepted the exact text of the same proposal id", "never fake agreement",
                 "proceed, investigate, defer or abandon", "A cancel stops the debaters and asks nothing more")

    def test_r39_conclusion_first_then_the_handoff(self):
        self.has("\"Turn this into a workflow plan\" · \"Investigate <the uncertainty> first\" · "
                 "\"Continue sparring\" · \"Leave it here\"", "bounded investigation brief",
                 "running it needs its own approval", "whose PLAN links the SPAR.md revision", "authorizes planning only")
        self.has("## The conclusion", "before the handoff question", "`send_to_user`", where=self.file)

    def test_r40_what_stays(self):
        self.has("**Spar:** <idea> · effort <effort> (at most <n> launches) · <A> vs <B>",
                 "No debater starts before this line is shown", "neither sees the other's",
                 "check the cited evidence yourself", "agreement without evidence is not agreement",
                 "A credible safety, security or data-loss finding goes to the owner at once",
                 "the standing diagnostic allowance in `../rule-maker/rules/OPERATIONS.md`")
        self.assertNotIn("`Spar:", self.skill)
        self.assertNotIn("flows/bug.md", self.skill)

    def test_the_glossary_points_to_the_handoff_instead_of_restating_it(self):
        context = text(ROOT / "CONTEXT.md")
        term = context[context.index("**Spar**:"):]
        term = term[:term.index("\n\n")]
        self.assertNotIn("starts a task", term)
        self.assertIn("SKILL.md` step 5", term)
        self.assertIn("SPAR-FILE.md", term)

    def test_briefs_and_waiting(self):
        self.has("## The opening brief", "## The exchange brief", "## The synthesis brief", "challenge the framing",
                 "your verdict on each current proposal, by its id", "Never poll.",
                 "act on a round only when both have returned", where=self.t3)

    def test_keeping_spar_md_is_the_owners_choice(self):
        self.has("\"Keep a SPAR.md\" · \"Conversation only\"", "asks only what the command did not state",
                 "write SPAR.md first, since the plan links it")
        self.has("Create `docs/spar/<date>-<topic>/SPAR.md` when the owner chooses to keep one", where=self.file)
        self.assertNotIn("Start it when the owner starts /spar", self.skill)

    def test_an_agreed_task_is_reopened_only_by_the_owners_plan_choice(self):
        self.has("Leave the task's checkpoint as it is while sparring",
                 "A spar is during a task only when the owner names the task, or the idea changes the active task's "
                 "agreed scope. Otherwise it is outside any task; ask when unclear.",
                 "only when the owner then picks \"Turn this into a workflow plan\"",
                 "keep the task's previous next step in that line",
                 "Any other ending leaves the checkpoint unchanged", where=self.file)

    def test_conversation_only_writes_nothing_to_a_task(self):
        self.has("When it is first written, add one line to the task's FINDINGS",
                 "a conversation-only spar writes nothing to the task until the owner picks \"Turn this into a "
                 "workflow plan\"", where=self.file)

    def test_the_plan_handoff_outside_and_during_a_task(self):
        self.has("Outside a task: start `/workflow` with a new task in `docs/plans/`",
                 "During a task (SPAR-FILE.md \"Where it lives\"): continue that task's workflow-clarify with the "
                 "Handoff brief, and change its checkpoint only as SPAR-FILE.md says",
                 "write a bounded investigation brief into SPAR.md (in the conversation when conversation only)",
                 "can keep a SPAR.md")

    def test_small_rules_a_following_agent_needs(self):
        self.has("In T3 Code, send it with `send_to_user` or end the turn with it",
                 "a synthesis gets the id S1, S2 and so on")
        self.has("**End sparring**: cancel any debater still running; show the partial conclusion, then the handoff "
                 "question", "In this mode the frame names <A> vs <B> as \"you vs me\" and the launch limit as 0",
                 where=self.t3)
        self.has("(in the conversation when conversation only)", where=self.file)
        self.assertNotIn("WHAT and WHY", text(ROOT / "skills/spar/agents/openai.yaml"))

    def test_grilling_and_clarify_follow_the_spar_record(self):
        grilling = text(ROOT / "skills/grilling/SKILL.md")
        self.assertIn("During `/spar`, questions and answers go into its SPAR.md", grilling)
        self.assertNotIn("a `/spar` run outside a task", grilling)
        self.assertIn("Without a linked SPAR.md, leave this part out.", text(ROOT / "skills/workflow-clarify/SKILL.md"))

    def test_no_menu_label_reads_as_a_stop_to_the_hook(self):
        spec = importlib.util.spec_from_file_location("phase_gate_for_spar", ROOT / "hooks/phase_gate.py")
        gate = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(gate)
        for label in ("Turn this into a workflow plan", "Continue sparring", "Leave it here", "End sparring",
                      "Try again later", "Relaunch the failed debater", "Spar with me only"):
            with self.subTest(label=label):
                self.assertNotEqual(gate.control_intent(label), "pause")

    def test_the_skill_stays_small(self):
        """Raised on purpose for docs/plans/2026-11-17-spar-owner-in-loop: its rules added about 370 words."""
        self.assertLess(len(self.skill.split()), 1700)
        self.assertLess(len(self.t3.split()), 1200)
        self.assertLess(len(self.file.split()), 900)


class AgreementSeven(unittest.TestCase):
    """Agreement 7, R41-R44 (D35): the start card, until agreement, and a strict "agreed"."""

    skill, t3 = text(SKILL), text(T3)

    def has(self, *phrases, where=None):
        body = self.skill if where is None else where
        for phrase in phrases:
            with self.subTest(phrase=phrase[:60]):
                self.assertIn(phrase, body)

    def test_r41_one_start_card_for_what_the_command_left_out(self):
        self.has("**The start card**", "asks only what the command did not state",
                 "Quick (up to 6 launches) · Normal (up to 10) · Thorough (up to 14) · Until agreement",
                 "\"Keep a SPAR.md\" · \"Conversation only\"", "preselected, never used silently",
                 "No card when the command states all three", "No debater starts before the owner answers")
        self.has("a recommended pair from two different makers", "or the owner chooses A and B", where=self.t3)

    def test_r41_the_command_can_state_all_three_and_the_card_holds_the_cap(self):
        self.has("[quick|normal|thorough|N|until agreement <cap>] [<A> vs <B>] [keep a SPAR.md|conversation only]",
                 "Until agreement (cap 30, at most the launches left; another cap through Other)")
        self.has("Call `orchestrator_capabilities` once, before the start card",
                 "the card's debater field offers the menu below instead; no separate question", where=self.t3)
        self.assertNotIn("before the frame is final", self.t3)

    def test_r42_until_agreement_has_the_owners_cap_and_three_endings(self):
        self.has("**Until agreement**", "The cap comes from the command or the start card: 20 · 30 · 50 or a number, at least 6",
                 "deadlock (two consecutive exchanges in which neither debater brings new evidence, a new argument or "
                 "a changed position)", "each reported as itself",
                 "Start another exchange only while at least four launches remain; the last two go to a synthesis check "
                 "of the current best proposal, labelled S<n>", "Count every launch, failed ones and replacements too",
                 "When fewer launches remain than the next step needs, the cap is reached",
                 "never past the cap without the owner's OK", "A cap limits launches, not money",
                 "Until agreement ends only on agreement, deadlock or the cap, the owner's own direction (dissent "
                 "recorded), a cancel, or a debater that can't continue")

    def test_the_card_offers_only_the_launches_left_and_a_new_cap_is_above_those_used(self):
        """docs/plans/2026-11-17-plain-owner-questions T9: run 5's card offered cap 30 when the owner had 20 left."""
        self.has("at least 6, and never more than the owner has left", "A new cap must exceed the launches used.")

    def test_r42_continuing_and_one_model_never_pick_their_own_budget(self):
        self.has("**Continue sparring**: ask for more effort or a new cap with the start card's choices; an effort's "
                 "launches come on top of those spent, a cap counts every launch so far; show a new frame line, then go on")
        self.has("effort and cap don't apply; it is never \"agreed\", only a labelled recommendation",
                 "A retry or replacement never uses the last two launches of a cap unless the owner raises it",
                 "exchange <n> of <budget or cap>", "reason; an accept with amendments is a reject)", where=self.t3)

    def test_r43_agreed_means_the_exact_same_text(self):
        self.has("accepted the exact text of the same proposal id, without conditions or blockers",
                 "An accept with amendments rejects that version", "Any later edit voids the acceptance",
                 "the last version the debaters accepted")
        self.has("accept it as written, or reject it", "A replacement debater judges the current text itself",
                 where=self.t3)
        self.assertEqual(self.t3.lower().count("an accept with amendments is a reject"), 2)

    def test_r44_briefs_reward_justified_disagreement(self):
        self.assertEqual(self.t3.count("Justified disagreement is success; a changed position needs its reason."), 3)


class OwnerInTheLoop(unittest.TestCase):
    """docs/plans/2026-11-17-spar-owner-in-loop R1-R8: the owner decides and judges; the spar stops for the owner."""

    skill, t3, file = text(SKILL), text(T3), text(FILE)

    def has(self, *phrases, where=None):
        body = self.skill if where is None else where
        for phrase in phrases:
            with self.subTest(phrase=phrase[:60]):
                self.assertIn(phrase, body)

    def test_r1_roles_and_the_launch_rule(self):
        self.has("## Rules of the spar",
                 "The owner decides and judges; the two debaters argue; you moderate, check evidence and never decide "
                 "for the owner", "No launch whose brief depends on an open owner choice",
                 "and none while continuing would be unsafe")
        self.has("state the strongest argument for the other side before you rebut it", where=self.t3)

    def test_r2_grilling_before_the_openings(self):
        self.has("Before the openings, run one grilling round on the frontier of unsettled choices that shape the "
                 "opening brief", "a settled brief needs no question",
                 "With \"no interview\", show labelled options and leave them open")

    def test_r3_three_checkpoints_shown_before_the_question(self):
        self.has("a message the owner can read before the question tool opens",
                 "then ask in plain language and grilling's form",
                 "(a) after the openings, always: both opening cases, the disagreement most likely to change the outcome, "
                 "and an open \"your view?\"", "as soon as it becomes askable", "there is no fixed number of these stops",
                 "(c) the verdict: the exact proposal both debaters accepted, in full, with any remaining dissent",
                 "The owner may ask for a pause after every round or waive the optional ones",
                 "\"Spar with me only\" has no debaters, so (a) and (c) don't apply")
        self.assertNotIn("Pause only when an owner decision blocks the next step", self.skill)

    def test_r4_the_spar_waits(self):
        self.has("Wait for the owner's view or an explicit \"I have no feedback on the openings\" before the next launch",
                 "that answer clears this pause only, not an open owner choice",
                 "silence spends no launches", "\"Record answers\" what a reply settles",
                 "\"carry on\" releases an optional pause only",
                 "answered, delegated with limits, deferred by the owner, or blocking",
                 "after a deferral only work independent of it continues")
        self.has("launch the next round only as SKILL.md \"Rules of the spar\" allows", where=self.t3)

    def test_r5_sorting_points_to_grilling(self):
        self.has("with grilling (`../grilling/SKILL.md`): its table (\"Sort what you found\") says what you look up and "
                 "what only the owner decides", "\"How to ask\" how to ask", "Research what is objective")

    def test_r6_owner_decisions_bind_owner_opinions_are_challenged(self):
        self.has("An owner decision binds and goes into the next briefs as a decision",
                 "never into the opening brief", "may push back with reasons",
                 "a factual claim of the owner is checked like any other")
        self.has("Owner input since your last position:", "push back with reasons where you disagree", where=self.t3)
        self.has("Owner decisions so far (decisions only, no owner preference):", where=self.t3)
        self.has("Owner input since your last position: <as in the exchange brief>", where=self.t3)
        self.assertEqual(self.t3.count("new ones marked; they bind"), 2)

    def test_r7_agreed_needs_the_owner_and_the_verdict_costs_no_launch(self):
        self.has("Agreement: both debaters and the owner accepted the exact text of the same proposal id",
                 "even when the last launches are spent; it costs no launch",
                 "both debaters accepted; the owner's verdict is pending",
                 "The owner may instead choose a direction over both debaters, with their dissent recorded",
                 "starts another exchange only with a concrete issue and at least four launches left",
                 "the last version the debaters accepted is kept, and the owner's verdict is asked again",
                 "the owner's own direction (dissent recorded)")
        self.has("the owner's verdict on each proposal both debaters accepted",
                 "or agreed by both debaters and the owner", "the owner's direction over the debaters' dissent",
                 where=self.file)
        self.assertNotIn("Agreement: both debaters accepted the exact text", self.skill)
        self.assertNotIn("or agreed by both.", self.file)


class Scenarios(unittest.TestCase):
    """A8: live process scenarios; a result other than NOT_RUN names its evidence and candidate."""

    REQUIRED = ("real-idea", "owner-direction", "labelled-synthesis", "budget-spent", "one-model", "cancel",
                "record-choice", "handoff-in-task",
                "handoff", "spar-file", "start-card", "until-agreement", "owner-checkpoints")
    RESULTS = ("NOT_RUN", "OBSERVED", "PARTIAL", "FAILED", "NOT_PROVOKED")

    def setUp(self):
        self.data = json.loads(text(ROOT / "tests/behavioral/spar.json"))
        self.skill = text(SKILL) + text(T3) + text(FILE)

    def test_every_required_scenario_exists_and_a_result_needs_evidence(self):
        ids = [c["id"] for c in self.data["scenarios"]]
        self.assertEqual(len(ids), len(set(ids)))
        for required in self.REQUIRED:
            self.assertIn(required, ids)
        findings = text(ROOT / "docs/plans/2026-11-17-spar-skill/FINDINGS.md")
        for case in self.data["scenarios"]:
            with self.subTest(case=case["id"]):
                self.assertEqual(case["mode"], "live-host")
                self.assertIn(case["result"], self.RESULTS)
                self.assertTrue(case["setup"] and case["process_checks"])
                if case["result"] != "NOT_RUN":
                    self.assertTrue(case.get("candidate"))
                    cited = re.findall(r"\b([OV]\d+)\b", case.get("evidence", ""))
                    self.assertTrue(cited)
                    for line in cited:
                        self.assertRegex(findings, rf"(?m)^- {line}\b")

    def test_no_scenario_prescribes_the_answer(self):
        for case in self.data["scenarios"]:
            with self.subTest(case=case["id"]):
                self.assertIs(case["prescribed_answer"], None)

    def test_each_scenario_names_rules_the_skill_states(self):
        for case in self.data["scenarios"]:
            for rule in case["rules"]:
                with self.subTest(case=case["id"], rule=rule[:40]):
                    self.assertIn(rule, self.skill)


if __name__ == "__main__":
    unittest.main()
