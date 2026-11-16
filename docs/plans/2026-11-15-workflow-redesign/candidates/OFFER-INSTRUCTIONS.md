# Candidate text: the offer and the one question, and the CSS switch (activate at T17)

Candidate-only under the §14 transition rule. Ticket T16 wrote these blocks; `tools/stage_candidate.py` applies them to an isolated copy for the host tests, and T17 applies them to the package. Each `### <path>` heading names one file. The ```` ```old ```` block below it must occur exactly once there, and is replaced by the ```` ```new ```` block. Contracts C-OFFER-2..4, C-OFFER-7, C-CSS-1/2.

### skills/workflow-specify/SKILL.md

```old
First compare every ticket with the agreement line by line (behavior, timing, data, failures, assumptions); any difference is an agreement change (step 4). Build the plan report as `workflow/VISUAL-REVIEW.md` "Prepare the report" says and ask for implementation approval; say "implements the behavior we agreed" only when that comparison found no difference. **STOP** (VISUAL-REVIEW "Prepare the report" step 4).
```

```new
First compare every ticket with the agreement line by line (behavior, timing, data, failures, assumptions); any difference is an agreement change (step 4). Then write the **offer**: a JSON file with the behaviour summary, the paths the tickets may change, the operations (only protected actions, each by its exact name: `git commit` when asked, `git push`, an MCP tool's name; never a check), exclusions, conditions and required checks, and create it with `python -X utf8 -I <workflow>/scripts/record.py offer create <task-folder> <file.json>`. Run `record.py offer present <task-folder> <id>` and copy the block it prints, from its `--- workflow-axa offer` line to its `--- end offer` line, **into your reply** inside a code block, byte for byte. The owner doesn't see tool output, and only the block in your reply (or in the question) counts as presented. Your own summary may sit around it, never in place of it.

End with **the one question**, with three answers: *Show review.html first*, *Approve from this summary*, *Change something*. Recommend the first when the change touches saved data, auth, a public interface, a migration, deletion, money, more than one owner or visible UI, and say why. Use the question tool when you have one (the block goes in the question). Without one, ask in text and end with this line, filled in: "Answer `/approve <id>` or approve, yes, ok, go, ja, akkoord or doe maar to approve from this summary; `/report <id>` to see review.html first; or say what to change." **STOP.** Say "implements the behavior we agreed" only when the comparison found no difference.
```

### skills/workflow-specify/SKILL.md

```old
Done when the report exists for this revision and its path is in your approval question (one-line changes included), or the user's explicit "no report" is recorded, or the task is on the small change route (valid `Small change:` line, no switch to the full route; `workflow/VISUAL-REVIEW.md`).
```

```new
Done when the offer was presented and the one question asked (one-line changes included). *Show review.html first*: build the report as `workflow/VISUAL-REVIEW.md` "Prepare the report" says (read `../codebase-map/TASK-REPORT.md`, `../codebase-map/FLOWCHART-DESIGN.md` and `../workflow/SIMPLE-ENGLISH.md` whole first), name its `docs/plans/<task>/reviews/<file>.html` path, and ask again with *Approve from this summary* and *Change something*.
```

### skills/workflow-specify/SKILL.md

```old
Record the answer in the checkpoint `Approval` line and DECISIONS: approved (revision, report, tickets, exclusions), a correction (behavior or scope → `workflow-clarify`; tickets, seams, presentation → here), or a scoped waiver.
```

