# Troubleshooting


## Contents

- [The logs](#the-logs)
- [Common failures -- diagnostic tree](#common-failures-diagnostic-tree)
- [Diagnostic playbook (for sub-agents)](#diagnostic-playbook-for-sub-agents)
- [Looking up obscure errors](#looking-up-obscure-errors)

## The logs

| Log | How to read |
|---|---|
| **Creation log** | Container build, feature install, lifecycle commands up to first attach. **Read this first** for any creation failure. |
| **Container log** | Runtime container stderr/stdout. |
| **VS Code Server log** | Editor-side issues. |
| **Extension host log** | Per-extension errors. |

### Accessing logs

```bash
# Creation log via gh
gh codespace logs -c CODESPACE_NAME

# Save full bundle from VS Code
# Command Palette → "Codespaces: Export Logs" → unzip
```

In VS Code (browser or desktop): Command Palette →
- `Codespaces: View Creation Log`
- `Codespaces: Export Logs` (saves a zip with all logs)
- `Developer: Show Logs...` → Extension Host (for extension issues)

### Reading the creation log

Look for these section markers (in order):
1. `Creating codespace` / `Setting up prebuilt codespace` (← prebuild hit)
2. `Building image` (Dockerfile path) or `Pulling image` (image path)
3. `Running 'install' commands for features:` (feature install order + per-feature output)
4. Lifecycle commands: `Running 'onCreateCommand'`, `Running 'updateContentCommand'`, etc.
5. `Codespace created` (success) or `Failed to create codespace` (with reason)

## Common failures -- diagnostic tree

### Codespace creation fails entirely

1. **GitHub Status page** -- https://www.githubstatus.com -- check for incidents. Most one-off failures are transient.
2. **Re-create** -- delete the failed codespace (it's permanently broken) and try again.
3. **Build > 1 hour** -- GitHub cancels at 1 hr. Check creation log for which step is slow:
   - Heavy feature install → swap to a custom Dockerfile that bakes the tools in.
   - Slow `onCreateCommand` → enable prebuilds.
   - Big repo clone → consider `git clone --depth 1` patterns or switch to a `dockerComposeFile` that mounts code on demand.
4. **Spending limit hit** -- admin sees this in audit log; user sees a 403 message at create time.
5. **Image pull auth failure** -- see private-registry section below.

### Codespace creates but with a banner ("Container failed to start")

Almost always: a lifecycle command exited non-zero.

1. Open creation log. Search for the exit code.
2. Common culprits:
   - `npm ci` failing because a private-registry `.npmrc` token isn't set (Codespaces secret missing or named wrong).
   - `postCreateCommand` calling a binary not yet installed (wrong feature or wrong order).
   - `apt-get install` failing for missing `sudo`, fix: `"postCreateCommand": "sudo apt-get update && sudo apt-get install -y ..."`.
3. Open a terminal in the broken codespace and run the failing command manually to reproduce.
4. Edit `devcontainer.json`, then `gh codespace rebuild -c NAME` (or `--full` if you changed features/Dockerfile).

### Port forwards but service unreachable

| Symptom | Cause | Fix |
|---|---|---|
| URL gives 502 | Service not actually listening | Check `lsof -i :PORT` in codespace |
| URL gives "connection refused" | Service listening on `127.0.0.1` only | Bind to `0.0.0.0` |
| URL works locally but not on phone/external | Visibility = private | Set to `org` or `public` (with care) |
| URL changes between sessions | Expected | Use `${CODESPACE_NAME}` in URL refs, not hardcoded |
| URL gives auth page | Visibility = private and not signed in | Sign in to GitHub in that browser |

The forwarded URL pattern: `https://CODESPACE_NAME-PORT.app.github.dev` (or the codespace's region-specific domain -- check `gh codespace ports`).

### Auth to private repos fails

```
fatal: could not read Username for 'https://github.com': No such device or address
```

1. **`GITHUB_TOKEN` scope** -- by default reads only the source repo. For other private repos, add `customizations.codespaces.repositories` permissions in `devcontainer.json`. Rebuild after.
2. **Dotfiles overriding URL config** -- see `secrets-and-env.md`. Check `git config --list --show-origin` for unwanted overrides.
3. **HTTPS vs SSH mismatch** -- Codespaces uses HTTPS by default; if your dotfiles force SSH, fall back gracefully.

### `gh codespace ssh` hangs or times out

1. Codespace might be stopped -- `gh codespace list` to check state. SSH triggers start, which can take 10-30s.
2. SSH host key cached locally and machine recreated → `ssh-keygen -R "cs.${CODESPACE_NAME}.${USER}.github.dev"`.
3. Local SSH agent running but with no usable keys -- `gh codespace ssh` generates and uses its own key in `~/.config/gh/codespaces/`. Don't fight it.

### GPG signing not working (commits show "Unverified")

The default flow auto-signs with a GitHub-managed key. Things that break it:

1. Dotfiles set `gpg.program` → unset, or guard with `[ -z "$CODESPACES" ]`.
2. Dotfiles set `commit.gpgsign = false` → remove or guard.
3. Dotfiles set `user.signingkey` to a key not present in the codespace → unset.

Check active config:

```bash
git config --list --show-origin | grep -i -E 'gpg|sign'
```

Anything coming from `~/.gitconfig` or `/workspaces/.codespaces/.persistedshare/dotfiles/...` is suspect.

### Private registry image pull fails

Check the prefix-triple secrets (`<PREFIX>_CONTAINER_REGISTRY_*`) are:

1. **Set** -- at user, repo, or org level (whichever applies).
2. **Spelled correctly** -- exact suffix matters: `_CONTAINER_REGISTRY_SERVER`, `_USER`, `_PASSWORD`.
3. **Available to this repo** -- if org-level, that repo must be in the secret's selected repos.
4. **Not expired** -- PATs and OAuth tokens expire.

For `ghcr.io` images owned by the same org: no secrets needed, but the package's "Codespaces access" must be set in the package settings to allow the repo.

### Prebuild not being used

In creation log, check for `Setting up prebuilt codespace` (hit) vs `Setting up new codespace` (miss). Reasons for misses:

- User created from a branch with no prebuild config.
- User selected a different `devcontainer.json` than the one prebuilds target.
- User's region has prebuilds disabled.
- Prebuild workflow most recently failed → check Actions tab.
- `devcontainer.json` was modified more recently than the latest successful prebuild.

### "Cannot connect to the Docker daemon" inside codespace

DinD feature isn't installed. Add:

```jsonc
"features": {
  "ghcr.io/devcontainers/features/docker-in-docker:2": {}
}
```

…and rebuild. Note: DinD pulls don't work in `onCreateCommand` (daemon not running yet); use `postCreateCommand`.

### File permission errors on bind mounts

Caused by UID mismatch between host and container. Default behavior (`updateRemoteUserUID: true` on Linux) handles this. If you've explicitly disabled it or are using a custom `containerUser`, set:

```jsonc
"updateRemoteUserUID": true,
"remoteUser": "vscode"
```

…and rebuild.

### Extension not loading in browser editor

1. Check Extension Host log (`Developer: Show Logs... → Extension Host`).
2. Some extensions don't support the web editor -- check the extension's marketplace page for "Workspace support: virtual workspaces" / "Limited" / "None".
3. Try in VS Code desktop (`gh codespace code -c NAME`) -- full extension support there.

## Diagnostic playbook (for sub-agents)

When user reports an issue, gather in this order:

1. **What state?** `gh codespace list` (running/stopped/failed?)
2. **What changed recently?** Git log of `.devcontainer/` and lockfiles.
3. **Creation log.** `gh codespace logs -c NAME`. Find the first error.
4. **Reproduce.** SSH into codespace, run the failing command manually.
5. **Isolate.** Comment out features/lifecycle steps until creation succeeds; re-add to find the offender.
6. **Fix in `devcontainer.json`.** Rebuild (`gh codespace rebuild -c NAME` or `--full`).

## Looking up obscure errors

For exact error messages and recent changes:

1. Context7: `/websites/github_en` with `"Codespaces troubleshooting <error keyword>"`.
2. Fallback: `web_fetch` `docs.github.com/en/codespaces/troubleshooting`.
3. Last resort: GitHub Community Discussions search.
