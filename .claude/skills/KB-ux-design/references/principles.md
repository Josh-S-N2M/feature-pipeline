# Principles — Nielsen's 10 Heuristics

Jakob Nielsen's ten usability heuristics, published in 1994 and refined since, remain the durable evaluation lens for software interfaces. They are criteria for interrogating a design, not rules for generating one. The framing below: state the heuristic, describe its dominant failure mode, name the remediation discipline.

## Contents

- [x] How to use these heuristics
- [x] H1. Visibility of system status
- [x] H2. Match between system and the real world
- [x] H3. User control and freedom
- [x] H4. Consistency and standards
- [x] H5. Error prevention
- [x] H6. Recognition rather than recall
- [x] H7. Flexibility and efficiency of use
- [x] H8. Aesthetic and minimalist design
- [x] H9. Help users recognize, diagnose, and recover from errors
- [x] H10. Help and documentation
- [x] What the heuristics don't cover
- [x] Cross-references

## How to use these heuristics

Heuristic evaluation is a discount usability technique: a small number of evaluators (typically 3-5) walk through the interface independently, flagging violations of each heuristic with a severity rating. Aggregated findings prioritize remediation.

The discipline that makes the technique work: evaluators must apply each heuristic explicitly, in turn, against each surface — not eyeball the interface for general issues. The heuristics' value is forcing structured attention on failure modes that ad-hoc inspection misses.

