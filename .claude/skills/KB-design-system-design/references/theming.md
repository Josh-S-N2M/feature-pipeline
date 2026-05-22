# Theming

How variant systems (light/dark/brand/density) consume the token architecture. Three durable patterns: CSS custom properties (the modern default; browser-native), Style Dictionary polyglot output (build-time transformation across platforms), and CSS-in-JS theme contexts (legacy pattern still present in some codebases).

## Contents

- [x] What "theming" encompasses
- [x] CSS custom properties — modern default
- [x] Style Dictionary — polyglot pipeline
- [x] CSS-in-JS theme context — legacy default
- [x] Theme switching at runtime
- [x] System preference detection
- [x] Patterns and anti-patterns
- [x] Cross-references

## What "theming" encompasses

Themes are variant systems. The common dimensions:

- **Color scheme** — light, dark, high-contrast, brand variants.
- **Density** — comfortable, default, compact.
- **Direction** — LTR, RTL (for languages like Arabic, Hebrew).
- **Reduced motion** — full motion, reduced motion (typically not a "theme" but applied via the same mechanism).

A theme is a set of token VALUES that swap in. The token NAMES are stable; the consuming components don't know what theme is active.

## CSS custom properties — modern default

CSS variables (`--token-name: value`) declared on a root element, optionally scoped to attribute selectors for variants. The browser handles the cascade; theme switches require no JavaScript beyond toggling an attribute.

```css
:root {
  --color-background: oklch(98% 0 0);
  --color-foreground: oklch(15% 0 0);
  --color-primary:    oklch(60% 0.18 260);
}

:root[data-theme='dark'] {
  --color-background: oklch(15% 0 0);
  --color-foreground: oklch(95% 0 0);
  --color-primary:    oklch(70% 0.15 260);
}

:root[data-theme='high-contrast'] {
  --color-background: oklch(100% 0 0);
  --color-foreground: oklch(0% 0 0);
  --color-primary:    oklch(40% 0.25 260);
}
```

Component CSS consumes the tokens; theme is set on `<html data-theme="dark">`:

```css
.card {
  background-color: var(--color-background);
  color: var(--color-foreground);
}
```

A toggle component changes the attribute:

```ts
document.documentElement.dataset.theme = 'dark';
```

Advantages:

- **Browser-native cascade.** No framework involved; works in vanilla CSS.
- **Runtime swap with zero re-render.** Changing the attribute repaints; React/Vue/Svelte components don't re-render.
- **Server-side rendering compatible.** The HTML attribute can be set before the page hydrates; no flash of incorrect theme.
- **Composable.** Multiple attributes combine — `data-theme="dark" data-density="compact"` activates both variants. Each contributes its own token overrides.

This is the modern default for browser-targeted projects.

## Style Dictionary — polyglot pipeline

For projects that need to ship token values to multiple platforms (web, iOS, Android, native desktop), Style Dictionary transforms one source-of-truth token file into platform-specific outputs. The build pipeline:

```
tokens.json (DTCG format)
    ↓ Style Dictionary
    ├── tokens.css         (CSS variables for web)
    ├── tokens.scss        (Sass variables; for projects on Sass)
    ├── tokens.ts          (TypeScript constants)
    ├── Colors.swift       (iOS Swift constants)
    ├── colors.xml         (Android color resources)
    └── tokens.json        (DTCG format for designer tools)
```

Each output is generated from the same source; values stay synchronized.

Theme variants in Style Dictionary: separate source files per theme, processed independently.

```
tokens/
├── base.tokens.json          # primitives (shared across themes)
├── light.tokens.json         # semantic tokens for light theme
└── dark.tokens.json          # semantic tokens for dark theme
```

The pipeline generates `tokens-light.css` and `tokens-dark.css`; the application loads both and switches between them. Alternatively (more common), generate one `tokens.css` that includes both theme blocks (the CSS-variables-with-attribute-selector pattern shown above).

When to use Style Dictionary: cross-platform products (web + mobile native); design-system packages that ship to consumers in multiple formats; large teams that want a build-time enforcement boundary between design-token authoring and consumption.

When to skip: web-only projects with no need for non-CSS outputs. The CSS-variables-direct approach is simpler.

## CSS-in-JS theme context — legacy default

CSS-in-JS libraries (styled-components, Emotion, Vanilla Extract) historically used a JavaScript theme object passed via React Context.

```tsx
import { ThemeProvider } from 'styled-components';

const lightTheme = {
  colors: {
    background: '#FAFAFA',
    foreground: '#171717',
    primary: '#3B82F6',
  },
};

const darkTheme = {
  colors: {
    background: '#171717',
    foreground: '#FAFAFA',
    primary: '#5B9DF5',
  },
};

function App() {
  const [isDark, setIsDark] = useState(false);
  return (
    <ThemeProvider theme={isDark ? darkTheme : lightTheme}>
      {/* ... */}
    </ThemeProvider>
  );
}

const Card = styled.div`
  background-color: ${props => props.theme.colors.background};
  color: ${props => props.theme.colors.foreground};
`;
```

