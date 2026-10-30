"""Package contracts and freshness regressions; content assertions do not prove agent compliance."""
from __future__ import annotations
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
RULES=ROOT/'skills/rule-maker/rules'
spec=importlib.util.spec_from_file_location('readiness_engineering_tests',ROOT/'skills/rule-maker/scripts/readiness.py')
r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)

class EngineeringRulesTests(unittest.TestCase):
    def test_new_modules_are_in_the_integrity_manifest(self):
        data=json.loads((RULES/'version.json').read_text())
        for name in ('ENGINEERING.md','VERSIONS.md','data-contracts.md','lifetimes.md','reliability.md','testing.md','security.md','performance.md','compatibility.md','php.md','laravel.md','rust.md'):
            self.assertIn(name,data['files']);self.assertIn(name,data['sha256'])
        self.assertEqual(data['rules_version'],'1.1.0')

    def test_core_has_no_universal_nesting_or_comment_quota(self):
        text=(RULES/'CORE.md').read_text()
        self.assertIn('No arbitrary universal',text)
        self.assertIn('not authorise a repository-wide cleanup',text)
        self.assertIn('**default**',text)
        self.assertLessEqual(len(text.split()),650)

    def test_selective_loading_and_rust_boundary(self):
        start=(RULES/'START.md').read_text()
        for name in ('ENGINEERING.md','VERSIONS.md','php.md','laravel.md','rust.md'):
            self.assertIn(name,start)
        self.assertIn('Load only for actual Rust work',(RULES/'rust.md').read_text())
        self.assertIn('Chromium-only',(RULES/'rust.md').read_text())

    def test_engineering_modules_have_applicability_checks_and_sources(self):
        for name in ('data-contracts','lifetimes','reliability','testing','security','performance','compatibility'):
            text=(RULES/(name+'.md')).read_text()
            self.assertIn('Applies to',text,name)
            self.assertIn('Verification',text,name)
            self.assertTrue('Sources:' in text or 'Source:' in text,name)
            self.assertLessEqual(len(text.split()),450,name)

    def test_laravel_preserves_old_structure_and_version_choice(self):
        text=(RULES/'laravel.md').read_text()
        for fragment in ('older application structure','No automatic migration or upgrade','php.md','versions','parameter'):
            if fragment=='versions':self.assertIn('VERSIONS.md',text)
            elif fragment=='parameter':self.assertIn('authorise',text)
            else:self.assertIn(fragment,text)

    def test_versions_distinguishes_runtime_platform_and_lock(self):
        text=(RULES/'VERSIONS.md').read_text()
        for fragment in ('emulated platform','not the real PHP runtime','not a dependency solver','monorepo'):
            self.assertIn(fragment,text)

    def test_review_routes_use_local_modules_not_new_dependencies(self):
        for name in ('skills/workflow/RULES.md','skills/workflow/AUDIT.md','skills/plan-review/SKILL.md'):
            self.assertIn('ENGINEERING.md',(ROOT/name).read_text())
        data=json.loads((ROOT/'skills/workflow/specialists.json').read_text())
        self.assertEqual(len(data['skills']),27)
        self.assertIn('grilling',data['skills'])
        self.assertNotIn('diagram-design',data['skills'])

    def test_version_input_freshness_includes_composer_and_cargo(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'src').mkdir()
            original=r.snapshot(root,['src'],task='test',host='fixture')
            for name,content in (('composer.json','{}'),('composer.lock','{}'),('.php-version','8.2'),('Cargo.toml','[package]'),('rust-toolchain.toml','[toolchain]')):
                with self.subTest(name=name):
                    (root/name).write_text(content)
                    changed=r.snapshot(root,['src'],task='test',host='fixture')
                    self.assertNotEqual(original['fingerprint'],changed['fingerprint'])
                    self.assertIsNotNone(changed['project_inputs'][name])
                    (root/name).unlink()

    def test_new_library_assessment_requires_refresh_not_task_migration(self):
        text=(ROOT/'UPGRADE.md').read_text()
        self.assertIn('assessment',text)
        self.assertIn('history',text)

    def test_scenarios_are_not_test_results(self):
        data=json.loads((ROOT/'tests/behavioral/engineering-rules.json').read_text())
        self.assertEqual(data['candidate_version'],json.loads((ROOT/'.claude-plugin/plugin.json').read_text())['version'])
        ids=[c['id'] for c in data['cases']]
        self.assertEqual(len(ids),len(set(ids)))
        self.assertGreaterEqual(len(ids),20)
        for c in data['cases']:
            self.assertEqual(c['result'],'NOT_RUN')
            self.assertTrue(c['prompt'] and c['expected'] and c['preparation'])

if __name__=='__main__':unittest.main()
