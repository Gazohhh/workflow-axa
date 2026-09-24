# workflow-axa

Our development flow, as a skill. One way of working, so a task looks the same whoever picked it up.

Every task runs through subagents, writes tests, keeps a TODO and handover folder, updates the architecture and flow docs it touches, and ends with an audit of the staged changes — because the failure worth preventing is not a broken test, it is a green suite beside a call site nobody looked at.

## Install

Two routes. **Pick one** — installing both leaves you with the skill twice.

### Any agent (Claude Code, Codex, Cursor, …)

```bash
npx skills@latest add Gazohhh/workflow-axa --skill=workflow
```

Update later with `npx skills update`.

### Claude Code as a plugin

```
/plugin marketplace add Gazohhh/workflow-axa
/plugin install workflow-axa@gazohhh
```

Read-only and updates on its own. Use this one unless you want editable local copies.

Either way, type `/workflow` in your agent afterwards.

Two things worth knowing about the `npx` route:

**On Windows, add `--copy` if the install fails.** The CLI keeps one canonical copy in `.agents/skills/` and symlinks each agent's directory to it. Windows symlinks need Developer Mode or an elevated shell; `--copy` writes independent copies instead and sidesteps it.

**Do not edit the installed copy.** `npx skills update` deletes the skill's directory and rewrites it — no merge, no backup, no warning. Edits belong in this repo, then pulled down by updating.

### Dependency

The skill hands underspecified requests to `grill-me`, which is not part of this repo:

```
/plugin install mattpocock-skills
```

Install it once. The skill tells you if it is missing. Pick one install route for those skills and stick to it — installing them both as a plugin and via `npx skills` leaves you with every skill twice.

## Using it

Type `/workflow`, then describe the task — or paste a prompt you prepared elsewhere.

Three ways in, and the skill picks:

| What you bring | What happens |
|---|---|
| A prepared prompt | Straight to implementation |
| A bare goal or a symptom | Interviewed first, then implementation |
| A typo, a string, a version bump | Changed and audited, nothing else |

It stages the result and stops. **Commits stay yours.**

## Making it fire without the command

The skill's description means the agent usually reaches for it on its own. To make that non-negotiable in a given project, paste this into that project's `AGENTS.md` — or its `CLAUDE.md` if it has no `AGENTS.md`:

```markdown
## How we work

All implementation work — features, bugfixes, refactors — follows the team flow:
prepared prompt, subagents, tests, a task folder under `docs/plans/`,
architecture and flow docs kept in step with the code, and an audit of the staged changes before committing. In Claude Code, run `/workflow`.
```

A description is a suggestion the agent weighs. A line in the rules file is an instruction it follows.

### If the project has both files

`AGENTS.md` is the standard the other tools read — Codex, Cursor, Copilot, Windsurf. Claude Code reads `CLAUDE.md` only. Keep the content in `AGENTS.md` and make `CLAUDE.md` one line:

```markdown
@AGENTS.md
```

Do not symlink them. On Windows, git checks a committed symlink out as a text file containing the word `AGENTS.md` — no error, and every instruction silently gone.

## The task folder

Lives at `docs/plans/YYYY-MM-DD-<slug>/`, committed. It is the point of the whole flow: open a new chat, hand the branch to someone else, come back in three weeks — the folder says what was done, what is left, what was learned, and where the last agent stopped.

| File | Holds |
|---|---|
| `PLAN.md` | Goal, scope, what done looks like, which docs the task must update |
| `TODO.md` | `[ ]` not started, `[~]` in progress, `[x]` done with its proof |
| `FINDINGS.md` | Discoveries, blockers, audit findings, as they happen |
| `DECISIONS.md` | Choices and their reasons; created on the first one. Hard-to-reverse architecture calls also get an ADR in `docs/adr/` |

When a folder for the work already exists, the skill continues it instead of starting another.

A task that skipped its tests says so in `FINDINGS.md`, in writing, with a ⚠️. That is deliberate. Silence there is indistinguishable from success.

## Docs are part of the change

When a task changes architecture, ownership, dependencies, data flow, user flow, build flow, or runtime behaviour, it updates the project's existing docs that describe it, in the same task. The verifier and the audit both compare docs against code, so a stale diagram counts as a finding just like a missed call site.

## Versioning

Versions are git tags, matched by `.claude-plugin/plugin.json` and described in [`CHANGELOG.md`](./CHANGELOG.md).

The `npx skills` route ignores versions entirely — it tracks the git ref and a content hash, recorded in each project's `skills-lock.json`. The version is for the plugin route and for humans: when someone says "the audit behaves differently than last week", a tag and a changelog entry answer that and a hash does not.

Releasing:

```bash
# bump "version" in .claude-plugin/plugin.json, add a CHANGELOG entry, then:
git tag v1.0.0
git push --tags
```
