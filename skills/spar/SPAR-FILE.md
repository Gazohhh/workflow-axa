# SPAR.md: the record of a spar

Write SPAR.md and the conclusion for a person, as `../workflow/WRITING.md` says.

Read by `/spar` at the start.

## Where it lives

Create `docs/spar/<date>-<topic>/SPAR.md` when the owner chooses to keep one (SKILL.md "The start card"). /spar is its own skill, not part of the workflow: that folder holds only SPAR.md, which the approval hook lets you write without an approval offer. A "conversation only" spar writes nothing and keeps the same sections in the conversation.

A spar is during a task only when the owner names the task, or the idea changes the active task's agreed scope. Otherwise it is outside any task; ask when unclear.

During a workflow task, a kept SPAR.md still lives in `docs/spar/`. When it is first written, add one line to the task's FINDINGS through `../workflow/scripts/record.py` that links it; a conversation-only spar writes nothing to the task until the owner picks "Turn this into a workflow plan". Leave the task's checkpoint as it is while sparring. When the task's agreement is already agreed and the conclusion proposes a change to it, change the checkpoint only when the owner then picks "Turn this into a workflow plan": set `Agreement (gate one): <current state>; proposed revision pending (SPAR.md)` and `Next safe action: agree the revision (workflow-clarify; Handoff brief in SPAR.md)`, and keep the task's previous next step in that line. Any other ending leaves the checkpoint unchanged.

SPAR.md is written with the editor tools; PLAN, TODO, FINDINGS and DECISIONS go only through `record.py`.

## When it changes

Update it after each meaningful step: an owner decision, changed evidence, each exchange, the ending. Each update raises `Revision <n>` in Current position. A later `/spar` on the same topic reads SPAR.md first and re-checks only what changed.

## Its sections

Scale each section to the discussion: short entries, or "none identified". It is never a transcript.

```markdown
# Spar: <topic>

## Current position
Revision <n>, <date>. The idea in one line. The current recommendation, labelled: coordinator recommendation, or a debater's, or agreed by both. What the owner chose. The next move.

## Intent and boundaries
The desired outcome in the owner's words. Constraints. Success criteria.

## Evidence
Facts with their source. Assumptions. Contradictions, with their evidence.

## Options considered
Each option: its strongest honest case, its strongest objection, and who holds which view.

## What changed our thinking
Each decisive challenge, piece of evidence or revision, and its effect.

## Owner decisions
Each choice: answered (with the reason), deferred by the owner, or blocking.

## Open questions and dissent
Each one: why it matters, and what would resolve it. The uncertainty most likely to change the decision, with its cheapest credible test.

## Handoff brief
The selected direction, its boundaries, the conditions for going ahead, and what stays an assumption.
```

Keep three labels apart wherever a view is stated: coordinator recommendation, each debater's assessment, owner decision.

## The conclusion

At every ending except a cancel, show the conclusion before the handoff question. In T3 Code, send it with `send_to_user`; elsewhere, write it before the question. Keep it short, in this order:

1. The outcome: agreed, a labelled recommendation, or competing approaches (for until agreement: agreement, deadlock or the cap), and whether the owner can act now.
2. The recommendation, or each competing approach, in a few bullets with its reasons.
3. Blockers and open dissent; none is dropped to keep it short.
4. The owner's decisions. A decision still needed is asked through grilling's "How to ask": numbered, with lettered options and "Recommended: <letter>" and its trade-off, never as a list of labels such as "O1-O5" whose meaning depends on codes.
5. The uncertainty that could change the decision, and its cheapest test.
6. Where SPAR.md is, with its revision, or "not saved" for a conversation-only spar.

After a cancel, record the partial position in SPAR.md (in the conversation when conversation only) and show it; ask nothing more.
