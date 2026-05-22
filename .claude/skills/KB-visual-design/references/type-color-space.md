# Type, Color, Space

The three primary surfaces of visual design. Each carries hard-won discipline accumulated across decades of typography research, color science, and grid practice. The framing here: name the discipline; describe the dominant failure mode; supply the durable patterns.

## Contents

- [x] Type scales
- [x] Type pairing
- [x] Reading lines and line-height
- [x] Font loading and FOIT/FOUT
- [x] Color spaces (legacy → modern)
- [x] Accessibility contrast (WCAG → APCA)
- [x] Semantic color systems
- [x] Dark mode as first-class
- [x] Spatial grids (8pt and 4pt)
- [x] Spacing scales
- [x] Iconography sizing
- [x] Cross-references

## Type scales

A type scale defines the discrete sizes used in the interface. Three durable approaches:

**Modular scale (multiplicative).** Pick a base size (commonly 16px) and a ratio (1.125 minor second; 1.2 minor third; 1.25 major third; 1.333 perfect fourth; 1.414 augmented fourth; 1.5 perfect fifth; 1.618 golden ratio). Each step multiplies the previous by the ratio. The minor-third (1.2) is the default for most product UIs — distinguishable steps without dramatic jumps.

```
Base 16px, ratio 1.2:
13px → 16px → 19px → 23px → 28px → 33px → 40px → 48px → 58px
```

**Material 3 type scale.** Google's Material Design 3 defines explicit semantic sizes: display-large, display-medium, display-small, headline-large, headline-medium, headline-small, title-large, title-medium, title-small, body-large, body-medium, body-small, label-large, label-medium, label-small. Each carries size, weight, line-height, and letter-spacing. Useful when a project wants a pre-tuned scale; restrictive when the project's voice differs from Material's.

**Fluid scale via `clamp()`.** CSS `clamp(min, preferred, max)` produces a size that scales with viewport width within bounds.

```css
/* Heading scales from 24px at narrow viewports to 48px at wide viewports */
font-size: clamp(1.5rem, 1rem + 2.5vw, 3rem);
```

The preferred value (`1rem + 2.5vw`) is the linear interpolation; the min and max clamp it. The fluid scale eliminates the breakpoint problem (a step from 24px to 32px at 768px is visually abrupt; the fluid version is continuous).

Most projects benefit from a HYBRID: a modular scale defines the semantic steps; fluid `clamp()` applies to the larger sizes (display, headline) so they breathe at wide viewports.

## Type pairing

Pairing two or more typefaces in one interface. The discipline:

- **Contrast intent.** Pair faces that contrast in voice (serif + sans; geometric + humanist; condensed + wide). Pairings that DON'T contrast (two sans-serifs with similar proportions) read as design errors rather than design choices.
- **Limit count.** Two faces is the default; three is unusual; four+ is almost always a mistake. Variable fonts collapse multiple "weights and widths" into one file, reducing the temptation to add more faces.
- **Hierarchy by family role.** Display face for headlines; reading face for body text; monospace for code. Don't blur the roles.

The AI-default reach for "Inter" or "Space Grotesk" as a universal sans-serif note: these are commonly-overused defaults named in the Anthropic anti-slop discipline — not blanket-prohibited, but reach-for-by-default is the signal warrants explicit justification when used. A brand choosing Inter for legitimate reasons (its metrics; its rendering on legacy systems) is fine; reaching for it because it's the default is the failure mode.

## Reading lines and line-height

Two rules that govern body text legibility:

- **Line length 45-75 characters per line.** Beyond 75ch, the eye loses its place returning to the next line; below 45ch, the rhythm fragments. CSS: `max-width: 65ch` on prose containers.
- **Line-height ratio 1.4-1.6 for body text.** Tighter (1.2) for display headings; looser (1.7+) for low-contrast settings. Line-height is unitless to inherit correctly: `line-height: 1.5` not `line-height: 24px`.

Display headlines can break both rules deliberately — short headlines at 1.1 line-height, full-width on the layout. The rules apply to reading text.

## Font loading and FOIT/FOUT

