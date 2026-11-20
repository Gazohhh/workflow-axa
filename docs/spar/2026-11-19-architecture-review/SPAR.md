# Spar: workflow-axa architecture review (routing, terms, instructions, structure; /spar first)

## Current position
Revision 9, 2026-11-20 (baseline replay done, $7.43). Revision 8, 2026-11-19. Point 12 (show what every label means) added after an extra round; all 14 launches used. Agreed by both debaters and the owner: S3 (Handoff brief below). The owner's verdict was confirmed after the owner had read all of S3. 12 of 14 launches used. The owner chose "Investigate first": a baseline replay on 3972094 with a $20 total cap, then planning. Next move: the owner confirms the investigation brief below, and the run starts.

## Intent and boundaries
The owner's words: review "routing, terminology, instructions, and structure"; "Think like the authors, especially pstack ... rather than blindly copying"; "Preserve what already works, including our existing skills and engineering safeguards. Do not propose changes simply for the sake of improvement." On /spar: "it works great but i think we need to make some changes to it ... its good but it feels a bit off."

Constraints:
- The review reads worktree D:/workflow-axa-spar (branch spar/architecture-review, commit 3972094). The main working tree is never modified.
- Nothing is implemented until the owner approves a plan.
- Prefer simplifying routing and reusing existing skills over new abstractions. Keep useful terms unless there is a demonstrated reason to change them.

Success criteria (proposed to the owner, no objection raised):
1. Each recommendation has a problem, evidence (file and line, plus the outside source), a solution, a trade-off and a test.
2. Each is labelled measurable or opinion.
3. Nothing changes just to change. "Keep" is a real outcome.
4. /spar gets a specific diagnosis of what feels off.
5. One test plan runs the same realistic cases before and after: routing accuracy, unnecessary skill loading, missed safeguards and regressions.

## Evidence
Facts:
- Skills: 22, registered in .claude-plugin/plugin.json. Four are user-invoked only (interrogate, no-comments, wait-what, spar).
- Router `skills/workflow/SKILL.md` is 64 lines. The workflow folder holds 25 reference .md files (1,011 lines), plus flows/, scripts/, templates/ and agents/.
- Description lengths: 118 to 430 characters. The workflow router's description is 430.
- Always-on load each session is about 3,450 words: ~/.claude/CLAUDE.md 616, START 583, CORE 702, ARTIFACTS 886, AGENTS.md 662. Hooks: approval.py, phase_gate.py, read_evidence.py, duplicate_skills.py.
- /spar is 3,574 words in three files (SKILL 1,691, T3 1,171, SPAR-FILE 712). If a run reads every reference, it reads about 10,600 words.
- /spar SKILL.md sits at 1,691 words against a 1,700 limit in tests/test_spar.py:188. That limit was raised once already for the owner-in-loop rules.
- /spar started at 65 lines (bcb76ec, 2026-11-17) and has had four commits since. The owner-in-loop change (docs/plans/2026-11-17-spar-owner-in-loop) added rules R1 to R8. tests/test_spar.py (379 lines) pins wording for rule groups up to at least R44.
- The owner asked for owner-in-the-loop sparring (D1) and accepted the change as is (D4). The owner's final verdict on an accepted proposal has never been tested live.
- External research, with sources: scratchpad spar-evidence/RESEARCH.md. pstack routes through one user-invoked hub with 8-25-line playbooks and a principles index. Its debate-like skills (/arena, /interrogate) end with the parent picking against a rubric, or keeping only findings it reproduced, never with a consensus vote. Pocock has no debate skill, rejected a /red-team skill and requires an "Observed failure" for changes.

Assumptions:
- The owner's feeling that /spar is "off" has a cause the files show. The owner has not yet said what it is.
- The 2.10.0 version bump in the main tree doesn't affect the skills under review.

Contradictions: none confirmed yet.

## Options considered
- **A1 (GPT-6.2 Sol): keep the architecture, fix /spar's ending first.** Diagnosis: /spar has two competing finish lines. Its stated job is to help the owner choose, but most of its detail pushes towards three parties accepting identical text, so a debate becomes a ratification exercise. Proposals:
  - (1) Put the bounded ending first: compare options against the criteria, name the objection that could change the choice, and give its cheapest check. Run a synthesis check only when it resolves something. Keep the exact-text verdict, and keep until agreement as an opt-in.
  - (2) Keep every owner-in-the-loop rule, but load T3.md and SPAR-FILE.md details only when their branch is reached.
  - (3) Change package routing only where a replay shows a misroute. The first candidate is a UI-facing migration that fits both the ui and migration recipes.
  - Doing nothing wins if the replays show no problem.
  - Strongest case: it changes the least and protects what the owner asked for.
  - Strongest objection: it gives no concrete test of whether the output is better, only that it is cheaper.
