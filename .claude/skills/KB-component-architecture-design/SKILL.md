---
name: kb-component-architecture-design
description: >-
  Design knowledge for component architecture — how UI components are
  decomposed, structured, and composed for reuse. Covers Brad Frost's
  atomic design (atoms / molecules / organisms / templates / pages) as
  mental model and decomposition tool; the headless-library landscape
  (Radix, React Aria, Headless UI, Ariakit, shadcn/ui — what each commits
  to and what each leaves open); the canonical component patterns
  (compound, slot, polymorphic via `as`, controlled / uncontrolled,
  ref forwarding, prop API design). Always preloaded by `design-frontend`
  and `design-composer` alongside the other 3 design-side KBs.
allowed-tools: Read, Grep, Glob
---

# KB-component-architecture-design — Component Architecture

## Contents

- [x] When this KB is loaded
- [x] What "component architecture" means at the Design layer in this project
- [x] The three durable concerns
- [x] Lookup chains by question type
- [x] Related KBs

## When this KB is loaded

This KB is always preloaded by:

- `design-frontend` — the per-layer Design agent for the Frontend layer.
- `design-composer` — the cross-layer Design fan-in agent.

It is consulted when the feature's design surface involves:

- Decomposing UI into reusable components.
- Choosing between building from scratch vs adopting a headless component library.
- Designing a component's prop API.
- Deciding between compound, slot, polymorphic, or controlled/uncontrolled patterns.
- Managing component refs (forwarding; React 19 implicit ref).
- Building accessible custom controls (combobox; tree; tablist; dialog).

It is NOT consulted for:

- The values components consume (those go to `KB-visual-design` for raw values and `KB-design-system-design` for token architecture).
- User flows the components compose into (those go to `KB-ux-design`).
- Storybook integration for the components (`KB-storybook-platform`, when invoked).

## What "component architecture" means at the Design layer in this project

Component architecture in this KB is **the discipline of structuring UI components for reuse, composability, and a11y correctness**. The three observable concerns: how to decompose; what to build vs adopt; how to design the API.

It is NOT:

- A framework tutorial. React, Vue, Svelte, and others have different syntactic forms for the same patterns; this KB covers the patterns, citing examples mostly in React because React's documentation is the most extensive.
- A styling discipline. How components LOOK is `KB-visual-design`; how they're TOKENIZED is `KB-design-system-design`; how they're ARCHITECTED is this KB.
- A complete component library. The discipline names tradeoffs; the project's component library applies them.

## The three durable concerns

### 1. Atomic design — `references/atomic-design.md`

Brad Frost's five-tier mental model: atoms (foundational primitives), molecules (small functional groupings), organisms (substantial sections), templates (page-level layouts without content), pages (template + content). Useful as decomposition guidance; common misuse is treating it as file-structure prescription.

### 2. Headless libraries — `references/headless-libraries.md`

The current landscape of "headless" component libraries that provide behavior + accessibility without prescribing visual styling: Radix UI, React Aria (Adobe), Headless UI (Tailwind Labs), Ariakit, shadcn/ui (a vendoring approach rather than a library). For each: what they commit to; what they leave open; when to reach for which.

### 3. Canonical patterns — `references/patterns.md`

The patterns that distinguish considered component APIs: compound components (`<Tabs.Root><Tabs.List><Tabs.Trigger>`); slot patterns (Radix's `asChild` and React's `cloneElement`); polymorphic components (`as` prop); controlled vs uncontrolled; ref forwarding (React 19's implicit ref change); prop API design (boolean explosion vs variant unions).

## Lookup chains by question type

- **"How should I decompose this surface into components?"** → `references/atomic-design.md` → atomic tier framing.
- **"Should I build this or use a library?"** → `references/headless-libraries.md` → library landscape + trade-offs.
- **"How should the API of this component look?"** → `references/patterns.md` → compound vs slot vs polymorphic vs straightforward.
- **"How do I expose customization without exposing implementation?"** → `references/patterns.md` → slot pattern + asChild.
- **"How do I handle ref forwarding correctly?"** → `references/patterns.md` → ref forwarding (React 19 changes).
- **"How do I implement controlled and uncontrolled modes?"** → `references/patterns.md` → controlled/uncontrolled pattern.

## Related KBs

- **`KB-visual-design`** — what components LOOK like. Component architecture is the skeleton; visual design is the skin.
- **`KB-design-system-design`** — how components consume tokens and where they live in the system. Component patterns enable theming; the design-system architecture organizes the tokens.
- **`KB-ux-design`** — flows components compose into. A well-architected component that doesn't serve the user flow is wrong; flow drives component decomposition.
- **`KB-frontend-design`** — the broader frontend discipline. Component architecture is one lens among several; this sibling KB elaborates.
- **`KB-storybook-platform`** — where components are surfaced for review. Each component has at least one story; substantial components have many.
