# Writing

How to write anything a person reads: questions, chat updates, plans, tickets, findings, reports. Agent instructions (skills, AGENTS.md) follow this package's `writing-for-agents` skill (`../writing-for-agents/SKILL.md`) for structure; this file covers the human-facing text.

## The reader

Assume no project or technical background unless the user asks for a specialist format. Be direct and adult: explain the situation and its consequence before any technical term. Keep the user's language and requested length.

## Order

1. What the reader needs to understand or decide.
2. What happens today, what changes, why it matters.
3. Exact names, files, commands and caveats underneath, or in the evidence section.

The top part must stand on its own. Exclusions, risks and open questions belong there, never only in the details.

Define an unfamiliar term once; otherwise use everyday words. Use one name per concept, and the project's own name when it has one.

| Less useful | Clearer |
|---|---|
| "Should the preference persist?" | "Should the app remember this setting after someone closes and reopens it?" |
| "Hydration parity is maintained." | Which screen or saved data stays consistent, under which condition. |
| "Implemented a robust, production-ready solution." | The changed behavior, the checks that passed, the environments not tested. |

## Cut

Delete filler, repeated headings, empty template sections, invented certainty and second copies of a decision. Do not create a file just to look thorough. When you say something is slop, show it: the repeated paragraph or unsupported claim, and why removing it loses nothing.

## Keep the meaning

Simpler words must keep the rule. Before rewording a requirement, finding or technical sentence, check that each part survives:

| Part | Ask | Lost looks like |
|---|---|---|
| Actor | Who acts or is affected? | "The setting is saved" when only admins can save it |
| Condition | When does it apply? | Dropping "after the first sync" |
| Obligation | Must, may, must not, or only proposed? | "We keep old reports" for "never rewrite them" |
| Result | What can be observed? | "Handled" for "rejected with an error message" |
| Exception | What is excluded? | Omitting the lightweight-edit route |
| Evidence | How strong is the support? | A file read presented as a passed test |

If plain words cannot carry a part, keep the precise wording and explain it. Shorter is never the goal on its own.

Words that carry uncertainty, permission or a proposal (may, might, could, should, would) are part of the meaning. "The cause could be the cache" is not "The cause is the cache". Keep them, rewrite only empty hedging, and never just delete one.

Write chat messages and reports with `../simple-english/SKILL.md` (Plain mode and its workflow-axa adaptation).

## Cold-reader check

Before presenting an approval report, a substantial plan or a final report, reread it as someone who missed the conversation. Can they explain the goal, what changes, what stays the same, the decision asked of them and how completion is checked? Can a developer find the evidence? Check each claim against it: "the full suite passes" names any failures it already had; "every finding is fixed" counts the open ones; "what works now" lists only what a check showed.

When you can, give an independent reviewer only the document and its audience, ask them to restate those five things, and compare part by part with the table above. Each mismatch is a writing defect. Without a reviewer, write the restatement yourself before rereading the records, and say it was a self-check.

## Say which state

Use "before this change" for the old code, "agreed" for gate one, "approved plan" for gate two, and a dated checkpoint for progress. Report agreement, approval, implementation and verification separately: "R3 is agreed and approved, coded, and still needs a phone check" beats "R3 done."
