# Frontend Design Principles

The foundational principles a Frontend Designer applies when authoring the `### Frontend Design` subsection of the Blueprint.

## Contents

- Principle 1: Separate server state from client state
- Principle 2: Colocate, then lift
- Principle 3: Accessibility is a baseline, not a feature
- Principle 4: Performance budgets are concrete numbers, not aspirations
- Principle 5: Progressive enhancement, not perfect-or-nothing
- Principle 6: Error boundaries scoped to recovery, not coverage
- Principle 7: Type the contract, not just the view
- Principle 8: Choose the framework's grain

## Principle 1: Separate server state from client state

**Server state** is data that originates outside the browser (or the client process) and may change without the client knowing. It has different lifecycle characteristics from client state:

| Concern | Client state | Server state |
|---|---|---|
| Source of truth | The component or store | The server |
| Staleness | Never (always current) | Always possible |
| Caching | Not needed | Required (otherwise refetch storms) |
| Invalidation | Set / update directly | Requires explicit revalidation |
| Concurrency | Single-writer (the user) | Multi-writer (other users, jobs) |
| Optimistic updates | N/A | Often beneficial |

Putting server state in the same store as client state (e.g., shoving fetched users into a Redux slice next to the modal-open flag) collapses these distinctions and pushes the team into hand-rolling cache, invalidation, and refetch logic — usually badly.

The Frontend Designer recommends a server-state library (TanStack Query, SWR, RTK Query, Apollo) when:

- The application has more than ~3 API endpoints
- Multiple components consume the same fetched data
- Mutations need optimistic UI
- Background revalidation matters (the user expects "fresh enough" data)

Client state (UI flags, form draft, navigation) stays in component state, context, or a lightweight store (Zustand, Jotai, Signals) — kept separate.

## Principle 2: Colocate, then lift

Start with state in the component that uses it. Lift only when a second component genuinely needs the same value.

Anti-pattern: starting with global state ("we might need it elsewhere later"). The result is a global store with 200 keys, half of which are used by one component, and the application is slower than it should be because every dispatch triggers reconciliation work nobody cares about.

The decision sequence for a new piece of state:

1. **One component uses it?** → local state (`useState`, `signal`, `ref`).
2. **Multiple sibling components use it?** → lift to their common parent.
3. **Components far apart use it?** → context (React) or shared store with selectors (Zustand, Jotai, signals).
4. **It's server data?** → server-state library (see Principle 1), not the shared store.

Lifting is a refactor, not a design-time decision in most cases. Designing for the worst case ("everything might need to be global") is overhead the rest of the team pays for indefinitely.

## Principle 3: Accessibility is a baseline, not a feature

WCAG 2.2 AA conformance is the floor, not the ceiling. The Frontend Designer makes the accessibility baseline an Acceptance Criterion of the layer.

Concrete commitments at design time:

- **Keyboard navigation** — every interactive element reachable by Tab, with visible focus indicators. No `outline: none` without a replacement.
- **Semantic HTML** — `<button>` for buttons, `<a>` for links, `<form>` for forms. Native semantics carry baked-in accessibility behavior; ARIA roles bolt-on are second-best and easy to get wrong.
- **Color contrast** — 4.5:1 for normal text, 3:1 for large text and UI components.
- **`prefers-reduced-motion`** — every animation respects this media query. Auto-playing carousels, parallax effects, and decorative animations get a no-motion path.
- **Form labels** — every input has a programmatically associated label. Placeholders are not labels.
- **Live regions** — async UI changes (toasts, search results, validation errors) get an `aria-live` region so screen readers announce them.

The Frontend Designer SHOULD include accessibility Acceptance Criteria. Example EARS-format ACs:

- When the user navigates the form using Tab, the system shall expose every interactive element in DOM order with a visible focus indicator.
- The system shall maintain 4.5:1 contrast ratio for all text in the default and dark themes.
- Where `prefers-reduced-motion: reduce` is set, the system shall not play decorative animations.

## Principle 4: Performance budgets are concrete numbers, not aspirations

"Fast" is not a design commitment. Concrete budgets are.

