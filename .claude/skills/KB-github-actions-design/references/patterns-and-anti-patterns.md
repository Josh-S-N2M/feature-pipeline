# CI/CD Patterns and Anti-Patterns (GitHub Actions)

## Contents

- Workflow composition patterns
- Reusability patterns (workflow_call, composite, custom action)
- Concurrency patterns
- Environment topology patterns
- Deployment patterns
- Matrix and parallelization patterns
- Cache and artifact patterns
- Anti-patterns reviewers should flag
- Decision frames

## Workflow composition patterns

### Single CI workflow

```yaml
name: CI
on: pull_request

jobs:
  lint:    ...
  test:    ...
  build:   ...
```

**When to use.** PR validation; tightly-coupled jobs that share scope. Default for early projects.

### Separate CI and CD workflows

```yaml
# .github/workflows/ci.yml — on PR
# .github/workflows/cd-staging.yml — on push to main
# .github/workflows/cd-prod.yml — on workflow_dispatch
```

**When to use.** Default for production-grade setups. Each workflow has independent triggers, concurrency, secrets, timeouts.

### Orchestrated workflows

A "controller" workflow triggers sub-workflows via `workflow_run`, `repository_dispatch`, or by invoking reusable workflows.

**When to use.** Complex pipelines where a deploy depends on multiple builds; cross-repo orchestration.

**Risks.** Hard to follow execution; failure modes proliferate.

## Reusability patterns

### Reusable workflow (`workflow_call`)

A workflow that other workflows call as a unit:

```yaml
# .github/workflows/deploy-service.yml
on:
  workflow_call:
    inputs:
      environment:
        type: string
        required: true
    secrets:
      DEPLOY_TOKEN:
        required: true

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps: ...
```

Consumers:

```yaml
jobs:
  deploy-staging:
    uses: ./.github/workflows/deploy-service.yml
    with:
      environment: staging
    secrets:
      DEPLOY_TOKEN: ${{ secrets.STAGING_TOKEN }}
```

**When to use.** Whole-workflow reuse. Each call gets its own runner, its own job graph, its own logs.

**Strengths.** Strong isolation; clear input/output; org-level reuse via cross-repo `uses:`.

**Limits.** Up to 4 levels of nesting. Up to 20 unique reusable workflows per caller.

### Composite action

A step bundle wrapped as a reusable step:

```yaml
# .github/actions/setup-node-and-cache/action.yml
runs:
  using: composite
  steps:
    - uses: actions/setup-node@<SHA>
      with:
        node-version: ${{ inputs.node-version }}
    - uses: actions/cache@<SHA>
      with:
        path: ~/.npm
        key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}
```

**When to use.** Tight step bundle reused within a workflow or across workflows. Runs as if inlined; no separate runner.

**Strengths.** Lightweight; no setup overhead.

**Limits.** No `if:` per step; no separate runner; limited input types.

### Custom JS / Docker action

Action authored in JS or Docker, distributed via repo:

**When to use.** Logic too complex for composite; cross-language tooling; want to publish to the marketplace.

**Trade-off.** More work to author and maintain.

## Concurrency patterns

### Cancel previous runs on same PR (CI)

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

**When to use.** PR CI workflows. New pushes invalidate older runs.

### Serialize deploys per environment

```yaml
concurrency:
  group: deploy-${{ inputs.environment }}
  cancel-in-progress: false
```

**When to use.** CD workflows. Two simultaneous deploys to the same environment race.

### Per-resource serialization

```yaml
concurrency:
  group: migrate-${{ inputs.database }}
  cancel-in-progress: false
```

**When to use.** Migrations or other operations on shared mutable resources.

## Environment topology patterns

### dev → staging → prod (linear promotion)

Each environment has its own:

- Cloud resources (or namespace within shared resources)
- OIDC role
- Secrets (environment-scoped in GitHub)
- Protection rules

Promotion: CI runs on PR; merge deploys to staging automatically; release tag deploys to prod with approval gate.

**When to use.** Default for most teams.

### Multi-region or multi-tenant

```
main → deploy-us-east → deploy-eu-west → deploy-ap-south
```

Each region a sequential step (or parallel jobs with cross-region coordination).

**When to use.** Global deploys; data-residency requirements.

**Discipline.** Per-region failure handling; rollback playbook; staged rollout.

### Per-PR ephemeral environment

A PR creates a unique environment (`pr-1234`) for review; the environment tears down on PR close.

**When to use.** Visual review of changes; integration testing.

**Cost.** Provisioning each PR isn't free; document the cleanup strategy.

## Deployment patterns

### Rolling deploy

Replace pods/instances one by one, draining traffic from old before bringing up new.

**When to use.** Default for most stateless services.

**Risks.** Brief mixed-version period; both versions need to handle each other's data.

### Blue-green

Stand up the new version in parallel ("green"); swap traffic; tear down old ("blue").

**When to use.** Atomic-cutover preference; want zero mixed-version time.

**Cost.** 2x resource cost during the transition.

### Canary

Route a small percentage of traffic to the new version; observe; increase percentage gradually.

**When to use.** High-risk releases; need to observe under real load before full rollout.

**Discipline.** Define the success metric; the automation watches it and rolls back if it crosses a threshold.

### Immutable infrastructure

