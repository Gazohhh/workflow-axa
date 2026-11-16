---
name: feature
uses: [grilling, tdd, code-review, codebase-design]
fallbacks: [Reduced evidence, Conditional design]
approval-exceptions: none
---

# Feature

Add or change behaviour that users or callers notice, with every open choice settled first.

1. **Trace the journeys and callers** the change touches: who uses it, from where, and what happens on failure.
2. **Ask only open choices** through `grilling`: behaviour, scope, compatibility or safety decisions the code can't answer.
3. **Shape the seam** with `codebase-design` only when the right interface is disputed.
4. **Slice vertically.** Each ticket ends in a working, checkable state and the order proves itself to a reviewer.
5. **Build each ticket test first** with `tdd`, asserting what users or callers can observe.
6. **Check the integration** across the touched journeys, then review with `code-review`.

**Done when:** every ticket has its passing tests, the journeys work end to end, and the docs describe the new behaviour.
