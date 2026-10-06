# Reader-focused PDF deliverable

Apply this procedure only when a PDF is requested alongside the development workflow. The existing workflow remains the authoritative development process; this reference adds PDF-specific work and gates. Even an otherwise trivial implementation follows the normal task-folder and approval path when a PDF is requested. The PDF explains the verified situation, consequences, decisions and next steps to its intended reader; it is not a developer handover exported to PDF. Keep the technical relay records for agents in the task folder.

## 1. Establish audience and language before drafting

Read the task instructions and sources. Determine who will read the PDF, what they already know, why they will read it, and what they need to understand or decide. Present the proposed audience, purpose and language to the owner with the terminology map in batch 1. Ask about missing information; do not invent a persona or assume product familiarity.

Create `PDF-BRIEF.md` in the claimed task folder with the audience, purpose, language, scope, evidence sources and terminology map:

| Source term or concept | Verified meaning and source | Proposed reader wording | Immediate everyday explanation, if needed | Owner confirmation |
|---|---|---|---|---|

This is a private working map, not an automatic glossary for the PDF. Include product names, roles, process stages and concepts needed for the reader's understanding. Map internal terms to verified meanings before proposing simpler wording. Preserve distinctions between concepts; an attractive replacement is unacceptable if it changes meaning. Mark disputed or unsupported meanings as unknown and ask the owner to resolve them.

**Gate:** the owner explicitly confirms the intended audience, purpose, document language and every proposed mapping before any PDF prose, captions or diagram labels are written. Approval of the development plan, silence or partial answers do not satisfy this gate. Record the confirmed map version and answer in `PDF-BRIEF.md`. Independent investigation or approved implementation may continue while drafting waits. A newly discovered term or a changed mapping returns to the owner for confirmation before dependent PDF content is drafted.

## 2. Build the evidence record

Create `PDF-EVIDENCE.md` in the task folder. For every substantive claim, capture its source and location, evidence category, scope, date and relevant limitations. Record contradictions and unanswered questions rather than selecting the more convenient account. Clarify conflicts that affect meaning before drafting dependent content.

- **Facts:** verified descriptions or events, attributed to the relevant source.
- **Measurements:** observed numbers with units, time period, population or sample, method and limitations where they affect interpretation. A test result supports only what that test actually checked.
- **Estimates:** visibly labelled estimates with their source, assumptions and range or uncertainty. A calculated value records its inputs and calculation; precision must match the evidence.
- **Unknowns:** say what is unknown and why it matters. State who will resolve it and when only if verified; otherwise leave those details unknown.

Distinguish proposals, decisions and completed outcomes as well. Do not turn an intended benefit into a measured result, an assertion into a verified fact, or a missing measurement into zero. Never invent, silently reinterpret, or strengthen information. Owner terminology approval is evidence of language agreement, not proof of a factual claim.

**Gate:** each planned substantive claim has traceable support or an explicit unknown/estimate label, and meaning-changing source conflicts are resolved or clearly presented as unresolved.

## 3. Write for the reader

Outline the document around the reader's needs: enough context to understand the situation, what it means for them, the relevant decision or outcome, and the next step. Choose section order and length for this purpose; do not copy the development workflow or source-document structure automatically.

For each detail ask: does a reader with no prior knowledge need this to understand the situation, consequence, decision or next step? Include it only if the answer is yes. Provide the missing context inside the document rather than relying on the chat, repository or a glossary. Omit technical evidence that serves only the developer; retain it in the working records.

Use confirmed product language and concrete everyday words. Code identifiers, internal shorthand and developer vocabulary do not enter the PDF merely because they appear in a source, including in headings, quotations, source labels or diagrams. If a technical concept is unavoidable for the reader's purpose, explain it immediately in simple everyday language at first use. Include an exact technical label only when the reader needs it to act or recognize something and the owner has confirmed it in the map.

Write natural sentences with specific actors and actions. Remove filler, exaggerated claims, quirky phrasing, repetitive conclusions and unnecessary restatement. Use concise sentence-case headings, connected paragraphs and short bullets when items are parallel or sequential. Clearly label evidence categories where readers could otherwise confuse them. Separate recommendations from confirmed decisions.

