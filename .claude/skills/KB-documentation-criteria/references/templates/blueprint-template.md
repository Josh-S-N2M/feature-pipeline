---
id: BP-<feature-slug>
version: 1.0.0
status: draft
feature_slug: <feature-slug>
derived_from: <prd-path>
predecessor: <previous-blueprint-version-path>   # only when version > 1.0.0
codebase_analysis: <codebase-analysis.json-path>
adrs_referenced: []
adrs_authored: []
generated: <ISO-8601-UTC>
generated_by: design-composer
---

# [Feature Name] Design Document

## Contents

Section completion checklist — each box must be checked (including `N/A — out of scope` rows) before this document leaves draft. The reviewer's Gate 0 check uses this list as the structural-presence anchor.

- [ ] Overview
- [ ] Design Summary (Meta)
- [ ] Background and Context
- [ ] Acceptance Criteria (AC) - EARS Format
- [ ] Existing Codebase Analysis
- [ ] Design
- [ ] Implementation Plan
- [ ] Security Considerations
- [ ] Test Boundaries
- [ ] Verification Strategy
- [ ] Future Extensibility
- [ ] Alternative Solutions
- [ ] Risks and Mitigation
- [ ] References
- [ ] Update History

**Note to authoring sub-agent:** update this list if you add or remove top-level (H2) sections from the document. Do NOT remove the `## Contents` heading — it is required for Gate 0 structural review. Mark each box `[x]` when the corresponding section is complete (or contains an explicit `N/A — out of scope` marker for layers not in scope).

## Overview

[Explain the purpose and overview of this feature in 2-3 sentences]

### Layer Scope

Declare which layers this feature touches. Sections under Design, Security, Test Boundaries, and Verification corresponding to unchecked layers may be marked `N/A — out of scope` without further elaboration.

**Canonical source.** The layer enumeration is maintained in [`.claude/canonical/engineering-domain-layers.yaml`](../../../../canonical/engineering-domain-layers.yaml) (machine source) with the verbatim checkbox block mirrored in its prose companion [`../layer-taxonomy.md`](../layer-taxonomy.md). The Blueprint's Layer Scope MUST carry the PRD's Layer Scope verbatim (per layer-taxonomy.md §"Why a single taxonomy"). When filling in this template, **copy the checkbox block from the PRD this Blueprint accompanies** — both the PRD and this Blueprint source the same canonical list. This template intentionally omits the inline list to force the author to consult the canonical source or the paired PRD.

<!-- Paste the Layer Scope checkbox block from the paired PRD here (or from layer-taxonomy.md if no PRD is paired). Carry the PRD's tick state forward verbatim. -->

### Referenced Specifications

- **UI Spec** (when frontend in scope): [docs/ui-spec/xxx-ui-spec.md]
- **API Spec** (when API in scope): [docs/api/xxx-openapi.yaml | docs/api/xxx-graphql.sdl]
- **Data Model Spec** (when DB in scope): [docs/data/xxx-erd.md]
- **Runbook / Operational Spec** (when infra/CI in scope): [docs/ops/xxx-runbook.md]

## Design Summary (Meta)

```yaml
design_type: "new_feature|extension|refactoring|infra_change|tooling_change"
risk_level: "low|medium|high"
complexity_level: "low|medium|high"
complexity_rationale: "[Required if medium/high: (1) which requirements/ACs necessitate this complexity, (2) which constraints/risks it addresses]"
layers_touched:
  - "[layer name from Layer Scope]"
blast_radius:
  runtime: "[which services/users are affected if this fails]"
  build_time: "[which pipelines/devs are affected if this breaks the build]"
main_constraints:
  - "[constraint 1]"
  - "[constraint 2]"
biggest_risks:
  - "[risk 1]"
  - "[risk 2]"
unknowns:
  - "[uncertainty 1]"
  - "[uncertainty 2]"
```

## Background and Context

### Prerequisite ADRs

- [ADR File Name]: [Related decision items]
- Reference common technical ADRs when applicable

### External Resources Used

Lists each external resource this feature depends on with its feature-specific identifier. Resources not used by this feature are omitted from the table.

| Resource (project-tier label) | Feature-specific identifier | Notes |
|-------------------------------|-----------------------------|-------|
| [Resource label] | [e.g., endpoint path, schema source, IaC module, GitHub Action ref, Docker image] | [feature-specific scope] |

### Agreement Checklist

#### Scope
- [ ] [Features/components to change]
- [ ] [Features to add]

#### Non-Scope (Explicitly not changing)
- [ ] [Features/components not to change]
- [ ] [Existing logic, schemas, or pipelines to preserve]

