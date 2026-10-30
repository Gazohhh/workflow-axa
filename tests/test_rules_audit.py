"""Read-only install comparison, stack detection and audit-policy regression contracts."""
from __future__ import annotations
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load(name,path):
 spec=importlib.util.spec_from_file_location(name,ROOT/path)
 module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
check=load('installation_test','skills/rule-maker/scripts/audit_installation.py')
versions=load('versions_audit_test','skills/rule-maker/scripts/version_facts.py')
readiness=load('readiness_audit_test','skills/rule-maker/scripts/readiness.py')

class InstallationAuditTests(unittest.TestCase):
 def test_current_default_disk_match_never_loading_proof(self):
  r=check.inspect([])
  self.assertEqual(r['state'],'DISK_MATCH')
  self.assertEqual(r['host_loading'],'NOT_VERIFIED')
  self.assertEqual(r['enforcement'],'NOT_VERIFIED')
 def test_paths_resolve_package_skills_or_rule_maker(self):
  for p in (ROOT,ROOT/'skills',ROOT/'skills/rule-maker'):
   self.assertEqual(check.skill_root(p),ROOT/'skills')
 def test_repeated_identical_path_not_duplicate(self):
  r=check.inspect([ROOT,ROOT/'skills'])
  self.assertEqual(r['state'],'DISK_MATCH')
 def test_distinct_copies_warn_even_if_identical(self):
  with tempfile.TemporaryDirectory() as d:
   new=Path(d)/'copy';shutil.copytree(ROOT/'skills',new,ignore=shutil.ignore_patterns('__pycache__'))
   r=check.inspect([ROOT,new]);self.assertTrue(r['multiple_copies'])
   self.assertEqual(r['state'],'WARNING')
 def test_mixed_install_detected_even_with_current_label(self):
  with tempfile.TemporaryDirectory() as d:
   new=Path(d)/'skills';shutil.copytree(ROOT/'skills',new,ignore=shutil.ignore_patterns('__pycache__'))
   (new/'rule-maker/rules/design.md').write_text('older rules')
   (new/'ui-design/KIT.md').unlink()
   r=check.inspect([new]);row=r['candidates'][0]
   self.assertEqual(row['state'],'DRIFT')
   self.assertIn('rule-maker/rules/design.md',row['changed'])
   self.assertIn('ui-design/KIT.md',row['missing'])
 def test_symlink_candidate_rejected(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/'linked'
   try:p.symlink_to(ROOT,target_is_directory=True)
   except OSError:self.skipTest('Symlinks unavailable')
   with self.assertRaises(ValueError):check.inspect([p])
 def test_nonexistent_candidate_blocked(self):
  with tempfile.TemporaryDirectory() as d:
   with self.assertRaises(ValueError):check.inspect([Path(d)/'missing'])
 def test_check_global_missing_never_writes(self):
  with tempfile.TemporaryDirectory() as d:
   result=subprocess.run([sys.executable,str(ROOT/'skills/rule-maker/scripts/audit_installation.py'),'--check-global','--home',d,'--claude-dir',d+'/claude','--codex-home',d+'/codex'],capture_output=True,text=True)
   self.assertEqual(result.returncode,1,result.stdout+result.stderr)
   self.assertEqual(list(Path(d).iterdir()),[])
   self.assertEqual(json.loads(result.stdout)['host_loading'],'NOT_VERIFIED')

class NewFrameworkTests(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.addCleanup(self.tmp.cleanup)
  self.root=Path(self.tmp.name)
 def put(self,path,value):
  p=self.root/path;p.parent.mkdir(parents=True,exist_ok=True)
  p.write_text(json.dumps(value) if isinstance(value,dict) else value)
 def test_angular_ionic_capacitor_detected_without_execution(self):
  self.put('package.json',{'dependencies':{'@angular/core':'20.3.0','@ionic/angular':'8.0.0','@capacitor/core':'8.0.0','@capacitor/camera':'8.0.0'}})
  self.put('angular.json',{})
  self.put('capacitor.config.ts','throw new Error("must never run")')
  r=versions.inspect_versions(self.root,['src']);c=r['contexts'][0]
  modules={p['module'] for p in c['packages']}
  self.assertEqual(modules,{'angular.md','ionic.md','capacitor.md'})
  self.assertFalse(c['configuration_evaluated']);self.assertFalse(r['compatibility_verified'])
  self.assertIn('capacitor.config.ts',r['sources'])
 def test_react_capacitor_does_not_require_ionic(self):
  self.put('package.json',{'dependencies':{'react':'18.3.1','@capacitor/core':'8.0.0'}})
  c=versions.inspect_versions(self.root,['.'])['contexts'][0]
  self.assertEqual({p['module'] for p in c['packages']},{'react.md','capacitor.md'})
 def test_ionic_vue_does_not_claim_angular(self):
  self.put('package.json',{'dependencies':{'@ionic/vue':'8.0.0'}})
  c=versions.inspect_versions(self.root,['.'])['contexts'][0]
  self.assertEqual(c['packages'][0]['module'],'ionic.md')
 def test_separate_angular_versions_remain_separate(self):
  for name,v in [('old','17.3.0'),('new','20.3.0')]:
   self.put(name+'/package.json',{'dependencies':{'@angular/core':v}})
   self.put(name+'/package-lock.json',{'lockfileVersion':3,'packages':{'node_modules/@angular/core':{'version':v}}})
  r=versions.inspect_versions(self.root,['old/src','new/src'])
  self.assertEqual({p['locked'] for c in r['contexts'] for p in c['packages']},{'17.3.0','20.3.0'})
 def test_config_change_invalidates_readiness(self):
  before=readiness.snapshot(self.root,['src'],task='fixture',host='test')
  for name in ('angular.json','ionic.config.json','capacitor.config.ts'):
   self.put(name,'{}')
   after=readiness.snapshot(self.root,['src'],task='fixture',host='test')
   self.assertNotEqual(after['fingerprint'],before['fingerprint']);before=after
 def test_shared_modules_are_routed_and_fingerprinted(self):
  data=json.loads((ROOT/'skills/rule-maker/rules/version.json').read_text())
  start=(ROOT/'skills/rule-maker/rules/START.md').read_text()
  for name in ('angular.md','ionic.md','capacitor.md','POLICY.md','operations.md'):
   self.assertIn(name,start);self.assertIn(name,data['sha256'])
 def test_react_compiler_correction_is_not_upgrade_authority(self):
  text=(ROOT/'skills/rule-maker/rules/react.md').read_text()
  self.assertIn('not inherently React-19-only',text)
  self.assertIn('does not authorise',text)
 def test_full_audit_is_not_task_readiness(self):
  text=(ROOT/'skills/rule-maker/AUDIT.md').read_text()
  for term in ('memory','coverage','Installed','readiness'):
   self.assertIn(term.lower(),text.lower())
  self.assertIn('full requested rules scope',(ROOT/'skills/rule-maker/SKILL.md').read_text())
 def test_shared_policy_preserves_intent_and_real_proof(self):
  text=(ROOT/'skills/rule-maker/rules/POLICY.md').read_text()
  self.assertIn('current valid policy',text);self.assertIn('silence',text)
  ops=(ROOT/'skills/rule-maker/rules/operations.md').read_text()
  self.assertIn('A rule that requires GREEN is not evidence',ops)
  self.assertIn('production mutation',ops);self.assertIn('quiet-host',ops)
 def test_kit_templates_do_not_invent_approved_style(self):
  data=json.loads((ROOT/'skills/ui-design/templates/design-kit.json').read_text())
  self.assertEqual(data['items'],[]);self.assertEqual(data['status'],'draft')
  text=(ROOT/'skills/ui-design/KIT.md').read_text()
  self.assertIn('not** ship an approved application theme',text)
  self.assertIn('not separate installed skills',text)

class LiveCaseContractTests(unittest.TestCase):
 def test_authored_cases_never_claim_execution(self):
  data=json.loads((ROOT/'tests/behavioral/rules-audit-kit.json').read_text())
  self.assertEqual(data['candidate_version'],json.loads((ROOT/'.claude-plugin/plugin.json').read_text())['version'])
  self.assertEqual(data['status'],'AUTHORED_NOT_RUN')
  self.assertEqual(len(data['cases']),30)
  self.assertEqual(len({c['id'] for c in data['cases']}),30)
  for case in data['cases']:
   self.assertEqual(case['result'],'NOT_RUN')
   self.assertTrue(case['prompt'] and case['expected'] and case['preparation'])

if __name__=='__main__':unittest.main()
