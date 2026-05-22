---
id: RN-T-006
topic_id: T-006
topic_name: Storybook (CSF3 / CSF Factories, addons, composition, VRT)
maps_to_ac: AC-FR-1-f
generated: 2026-05-20T23:15:00Z
generated_by: discovery-external-researcher
---

# T-006: Storybook

## Research question

What is the established Storybook knowledge body — story format (CSF3 and the emerging CSF Factories), `args` / `argTypes` / `parameters` / `play` functions, decorators, MDX docs composition, canonical addons (controls, a11y, viewport, interactions, docs), Chromatic visual regression, test-runner integration, multi-package composition (Storybook `ref`)?

## Findings

### Current Storybook version state (as of late-2025 / early-2026)

- **Storybook 10** — released November 5, 2025. ESM-only; ~29% lighter than v9; module automocking; typesafe CSF Factories as a primary feature. The current "latest."
- **Storybook 9** — released June 4, 2025. Revamped testing with Vitest integration; leaner core; accessibility tools (the a11y addon was substantially upgraded).
- **Storybook 8.x** — the prior generation. Still in production use; CSF3 default since SB 7.0 (early 2023).
- **Storybook MCP** — released March 26, 2026. AI-agent integration for React.

The KB content should target Storybook 9+ as the supported floor, with explicit notes on CSF Factories as the v10-and-forward evolution. CSF3 remains the broadly-deployed format; CSF Factories is the next-generation API.

### Component Story Format (CSF) — current discipline

**CSF3** (default since Storybook 7, early 2023). A story file is an ES module exporting a default object (component metadata) and named exports (stories). Story shape:

```ts
// Button.stories.ts
import type { Meta, StoryObj } from '@storybook/react';
import { Button } from './Button';

const meta: Meta<typeof Button> = {
  title: 'Atoms/Button',
  component: Button,
  args: { children: 'Click me' },
  argTypes: { variant: { control: 'select', options: ['primary', 'secondary'] } },
};
export default meta;
type Story = StoryObj<typeof Button>;

export const Primary: Story = { args: { variant: 'primary' } };
export const Secondary: Story = { args: { variant: 'secondary' } };
export const WithInteraction: Story = {
  args: { variant: 'primary' },
  play: async ({ canvasElement }) => {
    const canvas = within(canvasElement);
    await userEvent.click(canvas.getByRole('button'));
  },
};
```

Key CSF3 elements:

- **`args`** — props passed to the component. Story-level args override meta-level args.
- **`argTypes`** — controls (UI affordances for tweaking args in the Storybook panel) + descriptions + documentation hints.
- **`parameters`** — non-prop metadata: viewport configuration, background settings, doc-page customization, decorator behavior.
- **`play`** — async function executing user interactions after render; used by the Interactions addon and by the test-runner.
- **`decorators`** — wrapping functions that provide context (theme provider, router provider, mock store). Stack from outermost to innermost.
- **`render`** — explicit render function (rarely needed in CSF3; default render uses `args` directly).

**CSF Factories** (Storybook 10, typesafe successor). Four factory functions chained from `defineMain` (config) → `definePreview` (preview annotations) → `preview.meta` (component meta) → `meta.story` (per-story). Provides full type safety across the chain; eliminates the type-juggling boilerplate of CSF3. Migration path documented at storybook.js.org; the `automigrate csf-factories` codemod converts CSF3 files automatically.

### Canonical addons (5+)

- **`@storybook/addon-essentials`** (or the v8+ split). Bundles controls, actions, docs, viewport, backgrounds, toolbars. The base configuration for most projects.
- **`@storybook/addon-controls`** — UI panel to manipulate `args` at runtime; reads `argTypes` for control types. The primary affordance for component-API exploration.
- **`@storybook/addon-a11y`** — runs axe-core against the rendered component; surfaces violations in the Storybook panel. Storybook 9 upgraded this addon substantially.
- **`@storybook/addon-viewport`** — preset viewport sizes for responsive checking; integrates with parameters.
- **`@storybook/addon-interactions`** — visualizes `play` function steps; provides time-travel debugging for interaction sequences.
- **`@storybook/addon-docs`** — auto-generated documentation pages with embedded stories; consumes `argTypes` for the props table.
- **`@storybook/addon-themes`** — toggles theme decorators (light/dark) via the toolbar.
- **`@storybook/addon-coverage`** — instruments component code, reports coverage from story-driven testing.

### MDX docs composition

Storybook supports `.mdx` files for documentation pages. The pattern:

```mdx
import { Meta, Story, Canvas, Controls } from '@storybook/blocks';
import * as ButtonStories from './Button.stories';

<Meta of={ButtonStories} />

# Button

A button is...

<Canvas of={ButtonStories.Primary} />

## Props

<Controls />
```

Doc Blocks (`Meta`, `Story`, `Canvas`, `Controls`, `Source`, `Description`, `Subtitle`) compose into a documentation page. Stories are referenced by import, not duplicated. The discipline: stories live in `*.stories.ts(x)` files; MDX is a presentation layer.