#### Constraints
- [ ] Parallel operation: [Yes/No]
- [ ] Backward compatibility: [Required/Not required] — applies to: [API consumers / DB readers / CI consumers / IaC state]
- [ ] Performance measurement: [Required/Not required]
- [ ] Zero-downtime deployment: [Required/Not required]
- [ ] Forward-compatible migration: [Required/Not required] — i.e., old code can run against new schema

#### Applicable Standards
- [ ] [Standard/convention] `[explicit]` - Source: [config / rule file / documentation path]
- [ ] [Observed pattern] `[implicit]` - Evidence: [file paths] - Confirmed: [Yes/No]

#### Quality Assurance Mechanisms

How quality is enforced in the change area. Each item is either adopted (will be enforced during implementation) or noted (observed but not adopted, with reason).

- [ ] [Tool/check name] — Enforces: [what] — Config: [path] — Covers: [file paths/patterns, or "project-wide"] — Status: `adopted` / `noted (reason)`
- [ ] [Domain-specific constraint] — Enforces: [what] — Source: [path] — Covers: [file paths/patterns, or "project-wide"] — Status: `adopted` / `noted (reason)`

### Problem to Solve

[Specific problems or challenges this feature aims to address]

### Current Challenges

[Current system issues or limitations]

### Requirements

#### Functional Requirements

- [List mandatory functional requirements]

#### Non-Functional Requirements

- **Performance**: [Response time, throughput, query latency, build time]
- **Scalability**: [Requirements for handling increased load]
- **Reliability**: [Error rate, availability, recovery time objectives]
- **Maintainability**: [Code readability, schema evolvability, IaC modularity]
- **Operability**: [Observability, debuggability, rollback safety]

## Acceptance Criteria (AC) - EARS Format

Each AC is written in EARS (Easy Approach to Requirements Syntax) format. Group ACs by layer when the feature spans multiple layers so coverage gaps are visible.

**EARS Keywords**:
| Keyword | Usage | Test Type |
|---------|-------|-----------|
| **When** | Event-triggered behavior | Event-driven test |
| **While** | State-dependent behavior | State condition test |
| **If-then** | Conditional behavior | Branch coverage test |
| (none) | Ubiquitous behavior | Basic functionality test |

**Format**: `[Keyword] <trigger/condition>, the system shall <expected behavior>`

### Functional ACs

#### [Functional Requirement 1] — Layer: [frontend / backend / api / ...]

- [ ] **When** user clicks login button with valid credentials, the system shall authenticate and redirect to dashboard
- [ ] **If** credentials are invalid, **then** the system shall display error message "Invalid credentials"
- [ ] **While** user is logged in, the system shall maintain the session for configured timeout period

#### [Functional Requirement 2] — Layer: [...]

- [ ] The system shall display data list with pagination of 10 items per page
- [ ] **When** input is entered in search field, the system shall apply real-time filtering

### Cross-Layer / Operational ACs

- [ ] **When** the migration runs on a production-sized dataset, the system shall complete within [N minutes] and produce zero data loss
- [ ] **When** the deploy workflow runs on `main`, the system shall promote the image to staging and run smoke tests before promoting to production
- [ ] **If** the Terraform plan shows destructive changes to stateful resources, **then** the system shall block apply pending manual approval
- [ ] **When** a Codespace is created from this branch, the system shall provide a working dev environment within [N minutes] with all tools installed

## Existing Codebase Analysis

### Implementation Path Mapping
| Layer | Type | Path | Description |
|-------|------|------|-------------|
| Frontend | Existing | `src/[actual-path]` | [Current implementation] |
| Frontend | New | `src/[planned-path]` | [Planned new creation] |
| Backend | Existing | `services/[...]` | [...] |
| API | Existing | `[openapi.yaml / routes/...]` | [...] |
| Query | Existing | `[repository / dao path]` | [...] |
| Database | Existing | `[migrations path]` | [...] |
| CI/CD | Existing | `.github/workflows/[...]` | [...] |
| IaC | Existing | `infra/[...]` | [...] |
| Codespaces | Existing | `.devcontainer/[...]` | [...] |

### Integration Points (Include even for new implementations)
- **Integration Target**: [What to connect with]
- **Invocation Method**: [How it will be invoked — direct call / event / scheduled / webhook / workflow_dispatch]

### Code Inspection Evidence

| File/Function | Relevance |
|---------------|-----------|
| [path:function] | [similar functionality / integration point / pattern reference] |

### Fact Disposition Table

One row per codebase analysis `focusAreas` entry. This table is the single binding between existing-behavior facts and the design — other sections that describe existing behavior reference the row by Focus Area name.

| Fact ID | Focus Area | Disposition | Rationale | Evidence |
|---------|------------|-------------|-----------|----------|
| [fact_id from focusAreas] | [area name from focusAreas] | preserve / transform / remove / out-of-scope | [for transform: state new outcome; for remove: state reason; for out-of-scope: state which scope boundary excludes it; for preserve: brief confirmation] | [evidence value carried verbatim from focusAreas] |