Web fonts load asynchronously; the browser must decide what to render before they arrive.

- **FOIT (Flash of Invisible Text).** Browser hides text until the font loads. User sees blank space, then text appears. Annoying.
- **FOUT (Flash of Unstyled Text).** Browser renders text in fallback font, then swaps to the loaded font. User sees text rendered in two fonts within a second. Slightly jarring but content-first.
- **FOFT (Flash of Faux Text).** Browser renders text in a synthetic style (faux-bold; faux-italic) before the real face loads. Worst of both worlds.

The modern default: `font-display: swap` in `@font-face`. Renders fallback immediately; swaps when web font arrives. Pair with a `font-family` declaration that puts a high-quality fallback first:

```css
@font-face {
  font-family: 'Brand Sans';
  src: url('/fonts/brand-sans.woff2') format('woff2');
  font-display: swap;
}

body {
  font-family: 'Brand Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
}
```

For critical above-the-fold text, preloading the font file (`<link rel="preload" as="font">`) shortens the swap window.

## Color spaces (legacy → modern)

**HSL (hue / saturation / lightness).** The dominant CSS color system since the late 2000s. Conceptually accessible but perceptually non-uniform — two colors with the same L value can look dramatically different in brightness. A pure yellow at L=50% looks far brighter than a pure blue at L=50%.

**LCH (lightness / chroma / hue).** Perceptually uniform; an L=50% color looks like medium brightness regardless of hue. CSS Color Module Level 4 supports `lch()` directly. Useful for generating accessible palettes — fixing L gives you reliable contrast against backgrounds.

