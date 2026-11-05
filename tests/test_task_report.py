"""Exercise the optional task overview through the renderer's public interface."""
from __future__ import annotations

import copy
import html
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("task_report_renderer", ROOT / "skills/codebase-map/scripts/render_report.py")
renderer = importlib.util.module_from_spec(spec)
spec.loader.exec_module(renderer)


def extended(data):
    source = data["sources"][0]["id"]
    evidence = {"source": source, "locator": "Fixture agreement and results"}
    data["task_report"] = {
        "phase": "planning", "screen_change": "none",
        "agreement": {"status": "approved", "revision": "A1", "summary": "Behavior agreed. The plan waits for approval.",
                      "response": "Yes to the described behavior.", **evidence},
        "sections": [{"id": name, "title": name.title(), "text": "Source-backed " + name + ".", **evidence}
                     for name in ("request", "agreement", "specification", "decisions", "risks", "testing")],
        "tickets": [{"task": t["id"], "specification": "Implement " + t["id"] + " through its existing owner.",
                     "expected": "Acceptance for " + t["id"] + " holds through the public interface.", **evidence} for t in data["tasks"]],
        "checks": [], "acceptance_results": [],
    }
    return data


def split(out):
    """Visible report body and the collapsed technical appendix."""
    body = out.split('<main id="report">', 1)[1]
    visible, technical = body.split('<details class="appendix" id="technical-details">', 1)
    return visible, technical


def header(out):
    return out.split('<header class="report-header">', 1)[1].split("</header>", 1)[0]


