---
name: kb-codespaces-platform
description: >-
  Platform knowledge for GitHub Codespaces and dev containers — devcontainer.json
  schema, lifecycle hooks (onCreate / updateContent / postCreate / postStart /
  postAttach), Dev Container Features, prebuilds, machine sizing, port
  forwarding, secrets and dotfiles, org-level policies, and CLI/REST API
  recipes. Loaded when a feature touches `.devcontainer/`, `devcontainer.json`,
  or Codespaces configuration. Pairs with KB-codespaces-design which adds the
  design discipline (image vs Dockerfile vs docker-compose; when to use
  prebuilds; lifecycle hook placement). This KB is the PLATFORM half: facts,
  schema, lifecycle order, and lookup chains.
allowed-tools: Read, Grep, Glob, WebFetch
pedagogical_sections:
  - path: references/devcontainer.md
    justification: "DevContainer spec reference; documents .devcontainer/devcontainer.json + .vscode/extensions.json paths typical of Codespaces projects (auditor flags non-existent demo paths)"
  - path: references/workflows.md
    justification: "Codespaces workflow reference; documents .vscode/extensions.json + .devcontainer/devcontainer.json paths + credential-file references for SSH-key forwarding pedagogical examples"
  - path: references/secrets-and-env.md
    justification: "Secrets+env reference catalog documenting credential-file path patterns (cloud SDK credential files, SSH private keys, NETRC, dotenv files) and shell-startup persistence-vector paths the auditor flags via DE-2 scanner. Reference content explaining what to protect, not real credentials."
  - path: references/architecture.md
    justification: "Codespaces architecture reference documenting credential-file path patterns referenced in the persistence/lifecycle discussion; reference catalog used to explain Codespaces' storage model, not real credentials."
  - path: references/cli-and-api.md
    justification: "gh codespace CLI + REST API reference documenting credential-shaped environment variable patterns the auditor flags (DE-2 scanner) as part of pedagogical examples of CLI authentication; not real credentials."
---

# KB-codespaces-platform — GitHub Codespaces Platform Knowledge

Platform knowledge for GitHub Codespaces and dev containers. This is the **platform half** of the codespaces skill pair: it teaches what exists (devcontainer.json schema, lifecycle hooks, Features), the source-of-truth lookup protocol, and the troubleshooting decision trees. The **design half** lives in `KB-codespaces-design` (sister KB) — that one teaches when to choose image vs Dockerfile vs docker-compose, when to add a prebuild, and lifecycle hook placement. Load both for Codespaces-touching design work; load just this one for reviewing or auditing existing setups.

## Contents

- When this KB is loaded
- How this skill loads (in Claude Code)
- Source-of-truth lookup protocol
- Mental model (must understand before changing anything)
- Reference-only contract
- What this skill produces
- Routing table
- Templates
- Operating principles

## When this KB is loaded

This KB is in scope when:

- A feature's PRD or Blueprint declares the **Codespaces / Dev Environment** layer in scope (per `layer-taxonomy.md` in KB-documentation-criteria)
- A per-layer Designer is producing the `codespaces-design.md` subsection of the Blueprint
- Plan Authoring produces tasks that touch `.devcontainer/`, `devcontainer.json`, prebuilds, machine sizing, or org-level Codespaces policy
- `shared-document-reviewer` or `review-architecture-auditor` is auditing artifacts that include Codespaces configuration

Sub-agents that reference this KB (per Blueprint v4.3.1):

- `design-codespaces` (per-layer Design, when Codespaces / Dev Environment layer is in scope)
- `design-composer` (Design Composition, integrating Codespaces design with cross-cutting concerns)
- `plan-author` (when tasks touch devcontainer or prebuild config)
- `shared-document-reviewer` (Gate 1 Codespaces-specific checks)
- `review-architecture-auditor` (CoVe checks on Codespaces-related claims)

For the design discipline overlays (image vs Dockerfile vs docker-compose, when to add a prebuild, lifecycle-hook placement decisions), load `KB-codespaces-design` in parallel.

