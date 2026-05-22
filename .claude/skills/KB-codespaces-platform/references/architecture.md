# Architecture, Lifecycle, and Persistence


## Contents

- [The stack](#the-stack)
- [Machine types](#machine-types)
- [Regions (geo)](#regions-geo)
- [Lifecycle states](#lifecycle-states)
- [Lifecycle transitions](#lifecycle-transitions)
- [Timeouts and retention](#timeouts-and-retention)
- [Directory persistence rules](#directory-persistence-rules)
- [The default user](#the-default-user)
- [What ships in the default image](#what-ships-in-the-default-image)
- [Network model (summary; see `security.md` for detail)](#network-model-summary-see-securitymd-for-detail)

## The stack

```
┌─────────────────────────────────────────┐
│ Client (browser / VS Code / JetBrains)  │  Thin client
└──────────────┬──────────────────────────┘
               │ HTTPS + WebSocket (port-forwarded)
┌──────────────▼──────────────────────────┐
│ Linux VM (Ubuntu host, regional)         │  GitHub-hosted, isolated network
│                                          │
│   ┌────────────────────────────────┐     │
│   │ Docker container (devcontainer)│     │
│   │  - VS Code Server              │     │
│   │  - User shell, tools, runtimes │     │
│   │  - /workspaces/<repo> mount   ◄─┼──── persistent volume on VM
│   └────────────────────────────────┘     │
└──────────────────────────────────────────┘
```

Regardless of the user's local OS, the codespace **always runs Linux**. The local OS only runs the client.

## Machine types

Available SKUs (verify current list via `gh codespace create --help` or REST API `GET /repos/{owner}/{repo}/codespaces/machines`):

| Name | Cores | RAM | Storage |
|---|---|---|---|
| `basicLinux32gb` | 2 | 8 GB | 32 GB |
| `standardLinux32gb` | 4 | 16 GB | 32 GB |
| `premiumLinux` | 8 | 32 GB | 64 GB |
| `largePremiumLinux` | 16 | 64 GB | 128 GB |
| `xLargePremiumLinux` | 32 | 128 GB | 128 GB |

Availability per repo varies based on org policy and `hostRequirements` in `devcontainer.json`. Always verify current SKUs and pricing via Context7 or the docs -- these change.

`hostRequirements` in `devcontainer.json` filters out machines too small for the project:
```jsonc
"hostRequirements": { "cpus": 4, "memory": "8gb", "storage": "32gb" }
```

## Regions (geo)

`UsEast`, `UsWest`, `EuropeWest`, `SoutheastAsia`. Auto-assigned by client IP unless overridden via `geo` parameter on creation. **Prebuilds are scoped per region** -- a prebuild for `UsEast` doesn't help `EuropeWest` users.

## Lifecycle states

| State | Meaning |
|---|---|
| `Created` | Resource exists; container not yet built |
| `Queued` / `Provisioning` | VM being allocated |
| `Available` | Running and connectable |
| `Starting` / `Awaiting` | Coming back from stopped |
| `Shutdown` / `Stopped` | Idle-timed-out or explicitly stopped; storage retained |
| `Failed` | Build/runtime error; not recoverable, must delete |
| `Rebuilding` | Container being rebuilt; data in `/workspaces` preserved |
| `Deleted` | Gone, including `/workspaces` contents |

## Lifecycle transitions

```
   ┌─────────┐ create  ┌──────────┐ stop/idle ┌─────────┐ delete  ┌─────────┐
   │ (none)  ├────────►│ Available├──────────►│ Stopped │────────►│ Deleted │
   └─────────┘         └────┬─────┘           └────┬────┘         └─────────┘
                            │ rebuild              │ start
                            └◄────────────────►────┘
```

- **Stop**: container halts. RAM lost. Disk persists.
- **Start**: existing container restarts. Runs `postStartCommand`, `postAttachCommand`. Does **not** run `onCreateCommand` or `postCreateCommand`.
- **Rebuild** (`gh codespace rebuild`): re-runs the container build using the cached image; `/workspaces` survives, everything else is wiped. Re-runs the full lifecycle (`onCreate*` → `postAttach*`).
- **Full rebuild** (`gh codespace rebuild --full`): also discards the cached image. Use after changing the Dockerfile or feature versions.
- **Delete**: VM and all storage gone. Uncommitted work in `/workspaces` is lost.

## Timeouts and retention

| Setting | Default | Max | Override path |
|---|---|---|---|
| Idle timeout | 30 min | 240 min | User setting → org policy can cap |
| Retention period | 30 days | 30 days | User setting → org policy can cap |

A stopped codespace keeps consuming **storage billing** until deleted or retention expires.

`idle_timeout_minutes` and `retention_period_minutes` can be set per-codespace at creation via REST API.

## Directory persistence rules

| Path | Stop/start | Rebuild | Delete |
|---|---|---|---|
| `/workspaces/<repo>` | ✅ | ✅ | ❌ |
| `/workspaces/.codespaces/.persistedshare` | ✅ | ✅ | ❌ |
| `/tmp` | ✅ | ❌ | ❌ |
| `~` (home) | ✅ | ❌ | ❌ |
| `/usr/local/...` etc. | ✅ | ❌ | ❌ |

```audit-example -- Documents the Codespaces persistence pattern: home-directory configuration files (cloud SDK credentials, SSH keys, etc.) must be symlinked from postCreateCommand to survive container rebuilds. The auditor flags the credential-file path reference; this is documentation of WHERE the auditor's pattern fires in real Codespaces configuration, not an instruction to embed credentials.
**Implication:** any binary you `apt install` or any global tool config you write outside `/workspaces` is gone after `--full` rebuild. Bake those into the image (Dockerfile / Features) instead. For things that *must* live in home (e.g. `~/.aws/credentials`), symlink from `postCreateCommand`:
```

```jsonc
"postCreateCommand": "mkdir -p /workspaces/.devcontainer/aws && ln -sf /workspaces/.devcontainer/aws ~/.aws"
```

## The default user

Most `mcr.microsoft.com/devcontainers/*` images create a non-root user named `vscode` (or `node` in the typescript-node image). VS Code Server and your shell run as that user. `sudo` works without password by default.

- `remoteUser` -- who VS Code Server and integrated terminal run as. Default = the image's non-root user.
- `containerUser` -- who the container's `PID 1` runs as. Default = whatever the Dockerfile `USER` directive says.
- `updateRemoteUserUID: true` (default on Linux) -- adjusts the in-container user's UID to match the host so file mounts work without permission errors.

## What ships in the default image

`mcr.microsoft.com/devcontainers/universal:2` (default if no devcontainer.json exists) includes Node, Python, Java, .NET, Go, Ruby, PHP, Rust, common CLIs, and many SDKs. It's heavy (~10 GB) -- for a TS-only project, prefer `mcr.microsoft.com/devcontainers/typescript-node:1-22-bookworm`.

Image tag conventions:
- `mcr.microsoft.com/devcontainers/<name>:<major>-<variant>-<distro>` -- e.g. `1-22-bookworm` = v1 of feature script + Node 22 + Debian Bookworm
- Pin to a major version (`:1-...`) but accept patch updates.
- Avoid `:latest` -- bakes into prebuilds and surprises everyone on rebuild.

## Network model (summary; see `security.md` for detail)

- Each codespace = own VM, own virtual network
- Outbound HTTPS/HTTP to internet allowed
- Inbound only via the GitHub-managed port-forwarding service (per-port URLs like `https://CODESPACE-NAME-PORT.app.github.dev`)
- Codespaces cannot reach each other on internal networks
