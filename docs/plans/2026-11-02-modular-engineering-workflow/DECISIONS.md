# Decisions

## D1 — Separate linked task (approved)

The user selected “Create a linked modular-workflow task (Recommended)” on 2026-11-02 after being shown the completed workflow-v2 task and pending rules-installation task. This task owns the new refactor proposal; it does not reopen or modify their history.

## D2 — Implementation approval (pending)

The user requires independent Claude Opus 5.5 and ChatGPT evaluation, reasoned agreement, and presentation of proposed changes before implementation. Research is authorized. No implementation approval is inferred from the initial goal or reviewer agreement.

## D3 — Two distinct approvals (approved)

On 2026-11-02 the user selected “Two approvals: agreement, then implementation plan (Recommended)”. First present and obtain approval of intended behavior and scope. Only then prepare the detailed implementation specification/tickets and HTML approval report. That second approval authorizes implementation of the identified plan. This choice is not approval of an agreement that has not yet been presented.

## D4 — Shared architecture and writing recommendation (proposed to user)

Independent Codex and Claude reviews, followed by explicit challenge/reconciliation (FINDINGS E6–E10), support four real phase skills and retention of existing entrypoints/policies. Improve existing WRITING.md with writing-for-agents rather than adopting a new writing dependency. Adapt Implement Spec's task-graph execution without changing upstream invocation flags or assuming Git/tracker authority. Preserve strict rc.7 UI reuse and all historical snapshots.

The user is being asked to approve behavior/scope in PLAN R1. Reviewer agreement is not user approval. The exact module/file contracts and evidence-producing test plan remain for gate two.

## D5 — Proceed through implementation, review and testing (approved)

After presentation of R1 the user instructed: “Start working toward this goal: do not stop finish/review/test everything.” This authorizes completing this bounded refactor without another approval pause. R1 behavior/scope is accepted; the additional implementation-approval pause for this task is waived by that instruction. Prepare and preserve the concrete plan/review before implementation, then execute and verify it. This exception does not remove the two-gate protocol from the workflow product or extend authority to global installation, other projects, publishing or unrelated edits.

Use the existing installed runtime and bounded source-loaded test sessions for evaluation. No package installation or global activation is authorized or needed merely to test source instructions. Account usage from the explicitly requested Claude/Codex collaboration is within this task; do not launch an unbounded evaluation campaign.

## D6 — Matt-style rewrite and reader-first report (approved)

On 2026-11-02, after reviewing the Cheflabels evaluation report (`review-r1.html`) and the skills, the user said the report's "In this report" list, the Proposed/Today/Build order switcher, "Agreement and authority" and the technical evidence are hard to read, and that the skills carry fluff and complexity compared with Matt Pocock's style. Choices: **"Phases + their references (Recommended)"**: rewrite the router and four phase skills as short numbered steps and fold/trim QUESTIONS, GROUNDING, WRITING, VISUAL-REVIEW and TASK-FOLDER so each rule lives once (target roughly half the words; all gates and safety rules kept). **"One-pass, reader-first (Recommended)"** report: plain status sentence → what you're approving → flows → what changes → one card per ticket → how we'll know it works → risks/open questions → technical details collapsed; each fact once. Old saved snapshots are not changed.

## D7 — Bundle the specialists the workflow depends on (approved by the user's goal; location superseded by D10)

On 2026-11-02 the user set the goal: "we are relying on lots of skills external if they ever change get removed we dont have references anymore make sure to copy them over here as well and improve where needed." Implementation choice (coordinator): copy Matt Pocock's `grilling`, `tdd`, `code-review`, `writing-for-agents`, `codebase-design`, `domain-modeling`, `implement-spec` and `retro` at commit `4ae2317ddb22b046e26455e4f9c9b3aaaf62212d` (MIT, license kept) into `skills/workflow/specialists/<name>/SPECIALIST.md`. Upstream text unchanged; a "workflow-axa adaptation" section replaces the former Q/T/C/M adapters in SPECIALISTS.md. Named `SPECIALIST.md`, not `SKILL.md`, so hosts never register them as competing skills (the same-named built-in `code-review` ambiguity from review R1 disappears). `tools/vendor_specialists.py` regenerates them; README records per-file hashes for drift checks. `research`, `diagnosing-bugs`, `prototype`, `pr`, `wizard` stay optional installs.

