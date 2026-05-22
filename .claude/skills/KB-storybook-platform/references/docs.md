# Documentation — MDX and Doc Blocks

Storybook documentation has two surfaces: auto-generated docs pages (driven by `argTypes` and the docs addon) and authored MDX files (driven by explicit Doc Block composition). Most projects use both: auto-docs for the default props/usage view, MDX for tutorial-style component documentation.

## Contents

- [x] Auto-generated docs
- [x] MDX file shape
- [x] Doc Blocks catalog
- [x] Decorator stacking in docs
- [x] Patterns and anti-patterns
- [x] Cross-references

## Auto-generated docs

When `@storybook/addon-docs` is registered, Storybook generates a documentation page for each component with stories. The page shows:

- Component title and description (from JSDoc on the component, or `meta.parameters.docs.description.component`).
- Props table (derived from `argTypes` plus framework-specific extractors — React PropTypes, TypeScript type extraction, etc.).
- Embedded stories with their args and `play` step visualizations.
- Source code panels for each story.

Most projects need no MDX for components with straightforward documentation needs — the auto-generated page suffices. MDX is reached for when tutorial-style explanation, design rationale, or multi-component composition needs to be authored as prose.

Per-component opt-out: `meta.parameters.docs.disable = true`.

Per-story opt-out (hide from docs page but keep as a navigable story): `Story.parameters.docs.disable = true`.

## MDX file shape

An MDX documentation file imports Doc Blocks from `@storybook/blocks` and the story file's exports. The file's location convention is alongside the component (`Button.stories.tsx` + `Button.mdx`); the docs addon discovers MDX files via the `stories` glob in `main.ts`.

```mdx
{/* Button.mdx */}
import { Meta, Title, Description, Primary, Controls, Stories, Canvas } from '@storybook/blocks';
import * as ButtonStories from './Button.stories';

<Meta of={ButtonStories} />

<Title />
<Description />

The `Button` is the project's primary call-to-action element. Use the
`primary` variant for the single most-important action on a page; use
`secondary` for adjacent actions; use `ghost` for tertiary affordances.

## Primary usage

<Canvas of={ButtonStories.Primary} />

<Controls />

## All variants

<Stories />

## Accessibility notes

The component renders as `<button type="button">` by default. When used
as a navigational element (linking to another page), wrap a Next.js `Link`
or React Router `Link` and pass `asChild` to render the underlying anchor
with button styling.
```

Two load-bearing patterns visible here:

- **`<Meta of={ButtonStories} />`** — connects the MDX file to its story module via the imported namespace. The Meta block must come first; it establishes the docs context for all subsequent blocks.
- **`<Canvas of={ButtonStories.Primary} />`** — embeds a specific story. The `of` prop references the story by its named export, not by string name.

## Doc Blocks catalog

| Block | Purpose | Common props |
|---|---|---|
| `Meta` | Connects MDX to story module | `of={Stories}` |
| `Title` | Page title (from meta.title or component name) | — |
| `Subtitle` | Subtitle below title | — |
| `Description` | Component description | `of={Component}` or `of={Story}` |
| `Primary` | First story rendered in canvas | — |
| `Canvas` | Embed a specific story | `of={Story}`, `sourceState='shown'\|'hidden'\|'none'` |
| `Story` | Embed a story without canvas chrome | `of={Story}` |
| `Source` | Show source code for a story | `of={Story}`, `code='...'` for custom |
| `Controls` | Show controls panel inline | `of={Story}` (optional) |
| `ArgTypes` | Show argTypes table for a story | `of={Story}` |
| `Stories` | Render all stories in a section | `includePrimary={boolean}` |
| `Markdown` | Embed raw markdown | (children) |
| `Unstyled` | Render children without docs styles | (children) |

Doc Blocks accept standard React props (className, style); custom blocks can be authored as ordinary React components and embedded directly in MDX.

## Decorator stacking in docs

Decorators apply in docs pages as in stories. The order is: global decorators (from `preview.ts`) → meta decorators (from the story file's `meta.decorators`) → story decorators (from the individual story's `decorators`). In MDX, a `<Canvas>` block renders its referenced story with all three layers; a `<Story>` block does the same without the canvas chrome.

For docs-only decorator overrides (e.g., wrapping the docs page in a different theme for documentation purposes), use the `parameters.docs.container` option in `meta.parameters` to provide a custom container component.

## Patterns and anti-patterns

**Pattern: one MDX file per component when MDX is reached for.** Mirror the `Button.stories.tsx` + `Button.mdx` colocation. Documentation that crosses components belongs in a top-level page (e.g., `docs/getting-started.mdx` with `meta.title: 'Getting Started'`).

**Pattern: import stories by namespace, not individual names.** `import * as ButtonStories from './Button.stories'` keeps the MDX file in sync as new stories are added; you only update MDX when adding new sections that reference specific new stories.

**Pattern: prose for rationale; stories for examples.** Use MDX for *why* — design rationale, when to use each variant, accessibility notes. Use embedded stories for *how* — actual rendered examples with controls.

**Anti-pattern: re-implementing stories in MDX inline.** When MDX defines its own story shapes inline, they diverge from the canonical story file. The canonical pattern is: stories live in `*.stories.tsx`; MDX embeds them by reference.

**Anti-pattern: MDX for components with simple usage.** If the auto-generated docs page covers a component adequately, adding an MDX file just to write a title and subtitle is overhead. MDX is reached for when prose carries something the auto-docs cannot.

**Anti-pattern: long MDX files (>500 lines).** When a component's documentation grows past 500 lines, the component is probably under-decomposed (separate concerns; multiple sub-components; split into multiple MDX files in a folder).

## Cross-references

- **Story-level `parameters.docs.*`:** see `story-format.md`.
- **`@storybook/addon-docs` configuration:** see `addons.md`.
- **Doc Blocks API reference:** `storybook.js.org/docs/api/doc-blocks/doc-block-canvas` (one page per block).
- **MDX 2 syntax reference:** `mdxjs.com` — Storybook uses MDX 2.