**OKLCH.** A refinement of LCH using the Oklab color space. Better hue uniformity (purple-blue and red-blue don't shift hue when you adjust lightness). Becoming the default for design-system color palettes in 2025+. CSS: `oklch(70% 0.15 200)`.

```css
/* OKLCH ramp: same chroma + hue, varying lightness */
--blue-50:  oklch(96% 0.025 260);
--blue-100: oklch(92% 0.05 260);
--blue-500: oklch(60% 0.18 260);
--blue-700: oklch(45% 0.18 260);
--blue-900: oklch(25% 0.12 260);
```

The lightness values are perceptually meaningful — `blue-700` looks "70% as bright as white" reliably across the palette.

## Accessibility contrast (WCAG → APCA)

**WCAG 2 contrast formula** — the dominant accessibility contrast standard. Computes contrast ratio between foreground and background luminance. Requirements:

- 4.5:1 for normal text
- 3:1 for large text (18pt+ or 14pt+ bold)
- 3:1 for UI components and graphical objects (WCAG 2.1+)
- 7:1 for normal text at AAA

The formula has known weaknesses: it underweighs dark-text-on-light vs light-text-on-dark; it's not perceptually uniform across the hue spectrum.

**APCA (Accessible Perceptual Contrast Algorithm).** The successor under development for WCAG 3. Perceptually calibrated; produces a "Lc" value with different thresholds:

- 90+ for body text
- 75+ for small body text and content links
- 60+ for non-content text and large UI text
- 45+ for large display text and non-text UI

APCA accounts for text size and weight in the calculation (smaller / thinner text needs higher Lc). Tools: `apcacontrast.com`; the `apca-w3` npm package for programmatic checks.

For 2026 projects: WCAG 2.x for legal/regulatory compliance; APCA as the design tool for actual readability decisions. The two correlate broadly; APCA is more reliable at the edges (very dark backgrounds; small text).

## Semantic color systems

A semantic color system maps brand-derived colors to semantic roles. The pattern:

```
PRIMITIVE LAYER — raw color values (the palette)
  blue-50 → blue-900
  red-50  → red-900
  ...

SEMANTIC LAYER — role-keyed aliases
  --color-background     → gray-50
  --color-foreground     → gray-900
  --color-primary        → blue-600
  --color-primary-hover  → blue-700
  --color-destructive    → red-600
  --color-warning        → amber-500
  --color-success        → green-600
  ...

COMPONENT LAYER — component-keyed aliases
  --button-bg → --color-primary
  --button-bg-hover → --color-primary-hover
  ...
```

Components consume semantic tokens, not primitives. Themes (dark mode; brand variants) override semantic tokens. Components never need to change.

Full token architecture is in `KB-design-system-design/references/tokens.md`. This KB's role is naming the VALUES that flow into the architecture.

## Dark mode as first-class

Dark mode is not "the same UI with inverted colors." It's a separate set of color decisions:

- **Backgrounds shift from white to near-black.** True black (`#000`) causes excessive contrast; offset blacks (`oklch(15% 0 0)` to `oklch(20% 0 0)`) reduce eye strain.
- **Foreground shifts from black to off-white.** Pure white on dark causes glare; off-white (`oklch(95% 0 0)`) is more readable.
- **Accent colors desaturate.** A blue that pops against white may be too saturated against dark; reduce chroma by ~20% in dark mode.
- **Elevation reverses.** In light mode, raised elements use shadows; in dark mode, they use LIGHTER backgrounds (raised = brighter), since shadows are invisible.
- **Images and illustrations may need dark variants.** Logos with dark elements; illustrations with white backgrounds.

The OKLCH ramp pattern makes dark-mode generation tractable: invert the L scale (50 ↔ 900; 100 ↔ 800) while keeping C and H. Auditable; refinable.

## Spatial grids (8pt and 4pt)

Most design systems use a discrete spacing scale. Two common bases:

**8pt grid.** All spacing is a multiple of 8 (8, 16, 24, 32, 48, 64, 96, 128). Origin: legacy iOS guidelines. Coarse enough that the system is visible at a glance; works well for marketing pages and large-scale layouts.

**4pt grid.** All spacing is a multiple of 4. Allows finer adjustments (4, 8, 12, 16, 20, 24, 32, 40, 48, 64). The Material Design baseline; common for dense product UIs.

**Hybrid (4pt with 8pt cadence for major divisions).** Component-internal spacing on the 4pt grid; component-to-component spacing on the 8pt cadence. The default for most modern systems.

The spacing scale should be encoded as tokens (`--space-1` = 4px; `--space-2` = 8px; etc.). Free-form pixel values are a violation; "the design called for 13px" is a sign the system needs another scale step or the design needs adjustment.

## Spacing scales

The scale's progression. Two patterns:

- **Linear.** Each step adds a fixed amount: 4, 8, 12, 16, 20, 24. Predictable; allows fine adjustment. Default for most product UIs.
- **Geometric.** Each step multiplies by a factor: 4, 8, 16, 32, 64. Bigger jumps at the larger end. Default for marketing pages and dramatic layouts.

A common practical scale combines: linear in the small range (4, 8, 12, 16, 20, 24, 32), geometric beyond (48, 64, 96, 128, 192).

The scale should have a manageable number of steps — 8 to 12 total. More than that, choices proliferate and consistency erodes.

## Iconography sizing

Icons render at discrete sizes aligned to the grid:

- 16px — inline icons in text or controls
- 20px — slightly emphasized inline icons
- 24px — default standalone icon size
- 32px — feature icons
- 48px — display-scale icons (illustrative)

Icon stroke weight must adjust with size; a 1.5px stroke at 16px is too thin at 48px (looks fragile) and a 2px stroke at 48px is too heavy at 16px (looks crowded). Quality icon sets ship multiple weights or variable stroke widths.

The standard SVG viewBox for icon sets is `0 0 24 24`; icons authored at 24px scale cleanly to smaller and larger sizes if the stroke is in user units.

## Cross-references

- **Tokens encoding these values for reuse:** see `KB-design-system-design/references/tokens.md`.
- **Theming (light/dark/brand variants) consuming tokens:** see `KB-design-system-design/references/theming.md`.
- **Motion that pairs with visual decisions:** see `motion.md`.
- **Anti-slop signatures naming the AI-default tells:** see `anti-slop.md`.
- **Material 3 type scale documentation:** `m3.material.io/styles/typography/type-scale-tokens`.
- **OKLCH color picker (Evil Martians):** `oklch.com`.
- **APCA documentation:** `git.apcacontrast.com`.
