"""Setup safety and instruction contracts, not live Claude/Codex behavior."""
from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import io
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('workflow_global_policy', ROOT/'skills/workflow/scripts/global_policy.py')
g = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = g
SPEC.loader.exec_module(g)


class GlobalPolicyTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.home = Path(self.temp.name)/'user with spaces'
        self.claude = self.home/'.claude'
        self.codex = self.home/'.codex'

    def plan(self, host='both'):
        return g.build_plan(self.home, self.claude, self.codex, host)

    def write(self, relative, data):
        path = self.home/relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return path

    def cli(self, *args):
        with mock.patch.dict(os.environ, {}, clear=True), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return g.main(['--home',str(self.home),*args])

    def test_preview_does_not_create_home(self):
        self.assertEqual(self.cli(), 0)
        self.assertFalse(self.home.exists())

    def test_missing_check_is_read_only(self):
        self.assertEqual(self.cli('--check'),1)
        self.assertFalse(self.home.exists())

    def test_apply_creates_only_three_expected_files(self):
        self.assertEqual(self.cli('--apply'),0)
        actual={str(p.relative_to(self.home)) for p in self.home.rglob('*') if p.is_file()}
        self.assertEqual(actual,{'.workflow-axa/ARTIFACTS.md','.claude/CLAUDE.md','.codex/AGENTS.md'})
        self.assertEqual(self.cli('--check'),0)

    def test_apply_is_idempotent_without_backups(self):
        g.apply_plan(self.plan())
        before={p:p.read_bytes() for p in self.home.rglob('*') if p.is_file()}
        again=self.plan();self.assertTrue(all(c.before==c.after for c in again))
        g.apply_plan(again)
        self.assertEqual(before,{p:p.read_bytes() for p in self.home.rglob('*') if p.is_file()})

    def test_unrelated_existing_content_and_crlf_are_preserved(self):
        old=b'\xef\xbb\xbf# Personal instructions\r\n\r\nKeep this exact: \xe2\x86\x92\r\n'
        path=self.write('.claude/CLAUDE.md',old)
        g.apply_plan(self.plan())
        data=path.read_bytes();self.assertTrue(data.startswith(old))
        self.assertEqual(data.count(b'\n'),data.count(b'\r\n'))
        self.assertEqual(data.count(b'\xef\xbb\xbf'),1)

    def test_managed_replacement_preserves_surrounding_bytes(self):
        before=('prefix\r\n'+g.START+'\r\nold\r\n'+g.END+'\r\nsuffix without newline').encode()
        after=g.merge_block(before,g.START+'\nnew\n'+g.END)
        self.assertEqual(after,('prefix\r\n'+g.START+'\r\nnew\r\n'+g.END+'\r\nsuffix without newline').encode())

    def test_existing_override_and_base_are_both_updated(self):
        override=self.write('.codex/AGENTS.override.md',b'# Temporary constraints\n')
        plan=self.plan();self.assertEqual(len(plan),4)
        g.apply_plan(plan)
        self.assertTrue(override.read_bytes().startswith(b'# Temporary constraints\n'))
        self.assertIn(g.START,(self.codex/'AGENTS.md').read_text())
        self.assertEqual(self.cli('--check'),0)

    def test_empty_override_is_not_changed(self):
        override=self.write('.codex/AGENTS.override.md',b'\xef\xbb\xbf \r\n')
        before=override.read_bytes();g.apply_plan(self.plan())
        self.assertEqual(override.read_bytes(),before)

    def test_unowned_policy_is_not_overwritten(self):
        p=self.write('.workflow-axa/ARTIFACTS.md',b'User-owned policy\n')
        with self.assertRaisesRegex(ValueError,'unowned'):
            self.plan()
        self.assertEqual(p.read_bytes(),b'User-owned policy\n')
        self.assertFalse(self.claude.exists())

    def test_modified_policy_requires_review(self):
        g.apply_plan(self.plan());p=self.home/'.workflow-axa/ARTIFACTS.md'
        p.write_bytes(p.read_bytes()+b'\nLocal edit\n')
        with self.assertRaisesRegex(ValueError,'modified'):
            self.plan()

    def test_newer_policy_cannot_be_downgraded(self):
        body=b'newer instructions\n';digest=hashlib.sha256(body).hexdigest()
        self.write('.workflow-axa/ARTIFACTS.md',f'<!-- workflow-axa:artifact-policy version=99.0.0 sha256={digest} -->\n'.encode()+body)
        with self.assertRaisesRegex(ValueError,'downgrade'):
            self.plan()

    def test_valid_older_managed_policy_can_upgrade(self):
        body=b'previous instructions\n';digest=hashlib.sha256(body).hexdigest()
        self.write('.workflow-axa/ARTIFACTS.md',f'<!-- workflow-axa:artifact-policy version=2.4.0 sha256={digest} -->\n'.encode()+body)
        g.apply_plan(self.plan());self.assertEqual(self.cli('--check'),0)

    def test_partial_duplicate_and_reversed_markers_rejected(self):
        for text in (g.START,g.END,g.START+g.END+g.START+g.END,g.END+g.START):
            with self.subTest(text=text),self.assertRaises(ValueError):
                g.merge_block(text.encode(),g.START+'\nnew\n'+g.END)

    def test_preflight_failure_writes_nothing_else(self):
        path=self.write('.codex/AGENTS.md',g.START.encode())
        self.assertEqual(self.cli('--apply'),2)
        self.assertEqual(path.read_bytes(),g.START.encode())
        self.assertFalse((self.home/'.workflow-axa').exists())
        self.assertFalse(self.claude.exists())

    def test_changed_input_after_plan_is_rejected(self):
        p=self.write('.claude/CLAUDE.md',b'initial\n');plan=self.plan()
        p.write_bytes(b'new concurrent instruction\n')
        with self.assertRaisesRegex(ValueError,'changed after'):
            g.apply_plan(plan)
        self.assertFalse((self.home/'.workflow-axa').exists())
        self.assertEqual(p.read_bytes(),b'new concurrent instruction\n')

    def test_new_file_created_after_plan_is_not_overwritten(self):
        plan=self.plan();self.write('.codex/AGENTS.md',b'Another session\n')
        with self.assertRaises(ValueError):g.apply_plan(plan)
        self.assertFalse((self.home/'.workflow-axa').exists())

    def test_symlinked_file_is_rejected(self):
        target=self.write('real.txt',b'not ours');self.claude.mkdir()
        (self.claude/'CLAUDE.md').symlink_to(target)
        with self.assertRaisesRegex(ValueError,'Symlink'):
            self.plan()
        self.assertEqual(target.read_bytes(),b'not ours')

    def test_symlinked_parent_is_rejected(self):
        target=self.home/'real';target.mkdir(parents=True)
        self.claude.symlink_to(target,target_is_directory=True)
        with self.assertRaisesRegex(ValueError,'Symlink'):
            self.plan()

    def test_hardlinked_file_is_rejected(self):
        target=self.write('real.txt',b'not ours');self.claude.mkdir()
        os.link(target,self.claude/'CLAUDE.md')
        with self.assertRaisesRegex(ValueError,'single-link'):
            self.plan()

    def test_config_directory_not_file_rejected(self):
        (self.claude/'CLAUDE.md').mkdir(parents=True)
        with self.assertRaises(ValueError):self.plan()

    def test_non_utf8_instructions_are_not_rewritten(self):
        p=self.write('.claude/CLAUDE.md',b'\xffinvalid')
        with self.assertRaises(UnicodeError):self.plan()
        self.assertEqual(p.read_bytes(),b'\xffinvalid')

    def test_relative_or_newline_paths_rejected(self):
        for path in (Path('relative'),self.home/'bad\nfile',self.home/'bad`file'):
            with self.subTest(path=path),self.assertRaises(ValueError):g.safe_path(path)

    def test_space_escaping_and_codex_plain_read_instruction(self):
        plan=self.plan();claude=plan[1].after.decode();codex=plan[2].after.decode()
        self.assertIn('user\\ with\\ spaces',claude)
        self.assertIn('not an automatic Markdown import',codex)
        self.assertNotIn('@'+plan[0].path.as_posix(),codex)

    def test_custom_environment_roots(self):
        altc=self.home/'profiles/c';altx=self.home/'profiles/x'
        with mock.patch.dict(os.environ,{'CLAUDE_CONFIG_DIR':str(altc),'CODEX_HOME':str(altx)},clear=True),contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(g.main(['--home',str(self.home),'--apply']),0)
        self.assertTrue((altc/'CLAUDE.md').exists());self.assertTrue((altx/'AGENTS.md').exists())
        self.assertFalse(self.claude.exists());self.assertFalse(self.codex.exists())

    def test_explicit_roots_take_precedence(self):
        altc=self.home/'explicit-c';altx=self.home/'explicit-x'
        with mock.patch.dict(os.environ,{'CLAUDE_CONFIG_DIR':'relative-bad','CODEX_HOME':'relative-bad'},clear=True),contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(g.main(['--home',str(self.home),'--claude-dir',str(altc),'--codex-home',str(altx),'--apply']),0)
        self.assertTrue((altc/'CLAUDE.md').exists());self.assertTrue((altx/'AGENTS.md').exists())

    def test_single_host_does_not_touch_the_other(self):
        g.apply_plan(self.plan('claude'))
        self.assertTrue(self.claude.exists());self.assertFalse(self.codex.exists())
        self.assertEqual(len(self.plan('codex')),2)

    def test_stale_host_block_detected_without_writes(self):
        g.apply_plan(self.plan());p=self.codex/'AGENTS.md'
        p.write_bytes(p.read_bytes().replace(b'keep only necessary',b'keep all'))
        before=p.read_bytes();self.assertEqual(self.cli('--check'),1)
        self.assertEqual(before,p.read_bytes())

    def test_apply_preserves_existing_mode(self):
        p=self.write('.claude/CLAUDE.md',b'rules\n');p.chmod(0o640)
        g.apply_plan(self.plan());self.assertEqual(p.stat().st_mode & 0o777,0o640)

    def test_package_version_and_policy_agree(self):
        version=json.loads((ROOT/'.claude-plugin/plugin.json').read_text())['version']
        self.assertEqual(g.VERSION,version)
        self.assertIn('Policy revision: '+version,g.SOURCE.read_text())

    def test_unrelated_project_artifacts_are_untouched(self):
        p=self.write('project/.artifacts/builds2/proof.txt',b'keep this old evidence')
        g.apply_plan(self.plan());self.assertEqual(p.read_bytes(),b'keep this old evidence')
        self.assertEqual(list(p.parent.iterdir()),[p])