## Design

### Change Impact Map

```yaml
Change Target: [Component/feature to change]
Direct Impact:
  frontend: [files/components requiring direct changes]
  backend: [services/handlers requiring direct changes]
  api: [endpoints/contracts changing]
  query: [repositories/queries changing]
  database: [tables/columns/indexes changing]
  cicd: [workflows/jobs changing]
  iac: [modules/resources changing]
  codespaces: [devcontainer/prebuild changes]
Indirect Impact:
  - [Data format changes that ripple to consumers]
  - [Build/deploy time changes]
  - [Cache invalidation needs]
No Ripple Effect:
  - [Explicitly specify unaffected features/services/pipelines]
```

### Interface Change Matrix

| Existing | New | Conversion Required | Compatibility Method |
|----------|-----|--------------------|--------------------|
| [Function/method/endpoint/table/column/workflow] | [New form] | [Yes/No] | [Approach: adapter, wrapper, deprecation header, expand-contract migration, etc.] |

### Architecture Overview

[How this feature is positioned within the overall system. Include a diagram or pseudo-architecture when more than two layers interact.]

### Data Flow

```
[Express data flow using diagrams or pseudo-code. Identify the boundary between client, API, service, query layer, and storage.]
```

### Integration Points List

| Integration Point | Location | Old Implementation | New Implementation | Switching Method | Verification Method |
|-------------------|----------|-------------------|-------------------|------------------|-------------------|
| Integration Point 1 | [Class/Function/Endpoint] | [Existing] | [New] | [DI/Factory/feature flag/route version] | [How to verify this switching works] |

### Main Components

#### Component 1

- **Responsibility**: [Scope of responsibility]
- **Interface**: [APIs and contract definitions provided]
- **Dependencies**: [Relationships with other components]

#### Component 2

- **Responsibility**: [Scope]
- **Interface**: [Contract]
- **Dependencies**: [Relationships]

### Data Representation Decision (When Introducing New Structures)

