# Design decisions and sources

## 2.1.0 — grounded understanding and visual approval

The user's approved change adds current-code evidence before proposals and a visible check of understanding after PLAN/TODO preparation, before implementation. Structured decisions stay with grilling; the final review and approval are separate. One workflow entry point invokes a separately useful codebase-map skill. Plain requests need a verified host-loaded routing rule, not merely a plugin installed somewhere on disk.

PLAN/TODO/FINDINGS/DECISIONS remain authoritative; the JSON/HTML projection is revisioned and evidence-linked. The renderer is original Python-standard-library code with inline SVG/CSS and a small local viewer. It borrows the visual-report concept, not upstream text, code, dependencies or the architecture-improvement workflow. The source-fingerprint checker detects changes only to named supplied bytes. Neither it nor Markdown enforces model understanding, identity or permissions.

The renderer was kept dependency-free and intentionally is not a full editable whiteboard. Host policy and model behavior need live integration tests. A file-opening request does not prove display, and no HTML controls approve or execute work.

Primary sources actually checked for this update (2026-10-13):

| Source | Specific relevance |
|---|---|
| [Claude skills](https://code.claude.com/docs/en/skills) | Skill discovery, explicit/implicit use and conditional body loading; support-file instructions. |
| [Claude project instructions](https://code.claude.com/docs/en/memory) | Applicable persistent project rules for ordinary prompts. |
| [Claude plugin manifest](https://code.claude.com/docs/en/plugins-reference) | Register the two local skill directories. |
| [OpenAI skills](https://developers.openai.com/codex/skills/) | Current skill activation and local packaging guidance. |
| [OpenAI AGENTS guidance](https://developers.openai.com/codex/guides/agents-md/) | Host-loaded repository instructions and scope. |
| [Matt's architecture command](https://github.com/mattpocock/skills/blob/main/skills/engineering/improve-codebase-architecture/SKILL.md) | Visual candidates followed by questions; do not chain its refactor process for inspection maps. |
| [Matt's HTML reference](https://github.com/mattpocock/skills/blob/main/skills/engineering/improve-codebase-architecture/HTML-REPORT.md) | Visual before/after concept; CDN and loose-rendering choices are not inherited. |

This update did not re-audit or execute all upstream skills. The 2.0.0 specialist inventory retains its historical provenance. Package test counts and browser limits belong in [VALIDATION.md](../VALIDATION.md), not implied claims of live agent reliability.

## Historical 2.0.0 design and source notes


## Scope

This rebuild applies the user's approval of the supplied workflow review. It retains one entrypoint and task-scoped documentation, while changing conflicting approval, questions, delegation, staging and recovery defaults. The historical review reported reading Matt Pocock's 27 catalogue entrypoints. The
2.0.0 integration rechecked the 11 routed model-invocable entrypoints, relevant wrappers/setup,
selected manual workflows, and skill mechanics. This is source review, not a claim of
executing all 27 skills.

The policy is tailored to this team, not asserted to be a universally best or guaranteed production workflow. In 2.0.0, the applicable Matt Pocock specialists are explicit runtime dependencies,
installed separately, not merely inspiration. Other comparative sources remain design
references. No upstream skill stack is copied into the package.

## Why this shape

The main file keeps the ordered process and authority boundaries. Record templates, nuanced questions, audit criteria and PDF mechanics live behind explicit conditional pointers. This reduces core size without hiding the rules that every implementation needs.

Approval distinguishes user-owned decisions from ordinary execution of a settled approach. A short checkpoint is written before and after meaningful work units; it does not wait for a graceful shutdown. Recovery reconciles records with real files and approval. Cleanup targets obsolete parts of the approved change, not an opportunistic repository refactor.

The workflow removes automatic staging rather than attempting to infer ownership from filenames. It retains optional PDF review while allowing traceable reuse of applicable language approval. Real independent review is preferred; unsupported host capabilities are disclosed instead of simulated.

The core's 1,200-word maintenance check is a local review budget, not a model context limit or evidence of reliability. Structural tests and live behavioral evaluations serve different purposes. Missing real before/after examples from the user are not fabricated; current maintainability examples are explicitly illustrative.

## Primary sources checked on 9 October 2026

| Source | Relevant use and boundary |
|---|---|
| [Anthropic skill authoring](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) | Concise main instructions and conditional references; a size guideline does not prove reliability. |
| [Agent Skills specification](https://agentskills.io/specification) | Directory/entrypoint conventions and basic metadata. |
| [OpenAI skill guidance](https://developers.openai.com/codex/skills/) | Codex local discovery, invocation and optional display metadata. |
| [OpenAI skill evaluation](https://developers.openai.com/blog/eval-skills) | Evaluate observable outcomes and targeted regressions rather than only formatting. |
| [Claude plugin creation](https://code.claude.com/docs/en/plugins/create) | Local session loading, namespaced invocation and host validation. |
| [Claude plugin evals](https://code.claude.com/docs/en/plugin-evals) | Native evaluations, account usage and keeping reports local; native and skill-creator formats differ. |
| [Matt Pocock: writing-for-agents](https://github.com/mattpocock/skills/blob/main/skills/productivity/writing-for-agents/SKILL.md) | Clear ordered steps, explicit reference triggers and removing duplicated instructions. |
| [Matt Pocock: grilling](https://github.com/mattpocock/skills/blob/main/skills/productivity/grilling/SKILL.md) | Separate fact-finding from user decisions; group questions whose prerequisites are settled. |
| [Matt Pocock: codebase-design](https://github.com/mattpocock/skills/blob/main/skills/engineering/codebase-design/SKILL.md) | Evaluate whether an abstraction genuinely removes complexity for its callers. |
| [Anthropic skill-creator](https://github.com/anthropics/skills/blob/main/skills/skill-creator/SKILL.md) | Compare an existing skill against a candidate with realistic tasks and reviewed outputs. |
| [Superpowers verification-before-completion](https://github.com/obra/superpowers/blob/main/skills/verification-before-completion/SKILL.md) | Require observed verification for completion claims. |

Installation and CLI behavior can change. Consult installed help and official documentation when a command is unsupported. This ZIP neither configures host permissions nor grants access to external services. The actual checks and unrun host tests are recorded in [VALIDATION.md](../VALIDATION.md).


## 2.0.0 specialist integration

[SPECIALISTS.md](../skills/workflow/SPECIALISTS.md) is the one integration reference:
triggers, exact responsibilities, explicit adapters and exceptions. [SETUP.md](../skills/workflow/SETUP.md)
is loaded for setup/change checks. [specialists.json](../skills/workflow/specialists.json)
is a catalogue, not a native auto-install declaration or an invented immutable upstream lock.

The upstream plugin manifest was observed as 1.3.1 through public web retrieval. Its
source commit and byte-identical archive were not retrievable here. Instead, the checker
fingerprints a team's actual local installation and compares an explicitly approved
inventory. Name matches and disk presence do not establish source authenticity or host
availability. Existing installations may need a compatibility review before this workflow
can use them; 2.0.0 is not a claim that upstream 1.3.1 has passed live integration tests.

The checker is deterministic filesystem work that benefits from a small script. It never
installs, executes a supporting script, enables a plugin, changes a baseline or calls a
network service. Host discovery and actual invocation remain the agent's responsibility.

Additional primary sources reviewed on 9 October 2026:
- [Matt's manifest](https://github.com/mattpocock/skills/blob/main/.claude-plugin/plugin.json) and [installation guide](https://github.com/mattpocock/skills#installation-30-second-setup).
- [Reusable grilling](https://github.com/mattpocock/skills/blob/main/skills/productivity/grilling/SKILL.md) and [grill-me wrapper](https://github.com/mattpocock/skills/blob/main/skills/productivity/grill-me/SKILL.md).
- [Code review](https://github.com/mattpocock/skills/blob/main/skills/engineering/code-review/SKILL.md), [TDD](https://github.com/mattpocock/skills/blob/main/skills/engineering/tdd/SKILL.md), [research](https://github.com/mattpocock/skills/blob/main/skills/engineering/research/SKILL.md), and [diagnosing bugs](https://github.com/mattpocock/skills/blob/main/skills/engineering/diagnosing-bugs/SKILL.md).
- [Domain modeling](https://github.com/mattpocock/skills/blob/main/skills/engineering/domain-modeling/SKILL.md), [prototype](https://github.com/mattpocock/skills/blob/main/skills/engineering/prototype/SKILL.md), [PR writing](https://github.com/mattpocock/skills/blob/main/skills/engineering/pr/SKILL.md), and [wizard](https://github.com/mattpocock/skills/blob/main/skills/engineering/wizard/SKILL.md).
- [Skill mechanics](https://github.com/mattpocock/skills/blob/main/skills/productivity/writing-for-agents/SKILL-MECHANICS.md), [Claude skill invocation](https://code.claude.com/docs/en/skills), and [Claude installation management](https://code.claude.com/docs/en/discover-plugins).


## 2.2.0 — approved flowchart design integration

The owner rejected the first wireflow/card sample and approved the second diagram-design flowchart. The requirement is a real flowchart first, not just a simplified report. Actual source-derived feature behavior is separate from delivery order and structural containment; all needed evidence remains in the same records.

The local workflow still owns context, grilling, plan/task mapping, handoff, cleanup and approval. The local codebase-map now invokes the separate diagram-design specialist for editorial geometry. It packages that design through a deterministic schema-2 renderer, rather than treating renderer output as a specialist invocation. Only diagram-design is added to the catalogue; Matt’s historical entries are not silently upgraded.

Sources reviewed 2026-10-14: https://github.com/cathrynlavery/diagram-design/tree/main/skills/diagram-design , especially SKILL.md, flowchart conventions and style guide. Web review returned skill metadata 2.6. Container DNS prevented a local checkout; no upstream scripts were executed, no upstream license/font assets are bundled, and no immutable revision is asserted. The palette/treatments are referenced from the owner-approved sample, not a claim of brand-font fidelity.

Schema 2 intentionally replaces fixed grid positions and cubic automatic routing. It validates explicit orthogonal geometry, text budgets, focal limits and source/task relationships; browser inspection is still needed for actual type metrics, and semantic source fidelity is an agent/human responsibility. Reports from 2.1 remain unchanged and checkable; silent topology conversion is prohibited.

The approved style is reused without repeat onboarding. No network fonts, brand-site fetching, global profile writes or upstream installs are authorized by preparing a preview. No visual control approves or starts the application change. Existing uncertainties are not resolved by a restyle.
