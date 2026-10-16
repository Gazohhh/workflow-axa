from __future__ import annotations
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from tools.visual_regression import compare, load_capture, new_output, sha

HAS_PIL = importlib.util.find_spec('PIL') is not None

@unittest.skipUnless(HAS_PIL, 'Pillow unavailable: optional pixel-comparison tests not run.')
class VisualRegressionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def fixture(self, name, color='white', size=(12, 8), environment=None):
        from PIL import Image
        path = self.root/name
        path.mkdir()
        Image.new('RGB', size, color).save(path/'view.png')
        data = {'schema_version':1,'kind':'visual-capture','environment':environment or {'browser':'test'},
                'cases':[{'name':'view','file':'view.png','width':size[0],'height':size[1],'sha256':sha(path/'view.png')}]}
        (path/'manifest.json').write_text(json.dumps(data))
        return path

    def test_identical_pixels_pass(self):
        code, result=compare(self.fixture('base'),self.fixture('next'),self.root/'result')
        self.assertEqual(code,0)
        self.assertEqual(result['checks'][0]['changed_pixels'],0)

    def test_changed_pixels_fail_and_emit_difference(self):
        code, result=compare(self.fixture('base'),self.fixture('next','black'),self.root/'result')
        self.assertEqual(code,1)
        self.assertEqual(result['checks'][0]['changed_pixels'],96)
        self.assertTrue((self.root/'result/difference-1.png').is_file())

    def test_one_pixel_change_fails(self):
        from PIL import Image
        base, current=self.fixture('base'),self.fixture('next')
        with Image.open(current/'view.png') as im:
            im.putpixel((1,1),(254,255,255)); im.save(current/'view.png')
        data=json.loads((current/'manifest.json').read_text());data['cases'][0]['sha256']=sha(current/'view.png')
        (current/'manifest.json').write_text(json.dumps(data))
        code,result=compare(base,current,self.root/'result')
        self.assertEqual(code,1)
        self.assertEqual(result['checks'][0]['changed_pixels'],1)

    def test_environment_mismatch_is_not_verified(self):
        code,result=compare(self.fixture('base'),self.fixture('next',environment={'browser':'other'}),self.root/'result')
        self.assertEqual(code,2)
        self.assertEqual(result['status'],'NOT_VERIFIED')
        self.assertEqual(result['checks'],[])

    def test_size_change_fails(self):
        code,result=compare(self.fixture('base'),self.fixture('next',size=(13,8)),self.root/'result')
        self.assertEqual(code,1)
        self.assertEqual(result['checks'][0]['reason'],'Image dimensions changed.')

    def test_inputs_never_rewritten(self):
        base,current=self.fixture('base'),self.fixture('next','black')
        before={str(p):sha(p) for parent in (base,current) for p in parent.iterdir()}
        compare(base,current,self.root/'result')
        self.assertEqual(before,{str(p):sha(p) for parent in (base,current) for p in parent.iterdir()})

    def test_existing_output_refused(self):
        base,current=self.fixture('base'),self.fixture('next')
        with self.assertRaises(ValueError):compare(base,current,base)

    def test_output_inside_input_refused(self):
        base,current=self.fixture('base'),self.fixture('next')
        with self.assertRaises(ValueError):compare(base,current,base/'new')
        self.assertFalse((base/'new').exists())

    def test_missing_image_refused(self):
        base=self.fixture('base');(base/'view.png').unlink()
        with self.assertRaisesRegex(ValueError,'Missing'):load_capture(base)

    def test_modified_image_hash_refused(self):
        base=self.fixture('base');(base/'view.png').write_bytes(b'not a png')
        with self.assertRaisesRegex(ValueError,'hash'):load_capture(base)

    def test_unsafe_manifest_path_refused(self):
        base=self.fixture('base');data=json.loads((base/'manifest.json').read_text())
        data['cases'][0]['file']='../elsewhere.png';(base/'manifest.json').write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError,'basename'):load_capture(base)

    def test_case_set_mismatch_is_not_verified(self):
        base,current=self.fixture('base'),self.fixture('next')
        data=json.loads((current/'manifest.json').read_text());data['cases'][0]['name']='different'
        (current/'manifest.json').write_text(json.dumps(data))
        code,result=compare(base,current,self.root/'result')
        self.assertEqual(code,2)
        self.assertEqual(result['status'],'NOT_VERIFIED')

    def test_missing_baseline_does_not_create_one(self):
        current=self.fixture('next')
        with self.assertRaises(FileNotFoundError):compare(self.root/'missing',current,self.root/'result')
        self.assertFalse((self.root/'missing').exists())
        self.assertFalse((self.root/'result').exists())

    def test_nonobject_manifest_rejected(self):
        base=self.fixture('base');(base/'manifest.json').write_text('[]')
        with self.assertRaisesRegex(ValueError,'Unsupported'):load_capture(base)

    def test_duplicate_case_is_rejected(self):
        base=self.fixture('base');data=json.loads((base/'manifest.json').read_text());data['cases']*=2
        (base/'manifest.json').write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError,'Duplicate'):load_capture(base)

    def test_false_dimensions_are_rejected(self):
        base,current=self.fixture('base'),self.fixture('next')
        data=json.loads((current/'manifest.json').read_text());data['cases'][0]['width']=20
        (current/'manifest.json').write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError,'dimensions'):compare(base,current,self.root/'result')

if __name__=='__main__':unittest.main()
