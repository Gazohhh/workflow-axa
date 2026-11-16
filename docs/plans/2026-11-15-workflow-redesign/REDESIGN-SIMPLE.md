# The plan in plain words (with the details that matter)

This is the readable version of `FULL-PLAN.md`. The section numbers (§) point to the full plan if you want the deep version. Both models (Opus and Astra) must agree on every part before it's called ready.

---

## 1. What's wrong today

1. **Approving is fragile.** The approval hook (`phase_gate.py`, 2,655 lines) re-reads the chat and looks for your exact words, report fingerprints and revision numbers. In your real session you approved one plan 3 times and another 4 times:
   - you wrote "no need for report", but the hook only knows "no report";
   - a plan message didn't contain the literal text "r4";
   - writing a record for another task switched the "current task", so an approved commit was blocked.
2. **One heavy process for everything.** A typo fix and a big feature go through mostly the same steps. By default every approval needs an HTML report. The only ways around it are narrow: a "small change" route, a "lightweight edit" route (no behaviour change at all, approved with zero questions), or a waiver in the exact words the hook knows.
3. **The CSS rule is copied into 6 rule files, so they can drift apart.** There's no supported way for you, the designer, to switch it off. That's why it sometimes "listens, then doesn't, then does".
4. **Too many moving parts.** 21 skills and 5 hooks. Some hooks police reading habits and punctuation. The validator has hand-written file lists, so adding one skill means editing several files.

**What stays, because it's where your quality comes from:** read the code and its callers first, reproduce bugs, tests first, a separate reviewer checking standards and spec, honest reporting, and asking you only about real decisions.

---

## 2. How a task will run (6 steps)

**Step 1: what kind of job is it?**
The AI reads your message and the code, then picks one of 9 recipes (§4):

| Recipe | For | What's special |
|---|---|---|
| bug | something broken | reproduce first; after two failed fixes it questions its own assumption |
| feature | new or changed behaviour | asks only about open choices |
| new-project | empty or new repo | rules proposal + first small slice; nothing installed without OK |
| ui | screens, Figma, styling | reuse existing classes; new CSS only when the CSS switch is on |
| refactor | restructure, same behaviour | tests that lock today's behaviour first; remove dead code before adding |
| architecture | big structure decisions | plan-review before tickets |
| performance | slow, memory | measure before and after; explain the number |
| migration | data, schema, versions | list everything that depends on it; rehearse on a copy |
| docs-tests | docs or tests only | lightweight |

Plus two modes without a file: **Inspect** (explain, review, no changes) and **Other**.
It also adds "modifiers" when needed: UI, security, compatibility.

If it isn't sure (two recipes fit and they behave differently, or there's no clear goal like "make it better"), it asks **one** question:
*Fix something broken · Add or change a feature · Start a new project · Only investigate · Other*
A vague "Other" means it first looks around, then comes back with a concrete proposal.

**Step 2: the rules check.**
If the project's rules are missing or weak, it says which gaps it found (for example "no test command, no ownership notes") and asks:
*Set up rules now · Skip for this task*
- Skip only waives the gaps it named, for this task. The rules that do exist still apply, and every other step (like the offer) still happens.
- Not answering is not the same as skipping. Meanwhile it can still read and investigate, but it won't change files.

**Step 3: it looks at the code** (callers, tests, history) and asks you only about choices that change what gets built.

**Step 4: the offer.**
It shows a numbered offer, for example:
> **Offer #12** — I'll understand this as: VAT rounds wrong on totals over €1,000.
> Changes: `vat.ts:40` + new test `vat.spec.ts`. Won't touch: database, invoices already sent. Checks: unit tests, type check.

Then it always asks one question:
*Show review.html first · Approve from this summary · Change something*
- Asked for **every** change, even a typo, because a small change can do big damage.
- It **recommends** the report when the change touches: saved data, login/security, money, deleting things, customer screens, or code others depend on. You always decide.
- If you pick the report, you see it first, then approve with one more click.
- If you change the scope ("but don't touch the DB"), that's a new offer and it asks once more. A restart or resume with the same offer doesn't ask again.
- No exact-word matching any more. What counts as approval is closed and tied to the offer number: a button click, `/approve 12`, or a whole message that is just one of a short list (yes, ok, approve, go, ja, akkoord, doe maar). Anything with a condition, like "yes but don't touch the DB", is not an approval: it becomes a narrowed offer you confirm with one click.
- Typing `/wait-what` while an offer is open neither approves nor cancels it. The agent re-explains, shows the same offer again, and your next answer counts as normal.

**Step 5: build, test, review.** The same quality loop as today: test first, implement, a separate reviewer checks it.

**Step 6: delivery.** What was done, the evidence, and what still isn't proven ("unknown" is an allowed answer).

---

## 3. When something is missing: fallbacks

The agent never gets stuck silently. It writes one line, for example:
> "Fallback: no test framework. I'll check it with a script instead. Full test coverage stays unproven."

