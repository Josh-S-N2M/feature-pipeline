---
id: RN-T-002
topic_id: T-002
topic_name: UX design + accessibility-as-flow
maps_to_ac: AC-FR-1-b
generated: 2026-05-20T23:10:00Z
generated_by: discovery-external-researcher
---

# T-002: UX design + accessibility-as-flow

## Research question

What is the established UX design knowledge body — usability heuristics, information architecture, user-journey frameworks, cognitive load, error prevention and recovery? Specifically for accessibility-as-flow: what patterns address cognitive load on assistive-technology users, keyboard task completion, focus management, and error recovery for screen-reader paths (distinct from accessibility-as-baseline, which the existing `KB-frontend-design` Principle 3 already covers)?

## Findings

### Nielsen's 10 usability heuristics (Jakob Nielsen, 1994; refined repeatedly; current per Nielsen Norman Group)

1. **Visibility of system status.** Keep users informed about what's going on through appropriate feedback within reasonable time. (Loading states, progress, current location in IA.)
2. **Match between system and the real world.** Speak the user's language, follow real-world conventions. Information appears in natural and logical order.
3. **User control and freedom.** Users often choose system functions by mistake; emergency exit clearly marked. Undo and redo.
4. **Consistency and standards.** Don't make users wonder whether different words, situations, or actions mean the same thing. Follow platform conventions.
5. **Error prevention.** Even better than good error messages is a careful design that prevents the problem from occurring in the first place. Eliminate error-prone conditions or check for them and present users with a confirmation option.
6. **Recognition rather than recall.** Minimize memory load by making objects, actions, and options visible. The user should not have to remember information from one part of the interface to another.
7. **Flexibility and efficiency of use.** Accelerators — unseen by the novice user — may often speed up the interaction for the expert user. Allow tailoring of frequent actions.
8. **Aesthetic and minimalist design.** Dialogues should not contain information which is irrelevant or rarely needed. Every extra unit of information competes with relevant units.
9. **Help users recognize, diagnose, and recover from errors.** Error messages in plain language; precisely indicate the problem; constructively suggest a solution.
10. **Help and documentation.** Even though it is better if the system can be used without documentation, it may be necessary. Easy to search, focused on user's task, listing concrete steps.

### Canonical user-journey and IA frameworks (3+)

