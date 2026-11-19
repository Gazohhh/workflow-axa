---
name: docs-tests
uses: [writing-for-agents, rule-maker, tdd]
fallbacks: [Manual contract check]
approval-exceptions: none
---

# Docs and tests

Change only documentation, agent instructions or tests, and keep them true to the code.

1. **Check the real contract** first: the code, commands and behaviour the text or test describes. When a tool, test, validator or other document reads the text, name those readers (`../../code-review/BLAST-RADIUS.md`).
2. **Edit:** agent instructions follow `writing-for-agents`; human-facing docs get the Unslop check of `../WRITING.md`; tests assert observable behaviour (`tdd`).
3. **Validate:** run each reader named in step 1 (`../../code-review/BLAST-RADIUS.md`), the examples and commands the text names and the tests; check the documentation structure with `rule-maker`'s docs check. An example that can't run: record Manual contract check.
4. **Treat a change with no behaviour anyone can notice** as a lightweight edit.

**Done when:** every command and example in the change was run or listed as unchecked, and the tests pass.
