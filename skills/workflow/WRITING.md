# Write for the reader; retain the evidence

Applies to questions, chat updates, plans, review findings, HTML, PDFs and completion reports. Assume no prior project or technical knowledge unless the user explicitly asks for a specialist-only format. Be adult, direct and accurate, not childish or padded. Explain the concrete situation and consequence before a technical term. Respect the user's language and requested length.

## Useful order

Start with what the user needs to understand or decide. Explain what happens today, what would change and why it matters. Keep exact names, files, commands, types and caveats available underneath or in a linked evidence section. The main explanation must stand on its own; important exclusions, risks and unanswered questions cannot be hidden as technical detail.

Define a necessary unfamiliar term on first use; otherwise prefer everyday words. Use the same product term consistently. Preserve authoritative terminology and quoted requirements; explain them rather than quietly rewriting their meaning. Reuse approved audience/glossary choices, and ask only when genuinely new meaning is ambiguous. Do not add an introductory lecture to every update.

## Examples (illustrative, not user-provided code)

| Less useful | Clearer |
|---|---|
| “Should the preference persist?” | “Should the app remember this setting after someone closes and reopens it?” |
| “The fixture is regenerated after a GREEN gate.” | “Once Unity's required checks pass, recreate the saved sample data used by the web tests so it matches the controls Unity provides.” Keep the exact command/file beneath it. |
| “Hydration parity is maintained.” | State which screen or saved data remains consistent, and under which condition. Do not invent those facts when the source does not identify them. |
| “Implemented a robust, production-ready solution.” | Name the changed behavior, checks that actually passed and environments not tested. |

A short technical label may remain in a diagram when the visible explanation defines it. Do not fill every node with paths and reference IDs, or substitute a card wall for the approved flowchart. Reports should distinguish observed behavior from a proposal without relying on color alone.

## Remove writing slop

Delete filler, repeated headings, empty template sections and status prose that adds no information. Avoid unexplained abbreviations, invented certainty, unnecessary analogies and duplicate copies of decisions. “No slop” is not itself a review result. Demonstrate the correction: show the unnecessary helper, repeated paragraph or unsupported claim and why it can be removed without losing meaning.

Use the existing authoritative docs. Do not create a new glossary, plan, summary or handoff file solely to make output look comprehensive. Necessary contractual/API wording can be precise and lengthy; brevity must not discard a condition.

## Cold-reader check for consequential deliverables

Before presenting an approval report, substantial plan or final explanation, reread it without relying on the conversation. Can a new reader explain the goal, current/proposed difference, unchanged behavior, important consequences, requested decision and completion checks? Can a technical reader locate supporting evidence?

When available, give a separate reviewer only the artifact and audience, not the conversation; ask for their interpretation and identify mismatches. Otherwise perform and label a self-review. This is not an extra routine approval or proof of usability. Testing with a real nontechnical teammate remains stronger evidence. Record specific corrections in existing findings, not a new writing-audit document for every task.

## Say which time and which state

Use “Baseline before this change” for earlier code, “Approved scope” for agreed work, and a dated current checkpoint for progress. Avoid several unqualified “today” paragraphs. Explain approval, implementation and verification separately: “R3 is approved and coded; the phone appearance still needs acceptance” is clearer than “R3 done.”

Keep a short reason for each changed agreement in the existing revision log; send detailed failed attempts to the existing evidence section. A status update or test retry is not a plan revision. Preserve older reasoning and aliases without asking readers to reconstruct the current state from them.
