# Verify the boundary, not just CSS filenames

Inspect actual task changes against the initial ownership baseline and the recorded UI mode. Include staged, unstaged and untracked work, deletions, shared component definitions, generated outputs and visual assets where relevant. Do not attribute all working-tree changes to this task or stage files to obtain a diff. Resolve unknown ownership rather than deleting others' work.

## Review sequence

1. Reconcile area, mode, source/kit revision, approved variants/patterns, exact exceptions and preview destination. Check project constraints and the shared design rule. No evidence means not verified, not approval.
2. Inspect changed markup and styles, imports, utility-class combinations, styling APIs, visual props, CSS tokens, assets and native/rendering code. Existing classes may be unapproved, and changing a component definition can affect many screens. Review removed styling as well as new styling.
3. Verify relevant observable behaviour, validation, labels, keyboard/focus flow and disabled/loading/error states. Use existing tooling and approved targets. Do not install Storybook, a component library, browser dependencies or test frameworks just to claim a check ran.
4. Inspect visible effects in authorised environments. Existing global styles, DOM order/wrappers and non-CSS renderers can alter appearance. For existing/kit interfaces, compare approved references under controlled conditions when available; missing references are not a request to invent a new baseline. For behaviour-only work, verify unchanged markup/appearance and the intended behaviour; for approved-kit work check the exact pattern/variant selection. New plain controls are a policy violation, not a legitimate fallback.
5. Report evidence and limits. Keep only useful captures/results under the workflow artifact policy. Designer handoff reuses existing records. Missing browser/device access means the visual layer is unverified. A static scan is not an accessibility audit or release gate.

## Optional local diff triage

`python -X utf8 <installed-ui-design>/scripts/review_ui_diff.py` reads a standard unified diff on stdin. `--diff /path/to/existing.diff` reads an existing file. No command execution, network, dependency install, repository walk, Git writes or output files. Do not create a diff artifact just for this helper; use stdin when available. Feed only the correctly attributed patch, with necessary context, after inspecting how it was obtained. New/untracked files must be included explicitly; a plain Git diff may omit them.

The result identifies review cues with paths and line numbers, without copying potentially sensitive source lines. Exit codes: **0** = no recognised styling cues (or empty input), **1** = review required, **2** = invalid/unsupported input. It never returns approval, policy compliance, design acceptance or release readiness. Do not wire exit 0 into automatic design signoff. Legacy design-authoring language does not exempt these cues; an application task is not exempt because its path contains `report`, `test` or `preview`.

The scanner is intentionally conservative, not a parser for every language. It cannot prove the semantics of arbitrary component props, dynamic styles, external components, global selector effects, minified/generated code or binary assets. Unknown/nontext changes remain review-required. Quoted and normal paths are supported; combined diffs and unsupported encodings fail closed. It never opens paths named inside the patch. If it cannot inspect the patch, use authorised manual review; do not treat an error as a clean pass.

## Required negative and legitimate cases

Test new/removed CSS, inline styles, style tags, CSS-in-JS, arbitrary class combinations, theme/visual props, SVG/native/Unity/Pixi changes and new visual dependencies. Test that a newly authored no-styling semantic form is blocked by policy review, while behaviour-only changes preserving presentation and selected approved-component API use remain possible. A styling repair is still blocked under this policy; it is not an automatic accessibility or bug-fix exception. Exercise new/untracked and binary files, malformed inputs and no-write behaviour. Mechanical tests establish the helper's behaviour, not the agent's compliance.

Live acceptance must also test ordinary prompts without `/workflow`, missing kit coverage, preview exposure, rejection of legacy design-authoring permission, a subagent, a resumed task and the approved report exemption. Inspect actual file changes and decisions; do not grade “I followed the rules” as a pass.

## Visual approval report

For a UI task, inspect the bundled screen flow in the complete report. Verify source/kit selection, actual capture provenance, schematic labels, task/requirement mapping, transitions and design-decision markers. Confirm that no file name or illustration is treated as approval. Compare the unchanged report shell against the established reference; the UI extension is additive. A report image is not live interaction/device verification. Existing no-appearance-change tasks need no repeated screen sample.

## Strict reuse and live references

Check actual approved component calls and patterns, not an allow-list of class names. Review changed definitions and runtime styles as well as their callers. Before approval-ready application reports, select kit_binding and per-screen elements with a composition pattern, real capture/capture record and exact variants/states. Detect changed, removed, unapproved or out-of-scope sources. Reuse the generated live inventory; do not rewrite Markdown component inventories. Source checker exit 0 still means manual/semantic review, not compliance or permission. Test component deletion, story removal, changed dependency, stale capture context and unchanged historical HTML.
