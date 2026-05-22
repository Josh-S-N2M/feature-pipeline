# Secrets, Environment, Dotfiles, Registries


## Contents

- [Codespaces secrets -- the three tiers](#codespaces-secrets-the-three-tiers)
- [`containerEnv` vs `remoteEnv` (in `devcontainer.json`)](#containerenv-vs-remoteenv-in-devcontainerjson)
- [Persisting env vars across stops/rebuilds](#persisting-env-vars-across-stopsrebuilds)
- [Dotfiles](#dotfiles)
- [`GITHUB_TOKEN` -- automatic auth](#githubtoken-automatic-auth)
- [Private container registries](#private-container-registries)
- [GPG commit signing](#gpg-commit-signing)
- [SSH keys](#ssh-keys)
- [Looking up current values](#looking-up-current-values)

## Codespaces secrets -- the three tiers

| Tier | Configured at | Scope | Use case |
|---|---|---|---|
| **User** | https://github.com/settings/codespaces | The user's codespaces, in selected repos | Personal API keys |
| **Repository** | Repo Settings → Secrets and variables → Codespaces | All codespaces created from this repo | Project-wide non-sensitive config |
| **Organization** | Org Settings → Codespaces → Codespaces secrets | Selected repos in the org | Shared service credentials |

Codespaces secrets surface inside the container as **environment variables** (not files). Naming follows env-var conventions: uppercase, underscore-separated.

**Codespaces secrets are a different store from Actions secrets.** Setting a value in the Actions UI does not make it available in Codespaces. Set both if both contexts need it.

After adding a new secret, **restart the codespace** for it to be picked up.

### Setting via gh CLI

```bash
# User-level (settings page is the canonical UI; CLI works for repo/org)
gh secret set MY_SECRET --user

# Repo-level Codespaces secret
gh secret set MY_SECRET --app codespaces --repo OWNER/REPO

# Org-level
gh secret set MY_SECRET --app codespaces --org ORG --visibility selected --repos REPO1,REPO2
```

## `containerEnv` vs `remoteEnv` (in `devcontainer.json`)

- **`containerEnv`** -- set in the container's environment block. Visible to **every process** including PID 1, background services, and the VS Code Server. Bakes into the prebuild snapshot.
- **`remoteEnv`** -- only set for processes started by tools (terminals, debug sessions, tasks). Not visible to background services started by `postStartCommand`.

```jsonc
"containerEnv": {
  "NODE_ENV": "development",
  "DATABASE_URL": "postgresql://localhost:5432/dev"
},
"remoteEnv": {
  "PATH": "${containerEnv:PATH}:/workspaces/${localWorkspaceFolderBasename}/.bin"
}
```

**Don't put secrets in `containerEnv` or `remoteEnv`** -- both live in the committed `devcontainer.json`. Use Codespaces secrets, which the runtime injects.

## Persisting env vars across stops/rebuilds

Codespaces secrets are re-injected on every start, so they're already persistent.

```audit-example -- Documents the Codespaces postCreateCommand pattern for environment-variable persistence; the auditor's shell-startup-file scanner flags HOME-relative bashrc references, but this is documentation of a normal codespace customization pattern (modifying the bashrc INSIDE the codespace container, not the user's host) — the substance claim is that the in-container shell-startup file is a normal customization vector for codespaces and not a host persistence anti-pattern.
For **non-secret** env vars you want available in every shell:

> **Scope note:** the example below modifies `~/.bashrc` *inside the codespace container only*. It does not touch the user's host machine. This is a normal codespace customization pattern, not a host-level shell-startup modification.

"postCreateCommand": "echo 'export MY_VAR=hello' >> /workspaces/.bashrc-extras && echo 'source /workspaces/.bashrc-extras' >> ~/.bashrc"

Writing to `/workspaces/...` survives rebuild; sourcing it from `~/.bashrc` (which is wiped on rebuild) means re-running the append in `postCreateCommand` keeps it working.
```

## Dotfiles

Each user can specify a personal dotfiles repo at https://github.com/settings/codespaces. When a codespace starts, GitHub clones it into `/workspaces/.codespaces/.persistedshare/dotfiles` and runs (in priority order) `install`, `install.sh`, `bootstrap`, `bootstrap.sh`, `setup`, `setup.sh`, or symlinks all dotfiles to `$HOME`.

**Rules:**
- Dotfiles run **as the user**, before `postCreateCommand`.
- Don't put credentials in dotfiles -- they're a personal repo, but they run automatically and silently.
- Beware Git config conflicts: setting `gpg.program` in dotfiles can break Codespaces' auto-signing. Guard with `[ -z "$CODESPACES" ]`.

```bash
# In ~/.gitconfig (in dotfiles repo) -- Codespaces-aware override
[url "git@github.com:"]
  insteadOf = https://github.com/
```

```bash
# Or guard at install time
if [ -z "$CODESPACES" ]; then
  git config --global url."git@github.com:".insteadOf "https://github.com/"
fi
```

## `GITHUB_TOKEN` -- automatic auth

Every codespace gets a `GITHUB_TOKEN` env var, scoped to **read** permissions on the source repository by default. Use it for `gh` and `git` operations:

```bash
gh repo view             # works out of the box
git clone https://github.com/OWNER/OTHER-PUBLIC-REPO   # works
```

### Multi-repo permissions

For a codespace that needs write or cross-repo access, declare in `devcontainer.json`:

```jsonc
"customizations": {
  "codespaces": {
    "repositories": {
      "OWNER/SECONDARY-REPO": {
        "permissions": {
          "contents": "write",
          "issues": "write",
          "pull_requests": "write"
        }
      }
    }
  }
}
```

The user is prompted to authorize these scopes the first time they create the codespace. They can revoke from https://github.com/settings/codespaces.

For permissions on the **current repo** beyond the default read:

```jsonc
"customizations": {
  "codespaces": {
    "repositories": {
      "${localEnv:GITHUB_REPOSITORY}": {
        "permissions": "write-all"
      }
    }
  }
}
```

(Or list specific permission keys; `write-all` is convenient but broad.)

## Private container registries

To pull a private base image at codespace creation, set three secrets per registry, with a shared prefix:

| Secret name | Value |
|---|---|
| `<PREFIX>_CONTAINER_REGISTRY_SERVER` | e.g. `mycorp.azurecr.io` |
| `<PREFIX>_CONTAINER_REGISTRY_USER` | username |
| `<PREFIX>_CONTAINER_REGISTRY_PASSWORD` | token / password |

Set at **user**, **repo**, or **org** level. Codespaces detects the triple, logs in, and pulls the image. Can configure multiple registries by using different prefixes (`ACR_`, `DOCKERHUB_`, etc.).

For **GitHub Container Registry** (`ghcr.io`) packages owned by the same org as the codespace's repo, **no secrets needed** -- Codespaces auto-authenticates.

For **runtime** Docker pulls (DinD `docker pull`), the same secrets are written into `~/.docker/config.json` automatically, **after `onCreateCommand` and before `postCreateCommand`**. So:

- `onCreateCommand` -- cannot pull private images (DinD not running, no auth yet).
- `postCreateCommand` -- can.

## GPG commit signing

Codespaces auto-configures Git to sign commits with a GitHub-managed key, so commits show as **Verified**. Don't override:

- `gpg.program`
- `commit.gpgsign`
- `user.signingkey`

…in your dotfiles or repo `.gitconfig` unless you understand you're disabling Codespaces signing. If you must override locally only:

```bash
git config --system gpg.program gpg2     # system-level, not pushed to dotfiles
```

## SSH keys

By default, codespaces use HTTPS + `GITHUB_TOKEN` for git operations -- no SSH key needed. If you must use SSH (e.g. to pull from a non-GitHub remote):

- Mount your local SSH agent: `"mounts": ["source=${localEnv:HOME}/.ssh,target=/home/vscode/.ssh,type=bind,consistency=cached"]`
```audit-example -- Documents the Codespaces deploy-key pattern: storing an SSH private key as a Codespaces secret and writing it to the HOME-relative SSH-private-key path at container-start time. The auditor flags the SSH-private-key path reference; this is documentation of the canonical Codespaces SSH-deploy-key flow, not an instruction to write real keys here.
- Or store a deploy key as a Codespaces secret and write to `~/.ssh/id_ed25519` from `postCreateCommand`. **Carefully** -- secrets-as-files have failure modes.
```

## Looking up current values

For exact current behavior of any of the above (especially permission scopes and prebuild secret behavior), query Context7 (`/websites/github_en` with the specific topic) or `web_fetch` the relevant page under `docs.github.com/en/codespaces/`.
