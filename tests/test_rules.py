"""Mechanical rule gates/config helpers; these do NOT claim live model or hook enforcement."""
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

ROOT=Path(__file__).resolve().parents[1]
from links_helper import make_link
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    module=importlib.util.module_from_spec(spec);sys.modules[name]=module;spec.loader.exec_module(module)
    return module
r=load('rules_readiness_test',ROOT/'skills/rule-maker/scripts/readiness.py')
a=load('rules_activation_test',ROOT/'skills/rule-maker/scripts/activate_rules.py')

class RuleGateTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)/'project';self.root.mkdir()
        (self.root/'AGENTS.md').write_text('Synthetic project rules for test evidence, not a real assessment.')
        (self.root/'src').mkdir()
        self.current=r.snapshot(self.root,['src'],task='T1',host='test-host/profile')
        self.data={'schema_version':1,'snapshot':copy.deepcopy(self.current),
                   'checks':{n:{'status':'verified','evidence':'Synthetic test assertion: '+n} for n in r.REQUIRED}}
    def test_ready_not_implementation_approval(self):
        out=r.evaluate(self.data,self.current,'change')
        self.assertEqual(out['state'],'READY');self.assertFalse(out['implementation_approved'])
    def test_missing_project_rules_require_decision(self):
        self.data['checks']['project_rules']['status']='missing'
        self.assertEqual(r.evaluate(self.data,self.current,'plan')['state'],'NEEDS_SETUP')
    def test_existing_valid_rules_no_setup_marker(self):
        self.assertNotIn('setup',self.data)
        self.assertEqual(r.evaluate(self.data,self.current,'plan')['state'],'READY')
    def test_generic_continue_not_exception(self):
        self.data['checks']['project_rules']['status']='missing';self.data['exception']='go ahead'
        self.assertEqual(r.evaluate(self.data,self.current,'change')['state'],'BLOCKED')
    def exception(self):
        self.data['checks']['project_rules']['status']='missing'
        self.data['exception']={'authority_confirmed':True,'active':True,'response_ref':'user message 7',
             'reason':'Owner explicitly accepts this documentation gap for T1','expires':'task',
             'gaps':['project_rules'],'operations':['plan','change'],
             'snapshot_fingerprint':self.current['fingerprint']}
    def test_scoped_exception_allows_only_named_operations(self):
        self.exception()
        self.assertEqual(r.evaluate(self.data,self.current,'change')['state'],'LIMITED_EXCEPTION')
        self.assertEqual(r.evaluate(self.data,self.current,'test')['state'],'BLOCKED')
    def test_exception_never_approves_implementation(self):
        self.exception();self.assertFalse(r.evaluate(self.data,self.current,'change')['implementation_approved'])
    def test_partial_exception_is_not_consent(self):
        self.exception();del self.data['exception']['response_ref']
        self.assertEqual(r.evaluate(self.data,self.current,'change')['state'],'BLOCKED')
    def test_expired_exception_blocks(self):
        self.exception();self.data['exception']['active']=False
        self.assertEqual(r.evaluate(self.data,self.current,'change')['state'],'BLOCKED')
    def test_permanent_exception_rejected(self):
        self.exception();self.data['exception']['expires']='forever'
        self.assertEqual(r.evaluate(self.data,self.current,'change')['state'],'BLOCKED')
    def test_exception_does_not_cover_another_gap(self):
        self.exception();self.data['checks']['verification']['status']='missing'
        self.assertEqual(r.evaluate(self.data,self.current,'change')['state'],'BLOCKED')
    def test_nonwaivable_unknowns_block(self):
        for name in set(r.REQUIRED)-r.WAIVABLE:
            with self.subTest(name=name):
                data=copy.deepcopy(self.data);data['checks'][name]['status']='missing'
                self.assertEqual(r.evaluate(data,self.current,'change')['state'],'BLOCKED')
    def test_conflict_not_waived(self):
        self.exception();self.data['checks']['conflicts']['status']='blocked'
        self.assertEqual(r.evaluate(self.data,self.current,'change')['state'],'BLOCKED')
    def test_missing_assessment_not_ready(self):
        self.assertEqual(r.evaluate({'schema_version':1},self.current,'plan')['state'],'BLOCKED')
    def test_unknown_state_default_blocks(self):
        self.data['checks']['authority']['status']='probably'
        self.assertEqual(r.evaluate(self.data,self.current,'change')['state'],'BLOCKED')
    def test_unknown_schema_and_mode_block(self):
        self.assertEqual(r.evaluate(self.data,self.current,'deploy')['state'],'BLOCKED')
        self.data['schema_version']=42
        self.assertEqual(r.evaluate(self.data,self.current,'change')['state'],'BLOCKED')
    def test_missing_evidence_blocks(self):
        self.data['checks']['scope']['evidence']=''
        self.assertEqual(r.evaluate(self.data,self.current,'plan')['state'],'BLOCKED')
    def test_required_check_cannot_be_skipped(self):
        self.data['checks']['verification']['status']='not-applicable'
        self.assertEqual(r.evaluate(self.data,self.current,'plan')['state'],'BLOCKED')
    def test_unrelated_design_may_be_not_applicable(self):
        self.data['checks']['design']={'status':'not-applicable','evidence':'No appearance changes in this fixture.'}
        self.assertEqual(r.evaluate(self.data,self.current,'plan')['state'],'READY')
    def test_unknown_category_is_not_ignored(self):
        self.data['checks']['magic']={'status':'verified','evidence':'x'}
        self.assertEqual(r.evaluate(self.data,self.current,'plan')['state'],'BLOCKED')
    def test_read_only_needs_no_setup(self):
        self.assertEqual(r.evaluate({'schema_version':1},self.current,'read-only')['state'],'READ_ONLY')
    def test_setup_requires_named_consent(self):
        self.data['checks']['project_rules']['status']='missing'
        self.assertEqual(r.evaluate(self.data,self.current,'setup')['state'],'NEEDS_SETUP')
        self.data['setup_consent']={'authority_confirmed':True,'response_ref':'owner exact setup files','paths':['AGENTS.md']}
        self.assertEqual(r.evaluate(self.data,self.current,'setup')['state'],'SETUP_ONLY')
        self.assertEqual(r.evaluate(self.data,self.current,'change')['state'],'NEEDS_SETUP')
    def test_setup_does_not_clear_trust(self):
        self.data['setup_consent']={'authority_confirmed':True,'response_ref':'yes','paths':['AGENTS.md']}
        self.data['checks']['trust']['status']='blocked'
        self.assertEqual(r.evaluate(self.data,self.current,'setup')['state'],'BLOCKED')
    def test_change_in_project_rules_invalidates_snapshot(self):
        (self.root/'AGENTS.md').write_text('different restrictions')
        current=r.snapshot(self.root,['src'],task='T1',host='test-host/profile')
        self.assertEqual(r.evaluate(self.data,current,'change')['state'],'BLOCKED')
    def test_new_nested_rules_invalidate_snapshot(self):
        (self.root/'src/AGENTS.md').write_text('new nested rules')
        current=r.snapshot(self.root,['src'],task='T1',host='test-host/profile')
        self.assertEqual(r.evaluate(self.data,current,'change')['state'],'BLOCKED')
    def test_changed_manifest_invalidates(self):
        (self.root/'package.json').write_text('{"dependencies":{"react":"18.3.1"}}')
        current=r.snapshot(self.root,['src'],task='T1',host='test-host/profile')
        self.assertEqual(r.evaluate(self.data,current,'change')['state'],'BLOCKED')
    @unittest.skipUnless(shutil.which('git'),'Git unavailable')
    def test_branch_identity_invalidates(self):
        subprocess.run(['git','init','-q',str(self.root)],check=True)
        before=r.snapshot(self.root,['src'],task='T1',host='test')
        subprocess.run(['git','-C',str(self.root),'symbolic-ref','HEAD','refs/heads/other-task'],check=True)
        after=r.snapshot(self.root,['src'],task='T1',host='test')
        self.assertNotEqual(before['fingerprint'],after['fingerprint'])
    def test_scope_expansion_invalidates(self):
        current=r.snapshot(self.root,['src','UnityClient'],task='T1',host='test-host/profile')
        self.assertEqual(r.evaluate(self.data,current,'change')['state'],'BLOCKED')
    def test_other_task_and_host_invalidates(self):
        for task,host in [('T2','test-host/profile'),('T1','other-account')]:
            current=r.snapshot(self.root,['src'],task=task,host=host)
            self.assertEqual(r.evaluate(self.data,current,'change')['state'],'BLOCKED')
    def test_exception_not_reusable_in_other_project(self):
        self.exception();other=Path(self.tmp.name)/'other';other.mkdir();(other/'src').mkdir()
        current=r.snapshot(other,['src'],task='T1',host='test-host/profile')
        self.assertEqual(r.evaluate(self.data,current,'change')['state'],'BLOCKED')
    def test_rerun_with_same_inputs_reuses_assessment(self):
        current=r.snapshot(self.root,['src'],task='T1',host='test-host/profile')
        self.assertEqual(r.evaluate(self.data,current,'change')['state'],'READY')
    def test_escape_paths_rejected(self):
        for scope in ('../outside','/absolute','C:/wrong','src\\wrong','src\nwrong'):
            with self.subTest(scope=scope),self.assertRaises(ValueError):
                r.snapshot(self.root,[scope],task='T1',host='test')
    def test_linked_input_rejected(self):
        other=Path(self.tmp.name)/'outside';other.write_text('private')
        (self.root/'AGENTS.md').unlink();make_link(self.root/'AGENTS.md',other)
        with self.assertRaises(ValueError):r.snapshot(self.root,['src'],task='T1',host='test')
    def test_partial_shared_update_rejected(self):
        shared=Path(self.tmp.name)/'rules';shutil.copytree(r.RULES,shared)
        (shared/'CORE.md').write_text('truncated core')
        with self.assertRaisesRegex(ValueError,'Mixed/modified'):
            r.snapshot(self.root,['src'],task='T1',host='test',shared=shared)
    def test_explicit_reference_change_detected(self):
        (self.root/'POLICY.md').write_text('approved rule references')
        first=r.snapshot(self.root,['src'],task='T1',host='test',sources=['POLICY.md'])
        (self.root/'POLICY.md').write_text('changed')
        second=r.snapshot(self.root,['src'],task='T1',host='test',sources=['POLICY.md'])
        self.assertNotEqual(first['fingerprint'],second['fingerprint'])
    def test_inspect_cli_never_claims_readiness_and_writes_nothing(self):
        before=sorted(p.relative_to(self.root).as_posix() for p in self.root.rglob('*'))
        cmd=[sys.executable,str(ROOT/'skills/rule-maker/scripts/readiness.py'),'inspect','--root',str(self.root),'--scope','src','--task','T1','--host','test']
        out=subprocess.run(cmd,capture_output=True,text=True,check=True)
        self.assertEqual(json.loads(out.stdout)['state'],'REVIEW_REQUIRED')
        self.assertEqual(before,sorted(p.relative_to(self.root).as_posix() for p in self.root.rglob('*')))
    def test_assess_stdin_blocks_missing_rules(self):
        current=r.snapshot(self.root,['src'],task='T1',host='test')
        data=copy.deepcopy(self.data);data['snapshot']=current;data['checks']['project_rules']['status']='missing'
        cmd=[sys.executable,str(ROOT/'skills/rule-maker/scripts/readiness.py'),'assess','--root',str(self.root),'--scope','src','--task','T1','--host','test']
        out=subprocess.run(cmd,input=json.dumps(data),capture_output=True,text=True)
        self.assertEqual(out.returncode,2);self.assertEqual(json.loads(out.stdout)['state'],'NEEDS_SETUP')

class RulesActivationTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup);self.home=Path(self.tmp.name)
        self.claude=self.home/'.claude';self.codex=self.home/'.codex'
    def plan(self):return a.build_plan(self.home,self.claude,self.codex,'both')
    def test_preview_does_not_write(self):
        self.assertEqual(len(self.plan()),2);self.assertFalse(self.claude.exists());self.assertFalse(self.codex.exists())
    def test_apply_is_idempotent_and_does_not_copy_rules(self):
        a.load_file_helpers().apply_plan(self.plan());self.assertTrue(all(c.before==c.after for c in self.plan()))
        self.assertFalse((self.home/'.workflow-axa').exists())
        self.assertEqual(len(list(self.home.rglob('*.md'))),2)
    def test_preserves_crlf_bom_and_other_policy(self):
        self.claude.mkdir();p=self.claude/'CLAUDE.md';original=b'\xef\xbb\xbf# Private\r\nDo not remove.\r\n'
        p.write_bytes(original);a.load_file_helpers().apply_plan(self.plan())
        self.assertTrue(p.read_bytes().startswith(original));self.assertNotIn(b'\n',p.read_bytes().replace(b'\r\n',b''))
    def test_codex_nonempty_override_is_covered(self):
        self.codex.mkdir();p=self.codex/'AGENTS.override.md';p.write_text('Existing override')
        changes=self.plan();self.assertEqual(len(changes),3)
        a.load_file_helpers().apply_plan(changes);self.assertIn(a.START,p.read_text());self.assertTrue(p.read_text().startswith('Existing override'))
    def test_empty_override_untouched(self):
        self.codex.mkdir();p=self.codex/'AGENTS.override.md';p.write_text(' \n')
        self.assertEqual(len(self.plan()),2);self.assertEqual(p.read_text(),' \n')
    def test_wrong_duplicate_markers_refused(self):
        for raw in (a.START+a.START+a.END,a.START,a.END+a.START):
            with self.subTest(raw=raw),self.assertRaises(ValueError):a.merge(raw.encode(),'replacement')
    def test_config_symlink_refused(self):
        self.claude.mkdir();outside=self.home/'outside';outside.write_text('outside')
        make_link(self.claude/'CLAUDE.md',outside)
        with self.assertRaises(ValueError):self.plan()
    def test_profile_overlap_refused(self):
        # Same physical target is rejected by the underlying safe-file checks when linked.
        with self.assertRaises(ValueError):a.build_plan(self.home,Path('relative'),self.codex,'both')
    def test_library_modified_before_activation_is_rejected(self):
        shared=self.home/'rules';shutil.copytree(a.LIBRARY,shared);(shared/'CORE.md').write_text('changed')
        with self.assertRaisesRegex(ValueError,'Mixed/modified'):
            a.build_plan(self.home,self.claude,self.codex,'both',shared)
    def test_config_changed_after_preview_is_rejected(self):
        changes=self.plan();self.claude.mkdir();(self.claude/'CLAUDE.md').write_text('concurrent edit')
        with self.assertRaises(ValueError):a.load_file_helpers().apply_plan(changes)
        self.assertEqual((self.claude/'CLAUDE.md').read_text(),'concurrent edit')
    def test_import_syntax_is_host_specific(self):
        claude=a.block('claude',a.LIBRARY);codex=a.block('codex',a.LIBRARY)
        self.assertIn('@'+a.LIBRARY.as_posix()+'/START.md',claude)
        self.assertIn('not automatic Markdown imports',codex)
    def test_ambiguous_import_path_is_rejected(self):
        with self.assertRaises(ValueError):a.block('claude',Path('/tmp/name with spaces/rules'))

