# Story Format — CSF3 and CSF Factories

The story file is Storybook's authoring primitive. Two formats are current: CSF3 (broadly deployed; default since Storybook 7 in January 2023) and CSF Factories (typesafe successor introduced in Storybook 10, November 2025). CSF2 is the legacy format; the codemod path is CSF2 → CSF3 → CSF Factories.

## Contents

- [x] CSF3 — the broadly-deployed format
- [x] The five primitives in CSF3
- [x] CSF Factories — the typesafe v10 evolution
- [x] Migration between formats
- [x] Patterns and anti-patterns
- [x] Cross-references

## CSF3 — the broadly-deployed format

A CSF3 story file exports a default object (meta) and named exports (stories). Each named export is a plain object with `args`, `parameters`, `decorators`, and optionally `play`. Type safety is achieved with TypeScript `satisfies` against `Meta<typeof Component>` and `StoryObj<typeof Component>`.

```tsx
// Button.stories.tsx
import type { Meta, StoryObj } from '@storybook/react';
import { within, userEvent, expect } from '@storybook/test';
import { Button } from './Button';

const meta = {
  title: 'Atoms/Button',
  component: Button,
  args: { children: 'Click me' },
  argTypes: {
    variant: { control: 'select', options: ['primary', 'secondary', 'ghost'] },
    size: { control: 'select', options: ['sm', 'md', 'lg'] },
    disabled: { control: 'boolean' },
  },
  parameters: {
    layout: 'centered',
  },
} satisfies Meta<typeof Button>;

export default meta;
type Story = StoryObj<typeof meta>;

export const Primary: Story = { args: { variant: 'primary' } };
export const Secondary: Story = { args: { variant: 'secondary' } };
export const Disabled: Story = { args: { disabled: true } };

export const Clicked: Story = {
  args: { variant: 'primary' },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    const button = canvas.getByRole('button');
    await userEvent.click(button);
    await expect(button).toHaveFocus();
  },
};
```

Three load-bearing elements:

- **`satisfies Meta<typeof Button>`** — the type assertion that gives `StoryObj<typeof meta>` access to the component's prop types. Without `satisfies`, args lose type information.
- **`type Story = StoryObj<typeof meta>`** — derived once at the top; reused per story. The convention is consistent across the Storybook documentation.
- **`play: async ({ canvasElement }) => ...`** — the function signature accepting Storybook test context. Returns nothing; assertions throw to fail.

## The five primitives in CSF3

**`meta`** — the default-exported object. Required keys: `title` (sidebar location) OR `component` (allows auto-title generation). Optional keys: `args`, `argTypes`, `parameters`, `decorators`, `tags`, `render`.

**`story`** — each named export. Overrides meta's keys; adds story-specific `play`. Stories typically only declare `args` overrides; defaults flow from meta.

**`args`** — props for the component. Story-level args MERGE WITH meta-level args (story wins on conflict). Args drive the controls panel; non-arg props (function props, slot children that are JSX) are typically rendered via a `render` function override.

**`argTypes`** — control UI affordances + documentation hints. Common control types: `select` (enum), `boolean`, `text`, `range` (numeric slider), `color`, `date`. The `argTypes` entry can also carry `description` (consumed by the docs addon for the props table).

**`parameters`** — non-prop metadata. Common keys:

- `layout: 'centered' | 'fullscreen' | 'padded'` — story container layout.
- `backgrounds: { default: 'dark' }` — backgrounds-addon default selection.
- `viewport: { defaultViewport: 'mobile1' }` — viewport-addon default.
- `chromatic: { disableSnapshot: true }` — opt-out of Chromatic VRT for this story.
- `docs: { description: { story: '...' } }` — per-story documentation override.
- `a11y: { config: { rules: [{ id: 'color-contrast', enabled: false }] } }` — a11y-addon rule overrides.

**`decorators`** — wrapping functions. Stack outermost-to-innermost. Global decorators in `preview.ts` apply to all stories; meta decorators apply to one component's stories; story decorators apply to a single story.

```tsx
// preview.ts
import type { Preview } from '@storybook/react';

const preview: Preview = {
  decorators: [
    (Story) => (
      <ThemeProvider theme={defaultTheme}>
        <Story />
      </ThemeProvider>
    ),
  ],
};

export default preview;
```

## CSF Factories — the typesafe v10 evolution

CSF Factories chain four factory functions: `defineMain` → `definePreview` → `preview.meta` → `meta.story`. Each step's return value carries the prior step's type information forward; addon configuration becomes type-checked at story-write time.

