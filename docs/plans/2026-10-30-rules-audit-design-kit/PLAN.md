# Rules-audit corrections and local design-kit support

## Current checkpoint (2026-11-02, deployed — authoritative)

- **Deployed:** workflow-axa **2.7.0-rc.8**, from the frozen isolated snapshot. G1 and G2 ran 2026-11-02 between 12:25 and 12:27 under the existing owner setup approval, after the reviewer's final GO and the coordinator's maintenance boundary.
- **G1:** all eight skills staged under `C:/Users/Cem/.workflow-axa/rollback/2.7.0-rc.8-g1/` and verified (111 files, `5003ddfb07cfe047dbe1122d7c8c4a56c0401ab9de186084260e0c284698b864`; audit MATCH), then swapped one at a time with a journal.
  - The runtime is now 111 files at `5003ddfb...`. The source-to-runtime audit gives MATCH: 0 changed, 0 missing, 0 unexpected.
  - The 8 Claude junctions are unchanged.
  - The baseline (CRLF rc.4, `2c0d0658...`) is preserved byte-exact in `baseline/`. That is evidence-only recovery. The rollback source is `e9b2723`: an integrity-valid LF rc.4. It lacks the Windows helper fixes and has no live acceptance, so it is a byte-valid fallback, not a fully healthy one.
- **G2:** before-bytes saved in `global-before/`. Applied with the installed helper, one host at a time.
  - `~/.claude/CLAUDE.md` → `7a54ae59c4fe839e5997073410ea6680d1c7a0b8d3643fda725c9d58f08ed3f2`; `~/.codex/AGENTS.md` → `4030878c0cfbbeed4985dcef571f3e802d010d7594b27b2bcc95f33d3913a37c`. Both equal the reviewed preview; append-only.
  - Installed `audit_installation --check-global`: DISK_MATCH, both references MATCH. `global_policy --check`: all MATCH. `activate_rules --check`: MATCH.
- **Readiness:** the installed readiness check on both projects gives REVIEW_REQUIRED (rules 1.6.0); it is no longer blocked by the manifest.
- **Memory:** C4 is updated to "deployed 2026-11-02".
- **Layers:** installed and on-disk references are verified. Loaded, followed and enforced are **not** verified; the coordinator owns the four approved live sessions. One observation only: this Claude session's skill list reloaded with rc.8's ui-design description. That is not evidence that rules load in a fresh session.
- **Live acceptance (D12):** three sessions completed read-only and one failed at startup (429). The Altinstar Codex session read START/CORE/READINESS. No complete framework-module reads were observed; the Cheflabels Opus session only grepped Ionic and design excerpts. Mitigation: scope-selected module routing in both projects, plus generic-prose consolidation; this is untested live. Details: FINDINGS "2026-11-02 live acceptance results".
- **Final independent review (Astra, 2026-11-02):** installation and all five project files have no blocker. Four report evidence-labelling fixes were applied.
  - Report: `review-r2-current.json/html`, corrected and re-rendered. The pre-review pair is kept as `review-r2-current.pre-final-review.json/html`.
  - **Verdict, bounded:** installed and on-disk routing verified. Live acceptance is **INCOMPLETE**:
    - three of four sessions completed;
    - Claude loading is not visible in traces;
    - no complete framework-module reads were observed;
    - post-mitigation routing is untested;
    - live cases 4-8 are untested or blocked;
    - enforcement is none.
- **Remaining (2026-11-02 continuation):**
  - First live batch (D12) is exhausted: three sessions completed and one failed on quota. Evidence is in FINDINGS.
  - **Additional batch (D13): STOPPED after its first attempt.** `mcp:launch:03f324583316a900c011e8cac0b345481d6cb3aeb483b5d86abe76a3bb452721` (Cheflabels, Codex gpt-6-astra medium, full-access, same neutral read-only prompt) failed at startup on 2026-11-02 at 11:54:33 UTC with "Usage limit reached: exceeded retry limit, last status: 429 Too Many Requests" (request id `req_f0b498ef070d46239097808bdc960740`). There was no model inspection. Per D13 the batch stopped: no retries, and the remaining three were not launched.
  - **Live acceptance stays INCOMPLETE.** The next prerequisite is Codex provider availability plus a newly authorised batch, not more package work. The coordinator verified the installed, global and project hashes as unchanged.
  - Generic-prose consolidation: done (FINDINGS "mitigation applied").
  - Canonical `VALIDATION.md`: not synced, and it will not overwrite the concurrent 2.8 work. The rc.8 snapshot validation is the release evidence.
  - Project edits are unstaged in both repositories (owner to commit).
  - Report: `review-r2-current.html` is a dated, reviewed snapshot. Its `--check` will show a source mismatch, solely because of this continuation checkpoint. It is not regenerated.

