# Changelog

## 2.8.0-rc.24 — kit examples render correctly and are visually reviewed (2026-11-07)

- ui-design LIVE-KIT: labels are exact classes or props under their own variant, never prose; each icon is rendered with its class; page shells contribute elements, never whole pages; overlays render open; sticky elements cannot cover others; no empty, unstyled, clipped or placeholder-text examples and no duplicates. Done-when requires a full top-to-bottom screenshot review, repeated until clean. On rc.23 an independent review of a fresh kit found bulk icon lists, prose labels, whole-page examples, trigger-only modals, empty examples and leaked "Laravel::" keys.

## 2.8.0-rc.23 — kit requests reach ui-design; reference kits lend definitions, not navigation (2026-11-07)

- ui-design description now names building, setting up or checking a design kit, so a plain "build the design kit" prompt loads it. On rc.22 a fresh run never loaded workflow or ui-design.
- LIVE-KIT: a reference kit the owner points to supplies its element definitions, class labels, variants and DESIGN.md sections; its tabs, example picker, one-at-a-time views and full-page previews are never copied. The rc.22 run copied the Cheflabels tabs and picker.

## 2.8.0-rc.22 — every kit example defines its classes (2026-11-07)

- ui-design LIVE-KIT: one example per component and per repeated pattern; each shows a definition line (source plus base `tag.class` and modifiers) and a class or prop label on every variant, instead of a bulk class list. Tokens and icons come first. Server-dependent components load their real page's stylesheets and scripts. Done-when adds a visual check of the labels and requires each DESIGN.md to follow `templates/DESIGN.md`. On rc.21 a fresh run produced bulk `Patterns:` captions and a how-it-works DESIGN.md.

## 2.8.0-rc.21 — one-page kit rule stated where setup reads it (2026-11-07)

- ui-design KIT.md setup step and LIVE-KIT anatomy: no per-client or per-module sections, no framed page previews; a view with its own layout contributes its elements to the groups; email and PDF views are excluded as non-screen UI. On rc.20 a fresh kit run read the rule but still recommended module sections and framed page previews.

## 2.8.0-rc.20 — one stacked kit page grouped by element type (2026-11-07)

- ui-design LIVE-KIT: the kit is one page where components and repeated elements appear one under another, grouped by element type (actions, forms, lists, overlays, feedback, icons, layout), never by owner, module or page. Module and client components join the same groups. No per-module tabs, whole-page sub-pages or index page; coverage is a generated project test. Replaces the rc.19 index category.

## 2.8.0-rc.19 — element index visible on the kit page (2026-11-07)

- ui-design LIVE-KIT: the generated element index is both the coverage check and its own category on the kit page. Two fresh kit runs built only the check until the owner asked to see the index.

## 2.8.0-rc.18 — kit "done when" checks against the served app (2026-11-07)

- ui-design LIVE-KIT: a kit is done only when the served build is current, every category and sub-page opens logged out in a real browser without server or console errors or outside requests (owner-allowed services excepted; CDN modules get local stand-ins), write actions are stopped, and the production configuration has no kit route. A fresh kit run on rc.17 needed a fix round for exactly these.

## 2.8.0-rc.17 — mimic question without alternatives (2026-11-06)

- Shared rules 1.8.5: after the exact question, list only same-tag existing elements, nothing else. On rc.16 a fresh Claude session asked the exact question but still listed plain HTML and "add a style yourself".

## 2.8.0-rc.16 — exact mimic question in the always-loaded rules (2026-11-06)

- Shared rules 1.8.4: CORE.md now states the exact no-match question and the allowed options. A fresh Claude session asked for a "tiny" badge edit skipped the ui-design skill and offered new CSS and plain HTML as options; Codex asked the exact question.

## 2.8.0-rc.15 — one in-app design kit with a fixed shape (2026-11-06)

- ui-design: the default kit is one development-only page inside the real application (for example `/design-kit`), registered only in development, outside login, using the real layout and styles; one per application or client build, including its overrides and enabled modules. A separate preview server needs a stated reason.
- New LIVE-KIT section "Page anatomy and coverage": per example a title, a caption naming the exact `tag.class` patterns and variants, then real instances in their real wrappers; server-dependent components render with fixture data. Every component and every element pattern used twice or more must be in the kit or excluded with a reason, checked by a generated element index.
- New `templates/DESIGN.md`: the default shape for a project's design-decision record (intent, source of truth, access, approval, reuse rules, caller-inferred usage guidance, findings, history), with no CSS values or inventories.

## 2.8.0-rc.14 — single-command recovery after a shell denial (2026-11-06)

- Workflow RULES.md: a denied shell command refuses only that command. Run each required helper alone, as one command, before reporting that it cannot run. The rc.13 Claude evaluation (P70) and P67 both stopped after one denied compound command although the single helper commands were allowed.

## 2.8.0-rc.13 — record and required-read guards (2026-11-06)

- In active Claude workflow sessions, reject direct Write, Edit and MultiEdit of canonical task records before bytes change. Use `record.py` instead. Inactive sessions and other paths are unchanged.
- Require a complete read of the flowchart design guide before workflow report validation or rendering.
- Honor optional required-read declarations in the project root AGENTS.md or CLAUDE.md. Entering specify, execute or deliver, and report validation or rendering, wait until each declared file was read whole in the current context. The PreToolUse matcher now includes Skill. The package AGENTS.md declares tests/README.md.
- Make superseded review cleanup in VISUAL-REVIEW.md the single report retention rule. Delivery reuses an unchanged delivery snapshot.
- Shared rules 1.8.3 document required-read declarations in READINESS.md.
- Native Claude CLI and Codex evaluation is pending. It runs after publication on the installed copy; see VALIDATION.md.

