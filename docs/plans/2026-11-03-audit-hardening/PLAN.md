# Audit fixes: approvals, recovery, verification and less repeated work

## Publication checkpoint, 2026-11-06

The owner approved publication of the two tested retrospective fixes and Git updates for Claude and Codex: "Publish workflow fixes and Git-update both". Release target: 2.8.0-rc.7. Source is the retained D:/wfaxa-pilot/workflow-rollout candidate. Only the approval parser, transcript digest, their regression tests and release records are transferred. Application worktrees remain separate and preserved. Full rollout and architecture coverage remain partial. The earlier checkpoint below is historical.

## Historical r4 checkpoint

- Status: follow-up r4 implementation delivered. Local verification passed. Live positive write and write-after-restart remain unverified.
- Owner: Codex. Delivery reconciliation by an independent reviewer who did not build the code.
- Updated: 2026-11-05.
- Repository / worktree: isolated D:/wfaxa-pilot/workflow-fixes, a source snapshot without Git metadata. Source HEAD: 0d67057a6e15b72436624e48b0698bab00185ab5.
- Task identity: continuation of this audit under follow-up r4. Cheflabels retains its separate task and approvals.
- Rules readiness: READY for the bounded candidate and delivery records. Installed shared rules 1.8.2 and project protections apply.
- Agreement: direct owner instruction "fix all of it" after the defect audit covers the isolated follow-up fixes. See D-r4-1.
- Approval: direct task authority "fix all of it" covers candidate implementation. No r4 HTML approval is claimed. Live installation was never granted.
- Evidence: FINDINGS V-r4-final, V-r4-URI-final, V-r4-review-final and V-r4-live-budget. Final suite: 886 tests, zero failures/errors, 14 skips, 171.116 seconds. Validator PASS, 699 words.
- Current outcome: F1-F6 implementation verified by local public-hook tests and offline replay. Live positive write/restart remains unverified. F7 accepted, transferred and its disposable worktree removed.
- Source preservation: original tracked diff SHA-256 2f11292dd0d1a64c1b93c1bf9fe0a16305e7c90c5455c3abdfb840f4da3dcd72 remains unchanged.
- Next safe action: package this tested source candidate and verify both archives and checksums. No more paid sessions or installation is requested.

## Historical checkpoint before final reconciliation
- Status: implementing follow-up r4; local candidate suite passed, live-host and Cheflabels handoff partially verified.
- Owner: Codex; ownership: active in isolated D:/wfaxa-pilot/workflow-fixes.
- Updated: 2026-11-05
- Repository / branch / worktree: D:\workflow-axa, main, main worktree. Commits up to 9e8338e are local; everything after is uncommitted (owner, 2026-11-03).
- Task identity: new, separate task. Source: the owner's ChatGPT audit prompt (2026-11-03). Related: `2026-11-02-modular-engineering-workflow` (the package build); this task fixes defects found in it. Sibling: `2026-11-03-ui-evidence-engine`.
- Rules readiness: READY. The repository's own CLAUDE.md, the package tests and the shared rules 1.8.0 cover it (`rules_stamp.py`: NONE, the package has no project line).
- Agreement: revision r1 agreed by the owner 2026-11-03: "Yes to both".
- Approval: revision r1 approved by the owner 2026-11-03: "Yes to both" (report `reviews/plan-r1.html`, all tickets, the exclusions in Approach and Boundaries).
- Current understanding / evidence: FINDINGS.md E1-E23. Reproduced: E1-E6, E11-E14, E16-E18, E20-E23. Measured: E10, E19. E7 settled by V-E7. Limit or risk: E8, E15.
- Next safe action: finish live evidence and candidate handoff; reconcile Cheflabels baseline console error and request final transfer approval only after concrete review.

## Goal and acceptance
Fewer unauthorised actions, clearer recovery and less repeated work. Not more instructions or a bigger test count.

