# Upgrade to workflow-axa 2.7.0-rc.6

## From the supplied rc.5

Replace the complete plugin or all **eight complete skill folders together** from this release. Do not merge individual files into an unknown mixed installation. Preserve the old reviewed copy outside active skill discovery and do not delete unrelated Matt skills. This package keeps the rc.5 Windows/home/integrity fixes.

The source ZIP supplied for this update contained `.git` and scratch release output. Those are not installation payloads and are excluded here. Existing documentation/task history is retained. Some owner-local historical records contain machine paths; review before public redistribution.

### Shared rules and host setup

Rules library 1.5.0 adds task-level UI-source selection. Existing valid global references continue working at the same stable install path; no new hook or automatic updater is installed. Ordinary UI prompts still depend on those host references being loaded.

From the trusted package directory, compare the actual runtime copy first:

```bash
python -X utf8 skills/rule-maker/scripts/audit_installation.py --candidate /actual/path/to/skills
```

Then run from the **installed** package/skills location to check its own host references:

```bash
python -X utf8 skills/rule-maker/scripts/audit_installation.py --check-global
python -X utf8 skills/rule-maker/scripts/activate_rules.py --check
```

Use explicit `--claude-dir` and `--codex-home` where T3 uses other profiles. The source-copy check proves neither host loading nor source freshness at a different path. The audit now flags unexpected files inside the eight owned folders as DRIFT; inspect them, do not automatically delete them. Other separately installed skills are outside this comparison.

If global references are missing, preview `activate_rules.py`, then apply only after reviewing its changes. Never infer success from the prior task record: the uploaded rc.5 history explicitly left runtime swap/global activation pending. Start fresh sessions and test an ordinary neutral request as well as /workflow.

### Reports and design

Do not replace your original review-r2.html. It is retained verbatim under its original historical task path. New samples are under `skills/codebase-map/examples/ui-review/`:

- `review-r2.html`: your source R2 layout/content, plus an optional, clearly separate fictional UI screen-flow example. It is not a new live audit.
- `ui-task-review-r2.html`: the same complete report template for a synthetic UI feature, opening on the screen flow. All usual plan, comparison, task, approval and evidence sections remain.

Use the UI screens tab or Inspect screen links. Existing schema-2 input remains valid without the optional `ui_review` field. No report regeneration or documentation migration is required just to upgrade. Already presented HTML/JSON is never overwritten.

Approved-kit appearance must come from actual authorised component captures; no real project kit is included in this package. Without one, ask which source or bounded plain/schematic preview to use. Do not ship design-pending UI. The report theme remains approved and separate from application styling.

Read `AUDIT-rc5.md` and `VALIDATION.md` for what was inspected, retained, fixed and not tested. No application repository, global profile, private memory or live deployment was modified by this release build.

---

## Earlier upgrade instructions — historical context

# Upgrade to workflow-axa 2.7.0-rc.5

## From rc.4 to rc.5

rc.5 keeps rc.4's skills and routing. It changes the following:
- install integrity on Windows;
- Windows fixes to the rules helpers;
- the shared TypeScript rule (rules library 1.4.0).

Replace all eight folders byte for byte, as described in section 1. An rc.4 copy that differs only by CRLF line endings is reported as `line_ending_only`; reinstall it rather than editing it. Existing global blocks stay valid when the installation path is unchanged. Project files need no change for this release.

## Scope

This is the full eight-skill package, based on rc.3 through rc.4. It is not a patch or a replacement for your application UI. All shared standards remain centrally inside the installed library. Project-specific rules and actual component implementations remain in their projects.

Replace the complete plugin or all eight complete folders: workflow, codebase-map, task-status, resume-task, workflow-doctor, plan-review, rule-maker and ui-design. Do not mix rc.2 rules with rc.3+ routing, or rc.4 and rc.5 folders in one installation. Keep a previous release outside active discovery for rollback; do not automatically delete other installations.

## 1. Identify and check the actual installation

From its final installed location (Python 3.10+):

```bash
python -X utf8 skills/rule-maker/scripts/audit_installation.py --check-global
```

Copy the folders byte for byte, and check the copy in two steps (bytes from the package, then the installed copy's global check); see rule-maker [INSTALLATION.md](skills/rule-maker/INSTALLATION.md), "Install byte for byte". Supply an explicit `--candidate /path/to/other/installation` for additional known copies; do not scan all private files. Package root, skills root or rule-maker directory are supported. A warning about multiple identical copies still requires determining which host uses which. No helper result proves runtime loading.

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
