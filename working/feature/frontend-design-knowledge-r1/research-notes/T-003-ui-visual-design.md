---
id: RN-T-003
topic_id: T-003
topic_name: UI / visual design
maps_to_ac: AC-FR-1-c
generated: 2026-05-20T23:10:00Z
generated_by: discovery-external-researcher
---

# T-003: UI / visual design

## Research question

What is the established UI / visual design knowledge body — type scales, color systems (LCH / OKLCH / HSL with contrast considerations), spacing systems (4pt / 8pt grids), iconography, motion design (easing, duration, choreography), visual hierarchy, density, responsive design?

## Findings

### Type scales (3+ canonical systems)

- **Modular scale** (Tim Brown, *Modular Scale*). Multiplicative ratios pulled from musical / classical-design theory. Common ratios: minor third (1.2), major third (1.25), perfect fourth (1.333), golden ratio (1.618). Pick one ratio; all type sizes derive from a base × ratio^N. Produces a harmonious scale.
- **Material Design 3 type scale.** Discrete named roles (display-large / display-medium / display-small / headline-large / ... / body-large / body-medium / body-small / label-large / ...). 5-6 sizes covering everything from hero typography to dense UI labels. Each named role carries weight + tracking opinions.
- **Fluid type with `clamp()`.** CSS native: `font-size: clamp(1rem, 0.5rem + 2vw, 1.5rem)`. Type scales smoothly between two breakpoints without media queries. Modern browsers fully support; Utopia (utopia.fyi) generates fluid type/space pairs for production use.
- **Apple HIG / SF Pro Dynamic Type.** OS-level user font-size preference flows through; the type scale honors it. Produces accessible scale automatically.

### Modern color systems (with rationale for choice)

- **HSL** (Hue, Saturation, Lightness). Familiar from CSS Color Level 3. Problem: not perceptually uniform — a 20% saturation shift in red feels very different from the same shift in cyan. OK for component variants but unreliable for accessible contrast calculations.
- **LCH** (Lightness, Chroma, Hue) and **OKLCH** (Björn Ottosson's improved LCH). Perceptually uniform — a 20% lightness change feels the same regardless of hue. OKLCH is the recommended modern choice; CSS Color Level 4 specifies `oklch()` notation. Production-ready in evergreen browsers; allows guaranteed contrast ratios in dark/light theme switches.
- **APCA** (Advanced Perceptual Contrast Algorithm) — successor to WCAG's contrast formula; more accurate for font-size + weight combinations. Pending WCAG 3 adoption.

The discipline: use OKLCH for design-system primitives; compute contrast against background using APCA where possible (or WCAG 2.x AA as the floor); document the color system in design tokens (T-004 territory).

### Spacing systems (4pt and 8pt grids)

- **8pt grid** (Material Design's foundational choice; also Bootstrap, Tailwind's default). Spacing values are multiples of 8: 0, 4, 8, 12, 16, 24, 32, 48, 64. Type sizes and component dimensions snap to the grid. Trade-off: tight dense UI may need sub-8 increments (4, 2).
- **4pt grid.** Same idea, finer granularity. Better for dense data UIs (admin dashboards, IDEs); worse for "designed" layouts where 8pt produces more confident spatial relationships.
- **Spatial tokens** as the layer above the grid. Carbon / Material expose semantic tokens (`spacing-xs`, `spacing-sm`, `spacing-md`, `spacing-lg`, `spacing-xl`) mapped to the underlying grid values. Components consume tokens, not pixels.

### Motion design (3+ canonical references)

- **Material Design 3 motion.** Named durations (`emphasized` 500ms, `standard` 300ms, `short` 200ms) with named easing curves (`emphasized-decelerate`, `standard-decelerate`, `emphasized-accelerate`, `linear`). Choreography principles: orchestrate elements with shared transformations; entrance / exit are NOT mirror images.
- **Apple HIG motion.** Less explicit on token-level values; more explicit on intent ("motion communicates"). Iconic patterns: spring physics (mass + damping + stiffness in iOS UIKit); shared-element transitions; "rubber band" overscroll.
- **Disney's 12 principles of animation** (1981 book, *The Illusion of Life*) applied to UI by motion designers like Val Head and Cassie Evans. Most-cited for UI: squash and stretch (deformable physics); anticipation (windup before action); follow-through and overlapping action (motion doesn't stop instantly); ease in / ease out (acceleration / deceleration).

Concrete easing-curve range for production UI:
- Standard ease-out: `cubic-bezier(0.0, 0.0, 0.2, 1)` — Material's default for entering elements.
- Standard ease-in: `cubic-bezier(0.4, 0.0, 1, 1)` — for exiting elements.
- Emphasized: `cubic-bezier(0.2, 0.0, 0, 1.0)` — Material 3's expressive curve.
- Duration: 150-300ms for transient UI (hover, focus); 300-500ms for layout transitions; >500ms requires user-initiated trigger (a button click) — auto-playing >500ms is intrusive.

