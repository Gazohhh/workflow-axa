---
name: docs-tests
uses: [writing-for-agents, rule-maker, tdd]
fallbacks: [Manual contract check]
approval-exceptions: none
---

# Docs and tests

Change only documentation, agent instructions or tests, and keep them true to the code.

1. **Check the real contract** first: the code, commands and behaviour the text or test describes. When a tool, test, validator or other document reads the text, name those readers (`../../code-review/BLAST-RADIUS.md`).
2. **Edit.** Agent instructions follow `writing-for-agents`. Human-facing docs get the Unslop check of `../WRITING.md`. Tests assert observable behaviour (`tdd`).
3. **Validate:** run each reader named in step 1 (`../../code-review/BLAST-RADIUS.md`), run the examples and commands the text names, run the tests, and check the documentation structure with `rule-maker`'s docs check. An example that can't run: record Manual contract check.
4. A change with no behaviour anyone can notice is a lightweight edit.

**Done when:** every command and example in the change was run or listed as unchecked, and the tests pass.
