"""tools/stage_candidate.py and the candidate texts applied at the T17 cutover (docs/plans/2026-11-15-workflow-redesign)."""
from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("stage_candidate_under_test", ROOT / "tools/stage_candidate.py")
stage = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = stage
spec.loader.exec_module(stage)


# T24 rewrote these T17 blocks for the offer model (small change folded into the one-ticket offer, report only on
# html-first or when asked, answers owned by specify). Key: (file, first 50 characters of the T17 new text); value:
# the file and phrase that replace it. The T17 old text must still be gone.
SUPERSEDED_BY_T24 = {
    ("skills/workflow-specify/SKILL.md", "First compare every ticket with the agreement line"):
        ("skills/workflow-specify/SKILL.md", "Then write the **offer** (the minimal offer for a lightweight edit, "
                                             "one ticket's paths for one-ticket work)"),
    ("skills/workflow-specify/SKILL.md", "Done when the offer was presented and the one ques"):
        ("skills/workflow-specify/SKILL.md", "Record the owner's choice with `record.py offer presentation"),
    ("skills/workflow-specify/SKILL.md", "The hook reads the answer from the conversation; n"):
        ("skills/workflow-specify/SKILL.md", "This step owns qualified answers and corrections."),
    ("skills/workflow/VISUAL-REVIEW.md", "The answer to the one question decides; the hook r"):
        ("skills/workflow/VISUAL-REVIEW.md", "Qualified answers, corrections and what to record: `workflow-specify` "
                                             "step 5 owns them."),
    ("skills/workflow/VISUAL-REVIEW.md", "| 2 — Implementation approval | Tickets, dependenc"):
        ("skills/workflow/VISUAL-REVIEW.md", "| 2 — Implementation approval | The offer: behavior summary, paths, "
                                             "operations, exclusions and checks |"),
    ("skills/workflow/VISUAL-REVIEW.md", "- **Every implementation approval is an offer with"):
        ("skills/workflow/VISUAL-REVIEW.md", "the minimal offer for a lightweight edit (files, check, one-line why), "
                                             "one ticket for one-ticket work"),
    ("skills/workflow/VISUAL-REVIEW.md", "1. Write the task record first, making the task cu"):
        ("skills/workflow/VISUAL-REVIEW.md", "**No separate agreement** for a lightweight edit, or for one-ticket work"),
    ("skills/workflow/VISUAL-REVIEW.md", "Changing the file list or the description is a rev"):
        ("skills/workflow-specify/SKILL.md", "Any change to the offer's allowed paths, operations or checks needs a "
                                             "revised offer"),
    ("skills/workflow/VISUAL-REVIEW.md", "The hook enforces the offer's paths and the owner'"):
        ("skills/workflow/VISUAL-REVIEW.md", "The hook enforces the offer's paths, operations and the owner's answer."),
    ("skills/workflow/VISUAL-REVIEW.md", "4. The owner asked for this report with *Show revi"):
        ("skills/workflow/VISUAL-REVIEW.md", "present the offer again as `workflow-specify` step 5 says, so the owner "
                                             "can now answer *Approve from this summary* or *Change something*"),
}

# Speed 2.10 moved these T17 blocks, word for word, into on-demand files; the source keeps a pointer section.
MOVED_IN_2_10 = {
    ("skills/workflow/VISUAL-REVIEW.md", "This applies only to tasks the owner listed as pre"):
        "skills/workflow/LEGACY-APPROVALS.md",
}


class CandidateBlocks(unittest.TestCase):

    def test_the_cutover_applied_every_block(self):
        """T17: the package carries the new text; a block whose new text contains its old text only needs the new.
        A block T24 (or 2.9.0-rc.2) rewrote carries its replacement instead (SUPERSEDED_BY_T24)."""
        found, moved = set(), set()
        for rel, old, new in stage.blocks(stage.CANDIDATES.read_text(encoding="utf-8")):
            with self.subTest(rel=rel, new=new[:50]):
                if (rel, new[:50]) in MOVED_IN_2_10:
                    moved.add((rel, new[:50]))
                    rel = MOVED_IN_2_10[(rel, new[:50])]
                text = (ROOT / rel).read_text(encoding="utf-8").replace("\r\n", "\n")
                replacement = SUPERSEDED_BY_T24.get((rel, new[:50]))
                if replacement:
                    found.add((rel, new[:50]))
                    self.assertNotIn(new, text)
                    self.assertIn(replacement[1], (ROOT / replacement[0]).read_text(encoding="utf-8"))
                else:
                    self.assertIn(new, text)
                if old not in new:
                    self.assertNotIn(old, text)
        self.assertEqual(found, set(SUPERSEDED_BY_T24))  # every listed block still exists in the candidates
        self.assertEqual(moved, set(MOVED_IN_2_10))


class Staging(unittest.TestCase):

    def test_a_folder_it_did_not_make_is_never_replaced(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            out.mkdir()
            (out / "keep.txt").write_text("x", encoding="utf-8")
            with self.assertRaises(SystemExit):
                stage.fresh(out)
            self.assertTrue((out / "keep.txt").is_file())
            (out / "keep.txt").unlink()
            (out / stage.MARKER).write_text("x", encoding="utf-8")
            stage.fresh(out)  # its own folder: replaced
            self.assertTrue((out / stage.MARKER).is_file())


if __name__ == "__main__":
    unittest.main()