Each deploy provisions new instances; old instances are destroyed (not modified).

**When to use.** Stateless services; configuration drift unacceptable.

## Matrix and parallelization patterns

### Matrix across configs

```yaml
jobs:
  test:
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        node: [18, 20, 22]
    steps: ...
```

Runs 9 jobs in parallel (3 OS × 3 Node versions). Each is an independent runner.

**When to use.** Genuine cross-config testing.

**Anti-pattern.** Two unrelated jobs in a matrix to "save lines." They aren't related; they shouldn't share a job definition.

### `max-parallel`

```yaml
strategy:
  matrix:
    region: [us-east, us-west, eu-west, eu-central, ap-south, ap-northeast]
  max-parallel: 2
```

**When to use.** Matrix entries hit a shared rate-limited resource (cloud API, deploy target).

### `fail-fast: false`

```yaml
strategy:
  matrix:
    ...
  fail-fast: false
```

**When to use.** Want to see all failures, not just the first. Useful for flaky tests, cross-platform debugging.

## Cache and artifact patterns

### Dependency cache keyed by lockfile

```yaml
- uses: actions/cache@<SHA>
  with:
    path: ~/.cache/pip
    key: ${{ runner.os }}-pip-${{ hashFiles('**/poetry.lock') }}
```

### Build artifact

```yaml
- uses: actions/upload-artifact@<SHA>
  with:
    name: dist
    path: dist/
    retention-days: 30

# Consuming job:
- uses: actions/download-artifact@<SHA>
  with:
    name: dist
```

**When to use.** Pass build output between jobs in the same workflow; archive for inspection.

### Container image as artifact

Push to a registry (ECR, GCR, ghcr.io) with a deterministic tag.

**When to use.** Containerized deploys; tag is the deploy identifier.

## Anti-patterns reviewers should flag

| Anti-pattern | Why it's bad | Typical fix |
|---|---|---|
| `pull_request_target` checking out PR head | Runs untrusted PR code with secrets; injection vector | Use `pull_request` and pass artifacts via approved jobs |
| Tag-pinned third-party action (`@v3`) | Mutable; supply-chain risk | SHA-pin with version comment |
| `${{ github.event.pull_request.title }}` in `run:` block | Shell injection via PR title | Pass through `env:` and quote `"$VAR"` |
| Long-lived AWS access keys in secrets | Breach blast radius | OIDC federation |
| `permissions:` block missing | Token has whatever defaults exist; possibly broad | Explicit minimum (`contents: read`) |
| Production deploy without approval gate | Single mistake hits production | GitHub Environment with required reviewers |
| Concurrency unspecified for deploy workflow | Two deploys race | Concurrency group per environment, `cancel-in-progress: false` |
| `if: always()` on cleanup that hides failure | Failures swallowed | Explicit `if: failure()` or `if: ${{ !cancelled() }}` |
| Matrix that's two unrelated jobs | Conflates concerns | Separate jobs |
| Reusable workflow with 20+ inputs | Not reusable; config protocol | Decompose; or use composite action |
| Workflow that runs on push AND `workflow_dispatch` AND `schedule` for the same purpose | Overlapping triggers; double-runs | Separate workflows per concern |
| Hardcoded environment in workflow | Can't promote without editing YAML | Inputs / matrix |
| Cache without `restore-keys` | Cache miss means full cold start; no partial benefit | Add restore-keys for fallback |
| Cache key without lockfile hash | Stale dependencies persist | Include `hashFiles('**/lock')` |
| Build artifact with `retention-days: 90` for ephemeral check | Wastes storage | Right-size retention (1-7 days for ephemeral) |
| Self-hosted runner without isolation | Cross-PR contamination | Per-job containerization or per-PR ephemeral |
| Secret used in expression context (`${{ secrets.X }}` outside `env:`) | Logged on some operations | Pass via `env:`; never inline in `run:` |
| `pull_request: branches: [main]` only | Doesn't run for fork PRs | Document scope; use `pull_request_target` cautiously if needed |
| Status check name not pinned in branch protection | New check additions don't enforce | Required-check list reviewed when workflow changes |
| Runner OS pinned to `latest` without revisiting | Drift; build breaks unexpectedly | Pin to specific version (e.g., `ubuntu-22.04`) |
| Action that fetches scripts from internet at runtime | Supply-chain risk; non-reproducible | Vendor the script or use a pinned action |
| Workflow that writes to its own repo via `GITHUB_TOKEN` without `contents: write` | Will fail when run | Explicit `permissions:` declaration |

## Decision frames

When the CI/CD Designer faces a choice:

1. **What's the trigger?** PR / push / manual / scheduled / event-driven. Each is a different workflow.
2. **What's the blast radius?** Production-touching workflows need stronger gates than internal-only.
3. **What's the run cadence?** A workflow that runs 100 times per day on every PR has different cost considerations than one that runs nightly.
4. **What's the duplication level?** Three nearly-identical workflows are a refactor signal — reusable workflow or composite action.
5. **What's the team's tolerance?** Some teams want full auto-deploy with rollback; others require manual gates. Reflect the team's actual risk posture.

The Designer documents the structure, the triggers, the concurrency, the environments, and the deployment pattern in the per-layer Design subsection — alongside the rationale.