- **Norman's 7 stages of action** (Don Norman, *The Design of Everyday Things*). Goal → Plan → Specify → Perform → Perceive → Interpret → Compare. Two "gulfs" the design must bridge: the **gulf of execution** (between user's intent and system controls) and the **gulf of evaluation** (between system output and user's understanding). The model for diagnosing where in a task a user falls off.
- **Service Blueprint** (originally Lynn Shostack, 1984; modernized by Nielsen Norman Group). Maps the user-facing journey *and* the backstage processes that produce it; surfaces failure points at the line of visibility. Useful for cross-layer features where Frontend choices depend on Backend / API / Database behaviors.
- **Customer Journey Map** (Nielsen Norman Group's canonical format). Persona + scenario + journey phases + actions + thoughts + feelings + opportunities. Lighter-weight than service blueprint; emphasizes emotional arc.
- **Job-to-be-Done** (Clayton Christensen et al.). Frames the user's goal as the "job" they hire the interface to do. Useful for scoping (which jobs are in scope; which adjacent jobs are out).

### Canonical IA patterns

- **Card sort** — users group concepts into categories; reveals their mental model of the domain.
- **Tree test** — given a category tree, can users find a specific item? Measures findability without UI bias.
- **Content inventory** — systematic enumeration of all content with metadata (type, owner, freshness, audience). Substrate for IA decisions.
- **Sitemap / IA diagrams** — visual representation of the structure; how the user navigates between sections.

### Accessibility-as-flow (5+ patterns)

This is the dimension `KB-frontend-design`'s existing Principle 3 does NOT cover. Drawn primarily from Heydon Pickering's *Inclusive Components* and *Inclusive Design Patterns*, plus WCAG 2.2 understanding documents and Marcy Sutton's talks.

1. **Focus restoration after modal close.** When a modal opens, focus moves into it. When it closes, focus must return to the element that triggered the modal — otherwise screen-reader users lose their place in the task. Pattern: capture the triggering element; restore on close.
2. **Live-region choreography for async updates.** Toasts, search-results-updated, validation errors arriving after submit. Use `aria-live="polite"` for non-urgent (defer until current speech finishes) and `aria-live="assertive"` for urgent (interrupt). Avoid stacking — multiple concurrent announcements confuse the listener. Pattern: a single, well-managed live region per concern (form errors, system notices, route changes).
3. **Error-recovery paths for screen-reader users.** Inline validation that announces only when the user has left the field (not on every keystroke). Errors summarized in a live region or `role="alert"` AND linked to the offending field via programmatic association. Pattern: error → announce → focus stays at submit so the user can navigate back through `aria-describedby` references.
4. **Keyboard task completion.** Every interactive element reachable in tab order; arrow keys for grouped controls (radio groups, menus); Escape to close transient UI; Enter / Space to activate. The screen-reader user's reality: the page is a serial document. Task completion means: every step is reachable in serial order without getting lost in deep nested groups.
5. **Cognitive-load reduction.** Assistive-technology users carry higher per-step cognitive cost: screen-reader users read serial output, not visual hierarchy. Forms with 30 fields exhaust before completion. Pattern: progressive disclosure; chunked steps; explicit task boundaries ("Step 2 of 4"); auto-save so abandonment isn't catastrophic.
6. **Focus indicators that survive theme switches.** `:focus-visible` not `:focus`; minimum 3:1 contrast against adjacent surface; not relying on color alone (outline + offset). Pattern: a focus-style that works in light and dark themes and in high-contrast forced-colors mode.
7. **Heading hierarchy as a navigation aid.** Screen-reader users navigate by headings (H key). A page with malformed headings (skipped levels, decorative headings outside semantic structure) is harder to navigate than a page without any headings. Pattern: heading levels reflect the logical document structure, not the visual emphasis.

## Sources

- **Nielsen Norman Group** (nngroup.com) — Jakob Nielsen's 10 usability heuristics + the modern customer-journey-map format. Primary authoritative source.
- **Don Norman, *The Design of Everyday Things*** — 7 stages of action, gulfs of execution/evaluation. Foundational.
- **Heydon Pickering, *Inclusive Components* and *Inclusive Design Patterns*** — accessibility-as-flow patterns: focus management, live-region choreography, error-recovery.
- **Marcy Sutton talks and writing** — screen-reader-user experience reality; keyboard task completion.
- **WCAG 2.2 Understanding documents** (w3.org) — official guidance on each success criterion, with the rationale (and the difference between conformance and usability).
- **Lynn Shostack** ("Designing Services that Deliver," HBR 1984) — service blueprint origin.
- **Clayton Christensen et al., *Competing Against Luck*** — Jobs-to-be-Done framework.

## Acceptance-criteria check

| AC | Target | Status |
|---|---|---|
| Lists Nielsen's 10 heuristics with one-line summaries | 10 | ✅ All 10 with summaries |
| Names 3+ user-journey / IA frameworks | 3+ | ✅ 4 (Norman's 7 stages; service blueprint; customer journey map; JTBD) |
| Identifies 5+ accessibility-as-flow patterns with concrete examples | 5+ | ✅ 7 (focus restoration; live-region; error-recovery; keyboard completion; cognitive-load reduction; focus indicators; heading hierarchy) |
| Cites Nielsen Norman Group, WCAG, and 2+ accessibility-as-flow specialists | required | ✅ Nielsen Norman + WCAG 2.2 + Heydon Pickering + Marcy Sutton |

Acceptance-criteria check: **satisfied.**

## Notes for Synthesis and per-layer Design

1. **Separation from existing `KB-frontend-design` Principle 3 (accessibility-as-baseline).** The new content is additive, not replacing. Baseline (WCAG conformance, semantic HTML, contrast) stays; flow (focus, live regions, cognitive load) joins. The merged accessibility principle is wider but the boundary is clear: baseline = "is the page usable at all by AT users?"; flow = "can AT users efficiently complete the task with the cognitive budget they have?"
2. **Calibration to senior-handbook depth.** Nielsen's 10 are well-known to senior engineers but reading them as one-liners in the KB serves as a quick reference at preload time. The depth comes in the accessibility-as-flow patterns — these are NOT well-known and warrant the senior-handbook treatment.
3. **Citation precedent.** Nielsen Norman Group articles are the canonical citation; the new KB content should link to specific NN/g articles rather than re-state the heuristics in a substantively different form.
