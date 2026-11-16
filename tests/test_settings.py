"""The machine settings file and its one reader (T12 of docs/plans/2026-11-15-workflow-redesign, contract C-CSS-1)."""
from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/workflow/scripts/settings.py"
spec = importlib.util.spec_from_file_location("workflow_axa_settings", SCRIPT)
settings = importlib.util.module_from_spec(spec)
spec.loader.exec_module(settings)


class SettingsTests(unittest.TestCase):

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.dir = Path(tmp.name)
        self.file = self.dir / ".workflow-axa" / "settings.json"
        self.project = self.dir / "project"
        self.project.mkdir()

    def put(self, text):
        self.file.parent.mkdir(parents=True, exist_ok=True)
        self.file.write_text(text, encoding="utf-8")

    def cli(self, *args):
        return subprocess.run([sys.executable, "-X", "utf8", "-I", str(SCRIPT), "--file", str(self.file), *args],
                              capture_output=True, text=True, encoding="utf-8")

    def test_missing_invalid_or_unknown_means_off(self):
        self.assertEqual(settings.read(self.file), {"css": "off"})
        for text in ("not json", "[]", '"on"', '{"css": "ON"}', '{"css": true}', '{"css": "yes"}', '{}'):
            with self.subTest(text=text):
                self.put(text)
                self.assertEqual(settings.read(self.file)["css"], "off")
        self.put('{"css": "on"}')
        self.assertEqual(settings.read(self.file)["css"], "on")

    def test_a_project_can_only_be_stricter(self):
        self.put('{"css": "on"}')
        self.assertTrue(settings.css_allowed(self.project, self.file))
        (self.project / "DESIGN.md").write_text("# Design\n\n- css: never\n", encoding="utf-8")
        self.assertFalse(settings.css_allowed(self.project, self.file))
        self.put('{"css": "off"}')
        (self.project / "DESIGN.md").write_text("# Design\n\ncss: on\n", encoding="utf-8")  # a repo can't turn it on
        self.assertFalse(settings.css_allowed(self.project, self.file))

    def test_css_never_in_a_code_block_or_docs_folder(self):
        self.put('{"css": "on"}')
        (self.project / "DESIGN.md").write_text("Example:\n\n```\ncss: never\n```\n\nand `css: never` inline\n",
                                                encoding="utf-8")
        self.assertTrue(settings.css_allowed(self.project, self.file))  # examples don't count
        (self.project / "docs").mkdir()
        (self.project / "docs/DESIGN.md").write_text("css: never\n", encoding="utf-8")
        self.assertFalse(settings.css_allowed(self.project, self.file))

    def test_an_unreadable_file_never_allows_styling(self):
        from unittest import mock
        real = Path.read_text
        self.put('{"css": "on"}')
        for rel in ("DESIGN.md", "docs/DESIGN.md"):
            with self.subTest(project_design=rel):
                (self.project / rel).parent.mkdir(exist_ok=True)
                (self.project / rel).write_text("# Design\n", encoding="utf-8")
                self.assertTrue(settings.css_allowed(self.project, self.file))
                broken = self.project / rel
                with mock.patch.object(Path, "read_text", lambda p, *a, **k: (_ for _ in ()).throw(PermissionError())
                                       if p == broken else real(p, *a, **k)):
                    self.assertFalse(settings.css_allowed(self.project, self.file))
                broken.unlink()
        with mock.patch.object(Path, "read_text", lambda p, *a, **k: (_ for _ in ()).throw(PermissionError())
                               if p == self.file else real(p, *a, **k)):
            self.assertEqual(settings.read(self.file)["css"], "off")  # unreadable machine settings
            self.assertFalse(settings.css_allowed(self.project, self.file))

    def test_set_keeps_other_keys_and_init_never_overwrites(self):
        self.assertEqual(self.cli("init").returncode, 0)
        self.assertEqual(json.loads(self.file.read_text(encoding="utf-8")), {"css": "off"})
        self.put('{"css": "on", "future": 1}')
        self.assertIn("KEPT", self.cli("init").stdout)
        self.assertEqual(json.loads(self.file.read_text(encoding="utf-8")), {"css": "on", "future": 1})
        self.assertEqual(self.cli("css", "off").returncode, 0)
        self.assertEqual(json.loads(self.file.read_text(encoding="utf-8")), {"css": "off", "future": 1})
        self.assertNotEqual(self.cli("css", "maybe").returncode, 0)

    def test_show_reports_the_effective_setting(self):
        self.put('{"css": "on"}')
        out = json.loads(self.cli("show", "--root", str(self.project)).stdout)
        self.assertEqual((out["css"], out["css_allowed_here"], out["project_css_never"]), ("on", True, False))

    def test_no_other_code_parses_the_settings_file(self):
        """One reader: the hooks and record.py import this module instead of reading the file themselves."""
        for path in [*(ROOT / "hooks").glob("*.py"), *(ROOT / "skills").rglob("*.py")]:
            if path == SCRIPT:
                continue
            with self.subTest(file=path.name):
                text = path.read_text(encoding="utf-8")
                self.assertFalse("settings.json" in text and "json.load" in text and "css" in text, path)


if __name__ == "__main__":
    unittest.main()
