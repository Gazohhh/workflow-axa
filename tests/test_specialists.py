from __future__ import annotations

import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'skills/workflow/scripts/check_specialists.py'
spec = importlib.util.spec_from_file_location('specialist_checker', SCRIPT)
checker = importlib.util.module_from_spec(spec)
spec.loader.exec_module(checker)
CATALOGUE = json.loads(checker.CATALOGUE.read_text(encoding='utf-8'))


def make_skill(root: Path, name: str, *, disabled: bool | None = None) -> Path:
    """Synthetic local fixtures, not upstream skill copies or live invocations."""
    entry = CATALOGUE['skills'][name]
    folder = root / name
    folder.mkdir(parents=True)
    flag = entry['invocation'] == 'manual' if disabled is None else disabled
    content = f'---\nname: {name}\ndescription: Synthetic test fixture.\n'
    content += f'disable-model-invocation: {str(flag).lower()}\n---\nFixture only.\n'
    (folder / 'SKILL.md').write_text(content, encoding='utf-8')
    for relative in entry['required_files']:
        if relative != 'SKILL.md':
            path = folder / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(f'Synthetic supporting file: {relative}\n', encoding='utf-8')
    return folder


class SpecialistTests(unittest.TestCase):
    def test_catalogue_has_complete_collection_and_expected_routes(self):
        self.assertEqual(len(CATALOGUE['skills']), 27)
        routes = {n for n, row in CATALOGUE['skills'].items() if row['invocation'] == 'model'}
        self.assertEqual(routes, {'grilling', 'research', 'diagnosing-bugs', 'tdd', 'codebase-design',
                                 'writing-for-agents', 'code-review', 'domain-modeling', 'prototype', 'pr', 'wizard'})
        self.assertEqual(CATALOGUE['skills']['grill-me']['invocation'], 'manual')
        self.assertIsNone(CATALOGUE['source']['immutable_commit'])

    def test_present_files_do_not_claim_host_readiness(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_skill(root, 'grilling')
            result = checker.check([root], CATALOGUE, ['grilling'])
            self.assertTrue(result['disk_check_passed'])
            self.assertEqual(result['runtime_status'], 'NOT_CHECKED')
            self.assertEqual(result['source_authenticity'], 'NOT_CHECKED')
            self.assertEqual(result['skills']['grilling']['status'], 'ON_DISK')

    def test_complete_collection_in_nested_layout(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name, row in CATALOGUE['skills'].items():
                parent = root / Path(row['source_path']).parent
                make_skill(parent, name)
            result = checker.check([root], CATALOGUE, list(CATALOGUE['skills']))
            self.assertTrue(result['disk_check_passed'], result)

    def test_missing_wrapper_does_not_block_selected_grilling_route(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_skill(root, 'grilling')
            self.assertTrue(checker.check([root], CATALOGUE, ['grilling'])['disk_check_passed'])
            full = checker.check([root], CATALOGUE, ['grilling', 'grill-me'])
            self.assertFalse(full['disk_check_passed'])
            self.assertEqual(full['skills']['grill-me']['status'], 'MISSING')

    def test_wrapper_is_not_an_alias_for_missing_grilling(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_skill(root, 'grill-me')
            result = checker.check([root], CATALOGUE, ['grilling'])
            self.assertEqual(result['skills']['grilling']['status'], 'MISSING')

    def test_model_disabled_skill_is_not_available_for_route(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_skill(root, 'grilling', disabled=True)
            result = checker.check([root], CATALOGUE, ['grilling'])
            self.assertEqual(result['skills']['grilling']['status'], 'POLICY_MISMATCH')
            self.assertFalse(result['disk_check_passed'])

    def test_manual_workflow_must_not_be_silently_made_automatic(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_skill(root, 'implement', disabled=False)
            result = checker.check([root], CATALOGUE, ['implement'])
            self.assertEqual(result['skills']['implement']['status'], 'POLICY_MISMATCH')

    def test_duplicate_physical_copies_are_ambiguous(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_skill(root / 'user', 'research')
            make_skill(root / 'project', 'research')
            result = checker.check([root], CATALOGUE, ['research'])
            self.assertEqual(result['skills']['research']['status'], 'AMBIGUOUS')

    def test_overlapping_roots_do_not_invent_duplicate_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            folder = make_skill(root, 'research')
            result = checker.check([root, folder, root], CATALOGUE, ['research'])
            self.assertTrue(result['disk_check_passed'])
            self.assertEqual(len(result['skills']['research']['paths']), 1)

    def test_complete_directory_symlink_is_supported(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            actual = make_skill(root / 'actual', 'research')
            visible = root / 'visible'
            visible.mkdir()
            try:
                (visible / 'research').symlink_to(actual, target_is_directory=True)
            except (OSError, NotImplementedError):
                self.skipTest('Symlinks unavailable on this host')
            result = checker.check([visible], CATALOGUE, ['research'])
            self.assertTrue(result['disk_check_passed'])

    def test_missing_support_file_is_incomplete(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            folder = make_skill(root, 'tdd')
            (folder / 'mocking.md').unlink()
            result = checker.check([root], CATALOGUE, ['tdd'])
            self.assertEqual(result['skills']['tdd']['status'], 'INCOMPLETE')

    def test_changed_support_file_requires_review(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            folder = make_skill(root, 'tdd')
            baseline = checker.check([root], CATALOGUE, ['tdd'])
            (folder / 'tests.md').write_text('Different guidance.', encoding='utf-8')
            current = checker.check([root], CATALOGUE, ['tdd'], baseline)
            self.assertEqual(current['skills']['tdd']['status'], 'CHANGED')
            self.assertFalse(current['disk_check_passed'])

    def test_new_support_file_changes_fingerprint(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            folder = make_skill(root, 'research')
            baseline = checker.check([root], CATALOGUE, ['research'])
            (folder / 'new-rule.md').write_text('New guidance.', encoding='utf-8')
            self.assertEqual(checker.check([root], CATALOGUE, ['research'], baseline)['skills']['research']['status'], 'CHANGED')

    def test_same_content_can_move_between_accounts(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            folder = make_skill(root / 'first', 'grilling')
            baseline = checker.check([root / 'first'], CATALOGUE, ['grilling'])
            shutil.copytree(folder, root / 'second' / 'grilling')
            result = checker.check([root / 'second'], CATALOGUE, ['grilling'], baseline)
            self.assertTrue(result['disk_check_passed'])
            self.assertEqual(result['runtime_status'], 'NOT_CHECKED')

    def test_missing_baseline_entry_is_not_approved(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_skill(root, 'research')
            baseline = checker.check([root], CATALOGUE, ['research'])
            make_skill(root, 'grilling')
            result = checker.check([root], CATALOGUE, ['grilling'], baseline)
            self.assertEqual(result['skills']['grilling']['status'], 'NO_BASELINE')

    def test_wrong_baseline_source_is_refused(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            make_skill(root, 'research')
            baseline = checker.check([root], CATALOGUE, ['research'])
            baseline['source'] = 'unrelated/source'
            with self.assertRaises(ValueError):
                checker.check([root], CATALOGUE, ['research'], baseline)

    def test_malformed_frontmatter_cannot_pass(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            folder = make_skill(root, 'grilling')
            (folder / 'SKILL.md').write_text('No metadata', encoding='utf-8')
            result = checker.check([root], CATALOGUE, ['grilling'])
            self.assertFalse(result['disk_check_passed'])
            self.assertTrue(result['scan_errors'])

    def test_unknown_name_and_missing_root_are_errors(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                checker.check([Path(tmp)], CATALOGUE, ['not-a-skill'])
            with self.assertRaises(ValueError):
                checker.check([Path(tmp) / 'missing'], CATALOGUE, ['research'])

    def test_boolean_variants_and_model_only_visibility(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            folder = make_skill(root, 'grilling')
            path = folder / 'SKILL.md'
            path.write_text('---\nname: "grilling"\nuser-invocable: false\ndisable-model-invocation: OFF\n---\n', encoding='utf-8')
            self.assertTrue(checker.check([root], CATALOGUE, ['grilling'])['disk_check_passed'])
            path.write_text(path.read_text().replace('OFF', 'ON'), encoding='utf-8')
            self.assertFalse(checker.check([root], CATALOGUE, ['grilling'])['disk_check_passed'])

    def test_checker_does_not_modify_input_or_execute_support_scripts(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            folder = make_skill(root, 'research')
            marker = root / 'should-not-exist'
            (folder / 'run.py').write_text(f'from pathlib import Path\nPath({str(marker)!r}).touch()\n', encoding='utf-8')
            before = {p.relative_to(root): p.read_bytes() for p in root.rglob('*') if p.is_file()}
            result = checker.check([root], CATALOGUE, ['research'])
            after = {p.relative_to(root): p.read_bytes() for p in root.rglob('*') if p.is_file()}
            self.assertTrue(result['disk_check_passed'])
            self.assertEqual(before, after)
            self.assertFalse(marker.exists())

    def test_cli_reports_nonzero_for_missing_and_zero_for_files_only(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            command = [sys.executable, str(SCRIPT), '--root', str(root), '--only', 'grilling', '--json']
            result = subprocess.run(command, capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 1)
            self.assertEqual(json.loads(result.stdout)['skills']['grilling']['status'], 'MISSING')
            make_skill(root, 'grilling')
            result = subprocess.run(command, capture_output=True, text=True, timeout=10)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)['runtime_status'], 'NOT_CHECKED')


if __name__ == '__main__':
    unittest.main()
