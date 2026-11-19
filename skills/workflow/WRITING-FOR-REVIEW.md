# Writing what the owner reviews

Read this before you write a report's JSON or render it, and before you present a plan report, a substantial plan or a final report (the delivery chat report included). [WRITING.md](WRITING.md) owns the rules this file applies; read it first.

## Report prose fields

A report is a document: apply the rules of WRITING.md "Documents and reports" to every prose field of the report JSON (the understanding line, section texts, ticket specifications and expected results, acceptance notes, check expectations, results and limits, decision summaries, risks), and run the self-check on that text before rendering.

The report renderer checks every report before writing. It prints `PLAIN ENGLISH:` problems and `PLAIN ENGLISH NOTE:` lines for modals, skipping quoted text. Problems never block it; `--open` waits. Until the user sees the report, re-render into the same file with `--replace-unpresented`.

## Cold-reader check

Before presenting a plan report, a substantial plan or a final report, reread it as someone who missed the conversation. Can they explain the goal, what changes, what stays the same, the decision asked of them and how completion is checked? Can a developer find the evidence? Check each claim against it: "the full suite passes" names any failures it already had; "every finding is fixed" counts the open ones; "what works now" lists only what a check showed.

When you can, give an independent reviewer only the document and its audience, ask them to restate those five things, and compare part by part with WRITING.md "Keep the meaning". Each mismatch is a writing defect. Without a reviewer, write the restatement yourself before rereading the records, and say it was a self-check.