The Frontend Designer sets budgets aligned with Core Web Vitals (or platform equivalents):

| Budget | Web baseline | Aggressive target |
|---|---|---|
| Largest Contentful Paint (LCP) | < 2.5s p75 | < 1.8s p75 |
| Interaction to Next Paint (INP) | < 200ms p75 | < 100ms p75 |
| Cumulative Layout Shift (CLS) | < 0.1 p75 | < 0.05 p75 |
| Total Blocking Time (TBT) on a mid-tier mobile | < 200ms | < 100ms |
| JS bundle, initial route, gzipped | < 200KB | < 100KB |

Mobile equivalents (Frame rate, app startup time, memory footprint) apply analogously.

These budgets become Acceptance Criteria. The Frontend Designer documents how the budgets will be measured (Lighthouse CI, Web Vitals in production telemetry, etc.) and at what test boundary they're verified (Verification Strategy section of the Blueprint).

Anti-pattern: declaring a budget that isn't measured. A budget without instrumentation is wishful thinking.

## Principle 5: Progressive enhancement, not perfect-or-nothing

The application should function — even if degraded — when:

- JavaScript fails to load (network glitch, ad-blocker over-reach, CDN incident)
- The network is slow (3G or worse) or intermittent
- The user is on assistive tech (screen reader, switch control, voice control)
- The user prefers reduced motion, high contrast, or large text

Progressive enhancement isn't the same as "no JS." It means: the critical path works first; enhancements layer on top. The Frontend Designer documents which parts of the experience MUST work without JS (login, primary CTA, content read) and which are JS-enhanced (rich validation, optimistic UX, animations).

For web specifically: server-rendered HTML is the foundation; client-side hydration enhances it. SPA-only architectures still benefit from documenting what happens when the bundle fails.

## Principle 6: Error boundaries scoped to recovery, not coverage

A common mistake: wrapping the entire app in one error boundary "to catch everything." When something throws, the user sees a blank "Something went wrong" page and loses all context.

The Frontend Designer specifies error boundaries at the granularity of recovery: each boundary should isolate failures to the part of the UI that can fail independently and still leave the rest functional.

Examples:

- Per-route error boundary — a broken page doesn't blank the whole app.
- Per-widget error boundary on a dashboard — one chart can fail without taking down the others.
- Per-modal error boundary — a broken modal can close and let the user retry.

Boundaries are paired with telemetry (the error gets logged, not just displayed) and recovery (the user can navigate away, retry, or close the failed component).

## Principle 7: Type the contract, not just the view

In typed languages (TypeScript, Kotlin/Swift for mobile), the Frontend Designer ensures the typed model covers:

- **The API response shape** — generated from the API contract (OpenAPI, GraphQL schema, gRPC proto) when possible. Hand-typed copies drift.
- **The component prop interface** — required vs. optional fields, allowed values (literal unions for enum-shaped props).
- **The state shape** — including loading and error variants. A common anti-pattern is `loading: boolean; data: T; error: Error` which has 8 representable states (most invalid). Better: a discriminated union (`{ status: 'idle' | 'loading' | 'success' | 'error', data?, error? }`).

Generated types from the API contract are the source of truth. When the API changes shape, the Frontend's type checker should fail first, before runtime.

## Principle 8: Choose the framework's grain

Every framework has a grain — patterns that work with it and patterns that fight it. React's grain is composition + hooks; Vue's grain is reactive refs + computed; Svelte's grain is reactive declarations; SwiftUI's grain is state-driven view tree. Designing against the grain produces brittle code.

Examples of designing against the grain:

- React: building a global reactive system mid-component-tree, fighting render cycles. Fix: use the framework's mechanisms (context, derived state) or pick a state library that integrates well.
- Vue: imperatively manipulating the DOM with refs when reactivity would have done it declaratively.
- SwiftUI: forcing imperative `UIKit` patterns into SwiftUI, ending up with hybrid code nobody can debug.

The Frontend Designer documents the chosen framework's grain in the Frontend Design subsection's "Patterns" section and justifies any deviation explicitly.