## Checkpoint 2026-11-02 read-only reconciliation (superseded by deployment; kept as written)

- **Source:** clean HEAD `9daf5076763fadcdf8c498cfbaebcd30d71fbaa2`, 2.7.0-rc.7, rules library 1.6.0. Skills inventory: 111 files, `f805cc736c2d16a19137c01a82369982ea154753f03b6edd9375662ca031e0bb`.
  - rc.6 (`3647c14`) audited and kept our rc.5 fixes.
  - rc.7 adds strict UI reuse (behaviour-only).
  - Both newer tasks were package-only.
- **Runtime:** still CRLF 2.7.0-rc.4, rules 1.3.0. 95 files, `2c0d0658aa8b620dac009dd3b4e00f9c7d5271f7cbe94a00522e85b5cea22845`.
- **G1/G2 not run.** No shared-rules blocks; global before-hashes unchanged; no rollback folder.
- **rc.5 archive absent.** `6e706e9a…` is gone with the whole `.artifacts/` folder; cause unknown, not removed by this task. No current rc.6/rc.7 archive is named in the records. The rc.5 test results are history, not rc.7 proof.
- **Projects:**
  - Altinstar: A1, A2, A3, A5 preserved (committed upstream in `c5cd88e61`).
  - Cheflabels: C1, C2 and C3 are absent (external change); there is uncommitted owner work (`2026-10-31-design-kit-page`, DESIGN.md r3, app routing). DESIGN.md r3:31 allows a plain-semantic-markup fallback, which conflicts with rc.7 behaviour-only.
- **Authority:** Existing approval remains valid for the originally reviewed bounded rules fixes and setup. Execution is held because the exact rc5 candidate is unavailable, current source/project inputs changed, and materially stricter rc7 policy needs owner direction. Reverification alone does not require renewed approval of unchanged work.
- **Resolved 2026-11-02 (DECISIONS D10-D12):** adopt and verify rc.7 with its strict UI policy; align the project exceptions; four post-deployment live sessions, managed by the coordinator. The rc.5 and rc.6 alternatives are closed.
- **Candidate (2026-11-02):** isolated rc.8 snapshot. ZIP `cb822ad2409a25c27671fb5dfea0907f5ced989bf02f0ca0fa0ed67dcf68018f`; skills `5003ddfb07cfe047dbe1122d7c8c4a56c0401ab9de186084260e0c284698b864` (FINDINGS "isolated rc.8 release snapshot"). G1/G2 held for the final technical review and the coordinator’s maintenance boundary. Canonical files are frozen (the modular task owns them as 2.8.0-rc.1).
- **Earlier blocker (resolved by isolation):** a concurrent writer (the modular-engineering task) is changing the same source tree. Packaging and G1/G2 are halted pending the coordinator or owner deciding isolation and ownership; see FINDINGS "rc.7 adoption unit".
- **Now:** sole-editor work on the rc.7 candidate: verification, project alignment, the replacement package, and a fresh G1/G2 inventory and preview. G1/G2 are held pending the reviewer's technical review and the coordinator's maintenance boundary.
- **Next safe action:** after the owner's choice, reconcile the intended candidate and scope. Then: independent review, validation of that exact candidate, and a fresh G1/G2 inventory and preview. The rc.5 G1/G2 plan below is history for an unavailable candidate.

## R2 checkpoint 2026-10-30 (superseded by the 2026-11-02 checkpoint; kept as written)

R2 extends this task with a live audit and the bounded fixes for the installed package and two projects, Altinstar and Cheflabels.

- **Current authority:** the owner's coordination message "approved the rules fix where needed". It covers the bounded R2 rules fixes and their implementation verification (validator and unittest runs). Opus is sole editor.
  - Not covered: application behaviour, styles or dependencies; publication; staging or commits; installs or hooks; artifact deletion; billable live sessions; browser checks.
  - The baseline package test run was a separate one-time approval (DECISIONS D6).
- **Review:** the Astra/medium reviewer `mcp:launch:ef80c6b5da0d196bc244add6975c34141ec9776753bda0d20ab1645957877371` is functioning: full-access runtime, read-only operations.
  - It has reviewed F1, the activation checks and parts of the text diffs.
  - It is now reviewing the unit 1/2 diffs and the G1/G2 package.
  - The first reviewer thread (`mcp:launch:9400bd97…`) is stopped history.
