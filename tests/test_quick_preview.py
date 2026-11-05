"""Source-backed UI preview tests; not claims about live framework component rendering."""
from __future__ import annotations

import copy
import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/'skills/codebase-map/scripts/render_report.py'
spec=importlib.util.spec_from_file_location('quick_preview_report_tests', SCRIPT)
r=importlib.util.module_from_spec(spec)
spec.loader.exec_module(r)


class QuickPreviewTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        shutil.copytree(ROOT/'skills/codebase-map/examples',self.root,dirs_exist_ok=True)
        self.data=r.load_json(self.root/'review.json')
        self.data.update(state='draft',open_decisions=['Test only; not an approval'])
        self.ui=copy.deepcopy(json.loads((ROOT/'skills/codebase-map/examples/ui-review/review-r2.json').read_text())['ui_review'])
        self.data['ui_review']=self.ui
        self.html=self.root/'fixture.html'
        self.css=self.root/'fixture.css'
        self.html.write_text('<div class="other">Ignore</div><section id="card" class="card">'
                             '<h2 class="title">Existing title</h2>'
                             '<button class="primary" onclick="fetch(\'https://bad\')">Save</button>'
                             '<img src="https://bad.test/x.png"><script>fetch("https://bad")</script>'
                             '<a href="https://bad.test">External</a></section>',encoding='utf-8')
        self.css.write_text('.card{padding:12px;background:#eee;} .primary{background:#222;color:white;}',encoding='utf-8')
        self.data['sources'] += [
            {'id':'UIREF','role':'design-example','path':'ui-review/README.md'},
            {'id':'FRAGMENT','role':'code','path':'fixture.html'},
            {'id':'STYLE','role':'code','path':'fixture.css'},
        ]
        self.ui['quick_previews']=[{'id':'card','title':'Existing card','html_source':'FRAGMENT',
                                  'selector':'section#card','css_sources':['STYLE'],
                                  'note':'Static source-backed preview; not the proposed app.'}]
        self.input=self.root/'input.json'

    def render(self):
        self.input.write_text(json.dumps(self.data),encoding='utf-8')
        return r.render(self.data,self.root,self.input)

    def test_preview_embeds_current_classes_and_css_in_inert_iframe(self):
        output=self.render()
        self.assertIn('Real-style component samples',output)
        self.assertIn('sandbox=""',output)
        self.assertIn('srcdoc="',output)
        self.assertIn('Existing title',output)
        self.assertIn('.card{padding:12px',output)
        self.assertIn('frame-src \'self\' about:',output)
        self.assertIn('Expand full-size sample',output)
        self.assertNotIn('onclick=',output)
        self.assertNotIn('https://bad',output)
        self.assertNotIn('<script>fetch',output)
        self.assertIn('No Angular/React runtime',output)
        self.assertLess(len(output.encode()), r.MAX_BYTES)

    def test_unavailable_selector_fails_instead_of_mocking(self):
        self.ui['quick_previews'][0]['selector']='.missing'
        with self.assertRaisesRegex(ValueError,'cannot find a complete element'):
            self.render()

    def test_uncompiled_scss_is_not_claimed_as_rendered_css(self):
        self.data['sources'][-1]['path']='fixture.scss'
        (self.root/'fixture.scss').write_text('$a:red;.card{color:$a;}',encoding='utf-8')
        with self.assertRaisesRegex(ValueError,'compiled .css'):
            self.render()

    def test_no_freeform_source_markup_in_projection(self):
        self.ui['quick_previews'][0]['markup']='<script>bad()</script>'
        with self.assertRaisesRegex(ValueError,'Quick preview needs id'):
            self.render()

    def test_stale_sources_still_participate_in_report_fingerprint(self):
        self.render()
        self.assertEqual(len([s for s in self.data['sources'] if s['id'] in ('FRAGMENT','STYLE')]),2)
        old=self.css.read_text()
        self.css.write_text(old+'\n.card{padding:16px}',encoding='utf-8')
        updated=self.render()
        self.assertIn('padding:16px',updated)
        self.assertIn('fixture.css',updated)

    def test_no_quick_preview_leaves_legacy_screen_diagram(self):
        self.ui.pop('quick_previews')
        output=self.render()
        self.assertNotIn('ui-quick-gallery',output.split('<body>',1)[1].split('<script type="application/json"',1)[0])
        self.assertIn('panel-ui-preview',output)
        self.assertIn("frame-src 'none'",output)


if __name__=='__main__':
    unittest.main()
