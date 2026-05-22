# Testing — Visual Regression and Interaction

Storybook has three testing surfaces, increasingly integrated since Storybook 8: visual regression via Chromatic, interaction testing via `@storybook/test-runner`, and component testing via Vitest integration (Storybook 9+). Each addresses a distinct failure mode; most production design systems use all three.

## Contents

- [x] What each tool catches
- [x] Chromatic — visual regression
- [x] `@storybook/test-runner` — interaction testing via Playwright
- [x] Vitest integration — component testing (Storybook 9+)
- [x] Accessibility assertions via axe-core
- [x] CI integration patterns
- [x] Patterns and anti-patterns
- [x] Cross-references

## What each tool catches

| Surface | Catches | Misses |
|---|---|---|
| Chromatic | Unintended visual changes (pixel diffs); responsive breakpoint regressions; theme regressions | Logic bugs; interaction failures; performance |
| test-runner | `play` function assertion failures; runtime errors during story render; a11y violations (with config) | Visual regressions; production-build regressions |
| Vitest | Component logic; hook behavior; assertion failures | Visual regressions; cross-browser issues |

The three tools are complementary, not redundant. A mature setup runs Chromatic for VRT on PR, test-runner OR Vitest for interaction testing on PR, and reserves browser-level E2E (Playwright outside Storybook) for full-app flows.

## Chromatic — visual regression

Chromatic is a cloud-hosted VRT service from the Storybook team. On every PR, it builds Storybook, snapshots every story (per viewport, per theme), and surfaces a UI diff for review. Reviewers approve or deny each change; the project's main branch tracks approved baselines.

Setup:

```bash
npm install --save-dev chromatic
```

```yaml
# .github/workflows/chromatic.yml
name: Chromatic
on: [push, pull_request]
jobs:
  chromatic:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }
      - uses: actions/setup-node@v4
        with: { node-version: '20' }
      - run: npm ci
      - uses: chromaui/action@v11
        with:
          projectToken: ${{ secrets.CHROMATIC_PROJECT_TOKEN }}
          exitZeroOnChanges: true
```

Per-story controls via `parameters.chromatic`:

```ts
parameters: {
  chromatic: {
    viewports: [320, 1200], // snapshot at multiple widths
    delay: 300, // wait before snapshot (animations settle)
    pauseAnimationAtEnd: true, // pause CSS animations at end state
    disableSnapshot: true, // opt-out of VRT for this story
    modes: { // multi-mode snapshots (light/dark; mobile/desktop)
      light: { theme: 'light' },
      dark: { theme: 'dark' },
    },
  },
}
```

Snapshot stability discipline:

- Stories with random data or timestamps cause flaky snapshots. Stub these with fixed values in `args` or `parameters`.
- Animated stories should pause at end-state via `parameters.chromatic.pauseAnimationAtEnd: true` or skip via `disableSnapshot: true`.
- Font loading races cause one-pixel diffs; preload fonts in `preview.ts` or set `parameters.chromatic.delay` adequate for the project.

The `exitZeroOnChanges: true` setting permits visual changes without failing CI; the team reviews and approves changes in the Chromatic UI. Set to `false` to fail CI on any unreviewed change (stricter; useful for design-system releases).

## `@storybook/test-runner` — interaction testing via Playwright

The test-runner is a Playwright-based local runner that executes `play` functions across all stories. Setup:

```bash
npm install --save-dev @storybook/test-runner
npx playwright install --with-deps
```

```json
// package.json
{
  "scripts": {
    "test-storybook": "test-storybook",
    "test-storybook:ci": "concurrently -k -s first \"npm run storybook -- --ci --quiet --port 6006\" \"wait-on tcp:6006 && npm run test-storybook\""
  }
}
```

Stories with `play` functions become tests automatically. Stories without `play` are smoke-tested — the runner asserts the story renders without throwing.

Configuration via `test-runner.js`:

```ts
// .storybook/test-runner.js
import { injectAxe, checkA11y } from 'axe-playwright';

export default {
  async preVisit(page) {
    await injectAxe(page);
  },
  async postVisit(page, context) {
    await checkA11y(page, '#storybook-root', {
      detailedReport: true,
      detailedReportOptions: { html: true },
    });
  },
};
```

The `preVisit` hook runs before each story renders; `postVisit` runs after. The example above injects axe-core via `axe-playwright` and asserts a11y compliance on every story. Violations fail the test.

## Vitest integration — component testing (Storybook 9+)

Storybook 9 introduced Vitest integration as a first-class path: `*.stories.ts(x)` files become Vitest test files; `play` functions become test bodies. Setup:

```bash
npx storybook@latest init --type vitest
```

The init scaffolds `vitest.config.ts` with a Storybook test project:

```ts
// vitest.config.ts
import { defineConfig } from 'vitest/config';
import { storybookTest } from '@storybook/addon-vitest/vitest-plugin';

export default defineConfig({
  plugins: [
    storybookTest({
      configDir: '.storybook',
      tags: { include: ['test'], exclude: ['skip-vitest'] },
    }),
  ],
  test: {
    browser: {
      enabled: true,
      provider: 'playwright',
      headless: true,
      instances: [{ browser: 'chromium' }],
    },
  },
});
```

