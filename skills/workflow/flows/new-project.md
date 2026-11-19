---
name: new-project
uses: [rule-maker, domain-modeling, codebase-design, tdd]
fallbacks: [Conditional design, Direct check]
approval-exceptions: none
---

# New project

Start a project with its rules, its first decisions and one small working slice.

1. **Run the rules readiness check first** ([../RULES.md](../RULES.md)) and offer its choices. Setup chosen: `rule-maker` proposes the minimal rules, applied before the slice. A limited exception: list its named gaps at delivery.
2. **Record constraints and owners:** the stack, hosting, data and ownership decisions already made; ask only the open ones.
3. **Name the domain's core terms** with `domain-modeling` when they're not obvious.
4. **Propose a throwaway prototype only to answer a design question**, as its own approved scope: an isolated folder and only the files that approval names. Delete it afterwards; moving any of it into production code needs a separate approval.
5. **Build the first slice:** one thin end-to-end path, test first with `tdd`. Nothing is installed without the owner's OK.

**Done when:** the rules exist (or their gaps are listed), the first slice runs and its tests pass, and the next decisions are written down.
