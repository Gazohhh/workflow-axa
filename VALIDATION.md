# Validation

## Current verification

Candidate workflow-axa 2.8.0-rc.5 retains shared rules 1.8.2 and 21 registered skills. This revision clarifies source-backed example creation, actual variant coverage and capture readiness. The approved five-project live evaluation has not started. Prior host evidence below does not certify this revision.

| Evidence | Result and limit |
|---|---|
| Source commit | `45670f28ce506d5df43a9e632c9fd2cdcdcc9931` plus the rc.5 instruction and release metadata changes. |
| Focused kit checks | 40 tests passed. |
| Full suite | 886 tests, 13 environment/platform skips; one documentation failure because this source identity row was missing. All other checks passed. The documentation checks are rerun after adding this row. |
| Live evaluation | Pending. No new paid process has run. |

## History - rc.4 verification

Candidate workflow-axa 2.8.0-rc.4, shared rules 1.8.2, 21 registered skills. Isolated source snapshot at D:/wfaxa-pilot/workflow-fixes. No live installation.

| Evidence | Current result and limit |
|---|---|
| Source commit | `0d67057a6e15b72436624e48b0698bab00185ab5` plus preserved UI-lite edits. Original tracked diff SHA-256 2f11292dd0d1a64c1b93c1bf9fe0a16305e7c90c5455c3abdfb840f4da3dcd72 remains unchanged. |
| Final full suite | 886 tests, zero failures/errors, 14 skips, 171.116 seconds, exit 0. [Final log](docs/plans/2026-11-03-audit-hardening/evidence/rc4-full-suite.txt). |
| Validator | PASS with 699 core words after final code freeze. Parent reruns metadata validation after delivery records. |
| Focused checks | 22 session-recovery tests passed after URI/link repair. Eight new read-evidence and ten existing Stop-hook tests passed. Final suite includes these cases. |
| Reviews | Independent Standards and Spec PASS after all reported repairs, including STATE_VERSION 14 parser. |
| Offline recovery | [Final host-derived replay](docs/plans/2026-11-03-audit-hardening/evidence/rc4-replay-final.json): corrected-record and same-workspace sibling-transcript paths allowed. Reply output regenerated offline. |
| Live behavior | Waiting was idle for 30 seconds and rejection respected. Read-only resume reconciled prior answers. Host permissions and malformed approval records prevented a positive write/restart result. |
| Paid scope | Four processes across two approved batches. Reported combined list-price total USD 0.171788. This is not invoice metering. No further paid run. |
| Separate Cheflabels result | Accepted and transferred to the original branch. Runtime browser checks reported zero errors. Disposable worktree removed. Its separate final report records native/backend limits. |
| Packaging | Parent creates install/source ZIPs and SHA256SUMS.txt under the task release folder after this reconciliation. Reserved paths are not claimed as built archives. |

Current verification is partial. Fourteen native/environment skips, a fresh POSIX run, and live positive write/write-after-restart remain unverified. The hook is conservative command/transcript matching, not a complete sandbox or language interpreter. The prior 878-test pass predates URI repair. Historical figures below do not establish the current candidate result.

## History — rc.3 verification, not current evidence

This is the current verification summary for **workflow-axa 2.8.0-rc.3**, shared rules **1.8.2**, 21 registered skills. It is a test candidate, not owner acceptance, deployment or a guarantee that a model follows instructions. Prior results below are historical.

| Fact | Value |
|---|---|
| Source commit | `9e8338e12a9c6791cfa81a3d63cb8b897cadf2c4` (historical ancestor from the input; not a commit of this candidate) |
| Input | Available rc.2 source ZIP; SHA-256 `d0426dc7162d28c071ff9bd516c95038a3f42795bb01f8145de8e49d33a6f3c6` |
| Candidate content digest | `2ad27b0209bd2b0d28964f1bbd6abeb0d4b271f5e36a687084d1b87945750e2e` (352 files): the rc.3 bytes the owner trial tested; historical, kept as evidence |
| Patched candidate content digest | `5f8927ef99cab9403c34b3b2beb5f099fdac142cda4bc14d5a565cf4dff6907f` (354 files), same scope; the old digest was reproduced with the same method first. Frozen and live-tested in P1–P3; historical |
| Second patched candidate content digest | `b03be15a8cb997372bfbb90cae1787abfc7e12a92a62266563e7adcf7eb67019` (355 files), same scope; not live-tested; historical |
| Pilot candidate content digest | `f9db7ea994f14e8a606eff204b075afa45d704e79893f904dc04a5db729c5ec8` (357 files), same scope; frozen as `rc3 pilot`; not live-tested; historical |
| Pilot candidate 2 content digest | `34bf1447e013df9fe88df9fd0e9d377121d646c0c12185c9d52af86b22ab3d1f` (357 files), same scope; frozen as `rc3 pilot2` for live tests LA and LB. Only change from `rc3 pilot`: the real-project TODO fixture is sanitised (names and paths replaced; ticket IDs, structure, states and verification cases unchanged; parse identical); affected tests and the validator pass; historical |
| Pilot candidate 3 (fingerprint repair) | Frozen as `rc3 pilot3`; digest recorded in the frozen copy's handoff (it excludes this file). `rc3 pilot2` plus the independent repair of report-path capture (`shell_report_paths` in hooks/phase_gate.py: same-command variables and `cd`/`Set-Location`) and the audit's regression fix (paths inside larger arguments such as `python -c` code and `bash -c`, and heredoc bodies; unknown variables or folders still record nothing), with tests, including one that a merely mentioned report cannot approve bytes the owner was not shown. Native Windows 11, Python 3.14, spaced path: validator PASS; **845 ran, 0 failures, 14 skipped**. WSL Linux, same path: validator PASS; 845 ran, 0 failures, 18 skipped. Capture probe: 16/16 (11 forms must record, 5 must not). Not live-tested. |
| Digest scope | Sorted relative source path, NUL, SHA-256, newline for every source-bundle file; excludes VALIDATION.md itself, Git internals, bytecode/caches and raw test artifacts. Identifies bytes, not approval. |
| Date | 2026-11-04 |
| Environment | Linux x86_64; Python 3.13.5; Git 2.47.3; Chromium 144.0.7559.96; Python Playwright 1.57.0 |
| Owner trial report | Read as reported evidence only. No raw transcripts or fresh installed-tree export were supplied. Its $17.05 excluded coordination/retro and is not the old batch total. |

