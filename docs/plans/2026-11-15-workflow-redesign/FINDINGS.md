# Findings

## Checks (V)
- V1 baseline (2026-11-15, bfc18fd, clean worktree): validate.py exit 0 (21 skills); unittest 1229 tests OK, 13 skipped, ~300 s.

- V2 historical sample (T2; `digest_sessions.py --counts --min-user 5` over every local Claude Code project, sessions started 2026-11-12/13). **A mixed rc.38/rc.39 sample, not a matched baseline:** each session's plugin version, model and environment are unknown (not recorded in the transcripts we read). Approval and process counts are heuristics; denial reasons count workflow-axa refusals only. 10 sessions: 352 human messages, 44 approval messages, 72 process-only turns, 131 hook denials. T26 compares per comparable scenario, never these aggregates alone.

| session | start | human messages | approval messages | process-only turns | hook denials | workflow-axa denials by reason |
|---|---|---|---|---|---|---|
| 6d180d94 | 2026-11-12 | 13 | 4 | 6 | 13 | other 6, use record.py 4, no plan report 1, install 1, quote not matched 1 |
| c63ac027 | 2026-11-12 | 21 | 3 | 3 | 11 | no plan report 7, plan not seen as presented 3, required reads 1 |
| 25eea459 | 2026-11-12 | 23 | 6 | 7 | 18 | plan not seen as presented 4, use record.py 3, task switch 3, no plan report 2, install 2, quote not matched 2, required reads 1, other 1 |
| cca197d4 | 2026-11-12 | 45 | 2 | 9 | 13 | use record.py 3, no plan report 3, quote not matched 3, required reads 2, plan not seen as presented 1, answer before presentation 1 |
| 2346530a | 2026-11-12 | 66 | 4 | 8 | 22 | quote not matched 16, use record.py 2, required reads 1, other 1, no plan report 1, plan not seen as presented 1 |
| 2986f1c5 | 2026-11-13 | 15 | 2 | 4 | 4 | use record.py 2, required reads 1, other 1 |
| 03802d78 | 2026-11-13 | 30 | 6 | 6 | 9 | no plan report 4, other 2, use record.py 1, plan not seen as presented 1, answer before presentation 1 |
| b129a6da | 2026-11-13 | 34 | 11 | 16 | 9 | no plan report 3, plan not seen as presented 2, task switch 2, use record.py 1, required reads 1 |
| 0988be64 | 2026-11-13 | 6 | 0 | 0 | 4 | use record.py 1, other 1, quote not matched 1, install 1 |
| 70ac997a | 2026-11-13 | 99 | 6 | 13 | 28 | other 8, plan not seen as presented 5, use record.py 4, task switch 4, required reads 3, install 2, quote not matched 2 |

Raw per-project tables: `.artifacts/2026-11-15-workflow-redesign/baseline/` (ignored; kept until the T26 comparison, then removable).

## Reviews (one line per ticket: Opus verdict, Astra verdict, round)
- Execution plan (PLAN/TODO/DECISIONS): Opus Agree; Astra Disagree r1 (8 changes, applied), Disagree r2 (2 sequencing changes, applied), Agree r3.
- T1: Opus Agree; Astra Disagree r1 (P3 reason assertion, applied), Agree r2. `tests/test_session_failures.py`: 6 OK (3 expected failures, removed in T7).
- T2: Opus Agree; Astra Disagree r1 (labels, negative cases, sample wording; applied), Agree r2. test_owned_skills 10 OK.
- T3: Opus Agree; Astra Disagree r1 (4 contract summaries corrected), Agree r2. RULE-CONTRACTS redesign section.
- T4: Opus Agree; Astra Disagree r1 (no blocking ceiling assertion; manifest entries validated before use), Disagree r2 (synthetic ceiling file), Agree r3. budgets 10, package 19, contract 8 OK.
- V3: the checkpoint-1 full run (.artifacts/.../suite/cp1.txt) overlapped T4 edits; its one failure was the old synonym CLI test against the new validate.py. Not valid checkpoint evidence; a clean full run is required at the end of checkpoint 2.
- T4 reopened by Opus after the full suite (licence check lost from validate); fixed (licensed skills read from VENDORED-SKILLS credits table); Astra Agree.
- T5: Opus Agree; Astra Disagree r1 (zero-test/unsummarised pass, unknown identity, unittest labels with spaces, unreadable file), Agree r2. test_docs_consistency 30 OK. Pre-existing bug fixed: expected failures were counted as failures.
- V4: clean full suite after T4 fix (before T5 fixes): 1251 tests OK, 13 skipped, 3 expected failures (.artifacts/.../suite/t5.txt).
- T6: Opus Agree; Astra Disagree r1 (explicit scope fields, folder overlap, task at last user message), Disagree r2 (whole-field validation), Agree r3. test_required_reads 13 OK.
- T6 reopened by Opus after the full suite (missing parser failed open); fixed to fail closed; Astra Agree.
- V5 checkpoint 2 gate: clean full suite 1268 tests OK, 13 skipped, 3 expected failures (.artifacts/.../suite/cp2.txt); validate PASS.
- T7: Opus Agree; Astra Disagree r1 (workspace and task binding of earlier small yes, unambiguous pre-task waiver, doc wording), Agree r2. test_session_failures 17 OK; full suite 1279 OK.
- T8: Opus Agree; Astra Agree r1.
- V6 checkpoint 3 gate: full suite 1282 OK (13 skipped), validate PASS (.artifacts/.../suite/cp3.txt).
- T9: Opus Agree; Astra Disagree r1 (5 changes), Disagree r2 (full allowance list), Agree r3. test_flows 10 OK.
- T10: Opus Agree; Astra Disagree r1 (transition rule in new-project, ui routing wording, conditional done-claim blocks), Agree r2. test_flows 14 OK.

## T11 rules-library checklist (29 modules)

