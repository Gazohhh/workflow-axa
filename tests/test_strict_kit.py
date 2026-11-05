"""Strict selection and provenance regressions, not live model or designer signoff."""
import copy
import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from kit_fixture import ROOT, fixture

spec=importlib.util.spec_from_file_location('strict_renderer',ROOT/'skills/codebase-map/scripts/render_report.py')
r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)


class StrictKitTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name);self.data,self.kit=fixture(self.root)
        self.ui=self.data['ui_review'];self.screen=self.ui['screens'][0]
    def render(self):
        p=self.root/'input.json';p.write_text(json.dumps(self.data))
        return r.render(self.data,self.root,p)
    def savekit(self):
        (self.root/'kit.json').write_text(json.dumps(self.kit))
    def test_full_report_shows_exact_selected_elements(self):
        out=self.render()
        for text in ('Exactly which kit elements are used','Save action','Page composition','primary','default / normal','What changes','Technical evidence and task details'):
            self.assertIn(text,out)
        self.assertIn('do not authenticate consent',out)
    def test_render_keeps_base_theme_and_viewer_verbatim(self):
        out=self.render()
        for name in ('report.css','report.js'):
            self.assertIn((ROOT/'skills/codebase-map/assets'/name).read_text(),out)
    def test_manifest_covers_transitive_sources(self):
        out=self.root/'report.html';out.write_text(self.render())
        self.assertEqual(r.check_report(out,self.root),[])
        (self.root/'src/Button.tsx').write_text('changed')
        self.assertIn('CHANGED: src/Button.tsx',r.check_report(out,self.root))
    def test_deleted_component_blocks_new_render_but_not_old_snapshot(self):
        out=self.render();p=self.root/'old.html';p.write_text(out)
        (self.root/'src/Button.tsx').unlink()
        with self.assertRaisesRegex(ValueError, 'missing or unreadable'):self.render()
        self.assertEqual(p.read_text(),out)
        self.assertTrue(r.check_report(p,self.root))
    def test_missing_binding_is_not_approved_from_capture(self):
        self.ui.pop('kit_binding')
        for s in self.ui['screens']:s.pop('elements');s.pop('capture_context')
        with self.assertRaisesRegex(ValueError,'Legacy approved-kit review needs its kit binding'):self.render()
    def test_legacy_plain_mode_cannot_be_approval_ready(self):
        self.ui['mode']='functionality-only'
        with self.assertRaisesRegex(ValueError,'current mode'):self.render()
    def test_legacy_design_authoring_is_not_an_escape(self):
        self.ui['mode']='design-authoring'
        with self.assertRaisesRegex(ValueError,'current mode'):self.render()
    def test_current_reuse_modes_can_be_approval_ready_without_a_kit_binding(self):
        # D14: existing classes (kit or code) are allowed; a labelled sketch or capture may show the screens.
        self.ui.pop('kit_binding')
        for s in self.ui['screens']:s.pop('elements');s.pop('capture_context')
        for mode in ('plain-by-instruction','behaviour-only'):
            self.ui['mode']=mode
            with self.subTest(mode=mode):self.assertIn('ui-review',self.render())
    def reuse(self):
        self.ui.pop('kit_binding',None);self.ui['mode']='reuse';self.screen['state']='proposed'
        for s in self.ui['screens']:s.pop('capture_context',None);s['elements']=[
            {'id':'E1','source':'STORY','locator':'src/kit.stories.ts:3','tag':'div','classes':['sm-chip','info-chip'],'context':'inside div.dashboard-info-line-chip','changes':'Text "Top"'}]
    def test_reuse_mode_lists_the_copied_elements(self):
        # Retro: ui-design asks for the reused elements per screen; reports had nowhere to put them.
        self.reuse();out=self.render()
        for text in ('Existing elements this screen copies','&lt;div class=&quot;sm-chip info-chip&quot;&gt;','src/kit.stories.ts:3','Screenshot · copied elements listed below','Context: inside div.dashboard-info-line-chip'):
            self.assertIn(text,out)
    def test_reused_framework_names_are_preserved_as_inert_references(self):
        for tag in ('SwatchTile', 'Text', 'Form.Group', 'animated.div'):
            with self.subTest(tag=tag):
                self.reuse()
                element=self.screen['elements'][0]
                element.update(tag=tag,classes=[],context='Existing framework component in its source wrapper')
                (self.root/'src/kit.stories.ts').write_text(f'export const Example = () => <{tag} />;')
                out=self.render()
                self.assertIn(f'&lt;{tag}&gt;',out)
                self.assertNotIn(f'<{tag}>',out)
    def test_reused_framework_reference_rejects_expressions_and_markup(self):
        for tag in ('Form..Group', 'Button()', '<Button>', 'Button onClick=run', 'Button[0]'):
            with self.subTest(tag=tag):
                self.reuse();self.screen['elements'][0]['tag']=tag
                with self.assertRaisesRegex(ValueError,'plain tag'):self.render()
    def test_reused_element_needs_its_context(self):
        # Round-4 retro: the copied pill lost its look because its style came from the parent wrapper.
        self.reuse();self.screen['elements'][0].pop('context')
        with self.assertRaisesRegex(ValueError,'context'):self.render()
    def test_reuse_mode_proposed_screen_needs_its_elements(self):
        self.reuse();self.screen.pop('elements')
        with self.assertRaisesRegex(ValueError,'lists the existing elements it copies'):self.render()
        # Round-6 regression run: the combined-gates route renders drafts, which skipped this check.
        self.data['state']='draft'
        with self.assertRaisesRegex(ValueError,'lists the existing elements it copies'):self.render()
    def test_reused_element_rejects_markup_unknown_source_and_bad_classes(self):
        for field,value,msg in (('locator','<b>x</b>','plain text'),('source','NOPE','supplied source'),
                                ('classes',['a b'],'existing class names'),('tag','div style','plain tag'),('context','<p>','plain text')):
            self.reuse();self.screen['elements'][0][field]=value
            with self.subTest(field=field),self.assertRaisesRegex(ValueError,msg):self.render()
    def test_unselected_and_blocked_modes_not_ready(self):
        for mode in ('unselected','blocked'):
            self.ui['mode']=mode
            with self.subTest(mode=mode),self.assertRaises(ValueError):self.render()
    def test_malformed_binding_source_is_rejected_cleanly(self):
        self.ui['kit_binding']['source']=[]
        with self.assertRaises(ValueError):self.render()
    def test_malformed_capture_source_is_rejected_cleanly(self):
        self.screen['capture_context']['source']={}
        with self.assertRaises(ValueError):self.render()
    def test_raw_css_or_html_in_reference_rejected(self):
        self.screen['elements'][0]['css']='color:red'
        with self.assertRaisesRegex(ValueError,'markup, styles'):self.render()
    def test_missing_component_id_not_replaced(self):
        self.screen['elements'][0]['item']='gone'
        with self.assertRaisesRegex(ValueError,'removed or is unknown'):self.render()
    def test_unknown_variant_rejected(self):
        self.screen['elements'][0]['variant']='xl'
        with self.assertRaisesRegex(ValueError,'variant'):self.render()
    def test_unknown_state_rejected(self):
        self.screen['elements'][0]['state']='loading'
        with self.assertRaisesRegex(ValueError,'state'):self.render()
    def test_buttons_alone_do_not_approve_layout(self):
        self.screen['elements']=self.screen['elements'][:1]
        with self.assertRaisesRegex(ValueError,'composition pattern'):self.render()
    def test_candidate_entry_cannot_inherit_kit_approval(self):
        self.kit['items'][0].update(status='candidate',approval=None);self.savekit()
        with self.assertRaisesRegex(ValueError,'Kit selection blocked'):self.render()
    def test_out_of_scope_selection(self):
        self.ui['kit_binding']['scope']='other-project'
        with self.assertRaisesRegex(ValueError,'Kit selection blocked'):self.render()
    def test_changed_approval_blocks(self):
        (self.root/'docs/kit-approval.md').write_text('revoked')
        with self.assertRaisesRegex(ValueError,'Kit selection blocked'):self.render()
    def test_changed_theme_source_blocks(self):
        (self.root/'src/Button.tsx').write_text('changed')
        with self.assertRaisesRegex(ValueError,'Kit selection blocked'):self.render()
    def test_missing_capture_record(self):
        self.screen.pop('capture_context')
        with self.assertRaisesRegex(ValueError,'capture_context'):self.render()
    def test_missing_capture_dependency(self):
        self.screen['capture_context']['inputs']=self.screen['capture_context']['inputs'][:1]
        with self.assertRaisesRegex(ValueError,'omits'):self.render()
    def test_rehashed_catalogue_does_not_refresh_old_capture(self):
        p=self.root/'src/Button.tsx';p.write_text('changed')
        self.kit['items'][0]['sources'][0]['sha256']=hashlib.sha256(p.read_bytes()).hexdigest();self.savekit()
        with self.assertRaisesRegex(ValueError,'Capture input changed'):self.render()
    def test_wrong_capture_fingerprint(self):
        self.screen['capture_context']['capture_sha256']='0'*64
        with self.assertRaisesRegex(ValueError,'Capture image differs'):self.render()
    def test_duplicate_capture_input(self):
        self.screen['capture_context']['inputs'].append(copy.deepcopy(self.screen['capture_context']['inputs'][0]))
        with self.assertRaisesRegex(ValueError,'Duplicate capture'):self.render()
    def test_example_must_be_real_declared_source(self):
        self.screen['elements'][0]['example_source']='UIREF'
        with self.assertRaisesRegex(ValueError,'exact example source'):self.render()
    def test_duplicate_element_ids(self):
        self.screen['elements'][1]['id']='E1'
        with self.assertRaisesRegex(ValueError,'unique'):self.render()
    def test_capture_element_marker_links_exact_selection(self):
        self.screen['markers']=[{'element':'E1','position':[0.5,0.5]}]
        self.assertIn('href="#ui-element-'+self.screen['id']+'-E1"',self.render())
    def test_marker_unknown_element_rejected(self):
        self.screen['markers']=[{'element':'missing','position':[0.5,0.5]}]
        with self.assertRaisesRegex(ValueError,'selected element'):self.render()
    def test_markdown_catalogue_uses_projection_in_existing_input(self):
        (self.root/'KIT.md').write_text('Authoritative synthetic catalogue; no duplicate maintained JSON.')
        next(row for row in self.data['sources'] if row['id']=='KIT')['path']='KIT.md'
        self.ui['kit_binding']['projection']=copy.deepcopy(self.kit)
        self.assertIn('Exactly which kit elements are used',self.render())
    def test_markdown_projection_does_not_ignore_source_drift(self):
        self.test_markdown_catalogue_uses_projection_in_existing_input()
        (self.root/'src/Button.tsx').write_text('different')
        with self.assertRaises(ValueError):self.render()
    def test_input_text_is_escaped(self):
        self.screen['elements'][0]['role']='<script>alert(1)</script>'
        out=self.render();self.assertNotIn('<script>alert(1)</script>',out)
        self.assertIn('&lt;script&gt;',out)
    def test_no_output_writes_during_render(self):
        self.render();before={p.relative_to(self.root):p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        r.render(self.data,self.root,self.root/'input.json')
        after={p.relative_to(self.root):p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        self.assertEqual(before,after)


class StrictPolicyTests(unittest.TestCase):
    def test_no_ordinary_escape_modes(self):
        core=(ROOT/'skills/rule-maker/rules/design.md').read_text()
        self.assertIn('No new CSS, ever.',core)
        self.assertIn('Plain only on instruction.',core)
        self.assertIn('Record their words',core)
        self.assertIn('"no kit" is never permission to write CSS',core)
    def test_one_code_backed_catalogue(self):
        text=(ROOT/'skills/ui-design/LIVE-KIT.md').read_text()
        self.assertIn('actual framework components',text)
        self.assertIn('historical',text.lower())
        self.assertIn('does **not** automatically wire',text)
    def test_no_claim_of_tool_enforcement(self):
        text=(ROOT/'skills/ui-design/VERIFY.md').read_text()
        self.assertIn('not a parser',text)
        self.assertIn('not compliance or permission',text)

if __name__=='__main__':unittest.main()
