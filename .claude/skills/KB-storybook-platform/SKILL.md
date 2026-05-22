---
name: kb-storybook-platform
description: >-
  Platform knowledge for Storybook — the open-source UI component workshop for
  authoring stories, running visual regression tests, and publishing component
  documentation. Covers Component Story Format (CSF3 default; CSF Factories as
  the typesafe v10 evolution), the canonical addons (essentials, controls,
  a11y, viewport, interactions, docs, themes, coverage), MDX documentation
  composition with Doc Blocks, Chromatic + `@storybook/test-runner` + Vitest
  for visual regression and interaction testing, and multi-package composition
  via `refs`. Loaded when a feature involves Storybook stories, addon
  configuration, MDX documentation, visual regression testing, or Storybook-
  level monorepo composition. Pairs with no design partner KB — design
  discipline for components lives in KB-component-architecture-design;
  Storybook is the platform that surfaces those components for review.
allowed-tools: Read, Grep, Glob, Edit, Write, WebFetch
---

# KB-storybook-platform — Storybook Platform Knowledge

## Contents

- [x] When this KB is loaded
- [x] Topology at a glance
- [x] Version state (Storybook 9 floor, Storybook 10 latest)
- [x] Story format spectrum (CSF2 → CSF3 → CSF Factories)
- [x] The five primitives (story, meta, args, parameters, decorators)
- [x] Addon model
- [x] Documentation model (MDX + Doc Blocks)
- [x] Testing model (Chromatic VRT, test-runner, Vitest)
- [x] Composition model (multi-package refs)
- [x] Lookup chains by question type
- [x] Related KBs

## When this KB is loaded

This KB is **model-invocable**, not always-preloaded. It is invoked when:

- A feature's Frontend layer authors Storybook stories (`*.stories.ts`, `*.stories.tsx`, `*.stories.mdx`).
- A feature adds or modifies Storybook addons or `.storybook/main.ts` / `.storybook/preview.ts` configuration.
- A feature integrates Chromatic, `@storybook/test-runner`, or Vitest with Storybook for visual regression or interaction testing.
- A feature establishes Storybook composition across multiple packages (design-system Storybook composed into a product Storybook via `refs`).
- A feature consumes Storybook's published static build (Storybook as documentation hosting).

It is NOT invoked when the feature's frontend work has no Storybook surface (component authoring without Storybook; pure runtime UI; non-component frontend changes). In those cases, `design-frontend` proceeds with `KB-frontend-design` + the design-side KBs (`KB-ux-design`, `KB-visual-design`, `KB-design-system-design`, `KB-component-architecture-design`) and skips this KB.

The invocation discipline is documented in `design-frontend.md`'s body section and in `design-composer.md`'s. Either agent can invoke this KB via `/skill kb-storybook-platform` when the Storybook trigger applies.

## Topology at a glance

Storybook surfaces a stack with five distinct layers:

| Layer | Artifact | Purpose |
|---|---|---|
| Config | `.storybook/main.ts` | framework, stories glob, addons list, features |
| Preview | `.storybook/preview.ts` | global decorators, parameters, themes |
| Stories | `*.stories.ts(x)`, `*.stories.mdx` | individual component variants |
| Addons | `@storybook/addon-*` packages | tooling: controls, a11y, viewport, interactions, docs |
| Output | `storybook-static/` build | published HTML/CSS/JS bundle for hosting |

The CLI: `storybook dev` (local server with HMR), `storybook build` (static production build), `storybook test` (test-runner). Frameworks: `@storybook/react-vite`, `@storybook/vue-vite`, `@storybook/svelte-vite`, `@storybook/web-components-vite`, etc. Vite-based; Webpack5-based legacy frameworks remain for older projects.

## Version state

| Version | Released | Key changes |
|---|---|---|
| **Storybook 10** | 2025-11-05 | ESM-only; ~29% lighter core; module automocking; typesafe CSF Factories (alpha → stable) |
| **Storybook 9** | 2025-06-04 | Vitest integration as first-class testing path; leaner core; substantial a11y addon upgrade |
| Storybook 8.5 | 2025-01-22 | Accessibility / testing / coverage refinements |
| Storybook 8.x | 2024 | Vite as default; portable stories; package consolidation |
| Storybook 7 | 2023-01 | CSF3 default; React 18 support; new docs architecture |

