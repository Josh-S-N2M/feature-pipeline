# Tokens — Three-Tier Architecture

The durable architecture for design tokens organizes them into three tiers: primitive → semantic → component. Each tier serves a distinct purpose; conflating tiers produces systems that can't evolve. This document covers the three-tier model with concrete mappings from four mature design systems and the W3C DTCG interoperability format.

## Contents

- [x] The three tiers
- [x] Tier 1: primitives
- [x] Tier 2: semantic tokens
- [x] Tier 3: component tokens
- [x] How the tiers compose
- [x] Concrete mappings: Carbon, Material 3, Primer, Salesforce
- [x] The W3C DTCG format
- [x] Tooling (Style Dictionary, Theo, Token Studio)
- [x] Patterns and anti-patterns
- [x] Cross-references

## The three tiers

```
TIER 3: COMPONENT TOKENS    component-keyed (button-bg, button-text, ...)
                            ↑
                            consumes
                            ↑
TIER 2: SEMANTIC TOKENS     role-keyed (color-primary, color-background, ...)
                            ↑
                            consumes
                            ↑
TIER 1: PRIMITIVE TOKENS    value-keyed (blue-500, gray-100, space-4, ...)
```

Component tokens consume semantic tokens; semantic tokens consume primitive tokens; primitive tokens are leaf values. Themes (light/dark/brand) override at the semantic layer; primitive values are stable.

The tiers are NOT "small / medium / large" or "atom / molecule / organism." They're orthogonal abstraction layers in the resolution chain from raw value to component-specific usage.

## Tier 1: primitives

Primitive tokens are raw values without semantic meaning. The full palette, the full spacing scale, the full type scale.

```css
:root {
  /* Color primitives */
  --blue-50:  oklch(96% 0.025 260);
  --blue-100: oklch(92% 0.05 260);
  --blue-200: oklch(85% 0.08 260);
  --blue-300: oklch(78% 0.12 260);
  --blue-400: oklch(70% 0.15 260);
  --blue-500: oklch(60% 0.18 260);
  --blue-600: oklch(50% 0.20 260);
  --blue-700: oklch(40% 0.18 260);
  --blue-800: oklch(30% 0.15 260);
  --blue-900: oklch(20% 0.10 260);

  /* Spacing primitives */
  --space-0:  0;
  --space-1:  4px;
  --space-2:  8px;
  --space-3:  12px;
  --space-4:  16px;
  --space-5:  20px;
  --space-6:  24px;
  --space-8:  32px;
  --space-10: 40px;
  --space-12: 48px;
  --space-16: 64px;

  /* Type primitives */
  --font-size-xs:   12px;
  --font-size-sm:   14px;
  --font-size-base: 16px;
  --font-size-lg:   18px;
  --font-size-xl:   20px;
  --font-size-2xl:  24px;
  --font-size-3xl:  30px;
  --font-size-4xl:  36px;
}
```

Discipline at the primitive tier:

- **Comprehensive but bounded.** The palette includes every step needed across themes (you'll use different primitives in light vs dark mode); the spacing scale has 8-12 steps total; the type scale has 6-10 sizes.
- **Value-keyed, not role-keyed.** `--blue-500` is fine; `--blue-primary` is not (the latter conflates tiers).
- **Stable across themes.** A theme doesn't reassign primitives; it picks different primitives for the semantic layer.
- **No business meaning.** `--blue-500` carries no opinion about WHERE it should be used; that's the next tier's job.

## Tier 2: semantic tokens

Semantic tokens map roles to primitives. The role names the WHERE; the primitive provides the VALUE. Themes override this tier.

```css
:root {
  /* Surface colors */
  --color-background:           var(--gray-50);
  --color-background-secondary: var(--gray-100);
  --color-background-tertiary:  var(--gray-200);

  /* Foreground colors */
  --color-foreground:           var(--gray-900);
  --color-foreground-muted:     var(--gray-600);
  --color-foreground-subtle:    var(--gray-500);

  /* Brand */
  --color-primary:              var(--blue-600);
  --color-primary-hover:        var(--blue-700);
  --color-primary-active:       var(--blue-800);

  /* Semantic colors */
  --color-success:              var(--green-600);
  --color-warning:              var(--amber-500);
  --color-error:                var(--red-600);
  --color-info:                 var(--blue-500);

  /* Spacing semantics */
  --space-inset-sm:             var(--space-2);
  --space-inset-md:             var(--space-3);
  --space-inset-lg:             var(--space-4);
  --space-stack-sm:             var(--space-2);
  --space-stack-md:             var(--space-4);
  --space-stack-lg:             var(--space-6);

  /* Type semantics */
  --font-size-body:             var(--font-size-base);
  --font-size-caption:          var(--font-size-sm);
  --font-size-heading-1:        var(--font-size-3xl);
  --font-size-heading-2:        var(--font-size-2xl);
  --font-size-heading-3:        var(--font-size-xl);
}

:root[data-theme='dark'] {
  --color-background:           var(--gray-900);
  --color-background-secondary: var(--gray-800);
  --color-background-tertiary:  var(--gray-700);

  --color-foreground:           var(--gray-50);
  --color-foreground-muted:     var(--gray-300);
  --color-foreground-subtle:    var(--gray-400);

  /* Brand tweaked for dark mode (desaturate slightly) */
  --color-primary:              var(--blue-500);
  --color-primary-hover:        var(--blue-400);
  --color-primary-active:       var(--blue-300);
}
```

Discipline at the semantic tier:

- **Role-keyed, not value-keyed.** `--color-primary` is fine; `--color-blue` is not.
- **One source of truth per role.** Only ONE token represents "background"; reassigning components to use a different background means changing the token, not adding more tokens.
- **Themable.** Every semantic token's value is a primitive reference; theme overrides change the references, not the names.
- **Modest count.** 30-80 semantic color tokens is typical; 100+ usually means the semantic layer has become a duplicate of primitives.

## Tier 3: component tokens

Component tokens map component-specific roles to semantic tokens. Optional; many design systems skip this tier and let components consume semantic tokens directly. Useful when a component family has consistent internal token names that should be themable independently.

```css
:root {
  --button-primary-bg:           var(--color-primary);
  --button-primary-bg-hover:     var(--color-primary-hover);
  --button-primary-bg-active:    var(--color-primary-active);
  --button-primary-text:         var(--color-on-primary);
  --button-primary-border:       transparent;

  --button-secondary-bg:         var(--color-background);
  --button-secondary-bg-hover:   var(--color-background-secondary);
  --button-secondary-text:       var(--color-foreground);
  --button-secondary-border:     var(--color-border);
}
```

Discipline at the component tier:

- **Component-keyed.** `--button-primary-bg`; `--card-padding`; `--input-border-color`. The component name is the prefix.
- **Reaches for semantic tokens.** Not primitives. If a component token references a primitive directly (`--button-primary-bg: var(--blue-600)`), you've broken the chain.
- **Optional.** Add when a component genuinely needs independent theming or when component-keyed tokens improve documentation. Skip when semantic tokens suffice.
- **Per-state variants where state is part of the design system.** Button hover/active states are component tokens; button "disabled by feature flag" is not.

## How the tiers compose

A component CSS file consumes tokens from the tier closest to its purpose:

```css
/* Card component — consumes semantic tokens (no component tokens for Card) */
.card {
  background-color: var(--color-background-secondary);
  color: var(--color-foreground);
  padding: var(--space-inset-lg);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-sm);
}

/* Button component — consumes component tokens */
.button-primary {
  background-color: var(--button-primary-bg);
  color: var(--button-primary-text);
  padding: var(--space-inset-md) var(--space-inset-lg);
  border: 1px solid var(--button-primary-border);
}

.button-primary:hover {
  background-color: var(--button-primary-bg-hover);
}
```

The resolution chain when a theme changes:

```
Dark theme activated
  ↓
[data-theme='dark'] overrides --color-background-secondary → var(--gray-800)
  ↓
.card's background-color resolves to oklch(30% 0 0)  [gray-800 in dark mode]
  ↓
Card renders with dark background
```

No JavaScript involved. No component re-render. Browser handles the cascade.

## Concrete mappings: Carbon, Material 3, Primer, Salesforce

How four mature design systems organize their token tiers. Reading these in sequence shows the convergent pattern even with different naming conventions.

### IBM Carbon

Carbon Design System (IBM, since 2017) uses a strict three-tier model.

| Tier | Carbon naming | Example |
|---|---|---|
| Primitive | "Color tokens" — palette swatches | `$gray-90`; `$blue-60` |
| Semantic | "Theme tokens" — role-keyed | `$background`; `$text-primary`; `$interactive` |
| Component | "Component tokens" — component-keyed | `$button-primary-text`; `$accordion-background` |

Carbon ships four canonical themes (White, Gray 10, Gray 90, Gray 100) — light/dark variants at two intensities each. Themes override the theme-token tier; primitives and component tokens are stable.

Documentation: `carbondesignsystem.com/elements/color/tokens`.

### Material 3

Material Design 3 (Google, since 2022) calls primitives "reference tokens"; calls semantics "system tokens"; calls components "component tokens." Three tiers, different vocabulary.

| Tier | Material 3 naming | Example |
|---|---|---|
| Primitive | "Reference tokens" — palette + measurement values | `md.ref.palette.primary40`; `md.ref.typeface.brand` |
| Semantic | "System tokens" — applied design decisions | `md.sys.color.primary`; `md.sys.typescale.headline-large` |
| Component | "Component tokens" — per-component values | `md.comp.filled-button.container-color` |

Material 3 introduces dynamic color (palette derived from a user-selected source color); the reference-token palette is generated at runtime. The system-token mapping still applies; the component tokens still consume system tokens.

Documentation: `m3.material.io/foundations/design-tokens`.

### GitHub Primer

GitHub Primer (since ~2017; rewritten 2023) uses a two-tier model in practice — primitives and semantic functional tokens — with component-keyed tokens as a thin layer for specific components.

| Tier | Primer naming | Example |
|---|---|---|
| Primitive | "Base scales" | `scale.gray.6`; `scale.blue.5` |
| Semantic | "Functional tokens" — role + state | `fgColor.muted`; `bgColor.accent.emphasis` |
| Component | (sparse) | `button.primary.bgColor.rest` |

Primer's semantic tier carries state in the name (`-rest`, `-hover`, `-active`, `-disabled`, `-selected`). This expands the token count (8-10x more semantic tokens than Carbon) but eliminates the need for state-specific component tokens.

Documentation: `primer.style/foundations/primitives`.

### Salesforce Lightning

Salesforce Lightning Design System (since 2015; updated continuously) was an early adopter of the W3C DTCG format. Three tiers.

| Tier | Lightning naming | Example |
|---|---|---|
| Primitive | "Global tokens" — raw values | `BRAND_PRIMARY` (a specific blue hex) |
| Semantic | "Alias tokens" — role mappings | `COLOR_TEXT_DEFAULT`; `COLOR_BACKGROUND_BRAND` |
| Component | "Component tokens" — per-component | `BUTTON_COLOR_BACKGROUND_PRIMARY` |

Lightning publishes tokens in multiple platform formats (CSS, JSON, iOS, Android) generated from a single source via Theo. The three-tier model maps cleanly across platforms; what changes is the syntax.

Documentation: `lightningdesignsystem.com/design-tokens`.

## The W3C DTCG format

The W3C Design Tokens Community Group standardizes a JSON format for design tokens. The format enables interoperability — tokens authored in Figma's Tokens Studio can flow to code via Style Dictionary; tokens authored in code can be exported back to Figma.

```json
{
  "color": {
    "blue": {
      "500": {
        "$type": "color",
        "$value": "#3B82F6"
      },
      "600": {
        "$type": "color",
        "$value": "#2563EB"
      }
    }
  },
  "space": {
    "1": { "$type": "dimension", "$value": "4px" },
    "2": { "$type": "dimension", "$value": "8px" }
  },
  "color-background": {
    "$type": "color",
    "$value": "{color.gray.50}"
  },
  "color-primary": {
    "$type": "color",
    "$value": "{color.blue.600}"
  }
}
```

Key DTCG conventions:

- `$type` declares the token type (color, dimension, fontFamily, shadow, etc.).
- `$value` is the raw value; alias values use `{path.to.token}` syntax.
- Nested objects create paths (the path is the canonical token name).
- The format supports composite types (shadow tokens with x/y/blur/spread/color; typography tokens with family/size/weight/lineHeight).

DTCG is stable enough for production use. Most modern tooling (Style Dictionary v4+; Token Studio; Specify) supports DTCG natively.

Spec: `design-tokens.github.io/community-group/format`.

## Tooling (Style Dictionary, Theo, Token Studio)

Three tools commonly used for token pipelines:

**Style Dictionary (Amazon, open source).** Transforms DTCG-format JSON into platform-specific outputs (CSS variables, JS modules, iOS Swift, Android XML, etc.). Configuration:

```js
// style-dictionary.config.js
module.exports = {
  source: ['tokens/**/*.tokens.json'],
  platforms: {
    css: {
      transformGroup: 'css',
      buildPath: 'build/css/',
      files: [{ destination: 'tokens.css', format: 'css/variables' }],
    },
    js: {
      transformGroup: 'js',
      buildPath: 'build/js/',
      files: [{ destination: 'tokens.js', format: 'javascript/es6' }],
    },
  },
};
```

Style Dictionary v4 added native DTCG support. The default for new projects.

**Theo (Salesforce, open source).** Predates Style Dictionary; still used by Salesforce. Similar capability; less active development. Salesforce Lightning uses it internally.

**Tokens Studio for Figma (commercial).** Figma plugin that lets designers manage tokens in Figma; exports DTCG-format JSON. The bridge from design tool to code pipeline.

The pipeline: designers manage tokens in Tokens Studio → exported as DTCG JSON → Style Dictionary transforms to CSS / JS / iOS / Android → consuming applications import platform-specific files.

## Patterns and anti-patterns

**Pattern: components consume tokens, never raw values.** A button's background is `var(--button-primary-bg)`, never `#3B82F6`. The token enables theming; the raw value defeats it.

**Pattern: themes override the semantic tier.** Light/dark/brand variants reassign semantic tokens to different primitives. Primitives and component tokens are stable across themes.

**Pattern: name semantic tokens by intent, not appearance.** `--color-destructive`, not `--color-red`. Themes may make destructive yellow in some contexts; the name should communicate purpose.

**Pattern: maintain one canonical source.** Whether DTCG JSON or platform-native files, choose one format as authoritative and generate others. Manual sync across multiple sources of truth produces drift.

**Anti-pattern: hardcoded values in components.** Every CSS file that uses `#fff` or `16px` is bypassing the token system. Lint rules can enforce this (stylelint's `declaration-property-value-disallowed-list` or similar).

**Anti-pattern: semantic tokens that ARE primitives.** A token named `--color-blue` mapped to `var(--blue-500)` is just renaming the primitive. Either it should be a semantic name (`--color-primary`) or it shouldn't exist.

**Anti-pattern: too many tokens at the semantic tier.** When the semantic-token list exceeds ~100 colors, it's probably duplicating primitives. Audit periodically.

**Anti-pattern: nested theme contexts in CSS-in-JS.** When CSS-in-JS theme providers nest (one component overrides a parent's theme), the resolution becomes hard to reason about. CSS custom properties cascade naturally; CSS-in-JS theme override requires every consuming component to participate.

**Anti-pattern: component tokens without justification.** Component-keyed tokens add to the system's surface area. Only add them when a component family genuinely needs independent theming OR when component-keyed names improve documentation noticeably.

## Cross-references

- **The values that flow into primitive tokens:** see `KB-visual-design/references/type-color-space.md`.
- **Theming patterns that consume the token system:** see `theming.md`.
- **Governance over the token system's evolution:** see `governance.md`.
- **W3C DTCG specification:** `design-tokens.github.io/community-group/format`.
- **Style Dictionary documentation:** `styledictionary.com`.
- **Token-name semantic vocabulary (a useful reference):** Nathan Curtis. "Naming Tokens in Design Systems." Medium, 2020.