```new
The hook reads the answer from the conversation; never write an approval yourself. Record `- Offer: #<id>` in the checkpoint and the answer in DECISIONS. A qualified answer ("yes, but not the database") approves nothing: write the narrowed offer with `record.py offer revise`, present it, and ask once more. A correction of behavior or scope goes to `workflow-clarify`; tickets, seams or presentation stay here. `/wait-what` is no answer: explain, then present the unchanged offer and the same question again.
```

### skills/workflow/VISUAL-REVIEW.md

```old
4. Ask: "This plan implements the behavior we agreed. Approve it to start implementation, or describe what needs changing." **STOP.**
```

```new
4. The owner asked for this report with *Show review.html first*: ask the one question again without that answer (*Approve from this summary* · *Change something*). **STOP.**
```

### skills/workflow/VISUAL-REVIEW.md

```old
Set `write_paths` to the repository files (or folders ending in `/`) the plan may change; after approval the phase gate blocks other file writes.
```

```new
Set `write_paths` to the same paths as the offer; the offer, not the report, is what the hook checks.
```

### skills/workflow/VISUAL-REVIEW.md

```old
A clear "yes, proceed" to this report approves the shown revision.
```

```new
The answer to the one question decides; the hook reads it from the conversation (workflow-specify step 5).
```

### skills/rule-maker/rules/DESIGN.md

```old
# Application UI: reuse existing styles, never write CSS
```

```new
# Application UI: reuse existing styles; CSS only when the owner switched it on
```

### skills/rule-maker/rules/DESIGN.md

```old
1. **No new CSS, ever.** Do not create, modify or inject CSS: no new stylesheet rules, no `<style>` blocks, no `style=""` attributes, no CSS-in-JS, theme overrides or arbitrary visual props. JavaScript style mutation, canvas/SVG or native attributes are not loopholes.
```

```new
1. **No new CSS while the CSS switch is off**, which is the default. Do not create, modify or inject styling (see "What counts as styling"): JavaScript style mutation, canvas/SVG or native attributes are not loopholes. `python -X utf8 -I <workflow>/scripts/settings.py show` tells the machine's switch; a project's DESIGN.md with `css: never` keeps it off there. Only the owner turns it on: ask exactly *"Turn CSS on for every project on this machine? Yes / No"* and run `settings.py css on` only after that Yes. When it is on, styling stays inside the approved offer's paths, and reuse (rules 2–4) still comes first.
```

### skills/ui-design/SKILL.md

```old
description: "Use for any application UI work (behavior-only included), in workflow or ordinary requests, and to build or check a design kit or DESIGN.md. Never write CSS: reuse existing classes and IDs; when nothing matches, ask which existing element to mimic."
```

```new
description: "Use for any application UI work (behavior-only included), in workflow or ordinary requests, and to build or check a design kit or DESIGN.md. Reuse existing classes and IDs; when nothing matches, ask which existing element to mimic. CSS only when the owner switched it on."
```

### skills/ui-design/SKILL.md

```old
No new CSS in any mode.
```

```new
No new CSS while the machine CSS switch is off (`settings.py show`; DESIGN.md rule 1); never switch it yourself.
```

### skills/ui-design/SKILL.md

```old
No CSS, inline style or arbitrary visual props;
```

```new
No CSS, inline style or arbitrary visual props while the CSS switch is off;
```

### skills/workflow/VISUAL-REVIEW.md

```old
| 2 — Implementation approval | Tickets, dependencies, test strategy and the HTML report | The codebase-map report | Code and tests inside the approved tickets | Checkpoint `Approval` line, DECISIONS |
```

```new
| 2 — Implementation approval | Tickets, dependencies, test strategy, as an offer | The offer and the one question (the report when asked) | Code and tests inside the approved offer | Checkpoint `Offer: #<id>`, DECISIONS (the hook reads the answer) |
```

### skills/workflow/VISUAL-REVIEW.md

```old
- **Every implementation approval request comes with a fresh HTML report**, combined and one-line changes included, except the small change route. Skip it only when the user explicitly says they don't want it; record their words. A plan in chat alone is not enough.
```

```new
- **Every implementation approval is an offer with the one question** (workflow-specify step 5), small changes included. The HTML report is built when the owner answers *Show review.html first*, or when you recommend it and they agree.
```

### skills/workflow/VISUAL-REVIEW.md

```old
1. Write the task record first, making the task current, with `- Small change: <files> — <what changes>` in its checkpoint: comma-separated, repository-relative files that exist, plus any new regression test file.
2. In one message or AskUserQuestion, show that `Small change:` line exactly, on its own line, and ask for a yes. End the turn.
3. Record `- Approval (gate two): small change approved <date>: "<the owner's whole answer>"`, then edit only the listed files.
```

```new
1. Write the task record first, making the task current, with `- Small change: <files> — <what changes>` in its checkpoint.
2. Create the offer with those files as its paths (plus any new regression test file), present it and ask the one question (workflow-specify step 5). End the turn.
3. After the approval, edit only the offer's paths.
```

### skills/workflow/VISUAL-REVIEW.md

```old
Changing the file list or the description needs a new offer and yes. A small change approved in an earlier session continues without a new yes, unless that session withdrew, stopped or restricted it afterwards; then show the same offer again and record the new answer on a separate `- Reconfirmed (gate two): small change, <date>: "<the owner's whole answer>"` line; the original Approval line is never changed. Growing scope or risk: switch to the full route (`workflow-clarify`, then the plan report).
```

```new
Changing the file list or the description is a revised offer (`record.py offer revise`) and a new answer. An approval from an earlier session holds until a later withdrawal, narrowing or stop; then present the offer again. Growing scope or risk: switch to the full route (`workflow-clarify`, then the plan).
```

### skills/workflow/VISUAL-REVIEW.md

```old
The gate enforces the file list and the quoted yes ([SETUP.md](SETUP.md) "Small change"). Whether it qualifies, and "no interface or behavior change beyond the description", are enforced by instructions only.
```

```new
The hook enforces the offer's paths and the owner's answer. Whether it qualifies, and "no interface or behavior change beyond the description", are enforced by instructions only.
```

### skills/workflow/VISUAL-REVIEW.md

```old
The hook accepts an explicit `legacy` Approval line with **one named existing report**
```

```new
This applies only to tasks the owner listed as pre-offer approvals at the upgrade (`legacy_inventory.py`, SETUP.md); every other task uses offers. The hook accepts an explicit `legacy` Approval line with **one named existing report**
```

### skills/workflow/AUDIT.md

```old
| Maintainability | Existing owner, clear data flow, justified helpers, useful comments, no speculative wrappers or unrelated churn. |
```

```new
| Maintainability | Existing owner, clear data flow, justified helpers, no comments beyond CORE's exceptions, no speculative wrappers or unrelated churn. |
```

### skills/workflow/AUDIT.md

```old
Comments explain constraints, intent, externally required quirks, or surprising behavior. They need not narrate syntax, repeat good names, preserve deleted code, or restate the task ticket. Document public contracts or safety constraints when needed; do not enforce an arbitrary comment-to-code ratio.
```

```new
New code carries no comments except CORE's exceptions (licence headers, an unchangeable constraint with its link, public API doc comments, tool-required text, issue links). Comments are claims, not evidence: check the code, and report a comment that contradicts it as a possible bug (CORE).
```

### skills/workflow/AUDIT.md

```old
- Weak comment: `Increment the counter.`
- Useful comment: `Keep this ID stable: saved playlists reference it.`
```

```new
- Weak: a comment such as `Keep this ID stable: saved playlists reference it.`
- Useful: the name `stablePlaylistId` and a test that saved playlists still resolve.
```