## 2.8.0-rc.12 — report preflight and release verification (2026-11-06)

- Add read-only `--validate-input` to the existing report renderer. Reuse schema, source, size and wording checks without files, Python helper caches or browser opening. Existing render and protected replacement behavior stays unchanged.
- Validate before recording the final report path, then save the approval-wait checkpoint before the last check and render.
- Synchronize renderer and authored-scenario version metadata with the package. Preserve historical baselines and every unrun scenario result.
- Repair the parallel append test's pipe handling and child cleanup. Keep its successful-write and lock-refusal assertions. No record.py runtime change.

## 2.8.0-rc.11 — superseded review cleanup (2026-11-06)

- Ask once whether to delete named superseded review files after their replacement is accepted. Reuse one filename for unpresented drafts.
- Preserve active approval dependencies and necessary evidence with stated reasons; reconcile current links before owner-approved deletion. No automatic deletion or changes to other checkouts.

## 2.8.0-rc.10 — development-only preview access (2026-11-06)

- Require kit and developer previews outside login and account initialization in development. Use local synthetic data without backend access.
- Exclude preview routes and preview-only imports from production; hidden links and post-import redirects are insufficient. Verify direct URLs and production output.
- Existing application routes require scoped revisions. This guidance does not itself change applications or prove their build exclusion.

## 2.8.0-rc.9 — isolated preview verification (2026-11-06)

- Check real provider initialization, shell readiness and served-module freshness in isolated previews. Preserve watcher exclusions and separate fixture failures from application defects.
- Altinstar real-component browser interactions pass after fixing the fixture. Narrow desktop-brand layout still clips; no responsiveness or release acceptance claimed.
- Documentation-only correction; hook behavior unchanged.

## 2.8.0-rc.8 — revision naming (2026-11-06)

- Document the existing r1, r2 revision convention before plan generation. Preserve historical report bytes and require explicit owner authority when reconciling another label.
- No hook change. Native Claude recovered the unchanged Hooqd plan after explicit identity reconciliation and began the scoped implementation. Broader project acceptance remains partial.

## 2.8.0-rc.7 — focused retrospective fixes (2026-11-06)

- Separate approval checkpoint status from the quoted owner answer, so pending visual acceptance does not reject an approved implementation. Preserve report fingerprints, quote provenance and refusal/withdrawal checks.
- Handle modern transcript records in the retrospective digest and count host permission denials separately.
- Add regression tests. Candidate suite: 879 passed, 13 skipped; native Claude confirms the conditional approval permits its scoped write. Broader project evaluation remains partial.

## 2.8.0-rc.6 — live evaluation repairs (2026-11-05)

- Preserve real framework identifiers in reused-element references; accept SwatchTile and Form.Group without replacing them with inferred HTML tags. References remain escaped, bounded and tied to source records.
- Return a clear screenshot failure on browser timeout, preserve earlier captures and start no retry.
- Route a resumed setup answer to rule-maker before drafting project rules.
- Add regressions for exact component names, invalid expressions and first/second capture timeouts. Live five-project evaluation remains partial.

## 2.8.0-rc.5 — source-backed examples (2026-11-05)

- Allow approved minimal framework examples and registration using real components and existing markup patterns; setup alone still grants no implementation authority.
- Verify claimed variants against renderers and real callers before promising coverage.
- Capture after presentation and finite transitions complete; compare equivalent caller contexts and disclose unsupported examples.
- No new tooling, dependencies, styling or enforcement claims. Five-project live evaluation remains pending.

## 2.8.0-rc.4 — session recovery candidate (2026-11-05)

- Distinguish report revisions from requirement IDs. Bind report/chat approvals and withdrawals to their actual workspace/task.
- Reject incompatible registration protocols with recovery guidance; preserve fingerprint and real-consent requirements.
- Accept a report-linked question only after its matching successful host answer; never accept thinking or question existence.
- Keep workflow Stop silent at approval waits, document bounded host goals and explicit stale-goal recovery.
- Recognise conservative whole-file shell/Python reads with successful complete tool results; reject conditional, partial and failed reads.
- Preserve UI-lite work; correct its legacy snapshot expectation for the sole explicit frame-denial CSP addition.
- Candidate only: no active installation, external project migration or publication. Live-host and E2 acceptance remain distinct.

## 2.8.0-rc.3 — readable tickets and explicit exceptions (2026-11-04)

- Replace dense TODO example with labelled ticket blocks. Use existing qualified IDs, preserve history and separate implemented, verified, blocked and owner-closed outcomes. `open_items` and `record tick` support both forms; ambiguous IDs and explicit incomplete verification are refused rather than guessed.
- Require an identifiable paid-batch cap and accounting scope, including orchestration/review/retro; no default $40, unresolved placeholder, blanket recommendation consent or unlimited retries. This is a policy, not provider billing enforcement.
- Clarify D14: no plain-HTML recommendation and no generic yes treated as the exception. Legitimate explicit owner instructions remain; no CSS permission added.
- Accept a narrowly evidenced legacy report identity without a fabricated numeric revision; unresolved scope/provenance routes to resume/clarify/specify, never editing the hook.
- Resolve partial-read paths from the actual install root instead of the basename. Support quoted spaces, Git Bash drive forms and relative paths; remove the test workaround which renamed a copy to workflow-axa.
- Keep 21 skills, bundled upstream methods and report appearance. Rules 1.8.2 records the permission clarification. No application/project files or existing history migrated.
- Supply a candidate-only test handoff and six live cases. Local checks do not prove live agent compliance.

