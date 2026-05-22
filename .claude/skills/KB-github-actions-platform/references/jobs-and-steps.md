# Jobs and Steps

Everything about how jobs are structured, ordered, and parameterized: dependencies, outputs, conditionals, matrix strategies, services, and step mechanics.

## Table of contents

- [Job basics](#job-basics)
- [Dependencies with `needs:`](#dependencies-with-needs)
- [Outputs](#outputs)
- [Conditional execution](#conditional-execution)
- [Matrix strategy](#matrix-strategy)
- [Service containers](#service-containers)
- [Container jobs](#container-jobs)
- [Step mechanics](#step-mechanics)
- [Sharing data between steps](#sharing-data-between-steps)
- [Common patterns](#common-patterns)

## Job basics

```yaml
jobs:
  build:
    name: Build (optional display name)
    runs-on: ubuntu-latest
    timeout-minutes: 15
    steps:
      - uses: actions/checkout@v6
      - run: make build
```

Jobs run in parallel unless you use `needs:`.

## Dependencies with `needs:`

```yaml
jobs:
  lint:
    runs-on: ubuntu-latest
    steps: [...]

  test:
    needs: lint           # waits for lint to succeed
    runs-on: ubuntu-latest
    steps: [...]

  build:
    needs: [lint, test]   # waits for both
    runs-on: ubuntu-latest
    steps: [...]

  deploy:
    needs: build
    runs-on: ubuntu-latest
    steps: [...]
```

By default, a job is skipped if any of its `needs:` jobs failed or was skipped. Override with `if: always()` or specific status checks:

```yaml
notify:
  needs: [lint, test, build]
  if: always()           # run regardless of outcomes
  runs-on: ubuntu-latest
  steps:
    - if: needs.build.result == 'failure'
      run: ./notify-failure.sh
```

### `if: always()` cascade gotcha

If a job uses `if: always()` and depends on a skipped job, you may want it to *also* be skipped, not run. The pattern:

```yaml
notify:
  needs: [build]
  if: ${{ !cancelled() && needs.build.result != 'skipped' }}
```

## Outputs

Jobs can publish outputs that downstream jobs consume.

```yaml
jobs:
  prepare:
    runs-on: ubuntu-latest
    outputs:
      version: ${{ steps.bump.outputs.version }}
      changed: ${{ steps.diff.outputs.changed }}
    steps:
      - id: bump
        run: echo "version=$(cat VERSION)" >> "$GITHUB_OUTPUT"
      - id: diff
        run: |
          if git diff --quiet HEAD~1 -- src/; then
            echo "changed=false" >> "$GITHUB_OUTPUT"
          else
            echo "changed=true" >> "$GITHUB_OUTPUT"
          fi

  build:
    needs: prepare
    if: needs.prepare.outputs.changed == 'true'
    runs-on: ubuntu-latest
    steps:
      - run: echo "Building ${{ needs.prepare.outputs.version }}"
```

**Step outputs syntax** (since 2022; `set-output` is deprecated):

```yaml
- id: my-step
  run: |
    echo "name=value" >> "$GITHUB_OUTPUT"
    echo "another=42" >> "$GITHUB_OUTPUT"
```

Multi-line values use heredoc:

```yaml
- id: notes
  run: |
    {
      echo 'notes<<EOF'
      cat CHANGELOG.md
      echo 'EOF'
    } >> "$GITHUB_OUTPUT"
```

**Output size limits:** total step outputs are capped at 1 MB per job, 50 MB per workflow run. For large data, write a file and upload as an artifact.

**Outputs from matrix jobs:** all matrix permutations have the same output keys; downstream jobs see the *last* one's outputs (or the first that wrote, depending on race). To collect outputs from all matrix permutations, write to artifacts or use a fan-in job that reads them.

## Conditional execution

`if:` can appear at the workflow (limited), job, and step level.

### Job-level `if:`

```yaml
deploy:
  if: github.ref == 'refs/heads/main' && github.event_name == 'push'
  runs-on: ubuntu-latest
  steps: [...]
```

A job whose `if:` evaluates false is *skipped*, not *failed*. Downstream `needs:` will see `result: skipped`.

### Step-level `if:`

```yaml
- name: Upload coverage
  if: success() && matrix.os == 'ubuntu-latest'
  uses: codecov/codecov-action@SHA
```

### Status functions in `if:`

- `success()` (default if no `if:`)
- `failure()` — any previous step failed
- `cancelled()` — workflow was cancelled
- `always()` — always run

```yaml
- name: Cleanup
  if: always()
  run: rm -rf /tmp/build

- name: Notify
  if: failure() || cancelled()
  run: ./notify.sh
```

## Matrix strategy

Run the same job multiple times across combinations of variables.

```yaml
jobs:
  test:
    strategy:
      fail-fast: false       # default true: stop all matrix jobs on first failure
      max-parallel: 5        # default: as many as account allows
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        python: ['3.10', '3.11', '3.12', '3.13']
        # 12 combinations
        exclude:
          - os: windows-latest
            python: '3.10'
          # now 11
        include:
          - os: ubuntu-latest
            python: '3.13'
            extra-flag: --experimental
          # now 12, the included one has an extra dimension
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/setup-python@v6
        with:
          python-version: ${{ matrix.python }}
      - run: pytest ${{ matrix.extra-flag || '' }}
```

Notes:
- `fail-fast: false` is usually what you want for testing — let other matrix jobs finish so you see the full picture.
- `include:` adds new combinations or extends existing ones with extra fields.
- `exclude:` removes specific combinations.
- The matrix variables become available in the `matrix` context.

### Dynamic matrix

Generate the matrix at runtime using a setup job:

```yaml
jobs:
  setup:
    runs-on: ubuntu-latest
    outputs:
      matrix: ${{ steps.discover.outputs.matrix }}
    steps:
      - uses: actions/checkout@v6
      - id: discover
        run: |
          # e.g. discover all packages in a monorepo
          packages=$(ls packages | jq -R . | jq -s .)
          echo "matrix=$(echo "{\"package\": $packages}" | jq -c .)" >> "$GITHUB_OUTPUT"

  test:
    needs: setup
    strategy:
      matrix: ${{ fromJSON(needs.setup.outputs.matrix) }}
    runs-on: ubuntu-latest
    steps:
      - run: echo "Testing ${{ matrix.package }}"
```

This unlocks "test only changed packages" workflows.

## Service containers

Service containers run alongside the job and are network-reachable as hostnames matching the service ID. Ideal for databases in CI.

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_PASSWORD: postgres
          POSTGRES_USER: postgres
          POSTGRES_DB: test
        ports:
          - 5432:5432
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
      redis:
        image: redis:7
        ports:
          - 6379:6379
        options: >-
          --health-cmd "redis-cli ping"
          --health-interval 10s
    steps:
      - uses: actions/checkout@v6
      - env:
          DATABASE_URL: postgres://postgres:postgres@localhost:5432/test
          REDIS_URL: redis://localhost:6379
        run: ./run-tests.sh
```

Notes:
- If the job runs on the host (i.e., not in a `container:`), services are reachable on `localhost:<port>`.
- If the job runs in a `container:`, services are reachable on `<service-id>:<port>` (Docker network DNS).
- Services start before the first step. The `--health-cmd` ensures readiness; without it, your tests may race the service's startup.

## Container jobs

Run the entire job inside a container. Useful for reproducible tool versions across runners or when the host runner doesn't have what you need.

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    container:
      image: node:22-bookworm
      env:
        NODE_ENV: production
      ports: []
      volumes: []
      options: --cpus 2
    steps:
      - uses: actions/checkout@v6   # checkout works inside the container
      - run: node --version
```

Trade-offs:
- Slower startup (container pull adds ~10–30s).
- Some actions don't run inside containers (anything needing host access).
- The `actions/setup-*` actions still work but install tools inside the container.

## Step mechanics

```yaml
steps:
  - name: Display name
    id: my-id
    if: condition
    uses: org/action@SHA            # OR
    run: |
      multi-line shell script
    shell: bash                     # default on Linux/macOS
    working-directory: ./subdir
    env:
      KEY: value
    with:                           # only with `uses:`
      input: value
    continue-on-error: false
    timeout-minutes: 5
```

A step has either `uses:` or `run:`, not both.

### Available shells

- Linux/macOS: `bash` (default), `sh`, `python`, `pwsh`
- Windows: `pwsh` (default), `cmd`, `bash` (Git Bash), `python`, `powershell`

`bash` on GitHub-hosted runners runs in `bash --noprofile --norc -eo pipefail` — meaning script failures stop execution. Custom shells: `shell: 'perl {0}'` runs the run block as `perl /path/to/script`.

### `working-directory`

Default is `$GITHUB_WORKSPACE` (the checkout root). Override per step or via `defaults.run.working-directory:` at the job/workflow level.

## Sharing data between steps

Three mechanisms, in order of preference for most use cases:

### 1. Step outputs

Best for small, structured values. See [Outputs](#outputs).

### 2. Environment variables (`$GITHUB_ENV`)

```yaml
- run: echo "BUILD_ID=$(date +%s)" >> "$GITHUB_ENV"
- run: echo "Build is $BUILD_ID"
```

`$GITHUB_ENV` writes to a file that GitHub processes between steps to set actual environment variables for subsequent steps. Outputs are accessed via `${{ ... }}` interpolation; env vars via `$VAR` shell syntax. Env vars are not redacted in logs unless they're secrets.

### 3. Files

Write to `$RUNNER_TEMP/` for ephemeral data, or to `$GITHUB_WORKSPACE/` for stuff downstream jobs need (use upload-artifact to share across jobs).

```yaml
- run: |
    mkdir -p "$RUNNER_TEMP/build"
    cp -r dist/ "$RUNNER_TEMP/build/"
    echo "BUILD_DIR=$RUNNER_TEMP/build" >> "$GITHUB_ENV"
```

## Job summary

Each job has a Markdown summary file at `$GITHUB_STEP_SUMMARY`. Anything appended to it shows in the workflow run UI.

```yaml
- run: |
    {
      echo "## Test Results"
      echo "| Suite | Passed | Failed |"
      echo "|---|---|---|"
      echo "| Unit | $unit_pass | $unit_fail |"
    } >> "$GITHUB_STEP_SUMMARY"
```

Useful for: test summaries, deployment URLs, build sizes, links to artifacts.

## Common patterns

### Continue-but-record-failure

You want the workflow to run all jobs but mark the run as failed if any of a group fails.

```yaml
jobs:
  lint:
    continue-on-error: true     # job-level: don't fail the workflow yet
    runs-on: ubuntu-latest
    steps: [...]
  test:
    continue-on-error: true
    runs-on: ubuntu-latest
    steps: [...]
  result:
    needs: [lint, test]
    if: always()
    runs-on: ubuntu-latest
    steps:
      - if: needs.lint.result != 'success' || needs.test.result != 'success'
        run: |
          echo "::error::One or more checks failed"
          exit 1
```

The `result` job aggregates and is what branch protection cares about.

### Re-run a single job

A failed job can be re-run from the UI ("Re-run failed jobs"). Use stable job IDs and avoid timestamps in IDs so re-runs are predictable.

### Skip duplicate workflow runs

If the same SHA gets pushed twice (e.g., a force-push), use `concurrency:` with `cancel-in-progress: true` keyed on `github.workflow + github.ref` to cancel the older run automatically. See [concurrency-and-environments.md](concurrency-and-environments.md).

### Pass data from matrix to fan-in job

Matrix jobs all write to the same outputs; the last to finish wins. To collect from all permutations, write artifacts:

```yaml
test:
  strategy:
    matrix:
      shard: [1, 2, 3, 4]
  runs-on: ubuntu-latest
  steps:
    - run: ./run-tests.sh --shard=${{ matrix.shard }} --report=report-${{ matrix.shard }}.json
    - uses: actions/upload-artifact@v4
      with:
        name: test-report-${{ matrix.shard }}
        path: report-${{ matrix.shard }}.json

aggregate:
  needs: test
  if: always()
  runs-on: ubuntu-latest
  steps:
    - uses: actions/download-artifact@v5
      with:
        pattern: test-report-*
        path: reports/
        merge-multiple: true
    - run: ./aggregate-reports.sh reports/
```
