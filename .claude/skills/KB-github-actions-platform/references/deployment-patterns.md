# Deployment Patterns

Per-target playbooks for the common deployment surfaces. Each section is self-contained: cloud-side setup steps, workflow patterns, and gotchas.

## Table of contents

- [AWS via OIDC](#aws-via-oidc)
- [Azure via OIDC](#azure-via-oidc)
- [GCP via Workload Identity Federation](#gcp-via-workload-identity-federation)
- [Netlify](#netlify)
- [Supabase](#supabase)
- [GitHub Pages](#github-pages)
- [Container registries (GHCR, Docker Hub, ECR, GAR)](#container-registries)
- [npm, PyPI](#npm-pypi)

For full template files, see `assets/templates/`.

## AWS via OIDC

### Cloud-side setup (one-time)

1. Create an OIDC identity provider in IAM:
   - Provider URL: `https://token.actions.githubusercontent.com`
   - Audience: `sts.amazonaws.com`

2. Create an IAM role with a trust policy scoped to your repo and ideally to a specific branch or environment:

```json
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Principal": { "Federated": "arn:aws:iam::ACCOUNT:oidc-provider/token.actions.githubusercontent.com" },
    "Action": "sts:AssumeRoleWithWebIdentity",
    "Condition": {
      "StringEquals": {
        "token.actions.githubusercontent.com:aud": "sts.amazonaws.com"
      },
      "StringLike": {
        "token.actions.githubusercontent.com:sub": "repo:my-org/my-repo:environment:production"
      }
    }
  }]
}
```

The `sub:` claim is what scopes which workflows can assume the role. Common patterns:
- `repo:my-org/my-repo:ref:refs/heads/main` — only main branch
- `repo:my-org/my-repo:environment:production` — only when `environment: production` is declared
- `repo:my-org/my-repo:pull_request` — for PR-triggered workflows
- `repo:my-org/*:ref:refs/heads/main` — any repo in the org, on main

Prefer environment-based scoping with deployment protection rules — gives you human approval gates.

### Workflow

```audit-example -- Documents the canonical GitHub Actions OIDC workflow for GCP Workload Identity Federation; contains long Google IAM resource paths that the auditor's base64 detector matches against (OB-1: 60+ char run of alphanumeric/slash). The paths are documentation of Google IAM resource-path format, not encoded payloads.
permissions:
  id-token: write
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v6
      - uses: aws-actions/configure-aws-credentials@e3dd6a429d7300a6a4c196c26e071d42e0343502  # v4.0.2
        with:
          role-to-assume: arn:aws:iam::123456789012:role/github-deploy
          role-session-name: gh-${{ github.run_id }}
          aws-region: us-east-1
      - run: aws s3 sync ./dist s3://my-bucket/
```

### Common gotchas

- The role must trust the *exact* `sub` claim — typos in the trust policy are the #1 cause of `AccessDenied`.
- If you use `environment:` in the workflow, the OIDC token's `sub` includes the environment; if the trust policy expects `ref:refs/heads/main` instead, it won't match.
- For multi-region deploys, the role is per-account (or per-AWS-org). Region is per-call.

See template: `assets/templates/cd-aws-oidc.yml`.

## Azure via OIDC

### Cloud-side setup

1. Register an Azure AD application (Microsoft Entra ID).
2. On the app, add a federated credential:
   - Issuer: `https://token.actions.githubusercontent.com`
   - Subject identifier: `repo:my-org/my-repo:environment:production` (or a different scope)
   - Audience: `api://AzureADTokenExchange`
3. Assign the app's service principal to the appropriate Azure subscription/resource group with required RBAC roles.
4. Capture the app's client ID, tenant ID, subscription ID — store as repo or environment secrets (these are not actually secret, but it's the convention).

### Workflow

```audit-example -- Documents the canonical GitHub Actions OIDC workflow for GCP Workload Identity Federation; contains long Google IAM resource paths that the auditor's base64 detector matches against (OB-1: 60+ char run of alphanumeric/slash). The paths are documentation of Google IAM resource-path format, not encoded payloads.
permissions:
  id-token: write
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v6
      - uses: azure/login@8c334a195cbb38e46038007b304988d888bf676a   # pin to current SHA
        with:
          client-id: ${{ secrets.AZURE_CLIENT_ID }}
          tenant-id: ${{ secrets.AZURE_TENANT_ID }}
          subscription-id: ${{ secrets.AZURE_SUBSCRIPTION_ID }}
      - run: az account show
      - run: az webapp deploy --resource-group rg --name app --src-path ./dist
```

See template: `assets/templates/cd-azure-oidc.yml`.

## GCP via Workload Identity Federation

### Cloud-side setup

1. Create a Workload Identity Pool.
```audit-example -- Documents the canonical Google Cloud Workload Identity Federation OIDC-provider configuration; contains long Google IAM resource paths (projects/.../workloadIdentityPools/.../providers/...) that the auditor's base64 detector OB-1 matches against. Pedagogical reference for OIDC setup, not encoded payloads.
2. Create an OIDC provider in the pool:
   - Issuer URI: `https://token.actions.githubusercontent.com`
   - Allowed audiences: `https://iam.googleapis.com/projects/PROJECT_NUMBER/locations/global/workloadIdentityPools/POOL/providers/PROVIDER`
   - Attribute mapping: `google.subject=assertion.sub`, `attribute.repository=assertion.repository`, etc.
   - Attribute condition (critical): `assertion.repository == 'my-org/my-repo'`
```
3. Create a service account with the necessary roles.
4. Grant the workload identity pool permission to impersonate the service account: `roles/iam.workloadIdentityUser`, scoped to your repo via the attribute.

### Workflow

```audit-example -- Documents the canonical GitHub Actions OIDC workflow for GCP Workload Identity Federation; contains long Google IAM resource paths that the auditor's base64 detector matches against (OB-1: 60+ char run of alphanumeric/slash). The paths are documentation of Google IAM resource-path format, not encoded payloads.
permissions:
  id-token: write
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v6
      - id: auth
        uses: google-github-actions/auth@SHA   # pin to current SHA
        with:
          workload_identity_provider: projects/123/locations/global/workloadIdentityPools/gh/providers/gh-provider
          service_account: deployer@PROJECT.iam.gserviceaccount.com
      - uses: google-github-actions/setup-gcloud@SHA
      - run: gcloud run deploy my-service --image gcr.io/PROJECT/my-service:${{ github.sha }} --region us-central1
```

See template: `assets/templates/cd-gcp-oidc.yml`.

## Netlify

Netlify can either build itself (you point it at the repo) or accept pre-built artifacts from GitHub Actions. The latter is more flexible — you control the build environment.

### Required secrets

- `NETLIFY_AUTH_TOKEN` — personal access token from Netlify user settings.
- `NETLIFY_SITE_ID` — found in Site settings → Site information.

### Workflow (using Netlify CLI directly — simpler, no third-party action)

```yaml
name: Deploy to Netlify
on:
  push: { branches: [main] }
  pull_request:

permissions:
  contents: read
  pull-requests: write    # for PR comments with preview URL

jobs:
  deploy:
    runs-on: ubuntu-latest
    concurrency:
      group: netlify-${{ github.head_ref || github.ref }}
      cancel-in-progress: ${{ github.event_name == 'pull_request' }}
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-node@v6
        with: { node-version: '22', cache: npm }
      - run: npm ci
      - run: npm run build
      - name: Deploy
        env:
          NETLIFY_AUTH_TOKEN: ${{ secrets.NETLIFY_AUTH_TOKEN }}
          NETLIFY_SITE_ID: ${{ secrets.NETLIFY_SITE_ID }}
        run: |
          if [[ "${{ github.event_name }}" == "push" && "${{ github.ref }}" == "refs/heads/main" ]]; then
            npx netlify deploy --dir=dist --prod --message "Deploy ${{ github.sha }}"
          else
            npx netlify deploy --dir=dist --alias deploy-preview-${{ github.event.pull_request.number }} \
              --message "Preview ${{ github.sha }}" --json > deploy.json
            url=$(jq -r '.deploy_url' deploy.json)
            echo "preview_url=$url" >> "$GITHUB_OUTPUT"
          fi
```

### Workflow (using `nwtgck/actions-netlify` — community action)

```yaml
- uses: nwtgck/actions-netlify@SHA   # pin to current SHA
  with:
    publish-dir: ./dist
    production-branch: main
    github-token: ${{ secrets.GITHUB_TOKEN }}
    deploy-message: 'From GitHub Actions'
    enable-pull-request-comment: true
    overwrites-pull-request-comment: true
  env:
    NETLIFY_AUTH_TOKEN: ${{ secrets.NETLIFY_AUTH_TOKEN }}
    NETLIFY_SITE_ID: ${{ secrets.NETLIFY_SITE_ID }}
```

The community action handles PR commenting nicely; the CLI approach gives you full control.

See template: `assets/templates/cd-netlify.yml`.

## Supabase

Supabase deployments typically have two parts: database migrations and Edge Functions. Both managed via the Supabase CLI.

### Required secrets

- `SUPABASE_ACCESS_TOKEN` — personal access token (account-level).
- `SUPABASE_PROJECT_ID` — your project's reference ID (e.g., `abcdefghijklmno`).
- `SUPABASE_DB_PASSWORD` — for migration commands that connect to the database directly.

### Workflow

```yaml
name: Deploy to Supabase
on:
  push:
    branches: [main]

permissions:
  contents: read

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment: production
    concurrency:
      group: supabase-prod
      cancel-in-progress: false
    steps:
      - uses: actions/checkout@v6
      - uses: supabase/setup-cli@SHA   # pin to current SHA
        with:
          version: latest
      - name: Link to project
        run: supabase link --project-ref "$PROJECT_ID"
        env:
          SUPABASE_ACCESS_TOKEN: ${{ secrets.SUPABASE_ACCESS_TOKEN }}
          PROJECT_ID: ${{ secrets.SUPABASE_PROJECT_ID }}
      - name: Push database migrations
        env:
          SUPABASE_ACCESS_TOKEN: ${{ secrets.SUPABASE_ACCESS_TOKEN }}
          SUPABASE_DB_PASSWORD: ${{ secrets.SUPABASE_DB_PASSWORD }}
        run: supabase db push
      - name: Deploy Edge Functions
        env:
          SUPABASE_ACCESS_TOKEN: ${{ secrets.SUPABASE_ACCESS_TOKEN }}
        run: supabase functions deploy --project-ref "${{ secrets.SUPABASE_PROJECT_ID }}"
```

### Notes

- `supabase db push` applies migrations from `supabase/migrations/`. Run it before function deploys so the schema is current.
- For PR previews, Supabase has the [Branching feature](https://supabase.com/docs/guides/platform/branching) — branch databases that ephemerally exist for a PR.
- Set up branching with the GitHub integration in the Supabase dashboard rather than a custom workflow.

See template: `assets/templates/cd-supabase.yml`.

## GitHub Pages

```yaml
permissions:
  contents: read
  pages: write
  id-token: write     # for the new Pages deployment flow (not classic gh-pages branch)

jobs:
  deploy:
    runs-on: ubuntu-latest
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-node@v6
        with: { node-version: '22', cache: npm }
      - run: npm ci && npm run build
      - uses: actions/upload-pages-artifact@SHA
        with: { path: ./dist }
      - id: deployment
        uses: actions/deploy-pages@SHA
```

Settings → Pages → Source → "GitHub Actions". The classic `gh-pages` branch flow is legacy.

## Container registries

### GHCR (GitHub Container Registry)

Built-in; uses the workflow's `GITHUB_TOKEN`.

```yaml
permissions:
  contents: read
  packages: write
  attestations: write
  id-token: write    # for attestations

jobs:
  build-push:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: docker/login-action@SHA
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}
      - uses: docker/setup-buildx-action@SHA
      - id: meta
        uses: docker/metadata-action@SHA
        with:
          images: ghcr.io/${{ github.repository }}
          tags: |
            type=ref,event=branch
            type=ref,event=pr
            type=semver,pattern={{version}}
            type=sha,format=long
      - id: push
        uses: docker/build-push-action@SHA
        with:
          context: .
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          platforms: linux/amd64,linux/arm64
          cache-from: type=gha
          cache-to: type=gha,mode=max
      - uses: actions/attest-build-provenance@SHA
        with:
          subject-name: ghcr.io/${{ github.repository }}
          subject-digest: ${{ steps.push.outputs.digest }}
          push-to-registry: true
```

### ECR (AWS)

Use OIDC + `aws-actions/amazon-ecr-login@SHA`.

### GAR (Google Artifact Registry)

Use Workload Identity Federation + `gcloud auth configure-docker`.

See template: `assets/templates/release-docker-ghcr.yml`.

## npm, PyPI

Both support OIDC trusted publishing — no API tokens needed.

### npm (with provenance)

```yaml
permissions:
  contents: read
  id-token: write    # for provenance

jobs:
  publish:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-node@v6
        with:
          node-version: '22'
          registry-url: 'https://registry.npmjs.org'
      - run: npm ci
      - run: npm run build
      - run: npm publish --provenance --access public
        env:
          NODE_AUTH_TOKEN: ${{ secrets.NPM_TOKEN }}    # still needed; OIDC for provenance only
```

For full OIDC (no NPM_TOKEN), use npm Trusted Publishers configured at npmjs.com.

### PyPI (Trusted Publishing)

```yaml
permissions:
  contents: read
  id-token: write

jobs:
  publish:
    runs-on: ubuntu-latest
    environment: pypi
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-python@v6
        with: { python-version: '3.13' }
      - run: pip install build && python -m build
      - uses: pypa/gh-action-pypi-publish@SHA   # pin
        # No password needed when configured as a Trusted Publisher
```

PyPI side: project Settings → Publishing → Add a trusted publisher pointing to your repo, workflow, and (optionally) environment.

See templates: `assets/templates/release-npm.yml`, `assets/templates/release-pypi.yml`.