### Freshly observed local results

| Check | Observed result |
|---|---|
| Original rc.2 source | Validator PASS; 786 unittest tests ran: 785 passed, one Git-checkout-only skip. Linux, not a reproduction of the owner's native Windows session. |
| Initial targeted reproduction | Fourteen targeted regression cases against rc.2: 12 failed, 2 passed. This reproduced parser/legacy/path cases using local fixtures, not actual model judgment or billing. |
| Candidate validation | PASS: registered skills, source references, integrity metadata and word budgets; router remains 697 words. |
| Complete candidate suite | `python -B -m unittest discover -s tests -v`: **813 ran; 812 passed, one skipped; zero failures/errors**; exit 0, 374.609 s. |
| New focused regression suite | 27 tests passed. Includes real helper/hook behavior and three instruction-contract checks; the latter are not live model tests. |
| Renamed installation | Seven partial-read hook tests and all 27 new regressions passed from a Linux folder with spaces named `marketplace 003`, not `workflow-axa`. Synthetic Git Bash drive/Windows-case paths tested separately within these cases. |
| Browser suites | 20 general report checks + 19 UI report checks + 10 source-bound kit/report checks = **49 passed**; existing installed Chromium, networking blocked. (This row first said 19 + 19 = 48; `browser_smoke.py` prints 20 checks.) |
| Visual comparison | Four desktop/mobile views against the supplied rc.2 source: **zero changed pixels**, matched render environment. Does not promise identical pixels on other systems. |
| Fresh source extraction | Validator PASS; **107 focused helper/hook/record/release tests passed** from an arbitrary spaced extraction path, plus **all 49 browser checks** rerun. Source/archive equality and ZIP integrity passed. |
| Qualified report identity | Synthetic `D4/T8` ticket rendered with safe `D4-T8` JSON alias, original ID visible in the title, valid graph/dependency links. Existing schema and renderer unchanged apart from package version. |
| Post-trial patch (2026-11-04) | Fixes from the rc.3 owner trial: the partial-read warning shows Windows file names as typed; the phase gate expands `cd "$VAR"` (an unresolved variable folder now needs an explicit path); the ticket parser reports an unlisted or conflicting Status instead of reading it as open, reads `- [ ]ID` without a space and treats "needs human" as outstanding verification, and `record.py tick` refuses such tickets. L1 regression tests use the trial's saved TODO before/after (`tests/fixtures/l1-todo-tidy`). Native Windows 11, Python 3.14, spaced path not named `workflow-axa`: validator PASS; **821 ran, 0 failures, 14 skipped**; 49 browser checks PASS with installed Chrome (run before the parser change, which no browser suite uses). WSL Linux, same path: validator PASS; 821 ran, 0 failures, 18 skipped. |
| Second post-trial patch (2026-11-04) | From live tests P1–P3 (5f8927ef): an approval found in an earlier session no longer carries over after a later revocation, an unrecorded later restriction, a stop with no continuation since, or a report changed after that session; a missing answer gets a focused reconfirmation request naming the report path, recorded on a separate `- Reconfirmed` line while the original quote stays; a resumed session without a named task is pointed at the existing task folders instead of workflow-clarify; a stopped ticket is `Status: paused` with the reason on its own line, and an unlisted status is reported before any closed-word match; the session digest counts hook denials separately. Native Windows 11, Python 3.14, spaced path: validator PASS; **828 ran, 0 failures, 14 skipped**. WSL Linux, same path: validator PASS; 828 ran, 0 failures, 18 skipped. New tests fail on 5f8927ef except one characterisation test (another revision's approval was already blocked). Browser suites not rerun: no renderer or browser-tool file changed. |
| Pilot hardening (2026-11-05) | Report identity is SHA-256 content, not timestamps: the gate's own PostToolUse/UserPromptSubmit hook context fingerprints a task report when a tool call reads, writes or renders it by path and again at the owner's answer, and approval needs the same bytes before presentation, at the answer and at the edit or resumed session; missing evidence means focused reconfirmation. A report rendered with `write_paths` bounds file writes after approval (records stay writable; git, MCP writes without a path and unresolved shell code are not path-checked; approval wording is not parsed). TODO format: overview table (summary only; disagreements with ticket Status/Depends on are reported and block `tick` for that ticket) and labelled ticket sections; round-trip test on a real legacy TODO. Native Windows 11, Python 3.14, spaced path: validator PASS; **842 ran, 0 failures, 14 skipped**; browser suites 20 + 19 + 10 = 49 PASS. WSL Linux, same path: validator PASS; 842 ran, 0 failures, 18 skipped. |
| Preservation | All 65 task-history files and all nine pinned specialist trees match rc.2 byte for byte. Report assets/examples, artifact policy and global activation helpers unchanged. |

The first candidate integration run found eight stale metadata/wording-contract assertions. Version targets and the preserved instruction phrases were brought into agreement; checks were not deleted or suppressed. Additional ticket evidence edge cases were added before the final complete rerun. The one skip needs an actual Git checkout; independent byte comparison covers preservation of the supplied task records.

### Commands for the isolated source bundle

```bash
python -X utf8 -B tools/validate.py
python -X utf8 -B -m unittest discover -s tests -v
python -X utf8 -B -m unittest discover -s tests -p test_rc3_reliability.py -v
python -X utf8 -B -m unittest discover -s tests -p test_truncated_read_hook.py -v
```

For browser commands use the already installed browser's actual path. Outputs must be new temporary QA directories, not real project outputs. Do not install Playwright/browsers without permission:

```bash
python -B tools/browser_smoke.py --browser <installed-browser> --output <new-qa-report-folder>
python -B tools/ui_browser_smoke.py --browser <installed-browser> --output <new-qa-ui-folder>
python -B tools/kit_browser_smoke.py --browser <installed-browser> --output <new-qa-kit-folder>
```

The trusted container here required `--no-sandbox`; do not copy that flag into ordinary desktop/remote environments without its own justification. The environment blocked direct `file://` navigation; browser checks used the identical HTML bytes through content loading with networking disabled. Opening via the user's OS/default browser was not tested.

### Deliberate limits

- Native Windows, actual marketplace installation, Claude/Codex/T3 sessions, global loading and live-agent compliance: **NOT RUN here**. Repeat native Windows in an arbitrary renamed/spaced install path.
- RC3-CASES.md is six proposed live cases, **not six passes**. Actual in-flight cancellation, post-approval C3/C5 builds, resumed legacy work and billing interpretation need the authorised live trial.
- The budget and UI permission changes are instruction/protocol contracts, not a provider spend meter or universal tool-level blocker. Caps require explicit authority and observable accounting before launch.
- The partial-read hook is advisory and handles supported literal paths, not arbitrary shell evaluation. Legacy approval checks rely on accessible presentation/answer evidence and do not prove semantic scope equivalence.
- The ticket parser flags explicit record inconsistencies; it does not interpret every prose format, run tests, authenticate decisions or prove evidence freshness. Tick does not turn a claim into verification.
- No app, project TODO, global profile, installed runtime, existing report or paid-model test batch was changed or launched here. Pending D7–D10 and previous delivery acceptance remain pending.
- Use this candidate alone if an older control is unavailable. Do not demand an overwritten RAR or invent a comparison result. Live batch scope and all-inclusive budget require separate owner approval; no automatic retries, repairs or rollout.

## History — previous results are not current evidence

### rc.2 verification (historical)

This is the authoritative summary for the candidate. Existing task checkpoints and the history below belong to prior work; they do not accept this release or the owner's pending D7–D10 choices.

| Fact | Value |
|---|---|
| Package | workflow-axa 2.8.0-rc.2, rules 1.8.1; 21 registered skills |
| Source commit | `9e8338e12a9c6791cfa81a3d63cb8b897cadf2c4` (supplied input parent only; candidate changes are not committed) |
| Input archive SHA-256 | `ec25c67dfe0c98cd05bf5df35178dad679905b550bbf90932e308c64f6df3d1b` |
| Candidate content digest | `cb7a2e7d27a1a132c0b35eedf259a3b4ae78b23e63d60e2cbb0c3aae71cf174a` |
| Digest scope | Sorted source path, NUL, SHA-256, newline for each packaged source file; excludes VALIDATION.md itself, Git internals, caches and raw artifacts. This identifies bytes, not consent or test completeness. |
| Date | 2026-11-04 |
| Environment | Linux x86_64; Python 3.13.5; Git 2.47.3; Chromium 144.0.7559.96; Python Playwright 1.57.0 |

#### Freshly observed checks

| Check | Actual result |
|---|---|
| Original input baseline | Validator PASS; 763 unittest tests ran and passed; 0 skips. These Linux results do not reproduce the original Windows or live-model sessions. |
| Candidate complete unit suite | `python -X utf8 -m unittest discover -s tests -p "test_*.py" -v`: 786 ran, **785 passed, 1 skipped, 0 failures/errors**, exit 0. |
| Skip | `test_skills_are_lf_and_task_records_are_untouched`: Git checkout unavailable in this source copy. Separate byte comparisons confirm preservation of 65 supplied task-history files. |
| New boundary regressions | 23 targeted tests pass, covering full-answer approval, presentation/waiver provenance, scope/revision references, direct stop/resume, baseline inputs and conditional guidance. |
| Package/static checks | Validator PASS: metadata, 21 skills, references, rule integrity and word budgets. Existing instruction regression and contract suites pass. |
| Report browser suite | 19 checks PASS. |
| Optional UI screen browser suite | 19 checks PASS. |
| Source-bound kit browser suite | 10 checks PASS. |
| Visual comparison | Four existing desktop/mobile report views compared against this supplied input: 0 changed pixels in each, in the same controlled environment. |
| Preserved material | Nine pinned bundled specialist trees, resume-task, current ui-design policy, artifacts policy/installer, report assets and examples, and all 65 existing task-history files are unchanged. Renderer code differs only in its embedded package-version label. |
| Live model/host evaluation | **NOT RUN**: Claude, Codex and T3 are not available here. No paid/model evaluation, global install, runtime replacement or owner acceptance occurred. |

The full suite above ran on the final implementation and tests before writing this validation summary. The distributed source ZIP is separately checked for archive integrity and byte equality, then its validator and focused regression/packaging/documentation tests are rerun. Those extraction checks are reported with the handoff; they are not another full 786-test run.

#### Reproduction

From the source-and-tests bundle, using already available tools:

```bash
python -X utf8 tools/validate.py
python -X utf8 -m unittest discover -s tests -p 'test_*.py' -v
python -X utf8 -m unittest discover -s tests -p 'test_followup_boundaries.py' -v
python -X utf8 tools/browser_smoke.py --browser /path/to/chromium --output /approved/test-location/report
python -X utf8 tools/ui_browser_smoke.py --browser /path/to/chromium --output /approved/test-location/ui
python -X utf8 tools/kit_browser_smoke.py --browser /path/to/chromium --output /approved/test-location/kit
```

Do not install missing tools, start live model sessions, update global profiles or regenerate accepted screenshots without the relevant approval. The install ZIP deliberately omits source development tests/tools; use the source bundle for verification.

#### Failures found during this review

The first 16 new regression checks against the input produced 10 failures and 1 error. Candidate fixes and additional positive cases produced the current 23 passing boundary checks. Intermediate runs exposed stale phrase/version assertions, which were corrected to reflect the retained requirements rather than weakening the boundaries. The input's browser harness also expected older wording; its captured-UI test fixture wrongly retained a not-needed preview status. Only fixture/expectation corrections were made; the renderer's authority validation and styling were preserved. See CANDIDATE-REVIEW.md.

#### Limits

The hook remains a heuristic aid, not a complete authority engine or sandbox. It verifies several narrow transcript facts; it cannot interpret every condition, guarantee file-by-file scope, authenticate arbitrary external text, revoke all sibling-session authority or cancel running tools. A generic matched approval does not enforce separate publication/Git consent. Task selection still uses the supplied D8 heuristic; that pending decision is not accepted here. Current project policies and host permissions remain necessary.

Baseline signatures cover recorded Git inputs, exact command/cwd and selected environment facts, not every external service, ignored artifact or variable. A matching saved baseline is not proof a check ran. Stop-hook read/review signals do not prove review completion or quality.

Direct local-file navigation was blocked by browser policy. The identical generated HTML was loaded using the browser content API with networking disabled; successful browser suites observed no external requests or script exceptions. This does not prove desktop double-click behavior, cross-browser accessibility, real component captures or human comprehension. Visual equality covers four fixtures only, not every possible report.

No Windows/T3 installation or current project repository, application build, device, production backend, real design-kit runtime or account was tested. No claim is made about lower actual token costs, improved live success rates, or the screenshot's 6,400-word saving. The bounded live comparison and one read-only retro remain for the owner to authorise; see CLAUDE-TEST-PROMPT.txt.


### Earlier history — supplied results, not current evidence

### Supplied current verification (2.8.0-rc.1)


Generated by `tools/verification_summary.py` from the command output below. This is the only current evidence; everything under History is older.

| Fact | Value |
|---|---|
| Package | workflow-axa 2.8.0-rc.1, rules 1.8.0 |
| Source commit | `9e8338e12a9c6791cfa81a3d63cb8b897cadf2c4` |
| Working tree | uncommitted changes present |
| Date | 2026-11-04 |
| OS | Windows-11-10.0.26200-SP0 |
| Python | 3.14.2 |
| Git | git version 2.38.0.windows.1 |

| Check | Command | Result |
|---|---|---|
| Unit tests | `python -X utf8 -m unittest discover -s tests -p "test_*.py" -v` | exit 0; 763 ran, 750 passed, 13 skipped, 0 failed |
| Skip reasons | | FIFO unavailable (1); File symlinks need a privilege this host lacks; file-link rejection is unverified here. (5); POSIX permission bits (1); Symlink unavailable in this environment (1); Symlinks unavailable (1); Symlinks unavailable on this host (1); This host does not permit symlinks. (1); Windows has no POSIX permission bits; mode preservation is unverified here. (1); symlinks unavailable (1) |
| Validator | `python -X utf8 -I tools/validate.py` | exit 0; PASS: package structure, manifest consistency, minimal metadata, twenty-one local skills, relative links, core budget (700 workflow words). |
| Browser suites | | NOT_RUN |
| Visual regression | | NOT_RUN |
| Host discovery | | NOT_RUN |


### Earlier source history

 — earlier results, not current evidence

Each block below records what was observed at its own date, commit and environment. None of it describes the current tree; the section above does. Counts and versions in these blocks are the values of their time.

### Modular refactor (2.8.0-rc.1) — observed 2026-11-02, before the audit hardening

Task: `docs/plans/2026-11-02-modular-engineering-workflow/` (PLAN, TODO, FINDINGS E11–E20, DECISIONS D1–D10). Host: Windows 11, Python 3.14.2, Claude Code CLI with Opus 5.5, codex-cli 0.166.0. Every result below was observed on 2026-11-02; each behavior run is one run, not a statistical sample.

#### Pre-refactor baseline

Commit `9daf507` (2.7.0-rc.7) plus task records: `tools/validate.py` PASS; unittest 545 ran, 11 skipped (from `reviews/implementation-r1.json`). The rc.8 snapshot under the rules-audit task's artifacts is the comparison package for behavior runs.

#### Package checks (final state)

| Check | Result |
|---|---|
| `python -X utf8 tools/validate.py` | PASS: twenty registered skills, metadata, word budgets, required files, relative links |
| `python -X utf8 -m unittest discover -s tests -p "test_*.py"` | 620 ran, OK, 11 skipped (after the D14 design loop, FINDINGS V21). Every skip is a host limit (no file-symlink privilege, no FIFO, no POSIX mode bits); symlink/FIFO rejection stays unverified on Windows |
| Vendored skills | Upstream file hashes and the unchanged upstream text inside each `SKILL.md` match VENDORED-SKILLS.md (test proven to fail on a one-character edit) |
| Report layout | Legacy inputs render byte-identically apart from timestamps; reader-first layout checked by screenshot at 1280 and 390 px (`.artifacts/.../checks/report-readability/after-*.png`). No visual-baseline test covers task reports |
| Visual regression (same environment) | PASS: rc.8 snapshot vs candidate, 4 legacy-fixture captures pixel-identical (Playwright 1.64.1, installed Chrome). Shipped 2.2.1 baselines: NOT_VERIFIED (other environment) |
| Browser suites | PASS: browser_smoke 20, ui_browser_smoke 19, kit_browser_smoke 10 checks |
| Native plugin discovery | PASS: installed from the local marketplace; a fresh session without `--plugin-dir` resolved `/workflow-axa:workflow` from the package (20 skills, ~1,760 always-on tokens) |

#### Behavior runs (headless `claude -p --plugin-dir`, exact candidate source)

Worktrees: `D:/Altinstar/wfaxa-eval`, `D:/Altinstar/wfaxa-eval-base` (sparse; branch `eval/workflow-axa-*`) and `D:/Cheflabels-labeler-V2-wfaxa-eval`. Main checkouts and the separate web repository were not modified.

| Run | What it tested | Observed |
|---|---|---|
| E2 vs E1/E1b | Same Altinstar prompt on rc.8 and candidate | Both grounded; candidate added cents/BTC, both brands, kit consequence. E1 (pre-fix router) skipped gate one; E1b (fixed router) held it |
| E3 (6 turns) | Cheflabels, wrong premise, contradictory and partial answers, scoped reopening | Found the false premise, derived follow-ups from code, revised only affected agreement items, reached gate two with a kit-reusing plan |
| E4 | Direct `workflow-execute` without gate two | Refused, wrote nothing |
| E1-t3, C2 | Execution and delivery in fresh sessions | Red→green observed; independent reviews found real defects (wrong endpoint); deliveries honest and partial; external repo untouched |
| A2 s2/s3, A3, A4 | Multi-session resume, agreement, plan, build, in-scope repair, task extension | Resumed from records alone; state lines at turn end; repair handled without new gates; extension added as revision r2 |
| A5–A11 (loops 4–6) | Lightweight boundary, combined gates, router invocation, identity questions, HTML report for small changes | Found and fixed: a rewrite regression (visible changes treated as lightweight), clarify asking plan approval itself, router not invoking phases, identity questions bundled with approvals, borrowed shortcuts. Observed after fixes: combined approval (A6), full execute→independent review→deliver chain (A7), identity-only question (A11 s1), HTML report for a one-line change (A11 s3) |
| A4 s2, A4 s3 | Explicit plan waiver; direct `workflow-deliver` | Waiver honored; agent-written ticket recorded `by: agent`. After the snapshot rule became a "Done when" condition, a direct deliver call made the dated snapshot unprompted, kept the earlier report, and downgraded a stale verdict to partial |

Defects found by these runs and fixed: router not invoking phase skills; questions before tracing; skipped `tdd`; no baseline run; repair changing visible behavior shipped before asking; delivery snapshot skipped. Each fix has a static regression test (`test_behavioral_cases.py`). Re-observed live: router invoking phases (E1b, A11), state lines (A2–A11), `by: agent` (A4 s2), delivery snapshot (A4 s3, A7 s2), baseline run before changes (A6 s2), independent review subagent (A7 s2), HTML report for small changes (A11 s3). Not re-observed: reading `tdd` before the first test, asking before a visible repair.

#### Reviews

Independent Claude (fresh context) and Codex reviews: R1 (13 findings), Codex R2 (17), Codex R3 (14), final Claude review (15), all applied (the two deferrals were later done, E22). Retros: 55 real sessions (nine fixes, E16) and the ~25 evaluation sessions (five fixes, E23).

#### Not established

- Claude Desktop discovery (Claude Code CLI and Codex verified; Codex via project-scoped `.agents/skills`, which took precedence over the global rc.8 copy).
- Statistical reliability: one run per scenario.
- Renderer tests show structure and consistency; they cannot prove a projection matches its records' meaning or that a recorded check ran.

### 2.7.0-rc.8 — history, not 2.8.0-rc.1 evidence

Date: 2 November 2026. rc.8 is the committed rc.7 tree (`9daf507`) plus the Windows verification fixes listed in CHANGELOG. Run on the owner's Windows 11 machine: Python 3.14.2, Git 2.38.0.windows.1, Pillow 12.1.0. Python Playwright is not installed. Checks ran with `PYTHONDONTWRITEBYTECODE=1` and `python -B`; output went to the console.

#### Observed package checks (rc.8, Windows)

- Unmodified rc.7 on this host (before the fixes): validator PASS; unittest **545 ran = 534 passed + 11 skipped**.
- rc.8 source: `tools/validate.py` PASS (exit 0). `python -X utf8 -m unittest discover -s tests -p "test_*.py"`: exit 0, **546 ran = 535 passed + 11 skipped**.
  - Skipped: 5 symlink-dependent tests; 4 file-symlink rejection tests ("file-link rejection is unverified here"); 1 POSIX-mode test ("mode preservation is unverified here"); 1 FIFO test.
  - Directory-link rejection was exercised through NTFS junctions.
- The release archive and extracted-tree results are recorded below once run.

#### Not run or unverified (rc.8)

- No browser suites: Playwright is not installed here and was not installed. rc.7's browser results (Linux) are history and do not cover rc.8.
- On this host: file-symlink rejection and POSIX file-mode preservation.
- No live Claude/Codex sessions; no application tests, builds or backend calls.

### Earlier candidate (2.7.0-rc.7) — history, not rc.8 evidence

Date: 30 October 2026. Based on the actual supplied rc.6 archive. Tests use Python 3.13/Linux and Chromium 144.0.7559.96 with already installed Playwright. This release changes the package only, not an application, live kit, user profile, memory, device or global installation.

### Observed results

- rc.6 baseline: **490 tests ran, 489 passed, 1 skipped** (Git-checkout-only policy test; archive has no .git).
- Candidate: **545 tests ran, 544 passed, 1 skipped**, same checkout limitation. Fifty-five added regressions exercise strict UI policy, exact component/pattern/variant/state/example selection, scope and candidate rejection, capture input/image fingerprints, changed/deleted sources, partial approval, source escaping and local Storybook-index discovery. No unresolved failing tests or expected failures.
- Package validator: PASS, eight local skills, relative references, manifest consistency and existing word budgets. Main workflow: 1,236 words. Shared rules library 1.6.0, package rc.7.
- Browser suites: **19 base-report + 19 historical/additive UI + 10 source-bound kit checks = 48 passed**. The new suite checks component details, element/source navigation, mobile scrolling, no-script disclosures, inert images, offline behaviour and deletion without rewriting the saved report. Its grey PNG and catalogue are synthetic fixture data, not a real application kit or human approval.
- Visual regression against rc.6: initial comparison matched three views exactly and found eight edge pixels different in the desktop-build view. No report asset or threshold was changed. A second capture matched all four views exactly against the original baseline. This small rendering variability is disclosed rather than claiming universal pixel identity.
- All four report assets (`report.css`, `report.js`, `ui-review.css`, `ui-review.js`) are byte-identical to rc.6. The existing full report shell is retained; exact selection tables are added only to optional UI-screen details using existing styles.
- All **34 pre-existing task-history files** are byte-identical. Matt's catalogue differs only in the package version field. Questioning policy, artifact policy/installer, shared TypeScript rule and global activation helper are byte-identical.
- Release packaging: archive integrity and source/extraction equality are checked. Package validation, all tests and all three browser suites are rerun from the fresh extracted release. No generated QA images/logs, machine paths, Git internals or Python caches are included in the installable archive.

### Initial failures and repairs

The first suite runs identified stale version assertions and missing documentation wording after the edit. Those were corrected without weakening the checks. Browser verification caught a changed accessible label for existing decision markers; that label was restored. The new fixture exposed a missing-source error path and narrow mobile table columns; the error now names the missing kit source, and the optional table reuses the existing scrollable technical-table styling. No application theme, core report CSS or screenshot reference was changed to force a pass.

### What the checks do not establish

- **No live Claude/Codex/T3 loading or compliance test was run.** All 26 new cases in [STRICT-KIT.md](tests/behavioral/STRICT-KIT.md) remain NOT RUN. Earlier live-host cases remain unverified unless their own evidence establishes otherwise.
- No real Altinstar/Cheflabels kit, React/Angular component runtime, backend, build or device was inspected or modified. Installing this skill does not create a kit page, set up Storybook, run a sync service or migrate project documentation.
- No OS/tool-level hook, permission blocker or absolute prevention mechanism was installed. Instruction compliance still requires actual host testing. The diff helper is triage, not approval or comprehensive enforcement.
- Source hashes establish that declared inputs match supplied bytes. They do not authenticate a human decision, prove every dependency is listed, or prove the captured pixels came from that code. Actual render evidence and owner acceptance remain necessary.
- The optional Storybook adapter reads a local generated v4/v5 index. It detects missing story files/entries but is not a compiler or module graph; deleted exports or broken nested imports still need project verification. Tags are not approval. Generated indexes can themselves be stale.
- No native Windows/macOS profile, desktop opener, Firefox/Safari, real accessibility audit or human comprehension test was performed. Existing Windows-related regression fixtures remain present.

### Browser transport

Direct file:// navigation was blocked by the managed environment (ERR_BLOCKED_BY_ADMINISTRATOR). Identical HTML bytes were loaded through the browser content API with networking disabled. No external HTTP/WebSocket request or script exception was observed in successful suites. --no-sandbox was used only in this trusted disposable container. This does not verify desktop double-click/open behaviour.

### Compatibility

Non-UI report input remains compatible and existing saved HTML is untouched. Historical/draft schematic demonstrations remain readable, explicitly non-authoritative. **New approval-ready application UI reports have a stricter contract:** approved-kit selection, real captures, exact elements including the composition pattern, and source/capture evidence. Earlier plain-markup/design-authoring modes do not grant current UI permissions. See UPGRADE.md and UI-FLOW.md; do not silently rewrite old approvals or add mandatory duplicate kit manifests.

### Reproduce with already installed tools

```bash
python -X utf8 tools/validate.py
python -X utf8 -m unittest discover -s tests -q
python -X utf8 skills/rule-maker/scripts/audit_installation.py
python -X utf8 tools/browser_smoke.py --browser /path/to/chromium --output /new/base-check
python -X utf8 tools/ui_browser_smoke.py --browser /path/to/chromium --output /new/ui-check
python -X utf8 tools/kit_browser_smoke.py --browser /path/to/chromium --output /new/kit-check
```

Do not install tools or spend live-model credits implicitly. Browser helpers refuse existing output directories. Keep only necessary release evidence under the artifact policy; these commands do not author or install a project UI.

---

### Earlier release reports — historical, not current results

## Validation — workflow-axa 2.7.0-rc.6

Date: 30 October 2026. Based on the owner's uploaded rc.5 source checkout and original review-r2.html. Testing here used Python 3.13/Linux and Chromium 144.0.7559.96 through already installed Playwright. No application repository, production backend, global host profile or remote model was modified or invoked.

### Observed results

- Supplied rc.5 baseline in a sanitised package: **437 tests ran = 436 passed + 1 skipped**. The skipped test requires a Git checkout; the installable payload deliberately contains no .git. This is a separate Linux run, not a claim to have repeated the source's Windows environment.
- Candidate: **490 tests ran = 489 passed + 1 skipped**. The same Git-checkout-only test was skipped. No expected failures or unresolved failing tests. Fifty-three new tests cover optional UI schema, authority boundaries, source/PNG validation, preserved sections, safe escaping, original views, capture sources, installation extras and policy references.
- Three new regression tests first demonstrated missing draft-preview/kit/acceptance constraints; after the targeted fix they pass. No test assertion was weakened to suppress those failures.
- Package validator: PASS; eight local skills, references, metadata and rule manifest. Core sizes remain within existing budgets (workflow 1,250 words; codebase-map 844; ui-design 849, including frontmatter).
- Existing browser suite: **19 checks passed**.
- New additive UI report suite: **19 checks passed**. Includes full-report preservation, diagrams and screen tabs, native zoom/Fit, source/decision links, desktop/mobile overflow, inert screen controls, no-JavaScript navigation, print layout and the local PNG path.
- Visual comparison: **four legacy desktop/mobile views match the uploaded rc.5 with zero changed pixels** in the same controlled environment. This does not assert that new UI views have no pixels, nor promise identical fonts across operating systems.
- Both original R2 SVG diagrams are structurally identical in the additive sample. The original report.css and report.js are byte-identical; optional UI CSS/JS are appended only when ui_review is present.
- Original review-r2.html matches the supplied historical task file byte-for-byte. All **33 existing task-history files** are preserved. The Matt specialist registry is unchanged apart from package version. Grilling policy, artifact policy/installer, TypeScript rule and global activation helper remain byte-identical.
- Source rule manifest: consistent. Shared library 1.5.0, package 2.7.0-rc.6. Source-to-release byte equality, ZIP integrity and the final extracted-run results are checked during release packaging.

### Browser and artifact limits

Direct file:// navigation was blocked by this managed test environment (ERR_BLOCKED_BY_ADMINISTRATOR). The identical generated HTML was tested through the browser content API, offline. No external HTTP/WebSocket request or JavaScript exception was observed. No desktop default opener, Firefox, Safari, native Windows/macOS installation or device rendering was tested. --no-sandbox was used only for Chromium inside this trusted disposable container.

The report uses no network assets or bundled fonts. Screens are either inert structured sketches or bounded local PNG captures. The parser validates structure, dimensions, CRC and limits; it does not scrub private pixels, verify the depicted application or authenticate designer consent. The tested image fixture is synthetic. No real project kit was rendered.

### Explicitly unverified

- **No live Claude/Codex/T3 session, context loading or compliance test.** Fourteen new cases in [UI-SCREEN-FLOW.md](tests/behavioral/UI-SCREEN-FLOW.md) remain unrun, as do earlier live cases unless separately established in their own histories.
- No current Altinstar/Cheflabels code, kit, memory, build, backend or device acceptance. Source records of owner decisions and past tests are preserved, not independently re-certified.
- The owner's rc.5 runtime swap/global activation were still held in the supplied checkpoint. This release does not perform them or imply they succeeded.
- No OS sandbox or agent-tool permission hook is installed by this update. Read-only helpers check structure/freshness, not all ways an agent might act.
- The installation audit is relative to a trusted local package, not a remotely authenticated signature. Unexpected files inside the eight owned trees are flagged, not deleted. Unrelated external skills remain outside its comparison.
- Old schema-2 inputs still work. An old renderer may ignore the new optional UI field: install the complete new codebase-map folder and verify the UI tab rather than assuming an older runtime supports it.
- Presentation snapshots are not current task status. Draft, design-authoring, behaviour approval, implementation and release remain distinct.

### Reproduce locally

From a complete package, with already installed optional tools:

```bash
python -X utf8 tools/validate.py
python -X utf8 -m unittest discover -s tests -p 'test_*.py'
python -X utf8 skills/rule-maker/scripts/audit_installation.py
python -X utf8 tools/browser_smoke.py --browser /path/to/chromium --output /new/qa-directory
python -X utf8 tools/ui_browser_smoke.py --browser /path/to/chromium --output /new/ui-qa-directory
```

Do not run browser installations or live-credit tests implicitly. Existing output directories are not overwritten. Optional visual capture/comparison commands are documented in tests/VISUAL-REGRESSION.md.

---

### Earlier release reports — historical evidence, not this release's environment

## Validation — workflow-axa 2.7.0-rc.5

Date: 30 October 2026. Built from the rc.4 source tree on the owner's Windows 11 machine. Python 3.14.2 (Windows), Git 2.38.0.windows.1, Pillow 12.1.0. Python Playwright is not installed. Checks ran with `PYTHONDONTWRITEBYTECODE=1` and `python -B`; output went to the console.

### Observed package checks (rc.5)

- `python -X utf8 tools/validate.py`: PASS (exit 0). Eight skills, manifest consistency, shared-rule hashes, relative links; workflow core 1,235 words.
- `python -X utf8 -m unittest discover -s tests -p "test_*.py"` in the source checkout: exit 0. **437 ran = 426 passed + 11 skipped.**
  - Skipped: 5 existing symlink-dependent tests ("symlinks unavailable"); 4 file-symlink rejection tests ("file-link rejection is unverified here"); 1 POSIX-mode test ("mode preservation is unverified here"); 1 FIFO test.
  - Directory-link rejection was exercised with real NTFS junctions.
- **Release archive:**
  - The replacement ZIP holds every Git-tracked file in its working-tree bytes, plus `.gitattributes` and the two new test files.
  - It excludes this release's live-audit task folder (`docs/plans/2026-10-30-rules-audit-design-kit/`), which holds machine-specific evidence.
  - It was extracted into a fresh directory. Archive integrity passed, and the payload is byte-identical to the source.
  - In the extracted tree: validator PASS (exit 0); unittest exit 0, 437 ran = 425 passed + 12 skipped (the extra skip is the Git checkout-policy test, since the extract is not a Git checkout); installation self-audit DISK_MATCH at 2.7.0-rc.5.
- Skills inventory: 95 files, sha256 `a53b10d516db7b060d4588905b148516516990e32bdf6c8b9b5e9654ff108abd` (sha256 over the sorted list of "path, NUL, file sha256, newline"). Identical in source and extract.

### Not run or unverified (rc.5)

- **No live Claude/Codex sessions.** Installed, loaded, followed and enforced are separate, and only disk-level checks ran.
- No browser checks or visual comparisons: Playwright is unavailable and was not installed. The flowchart renderer is unchanged from rc.4.
- On this host: file-symlink rejection and POSIX file-mode preservation.
- No Linux or macOS run of rc.5.
- No application tests, builds, device checks or backend calls.

### Earlier candidate (2.7.0-rc.4) — history, not rc.5 evidence

Date: 30 October 2026. Full candidate built from the supplied rc.3 package. The supplied two-project review pack informed requirements; it is not proof of the current repositories or host installations. No private source pack, memory transcript or project component was bundled.

### Observed package checks

- **418 automated tests passed.** Includes all retained regressions plus installation comparison, Angular/Ionic/Capacitor facts, source/config freshness, no-write checks, optional catalogue schema/selection/scope/reference checks, unsafe paths, drafts/deprecation, stale approval evidence and authored-scenario integrity.
- **19 Chromium browser checks passed**, with no external requests/page errors. Covered report layout, semantic controls, view switching, source links, mobile behaviour, optional checkpoint/history and no-script operation.
- **4 same-environment visual comparisons passed with zero changed pixels** against rc.3: desktop proposed/current/build views and mobile proposed view. These compare the approved report renderer, not a real application design kit.
- Package validator passed: eight registered skills, manifest consistency, shared-rule hashes, relative references and existing maintenance budgets. Workflow core remains 1,235 whitespace-delimited words.
- The final ZIP was extracted into a fresh directory; package validation, the complete 418-test suite, installation self-check and 19 browser checks were rerun there. Archive integrity and source/extracted payload equality were checked.

Read the bounded results in [rules-audit-kit-results.json](tests/evidence/rules-audit-kit-results.json) and the tooling transcript in [rules-audit-kit-tooling.txt](tests/evidence/rules-audit-kit-tooling.txt). Prior evidence files remain historical, not new test claims.

### Preservation checks

Matt's 27 catalogue entries are identical to rc.3 except the package release label; the specialist adapters and questioning rules are byte-identical. The shared artifact policy, artifact installer and shared global-reference helper are byte-identical. The flowchart renderer, CSS, JavaScript, local design guide and example files are unchanged. All old package files/task history are retained; no font binaries are included.

### Environment and browser limitation

Python standard-library tooling tests ran on Linux with Git available. Optional visual tests used the already available Pillow and Playwright/Chromium (144.0.7559.96); no package installation was performed. Existing visual comparison code emitted a Pillow deprecation warning; it did not affect the passing comparison and no runtime dependency was upgraded.

Browser checks ran with networking disabled. Managed policy blocked direct `file://` navigation, so the same HTML bytes were loaded via the browser content API. Tests used the explicit no-sandbox switch only inside this trusted disposable container. This does not verify a desktop file opener, Safari, Firefox, native Windows/macOS installation or all accessibility behaviour.

### Explicitly unverified

**No live Claude/Codex evaluations ran.** The 30 new cases in [RULES-AUDIT-KIT.md](tests/behavioral/RULES-AUDIT-KIT.md), as well as earlier live suites, are authored scenarios, not passed model tests. Instructions do not enforce tool calls; the helpers do not install hooks, run the host, infer authentic permission or prove an agent followed a rule.

The installation checker compares explicit candidates against the trusted local package executing it, not a remote release/signature. It does not discover every host cache or identify the host-selected copy from disk alone. Its global check validates managed references, not all user settings or semantic contradictions.

The optional kit checker validates selected local records and fingerprints. It does not authenticate approval, render components, infer all stylesheet/theme dependencies, guarantee preview isolation or approve shipping. Markdown/existing catalogues remain supported without conversion. Included templates contain no approved application components, palette or designer sign-off. Real project catalogue setup requires bounded inspection and approval.

No Cheflabels/Altinstar application tests, builds, production calls, device checks, repository-rule rewrites or memory changes were executed. Any current project contradictions still need an explicit scoped decision. No automatic migration, cleanup, dependency upgrade or publication is included.