## 2.8.0-rc.2 — 2026-11-04 — comparison candidate

- Preserve existing hardening; verify the supplied baseline before changing it. No release acceptance or paid/live evaluation approval is inferred from the screenshots.
- A phase load or report file write is not report presentation. Match the full human answer, including conditions, after the identified report (or an explicitly waived task/revision-bound textual plan). Never permit a later report to borrow an earlier answer.
- Recognise narrowly defined direct stop/hold requests, while allowing handoff records. Do not force another read/review cycle after a recognised stop. This is not a general natural-language intent classifier or sandbox.
- Baseline matching includes exact command text and working directory. Unknown environment evidence and malformed records do not claim verified reuse. The helper does not attest that tests were run.
- Consolidate readiness; preserve legacy reference paths. Shorten phase-loading reminders; load UI and test-first details only when applicable. Cosmetic punctuation alone no longer forces another agent turn. Keep independent review, approval and questioning safeguards.
- Archive old installation detail under UPGRADE history, retain the handoff template and all existing task history, bundled specialist text, UI policy and visual renderer. No new skill dependency or framework upgrade.
- Package workflow-axa 2.8.0-rc.2, shared rules 1.8.1. Actual measured results and limitations: VALIDATION.md. Source and lean-install archives are separate.

## 2.8.0-rc.1 — 2026-11-02

Modular engineering workflow. Builds on 2.7.0-rc.8; its strict UI policy, artifact policy and Windows fixes are carried forward. Shared rules library 1.8.0 (rc.8 had 1.6.0; `skills/rule-maker/rules/CHANGES.md` lists what changed for projects).

Audit hardening (2026-11-03, same version; task `docs/plans/2026-11-03-audit-hardening/`):
- Approval gate: after `/workflow`, the `phase_gate.py` hook allows code edits and git writes only when the current task's PLAN.md Approval line approves a revision and quotes words found in a real user message, or a Lightweight edit line names the file. Loading a phase grants nothing; another task's approval does not count. It also watches PowerShell and MCP write tools and more shell writes. Command-text filtering is advice, not a security boundary (SETUP.md, "What the hooks enforce").
- Safe records: `record.py` writes through a temporary file and a replace, refuses a file that changed since it was read, creates new files exclusively, keeps BOM and line endings, and ticks only the exact ticket ID.
- Stop routes: stopped, paused and cancelled states. "Stop" goes to a partial delivery with no review loop and never back to execution on its own; the handoff names changed files, what was verified, what remains and the next safe action.
- Baselines by test name: `workflow/scripts/compare_failures.py` compares failing tests by identity, so five old failures becoming four old plus one new reports one new failure. A baseline is reused only while its command, commit, diff and environment match.
- Report wording: uncertainty, permission and proposal words keep their meaning; the wording check runs before a report is written; a report the task records name as presented or approved is never replaced.
- Small route: one ticket with named files and no interface, data, dependency or security change gets one builder and one independent review, and leaves the route when it turns risky.
- Portability: tests build paths from the checkout root instead of assuming a path without spaces.
- Docs and release: root `LICENSE` (MIT). `tools/verification_summary.py` generates VALIDATION's "Current verification" section (commit, tree state, environment, commands, totals); older results moved under a History heading. `tools/validate.py` rejects skill counts and package or rules versions in README, this entry, UPGRADE and VENDORED-SKILLS that differ from the manifests. `tools/build_release.py` builds the ZIP from an explicit include list. Counts corrected: 21 skills, nine vendored, rules 1.8.0.
- Results: VALIDATION.md, section "Current verification". Live host acceptance (ticket T9) is reported separately.