| Criterion | Assessment | Reason |
|-----------|-----------|--------|
| Semantic Fit | [Yes/No] | [Does existing structure's meaning align?] |
| Responsibility Fit | [Yes/No] | [Same bounded context?] |
| Lifecycle Fit | [Yes/No] | [Same creation/mutation/deletion timing?] |
| Boundary/Interop Cost | [Low/Medium/High] | [Cost of sharing across boundaries?] |

**Decision**: [reuse / extend / new] — [rationale in 1-2 sentences]

### Contract Definitions

```
// Record major contract/interface definitions here
```

### Data Contract

#### Component 1

```yaml
Input:
  Type: [Data shape, contract, or schema]
  Preconditions: [Required items, format constraints]
  Validation: [Validation method]

Output:
  Type: [Data shape, contract, or schema]
  Guarantees: [Conditions that must always be met]
  On Error: [Exception/null/default value]

Invariants:
  - [Conditions that remain unchanged before and after processing]
```

### Field Propagation Map (When Fields Cross Boundaries)

| Field | Boundary | Status | Detail |
|-------|----------|--------|--------|
| [field name] | [Component A → B, or DB → API → Frontend] | preserved / transformed / dropped | [logic or reason] |

### State Transitions and Invariants (When Applicable)

```yaml
State Definition:
  - Initial State: [Initial values and conditions]
  - Possible States: [List of states]

State Transitions:
  Current State → Event → Next State

System Invariants:
  - [Conditions that hold in any state]
```

---

### Claude Code / Project Filesystem Design

Mark as `N/A — out of scope` if Claude Code / Project Filesystem not in Layer Scope.

This subsection covers how the feature affects the Claude Code / Project Filesystem layer (per the 9-layer taxonomy in `../layer-taxonomy.md`): CLAUDE.md files, slash commands, hooks, skills, MCP configuration, sub-agent definitions, and project-wide filesystem conventions.

#### Conventions Touched (snapshot)

| Path | Purpose | Change Type |
|---|---|---|
| [e.g., `apps/web/`] | [Frontend application] | new / modified / unchanged but conventions added |
| [e.g., `services/api/`] | [Backend service] | new / modified / unchanged but conventions added |
| [e.g., `infra/terraform/`] | [IaC modules] | new / modified / unchanged but conventions added |
| [e.g., `.github/workflows/`] | [CI pipelines] | new / modified / unchanged but conventions added |
| [e.g., `.devcontainer/`] | [Codespaces config] | new / modified / unchanged but conventions added |

#### CLAUDE.md Updates

| File | Change | Rationale |
|---|---|---|
| [`CLAUDE.md` at repo root] | [Add/modify/remove a directive] | [Why agents need this context] |
| [`<subdir>/CLAUDE.md`] | [Scoped conventions for this area] | [Local-only rules] |

#### Slash Commands

| Command Path | Trigger | Purpose | Notes |
|---|---|---|---|
| `.claude/commands/[name].md` | `/[name]` | [What it automates] | [Args, gotchas, prerequisites] |

#### Hooks

| Hook Event | Script | Behavior | Failure Mode |
|---|---|---|---|
| [PreToolUse / PostToolUse / Stop / etc.] | [path to hook script] | [what it does] | [blocking / non-blocking, surfaced error] |

#### Skills

| Skill | Location | When Triggered | What It Provides |
|---|---|---|---|
| [skill name] | [`.claude/skills/<name>/SKILL.md`] | [trigger description] | [capabilities, file outputs] |

#### Sub-Agents

| Sub-Agent | Location | Phase | What It Does |
|---|---|---|---|
| [agent name] | [`.claude/agents/<name>.md`] | [phase name from canonical taxonomy] | [responsibility summary] |

#### MCP Servers

| Server | Configuration | Tools Exposed | Auth Method |
|---|---|---|---|
| [server name] | [`.mcp.json` entry or config path] | [tool names] | [token / oauth / none] |

#### File Naming & Layout Conventions Introduced

- [Convention 1]: [Rule] — Applies to: [paths/patterns] — Enforcement: [linter / convention only / hook]
- [Convention 2]: [Rule] — Applies to: [paths/patterns] — Enforcement: [linter / convention only / hook]

#### Project Filesystem Error State Design

How does the feature behave when expected Claude Code constructs are missing or malformed?

- [Missing CLAUDE.md: how do agents discover the conventions otherwise?]
- [Hook script returns non-zero: how does the orchestrator surface to user?]
- [Skill frontmatter invalid: per ADR-0010, what's the load-time guarantee?]

### Frontend Design

Mark as `N/A — out of scope` if Frontend not in Layer Scope.

#### UI Error State Design

| Component / Screen | Loading | Empty | Error | Partial |
|-------------------|---------|-------|-------|---------|
| [Component name] | [Skeleton / spinner] | [Empty state + CTA] | [Error message + Retry] | [Cached display + Banner] |

#### Client State Design

| State Category | State | Management Method | Sync Strategy |
|---------------|-------|-------------------|---------------|
| Server state | [Fetched data] | [Cache library / custom hook] | [Polling / WebSocket / SSE / manual refresh] |
| Local UI state | [Modal open, tab selection] | [useState / useReducer / store] | - |
| Temporary state | [Form input, draft] | [useState / form library] | [Auto-save / manual save] |
| URL state | [Filters, pagination] | [Router params / search params] | [Bookmarkable / shareable] |

#### UI Action - API Contract Mapping

| UI Action | API Endpoint | Request | Response | Error Contract |
|-----------|-------------|---------|----------|----------------|
| [Button click / form submit] | [POST /api/xxx] | [Request body fields] | [Response fields] | [Error codes and UI handling] |

#### Routing & Code-Splitting

- **New routes**: [paths and entry components]
- **Code-split boundaries**: [lazy-loaded chunks]
- **Auth-gated routes**: [redirect behavior on unauth]

#### Accessibility & i18n

- **A11y commitments**: [keyboard navigation, ARIA, contrast targets]
- **i18n keys added**: [namespace and key prefix]

---

### Backend Design

Mark as `N/A — out of scope` if Backend not in Layer Scope.

#### Service / Module Layout

| Module | Responsibility | Public Surface |
|--------|----------------|----------------|
| [module path] | [domain concern owned] | [exported functions/types/handlers] |

#### Domain Model

- **Entities introduced/modified**: [list, with invariants]
- **Aggregates / transactional boundaries**: [what mutates together atomically]
- **Domain events emitted**: [event name, payload, consumers]

#### Background Work

| Job / Worker | Trigger | Idempotency Key | Failure Behavior | SLO |
|--------------|---------|-----------------|------------------|-----|
| [job name] | [schedule / queue message / webhook] | [key derivation] | [retry policy / DLQ] | [completion target] |

#### External Service Calls

| Dependency | Call Pattern | Timeout | Retry Policy | Circuit Breaker | Fallback |
|------------|--------------|---------|--------------|-----------------|----------|
| [service name] | [sync/async, REST/gRPC] | [ms] | [count/backoff] | [threshold] | [graceful degradation] |

---

### API Design

Mark as `N/A — out of scope` if API not in Layer Scope.

#### Endpoint Catalog

| Method | Path | Purpose | Auth | Idempotent |
|--------|------|---------|------|------------|
| [GET/POST/...] | [/api/v1/...] | [purpose] | [scheme + scope] | [Yes/No] |

#### Request / Response Schemas

For each endpoint, reference the schema source rather than duplicating:

| Endpoint | Request Schema | Response Schema | Error Schema |
|----------|----------------|-----------------|--------------|
| [METHOD /path] | [`$ref` or path] | [`$ref` or path] | [`$ref` or path] |

#### Versioning & Deprecation

- **Versioning strategy**: [URL / header / media-type]
- **Deprecation policy**: [sunset header, notice period, removal target]
- **Breaking change?** [Yes/No] — if Yes: [migration path for clients]

#### Pagination, Filtering, Sorting

| Endpoint | Pagination | Filter Fields | Sort Fields | Default Order |
|----------|------------|---------------|-------------|---------------|
| [endpoint] | [cursor / offset / page] | [allowed fields] | [allowed fields] | [field + direction] |

#### Rate Limiting & Quotas

- **Per-endpoint limits**: [requests / window / scope]
- **Rate-limit signaling**: [headers, error code on breach]

---

### Query & Data Access Design

Mark as `N/A — out of scope` if Query not in Layer Scope.

#### Access Pattern Inventory

| Access Pattern | Read/Write | Frequency | Latency Target | Path |
|----------------|-----------|-----------|----------------|------|
| [e.g., "list active orders for user"] | Read | [high/medium/low] | [p95 target] | [repository.method] |

#### Query Plan / Index Coverage

| Query | Tables Touched | Indexes Relied On | Expected Plan | Risk |
|-------|---------------|-------------------|---------------|------|
| [query name or representative SQL] | [tables] | [index names — see Database section] | [seq scan / index scan / hash join / etc.] | [hot table / large scan / lock contention] |

#### Caching Strategy

| Cache Layer | Key Shape | TTL | Invalidation Trigger | Stampede Protection |
|-------------|-----------|-----|----------------------|---------------------|
| [in-memory / Redis / CDN] | [key template] | [duration] | [event/write-through] | [single-flight / jitter] |

#### Transaction Boundaries

- **Atomic units**: [which operations must commit/rollback together]
- **Isolation level required**: [READ COMMITTED / REPEATABLE READ / SERIALIZABLE]
- **Locking strategy**: [optimistic version column / `SELECT ... FOR UPDATE` / advisory lock]

#### N+1 & Hot-Path Audit

- **Known N+1 risks**: [pattern and mitigation: batch loader / eager join / projection]
- **Hot paths protected**: [path and protection mechanism]

---

### Database Schema & Migration Design

Mark as `N/A — out of scope` if Database not in Layer Scope.

#### Schema Changes

| Table | Change Type | Detail | Backward Compatible |
|-------|-------------|--------|---------------------|
| [table name] | add table / add column / alter column / drop column / add constraint / drop constraint | [DDL summary] | [Yes/No — old code can still run] |

#### New / Modified Columns

| Table.Column | Type | Nullable | Default | Constraint | Notes |
|--------------|------|----------|---------|------------|-------|
| [table.column] | [type] | [Y/N] | [value or none] | [PK / FK / UNIQUE / CHECK] | [domain meaning] |

#### Indexes

| Index | Table | Columns | Type | Rationale | Created Concurrently? |
|-------|-------|---------|------|-----------|----------------------|
| [name] | [table] | [columns + order] | [btree / hash / gin / partial / covering] | [query it serves] | [Yes/No — for online DDL] |

#### Migration Strategy

```yaml
Approach: "expand-contract | single-step | blue-green | shadow-write"
Steps:
  - step: "[e.g., add nullable column]"
    deployable_independently: true
    reversible: true
  - step: "[e.g., backfill]"
    chunking: "[batch size / throttle]"
    estimated_duration: "[time]"
    reversible: false_but_idempotent
  - step: "[e.g., set NOT NULL]"
    requires_prior_steps_complete: true
Rollback_Plan: "[forward-fix only / down migration / restore from snapshot]"
Lock_Behavior:
  - "[which steps take exclusive locks, expected duration, contention risk]"
Data_Backfill:
  source: "[where data originates]"
  validation: "[row count, checksum, sampling]"
```

#### Constraints & Referential Integrity

- **Foreign keys added**: [parent → child, ON DELETE / ON UPDATE behavior]
- **Check constraints**: [predicate and purpose]
- **Unique constraints**: [columns and scope]

#### Seed / Reference Data

- **Reference data changes**: [table, rows added/changed, source of truth]
- **Seed mechanism**: [migration / separate seed script / IaC]

---

### CI/CD Design (GitHub Actions)

Mark as `N/A — out of scope` if CI/CD not in Layer Scope.

#### Workflow Inventory

| Workflow File | Triggers | Purpose | Concurrency Group |
|---------------|----------|---------|-------------------|
| `.github/workflows/[name].yml` | [push / pull_request / workflow_dispatch / schedule / workflow_call] | [purpose] | [group key — prevents overlap] |

#### Job Graph

```
[Pseudo-diagram of job dependencies, e.g.:
  lint ──┐
         ├─► build ──► test ──► deploy-staging ──► smoke ──► deploy-prod
  typecheck ─┘                                                    │
                                                       (manual approval)]
```

#### Reusable Actions / Composite Actions

| Action | Location | Inputs | Outputs |
|--------|----------|--------|---------|
| [action name] | [`.github/actions/<name>/action.yml` or `org/repo@ref`] | [key inputs] | [key outputs] |

#### Secrets, Variables & Environments

| Name | Scope | Type | Source | Used By |
|------|-------|------|--------|---------|
| [SECRET_NAME] | [repo / environment / org] | [secret / variable] | [vault / OIDC federation / manual] | [job names] |

#### Permissions

| Workflow / Job | `permissions:` block | Justification |
|----------------|----------------------|---------------|
| [name] | [e.g., `contents: read, id-token: write`] | [why each scope is needed — principle of least privilege] |

#### Caching & Artifacts

| Cache / Artifact | Key | Scope | Retention |
|------------------|-----|-------|-----------|
| [name] | [cache key template / artifact name] | [job / workflow / cross-workflow] | [days] |

#### Environments & Promotion

| Environment | Protection Rules | Required Reviewers | Wait Timer | Deployment Branches |
|-------------|------------------|---------------------|------------|---------------------|
| [staging / production] | [protection rules] | [users/teams] | [duration] | [branch patterns] |

#### Failure & Rollback

- **Failed-deploy behavior**: [auto-rollback / hold / alert]
- **Rollback workflow**: [manual `workflow_dispatch` / automatic on health-check failure]
- **Notification routing**: [channel and triggers]

---

### Infrastructure as Code Design

Mark as `N/A — out of scope` if IaC not in Layer Scope.

#### IaC Tooling Context

- **Tool**: [Terraform / OpenTofu / Pulumi / CDK / CloudFormation / Bicep]
- **Version**: [version pin source]
- **State backend**: [where state lives, locking mechanism]
- **Workspace / stack model**: [per-env workspace / branch-based / directory-based]

#### Module / Stack Changes

| Module / Stack | Path | Change Type | Affected Resources |
|----------------|------|-------------|--------------------|
| [name] | [path] | new / modified / deprecated | [resource types and counts] |

#### Resources Created / Modified / Destroyed

| Resource Type | Identifier | Change | Stateful? | Replacement Risk |
|---------------|------------|--------|-----------|------------------|
| [e.g., aws_db_instance] | [logical name] | create / update / replace / destroy | [Y/N] | [does change force replacement?] |

#### Provider Versions & Drift

- **Provider version constraints**: [provider → version range, rationale for any pin]
- **Drift detection**: [how drift is detected — scheduled plan / Atlantis / Terraform Cloud]
- **Manual changes policy**: [allowed / forbidden / how reconciled]

#### Plan & Apply Workflow

- **Plan execution**: [where plan runs — local / CI / Terraform Cloud]
- **Apply approval**: [who approves, on which environments]
- **Destructive change handling**: [`prevent_destroy`, manual approval gate]

#### Secrets in IaC

- **Secret references**: [how secrets are read — SSM / Secrets Manager / Vault / GitHub OIDC]
- **No-plaintext guarantee**: [how this is enforced — pre-commit hook / CI scan]

#### Cost & Quota Awareness

- **Cost impact**: [estimated delta, source of estimate — Infracost / manual]
- **Quota / limit checks**: [service quotas this could approach]

---

### Dev Environment (Codespaces) Design

Mark as `N/A — out of scope` if Codespaces not in Layer Scope.

#### Devcontainer Configuration

| File | Change | Purpose |
|------|--------|---------|
| `.devcontainer/devcontainer.json` | [new / modified] | [base image, features, settings] |
| `.devcontainer/Dockerfile` | [new / modified / N/A] | [customizations beyond features] |
| `.devcontainer/docker-compose.yml` | [new / modified / N/A] | [multi-service dev topology] |

#### Base Image & Features

- **Base image**: [`mcr.microsoft.com/devcontainers/...` or custom]
- **Features added**: [list of `ghcr.io/devcontainers/features/...` with versions]
- **Rationale for image choice**: [size, tooling, parity with prod]

#### Lifecycle Scripts

| Hook | Script | Purpose | Idempotent |
|------|--------|---------|------------|
| `onCreateCommand` | [command] | [one-time setup on container creation] | [Y/N] |
| `postCreateCommand` | [command] | [setup after create — installs, seeds] | [Y/N] |
| `postStartCommand` | [command] | [each container start] | [Y/N] |
| `postAttachCommand` | [command] | [each terminal attach] | [Y/N] |

#### Forwarded Ports & Services

| Port | Service | Visibility | Auto-forward |
|------|---------|------------|--------------|
| [port] | [service] | [private / org / public] | [Y/N] |

#### Prebuilds

- **Prebuild config**: [which branches trigger prebuilds, machine size]
- **Expected cold-start time**: [with prebuild / without]

#### VS Code Configuration

- **Extensions installed**: [list of extension IDs]
- **Workspace settings**: [key `settings.json` entries]
- **Tasks / launch configs**: [debugger / task changes]

#### Parity with CI & Production

- **CI uses the same image?** [Y/N — if no, drift risk]
- **Production parity**: [what differs from prod, why it's acceptable]

#### Secrets in Codespaces

- **Required Codespace secrets**: [name, scope, source]
- **First-run experience**: [what a contributor must configure manually]

---

### Error Handling

| Error Category | Example | Detection | Recovery Strategy | User Impact |
|---------------|---------|-----------|-------------------|-------------|
| [Validation / External / Infrastructure / Business logic / Migration / Pipeline] | [Specific error] | [How detected] | [Retry / Fallback / Propagate / Log-and-continue / Halt pipeline] | [User-facing message or silent handling] |

### Logging and Monitoring

- **Log events**: [Key events to log: state transitions, external calls, error occurrences, performance thresholds, migration progress, deploy outcomes]
- **Log levels**: [Which events at DEBUG/INFO/WARN/ERROR]
- **Sensitive data**: [Fields to mask or exclude — coordinate with Security Considerations]
- **Metrics**: [Counters, histograms, gauges — name and labels]
- **Traces**: [Critical spans, propagation across service/queue boundaries]
- **Alerts**: [Alert name, condition, severity, routing]
- **Dashboards**: [Which dashboard(s) updated; new panels added]

## Implementation Plan

### Implementation Approach

**Selected Approach**: [Approach name or combination]
**Selection Reason**: [Reason considering project constraints and technical dependencies]

### Technical Dependencies and Implementation Order

#### Required Implementation Order

1. **[Component/Feature A]**
   - Layer: [layer]
   - Technical Reason: [Why this needs to be implemented first]
   - Dependent Elements: [Other components that depend on this]

2. **[Component/Feature B]**
   - Layer: [layer]
   - Technical Reason: [Technical necessity to implement after A]
   - Prerequisites: [Required pre-implementations]

#### Cross-Layer Sequencing Notes

- **Schema before code**: [if DB changes precede backend code that uses them]
- **API before client**: [if backend/contract precedes frontend consumption]
- **IaC before pipeline**: [if pipeline depends on new infra]
- **Devcontainer before everything**: [if new tooling is required to build locally]

### Migration Strategy

[Technical migration approach. Reference Database section's migration plan if applicable. For pipeline/IaC changes, describe how old and new run side-by-side or cut over.]

### Feature Flags & Rollout

| Flag | Default | Audience Progression | Kill-Switch Behavior |
|------|---------|----------------------|----------------------|
| [flag name] | [off/on] | [internal → 1% → 10% → 100%] | [what reverting to default does] |

## Security Considerations

Evaluate per layer in scope. Mark items as N/A with brief rationale when the layer or boundary does not apply.

### Cross-Cutting

- **Authentication & Authorization**: What authentication is required for new entry points? What authorization checks protect resource access?
- **Input Validation**: Where does external input enter the system? How is it validated before processing?
- **Sensitive Data Handling**: What data requires protection (encryption, masking, access control)? What data is safe to include in logs and error responses?

### Frontend
- **XSS / injection surfaces**: [user-rendered content, sanitization]
- **CSRF protections**: [token, SameSite cookies]
- **Client-side secrets**: [confirmed none, or rationale]

### Backend / API
- **AuthN/AuthZ enforcement points**: [middleware, per-route checks]
- **Input validation library and contract**: [schema enforcement at boundary]
- **Rate limiting & abuse prevention**: [per-IP / per-user / per-key]

### Query / Database
- **SQL injection surface**: [parameterization enforced, ORM coverage]
- **Row-level security**: [tenant isolation, RLS policies]
- **PII columns**: [encryption at rest, access logging]

### CI/CD
- **Secret exposure surface**: [`pull_request_target` usage, fork PR handling]
- **Supply chain**: [action pinning by SHA, allowed-action policy]
- **OIDC vs long-lived credentials**: [federation in place where possible]

### IaC
- **Blast radius of credentials**: [admin role scoping, separation of plan vs apply identities]
- **Public exposure risk**: [security groups, bucket ACLs, default-deny posture]

### Codespaces
- **Repo access from Codespace**: [token scopes, GITHUB_TOKEN permissions]
- **Dotfiles / extension trust**: [first-run prompts, untrusted extension policy]

## Test Boundaries

### Mock Boundary Decisions

| Component/Dependency | Mock? | Rationale |
|---------------------|-------|-----------|
| [External API / DB / File system / Queue / Cloud SDK / GitHub API / etc.] | [Yes/No] | [Why this boundary was chosen] |

### Data Layer Testing Strategy

- **Schema dependencies**: [List tables/models this feature reads from or writes to, with paths to their definitions]
- **Test data approach**: [Fixtures / factories / seed scripts / ephemeral DB / real database]
- **Mock limitations acknowledged**: [What cannot be reliably tested with mocks alone]

### Per-Layer Test Strategy

| Layer | Test Type | Tooling | Location |
|-------|-----------|---------|----------|
| Frontend | [unit / component / e2e] | [Jest / Vitest / Playwright / Cypress] | [test path] |
| Backend | [unit / integration] | [framework] | [test path] |
| API | [contract / integration] | [Pact / Dredd / schema-validation] | [test path] |
| Query | [integration against real or ephemeral DB] | [testcontainers / sqlite / etc.] | [test path] |
| Database | [migration test, forward+backward] | [migration runner in CI] | [workflow / test path] |
| CI/CD | [act / workflow lint / sample run] | [actionlint / nektos/act] | [where validated] |
| IaC | [plan diff, policy-as-code] | [terraform plan / tflint / Checkov / OPA] | [pipeline step] |
| Codespaces | [prebuild boot test, smoke command] | [`devcontainer/ci` action] | [workflow path] |

### Integration Verification Points

- [List critical integration points that require testing beyond unit-level mocks]

## Verification Strategy

Verification Strategy defines what correctness means and how to prove it at design time. L1/L2/L3 levels (L1: functional operation works as end-user feature; L2: tests added and passing; L3: build succeeds without errors) define completion verification granularity at task execution time.

### Correctness Proof Method

- **Correctness definition**: [What "correct" means for this change — e.g., "output matches existing behavior", "all ACs pass in production-equivalent environment", "generated queries execute without error on target DB", "Terraform plan is empty after apply", "Codespace boots and runs `make test` successfully"]
- **Verification method**: [Specific technique — e.g., "compare new implementation output against existing", "run against staging DB", "contract test with real API", "smoke workflow against ephemeral env"]
- **Verification timing**: [When verification occurs — e.g., "after first vertical slice", "per repository", "at integration phase", "in pre-merge CI", "post-deploy in staging"]

### Early Verification Point

- **First verification target**: [The smallest unit that proves the approach works — e.g., "first repository migration", "single API endpoint", "one screen flow", "one tenant's data through the pipeline", "single environment's Terraform apply"]
- **Success criteria**: [Observable outcome — e.g., "CSV download produces identical output to legacy", "API returns 200 with expected schema", "plan produces only expected diffs"]
- **Failure response**: [What to do if early verification fails — e.g., "reassess approach before proceeding", "escalate to user"]

### Output Comparison (When Replacing or Modifying Existing Behavior)

- **Comparison input**: [Identical input used for both implementations — e.g., "same DB snapshot", "same API request payload", "same workflow trigger event"]
- **Expected output fields**: [Specific fields/columns/artifacts to compare]
- **Diff method**: [File-level diff / JSON field-by-field / row count + spot check / plan diff]
- **Transformation pipeline coverage**: [Each step from codebase analysis `dataTransformationPipelines` and what the comparison covers]

Mark as N/A with brief rationale when the design introduces entirely new behavior with no existing equivalent.

### Operational Verification (When Pipeline / Infra / Migration in Scope)

- **Pre-merge gates**: [which checks must pass before merge]
- **Post-deploy verification**: [health probes, smoke tests, canary metrics]
- **Migration verification**: [row counts, checksums, sampling, foreign-key validation]
- **Rollback rehearsal**: [whether rollback was tested in staging, evidence]

## Future Extensibility

- **Extension points**: [Interfaces, hooks, plugin mechanisms, schema reserved fields, workflow inputs designed for future use]
- **Known future requirements**: [Planned features that influenced current design decisions]
- **Intentional limitations**: [What was deliberately kept simple and why]

## Alternative Solutions

### Alternative 1

- **Overview**: [Description of alternative solution]
- **Advantages**: [Advantages]
- **Disadvantages**: [Disadvantages]
- **Reason for Rejection**: [Why it wasn't adopted]

## Risks and Mitigation

| Risk | Layer | Impact | Probability | Mitigation |
|------|-------|--------|-------------|------------|
| [Risk 1] | [layer] | High/Medium/Low | High/Medium/Low | [Countermeasure] |

## References

- [Related documentation and links]

## Update History

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| YYYY-MM-DD | 1.0 | Initial version | [Name] |