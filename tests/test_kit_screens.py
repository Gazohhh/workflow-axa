"""Kit screens: markup copied from a saved kit snapshot, checked and shown in sandboxed frames."""
from __future__ import annotations
import copy
import importlib.util
import json
import re
import shutil
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('kit_report_test', ROOT/'skills/codebase-map/scripts/render_report.py')
r = importlib.util.module_from_spec(spec); spec.loader.exec_module(r)
snap_spec = importlib.util.spec_from_file_location('kit_snapshot_test', ROOT/'skills/codebase-map/scripts/kit_snapshot.py')
ks = importlib.util.module_from_spec(snap_spec); snap_spec.loader.exec_module(ks)

KIT_BODY = ('<main class="page"><h1 class="title">Kit</h1><button class="button primary">Save</button>'
            '<div class="card" style="width: 200px;"><span class="label">Name</span></div>'
            '<ion-button class="ion-color-primary hydrated"><template shadowrootmode="open">'
            '<style data-kit-shadow-ref="k1"></style><button class="button-native"><slot></slot></button>'
            '</template>Go</ion-button><img src="__KIT_ASSET_0__" alt=""></main>')


def snapshot(typekit=True) -> str:
    result = {'html_attrs': ' class="hydrated" lang="en"', 'body_attrs': ' class="kit"',
              'css': '.button{color:red} .card{border:1px solid}', 'shadow': {'k1': ':host{display:inline-block}'},
              'body': KIT_BODY, 'asset_values': {'__KIT_ASSET_0__': 'data:image/png;base64,AAAA'}}
    return ks.document(result, ['https://use.typekit.net/abc1234.css'] if typekit else [])


class KitScreenTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        shutil.copytree(ROOT/'skills/codebase-map/examples', self.root, dirs_exist_ok=True)
        self.data = r.load_json(self.root/'review.json')
        self.data.update(state='draft', open_decisions=['Synthetic sample'])
        ui = copy.deepcopy(json.loads((ROOT/'skills/codebase-map/examples/ui-review/review-r2.json').read_text())['ui_review'])
        self.data['sources'] += [{'id': 'UIREF', 'role': 'design-example', 'path': 'ui-review/README.md'},
                                 {'id': 'KIT', 'role': 'kit-snapshot', 'path': 'kit.html'},
                                 {'id': 'SCR', 'role': 'kit-screen', 'path': 'screen.html'}]
        (self.root/'kit.html').write_text(snapshot(), encoding='utf-8')
        self.write_screen('<main class="page"><h1 class="title">Orders</h1><button class="button primary">Add order</button></main>')
        for s in ui['screens']:
            for key in ('content', 'capture', 'markers'):
                s.pop(key, None)
            s.update(representation='kit', kit_snapshot='KIT', kit_markup='SCR')
            s['sources'] = s['sources'] + ['KIT', 'SCR']
        self.ui = ui
        self.data['ui_review'] = ui
        self.input = self.root/'input.json'

    def write_screen(self, markup):
        (self.root/'screen.html').write_text(markup, encoding='utf-8')

    def render(self):
        self.input.write_text(json.dumps(self.data), encoding='utf-8')
        return r.render(self.data, self.root, self.input)

    def test_renders_frames_with_one_copy_of_kit_styles(self):
        html = self.render()
        self.assertIn('id="ui-kit-data"', html)
        self.assertEqual(html.count('.button{color:red}'), 1)
        self.assertIn('data-kit-screen=', html)
        self.assertIn('sandbox=""', html)
        self.assertIn('Kit preview · real kit markup and CSS, fake data', html)
        self.assertNotIn('Sketch · not a screenshot', html)

    def test_report_policy_allows_only_inlined_fonts_and_typekit(self):
        html = self.render()
        policy = re.search(r'Content-Security-Policy" content="([^"]+)"', html).group(1)
        self.assertIn('font-src data: https://use.typekit.net;', policy)
        self.assertIn("connect-src 'none'", policy)
        (self.root/'kit.html').write_text(snapshot(typekit=False), encoding='utf-8')
        policy = re.search(r'Content-Security-Policy" content="([^"]+)"', self.render()).group(1)
        self.assertIn('font-src data:;', policy)
        self.assertNotIn('typekit', policy)

    def test_unknown_class_is_blocked_and_named(self):
        self.write_screen('<main class="page"><button class="button shiny">Add</button></main>')
        with self.assertRaisesRegex(ValueError, r'class "shiny" on <button> is not in the kit snapshot'):
            self.render()

    def test_unknown_tag_inline_style_and_new_css_are_blocked(self):
        self.write_screen('<section class="page"><div class="card" style="width: 999px;">x</div></section>'
                          '<style>.page{color:blue}</style>')
        with self.assertRaises(ValueError) as caught:
            self.render()
        message = str(caught.exception)
        self.assertIn('tag <section>', message)
        self.assertIn('inline style "width: 999px;"', message)
        self.assertIn('never add CSS', message)
        self.assertIn('Is there an existing element I should mimic?', message)

    def test_copied_kit_parts_with_shadow_roots_styles_and_images_pass(self):
        self.write_screen('<main class="page"><div class="card" style="width: 200px;"><span class="label">Customer</span></div>'
                          '<ion-button class="ion-color-primary hydrated"><template shadowrootmode="open">'
                          '<style data-kit-shadow-ref="k1"></style><button class="button-native"><slot></slot></button>'
                          '</template>Send</ion-button><img src="__KIT_ASSET_0__" alt=""></main>')
        html = self.render()
        self.assertIn('Send', html)

    def test_scripts_handlers_links_and_unknown_shadow_refs_are_blocked(self):
        for markup, expected in [('<main class="page" onclick="x()">a</main>', 'onclick'),
                                 ('<main class="page"><a href="https://example.com">a</a></main>', 'href'),
                                 ('<main class="page"><script>1</script></main>', '<script>'),
                                 ('<main class="page"><style data-kit-shadow-ref="k9"></style></main>', 'k9')]:
            self.write_screen(markup)
            with self.assertRaisesRegex(ValueError, re.escape(expected)):
                self.render()

    def test_kit_screen_needs_snapshot_written_by_the_capture_script(self):
        (self.root/'kit.html').write_text('<!doctype html><html><head></head><body><main class="page"></main></body></html>', encoding='utf-8')
        with self.assertRaisesRegex(ValueError, 'written by kit_snapshot.py'):
            self.render()

    def test_sketch_next_to_kit_screens_must_say_why(self):
        sketch = self.ui['screens'][0]
        for key in ('kit_snapshot', 'kit_markup'):
            sketch.pop(key)
        sketch['sources'] = [x for x in sketch['sources'] if x not in ('KIT', 'SCR')]
        sketch.update(representation='schematic', content=[{'kind': 'heading', 'label': 'Menu'}])
        with self.assertRaisesRegex(ValueError, 'sketch_reason'):
            self.render()
        sketch['sketch_reason'] = 'The kit has no example of the sidebar.'
        html = self.render()
        self.assertIn('Why a sketch:', html)
        self.assertIn('The kit has no example of the sidebar.', html)

    def test_classes_defined_by_the_kit_css_are_existing_styles(self):
        self.write_screen('<main class="page"><span class="card label">x</span></main>')
        self.render()
        (self.root/'kit.html').write_text(snapshot().replace('.card{border:1px solid}', '.card{border:1px solid} .fa-headset{content:"x"}'), encoding='utf-8')
        self.write_screen('<main class="page"><span class="fa-headset"></span></main>')
        self.render()

    def test_snapshot_width_sets_the_frame_width(self):
        (self.root/'kit.html').write_text(snapshot().replace('content="1">', 'content="1"><meta name="workflow-kit-width" content="390">'), encoding='utf-8')
        html = self.render()
        widths = set(re.findall(r'data-kit-screen="[^"]+" title="[^"]*" width="(\d+)"', html))
        self.assertEqual(widths, {'390'})

    def test_copied_web_component_keeps_its_shadow_style(self):
        self.write_screen('<main class="page"><ion-button class="ion-color-primary hydrated"><template shadowrootmode="open">'
                          '<button class="button-native"><slot></slot></button></template>Go</ion-button></main>')
        with self.assertRaisesRegex(ValueError, r'shadow root of <ion-button> lost its kit style'):
            self.render()

    def test_snapshot_never_closes_its_own_style_element(self):
        text = ks.document({'html_attrs': '', 'body_attrs': '', 'css': 'a{content:"</style><script>"}',
                            'shadow': {}, 'body': ''}, [])
        self.assertNotIn('</style><script>', text)


if __name__ == '__main__':
    unittest.main()
