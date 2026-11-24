# Tickets

## Overview

| Ticket | What needs to happen | Status | Dependencies |
|---|---|---|---|
| T1 | Reviewers read the output first and open cited sources | Verified | none |

## Tickets

### T1 — Reviewers read the output first and open cited sources
Status: Verified

What needs to happen: add an "Output read" section to AUDIT.md and a "Cited sources" section to WRITING.md, replace the text of Unslop 5 by a pointer, and point to both from the skills that own the step.

What should work:
- Output read (AUDIT.md): applies when reviewed work creates or changes the content of a message, report, dashboard or document for a person. A fresh reviewer gets only the finished output and who reads it. It returns the question each part answers, then the obvious questions left out. Only then do the plan and code reviews start. A left-out question the spec does not exclude in words goes to the owner before delivery. No output yet: use a real or sample one, else NOT VERIFIED. No subagents: self-check, read before the plan, labeled.
- Cited sources (WRITING.md): a source named as authority for a method, formula, number, threshold or standard carries its URL (offline: file and page) and the sentence or formula read there; else "unverified" with the reason. Checked before a question or an offer is sent. A reviewer opens each source itself; a missing or wrong quote is a finding; one it can't open is unverified.
- Pointers: code-review (a step before step 4, step 3's checks, the Standards brief, the result under `## Reader`), plan-review (before step 1; step 3), spar SKILL.md (Evidence; the cited-evidence line) and T3.md (one line in each brief), workflow-deliver step 5, grilling "How to ask", workflow-specify step 5.

Technical details:
- Files: skills/workflow/AUDIT.md, skills/workflow/WRITING.md, skills/code-review/SKILL.md, skills/plan-review/SKILL.md, skills/spar/SKILL.md, skills/spar/T3.md, skills/grilling/SKILL.md, skills/workflow-specify/SKILL.md, skills/workflow-deliver/SKILL.md, CONTEXT.md (term "Output read", two owner rows), docs/RULE-CONTRACTS.md (rows of the changed skills), tests/test_reader_and_sources.py (new), tests/test_spar.py (size limits only), tests/behavioral/cases.json (B31, B32, NOT_RUN), tests/README.md. Must not change: hooks/, tools/, any other file.
- Cleanup: the Unslop 5 sentence it replaces.
- Test seam: the skill texts, read by tests. Catches a lost rule, a lost pointer or a second copy. Misses whether an agent follows it; the probes cover a part of that. TDD: yes for the text tests.
- spar/SKILL.md is close to its tested limit. Cut first; raise the limit only by what the new lines need (at most 60 words each for SKILL.md and T3.md).

Documents: CONTEXT.md, docs/RULE-CONTRACTS.md, tests/README.md

How to verify:
- `python -X utf8 -m unittest discover -s tests -p "test_reader_and_sources.py"`: fails before, passes after.
- Baseline before and full suite after: `python -X utf8 -m unittest discover -s tests -p "test_*.py"`; `python -X utf8 -I tools/validate.py`; log in .artifacts/2026-11-24-reviewer-output-and-sources/.
- At most 4 subagent probes on synthetic material (no client, project or event names): a daily report that compares only with a "usual day", reviewed with the old and with the new text; a plan that cites the wrong section of a public document, reviewed with the old and with the new text.
- One fresh reviewer, writing-for-agents plus AUDIT's categories and BLAST-RADIUS.md; it also checks "one place per rule" and that no client, project or event name is in the diff.

Verification: passed (V4, V8; reviews S1 to S6)

References:
- Supports: R1, R2, R3, A1, A2, A3, A4, A5. Rules: AGENTS.md (tests/README checks first; no commit).
- Depends on: none
- Evidence: V4, V5, V6, V8, reviews S1 to S6
