"""The T17 cutover of docs/plans/2026-11-15-workflow-redesign: no active text keeps the old route, the registered hook
is the one that runs, a legacy task still works through it, and rolling back to rc.39 refuses rather than trusts."""
from __future__ import annotations

import hashlib
import io
import json
import os
import re
import subprocess
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
STALE = [
    "No new CSS, ever",
    "Record the answer in the checkpoint `Approval` line",
    "Every implementation approval request comes with a fresh HTML report",
    "A clear \"yes, proceed\" to this report approves",
    "Useful comment:",
    "Missing prerequisites produce a clear stop",
    "offer setup, limited exception, read-only inspection or stop",
    "Approval` is approved, legacy or an explicit waiver",  # T24: execute checks the offer, not an Approval line
]
STALE_PATTERNS = [  # the variants Astra found after the first cutover review
    r"(?<!switch off, )never (?:write or )?offer new CSS",
    r"(?<!switch off, )never write CSS",
    r"never include new CSS",
    r"read checkpoint Agreement and Approval",
    r"approved by one quoted owner yes",
    r"Implementation approval\*\* of tickets, tests and the plan report",
    r"tickets or plan report unapproved",
]
RC39 = "bfc18fd"  # the rc.39 delivery commit this redesign started from (D2); not HEAD, which moves on
NOT_ACTIVE = ("skills/rule-maker/rules/CHANGES.md", "skills/rule-maker/rules/SOURCES.md")


def registered_pretooluse() -> str:
    data = json.loads((ROOT / "hooks/hooks.json").read_text(encoding="utf-8"))
    return data["hooks"]["PreToolUse"][0]["hooks"][0]["command"]


def run_command(command: str, event: dict, env: dict) -> dict | None:
    """The registered command as the host runs it: ${CLAUDE_PLUGIN_ROOT} is the package root."""
    args = [a.replace("${CLAUDE_PLUGIN_ROOT}", str(ROOT)) for a in re.findall(r'"[^"]*"|\S+', command)]
    args = [a.strip('"') for a in args]
    args[0] = sys.executable if args[0] == "python" else args[0]
    done = subprocess.run(args, input=json.dumps(event), capture_output=True, text=True, encoding="utf-8",
                          env={**os.environ, **env})
    assert done.returncode == 0, done.stderr
    return json.loads(done.stdout)["hookSpecificOutput"] if done.stdout.strip() else None


class ActiveText(unittest.TestCase):

    def test_no_active_file_keeps_the_old_approval_route_css_ban_or_comment_advice(self):
        for path in sorted((ROOT / "skills").rglob("*.md")):
            rel = path.relative_to(ROOT).as_posix()
            if rel in NOT_ACTIVE or "/examples/" in rel:
                continue
            text = path.read_text(encoding="utf-8")
            for phrase in STALE:
                with self.subTest(file=rel, phrase=phrase):
                    self.assertNotIn(phrase, text)
            for pattern in STALE_PATTERNS:
                with self.subTest(file=rel, pattern=pattern):
                    self.assertIsNone(re.search(pattern, text, re.I))

    def test_lightweight_edits_and_small_changes_also_end_with_the_one_question(self):
        # T24: the small-change route is folded into the one-ticket offer; a lightweight edit gets the minimal offer.
        router = (ROOT / "skills/workflow/SKILL.md").read_text(encoding="utf-8")
        self.assertIn("**Every change** gets an offer and the one question", router)
        self.assertIn("A lightweight edit gets the minimal offer (its files, its check and a one-line why) through "
                      "`workflow-specify` step 5, and is still asked the one question", router)
        self.assertIn("One-ticket work, a small visible change included, gets one ticket and its offer", router)
        self.assertIn("The plan report is built only on *Show review.html first* or when the owner asks for it", router)


