# Project instructions and documentation

Read to audit, apply or check a project's instructions and documents, or when a workflow phase finds, updates or checks a task's documents.

## The shared principle

Structure is standardized by responsibility and discoverability, not by fixed headings. Valid existing rules still pass. A project changes to this shape only through an approved proposal for that repository. Core coverage is proportional: only what the work needs.

## Where each thing belongs

| Location | Holds |
|---|---|
| AGENTS.md | The canonical entry point (see [The AGENTS.md shape](#the-agentsmd-shape)). |
| CLAUDE.md | The import of AGENTS.md (see [CLAUDE.md](#claudemd)). |
| CONTEXT.md | The product, its users and the project's terms. No implementation details. |
| docs/ARCHITECTURE.md | Components, boundaries, data flow and ownership. |
| docs/adr/ | One file per lasting trade-off a future reader would question. |
| Nested index (docs/README.md, a package's AGENTS.md) | The documents of one area, in the same index format. |
| plans/ and archive/ at the root or under docs/; the root CHANGELOG.md or CHANGES.md | Task records and preserved history. Never current rules. |

Keep an existing location that the index reaches, such as a README section. Create a file only when it has content. A one-word Markdown document name is written in capitals (DESIGN.md, SETUP.md, like README.md); rename a lowercase one with `git mv` and fix its links. Names of several words (data-and-security.md), vendored files and files a tool loads by name keep theirs. A new project starts with AGENTS.md, CLAUDE.md and CONTEXT.md.

Shared standards stay in the installed rules library. Project files state project facts, decisions and approved exceptions, and refer to the library instead of copying it.

For the CONTEXT.md and ADR formats, read `../domain-modeling/GLOSSARY-FORMAT.md` and `../domain-modeling/ADR-FORMAT.md`. In a project, the file the format calls GLOSSARY.md is named CONTEXT.md.

## The AGENTS.md shape

AGENTS.md is short: the advisory size is about 1,200 words. It holds four things:

1. Essential rules: ownership, protected or generated files, and project decisions an agent must know on every task.
2. Boundaries and safety rules: what needs the owner's approval, what stays out of scope.
3. The common build and test commands. Complex setup and environment details go to a referenced document.
4. The index: one entry per document, with a link, one line on what it holds, and a "Read when" line.

Safety and boundary rules stay in AGENTS.md even above the advisory size; only their details move. A block a tool manages inside AGENTS.md (such as the Next.js `next dev` block) stays byte-identical; write around it.

```markdown
# Shop API

Shared standards: the installed workflow-axa rules library. Project rules here win where they are stricter.

## Rules
- `src/billing/` owns invoices. Other modules call its service, never its tables.

## Boundaries
- Deployments and dependency changes need the owner's approval.

## Commands
- Build: `npm run build`. Test: `npm test`. End-to-end tests need the local stack (docs/SETUP.md).

## Index
- [CONTEXT.md](CONTEXT.md): product, users and terms. Read when a name or a user need is unclear.
- [docs/SETUP.md](docs/SETUP.md): local stack and environment variables. Read when tests need services.
```

## Nested indexes and packages

Keep indexes shallow: AGENTS.md may link a subordinate index, which links its own documents, so not every document needs a root entry. A level deeper than two below AGENTS.md is reported as advisory.

A nested package with its own AGENTS.md gets its own CLAUDE.md beside it, and an index above links that AGENTS.md.

## CLAUDE.md

CLAUDE.md, or `.claude/CLAUDE.md`, is the one line `@AGENTS.md`. Blank lines and HTML comments, such as a required-read marker, may sit beside it. If the repository is used with Claude Code (record the owner's host choice), a missing CLAUDE.md means Claude Code loads no project rules: add it with that one line.

## Covers hints

A document relates to itself and the paths it links or names. A changed file also relates to the README.md and top-level docs/*.md of the nearest folder above it, below the root, that has either. An index entry may add an optional hint for more, on the entry line or the line under it:

```markdown
- [docs/BILLING.md](docs/BILLING.md): invoice rules. Read when billing changes.
  Covers: src/billing/, src/payments/**
```

Hints are directory-level patterns: `*` is one name, `**` any depth. A per-file map is never kept. A hint that matches no path is reported as stale.

## Check with docs_check.py

Paths here are relative to this folder, so a phase skill's `../rule-maker/scripts/docs_check.py` is the same script. It is read-only.

```bash
python -X utf8 -I scripts/docs_check.py <project-root>
python -X utf8 -I scripts/docs_check.py <project-root> --changed <path> [<path> ...]
python -X utf8 -I scripts/docs_check.py <project-root> --changed-from-git
```

The plain check reports the structure: the AGENTS.md and CLAUDE.md shape, links, reach, cycles, depth, size, repeated paragraphs, required-read markers and hints, plus untracked entry points it learns of from Git; it checks no facts. Without AGENTS.md, it treats CLAUDE.md as the entry point. `--changed` and `--changed-from-git` add the related documents with the reason for each, and the named facts in those documents (paths, manifest commands, versions) as matched, contradicted or not-checkable.

## Claim review

After a `--changed` or `--changed-from-git` run, review every affected claim, not only the facts the script named. An affected claim is every code-related claim in each related document, any claim anywhere in those documents about a changed file, and each non-code claim in the same passages. When the script relates an index by its Covers hint, review the document that entry links. Skip documents the output marks historical, except a changelog entry this task added or changed: it is current, so review its claims.

1. Check a code claim against source, configuration and tests, and a non-code claim against its own evidence.
2. Record it as verified (with the evidence), contradicted (with the evidence), not verified (with the reason), or, for a non-code claim without evidence of its own, not verifiable. A configured command not run is not verified (not run), and contradicted only when an approved run shows it wrong.
3. When code and document disagree, decide from the evidence which side is wrong. When the code and its tests agree, the document is wrong, unless the document is the contract (an API spec, a partner promise, a legal or financial rule). Otherwise, report it.
4. Report a changed behavior (the diff since the starting `git status`, else the tickets' scope) that no related document mentions as an undocumented change, with the document where it would belong. Create a document only when an approved ticket includes it.

In audit or check, record the verdict only. Correct a document or code only inside an approved task's scope. Never call a document accurate because a check passed. A matched path, command or version supports only that fact, not the claim around it.

## Severity

Two documentation conditions block:

1. A broken link to a document marked required (the `workflow-axa:required-read` marker). docs_check reports it as blocking and exits 1.
2. A contradiction unsafe to build on: the evidence cannot tell which side is right, and a wrong guess could change behavior that users, data, money, security, permissions or an external contract depend on, or the task's own acceptance. It blocks the task: set the phase to blocked, put the owner's question on the Blockers line, and start no work that builds on the contradicted claim. Other tickets continue as `../workflow/TASK-FOLDER.md` says for blocked work. This holds even when this task caused it. The fix goes to deliver step 7 after the owner answers. At delivery, the checkpoint update and a partial Outcome with the owner's question record the block.

Both add to every approval, safety hook and blocking protection, and replace none. Delivery reports in this order: unsafe contradictions, warnings, notes, contradictions safe to build on, undocumented changes, claims not verified or not verifiable, and verified claims with their evidence. A docs_check warning or note about a claim is reviewed as that claim and reported once.
