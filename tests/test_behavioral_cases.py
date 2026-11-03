"""Validate evaluation inputs, not the model behaviors they describe."""
from __future__ import annotations
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from tools.create_fixture import ROOT, SCENARIOS, create_fixture

class EvaluationInputTests(unittest.TestCase):
    def test_cases_are_unique_supported_and_unrun(self):
        suite=json.loads((ROOT/'tests/behavioral/cases.json').read_text())
        ids=[case['id'] for case in suite['cases']]
        self.assertEqual(len(ids),len(set(ids)))
        for case in suite['cases']:
            with self.subTest(case=case['id']):
                self.assertIn(case['fixture'],SCENARIOS)
                self.assertTrue(case['prompt'].strip())
                self.assertTrue(case['expect'])
                self.assertEqual(case['result'],'NOT_RUN')
        self.assertEqual(suite['baseline_version'],'2.6.0')

    def test_shipped_visual_reference_integrity(self):
        from tools.visual_regression import load_capture
        reference=load_capture(ROOT/'tests/visual-baselines/2.2.1')
        self.assertEqual(len(reference['cases']),4)
        self.assertEqual(reference['provenance']['package_version'],'2.2.1')

    def test_behavior_results_not_mislabelled_as_tool_passes(self):
        result=json.loads((ROOT/'tests/evidence/behavioral-results.json').read_text())
        self.assertEqual(result['status'],'NOT_RUN')
        self.assertTrue(all(c['status']=='NOT_RUN' for c in result['cases']))

    @unittest.skipUnless(shutil.which('git'),'Git unavailable')
    def test_related_task_context_is_discoverable_without_oracle(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo=create_fixture(Path(tmp)/'repo','related-task')
            plans=list((repo/'docs/plans').glob('*/PLAN.md'))
            self.assertEqual(len(plans),1)
            self.assertIn('Display quality',plans[0].read_text())
            self.assertFalse((repo/'tests/behavioral').exists())
            self.assertFalse((repo/'cases.json').exists())
            self.assertIn('only auto is supported',(repo/'src/quality.py').read_text())

    @unittest.skipUnless(shutil.which('git'),'Git unavailable')
    def test_ambiguous_tasks_really_differ(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo=create_fixture(Path(tmp)/'repo','multiple-tasks')
            content='\n'.join(p.read_text() for p in (repo/'docs/plans').glob('*/PLAN.md'))
            self.assertIn('local low/high',content)
            self.assertIn('frame times',content)
            self.assertEqual(len(list((repo/'docs/plans').glob('*/PLAN.md'))),2)

    @unittest.skipUnless(shutil.which('git'),'Git unavailable')
    def test_completed_task_preserves_historical_outcome(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo=create_fixture(Path(tmp)/'repo','completed-task')
            text=next((repo/'docs/plans').glob('*/PLAN.md')).read_text()
            self.assertIn('Status: done',text)
            self.assertIn('does not authorize a new feature',text)

    @unittest.skipUnless(shutil.which('git'),'Git unavailable')
    def test_answered_task_has_actual_synthetic_answers(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo=create_fixture(Path(tmp)/'repo','answered-task')
            text=next((repo/'docs/plans').glob('*/DECISIONS.md')).read_text()
            self.assertIn('reset on restart',text)
            self.assertIn('ValueError',text)
            self.assertIn('Synthetic user-approved',text)

class InstructionRegressionTests(unittest.TestCase):
    """Guard text contracts from accidental removal; these do not prove obedience."""
    def text(self,name):return (ROOT/'skills/workflow'/name).read_text()

    def test_proactive_trigger_and_no_quota_are_explicit(self):
        self.assertIn('every new substantive goal',(ROOT/'skills/grilling/SKILL.md').read_text())
        self.assertIn('there is no minimum question count',(ROOT/'skills/grilling/SKILL.md').read_text())
        self.assertIn('detailed prompt',self.text('SPECIALISTS.md'))

    def test_existing_task_match_not_restricted_to_exact_scope(self):
        text=self.text('TASK-FOLDER.md')
        self.assertNotIn('Continue only an exact goal/scope match',text)
        for term in ('Several plausible tasks','Related task is complete','No relevant record','scope extension','ownership'):
            self.assertIn(term,text)

    def test_approval_and_partial_answers_are_separate(self):
        self.assertIn('A partial reply settles only addressed items',(ROOT/'skills/grilling/SKILL.md').read_text())
        self.assertIn('STOP for user approval',self.text('SKILL.md'))
        self.assertIn('not approval of an unseen plan',self.text('SKILL.md'))

    def test_router_invokes_phases_instead_of_running_them(self):
        # E1 evaluation: an agent ran clarification from the routing table and treated grilling answers as agreement.
        router=self.text('SKILL.md')
        self.assertIn('never run a phase from it',router)
        # A9: the router was loaded but no phase skill was invoked.
        self.assertIn('your next action is invoking the phase skill',router)
        # A10 then D13: the identity question goes with clarify's first questions, never with approvals.
        self.assertIn('which asks "separate task or revision?" with its first questions',router)
        self.assertIn('never ask it alongside approvals',(ROOT/'skills/workflow-clarify/SKILL.md').read_text())
        # Design loop: identity-pending questions existed only in chat (W2 bug again); save them in an identity-pending folder.
        self.assertIn('identity pending (vs <related task>)',self.text('TASK-FOLDER.md'))
        # Design loop: questions bundled into a readiness stop were never saved; ui-design skipped for a UI change.
        self.assertIn('ask only the readiness choice and stop',self.text('RULES.md'))
        self.assertIn('first read `../ui-design/SKILL.md` and `../rule-maker/rules/design.md`, then trace',(ROOT/'skills/workflow-clarify/SKILL.md').read_text())
        self.assertIn('A script hook is not styling',(ROOT/'skills/rule-maker/rules/design.md').read_text())
        # Design retro: reference files still taught the strict-kit model, and a plan offered new CSS as an option.
        stale={'skills/codebase-map/UI-FLOW.md':('omit the screen view','requires `approved-kit`, real captures','No new application layout sketches'),
               'skills/workflow/VISUAL-REVIEW.md':('missing kit evidence keeps the UI review a draft','plain-control stand-ins'),
               'skills/ui-design/VERIFY.md':('not an allow-list of class names','not a legitimate fallback'),
               'skills/ui-design/EXAMPLES.md':('Which existing kit or pattern should I use',)}
        for path,phrases in stale.items():
            for phrase in phrases:
                with self.subTest(path=path,phrase=phrase):self.assertNotIn(phrase,(ROOT/path).read_text(encoding='utf-8'))
        for path in ('skills/workflow/SKILL.md','skills/workflow-clarify/SKILL.md','skills/workflow-specify/SKILL.md'):
            text=(ROOT/path).read_text(encoding='utf-8')
            self.assertRegex(text,r'(?i)never (offer|write or offer|include) new CSS',path)
        self.assertIn('never an option the rules forbid',(ROOT/'skills/grilling/SKILL.md').read_text(encoding='utf-8'))
        # Design round 4: specify asked whether to delete the replaced, presented review-r1.
        self.assertIn('delete or offer to delete a presented',(ROOT/'skills/workflow/VISUAL-REVIEW.md').read_text(encoding='utf-8'))
        # Round-4 retro: copied pill lost its parent-scoped look; a placement answer bypassed gate one.
        self.assertIn('Mirror the element, with its context',(ROOT/'skills/rule-maker/rules/design.md').read_text(encoding='utf-8'))
        self.assertIn('scripts/class_rules.py',(ROOT/'skills/ui-design/SKILL.md').read_text(encoding='utf-8'))
        specify=(ROOT/'skills/workflow-specify/SKILL.md').read_text(encoding='utf-8')
        self.assertIn('changes the agreement: write a new agreement revision',specify)
        self.assertIn('so a needed check is never dropped silently',specify)
        execute=(ROOT/'skills/workflow-execute/SKILL.md').read_text(encoding='utf-8')
        self.assertIn('hand every ticket, even a single one, to a fresh worker',execute)
        self.assertIn('Stop and ask which worktree is meant',(ROOT/'skills/workflow/TASK-FOLDER.md').read_text(encoding='utf-8'))
        # Round-5 retro: project rule missed until review; context difference recommended anyway; open finding ticked.
        self.assertIn('- **Rules**: the project rules',(ROOT/'skills/workflow-specify/SKILL.md').read_text(encoding='utf-8'))
        self.assertIn('a project rule for new code wins over an older neighbour',(ROOT/'skills/rule-maker/rules/CORE.md').read_text(encoding='utf-8'))
        self.assertIn('never recommend the copy anyway',(ROOT/'skills/rule-maker/rules/design.md').read_text(encoding='utf-8'))
        self.assertIn('with no open review finding',(ROOT/'skills/workflow-deliver/SKILL.md').read_text(encoding='utf-8'))
        self.assertIn('name only rule files you actually opened',(ROOT/'skills/workflow/RULES.md').read_text(encoding='utf-8'))
        # Round-6 check: saved Q6 recommended a, the sent message recommended b.
        self.assertIn('saved and sent options and recommendations match exactly',(ROOT/'skills/grilling/SKILL.md').read_text(encoding='utf-8'))
        # Round-6 retro: plan changed agreed timing yet said it matched; sketch promised to show the look.
        self.assertIn('First compare every ticket with the agreement line by line',(ROOT/'skills/workflow-specify/SKILL.md').read_text(encoding='utf-8'))
        self.assertIn('A sketch shows structure, not the look',(ROOT/'skills/ui-design/SKILL.md').read_text(encoding='utf-8'))
        # Round-6b retro: delivery reread the agreement, shipped a user-decision fix, overclaimed passes.
        deliver=(ROOT/'skills/workflow-deliver/SKILL.md').read_text(encoding='utf-8')
        self.assertIn('Reading the agreement differently from its words is a gap',deliver)
        self.assertIn('run the reconciliation in a fresh one',deliver)
        self.assertIn('A finding the reviewer calls a user decision',(ROOT/'skills/workflow-execute/SKILL.md').read_text(encoding='utf-8'))
        self.assertIn('names any failures it already had',(ROOT/'skills/workflow/WRITING.md').read_text(encoding='utf-8'))
        # Old-docs test: resume offered to rewrite an old review JSON to 'approved'.
        self.assertIn('never edit or offer to edit an old report',(ROOT/'skills/resume-task/SKILL.md').read_text())
        # Design loop: plan and delivery of a capturable page used sketches only.
        self.assertIn('real captures of the built result',(ROOT/'skills/workflow-deliver/SKILL.md').read_text())
        self.assertIn('capture the current screen when it opens safely',(ROOT/'skills/workflow-specify/SKILL.md').read_text())
        self.assertIn('Answering grilling questions is not agreement',router)
        rows=[line for line in router.splitlines() if line.startswith('| ') and '`workflow-' in line]
        self.assertLess([i for i,r in enumerate(rows) if 'workflow-deliver' in r][0],[i for i,r in enumerate(rows) if 'workflow-execute' in r][0],
                        'stopped work must reach delivery before execute matches')

    def test_phase_skills_resolve_their_sibling_workflow_folder(self):
        for phase in ('clarify','specify','execute','deliver'):
            text=(ROOT/f'skills/workflow-{phase}/SKILL.md').read_text()
            self.assertIn('`../workflow/` from this SKILL.md',text)
            self.assertNotIn('different package version',text)

    def test_retro_findings_stay_fixed(self):
        # Retro over 55 real sessions (FINDINGS E16): each rule answers a measured friction pattern.
        router=self.text('SKILL.md')
        self.assertIn('**Waiting on you**',router)
        self.assertIn('unless the host will wake you',router)
        self.assertIn('offer a fresh session',router)
        # A5: a fully specified visible change was wrongly treated as lightweight after the rewrite.
        self.assertIn('A visible behavior change, however small and fully specified, is not lightweight',router)
        self.assertIn('Handoff message',self.text('CHATGPT-PROMPTS.md'))
        questions=(ROOT/'skills/grilling/SKILL.md').read_text()
        self.assertIn('is an open choice, never a delegated detail',questions)
        self.assertIn('`by: agent`',questions)
        self.assertIn('standing answers',questions)
        self.assertIn('structured multiple-choice',questions)
        # W2: a later session could not read "Q1 a" because only the question, not its options, was saved.
        self.assertIn('with its exact options, letters and recommendation',questions)
        # E30 retro: tools named where records are written; reviewers labelled correctly.
        self.assertIn('never a shell heredoc',self.text('TASK-FOLDER.md'))
        self.assertIn('task_report.py scaffold',(ROOT/'skills/workflow-deliver/SKILL.md').read_text())
        self.assertIn('independent, axes sequential',(ROOT/'skills/code-review/SKILL.md').read_text())
        self.assertIn("I don't need to see the plan",self.text('VISUAL-REVIEW.md'))
        self.assertIn('needs human',(ROOT/'skills/workflow-specify/SKILL.md').read_text())
        execute=(ROOT/'skills/workflow-execute/SKILL.md').read_text()
        self.assertIn('Run every ready ticket whose files overlap nothing running',execute)
        # A6 s2: self-review despite subagents, and no deliver after execution.
        self.assertIn('the reviewer must be a fresh subagent that reads that file',execute)
        self.assertIn('Execution is done only when deliver has run',execute)
        self.assertIn('(full suites included) once before changing anything',execute)
        self.assertIn('goes to the user before you ship it',execute)
        self.assertIn('read `../tdd/SKILL.md` before the first test',execute)
        gates=self.text('VISUAL-REVIEW.md')
        # D11: the owner wants the HTML report even for small changes unless they explicitly decline it.
        self.assertIn('Every gate-two request comes with a fresh HTML report',gates)
        self.assertIn('(one-line changes included)',(ROOT/'skills/workflow-specify/SKILL.md').read_text())
        # A8: clarify asked for both gates itself (no specify, no report) and copied earlier revisions.
        self.assertIn('Clarify never asks for plan approval itself',(ROOT/'skills/workflow-clarify/SKILL.md').read_text())
        # A11: clarify invited approval of an unseen plan, copying another task's habit.
        self.assertIn("Never invite approval of a plan the user hasn't seen",(ROOT/'skills/workflow-clarify/SKILL.md').read_text())
        # W1/W2 (D14 goal): visible changes skipped ui-design, so their reports had no screen diagram.
        self.assertIn('anything a user sees on screen (order, text, which rows or items show',(ROOT/'skills/workflow-clarify/SKILL.md').read_text())
        self.assertIn("also needs the report's screen diagram",(ROOT/'skills/workflow-specify/SKILL.md').read_text())
        self.assertIn('An earlier revision that skipped a step is not a precedent',self.text('TASK-FOLDER.md'))
        self.assertIn('Both gates in one message',gates)
        self.assertIn('Only an explicit yes to both records both lines',gates)
        deliver=(ROOT/'skills/workflow-deliver/SKILL.md').read_text()
        self.assertIn('Done when all three exist',deliver)
        self.assertIn('whenever the task has any HTML report',deliver)
        self.assertIn('open_items.py',deliver)
        self.assertIn('`by: agent`',deliver)

    def test_plain_language_is_in_both_entrypoints(self):
        self.assertIn('someone new to the project',self.text('SKILL.md'))
        self.assertIn('reader new to the project',(ROOT/'skills/codebase-map/SKILL.md').read_text())
        self.assertIn('Cold-reader check',self.text('WRITING.md'))

    def test_optional_helpers_not_required_inventory(self):
        data=json.loads((ROOT/'skills/workflow/specialists.json').read_text())
        for name in ('skill-creator','webapp-testing','diagram-design'):
            self.assertNotIn(name,data['skills'])
        self.assertIn('Missing optional helpers never block',self.text('OPTIONAL-HELPERS.md'))

if __name__=='__main__':unittest.main()
