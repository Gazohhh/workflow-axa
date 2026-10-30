"""Catalogue safety/freshness checks, not human design approval or live model tests."""
from __future__ import annotations
import copy
import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'skills/ui-design/scripts/check_design_kit.py'
spec = importlib.util.spec_from_file_location('design_kit_tests', SCRIPT)
k = importlib.util.module_from_spec(spec); spec.loader.exec_module(k)


class DesignKitTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / 'project'; self.root.mkdir()
        self.data = {'schema_version':1,'kit_id':'fixture-kit','revision':'r1','status':'approved',
                     'scope':['src'], 'approval':self.ref('docs/approval.md','SYNTHETIC: owner accepts named fixture'),
                     'preview':self.ref('docs/preview.md','SYNTHETIC: test-only destination, not public'), 'items':[]}
        self.data['items'] = [self.item('save-button')]

    def ref(self, name, contents):
        p=self.root/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(contents)
        return {'path':name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}

    def item(self, key):
        return {'id':key,'kind':'component','name':key,'purpose':'Synthetic test operation',
                'status':'approved','scope':['src'],'sources':[self.ref('src/'+key+'.tsx','<button type="submit">Save</button>')],
                'approval':self.ref('docs/'+key+'.md','SYNTHETIC decision for '+key),
                'variants':['default'],'states':['enabled'],'uses':[]}

    def run_check(self, selected=(), scopes=()):
        (self.root/'kit.json').write_text(json.dumps(self.data))
        return k.inspect(self.root,'kit.json',selected,scopes)

    def test_current_references_still_require_semantic_review(self):
        result=self.run_check(['save-button'],['src/settings'])
        self.assertEqual(result['state'],'REVIEW_REQUIRED')
        for field in ('approval_authenticated','runtime_verified','implementation_approved'):
            self.assertFalse(result[field])
        self.assertTrue(result['scope_coverage_checked'])

    def test_no_scope_is_not_claimed_checked(self):
        self.assertFalse(self.run_check()['scope_coverage_checked'])

    def test_changed_source_blocks(self):
        (self.root/'src/save-button.tsx').write_text('changed presentation')
        self.assertEqual(self.run_check()['state'],'BLOCKED')

    def test_changed_approval_blocks(self):
        (self.root/'docs/save-button.md').write_text('approval revoked')
        self.assertEqual(self.run_check()['state'],'BLOCKED')

    def test_changed_kit_authority_blocks(self):
        (self.root/'docs/approval.md').write_text('different scope')
        self.assertEqual(self.run_check()['state'],'BLOCKED')

    def test_changed_preview_boundary_blocks(self):
        (self.root/'docs/preview.md').write_text('now public')
        self.assertEqual(self.run_check()['state'],'BLOCKED')

    def test_no_authority_is_not_implicitly_approved(self):
        self.data['approval']=None
        with self.assertRaises(ValueError):self.run_check()

    def test_item_needs_its_own_approval(self):
        self.data['items'][0]['approval']=None
        with self.assertRaises(ValueError):self.run_check()

    def test_empty_approved_kit_has_no_component_coverage(self):
        self.data['items']=[]
        self.assertEqual(self.run_check()['state'],'DRAFT')

    def test_template_is_draft_not_ready(self):
        self.data=json.loads((ROOT/'skills/ui-design/templates/design-kit.json').read_text())
        self.assertEqual(self.run_check()['state'],'DRAFT')

    def test_new_candidate_does_not_inherit_approval(self):
        row=self.item('pending'); row.update(status='candidate',approval=None)
        self.data['items'].append(row)
        self.assertEqual(self.run_check(['pending'])['state'],'DRAFT')
        self.assertEqual(self.run_check(['save-button'])['state'],'REVIEW_REQUIRED')

    def test_stale_unrelated_entry_does_not_block_scoped_selection(self):
        self.data['items'].append(self.item('unrelated'))
        (self.root/'src/unrelated.tsx').write_text('changed')
        self.assertEqual(self.run_check(['save-button'])['state'],'REVIEW_REQUIRED')
        self.assertEqual(self.run_check()['state'],'BLOCKED')

    def test_dependencies_are_checked_transitively(self):
        self.data['items'].append(self.item('token'))
        self.data['items'][0]['uses']=['token']
        (self.root/'src/token.tsx').write_text('changed')
        result=self.run_check(['save-button'])
        self.assertEqual(result['state'],'BLOCKED')
        self.assertEqual({r['id'] for r in result['checked_items']},{'token','save-button'})

    def test_deprecated_dependency_blocks(self):
        self.data['items'].append(self.item('token'))
        self.data['items'][1]['status']='deprecated'; self.data['items'][0]['uses']=['token']
        self.assertEqual(self.run_check(['save-button'])['state'],'BLOCKED')

    def test_deprecated_kit_blocks(self):
        self.data['status']='deprecated'
        self.assertEqual(self.run_check()['state'],'BLOCKED')

    def test_unknown_dependency_rejected(self):
        self.data['items'][0]['uses']=['absent']
        with self.assertRaises(ValueError):self.run_check()

    def test_cycle_rejected(self):
        self.data['items'][0]['uses']=['save-button']
        with self.assertRaises(ValueError):self.run_check()

    def test_invalid_selection_rejected(self):
        with self.assertRaises(ValueError):self.run_check(['absent'])

    def test_scope_prefix_is_not_string_prefix(self):
        self.data['items'][0]['scope']=['src/settings']
        self.assertEqual(self.run_check(['save-button'],['src/settings-other'])['state'],'BLOCKED')

    def test_item_scope_cannot_exceed_kit(self):
        self.data['items'][0]['scope']=['.']
        with self.assertRaises(ValueError):self.run_check()

    def test_unsafe_paths_rejected(self):
        for name in ('../escape','/tmp/escape','C:/escape','https://example.org/x','src/*','src\\file'):
            with self.subTest(path=name), self.assertRaises(ValueError): k.path_value(name)

    def test_unknown_fields_and_bool_schema_rejected(self):
        for field,value in (('schema_version',True),('auto_approve',True)):
            old=copy.deepcopy(self.data); self.data[field]=value
            with self.assertRaises(ValueError):self.run_check()
            self.data=old

    def test_duplicate_ids_rejected(self):
        self.data['items'].append(copy.deepcopy(self.data['items'][0]))
        with self.assertRaises(ValueError):self.run_check()

    def test_json_duplicate_fields_rejected(self):
        (self.root/'kit.json').write_text('{"schema_version":1,"schema_version":2}')
        with self.assertRaises(ValueError):k.inspect(self.root,'kit.json')

    def test_missing_reference_is_not_silently_ignored(self):
        (self.root/'src/save-button.tsx').unlink()
        with self.assertRaises(OSError):self.run_check()

    def test_symlink_reference_rejected(self):
        target=self.root/'src/save-button.tsx';target.unlink()
        try:target.symlink_to(self.root/'docs/approval.md')
        except OSError:self.skipTest('Symlinks unavailable')
        with self.assertRaises(ValueError):self.run_check()

    def test_oversized_input_rejected(self):
        (self.root/'src/save-button.tsx').write_bytes(b'x'*(k.MAX_FILE+1))
        with self.assertRaises(ValueError):self.run_check()

    def test_no_writes(self):
        self.run_check()
        before={p.relative_to(self.root):p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        k.inspect(self.root,'kit.json')
        after={p.relative_to(self.root):p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        self.assertEqual(before,after)

    def test_cli_exits_with_structural_review_not_approval(self):
        self.run_check()
        command=[sys.executable,str(SCRIPT),'--root',str(self.root),'--catalog','kit.json']
        result=subprocess.run(command,capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)
        self.assertFalse(json.loads(result.stdout)['implementation_approved'])
        self.data['status']='draft'; self.run_check()
        self.assertEqual(subprocess.run(command,capture_output=True).returncode,1)
        (self.root/'kit.json').write_text('invalid')
        result=subprocess.run(command,capture_output=True,text=True)
        self.assertEqual(result.returncode,2)
        self.assertEqual(json.loads(result.stdout)['state'],'BLOCKED')

if __name__=='__main__':unittest.main()
