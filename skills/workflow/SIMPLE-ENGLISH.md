<!-- Reference text, formerly the simple-english skill (unregistered in 2.9.0); licence: SIMPLE-ENGLISH.LICENSE, credits: VENDORED-SKILLS.md. -->

# Simple English

The common writing rules (documents and reports, chat replies, the self-check and the Unslop tells) live in [WRITING.md](WRITING.md). This file keeps only what Strict mode and CHECK requests need.

## Modes

Plain is the default: WRITING.md's rules. Reports and workflow messages use Plain only. Strict applies when the user names STE, ASD-STE100, or compliance: read `simple-english/strict-vocabulary.md` before you draft the document, and say once that no tool guarantees compliance. The reply stays Plain in every mode.

When asked to CHECK text instead of writing it, first open `simple-english/rule-catalog.md`. Then report each violation as: rule number quoted from that file, the offending text, a compliant rewrite. Never cite a rule number from memory. In Plain mode, judge a modal hit against WRITING.md's document rule 5, not the catalog's ban, and report the catalog's contraction rule (4.2) and its Word Choice swaps as suggestions, not violations; Strict mode keeps them as rules. When the user asked for compliance, end with one sentence: no tool can guarantee ASD-STE100 compliance, and the standard is a free download at asd-ste100.org.

For an error message, a runbook, an incident report, release notes, a commit message, or UI copy, `simple-english/use-cases.md` names the mode and the pattern for each.

## References

- `simple-english/rule-catalog.md`: the 53 rules of Issue 9 with software examples, for CHECK mode
- `simple-english/strict-vocabulary.md`: the dictionary discipline for Strict mode
- `simple-english/word-swaps.md`: a map from overused words to plain ones
- `simple-english/use-cases.md`: the mode and the pattern for error messages, runbooks, incident reports, release notes, commits, agent prompts, UI copy, and translation prep