class TaskReportTests(unittest.TestCase):
    def setUp(self):
        import shutil
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "source"
        shutil.copytree(ROOT / "skills/codebase-map/examples", self.root)
        self.data = json.loads((self.root / "review.json").read_text(encoding="utf-8"))
        self.path = self.root / "candidate.json"

    def render(self):
        self.path.write_text(json.dumps(self.data), encoding="utf-8")
        return renderer.render(self.data, self.root, self.path)

    def test_old_input_does_not_gain_new_sections(self):
        out = self.render()
        self.assertNotIn('id="task-report"', out)
        for legacy in ("Changes and cleanup", "How completion will be checked", "What will not change"):
            self.assertIn(legacy, out)

    def test_legacy_example_renders_unchanged(self):
        import re

        def normal(value):
            for pattern, repl in ((r'"generated_utc": "[^"]+"', ""), (r"Generated [0-9T:.+-]+\.", ""),
                                  (r'"tool_version": "[^"]+"', ""), (r"sha256-[A-Za-z0-9+/=]+", "")):
                value = re.sub(pattern, repl, value)
            return value
        path = self.root / "task-overview.json"
        out = renderer.render(renderer.load_json(path), self.root, path)
        self.assertEqual(normal(out), normal((self.root / "task-overview.html").read_text(encoding="utf-8")))

    def test_planning_shows_agreement_separate_from_plan(self):
        extended(self.data)
        out = self.render()
        visible, technical = split(out)
        self.assertIn('id="task-report"', out)
        self.assertIn("Behavior agreed (A1).", visible)
        self.assertIn("Waiting for your OK on this plan", visible)
        self.assertIn("Yes to the described behavior.", technical)
        for name in ("request", "specification", "decisions", "risks", "testing"):
            self.assertIn("Source-backed " + name + ".", visible)
        for t in self.data["tasks"]:
            self.assertIn('id="spec-' + t["id"] + '"', visible)

    def test_each_fact_appears_once_in_visible_part(self):
        extended(self.data)
        visible, _ = split(self.render())
        facts = ["Source-backed agreement.", "Source-backed decisions.", "Source-backed risks."]
        facts += [row["specification"] for row in self.data["task_report"]["tickets"]]
        facts += [row["text"] for row in self.data["acceptance"]] + self.data["boundaries"]
        for fact in facts:
            with self.subTest(fact=fact):
                self.assertEqual(visible.count(html.escape(fact)), 1)
        for retired in ("Agreement and authority", "Ticket specifications", "Changes and cleanup", "In this report",
                        "How completion will be checked", "What will not change", "do not authenticate approval"):
            self.assertNotIn(retired, visible)
        self.assertNotIn('href="#t-', visible.split('id="what-changes"')[1].split("</section>")[0])

    def test_sections_follow_the_reader_order(self):
        extended(self.data)
        visible, _ = split(self.render())
        headings = ["What you approve", "How it works", "What changes", "The work",
                    "How the work will be checked", "Risks and open questions"]
        positions = [visible.index('<h2 class="section__title" ' + part) for part in ('id="agreed"', 'id="how-it-works"', 'id="what-changes"',
                                                              'id="the-work"', 'id="checks"', 'id="risks"')]
        self.assertEqual(positions, sorted(positions))
        nav = visible.split('<nav class="toc"')[1].split("</nav>")[0]
        for heading in headings:
            self.assertIn(html.escape(heading), nav)

    def test_plain_english_check_names_each_problem_and_its_field(self):
        # Round-14 retro: the plan report kept semicolons and an 8-sentence paragraph.
        spec = importlib.util.spec_from_file_location("task_report_lint", ROOT / "skills/codebase-map/scripts/task_report.py")
        helper = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(helper)
        extended(self.data)
        self.assertEqual(helper.prose_issues(self.data), [])
        section = self.data["task_report"]["sections"][0]
        section["text"] = "We ensure it works; it isn't hard. " + " ".join(["One short sentence."] * 7)
        problems = [problem for path, problem in helper.prose_issues(self.data) if path == f'task_report.sections[{section["id"]}].text']
        for expected in ("semicolon", "words to replace: ensure", "contraction", "paragraph of"):
            self.assertTrue(any(expected in problem for problem in problems), (expected, problems))

    def test_expected_red_check_is_shown_as_such_and_allows_complete(self):
        report = self.delivery()
        report["checks"].append({"id": "V0", "title": "Check before the change", "kind": "test", "status": "red",
                                 "expected": "Fails on the old label", "actual": "RESULT: FAIL", "limits": "None",
                                 "source": report["checks"][0]["source"], "locator": "V0"})
        out = self.render()
        self.assertIn("Failed before the change, as expected", out)
        self.assertNotIn(">Passed</span></li>", out.split('id="check-V0"')[1].split("</li>")[0] + "</li>")

    def test_delivery_scaffold_flags_plan_time_wording(self):
        spec = importlib.util.spec_from_file_location("task_report_stale", ROOT / "skills/codebase-map/scripts/task_report.py")
        helper = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(helper)
        extended(self.data)
        self.data["task_report"]["sections"][0]["text"] = "The script will run at delivery."
        scaffold = helper.scaffold_delivery(self.data)
        self.assertTrue(scaffold["task_report"]["sections"][0]["text"].startswith("FILL: rewrite in the past tense"))

    def test_task_reports_use_the_owner_design_verbatim(self):
        # Owner's report design (2026-11-03): report-style.css and report-extra.js, unchanged; older reports keep report.css.
        assets = ROOT / "skills/codebase-map/assets"
        legacy = self.render()
        extended(self.data)
        out = self.render()
        for name in ("report-style.css", "report-extra.js", "report.js"):
            self.assertIn((assets / name).read_text(encoding="utf-8"), out, name)
        self.assertNotIn((assets / "report.css").read_text(encoding="utf-8"), out)
        self.assertIn((assets / "report.css").read_text(encoding="utf-8"), legacy)
        self.assertNotIn((assets / "report-style.css").read_text(encoding="utf-8"), legacy)
        for marker in ('class="skip-link"', 'class="masthead"', 'class="report-header"', 'class="facts"', 'class="toc"',
                       'class="section__title"', 'class="ticket__stub"', 'class="checks"', 'class="report-footer"'):
            self.assertIn(marker, out)

    def test_friendly_tab_labels_only_with_task_report(self):
        legacy = self.render()
        for label in ("After the change", "Work order", ">Zoom<"):
            self.assertNotIn(label, legacy)
        self.assertIn(">Feature flow</label>", legacy)
        extended(self.data)
        out = self.render()
        for label in ("After the change", "Today", "Work order"):
            self.assertIn(">" + label + "</label>", out)
        self.assertIn(">Zoom<", out)
        self.assertNotIn(">Feature flow</label>", out)

    def test_technical_details_are_collapsed_and_keep_traceability(self):
        extended(self.data)
        out = self.render()
        self.assertIn('<details class="appendix" id="technical-details">', out)
        _, technical = split(out)
        for row in self.data["sources"]:
            self.assertIn('id="s-' + row["id"] + '"', technical)
        for key, prefix in (("requirements", "r"), ("evidence", "e"), ("tasks", "t")):
            for row in self.data[key]:
                self.assertIn('id="' + prefix + "-" + row["id"] + '"', technical)
        self.assertIn("Source: <a href=\"#s-", technical)
        self.assertIn("Fixture agreement and results", technical)

    def test_status_sentence_per_phase(self):
        extended(self.data)
        self.assertIn("Waiting for your OK on this plan", header(self.render()))
        self.data["state"] = "draft"
        self.assertIn("Draft", header(self.render()))
        # Both gates in one message: a draft with nothing open must not say "nothing to approve yet".
        self.data["task_report"]["agreement"] = {"status": "not-approved", "summary": "Asked together with this plan."}
        self.data["open_decisions"] = []
        self.assertIn("Waiting for your OK on the behavior and on this plan", header(self.render()))
        self.data["open_decisions"] = ["Which colour?"]
        self.assertIn("Draft", header(self.render()))
        self.data["open_decisions"] = []
        report = self.delivery()
        self.assertIn("Delivered: complete", header(self.render()))
        report["completion"] = "partial"
        self.data["checkpoint"]["verification"] = {"status": "limited", "summary": "One open"}
        self.assertIn("Delivered: partial", header(self.render()))

    def test_material_missing_agreement_blocks_approval_ready_plan(self):
        extended(self.data)["task_report"]["agreement"] = {"status": "not-approved", "summary": "Waiting for a behavior decision."}
        with self.assertRaisesRegex(ValueError, "agreement"):
            self.render()

    def test_unapproved_agreement_is_honestly_renderable_in_draft(self):
        self.data["state"] = "draft"
        extended(self.data)["task_report"]["agreement"] = {"status": "not-approved", "summary": "Not yet agreed."}
        self.assertIn("Not yet agreed", self.render())

    def test_missing_ticket_is_rejected(self):
        extended(self.data)["task_report"]["tickets"].pop()
        with self.assertRaisesRegex(ValueError, "every task"):
            self.render()

    def test_sourced_content_cannot_reference_missing_file_id(self):
        extended(self.data)["task_report"]["sections"][0]["source"] = "absent"
        with self.assertRaisesRegex(ValueError, "source"):
            self.render()

    def test_unknown_new_keys_are_rejected_but_legacy_keys_remain_compatible(self):
        self.data["legacy_annotation"] = "Preserved legacy behavior"
        self.render()
        extended(self.data)["task_report"]["unrendered_claim"] = "completed"
        with self.assertRaisesRegex(ValueError, "Unknown"):
            self.render()

    def test_narrative_and_review_content_is_inert(self):
        report = extended(self.data)["task_report"]
        report["sections"][0]["text"] = '<script>alert("x")</script> & <img src=x onerror=bad()>'
        out = self.render()
        self.assertNotIn('<script>alert', out)
        self.assertIn('&lt;script&gt;alert', out)

    def delivery(self):
        extended(self.data)
        self.data["report_kind"] = "task-overview"
        self.data["state"] = "draft"
        source = self.data["sources"][0]["id"]
        self.data["checkpoint"] = {"as_of": "Fixture only", "source": source, "locator": "Checkpoint", "next_action": "Deliver results",
            "approval": {"status": "approved", "revision": "P1", "summary": "Synthetic approved plan"},
            "implementation": {"status": "implemented", "summary": "Fixture work complete"},
            "verification": {"status": "passed", "summary": "Fixture checks passed"}}
        report = self.data["task_report"]
        report.update(phase="delivery", completion="complete")
        ev = {"source": source, "locator": "Fixture results"}
        report["sections"].append({"id": "delivery", "title": "Delivery", "text": "Completed with fixture evidence.", **ev})
        report["checks"] = [{"id": "V1", "title": "Public behavior", "kind": "test", "status": "passed", "expected": "Valid scores preserved, negatives rejected", "actual": "Both public callers passed", "limits": "Synthetic fixture only", **ev},
                            {"id": "V2", "title": "Whole-feature review", "kind": "review", "status": "passed", "expected": "Standards and Spec findings resolved", "actual": "No open findings", "limits": "Synthetic fixture only", **ev}]
        report["acceptance_results"] = [{"acceptance": a["id"], "status": "verified", "checks": ["V1"], "note": "Both public callers checked", **ev} for a in self.data["acceptance"]]
        for task in self.data["tasks"]:
            task.update(outcome="verified", outcome_note="Checked by V1")
        return report

    def test_legacy_agreement_is_reported_without_inventing_one(self):
        report = self.delivery()
        report["agreement"] = {"status": "legacy", "summary": "Single-gate approval from 2.7", "source": self.data["sources"][0]["id"], "locator": "DECISIONS D2"}
        out = self.render()
        self.assertIn("older single approval", header(out))
        self.assertIn("Delivered: complete", header(out))
        report["agreement"]["response"] = "Invented consent"
        with self.assertRaisesRegex(ValueError, "response"):
            self.render()

    def test_superseded_acceptance_needs_its_decision_and_is_not_a_pass(self):
        report = self.delivery()
        report["acceptance_results"][0].update(status="superseded", checks=[], note="Descoped by DECISIONS D4")
        report["completion"] = "partial"
        self.data["checkpoint"]["verification"] = {"status": "limited", "summary": "One criterion descoped"}
        self.assertIn("superseded", self.render())
        report["acceptance_results"][0]["checks"] = ["V1"]
        with self.assertRaisesRegex(ValueError, "superseded"):
            self.render()

    def test_stale_check_cannot_verify_acceptance(self):
        report = self.delivery()
        report["checks"][0]["status"] = "stale"
        with self.assertRaisesRegex(ValueError, "passed"):
            self.render()

    def test_complete_delivery_rejects_unreconciled_records(self):
        cases = {
            "blocked ticket": lambda: self.data["tasks"][0].update(outcome="blocked", outcome_note="Device missing"),
            "ticket without outcome": lambda: (self.data["tasks"][0].pop("outcome"), self.data["tasks"][0].pop("outcome_note")),
            "open decision": lambda: self.data["open_decisions"].append("Which brand ships first?"),
            "uncovered requirement": lambda: self.data["requirements"].append({"id": "R99", "text": "Unplanned", "origin": "Fixture"}),
            "no review": lambda: self.data["task_report"]["checks"].pop(),
        }
        for name, change in cases.items():
            with self.subTest(name):
                self.delivery()
                change()
                with self.assertRaisesRegex(ValueError, "complete delivery"):
                    self.render()
                self.data["task_report"]["completion"] = "partial"
                self.data["checkpoint"]["verification"] = {"status": "limited", "summary": "Reconciliation open"}
                self.assertIn("Delivered: partial", self.render())

    def test_delivery_scaffold_renders_unedited_and_claims_nothing(self):
        # Retro E30: every delivery session hand-wrote a 50-80 line generator; 4 of 6 first tries failed.
        spec = importlib.util.spec_from_file_location("task_report_cli", ROOT / "skills/codebase-map/scripts/task_report.py")
        helper = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(helper)
        extended(self.data)
        self.data = helper.scaffold_delivery(self.data)
        report = self.data["task_report"]
        self.assertEqual(report["phase"], "delivery")
        self.assertEqual(report["completion"], "partial")
        self.assertTrue(all(row["status"] == "unverified" for row in report["acceptance_results"]))
        out = self.render()
        self.assertIn("FILL: ", out)
        self.assertIn("Delivered: partial", out)
        # Round-5 retro: the plan's checkpoint and "not built yet" captions contradicted "Delivered".
        self.assertEqual(self.data["checkpoint"]["implementation"]["status"], "implemented")
        self.assertNotIn("Proposed — not built yet", out)
        self.assertNotIn("Proposed is not implemented.", out)
        self.assertIn("As built. The results are below.", out)
        self.assertIn("How it was checked", out)  # round 8: plan-time headings in delivery
        self.assertNotIn("How the work will be checked", out)
        self.assertNotIn("not proof it was implemented", out)
        self.assertTrue(self.data["snapshot"]["basis"].startswith("FILL: "))
        # Round 7: task outcomes were missing and the completeness error named nothing.
        self.assertTrue(all(t["outcome"] == "implemented" for t in self.data["tasks"]))
        self.data["task_report"]["completion"] = "complete"
        with self.assertRaisesRegex(ValueError, "every task outcome verified.*Otherwise use partial"):
            self.render()

    def test_geometry_errors_name_the_node_and_the_limit(self):
        # Retro E23: agents decoded vague renderer errors by reading the source 30 times.
        node = self.data["graphs"][0]["nodes"][0]
        node["label"] = "An extremely long node label nobody can fit"
        with self.assertRaisesRegex(ValueError, r"node " + node["id"] + r": longest line needs ~\d+px, \d+px available"):
            self.render()

    def test_delivery_shows_every_acceptance_and_actual_results(self):
        self.delivery()
        out = self.render()
        visible, _ = split(out)
        self.assertIn('<span>Delivery ' + self.data["revision"] + '</span>', out)
        self.assertEqual(visible.count("Both public callers passed"), 1)
        self.assertIn("Delivered: complete", out)
        for a in self.data["acceptance"]:
            self.assertIn('id="result-' + a["id"] + '"', visible)
            self.assertEqual(visible.count(html.escape(a["text"])), 1)

    def test_verified_acceptance_requires_passed_evidence(self):
        for status in ("failed", "not-run", "blocked", "limited"):
            with self.subTest(status=status):
                report = self.delivery()
                report["checks"][0]["status"] = status
                with self.assertRaisesRegex(ValueError, "passed"):
                    self.render()

    def test_missing_or_unknown_evidence_cannot_verify_acceptance(self):
        for refs in ([], ["V404"]):
            with self.subTest(refs=refs):
                self.delivery()["acceptance_results"][0]["checks"] = refs
                with self.assertRaises(ValueError):
                    self.render()

    def test_partial_delivery_stays_visible(self):
        report = self.delivery()
        report["completion"] = "partial"
        report["acceptance_results"][0].update(status="unverified", checks=[], note="Device unavailable")
        self.data["checkpoint"]["verification"] = {"status": "limited", "summary": "Device unavailable"}
        self.assertIn("Device unavailable", self.render())
        report["completion"] = "complete"
        with self.assertRaisesRegex(ValueError, "complete"):
            self.render()

    def test_delivery_must_account_for_all_acceptance(self):
        self.delivery()["acceptance_results"].pop()
        with self.assertRaisesRegex(ValueError, "every acceptance"):
            self.render()

    def test_nested_unknown_fields_and_duplicate_checks_fail(self):
        self.delivery()["checks"][0]["silently_ignored"] = True
        with self.assertRaisesRegex(ValueError, "Unknown"):
            self.render()
        report = self.delivery()
        report["checks"].append(copy.deepcopy(report["checks"][0]))
        with self.assertRaises(ValueError):
            self.render()



