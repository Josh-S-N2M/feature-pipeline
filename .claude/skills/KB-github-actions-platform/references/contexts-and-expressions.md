# Contexts and Expressions

GitHub Actions provides runtime data through **contexts** and lets you compute on them with **expressions** wrapped in `${{ ... }}`. Knowing what's available where is crucial — many bugs come from referencing a context that isn't populated for the current event.

## Table of contents

- [Expression syntax](#expression-syntax)
- [The contexts](#the-contexts)
- [Functions](#functions)
- [Status check functions](#status-check-functions)
- [Operators](#operators)
- [Context availability matrix](#context-availability-matrix)
- [Common patterns](#common-patterns)

## Expression syntax

Wrap in `${{ ... }}`. Used in `if:`, `with:`, `env:`, `run:` (and many other places).

```yaml
- if: ${{ github.event_name == 'pull_request' }}
- run: echo "${{ inputs.message }}"
- env:
    REGION: ${{ matrix.region }}
```

In `if:` keys, the `${{ ... }}` wrapper is *optional* and increasingly omitted in modern workflows:

```yaml
if: github.event_name == 'pull_request'
```

Both forms work. The wrapper version is required everywhere else.

## The contexts

### `github`

Metadata about the workflow run. Always available.

Common fields:
- `github.actor` — username that triggered the run
- `github.actor_id` — numeric user ID
- `github.event_name` — `push`, `pull_request`, `workflow_dispatch`, etc.
- `github.event` — full event payload (huge, schema varies by event)
- `github.ref` — full git ref (e.g. `refs/heads/main`, `refs/pull/42/merge`, `refs/tags/v1.2.3`)
- `github.ref_name` — short name (e.g. `main`, `42/merge`, `v1.2.3`)
- `github.ref_type` — `branch` or `tag`
- `github.head_ref` — source branch of a PR (only on `pull_request`/`pull_request_target`)
- `github.base_ref` — target branch of a PR
- `github.sha` — commit SHA the workflow runs against (for PRs, the merge SHA)
- `github.repository` — `owner/name`
- `github.repository_owner` — `owner`
- `github.workspace` — checkout root path
- `github.workflow` — workflow name
- `github.workflow_ref` — `owner/repo/.github/workflows/foo.yml@refs/heads/main`
- `github.run_id`, `github.run_number`, `github.run_attempt`
- `github.token` — equivalent to `secrets.GITHUB_TOKEN`
- `github.api_url`, `github.server_url`
- `github.triggering_actor` — the user who re-ran a workflow (may differ from `github.actor`)

### `env`

Environment variables defined in `env:` blocks. Note: `env` does NOT contain shell environment variables set inside `run:` steps via `$GITHUB_ENV`; those are accessed in subsequent steps as actual environment variables, not via this context.

### `vars`

Repository, environment, or organization **variables** (non-secret config). Configured in repo/org settings.

```yaml
- run: echo "Building for ${{ vars.DEPLOY_REGION }}"
```

Useful for non-secret config that varies by environment (regions, URLs, feature flags).

### `secrets`

Repository, environment, or organization **secrets**. Masked in logs.

```yaml
- env:
    API_KEY: ${{ secrets.API_KEY }}
```

`secrets.GITHUB_TOKEN` is the auto-generated token for this run. Its scopes are determined by the `permissions:` block.

**Empty secrets stay empty:** `if: ${{ secrets.OPTIONAL != '' }}` works even if the secret isn't defined.

### `inputs`

Typed inputs for `workflow_dispatch` and `workflow_call`. Always available when those triggered the run.

```yaml
on:
  workflow_dispatch:
    inputs:
      env: { type: choice, options: [dev, prod] }

# Later:
- if: inputs.env == 'prod'
  run: deploy --target=prod
```

`github.event.inputs.*` exists too but values are always strings — `inputs.*` preserves types.

### `needs`

Outputs and result of jobs this job depends on. See [jobs-and-steps.md](jobs-and-steps.md) for outputs.

```yaml
needs: [build]
# ...
- run: echo "Built ${{ needs.build.outputs.version }}"
- if: needs.build.result == 'success'
```

`needs.<job>.result` is one of: `success`, `failure`, `cancelled`, `skipped`.

### `matrix`

The current matrix combination's values. Only available in jobs with a `strategy.matrix:`.

```yaml
strategy:
  matrix:
    os: [ubuntu-latest, macos-latest]
    node: [20, 22]
runs-on: ${{ matrix.os }}
steps:
  - run: echo "Node ${{ matrix.node }} on ${{ matrix.os }}"
```

### `strategy`

Within a matrix job, exposes job-fail-fast and indices. Rarely used.

- `strategy.fail-fast` — true/false
- `strategy.job-index` — current index in the matrix expansion (0-based)
- `strategy.job-total` — total number of jobs in the matrix
- `strategy.max-parallel`

### `runner`

Runner machine info.

- `runner.os` — `Linux`, `Windows`, `macOS`
- `runner.arch` — `X86`, `X64`, `ARM`, `ARM64`
- `runner.name` — runner display name
- `runner.temp` — temp directory path
- `runner.tool_cache` — pre-installed tool cache path
- `runner.workspace` — base directory containing the workspace
- `runner.debug` — `'1'` if debug logging is enabled

### `job`

Info about the current job.

- `job.status` — `success`, `failure`, `cancelled` (computed up to the current step; useful in `if: always()` cleanup steps)
- `job.container.id`, `job.container.network` — if running in a container
- `job.services.<id>.id`, `.ports.<port>` — service container info

### `steps`

Outputs and outcomes of previous steps in the same job. Step must have an `id:`.

```yaml
- id: build
  run: echo "version=1.2.3" >> "$GITHUB_OUTPUT"
- run: echo "Built ${{ steps.build.outputs.version }}"
- if: steps.build.outcome == 'success'
```

`steps.<id>.outcome` — pre-`continue-on-error` result.
`steps.<id>.conclusion` — post-`continue-on-error` result.

## Functions

### Type / data manipulation

- `contains(haystack, needle)` — `contains('abc', 'b')`, `contains(github.event.commits.*.message, 'fix')`, `contains(fromJSON('["a","b"]'), 'a')`
- `startsWith(string, prefix)`
- `endsWith(string, suffix)`
- `format(template, args...)` — `format('Hello {0} {1}', 'World', '!')`
- `join(array, separator)` — defaults to `,` if no separator
- `toJSON(value)` — pretty-printed JSON. Useful for debugging: `run: echo '${{ toJSON(github.event) }}'`
- `fromJSON(string)` — parse JSON to object. Essential for matrix from job output.

### File hashing

- `hashFiles(path, ...)` — SHA-256 of all files matching the glob(s). Most-used: cache keys.

```yaml
key: ${{ runner.os }}-pip-${{ hashFiles('requirements*.txt') }}
```

If no files match, returns empty string.

## Status check functions

These functions evaluate workflow/job status and are mainly used in `if:`:

- `success()` — true if all previous steps succeeded (the default if `if:` isn't specified)
- `failure()` — true if any previous step failed
- `always()` — always true; runs the step even on cancellation. Use for cleanup.
- `cancelled()` — true if the workflow was cancelled

```yaml
- name: Cleanup
  if: always()
  run: ./cleanup.sh

- name: Notify on failure
  if: failure() && github.ref == 'refs/heads/main'
  run: ./notify-slack.sh
```

**`always()` defeats `cancelled()`** — if you write `if: always() && X`, the step runs on cancellation. Use `if: !cancelled() && failure()` for "run on failure but not on cancellation."

## Operators

Standard:
- Comparison: `==`, `!=`, `<`, `<=`, `>`, `>=`
- Logical: `&&`, `||`, `!`
- Grouping: `( )`
- Index: `[ ]` and `.`

Coercion: comparisons coerce to numbers if both sides are numeric strings, otherwise to strings.

`null` and missing fields evaluate to falsy. Empty string is also falsy.

## Context availability matrix

Not every context is available everywhere. Common surprises:

| Context | `concurrency:` (workflow) | `concurrency:` (job) | `if:` (workflow `concurrency`) | `runs-on:` | `env:` (workflow) | `if:` (step) |
|---|---|---|---|---|---|---|
| `github` | ✓ | ✓ | n/a | ✓ | ✓ | ✓ |
| `inputs` | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| `vars` | ✓ | ✓ | n/a | ✓ | ✓ | ✓ |
| `secrets` | ✗ | ✓ | n/a | ✗ | ✗ | ✓ |
| `env` | n/a | ✓ | n/a | ✓ | n/a | ✓ |
| `needs` | ✗ | ✓ | n/a | ✓ | ✗ | ✓ |
| `matrix` | ✗ | ✓ | n/a | ✓ | ✗ | ✓ |
| `steps` | ✗ | ✗ | n/a | ✗ | ✗ | ✓ |
| `runner` | ✗ | ✗ | n/a | ✗ | ✗ | ✓ |
| `job` | ✗ | ✗ | n/a | ✗ | ✗ | ✓ |

The big traps:
- **You can't use `secrets.*` in workflow-level `concurrency:` or `env:`.** Move it to the job level.
- **You can't use `matrix.*` outside the matrix job.** Compute the matrix as a job output and pass via `needs.<job>.outputs.*` to dependent jobs.

## Common patterns

### Conditional on branch

```yaml
if: github.ref == 'refs/heads/main'
# or
if: github.ref_name == 'main'
```

### Conditional on event

```yaml
if: github.event_name == 'push'
if: github.event_name == 'pull_request' && github.event.action == 'opened'
```

### Skip on draft PRs

```yaml
if: github.event_name != 'pull_request' || github.event.pull_request.draft == false
```

### Boolean from string input

```yaml
on:
  workflow_dispatch:
    inputs:
      deploy: { type: boolean }

jobs:
  deploy:
    if: inputs.deploy   # works because type: boolean is a real bool
    # vs github.event.inputs.deploy which is always 'true'/'false' strings
```

For string-typed inputs that need boolean semantics, use `fromJSON()`:

```yaml
if: fromJSON(inputs.flag)
```

### Dynamic matrix from job output

```yaml
jobs:
  setup:
    runs-on: ubuntu-latest
    outputs:
      matrix: ${{ steps.set.outputs.matrix }}
    steps:
      - id: set
        run: echo 'matrix={"target":["dev","stage","prod"]}' >> "$GITHUB_OUTPUT"
  fan-out:
    needs: setup
    strategy:
      matrix: ${{ fromJSON(needs.setup.outputs.matrix) }}
    runs-on: ubuntu-latest
    steps:
      - run: echo "Targeting ${{ matrix.target }}"
```

### Multi-line conditional

```yaml
if: >-
  github.event_name == 'push' &&
  github.ref == 'refs/heads/main' &&
  !contains(github.event.head_commit.message, '[skip deploy]')
```

The `>-` folds the multi-line scalar into a single line for parsing.

### Cache key with fallback

```yaml
key: ${{ runner.os }}-deps-${{ hashFiles('**/lockfile') }}
restore-keys: |
  ${{ runner.os }}-deps-
  ${{ runner.os }}-
```

### Print full event payload for debugging

```yaml
- env:
    EVENT: ${{ toJSON(github.event) }}
  run: echo "$EVENT"
```

(Don't interpolate directly into `run:` — it's a script-injection vector. Always go through env.)
