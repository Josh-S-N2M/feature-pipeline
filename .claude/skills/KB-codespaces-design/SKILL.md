---
name: kb-codespaces-design
description: >-
  Design discipline for the Codespaces / Dev Environment layer. Pairs with
  KB-codespaces-platform (the platform half). Covers when to choose image vs.
  Dockerfile vs. docker-compose; when to add a prebuild; lifecycle-hook
  placement (onCreate vs. updateContent vs. postCreate vs. postStart vs.
  postAttach); Features vs. Dockerfile-installed tools; machine sizing
  strategy; org-level policy considerations; and the per-layer designer's
  workflow for producing the Codespaces Design subsection of a Blueprint.
allowed-tools: Read, Grep, Glob
pedagogical_sections:
  - path: references/patterns-and-anti-patterns.md
    justification: "Codespaces design-pattern reference; contains .devcontainer/setup.sh example paths + credential-file anti-pattern examples + curl-pipe-shell installer anti-pattern examples"
---

# KB-codespaces-design — Codespaces Layer Design Discipline

Design discipline for the Codespaces / Dev Environment layer. The per-layer Codespaces Designer (`design-codespaces`) loads this KB during per-layer Design to produce the `### Codespaces Design` subsection of the Blueprint. This is the **design half** of the codespaces skill pair — KB-codespaces-platform is the platform half (devcontainer.json schema, lifecycle hooks, Features list, source-of-truth lookup).

## Contents

- When this KB is loaded
- The layer's responsibility
- Design decisions this layer owns
- Patterns and anti-patterns at a glance
- Interaction with other layers
- Surfacing architectural questions
- When to load each reference file

## When this KB is loaded

This KB is in scope when:

- A feature's PRD or Blueprint declares the **Codespaces / Dev Environment** layer in scope (per `layer-taxonomy.md` in KB-documentation-criteria)
- A per-layer Designer is producing the Codespaces Design subsection of the Blueprint
- The change involves choosing between dev-environment patterns (new project, refactor, prebuilds, machine class), NOT just modifying a `devcontainer.json` with known shape
- Plan Authoring produces tasks that introduce or refactor `.devcontainer/` in a way that requires design judgment

Sub-agents that reference this KB (per Blueprint v4.3.1):

- `design-codespaces` (per-layer Design, when Codespaces / Dev Environment layer is in scope)
- `design-composer` (Design Composition, integrating Codespaces design with cross-cutting concerns)
- `plan-author` (when tasks introduce new dev-environment artifacts)
- `shared-document-reviewer` (Gate 1 Codespaces-specific checks)

Load alongside KB-codespaces-platform for design work; load just the platform KB for schema questions or troubleshooting.

## The layer's responsibility

The Codespaces layer owns the developer's day-one experience. The Designer makes decisions about:

- **Container base.** Prebuilt image, custom Dockerfile, or docker-compose for multi-container dev.
- **Tools installation strategy.** Dev Container Features vs. Dockerfile RUN steps vs. lifecycle commands.
- **Lifecycle hook placement.** Which command runs at which hook (`onCreate` / `updateContent` / `postCreate` / `postStart` / `postAttach`).
- **Prebuild decision.** Whether to pre-snapshot the container (faster startup) or build cold (simpler ops).
- **Persistence boundaries.** What survives rebuild (`/workspaces`) and what doesn't.
- **Machine class and resource allocation.** Default size and which projects need bigger.
- **Secrets and dotfiles.** Codespaces Secrets vs. checked-in config; per-user dotfiles repo.
- **Port forwarding policy.** Which ports are auto-forwarded; visibility (public/private/org).
- **Org-level policy alignment.** Allowed base images, runtime limits, retention.

The Codespaces Designer does NOT own:

- The platform facts (devcontainer.json schema, lifecycle order). Those are in KB-codespaces-platform.
- The application code that runs inside the codespace.
- The CI/CD running outside (separate layer).
- The infrastructure provisioned by IaC (separate layer).

## Design decisions this layer owns

The Codespaces Designer makes (or surfaces) these decisions:

| Decision | Forced if … |
|---|---|
| Base mechanism (image / Dockerfile / docker-compose) | New project or major refactor |
| Image choice (universal, language-specific, custom) | Image-based setup |
| Features vs. Dockerfile RUN | Tools / language runtimes installed |
| Lifecycle hook placement for each setup step | Setup involves more than `apt install` |
| Prebuild (yes/no/on-which-branches) | Cold-start time matters or Codespaces are used frequently |
| Default machine class (2-core, 4-core, 8-core, ...) | Default 2-core is too constrained or too generous |
| Codespaces Secrets vs. dotenv-file vs. external secret manager | Secrets are required |
| Port-forward defaults and visibility | Local services run inside the container |
| Idle timeout override | Default 30 min doesn't fit workflow |
| Retention override | Default 30 days doesn't fit policy |
| Dotfiles support (encourage / discourage) | Team has preferences on personalization |
| Multi-container vs. single-container | App requires DB / cache / queue locally |
| Project's `devcontainer/` location (root or per-component) | Monorepo with distinct components |

