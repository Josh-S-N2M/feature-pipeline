# Codespaces Patterns and Anti-Patterns

## Contents

- Base-mechanism patterns (image / Dockerfile / docker-compose)
- Lifecycle-command placement patterns
- Prebuild patterns
- Multi-container patterns
- Tool-installation patterns
- Secrets-and-config patterns
- Monorepo patterns
- Anti-patterns reviewers should flag
- Decision frames

## Base-mechanism patterns

### Universal image + Features

```json
{
  "image": "mcr.microsoft.com/devcontainers/universal:linux",
  "features": {
    "ghcr.io/devcontainers/features/node:1": { "version": "20" },
    "ghcr.io/devcontainers/features/python:1": { "version": "3.12" }
  }
}
```

**When to use.** Default for new projects. Zero Dockerfile; quick to set up; well-maintained.

**Strengths.** Fast first build (image is cached on GitHub's side); Features versioned independently.

### Language-specific prebuilt image

```json
{
  "image": "mcr.microsoft.com/devcontainers/typescript-node:20"
}
```

**When to use.** Single-language project; the official image fits.

**Strengths.** Smaller image; faster start; less to configure.

### Custom Dockerfile

```json
{
  "build": {
    "dockerfile": "Dockerfile",
    "args": { "NODE_VERSION": "20" }
  }
}
```

**When to use.** Specific package versions, internal package registry config, or proprietary tooling.

**Risks.** Dockerfile maintenance burden; longer first build.

### docker-compose for multi-container

```json
{
  "dockerComposeFile": "docker-compose.yml",
  "service": "app",
  "workspaceFolder": "/workspace"
}
```

**When to use.** Local dev requires DB + cache + queue + app running together.

**Risks.** Longer startup; more memory; complexity multiplies.

## Lifecycle-command placement patterns

### Dependency install in `updateContentCommand`

```json
{
  "updateContentCommand": "npm ci && pip install -r requirements.txt"
}
```

**When to use.** Default for content-tied dependencies (package locks, requirements files).

**Why this hook.** Captured by prebuilds; re-runs when content changes (rebuild).

### One-time setup in `postCreateCommand`

```json
{
  "postCreateCommand": "./.devcontainer/init-local-db.sh"
}
```

**When to use.** Project-specific first-time initialization (local DB schema, marker files).

**Why this hook.** Runs once per creation; not captured by prebuilds (correct — the side effect needs to happen per-codespace).

### Daemon start in `postStartCommand`

```json
{
  "postStartCommand": "docker compose up -d redis"
}
```

**When to use.** Sidecar service that needs to be running. Each start re-establishes.

**Caveat.** Keep this fast; runs on every start.

### Terminal config in `postAttachCommand`

```json
{
  "postAttachCommand": "echo 'Welcome! Run ./dev to start.'"
}
```

**When to use.** Banners, terminal-specific config, very-fast UX touches.

**Caveat.** Runs on EVERY terminal attach — every new terminal in the same codespace. Anything non-trivial is wrong here.

## Prebuild patterns

### Prebuild main branch only

```yaml
# .github/workflows/codespaces-prebuilds.yml
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
    paths: ['.devcontainer/**', 'package-lock.json', 'requirements.txt']
```

**When to use.** Default. Most codespaces start from main or a recent feature branch.

### Prebuild main + most recent N feature branches

**When to use.** Long-lived feature branches; team works on big features for weeks.

**Cost.** More prebuild compute; org budget consideration.

### No prebuild

**When to use.** Codespaces are used rarely; cold-start cost is acceptable.

**Risk.** First-time-user friction.

## Multi-container patterns

### App + DB + Cache

```yaml
# docker-compose.yml
services:
  app:
    image: mcr.microsoft.com/devcontainers/typescript-node:20
    volumes:
      - ../..:/workspaces:cached
    command: sleep infinity
  postgres:
    image: postgres:16
    environment:
      POSTGRES_PASSWORD: dev
  redis:
    image: redis:7
```

**When to use.** App needs DB and cache locally; testing integration; offline development.

**Caveat.** Memory and CPU multiply; consider 4-core+ machine.

### App + Mock external services

```yaml
services:
  app: ...
  mock-payments:
    image: stripe/stripe-mock:latest
    ports: [12111:12111]
  mock-auth:
    image: ghcr.io/dexidp/dex:v2.38.0
```

**When to use.** Need external service behavior in local dev without hitting prod sandboxes.

**Discipline.** Document which mocks model which prod service; keep mocks current.

## Tool-installation patterns

### Features for known tools

```json
{
  "features": {
    "ghcr.io/devcontainers/features/aws-cli:1": {},
    "ghcr.io/devcontainers/features/terraform:1": { "version": "1.7.0" },
    "ghcr.io/devcontainers/features/docker-in-docker:2": {}
  }
}
```

**When to use.** Default for common tools.

**Discipline.** Pin versions where supported. `latest` drifts.

### Dockerfile RUN for project-specific tools

```audit-example -- Documents the curl-pipe-shell installer pattern the auditor flags via DE-1 scanner; reference catalog of anti-pattern signatures, not real install instructions.
FROM mcr.microsoft.com/devcontainers/universal:linux

RUN apt-get update && apt-get install -y \
    libsndfile1-dev \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://internal-registry.example.com/installer.sh | bash
```

**When to use.** Tool not in Features registry; project-specific dependencies.

### Lifecycle install for one-off scripts

```audit-example -- Documents the curl-pipe-shell installer pattern the auditor flags via DE-1 scanner; reference catalog of anti-pattern signatures, not real install instructions.
{
  "onCreateCommand": "curl -fsSL https://example.com/tool/install.sh | bash"
}
```

**When to use.** Tool not in Features; install is small and stable; can run after container exists.

**Risk.** Fetches at create time — non-reproducible if the install script changes.

## Secrets-and-config patterns

### Codespaces Secrets for credentials

```json
{
  "containerEnv": {
    "GITHUB_TOKEN": "${localEnv:GITHUB_TOKEN}",
    "OPENAI_API_KEY": "${localEnv:OPENAI_API_KEY}"
  }
}
```

The secrets are configured in GitHub at the repo / org / user level; the container reads them as env vars.

**When to use.** Default for any sensitive credential.

### Non-secret config in `devcontainer.json`

```json
{
  "containerEnv": {
    "NODE_ENV": "development",
    "DB_HOST": "postgres",
    "API_BASE_URL": "http://localhost:8080"
  }
}
```

**When to use.** Development-only, non-sensitive defaults. The repo can see them.

### Per-user dotfiles repo

A user-owned repo (`~/dotfiles`) is cloned and run automatically by Codespaces.

**When to use.** Personalization (zsh config, editor preferences).

**Discipline.** Encourage; don't require. Team shouldn't depend on every member having a dotfiles repo.

## Monorepo patterns

### Single root `.devcontainer/` for the whole repo

**When to use.** Components share most tooling; one machine class fits all.

### Per-component `.devcontainer/<name>/`

```
.devcontainer/
├── frontend/
│   └── devcontainer.json
├── backend/
│   └── devcontainer.json
└── infra/
    └── devcontainer.json
```

**When to use.** Components have meaningfully different needs (Frontend wants Node; Infra wants Terraform + cloud CLIs).

**Trade-off.** User picks a component when creating the codespace; can't easily switch.

### Workspaces folder per component

```json
{
  "workspaceFolder": "/workspaces/my-repo/backend"
}
```

**When to use.** Designer wants the codespace to open inside a specific component.

## Anti-patterns reviewers should flag

| Anti-pattern | Why it's bad | Typical fix |
|---|---|---|
| `npm install` in `postCreateCommand` | Prebuilds don't capture; cost paid every time | Move to `updateContentCommand` |
| Long-running setup in `postAttachCommand` | Every terminal attach pays the cost | Move to a different hook |
| Tools installed in `postStartCommand` | Re-runs every start | Move to Dockerfile or `updateContent` |
| Build output stored outside `/workspaces` | Lost on rebuild | Configure build output under `/workspaces` |
| Hardcoded token in `devcontainer.json` | In git forever | Codespaces Secrets |
| `.env` checked into repo | Eventual leak | Codespaces Secrets or `.env.example` (no real values) |
| `image: ...:latest` | Drift; non-reproducible | Pin to specific tag |
| Custom Dockerfile to install Node when Features registry has it | Maintenance burden | Use Features |
| Mixing Features and manual install of same tool | Drift between mechanisms | Pick one |
| Multi-container compose for what could be one container | Startup time; memory; complexity | Single container if components fit |
| Port forwarded with `visibility: public` for a dev service | Exposed beyond user | `visibility: private` |
| `forwardPorts` omitted (relying on auto-detection) | User confusion; inconsistent UX | Declare explicitly |
| `machine.cpus: 16` for a single-component TS service | Compute waste | Right-size (2 or 4) |
| Prod credentials in Codespaces Secrets | Codespaces are ephemeral but they're still developer machines | Dev/sandbox credentials only |
| Dotfiles repo required for the project to work | Onboarding friction | Project setup is self-sufficient; dotfiles are personal-extra |
| Hook commands that prompt for input | Hang the codespace creation | Non-interactive commands; defaults from env |
| `apt install` in lifecycle commands instead of Dockerfile | Repeat install on rebuild | Move to Dockerfile |
| Setup that fails silently (`|| true`) | Hides real problems | Fail loudly; document recovery |
| Long monolithic shell script in lifecycle command | Hard to debug | Split into a `.devcontainer/setup.sh` file with proper logging |
| `docker-compose` services without health checks | Race conditions on startup | `healthcheck:` blocks + `depends_on: condition: service_healthy` |
| Volumes used in compose without `:cached` consistency mode (macOS) | Slow file access from host | `:cached` for read-heavy mounts |
| Storing dev DB data in `/var/lib/postgresql` (ephemeral) | Lost on rebuild | Volume mount or accept ephemeral |
| `containerEnv` with non-secret values that should be `remoteEnv` | Container env is process-wide; remote env is per-user | Pick based on scope |

## Decision frames

When the Codespaces Designer faces a choice:

1. **How often will codespaces be created vs. resumed?** Frequent creates → prebuild matters; few creates → cold start is OK.
2. **What's the team size and onboarding cadence?** Many new joiners → invest in first-time UX (prebuild, simple machine class default, README).
3. **What does local dev require?** Single component → simple devcontainer; multi-service → docker-compose; production-parity → 4+-core machine.
4. **What's the secret model?** Personal tokens → user secrets; org tools → org secrets.
5. **What's the org Codespaces policy?** Some orgs restrict base images, machine classes, retention; design within those.

The Designer documents the chosen base mechanism, the lifecycle-hook placement table, the prebuild strategy, and the machine-class default — in the per-layer Design subsection.