- A1: After `/workflow`, application code edits and git writes are allowed only when the current task's Approval line approves the current revision, and the user's words it quotes appear in a real user message. Loading clarify or specify allows only task records and the report.
- A2: Negated or quoted "lightweight" wording grants nothing. A lightweight edit needs a recorded line that names its files.
- A3: Another task's approval does not authorise the current task. A valid approval survives resumption; a changed scope does not inherit it.
- A4: Reading a phase SKILL.md whole counts as loading that phase, as the router documents.
- A5: The gate also runs for the PowerShell tool and MCP write tools, and catches common shell writes (redirection, tee, cp, mv, Set-Content, git apply/checkout/reset). The docs say plainly that command-text filtering is advice, not a security boundary.
- A6: An interrupted record write leaves the old file intact; a concurrent change is refused, never silently lost.
- A7: "Stop" ends implementation: no review loop, no return to execute. Paused, blocked, cancelled and partial each have one clear route, and the handoff names what changed, what was verified, what remains and the next safe action.
- A8: A failure counts as existing only when the same test fails the same way. Five existing failures becoming four existing plus one new is reported as one new failure.
- A9: A baseline is reused only while its command, commit, diff and environment still match. The required checks run again after the last repair.
- A10: A small change (one ticket, named files, no interface, data, dependency or security change) uses one builder and one independent review. It leaves that route when it turns risky. No second review of an unchanged diff.
- A11: Words that carry uncertainty, permission or a proposal keep their meaning. The wording check runs before the report is written, never blocks a valid report, and covers every report kind. An approved or presented report is never overwritten: a report counts as presented once the task records name it.
- A12: The test suite passes in a path with spaces and under POSIX.
- A13: One current verification summary, tied to a commit and environment, and generated where practical. The other documents point to it.
- A14: A release package is built from an explicit include list, without Git internals, caches, secrets or evaluation output.

## Historical r1 agreement
Revision r1, agreed by the owner 2026-11-03: "Yes to both". It covers acceptance A1-A14 above and the approach below, with the owner's answers D1-D5: approval needs the Approval line plus the user's real words (A1), the small route (A10), an MIT licence and a release tool now (A14), and at most 8 live Claude runs plus useful Codex runs (T9).

## Approach and scope
- Package files only: hooks, scripts, skills and docs of workflow-axa, plus tests. No application repository changes. No global settings or permission changes. No automatic commits.
- Keep: the four phases, grilling, grounded planning, both gates, task reuse, history, shared rules, artifact protections, pinned specialist methods, the D14 UI rule and the approved report design.
- Each confirmed defect gets a regression test that fails before the fix.
- Order by impact: T1 approvals, T2 records, T3 stop and recovery, then T4 baselines, T5 reports and wording, T6 proportional agents, T7 portability, T8 docs and release, T9 live acceptance.
- Budgets: this nine-ticket task is not a small route; the main session and parallel workers build tickets with separate files. T1, T2 and T3 each get one fresh reviewer; the others get one combined review at the end. Full package suite once per ticket and once at the end. Live runs: at most 8 Claude runs plus Codex runs where useful (D5), none repeated without a reason.
- Enforcement honesty: the hook can block explicit edit tools it sees. It cannot see every shell write, edits outside Claude Code, or prove that a record is truthful beyond matching the user's words in the transcript. Codex gets no hooks. The docs will say so.

## Historical r1 approval
Revision r1, `reviews/plan-r1.html`, approved by the owner 2026-11-03 together with the agreement: "Yes to both".


## Historical r1 outcome

Delivered as complete on 2026-11-04 (fresh reconciliation, `reviews/delivery-r3.html`; `delivery-r2.html` is the earlier partial snapshot, kept as history).

