# Laravel defaults

**Load for:** a verified Laravel application or the relevant Illuminate packages. Also read [php.md](php.md), [VERSIONS.md](VERSIONS.md) and the engineering modules selected by the task. Standalone Illuminate components do not establish a full Laravel application.

## Version and application structure

Read composer.json and the corresponding composer.lock; identify laravel/framework and related packages, supported PHP/extensions, and the actual bootstrap/middleware/provider layout. A requirement range is not a resolved version; a resolved dependency is not a running installation.

**Laravel 10/11 transition:** 11 requires PHP 8.2, but upgraded applications may retain the older application structure. Do not move middleware/providers into a new skeleton just because the dependency is 11 or later. Newer APIs, builder helpers and defaults require matching documentation. Laravel 12 examples are not a guarantee for 10, and an unfamiliar later version needs source verification rather than extrapolation. No automatic migration or upgrade.

## Keep framework use deliberate

- Validate request data and separately authorise the actor/resource using the established policy/gate/request conventions. Do not treat authentication or a validated ID as sufficient access control. Preserve mass-assignment, tenant boundaries and server-side protections.
- Use existing query facilities safely. Identify N+1 queries and unnecessary result loading on affected paths; load the relationships actually needed. Do not eager-load everything or change global lazy-loading policy without approval. Test meaningful query budgets with realistic fixture sizes where relevant.
- Keep business behaviour with its existing owner. A controller need not gain repository/service/DTO layers solely to follow a pattern. Reuse intentional boundaries and project error/response contracts.
- Review transaction boundaries, job dispatch timing and duplicate delivery. Jobs/retries must preserve the agreed repeat-execution behaviour. An after-commit hook or uniqueness option is version/configuration-dependent and does not prove every external effect is atomic.
- Respect configuration caching and established env/config access. Do not expose secrets in errors, logs or artifacts. Long-running workers must not retain another request/tenant's state.
- Treat schema changes and mixed deployments as compatibility work. Never run migrations or reset a real database as an incidental test step.

## Verification

Select the actual PHPUnit/Pest/framework test runner, relevant feature/unit/database checks and supported environment. Include denied access, validation failures and relevant queue/transaction/error behaviour. Use disposable test data; a fake alone may not establish the integration being changed. No new packages, live jobs or production writes merely to validate rules.

Sources: [11 upgrade/structure](https://laravel.com/docs/11.x/upgrade), [12 relationships](https://laravel.com/docs/12.x/eloquent-relationships), [queues](https://laravel.com/docs/12.x/queues), [authorisation](https://laravel.com/docs/12.x/authorization), [configuration](https://laravel.com/docs/12.x/configuration). Open the matching version before relying on API-specific advice.
