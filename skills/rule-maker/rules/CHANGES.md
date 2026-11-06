# Rules changes that affect projects

Newest first. Each entry says what changed and what a project's own rules must be checked for. `scripts/rules_stamp.py` prints the entries newer than a project's `workflow-axa rules checked` line, so an audit after an update looks only at these.

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