**Supported floor for this project: Storybook 9.** Storybook 10 is the recommended target for greenfield work. CSF3 is the broadly-deployed story format; CSF Factories is the typesafe successor introduced in Storybook 10. Migration tooling exists in both directions (CSF2 → CSF3 via `npx storybook migrate csf-2-to-3`; CSF3 → CSF Factories via `npx storybook automigrate csf-factories`).

A separate `Storybook MCP` (released 2026-03-26) integrates Storybook with AI agents for React; out of scope for this KB's v1 but worth noting as the project's forward direction matures.

## Story format spectrum

Component Story Format (CSF) has three versions; CSF3 is the current default, CSF Factories is the v10 evolution.

**CSF3** — the broadly-deployed format since Storybook 7 (Jan 2023). A story file exports a default object (meta) and named exports (stories). Stories are plain objects with `args`, `parameters`, `play`, etc. Type safety is achieved with TypeScript `satisfies` against `Meta<typeof Component>` / `StoryObj<typeof Component>`.

**CSF Factories** — Storybook 10's typesafe successor. Four factory functions form a typed chain: `defineMain` → `definePreview` → `preview.meta` → `meta.story`. Each step's return value carries the prior step's type information. The result: addon configuration, parameters, and globals are fully type-checked at story-write time. Migration is mechanical for most CSF3 files; the codemod is `npx storybook automigrate csf-factories`.

**CSF2** — the legacy format (named exports as functions returning JSX). Backwards-compatible in Storybook 7+. Migrate to CSF3 before adopting CSF Factories.

Authoring discipline: new stories should use CSF Factories where the project is on Storybook 10; CSF3 otherwise. Mixed-format files are not permitted (Storybook resolves per-file but mixing within a file is rejected by the compiler).

## The five primitives

Every story is composed of five primitives:

1. **`meta`** — the default export. Carries `title` (sidebar location), `component` (the component class/function under test), `args` (default props for all stories below), `argTypes` (control UI affordances + documentation hints), `parameters` (non-prop metadata: viewport, backgrounds, doc-page config), and `decorators` (wrapping functions providing context).
2. **`story`** — each named export. Overrides meta's `args`/`parameters`/`decorators`; adds story-specific `play` function for interactions.
3. **`args`** — the props passed to the component. Story-level args override meta-level args. Controls panel exposes these for runtime tweaking.
4. **`parameters`** — non-prop metadata. Common keys: `viewport.defaultViewport`, `backgrounds.default`, `docs.description`, `chromatic.disableSnapshot`.
5. **`decorators`** — higher-order components wrapping the story. Stack outermost to innermost. Used for theme providers, router providers, mock stores. Global decorators in `preview.ts`; per-meta and per-story decorators in the story file.

A `play` function is a sixth primitive when present: an async function executed after render with access to `canvasElement` and Storybook test utilities (`within`, `userEvent`, `expect` from `@storybook/test`). The interactions addon visualizes its steps; the test-runner runs it as a test.

## Addon model

Storybook is unopinionated by default; addons extend the surface. Each addon is an npm package with a Storybook plugin entry point that registers panels, decorators, or build hooks. Configuration: `.storybook/main.ts`'s `addons` array.

