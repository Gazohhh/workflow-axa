# Project design kit — source-backed, reviewed, never invented

The package supplies the kit workflow, templates and a read-only checker. It does **not** ship an approved application theme, new React/Ionic components or a visual design for a real project. The existing local flowchart design remains separate. No Storybook/Figma/vendor service is required or installed.

## Entry points through this skill

- `ui-design kit-audit <area>`: read-only inventory of the owner's designated components, pages, style sources and existing catalogue. State missing access and unapproved candidates. Return findings in chat or existing task records. No screenshots/builds/network unless authorised.
- `ui-design kit-setup <area>`: prepare a minimal proposal for the existing project's catalogue/preview surface, component scope, owner and acceptance. Apply only after exact approval. It is not permission to design new components or install a UI tool.
- `ui-design kit-check <catalogue>`: inspect authority, actual sources, supported options/patterns and freshness. The optional JSON checker below assists; it never authenticates a human approval.
- Ordinary UI work selects behaviour-only / approved-kit or blocks through CONTRACT.md. No agent-authored HTML/templates, CSS or inline styles; no plain-markup or design-authoring fallback. A kit review or setup command does not approve the original feature.

These are arguments to the one ui-design skill, not separate installed skills. Plugin example: `/workflow-axa:ui-design kit-audit settings`. A caller may route here automatically for a genuine kit setup/review request, but normal backend work never needs a kit.

## One authoritative catalogue per relevant area

Reuse an existing project UI-kit page, Storybook stories, design reference or component library when designated by its owner. It must identify actual source/API, allowed variants, intended use and approval. Inspect implementation only to verify that designated contract; searching random legacy HTML does not choose the design standard. A library can cover one brand/platform without covering another.

Use the existing approved project path. Do not mandate `docs/design/`, duplicate AGENTS rules, create empty catalogues in every project or copy our global standards into the repo. A normal Markdown/reference catalogue is valid. If machine checks are useful, choose the optional JSON profile as the catalogue or a generated projection of the authoritative record; do not maintain two independent truth sources. Ordinary feature tasks record only kit/reference and scope in their existing checkpoint.

For each component/pattern/token set, capture:

| Field | Purpose |
|---|---|
| Identity, area and owner | Which brand/platform/path it covers and who can approve changes. |
| Actual source and contract | Import/export or approved markup pattern, style/token dependencies, accessible behaviour and usage example. |
| Supported variants and states | Default/loading/error/disabled/focus/empty only where meaningful; no invented states or arbitrary props. |
| Composition | Approved page/layout patterns, permitted combinations and exceptions. A button approval does not approve a dashboard layout. |
| Status and decision | Candidate, approved or deprecated; named decision/reference and revision, not a job title or a directory name. |
| Verification and limits | Relevant interaction, keyboard, responsive and device evidence; what remains untested. |

## Lifecycle and approval

1. Discover designated sources; retain useful existing components without auto-approving them. Mark gaps and candidates.
2. Agree the intended behaviour and exact approved-kit selection through normal grilling/plan/visual approval. The behaviour flowchart alone is not a visual-design sign-off.
3. Only wire existing approved component/catalogue sources within the approved scope. New component HTML/CSS belongs to the designated designer/maintainer, not this agent. Use the project's existing preview tooling; no default theme, reset, component framework, new route or token system without explicit authority.
4. Inspect the actual preview with representative safe data and relevant states, keyboard/focus, screen sizes and required native behaviour. Record observations and limitations, not invented acceptance.
5. The authorised owner/designer accepts the named revision and enumerated components/variants/patterns. Only that coverage can be used in approved-kit mode. Freeze the source/contract references needed to identify it; signatures/hashes are freshness aids, not proof of consent.
6. When a source, theme dependency or contract changes, reconcile the affected entries and consumer scope. Do not simply refresh hashes to make the check pass, restyle older work or revoke unaffected approvals. Deprecation needs an explicit replacement/migration decision; no mass update of consumers.

New candidate entries must not inherit approval merely because the catalogue was previously approved. Independent areas may remain behaviour-only or UI-blocked. Inaccessible/stale required references pause affected styling, not unrelated authorised logic. Keep historical approvals and final reference screenshots under the existing record/artifact policy; no new snapshot for every rerun.

## Included templates and checker

`templates/KIT.md` is an adaptable section for an existing project reference. Do not copy it as an extra document by default. `templates/design-kit.json` is an empty **draft**, with no component or visual decisions. Choose an existing representation first; JSON is optional, never a readiness prerequisite.

For an explicitly chosen JSON catalogue, see [CATALOGUE.md](CATALOGUE.md). From the installed package:

```bash
python -X utf8 skills/ui-design/scripts/check_design_kit.py --root /path/to/project --catalog path/to/design-kit.json
python -X utf8 skills/ui-design/scripts/check_design_kit.py --root /path/to/project --catalog path/to/design-kit.json --item save-button --scope src/settings
```

Output is stdout only. The helper checks selected entries/dependencies, exact scoped coverage, referenced local-file existence and fingerprints. It does not run components, render a UI, query a remote design tool, prove completeness of the dependency list, authenticate approval or permit implementation. An approved Markdown kit remains valid after equivalent human/agent inspection; absence of this JSON is not an installation error.

Design concepts: [stories tied to component states](https://storybook.js.org/docs/get-started/whats-a-story/), [review before publishing components](https://design-system.service.gov.uk/community/contribution-criteria/). These are references, not mandatory tools or their visual themes.

## Live project kit integration

Use [LIVE-KIT.md](LIVE-KIT.md): current catalogue and technical metadata derive from actual component code and adjacent examples, not a hand-maintained duplicate in DESIGN.md. A short project pointer and one approval source remain. Current previews refresh; historical reports do not. The optional local index inspector checks generated Storybook entries without running/installing it. Kit setup itself never authorises new application markup/styles.
