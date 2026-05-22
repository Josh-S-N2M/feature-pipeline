# Recipes: TypeScript / Node.js

Patterns for TypeScript and JavaScript projects on GitHub Actions. Covers npm/pnpm/yarn, monorepos, common toolchains (Vitest, Jest, ESLint, Biome, tsc), and bundlers.

## Table of contents

- [Setup basics](#setup-basics)
- [Package manager: npm, pnpm, yarn](#package-manager-npm-pnpm-yarn)
- [Standard CI pipeline](#standard-ci-pipeline)
- [Test runners: Vitest, Jest](#test-runners-vitest-jest)
- [Linting: ESLint, Biome](#linting-eslint-biome)
- [Type checking: tsc](#type-checking-tsc)
- [Monorepos: Turborepo, Nx, pnpm workspaces](#monorepos-turborepo-nx-pnpm-workspaces)
- [Bundling and build artifacts](#bundling-and-build-artifacts)
- [Publishing to npm](#publishing-to-npm)

For a ready-to-use template, see `assets/templates/ci-typescript.yml` and `assets/templates/release-npm.yml`.

## Setup basics

```yaml
- uses: actions/checkout@v6
- uses: actions/setup-node@v6
  with:
    node-version: '22'        # specify exact major; 24 is current default but stick to LTS for prod
    cache: npm
```

Node version policy:
- **20** — was LTS; deprecating in mid-2026 on GitHub Actions runners.
- **22** — current LTS through 2027. Default choice for production projects.
- **24** — current default for new actions. Use for cutting-edge.
- For libraries, test against the LTS line (matrix on 20, 22, 24).

`node-version-file:` is preferred when the project has a `.nvmrc` or `.node-version`:
```yaml
- uses: actions/setup-node@v6
  with: { node-version-file: '.nvmrc', cache: npm }
```

## Package manager: npm, pnpm, yarn

### npm (default)

```yaml
- uses: actions/setup-node@v6
  with: { node-version: '22', cache: npm }
- run: npm ci
- run: npm test
```

`npm ci` (not `npm install`) for CI: deterministic, fails if `package-lock.json` is out of sync.

### pnpm

```yaml
- uses: pnpm/action-setup@SHA   # pin to current SHA
  with: { version: 9 }
- uses: actions/setup-node@v6
  with: { node-version: '22', cache: pnpm }
- run: pnpm install --frozen-lockfile
- run: pnpm test
```

The pnpm setup action must run **before** `setup-node` because `setup-node`'s caching needs to know about pnpm.

### yarn (classic v1)

```yaml
- uses: actions/setup-node@v6
  with: { node-version: '22', cache: yarn }
- run: yarn install --frozen-lockfile
- run: yarn test
```

### yarn (Berry / v3+)

```yaml
- uses: actions/setup-node@v6
  with: { node-version: '22' }    # don't use cache: yarn here; berry caches differently
- run: corepack enable
- run: yarn install --immutable
- run: yarn test
```

## Standard CI pipeline

Lint → typecheck → test → build, in a parallel-where-possible structure:

```yaml
name: CI
on:
  push: { branches: [main] }
  pull_request:

permissions:
  contents: read

concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: ${{ github.event_name == 'pull_request' }}

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-node@v6
        with: { node-version: '22', cache: npm }
      - run: npm ci
      - run: npm run lint

  typecheck:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-node@v6
        with: { node-version: '22', cache: npm }
      - run: npm ci
      - run: npm run typecheck   # tsc --noEmit

  test:
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix: { node: [20, 22] }
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-node@v6
        with: { node-version: '${{ matrix.node }}', cache: npm }
      - run: npm ci
      - run: npm test -- --reporter=verbose --coverage

  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-node@v6
        with: { node-version: '22', cache: npm }
      - run: npm ci
      - run: npm run build
      - uses: actions/upload-artifact@v4
        with: { name: dist, path: dist/, retention-days: 7 }
```

Notes:
- Each job re-runs `npm ci`. Unfortunate but standard — jobs are isolated. The cache makes it fast (10–20s).
- Optimization: a single `setup` job that builds and uploads `node_modules` as an artifact, with downstream jobs downloading. Worth it only when install is slow (>1 min).

## Test runners: Vitest, Jest

### Vitest

```yaml
- run: npm test -- --coverage --reporter=verbose
- uses: actions/upload-artifact@v4
  if: always()
  with: { name: coverage, path: coverage/, retention-days: 7 }
```

Vitest's coverage with V8 is very fast. Configure thresholds in `vitest.config.ts`.

### Jest

```yaml
- run: npm test -- --ci --coverage --reporters=default --reporters=github-actions
- uses: actions/upload-artifact@v4
  if: always()
  with: { name: coverage, path: coverage/ }
```

The `github-actions` reporter for Jest annotates failed tests in the PR diff.

### Test sharding

For large suites (>5 min):

```yaml
test:
  strategy:
    fail-fast: false
    matrix: { shard: [1, 2, 3, 4] }
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v6
    - uses: actions/setup-node@v6
      with: { node-version: '22', cache: npm }
    - run: npm ci
    - run: npm test -- --shard=${{ matrix.shard }}/4
```

(Most modern test runners support `--shard=N/M`.)

## Linting: ESLint, Biome

### ESLint

```yaml
- run: npm run lint -- --output-file eslint-report.json --format json
- if: always()
  uses: actions/upload-artifact@v4
  with: { name: eslint-report, path: eslint-report.json }
```

For inline annotations:
```yaml
- run: npm run lint -- --format=@microsoft/eslint-formatter-sarif --output-file eslint-results.sarif
- if: always()
  uses: github/codeql-action/upload-sarif@SHA
  with: { sarif_file: eslint-results.sarif }
```

This populates the Security tab and surfaces lint issues as code-scanning alerts.

### Biome

```yaml
- run: npx @biomejs/biome ci .
```

Biome is faster than ESLint+Prettier and has built-in CI mode that handles formatting + lint in one pass.

## Type checking: tsc

```yaml
- run: npx tsc --noEmit
```

For monorepos using project references:
```yaml
- run: npx tsc --build --verbose
```

## Monorepos: Turborepo, Nx, pnpm workspaces

### Turborepo

```yaml
- uses: actions/checkout@v6
  with: { fetch-depth: 0 }    # turbo needs git history for affected/changed
- uses: actions/setup-node@v6
  with: { node-version: '22', cache: npm }
- run: npm ci
- run: npx turbo run lint typecheck test build --filter=...[origin/main]
- name: Cache turbo build
  uses: actions/cache@v4
  with:
    path: .turbo
    key: ${{ runner.os }}-turbo-${{ github.sha }}
    restore-keys: ${{ runner.os }}-turbo-
```

Or use Turborepo Remote Caching (set `TURBO_TOKEN`, `TURBO_TEAM`) so the cache is shared across CI runs and developers.

### Nx

```yaml
- uses: actions/checkout@v6
  with: { fetch-depth: 0 }
- uses: actions/setup-node@v6
  with: { node-version: '22', cache: npm }
- uses: nrwl/nx-set-shas@SHA   # pin to current SHA
- run: npm ci
- run: npx nx affected -t lint test build
```

Nx Cloud's distributed task execution can parallelize across multiple GitHub Actions runners — useful for huge monorepos.

### pnpm workspaces (manual)

```yaml
- run: pnpm install --frozen-lockfile
- run: pnpm -r --parallel run lint
- run: pnpm -r --parallel run test
- run: pnpm -r --parallel run build
```

`-r` runs across all workspace packages; `--parallel` runs them concurrently.

## Bundling and build artifacts

### Standard build → artifact

```yaml
build:
  runs-on: ubuntu-latest
  steps:
    - uses: actions/checkout@v6
    - uses: actions/setup-node@v6
      with: { node-version: '22', cache: npm }
    - run: npm ci
    - run: npm run build
    - uses: actions/upload-artifact@v4
      with:
        name: app-${{ github.sha }}
        path: dist/
        retention-days: 14
```

### Bundle-size check

For libraries: track bundle size and fail PRs that regress it.

```yaml
- uses: andresz1/size-limit-action@SHA   # pin
  with:
    github_token: ${{ secrets.GITHUB_TOKEN }}
```

Or roll your own with `bundlesize`, `size-limit`, etc.

## Publishing to npm

See `assets/templates/release-npm.yml` for a full template. Two approaches:

### With `NPM_TOKEN`

```yaml
permissions:
  contents: read
  id-token: write   # for provenance

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-node@v6
        with:
          node-version: '22'
          registry-url: 'https://registry.npmjs.org'
      - run: npm ci
      - run: npm run build
      - run: npm publish --provenance --access public
        env:
          NODE_AUTH_TOKEN: ${{ secrets.NPM_TOKEN }}
```

`--provenance` requires `id-token: write`; the resulting publish has a Sigstore-backed attestation visible on npmjs.com.

### Trusted Publishing (no NPM_TOKEN)

Beta, but worth tracking. Configure on npmjs.com → package settings → Trusted publishers → Add publisher. Specify the GitHub repo, workflow name, and (optionally) environment. The workflow then publishes via OIDC alone:

```yaml
permissions:
  contents: read
  id-token: write

jobs:
  publish:
    environment: npm-publish
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-node@v6
        with: { node-version: '22', registry-url: 'https://registry.npmjs.org' }
      - run: npm ci
      - run: npm run build
      - run: npm publish --provenance --access public
        # No NODE_AUTH_TOKEN needed
```

### Release-please / changesets

For release automation:
- **Changesets** — file-based version management for monorepos. Pairs with `changesets/action` for the release PR.
- **release-please** — Google's tool; manages versions and changelogs from conventional commits.

Both integrate with GitHub Actions and emit publish steps once a release PR is merged.

## Common gotchas

- **`npm ci` requires `package-lock.json`** to be in sync with `package.json`. If `package.json` was edited without re-locking, the run fails. (This is correct behavior — it catches drift.)
- **`actions/setup-node@v6` with `package-manager-cache: false`** is required when the workflow has elevated permissions and you don't want a poisoned cache to affect prod builds. See [security.md](security.md).
- **Native modules** (sharp, sqlite3, esbuild) have platform-specific binaries. Caching `~/.npm` is fine; caching `node_modules` cross-platform isn't.
- **Yarn Berry's PnP mode** doesn't create `node_modules`. Tools that walk `node_modules` (some scanners, IDE features) misbehave. Most CI tasks work fine.
- **Workspace protocols** (`workspace:*`, `workspace:^`) in package.json are pnpm/yarn-only. They fail under npm.
- **Avoid `npm install --force`** in CI — it suppresses the safety net of `npm ci`.
