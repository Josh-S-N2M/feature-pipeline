# Action Versions Reference

Current major versions of commonly used actions, as of mid-2026. Use this when suggesting `uses:` lines in new or refactored workflows.

**Always SHA-pin third-party actions.** This doc lists the current major version tag — use it as a hint, then resolve to a 40-character SHA via `git ls-remote https://github.com/<org>/<repo> <tag>` (or the GitHub UI: open the tag, copy the commit hash). Keep the tag as a comment for human readability:

```yaml
- uses: tj-actions/changed-files@<full-40-char-sha>  # v45.0.5
```

For first-party `actions/*` and `github/*`, major tags are acceptable but SHA pinning is still safer.

## Table of contents

- [GitHub-published (`actions/*`)](#github-published-actions)
- [Cloud auth](#cloud-auth)
- [Anthropic / Claude Code](#anthropic--claude-code)
- [Container build / publish](#container-build--publish)
- [Language ecosystem](#language-ecosystem)
- [Infrastructure-as-Code](#infrastructure-as-code)
- [Testing & coverage](#testing--coverage)
- [Code quality / security scanning](#code-quality--security-scanning)
- [Deployment / hosting](#deployment--hosting)
- [Release automation](#release-automation)
- [Notification / chat](#notification--chat)
- [How to find current SHAs](#how-to-find-current-shas)
- [Runtime deprecation timeline](#runtime-deprecation-timeline)
- [How this list stays current](#how-this-list-stays-current)

## GitHub-published (`actions/*`)

| Action | Current major | Notes |
|---|---|---|
| `actions/checkout` | v6 | Default Node runtime is now Node 24. v3 and v4 still receive critical fixes; v5 the previous major. |
| `actions/setup-node` | v6 | Node 24 default; supports `cache:` for npm/yarn/pnpm. |
| `actions/setup-python` | v6 | Built-in cache supports pip, pipenv, poetry. |
| `actions/setup-go` | v5 | Go module caching enabled by default. |
| `actions/setup-java` | v4 | Supports Temurin, Zulu, Microsoft, Corretto, Liberica. |
| `actions/setup-dotnet` | v4 | .NET 9 GA support. |
| `actions/cache` | v4 | Major rework from v3 — incompatible cache format. |
| `actions/cache/restore` | v4 | Restore-only sub-action. |
| `actions/cache/save` | v4 | Save-only sub-action. |
| `actions/upload-artifact` | v4 | Major rework. **Not compatible with v3 in same run.** Matrix uploads need unique names. |
| `actions/download-artifact` | v5 | v5 fixes minor v4 quirks; v4 still supported. |
| `actions/github-script` | v8 | Octokit-based scripting. |
| `actions/labeler` | v5 | Reads the repo's labeler config (typically under `.github/`). |
| `actions/stale` | v9 | Stale issue/PR handling. |
| `actions/dependency-review-action` | v4 | Blocks PRs introducing vulnerable deps. |
| `actions/attest-build-provenance` | v2 | Sigstore-backed build attestations. |
| `actions/create-github-app-token` | v1 | GitHub App token minting. |

### Deprecated — do NOT suggest

| Action | Status |
|---|---|
| `actions/checkout@v1`, `@v2`, `@v3` | Deprecated; warnings in logs. Upgrade to v6. |
| `actions/cache@v1`, `@v2`, `@v3` | Deprecated. Upgrade to v4 (clear cache). |
| `actions/upload-artifact@v1`, `@v2`, `@v3` | Deprecated and incompatible with v4 within same run. |
| `actions/setup-node@v1`–`@v3` | Deprecated. |
| `actions/setup-python@v1`–`@v4` | Deprecated. |

If you find any of these in a workflow, flag for upgrade.

## Cloud auth

| Action | Current major | Notes |
|---|---|---|
| `aws-actions/configure-aws-credentials` | v4 | Use OIDC (`role-to-assume:`); avoid `aws-access-key-id:`. |
| `azure/login` | v2 | Federated credential (OIDC) preferred. |
| `google-github-actions/auth` | v2 | Workload Identity Federation. |
| `google-github-actions/setup-gcloud` | v2 | Pairs with `auth@v2`. |
| `hashicorp/vault-action` | v3 | Read secrets from Vault using JWT/OIDC auth. |

## Anthropic / Claude Code

| Action | Current major | Notes |
|---|---|---|
| `anthropics/claude-code-action` | v1 | Run Claude Code agent in workflows. v1.0 introduced breaking changes from beta — see `../../KB-github-actions-platform/references/claude-code-cicd.md` § Beta → v1 migration. Supports direct Claude API, Amazon Bedrock (`use_bedrock: true`), Google Vertex AI (`use_vertex: true`), and Microsoft Foundry (via `CLAUDE_CODE_USE_FOUNDRY=1` env). |
| `actions/create-github-app-token` | v2 | Mint a GitHub App installation token for use as `github_token:` — needed when using a custom GitHub App (recommended for enterprise Claude Code setups so commits attribute to your app and trigger downstream CI). |

## Container build / publish

| Action | Current major | Notes |
|---|---|---|
| `docker/setup-qemu-action` | v3 | Required for cross-arch builds. |
| `docker/setup-buildx-action` | v3 | BuildKit setup. |
| `docker/login-action` | v3 | Works with GHCR, ECR, GAR, Docker Hub. |
| `docker/metadata-action` | v5 | Tag/label generation. |
| `docker/build-push-action` | v6 | Cache via `cache-from`/`cache-to`. |
| `aws-actions/amazon-ecr-login` | v2 | Pairs with configure-aws-credentials. |

## Language ecosystem

| Action | Current major | Notes |
|---|---|---|
| `astral-sh/setup-uv` | v6 | Fast Python package/project manager. |
| `pnpm/action-setup` | v4 | Run BEFORE `actions/setup-node` so cache works. |
| `pypa/gh-action-pypi-publish` | v1 | Trusted Publishing via OIDC. |
| `pypa/cibuildwheel` | v2 | Multi-platform wheel building. |
| `JS-DevTools/npm-publish` | v3 | Alternative to direct `npm publish`. |
| `goreleaser/goreleaser-action` | v6 | Go release automation. |
| `rust-lang/setup-rust-toolchain` | v1 | Rust toolchain installer (replaces deprecated actions-rs). |
| `Swatinem/rust-cache` | v2 | Cargo build caching for Rust. |
| `nrwl/nx-set-shas` | v4 | Compute affected base/head for Nx. |
| `supabase/setup-cli` | v1 | Supabase CLI installer. |

## Infrastructure-as-Code

| Action | Current major | Notes |
|---|---|---|
| `hashicorp/setup-terraform` | v3 | Sets up Terraform with optional wrapper. |
| `opentofu/setup-opentofu` | v1 | OpenTofu (Terraform fork) installer. |
| `pulumi/actions` | v6 | Pulumi preview/up. |
| `terraform-linters/setup-tflint` | v4 | Terraform linter. |
| `aquasecurity/tfsec-action` | v1 | Terraform security scan. |
| `aquasecurity/trivy-action` | v0 | Container & IaC vulnerability scanner. |
| `bridgecrewio/checkov-action` | v12 | Multi-IaC policy scanner. |

## Testing & coverage

| Action | Current major | Notes |
|---|---|---|
| `codecov/codecov-action` | v5 | Coverage upload. Token now strongly recommended even for OSS. |
| `coverallsapp/github-action` | v2 | Coveralls integration. |
| `dorny/test-reporter` | v2 | JUnit/etc. test result reporting. |
| `mikepenz/action-junit-report` | v5 | JUnit XML to PR annotations. |
| `jakebailey/pyright-action` | v2 | Pyright type checker with annotations. |

## Code quality / security scanning

| Action | Current major | Notes |
|---|---|---|
| `github/codeql-action/init` | v3 | CodeQL setup. |
| `github/codeql-action/analyze` | v3 | CodeQL analysis. |
| `github/codeql-action/upload-sarif` | v3 | SARIF upload to Code Scanning. |
| `actions/dependency-review-action` | v4 | Already listed above. |
| `gitleaks/gitleaks-action` | v2 | Secret scanning. |
| `trufflesecurity/trufflehog` | v3 | Alternative secret scanner. |

## Deployment / hosting

| Action | Current major | Notes |
|---|---|---|
| `nwtgck/actions-netlify` | v3 | Community Netlify deploy action. The Netlify CLI (`netlify-cli` via `npx`) is the official path; this action is a convenience wrapper. |
| `cloudflare/wrangler-action` | v3 | Cloudflare Workers deploy. |
| `vercel/action` | (no official) | Use `vercel` CLI directly via `npx vercel`. |
| `peaceiris/actions-gh-pages` | v4 | Community alternative to GitHub's native Pages deployment. The native `actions/deploy-pages@v4` is preferred for new setups. |
| `actions/configure-pages` | v5 | Native GitHub Pages configuration. |
| `actions/deploy-pages` | v4 | Native GitHub Pages deploy. |

## Release automation

| Action | Current major | Notes |
|---|---|---|
| `softprops/action-gh-release` | v2 | Create GitHub releases from tags. |
| `googleapis/release-please-action` | v4 | Conventional-commit-driven release management. |
| `changesets/action` | v1 | Changesets release PR for monorepos. |
| `semantic-release/semantic-release` | (npm pkg) | Run via `npx semantic-release`. |

## Notification / chat

| Action | Current major | Notes |
|---|---|---|
| `slackapi/slack-github-action` | v2 | Send to Slack via webhook or bot. |
| `8398a7/action-slack` | v3 | Community alternative. |
| `Ilshidur/action-discord` | v2 | Discord webhook. |

## How to find current SHAs

For any action listed above:

```bash
# Get the SHA for a specific tag
git ls-remote https://github.com/<org>/<repo> refs/tags/<tag>
# Example:
git ls-remote https://github.com/actions/checkout refs/tags/v6.0.0
```

The output's first column is the SHA. Use the full 40 characters in the workflow.

For automation, [`pinact`](https://github.com/suzuki-shunsuke/pinact) and [Renovate](https://docs.renovatebot.com/) (with `pinDigests: true`) auto-pin actions to SHAs and keep them updated.

## Runtime deprecation timeline

GitHub Actions runs JavaScript actions on a Node.js runtime baked into the runner. When a Node major reaches GitHub's deprecation window, all actions using that runtime emit warnings, then eventually fail.

| Runtime | Status (2026) |
|---|---|
| `node12` | Removed; actions still declaring it fail. |
| `node16` | Deprecated; warnings in logs. |
| `node20` | Deprecated mid-2026; final removal date TBD. |
| `node24` | Current default for new actions. |

When auditing, flag any `action.yml` in the repo's own composite/JS actions that declares an old runtime.

## How this list stays current

Recheck quarterly. Major-version bumps for `actions/*` are announced on the [GitHub blog](https://github.blog/changelog/) and in the action's repo README. For third-party actions, watch the upstream repo for releases.

Where in doubt, check the action's GitHub repo Releases page for the latest tag.
