# Workflow AXA — 2.7.0-rc.6


## This update: keep the full report, add the screens

The uploaded rc.5 is the base. Its Windows integrity/home fixes and shared TypeScript rule are retained. [Audit findings](AUDIT-rc5.md) distinguish package evidence from the interrupted owner's still-pending runtime installation.

The existing editorial report is not redesigned. An optional **UI screens** view shows connected state previews, meaningful design choices and sources within the same report. Actual approved-kit captures and explicit schematic proposals are distinct. Core report CSS/JS remain unchanged.

Full samples: [R2 with the additive UI example](skills/codebase-map/examples/ui-review/review-r2.html) · [complete synthetic UI-feature report](skills/codebase-map/examples/ui-review/ui-task-review-r2.html). The original R2 remains unchanged in its task history. Open the HTML directly; no server or external assets are needed.

[Upgrade](UPGRADE.md) · [Screen-flow contract](skills/codebase-map/UI-FLOW.md) · [Validation](VALIDATION.md). No new external skill or component library.


Complete replacement package: **eight local skills**, the existing Matt specialist integrations, shared version-aware engineering rules, and local design-kit support. This candidate fixes gaps exposed by the two project rules audits without making their project-specific instructions identical.

## What is new

- **Full rules audit:** distinguish whole requested-scope review from readiness for one task. Check authority/memory conflicts, actual loading, framework coverage, technical claims, verification safety and rule placement; disclose coverage and unknowns rather than issue a blanket pass.
- **Actual-installation check:** compare explicitly named skill copies with this trusted release, detect missing/changed/mixed files, and optionally check global activation. It writes nothing and cannot prove host selection or compliance.
- **Framework coverage:** Angular, Ionic and Capacitor modules plus static version/configuration facts. React Compiler guidance distinguishes configuration from React major; Ionic page visibility differs from destruction. No upgrade is authorised.
- **Operation boundaries:** inspect test prerequisites, build permissions and effective backend isolation; keep quiet-host requirements and report actual gate proof. Old memory cannot silently replace current approved project policy.
- **Design kit:** local catalogue workflow, adaptable templates and an optional read-only source/approval-freshness checker. No new external design dependency, invented project theme or unauthorised UI-tool installation.

## Design kit included — what it is and is not

Use `ui-design kit-audit` to inventory **designated** components; `kit-setup` to propose and apply an approved catalogue setup; `kit-check` to review its authority and current sources. See [KIT.md](skills/ui-design/KIT.md). The included templates are **drafts**, not approved components. Real Cheflabels/Altinstar source components, colours and designer acceptance were not supplied and are not fabricated here.

Keep one project-approved catalogue backed by real components/APIs, supported variants, states, style/token dependencies and page patterns. Reuse an existing UI-kit page/Storybook/project reference; JSON is optional. A candidate entry does not inherit approval from an existing kit. Component approval does not approve any page layout. New kit revisions require targeted reconciliation, not automatic redesign of old work.

| UI mode | Permission |
|---|---|
| **Functionality-only — default** | Preserve appearance; explicitly approved component reuse; agreed semantic markup in an authorised preview. No invented styling. |
| **Approved-kit** | Use the designated components, variants and patterns within their approved coverage. Missing/stale coverage needs a decision. |
| **Design-authoring** | Only specifically approved presentation work; no permanent styling unlock. |

CSS, inline styling, CSS-in-JS, arbitrary classes, visual props, themes and rendered/native/game visuals share this boundary. Required labels, keyboard/focus and functional feedback remain. **Behaviour, design acceptance and release readiness stay separate.** Backend work does not need a kit. The approved local flowchart renderer is preserved and is not an application design system.

## Entry points

```text
/workflow-axa:workflow <goal>
/workflow-axa:rule-maker audit|setup|update
/workflow-axa:ui-design <UI task>
/workflow-axa:ui-design kit-audit|kit-setup|kit-check <area or catalogue>
/workflow-axa:workflow-doctor
/workflow-axa:task-status <task>
/workflow-axa:resume-task <task>
/workflow-axa:plan-review <task>
/workflow-axa:codebase-map explain|current|proposed|compare <scope>
```

These are plugin names. Standalone host registrations differ. The main sequence remains **rules readiness -> find/reuse task -> current-code evidence -> grilling -> PLAN/TODO and flowchart -> approval -> implementation -> verification**. UI/kit work uses the same task and authority, not another implementation workflow. A rules setup or catalogue check does not approve application edits.

## Install and verify the actual copy

Replace the complete plugin or all **eight complete skill folders**. Keep a stable installation path and one intended active route per host. See [UPGRADE.md](UPGRADE.md).

```bash
python -X utf8 skills/rule-maker/scripts/audit_installation.py --check-global
python -X utf8 skills/rule-maker/scripts/activate_rules.py --check
python -X utf8 tools/validate.py
python -X utf8 -m unittest discover -s tests -p 'test_*.py'
```

The first command checks only named/default disk inputs and references. Use repeatable `--candidate` arguments for other discovered copies. It does not delete duplicates, download updates, install hooks or prove which rules a running host loaded. An older global setup pointing only to ARTIFACTS.md is not enough for shared coding rules; use the existing activation helper's preview/apply procedure after review. Fresh Claude/Codex sessions and trace inspection remain necessary.

## Preserved and limited

Matt's 27 specialist entries/adapters, proactive grilling, task/revision history, local flowchart styling and artifact policy remain. No project application/rule files, memories, old evidence or approved designs are rewritten by installing this package. Project-specific contradictions need a scoped decision; templates do not migrate existing records.

[VALIDATION.md](VALIDATION.md) records observed tests separately from authored [live acceptance cases](tests/behavioral/RULES-AUDIT-KIT.md). This is a release candidate: live Claude/Codex compliance and native Windows installation remain unverified. Instructions and read-only helpers are not host-enforced security boundaries.
