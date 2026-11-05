"""Whole-read evidence at the Stop hook boundary, independent of approval consent."""
import json
from pathlib import Path
import tempfile
import unittest

import test_plain_reply_hook as stop


GUIDE = 'D:/workflow-axa/skills/grilling/SKILL.md'


class ReadEvidenceTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.path = Path(tmp.name) / 'session.jsonl'

    def missing(self, tool='Bash', result='guide text', error=False, extra=None, result_id='read-1', **data):
        call = {'type': 'tool_use', 'id': 'read-1', 'name': tool, 'input': data}
        rows = [
            {'type': 'user', 'message': {'content': '/workflow-axa:workflow-clarify add'}},
            {'type': 'assistant', 'message': {'content': [call]}},
        ]
        if result is not None:
            answer = {'type': 'tool_result', 'tool_use_id': result_id, 'content': result,
                      'is_error': error}
            rows.append({'type': 'user', 'message': {'content': [answer]}, **(extra or {})})
        rows.append({'type': 'assistant', 'message': {'content': [
            {'type': 'text', 'text': 'Questions are ready.'}]}})
        self.path.write_text('\n'.join(json.dumps(row) for row in rows), encoding='utf-8')
        code, output = stop.fire({'transcript_path': str(self.path)})
        self.assertEqual(code, 0)
        return 'grilling/SKILL.md' in output

    def test_printed_literal_python_read_counts(self):
        for code in (f"from pathlib import Path; print(Path('{GUIDE}').read_text())",
                     f"print(open('{GUIDE}', encoding='utf-8').read())"):
            with self.subTest(code=code):
                self.assertFalse(self.missing(command=f'python -c "{code}"'))
        self.assertFalse(self.missing(command=f'python -X utf8 -I -c "print(open(\'{GUIDE}\').read())"'))

    def test_powershell_raw_read_counts(self):
        self.assertFalse(self.missing(tool='PowerShell', command=f"Get-Content -Raw -LiteralPath '{GUIDE}'"))

    def test_unrelated_result_cannot_complete_pending_read(self):
        self.assertTrue(self.missing(command=f'cat {GUIDE}', result_id='other-call'))

    def test_successful_shell_result_does_not_prove_conditional_read_ran(self):
        for command in (f'false && cat {GUIDE}; echo ok',
                        f'true || cat {GUIDE}; echo ok',
                        f'cd missing && cat {GUIDE}; echo ok',
                        f'if false; then\ncat {GUIDE}\nfi; echo ok'):
            with self.subTest(command=command):
                self.assertTrue(self.missing(command=command, result='ok',
                                             extra={'toolUseResult': {'stdout': 'ok', 'exitCode': 0}}))

    def test_tool_output_does_not_load_another_phase(self):
        self.assertFalse(self.missing(command=f'cat {GUIDE}',
                                      result='/workflow-axa:workflow-specify is documented here'))
        self.assertFalse(self.missing(command=f'cat {GUIDE}',
                                      result='The guide explains how to handle output truncated by a host.'))

    def test_pending_failed_truncated_or_wrong_result_does_not_count(self):
        for result, error, extra in ((None, False, None), ('access denied', True, None),
                                     ('Warning: output truncated\npart of file', False, None),
                                     ('guide text', False, {'isSidechain': True}),
                                     ('guide text', False, {'toolUseResult': {'stdout': 'guide text', 'exitCode': 1}}),
                                     ('guide text', False, {'toolUseResult': {'stdout': 'guide text', 'stderr': 'access denied'}}),
                                     ('guide text', False, {'toolUseResult': {'file': {'numLines': 4, 'totalLines': 20}}})):
            with self.subTest(result=result, error=error, extra=extra):
                self.assertTrue(self.missing(command=f'cat {GUIDE}', result=result, error=error, extra=extra))

    def test_partial_piped_redirected_or_unprinted_reads_do_not_count(self):
        for command in (f'cat {GUIDE} | grep gate', f'cat {GUIDE} > saved.txt',
                        f'cat other.md # {GUIDE}', f"Get-Content '{GUIDE}' -TotalCount 4",
                        f'cat {GUIDE}.backup',
                        f'python -c "print(open(\'{GUIDE}\').read(40))"',
                        f'python -c "print(open(\'{GUIDE}\').read()[:40])"',
                        f'python -c "open(\'{GUIDE}\').read()"'):
            with self.subTest(command=command):
                self.assertTrue(self.missing(command=command))
        self.assertTrue(self.missing(tool='Read', file_path=GUIDE, offset=40))

    def test_compaction_drops_old_or_pending_read_evidence(self):
        rows = [
            {'type': 'user', 'message': {'content': '/workflow-axa:workflow-clarify add'}},
            {'type': 'assistant', 'message': {'content': [
                {'type': 'tool_use', 'id': 'read-1', 'name': 'Read', 'input': {'file_path': GUIDE}}]}},
            {'type': 'system', 'subtype': 'compact_boundary'},
            {'type': 'user', 'message': {'content': [
                {'type': 'tool_result', 'tool_use_id': 'read-1', 'content': 'guide text'}]}},
            {'type': 'assistant', 'message': {'content': [
                {'type': 'text', 'text': 'Questions are ready.'}]}},
        ]
        self.path.write_text('\n'.join(json.dumps(row) for row in rows), encoding='utf-8')
        self.assertIn('grilling/SKILL.md', stop.fire({'transcript_path': str(self.path)})[1])