Optimized for AI consumption. Be terse, imperative, and verify against fresh docs before answering anything non-trivial.

**How this skill loads:**

- **In the main Claude Code session** -- auto-triggers on Codespaces / `devcontainer.json` / `gh codespace` mentions per the description.
- **In a subagent** -- list `kb-codespaces-platform` in the subagent's `skills:` frontmatter field. Subagents do not auto-load skills by description; they only see skills explicitly listed.

**Reference-only contract:** This skill *teaches* and *generates* -- it does not execute. Commands shown (`gh codespace ...`, `curl ...`) are for the user to run, or to copy into a separate execution context. Claude will not run shell commands directly from this skill (`allowed-tools` is scoped to read/search/web only). If a workflow truly needs Claude to run `gh codespace` against the user's account, build a separate action skill with `allowed-tools: Bash(gh codespace *)`.

## What this skill produces

- `devcontainer.json` snippets from validated templates
- `gh codespace` CLI commands and REST API recipes (for the user to execute)
- Lifecycle-hook placement guidance (which command goes in `onCreateCommand` vs `updateContentCommand` vs `postCreateCommand`)
- Troubleshooting decision trees for creation, port-forwarding, and auth failures
- Routed pointers to the relevant reference file when the answer is too detailed for inline

## Source-of-truth lookup protocol

**Treat memory as stale.** For schema fields, API params, feature flags, machine SKUs, region availability, or anything specific:

1. **Primary (always available):** `web_fetch` against `https://docs.github.com/en/codespaces/...` or `https://containers.dev/implementors/json_reference/`. The `.md` URL suffix on `docs.github.com` (when supported) returns clean markdown.
2. **Faster alternative when Context7 MCP is connected:** `Context7:query-docs` with library ID `/websites/github_en`. Check available MCP servers with `/mcp` if unsure whether Context7 is connected. Query with a specific topic (e.g. `"devcontainer.json forwardPorts portsAttributes"`, `"Codespaces REST API list machines for repository"`).
3. **Cite the source** when answering API/schema questions so the user can verify.

Do this even when this skill seems to cover the answer -- this skill describes the shape of things, but the docs hold authoritative current detail.

## Mental model (must understand before changing anything)

- A codespace = **Linux VM** → **Docker container** → mounted **`/workspaces/<repo>`**. The user works inside the container; the VM is invisible.
- The container is defined by **devcontainer.json** (the canonical path is in `.devcontainer/`; alternate locations: root-level `.devcontainer.json`, or `.devcontainer/<name>/devcontainer.json` for multi-config repos).
- The base of the container is one of: a prebuilt **`image`**, a custom **`Dockerfile`** (via `build`), or a **`dockerComposeFile`** with a chosen `service`.
- **Dev Container Features** layer reusable installers (Node, Terraform, AWS CLI, Docker-in-Docker, etc.) on top of any base.
- **Lifecycle hooks** run in a strict order with different scopes -- getting these wrong is the #1 source of "it works the first time but not on rebuild."
- Only **`/workspaces`** persists across container rebuild. Everything outside (except `/tmp` across stop/start) is ephemeral once you rebuild.
- **Idle timeout default 30 min**, **retention default 30 days**. Both org-overridable.
- **Prebuilds** snapshot the container after `onCreateCommand` + `updateContentCommand` -- they do *not* run `postCreateCommand`.
- **Codespaces secrets ≠ Actions secrets** (separate stores). `GITHUB_TOKEN` is auto-provisioned, scoped to the current repo by default.
- Networking: each codespace has its own VM and isolated network. Outbound to internet OK; inbound blocked except via the port-forwarding service. Codespaces cannot reach each other.

## The five questions (ask before any change)