Scan by a read-only subagent (scope, protection or preference, duplication, dated claims, conflicts with the redesign), then decisions by Opus. "Mandatory" = a conflict with the agreed architecture, fixed in T11 (or candidate text in `candidates/READINESS-SKIP.md`, applied at T17). "Optional" = a separate improvement, not done here.

| Module | Mandatory edit (T11) | Optional follow-up |
|---|---|---|
| START | CSS example list → pointer to DESIGN.md; "clear stop" wording → candidate | routing table overlaps ENGINEERING |
| CORE | CSS copy → pointer; comment rules (required + default, Rust SAFETY exception); subtract-first and root-cause defaults; two sentences that repeated POLICY/OPERATIONS shortened | none |
| READINESS | CSS copy → pointer; set-up/skip wording, "all unclassified missing prerequisites block" → candidate | approval-recording detail in §4 could shrink with the offer model |
| POLICY | protection vs preference section; comment-length sentence bounded to CORE's exceptions | none |
| OPERATIONS | standing diagnostic allowance | pointer sentence repeated in PERFORMANCE, SECURITY, TESTING |
| DESIGN | "What counts as styling" list; drift-script fallback | switch wording → candidate (T16) |
| ENGINEERING | "Comments" detail section | table overlaps START |
| ANGULAR | none (already a pointer) | dated Node/Angular 20 claim; links duplicate SOURCES |
| IONIC | CSS parenthetical → pointer | Ionic 8 lifecycle names dated |
| CAPACITOR | styling-loophole clause → pointer; no-device fallback | none |
| UNITY | no-device fallback | Unity 6000.0 link dated |
| CHANGES | 1.9.0 candidate entry (history untouched) | none |
| SOURCES | none (history and links) | many dated "reviewed 2026-10-30" links |
| RUST | none (SAFETY comments now an explicit CORE exception) | none |
| COMPATIBILITY, LARAVEL, LIFETIMES, PERFORMANCE, PHP, PIXIJS, REACT, RELIABILITY, SECURITY, TESTING, THREEJS, TYPESCRIPT, VERSIONS, VITE, data-contracts | none: no conflict found | dated version notes (Laravel 10/11/12, React 18/19, PHP 8.x, Pixi v7/v8) to recheck at the next audit; small duplications listed by the scan |

Manifest: `tools/update_rules_manifest.py --apply` (repository-local). Rules version stays 1.8.8 in version.json until the T25 release bump; CHANGES has the 1.9.0 candidate entry.
- T11: Opus Agree; Astra Disagree r1 (new-project setup sentence in candidates + a coverage test), Agree r2. test_rules_pass 8 OK.
- V7 checkpoint 4 gate: full suite 1303 OK (13 skipped) after restoring LF in 28 files that text-mode Python writes had turned CRLF (caught by test_line_endings); validate PASS.
- T12: Opus Agree; Astra Disagree r1 (unreadable project DESIGN.md must disable styling), Agree r2. test_settings 7, test_global_policy 37 OK.
- T13: Opus Agree; Astra Disagree r1 (child revise inheritance, redelegation bound, task-level lock, presentation reference, unambiguous rendering), Agree r2. test_offers 14 OK.
- T14: Opus Agree; Astra Agree r8 after seven Disagree rounds. Fixes by round:
  - r1: rendering bound to task and workspace; answers bound to their question; report-first; withdraw, narrow and pause/resume; settings checks run on the whole call; single-use Yes; restyling counts; exact operations; rules pause and fail closed for all writes.
  - r2: resumed approvals also see this session's withdrawals; fresh approval replaces the reference (`offers.reapprove`); CSS value changes count; one switch change per call; atomic O_EXCL consumption; `/approve N` no longer waives the report.
  - r3–r5: the recorded history (relied_on/UserPromptSubmit) was replaced by the project's transcripts. decide() yields timed facts and fold() orders them across every session. CSS is judged on the whole proposed file. Offer files are writable only through record.py. An unreadable history refuses. Report debt survives refused approvals.
  - r6–r7: task binding follows trusted task transitions (owner naming, record writes, visible or question presentations). Times are timezone-aware. Undated facts are bounded by neighbouring times or the file's last change. Overlaps form unordered groups, which a later fresh approval resolves.
  - Superseded in T24 (2026-11-16): record writes no longer count as task transitions, as REDESIGN §3.4 (N4), approved by the owner, requires. Opus showed that a write to another task's records could otherwise redirect a later owner withdrawal, stop or resume away from the offer it was meant for; Astra agreed, since reviewer agreement doesn't override an owner-approved rule. Owner naming and offer presentations remain the transitions.
  - r8: the groups grow transitively.
  test_approval_hook 58 OK, test_offers 15 OK.
- V8 after T14: full suite 1386 OK (13 skipped), 341 s.
- T15: Opus Agree; Astra Disagree r1 (diagnostic print mode skipped the assertions; the summary counted wrong), Agree r2. tests/test_shadow_comparison.py runs 21 scenarios through both hooks: 13 same, 8 classified differences, none unexpected.
  The 8 differences are visible behaviour changes for the owner:
  - a later narrowing message suspends the approval (C-OFFER-3);
  - a qualified "yes but …" no longer approves (C-OFFER-3);
  - "/wait-what" then "yes" needs a re-presentation (C-OFFER-7);
  - git push needs its exact operation in the offer; plan approval alone used to allow it (C-SAFE-1);
  - styling writes need the CSS switch (C-CSS-1);
  - the switch itself needs a Yes (C-CSS-2);
  - offer records are writable only through record.py (C-OFFER-1);
  - a typed approval with extra words ("approve r4, no report") is a qualified answer, so the owner uses the one question (P3, C-OFFER-3).
- T16 plan: Opus Agree; Astra Disagree r1–r4, Agree r5. The rounds settled: legacy dispatch only through an owner-made inventory frozen at cutover; a coherent staged CSS contract; Codex observed or explicitly unmet; button acceptance never quietly downgraded; every invocation counted; isolation proven by host-reported sources, with the canary as supporting evidence only.