Modular workflow:
- Twelve workflow-axa skills (21 skills with the nine vendored ones below). `/workflow` becomes a router that reads the task's records and selects the next phase. Four new phase skills own the procedure: `workflow-clarify` (journeys, decision check, behavior agreement), `workflow-specify` (vertical tickets, dependencies, test seams, HTML plan), `workflow-execute` (ready-ticket loop, test-first slices, Standards/Spec ticket review, integration and whole-feature review) and `workflow-deliver` (evidence reconciliation and final delivery record). Each enforces its own entry guard and reads the shared policies in the installed `workflow` folder; no policy is copied per skill.
- Two approval gates for substantive work: agreement on behavior and scope (PLAN plus chat), then implementation approval of the specification, tickets, test strategy and HTML report. Agreement never authorizes code. Valid single-gate approvals from earlier versions keep their recorded scope; explicit waivers are recorded as bounded waivers. The lightweight-edit route is retained.
- Status and resumption read both gates. Material changes reopen only the affected agreement items or tickets.
- WRITING.md stays the single human-facing writing policy, with an added meaning-preservation check and reader reconstruction; Matt's `writing-for-agents` governs agent-document structure. No writing dependency is added.
- `workflow-execute` is a local adaptation of Implement Spec's ticket graph without automatic Git, worktree, merge or tracker actions; upstream invocation flags are untouched.
- codebase-map: optional, additive `task_report` object in report schema 2 (request, agreement, specification, tickets, decisions, risks, checks, acceptance results, delivery and completion state), validated and rendered by a sibling `task_report.py` helper with scoped `task-report.css`. Reports without it render as before; existing report assets, graph geometry and security checks are retained. Contract: `skills/codebase-map/TASK-REPORT.md`.
- Validator and metadata register all 21 skills with per-skill word budgets.
- Fixes from independent Codex/Claude review and live evaluations: the router invokes the phase skill and never runs a phase from its table (an evaluation run skipped gate one without this); legacy single-gate tasks are classified before routing; stopped or blocked execution routes to delivery; phase skills read only their sibling `../workflow/` folder; clarification asks only after the affected callers are traced; reviewers are chosen by what changed (Matt `code-review` for code, never a same-named built-in); lightweight edits keep one review; UI tickets apply ui-design VERIFY.md; the routing template and ChatGPT prompts name both gates.
- `task_report`: a complete delivery now also needs every ticket closed, every requirement covered, no open decision and a passed review; agreement may be `legacy`/`not-required`; checks may be `stale`; descoped criteria are `superseded`.
- Vendored specialists: Matt Pocock's `grilling`, `tdd`, `code-review`, `writing-for-agents`, `codebase-design`, `domain-modeling`, `implement-spec` and `retro` are vendored as separate skills at a pinned commit (MIT, `LICENSE` in each folder; provenance and update procedure in VENDORED-SKILLS.md, regenerated by `tools/vendor_specialists.py`). Each keeps the upstream text and ends with a workflow-axa adaptation that replaces the former adapter rules. Phases load their sibling copies, so upstream changes, removals or same-named installs (including a host's built-in `code-review`) no longer change the workflow. `retro` ships `scripts/digest_sessions.py` for large session logs. `simple-english` (AminBlg/SimpleEnglish 2.1.1, MIT) is vendored the same way and is used for every HTML report and delivery message (owner request, 2026-11-03).
- Matt-style rewrite of the router, the four phases and their references (about a third shorter; every gate and safety rule kept and test-guarded). Reports with `task_report` use a reader-first layout: one status sentence, what you're approving, how it works, what changes, one card per ticket, how we'll know it works, risks; technical details collapsed. Legacy reports render unchanged.
- From a retro over 55 real sessions: `workflow/scripts/open_items.py` lists open, blocked and evidence-less ticked items across task folders (used by task-status and deliver); turns end with a Running / Waiting on you / Done line and never while own work runs unattended; handoff messages are generated from the records; ready tickets with disjoint files start in parallel; user-visible changes are never delegated details and agent-made choices are listed at delivery; standing answers are checked before asking; steps needing a person are marked and batched.
- A small change with nothing left open may ask for both gates in one message; only an explicit yes to both records both (owner decision).
- Execute records a baseline run of each ticket's check before changing code and asks before a repair that changes the approved approach or anything user-visible; delivery needs its snapshot or the user's recorded refusal.
- Tooling from the evaluation retro: `workflow/scripts/record.py` (line-ending-safe record edits), renderer errors that name the node/edge and the limit, and `codebase-map/scripts/screenshot_report.py` (screenshots with the installed Edge/Chrome).
- Hardened from live runs: the router invokes the phase skill first and asks only task-identity questions itself; visible changes are never lightweight; the HTML plan report accompanies every plan approval unless the user declines it; independent review via a fresh subagent when available; execution ends with `workflow-deliver`.
- Results: VALIDATION.md, section "Current verification".

## 2.7.0-rc.8 — 2026-11-02

rc.7 content and its strict UI policy are unchanged. This release only adds Windows verification fixes found while validating rc.7 on Windows:
- `check_design_kit.py` and `inspect_kit_index.py` now report a `~` root with no resolvable home as BLOCKED (exit 2) instead of crashing with a traceback.
- The design-kit symlink test now uses the shared link helper: it skips only on the observed missing-privilege error and lets other errors propagate.
- Rules library 1.6.0 is unchanged.

## 2.7.0-rc.7 — 2026-10-30

- Shared rules library 1.6.0. Owner-requested strict application UI reuse: no agent-authored HTML/templates/JSX structure, CSS, inline styles or visual substitutes. Removes ordinary plain-markup/design-authoring fallback permissions while preserving history and logic-only repairs.
- Exact component/pattern selections in the existing HTML screen details; captured image/input fingerprints, variants/states, scope, example and transitive catalogue references validated. Missing provenance cannot create an approval-ready application UI report.
- Code-backed live-kit guide and optional read-only local Storybook v4/v5 index inspector. No app/gallery creation, Storybook installation, background sync, external skill or claimed real project kit.
- Existing non-JSON catalogues can be projected inside report input; no mandatory duplicate inventory. Removed/changed sources block affected reuse and old report captures stay unchanged.
- Raw markup-construction diff cues, negative tests, real browser verification and an explicitly unexecuted live-host scenario suite. Existing report CSS/JS/UI assets, Matt catalogue and previous task history preserved.
- Complete eight-skill replacement; see UPGRADE.md for stricter semantics and legacy report limits. No application/host files changed here.

## 2.7.0-rc.6 — 2026-10-30

