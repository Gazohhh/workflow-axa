# /spar: cross-model sparring before planning

## Current checkpoint
- Updated / phase: 2026-11-17; T11 implemented and in review (S15-S19); T6 continues on the rebuilt candidate
- Rules: READY (AGENTS.md project rules: validate, tests, boundaries, release permissions; shared START, CORE, READINESS)
- Recipe: feature; modifiers none — a new user-invoked skill in the package, feeding the existing workflow phases; scope: the task; classification question: not asked
- Agreement (gate one): agreement 7 additions agreed (D35, R41-R44); agreement 6 agreed (D25), revised by D26 and D28 (approved with offers #6 and #7, D27, D29, D32); D18 and D19 superseded by agreement 6; D31 confirmed by the owner (docs/plans/2026-11-17-rc3-merge D1); agreements 3-5 kept where agreement 6 doesn't replace them
- Offer: #9 approved (owner, question tool, 2026-11-17); #7 and #8 superseded
- Implementation: T1-T5 and T7-T12 verified (T12: agreement 7, offer #9); T6 live runs remain (run 5 needs the owner to raise the 26-launch cap: 25 used)
- Verification / owner acceptance: not run
- Blockers: none
- Changed files: skills/spar/ (SKILL.md, T3.md, SPAR-FILE.md, agents/openai.yaml), skills/grilling, skills/workflow-clarify, skills/workflow/scripts/settings.py, hooks/phase_gate.py (RECORD), .claude-plugin/plugin.json, CONTEXT.md, README.md, docs/ARCHITECTURE.md, docs/RULE-CONTRACTS.md, skills/workflow/SPECIALISTS.md, tests (spar, settings, approval hook, package counts). Worktree: D:\workflow-axa-redesign (detached at c5e954b); the main checkout stays untouched until release
- Scope paths: exactly offer #7's paths (docs/plans/2026-11-17-spar-skill/offers/offer-7.json), including hooks/phase_gate.py (SPAR_RECORD only); CHANGELOG.md and UPGRADE.md wait for the release

## Goal

Owner's request (2026-11-17, /workflow): a reusable `/spar` skill that replaces the owner's manual Claude and GPT planning discussions with structured, evidence-based sparring, then hands an agreed approach to `/workflow` for planning and approval. Reuse existing skills; verify the actual GPT mechanism; at most 3 debate rounds by default; no forced consensus; never implement without approval; project- and language-independent; keep token use down. Present the plan for approval before implementing.


## Agreement

Agreement 3, agreed by the owner on 2026-11-17 with offer #1 (D11): agreement 2 (agreed with additions R11-R13, A5; D9) changed by the owner's D10 (R6, R8, R9, R12, R14, A5, steps 3, 5 and 6). Agreement 2 replaced agreement 1 after revision 2. Designed independently by Claude and GPT-6 Astra (blind round 0), cross-examined in round 1; both agree on proposal v4 (FINDINGS S3, S4). Owner choices D1-D8.

### Requirements

- R1 `/spar <problem> [depth]` is started only by the owner (D3) and decides WHAT and WHY for one decision; `/workflow` decides HOW. It never implements (revision 2 items 8-9).
- R2 It composes existing skills and owns only the debate: grilling for owner questions; workflow-clarify step 1 for discovery inside a task; codebase-design for architecture weakness; domain-modeling for terms; `research` and `diagnosing-bugs` when installed, read-only, never fixing (item 6; E12, E13).
- R3 Foundations are challenged in proportion to the decision: the premises the existing code, docs, tests and past decisions give it are written down, the ones the decision depends on are tested and marked checked, contradicted or unverified; weaknesses, debt and whether a refactor must come first are named (item 3; pstack attack-the-premise).
- R4 Independence: two fresh debaters, a fresh Claude subagent and GPT through T3, get the same frame and criteria; the blind opening has neither see the other; the coordinator argues no side: it frames, validates objections and evidence (R11), compares and records (item 4; D5; arena).
- R5 Depth: quick 1, standard 3, deep 5, a number, or until-agreement, counted after the opening; default `standard` in `~/.workflow-axa/settings.json` (`spar.default_depth`, set through settings.py); the command overrides it (item 1; D8).
- R6 Stopping: a round makes progress only with new discriminating evidence, a reasoned resolution or a revision that fixes a named weakness; one exchange without progress stops it (stalled); an objection repeated without new grounds counts as no progress; before a round is called stalled, the coordinator checks whether a targeted owner question could unblock it and asks that question instead (D10); evidence nobody can get makes the point unverifiable and sends it to the owner; an open owner decision pauses the dependent debate; until-agreement has no round ceiling and no scheduled pauses, though it still waits for the owner's answers (D6); the owner stops it in plain words, which also cancels running delegates, and a late result can't restart it (item 2).
- R7 Agreement means both debaters judged the same proposal version and its material objections are closed with reasons; switching to the other side's already reviewed proposal needs no extra round; a mix of both is a new version both must review; no forced consensus (items 4, 6).
- R8 The owner is the third participant (D10). Objective technical questions are researched and verified, never asked. When requirements, priorities, trade-offs or acceptable risk are unclear, the owner is asked through grilling instead of the models guessing; no question is asked when evidence already settles the point. Questions reopen when the debate finds a new unknown, and the owner's answers change the positions: each side revises its position or says why the answer doesn't change it (item 5).
- R9 GPT is reached through T3's real capability list and `delegate_task`, a new task per exchange, `task_cancel` on stop. When GPT is unavailable, or the capability check fails, the coordinator says so and asks the owner how to proceed (for example a fresh helper of the host's model, labelled "single model, fresh context, not cross-model"; stop; or try later); it never substitutes another model by itself (D10, superseding D2 and D7). A failed capability check is reported as a failure, never as "GPT absent". With no second agent at all: report that sparring isn't available; one model reviewing itself is never sparring (item 7).
- R10 Any kind of decision: features, changes, bugs, architecture, refactoring, tooling, general technical choices; works with or without a codebase or task (item 10).
- R11 The coordinator is neutral but active: it argues no side, but checks each objection's cited evidence itself before marking it resolved, challenges agreement that rests on no evidence (two "agree"s without reasons are not agreement), and blocks premature agreement by sending the gap back as an objection (D9).
- R12 Foundation checks sort every premise into a verified fact, an unverified assumption or a contradiction. Passing tests show behaviour, not that the architecture is right. Where the premises are weak, the result shows the evidence and the alternatives (refactor first, investigate first, or build on it as is) and recommends one; when that choice changes scope or priorities it is the owner's decision, asked through grilling. Nothing is refactored by /spar (D9, D10).
- R14 Unresolved objections are never dismissed: each is either a technical disagreement (both positions with their evidence go into the result) or a decision that belongs to the owner (asked through grilling) (D10).
- R13 How much research and foundation checking happens follows the decision's complexity and risk, not the chosen debate depth: a quick debate on a risky decision still gets a full foundation check; a deep debate on a simple one doesn't add research it doesn't need (D9).

### What happens

1. **Frame.** The coordinator restates the decision in one sentence, lists 3-6 criteria a good answer must meet, says whether a codebase or task is involved, the depth and who the two debaters are.
2. **Foundations.** It gathers the facts through the reused skills and runs R3's premise check, proportional to the decision.
3. **Owner questions** that block the frame go through grilling first; objective facts are researched instead of asked.
4. **Opening (blind).** Both debaters get the same brief and write a position each: recommendation, alternatives they rejected, foundation weaknesses, their strongest uncertainty.
5. **Exchanges.** Each round both get the other side's latest position and the objection ledger (stable IDs: open, resolved, needs owner, unverifiable). Each returns its strongest objection with evidence, replies to objections against it, and what it changed and why. The coordinator updates the ledger, validates the evidence (R11), sends owner-level points to the owner (R8, R14) and checks R6, with one progress line per round. After an owner answer, both sides get it in the next brief.
6. **End** with one outcome, first match wins: cancelled; unavailable or interrupted (after asking the owner how to proceed); target changed; needs the owner; agreed; stalled (only after checking that no owner question could unblock it); limit reached. Real disagreement may remain at the end; it is reported, never forced into agreement.
7. **Result**: the recommended approach, its evidence (checked, inferred, preference), rejected alternatives with why, risks, required foundation changes, unresolved objections, owner decisions, who debated and whether it was cross-model, and the outcome.
8. **Handoff.** Inside a task: rounds in FINDINGS, owner choices in DECISIONS, the result as the agreement's Approach part (D4), then workflow-clarify's agreement question and the normal route to workflow-specify (HOW, plan, approval view, offer). Without a task: the result stays in the conversation and a later `/workflow` picks it up.

### Changes to the package

- Create `skills/spar/SKILL.md` (the steps above, short), `skills/spar/T3.md` (capability check, delegate brief and ledger formats, cancel; T3-only parts marked; loaded whenever /spar runs) and `skills/spar/agents/openai.yaml` (user-invoked).
- Modify: grilling's "Record answers" (with no task records, or when writes aren't allowed, questions, options, answers and sources stay in the conversation); workflow-clarify's agreement (an optional Approach part from /spar); SPECIALISTS.md (a /spar row: owner-started, recommended for high-stakes choices); settings.py (`spar.default_depth`, read and set, unknown keys kept); `.claude-plugin/plugin.json`, CONTEXT.md, README, docs/ARCHITECTURE.md, docs/RULE-CONTRACTS.md (grilling row, a /spar row), tests/README.md. The CHANGELOG entry and the version bump come with the release, not with this work.
- Remove nothing.

