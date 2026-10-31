"""Optional UI review validation and safe rendering; not model or human-approval tests."""
from __future__ import annotations
import copy
import hashlib
import importlib.util
import json
import shutil
import struct
import tempfile
import unittest
import zlib
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('screen_renderer_test',ROOT/'skills/codebase-map/scripts/render_report.py')
r=importlib.util.module_from_spec(spec);spec.loader.exec_module(r)
ui=r.ui_module()


def png(width=4,height=4):
    def chunk(kind,value):
        return struct.pack('>I',len(value))+kind+value+struct.pack('>I',zlib.crc32(kind+value)&0xffffffff)
    return b'\x89PNG\r\n\x1a\n'+chunk(b'IHDR',struct.pack('>IIBBBBB',width,height,8,6,0,0,0))+chunk(b'IDAT',zlib.compress((b'\0'+b'\xff\xff\xff\xff'*width) * height))+chunk(b'IEND',b'')


class ScreenFlowTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        shutil.copytree(ROOT/'skills/codebase-map/examples',self.root,dirs_exist_ok=True)
        self.data=r.load_json(self.root/'review.json')
        self.data.update(state='draft',open_decisions=['Synthetic sample — no application approval'])
        self.ui=copy.deepcopy(json.loads((ROOT/'skills/codebase-map/examples/ui-review/review-r2.json').read_text())['ui_review'])
        self.data['sources'].append({'id':'UIREF','role':'design-example','path':'ui-review/README.md'})
        self.data['ui_review']=self.ui
        self.input=self.root/'input.json'

    def render(self):
        self.input.write_text(json.dumps(self.data),encoding='utf-8')
        return r.render(self.data,self.root,self.input)

    def application(self):
        self.ui['kind']='application'
        for s in self.ui['screens']:
            s['requirements']=[self.data['requirements'][0]['id']]
            s['tasks']=[self.data['tasks'][0]['id']]
            s['evidence']=[self.data['evidence'][0]['id']]

    def ready(self):
        self.application()
        self.ui['mode']='functionality-only';self.ui['authority']['status']='confirmed'
        self.data['state']='awaiting-approval';self.data['open_decisions']=[]
        for d in self.ui['decisions']:
            d.update(status='deferred',reason='Appearance remains pending in the expressly approved functional preview.')

    def capture(self):
        p=self.root/'capture.png';p.write_bytes(png())
        self.data['sources'].append({'id':'CAP','role':'ui-capture','path':'capture.png'})
        for s in self.ui['screens']:
            s.pop('content',None);s['representation']='capture';s['capture']='CAP';s['sources'].append('CAP')
        return p

    def test_adds_view_without_replacing_full_report_sections(self):
        html=self.render()
        for label in ['What changes','What will not change','Changes and cleanup','How completion will be checked','Technical evidence and task details','UI screens']:
            self.assertIn(label,html)
        self.assertEqual(html.count('class="map"'),3)
        self.assertIn('Illustrative UI example',html)
        self.assertIn('data-only', (ROOT/'skills/codebase-map/UI-FLOW.md').read_text())

    def test_old_schema2_input_has_no_ui_assets_or_view(self):
        self.data.pop('ui_review');html=self.render()
        self.assertNotIn('panel-ui-preview',html)
        self.assertNotIn('fitUiFlow()',html)
        self.assertIn("img-src 'none'",html)

    def test_original_styles_and_script_remain_embedded_without_modifications(self):
        html=self.render()
        self.assertIn((ROOT/'skills/codebase-map/assets/report.css').read_text(),html)
        self.assertIn((ROOT/'skills/codebase-map/assets/report.js').read_text(),html)

    def test_original_view_stays_default(self):
        html=self.render()
        self.assertIn('id="view-proposed" aria-label="Feature flow" aria-controls="panel-proposed" checked',html)
        self.assertIn('id="view-ui-preview" aria-label="UI screens" aria-controls="panel-ui-preview" >',html)

    def test_actual_ui_can_open_first_without_erasing_other_graphs(self):
        self.ui['open_first']=True
        html=self.render()
        self.assertIn('id="view-ui-preview" aria-label="UI screens" aria-controls="panel-ui-preview" checked',html)
        self.assertIn('panel-current',html)

    def test_long_title_does_not_overlap_inspect(self):
        self.ui['screens'][0]['title']='X'*40
        with self.assertRaisesRegex(ValueError,'title does not fit'):self.render()

    def test_long_input_value_does_not_overflow(self):
        self.ui['screens'][0]['content'][1]={'kind':'input','label':'Value','value':'X'*42}
        with self.assertRaisesRegex(ValueError,'field value'):self.render()

    def test_draft_cannot_draw_proposed_screens_without_preview_permission(self):
        self.ui['preview']['status']='proposed'
        with self.assertRaisesRegex(ValueError,'preview permission'):self.render()

    def test_draft_kit_cannot_substitute_schematics(self):
        self.ui['mode']='approved-kit'
        with self.assertRaisesRegex(ValueError,'actual component captures'):self.render()

    def test_accepted_design_cannot_have_unresolved_source_or_choices(self):
        self.application()
        self.ui['acceptance'].update(status='accepted',source='UIREF',locator='decision',summary='Test acceptance')
        with self.assertRaisesRegex(ValueError,'accepted design'):self.render()

    def test_unknown_ui_fields_fail_instead_of_accepting_markup(self):
        self.ui['html']='<button onclick="fetch()">bad</button>'
        with self.assertRaisesRegex(ValueError,'raw HTML'):self.render()

    def test_unknown_screen_fields_are_rejected(self):
        self.ui['screens'][0]['css']='color:red'
        with self.assertRaisesRegex(ValueError,'Unknown screen'):self.render()

    def test_raw_control_or_style_is_rejected(self):
        self.ui['screens'][0]['content'][0]['style']='position:fixed'
        with self.assertRaisesRegex(ValueError,'structured inert'):self.render()

    def test_control_script_text_is_escaped(self):
        self.ui['screens'][0]['content'][1]['label']='<script>alert(1)</script>'
        html=self.render()
        self.assertNotIn('<script>alert(1)</script>',html)
        self.assertIn('&lt;script&gt;alert(1)&lt;/script&gt;',html)

    def test_no_executable_app_form_or_approval_controls(self):
        html=self.render()
        for text in ('<form','<iframe','<foreignObject','onclick=','<input type="checkbox"','<button type="submit"'):
            self.assertNotIn(text,html)
        self.assertIn('does not record approval',html)

    def test_missing_authority_is_not_assumed(self):
        del self.ui['authority']
        with self.assertRaisesRegex(ValueError,'actual supplied source'):self.render()

    def test_approval_ready_cannot_hide_unconfirmed_mode(self):
        self.ready();self.ui['authority']['status']='unconfirmed'
        with self.assertRaisesRegex(ValueError,'confirmed mode'):self.render()

    def test_no_automatic_plain_preview_permission(self):
        self.ready();self.ui['preview']['status']='proposed'
        with self.assertRaisesRegex(ValueError,'preview authority'):self.render()

    def test_open_visual_choice_blocks_actual_approval(self):
        self.ready();self.ui['decisions'][0].update(status='open');self.ui['decisions'][0].pop('reason')
        with self.assertRaisesRegex(ValueError,'Resolve blocking'):self.render()

    def test_legacy_plain_mode_no_longer_authorises_new_application_report(self):
        self.ready()
        with self.assertRaisesRegex(ValueError,'Strict kit-only'): self.render()

    def test_approved_kit_cannot_use_schematic_as_visual_proof(self):
        self.ready();self.ui['mode']='approved-kit'
        with self.assertRaisesRegex(ValueError,'actual component captures'):self.render()

    def test_source_backed_capture_can_be_rendered_for_approved_kit(self):
        self.ready();self.data['state']='draft';self.ui['mode']='approved-kit';self.capture()
        html=self.render();self.assertIn('data:image/png;base64,',html)
        self.assertIn('img-src data:',html)
        self.assertIn('preserveAspectRatio="xMidYMin meet"',html)

    def test_capture_is_in_freshness_manifest(self):
        p=self.capture();html=self.render();output=self.root/'report.html';output.write_text(html)
        self.assertEqual(r.check_report(output,self.root),[])
        p.write_bytes(p.read_bytes()+b'changed')
        self.assertIn('CHANGED: capture.png',r.check_report(output,self.root))

    def test_capture_paths_cannot_be_remote(self):
        self.capture();self.data['sources'][-1]['path']='https://example.com/a.png'
        with self.assertRaises(ValueError):self.render()

    def test_svg_disguised_as_png_is_rejected(self):
        p=self.capture();p.write_text('<svg><script>bad()</script></svg>')
        with self.assertRaisesRegex(ValueError,'not a supported PNG'):self.render()

    def test_oversized_capture_is_rejected(self):
        p=self.capture();p.write_bytes(b'x'*(ui.MAX_CAPTURE+1))
        with self.assertRaisesRegex(ValueError,'at most 2 MB'):self.render()

    def test_trailing_capture_bytes_are_rejected(self):
        p=self.capture();p.write_bytes(p.read_bytes()+b'<script>bad</script>')
        with self.assertRaisesRegex(ValueError,'trailing'):self.render()

    def test_capture_crc_damage_is_rejected(self):
        p=self.capture();raw=bytearray(p.read_bytes());raw[30]^=1;p.write_bytes(raw)
        with self.assertRaisesRegex(ValueError,'checksum'):self.render()

    def test_sample_cannot_claim_application_design_acceptance(self):
        self.ui['acceptance'].update(status='accepted',source='UIREF',locator='fake',summary='Synthetic approval')
        with self.assertRaisesRegex(ValueError,'illustrative sample'):self.render()

    def test_accepted_design_requires_record(self):
        self.application();self.ui['acceptance']['status']='accepted'
        with self.assertRaisesRegex(ValueError,'actual supplied source'):self.render()

    def test_selected_decision_requires_owner_record(self):
        self.ui['decisions'][0].update(status='selected',selection='Approved checkbox')
        with self.assertRaisesRegex(ValueError,'actual supplied source'):self.render()

    def test_open_decision_cannot_claim_selection(self):
        self.ui['decisions'][0]['selection']='Approved checkbox'
        with self.assertRaisesRegex(ValueError,'Unsettled'):self.render()

    def test_missing_source_mapping_is_rejected(self):
        self.ui['screens'][0]['sources']=[]
        with self.assertRaisesRegex(ValueError,'reference'):self.render()

    def test_actual_task_screen_needs_requirement_mapping(self):
        self.application();self.ui['screens'][0]['requirements']=[]
        with self.assertRaisesRegex(ValueError,'reference'):self.render()

    def test_unknown_task_is_rejected(self):
        self.application();self.ui['screens'][0]['tasks']=['missing']
        with self.assertRaisesRegex(ValueError,'reference'):self.render()

    def test_mismatched_decision_screen_link_is_rejected(self):
        self.ui['decisions'][0]['screens']=['UI1']
        with self.assertRaisesRegex(ValueError,'mapping disagrees'):self.render()

    def test_incorrect_control_marker_is_rejected(self):
        self.ui['screens'][0]['content'][2]['decision']='D9'
        with self.assertRaisesRegex(ValueError,'not mapped'):self.render()

    def test_screen_boxes_cannot_overlap(self):
        self.ui['screens'][1]['x']=64
        with self.assertRaisesRegex(ValueError,'Overlapping'):self.render()

    def test_connectors_cannot_cross_screens(self):
        self.ui['transitions'][0]['points']=[[352,240],[640,240],[480,240]]
        with self.assertRaises(ValueError):self.render()

    def test_short_screen_does_not_shrink_text(self):
        self.ui['screens'][0]['height']=280
        with self.assertRaisesRegex(ValueError,'too small'):self.render()

    def test_too_many_screens_requires_split(self):
        for n in range(3):
            s=copy.deepcopy(self.ui['screens'][0]);s['id']='NEW'+str(n);self.ui['screens'].append(s)
        with self.assertRaisesRegex(ValueError,'more than six'):self.render()

    def test_reserved_view_id_does_not_shadow_normal_flow(self):
        self.data['graphs'][0]['id']='ui-preview'
        with self.assertRaisesRegex(ValueError,'reserved'):self.render()

    def test_current_inspection_cannot_introduce_new_screens(self):
        self.data.update(mode='current',state='inspection',graphs=[self.data['graphs'][0]],tasks=[],acceptance=[],requirements=[],comparison=[],default_view='current')
        with self.assertRaisesRegex(ValueError,'Current inspection'):self.render()

    def test_ui_view_details_work_without_application_logic(self):
        html=self.render()
        self.assertIn('id="ui-detail-UI1"',html)
        self.assertIn('href="#ui-decision-D1"',html)
        self.assertIn('screen and sources',html)
        self.assertNotIn('fetch(',html)

    def test_report_manifest_tracks_new_renderer_version(self):
        version=json.loads((ROOT/".claude-plugin/plugin.json").read_text())["version"]
        self.assertIn('"tool_version": '+json.dumps(version),self.render())


