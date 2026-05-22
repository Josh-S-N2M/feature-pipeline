# Recipes: Infrastructure as Code

Patterns for Terraform, OpenTofu, Pulumi, AWS CDK, and similar IaC tools on GitHub Actions. Common shape: validate on PR, plan on PR (with comment), apply on merge with environment protection.

## Table of contents

- [The core pattern](#the-core-pattern)
- [Terraform / OpenTofu](#terraform--opentofu)
- [Pulumi](#pulumi)
- [AWS CDK](#aws-cdk)
- [State management considerations](#state-management-considerations)
- [Drift detection](#drift-detection)
- [Multi-environment promotion](#multi-environment-promotion)

For a ready-to-use template, see `assets/templates/ci-iac-terraform.yml`.

## The core pattern

IaC pipelines typically have three flavors of run:

1. **Validate** (every PR): syntax, formatting, basic checks. Fast, no cloud creds.
2. **Plan** (every PR touching infra): connect to cloud, compute change set, post to PR for review. Read-only cloud access.
3. **Apply** (on merge to main): execute the plan. Write access. Wrapped in an `environment:` with required reviewers for prod.

This separation gives reviewers human-readable diff information before merging, and gates the actual infrastructure change behind merge + (optionally) approval.

## Terraform / OpenTofu

(OpenTofu is a fork of Terraform. The workflow is essentially identical; substitute `tofu` for `terraform` and use [opentofu/setup-opentofu](https://github.com/opentofu/setup-opentofu) instead.)

### Setup

```yaml
- uses: actions/checkout@v6
- uses: hashicorp/setup-terraform@SHA   # pin to current SHA
  with:
    terraform_version: 1.10.0
    terraform_wrapper: true     # default; wraps stdout for outputs
```

### Validate workflow (PR)

```yaml
name: Terraform Validate
on:
  pull_request:
    paths: ['terraform/**']

permissions:
  contents: read
  pull-requests: write
  id-token: write

jobs:
  validate:
    runs-on: ubuntu-latest
    defaults:
      run:
        working-directory: ./terraform
    steps:
      - uses: actions/checkout@v6
      - uses: hashicorp/setup-terraform@SHA
        with: { terraform_version: 1.10.0 }
      - run: terraform fmt -check -recursive
      - run: terraform init -backend=false
      - run: terraform validate
```

`terraform init -backend=false` skips backend configuration — useful for validate, where you don't need cloud credentials.

### Plan workflow (PR)

```yaml
name: Terraform Plan
on:
  pull_request:
    paths: ['terraform/**']

permissions:
  contents: read
  pull-requests: write
  id-token: write

concurrency:
  group: terraform-plan-${{ github.ref }}
  cancel-in-progress: true

jobs:
  plan:
    runs-on: ubuntu-latest
    environment: terraform-readonly      # has read-only AWS role
    defaults:
      run:
        working-directory: ./terraform
    steps:
      - uses: actions/checkout@v6
      - uses: aws-actions/configure-aws-credentials@SHA
        with:
          role-to-assume: arn:aws:iam::ACCOUNT:role/terraform-readonly
          aws-region: us-east-1
      - uses: hashicorp/setup-terraform@SHA
        with: { terraform_version: 1.10.0 }
      - run: terraform init
      - id: plan
        run: |
          terraform plan -no-color -out=tfplan 2>&1 | tee plan.txt
          echo "exitcode=${PIPESTATUS[0]}" >> "$GITHUB_OUTPUT"
        continue-on-error: true
      - name: Comment plan on PR
        uses: actions/github-script@SHA
        env:
          PLAN_TEXT: ${{ steps.plan.outputs.stdout }}
        with:
          script: |
            const fs = require('fs');
            const plan = fs.readFileSync('terraform/plan.txt', 'utf8');
            const truncated = plan.length > 60000 ? plan.slice(0, 60000) + '\n\n...(truncated)' : plan;
            const body = `### Terraform Plan\n\n<details><summary>Show plan</summary>\n\n\`\`\`hcl\n${truncated}\n\`\`\`\n\n</details>`;
            github.rest.issues.createComment({
              issue_number: context.issue.number,
              owner: context.repo.owner,
              repo: context.repo.repo,
              body
            });
      - if: steps.plan.outputs.exitcode != '0'
        run: exit 1
```

Note the **read-only IAM role** — the plan workflow doesn't need write access; revoking it limits blast radius.

### Apply workflow (post-merge)

```yaml
name: Terraform Apply
on:
  push:
    branches: [main]
    paths: ['terraform/**']

permissions:
  contents: read
  id-token: write

concurrency:
  group: terraform-apply
  cancel-in-progress: false        # never cancel an apply mid-flight

jobs:
  apply:
    runs-on: ubuntu-latest
    environment: terraform-prod    # required reviewers configured here
    defaults:
      run:
        working-directory: ./terraform
    steps:
      - uses: actions/checkout@v6
      - uses: aws-actions/configure-aws-credentials@SHA
        with:
          role-to-assume: arn:aws:iam::ACCOUNT:role/terraform-apply
          aws-region: us-east-1
      - uses: hashicorp/setup-terraform@SHA
        with: { terraform_version: 1.10.0 }
      - run: terraform init
      - run: terraform apply -auto-approve
```

The `terraform-prod` environment has:
- Required reviewers (manual approval gate).
- A separate IAM role with write permissions (scoped via OIDC trust to environment-name).
- Branch restrictions (only `main`).

### Tooling additions

- **tflint** — `terraform-linters/setup-tflint@SHA` then `tflint --recursive`.
- **tfsec / trivy** — security scanner. `aquasecurity/tfsec-action@SHA` or `aquasecurity/trivy-action@SHA` with `scan-type: config`.
- **checkov** — broader policy scanner. `bridgecrewio/checkov-action@SHA`.
- **terraform-docs** — auto-generate module docs.

Combine these in the validate job for a comprehensive check.

## Pulumi

```yaml
permissions:
  contents: read
  id-token: write
  pull-requests: write

jobs:
  preview:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-node@v6
        with: { node-version: '22', cache: npm }     # if Pulumi program is TS/JS
      - run: npm ci
      - uses: aws-actions/configure-aws-credentials@SHA
        with:
          role-to-assume: arn:aws:iam::ACCOUNT:role/pulumi-readonly
          aws-region: us-east-1
      - uses: pulumi/actions@SHA   # pin to current SHA
        with:
          command: preview
          stack-name: my-org/staging
          comment-on-pr: true
        env:
          PULUMI_ACCESS_TOKEN: ${{ secrets.PULUMI_ACCESS_TOKEN }}
```

Apply (on push to main) uses `command: up` with a write-scoped role.

For Pulumi state stored in S3 / Azure Blob / GCS, OIDC works for state access too — no Pulumi Cloud token required.

## AWS CDK

```yaml
permissions:
  contents: read
  id-token: write
  pull-requests: write

jobs:
  diff:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-node@v6
        with: { node-version: '22', cache: npm }
      - run: npm ci
      - uses: aws-actions/configure-aws-credentials@SHA
        with:
          role-to-assume: arn:aws:iam::ACCOUNT:role/cdk-readonly
          aws-region: us-east-1
      - run: npx cdk diff --all --no-color > diff.txt
      - uses: actions/github-script@SHA
        env: { DIFF_TEXT: '$(cat diff.txt)' }
        with:
          script: |
            const fs = require('fs');
            const diff = fs.readFileSync('diff.txt', 'utf8');
            const body = `### CDK Diff\n\n<details><summary>Show diff</summary>\n\n\`\`\`\n${diff}\n\`\`\`\n\n</details>`;
            github.rest.issues.createComment({ issue_number: context.issue.number, owner: context.repo.owner, repo: context.repo.repo, body });

  deploy:
    if: github.event_name == 'push' && github.ref == 'refs/heads/main'
    needs: diff
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-node@v6
        with: { node-version: '22', cache: npm }
      - run: npm ci
      - uses: aws-actions/configure-aws-credentials@SHA
        with:
          role-to-assume: arn:aws:iam::ACCOUNT:role/cdk-deploy
          aws-region: us-east-1
      - run: npx cdk deploy --all --require-approval never --no-color
```

`--require-approval never` is necessary for unattended runs; the human approval gate is the GitHub environment.

### CDK bootstrap

The cdk-deploy role needs permission to assume the CDK bootstrap roles (`cdk-hnb659fds-deploy-role-*`). The simplest pattern: `cdk-deploy` is itself the bootstrap deploy role's principal.

## State management considerations

- **State backends:** never store state locally (loses on every CI run). Use S3 + DynamoDB locking, Azure Storage with state-locking, GCS with locking, Terraform Cloud, or Pulumi Cloud.
- **State locks:** the `concurrency:` group should align with the state backend's lock granularity. One state file = one concurrency group, even if multiple workflows write to it.
- **State drift between workflows:** if multiple workflows can apply (e.g., a manual workflow and a scheduled drift-correction), align their concurrency groups so they can't run simultaneously.

## Drift detection

A scheduled workflow that runs `terraform plan` and alerts if there's drift:

```yaml
on:
  schedule: [{ cron: '0 8 * * 1-5' }]   # weekdays 08:00 UTC
  workflow_dispatch:

permissions: { id-token: write, contents: read }

jobs:
  drift:
    runs-on: ubuntu-latest
    environment: terraform-readonly
    steps:
      - uses: actions/checkout@v6
      - uses: aws-actions/configure-aws-credentials@SHA
        with: { role-to-assume: arn:aws:iam::ACCOUNT:role/tf-readonly, aws-region: us-east-1 }
      - uses: hashicorp/setup-terraform@SHA
        with: { terraform_version: 1.10.0 }
      - run: terraform init
      - id: plan
        run: |
          terraform plan -detailed-exitcode -no-color || exit_code=$?
          echo "exit_code=${exit_code:-0}" >> "$GITHUB_OUTPUT"
      - if: steps.plan.outputs.exit_code == '2'
        # exit code 2 = changes detected; 0 = no changes; 1 = error
        run: ./scripts/notify-drift.sh
```

`-detailed-exitcode` distinguishes "no changes" (0) from "changes detected" (2) — useful for drift detection.

## Multi-environment promotion

Promote infrastructure changes through environments using stacks/workspaces:

```yaml
strategy:
  matrix:
    env:
      - { name: dev, role: arn:aws:iam::DEV_ACCT:role/tf-apply, stack: dev }
      - { name: stage, role: arn:aws:iam::STAGE_ACCT:role/tf-apply, stack: stage }
      - { name: prod, role: arn:aws:iam::PROD_ACCT:role/tf-apply, stack: prod }
  max-parallel: 1     # sequence dev → stage → prod

jobs:
  apply:
    needs: validate
    runs-on: ubuntu-latest
    environment: ${{ matrix.env.name }}
    steps:
      - uses: actions/checkout@v6
      - uses: aws-actions/configure-aws-credentials@SHA
        with: { role-to-assume: ${{ matrix.env.role }}, aws-region: us-east-1 }
      - uses: hashicorp/setup-terraform@SHA
        with: { terraform_version: 1.10.0 }
      - run: |
          terraform init
          terraform workspace select ${{ matrix.env.stack }}
          terraform apply -auto-approve
```

Each environment's deployment protection rules add the human gates between stages.

## Common gotchas

- **State backend credentials in CI** — must be configured before `init`. With OIDC and AWS S3 backend, `aws-actions/configure-aws-credentials` runs first.
- **Workspaces vs separate state files** — workspaces share resource definitions; separate state files allow per-env divergence. Pick one and document the convention.
- **`terraform init` re-downloads providers every run** unless cached. Cache `.terraform/` (but be wary: provider plugins are large and version-specific).
- **Plans go stale** — a plan generated 2 hours ago may not be valid against current state. Apply soon after plan, or re-plan in the apply workflow.
- **Don't store sensitive variables in tfvars files in the repo** — use cloud-native secret backends or `terraform_remote_state` from a secured state.
- **OpenTofu and Terraform aren't binary-compatible after 1.6** — pick one. Mixing breaks state.
