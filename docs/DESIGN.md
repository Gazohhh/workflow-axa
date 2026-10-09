# Design decisions and sources

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