The named fallbacks (§5):

| Fallback | When |
|---|---|
| Static diagnosis | the bug can't be reproduced |
| Direct check | no test framework |
| Existing-reference design | no Figma or design kit |
| Visual verification pending | no browser/device to check visuals |
| Reduced evidence | a tool fails |
| Instruction-only enforcement | the host has no hooks (Codex) |
| Single-provider review | no second model available |
| Manual contract check | an API can't be called |
| Inspect-first | the request is vague |
| Conditional design | a design choice is still open |
| Measurement-limited analysis | performance can't be measured reliably |
| Offline rehearsal | a migration can't be tried on real data |
| Fail closed + diagnosis | the approval checker itself breaks |

At the end, delivery lists only the gaps that remain.

**Work only pauses for:**
1. a question to you that's still open (rules or approval);
2. missing permission for the work;
3. a choice that changes what gets built and that only you can make;
4. anything touching secrets, production, identity or unclear safety;
5. actions that always need your OK (install, commit, push, deploy, delete);
6. a check that can't honestly pass, which only stops it from saying "done".

---

## 4. CSS: one on/off switch

One small file in your home folder. Every agent on your machine is told to read it (one line in the Claude and Codex global instructions, added during installation with your OK; the live tests check that each one really does). The Claude Code hook reads it directly:
`~/.workflow-axa/settings.json` → `{ "css": "off" }` or `{ "css": "on" }`

- **off** (the default on every new install, and whenever the file is missing or broken): the AI never writes CSS. It reuses existing classes or asks which element to copy, like today.
- **on**: the AI may write CSS when the task needs it, like building a Figma frame or a design change you ask for. It still reuses existing classes first, lists the style files in the offer and does a visual check.
- **It works immediately.** Switching off stops CSS writes straight away, even in a task you already approved. Switching on doesn't widen an approved task: CSS needs an offer that lists the style files.
- **Set it once, not in 90 places.** Run `settings.py css on` yourself, or say "turn CSS on" and it asks you one yes/no question. The AI can't flip it by itself, not even through the script: the hook blocks that without your yes.
- **Updates keep it.** Reinstalling or upgrading never resets your setting.
- **Projects can only be stricter.** A project can say `css: never` (for example a client with a locked design system). A repo can never turn it on, so cloning one doesn't change anything.
- **Why per machine:** you develop locally. Your machine is on; a junior's fresh install is off without them doing anything. It protects against the AI writing CSS, not against people (anyone can edit their own settings).
- In Codex it's followed as an instruction only, because Codex has no hooks.

"CSS" includes inline styles, Tailwind classes and CSS-in-JS, so it can't slip in another way.

---

## 5. Comments: the code is the truth (new)

**Why:** an agent reads `// returns the gross total` above code that returns the net total, believes the comment and makes a wrong decision.

1. **When reading:** a comment is a claim, not proof. The code shows what *happens*, so the AI never trusts a comment about that. But the code isn't always what *should* happen: if the comment describes an intended rule (public docs, a spec, a test name), the mismatch is reported as a **possible bug**, not "fixed" by deleting the comment.
2. **New code:** no comments. Names, types, small functions and tests carry the meaning. Allowed exceptions: licence headers, a link to a vendor/platform bug we can't fix, public API docs, tool directives (like `prettier-ignore` or PHPStan types), and an issue link for a constraint code can't express. A project can add its own exceptions (for example "PHPDoc on public methods" in Laravel).
3. **Lines it's already changing** (not the whole file): stale comments there get deleted, or the code gets renamed so the comment isn't needed. A comment like "IMPORTANT, do not remove" is checked first (code, git history). If it's true, it becomes a test or lint, or stays. If it can't be verified, it **stays**, unless the offer names its removal and you approve it.
   **Tool annotations are not comments:** PHPDoc/PHPStan types, decorators, `eslint-disable`, `@ts-expect-error` and similar are read by tools, so they stay unless the offer replaces them and the checks still pass.
4. **Code outside the task:** not touched. Bad comments there are listed as "comment debt".

**`/no-comments src/billing`** cleans a folder or the current diff on request: a fresh reviewer marks each comment delete / keep (with reason) / reshape; you get one offer; after approval it deletes and renames, then runs tests and the type check. **Removing comments must never change behaviour.**

---

## 6. `/wait-what` (new, from Matt Pocock)

Type `/wait-what` when a message didn't land. The agent re-explains that same message: a few lines of context first (what we're doing, where we are), then the point in short plain sentences, using the project's own terms. It repeats the open question unchanged. It does no new work, changes no offer, and never counts as your answer.

---

## 6b. Where the flows (bug, feature, new project...) are defined

**Flows are not skills.** Skills are building blocks (tdd, code-review, grilling, ui-design...). A flow is a short recipe that says which blocks to use, in which order, for one kind of job. The router picks a recipe; the recipe calls the skills.

