# Specialist integration — workflow-axa 2.0.0

## Current checkpoint
- Status: done (package delivered; runtime rollout not evaluated)
- Owner: release-building assistant; ownership: released
- Updated: 2026-10-09
- Repository / worktree: extracted workflow-axa-2.0.0-rc.1 ZIP; no Git repository
- Approved revision and scope: R1; user requested the agreed integration and a new 2.0.0 ZIP
- Active tasks: none
- Last completed step: final archive integrity, extraction and 39-test rerun passed (V4)
- Next safe action: teammate reviews SETUP.md, checks the actual host installation, and runs the documented local runtime pilot
- Blocked decisions: none; live host evaluation is unavailable here

## Goal and acceptance
One workflow coordinates relevant installed Matt Pocock specialist skills rather than
silently recreating them. Keep documented approval, scope, question timing, task records,
recovery, cleanup, no automatic Git mutations, and optional PDF delivery. Publish nothing.
Deliver a source-only ZIP labelled 2.0.0 with honest validation limits.

## Approach and scope
Change the workflow package only. Add one integration reference, a dependency catalogue,
a portable read-only local checker, setup guidance, and regression scenarios. Route to
model-invocable specialists; user-only workflows remain explicitly user-invoked.
Do not bundle upstream skill copies, silently install dependencies, or modify host caches.
Check collection installation separately from selected-route readiness and runtime use.

Verification: existing fixture tests, new checker tests, structural/reference/version
checks, and a final extracted-archive rerun. No claim of live agent behavior validation.

## Approval
R1 approved by: “do that give me a new zip 2.0.0 version”. This follows the proposal for
explicit specialist routing, installation/availability checks, documented adaptations,
and a single /workflow entrypoint. Routine implementation and tests are covered.
Installing on teammates’ machines, publishing/tagging, or claiming live host test success
is not covered. The version is the user-selected package version, not a reliability certification.

## Outcome
2.0.0 source package complete. One workflow, explicit specialist routes, installation/check
procedure and local regression tooling delivered. Local package/tooling and extracted-archive
checks passed. Runtime host installation and behavior, Windows execution and real cross-account
recovery remain UNTESTED; see VALIDATION.md. Nothing installed, committed or published.