1. **Base** -- image, Dockerfile, or Compose? Which image / which Compose service?
2. **Features** -- which `ghcr.io/devcontainers/features/*` are layered, in what install order?
3. **Lifecycle** -- what runs in `onCreateCommand` / `updateContentCommand` / `postCreateCommand` / `postStartCommand` / `postAttachCommand`, and is anything misplaced (e.g. expensive setup in `postCreateCommand` that should be in `onCreateCommand` so prebuilds capture it)?
4. **Ports** -- what's in `forwardPorts` and `portsAttributes`? Any with `visibility: public`?
5. **Secrets/env** -- what env vars are read? Are they Codespaces secrets, `containerEnv`, `remoteEnv`, dotfiles, or worse, hardcoded?

## Routing -- pick the reference for the task

| Task | Reference |
|---|---|
| Understand VM/container/lifecycle/persistence/timeouts | `references/architecture.md` |
| Read or write `devcontainer.json` (any field, any hook) | `references/devcontainer.md` |
| Pick or compose Dev Container Features | `references/features.md` |
| Configure or troubleshoot prebuilds | `references/prebuilds.md` |
| Secrets, env vars, dotfiles, private registries, GITHUB_TOKEN | `references/secrets-and-env.md` |
| `gh codespace` CLI or REST API | `references/cli-and-api.md` |
| Security model, isolation, hardening | `references/security.md` |
| Org policies, billing, machine/image policies, access | `references/org-management.md` |
| Diagnose creation/runtime/port/auth/GPG failures | `references/troubleshooting.md` |
| **Operational playbooks** -- review, create, refactor, remove, migrate, optimize | `references/workflows.md` |

For any "create new" or "refactor" task, also start from `assets/templates/` rather than synthesizing from scratch.

**Heavy-read tasks:** for a full audit that pulls in 5+ reference files, consider invoking with `context: fork` so the read noise stays in a subagent and only the summary returns to the main session. For iterative work where you want the loaded context retained for follow-ups, invoke normally.

## Inline cheat sheet (the 80% case)

### Minimal devcontainer.json skeleton

```jsonc
{
  "name": "my-project",
  "image": "mcr.microsoft.com/devcontainers/typescript-node:1-22-bookworm",

  "features": {
    "ghcr.io/devcontainers/features/github-cli:1": {},
    "ghcr.io/devcontainers/features/common-utils:2": {}
  },

  "forwardPorts": [3000],
  "portsAttributes": {
    "3000": { "label": "App", "onAutoForward": "notify" }
  },

  "postCreateCommand": "npm ci",

  "customizations": {
    "vscode": {
      "extensions": ["dbaeumer.vscode-eslint", "esbenp.prettier-vscode"],
      "settings": { "editor.formatOnSave": true }
    }
  },

  "remoteUser": "node"
}
```

### Lifecycle hook order (critical)

| # | Hook | Where it runs | Runs in prebuild? | Use for |
|---|---|---|---|---|
| 1 | `initializeCommand` | **Local host** | n/a | Pre-flight checks on user machine |
| 2 | `onCreateCommand` | Container, once at create | **Yes** | Heavy setup that should be cached in prebuild |
| 3 | `updateContentCommand` | Container, on creation + content updates | **Yes** | Repo-content-dependent setup (`npm ci`) |
| 4 | `postCreateCommand` | Container, once at create | **No** | Setup needing secrets / Docker-in-Docker / things you don't want in the prebuild snapshot |
| 5 | `postStartCommand` | Container, every start | n/a | Restart background services |
| 6 | `postAttachCommand` | Container, every attach | n/a | Greet user, open files, start dev server |

Each hook accepts a string, array (`["a","b"]` = exec), or object (`{"server":"npm start","db":"docker compose up db"}` = parallel).

### `gh` CLI essentials

```bash
gh codespace create -r OWNER/REPO -b BRANCH -m standardLinux32gb
gh codespace list
gh codespace ssh -c CODESPACE_NAME
gh codespace ssh -c CODESPACE_NAME -- "command-to-run"
gh codespace code -c CODESPACE_NAME            # open in VS Code desktop
gh codespace ports forward 3000:3000 -c NAME
gh codespace ports visibility 3000:public -c NAME
gh codespace cp -r src.txt remote:/workspaces/repo/   # local→remote
gh codespace stop -c NAME
gh codespace rebuild -c NAME [--full]
gh codespace logs -c NAME
gh codespace delete -c NAME
```