### Stays the same

The hooks, the offer model and approvals; workflow-specify owns HOW, the plan, the approval view and the offer; plan-review and `/interrogate` stay separate (/spar never runs them); only the task owner writes records; debaters only read and return findings.

### Not included

Automatic sparring; a separate SPAR.md; a third judge model; running code or experiments in the debate; prototypes; any change to T3 Code.

### Acceptance

- A1 `/spar` is registered and user-invoked only in both hosts; tools/validate.py passes.
- A2 Tests pin the skill's contract: depth names and counting, the progress rule, the outcome order, the labels, the WHAT/HOW boundary, no implementation, the no-task path, and settings.py reading, setting and defaulting `spar.default_depth`.
- A3 grilling's no-records rule, the SPECIALISTS row and clarify's Approach part are in place and tested.
- A4 A live T3 run on a small real decision shows the frame, a blind opening by a fresh Claude and GPT, at most the chosen number of exchanges, one outcome from the list, and records only inside a task. Until it runs this stays NOT_RUN.
- A5 The tests check the decision process, not predetermined conclusions (D9, D10). Scenarios stage situations where uncertainty, false consensus, stagnation, unresolved objections, missing GPT and a questionable existing architecture can arise, and check observable process: the skill recognises the uncertainty, researches what is objective, asks the owner only relevant questions (and none when evidence settles the point), uses the answers, revises or defends positions with reasons, and reports remaining disagreement. No scenario prescribes the recommended answer.

