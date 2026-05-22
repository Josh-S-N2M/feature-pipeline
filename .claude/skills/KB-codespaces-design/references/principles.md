# Codespaces Design Principles

## Contents

- Principle 1: Lifecycle hooks have strict order and scope
- Principle 2: Prebuilds capture some hooks, not others
- Principle 3: Only `/workspaces` persists across rebuild
- Principle 4: Right-size the machine class
- Principle 5: Secrets in Codespaces Secrets, never in the repo
- Principle 6: Features for known tools; Dockerfile for unknowns
- Principle 7: Port forwarding declared explicitly
- Principle 8: Dev environment ≠ production environment

## Principle 1: Lifecycle hooks have strict order and scope

`devcontainer.json` exposes several hooks; getting them wrong is the most common Codespaces design bug.

| Hook | When it runs | Scope | Prebuild captures? |
|---|---|---|---|
| `onCreateCommand` | Once, after container creation, before workspace mount | Container | Yes |
| `updateContentCommand` | After `onCreate` and on each `Rebuild Container`; runs after workspace mount | Container + workspace | Yes |
| `postCreateCommand` | Once, after `updateContent`, on first creation only | Container + workspace | NO |
| `postStartCommand` | On every start (creation, resume, rebuild) | Container + workspace | NO |
| `postAttachCommand` | On every attach (new terminal, reconnect) | Container + workspace | NO |

The Designer places setup at the right hook:

- **Image / OS tools that don't change frequently** → `onCreateCommand` (or Dockerfile).
- **Dependency installation tied to repo content (npm install, pip install, bundle install)** → `updateContentCommand`. Tied to the workspace, capturable by prebuilds.
- **First-time-only setup that depends on the workspace** → `postCreateCommand`. Examples: initialize a local DB schema, write a first-run marker file.
- **Setup that needs to run every start** → `postStartCommand`. Examples: start a background service. Use sparingly; runs every time the user opens the codespace.
- **Welcome message, terminal config, IDE-specific setup** → `postAttachCommand`. Runs on every new terminal. Must be fast.

A common bug: `npm install` in `postCreateCommand`. The dependency install runs once when the codespace is created, but prebuilds DON'T capture it — defeating the prebuild's purpose. Move to `updateContentCommand`.

## Principle 2: Prebuilds capture some hooks, not others

A prebuild snapshots the container after `onCreateCommand` and `updateContentCommand` run. It does NOT run `postCreateCommand`, `postStartCommand`, or `postAttachCommand`.

This means:

- Slow content-dependent setup belongs in `updateContentCommand` so prebuilds capture it.
- Side effects that need to happen per-creation (like "initialize a per-user config file") belong in `postCreateCommand`.
- Anything that needs the current user / runtime state belongs in `postStartCommand` or `postAttachCommand`.

The Designer documents the hook placement and the prebuild capture story in the per-layer subsection. A table mapping setup task → hook → captured-by-prebuild prevents the postCreate/updateContent confusion.

## Principle 3: Only `/workspaces` persists across rebuild

`/workspaces/<repo>` is mounted from a persistent volume. Everything else inside the container is ephemeral once you rebuild.

Implications:

- **Don't store build outputs outside `/workspaces`.** A `cargo target/` in `~/cache` is gone on rebuild.
- **Don't install user-config in `~`.** `~/.gitconfig`, `~/.npmrc` are ephemeral. Use dotfiles repo OR `postCreateCommand` that writes them.
- **Caches outside `/workspaces` rebuild from scratch each time.** Configure caches to live under `/workspaces` if rebuild-survival matters.

Across stop/start (not rebuild), `/tmp` and the container filesystem also persist. Only rebuild is destructive.

The Designer documents the persistence policy:

- What lives in `/workspaces` (source, generated artifacts to preserve, project-local caches).
- What's intentionally ephemeral (image-managed tools, system dirs).
- How re-init happens on rebuild (which lifecycle command restores what).

## Principle 4: Right-size the machine class

Codespaces machine classes range from 2-core / 4GB RAM to 32-core / 64GB. Cost scales with size.

The Designer picks based on the project's profile:

