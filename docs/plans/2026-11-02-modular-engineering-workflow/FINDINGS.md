# Research and verification

## E1 — Baseline and preservation

Repository inspection on 2026-11-02 found eight local skills, source version 2.7.0-rc.7, Markdown task records, a standard-library HTML/SVG report renderer, offline assets, package tests and separate live-agent scenario definitions. `git status --short` showed only the three existing audit record edits named in PLAN. Source inspection is not runtime validation.

Sources: README.md; docs/DESIGN.md; skills/workflow/SKILL.md, QUESTIONS.md, GROUNDING.md, WRITING.md, SPECIALISTS.md, TASK-FOLDER.md; skills/codebase-map/SKILL.md and REPORT.md; tests/README.md.

## E2 — Existing clarification and communication

QUESTIONS already requires a bounded decision tree, current-code investigation, stable IDs, sourced answers, follow-ups and no question quota. GROUNDING already maps requirements to evidence, acceptance and work. WRITING already uses plain language, consistent terms, preserved technical evidence and a cold-reader check. Improve execution and coverage rather than adding duplicate rules.

## E3 — Upstream integration boundary

Current public `implement-spec` is user-invoked and assumes a tracker, an integration branch, fresh ticket worktrees, TDD, merging and possible PR/closure actions. SPECIALISTS currently lists it as a competing manual workflow. The user now explicitly requests studying and adapting it, which authorizes a proposal, not silent automatic Git/tracker actions or alteration of installed upstream copies.

Public sources read: https://raw.githubusercontent.com/mattpocock/skills/main/skills/engineering/implement-spec/SKILL.md ; adjacent code-review and tdd; productivity/grilling. Version/provenance comparison is pending.

## Verification

No implementation, baseline suite, browser regression, live behavior evaluation or installation was run for this task. Historical test totals are not current proof.

## E4 — Structural pressure and reuse opportunities

Measured source sizes (bytes, not quality scores): render_report.py 56,063; screen_flow.py 25,806; TASK-FOLDER.md 20,708; SETUP.md 17,665; REPORT.md 15,803; SPECIALISTS.md 14,273. The renderer already separates UI screen flow and kit binding into helpers. Its main file still mixes validation, graph geometry, source fingerprinting and HTML composition. Extract only a coherent report-content responsibility if the requested expansion needs it; size alone does not justify rewriting geometry/security code.

Existing reusable entrypoints: workflow, codebase-map, task-status, resume-task, workflow-doctor, plan-review, rule-maker, ui-design. The latter seven should retain their independent roles. Workflow reference files contain stage procedures but are not independently invocable skills. Repeated readiness/artifact/UI paragraphs across entrypoints mix legitimate entry guards with duplicated policy; keep short guards pointing to a single policy owner.

`tools/validate.py` hardcodes the eight registered skills and required legacy reference paths. New registrations and compatibility pointers must update this deliberately, rather than deleting tests to achieve a pass. `tests/README.md` names rc.3 as a comparison baseline while `tests/behavioral/README.md` still names 2.5/2.6 and six local skills. These are observed maintenance gaps; a new comparison must pin the actual pre-refactor rc.7 revision and controlled runtime.

## E5 — HTML content gap

The renderer's `render()` already projects requirement/evidence/task/acceptance relations, dependencies, checkpoints, revision history and task outcomes. `validate_record_context()` distinguishes approval, implementation and verification. `REPORT.md` protects immutable snapshots and old schema-2 inputs. The requested central report should extend these structures rather than introduce a task database or competing page generator.

Missing first-class readable content includes the full request/agreement, categorized assumptions and decisions, per-ticket implementation specifications, review findings, test outcomes and a final delivery record. Today much of the information is behind one technical appendix and some exists only in Markdown. A sourced optional report-content section can fill this gap with visible navigation while preserving flow geometry and the editorial shell. HTML is an as-of projection, never an approval authority or live status oracle.

## E6 — Independent Codex writing evaluation (before receiving Claude's findings)

Method: discover on skills.sh; read actual GitHub SKILL.md at the repository commit; inspect up to three file-history entries. No candidate was installed or executed. Recent commits show maintenance activity, not quality or a support promise. Directory popularity/audit badges were not selection criteria.

