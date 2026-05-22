# Migration

Migrating from another CI system to GitHub Actions. Per-system mapping tables, common pitfalls, and the official tooling.

## Table of contents

- [GitHub Actions Importer](#github-actions-importer)
- [Concept mapping (cheat sheet)](#concept-mapping-cheat-sheet)
- [From Jenkins](#from-jenkins)
- [From CircleCI](#from-circleci)
- [From GitLab CI](#from-gitlab-ci)
- [From Travis CI](#from-travis-ci)
- [From Azure DevOps Pipelines](#from-azure-devops-pipelines)
- [Migration strategy](#migration-strategy)

## GitHub Actions Importer

GitHub provides an [official importer](https://github.com/github/gh-actions-importer) (`gh actions-importer`) that audits and converts pipelines from Jenkins, CircleCI, GitLab, Travis, Azure DevOps, Bitbucket, and BuildKite. Use it as a starting point — the output usually needs cleanup, but it gets you 60–80% of the way.

```bash
gh extension install github/gh-actions-importer
gh actions-importer configure
gh actions-importer audit jenkins --output-dir tmp/audit
gh actions-importer dry-run jenkins --source-url https://jenkins.example.com/job/myjob --output-dir tmp/dry-run
gh actions-importer migrate jenkins --source-url https://jenkins.example.com/job/myjob --target-url https://github.com/my-org/my-repo
```

The output PR contains the generated workflow plus comments where the importer wasn't sure how to translate something.

## Concept mapping (cheat sheet)

| Concept | Jenkins | CircleCI | GitLab CI | Travis | Azure DevOps | GitHub Actions |
|---|---|---|---|---|---|---|
| Pipeline file | `Jenkinsfile` | `.circleci/config.yml` | `.gitlab-ci.yml` | `.travis.yml` | `azure-pipelines.yml` | `.github/workflows/*.yml` |
| Trigger | `triggers {}` | `triggers:` | `rules:`, `only:` | `branches:` | `trigger:`, `pr:` | `on:` |
| Stage / job | `stage` | `job` | `job` (with `stage:`) | `stages:` | `stage`, `job` | `job` |
| Step | `step` (sh, etc.) | `step` | script command | `script:` array | `task`, `script` | `step` (`run:` or `uses:`) |
| Worker / runner | `agent` | `executor` / `docker` | `tags:`, `image:` | `os:`, `dist:` | `pool:`, `vmImage:` | `runs-on:`, `container:` |
| Reusable logic | shared library | orb | `include:`, anchors | (none) | template | composite action / reusable workflow |
| Secrets | credentials store | context | masked variables | encrypted env | variable group, key vault | repo/env/org secrets |
| Artifacts | `archiveArtifacts` | `store_artifacts` | `artifacts:` | (limited) | `publish` | `actions/upload-artifact` |
| Cache | `cache:` plugin | `save_cache`/`restore_cache` | `cache:` | `cache:` | `Cache@2` task | `actions/cache` |
| Matrix | parallel stages | matrix in workflow | parallel matrix | matrix | strategy.matrix | `strategy.matrix` |
| Env vars | `environment {}` | `environment:` | `variables:` | `env:` | `variables:` | `env:` |
| Conditional | `when {}` | `filters:`, `when:` | `rules:` | `if:` | `condition:` | `if:` |

## From Jenkins

### Mental shifts

- **No long-lived agents.** Each job gets a fresh runner. State that lived between Jenkins builds (workspace caches, downloaded files) needs explicit caching or artifacts.
- **No master/orchestrator.** The closest equivalents are reusable workflows (for shared multi-job logic) and `workflow_run` (for chaining workflows).
- **Declarative > scripted.** Most Jenkinsfile scripted-pipeline patterns become declarative YAML. Loops and dynamic logic move into shell scripts within `run:` blocks.

### Common translations

```groovy
// Jenkinsfile
pipeline {
  agent { docker 'node:22' }
  stages {
    stage('Build') {
      steps {
        sh 'npm ci'
        sh 'npm test'
      }
    }
    stage('Deploy') {
      when { branch 'main' }
      steps {
        withCredentials([string(credentialsId: 'aws-key', variable: 'AWS_ACCESS_KEY_ID')]) {
          sh './deploy.sh'
        }
      }
    }
  }
}
```

becomes:

```yaml
on: [push, pull_request]
permissions:
  id-token: write
  contents: read

jobs:
  build:
    runs-on: ubuntu-latest
    container: node:22
    steps:
      - uses: actions/checkout@v6
      - run: npm ci
      - run: npm test

  deploy:
    needs: build
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/checkout@v6
      - uses: aws-actions/configure-aws-credentials@SHA   # OIDC, no static keys
        with:
          role-to-assume: arn:aws:iam::ACCOUNT:role/deploy
          aws-region: us-east-1
      - run: ./deploy.sh
```

### Notes

- Jenkins agents that needed network access to internal systems → self-hosted runners or ARC.
- Jenkins shared libraries → composite actions in a shared `<org>/.github` repo, or reusable workflows.
- Jenkins parameters dialog → `workflow_dispatch` inputs.

## From CircleCI

CircleCI's model maps cleanly to GitHub Actions. Orbs become composite actions or reusable workflows.

```yaml
# .circleci/config.yml
version: 2.1
jobs:
  build:
    docker: [{ image: cimg/node:22 }]
    steps:
      - checkout
      - restore_cache:
          keys: ['v1-deps-{{ checksum "package-lock.json" }}']
      - run: npm ci
      - save_cache:
          key: 'v1-deps-{{ checksum "package-lock.json" }}'
          paths: [~/.npm]
      - run: npm test

workflows:
  ci:
    jobs:
      - build
```

becomes:

```yaml
on: [push, pull_request]
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-node@v6
        with: { node-version: '22', cache: npm }
      - run: npm ci
      - run: npm test
```

### Notes

- CircleCI orbs → search for an equivalent action on the GitHub Marketplace or write a composite action.
- CircleCI contexts → environment-scoped secrets in GitHub.
- CircleCI's `setup_remote_docker` → just use `docker/setup-buildx-action`.
- CircleCI `parallelism` (test splitting) → matrix strategy with shard inputs to your test runner.

## From GitLab CI

GitLab CI's `stages:` and `needs:` map closely to GitHub Actions' `needs:` graph. The biggest difference is variable handling and rules.

```yaml
# .gitlab-ci.yml
stages: [build, test, deploy]

build:
  stage: build
  image: node:22
  script:
    - npm ci
    - npm run build
  artifacts:
    paths: [dist/]

deploy:
  stage: deploy
  rules:
    - if: '$CI_COMMIT_BRANCH == "main"'
  script:
    - ./deploy.sh
```

becomes:

```yaml
on: [push, pull_request]
jobs:
  build:
    runs-on: ubuntu-latest
    container: node:22
    steps:
      - uses: actions/checkout@v6
      - run: npm ci
      - run: npm run build
      - uses: actions/upload-artifact@v4
        with: { name: dist, path: dist/ }

  deploy:
    needs: build
    if: github.ref == 'refs/heads/main' && github.event_name == 'push'
    runs-on: ubuntu-latest
    environment: production
    steps:
      - uses: actions/download-artifact@v5
        with: { name: dist, path: dist/ }
      - run: ./deploy.sh
```

### Notes

- GitLab anchors and `extends:` → composite actions or reusable workflows.
- `include:` (remote files) → `uses:` for a reusable workflow at a tagged ref.
- GitLab `dependencies:` (artifact passing) → `needs:` + `actions/upload-artifact` + `actions/download-artifact`.
- `rules:` with multiple conditions → `if:` expression with `&&`/`||`.
- Predefined variables (`CI_COMMIT_SHA`, `CI_PIPELINE_ID`, etc.) → the `github.*` context (`github.sha`, `github.run_id`, etc.). [Mapping table](https://docs.github.com/en/actions/migrating/from-gitlab/migrating-from-gitlab-cicd-to-github-actions).

## From Travis CI

Travis is the simplest to migrate; most workflows are linear.

```yaml
# .travis.yml
language: node_js
node_js: [20, 22]
script:
  - npm ci
  - npm test
deploy:
  provider: pages
  on:
    branch: main
```

becomes:

```yaml
on: [push, pull_request]
jobs:
  test:
    strategy:
      matrix: { node: [20, 22] }
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-node@v6
        with: { node-version: '${{ matrix.node }}', cache: npm }
      - run: npm ci
      - run: npm test
  # ...separate deploy workflow with environment
```

## From Azure DevOps Pipelines

```yaml
# azure-pipelines.yml
trigger: [main]
pool: { vmImage: 'ubuntu-latest' }
variables: { NODE_VERSION: '22' }

jobs:
- job: build
  steps:
  - task: NodeTool@0
    inputs: { versionSpec: $(NODE_VERSION) }
  - script: |
      npm ci
      npm test
  - task: PublishBuildArtifacts@1
    inputs: { pathToPublish: 'dist', artifactName: 'app' }
```

becomes:

```yaml
on:
  push: { branches: [main] }
jobs:
  build:
    runs-on: ubuntu-latest
    env: { NODE_VERSION: '22' }
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-node@v6
        with: { node-version: '${{ env.NODE_VERSION }}', cache: npm }
      - run: |
          npm ci
          npm test
      - uses: actions/upload-artifact@v4
        with: { name: app, path: dist/ }
```

### Notes

- Azure DevOps templates → reusable workflows or composite actions.
- Azure DevOps variable groups → environment-scoped variables/secrets in GitHub.
- Service connections to Azure → OIDC with `azure/login`.
- The `Approval` deployment gate → environment with required reviewers.
- Multiple stages with manual triggers → multiple environments with progressive promotion.

## Migration strategy

A pragmatic approach that minimizes risk:

1. **Audit first.** Run `gh actions-importer audit` to see how complex each pipeline is. Some are easy; some have custom plugins or shared libraries that need rewriting.
2. **Pick a low-risk pipeline.** Migrate one repo's CI first — preferably one that's not on the deployment critical path. Run both systems in parallel for 1–2 weeks.
3. **Mirror, don't refactor.** Resist the urge to "make it better" during migration. Translate as faithfully as possible. Refactor *after* it works.
4. **Migrate secrets last.** Don't move credentials until the workflow is otherwise complete; migrate to OIDC instead of copying long-lived keys.
5. **Branch protection → required checks.** Update branch protection to require the new workflow's check name(s). Decommission old required checks.
6. **Decommission gradually.** Once GitHub Actions is the source of truth and the team has acclimated, remove the old config. Keep it in git history for reference.

### Pitfalls

- **Different default shells.** Jenkins runs `sh` by default; GitHub uses `bash --noprofile --norc -eo pipefail`. Scripts that ignored exit codes ("works on Jenkins") will fail on GitHub. Audit for unhandled errors.
- **Different default working directory.** Some systems use `/home/runner/work/repo`; some use `/builds/group/repo`. Avoid hardcoded paths; use `$GITHUB_WORKSPACE` or relative paths.
- **No persistent agent.** State that survived between Jenkins builds (caches, tools) doesn't survive between GitHub Actions runs unless explicitly cached or pre-installed.
- **Different concurrency model.** Jenkins serializes pipelines on an agent by default; GitHub runs jobs in parallel by default. You may need `concurrency:` blocks to mimic Jenkins behavior.
- **Different secret masking.** GitHub masks the literal string; transformations leak. Audit for `echo $SECRET | base64` patterns.
