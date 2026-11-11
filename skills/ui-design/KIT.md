# Project design kit — source-backed, reviewed, never invented

The package supplies the kit workflow, templates and a read-only checker. It does **not** ship an approved application theme, new React/Ionic components or a visual design for a real project. The existing local flowchart design remains separate. No Storybook/Figma/vendor service is required or installed.

## Entry points through this skill

- `ui-design kit-audit <area>`: read-only inventory of the owner's designated components, pages, style sources and existing catalog. State missing access and unapproved candidates. Return findings in chat or existing task records. No screenshots/builds/network unless authorized.
- `ui-design kit-setup <area>`: prepare a minimal proposal for the kit route (by default one development-only page inside the real application; [LIVE-KIT.md](LIVE-KIT.md)), the project's DESIGN.md or equivalent, component scope, owner and acceptance. Apply only after exact approval. It is not permission to design new components or install a UI tool.
- `ui-design kit-check <catalogue>`: inspect authority, actual sources, supported options/patterns and freshness. The optional JSON checker below assists.
- Ordinary UI work selects its mode or blocks through CONTRACT.md and rule-maker DESIGN.md. A kit review or setup command does not approve the original feature.

These are arguments to the one ui-design skill, not separate installed skills. Plugin example: `/workflow-axa:ui-design kit-audit settings`. A caller may route here automatically for a genuine kit setup/review request, but normal backend work never needs a kit.

## One authoritative catalog per relevant area

Reuse an existing project UI-kit page, Storybook stories, design reference or component library when designated by its owner. It must identify actual source/API, allowed variants, intended use and approval. Inspect implementation only to verify that designated contract; searching random legacy HTML does not choose the design standard. A library can cover one brand/platform without covering another.

Use the existing approved project path. Do not mandate `docs/design/`, duplicate AGENTS rules, create empty catalogs in every project or copy our global standards into the repo. A normal Markdown/reference catalog is valid. If machine checks are useful, choose the optional JSON profile as the catalog or a generated projection of the authoritative record; do not maintain two independent truth sources. Ordinary feature tasks record only kit/reference and scope in their existing checkpoint.

For each component/pattern/token set, capture:

| Field | Purpose |
|---|---|
| Identity, area and owner | Which brand/platform/path it covers and who can approve changes. |
| Actual source and contract | Import/export or approved markup pattern, style/token dependencies, accessible behavior and usage example. |
| Supported variants and states | Default/loading/error/disabled/focus/empty only where meaningful; no invented states or arbitrary props. |
| Composition | Approved page/layout patterns, permitted combinations and exceptions. A button approval does not approve a dashboard layout. |
| Status and decision | Candidate, approved or deprecated; named decision/reference and revision, not a job title or a directory name. |
| Verification and limits | Relevant interaction, keyboard, responsive and device evidence; what remains untested. |

## Lifecycle and approval

1. Discover designated sources; retain useful existing components without auto-approving them. Mark gaps and candidates.
2. Agree the intended behavior and exact approved-kit selection through normal grilling/plan/visual approval. The behavior flowchart alone is not a visual-design sign-off.
3. Only wire existing approved component/catalog sources within the approved scope. New component HTML/CSS belongs to the designated designer/maintainer, not this agent. The kit is one development-only page inside the real application (for example `/design-kit`), built as [LIVE-KIT.md](LIVE-KIT.md) describes; reuse an existing designated kit or catalog instead when the owner names one. No default theme, reset, component framework or token system without explicit authority.
4. Inspect the actual preview with representative safe data and relevant states, keyboard/focus, screen sizes and required native behavior. Record observations and limitations, not invented acceptance.
5. The authorized owner/designer accepts the named revision and enumerated components/variants/patterns. Only that coverage can be used in approved-kit mode. Freeze the source/contract references needed to identify it.
6. When a source, theme dependency or contract changes, reconcile the affected entries and consumer scope. Do not simply refresh hashes to make the check pass, restyle older work or revoke unaffected approvals. Deprecation needs an explicit replacement/migration decision; no mass update of consumers.

New candidate entries must not inherit approval merely because the catalog was previously approved. Independent areas may remain behaviour-only or UI-blocked. Inaccessible/stale required references pause affected styling, not unrelated authorized logic. Keep historical approvals and final reference screenshots under the existing record/artifact policy; no new snapshot for every rerun.

## Included templates and checker

`templates/DESIGN.md` is the default shape for a project's design-decision record when it has none: intent, source of truth, access, approval authority, reuse rules, usage decisions and history. Adapt an existing equivalent record instead of adding a second one. `templates/KIT.md` is an adaptable section for an existing project reference. Do not copy it as an extra document by default. `templates/design-kit.json` is an empty **draft**, with no component or visual decisions. Choose an existing representation first; JSON is optional, never a readiness prerequisite.

For an explicitly chosen JSON catalog, see [CATALOGUE.md](CATALOGUE.md). From the installed package:

```bash
python -X utf8 skills/ui-design/scripts/check_design_kit.py --root /path/to/project --catalog path/to/design-kit.json
python -X utf8 skills/ui-design/scripts/check_design_kit.py --root /path/to/project --catalog path/to/design-kit.json --item save-button --scope src/settings
```

Output is stdout only. The helper checks selected entries/dependencies, exact scoped coverage, referenced local-file existence and fingerprints. An approved Markdown kit remains valid after equivalent human/agent inspection; absence of this JSON is not an installation error.

Design concepts: [stories tied to component states](https://storybook.js.org/docs/get-started/whats-a-story/), [review before publishing components](https://design-system.service.gov.uk/community/contribution-criteria/). These are references, not mandatory tools or their visual themes.

## Live project kit integration

Use [LIVE-KIT.md](LIVE-KIT.md): the development route, page anatomy and coverage rule; current catalog and technical metadata derive from actual component code and adjacent examples, not a hand-maintained duplicate in DESIGN.md. A short project pointer and one approval source remain. Current previews refresh; historical reports do not. The optional local index inspector checks generated Storybook entries without running/installing it. Kit setup itself never authorizes new application markup/styles.
