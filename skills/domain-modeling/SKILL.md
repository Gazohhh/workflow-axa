---
name: domain-modeling
description: "Sharpen a project's domain terms and decisions. Use when a term, owner or boundary is unclear or changing, or when editing the glossary (CONTEXT.md or GLOSSARY.md) or an ADR."
---

# Domain Modeling

Actively build and sharpen the project's domain model as you design. Use this skill when a term, owner or domain boundary is unclear or being changed: challenge terms, invent edge-case scenarios, and write the glossary and decisions down the moment they crystallise. Merely *reading* the glossary for vocabulary is a one-line habit any skill can do; this skill is for changing the model, not just consuming it.

## File structure

Use the files the project already has: its glossary (`CONTEXT.md`, `GLOSSARY.md` or a legacy path) and `docs/adr/`. Below, `GLOSSARY.md` stands for that glossary. Never start a parallel documentation system.

Most repos have a single context:

```
/
├── GLOSSARY.md
├── docs/
│   └── adr/
│       ├── 0001-event-sourced-orders.md
│       └── 0002-postgres-for-write-model.md
└── src/
```

If a `GLOSSARY-MAP.md` exists at the root, the repo has multiple contexts. The map points to where each one lives:

```
/
├── GLOSSARY-MAP.md
├── docs/
│   └── adr/                          ← system-wide decisions
├── src/
│   ├── ordering/
│   │   ├── GLOSSARY.md
│   │   └── docs/adr/                 ← context-specific decisions
│   └── billing/
│       ├── GLOSSARY.md
│       └── docs/adr/
```

Create files lazily: only when you have something to write. A new glossary, ADR folder or other policy document needs the user's approval first.

## During the session

### Challenge against the glossary

When the user uses a term that conflicts with the existing language in `GLOSSARY.md`, call it out: "Your glossary defines 'cancellation' as X, but you seem to mean Y. Which is it?" Ask at once when the answer blocks the work; batch the questions that do not.

### Sharpen fuzzy language

When the user uses vague or overloaded terms, propose a precise canonical term. "You're saying 'account': do you mean the Customer or the User? Those are different things."

### Discuss concrete scenarios

When domain relationships are being discussed, stress-test them with specific scenarios. Invent scenarios that probe edge cases and force the user to be precise about the boundaries between concepts.

### Cross-reference with code

When the user states how something works, check whether the code agrees. If you find a contradiction, surface it: "Your code cancels entire Orders, but you just said partial cancellation is possible. Which is right?"

### Record resolved terms as they happen

When a term is resolved, write it down right there; don't batch these up. Inside a workflow task, record every proposed model change (a term, an owner, a boundary or an ADR) in the task's DECISIONS first, then update `GLOSSARY.md` or the ADR in the format in [GLOSSARY-FORMAT.md](./GLOSSARY-FORMAT.md).

`GLOSSARY.md` should be totally devoid of implementation details. Do not treat `GLOSSARY.md` as a spec, a scratch pad, or a repository for implementation decisions. It is a glossary and nothing else.

### Offer ADRs sparingly

Only offer to create an ADR when all three are true:

1. **Hard to reverse**: the cost of changing your mind later is meaningful
2. **Surprising without context**: a future reader will wonder "why did they do it this way?"
3. **The result of a real trade-off**: there were genuine alternatives and you picked one for specific reasons

If any of the three is missing, skip the ADR. Use the format in [ADR-FORMAT.md](./ADR-FORMAT.md).
