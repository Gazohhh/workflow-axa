<!-- Reference text, formerly the simple-english skill (unregistered in 2.9.0); licence: SIMPLE-ENGLISH.LICENSE, credits: VENDORED-SKILLS.md. -->

# Simple English

Write plain English that a smart reader outside your field understands on one read. The rules come from ASD-STE100, the controlled language that aerospace uses for maintenance manuals. Two registers exist: the document you write or rewrite, and the reply you type in chat. Each has its own short rule set below. workflow-axa uses this skill for every HTML report (plan, progress, delivery) and the chat messages that hand them over.

## The Document

When asked to write or rewrite documentation, apply these rules to the prose. A report is a document: apply them to every prose field of the report JSON (the understanding line, section texts, ticket specifications and expected results, acceptance notes, check expectations, results and limits, decision summaries, risks), and run the self-check on that text before rendering.

1. Classify each passage. Procedural text tells the reader what to do: imperative mood, 20 words per sentence, one instruction per sentence. Descriptive text explains: simple tenses, 25 words per sentence, one topic per paragraph, six sentences per paragraph at most.
2. Never touch code, identifiers, commands, flags, file paths, quoted errors, product names, facts, quoted user words (double-quoted or in backticks), decision records, report values (`verified`, `partial` and so on), or DESIGN.md rule 4's question, which is quoted word for word. When the source gives no number or cause, keep the general statement.
3. Condition before command, with a comma: "If the build fails, read the log."
4. Use simple tenses and active voice. No present perfect ("has completed" → "completed"). No "-ing" verb after a comma (", making it easy" → new sentence). Name the actor: "You run the migration."
5. Modals keep their meaning. A required "should" becomes "must". Keep may, might, could, should and would when they state uncertainty, permission or a proposal. Rewrite empty hedging, never just delete it, unless the sentence states nothing else (rule 10).
6. Use complete grammar. No contractions, keep articles, keep "that". Write short sentences, not telegraph style.
7. No semicolons and no em-dashes. Write two sentences, or name the relation.
8. One word, one meaning, for the whole document. Use `make sure that` for check, verify, confirm, validate, ensure. Use `configuration` for config, settings, options. Break noun chains over three words with a preposition ("the timeout value for the connection pool"). The project's and the workflow's established terms win (ticket, agreement, gate, acceptance): never swap them for synonyms.
9. Give the reader each term and each fact before the step that needs it. Define a concept term at its first use, under ten words, one per sentence. Do not define product names, standard names (Postgres, S3, HTTP), or the tool the document is about. Also name the host, the flag, or the prior step that a command depends on. "Restart the service" becomes "Restart the `sync` service on the host that runs the job."
10. State the fact, not its importance. Delete words that carry no fact: simply, seamlessly, robust, powerful, comprehensive, leverage, crucial, "in order to", "it is worth noting". No "not just X, it is Y". No decorative triplets. No "in conclusion". Delete a sentence that states no fact, check or decision. Do not reword it.
11. Use formatting only where it carries structure. No bold lead-ins, no bold as emphasis, no emoji, no heading over two sentences. A vertical list is for three or more parallel items or steps: colon on the lead-in, uppercase start, one instruction per item.
12. Warnings: command or condition first, then the risk. "Do not run this against production. The command deletes rows."

Use American spelling. `simple-english/word-swaps.md` maps the overused words to plain ones. For an error message, a runbook, an incident report, release notes, a commit message, or UI copy, read `simple-english/use-cases.md` first. It names the mode and the pattern for each.

Before (AI output):

> **Connection timeouts.** If sqlpipe hangs or fails with `dial tcp: i/o timeout`, check that the host running sqlpipe can reach the Postgres port (usually 5432) — this is often a security group or firewall rule blocking the connection. If you're connecting to a managed database (RDS, Cloud SQL, etc.), confirm the instance allows connections from sqlpipe's IP.

After (procedural, headed, numbered):

> ## Connection timeouts
>
> sqlpipe stops with `dial tcp: i/o timeout` when it cannot connect to the Postgres port (5432 by default).
>
> 1. Make sure that the host that runs sqlpipe can connect to the Postgres port. A firewall or security group usually blocks it.
> 2. If the database is managed (RDS, Cloud SQL), make sure that the instance accepts connections from the IP of sqlpipe.

## The Reply

Every chat reply, in every mode, follows these rules:

1. Answer in prose. No headers, no bullet lists, no bold, no tables. A code block is legal when the reader must copy it. The workflow's required formats are the exception: numbered questions with options, short lists of three or more items, and the closing state line ("**Waiting on you:**", "**Running:**", "**Done.**"), which an offer's presentation replaces: nothing follows it.
2. The first sentence gives the answer or the result. Do not restate the question.
3. No em-dashes and no semicolons. Name the relation ("because", "but", "for example") or write two sentences.
4. Define a concept term in a few words the first time you use it: "idempotent (safe to run twice)". Do not define product names.
5. No contractions. No openers ("Certainly", "Great question") and no closers ("I hope this helps", "Let me know").
6. Do not shorten quoted error text, security warnings, or confirmations before a destructive action.