class ScreenChangeTests(unittest.TestCase):
    """Design retro: a visible change was planned with a report copied from a sibling task, without a screen diagram."""
    setUp = TaskReportTests.setUp
    render = TaskReportTests.render

    def test_screen_change_is_required_and_visible_needs_ui_review(self):
        self.data = extended(self.data)
        self.data["state"] = "awaiting-approval"
        self.data["task_report"].pop("screen_change")
        with self.assertRaisesRegex(ValueError, "screen_change is required"):
            self.render()
        self.data["task_report"]["screen_change"] = "visible"
        with self.assertRaisesRegex(ValueError, "needs its screen diagram"):
            self.render()
        self.data["task_report"]["screen_change"] = "maybe"
        with self.assertRaisesRegex(ValueError, '"visible" or "none"'):
            self.render()
        self.data["task_report"]["screen_change"] = "none"
        self.assertIn('id="task-report"', self.render())
        self.data["state"] = "draft"
        self.data["task_report"].pop("screen_change")
        with self.assertRaisesRegex(ValueError, "screen_change is required"):
            self.render()  # a combined-gates plan is a draft and still declares it


class WordingTests(unittest.TestCase):
    """Audit E16-E18: the wording check keeps meaning, skips quoted text and covers every report kind."""
    setUp = TaskReportTests.setUp

    def helper(self):
        spec = importlib.util.spec_from_file_location("task_report_wording", ROOT / "skills/codebase-map/scripts/task_report.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_uncertainty_permission_and_proposal_words_keep_their_meaning(self):
        # Audit E16: replacing these words turned "it could be the cache" into a false certainty.
        helper = self.helper()
        extended(self.data)
        audit = {"could": "The cause is not proven. It could be the cache.",
                 "might": "The phone check might fail on Android 12 because we have no device.",
                 "may": "You may keep the old reports. Workers must not rewrite them.",
                 "would": "The fix would change the score text only if the score is negative.",
                 "should": "We propose that the list should show the newest report first."}
        sections = self.data["task_report"]["sections"]
        for row, sentence in zip(sections, audit.values()):
            row["text"] = sentence
        self.assertEqual(helper.prose_issues(self.data), [])
        notes = dict(helper.prose_notes(self.data))
        for row, word in zip(sections, audit):
            note = notes[f'task_report.sections[{row["id"]}].text']
            self.assertIn(word, note)
            self.assertIn("keep", note)
            self.assertIn("never just delete", note)

    def test_quoted_and_code_text_is_exempt_from_wording_checks(self):
        helper = self.helper()
        extended(self.data)
        sections = self.data["task_report"]["sections"]
        sections[0]["text"] = 'The owner said "it should feel instant" in the agreed answer.'
        sections[1]["text"] = "The owner wrote “keep it fast; keep it small” in the answer."
        sections[2]["text"] = "Run `python -X utf8 -I tools/validate.py; echo done` once."
        self.assertEqual(helper.prose_issues(self.data), [])
        self.assertEqual(helper.prose_notes(self.data), [])

    def test_review_only_report_gets_wording_advice(self):
        # Audit E17: reports without task_report got no wording check at all.
        helper = self.helper()
        self.assertNotIn("task_report", self.data)
        self.data["understanding"] = "The list changes; the old order isn't kept."
        problems = [problem for path, problem in helper.prose_issues(self.data) if path == "understanding"]
        self.assertTrue(any("semicolon" in p for p in problems), problems)
        self.assertTrue(any("contraction" in p for p in problems), problems)

    def test_approved_task_report_is_refused_for_replacement(self):
        extended(self.data)
        self.data["state"] = "approved"
        self.data["approval"] = {"revision": "P1", "record": "PLAN Approval", "response": "Synthetic test response"}
        self.path.write_text(json.dumps(self.data), encoding="utf-8")
        output = self.root / "plan-approved.html"
        output.write_text(renderer.render(self.data, self.root, self.path), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "approved"):
            renderer.unpresented(output, self.root, self.data)

    def test_wording_docs_agree_on_uncertainty_words_and_replacing_drafts(self):
        adaptation = (ROOT / "skills/simple-english/SKILL.md").read_text(encoding="utf-8").split("## workflow-axa adaptation", 1)[1]
        writing = (ROOT / "skills/workflow/WRITING.md").read_text(encoding="utf-8")
        self.assertIn("uncertainty, permission or a proposal", adaptation)
        self.assertIn("never just delete", adaptation)
        self.assertIn("must, may, must not", writing.lower())
        self.assertIn("uncertainty, permission or a proposal", writing)
        self.assertIsNone(helper_contraction(writing), "WRITING.md uses a contraction")
        for path in ("skills/simple-english/SKILL.md", "skills/codebase-map/SKILL.md", "skills/codebase-map/TASK-REPORT.md"):
            text = (ROOT / path).read_text(encoding="utf-8")
            self.assertIn("--replace-unpresented", text, path)
            self.assertNotIn("then render a new file", text, path)


def helper_contraction(text):
    import re
    return re.search(r"\b(?:do|does|did|is|are|was|were|ca|wo|have|has|should|would|could|must)n['’]t\b|\b\w+['’](?:ve|re|ll|m)\b", text, re.I)


if __name__ == "__main__":
    unittest.main()