class OfferModelText(unittest.TestCase):
    """T24: the phase texts match the offer model (REDESIGN.md §3.2, §6 rows 1-5)."""

    def read(self, rel: str) -> str:
        return (ROOT / rel).read_text(encoding="utf-8")

    def test_lightweight_gets_the_minimal_offer_and_small_changes_the_one_ticket_offer(self):
        specify = self.read("skills/workflow-specify/SKILL.md")
        self.assertIn("A lightweight edit gets no ticket: step 5's **minimal offer** names its files, its check and a "
                      "one-line why", specify)
        self.assertIn("One-ticket work, a small visible change included, gets one ticket and the **one-ticket offer**",
                      specify)
        self.assertIn("A ticket list is for multi-ticket work only", specify)
        glossary = self.read("CONTEXT.md")
        self.assertIn("it gets the minimal offer (its files, its check and a one-line why) and the one question", glossary)
        self.assertIn("now absorbed into the one-ticket offer", glossary)

    def test_offers_are_made_only_through_specify(self):
        # T26 F2 (live run r20): the agent wrote an offer in its own words and asked "Go ahead?"; the hook could
        # never approve that, because no recorded offer was presented.
        router = " ".join(self.read("skills/workflow/SKILL.md").split())
        self.assertIn("Make and present it only through `workflow-specify`: it records the offer with "
                      "`record.py offer create` and shows its canonical block.", router)
        self.assertIn("An offer in your own words, or any other question, can't be approved", router)

    def test_a_stop_pauses_and_continue_keeps_the_approval(self):
        # Astra (T24 result): the text required a new presentation after a stop, unlike the hook (stop = pause).
        review = " ".join(self.read("skills/workflow/VISUAL-REVIEW.md").split())
        self.assertIn("A stop only pauses the work: when the owner says to continue, the approval holds again with no "
                      "new question", review)
        self.assertIn("A later withdrawal or narrowing ends it: present the offer again", review)
        self.assertNotIn("narrowing or stop; then present the offer again", review)

    def test_deliver_builds_a_missing_review_from_the_owner_of_report_preparation(self):
        # Opus (T24 round 2): the pointer named TASK-REPORT.md, which says nothing about building a review.json.
        deliver = self.read("skills/workflow-deliver/SKILL.md")
        self.assertIn("first build one for the approved offer as `../workflow/VISUAL-REVIEW.md` \"Prepare the report\" "
                      "step 2 describes", deliver)
        self.assertIn("## Prepare the report", self.read("skills/workflow/VISUAL-REVIEW.md"))

    def test_report_only_on_html_first_or_when_asked(self):
        self.assertIn("The plan report is built only on *Show review.html first* or when the owner asks",
                      self.read("skills/workflow-specify/SKILL.md"))
        self.assertIn("when the offer's presentation decision was `html-first` or the owner asks for one",
                      self.read("skills/workflow-deliver/SKILL.md"))
        gates = self.read("skills/workflow/VISUAL-REVIEW.md")
        self.assertIn("The HTML report is built only when the owner answers *Show review.html first*, or asks for it",
                      gates)
        self.assertIn("When the offer's presentation decision was `html-first`, make a new dated snapshot", gates)
        self.assertNotIn("no HTML snapshot", self.read("skills/workflow-deliver/SKILL.md"))

    def test_deliver_has_an_unknown_verdict(self):
        deliver = self.read("skills/workflow-deliver/SKILL.md")
        self.assertIn("| Unknown (`unknown`", deliver)
        self.assertIn("say so plainly, never guess a verdict", deliver)

    def test_execute_verifies_the_offer_from_evidence(self):
        execute = self.read("skills/workflow-execute/SKILL.md")
        self.assertIn("the checkpoint names `Offer: #<id>` covering these tickets, and approval is verified from "
                      "evidence, as `resume` requires: the offer's presentation, the owner's decision and any later "
                      "stop, withdrawal or narrowing", execute)
        self.assertIn("An `Approval` line counts only for a legacy task", execute)
        # Negative: the Offer line by itself is never treated as approval.
        self.assertIn("The `Offer:` line alone is not authority", execute)
        self.assertIsNone(re.search(r"`Offer: #<id>`[^.;]*\b(?:is enough|suffices|means approved|approves)", execute))
        self.assertNotIn("Adapts Implement Spec", execute)

    def test_no_active_phase_file_keeps_the_old_routes(self):
        files = ["skills/workflow/SKILL.md", "skills/workflow/VISUAL-REVIEW.md", "skills/workflow/TASK-FOLDER.md",
                 "skills/ui-design/SKILL.md"] + [f"skills/workflow-{p}/SKILL.md" for p in
                                                 ("clarify", "specify", "execute", "deliver")]
        for rel in files:
            text = self.read(rel)
            for phrase in ("Both gates in one message", "skips both", "## Small change", '"Small change"',
                           "small change route", "Small change:"):
                with self.subTest(file=rel, phrase=phrase):
                    self.assertNotIn(phrase, text)
            with self.subTest(file=rel, phrase="small change as a route"):
                self.assertIsNone(re.search(r"(?i)\bsmall change\b", text))


    def test_no_waiver_or_report_approval_outside_the_phase_files(self):
        # Opus (T24 result): AUDIT, the glossary and the Codex metadata still described the two-gate model.
        audit = " ".join(self.read("skills/workflow/AUDIT.md").split())
        self.assertNotIn("explicit bounded waiver", audit)
        self.assertIn("an approved offer, verified from its presentation and the owner's answer", audit)
        glossary = " ".join(self.read("CONTEXT.md").split())
        self.assertNotIn("the plan report with its tickets and checks, which permits code changes", glossary)
        self.assertNotIn("The report shown for implementation approval", glossary)
        self.assertIn("The owner's answer to the one question that approves an offer", glossary)
        for meta in sorted((ROOT / "skills").glob("*/agents/openai.yaml")):
            with self.subTest(meta=meta.parent.parent.name):
                self.assertNotRegex(meta.read_text(encoding="utf-8"), r"(?i)plan report approved|both gates|small change")


