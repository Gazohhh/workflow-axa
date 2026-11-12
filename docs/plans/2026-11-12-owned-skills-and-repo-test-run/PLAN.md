# Owned skills, rule contracts and repo test run

## Current checkpoint
- Updated / phase: 2026-11-12; implementing
- Agreement (gate one): agreed 2026-11-12, agreement 1 (## Agreement below; DECISIONS D1 to D10). Owner's words: "Sure no need for a review codebase mapping design but do document everything in docs so no review.html is needed"
- Approval (gate two): r1 approved, 2026-11-12, no report: "Approve r1, no report"
- Implementation: T1 to T7 implemented; T1, T2, T3, T4, T5, T7 verified; T6 waits on the owner's fresh-session check; T8 (publish, reinstall, after-run) next
- Verification / owner acceptance: V1 baseline; V3-V17 ticket checks and reviews; whole-feature review V17 done; owner acceptance pending; T6 human check pending
- Blockers: none (E1/Q9 answered 2026-11-12)
- Changed files: skills/ (9 merged skills, descriptions, workflow, codebase-map, workflow-doctor, rule-maker rules 1.8.8 and docs_check.py; deleted workflow/specialists.json and scripts/check_specialists.py), tools/validate.py, tools/vendor_specialists.py (deleted), tests/ (test_owned_skills.py new; test_vendored_specialists.py and test_specialists.py deleted; others updated), docs/RULE-CONTRACTS.md (new), AGENTS.md, CONTEXT.md, README.md, CHANGELOG.md, UPGRADE.md, VALIDATION.md, VENDORED-SKILLS.md, docs/ARCHITECTURE.md, docs/DESIGN.md, .claude-plugin/plugin.json, tests/behavioral/*.json; full list: git status
- Next safe action: T8: commit and push this task's files (staged 2026-11-11 records stay out), reinstall Claude and Codex from Git, after-run on the 7 repos, compare

## Working context
- Owner: Gazoh; repository D:\workflow-axa, branch main, main checkout. Existing staged edits in docs/plans/2026-11-11-consistency-review-findings/ (PLAN, FINDINGS, DECISIONS) belong to that task and stay untouched.
- Task identity: new separate task (the request is a new goal; the 2026-11-11 task is delivered).
- Decision check: FINDINGS "Answers" rounds 1 and 2.
- Rules: READY / AGENTS.md, tests/README.md / scope: skills, tools, tests, docs
- Test output folder: .artifacts/2026-11-12-owned-skills-and-repo-test-run/ (baseline/ and after/ kept until owner acceptance; then the raw outputs may go, the comparison stays in FINDINGS)
- Application repos (Altinstar-react, Hooqd, workflow-paperclip, Cheflabels-labeler-V2, D:\PletrixV2, PletrixV2/core): read-only, current branches, no writes, no git actions.

## Goal and acceptance
Owner's words (2026-11-12): "Read UNDERSTANDING.md and let me know what you think and how we could improve all skills. What i also dont like is the references to the skills where we got them originally from i want that out the skills. Also do a test run on all repos here ..."

- A1: No file under skills/ names the projects the copied skills came from (no "Bundled with", no source URL, no source author, no "upstream" in that sense). Each of the 9 formerly copied folders still has its LICENSE.
- A2: Each of the 9 skills reads as one text: no "the adaptation overrides the text above" structure, and no instruction the old adaptation contradicted. Every old adaptation rule is kept or its removal has a DECISIONS entry.
- A3: The hard rules (two approval gates, small change, no new CSS, artifact cleanup) each have a written contract: when it applies, what it covers, what to do when blocked, what checks it (hook, test or instructions only). Every main rule of each skill is labelled hard rule, procedure or judgment call in docs/RULE-CONTRACTS.md. Rules a hook could check but does not are listed as hook candidates.
- A4: The cause of the 6 missing skill descriptions is found and fixed; a fresh session shows the descriptions (human check).
- A5: docs_check no longer reports files inside git-ignored folders at any depth, and reports a tracked third-party folder once instead of once per file.
- A6: validate.py and the full test suite pass; workflow-axa is committed, pushed and reinstalled for Claude and Codex from Git; the read-only checks run again on the 7 repos with the installed copy; the before/after comparison is written in FINDINGS and docs.

## Agreement
Agreement 1, agreed 2026-11-12 ("Sure ..."). Summary as shown in chat the same day:
1. The 9 copied skills become owned single texts; source mentions leave skills/; LICENSE files stay; VENDORED-SKILLS.md becomes a short credits note; vendor_specialists.py and the hash checks retire; tests check LICENSE presence and no source mention instead.
2. Rule contracts for the hard rules; labels for every rule; the skill-listing description problem investigated and only called fixed after a fresh session shows it. No hook changes.
3. docs_check skips git-ignored and third-party folders, with a test.
4. Read-only test run before (done) and after, current branches; push, reinstall from Git, after-run with the installed copy; Altinstar and D:\PletrixV2 rule gaps reported only.

Assumptions (owner may reject): README keeps one credits line (D10); hash tests are replaced, not weakened (D9); the release becomes 2.8.0-rc.37 with rules 1.8.8 (rules files change); reinstall uses the documented install commands in README.md and needs no other global setting change; the staged 2026-11-11 records are not part of this task's commit.

## Approach and scope
Tickets in TODO.md. Parallel groups by file ownership: {T1, T7} first, then {T2, T3}, then T5, T6, T4, T8.
Excluded: hooks/ (D5), application repos (read-only), paid evaluations, the HTML plan report and codebase map (owner's words above).

## Approval

r1 approved 2026-11-12. The owner's first answer "Yes go" (D12) did not carry the report waiver the gate needs (E1); the owner then answered "Approve r1, no report" (D14), which the checkpoint quotes. Includes T1 to T8 as written in TODO.md (r1), including the commit/push of workflow-axa, reinstall of Claude and Codex from Git and verification_summary.py --run --write. Excludes hooks/, application repo writes, paid evaluations, the staged 2026-11-11 records in the commit. Later owner decision inside scope: Q10 a (D17).

## Outcome
