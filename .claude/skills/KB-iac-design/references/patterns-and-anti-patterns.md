# IaC Patterns and Anti-Patterns

## Contents

- Stack-and-module patterns
- Environment-isolation patterns
- State-backend patterns
- Runner / apply-gate patterns
- Secret-management patterns
- Drift-handling patterns
- Anti-patterns reviewers should flag
- Decision frames

## Stack-and-module patterns

### Stack-per-environment

```
infra/
├── environments/
│   ├── dev/        # state: dev.tfstate
│   ├── staging/    # state: staging.tfstate
│   └── prod/       # state: prod.tfstate
└── modules/
    ├── network/
    ├── database/
    └── kubernetes/
```

**Pattern.** One stack (state file) per environment. Same module library, different parameters.

**When to use.** Default. Provides clear blast-radius boundary; environments evolve at their own pace.

**Strengths.** Promote-from-dev workflow (validate change in dev → staging → prod, each its own apply). Different environments can use different module versions.

### Module-per-concern

**Pattern.** Each logical concern is a module: `network`, `database`, `cluster`, `monitoring`, `iam`. Composed in the environment root.

**When to use.** Codebase has more than ~5 distinct resource groups. Reuse across environments justifies the abstraction.

**Strengths.** Versionable independently; clear ownership; testable in isolation.

**Weaknesses.** Versioning discipline required (semver tags + pin); without it, modules become "always-latest" and changes cascade unpredictably.

### Stack-per-concern within an environment

```
environments/prod/
├── network/       # state: prod-network.tfstate
├── database/      # state: prod-database.tfstate
├── cluster/       # state: prod-cluster.tfstate
└── application/   # state: prod-application.tfstate
```

**Pattern.** Within an environment, split into multiple stacks by concern. Cross-stack data via remote-state lookups.

**When to use.** Single environment has so many resources that a single plan takes minutes; ownership splits across teams (network team owns the network stack; application team owns its stack).

**Risks.** Cross-stack dependencies are loose; ordering matters; explicit documentation required.

### Workspaces (Terraform-specific)

**Pattern.** Single code base, multiple state files indexed by workspace name. `terraform workspace select prod`.

**When to use.** Small team, simple infrastructure, easy to keep track of which workspace is active. A middle ground between "one state" and "stack-per-environment."

**Risks.** Easy to apply to the wrong workspace. The active workspace is a session-local setting, not a code property. Workspace mistakes are the most common IaC incident type for small teams.

## Environment-isolation patterns

### Separate AWS accounts / GCP projects per environment

**Pattern.** Dev, staging, prod live in different cloud accounts. IaC code provisions resources in the appropriate account based on configuration.

**When to use.** Strong isolation required (compliance, blast-radius). Default for production-grade setups.

**Strengths.** Cloud-level IAM separation; cost tracking per environment; experimental changes in dev can't reach prod.

### Single account, separate VPCs / namespaces

**Pattern.** All environments in one account, separated by VPC (network) and IAM policies.

**When to use.** Small organizations; budget constraints; bootstrap before multi-account.

**Risks.** A bad IAM policy can cross environment lines. Stricter discipline required.

### Tag-based separation

**Pattern.** Same account, resources tagged with environment.

**When to use.** Almost never for production. Acceptable for ad-hoc experimentation.

## State-backend patterns

### Remote state with locking (Terraform: S3 + DynamoDB)

```hcl
terraform {
  backend "s3" {
    bucket         = "company-tfstate"
    key            = "prod/network/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "tfstate-lock"
    encrypt        = true
  }
}
```

**Pattern.** State in cloud storage with object versioning; lock via DynamoDB (or equivalent).

**When to use.** Default for self-managed Terraform. AWS-native; cheap; well-understood.

### Terraform Cloud / Pulumi Cloud / managed backends

**Pattern.** Vendor manages state, locking, RBAC, audit, run history.

**When to use.** Want managed UX, RBAC, run history out of the box. Acceptable trade-off vs. self-managed.

**Risks.** Vendor lock-in; cost at scale.

### Hosted runners with state colocation (Spacelift, Atlantis)

**Pattern.** Runner is the source of state and the apply environment. PRs trigger plan; merges trigger apply.

**When to use.** Want GitOps-style flow with managed UX.

## Runner / apply-gate patterns

### GitHub Actions with OIDC

**Pattern.** Workflow assumes a cloud role via OIDC; runs plan on PR; runs apply on merge (or with manual approval gate for production).

**When to use.** Lightweight setup; GitHub-native; works for most teams.

**Discipline.**

- Plan workflow on PR open / sync.
- Apply workflow on merge to main, with environment protection rules for production.
- OIDC trust policy scopes which workflows / branches can assume which roles.

### Atlantis

**Pattern.** Self-hosted Terraform PR automation. Posts plan output on PRs; applies on `atlantis apply` PR comment.

**When to use.** Team prefers self-hosted; PR-comment-driven workflow.

### Terraform Cloud / Spacelift

**Pattern.** Managed runner with native PR integration, plan-and-apply UI, RBAC, policy-as-code.

**When to use.** Larger teams with policy-as-code needs (OPA, Sentinel).

### Manual local apply

**Pattern.** Developer runs `terraform apply` from their machine.

**When to use.** Bootstrap (before CI infrastructure exists). One-off recovery operations with full audit trail.

**Never use for.** Routine production changes. Multi-person teams.

## Secret-management patterns

### OIDC for cloud auth

```yaml
permissions:
  id-token: write
  contents: read

steps:
  - uses: aws-actions/configure-aws-credentials@<SHA>
    with:
      role-to-assume: arn:aws:iam::123456789012:role/github-deploy
      aws-region: us-east-1
```

