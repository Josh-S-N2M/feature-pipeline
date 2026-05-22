# IaC Design Principles

## Contents

- Principle 1: State is the source of truth; never edit by hand
- Principle 2: Plan before apply, always
- Principle 3: Idempotency by design
- Principle 4: Blast-radius minimization
- Principle 5: Drift detection on a schedule
- Principle 6: Secrets never in state plaintext; OIDC for cloud auth
- Principle 7: Modules versioned semantically; consumers pin
- Principle 8: Prefer declarative resources over `local-exec`

## Principle 1: State is the source of truth; never edit by hand

The IaC tool's state file is what the tool believes about reality. Every operation (plan, apply, destroy) reads state, compares against code and reality, and produces a diff. Editing the state file directly is the path to operational chaos.

The Designer's discipline:

- **Remote state, locked.** S3 + DynamoDB (Terraform), GCS bucket with object versioning, or managed (Terraform Cloud, Pulumi Cloud). Never local state for shared infrastructure.
- **State backups enabled.** Object versioning, point-in-time recovery, or whatever the backend supports.
- **Manual state surgery is a process, not a habit.** `terraform state mv` / `import` / `rm` are recovery tools, not routine operations. When used, the change is reviewed, recorded, and tested before being applied to production state.
- **State files in source control: NO.** State contains secrets and is mutable; commit state files and you've lost both the security and the locking guarantees.

For Pulumi: Pulumi's state is similarly authoritative. The same discipline applies (remote backend, no manual edits).

For Crossplane / Kubernetes-native IaC: state lives in the cluster's etcd. Backup discipline is part of cluster operations.

## Principle 2: Plan before apply, always

Every change runs `plan` first; a human or automated rule reviews the plan; then `apply` runs.

Why this matters:

- **Apply is irreversible** for many resources. A `terraform apply` that deletes the production database doesn't have an undo button.
- **Plan output shows the diff.** Reviewing the plan is the only way to catch unintended changes (e.g., a typo causing a destroy/replace instead of an update).
- **The plan is the contract.** What was planned is what was applied. If apply diverges, that's an incident.

The Designer specifies the plan-and-apply discipline in the per-layer subsection:

- **Where plan runs.** CI on every PR; runner (TF Cloud, Spacelift, Atlantis) on merge.
- **Who reviews.** PR review for code; plan output reviewed by reviewer.
- **Auto-apply rules.** Some environments may auto-apply (dev); production never auto-applies without an explicit approval step.
- **Plan output retention.** Plan artifacts archived for audit; tied to the PR.

Anti-patterns:

- Developer runs `terraform apply` locally on production. No audit, no review, no lock against concurrent applies.
- `--auto-approve` in CI without a manual gate for production.
- Plan output not displayed in PR.

## Principle 3: Idempotency by design

The same IaC code applied twice produces the same result. Runs are repeatable; retries are safe.

Declarative IaC tools are mostly idempotent by construction — they reconcile reality to code. But the Designer avoids patterns that break idempotency:

- **`local-exec` provisioners** that mutate state outside of IaC (running scripts, calling APIs). These run on first apply but not on re-apply; if the script's effect is "set a value," the value can drift.
- **`null_resource` with triggers** that re-run on every plan. These are escape hatches; minimize.
- **External data sources** that change between runs without code changes. Cause plan flapping.

When non-idempotent operations are unavoidable (e.g., a one-time database initialization), the Designer:

- Isolates them in a dedicated resource with explicit lifecycle (`create_before_destroy`, `ignore_changes`).
- Documents the non-idempotency in the per-layer subsection.
- Provides a manual override path (a flag to skip on subsequent runs).

## Principle 4: Blast-radius minimization

When something goes wrong, what's the worst that can happen? IaC blast radius is bounded by:

- **State boundaries.** What's in this state file vs. another. A corrupt apply only affects what the apply was touching.
- **Apply scope.** A plan that touches 5 resources can only break 5 resources.
- **Environment isolation.** Dev, staging, prod in separate stacks; an apply in dev can never affect prod.

The Designer's defaults:

- **Per-environment stacks.** Separate state file per environment. Workspaces (Terraform) are an acceptable middle ground but harder to govern (same code, different state).
- **Per-concern modules within a stack.** Network module, database module, Kubernetes module. Each can be applied independently.
- **Avoid one giant root.** A root `main.tf` that includes every module in every environment is the operational equivalent of a single-shard database — every change touches the whole.
- **Cross-stack references via data sources or remote-state lookups**, not via embedding one stack in another. Loose coupling between stacks.

Example layout:

```
infra/
├── environments/
│   ├── dev/
│   │   ├── main.tf          # composes modules for dev
│   │   ├── backend.tf       # state config for dev
│   │   └── variables.tf
│   ├── staging/
│   └── prod/
└── modules/
    ├── network/
    ├── database/
    └── kubernetes/
```

Each environment has its own state; modules are versioned and consumed via `source = "git::...?ref=v1.2.0"` or a registry.

## Principle 5: Drift detection on a schedule

Even with strict apply discipline, drift happens:

- Someone fixes an incident by clicking in the console; forgets to update code.
- A managed service auto-rotates a setting (TLS certificate, version).
- A different IaC tool or scripted automation touches the same resources.

The Designer specifies drift detection:

- **Schedule.** Nightly `terraform plan` (or `pulumi preview`) against production state, comparing code to reality.
- **Output.** Plan output captured. Non-zero diff triggers an alert (Slack, PagerDuty, email).
- **Triage.** A non-zero drift is investigated within a documented window: either the code is updated (drift was intentional and good) or the resource is corrected (drift was accidental).

This Acceptance Criterion is concrete:

- The system shall run `terraform plan` against the production state at 02:00 UTC daily.
- When the scheduled plan produces a non-zero diff, the system shall alert `#infra-drift` within 60 seconds.

## Principle 6: Secrets never in state plaintext; OIDC for cloud auth

Two related concerns: how the IaC tool authenticates to clouds, and how secrets reach the resources being provisioned.

**Cloud authentication.**

- **Long-lived AWS/GCP/Azure keys stored in CI as secrets.** Default for years; significant breach blast radius if leaked. Static key in CI → access to your cloud.
- **OIDC federation from GitHub Actions (or equivalent) to AWS / GCP / Azure / HashiCorp Vault.** GitHub presents a JWT; the cloud's trust policy validates and issues short-lived credentials scoped to the workflow.

The Designer specifies OIDC where supported. Long-lived keys are an interim only.

**Secrets reaching resources.**

- **Never plaintext in code.** No `password = "hunter2"` in `main.tf`.
- **Never plaintext in state.** Even with remote state, secrets in plaintext are exposed to anyone with state read access. Some resources (e.g., RDS master password) end up in state regardless — the discipline is to limit state access and rotate frequently.
- **External secret stores.** Vault, AWS Secrets Manager, GCP Secret Manager. The IaC code references the secret by name; the actual value is in the store. On apply, the cloud provider pulls the secret at runtime.
- **Encrypted secrets in repo (last resort).** SOPS, sealed-secrets, encrypted with cloud KMS. Acceptable for low-privilege secrets where an external store would be over-engineering.

The Designer documents the secret-management approach for each environment.

## Principle 7: Modules versioned semantically; consumers pin

Modules are the unit of reuse. They have:

- **A versioned source.** Git tag (`?ref=v1.2.0`) or registry entry (Terraform Registry, Pulumi Package). Never `?ref=main`.
- **Semantic versioning.** Major version bumps for breaking changes; consumers pin majors.
- **A contract documented in the module's README.** Inputs (variables), outputs, side effects, version compatibility.

Anti-patterns:

- `?ref=main` — consumers pull whatever HEAD is at apply time. Non-reproducible; a module change breaks every consumer simultaneously.
- Modules that aren't independently testable. The module's own CI should run a `plan` against a test stack.
- Module versions never bumped past v1.0.0. The consumer-author contract is invisible.

## Principle 8: Prefer declarative resources over `local-exec`

Declarative IaC tools express infrastructure as "what should exist," and the tool reconciles. `local-exec` (or equivalent provisioner / shell-out) is the escape hatch: run an arbitrary shell command on apply.

`local-exec` is sometimes necessary (initializing a managed service via its CLI, running a database migration), but it should be rare:

- Loses idempotency unless the script is itself idempotent.
- Loses the diff (the tool can't show what `local-exec` will do until it runs).
- Loses error reporting (the failure looks like "the apply failed" without context).
- Local-only dependencies (the `aws` CLI must be installed; the shell must have permissions).

When `local-exec` is unavoidable, the Designer:

- Justifies the use in the per-layer subsection.
- Wraps the operation in a dedicated `null_resource` (Terraform) with explicit triggers.
- Documents the rollback path (what to undo if the apply fails partway).
- Considers whether a custom Terraform provider or a Pulumi dynamic resource would be cleaner.

A common alternative: instead of `local-exec` running migrations, the migration is a job in CI (a separate step that runs after `apply`). Keeps the IaC declarative and gives the migration a proper execution context.
