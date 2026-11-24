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
SKILL_CEILING, T3_CEILING, FILE_CEILING = 1740, 1100, 760


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
        self.has("quick (openings and 1 exchange)", "normal (3)", "thorough (5)", "an explicit launch limit",
                 "say which open issue it would settle", "a partial conclusion and a recommended next move",
                 "`spar_default_depth`")

    def test_r37_debaters_and_one_model(self):
        self.has("`orchestrator_capabilities`", "`delegate_task`", "`claudeAgent`", "ask the owner how to proceed",
                 "single model, fresh context, not cross-model", "Never substitute a model on your own",
                 "A failed check is a failure, never \"GPT absent\"", "**Spar with me only**",
                 "self-critique", where=self.t3)

    def test_r38_how_it_ends(self):
        self.has("never fake agreement", "A bounded spar ends when the owner can choose a next move (proceed, investigate, "
                 "defer or abandon); dissent is a valid ending", "A cancel stops the debaters and asks nothing more",
                 "a cancel, a provider failure and a spent budget are each reported as themselves")

    def test_r39_conclusion_first_then_the_handoff(self):
        self.has("\"Turn this into a workflow plan\" · \"Investigate <the uncertainty> first\" · "
                 "\"Continue sparring\" · \"Leave it here\"", "bounded investigation brief",
                 "running it needs its own approval", "whose PLAN links the SPAR.md revision", "authorizes planning only")
        self.has("## The conclusion", "before the handoff question", "`send_to_user`", where=self.file)

    def test_r40_what_stays(self):
        self.has("**Spar:** <idea> · effort <effort> (at most <n> launches) · <A> vs <B>",
                 "a receipt that needs no reply, sent in the same turn as the first launch and before it",
                 "neither sees the other's",
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
        self.has("## The opening brief", "## The exchange brief", "challenge the framing",
                 "for each decision point: agree, disagree or mis-framed", "Never poll.",
                 "act on a round only when both have returned", where=self.t3)
        self.assertNotIn("## The synthesis brief", self.t3)

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
        self.has("In T3 Code, send it with `send_to_user` or end the turn with it")
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
        """Set for docs/plans/2026-11-20-spar-rework T2 just above the sizes reached (SKILL 1,677, T3 1,060,
        SPAR-FILE 737 words); the agreed rules, not the estimates, set them."""
        self.assertLess(len(self.skill.split()), SKILL_CEILING)
        self.assertLess(len(self.t3.split()), T3_CEILING)
        self.assertLess(len(self.file.split()), FILE_CEILING)


class AgreementSeven(unittest.TestCase):
    """Agreement 7, R41-R44 (D35), as reworked by docs/plans/2026-11-20-spar-rework: the start card, until agreement
    and a mechanical "agreed"."""

    skill, t3 = text(SKILL), text(T3)

    def has(self, *phrases, where=None):
        body = self.skill if where is None else where
        for phrase in phrases:
            with self.subTest(phrase=phrase[:60]):
                self.assertIn(phrase, body)

    def test_r41_one_start_card_for_what_the_command_left_out(self):
        self.has("**The start card**", "asks only what the command did not state",
                 "Quick (up to 4 launches) · Normal (up to 8) · Thorough (up to 12) · Until agreement",
                 "\"Keep a SPAR.md\" · \"Conversation only\"", "preselected, never used silently",
                 "3 to 6 proposed success criteria, which \"yes\" accepts",
                 "only the open choices that shape the opening brief",
                 "No card when the command states all three", "No debater starts before the owner answers")
        self.has("a recommended pair from two different makers", "or the owner chooses A and B", where=self.t3)

    def test_r41_the_command_can_state_all_three_and_the_card_holds_the_cap(self):
        self.has("[quick|normal|thorough|N|until agreement <cap>] [<A> vs <B>] [keep a SPAR.md|conversation only]",
                 "Until agreement (cap 30, at most the launches left; another cap through Other)")
        self.has("Call `orchestrator_capabilities` once, before the start card",
                 "the card's debater field offers the menu below instead; no separate question", where=self.t3)
        self.assertNotIn("before the frame is final", self.t3)

    def test_r42_until_agreement_is_one_opt_in_rule(self):
        """docs/plans/2026-11-20-spar-rework R2: one rule, deadlock and the cap reported apart, no cap tiers."""
        self.has("**Until agreement**", "is opt-in", "ends when every decision point is agreed or in deadlock",
                 "changed position), at the cap, or by the owner's decision", "deadlock (a point on which two consecutive exchanges brought no new "
                 "evidence, argument or changed position)", "deadlock and the cap are reported separately",
                 "The cap comes from the command or the start card", "Count every launch, failed ones and replacements too",
                 "When fewer launches remain than the next exchange needs, the cap is reached",
                 "never past the cap without the owner's OK", "A cap limits launches, not money")
        self.assertNotIn("20 · 30 · 50", self.skill)
        self.assertNotIn("synthesis check", self.skill + self.t3)

    def test_the_card_offers_only_the_launches_left_and_a_new_cap_is_above_those_used(self):
        """docs/plans/2026-11-17-plain-owner-questions T9: run 5's card offered cap 30 when the owner had 20 left."""
        self.has("at least 6, and never more than the owner has left", "A new cap must exceed the launches used.")

    def test_r42_continuing_and_one_model_never_pick_their_own_budget(self):
        self.has("**Continue sparring**: ask for more effort or a new cap with the start card's choices; an effort's "
                 "launches come on top of those spent, a cap counts every launch so far; show a new frame line, then go on")
        self.has("effort and cap don't apply; it is never \"agreed\", only a labelled recommendation",
                 "exchange <n> of <budget or cap>", where=self.t3)
        self.assertNotIn("last two launches", self.skill + self.t3)

    def test_r43_agreement_is_on_decision_points_and_the_label_is_mechanical(self):
        """docs/plans/2026-11-20-spar-rework R1: agreement on ideas, not on exact text; the label stays mechanical."""
        self.has("decision points", "agree, disagree or mis-framed", "may split a point or add one",
                 "one line in its own words", "quoted verbatim",
                 "Label a point \"both debaters agree\" only when both answered agree to the identical point text and "
                 "neither quote adds a condition the other lacks", "otherwise show the two quotes without a label",
                 "inside an exchange the budget or cap still allows; when none remains, the point stays unresolved",
                 "The owner's verdict is separate and always explicit")
        self.has("A replacement debater answers every open decision point itself", where=self.t3)
        everything = (self.skill + self.t3 + text(FILE)).lower()
        for removed in ("exact text", "accept with amendments", "voids the acceptance", "synthesis brief",
                        "accept it as written", "s<n>", "s1, s2"):
            with self.subTest(removed=removed):
                self.assertNotIn(removed, everything)

    def test_r44_briefs_reward_justified_disagreement(self):
        briefs = self.t3.count("```text")
        self.assertEqual(briefs, 2)
        self.assertEqual(self.t3.count("Justified disagreement is success; a changed position needs its reason."), briefs)


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
        """docs/plans/2026-11-20-spar-rework R3: the grilling round before the openings now rides on the start card."""
        self.has("only the open choices that shape the opening brief (outcome, boundaries, trade-offs)",
                 "a settled brief needs no question", "with \"no interview\", show labelled options and leave them open")

    def test_r3_three_checkpoints_shown_before_the_question(self):
        self.has("a message the owner can read before the question tool opens",
                 "then ask in plain language and grilling's form",
                 "(a) after the openings, always: both opening cases, the disagreement most likely to change the outcome, "
                 "and an open \"your view?\"", "as soon as it becomes askable", "there is no fixed number of these stops",
                 "(c) the verdict, at the ending:",
                 "every owner choice that can be asked now is asked in the same message, not one by one afterwards",
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
                 "An owner's factual claim goes into the briefs from the first exchange on, marked \"not yet checked\"",
                 "the debaters check it or say they could not")
        self.has("Owner input since your last position:", "push back with reasons where you disagree", where=self.t3)
        self.has("Owner decisions so far (decisions only, no owner preference):", where=self.t3)
        self.assertEqual(self.t3.count("new ones marked; they bind"), 1)
        self.assertEqual(self.t3.count("marked \"not yet checked\""), 2)

    def test_r7_agreed_needs_the_owner_and_the_verdict_costs_no_launch(self):
        self.has("it costs no launch", "The owner may instead choose a direction over both debaters, with their dissent recorded",
                 "starts another exchange only with a concrete issue and launches left for it")
        self.has("the owner's verdict on the points both debaters agree on",
                 "or agreed by both debaters and the owner", "It never states the owner's agreement",
                 where=self.file)
        self.assertNotIn("or agreed by both.", self.file)


class SparRework(unittest.TestCase):
    """docs/plans/2026-11-20-spar-rework T2 (R1-R7): ideas, fewer stops, evidence first, focused debaters."""

    skill, t3, file = text(SKILL), text(T3), text(FILE)

    def has(self, *phrases, where=None):
        body = " ".join((self.skill if where is None else where).split())
        for phrase in phrases:
            with self.subTest(phrase=phrase[:60]):
                self.assertIn(phrase, body)

    def test_r3_one_start_card_and_the_frame_is_a_receipt(self):
        self.has("the debaters (T3.md \"Who debates\")", "the record: \"Keep a SPAR.md\" · \"Conversation only\"",
                 "a receipt that needs no reply")
        self.assertNotIn("a setting to skip", self.skill.lower())

    def test_the_conclusion_never_claims_the_owners_agreement_before_the_card(self):
        """Review S1, defect 1: the verdict is asked after the conclusion, so the conclusion can't state it."""
        self.has("\"both debaters agree; the owner's verdict is pending\"", "It never states the owner's agreement",
                 where=self.file)
        self.assertNotIn("1. The outcome (agreed by both debaters and the owner", self.file)
        self.has("only after the answer does SPAR.md say \"agreed by both debaters and the owner\"")

    def test_the_card_is_skipped_only_when_the_criteria_are_settled(self):
        """Review S1, defect 2: a fully stated command must not skip the success criteria."""
        self.has("No card when the command states all three, the success criteria are settled,")

    def test_owner_claims_stay_out_of_the_independent_openings(self):
        self.has("An owner's factual claim goes into the briefs from the first exchange on, marked \"not yet checked\"")
        self.assertNotIn("the opening brief included", self.skill)

    def test_r4_an_evidence_step_before_the_openings(self):
        self.has("## 1. Understand and gather the evidence", "the `research` specialist when installed",
                 "outside sources included", "verify the decisive claim yourself before it counts",
                 "the observation that would falsify it and the cheapest check", "\"Investigate first\"")
        self.has("owner claims marked \"not yet checked\"", where=self.file)

    def test_r5_the_card_warns_when_only_one_model_debates(self):
        self.has("When only one model can debate, the card says that helpers of the same model tend to agree at once")

    def test_r6_plain_titles_live_disagreements_and_the_trade_off_first(self):
        self.has("Plain titles for the owner; ids only in the record")
        self.has("each side's current claim, its strongest objection and its source",
                 "what would change your mind on each point still disputed, or \"none\"", where=self.t3)
        self.assertNotIn("<in full>", self.t3)
        self.has("2. The decisive trade-off", "a table only when several criteria separate the options",
                 "both debaters' lines quoted verbatim", where=self.file)
        self.assertNotRegex(self.skill + self.t3, r"\b(standard|deep)\b")

    def test_r7_every_brief_keeps_the_debater_to_its_task(self):
        briefs = self.t3.count("```text")
        self.assertEqual(self.t3.count("This brief is your whole task: read only, load no skills, ask no one."), briefs)

    def test_labels_point_to_the_one_writing_rule(self):
        self.has("`../workflow/WRITING.md` \"Chat replies\" rule 7", where=self.file)
        writing = text(ROOT / "skills/workflow/WRITING.md")
        self.assertRegex(writing, r"(?m)^7\. A label .* comes after its plain meaning")
        for body in (self.skill, self.t3, self.file):
            self.assertNotIn("comes after its plain meaning", body)


class Scenarios(unittest.TestCase):
    """A8: live process scenarios; a result other than NOT_RUN names its evidence and candidate."""

    REQUIRED = ("real-idea", "owner-direction", "labelled-synthesis", "budget-spent", "one-model", "cancel",
                "record-choice", "handoff-in-task",
                "handoff", "spar-file", "start-card", "until-agreement", "owner-checkpoints",
                "incompatible-agree", "restatement-at-the-last-exchange", "part-fails-before-a-question",
                "unchecked-owner-claim", "same-model-helpers")
    RESULTS = ("NOT_RUN", "OBSERVED", "PARTIAL", "FAILED", "NOT_PROVOKED")

    def setUp(self):
        self.data = json.loads(text(ROOT / "tests/behavioral/spar.json"))
        self.skill = text(SKILL) + text(T3) + text(FILE)

    def test_every_required_scenario_exists_and_a_result_needs_evidence(self):
        ids = [c["id"] for c in self.data["scenarios"]]
        self.assertEqual(len(ids), len(set(ids)))
        for required in self.REQUIRED:
            self.assertIn(required, ids)
        for case in self.data["scenarios"]:
            with self.subTest(case=case["id"]):
                self.assertEqual(case["mode"], "live-host")
                self.assertIn(case["result"], self.RESULTS)
                self.assertTrue(case["setup"] and case["process_checks"])
                if case["result"] != "NOT_RUN":
                    self.assertTrue(case.get("candidate"))
                    cited = re.findall(r"\b([OV]\d+)\b", case.get("evidence", ""))
                    self.assertTrue(cited)
                    findings = text(self.findings_of(case.get("evidence", "")))
                    for line in cited:
                        self.assertRegex(findings, rf"(?m)^- {line}\b")

    @staticmethod
    def findings_of(evidence: str) -> Path:
        """Evidence ids are looked up in the task the evidence names; without a name, the /spar skill's own task."""
        named = re.search(r"docs/plans/[\w.-]+", evidence)
        return ROOT / (named.group(0) if named else "docs/plans/2026-11-17-spar-skill") / "FINDINGS.md"

    def test_evidence_ids_are_looked_up_in_the_named_task_only(self):
        case = next(c for c in self.data["history"] if c["id"] == "owner-checkpoints")
        self.assertEqual(self.findings_of(case["evidence"]),
                         ROOT / "docs/plans/2026-11-17-spar-owner-in-loop/FINDINGS.md")
        self.assertRegex(text(self.findings_of(case["evidence"])), r"(?m)^- V3 T2 live check")
        self.assertEqual(self.findings_of("O4: no task named"),
                         ROOT / "docs/plans/2026-11-17-spar-skill/FINDINGS.md")

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
