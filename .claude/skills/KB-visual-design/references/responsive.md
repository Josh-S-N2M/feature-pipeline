# Responsive and Density

How interfaces adapt to viewport size and how density choices serve different audiences. The discipline has matured since the original 2010 "Responsive Web Design" piece — container queries, fluid type, and density-aware design extend what's possible.

## Contents

- [x] Breakpoint frameworks
- [x] Container queries
- [x] Fluid type and space
- [x] Responsive vs adaptive
- [x] Density spectrum
- [x] Touch target sizing
- [x] Patterns and anti-patterns
- [x] Cross-references

## Breakpoint frameworks

Most projects use 4-6 breakpoints organized around content needs (not specific devices). A common framework:

| Token | Min width | Typical use |
|---|---|---|
| `sm` | 640px | small tablets; large phones in landscape |
| `md` | 768px | tablets in portrait |
| `lg` | 1024px | tablets in landscape; small laptops |
| `xl` | 1280px | laptops; desktops |
| `2xl` | 1536px | wide desktops |

The Tailwind defaults follow this pattern; many projects adopt them. Custom breakpoints are appropriate when the content's needs differ — e.g., a data-heavy product UI may need a `data-table` breakpoint at 1100px (where columns become readable).

**Mobile-first authoring.** Default styles apply to the smallest viewport; `min-width` media queries layer in larger-viewport adjustments.

```css
.card {
  padding: 1rem;       /* mobile default */
}

@media (min-width: 768px) {
  .card {
    padding: 1.5rem;   /* tablet+ */
  }
}

@media (min-width: 1024px) {
  .card {
    padding: 2rem;     /* laptop+ */
  }
}
```

The inverse (desktop-first; `max-width` queries) works but produces more verbose CSS and harder-to-extend rules.

## Container queries

Container queries (now broadly available across modern browsers since 2023) base layout decisions on a containing element's size rather than the viewport. Solves the long-standing problem of components that should adapt to where they're placed, not just the window size.

```css
.card-container {
  container-type: inline-size;
}

.card {
  display: flex;
  flex-direction: column;
}

@container (min-width: 400px) {
  .card {
    flex-direction: row;
  }
}
```

The card stacks vertically when its container is narrow; lays out horizontally when its container is wide. The same card component in a wide sidebar vs a narrow grid cell renders differently — without knowing about the viewport.

Container queries enable truly portable components. A `<Card>` placed in a 3-column grid at desktop renders compactly; the same `<Card>` placed in a single-column dashboard panel renders expansively. The component author controls its behavior; the layout author controls the placement.

Use container queries for component-level responsive behavior; use media queries for page-level layout shifts (sidebars collapsing; navigation patterns changing).

## Fluid type and space

`clamp()` enables fluid scaling of type and space without breakpoint jumps:

```css
:root {
  /* Heading scales smoothly from 24px (320px viewport) to 48px (1280px viewport) */
  --font-size-h1: clamp(1.5rem, 0.95rem + 2.75vw, 3rem);

  /* Section spacing scales smoothly from 32px to 96px */
  --space-section: clamp(2rem, 1rem + 5vw, 6rem);
}
```

The middle argument (`0.95rem + 2.75vw`) is the linear interpolation. The math: at 320px viewport, `2.75vw = 8.8px`, plus `0.95rem ≈ 15.2px`, totals ~24px (the min). At 1280px viewport, `2.75vw = 35.2px`, plus 15.2px, totals ~50.4px (clamps to max 48px).

The Utopia calculator (`utopia.fyi`) generates fluid scales given min/max viewport and min/max size. A useful starting point.

Fluid scaling and breakpoints are not exclusive. A common pattern: fluid `clamp()` for typography sizes and large-scale spacing; breakpoints for layout shifts (single-column → multi-column).

## Responsive vs adaptive

**Responsive design.** One codebase; layouts shift fluidly with viewport. Modern default.

**Adaptive design.** Discrete layouts per viewport; the server (or client-side router) picks one. Common in early-2010s mobile-web era ("`m.example.com`"); rare today.

**Hybrid: feature flags by viewport class.** Some product UIs hide entire features at small viewports (a complex data table simplifies to a card list; a multi-column dashboard collapses to a tabbed interface). This is responsive in delivery but adaptive in feature surface.

The decision: responsive is the default; adaptive is appropriate when a single codebase truly cannot accommodate both viewports (e.g., a CAD tool whose mobile experience must be radically different).

