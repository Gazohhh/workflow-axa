# Credits and licenses

Some skills in this package started as copies of other MIT-licensed projects. Since 2.8.0-rc.37 they are this package's own text: they are maintained here and no longer follow their sources. Each keeps its `LICENSE` file at the place the table names; keep it when you edit or move the text. Since 2.9.0, `implement-spec` and `retro` are archived (not shipped) and `simple-english` is reference text inside the `workflow` skill.

| Skills | Source | License |
|---|---|---|
| `grilling`, `tdd`, `code-review`, `writing-for-agents`, `codebase-design`, `domain-modeling` | [mattpocock/skills](https://github.com/mattpocock/skills) by Matt Pocock, last copied at commit `4ae2317ddb22b046e26455e4f9c9b3aaaf62212d` | MIT, `skills/<name>/LICENSE` |
| `implement-spec`, `retro` (archived) | [mattpocock/skills](https://github.com/mattpocock/skills) by Matt Pocock, last copied at commit `4ae2317ddb22b046e26455e4f9c9b3aaaf62212d` | MIT, `docs/archive/skills/<name>/LICENSE` |
| `simple-english` (reference text `skills/workflow/SIMPLE-ENGLISH.md`; its plain-writing rules are now in `skills/workflow/WRITING.md`) | [AminBlg/SimpleEnglish](https://github.com/AminBlg/SimpleEnglish), `skills/simple-english/` version 2.1.1, last copied at commit `a6fcb4fde098b33617cc1578d151ebf58774b883` | MIT, `skills/workflow/SIMPLE-ENGLISH.LICENSE` and `docs/archive/skills/simple-english/LICENSE` |
| `verify-app`, `reproduce-bug` | [cursor/plugins](https://github.com/cursor/plugins) pstack by Lauren Tan: `pstack/skills/create-verification-skill` and `pstack/skills/maintain-verification-skill` adapted into `verify-app`; `pstack/automations/benny/skills/reproduce-and-fix-issues` with its references `control-adapter.md`, `feature-map.example.md` and `verify-existing-fix.md` adapted into `reproduce-bug` without its fix step; copied at commit `35a90942a7f02e1ebbc2443643179815f2147954` | MIT, `skills/verify-app/LICENSE` and `skills/reproduce-bug/LICENSE` |
| `code-review` and `simple-english`: the blast-radius method in skills/code-review/BLAST-RADIUS.md and the Unslop tells in skills/workflow/WRITING.md | [cursor/plugins](https://github.com/cursor/plugins) pstack by Lauren Tan: `pstack/skills/blast-radius` adapted at commit `bf0c7cd80abdbf7fe47b634978a7d1b4071f71a7`, `pstack/skills/unslop` adapted at commit `2f87c854fe3e2fcda44ca86b46ede35aad3c46b7` | MIT, `skills/code-review/BLAST-RADIUS.LICENSE` and `skills/workflow/UNSLOP.LICENSE` |

The flowchart style in `skills/codebase-map/FLOWCHART-DESIGN.md` was inspired by Cathryn Lavery's [diagram-design](https://github.com/cathrynlavery/diagram-design) skill. No file, script or font was copied from it, so no license applies.

The rest of the package is MIT licensed ([LICENSE](LICENSE)).
