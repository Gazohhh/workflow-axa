# /spar with the owner in the loop

## Current checkpoint
- Updated / phase: 2026-11-18; T1 verified and pushed; T2 partial (V3); waiting for the owner on the verdict checkpoint and acceptance
- Rules: READY (AGENTS.md project rules; shared START, CORE, READINESS)
- Recipe: feature; modifiers none. It changes how /spar involves the owner during a spar. Scope: the task. Classification question: not asked
- Agreement (gate one): agreed. The plan S2 was accepted word for word by GPT-6.2 Sol (FINDINGS S1); the owner approved it with offer #1 (D2)
- Offer: #1 approved (owner, question tool, 2026-11-17); approving it also approved the plan
- Implementation: T1 verified (FINDINGS V1, V2; review S2 passed). T2 live check run (V3): four checks pass, the verdict checkpoint was not provoked; $3.89 of $5
- Verification / owner acceptance: full suite 1543 OK, validate PASS; live check partial (V3); owner acceptance not given
- Blockers: none
- Changed files: skills/spar/SKILL.md, T3.md, SPAR-FILE.md; tests/test_spar.py, tests/behavioral/spar.json, tests/README.md. Work happens on D:\workflow-axa main

## Goal

The owner, 2026-11-17:

> "So the spar skill does it use the grilling because inside spar i need to also give my feedback right instead of only relying on both models right? ... now i feel like the sparring is only between the agents without any feedback the spar session is based on also on feedback. ... there are normally rules for sparring right now its just 2 agents talking and giving you a plan. But it also needs to use the grilling skill to grill where needed right not just make decisions all on its own?"

On how often to stop: "depends on the input ... there is no fixed amount ... There should not be a limit to this." On who agrees: follow the protocol; "sparring between AI models, different models and you and your input that can be pushed back as well if not agreed or incorrect".

## What changes for the owner

- Before the models start, you are asked only what is still unclear about your goal, success, limits and trade-offs.
- After the opening positions the spar always stops: you read both positions and the disagreement that matters most, and give your view or say "no feedback". It waits for you.
- Whenever a choice only you can make comes up, you are asked right then, as a numbered grilling question. There is no fixed number of these stops.
- Your decisions bind both models. Your opinions and claims are challenged like any other position: the models may push back with reasons, and a wrong fact is corrected with evidence.
- "Agreed" means both models and you accept the exact same text, which you see in full first. You can also overrule both; their objection is recorded.

## Agreement

Agreed design S2 (FINDINGS S1), with the owner's answers D1:

- R1 Rules of the spar: one short section in skills/spar/SKILL.md. The owner decides and judges; the debaters argue; the coordinator moderates, checks evidence and never decides for the owner. The launch rule: no next launch whose brief depends on an open owner choice. Keep the focus on the disagreements that could change the outcome and "a changed position needs its reason". Exchange briefs (T3.md) ask each debater to state the strongest opposing argument on a disputed point before rebutting it.
- R2 Before the openings: grilling's frontier for the unsettled choices that shape the opening brief (outcome, success criteria, boundaries, trade-offs). A settled brief needs zero questions. "No interview": show labelled options and leave them open.
- R3 Owner checkpoints: (a) after the openings, always; (b) whenever a consequential choice becomes askable, with no fixed number (D1 Q1); (c) for the owner's verdict on a proposal both debaters accepted. Each checkpoint is shown in a message the owner can read before the question tool opens (send_to_user in T3 Code): at (a) both opening cases, the disagreement most likely to change the outcome, and an open "your view?"; at (c) the exact proposal both debaters accepted, in full, with any remaining dissent. Every question, verdict included, is in plain language and grilling's format; a proposal or decision id only follows as a reference. Other exchanges keep the one progress line. The owner may ask for a pause after every round or waive optional pauses; no "at the end only".
- R4 Waiting: the checkpoint is asked through the host's question tool or ends the turn; silence consumes no launches. After the openings, wait for the owner's view or an explicit "I have no feedback on the openings" before the next launch; that answer clears the feedback pause only. A partial reply settles only what it addresses; "carry on" releases an optional pause only; an open decision needs an answer, a bounded delegation or an explicit deferral, and after a deferral only work independent of it continues.
- R5 Sorting what debaters raise: grilling's full table. Visible behaviour and material trade-offs stay with the owner unless settled or explicitly delegated; a fact is looked up; an inaccessible fact is asked only after saying what was checked.
- R6 Owner input in briefs: binding decisions go into both next briefs as decisions. Openings stay independent (no tentative owner preferences in the opening brief). After the openings the owner's reasoning and claims go to both, with the question what they change and which objection still stands; the debaters may push back on them with reasons, and a factual claim of the owner is checked like any other (D1 Q2). Earlier positions stay visible.
- R7 Agreement: all three accept the exact same proposal version. The owner may instead choose a direction over the debaters and end with dissent recorded. The verdict is asked even when the final synthesis check spent the last launches; it costs zero launches; while pending, report "both debaters accepted; the owner's verdict is pending". A rejection records the objection, and starts another exchange only with a concrete issue and within the existing cap and launch reservations. Any edit needs fresh acceptance. Cap and deadlock stay as they are. SPAR-FILE.md: the conclusion and Owner decisions show the owner's verdict.
- R8 Verification: tests/test_spar.py pins the contract (launch rule, opening checkpoint and its wait, owner verdict in agreement at zero launches, checkpoint shown before the question, no "end only" option). One live replay, with the owner's OK and a cap before it runs, stages a consequential choice after the openings and checks: its numbered question, lettered options and trade-off make sense with every project id removed; the next briefs reflect the owner's answer and reasoning; the next launch waited; at the verdict checkpoint the owner sees the same full text both debaters accepted before being asked; model consensus alone is never reported as agreement.

### Stays the same
- grilling; the start card's effort, debaters and record choices; launch counting, cap and deadlock.
- /spar never implements.

### Not included
- A release; that is a separate step.
- The recorded follow-ups from rc.3 (delegated-prompt pause, worktree removal, operation-name matching).

### Acceptance
- Every R8 test exists, fails before its change and passes after.
- The full suite and validate pass on main.
- The live replay passes, or each failure is recorded and decided by the owner.
