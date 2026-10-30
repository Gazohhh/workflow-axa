# Rules-readiness gate and shared rule maker

## Current checkpoint

User request: fix the missing project-rules check before /workflow, including the case where rule-maker was never invoked. Preserve the shared rules inside the skill, global references, existing specialists, project rules, history and local flowchart.

Scope: package-only candidate based on supplied 2.6.0. No application repository, installed user configuration or existing plans/ADRs are changed. User's request authorises this package revision; it is not project-setup or application implementation approval.

Implementation: add a mandatory read-only preflight before substantial planning/writes; a scoped setup/exception process; local shared framework references; a preview-first global reference helper; a declared-assessment/freshness checker; forward-only adapters and tests. No new external specialist, automatic updater, project rulebook copies or untested host action firewall.

Verification: see VALIDATION.md for observed results and limits. Live host gates remain unverified until piloted. Current release is explicitly a candidate.

## Decisions

D1: Valid existing rules pass without a rule-maker marker. Missing files alone do not establish semantics; placeholder files do not establish readiness.
D2: Read-only discovery/diagnosis is possible before setup; application work remains blocked. Setup approval and implementation approval are separate. Bootstrap may change only approved setup artifacts.
D3: A bounded explicit exception is possible for known coverage gaps, not unknown safety/identity/trust conflicts. No permanent global bypass.
D4: Shared rules live only in rule-maker/rules. Global files reference them; project files retain only local agreements. No bulk migration or unrelated policy rewrite.
D5: Validators inspect declarations/fingerprints and cannot authenticate human intent or guarantee model obedience. No invented all-scenarios/perfect score.