class ReadinessContractTests(unittest.TestCase):
    def test_live_scenario_matrix_is_authored_not_claimed_run(self):
        suite=json.loads((ROOT/'tests/behavioral/rules-readiness.json').read_text())
        self.assertEqual(suite['candidate_version'],json.loads((ROOT/'.claude-plugin/plugin.json').read_text())['version'])
        self.assertEqual(len(suite['cases']),40)
        self.assertEqual(len({c['id'] for c in suite['cases']}),40)
        self.assertTrue(all(c['result']=='NOT_RUN' and c['expected'] and c['preparation'] for c in suite['cases']))

    def test_workflow_gate_precedes_task_creation(self):
        t=(ROOT/'skills/workflow/SKILL.md').read_text()
        self.assertLess(t.index('## 0. Check rules readiness'),t.index('Before creating any task folder'))
        self.assertIn('even if rule-maker never ran',t)
    def test_scoped_exception_and_bootstrap_are_documented(self):
        t=(ROOT/'skills/rule-maker/rules/READINESS.md').read_text()
        for s in ('LIMITED_EXCEPTION','SETUP_ONLY','No separate waiver report','Noninteractive runs','unknown state','before delegation'):
            self.assertIn(s,t)
    def test_all_entrypoints_address_readiness_without_duplicate_full_policy(self):
        for name in ('workflow','resume-task','plan-review','workflow-doctor','task-status','codebase-map'):
            t=(ROOT/f'skills/{name}/SKILL.md').read_text().lower()
            self.assertTrue('rules' in t,name)
        self.assertEqual(len(list((ROOT/'skills').rglob('READINESS.md'))),1)
    def test_no_external_diagram_dependency_added(self):
        c=json.loads((ROOT/'skills/workflow/specialists.json').read_text())
        self.assertNotIn('diagram-design',c['skills'])
        self.assertIn('grilling',c['skills'])
    def test_rule_module_integrity(self):
        self.assertEqual(a.validate_library(a.LIBRARY)['rules_version'],'1.6.0')
