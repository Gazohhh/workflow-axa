"""The package's essentials, listed here independently of plugin.json, hooks.json and tools/validate.py.

tools/validate.py derives the registered skills from plugin.json (REDESIGN.md §11, G2/G5), so deleting a skill and its
manifest entry together would still validate. This suite keeps an explicit list, so such a deletion fails here. A ticket
that adds, removes or renames one of these items updates this file in the same change.
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

EXPECTED_SKILLS = (
    "workflow", "codebase-map", "resume", "plan-review", "rule-maker",
    "ui-design", "workflow-clarify", "workflow-specify", "workflow-execute", "workflow-deliver", "grilling", "tdd",
    "code-review", "writing-for-agents", "codebase-design", "domain-modeling",
    "interrogate", "no-comments", "wait-what",  # T23
)
# (event, hook script) pairs hooks/hooks.json registers.
EXPECTED_HOOKS = {
    ("SessionStart", "duplicate_skills.py"), ("PreToolUse", "approval.py"), ("PostToolUse", "phase_gate.py"),
    ("UserPromptSubmit", "phase_gate.py"),  # T20: plain_reply, phase_reads, truncated_read removed
}
# Each formerly copied skill keeps its LICENSE: the licence requires the notice to travel with the text (AGENTS.md).
# T22: implement-spec and retro are archived (not shipped); simple-english's licence ships as
# skills/workflow/SIMPLE-ENGLISH.LICENSE (KEY_FILES). test_owned_skills checks the archive copies.
LICENSED = ("grilling", "tdd", "code-review", "writing-for-agents", "codebase-design", "domain-modeling")
RENDERER = (
    "skills/codebase-map/scripts/render_report.py", "skills/codebase-map/scripts/task_report.py",
    "skills/codebase-map/scripts/screen_flow.py", "skills/codebase-map/assets/report.css",
    "skills/codebase-map/assets/report.js", "skills/codebase-map/assets/report-style.css",
    "skills/codebase-map/assets/report-style-compat.css", "skills/codebase-map/assets/report-extra.js",
    "skills/codebase-map/assets/task-report.css", "skills/codebase-map/assets/ui-review.css",
    "skills/codebase-map/assets/ui-review.js", "skills/codebase-map/examples/review.json",
    "skills/codebase-map/examples/review.html",
)
KEY_TESTS = (
    "tests/test_package.py", "tests/test_package_contract.py", "tests/test_phase_gate_hook.py",
    "tests/test_gate_regressions.py", "tests/test_session_failures.py", "tests/test_record.py",
    "tests/test_rules.py", "tests/test_reports.py", "tests/test_task_report.py", "tests/test_ui_design.py",
    "tests/test_owned_skills.py", "tests/test_validate_budgets.py", "tests/test_docs_check.py", "tests/test_required_reads.py", "tests/test_flows.py", "tests/test_settings.py", "tests/test_offers.py", "tests/test_approval_hook.py", "tests/test_completion_check.py", "tests/test_cutover.py",
)
KEY_FILES = (
    "AGENTS.md", "CONTEXT.md", "README.md", "CHANGELOG.md", "UPGRADE.md", "VALIDATION.md", "VENDORED-SKILLS.md",
    "docs/ARCHITECTURE.md", "docs/RULE-CONTRACTS.md", "tests/README.md", "tools/validate.py",
    "skills/interrogate/scripts/snapshot.py",  # T23
    "skills/workflow/scripts/record.py", "skills/workflow/scripts/global_policy.py",
    "skills/rule-maker/rules/START.md", "skills/rule-maker/rules/CORE.md", "skills/rule-maker/rules/READINESS.md",
    "skills/rule-maker/rules/DESIGN.md", "skills/rule-maker/rules/version.json",
    "tools/digest_sessions.py", "skills/workflow/SIMPLE-ENGLISH.md", "skills/workflow/SIMPLE-ENGLISH.LICENSE", "skills/rule-maker/scripts/required_reads.py", "skills/workflow/flows/INDEX.md", "skills/workflow/FALLBACKS.md", "skills/workflow/scripts/settings.py", "skills/workflow/scripts/offers.py", "hooks/approval.py", "hooks/read_evidence.py", "skills/workflow-deliver/scripts/completion_check.py", "skills/workflow/scripts/legacy_inventory.py", "skills/workflow/flows/TEMPLATE.md",
    "skills/code-review/BLAST-RADIUS.md", "skills/code-review/BLAST-RADIUS.LICENSE", "skills/workflow/UNSLOP.LICENSE",
)


class PackageContract(unittest.TestCase):

    def test_plugin_registers_exactly_the_expected_skills(self):
        entries = json.loads((ROOT / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))["skills"]
        self.assertEqual(sorted(entries), sorted(f"./skills/{name}" for name in EXPECTED_SKILLS))

    def test_each_expected_skill_has_its_files(self):
        for name in EXPECTED_SKILLS:
            with self.subTest(skill=name):
                self.assertTrue((ROOT / f"skills/{name}/SKILL.md").is_file())
                self.assertTrue((ROOT / f"skills/{name}/agents/openai.yaml").is_file())

    def test_hook_registrations_and_their_scripts(self):
        data = json.loads((ROOT / "hooks/hooks.json").read_text(encoding="utf-8"))["hooks"]
        found = set()
        for event, groups in data.items():
            for group in groups:
                for hook in group["hooks"]:
                    script = hook["command"].split("/hooks/", 1)[1].split('"', 1)[0]
                    found.add((event, script))
                    self.assertTrue((ROOT / "hooks" / script).is_file(), script)
        self.assertEqual(found, EXPECTED_HOOKS)

    def test_licences_travel_with_the_formerly_copied_skills(self):
        for name in LICENSED:
            with self.subTest(skill=name):
                self.assertTrue((ROOT / f"skills/{name}/LICENSE").is_file())
                self.assertIn(name, (ROOT / "VENDORED-SKILLS.md").read_text(encoding="utf-8"))

    def test_renderer_assets_key_tests_and_key_files_exist(self):
        for rel in RENDERER + KEY_TESTS + KEY_FILES:
            with self.subTest(path=rel):
                self.assertTrue((ROOT / rel).is_file(), rel)


class ContractCatchesDeletions(unittest.TestCase):
    """Acceptance of T4: a deletion that the manifests absorb still fails this suite."""

    def run_contract(self, change) -> int:
        import shutil, subprocess, sys, tempfile
        with tempfile.TemporaryDirectory() as tmp:
            copy = Path(shutil.copytree(ROOT, Path(tmp) / "pkg", ignore=shutil.ignore_patterns(
                ".git", "__pycache__", ".artifacts", ".local-fixtures", "dist", "plans", "archive")))
            change(copy)
            return subprocess.run([sys.executable, "-X", "utf8", "-m", "unittest", "test_package_contract.PackageContract"],
                                  cwd=copy / "tests", capture_output=True).returncode

    def test_the_unchanged_copy_passes(self):
        self.assertEqual(self.run_contract(lambda copy: None), 0)

    def test_deleting_a_key_test_fails(self):
        self.assertNotEqual(self.run_contract(lambda copy: (copy / "tests/test_record.py").unlink()), 0)

    def test_deleting_a_skill_with_its_manifest_entry_fails(self):
        def drop(copy):
            import shutil
            shutil.rmtree(copy / "skills/plan-review")
            path = copy / ".claude-plugin/plugin.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            data["skills"].remove("./skills/plan-review")
            path.write_text(json.dumps(data), encoding="utf-8")
        self.assertNotEqual(self.run_contract(drop), 0)


if __name__ == "__main__":
    unittest.main()
