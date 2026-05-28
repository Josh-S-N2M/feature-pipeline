# Layer Taxonomy

The engineering layers used by both the PRD's and the Blueprint's `### Layer Scope` section.

> **Canonical source.** The machine-readable enumeration lives in [`.claude/canonical/engineering-domain-layers.yaml`](../../../canonical/engineering-domain-layers.yaml) (loaded by `auditing-shared/scripts/canonical.py`; per ADR-0069). **That YAML is the single source of truth for the layer list, slugs, names, descriptions, and KB pairings.** This markdown file is its *prose companion* — it carries the discipline (why one taxonomy, per-layer disposition, boundary cases, cross-cutting notes) that does not fit cleanly in YAML. If the two ever disagree on the layer *list*, the YAML wins and this file is updated. The CANON-2 document-drift audit (`audit_canonical_doc_drift.py`) flags any other document that hard-codes the layer list without referencing the canonical source.

## Contents

- Why a single taxonomy
- The 9 layers
- Layer Scope checkboxes (the literal block to use in templates)
- Per-layer disposition: what "out of scope" actually means at each layer
- Cross-cutting layers
- Boundary cases and how to decide

## Why a single taxonomy

Earlier templates (v4.2 and prior) had the PRD's Layer Scope use 9 product-surface labels (e.g., "Frontend / End-User Experience," "Backend Behavior," "Data as Product") and the Blueprint's Layer Scope use 9 engineering labels ("Frontend," "Backend," "Database"). The two lists didn't map cleanly, and authors had to maintain a translation in their head.

In v4.3, both PRD and Blueprint adopt the engineering labels. The reasoning:

- **Engineering labels are concrete.** "Backend" names a layer in the codebase; "Backend Behavior" is a vague category that includes latency, freshness, jobs, notifications, and several other dimensions.
- **Product surface is a different question.** Whose experience matters — end users, admins, partner APIs, dev contributors — is a stakeholder question, not a layer question. The PRD's Stakeholders, User Stories, Non-Functional Requirements, and Product Policy Decisions sections answer that.
- **No translation table.** The Blueprint's `### Layer Scope` carries the PRD's Layer Scope verbatim. If the PRD said "Backend is in scope," the Blueprint says the same and authors the Backend Design subsection.

## The 9 layers

Order matters — this is the order used in the Layer Scope checkbox block and in the Blueprint's `## Design` subsections.

### 1. Claude Code / Project Filesystem

CLAUDE.md files (root and scoped), slash commands at `.claude/commands/<name>.md`, hooks at `.claude/hooks/`, skills at `.claude/skills/<name>/SKILL.md`, MCP configuration at `.mcp.json`, agent definitions at `.claude/agents/<name>.md`, and project-wide filesystem conventions (naming, layout, deny lists).

**In scope when:** the feature introduces or modifies any of the above; the feature relies on agent-driven workflows that need new project conventions; the feature requires changes to how Claude Code or other agents navigate the repo.

**Examples in scope:** adding a slash command that automates the deploy gate; introducing a new sub-agent for a specialized review; adding a hook that blocks commits to `main`.

**Examples out of scope:** features that don't touch agent workflows; pure runtime features where Claude Code is just the editor.

### 2. Frontend

UI components (React/Vue/Svelte/etc.), client state management, client routing, client-side styling, component-level data fetching.

**In scope when:** the feature changes what the user sees in a browser or mobile app; the feature changes client routes; the feature changes client state lifecycle.

### 3. Backend

Services, domain logic, background jobs, schedulers, message handlers, business rules. Excludes the API surface (a separate layer) and the data-access layer (a separate layer).

**In scope when:** the feature changes service behavior; the feature adds a new domain concept; the feature introduces a job, scheduler, or message handler.

### 4. API

HTTP/GraphQL/RPC endpoint contracts, request/response schemas, OpenAPI/SDL definitions, versioning policy, content negotiation, error envelopes. This layer is the **contract**, not the implementation — Backend implements it.