### Visual regression testing (Chromatic + test-runner)

- **Chromatic** (chromatic.com, by Storybook's parent company). Cloud-based VRT: every PR snapshots all stories; UI diff review surfaces visual changes. Integrates with GitHub / GitLab / Bitbucket PRs. The dominant VRT solution for Storybook-based design systems.
- **`@storybook/test-runner`** — local CI runner that executes `play` functions across all stories; uses Playwright under the hood. Pairs with axe-core for a11y assertions and Chromatic for VRT.
- **Vitest integration** (Storybook 9). `npx storybook init` can now scaffold a Vitest setup that runs `*.stories.ts(x)` files as test files; the `play` function becomes the test body. Reduces the test-runner-vs-unit-test dichotomy.

### Multi-package composition (Storybook `ref`)

For monorepos with multiple Storybook instances (e.g., a design-system Storybook + a separate product Storybook that consumes it), Storybook composition links them:

```ts
// .storybook/main.ts of the consuming Storybook
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

The consuming Storybook surfaces the referenced Storybook's stories in its sidebar. Useful for design-system documentation that lives in a separate repo / deployment from the product Storybook.

### Storybook's project topology

A typical Storybook project:

```
.storybook/
  main.ts          # config: addons, framework, story locations
  preview.ts       # global decorators, parameters, themes
src/
  components/
    Button.tsx
    Button.stories.ts
    Button.mdx        # optional docs
```

Story file location is configured via `main.ts`'s `stories` glob; the convention is colocate stories with components.

## Sources

- **Storybook official documentation** (storybook.js.org/docs) — primary authoritative source. Versioned docs for each major release.
- **Storybook 9 release announcement** (storybook.js.org/blog) — June 4, 2025. Vitest integration; leaner core; a11y upgrade.
- **Storybook 10 release announcement** (storybook.js.org/blog) — November 5, 2025. ESM-only; typesafe CSF Factories.
- **CSF Factories RFC** (github.com/storybookjs/storybook/discussions/30112) — the typesafe-evolution discussion.
- **Storybook blog post on CSF3** (storybook.js.org/blog/storybook-csf3-is-here/, January 2023) — the canonical CSF3 reference.
- **Chromatic documentation** (chromatic.com/docs) — VRT workflow; PR integration.
- **`@storybook/test-runner` documentation** (storybook.js.org/docs/writing-tests/test-runner) — the canonical CI integration.
- **Storybook MCP announcement** (March 2026) — AI-agent integration; relevant for downstream features that may want to expose Storybook stories to Claude.

## Acceptance-criteria check

| AC | Target | Status |
|---|---|---|
| Documents CSF3 story file shape | required | ✅ With concrete example; with CSF Factories noted as the v10 evolution |
| Names 5+ canonical addons | 5+ | ✅ 8 named (essentials, controls, a11y, viewport, interactions, docs, themes, coverage) |
| Identifies MDX docs composition + decorator stacking | required | ✅ Doc-blocks pattern; decorator outer→inner stacking |
| Names Chromatic + test-runner VRT workflow | required | ✅ Chromatic (cloud), test-runner (local), Vitest integration (Storybook 9) |
| Identifies multi-package composition (`ref`) | required | ✅ With concrete config example |
| Cites Storybook + Chromatic official documentation | required | ✅ Both primary sources cited |

Acceptance-criteria check: **satisfied.**

## Notes for Synthesis and per-layer Design

1. **Version targeting.** The KB content should target Storybook 9+ as the supported floor. CSF Factories (v10) is the typesafe evolution; the KB can show CSF3 syntax as the broadly-deployed format and note CSF Factories as the next-generation direction.
2. **`KB-storybook-platform` is the only platform KB elected.** Per the user's intake constraint, this is the project's fourth platform KB (joining cc / github-actions / codespaces). Structure mirrors KB-github-actions-platform (largest existing platform KB at 6719 lines) for depth precedent.
3. **Code-block density allowance.** Per the user's intake constraint, KB-storybook-platform allows code blocks where syntax IS the knowledge (story shape, addon config, MDX composition). Expected density 3-5 blocks per 100 lines — closer to KB-github-actions-platform's 4.1 than to design KBs' 0.8-1.0.
4. **Anthropic's `frontend-design` skill does not address Storybook.** Storybook is a tooling concern, not an aesthetic one. The KB content stands on its own without an upstream Anthropic skill reference.
5. **Storybook MCP** (Mar 2026) is an emerging story for AI integration. Worth a forward-looking mention in the KB content but not depth-of-coverage at v1.
6. **The design-system + Storybook intersection** (T-004 + T-006) is where `KB-storybook-platform` connects to the design-side KBs. The composition `ref` pattern is the bridge: design-system Storybook documents the components; product Storybook consumes them via ref. Worth surfacing as a cross-cutting note when Synthesis integrates the topics.
