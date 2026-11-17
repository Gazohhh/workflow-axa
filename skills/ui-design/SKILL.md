---
name: ui-design
description: "Use for any application UI work (behavior-only included), in workflow or ordinary requests, and to build or check a design kit or DESIGN.md. Reuse existing classes and IDs; when nothing matches, ask which existing element to mimic. CSS only when the owner switched it on."
---

# UI: reuse, do not invent

Write kit findings and reports for a person, as `../workflow/WRITING.md` says; application UI copy is not changed by those rules.

Read `../rule-maker/rules/DESIGN.md` (the installed sibling skill) and [CONTRACT.md](CONTRACT.md). This is a permission/selection skill, not a designer or another implementation workflow. The normal rules-readiness gate, grilling, plan review and implementation approval remain in force.

## 1. Establish the surface and decision

Identify the task, framework versions, affected area/brand/platform, designated project sources, existing changes and applicable rules. Backend-only work skips this skill unless it changes UI contracts. A missing DESIGN.md filename is not a blocker when an equally authoritative source exists. The mere presence of that file, a catalog or a familiar class is not selection/approval.

For a new substantive UI task, confirm the exact source and selected component/pattern IDs, variants and states. Reuse explicit owner choices or a still-valid same-task decision. Ask once when unresolved, batching consequential gaps through grilling. Do not ask again on every control or unchanged resume.

## 2. Select a permitted mode

Pick **behaviour-only**, **reuse**, **blocked** or **plain-by-instruction** exactly as the shared rule-maker `rules/DESIGN.md` defines them; [CONTRACT.md](CONTRACT.md) lists what each permits and forbids. For each new or changed element, search the design kit (if any) and the existing code for an element doing the same job for the same user (DESIGN.md rule 4), and record the element you mirror as `file:line`, tag, classes, the wrapper it needs and why it fits that job (`python -X utf8 -I scripts/class_rules.py <project-root> <class>...` lists every rule for a class, marking the ones that need context). No new CSS while the machine CSS switch is off (`settings.py show`; DESIGN.md rule 1); never switch it yourself. No new plain-HTML controls without the user's explicit instruction. A blocked element waits for the user's answer to the exact question in DESIGN.md rule 4; offer only what that rule allows; a plain-HTML exception needs that rule's explicit instruction, never a blanket yes. Independent logic and tests can continue.

Use [KIT.md](KIT.md) for `kit-audit`, `kit-setup`, `kit-check` and [LIVE-KIT.md](LIVE-KIT.md) for code-backed discovery. For manual designer changes, run `scripts/design_drift.py --root <project>`; reconcile its findings as [LIVE-KIT.md](LIVE-KIT.md) explains. Setup can audit/propose the development-only kit route inside the application and a DESIGN.md shaped by `templates/DESIGN.md`; it cannot create application presentation, install tools or approve new components. Designer changes are external inputs to reconcile, not permission for this agent to write CSS. Older mode names map as CONTRACT.md says.

## 3. Prepare the existing plan/report

Keep one compact selection record in the PLAN checkpoint (a legacy task's `STATUS.md` when it has one): mode, area, authority, stable item/story IDs, component and example sources, variants/states, selected pattern and why, preview access and remaining design/release limits. No duplicate component inventory or new folder per selection. Use [EXAMPLES.md](EXAMPLES.md).

For quick styled references, use `ui_review.quick_previews` with existing HTML and compiled CSS; see codebase-map/UI-FLOW.md. No prototype build or claims of live framework rendering.

When the owner asks for the plan report, a UI-visible change gets a **screen diagram** in it: `workflow/VISUAL-REVIEW.md` "UI work" owns the rules: kit screens with a design kit, else a capture and a sketch. A sketch shows structure, not the look.

With the CSS switch on, the offer lists the style-bearing files it may change (DESIGN.md "What counts as styling") and names a visual check. A visual change whose look the owner hasn't settled is reported as "design acceptance pending".

Resolve material decisions, present the offer and the one question (`workflow-specify` step 5) and stop for owner approval; the plan report is optional, built when the owner asks. Behavior approval is not unseen design signoff. New ordinary UI requests use these gates even without a slash command.

## 4. Implement and verify only authorized reuse

Pass the same selected IDs, APIs, pattern, source revision, protected internals and preview permissions to workers. No CSS, inline style or arbitrary visual props while the CSS switch is off; new elements mirror an existing element's class and tag, or are plain only where the user said so. Preserve existing functional selectors and runtime contracts. Accessibility remains required: reuse an accessible existing element or ask; never ship an inaccessible substitute. Before finishing, list each class used with the file that defines it. With the CSS switch off, confirm no CSS was added. With it on, confirm the styling stays within the offer's listed style files and that the named visual check ran.

Use [VERIFY.md](VERIFY.md) on the actual final diff and relevant runtime states; its `review_ui_diff.py` section covers the diff check. Check source/variant/scope freshness, safe environment and build permissions before executing previews. Keep approved references and follow the artifact policy.

On update/deletion/resume, reconcile only affected sources/consumers. A missing component blocks its selection; a changed one needs review, not automatic reapproval. Preserve historical captures and decisions. Report behavior verified, design accepted and release-ready separately. Never claim a live kit was installed or every host follows the rules unless actually checked.
