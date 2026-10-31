---
name: workflow-doctor
description: "Diagnose workflow-axa installation, global routing, rule coverage, duplicate copies and local kit/report assets. Read-only; no automatic repair or installation."
---

# Workflow doctor

Inspect without changing the environment. Check package/version, host profile/registrations, global/project routing, duplicate copies, local assets and selected Matt specialists. Return PASS / WARNING / BLOCKED / NOT VERIFIED with evidence and the next step in chat, not a new artifact folder.

Separate **installed on disk**, **discoverable/enabled**, **actually loaded**, **followed** and **enforced**. Validators cannot prove the later claims. Do not install, enable, delete, overwrite or repair anything automatically.

## Global artifact policy

Use workflow/scripts/global_policy.py --check with the actual profile paths. Respect CLAUDE_CONFIG_DIR/CODEX_HOME and active Codex overrides. Missing/changed markers, stale policy, newer deployments, duplicates or linked configuration need review; never repair them automatically. Test an ordinary request without /workflow in the real host to establish loading; remote environments need their own setup. Pass project protections to workers. Policy version 2.5.0 can legitimately differ from the package version; compare bytes, not version equality.

## Shared rules

Use rule-maker/INSTALLATION.md and scripts/audit_installation.py --check-global with explicit known candidate paths. activate_rules.py --check remains available. Byte comparisons detect mixed copies; names do not. readiness.py inspects bounded inputs but cannot infer adequate rules from file presence. version_facts.py reports static versions, not runtime compatibility. Adequate existing project rules need no migration. Report host-loading and enforcement gaps separately; missing capabilities block dependent work, not diagnosis.

## UI and report route

Check local ui-design, shared design.md, CONTRACT.md, VERIFY.md, LIVE-KIT.md and the diff/index helpers. Strict kit reuse forbids agent-authored application markup/CSS/inline styles and plain-HTML fallbacks. Behaviour-only repairs preserving presentation need no complete kit; new UI needs selected approved components/patterns. A sample, filename or tag is not approval.

Check codebase-map/kit_bindings.py and its ui-design sibling. Distinguish current story-source observations, declared approval, real capture provenance and actual renderer use. Missing/deleted/stale sources block their selection, not unrelated work. Do not build a kit, refresh approval hashes or create substitute templates. No UI framework or tool-level enforcement is installed.

## Existing records

Report conflicts with preservation of presented reviews or unnecessary bulk migration. Legacy STATUS.md layouts and old review filenames are not setup defects. New approval-ready UI inputs need current kit references; historical reports stay unchanged. Test ordinary prompts, scope changes, resume and delegation on the installed hosts before claiming reliable operation.