- Audited the supplied rc.5 source against rc.4 and reran its package tests. Retained the Windows home handling, strict CRLF diagnosis, byte-preserving manifest writes and owner-approved shared TypeScript rule.
- Optional UI screen flows are rendered inside the existing full editorial HTML report, not a replacement dashboard. Existing report.css/report.js stay byte-identical; non-UI JSON remains compatible.
- Show source-backed static PNG component captures or explicitly authorised labelled schematics, linked screen transitions, control-level design decisions and enlarged evidence/details. No arbitrary app HTML, CSS, scripts, remote URLs or approval callbacks execute.
- Task design source/mode must be established before new substantive UI work; DESIGN.md alone does not choose the source. Explicit task choices and unchanged resumes do not need repetitive questions. Same boundary for ordinary prompts and workflow tasks.
- Installation audits now report unexpected files inside the eight owned skill folders. They do not touch unrelated external skills or delete anything.
- Preserve raw-byte LF integrity while exempting binary assets from Git text conversion. Report manifests now identify this renderer release instead of the stale 2.6.0 label.
- Includes the original historical R2 report unchanged, an additive R2 sample, and a complete synthetic UI-workflow report. Historical deployment/approval claims are not relabelled as current verification.


## 2.7.0-rc.5 — 2026-10-30

- Keep installed rule bytes verifiable on Windows. `.gitattributes` keeps `skills/` and `.claude-plugin/` LF on every checkout, even with `core.autocrlf=true`. The manifest writer writes bytes, so it can no longer emit CRLF.
- Diagnose CRLF-only copies without weakening integrity. `audit_installation.py` lists `line_ending_only` files (the state stays DRIFT). Activation and readiness still refuse, and name the first CRLF-only file. Real edits remain "Mixed/modified".
- Fix Windows home handling in `global_policy.py`, `activate_rules.py` and `audit_installation.py`. Home is resolved only when a selected host still needs a default, and a missing or unexpandable home is a controlled error.
- Document byte-for-byte installation and the two-step check: the package's `--candidate` compares bytes, then the installed copy's `--check-global` verifies the route. Also documented: the shared baseline scope and the unsigned-provenance limit.
- Shared TypeScript rule (rules library 1.4.0): no nested conditional expressions in new or meaningfully changed code; no mandated abstraction.
- Tests: CRLF-only vs hidden-edit, LF manifest, checkout-policy and home-resolution regressions, each with a negative case. Windows junctions exercise directory-link rejection. File-symlink and POSIX-mode checks skip with explicit "unverified here" reasons. Unrelated link errors propagate.

## 2.7.0-rc.4 — 2026-10-30

- Separate requested full rules audits from scoped readiness, including policy/memory conflicts and explicit coverage/loading limits.
- Add read-only comparison of named installations and global references; preserve activation helpers and host permissions.
- Add Angular, Ionic and Capacitor rules/configuration facts, correct React Compiler context and operation/verification boundaries.
- Bundle project design-kit lifecycle, optional catalogue templates and a read-only selection/scope/source-freshness checker. No invented project visuals or new external dependencies.
- Preserve eight skills, Matt integrations, grilling, artifact policy, historical records and the approved flowchart renderer/assets.
- Add tooling regressions and authored live scenarios; see VALIDATION.md for observed results and untested hosts.

## 2.7.0-rc.3 — 2026-10-30

- Add local ui-design as the eighth skill, automatically routed for application UI and ordinary globally guided work.
- Introduce functionality-only default, scoped approved-kit and explicitly authorised design-authoring. No guessed styling via existing classes, utility combinations, props or native/rendered paths.
- Preserve existing appearance, require authorised preview placement for design-pending UI, and distinguish behaviour, design acceptance and release readiness in existing records.
- Keep the local flowchart report exemption narrow; renderer/assets unchanged. No external design dependency or automatic kit/preview creation.
- Add read-only unified-diff triage, mechanical regressions and 32 unexecuted live-host scenarios. The helper does not grant approval or prove styling compliance.
- Shared rules become 1.2.0. Existing activation helpers, Matt catalogue entries, proactive questioning, artifact policy and framework/version tooling are retained.

## 2.7.0-rc.2 — 2026-10-30

- Strengthen shared core semantics; add conditionally loaded data, lifetime, reliability, testing, security, performance and compatibility rules with examples/checks and primary-source leads.
- Add PHP/Laravel and actual-Rust guidance; keep common principles separate from framework/version-specific mechanisms.
- Add read-only static version facts for scoped JS/npm, Composer/Laravel and Unity; report unsupported formats and actual-runtime uncertainty rather than guessing compatibility.
- Fingerprint Composer/Cargo/runtime marker and additional JS lock inputs in readiness. Old assessments must be refreshed; task histories and approval records do not migrate.
- Connect selected engineering/version rules to existing planning, review and doctor routes. Keep the seven skills, Matt integrations, grilling, local viewer and artifact policy.
- Shared library is 1.1.0; requires a complete package update. Global-reference helper is unchanged. No project rewrites, dependency installs/upgrades, automatic updater or host action blocker.
- Candidate status retained: live Claude/Codex behaviour is not established by mechanical tests.

## 2.7.0-rc.1 — 2026-10-29

- Add mandatory rules-readiness before substantive planning/application work, even without prior rule-maker setup. Existing adequate rules are accepted; gaps stop for setup, bounded explicit exception, read-only work or stop.
- Add one local rule-maker with centrally referenced core/framework standards; no per-project rulebook copies and no new external specialist.
- Separate setup, rules readiness, task approval and enforcement. Cover bootstrap, stale/partial/conflicting rules, resumption, scope changes, delegated work, trust and unknown states.
- Add preview/apply/check global reference activation preserving existing instructions and a read-only declared-assessment/freshness checker. No host hooks, silent updates, app rewrites or bulk migrations.
- Retain local flowchart renderer/assets, artifact policy, all Matt entries and historical records. Candidate pending live host/model acceptance; no zero-drift guarantee.