**Canonical addons** (the v1 KB's scope):

- **`@storybook/addon-essentials`** — bundles controls + actions + docs + viewport + backgrounds + toolbars + measure + outline. The baseline for most projects. Storybook 8.x split some of these out; check the version-specific docs for the current bundle.
- **`@storybook/addon-controls`** — manipulates `args` at runtime via the panel. Reads `argTypes` for control widget types (`select`, `boolean`, `text`, `range`, `color`, etc.).
- **`@storybook/addon-a11y`** — runs `axe-core` against the rendered story; surfaces violations in the panel. Storybook 9 substantially upgraded this addon's surface area.
- **`@storybook/addon-viewport`** — presets for common device viewports; integrates with `parameters.viewport`.
- **`@storybook/addon-interactions`** — visualizes `play` function steps; provides time-travel debugging.
- **`@storybook/addon-docs`** — auto-generates documentation pages with embedded stories; consumes `argTypes` for the props table.
- **`@storybook/addon-themes`** — toggles theme decorators (light/dark/brand variants) via the toolbar.
- **`@storybook/addon-coverage`** — instruments component code; reports coverage from story-driven testing.

Custom addons exist (Chromatic publishes one; story.to.design publishes one for Figma integration). Building a custom addon is documented at `storybook.js.org/docs/addons/writing-addons` and is out of scope for v1 of this KB.

For each canonical addon, the reference file `references/addons.md` carries the configuration shape, common parameters, and trade-offs.

## Documentation model (MDX + Doc Blocks)

Storybook supports `.mdx` files for documentation pages. The pattern: a Markdown file with embedded React-style component invocations from `@storybook/blocks`. Stories are referenced by import — not duplicated — so the documentation stays in sync with the story file.

Canonical Doc Blocks: `Meta`, `Story`, `Canvas`, `Controls`, `Source`, `Description`, `Subtitle`, `Primary`, `ArgTypes`, `Stories`. Each block reads from the story file's `meta` or named story exports.

The discipline: stories live in `*.stories.ts(x)` files (one file per component); MDX is the presentation layer (one or more MDX files per component for tutorial-style documentation; many components also use auto-generated docs without explicit MDX).

`references/docs.md` carries the full Doc Blocks API and decorator stacking patterns.

## Testing model

Three testing surfaces, increasingly integrated since Storybook 8:

- **Visual regression via Chromatic** — cloud-hosted; every PR snapshots all stories; UI diff review for visual changes. The dominant VRT solution for Storybook design systems. Integrates with GitHub/GitLab/Bitbucket. Configuration: `chromatic-cli` invocation in CI; per-story opt-out via `parameters.chromatic.disableSnapshot`.
- **Interaction testing via `@storybook/test-runner`** — local Playwright-based runner that executes `play` functions across all stories. Pairs with `axe-core` for a11y assertions.
- **Vitest integration** (Storybook 9+) — `npx storybook init` can scaffold a Vitest setup where `*.stories.ts(x)` files are test files; `play` becomes the test body. Collapses the test-runner/unit-test dichotomy for component-level tests.

Choosing among them: Chromatic for VRT (visual regressions); test-runner OR Vitest for interaction testing. Vitest is the newer recommendation when starting fresh; test-runner remains valid for established projects.

`references/testing.md` carries the configuration and CI integration patterns.

## Composition model

Storybook supports composing multiple Storybook instances into one navigable interface. Common topology: a design-system Storybook (deployed at one URL) composed into a product Storybook (deployed at another URL) via `refs`.

```ts
// .storybook/main.ts (consuming Storybook)
export default {
  refs: {
    'design-system': {
      title: 'Design System',
      url: 'https://design-system.example.com',
      expanded: false,
    },
  },
};
```

The consuming Storybook surfaces the referenced Storybook's stories in its sidebar. Useful for design-system documentation that lives in a separate repo or deployment.

`references/composition.md` covers the topology choices and trade-offs.

## Lookup chains by question type

- **"How do I write a story for X?"** → `references/story-format.md` → CSF3 default; CSF Factories if v10.
- **"Which addon should I add for Y?"** → `references/addons.md` → match Y to the canonical addon list.
- **"How do I document component Z?"** → `references/docs.md` → MDX + Doc Blocks.
- **"How do I test interactions / catch visual regressions?"** → `references/testing.md` → `play` + test-runner / Vitest / Chromatic.
- **"How do I share components across multiple Storybooks?"** → `references/composition.md` → `refs` in `main.ts`.

## Related KBs

- **`KB-component-architecture-design`** — the design-side discipline for components Storybook surfaces. Atomic design tiers; headless library patterns; compound/slot/polymorphic/controlled patterns. Storybook is where you make these components visible; the design KB tells you how to architect them.
- **`KB-visual-design`** — the visual design discipline informing what stories should LOOK like. Type / color / motion / spacing tokens flowing through to Storybook's themes addon.
- **`KB-design-system-design`** — the design-system-level concerns Storybook supports at scale. The composition model (`refs`) is the bridge: design-system Storybook documents tokens + base components; product Storybook composes it in.
- **`KB-frontend-design`** — the broader frontend discipline (state, perf, errors, typing, framework grain, a11y baseline). Storybook stories must respect these principles.
- **`KB-cc-platform` / `KB-cc-design`** — orthogonal; covers Claude Code primitives, not Storybook. Cited here only to clarify that Storybook is the platform for the design KBs to surface their work in.
