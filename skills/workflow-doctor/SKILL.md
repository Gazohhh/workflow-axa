---
name: workflow-doctor
description: "Diagnose the local workflow-axa setup: registered skills, routing, local assets, Matt specialist inventory and obvious duplicate/version conflicts. Read-only; never install or modify configuration automatically."
---

# Workflow doctor

Diagnose workflow-axa setup problems without changing the environment.

Check package/version, host registrations, routing, duplicates, local assets and selected Matt specialists. Use the established inventory; disk presence does not prove invocation.

Separate **installed on disk**, **discoverable by the host**, **enabled/invocable**, and **successfully used**. Do not claim one proves another. Use bundled read-only validators/checkers when present; do not install, enable, delete or rewrite anything.

Return PASS / WARNING / BLOCKED / NOT VERIFIED with evidence and next step. Optional missing helpers are not failures.

## Global artifact activation

Resolve the installed workflow directory and run its `scripts/global_policy.py --check` read-only with the actual user/config paths. Check the deployed policy, effective Claude instructions and Codex base/nonempty override. Respect CLAUDE_CONFIG_DIR/CODEX_HOME. Missing or stale markers, a changed policy, a newer deployment, duplicate copies or linked configuration require review; never repair them automatically.

Disk checks are not loading proof. Verify an ordinary testing request without `/workflow` in the actual fresh host; remote environments need setup. Check project-specific protections and delegated-worker instructions separately. Return the result in chat, not a new artifact folder. If the checker is unavailable, inspect known paths and say which checks remain unverified.

For record-history adoption, check whether project instructions conflict with preservation of presented reviews or demand a bulk migration. Report the conflict and a minimal setup merge; do not rewrite task records. Old STATUS.md layouts, older schemas and review filenames are not installation defects. The artifact policy may retain version 2.5.0 independently of the package version; compare policy bytes, not equal version numbers.

## Rules readiness and global references

Resolve local rule-maker; use its INSTALLATION.md and `scripts/audit_installation.py --check-global` with explicit candidate copies/profile paths. Compare bytes, not version labels. The existing `scripts/activate_rules.py --check` remains available. Check library and project coverage, not filenames. Use `scripts/readiness.py inspect` for bounded inputs; it never proves readiness from file presence. The optional `scripts/version_facts.py` reports static stack evidence, not runtime/API compatibility. Report effective loading and hook enforcement separately. Missing rule-maker blocks affected work, not read-only diagnosis. Adequate legacy rules need no migration. No silent repairs or global updates.

## Local UI route

Check local ui-design, its contract/verification references and read-only diff helper, plus the shared design.md and workflow routing. Distinguish file presence from actual host invocation. Functionality-only needs no external design skill or complete project kit. Report mode/source/preview gaps only for affected UI; do not demand kit setup for backend work. Use ui-design/KIT.md for catalogue lifecycle checks. A sample, draft or deprecated kit is not approval. No enforcement or UI framework is installed.
