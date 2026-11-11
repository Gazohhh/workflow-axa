# Full rules audit versus task readiness

Use this procedure for a requested audit of project/agent rules. Ordinary task readiness remains a bounded check of the next task, not a certificate for the entire repository. `audit` defaults to the supplied project/rules scope, read-only; explicitly narrow it when the user asks.

## Inspect the effective sources

Establish the requested roots, areas and hosts; preserve coverage gaps. Inspect shared library identity and fingerprints, project root/scoped rules and imports, relevant host settings when accessible, explicit owner decisions, task records and relevant supplied memory. Do not crawl unrelated private memory, transcripts or credentials. Use [rules/POLICY.md](rules/POLICY.md) for competing instructions. An exported pack proves only its captured contents, not the live installation. Flattened export filenames are not necessarily broken repository paths.

Use the read-only `scripts/audit_installation.py` with explicit candidate installation paths and, when authorized, `--check-global`. It compares candidates against the trusted package running the check. It does not search the internet, pick a winning duplicate, execute host CLIs, alter files or prove which copy the host selected. Check plugin, user and repository copies actually relevant to the host. Report supplied/disk identity separately from observed session loading, followed behavior and enforced actions. Three versions differ by design: the package (plugin.json), the rules library (rules/version.json) and the artifact policy revision (workflow/ARTIFACTS.md). Judge the global artifact block with `workflow/scripts/global_policy.py --check` (bytes), never by comparing its revision with the package version.

## Review every relevant dimension

| Dimension | Establish and report |
|---|---|
| Scope and authority | Which requirements are current, who decided them, affected area, exceptions; a memory suggestion is not a new owner decision. |
| Coverage | Actual stack/versions and shared module, project guidance, reviewed fallback or material gap per area. TypeScript does not substitute for Angular/Ionic/Capacitor. |
| Correctness | Version-sensitive claims against installed configuration and matching primary docs. Separate verified fact, recommendation and unverified history. |
| Contradictions | Root/scoped/global rules, relevant memories, artifact retention, review history, documentation and concurrency requirements. Expose both sides before proposing a choice. |
| Verification safety | Current command, prerequisites/implicit builds, effective backend and mock isolation, permitted writes, quiet-host needs, current baseline and actual gate proof. |
| UI authority | The local ui-design route, area-specific mode, designated kit/reference and preview boundary; project UI rules agree with DESIGN.md (no CSS, copy existing elements with their wrapper, ask when nothing matches) and with each other. A stricter project rule (for example "candidate entries need the owner's OK") wins and is stated where agents read it. |
| Placement and language | Shared standards versus local contracts; each document's responsibility ([DOCS.md](DOCS.md)); concise routing versus long runbooks; plain explanations without forced vocabulary or arbitrary quotas. |
| Discoverability | docs_check findings; actual host/profile paths, imports, scope selectors and worker instructions. Check ordinary-prompt loading in a fresh session, not by reading the skill manually. |

Apply [the shared principle](DOCS.md#the-shared-principle). Retain intentional Git restrictions, architecture, test layouts, line endings, generated-output contracts, environment warnings and design decisions. A numeric test total or archived GREEN badge is not current proof. Correct misleading technical wording without enabling the feature it describes. An audit only proposes: it never rewrites source code, moves glossaries/ADRs or weakens safety rules.

## Proposal

The audit ends in one proposal with:

1. The problems, each listed once with its location: duplicated, conflicting, missing, stale or misplaced instructions, and project details that belong in documentation. For each, give the exact conflict or gap, its consequence, the smallest change, the authority needed and the verification. Label it confirmed defect, policy proposal, coverage gap or unknown.
2. The exact files it changes.
3. The proposed AGENTS.md and indexes. Every safety and boundary rule stays in auto-loaded text: production or misleadingly named hosts, live data, secrets, destructive or data-writing commands and approval boundaries. List a command that writes data outside a disposable local test store, or reaches a real backend, as needing the owner's OK, with what it writes, after checking its real target.
4. Document moves.
5. Migration risks: protections that could be lost, links that could break, tools that read old paths.
6. The auto-loaded words before and after, per host. Claude Code: CLAUDE.md (or `.claude/CLAUDE.md`) and its imports, `.claude/rules/*.md` (path-scoped ones only when their paths match) and, counted separately, nested CLAUDE.md files loaded on demand; `CLAUDE.local.md` counts for the person who has it; an AGENTS.md that CLAUDE.md links without importing does not count. Codex: the AGENTS.md chain. Count tracked files only: a fresh clone has no untracked ones.
7. The claim-review verdicts for the sample.
8. For each policy change: **current rule -> proposed rule -> behavioral effect -> reason -> required approval**, including preservation of previous decisions. Every rule the proposal drops or moves out of auto-loaded text gets a row.

Keep already-correct rules and acknowledged corrections. Do not report fixed historical failures as current defects.

End with a scoped verdict: task readiness, audit coverage, installed version, host loading, framework coverage, safety limits and unresolved choices are separate. Never compress them to "all rules ready". Missing live files/hosts stay NOT VERIFIED.

Write the proposal in the requesting task's FINDINGS.md or at a path the user names. Never write it inside the audited repository without approval. Obtain bounded approval before edits, and rerun the original task's readiness after authorized changes.

## Acceptance cases

Test ordinary prompts and explicit skills, missing/old global references, mixed installs, root and nested areas, stale memory versus current policy, partial answers, UI without approved styling, production-target checks, unrequested builds and quiet-host conflicts. Observe reads, commands and final changes rather than relying on the agent saying it complied. Use disposable fixtures and existing evaluation records; no per-run report tree.