```ts
// .storybook/main.ts
import { defineMain } from '@storybook/react-vite/node';
import a11y from '@storybook/addon-a11y/preview';
import themes from '@storybook/addon-themes/preview';

export default defineMain({
  framework: '@storybook/react-vite',
  stories: ['../src/**/*.stories.@(ts|tsx)'],
  addons: [a11y, themes],
});
```

```ts
// .storybook/preview.ts
import { definePreview } from '@storybook/react-vite';
import config from './main';
import { ThemeProvider } from '../src/theme';

export default definePreview({
  ...config,
  decorators: [
    (Story) => <ThemeProvider><Story /></ThemeProvider>,
  ],
});
```

```tsx
// Button.stories.tsx
import preview from '../.storybook/preview';
import { Button } from './Button';

const meta = preview.meta({
  component: Button,
  args: { children: 'Click me' },
});

export default meta;

export const Primary = meta.story({ args: { variant: 'primary' } });
export const Secondary = meta.story({ args: { variant: 'secondary' } });
```

Three load-bearing differences from CSF3:

- **No `satisfies` boilerplate.** `preview.meta` accepts the component-typed object; `meta.story` accepts component-typed args. Type errors surface at the right call site without intermediate `Meta<typeof ...>` declarations.
- **Addons can contribute types.** When an addon ships a preview module (e.g., `@storybook/addon-a11y/preview`), its `parameters` and `globals` shape flows through `definePreview` into every story file. Misconfiguration surfaces as a compile error.
- **Preview is imported, not implicit.** The story file imports the project's preview to derive `meta`; this makes the dependency explicit rather than implicit through Storybook's resolver.

The `vitest.setup.ts` boilerplate becomes unnecessary in CSF Factories — `setProjectAnnotations` is called automatically. Manual upgrade instructions for projects with custom Vitest setups are documented at `storybook.js.org/docs/migration-guide`.

## Migration between formats

| From | To | Codemod |
|---|---|---|
| CSF2 | CSF3 | `npx storybook migrate csf-2-to-3 --glob="**/*.stories.tsx" --parser=tsx` |
| CSF3 | CSF Factories | `npx storybook automigrate csf-factories` |
| CSF2 | CSF Factories | Two-step (CSF2 → CSF3 first, then CSF3 → CSF Factories) |

Migration is mechanical for stories using the canonical patterns. Stories using legacy patterns (custom `render` functions with complex signatures, decorators with non-standard parameter shapes) may require manual review. The codemods are idempotent; running twice on already-migrated files is safe.

For projects on Storybook 9: stay on CSF3. For greenfield projects starting on Storybook 10: use CSF Factories. For projects mid-migration on Storybook 10: mixed CSF3 + CSF Factories within a project is supported (per-file, not within-file).

## Patterns and anti-patterns

**Pattern: derive `type Story` once per file.** `type Story = StoryObj<typeof meta>` at the top; reuse for every story. Avoids re-declaring the type in each story export.

**Pattern: `args` for runtime-tweakable props; `render` for compositional structure.** Use `args` for primitives (strings, numbers, booleans, enums); use a `render` function override when a story needs custom children or slots that controls can't manipulate.

```tsx
export const WithIcon: Story = {
  render: (args) => (
    <Button {...args}>
      <Icon name="check" />
      Click me
    </Button>
  ),
};
```

**Pattern: extract reusable `play` helpers.** When multiple stories share interaction sequences, factor them into a `play-helpers.ts` module. Keeps stories focused on what's distinct.

**Anti-pattern: stories with inline business logic.** A story should configure the component and (optionally) drive interaction. It should not embed business logic the component itself doesn't expose. If a story needs a complex setup, that's a sign the component's API is incomplete.

**Anti-pattern: mixing CSF3 and CSF Factories within a file.** The compiler rejects this. Choose one format per file; mixed-format projects are valid at the project level.

**Anti-pattern: untyped meta.** Skipping `satisfies Meta<typeof Component>` (in CSF3) leaves args without type checking and silently degrades the developer experience. In CSF Factories, `preview.meta(...)` enforces the typing; CSF3 without `satisfies` is a graceful degradation that's still rejected by the project's TypeScript strict mode.

**Anti-pattern: per-story decorators that mutate global state.** Decorators that set up shared mocks should be in `preview.ts` (global). Per-story decorators should be scoped to that story's needs only. State that leaks across stories produces flaky test runs.

## Cross-references

- **Addon configuration:** see `addons.md`.
- **MDX docs composition:** see `docs.md`.
- **Testing the `play` function via test-runner or Vitest:** see `testing.md`.
- **Multi-package composition:** see `composition.md`.
- **CSF Factories official documentation:** `storybook.js.org/docs/api/csf/csf-factories`.
- **CSF3 official documentation:** `storybook.js.org/docs/api/csf`.
