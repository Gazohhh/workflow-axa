---
name: workflow-doctor
description: "Diagnose the local workflow-axa setup: registered skills, routing, local assets, Matt specialist inventory and obvious duplicate/version conflicts. Read-only; never install or modify configuration automatically."
---

# Workflow doctor

Diagnose workflow-axa setup problems without changing the environment.

Check what can be observed in the current host/repository: workflow-axa version and registered skills; project routing instructions; duplicate/local copies; local `codebase-map` guide/assets/renderer; task-record location; Python/browser prerequisites used by bundled validation; and the resolved availability/identity of required Matt specialists such as `grilling`, `research`, `diagnosing-bugs`, `tdd`, `codebase-design`, `domain-modeling`, `writing-for-agents` and `code-review`.

Separate **installed on disk**, **discoverable by the host**, **enabled/invocable**, and **successfully used**. Do not claim one proves another. Use bundled read-only validators/checkers when present; do not install, enable, delete or rewrite anything.

Return a short table: PASS / WARNING / BLOCKED / NOT VERIFIED, what it means in plain language, evidence, and the exact manual next step. Highlight version conflicts and duplicate skill copies first. A missing optional helper is not a failure.

## Global artifact activation

Resolve the installed workflow directory and run its `scripts/global_policy.py --check` read-only with the actual user/config paths. Check the single deployed policy against that package, Claude's effective user instructions and Codex's base plus any nonempty global override. Respect CLAUDE_CONFIG_DIR/CODEX_HOME. Missing or stale markers, a changed policy, a newer deployment, duplicate copies or linked configuration require review; never repair them automatically.

This verifies disk setup only. In a fresh host session check that the actual global instructions/policy were read for an ordinary testing request without `/workflow`; cloud/remote accounts need their own setup. Check project-specific protections and delegated-worker instructions separately. Return the result in chat, not a new artifact folder. If the checker is unavailable, inspect known paths and say which checks remain unverified.

For record-history adoption, check whether project instructions conflict with preservation of presented reviews or demand a bulk migration. Report the conflict and a minimal setup merge; do not rewrite task records. Old STATUS.md layouts, older schemas and review filenames are not installation defects. The artifact policy may retain version 2.5.0 independently of the package version; compare policy bytes, not equal version numbers.

## Rules readiness and global references

Resolve local rule-maker and run `scripts/activate_rules.py --check` in the actual profile. Check its library and applicable project coverage, not just filenames. Use `scripts/readiness.py inspect` for bounded inputs; it never proves readiness from file presence. The optional `scripts/version_facts.py` reports static stack evidence, not runtime/API compatibility. Report effective loading and hook enforcement separately. Missing rule-maker blocks affected work, not read-only diagnosis. Adequate legacy rules need no migration. No silent repairs or global updates.
