"""Static facts/read-only behaviour; these are not live-agent compliance tests."""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'skills/rule-maker/scripts/version_facts.py'
spec = importlib.util.spec_from_file_location('version_facts_under_test', SCRIPT)
v = importlib.util.module_from_spec(spec)
spec.loader.exec_module(v)


class VersionFactsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'repo'
        self.root.mkdir()

    def put(self, path, value):
        p = self.root / path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(value) if isinstance(value, (dict, list)) else value, encoding='utf-8')
        return p

    def inspect(self, *scopes):
        return v.inspect_versions(self.root, list(scopes or ('.',)))

    def npm(self, version='18.3.1', fmt=3, base=''):
        base = base.rstrip('/') + '/' if base else ''
        self.put(base+'package.json', {'dependencies': {'react': '^18.2.0'}, 'engines': {'node': '>=18'}})
        lock = {'lockfileVersion': fmt}
        lock['dependencies' if fmt == 1 else 'packages'] = {('react' if fmt == 1 else 'node_modules/react'): {'version': version}}
        self.put(base+'package-lock.json', lock)

    def composer(self, version='v11.3.0', base=''):
        base = base.rstrip('/') + '/' if base else ''
        self.put(base+'composer.json', {'require': {'php': '^8.2', 'laravel/framework': '^11.0'}, 'config': {'platform': {'php': '8.2.0'}}})
        self.put(base+'composer.lock', {'packages': [{'name': 'laravel/framework', 'version': version}], 'packages-dev': [], 'platform': {'php': '^8.2'}, 'platform-dev': []})

    def test_empty_project_has_no_invented_stack_or_readiness(self):
        result = self.inspect()
        self.assertEqual(result['contexts'], [])
        self.assertEqual(result['state'], 'REVIEW_REQUIRED')
        self.assertFalse(result['runtime_verified'])
        self.assertFalse(result['compatibility_verified'])
        self.assertFalse(result['implementation_approved'])

    def test_range_and_locked_version_stay_distinct(self):
        self.npm()
        c = self.inspect('src')['contexts'][0]
        self.assertEqual(c['packages'][0]['declared'][0]['constraint'], '^18.2.0')
        self.assertEqual(c['packages'][0]['locked'], '18.3.1')
        self.assertIn('NOT_CHECKED', c['constraint_compatibility'])
        self.assertEqual(c['engine_constraints'], {'node': '>=18'})

    def test_npm_all_supported_lock_schemas(self):
        for fmt in (1, 2, 3):
            with self.subTest(fmt=fmt):
                self.npm(fmt=fmt)
                self.assertEqual(self.inspect()['contexts'][0]['packages'][0]['locked'], '18.3.1')

    def test_unknown_npm_schema_is_not_guessed(self):
        self.npm(fmt=99)
        row = self.inspect()['contexts'][0]['packages'][0]
        self.assertIsNone(row['locked'])
        self.assertIn('Unsupported', row['limit'])

    def test_bool_is_not_a_lock_schema_number(self):
        self.npm(fmt=True)
        row = self.inspect()['contexts'][0]['packages'][0]
        self.assertIsNone(row['locked'])

    def test_separate_apps_keep_separate_versions(self):
        self.npm('18.3.1', base='apps/old')
        self.npm('19.0.0', base='apps/new')
        contexts = self.inspect('apps/old/src', 'apps/new/src')['contexts']
        versions = {c['manifest']: c['packages'][0]['locked'] for c in contexts}
        self.assertEqual(versions, {'apps/old/package.json': '18.3.1', 'apps/new/package.json': '19.0.0'})

    def test_duplicate_scopes_do_not_duplicate_contexts(self):
        self.npm()
        self.assertEqual(len(self.inspect('src', 'src', 'test')['contexts']), 1)

    def test_workspace_lock_uses_nearest_package_slot(self):
        self.put('apps/ui/package.json', {'dependencies': {'react': '^18.2.0'}})
        self.put('package-lock.json', {'lockfileVersion': 3, 'packages': {
            'apps/ui': {'dependencies': {'react': '^18.2.0'}},
            'node_modules/react': {'version': '19.0.0'},
            'apps/ui/node_modules/react': {'version': '18.3.1'}}})
        row = self.inspect('apps/ui/src')['contexts'][0]['packages'][0]
        self.assertEqual(row['locked'], '18.3.1')

    def test_workspace_can_use_its_hoisted_slot(self):
        self.put('apps/ui/package.json', {'dependencies': {'react': '^18.2.0'}})
        self.put('package-lock.json', {'lockfileVersion': 3, 'packages': {
            'apps/ui': {}, 'node_modules/react': {'version': '18.3.1'}}})
        self.assertEqual(self.inspect('apps/ui/src')['contexts'][0]['packages'][0]['locked'], '18.3.1')

    def test_unrelated_ancestor_lock_is_not_borrowed(self):
        self.put('apps/ui/package.json', {'dependencies': {'react': '^18.2.0'}})
        self.put('package-lock.json', {'lockfileVersion': 3, 'packages': {'node_modules/react': {'version': '19.0.0'}}})
        row = self.inspect('apps/ui/src')['contexts'][0]['packages'][0]
        self.assertIsNone(row['locked'])
        self.assertIn('Ancestor lock', row['limit'])

    def test_multiple_lockfiles_require_selection(self):
        self.npm()
        self.put('yarn.lock', 'unparsed')
        c = self.inspect()['contexts'][0]
        self.assertIsNone(c['packages'][0]['locked'])
        self.assertIn('Multiple lockfiles', c['warnings'][0])

    def test_pnpm_yarn_bun_are_reported_without_guessing(self):
        for filename in ('pnpm-lock.yaml', 'yarn.lock', 'bun.lock', 'bun.lockb'):
            with self.subTest(filename=filename):
                self.put('package.json', {'dependencies': {'react': '^18'}})
                p = self.put(filename, 'react 19 suspicious content not interpreted')
                result = self.inspect()
                self.assertIsNone(result['contexts'][0]['packages'][0]['locked'])
                self.assertIn('does not parse', result['contexts'][0]['warnings'][0])
                self.assertIn(filename, result['sources'])
                p.unlink()

    def test_manager_conflict_does_not_choose_stale_npm_lock(self):
        self.npm()
        self.put('package.json', {'packageManager': 'pnpm@9.0.0', 'dependencies': {'react': '^18'}})
        c = self.inspect()['contexts'][0]
        self.assertIsNone(c['packages'][0]['locked'])
        self.assertIn('conflicts', c['warnings'][0])

    def test_missing_lock_preserves_only_declared_facts(self):
        self.put('package.json', {'dependencies': {'react': '^18'}})
        c = self.inspect()['contexts'][0]
        self.assertIsNone(c['packages'][0]['locked'])
        self.assertIn('No lockfile', c['warnings'][0])

    def test_linked_package_does_not_claim_registry_version(self):
        self.npm()
        self.put('package-lock.json', {'lockfileVersion': 3, 'packages': {'node_modules/react': {'version': '18.3.1', 'link': True}}})
        row = self.inspect()['contexts'][0]['packages'][0]
        self.assertIsNone(row['locked'])
        self.assertIn('Linked/aliased', row['limit'])

    def test_dependency_url_credentials_are_not_echoed(self):
        self.put('package.json', {'dependencies': {'react': 'https://user:SECRET@registry.invalid/react.tgz'}})
        text = json.dumps(self.inspect())
        self.assertNotIn('SECRET', text)
        self.assertNotIn('registry.invalid', text)
        self.assertIn('non-version', text)

    def test_npm_alias_requires_review(self):
        self.npm()
        self.put('package.json', {'dependencies': {'react': 'npm:preact@10'}})
        c = self.inspect()['contexts'][0]
        self.assertIsNone(c['packages'][0]['locked'])
        self.assertIn('explicit resolution', c['packages'][0]['limit'])

    def test_composer_platform_and_lock_are_not_runtime(self):
        self.composer()
        c = self.inspect('app')['contexts'][0]
        self.assertEqual(c['requirements']['php'][0]['constraint'], '^8.2')
        self.assertEqual(c['platform_emulation']['php'], '8.2.0')
        self.assertEqual(c['packages'][0]['locked'], 'v11.3.0')
        self.assertIn('NOT_OBSERVED', c['runtime'])
        self.assertIn('NOT_INFERRED', c['application_structure'])
        self.assertEqual(c['modules'], ['php.md', 'laravel.md'])

    def test_composer_empty_platform_array_is_accepted(self):
        self.composer()
        c = self.inspect()['contexts'][0]
        self.assertEqual(c['lock_platform-dev'], {})

    def test_composer_without_lock_is_not_resolved(self):
        self.composer()
        (self.root/'composer.lock').unlink()
        c = self.inspect()['contexts'][0]
        self.assertIsNone(c['lockfile'])
        self.assertEqual(c['packages'], [])
        self.assertIn('No corresponding', c['warnings'][0])

    def test_php_without_laravel_does_not_load_laravel(self):
        self.put('composer.json', {'require': {'php': '^8.1'}})
        self.assertEqual(self.inspect()['contexts'][0]['modules'], ['php.md'])

    def test_standalone_illuminate_is_not_called_full_app(self):
        self.put('composer.json', {'require': {'illuminate/database': '^10.0'}})
        c = self.inspect()['contexts'][0]
        self.assertIn('laravel.md', c['modules'])
        self.assertIn('NOT_INFERRED', c['application_structure'])

    def test_composer_aliases_are_explicit(self):
        self.composer()
        p = self.root/'composer.lock';d=json.loads(p.read_text());d['aliases']=[{'package':'laravel/framework','version':'dev-main','alias':'11.0'}]
        p.write_text(json.dumps(d))
        self.assertIn('aliases', self.inspect()['contexts'][0]['warnings'][0])

    def test_composer_platform_extension_false_is_preserved(self):
        self.put('composer.json', {'require': {'php':'^8.1'}, 'config': {'platform': {'php':'8.1.0','ext-foo':False}}})
        self.assertIs(self.inspect()['contexts'][0]['platform_emulation']['ext-foo'], False)

    def test_composer_and_js_in_same_app_are_separate(self):
        self.composer();self.npm()
        self.assertEqual({c['ecosystem'] for c in self.inspect()['contexts']}, {'php','javascript'})

    def test_multiple_composer_apps_do_not_use_root_lock(self):
        self.composer(base='old', version='v10.4.0')
        self.composer(base='new', version='v12.0.0')
        self.assertEqual({c['packages'][0]['locked'] for c in self.inspect('old/app','new/app')['contexts']}, {'v10.4.0','v12.0.0'})

    def test_unity_config_and_render_pipeline_facts(self):
        self.put('UnityClient/ProjectSettings/ProjectVersion.txt', 'm_EditorVersion: 6000.6.1f1\n')
        self.put('UnityClient/Packages/manifest.json', {'dependencies': {'com.unity.render-pipelines.universal':'17.6.0'}})
        self.put('UnityClient/Packages/packages-lock.json', {'dependencies': {'com.unity.render-pipelines.universal': {'version':'17.6.0'}}})
        c = self.inspect('UnityClient/Assets')['contexts'][0]
        self.assertEqual(c['editor_configured'], '6000.6.1f1')
        self.assertEqual(c['packages'][0]['locked'], '17.6.0')
        self.assertIn('NOT_OBSERVED', c['runtime'])

    def test_rust_does_not_fake_toml_resolution(self):
        self.put('Cargo.toml', '[package]\nedition = "2021"\nrust-version = "1.70"\n')
        self.put('rust-toolchain.toml', '[toolchain]\nchannel = "stable"')
        c = self.inspect('src')['contexts'][0]
        self.assertEqual(c['ecosystem'], 'rust')
        self.assertIn('NOT_PARSED', c['versions'])
        self.assertIn('rust-toolchain.toml', c['sources'])

    def test_read_only_cli_does_not_execute_scripts_or_write_files(self):
        marker = self.root/'executed'
        self.put('package.json', {'scripts':{'postinstall':f'touch {marker}'},'dependencies':{'react':'18.3.1'}})
        self.put('composer.json', {'scripts':{'post-install-cmd':[f'touch {marker}']},'require':{'php':'^8.1'}})
        self.put('.env','PRIVATE=DO_NOT_ECHO')
        before={p.relative_to(self.root).as_posix():p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        out=subprocess.run([sys.executable,str(SCRIPT),'--root',str(self.root),'--scope','.'],capture_output=True,text=True)
        self.assertEqual(out.returncode,0,out.stderr)
        self.assertEqual(json.loads(out.stdout)['state'],'REVIEW_REQUIRED')
        self.assertNotIn('DO_NOT_ECHO',out.stdout)
        self.assertFalse(marker.exists())
        after={p.relative_to(self.root).as_posix():p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        self.assertEqual(before,after)

    def test_bom_json_is_readable(self):
        self.put('package.json','\ufeff{"dependencies":{"react":"18.3.1"}}')
        self.assertEqual(self.inspect()['contexts'][0]['packages'][0]['name'],'react')

    def test_invalid_json_fails_instead_of_guessing(self):
        self.put('composer.json','not JSON')
        with self.assertRaises(ValueError): self.inspect()

    def test_unexpected_map_shape_is_rejected(self):
        self.put('package.json', {'dependencies':['react']})
        with self.assertRaises(ValueError): self.inspect()

    def test_bad_composer_lock_shape_is_rejected(self):
        self.composer();self.put('composer.lock',{'packages':{}})
        with self.assertRaises(ValueError): self.inspect()

    def test_large_input_is_rejected(self):
        self.put('package.json',' '* (v.MAX_BYTES+1))
        with self.assertRaises(ValueError): self.inspect()

    def test_paths_cannot_escape(self):
        for scope in ('../other','/absolute','C:/wrong','bad\\scope','bad\nname'):
            with self.subTest(scope=scope),self.assertRaises(ValueError):self.inspect(scope)

    def test_linked_manifest_is_rejected(self):
        outside=Path(self.tmp.name)/'outside.json';outside.write_text('{}')
        (self.root/'package.json').symlink_to(outside)
        with self.assertRaises(ValueError): self.inspect()

    def test_linked_scope_is_rejected(self):
        outside=Path(self.tmp.name)/'outside';outside.mkdir()
        (self.root/'other').symlink_to(outside,target_is_directory=True)
        with self.assertRaises(ValueError): self.inspect('other')

    @unittest.skipUnless(hasattr(os,'mkfifo'),'FIFO unavailable')
    def test_nonregular_input_is_rejected_without_reading(self):
        os.mkfifo(self.root/'package.json')
        with self.assertRaises(ValueError): self.inspect()

    def test_changed_version_input_changes_source_identity(self):
        self.npm('18.3.1');a=self.inspect()['sources']
        self.npm('19.0.0');b=self.inspect()['sources']
        self.assertNotEqual(a['package-lock.json'],b['package-lock.json'])

    def test_nested_scope_does_not_crawl_unrelated_apps(self):
        self.npm(base='a');self.put('b/composer.json','malformed')
        self.assertEqual(len(self.inspect('a/src')['contexts']),1)

    def test_proposed_nonexistent_file_resolves_parent_manifests(self):
        self.npm()
        self.assertEqual(self.inspect('src/new/component.tsx')['contexts'][0]['manifest'],'package.json')

    def test_malformed_cli_has_clear_blocked_exit(self):
        self.put('package.json','[]')
        out=subprocess.run([sys.executable,str(SCRIPT),'--root',str(self.root),'--scope','.'],capture_output=True,text=True)
        self.assertEqual(out.returncode,2)
        self.assertEqual(json.loads(out.stdout)['state'],'BLOCKED')

    def test_scope_limit_prevents_unbounded_scan(self):
        with self.assertRaises(ValueError):v.inspect_versions(self.root,[f'a{i}' for i in range(65)])


if __name__ == '__main__':
    unittest.main()
