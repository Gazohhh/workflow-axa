---
name: bug
uses: [tdd, code-review, grilling]
fallbacks: [Static diagnosis, Direct check]
approval-exceptions: none
---

# Bug

Find the first place the system goes wrong, prove it, and fix it there.

1. **Reproduce.** Build the shortest feedback loop that shows the failure: a test, a script or a request. A probe runs before approval only when every condition of the standing diagnostic allowance holds: it writes only to an owned disposable location, uses synthetic, sanitised or already authorised inputs, runs on an established isolated target, involves no protected operation, install, external change or persistent configuration change, stays within the OPERATIONS resource limits, and keeps its output under the artifact policy. Anything else, such as instrumenting the real app, goes into the plan. No reproduction: record Static diagnosis and say what stays unproven.
2. **Settle the expected result.** When the correct behaviour is unclear or owned by someone else, ask through `grilling`; never infer it from the current code.
3. **Simple branch** (expected result clear, one owner, cause known): go to step 5.
4. **Complex branch** (cause unknown or intermittent, whatever else is clear): rank falsifiable hypotheses, run the probe that separates them best, and shrink the failure to its minimum. After two fixes that share one assumption have failed, test that assumption directly before a third fix.
5. **Regression test first** with `tdd`: write it and see it fail before changing the code.
6. **Fix the root cause** until that test passes. Add a guard only when the state it handles is legitimate. A root cause outside the approved scope is a new or revised plan, never a silent widening.
7. **Review** with `code-review`; when the fix touches code others depend on, name what could break outside the diff and run the check that proves the key fact.

**Done when:** the reproduction passes, the regression test went red then green (or the recorded alternative evidence), and the review found nothing open.
