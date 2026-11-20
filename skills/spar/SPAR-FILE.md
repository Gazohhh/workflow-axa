# SPAR.md: the record of a spar

Read by `/spar` at the start. Write SPAR.md and the conclusion for a person, as `../workflow/WRITING.md` says.

## Where it lives

Create `docs/spar/<date>-<topic>/SPAR.md` when the owner chooses to keep one (SKILL.md "The start card"). /spar is its own skill, not part of the workflow: that folder holds only SPAR.md, which the approval hook lets you write without an approval offer. A "conversation only" spar writes nothing and keeps the same sections in the conversation.

A spar is during a task only when the owner names the task, or the idea changes the active task's agreed scope. Otherwise it is outside any task; ask when unclear.

During a workflow task, a kept SPAR.md still lives in `docs/spar/`. When it is first written, add one line to the task's FINDINGS (through `record.py`) that links it; a conversation-only spar writes nothing to the task until the owner picks "Turn this into a workflow plan". Leave the task's checkpoint as it is while sparring. When the task's agreement is already agreed and the conclusion proposes a change to it, change the checkpoint only when the owner then picks "Turn this into a workflow plan": set `Agreement (gate one): <current state>; proposed revision pending (SPAR.md)` and `Next safe action: agree the revision (workflow-clarify; Handoff brief in SPAR.md)`, and keep the task's previous next step in that line. Any other ending leaves the checkpoint unchanged.

SPAR.md is written with the editor tools; PLAN, TODO, FINDINGS and DECISIONS go only through `record.py`.

## When it changes

Update it after each owner decision, evidence change, exchange and the ending. Each update raises `Revision <n>` in Current position. A later `/spar` on the same topic reads SPAR.md first and re-checks only what changed.

## Its sections

Scale each section to the discussion: short entries, or "none identified". It is never a transcript.

```markdown
# Spar: <topic>

## Current position
Revision <n>, <date>. The idea in one line. The current recommendation, labelled: coordinator recommendation, a debater's, "both debaters agree; the owner's verdict is pending", or agreed by both debaters and the owner. What the owner chose. The next move.

## Intent and boundaries
The desired outcome in the owner's words. Constraints. Success criteria.

## Evidence
Facts with their source; who verified the decisive claim. Assumptions, owner claims marked "not yet checked". Prototype-only claims, with the observation that would falsify each and its cheapest check. Contradictions, with their evidence.

## Options considered
Each option: its strongest honest case, its strongest objection, and who holds which view. Each decision point (id and plain title) with both debaters' quoted lines and any label.

## What changed our thinking
Each decisive challenge, piece of evidence or revision, and its effect.

## Owner decisions
Each choice: answered (with the reason), delegated with limits, deferred by the owner, or blocking. The owner's view at each checkpoint, and the owner's verdict on the points both debaters agree on.

## Open questions and dissent
Each one: why it matters, and what would resolve it. The uncertainty most likely to change the decision, with its cheapest credible test.

## Handoff brief
The selected direction, its boundaries, the conditions for going ahead, and what stays an assumption.
```

Keep three labels apart wherever a view is stated: coordinator recommendation, each debater's assessment, owner decision.

## The conclusion

At every ending except a cancel, show the conclusion before the handoff question (`send_to_user` in T3 Code), short, in this order:

1. The outcome before the owner's verdict ("both debaters agree; the owner's verdict is pending", a labelled recommendation, competing approaches, or the ending as itself) and whether the owner can act now. It never states the owner's agreement; that comes from the answer to the card.
2. The decisive trade-off, in a sentence or two.
3. The criteria that differ: one sentence for one, a table only when several criteria separate the options.
4. Each decision point by plain title, both debaters' lines quoted verbatim, labelled only as SKILL.md "3. Challenge" allows; unresolved points, blockers and dissent included, none dropped.
5. The owner's decisions. One still needed is asked through grilling's "How to ask": numbered, with lettered options and "Recommended: <letter>" and its trade-off; labels follow `../workflow/WRITING.md` "Chat replies" rule 7.
6. The uncertainty that could change the decision, and its cheapest test.
7. Where SPAR.md is, with its revision, or "not saved".

After a cancel, record the partial position in SPAR.md (in the conversation when conversation only) and show it; ask nothing more.