class ReleaseNotes(unittest.TestCase):
    """T25: the current CHANGELOG entry names what the redesign removed and added, and those facts hold."""

    def current_entry(self) -> str:
        version = json.loads((ROOT / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))["version"]
        text = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
        start = text.index(f"\n## {version} — ")
        end = text.find("\n## ", start + 1)
        return text[start:end if end != -1 else len(text)]

    def test_the_entry_names_the_removed_hooks_and_the_three_new_skills(self):
        entry = self.current_entry()
        for hook in ("plain_reply.py", "phase_reads.py", "truncated_read.py"):
            with self.subTest(hook=hook):
                self.assertIn(f"`{hook}`", entry)
                self.assertFalse((ROOT / "hooks" / hook).exists())
        registered = json.loads((ROOT / ".claude-plugin/plugin.json").read_text(encoding="utf-8"))["skills"]
        for skill in ("interrogate", "no-comments", "wait-what"):
            with self.subTest(skill=skill):
                self.assertIn(f"`{skill}`", entry)
                self.assertIn(f"./skills/{skill}", registered)


class PhaseReferences(unittest.TestCase):
    """T20: with the reminder hooks gone, each phase names the files it needs (the READS table in read_evidence.py)."""

    def test_every_phase_names_its_required_reads(self):
        import importlib.util
        spec = importlib.util.spec_from_file_location("read_evidence_refs", ROOT / "hooks/read_evidence.py")
        evidence = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(evidence)
        for phase, files in evidence.READS.items():
            text = (ROOT / "skills" / phase / "SKILL.md").read_text(encoding="utf-8")
            for rel in files:
                with self.subTest(phase=phase, file=rel):
                    self.assertIn(rel, text)


