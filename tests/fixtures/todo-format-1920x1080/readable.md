# Tickets (revision 1, proposed 2026-11-04)

Test output: `.artifacts/2026-11-04-1920x1080-format/` (only the T4 captures; deleted after owner acceptance unless kept as evidence).

## Overview

| Ticket | What needs to happen | Status | Dependencies |
|---|---|---|---|
| T1 | Add the 1920×1080 format for category-a, linked to Template 1 | Verified | none |
| T2 | The server refuses 1920×1080 with any other template | Not started | T1 |
| T3 | Show 1920×1080 only for Template 1 | Not started | T1 |
| T4 | Check that Template 1 draws cleanly at 1920×1080 | Not started | T1 |

T2 and T3 share no file and can run in either order after T1.

## Tickets

### T1 — Add the 1920×1080 format for category-a, linked to Template 1
Status: Verified

What needs to happen: Add the format `fmt-hd` (1920×1080), offer it to category-a only and link it to Template 1, on fresh and live databases.

What should work:
- `GET /formats` for category-a lists `fmt-hd` last, with `template_ids` = [Template 1's id].
- Every other preset has `template_ids` = []; category-b does not get `fmt-hd`.
- Running the migration twice adds nothing twice.
- On a database without a Template 1 row the migration adds nothing, so the format never appears unlinked and open to every template.

Technical details:
- `server/app/FormatCatalog.php`: definition `fmt-hd` 1920x1080 sort 11, `CATEGORIES['fmt-hd'] = ['category-a']`, new `TEMPLATES` map `'fmt-hd' => ['template-1']`.
- New migration creating `format_template`: preset FK, template FK, both cascade on delete, unique pair, index on template.
- New live-data migration adding `fmt-hd` and its category-a and Template 1 links: additive, idempotent, links frozen in the migration, skips a missing category or template; `down` removes only an unused preset row.
- `server/app/Models/Format.php`: `templates()` relation.
- `server/database/seeders/FormatSeeder.php`: links templates that exist; skips a template-limited preset when none of its templates exists (same reason as D1).
- `DatabaseSeeder.php`: runs FormatSeeder after LayoutSeeder, so template rows exist on a fresh database.
- `FormatController::payload` and `index`: add `template_ids`, eager-loaded; an empty list means every template.
- `server/lang/locale.json` key `format.fmt-hd` = "1920 × 1080 px"; `CONTEXT.md` "Format" entry (links to Templates); generated `web/app/src/i18n/locale.json` via `npm run sync:i18n` only.
- Must not change: other presets' rows, sort orders or category links; layout packs; `LayoutCatalog`.
- Test seam: feature tests on `GET /api/formats` (FormatTest, CategoryOfferTest) and a migration test running `up()` twice on a seeded database. They miss MySQL-only behaviour; the migration uses only portable query-builder calls.
- TDD: yes.

How to verify:
- From `server/`: `composer test` and `composer lint` pass.

Verification: passed

References:
- Supports: R1, R2, R4, A6, A7
- Depends on: none
- Decision: D1 (by: agent)
- Rules: AGENTS.md (live data by additive idempotent migration, never a seeder), `.claude/rules/backend.md` (FK/index/unique in migration, explicit payload, eager loading)
- Evidence: FINDINGS V1, V1-review

### T2 — The server refuses 1920×1080 with any other template
Status: Not started

What needs to happen: Saving a area that pairs 1920×1080 with a template other than Template 1 is refused for every actor, including invitations.

What should work:
- PUT screen areas with `fmt-hd` + Template 2 or Template 3 → 422 with the message; nothing saved.
- A Template 1 area on `fmt-hd` switched to Template 2 → 422; the area is unchanged.
- `fmt-hd` + Template 1 → saved; the area is 1920x1080 on Template 1's current release.
- Every other preset with any category-a template → saved as before.
- An invitation with `fmt-hd` + Template 2 → 422.

Technical details:
- `server/app/Services/Assignment.php`: one guard beside `guardCategory`, for every actor. A area whose preset has template links and whose template is not among them is refused on `areas.N.format_id`. A area keeping both its current preset and current template stays allowed (the exemption rule `guardCategory` uses).
- `server/lang/locale/errors.php`: new `presetOtherTemplate`.
- Tests: `server/tests/Feature/AssignmentTest.php` and the invitation tests (`Invitee` reaches the same service).
- Must not change: `guardCategory` behaviour, area geometry rules, custom-size areas without a preset (not restricted).
- Test seam: HTTP feature tests on the screen update and invitation endpoints; they catch every pairing path. The UI filter is T3.
- TDD: yes (red first on the refusal cases).

How to verify:
- From `server/`: `composer test` and `composer lint` pass.

Verification: not run

References:
- Supports: R3, R6, A3, A4
- Depends on: T1
- Rules: AGENTS.md, `.claude/rules/backend.md` (translated domain errors, validation shape unchanged)
- Evidence: none

### T3 — Show 1920×1080 only for Template 1
Status: Not started

What needs to happen: Both format pickers list 1920×1080 only when the area's template is Template 1. Formats without template links stay available for every template.

What should work:
- A1 and A2 as written in the agreement, in both popups.
- Formats without links are listed for every template, as before.
- A selected format that no longer fits the new template resets to the first fitting one.

Technical details:
- `web/api/src/types/screens.ts`: `Format.template_ids: number[]`.
- `web/app/src/lib/format.ts`: one rule, "a preset fits a template when it lists none or lists that template", used by both pickers.
- `account-dialog.tsx` (single area and the dormant multi-area list) and `invite-dialog.tsx`: options filtered by the area's selected template.
- Web Jest tests beside `__tests__/account-single.web.test.jsx`, `account-areas.web.test.jsx`, `invite-*.web.test.jsx`.
- Must not change: the select component and its styling (behaviour-only: an option shows or not; no new element, no CSS); MULTI_AREA_EDITOR stays off and its path keeps working.
- Test seam: rendered popups with mocked `formatsApi`/`layoutsApi`, asserting visible options and the value after a template change. They miss native (iOS/Android) select rendering; the logic is shared, and the popups are admin, web-first.
- TDD: yes.

How to verify:
- From `web/`: `npm run typecheck`, `npm run lint` and `npm test` pass.

Verification: not run

References:
- Supports: R5, A1, A2
- Depends on: T1
- Rules: `.claude/rules/frontend.md` (derive during render, no mirrored state, i18n), `web/app/AGENTS.md` (no styles), ui-design behaviour-only mode
- Evidence: none

### T4 — Check that Template 1 draws cleanly at 1920×1080
Status: Not started

What needs to happen: Confirm that Template 1 fills a 1920×1080 panel without clipping, with the banner at the top, at the bottom and hidden. No layout file changes.

What should work:
- A5.
- The layout-fit and region-sizes tests pass with 1920x1080 included for Template 1.

Technical details:
- `server/tests/player/layout-fit.test.js`: adds 1920x1080 to the formats checked for Template 1; the "range gets squarer" check keeps its meaning for the display range.
- Must not change: Template 1/2/3 layout files. If the captures show clipping, stop and ask before any pack change (that needs the "new release" from Q4).
- TDD: no for the captures (visual check); the layout-fit addition is a characterisation test of current behaviour, expected green.

How to verify:
- From `server/`: `node --test tests/player/*.test.js` passes.
- Headless browser captures of the Template 1 preview at 1920x1080 with the banner top, bottom and hidden, saved in `.artifacts/2026-11-04-1920x1080-format/`.
- Human check: the owner looks at the three captures (or a real display) after T4.

Verification: not run

Owner acceptance: none

References:
- Supports: R7, A5
- Depends on: T1
- Rules: `.claude/rules/player.md` (verify fill, clipping and legibility at every supported preset)
- Evidence: none
