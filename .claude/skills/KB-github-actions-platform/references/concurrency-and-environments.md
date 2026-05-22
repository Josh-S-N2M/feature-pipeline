# Concurrency and Environments

Two related controls that prevent races and gate deployments. Used together, they form the spine of any safe deployment pipeline.

## Table of contents

- [Concurrency](#concurrency)
- [Concurrency patterns](#concurrency-patterns)
- [Environments](#environments)
- [Deployment protection rules](#deployment-protection-rules)
- [Environments + concurrency together](#environments--concurrency-together)
- [Common patterns](#common-patterns)

## Concurrency

A `concurrency:` block ensures that no two workflow runs (or jobs) sharing the same group execute simultaneously.

```yaml
concurrency:
  group: <expression>
  cancel-in-progress: <true | false | expression>
```

- `group:` — a string that identifies the resource being protected. Two runs share the lock if they compute the same `group:`.
- `cancel-in-progress:` — when `true`, a new run cancels the in-progress run with the same group. When `false`, the new run waits in queue.

Set at the workflow or job level.

## Concurrency patterns

### Cancel duplicate PR runs

When a developer pushes again to a PR, you want the previous CI run to be cancelled (no point finishing a build of stale code).

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

`github.ref` is the PR's merge ref (e.g., `refs/pull/42/merge`), so two pushes to the same PR collide; pushes to different PRs don't.

### Serialize deployments to production

Two pushes to `main` shouldn't trigger two simultaneous deploys racing each other.

```yaml
concurrency:
  group: deploy-production
  cancel-in-progress: false      # queue, don't cancel
```

If one deploy is in progress and another arrives, the new one waits. Once the first finishes, the second runs. Avoid `cancel-in-progress: true` for production deploys — you don't want a half-finished deploy to be cancelled mid-rollout.

### Cancel preview deployments per PR

```yaml
concurrency:
  group: preview-pr-${{ github.event.pull_request.number || github.ref }}
  cancel-in-progress: true
```

If a developer pushes twice in 30 seconds, only the latest preview is built. The fallback to `github.ref` handles non-PR runs (manual dispatches).

### Per-environment concurrency

Allow staging and production to deploy in parallel, but not two deploys to the same environment.

```yaml
deploy:
  strategy:
    matrix:
      env: [staging, production]
  concurrency:
    group: deploy-${{ matrix.env }}
    cancel-in-progress: false
  environment: ${{ matrix.env }}
  runs-on: ubuntu-latest
  steps: [...]
```

Job-level `concurrency:` works here even with a matrix.

## Environments

A GitHub *environment* is a named deployment target (e.g., `production`, `staging`, `preview`). Environments give you:

- **Environment-specific secrets** (separate from repo secrets, accessible only when the job uses `environment:`).
- **Environment-specific variables** (`vars` context).
- **Deployment protection rules** (required reviewers, wait timers, branch restrictions, custom rules).
- **Deployment history** in the repo's Deployments tab, with status and URL.

Configured at: repo Settings → Environments → New environment.

### Linking a job to an environment

```yaml
deploy:
  runs-on: ubuntu-latest
  environment:
    name: production
    url: https://example.com    # shown in deployments UI; supports expressions
  steps:
    - run: ./deploy.sh
```

When this job starts, GitHub:
1. Checks deployment protection rules (may pause for approval).
2. Loads environment-scoped secrets and vars.
3. Records a deployment in the repo Deployments view.
4. On success, sets the environment's "current deployment" to this run.

### Dynamic environment URLs

```yaml
environment:
  name: preview
  url: ${{ steps.deploy.outputs.preview_url }}
```

The URL appears in the PR after deployment finishes — clickable for reviewers.

## Deployment protection rules

Configured per environment in the repo Settings UI:

### Required reviewers

Up to 6 reviewers (users or teams). The job pauses until enough approve. Useful for prod deploys that need human sign-off.

### Wait timer

Forced delay (0–43,200 minutes) before the job can run. Useful for canaries or "let monitoring catch up before promoting."

### Deployment branches and tags

Only specified branches/tags can deploy to this environment. E.g., production accepts only `refs/tags/v*.*.*`; staging accepts only `refs/heads/main`.

### Custom protection rules

Apps can register custom checks (e.g., "deployment requires a passing change-management ticket"). Used in regulated environments.

## Environments + concurrency together

Combine for safe, fast pipelines:

```yaml
name: Deploy
on:
  push:
    branches: [main]

permissions:
  id-token: write
  contents: read

jobs:
  deploy-staging:
    runs-on: ubuntu-latest
    environment:
      name: staging
      url: https://staging.example.com
    concurrency:
      group: deploy-staging
      cancel-in-progress: false
    steps:
      - uses: actions/checkout@v6
      - run: ./deploy.sh staging

  deploy-production:
    needs: deploy-staging
    runs-on: ubuntu-latest
    environment:
      name: production            # has required reviewers configured
      url: https://example.com
    concurrency:
      group: deploy-production
      cancel-in-progress: false
    steps:
      - uses: actions/checkout@v6
      - run: ./deploy.sh production
```

What this gives you:
- Staging deploys serially; the second push waits.
- Production requires manual approval (configured on the environment).
- Production also serializes — no two deploys racing.
- Each deploy is recorded in the repo Deployments UI with its URL.
- Each environment has its own scoped secrets (e.g., a different deploy key for staging vs prod).

## Common patterns

### Concurrency at workflow vs job level

- **Workflow-level:** simpler; the entire workflow is the lock unit. Use when the whole workflow operates on one resource.
- **Job-level:** finer; different jobs can have different groups. Use when, e.g., the build job is parallelizable across PRs but the deploy job must serialize.

### `${{ github.head_ref || github.ref }}`

When you want one expression that works for both PRs and pushes:

```yaml
concurrency:
  group: ci-${{ github.head_ref || github.ref }}
  cancel-in-progress: true
```

For PRs, `github.head_ref` is the source branch name (e.g., `feat/new-thing`). For pushes, it's empty, so the fallback `github.ref` (e.g., `refs/heads/main`) kicks in.

### Don't cancel deploys, do cancel CI

Rule of thumb:
- CI / build / test workflows → `cancel-in-progress: true`.
- Deploy / release workflows → `cancel-in-progress: false`.

Exception: preview deploys can be `true` (it's fine to cancel a half-built preview when the user pushes again).

### Environment for OIDC scoping

When OIDC trust is scoped to `environment:production`, only jobs that declare `environment: production` can request the cloud credentials. This adds a layer beyond branch scoping — even a malicious push to main can't deploy to prod without an approved environment job.

```yaml
deploy:
  environment: production    # OIDC trust policy includes "sub: ...:environment:production"
  permissions:
    id-token: write
    contents: read
  steps:
    - uses: aws-actions/configure-aws-credentials@SHA
      with:
        role-to-assume: arn:aws:iam::...:role/prod-deploy
        aws-region: us-east-1
```

### Pause-during-incident pattern

Configure a wait timer of 30 minutes on the `production` environment during an incident. New deploys pile up but don't run; once the incident is over, remove the timer and they go through. No code changes needed.