class ArtifactInstructionTests(unittest.TestCase):
    def text(self,name):return (ROOT/name).read_text()

    def test_categories_and_protected_exceptions(self):
        text=self.text('skills/workflow/ARTIFACTS.md')
        for phrase in ('Temporary work','Evidence:','Deliverables','isolated child directories for concurrency','before/after','Screenshot sets','A hash cannot restore'):
            self.assertIn(phrase,text)

    def test_no_new_record_and_no_legacy_purge(self):
        text=self.text('skills/workflow/ARTIFACTS.md')
        for phrase in ('no task','do not create PLAN/TODO','no loose files','absence from FINDINGS is not deletion authority','never','older'):
            self.assertIn(phrase.lower(),text.lower())

    def test_six_skills_include_artifact_boundary(self):
        for skill in ('workflow','codebase-map','resume-task','task-status','workflow-doctor','plan-review'):
            self.assertIn('artifact',self.text(f'skills/{skill}/SKILL.md').lower(),skill)

    def test_doctor_is_read_only_and_checks_globals(self):
        text=self.text('skills/workflow-doctor/SKILL.md')
        self.assertIn('global_policy.py --check',text)
        self.assertIn('never repair them automatically',text)
        self.assertIn('not a new artifact folder',text)

    def test_investigations_and_required_deliverables_not_removed(self):
        text=self.text('skills/workflow/ARTIFACTS.md')
        for phrase in ('Keep required PLAN/TODO/FINDINGS/DECISIONS','unresolved-failure','do not delete a requested build','cannot enforce retention'):
            self.assertIn(phrase.lower(),text.lower())


if __name__=='__main__':unittest.main()
