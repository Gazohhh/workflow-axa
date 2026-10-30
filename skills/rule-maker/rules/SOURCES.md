# Sources and limits

Reviewed 2026-10-29. These primary sources inform loading/verification boundaries; they are not required web fetches on every task. Check current host versions/help before configuring host-specific integrations.

- [Claude memory/instructions](https://code.claude.com/docs/en/memory): global/project context, imports, scoped loading, conflicts and lack of guaranteed compliance.
- [Claude hooks](https://code.claude.com/docs/en/hooks): host lifecycle and action-specific behaviour; configuration and tested runtime results are different evidence.
- [Codex instruction discovery](https://developers.openai.com/codex/guides/agents-md): global/profile overrides, directory discovery and context limits.
- [Codex hooks](https://developers.openai.com/codex/hooks): trust and event-specific behaviour. No hook is installed by this package's rules activation.
- [Agent Skills specification](https://agentskills.io/specification): conditional references versus automatically loaded instruction text.
- [Matt's codebase-design](https://github.com/mattpocock/skills/blob/main/skills/engineering/codebase-design/SKILL.md): retained external discipline for scoped design review. Existing workflow adapter still controls scope, approvals and terminology compatibility.

This release implements a documented readiness gate, a declared-assessment checker and global reference activation. It does not install a tool-call firewall, validate every shell/MCP effect, authenticate an agent-written approval record, update other machines automatically, or prove live model obedience. Gate/checker PASS is not a security certification. Unknown action semantics or incomplete prerequisites stop affected work under the policy; host permissions remain the actual boundary.

## Engineering expansion — reviewed 2026-10-30

These are source leads for our locally written rules, not files fetched at runtime, vendor endorsement, or a complete copy of any company's policies. Consult matching documentation for a version-specific operation. No rule library proves defect-free code. Sources may move; local guidance remains usable offline with stated limits.

| Local guidance | Primary sources and adaptation |
|---|---|
| Core, data, actual Rust | [Google Rust guide](https://google.github.io/styleguide/rustguide.html), [Rust API type safety](https://rust-lang.github.io/api-guidelines/type-safety.html). Use meaningful contracts; do not export Chromium-only async/thread bans to unrelated projects. |
| Review and tests | [Google code review](https://google.github.io/eng-practices/review/reviewer/looking-for.html), [Microsoft agent-oriented Rust advice](https://microsoft.github.io/rust-guidelines/guidelines/ai/index.html). Preserve necessary safety/API docs; do not force arbitrary short-function/comment quotas. |
| Lifetimes/React | [React effects](https://react.dev/reference/react/useEffect), [Hooks](https://react.dev/reference/rules/rules-of-hooks), [versions](https://react.dev/versions), [Three disposal](https://threejs.org/manual/pages/how-to-dispose-of-objects.html). Common principles do not replace installed-version contracts. |
| Reliability | [Amazon retries](https://aws.amazon.com/builders-library/timeouts-retries-and-backoff-with-jitter/). Applied to bounded repeatable work; not a global retry framework. |
| Security | [OWASP input validation](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html), [authorisation](https://cheatsheetseries.owasp.org/cheatsheets/Authorization_Cheat_Sheet.html), [logging](https://cheatsheetseries.owasp.org/cheatsheets/Logging_Cheat_Sheet.html). Focused boundaries/checks, not full audit certification. |
| Performance | [Microsoft hot paths](https://microsoft.github.io/rust-guidelines/guidelines/performance/index.html), [Unity bottlenecks](https://docs.unity3d.com/6000.0/Documentation/Manual/OptimizingGraphicsPerformance.html), [Pixi tradeoffs](https://pixijs.com/8.x/guides/concepts/performance-tips). Preserve workload/quality and target environment; throughput advice is not universally the goal. |
| Compatibility | [Amazon rollback safety](https://aws.amazon.com/builders-library/ensuring-rollback-safety-during-deployments/). Review supported transitions; no automatic deployment/migration or eternal compatibility wrappers. |
| PHP | [Types](https://www.php.net/manual/en/language.types.declarations.php), [enums](https://www.php.net/manual/en/language.enumerations.php), [readonly classes](https://www.php.net/manual/en/language.oop5.basic.php#language.oop5.basic.class.readonly). Verify each feature against the supported runtime; selected examples are not a full version matrix. |
| Laravel | [11 upgrade](https://laravel.com/docs/11.x/upgrade), [12 relationships](https://laravel.com/docs/12.x/eloquent-relationships), [queues](https://laravel.com/docs/12.x/queues), [authorisation](https://laravel.com/docs/12.x/authorization), [configuration](https://laravel.com/docs/12.x/configuration). Preserve upgraded legacy structure; future versions require fresh verification. |
| Static version tooling | [Composer usage](https://getcomposer.org/doc/01-basic-usage.md), [platform emulation](https://getcomposer.org/doc/06-config.md#platform), [Composer lock schema](https://raw.githubusercontent.com/composer/composer/main/res/composer-lock-schema.json), [npm lock format](https://docs.npmjs.com/cli/v11/configuring-npm/package-lock-json), [Cargo manifest](https://doc.rust-lang.org/cargo/reference/manifest.html). Static facts are not installed/runtime evidence or dependency solving. |

The general AI-rule prompt supplied by the owner asked for inspection, stack-specific official guidance, and adaptation of Google/Rust principles without blindly transplanting their syntax. This release implements that authorised direction; it does not execute the old prompt's broad repository audit or compulsory twenty-worker policy.