- **F1:** option A is chosen and implemented: raw-byte integrity, scoped LF checkout policy (`.gitattributes`), line-ending diagnosis, and a byte-preserving reinstall. The normalised-manifest alternative was not adopted.
- **Done:**
  - Unit 1, text fixes: D2, A1, A2, A3 (area-specific), A5 plus the cap fix, C1, C2, D1, C4, G3.
  - Unit 2, package: S1-S5, S8, and the Windows helper fixes.
  - Evidence: FINDINGS "R2 implementation log". Altogether this is only part of the R2 proposal.
- **Validation (latest, rc.5 source):** `tools/validate.py` PASS (exit 0). Unittest exit 0: **437 ran = 426 passed + 11 skipped**. Unit 2 alone was 432 = 421 + 11.
  - Two directory-link rejection cases were exercised through real Windows junctions.
  - File-symlink rejection and POSIX mode preservation are **unverified on this host** (explicit skips).
  - Browser checks and live sessions: not run.
- **Held:**
  - G1 runtime replacement and G2 global activation, pending the reviewer's final identity and recovery review (FINDINGS "G1/G2 final plan for rc.5"). After that, they run under D7 with no new owner question.
  - Four proposed read-only live sessions are not approved and not started.
  - C3 was written after the owner's answer (DECISIONS D9), routing UI to DESIGN.md's approved scope. The upstream kit files are untouched.
  - Replacing generic duplicated project prose: waits for verified shared routing.
- **Release identity:** **2.7.0-rc.5** (rules library 1.4.0) is labelled with CHANGELOG, UPGRADE, DESIGN and VALIDATION.
  - Complete replacement package: `.artifacts/2026-10-30-rules-audit-design-kit/release/workflow-axa-2.7.0-rc.5.zip`, sha256 `6e706e9a199144225d4397f1283a2d922540c3c9738794bd7c7a966d4070a525`, 197 entries. It excludes this audit's machine-specific records.
  - Extracted-release checks: validator PASS; 437 ran = 425 passed + 12 skipped; self-audit DISK_MATCH.
  - Skills inventory `a53b10d516db7b060d4588905b148516516990e32bdf6c8b9b5e9654ff108abd`.
  - Not published. Final identity review by the reviewer is pending.
- **Live acceptance:** not run and not claimed. The matrix in FINDINGS is a non-executable draft, not an approval request; the per-case status is in FINDINGS "Live acceptance status".
- **Report:**
  - `review-r2.json/html` is a stale, unpresented draft, kept as history.
  - After review, generate ONE final snapshot as `review-r2-current.json/html` in this folder (same task and revision).
  - Exclusive creation only: no overwrite, deletion or renderer change, and no file per retry. Not generated yet.
- **Next safe action:** wait for Astra's review of the units and the G1/G2 package. Then, within current authority, run G1 → G2 with their checks, label rc.5, build the replacement package and generate the final snapshot.

## R2 checkpoint history (superseded states, kept verbatim)


R2 (2026-10-30). The owner extended this task with a live read-only audit of the installed package and two projects, Altinstar and Cheflabels. The audit covers shared versus project placement, automatic loading, update propagation, missing-rule handling and UI authority.

- Approved so far:
  - read-only investigation and these task records;
  - two exact package commands, approved once by the owner and executed 2026-10-30: `tools/validate.py` and the unittest discover command.
- Earlier state (superseded): no rule, config, memory, hook or application change approved.
- **Current authority (2026-10-30):** the owner's coordination message "approved the rules fix where needed" approves the bounded R2 text fixes. Opus is sole editor.
  - Now in progress: shared `typescript.md` (D2); Altinstar A1, A2, A3, A5; Cheflabels C1, C2, C3; memories D1 and C4; global G3.
  - Manifest: `rules/version.json` metadata only as needed for consistency (via S5 if needed). No release bump during unit 1.
  - Unit 1 status (2026-10-30): applied. A3 was applied, then reverted and HELD with C3 under the design-authority conflict (Cheflabels DESIGN.md r2 vs D3), which the coordinator is resolving with the owner. Upstream kit routes stay untouched. Log: FINDINGS "R2 implementation log".
  - Unit 2 (in progress), under the same owner approval: canonical package S1-S8 with F1 option A, plus narrow Windows fixes to the rules helpers. The reviewer's preference for option A is advice, not authority.
  - **Version decision:** because the package changes, it becomes identifiable **2.7.0-rc.5** (rules library 1.3.0 → 1.4.0 for the TypeScript rule). Labels, CHANGELOG and VALIDATION are updated once unit 2 is complete, with a complete replacement package for delivery. Until then the tree is an unlabelled work in progress, not rc.4.
  - Later, after shared routing is verified: replace only generic duplicated project prose with exact shared references, keeping local evidence and stricter contracts.
  - Live acceptance is not run, and none will be claimed. The matrix still has unresolved runtime, isolation, cost, nested and delegation limits.
  - **On hold until independent Astra review:** the F1 method, code/helper fixes (S1-S4, S8), runtime replacement (G1) and global activation (G2).
  - Not approved: application behaviour, styles or dependencies; publication; staging or commits; installs or hooks; artifact deletion; new test runs.
