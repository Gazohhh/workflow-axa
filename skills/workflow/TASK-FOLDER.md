# Task folder

`docs/plans/YYYY-MM-DD-<slug>/`, committed. One folder per piece of work; continue it rather than start a second.

| File | Holds |
|---|---|
| `PLAN.md` | Goal, scope, what done looks like, which docs this task must update |
| `TODO.md` | The work items — source of truth while implementing |
| `FINDINGS.md` | Discoveries, blockers, regressions, audit findings, `⚠️ untested` lines |
| `DECISIONS.md` | Choices with more than one defensible answer, each with its reason |

Create `DECISIONS.md` on the first decision, not before. When the project keeps ADRs in `docs/adr/`, a hard-to-reverse architecture decision gets an ADR there and a one-line link here.

## TODO.md

One item per piece of work, specific enough that someone else could pick up any single one. Doc updates are items, named by file.

```markdown
- [ ] (lane 1) not started
- [~] (lane 2) in progress — one per running lane; where the last agent stopped
- [x] (lane 1) done — proof: <test name, command and result, or file:line checked>
```

## FINDINGS.md

Dated, newest last:

```markdown
- YYYY-MM-DD — <what was found>, <where>, <what it means for the task>
- ⚠️ untested — <what was not covered, and why>
```

The `⚠️ untested` line is mandatory when tests are skipped: without it, "we skipped tests" and "tests passed" read the same three weeks later.
