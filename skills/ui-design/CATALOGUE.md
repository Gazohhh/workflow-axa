# Optional JSON catalogue profile (schema 1)

Use only when the owner chooses it. An existing Markdown, Storybook or project catalogue does not require conversion. No catalogue is created by the checker. This is a reference contract, not a component implementation or visual theme.

Top-level fields: `schema_version` (integer 1), `kit_id`, `revision`, `status` (`draft`, `approved`, `deprecated`), `scope` (nonempty repository-relative directories), `approval` (reference or null), `preview` (reference or null), `items` (up to 256). An approved kit needs both references. The preview reference points to the existing written access/release boundary; it does not prove route isolation.

Each item: `id`, `kind` (`component`, `pattern`, `tokens`), `name`, `purpose`, `status` (`candidate`, `approved`, `deprecated`), `scope`, `sources` (up to 32 local references), `approval` (reference or null), `variants`, `states`, `uses` (IDs of other entries). Approved entries need at least one source and their own approval reference. Their sources should cover the actual implementation and its relevant styles/tokens/contracts. A top-level approval does not automatically approve a newly added entry.

A reference has exactly `path` (repository-relative, forward slashes, no traversal/URLs) and `sha256` (64 lowercase hex digits). Both the source and approval record are fingerprinted. A hash detects byte changes; it does not prove the record actually grants the stated permission. The caller must inspect that decision. External design references can be documented in the existing local decision; the checker never fetches a URL.

Example shape for an established entry (illustrative placeholders, **not** an approval):

```json
{
  "id": "save-button",
  "kind": "component",
  "name": "Existing save button",
  "purpose": "Submit the settings form through the approved component API",
  "status": "candidate",
  "scope": ["src/settings"],
  "sources": [],
  "approval": null,
  "variants": [],
  "states": [],
  "uses": []
}
```

Do not pretend these placeholders identify actual project components. Hash and reference real sources only after inspection. `uses` records component/pattern/token relationships, not arbitrary runtime flow. Unknown IDs and cycles are invalid. Selection includes transitive dependencies. With `--scope`, the requested directory must be covered by the kit and each selected dependency's declared scope; widening scope is an approval decision. Paths are literal directories, not glob patterns.

Result meanings: `DRAFT` means selected coverage lacks current approval; `BLOCKED` means invalid, stale, inaccessible, out-of-scope or deprecated required inputs; `REVIEW_REQUIRED` means structural references match but semantic/approval/runtime review is still needed. **There is no automatic READY or APPROVED result.** Exit 0 means structurally current references require review; 1 means draft/incomplete approval; 2 means blocked/invalid. JSON input is bounded, duplicate keys and unknown fields are rejected, symlinks/junctions are not followed, no output files or network are used.

The checker hashes only listed, selected inputs. It cannot discover every transitive stylesheet, theme, ancestor layout, remote asset or dynamic dependency. Selecting one item intentionally does not invalidate it for an unrelated stale item, but common dependencies and kit-level authority must still match. Runtime checks, design acceptance and the workflow's implementation approval remain separate.
