"""Design changes made without AI are detected from Git, never auto-approved."""
from __future__ import annotations
import importlib.util
import json
import subprocess
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/'skills/ui-design/scripts/design_drift.py'
spec=importlib.util.spec_from_file_location('design_drift_tests',SCRIPT)
d=importlib.util.module_from_spec(spec);spec.loader.exec_module(d)


class DriftTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)/'repo with spaces'
        self.root.mkdir()
        self.git('init','-q')
        self.write('DESIGN.md','# Design\n')
        self.write('src/global.scss','--main-pad: 24px;\n')
        self.write('src/app/product.component.html','<div class="card">Old</div>')
        self.git('add','.')
        self.git('-c','user.name=Test','-c','user.email=example@invalid.test','commit','-qm','initial')
        self.base=self.git('rev-parse','HEAD').strip()

    def git(self,*args):
        result=subprocess.run(['git','-C',str(self.root),*args],capture_output=True,text=True,check=True)
        return result.stdout

    def write(self,path,text):
        p=self.root/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(text)

    def test_manual_css_and_html_changes_detected_since_baseline(self):
        self.write('DESIGN.md',f'<!-- workflow-axa-design-baseline: {self.base} -->\n')
        self.write('src/global.scss','--main-pad: 32px;\n')
        self.write('src/app/product.component.html','<div class="card">New</div>')
        output=d.scan(self.root)
        self.assertEqual(output['status'],'needs-reconciliation')
        self.assertTrue(output['shared_style_changed'])
        self.assertEqual({x['path'] for x in output['changed_ui_files']},
                         {'src/global.scss','src/app/product.component.html'})
        self.assertEqual(output['approval'],'Not determined. Git changes never grant design approval.')

    def test_missing_baseline_does_not_claim_clean_design(self):
        output=d.scan(self.root)
        self.assertEqual(output['status'],'baseline-unknown')
        self.assertIsNone(output['baseline'])

    def test_committed_design_change_and_untracked_component_detected(self):
        self.write('src/global.scss','--main-pad: 40px;\n')
        self.git('add','.')
        self.git('-c','user.name=Test','-c','user.email=example@invalid.test','commit','-qm','designer edit')
        self.write('src/app/new.component.tsx','export const New = () => null;')
        output=d.scan(self.root,self.base)
        self.assertEqual(len(output['changed_ui_files']),2)
        self.assertTrue(any(x['untracked'] for x in output['changed_ui_files']))

    def test_explicit_current_baseline_no_changes(self):
        output=d.scan(self.root,self.base)
        self.assertEqual(output['status'],'no-drift-found')

    def test_invalid_baseline_cannot_silently_fall_back(self):
        output=d.scan(self.root,'a'*40)
        self.assertEqual(output['status'],'baseline-unknown')


if __name__=='__main__':
    unittest.main()
