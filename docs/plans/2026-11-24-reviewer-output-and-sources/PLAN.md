# Reviewers read the output first, and cited sources are opened

## Current checkpoint
- Updated / phase: 2026-11-24; closed (released 2.12.0)
- Recipe: docs-tests; modifiers none — only agent instructions and the tests and documents that read them change; scope: the task; classification question: not asked (the request states the outcome)
- Agreement (gate one): not required — one-ticket offer
- Offer: #3 approved (release 2.12.0, D7; supersedes #2, approved and delivered, D1)
- Implementation: implemented (T1 verified)
- Verification / owner acceptance: passed (V8); A5 partial (probes ran before small repairs); owner accepted 2026-11-24 ("yes i accept")
- Blockers: none
- Changed files: the 15 files offer #2 lists (CONTEXT.md, docs/RULE-CONTRACTS.md, nine skill files, tests/README.md, tests/behavioral/cases.json, tests/test_reader_and_sources.py, tests/test_spar.py) and this folder
- Rules: READY / AGENTS.md, CLAUDE.md, CONTEXT.md, tests/README.md, rule-maker START, CORE, READINESS, OPERATIONS / this task / rules 1.9.0 / rules_stamp NONE (information only). docs_check: no blocking finding; two existing warnings in UPGRADE.md:108 are unrelated
- Scope paths: `skills/`, `tests/`, `CONTEXT.md`, `docs/RULE-CONTRACTS.md`
- Next safe action: the owner updates D:/workflow-axa and the installs, then starts new sessions

## Working context
- Owner: Cem. Branch t3/reviewer-output-and-source-checks at 432da9b, equal to main and origin/main after a fetch on 2026-11-24; clean at the start. This worktree only. The hooks and skills of running sessions load from D:/workflow-axa, so edits here do not reach them.
- Task identity: new. The finished spar and approval-hook tasks cover other goals.
- Output folder: .artifacts/2026-11-24-reviewer-output-and-sources/ (ignored); scratch goes after the review, the final suite log stays until acceptance.
- Privacy: the repository is public. No client, project or event names in any file of this change.
- Decision check: FINDINGS Q1.

## Goal and acceptance
- R1 (request, gap 1): when reviewed work produces something a person reads, one reviewer first reads the finished output without the plan, says which question each part answers for its reader, and names the obvious questions it leaves out. Plan and code review follow.
- R2 (request, gap 2): a cited method carries the URL and the quoted sentence or formula that was actually read, or is marked unverified. Question cards and offers are included, and reviewers check it.
- R3 (request): one place per rule, pointers elsewhere.
- A1: the rule for R1 stands in skills/workflow/AUDIT.md only; code-review, plan-review, spar and workflow-deliver point to it at the step where it runs.
- A2: the rule for R2 stands in skills/workflow/WRITING.md only; Unslop 5, grilling, workflow-specify, code-review, plan-review and spar point to it. The two spar briefs repeat one short line, because a debater loads no files.
- A3: a left-out question reaches the owner. It is not filed as a note that nobody acts on.
- A4: text tests fail before the change and pass after it; the full suite and tools/validate.py show no new failure.
- A5: the probes (V-IDs) show that a reviewer with the new text names the missing earlier-period comparison, and that a reviewer opens a cited source and catches a wrong section.

| Requirement and source | Evidence / gap | Acceptance | Work |
|---|---|---|---|
| R1 — request, gap 1 | E1, E2, E3 | A1, A3, A4, A5 | T1 |
| R2 — request, gap 2 | E4, E5, E6 | A2, A4, A5 | T1 |
| R3 — request | E7 | A1, A2 | T1 |

## Approach and scope
One ticket, because both rules change the same skills. The owner files hold the rules; every other edit is a pointer.

Safety assumptions (planning form of BLAST-RADIUS.md): what reads the changed text is listed in FINDINGS E8; each one is checked by its test or by tools/validate.py. Hooks do not parse these sections (E8).

Not included: release, version bump, changelog, commit, push, installing the change, hook changes, a project's CODING_STANDARDS.md.

## Outcome
Delivered 2026-11-24 under offer #2 (D1).

- Asked: two review rules, each in one place, with pointers; plan and offer first.
- Built: AUDIT.md "Output read" and WRITING.md "Cited sources"; Unslop 5 is a pointer; pointers in code-review, plan-review, spar (SKILL.md, T3.md), grilling, workflow-specify and workflow-deliver; the term and owner rows in CONTEXT.md; RULE-CONTRACTS rows; one new test file; B31 and B32 (NOT_RUN); the spar SKILL.md size limit 1700 to 1740.
- Ticket: T1 verified.
- Verdicts: R1, R2 and R3 verified as written text (V4, V8, reviews); A1, A2, A3 and A4 verified; A5 partial: V5 and V6 show both results, but on the text before the review repairs, and the wrong section was also caught with the old text (V2).
- Checks: baseline V3 `Ran 1713 tests` / OK; V7 one failure of this task, repaired; V8 `Ran 1727 tests in 1122.081s` / `OK (skipped=14)`; validate.py PASS.
- Reviews: one independent subagent, both axes plus blast radius, S1 to S6; four findings, all repaired and passed by the same reviewer.
- Limits: FINDINGS UNTESTED; a content fix in a README also triggers the output read; the output reader can return many questions.
- Decisions by the agent: D2, D3, D4, D5.
- Kept: .artifacts/2026-11-24-reviewer-output-and-sources/ baseline.log, after.log, after-2.log until the commit and release decision. Scratch only in the session scratchpad.
- Owner acceptance, 2026-11-24: "yes i accept". It names no commit, push or release.
- Release 2.12.0 (offer #3, D7): the change is commit e931728; version strings, CHANGELOG, UPGRADE, README, ARCHITECTURE, DESIGN and VALIDATION.md follow in the release commit; released as 323c7f9 on origin/main (V10). Not done: D:/workflow-axa, the installed plugin and the Codex copies (the owner updates them); tags and GitHub releases. completion_check does not cover the release files (V9).