- **B1 (Claude Opus 5.5): change how /spar ends and how it is graded; package changes only small and evidence-gated.** Same diagnosis: the win condition is consensus and launch arithmetic, while the agreed success criteria never come back. The result is agreed but not sharp. Proposals:
  - (1) Every brief returns a verdict per success criterion, and the conclusion opens with a criterion × option table.
  - (2) Keep three-way agreement, but drop "any later edit voids acceptance" in favour of "accept, or name a blocker against the criteria".
  - (3) Fewer budget forms. Drop the standard/deep aliases and the cap tiers, or use a small counter script.
  - (4) Replace wording-pinning tests with behavioural cases.
  - (5) Debaters inherit global "MUST invoke a skill" and readiness-question instructions that contradict their brief. Start them with a reduced context or an explicit override line.
  - Package: keep the router, INDEX and hooks; measure what a real task reads before cutting; possibly load ARTIFACTS.md on demand; narrow the router's greedy description.
  - Strongest case: it targets the quality of the output, not just its cost.
  - Strongest objection: adding criterion grading adds text to a skill already at its word cap.
- **Coordinator checks:**
  - Confirmed: skills/workflow/*.md is 18,660 words; workflow/SKILL.md is 1,472 words; interrogate also briefs two cross-model adversaries (skills/interrogate/SKILL.md:24).
  - Corrected: skills/workflow/ARTIFACTS.md is the *source* that global_policy.py installs as the global ARTIFACTS.md, not an independent duplicate. The real cost is that it loads globally every session.
  - Not checked yet: whether the debaters' inherited context actually changed their behaviour.

## What changed our thinking
- Owner at checkpoint (a): all four symptoms are real, and agreement is about the idea. Effect: both debaters drop exact-text ratification.
  - A moved from "keep the exact-text verdict" to "remove exact-text ratification".
  - B moved from "keep three-way exact-text agreement" to "decision points with verbatim verdicts".
- Exchange 1, areas of convergence:
  - A bounded spar ends when the owner can choose, and dissent is a valid ending.
  - Merge the start card with the pre-opening grilling.
  - Keep checkpoint (a). Its answer produced this spar's two most important decisions.
  - The `research` specialist, or the coordinator's own reading, becomes an explicit evidence step before the openings.
  - Show the owner plain titles. Ids stay in the record.
  - Replace the exact-text test pins (tests/test_spar.py:240-246) with behaviour cases. Keep the control-intent check.
  - Package-level changes wait for a failing replay.
- Exchange 1, positions A2 and B2: see the conversation. Coordinator checks:
  - A's false-agreement evidence is confirmed: tests/behavioral/spar.json:53, "the outcome line said both models agree before either saw S3".
  - B's test pins are confirmed.
  - B corrected its own citation: the conclusion order is SPAR-FILE.md:57-64, not 148-153.

- Exchange 2, positions A3 and B3: the debaters converged. A adopted quoted per-point verdicts, removed the separate synthesis template and supports the override line now, because the collision was observed. B kept the frame as a receipt, cut the criteria table to the rows that differ, and moved re-review into the exchange brief. What remains: A lets the coordinator report agreement when the quotes plainly match, and asks for confirmation only when interpretation is needed; B says the coordinator only ever shows the quotes. Coordinator's synthesis S1 (unreviewed) merges the two as eleven decision points (P1-P11); the text is kept beside this record's research notes and is checked in exchange 3.

- Exchange 3, verdicts on S1:
  - Both agreed with P1, P3, P4, P5 and P7.
  - P2: A wanted interpretive matching; B narrowed it to a mechanical "both agree" label on identical point text.
  - P6: B narrowed to one change-my-mind line on the most contested claim; A asked to keep the settings aliases (settings.py:36).
  - P8: both say the sizes are estimates, not gates.
  - P9: A says update docs/RULE-CONTRACTS.md, which still states the exact-text rule.
  - P10 (both said mis-framed):
    - A corrected the ARTIFACTS loading paths: an @import on Claude, a read before output on Codex (global_policy.py:70).
    - B widened always-on load to START, CORE and ARTIFACTS (about 2,170 words a session).
    - B added a package-wide inventory of tests that pin prose (test_verify_skills.py has 266 checks).
  - P11: A added traces and a seeded case with incompatible conditions; B added an unrelated-project case.
- Coordinator checks:
  - Confirmed: settings.py:36, global_policy.py:70, RULE-CONTRACTS.md, the 266 checks.
  - Corrected B: tests/behavioral/spar.json already exists (482 lines).
- S2 merges all of this and goes to exchange 4.
- Exchange 4, verdicts on S2:
  - Both agreed with P1, P3-P5, P6b, P7-P9, P10a, P10b and P11.
  - On P2, A requires the label to also need the same conditions, and B requires a restatement to stay inside the cap.
  - On P6a, A wants the change-my-mind line only for a live disagreement; B agreed with it as written.
  - B fixed a citation: the line is global_policy.py:73, not :70.
- S3 adds these amendments, marked [S3]. S3 goes to a final check (launches 11-12) to settle P2 and P6a.

- Exchange 5 (synthesis check): both debaters agreed with S3 and every point in it. Both read the owner's pending "skip setting for checkpoint (a)" as "skip candidate (a)", so that question goes to the owner again in plain words.

Settled by exchange 2 (these were open after exchange 1):
- The synthesis brief: remove it entirely (B), or keep a re-review for material amendments (A)?
- The conclusion: a full criterion × option table (B), or criteria used to surface the decisive trade-off first (A)?
- The frame line: fold it into the card (B), or keep it as a no-reply receipt (A)?
- The override line in debater briefs: now (B), or after counting the effect (A)?

## Owner decisions
- Effort thorough (14 launches); debaters GPT-6.2 Sol (A) vs Claude Opus 5.5 (B); SPAR.md kept in the worktree; baseline committed 3972094 with the uncommitted diff noted (start card, 2026-11-19).
- Success criteria: proposed and not objected to (start card message). Not yet explicitly confirmed.
- What feels off about /spar (checkpoint (a), answered): all four. Too much ceremony and too many stops; a bland agreed result; hard to follow; the debate lacks real evidence.
- Ending (checkpoint (a), answered, binding): agreement is about the idea, not string matching. In the owner's words: "the reason of a spar is not aiming same text ... its a sparring session ... normally you do this with 1 agent now the advantage in t3 is i can use multi agents to talk with each other to disagree and agree."
- Coordinator's answer to "am I correct?": yes on the substance. One caveat goes to the debaters: exact text was introduced to stop the coordinator from paraphrasing a disagreement into a fake agreement. Whatever replaces it must still prevent that.

- Verdict on S3: accepted (question tool, 2026-11-19). It was first given after only part 2 had been shown, because part 1 failed to send (over the message limit); the coordinator disclosed this and showed part 1, and the owner then confirmed it.
- Until agreement: keep, slimmed to one opt-in rule.
- Global always-on files (START, CORE, ARTIFACTS): in scope, replay-gated; every change needs the owner's explicit approval before install.
- Next move: Investigate first. Spending cap for the replay: $20 in total.
- Added by the owner after the verdict (binding, 2026-11-19): never ask "do you agree with S4?" without the content. Every question shows, in the same message and right before the question, the full text of what is being asked about, in plain words. An id may follow only as a reference. Added to the plan as point 12. The debaters didn't raise it: P6a covered titles in progress messages, not questions. This spar broke the rule once, when the verdict question pointed to S3 while part 1 of S3 had failed to send. Test: every owner question in the replay traces is scored on whether its content was visible in that message, and the target is 100%.
- The owner widened point 12 (binding, 2026-11-19): "i want to see what the reference is when being asked or referred to". This covers every message, not only questions: whenever a message refers to something by a label (S4, P2, D1, a test name, an option letter from an earlier message), it shows what that label means right there. The owner asked for a debate round on it, then the full plan again. That round uses launches 13-14.
- Owner answers, 2026-11-19 ("1 = a and 2 a"):
  - Commit messages, pull-request text and HTML reports count as owner-facing, so the label rule applies to them.
  - There is no setting to skip the pause after the openings for now.
- Recipes vs pstack playbooks (coordinator analysis, not debated): our recipes are playbooks already. workflow-execute/SKILL.md:23 copies the recipe steps word for word into the todo list, and flows/TEMPLATE.md:13 says the same. Recommendation: keep "recipe" as the term and add no new recipes. The UI-facing migration replay case tests the recipe choice.
- Superseded by the two answers above: "yes" on the start card accepts the proposed criteria (recommended: yes); a setting to skip checkpoint (a) (recommended: no setting for now). Both debaters misread this second question as "skip candidate (a)", so it will be asked again in plain words.


Point 12, after exchange 6 (launches 13-14; all 14 used). This is the coordinator's summary of two converging answers, not separately checked by the debaters:
- One rule in skills/workflow/WRITING.md, "Chat replies" (the one owner of the shared writing rules, already read by the router, /spar and deliver): every owner-facing message stands on its own. A label comes after its plain meaning in the same message. A label shown only in an earlier message, or in a part that failed to send, counts as unseen.
- grilling/SKILL.md:54 and spar/SPAR-FILE.md:62 point to that rule instead of restating it. The pin at tests/test_owner_questions.py:70 moves with it.
- The WRITING.md:135 example is fixed so the meaning comes first.
- No hook: a pattern can't judge meaning, and offers.py:64-99 already rejects an offer that starts with a code.
- Long content is sent in parts at section boundaries, each part checked as sent, and no question opens until every part has arrived. A failed send has a detectable error (seen in this spar: "at most 4000"). A verdict on a whole plan shows the whole plan; elsewhere a one-line meaning per label is enough.
- Bare labels are fine inside records, files and agent briefs.
- Tests:
  - Replay traces: every label in owner-facing text is graded for visible meaning, target 100%.
  - A deterministic check that no question opens after a failed send.
  - A new spar case where part of the conclusion fails to send.
- Owner-only: do commit or pull-request text and HTML reports count as owner-facing? (Recommended: yes.)

## Open questions and dissent
- Dissent: none on S3.
- The uncertainty most likely to change the decision: whether the four symptoms come from the consensus mechanics (P1) or mostly from host delivery and stop cadence. Cheapest test: the baseline spar cases in the investigation brief, scored on stops, fake-consensus and blind readability.

## Investigation brief (Investigate first; running it needs the owner's go)
Goal: before-numbers on baseline 3972094 for the S3 test plan (P11), so planning works from measurements, not opinion. The candidate does not exist yet. The same cases rerun on it after the plan, under a separate budget.

Cost: at most $20 in total, including retries. `--max-budget-usd` is set per run, and every run is logged with its cost. Stop at the cap.

How:
- Follow the live-pilot recipe: a release ZIP of 3972094 (`tools/build_release.py`), a separate plugin copy, and disposable fixture projects from `tools/create_fixture.py` outside any repository.
- Run `claude -p` with `--plugin-dir` and `--add-dir` for the copy, `--setting-sources project,local`, and an allow-list that denies git writes and installs. Traces are captured as stream-json.
- Staged owner replies use `--resume`. Evaluator expectations stay outside the fixture.
- Evidence goes to `D:/workflow-axa-spar/.artifacts/2026-11-19-architecture-review/` (git-ignored), keeping one trace per case. Fixtures and plugin copies are disposable once scored.

Cases, Claude host:
1. R1 explain-only.
2. R2 a one-ticket visible fix.
3. R3 a UI-facing saved-data migration (P10b(a)).
4. R4 an ordinary request in an unrelated project, which measures the always-on load: words loaded before the first useful action, and unrelated rules-setup questions (P10b(c)).
5. R5 a narrowed approval on resume.
6. Spar, quick effort, with scripted owner replies:
   - S-a a contested design with persistent dissent;
   - S-b a seeded disagreement plus two "agree"s with incompatible conditions;
   - S-c an idea with no code.

Codex runs R1 and R4 only if budget remains.

Known limit: cross-model /spar needs T3's `delegate_task`. Under `claude -p` the spar falls back to the labelled single-model route. S-a to S-c are therefore run as T3 threads with the same models as this spar, or labelled single-model if T3 can't be scripted.

Measures (P11): the recipe and phase chosen, skills loaded, files and words read, blocking stops, launches, words shown to the owner, decisive claims verified, the fake-consensus count, debaters' unrelated skill calls or questions, and safeguard regressions.

Which result changes what:
- R1-R3 and R5 route correctly with no extra loads: drop candidates P10b(a) and (b).
- A misroute: plan only that fix.
- R4 shows unrelated rules-setup questions, or global text that never affects the answer: plan a P10b(c) change for the owner's approval.
- Spar baselines become the before-numbers for P1-P7. A fake consensus, or more than 2 blocking stops before the first exchange, confirms the diagnosis directly.

- How "agreed on the idea" is shown without allowing fake consensus.

## Baseline replay results (2026-11-20, commit 3972094, Claude Code 2.1.327, Opus 5.5)
Spent: $7.43 of the $20 cap. Traces are in D:/workflow-axa-spar/.artifacts/2026-11-19-architecture-review/ (one .jsonl per run). The fixtures and plugin copy in D:/axa-replay-2026-11-19/ are kept for the after-run, then removed. Their recipe: create_fixture.py clean or answered-task, plus a saved-history file for case 3.

Routing (plugin only, project and local settings):
- Explain-only: no skill loaded, 5 project files read, nothing written, $0.37. Pass.
- Visible separator change: the feature recipe, then clarify, specify and a one-ticket offer; no code changed before approval, $0.74. Pass.
- History screen with saved data: the feature recipe plus the Compatibility modifier. It asked whether to convert at display time or rewrite the saved file, so the migration safety question was asked. $0.57. Not a misroute: suspect (a) is not confirmed.
- A changed rule on a resumed approved task: recorded as a revision with a new offer; no code changed, $0.99. Pass.
- Unrelated question with the owner's real setup: a correct answer, no workflow, no rules questions, $1.60.
  - First-turn context: 135,573 tokens with the real setup; 39,670 with workflow-axa only; 37,955 with no plugin ($0.33 for the same question).
  - So workflow-axa itself adds about 1,700 tokens; its global rules files add roughly 4,000 more.
  - About 90,000 tokens come from the rest of the user-level setup: 13 plugins and 117 skills.
  - Suspect (b), an over-broad router, did not fire. Suspect (c) is mostly not workflow-axa's text.

Spar (quick effort, Claude CLI, so single-model helpers):
- Case A, formatter ownership, $1.24: 3 blocking stops before the first debate step (start card, the pause after the openings, an owner choice), 4 in all. The helpers gave the same recommendation from their openings, so the spar went straight to one synthesis check. Exact-text acceptance; no fake consensus.
- Case B, live scores with no code, $1.59: 3 stops before the exchange, 5 in all.
  - The helpers agreed at the openings.
  - After owner pushback they held "no WebSockets" with reasons. They switched "later" to "now" on the owner's unchecked claim "users keep asking"; the rule says owner facts are checked like any other.
  - The coordinator corrected a helper claim but labelled the correction unchecked, and raised a security point unprompted.
- Labels: ids came with their meaning, except one "S1 is agreed" placed before its meaning in the same message. Under T3 in this spar there was one real failure: the verdict was asked about S3 while part of S3 had failed to send.
- Debater skill calls: 0 under the CLI, where the user-level hooks were not loaded. The inherited-instruction clash was reported only under T3, and is not measured here.

What this changes in the plan:
- Drop suspects (a) and (b) for now.
- Reframe (c): workflow-axa's always-on share is small. The large cost is the user's overall plugin setup, which is an owner choice outside this package.
- For the start: the card already merges the setup questions. The extra stops come from owner choices asked one at a time right after the pause. Fold any choice that can be asked at the pause into the same message.
- New: single-model helpers converge at once (bland), while the cross-model route disagreed and moved over 4 rounds. When only one model is available, say so on the start card.
- New: mark owner factual claims as unverified in briefs, so debaters check them instead of adopting them.

Not run: Codex; a scripted cross-model T3 replay (this spar is the only cross-model data point: 2 stops before the first exchange); the blind readability preference, which needs the after-run.

## Handoff brief
The proposal both debaters accepted, in full (S3):

Coordinator's synthesis S3 (unreviewed). It is S2 with the exchange-4 amendments in P2, P6a, P9, P10b and P11 (marked [S3]). Every other point is word for word as in S2, which both debaters accepted.

P1 Diagnosis. Unchanged. Its effect on blandness is a diagnosis to test in the replay.

P2 Agreement [S3]. Decision points are taken from "the disagreements that could change the outcome". Each debater answers each point with agree, disagree or mis-framed, and may split a point or add one, plus one line in its own words. The conclusion quotes both lines verbatim.
- The coordinator adds the label "both debaters agree" only when both answered "agree" to the identical point text and neither quote adds a condition the other does not state. In every other case it shows the quotes without a label.
- When the quotes look compatible but the verdicts or conditions differ, the coordinator may restate the point and send it back to both. A restatement uses an exchange the budget or cap already allows; when none remains, the point stays unresolved.
- The owner's verdict is separate and always explicit.
- Removed: exact-text acceptance, "an accept with amendments is a reject", "any later edit voids the acceptance", the separate synthesis brief and the S-ids.

P3 Ending. Unchanged. Dissent, cancel and provider failure stay distinct endings. If the owner keeps until agreement, deadlock and the cap are reported separately.

P4 Stops. Unchanged. 3 to 2 blocking stops is scored on a case that actually needs setup.

P5 Evidence [changed]. Unchanged, except that the evidence note goes in the existing record (SPAR.md, or the chat when conversation-only), not in a new file. "Investigate first" names the observation that would change the decision and the cheapest way to get it.

P6a Readability shown to the owner [changed].
- Plain titles; ids only in the record.
- Briefs carry each side's current claim, strongest objection and source.
- Each position ends with one "what would change my mind" line for a live disagreement, or "none" when nothing it disputes is still open. [S3]
- The conclusion leads with the decisive trade-off. It uses a table only when several criteria distinguish the options; one differing criterion gets one sentence.
- One launch rule. The skill text drops the standard/deep aliases and the cap tiers.

P6b Input compatibility [new split]. settings.py keeps accepting the old words standard and deep (skills/workflow/scripts/settings.py:36 OLD_DEPTHS).

P7 Debater brief. Unchanged. T3.md:47,61,81 already say "Role... Write nothing. Start no agents."; the brief adds "this brief is your whole task: invoke no skills, ask no one".

P8 Size [changed]. Estimates only: SKILL.md about 1,050 words, T3.md 700-750, SPAR-FILE.md 550-600. Size-test ceilings are set to the sizes actually reached once the behaviour cases pass, not to these estimates.

P9 Tests [changed].
- Replace the wording pins of removed rules (tests/test_spar.py:240-246 and similar) with behaviour cases in the existing tests/behavioral/spar.json (482 lines, which already exists).
- Keep the control-intent and safety checks, and test_r44 (briefs reward justified disagreement) across the surviving briefs. [S3]
- Update the /spar row in docs/RULE-CONTRACTS.md, which still states "agreement only when both accept the exact text".
- Size ceilings follow P8.

P10a Package: keep [split]. Keep the router, the phases and their table, flows/INDEX.md, the terms (CONTEXT.md, with no GLOSSARY rename: no demonstrated failure), the hooks and the approval gates. Nothing is removed at package level.

P10b Package: candidates gated on a failing replay [changed]. None changes without a failing replay and, where it applies, the owner's approval.
- (a) A UI-facing saved-data migration matches both the ui and migration recipes.
- (b) The router description is broad (skills/workflow/SKILL.md:3, 430 characters).
- (c) Always-on load:
  - Every Claude session loads about 2,170 words through the global CLAUDE.md: START 583, CORE 702 and ARTIFACTS 886. ARTIFACTS arrives as an @import (global_policy.py:73) [S3]; Codex reads it only before output.
  - Per-task reads across skills/workflow/*.md total 18,660 words.
  - Global changes need explicit owner approval.
- (d) Package-wide prose pins: tests/test_verify_skills.py alone has 266 has/assertIn checks. Inventory which ones guard removable prose rather than behaviour, and replace them only where a behaviour case exists.

P11 Test plan [changed]. Run the same cases on 3972094 and on the candidate, with the same models and scripted owner input.
- Spar cases: this review, a naming decision, a contested design, an idea with no code, persistent dissent, a seeded disagreement that must surface, two "agree" verdicts with incompatible conditions (must not be labelled agreed), a restatement attempted at the last exchange (must stay unresolved) [S3], convergence at the cap, provider failure and cancel.
- Routing cases: explain-only, a one-ticket visible fix, the UI-facing migration, narrowed approval on resume, and an ordinary non-workflow request in an unrelated project (it measures the always-on load: unrelated rules-setup questions and words read before the first useful action).
- Measured from traces on each host: the recipe and phase chosen, the skills resolved, files and words read, blocking stops, launches, words shown to the owner, decisive claims verified, the fake-consensus count (must be 0), unrelated skill calls or questions by debaters, and safeguard regressions (must be 0).
- Readability is judged by blind owner preference, which is labelled opinion.
- Paid host runs need an owner spending cap (AGENTS.md).
- Adopt only with zero safeguard regressions and an observable gain.

Boundaries: planning only. Every assumption above stays an assumption until the replay. Changes to global files (START, CORE, ARTIFACTS) and paid replay runs each need the owner's explicit approval and a spending cap.
