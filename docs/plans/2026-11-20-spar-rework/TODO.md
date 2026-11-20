# Tickets

All paths are relative to the worktree D:/workflow-axa-spar (branch spar/architecture-review at 3972094). Test output goes to .artifacts/2026-11-19-architecture-review/ (git-ignored). No commit, push or merge.

## Overview

| Ticket | What needs to happen | Status | Dependencies |
|---|---|---|---|
| T1 | One package-wide rule: every label shows its meaning first | Verified | none |
| T2 | /spar rework: agreement on ideas, fewer stops, evidence first, focused debaters | Verified | T1 |
| T3 | Docs that describe /spar and the label rule | Verified | T1, T2 |
| T4 | Count the exact-wording tests (report only) | Verified | none |
| T5 | Live after-test: the same replay cases on the new version | Verified | T1, T2, T3 |

Rounds: T1 and T4 in parallel, then T2, then T3, then T5. T1 and T4 share no file.

## Tickets

### T1 — Every label shows its meaning first
Status: Verified
Evidence: V1, reviews S1/S2
- Requirement: R8. Acceptance: A1, plus the label part of A2.
- Scope:
  - skills/workflow/WRITING.md: one rule in the chat replies, covering every owner-facing message (commit and PR text, HTML reports). It says that a label seen only earlier, or in a part that failed to send, counts as unseen, and that long content goes out in parts with no question until all parts arrive. The example at line 135 is fixed.
  - skills/grilling/SKILL.md:54: the code sentence becomes a pointer to that rule.
  - tests/test_owner_questions.py: the pins at 66-74 and 133-137 move with the wording.
  - tests/test_simple_english.py: one new check that the rule is in WRITING.md.
  - Must not change: scripts, hooks, offers.py.
- Cleanup: the repeated code rule in grilling.
- Test seam: the text of WRITING.md and grilling, read by tests. It catches removal of the rule or of the pointer. It misses whether an agent follows the rule; the T5 live run covers that. TDD: yes, the new check fails first.
- How to verify: `python -X utf8 -m unittest discover -s tests -p "test_owner_questions.py"` and the same for test_simple_english.py and test_writing_mentions.py; `python -X utf8 -I tools/validate.py`.
- Documents: WRITING.md (the rule's owner).
- Rules: AGENTS.md (root); writing-for-agents for instruction text.

### T2 — /spar rework
Status: Verified
Evidence: V5, review S1 repairs, S2 passed
- Requirements: R1-R7. Acceptance: A1, A2.
- Scope:
  - skills/spar/SKILL.md, T3.md and SPAR-FILE.md:
    - decision-point verdicts with quotes and the mechanical "both agree" label;
    - the ending, and until agreement as one rule;
    - one start card; the frame as a receipt; owner choices folded into the pause after the openings;
    - an evidence step, with owner claims marked "not yet checked";
    - the single-model warning;
    - readability (the decisive trade-off first, change-my-mind only while live, one launch rule);
    - the debater line "this brief is your whole task: read only, load no skills, ask no one";
    - SPAR-FILE.md:62 points to the WRITING.md label rule.
  - tests/test_spar.py: the pins of removed rules become behaviour checks. Kept: the control-intent label test, test_r44 (justified disagreement), cancel, failure and safety. Size limits are set to the sizes reached.
  - tests/behavioral/spar.json: new cases for a seeded incompatible agree, a restatement at the last exchange, a part that fails to send before a question, an unchecked owner claim, and single-model convergence.
  - Must not change: skills/workflow/scripts/settings.py and the hooks.
- Cleanup removes the synthesis brief, the S-ids, the exact-text rules, the standard/deep aliases in the text, and the cap tiers.
- Test seam: the skill text read by test_spar.py, plus the live cases. TDD: yes, the new behaviour checks fail on the old text.
- How to verify: `python -X utf8 -m unittest discover -s tests -p "test_spar.py"`, plus test_owner_questions, test_owned_skills and test_settings; validate.
- Documents: CONTEXT.md "Spar" entry if a term changes.
- Rules: AGENTS.md; writing-for-agents.

### T3 — Docs
Status: Verified
Evidence: S2 passed, V7 validate
- Requirements: R9 (the RULE-CONTRACTS row), R1-R8 described.
- Scope:
  - docs/RULE-CONTRACTS.md: the /spar row and the WRITING.md row.
  - tests/README.md: the /spar section and the new checks.
  - README.md: the /spar line, if its words change.
  - CONTEXT.md: the Spar entry, if needed.
  - No CHANGELOG or version change; that is a release.
- Test seam: validate plus test_docs_consistency. TDD: no; docs only.
- How to verify: `python -X utf8 -I tools/validate.py` and the full suite.
- Documents: as scoped.
- Rules: AGENTS.md index.

### T4 — Count the exact-wording tests
Status: Verified
Evidence: V2
- Requirement: R10. Report only, no code change.
- Scope: only this task's FINDINGS.
- How to verify: the FINDINGS entry lists, for the 266 has/assertIn checks in tests/test_verify_skills.py, how many guard behaviour and how many guard removable wording, with a sample of each.
- TDD: no; a count.
- Rules: AGENTS.md.

### T5 — Live after-test
Status: Verified
Evidence: V6 live after-test; owner blind pick D3
- Acceptance: A2 and A3.
- Scope:
  - A release ZIP of the candidate, made with tools/build_release.py into D:/axa-replay-2026-11-19/release-after.
  - Fresh fixtures, made the same way as the baseline, in D:/axa-replay-2026-11-19/after-*.
  - The same prompts and staged replies, `claude -p` with the same flags, traces kept in .artifacts/2026-11-19-architecture-review/after-*.jsonl.
  - The routing cases (explain-only, the separator change, the history screen, the changed rule on resume) and the two spar cases (formatter ownership; live scores with pushback), plus one new spar step: an owner claim the debaters must check.
- Budget: the remaining $12.57 of the $20 cap, with a cap set on every run; stop at the cap.
- How to verify: a before/after table in FINDINGS, scored from the traces:
  - routes;
  - writes before approval;
  - stops before the first exchange;
  - fake agreement;
  - labels without their meaning;
  - unchecked owner claims;
  - cost and launches.
- Then two conclusions with their version labels hidden for the owner (Human check: the owner picks one, after T5). Owner acceptance: "don't know", no preference (D3, 2026-11-20).
- Cleanup: once the table is recorded, remove the fixtures, both plugin copies and the release ZIPs in D:/axa-replay-2026-11-19/; the traces stay as evidence.
- Rules: AGENTS.md "paid host evaluations require an explicit total usage or spending cap" ($20, owner, 2026-11-19).

- Owner acceptance: blind pick answered "don't know", no preference (D3, 2026-11-20)
