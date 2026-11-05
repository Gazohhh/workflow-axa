# One code-backed catalogue, not copied UI

A kit is a project-local preview of **the actual framework components and approved patterns**. React renders its React components; Angular/Ionic renders its components. The workflow report is a saved projection/capture, not another implementation of those controls. Existing project sources are required; this package contains no Altinstar/Cheflabels kit and installs no preview tools.

## Single sources

| Information | Authoritative location |
|---|---|
| Current appearance/behaviour | Real component, styles/theme and dependencies. |
| Examples, variants and states | Existing adjacent framework stories/tests/examples importing the component. |
| Current catalogue/reference inventory | Generated from that code/examples through existing approved tooling. |
| Purpose, approved scope and exceptions | One designated approval/usage record; human decisions are not inferred from code. |
| Project entry point | A short pointer in current project instructions or DESIGN.md, not a copied CSS/property list. |
| Historical task review | The presented report and captured sources, preserved unchanged. |

Rebuilding/reloading the existing catalogue reflects component changes. A new input/state may require changing the adjacent example or test. Do not promise that human approval or intended use regenerates itself. An automatically generated index may still be stale; inspect the actual checkout and required source/preview checks.

## Setup sequence through ui-design

1. `kit-audit <area>` finds designated real components, existing preview tooling and authority. Search is inventory, not approval. No installation, routes, builds or captures without permission.
2. `kit-setup <area>` proposes connecting existing sources, short project pointers and safe preview/verification. Setup is not application implementation approval. After approval, normal execution may add the minimum framework example and registration that render real components or mirror existing tags, classes and wrappers. A missing example alone is not a designer blocker. New visual designs, styling, dependencies or custom preview infrastructure remain outside that reuse scope; name the specific gap before dependent work. Do not install a tool merely to satisfy this skill.
3. `kit-check <catalogue>` checks selected sources/scope. A Markdown catalogue remains valid; do not force conversion. If a JSON profile is used, it is a generated projection or the sole existing catalogue, not another independently maintained truth source.
4. Check claimed variants against their renderer and real callers, including host wrappers/styles. A declared type or enum is not proof of a working example. Identify absent, inert and context-dependent variants in the plan before approval; preserve distinct existing variants. Record exact selections in the existing task, generate the existing review with captured screens and per-element references, obtain normal approval, then wire only selected supported component APIs.

## Optional read-only Storybook index adapter

For an already generated local v4/v5 `index.json`:

```bash
python -X utf8 skills/ui-design/scripts/inspect_kit_index.py --root /path/to/project --index path/to/index.json
python -X utf8 skills/ui-design/scripts/inspect_kit_index.py --root /path/to/project --index path/to/index.json --story buttons-primary--loading --catalogue path/to/kit.json --item primary-button --scope src/settings
```

It returns current story IDs/labels, local source existence/fingerprints and preview reference suffixes on stdout. With `--previous` it lists added/removed/changed index metadata; that older input must already exist. No output files, network, source execution or plugin installation. A story selection bound to the optional existing catalogue checks the entry and its dependencies/scope; the story source must be among its declared sources. Unknown formats, virtual import paths or missing files require review, not guessed resolution. The index is not a dependency parser: a deleted export inside an existing file or a broken component import requires actual project compilation/story checks. Tags never establish approval.

Use the project's existing dev/build verification process to generate/validate its catalogue. The workflow does **not** automatically wire this adapter into an unseen repository or claim an auto-refresh service is running. Avoid a new snapshot for every rerun; use existing tool output paths and the artifact policy.

## Manual designer edits: detect drift without rewriting DESIGN.md

The next UI workflow checks **Git changes**, not conversation memory and not every page:

```bash
python -X utf8 skills/ui-design/scripts/design_drift.py --root /path/to/project
```

After a real, owner-reviewed initial design reconciliation, the designated existing policy file may contain **one** baseline pointer:

```markdown
<!-- workflow-axa-design-baseline: <reviewed full Git commit SHA> -->
```

The tool compares that commit with the **current checkout**, including committed, staged, unstaged and untracked UI files. It reports changed paths and whether shared/global CSS changed (then examine dependent consumers). It never edits files, approves a style or infers intent. Don't update the marker on every CSS change: move it only as part of an explicit review that covered the changes. Worktrees/teammates use the Git SHA from the checked-out project, not a per-machine cache. If the baseline is absent, unavailable, or the repository isn't accessible, output **baseline-unknown** and do an initial targeted inspection. A filename-level change list is not a CSS dependency graph; investigate selector/component effects and actual runtime as needed.

Routine changes to existing token values or styles should appear directly in the project's **real components/kit** without transcribing those values into DESIGN.md. Keep only approval, intended use, Figma references and exceptions in that document. A new component/variant is discovered as a candidate and requires a human decision before becoming approved; the kit example may need one-time registration.

## Change and deletion handling

- Same component, changed internals: current preview updates through existing tooling; targeted review establishes whether appearance/contract changed. A hash change is not automatically design rejection or renewed approval.
- New variant/story: candidate until its coverage is approved; top-level catalogue status does not grant it consent.
- Removed usage: update that screen only; do not delete a shared component used elsewhere.
- Renamed/moved source: preserve a stable entry ID when intended; update actual imports/references through the approved change. No automatic replacement.
- Deleted component/story: surface missing references and consumers; affected reuse pauses. Do not hide broken stories to make checks pass.
- Changed theme/brand/dependency: check affected coverage, not just the leaf component file.
- Old review: preserve its embedded capture and source identity. Current generated references cannot rewrite what was presented.
- Inaccessible source/runtime, unknown ownership or permission: report the gap and stop the dependent action, not unrelated authorised logic.

## What the owner sees

In the unchanged HTML report's **Inspect screen** section, each element names its role, exact catalogue entry/variant/state, code/example references and intended content/event change. A pattern entry identifies composition. Real captures are labelled as captures; source checks do not prove the image actually used those components. Capture records and actual preview inspection supply that evidence. No “approved kit” badge is inferred from a file name, screenshot or agent assertion.

Background guidance: [stories](https://storybook.js.org/docs/get-started/whats-a-story), [Autodocs](https://storybook.js.org/docs/writing-docs/autodocs), [generated index](https://storybook.js.org/docs/configure/user-interface/sidebar-and-urls). These are optional tooling references, not runtime dependencies or authorisation to install anything.
