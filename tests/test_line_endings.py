"""Install-copy line endings and home resolution: behaviour checks with a negative mutation case each."""
from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import io
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]


def load(name, relative):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module  # dataclasses resolve annotations through sys.modules
    spec.loader.exec_module(module)
    return module


audit = load('audit_under_test', 'skills/rule-maker/scripts/audit_installation.py')
activation = load('activate_under_test', 'skills/rule-maker/scripts/activate_rules.py')
policy = load('policy_under_test', 'skills/workflow/scripts/global_policy.py')
manifest_tool = load('manifest_tool_under_test', 'tools/update_rules_manifest.py')

CRLF, LF = bytes([13, 10]), bytes([10])


def to_crlf(path: Path) -> None:
    path.write_bytes(path.read_bytes().replace(CRLF, LF).replace(LF, CRLF))


class InstalledCopyTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.skills = Path(self.tmp.name) / 'skills'
        shutil.copytree(ROOT / 'skills', self.skills, ignore=shutil.ignore_patterns('__pycache__'))
        self.rules = self.skills / 'rule-maker/rules'

    def test_audit_names_line_ending_only_files_and_stays_drift(self):
        for path in self.rules.glob('*.md'):
            to_crlf(path)
        row = audit.inspect([self.skills])['candidates'][0]
        self.assertEqual(row['state'], 'DRIFT')
        self.assertTrue(row['line_ending_only'])
        self.assertEqual(sorted(row['line_ending_only']), sorted(row['changed']))

    def test_audit_does_not_excuse_a_real_edit_hidden_in_a_crlf_copy(self):
        core = self.rules / 'CORE.md'
        core.write_bytes(core.read_bytes().replace(b'Core standards', b'Core standardz', 1))
        to_crlf(core)
        row = audit.inspect([self.skills])['candidates'][0]
        self.assertIn('rule-maker/rules/CORE.md', row['changed'])
        self.assertNotIn('rule-maker/rules/CORE.md', row['line_ending_only'])

    def test_activation_refuses_crlf_copy_with_file_scoped_reason(self):
        to_crlf(self.rules / 'CORE.md')
        with self.assertRaisesRegex(ValueError, 'only by CRLF line endings: .*CORE.md'):
            activation.validate_library(self.rules)

    def test_activation_reports_real_edit_as_modified(self):
        core = self.rules / 'CORE.md'
        core.write_bytes(core.read_bytes() + b'extra\n')
        to_crlf(core)
        with self.assertRaises(ValueError) as caught:
            activation.validate_library(self.rules)
        self.assertIn('Mixed/modified', str(caught.exception))
        self.assertNotIn('only by CRLF', str(caught.exception))

    def readiness(self) -> dict:
        project = Path(self.tmp.name) / 'project'
        project.mkdir(exist_ok=True)
        (project / 'AGENTS.md').write_text('# Rules\n', encoding='utf-8')
        script = self.skills / 'rule-maker/scripts/readiness.py'
        env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1')
        out = subprocess.run([sys.executable, '-B', str(script), 'inspect', '--root', str(project), '--scope', '.',
                              '--task', 'T1', '--host', 'test', '--mode', 'read-only'],
                             capture_output=True, text=True, env=env, timeout=60)
        return json.loads(out.stdout)

    def test_readiness_blocks_crlf_copy_with_file_scoped_reason(self):
        to_crlf(self.rules / 'CORE.md')
        result = self.readiness()
        self.assertEqual(result['state'], 'BLOCKED')
        self.assertIn('only by CRLF line endings: CORE.md', ' '.join(result['reasons']))

    def test_readiness_blocks_real_edit_as_modified(self):
        core = self.rules / 'CORE.md'
        core.write_bytes(core.read_bytes() + b'extra\n')
        result = self.readiness()
        self.assertEqual(result['state'], 'BLOCKED')
        self.assertIn('Mixed/modified', ' '.join(result['reasons']))
        self.assertNotIn('only by CRLF', ' '.join(result['reasons']))


class ManifestWriterTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        shutil.copytree(ROOT / 'skills/rule-maker/rules', self.root / 'skills/rule-maker/rules')
        self.manifest = self.root / 'skills/rule-maker/rules/version.json'
        patcher = mock.patch.object(manifest_tool, 'ROOT', self.root)
        patcher.start()
        self.addCleanup(patcher.stop)

    def run_tool(self, *args):
        with contextlib.redirect_stdout(io.StringIO()):
            return manifest_tool.main(list(args))

    def test_apply_writes_lf_bytes_with_the_new_hash(self):
        core = self.root / 'skills/rule-maker/rules/CORE.md'
        core.write_bytes(core.read_bytes() + b'extra\n')
        self.assertEqual(self.run_tool('--apply'), 0)
        raw = self.manifest.read_bytes()
        self.assertNotIn(CRLF, raw)
        self.assertEqual(json.loads(raw)['sha256']['CORE.md'], hashlib.sha256(core.read_bytes()).hexdigest())

    def test_preview_writes_nothing(self):
        before = self.manifest.read_bytes()
        core = self.root / 'skills/rule-maker/rules/CORE.md'
        core.write_bytes(core.read_bytes() + b'extra\n')
        self.assertEqual(self.run_tool(), 0)
        self.assertEqual(self.manifest.read_bytes(), before)