class InstallAuditExtraFiles(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.skills=Path(self.tmp.name)/'skills'
        shutil.copytree(ROOT/'skills',self.skills,ignore=shutil.ignore_patterns('__pycache__'))
        spec=importlib.util.spec_from_file_location('extra_audit',ROOT/'skills/rule-maker/scripts/audit_installation.py')
        self.audit=importlib.util.module_from_spec(spec);spec.loader.exec_module(self.audit)

    def test_unexpected_instruction_file_means_drift(self):
        (self.skills/'rule-maker/rules/OLD.md').write_text('old active instruction')
        r=self.audit.inspect([self.skills]);row=r['candidates'][0]
        self.assertEqual(row['state'],'DRIFT')
        self.assertIn('rule-maker/rules/OLD.md',row['unexpected'])
        self.assertTrue((self.skills/'rule-maker/rules/OLD.md').exists())

    def test_unrelated_external_skills_are_not_flagged(self):
        p=self.skills/'grilling';p.mkdir();(p/'SKILL.md').write_text('external')
        self.assertEqual(self.audit.inspect([self.skills])['candidates'][0]['state'],'MATCH')

    def test_cache_files_are_not_policy_drift(self):
        p=self.skills/'workflow/__pycache__';p.mkdir();(p/'sample.pyc').write_bytes(b'x')
        self.assertEqual(self.audit.inspect([self.skills])['candidates'][0]['state'],'MATCH')


class ScreenFlowPolicyTests(unittest.TestCase):
    def test_owning_workflow_preserves_full_report(self):
        text=(ROOT/'skills/workflow/VISUAL-REVIEW.md').read_text()
        self.assertIn('same full report',text)
        self.assertIn('not replace the report',text)
    def test_design_source_selection_is_not_filename_authority(self):
        text=(ROOT/'skills/rule-maker/rules/design.md').read_text()
        self.assertIn('exact component/pattern source',text)
        self.assertIn('same-task decision',text)
    def test_no_automatic_plain_html_fallback(self):
        text=(ROOT/'skills/ui-design/SKILL.md').read_text()
        self.assertIn('No new plain-HTML controls',text)
    def test_old_report_records_are_present(self):
        p=ROOT/'docs/plans/2026-10-30-rules-audit-design-kit/review-r2.html'
        self.assertIn('R2-draft',p.read_text())
    def test_binary_capture_policy_preserves_bytes(self):
        text=(ROOT/'.gitattributes').read_text()
        self.assertIn('*.png -text',text)
        self.assertIn('skills/** text eol=lf',text)

if __name__=='__main__':unittest.main()
