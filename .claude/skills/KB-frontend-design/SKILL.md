---
name: kb-frontend-design
description: >-
  Design discipline for the Frontend layer — the user-facing rendering surface
  (web, mobile, desktop UI). Covers component composition, state-management,
  rendering strategy (SSR/SSG/CSR/streaming), data-flow, accessibility,
  performance budgets, and the per-layer designer's workflow. Use when a
  feature touches user-facing UI. Pairs with four sibling design-side KBs:
  KB-ux-design (Nielsen heuristics; journey + IA; accessibility-as-flow),
  KB-visual-design (type/color/space/motion; anti-slop discipline citing the
  Anthropic frontend-design skill), KB-design-system-design (token three-tier
  model; theming; governance), KB-component-architecture-design (atomic
  design; headless libraries; compound/slot/polymorphic patterns). Pairs with
  KB-storybook-platform (model-invocable; for Storybook-touching features)
  and KB-general-coding-principles. No platform partner KB — frontend
  platforms vary too widely (React, Vue, Svelte, SwiftUI, Jetpack Compose);
  design discipline is framework-agnostic.
allowed-tools: Read, Grep, Glob
---

# KB-frontend-design — Frontend Layer Design Discipline

Design discipline for the Frontend layer. The per-layer Frontend Designer (`design-frontend`) loads this KB during per-layer Design to produce the `### Frontend Design` subsection of the Blueprint. This KB is design-discipline-only — there is no platform partner KB (frontend platforms vary widely: React, Vue, Svelte, SwiftUI, Jetpack Compose, etc., and the design discipline is largely framework-agnostic).

## Contents

- When this KB is loaded
- The layer's responsibility
- Design decisions this layer owns
- Patterns and anti-patterns at a glance
- Interaction with other layers
- Surfacing architectural questions
- When to load each reference file

## When this KB is loaded

This KB is in scope when:

- A feature's PRD or Blueprint declares the **Frontend** layer in scope (per `layer-taxonomy.md` in KB-documentation-criteria)
- A per-layer Designer is producing the Frontend Design subsection of the Blueprint
- Plan Authoring produces tasks that touch UI components, client-side state, or rendering pipelines
- `shared-document-reviewer` or `review-architecture-auditor` is auditing artifacts that include Frontend Design

Sub-agents that reference this KB (per Blueprint v4.3.1):

- `design-frontend` (per-layer Design, when Frontend layer is in scope)
- `design-composer` (Design Composition, integrating Frontend design with cross-cutting concerns)
- `plan-author` (when tasks touch UI artifacts)
- `shared-document-reviewer` (Gate 1 Frontend-specific checks)
- `review-architecture-auditor` (CoVe checks on Frontend claims)

For platform-specific knowledge (React idioms, Vue composition API, SwiftUI property wrappers, etc.), Frontend Designers consult the Synthesis output (`synthesis.md`) — KBs in this pipeline are intentionally framework-agnostic on the design-discipline side.

## The layer's responsibility

The Frontend layer renders the application's user interface and brokers the user's interactions with the rest of the system. It owns:

- **What the user sees** — components, layout, visual hierarchy, accessibility affordances.
- **Client-side state** — local component state, shared cross-component state, server-state caching, navigation state, form state.
- **The rendering strategy** — how content reaches the user: server-side rendered, static-generated, client-side rendered, hybrid (streamed / island-architecture).
- **Data-flow choreography** — when to fetch (on mount? on hover? on submit?), what to optimistically update, how to roll back failed mutations, how to surface loading and error states.
- **User-perceived performance** — initial-load budget (Largest Contentful Paint, Interaction to Next Paint, Cumulative Layout Shift), the cost of every dependency added.

The Frontend layer does NOT own:

- The data contract — that belongs to the API layer (`KB-api-design`).
- Authentication and authorization logic — implemented at the API/Backend layer; the Frontend layer consumes the resulting session/token.
- Business logic that decides domain outcomes — that belongs to the Backend layer (`KB-backend-design`).
- Persistence — Frontend may cache, but the source of truth is the Backend.

## Design decisions this layer owns

The Frontend Designer makes (or surfaces) these decisions:

| Decision | Forced if … |
|---|---|
| Framework / library selection (React, Vue, Svelte, SwiftUI, etc.) | Greenfield; if brownfield, this is generally pre-existing |
| Rendering strategy (SSR / SSG / CSR / hybrid) | Public-facing pages exist; SEO matters; first-paint budget tight |
| State management scope (local vs. shared vs. server-state) | Multi-component state coordination required |
| Server-state caching library (TanStack Query, SWR, Apollo, custom) | API responses are consumed by multiple components |
| Component composition pattern (smart/dumb, container/presentational, hooks, signals) | Component count >~30 |
| Routing approach (file-system-based, declarative, manual) | Multi-page navigation |
| Form library and validation strategy | Forms with >3 fields or non-trivial validation |
| Accessibility baseline (WCAG level, focus management, ARIA) | The application has any user interaction |
| Performance budget (LCP target, INP target, JS bundle ceiling) | The feature degrades user experience if missed |
| Internationalization strategy | Multi-locale support is in scope |

Designers do NOT author ADRs (per FR-5 in Blueprint v4.3.1). When a decision warrants an ADR (cross-cutting concern, kill-criteria worth preserving, alternative-comparison worth recording), the designer surfaces it as an open item in the per-layer output's "Architectural Questions for Composer" section.

## Patterns and anti-patterns at a glance

The full discipline lives in `references/principles.md` and `references/patterns-and-anti-patterns.md`. Quick reference:

**Patterns to favor:**

- **Server state separate from client state** — don't put fetched data in the same store as UI state. The lifecycles, caching needs, and invalidation strategies differ.
- **Lift state only as far as it needs to go** — colocate when possible; lift only when multiple components need it.
- **Boundary errors at the right level** — error boundaries that catch render-time failures should be tight enough to isolate the failure but broad enough to recover meaningfully.
- **Optimistic updates with explicit rollback** — when latency would degrade UX and the failure mode is rare and recoverable.
- **Progressive enhancement** — the page should function (even if degraded) when JS fails to load, when network is flaky, when the user is on assistive tech.

**Anti-patterns to flag:**

- **Prop drilling past three levels** — pass a callback or use context/composition; deep drilling is a refactor signal.
- **Fetching inside render** — leads to waterfalls and re-fetch storms; fetch in effects or via a server-state library.
- **State stored in two places** — derived state recomputed twice gets out of sync; either compute on the fly or store once and derive.
- **Scattered global state** — every component reading from a global store is the same as prop drilling but slower to debug.
- **Animations and effects without `prefers-reduced-motion` check** — accessibility regression.
- **`any` in TypeScript Frontend code** — defeats the purpose of typed UI props.

## Interaction with other layers

The Frontend layer's typical layer-graph position:

```
User ──► Frontend ──► API ──► Backend ──► Query ──► Database
                                  │
                                  └──► IaC (deploy) ──► CI/CD (build)
```

The Frontend Designer's responsibility regarding adjacent layers:

- **API (upstream)** — the Frontend consumes the API's contract. The Frontend Designer should NOT design the API; they may surface requests for API changes via `dependencies_on_other_layers` in the per-layer output's sidecar JSON.
- **Backend / Query / Database** — Frontend has no direct relationship. Coupling between Frontend and Database (e.g., the Frontend reading a DB column name) is an architectural smell — surface to the composer.
- **CI/CD** — Frontend has build-time concerns (bundling, asset pipelines, static analysis); these usually go in the CI/CD design subsection, not Frontend Design.

## Surfacing architectural questions

The Frontend Designer cannot author ADRs (per FR-5). When a decision should be recorded as an ADR, surface it in the per-layer output's open-items section using this template:

```markdown
## Architectural Questions for Composer

- **Q-FE-1**: Should we adopt a server-state library (TanStack Query / SWR / RTK Query)? The choice affects how Backend exposes mutation endpoints (idempotency, error envelope shape) and how the Frontend handles optimistic updates. Evidence: 12 of the 17 features in scope have at least one mutation that would benefit from optimistic UX. Options: (a) TanStack Query; (b) SWR; (c) keep ad-hoc fetching for now. Recommended: (a) — superset of (b)'s features, robust mutation API. Defer to composer.
```

Composers resolve Q-FE-N items via cross-layer arbitration (see `design-composition.md` in KB-documentation-criteria) and may author an ADR.

## When to load each reference file

| Load this file | When the task involves |
|---|---|
| `references/principles.md` | Authoring or reviewing a Frontend Design subsection — covers the layer's foundational principles (separation of concerns, accessibility-by-default, performance budgets, progressive enhancement) |
| `references/patterns-and-anti-patterns.md` | Choosing between competing component / state / data-flow approaches — covers common patterns with when-to-use, and the anti-patterns reviewers should flag |

These are intentionally short and high-leverage. For depth on a specific framework, consult the Synthesis output of the current pipeline run.
