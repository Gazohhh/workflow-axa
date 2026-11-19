# Writing

How to write anything a person reads: questions, chat updates, plans, tickets, findings, reports. Agent instructions (skills, AGENTS.md) follow this package's `writing-for-agents` skill (`../writing-for-agents/SKILL.md`) for structure; this file covers the human-facing text. It is the one owner of the common writing rules and of the Unslop check. [SIMPLE-ENGLISH.md](SIMPLE-ENGLISH.md) keeps only its Strict and CHECK modes.

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

## Documents and reports

Write plain English that a smart reader outside your field understands on one read. These rules come from ASD-STE100, the controlled language that aerospace uses for maintenance manuals, in its Plain form. When asked to write or rewrite documentation, apply them to the prose. A report is a document: apply them to every prose field of the report JSON (the understanding line, section texts, ticket specifications and expected results, acceptance notes, check expectations, results and limits, decision summaries, risks), and run the self-check on that text before rendering.

1. Classify each passage. Procedural text tells the reader what to do: imperative mood, 20 words per sentence, one instruction per sentence. Descriptive text explains: simple tenses, 25 words per sentence, one topic per paragraph, six sentences per paragraph at most.
2. Never touch code, identifiers, commands, flags, file paths, quoted errors, product names, facts, quoted user words (double-quoted or in backticks), decision records, report values (`verified`, `partial` and so on), or DESIGN.md rule 4's question, which is quoted word for word. When the source gives no number or cause, keep the general statement.
3. Condition before command, with a comma: "If the build fails, read the log."
4. Use simple tenses and active voice. No present perfect ("has completed" → "completed"). No "-ing" verb after a comma (", making it easy" → new sentence). Name the actor: "You run the migration."
5. Modals keep their meaning. A required "should" becomes "must". Keep may, might, could, should and would when they state uncertainty, permission or a proposal. Rewrite empty hedging, never just delete it, unless the sentence states nothing else (rule 10).
6. Use complete grammar: keep articles and "that". Write short sentences, not telegraph style. Writing out contractions is a suggestion, not a rule.
7. No semicolons and no em-dashes. Write two sentences, or name the relation.
8. One word, one meaning, for the whole document. Plainer swaps are suggestions: `make sure that` for check, verify, confirm, validate or ensure, and `configuration` for config, settings or options, unless the swap changes the meaning. Break noun chains over three words with a preposition ("the timeout value for the connection pool"). The project's and the workflow's established terms win (ticket, agreement, gate, acceptance): never swap them for synonyms.
9. Give the reader each term and each fact before the step that needs it. Define a concept term at its first use, under ten words, one per sentence. Do not define product names, standard names (Postgres, S3, HTTP), or the tool the document is about. Also name the host, the flag, or the prior step that a command depends on. "Restart the service" becomes "Restart the `sync` service on the host that runs the job."
10. State the fact, not its importance. Delete words that carry no fact: simply, seamlessly, robust, powerful, comprehensive, leverage, crucial, "in order to", "it is worth noting". No "not just X, it is Y". No decorative triplets. No "in conclusion". Delete a sentence that states no fact, check or decision. Do not reword it.
11. Use formatting only where it carries structure. No bold lead-ins, no bold as emphasis, no emoji, no heading over two sentences. A vertical list is for three or more parallel items or steps: colon on the lead-in, uppercase start, one instruction per item.
12. Warnings: command or condition first, then the risk. "Do not run this against production. The command deletes rows."

Use American spelling. `simple-english/word-swaps.md` maps the overused words to plain ones. For an error message, a runbook, an incident report, release notes, a commit message, or UI copy, read `simple-english/use-cases.md` first. It names the mode and the pattern for each. These rules are for facts and instructions, not marketing copy or brand writing, because they delete persuasion. Say so, and offer them for the docs instead. When you rewrite documentation, [WRITING-EXAMPLE.md](WRITING-EXAMPLE.md) shows these rules applied to one passage.

## Chat replies

Every chat reply, in every mode, follows these rules:

1. Answer in prose. No headers, no bullet lists, no bold, no tables. A code block is legal when the reader must copy it. The workflow's required formats are the exception: numbered questions with options, short lists of three or more items, and the closing state line ("**Waiting on you:**", "**Running:**", "**Done.**"), which an offer's presentation replaces: nothing follows it.
2. The first sentence gives the answer or the result. Do not restate the question.
3. No em-dashes and no semicolons. Name the relation ("because", "but", "for example") or write two sentences.
4. Define a concept term in a few words the first time you use it: "idempotent (safe to run twice)". Do not define product names.
5. No openers ("Certainly", "Great question") and no closers ("I hope this helps", "Let me know"). Writing out contractions is a suggestion.
6. Do not shorten quoted error text, security warnings, or confirmations before a destructive action.

Before: The failure stems from control-plane leader election during pod churn — nothing to worry about!
After: The pods restarted and the queue lost its leader for a short time. It recovered without help. You do not have to do anything.

## Self-check