### Assumptions you can reject

1. The coordinator (the model you're talking to) argues no side; it frames, validates objections and evidence, compares the proposals on the criteria and writes the result (R11).
2. It ships in the next release, 2.9.0-rc.3.


## Agreement 4 additions (agreed 2026-11-17 with offer #3, D17)

The owner's request after pilot run 1 (D16), designed by Claude and GPT-6 Astra (blind C1 and G1, one exchange; both accept G2: FINDINGS S7). Agreement 3 stays; these are added:

- R15 Saving a standalone debate: at its ending (not after the owner's stop), /spar asks once: "Save so /workflow can continue later" · "Save and continue with /workflow now" · "Don't save". Inside an existing task it records as today, with no question.
- R16 Saving creates or reuses the task folder (TASK-FOLDER.md) through record.py with PLAN.md (goal, proposed Approach, outcome, workspace, next safe action; agreement pending, implementation not started), FINDINGS.md (decisive evidence, round outcomes, objections, the exact final versions and who judged them) and DECISIONS.md only when the owner made a material choice. No TODO, no transcript.
- R17 The last message names the saved PLAN, the outcome and `/workflow continue from <path>` (here or in a new session), and says implementation is not approved. "Continue now" starts workflow-clarify on the saved task; it approves nothing. Saving is not agreement.
- R18 The frame line is a required check before any debater starts.
- R19 An owner priority (timing, scope, acceptable risk) is asked as soon as it is named, before launch or after a round, not listed only at the end.
- R20 One complete menu when a debater can't run: same-model helpers, stop, or try again later; a failed check is not "absent".
- R21 At the depth limit with versions nobody judged jointly, offer once: "Check <A> and <B> together (one more exchange, two launches) · Stop here". Never automatic; new revisions after it stay "revised, not jointly checked".
- R22 A credible safety, security or data-loss finding reaches the owner at once with its evidence and uncertainty; the debate pauses only when an owner decision blocks it or continuing would be unsafe.
- R23 Coordinator checks follow the bug recipe's standing diagnostic allowance (every condition), else the hypothesis and the needed check are reported; never a fix.
- R24 Every verdict names the exact position id; the result says what fact would change the recommendation; continuing a saved debate re-checks only premises and objections that changed.
- A6 Live scenarios cover the save question, continuing from a saved task, an early owner question and the extra-exchange offer; scenario results can be recorded as NOT_RUN, OBSERVED, PARTIAL (some checks unmet, named), FAILED or NOT_PROVOKED, each with evidence and the candidate it ran on.

Proposed wording revision (D18, for the owner to confirm at delivery): R16 — a matching task gets a `Spar result <date>` entry in FINDINGS as a proposed revision, not a new PLAN; R20 — the menu's "stop" is "End sparring"; R21 — "Stop here" is "End with this result". Reason: the hook reads "stop" and "Stop here" as the owner stopping the session (Review S5/S6), and rewriting a matching task's PLAN could reset a live checkpoint. Behaviour is unchanged.

## Agreement 5 additions (agreed 2026-11-17 with offer #4, D22)

The owner's request after run 2a (D21): a sparring session must end with a usable result. Designed by Claude and GPT-6 Astra (blind C1 and G1, one exchange; both accept C2 as amended by G2: FINDINGS S11). Agreements 3 and 4 stay; these are added:

- R25 A closure check after every round, including the last: each consequential owner choice is answered, explicitly deferred by the owner, or reported as blocking. Questions go through grilling in batches of at most 4, continued while consequential choices remain; facts are researched and implementation details left to /workflow. Each question says which recommendation its answer changes; recommendations are attributed to the debater who made them, and the coordinator advocates none.
- R26 The final joint check is a closing assessment of fixed, named proposals: each debater accepts or rejects each with reasons and remaining blockers. An amendment stays visible but unreviewed and never replaces the assessed proposal. A failed check gives explicit disagreement and launches nothing.
- R27 The result reports the debate outcome and a handoff state: ready for behaviour agreement, waiting for an owner choice, or requiring evidence. Disagreeing recommendations are attributed with reasons. Only when competing approaches remain and the owner hasn't selected or deferred, and only after the compact outcome is shown, one question offers "Take A's approach (<id>)" · "Take B's approach (<id>)" · "Leave it open for /workflow", each with a neutral one-line summary. A selection is recorded as the owner's selection, never model agreement; dissent and missing evidence stay; leaving it open is an explicit deferral.
- R28 The compact result comes first, in a fixed order: outcome and handoff state; the recommendation (at most 5 bullets) or the competing approaches; blockers (never dropped for length); owner decisions as answered, deferred or blocking; the next step and where it is saved. Outside a task it says "Not saved yet" before the save question; after a save, the PLAN link comes first.
- R29 The frame is a normal line starting with a bold **Spar:** label, shown once (revised only if the target changes); progress lines are plain prose.
- R30 A save keeps the exact final proposal texts with their verdicts in FINDINGS.
- A7 Pilots avoid the duplicate-skill block only with the owner's OK for any plugin change; a CLI pilot states which debaters ran and any loss of cross-model coverage.

## Agreement 6: rebuild around SPAR.md (agreed 2026-11-17 with offer #5, D25)

The owner's request (D24): "the best general sparring skill there is: sparring with agents about an idea to get it into reality", with a SPAR.md that structures what was sparred and a question whether to turn it into a workflow plan. Designed by Claude and GPT-6 Astra (blind C1 and G1, one exchange; both accept C2 as amended by G2: FINDINGS S14). It replaces agreements 3-5 where they conflict (the round-and-ledger machinery, saving into PLAN/FINDINGS/DECISIONS, the neutral-only coordinator, the closing-assessment ceremony, the D18 and D19 labels); what they got right stays.

- R31 SPAR.md is the record: `docs/plans/<date>-<topic>/SPAR.md` (a folder the approval hook already treats as records, and the place PLAN.md joins if the owner turns it into a plan); inside a task, that task's SPAR.md. Saved automatically when the owner starts /spar (D24); "conversation only" keeps it in the conversation. Updated after each meaningful step: an owner decision, changed evidence, each exchange, the ending.
- R32 Sections, scaled to the discussion ("none identified" is fine; never a transcript): Current position (the idea, the recommendation, what the owner chose versus what the agents recommend, the next move) · Intent and boundaries (desired outcome, constraints, success criteria) · Evidence (facts with sources, assumptions, contradictions) · Options considered (each with its strongest honest case and objection) · What changed our thinking · Owner decisions · Open questions and dissent (each with what would resolve it) · Handoff brief.
- R33 Flow: understand (the idea in the owner's words, the desired outcome, what makes it hard, what a useful outcome today is) → explore (independent openings; each challenges the framing: doing nothing, a simpler way, whether the need is real) → challenge (exchanges on the few disagreements that could change the outcome; a pre-mortem when useful) → decide (the uncertainty most likely to change the decision, the cheapest credible test, the observation that would change it; or "no material uncertainty").
- R34 The owner is brought in when an answer changes the direction: the trade-off shown, a recommendation with reasons, alternatives invited; no questionnaire at the end. Consequential choices end answered, deferred or blocking.
- R35 The coordinator keeps the working proposal and may give its own recommendation (D24). Labels stay separate: coordinator recommendation, each debater's assessment, owner decision. Debaters assess a synthesis when the budget allows; an unreviewed one stays labelled unreviewed; objections stay visible.
- R36 Effort is a budget (quick, normal, thorough) with an explicit launch limit. Before spending more, say which open issue it would settle. A spent budget gives a partial conclusion and a recommended next move.
- R37 Claude and GPT cross-model by default (T3.md's debaters and menu stay). With one model: the owner and the assistant spar, the assistant's self-critique labelled; optional same-model helpers are never called cross-model.
- R38 It ends when the owner can choose a next move: proceed, investigate, defer or abandon. Dissent may remain; models never fake agreement. A cancel stops and asks nothing more.
- R39 The conclusion comes first (in T3 Code with `send_to_user`), then one question: "Turn this into a workflow plan" · "Investigate <the uncertainty> first" (prepares a bounded investigation brief; running it needs its own approval) · "Continue sparring" · "Leave it here". A plan means /workflow with PLAN.md next to SPAR.md, its Approach linking the SPAR.md revision; assumptions never become requirements; it authorizes planning only.
- R40 Kept: blind openings; evidence checked before an objection counts as settled; a safety finding told at once; the frame as one plain line; cancel; no implementation, tickets or offers from /spar.
- Revision of R31 and R39 (D26, proposed with offer #6): /spar is a separate skill, not part of the workflow. SPAR.md lives in `docs/spar/<date>-<topic>/SPAR.md`, inside a task too (the task's FINDINGS links it); the approval hook counts `docs/spar/<folder>/SPAR.md` (that file name only) as a record. "Turn this into a workflow plan" starts a normal task in `docs/plans/` whose PLAN links the SPAR.md revision. Effort names follow R36 (quick, normal, thorough; standard and deep accepted as the old names).
- Revision of R31 (D28, offer #7): keeping SPAR.md is the owner's choice, asked once at the start ("Keep a SPAR.md" · "Conversation only") unless the command says which; a conversation-only spar writes SPAR.md only when the owner picks "Turn this into a workflow plan". This replaces "saved automatically" above.
- Proposed wording revision (D31, for the owner to confirm at delivery; from review S16/V20): during a workflow task, "Turn this into a workflow plan" continues that task's workflow-clarify with the Handoff brief and creates no new task; an agreed task's checkpoint changes only after that choice (proposed revision pending, previous next step kept). Outside a task it starts a new task in docs/plans/ as above.
- A8 Live: a T6 run on the rebuilt skill shows SPAR.md, when kept, built as it goes, the owner asked only when direction changes, the conclusion before the question, and the four-way handoff.

## Agreement 7 additions (agreed 2026-11-17, D35)

After run 4 (D34), designed by Claude and GPT-6.1 Sol (FINDINGS S21). Agreement 6 stays; these are added or replace:

- R41 Start card: before any launch, one question card asks only what the command did not state: effort (Quick, up to 6 launches · Normal, up to 10 · Thorough, up to 14 · Until agreement), the debaters (a recommended pair from two different makers among the models actually available, or choose A and B), and the record (Keep a SPAR.md · Conversation only). The saved default effort is preselected, never used silently. No card when the command states everything.
- R42 Until agreement: runs until both debaters accept the same proposal, or deadlock (two full rounds with nothing material new: evidence, argument or position), or the owner's launch cap, chosen each time (20 · 30 · 50 or the owner's number, at least 6). The three endings are reported as themselves. Two launches stay reserved for the final acceptance check; retries and replacements count; the cap is never passed without the owner's OK. A cap limits calls, not money.
- R43 Agreed means both debaters accepted the exact text of the same proposal id without conditions or blockers. "Accept with amendments" rejects that version. Any later edit voids acceptance and is labelled an unreviewed coordinator synthesis; the last jointly accepted version is kept. Applies in every effort. A replacement debater judges the current text itself.
- R44 Debater briefs say that justified disagreement is success and that a changed position needs its reason.

## Revision history

- Agreement 1 (2026-11-17, asked, not agreed) was replaced by agreement 2 after the owner's revision 2; its design and spar rounds are FINDINGS S1-S2 and D1-D4.