| Candidate | Observed revision / last skill edit | Useful behavior | Compatibility and recommendation |
|---|---|---|---|
| [Obra writing-clearly-and-concisely](https://skills.sh/obra/the-elements-of-style/writing-clearly-and-concisely) | `05fc4f0d2b97b7c042dd9949ad658568e4a1324e`; skill edit 2025-10-18 | Concrete language, active voice, deletion of redundant text | Broad trigger, approximately 12,000-token supporting book, optional copyediting delegation. Overlaps WRITING; do not add as mandatory dependency. |
| [ofweb concise-prose](https://skills.sh/ofweb/skills/concise-prose) | `dba47c9c7f4281347de1c97ea8be6e5bc3882b77`; skill edit 2026-10-01 | Preserves meaning, exact identifiers, project terminology; no fixed sentence cap | Mandatory `prose-check`/Vale adds tool/config dependency. Useful principles, but adoption unchanged is unnecessary. |
| [OpenHands plain-english-content](https://skills.sh/openhands/extensions/plain-english-content) | `21c88f56f02c7ebd4c3cac6ad3b7895290637348`; skill edit 2026-06-29 | Reader need first, concrete consequences, accessibility without losing detail | Short-sentence targets and rigid emphasis/date/word rules can conflict with established reports and technical terminology. Use as comparative evidence, not wholesale policy. MIT declared. |
| [Metabase docs-write](https://skills.sh/metabase/metabase/docs-write) | `a0a3d03f817278b42edfb78ae05aaca0dadcefd1`; skill edit 2026-02-10 | Audience-aware drafting, actionable headings, working examples and descriptive links | Imports a project-specific style guide and runs Bun/Prettier. Product substitutions can change domain meaning. Do not add to this Python/Markdown package. |

Primary instruction paths at the listed commits: Obra `skills/writing-clearly-and-concisely/SKILL.md`; ofweb `concise-prose/SKILL.md`; OpenHands `skills/plain-english-content/SKILL.md`; Metabase `.claude/skills/docs-write/SKILL.md`. skills.sh served some indexed text while direct page opens failed; actual instruction reads used GitHub, not search snippets. Supporting book, Vale config and Metabase style-guide dependency are not fully evaluated for adoption because the entrypoint already establishes the incompatible mandatory dependencies; no claim of full dependency audit.

Independent recommendation: retain Matt's existing writing-for-agents for agent-document structure and improve workflow WRITING.md as the single human-facing writing policy. Add a concrete meaning-preservation check (actor, condition, obligation, result, exception, evidence) and a cold-reader reconstruction test. No new writing runtime dependency. This is a recommendation pending Claude's independent result and user approval, not agreement.

## E7 — Matt upstream provenance and adaptation

GitHub tree observed at `4ae2317ddb22b046e26455e4f9c9b3aaaf62212d` on 2026-11-02. File history: grilling and code-review last changed 2026-10-29 (`7739eaed…`, fresh-context guidance); implement-spec 2026-10-29 (`a496f551…`, fresh implementer per ticket); TDD 2026-10-07 (`3f599139…`, seam coverage tradeoffs). Current catalogue's 2026-10-09 main/version note is historical provenance, not a pinned guarantee of these current files or installed host behavior.

- Grilling: keep decision dependencies, sourced answers and follow-ups. Add evidence-derived journeys and an adversarial missing-case pass. Empty question frontier alone is insufficient if the agent failed to discover a branch. Stop when relevant journeys have observable outcomes and all material unknowns are resolved/deferred out of scope by authority; no universal completeness guarantee or question quota.
- Implement Spec: reuse dependency graph, ready-ticket selection, fresh bounded contexts where supported, integration checks and final review. Propose a separately named local execution skill with explicit adaptations. Do not remove upstream user-only flags or silently enable tracker/Git actions. Sequential execution is a supported fallback, not a claim that parallel delegation occurred.
- Code Review: keep Standards and Spec axes and evidence. Existing C adapter already fixes committed-only diff and tracker assumptions; retain initial user-edit attribution. Severity/actionability may be reported per axis without merging them or requiring every heuristic to become a refactor.
- TDD: keep agreed public seams, independent expected outcomes, observed red then green, and one vertical slice. Review/refactor is a distinct step. Existing T adapter reuses approved seams. Documentation edits need meaningful contract/behavior checks rather than fake red/green claims.

## Independent architecture hypothesis (not approved)

Prefer four focused phase entrypoints over one skill per numbered workflow stage: clarify (grounding plus grilling and agreement), specify (implementation specifications and dependent tickets), execute (approved ticket cycle using existing implementation/TDD/review specialists), deliver (whole-feature acceptance and final evidence-backed record). Preserve the eight existing entrypoints and shared policy owners. `/workflow` routes by current state and prerequisite evidence; independent entrypoints enforce the same entry guards without calling the entire workflow recursively. Names and final cut remain subject to independent challenge.

Keep PLAN/TODO/FINDINGS/DECISIONS authoritative. Stable R/A/T/E IDs connect requirements, acceptance, ticket work and evidence; add stable journey/question IDs only where needed. Avoid another mandatory agreement/spec/delivery database or empty template files. The user is being asked whether agreement and implementation planning have two distinct approvals.

## E8 — Independent Claude review and Codex challenge

Claude Opus 5.5 completed an independent research run, 2026-11-02. Review session: <t3-thread://v2/a13a5f85-59c9-4e5e-a03d-c9389a2f2556/thread:delegated-task:command%3Amcp%3A7e5e65d6-a034-4adf-b634-94dfa6af500f%3Adelegate-task%3A455d6377-8720-48c7-a86e-2cea08e7d576>.

Its recommendation also keeps WRITING.md plus writing-for-agents and adapts Implement Spec ideas locally. Its independently selected comparison sources include Anthropic doc-coauthoring (reader reconstruction), Vercel writing-guidelines (runtime remote rule fetch), Addy Osmani documentation-and-adrs (overlapping ADR conventions), GitHub documentation-writer (generic documentation categorization) and mgifford plain-language (broad public-content policy). These are reviewer findings, not a claim Codex independently read all those dependencies.

Useful findings accepted for the proposal: acceptance results need explicit evidence links in the final HTML; a same-named built-in reviewer must not masquerade as Matt's provider; old installed skills differ from source; deduplication must retain effective entry guards and live regression coverage; test seams need explicit approval within the detailed plan.

Reported host observations need bounded interpretation: Claude saw no installed Matt code-review and saw a competing Superpowers hook in its own session. This does not prove every host silently uses the wrong skill. The existing specialist checker only inspects files; it cannot authenticate live host resolution. Runtime inventory and actual invocation must remain distinct. Preserve legacy CONTEXT/GLOSSARY conventions through explicit source resolution rather than requiring a global rename. No host repairs are authorized by these findings.

Claude disclosed an accidental empty `/tmp/x` scratch write during public-source fetching and immediate removal. No repository/config/skill edits were reported. This deviated from its read-only brief; subsequent review must use stdout/in-memory fetches only. No test result is inferred.

### Objections sent for resolution

1. Reference files alone do not meet the explicit request for smaller independently reusable skills. Prefer four independently useful phase skills (clarify/specify/execute/deliver), each owning real procedure and using shared guard contracts. Keep the existing skills; do not create eleven thin wrappers.
2. The user has now explicitly selected two approvals (DECISIONS D3). A combined agreement/implementation approval is no longer a valid recommendation. Agreement comes before detailed planning; the HTML plan gate follows it.
3. A journey is a user/actor outcome, not necessarily one row per code entrypoint. Multiple callers can share a journey. New requested behavior may intentionally differ from existing code: unexplained conflicts block, intended differences are the purpose of the change.
4. Reject a universal three-round interview cap or two-cycle repair limit as a quality/completeness proxy. Escalate when material user choice, no-progress evidence, capability or approved budget requires it. A bounded experiment may have explicit limits. Ground questions in evidence or requested behavior; keep technical IDs in records rather than making users decipher them.
5. One ticket can contain several red/green slices or be documentation-only. Preserve meaningful ticket-level review and integration checks plus final whole-feature review. One final review/one repair pass does not satisfy the requested iterative cycle.
6. Acceptance results alone do not meet the requested central report content. Surface agreement, specification/tickets, risks, decisions, review/test results and delivery as sourced optional content in the existing renderer. Do not duplicate hand-maintained data. Unknown keys in newly introduced fields should fail or produce explicit diagnostics; blanket rejection of all legacy extra keys risks compatibility and needs separate evidence.
7. Source pinning and isolated candidate sessions should allow evaluation without replacing the globally installed rc.4 or reopening the pending installation task. Fail to NOT VERIFIED if the host cannot actually load the exact source; do not assume a global reinstall is necessary.
8. Independently evaluate the same four writing candidates in E6 before claiming shared candidate selection. Retain reader tests and meaning preservation; avoid mandatory question counts, grammar quotas or adoption of candidate code/text without its license conditions.

Agreement remains pending reconciliation; no objections have been hidden by a consensus label.

## E9 — Parent checks on reviewer observations

The coordinating session independently listed the known active `C:/Users/Cem/.agents/skills` directories: grilling, tdd, writing-for-agents and domain-modeling are present; code-review and implement-spec are absent in that root. The active skill catalogue supplied to Codex likewise does not expose Matt code-review. This establishes a relevant capability gap, not exhaustive absence from every cache or host. Installed domain-modeling explicitly uses CONTEXT.md and docs/adr. The source catalogue's different required glossary support file needs version-compatible setup handling; no rename or update has been made.

At upstream commit `4ae2317ddb22b046e26455e4f9c9b3aaaf62212d`, the parent also read TDD's tests.md and mocking.md and re-read pinned grilling/implement-spec. They support public-interface behavior checks and boundary mocks. No local test is claimed by reading these examples.

The current source UI CONTRACT and rules/design.md were read directly: no invented application presentation or plain-markup fallback; approved report maintenance is distinct from application design. `render_report.py` validation/render paths were inspected: dependency cycles and unmapped work already fail; acceptance definitions currently lack structured execution results; unknown optional fields are not rendered. Both the compatibility risk and missing-content risk are real and should be handled in the plan.

`git rev-parse HEAD` still returned the recorded baseline. Status shows only the original three audit modifications and this new task directory. No package implementation files changed.

## E10 — Reconciled recommendation and remaining plan conditions

Second independent Claude Opus 5.5 review: <t3-thread://v2/a13a5f85-59c9-4e5e-a03d-c9389a2f2556/thread:delegated-task:command%3Amcp%3A7e5e65d6-a034-4adf-b634-94dfa6af500f%3Adelegate-task%3A2c39038c-4343-480b-aec3-4490fe955d2f>. Completed 2026-11-02, with no reported writes/tests/installs. It independently fetched all four E6 candidates at the listed commits.

All eight E8 objections were accepted with reasons. Claude withdrew the reference-only architecture, combined gate, per-ticket single-test assumption, final-review-only cycle and fixed interview/repair limits. The resulting direction is four procedure-owning phase skills plus the retained existing skills; two distinct approvals; actor journeys mapped to relevant callers; completion/no-progress conditions rather than quotas; per-ticket review/integration checks plus whole-feature review; sourced optional report content with legacy compatibility; isolated evaluations with actual loaded-version evidence; and improved existing writing guidance without a new dependency.

The writing choice is shared: WRITING.md owns human-facing prose; writing-for-agents owns agent-document structure. Add meaning preservation and reader reconstruction. Neither reviewer recommends installing any of the four candidates. No candidate source text or runtime tool is adopted by this research.

Four review conditions are carried into the agreement/next plan:

1. Preserve proportionality: two gates for substantive work, the existing genuinely lightweight route retained. Small behavioral changes are not automatically exempt. This is an explicit proposed term for the user's gate-one approval, not silently approved policy.
2. Gate one uses PLAN plus chat; HTML is required for gate two. This follows the selected stage order and is explicitly presented to the user.
3. Persist separate agreement and implementation-plan authority through status/resume/report flows. Existing single-gate wording must be replaced consistently in the approved implementation; valid legacy authority is reconciled forward rather than revoked.
4. Detailed planning must prove the delivery skill's independent responsibility, choose precise policy/file ownership and preserve package/link contracts. New skill names must avoid collisions. Validator registration, per-skill metadata, reference checks and maintenance budgets must be updated deliberately. Preserve existing standalone report-skill packaging.

The parent independently inspected validator lines 138–184 confirming fixed registrations, budgets, metadata and cross-folder link rules. The reviewer reported workflow at 1,236 words against a 1,250-word budget; this is its static measurement, not a test pass. It supports moving procedure out, but smaller files alone do not demonstrate better behavior.

No substantive disagreement remains about the direction. Exact file/schema decisions, live-evaluation setup/budget and proof of the final module cut belong in the next detailed plan, after user agreement. No implementation or host behavior has been verified.

## E11 — Takeover state and package checks (Claude session, 2026-11-02 13:10–13:40)

Observed on arrival: T2–T4 files present (12:10–12:25), PLAN still said "Implementation: not started", no handoff. `tools/validate.py` failed (codebase-map 868/850 words) and the suite had 7 failures (560 run): five candidate-version assertions (behavioral manifests and `RENDERER_VERSION` still 2.7.0-rc.8 while plugin.json said 2.8.0-rc.1) and `test_eighth_local_skill_registered_once` expecting 8 skills. These were incomplete integration, not behavior regressions.

Repairs: shortened two codebase-map SKILL.md sentences (meaning kept, TASK-REPORT.md pointer kept); set the five manifests and `RENDERER_VERSION` to 2.8.0-rc.1; renamed the skill-count test to `test_ui_design_registered_once_among_twelve` and changed 8→12 (the ui-design-once assertion is unchanged).

**V1** — `python -X utf8 tools/validate.py`: PASS (twelve skills, 684 workflow words). `python -X utf8 -m unittest discover -s tests -p "test_*.py"`: 560 run, OK, 11 skipped. Every skip is a host limit (no file-symlink privilege, no FIFO, no POSIX mode bits), so symlink/FIFO rejection paths stay unverified on this Windows host. Log: `.artifacts/2026-11-02-modular-engineering-workflow/candidate-unittest.log`. Package/tooling proof only; not agent behavior.

## E12 — Behavior evaluations, first turns (headless `claude -p`, Opus 5.5, 2026-11-02)

Transcripts: `~/.claude/projects/D--Altinstar-wfaxa-eval/`, `D--Altinstar-wfaxa-eval-base/`, `D--Cheflabels-labeler-V2-wfaxa-eval/`; result JSON in `.artifacts/2026-11-02-modular-engineering-workflow/eval/`. Each scenario is one run, not a statistical sample.

| Run | Package | Cost / turns | Observed |
|---|---|---|---|
| E2-t1 Altinstar compact winner amounts | installed rc.8 (no plugin) | $1.97 / 8 | Correct owners (DashboardGameWinners, LastWinners), noticed "balances" are not in these lists, 6 grounded questions with recommendations, stopped before code. Did not raise OkeyPlaza cents/BTC. |
| E1-t1 same prompt | candidate `--plugin-dir` | $2.14 / 10 | Same owners with line numbers, 129 `renderMonetaryValue` call sites kept unchanged, cents/BTC in the test plan, both brands' builds, tooltip flagged as needing kit authority; stopped at gate one. Read candidate `D:/workflow-axa/skills/workflow/RULES.md`/TASK-FOLDER.md (via `cat \| head -150`, truncating TASK-FOLDER). **Defect: never invoked `workflow-clarify`**; ran clarification from the router summary; no journeys in FINDINGS. |
| E3-t1 Cheflabels expired-label warning | candidate | $1.92 / 9 | Invoked `workflow-axa:workflow-clarify`. Found the request's premise false (products/recipes have no expiry; labels compute today+shelf life; real expiry is on stock rows with backend `expiry_status`), listed four print entry points, raised offline fetch and the separate translations repo. **Deviation: skipped `grilling`** and disclosed it. |

Repairs from these observations: `workflow/SKILL.md` §2 now says to invoke the phase with the skill tool (plugin name `workflow-axa:<name>`) or read its SKILL.md in full, and that the table holds no procedure. `workflow-clarify` step 2 now says asking without `grilling` skips the decision check. A fresh E1 first turn must confirm the router fix.

## E13 — Independent reviews R1 and repairs

Both reviewers got the same brief (code plus PLAN R1–R10, not the coordinator's conclusions), read-only. Codex: `codex exec -s read-only` (codex-cli 0.166.0), output `.artifacts/2026-11-02-modular-engineering-workflow/review-codex-r1.md`. Claude: fresh-context Opus 5.5 subagent. The Claude reviewer wrote two scratch logs in the session scratchpad, contrary to its brief; nothing in the repository.

| # | Finding (raised by) | Disposition |
|---|---|---|
| 1 | "complete" delivery accepted blocked/unplanned tickets, uncovered requirements, open decisions, no review (both) | Fixed in task_report.py; red→green tests `test_complete_delivery_rejects_unreconciled_records` (5 cases, each also renders as partial) |
| 2 | Legacy/lightweight agreement not representable; router sends legacy tasks to clarify (Claude) | Agreement statuses `legacy`/`not-required` (cite record, no invented response); router classifies legacy first. Test `test_legacy_agreement_is_reported_without_inventing_one` |
| 3 | First-match routing loops stopped work back to execute (both) | Delivery row now precedes execute and matches handed-off/stopped/blocked/limited. Test `test_router_invokes_phases_instead_of_running_them` |
| 4 | Phase skills cannot verify the shared folder's version (both) | Anchored to sibling `../workflow/`, never another skills root; unverifiable version claim removed. Test `test_phase_skills_resolve_their_sibling_workflow_folder` |
| 5 | Single-gate text in PROJECT-ROUTING template and CHATGPT-PROMPTS (both) | Both now name agreement then implementation approval; UPGRADE tells the owner to review the merged block. codebase-map:42, KIT.md:34, DESIGN.md:139 checked: they describe the still-valid gate-two approval; unchanged |
| 6 | Three verdict vocabularies; no stale state (Claude) | Deliver verdict table now carries report values incl. Failed; check `stale`; result `superseded` (no checks). TASK-REPORT.md aligned. Tests for stale and superseded |
| 7 | Docs-only work forced through code-review; same-name built-in ambiguity (both) | Execute selects reviewer by AUDIT.md (code → Matt `code-review` with C adapter, never a same-named built-in; docs/skills → writing-for-agents + AUDIT) |
| 8 | Lightweight route lost review (Claude) | Router lightweight route reviews per AUDIT; deliver short form expects one review |
| 9 | Delivery snapshot trigger contradicts "only when requested" (Claude) | VISUAL-REVIEW and TASK-REPORT name delivery as a permitted trigger |
| 10 | UI verification missing from execute (Claude) | Execute step 5: UI tickets apply ui-design VERIFY.md, design acceptance separate |
| 11 | QUESTIONS lost extend/replace, state/timing, cost/env/privacy prompts (Claude) | Restored as journey-grounding items 4–6 |
| 12 | J/Q/V IDs undefined in TASK-FOLDER (Claude) | Added. Gate wording deduplicated in router §3 to a pointer plus the two rules E1 showed must be up front |
| 13 | grilling "with the skill tool" excludes file-based hosts (Codex) | Host-neutral wording |
| 14 | Router over 700-word budget after the routing fix (Codex) | 681 words |
| 15 | VALIDATION.md stale; workflow-doctor lacks same-version check (Claude) | VALIDATION updated at delivery. Doctor not changed: sibling anchoring removes the cross-root case it would check; recorded as a limit |

Additional repairs from evaluations: clarify step 1 says questions wait for traced callers (E3 asked two rounds about batch rules later found moot); clarify refreshes the checkpoint next action on recording a gate response (E3 left it stale).

**V2** — after repairs: `tools/validate.py` PASS (681 workflow words); unittest 566 run, OK, 11 skipped (same host limits).

## E14 — Behavior evaluations, later turns

| Run | Observed |
|---|---|
| E3-t2 contradictory answer ($3.59) | Recorded settled items; derived 4 new questions from code: no "manager" permission exists (roles user/admin/superuser), missing shelf life = 0 so "today counts" would block every such recipe, offline printing, unlinked labels |
| E3-t3 ($3.76) | Gate one presented: actors, unchanged behavior, exclusions, rejectable assumptions AS1–AS3, exact gate question. Checkpoint `Agreement: draft revision 1`, `Approval: not approved` |
| E3-t4 partial rejection of AS2 ($3.92) | Agreement revision 2 "partially agreed"; only R9 reopened; found knock-on contradiction (manager cancel < chef). Defect: checkpoint next-action line stale |
| E3-t5 ($4.52) | During specification found only recipe prints are item-linked, making agreed batch rules R8/R9 moot; paused specify, reopened only R1/R8/R9, others kept authority. Shows premature questioning in t1–t2 (it had not traced print callers) → clarify repair "questions wait for traced callers" |
| E1-t2 grilling answers ($4.55) | **Gate-one failure**: treated the answers as agreement, wrote tickets and the HTML plan (`review-r1.html`), stopped at gate two with no code. Session had never loaded `workflow-clarify` (pre-fix router) |
| E1b-t1/t2 same prompt and answers, repaired router ($1.17 + $1.87) | Invoked `workflow-axa:workflow-clarify`; after the answers recorded `Agreement: pending, draft r1`, presented the agreement with an example table and assumptions S1–S2, asked the gate question, wrote no plan. Before/after on one run each: evidence of the defect and fix, not a rate |
| E3-t6 agreement + specification ($7.57, 41 turns) | Invoked clarify → specify → ui-design → codebase-map. Plan reuses the approved alert sheet (no new markup/CSS), records 30/32 already-failing baseline tests, keeps `environment.ts` (production) off-limits, leaves the staging check to the owner. `review-r1.json` carries `task_report` (planning, agreement approved, 6 sections, 3 ticket specifications), state awaiting-approval |
| E4 direct `/workflow-axa:workflow-execute` "implement now", fresh session ($0.84) | Entry guard held: refused because gate two is not approved; wrote no files (records included); restated the plan and asked for gate two plus separate cross-repo permission. Independent invocation verified for execute's guard |

## E15 — D6 rewrite, report restructure and D7 bundled specialists

- **Rewrite (D6).** Router, four phases, QUESTIONS, GROUNDING, WRITING, VISUAL-REVIEW, TASK-FOLDER rewritten as short imperative steps: ~11,300 → ~7,400 words; SPECIALISTS 2,168 → ~800. Every rule guarded by a test kept (7 guarded phrases restored after the first pass; one assertion changed only for a renamed heading, `## 0.` → `## 1. Check rules readiness`). Independent rule-preservation review by Codex pending (first two attempts: stdin wait, then "model at capacity").
- **Report (D6).** Subagent restructured `task_report` reports to the reader-first order; legacy inputs byte-identical apart from timestamps; 5 new red→green tests; screenshots `.artifacts/.../checks/report-readability/after-*.png` reviewed by the coordinator (one status callout, six sections, friendly tabs, ticket cards, single acceptance list, details collapsed). Ticket wording itself still comes from task records.
- **Bundled specialists (D7).** 15 files from `mattpocock/skills@4ae2317` (MIT) under `skills/workflow/specialists/`, generated by `tools/vendor_specialists.py`; adaptation sections replace the old Q/T/C/M adapters; phase skills, router, QUESTIONS, WRITING, AUDIT, plan-review, rule-maker, SETUP and README point at the copies. `retro` ships with `digest_sessions.py`. Regression tests `tests/test_vendored_specialists.py` (4; written after the code, so characterization, not red-first).

## E16 — Retro over 55 real sessions and fixes

Method: `digest_sessions.py` over `~/.claude/projects/D--Altinstar-Altinstar-react` (47 sessions, 3.5 GB) and `D--Cheflabels-labeler-V2` (8); a fresh-context analyst followed the bundled `retro`. Report: `.artifacts/2026-11-02-modular-engineering-workflow/retro/retro-findings.md` (counts approximate; inference labelled there). Altinstar totals: 46 compactions, 426 AskUserQuestion calls, 368 tool errors, 37 denials; one session ran 5 days with 11 compactions and ~6 unrelated goals.

| Pattern (approx. count) | Fix | Where |
|---|---|---|
| User relays status between sessions/Mac/GPT/Trello (~104) | Generated "Handoff message"; tracker mirroring on request from the records | CHATGPT-PROMPTS, router, SPECIALISTS |
| "Is it done / ticked?" (~170) | Deterministic `scripts/open_items.py` (tests/test_open_items.py, 3 tests); used by task-status and deliver. On the real Altinstar plans: 51 tasks, **854 ticked items with no evidence pointer**, 15 open | scripts, task-status, deliver |
| Turn ends while work runs (33 "why did you stop?") | Never end a turn with own work running unless the host will wake you; every turn ends with Running / Waiting on you / Done | router |
| Unrequested visible changes (~22) | Anything a user could notice is an open choice, never a delegated detail; agent choices marked `by: agent`; delivery lists them | QUESTIONS, TASK-FOLDER, deliver |
| Same questions re-asked; multiple choice demanded (24) | Check standing answers first; structured multiple-choice tool | QUESTIONS |
| Mega-sessions drift after compaction | Unrelated new goal → checkpoint and offer a fresh session | router |
| Explicit "approve without seeing" refused | Explicit "I don't need to see the plan" is a recorded gate-two waiver | VISUAL-REVIEW |
| User does device/visual QA ad hoc (~80) | `needs human: what, when` per ticket; asked together | specify, execute |
| Parallelism had to be demanded (69) | Start every ready ticket with disjoint files at once | execute |

Not changed, left for the user: merging both gates into one message when clarification leaves nothing open (would change D3), and Playwright-vs-Figma automatic visual compare (needs a per-project setup decision). Static guard: `test_retro_findings_stay_fixed`.

## E17 — Codex review R2 (rule preservation and style after the rewrite)

`codex exec -s read-only` (first attempt waited on stdin; second hit "model at capacity"; two later runs completed, output `.artifacts/.../review-codex-r2.md`). Compared HEAD originals, PLAN R1–R10 and E13 repairs against the rewritten package. **No blocker.** Applied, all with the suite green after:

- Clarify accepts a recorded LIMITED_EXCEPTION; asks direction/access blockers early instead of a blanket "don't ask before tracing" (E3 lesson kept: trace the callers a question depends on first).
- Restored lost rules: ask for a fact only when inaccessible (QUESTIONS and the bundled grilling adaptation); missing-review recovery (TASK-FOLDER); no-file checkpoint disclosure (router); lightweight record promotion (TASK-FOLDER).
- Terminal ticket states defined once in TASK-FOLDER (verified, blocked, superseded, removed, not applicable) and used by router and execute.
- VISUAL-REVIEW: the gate-two pause covers the proposed scope only; unaffected approved work, baseline checks and approved diagnostics continue.
- Bounded delegation still settles a visible detail (the retro rule was too absolute). Plan-only mode stops after specify. TDD refactoring belongs to review, per upstream.
- Docs-only route: my first fix made substantive docs pass both gates; reverted the same hour as an unrequested behavior change; it keeps its own route as in HEAD, now named (PDF-DELIVERABLE or lightweight edit).
- Style: removed the garage analogy, "Better:" hedge, and the 3-line shared-policy sentence in every phase (now one line).

## E18 — Loop 2 runs on the final package

| Run | Observed |
|---|---|
| A2 session 2, fresh session (Altinstar base; $2.59) | Resumed from records; recorded gate one with the user's words; `workflow-specify` → `codebase-map` report; stopped at gate two, report marked draft for two open technical choices (Q7, Q8); ended with "**Waiting on you:**" (retro state-line fix observed); deleted its own check screenshots; flagged visual check and builds as human steps |
| C2, fresh session, approve except T1 (Cheflabels; $3.94, 56 turns) | `workflow-execute` → `workflow-deliver`. Never wrote to `../pletrix-cheflabels` (its pending changes date from March/May 2026, the owner's). Reviewer subagent read the bundled `code-review` and found a real defect: the planned endpoint returns no stock rows, so every check would allow printing. Spec 10/10 after failing first; dev build OK; full suite 26/332 failing old stubs. Delivered as partial with owner steps listed. **Defects**: switched endpoint, adding a "recently viewed" side effect, and disclosed it only after shipping; never opened the bundled `tdd` (wrote 10 tests at once, disclosed); no baseline suite run before changes; skipped the delivery snapshot despite a visual review |

Repairs (guarded by `test_retro_findings_stay_fixed`): execute reads the tdd file before the first test, records a baseline run of the ticket's check before changing anything, and sends a repair that changes the approach or anything user-visible to the user before shipping; deliver must make the snapshot or record the user's refusal. D8 implemented.
| A2 session 3, fresh session, approve with 7a/8a (Altinstar base; $3.69, 10 turns) | `workflow-execute` → `workflow-deliver`; read the bundled code-review (main and reviewer subagent). Red first (chips showed `12.345`/`1.000.000`), 38/38 after; TS no new errors; lint clean; caller search shows only two `compact` users. Independent reviewer found a BTC-decimals edge (recorded, low). Full web gate not GREEN: 17/18 failures from files the sparse worktree lacks (`game-assets/`, dev Unity player), 1 (`UIButtons.room-chat.integration`, missing `initReducer`) unattributed because no pre-change baseline run, which the newer execute rule now requires. Restored an unrelated snapshot's line endings the gate run changed. Delivered **partial**, owner steps listed, ended "Waiting on you". Skipped the delivery snapshot: this session loaded the deliver text from before the snapshot rule was tightened (verified in its transcript) |

## E19 — Vendored skills become separate skills (user correction)

The user: "i also do not want the matt pea cocks skills inside workflow it needs to be actuall skills seperate skills." Implemented: `skills/<name>/SKILL.md` for grilling, tdd, code-review, writing-for-agents, codebase-design, domain-modeling, implement-spec, retro (upstream frontmatter; `disable-model-invocation` kept for implement-spec and retro; per-folder `LICENSE`; `agents/openai.yaml`); provenance moved to `VENDORED-SKILLS.md`; plugin and validator register twenty skills (header rule allows the upstream flag; budgets ~115 % of current size). Phases load siblings (`../grilling/SKILL.md` …). The old `skills/workflow/specialists/` folder was removed after A2 session 3 (the last run that could read it) finished. One test adjusted for meaning: the "unrelated external skill" fixture now uses `research`, since `grilling` is a package skill. Validator PASS; 580 tests OK (11 host skips).

The user also said the split is confusing; most use is `/workflow`. Explained the map; asked whether to hide internal skills from the `/` menu (pending).

## E20 — One owner per rule (user request) and Codex review R3

The user found it confusing that questioning lived in `grilling`, `workflow/QUESTIONS.md` and a 5-step summary in clarify, and asked: "why not put it in grilling … do a review over all files and improve where needs improving."

- **Questions → `grilling`.** QUESTIONS.md content (when to grill, trace first, item classes, visible changes, standing answers, structured tool, break-it pass and stop rules, recording answers, gate one) moved into `skills/grilling/SKILL.md`'s adaptation section without repeating what Matt's text already says. Clarify step 2 is now one pointer. Router, validator, UPGRADE and tests repointed; guarded phrases now asserted on the grilling skill. QUESTIONS.md is deleted once the running A3 session finishes.
- **Generator.** `tools/vendor_specialists.py` no longer embeds adaptation text; it refreshes the upstream part and keeps each SKILL.md's own adaptation section (verified idempotent: regenerating changed nothing).
- **Codex R3** (`.artifacts/.../review-codex-r3.md`, 14 findings) applied: installation checker and INSTALLATION.md cover all twenty skills (it listed eight); option B could not run because specify demanded a recorded agreement and the report validator rejects approval-ready reports without one — specify now accepts the combined route and the report stays draft until the yes to both; resumption owned by `resume-task` (TASK-FOLDER points to it; takeover and other-machine rules moved there); TDD loop owned by `tdd`; re-review owned by `code-review`; report production owned by `codebase-map`; necessity check single owner AUDIT (plan-review points to it); artifact cleanup owned by ARTIFACTS; ADR criteria owned by `domain-modeling`; plan-review routes plan text to WRITING and agent instructions to writing-for-agents; routing template no longer says "installed grilling"; Implement Spec adaptation owned by `workflow-execute`.
- **Deferred, recorded as remaining work:** RULES.md restates part of rule-maker READINESS (it already declares itself a router; low risk), and the UI mode definitions appear in ui-design SKILL, CONTRACT and shared design.md (strict-UI area with many guarded phrases and the owner-approved rc.7 policy; needs its own careful pass).

**V3** — validator PASS (twenty skills); unittest 580 run, OK, 11 host skips.

## E21 — Loop 3 runs and the final Claude review

| Run | Observed |
|---|---|
| A3, fresh session, BTC decimals fix ($1.11) | Treated as an in-scope repair of the approved task (agreed: below 10.000 exactly as before), so no new gates, which matches VISUAL-REVIEW "Don't re-ask". Failing test first (`'0'`), 39 related tests pass, lint clean, typecheck 95→95. Ended "**Done**". Option B therefore not exercised |
| A4 s1, new small request: jackpot list too ($1.33) | Reused the task as proposed revision r2; found a real open choice (two places show the list) and a `CONTEXT.md` conflict, so asked gate one (option B correctly not applicable); offered answering both at once |
| A4 s2, "9a, agree r2, I don't need to see the plan" ($2.61) | Honored the explicit waiver; recorded its self-written ticket as an agent decision (`by: agent` observed live); red→green; independent reviewer; delivered partial. **Skipped the delivery snapshot despite the rule** → rule moved into deliver's explicit "Done when all three exist" (snapshot whenever the task has any HTML report, or the user's recorded no) |

Final independent Claude review (15 findings) applied: execute and README no longer say "one at a time"; VISUAL-REVIEW step 1 admits the combined route (agreement status `not-approved` until the yes to both); phase skills point to the router's "Always" list (state line on direct calls); D10 recorded and D7 marked superseded; UPGRADE drops the unverifiable version claim, says twenty, rewrites the specialists paragraph; installation checker and docs speak of all registered skills; counts fixed in CHANGELOG and test READMEs; snapshot rule owned by deliver; clarify records a "yes to both" from a later session; project routing block names the combined case; red/green in AUDIT points to tdd; README opens with a five-step "Start here"; vendored upstream text is hash-checked by a test proven to fail on a one-character edit. Delivery snapshot masthead says "Delivery D1" for delivery reports (red→green).

**V4** — validator PASS; 580 run, OK, 11 host skips.

## E22 — Loop 4: deferred clean-ups, option B and a rewrite regression

- **RULES.md** reduced to loading, the readiness states by name (owner: rule-maker READINESS.md), module selection and hand-off (~600 → 275 words). **ui-design** §2 now points to the shared design.md definitions and CONTRACT.md's permission table instead of restating them; the guarded "No new plain-HTML controls" stays. design.md itself untouched (versioned, hashed shared library; changing it belongs to the rules-audit task).
- **A4 s3** (direct `workflow-deliver`, $2.85): made `delivery-2026-11-02.html` unprompted, kept `review-r1.html`, downgraded a stale "verified" to partial, labelled its self-reconciliation. Delivery-snapshot rule confirmed live.
- **A5** (fully specified small visible change "lowercase k", $2.27): handled as a lightweight edit with no gate and only a self-review. Root cause: my D6 rewrite changed the lightweight definition from HEAD's "behavior … is not lightweight" to "no behavior … *question*". Restored HEAD's meaning in the router ("A visible behavior change, however small and fully specified, is not lightweight: it takes the two gates, or both at once when nothing is open"); guarded in `test_retro_findings_stay_fixed`. A6 retests option B.
- **A6** (fully specified visible change after the lightweight fix, $0.99): option B observed live. It saved "Agreement r4", asked for both approvals in one message ("agree and approve r4"), and its break-it pass surfaced a real edge (1.999.999 → 1M). Deviation: no HTML report in the combined message; clarify's hand-off now says "tickets and the HTML report … with the report path".

## E23 — Retro over the evaluation sessions (agent-side bottlenecks)

Fresh-context analyst, bundled `retro`, digests of the three eval projects plus raw transcripts; report `.artifacts/.../retro/retro-eval-findings.md`. 12 candidate transcripts, ~$34.5 total, 16 tool errors, 0 permission denials. Phase shares are the analyst's estimates.

| Finding | Fix (package) |
|---|---|
| Report building costs most and fails most: 9/16 errors from renderer geometry/validation messages that name nothing; agents read `render_report.py` in pieces 30 times and guessed with 12 JSON/coordinate patches | All 20 geometry/validation errors now name the node/edge, the measured value and the limit (old wording kept as prefix); test `test_geometry_errors_name_the_node_and_the_limit` (written after the change). Not done: a JSON scaffold and a bundled screenshot helper (recorded as follow-ups) |
| New requests on an approved/delivered task bypassed `workflow-execute` in 3 of 6 code sessions; one shipped a visible change with only a self-review | Router row: such a request goes to `workflow-clarify` (in-scope repair or new revision); "code changes go through `workflow-execute`"; plus the E22 lightweight fix |
| Long checks rerun just to filter output (~30 min) or waited on when known to fail | Execute step 5: save long output once, query the file, never rerun to filter |
| ~100 record-write commands, mostly inline scripts to keep CRLF; ~59 line-ending probes; heredoc failures | `workflow/scripts/record.py` (append, set-line, tick with evidence; keeps line endings) + `tests/test_record.py` (4 tests); TASK-FOLDER points to it |
| Truncated reads of package files (TASK-FOLDER 80/110 lines) returned | Router: read package files whole, never through `head`/`sed -n` |
| Startup context 133–156k tokens per session (~$0.85 floor), superpowers/MCP/global blocks | Environment, not package: reported to the owner |
| Eval harness gaps (one run missing its JSON; Cheflabels worktree untrusted, "Ignoring 5 permissions.allow entries") | Evaluation setup, not package: reported |

**V5** — validator PASS (699 workflow words); 585 run, OK, 11 host skips.

## E24 — Loop 5 runs: execute route, review and delivery hardening, D11

| Run | Observed |
|---|---|
| A6 s2 "agree and approve r4" ($1.32) | Both gates recorded from one answer; went through `workflow-execute` (route fix); **baseline run before changes** (43 pass) observed live; red (4 fail) → green (44). Gaps: self-review despite subagents; no `workflow-deliver`; no `record.py` (an edit flipped PLAN to LF, repaired) |
| Repair | Execute: with subagents the reviewer must be a fresh subagent reading `code-review`; execution is done only when `workflow-deliver` has run. Guarded |
| A7 s1, small visible change ($0.99) | Combined approval asked; break-it found a real edge (line break inside a chip). Skipped the HTML report a third time → owner decision D11 (always, unless explicitly declined), enforced in VISUAL-REVIEW, specify "Done when", clarify |
| A7 s2 "Q10 b, agree and approve r5" ($3.38, 48 turns) | Full chain observed: execute → tests first (12 fail) → 44 pass, lint → **fresh reviewer subagent read `code-review` (8 reads)** → `workflow-deliver` → dated snapshot `delivery-2026-11-02-r5.html` unprompted. Remaining gaps: did not open the `tdd` file first; no `record.py` |

**V6** — validator PASS; 585 run, OK, 11 host skips.

## E25 — Loop 6: phase invocation and shortcut habits

| Run | Observed | Repair |
|---|---|---|
| A8 "Mrd" ($1.08) | Loaded only clarify; asked both gates itself without specify or an HTML report, "As in r4 and r5" (copied the task's earlier revisions). Used `record.py` unprompted | Clarify may not ask for plan approval; on the combined route it invokes `workflow-specify`. TASK-FOLDER: an earlier revision that skipped a step is not a precedent |
| A9 "5 winners" ($0.87) | **No skill invoked**; bundled identity, clarification and a combined approval with open questions | Router opening: "your next action is invoking the phase skill §3 picks; never ask the user questions or approvals from this file" |
| A10 same ($0.86) | Still no skill: the identity question (legitimately the router's) was bundled with clarification and approval | Router step 3: "When a related task might match, ask only that and stop" |
| A11 s1 same ($0.83) | Asked only the identity question and stopped — fix observed | — |
| A11 s2 "Q1 a, separate task" ($1.26) | Invoked clarify; found a real cross-task test conflict; asked gate one alone (open question). But invited "agree and approve r1" for an unseen plan, borrowing another task's habit | Clarify: never invite approval of an unseen plan; never borrow shortcuts from other tasks or earlier revisions |

Pattern across loops: agents follow the skill they load, but take shortcuts the user accepted elsewhere and skip nested "also run X" steps. Each repair is guarded in `test_retro_findings_stay_fixed`; compliance remains probabilistic (one run per scenario).

**V7** — validator PASS (router exactly 700 words); 585 run, OK, 11 host skips.
| A11 s3 "Q1 a, I agree to r1" ($2.04) | `workflow-specify` → `codebase-map` built `review-r1.html` for a one-line change, asked exactly the gate-two question, stopped. **D11 observed live** | — |

## E26 — Screenshot helper (eval-retro follow-up)

`skills/codebase-map/scripts/screenshot_report.py` takes desktop (1280) and narrow (500) screenshots with the installed Edge/Chrome; nothing installed; never overwrites. Found while building it: on Windows the Edge launcher returns before the image is written (helper waits up to 30 s), and headless Chromium won't lay out narrower than ~500 px (a 390 px capture was clipped; exact phone widths still need Playwright). Observed on `reviews/delivery-r2.html`: desktop and narrow images readable, no clipping at 500 px. Tests `tests/test_screenshot_report.py` (2, fake browser). REPORT.md points to it. **V8** — validator PASS; 587 run, OK, 11 host skips.

## E27 — Checks enabled by D12 (installs approved by the user)

- **Python Playwright 1.64.1** installed with `python -m pip install --user playwright` (no Playwright browser download; the tools used the installed Chrome via `--browser`).
- **Visual regression, same environment:** `tools/visual_regression.py capture` of the rc.8 snapshot and of the candidate, then `compare`: **PASS, 4 comparisons pixel-identical** (legacy fixture; desktop flow panels and mobile). Against the shipped `visual-baselines/2.2.1`: NOT_VERIFIED (different capture environment), as the tool is designed to report. Evidence: `.artifacts/.../checks/visual/`.
- **Browser suites:** `browser_smoke.py` PASS 20 checks; `ui_browser_smoke.py` PASS 19; `kit_browser_smoke.py` PASS 10.
- **Native plugin discovery:** `claude plugin marketplace add D:/workflow-axa` (marketplace `gazohhh`) and `claude plugin install workflow-axa@gazohhh` (user scope): 20 skills listed, ~1,760 always-on tokens. A fresh headless session **without** `--plugin-dir` resolved `/workflow-axa:workflow` from `D:/workflow-axa/skills/workflow` (local marketplaces load the source folder) and gave an accurate, read-only status of the Cheflabels task ($0.87). It answered the status question itself rather than invoking `task-status` (the router lists it as an option, not a requirement). To remove: `claude plugin uninstall workflow-axa@gazohhh` and `claude plugin marketplace remove gazohhh`. The rc.8 personal skills in `~/.claude/skills` are unchanged.
- **Codex discovery:** copied the candidate's 20 skill folders into the Cheflabels eval worktree's `.agents/skills` (project scope; nothing global changed; removed afterwards). `codex exec -s read-only` with "Use the $workflow skill: where does the task … stand" read `…/.agents/skills/workflow/SKILL.md` and `…/task-status/SKILL.md` (the candidate, not the global rc.8 in `~/.agents/skills`), routed to task-status, set READ_ONLY, and ended "**Done.**" Output `.artifacts/.../eval/codex-native.md`.

## E28 — Trend across the loops

32 headless evaluation runs cost $78.81 in total. Early runs (E1–C2, 14 runs) averaged $3.42; the latest (A5–A11 and the native run, 12 runs) averaged $1.40 with similar agent-turn counts. The later requests were smaller changes, so this is not a controlled efficiency measurement. Tool errors per session fell from 16 across the earlier sessions (E23) to 0–1 per session in the latest digest (`.artifacts/.../retro/eval-final.md`).

## E29 — Small end-to-end workflows on the worktrees (user goal)

The user asked for a small workflow on the worktrees to catch bugs. Two runs, fresh session per step:

| Run | Steps observed | Bugs found |
|---|---|---|
| W1 Cheflabels "expired stock rows first" ($1.08 + $1.92 + $2.39) | clarify (4 grounded questions) → "yes to all" → specify + HTML `plan-rev1.html` + one combined question → "yes to both" → execute (read `tdd`; tests failed first; 4/4 pass) → fresh reviewer subagent read `code-review` (9 reads), one note fixed, one plan deviation recorded → deliver → `delivery-2026-11-02.html` | Full-suite baseline not run before the change (26 failures attributed by type, not count) |
| W2 Altinstar "no filler rows in Last winners" ($0.88 + $1.22 + $0.95 + $2.32 + …) | router asked only the task-identity question → clarify found the zero-winners edge → **a new session could not read "Q1 a"** because only the question had been saved → re-asked → specify + HTML `review-r1.html` + combined question | Options of an open question not saved with it → fixed in `grilling` ("save every open question before you send it, with its exact options, letters and recommendation"), guarded |

**Altinstar full web gate for the compact-amounts test change** (eval worktree `wfaxa-eval-base`, `game-assets/` added to the sparse checkout, `public/unity-native-dev` linked read-only to the main checkout's ignored build): NOT GREEN, but not because of the change. Vitest 7,912 pass / 2 fail; owner-build 49/49, fixture-typecheck 4/4, build-graph 172/172, reconnect-e2e 30/30. The 2 Vitest failures: `UIButtons.room-chat.integration` (its test store lacks `initReducer`, which `RoomConnectionContext` reads; a project test-setup gap, unrelated to money formatting) and `nativePlayerFreshness` (0 Unity source files to fingerprint in this worktree; environment). Node-test failures read the excluded `ios/` tree or call staging hosts. Log `.artifacts/.../checks/altinstar-web-gate/gate.log`. The on-screen look check stays with the owner (design acceptance).
| W2 cont. "yes to both" ($3.15, 45 turns) | execute (read `tdd`; 3 of 4 new tests failed first; 4/4 after; typecheck 95→95; eslint clean) → fresh reviewer read `code-review` (7 reads), one note fixed and re-confirmed → deliver → `delivery-2026-11-02.html`; delivered partial because the test ran through a stand-in config (worktree lacked `UnityClient/`). Coordinator then added `UnityClient/` to that worktree and ran it with the project config: **4/4 pass** | — |

Repair from W1: execute's baseline now covers every check the ticket names, full suites included, recorded as counts. Both small workflows completed clarify → specify (HTML) → execute → independent review → deliver with snapshot. **V9** after the repairs below.

## E30 — Retro over all test sessions (user request) and fixes

Fresh-context analyst, bundled `retro`, all three eval projects plus the Codex run; report `.artifacts/.../retro/retro-all-findings.md`. Newest 20 sessions: 324 tool calls, $30.67, 4 tool errors, 0 denials. Earlier fixes (question options, baseline run) not recurring.

| Finding | Fix |
|---|---|
| Report JSON is the costliest step: all 6 HTML builds hand-wrote 50–80-line generators; 4/6 first tries failed | `task_report.py scaffold <approved review.json> <new delivery.json>` (valid delivery JSON, claims nothing, `FILL:` texts only); named in deliver's Done-when; test renders an unedited scaffold (example and the real W2 review JSON) |
| Heredocs with backslashes break scripts | TASK-FOLDER: write scripts and JSON with the file-write tool, never a heredoc |
| 36% of tool calls touch records; `record.py` mostly bypassed (it could not create files or replace sections); LF flips, a cp1252 byte, NBSP repairs | `record.py new` and `replace-section` (6 tests); named in clarify step 3, specify step 2, deliver step 8 |
| Session-start `cat *.md` overflows output (7 times) | `open_items.py --task <folder>`: checkpoint, latest Outcome, tickets, record problems (non-UTF-8, mixed line endings); test |
| Independent reviewers labelled themselves "self-review" | `code-review` adaptation: a fresh non-builder sub-agent is "independent, axes sequential" |
| Screenshot helper stopped on a missing output folder | Creates it when its parent exists |
| Truncated package reads persist; identity question costs a full session (~$0.80) | Owner decisions (warning hook; bundling identity with grilling round 1) — asked |

**V10** — validator PASS; 591 run, OK, 11 host skips.

## E31 — D13 implemented

Plugin hook `hooks/hooks.json` + `hooks/truncated_read.py` (PostToolUse on Bash|Read; warns, never blocks) with 4 tests; `claude plugin details` lists "Hooks (1) PostToolUse"; a live probe (`sed -n 1,5p …/TASK-FOLDER.md`) received the warning as context. Identity question moved into clarify's first round (router invokes clarify; never with approvals); guarded.

## E32 — D14 implemented: owner's styling rules replace strict kit reuse

Rules library 1.6.0 → **1.7.0** (`design.md` rewritten; CORE, START, READINESS, ionic, SOURCES aligned; manifest regenerated with `tools/update_rules_manifest.py --apply`). ui-design SKILL and CONTRACT rewritten (modes behaviour-only, reuse, blocked, plain-by-instruction; legacy names mapped). Renderer `screen_flow.py`: new modes; approval-ready UI needs a current mode; legacy approved-kit keeps its binding check; labelled sketches allowed so every UI-visible change can show a diagram. Clarify: anything a user sees on screen is application UI; specify: visible changes need the report's screen diagram (W1/W2 had none). Router, SPECIALISTS, routing template, plan-review, rule-maker, doctor, UI-FLOW, KIT docs, README updated. Policy tests rewritten to D14 with equal protection plus a new test that reuse/plain-by-instruction/behaviour-only can be approval-ready without a kit binding. Found and fixed during the change: Python `write_text` had silently turned 17 package files to CRLF (tests caught it via the rules manifest). **V11** — validator PASS; 596 run, OK, 11 host skips.

Not changed: the user's global CLAUDE.md imports START/CORE from the installed rc.8 rule-maker in `~/.agents/skills`, which still carries the strict wording until that installation is updated.

## E33 — Design loop round 1 (D14), global sync (D15)

| Run | Observed | Repair |
|---|---|---|
| ds-nk1 no-kit badge ($0.68) | Readiness stop correct. **Violations**: offered "C: a one-off exception to the no-CSS rule", and options putting button classes on a `<span>` and a `<p>` class on a `<span>`; did not ask the exact question. It read the installed rc.8 START/CORE (global CLAUDE.md imports), never the new design.md; a `cd …/skills && cat … | head -80` slipped past the hook | design.md rule 4 and ui-design: ask exactly; offer only existing same-tag elements or plain-by-instruction; never CSS or another tag's classes. Hook: relative paths after `cd` into the package (red→green test) |
| ds-al1 Altinstar kit ($1.07) | Loaded clarify; kit entries are unapproved drafts (project DESIGN_KIT.md) so treated "Top" as needing an element to copy; proposed mirroring `sm-chip info-chip`; identity question bundled with round 1 (D13 observed) | — |
| ds-ch1 Cheflabels DESIGN.md ($1.18) | Loaded ui-design and clarify; found the approved "Row status chip" `.main-list-item-chip-error` and reused key `STOCK_CHIP_EXPIRED`. **Conflict**: questions "exist only in this chat" because D13 said create no folder before the identity answer — recreating the W2 bug | TASK-FOLDER: save the round in a folder named for the recommendation, checkpoint `identity pending (vs <task>)`; move it if the user picks the existing task. Guarded |
| ds-nk2 no-kit badge after D15 sync ($0.66) | Asked the exact question word for word, offered only the existing `<span class="item-name">` (same tag), plain HTML only as the user's choice, no CSS options | — |

## D15 action — global installation synced (user-approved)

Backup `~/.workflow-axa/backup/2026-11-02-rc8/` (134 files, counts verified, rule-maker byte-identical). Mirrored the 20 candidate skills into `~/.agents/skills` (robocopy /MIR, no `__pycache__`); updated the two real folders in `~/.claude/skills` (grilling, domain-modeling); added junctions for the 7 new names in `~/.claude/skills` (same pattern as existing). Verified byte-identical to the package in both roots; `audit_installation.py --check-global`: candidate MATCH; the managed blocks in `~/.claude/CLAUDE.md` and `~/.codex/AGENTS.md` report UPDATE (older template text; their imports already load the new files) — left for the owner. Restore: copy the backup folders back.

## E34 — Design loop round 2

| Run | Observed | Repair |
|---|---|---|
| ds-nk3 (one-task exception + plain HTML allowed, $0.88) | Recorded "plain HTML, no classes, no CSS, no inline style"; flagged that a new `id` is not an existing ID. The earlier round's questions were lost because they were bundled into a readiness stop before any task folder existed | RULES: a readiness stop asks only the readiness choice; design.md: script hooks use `data-*` (never an invented styling class/ID); clarify names `../ui-design/SKILL.md` (ui-design had not been loaded) |
| rm1 rule-maker audit, Cheflabels ($1.43) | Read-only. Loaded the synced 1.7.0 library (START, CORE, design.md, AUDIT, version), chose modules from actual versions (Angular 20, TS 5.8, Ionic 8, Capacitor 8), applied "stricter project rule wins", and found real conflicts between Cheflabels DESIGN.md/AGENTS.md and D14 plus gaps (Node range, no type-check command, stale stub baseline, `.claude/settings.local.json` pre-approving writes to the backend repo) | Project changes are the owner's; listed for them |
| ds-nk4 (combined plan, $2.25) | clarify → specify; report with "UI screens" tab (sketches); banner said "Draft — nothing to approve yet" while asking for both approvals | Status sentence for the combined route ("Waiting for your OK on the behaviour and this plan…"); red→green test |
| ds-nk5 (build + deliver, $2.00) | Diff verified by the coordinator: `styles.css` unchanged; only `<span data-item-count></span>` and two lines in `refresh()`; real-browser check 8/8 red→green; independent reviewer; delivery snapshot. Sketches only although the page was capturable | specify: capture the current screen when safe; deliver: real captures of the built result (screenshot helper) |
| ds-nk6 (direct deliver, $2.19) | New dated snapshot `delivery-2026-11-02-r2.html` with **two real captures** of the built page (loaded, empty); earlier reports untouched. Reported `open_items.py` crashing on a cp1252 console | `open_items.py`/`record.py` force UTF-8 output; test with `PYTHONIOENCODING=cp1252` |
| ds-ch2–ch4 Cheflabels (kit project) | ch2 could not use answers from ch1 (pre-fix, unsaved) and refused to guess; ch3 gate one with two approvals (new component input = interface); ch4 plan mirrors the stocks-list chip with identical tags/classes, report with UI screens diagram (sketch: the page needs a production login), explicit "no `.scss` changed" check | — |
| Owner's complaint "I don't see a diagram" | The screen diagram sat behind a "UI screens" tab | Renderer opens application UI reports on the screen diagram unless `open_first: false`; test |

**V12** — validator PASS; 599 run, OK, 11 host skips. Installed copies re-synced after each package change.

## E35 — Old documents (design loop round 3)

| Run | What happened | Fix |
|---|---|---|
| old1 task-status on Altinstar `2026-10-30-react-design-kit` | Read-only. Mapped the old `functionality-only` mode to `behaviour-only`, kept the stricter project rule, changed no files | — |
| old2 resume-task on Altinstar `2026-10-28-game-connection-state-machine` ($1.16) | Read-only reconcile: classified rev1/rev2 approvals, noticed the stale `review-r2.json` "awaiting-approval", code changed after the phone test, evidence only in the main checkout, other tasks' uncommitted changes; asked where to run the delivery check. Offered to rewrite the old review JSON to match the records | resume-task: old reports are history, never edit or offer to edit one; guard test |
| Old `review-r2.json` re-render | Renders with the current renderer; `--check` reports CHANGED sources (expected: code moved on) | — |

**V13** — validator PASS; 599 run, OK, 11 host skips; resume-task re-synced.

## E36 — Design retro and round 4

Retro over 13 design-loop sessions (`.artifacts/2026-11-02-modular-engineering-workflow/retro/retro-design-findings.md`). Diffs clean: no CSS in nokit or Cheflabels; the Cheflabels chip has identical tags/classes to `stock-list-item.component.html:23-27`.

| Finding | Fix |
|---|---|
| The `open_first: false` from the illustration example was copied into a real plan and scaffolded into delivery, so the diagram was hidden again | Renderer: an `application` review always opens on the screen diagram; `open_first` only for illustrations; test |
| UI-FLOW, VISUAL-REVIEW, VERIFY and EXAMPLES still taught the strict-kit model (omit the screen view, approved-kit required, "not an allow-list of class names", a different question) | Rewritten to D14; guard test against the stale phrases |
| ui-design asks for reused elements per screen, but reports had no place for them | `ui_review` screens take `elements: {id, source, locator, tag, classes, changes}` without a kit; required on proposed screens in `reuse` mode; rendered as "Existing elements this screen copies"; tests |
| design.md rarely read; execute never pointed at ui-design | ui-design names `../rule-maker/rules/design.md`; clarify reads both first; specify and execute read ui-design; router: "Never write or offer new CSS, even as an exception" |
| Delivery did not name the file that defines each class | deliver Outcome lists each class with its defining file and "no CSS added" |
| The sketch checker reports one problem per run | UI-FLOW documents all sketch limits (height, 42 characters, width estimate) |
| Altinstar DESIGN_KIT.md still says "strict kit" | Owner's item |

Round 4 runs:

| Run | What happened | Fix |
|---|---|---|
| ds-al2–al3 Altinstar (kit project, $3.6) | Answers saved, agreement r1; then found the name column stacks blocks, and offered **option c: "a small new style rule… an explicit exception to no new CSS"**. The session never read ui-design or design.md | Option ban in router, clarify, specify, grilling; guard test |
| ds-nk7 no-kit, "red circle badge" ($0.92) | No CSS offered; explained `.btn-danger` is a different tag; queued the exact question; asked readiness alone (rev 1's exception expired); no code changed | — |
| ds-al4 Altinstar plan ($3.20) | Plan report for a visible change **without any screen diagram**, state awaiting-approval: it copied a sibling task's report JSON as its template and never read UI-FLOW/TASK-REPORT | `task_report.screen_change` (`visible`/`none`) is required for approval-ready plans; `visible` without an application `ui_review` fails; TASK-REPORT, specify; test |

**V14** — validator PASS (700 workflow words); 603 run, OK, 11 host skips; installed copies re-synced.

## E37 — Round 4 build, delivery and retro

ds-al5 (repair, $4.05): after "I don't see any diagram", made review-r2 with `screen_change: visible`, mode reuse, Today/After/No-winners screens, two copied elements; opens on the diagram (screenshot checked). It offered to delete the presented r1 (fixed: VISUAL-REVIEW forbids it). ds-al6 (build + deliver, $8.86): `InfoLinePlayer` gained `nameLabel` rendering `<div className="sm-chip info-chip">` (same tag/classes as `InfoLinePlayer.tsx:94`), no stylesheet changed, Outcome lists `sm-chip` and `info-chip` with `RedwinxGameClient.scss:801/:819`, 10 tests pass, delivery partial (no dev server), delivery report opens on the diagram, `--check` MATCH.

Retro (`retro/retro-round4-findings.md`, 14 findings):

| Finding | Fix |
|---|---|
| The copied pill renders as a full-width bar: its shape comes from `.dashboard-info-line-chip .sm-chip.info-chip` (scss:6515), and the name column's `div` rule restyles it (verified by the coordinator) | design.md rule 3 "Mirror the element, with its context"; new `ui-design/scripts/class_rules.py` lists every rule for a class with nested selectors joined and marks rules that need context; reused elements require `context`; tests |
| A specify-time answer (placement) became a decision while R1 still said "next to the name" | specify: such an answer is a new agreement revision, asked with gate two |
| $8.86: 84% was re-reading a 290k context; deliver and the single ticket ran in the planning context; a late re-review missed the cache | execute hands every ticket to a fresh worker; deliver in a fresh subagent; re-review promptly |
| Seven render attempts: one error per run | screen checker reports every screen's problems in one run; test |
| `record.py` unused; 14 silent `node -e` replaces | `record.py batch` (all-or-nothing, exact single match, keeps CRLF); TASK-FOLDER points to it; test |
| Whole-feature review skipped for one ticket | one review briefed with the whole-feature checks counts as both |
| The web gate's server prerequisite surfaced only at delivery | specify names each check's prerequisites and asks with gate two |
| Stale "real kit captures" in codebase-map SKILL | rewritten |
| Exception expiry ambiguous for a reopened task | READINESS: expiry says "this task folder, all revisions" or "revision rN only" |
| TASK-FOLDER "ask reopen or follow-up" vs router "clarify decides" | aligned: clarify asks with its first questions |
| An interrupted run in the wrong worktree created a task folder there | TASK-FOLDER: checkpoint names another worktree → stop and ask (the orphan folder in `D:/Altinstar/wfaxa-eval` is eval scratch from the coordinator's wrong-cwd resume) |
| Project-owned: 6–7 minute type check, mixed line endings in `DashboardGameWinners.tsx`, 1.4 MB raw type-check evidence | owner's |

**V15** — validator PASS (700 workflow words); 608 run, OK, 11 host skips; installed copies identical.

## E38 — Round 5: context rule end to end (Altinstar "Big win" pill)

| Run | What happened | Fix |
|---|---|---|
| ds-al7 (fresh, $2.04) | Claimed "no new CSS or layout" for the name-label slot (the round-4 context problem); never opened ui-design, design.md or grilling; `record.py new` wrote LF in a CRLF project | clarify trace step 6 inlines the screen check with the `class_rules.py` command; grilling read "now, before writing any question"; `record.py new` follows CRLF input or sibling records (input read as bytes); tests |
| ds-al8 (rerun, $2.02) | Checked the popup title-column rules and warned about the look; questions saved | — |
| ds-al9–al11 (agreement, plan) | Agreement correct; plan stopped for Q7 "may the report include a sketch?"; final review-r2 has `screen_change: visible`, Today/After/No-data sketches and both elements with `context` citing `class_rules.py` and `RedwinxGameClientMobile.scss:8860` | Sketches inside the offline report need no permission; only captured proposed screens need preview authority; UI-FLOW; test |
| ds-al12 (build + deliver, $2.97 for the turn) | One-line diff, no stylesheet, fresh worker built T1 test-first, fresh reviewer; Outcome names `RedwinxGameClient.scss:801/:819`; delivery partial, opens on the diagram | see retro |

Retro (`retro/retro-round5-findings.md`). Costs were running totals: per turn $2.02, $1.66, $1.73, $0.63, $2.97; about $1.9 was cache rebuilds from MCP servers reconnecting (owner's environment).

| Finding | Fix |
|---|---|
| The plan copied a neighbour's `clientIsOkeyplaza()` against AGENTS.md; only the reviewer noticed, after the build | specify ticket field **Rules** (each AGENTS.md/CLAUDE.md on the path; a forbidden neighbour pattern is no precedent, ask with gate two); CORE: a project rule for new code wins over an older neighbour |
| Delivery report said "Not implemented" and "Proposed — not built yet" under "Delivered: partial" | scaffold always writes a fresh delivery checkpoint; renderer captions the proposed flow "As built" in delivery; deliver sets every status from the records, not only `FILL:` texts; test |
| The name-column difference was noted but the slot was still recommended | design.md rule 3: compare the parents; any layout difference is no match, never recommend the copy anyway; `class_rules.py --compare <from> <into>` prints both parents' declarations and rules that style their children; clarify step 6; test |
| T1 ticked verified with an open review finding | deliver: verified needs no open review finding |
| Readiness line named files never opened | RULES.md: name only rule files you opened |
| Agents learned the report schema from a sibling task | VISUAL-REVIEW: start from codebase-map's example JSON and TASK-REPORT.md |
| Deliver did not run in a fresh subagent | Recorded; the retro found no cost saving here, so not enforced further |
| Project-owned: unused MCP servers, no lint rule for new brand checks, `LastWinners.compact.spec.tsx` breaks test/AGENTS.md, C2 must check the pill width | owner's |

**V16** — validator PASS; 610 run, OK, 11 host skips; installed copies identical.

## E39 — Round 6: Cheflabels header chip (kit project, plain-by-instruction)

| Run | What happened | Fix |
|---|---|---|
| ds-ch6 (fresh, $1.33) | Read ui-design, grilling and design.md first; ran `class_rules.py` and `--compare`; saw the row chip's look depends on its row; asked design.md rule 4's exact question with same-tag options, no CSS, plain only on instruction, no recommendation; identity bundled as Q1; read the backend repo only | Saved Q6 recommended a, sent message b → grilling: saved and sent options and recommendations match exactly; guard test |
| ds-ch7 (answers, Q4 c) | Plain-HTML permission saved word for word (D4); agreement honest that the count will not be red; no backend change | — |
| ds-ch8 (plan) | Tickets carry the new **Rules** field (AGENTS.md lifecycle, rights, naming); `plain-by-instruction`, `screen_change: visible`, sketches, report in `reviews/`, opens on the diagram; H1 against staging, not production | see retro |

Retro (`retro/retro-round6-findings.md`):

| Finding | Fix |
|---|---|
| T1 reused the start-up copy where the agreement said "reload every visit", and the message still said "implements the behavior we agreed" | specify gate two: compare every ticket with the agreement first; any difference is an agreement change; that sentence only when none; the agreement-change rule applies in any step |
| Told the owner the sketch would show the look and readability | ui-design step 3: a sketch shows structure, not the look |
| `preview.status: authorised` cited a record that granted nothing | `not-needed` status for sketch-only reports (rejected with a proposed capture); UI-FLOW; test |
| All five partial-read hook warnings were false (`grep | head`, `--help | head`, full-length `head -N`, project paths after a later `cd`) | Hook checks each pipeline segment, skips searches and tools, accepts a limit that covers the whole file(s), converts `/d/` paths, resets on `cd` out; tests with the five commands |
| Records edited with `sed -i`, `>>`, `str.replace` (one matched nothing) | Hook also warns on in-place edits of PLAN/TODO/FINDINGS/DECISIONS and points to `record.py`; test |
| Rules line named modules never opened | Already covered by RULES.md "name only rule files you actually opened" (added after this session started) |
| Project-owned: Unity/Postman MCP reconnects re-inject instructions (cost) | owner's |

**V17** — validator PASS; 613 run, OK, 11 host skips; installed copies synced.

## E40 — Round 6b: Cheflabels build and delivery (plain-by-instruction)

ds-ch9 ($9.34): fresh worker built T1 test-first, fresh reviewer (two rounds), baseline compared by name (0 new failures, 1 fixed), dev build passes; markup is one plain `<div *ngIf>` with no class or style (D4); no stylesheet, backend or production. Delivery `reviews/delivery-2026-11-02.html`: "As built" captions, fresh checkpoint "implemented", completion partial (device check H1 open), opens on the diagram. After the round-6 hook note every record edit went through `record.py`.

Retro (`retro/retro-round6b-findings.md`):

| Finding | Fix |
|---|---|
| Delivery header said "Nothing was run"; preview still "authorised" citing the Rules line | scaffold sets `snapshot.basis` to `FILL:` and a sketch-only preview to `not-needed` with a `FILL:` summary; test |
| D10 "read" the agreement to match the plan; A1 verified, S1 and the per-actor line had no verdict | deliver step 2: per-actor lines and assumptions get verdicts; reading the agreement differently from its words is a gap for clarify |
| A fix the reviewer called a user decision shipped without asking | execute step 7: such findings go to the user |
| Repairs and delivery ran in the 300k-token main context | deliver runs in a fresh subagent whenever the host has them; self-performed only without |
| Chat said "the full suite passes" (25 old failures) and "every finding is fixed" (two open) | WRITING cold-reader: claims name old failures, count open findings, list only checked behaviour |
| Hook warned on a Read with only an offset (rest of file) | Read warns only with a limit; test |
| Low: implementer skipped AGENTS.md and tdd; one slice added nine tests at once; VERIFY.md diff helper unused; screenshots in the scratchpad | Existing rules cover these; recorded |

**V18** — validator PASS; 613 run, OK, 11 host skips; installed copies synced.

## E41 — Round 7: final regression (no kit, no project rules, both gates in one message)

ds-nk8–nk10 ($1.56 + $4.05 + $6.52): readiness stop asked only the readiness choice (badge task's exception had expired) → one-task exception → both gates in one message with `reviews/plan-P1.html` → "Yes to both" → check red 5/8 before, green 8/8 after → fresh worker (its pasted diff was caught and re-run), fresh reviewer, fresh delivery reconciler → delivery with a real capture of the built page and its copied element, opens on the diagram, no `FILL:` left. Diff: only the three labels; no CSS.

Draft gap found by the coordinator: the combined route always renders a draft, so `reuse` elements and `screen_change` were never enforced on it → now required on every plan report, draft included; specify names `screenshot_report.py` for a local page and `not-needed` for sketch-only previews; tests.

Retro (`retro/retro-round7-findings.md`):

| Finding | Fix |
|---|---|
| ui-design, design.md, VERIFY.md and `class_rules.py` never opened (repeat) | Model compliance limit: the rules that matter are now inline in router, clarify and specify and enforced by the renderer where possible; recorded, not fixable by more text |
| Test output put in the session scratchpad because `.artifacts/` was not ignored; the check script deleted, so V1 cannot be re-run | TASK-FOLDER: use `.artifacts/<task>/` even when not ignored (say so; never change `.gitignore`); a script a recorded check names is evidence until acceptance |
| "Delivered: complete — everything agreed is done and checked" while owner acceptance is pending; invented exception expiry | complete wording adds "Your acceptance is still yours to give"; READINESS: expiry in the user's words |
| Tool friction (~29% of the build turn): screenshot helper exit 1 on Windows cleanup; scaffold missing task outcomes; completeness error named nothing; `replace-section` duplicated a heading | `ignore_cleanup_errors`; scaffold sets `outcome: implemented` with a `FILL:` note; the error lists each failed condition; `record.py` refuses a duplicate heading; tests |
| Execute vs deliver on who runs deliver | execute invokes deliver; deliver runs its reconciliation in a fresh subagent |
| Environment: ~145k tokens loaded before any work (MCP servers) | owner's environment |

**V19** — validator PASS; 614 run, OK, 11 host skips; installed copies synced. The design loop ends here: the last three rounds found no CSS written or offered, the exact question used, context compared, plain HTML only on recorded instruction, and a screen diagram that opens first in every plan and delivery report. What remains is tool friction and agents sometimes skipping required reads.

## E42 — Round 8: structural hooks, full rule-maker audit, more old documents, live re-checks

Stop-hook review after E41: required reads were still skipped, rule-maker had only one partial audit, few old-document scenarios, and the round-7 fixes were not re-verified live.

| Run | What happened | Fix |
|---|---|---|
| New hook `hooks/phase_reads.py` | When a phase skill loads (PostToolUse on Skill) it names the exact files to read with full paths and the `class_rules.py` commands; when `/workflow` loads (Skill, or typed via UserPromptSubmit) it says the next action is the phase skill, no questions from the router; tests | — |
| r8-nk1 (no-kit context trap, `.tag-alert` red only inside `.list-item`) | Caught the trap and asked the exact question, but from the router itself (no task folder, question unsaved) | Router note in the hook, also for typed slash commands (the typed form needed UserPromptSubmit) |
| r8-nk2–nk6 (rerun to delivery) | Router invoked clarify; clarify read grilling, ui-design and design.md whole; Q5 asked again when the grey tag inside the heading would sit differently; plan with a real capture of the current page, a sketch of the proposed one, element + context, `preview: not-needed`; build stopped at Q6 when screenshots showed the heading made the label bold; delivery "Your acceptance is still yours to give", "As built", real captures of current and built page, evidence kept in `.artifacts/<task>/check/`, four fresh subagents | — |
| r8-rm1 rule-maker full audit, Altinstar (plan mode, $1.60) | Loaded START/CORE/READINESS/VERSIONS/ENGINEERING/POLICY/AUDIT, react, typescript, vite, capacitor, threejs, pixijs, unity, design and the risk modules, each with a reason; skipped angular/ionic/php/laravel/rust; checked versions against the lockfile; found `src/AGENTS.md` styles section and root AGENTS.md:83 still conflicting with D14, a memory note against the artifact policy, and minor gaps | Altinstar `AGENTS.md` and `src/AGENTS.md` aligned (uncommitted); its "global block out of date" was a false reading (header line in the deployed policy; `activate_rules.py` run from the package copy) → `activate_rules.py --check` now explains when the block points to another copy; test |
| r8-od1–od3 old documents (plan mode) | Oldest Cheflabels task (stale records found, superseded placement asked); old strict-kit UI task (refused to call it delivered: old checks, no review, open design questions; asked before leaving read-only mode); Altinstar cleanup task (stale checkpoint, untracked owner items, dead review link); nothing written | — |

Retro (`retro/retro-round8-findings.md`):

| Finding | Fix |
|---|---|
| Execute skipped the whole-feature review; deliver ran it and changed a check, then reported reconciliation as clean | deliver: execute must have recorded the whole-feature review (else hand back, never run it here); anything fixed after reconciliation means reconciling again |
| Router note never fired for `/workflow` in plan mode | hook also matches the `<command-name>` form; test |
| Two avoidable rounds (Q5, Q6): placements offered without `--compare`; heading bold not visible to the helper | design.md rule 3: inherited text differences count, compare every placement before offering it; `--compare` notes inherited text and bold heading defaults; test |
| Record-edit warning discounted; a heredoc wrote a control character into FINDINGS | warning names the real risk (backslashes become control characters) and gives a copyable `record.py` example |
| Deliver skipped WRITING.md and the cold-reader check | deliver step 8 reads WRITING.md first and says the check ran |
| Delivery report kept plan-time headings ("How we'll know it works", "not proof it was implemented") | delivery reads "How it was checked" and "the proposed view is what was built"; test |
| Low: task-status inferred approval from ticked TODOs; thin reading in an old task; audit listed an unchecked file as a gap | recorded |

**V20** — validator PASS; 620 run, OK, 11 host skips; installed copies synced.

## E43 — Round 9: live re-checks of the round-8 fixes (clean)

| Run | What happened | Fix |
|---|---|---|
| r9-ch1 Cheflabels `/workflow continue` on an old delivered task (plan mode) | Router hook note fired in the `<command-name>` form; reported the task as delivered with its evidence and the open owner check; changed nothing | — |
| r9-nk1 no-kit "grey New tag inside the page title" | Clarify spotted the heading's bold, baseline and missing gap before building, saved the task and questions; but recommended the non-matching copy and paraphrased the question | Clarify hook note: any look difference is no match; ask the exact question, same-tag options, recommend none; test |
| r9-nk2 rerun | Exact question word for word, same-tag options, plain only on instruction, "I'm not recommending any of these", question saved in the task folder | — |

Coordinator self-check over both runs (small, single-turn; no separate retro agent): no CSS written or offered, nothing written in Cheflabels, records in the task folder. The recreated no-kit project was removed afterwards.

**V21** — validator PASS; 620 run, OK, 11 host skips.

## E44 — Round 10: rule-maker on both stacks, live re-checks, report layout

| Check | Result | Fix |
|---|---|---|
| Altinstar audit (r8-rm1) transcript | All 16 claimed modules were read whole (one `for f in react typescript … ; do cat $f.md` loop) | — |
| r10-rm2 rule-maker audit, Cheflabels (plan mode, $1.62) | Loaded angular, ionic, typescript, capacitor, design, operations and the risk modules with reasons; skipped vite (webpack build), react, php/laravel, unity, three, pixi, rust; matched twelve project rules to module text. Found: rule-maker SKILL still said "missing kit coverage blocks new UI"; Cheflabels DESIGN.md line 5 still "shared strict kit reuse"; AGENTS.md silent on candidate entries; plus project gaps (no HTTP mocking rule, no type-check command, stale test baseline, `ionViewWillLeave`) | rule-maker SKILL and AUDIT aligned with D14 (stricter project rules win and must be stated where agents read); specify "an unrecorded mode blocks only UI tickets"; Cheflabels DESIGN.md line 5 and AGENTS.md aligned (uncommitted). Project gaps are the owner's |
| Example report re-render | Rendered with the current code: UI screens open first; example text still said "functionality-only preview" and preview "authorised"; the 1280px board was cut off in a 1280px window (also seen in two delivery reports) | Example text and `preview: not-needed` updated; UI-FLOW: screen boards at most 1160px (wrap to a second row); both examples re-laid out to 1152px, HTML regenerated; screenshot shows all screens without sideways scrolling |
| r10-nk1–nk3 end to end (no kit) | Router → clarify → specify → execute → deliver; real capture of the current page plus sketch with element and context; fresh builder and reviewer; one review covering ticket and whole feature (single ticket), recorded; fresh reconciliation; cold-reader check stated; diff one word, no CSS. WRITING.md not opened; a check was fixed after reconciliation without reconciling again | Deliver step 8 carries the cold-reader questions itself; deliver hook note: deliver never fixes, reconcile again in a fresh subagent after any fix; test |
| r11-nk1–nk3 end to end again | Router → clarify (spotted the uncommitted edit on the same line and the older task's check that would start failing) → both gates → fresh builder, fresh reviewer → fresh reconciliation found two note mistakes → fixed → second fresh check confirmed them | — |

**V22** — validator PASS; 620 run, OK, 11 host skips; installed copies synced. The recreated test project was removed again.

## E45 — Round 11: kit project end to end with the current package; Altinstar re-audit

| Check | Result | Fix |
|---|---|---|
| Round-10 deliver fixes | Already live-verified by r11 (reconcile → note fixes → second fresh check), which ran after those edits | — |
| r12-ch1–ch3 Cheflabels kit project, temporary detached worktree with the owner's aligned AGENTS.md/DESIGN.md ($1.19 + $3.35 + $7.53) | Router → clarify → specify → execute → deliver; six questions saved; Q5 answered "no backend change"; plan with the approved neutral chip copied (`div.main-list-item-chip.main-list-item-chip-neutral`, context "inside div.main-list-item-chips"); fresh builder test-first (3 of 4 failing, then 4 of 4), fresh reviewer, fresh reconciler; classes named with `global.scss:2289/2304`; no CSS, translations, backend or production; delivery "As built", "How it was checked", "Your acceptance is still yours to give", diagram first on a 1000px board | — |
| r12-rm3 Altinstar rule-maker re-audit (plan mode, $1.74) | Earlier conflicts gone; loaded all applicable modules with reasons; found `src/AGENTS.md` style bullets still read as CSS instructions, a stale auto-mode permission in `.claude/settings.local.json` for a finished task, a delegation list in CLAUDE.md that omits the shared rules, and an unclear "every change needs a measurement" rule | `src/AGENTS.md` bullets reworded as where-to-find notes (uncommitted); the settings permission, delegation clause and measurement wording are the owner's |

The temporary worktree was removed (junction unlinked first; target intact).

**V23** — validator PASS; 620 run, OK, 11 host skips.

## E46 — Plain English and the owner's report design (2026-11-03)

Owner requests: report wording had "lots of AI slop" (use the Simple English skill), then a new report design (`files.zip`: `report-style.css`, `report-extra.js`, sample `review-r1.html`).

| Change | Evidence |
|---|---|
| `skills/simple-english` vendored from AminBlg/SimpleEnglish `a6fcb4f` (2.1.1, MIT): skill folder only, LF, hashes in VENDORED-SKILLS.md, workflow-axa adaptation (reports are documents; exact text kept; project terms kept; chat without contractions); registered (21 skills) | `tests/test_simple_english.py` |
| Report steps load it: TASK-REPORT.md, VISUAL-REVIEW, deliver step 8, specify/deliver hook notes | test |
| Renderer fixed wording rewritten by the Simple English rules (no em-dashes, no contractions, short active sentences, American spelling to match content) in task_report.py, render_report.py and screen_flow.py; example snapshots regenerated | 627 tests |
| Renderer prints `PLAIN ENGLISH:` lines (semicolons, em-dashes, banned words, contractions, sentences over 25 words, paragraphs over 6 sentences) with each JSON path | test; the long task's plan and delivery reports had 0 problems |
| Owner design: reports with `task_report` use `report-style.css` and `report-extra.js` unchanged (`report-style-compat.css` maps the older tokens the screen diagram uses); new markup: skip link, masthead, report header with status tag and facts row, sticky numbered contents, sections, ticket stubs, checks with progress, risks, open-questions box, appendix, footer. Older reports keep `report.css` | test; screenshots of sample, plan and delivery reports |
| Screen diagram canvas carries `--board-width`, so the owner's JS starts it on Fit; plain card captions; empty decisions heading hidden; narrow captures named in hooks | screenshots |
| Retro r14 (`retro/retro-round14-findings.md`): simple-english read only at delivery; "Passed" next to an expected red run; plan wording copied into deliveries; header counted acceptance as "Checks" | prose check; `red` check state ("Failed before the change, as expected"); scaffold marks plan-time wording as `FILL: rewrite in the past tense`; label "Acceptance"; deliver hook: write nothing until reconciliation reports |
| Runs: short task r14 (rename, plan + delivery in the new design, plain wording), long task r15 (two dependent tickets, both questions with the exact mimic question, plain HTML by instruction, 13/13 checks, fresh agents, delivery in the new design, readable narrow captures) | `eval/r14-*`, `eval/r15-*` |
| Altinstar-react and Cheflabels rule edits committed and pushed on the owner's request (Altinstar after merging one remote commit; Cheflabels only `AGENTS.md`, `DESIGN.md`) | `dfab50db7`/`f4a8c225e`, `a9565f5` |

**V24** — validator PASS (21 skills); 627 run, OK, 11 host skips; installed copies synced.

## E47 — Long-task retro and final short-task check (2026-11-03)

Retro over the two-ticket session (`retro/retro-round15-findings.md`):

| Finding | Fix |
|---|---|
| "Clear list" used `btn btn-danger`, a class set no existing element had (Delete buttons are `btn btn-small btn-danger`); reviewers missed it | design.md rule 3: copy the whole class list; `class_rules.py --match <tag> <classes>` lists existing elements with exactly that tag and class set (markup, templates, HTML in JS strings); execute hook runs it on every new element; test |
| Both tickets built in the main session ("two-line edit") | execute hook: a fresh worker for every ticket, even a two-line edit; record who built it |
| T2 started before T1 was verified; repairs not re-reviewed | execute hook: dependencies verified first; re-review every repair |
| "Failed before the edits (1 of 13 lines)" when 12 of 13 failed | execute hook: quote counts exactly as the check output states them |
| Chat messages outside delivery skipped simple-english | WRITING.md points to it |
| Prose check missed other page text | it also checks boundaries, open decisions, ticket outcome notes, flow titles and descriptions, next action and screen-diagram text; bundled examples rewritten to pass |
| `record.py tick` wrote "verified: verified:" | strips a repeated prefix; test |

Final short task r16 (second "Add item" button, $0.98 + $3.07 + $7.33): exact mimic question, then plan with both gates; a fresh worker built the one ticket, `--match` found the header button `btn btn-primary` (`index.html:8`), check counts quoted exactly (10 passed, 8 failed before; 18 and then 21 passed after), repair re-reviewed, fresh reconciliation, narrow screenshots.

**V25** — validator PASS (21 skills); 629 run, OK, 11 host skips; installed copies synced. The test projects `D:/wfaxa-eval-nokit` and `D:/wfaxa-eval-nokit-codex` remain (removal blocked by a safety check; the owner deletes them).

## E48 — Chat wording hook and a design-kit run with the new report (2026-11-03)

| Change or run | Result |
|---|---|
| `hooks/plain_reply.py` (Stop): in sessions that used workflow-axa, the last reply with contractions, em-dashes or semicolons gets one rewrite request (never twice in a row; code and quoted text exempt); tests | In r17 it fired and the final message had none of those |
| r17 Cheflabels kit task (temporary detached worktree on `a9565f5`, $2.15) | Plan report in the owner's design; approved neutral chip copied inside the same chip wrapper with its DESIGN.md reference; `preview: not-needed`; honest sketch note; plain-English check: 0 problems in the report, 0 in the final reply |
| `class_rules.py --match` reported "no match" for `div.main-list-item-chip.main-list-item-chip-neutral` because Angular adds the variant with `[ngClass]` | Now reports `BOUND MATCH` for same-tag elements with a class binding whose missing classes appear as strings in the code (found `action-card.component.html:18`); test |

The temporary worktree was removed (junction unlinked first; target intact).

**V26** — validator PASS (21 skills); 633 run, OK, 11 host skips; installed copies synced.

## E49 — Retro r17 and a Stop-hook read check (2026-11-03)

Retro over the Cheflabels kit run (`retro/retro-round17-findings.md`): the Stop hook rewrite worked, but the agent ignored both phase reminders and never opened grilling, ui-design, design.md, UI-FLOW.md or simple-english, while the records listed design.md as read.

| Fix | Evidence |
|---|---|
| `hooks/plain_reply.py` also checks, for every workflow phase loaded in the session, that each required file (phase_reads `READS`) was opened after the load; the UI files count only when the session wrote a `ui_review` or `screen_change`; one combined rewrite request | tests; replayed on r17 it names exactly the skipped files |
| Clarify and specify hook notes name `class_rules.py --match` (the mirror record cited the wrong element) | test |
| VISUAL-REVIEW: a visible or accessibility choice the user has not made is an open choice, not an "assumption you can reject" | — |
| Combined-gate reports tag "Waiting for you", not "Draft" | 634 tests |
| TASK-FOLDER: owner is a name, never an email address | — |

Live check r18 (uppercase category tags, no kit, $1.97): the hook asked for the missing reads and plain wording (5 requests each); at the end no required file was unread and the reply used full forms. No CSS: the capitals were typed into the words, with the side effects stated.

**V27** — validator PASS (21 skills); 634 run, OK, 11 host skips; installed copies synced. `D:/wfaxa-eval-nokit` and `D:/wfaxa-eval-nokit-codex` were deleted by the owner on 2026-11-03 (confirmed gone).
