---
name: kb-iac-design
description: >-
  Design discipline for the Infrastructure-as-Code (IaC) layer — Terraform,
  Pulumi, CDK, Crossplane, and equivalent tools that declare cloud and platform
  resources in code. Covers state management, plan-before-apply discipline,
  idempotency, blast-radius containment (stack-per-environment, module-per-
  concern), drift detection, secret management, and the per-layer designer's
  workflow for producing the IaC Design subsection of a Blueprint. Use when
  the feature touches provisioned infrastructure. Pairs with KB-github-actions-
  design (where IaC is run) and KB-database-design / KB-codespaces-design /
  KB-cc-design (the resources being provisioned).
allowed-tools: Read, Grep, Glob
---

# KB-iac-design — Infrastructure-as-Code Layer Design Discipline

Design discipline for the Infrastructure-as-Code layer. The per-layer IaC Designer (`design-iac`) loads this KB during per-layer Design to produce the `### IaC Design` subsection of the Blueprint. Design-discipline-only — specific tools (Terraform, Pulumi, CDK, Crossplane) and target platforms (AWS, GCP, Azure, Kubernetes) are platform-level concerns the Designer pulls from Synthesis output as needed.

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

- A feature's PRD or Blueprint declares the **IaC** layer in scope (per `layer-taxonomy.md` in KB-documentation-criteria)
- A per-layer Designer is producing the IaC Design subsection of the Blueprint
- Plan Authoring produces tasks that touch Terraform / Pulumi / CDK / Crossplane code or remote state
- `shared-document-reviewer` or `review-architecture-auditor` is auditing artifacts that include IaC Design

Sub-agents that reference this KB (per Blueprint v4.3.1):

- `design-iac` (per-layer Design, when IaC layer is in scope)
- `design-composer` (Design Composition, integrating IaC design with cross-cutting concerns)
- `plan-author` (when tasks touch IaC code or state)
- `shared-document-reviewer` (Gate 1 IaC-specific checks)
- `review-architecture-auditor` (CoVe checks on IaC claims)

## The layer's responsibility

The IaC layer expresses infrastructure as code, with state tracked and changes governed by a plan-before-apply discipline. It owns:

- **The infrastructure inventory.** Every cloud resource (compute, storage, network, identity, managed service) declared in code, not provisioned by hand.
- **State management.** Where the IaC tool stores its current view of reality, who can read it, who can lock it, how it backs up.
- **The apply discipline.** Plan output is reviewed before apply. Apply is gated by CI or by a runner (Terraform Cloud, Spacelift, Atlantis, Pulumi Cloud).
- **Blast-radius containment.** A bad change in one stack doesn't take down others. Environments, concerns, and ownership boundaries split into separate state files / stacks.
- **Drift detection.** Detect when reality diverges from code (someone clicked in the console). Reconcile or flag.
- **Secret management.** Secrets are never plaintext in state; access is via OIDC, KMS-encrypted, or external secret stores (Vault, AWS Secrets Manager, GCP Secret Manager).
- **Module versioning.** Reusable modules are versioned semantically; consumers pin versions.

The IaC layer does NOT own:

- The application code that runs on the infrastructure (Backend, Frontend, Query, Database layers).
- The CI/CD workflow that runs the IaC tool (CI/CD layer's job).
- The runtime configuration of services (often deferred to the platform; the IaC layer provisions the SECRETS REFS, not the values).

## Design decisions this layer owns

The IaC Designer makes (or surfaces) these decisions:

| Decision | Forced if … |
|---|---|
| Tool (Terraform / Pulumi / CDK / Crossplane / cloud-native) | Greenfield; brownfield usually inherits |
| State backend (cloud bucket + lock table, Terraform Cloud, Pulumi Cloud, hosted runner) | Any infrastructure being provisioned |
| Module structure (per-concern modules, monolithic root) | Codebase has more than ~5 resources |
| Environment strategy (workspaces vs. separate directories vs. separate state files) | More than one environment exists |
| Stack boundaries (one stack vs. many; what's together, what's apart) | The infrastructure has more than ~20 resources or multiple concerns |
| Runner / CI integration (manual local apply, GitHub Actions, Terraform Cloud, Atlantis, Spacelift) | Team has more than 1 person making infra changes |
| Apply gate (auto-apply on merge vs. manual approval vs. environment-specific gate) | Production environment exists |
| Secret-management approach (cloud KMS, Vault, SOPS, env-var injection via runner) | Any secret is required |
| OIDC vs. long-lived credentials | Any cloud integration |
| Drift-detection cadence (scheduled plan + alert on diff) | Manual changes are possible |
| Module-versioning approach (semver tags + version pinning, monorepo with internal refs) | Modules are reused across stacks |
| Naming convention (resource names, tags) | Any non-trivial resource count |

Designers do NOT author ADRs (per FR-5). Cross-cutting IaC decisions (tool standardization, secret-management policy, OIDC adoption) get surfaced as open items.

## Patterns and anti-patterns at a glance

The full discipline lives in `references/principles.md` and `references/patterns-and-anti-patterns.md`. Quick reference:

**Patterns to favor:**

- **State as source of truth.** Never edit state by hand. Reality and code are reconciled via plan + apply.
- **Plan-before-apply on every change.** The plan output is human-reviewed (or machine-validated against allow/deny rules) before apply.
- **Stack-per-environment.** Dev, staging, prod are separate state files / stacks. A bad apply in staging can't accidentally affect prod.
- **Module-per-concern.** A network module, a database module, a Kubernetes-cluster module. Each is independently versionable and reusable.
- **OIDC for cloud auth.** No long-lived AWS/GCP/Azure keys stored as secrets. CI authenticates via OIDC; the cloud issues short-lived tokens.
- **Remote state with locking.** S3 + DynamoDB lock table; GCS + state lock; or managed (Terraform Cloud, Pulumi Cloud). Never local state for shared infra.
- **Drift detection scheduled.** Nightly `terraform plan` (or equivalent) checks for drift; non-zero diff fires an alert.
- **Idempotent by construction.** The same code applied twice produces the same result; runs are repeatable.

**Anti-patterns to flag:**

- **Untracked manual changes.** Clicking in the console then forgetting to update code; state drifts; future applies fail or revert unexpectedly.
- **Monolithic stack.** One huge stack containing all environments and all concerns. Blast radius too large; plan times grow unbounded.
- **Hardcoded secrets in code.** Even if encrypted later, they're in git history.
- **`local-exec` running production-critical shell scripts.** Imperative escape hatch; defeats the declarative model.
- **Manual `terraform apply` from a developer machine on production.** No audit, no review, no lock guarantees against concurrent applies.
- **Long-lived AWS access keys in CI secrets.** Should be OIDC.

## Interaction with other layers

```
[IaC layer] ──provisions──► Database, network, compute, managed services
     │                              │
     │                              └──► Backend / Query / Frontend / CC platform RUN on these
     │
     └──run-by──► CI/CD (GitHub Actions, Terraform Cloud, etc.)
                       │
                       └──► reads code from repo; applies state
```

The IaC Designer's responsibility:

- **CI/CD (executor)** — the CI/CD pipeline runs the IaC tool. The IaC Designer documents what the pipeline must do (plan, gate, apply), not how (the CI/CD Designer implements).
- **Database, Codespaces, CC platform (provisioned resources)** — these layers' Designers tell the IaC Designer what infrastructure they need (engine version, instance class, secret-references). The IaC Designer provisions accordingly.
- **Backend / Query / Frontend** — these layers run on infrastructure provisioned by IaC. Coupling between application code and IaC outputs (e.g., the Backend reads an environment variable populated from an IaC-output) should be explicit; document the contract.
- **Security / compliance (cross-cutting)** — the IaC layer is often where compliance controls land (encryption at rest, network policies, IAM scopes). The Designer documents the compliance commitments as Acceptance Criteria.

## Surfacing architectural questions

```markdown
## Architectural Questions for Composer

- **Q-IaC-1**: Should we adopt OIDC federation from GitHub to AWS for all CI deploys, replacing the current long-lived access keys? The choice affects CI/CD design (workflow auth steps), IaC code (IAM trust policies), and the secret rotation discipline (OIDC eliminates the rotation requirement). Evidence: 4 of 6 deploy pipelines currently use long-lived keys; 2 already use OIDC. Options: (a) standardize on OIDC for all new and migrate existing within a quarter; (b) leave existing as-is; require OIDC for new only; (c) maintain status quo. Recommended: (a). Defer to composer.
```

## When to load each reference file

| Load this file | When the task involves |
|---|---|
| `references/principles.md` | Authoring or reviewing an IaC Design subsection — covers the foundational principles (state as source of truth, plan-before-apply, blast-radius containment, OIDC, drift detection) |
| `references/patterns-and-anti-patterns.md` | Choosing between stack / module layouts, picking runner and secret-management approaches — covers common patterns with when-to-use and the anti-patterns reviewers should flag |
