# Events and Triggers

Every workflow is started by an event. Picking the wrong event is a top source of bugs (workflow doesn't run, runs at the wrong time, runs with wrong permissions, leaks secrets to fork PRs). This reference covers the common events and their gotchas.

## Table of contents

- [Repository events](#repository-events)
- [Pull request events](#pull-request-events)
- [Manual and external triggers](#manual-and-external-triggers)
- [Scheduled events](#scheduled-events)
- [Workflow chaining](#workflow-chaining)
- [Issue, release, deployment events](#issue-release-deployment-events)
- [Filters: branches, tags, paths, types](#filters-branches-tags-paths-types)
- [Token scope and the fork PR problem](#token-scope-and-the-fork-pr-problem)
- [Common patterns](#common-patterns)

## Repository events

### `push`

Fires on any pushed commit (and on tag pushes if `tags:` is configured). The most common workflow trigger.

```yaml
on:
  push:
    branches: [main, 'release/**']
    paths-ignore: ['docs/**', '**.md']
    tags: ['v*.*.*']
```

Notes:
- `paths-ignore:` can be combined with `branches:` — both must match.
- A tag push and a branch push are two separate events. To trigger on both, list both filters; or use two separate `push:` blocks via the `tags:` and `branches:` keys.
- A push that creates a new branch is a normal push; `github.event.created` is `true`.

### `create`, `delete`

Branch or tag created/deleted. Less common than `push:` with `tags:`. `delete:` cannot be combined with branch/tag filters.

### `fork`, `public`, `watch`

Repository-level events. Rarely used for CI; useful for organizational automation.

## Pull request events

### `pull_request`

Fires when a PR is opened, synchronized (new push to the source branch), reopened, etc. The workflow runs in the context of the PR's *base* repository (i.e., your repo) but checks out the PR's *head* code by default.

```yaml
on:
  pull_request:
    types: [opened, synchronize, reopened, ready_for_review]
    branches: [main]
    paths: ['src/**', 'tests/**']
```

Available `types:`: `assigned`, `unassigned`, `labeled`, `unlabeled`, `opened`, `edited`, `closed`, `reopened`, `synchronize`, `converted_to_draft`, `ready_for_review`, `locked`, `unlocked`, `review_requested`, `review_request_removed`, `auto_merge_enabled`, `auto_merge_disabled`. Default if not specified: `[opened, synchronize, reopened]`.

**The fork PR token gotcha:** when the PR comes from a fork, the `GITHUB_TOKEN` is read-only and secrets are not exposed. This is a security feature — without it, anyone who could open a PR could exfiltrate your secrets. CI works (lint, typecheck, build, test) but anything needing write access (commenting on the PR, deploying a preview, accessing private package registries) won't.

### `pull_request_target`

⚠️ **High-risk trigger.** Fires on PR events but runs in the context of the PR's *target* (your default branch), with full token write access and full secrets. Useful for: labeling PRs, posting comments, running approved-fork checks.

**The danger:** the default checkout (`actions/checkout` with no `ref:`) checks out the *target* branch, not the PR head. So far so good. But if a workflow uses `pull_request_target` and then explicitly checks out the PR's head SHA *and* runs build/test scripts from that PR, it executes attacker-controlled code with full secrets. This is how supply-chain attacks have happened.

**Safe usage rules:**
1. Never check out the PR head in a `pull_request_target` workflow unless you have a separate, hardened approval gate.
2. If you must, only run pre-defined steps that don't execute PR-supplied scripts. Don't `npm install` or `pip install` or run any build script from the PR's checkout.
3. Don't combine `pull_request_target` with caching that the PR can populate.

A safer pattern: use two workflows. One on `pull_request` does the build/test (no secrets, read-only token). Another on `workflow_run` (triggered when the first completes) handles the privileged steps.

### `pull_request_review`, `pull_request_review_comment`

Fires when a review is submitted/edited/dismissed. Useful for "auto-merge after approval" workflows.

## Manual and external triggers

### `workflow_dispatch`

Manual trigger from the Actions UI, GitHub CLI (`gh workflow run`), or API. Define typed inputs:

```yaml
on:
  workflow_dispatch:
    inputs:
      environment:
        description: Target environment
        type: environment        # populated from configured environments
        required: true
      version:
        description: Version to deploy
        type: string
        required: true
      dry_run:
        type: boolean
        default: false
      log_level:
        type: choice
        options: [debug, info, warn, error]
        default: info
```

Access via `inputs.*` (typed) or `github.event.inputs.*` (always string).

### `repository_dispatch`

External webhook trigger. Anyone with a token having `repo` scope can fire it via:
```
POST /repos/:owner/:repo/dispatches
{ "event_type": "deploy", "client_payload": { ... } }
```

Use for: external systems triggering workflows (e.g., a release in another repo triggers a deploy here).

```yaml
on:
  repository_dispatch:
    types: [deploy, rollback]
```

The `event_type` from the API is matched against `types:`. Access the payload via `github.event.client_payload.*`.

## Scheduled events

### `schedule`

Cron-style scheduled runs. Runs on the default branch.

```yaml
on:
  schedule:
    - cron: '0 6 * * 1-5'    # 06:00 UTC, Monday-Friday
    - cron: '0 */4 * * *'    # every 4 hours
```

Notes:
- Times are UTC.
- Minimum interval: 5 minutes between runs.
- Scheduled workflows can be delayed during peak load — don't rely on exact timing.
- Schedules pause after 60 days of repository inactivity.
- To distinguish *which* schedule fired (when there are multiple `cron:` entries), check `github.event.schedule`.

## Workflow chaining

### `workflow_call`

Makes the workflow callable from another workflow. The defining workflow declares `inputs`, `secrets`, and `outputs`. See [reusable-workflows-and-actions.md](reusable-workflows-and-actions.md).

```yaml
on:
  workflow_call:
    inputs:
      target:
        type: string
        required: true
    secrets:
      DEPLOY_TOKEN:
        required: true
    outputs:
      deployed_url:
        description: URL of the deployed service
        value: ${{ jobs.deploy.outputs.url }}
```

### `workflow_run`

Fires when *another* workflow completes (success or failure). Runs in the context of the default branch with full token/secret access — useful for privileged follow-ups to PR workflows.

```yaml
on:
  workflow_run:
    workflows: [CI]
    types: [completed]
    branches: [main]
```

Inside a `workflow_run` workflow:
- `github.event.workflow_run.*` has the upstream run's metadata.
- To download artifacts from the upstream run, use the GitHub API (the standard `actions/download-artifact` only works for the same run).
- The `head_sha` is from the upstream run, not the trigger event itself.

This is the safe channel for PR workflows that need privileged access.

## Issue, release, deployment events

```yaml
on:
  issues:
    types: [opened, edited, labeled]
  issue_comment:
    types: [created]
  release:
    types: [published]    # most common
  deployment:
  deployment_status:
  page_build:
  registry_package:
  discussion:
  discussion_comment:
```

`release: types: [published]` is the canonical "build and publish artifacts on release" trigger.

## Filters: branches, tags, paths, types

Glob patterns (Action Filter syntax, similar to `.gitignore`):
- `*` — matches anything except `/`
- `**` — matches across `/`
- `?` — single character
- `[abc]` — character class
- `!pattern` — negation (exclude)

Examples:
- `branches: ['main', 'release/**']` — main and any release/* branch
- `paths: ['src/**', '!src/vendor/**']` — src but not vendor
- `tags: ['v*.*.*', '!*-rc*']` — full version tags, no rc

**`paths-ignore` precedence:** if a commit touches *only* paths in `paths-ignore`, the workflow doesn't run. If it touches even one path outside, the workflow runs. Use `paths:` for a positive include, `paths-ignore:` for an exclude.

## Token scope and the fork PR problem

Summary of what the `GITHUB_TOKEN` can do under each event:

| Event | From own repo | From fork |
|---|---|---|
| `push` | full token, full secrets | n/a (forks can't push to your repo) |
| `pull_request` | full token (limited by `permissions:`), secrets available | **read-only token, no secrets** |
| `pull_request_target` | full token, full secrets | **full token, full secrets** ⚠️ |
| `workflow_run` | full token, full secrets | full token, full secrets |
| `workflow_dispatch` | full token, full secrets | n/a (only authenticated users can dispatch) |
| `schedule` | full token, full secrets | n/a |

**Implication:** if your CI workflow needs to comment on PRs from forks, post coverage results, etc., you have two options:
1. Use `pull_request_target` carefully (do *not* run untrusted PR code).
2. Use a two-workflow pattern: `pull_request` for build/test (no secrets), `workflow_run` for the privileged comment step (full secrets, only runs after the first succeeds).

## Common patterns

### "CI on PRs and pushes to main"

```yaml
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
```

Note: this means a PR to `main` runs the workflow once on `pull_request`, and again on `push` when it merges. Most teams accept this; if you want to skip the post-merge run when content is unchanged, use `paths:` or skip-ci commit messages.

### "Deploy on tag, manual rollback"

```yaml
on:
  push:
    tags: ['v*.*.*']
  workflow_dispatch:
    inputs:
      version:
        type: string
        required: true
```

### "Run nightly + on demand + on PR for changed files"

```yaml
on:
  schedule:
    - cron: '0 4 * * *'
  workflow_dispatch:
  pull_request:
    paths: ['src/**']
```

### "Skip CI on docs-only changes"

```yaml
on:
  push:
    paths-ignore: ['docs/**', '**.md', '.github/ISSUE_TEMPLATE/**']
  pull_request:
    paths-ignore: ['docs/**', '**.md']
```

### Skip via commit message

GitHub recognizes `[skip ci]`, `[ci skip]`, `[no ci]`, `[skip actions]`, `[actions skip]` in commit messages and skips workflow runs. Use sparingly.
