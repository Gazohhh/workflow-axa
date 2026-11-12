# Rules changes that affect projects

Newest first. Each entry says what changed and what a project's own rules must be checked for. `scripts/rules_stamp.py` prints the entries newer than a project's `workflow-axa rules checked` line, so an audit after an update looks only at these.

## 1.8.8 (2026-11-12)

- SOURCES.md, TESTING.md and RUST.md: source-project names and wording that pointed to a source project are removed; the skills that came from other projects are now the package's own. No rule changed. **Project action:** none.

## 1.8.7 (2026-11-11)

- The one-word modules are renamed to capitals: DESIGN.md, REACT.md, PHP.md, OPERATIONS.md and the other sixteen. Their rules did not change. A one-word Markdown document name is written in capitals (rule-maker DOCS.md). **Project action:** update project links to a module, such as design.md, to its new name; rename a project's own one-word documents with `git mv` at the next audit.

## 1.8.6 (2026-11-11)

- READINESS.md: run `scripts/docs_check.py` and use its facts as advisory input. READY stays the agent's judgment. Two documentation conditions block: a broken link to a required-read document, and a contradiction the agent judges unsafe to build on. Every other finding is reported and never blocks by itself. In the rule-maker structure, AGENTS.md is the entry point and CLAUDE.md imports it. Valid existing rules still pass in their current files and shape. **Project action:** none. Fix a broken required-read link before the next workflow task.
- design.md rule 4: an element is chosen by the job it does for the same user. That user comes from the task's purpose statement. Without a task, the user and goal that the request or CONTEXT.md names stand in for it. The reason for the choice is recorded. The job only chooses among existing elements and never permits a new style. **Project action:** reword project UI rules that choose an element by its look alone; otherwise none.
- design.md: a change on the small change route (workflow VISUAL-REVIEW.md "Small change") needs no screen diagram. Every other UI-visible change still shows one. **Project action:** none.
- CORE.md, START.md and the other rules files: wording and American spelling only. Release history is removed. Notes on what a check does not prove moved to the package's docs/EVALUATION.md. No rule changed. CORE.md's UI sentence is unchanged. START.md now points to design.md for the UI rules and keeps examples of them. **Project action:** none.

## 1.8.5 (2026-11-06)

- CORE.md: after the exact mimic question, list only same-tag existing elements and nothing else (no plain-HTML or add-a-style alternatives). **Project action:** none.

## 1.8.4 (2026-11-06)

- CORE.md spells out the no-match UI case in the always-loaded rules: stop that element, ask exactly "I couldn't find a matching style for [element]. Is there an existing element I should mimic?", offer at most existing same-tag elements, never new CSS, a new class, another tag's classes or plain HTML as options, small edits included. **Project action:** none.

## 1.8.3 (2026-11-06)

- READINESS.md documents optional required-read declarations: `<!-- workflow-axa:required-read phases=specify,execute,deliver path="tests/README.md" -->` in the project root AGENTS.md or CLAUDE.md. In Claude workflow sessions the hook waits for a complete current-context read of each declared file before the named phase starts and before report validation or rendering. **Project action:** none required. A project whose root rules say a file must be read before planning, implementation or delivery may add a declaration with the owner's approval. A malformed declaration blocks those boundaries until it is fixed.

## 1.8.2 (2026-11-04)

- Clarify D14 permission: no agent-recommended plain-HTML fallback and no blanket yes treated as that exception. Preserve legitimate element-specific owner instructions and stricter project rules. **Project action:** no automatic rewrite; reconcile contradictory guidance before the next affected UI unit. Related phase instructions now distinguish explicit paid-evaluation budgets and legacy approval recovery. No new external dependency or automatic deployment.

## 1.8.1 (2026-11-04)

- Consolidate workflow entry/readiness ownership in READINESS.md; RULES.md remains a compatibility pointer. No new application coding or UI policy. **Project action:** no rule-copy migration; check the affected shared references when using this candidate. This metadata does not accept an earlier delivery or D7–D10 on the owner's behalf.

## 1.8.0 (2026-11-03)

- A project may carry one line in its root AGENTS.md: `workflow-axa rules checked: <version> (<date>)`. Only a passed setup or audit writes it, with the owner's approval. It is information, never a requirement: a project without it is checked as before. **Project action:** none; add the line after the next passed audit.

## 1.7.0 (2026-11-03)

- Application UI: never write CSS (no stylesheet rules, `<style>` or `style=""`). Reuse existing classes and IDs, copying the whole class list, the tag and the wrapper. When nothing matches, ask exactly: "I couldn't find a matching style for [element]. Is there an existing element I should mimic?" Plain unstyled HTML only on the owner's explicit instruction. **Project action:** reword project rules or design docs that allow new CSS or inline styles, or that demand a kit for every change. Record an approved exception, such as runtime-only inline values, in the owner's words.
- A project rule for new code wins over an older neighbour in the code. **Project action:** none.
- An approved exception lasts as long as the owner's words say. **Project action:** exceptions in project rules name their scope and end.

## 1.6.0 (2026-10-31)

- Strict kit-only UI reuse. Replaced by 1.7.0. **Project action:** none beyond 1.7.0.

## 1.5.0 (2026-10-30)

- UI tasks name their design source and mode, and UI plans show a screen flow. **Project action:** a project with a design kit points to it from its rules.
- TypeScript: no nested ternaries in new or changed code. **Project action:** remove project rules that contradict it.

## 1.3.0 (2026-10-30)

- New or extended modules: angular, ionic, capacitor and operations (checks with side effects), plus additions to design, security, testing and performance. **Project action:** Angular, Ionic and Capacitor projects record their versions and who runs native builds. Every project names which builds, deploys, store uploads and device runs need the owner.

## 1.1.0 and earlier

- The baseline. A project with no line is checked against all entries above.