## Density spectrum

Most products implement a single density. Mature product UIs offer a density spectrum — typically 3 levels:

| Level | Spacing scale multiplier | Audience |
|---|---|---|
| Comfortable | 1.25x base | First-time users; large viewports; touch |
| Default | 1.0x base | Most users |
| Compact | 0.75x base | Power users; data-heavy workflows; desktop |

Compact density is the differentiator for tools like Linear, Notion, Figma — power users want more visible information per pixel. Comfortable density serves accessibility (larger touch targets) and first-time users (less overwhelming).

Density choice typically lives in settings, applied as a CSS variable scale:

```css
:root[data-density='compact'] {
  --space-1: 3px;
  --space-2: 6px;
  --space-3: 9px;
  /* ... */
}

:root[data-density='comfortable'] {
  --space-1: 5px;
  --space-2: 10px;
  --space-3: 15px;
}
```

Components consume `--space-N` tokens; the density attribute swaps the entire scale.

Not every project needs three densities. Single-density is fine. But the density spectrum is the framing tool for thinking about who the audience is.

## Touch target sizing

WCAG 2.5.5 (Target Size Enhanced; AAA) requires 44×44 CSS pixels for touch targets; WCAG 2.5.8 (Target Size Minimum; AA in WCAG 2.2) requires 24×24. Apple HIG recommends 44pt; Material recommends 48dp.

The discipline:

- **Touch surfaces (mobile; tablet)** — interactive elements at minimum 44×44 px. Buttons should have adequate padding even when visually small.
- **Mouse surfaces (desktop with non-touch)** — can go smaller (24×24 acceptable; many interfaces use 32×32 as a default), but adjacent targets need spacing to prevent mis-clicks.
- **Pointer-agnostic surfaces (most modern web)** — default to the 44×44 minimum; use `@media (hover: hover)` to identify mouse-primary contexts where smaller is acceptable.

The `@media (hover: hover)` and `@media (pointer: fine)` queries detect pointer characteristics:

```css
.button {
  padding: 12px 16px; /* touch-friendly default */
}

@media (hover: hover) and (pointer: fine) {
  .button {
    padding: 8px 12px; /* tighter for mouse */
  }
}
```

`hover: hover` indicates a primary pointer that can hover (mouse, stylus). `pointer: fine` indicates a precise pointer (mouse, trackpad). Touch devices report `hover: none, pointer: coarse`.

## Patterns and anti-patterns

**Pattern: mobile-first, content-driven breakpoints.** Author for the smallest viewport; add breakpoints where the content demands them, not at arbitrary device boundaries.

**Pattern: container queries for component portability.** Components adapt to their placement; layout adapts to viewport. Separation of concerns.

**Pattern: fluid type for marketing; discrete sizes for product UI.** Marketing pages with display headlines benefit from fluid scaling. Dense product UIs benefit from predictable discrete sizes.

**Pattern: density as user preference.** When density is exposed, persist the choice in user settings. Don't default to one and ignore the spectrum.

**Anti-pattern: device-class breakpoints.** Breakpoints named `iphone-portrait` or `ipad-landscape` couple the design to specific devices. Devices change; viewport widths persist. Name breakpoints by purpose (`tablet`; `desktop`) or by size (`sm`; `md`; `lg`).

**Anti-pattern: hiding content at small viewports.** "Mobile users don't need this feature" is almost always wrong. Mobile users have the same goals as desktop users; the interface needs to adapt, not amputate.

**Anti-pattern: text smaller than 14px on touch devices.** Touch interaction requires legible text at glance distance. 14px minimum for body text on mobile; 16px is the safer default.

**Anti-pattern: ignoring landscape orientation on mobile.** Landscape mode has different constraints (short height; wide width). At minimum, test that flows work in landscape — many otherwise-polished UIs break on landscape phones.

## Cross-references

- **Type and spacing tokens responsive choices apply to:** see `type-color-space.md`.
- **Motion that pairs with layout shifts at breakpoints:** see `motion.md`.
- **Token architecture supporting density scales:** see `KB-design-system-design/references/tokens.md`.
- **MDN container queries:** `developer.mozilla.org/en-US/docs/Web/CSS/CSS_containment/Container_queries`.
- **Utopia fluid scale calculator:** `utopia.fyi`.
- **WCAG 2.2 target size:** `w3.org/TR/WCAG22/#target-size-minimum`.