- Asked: fix the ChatGPT audit's findings (approvals, recovery, verification, less repeated work, writing, records, docs and release). Agreed and approved: r1, "Yes to both" (2026-11-03), with D1-D5; D11 widened the live-run limit.
- Built: all nine tickets T1-T9 (FINDINGS V1-V11), plus the live-loop fixes (install guard, unreviewed-code check, report location, consent wording) and a baseline-input checker (`scripts/baseline_state.py`).
- Verified: all 14 acceptance items A1-A14 and AC11. Final runs on the final state: Windows, a checkout path with spaces and WSL, 763 tests OK each; validate PASS. Live: 8 rounds in Hooqd, Mulcol-app2, PletrixV2 and Altinstar; a PowerShell-tool write denied before approval; a write-enabled Codex run that changed nothing. Reviews: fresh reviews for T1, T2, T3/T4/T6, the whole feature (V9) and the baseline helper (V11); the fixes from V9 and V11 were checked by tests and the final runs, not by a second review.
- Not run on this host: symlink and POSIX file-mode cases. Codex results show model behaviour, not enforcement (Codex has no hooks).
- Decisions made for the owner (by: agent): D7-D10, to review.
- Not committed or pushed (owner, 2026-11-03). Release zip: `.artifacts/release/workflow-axa-2.8.0-rc.1.zip` (SHA-256 e2f4d7ce…). Gate cache: `%TEMP%\workflow-axa-gate` (pruned after 14 days).
- Next safe action: the owner accepts the delivery and reviews D7-D10; then the follow-up simplification review (proposal only, waiting for approval).

## Follow-up r4: session recovery and approval defects (2026-11-05)
- Phase: delivered source candidate. Current checkpoint and Outcome supersede this initial follow-up status.
- Working context: D:/wfaxa-pilot/workflow-fixes, source snapshot without .git; extends this audit's approval/recovery scope. Cheflabels retains its separate task and approvals.
- Source: D:/workflow-axa main 0d67057a6e15b72436624e48b0698bab00185ab5 plus existing UI-lite edits. Tracked diff SHA-256: 2f11292dd0d1a64c1b93c1bf9fe0a16305e7c90c5455c3abdfb840f4da3dcd72.
- Authority: user requested "fix all of it" after the audit findings. This authorises the isolated candidate work. It is not a claim that a new HTML plan was presented/approved, and grants no live installation or Cheflabels transfer approval.
- Rules: READY for isolated package investigation/candidate work. Read root AGENTS.md/CLAUDE.md, installed START/CORE/READINESS, operations, data-contracts, testing, security, compatibility, reliability and artifact policy. Installed shared rules 1.8.2; no setup stamp required. Original checkout edits and live hooks protected.
- Output parent: .artifacts/2026-11-03-audit-hardening/. Keep baseline/red/final regression evidence and deliverable candidate; temporary fixtures owned by unittest clean themselves.
- Scope: precise revision parsing, mixed-hook diagnosis, trusted report presentation, workspace-bound consent, read evidence, waiting and goal guidance; regressions and deployment recommendation.
- Authority boundary: live installation remains outside scope. Cheflabels r5, final transfer and worktree removal later received separate owner approval. Both bounded paid batches are complete.
- Completion: candidate implementation and local checks finished. Live positive write/restart remains unverified. Final packaging is a separate handoff step.

## Outcome

Follow-up r4 is delivered as an implemented source candidate with partial live verification on 2026-11-05. The earlier r1 delivery and presented progress-r4 snapshot remain historical.

