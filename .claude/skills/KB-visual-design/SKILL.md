---
name: kb-visual-design
description: >-
  Design knowledge for visual discipline — type, color, space, motion, and
  the aesthetic dimensions that distinguish considered interfaces from
  defaulted ones. Covers type scales and pairing systems, OKLCH/APCA-era
  color discipline, 8pt and 4pt spatial grids, motion systems (Material 3,
  Apple HIG, Disney 12), responsive and density-spectrum frameworks. Includes
  anti-slop discipline (references/anti-slop.md) — naming the AI-default
  aesthetic signatures (system-font convergence; Inter/Roboto/Space Grotesk
  defaults; purple-on-white gradients) so the design layer can recognize and
  refuse them. Always preloaded by `design-frontend` and `design-composer`
  alongside the other 3 design-side KBs.
allowed-tools: Read, Grep, Glob
---

# KB-visual-design — Visual Design

## Contents

- [x] When this KB is loaded
- [x] What "visual design" means at the Design layer in this project
- [x] The four durable surfaces
- [x] Anti-slop discipline
- [x] Lookup chains by question type
- [x] Source dependencies
- [x] Related KBs

## When this KB is loaded

This KB is always preloaded by:

- `design-frontend` — the per-layer Design agent for the Frontend layer.
- `design-composer` — the cross-layer Design fan-in agent.

It is consulted when the feature's design surface involves typography, color, spacing, motion, responsive behavior, density choices, or any decision about what the interface should LOOK like. It is NOT consulted for component architecture (`KB-component-architecture-design`), interaction flow (`KB-ux-design`), or design-system-level token architecture (`KB-design-system-design` — that KB covers HOW tokens are organized; this KB covers WHAT good token VALUES are).

The overlap with `KB-design-system-design` is intentional and bounded: this KB names good visual decisions; the design-system KB names how to encode those decisions as tokens for reuse.

## What "visual design" means at the Design layer in this project

Visual design in this KB is **the discipline of considered aesthetic choices**. Not "making it pretty" — making intentional, defensible decisions about type, color, space, and motion that serve the product's communicative goals.

It is NOT:

- A pure styling exercise. Visual decisions encode information: hierarchy, status, mood, brand. "It looks fine" without articulating what it COMMUNICATES is undisciplined.
- Brand identity work. Brand identity (logo, voice, color palette ownership) is upstream of this KB; this KB applies brand decisions to interface contexts.
- Marketing-style motion. Hero scroll animations, parallax effects, and product-page motion are out of scope. This KB covers UI motion (state transitions, feedback motion, affordance motion).
- Pedagogical introduction. Senior practitioner voice; the audience is the design-agent network and the engineers reading their outputs.

## The four durable surfaces

### 1. Type, color, space — `references/type-color-space.md`

The three primary surfaces of visual design. Each carries hard-won discipline:

- **Type.** Type scales (modular; Material 3; fluid clamp); font pairing; reading line lengths; line height ratios; font loading discipline. The dominant failure mode is system-font defaults (see anti-slop).
- **Color.** Color spaces (HSL is legacy; LCH and OKLCH are perceptually uniform); accessibility (APCA is the successor to WCAG contrast); semantic color systems; dark-mode-as-first-class.
- **Space.** 8pt and 4pt grids; spacing scales (linear vs geometric); component density; iconography sizing.

### 2. Motion — `references/motion.md`

UI motion systems. Material 3 motion, Apple Human Interface Guidelines motion principles, Disney's twelve principles of animation as applied to UI. Cubic-bezier easing curves with semantic names. `prefers-reduced-motion` as a first-class accommodation, not a footnote.

### 3. Responsive and density — `references/responsive.md`

Breakpoint frameworks; container queries (now broadly available); fluid type with `clamp()`; responsive vs adaptive trade-offs; density spectrum (comfortable, default, compact).

### 4. Anti-slop — `references/anti-slop.md`

The naming and refusal of AI-default aesthetic signatures. Cites the Anthropic `frontend-design` skill upstream as authoritative; this file adds project-specific framing and pedagogical markers. The marker-heavy reference file in this KB.

## Anti-slop discipline

A particular failure mode of AI-assisted design merits explicit framing. Models trained on the web's surface tend to converge on a narrow visual default: system fonts (San Francisco, Segoe UI, Roboto, Inter); a small set of "modern-looking" fonts (Space Grotesk has become a tell); purple-on-white gradients; a particular shade of subdued grayscale neutral. The result is a recognizable AI-default look — interfaces with no aesthetic identity, distinguishable from each other only by content.

The Anthropic `frontend-design` skill (released November 2025) names this pattern explicitly and provides the most authoritative anti-slop reference available. `references/anti-slop.md` in this KB CITES that skill, summarizes its taxonomy, and adds project-local framing. The goal: when the design agent encounters a feature that drifts toward the AI-default aesthetic, it has named tools to refuse.

The discipline is NOT anti-default-fonts or anti-Inter; it's anti-defaulting. A project deliberately choosing Inter as a brand decision is fine. A project using Inter because the agent reached for the default is the failure mode.

## Lookup chains by question type

- **"What font should this use?"** → `references/type-color-space.md` → type scale + pairing decisions; cross-check `references/anti-slop.md` for AI-default tells.
- **"What color should this be?"** → `references/type-color-space.md` → color spaces + semantic systems.
- **"How much spacing between these elements?"** → `references/type-color-space.md` → spatial grid section.
- **"How should this animation feel?"** → `references/motion.md` → motion system + easing curves.
- **"How does this respond to viewport changes?"** → `references/responsive.md` → breakpoints + container queries + fluid type.
- **"Is this drifting into AI-default territory?"** → `references/anti-slop.md` → named signatures + calibration exemplars.

## Source dependencies

This KB depends on one external upstream that may evolve:

- **Anthropic `frontend-design` skill** — located at `/mnt/skills/public/frontend-design/SKILL.md` in this project's environment. Released 2025-11-12 by the Anthropic Cookbook authors. Names AI-slop signatures and the five aesthetic dimensions. `references/anti-slop.md` cites it as the primary source; project-local additions are framing and pedagogical markers.

When the upstream skill evolves, `references/anti-slop.md` may need refresh. The refresh is non-destructive — additions only — per ADR-0005 supersession discipline.

## Related KBs

- **`KB-design-system-design`** — encodes visual decisions as tokens for reuse. This KB names what good values are; that KB names how to organize them.
- **`KB-ux-design`** — visual decisions support UX decisions. A beautifully-typed interface where users can't complete tasks is a UX failure, not a visual success.
- **`KB-component-architecture-design`** — components are the surface visual design renders into. Component patterns (compound, slot, polymorphic) shape what visual customization is possible.
- **`KB-frontend-design`** — the broader frontend discipline (state, perf, errors, typing, framework grain, a11y baseline). Visual design is one lens among several in `KB-frontend-design`; this sibling KB elaborates.
- **`KB-storybook-platform`** — where visual decisions become visible for review. Stories render components with their visual decisions intact.