- T17 plan: Opus Agree; Astra Disagree r1 (the inventory must come before the new hooks are enabled; rollback for offer-only tasks), Agree r2.
- T17: Opus Agree; Astra Disagree r1, Agree r2. What changed:
  - hooks.json: approval.py in phase_gate's PreToolUse place.
  - Three non-approval checks the old place made were found missing and kept (required reads, report guides, records only through record.py); phase_gate's own tests run unchanged against approval.py.
  - All candidate texts applied, plus the stale lines Codex (run 17) and Astra found: the router's routing, lightweight and small changes through the offer, the report only when asked, CSS conditional on the switch in router, clarify, specify, DESIGN and VISUAL-REVIEW, and AUDIT comment advice.
  - SETUP and UPGRADE: the owner's order (stop sessions → preview the inventory → --apply → install) and "Back to rc.39".
  - tests/test_cutover.py: no stale text (phrases and patterns), the registered command and the legacy route, and rollback with rc.39 pinned to bfc18fd.
- V10 checkpoint 5 gate: full suite 1418 OK (13 skipped); validate PASS.

- T18 plan: Astra Disagree r1 (task-bound changes, snapshot-bound stamps, a defined record, keep the old check), r2 (the effective baseline, immutable evidence), Agree after those.
- T18: Opus Agree; Astra Disagree r1 (lock, the latest evidence per version, exit 2 blocks Done), Agree r2. completion_check.py (baseline, snapshot, check; completion.json written only by the script), wired into execute step 6 and deliver §5; tests/test_completion_check.py 13 OK. plain_reply.unreviewed_code stays until T20.

- T19: Opus Agree; Astra plan Disagree r1 (keep the agreed retirement condition; no SHA pin), Agree r2 and on the result. phase_gate.py is the retained legacy checker and shared library (header); RULE-CONTRACTS has the ownership map; OfferRouteNeverUsesLegacyApproval; phase_gate's report-guide cases run against approval.py. Full suite 1435 OK.

- T20 removed tests, each because its hook is gone (the checks are mapped in RULE-CONTRACTS "Removed with their hooks"):
  - files: test_plain_reply_hook.py (17), test_phase_reads_hook.py (6), test_truncated_read_hook.py (8);
  - test_gate_regressions: the seven Stop-hook methods plus the NoReportStopRegressions class;
  - test_followup_boundaries: the Stop case; test_rc3_reliability: PackageLocationTests (truncated_read's parser); test_stop_and_baseline: the phase_reads note case;
  - test_duplicate_skills_hook: the 27 pause and override cases.
  Moved instead of removed: the read-evidence cases (test_read_evidence, ConditionalGuidanceTests) now run against hooks/read_evidence.py. The broken-copy case now checks that the required-read check fails closed.

- T20: Opus Agree; Astra plan Agree (keep read evidence unchanged; diagnostics explain options; fail closed), result Disagree r1 (a missing read_evidence.py failed open at the report-guide check), Agree r2. read_evidence.py is a library; plain_reply, phase_reads and truncated_read are removed; duplicate_skills diagnoses only; evidence_library() turns load failures into a refusal.
- V11 checkpoint 6 gate: full suite 1364 OK (13 skipped); validate PASS.

- T21: Opus Agree; Astra plan Agree (status read-only, handoff only when asked), result Disagree r1 (offer state is a cache; VALIDATION verification incomplete; stdin handoff), Agree r2.
  - The resume skill has status, continue and handoff modes; rule-maker gains a diagnose mode (DIAGNOSE.md); task-status, resume-task and workflow-doctor are removed (19 skills).
  - README and UPGRADE carry the name mapping.
  - VALIDATION.md was regenerated with the owner's OK (D7): 1364 ran, 0 failed; validator PASS; --check CURRENT. The rc.39 record is kept as History.

- T22: implemented, not yet accepted. Opus Disagree r1: SIMPLE-ENGLISH.md named four reference files that only the archive held, so its CHECK and Strict modes couldn't work in the ZIP. Fixed: they ship in skills/workflow/simple-english/, and test_simple_english and test_release check every named path. Minor wording in tests/README, the digest usage line and README/UPGRADE was fixed too. Astra Disagree r1 (six known failures can't close a ticket), then Agree to one acceptance unit with T23.
  - Why joint: D7 allows rewriting VALIDATION.md only at T21 and T25, and hand edits are ruled out. T23 brings the package back to 19 skills, which VALIDATION.md and the count tests already state. Neither ticket closes until validate passes, the full suite has 0 failures and both reviewers agree. If T23 ends with a count failure, T22 reopens. No test was changed to 16.
  - Open failures (count only, 16 skills against 19): test_docs_consistency.test_current_docs_agree_with_manifests; test_package.test_current_package, test_unregistered_extra_skill_is_rejected, test_a_new_skill_needs_only_its_folder_its_manifest_entry_and_the_stated_counts; test_ui_design.test_ui_design_registered_once_among_the_skills; test_validate_budgets.test_a_new_reference_file_needs_no_validator_edit. Full suite: 1364 ran, 6 failed.
  - VALIDATION.md's evidence is stale (it describes T21) until the T25 regeneration, even once the counts match again.
  - Moved: implement-spec and retro to docs/archive/skills/ with their LICENSE; simple-english to skills/workflow/SIMPLE-ENGLISH.md with SIMPLE-ENGLISH.LICENSE (archive copy of the licence too); digest_sessions.py to tools/.
  - Licences: validate.py reads each credits row's licence paths from VENDORED-SKILLS.md, and a row without one fails. Archive paths are required where docs/archive exists (the source checkout). The shipped ZIP leaves the archive out.
  - Tests retargeted, none removed: test_owned_skills (archived skills unregistered, their folders gone, licences in place; the digest tests run tools/digest_sessions.py), test_package_contract (LICENSED = the six shipped skills; KEY_FILES gain the digest script and SIMPLE-ENGLISH.md/.LICENSE), test_release (the ZIP has SIMPLE-ENGLISH.md and .LICENSE, and no archived folders), test_simple_english, test_task_report, test_phase_gate_hook (report-guide paths).
