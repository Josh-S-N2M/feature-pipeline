# Addons — Canonical Catalog

Storybook is unopinionated by default; addons extend the surface. Each addon is an npm package registering panels, decorators, or build hooks via a Storybook plugin entry point. Configuration: `.storybook/main.ts`'s `addons` array (in CSF3 projects) or imported preview modules (in CSF Factories projects).

## Contents

- [x] Addon registration
- [x] Essentials bundle
- [x] Individual canonical addons
- [x] Custom addons (out of scope notes)
- [x] Addon ordering and conflicts
- [x] Cross-references

## Addon registration

In CSF3 projects, addons are registered as strings in `.storybook/main.ts`:

```ts
import type { StorybookConfig } from '@storybook/react-vite';

const config: StorybookConfig = {
  framework: '@storybook/react-vite',
  stories: ['../src/**/*.stories.@(ts|tsx)'],
  addons: [
    '@storybook/addon-essentials',
    '@storybook/addon-a11y',
    '@storybook/addon-themes',
    '@storybook/addon-interactions',
  ],
};

export default config;
```

In CSF Factories projects (Storybook 10+), addons are imported as preview modules:

```ts
import { defineMain } from '@storybook/react-vite/node';
import a11y from '@storybook/addon-a11y/preview';
import themes from '@storybook/addon-themes/preview';
import interactions from '@storybook/addon-interactions/preview';

export default defineMain({
  framework: '@storybook/react-vite',
  stories: ['../src/**/*.stories.@(ts|tsx)'],
  addons: [a11y, themes, interactions],
});
```

The CSF Factories form provides type-checked parameters and globals at the project level. Addons that have not yet shipped CSF Factories–compatible preview modules can still be registered as strings within the array; mixed registration is supported during the migration window.

## Essentials bundle

`@storybook/addon-essentials` historically bundled controls + actions + docs + viewport + backgrounds + toolbars + measure + outline. Storybook 8.x split several of these out; in Storybook 9+ the bundle is leaner. Check the version-specific package contents at `storybook.js.org/docs/essentials` for the current set.

When adding essentials, individual addons in the bundle do NOT need separate registration. Adding a same-named individual addon alongside the bundle causes a duplicate-registration warning; the individual addon wins.

For new projects on Storybook 9+, prefer registering only the addons actually needed. The essentials bundle remains useful for prototyping but adds modest install size for production-grade setups.

## Individual canonical addons

### `@storybook/addon-controls`

The runtime arg-manipulation panel. Reads `argTypes` from meta for control widget type and configuration. Common control types:

| Control | Use |
|---|---|
| `select` | enum prop with `options: [...]` |
| `radio` | small enum where button-group affordance is clearer |
| `boolean` | toggle for boolean prop |
| `text` | string prop free-form |
| `number` | numeric input |
| `range` | numeric prop with `min`/`max`/`step` |
| `color` | color string |
| `date` | date input |
| `object` | JSON editor for object props |
| `file` | file upload for File-prop testing |

In CSF3:

```ts
argTypes: {
  variant: { control: 'select', options: ['primary', 'secondary'] },
  size: { control: { type: 'range', min: 8, max: 64, step: 4 } },
  disabled: { control: 'boolean' },
}
```

Controls panel disposition is exposed via `parameters.controls.exclude: ['internalProp']` to hide props from the panel without removing them from `args`.

### `@storybook/addon-a11y`

Runs `axe-core` against the rendered story and surfaces violations in the panel. Storybook 9 substantially upgraded this addon (more rules; better diagnostics; improved test-runner integration).

Configuration in `parameters`:

```ts
parameters: {
  a11y: {
    config: {
      rules: [
        { id: 'color-contrast', enabled: false },
      ],
    },
    options: {
      runOnly: ['wcag2a', 'wcag2aa'],
    },
  },
}
```

Per-story disable (rare; document the reason):

```ts
parameters: { a11y: { disable: true } }
```

When paired with `@storybook/test-runner`, axe violations can be promoted to test failures via `test-runner.js` configuration.

### `@storybook/addon-viewport`

Presets for common device viewports. Configuration:

```ts
parameters: {
  viewport: {
    viewports: MINIMAL_VIEWPORTS, // or INITIAL_VIEWPORTS or custom
    defaultViewport: 'mobile1',
  },
}
```

Custom viewports follow the shape `{ name, styles: { width, height }, type: 'desktop' | 'mobile' | 'tablet' }`.

### `@storybook/addon-interactions`

Visualizes `play` function steps; provides time-travel debugging. The panel shows each `await userEvent.*` and `await expect.*` step with success/failure state and a snapshot of the DOM at that step. No story-level configuration needed; the panel activates automatically when a story has a `play` function.

Pair with `@storybook/test` (which re-exports `userEvent`, `within`, `expect`, `waitFor`, `fn` from the underlying Testing Library / Vitest integration).

### `@storybook/addon-docs`

Auto-generates documentation pages with embedded stories. Reads `argTypes` for the props table; consumes `parameters.docs.description.story` for per-story descriptions. Full Doc Blocks API is in `docs.md`.

Configuration to opt out of docs page for a specific story:

```ts
parameters: { docs: { disable: true } }
```

### `@storybook/addon-themes`

Toggles theme decorators (light/dark/brand variants) via the toolbar. Configuration:

```ts
// preview.ts
import { withThemeByClassName } from '@storybook/addon-themes';

export const decorators = [
  withThemeByClassName({
    themes: { light: 'theme-light', dark: 'theme-dark' },
    defaultTheme: 'light',
  }),
];
```

Three theme provider patterns supported: `withThemeByClassName` (adds CSS class to root), `withThemeByDataAttribute` (sets `data-theme` attribute), `withThemeFromJSXProvider` (wraps in a JSX provider component).

### `@storybook/addon-coverage`

Instruments component code; reports coverage from story-driven testing. Pairs with the test-runner; the coverage report writes to `./coverage/storybook/`. Configuration:

```ts
// main.ts
addons: [
  {
    name: '@storybook/addon-coverage',
    options: {
      istanbul: {
        include: ['src/**/*.tsx'],
        exclude: ['**/*.stories.tsx', '**/*.test.tsx'],
      },
    },
  },
],
```

### `@storybook/addon-measure` and `@storybook/addon-outline`

Visual debugging affordances. Measure shows pixel measurements of hovered elements; outline shows box-model outlines. Useful during design-system development; typically not needed in production-grade story files.

## Custom addons (out of scope notes)

Building custom addons is documented at `storybook.js.org/docs/addons/writing-addons`. Out of scope for v1 of this KB. Two adjacent patterns worth knowing:

- **Chromatic's addon** (visual regression) — see `testing.md`.
- **story.to.design's addon** — Figma integration; out of scope.

## Addon ordering and conflicts

The `addons` array's order can matter for decorator stacking. Addons providing decorators (themes, viewport, backgrounds) stack outermost-to-innermost in array order. The first addon's decorator wraps everything below it.

When addons conflict (e.g., two addons both adding a toolbar entry with the same key), the later-registered addon wins. Document conflicts explicitly in `main.ts` comments when intentional.

The `essentials` bundle is registered as a single entry but expands internally; if a specific addon from essentials needs configuration via `options`, register it individually instead of through the bundle.

## Cross-references

- **Story-level `parameters` reference:** see `story-format.md`.
- **Doc Blocks for the docs addon:** see `docs.md`.
- **Test-runner integration with addon-a11y, addon-interactions, addon-coverage:** see `testing.md`.
- **Storybook addons catalog:** `storybook.js.org/addons`.
