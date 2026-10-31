# Workflow AXA — 2.7.0-rc.7

Full replacement package: **eight skills**, shared version-aware rules, Matt's existing specialists, rules-readiness, proactive grilling, approved flowchart reports, recoverable records and the artifact policy.

## This update: reuse the real kit, never invent application markup/styles

Ordinary agent work may **not create, modify or inject application HTML/templates/JSX structure, CSS, inline styles or other invented presentation**. No plain-HTML fallback. No automatic styling exception from old design-authoring records. Approved component calls/data/event wiring are allowed through selected supported APIs and approved patterns; do not copy the component's DOM or modify its internals.

| Situation | Behaviour |
|---|---|
| Existing interface logic fix | Keep its markup/appearance intact; change only authorised behaviour. |
| New UI with selected approved components and pattern | Reuse exactly those entries/variants/states; show actual captures and component references in the normal report before implementation approval. |
| Missing, stale, inaccessible, deleted or unapproved component/layout | Stop affected integration and ask for the approved source or designer input. Continue only independent authorised work. |
| No DESIGN.md | Look for an equivalent designated source; the filename is not mandatory and absence does not authorise improvisation. |
| Ordinary prompt without /workflow | Same boundary when the global core is loaded. Verify actual host loading; installation alone is not proof. |

**The existing report remains styled.** Its approved local renderer is a narrow reporting exception, not permission to build application prototypes. Base report CSS/JS and UI asset files are unchanged. Inspect screen now lists each selected kit entry, variant/state, actual source/example, role and intended nonvisual changes. Real captures are distinct from source approval; hashes cannot authenticate consent or prove which code produced an image.

## The project kit is real code, not another HTML mockup

[Live-kit guide](skills/ui-design/LIVE-KIT.md): use the project's existing framework components and adjacent examples. Generate its current catalogue and technical references through existing tooling. Keep project instructions short: catalogue location, owner and project constraints. Do not manually maintain several copies of a component/style inventory.

An optional **read-only local Storybook index inspector** reports selected example identities, missing sources and metadata changes. It does not install/run Storybook or discover every transitive import. [Kit workflow](skills/ui-design/KIT.md) supports audit/setup/check of existing sources. Actual Altinstar/Cheflabels kits are not supplied or invented by this package; connecting each real project's tooling is separately scoped work.

Human acceptance stays recorded once. Component edits can refresh current previews after rebuild; they do not renew approval or rewrite historical review captures. Deleted sources cause affected selection checks to fail, not a guessed replacement.

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

Plugin syntax is shown; standalone names depend on the host. The main sequence is unchanged: **rules readiness → find/reuse task → inspect current code → grilling → plan/full report → owner approval → implementation → verification**. Kit setup or rule setup does not approve application changes. Backend work does not require a kit.

## Install and check

Replace the complete plugin or all **eight complete skill folders** together, preserving separately installed Matt skills and actual user modifications after review. Use one stable active installation, start fresh sessions, then check from the installed package:

```bash
python -X utf8 skills/rule-maker/scripts/audit_installation.py --check-global
python -X utf8 skills/rule-maker/scripts/activate_rules.py --check
```

These read-only checks do not repair settings or prove loading. Existing correct references remain valid when the install path stays fixed. For missing references, use the activation helper's preview/apply procedure after reviewing it. No host hook, auto-updater or tool sandbox is installed.

[Upgrade guide](UPGRADE.md) · [Validation](VALIDATION.md) · [Strict reuse scenarios](tests/behavioral/STRICT-KIT.md) · [UI report contract](skills/codebase-map/UI-FLOW.md).

## Compatibility and limits

Non-UI report behaviour is unchanged. Historical HTML and task files remain intact. Old UI draft/illustration inputs remain readable, but old permissive modes cannot generate a newly approval-ready application report; add real kit selections/capture provenance instead. JSON is optional as the authoritative kit format: existing Markdown catalogues can be projected inside the report input without another maintained file.

Original rc.6 HTML samples remain as **historical schematic demonstrations, not the current permission policy or project-kit evidence**. See their example README. No replacement styled application sample is manufactured in this release.

All package/test results concern observed tooling. Live Claude/Codex/T3 compliance and real project-kit execution are not established here. A model can still disobey instructions; no absolute guarantee is claimed. No application source, real kit, user profile, memory or project instructions were changed by creating this archive.