## D8 — Both gates in one message for small, settled changes (approved)

On 2026-11-02 the coordinator explained that the retro showed the user often pre-approving ("approving plan dont need to see the plan") and offered A (always two stops) or B (combine when nothing is open and the change is small). The user answered: **"option b"**. Implemented in VISUAL-REVIEW.md ("Both gates in one message": one journey, no new interface, dependency, data migration, security or UI-kit question; only an explicit yes to both records both lines), with pointers in workflow-clarify and the router. D3's two distinct approvals remain the default for everything else.

## D9 — Keep all skills visible in the `/` menu (decided)

On 2026-11-02 the coordinator offered to hide the internal skills (four `workflow-*` phases and the eight vendored skills) from the user's `/` menu. The user answered: **"no leave the menu as it is"**. No `user-invocable` or visibility changes are made; `/workflow` remains the documented entry point.

## D10 — Vendored skills are separate skills; one owner per rule (user corrections)

Supersedes D7's location. On 2026-11-02 the user said: "i also do not want the matt pea cocks skills inside workflow it needs to be actuall skills seperate skills." The eight copies now live at `skills/<name>/SKILL.md` (registered, plugin names `workflow-axa:<name>`, own `LICENSE`, upstream text unchanged plus a "workflow-axa adaptation" section; provenance and per-file and body hashes in VENDORED-SKILLS.md). The coordinator kept Matt's names (namespaced by the plugin) and told the user; no objection was raised.

Later the user said the split of questioning across `grilling`, QUESTIONS.md and clarify was confusing: "why not put it in grilling as we now have that skill please do a review over all files and improve where needs improving." Decision: each rule has one owner file and every other place points to it (questions → grilling; red/green → tdd; review → code-review; report production → codebase-map; resumption → resume-task; gates → VISUAL-REVIEW; records → TASK-FOLDER; ADR criteria → domain-modeling; Implement Spec adaptation → workflow-execute). QUESTIONS.md was removed. Deferred with reason: RULES.md vs rule-maker READINESS overlap, and UI mode definitions in ui-design/CONTRACT/design.md (FINDINGS E20).

## D11 — HTML plan report for every gate two, small changes included (decided)

After three live runs skipped the HTML report in the combined small-change message, the coordinator asked whether small settled changes need the HTML page (A: always; B: chat plan suffices). The user answered: **"A unless user does not want it explicitly asking for it"**. Every gate-two request, combined or not, includes a fresh HTML report; skipped only on the user's explicit request, recorded in their words. Enforced in VISUAL-REVIEW (owner), workflow-specify ("Done when"), workflow-clarify (combined route); guarded by `test_retro_findings_stay_fixed`.

## D12 — Installs allowed for the two open checks; delivery not yet accepted

On 2026-11-02 the user selected both "Install Python Playwright" and "Install candidate plugin", and answered "Not yet" to accepting the 2.8.0-rc.1 delivery. Scope: Playwright for Python plus its Chromium, to run the package's visual-regression suites; installing this candidate as a Claude Code plugin to test native discovery. Nothing else is authorized by this.

## D13 — Truncated-read warning hook; task question bundled with the first question round (decided)