class RegisteredHook(unittest.TestCase):

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.base = Path(tmp.name)
        self.repo = self.base / "repo"
        (self.repo / ".git").mkdir(parents=True)
        (self.repo / "src").mkdir()
        (self.repo / "src/vat.ts").write_text("export const vat = 1;\n", encoding="utf-8")
        self.env = {"WORKFLOW_AXA_HOME": str(self.base / "home"), "WORKFLOW_AXA_GATE_CACHE": str(self.base / "cache"),
                    "WORKFLOW_AXA_SETTINGS": str(self.base / "settings.json")}

    def test_the_registered_command_runs_the_offer_checker_and_a_listed_legacy_task_through_it(self):
        from test_phase_gate_hook import APPROVED, ROUTER, hooked, say, tool, user
        self.assertIn("approval.py", registered_pretooluse())
        task = self.repo / "docs/plans/2026-11-01-legacy"
        (task / "reviews").mkdir(parents=True)
        (task / "reviews/plan-r1.html").write_text("<!DOCTYPE html>", encoding="utf-8")
        (task / "PLAN.md").write_text(f"# Legacy\n\n## Current checkpoint\n{APPROVED}\n", encoding="utf-8")
        rows = [ROUTER, tool("Write", file_path=str(task / "TODO.md"), content="x"),
                say(f"Plan report: {task / 'reviews/plan-r1.html'}. Approve?"), user("Yes to both")]
        transcript = self.base / "s.jsonl"
        transcript.write_text("\n".join(json.dumps(r) for r in hooked(rows, self.repo)), encoding="utf-8")
        event = {"hook_event_name": "PreToolUse", "tool_name": "Edit", "cwd": str(self.repo),
                 "transcript_path": str(transcript),
                 "tool_input": {"file_path": str(self.repo / "src/vat.ts"), "old_string": "1", "new_string": "2"}}
        out = run_command(registered_pretooluse(), event, self.env)
        self.assertIn("approved offer", out["permissionDecisionReason"])  # not listed: offers only
        script = ROOT / "skills/workflow/scripts/legacy_inventory.py"
        subprocess.run([sys.executable, "-X", "utf8", "-I", str(script), "--apply", str(self.repo)], check=True,
                       capture_output=True, env={**os.environ, **self.env})  # the owner's step at the upgrade
        self.assertIsNone(run_command(registered_pretooluse(), event, self.env))  # listed: the legacy checker decides


class RollbackToRc39(unittest.TestCase):
    """UPGRADE.md "Back to rc.39": rc.39 doesn't read offers, so an offer-only task is refused there, and its offer
    files are left as they are."""

    def test_rc39_refuses_an_offer_only_task_and_keeps_its_offers(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            rc39 = base / "rc39"
            archive = subprocess.run(["git", "-C", str(ROOT), "archive", RC39, "hooks", "skills"],
                                     capture_output=True, check=True).stdout
            with tarfile.open(fileobj=io.BytesIO(archive)) as tar:
                tar.extractall(rc39, filter="data")
            self.assertFalse((rc39 / "hooks/approval.py").exists())  # really the pre-cutover package
            repo = base / "repo"
            (repo / ".git").mkdir(parents=True)
            (repo / "src").mkdir()
            (repo / "src/vat.ts").write_text("export const vat = 1;\n", encoding="utf-8")
            task = repo / "docs/plans/2026-11-20-offer-only"
            (task / "offers").mkdir(parents=True)
            (task / "PLAN.md").write_text("# Offer task\n\n## Current checkpoint\n- Offer: #1 approved\n", encoding="utf-8")
            offer = task / "offers/offer-1.json"
            offer.write_text('{"id": 1, "state": "approved"}\n', encoding="utf-8")
            before = hashlib.sha256(offer.read_bytes()).hexdigest()
            from test_phase_gate_hook import ROUTER, tool, user
            transcript = base / "s.jsonl"
            transcript.write_text("\n".join(json.dumps(r) for r in [
                ROUTER, tool("Write", file_path=str(task / "TODO.md"), content="x"), user("approve")]), encoding="utf-8")
            event = {"tool_name": "Edit", "cwd": str(repo), "transcript_path": str(transcript),
                     "tool_input": {"file_path": str(repo / "src/vat.ts"), "old_string": "1", "new_string": "2"}}
            done = subprocess.run([sys.executable, "-X", "utf8", "-I", str(rc39 / "hooks/phase_gate.py"),
                                   "--hook-protocol=1"], input=json.dumps(event), capture_output=True, text=True,
                                  encoding="utf-8", env={**os.environ, "WORKFLOW_AXA_GATE_CACHE": str(base / "cache")})
            self.assertEqual(json.loads(done.stdout)["hookSpecificOutput"]["permissionDecision"], "deny", done.stderr)
            self.assertEqual(hashlib.sha256(offer.read_bytes()).hexdigest(), before)


if __name__ == "__main__":
    unittest.main()