Severity ratings (Nielsen's 0-4 scale):

| Rating | Meaning |
|---|---|
| 0 | Not a usability problem |
| 1 | Cosmetic — fix when convenient |
| 2 | Minor — low priority |
| 3 | Major — high priority |
| 4 | Catastrophic — must fix before release |

## H1. Visibility of system status

**Heuristic:** the system should always keep users informed about what is going on, through appropriate feedback within reasonable time.

**Dominant failure mode:** silent processing. A button click that triggers a 3-second backend call with no visual change leaves the user uncertain whether the click registered. They retry, double-submit, or abandon.

**Remediation discipline:**

- For actions <100ms: no feedback needed beyond the action's intrinsic visual change (button click ripple).
- For actions 100ms-1s: immediate visual acknowledgment (button enters loading state).
- For actions 1s-10s: explicit progress indicator (spinner, progress bar, "saving..." text).
- For actions >10s: progress with estimated time remaining; allow cancellation.
- For async updates the user didn't initiate: live-region announcement so screen readers learn about the change without polling.

Examples of well-handled status:

- A file upload showing percentage progress.
- A "saved 3 seconds ago" indicator after autosave.
- A toast notification confirming an action that updated state elsewhere on the page.

## H2. Match between system and the real world

**Heuristic:** the system should speak the users' language, with words, phrases, and concepts familiar to the user, rather than system-oriented terms. Follow real-world conventions, making information appear in a natural and logical order.

**Dominant failure mode:** exposing system internals in the UI. Error messages naming database tables; navigation labeled after internal modules; status codes shown literally to end users.

**Remediation discipline:**

- Translate system vocabulary to user vocabulary. "Validation error on field user_email_address" → "We don't recognize that email format."
- Use domain terminology the user brings to the product. A medical product's UI uses medical language; a developer tool's UI uses developer language.
- Order information by user-relevance, not implementation order. The user's most-needed item first.

This heuristic is also where internationalization considerations surface. Direct translation of UI strings often loses idiom; locale-appropriate phrasing requires cultural review beyond machine translation.

## H3. User control and freedom

**Heuristic:** users often choose system functions by mistake and will need a clearly marked "emergency exit" to leave the unwanted state without having to go through an extended dialogue. Support undo and redo.

**Dominant failure mode:** destructive actions without reversibility. Deleting an item without a "you can undo this for 10 seconds" affordance. Confirming a modal whose contents the user can't review.

**Remediation discipline:**

- Provide visible undo for destructive actions (preferred over confirmation modals, which interrupt flow).
- Modals must have a clear close affordance (X button, Escape key, click outside, "Cancel" button).
- Multi-step flows should support "back" without losing intermediate state.
- Long-running actions should be cancelable.

Undo > confirmation for routine actions. Confirmation > undo for irreversible actions (deleting an account; sending an email).

## H4. Consistency and standards

**Heuristic:** users should not have to wonder whether different words, situations, or actions mean the same thing. Follow platform conventions.

**Dominant failure mode:** inconsistent component behavior across the product. A "Save" button that saves on one page and submits a form on another. Modal close behavior varying by which modal.

**Remediation discipline:**

- Codify patterns in a design system (see `KB-design-system-design`).
- Follow platform conventions: macOS / Windows / Linux UI patterns where the product runs as a desktop app; iOS / Android conventions for mobile; web platform conventions for browsers.
- Component variants should be discoverable: a button has documented variants (primary, secondary, ghost); ad-hoc one-off buttons are a violation.

When breaking a convention, document why. "We use a slide-up panel instead of a modal for this case because [...]"

## H5. Error prevention

**Heuristic:** even better than good error messages is a careful design which prevents a problem from occurring in the first place.

**Dominant failure mode:** asking the user to do something the system could verify in advance. Free-text date fields when a date picker would constrain to valid dates. Sending an email without checking the recipient address format.

**Remediation discipline:**

- Constrain input where possible (date pickers, dropdowns, type-ahead, file pickers).
- Validate as the user types, not just on submit. Surface validation feedback inline near the field.
- Confirm for irreversible actions (see H3); but confirmation is the fallback, not the primary defense.
- Disable affordances that cannot succeed (a "Submit" button that's disabled until the form is valid is honest about its state).

Disabled affordances should explain why they're disabled. A grey button users can't click is hostile; a grey button with a tooltip ("Complete all required fields to submit") is informative.

## H6. Recognition rather than recall

**Heuristic:** minimize the user's memory load by making objects, actions, and options visible. The user should not have to remember information from one part of the dialogue to another.

**Dominant failure mode:** asking the user to remember what they typed three screens ago. Multi-step forms that hide previous steps' answers. CLIs that succeed on the third try because the user finally remembered the right flag combination.

**Remediation discipline:**

- Multi-step flows should show all prior steps' inputs (visible or one-click-expandable).
- Recently-used items surface in pickers (recent files; recent recipients; recent searches).
- Search affordances over deep navigation hierarchies for finding known items.
- Persistent navigation (the user always knows where they are; breadcrumbs; current-section indicators).

This heuristic argues against UIs where the user must hold state in their head. State should be in the interface, retrievable by glancing.

## H7. Flexibility and efficiency of use

**Heuristic:** accelerators — unseen by the novice user — may often speed up the interaction for the expert user. Allow users to tailor frequent actions.

**Dominant failure mode:** all interactions paced for the novice. Five-click flows where two clicks would suffice for users who know what they want. No keyboard shortcuts. No bulk operations.

**Remediation discipline:**

- Keyboard shortcuts for power users. Document them via `?` overlay or visible in menus.
- Bulk operations for repetitive tasks (select-many; apply-to-many).
- Saved searches, saved filters, saved views.
- Customizable layouts where users genuinely have different workflows.

The tension: novice clarity vs expert speed. Resolve by progressive disclosure — novice path obvious; expert shortcuts available but not in the novice's way.

## H8. Aesthetic and minimalist design

**Heuristic:** dialogues should not contain information which is irrelevant or rarely needed. Every extra unit of information competes with the relevant units and diminishes their relative visibility.

**Dominant failure mode:** dense UIs cluttered with metadata, status, icons, and affordances the user rarely needs. The result: scanning becomes work.

**Remediation discipline:**

- Default view: the most-needed information, prominently. Less-needed information available on demand (expand; hover; secondary tab).
- Visual hierarchy that matches information hierarchy. Most important largest / boldest / first.
- White space is not wasted space; it's the affordance for grouping and breathing room.
- Iconography that's recognizable without labels for actions the user takes constantly; labels for everything else.

The heuristic is anti-clutter, not anti-density. A spreadsheet's density is appropriate to its task; a dashboard with twelve KPIs of equal weight is a different problem.

## H9. Help users recognize, diagnose, and recover from errors

**Heuristic:** error messages should be expressed in plain language (no codes), precisely indicate the problem, and constructively suggest a solution.

**Dominant failure mode:** error messages that name what failed without saying why or how to fix it. "Validation failed." "An error occurred." Stack traces shown to end users.

**Remediation discipline:**

The three-part error message structure:

1. **Name the failure plainly.** "We couldn't save your draft."
2. **Locate the cause precisely.** "The email field has an invalid format" — and visually indicate which field via inline error UI.
3. **Suggest the recovery action.** "Try formatting like name@example.com." If the recovery requires action the user can't take alone, name who they should contact.

Pair with accessibility-as-flow disciplines (`accessibility-as-flow.md`): the error must be announced to screen readers via `aria-live` or `role="alert"`; focus should move to the error or to the offending field for keyboard users.

## H10. Help and documentation

**Heuristic:** even though it is better if the system can be used without documentation, it may be necessary to provide help and documentation. Any such information should be easy to search, focused on the user's task, list concrete steps to be carried out, and not be too large.

**Dominant failure mode:** documentation that exists somewhere but the user can't find it from the point of confusion. Onboarding tours that interrupt instead of helping. Help text that explains what a field IS rather than what to enter in it.

**Remediation discipline:**

- Contextual help at the point of confusion. Tooltip on the field; "?" icon next to the section.
- Search-first documentation: users with a specific question type the question; they don't browse to it.
- Documentation written task-first: "How do I cancel my subscription?" not "Subscription Management Module."
- Onboarding that's skippable, resumable, and re-launchable from settings.

## What the heuristics don't cover

Nielsen's heuristics are a 1994 framework that's held up remarkably well, but they are not a complete UX discipline. Areas where they're light:

- **Modern accessibility.** WCAG and a11y-as-flow disciplines (this KB's `accessibility-as-flow.md`) emerged after the original heuristics. Heuristic 9 touches a11y for errors; the rest are silent on screen-reader, keyboard, and cognitive a11y.
- **Mobile and touch.** Designed for mouse-driven desktop interfaces. Touch targets, gesture conflicts, mobile-specific patterns (pull-to-refresh; swipe actions) aren't addressed.
- **Information architecture at scale.** Heuristics evaluate a surface; IA evaluates a structure. `journey-and-ia.md` covers IA explicitly.
- **Cognitive load and decision fatigue.** Heuristic 6 (recognition) and heuristic 8 (minimalism) touch the area; cognitive-load research since (Sweller; cognitive accessibility guidelines) goes deeper.
- **Trust, privacy, and ethics.** Modern UX disciplines treat data handling, consent UX, dark-pattern avoidance as core. Heuristics are silent on these.

Use the heuristics as the durable lens; augment with the other reference files for the gaps.

## Cross-references

- **Accessibility flows that elaborate heuristic 9:** see `accessibility-as-flow.md`.
- **Journey decomposition that elaborates heuristic 7 (efficiency for expert users):** see `journey-and-ia.md`.
- **Design-system codification of consistency (heuristic 4):** see `KB-design-system-design`.
- **The original publication:** Nielsen, Jakob. "10 Usability Heuristics for User Interface Design." Nielsen Norman Group, 1994 (refined 2024). `nngroup.com/articles/ten-usability-heuristics`.
