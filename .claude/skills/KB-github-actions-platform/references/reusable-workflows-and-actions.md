# Reusable Workflows and Actions

Three primary mechanisms exist for sharing logic across workflows. Picking the right one is the most common architectural question. This reference is a decision tree plus the mechanics of each.

## Table of contents

- [The four mechanisms](#the-four-mechanisms)
- [Decision tree](#decision-tree)
- [Reusable workflows (`workflow_call`)](#reusable-workflows-workflow_call)
- [Composite actions](#composite-actions)
- [JavaScript actions](#javascript-actions)
- [Docker container actions](#docker-container-actions)
- [Sharing across repositories](#sharing-across-repositories)
- [Versioning and releasing actions](#versioning-and-releasing-actions)

## The four mechanisms

| Mechanism | What it is | Granularity | Where it lives |
|---|---|---|---|
| **Reusable workflow** | A whole workflow callable from another workflow via `workflow_call` | Multiple jobs | `.github/workflows/*.yml` |
| **Composite action** | A bundle of steps callable as a single step via `uses:` | Multiple steps within one job | `<some-dir>/action.yml` |
| **JavaScript action** | A Node.js program callable as a single step | One step's worth of logic | `<some-dir>/{action.yml, dist/index.js}` |
| **Docker container action** | A containerized program callable as a single step | One step's worth of logic | `<some-dir>/{action.yml, Dockerfile}` |

## Decision tree

```
Is the logic a multi-step sequence with potentially different runners or environments?
├── YES → Reusable workflow (workflow_call)
└── NO  → Continue
        Does it run as a single step?
        ├── YES → Continue
        │       Can it be expressed as shell + a few existing actions?
        │       ├── YES → Composite action
        │       └── NO → Continue
        │               Can it run on the runner directly (no isolation needed)?
        │               ├── YES → JavaScript action (Node.js)
        │               └── NO  → Docker container action
        └── NO → You probably want a reusable workflow
```

In practice, ~80% of "share this logic" tasks are best served by either a **reusable workflow** (multi-step, multi-job, possibly involving different runners) or a **composite action** (a small sequence of steps inside an existing job).

JavaScript and Docker actions are for distributed actions on the GitHub Marketplace — not your typical internal-sharing case.

## Reusable workflows (`workflow_call`)

A workflow that can be called from another workflow. Has its own runners, its own permissions, its own jobs.

### Defining

```yaml
# .github/workflows/build-and-test.yml
name: Build and Test (reusable)

on:
  workflow_call:
    inputs:
      node-version:
        type: string
        default: '22'
      run-tests:
        type: boolean
        default: true
    secrets:
      NPM_TOKEN:
        required: false
    outputs:
      version:
        description: The built version
        value: ${{ jobs.build.outputs.version }}

jobs:
  build:
    runs-on: ubuntu-latest
    outputs:
      version: ${{ steps.bump.outputs.version }}
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-node@v6
        with:
          node-version: ${{ inputs.node-version }}
          cache: npm
      - run: npm ci
      - id: bump
        run: echo "version=$(node -p 'require("./package.json").version')" >> "$GITHUB_OUTPUT"

  test:
    if: ${{ inputs.run-tests }}
    needs: build
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-node@v6
        with: { node-version: '${{ inputs.node-version }}', cache: npm }
      - run: npm ci
      - run: npm test
```

### Calling

```yaml
# .github/workflows/ci.yml
on: [push, pull_request]

jobs:
  ci:
    uses: ./.github/workflows/build-and-test.yml         # same repo
    # or: uses: my-org/shared/.github/workflows/build-and-test.yml@v1.0.0
    with:
      node-version: '22'
      run-tests: true
    secrets:
      NPM_TOKEN: ${{ secrets.NPM_TOKEN }}
    permissions:
      contents: read
      packages: read

  deploy:
    needs: ci
    runs-on: ubuntu-latest
    steps:
      - run: echo "Deploying ${{ needs.ci.outputs.version }}"
```

### Constraints and gotchas

- A reusable workflow has its own `permissions:`. The caller passes a `permissions:` block, but the reusable workflow's own block must permit what its actions need. The effective permissions are the *intersection*.
- You can nest reusable workflows up to 4 levels deep.
- `secrets: inherit` passes all the caller's secrets; otherwise list specific secrets in `secrets:`.
- A reusable workflow can't be called from inside a regular job's steps — it's a job-level concept (`jobs.<id>.uses`).
- Outputs are job outputs, declared in the `workflow_call` block.
- The `concurrency:` of the caller doesn't apply to the reusable workflow's jobs unless you set it inside the reusable workflow.

### When to use

- Multi-job patterns (build → test → publish) reused across many repos.
- Org-wide standards (e.g., "every repo must run this security scan workflow").
- Logic involving different runners (build on Linux, test on Windows).

## Composite actions

A bundled sequence of steps that runs as a single step inside an existing job.

### Defining

```yaml
# .github/actions/setup-typescript/action.yml
name: Setup TypeScript Project
description: Checkout, install Node, install deps with cache
inputs:
  node-version:
    description: Node.js version
    required: false
    default: '22'
  install-cmd:
    description: Install command
    required: false
    default: 'npm ci'
outputs:
  cache-hit:
    description: Whether the npm cache was hit
    value: ${{ steps.setup.outputs.cache-hit }}
runs:
  using: composite
  steps:
    - id: setup
      uses: actions/setup-node@v6
      with:
        node-version: ${{ inputs.node-version }}
        cache: npm
    - shell: bash
      run: ${{ inputs.install-cmd }}
```

### Calling

```yaml
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: ./.github/actions/setup-typescript
        with:
          node-version: '20'
      - run: npm test
```

### Constraints

- Inputs and outputs only; no secrets parameter (composite actions inherit env, not secrets explicitly).
- Each step in the composite needs `shell:` set if it's a `run:` (because the composite doesn't inherit the calling job's defaults).
- A composite action can call other actions (`uses:`) and run shell (`run:`).
- Conditional steps inside a composite work but use `if:` inside the action's `steps:`, not from the caller.
- The path-based reference (`./.github/actions/setup-typescript`) requires `actions/checkout` to have run first in the calling job.

### When to use

- A handful of steps repeated across many jobs in the same repo.
- Setup scaffolding (checkout → install language → install deps → set env).
- Wrapping a few existing actions with project-specific defaults.

## JavaScript actions

A Node.js program with an `action.yml` that declares inputs/outputs and runs a JS entrypoint.

### Defining

```yaml
# action.yml
name: My JS Action
description: Does a thing
inputs:
  who:
    required: true
    default: world
outputs:
  greeting:
    description: The greeting produced
runs:
  using: node24      # node20 deprecating in mid-2026
  main: dist/index.js
```

```javascript
// src/index.js
const core = require('@actions/core');

try {
  const who = core.getInput('who');
  const greeting = `Hello, ${who}!`;
  core.setOutput('greeting', greeting);
  console.log(greeting);
} catch (err) {
  core.setFailed(err.message);
}
```

Then bundle (`@vercel/ncc` or rollup) so `dist/index.js` is a single file with deps inlined, and commit `dist/`.

### When to use

- Distributing an action publicly on the Marketplace.
- Logic too complex for shell, needing the GitHub API, or wanting good cross-platform support.
- Anything that needs to interact with the runner toolkit (`@actions/core`, `@actions/github`, `@actions/exec`).

For internal use, a composite action calling a `node script.js` step is usually simpler.

## Docker container actions

A `Dockerfile` plus an `action.yml` declaring the container as the runtime.

### Defining

```yaml
# action.yml
name: My Docker Action
description: Runs a thing in a container
runs:
  using: docker
  image: Dockerfile
  args:
    - ${{ inputs.target }}
```

### Constraints

- Linux runners only (Docker actions don't work on macOS or Windows runners).
- Slower startup (image build or pull).
- Useful when the action needs specific tools or libraries that are awkward to install on the bare runner.

### When to use

- The action needs a specific OS userspace or a niche toolchain.
- You want hermetic isolation.
- Almost never the right choice for internal sharing — composite actions or reusable workflows are easier to maintain.

## Sharing across repositories

### Reusable workflows from another repo

```yaml
jobs:
  call:
    uses: my-org/shared-workflows/.github/workflows/test.yml@v1.0.0
    with: { ... }
    secrets: inherit
```

The referenced repo must allow your repo to use its workflows (Settings → Actions → "Access" for private repos). For public repos, anyone can reference them.

### Cross-repo composite actions

```yaml
- uses: my-org/shared-actions/setup@v1.0.0
```

Same: pin to a version, public/private access controlled at the source repo level.

### Internal repo for shared automation

A common pattern is a single `<org>/.github` or `<org>/actions` repo holding all reusable workflows and composite actions. Pros:
- Single source of truth.
- One place to release versions.
- Centralized review for security-sensitive changes.

## Versioning and releasing actions

For an action repo (whether you'll publish to the Marketplace or just use internally):

### Tag scheme

- Full version tags: `v1.2.3`.
- Major version moving tags: `v1` (re-pointed to latest `v1.x.y` on each release). Convenient for users, but **callers should pin to SHA, not the major tag**, for the security reasons in `references/security.md`.

### Release script

```bash
# Cut a release
git tag v1.2.3
# Move the major tag
git tag -fa v1 -m "v1.2.3"
git push origin v1.2.3
git push origin v1 --force
```

GitHub now offers [immutable releases](https://docs.github.com/en/actions/how-tos/create-and-publish-actions/using-immutable-releases-and-tags-to-manage-your-actions-releases) which prevent the tag from being moved — recommended for public actions.

### Distributing built JavaScript

For JS actions, commit the `dist/` directory. Users install your action without npm install — they just download the action and run `dist/index.js`. Use a CI workflow to verify `dist/` is up to date relative to `src/`.

```yaml
# .github/workflows/check-dist.yml
on: pull_request
jobs:
  check-dist:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v6
      - uses: actions/setup-node@v6
        with: { node-version: 22, cache: npm }
      - run: npm ci
      - run: npm run build
      - run: |
          if [ -n "$(git status --porcelain dist/)" ]; then
            echo "::error::dist/ is out of date — run 'npm run build' and commit"
            exit 1
          fi
```

## Quick recap

- **Many jobs, many repos** → reusable workflow.
- **Many steps, one job** → composite action.
- **One step, complex logic, public** → JavaScript action.
- **One step, exotic deps, hermetic** → Docker action.

When in doubt, start with composite or reusable workflow. Move to JS/Docker only if you need their specific advantages.
