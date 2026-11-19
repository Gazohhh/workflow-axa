---
name: bug
uses: [tdd, code-review, grilling]
fallbacks: [Static diagnosis, Direct check]
approval-exceptions: none
---

# Bug

Find the first place the system goes wrong, prove it, and fix it there.

1. **Reproduce** the failure with the shortest feedback loop: a test, a script or a request. Run a probe before approval only when every condition of the standing diagnostic allowance (`../../rule-maker/rules/OPERATIONS.md`) holds; anything else, such as instrumenting the real app, goes into the plan. No reproduction: record Static diagnosis and what stays unproven.
2. **Settle the expected result** through `grilling` when it is unclear or owned by someone else; never infer it from the current code.
3. **Take the simple branch** (expected result clear, one owner, cause known): go to step 5.
4. **Take the complex branch** (cause unknown or intermittent, whatever else is clear): rank falsifiable hypotheses, run the probe that separates them best, shrink the failure to its minimum. After two failed fixes that share one assumption, test that assumption directly before a third.
5. **Write the regression test first** with `tdd` and see it fail before changing the code.
6. **Fix the root cause** until that test passes. Add a guard only for a legitimate state. A root cause outside the approved scope is a new or revised plan, never a silent widening.
7. **Review** with `code-review`; its step 4b proves the safety facts (`../../code-review/BLAST-RADIUS.md`).

**Done when:** the reproduction passes, the regression test went red then green (or the recorded alternative evidence), and the review found nothing open.