- Review:
  - The first Astra reviewer thread (`mcp:launch:9400bd97…`) was blocked by the T3 runtime and is stopped (history, not active).
  - With the owner's explicit approval, it is replaced by one Astra/medium reviewer, `mcp:launch:ef80c6b5da0d196bc244add6975c34141ec9776753bda0d20ab1645957877371`: full-access runtime, strictly read-only operations, sole active reviewer.
  - Its review of F1, activation, evidence, the draft and the text diffs is in progress. Nothing is independently reviewed yet.
- Open: owner decisions are pending in the coordination thread. Evidence and the draft proposal are in [FINDINGS.md](FINDINGS.md), section "R2 live audit".
- Package tests (owner-approved, run 2026-10-30): validator exit 0, PASS. Unittest exit 1: 418 ran, 396 passed, 1 failure, 15 errors, 6 skipped.
  - Failure categories: home-directory default, symlink privilege, POSIX mode; all host portability. Causes are still to be independently validated.
  - Link-rejection and mode-preservation paths are unverified on this host.
  - Output-handling deviation: details in FINDINGS "R2 package test run".
- Unresolved review points (coordinator, for Astra):
  - approval-required runtime failed for Astra;
  - denying every command would also block safe loading reads in live sessions;
  - a genuine rc.5 update is not equivalent to the requested isolated marker experiment.
  The live matrix is not revised until review.
- Draft proposal: [FINDINGS.md](FINDINGS.md) "R2 draft proposal".
- Draft loading report: [review-r2.html](review-r2.html), from [review-r2.json](review-r2.json); revision R2-draft, state draft, not yet presented. It passed renderer validation and `--check` **at generation**. It is now stale on two counts:
  - Freshness: the record edits since then changed its source hashes.
  - Content: it predates the coordinator corrections (S6 wording, A5/G3 alignment, root-level UI lines, live matrix).
  - Plan: re-render once after the independent review, keeping the same draft identity. The renderer refuses overwrites and none will be forced, so the stale unpresented draft is replaced only through an ownership-safe step agreed then.
  - Not inspected in a browser; the coordinator will show the final report inline.
- Next safe action: independent Astra review of FINDINGS and the draft. Then resolve the open questions, re-render as a new revision if the content changes, and present for owner approval.

## R1 checkpoint (historical — rc.4 package preparation, complete)

Requested scope: user approved a complete updated workflow package after the two-project rules comparison, including design-kit support. Base: supplied workflow-axa 2.7.0-rc.3. Package implementation authorised; no live application repository, memory cleanup, visual theme, host configuration write or designer acceptance authorised.

Implementation: complete for the candidate. Shared audit/source-conflict/operation rules; Angular/Ionic/Capacitor guidance and static detection; read-only installation checks; ui-design catalogue lifecycle/templates/source-freshness checker; integration and regressions. Release: 2.7.0-rc.4 candidate. Package/tooling validation: 418 tests and 19 browser checks passed; four report comparisons unchanged. Live host/design acceptance: not run. Final measured validation and limits are in the release VALIDATION.md. Next safe action: install one complete candidate in a disposable agent environment and run the authored acceptance cases.

Preserved: eight local skills; Matt catalogue/adapters; grilling; standalone flowchart renderer/assets/examples; artifact policy/installers; existing task history; project-specific constraints.

## Agreement and acceptance (from R1; still in force)

- Full audit and task readiness cannot be reported interchangeably. Installed, loaded, followed and enforced remain distinct.
- Current valid policy is not silently replaced by old narrow memory; actual conflicts need a named decision.
- Tests/build prerequisites and real backend targets need authority/isolation; obligations are not GREEN proof.
- The kit is a source-backed catalogue procedure, not invented application styling. New entries remain candidates; exact approved scope and freshness matter. Existing project kits need no JSON migration.
- Helpers are bounded, read-only, network-free and report uncertainty. No file output from normal checks.
- All package tests and local report checks must be rerun, including an extracted release. Live agent/device/designer tests remain explicitly unverified.

## Revision history

R1: implements the user's requested package update. Meaningful project fixes are described for adoption but not applied to the supplied historical exports. No audit pack, real memory transcript or application component is copied into the release.

R2: live installed-package and two-project rules audit, followed by the owner-approved bounded rules fixes (units 1 and 2). G1/G2, C3 and release labelling are pending; see the current checkpoint.