## 2.6.0 — 2026-10-29

- Build from the owner's supplied workflow-axa(1).zip (2.5.0), not an older generated copy. Preserve the six skills, Matt's integrations, proactive grilling, global artifact policy and original flowchart geometry.
- Separate current approval, implementation and verification/owner acceptance. Keep one current checkpoint, short TODOs and detailed evidence in their existing owners; do not repeat live totals or create CURRENT/HANDOFF/revision tracker files.
- Define meaningful plan revisions versus progress, retries and session switches. Add a compact change/reason/authority log in existing records; preserve old identifiers, review/phase aliases and partial supersession.
- Forward-only adoption: new tasks use the clarified structure; authorised resumption reconciles only that task; legacy STATUS.md/inline decisions remain supported. No bulk rewrite, renaming, missing-review reconstruction or automatic deletion.
- Keep presented reviews immutable. Add optional sourced checkpoint/revision/outcome fields to schema 2, and a requested task-overview presentation that does not ask for or grant approval. Old schema-2 inputs remain valid and old HTML freshness checks remain available.
- Retain the uploaded DIAGRAM-DESIGN.md filename as a compatibility pointer to the local guide; its stale external-install instructions are superseded.
- Add projection/security/compatibility tests and synthetic legacy-history evaluation cases. Live agent adherence is not inferred from tooling tests.

## 2.5.0 — 2026-10-26

- Add one shared ARTIFACTS.md policy: stable task parents, concurrency-safe child runs, required evidence, reuse of tools and narrowly authorized own-scratch cleanup. No legacy sweep or automatic producer changes.
- Add preview/apply/check global setup for Claude/Codex, preserving existing user instructions, CRLF/BOM and Codex override handling. One deployed policy copy is verified against the packaged source.
- Route all six local skills and delegated workers through the same boundaries; preserve grilling, approval, Matt's routes and local flowchart design.
- Define durable review destinations separately from ignored test output; keep approved reviews and reference images.
- Add setup safety tests and evaluator-only artifact scenarios. Host obedience and project script retention remain explicitly unverified.

## 2.4.0 — workflow utilities and anti-slop review

- Added local `task-status`, `resume-task`, `workflow-doctor` and `plan-review` skills.
- Added `codebase-map explain` for no-assumed-context current-flow explanations.
- Strengthened domain-modeling use before inventing terminology or ownership.
- Added an explicit necessity check for new abstractions/fallbacks/config layers and reinforced the cold-reader check.
- Kept Matt Pocock specialist integrations and the bundled local flowchart unchanged as dependencies.

## 2.3.0 — 2026-10-16

- Proactive grilling for new substantive intent and material scope changes, with sourced decision coverage, partial-answer protection and no repeated interview for unchanged approved work.
- Resolve current/named/related/completed tasks before folder creation; reuse stable records through revisions and ask on ambiguous identity/ownership.
- Plain-language-first questions, plans, HTML and reviews; concrete code/document/report quality examples and cold-reader checks.
- Read-only controlled screenshot capture/comparison and regression cases; preserve the approved local flowchart assets and renderer behavior.
- Evaluator-only behavioral cases and safe task-discovery fixtures for comparing real Claude/Codex sessions against 2.2.1. Live runs are not claimed.
- Optional skill-creator/webapp-testing compatibility notes, not new dependencies; all Matt catalogue entries retained.



## 2.2.1 — local flowchart dependency correction

- Keep Matt Pocock's research, diagnosing-bugs, TDD, code-review, grilling and all other established entries/routes/adapters unchanged. Do not replace their methods with local summaries.
- Move the approved flowchart contract into codebase-map/FLOWCHART-DESIGN.md. Use the bundled renderer/assets directly; no separate diagram-design installation, lookup or invocation.
- Remove only the external diagram-design catalogue entry and visual adapter. Update setup, routing, audit and regression scenarios; retain historical design attribution.
- Preserve schema 2, example source, rendered geometry, editorial CSS/JS and the stop for explicit approval. Bump only the renderer's tool-version metadata.
- Add regression coverage for local guide completeness, Matt-only inventories, old-baseline rejection and standalone no-dependency rendering. Actual checks and host limits are recorded in VALIDATION.md.

## 2.2.0 — flowchart-first editorial reviews (2026-10-14)

- Replace the fixed-height generic component grid with explicit, typed flowchart geometry and the approved editorial style. The feature flow opens first; current comparison, delivery dependencies and structure are separate where useful.
- Add explicit Cathryn Lavery diagram-design routing, provider-aware inventory, dependency/setup instructions and the preapproved offline/system-font design brief. All 27 Matt catalogue entries and grilling are retained.
- Introduce schema 2 for explicit nodes/routes/views and aligned change summaries. Reject overlaps, unsafe connectors/masks, repeated ports and unlabelled decision branches. Preserve existing HTML source-manifest checks; old JSON regeneration requires documented migration.
- Native view/zoom controls and scrolling work without JavaScript; optional script enhances evidence navigation and mouse drag. Source records, requirements, exclusions, acceptance, visible uncertainties and approval authority remain intact.
- Replace old renderer/assets/examples rather than keeping a silent generic-grid fallback. Add regression/browser scenarios and documented validation limits. No upstream installation, application work, Git publication or live-agent pass is implied.


