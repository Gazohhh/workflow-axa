"""Read-only generated-index adapter tests. No Storybook install or UI execution."""
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/'skills/ui-design/scripts/inspect_kit_index.py'
sys.path.insert(0,str(SCRIPT.parent))
spec=importlib.util.spec_from_file_location('kit_index_test',SCRIPT)
k=importlib.util.module_from_spec(spec);spec.loader.exec_module(k)

class KitIndexTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name);(self.root/'src').mkdir()
        (self.root/'src/Buttons.stories.ts').write_text('synthetic source bytes')
        self.row={'id':'buttons-primary--default','title':'Buttons/Primary','name':'Default','type':'story','importPath':'./src/Buttons.stories.ts','tags':['approved']}
        self.data={'v':5,'entries':{self.row['id']:self.row}}
    def run_check(self,**kw):
        (self.root/'index.json').write_text(json.dumps(self.data))
        return k.inspect(self.root,'index.json',**kw)
    def test_real_source_reference_not_approval(self):
        out=self.run_check();self.assertEqual(out['state'],'REVIEW_REQUIRED')
        self.assertEqual(out['entries'][0]['source'],'src/Buttons.stories.ts')
        self.assertFalse(out['approval_authenticated']);self.assertFalse(out['runtime_verified'])
    def test_index_v4(self):
        self.data['v']=4;self.assertEqual(self.run_check()['state'],'REVIEW_REQUIRED')
    def test_unknown_schema(self):
        self.data['v']=99
        with self.assertRaises(ValueError):self.run_check()
    def test_missing_file_is_reported(self):
        (self.root/'src/Buttons.stories.ts').unlink()
        self.assertEqual(self.run_check()['state'],'BLOCKED')
    def test_removed_selected_entry_is_not_replaced(self):
        self.assertEqual(self.run_check(selected=['gone'])['state'],'BLOCKED')
    def test_empty_index_not_coverage(self):
        self.data['entries']={};self.assertEqual(self.run_check()['state'],'BLOCKED')
    def test_unsupported_virtual_import(self):
        self.row['importPath']='virtual:button'
        self.assertEqual(self.run_check()['state'],'BLOCKED')
    def test_unsafe_paths(self):
        for name in ('../escape','https://x/y','/tmp/a','C:/x','src\\x'):
            with self.subTest(path=name):
                self.row['importPath']=name
                self.assertEqual(self.run_check()['state'],'BLOCKED')
    def test_mismatched_ids(self):
        self.row['id']='mismatch'
        with self.assertRaises(ValueError):self.run_check()
    def test_unknown_entry_type(self):
        self.row['type']='code'
        with self.assertRaises(ValueError):self.run_check()
    def test_docs_do_not_become_components(self):
        self.row['type']='docs';self.assertEqual(self.run_check()['state'],'BLOCKED')
    def test_source_edits_update_observation_not_approval(self):
        before=self.run_check()['entries'][0]['sha256']
        (self.root/'src/Buttons.stories.ts').write_text('changed')
        after=self.run_check()
        self.assertNotEqual(before,after['entries'][0]['sha256']);self.assertFalse(after['implementation_approved'])
    def test_previous_index_shows_removed_and_added_ids(self):
        old=json.loads(json.dumps(self.data));old['entries']['old']={**self.row,'id':'old'}
        (self.root/'previous.json').write_text(json.dumps(old))
        out=self.run_check(previous='previous.json');self.assertEqual(out['delta']['removed'],['old'])
    def test_no_writes(self):
        self.run_check();before={p.relative_to(self.root):p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        k.inspect(self.root,'index.json');after={p.relative_to(self.root):p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        self.assertEqual(before,after)
    def test_tags_are_not_read_as_approval(self):
        self.row['tags']=['approved','production','autodocs']
        self.assertFalse(self.run_check()['approval_authenticated'])
    def test_duplicate_json_rejected(self):
        (self.root/'bad.json').write_text('{"v":5,"v":4,"entries":{}}')
        with self.assertRaises(ValueError):k.inspect(self.root,'bad.json')
    def test_catalogue_binding_checks_exact_example(self):
        from kit_fixture import fixture
        data,catalogue=fixture(self.root)
        self.row['importPath']='./src/kit.stories.ts'
        out=self.run_check(selected=[self.row['id']],catalogue='kit.json',item='primary',scope='src/settings')
        self.assertEqual(out['state'],'REVIEW_REQUIRED')
        self.assertFalse(out['approval_authenticated'])
    def test_catalogue_binding_rejects_unlisted_example(self):
        from kit_fixture import fixture
        fixture(self.root)
        out=self.run_check(selected=[self.row['id']],catalogue='kit.json',item='primary',scope='src/settings')
        self.assertEqual(out['state'],'BLOCKED')
    def test_binding_cannot_apply_one_item_to_many_stories(self):
        from kit_fixture import fixture
        fixture(self.root)
        self.data['entries']['second']={**self.row,'id':'second'}
        with self.assertRaises(ValueError):self.run_check(catalogue='kit.json',item='primary',scope='src')
    def test_selection_metadata_requires_catalogue(self):
        with self.assertRaises(ValueError):self.run_check(item='primary')

if __name__=='__main__':unittest.main()
