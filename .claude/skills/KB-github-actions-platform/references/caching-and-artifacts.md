# Caching and Artifacts

Two related but distinct mechanisms for moving data through workflows. Confusing them is a common source of slow or broken pipelines.

| Use case | Mechanism |
|---|---|
| Speed up dependency installation across runs | Cache (`actions/cache` or `cache:` input on setup actions) |
| Pass build outputs between jobs in the same run | Artifact (`actions/upload-artifact` + `actions/download-artifact`) |
| Distribute build outputs after the run (download, attach to a release) | Artifact + GitHub UI / API |
| Persist data across runs not tied to specific dependencies | Cache (less ideal) or external storage (S3, etc.) |

## Table of contents

- [Caching](#caching)
- [Cache key design](#cache-key-design)
- [Built-in caching in setup actions](#built-in-caching-in-setup-actions)
- [Artifacts](#artifacts)
- [Artifact v4 and the breaking changes](#artifact-v4-and-the-breaking-changes)
- [Cross-job artifact patterns](#cross-job-artifact-patterns)
- [Common pitfalls](#common-pitfalls)

## Caching

`actions/cache@v4` saves and restores files keyed by a string. Hits make subsequent runs faster; misses save fresh content for next time.

```yaml
- uses: actions/cache@v4
  with:
    path: ~/.npm
    key: ${{ runner.os }}-npm-${{ hashFiles('**/package-lock.json') }}
    restore-keys: |
      ${{ runner.os }}-npm-
```

### How it works

1. On a hit (key matches an existing cache entry): the path is restored.
2. On a miss: nothing is restored. After the job, the path is uploaded with the given key.
3. `restore-keys:` is a list of fallback prefixes — partial matches restore approximate caches.

### Limits

- 10 GB total cache size per repository (older entries evicted).
- Cache entries unused for 7 days are automatically deleted.
- Cache is scoped: caches written on the default branch are restorable from any branch; caches written on a feature branch are restorable from that branch and its descendants.

## Cache key design

The key is the most important decision. Wrong key = either no hit (slow) or stale content (broken).

### Pattern: lockfile-derived

```yaml
key: ${{ runner.os }}-npm-${{ hashFiles('**/package-lock.json') }}
```

- `hashFiles('**/package-lock.json')` is a SHA-256 of the lockfile content. Changes when deps change. Stable when deps don't.
- Including `runner.os` prevents Linux caches from being restored on macOS/Windows (which would fail or worse).

### Pattern: with restore-key fallbacks

```yaml
key: ${{ runner.os }}-npm-${{ hashFiles('**/package-lock.json') }}
restore-keys: |
  ${{ runner.os }}-npm-
  ${{ runner.os }}-
```

When the exact key doesn't hit, GitHub looks for the longest matching `restore-keys` prefix. This restores a "close enough" cache (e.g., from yesterday's lockfile), and your install command (`npm ci`, `pip install`) updates only what changed. Often dramatically faster than no cache.

### Pattern: include tool version

```yaml
key: ${{ runner.os }}-py${{ matrix.python }}-${{ hashFiles('requirements*.txt') }}
```

Different Python minor versions have different wheel artifacts; segregate by version.

### Anti-pattern: time-based keys

```yaml
key: ${{ runner.os }}-npm-${{ github.run_id }}    # ☠️
```

`run_id` is unique per run, so this never hits. Useless.

### Anti-pattern: keys without lockfile dependency

```yaml
key: ${{ runner.os }}-npm    # ☠️
```

Always hits the same key; cache becomes stale and you might never see updated dependencies.

## Built-in caching in setup actions

The setup-* actions have a `cache:` input that handles caching automatically:

```yaml
- uses: actions/setup-node@v6
  with:
    node-version: '22'
    cache: npm                        # also: yarn, pnpm
    cache-dependency-path: subdir/package-lock.json   # optional override

- uses: actions/setup-python@v6
  with:
    python-version: '3.13'
    cache: pip                        # also: pipenv, poetry
    cache-dependency-path: requirements*.txt

- uses: actions/setup-go@v6
  with:
    go-version: '1.23'
    cache: true                       # auto-detects go.sum
```

These usually beat hand-rolled `actions/cache` because they know the language's idioms (which paths to cache, how to handle multi-lockfile monorepos).

**Note:** `setup-node@v6+` enables npm caching by default if `package.json` declares `packageManager` or `devEngines.packageManager` set to npm. Disable with `package-manager-cache: false` for elevated-privilege workflows where caching could be a poisoning vector.

## Artifacts

Used to pass files between jobs in the same workflow run, or to surface build outputs to users via the UI.

```yaml
- uses: actions/upload-artifact@v4
  with:
    name: build-output
    path: dist/
    retention-days: 7         # default 90; max 90 unless repo policy raised
    if-no-files-found: error  # warn (default) | error | ignore
    compression-level: 6      # 0-9; 6 is default, 0 for already-compressed content

- uses: actions/download-artifact@v5
  with:
    name: build-output         # the same name from upload
    path: ./local-dir
```

Without `name:`, both actions use the default `artifact`.

### Multiple paths per artifact

```yaml
- uses: actions/upload-artifact@v4
  with:
    name: test-results
    path: |
      coverage/
      junit.xml
      screenshots/
      !coverage/lcov.info
```

Wildcards and exclusions (`!`) supported.

## Artifact v4 and the breaking changes

`actions/upload-artifact@v4` and `download-artifact@v4+` are not compatible with v3. Don't mix them in the same run.

Key changes from v3:
- **Each artifact upload is immutable.** You can't append to an existing artifact name in the same run. Uploading the same name twice now errors.
- **Up to 10× faster** for large artifacts.
- **Up to 500 artifacts per workflow run** (vs unlimited in v3).
- Artifacts are stored as zip archives (v4) or, since 2026, can be uploaded non-zipped if `archive: false`.
- Cross-OS download: the same artifact can be downloaded on any OS (v3 had Linux-line-ending issues).

### v4 download patterns

```yaml
# Download a single named artifact
- uses: actions/download-artifact@v5
  with:
    name: build-output
    path: ./dist

# Download all artifacts (no name)
- uses: actions/download-artifact@v5
  with:
    path: ./all-artifacts/      # creates ./all-artifacts/<name>/ for each

# Download by pattern
- uses: actions/download-artifact@v5
  with:
    pattern: build-*             # wildcard match
    path: ./builds/
    merge-multiple: true         # combine into one directory (otherwise one per artifact)
```

### v3 → v4 migration gotchas

- v3 allowed appending to an artifact across multiple upload steps in one run; v4 doesn't. Workaround: give each upload a unique name (e.g., `name: ${{ matrix.shard }}-results`), then download with `pattern:` and `merge-multiple: true`.
- v3 had unlimited artifacts; v4 caps at 500 per run. Hit by matrix workflows that upload per permutation.

## Cross-job artifact patterns

### Build once, deploy in many environments

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - run: npm ci && npm run build
      - uses: actions/upload-artifact@v4
        with:
          name: app-build
          path: dist/

  deploy:
    needs: build
    strategy:
      matrix:
        env: [staging, production]
    runs-on: ubuntu-latest
    environment: ${{ matrix.env }}
    steps:
      - uses: actions/download-artifact@v5
        with: { name: app-build, path: dist/ }
      - run: ./deploy.sh ${{ matrix.env }}
```

Same build artifact deployed to multiple environments — guarantees identical bits.

### Matrix → fan-in aggregation

```yaml
jobs:
  test:
    strategy:
      matrix:
        shard: [1, 2, 3, 4]
    runs-on: ubuntu-latest
    steps:
      - run: ./run-tests --shard=${{ matrix.shard }} --report=results-${{ matrix.shard }}.json
      - uses: actions/upload-artifact@v4
        with:
          name: results-${{ matrix.shard }}
          path: results-${{ matrix.shard }}.json

  aggregate:
    needs: test
    if: always()
    runs-on: ubuntu-latest
    steps:
      - uses: actions/download-artifact@v5
        with:
          pattern: results-*
          path: results/
          merge-multiple: true
      - run: ./summarize results/*.json
```

### Cross-run artifact access (`workflow_run`)

```yaml
on:
  workflow_run:
    workflows: [CI]
    types: [completed]

jobs:
  comment:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/download-artifact@v5
        with:
          run-id: ${{ github.event.workflow_run.id }}
          github-token: ${{ secrets.GITHUB_TOKEN }}
          name: results
```

This is the safe way for a privileged workflow to pick up build outputs from a fork-PR CI run.

## Common pitfalls

- **Cache stores empty path silently.** If `path:` doesn't exist when the job ends, `actions/cache` saves an empty cache. Next run "hits" but restores nothing, and you wonder why install is still slow. Verify the path exists.
- **Cache key changes invalidate restore-keys too coarsely.** If you bump the OS family in the key, every prefix-matching restore key still hits within the same family. Plan keys to reflect actual cache validity.
- **Artifact name collisions in matrix jobs.** All four matrix shards uploading `name: results` will conflict (v4 errors). Include matrix variables in the name.
- **Forgot to `actions/checkout` before composite action**. Local actions referenced via `./.github/actions/foo` need the working tree on disk.
- **`cache: npm` without `package-lock.json`.** The cache key falls back to `package.json`, which is less stable. Always commit a lockfile.
- **Using `actions/cache` for things that change every run.** Test results, build outputs — those are artifacts, not cache.
- **Tarballing into a cache.** Tarring `node_modules` into a single file before caching is rarely faster than caching `~/.npm` or `~/.cache/yarn` and reinstalling. Profile before optimizing.
- **Unbounded retention.** Default 90-day artifact retention adds up. Set `retention-days:` to the minimum useful value (1 for ephemeral, 7 for typical CI, 30+ for releases).
