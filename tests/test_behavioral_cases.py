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
        self.assertEqual(suite['baseline_version'],'2.4.0')

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
        self.assertIn('every new substantive goal',self.text('QUESTIONS.md'))
        self.assertIn('there is no minimum question count',self.text('QUESTIONS.md'))
        self.assertIn('detailed prompt',self.text('SPECIALISTS.md'))

    def test_existing_task_match_not_restricted_to_exact_scope(self):
        text=self.text('TASK-FOLDER.md')
        self.assertNotIn('Continue only an exact goal/scope match',text)
        for term in ('Several plausible tasks','Related task is complete','No relevant record','scope extension','ownership'):
            self.assertIn(term,text)

    def test_approval_and_partial_answers_are_separate(self):
        self.assertIn('A partial reply settles only addressed items',self.text('QUESTIONS.md'))
        self.assertIn('STOP for user approval',self.text('SKILL.md'))
        self.assertIn('not approval of an unseen plan',self.text('SKILL.md'))

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
