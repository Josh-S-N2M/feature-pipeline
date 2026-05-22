# Operational Playbooks

This is the doc to open when the user has an *intent* (review, create, refactor, remove, migrate, optimize) rather than a specific question. Each section is a checklist sub-agents can execute.


## Contents

- [§Audit -- Reviewing existing Codespaces setup](#audit-reviewing-existing-codespaces-setup)
- [§Create -- New Codespaces config from scratch](#create-new-codespaces-config-from-scratch)
- [§Refactor -- Common safe transformations](#refactor-common-safe-transformations)
- [§Remove -- Deprecating Codespaces from a repo](#remove-deprecating-codespaces-from-a-repo)
- [§Migrate -- From local dev to Codespaces](#migrate-from-local-dev-to-codespaces)
- [§Optimize -- Reducing creation time](#optimize-reducing-creation-time)
- [§Multi-repo / monorepo strategies](#multi-repo-monorepo-strategies)
- [Quick references](#quick-references)

## §Audit -- Reviewing existing Codespaces setup

When user asks: *"review our devcontainer setup"*, *"audit Codespaces config"*, *"is this dev container any good"*.

### Deliverables to produce

1. A findings list grouped by severity (Critical / Important / Nice-to-have).
2. A diff or PR-ready proposed changes for each finding.
3. A short narrative recap.

### Step-by-step

1. **Inventory.** Find every `devcontainer.json` in the repo:
   ```bash
   find . -name 'devcontainer.json' -o -name '.devcontainer.json'
   ```
   Note the structure: single config, multiple configs (`.devcontainer/<name>/`), or per-package configs in a monorepo.

2. **Read the base.** `image` / `build.dockerfile` / `dockerComposeFile`. Check:
   - [ ] Image is from a trusted registry
   - [ ] Image is pinned to a specific major (no `:latest`)
   - [ ] Image is current -- check the registry for a newer version
   - [ ] Custom Dockerfile (if any) doesn't `apt-get install` things that should be features

3. **Read the features.** For each:
   - [ ] Pinned to a major (`:1`, not `latest`)
   - [ ] Used (not just left over from a removed flow)
   - [ ] Not duplicating something already in the base image
   - [ ] If order-sensitive, `overrideFeatureInstallOrder` is set

4. **Read lifecycle commands.** Walk `initializeCommand` → `onCreateCommand` → `updateContentCommand` → `postCreateCommand` → `postStartCommand` → `postAttachCommand`:
   - [ ] Heavy content-independent setup is in `onCreateCommand` (cached in prebuild)
   - [ ] Content-dependent setup (`npm ci` etc.) is in `updateContentCommand` (cached in prebuild and re-runs on content change)
   - [ ] Secret-using or DinD setup is in `postCreateCommand` (not earlier)
   - [ ] No `apt install` outside the Dockerfile / feature (gets wiped on rebuild)
   - [ ] `postCreateCommand` doesn't curl-pipe-bash from random URLs

5. **Read ports.**
   - [ ] All exposed ports listed in `forwardPorts`
   - [ ] Each has a `portsAttributes` entry with a `label`
   - [ ] No port has `"visibility": "public"` baked in
   - [ ] Services bind to `0.0.0.0`, not `127.0.0.1` (check the project code)

6. **Read secrets/env.**
   - [ ] No secrets in `containerEnv` / `remoteEnv`
   - [ ] Codespaces secrets used for sensitive values
   - [ ] Multi-repo permissions in `customizations.codespaces.repositories` are minimal (no `write-all` unless justified)
   - [ ] Private registry secrets are configured correctly if non-`mcr.microsoft.com` images are used

7. **Read identity.**
   - [ ] `remoteUser` is non-root
   - [ ] No `runArgs: ["--privileged"]` unless justified
   - [ ] No `mounts` of sensitive host paths

8. **Check prebuild.** Is there a `.github/codespaces-prebuilds-*.yml` workflow (auto-generated) or a configured prebuild visible in repo Settings → Codespaces?
   - [ ] If creation takes >2 min and there's no prebuild → recommend enabling
   - [ ] If prebuild exists but recent runs failed → flag for fix
   - [ ] If prebuild exists for unused regions → suggest disabling

9. **Check machine sizing.** What does `hostRequirements` say? What's actually used? Are users on the right SKU?

10. **Output the findings.** Structure as a table:

    | Severity | Finding | Location | Proposed fix |
    |---|---|---|---|
    | Critical | `runArgs: ["--privileged"]` with no justification | `.devcontainer/devcontainer.json:42` | Remove unless DinD specifically requires |
    | Important | `npm install` in `postCreateCommand` defeats prebuild | `.devcontainer/devcontainer.json:30` | Move to `updateContentCommand` |
    | Nice | Image pinned to `:1` but no patch updates in 6 months | line 3 | Bump to current `1-22-bookworm` |

## §Create -- New Codespaces config from scratch

When user asks: *"set up Codespaces for this repo"*, *"add a devcontainer"*.

### Decision tree

```
Is project pure TypeScript/Node, no DB or external services?
├─ Yes → assets/templates/typescript-single.devcontainer.json
└─ No → Is it a TS monorepo (pnpm/turbo/yarn workspaces)?
        ├─ Yes → assets/templates/typescript-monorepo/
        └─ No → Does it need sidecar services (Postgres, Redis, etc.)?
                ├─ Yes → assets/templates/docker-compose/
                └─ No → Does it need a system tool not in any feature?
                        ├─ Yes → assets/templates/dockerfile-based/
                        └─ No → Is it IaC (Terraform / cloud CLI heavy)?
                                ├─ Yes → assets/templates/terraform-iac.devcontainer.json
                                └─ No → assets/templates/typescript-single.devcontainer.json (start here)
```

### Step-by-step

1. **Pick the template.** Copy from `assets/templates/`.
2. **Adjust the image.** Match the project's actual Node version (check `.nvmrc`, `package.json` `engines`, or `Dockerfile` if migrating from one).
3. **Add features only as needed.** Start minimal. Common adds for TS projects:
   - `github-cli` if scripts call `gh`
   - `aws-cli` / `azure-cli` / `gcloud` if deploying to that cloud
   - `docker-in-docker` if the project builds images
4. **Set `forwardPorts`.** From `package.json` scripts and the codebase, find every port the app listens on. Add a `label` for each.
5. **Set lifecycle commands.** Map them by purpose:
   - Image-bakeable system setup → into Dockerfile (skip if using `image`)
   - Content-independent setup (`pre-commit install`, etc.) → `onCreateCommand`
   - Lockfile install (`npm ci` / `pnpm install --frozen-lockfile`) → `updateContentCommand`
   - Secret-using or one-off setup → `postCreateCommand`
   - Greeting / file-open → `postAttachCommand` with `customizations.codespaces.openFiles`
6. **Add VS Code extensions.** The minimum: linter and formatter for TS (`dbaeumer.vscode-eslint`, `esbenp.prettier-vscode`). Don't bloat -- extensions slow startup.
7. **Test locally** (optional but recommended). Install Dev Containers extension in VS Code, "Reopen in Container" -- same `devcontainer.json` works.
8. **Push.** Open in Codespaces from the GitHub UI ("Code" button → Codespaces → "Create on `<branch>`").
9. **Iterate.** Watch the creation log; rebuild after each fix.
10. **Once stable, enable prebuild** if creation takes >2 min.

## §Refactor -- Common safe transformations

### Image → Dockerfile

When the default image plus features can't satisfy the project (need a specific system package, custom CA bundle, internal tool):

1. Create `.devcontainer/Dockerfile`:
   ```dockerfile
   FROM mcr.microsoft.com/devcontainers/typescript-node:1-22-bookworm
   RUN apt-get update && apt-get install -y --no-install-recommends \
         libwhatever-dev \
       && rm -rf /var/lib/apt/lists/*
   ```
2. Replace `"image": "..."` with:
   ```jsonc
   "build": { "dockerfile": "Dockerfile", "context": ".." }
   ```
3. `gh codespace rebuild --full -c NAME` (full = discard cached image).

### Dockerfile → Compose (adding a sidecar)

When the project starts needing Postgres/Redis/etc.:

1. Copy `assets/templates/docker-compose/` skeleton.
2. Move existing Dockerfile to `.devcontainer/Dockerfile`, reference from compose `build`.
3. Replace `"build": ...` with:
   ```jsonc
   "dockerComposeFile": "docker-compose.yml",
   "service": "app",
   "workspaceFolder": "/workspaces/${localWorkspaceFolderBasename}"
   ```
4. Add `"shutdownAction": "stopCompose"` so all sidecars stop with the codespace.
5. Update `forwardPorts` to include the sidecar's port if the user needs to hit it (e.g. db UI tools).

### Adding a feature

1. Add to `features` block, pin to major.
2. If the feature depends on another, set `overrideFeatureInstallOrder`.
3. Rebuild; check the feature install log shows success.
4. Verify the tool works from a terminal.

### Adopting prebuild on a hot repo

1. Move all heavy, content-independent install steps from `postCreateCommand` to `onCreateCommand`.
2. Move `npm ci` / `pip install` to `updateContentCommand`.
3. Verify creation still works end-to-end.
4. Repo Settings → Codespaces → Set up prebuild on the active branches and regions.
5. Wait for first prebuild workflow to complete (Actions tab).
6. Create a fresh codespace to verify "Prebuild ready" badge appears and creation is faster.

### Bumping image / feature versions

1. Update one at a time.
2. `gh codespace rebuild --full` (discards image cache so the bump actually takes).
3. Run the full project test suite.
4. If prebuilds enabled, manually trigger or wait for the next push to rebuild prebuilds.

## §Remove -- Deprecating Codespaces from a repo

When user asks: *"remove Codespaces from this repo"*.

### Checklist

- [ ] Delete `.devcontainer/` directory and any `.devcontainer.json` at repo root.
- [ ] Delete `.github/codespaces-prebuilds-*.yml` if it exists (auto-generated prebuild workflows).
- [ ] Disable prebuild in Repo Settings → Codespaces (releases storage).
- [ ] Remove repo-level Codespaces secrets (Repo Settings → Secrets and variables → Codespaces). Don't confuse with Actions secrets.
- [ ] Remove "Open in Codespaces" badges from README and any deep links.
- [ ] Update CONTRIBUTING.md to remove Codespaces instructions.
- [ ] Notify active users: anyone with running codespaces against this repo should commit and push, then delete their codespaces (`gh codespace list --repo OWNER/REPO`).
- [ ] If the repo was in an org-level secret's `selected repos`, remove it.
- [ ] Audit for code dependencies on `CODESPACES`, `GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN`, or `CODESPACE_NAME` env vars.

If only deprecating the *config* (keeping Codespaces support but switching to user-managed):
- Keep an empty repo, let users supply their own templates via `gh codespace create`'s template flow, or rely on the universal default image.

## §Migrate -- From local dev to Codespaces

### Source artifacts to map

| Local artifact | Codespaces equivalent |
|---|---|
| `README` setup steps (install Node, install pnpm, etc.) | Image + features |
| `make setup` / `bin/setup` script | `onCreateCommand` (or split per the lifecycle table) |
| `.envrc` / `.env.example` | Codespaces secrets (sensitive) + `containerEnv` (non-sensitive defaults) |
| `docker-compose.yml` (services + app) | `dockerComposeFile` + `service` |
| `.tool-versions` / `.nvmrc` | Image tag or feature `version` option |
| `.editorconfig` / `.prettierrc` | Already works as-is |
| Recommended VS Code extensions in `.vscode/extensions.json` | Already works; can promote to `customizations.vscode.extensions` for forced install |
| Cloud-SDK credential files (cloud creds, kubeconfigs, etc. — typically under home directory) | Codespaces secrets, written via `postCreateCommand` |

### Step-by-step

1. Pick the template that most closely matches the project (see §Create decision tree).
2. Translate `README` setup into the lifecycle hooks -- being careful to put pip/npm installs in `updateContentCommand` for prebuild caching.
3. Translate `.env.example` into Codespaces secrets at user or repo level.
4. Open a draft PR with the new `.devcontainer/`. Test by creating a codespace from the PR branch.
5. Fix any creation errors; iterate.
6. Update CONTRIBUTING.md with the "Open in Codespaces" path as an alternative to local setup.
7. Once a few people have used it successfully, enable prebuild.

## §Optimize -- Reducing creation time

If creation > 2 min, work through these in order:

1. **Enable prebuilds** for the active branches. This is the biggest win for most repos.
2. **Move setup earlier in the lifecycle** so it gets cached:
   - `postCreateCommand` → `onCreateCommand` (if content-independent)
   - `postCreateCommand` → `updateContentCommand` (if content-dependent)
3. **Bake stable system tools into the image** (Dockerfile or feature) instead of installing in lifecycle commands.
4. **Trim features** -- every feature adds ~10-30s. Drop unused ones.
5. **Trim VS Code extensions** in `customizations.vscode.extensions` -- they install on first attach.
6. **Use a smaller base image** -- `mcr.microsoft.com/devcontainers/typescript-node:1-22-bookworm` is ~600 MB; the universal image is ~10 GB.
7. **Pin features by digest** for reproducibility (and prebuild snapshot stability).
8. **Profile.** Read the creation log: time-stamp each section. Attack the slowest.

## §Multi-repo / monorepo strategies

### One devcontainer for the whole monorepo

Simplest. Single `.devcontainer/devcontainer.json` at root. `workspaceFolder` is the repo root. `updateContentCommand` runs `pnpm install` (or equivalent) from root.

Pros: single source of truth, one prebuild.
Cons: every developer pays for every package's deps; image gets fat with all toolchains.

### Per-package devcontainers

Multiple configs in `.devcontainer/<package-name>/devcontainer.json`. User picks at create time.

Pros: focused per-package envs (tiny TS-only env vs heavy ML env).
Cons: N prebuilds to maintain.

### Hybrid (recommended for most monorepos)

One devcontainer at root with the **superset** of common tooling, plus:
- `customizations.codespaces.openFiles` per-config to land users in the right place.
- Per-package `package.json` scripts (`pnpm --filter @scope/web dev`) instead of per-package containers.

Use prebuild only on the root config; switch to per-package configs only if the superset image grows past 2 GB or prebuild times exceed 10 min.

## Quick references

- Need a template? → `assets/templates/`
- Need to look up a field? → `references/devcontainer.md`
- Need to look up a feature? → `references/features.md` (then Context7)
- Need to look up an API? → `references/cli-and-api.md` (then Context7)
- Need to debug? → `references/troubleshooting.md`
