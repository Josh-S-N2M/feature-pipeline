# Accessibility as Flow

Accessibility framed as task completion, not as a checklist. The discipline asks: can a person who cannot rely on visual-default affordances actually finish the task? A WCAG checklist passing while the flow fails is a common failure mode. This document covers the patterns that make accessibility load-bearing in flow.

## Contents

- [x] Why "as flow" matters
- [x] Focus restoration
- [x] Live-region choreography
- [x] Error-recovery loops
- [x] Keyboard task completion
- [x] Cognitive-load reduction
- [x] Focus indicators
- [x] Heading hierarchy
- [x] When the checklist matters
- [x] Cross-references

## Why "as flow" matters

The standard a11y discipline is structured around WCAG (Web Content Accessibility Guidelines). WCAG is a useful framework but its grain is the static page: does this element have alt text; is this color contrast sufficient; is this label associated with this input. Pages pass WCAG; flows still fail.

Example: a multi-step form with WCAG-compliant labels, contrast, and alt text. A keyboard user starts at step 1, completes it, advances to step 2. Focus lands... where? If focus lands on the page body (default browser behavior after `<a>` navigation), the user must Tab through the heading, navigation, and several form scaffolding elements before reaching the first input of step 2. By the time they get there, they've forgotten which step they're on. WCAG checks pass; the flow is unusable.

Accessibility-as-flow is the discipline that treats every transition (route change; modal open; modal close; error appearance; async update; step advance) as a focus-management decision. The audience is keyboard users, screen-reader users, and users with cognitive disabilities — all of whom rely on the interface's flow discipline, not just its static markup.

## Focus restoration

Focus management is the single highest-leverage discipline in a11y-as-flow. The rules:

**On route change (SPA navigation):** focus should move to a sensible target on the new page. Default browser behavior (full page reload) moves focus to the page top; SPA frameworks do not, by default. Set focus explicitly:

- Preferred target: the new page's H1 (with `tabindex="-1"` to make it focusable but not in tab order).
- Alternative: the main content landmark (`<main>` with `tabindex="-1"`).
- Avoid: focusing the back/forward navigation, which fights the user's reading direction.

In React Router or TanStack Router setups, this is typically a router-level effect that runs on pathname change. Document the pattern explicitly in the project's frontend skeleton.

**On modal open:** focus moves into the modal, typically to the first focusable element (input; primary action button). Focus is trapped within the modal (Tab cycles through modal elements; Shift+Tab cycles backward; Tab from the last element returns to the first).

**On modal close:** focus returns to the element that opened the modal. This is the most commonly violated discipline. The user clicked a button, opened a dialog, closed it — and focus is now at the page top, far from their place. Restore focus to the originating element.

Headless component libraries (Radix, React Aria, Headless UI) handle these patterns correctly out of the box. Ad-hoc modal implementations almost always get this wrong.

**On step advance in a multi-step flow:** focus moves to the new step's first input or the step heading. The user should land where they need to act next, not where the framework happens to land them.

**On async update that replaces the focused element:** if the user was interacting with an element that gets removed (saved a field; toggled an item out of a list), focus should move to a logical successor (next item; parent container; toast confirming the action).

## Live-region choreography

Async updates the user did not initiate need to be announced to screen readers. The mechanism: `aria-live` regions and `role="status"` / `role="alert"` containers.

```html
<div aria-live="polite" aria-atomic="true">
  <!-- Content written here is announced by screen readers -->
</div>
```

Three politeness levels:

- **`aria-live="off"`** (default for normal elements) — no announcement.
- **`aria-live="polite"`** — announced when the screen reader finishes its current utterance. Use for informational updates (autosave confirmation; new notification badge).
- **`aria-live="assertive"`** — interrupts current utterance. Use sparingly; reserved for error states or urgent feedback. Equivalent to `role="alert"`.

`aria-atomic="true"` ensures the entire region content is announced when any part changes; `aria-atomic="false"` announces only the changed nodes. The default behavior is browser-dependent; declaring explicitly avoids surprises.

