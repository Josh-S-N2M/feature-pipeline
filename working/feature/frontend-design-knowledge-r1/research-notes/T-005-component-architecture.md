---
id: RN-T-005
topic_id: T-005
topic_name: Component architecture
maps_to_ac: AC-FR-1-e
generated: 2026-05-20T23:15:00Z
generated_by: discovery-external-researcher
---

# T-005: Component architecture

## Research question

What is the established component architecture knowledge body — atomic design (Frost's 5 tiers), compound components, headless components (Radix UI, React Aria), controlled vs uncontrolled, polymorphic / `as` prop, slot patterns, ref forwarding, prop API design?

## Findings

### Atomic design — Brad Frost's 5 tiers (2013, now canonical)

A mental model for the *organizational hierarchy* of a UI, not a strict implementation requirement. From smallest to largest:

1. **Atoms.** Smallest functional building blocks. Single inputs / buttons / labels / icons / a single text input. Cannot be broken down further while remaining useful. Examples: `Button`, `Input`, `Icon`, `Label`.
2. **Molecules.** Small groups of atoms working as a unit. Examples: `SearchBar` (Input + Button + Icon); `FormField` (Label + Input + ErrorMessage); `NavigationItem` (Icon + Label + active-state marker).
3. **Organisms.** Distinct sections of an interface composed of molecules and atoms. Examples: `Header` (Logo + Nav + SearchBar + UserMenu); `ProductCard` (Image + Title + Price + AddToCart); `DataTable` (Filters + Headers + Rows + Pagination).
4. **Templates.** Page-level layouts with placeholder content. Define the structure; the content slots are filled later. Examples: `DashboardTemplate` (header + sidebar + main + footer); `ArticleTemplate` (hero + body + sidebar + related).
5. **Pages.** Templates instantiated with real content. The user-facing artifact. Examples: `OrdersPage`, `SettingsPage`, `BlogPostPage`.

The criticism Frost addresses repeatedly: atomic design is a *mental model*, not a rigid file/folder structure. Implementations vary — some teams use the names as directory structure; others use them as concept-only. The value is shared vocabulary.

### Headless component libraries (3+ canonical)

"Headless" = the library provides behavior, accessibility, and state — but no visual styling. The consumer brings the styles. This is the dominant pattern as of 2025-2026.

- **Radix UI** (Modulz / WorkOS, primary author Pedro Duarte / Diego Haz). Atom-to-organism range. Compound-component API. Tree-shakeable individual primitives (`@radix-ui/react-dialog`, `@radix-ui/react-popover`, `@radix-ui/react-select`). Strong accessibility (focus management, keyboard navigation, ARIA built in). The primary infrastructure for shadcn/ui's components.
- **React Aria** (Adobe, primary author Devon Govett). Behavior hooks (`useButton`, `useDialog`, `useSelect`) returning props to spread onto elements. Even more headless than Radix — Radix provides components, React Aria provides hooks. Trade-off: Radix is faster to adopt; React Aria gives finer-grained control. Adobe also ships React Aria Components (component-level wrapper).
- **Headless UI** (Tailwind Labs). Tighter scope than Radix / React Aria — focused on the common interactive primitives (`Menu`, `Listbox`, `Combobox`, `Dialog`, `Switch`, `Disclosure`, `Tabs`). Tailwind-friendly but not Tailwind-required.
- **Ariakit** (Diego Haz, formerly Reach UI). Behavior-first; supports both component and hook APIs. Heavy on extensibility.
- **shadcn/ui** (community / shadcn). Not a library — a copy-paste catalog of Radix-UI-wrapped components with Tailwind styles. The user owns the source after copy. Massively adopted; carries the trade-offs of being non-versioned (your copies don't update automatically).

### Compound components

A pattern where a parent component exposes named children that share implicit state via context. Pioneered by Kent C. Dodds (around 2017-2018); refined by Radix UI's primitives. Example shape:

```tsx
<Select>
  <Select.Trigger>...</Select.Trigger>
  <Select.Content>
    <Select.Item value="a">A</Select.Item>
    <Select.Item value="b">B</Select.Item>
  </Select.Content>
</Select>
```

Trade-offs vs. monolithic-prop API (`<Select options={[...]} value={...} onChange={...} />`):
- ✅ Composition: consumer can add custom JSX between the trigger and content.
- ✅ Slot-level customization: each named child can be styled or wrapped independently.
- ✅ Avoids "config object hell" for components with many options.
- ⚠️ Higher initial complexity; the API surface is larger.
- ⚠️ Order-of-children may carry implicit meaning, which can confuse consumers.

### Slot patterns

Two distinct senses:

1. **The Radix `asChild` pattern.** A compound component renders no element of its own; it forwards behavior to its child via `React.cloneElement`. Example: `<Button asChild><Link href="/foo">Click</Link></Button>` produces a `<Link>` styled and behaving as a button. Trade-off: powerful composition; can confuse consumers if the rendered element type changes unexpectedly.
2. **Named slots (Web Components, Vue, Svelte).** Component declares slots (`<slot name="header">`); consumer fills them by name. React's `children` is a single anonymous slot; React's idiomatic alternative is named props (`<Card header={...} footer={...}>`).

### Polymorphic / `as` prop

A component that can render as different underlying elements via an `as` prop: `<Box as="section">`, `<Text as="h1">`, `<Button as="a" href="/foo">`. Trade-offs:
- ✅ Reusable across HTML element types without component proliferation (no need for `Box`, `Section`, `Article` versions).
- ⚠️ TypeScript complexity is high; carrying through props is non-trivial.
- ⚠️ Easy to break accessibility (`<Button as="div">` produces a non-button-shaped button).

The canonical TypeScript pattern is documented in the React community (Lee Robinson's blog; Sébastien Lorber's posts). Chakra UI and Stitches' inventor (modulz/stitches) carried it through to production-grade APIs. Radix uses `asChild` instead of `as` precisely because `as` is hard to type cleanly.

### Controlled vs uncontrolled

A component that holds its own state internally is **uncontrolled** (`<input>` with no `value` prop just remembers what was typed). When the consumer provides `value` AND `onChange`, the component becomes **controlled** (consumer owns the state).

The discipline:
- Components that have mutable state should support both modes.
- Controlled mode is enabled when the consumer provides `value` (and a corresponding setter); uncontrolled mode is the default.
- For uncontrolled, accept a `defaultValue` prop for initial state. NEVER tie initial state to `value` — that surprises consumers when `value` changes via re-render.

React's primitive `<input>` is the model. Headless libraries (Radix, React Aria) follow the same convention rigorously.

### Ref forwarding

A component that wraps an underlying DOM element should accept a `ref` and forward it. In React 19, this is implicit — `forwardRef` is no longer required; `ref` is a normal prop. In React 18 and earlier, `React.forwardRef` is the canonical mechanism.

Why it matters: consumers using imperative APIs (`.focus()`, measuring with `ResizeObserver`, attaching to a `Portal`) need access to the underlying DOM node. Components that swallow refs make these use-cases impossible.

### Prop API design

Conventions across mature design systems:

1. **`variant` + `size` for component shapes.** `<Button variant="primary" size="lg">`. Two orthogonal axes; usually 2-5 values each. Avoids "every combination becomes a different component."
2. **Boolean props default-falsy.** `disabled`, `loading`, `required`. The absence of the prop means the default state. Avoid `enabled={true}` — confusing default.
3. **Consistent naming across the system.** `onClick`, `onChange`, `onValueChange`; `isOpen` vs `open`; `defaultValue` vs `value`. Pick a convention and apply it system-wide.
4. **`children` as the primary content slot.** When a single slot suffices, use `children` rather than a `content` or `text` prop. Reserve named props for additional slots.
5. **Spread the remaining props to the root element.** `<Button {...rest}>` so the consumer can pass `aria-*`, `data-*`, `id`, etc. without explicit prop declarations.

## Sources

- **Brad Frost, *Atomic Design*** (atomicdesign.bradfrost.com; published as a book in 2016). The canonical reference for the 5-tier model.
- **Radix UI documentation** (radix-ui.com) — primitives, compound-component patterns, `asChild` slot pattern.
- **React Aria documentation** (react-spectrum.adobe.com/react-aria) — behavior-hook API; the most rigorous accessibility-first headless library.
- **Headless UI documentation** (headlessui.com) — Tailwind Labs's focused headless library.
- **Ariakit documentation** (ariakit.org) — Diego Haz's component-and-hook headless library.
- **Kent C. Dodds on compound components** (kentcdodds.com) — the canonical pattern explanation.
- **Sébastien Lorber on polymorphic components** (sebastienlorber.com / the React community) — the canonical TypeScript-pattern reference.
- **shadcn/ui** (ui.shadcn.com) — the dominant Radix-based component catalog.
- **React docs on forwarding refs** (react.dev) — the canonical mechanism.

## Acceptance-criteria check

| AC | Target | Status |
|---|---|---|
| Names atomic design's 5 tiers with one example each | 5 | ✅ Atoms (Button); Molecules (SearchBar); Organisms (Header); Templates (DashboardTemplate); Pages (OrdersPage) |
| Names 3+ headless component libraries with their canonical pattern | 3+ | ✅ 5 (Radix UI, React Aria, Headless UI, Ariakit, shadcn/ui) with each pattern explained |
| Identifies compound + slot + polymorphic + controlled/uncontrolled + ref + prop API patterns each with one example | required | ✅ Each pattern with concrete example and trade-off discussion |
| Cites 3+ specialist authors | 3+ | ✅ Brad Frost, Kent C. Dodds, Sébastien Lorber, Diego Haz, Devon Govett |

Acceptance-criteria check: **satisfied.**

## Notes for Synthesis and per-layer Design

1. **Atomic design as mental model, not file structure.** The KB content should be clear about this — many teams have failed by treating Frost's tiers as a folder taxonomy.
2. **The headless trend is dominant.** As of 2025-2026, the standard recommendation for new design systems is: build on Radix UI primitives (or React Aria hooks for finer control); add styling via the project's tokens; ship as a thin wrapper layer. The KB content should be opinionated about this.
3. **React 19's implicit ref forwarding** changes the canonical code shape. The KB content should default to React 19 conventions (no `forwardRef`) and note the legacy pattern as a footnote.
4. **`asChild` vs `as`** is a well-established design tension. Radix's choice (asChild) is the more typesafe modern recommendation; the KB content can recommend it while documenting `as` for completeness.
5. **Prop API conventions** are dependent on the system's broader naming discipline. The KB content can establish the *categories* of decisions (variant/size; boolean naming; `children` primacy; spread to root) without dictating specific names — those are per-system choices.