Historical entries describe previous behavior; current instructions live in skills/workflow. Package version labels do not imply a published Git tag or successful live host evaluation.

## 2.1.0 — 2026-10-13

- Ground repository-specific proposals and explanations in inspected current code, with requirement/evidence/gap/task/acceptance mapping and scope limits.
- Add the automatic substantive-work visual approval gate after PLAN/TODO preparation; keep grilling for unresolved decisions, not implementation authorization.
- Add independently callable codebase-map for current/proposed/compare views. Original offline HTML/SVG renderer, editable JSON, safe text handling, pan/zoom/fit, evidence/task links and supplied-source drift checks; no Miro account or CDN.
- Add a reviewed project-routing template and fresh-session implicit-invocation setup tests. Template files do not configure a user's project automatically.
- Register/install two local skills; retain Matt's 27-entry historical inventory, 11 explicit specialist routes and no automatic installs or Git actions.
- Extend recovery, approval provenance, auditing, negative test fixtures and browser/package validation. Live Claude/Codex model behavior is not asserted by tooling tests.

## 2.0.0 — 2026-10-09

User-requested package release; not published, installed or live host-certified here.

### Added

- Explicit routes to 11 of Matt Pocock's reusable specialist skills, with `grilling` for structured questions rather than optional interview assistance.
- Full 27-skill installation catalogue, one-route-per-host setup guidance, host/source/availability checks and recorded invocation evidence.
- Portable read-only checker for selected/full inventories, duplicate copies, invocation policy, known supporting files and approved local content baselines.
- Compatibility adapters for question timing, existing approval, subagent absence, existing docs, uncommitted review, prototype cleanup and no automatic commits/publication.
- Specialist tooling regression tests and seven new staged behavioral scenarios (22 main scenarios total).

### Changed

- Workflow, questions, records, audit, prompt examples and README consistently require the applicable installed specialist rather than silently recreating it.
- Missing/disabled/ambiguous/changed selected skills block dependent work or use a previously approved explicit fallback; unrelated work may continue.
- Reuse approved test seams and task scope across specialist calls; host changes recheck capability without reopening settled product approval.
- The synthetic approved fixture explicitly records test seams for the TDD integration exercise.

### Boundaries

- One user-facing workflow, no vendored upstream skill stack, automatic installations, invented native dependency keys or commits/pushes.
- `grill-me` and other user-only upstream workflows stay user-invoked. Installation and a successful disk check are not evidence of runtime invocation.
- Upstream 1.3.1 metadata was observed; no source commit, upstream byte hash or live-tested team baseline is fabricated. See VALIDATION.md.

## 2.0.0-rc.1 — 2026-10-09

Local-test candidate; not a published release. Live Claude Code/Codex behavior remains to be evaluated.

### Changed

- One shorter core workflow with conditional references; no mandatory external grilling or subagents.
- Discover facts independently, batch nonblocking questions, and interrupt only at a meaningful decision boundary.
- Persist approval revision/scope and delegate ordinary execution without repeated micro-approvals; scope expansions and reserved decisions still need the user.
- Create task records before substantial discovery or implementation. Add lightweight records, before/after checkpoints, ownership, worktree reconciliation and cold recovery.
- Audit the task-attributable final state without automatic staging. Preserve unrelated staged/unstaged edits; Git publication actions remain separately authorized.
- Classify regression, task-caused, baseline and environment failures; retain final-state verification after the last repair and honest partial reporting.
- Make abstraction/comment standards and directly superseded-code cleanup concrete, without banning helper names or deleting unrelated code.
- Retain optional reader-focused PDFs, with reuse of applicable owner-approved language and honest reviewer limitations.
- Align README, prompt examples, plugin descriptions and Codex metadata with these defaults.

### Added

- Standard-library structural validation, safe disposable fixtures and tooling tests; behavioral scenario guide for local baseline/candidate comparison.
- Candidate verification report and source/design notes. No automatic CI, service, installation, staging, commit, push or release action.

## 1.3.0 — 2026-09-24

The relay said what was done and what remained, but not what was learned, and nothing kept the project's own docs honest. Tests could pass beside an architecture doc that still described the old system.

### Added

- **Documentation is part of the implementation.** A change to architecture, ownership, dependencies, data flow, user flow, build flow, or runtime behaviour updates the project's existing docs in the same task, before its item is ticked. Stale text is corrected or deleted, not duplicated.
- **Recon finds the docs and the reach.** Two new recon questions: what the change touches beyond the edited files, and which docs describe the area today.
- **A task folder replaces the single task document**, and moves from `docs/superpowers/plans/` to `docs/plans/YYYY-MM-DD-<slug>/`. `PLAN.md`, `TODO.md`, `FINDINGS.md`, and `DECISIONS.md` (created on the first decision; ADRs in `docs/adr/` for hard-to-reverse architecture calls).
- **TODO states with proof.** `[ ]`, `[~]` (one per running lane: where the last agent stopped), and `[x]` only with its proof seen.
- **Maximum parallel delegation.** The orchestrator delegates every TODO item and fans out to the harness's concurrency limit. Items are grouped into lanes with non-overlapping files; lanes run at once, each as implementer → test writer, and the verifier runs once over the full diff when all lanes are done. Running subagents are never interrupted: cross-lane effects become findings and queued follow-ups.
- **A seventh audit check.** Docs that no longer match the code, and whether the diff delivers the goal in `PLAN.md`. The verifier checks docs too.

### Changed

