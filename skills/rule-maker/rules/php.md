# PHP defaults

**Load for:** PHP source, runtime/configuration, Composer or PHP verification. Read [VERSIONS.md](VERSIONS.md); Laravel work also loads [laravel.md](laravel.md). No runtime or dependency upgrade is implied.

## Version and contract checks

Inspect the package's PHP requirement, lockfile, extensions, emulated Composer platform and actual relevant runtime. A local CLI executable does not prove the web server or queue worker runs the same PHP. Preserve the project's minimum supported version and deployment constraints.

Type declarations and syntax must be supported by that minimum. Union types require PHP 8.0; enums and intersection types require 8.1; readonly classes require 8.2. These are selected guardrails, not a complete compatibility table. Verify the specific feature in primary documentation. Do not impose a newer syntax just to match an example.

## Required and default practices

Use precise supported types at useful boundaries and preserve intentional nullable/error contracts. Type declarations do not validate external structure, permission or business meaning. Do not introduce blanket casts or `@` suppression that conceal malformed data and failures.

Use the established exceptions/return contracts; do not force every operation into a new result wrapper. Follow the project's `strict_types` policy: adding it can change call behaviour and is not a harmless formatting change. Avoid silently changing public signatures or numeric/string coercion assumptions.

Prefer existing framework/library facilities and cohesive code over a generic repository/service layer without a demonstrated need. Use parameterised database operations and existing escaping/security facilities. Close owned resources and protect transaction/error paths. Review state retained by long-lived workers separately from request-local state.

## Verification

Use the project's actual lint, static analysis and test commands compatible with its PHP version; do not install a formatter/analyzer automatically. Include boundary/error cases and the relevant runtime/extension coverage. Establish compatibility for the supported minimum, not merely the newest local interpreter. Preserve existing project baselines and generated files.

Sources: [PHP type declarations](https://www.php.net/manual/en/language.types.declarations.php), [enumerations](https://www.php.net/manual/en/language.enumerations.php), [readonly classes](https://www.php.net/manual/en/language.oop5.basic.php#language.oop5.basic.class.readonly), [Composer platform configuration](https://getcomposer.org/doc/06-config.md#platform). No vendor directory is executed by rule inspection.
