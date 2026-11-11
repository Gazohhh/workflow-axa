"""docs_check.py reports the structure of a repository's instruction files and documentation index (D1).

Every fixture repository is built in a temporary folder, so its deliberately broken links never reach the
package validator or an agent's folder walk.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills/rule-maker/scripts/docs_check.py"


class Fixture(unittest.TestCase):
    """A temporary repository and the script run on it."""

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "repo"
        self.root.mkdir()

    def write(self, files: dict[str, str]) -> Path:
        for name, text in files.items():
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8")
        return self.root

    def run_script(self, *args: str) -> subprocess.CompletedProcess:
        return subprocess.run([sys.executable, "-X", "utf8", "-I", str(SCRIPT), *args],
                              capture_output=True, text=True, encoding="utf-8")

    def check(self, files: dict[str, str] | None = None, exit_code: int = 0) -> dict:
        if files:
            self.write(files)
        result = self.run_script(str(self.root), "--json")
        self.assertEqual(result.returncode, exit_code, result.stdout + result.stderr)
        return json.loads(result.stdout)

    def codes(self, report: dict) -> list[str]:
        return [f["code"] for f in report["findings"]]

    def finding(self, report: dict, code: str) -> dict:
        found = [f for f in report["findings"] if f["code"] == code]
        self.assertTrue(found, (code, report["findings"]))
        return found[0]


class DocsCheckTests(Fixture):
    def test_missing_agents_is_a_warning(self):
        report = self.check({"README.md": "# Project\n"})
        found = self.finding(report, "no-agents")
        self.assertEqual(found["severity"], "warning")
        self.assertEqual(found["path"], "AGENTS.md")

    def test_link_to_a_renamed_file_is_broken(self):
        report = self.check({
            "AGENTS.md": "# Rules\n\nRead [setup](docs/setup.md) first.\n",
            "docs/install.md": "# Install\n",
        })
        found = self.finding(report, "broken-link")
        self.assertEqual((found["severity"], found["path"], found["line"]), ("warning", "AGENTS.md", 3))
        self.assertIn("docs/setup.md", found["message"])

    def test_link_escaping_the_root_is_broken(self):
        (self.root.parent / "outside.md").write_text("# Outside\n", encoding="utf-8")
        report = self.check({"AGENTS.md": "# Rules\n\nSee [outside](../outside.md).\n"})
        self.assertEqual(self.finding(report, "broken-link")["line"], 3)
        self.assertNotIn("../outside.md", report["reached"])

    def test_symlink_out_of_the_root_is_not_followed(self):
        outside = self.root.parent / "outside.md"
        outside.write_text("# Outside\n\nSee [more](more.md).\n", encoding="utf-8")
        (self.root / "docs").mkdir()
        try:
            (self.root / "docs/linked.md").symlink_to(outside)
        except OSError as error:
            self.skipTest(f"file symlinks unavailable: {error}")
        report = self.check({"AGENTS.md": "# Rules\n\nSee [linked](docs/linked.md).\n"})
        self.assertEqual(self.finding(report, "broken-link")["path"], "AGENTS.md")
        self.assertEqual(report["reached"], ["AGENTS.md"])

    def test_broken_link_inside_history_is_a_note(self):
        report = self.check({
            "AGENTS.md": f"# Rules\n\n{self.MARKER}\n\n[Plan](docs/plans/task/PLAN.md) and [Old](docs/archive/OLD.md)\n",
            "docs/plans/task/PLAN.md": "# Plan\n\nSee [the old module](../../../src/gone.py).\n",
            "docs/archive/OLD.md": "# Old\n\nRead [tests](../../tests/README.md) first.\n",
        }, exit_code=1)
        broken = sorted((f["severity"], f["path"]) for f in report["findings"] if f["code"] == "broken-link")
        # The missing required-read file still blocks once, at its marker; history links are notes.
        self.assertEqual(broken, [("blocking", "AGENTS.md"), ("note", "docs/plans/task/PLAN.md")])

    def test_text_output_has_one_line_per_finding_and_a_summary(self):
        self.write({"AGENTS.md": "# Rules\n\nRead [setup](docs/setup.md) first.\n", "CLAUDE.md": "@AGENTS.md\n"})
        result = self.run_script(str(self.root))
        self.assertEqual(result.returncode, 0, result.stderr)
        lines = result.stdout.splitlines()
        self.assertTrue(lines[0].startswith("WARNING broken-link AGENTS.md:3 "), lines)
        self.assertRegex(lines[-1], r"0 blocking, 1 warning, 0 note")

    def test_missing_root_is_a_usage_error(self):
        result = self.run_script(str(self.root / "absent"))
        self.assertEqual(result.returncode, 2)

    NESTED = {
        "AGENTS.md": "# Rules\n\n- [Documentation index](docs/README.md): read when you change code.\n",
        "CLAUDE.md": "@AGENTS.md\n",
        "docs/README.md": "# Docs\n\n- [Architecture](architecture.md#layers)\n- <https://example.com/guide>\n"
                          "- [Top](#docs) and [mail](mailto:team@example.com)\n",
        "docs/architecture.md": "# Architecture\n\nSee the [source](../src/) and [this section](architecture.md#x).\n",
        "src/app.py": "print('hi')\n",
    }

    def test_clean_nested_index_has_no_warning(self):
        report = self.check(self.NESTED)
        self.assertEqual(report["reached"], ["AGENTS.md", "CLAUDE.md", "docs/README.md", "docs/architecture.md"])
        self.assertEqual([f for f in report["findings"] if f["severity"] != "note"], [])

    def test_broken_link_in_a_nested_document_is_found(self):
        files = dict(self.NESTED)
        files["docs/architecture.md"] = "# Architecture\n\nSee [layers](layers.md).\n"
        found = self.finding(self.check(files), "broken-link")
        self.assertEqual((found["path"], found["line"]), ("docs/architecture.md", 3))

    def test_index_linking_back_to_an_index_on_the_path_is_a_cycle_note(self):
        # An index document links two or more other documents; index A -> index B -> index A is a cycle.
        report = self.check({
            "AGENTS.md": "# Rules\n\n[Docs](docs/README.md)\n",
            "docs/README.md": "# Docs\n\n[Guides](guide/README.md) and [terms](terms.md)\n",
            "docs/terms.md": "# Terms\n",
            "docs/guide/README.md": "# Guides\n\n[Start](start.md)\n\nUp to [the docs](../README.md).\n",
            "docs/guide/start.md": "# Start\n",
        })
        found = self.finding(report, "index-cycle")
        self.assertEqual((found["severity"], found["path"], found["line"]), ("note", "docs/guide/README.md", 5))
        self.assertIn("docs/README.md -> docs/guide/README.md -> docs/README.md", found["message"])
        self.assertEqual(self.codes(report).count("index-cycle"), 1)

    # A topical document: several lines of prose, so a link or two does not make it an index.
    BODY = "Context: the decision and its reasons.\n\nDecision: what we do.\n\nConsequences: what follows.\n\n"

    def test_cycle_through_an_exempt_folder_is_not_reported(self):
        report = self.check({
            "AGENTS.md": "# Rules\n\n[Docs](docs/README.md)\n",
            "docs/README.md": "# Docs\n\n[Old work](plans/before/README.md)\n",
            "docs/plans/before/README.md": "# Before\n\n[Plan](plan.md)\n\nBack to [the docs](../../README.md).\n",
            "docs/plans/before/plan.md": "# Plan\n",
        })
        self.assertNotIn("index-cycle", self.codes(report))

    def test_topical_documents_linking_each_other_are_not_a_cycle(self):
        prose = "".join(f"Paragraph {n} explains one rule of the access model in plain words.\n\n" for n in range(8))
        report = self.check({
            "AGENTS.md": "# Rules\n\n[Docs](docs/README.md)\n",
            "docs/README.md": "# Docs\n\n- [Access](access.md)\n- [Lock](lock.md)\n",
            "docs/access.md": f"# Access\n\n{prose}See [the lock](lock.md) and [terms](terms.md).\n",
            "docs/lock.md": f"# Lock\n\n{prose}See [access](access.md) and [terms](terms.md).\n",
            "docs/terms.md": "# Terms\n",
        })
        self.assertNotIn("index-cycle", self.codes(report))

    def test_chain_of_short_notes_with_one_link_each_is_not_an_index_chain(self):
        files = {"AGENTS.md": "# Rules\n\n[Start](docs/a.md)\n"}
        for name, following in zip("abcd", "bcda"):
            files[f"docs/{name}.md"] = f"# {name.upper()}\n\nSee [next]({following}.md).\n"
        report = self.check(files)
        self.assertNotIn("index-cycle", self.codes(report))
        self.assertNotIn("index-depth", self.codes(report))

    def test_a_document_that_is_mostly_links_is_an_index(self):
        report = self.check({
            "AGENTS.md": "# Rules\n\n[Map](docs/map.md)\n",
            "docs/map.md": "# Map\n\n- [Guides](guides.md)\n- [Terms](terms.md)\n",
            "docs/guides.md": "# Guides\n\n- [Start](start.md)\n- [Back to the map](map.md)\n",
            "docs/start.md": "# Start\n", "docs/terms.md": "# Terms\n",
        })
        found = self.finding(report, "index-cycle")
        self.assertIn("docs/map.md -> docs/guides.md -> docs/map.md", found["message"])

    def test_back_links_to_an_entry_or_from_a_plain_document_are_not_cycles(self):
        report = self.check({
            "AGENTS.md": "# Rules\n\n[Design](DESIGN.md) and [docs](docs/README.md)\n",
            "DESIGN.md": "# Design\n\nRead [the rules](AGENTS.md) and [the product](PRODUCT.md) first.\n",
            "PRODUCT.md": "# Product\n",
            "docs/README.md": "# Docs\n\n[ADR 1](adr/0001.md) and [ADR 2](adr/0002.md)\n",
            "docs/adr/0001.md": f"# ADR 1\n\n{self.BODY}Back to [the index](../README.md).\n",
            "docs/adr/0002.md": f"# ADR 2\n\n{self.BODY}Supersedes [ADR 1](0001.md).\n",
        })
        self.assertNotIn("index-cycle", self.codes(report))

    def test_document_reached_only_at_level_three_is_a_depth_note(self):
        # Levels count index documents: AGENTS.md (0) -> docs/README.md (1) -> docs/b/README.md (2) -> docs/c/*.md (3).
        report = self.check({
            "AGENTS.md": "# Rules\n\n[Docs](docs/README.md) and [shortcut](docs/c/linked-from-root.md)\n",
            "docs/README.md": "# Docs\n\n[B](b/README.md) and [terms](terms.md)\n",
            "docs/terms.md": "# Terms\n",
            "docs/b/README.md": "# B\n\n[C](../c/README.md) and [the shortcut](../c/linked-from-root.md)\n",
            "docs/c/README.md": "# C\n",
            "docs/c/linked-from-root.md": "# Also linked from the root\n",
        })
        notes = [f for f in report["findings"] if f["code"] == "index-depth"]
        self.assertEqual([(f["severity"], f["path"]) for f in notes], [("note", "docs/c/README.md")])
        self.assertIn("3", notes[0]["message"])

    def test_deep_documents_in_exempt_folders_get_no_depth_note(self):
        report = self.check({
            "AGENTS.md": "# Rules\n\n[Docs](docs/README.md)\n",
            "docs/README.md": "# Docs\n\n[Plans](plans/README.md)\n",
            "docs/plans/README.md": "# Plans\n\n[Task](task/README.md)\n",
            "docs/plans/task/README.md": "# Task\n\n[Plan](PLAN.md)\n",
            "docs/plans/task/PLAN.md": "# Plan\n",
        })
        self.assertIn("docs/plans/task/PLAN.md", report["reached"])
        self.assertNotIn("index-depth", self.codes(report))

    def test_links_between_plain_documents_add_no_level(self):
        report = self.check({
            "AGENTS.md": "# Rules\n\n[Decisions](docs/adr/README.md)\n",
            "docs/adr/README.md": "# Decisions\n\n[ADR 1](0001.md) and [ADR 2](0002.md)\n",
            "docs/adr/0001.md": f"# ADR 1\n\n{self.BODY}See [ADR 3](0003.md).\n",
            "docs/adr/0002.md": "# ADR 2\n",
            "docs/adr/0003.md": f"# ADR 3\n\n{self.BODY}See [ADR 4](0004.md).\n",
            "docs/adr/0004.md": "# ADR 4\n",
        })
        self.assertNotIn("index-depth", self.codes(report))
        self.assertIn("docs/adr/0004.md", report["reached"])

    def test_agents_over_1200_words_is_a_size_warning(self):
        report = self.check({"AGENTS.md": "# Rules\n\n" + "word " * 1199 + "\n"})  # 1,201 words with the heading
        found = self.finding(report, "agents-size")
        self.assertEqual((found["severity"], found["path"]), ("warning", "AGENTS.md"))
        self.assertIn("1201", found["message"].replace(",", ""))

    def test_agents_at_1200_words_has_no_size_warning(self):
        report = self.check({"AGENTS.md": "# Rules\n\n" + "word " * 1198 + "\n"})
        self.assertNotIn("agents-size", self.codes(report))

    def test_claude_that_is_not_the_one_line_import_is_a_warning(self):
        report = self.check({"AGENTS.md": "# Rules\n", "CLAUDE.md": "# Claude\n\nRead AGENTS.md first.\n"})
        found = self.finding(report, "claude-not-import")
        self.assertEqual((found["severity"], found["path"]), ("warning", "CLAUDE.md"))

    def test_nested_claude_beside_a_nested_agents_must_be_the_import(self):
        report = self.check({
            "AGENTS.md": "# Rules\n\n[Web](packages/web/AGENTS.md) and [API](packages/api/AGENTS.md)\n",
            "CLAUDE.md": "@AGENTS.md\n",
            "packages/web/AGENTS.md": "# Web\n", "packages/web/CLAUDE.md": "# Web notes\n\nUse pnpm.\n",
            "packages/api/AGENTS.md": "# API\n", "packages/api/CLAUDE.md": "@AGENTS.md\n",
            "tools/CLAUDE.md": "# Tool notes without an AGENTS.md beside them\n",
        })
        found = [(f["severity"], f["path"]) for f in report["findings"] if f["code"] == "claude-not-import"]
        self.assertEqual(found, [("warning", "packages/web/CLAUDE.md")])

    def test_instruction_files_in_exempt_folders_are_not_checked(self):
        files = {"AGENTS.md": f"# Rules\n\n{self.RULE}\n", "CLAUDE.md": "@AGENTS.md\n"}
        for folder in ("tests/fixtures/project", "examples/app", "docs/plans/task", "archive/v1"):
            files[f"{folder}/AGENTS.md"] = f"# Copy\n\n{self.RULE}\n"
            files[f"{folder}/CLAUDE.md"] = "# Fixture notes\n\nNot an import on purpose.\n"
        report = self.check(files)
        for code in ("claude-not-import", "repeated-paragraph", "claude-duplicates-agents"):
            self.assertNotIn(code, self.codes(report))

    def test_claude_import_with_blank_lines_and_a_comment_is_fine(self):
        report = self.check({"AGENTS.md": "# Rules\n",
                             "CLAUDE.md": "<!-- Claude Code reads\nthis file -->\n\n@AGENTS.md\n\n"})
        self.assertNotIn("claude-not-import", self.codes(report))

    RULE = ("Never commit, push or deploy without the owner's explicit permission, and never install a dependency "
            "or change global settings while a task is running, because other sessions may depend on them.")  # 30 words
    SHORT = "Run the unit tests before every change and report the exact command and its output to the owner."  # 18

    def test_paragraph_repeated_across_instruction_files_is_a_note(self):
        report = self.check({
            "AGENTS.md": f"# Rules\n\n{self.RULE}\n\n{self.SHORT}\n\n- [API package](packages/api/AGENTS.md)\n",
            "packages/api/AGENTS.md": f"# API\n\n{self.RULE.upper()}\n\n{self.SHORT}\n",
            "packages/api/CLAUDE.md": "@AGENTS.md\n\n" + "  ".join(self.RULE.split()) + "\n",
        })
        notes = [f for f in report["findings"] if f["code"] == "repeated-paragraph"]
        self.assertEqual(len(notes), 1, notes)
        self.assertEqual((notes[0]["severity"], notes[0]["path"], notes[0]["line"]), ("note", "AGENTS.md", 3))
        self.assertIn("packages/api/AGENTS.md:3", notes[0]["message"])
        self.assertIn("packages/api/AGENTS.md", report["reached"])
        # The nested CLAUDE.md copies the AGENTS.md beside it: that is its own warning, not part of the note.
        self.assertNotIn("CLAUDE.md", notes[0]["message"])
        copied = self.finding(report, "claude-duplicates-agents")
        self.assertEqual((copied["path"], copied["line"]), ("packages/api/CLAUDE.md", 3))

    def test_claude_repeating_an_agents_paragraph_is_a_warning(self):
        report = self.check({"AGENTS.md": f"# Rules\n\n{self.RULE}\n",
                             "CLAUDE.md": f"@AGENTS.md\n\n# Extra\n\n{self.RULE}\n"})
        found = self.finding(report, "claude-duplicates-agents")
        self.assertEqual((found["severity"], found["path"], found["line"]), ("warning", "CLAUDE.md", 5))
        self.assertIn("AGENTS.md:3", found["message"])
        # The warning already names this pair, so the general note does not repeat it.
        self.assertNotIn("repeated-paragraph", self.codes(report))

    def test_claude_copying_several_paragraphs_gets_one_warning_with_the_count(self):
        second = self.RULE.replace("Never commit", "Always ask before you commit")
        report = self.check({"AGENTS.md": f"# Rules\n\n{self.RULE}\n\n{second}\n",
                             "CLAUDE.md": f"@AGENTS.md\n\n{self.RULE}\n\n{second}\n"})
        found = [f for f in report["findings"] if f["code"] == "claude-duplicates-agents"]
        self.assertEqual(len(found), 1, found)
        self.assertEqual((found[0]["path"], found[0]["line"]), ("CLAUDE.md", 3))
        self.assertIn("2 paragraphs", found[0]["message"])

    def test_documents_nothing_reaches_are_notes(self):
        report = self.check({
            "AGENTS.md": "# Rules\n\n[Docs](docs/README.md)\n",
            ".gitignore": "# build output\ngenerated/\n/out\n*.log\nsite/out\n",
            "out/AGENTS.md": "# Build copy\n",
            "docs/README.md": "# Docs\n",
            "docs/old/orphan.md": "# Orphan\n",
            "docs/plans/2026-01-01-task/PLAN.md": "# Plan\n",
            "docs/archive/AUDIT.md": "# Old\n",
            "docs/generated/api.md": "# Generated\n",
            "packages/web/AGENTS.md": "# Web rules\n",
            "node_modules/lib/AGENTS.md": "# Vendored\n",
            "vendor/lib/AGENTS.md": "# Vendored\n",
            "notes/scratch.md": "# Not under docs, still unreached\n",
        })
        unreached = sorted((f["severity"], f["path"]) for f in report["findings"] if f["code"] == "unreachable-doc")
        self.assertEqual(unreached, [("note", "docs/old/orphan.md"), ("note", "notes/scratch.md"),
                                     ("note", "packages/web/AGENTS.md")])

    def test_dependency_and_build_folders_are_not_searched(self):
        files = {"AGENTS.md": "# Rules\n", "CLAUDE.md": "@AGENTS.md\n"}
        for folder in (".venv/lib", "__pycache__", "dist", "build", "storage/app", "api/node_modules/x"):
            files[f"{folder}/AGENTS.md"] = "# Copied rules\n"
            files[f"{folder}/docs/guide.md"] = "# Copied guide\n"
        report = self.check(files)
        self.assertEqual(report["findings"], [])

    def test_unreached_documents_in_any_docs_folder_are_notes_with_default_exemptions(self):
        report = self.check({
            "AGENTS.md": "# Rules\n\n[API](packages/api/AGENTS.md)\n",
            "packages/api/AGENTS.md": "# API\n",
            "packages/api/docs/guide.md": "# Not linked\n",
            "packages/api/docs/plans/task/PLAN.md": "# Plan\n",
            "packages/api/docs/archive/old.md": "# Old\n",
            "tests/fixtures/project/AGENTS.md": "# Fixture rules\n",
            "examples/docs/sample.md": "# Example\n",
            "docs/fixtures/case.md": "# Fixture\n",
        })
        unreached = [f["path"] for f in report["findings"] if f["code"] == "unreachable-doc"]
        # fixtures and examples are exempt only outside a docs folder, so docs/fixtures is documentation.
        self.assertEqual(unreached, ["docs/fixtures/case.md", "packages/api/docs/guide.md"])

    def test_build_and_examples_inside_docs_are_still_documentation(self):
        report = self.check({
            "AGENTS.md": "# Rules\n\n[Docs](docs/README.md)\n",
            "docs/README.md": "# Docs\n",
            "docs/build/how-to-build.md": "# How to build\n",
            "docs/examples/guide.md": "# Example guide\n",
            "docs/plans/task/PLAN.md": "# Plan\n",
            "build/docs/generated.md": "# Build output\n",
            "examples/docs/sample.md": "# Example\n",
        })
        unreached = sorted(f["path"] for f in report["findings"] if f["code"] == "unreachable-doc")
        self.assertEqual(unreached, ["docs/build/how-to-build.md", "docs/examples/guide.md"])

    def test_non_utf8_files_are_noted_and_skipped(self):
        self.write({"AGENTS.md": "# Rules\n\n[Bad](docs/bad.md) and [good](docs/good.md)\n",
                    "docs/good.md": "# Good\n"})
        (self.root / "docs/bad.md").write_bytes(b"# Caf\xe9\n\n[x](missing.md)\n")
        (self.root / "packages/api").mkdir(parents=True)
        (self.root / "packages/api/CLAUDE.md").write_bytes(b"\xff\xfe@AGENTS.md\n")
        report = self.check()
        unreadable = sorted((f["severity"], f["path"]) for f in report["findings"] if f["code"] == "unreadable-file")
        self.assertEqual(unreadable, [("note", "docs/bad.md"), ("note", "packages/api/CLAUDE.md")])
        self.assertIn("docs/good.md", report["reached"])
        self.assertNotIn("broken-link", self.codes(report))

    def test_non_utf8_agents_is_noted_not_a_crash(self):
        (self.root / "AGENTS.md").write_bytes(b"# R\xe8gles\n")
        self.write({"CLAUDE.md": "@AGENTS.md\n"})
        report = self.check()
        self.assertEqual(self.codes(report), ["unreadable-file"])

    def test_monorepo_package_index_linked_from_the_root_is_clean(self):
        report = self.check({
            "AGENTS.md": "# Rules\n\n- [API package rules](packages/api/AGENTS.md): read when you change the API.\n",
            "CLAUDE.md": "@AGENTS.md\n",
            "packages/api/AGENTS.md": "# API\n\n- [Endpoints](docs/endpoints.md)\n",
            "packages/api/CLAUDE.md": "@AGENTS.md\n",
            "packages/api/docs/endpoints.md": "# Endpoints\n\nSee [the handlers](../src/).\n",
            "packages/api/src/handlers.py": "pass\n",
        })
        self.assertEqual(report["findings"], [])
        self.assertIn("packages/api/docs/endpoints.md", report["reached"])

    def test_undocumented_code_is_not_a_finding(self):
        report = self.check({"AGENTS.md": "# Rules\n", "CLAUDE.md": "@AGENTS.md\n",
                             "src/billing/invoice.py": "pass\n", "src/billing/tax.py": "pass\n"})
        self.assertEqual(report["findings"], [])

    def test_conflicting_claude_rules_show_as_a_structure_warning_only(self):
        report = self.check({"AGENTS.md": "# Rules\n\nUse pnpm for every install.\n",
                             "CLAUDE.md": "@AGENTS.md\n\nUse npm for every install.\n"})
        # The script reports where instructions live, not which of two rules is right.
        self.assertEqual(self.codes(report), ["claude-not-import"])

    def test_links_inside_code_are_not_checked(self):
        report = self.check({"AGENTS.md": "# Rules\n\n```md\n[example](missing.md)\n```\n\n"
                                          "Write `[text](path.md)` or `<path.md>` for a link.\n"})
        self.assertNotIn("broken-link", self.codes(report))

    def test_link_forms_with_titles_spaces_parentheses_and_references_resolve(self):
        report = self.check({
            "AGENTS.md": ("# Rules\n\n"
                          "[a](docs/a.md 'Title') [b](docs/b.md (Title)) [c](docs/c.md \"Title\")\n"
                          "[space](<docs/with space.md>) [parens](docs/a_(b).md)\n\n"
                          "Read the [reference][ref].\n\n"
                          "[ref]: docs/ref.md \"Reference\"\n"
                          "[^1]: A footnote, not a link definition.\n"
                          "[note]: this line is prose, not a definition\n"),
            "docs/a.md": "# A\n", "docs/b.md": "# B\n", "docs/c.md": "# C\n",
            "docs/with space.md": "# Space\n", "docs/a_(b).md": "# Parens\n", "docs/ref.md": "# Ref\n",
        })
        self.assertNotIn("broken-link", self.codes(report))
        for name in ("docs/a.md", "docs/b.md", "docs/c.md", "docs/with space.md", "docs/a_(b).md", "docs/ref.md"):
            self.assertIn(name, report["reached"])

    def test_broken_reference_definition_is_found(self):
        report = self.check({"AGENTS.md": "# Rules\n\nSee [setup][s].\n\n[s]: <docs/old setup.md>\n"})
        found = self.finding(report, "broken-link")
        self.assertEqual((found["path"], found["line"]), ("AGENTS.md", 5))

    def test_bare_angle_paths_and_commented_links_are_not_links(self):
        report = self.check({"AGENTS.md": "# Rules\n\nWrite <docs/missing.md> as plain text.\n\n"
                                          "<!-- old index:\n[gone](gone.md)\n-->\n"})
        self.assertNotIn("broken-link", self.codes(report))

    def test_links_that_only_work_without_case_or_with_backslashes_are_link_case(self):
        report = self.check({
            "AGENTS.md": "# Rules\n\n[Setup](Docs/Setup.md)\n\n[Again](docs\\setup.md) and [fine](docs/setup.md)\n",
            "docs/setup.md": "# Setup\n",
        })
        found = sorted((f["severity"], f["path"], f["line"]) for f in report["findings"] if f["code"] == "link-case")
        self.assertEqual(found, [("warning", "AGENTS.md", 3), ("warning", "AGENTS.md", 5)])
        self.assertNotIn("broken-link", self.codes(report))
        self.assertIn("docs/setup.md", report["reached"])
        self.assertEqual([r for r in report["reached"] if r.lower() == "docs/setup.md"], ["docs/setup.md"])

    def test_check_never_writes(self):
        self.write(dict(self.NESTED, **{"docs/orphan.md": "# Orphan\n", "AGENTS.md": "[gone](gone.md)\n"}))

        def snapshot():
            return {path: (path.stat().st_mtime_ns, path.read_bytes()) for path in self.root.rglob("*")
                    if path.is_file()} | {"dirs": sorted(str(p) for p in self.root.rglob("*") if p.is_dir())}

        before = snapshot()
        self.run_script(str(self.root))
        self.run_script(str(self.root), "--json")
        self.run_script(str(self.root), "--changed", "src/app.py", "docs/architecture.md")
        self.run_script(str(self.root), "--changed-from-git")
        self.assertEqual(snapshot(), before)

    def test_repeated_paragraphs_function_is_reusable(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("docs_check", SCRIPT)
        module = importlib.util.module_from_spec(spec)
        sys.modules["docs_check"] = module  # dataclasses look their module up while the class is built
        self.addCleanup(sys.modules.pop, "docs_check", None)
        spec.loader.exec_module(module)
        self.write({"a.md": f"# A\n\n{self.RULE}\n", "b.md": f"Intro\n\n{self.RULE.lower()}\n", "c.md": self.SHORT})
        repeats = module.repeated_paragraphs([self.root / "a.md", self.root / "b.md", self.root / "c.md"])
        self.assertEqual(len(repeats), 1)
        self.assertEqual([(path.name, line) for path, line in repeats[0].places], [("a.md", 3), ("b.md", 3)])

    MARKER = '<!-- workflow-axa:required-read phases=specify,execute,deliver path="tests/README.md" -->'

    def test_required_read_marker_naming_a_missing_file_blocks(self):
        report = self.check({"AGENTS.md": f"# Rules\n\n{self.MARKER}\n"}, exit_code=1)
        found = self.finding(report, "broken-link")
        self.assertEqual((found["severity"], found["path"], found["line"]), ("blocking", "AGENTS.md", 3))
        self.assertIn("tests/README.md", found["message"])
        self.assertEqual(report["counts"]["blocking"], 1)

    def test_broken_link_to_a_required_document_blocks(self):
        report = self.check({"AGENTS.md": "# Rules\n\nSee [tests](tests/README.md).\n",
                             "CLAUDE.md": f"@AGENTS.md\n{self.MARKER}\n"}, exit_code=1)
        # The missing required file is reported once, at the marker, not again at the link.
        severities = sorted((f["path"], f["severity"]) for f in report["findings"] if f["code"] == "broken-link")
        self.assertEqual(severities, [("CLAUDE.md", "blocking")])

    def test_malformed_markers_are_notes(self):
        report = self.check({"AGENTS.md": (
            "# Rules\n\n"
            '<!-- workflow-axa:required-read phases=build path="tests/README.md" -->\n'
            '<!-- workflow-axa:required-read phases=execute path="../outside.md" -->\n'
            '<!-- workflow-axa:required-read phases=execute path="docs\\\\*.md" -->\n'
            '<!-- workflow-axa:required-read phases=execute -->\n'
            "Example in prose: <!-- workflow-axa:required-read phases=x --> is not a declaration.\n")})
        found = [(f["severity"], f["line"]) for f in report["findings"] if f["code"] == "malformed-marker"]
        self.assertEqual(found, [("note", 3), ("note", 4), ("note", 5), ("note", 6)])
        self.assertEqual(report["counts"]["blocking"], 0)

    def test_required_read_marker_naming_a_folder_is_malformed(self):
        report = self.check({"AGENTS.md": "# Rules\n\n" + self.MARKER.replace("tests/README.md", "tests") + "\n",
                             "tests/README.md": "# Tests\n"})
        found = self.finding(report, "malformed-marker")
        self.assertEqual((found["severity"], found["line"]), ("note", 3))
        self.assertNotIn("broken-link", self.codes(report))

    def test_required_read_marker_naming_an_existing_file_is_fine(self):
        report = self.check({"AGENTS.md": f"# Rules\n\n{self.MARKER}\n", "tests/README.md": "# Tests\n"})
        self.assertNotIn("broken-link", self.codes(report))

    def test_agents_without_a_claude_beside_it_is_reported(self):
        report = self.check({
            "AGENTS.md": "# Rules\n\n[API](packages/api/AGENTS.md) and [web](packages/web/AGENTS.md)\n",
            "packages/api/AGENTS.md": "# API\n",
            "packages/web/AGENTS.md": "# Web\n", "packages/web/CLAUDE.md": "@AGENTS.md\n",
            "docs/plans/task/AGENTS.md": "# Fixture copy in history\n",
        })
        found = [(f["severity"], f["path"], f["message"]) for f in report["findings"] if f["code"] == "no-claude"]
        self.assertEqual(found, [
            ("warning", "CLAUDE.md",
             "If this repository is used with Claude Code, add CLAUDE.md with the one line @AGENTS.md "
             "(Claude Code loads no project rules now)"),
            ("note", "packages/api/CLAUDE.md",
             "If this repository is used with Claude Code, add packages/api/CLAUDE.md with the one line @AGENTS.md "
             "(Claude Code loads no rules for packages/api now)"),
        ])

    def test_claude_rules_in_dot_claude_or_claude_local_count_as_claude(self):
        for other in (".claude/CLAUDE.md", "CLAUDE.local.md"):
            with self.subTest(other=other):
                shutil.rmtree(self.root)
                self.root.mkdir()
                report = self.check({"AGENTS.md": "# Rules\n\n[API](packages/api/AGENTS.md)\n", other: "@AGENTS.md\n",
                                     "packages/api/AGENTS.md": "# API\n",
                                     f"packages/api/{other}": "@AGENTS.md\n"})
                self.assertNotIn("no-claude", self.codes(report))

    def test_nested_duplicate_names_its_folder_and_a_full_copy_is_one_finding(self):
        agents = f"# Backend\n\n{self.RULE}\n\nUse PHP 8.\n"
        report = self.check({
            "AGENTS.md": "# Rules\n\n[Backend](backend/AGENTS.md) and [web](web/AGENTS.md)\n", "CLAUDE.md": "@AGENTS.md\n",
            "backend/AGENTS.md": agents, "backend/CLAUDE.md": f"@AGENTS.md\n\n{self.RULE}\n",
            "web/AGENTS.md": agents.replace("Backend", "Web"), "web/CLAUDE.md": agents.replace("Backend", "Web"),
        })
        found = sorted((f["code"], f["path"], f["message"]) for f in report["findings"]
                       if f["code"] in ("claude-not-import", "claude-duplicates-agents"))
        self.assertEqual(found, [
            ("claude-duplicates-agents", "backend/CLAUDE.md",
             "backend/CLAUDE.md duplicates backend/AGENTS.md: repeats 1 paragraph (first at backend/AGENTS.md:3); "
             "backend/CLAUDE.md should only import it"),
            ("claude-duplicates-agents", "web/CLAUDE.md",
             "web/CLAUDE.md is a full copy of web/AGENTS.md; replace it with the one line @AGENTS.md"),
            # A partial copy keeps both findings: it adds rules besides the import.
            ("claude-not-import", "backend/CLAUDE.md",
             "CLAUDE.md is not the one line @AGENTS.md (blank lines and HTML comments aside)"),
        ])

    def test_unreached_markdown_anywhere_is_a_note_with_root_and_history_exemptions(self):
        marker = self.MARKER.replace("tests/README.md", "guides/required.md")
        report = self.check({
            "AGENTS.md": f"# Rules\n\n{marker}\n\n[Docs](docs/README.md)\n", "CLAUDE.md": "@AGENTS.md\n",
            ".gitignore": "generated/\n",
            "docs/README.md": "# Docs\n",
            "guides/required.md": "# Required, reached through the marker\n",
            "guides/setup.md": "# Not linked\n",
            "src/billing/NOTES.md": "# Not linked\n",
            "README.md": "# Project\n", "CHANGELOG.md": "# Changes\n", "LICENSE.md": "MIT\n",
            "CONTRIBUTING.md": "# How\n", "CODE_OF_CONDUCT.md": "# Be kind\n", "SECURITY.md": "# Report\n",
            "src/README.md": "# Source\n",
            "docs/plans/task/PLAN.md": "# Plan\n", "plans/2025.md": "# Old\n", "docs/archive/old.md": "# Old\n",
            "docs/notes/plans/t.md": "# Plan\n",
            "generated/api.md": "# Generated\n",
        })
        unreached = sorted(f["path"] for f in report["findings"] if f["code"] == "unreachable-doc")
        # src/ holds no file besides its README, so that README is not found by location: it is reported.
        self.assertEqual(unreached, ["guides/setup.md", "src/README.md", "src/billing/NOTES.md"])

    def test_dot_folders_skill_packages_and_readmes_are_not_unreachable(self):
        report = self.check({
            "AGENTS.md": "# Rules\n", "CLAUDE.md": "@AGENTS.md\n",
            ".superpowers/sdd/spec.md": "# Tool output\n", ".claude/agents/x.md": "# Agent\n",
            "skills/tdd/SKILL.md": "# Skill\n\nSee [tests](tests.md).\n",
            "skills/tdd/tests.md": "# Reference\n\nAlso [mocking](refs/mocking.md).\n",
            "skills/tdd/refs/mocking.md": "# Reached through tests.md\n",
            "skills/tdd/refs/deep.md": "# Deeper reference nothing in the package links\n",
            "src/billing/README.md": "# Found by location beside the code\n", "src/billing/invoice.py": "pass\n",
            "docs/security/README.md": "# A docs README still needs an index entry\n",
            "notes/README.md": "# A folder of notes only\n", "notes/idea.md": "# Idea\n",
            "skills/notes.md": "# Not inside a skill package\n",
            "tests/SCENARIOS.md": "# Unlinked\n",
        })
        unreached = sorted(f["path"] for f in report["findings"] if f["code"] == "unreachable-doc")
        self.assertEqual(unreached, ["docs/security/README.md", "notes/README.md", "notes/idea.md",
                                     "skills/notes.md", "skills/tdd/refs/deep.md", "tests/SCENARIOS.md"])
        # A skill package is reached through its own SKILL.md, so the note names that file.
        deep = [f for f in report["findings"] if f["path"] == "skills/tdd/refs/deep.md"]
        self.assertEqual(deep[0]["message"], "no document reached from skills/tdd/SKILL.md links to it")

    def test_without_agents_claude_is_the_entry_point(self):
        report = self.check({"CLAUDE.md": "# Rules\n\n" + "word " * 1199 + "\n", "docs/orphan.md": "# Orphan\n"})
        size = self.finding(report, "agents-size")
        self.assertEqual(size["path"], "CLAUDE.md")
        self.assertIn("CLAUDE.md has 1201 words", size["message"])
        self.assertEqual(self.finding(report, "unreachable-doc")["message"],
                         "no document reached from CLAUDE.md links to it")
        result = self.run_script(str(self.root), "--json", "--changed", "src/app.py")
        related = json.loads(result.stdout)["related"]
        self.assertEqual([(r["changed"], r["document"], r["reason"]) for r in related],
                         [("src/app.py", "CLAUDE.md", "entry point")])

    def test_nested_repositories_and_worktrees_are_not_walked(self):
        # A worktree has a .git file; a nested clone has a .git folder. Neither belongs to this repository.
        files = {"AGENTS.md": "# Rules\n", "CLAUDE.md": "@AGENTS.md\n"}
        for folder in (".claude/worktrees/agent-1", "vendor-clone"):
            files[f"{folder}/AGENTS.md"] = "# Copy\n\n[gone](gone.md)\n"
            files[f"{folder}/CLAUDE.md"] = "# Not an import\n"
            files[f"{folder}/docs/orphan.md"] = "# Orphan\n"
        files[".claude/worktrees/agent-1/.git"] = "gitdir: ../../../.git/worktrees/agent-1\n"
        self.write(files)
        (self.root / "vendor-clone/.git").mkdir()
        report = self.check()
        self.assertEqual(report["findings"], [])


class ChangedFilesTests(Fixture):
    """D2: `--changed` lists the documents related to changed files and checks the facts they name."""

    def changed(self, *paths: str, files: dict[str, str] | None = None, exit_code: int = 0) -> dict:
        if files:
            self.write(files)
        result = self.run_script(str(self.root), "--json", "--changed", *paths)
        self.assertEqual(result.returncode, exit_code, result.stdout + result.stderr)
        return json.loads(result.stdout)

    def related(self, report: dict) -> list[tuple[str, str, str]]:
        """The relations found by links, names, folders and hints; the root AGENTS.md "entry point" entry,
        present for every changed file, is checked by its own test."""
        return sorted((r["changed"], r["document"], r["reason"]) for r in report["related"]
                      if r["reason"] != "entry point")

    def test_root_agents_is_always_related_as_the_entry_point(self):
        report = self.changed("src/payments/retry.ts", files={
            "AGENTS.md": "# Agent instructions\n\nRun tests with `npm test`.\n",
            "package.json": json.dumps({"scripts": {"test": "node tests/run.js"}}),
            "src/payments/retry.ts": "x\n",
        })
        self.assertEqual([(r["changed"], r["document"], r["reason"]) for r in report["related"]],
                         [("src/payments/retry.ts", "AGENTS.md", "entry point")])
        self.assertEqual([(f["claim"], f["status"]) for f in report["facts"]], [("npm test", "matched")])

    def test_document_linking_the_changed_file_or_its_folder_is_related(self):
        report = self.changed("src/billing/invoice.py", "src/auth/login.py", files={
            "AGENTS.md": "# Rules\n\n[Docs](docs/README.md)\n",
            "docs/README.md": "# Docs\n\n- [Billing](billing.md)\n- [Auth](auth.md)\n",
            "docs/billing.md": "# Billing\n\nInvoices are built in [the invoice module](../src/billing/invoice.py).\n",
            "docs/auth.md": "# Auth\n\nEverything in [the auth folder](../src/auth/) checks sessions.\n",
            "src/billing/invoice.py": "pass\n", "src/auth/login.py": "pass\n",
        })
        self.assertIn(("src/billing/invoice.py", "docs/billing.md", "links to the path"), self.related(report))
        self.assertIn(("src/auth/login.py", "docs/auth.md", "links to its folder src/auth"), self.related(report))
        self.assertNotIn("docs/auth.md", [r["document"] for r in report["related"]
                                          if r["changed"] == "src/billing/invoice.py"])

    def test_document_naming_the_path_in_backticks_is_related(self):
        report = self.changed("src/billing/tax.py", files={
            "AGENTS.md": "# Rules\n\nTaxes live in `src/billing/tax.py`; prose naming src/billing/tax.py is not used.\n",
            "src/billing/tax.py": "pass\n",
        })
        self.assertEqual(self.related(report), [("src/billing/tax.py", "AGENTS.md", "names the path")])

    def test_nearest_readme_or_docs_folder_up_the_tree_is_related(self):
        report = self.changed("packages/api/src/handlers/user.py", files={
            "AGENTS.md": "# Rules\n", "README.md": "# Whole project\n", "docs/overview.md": "# Overview\n",
            "packages/api/README.md": "# API\n",
            "packages/api/docs/endpoints.md": "# Endpoints\n",
            "packages/api/docs/deep/notes.md": "# Deeper\n",
            "packages/web/README.md": "# Web\n",
            "packages/api/src/handlers/user.py": "pass\n",
        })
        reason = "in a folder that contains it (packages/api)"
        self.assertEqual(self.related(report), [
            ("packages/api/src/handlers/user.py", "packages/api/README.md", reason),
            ("packages/api/src/handlers/user.py", "packages/api/docs/endpoints.md", reason),
        ])

    COVERS = {
        "AGENTS.md": ("# Rules\n\n"
                      "- [Billing](docs/billing.md): read when you change invoices.\n"
                      "  Covers: `src/billing/`, src/tax/**\n"
                      "- [Legacy](docs/legacy.md): old importer. Covers: src/legacy/\n"
                      "- [Jobs](docs/jobs.md): Covers: src/*/jobs/\n"),
        "docs/billing.md": "# Billing\n", "docs/legacy.md": "# Legacy\n", "docs/jobs.md": "# Jobs\n",
        "src/billing/invoice/pdf.py": "pass\n", "src/tax/rates/eu.py": "pass\n", "src/mail/jobs/send.py": "pass\n",
    }

    def test_covers_hint_relates_files_under_its_directory_patterns(self):
        report = self.changed("src/billing/invoice/pdf.py", "src/tax/rates/eu.py", "src/mail/jobs/send.py",
                              "src/other.py", files=self.COVERS)
        self.assertEqual(self.related(report), [
            ("src/billing/invoice/pdf.py", "docs/billing.md", "Covers hint src/billing/ in AGENTS.md:4"),
            ("src/mail/jobs/send.py", "docs/jobs.md", "Covers hint src/*/jobs/ in AGENTS.md:6"),
            ("src/tax/rates/eu.py", "docs/billing.md", "Covers hint src/tax/** in AGENTS.md:4"),
        ])

    def test_covers_hint_under_a_described_entry_relates_the_linked_document(self):
        report = self.changed("src/payments/retry.ts", files={
            "AGENTS.md": ("# Agent instructions\n\n## Documentation\n\n"
                          "- [Billing](docs/billing.md)\n"
                          "  Billing and payment retries. Read before changing payments.\n"
                          "  Covers: src/payments/**\n\n"
                          "Covers: src/jobs/\n"),
            "docs/billing.md": ("# Billing\n\nRun the billing tests with `npm run test:unit`.\n\n"
                                "Invoices are created in `src/billing/invoice.ts`.\n"),
            "package.json": json.dumps({"scripts": {"test": "node tests/run.js"}}),
            "src/payments/retry.ts": "x\n", "src/billing/invoices/create.ts": "x\n", "src/jobs/send.ts": "x\n",
        })
        self.assertEqual(self.related(report), [
            ("src/payments/retry.ts", "docs/billing.md", "Covers hint src/payments/** in AGENTS.md:7")])
        facts = {f["claim"]: f["status"] for f in report["facts"]}
        self.assertEqual(facts, {"npm run test:unit": "contradicted", "src/billing/invoice.ts": "contradicted"})
        # A hint that is not under a link item keeps relating the file that holds it.
        loose = self.changed("src/jobs/send.ts")
        self.assertEqual(self.related(loose), [("src/jobs/send.ts", "AGENTS.md", "Covers hint src/jobs/ in AGENTS.md:9")])

    def test_covers_hint_matching_no_path_is_stale(self):
        report = self.check(self.COVERS)
        stale = [(f["severity"], f["path"], f["line"]) for f in report["findings"] if f["code"] == "stale-hint"]
        self.assertEqual(stale, [("warning", "AGENTS.md", 5)])
        self.assertIn("src/legacy/", self.finding(report, "stale-hint")["message"])

    def facts(self, report: dict, kind: str) -> list[tuple[str, int, str, str]]:
        return [(f["document"], f["line"], f["claim"], f["status"]) for f in report["facts"] if f["kind"] == kind]

    def test_named_paths_in_related_documents_are_checked(self):
        report = self.changed("src/billing/invoice.py", files={
            "AGENTS.md": "# Rules\n\n[Billing](docs/billing.md)\n",
            "docs/billing.md": ("# Billing\n\n"
                                "Invoices: `src/billing/invoice.py`.\n"
                                "PDFs: `src/billing/pdf_writer.py`.\n"
                                "Old spelling: `src/Billing/invoice.py`.\n"
                                "Settings: `config.yml`, route `/api/invoices`, package `@scope/pdf`.\n"
                                "See [the code](../src/billing/invoice.py).\n"),
            "src/billing/invoice.py": "pass\n",
        })
        self.assertEqual(self.facts(report, "path"), [
            ("docs/billing.md", 3, "src/billing/invoice.py", "matched"),
            ("docs/billing.md", 4, "src/billing/pdf_writer.py", "contradicted"),
            ("docs/billing.md", 5, "src/Billing/invoice.py", "contradicted"),
            ("docs/billing.md", 6, "config.yml", "not-checkable"),
        ])
        contradicted = [(f["severity"], f["path"], f["line"]) for f in report["findings"]
                        if f["code"] == "contradicted-fact"]
        self.assertEqual(contradicted, [("warning", "docs/billing.md", 4), ("warning", "docs/billing.md", 5)])
        self.assertTrue(all(f["evidence"] for f in report["facts"]))

    def test_related_documents_without_checkable_facts_are_marked(self):
        files = {"AGENTS.md": "# Rules\n\nThe [app](src/app.py) runs `npm run build`.\n",
                 "src/README.md": "# Source\n\nPlain words only.\n",
                 "package.json": json.dumps({"scripts": {"build": "x"}}), "src/app.py": "pass\n"}
        report = self.changed("src/app.py", files=files)
        self.assertEqual(report["meaning"], "not checked")
        checked = {r["document"]: r.get("facts_checked") for r in report["related"]}
        self.assertEqual(checked, {"AGENTS.md": None, "src/README.md": 0})
        text = self.run_script(str(self.root), "--changed", "src/app.py").stdout.splitlines()
        self.assertIn("  src/README.md: no checkable facts", text[text.index("Facts:") + 1:])

    def test_shortened_foreign_and_missing_paths_are_told_apart(self):
        report = self.changed("src/app/providers/http.service.ts", files={
            "AGENTS.md": ("# Rules\n\n"
                          "HTTP: `providers/http.service.ts`.\n"
                          "Backend: `Modules/Pletrix/Routes/api.php`.\n"
                          "Branch: `origin/HEAD`.\n"
                          "Gone: `src/app/missing.service.ts`.\n"
                          "Case: `src/App/providers/http.service.ts`.\n"
                          "Twice: `shared/util.ts`.\n"
                          "Here: `./notes.md`.\n"
                          "The [service](src/app/providers/http.service.ts).\n"
                          "Sibling repository: `../backend-repo`.\n"),
            "src/app/providers/http.service.ts": "x\n",
            "src/a/shared/util.ts": "x\n", "src/b/shared/util.ts": "x\n",
        })
        facts = {f["claim"]: (f["status"], f["evidence"]) for f in report["facts"] if f["kind"] == "path"}
        self.assertEqual(facts["providers/http.service.ts"],
                         ("matched", "found as src/app/providers/http.service.ts"))
        reason = "first folder not found here; may belong to another repository or not be a path"
        self.assertEqual(facts["Modules/Pletrix/Routes/api.php"], ("not-checkable", reason))
        self.assertEqual(facts["origin/HEAD"], ("not-checkable", reason))
        self.assertEqual(facts["src/app/missing.service.ts"][0], "contradicted")
        self.assertEqual(facts["src/App/providers/http.service.ts"],
                         ("contradicted", "only src/app/providers/http.service.ts exists (letter case differs)"))
        self.assertEqual(facts["shared/util.ts"], ("not-checkable", "2 files or folders end with this path"))
        self.assertEqual(facts["./notes.md"][0], "contradicted")
        self.assertEqual(facts["../backend-repo"], ("not-checkable", "leaves this repository"))
        contradicted = sorted(f["line"] for f in report["findings"] if f["code"] == "contradicted-fact")
        self.assertEqual(contradicted, [6, 7, 9])

    def test_bare_name_matching_only_in_other_letter_case_is_not_checkable(self):
        report = self.changed("src/app.py", files={
            "AGENTS.md": ("# Rules\n\nThe [app](src/app.py). Read the other repository's `design.md`.\n"
                          "Guide: `docs/Guide.md`. Also the [design notes](Design.md).\n"),
            "DESIGN.md": "# Design\n", "docs/guide.md": "# Guide\n", "src/app.py": "pass\n",
        })
        facts = {f["claim"]: (f["status"], f["evidence"]) for f in report["facts"] if f["kind"] == "path"}
        self.assertEqual(facts["design.md"],
                         ("not-checkable", "bare file name; only DESIGN.md exists (letter case differs), "
                                           "so it may name another repository's file"))
        self.assertEqual(facts["docs/Guide.md"],
                         ("contradicted", "only docs/guide.md exists (letter case differs)"))
        self.assertIn(("AGENTS.md", 4), [(f["path"], f["line"]) for f in report["findings"] if f["code"] == "link-case"])

    def test_command_options_workspaces_binaries_and_aliases(self):
        report = self.changed("src/app.js", files={
            "AGENTS.md": ("# Rules\n\nThe [app](src/app.js).\n\n```sh\n"
                          "npm run --silent build\n"            # 6: option skipped, script found
                          "pnpm --filter api build\n"           # 7: another package
                          "npm run --prefix web build\n"        # 8: another package
                          "pnpm -r test && yarn -w lint\n"      # 9: two, both another package
                          "pnpm vitest\n"                       # 10: may be a local binary
                          "yarn eslint src\n"                   # 11: may be a local binary
                          "pnpm run vitest\n"                   # 12: run names a script: contradicted
                          "composer u && composer req a/b && composer du\n"  # 13: aliases of built-ins
                          "composer run -l\n"                   # 14: lists the scripts
                          "composer run-script --dev lint\n"    # 15: option skipped
                          "```\n"),
            "package.json": json.dumps({"scripts": {"build": "x", "test": "y"}}),
            "composer.json": json.dumps({"scripts": {"lint": "phpcs"}}),
            "src/app.js": "x\n",
        })
        facts = [(f["line"], f["claim"], f["status"], f["evidence"]) for f in report["facts"] if f["kind"] == "command"]
        another = "runs in another package"
        self.assertEqual([fact[:3] for fact in facts], [
            (6, "npm run --silent build", "matched"),
            (7, "pnpm --filter api build", "not-checkable"),
            (8, "npm run --prefix web build", "not-checkable"),
            (9, "pnpm -r test", "not-checkable"),
            (9, "yarn -w lint", "not-checkable"),
            (10, "pnpm vitest", "not-checkable"),
            (11, "yarn eslint", "not-checkable"),
            (12, "pnpm run vitest", "contradicted"),
            (13, "composer u", "not-checkable"),
            (13, "composer req", "not-checkable"),
            (13, "composer du", "not-checkable"),
            (14, "composer run -l", "not-checkable"),
            (15, "composer run-script --dev lint", "matched"),
        ])
        evidence = {fact[1]: fact[3] for fact in facts}
        for claim in ("pnpm --filter api build", "npm run --prefix web build", "pnpm -r test", "yarn -w lint"):
            self.assertEqual(evidence[claim], another)
        self.assertIn("may be a local binary", evidence["pnpm vitest"])
        self.assertIn("lists the scripts", evidence["composer run -l"])

    def test_folder_option_after_the_script_name_runs_elsewhere(self):
        report = self.changed("src/app.js", files={
            "AGENTS.md": "# Rules\n\nThe [app](src/app.js). Run `npm run dev --prefix apps/web` or `pnpm test -r`.\n",
            "package.json": json.dumps({"scripts": {"build": "x"}}),
            "src/app.js": "x\n",
        })
        facts = [(f["status"], f["evidence"]) for f in report["facts"] if f["kind"] == "command"]
        self.assertEqual(facts, [("not-checkable", "runs in another package")] * 2)

    def test_npm_script_shortcuts_are_checked_as_scripts(self):
        report = self.changed("src/app.js", files={
            "AGENTS.md": ("# Rules\n\nThe [app](src/app.js). Run tests with `npm test`, serve with `npm start`.\n"
                          "Also `npm stop`, `npm restart` and `npm install`.\n"),
            "package.json": json.dumps({"scripts": {"test": "node t.js", "start": "node s.js"}}),
            "src/app.js": "x\n",
        })
        facts = [(f["claim"], f["status"]) for f in report["facts"] if f["kind"] == "command"]
        self.assertEqual(facts, [("npm test", "matched"), ("npm start", "matched"),
                                 ("npm stop", "contradicted"), ("npm restart", "not-checkable")])

    def test_npm_start_and_restart_without_a_script_use_npm_defaults(self):
        report = self.changed("src/app.js", files={
            "AGENTS.md": ("# Rules\n\nThe [app](src/app.js). Serve with `npm start`, reload with `npm restart`.\n"
                          "Test with `npm test`, build with `npm run start`.\n"),
            "package.json": json.dumps({"scripts": {"build": "x"}}),
            "src/app.js": "x\n",
        })
        facts = {f["claim"]: (f["status"], f["evidence"]) for f in report["facts"] if f["kind"] == "command"}
        self.assertEqual(facts["npm start"],
                         ("not-checkable", "no script start in package.json; npm start runs node server.js if it exists"))
        self.assertEqual(facts["npm restart"],
                         ("not-checkable", "no script restart in package.json; npm restart runs stop, then start"))
        self.assertEqual(facts["npm test"][0], "contradicted")
        self.assertEqual(facts["npm run start"][0], "contradicted")

    def test_a_fact_repeated_on_one_line_is_listed_once(self):
        report = self.changed("src/app.js", files={
            "AGENTS.md": ("# Rules\n\nThe [app](src/app.js). Run `npm run sync` from here, never edit by hand; "
                          "`npm run sync -- --check` only checks.\n"),
            "package.json": json.dumps({"scripts": {"sync": "node sync.js"}}),
            "src/app.js": "x\n",
        })
        facts = [(f["line"], f["claim"], f["status"]) for f in report["facts"] if f["kind"] == "command"]
        self.assertEqual(facts, [(3, "npm run sync", "matched")])

    def test_a_repeated_claim_keeps_its_contradiction(self):
        # The first mention reads as planned, the second as a fact about today; merging must not hide the second.
        report = self.changed("src/app.js", files={
            "AGENTS.md": "# Rules\n\nThe [app](src/app.js). `src/b.ts` will be added. Edit `src/b.ts` now.\n",
            "src/app.js": "x\n",
        })
        facts = [(f["line"], f["claim"], f["status"]) for f in report["facts"] if f["claim"] == "src/b.ts"]
        self.assertEqual(facts, [(3, "src/b.ts", "contradicted")])

    def test_makefile_rules_with_several_targets_define_each(self):
        report = self.changed("src/app.c", files={
            "AGENTS.md": ("# Rules\n\nThe [app](src/app.c).\n\n"
                          "`make test`, `make lint`, `make deploy`, `make VERSION`, `make CC`, `make echo`\n"),
            "Makefile": ("VERSION := 1\nCC ?= gcc\nFLAGS = -O2\n"
                         "build test lint: deps\n\techo build: done\n"
                         "deploy:: build\n\tscp out host:\n"),
            "src/app.c": "x\n",
        })
        statuses = {f["claim"]: f["status"] for f in report["facts"] if f["kind"] == "command"}
        self.assertEqual(statuses, {"make test": "matched", "make lint": "matched", "make deploy": "matched",
                                    "make VERSION": "contradicted", "make CC": "contradicted",
                                    "make echo": "contradicted"})

    def test_missing_paths_described_as_planned_are_not_checkable(self):
        report = self.changed("src/app.py", files={
            "AGENTS.md": ("# Rules\n\nThe [app](src/app.py).\n"
                          "A planned `src/billing/export.py` handles exports.\n"
                          "We will create `src/jobs/` next.\n"
                          "`src/reports.py` is to be written.\n"
                          "The settings live in `src/settings.py`.\n"),
            "src/app.py": "pass\n",
        })
        facts = {f["claim"]: (f["status"], f["evidence"]) for f in report["facts"] if f["kind"] == "path"}
        planned = ("not-checkable", "described as planned")
        self.assertEqual(facts["src/billing/export.py"], planned)
        self.assertEqual(facts["src/jobs/"], planned)
        self.assertEqual(facts["src/reports.py"], planned)
        self.assertEqual(facts["src/settings.py"][0], "contradicted")

    def test_historical_documents_are_related_but_not_checked(self):
        files = {"AGENTS.md": "# Rules\n\nThe [app](src/app.py). [Old audit](docs/plans/2026-01-01-audit/AUDIT.md)\n",
                 "docs/plans/2026-01-01-audit/AUDIT.md": ("# Old audit\n\nThe [app](../../../src/app.py) used "
                                                         "`src/old_player.py` and `npm run gone`.\n"),
                 "src/app.py": "pass\n"}
        report = self.changed("src/app.py", files=files)
        entries = {r["document"]: r for r in report["related"]}
        self.assertTrue(entries["docs/plans/2026-01-01-audit/AUDIT.md"]["historical"])
        self.assertNotIn("historical", entries["AGENTS.md"])
        self.assertEqual([f for f in report["facts"] if f["document"].startswith("docs/plans/")], [])
        self.assertNotIn("contradicted-fact", self.codes(report))
        text = self.run_script(str(self.root), "--changed", "src/app.py").stdout.splitlines()
        block = text[text.index("Related documents:") + 1:text.index("Facts:")]
        self.assertIn("  historical, not checked: docs/plans/2026-01-01-audit/AUDIT.md", block)

    def test_artisan_signatures_are_found_beside_the_nearest_artisan_file(self):
        report = self.changed("backend/routes/api.php", files={
            "AGENTS.md": "# Rules\n",
            "backend/artisan": "#!/usr/bin/env php\n",
            "backend/app/Console/Commands/PublishPacks.php": "<?php\nprotected $signature = 'packs:publish {pack}';\n",
            "backend/docs/guide.md": "# Guide\n\n`php artisan packs:publish` and `php artisan migrate`.\n",
            "backend/routes/api.php": "<?php\n",
        })
        facts = {f["claim"]: (f["status"], f["evidence"]) for f in report["facts"] if f["kind"] == "command"}
        self.assertEqual(facts["php artisan packs:publish"],
                         ("matched", "signature packs:publish in backend/app/Console/Commands/PublishPacks.php"))
        self.assertEqual(facts["php artisan migrate"][0], "not-checkable")

    def test_instructions_to_add_to_a_missing_file_are_contradicted(self):
        report = self.changed("src/app.py", files={
            "AGENTS.md": ("# Rules\n\nThe [app](src/app.py).\n"
                          "Add each route to `src/routes.ts`.\n"
                          "Create a new handler in `src/handlers/`.\n"),
            "src/app.py": "pass\n",
        })
        facts = {f["claim"]: f["status"] for f in report["facts"] if f["kind"] == "path"}
        self.assertEqual(facts, {"src/routes.ts": "contradicted", "src/handlers/": "contradicted"})

    def test_plans_folder_outside_docs_or_root_is_live_documentation(self):
        report = self.changed("src/app.py", files={
            "AGENTS.md": ("# Rules\n\n[Roadmap](product/plans/ROADMAP.md), [old](plans/2025.md), "
                          "[task](docs/plans/t/PLAN.md)\n"),
            "product/plans/ROADMAP.md": "# Roadmap\n\nThe [app](../../src/app.py) moves to `src/gone.py`.\n",
            "plans/2025.md": "# 2025\n\nThe [app](../src/app.py) used `src/gone.py`.\n",
            "docs/plans/t/PLAN.md": "# Plan\n\nThe [app](../../../src/app.py) used `src/gone.py`.\n",
            "src/app.py": "pass\n",
        })
        historical = sorted(r["document"] for r in report["related"] if r.get("historical"))
        self.assertEqual(historical, ["docs/plans/t/PLAN.md", "plans/2025.md"])
        checked = [(f["document"], f["status"]) for f in report["facts"] if f["claim"] == "src/gone.py"]
        self.assertEqual(checked, [("product/plans/ROADMAP.md", "contradicted")])

    def test_history_folders_are_exempt_and_historical_alike_and_the_rule_is_named(self):
        files = {"AGENTS.md": "# Rules\n", "CLAUDE.md": "@AGENTS.md\n", "src/app.py": "pass\n"}
        for name in ("docs/plans/t/PLAN.md", "docs/archive/old.md", "docs/notes/plans/t.md",
                     "pkg/docs/archive/a.md", "plans/2025.md", "archive/2024.md", "old/archive/v1.md",
                     "src/archive/README.md", "product/plans/ROADMAP.md"):
            files[name] = "# Record\n\nThe app is in `src/app.py`.\n"
        report = self.changed(*[name for name in files if name.endswith(".md") and "/" in name], files=files)
        historical = {r["document"]: r.get("history") for r in report["related"] if r.get("historical")}
        self.assertEqual(historical, {
            "docs/plans/t/PLAN.md": "plans folder under docs/", "docs/archive/old.md": "archive folder under docs/",
            "docs/notes/plans/t.md": "plans folder under docs/", "pkg/docs/archive/a.md": "archive folder under docs/",
            "plans/2025.md": "plans folder at the root", "archive/2024.md": "archive folder at the root"})
        # plans and archive folders outside docs and below the root are live and need an index entry.
        self.assertEqual(sorted(f["path"] for f in report["findings"] if f["code"] == "unreachable-doc"),
                         ["old/archive/v1.md", "product/plans/ROADMAP.md", "src/archive/README.md"])
        text = self.run_script(str(self.root), "--changed", "docs/notes/plans/t.md").stdout.splitlines()
        line = text.index("  historical, not checked: docs/notes/plans/t.md")
        self.assertEqual(text[line + 1], "    history rule: plans folder under docs/")

    def test_root_changelog_is_history_and_its_old_paths_are_not_contradictions(self):
        report = self.changed("CHANGELOG.md", "CHANGES.md", "docs/CHANGELOG.md", files={
            "AGENTS.md": "# Rules\n", "CLAUDE.md": "@AGENTS.md\n", "src/app.py": "pass\n",
            "CHANGELOG.md": "# Changes\n\n- `src/old_tool.py` prepares runs.\n",
            "CHANGES.md": "# Changes\n\n- `src/older.py` builds.\n",
            "docs/CHANGELOG.md": "# Not at the root\n\n- `src/gone.py` is current.\n",
        })
        historical = {r["document"]: r.get("history") for r in report["related"] if r.get("historical")}
        self.assertEqual(historical, {"CHANGELOG.md": "changelog at the root", "CHANGES.md": "changelog at the root"})
        self.assertEqual([f["path"] for f in report["findings"] if f["code"] == "contradicted-fact"],
                         ["docs/CHANGELOG.md"])

    def test_planned_and_history_words_apply_to_their_own_sentence(self):
        report = self.changed("src/app.py", files={
            "AGENTS.md": ("# Rules\n\nThe [app](src/app.py).\n"
                          "Add each route to `src/routes.ts`. The file `src/later.ts` will be added.\n"
                          "We migrated last year; the app uses Angular 15. Angular 14 was deprecated.\n"),
            "package.json": json.dumps({"dependencies": {"@angular/core": "^17.1.0"}}),
            "src/app.py": "pass\n",
        })
        paths = {f["claim"]: (f["status"], f["evidence"]) for f in report["facts"] if f["kind"] == "path"}
        self.assertEqual(paths["src/routes.ts"][0], "contradicted")
        self.assertEqual(paths["src/later.ts"], ("not-checkable", "described as planned"))
        versions = {f["claim"]: (f["status"], f["evidence"]) for f in report["facts"] if f["kind"] == "version"}
        self.assertEqual(versions["Angular 15"][0], "contradicted")
        self.assertEqual(versions["Angular 14"], ("not-checkable", "reads as history"))

    def test_named_commands_are_checked_against_the_manifests(self):
        report = self.changed("src/app.js", files={
            "AGENTS.md": ("# Rules\n\nBuild with `npm run build`, not `npm run biuld`. Test: `pnpm test`.\n"
                          "Install: `pnpm install`. Lint: `yarn lint`.\n\n"
                          "```sh\ncomposer lint && composer install\nmake deploy\nmake clean\n"
                          "php artisan invoices:send\nphp artisan migrate\n"
                          "python -m tools.report\npython -m http.server\n```\n\n"
                          "Make sure you read this; npm run in prose is not a command.\n\n"
                          "The [app](src/app.js) starts here.\n"),
            "package.json": json.dumps({"scripts": {"build": "vite build", "test": "vitest"}}),
            "composer.json": json.dumps({"scripts": {"lint": "phpcs"}}),
            "Makefile": "deploy: build\n\tscp dist host:\n\nVERSION := 1\n",
            "app/Console/Commands/SendInvoices.php": "<?php\nprotected $signature = 'invoices:send {--dry}';\n",
            "tools/report.py": "pass\n",
            "src/app.js": "x\n",
        })
        self.assertEqual(self.facts(report, "command"), [
            ("AGENTS.md", 3, "npm run build", "matched"),
            ("AGENTS.md", 3, "npm run biuld", "contradicted"),
            ("AGENTS.md", 3, "pnpm test", "matched"),
            ("AGENTS.md", 4, "pnpm install", "not-checkable"),
            ("AGENTS.md", 4, "yarn lint", "not-checkable"),  # no script: may be a local binary
            ("AGENTS.md", 7, "composer lint", "matched"),
            ("AGENTS.md", 7, "composer install", "not-checkable"),
            ("AGENTS.md", 8, "make deploy", "matched"),
            ("AGENTS.md", 9, "make clean", "contradicted"),
            ("AGENTS.md", 10, "php artisan invoices:send", "matched"),
            ("AGENTS.md", 11, "php artisan migrate", "not-checkable"),
            ("AGENTS.md", 12, "python -m tools.report", "matched"),
            ("AGENTS.md", 13, "python -m http.server", "not-checkable"),
        ])

    def test_version_claims_are_compared_with_version_facts(self):
        report = self.changed("src/main.ts", files={
            "AGENTS.md": ("# Rules\n\nThe [app](src/main.ts) uses Angular 18 and Next.js 14.\n"
                          "The API runs Laravel 10 on PHP 7.4; Node 20 builds it.\n"),
            "package.json": json.dumps({"dependencies": {"@angular/core": "^18.2.0"}, "engines": {"node": ">=20"}}),
            "package-lock.json": json.dumps({"lockfileVersion": 3, "packages": {
                "": {}, "node_modules/@angular/core": {"version": "18.2.3"}}}),
            "composer.json": json.dumps({"require": {"php": "^8.2", "laravel/framework": "^11.0"}}),
            "composer.lock": json.dumps({"packages": [{"name": "laravel/framework", "version": "v11.9.1"}]}),
            "src/main.ts": "x\n",
        })
        self.assertEqual(self.facts(report, "version"), [
            ("AGENTS.md", 3, "Angular 18", "matched"),
            ("AGENTS.md", 3, "Next.js 14", "not-checkable"),
            ("AGENTS.md", 4, "Laravel 10", "contradicted"),
            ("AGENTS.md", 4, "PHP 7.4", "contradicted"),
            ("AGENTS.md", 4, "Node 20", "not-checkable"),
        ])
        evidence = {f["claim"]: f["evidence"] for f in report["facts"]}
        self.assertIn("18.2.3 in package-lock.json", evidence["Angular 18"])
        self.assertIn("v11.9.1", evidence["Laravel 10"])
        self.assertIn("^8.2", evidence["PHP 7.4"])

    def test_monorepo_commands_next_shorthand_and_nvmrc(self):
        report = self.changed("src/app.ts", files={
            "AGENTS.md": ("# Rules\n\nThe [app](src/app.ts) uses Next 16.3 and Node 22.\n"
                          "Run `npm run lint` from `web/`.\n"
                          "Run `npm run dev` and `php artisan packs:publish`.\n"),
            ".nvmrc": "v20.11.0\n",
            "web/package.json": json.dumps({"scripts": {"lint": "eslint"}}),
            "app/package.json": json.dumps({"scripts": {"dev": "next dev"}, "dependencies": {"next": "^15.1.0"}}),
            "api/artisan": "#!/usr/bin/env php\n",
            "api/app/Console/Commands/Publish.php": "<?php\nprotected $signature = 'packs:publish';\n",
            "src/app.ts": "x\n",
        })
        facts = {f["claim"]: (f["status"], f["evidence"]) for f in report["facts"]}
        self.assertEqual(facts["npm run lint"], ("matched", "script lint in web/package.json"))
        # Two subfolders hold a package.json, so without "from" nothing is chosen.
        self.assertEqual(facts["npm run dev"][0], "not-checkable")
        self.assertEqual(facts["php artisan packs:publish"],
                         ("matched", "signature packs:publish in api/app/Console/Commands/Publish.php"))
        self.assertEqual(facts["Node 22"], ("contradicted", "node pinned v20.11.0 in .nvmrc"))
        self.assertEqual(facts["Next.js 16.3"][0], "not-checkable")  # no package.json at the root
        (self.root / "web/package.json").unlink()
        single = self.changed("src/app.ts")
        facts = {f["claim"]: (f["status"], f["evidence"]) for f in single["facts"]}
        self.assertEqual(facts["npm run dev"], ("matched", "script dev in app/package.json"))
        self.assertEqual(facts["Next.js 16.3"], ("contradicted", "next constraint ^15.1.0 in app/package.json"))

    def from_git(self, env: dict | None = None) -> dict:
        self.write({"AGENTS.md": "# Rules\n", "CLAUDE.md": "@AGENTS.md\n"})
        result = subprocess.run([sys.executable, "-X", "utf8", "-I", str(SCRIPT), str(self.root), "--json",
                                 "--changed-from-git"], capture_output=True, text=True, encoding="utf-8", env=env)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return json.loads(result.stdout)

    def test_changed_from_git_lists_changed_and_untracked_files(self):
        git = shutil.which("git")
        if git is None:
            self.skipTest("git is not installed")

        def run(*args: str) -> str:
            result = subprocess.run([git, "-C", str(self.root), *args], capture_output=True, text=True,
                                    encoding="utf-8")
            self.assertEqual(result.returncode, 0, result.stderr)
            return result.stdout.strip()

        # A throwaway repository in the temporary folder; the commit is made with plumbing, so no hooks run.
        self.write({"AGENTS.md": "# Rules\n\nThe [app](src/app.py) and `src/new.py`.\n", "CLAUDE.md": "@AGENTS.md\n",
                    "src/app.py": "print(1)\n", "src/same.py": "pass\n"})
        run("init", "-q")
        run("config", "user.name", "docs-check test")
        run("config", "user.email", "docs-check@example.invalid")
        run("add", "AGENTS.md", "CLAUDE.md", "src/app.py", "src/same.py")
        commit = run("commit-tree", run("write-tree"), "-m", "fixture")
        run("update-ref", "HEAD", commit)
        self.write({"src/app.py": "print(2)\n", "src/new.py": "pass\n"})
        result = self.run_script(str(self.root), "--json", "--changed-from-git")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["changed"], ["src/app.py", "src/new.py"])
        self.assertEqual(self.related(report), [("src/app.py", "AGENTS.md", "links to the path"),
                                                ("src/new.py", "AGENTS.md", "names the path")])
        self.assertNotIn("git-unavailable", self.codes(report))

    def test_placeholders_absences_future_and_ignored_paths_are_not_checkable(self):
        report = self.changed("src/app.py", files={
            "AGENTS.md": ("# Rules\n\nThe [app](src/app.py).\n"
                          "Plans live in `docs/plans/YYYY-MM-DD-task/PLAN.md`.\n"   # 4
                          "Helpers sit in `src/.../helpers.py`.\n"                  # 5
                          "One page per `src/pages/<name>/index.ts`.\n"             # 6
                          "Tests match `src/**/test_*.py`.\n"                       # 7
                          "`src/legacy.py` does not exist any more.\n"              # 8
                          "We no longer ship `src/old_api.py`.\n"                   # 9
                          "`src/cron.py` was removed.\n"                            # 10
                          "Never edit `src/gen.py` by hand; it is gone.\n"          # 11
                          "`src/export.py` comes later.\n"                          # 12
                          "Reports land in `out/report.html`.\n"                    # 13
                          "The settings live in `src/settings.py`.\n"               # 14
                          "Never run `tools/reset_db.php` against production.\n"    # 15
                          "`src/never.py` never existed; `src/x.py` is gone.\n"),   # 16
            ".gitignore": "out/\n",
            "docs/plans/keep.md": "# Keep\n",
            "tools/reset_database.php": "<?php\n",
            "src/app.py": "pass\n",
        })
        facts = {f["claim"]: (f["line"], f["status"], f["evidence"]) for f in report["facts"] if f["kind"] == "path"}
        self.assertEqual({claim: fact[:2] for claim, fact in facts.items()}, {
            "docs/plans/YYYY-MM-DD-task/PLAN.md": (4, "not-checkable"),
            "src/.../helpers.py": (5, "not-checkable"),
            "src/pages/<name>/index.ts": (6, "not-checkable"),
            "src/**/test_*.py": (7, "not-checkable"),
            "src/legacy.py": (8, "not-checkable"),
            "src/old_api.py": (9, "not-checkable"),
            "src/cron.py": (10, "not-checkable"),
            # "Never" alone is an instruction, not a claim that the file is absent.
            "src/gen.py": (11, "contradicted"),
            "src/export.py": (12, "not-checkable"),
            "out/report.html": (13, "not-checkable"),
            "src/settings.py": (14, "contradicted"),
            "tools/reset_db.php": (15, "contradicted"),
            "src/never.py": (16, "not-checkable"),
            "src/x.py": (16, "not-checkable"),
        })
        self.assertEqual(facts["src/pages/<name>/index.ts"][2], "placeholder path")
        self.assertEqual(facts["src/cron.py"][2], "described as absent")
        self.assertEqual(facts["src/export.py"][2], "described as planned")
        self.assertEqual(facts["out/report.html"][2], "under a git-ignored folder (generated output)")
        self.assertEqual([f["line"] for f in report["findings"] if f["code"] == "contradicted-fact"], [11, 14, 15])

    def test_only_clear_planned_phrases_hide_a_missing_path(self):
        report = self.changed("src/app.py", files={
            "AGENTS.md": ("# Rules\n\nThe [app](src/app.py).\n"
                          "Run `tools/migrate.py` later in the deploy.\n"       # 4: an instruction
                          "The CLI will print `tools/report.txt` paths.\n"      # 5: "will", but not about the file
                          "`tools/export.py` will be added.\n"                  # 6
                          "`tools/sync.py` is to be added later.\n"             # 7
                          "`tools/check.py` comes later.\n"),                   # 8
            "tools/run.py": "pass\n", "src/app.py": "pass\n",
        })
        facts = {f["claim"]: f["status"] for f in report["facts"] if f["kind"] == "path"}
        self.assertEqual(facts, {"tools/migrate.py": "contradicted",
                                 "tools/report.txt": "contradicted", "tools/export.py": "not-checkable",
                                 "tools/sync.py": "not-checkable", "tools/check.py": "not-checkable"})

    def test_a_missing_path_right_after_an_external_link_names_another_repository(self):
        report = self.changed("src/app.py", files={
            "AGENTS.md": ("# Rules\n\nThe [app](src/app.py).\n"
                          "> Bundled from [mattpocock/skills](https://github.com/mattpocock/skills) "
                          "`skills/engineering/tdd/SKILL.md` at `4ae2317`.\n"
                          "Copied from [upstream](https://example.com/repo) at `lib/vendor.py`.\n"
                          "Upstream: https://example.com/repo keeps `src/upstream.py`.\n"
                          "See [the guide](https://example.com/guide) and edit `src/handler.py` here.\n"
                          "Local: `src/app.py` and `src/missing.py`; see [docs](https://example.com).\n"
                          "Plain: `skills/gone.md` is local.\n"),
            "skills/tdd/SKILL.md": "# Skill\n", "lib/keep.py": "pass\n", "src/app.py": "pass\n",
        })
        facts = {f["claim"]: (f["status"], f["evidence"]) for f in report["facts"] if f["kind"] == "path"}
        other = ("not-checkable", "follows an external link; may name another repository's path")
        self.assertEqual(facts["skills/engineering/tdd/SKILL.md"], other)
        self.assertEqual(facts["lib/vendor.py"], other)
        # A URL earlier in the sentence, but not right before the path, does not make it another repository's.
        self.assertEqual(facts["src/upstream.py"][0], "contradicted")
        self.assertEqual(facts["src/handler.py"][0], "contradicted")
        self.assertEqual(facts["src/app.py"][0], "matched")
        self.assertEqual(facts["src/missing.py"][0], "contradicted")  # the link is in another sentence
        self.assertEqual(facts["skills/gone.md"][0], "contradicted")

    def test_a_changed_document_relates_to_itself_and_its_facts_are_checked(self):
        report = self.changed("README.md", "docs/gone.md", files={
            "AGENTS.md": "# Rules\n", "CLAUDE.md": "@AGENTS.md\n",
            "README.md": "# Project\n\nRun `tools/build.py`, then `tools/missing.py`.\n",
            "tools/build.py": "pass\n",
        })
        self.assertEqual(self.related(report), [("README.md", "README.md", "changed document")])
        self.assertEqual(self.facts(report, "path"), [("README.md", 3, "tools/build.py", "matched"),
                                                      ("README.md", 3, "tools/missing.py", "contradicted")])

    def git_repository(self, files: dict[str, str]):
        """A throwaway repository holding `files` in one commit (plumbing only, so no hooks run); returns a runner."""
        git = shutil.which("git")
        if git is None:
            self.skipTest("git is not installed")

        def run(*args: str, cwd: Path | None = None) -> str:
            result = subprocess.run([git, "-C", str(cwd or self.root), *args], capture_output=True, text=True,
                                    encoding="utf-8")
            self.assertEqual(result.returncode, 0, result.stderr)
            return result.stdout.strip()

        self.write(files)
        run("init", "-q")
        run("config", "user.name", "docs-check test")
        run("config", "user.email", "docs-check@example.invalid")
        run("add", *files)
        run("update-ref", "HEAD", run("commit-tree", run("write-tree"), "-m", "fixture"))
        return run

    def from_git_report(self) -> dict:
        result = self.run_script(str(self.root), "--json", "--changed-from-git")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return json.loads(result.stdout)

    def test_changed_from_git_leaves_out_nested_repositories(self):
        run = self.git_repository({"AGENTS.md": "# Rules\n", "CLAUDE.md": "@AGENTS.md\n", "src/app.py": "print(1)\n"})
        self.write({"src/app.py": "print(2)\n", "clone/README.md": "# Clone\n", "wt/notes.md": "# Worktree\n",
                    "wt/.git": "gitdir: /nowhere/worktrees/wt\n"})
        run("init", "-q", cwd=self.root / "clone")
        report = self.from_git_report()
        self.assertEqual(report["changed"], ["src/app.py"])

    def test_untracked_or_ignored_entry_points_and_index_targets_are_notes(self):
        self.git_repository({"AGENTS.md": "# Rules\n\n[A](docs/a.md), [B](docs/b.md), [C](docs/c.md)\n",
                             ".gitignore": "b.md\n", "docs/c.md": "# Tracked\n"})
        self.write({"CLAUDE.md": "@AGENTS.md\n", "docs/a.md": "# Untracked\n", "docs/b.md": "# Ignored\n"})
        report = self.check()
        found = sorted((f["severity"], f["path"], f["message"]) for f in report["findings"]
                       if f["code"] == "untracked-doc")
        message = "untracked: a fresh clone will not have it"
        self.assertEqual(found, [("note", "CLAUDE.md", message), ("note", "docs/a.md", message),
                                 ("note", "docs/b.md", message)])

    def test_changed_from_git_skips_deleted_paths(self):
        run = self.git_repository({"AGENTS.md": "# Rules\n", "CLAUDE.md": "@AGENTS.md\n",
                                   "src/old.py": "pass\n", "src/gone.py": "pass\n", "src/kept.py": "pass\n"})
        run("mv", "src/old.py", "src/new.py")
        (self.root / "src/gone.py").unlink()
        self.write({"src/kept.py": "print(2)\n"})
        self.assertEqual(self.from_git_report()["changed"], ["src/kept.py", "src/new.py"])

    def test_text_output_names_the_entry_point_once(self):
        self.write({"AGENTS.md": "# Rules\n", "CLAUDE.md": "@AGENTS.md\n",
                    "docs/a.md": "# A\n\n[x](../src/x.py)\n", "src/x.py": "pass\n"})
        result = self.run_script(str(self.root), "--changed", "src/x.py", "src/y.py", "src/z.py")
        lines = result.stdout.splitlines()
        block = lines[lines.index("Related documents:") + 1:lines.index("Facts:")]
        self.assertEqual([line for line in block if "AGENTS.md" in line],
                         ["  3 changed files -> AGENTS.md (entry point)"])

    def test_git_runs_without_stdin_fsmonitor_or_optional_locks(self):
        import importlib.util
        from unittest import mock
        spec = importlib.util.spec_from_file_location("docs_check_git", SCRIPT)
        module = importlib.util.module_from_spec(spec)
        sys.modules["docs_check_git"] = module
        self.addCleanup(sys.modules.pop, "docs_check_git", None)
        spec.loader.exec_module(module)
        calls = []

        def fake_run(command, **options):
            calls.append((command, options))
            return subprocess.CompletedProcess(command, 0, "src/a.py\n", "")

        with mock.patch.object(module.subprocess, "run", fake_run):
            changed = module.git_changes(module.Scan(self.root))
        self.assertEqual(changed, ["src/a.py"])
        self.assertEqual(len(calls), 2)
        for command, options in calls:
            self.assertEqual(command[:5], ["git", "-c", "core.quotepath=off", "-c", "core.fsmonitor=false"])
            self.assertIs(options["stdin"], subprocess.DEVNULL)
            self.assertEqual(options["env"]["GIT_OPTIONAL_LOCKS"], "0")
            self.assertTrue(options["timeout"])

    def test_changed_from_git_outside_a_repository_is_a_note(self):
        # The temporary folder is not a Git work tree (TMP is outside any repository here).
        report = self.from_git()
        found = self.finding(report, "git-unavailable")
        self.assertEqual(found["severity"], "note")
        self.assertEqual((report["changed"], report["related"], report["facts"]), ([], [], []))

    def test_changed_from_git_without_git_installed_is_a_note(self):
        env = {key: value for key, value in os.environ.items() if key.upper() != "PATH"}
        env["PATH"] = str(self.root)  # no git here
        report = self.from_git(env)
        self.assertIn("git", self.finding(report, "git-unavailable")["message"])

    def test_text_output_has_related_and_facts_blocks_and_never_says_accurate(self):
        self.write({"AGENTS.md": "# Rules\n\nInvoices: `src/invoice.py`; old: `src/bill.py`. Run `npm run build`.\n",
                    "CLAUDE.md": "@AGENTS.md\n", "package.json": json.dumps({"scripts": {"build": "x"}}), "src/invoice.py": "pass\n"})
        result = self.run_script(str(self.root), "--changed", "src/invoice.py")
        self.assertEqual(result.returncode, 0, result.stderr)
        lines = result.stdout.splitlines()
        related = lines.index("Related documents:")
        facts = lines.index("Facts:")
        self.assertLess(related, facts)
        self.assertIn("  src/invoice.py -> AGENTS.md (names the path)", lines[related + 1:facts])
        block = lines[facts + 1:]
        self.assertIn("  AGENTS.md:3 path src/invoice.py: matched (src/invoice.py exists)", block)
        self.assertTrue(any(line.startswith("  AGENTS.md:3 path src/bill.py: contradicted") for line in block))
        self.assertIn("  AGENTS.md:3 command npm run build: matched (script build in package.json)", block)
        meaning = block.index("Meaning not checked: review each claim in the related documents.")
        self.assertTrue(lines[facts + 1 + meaning + 1].startswith("docs_check: 0 blocking, 1 warning"))
        self.assertNotIn("accurate", result.stdout.lower())

    def test_version_claims_that_read_as_history_are_not_checkable(self):
        report = self.changed("src/main.ts", files={
            "AGENTS.md": ("# Rules\n\nThe [app](src/main.ts) uses Laravel 10.\n"
                          "Upgraded from Laravel 9 to Laravel 10 last year.\n"
                          "Laravel 8 was the version before the migration.\n"
                          "The legacy admin still mentions Laravel 7.\n"),
            "composer.json": json.dumps({"require": {"laravel/framework": "^11.0"}}),
            "src/main.ts": "x\n",
        })
        facts = [(f["line"], f["claim"], f["status"], f["evidence"]) for f in report["facts"] if f["kind"] == "version"]
        self.assertEqual(facts[0][:3], (3, "Laravel 10", "contradicted"))
        self.assertEqual([fact[:3] for fact in facts[1:]], [
            (4, "Laravel 9", "not-checkable"), (4, "Laravel 10", "not-checkable"),
            (5, "Laravel 8", "not-checkable"), (6, "Laravel 7", "not-checkable")])
        self.assertTrue(all(fact[3] == "reads as history" for fact in facts[1:]))

    def test_only_clear_history_words_hide_a_version_claim(self):
        report = self.changed("src/main.ts", files={
            "AGENTS.md": ("# Rules\n\nThe [app](src/main.ts).\n"
                          "Data comes from the API; the app uses Angular 15.\n"
                          "It was fast before, and Angular 16 is old news.\n"
                          "We came from Angular 15 last spring.\n"),
            "package.json": json.dumps({"dependencies": {"@angular/core": "^17.1.0"}}),
            "src/main.ts": "x\n",
        })
        facts = [(f["line"], f["claim"], f["status"]) for f in report["facts"] if f["kind"] == "version"]
        self.assertEqual(facts, [(4, "Angular 15", "contradicted"), (5, "Angular 16", "contradicted"),
                                 (6, "Angular 15", "not-checkable")])

    def test_renamed_file_relates_the_document_that_still_links_the_old_name(self):
        # The file moved from src/old_name.py to src/new_name.py; the document still links the old name.
        report = self.changed("src/old_name.py", "src/new_name.py", files={
            "AGENTS.md": "# Rules\n\nThe entry point is [old name](src/old_name.py).\n",
            "src/new_name.py": "pass\n",
        })
        self.assertEqual(self.related(report), [("src/old_name.py", "AGENTS.md", "links to the path")])
        self.assertEqual(self.finding(report, "broken-link")["line"], 3)


if __name__ == "__main__":
    unittest.main()