@unittest.skipUnless(shutil.which('git') and (ROOT / '.git').exists(), 'Git checkout unavailable')
class CheckoutPolicyTests(unittest.TestCase):
    def test_skills_are_lf_and_task_records_are_untouched(self):
        out = subprocess.run(['git', '-C', str(ROOT), 'check-attr', 'eol', '--',
                              'skills/rule-maker/rules/CORE.md', 'docs/plans/any/PLAN.md'],
                             capture_output=True, text=True, check=True).stdout
        self.assertIn('skills/rule-maker/rules/CORE.md: eol: lf', out)
        self.assertIn('docs/plans/any/PLAN.md: eol: unspecified', out)


class HomeResolutionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = Path(self.tmp.name)

    def call(self, main, *args):
        # Path.home() and Path('~').expanduser() both resolve through os.path.expanduser; returning the
        # input unchanged simulates "no home directory" on every OS without reading the real one.
        out, err = io.StringIO(), io.StringIO()
        unresolved = mock.Mock(side_effect=lambda value: value)
        with mock.patch.dict(os.environ, {}, clear=True), mock.patch('os.path.expanduser', unresolved), \
             contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = main(list(args))
        self.expanded = [c.args[0] for c in unresolved.call_args_list]
        return code, err.getvalue() + out.getvalue()

    def test_policy_without_home_fails_with_controlled_error(self):
        code, err = self.call(policy.main, '--check')
        self.assertEqual(code, 2)
        self.assertIn('pass --home', err)

    def test_policy_tilde_home_without_home_fails_with_controlled_error(self):
        code, _ = self.call(policy.main, '--check', '--home', '~')
        self.assertEqual(code, 2)
        self.assertIn('~', self.expanded)

    def test_activation_tilde_root_without_home_fails_with_controlled_error(self):
        code, _ = self.call(activation.main, '--check', '--host', 'claude', '--claude-dir', '~/claude')
        self.assertEqual(code, 2)
        self.assertIn('~', self.expanded)

    def test_audit_tilde_home_without_home_is_blocked_not_crashed(self):
        code, out = self.call(audit.main, '--check-global', '--home', '~')
        self.assertEqual(code, 2)
        self.assertIn('BLOCKED', out)
        self.assertIn('~', self.expanded)

    def test_activation_with_explicit_roots_never_expands_a_home(self):
        self.call(activation.main, '--check', '--claude-dir', str(self.dir / 'claude'),
                  '--codex-home', str(self.dir / 'codex'))
        self.assertNotIn('~', self.expanded)

    def test_activation_with_explicit_roots_does_not_need_home(self):
        code, err = self.call(activation.main, '--check', '--claude-dir', str(self.dir / 'claude'),
                              '--codex-home', str(self.dir / 'codex'))
        self.assertNotEqual(code, 2, err)

    def test_activation_single_host_needs_only_that_root(self):
        code, err = self.call(activation.main, '--check', '--host', 'claude', '--claude-dir', str(self.dir / 'claude'))
        self.assertNotEqual(code, 2, err)

    def test_activation_needing_a_default_root_fails_with_controlled_error(self):
        code, err = self.call(activation.main, '--check', '--host', 'codex')
        self.assertEqual(code, 2)
        self.assertIn('pass --home', err)


class LinksHelperTests(unittest.TestCase):
    def test_unrelated_link_errors_propagate_instead_of_skipping(self):
        from links_helper import make_link
        with tempfile.TemporaryDirectory() as tmp:
            # A directory link reaches a real OS call on every host (symlink, or the junction fallback).
            with self.assertRaises(OSError):
                make_link(Path(tmp) / 'absent' / 'link', Path(tmp), directory=True)

    def test_capability_failure_is_the_only_fallback(self):
        from links_helper import make_link
        denied = OSError('privilege not held')
        denied.winerror = 1314
        other = OSError('something else')
        other.winerror = 5
        with tempfile.TemporaryDirectory() as tmp:
            link = Path(tmp) / 'link'
            for directory in (False, True):
                with self.subTest(directory=directory), \
                     mock.patch.object(Path, 'symlink_to', side_effect=other), self.assertRaises(OSError):
                    make_link(link, Path(tmp), directory=directory)
            with mock.patch.object(Path, 'symlink_to', side_effect=denied), self.assertRaises(unittest.SkipTest):
                make_link(link, Path(tmp))


if __name__ == '__main__':
    unittest.main()
