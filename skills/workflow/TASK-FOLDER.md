# Task folder

`docs/plans/YYYY-MM-DD-<slug>/`, committed. One folder per piece of work, claimed before investigation (see SKILL.md step 3) and never switched. Resume by reading its records, never overwriting its history. Keep supporting SQL, CSVs, logs, and other relevant evidence alongside them.

| File | Holds |
|---|---|
| `PLAN.md` | Issue, opened date, status, goal, scope, what done looks like, required doc updates, outcome |
| `TODO.md` | The work items — source of truth while implementing |
| `FINDINGS.md` | Investigation history: findings, actions, dead ends, blockers, regressions, audit findings, `⚠️ untested` lines |
| `DECISIONS.md` | Choices with more than one defensible answer, each with its reason |

Create `DECISIONS.md` on the first decision, not before. When the project keeps ADRs in `docs/adr/`, a hard-to-reverse architecture decision gets an ADR there and a one-line link here.

## PLAN.md

Restate the issue using confirmed facts; list unanswered questions explicitly. Use `unknown` for details not yet established. Maintain status (`open`, `investigating`, `blocked`, `done`) as work proceeds. Outcome stays `pending` until verified; when blocked, record the reason and next step. Every clarification must be answered before completion.

## TODO.md

One item per piece of work, specific enough that someone else could pick up any single one. Doc updates are items, named by file.

```markdown
- [ ] (lane 1) not started
- [~] (lane 2) in progress — one per running lane; where the last agent stopped
- [x] (lane 1) done — proof: <test name, command and result, or file:line checked>
```

## FINDINGS.md

Dated, newest last; append findings, actions, and dead ends as they happen, with evidence and implications. Preserve earlier entries; append corrections when understanding changes:

```markdown
- YYYY-MM-DD — <what was found>, <where>, <what it means for the task>
- ⚠️ untested — <what was not covered, and why>
```

The `⚠️ untested` line is mandatory when tests are skipped: without it, "we skipped tests" and "tests passed" read the same three weeks later.