On 2026-11-02, after the retro over all test sessions, the user chose "Add warning hook (Recommended)" (a plugin hook that only warns, never blocks, on partial reads of the package's .md files) and "Bundle with first questions (Recommended)" (when a related task might match, ask "separate task or revision?" together with the first clarification round, with options for both answers, never together with approvals). This supersedes the A10 rule "ask only that and stop".

## D14 — Adopt the owner's styling rules for application UI (decided; supersedes rc.7 strict kit reuse)

On 2026-11-02 the user supplied `C:/Users/Cem/Downloads/styling-rules.md` and chose "Adopt styling-rules.md (Recommended)" over keeping rc.7's strict kit rule. Rules: never create, modify or inject CSS (no stylesheet rules, `<style>` blocks or `style=""`); use only classes/IDs already defined in the project's stylesheets or present in its HTML (design kit or existing code); a new element mirrors both the class name and the HTML tag of the existing element it copies; decision workflow: search existing code for a matching element → if none, stop and ask "I couldn't find a matching style for [element]. Is there an existing element I should mimic?" → only on the user's explicit instruction, or when the user confirms no similar element exists, add plain HTML with no classes or styling; before finishing, verify no new CSS properties were introduced and every class used already exists. Also from the same goal: every UI-visible change shows a screen diagram in the HTML report (real captures when available, otherwise a clearly labelled layout sketch). Must be tested with and without project design-kit rules, and through rule-maker.

## D15 — Sync the global installation with backup (decided)

On 2026-11-02 the coordinator showed that the user's global CLAUDE.md loads START/CORE from the installed rc.8 rule-maker, which still had the old strict UI wording. The user chose "Yes, sync with backup (Recommended)": back up the installed workflow-axa folders to `~/.workflow-axa/backup/` and copy the 20 candidate skills over them. Editing the global CLAUDE.md/AGENTS.md blocks was not included.

## D16 — Owner items after testing (decided)

On 2026-11-02 the user said: "Yours to decide fix them after all testing is done and we remove the worktrees than on current branch we work on you can make the changes without pushing your self yet but thats only after everything is tested/looped/retro ran and fixed and workflows are tested like said also design guide all is done marked as done".

Meaning: only after the design loop is finished (retro clean, workflows and design checks done, goal marked done) and the eval worktrees are removed, the coordinator may make the owner items on each repository's current branch: Cheflabels `DESIGN.md`/`AGENTS.md` conflicts with D14, Altinstar `DESIGN_KIT.md` strict-kit wording, and the global CLAUDE.md/AGENTS.md block update. No pushing. Not before that point.

## D17 — Owner decisions after the rule-maker audits (decided)

On 2026-11-03 the user answered four questions:

- **Cleanup in Altinstar:** "Memory note wins (Recommended)". Altinstar `AGENTS.md` now says to keep test setups (worktrees, branches, `.artifacts` output and players) until the owner says to remove them, stricter than the shared default.
- **Stale auto-mode permission:** "Remove it for me". The 2026-10-16 docs-cleanup entry was removed from Altinstar `.claude/settings.local.json` (`$defaults` and all other entries kept); backup at `.artifacts/2026-11-02-modular-engineering-workflow/altinstar-settings.local.json.bak`.
- **Cheflabels test rules:** "Mock HTTP + dev build (Recommended)". Cheflabels `AGENTS.md` now says specs never call a real server (`HttpTestingController` or stubs) and the type check is `npx ng build --configuration development` (there is no `npm run build` script; the default configuration is production).
- **Commit:** "No, I'll review first (Recommended)". All rule edits stay uncommitted.

## D18 — Remaining audit findings and eval branches (decided)

On 2026-11-03 the user answered:

- **Subagent briefs (Altinstar CLAUDE.md):** "Add one clause (Recommended)". The delegation bullet now also passes the shared rule modules in use with their revision and the design rule; "permitted scratch cleanup" became "the keep-test-setups rule" (D17).
- **Measurement rule:** the user asked: "i would say performance affecting but than again how is something marked as performance affecting imagine something you didnt know that could effect.. so i would say every change than your opinion?". The coordinator proposed drawing the line by what ships; the user chose "Everything that ships (Recommended)". Altinstar `AGENTS.md` and `docs/plans/2026-09-24-architecture-audit/README.md` now say every change to something that ships (code under `src/` or `UnityClient/`, assets, build config, dependencies) needs a before/after measurement even when it looks harmless; docs, agent rules, task records, test-only files and comments are exempt.
- **Eval branches:** "Delete them". Deleted locally: Altinstar-react `eval/workflow-axa-2.8.0-rc.1` and `eval/workflow-axa-rc8-baseline` (both at `d63970a5b`), Cheflabels `eval/workflow-axa-2.8.0-rc.1` (at `2b41ba8`); both tips are base commits still on the main branches. Nothing remote.

All rule edits stay uncommitted (D17).
