---
name: docs-tests
uses: [writing-for-agents, rule-maker, tdd]
fallbacks: [Manual contract check]
approval-exceptions: none
---

# Docs and tests

Change only documentation, agent instructions or tests, and keep them true to the code.

1. **Check the real contract** first: the code, commands and behaviour the text or test describes.
2. **Edit.** Agent instructions follow `writing-for-agents`; tests assert observable behaviour (`tdd`).
3. **Validate:** run the examples and commands the text names, run the tests, and check the documentation structure with `rule-maker`'s docs check. An example that can't run: record Manual contract check.
4. A change with no behaviour anyone can notice is a lightweight edit.

**Done when:** every command and example in the change was run or listed as unchecked, and the tests pass.
