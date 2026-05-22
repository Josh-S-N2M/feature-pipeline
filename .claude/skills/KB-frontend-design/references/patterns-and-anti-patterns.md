# Frontend Patterns and Anti-Patterns

Patterns the Frontend Designer favors, anti-patterns to flag, and the decision frames the per-layer Designer applies when choosing among them.

## Contents

- Component composition patterns
- State management patterns
- Data-fetching patterns
- Form patterns
- Rendering strategy patterns
- Anti-patterns reviewers should flag
- Decision frames

## Component composition patterns

### Smart / dumb (container / presentational) split

**Pattern.** Separate components that fetch and own data ("smart" / "containers") from components that purely render props ("dumb" / "presentational").

**When to use.** When the same visual component appears in multiple contexts with different data sources, or when testing presentation in isolation matters. The presentational component is easy to unit test (pure props → render) and reusable.

**When not.** For small applications, the split adds overhead without benefit. Modern hooks (React) and composition APIs (Vue) often collapse the boundary cleanly.

### Compound components

**Pattern.** A parent component exposes related child components via dot-notation or context:

```tsx
<Modal>
  <Modal.Title>...</Modal.Title>
  <Modal.Body>...</Modal.Body>
  <Modal.Footer>...</Modal.Footer>
</Modal>
```

**When to use.** When the children logically belong to the parent and the parent coordinates their behavior (focus management, open/close state). Gives flexibility without prop explosion.

**When not.** When a single configuration object would do — compound components are a layout abstraction, not a configuration mechanism.

### Render props / slots

**Pattern.** A parent component takes a child-rendering function (React) or named slot (Vue) and supplies values to it.

**When to use.** When the parent owns logic (e.g., data fetching, drag-and-drop) but the consumer wants to control rendering.

**When not.** Hooks (React) or composables (Vue) have largely replaced this pattern for logic reuse. Render props remain useful for layout customization.

### Hooks / composables / signals

**Pattern.** Factor out reusable stateful logic into a function that components call. Each call gets its own instance of the state.

**When to use.** The default for logic reuse in React, Vue 3, and Solid. Replaces higher-order components and most render props.

**When not.** When the logic doesn't need React/Vue/Solid features (no state, no effects). Plain functions are simpler.

## State management patterns

### Local state for transient UI

Use the framework's primitive (React `useState`, Vue `ref`, Svelte stores) for state that:

- Belongs to a single component
- Has a short lifecycle (tied to the component's mount)
- Doesn't need to survive navigation

Examples: form draft, modal open/close, hover state, current tab.

### Context for cross-cutting client state

Use the framework's context mechanism for state that:

- Multiple non-adjacent components consume
- Is rarely updated (changing context value triggers re-render of all consumers)
- Is genuinely cross-cutting (theme, locale, current user, feature flags)

Anti-pattern: putting frequently-changing state in context. Every change re-renders every consumer.

### Shared store (Zustand, Jotai, Pinia, signals)

Use a lightweight store for state that:

- Is shared across many components (more than ~3) AND
- Changes frequently AND
- Doesn't fit the server-state model

Modern stores expose granular subscriptions — components only re-render when the slice they read changes. Redux still works but is overkill for most applications now; its strengths (time-travel debugging, devtools) are matched by Zustand + Redux DevTools.

### Server-state library

Use a dedicated server-state library for fetched data (see `principles.md` Principle 1). The library handles:

- Background revalidation
- Stale-while-revalidate
- Mutation with rollback
- Cache invalidation
- Request deduplication
- Pagination, infinite scroll

Examples: TanStack Query (React, Vue, Solid, Svelte), SWR (React), RTK Query (React/Redux), Apollo (GraphQL).

## Data-fetching patterns

### Fetch in effects, not in render

A component's `render` function should be pure. Fetching in render (or in a `useMemo` that calls `fetch`) leads to:

- Waterfall: child fetches block on parent finishing first render
- Refetch storms: every re-render kicks a new fetch
- Race conditions: late fetches overwrite fresh ones

Fetch in an effect (React `useEffect`, Vue `onMounted`, Svelte `onMount`) or use a server-state library that handles the lifecycle.

### Parallel data fetching at route boundaries

When a route needs multiple independent pieces of data, fetch them in parallel — not sequentially. Most server-state libraries support this idiom (multiple `useQuery` calls in the same component run in parallel; framework-level data routers like TanStack Router, Next.js loaders, Remix loaders enforce parallel by default).

Anti-pattern: sequential fetches that each `await` the previous one when they don't have a real dependency.

### Mutation with optimistic update + rollback

When a mutation is likely to succeed and latency matters, optimistically update the local cache, then roll back on error:

```ts
mutation.mutate(newValue, {
  onMutate: async (newValue) => {
    await queryClient.cancelQueries(['key']);
    const previous = queryClient.getQueryData(['key']);
    queryClient.setQueryData(['key'], newValue);
    return { previous };
  },
  onError: (err, _newValue, context) => {
    queryClient.setQueryData(['key'], context.previous);
    notify.error('Could not save, reverted.');
  },
  onSettled: () => queryClient.invalidateQueries(['key']),
});
```

The Frontend Designer specifies which mutations get optimistic UX (high-frequency, low-stakes) and which get explicit loading indicators (low-frequency, high-stakes — e.g., payment, deletion).

## Form patterns

### Controlled vs. uncontrolled

**Controlled inputs** keep the value in component state; the input reads the state and updates on change. Pros: full control, easy validation. Cons: every keystroke re-renders.

**Uncontrolled inputs** keep the value in the DOM; reads happen on submit via refs or `FormData`. Pros: no re-renders, native form semantics. Cons: harder to do live validation.

The Frontend Designer picks the right one by validation needs:

- Live validation, dependent fields, computed-from-other-fields → controlled
- Submit-time validation only, simple form → uncontrolled (or a form library that uses uncontrolled under the hood, like React Hook Form)

### Form library selection

For forms with >5 fields, complex validation, or array-of-records inputs: use a form library (React Hook Form, Formik, Vee-Validate). Hand-rolling form state for these consistently produces bugs in field-level dirty/touched tracking, multi-step navigation, and async validation.

For forms with 1–3 simple fields, controlled state is fine — no library needed.

## Rendering strategy patterns

### SSR (Server-Side Rendering)

The server renders HTML per request. Good for: content that varies per user (authenticated dashboards), SEO-critical pages with dynamic data, low-latency first paint.

Cost: server compute per request, more complex deploys.

### SSG (Static Site Generation)

HTML pre-rendered at build time, served as static files. Good for: marketing pages, blogs, documentation, anything with low update frequency.

Cost: rebuild required for content changes (unless paired with ISR).

### ISR (Incremental Static Regeneration)

SSG with revalidation: pages pre-rendered, then regenerated in the background after a stale interval. Good for: e-commerce catalogs, news, mostly-static content with occasional updates.

### CSR (Client-Side Rendering)

JS renders everything in the browser. Good for: authenticated SPAs where SEO doesn't matter, internal tools, dashboards with heavy interactivity.

Cost: blank-page wait until JS loads and runs; SEO issues without a fallback.

### Streaming SSR / islands / partial hydration

Modern frameworks (Next.js App Router, Remix, SvelteKit, Astro, Qwik) blur the lines. The Frontend Designer documents which routes use which strategy and why.

## Anti-patterns reviewers should flag

| Anti-pattern | Why it's bad | Typical fix |
|---|---|---|
| Prop drilling past 3 levels | Refactoring nightmare; obscures component ownership | Context, composition, or shared store |
| Fetching inside render | Refetch storms, waterfalls, race conditions | Move to effect or server-state library |
| Two stores for the same data | Inevitable drift | Single source; derive other views |
| `any` in TypeScript Frontend code | Defeats type safety; bugs leak through | Generated types from API contract |
| Boolean flags for loading/error/data | 8 representable states, most invalid | Discriminated union |
| `outline: none` without focus replacement | Accessibility regression | `:focus-visible` with explicit styling |
| Decorative animations without `prefers-reduced-motion` | Accessibility regression | Media query gate |
| Form `<input>` without an associated `<label>` | Accessibility regression | `htmlFor` / `for` attribute |
| Auto-playing carousel without pause | Accessibility regression | Pause control, respect `prefers-reduced-motion` |
| Color as the only signal (red = error) | Accessibility regression for color-blind users | Color + icon + text |
| Modal that traps focus on open but doesn't release on close | Accessibility regression | Focus management library or careful refs |
| Storing JWT in `localStorage` for an auth-sensitive app | XSS exposure | HttpOnly cookie if backend supports it; otherwise document the trade-off |
| Hand-typed copies of API responses (no generated types) | Drift between FE types and actual API shape | Codegen from OpenAPI / GraphQL / gRPC |
| Mixing CSS-in-JS, CSS modules, and global CSS without convention | Specificity wars, maintenance pain | One styling approach per project, documented in the Frontend Design subsection |
| Component file >500 lines | Hard to read, hard to test | Extract sub-components and hooks |
| `useEffect` with missing dependencies | Bugs that surface intermittently | Lint rule (`react-hooks/exhaustive-deps`) and fix the warnings |

## Decision frames

When the Frontend Designer faces a choice (framework, state library, rendering strategy, form library, etc.), apply this frame:

1. **What does the team already use?** Familiarity reduces design risk. Deviation needs justification.
2. **What's the worst-case load shape?** A B2C app with mobile-3G users has different constraints than an internal admin tool on a wired network.
3. **What's the team's testing maturity?** Untested code in a framework with a steep learning curve compounds risk.
4. **What's the dependency cost?** Every library added to the bundle costs initial load time and security-update surface area.
5. **What's the deprecation horizon?** Frameworks and libraries deprecate; check the project's age and ongoing maintenance.

These frames produce arguments, not answers. The Designer writes the argument in the per-layer Design subsection's "Rationale" portion so the composer (and later reviewers) can evaluate it.