Use brief reader-friendly source notes where useful, with full traceability retained in `PDF-EVIDENCE.md`. Public citations must not leak internal identifiers or unrelated private information. If a source title is opaque, use a meaningful reader label without changing what it supports.

**Gate:** all text follows the confirmed terminology map, every retained detail serves a reader need, and evidence categories and status remain clear.

## 4. Design and render

Create the editable source and PDF inside the task folder using available local PDF tooling. Use an available PDF creation skill for rendering mechanics when helpful, while preserving this brief's audience, wording and design requirements. The skill must also work without a separate PDF skill installed. If no usable renderer exists, report the blocker and ask how to proceed; an unrendered source is not the PDF deliverable.

Design primarily as a readable document: consistent typography, comfortable body type and line spacing, left-aligned text, restrained color, adequate margins and a clear heading hierarchy. Follow verified brand guidance when provided; otherwise use a neutral professional style rather than borrowing unrelated branding. Match page size to the intended use. Keep text selectable/searchable; use page numbers and navigation when document length warrants them.

Use a simple professional flowchart or diagram only when it genuinely makes a sequence, responsibility, handoff or decision easier to understand than prose. Use confirmed reader wording in labels. Keep direction, arrows and branch outcomes clear; do not imply an unsupported sequence, dependency or causation. Explain the diagram in adjacent text. Decorative diagrams, slide-like card grids and dense architecture charts do not replace the document's narrative.

Render every page and inspect the page images at a readable size. Fix clipping, overflow, tiny labels, awkward breaks, stranded headings, table splits, footer overlap and excessive empty space. Let content flow onto another page rather than shrinking type or hiding essential information. Extract PDF text and compare it with the approved source to catch lost or corrupted content.

**Gate:** every page has been visually inspected, the PDF text matches its source, and typography, layout and any diagrams support reading.

## 5. Run three separate validation passes

Record each pass in `PDF-VALIDATION.md`: reviewed file/version, reviewer, evidence inspected, verdict, findings and revisions. Use separate reviewer subagents where available; give each the material appropriate to their role. Explicitly run all three passes even if one reviewer performs more than one. A checklist without document inspection is not a pass.

1. **Accuracy against sources.** Compare every claim, number, label, diagram relationship and stated outcome with `PDF-EVIDENCE.md` and the original sources. Check units, dates, scope, uncertainty, qualifications and conflicts. Pass only when every substantive statement is supported and correctly characterized, with unknowns visible.
2. **Zero-knowledge reader.** Give the reviewer the PDF and confirmed audience/purpose, without implementation notes, private terminology mappings or the conversation. Ask: “Would someone unfamiliar with this product actually understand this?” Have them explain the situation, consequence, decision and next step in their own words and identify every unexplained reference or inferential leap. Pass only when the document itself supplies the context needed for the audience's purpose.
3. **Product language and meaning.** Give a reviewer familiar with the product, or equipped with authoritative product sources, the PDF, confirmed map and relevant product evidence. Check that everyday wording preserves product meanings, roles, distinctions, process order and limitations. Do not pretend an uninformed reviewer has product expertise. If sources cannot resolve a meaning, obtain clarification from the product owner. Pass only when no terminology or meaning issue remains unresolved.

Revise until all three pass. Keep revisions within confirmed language and evidence; changed terms require renewed owner confirmation. After any content revision, run all three passes on the same updated version. After layout changes, rerender and inspect all affected pages, verify extracted text, and recheck any affected validation findings. Record an explicit verdict for each pass against the final version; carry forward a verdict only with evidence that a layout-only revision leaves that pass's conclusions unchanged. Never present an earlier version's pass as approval of the final PDF. Unresolved findings keep the deliverable open.

## 6. Deliver alongside the workflow report

Before batch 2, verify that the final PDF is the version reviewed in all three passes, the owner confirmation of audience, purpose, document language and every terminology mapping is recorded, and visual/text checks are complete. Update the task outcome and PDF TODO items with proof. Include the PDF, editable source, brief, evidence record and validation record in the task's scope and audit; keep working records distinct from the reader deliverable.

Link the final PDF in batch 2, summarize its intended audience and purpose, and report validation results and any verified limitations. Do not mark the task done while required PDF gates remain open. Local creation does not authorize upload or publication. Preserve the workflow's no-commit/no-push boundary.