This pattern predates CSS custom property support (which became ubiquitous around 2017). At the time, CSS-in-JS theme context was the only way to swap design tokens at runtime in a framework-friendly way.

In 2026, the pattern is largely legacy:

- React Context's re-render cost makes theme switching less performant than CSS variable cascade.
- Server-side rendering with theme context requires careful hydration to avoid mismatches.
- The CSS-variables pattern is simpler, more performant, and framework-agnostic.

When CSS-in-JS theme context is still appropriate:

- The project is committed to a CSS-in-JS library and migration cost outweighs perf gains.
- The theme system requires logic at theme-application time (computed values; conditional decisions based on context). CSS variables can't carry logic; theme objects can.
- The team uses Vanilla Extract or similar that compiles CSS-in-JS to CSS at build time (sidestepping the runtime cost).

For new projects: start with CSS custom properties. Reach for CSS-in-JS theme context only if there's a specific requirement it serves.

## Theme switching at runtime

Three patterns:

**Toggle attribute on root element.** The pattern shown above. Simplest; most performant.

```ts
function setTheme(theme: 'light' | 'dark') {
  document.documentElement.dataset.theme = theme;
  localStorage.setItem('theme', theme);
}
```

**Toggle CSS class on root element.** Equivalent to attribute; uses class selectors instead. Some prefer the syntax (`.dark { ... }`); functionally identical.

```css
:root.dark {
  --color-background: oklch(15% 0 0);
  /* ... */
}
```

**Replace stylesheet href.** Load one of multiple CSS files based on theme. Most heavyweight (full stylesheet swap); rarely useful unless themes are too divergent to share a base stylesheet.

Persistence: persist user theme preference to `localStorage`; apply on page load before render to avoid flash.

```html
<script>
  // Inline script in <head> runs before any rendering
  const stored = localStorage.getItem('theme');
  const system = window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
  document.documentElement.dataset.theme = stored || system;
</script>
```

This inline script is the only acceptable case for blocking script in `<head>` — it must run before content paints to prevent FOUC (Flash of Unstyled Content with wrong theme).

## System preference detection

`prefers-color-scheme` media query detects the user's OS-level color-scheme preference:

```css
@media (prefers-color-scheme: dark) {
  :root {
    --color-background: oklch(15% 0 0);
    --color-foreground: oklch(95% 0 0);
  }
}
```

The behavior: when no explicit theme is set (`data-theme` attribute absent), the OS preference applies. When `data-theme` is set, it overrides.

Pattern using both:

```css
:root {
  --color-background: oklch(98% 0 0); /* light default */
}

@media (prefers-color-scheme: dark) {
  :root {
    --color-background: oklch(15% 0 0); /* dark when OS prefers dark */
  }
}

:root[data-theme='light'] {
  --color-background: oklch(98% 0 0); /* explicit light overrides OS */
}

:root[data-theme='dark'] {
  --color-background: oklch(15% 0 0); /* explicit dark overrides OS */
}
```

The three-state pattern: 'auto' (follows OS), 'light' (explicit override), 'dark' (explicit override). Most products offer this; many products skip 'auto' and default to one explicit theme.

`prefers-reduced-motion`, `prefers-contrast`, and `prefers-reduced-transparency` are sibling media queries for non-color preferences. The same pattern applies.

## Patterns and anti-patterns

**Pattern: tokens declared at `:root`; overrides at attribute selectors.** Modern, framework-agnostic, performant. The default.

**Pattern: inline `<script>` in `<head>` for theme initialization.** Avoid FOUC by reading and applying theme before render. The one case where blocking script is correct.

**Pattern: CSS variables for all theme-dependent values.** If something differs between themes, it's a token. Hardcoding a color "because it's always white" couples the value to the theme implicitly.

**Pattern: combine theme dimensions via independent attributes.** `data-theme="dark" data-density="compact"` activates both. Each dimension defines its own overrides; they compose naturally.

**Anti-pattern: theme-aware components that switch styles in JavaScript.** When a component reads the theme and renders differently per theme, the theme system isn't doing its job. The component should consume tokens; the tokens should change with the theme.

**Anti-pattern: theme baked into component variants.** A `<DarkButton>` component is a code smell. There should be one `<Button>`; the theme decides what it looks like.

**Anti-pattern: localStorage read on every render.** Read once on app initialization; sync to state. Repeated reads are slow (localStorage is synchronous) and unnecessary.

**Anti-pattern: theme-specific component implementations.** If a component requires different markup or logic per theme, the design system has failed to abstract the variation properly.

**Anti-pattern: conflicting theme sources.** When server, client, and user-preference all set theme, race conditions cause flickering. Establish a single source of truth (typically client-side after initial render) and have other sources defer to it.

## Cross-references

- **Token tier architecture this theming consumes:** see `tokens.md`.
- **Design-system governance over theme additions:** see `governance.md`.
- **Visual decisions per theme (dark mode values; brand palette generation):** see `KB-visual-design/references/type-color-space.md`.
- **Motion theme respecting `prefers-reduced-motion`:** see `KB-visual-design/references/motion.md`.
- **MDN `prefers-color-scheme`:** `developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-color-scheme`.
