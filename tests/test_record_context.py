"""Check optional report projections and instruction contracts, not model obedience."""
from __future__ import annotations
import copy
import importlib.util
import json
import re
import shutil
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skills/codebase-map'
spec = importlib.util.spec_from_file_location('record_context_renderer', SKILL/'scripts/render_report.py')
report = importlib.util.module_from_spec(spec)
spec.loader.exec_module(report)

class RecordContextTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)/'source'
        shutil.copytree(SKILL/'examples', self.root)
        self.data = json.loads((self.root/'task-overview.json').read_text())
        self.path = self.root/'candidate.json'

    def render(self):
        self.path.write_text(json.dumps(self.data, ensure_ascii=False), encoding='utf-8')
        return report.render(self.data, self.root, self.path)

    def test_old_schema_two_has_no_new_required_fields(self):
        self.data = json.loads((self.root/'review.json').read_text())
        output = self.render()
        self.assertIn('AWAITING USER APPROVAL', output)
        self.assertNotIn('id="checkpoint-heading"', output)
        self.assertNotIn('id="revision-history"', output)

    def test_overview_has_separate_states_and_no_approval_request(self):
        out = self.render()
        for label in ('Approval', 'Implementation', 'Verification / acceptance', 'Next safe action', 'As recorded:'):
            self.assertIn(label, out)
        self.assertIn('SAVED TASK OVERVIEW', out)
        self.assertIn('Authority stays in the task record.', out)
        self.assertNotIn('Approve plan P1 in the agent conversation', out)
        self.assertIn('Baseline before the selected change', out)
        self.assertNotIn('Proposed — not implemented', out)

    def test_original_report_and_sources_are_not_changed(self):
        before = {p.relative_to(self.root):p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        self.render()
        self.assertTrue(all((self.root/p).read_bytes()==b for p,b in before.items()))

    def test_geometry_is_identical_to_prior_review(self):
        self.assertEqual(self.data['graphs'],json.loads((self.root/'review.json').read_text())['graphs'])

    def test_missing_checkpoint_in_overview_fails(self):
        del self.data['checkpoint']
        with self.assertRaisesRegex(ValueError,'sourced checkpoint'): self.render()

    def test_missing_source_fails(self):
        self.data['checkpoint']['source']='S999'
        with self.assertRaisesRegex(ValueError,'supplied source'): self.render()

    def test_approval_cannot_be_invented_by_missing_revision(self):
        del self.data['checkpoint']['approval']['revision']
        with self.assertRaisesRegex(ValueError,'exact covered revision'): self.render()

    def test_unknown_authority_does_not_name_approved_revision(self):
        self.data['checkpoint']['approval']['status']='unknown'
        with self.assertRaisesRegex(ValueError,'unknown/unapproved'): self.render()

    def test_unknown_authority_is_explicitly_renderable(self):
        self.data['checkpoint']['approval'].update(status='unknown',revision=None,summary='No approval source can be established.')
        out=self.render()
        self.assertIn('No approval source can be established.',out)

    def test_approved_state_still_requires_original_record_response(self):
        self.data['state']='approved'
        with self.assertRaisesRegex(ValueError,'matching recorded approval'): self.render()

    def test_approved_state_must_match_checkpoint(self):
        self.data['state']='approved'
        self.data['approval']={'revision':'P1','record':'fixture','response':'synthetic'}
        self.data['checkpoint']['approval']['revision']='P0'
        with self.assertRaisesRegex(ValueError,'same approved revision'): self.render()

    def test_pending_material_decision_still_blocks_approved_state(self):
        self.data['state']='approved'
        self.data['approval']={'revision':'P1','record':'fixture','response':'synthetic'}
        self.data['open_decisions']=['Unresolved user choice']
        with self.assertRaisesRegex(ValueError,'no blocking decisions'): self.render()

    def test_same_approved_scope_not_represented_as_new_pending_review(self):
        self.data['report_kind']='review'
        with self.assertRaisesRegex(ValueError,'another approval request'): self.render()

    def test_new_proposal_does_not_replace_existing_approval(self):
        self.data['report_kind']='review';self.data['revision']='P2'
        out=self.render()
        self.assertIn('Approved · P1',out)
        self.assertIn('Approve plan P2',out)

    def test_legacy_combined_status_record_can_supply_roles(self):
        for row in self.data['sources']:
            if row['role'] in ('plan','todo','findings'):row['path']='STATUS.md'
        self.assertIn('SAVED TASK OVERVIEW',self.render())

    def test_aliases_preserved_not_renumbered(self):
        self.data['revision_log'][0].update(revision='P1-r1',review='review-r5.html / phase C3')
        out=self.render()
        self.assertIn('review-r5.html / phase C3',out);self.assertIn('P1-r1',out)

    def test_missing_historical_review_can_be_described_not_rebuilt(self):
        self.data['revision_log'][0]['review']='review-r0.html — unavailable, not reconstructed'
        out=self.render()
        self.assertIn('unavailable, not reconstructed',out)
        self.assertFalse((self.root/'review-r0.html').exists())

    def test_duplicate_revision_rows_rejected(self):
        self.data['revision_log'].append(copy.deepcopy(self.data['revision_log'][0]))
        with self.assertRaisesRegex(ValueError,'Duplicate revision_log'):self.render()

    def test_current_approval_not_also_superseded(self):
        self.data['revision_log'][1]['status']='superseded'
        with self.assertRaisesRegex(ValueError,'conflicts'):self.render()

    def test_revision_row_requires_change_reason_and_source(self):
        for key in ('change','reason','source','locator'):
            with self.subTest(key=key):
                old=self.data['revision_log'][0].pop(key)
                with self.assertRaises(ValueError):self.render()
                self.data['revision_log'][0][key]=old

    def test_removed_and_superseded_not_labelled_verified(self):
        for state in ('removed','superseded'):
            with self.subTest(state=state):
                self.data['tasks'][0].update(outcome=state,outcome_note='Explicit synthetic owner decision D3.')
                out=self.render();self.assertIn('not a passed test',out)

    def test_task_outcome_requires_note(self):
        self.data['tasks'][0].pop('outcome_note')
        with self.assertRaisesRegex(ValueError,'outcome_note'):self.render()

    def test_implemented_can_have_blocked_acceptance(self):
        self.data['checkpoint']['implementation'].update(status='implemented',summary='Synthetic recorded claim; not a code audit.')
        self.data['checkpoint']['verification'].update(status='blocked',summary='Phone owner acceptance remains open.')
        out=self.render();self.assertIn('Phone owner acceptance remains open.',out)
        self.assertIn('Implemented',out);self.assertIn('Blocked',out)

    def test_record_text_and_aliases_are_inert(self):
        payload='</script><img src="https://invalid.example/x" onerror="alert(1)">'
        self.data['checkpoint']['next_action']=payload
        self.data['revision_log'][0]['review']=payload
        out=self.render()
        self.assertNotIn('<img ',out);self.assertIn('&lt;img',out)

    def test_duplicate_plan_prefix_not_added(self):
        self.assertEqual(report.plan_label('PLAN revision 3'),'PLAN revision 3')
        self.assertEqual(report.plan_label('P1-r1'),'Plan P1-r1')

    def test_checkpoint_update_changes_fingerprint_not_original_report(self):
        out=self.render();html=self.root/'overview-rendered.html';html.write_text(out)
        self.assertEqual(report.check_report(html,self.root),[])
        with (self.root/'STATUS.md').open('a') as stream:stream.write('\nProgress update, unchanged approval.\n')
        self.assertEqual(report.check_report(html,self.root),['CHANGED: STATUS.md'])
        self.assertEqual(html.read_text(),out)

    def test_current_only_overview_has_no_nonexistent_proposed_view_claim(self):
        self.data.update(mode='current',state='inspection',graphs=[self.data['graphs'][0]],tasks=[],requirements=[],acceptance=[],comparison=[],default_view='current')
        self.assertIn('Current flow as inspected',self.render())

class RecordPolicyContracts(unittest.TestCase):
    """Static regression guard only; live behavior cases remain separate."""
    def test_policy_contains_forward_only_and_authority_boundaries(self):
        text=(ROOT/'skills/workflow/TASK-FOLDER.md').read_text()
        for term in ('Forward-only adoption','legacy `STATUS.md`','No new plan revision','Proposed ADRs are not accepted','Do not bulk rewrite closed tasks','immutable snapshots','phase names separate'):
            self.assertIn(term,text)

    def test_utility_modes_remain_bounded(self):
        text=(ROOT/'skills/task-status/SKILL.md').read_text()
        self.assertIn('do not implement',text)
        self.assertIn('without editing',text)
        text=(ROOT/'skills/resume-task/SKILL.md').read_text()
        self.assertIn('no bulk migration',text)
        self.assertIn('no new plan revision',text.lower())


class LegacyFixtureTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which('git'), 'Git unavailable')
    def test_legacy_record_requires_no_template_migration(self):
        from tools.create_fixture import create_fixture, TASK
        with tempfile.TemporaryDirectory() as tmp:
            repo=create_fixture(Path(tmp)/'legacy','record-legacy')
            task=repo/TASK
            self.assertEqual({p.name for p in task.iterdir()},{'STATUS.md'})
            self.assertIn('Decision D2',(task/'STATUS.md').read_text())

    @unittest.skipUnless(shutil.which('git'), 'Git unavailable')
    def test_history_fixture_has_actual_implemented_code(self):
        from tools.create_fixture import create_fixture, TASK
        import subprocess, sys
        with tempfile.TemporaryDirectory() as tmp:
            repo=create_fixture(Path(tmp)/'history','record-history')
            result=subprocess.run([sys.executable,'-c',
                'from src.web import render_score; render_score(-1,2)'],cwd=repo,capture_output=True,text=True)
            self.assertNotEqual(result.returncode,0)
            self.assertIn('ValueError',result.stderr)
            self.assertNotIn('_legacy_score',(repo/'src/player.py').read_text())
            self.assertIn('Awaiting user approval',(repo/TASK/'review-r2.html').read_text())
            self.assertIn('Approval: R2',(repo/TASK/'PLAN.md').read_text())

    @unittest.skipUnless(shutil.which('git'), 'Git unavailable')
    def test_absent_original_is_not_fabricated(self):
        from tools.create_fixture import create_fixture, TASK
        with tempfile.TemporaryDirectory() as tmp:
            repo=create_fixture(Path(tmp)/'missing','record-missing-review')
            self.assertFalse((repo/TASK/'review-r2.html').exists())
            self.assertIn('unavailable',(repo/TASK/'PLAN.md').read_text())
