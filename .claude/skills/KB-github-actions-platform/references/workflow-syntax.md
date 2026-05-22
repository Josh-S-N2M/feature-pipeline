# Workflow Syntax Reference

Complete YAML syntax for GitHub Actions workflows. This reference is task-oriented: skim the table of contents, jump to what you need.

## Table of contents

- [File location](#file-location)
- [Top-level keys](#top-level-keys)
- [`name`, `run-name`](#name-run-name)
- [`on` — triggers](#on--triggers)
- [`permissions`](#permissions)
- [`env`](#env)
- [`defaults`](#defaults)
- [`concurrency`](#concurrency)
- [`jobs`](#jobs)
- [Job-level keys](#job-level-keys)
- [`steps`](#steps)
- [Step-level keys](#step-level-keys)
- [Reusable workflow callers](#reusable-workflow-callers)
- [Common gotchas](#common-gotchas)

## File location

Workflows live in `.github/workflows/` at the repository root. The file extension must be `.yml` or `.yaml`. The filename is arbitrary, but conventional names: `ci.yml`, `release.yml`, `deploy.yml`. The filename is what shows in the Actions UI sidebar unless `name:` is set.

## Top-level keys

```yaml
name: Optional, the human-readable name shown in the Actions UI
run-name: Optional, the dynamic name shown for individual runs
on: required — what triggers this workflow
permissions: defaults for all jobs unless overridden
env: workflow-level environment variables
defaults: shell and working-directory defaults
concurrency: workflow-level concurrency control
jobs: required — the actual work
```

## `name`, `run-name`

`name:` is static. `run-name:` is dynamic and supports expressions referencing `github.*` and `inputs.*` (but not `secrets.*` or `env.*`).

```yaml
name: CI
run-name: ${{ github.actor }} — ${{ github.event_name }} on ${{ github.ref_name }}
```

## `on` — triggers

Three forms: scalar, list, or map. The map form lets you filter by branch, tag, path, or event activity type.

```yaml
# Scalar form
on: push

# List form
on: [push, pull_request]

# Map form (most common in practice)
on:
  push:
    branches: [main, 'release/**']
    paths-ignore: ['docs/**', '**.md']
  pull_request:
    branches: [main]
    types: [opened, synchronize, reopened, ready_for_review]
  schedule:
    - cron: '0 6 * * 1-5'   # 06:00 UTC, Mon-Fri
  workflow_dispatch:
    inputs:
      environment:
        type: environment
        required: true
      log_level:
        type: choice
        options: [debug, info, warn, error]
        default: info
  workflow_call:
    inputs:
      target:
        type: string
        required: true
    secrets:
      DEPLOY_TOKEN:
        required: true
```

For the full list of events and their gotchas (especially `pull_request_target`, `workflow_run`, fork PR token scopes), see [events-and-triggers.md](events-and-triggers.md).

### Branch and path filters

- `branches:` / `branches-ignore:` — match by branch ref (no `refs/heads/` prefix). Supports glob: `release/**`.
- `tags:` / `tags-ignore:` — match by tag ref.
- `paths:` / `paths-ignore:` — only run if the diff touches these paths. Supports glob.
- Don't combine `branches:` with `branches-ignore:` in the same trigger; pick one.
- Filters do not apply to `workflow_dispatch` or `workflow_call` (those are explicit invocations).

## `permissions`

Controls the scopes of the `GITHUB_TOKEN` used by all jobs. Always declare this explicitly. Possible values:

```yaml
permissions:
  actions: read | write | none
  attestations: read | write | none
  checks: read | write | none
  contents: read | write | none
  deployments: read | write | none
  discussions: read | write | none
  id-token: write | none           # required for OIDC
  issues: read | write | none
  models: read | none
  packages: read | write | none
  pages: read | write | none
  pull-requests: read | write | none
  repository-projects: read | write | none
  security-events: read | write | none
  statuses: read | write | none
```

Shorthand:

```yaml
permissions: read-all      # all read scopes
permissions: write-all     # all write scopes (avoid)
permissions: {}            # no permissions at all (token has nothing)
```

Set at the workflow level for defaults; override per job when one job needs more.

## `env`

Environment variables exposed to all steps. Can be set at workflow, job, or step level (most-specific wins). Step-level `env:` is the only place for secrets that should not leak across steps.

```yaml
env:
  NODE_ENV: production
  CI: true
```

## `defaults`

Default `shell` and `working-directory` for all `run:` steps. Useful when most jobs use the same subdirectory or the same non-default shell.

```yaml
defaults:
  run:
    shell: bash
    working-directory: ./packages/api
```

Available shells: `bash`, `pwsh`, `python`, `sh`, `cmd`, `powershell`. Linux/macOS default: `bash`. Windows default: `pwsh`.

## `concurrency`

Workflow-level. Same shape as job-level. See [concurrency-and-environments.md](concurrency-and-environments.md).

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

## `jobs`

A map of job IDs to job definitions. Job IDs must start with a letter or `_` and contain only alphanumeric, `-`, `_`. The ID is what other jobs use in `needs:`.

## Job-level keys

```yaml
jobs:
  job-id:
    name: Optional human-readable name
    runs-on: ubuntu-latest                    # required (unless `uses:` is set)
    needs: [other-job-id]                     # depends on these jobs
    if: ${{ github.event_name == 'push' }}    # job-level conditional
    permissions:                               # override workflow-level
      contents: read
    environment:                               # links to GitHub Environment
      name: production
      url: https://example.com
    concurrency:                               # job-level concurrency
      group: deploy-${{ matrix.region }}
      cancel-in-progress: false
    timeout-minutes: 30                        # default 360 (6h) — set lower
    continue-on-error: false                   # if true, failure won't fail the workflow
    strategy:                                  # matrix / fail-fast / max-parallel
      fail-fast: false
      max-parallel: 4
      matrix:
        os: [ubuntu-latest, macos-latest]
        node: [20, 22]
        include:
          - os: ubuntu-latest
            node: 22
            extra: special
        exclude:
          - os: macos-latest
            node: 20
    services:                                  # docker services for the job
      postgres:
        image: postgres:16
        env:
          POSTGRES_PASSWORD: postgres
        ports: ['5432:5432']
        options: --health-cmd pg_isready --health-interval 10s
    container:                                 # run the job inside a container
      image: node:22-bookworm
      env: { CI: 'true' }
    defaults:
      run:
        shell: bash
        working-directory: ./api
    env:
      JOB_LEVEL: value
    outputs:                                   # outputs consumed by other jobs via needs.*
      version: ${{ steps.bump.outputs.version }}
    steps:
      # ...
```

### Reusable workflow caller form

```yaml
jobs:
  call-reusable:
    uses: org/repo/.github/workflows/build.yml@v1.2.3
    with:
      target: prod
    secrets:
      TOKEN: ${{ secrets.DEPLOY_TOKEN }}
    # Or, if the caller can pass all of its secrets through:
    # secrets: inherit
```

A job that uses `uses:` cannot have `steps:`, `runs-on:`, `container:`, or `services:`. It calls another workflow as a unit.

## `steps`

A list of steps inside a job. Steps share the same runner and filesystem; they pass data via files, environment variables, or step outputs.

## Step-level keys

```yaml
steps:
  - name: Optional human-readable name
    id: my-step                                # used to reference outputs
    if: ${{ steps.previous.outcome == 'success' }}
    uses: org/action@SHA                       # OR run, not both
    with:                                      # inputs to the action
      key: value
    run: |                                     # OR uses, not both
      echo "hello"
    shell: bash
    working-directory: ./subdir
    env:
      STEP_VAR: value
    continue-on-error: false
    timeout-minutes: 5
```

A step has either `uses:` or `run:`, never both.

### Step outputs

Modern syntax (since 2022, `set-output` is deprecated):

```yaml
- id: bump
  run: |
    echo "version=1.2.3" >> "$GITHUB_OUTPUT"
- run: echo "Got ${{ steps.bump.outputs.version }}"
```

Multi-line values use heredoc form:

```yaml
- id: notes
  run: |
    {
      echo 'notes<<EOF'
      cat CHANGELOG.md
      echo 'EOF'
    } >> "$GITHUB_OUTPUT"
```

## Reusable workflow callers

A job calling a reusable workflow has a different shape from a regular job:

```yaml
jobs:
  build:
    uses: ./.github/workflows/build.yml          # same repo, by path
    # OR
    uses: org/repo/.github/workflows/build.yml@v1.2.3
    with:
      input1: value
    secrets: inherit
    permissions:
      contents: read
      id-token: write
```

`permissions:` here applies to the job invocation; the reusable workflow itself can also declare `permissions:` and the union must satisfy what its actions need.

## Common gotchas

- **`runs-on:` requires a value or list of labels.** `ubuntu-latest` is a magic label that resolves to the current default Ubuntu runner. Use specific labels (`ubuntu-22.04`, `ubuntu-24.04`) for reproducibility-sensitive workflows. The "latest" label can shift unexpectedly.
- **`if:` evaluates strings.** `if: ${{ inputs.deploy }}` is true even when `inputs.deploy` is the string `"false"`. Use `if: ${{ inputs.deploy == 'true' }}` or `if: ${{ fromJSON(inputs.deploy) }}`.
- **YAML booleans coerce.** `on: push: branches: [yes, no]` will be interpreted as `[true, false]` because YAML 1.1 treats `yes`/`no` as booleans. Quote: `branches: ['yes', 'no']`.
- **`needs:` with a single job is a string, not a list:** `needs: build`. With multiple, it's a list: `needs: [build, test]`.
- **Job-level `permissions:` replaces, doesn't merge.** Setting one permission at the job level removes all others — even those granted at the workflow level.
- **`continue-on-error:` masks failures.** A step with `continue-on-error: true` shows green even if it failed. The job's `outcome` is still `failure`, but `conclusion` is `success`. This breaks downstream `if: failure()` conditions in unexpected ways.
- **`env:` doesn't expand at parse time.** You can't reference one `env:` from another in the same block. Set them in a `run:` step that writes to `$GITHUB_ENV` if you need composition.
- **`uses:` with a local path** (`./.github/actions/foo`) requires `actions/checkout` to have run first in that job; otherwise the action file isn't on disk.
- **`workflow_dispatch` inputs are always strings** when accessed via `github.event.inputs.*`; use `inputs.*` (typed) instead, or wrap with `fromJSON()` for booleans.