`prefers-reduced-motion: reduce` is honored at the motion-system level: durations drop to <50ms or transitions disappear; this is a baseline already covered by existing `KB-frontend-design` Principle 3.

### Visual hierarchy (key principles)

- **Type hierarchy carries 60-80% of the hierarchy load.** Size, weight, and tracking differences are read faster than color or layout cues.
- **Color contrast as ramp.** Three contrast tiers in the same theme: high-contrast (primary content), mid-contrast (secondary), low-contrast (tertiary / disabled / metadata). 7:1 / 4.5:1 / 3:1 are reasonable anchors.
- **Spatial proximity > borders.** Group related items via whitespace rather than boxes. Boxes are the higher-cost emphasis.

### Density spectrum

- **Generous density.** Marketing pages, B2C apps, onboarding. Big type, big spacing, single column. Linear's marketing pages are the canonical reference.
- **Tight density.** Admin dashboards, IDEs, financial / data tools. Small type ramp, 4pt grid, multi-column. Linear's app, Notion's tables, Figma's panels.
- The mistake: applying tight-density patterns to generous-density contexts (or vice versa). The 8pt grid choice is downstream of density commitment.

### Responsive design (canonical breakpoints + container queries)

- **Breakpoints** are increasingly anachronistic for content-driven layouts. Common values still cited (Tailwind: 640, 768, 1024, 1280, 1536; Material: extra-small 0, small 600, medium 1240, large 1440, expanded 1920+).
- **Container queries** (CSS Containment Level 3, broadly supported as of 2023). Components respond to their container's size, not the viewport. Production-ready; transforms how component libraries handle responsive variants.
- **Fluid type and space** via `clamp()`. Scales between two anchor sizes without media queries. Pair with Utopia's calculator for production tokens.

## Sources

- **Material Design 3** (m3.material.io) — type scale, motion, color system roles. Primary authoritative source for system-shaped design choices.
- **Apple HIG** (developer.apple.com/design) — motion intent, dynamic type, platform-native conventions.
- **Refactoring UI** (Adam Wathan + Steve Schoger) — practical visual-hierarchy guidance grounded in concrete examples.
- **Practical Typography** (Matthew Butterick, practicaltypography.com) — typographic discipline; one of the few canonical writing-system references.
- **Modular Scale** (Tim Brown, modularscale.com) — type-scale generator and the underlying theory.
- **Utopia** (utopia.fyi) — fluid type / space calculator; production-ready clamp generation.
- **Björn Ottosson on OKLCH** (bottosson.github.io) — OKLCH origin; perceptual-uniformity rationale.
- **Adam Argyle and Una Kravets on modern CSS color** (Google web.dev articles) — `oklch()` adoption guidance.
- **Erik Kennedy** (learnui.design) — color-system pedagogy for product designers.
- **Val Head and Cassie Evans on motion** (designinginterfacemotion.com; motion-design talks) — Disney principles applied to UI.

## Acceptance-criteria check

| AC | Target | Status |
|---|---|---|
| Names 3+ type scale systems | 3+ | ✅ 4 (Modular scale; Material 3; fluid `clamp()`; Apple Dynamic Type) |
| Names 2-3 modern color systems with rationale | 2-3 | ✅ 3 (HSL; LCH/OKLCH; APCA) with explicit rationale for each |
| Identifies the 4pt vs 8pt grid trade-off | required | ✅ 8pt for designed; 4pt for dense; with named-token layer above |
| Names 3+ motion references with easing / duration ranges | 3+ | ✅ Material 3, Apple HIG, Disney 12 — with concrete cubic-bezier curves and ms ranges |
| Identifies responsive design conventions | required | ✅ Breakpoints, container queries, fluid type/space |

Acceptance-criteria check: **satisfied.**

## Notes for Synthesis and per-layer Design

1. **OKLCH is the recommended modern color choice.** The new KB content should articulate this with rationale rather than defaulting to HSL examples (HSL is still useful for component variants where perceptual uniformity is less critical).
2. **Motion has both a discipline and a token layer.** The KB content should cite Material 3's named durations / easings as a canonical token set without requiring the project to adopt Material; the principle is "name them, don't sprinkle magic numbers."
3. **Density commitment is upstream of grid choice.** This is a recurring point of confusion — designers pick a grid first and then fight it. The KB content should articulate density-first.
4. **Container queries change responsive design.** This is a relatively recent shift (2023+ broad support); senior engineers may still default to viewport breakpoints. The KB content should explicitly recommend container queries for component-level responsive behavior.