- Asked and authorized: "fix all of it" after the audit. This direct instruction covers isolated fixes and verification, not installation or approval of an unseen HTML revision.
- Built: precise revision parsing, hook registration compatibility, workspace-bound consent, completed-question presentation, whole-read evidence, quiet approval waits and recovery guidance. Candidate URI/link parsing regressions were found and repaired before this delivery.
- Tickets: F1-F6 verified at the local test boundary. Unobserved live positive write/restart is a verification limit, not unfinished implementation or authority for more paid work. F7 accepted and transferred under its separate owner approval.
- Verification: 886 tests, zero failures/errors, 14 skips in 171.116 seconds. Validator PASS with 699 core words. Final Standards and Spec reviews PASS after repairs.
- Offline replay: corrected-record approval and same-workspace sibling-transcript recovery passed. Reply fingerprint output was regenerated. This is not a live model restart or write.
- Live evidence: four paid processes across two approved batches. Waiting and rejection behaved correctly. Host permission and malformed-record limits prevented a positive model-driven write/restart result. Reported combined list-price total: USD 0.171788. No more paid calls.
- File map: phase_gate.py and gate/session tests support F1-F3. hooks.json supports F2. plain_reply.py and read/Stop tests support F4. workflow and doctor guidance support F5. Version metadata, fixtures, preserved UI-lite snapshot expectation and delivery records support F6. The renderer changes only its version label.
- Preservation: original checkout edits and historical reports remain intact. No new CSS, dependency installation or live plugin/cache/settings change. D7-D10 remain historical agent decisions, not newly accepted policy.
- Cheflabels: owner accepted the repaired runtime result and final transfer. The original branch contains the verified files and task evidence. Its disposable worktree was removed. No commit or push.
- Retained evidence: final suite, selected red reproductions, original UI-lite failure, final offline replay and protected reports under .artifacts/2026-11-03-audit-hardening and this task. Raw host traces remain outside the release archives. No unfamiliar output was removed.
- Limits: 14 native/environment skips, no new POSIX suite, no live positive write or write-after-restart, no universal language/command enforcement claim. Cheflabels native devices and remote translations were outside its browser check.
- Packaging: reserved paths .artifacts/2026-11-03-audit-hardening/release/workflow-axa-2.8.0-rc.4.zip and workflow-axa-2.8.0-rc.4-source.zip. Archive creation and SHA256SUMS.txt remain the parent handoff step.
- Delivery snapshot: reviews/delivery-r4-final.html. Source/tests are delivered with the stated limits. The earlier delivery-2026-11-05 draft is preserved as superseded. No installation or transfer approval question is attached.

## Follow-up rollout checkpoint (2026-11-05)
User accepted Cheflabels and approved the bounded live batch (D-rollout-1/2). This is the requested continuation of workflow testing, not a new product feature. Candidate worktree: D:/wfaxa-pilot/workflow-rollout, detached from45670f28ce506d5df43a9e632c9fd2cdcdcc9931. Original D:/workflow-axa main is clean. All skill development/checks happen in this worktree. Output parent: .artifacts/2026-11-03-audit-hardening/rollout/. Rules READY: original AGENTS/CLAUDE, shared START/CORE/READINESS/VERSIONS/ENGINEERING/operations, artifact policy and installed skill-authoring guidance inspected. Rules stamp NONE is informational. No subagents for this rollout.

Direct task authority: owner explicitly requested update/push, download latest, run Claude Opus5.5 across all five named repositories, exercise rules/design/agreements/approval/tickets/revisions/report previews and legacy-document handling. The user then accepted Cheflabels and approved the live budget. No unseen HTML plan approval is claimed. Preserve existing gates, approved source reuse and report renderer.

Work: R5a clarify kit setup versus approved example implementation, actual-rendered variant evidence and settled capture readiness; R5b validate/review/release the candidate and install from Git; R5c run staged disposable-worktree scenarios on all named repositories; R5d inspect transcripts/files/reports, fix demonstrated skill defects within this scope and finish with one bounded retrospective. Cases must preserve real components, dynamic source styling and real report samples. Missing rules/preview prerequisites must be surfaced, not silently bypassed. Current package tests and a single provider process are different evidence categories.

Initial evidence: Claude Code2.1.318; current package2.8.0-rc.4. Both installed skill sets match all175 registered package files, with no missing/different files. All target repositories exist. Hooqd and the three Pletrix checkouts are clean; Altinstar has unrelated uncommitted work and existing worktrees. The three Pletrix roots and their parent directories have no AGENTS/CLAUDE files. Use source HEAD worktrees, preserve original edits and load scoped rules before any application-scenario work. Current goal remains unfinished until rollout and all required test cases are reconciled.
