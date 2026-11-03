# Vendored skills

Eight skills in this package are copies of Matt Pocock's skills: `grilling`, `tdd`, `code-review`, `writing-for-agents`, `codebase-design`, `domain-modeling`, `implement-spec`, `retro`. They are separate skills like the others (plugin names `workflow-axa:<name>`). The workflow phases load them from their sibling folders, so an upstream change, a removed skill or a same-named skill installed elsewhere can't change the workflow. Each `SKILL.md` keeps the upstream text and ends with a **workflow-axa adaptation** section that overrides it where they conflict; supporting files are unchanged upstream copies.

Source: [mattpocock/skills](https://github.com/mattpocock/skills) at commit `4ae2317ddb22b046e26455e4f9c9b3aaaf62212d`, MIT license; each skill folder carries its own `LICENSE` copy. Keep it with the files.

| Skill | Upstream file | SHA-256 (first 16) of the upstream file | SHA-256 (first 16) of the unchanged upstream text inside our SKILL.md |
|---|---|---|---|
| grilling | `skills/productivity/grilling/SKILL.md` | `a146842ed93ca43d` | `e859b47f7da81db8` |
| tdd | `skills/engineering/tdd/SKILL.md` | `5505d25bbaa8fc14` | `eb5d2c89ebc29d4a` |
| tdd | `skills/engineering/tdd/tests.md` | `859f9e592c188fda` | — |
| tdd | `skills/engineering/tdd/mocking.md` | `3ceb807fdf4a47d6` | — |
| code-review | `skills/engineering/code-review/SKILL.md` | `9c921a8d88138a41` | `e1b0ac9a379ee322` |
| writing-for-agents | `skills/productivity/writing-for-agents/SKILL.md` | `551adca942227b44` | `20e3b1bbcf8eec73` |
| writing-for-agents | `skills/productivity/writing-for-agents/SKILL-MECHANICS.md` | `c768e6307c7c1072` | — |
| codebase-design | `skills/engineering/codebase-design/SKILL.md` | `2c20617f87ec8af6` | `9153e20f10ff70df` |
| codebase-design | `skills/engineering/codebase-design/DEEPENING.md` | `f3dd099ce99289bd` | — |
| codebase-design | `skills/engineering/codebase-design/DESIGN-IT-TWICE.md` | `c222ab5a82e04056` | — |
| domain-modeling | `skills/engineering/domain-modeling/SKILL.md` | `7b925d7b1e341a2e` | `89fe9ba785772fcc` |
| domain-modeling | `skills/engineering/domain-modeling/GLOSSARY-FORMAT.md` | `21dcc40cdec8e151` | — |
| domain-modeling | `skills/engineering/domain-modeling/ADR-FORMAT.md` | `944c92aa790e8fbd` | — |
| implement-spec | `skills/engineering/implement-spec/SKILL.md` | `1993a473cec40ac8` | `23d568158abaf933` |
| retro | `skills/engineering/retro/SKILL.md` | `33fbc28568e3146f` | `1e95a44a76bc43bf` |

## Updating from upstream

1. Fetch the new upstream files into a scratch folder outside the package.
2. Compare each file's SHA-256 with the table. Unchanged: nothing to do.
3. For a changed file, read the upstream diff and decide with the maintainer whether to take it. Re-check each adaptation section.
4. Regenerate with `python -X utf8 -I tools/vendor_specialists.py <upstream-root> .`, update the commit, then run `tools/validate.py` and the tests.

Never take an upstream change unread: these files steer the agent.

## Simple English

`simple-english` is a copy of [AminBlg/SimpleEnglish](https://github.com/AminBlg/SimpleEnglish) `skills/simple-english/` (version 2.1.1) at commit `a6fcb4fde098b33617cc1578d151ebf58774b883`, MIT license (`skills/simple-english/LICENSE`). Only the skill folder is copied, with LF line endings (hashes are of the LF text); the upstream hooks, scripts and evals are not. The workflow uses it for every HTML report and delivery message (owner request, 2026-11-03). Its `SKILL.md` keeps the upstream text and ends with a **workflow-axa adaptation** section.

| File | SHA-256 (first 16) of the upstream file | SHA-256 (first 16) of the unchanged upstream text inside our SKILL.md |
|---|---|---|
| `skills/simple-english/SKILL.md` | `2f25072b7edd707d` | `893cb2f4e0800343` |
| `skills/simple-english/references/rule-catalog.md` | `49175a0614ffe23f` | — |
| `skills/simple-english/references/strict-vocabulary.md` | `3f34ef3a878d9dc8` | — |
| `skills/simple-english/references/use-cases.md` | `ac0e7129107693a4` | — |
| `skills/simple-english/references/word-swaps.md` | `4a0056cbc9e5faf2` | — |

To update: fetch the upstream skill folder into a scratch folder, compare hashes, read the diff, copy the changed files, keep the adaptation section, update this table, then run the validator and tests.
