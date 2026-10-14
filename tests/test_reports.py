from __future__ import annotations

import copy
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / 'skills/codebase-map'
SCRIPT = SKILL / 'scripts/render_report.py'
spec = importlib.util.spec_from_file_location('report_renderer', SCRIPT)
report = importlib.util.module_from_spec(spec)
spec.loader.exec_module(report)


class ReportTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'sources'
        shutil.copytree(SKILL / 'examples', self.root)
        self.input = self.root / 'review.json'
        self.data = report.load_json(self.input)
        self.output = Path(self.temp.name) / 'rendered.html'

    def render(self):
        self.input.write_text(json.dumps(self.data,ensure_ascii=False),encoding='utf-8')
        return report.render(self.data,self.root,self.input)

    def cli(self, *args):
        return subprocess.run([sys.executable,str(SCRIPT),'--root',str(self.root),*map(str,args)],capture_output=True,text=True,timeout=15)

    def test_projection_must_match_the_fingerprinted_input(self):
        self.data['understanding']='Different from the saved projection'
        with self.assertRaisesRegex(ValueError,'match saved input'):
            report.render(self.data,self.root,self.input)

    def test_full_example_validates_and_renders(self):
        content = self.render()
        self.assertIn('AWAITING USER APPROVAL',content)
        self.assertEqual(content.count('class="map"'),3)
        self.assertIn('implementation not authorized',content)
        self.assertNotIn('<button type="submit"',content)
        self.assertIn('no approve button',content)

    def test_current_map_needs_no_implementation_scaffold(self):
        self.data.update(mode='current',state='inspection',graphs=[self.data['graphs'][0]],tasks=[],acceptance=[],requirements=[],comparison=[],default_view='current')
        self.assertIn('inspection only',self.render())

    def test_proposed_design_can_remain_draft(self):
        self.data.update(mode='proposed',state='draft',graphs=[self.data['graphs'][1]],open_decisions=['Choose the error behavior.'])
        self.assertIn('not approval-ready',self.render())

    def test_pending_decision_blocks_approval_ready_state(self):
        self.data['open_decisions']=['New behavior is not settled.']
        with self.assertRaisesRegex(ValueError,'no blocking decisions'):
            self.render()

    def test_approval_ready_needs_compare_mode(self):
        self.data.update(mode='proposed',graphs=[self.data['graphs'][1]])
        with self.assertRaisesRegex(ValueError,'compare mode'):
            self.render()

    def test_approval_ready_needs_authoritative_sources(self):
        self.data['sources'][1]['role']='misc'
        with self.assertRaisesRegex(ValueError,'plan, todo and findings'):
            self.render()

    def test_recorded_approval_requires_matching_revision(self):
        self.data['state']='approved'
        self.data['approval']={'revision':'P0','record':'PLAN Approval','response':'Synthetic test response'}
        with self.assertRaisesRegex(ValueError,'matching recorded approval'):
            self.render()

    def test_recorded_approval_is_not_authentication(self):
        self.data['state']='approved'
        self.data['approval']={'revision':'P1','record':'Synthetic PLAN Approval','response':'Synthetic fixture approval, not a real authorization'}
        self.assertIn('does not authenticate',self.render())

    def test_unsupported_mode_is_rejected(self):
        self.data['mode']='implement'
        with self.assertRaisesRegex(ValueError,'Invalid mode'):
            self.render()

    def test_unrequested_task_is_rejected(self):
        self.data['tasks'][0]['requirements']=[]
        with self.assertRaisesRegex(ValueError,'task.requirements'):
            self.render()

    def test_uncovered_requirement_is_rejected(self):
        self.data['requirements'].append({'id':'R3','text':'Another explicit requirement','origin':'Synthetic test'})
        with self.assertRaisesRegex(ValueError,'Every requirement'):
            self.render()

    def test_task_dependency_cycle_is_rejected(self):
        self.data['tasks'][0]['depends_on']=['T4']
        with self.assertRaisesRegex(ValueError,'cycle'):
            self.render()

    def test_unknown_task_reference_is_rejected(self):
        self.data['graphs'][1]['nodes'][0]['tasks']=['T999']
        with self.assertRaisesRegex(ValueError,'unknown or duplicate'):
            self.render()

    def test_current_relationship_needs_evidence(self):
        self.data['graphs'][0]['edges'][0]['evidence']=[]
        with self.assertRaisesRegex(ValueError,'graph.evidence'):
            self.render()

    def test_design_is_not_observed_code_evidence(self):
        self.data['evidence'][0]['kind']='design'
        with self.assertRaisesRegex(ValueError,'static or runtime'):
            self.render()

    def test_current_flow_cannot_claim_future_behavior(self):
        self.data['graphs'][0]['nodes'][0]['basis']='proposed'
        with self.assertRaisesRegex(ValueError,'Current flow'):
            self.render()

    def test_future_changes_need_proposed_label(self):
        self.data['graphs'][1]['nodes'][0]['basis']='observed'
        with self.assertRaisesRegex(ValueError,'must be marked proposed'):
            self.render()

    def test_unknown_relationship_is_explicit(self):
        edge=self.data['graphs'][0]['edges'][0]
        edge.update(basis='unknown',evidence=[])
        with self.assertRaisesRegex(ValueError,'explain uncertainty'):
            self.render()
        edge['uncertainty']='Dynamic call could not be resolved from available evidence.'
        self.assertIn('Dynamic call could not',self.render())

    def test_missing_edge_endpoint_is_rejected(self):
        self.data['graphs'][0]['edges'][0]['to']='missing'
        with self.assertRaisesRegex(ValueError,'endpoint'):
            self.render()

    def test_overlapping_nodes_are_rejected(self):
        self.data['graphs'][0]['nodes'][1]['x']=48
        with self.assertRaisesRegex(ValueError,'Overlapping'):
            self.render()

    def test_duplicate_ids_are_rejected(self):
        self.data['tasks'][1]['id']='T1'
        with self.assertRaisesRegex(ValueError,'duplicate id'):
            self.render()

    def test_excessive_label_is_rejected_instead_of_clipped(self):
        self.data['graphs'][0]['nodes'][0]['label']='abcdefghijklmnop abcdefghijklmnop abcdefghijklmnop'
        with self.assertRaisesRegex(ValueError,'Shorten'):
            self.render()

    def test_html_and_script_like_text_is_escaped(self):
        payload='</script><img src=x onerror="window.pwned=true"><script>alert(1)</script>'
        self.data['understanding']=payload
        content=self.render()
        self.assertNotIn(payload,content)
        self.assertIn('&lt;img',content)
        self.assertIn("connect-src 'none'",content)
        self.assertIn("script-src 'sha256-",content)
        self.assertNotIn('src="http',content)

    def test_unicode_survives(self):
        self.data['understanding']='Wijzig Café en naïeve labels — 日本語.'
        self.assertIn('日本語',self.render())

    def test_supplied_source_change_and_input_change_are_detected(self):
        self.output.write_text(self.render(),encoding='utf-8')
        self.assertEqual(report.check_report(self.output,self.root),[])
        (self.root/'src/scoreboard.py').write_text('# changed uncommitted fixture',encoding='utf-8')
        self.input.write_text('{}',encoding='utf-8')
        changed=report.check_report(self.output,self.root)
        self.assertIn('CHANGED: src/scoreboard.py',changed)
        self.assertIn('CHANGED: review.json',changed)

    def test_missing_source_is_reported(self):
        self.output.write_text(self.render(),encoding='utf-8')
        (self.root/'PLAN.md').unlink()
        self.assertIn('MISSING OR UNSAFE: PLAN.md',report.check_report(self.output,self.root))

    def test_path_traversal_is_rejected(self):
        outside=Path(self.temp.name)/'outside.md';outside.write_text('private')
        self.data['sources'][0]['path']='../outside.md'
        with self.assertRaisesRegex(ValueError,'inside root'):
            self.render()

    def test_symlink_escape_is_rejected(self):
        outside=Path(self.temp.name)/'outside.md';outside.write_text('private')
        try:
            (self.root/'escape.md').symlink_to(outside)
        except (OSError,NotImplementedError):
            self.skipTest('This host does not permit symlinks.')
        self.data['sources'][0]['path']='escape.md'
        with self.assertRaisesRegex(ValueError,'outside-root'):
            self.render()

    def test_file_size_limit_is_explicit(self):
        with (self.root/'large.md').open('wb') as stream:
            stream.truncate(report.MAX_BYTES+1)
        self.data['sources'][0]['path']='large.md'
        with self.assertRaisesRegex(ValueError,'8 MiB'):
            self.render()

    def test_cli_does_not_overwrite_existing_output(self):
        self.output.write_text('preserve this approval revision')
        result=self.cli('--input',self.input,'--output',self.output)
        self.assertEqual(result.returncode,2)
        self.assertEqual(self.output.read_text(),'preserve this approval revision')

    def test_cli_creates_only_requested_file_then_checks_without_writes(self):
        before={p.relative_to(self.root).as_posix():p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        result=self.cli('--input',self.input,'--output',self.output)
        self.assertEqual(result.returncode,0,result.stderr)
        after={p.relative_to(self.root).as_posix():p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        self.assertEqual(before,after)
        result=self.cli('--check',self.output)
        self.assertEqual(result.returncode,0,result.stderr)
        (self.root/'TODO.md').write_text('changed')
        self.assertEqual(self.cli('--check',self.output).returncode,1)

    def test_outside_root_input_is_rejected_before_rendering(self):
        outside=Path(self.temp.name)/'outside.json'
        outside.write_text(json.dumps(self.data),encoding='utf-8')
        result=self.cli('--input',outside,'--output',self.output)
        self.assertEqual(result.returncode,2)
        self.assertIn('inside the supplied source root',result.stderr)
        self.assertFalse(self.output.exists())

    def test_non_html_output_is_rejected(self):
        output=Path(self.temp.name)/'not-a-report.exe'
        result=self.cli('--input',self.input,'--output',output)
        self.assertEqual(result.returncode,2)
        self.assertIn('extension',result.stderr)
        self.assertFalse(output.exists())

    def test_malformed_input_reports_error_without_traceback(self):
        self.input.write_text('{"schema_version": 1, "graphs": 123}')
        result=self.cli('--input',self.input,'--output',self.output)
        self.assertEqual(result.returncode,2)
        self.assertNotIn('Traceback',result.stderr)
        self.assertFalse(self.output.exists())

    def test_open_failure_does_not_claim_display_or_delete_report(self):
        with patch.object(sys,'argv',['render','--root',str(self.root),'--input',str(self.input),'--output',str(self.output),'--open']), patch.object(report.webbrowser,'open',return_value=False) as opener, patch('builtins.print') as messages:
            self.assertEqual(report.main(),0)
        self.assertTrue(self.output.exists())
        self.assertTrue(opener.call_args[0][0].startswith('file:'))
        self.assertTrue(any('NOT ACCEPTED' in str(c) for c in messages.call_args_list))

    def test_portable_skill_copy_includes_every_renderer_dependency(self):
        copy_path=Path(self.temp.name)/'standalone-map'
        shutil.copytree(SKILL,copy_path,ignore=shutil.ignore_patterns('__pycache__'))
        result=subprocess.run([sys.executable,str(copy_path/'scripts/render_report.py'),'--root',str(copy_path/'examples'),'--input',str(copy_path/'examples/review.json'),'--output',str(self.output)],capture_output=True,text=True,timeout=15)
        self.assertEqual(result.returncode,0,result.stderr)


if __name__=='__main__':
    unittest.main()