**In scope when:** the feature adds, removes, or changes an endpoint's contract; the feature changes versioning, deprecation, or compatibility policy; the feature changes error contracts visible to clients.

### 5. Query / Data Access

ORM models, repositories, query builders, caches in front of data stores, transaction boundaries, connection pooling. This is the layer between Backend domain code and Database storage.

**In scope when:** the feature changes how data is read or written; the feature introduces a new repository or cache; the feature changes transaction or isolation requirements.

### 6. Database

Schema definitions, migrations, indexes, constraints, foreign keys, seed data, materialized views, stored procedures, partitioning, sharding. Pure persistence layer.

**In scope when:** the feature changes the schema; the feature adds an index; the feature requires a data migration.

### 7. CI/CD (GitHub Actions)

GitHub Actions workflows (`.github/workflows/`), reusable actions, composite actions, environments, secrets, matrix builds, deployment gates, status checks.

**In scope when:** the feature changes how the project builds, tests, or deploys; the feature adds an environment; the feature changes deployment gating.

### 8. Infrastructure as Code

Terraform/Pulumi/CDK/CloudFormation modules, state files, providers, backend configuration, workspace management, drift detection.

**In scope when:** the feature provisions new infrastructure; the feature changes existing module structure; the feature changes the state backend.

### 9. Dev Environment (Codespaces / Devcontainer)

`devcontainer.json`, container features, prebuild configuration, port forwarding, lifecycle scripts (`postCreate`, `postStart`, `postAttach`, `onCreate`), dotfile integration, and any other contributor-onboarding automation.

**In scope when:** the feature changes the dev environment; the feature adds a new tool that contributors need; the feature changes the prebuild or container image.

## Layer Scope checkbox block (verbatim)

This is the exact block to use in the PRD's `### Layer Scope` and the Blueprint's `### Layer Scope`. Both use it identically. **It is derived from [`engineering-domain-layers.yaml`](../../../canonical/engineering-domain-layers.yaml)** — the `canonical.layers.CHECKBOX_BLOCK` accessor regenerates it from canonical data. If you edit the YAML, regenerate this block; do not hand-edit it independently.

```markdown
### Layer Scope

Declare which layers this feature touches. Sections under Design, Security, Test Boundaries, and Verification corresponding to unchecked layers may be marked `N/A — out of scope` without further elaboration.

- [ ] **Claude Code / Project Filesystem** — CLAUDE.md, slash commands, hooks, skills, MCP configuration, project conventions
- [ ] **Frontend** — UI components, client state, routing, styling
- [ ] **Backend** — services, domain logic, background jobs, schedulers
- [ ] **API** — HTTP/GraphQL/RPC endpoints, contracts, versioning
- [ ] **Query / Data Access** — ORM models, repositories, query layer, caching
- [ ] **Database** — schema, migrations, indexes, constraints, seed data
- [ ] **CI/CD (GitHub Actions)** — workflows, jobs, reusable actions, environments, secrets
- [ ] **Infrastructure as Code** — Terraform/Pulumi/CDK/CloudFormation modules, state, providers
- [ ] **Dev Environment (Codespaces / Devcontainer)** — devcontainer.json, prebuilds, ports, lifecycle scripts
```

## What "out of scope" means at each layer

A layer marked out of scope means: this feature does not require changes at that layer. The corresponding Blueprint Design subsection (`### <Layer> Design`) is marked `N/A — out of scope`. Per-layer designers for unchecked layers are NOT invoked during per-layer Design.

What out-of-scope does NOT mean:

- It does not mean the layer doesn't exist in the project.
- It does not mean the feature has no effect at that layer — only that any effect is incidental and does not require designer attention. (E.g., a Frontend-only color change might pass through a CDN — Infrastructure as Code is not in scope.)
- It does not mean reviewer checks at that layer are skipped — `shared-document-reviewer` still verifies the `N/A — out of scope` marker is present where expected.

If an "out-of-scope" layer turns out to need changes (discovered during Discovery Research or Architecture Audit), the orchestrator surfaces this to user; user re-checks the layer in Layer Scope; the corresponding designer runs. This is treated as a Layer Scope amendment, not an undeclared expansion.

