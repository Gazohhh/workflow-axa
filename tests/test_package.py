from __future__ import annotations

import json
import shutil
import tempfile
import unittest
from pathlib import Path

from tools.validate import ROOT, validate_package


class PackageTests(unittest.TestCase):
    def test_current_package(self):
        self.assertEqual(validate_package(ROOT), [])

    def copy_package(self, destination: Path) -> Path:
        return Path(shutil.copytree(ROOT, destination,
                    ignore=shutil.ignore_patterns(".git", "__pycache__", ".artifacts", ".local-fixtures")))

    def test_missing_reference_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.copy_package(Path(tmp) / "candidate")
            (root / "skills/workflow/GROUNDING.md").unlink()
            self.assertTrue(any("GROUNDING.md" in error for error in validate_package(root)))

    def test_unregistered_extra_skill_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.copy_package(Path(tmp) / "candidate")
            second = root / "skills/duplicate/SKILL.md"
            second.parent.mkdir()
            second.write_text("---\nname: duplicate\n---\n", encoding="utf-8")
            self.assertIn("Exactly the 20 SKILL.md files plugin.json registers are required.", validate_package(root))

    def test_malformed_skill_entries_fail_before_any_path_is_read(self):
        cases = {"/etc/passwd": "is not ./skills/<name>", "./skills/../../outside": "is not ./skills/<name>",
                 "C:/Windows": "is not ./skills/<name>", 7: "is not ./skills/<name>", None: "is not ./skills/<name>",
                 "./skills/workflow": "more than once"}
        with tempfile.TemporaryDirectory() as tmp:
            root = self.copy_package(Path(tmp) / "candidate")
            path = root / ".claude-plugin/plugin.json"
            original = json.loads(path.read_text(encoding="utf-8"))
            for entry, message in cases.items():
                with self.subTest(entry=entry):
                    data = dict(original, skills=original["skills"] + [entry])
                    path.write_text(json.dumps(data), encoding="utf-8")
                    errors = validate_package(root)
                    self.assertTrue(any(message in e for e in errors), errors)
                    self.assertFalse(any("Missing required file: skills/" in e for e in errors), errors)
            path.write_text(json.dumps(dict(original, skills=[])), encoding="utf-8")
            self.assertIn("plugin.json must register its skills as a non-empty list.", validate_package(root))

    def test_a_new_skill_needs_only_its_folder_its_manifest_entry_and_the_stated_counts(self):
        """G2: no validator edit. The only remaining errors are the docs that state the skill count."""
        with tempfile.TemporaryDirectory() as tmp:
            root = self.copy_package(Path(tmp) / "candidate")
            folder = root / "skills/dummy"
            (folder / "agents").mkdir(parents=True)
            (folder / "SKILL.md").write_text('---\nname: dummy\ndescription: "A dummy skill."\n---\n\n# Dummy\n',
                                             encoding="utf-8")
            (folder / "agents/openai.yaml").write_text('interface:\n  display_name: "Dummy"\n'
                                                       '  short_description: "A dummy skill."\n', encoding="utf-8")
            path = root / ".claude-plugin/plugin.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            data["skills"].append("./skills/dummy")
            path.write_text(json.dumps(data), encoding="utf-8")
            errors = validate_package(root)
            self.assertTrue(errors)
            self.assertTrue(all("states 20 skills" in error for error in errors), errors)

    def test_version_without_changelog_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.copy_package(Path(tmp) / "candidate")
            path = root / ".claude-plugin/plugin.json"
            data = json.loads(path.read_text(encoding="utf-8"))
            data["version"] = "99.0.0"
            path.write_text(json.dumps(data), encoding="utf-8")
            self.assertIn("Plugin version has no matching changelog entry.", validate_package(root))

    def test_broken_relative_link_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.copy_package(Path(tmp) / "candidate")
            with (root / "README.md").open("a", encoding="utf-8") as stream:
                stream.write("\n[Missing reference](missing-reference.md)\n")
            self.assertTrue(any("missing-reference.md" in error for error in validate_package(root)))

    def test_link_outside_package_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.copy_package(Path(tmp) / "candidate")
            (Path(tmp) / "outside.md").write_text("exists but is not bundled", encoding="utf-8")
            with (root / "README.md").open("a", encoding="utf-8") as stream:
                stream.write("\n[Outside](../outside.md)\n")
            self.assertTrue(any("outside.md" in error for error in validate_package(root)))

    def test_skill_references_are_self_contained(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.copy_package(Path(tmp) / "candidate")
            with (root / "skills/workflow/SKILL.md").open("a", encoding="utf-8") as stream:
                stream.write("\n[Not bundled with a direct skill copy](../../README.md)\n")
            self.assertTrue(any("escapes the separately installable" in error for error in validate_package(root)))

    def test_local_flowchart_guide_is_required(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.copy_package(Path(tmp) / "candidate")
            (root / "skills/codebase-map/FLOWCHART-DESIGN.md").unlink()
            self.assertTrue(any("FLOWCHART-DESIGN.md" in error for error in validate_package(root)))

    def test_retired_external_design_adapter_is_not_shipped(self):
        compat = (ROOT / "skills/codebase-map/DIAGRAM-DESIGN.md").read_text(encoding="utf-8")
        self.assertIn("Compatibility pointer", compat)
        self.assertIn("[FLOWCHART-DESIGN.md](FLOWCHART-DESIGN.md)", compat)
        self.assertNotIn("npx skills add", compat)
        self.assertNotIn("--only diagram-design", compat)
        self.assertFalse((ROOT / "skills/diagram-design").exists())
        self.assertFalse((ROOT / "skills/workflow/METHODS.md").exists())

    def test_visual_skill_loads_local_guide_and_preserves_style(self):
        core = (ROOT / "skills/codebase-map/SKILL.md").read_text(encoding="utf-8")
        guide = (ROOT / "skills/codebase-map/FLOWCHART-DESIGN.md").read_text(encoding="utf-8")
        self.assertIn("[FLOWCHART-DESIGN.md](FLOWCHART-DESIGN.md)", core)
        self.assertIn("no external diagram skill installation, lookup or invocation is required", core)
        for term in ("workflow-editorial-v1", "#f5f5f5", "#2d3142", "#bf4520",
                     "18px", "13px", "diamond", "grilling", "user approval"):
            self.assertIn(term, guide)

    def test_external_design_install_commands_are_not_active_setup(self):
        for name in ("README.md", "skills/workflow/SETUP.md", "skills/codebase-map/SKILL.md",
                     "skills/codebase-map/REPORT.md", "skills/workflow/templates/PROJECT-ROUTING.md"):
            text = (ROOT / name).read_text(encoding="utf-8")
            self.assertNotIn("npx skills add https://github.com/cathrynlavery", text, name)
            self.assertNotIn("--only diagram-design", text, name)
            self.assertNotIn("codebase-map → diagram-design", text, name)

    def test_registered_utility_skills_exist_and_are_bounded(self):
        plugin = json.loads((ROOT / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))
        self.assertEqual(plugin["version"], json.loads((ROOT / "skills/rule-maker/rules/version.json").read_text())["package_version"])
        for name in ("resume", "plan-review"):  # T21: task-status, resume-task and workflow-doctor merged
            self.assertIn(f"./skills/{name}", plugin["skills"])
            text=(ROOT/f"skills/{name}/SKILL.md").read_text(encoding="utf-8")
            self.assertIn("---", text)
        self.assertIn("no edits of any kind", (ROOT/"skills/resume/SKILL.md").read_text(encoding="utf-8").lower())
        self.assertIn("do not implement", (ROOT/"skills/plan-review/SKILL.md").read_text(encoding="utf-8").lower())
        self.assertIn("without changing", (ROOT/"skills/rule-maker/DIAGNOSE.md").read_text(encoding="utf-8").lower())

    def test_explain_and_anti_slop_contracts_are_explicit(self):
        workflow=(ROOT/"skills/workflow/SKILL.md").read_text(encoding="utf-8")
        map_skill=(ROOT/"skills/codebase-map/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("necessity check", workflow)
        self.assertIn("domain-modeling", workflow)
        self.assertIn("cold-reader check", workflow)
        self.assertIn("**explain**", map_skill)
        self.assertIn("do not create a plan", map_skill)

    def test_modified_shared_module_fingerprint_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.copy_package(Path(tmp) / "candidate")
            with (root / "skills/rule-maker/rules/CORE.md").open("a") as stream:
                stream.write("\nUnreviewed rule edit.\n")
            self.assertTrue(any("fingerprint mismatch" in error for error in validate_package(root)))

    def test_unlisted_shared_module_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.copy_package(Path(tmp) / "candidate")
            (root / "skills/rule-maker/rules/UNREVIEWED.md").write_text("Unreviewed extra module.")
            self.assertTrue(any("each bundled Markdown" in error for error in validate_package(root)))

    def test_duplicate_shared_manifest_entry_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.copy_package(Path(tmp) / "candidate")
            p = root / "skills/rule-maker/rules/version.json"
            data = json.loads(p.read_text()); data["files"].append("CORE.md")
            p.write_text(json.dumps(data))
            self.assertTrue(any("each bundled Markdown" in error for error in validate_package(root)))

    def test_mixed_rule_package_release_is_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self.copy_package(Path(tmp) / "candidate")
            p = root / "skills/rule-maker/rules/version.json"
            data = json.loads(p.read_text()); data["package_version"] = "99.0.0"
            p.write_text(json.dumps(data))
            self.assertTrue(any("package version must match" in error for error in validate_package(root)))


if __name__ == "__main__":
    unittest.main()