Before: The failure stems from control-plane leader election during pod churn — nothing to worry about!
After: The pods restarted and the queue lost its leader for a short time. It recovered without help. You do not have to do anything.

## Self-Check Before You Deliver

1. Reply: search for `—`, `;`, `**`, `#`, and a line that starts with `-`. Remove each one that the workflow formats do not need.
2. Document: count the words in your three longest sentences. Over 20 or 25, split. Search for `'`, `has been`, `;`, `—`, `, making`, `**`, `check`, `verify`, `config`, and any heading that covers fewer than three sentences. Fix each hit. Read each `should`, `may`, `might`, `could` and `would` against rule 5. Read each step: does it name a host, a flag, or a prior step the reader must already have? If not, add it or point to it.

The report renderer checks every report before writing. It prints `PLAIN ENGLISH:` problems and `PLAIN ENGLISH NOTE:` lines for modals, skipping quoted text. Problems never block it; `--open` waits. Until the user sees the report, re-render into the same file with `--replace-unpresented`.

## Unslop tells

WRITING.md runs these as its Unslop check, together with the self-check above. A bare rule number means that rule of The Document. Each tell keeps the number of its source list. That list has no tells 1, 2, 4, 6 or 21, and this package does not adopt Unslop 24. A tell that a rule here already covers names that rule and adds nothing else. Headings written before this table stay as they are until their section changes for another reason.

| Tell | What to do |
|---|---|
| Unslop 3 | Rule 4. |
| Unslop 5 | Name the source of a claim ("the Postgres docs say"). Without a source, state the claim with its evidence or mark it unverified. No "experts believe". |
| Unslop 7, 31 | Rule 10 and `simple-english/word-swaps.md`. |
| Unslop 8 | Write "is" or "has", not "serves as", "stands as", "boasts" or "features". |
| Unslop 9, 10, 23, 25 | Rule 10. |
| Unslop 11 | Rule 8. |
| Unslop 12 | Write "from X to Y" only when X and Y sit on a real scale. |
| Unslop 13 | Rule 7. En dashes and hyphens used as dashes count too. So do parentheses that wrap an aside where a dash would go. A short definition in parentheses, as The Reply rule 4 shows, stays. |
| Unslop 14 | A colon introduces a list, an example or the detail that explains the words before it. It never stands in for a connector such as "and", "so" or "because". |
| Unslop 15, 16, 18 | Rule 11. |
| Unslop 17 | Write new headings in sentence case. |
| Unslop 19 | Use straight quotes. |
| Unslop 20, 22 | The Reply, rule 5. |
| Unslop 24 | Not adopted. "One hedge at most" deletes uncertainty that carries meaning. Rule 5 and WRITING.md "Keep the meaning" apply instead. |
| Unslop 26 | No abstract metaphor noun (substrate, wedge, vector, nexus, primitive, harness, surface, scaffolding, paradigm, ratchet, north star, flywheel) where a concrete word exists. A word used in its literal technical sense stays: a math vector, a test harness, a language primitive. |
| Unslop 27 | Say what it does. Name the mechanism or the number. Delete a sentence that states no fact about this project and could appear unchanged in another project's docs. A general statement that rule 2 keeps stays. |
| Unslop 28 | Rule 1. |
| Unslop 29 | Rule 4. |
| Unslop 30 | Cut an adverb that adds no fact, or use a stronger verb. Give the number when there is one. |
| Unslop 32 | No metaphor, aphorism, personified code ("the function wants") or figurative verb where a literal phrase exists. |
| Unslop 33 | Rule 6. Spell out arrows and abbreviations in prose. |

## Modes

Plain is the default and is all of the above. Reports and workflow messages use Plain only. Strict applies when the user names STE, ASD-STE100, or compliance: read `simple-english/strict-vocabulary.md` before you draft the document, and say once that no tool guarantees compliance. The reply stays Plain in every mode.

When asked to CHECK text instead of writing it, first open `simple-english/rule-catalog.md`. Then report each violation as: rule number quoted from that file, the offending text, a compliant rewrite. Never cite a rule number from memory. In Plain mode, judge a modal hit against rule 5 above, not the catalog's ban. When the user asked for compliance, end with one sentence: no tool can guarantee ASD-STE100 compliance, and the standard is a free download at asd-ste100.org.

## Limits

These rules are for facts and instructions, not marketing copy or brand writing, because they delete persuasion. Say so, and offer them for the docs instead.

## References

- `simple-english/rule-catalog.md`: the 53 rules of Issue 9 with software examples, for CHECK mode
- `simple-english/strict-vocabulary.md`: the dictionary discipline for Strict mode
- `simple-english/word-swaps.md`: a map from overused words to plain ones
- `simple-english/use-cases.md`: the mode and the pattern for error messages, runbooks, incident reports, release notes, commits, agent prompts, UI copy, and translation prep
