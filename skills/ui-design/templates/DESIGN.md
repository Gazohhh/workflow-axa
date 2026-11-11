<!--
Template for a project's DESIGN.md: design decisions, allowed use and approval history.
Replace every [bracketed] placeholder with confirmed facts, or leave it visibly unresolved.
Never invent components, approvals, dates or owners. Keep CSS values, size tables, source
line numbers, usage counts and component inventories out of this file: the application
source and the live kit own appearance, and the coverage test is generated from the views, not copied here.
Delete this comment when the file is adopted.
-->

# Design intent and approvals

This file records design decisions, allowed use and approval history. Current appearance comes from the application source. [Optional: product principles live in ...; implementation rules live in AGENTS.md.]

## Source of truth

The live kit at `[/design-kit]` renders the application's actual components and existing patterns with synthetic data. Its page templates `[path]` and fixtures `[path]` own the examples.

Component templates, component styles, the global stylesheet `[path]` and theme/tokens `[path]` own appearance. Rebuilding and reloading reflects changes to existing components and styles without editing this document.

Each component example is registered once in the kit. A new component needs one registered example and any local fixture data; new inputs or states need an example update. A coverage test generated from the views fails when a repeated pattern is neither on the kit page nor excluded with a reason.

[External design references, such as a design-tool file, record intent only. A missing or uncertain match does not override an explicit owner approval of the code.]

## Scope and access

This policy covers [application/client/platform]. [Areas with separate owners] are outside this kit's scope.

### How to open the kit

Open `[/design-kit]` in a development build using the repository's existing development tooling. It needs no login and uses the application's real layout, providers and styles. [Production/staging/other] builds exclude the route through [the existing build-mode mechanism]. [Client builds: each client's kit page includes its overrides and its enabled modules' components, in the same element groups as core.]

Previews use synthetic fixtures with backend requests blocked. Never use customer data or run real account, payment, printing or backend actions to demonstrate a control. The kit labels examples that cannot render, with the reason. A rendered example does not prove its full feature journey, backend or native-device behavior was tested.

## Approval authority

[Owner/role named by the project] approves design changes in [chat/PR/task record]. Record the decision, date and exact scope here or in the linked task. Screenshots, source changes and presence in the kit are evidence, not approval.

[Approved groups with date and revision, for example: "The owner approved the existing ... on YYYY-MM-DD (r2)." An approval covers the entries at that revision, not future components or combinations.]

[Candidate groups: existing uses can remain; new uses need owner review.]

## Reuse and changes

Use an existing component through its supported inputs and events. For an existing markup pattern, preserve its tag, full class list and required wrappers. Search the kit first, then real application callers. Do not recreate a component's internal markup, invent visual variants or add CSS to improve a preview.

A candidate can remain in its current use; promoting it to a general standard needs an explicit owner decision, as does any new or materially changed design. Routine styling changes flow from source into the live kit without transcribing values here.

If no matching element exists, ask: "I couldn't find a matching style for [element]. Is there an existing element I should mimic?" Plain unstyled HTML requires the owner's explicit instruction for that element.

## Usage decisions

[Status: caller-inferred guidance until the owner approves it. Replace this line with the approval reference once approved.]

One short entry per family, stating intended use and distinctions to preserve, without CSS values or inventories:

- [Actions: ...]
- [Lists: ...]
- [Forms: ...]
- [Feedback and overlays: ...]
- [Navigation and layout: ...]

## Known source findings

[Unresolved issues found in the source: unimplemented design references, inert or context-dependent variants, intent that differs from code. Each needs an owner decision; none revokes a recorded approval.]

## History

| Revision | Date | Owner decision |
|---|---|---|
| r1 | [YYYY-MM-DD] | [Initial inventory. All entries were candidates.] |
