# Debugging and Troubleshooting

When a workflow doesn't behave as expected, work through these levels in order. Most issues are in the first three.

## Table of contents

- [Workflow won't trigger](#workflow-wont-trigger)
- [Workflow triggers but a job is skipped](#workflow-triggers-but-a-job-is-skipped)
- [Step fails with no useful error](#step-fails-with-no-useful-error)
- [Permissions / authentication errors](#permissions--authentication-errors)
- [Cache misses](#cache-misses)
- [Action version / deprecation issues](#action-version--deprecation-issues)
- [Debug logging](#debug-logging)
- [Useful diagnostic snippets](#useful-diagnostic-snippets)

## Workflow won't trigger

### Check the path

The file must be at `.github/workflows/<name>.yml` (or `.yaml`). Files in subdirectories don't trigger.

### Check the YAML is valid

A syntax error makes the entire file ignored — no error in the UI, just silence. Run:

```bash
# Locally
yq eval '.' .github/workflows/ci.yml >/dev/null
# or
python -c "import yaml; yaml.safe_load(open('.github/workflows/ci.yml'))"
```

GitHub also shows YAML errors in the Actions UI when you visit the workflow page directly.

### Check the trigger matches

- Pushed to a branch that's not in `branches:`? Won't trigger.
- Path filters (`paths:` / `paths-ignore:`) — does the diff actually touch the included paths?
- Event types: `pull_request: types: [opened, synchronize, reopened]` is the default. If you set `types: [opened]` only, edits and resyncs won't trigger.
- `workflow_dispatch:` requires the workflow to be on the *default branch* to appear in the UI.
- `schedule:` only runs on the default branch and pauses after 60 days of repo inactivity.

### Check repo/org settings

- Settings → Actions → "Disable Actions" globally disables.
- A new contributor's first workflow on a public repo requires maintainer approval.
- Org policies can restrict which actions are allowed (`Allow select actions and reusable workflows`).
- Branch protection with required status checks waits for those checks even on the first push to a new branch.

### Check that the previous step didn't error in YAML parsing

Sometimes a workflow exists but a recent edit added an invalid key. The Actions UI shows "Invalid workflow file" with the specific issue.

## Workflow triggers but a job is skipped

### Job-level `if:` evaluated false

Read the "Set up job" log; GitHub annotates skipped jobs with the reason. Common cause: `if:` references a context that's empty for the current event.

### `needs:` resolved to a failed/skipped job

By default, a downstream job is skipped if its `needs:` failed. Use `if: always()` plus explicit status checks if you want it to run anyway:

```yaml
notify:
  needs: [build]
  if: always()
  steps:
    - if: needs.build.result == 'failure'
      run: ./notify.sh
```

### String comparison gotcha

```yaml
if: inputs.deploy   # ☠️ truthy for the string "false" too
if: inputs.deploy == 'true'    # safer
if: inputs.deploy == true      # only works if `type: boolean`
```

For `workflow_dispatch` inputs typed as `boolean`, `inputs.deploy` is a real bool. For string-typed or `github.event.inputs.*`, always compare to `'true'`.

## Step fails with no useful error

### Re-run with debug logging

Repo Settings → Secrets/Variables → Actions:
- Add repo *secret* `ACTIONS_RUNNER_DEBUG` = `true`.
- Add repo *secret* `ACTIONS_STEP_DEBUG` = `true`.

(Yes, secrets, not variables — that's how GitHub designed it.)

Re-run the failing job. Logs now include detailed runner internals and step-level debug output.

### Add `set -x` to bash

```yaml
- run: |
    set -x
    ./flaky-script.sh
  shell: bash
```

`set -x` traces every shell command before execution.

### Check the runner state

```yaml
- name: Diagnostics
  if: failure()
  run: |
    echo "::group::Disk"
    df -h
    echo "::endgroup::"
    echo "::group::Memory"
    free -h
    echo "::endgroup::"
    echo "::group::Recent logs"
    tail -n 50 /var/log/syslog 2>/dev/null || true
    echo "::endgroup::"
```

`::group::` / `::endgroup::` create collapsible sections in the log.

### Out-of-disk errors

Standard GitHub-hosted runners have ~14 GB usable. Build pipelines that pull large Docker images, install heavy SDKs, or cache aggressively run out. Free space:

```yaml
- name: Free disk space
  run: |
    sudo rm -rf /usr/share/dotnet /usr/local/lib/android /opt/ghc
    docker system prune -af
    df -h
```

Alternative: a larger runner.

## Permissions / authentication errors

### `403 Resource not accessible by integration`

The `GITHUB_TOKEN` doesn't have the scope needed for the API call. Add to `permissions:`:

```yaml
permissions:
  contents: write       # to push, tag, create releases
  pull-requests: write  # to comment, label
  packages: write       # to push to GHCR
```

Job-level `permissions:` *replaces* workflow-level — set everything you need.

### `Error: Could not assume role with OIDC: AccessDenied`

The IAM role's trust policy doesn't match the OIDC token's `sub` claim. Common causes:
- Trust expects `ref:refs/heads/main` but the workflow uses `environment:production`. The `sub` claim differs.
- Typo in the repo path: `repo:my-org/my-repo` is case-sensitive.
- Missing the `Federated` principal pointing at the OIDC provider in the IAM account.
- Missing the `id-token: write` permission in the workflow.

Debug by adding a step that prints the OIDC token's claims:

```yaml
- run: |
    TOKEN=$(curl -sH "Authorization: bearer $ACTIONS_ID_TOKEN_REQUEST_TOKEN" \
      "$ACTIONS_ID_TOKEN_REQUEST_URL&audience=sts.amazonaws.com" | jq -r .value)
    echo "$TOKEN" | cut -d. -f2 | base64 -d 2>/dev/null | jq .
```

This shows the claims your trust policy must match.

### `Error: This request has been blocked because it has been determined to be a bot request`

You're hitting an unauthenticated API rate limit. Authenticate using `GITHUB_TOKEN`:

```yaml
- run: gh release list
  env:
    GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

## Cache misses

### Symptoms

The cache step shows "Cache not found for input keys" every run, even though dependencies don't change.

### Debug

```yaml
- name: Debug cache key
  run: |
    echo "Hash of lockfiles:"
    find . -name 'package-lock.json' -exec sha256sum {} \;
    echo "Computed key: ${{ runner.os }}-npm-${{ hashFiles('**/package-lock.json') }}"
```

If the hash changes every run, the lockfile is being modified during the build (e.g., a previous step ran `npm install` instead of `npm ci`).

### Restore-key fallback isn't working

`restore-keys:` matches by prefix. The fallback pattern must literally be a prefix of the primary key:

```yaml
key: ${{ runner.os }}-py3.13-${{ hashFiles('requirements.txt') }}
restore-keys: |
  ${{ runner.os }}-py3.13-       # ✓ prefix match works
  ${{ runner.os }}-              # ✓ also works
  ${{ runner.os }}-py-           # ✗ doesn't prefix the actual key
```

### Cache size limit

10 GB total per repo. Older entries are evicted when full. If your important cache keeps disappearing, prune large or stale caches: Settings → Actions → Caches.

## Action version / deprecation issues

### Common deprecated patterns to flag

| Old pattern | Replacement |
|---|---|
| `::set-output name=foo::bar` | `echo "foo=bar" >> "$GITHUB_OUTPUT"` |
| `::save-state name=foo::bar` | `echo "foo=bar" >> "$GITHUB_STATE"` |
| `set-env` workflow command | `echo "FOO=bar" >> "$GITHUB_ENV"` |
| `actions/checkout@v1`, `@v2`, `@v3` | `actions/checkout@v6` (or pin to SHA) |
| `actions/cache@v2`, `@v3` | `actions/cache@v4` |
| `actions/upload-artifact@v3` | `actions/upload-artifact@v4` |
| `actions/setup-node@v3` (Node 16) | `actions/setup-node@v6` |
| `node12`, `node16` runtimes in custom actions | `node20` or `node24` |

### Why this matters

GitHub deprecates and eventually disables old patterns. A workflow that works today may suddenly fail with a warning-then-error message. The audit script (`scripts/audit_workflow.py`) flags these.

## Debug logging

### Workflow command syntax

Inside `run:` steps, you can emit log commands:

```bash
echo "::debug::message"           # only shown when ACTIONS_STEP_DEBUG is true
echo "::warning file=app.js,line=10::Deprecated API"
echo "::error file=app.js,line=10::Type mismatch"
echo "::notice::Build complete"
echo "::group::Setup"
# ... grouped log output
echo "::endgroup::"
echo "::add-mask::$dynamic_secret"   # mask a value in logs from this point on
```

`warning`/`error` annotations appear in the PR diff and run summary.

### Re-run with debug from the UI

Re-run options now include "Enable debug logging" — equivalent to setting the secrets, scoped to that re-run.

## Useful diagnostic snippets

### Print the full event payload

```yaml
- name: Dump event
  env: { EVENT: ${{ toJSON(github.event) }} }
  run: echo "$EVENT"
```

(Always go through env to avoid script injection.)

### Print all contexts

```yaml
- name: Dump contexts
  env:
    GITHUB_CTX: ${{ toJSON(github) }}
    JOB_CTX: ${{ toJSON(job) }}
    STEPS_CTX: ${{ toJSON(steps) }}
    RUNNER_CTX: ${{ toJSON(runner) }}
    NEEDS_CTX: ${{ toJSON(needs) }}
    INPUTS_CTX: ${{ toJSON(inputs) }}
    VARS_CTX: ${{ toJSON(vars) }}
  run: |
    echo "::group::github"
    echo "$GITHUB_CTX"
    echo "::endgroup::"
    echo "::group::job"
    echo "$JOB_CTX"
    echo "::endgroup::"
    # etc.
```

Skip `secrets` — printing it leaks values.

### Check effective permissions of GITHUB_TOKEN

```audit-example -- Documents credential-shaped environment variable patterns the auditor flags via DE-2 scanner; pedagogical example of env-var-based credential handling, not real credentials.
- run: |
    curl -s -H "Authorization: token $GITHUB_TOKEN" \
      https://api.github.com/repos/${{ github.repository }} | jq .permissions
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

### Time a step

```yaml
- name: Time-stamped run
  run: |
    start=$SECONDS
    ./long-operation.sh
    echo "Elapsed: $((SECONDS - start))s"
```

### Catch a stuck process

`timeout-minutes:` at the step level kills the step (and the runner reports it cleanly):

```yaml
- run: ./potentially-stuck-thing
  timeout-minutes: 5
```

Default job timeout is 360 minutes (6 hours). Set lower for any job that shouldn't run that long.