## Cross-cutting layers

Some feature concerns span multiple layers. Examples:

- **Observability** — instrumentation usually touches Backend (emit), Query (emit), API (emit), CI/CD (deploy collectors), IaC (provision sinks). Each affected layer is checked.
- **Authentication** — touches Frontend (login UI), API (auth headers), Backend (session/token handling), Database (user table).
- **Background jobs** — touches Backend (handler), Query/Database (job tracking table), CI/CD (worker deployment).

The PRD's Layer Scope checks ALL touched layers. The Blueprint's per-layer Design subsections each cover that layer's slice of the cross-cutting concern.

## Boundary cases

### Frontend vs API

A backend-for-frontend (BFF) layer is API + Backend. Both checked. The API subsection covers the BFF contract; the Backend subsection covers its implementation.

### Query vs Database

The line: SQL strings, query builders, repositories, ORM models → Query / Data Access. Schema, migrations, indexes, constraints → Database. A change to "add an index to speed up a slow query" touches both: Query for the affected repository method (if its expected performance changes) and Database for the index migration.

### CI/CD vs IaC

The line: actions, workflows, deployment gates → CI/CD. Provisioning of the infrastructure those deployments target → IaC. A change to "deploy to a new region" touches both: IaC to provision in the new region, CI/CD to add the region to the deployment matrix.

### Claude Code / Project Filesystem vs everything else

The Claude Code / Project Filesystem layer is checked only when the feature INTRODUCES a Claude Code construct (slash command, hook, skill, agent) or new conventions. Just modifying source files inside Claude Code's purview does NOT count — that's the underlying layer (Frontend, Backend, etc.). Examples:

- Adding `.claude/commands/deploy.md` → Claude Code / Project Filesystem IS checked.
- Refactoring a service Claude Code happens to edit → Backend only; Claude Code / Project Filesystem NOT checked.

### Codespaces vs CI/CD

Codespaces is the contributor's dev environment. CI/CD is the project's automated build/test/deploy. They share container concepts but serve different purposes. A new tool needed both for local dev AND in CI checks BOTH layers.

## Discipline: never invent a 10th layer

If a feature seems to touch something outside these 9, the disposition is one of:

1. It's actually one of the 9, just expressed unfamiliarly. (E.g., "Notifications" → typically Backend + API, sometimes Frontend.)
2. It's cross-cutting across two or more of the 9. Check all that apply.
3. It belongs in Stakeholders / User Stories / NFRs / Product Policy in the PRD, not in Layer Scope.

If after honest analysis the feature still seems to need a 10th layer, surface to user as a structural change before authoring. Do NOT silently add a new layer to the checkbox block.

## Canonical-source discipline

The **machine-readable single source of truth** is [`.claude/canonical/engineering-domain-layers.yaml`](../../../canonical/engineering-domain-layers.yaml). This markdown file is its prose companion. Every document the pipeline produces (PRD template, Blueprint template, PRD authoring discipline, design-composer agent, plan-author agent, reviewers) reaches back to the YAML (or to this companion, which points at the YAML) when it needs the layer list — none of them duplicate the enumeration in their own prose.

If you are extending the taxonomy (adding a layer, renaming one, retiring one):

1. Edit **`engineering-domain-layers.yaml`** first and bump its `version`.
2. Update this prose companion to match (descriptions, boundary cases).
3. Re-run the project audit (`python3 .claude/skills/auditing-cc-configs/scripts/audit_project.py .`). The **CANON-2** document-drift check (`audit_canonical_doc_drift.py`) surfaces any document that hard-codes the layer list without a reference back to canonical; fix those in the same change.
4. The checkbox block below and the `canonical.layers.CHECKBOX_BLOCK` accessor are both derived from the YAML — keep this block in sync, or regenerate it from the accessor.

Adding a layer is a substantive architectural decision and warrants an ADR before the edit lands in the YAML.
