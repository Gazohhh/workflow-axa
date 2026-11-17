---
name: migration
uses: [plan-review, tdd, code-review]
fallbacks: [Offline rehearsal]
approval-exceptions: the live or destructive step needs its own approval after the rehearsal
---

# Migration

Move data, schemas, protocols or dependencies without breaking anyone who relies on them.

1. **Inventory consumers:** every reader and writer of what changes, including other services, jobs and saved data; use the "Where grep stops" list in `../../code-review/BLAST-RADIUS.md`.
2. **Compatibility matrix:** which old and new versions must work together, and for how long.
3. **Staged plan:** small reversible steps, each with its check and its rollback; review it with `plan-review`.
4. **Rehearse** on a copy and record the result. No copy available: record Offline rehearsal and what stays unproven.
5. **Prepare** code and scripts test first (`tdd`) and review them with `code-review`; its step 4b proves each consumer's safety fact (`../../code-review/BLAST-RADIUS.md`).
6. **Live or destructive step:** ask for its own approval, then run it and check the result against the rehearsal.

**Done when:** the rehearsal evidence and the live result match, the rollback path is documented, and no consumer is left on an unsupported version.
