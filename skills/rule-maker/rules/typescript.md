# TypeScript defaults

Inspect the installed compiler, target, strictness and existing boundary conventions. No compiler/configuration upgrade as a side effect. Use precise types and checked narrowing rather than new broad `any`, unchecked casts or fabricated defaults. A type assertion is not runtime validation. Validate untrusted input at the existing boundary without duplicating the entire application model.

Preserve intentional error and async contracts. Handle relevant promise failures; do not add redundant try/catch or silently swallow errors. Exceptions to defaults require a local reason, not broad suppression. Use the project's current typecheck command and baseline policy; compare introduced diagnostics, not just totals. Do not rewrite unrelated legacy typing.

Do not write nested conditional (ternary) expressions in new or meaningfully changed TypeScript. A single two-way conditional is fine. For more branches, choose what reads best for the actual contract: `if`/`else`, a `switch`, or an existing lookup that already fits. This is a readability rule; it requires no new abstraction or exhaustiveness pattern and is not a reason to rewrite untouched code. Stricter project conventions still apply.

Primary reference: [TypeScript narrowing](https://www.typescriptlang.org/docs/handbook/2/narrowing.html). Check compatibility with the installed compiler before adopting syntax or utilities.

## Related checks

Use [VERSIONS.md](VERSIONS.md) and [data-contracts.md](data-contracts.md). Prefer explicit state/units where they prevent real errors, without requiring branded wrappers for every primitive. Async changes also read [lifetimes.md](lifetimes.md); type assertions never replace runtime boundary validation.
