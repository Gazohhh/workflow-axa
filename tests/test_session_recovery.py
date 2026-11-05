"""Regression journeys from the November 5 approval and waiting incidents."""
import json
import subprocess
import sys
import unittest

import test_phase_gate_hook as gate
import test_plain_reply_hook as stop


class SessionRecoveryTests(unittest.TestCase):
    setUp = gate.ApprovalGateTests.setUp
    task = gate.ApprovalGateTests.task
    records = gate.ApprovalGateTests.records
    present = gate.ApprovalGateTests.present
    approval = gate.ApprovalGateTests.approval
    session = gate.ApprovalGateTests.session
    fire = gate.ApprovalGateTests.fire
    decision = gate.ApprovalGateTests.decision

    def test_requirement_ids_do_not_revoke_report_approval(self):
        for requirements in ('R7', 'R6', 'D4-R6', 'D4/R6', 'T8 supports R17'):
            with self.subTest(requirements=requirements):
                self.task(gate.TASK, gate.APPROVED, '- Requirements: ' + requirements)
                self.assertIsNone(self.decision([gate.ROUTER] + self.approval('Yes to both'),
                                               'Edit', {'file_path': self.code}))

    def test_real_newer_revision_still_revokes_approval(self):
        for revision in ('revision R2', 'revision 2', 'r2', 'reviews/plan-r2.html'):
            with self.subTest(revision=revision):
                self.task(gate.TASK, gate.APPROVED, '- Status: ' + revision + ' drafted')
                self.assertEqual(self.decision([gate.ROUTER] + self.approval('Yes to both'),
                                              'Edit', {'file_path': self.code}), 'deny')

    def test_old_registration_gives_restart_guidance_not_another_approval_loop(self):
        self.task(gate.TASK, gate.APPROVED)
        out = self.fire([gate.ROUTER] + self.approval('Yes to both'), 'Edit',
                        {'file_path': self.code}, hooks=False)
        self.assertEqual(out['permissionDecision'], 'deny')
        self.assertIn('restart', out['permissionDecisionReason'].lower())
        self.assertIn('registration', out['permissionDecisionReason'].lower())
        self.assertNotIn('ask whether it still holds', out['permissionDecisionReason'])

    def test_unknown_registration_protocol_blocks_code_but_not_records(self):
        self.task(gate.TASK, gate.APPROVED)
        self.session(self.path, [gate.ROUTER] + self.approval('Yes to both'))
        for path, denied in ((self.code, True),
                             (str(self.repo / 'docs/plans' / gate.TASK / 'FINDINGS.md'), False)):
            event = {'hook_event_name': 'PreToolUse', 'tool_name': 'Edit',
                     'tool_input': {'file_path': path}, 'cwd': str(self.repo),
                     'transcript_path': str(self.path)}
            result = subprocess.run([sys.executable, '-I', str(gate.HOOK), '--hook-protocol=999'],
                                    input=json.dumps(event), capture_output=True, text=True)
            self.assertEqual(result.returncode, 0)
            self.assertEqual(bool(result.stdout.strip()), denied)
            if denied:
                self.assertIn('protocol', result.stdout)

    def test_old_registration_without_protocol_requires_restart_even_with_copied_evidence(self):
        self.task(gate.TASK, gate.APPROVED)
        self.session(self.path, [gate.ROUTER] + self.approval('Yes to both'))
        event = {'hook_event_name': 'PreToolUse', 'tool_name': 'Edit', 'tool_input': {'file_path': self.code},
                 'cwd': str(self.repo), 'transcript_path': str(self.path)}
        result = subprocess.run([sys.executable, '-I', str(gate.HOOK)], input=json.dumps(event),
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0)
        self.assertIn('Restart', result.stdout)
        self.assertIn('deny', result.stdout)
        # A fresh host with the current registration and matching approval evidence succeeds.
        self.assertIsNone(gate.run_hook(event))

    def test_registration_pairs_all_fingerprint_events_with_the_same_protocol(self):
        hooks = json.loads((gate.ROOT / 'hooks/hooks.json').read_text())['hooks']
        for event in ('PreToolUse', 'PostToolUse', 'UserPromptSubmit'):
            commands = [h['command'] for group in hooks[event] for h in group['hooks']
                        if 'phase_gate.py' in h.get('command', '')]
            self.assertTrue(commands)
            self.assertTrue(all('--hook-protocol=1' in c for c in commands))

    def test_approval_wait_emits_no_stop_feedback_even_with_unread_guides(self):
        self.task(gate.TASK, '- Approval: not approved; report reviews/plan-r1.html')
        rows = [gate.ROUTER, self.records(), gate.skill('workflow-axa:workflow-specify'),
                self.present()]
        self.session(self.path, rows)
        event = {'hook_event_name': 'Stop', 'cwd': str(self.repo),
                 'transcript_path': str(self.path),
                 'last_assistant_message': 'Waiting on you: approve plan-r1.html or request changes.'}
        # No timer/retry/state mutation: repeated host Stop events stay silent.
        for _ in range(3):
            self.assertEqual(stop.fire(event), (0, ''))
        self.assertEqual(self.decision(rows, 'Edit', {'file_path': self.code}), 'deny')

    def test_copied_worktree_records_do_not_inherit_approval(self):
        self.task(gate.TASK, gate.APPROVED)
        other = self.base / 'other-tree'
        (self.repo / '.git/worktrees/other').mkdir(parents=True)
        other.mkdir()
        (other / '.git').write_text(f"gitdir: {self.repo / '.git/worktrees/other'}\n")
        self.task(gate.TASK, gate.APPROVED, root=other)
        rows = [gate.ROUTER] + self.approval('Yes to both')
        target = {'file_path': str(other / 'src/a.ts')}
        self.assertEqual(self.decision(rows, 'Edit', target), 'deny')
        # Explicitly present and approve the target workspace's report instead.
        rows += [gate.say(f"Approve {other / 'docs/plans' / gate.TASK / 'reviews/plan-r1.html'}?"),
                 gate.user('Yes to both')]
        self.assertIsNone(self.decision(rows, 'Edit', target))

    def test_reply_fingerprint_uses_the_explicitly_presented_worktree(self):
        self.task(gate.TASK, gate.APPROVED)
        other = self.base / 'OtherWorkspace'
        (self.repo / '.git/worktrees/other').mkdir(parents=True)
        other.mkdir()
        (other / '.git').write_text(f"gitdir: {self.repo / '.git/worktrees/other'}\n")
        folder = self.task(gate.TASK, gate.APPROVED, root=other)
        report = folder / 'reviews/plan-r1.html'
        report.write_text('<!DOCTYPE html><p>Target worktree scope</p>')
        rows = [gate.ROUTER, self.records(), gate.say(f'Approve {report.as_posix()}?')]
        self.session(self.path, rows)
        out = gate.run_hook({'hook_event_name': 'UserPromptSubmit', 'prompt': 'Yes to both',
                             'transcript_path': str(self.path), 'cwd': str(self.repo)})
        self.assertIn(gate.sha(report), out['additionalContext'])

    def test_markdown_local_file_uri_preserves_presentation_workspace(self):
        # Path.as_uri supplies file:///C:/... on Windows and file:///... on POSIX.
        for spaced in (False, True):
            with self.subTest(spaced=spaced):
                root = self.repo / 'with spaces' if spaced else self.repo
                if spaced:
                    (root / '.git').mkdir(parents=True)
                report = self.task(gate.TASK, gate.APPROVED, root=root) / 'reviews/plan-r1.html'
                rel = f'docs/plans/{gate.TASK}/reviews/plan-r1.html'
                before = gate.hook_context('PostToolUse',
                    f'workflow-axa report fingerprint: {rel} sha256={gate.sha(report)}')
                for label in (str(report), 'Review this plan'):
                    rows = [gate.ROUTER, self.records(root=root), before,
                            gate.say(f'Approve [{label}]({report.as_uri()})?')]
                    self.session(self.path, rows, hooks=False)
                    reply = gate.run_hook({'hook_event_name': 'UserPromptSubmit', 'prompt': 'Yes to both',
                                          'transcript_path': str(self.path), 'cwd': str(root)})
                    self.assertIsNotNone(reply)
                    self.assertIn(gate.sha(report), reply['additionalContext'])
                    rows += [gate.user('Yes to both'),
                             gate.hook_context('UserPromptSubmit', reply['additionalContext'])]
                    self.assertIsNone(self.decision(rows, 'Edit', {'file_path': str(root / 'src/a.ts')},
                                                   cwd=str(root), hooks=False))

    def test_remote_uri_cannot_become_local_report_presentation(self):
        report = self.task(gate.TASK, gate.APPROVED) / 'reviews/plan-r1.html'
        rel = f'docs/plans/{gate.TASK}/reviews/plan-r1.html'
        for target in (f'https://example.invalid/{rel}', f'unknown://host/{rel}',
                       f'https://example.invalid/[label]{rel}',
                       f'file://remote-host/{rel}', f'file:{rel}'):
            for link in (target, f'[{report}]({target})'):
                with self.subTest(link=link):
                    rows = [gate.ROUTER, self.records(), gate.hook_context('PostToolUse',
                        f'workflow-axa report fingerprint: {rel} sha256={gate.sha(report)}'),
                        gate.say(f'Approve {link}?'), gate.user('Yes to both'),
                        gate.hook_context('UserPromptSubmit',
                        f'workflow-axa report at owner reply: {rel} sha256={gate.sha(report)}')]
                    self.assertEqual(self.decision(rows, 'Edit', {'file_path': self.code}, hooks=False), 'deny')

    def test_file_uri_target_cannot_borrow_the_link_labels_workspace(self):
        report = self.task(gate.TASK, gate.APPROVED) / 'reviews/plan-r1.html'
        other = self.base / 'other workspace'
        (self.repo / '.git/worktrees/other').mkdir(parents=True)
        other.mkdir()
        (other / '.git').write_text(f"gitdir: {self.repo / '.git/worktrees/other'}\n")
        other_report = self.task(gate.TASK, gate.APPROVED, root=other) / 'reviews/plan-r1.html'
        rel = f'docs/plans/{gate.TASK}/reviews/plan-r1.html'
        rows = [gate.ROUTER, self.records(), gate.hook_context('PostToolUse',
                f'workflow-axa report fingerprint: {rel} sha256={gate.sha(report)}'),
                gate.say(f'Approve [{report}]({other_report.as_uri()})?'), gate.user('Yes to both'),
                gate.hook_context('UserPromptSubmit',
                f'workflow-axa report at owner reply: {rel} sha256={gate.sha(other_report)}')]
        self.assertEqual(self.decision(rows, 'Edit', {'file_path': self.code}, hooks=False), 'deny')
        self.assertIsNone(self.decision(rows, 'Edit', {'file_path': str(other / 'src/a.ts')}, hooks=False))

    def test_nested_or_reference_link_labels_cannot_present_a_local_report(self):
        report = self.task(gate.TASK, gate.APPROVED) / 'reviews/plan-r1.html'
        other = self.base / 'sibling'
        other_report = self.task(gate.TASK, gate.APPROVED, root=other) / 'reviews/plan-r1.html'
        rel = f'docs/plans/{gate.TASK}/reviews/plan-r1.html'
        for link in (f'[review [{report.as_posix()}]](https://example.invalid/)',
                     f'[review [deeper [{report.as_posix()}]]](https://example.invalid/)',
                     f'[review \\] {report.as_posix()}](https://example.invalid/)',
                     f'[review [{report.as_posix()}]]({other_report.as_uri()})',
                     f'[{report.as_posix()}][remote]\n[remote]: https://example.invalid/',
                     f'[{report.as_posix()}]\n[{report.as_posix()}]: https://example.invalid/',
                     f'[remote]\n[remote]: {report.as_uri()}'):
            with self.subTest(link=link):
                rows = [gate.ROUTER, self.records(), gate.hook_context('PostToolUse',
                        f'workflow-axa report fingerprint: {rel} sha256={gate.sha(report)}'),
                        gate.say(f'Approve {link}?'), gate.user('Yes to both'),
                        gate.hook_context('UserPromptSubmit',
                        f'workflow-axa report at owner reply: {rel} sha256={gate.sha(report)}')]
                self.assertEqual(self.decision(rows, 'Edit', {'file_path': self.code}, hooks=False), 'deny')

    def test_inline_link_titles_and_malformed_suffixes_are_not_report_destinations(self):
        report = self.task(gate.TASK, gate.APPROVED) / 'reviews/plan-r1.html'
        rel = f'docs/plans/{gate.TASK}/reviews/plan-r1.html'
        for destination in (f'unrelated.txt "{report.as_posix()}"',
                            f"unrelated.txt '{report.as_posix()}'",
                            f'unrelated.txt ({report.as_posix()})',
                            f'<unrelated.txt> "{report.as_posix()}"',
                            f'<unrelated.txt> ({report.as_posix()})',
                            f'unrelated.txt "title) {report.as_posix()}"',
                            f'unrelated.txt "unclosed {report.as_posix()}',
                            f'unrelated.txt (unclosed {report.as_posix()}',
                            f'<unrelated {report.as_posix()}>',
                            f'unrelated{report.as_posix()}',
                            f'<unrelated.txt "{report.as_posix()}">'):
            with self.subTest(destination=destination):
                rows = [gate.ROUTER, self.records(), gate.hook_context('PostToolUse',
                        f'workflow-axa report fingerprint: {rel} sha256={gate.sha(report)}'),
                        gate.say(f'Approve [review]({destination})?'), gate.user('Yes to both'),
                        gate.hook_context('UserPromptSubmit',
                        f'workflow-axa report at owner reply: {rel} sha256={gate.sha(report)}')]
                self.assertEqual(self.decision(rows, 'Edit', {'file_path': self.code}, hooks=False), 'deny')

    def test_local_inline_destination_with_optional_title_still_approves(self):
        report = self.task(gate.TASK, gate.APPROVED) / 'reviews/plan-r1.html'
        rel = f'docs/plans/{gate.TASK}/reviews/plan-r1.html'
        for destination in (f'{report.as_uri()} "Plan review"', f"{report.as_uri()} 'Plan review'",
                            f'{report.as_uri()} (Plan review)', f'<{report.as_uri()}> "Plan review"',
                            f'{report.as_uri()}#review "Plan review"', f'<{report.as_posix()}#review>'):
            with self.subTest(destination=destination):
                rows = [gate.ROUTER, self.records(), gate.hook_context('PostToolUse',
                        f'workflow-axa report fingerprint: {rel} sha256={gate.sha(report)}'),
                        gate.say(f'Approve [review]({destination})?'), gate.user('Yes to both'),
                        gate.hook_context('UserPromptSubmit',
                        f'workflow-axa report at owner reply: {rel} sha256={gate.sha(report)}')]
                self.assertIsNone(self.decision(rows, 'Edit', {'file_path': self.code}, hooks=False))

    def test_report_destination_suffix_cannot_name_a_different_file(self):
        report = self.task(gate.TASK, gate.APPROVED) / 'reviews/plan-r1.html'
        rel = f'docs/plans/{gate.TASK}/reviews/plan-r1.html'
        for suffix in ('.backup', '.bak', '/other', '%2ebackup'):
            for link in (f'[review]({report.as_uri()}{suffix})',
                         f'[review](<{report.as_posix()}{suffix}>)', f'{report.as_posix()}{suffix}'):
                with self.subTest(link=link):
                    rows = [gate.ROUTER, self.records(), gate.hook_context('PostToolUse',
                            f'workflow-axa report fingerprint: {rel} sha256={gate.sha(report)}'),
                            gate.say(f'Approve {link}?'), gate.user('Yes to both'),
                            gate.hook_context('UserPromptSubmit',
                            f'workflow-axa report at owner reply: {rel} sha256={gate.sha(report)}')]
                    self.assertEqual(self.decision(rows, 'Edit', {'file_path': self.code}, hooks=False), 'deny')

    def test_destination_brackets_preserve_the_actual_workspace_identity(self):
        reports = []
        for index, name in enumerate(('repo[other]', 'repo[]')):
            root = self.base / name
            (self.repo / f'.git/worktrees/bracket{index}').mkdir(parents=True)
            root.mkdir()
            (root / '.git').write_text(f"gitdir: {self.repo / f'.git/worktrees/bracket{index}'}\n")
            reports.append(self.task(gate.TASK, gate.APPROVED, root=root) / 'reviews/plan-r1.html')
        report, wrong_report = reports
        rel = f'docs/plans/{gate.TASK}/reviews/plan-r1.html'
        uri = report.as_uri().replace('%5B', '[').replace('%5D', ']')
        for link in (f'[review](<{report.as_posix()}>)', f'[review]({uri})', uri,
                     report.as_posix(), f'[review]({report.as_uri()})'):
            with self.subTest(link=link):
                rows = [gate.ROUTER, self.records(root=report.parents[4]), gate.hook_context('PostToolUse',
                        f'workflow-axa report fingerprint: {rel} sha256={gate.sha(report)}'),
                        gate.say(f'Approve {link}?'), gate.user('Yes to both'),
                        gate.hook_context('UserPromptSubmit',
                        f'workflow-axa report at owner reply: {rel} sha256={gate.sha(report)}')]
                self.assertEqual(self.decision(rows, 'Edit', {'file_path': str(wrong_report.parents[4] / 'src/a.ts')},
                                               hooks=False), 'deny')
                self.assertIsNone(self.decision(rows, 'Edit', {'file_path': str(report.parents[4] / 'src/a.ts')},
                                               hooks=False))

    def test_no_report_waiver_cannot_move_to_a_later_workspace_presentation(self):
        answer = 'Approved r1, no report'
        approval = f'- Approval: revision r1 approved, no report: "{answer}"'
        self.task(gate.TASK, approval, report=None)
        other = self.base / 'other-tree'
        (self.repo / '.git/worktrees/other').mkdir(parents=True)
        other.mkdir()
        (other / '.git').write_text(f"gitdir: {self.repo / '.git/worktrees/other'}\n")
        self.task(gate.TASK, approval, root=other, report=None)
        first = gate.say(f'Plan revision r1 for docs/plans/{gate.TASK}/: change src/a.ts, no report?')
        first['cwd'] = str(self.repo)
        second = json.loads(json.dumps(first))
        second['cwd'] = str(other)
        rows = [gate.ROUTER, self.records(), first, gate.user(answer), second]
        target = {'file_path': str(other / 'src/a.ts')}
        self.assertEqual(self.decision(rows, 'Edit', target), 'deny')
        self.assertIsNone(self.decision(rows + [gate.user(answer)], 'Edit', target))

    def test_sidechain_report_text_cannot_present_the_owners_plan(self):
        self.task(gate.TASK, gate.APPROVED)
        shown = self.present()
        shown['isSidechain'] = True
        self.assertEqual(self.decision([gate.ROUTER, self.records(), shown, gate.user('Yes to both')],
                                      'Edit', {'file_path': self.code}), 'deny')

    def test_completed_report_question_is_presentation_but_thinking_is_not(self):
        folder = self.task(gate.TASK, gate.APPROVED)
        report = folder / 'reviews/plan-r1.html'
        rel = f'docs/plans/{gate.TASK}/reviews/plan-r1.html'
        question = f'Approve {report.as_posix()}?'
        ask = gate.tool('AskUserQuestion', questions=[{'question': question,
                        'options': [{'label': 'Yes to both'}, {'label': 'Request changes'}]}])
        ask['message']['content'][0]['id'] = 'approval-question'
        answer = {'type': 'user', 'message': {'role': 'user', 'content': [
            {'type': 'tool_result', 'tool_use_id': 'approval-question', 'content': 'answered'}]},
            'toolUseResult': {'answers': {question: 'Yes to both'}}}
        before = [gate.ROUTER, self.records(), gate.hook_context('PostToolUse',
                  f'workflow-axa report fingerprint: {rel} sha256={gate.sha(report)}'), ask]
        after = gate.hook_context('PostToolUse',
                                 f'workflow-axa report at owner reply: {rel} sha256={gate.sha(report)}')
        self.assertIsNone(self.decision(before + [answer, after], 'Edit', {'file_path': self.code}, hooks=False))
        # No matched completed result means no presentation or consent from the question.
        self.assertEqual(self.decision(before + [gate.user('Yes to both'), after], 'Edit',
                                      {'file_path': self.code}, hooks=False), 'deny')
        for change in ('sidechain', 'failed', 'wrong-id', 'wrong-question'):
            altered = json.loads(json.dumps(answer))
            if change == 'sidechain':
                altered['isSidechain'] = True
            elif change == 'failed':
                altered['message']['content'][0]['is_error'] = True
            elif change == 'wrong-id':
                altered['message']['content'][0]['tool_use_id'] = 'unrelated'
            else:
                altered['toolUseResult']['answers'] = {'Other question': 'Yes to both'}
            with self.subTest(change=change):
                self.assertEqual(self.decision(before + [altered, after], 'Edit',
                                              {'file_path': self.code}, hooks=False), 'deny')
        thinking = {'type': 'assistant', 'message': {'content': [
            {'type': 'thinking', 'thinking': question}]}}
        self.assertEqual(self.decision(before[:-1] + [thinking, gate.user('Yes to both'), after],
                                      'Edit', {'file_path': self.code}, hooks=False), 'deny')

    def test_explicit_withdrawal_blocks_old_consent_until_a_new_real_approval(self):
        self.task(gate.TASK, gate.APPROVED)
        rows = [gate.ROUTER] + self.approval('Yes to both') + [gate.user('I withdraw this approval')]
        self.assertEqual(self.decision(rows, 'Edit', {'file_path': self.code}), 'deny')
        self.assertIsNone(self.decision(rows + [self.present(), gate.user('Yes to both')],
                                       'Edit', {'file_path': self.code}))
        self.session(self.sessions / 'earlier.jsonl', [gate.ROUTER] + self.approval('Yes to both'))
        current = [gate.ROUTER, gate.user(f'continue docs/plans/{gate.TASK}'),
                   gate.user('I withdraw this approval')]
        self.assertEqual(self.decision(current, 'Edit', {'file_path': self.code}), 'deny')

    def test_withdrawal_of_another_task_does_not_cancel_this_approval(self):
        self.task(gate.TASK, gate.APPROVED)
        other = '2026-11-05-other'
        self.task(other, gate.APPROVED)
        rows = [gate.ROUTER] + self.approval('Yes to both') + [
            self.records(other), gate.user(f'For docs/plans/{other}, I withdraw this approval'),
            gate.user(f'continue docs/plans/{gate.TASK}')]
        self.assertIsNone(self.decision(rows, 'Edit', {'file_path': self.code}))
        self.session(self.sessions / 'earlier.jsonl', [gate.ROUTER] + self.approval('Yes to both'))
        current = [gate.ROUTER, self.records(other),
                   gate.user(f'For docs/plans/{other}, I withdraw this approval'),
                   gate.user(f'continue docs/plans/{gate.TASK}')]
        self.assertIsNone(self.decision(current, 'Edit', {'file_path': self.code}))