**Pattern.** GitHub presents an OIDC JWT; AWS trust policy validates and issues short-lived credentials.

**When to use.** Default for new setups. Replace existing long-lived keys.

### External secret stores (Vault, AWS Secrets Manager, GCP Secret Manager)

**Pattern.** IaC code references secret by name; cloud provider pulls value at apply or runtime.

```hcl
data "aws_secretsmanager_secret_version" "db_pass" {
  secret_id = "prod/db/master-password"
}

resource "aws_db_instance" "main" {
  password = data.aws_secretsmanager_secret_version.db_pass.secret_string
  # ...
}
```

**When to use.** Default for any production secret. Provides rotation hooks, audit log, RBAC.

### SOPS-encrypted secrets in repo

**Pattern.** Secrets encrypted with KMS, stored in repo, decrypted at apply.

**When to use.** Air-gapped or self-hosted environments. Want git history of secret changes. Avoid for high-privilege production secrets.

### Sealed Secrets (Kubernetes)

**Pattern.** Secrets encrypted with a cluster public key, decryptable only by the cluster.

**When to use.** Kubernetes-native secret management; secrets stored in git but only the cluster can decrypt.

## Drift-handling patterns

### Scheduled plan with alerting

```yaml
on:
  schedule:
    - cron: '0 2 * * *'  # 02:00 UTC daily

jobs:
  drift-check:
    steps:
      - uses: actions/checkout@<SHA>
      - run: terraform init
      - id: plan
        run: |
          if ! terraform plan -detailed-exitcode -out=tfplan; then
            echo "drift=true" >> $GITHUB_OUTPUT
          fi
      - if: steps.plan.outputs.drift == 'true'
        run: |
          # Notify
          curl -X POST $SLACK_WEBHOOK -d '{"text": "Drift detected in prod"}'
```

**Pattern.** Daily plan checks for diff between code and reality. Non-zero diff alerts.

**When to use.** Default for production. Combines preventive (plan-and-apply discipline) with detective (drift catches what slipped through).

### Auto-remediation (cautious)

**Pattern.** Some teams auto-apply drift corrections. Dangerous outside narrow use cases.

**When to use.** Drift is from a known well-behaved source (e.g., a managed service auto-renews a cert; you update code, then auto-apply re-imports).

**When not.** Anything you couldn't undo. Default to alert-and-investigate.

## Anti-patterns reviewers should flag

| Anti-pattern | Why it's bad | Typical fix |
|---|---|---|
| Local state for shared infra | No locking; race conditions; lost work | Remote state with locking |
| `?ref=main` for module sources | Non-reproducible; cascading breakage | Pin versions: `?ref=v1.2.0` |
| Long-lived AWS access keys in CI | Breach blast radius; rotation discipline required | OIDC federation |
| Plaintext secrets in `*.tf` files | In git history forever; visible in plan output | External secret store; reference by name |
| `terraform apply --auto-approve` from a developer machine | No audit; no review; no lock guarantee | CI / runner with PR review and approval gate |
| Single root containing all environments and all concerns | Plan times minutes; blast radius enormous; team contention | Stack-per-environment; module-per-concern |
| `local-exec` running production-critical mutations | Defeats the declarative model; not idempotent | Custom provider; or a CI step outside IaC |
| Hardcoded environment in code (`provider "aws" { region = "us-east-1" }`) | Can't promote across regions | Variables / locals; per-environment configuration |
| `null_resource` with triggers that fire on every plan | Plan flapping; meaningless diffs | Remove the trigger; use explicit lifecycle |
| State file committed to git | Secrets in git history; lost locking | Remote state; `.gitignore` for `*.tfstate` |
| Resource names that aren't tag-able / discoverable | Hard to audit what's running in production | Naming convention + tags (env, owner, cost-center) |
| `count = 0` to "disable" a resource conditionally | Counts shift indexes; destroys other resources | `for_each` with explicit keys |
| Re-creating a resource on every apply (e.g., timestamp in name) | Production downtime; race conditions | `ignore_changes` lifecycle; or fix the source of churn |
| Cross-stack dependencies via copy-paste | Drift inevitable | Remote state data source; explicit contract |
| Apply without plan review | Unintended changes; data loss possible | Plan-and-review gate |
| One huge module that does "everything" | Untestable; un-reusable; conflicts on changes | Decompose into per-concern modules |
| Module without a version tag | Consumers can't pin; reproducibility broken | Tag versions; document compatibility |
| Module that takes 30+ inputs | Sign that it's not a single concern | Decompose; smaller modules with composed roots |
| `terraform refresh` as a routine operation | Hides real drift; trains team to ignore plan output | Investigate drift; don't paper over it |
| Workspaces used as environments without strict process | Apply-to-wrong-workspace incidents | Separate directories per environment |
| Manual `terraform state rm` to "fix" issues | Hides the underlying problem; future apply re-creates the resource | Investigate; document; recover with `import` if needed |

## Decision frames

When the IaC Designer faces a choice:

1. **What's the blast radius if this goes wrong?** Drives stack boundaries and apply gates.
2. **Who applies to production?** Drives runner choice and approval gates.
3. **What's the team's IaC maturity?** Beginner-friendly tooling (managed runner, simple workflow) vs. power-tool tooling (custom provider, modules, hosted state).
4. **What's the audit / compliance requirement?** Audit-grade IaC requires immutable plan logs, identity-tied applies, and drift detection — non-negotiable in regulated environments.
5. **What's the dependency between environments?** Promotion-driven (dev → staging → prod) vs. parallel (each environment self-managed) drives stack layout.

The Designer documents the stack layout, the runner, the apply gate, the secret-management approach, and the drift-detection cadence — in the per-layer Design subsection.
