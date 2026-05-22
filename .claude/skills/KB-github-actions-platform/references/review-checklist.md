# Review Checklist

A structured pass to make when reviewing or auditing a GitHub Actions workflow. Combine this with `scripts/audit_workflow.py` for the mechanical checks; this document covers the judgment calls.

Group findings by severity:
- **Blocker** — security vulnerability or correctness bug. Must be fixed before merging.
- **Major** — significant maintainability or operational concern. Should be fixed soon.
- **Minor** — style, optimization, polish. Nice to fix.

## Table of contents

- [Security](#security)
- [Correctness](#correctness)
- [Performance](#performance)
- [Maintainability](#maintainability)
- [Operational concerns](#operational-concerns)
- [Output format for review comments](#output-format-for-review-comments)

## Security

### Action pinning (Blocker if violated)

- [ ] Every third-party action (anything not in `actions/*` or `github/*`) is pinned to a 40-character commit SHA.
- [ ] Pinned actions have a comment indicating the version (e.g., `# v1.2.3`).
- [ ] First-party actions use a major version tag at minimum (`@v6`), preferably SHA.

### `permissions:` (Blocker if missing)

- [ ] Every workflow has an explicit `permissions:` block.
- [ ] The block grants minimum scopes: usually `contents: read`. Deviations are justified.
- [ ] Job-level overrides are intentional (job-level *replaces* workflow-level).
- [ ] `id-token: write` only present when OIDC is actually used.
- [ ] No `permissions: write-all`.

### Secrets handling (Blocker if violated)

- [ ] No `echo "$SECRET"` or `echo "${{ secrets.X }}"` patterns.
- [ ] Secrets aren't transformed in ways that bypass masking (`base64`, `jq`-extracted, etc.).
- [ ] Secrets aren't passed as command-line arguments (would appear in `ps`); use env vars.
- [ ] Production secrets are in a protected environment, not just repo-level secrets.
- [ ] Reusable workflow callers don't use `secrets: inherit` unless justified.

### Script injection (Blocker if violated)

- [ ] No `${{ github.event.* }}` interpolation directly into `run:` blocks.
- [ ] No `${{ github.head_ref }}` interpolation into `run:` blocks.
- [ ] No `${{ github.actor }}`, `${{ inputs.* }}` (from `workflow_dispatch`) interpolation into `run:` blocks for fields users control.
- [ ] Untrusted contexts pass through `env:` instead, with `"$VAR"` quoting in the script.

The full list of untrusted-input contexts is in [security.md § script injection prevention](security.md#script-injection-prevention).

### `pull_request_target` (Blocker if violated)

If the workflow uses `pull_request_target`:
- [ ] The workflow does NOT check out the PR head.
- [ ] OR if it does, there's an explicit approval gate (e.g., a `[deploy preview]` label that only maintainers can apply, plus an `if:` checking for that label) AND the workflow does not run any code from the PR's checkout (no `npm install`, no scripts).
- [ ] Caches the workflow uses are not poisonable from the PR (see anti-patterns.md).

### OIDC and cloud auth (Major if not implemented)

- [ ] Cloud deployments use OIDC where supported (AWS, Azure, GCP, PyPI, npm provenance).
- [ ] OIDC trust policies are scoped to the repo AND ideally to a branch or environment, not just the repo.
- [ ] Long-lived credentials are not stored as secrets when OIDC could replace them.

### Self-hosted runners (Blocker if violated)

- [ ] No self-hosted runners on public repositories.
- [ ] Self-hosted runners are ephemeral or aggressively reset between jobs.
- [ ] Self-hosted runner labels are scoped enough to prevent unrelated workflows from picking them up.

## Correctness

### Triggers

- [ ] The trigger matches the intent (e.g., `pull_request` for "run on PRs"; not `pull_request_target` unless the privileged variant is needed).
- [ ] Path filters are correct (no false negatives like missing a file type).
- [ ] Branch filters are correct (e.g., `main` not `master`).
- [ ] Tag filters use proper glob (`v*.*.*`, not just `v*`).

### Conditionals

- [ ] `if:` expressions handle the case where a context is empty (e.g., `github.head_ref` is empty for non-PR runs).
- [ ] String comparisons against booleans are explicit (`inputs.flag == 'true'` for string inputs, `inputs.flag` only for typed-boolean inputs).
- [ ] Job-level `if:` doesn't accidentally skip the job for the case it was meant to handle.
- [ ] `if: always()` and `if: !cancelled()` used appropriately for cleanup steps.

### Job dependencies

- [ ] `needs:` correctly captures the actual dependencies between jobs.
- [ ] Outputs flow correctly: `jobs.<id>.outputs:` declared, and `needs.<id>.outputs.*` referenced downstream.
- [ ] No accidental cycles or missed dependencies.
- [ ] Cleanup/notification jobs that should run on failure use `if: always()` or `if: failure()`.

### Matrix

- [ ] Matrix combinations are intentional (no redundant ones).
- [ ] `fail-fast:` is set explicitly (default `true`; usually want `false` for testing).
- [ ] `include:` / `exclude:` work as intended (test with a small example if uncertain).
- [ ] Matrix outputs aren't relied upon naively (last writer wins; use artifacts for fan-in).

### Outputs

- [ ] Step outputs use `>> "$GITHUB_OUTPUT"` (not deprecated `set-output`).
- [ ] Multi-line values use heredoc form correctly.
- [ ] Output sizes are within limits (1 MB per job).

## Performance

### Caching

- [ ] Dependencies are cached (via setup action `cache:` or explicit `actions/cache`).
- [ ] Cache keys are based on lockfile hashes, with sensible `restore-keys:` fallbacks.
- [ ] Cache paths are correct (the actual install location, not a custom one that the install command doesn't write to).
- [ ] No time-based or always-changing values in cache keys.

### Concurrency

- [ ] CI workflows on PRs use `cancel-in-progress: true` to drop stale runs.
- [ ] Deployment workflows use `cancel-in-progress: false` and a stable group keyed on the target environment.
- [ ] `concurrency:` group expressions don't accidentally collide unrelated workflows.

### Runner choice

- [ ] Runner size is appropriate (don't run a 5-minute test job on a 96-core larger runner).
- [ ] Self-hosted/larger runners are used only when necessary; default to GitHub-hosted.
- [ ] `timeout-minutes:` is set on long jobs to prevent runaway billing.

### Parallelization

- [ ] Independent jobs run in parallel (no false `needs:` chains).
- [ ] Test sharding is used when test suites take more than ~5 minutes.
- [ ] Build matrices fan out, then aggregate (rather than serializing).

## Maintainability

### Reuse

- [ ] Logic duplicated across 3+ workflows is extracted into a reusable workflow or composite action.
- [ ] Reusable workflows have clear `inputs:` documentation (description fields filled in).
- [ ] Reusable workflows pin to a tagged ref or SHA, not a moving branch.

### Naming

- [ ] Workflow `name:` is set and descriptive.
- [ ] Job IDs are descriptive (`build` rather than `job1`).
- [ ] Steps that aren't trivially self-describing have `name:` set.

### Comments

- [ ] Non-obvious choices are commented (why this trigger combo, why this permission scope, why this `if:` condition).
- [ ] SHA-pinned actions have a version comment.

### File organization

- [ ] One concern per workflow file (CI, release, deploy as separate files, not one mega-workflow).
- [ ] Reusable logic in `.github/workflows/` (for `workflow_call`) or `.github/actions/<name>/` (for composite actions).
- [ ] Templates aren't copy-pasted across many files; refactored as appropriate.

## Operational concerns

### Failure modes

- [ ] Failed deployments don't leave the system in a half-deployed state (or there's a documented rollback path).
- [ ] `continue-on-error:` is used sparingly and with explicit reason.
- [ ] Notifications fire on failure of important workflows.

### Observability

- [ ] Long-running steps have `name:` so the timing is identifiable.
- [ ] Errors include enough context for debugging (no opaque exit-code-only failures).
- [ ] `$GITHUB_STEP_SUMMARY` is used for important results (test counts, coverage, deployment URLs).

### Cost control

- [ ] Scheduled workflows aren't over-frequent (every 5 min when hourly would do).
- [ ] Large runners aren't used when standard would suffice.
- [ ] Artifact retention is bounded (not the default 90 days for ephemeral data).
- [ ] Caches don't grow unboundedly (the 10 GB total quota encourages tidiness, but watch for repos near the cap).

### Branch protection alignment

- [ ] Required status checks in branch protection match the workflow's job names.
- [ ] Renaming a job doesn't break branch protection silently — coordinate the rename.

## Output format for review comments

When writing review feedback:

```markdown
**[Blocker] [Security] Unpinned third-party action**

Line 23: `uses: tj-actions/changed-files@v4`

Tags are mutable. The action's repo could re-point `v4` to a malicious version,
which would silently run with the privileged context of this workflow.

**Fix:** pin to a 40-character commit SHA with a version comment:

```yaml
- uses: tj-actions/changed-files@<full-sha>  # v44.5.7
```

Reference: `references/security.md#pinning-third-party-actions`.
```

The structure: severity tag + category tag + one-line summary, then the location, the risk, the fix, and a reference. This format makes it easy to triage and act on.