Each story's `play` function runs as a Vitest test. Standard Vitest features apply: `--watch`, `--coverage`, filter by file/test name, parallelism.

In CSF Factories projects (Storybook 10+), the `vitest.setup.ts` boilerplate is unnecessary — `setProjectAnnotations` is called automatically. In CSF3 projects on Storybook 9, retain the explicit setup file.

When to choose test-runner vs Vitest:

- **Greenfield project / Storybook 9+**: Vitest is the newer recommendation. Tighter integration with the rest of the test suite; faster watch mode; coverage out of the box.
- **Established project on test-runner**: stay on test-runner unless a specific Vitest feature is needed. The migration is straightforward but not urgent.
- **Projects without other Vitest tests**: test-runner is the lower-overhead choice (no separate test framework setup).

## Accessibility assertions via axe-core

Three paths to a11y testing:

1. **Interactive (addon-a11y panel)** — developer-facing; surfaces violations in the Storybook UI during story authoring. Not enforcement; awareness.
2. **CI via test-runner** — `axe-playwright` in `test-runner.js` (above). Violations fail CI.
3. **CI via Vitest** — axe runs via the addon-a11y test integration; violations fail Vitest tests.

Rule configuration is shared across paths via `parameters.a11y.config.rules` in story or preview. Project-wide rule overrides go in `preview.ts`; per-story exceptions go in the story's `parameters`.

The standard rule set is WCAG 2.0/2.1 Level A and AA (`options.runOnly: ['wcag2a', 'wcag2aa']`). Adding Level AAA rules is project-dependent; the `addon-a11y` documentation lists trade-offs.

## CI integration patterns

A typical CI surface for a design system:

```yaml
# .github/workflows/test.yml
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '20', cache: 'npm' }
      - run: npm ci
      - run: npx playwright install --with-deps chromium
      - run: npm run lint
      - run: npm run typecheck
      - run: npm test # Vitest unit tests
      - run: npm run build-storybook
      - run: npm run test-storybook:ci # interaction + a11y
  chromatic:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }
      - uses: actions/setup-node@v4
        with: { node-version: '20', cache: 'npm' }
      - run: npm ci
      - uses: chromaui/action@v11
        with:
          projectToken: ${{ secrets.CHROMATIC_PROJECT_TOKEN }}
          buildScriptName: build-storybook
```

The `test` job runs first; if it passes, `chromatic` runs against the same Storybook build. This avoids Chromatic snapshots for builds with logic failures.

For projects using Vitest integration (Storybook 9+), replace the test-runner steps with `vitest run` — the storybookTest plugin includes the story-driven tests in the standard Vitest run.

## Patterns and anti-patterns

**Pattern: assertion-rich `play` functions.** A `play` that only drives interaction without asserting outcomes catches nothing meaningful. Each `play` should end with explicit `expect()` calls verifying the resulting state.

```ts
play: async ({ canvasElement }) => {
  const canvas = within(canvasElement);
  await userEvent.click(canvas.getByRole('button'));
  await expect(canvas.getByText('Submitted')).toBeInTheDocument();
  await expect(canvas.getByRole('button')).toBeDisabled();
}
```

**Pattern: stable fixture data.** Stories that drive testing should use deterministic args. Random data, current timestamps, and `Math.random()` produce flaky Chromatic snapshots. Stub these in `args` or via `parameters.mockData`.

**Pattern: per-viewport snapshots via `parameters.chromatic.viewports`.** When a component's behavior changes at breakpoints, snapshot at multiple widths. Don't rely on a single default viewport to catch responsive bugs.

**Anti-pattern: long `play` functions (>30 lines).** A `play` driving multiple distinct flows usually indicates the story is doing too much. Split into focused stories with single flows each.

**Anti-pattern: visual regression and interaction testing as one tool.** Chromatic catches visual; test-runner / Vitest catch behavior. Trying to make one tool do both is a category error — pixel diffs don't catch assertion failures, and interaction tests don't catch unintended visual drift.

**Anti-pattern: `parameters.chromatic.disableSnapshot: true` without justification.** Disabling VRT for a story leaves it untested. If a story is truly untestable visually (e.g., randomized art), document why in a comment.

**Anti-pattern: testing implementation details in `play`.** Asserting against internal class names, DOM structure, or refs couples tests to implementation. Prefer role-based queries (`getByRole`, `getByLabelText`) that match how users find affordances.

## Cross-references

- **Story-level `parameters.chromatic` / `parameters.a11y` config:** see `story-format.md`.
- **`@storybook/addon-a11y` configuration:** see `addons.md`.
- **`@storybook/addon-interactions` panel visualization:** see `addons.md`.
- **Chromatic documentation:** `chromatic.com/docs`.
- **Storybook test-runner documentation:** `storybook.js.org/docs/writing-tests/integrations/test-runner`.
- **Storybook Vitest plugin documentation:** `storybook.js.org/docs/writing-tests/integrations/vitest-addon`.
