---
name: new-project
uses: [rule-maker, domain-modeling, codebase-design, tdd]
fallbacks: [Conditional design, Direct check]
approval-exceptions: none
---

# New project

Start a project with its rules, its first decisions and one small working slice.

1. **Rules first.** Run the rules readiness check ([../RULES.md](../RULES.md)) and offer its choices. With setup chosen, `rule-maker` proposes the minimal rules and they are applied before the slice. With a limited exception, its named gaps are listed at delivery.
2. **Constraints and owners.** Record the stack, hosting, data and ownership decisions that are already made; ask only the open ones.
3. **Language.** Name the domain's core terms with `domain-modeling` when they're not obvious.
4. **Optional prototype.** To answer a design question, propose a throwaway prototype as its own approved scope: an isolated folder and only the files that approval names. It's deleted afterwards; moving any of it into production code needs a separate approval.
5. **First slice.** One thin end-to-end path, built test first with `tdd`. Nothing is installed without the owner's OK.

**Done when:** the rules exist (or their gaps are listed), the first slice runs and its tests pass, and the next decisions are written down.
