# Security Model and Hardening


## Contents

- [Isolation guarantees](#isolation-guarantees)
- [Trust model on creation](#trust-model-on-creation)
- [Secret handling rules](#secret-handling-rules)
- [Port-forwarding visibility](#port-forwarding-visibility)
- [Image trust](#image-trust)
- [Dotfiles caution](#dotfiles-caution)
- [Hardening checklist for review](#hardening-checklist-for-review)
- [Org-level controls (see `org-management.md`)](#org-level-controls-see-org-managementmd)

## Isolation guarantees

| Layer | Boundary |
|---|---|
| **VM** | Each codespace gets its own VM. No sharing across users or codespaces. |
| **Network** | Per-codespace virtual network. Codespaces cannot reach each other on internal IPs. Inbound from internet is **blocked** except via the GitHub-managed port-forwarding service. Outbound to internet is **allowed**. |
| **Storage** | Per-codespace volume. Wiped on delete. Survives stop/start (and rebuild for `/workspaces`). |
| **Identity** | Codespace inherits the creating user's GitHub identity for `GITHUB_TOKEN`. Multi-repo permissions require explicit grant. |

There is no shared filesystem, no shared cache, no cross-codespace IPC.

## Trust model on creation

When a user creates a codespace from an **unfamiliar repo**, GitHub prompts: *"This repository contains a dev container configuration. The configuration may run code on your behalf."* The user must opt in.

**Why it matters:** `initializeCommand` runs **on the user's local host** (when using VS Code Dev Containers locally; not in Codespaces) -- but `onCreateCommand`, `postCreateCommand`, and the dotfiles install script all run inside the codespace as the user, with that user's `GITHUB_TOKEN` and any granted org/repo secrets. **A malicious devcontainer.json can:**

- Exfiltrate `GITHUB_TOKEN` to attacker servers (outbound is allowed)
- Read any Codespaces secret the codespace has access to
- Make API calls as the user against any repo `GITHUB_TOKEN` can reach
- Persist via dotfiles or `/workspaces` for the user's next session

**Sub-agent rule:** when reviewing a `devcontainer.json` from an unfamiliar source, **read all lifecycle commands and feature install scripts before recommending the user opens it.**

## Secret handling rules

| Rule | Why |
|---|---|
| Never commit secrets in `devcontainer.json` (incl. `containerEnv`, `remoteEnv`) | The file is in the repo -- anyone with read access sees it. |
| Use Codespaces secrets, not Actions secrets | Different stores. Setting one doesn't set the other. |
| Don't echo secrets in `postCreateCommand` | Goes to creation log, which org admins can read. |
| Don't store secrets in `/workspaces` | Workspaces folder is included in publish-as-repo, exports, and is visible to anyone the user shares the codespace with. |
| Codespaces secrets ≠ visible during prebuild | If you need a secret at prebuild time, configure it as a "permitted prebuild secret" (org-level setting). Otherwise, postpone secret-using setup until `postCreateCommand` (runs on user codespace creation, after secrets are available). |
| Rotate secrets when a developer leaves the org | Secrets persist in their personal codespaces until manually revoked. |

## Port-forwarding visibility

Three levels:

| Visibility | Who can reach the URL |
|---|---|
| **Private** (default) | Only the codespace owner, signed in to GitHub |
| **Org** | Members of the repo's org (signed in) |
| **Public** | **Anyone with the URL** |

Public URLs are not indexed but are unauthenticated. Use only for short-lived demos and revert before stopping work. **Never** mark a port public for a service that exposes data, admin actions, or a database.

Setting via CLI:

```bash
gh codespace ports visibility 3000:public -c NAME
gh codespace ports visibility 3000:private -c NAME
```

Setting via `devcontainer.json`:

```jsonc
"portsAttributes": {
  "3000": { "visibility": "private" }
}
```

(`devcontainer.json` sets the *initial* default; runtime CLI changes it for the active session.)

## Image trust

| Source | Trust |
|---|---|
| `mcr.microsoft.com/devcontainers/*` | Microsoft-published, integrity-verified. Default-safe. |
| `ghcr.io/devcontainers/features/*` (official) | Maintained by the dev containers org. Reasonable. |
| `ghcr.io/devcontainers-contrib/features/*` (community) | Community-maintained. Read the install script before adopting. |
| Random Docker Hub images | **No trust.** A `:latest` tag from a small project can change under you. |
| Internal registries | As trusted as your org's processes. |

For maximum safety, **mirror critical base images and features into a private registry** under your control. Pin by digest (`@sha256:...`) for reproducibility.

## Dotfiles caution

Dotfiles run as the user before `postCreateCommand`. Common footguns:

- A dotfiles repo with `gpg.program` set → breaks Codespaces auto-signing.
- A dotfiles repo with `git config --global url."git@..."` → breaks HTTPS+`GITHUB_TOKEN` auth in Codespaces.
- A dotfiles repo with credentials (yes, people do this) → leaked across all the user's codespaces.

Guard Codespaces-incompatible config with the `$CODESPACES` env var (set to `true` in every codespace).

## Hardening checklist for review

When auditing a `devcontainer.json` from a security perspective:

- [ ] No secrets in `containerEnv`, `remoteEnv`, or `runArgs`
- [ ] No `--privileged` or `runArgs: ["--privileged"]` unless justified
- [ ] No `securityOpt: ["seccomp=unconfined"]` or `apparmor:unconfined` unless justified
- [ ] No `mounts` of host paths beyond `~/.ssh` (and even that should be questioned)
- [ ] `remoteUser` is **not** root unless required
- [ ] Image and features are pinned to majors (not `:latest`)
- [ ] Image source is trusted (`mcr.microsoft.com/...` or org-controlled)
- [ ] `postCreateCommand` doesn't curl-pipe-bash from random URLs
- [ ] `customizations.codespaces.repositories` permissions are minimal (no `write-all` unless required)
- [ ] No port marked `"visibility": "public"` by default
- [ ] No outbound webhook calls to non-org domains in lifecycle commands
- [ ] No `git config --global` overrides that break Codespaces auth/signing

## Org-level controls (see `org-management.md`)

- Restrict allowed base images
- Restrict machine types
- Set max idle timeout / retention
- Disallow public port forwarding (in some plans)
- Require Codespaces only for specific repos
- Audit log: codespace create/start/stop/delete events
