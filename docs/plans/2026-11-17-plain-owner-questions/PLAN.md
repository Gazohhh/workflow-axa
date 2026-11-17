# Owner questions in plain words, and unslopped records

## Current checkpoint
- Updated / phase: 2026-11-17; waiting — starts after the rc.3 merge (docs/plans/2026-11-17-rc3-merge) is verified
- Rules: READY (AGENTS.md project rules; shared START, CORE, READINESS)
- Recipe: feature; modifiers none — changes how skills word what the owner reads and decides; scope: the task; classification question: not asked
- Agreement (gate one): not started (workflow-clarify)
- Offer: none
- Implementation: not started
- Verification / owner acceptance: not run
- Blockers: the merge comes first (owner, D1)
- Changed files: none. Worktree: D:\workflow-axa-redesign

## Goal

The owner, 2026-11-17, after run 5:

> "Some questions I get are like: 'Do you accept S2 with the decisions of T2?' I have no idea what that is. I need to see what S2 and T2 are; I need this to be simplified. The tickets are made, yes, but present it to me humanly without talking in tickets. You can of course refer to the ticket, but when it comes to me making a decision based on that, I don't want to see that the reference is important, but plain English: unslop it, no slop. Also the writing in tickets and documents all needs to be unslopped, and the SPAR.md as well. Also check that it uses the grilling skill: it asked me no questions besides the spar questions, and I see decisions for me not in grilling style."

And: "If you could do this test yourself internally after we are done merging, because the sparring itself looks fine."

## What is known

- Run 5 (thread b9817ad7) ended with five owner decisions written as "O1-O5" whose meaning depended on ids (D31, T6, S2, C-OFFER-8). The same five, asked again in plain grilling style, were answered at once (docs/plans/2026-11-17-rc3-merge D1-D4).
- pstack's live runs: L5 failed (the Unslop check was never reached) and L6 was partial (a small request skipped the safety assumptions). The owner chose to fix both before rc.3 (rc3-merge D4). L5 overlaps with this request: Unslop has to reach what the owner reads.
- WRITING.md "Unslop" names the texts it runs on; run 5's debaters disagreed on whether a kept SPAR.md and the /spar conclusion are covered (SPAR.md dissent). The owner says they are.
- Run 5's F5 (an Unslop review of /spar's own text) moves here.

## To settle in clarify

Every question the owner must answer, in every skill (offers, grilling, /spar's conclusion and handoff, delivery): plain words first, what happens with each answer, ids only as a reference after the meaning. Where the grilling format is required and where /spar must route owner decisions through it. Which records Unslop runs on (tickets, PLAN, FINDINGS, DECISIONS, SPAR.md). How to fix L5 and L6. The internal test: a run, done by the agent, that shows a decision question with no unexplained id and in grilling form.
