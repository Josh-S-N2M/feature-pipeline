# `devcontainer.json` -- Field Reference and Patterns

The dev container spec is shared across Codespaces and VS Code Dev Containers. **Authoritative spec:** https://containers.dev/implementors/json_reference/. **Always verify a field against Context7 (`/websites/github_en` or `containers.dev`) before claiming it works a specific way.**


## Contents

- [File location and discovery](#file-location-and-discovery)
- [Top-level fields (grouped)](#top-level-fields-grouped)
- [Lifecycle commands](#lifecycle-commands)
- [Common patterns](#common-patterns)
- [Common pitfalls](#common-pitfalls)
- [When to escalate to Dockerfile or Compose](#when-to-escalate-to-dockerfile-or-compose)
- [Looking up unknown fields](#looking-up-unknown-fields)

## File location and discovery

In order of precedence:
1. `.devcontainer/devcontainer.json` -- canonical
2. `.devcontainer.json` -- repo root (legacy / simple cases)
3. `.devcontainer/<name>/devcontainer.json` -- multiple configs in one repo, user picks at create time

Multiple configs are how monorepos offer different per-package environments. Each subfolder name becomes a selectable label.

## Top-level fields (grouped)

### Base (choose exactly one)

| Field | Purpose |
|---|---|
| `image` | Reference a prebuilt image |
| `build` | Object with `dockerfile`, `context`, `args`, `target`, `cacheFrom` |
| `dockerComposeFile` | Path(s) to compose file(s); requires `service` |
| `service` | Compose service to attach to (with `dockerComposeFile`) |
| `runServices` | Other compose services to bring up alongside |
| `workspaceFolder` | Path inside container where repo is mounted (default `/workspaces/<repo>`) |
| `workspaceMount` | Override mount source/target/options |

### Features and customization

| Field | Purpose |
|---|---|
| `features` | Map of feature OCI ref → options. See `features.md` |
| `overrideFeatureInstallOrder` | Array of feature IDs in desired install order -- required when one feature depends on another |
| `customizations` | Tool-specific config; primarily `customizations.vscode` and `customizations.codespaces` |

### Customizations subfields

```jsonc
"customizations": {
  "vscode": {
    "extensions": ["publisher.id", ...],
    "settings": { "editor.formatOnSave": true }
  },
  "codespaces": {
    "openFiles": ["README.md", "src/index.ts"],
    "repositories": {                          // multi-repo permissions
      "OWNER/OTHER-REPO": {
        "permissions": { "contents": "read", "issues": "write" }
      }
    }
  }
}
```

`customizations.codespaces.repositories` requires the codespace user to grant cross-repo permissions on creation.

### Networking

| Field | Purpose |
|---|---|
| `forwardPorts` | Array of port numbers (or `"host:port"`) to forward |
| `portsAttributes` | Per-port config: `label`, `protocol` (`http`/`https`), `onAutoForward` (`notify`/`openBrowser`/`openPreview`/`silent`/`ignore`), `requireLocalPort`, `elevateIfNeeded`, `visibility` (`private`/`org`/`public`) |
| `otherPortsAttributes` | Defaults applied to any port not in `portsAttributes` |
| `appPort` | Legacy; prefer `forwardPorts` |

```jsonc
"forwardPorts": [3000, 5432],
"portsAttributes": {
  "3000": { "label": "Web", "onAutoForward": "openPreview", "visibility": "private" },
  "5432": { "label": "Postgres", "onAutoForward": "ignore" }
}
```

### Environment

| Field | Scope |
|---|---|
| `containerEnv` | Set in container's environment block (visible to all processes in container, including VS Code Server) |
| `remoteEnv` | Set only for processes started by tools (VS Code, terminals) -- not visible to background services |

`containerEnv` for things every process needs (`NODE_ENV=development`). `remoteEnv` for shell-only convenience.

```jsonc
"containerEnv": { "NODE_ENV": "development" },
"remoteEnv": { "PATH": "${containerEnv:PATH}:/workspaces/${localWorkspaceFolderBasename}/bin" }
```

Variable substitution available: `${localWorkspaceFolder}`, `${localWorkspaceFolderBasename}`, `${containerWorkspaceFolder}`, `${containerEnv:NAME}`, `${localEnv:NAME}`.

### Identity

| Field | Purpose |
|---|---|
| `remoteUser` | User VS Code Server runs as inside the container (default = image's non-root user) |
| `containerUser` | User PID 1 runs as |
| `updateRemoteUserUID` | (Linux) auto-align UID with host (default `true`) |
| `userEnvProbe` | How to load user shell env: `none`/`loginShell`/`loginInteractiveShell`/`interactiveShell` |

### Mounts and runtime

| Field | Purpose |
|---|---|
| `mounts` | Array of mount specs -- `"source=...,target=...,type=bind/volume"` |
| `runArgs` | Extra `docker run` flags |
| `init` | Add `tini` as PID 1 (recommended for proper signal handling) |
| `privileged` | Run privileged container (rare; required for some kernel features) |
| `capAdd` / `capDrop` | Linux capabilities |
| `securityOpt` | Docker security options |
| `shutdownAction` | `none` / `stopContainer` / `stopCompose` |

```jsonc
"mounts": [
  "source=${localEnv:HOME}/.ssh,target=/home/vscode/.ssh,type=bind,consistency=cached"
]
```

### Constraints

| Field | Purpose |
|---|---|
| `hostRequirements` | `cpus`, `memory`, `storage` -- filters available machine types |

## Lifecycle commands

Each accepts:
- **String** -- `sh -c "..."` (single command)
- **Array** -- `argv` form, no shell (`["npm", "ci"]`)
- **Object** -- keys are labels, values are commands run **in parallel** (`{"app": "npm run dev", "db": "docker compose up db"}`)

| Hook | When | Where | In prebuild? | Cached in image? | Use for |
|---|---|---|---|---|---|
| `initializeCommand` | Before any container action | **Local host** | n/a | No | Pre-flight checks; rare. **Beware:** opening a malicious repo can run this on your laptop. |
| `onCreateCommand` | Once, when container first created | Container | **Yes** | Yes (snapshot) | Heavy, deterministic, content-independent setup that benefits from prebuild caching |
| `updateContentCommand` | When content changes (incl. each prebuild) | Container | **Yes** | Yes (snapshot) | Repo-content-dependent setup: `npm ci`, `bundle install`, `pip install`, codegen |
| `postCreateCommand` | Once after creation | Container | **No** | No | Things needing secrets / Docker-in-Docker / things you don't want in the prebuild snapshot |
| `postStartCommand` | Every container start (incl. resume) | Container | n/a | No | Restart background services, refresh tokens |
| `postAttachCommand` | Every client attach | Container | n/a | No | Greet user, open files, start dev server |

**Rules of thumb:**
- Move installation that's the same across all branches into the **image/Dockerfile** if possible (cached forever, no recompute).
- Otherwise, content-independent setup → `onCreateCommand` (cached in prebuild).
- Content-dependent setup (depends on `package.json` etc.) → `updateContentCommand` (re-runs as content changes; still cached in prebuild).
- Secret-dependent or DinD work → `postCreateCommand`.
- Long-running dev server → `postAttachCommand` (object form so it doesn't block) or **don't run it** and let the user start it.

## Common patterns

### Pin everything

```jsonc
{
  "image": "mcr.microsoft.com/devcontainers/typescript-node:1-22-bookworm",
  "features": {
    "ghcr.io/devcontainers/features/github-cli:1": { "version": "latest" }
  }
}
```

Avoid `:latest` on the image. Major-pin features (`:1`) and use the feature's `version` option to control the installed tool version.

### Run setup in parallel (object form)

```jsonc
"postCreateCommand": {
  "deps": "npm ci",
  "submodules": "git submodule update --init --recursive",
  "tools": "pre-commit install"
}
```

### Open dev server on attach

```jsonc
"postAttachCommand": { "dev": "npm run dev" },
"portsAttributes": {
  "3000": { "onAutoForward": "openPreview" }
}
```

### Per-folder workspace in monorepo

```jsonc
"workspaceFolder": "/workspaces/my-monorepo",
"customizations": {
  "vscode": {
    "settings": {
      "files.exclude": { "**/node_modules": true }
    }
  },
  "codespaces": {
    "openFiles": ["packages/web/src/index.ts"]
  }
}
```

## Common pitfalls

- **Hard-coded ports in code.** The forwarded URL changes; reference `${CODESPACE_NAME}` and the `GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN` env var, or read from `process.env.PORT`.
- **Listening on `127.0.0.1`.** Port forwarding requires the service to listen on `0.0.0.0`.
- **`npm install` in `postCreateCommand`** when you have prebuilds enabled -- wastes the prebuild. Move to `updateContentCommand`.
- **`apt install` in `postCreateCommand`** -- gets wiped on every rebuild. Move to `onCreateCommand`, or better, into the Dockerfile or a feature.
- **Writing to `~/.config` and expecting it to persist** -- won't survive rebuild. Symlink from `/workspaces`.
- **Using `image` + `Dockerfile` simultaneously** -- pick one. Use `build.dockerfile` for custom Dockerfiles.

## When to escalate to Dockerfile or Compose

- Default image plus a few features -- stick with `image`.
- Need a system package not in any feature, or a specific tool version with custom build steps -- `build.dockerfile`.
- Need sidecar services (Postgres, Redis, message queue) -- `dockerComposeFile`.

See `assets/templates/dockerfile-based/` and `assets/templates/docker-compose/`.

## Looking up unknown fields

If a field appears in someone's config and you're not sure what it does:
1. Context7 query: `/websites/github_en` with `"devcontainer.json <fieldname>"`.
2. Fallback: `web_fetch` https://containers.dev/implementors/json_reference/
3. Cite which doc you used.