Why not route straight to a skill? The same skill is used by many jobs (tdd is used by bug, feature and refactor). If the order lived inside each skill, it would be copied nine times, which is exactly today's maintenance problem.

- **One index file**, `skills/workflow/flows/INDEX.md`: one line per flow (name, when to use it, file).
- **One file per flow**, same template every time, about 40 lines. When-to-use lives only in the index; the approval rules live only in the common steps, so a flow file lists only its exceptions (like a migration needing a second OK for the live step).
- **The validator checks** that the index and files match, and that every skill a flow uses exists.
- **Add a flow:** copy the template, add one line to the index, add a few example prompts and one test. **Change a flow:** edit one file. **Improve a flow:** when a task goes wrong, the lesson goes into that file, or becomes a test.
- **You own the flows.** The agent proposes changes as a normal offer.

---

## 7. Skills: 21 become 19

**Merged (3 into 2), and why:**
- **workflow-doctor → rule-maker** (new `diagnose` mode). Both answer "is my setup OK?", and rule-maker already has the script that does the checks. One entry point instead of two.
- **task-status + resume-task → `resume`.** Both start by comparing the task records with the code. Status stops there; resume continues. One skill, modes `status`, `continue` and `handoff` (a short note so another session can pick up).

**Archived (not loaded any more; licences kept):**
- implement-spec: it does the same as workflow-execute.
- retro: rarely used. Its session-digest script stays, because the plan uses it to measure.
- simple-english: becomes the text behind `/wait-what` and delivery.

**New:** `/interrogate` (two agents try to break a plan or change by actually running things, and report only), `/no-comments`, `/wait-what`.

**Improved:** workflow (recipes, fallbacks, the one question), ui-design (reads the CSS switch), rule-maker (rules question; a correction you give twice becomes a test or lint proposal), code-review (checks comments, how hard the code is to follow, and what could break outside the diff).

**Unchanged:** grilling, tdd, plan-review, codebase-design, domain-modeling, writing-for-agents, codebase-map (the report looks the same).

---

## 8. What we take from pstack and Matt Pocock

**Taken (adopted or adapted):**
- pstack: no-comments, blast-radius (what could break elsewhere), attack-the-premise and fix-root-causes (bugs), explain-the-number and the benchmark checklist (performance), subtract-before-you-add (refactor), test behaviour not internals (tdd), minimize reader load (review), guard the context window, prove it works, restate intent, interrogate, how/why for investigations.
- Matt Pocock: wait-what, handoff, prototype (throwaway try-outs for UI and new projects), questionnaire (when a decision belongs to a client or another team), the bug-diagnosis loop, small composing skills, "compose before adding new skills".

**Not taken, and why:** pstack's auto-PRs, forced delegation, swarm/arena and the decision-log file (FINDINGS/DECISIONS already do that); Matt's issue-tracker planning (wayfinder), auto-commits and PR writer (pushes need your OK).

---

## 9. Hooks: 5 become 2

- **Removed:** `plain_reply` (punctuation complaints), `phase_reads` (reading reminders), `truncated_read` (warnings on partial reads). Their useful checks move to delivery or tests.
- **Rebuilt:** the big approval hook becomes a small **offer checker**: "is there an approved offer that covers this file write?" It keeps today's safety guards (git commit/push, installs, bulk deletes) and adds the CSS switch check.
- **Kept, but only as a warning:** `duplicate_skills`.
- Old approvals from current tasks keep working through a frozen copy of today's checker (with the checkpoint-3 fixes). It's removed only after two releases **and** when no active task still relies on it.

---

## 10. How we build it: 8 checkpoints

You approve the plan once. Each checkpoint ends with tests green and a short report.
1. **Your real session becomes tests**, and today's speed is measured (approval messages per task).
2. **Validator fix:** it reads the skill list itself, so a new skill touches 2–3 files.
3. **Quick relief:** your three session problems need 0 extra approvals, even before the big change.
4. **Recipes (with the index and template), fallbacks, the rules question, the comment rules, the CSS text.** Anything that depends on the new offer system is written and tested here but only switched on in step 5, so it never clashes with the old approval hook.
5. **The offer system and the CSS switch**, first running silently next to the old one to compare, then live tests in Claude Code and T3.
6. **Remove the old machinery** (old approvals keep working).
7. **Skills:** merges, `/interrogate`, `/no-comments`, `/wait-what`.
8. **Docs, a pilot on real work, switch-on**, only with your OK.

Commits, pushes, global installs and paid test runs still need your separate OK each time.

---

## 11. What I need from you

- **A. Approve the plan** (after both models agree on every section). CSS starts **off** everywhere; you switch your own machine on once.
- **B. A limit for live tests.** My proposal: only Claude Code and Codex/T3 on your existing plans, at most 20 runs in total, and stop early if a plan hits its usage limit. Anything billed per use (an API key) is excluded unless you give it a money cap.
