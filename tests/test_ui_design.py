"""Mechanical UI policy/triage tests; not live agent behaviour or visual approval."""
from __future__ import annotations

import importlib.util
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / 'skills/ui-design/scripts/review_ui_diff.py'
spec = importlib.util.spec_from_file_location('ui_diff_test', SCRIPT)
ui = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = ui
spec.loader.exec_module(ui)


def patch(path='src/Thing.tsx', old='const x = 1;', new='const x = 2;'):
    before, after = old.splitlines(), new.splitlines()
    return (f'diff --git a/{path} b/{path}\n--- a/{path}\n+++ b/{path}\n'
            f'@@ -1,{len(before)} +1,{len(after)} @@\n'
            + ''.join('-' + s + '\n' for s in before)
            + ''.join('+' + s + '\n' for s in after))


def categories(result):
    return {cue['category'] for f in result['files'] for cue in f['cues']}


class UiDiffTests(unittest.TestCase):
    def cue(self, text, expected, path='src/Thing.tsx'):
        result = ui.review(patch(path, new=text))
        self.assertIn(expected, categories(result))
        self.assertEqual(result['status'], 'review-required')
        self.assertFalse(result['design_accepted'])
        return result

    def test_empty_is_not_approval(self):
        out = ui.review('')
        self.assertEqual(out['status'], 'no-changes')
        self.assertEqual(out['policy_decision'], 'not-evaluated')
        self.assertFalse(out['implementation_authorized'])

    def test_behavior_only_patch_is_not_design_signoff(self):
        out = ui.review(patch('src/save.ts', 'return oldValue;', 'return nextValue;'))
        self.assertEqual(out['status'], 'no-patterns-detected')
        self.assertFalse(out['design_accepted'])

    def test_stylesheet_new_declaration(self):
        self.cue('.button { color: red; }', 'stylesheet-change', 'src/style.scss')

    def test_stylesheet_removal_is_not_silent(self):
        out = ui.review(patch('src/style.css', '.x { padding: 2px; }', ''))
        self.assertIn('stylesheet-change', categories(out))

    def test_inline_html_and_jsx(self):
        for text in ('<button style="color:red">Save</button>', '<button style={{color: "red"}}>Save</button>'):
            with self.subTest(text=text):
                self.cue(text, 'inline-or-runtime-style')

    def test_runtime_style_mutation(self):
        for text in ('el.style.opacity = 0;', 'sheet.insertRule(rule);', 'el.setAttribute("style", "color:red");', 'document.adoptedStyleSheets = sheets;'):
            with self.subTest(text=text):
                self.cue(text, 'inline-or-runtime-style')

    def test_style_tags_and_injection(self):
        for text in ('<style>.x { color: red }</style>', 'document.createElement("style");'):
            self.cue(text, 'style-injection-or-css-in-js')

    def test_css_in_js_and_native_styles(self):
        for text in ('const X = styled.button`color: red;`;', 'const x = css`display: flex;`;', 'StyleSheet.create({root: {}});'):
            self.cue(text, 'style-injection-or-css-in-js')

    def test_utility_class_combination(self):
        self.cue('<div className="flex gap-4 rounded-xl shadow-lg" />', 'classes-or-utility-composition')

    def test_class_helpers_and_classlist(self):
        for text in ('const x = clsx("a", "b");', 'el.classList.add("large");'):
            self.cue(text, 'classes-or-utility-composition')

    def test_visual_component_props(self):
        for text in ('<Button variant="danger" />', '<Box sx={{padding: 3}}/>', '<Panel gap={4} />'):
            self.cue(text, 'visual-prop-or-token')

    def test_new_style_dependency(self):
        self.cue('"@mui/material": "^5.0.0"', 'style-import-or-visual-library', 'package.json')

    def test_style_import(self):
        self.cue('import "./screen.css";', 'style-import-or-visual-library')

    def test_svg_canvas_and_pixi(self):
        for text in ('<path fill="red" d="M0 0"/>', 'ctx.fillStyle = "red";', 'sprite.setTint(0xff0000);'):
            self.cue(text, 'rendered-or-native-appearance')

    def test_unity_and_native_props(self):
        for text in ('material.SetColor("_Color", Color.red);', 'android:background="@color/newColor"', 'Text("Save").foregroundStyle(.red)'):
            self.cue(text, 'rendered-or-native-appearance')

    def test_unity_asset_flagged(self):
        self.cue('m_Name: NewScreen', 'visual-asset-or-renderer-file', 'Assets/NewScreen.prefab')

    def test_plain_semantic_markup_has_no_styling_violation(self):
        out = ui.review(patch(new='<label htmlFor="enabled">Enabled</label>\n<input id="enabled" type="checkbox" />\n<button type="submit">Save</button>'))
        self.assertEqual(categories(out), {'markup-or-control-structure'})
        self.assertEqual(out['policy_decision'], 'not-evaluated')

    def test_functional_test_attribute_is_not_css(self):
        out = ui.review(patch(new='<button data-testid="save" onClick={save}>Save</button>'))
        self.assertEqual(categories(out), {'markup-or-control-structure'})

    def test_approved_component_still_needs_context(self):
        self.cue('<PrimaryButton onClick={save}>Save</PrimaryButton>', 'markup-or-control-structure')

    def test_comments_or_examples_are_not_exempt_or_auto_violations(self):
        out = self.cue('// Example: el.style.color = "red";', 'inline-or-runtime-style', 'docs/example.md')
        self.assertEqual(out['policy_decision'], 'not-evaluated')

    def test_report_path_is_not_blanket_exemption(self):
        self.cue('<div style="color:red">Prototype</div>', 'inline-or-runtime-style', 'reports/app.html')

    def test_removed_inline_style_is_reviewed(self):
        out = ui.review(patch(old='<div style={{color:"red"}} />', new='<div />'))
        cue = next(c for c in out['files'][0]['cues'] if c['category']=='inline-or-runtime-style')
        self.assertEqual(cue['removed_lines'], [1]); self.assertEqual(cue['added_lines'], [])

    def test_context_lines_do_not_become_new_style_findings(self):
        text = '--- a/src/a.tsx\n+++ b/src/a.tsx\n@@ -4,3 +4,3 @@\n <div style={{color:"red"}}>\n-oldValue\n+newValue\n </div>\n'
        out = ui.review(text)
        self.assertEqual(categories(out), set())
        self.assertEqual(out['files'][0]['changed_lines'], 2)

    def test_new_file_dev_null(self):
        text = '--- /dev/null\n+++ b/src/a.css\n@@ -0,0 +1 @@\n+.a {display:flex;}\n'
        out = ui.review(text)
        self.assertEqual(out['files'][0]['path'], 'src/a.css')
        self.assertIn('stylesheet-change', categories(out))

    def test_deleted_file_dev_null(self):
        text = '--- a/src/a.css\n+++ /dev/null\n@@ -1 +0,0 @@\n-.a {}\n'
        out = ui.review(text)
        self.assertEqual(out['files'][0]['path'], 'src/a.css')
        self.assertIn('stylesheet-change', categories(out))

    def test_binary_files_require_manual_review(self):
        out = ui.review('diff --git a/icon.png b/icon.png\nindex a..b 100644\nBinary files a/icon.png and b/icon.png differ\n')
        self.assertIn('nontext-or-file-operation-needs-review', categories(out))

    def test_rename_only_requires_review(self):
        out = ui.review('diff --git a/old.css b/new.txt\nsimilarity index 100%\nrename from old.css\nrename to new.txt\n')
        self.assertEqual(out['status'], 'review-required')

    def test_multiple_files_and_crlf(self):
        out = ui.review((patch('src/a.ts')+patch('src/b.css', new='.a{}')).replace('\n','\r\n'))
        self.assertEqual(len(out['files']), 2)
        self.assertEqual(out['files'][1]['path'], 'src/b.css')

    def test_quoted_space_and_unicode_paths(self):
        for path in ('src/my button.tsx', 'src/café.tsx'):
            text = f'--- {json.dumps("a/"+path)}\n+++ {json.dumps("b/"+path)}\n@@ -1 +1 @@\n-old\n+new\n'
            self.assertEqual(ui.review(text)['files'][0]['path'], path)

    def test_no_source_lines_in_result(self):
        text = 'el.style.color = "sensitive-example-token";'
        out = ui.review(patch(new=text))
        self.assertNotIn('sensitive-example-token', json.dumps(out))

    def test_patched_paths_are_never_read(self):
        with mock.patch.object(Path, 'open', side_effect=AssertionError('must not read files')):
            self.assertTrue(ui.review(patch(new='<button/>'))['files'])

    def test_malformed_truncated_and_extra_hunk_lines_fail(self):
        values = ('nonsense', '+++ b/file\n', '--- a/file\n', '--- a/file\n+++ b/file\n@@ -1,2 +1,2 @@\n-old\n+new\n', patch()+'+extra\n')
        for text in values:
            with self.subTest(text=text), self.assertRaises(ValueError):
                ui.review(text)

    def test_unsupported_combined_binary_encoding_and_nul_fail(self):
        for text in ('diff --cc src/a\n', 'diff --git a/a b/a\nGIT binary patch\n', '\x00', '--- "a/\\377"\n+++ b/a\n'):
            with self.subTest(text=text), self.assertRaises(ValueError):
                ui.review(text)

    def test_unsafe_paths_fail_without_reads(self):
        for path in ('../../secret', '/absolute', 'C:/secret', 'a/../secret'):
            with self.subTest(path=path), self.assertRaises(ValueError):
                ui.review(f'--- {path}\n+++ {path}\n@@ -1 +1 @@\n-a\n+b\n')

    def test_size_limit(self):
        with self.assertRaises(ValueError):
            ui.review('x'*(ui.MAX_BYTES+1))

    def test_no_newline_marker(self):
        out = ui.review(patch()+'\\ No newline at end of file\n')
        self.assertEqual(out['status'], 'no-patterns-detected')

    def test_cli_exit_codes_and_no_writes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for text,code,status in (('',0,'no-changes'),(patch(),0,'no-patterns-detected'),(patch(new='<p style="color:red"/>'),1,'review-required'),('bad',2,'invalid-input')):
                run = subprocess.run([sys.executable,str(SCRIPT)],input=text,text=True,capture_output=True,cwd=root)
                self.assertEqual(run.returncode,code,run.stderr)
                self.assertEqual(json.loads(run.stdout)['status'],status)
                self.assertEqual(list(root.iterdir()),[])

    def test_existing_file_is_read_not_modified(self):
        with tempfile.TemporaryDirectory() as tmp:
            file = Path(tmp)/'input.diff'; file.write_bytes(b'\xef\xbb\xbf'+patch().encode())
            before = file.read_bytes()
            text = ui.read_input(file,io.StringIO('ignored'))
            self.assertEqual(ui.review(text)['status'],'no-patterns-detected')
            self.assertEqual(file.read_bytes(),before)

    def test_linked_input_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp); source=root/'a'; source.write_text(patch()); link=root/'b'
            try: link.symlink_to(source)
            except OSError: self.skipTest('Symlink unavailable in this environment')
            with self.assertRaises(ValueError): ui.read_input(link,io.StringIO())


