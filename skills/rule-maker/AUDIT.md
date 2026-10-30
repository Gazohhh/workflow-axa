# Full rules audit versus task readiness

Use this procedure for a requested audit of project/agent rules. Ordinary task readiness remains a bounded check of the next task, not a certificate for the entire repository. `audit` defaults to the supplied project/rules scope, read-only; explicitly narrow it when the user asks. `setup` and `update` still require the existing proposal/approval process. An audit is not permission to implement its findings.

## Inspect the effective sources

Establish the requested roots, areas and hosts; preserve coverage gaps. Inspect shared library identity and fingerprints, project root/scoped rules and imports, relevant host settings when accessible, explicit owner decisions, task records and relevant supplied memory. Do not crawl unrelated private memory, transcripts or credentials. Use [rules/POLICY.md](rules/POLICY.md) for competing instructions. An exported pack proves only its captured contents, not the live installation. Flattened export filenames are not necessarily broken repository paths.

Use the read-only `scripts/audit_installation.py` with explicit candidate installation paths and, when authorised, `--check-global`. It compares candidates against the trusted package running the check. It does not search the internet, pick a winning duplicate, execute host CLIs, alter files or prove which copy the host selected. Check plugin, user and repository copies actually relevant to the host. Report supplied/disk identity separately from observed session loading, followed behaviour and enforced actions.

## Review every relevant dimension

| Dimension | Establish and report |
|---|---|
| Scope and authority | Which requirements are current, who decided them, affected area, exceptions; a memory suggestion is not a new owner decision. |
| Coverage | Actual stack/versions and shared module, project guidance, reviewed fallback or material gap per area. TypeScript does not substitute for Angular/Ionic/Capacitor. |
| Correctness | Version-sensitive claims against installed configuration and matching primary docs. Separate verified fact, recommendation and unverified history. |
| Contradictions | Root/scoped/global rules, relevant memories, artifact retention, review history, documentation and concurrency requirements. Expose both sides before proposing a choice. |
| Verification safety | Current command, prerequisites/implicit builds, effective backend and mock isolation, permitted writes, quiet-host needs, current baseline and actual gate proof. |
| UI authority | The local ui-design route, area-specific mode, designated kit/reference and preview boundary. Kit files or styling classes alone grant nothing. |
| Placement and language | Shared standards versus local contracts; concise routing versus long runbooks; plain explanations without forced vocabulary or arbitrary quotas. |
| Discoverability | Actual host/profile paths, imports, scope selectors and worker instructions. A manual skill read does not prove ordinary-prompt loading. |

Do not make different projects identical. Retain intentional Git restrictions, architecture, test layouts, line endings, generated-output contracts, environment warnings and design decisions. A numeric test total or archived GREEN badge is not current proof. Correct misleading technical wording without enabling the feature it describes. Do not rewrite source code, move glossaries/ADRs or weaken safety rules during a rules audit.

## Findings and changes

In chat or the existing task record, list each meaningful issue once: source/location, exact conflict or gap, consequence, proposed smallest change, authority needed and verification. Distinguish confirmed defect, policy proposal, coverage gap and unknown. Keep already-correct rules and acknowledged corrections; do not report fixed historical failures as current defects. A proposed policy change must show **current rule -> proposed rule -> behavioural effect -> reason -> required approval**, including preservation of previous decisions.

End with a scoped verdict: task readiness, audit coverage, installed version, host loading, framework coverage, safety limits and unresolved choices are separate. Never compress them to "all rules ready". Missing live files/hosts stay NOT VERIFIED. Obtain bounded approval before edits; rerun the original task's readiness after authorised changes.

## Acceptance cases

Test ordinary prompts and explicit skills, missing/old global references, mixed installs, root and nested areas, stale memory versus current policy, partial answers, UI without approved styling, production-target checks, unrequested builds and quiet-host conflicts. Observe reads, commands and final changes rather than relying on the agent saying it complied. Package tests are not live-model results. Use disposable fixtures and existing evaluation records; no per-run report tree.