- T23 plan: Opus Agree after r1-r4 changes (validate-safe paths, named exceptions, the missing §3.9 rules, a stale-snapshot rule, pasted checks, a shared clone, deletions in the hash, phrase fixes); Astra Disagree r1-r2 (invocation-level run budget, snapshot materialisation, the diagnostic allowance, the host's isolation first, /wait-what makes no tool call), Agree r3 on revision 4.
- T23: implemented; joint result review r1: Astra Disagree (Codex metadata must also say user-only: `policy.allow_implicit_invocation: false`, with a validator check that both markers agree), Opus Disagree (the snapshot hash wasn't reproducible, and a copy under core.autocrlf=true never matched: replaced by skills/interrogate/scripts/snapshot.py with tests/test_interrogate_snapshot.py; code-review 4b now uses it; /wait-what says "no tool call"; no-comments points to CORE's approved-change rule; tighter tests; this table's layout). All applied. Round 2: Opus Agree except one gap, which Astra also raised (Disagree): a host-made checkout couldn't receive the snapshot, because `copy` refuses an existing folder. Astra also found that mirroring could follow a link in the checkout out of isolation. Fixed: `snapshot.py fill` for an existing disposable checkout (it refuses the target, a folder above it and another HEAD, and removes the checkout's leftovers); writes never pass through a symbolic link or a Windows junction (Python doesn't report junctions as links), with a final inside-the-copy check; the executable bit is copied. tests/test_interrogate_snapshot.py has 9 tests (the executable-bit test skips on Windows); the link test uses a real junction here and fails when junction handling is removed (checked by mutation). The interrogate text names `fill` and where the script lives. Round 3: Astra Agree, Opus Agree. Opus's non-blocking note (a checkout nested inside the target and not ignored by Git would change the target's own snapshot) was closed as well: `fill` refuses it, and a test covers both the refusal and the ignored case (10 snapshot tests).
- V13 (T22+T23 final): full suite 1386 OK (14 skipped), 491 s; validate PASS (19 skills).
- **T22 + T23 accepted** (joint gate): Opus Agree, Astra Agree, validate PASS, full suite 0 failures (V13). Still open: the observed runs (an interrogate run on a seeded bug, a no-comments dry run) await the owner's run budget; VALIDATION.md stays stale until T25.
  - New user-invoked skills: interrogate, no-comments, wait-what (19 registered). code-review: comment and reader-load checks in the pasted Standards list, step 4b Blast radius under Standards.
  - Docs: README (counts, the new commands, a credit line for the adapted ideas), UPGRADE, SPECIALISTS, RULE-CONTRACTS label rows, CONTEXT terms Interrogation and Comment debt.
  - Tests: tests/test_new_skills.py (10); test_release checks the new skills and the shipped simple-english files; test_package_contract EXPECTED_SKILLS gains the three.
  - Observed runs (an interrogate run on a seeded bug, a no-comments dry run): **unmet, pending an owner-approved budget change**. They need about six invocations; decision B has 3 left, all for the T26 pilot (D5).
- V12 (T22+T23 joint gate): full suite 1375 OK (13 skipped), 338 s; validate PASS (19 skills). VALIDATION.md still describes T21 and stays stale until T25 (D7).
- Record incident (2026-11-16, T23): an inline script that added the T23 lines cut FINDINGS.md off after them (an operator-precedence mistake), so the "T16 host observations" section was lost. It was rebuilt from this session's transcript: the full copy from its first write, the one later Edit (the run-cap paragraph), the scripted replacements (runs 16–17, the state line, the ledger count) and a `tail` read of its final lower half made earlier in the session. Record edits now go through record.py.
- T24 plan: Opus Disagree r1 (item 10 can't be an agent decision against the owner-approved N4 rule; approval waivers; specify :12; exact offer states; the full READS list; the exact stale pattern; coverage), Astra Disagree r1 (approval verified from evidence; remaining bypasses; lightweight delivery's report rule; CSS check only when off). Revision 3: both Agree. Astra's notes: keep the historical T14 finding and append its supersession; test the stop across sessions. Opus's note: the execute check pins evidence, not the Offer line.
- T24 hook part (item 10): hooks/approval.py read_events no longer turns the agent's record writes into task transitions; written_tasks was removed. New regressions in test_approval_hook: a withdrawal after another task's record write still ends offer A, and a stop in another session after such a write still pauses it. Both fail when the old transition is put back (mutation check) and pass now. The four hook suites (approval_hook 90, shadow_comparison, session_failures, phase_gate_hook) pass; no existing test depended on the old transition. The legacy route is unaffected (legacy_session reads phase_gate's scan state).
- T24 text: phase texts, VISUAL-REVIEW, TASK-FOLDER, SETUP, ui-design, CONTEXT and the leftover small-change pointers (codebase-map, rules DESIGN.md with its manifest fingerprint, ui-design CONTRACT) follow the offer model. Result reviews: Astra Disagree r1 (a stop only pauses; continue keeps the approval), then Agree; Opus Disagree r1 (two-gate wording left in AUDIT, CONTEXT and the specify Codex metadata; router row; conditional snapshot), Disagree r2 (deliver pointed to TASK-REPORT for building a review.json; it now points to VISUAL-REVIEW "Prepare the report" step 2), then Agree. Both accepted the two worker choices: settled one-ticket work carries its agreement in the offer; `unknown` renders as `unverified` with an "unknown:" note. Retargeted pins are listed in the worker report (old phrase → new contract phrase, each old bypass phrase asserted absent); new: test_cutover.OfferModelText, cases B25–B28 (NOT_RUN).
- Known existing intermittent failure: test_record_safety.test_parallel_appends_lose_nothing sometimes leaves FINDINGS.md.lock after 8 parallel record.py appends (about 1 run in 30). It fails identically on an exact rc.39 copy (bfc18fd: 1 of 40 runs), so it predates the redesign; the redesign touched only record.py's `offer` dispatch. A retry-on-PermissionError release did not measurably help (original 0/30, retry 1/30) and was not kept. Follow-up, outside this redesign: find the cause and fix it, because a leftover lock blocks record writes for 5 minutes. Never weakened or skipped.
- V14 (T24 final): full suite 1396 OK (14 skipped), 399 s; validate PASS (19 skills). The run before it hit the known intermittent record_safety failure above; this clean rerun is the gate evidence.
- **T24 accepted:** Opus Agree, Astra Agree, V14.
- T25 plan: Astra Disagree r1 (task records count in the tree identity, so records come before the VALIDATION write; regenerate the rules manifest after the rules edits; settings.json is created only when missing), Opus Disagree r1 (manifest after the CHANGES edit; the 1.9.0 heading and its coverage; the global policy version; a tests/README release section; the rc.39-based host copy as a limit; rerun the intermittent test only for the same error), Opus Disagree r2 (the policy revision also lives in skills/workflow/ARTIFACTS.md and DIAGNOSE.md). Revision 4: both Agree.
- T25 result (implemented by an Opus worker, checked by me):
  - version 2.9.0-rc.1: plugin.json, version.json package_version, RENDERER_VERSION, the four behavioral candidate_version fields, and the README and UPGRADE titles;
  - rules library 1.9.0 (CHANGES.md "2.9.0-rc.1, 2026-11-16"; the manifest written after every rules edit, and the final preview reports no change);
  - global artifact policy 2.9.0 (global_policy.py, skills/workflow/ARTIFACTS.md, DIAGNOSE.md). The owner's installed ~/.workflow-axa/ARTIFACTS.md keeps 2.5.0 until the owner applies it;
  - docs: CHANGELOG (a new top entry with its Limits), UPGRADE, README, ARCHITECTURE, RULE-CONTRACTS (the "planned Tn" markers now read "Tn"), CONTEXT, EVALUATION, docs/DESIGN (a new last section), tests/README (a release section);
  - tests: the rules_version pins 1.8.8 → 1.9.0 in test_rules and test_engineering_rules (an expected version update); the new test_cutover.ReleaseNotes.
  - Full suite before the VALIDATION write: 1397 ran, 5 failures, all from VALIDATION.md still naming 2.8.0-rc.39 and rules 1.8.8. The worker confirmed this on a scratch copy with only those strings changed: validate PASS and the three affected test files pass. The known intermittent record_safety failure did not appear.
  - Next: VALIDATION.md regenerated under D7 (`verification_summary.py --run --write`, then `--check`); the reviewers review that tree. The acceptance line is added after their review, which makes VALIDATION's tree identity stale by that record edit only.
  - First VALIDATION write: CURRENT, 1397 ran, 0 failed, validate PASS.
  - Result review r1:
    - Astra Disagree: UPGRADE "Safe adoption" still required a report and fresh consent after a restart (now legacy tasks only; an offer task keeps its approval when its provenance validates); the ARCHITECTURE ui-design row still said stop when the kit can't express a request (now reuse first, styling within the approved offer when the CSS switch and the project allow it, otherwise the mimic question).
    - Opus Disagree: RULE-CONTRACTS hook candidate 6 and the Agreement-line gap described phase_gate as the approver (both now labelled legacy tasks only); an rc.39 history line in UPGRADE had lost its "21" (restored); the CORE.md word ceiling in test_engineering_rules was raised from 650 to 710 in T11 (CORE grew from 649 to 702 words with the required comment rules). That ceiling is a deliberately loosened check, now stated in tests/README instead of "none weakened".
    - All fixed; validate PASS and the affected doc tests pass. VALIDATION regenerated again (D7) for round 2.
  - V15: VALIDATION.md CURRENT for the reviewed tree (bfc18fd…+a4c29c1611e57d7d): 1397 ran, 0 failed, 14 skipped; validate PASS (19 skills). This acceptance line is a later record edit, so VALIDATION's tree identity is now stale by this edit only.
- **T25 accepted:** Astra Agree r2, Opus Agree r2, V15.
- T26 plan: Astra Disagree r1–r2 (fix the comparison before launch; an in-run isolation check; count every invocation; seeds with ground truth; bounded cleanup; the reduced scope stated), Opus Disagree r1–r2 (one run per repo; --settings instead of the tracked settings.local.json; deny rules; no installs; Bash allow list; git-write denies; a shared-file restore). Revision 3: both Agree. Owner: D8 (branches), Hooqd kept on master (contextual comparison), D9 (26 runs), D10 (29 runs).
- T26 pilot (results; evidence under .artifacts/2026-11-15-workflow-redesign/t26/):
  - Scope: the single-turn runs observe discovery, routing and offer presentation only. Live approval, implementation, completion checking and delivery on these repos stay unobserved; the offline replays are separate synthetic evidence. The comparison with the T2 baseline is contextual throughout.
  - Worktrees (detached; start SHAs): D:/wfaxa-t26-hooqd b4b8385c (Hooqd master), D:/wfaxa-t26-cheflabels f60a2fa0 (Cheflabels development/main; action-sheet.component.ts sha256 623b0e63… at start and after every run), D:/wfaxa-t26-paperclip 0419bc58 (workflow-paperclip master). The owner's checkouts were untouched.
  - Candidate: 2.9.0-rc.1 for r18–r21; 2.9.0-rc.1 with the F1/F2 fixes (snapshot id bfc18fd…:b77f2896…, t26/candidate-after-f1f2.txt) for r22–r29, child invocations included (the r24 and r25 streams hold r24–r27 and r28–r29). The F4 fix came after r29. Mode acceptEdits, model claude-sonnet-5, --setting-sources project,local plus a --settings file. In every run, isolation held by the host init: only workflow-axa@inline 2.9.0-rc.1 plus built-ins, and only the project's own CLAUDE.md and AGENTS.md as instructions.
  - Run ledger (decision B amended: 29 total; runs 18–29 here, counting every invocation):

| Run | Repo and case | Result |
|---|---|---|
| r18 | Hooqd, album count "7 / 20" (small visible change) | met: routed to clarify; found the shared AlbumManagerPopup and ALBUMS_PER_ACCOUNT; stopped with two genuine owner questions (task identity; combined or per-tab count); no writes, 0 hook denials, 2 permission refusals (test-driver allow list) |
| r19 | Cheflabels, lightweight doc-comment edit | lost: test-driver prompt flaw ("stop if anything comes from .agents"); the SessionStart note merely named that folder; stopped with no tool call |
| r20 | paperclip, --dry-run option (one-ticket) | **defect F2**: right route and a sensible offer, but in its own words ("Go ahead with this…?"), with no record.py offer create, no canonical block and not the one question |
| r21 | paperclip, /interrogate on the seed | cut off by a T3 server restart after 12 tool calls and no subagent (1 invocation); its probe file in its own scratch folder was removed by exact path |
| r22 | paperclip, r20 recheck after the F2 fix | met through the hook: the agent first tried the edit, the refusal named workflow-specify and record.py offer create, then it made records, a recorded offer #1, the canonical block and the one question; no tracked file changed (**F3**: the router sentence alone did not prevent the first attempt) |
| r23 | Cheflabels, redo of r19 | met: docs-tests recipe, lightweight route through workflow-specify, recorded offer #1, the canonical block, the one question with a recommendation (no report); 1 correct record.py refusal; target unchanged |
| r24–r27 | paperclip, /interrogate rerun (main + 2 adversaries + 1 confirmation) | met: snapshot pinned; copies with snapshot.py copy; two independent same-model adversaries; confirmation on a fresh copy; report current; three lists. Ground truth matched: sum invariant broken when total % parts ≥ 2 (planted, labelled synthetic). Its copy cleanup (`rm -rf`) was refused because rm wasn't on the allow list (not a deny rule), and was left for the driver. The run woke itself twice with ScheduleWakeup while waiting for its adversaries; that stays within the same invocation (3 init events, 1 main + 3 subagents) |
| r28–r29 | Cheflabels, /no-comments dry run (main + reviewer) | partial: a fresh reviewer, verdicts checked against the code with grep, the vendor constraint (rowId vs Ionic id) and the Ionic timing notes kept, comments that disagree with the code flagged as possible bugs, a dead debug method flagged, larger reshapes declined; target unchanged. **Defect F4**: the offer was in its own words with its own question. Expected keeps for exported-interface docs were proposed as deletions (the agent judged them app-internal, not public API): a judgement difference, not counted as a defect |

  - Contextual comparison with baseline 6d180d94 (Hooqd, 2026-11-12, rc.38/rc.39 era, model unknown; 13 human messages, 4 approval messages, 6 process-only turns, 13 hook denials: other 6, use record.py 4, no plan report 1, install 1, quote not matched 1): the pilot runs had 0 (r18), 1 (r22, the correct no-offer refusal) and 1 (r23, the kept record.py check) hook refusals, and no plan-report, quote-matching or task-switch denials. Human-message counts aren't comparable (the driver sent one turn).
  - Findings fixed in T26, each with a test: F1 (the SessionStart note claimed "superpowers is enabled" from settings and agents repeated it: now "Your settings enable the … plugin. If loaded here, …"); F2 (router: offers only through workflow-specify; the hook's no-offer refusal names workflow-specify step 5 and record.py offer create; the lightweight line names step 5; hook test; behavioural case B29 NOT_RUN); F4 (no-comments step 3: the offer through workflow-specify step 5, the canonical block, the one question). F1 and F2: both reviewers Agree; F2 was rechecked live in r22. F4: Astra Agree as an instruction fix; Opus asked for two more pinned phrases ("Show its canonical block", "Change nothing before it is approved"), now added to test_new_skills. It was not retested live, because no runs remained. The pre-fix text of step 3 was: "Present one offer: the deletions, the reshapes and the constraints that would become tests or lints. End with the one question. Change nothing before it is approved." F3 is recorded as observed: the hook is the effective safety net; no further text change. Caveat (Opus): in r22 the reads of RULES.md and flows/INDEX.md were refused (the missing --add-dir) before the first edit attempt, so r22 doesn't show that the router sentence alone fails; F3 is confounded.
  - Isolation note: the claude.ai Claude Docs and ClickUp connectors were connected in every run (host init); the settings denied their tools, and no run called them.
  - Test-driver issues, not package defects: r19's over-broad stop rule; --add-dir was missing in r18, r20 and r22 (package reference reads needed permission; the agent used cat); the allow list didn't cover `cd … &&`, `git -C` or python3 at first (widened before r22); the first r18 launch failed on a /d/ path: the claude CLI started, printed "Settings file not found" and exited with no session, no init event and no model call; it isn't counted as a run. The plan's example "split_amount(101, 3) summing to 103" was wrong: the seed gives 102 (t26/seed/), and the reported failures match the seed. Minor: r23's offer capitalised "False" where the request said "false".
  - Offline replays (t26/offline-replays.txt), approval.py on the real worktrees with synthetic transcripts: 9/9 as expected (an approved offer allows its files; a write outside it, git push without the operation, an informal yes without a presentation, and a withdrawal after another task's record write are refused; a repo with no offers gets the create-an-offer refusal). C2 (a .scss write) was refused for being outside the offer. C3, added after Astra's review, uses a synthetic approved offer that lists the stylesheet (task folder docs/plans/2026-11-16-t26-css-case in the Cheflabels worktree), and the refusal names the CSS switch ("changes styling, and CSS is off here"). The /interrogate subagent evidence is saved in t26/evidence-r24/subagent-transcripts.md, and the seed in t26/seed/.
  - T26 result reviews: Astra Disagree r1 (an offline CSS case covering the stylesheet; F4 status wording; the candidate binding through r29), Opus Disagree r1 (stream-accurate wording: rm not on the allow list, ScheduleWakeup, the F3 confound, connectors, the first r18 launch, 103→102, "False"; two more F4 pins); all applied. Round 2: both Agree. V16: full suite 1399 OK (14 skipped), validate PASS.
- **T26 accepted** (contextual pilot; the scope limits above stand).
- Cleanup (2026-11-16), by exact paths only:
  - The pilot worktrees: the task-created files only (the r22, r23 and CSS-case task folders, t26_seed and its __pycache__), then `git worktree remove` without --force in Hooqd, Cheflabels-labeler-V2 and workflow-paperclip. No prune.
  - Under .artifacts: t26/interrogate-copies/{adversary-a,adversary-b,confirm}, host-candidate, and the T16 sandboxes host-tests/{axa-home,axa-home-legacy,cache,cache-r14,cache-r3,cache-r4,cache-r9,r1-smoke,r2-offer,r3-css,r4-legacy,r5-button,r6-codex}, each checked first for links and junctions (none).
  - Kept until delivery: host-tests r*.stream.jsonl and r*.stderr.txt (runs 1–15), and everything else in t26/ (r18–r25 streams, evidence-r22/r23/r24, seed, settings, offline-replays.txt, css-offer.json, candidate-after-f1f2.txt, the axa-home sandboxes).
  - tools/stage_candidate.py and test_stage_candidate stay: retiring them is a separate change for the owner.
- Observation, not caused by this task: after the pilot, D:/workflow-paperclip showed 13 changed files where it had 1 before (AGENTS.md, salt-documents, team-tasks, the offerte-improvements and team-workspaces plans, configure-agents), dated 14:21–15:34. No T26 stream writes to that checkout (the only mention is a read-only file listing inside the pilot worktree), the settings denied Edit and Write there, and most changes are dated after the last pilot run ended (15:15). They look like another session's work and were left untouched. Hooqd (2) and Cheflabels (13) are unchanged from before.

## T16 host observations (live, Claude Code 2.1.325 CLI, OAuth plan; apiKeySource none)

These are observations, not offline tests. Answers in sandboxes were typed by the test driver (Opus) and are labelled simulated; none is an owner approval.

Setup:
- Staged copy: `.artifacts/2026-11-15-workflow-redesign/host-candidate/` (tools/stage_candidate.py: candidate blocks applied, approval.py in phase_gate's PreToolUse place, canary in CORE).
- Sandboxes: `host-tests/<case>/`. Project settings exclude the user's and parents' CLAUDE.md and the installed START/CORE/ARTIFACTS, and disable `workflow-axa@gazohhh`. Staged rules are copied in and imported.
- Runs: `--setting-sources project,local --plugin-dir <staged> --add-dir <staged>`; WORKFLOW_AXA_SETTINGS, _HOME and _GATE_CACHE point into host-tests/.
- Evidence: `host-tests/r<N>.stream.jsonl` (host-reported init and hook results) for runs 1–15. Runs 16–17 ran as T3 threads; their evidence is those host-owned thread transcripts.

Isolation, run 1:
- The init event's plugins: only the staged workflow-axa (inline) plus built-ins.
- The transcript's `instructions` attachment lists only the sandbox CLAUDE.md, so the global CLAUDE.md and its imports are excluded.
- The staged approval.py refused an edit with its own wording.
- Imports from outside the project were not expanded in -p, so the staged rules were copied into the sandbox from run 2 on; the canary was quoted in run 4 (supporting evidence only).

**Run-cap deviation:** the agreed T16 cap was 12, and 15 runs were used: a test-driver artefact (run 5), a candidate-text retry (run 3) and a code-fix retry (run 2). The overall 20-run allowance of decision B is not exceeded. The owner then decided (D4, D5): one run for the button test, one for Codex (D6), and the last 3 for T26.

**T16 state: done** (Astra Agree, 2026-11-16). The owner decided D4–D6; runs 16–17 are recorded below; the clean full suite passed (V9). Kept explicit: Codex is a weaker check (D6), and the child observation doesn't prove child-only authority.

Run ledger (17 of the 20 runs in decision B; 3 left for the T26 pilot, D5):

| Run | Case | Result |
|---|---|---|
| 1 | smoke / isolation | met (above) |
| 2 | present the offer | **defect:** `record.py offer create` refused (the gate's record.py parser read the verb as a file); fixed, offer_command_targets + test. O3: no question tool in -p |
| 3 | present again | **defect (candidate text):** the rendering stayed in tool output only, and the text answer forms weren't given; wording fixed |
| 4 | present again | met: byte-equal block in the reply, recommendation, answer line |
| 5 | `/approve 1` | test-driver artefact: Git Bash rewrote `/approve` into a path; refused correctly; rerun with MSYS_NO_PATHCONV=1 |
| 6 | `/approve 1` | met (O2): delivered as a user turn; edit allowed; decision reference cached |
| 7 | adapter failure | met (fail closed); **defect:** the diagnosis named a misleading AttributeError (half-loaded module); fixed in _load + test |
| 8 | recovery | met (O5): the same write allowed with no new question |
| 9 | present an offer with delegable tests/ | met |
| 10 | "approve" | **defect:** `offer derive` found the parent still a draft (approvals were recorded only on a write); fixed: derive_problem validates and records the parent before derive runs, + test |
| 11 | child | met (O4): derive recorded the parent's approval; a subagent wrote tests/page.spec.ts. Limitation: the parent offer also covered that file, so the child-only authority isn't separately proven live (offline tests cover it). Styling: the agent checked `settings.py show`, wrote nothing, asked the exact question |
| 12 | "yes" (CSS on) | met (O6): `settings.py css on` allowed; an inline style write allowed |
| 13 | "yes" (CSS off) | met (O6): `settings.py css off` allowed; the next inline style write refused with the CSS-off reason |
| 14–15 | legacy task (inventory via legacy_inventory.py --apply) | met (O7): report presented, "Yes to both", edit allowed; the offer route would have refused it (no offers) |
| 16 | button answer (owner decision D4) | met (O3). In a T3 Claude thread on a temporary T3 project for sandbox r5-button (removed afterwards), the agent put the offer block inside the question with the three buttons. The test driver chose "Approve from this summary". The edit was allowed and the offer became approved with its decision reference (only approval.py records that). The host's instruction list shows only the sandbox CLAUDE.md and the staged START/CORE; no installed workflow-axa hook ran. Other user plugins (superpowers, orca) did load: T3 reads user settings |
| 17 | Codex, instruction-only, old global rules still loaded (D6: a weaker check by the owner's choice) | met as such. Codex (T3 child) followed staged step 5: the offer block, a recommendation (money → report first), the answer line; `settings.py show` worked; the child handoff was described correctly. It named conflicts with text the candidate blocks don't yet cover (for T17): VISUAL-REVIEW, the router and RULES.md still require Approval lines and forbid all CSS; AUDIT.md still recommends explanatory comments against CORE's new comment rules. It also put a check into `operations`, so the offer text must define operations as protected actions only (git writes, MCP tools) |

Unmet, for the owner before T17:
- ~~Button answer~~: met in run 16 (D4).
- ~~Codex~~: run 17 instead of an isolated run (D6). The way the package deals with stale installed or project rules is an open design question for a spar with Astra; it doesn't block.
- **Codex instruction isolation:** CODEX_HOME holds the ChatGPT login; an isolated one needs `codex login`. Not run.
- Retention: the stream logs are evidence; the sandboxes and the staged copy became disposable when T16 was agreed. They are not removed yet; the T26 pilot reuses the staging tool, and their removal goes under TODO "Cleanup" after T26. Host transcripts under ~/.claude/projects/ are host-owned and stay.

- Release 2.9.0-rc.1 (2026-11-16, D11):
  - Commit 0c2a764 "Release 2.9.0-rc.1: the offer model"; main fast-forwarded from bfc18fd and pushed to origin.
  - VALIDATION.md was regenerated just before the commit: CURRENT for that tree, 1399 ran, 0 failed, validate PASS.
  - Install on the owner's machine, in this order:
    1. legacy_inventory.py --apply for 7 workspaces (49 tasks; the redesign task itself included);
    2. `claude plugin marketplace update gazohhh` and `claude plugin update workflow-axa@gazohhh` (2.8.0-rc.39 → 2.9.0-rc.1; restart needed);
    3. the Codex copies in ~/.agents/skills replaced from the release ZIP (19 folders; the 6 retired folders removed);
    4. global_policy.py --apply and activate_rules.py --apply, run from the installed copy so the global references keep pointing at ~/.agents/skills (both --check: MATCH). settings.json was created with css off.
  - Checks: audit_installation --check-global DISK_MATCH 2.9.0-rc.1 (host loading NOT_VERIFIED until a fresh session); the installed approval.py refuses an edit with no offer and names workflow-specify step 5.
  - Rollback data, under the redesign worktree's .artifacts/release/: codex-skills-rc39-backup/, global-backup-rc39/, and the release ZIP (SHA-256 a08fd1a9…).
  - Observation: 5 files of other tasks that were staged in this checkout no longer show as staged after the fast-forward. Their content equals the committed versions, and no other version exists in the object store, so no content difference was lost (most likely a mode or metadata-only staged entry).

## 2.9.0-rc.2 (2026-11-16, D12)

- Trigger: the owner's live T3 thread on D:\workflow-paperclip (session 5ed6485d, task 2026-11-12-offerte-improvements). The session started at 14:15 on the 2.8 router; the hooks switched to rc.1 at the 15:48 merge.
  - F5 (bug): T3 Code returns a finished delegate's report as a plain `type: user` message with the same metadata as the owner's (`promptSource: sdk`, `entrypoint: t3-code`, no `origin`). The hook read it as the owner: at 17:13 and 17:21 it consumed the open presentation and matched the narrowing pattern, so `/approve 1` was refused twice. Only the text tells it apart.
  - F6: the format-1 offer block (JSON-encoded fields in a code block) was unreadable for the owner.
  - F7: no "Recipe:" line ever appeared. The router ran once (14:15, old text); the new request at 16:46 (revision 7) entered workflow-clarify directly, so §3 was never reached.
  - F8: the review.html choice was offered nine times, only inside the long answer line, never as buttons and never recommended, although the task touches money and a visible document.
- Design spars with Astra (two rounds each on the offer format and on the recipe pick) until both agreed; then code reviews by Astra and Opus with re-checks until both agreed. Findings fixed during review:
  - format 1 accepted for every offer (hidden in an HTML comment) → new offers carry `presentation_format: 2`;
  - delegate statuses beyond the observed ones, and a host note before the report;
  - "end of message" per transcript entry → per visible block (text since the last tool call), `$$` added;
  - another offer asked by question left the text offer open;
  - task transitions: regex-only footers, hidden offers in the block, question footers searched in the options, presentations undone by later text, and a held text transition overtaking a newer question transition. offer_tasks() now validates transitions exactly like approval; format-2 text transitions are released at the owner's answer.
- V17 (rc.2 gate): full suite 1419 ran, 1 failure = the known intermittent record_safety parallel-append test (passed 5 of 5 alone; record.py and its test unchanged); validate PASS apart from VALIDATION.md, regenerated at release. Evidence: .artifacts/2026-11-15-workflow-redesign/rc2/ (all.diff, suite-final.log) in the redesign worktree.
- Not verified live: the format-2 presentation, the question-tool variant in T3's dialog, and the Recipe line on a real host (routing_cases stay NOT_RUN).
