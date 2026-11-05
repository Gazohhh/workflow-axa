"""Regressions reproduced while reviewing the supplied post-hardening candidate."""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch

import test_phase_gate_hook as fixtures

ROOT = Path(__file__).resolve().parents[1]


def load_file(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


class FollowupApprovalTests(unittest.TestCase):
    def setUp(self):
        self.h = fixtures.ApprovalGateTests()
        self.h.setUp()
        self.addCleanup(self.h.doCleanups)

    def test_loading_specify_is_not_presenting_the_plan(self):
        self.h.task(fixtures.TASK, fixtures.APPROVED)
        rows = [fixtures.ROUTER, self.h.records(), fixtures.skill('workflow-specify'),
                fixtures.user('Yes to both')]
        self.assertEqual(self.h.decision(rows, 'Edit', {'file_path': self.h.code}), 'deny')

    def test_writing_a_report_is_not_presenting_it(self):
        self.h.task(fixtures.TASK, fixtures.APPROVED)
        report = self.h.repo / 'docs/plans' / fixtures.TASK / 'reviews/plan-r1.html'
        rows = [fixtures.ROUTER, self.h.records(), fixtures.tool('Write', file_path=str(report), content='report'),
                fixtures.user('Yes to both')]
        self.assertEqual(self.h.decision(rows, 'Edit', {'file_path': self.h.code}), 'deny')

    def test_quote_must_keep_the_users_conditions(self):
        self.h.task(fixtures.TASK, fixtures.APPROVED)
        rows = [fixtures.ROUTER] + self.h.approval('Yes to both, but do not implement until I confirm.')
        self.assertEqual(self.h.decision(rows, 'Edit', {'file_path': self.h.code}), 'deny')

    def test_unquoted_no_report_is_not_a_user_waiver(self):
        self.h.task(fixtures.TASK, '- Approval: revision r1 approved: "Yes to both"; no report.', report=None)
        rows = [fixtures.ROUTER] + self.h.approval('Yes to both')
        self.assertEqual(self.h.decision(rows, 'Edit', {'file_path': self.h.code}), 'deny')

    def test_stop_blocks_code_but_keeps_handoff_records_available(self):
        rows = self.h.approved_rows() + [fixtures.user('Stop.')]
        self.assertEqual(self.h.decision(rows, 'Edit', {'file_path': self.h.code}), 'deny')
        record = self.h.repo / 'docs/plans' / fixtures.TASK / 'FINDINGS.md'
        self.assertIsNone(self.h.decision(rows, 'Write', {'file_path': str(record)}))

    def test_resume_reuses_unchanged_approval_without_reapproving(self):
        rows = self.h.approved_rows() + [fixtures.user('Pause this task.'), fixtures.user('Continue this task.')]
        self.assertIsNone(self.h.decision(rows, 'Edit', {'file_path': self.h.code}))

    def test_a_stop_mentioned_as_feature_behavior_is_not_a_stop_request(self):
        rows = self.h.approved_rows() + [fixtures.user('The Stop button should stop playback.')]
        self.assertIsNone(self.h.decision(rows, 'Edit', {'file_path': self.h.code}))

    def test_short_whole_answer_is_valid_after_an_actual_plan_question(self):
        self.h.task(fixtures.TASK, '- Approval: revision r1 approved: "Approve" (report reviews/plan-r1.html).')
        rows = [fixtures.ROUTER] + self.h.approval('Approve')
        self.assertIsNone(self.h.decision(rows, 'Edit', {'file_path': self.h.code}))

    def test_a_new_report_cannot_borrow_the_previous_report_consent(self):
        self.h.task(fixtures.TASK, '- Approval: revision r2 approved: "Yes to both" (report reviews/plan-r2.html).',
                    report='plan-r2.html')
        rows = [fixtures.ROUTER] + self.h.approval('Yes to both') + [
            fixtures.say(f'Updated plan: docs/plans/{fixtures.TASK}/reviews/plan-r2.html. Approve?')]
        self.assertEqual(self.h.decision(rows, 'Edit', {'file_path': self.h.code}), 'deny')

    def test_exact_presentation_and_whole_answer_keep_the_normal_route(self):
        rows = self.h.approved_rows()
        self.assertIsNone(self.h.decision(rows, 'Edit', {'file_path': self.h.code}))

    def test_a_later_status_link_does_not_cancel_the_same_report_approval(self):
        rows = self.h.approved_rows() + [self.h.present()]
        self.assertIsNone(self.h.decision(rows, 'Edit', {'file_path': self.h.code}))

    def test_full_approval_with_nonimplementation_restriction_still_allows_code(self):
        answer = 'Approve this plan. Do not commit or push.'
        self.h.task(fixtures.TASK, f'- Approval: revision r1 approved: "{answer}" (report reviews/plan-r1.html).')
        rows = [fixtures.ROUTER] + self.h.approval(answer)
        self.assertIsNone(self.h.decision(rows, 'Edit', {'file_path': self.h.code}))

    def test_a_whole_answer_which_holds_implementation_still_blocks(self):
        answer = 'Yes to both, but do not implement until I confirm.'
        self.h.task(fixtures.TASK, f'- Approval: revision r1 approved: "{answer}" (report reviews/plan-r1.html).')
        rows = [fixtures.ROUTER] + self.h.approval(answer)
        self.assertEqual(self.h.decision(rows, 'Edit', {'file_path': self.h.code}), 'deny')

    def test_textual_plan_waiver_cannot_borrow_another_revision(self):
        answer = 'Approve without the HTML report.'
        self.h.task(fixtures.TASK, f'- Approval: revision r2 approved: "{answer}"', report=None)
        rows = [fixtures.ROUTER, self.h.records(),
                fixtures.say(f'Plan revision r1 for docs/plans/{fixtures.TASK}/: fix a.ts. Approve?'),
                fixtures.user(answer)]
        self.assertEqual(self.h.decision(rows, 'Edit', {'file_path': self.h.code}), 'deny')


class FollowupBaselineTests(unittest.TestCase):
    def setUp(self):
        self.mod = load_file(ROOT / 'skills/workflow/scripts/baseline_state.py', 'baseline_followup')
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.top = Path(self.tmp.name)
        self.record = self.top / 'baseline.json'

    def fake_git(self, top, *args):
        if args == ('rev-parse', '--show-toplevel'):
            return str(self.top).encode()
        if args == ('rev-parse', 'HEAD'):
            return b'abc123'
        return b''

    def test_command_whitespace_inside_quotes_is_significant(self):
        with patch.object(self.mod, 'git', side_effect=self.fake_git), patch.object(self.mod, 'tool_version', return_value='1'):
            a = self.mod.state('python -c "print(\'a  b\')"', self.record)
            b = self.mod.state('python -c "print(\'a b\')"', self.record)
        self.assertNotEqual(a['command'], b['command'])

    def test_running_directory_is_part_of_the_baseline_signature(self):
        with patch.object(self.mod, 'git', side_effect=self.fake_git), patch.object(self.mod, 'tool_version', return_value='1'):
            with patch.object(Path, 'cwd', return_value=self.top / 'one'):
                a = self.mod.state('npm test', self.record)
            with patch.object(Path, 'cwd', return_value=self.top / 'two'):
                b = self.mod.state('npm test', self.record)
        self.assertNotEqual(a, b)

    def test_nonobject_baseline_is_a_clear_refusal_not_a_traceback(self):
        self.record.write_text('[]', encoding='utf-8')
        with patch.object(self.mod, 'state', return_value={'command': 'test'}):
            self.assertEqual(self.mod.main(['baseline', 'check', 'test', str(self.record)]), 2)

    def test_unknown_environment_cannot_be_reported_as_verified_reuse(self):
        state = {'command': 'test', 'environment': '{"node": "unknown"}', 'commit': 'abc', 'diff': 'abc'}
        self.record.write_text(json.dumps(state), encoding='utf-8')
        with patch.object(self.mod, 'state', return_value=state):
            self.assertNotEqual(self.mod.main(['baseline', 'check', 'test', str(self.record)]), 0)

class ConditionalGuidanceTests(unittest.TestCase):
    def setUp(self):
        self.mod = load_file(ROOT / 'hooks/plain_reply.py', 'plain_followup')
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / 'session.jsonl'

    def missing(self, rows):
        self.path.write_text('\n'.join(json.dumps(r) for r in rows), encoding='utf-8')
        return self.mod.unread_files(self.path)

    def test_not_needed_screen_metadata_does_not_force_ui_guidance(self):
        rows = [fixtures.skill('workflow-specify'), fixtures.tool('Write', file_path='docs/plans/x/report.json',
                content=json.dumps({'screen_change': 'not-needed'}))]
        missing = self.missing(rows)['workflow-specify']
        self.assertIn('codebase-map/TASK-REPORT.md', missing)
        self.assertFalse(any('ui-design/' in name or 'UI-FLOW' in name or name.endswith('/design.md') for name in missing))

    def test_visible_ui_still_requires_its_guidance(self):
        rows = [fixtures.skill('workflow-specify'), fixtures.tool('Write', file_path='docs/plans/x/report.json',
                content=json.dumps({'screen_change': 'visible'}))]
        missing = self.missing(rows)['workflow-specify']
        self.assertIn('ui-design/SKILL.md', missing)
        self.assertIn('codebase-map/UI-FLOW.md', missing)

    def test_documentation_ticket_does_not_force_tdd_or_code_review_skill_reads(self):
        missing = self.missing([fixtures.skill('workflow-execute'),
                               fixtures.tool('Edit', file_path='docs/README.md')])['workflow-execute']
        self.assertNotIn('tdd/SKILL.md', missing)
        self.assertNotIn('code-review/SKILL.md', missing)
        self.assertIn('workflow/AUDIT.md', missing)

    def test_code_change_and_planned_tdd_require_their_specialist_guidance(self):
        missing = self.missing([fixtures.skill('workflow-execute'), fixtures.tool('Edit', file_path='src/a.ts'),
                               fixtures.tool('Write', file_path='docs/plans/x/TODO.md', content='TDD: yes')])['workflow-execute']
        self.assertIn('tdd/SKILL.md', missing)
        self.assertIn('code-review/SKILL.md', missing)

    def test_stop_does_not_prompt_another_phase_read_or_review(self):
        import test_plain_reply_hook
        rows = [fixtures.ROUTER, fixtures.skill('workflow-execute'), fixtures.user('Stop.'),
                fixtures.say('Stopped; the work is incomplete.')]
        self.missing(rows)
        self.assertEqual(test_plain_reply_hook.fire({'transcript_path': str(self.path)}), (0, ''))


if __name__ == '__main__':
    unittest.main()
