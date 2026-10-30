# Data and error contracts

**Applies to:** states, identifiers, units, parsing, persistence and public/internal boundaries. Preserve approved contracts and installed-language capabilities.

## Required

- Make mutually exclusive states distinguishable. Do not allow invalid combinations accidentally; independent choices remain independent. Use the simplest compatible representation, not a custom type for every primitive.
- Keep units and identities explicit at conversions and interfaces. A display-formatted amount is not an authoritative stored amount. Honour the project's precision, currency, rounding and timestamp contracts; never invent a global money representation.
- Validate the structure and meaning of untrusted data at its boundary. A type assertion, successful parse or well-formed identifier is not authorisation. Trusted internal values need not be repeatedly sanitised everywhere.
- Specify intentional conversion. Reject or surface invalid input according to the existing error contract rather than silently replacing it with zero, an empty object or the first available entity. A fallback is valid only when the requirement defines it.
- Preserve absence, expected failure, cancellation and defects as meaningful distinctions. Add useful, non-sensitive context when propagating failures. Do not mandate exceptions or result objects across every language.

## Defaults and examples

Prefer one authoritative state over independently maintained derived copies. For a mutually exclusive loading flow, `loading | ready(data) | failed(error)` is clearer than three unrelated flags. A screen that keeps old data while refreshing needs a model for that legitimate combination instead; an on/off setting can remain a boolean.

Prefer meaningful names/types at confusion-prone boundaries: `durationMs` is different from `durationSeconds`. Avoid wholesale renaming or introducing a large validation layer when an existing boundary already owns the contract.

## Verification

Test relevant invalid/missing/zero/boundary values, transitions and conversion rules. Check whether malformed external data can reach trusted operations. Verify that an error still preserves its intended meaning and callers handle it. Expected values come from the requirement or independently established examples, not from calling the production conversion again.

Sources: [Rust API type safety](https://rust-lang.github.io/api-guidelines/type-safety.html), [Google Rust errors/API context](https://google.github.io/styleguide/rustguide.html), [OWASP input validation](https://cheatsheetseries.owasp.org/cheatsheets/Input_Validation_Cheat_Sheet.html). These are adapted engineering principles, not a requirement to adopt Rust types in every stack.
