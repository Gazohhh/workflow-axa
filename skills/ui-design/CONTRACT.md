# Modes and authority

The installed shared `rule-maker/rules/design.md` owns the general rule. This reference explains how ui-design applies it without copying a rulebook into a repository. Resolve project constraints before dependent changes; existing stricter rules are not waived by a default.

## Mode matrix

| Mode | Allowed | Not authorised by the mode alone |
|---|---|---|
| functionality-only | Scoped behaviour changes preserving existing appearance; explicitly approved component reuse; agreed minimal semantic markup in a named preview. | New/modified CSS, arbitrary class combinations, visual props, theme tokens, imagery, motion, spacing or page-layout invention; shipping unfinished interfaces. |
| approved-kit | Actual approved components and their supported variants, states and composition patterns, for the documented purpose and area. | Copying rendered markup to bypass component APIs; unsupported overrides; improvising a page layout from individually approved components; new kit variants. |
| design-authoring | Only the specific presentation changes, references and implementation boundaries approved for this design task. | Unrelated screen redesigns; new dependencies; permanent policy changes; self-approval of new baselines or release. |

Mode is scoped to an area, not assumed uniform across brands/platforms/packages. Record separate scopes in the same task when necessary. An explicit safe project rule can specialise the defaults; a vague conflicting rule is a question, not “latest wins”. A restricted area may forbid even the plain-HTML fallback.

## Approved sources

Prefer a designated catalogue backed by actual components and usage contracts. [KIT.md](KIT.md) provides the local catalogue lifecycle and optional source-freshness checker; no external design skill or UI-tool installation is required. A project may designate a particular component, pattern or existing screen without having a complete kit. Evidence should identify the exact source, supported variants, intended use and approving authority; source revision/content matters for long-running tasks. Inspect its real API and behaviour before reuse.

Repository search is allowed to understand current behaviour or verify the designated source. It is not permission to declare an arbitrary legacy class/tag the design standard. A screenshot or mockup can be an approved visual target, but does not automatically grant permission to create the CSS needed to implement it. Identical tag/class copying never overrides correct semantics or a component's contract.

When a kit becomes available later, ask for/verify its explicit approval and coverage at a task boundary. Do not switch modes merely because files appeared. No automatic restyling of earlier functionality-only work. Deprecation/unavailability requires a scoped decision, not a guessed substitute or silent dependency update.

## Preview and meaningful HTML

For new design-pending UI, identify an existing authorised preview/development surface and who can access it. An arbitrary URL is not isolation: check whether production builds, public navigation or users can reach it. Do not create a standalone prototype, feature-flag framework, new preview route or install a UI tool without scoped approval. When there is no approved destination, stop UI integration and continue only independently approved logic/tests. A specific exception to expose unfinished work requires explicit audience/risk/scope; it still does not count as design acceptance or bypass platform protections.

Plain means no new visual decisions, not zero computed styling. Inherited/global CSS can affect new HTML. Do not add resets, inline attributes, utility classes or cosmetic wrappers to compensate. Use the framework's existing rendering mechanism (React JSX, Blade, native equivalents), semantic controls, meaningful labels, validation and accessible state feedback. Functional IDs/ARIA references or test hooks are allowed only for their stated purpose, not as hidden styling selectors. Do not remove an existing ID/class/attribute without checking its CSS, behaviour and integration consumers.

Substantial decisions about where a dialog opens, focus handling, confirmation steps or mobile layout are not mere CSS choices. Settle consequential interaction decisions through grilling; group nonblocking gaps. An unavoidable accessibility repair that needs styling receives a bounded approved exception; do not ship inaccessible work or use accessibility as permission for a redesign.

## Styling routes and exceptions

New presentation through stylesheets, inline styles, style tags, CSS-in-JS, utility classes, visual component props, tokens, SVG/canvas drawing, native attributes, Unity/Pixi/Three visual assets or configuration is subject to the same boundary. A runtime animation/geometry calculation already required by the approved behaviour is not banned; preserve its established mechanism and approve material changes explicitly. Neither source extension nor “no CSS file touched” determines compliance.

A narrow styling bug fix records the exact area/property or contract, reason, approving response and verification. It does not change the whole task to design-authoring. Approval is task authority, not authentication supplied by a checker.

## Reports are not application prototypes

Generating the normal workflow HTML/SVG review through the bundled codebase-map renderer and its approved assets remains permitted. Reports explain behaviour and approval, not a newly designed application interface. Do not modify the report theme or create arbitrary prototype HTML under a `reports/` path to evade this boundary. The bundled codebase-map/UI-FLOW.md extension may show source-backed screen captures or explicitly authorised, labelled schematics inside the existing full report. Preview permission, source choice and app implementation remain separate. No raw application HTML/CSS/scripts execute in that viewer. An illustration is not approved kit evidence. Changes to the report renderer/design require their own explicit package-maintenance scope.

## Lifecycle, handoff and release

Keep the mode, sources, preview boundary and acceptance in the current existing task checkpoint. Behaviour complete/tested, design accepted, and release-ready are distinct. An authorised designer's acceptance may be recorded by reference; the agent does not approve itself. Existing approved interfaces need no fresh designer review for every no-appearance-change bug fix, but must be checked for regressions.

A handoff or kit update triggers targeted reconciliation, not another task folder or approval of unchanged work. If old records lack a mode, establish it for the next UI unit; preserve earlier history and work. Even an old implementation approval does not silently permit previously unapproved styling.
