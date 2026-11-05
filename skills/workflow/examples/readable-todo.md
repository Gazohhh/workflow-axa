# TODO — example of the readable ticket format

An illustration based on a 1920×1080 panel-format task. The states are chosen to show each field; they are not a
real project's records. The full conversion of that task's TODO, with its states unchanged, is
`tests/fixtures/todo-format-1920x1080/readable.md`.

## Overview

| Ticket | What needs to happen | Status | Dependencies |
|---|---|---|---|
| T1 | Add the 1920×1080 format for football, linked to Template 1 | Verified | none |
| T2 | Check that Template 1 draws cleanly at 1920×1080 | Blocked | T1 |
| T3 | Show 1920×1080 only for Template 1 | Not started | T1 |

## Tickets

### T3 — Show 1920×1080 only for Template 1
Status: Not started

What needs to happen: Both format pickers list 1920×1080 only when the zone's template is Template 1. Formats without template links stay available for every template.

What should work:
- With Template 1 selected, both popups list 1920×1080; with Template 2 or 3 they do not.
- A selected format that no longer fits a newly chosen template resets to the first fitting one.
- Formats without links are listed for every template, as before.

Technical details:
- `frontend/apps/operator/src/lib/panel-preset.ts`: one rule, "a preset fits a template when it lists none or lists that template", used by both pickers.
- `account-form-popup.tsx` and `subuser-invite-popup.tsx`: options filtered by the zone's selected template.
- Must not change: the select component and its styling; no new element, no CSS.
- TDD: yes. Test seam: rendered popups with mocked APIs; native select rendering is not covered.

How to verify:
- From `frontend/`: `npm run typecheck`, `npm run lint` and `npm test` pass, including new popup tests for the three cases above.

Verification: not run

References:
- Supports: R5, A1, A2
- Depends on: T1
- Rules: `.claude/rules/frontend.md`, ui-design behaviour-only mode
- Evidence: none

### T2 — Check that Template 1 draws cleanly at 1920×1080
Status: Blocked

What needs to happen: Confirm Template 1 fills a 1920×1080 panel without clipping, with the banner at the top, at the bottom and hidden.

What should work:
- `panel-fit` and `panel-region-sizes` tests pass with 1920x1080 included for Template 1.
- The three captures show no clipping. If they do, stop and ask before any pack change.

Technical details:
- `backend/tests/player/panel-fit.test.js` only; no pack file changes.

How to verify:
- From `backend/`: `node --test tests/player/*.test.js` passes.
- Headless Edge captures at 1920x1080, banner top, bottom and hidden, in the task's output folder.
- Human check: the owner looks at the three captures after T2.

Verification: tests passed (FINDINGS V4); captures not taken
Blocker: no Edge available on the build machine

Owner acceptance: none

References:
- Supports: R7, A5
- Depends on: T1
- Evidence: FINDINGS V4

### T1 — Add the 1920×1080 format for football, linked to Template 1
Status: Verified

What needs to happen: Add the `100m2` format, offer it to football only and link it to Template 1.

What should work:
- Football lists `100m2` last with `template_ids` = [Template 1's id]; other presets list none.

Technical details:
- Catalog, two additive idempotent migrations, seeder and payload, as approved in revision 1.

How to verify:
- From `backend/`: `composer test` and `composer lint` pass.

Verification: passed

References:
- Supports: R1, R2, A6
- Depends on: none
- Decision: D1
- Evidence: FINDINGS V1
