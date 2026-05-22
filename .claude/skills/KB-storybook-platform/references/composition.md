# Composition — Multi-Package Storybooks via `refs`

Storybook supports composing multiple Storybook instances into a single navigable interface. The mechanism: `refs` in `main.ts` declares external Storybook URLs whose stories appear in the consuming Storybook's sidebar. This solves the common topology where a design-system Storybook is deployed independently from product Storybooks that consume the design system.

## Contents

- [x] When composition applies
- [x] Topology
- [x] Configuration
- [x] Local vs deployed refs
- [x] Patterns and anti-patterns
- [x] Cross-references

## When composition applies

Composition is reached for when:

- A design system is published as a separate package (or separate repo) with its own Storybook deployment, and one or more product apps want to surface design-system stories alongside their own product stories.
- A monorepo has multiple packages each with their own Storybook, and a "root" Storybook should aggregate them for ergonomics.
- An organization runs multiple design systems (legacy + current) and wants both surfaced in one navigable interface during a migration.

Composition is NOT a replacement for a monorepo with a shared Storybook. If all stories live in the same repo and can run in one Storybook process, do that — composition adds operational overhead (separate builds, separate deployments, version coordination) that's only justified when the source files genuinely can't co-locate.

## Topology

The composed Storybook (the consumer) declares `refs` in `main.ts`. Each ref points at the deployed `storybook-static/` of another Storybook. The consuming Storybook fetches each ref's `index.json` (the story manifest) at load time and renders its sidebar entries alongside local stories.

```
Consuming Storybook (product app)
├── Local stories (./src/**/*.stories.tsx)
└── refs:
    └── 'design-system' → fetches https://design-system.example.com/index.json
                          renders design-system stories in sidebar
```

The user clicking a referenced story loads it from the referenced Storybook's URL (iframe-embedded in the consumer's canvas). Args/controls/play all work against the referenced deployment. The consumer never re-builds the referenced stories — it links to them.

## Configuration

```ts
// .storybook/main.ts (consumer)
import type { StorybookConfig } from '@storybook/react-vite';

const config: StorybookConfig = {
  framework: '@storybook/react-vite',
  stories: ['../src/**/*.stories.@(ts|tsx)'],
  refs: {
    'design-system': {
      title: 'Design System',
      url: 'https://design-system.example.com',
      expanded: false,
    },
    'legacy-ui': {
      title: 'Legacy UI (deprecated)',
      url: 'https://legacy-ui.example.com',
      expanded: false,
    },
  },
};

export default config;
```

Per-ref options:

- **`title`** — the sidebar group label.
- **`url`** — the deployed Storybook's URL. Must serve `index.json` from this URL root (default for `storybook build` output).
- **`expanded`** — whether the ref's sidebar group is expanded by default. Useful set to `false` for refs with many stories to keep the consumer's stories visible.
- **`disable`** — when `true`, the ref is registered but not loaded. Useful for feature-flagging refs during migrations.

## Local vs deployed refs

Refs can point at deployed URLs (production) or local development URLs (during development of the referenced Storybook). Local-dev workflow:

```ts
const isLocalDev = process.env.NODE_ENV === 'development';

const config: StorybookConfig = {
  refs: {
    'design-system': {
      title: 'Design System',
      url: isLocalDev
        ? 'http://localhost:6007' // design-system storybook dev server
        : 'https://design-system.example.com',
    },
  },
};
```

The pattern: design-system Storybook runs on port 6007 locally; product Storybook runs on the default 6006 and refs at 6007. Both must be running concurrently for the consumer's sidebar to populate refs.

## Patterns and anti-patterns

**Pattern: design-system Storybook as a long-lived ref.** The design system's Storybook is deployed once per release; product Storybooks ref the deployed URL. Updating the design-system version requires updating the ref's URL (or using a stable URL with version routing).

**Pattern: refs collapsed by default.** Set `expanded: false` so the consumer's own stories are visible first in the sidebar. Users explore the ref deliberately, not by accident.

**Pattern: one ref per repository / package.** Refs map cleanly to deployment units. Trying to split one repo's Storybook across multiple refs adds complexity without benefit.

**Anti-pattern: refs as a build-cache shortcut.** Refs are not a replacement for a shared Storybook in a monorepo. If all source files are in one repo, run one Storybook over the whole tree. Refs add network round-trips and version-skew risk that's not justified inside a single repo.

**Anti-pattern: refs to Storybook versions far from the consumer's.** Refs work across compatible Storybook versions, but a ref pointing at Storybook 6 from a Storybook 10 consumer carries undefined behavior. Keep ref'd Storybooks within a major-version of the consumer; coordinate upgrades.

**Anti-pattern: refs without a long-term ownership model.** A ref'd Storybook can become stale (URL 404s; deployment changes). Establish who owns each referenced Storybook's uptime; document the contract in the consumer's README.

## Cross-references

- **Storybook composition documentation:** `storybook.js.org/docs/sharing/storybook-composition`.
- **`refs` API reference:** `storybook.js.org/docs/api/main-config/main-config-refs`.
- **Design-system topology in the Design layer:** see `KB-design-system-design`.
