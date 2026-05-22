# CI/CD Design Principles (GitHub Actions)

## Contents

- Principle 1: CI and CD are separate concerns
- Principle 2: OIDC over long-lived cloud credentials
- Principle 3: Concurrency groups protect serial resources
- Principle 4: Environments gate, not just label
- Principle 5: Least privilege at every layer (token, runner, action)
- Principle 6: Pin third-party actions to SHA
- Principle 7: Caches are accelerators, not source of truth
- Principle 8: Workflows are tested like code

## Principle 1: CI and CD are separate concerns

CI (Continuous Integration) answers: "Does this change pass the build / tests / quality gates?"
CD (Continuous Deployment / Delivery) answers: "Should this change reach the next environment?"

Different triggers, different scopes, different failure modes. Conflating them produces a single megaworkflow that's hard to reason about, slow to run, and impossible to gate effectively.

The Designer's defaults:

| Workflow | Trigger | Scope | Failure means |
|---|---|---|---|
| CI | `pull_request` (PR-driven) | Build, test, lint, security scan | Block merge |
| CI on main | `push` to default branch | Build, test, publish artifact | Block release |
| CD to staging | `push` to default branch (post-CI) or `workflow_run` | Deploy to staging | Alert; investigate |
| CD to prod | Manual `workflow_dispatch` or release tag | Deploy to prod with approval gate | Page on-call; rollback |

The separation lets each have its own concurrency model, secret scope, and timeout budget.

## Principle 2: OIDC over long-lived cloud credentials

Long-lived AWS/GCP/Azure access keys stored as repository secrets are a breach blast radius: leaked once, leaked forever (until rotated, which is hard). OIDC federation eliminates this:

- GitHub presents a JWT identifying the workflow, branch, environment.
- The cloud's trust policy validates the JWT and issues short-lived credentials.
- No long-lived secret in GitHub.

Trust policy scoping matters. A trust policy that says `"any repo, any branch, any workflow"` defeats the security. The Designer scopes:

```json
{
  "Condition": {
    "StringEquals": {
      "token.actions.githubusercontent.com:sub": "repo:my-org/my-repo:environment:production"
    }
  }
}
```

This trust policy issues credentials only to workflows running in the `production` environment of `my-org/my-repo`. Other workflows can't assume the role.

The Designer documents the OIDC trust mapping in the per-layer subsection: which workflows assume which cloud roles under which conditions.

## Principle 3: Concurrency groups protect serial resources

`concurrency:` in a workflow or job restricts simultaneous runs of the same group. Without it:

- Two CI runs for the same PR run in parallel; the older one finishes after the newer one but is reported last (confusing).
- Two deploys to the same environment race; one wins; the deploy log doesn't make clear which.
- A long-running release blocks the queue; useful runs starve.

Common concurrency patterns:

```yaml
# CI: cancel older runs on the same PR
concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true

# CD: serialize deploys to the same environment; never cancel
concurrency:
  group: deploy-${{ inputs.environment }}
  cancel-in-progress: false
```

For deploys, `cancel-in-progress: false` is important: cancelling a partial deploy can leave the environment in an undefined state.

The Designer specifies concurrency for every workflow, with the group key chosen to reflect the actual shared resource.

## Principle 4: Environments gate, not just label

GitHub Environments are more than a label. With protection rules:

- **Required reviewers.** A specific team or user must approve before the job runs.
- **Wait timer.** N minutes of bake-time before the job proceeds.
- **Branch restrictions.** Only specified branches can deploy to this environment.

The Designer uses Environments for actual gates, not just to scope secrets:

- `dev` — no protection rules; any branch deploys.
- `staging` — branch restricted to `main`; no approval (continuous).
- `production` — required reviewers; branch restricted to `main`; wait timer of 5 min for human catch.

For per-environment secrets:

```yaml
jobs:
  deploy:
    environment: production
    steps:
      - uses: aws-actions/configure-aws-credentials@<SHA>
        with:
          role-to-assume: ${{ secrets.PROD_DEPLOY_ROLE }}  # environment-scoped secret
```

`secrets.PROD_DEPLOY_ROLE` only exists in the `production` environment scope; other workflows can't access it.

## Principle 5: Least privilege at every layer (token, runner, action)

Three layers of privilege to scope down:

### `GITHUB_TOKEN` permissions

By default the `GITHUB_TOKEN` may have broad scopes (`contents: write`, `pull-requests: write`, etc.) depending on repo / org defaults. The Designer declares explicit minimum:

```yaml
permissions:
  contents: read
  # Add only what's needed:
  # id-token: write       # if using OIDC
  # pull-requests: write  # if commenting on PRs
  # packages: write       # if publishing
```

### Runner privileges

Self-hosted runners have access to the network and machine they run on. The Designer documents:

- Where self-hosted runners run (private network? public internet?).
- What credentials they can access (cloud roles? secrets?).
- How they're isolated from each other (per-job? per-run? containerized?).

### Action privileges

Third-party actions run with the workflow's `GITHUB_TOKEN` and secrets. A malicious action exfiltrates these. Mitigation:

- SHA-pin every third-party action.
- Audit the action's source.
- Restrict the workflow's token / secrets to what the action needs.

## Principle 6: Pin third-party actions to SHA

Tags (`@v3`) and branches (`@main`) are mutable. The author can re-point them to any commit, including malicious code. Once a malicious commit lands, every workflow using the tag pulls it in on the next run.

The Designer's rule: every third-party action pinned to a 40-character commit SHA, with a comment showing the human-readable version:

```yaml
- uses: aws-actions/configure-aws-credentials@e3dd6a429d7300a6a4c196c26e071d42e0343502 # v4.0.2
```

First-party (`actions/*`, `github/*`) major-version tags are acceptable since GitHub controls the repos. Even so, SHA-pinning is safer.

Tools like Dependabot can update pinned SHAs automatically; the Designer documents the update cadence.

## Principle 7: Caches are accelerators, not source of truth

Caches speed up workflows by reusing artifacts from prior runs. A few rules keep them from becoming sources of bugs:

- **Cache keys include the dependency lockfile hash.** When dependencies change, the key changes; old cache is unused; fresh deps fetch.
- **Caches are advisory.** The workflow should produce the same result with or without the cache.
- **Don't cache build outputs that depend on uncached inputs.** A stale cache built from an old version of a now-deleted file is a debugging nightmare.

```yaml
- uses: actions/cache@<SHA>
  with:
    path: ~/.npm
    key: ${{ runner.os }}-node-${{ hashFiles('**/package-lock.json') }}
    restore-keys: |
      ${{ runner.os }}-node-
```

The `restore-keys` lets the workflow fall back to a partial cache (faster than no cache), but only the fully-keyed cache is considered a fresh hit.

Artifacts are different: they're outputs to be consumed by later jobs or stored for retention. Caches are inputs; artifacts are outputs.

## Principle 8: Workflows are tested like code

A workflow is code; it deserves testing.

- **Lint the workflow.** `actionlint`, `yamllint`, the workflow audit script in KB-github-actions-platform.
- **Run on a PR before merging changes.** The workflow itself triggers when its file changes.
- **Test in dev/staging before production.** A new deploy pattern is tested against staging before being promoted to production.
- **Document the rollback.** If a workflow change introduces a bug, what's the path back? Git revert is the default, but for state-affecting workflows (deploys, migrations), explicit rollback procedure.

The Designer documents the workflow-change discipline in the per-layer subsection: how new workflows are introduced, how they're tested, how rollback works.
