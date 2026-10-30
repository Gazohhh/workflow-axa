---
name: plan-review
description: "Challenge a workflow plan before approval for unnecessary scope, missing decisions, duplicate features, weak acceptance criteria and AI-slop abstractions. Review only; never implement or approve for the user."
---

# Plan review

Review an existing workflow plan before the user approves implementation. Do not implement, alter approval or manufacture extra product requirements.

1. Read the task records, relevant project rules and enough current code/evidence to test the plan's claims.
2. Use installed `codebase-design` when abstractions/boundaries need challenge, `domain-modeling` when terminology/ownership is unclear, and `writing-for-agents` when the plan/agent instructions themselves are confusing. Use `research` only for external facts the plan depends on.
3. Establish current authority and the proposed delta from the last approved scope. Resolve revision/phase/review aliases from sources; distinguish baseline descriptions from implementation and acceptance. Flag contradictions before readiness, without rewriting history. Check requirement → evidence → actual gap → TODO → acceptance traceability. Look for an already-existing capability, unrequested features, missing callers/error paths, stale-code cleanup, vague tests and user-owned decisions the plan silently made.
4. Run the necessity check on every proposed helper/wrapper/service/manager/mapper/fallback/compatibility/config layer: what concrete problem requires it, can existing code express it, and would deleting it spread necessary complexity or simply simplify the design?
5. Apply a cold-reader check. A nontechnical reader must understand what changes and why; a technical reader must be able to locate exact evidence.
6. Return PASS / ISSUE / QUESTION / NOT VERIFIED findings with concrete evidence and a minimal recommendation. Do not praise generally, invent question quotas, create another plan, or approve on the user's behalf.

For planned tests/builds, use the active workflow ARTIFACTS.md/global policy to check the output location, concurrency, necessary evidence and cleanup condition. A proposed retention change must protect tool-owned/live outputs. Review in chat; do not create another plan, screenshot set or cleanup report without a request.

Apply the installed workflow RULES.md readiness gate. Read-only review may identify gaps, but do not label a plan approval-ready while required rules are missing/conflicting or a scoped exception is unresolved. Pass applicable rules to `codebase-design`; it does not override project decisions or waive setup. No setup marker is required for adequate legacy rules.

For code plans, select the installed rule-maker's ENGINEERING.md guidance and applicable version context. Challenge invalid state combinations, unowned lifetimes, late results, unsafe retry/permission boundaries, unmeasured optimisation claims and unsupported compatibility assumptions where relevant. Require meaningful tests, not an implementation-mirroring assertion. No mandatory redesign or extra report.

For application UI, use local ui-design and shared design.md: verify the area's mode, actual approved components/patterns, preview access and bounded exceptions. Challenge invented layout or visual overrides, even without CSS files. A missing kit may use an explicitly agreed functionality-only scope, not a silent fallback. Behaviour approval, design acceptance and release readiness stay distinct. No unrelated backend UI setup or application designs hidden inside report artifacts.
