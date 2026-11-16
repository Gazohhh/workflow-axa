# Flows

The router picks one recipe from this table, plus any modifiers, then loads only that recipe. A recipe is the order of steps for one kind of job; the skills it names do the work. Signals live only here. Approval rules live only in the common process ([../SKILL.md](../SKILL.md) §4, [../VISUAL-REVIEW.md](../VISUAL-REVIEW.md)); a recipe names only its exceptions.

| Recipe | Use when | File |
|---|---|---|
| bug | something behaves wrongly: an error, a wrong result, a regression, "it used to work" | [bug.md](bug.md) |
| feature | add or change what the product does for its users or callers | [feature.md](feature.md) |
| new-project | an empty or new repository, or setting up a project from scratch | [new-project.md](new-project.md) |
| ui | the work is mainly on screen: a layout, a component, a Figma frame, a visual fix | [ui.md](ui.md) |
| refactor | restructure code while keeping its behaviour | [refactor.md](refactor.md) |
| architecture | ownership, module boundaries, interfaces or a public contract are the question | [architecture.md](architecture.md) |
| performance | slow, heavy on memory or CPU, or a numeric target to meet | [performance.md](performance.md) |
| migration | data, schema, protocol, dependency upgrade or deployment change with existing consumers | [migration.md](migration.md) |
| docs-tests | only documentation, agent instructions or tests change | [docs-tests.md](docs-tests.md) |

**Router only (no file):** *Inspect* (explain, review, audit, diagnose without changing anything) answers with cited evidence: "how" traces the runtime path, "why" cites history (git log, DECISIONS). *Other* with a clear outcome assembles steps from the common process; a vague *Other* starts with Inspect.

**Modifiers**, added to any recipe:
- **UI**: anything a user sees on screen. Load `ui-design` before dependent planning.
- **Security**: authentication, secrets, permissions, untrusted input. Load the rules library's SECURITY module.
- **Compatibility**: saved data, public interfaces, versions others depend on. Load COMPATIBILITY; keep a deprecation path for public interfaces.

**Adding a flow:** copy [TEMPLATE.md](TEMPLATE.md), add one row here, and add its labelled prompts and behavioural case to `tests/behavioral/flows.json`. The validator checks that rows and files match and that every skill a recipe uses is registered.
