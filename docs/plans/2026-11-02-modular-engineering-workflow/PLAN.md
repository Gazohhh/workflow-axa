# Modular engineering workflow

## Current checkpoint

- Updated / phase: 2026-11-02, delivered (partial; see Outcome); design loop (D14) finished in eleven rounds (FINDINGS E35–E45); evaluation worktrees removed (D16).
- Agreement (gate one): R1 agreed through D5; later user decisions D6–D10.
- Approval (gate two): waived for this task by D5 (bounded; the product keeps both gates).
- Implementation: done. Verification: V1–V7 passed; ~30 live sessions in six loops; browser suites and native host discovery not run.
- Owner: Claude session `workflow-axa-ff` since 13:10 (Codex wrote T2–T4 first; no handoff was recorded).
- Next safe action: the owner reviews the uncommitted design-rule edits in Altinstar-react (`AGENTS.md`, `CLAUDE.md`, `src/AGENTS.md`, `docs/plans/2026-09-24-reference/DESIGN_KIT.md`, `docs/plans/2026-09-24-architecture-audit/README.md`) and Cheflabels (`DESIGN.md`, `AGENTS.md`; the audit's project gaps: HTTP mocking rule, type-check command, test baseline), accepts the delivery and decides on committing; nothing is pushed or committed.

### Baseline and attribution (T1)

- HEAD `9daf5076763fadcdf8c498cfbaebcd30d71fbaa2` = 2.7.0-rc.7. The 2.7.0-rc.8 Windows fixes (check_design_kit.py, inspect_kit_index.py, test_design_kit.py, test_line_endings.py, behavioral STRICT-KIT/cases) were written 12:10–12:11 after E9 and belong to the rules-audit task; its snapshot `.artifacts/2026-10-30-rules-audit-design-kit/release/rc8-snapshot/workflow-axa/` is the pre-refactor comparison package. Read-only; owned by that task.
- Everything else in `git status` beyond the three audit records is this task's work. Installed host copies: rc.8 in `~/.claude/skills` and `~/.agents/skills`; Matt `code-review` and `implement-spec` not installed; `grilling`, `tdd`, `writing-for-agents` installed.

### Behavior evaluation plan (T5)

- Worktrees (user-requested): `D:/Altinstar/wfaxa-eval` (branch `eval/workflow-axa-2.8.0-rc.1` from `d63970a5b`, sparse: excludes ios, UnityClient, altinstar-apple, altinstar-android, game-assets) and `D:/Cheflabels-labeler-V2-wfaxa-eval` (same branch name from `2b41ba8`). Main checkouts untouched. `node_modules` reuse via junction to each main checkout only if a scenario runs tests; no installs.
- Runner: `claude -p --plugin-dir D:/workflow-axa` (exact candidate source, namespaced `workflow-axa:*`), budget-capped per run, staged replies via `--resume`. Baseline comparison: same prompt without `--plugin-dir` (installed rc.8).
- Output: transcripts and summaries in `.artifacts/2026-11-02-modular-engineering-workflow/eval/` (ignored). Retain final summary per scenario plus traces for failures; task records each run writes stay in the eval worktrees until the user removes them.

## Working context

- Repository: `D:/workflow-axa`, branch `main`, baseline HEAD `9daf5076763fadcdf8c498cfbaebcd30d71fbaa2` (reconfirm before implementation).
- Task identity: user chose “Create a linked modular-workflow task (Recommended)” on 2026-11-02. Earlier [workflow-v2](../2026-10-09-workflow-v2/PLAN.md) remains complete. The pending [rules installation/audit](../2026-10-30-rules-audit-design-kit/PLAN.md) remains separate.
- Initial edits belonging to other work: that audit's PLAN.md, FINDINGS.md and DECISIONS.md. Preserve all three and their unresolved installation choices.
- Rules: READY for research and task/review documentation. Read installed workflow RULES/TASK-FOLDER, rule-maker START/CORE/READINESS and repository README/DESIGN/report contracts. Source rc.7 strict UI reuse governs this proposal's preservation baseline; older installed instructions do not override it. No application UI is being designed.
- Output: durable reviews under this task's `reviews/`; any necessary checks under `.artifacts/2026-11-02-modular-engineering-workflow/`. Shared ARTIFACTS.md read. No output directory or cleanup required yet.

## Requested outcome

Make `/workflow` a small coordinator of reusable skills covering research, informed clarification, explicit agreement, specifications and dependent tickets, visual approval, implementation, review, tests, iteration, and a readable evidence-backed delivery report.

Preserve working behavior, approval gates, UI reuse, historical snapshots, task recovery and artifact protection. Improve question quality and traceability rather than forcing more questions. Evaluate actual Matt Pocock and skills.sh writing instructions independently with Claude Opus 5.5 before recommending adoption.

## Scope boundary

Package implementation, review and verification are authorized by D5. Host installation, other projects, publication, commits and remote tracker changes remain outside this package refactor.

## Approval

R1 agreement accepted and further approval pause waived by D5. Both independent reviews support the direction (FINDINGS E10). The preserved implementation report records this bounded waiver rather than inventing a response approving a report the user has not seen.

## Mutual agreement R1 (accepted through D5)

The feature being built is the engineering workflow itself. It should help an agent discover missing decisions, explain what will be built, carry an approved specification through dependent pieces of work, and show what was actually checked. It must remain usable by developers and people who do not read code.

| ID | Intended behavior and acceptance | Source |
|---|---|---|
| R1 | `/workflow` primarily selects the next applicable skill from the task's current state. Four focused phase skills cover clarification/agreement, specifications/tickets, approved execution/review, and final acceptance/delivery. Each owns real procedure, can be invoked independently within the package with its dependencies, and enforces shared entry conditions. Existing entrypoints and their supported installation contracts remain available. | User sections 1, 6 and final objective; independent review E10 |
| R2 | Clarification starts from inspected owners, callers, documentation and relevant rules. It reconstructs realistic journeys and failure paths, classifies facts/requirements/assumptions/open choices/recommendations, follows newly exposed uncertainty, and reuses sourced answers. Completion depends on coverage of relevant behavior and resolved critical choices, not question count. | User section 3 |
| R3 | For substantive new work and material scope changes, approval one confirms behavior, scope, exclusions, important journeys, acceptance and explicit assumptions in PLAN plus a chat summary. Approval two confirms the detailed specification, dependent tickets, test strategy and HTML report before coding. Records, reports, status and resumption distinguish both approvals. Material changes reopen only affected portions; unrelated authorized work may continue. Preserve the existing route for genuinely lightweight, explicit, unambiguous low-risk edits; a small behavioral/architectural change is not automatically lightweight. | User section 4; D3; preservation requirement |
| R4 | Specifications and TODOs describe bounded tickets, dependencies, implementation responsibility, acceptance and evidence. The next ticket is selected only when its prerequisites are met. Review/testing failures block dependent completion; whole-feature checks still follow ticket completion. | User sections 2, 6 and 9 |
| R5 | Preserve Matt's effective grilling, dependency-aware execution, separate Standards/Spec review, agreed public test seams and observed red/green behavior. Record explicit adaptations to tracker, Git, delegation and host constraints. Do not impersonate upstream invocation or silently modify installed skills. | User sections 1–2; existing specialist contract |
| R6 | One improved human-facing writing policy works with existing writing-for-agents guidance. Questions, plans, TODOs, decisions and reports explain meaning first while retaining exact technical conditions, terminology and evidence. The selection requires independent evaluations and resolution of objections. | User section 5 |
| R7 | The existing HTML report becomes a readable central view of the original request, agreement, current/proposed behavior, requirements, specifications, all tickets/dependencies, milestones, acceptance, checks, risks, decisions, progress, reviews and final delivery. UI work retains actual selected kit sources/captures and screen/state flows. | User section 7 |
| R8 | Markdown task records remain authoritative. Report snapshots remain immutable and dated, with prior approvals preserved; progress does not create a new agreement. New report content is derived from records. Existing report appearance, flow grammar, security checks and legacy supported inputs remain compatible. | User sections 1 and 7; current report/record contracts |
| R9 | Verify independent skills and the complete workflow, including multi-ticket work, missing requirements, approval refusal, scope change, interruptions, missing capabilities and failures. Compare the candidate with the exact pre-refactor package and establish which skill copies actually loaded. Update registration, metadata, validators and stale evaluation guidance for the agreed architecture. Keep tooling, agent-behavior and human-acceptance results separate. | User section 9; independent review E10 |
| R10 | Final delivery shows requested/agreed/implemented work, tickets, changed files, test outcomes, both review results, limitations and acceptance outcomes. Every completion or verification claim has evidence; partial and unverified work remain visible. | User section 10 |

### Representative journeys that must work

- A complete prompt: inspect the code, identify why important branches are already settled, ask no redundant questions, and present the agreement.
- A missing failure case: discover it from real code/journey evidence, explain its user-visible consequence, and wait only on dependent work.
- A partial or contradictory answer: persist the settled choices and reopen the affected branch without inventing assent.
- A dependent multi-ticket feature: execute ready tickets within approved scope, verify integration, repair review/test findings, then check the whole agreed feature.
- A later change: show the behavior delta and affected tickets/checks, request scoped approval, and preserve unchanged valid authority.
- An interrupted session: reconcile files, answers, approvals and evidence before resuming the same task and output parent.
- A missing reviewer/tool/kit or failing check: show the actual blocker and permitted independent work; never claim a pass or invent a UI fallback.
- Existing owner edits, old reports and historical records: retain ownership and history through all phases; generated status must not rewrite the agreement.

### Exclusions and limits

No automatic package or skill installation, host activation, other-project edits, external tracker requirement, commits, pushes, publication or broad historical migration. Existing rc.7 UI restrictions remain the preservation baseline; this refactor does not settle the separate pending live-installation choice. No universal guarantee that agents discover every possible requirement or obey prose. Claims of improved behavior require the planned actual evaluations.

Claude Opus 5.5 and Codex independently review this refactor and writing choice. This does not make two particular paid models mandatory dependencies for every future feature. Existing independent review requirements and honest fallback labeling remain intact; any stronger ongoing model requirement would be a new decision.

### Gate one and next step

The user has selected two approvals (D3). Approving this agreement permits detailed planning and preparation of the HTML implementation review, not implementation. The module names, exact file moves, ticket sequence and test execution details will be specified in that plan after the agreement is accepted.

The detailed plan must make the final-delivery skill's own procedure clear, resolve shared-reference packaging without duplicating rules, and specify compatible report fields for the two gates and evidence-backed outcomes. Legacy valid approvals remain valid for their recorded scope; adoption does not retroactively require a second approval or rewrite old records. Any separate runtime setup needed for actual evaluation will be identified before dependent execution.

## Implementation specification R1

### Skill and policy ownership

Add `workflow-clarify`, `workflow-specify`, `workflow-execute` and `workflow-deliver` with distinct triggers and minimal metadata. They are independently invocable within the installed package and require the shared workflow/rule-maker policies, not four independently copied policy libraries. Keep existing reference paths as stable policy/adaptation owners; move ordered phase procedure out of `/workflow`. Its routing table selects the phase from evidence and stops on missing prerequisites. Preserve the existing seven companion skills and the report skill's standalone contract.

Clarify owns the evidence-based journey/decision check and behavior agreement. Specify owns vertical tickets, dependencies, acceptance, approved test seams and the HTML plan gate. Execute owns ready-ticket selection, contextual handoffs, TDD where appropriate, ticket reviews and integration. Deliver independently reconciles whole-feature acceptance, stale evidence, unresolved reviews, changed files and an honest final delivery record/report. It does not implement repairs or turn a checked TODO into verification.

Keep QUESTIONS/GROUNDING/WRITING/ARTIFACTS/RULES/TASK-FOLDER/SPECIALISTS authoritative for their existing contracts; use explicit installed-skill pointers where cross-folder links would violate standalone packaging. Replace contradictory single-gate wording and update resume/status routes. Keep manual upstream invocation flags. Document a local execution adaptation of Implement Spec, not a false upstream invocation. Resolve actual provider identity before each required route; missing dependencies stay explicit.

### Additive central report

Keep schema 2, old required fields, existing styles, graph geometry, overwrite protection, path containment and escaping. Add an optional `task_report` object validated/rendered by a focused sibling helper. It carries sourced narrative sections (request, agreement, specification, decisions, risks, milestones, delivery), per-task specifications, explicit agreement authority, check/review outcomes and acceptance results. PLAN/TODO/FINDINGS/DECISIONS remain the master records; JSON is a generated projection with source/locator attribution. Existing checkpoint.approval continues to mean implementation authority. New agreement state is separate, never sufficient for implementation.

Provide section navigation and readable text within the established editorial report. Preserve old fixture output when task_report is absent. New fields reject unknown keys and broken references without changing legacy extra-key behavior. Verified acceptance requires passed evidence; waiver and partial/unverified states are visible. Validation can check consistency but cannot authenticate consent, executed commands or source meaning. No raw HTML, executable input or network dependency is introduced.

### Verification seams and expected results

- Public package validator and skill metadata: all twelve local skills registered once; shared references resolve; no accidental new runtime dependency; orchestrator procedure shrinks.
- Public renderer `render`/CLI and freshness check: old inputs still render; extended inputs show complete sourced content; malformed gate/evidence states, unknown new keys, unsafe text, source escape and overwrite attempts fail or remain inert as applicable.
- Existing unittest suite: unchanged behavior remains supported; deliberately update wording-specific checks only where policy ownership moved, retaining their contract assertions.
- Existing browser/visual tools if their installed prerequisites are available: old graph/UI assets and controlled baseline visuals preserved; new sections navigable/readable; no automatic baseline replacement or installation.
- Bounded actual agent evaluations: source-load exact candidate entrypoints in fresh sessions; test clarification/missing requirement, standalone stage gates, multi-ticket execution/review and evidence-backed delivery. Compare selected same-prompt baseline/candidate cases and inspect actual files/results. Missing native host-discovery proof remains a stated limit rather than a fabricated pass.
- Independent Claude final review of the task-attributable diff and results; parent review across Standards and Spec axes. Fix relevant findings and rerun affected checks.

### Ticket order and stop condition

T1 baseline/preservation → T2 skill procedures and T3 additive report (disjoint ownership) → T4 integration/docs/registration → T5 regression and actual behavior evaluation → T6 independent review/repairs → T7 final report. T2 and T3 may overlap only while file ownership remains separate. Stop when R1–R10 are accounted for with evidence and every remaining limitation is explicit; no unrelated installs, host repairs or speculative refactors.

## Outcome

**Delivered as partial** (2026-11-02). Everything agreed is built and checked; the limits below stay open.

- **Asked:** a modular, evidence-driven engineering workflow (goal file `C:/Users/Cem/Desktop/goal.md`), tested on Altinstar-react and Cheflabels worktrees, reviewed by Claude and Codex.
- **Built:** `/workflow` is a 682-word router to `workflow-clarify`, `-specify`, `-execute`, `-deliver`. Matt Pocock's eight skills ship as separate, license-carrying, hash-checked skills with workflow-axa adaptation sections; `grilling` owns all questioning. Retro-driven additions: `open_items.py`, handoff messages, turn-end state lines, parallel tickets, visible changes never delegated, standing answers, needs-human steps. Two gates, combined for small settled changes (D8), explicit waiver supported. Reader-first HTML report; stricter "complete" delivery validation.
- **Checks:** V7 validator PASS, 585 tests OK (11 host skips); about 30 live sessions in six loops on both repositories; retros over 55 real sessions and over the evaluation sessions; four independent review rounds, all findings applied. Details: VALIDATION.md and FINDINGS E11–E25.
- **Not done / not verified:** browser visual-regression suites (Playwright not installed); native discovery of the installed plugin in Claude Desktop and Codex; agents still sometimes skip nested steps (opening `tdd` first, `record.py`), so behavior is improved, not guaranteed. Follow-ups suggested by the eval retro: a `task_report` JSON scaffold and a bundled screenshot helper.
- **Agent decisions you should know about:** kept Matt's skill names (plugin-namespaced); sparse evaluation worktrees; one runner script and `node_modules` junctions reused, nothing installed.
- **Kept evidence:** `.artifacts/2026-11-02-modular-engineering-workflow/` (eval transcripts summaries, review outputs, retro digests, screenshots, upstream copy). Disposable once the owner accepts the delivery.
- **Design loop (D14, after delivery r2):** seven rounds of live runs in a no-kit project, Cheflabels (kit) and Altinstar (kit), rule-maker and old documents, each followed by a retro (E35–E41). The last three rounds wrote and offered no CSS, used the exact "I couldn't find a matching style…" question, compared wrapper context (`ui-design/scripts/class_rules.py`, `--compare`), used plain HTML only on recorded instruction, and opened every plan and delivery report on its screen diagram. Rounds 8–11 added hooks that name each phase's required reads and keep the router from asking questions, a full rule-maker audit on Altinstar, more old-document runs and live re-checks. Package checks: validator PASS, 620 tests OK (11 host skips). Still not guaranteed: agents sometimes skip required reads; the renderer enforces what it can.
- **Wrap-up (D16):** evaluation worktrees `D:/Altinstar/wfaxa-eval`, `wfaxa-eval-base`, `D:/Cheflabels-labeler-V2-wfaxa-eval` removed (their `node_modules`/`unity-native-dev` junctions unlinked first, targets intact) and the scratch project `D:/wfaxa-eval-nokit` deleted; branches `eval/workflow-axa-*` deleted on the owner's request (D18). Project design docs aligned with D14 on the current branches, uncommitted. Global CLAUDE.md/AGENTS.md blocks already match the installed library; the installed plugin reads `D:/workflow-axa` directly. Someone staged the package changes at 15:12; later edits are unstaged. Nothing was committed or pushed.