Common patterns:

- **Toast notifications** — render in a fixed `aria-live="polite"` region. Each new toast is appended; screen readers announce it. The visual presentation auto-dismisses; the announcement happens once at appearance.
- **Form validation** — a persistent `role="status"` region near the form summary announces "3 errors found" + the field-level details. Field-level errors use `aria-describedby` linking to the inline error message.
- **Search results** — `aria-live="polite"` on a results-count container announces "12 results found" after filter changes.
- **Loading states** — `aria-live="polite"` announces "Loading..." then "Loaded" or the result count. The loading announcement is informational; do NOT use `aria-busy="true"` alone (screen readers may suppress entirely while busy).

Anti-pattern: making the entire page an `aria-live` region. Every DOM mutation announces; the user is flooded.

Anti-pattern: `aria-live="assertive"` on routine status updates. Save the assertive level for genuine alerts.

## Error-recovery loops

A WCAG-compliant error message is necessary but not sufficient. The flow discipline:

1. **Announcement.** Errors must be announced to screen readers. Form-level summary in `role="alert"`; field-level errors in `aria-live="polite"` regions or via `aria-describedby` from the offending field.
2. **Identification.** Each error must indicate which field it applies to. Visual: red border + inline message. Programmatic: `aria-invalid="true"` on the input + `aria-describedby` pointing to the error message id.
3. **Correction guidance.** Each error tells the user how to fix it (Nielsen's heuristic 9). "Email must include @" is better than "Invalid format."
4. **Focus to the recovery point.** After submission with errors, focus moves to the first field with an error (or the error summary if multiple). The user shouldn't have to hunt for what failed.
5. **Confirmation on success.** When errors are corrected and submission succeeds, announce the success ("Saved" via `aria-live="polite"`).

```html
<label for="email">Email</label>
<input
  id="email"
  type="email"
  aria-invalid="true"
  aria-describedby="email-error"
  value="alice@"
/>
<div id="email-error" role="alert">
  Email must include a domain (e.g., alice@example.com).
</div>
```

The `id="email-error"` + `aria-describedby="email-error"` pairing connects the input to its error programmatically. Screen readers announce the error when focus is on the input.

## Keyboard task completion

Every flow must be completable using only the keyboard. The discipline:

- **Tab order matches visual order.** Source order in the DOM should reflect reading order. CSS can reorder visually (`flex-direction: row-reverse`; `grid-area` overrides); tab order follows DOM order regardless.
- **Every interactive element is focusable.** Buttons, links, form controls, custom controls — all in the tab sequence (or reachable via the appropriate pattern, e.g., arrow keys for radio groups, listboxes).
- **Custom controls follow ARIA patterns.** A custom dropdown is a `combobox` (with arrow-key navigation); a custom tab set is `tablist`/`tab`/`tabpanel`; a custom tree is `tree`/`treeitem`. The ARIA Authoring Practices Guide (`w3.org/WAI/ARIA/apg`) documents the keyboard expectations per pattern.
- **Visible affordances do not require pointer.** A button shown on row-hover that triggers an action — the action must also be reachable via keyboard. Common solution: row gets focus via Tab; action button shows on focus-within; action reachable via subsequent Tab.
- **Skip links for repetitive navigation.** A "Skip to main content" link at the top, visible on focus, lets keyboard users bypass site navigation.

Test discipline: walk through each new flow using only Tab, Shift+Tab, Enter, Space, and arrow keys. Note any step that requires a pointer. Each such step is a violation.

## Cognitive-load reduction

Cognitive accessibility addresses users with cognitive disabilities (attention, memory, comprehension) and benefits all users. The disciplines:

- **Chunk information into small units.** Multi-step forms with 3-5 inputs per step beat single forms with 30 inputs. Visible progress (step 2 of 5) anchors the user.
- **Progressive disclosure.** Advanced options collapsed by default. Power users expand; novice users aren't overwhelmed.
- **Predictable patterns.** A "Save" button is in the same place, same color, same label across every form. Heuristic 4 (consistency) translated to cognitive load.
- **Clear language.** Sentence-case labels, plain language, no jargon. WCAG 2.1's "Reading Level" success criterion (3.1.5) — content should be readable at lower secondary education level where feasible.
- **Adequate time.** Avoid timeouts on form submission and reading. If a timeout is necessary, allow extension. WCAG 2.2.1.
- **Concrete > abstract.** "Enter your phone number, including area code: (555) 123-4567" is more usable than "Phone number".

These overlap with general usability — cognitive load reduction is good UX for everyone, not a special-case discipline.

## Focus indicators

Visible focus indicators are how keyboard users see where they are. Default browser focus rings are functional but visually subtle; many designs override them. The discipline:

- **Never `outline: none` without replacement.** Removing the focus ring without providing an alternative is the most common a11y violation in modern UI.
- **Replacement must meet contrast.** WCAG 2.4.7 (focus visible) plus the newer WCAG 2.4.11 (focus appearance) require focus indicators with at least 3:1 contrast against the surrounding background. The newer 2.4.13 (focus appearance enhanced; AAA) requires 4.5:1.
- **Replacement must be visible on every interactive element.** Buttons, links, inputs, custom controls.

CSS pattern:

```css
:focus-visible {
  outline: 2px solid var(--color-focus);
  outline-offset: 2px;
}
```

`:focus-visible` (not just `:focus`) shows the indicator for keyboard focus only — clicked buttons don't show a ring (which would surprise mouse users) but tabbed-to buttons do. Modern browsers support this widely.

For complex controls (custom comboboxes, custom trees), the focus indicator may need to live on a child element or use `box-shadow` instead of `outline` to render correctly within parent overflow contexts.

## Heading hierarchy

Headings are screen-reader navigation. Users press `H` (NVDA, JAWS, VoiceOver) to jump between headings. A correct hierarchy is the screen-reader equivalent of a table of contents.

- **One `<h1>` per page.** The page's main subject.
- **No skipped levels.** `<h2>` follows `<h1>`; `<h3>` follows `<h2>`; etc. Skipping (h1 → h3) breaks the outline.
- **Heading content describes the section.** "Section heading" is meaningless; the actual topic earns the heading.
- **Heading text is announced, not the visual size.** A `<h2>` styled to look small is still navigation-relevant; a `<div>` styled to look like a heading is invisible to navigation.

CSS can decouple visual size from semantic level. A `<h3>` rendered at H1 size is fine if the document's outline requires h3 at that position. The semantic hierarchy serves screen readers; the visual hierarchy serves sighted users; they don't have to match.

## When the checklist matters

This document foregrounds flow over checklist. The checklist still matters — WCAG conformance is often a legal or organizational requirement. Treat the checklist as the floor:

- Color contrast meeting WCAG AA (4.5:1 for normal text; 3:1 for large text and UI components).
- Alt text on informative images; empty alt on decorative images.
- Labels associated with form controls.
- Language attribute on `<html>` and on inline language changes.
- Reflow at 320 CSS pixels without horizontal scrolling.
- Text spacing adjustable without content loss.

Tools that automate the checklist: axe-core (the engine behind `@storybook/addon-a11y`, Lighthouse, and most testing integrations); WAVE (browser extension); Accessibility Insights (Microsoft's tool). Manual review remains necessary for flow-level concerns the tools cannot catch.

## Cross-references

- **Nielsen's heuristic 9 (error recognition / recovery) elaborated for a11y:** see `principles.md`.
- **Journey decomposition that highlights focus-restoration touchpoints:** see `journey-and-ia.md`.
- **Headless component libraries that implement focus management correctly:** see `KB-component-architecture-design/references/headless-libraries.md`.
- **Storybook a11y testing integration:** see `KB-storybook-platform/references/testing.md`.
- **WCAG 2.2 reference:** `w3.org/TR/WCAG22`.
- **ARIA Authoring Practices Guide:** `w3.org/WAI/ARIA/apg`.
