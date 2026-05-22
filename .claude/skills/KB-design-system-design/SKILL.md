---
name: kb-design-system-design
description: >-
  Design knowledge for design-system architecture — the discipline of
  organizing visual decisions, components, and patterns for reuse at scale.
  Covers the three-tier token model (primitive → semantic → component) with
  concrete mappings from Carbon, Material 3, Primer, and Salesforce Lightning;
  the W3C Design Tokens Community Group spec (DTCG); theming patterns
  (CSS custom properties as the modern default; Style Dictionary as a
  polyglot transformer; CSS-in-JS theme contexts as a legacy pattern);
  governance discipline (semver for design systems, scope boundaries between
  tokens / components / patterns). Always preloaded by `design-frontend` and
  `design-composer` alongside the other 3 design-side KBs.
allowed-tools: Read, Grep, Glob
---

# KB-design-system-design — Design System Architecture

## Contents

- [x] When this KB is loaded
- [x] What "design system" means at the Design layer in this project
- [x] The three durable concerns
- [x] Lookup chains by question type
- [x] Related KBs

## When this KB is loaded

This KB is always preloaded by:

- `design-frontend` — the per-layer Design agent for the Frontend layer.
- `design-composer` — the cross-layer Design fan-in agent.

It is consulted when the feature's design surface involves:

- Design tokens (creating new tokens; renaming existing tokens; deciding what should be a token vs a hardcoded value).
- Theming (adding light/dark/brand variants; supporting white-label clients; runtime theme switching).
- Design-system scope (deciding what belongs at the system level vs the application level).
- Versioning a design system (semver decisions; breaking changes; migration paths).
- Design-system tooling (Style Dictionary; Theo; Token Studio; Tokens Studio for Figma).

It is NOT consulted for:

- The specific VALUES of visual decisions (those go to `KB-visual-design` — type scales, color palette values, motion timings).
- Component implementation patterns (those go to `KB-component-architecture-design`).
- Interaction flow design (`KB-ux-design`).

The overlap with `KB-visual-design` is intentional: this KB covers HOW visual decisions are organized for reuse; that KB covers WHAT good visual decisions look like.

## What "design system" means at the Design layer in this project

A design system in this KB is **the architectural discipline of organizing design decisions for reuse**. Three observable artifacts: a token system (the values); a component library (the structures); a pattern library (the compositions).

It is NOT:

- A component library alone. A component library without tokens is decoupled from the underlying visual decisions; updating a color requires updating every component.
- A Figma file alone. A Figma file is the design source; the engineered design system is the code expression of those decisions. Both matter; they're not the same thing.
- A style guide. A style guide documents decisions for humans; a design system encodes them for machines (tokens consumed by code; components consumed by applications).
- A universal solution. Design systems serve a defined scope (one product; one product family; one company). Trying to design a design system that serves "all possible products" produces a useless lowest-common-denominator system.

## The three durable concerns

### 1. Tokens — `references/tokens.md`

The three-tier token model: primitive → semantic → component. With concrete mappings showing how Carbon, Material 3, Primer (GitHub), and Salesforce Lightning each organize their token systems. The W3C Design Tokens Community Group (DTCG) format specification for interoperable token files. Tooling: Style Dictionary; Theo; Tokens Studio.

The dominant failure mode this discipline addresses: tokens at one level only (just primitives, or just component-keyed). Each level serves a distinct purpose; collapsing levels eliminates the system's ability to evolve.

### 2. Theming — `references/theming.md`

How themes (light/dark/brand variants/density) consume the token system. CSS custom properties as the modern default (browser-native; runtime-swappable; performant). Style Dictionary as the polyglot transformer (generates CSS, JS, iOS, Android from one source). CSS-in-JS theme contexts as a pattern that predates CSS variables (still in some codebases; legacy default).

### 3. Governance — `references/governance.md`

Versioning discipline (semver applied to design systems). Scope decisions (when a pattern belongs in the system vs in the application). Migration discipline (breaking changes; codemod-supported migrations; deprecation cycles). Communication discipline (changelogs; ADRs for design system decisions).

## Lookup chains by question type

- **"What should be a token?"** → `references/tokens.md` → three-tier rules.
- **"How are dark mode and light mode organized?"** → `references/theming.md` → theming patterns.
- **"Should this component live in the design system?"** → `references/governance.md` → scope rules.
- **"How do we change a token without breaking consumers?"** → `references/governance.md` → semver + migration.
- **"What format should our tokens be in?"** → `references/tokens.md` → DTCG + tooling.

## Related KBs

- **`KB-visual-design`** — the values that flow into tokens. This KB names HOW tokens are organized; that KB names WHAT good values are.
- **`KB-component-architecture-design`** — components consume tokens. The component patterns (compound, slot, polymorphic) shape how tokens are exposed for customization.
- **`KB-ux-design`** — patterns the design system codifies (form patterns, navigation patterns, feedback patterns) encode UX decisions for reuse.
- **`KB-frontend-design`** — the broader frontend discipline. Design-system architecture is one lens among several in `KB-frontend-design`; this sibling KB elaborates.
- **`KB-storybook-platform`** — where the design system becomes visible and testable. Storybook documents tokens (themes addon); surfaces components (stories per component); tests visual regressions (Chromatic).
