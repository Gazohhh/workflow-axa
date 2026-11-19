# The shape of AGENTS.md, CLAUDE.md and indexes

Read this when you audit, set up, apply or write a project's AGENTS.md, CLAUDE.md or document index, or when docs_check reports their shape, depth or Covers hints. [DOCS.md](DOCS.md) owns where each document belongs, the claim review and severity.

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