Designers do NOT author ADRs (per FR-5). Cross-cutting Codespaces decisions (org-wide base image, prebuild policy) surface as open items.

## Patterns and anti-patterns at a glance

The full discipline lives in `references/principles.md` and `references/patterns-and-anti-patterns.md`. Quick reference:

**Patterns to favor:**

- **Prebuilt image when one fits.** Microsoft's universal image or a language-specific image is faster to start and zero-Dockerfile-maintenance.
- **Features for common tools.** AWS CLI, Terraform, Docker-in-Docker, etc. Features are versioned and well-tested.
- **Dockerfile for what Features don't cover.** Custom apt packages, internal package registry config, project-specific tools.
- **Right hook for right cost.** `updateContentCommand` runs on every content change AND is captured by prebuilds; `postCreateCommand` runs once and is NOT captured by prebuilds.
- **Prebuilds for slow setups.** If `npm install` takes 90 seconds, a prebuild caches that work.
- **Default to 2-core unless the project's build is CPU-bound.** Larger machines cost more; right-size by build profile.
- **Codespaces Secrets for credentials.** Never check tokens or keys into `devcontainer.json` or dotfiles.

**Anti-patterns to flag:**

- **`postCreateCommand` for work that should be in `updateContentCommand`.** Prebuilds don't capture postCreate; users pay the cost every time.
- **Custom Dockerfile when the universal image + Features would work.** Maintenance burden without benefit.
- **Tools installed in `postStartCommand`.** Runs every start; turn into Dockerfile or `updateContentCommand`.
- **Long-running setup in `postAttachCommand`.** This runs on every reconnect; UX cliff.
- **Storing build outputs outside `/workspaces`.** Lost on rebuild.
- **Hard-coding tokens in `devcontainer.json`.** Public-by-default; lost on commit history forever.
- **Multi-container compose for a service the developer doesn't run locally.** Adds startup time; consider mock or remote service.

## Interaction with other layers

```
[Codespaces layer] ──provisions──► Developer's working environment
        │
        ├──can-run──► Backend / Frontend / DB / etc. (locally for dev)
        │
        ├──pulls-from──► IaC (sometimes — Terraform / CDK installed in container)
        │
        └──cooperates-with──► CC (Claude Code in the codespace's terminal)
```

The Codespaces Designer's responsibility:

- **Backend / Frontend / Query / Database** — each layer's local dev needs (DB, queue, mock services) shape the Codespaces design. The Codespaces Designer documents what the dev environment provides; per-layer Designers document what each component expects.
- **IaC** — sometimes IaC tools are installed in the dev container; the Codespaces Designer ensures the right versions are pinned.
- **CC** — Claude Code can run in a Codespace; the dev environment shouldn't fight that integration (e.g., proper terminal config, file permissions).
- **Security** — Codespaces are ephemeral and isolated; this is a design strength. The Designer documents what's intentionally NOT in the container (production secrets, prod DB credentials).

## Surfacing architectural questions

```markdown
## Architectural Questions for Composer

- **Q-CS-1**: Should we adopt prebuilds for our main branch? Cold-start currently averages 4.5 minutes; ~60% of the time is `npm install` and `pip install`. Prebuilds would reduce to ~30 seconds. The choice affects org Codespaces compute budget (prebuilds consume separate quota), branch coverage (which branches get prebuilds), and update cadence (prebuilds re-trigger on lockfile changes). Evidence: team starts ~25 codespaces per week. Options: (a) prebuild main only; (b) prebuild main + most recent N feature branches; (c) status quo. Recommended: (a). Defer to composer.
```

## When to load each reference file

| Load this file | When the task involves |
|---|---|
| `references/principles.md` | Authoring or reviewing a Codespaces Design subsection — covers the foundational principles (lifecycle hook semantics, prebuild boundaries, persistence, machine sizing, secrets) |
| `references/patterns-and-anti-patterns.md` | Choosing between image / Dockerfile / docker-compose; placing setup commands at the right hook; multi-container topology — covers common patterns with when-to-use and the anti-patterns reviewers should flag |
