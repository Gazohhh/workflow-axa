---
name: refactor
uses: [codebase-design, tdd, code-review]
fallbacks: [Direct check]
approval-exceptions: none
---

# Refactor

Change the structure, keep the behaviour, and prove both.

1. **Map the contract:** callers, inputs, outputs and side effects that must stay the same, including the readers a search misses (the planning form of `../../code-review/BLAST-RADIUS.md`).
2. **Write characterisation tests first** that lock today's observable behaviour before anything moves.
3. **Subtract before adding:** remove dead code, redundant checks and stale references inside the approved scope; report dead code outside it rather than removing it.
4. **Reshape** with `codebase-design`: fewer layers between a question and its answer, smaller mutable scope.
5. **Move every caller of an internal API** and delete the old API in the same change; a public interface keeps a deprecation path (Compatibility modifier).
6. **Prove equivalence:** the characterisation tests pass unchanged; review with `code-review`, whose step 4b proves the mapped contract (`../../code-review/BLAST-RADIUS.md`).

**Done when:** the characterisation tests pass without edits, no caller uses the old shape, and the review found no behaviour change.