### Persistence rule (memorize)

- `/workspaces/...` → persists through stop/start **and** rebuild. **Put anything you can't recreate here.**
- `/tmp` → persists through stop/start, lost on rebuild.
- Everything else → persists through stop/start, lost on rebuild. **Treat home dir as ephemeral.** Symlink config dirs into `/workspaces/.devcontainer/<name>/` from `postCreateCommand` if needed.

## Hard rules (non-negotiable)

1. **Never put secrets in `devcontainer.json` or commit them.** Use Codespaces user/repo/org secrets -- they appear as env vars in the container.
2. **Never put Docker-in-Docker pulls in `onCreateCommand`** -- DinD isn't available there. Use `postCreateCommand`.
3. **Never assume home directory survives a rebuild.** If you need persistence, write into `/workspaces`.
4. **Never mark a port `public` without explicit user consent** -- anyone with the URL can hit it.
5. **Never run as root unless required.** Default to `remoteUser: "vscode"` (or the image's non-root user); use `containerUser` only when the whole container needs it.
6. **Never put expensive content-independent setup in `postCreateCommand`** -- move it to `onCreateCommand` so prebuilds cache it.
7. **Never trust an unfamiliar repo's devcontainer** -- it can run arbitrary code on creation. Review before opening.

## Workflow protocols (high-level)

For any of these, open `references/workflows.md` for the full checklist:

- **Reviewing existing setup** → §Audit checklist (image freshness, hook placement, prebuild eligibility, secrets hygiene, port visibility, machine-size fit)
- **Creating new** → §Create decision tree → copy from `assets/templates/`
- **Updating/refactoring** → §Refactor patterns (image → Dockerfile, adding feature, adding Compose service, adopting prebuild)
- **Removing/deprecating** → §Remove checklist (`.devcontainer/` files, prebuild config, org config, badges, deep links)
- **Migrating local → Codespaces** → §Migrate
- **Optimizing startup time** → §Optimize

## Templates available

- `assets/templates/typescript-single.devcontainer.json` -- single-repo TS/Node app
- `assets/templates/typescript-monorepo/devcontainer.json` -- pnpm/turbo-style monorepo
- `assets/templates/terraform-iac.devcontainer.json` -- IaC environment (Terraform + cloud CLIs)
- `assets/templates/dockerfile-based/devcontainer.json` -- when the default image isn't enough
- [`assets/templates/dockerfile-based/Dockerfile`](assets/templates/dockerfile-based/Dockerfile) -- companion Dockerfile for the dockerfile-based template
- `assets/templates/docker-compose/devcontainer.json` -- multi-service (e.g. app + postgres + redis)
- `assets/templates/docker-compose/docker-compose.yml` -- companion compose file for the multi-service template
- [`assets/templates/docker-compose/Dockerfile`](assets/templates/docker-compose/Dockerfile) -- companion Dockerfile for the multi-service template

When using `dockerfile-based/` or `docker-compose/`, copy the entire directory -- the `devcontainer.json` references its sibling files by relative path, so they must travel together.

Always copy the closest template and adapt; do not synthesize a fresh `devcontainer.json` from memory.

## Where to install this skill

- **User scope (`~/.claude/skills/github-codespaces/`)** -- recommended default. Available in every Claude Code session, no per-repo install. Use this when you work on Codespaces across many repos.
- **Project scope (`.claude/skills/github-codespaces/`)** -- when one repo's Codespaces setup is the primary reason to use this skill, and the team should share it. Commit alongside `.devcontainer/`.

## When this skill might be insufficient

If asked about behavior introduced after the skill was last updated, or a specific endpoint/feature/machine type that this skill doesn't enumerate: **`web_fetch` `docs.github.com/en/codespaces/...` first** (always available), or use `Context7:query-docs` with `/websites/github_en` if Context7 MCP is connected. Do not guess.
