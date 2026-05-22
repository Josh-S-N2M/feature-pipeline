---
name: kb-github-actions-design
description: >-
  Design discipline for the CI/CD layer when implemented via GitHub Actions.
  Pairs with KB-github-actions-platform (the platform half). Covers when to
  choose workflow_call vs. composite action vs. reusable workflow, when to
  introduce GitHub Environments with protection rules, when matrix vs.
  separate jobs, concurrency-control strategy, deployment-pattern selection
  (rolling / blue-green / canary), CI vs. CD separation, and the per-layer
  designer's workflow for producing the CI/CD Design subsection of a
  Blueprint.
allowed-tools: Read, Grep, Glob
---

# KB-github-actions-design — CI/CD Layer Design Discipline (GitHub Actions)

Design discipline for the CI/CD layer when implemented via GitHub Actions. The per-layer CI/CD Designer (`design-cicd`) loads this KB during per-layer Design to produce the `### CI/CD Design` subsection of the Blueprint. This is the **design half** of the GitHub-Actions skill pair — KB-github-actions-platform is the platform half (workflow YAML, primitives, audit script, templates). Load both for CI/CD design work; load just KB-github-actions-platform for syntax / reference questions.

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

- A feature's PRD or Blueprint declares the **CI/CD** layer in scope (per `layer-taxonomy.md` in KB-documentation-criteria)
- A per-layer Designer is producing the CI/CD Design subsection of the Blueprint
- The change involves choosing between workflow patterns (new pipeline, refactor, deployment strategy), NOT just modifying a workflow with known shape
- Plan Authoring produces tasks that introduce or refactor `.github/workflows/` in a way that requires design judgment

Sub-agents that reference this KB (per Blueprint v4.3.1):

- `design-cicd` (per-layer Design, when CI/CD layer is in scope)
- `design-composer` (Design Composition, integrating CI/CD design with cross-cutting concerns)
- `plan-author` (when tasks introduce new workflows of non-trivial complexity)
- `shared-document-reviewer` (Gate 1 CI/CD-specific checks)

This KB and KB-github-actions-platform are designed to load together. The design KB teaches discipline; the platform KB teaches facts and provides templates / audit tooling.

## The layer's responsibility

The CI/CD layer owns the pipeline that turns commits into deployed artifacts. The Designer makes decisions about:

- **Pipeline structure.** What runs on PR, what runs on merge, what runs on release. What's a single workflow vs. multiple workflows.
- **Reusability mechanism.** When a duplicated step set warrants a composite action, a reusable workflow, or a custom action.
- **Concurrency model.** When two workflows can run together, when one cancels the other, how deployments are serialized.
- **Environment topology.** Which environments exist; what protection rules gate promotion; what approvals are required.
- **Cache and artifact strategy.** What's cached, where, how it's keyed. What's an artifact vs. a cache vs. ephemeral.
- **Deployment pattern.** Rolling, blue-green, canary, immutable infrastructure. Per environment.
- **Security posture.** OIDC scoping, secrets exposure, SHA-pinning policy enforcement, code-injection prevention.
- **Failure model.** Retry policies, manual gates, rollback path, notifications.

The CI/CD Designer does NOT own:

- The platform facts (YAML syntax, action versions, runner specs). Those are in KB-github-actions-platform.
- The application build/test commands themselves (Backend / Frontend / Query / Database design owns those at the artifact level; CI/CD invokes them).
- The infrastructure being deployed to (IaC layer's job).
- The Claude Code Action integration design — that's the CC layer pair (`KB-cc-design`).

## Design decisions this layer owns

The CI/CD Designer makes (or surfaces) these decisions:

| Decision | Forced if … |
|---|---|
| Trigger pattern (push / PR / schedule / manual / repository_dispatch / workflow_run) | A new workflow is added |
| Workflow composition (single workflow vs. orchestrated workflows) | The pipeline has more than ~5 jobs |
| Reusability mechanism (composite action / reusable workflow / custom JS action) | Duplication appears across workflows |
| Concurrency group strategy | More than one run of the same workflow can be triggered |
| Environment topology (dev/staging/prod; per-tenant; per-region) | Deploying to more than one place |
| Environment protection rules (required reviewers; wait timer; restricted branches) | Production environment exists |
| Deployment pattern (rolling / blue-green / canary / immutable) | Production deploys are part of scope |
| OIDC role scoping (per-environment, per-workflow) | Cloud integration via OIDC |
| Secret scoping (repo / environment / org) | Secrets are required |
| Cache strategy (what / where / key / restore-keys) | Build times warrant caching |
| Artifact policy (retention, naming, what's produced) | Artifacts are emitted |
| Matrix strategy (when matrix; max-parallel; fail-fast) | Tests across multiple configs |
| Self-hosted vs. GitHub-hosted runners | Specific OS, GPU, or network constraints exist |
| Status check requirements (which checks block merge) | Branch protection is in scope |
| Notification policy (Slack / email / GitHub) | Long-running deploys; failures need broadcast |

Designers do NOT author ADRs (per FR-5). Cross-cutting CI/CD decisions (canonical deploy pattern, OIDC adoption, runner topology) surface as open items.

## Patterns and anti-patterns at a glance

The full discipline lives in `references/principles.md` and `references/patterns-and-anti-patterns.md`. Quick reference:

**Patterns to favor:**

- **Separate CI and CD.** CI workflow runs on PR; CD workflow runs on merge or manual trigger. Don't conflate.
- **Reusable workflow for org-wide deploy logic.** When 5 services share the same "build → push → deploy" sequence, a reusable workflow centralizes it.
- **Composite action for tightly-coupled step bundles** within a single workflow file's domain.
- **Concurrency groups per environment.** `concurrency: ${{ github.workflow }}-${{ inputs.environment }}` prevents two deploys to the same env from racing.
- **OIDC for cloud auth; per-environment role.** No long-lived access keys.
- **Required environment approvals for production.** A second pair of eyes before production traffic is touched.
- **Status checks gating merges.** Branch protection requires the CI workflow to pass.
- **Caches keyed by dependency lockfile.** `${{ hashFiles('**/package-lock.json') }}` — stable across runs, invalidated on dependency change.

**Anti-patterns to flag:**

- **`pull_request_target` with checkout of PR head.** Code-injection vector; runs untrusted code with secrets.
- **Tag-pinned third-party action.** Tags are mutable; pin to SHA.
- **Hardcoded credentials in workflow.** Even encrypted, eventually leak; use OIDC or scoped secrets.
- **Concurrency unspecified for deploy workflows.** Two deploys race; one wins.
- **`if: always()` on critical steps.** Hides failures.
- **Reusable workflow with 20+ inputs.** It's not reusable; it's a config protocol — refactor.
- **Matrix that doesn't need to be a matrix.** Two unrelated jobs masquerading as matrix entries.

## Interaction with other layers

```
                    [CI/CD layer (this KB)]
                            │
        Triggered by ───────┤───── Triggers
            │               │           │
            ▼               ▼           ▼
        push / PR      build, test    deploy
                            │           │
                            │           ▼
                            │       IaC apply (separate workflow or stage)
                            │
                            └─► artifacts → registry / blob store
```

The CI/CD Designer's responsibility:

- **IaC** — CI/CD often runs Terraform/Pulumi/CDK. The CI/CD Designer documents the workflow that runs IaC (plan / apply, with approval gates); the IaC Designer specifies WHAT the IaC tool does.
- **Backend / Frontend / Query / Database** — CI/CD runs each layer's build / test / packaging commands. The Designer of each layer specifies the commands (in their per-layer Design); the CI/CD Designer composes them into workflows.
- **CC** — Claude Code Action can run in CI. The CC Designer specifies which skills / agents are usable from CI; the CI/CD Designer integrates.

## Surfacing architectural questions

```markdown
## Architectural Questions for Composer

- **Q-CICD-1**: Should we adopt a single reusable workflow for "build and deploy" across our 6 services? Currently each service has its own bespoke workflow with ~85% duplication. The choice affects ownership (centralized vs. per-service), update propagation (one change vs. six), and per-service flexibility (constrained by the reusable workflow's inputs). Evidence: drift between services has caused 2 production incidents in 6 months. Options: (a) reusable workflow in a shared repo; (b) composite action shared via the same mechanism; (c) status quo. Recommended: (a). Defer to composer.
```

## When to load each reference file

| Load this file | When the task involves |
|---|---|
| `references/principles.md` | Authoring or reviewing a CI/CD Design subsection — covers the foundational principles (separate CI from CD; OIDC over long-lived keys; concurrency groups; environment protection rules; least-privilege; SHA-pinning) |
| `references/patterns-and-anti-patterns.md` | Choosing between reusable workflow / composite action; matrix vs. separate jobs; deployment patterns; cache strategies — covers common design patterns with when-to-use and the anti-patterns reviewers should flag |
