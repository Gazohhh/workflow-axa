---
name: ui
uses: [ui-design, code-review]
fallbacks: [Existing-reference design, Visual verification pending]
approval-exceptions: none
---

# UI

Change what users see, reusing the project's existing design and checking the result on screen.

1. **Load `ui-design`** before planning. It owns the styling authority, the design kit and the reuse rules.
2. **Find the design source:** a Figma frame, the design kit, or an existing screen to match. No source: record Existing-reference design and name the reference used.
3. **Reuse before adding.** Use existing components, classes and IDs; when nothing matches, ask which existing element to mimic. When you edit a shared component, class, functional ID or text key, name the other screens and code that use it (`../../code-review/BLAST-RADIUS.md`).
4. **Build** the smallest change to markup and behaviour the design needs.
5. **Check** accessibility (keyboard, labels, contrast) and the visual result in the browser or on the device. After a shared edit from step 3, check at least one of them on screen too (ladder step 5 of `../../code-review/BLAST-RADIUS.md`). No way to look: record Visual verification pending.
6. **Review** with `code-review`.

**Done when:** the screen matches its source, accessibility checks pass, and design acceptance is recorded or listed as pending.
