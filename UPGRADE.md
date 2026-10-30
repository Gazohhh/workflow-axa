# Upgrade to workflow-axa 2.7.0-rc.4

## Scope

This is the full eight-skill package based on rc.3, not a patch or a replacement for your application UI. All shared standards remain centrally inside the installed library. Project-specific rules and actual component implementations remain in their projects.

Replace the complete plugin or all eight complete folders: workflow, codebase-map, task-status, resume-task, workflow-doctor, plan-review, rule-maker and ui-design. Do not mix rc.2 rules with rc.3/rc.4 routing. Keep a previous release outside active discovery for rollback; do not automatically delete other installations.

## 1. Identify and check the actual installation

From its final installed location (Python 3.10+):

```bash
python -X utf8 skills/rule-maker/scripts/audit_installation.py --check-global
```

Supply an explicit `--candidate /path/to/other/installation` for additional known copies; do not scan all private files. Package root, skills root or rule-maker directory are supported. A warning about multiple identical copies still requires determining which host uses which. No helper result proves runtime loading.

## 2. Repair missing global activation only after preview

The global-reference helper and managed block are unchanged from rc.3. A correct existing installation at the same path needs no new global merge. The artifact-policy helper is also unchanged and remains separately active.

```bash
# Read-only check
python -X utf8 skills/rule-maker/scripts/activate_rules.py --check
# Preview a missing/stale reference; writes nothing
python -X utf8 skills/rule-maker/scripts/activate_rules.py
# Apply only after reviewing the preview
python -X utf8 skills/rule-maker/scripts/activate_rules.py --apply
```

The existing helper preserves unrelated global content and handles a nonempty Codex override. Configure actual profile paths using its options when needed. Do not copy project AGENTS.md into a global profile. It neither installs host hooks nor auto-downloads updates.

## 3. Start fresh sessions and test loading

On each actual Claude/Codex environment, try an ordinary task in a disposable project without naming a skill. Verify the resolved file paths and reads, relevant module selection, missing-rule stop and UI no-styling boundary. Repeat root/nested and delegated cases as applicable. Disk presence, loaded context, followed rules and enforced actions are different results. No universal host precedence is assumed.

## 4. Audit each real project's differences

`/workflow-axa:rule-maker audit` now follows the full audit procedure rather than declaring all rules correct from a task-readiness check. Preserve current architecture, Git/build authority, line endings, test layout, production-target warnings and generated-file contracts. Reconcile relevant memory conflicts explicitly. Project fixes are proposed, not automatically applied by this release.

Shared additions: Angular/Ionic/Capacitor, operation safety, policy/memory conflict handling and correct compiler/lifecycle guidance. A stale readiness assessment needs refresh; valid prior scope/approval and history are not automatically reset. Retain legacy task names/STATUS layouts and presented reviews. No application cleanup or dependency migration is authorised.

## 5. Adopt the design kit without inventing one

`/workflow-axa:ui-design kit-audit <area>` is read-only. `kit-setup` proposes the designated catalogue, real components and preview/acceptance process; it does not select a new visual theme. Templates/checker are local under ui-design. A valid existing Markdown or UI-kit page needs no conversion to JSON. Do not copy both templates as duplicate authoritative records.

An approved kit needs real source contracts, allowed variants/patterns, actual owner acceptance and scoped coverage. Until those exist, functionality-only remains the default and new design-pending controls stay in an agreed preview. Installation does not approve the empty template or expose previews publicly. Existing styles and the flowchart renderer are preserved.

## Limits and rollback

This release does not modify your projects, auto-reconcile memories, create a kit page, ship application components, install browser tools or enforce tool calls. Live acceptance is still required. To roll back, restore one complete trusted installation and verify global references again; preserve active task records, approval history and project output. Do not use rollback to silently discard an approved policy change.