class UiPolicyContractTests(unittest.TestCase):
    def test_eighth_local_skill_registered_once(self):
        data=json.loads((ROOT/'.claude-plugin/plugin.json').read_text())
        self.assertEqual(len(data['skills']),8)
        self.assertEqual(data['skills'].count('./skills/ui-design'),1)

    def test_strict_modes_and_no_kit_invention(self):
        text=(ROOT/'skills/rule-maker/rules/design.md').read_text()
        for name in ('behaviour-only','approved-kit','design-authoring','legacy','blocked/unselected','preview'):
            self.assertIn(name,text)
        self.assertIn('no plain-HTML fallback',text)

    def test_ordinary_loading_covers_markup_not_only_css(self):
        text=(ROOT/'skills/rule-maker/rules/START.md').read_text()
        self.assertIn('including markup or interaction-only',text)
        self.assertIn('local `ui-design`',text)
        self.assertIn('Backend-only',text)

    def test_workflow_routes_before_substantive_plan(self):
        text=(ROOT/'skills/workflow/SKILL.md').read_text()
        self.assertLess(text.index('`ui-design`'),text.index('## 4.'))
        self.assertIn('preview/release limits',text)

    def test_handoffs_review_status_doctor_and_setup_connected(self):
        for path in ('skills/resume-task/SKILL.md','skills/task-status/SKILL.md','skills/plan-review/SKILL.md','skills/workflow-doctor/SKILL.md','skills/rule-maker/SKILL.md','skills/workflow/AUDIT.md','skills/workflow/templates/PROJECT-ROUTING.md'):
            text=(ROOT/path).read_text().lower()
            self.assertTrue('ui-design' in text or 'design acceptance' in text,path)

    def test_report_exemption_is_narrow(self):
        text=(ROOT/'skills/ui-design/CONTRACT.md').read_text()
        self.assertIn('Preview and report boundary',text)
        self.assertIn('codebase-map',text)
        self.assertIn('only routine HTML/CSS generation exception',text)

    def test_no_new_record_or_ui_tool_by_default(self):
        text=(ROOT/'skills/ui-design/SKILL.md').read_text()
        self.assertIn('No duplicate component inventory',text)
        self.assertIn('not a designer',text)
        self.assertIn('Backend-only',text)

    def test_verification_explains_no_pass_claim(self):
        text=(ROOT/'skills/ui-design/VERIFY.md').read_text()
        self.assertIn('not a parser',text)
        self.assertIn('no-patterns', (ROOT/'skills/ui-design/scripts/review_ui_diff.py').read_text())
        self.assertIn('exit 0',text)
        self.assertIn('untracked',text)

    def test_no_new_external_provider(self):
        data=json.loads((ROOT/'skills/workflow/specialists.json').read_text())
        self.assertEqual(len(data['skills']),27)
        self.assertNotIn('ui-design',data['skills'])
        self.assertNotIn('diagram-design',data['skills'])

    def test_live_cases_are_not_claimed_results(self):
        data=json.loads((ROOT/'tests/behavioral/ui-design.json').read_text())
        self.assertEqual(data['candidate_version'],json.loads((ROOT/'.claude-plugin/plugin.json').read_text())['version'])
        self.assertGreaterEqual(len(data['cases']),20)
        self.assertEqual(len({c['id'] for c in data['cases']}),len(data['cases']))
        for case in data['cases']:
            self.assertEqual(case['result'],'NOT_RUN')
            self.assertTrue(case['prompt'] and case['preparation'] and case['expected'])


if __name__=='__main__':
    unittest.main()
