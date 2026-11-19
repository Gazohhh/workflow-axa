---
name: feature
uses: [grilling, tdd, code-review, codebase-design]
fallbacks: [Reduced evidence, Conditional design]
approval-exceptions: none
---

# Feature

Add or change behaviour that users or callers notice, with every open choice settled first.

1. **Trace the journeys and callers** the change touches: who uses it, from where, what happens on failure. If it changes existing behaviour, record the safety assumptions for the callers and consumers it changes with the planning form of `../../code-review/BLAST-RADIUS.md`; a purely additive feature records "none" with its boundary trace.
2. **Ask only open choices** through `grilling`: behaviour, scope, compatibility or safety decisions the code can't answer.
3. **Shape the seam** with `codebase-design` only when the right interface is disputed.
4. **Slice vertically:** each ticket ends in a working, checkable state, in an order that proves itself to a reviewer.
5. **Build each ticket test first** with `tdd`, asserting what users or callers can observe.
6. **Check the integration** across the touched journeys, then review with `code-review`; its step 4b proves the safety assumptions from step 1 (`../../code-review/BLAST-RADIUS.md`).

**Done when:** every ticket has its passing tests, the journeys work end to end, and the docs describe the new behaviour.