1. Reply: search for `—`, `;`, `**`, `#`, and a line that starts with `-`. Remove each one that the workflow formats do not need.
2. Document: count the words in your three longest sentences. Over 20 or 25, split. Search for `has been`, `;`, `—`, `, making`, `**`, and any heading that covers fewer than three sentences. Fix each hit. Consider each `'`, `check`, `verify` and `config` against rules 6 and 8: they are suggestions. Read each `should`, `may`, `might`, `could` and `would` against rule 5. Read each step: does it name a host, a flag, or a prior step the reader must already have? If not, add it or point to it.

The report renderer checks every report before writing. It prints `PLAIN ENGLISH:` problems and `PLAIN ENGLISH NOTE:` lines for modals, skipping quoted text. Problems never block it; `--open` waits. Until the user sees the report, re-render into the same file with `--replace-unpresented`.

## Unslop

A required check. Run it after drafting, together with the self-check above, and before the cold-reader check. It removes the patterns that make text read as machine-written. The tells are listed under "Unslop tells" below, and their vocabulary is in `simple-english/word-swaps.md`. Run it on every new or changed text a person reads:

- Offer inputs, the prose fields of the offer file, before `record.py offer create`. The presented offer text is never edited.
- Tickets, PLAN, FINDINGS and DECISIONS prose, and other task records.
- The delivery chat report, and other reports.
- A kept SPAR.md and the /spar conclusion.
- Human-facing docs, such as a README or a guide.
- Changed prose in a code review.
- Commit and PR text, when you are asked to write it.
- Chat messages.

It never rewrites history: older task records, quoted owner answers and already-presented approvals stay word for word.

"Keep the meaning" wins over every tell. A tell never removes an uncertainty word, a condition or the text rule 2 above protects. The check never changes application UI copy, error messages or translations. Changing the text an application shows its users is the owner's decision. A README or a guide is a doc, not application text.

## Unslop tells

A bare rule number means that rule of "Documents and reports". Each tell keeps the number of its source list. That list has no tells 1, 2, 4, 6 or 21, and this package does not adopt Unslop 24. A tell that a rule here already covers names that rule and adds nothing else. Headings written before this table stay as they are until their section changes for another reason.

| Tell | What to do |
|---|---|
| Unslop 3 | Rule 4. |
| Unslop 5 | Name the source of a claim ("the Postgres docs say"). Without a source, state the claim with its evidence or mark it unverified. No "experts believe". |
| Unslop 7, 31 | Rule 10 and `simple-english/word-swaps.md`. |
| Unslop 8 | Write "is" or "has", not "serves as", "stands as", "boasts" or "features". |
| Unslop 9, 10, 23, 25 | Rule 10. |
| Unslop 11 | Rule 8. |
| Unslop 12 | Write "from X to Y" only when X and Y sit on a real scale. |
| Unslop 13 | Rule 7. En dashes and hyphens used as dashes count too. So do parentheses that wrap an aside where a dash would go. A short definition in parentheses, as "Chat replies" rule 4 shows, stays. |
| Unslop 14 | A colon introduces a list, an example or the detail that explains the words before it. It never stands in for a connector such as "and", "so" or "because". |
| Unslop 15, 16, 18 | Rule 11. |
| Unslop 17 | Write new headings in sentence case. |
| Unslop 19 | Use straight quotes. |
| Unslop 20, 22 | "Chat replies", rule 5. |
| Unslop 24 | Not adopted. "One hedge at most" deletes uncertainty that carries meaning. Rule 5 and "Keep the meaning" apply instead. |
| Unslop 26 | No abstract metaphor noun (substrate, wedge, vector, nexus, primitive, harness, surface, scaffolding, paradigm, ratchet, north star, flywheel) where a concrete word exists. A word used in its literal technical sense stays: a math vector, a test harness, a language primitive. |
| Unslop 27 | Say what it does. Name the mechanism or the number. Delete a sentence that states no fact about this project and could appear unchanged in another project's docs. A general statement that rule 2 keeps stays. |
| Unslop 28 | Rule 1. |
| Unslop 29 | Rule 4. |
| Unslop 30 | Cut an adverb that adds no fact, or use a stronger verb. Give the number when there is one. |
| Unslop 32 | No metaphor, aphorism, personified code ("the function wants") or figurative verb where a literal phrase exists. |
| Unslop 33 | Rule 6. Spell out arrows and abbreviations in prose. |

## Cold-reader check

Before presenting a plan report, a substantial plan or a final report, reread it as someone who missed the conversation. Can they explain the goal, what changes, what stays the same, the decision asked of them and how completion is checked? Can a developer find the evidence? Check each claim against it: "the full suite passes" names any failures it already had; "every finding is fixed" counts the open ones; "what works now" lists only what a check showed.

When you can, give an independent reviewer only the document and its audience, ask them to restate those five things, and compare part by part with the table above. Each mismatch is a writing defect. Without a reviewer, write the restatement yourself before rereading the records, and say it was a self-check.

## Say which state

Use "before this change" for the old code, "agreed" for the agreement, "approved plan" for implementation approval, and a dated checkpoint for progress. Report agreement, approval, implementation and verification separately: "R3 is agreed and approved, coded, and still needs a phone check" beats "R3 done."
