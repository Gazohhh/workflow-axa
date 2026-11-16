---
name: refactor
uses: [codebase-design, tdd, code-review]
fallbacks: [Direct check]
approval-exceptions: none
---

# Refactor

Change the structure, keep the behaviour, and prove both.

1. **Map the contract:** callers, inputs, outputs and side effects that must stay the same.
2. **Characterisation tests first.** Lock today's observable behaviour with tests before moving anything.
3. **Subtract before adding.** Remove dead code, redundant checks and stale references inside the approved scope first; report dead code outside it rather than removing it.
4. **Reshape** with `codebase-design`: fewer layers between a question and its answer, smaller mutable scope.
5. **Internal APIs:** move every caller and delete the old API in the same change. A public interface keeps a deprecation path (Compatibility modifier).
6. **Prove equivalence:** the characterisation tests pass unchanged; review with `code-review`.

**Done when:** the characterisation tests pass without edits, no caller uses the old shape, and the review found no behaviour change.