- **SKILL.md is roughly half its old length.** Formats moved to `TASK-FOLDER.md`, the audit checks to `AUDIT.md` (now the single copy; `CHATGPT-PROMPTS.md` points to it). Tests folded into the implement step, so there are seven steps instead of eight.
- **An existing task folder is continued**, not duplicated. Recon looks for one before planning.

### Fixed

- **Parallel workflows no longer write to each other's task folders.** With several workflows running in one repo, the agent sometimes guessed which folder or changelog to update. It now claims one folder in batch 1 (`Task folder: <path>`) on evidence only: the user named it, or its `PLAN.md` goal is this exact work. Recency, a similar name, or an in-progress `[~]` item do not count. When unsure it asks. Other task folders are read-only, and shared files like `CHANGELOG.md` are written only when the plan names them.
- **Findings are written as they happen**, not at the end; audit findings go to `FINDINGS.md` and become `TODO.md` items.
- The `⚠️ untested` line moves from the changelog to `FINDINGS.md`.

## 1.2.0 — 2026-09-18

1.1.0 stopped the agent from implementing before its questions were answered, but let the questions leak out one at a time, mid-flight, while subagents were still reporting. And it asked them before reading any code, which made them unanswerable.

### Added

- **An investigation step.** The flow now reads the codebase before it plans: parallel recon subagents map what exists, every call site, what the tests cover, and what constrains the change. This step was in the original team flow document — *"bestaande implementaties en relevante code controleren"* — and was missing from 1.0.0 and 1.1.0. Its absence is why the plan's questions were uninformed.
- **Two batches, and nothing in between.** The user is interrupted exactly twice: once after investigation with the plan and every question, once at the end with the report and anything that came up. Each batch is one numbered message with a recommendation per item, and it ends the agent's turn.
- **A parallelism rule.** Subagents run in parallel when they only read or touch different files, sequentially when one needs another's output or they would write the same file. Recon fans out; implementer → test writer → verifier does not.

### Fixed

- **No question is asked while a subagent is running.** Every dispatched agent finishes first. A question arriving beside a half-finished recon report was the reported mess.
- **Questions found mid-work park instead of interrupting.** Work continues on everything that does not depend on the answer; the agent stops early only when nothing else can move.
- **The document choice and the go are one round.** They were two separate asks inside a single step, which cost two round-trips.
- **Test decisions park for batch 2** rather than firing their own interruption.

## 1.1.0 — 2026-09-18

The 1.0.0 skill would start implementing before its questions were answered. It no longer can.

### Added

- **Checkpoints.** Four moments now belong to the human, named in a table near the top and marked 🛑 at each site: the goal is settled, the plan is approved, the document is chosen, and a test decision is made. Each one ends the agent's turn. `Done when:` measures the agent's work; a checkpoint measures the user's answer, and only their words clear it.
- **A plan, and a go gate before any code.** The document's Open list is the plan. The agent drafts it, shows it, and stops. Nothing outside the document is written until the user says go.
- **Repo pinning.** The agent states which repository it is working in before anything else, and treats every other directory its session can reach as out of scope. Sessions configured with additional working directories were sending recon into unrelated products.

### Fixed

- **Grilling no longer runs half-way.** The interview must finish and be confirmed before implementation; its outcome then becomes the prepared prompt. The old "return here with what it settles" assumed a frame that was long gone by the time the interview ended.
- **Subagents are strictly sequential.** The previous "run independent ones together" could dispatch the implementer and test writer onto the same files at once.
- **The audit is scoped to this task.** It sees only the diff for the files this task changed, leaves anything already staged alone, and treats pre-existing code as out of scope unless asked.
- **The audit runs twice.** A fix made in response to a finding was the one change in the flow that nothing checked. Capped at a second pass.
- **A real finding promotes a trivial task out of trivial.** A second call site was never a one-file change; the task restarts properly with a document.
- **Writing a missing `AGENTS.md` is an offer, not a detour.** It was an unbounded side-quest the agent took alone.
- **Every subagent's inputs are specified.** Previously only the implementer's were.
- **The `⚠️ untested` line has somewhere to go on a trivial task** — the final report, since there is no document.

## 1.0.0 — 2026-09-18

First release.

### Added

- **`workflow` skill** — the team development flow, end to end:
  - Classifies incoming work into three doors: a prepared prompt, a bare goal (handed to `grill-me`), or a trivial change that skips the flow but still gets audited.
  - Reads the project's `AGENTS.md` / `CLAUDE.md` before touching anything, and writes one when neither exists.
  - Keeps a handover document at `docs/superpowers/plans/YYYY-MM-DD-<slug>.md` with open items and a changelog, updated during the work rather than at the end.
  - Runs every task through three subagents: implementer, test writer, verifier.
  - Never skips tests. When tests can't run, asks — and records a `⚠️ untested` line in the changelog when the answer is to proceed without them.
  - Audits the staged changes in a **fresh subagent** that sees only the diff and the repo, never the implementation conversation.
  - Stages and stops. Commits stay with the human.
- **`CHATGPT-PROMPTS.md`** — what to ask for when preparing a task prompt or an audit prompt outside the agent.
- **`agents/openai.yaml`** — display metadata for Codex.
- **Claude Code plugin manifests** — the repo installs either via `npx skills` or as a Claude Code plugin.

### Notes

The triviality bar is deliberately strict: one file, no logic or control-flow change, no new behaviour, no new dependency. Anything else takes the full flow.