| Profile | Recommended class |
|---|---|
| TypeScript / Python service, single component | 2-core |
| TypeScript monorepo, frontend + backend | 4-core |
| Rust / C++ / large compilation | 4-core or 8-core (CPU-bound) |
| Big data tools (Spark local, large in-memory data) | 8-core+ (RAM-bound) |
| Container-based dev with docker-compose running 5+ services | 4-core or 8-core (concurrency) |

Default is 2-core. The Designer documents the default and the override mechanism: per-user override is available via the UI; project default is set in `devcontainer.json` via `machine.cpus` (org policy may constrain).

Don't over-provision "to be safe." Larger machines waste compute budget; the user can upgrade per-codespace if needed.

## Principle 5: Secrets in Codespaces Secrets, never in the repo

Codespaces has its own secret store (separate from Actions Secrets):

- **Repository Codespaces Secrets.** Per-repo; available to anyone with codespace access on the repo.
- **User Codespaces Secrets.** Per-user; available across codespaces they create.
- **Org Codespaces Secrets.** Org-level; mapped to selected repos.

The Designer documents:

- What secrets the codespace needs (auth tokens, API keys for development services).
- Which level of secret (repo / user / org) each one is.
- The fallback when a secret is absent (warn? fail? use a public sandbox key?).
- Explicit non-secrets (development DB URL, local-service ports) that can live in `devcontainer.json` directly.

Anti-pattern: a `.env` file checked into the repo. Even if .gitignored later, history retains it. Use the secret store.

For per-developer secrets (someone's personal API key): User Codespaces Secrets. The repo doesn't know or care about them.

## Principle 6: Features for known tools; Dockerfile for unknowns

Dev Container Features are versioned, well-tested installers for common tools: Node, Python, Go, Terraform, AWS CLI, Docker-in-Docker, etc.

When a tool is available as a Feature, use it:

```json
{
  "features": {
    "ghcr.io/devcontainers/features/node:1": { "version": "20" },
    "ghcr.io/devcontainers/features/aws-cli:1": {},
    "ghcr.io/devcontainers/features/terraform:1": { "version": "1.7.0" }
  }
}
```

Pros: zero Dockerfile maintenance; version pinning; works across base images.

When Features don't cover a tool:

- Custom Dockerfile installs it.
- Or `onCreateCommand` shell-installs it (acceptable for small one-offs).

Anti-patterns:

- Hand-rolling a Dockerfile to install Node when the Features registry has it.
- Mixing Features and manual installs of the same tool (drift).
- Using `:latest` instead of pinning a Feature version.

## Principle 7: Port forwarding declared explicitly

The Codespaces UI auto-forwards detected local services, but the Designer declares the intent explicitly:

```json
{
  "forwardPorts": [3000, 8080],
  "portsAttributes": {
    "3000": {
      "label": "Frontend",
      "visibility": "private",
      "onAutoForward": "openBrowserOnce"
    },
    "8080": {
      "label": "API",
      "visibility": "private",
      "onAutoForward": "notify"
    }
  }
}
```

- **`visibility`**: `private` (only the user) / `org` / `public`. Default to private; only widen if the workflow requires.
- **`onAutoForward`**: how the user is alerted (`silent`, `notify`, `openBrowser`, `openBrowserOnce`).
- **`label`**: human-readable name in the UI.

Document why each port is forwarded and at what visibility. Public visibility on a development service is rarely the right answer.

## Principle 8: Dev environment ≠ production environment

The codespace is for development. Productionizing it (running prod traffic, connecting to prod DB, holding prod secrets) is a category error.

The Designer makes this explicit:

- **Codespaces secrets contain development credentials.** Never production.
- **Local DB has development data.** Sample, anonymized, or empty.
- **External services are dev/sandbox endpoints.** Not prod APIs.
- **Idle timeout and retention are short.** Codespaces are ephemeral; data should not be unique-to-this-codespace.

When development requires touching prod (a one-off data investigation, an incident response), use a different mechanism (a separately-secured machine; explicit just-in-time access). The codespace is for routine dev work.

The Designer documents the "what's NOT in this codespace" list as a positive design statement: dev-only by intent.
