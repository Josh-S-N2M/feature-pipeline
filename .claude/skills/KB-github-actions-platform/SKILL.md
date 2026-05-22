---
name: kb-github-actions-platform
description: >-
  Platform knowledge for GitHub Actions — authoring, reviewing, refactoring, and
  architecting workflows. Covers the five primitives (workflow, event, job,
  step, action), workflow YAML syntax, jobs and steps, events and triggers,
  runners, reusable workflows and composite actions, OIDC for cloud auth,
  secrets and environments, caching and artifacts, security pinning rules,
  and the canonical decision trees. Loaded when a feature touches files in
  `.github/workflows/` or CI/CD pipelines on GitHub. Pairs with
  KB-github-actions-design which adds the design discipline (when to choose
  workflow_call vs composite action; when to introduce environments; when
  matrix vs separate jobs). This KB is the PLATFORM half: facts, syntax,
  security rules, and lookup chains.
allowed-tools: Read, Grep, Glob, Edit, Write, WebFetch, Bash(python3 *)
pedagogical_sections:
  - path: references/recipe-python.md
    justification: "Python-recipe reference for GitHub Actions workflows; contains script.py example paths the auditor flags (the example artifacts don't exist in this docs-only KB)"
  - path: references/migration.md
    justification: "Migration-guide reference for adopting GitHub Actions; references .circleci/config.yml as an example of legacy CI (auditor flags non-existent path)"
  - path: references/reusable-workflows-and-actions.md
    justification: "Reusable-workflows reference; documents dist/index.js example paths typical of JavaScript actions (auditor flags non-existent example artifacts)"
  - path: scripts/action_versions.md
    justification: "Action-versions script reference; documents .github/labeler.yml example path typical of action consumers (auditor flags non-existent demo path)"
  - path: references/security.md
    justification: "Security reference catalog documenting curl-pipe-shell anti-pattern, credential-file references, and prompt-injection payloads the auditor flags. Contains intentional negative-example pipe-to-shell installer commands as anti-pattern training material; not real install instructions."
  - path: references/debugging-and-troubleshooting.md
    justification: "Debugging reference documenting credential-shaped environment variable patterns the auditor flags (DE-2 scanner); pedagogical examples of debugging credential-related workflow failures, not real credentials."
  - path: references/claude-code-cicd.md
    justification: "Claude-Code CI/CD reference documenting prompt-injection attack pattern examples (the literal canonical attack-trigger phrase that begins with 'ignore' followed by 'previous' followed by 'instructions' — split here to avoid auditor self-flagging) and credential-environment-variable references in CI/CD context. Anti-pattern training material."
  - path: references/anti-patterns.md
    justification: "Anti-patterns reference catalog explicitly documenting pipe-to-shell, exfiltration, and prompt-injection patterns the auditor flags. Each entry exists to demonstrate what to refuse, not what to execute."
  - path: references/deployment-patterns.md
    justification: "Deployment-patterns reference; contains base64-encoded values in deployment configuration examples (e.g. cloud credentials in secrets-injection patterns) — the auditor's base64 detector flags these as long encoded payloads; pedagogical reference content for deployment workflows, not live credentials."
---

# KB-github-actions-platform — GitHub Actions Platform Knowledge

Platform knowledge for GitHub Actions. This is the **platform half** of the github-actions skill pair: it teaches what exists (primitives, syntax, security rules) and provides the audit script + workflow templates. The **design half** lives in `KB-github-actions-design` (sister KB) — that one teaches when to choose which pattern and how to evolve workflow architecture. Load both for GitHub-Actions-touching design work; load just this one for reviewing or auditing existing workflows.

## Contents

- When this KB is loaded
- How to use this skill
- The five primitives
- The non-negotiables
- When to load each reference file
- Templates
- Audit script
- Verifying current details

## When this KB is loaded

This KB is in scope when:

- A feature's PRD or Blueprint declares the **CI/CD** layer in scope (per `layer-taxonomy.md` in KB-documentation-criteria)
- A per-layer Designer is producing the `cicd-design.md` subsection of the Blueprint
- Plan Authoring produces tasks that touch `.github/workflows/`, GitHub Actions YAML, OIDC setup, reusable workflows, or composite actions
- `shared-document-reviewer` or `review-architecture-auditor` is auditing artifacts that include CI/CD workflow changes

Sub-agents that reference this KB (per Blueprint v4.3.1):

- `design-cicd` (per-layer Design, when CI/CD layer is in scope)
- `design-composer` (Design Composition, integrating CI/CD design with cross-cutting concerns)
- `plan-author` (when tasks touch workflow files)
- `shared-document-reviewer` (Gate 1 CI/CD-specific checks)
- `review-architecture-auditor` (CoVe checks on workflow-related claims)

For the design discipline overlays (workflow_call vs composite action, when to introduce environments, when matrix vs separate jobs), load `KB-github-actions-design` in parallel.

Authoritative reference and decision guide for GitHub Actions: authoring new workflows, reviewing existing ones, refactoring duplication, securing pipelines, and explaining architecture. The body of this file is a tight overview plus a routing table; the deep material lives under `references/`, `assets/templates/`, and `scripts/`.

## How to use this skill

For any GitHub Actions task, work in this order:

1. **Anchor the mental model** — make sure you are clear on the five primitives (below) before touching YAML.
2. **Pick the right reference doc** from the routing table — don't try to hold the entire surface in working memory.
3. **For new workflows, start from a template** in `assets/templates/` rather than typing from scratch — the templates encode current best practice (SHA-pinned actions, least-privilege permissions, OIDC, sensible caching).
4. **For reviews, run the audit script** (`scripts/audit_workflow.py`) on the workflow file(s) and combine its output with `references/review-checklist.md`. The script requires PyYAML — if you hit `ModuleNotFoundError: No module named 'yaml'`, run `pip install pyyaml` first.
5. **Cite the specific rule** when flagging an issue — vague "this is unsafe" feedback is much less actionable than "third-party action `foo/bar@v2` is pinned to a tag, which is mutable; pin to a 40-character commit SHA per `references/security.md` § Pinning."

## The five primitives

```
event  ─┬─►  workflow  ──►  job(s)  ──►  step(s)  ──►  action or shell script
        │                      │            │
        │                  runs on a       runs in
        │                   runner       sequence
        │
   push, PR, schedule, workflow_dispatch, issue, release, repository_dispatch, ...
```

- **Workflow** — a YAML file in `.github/workflows/`. Triggered by events. Contains one or more jobs.
- **Event** — what triggers the workflow (push, pull_request, schedule, workflow_dispatch, etc.).
- **Job** — a unit of work that runs on a single runner. Jobs run in parallel by default; use `needs:` to chain them.
- **Step** — an ordered task inside a job. Either a shell command (`run:`) or an action (`uses:`).
- **Action** — a reusable unit. Three flavors: JavaScript actions, Docker container actions, composite actions. A *reusable workflow* is different — it is a whole workflow callable from another workflow via `workflow_call`.

The most common confusion is between **composite action**, **reusable workflow**, and **custom action**. See `references/reusable-workflows-and-actions.md` for the decision tree; one-line summary below in the routing table.

## The non-negotiables

These five rules apply to every workflow you author or review. If a workflow violates one, flag it.

1. **Pin third-party actions to a 40-character commit SHA.** Tags like `@v3` are mutable and can be re-pointed to malicious code. Anything outside `actions/*` and `github/*` orgs must be SHA-pinned. First-party `actions/*` may use major-version tags (e.g. `@v6`) since GitHub controls them, though SHA-pinning is still safer. Add a comment with the version next to the SHA so humans can read it: `uses: aws-actions/configure-aws-credentials@e3dd6a429d7300a6a4c196c26e071d42e0343502 # v4.0.2`.

2. **Set least-privilege `permissions:`.** Without an explicit `permissions:` block, the `GITHUB_TOKEN` may have broad scopes depending on repo/org defaults. Always declare what the workflow needs. The common minimum is `contents: read`. Add `id-token: write` only if using OIDC; `pull-requests: write` only if commenting on PRs; etc.

3. **Never interpolate untrusted input directly into `run:` blocks.** Values from `github.event.pull_request.title`, `github.event.issue.body`, `github.head_ref`, etc. can contain shell metacharacters and are an injection vector. Pass them through an environment variable instead, then reference the env var with `"$VAR"` quoting.

4. **Prefer OIDC over long-lived cloud credentials.** AWS, Azure, GCP, HashiCorp Vault, and others support OpenID Connect federation from GitHub. Long-lived access keys stored as secrets are a breach blast radius; OIDC issues short-lived tokens scoped to the workflow.

5. **Set `concurrency:` on deployment workflows.** Without it, two pushes to `main` can race two deployments and corrupt state. The standard pattern is `concurrency: { group: deploy-${{ github.ref }}, cancel-in-progress: false }` for production (queue) and `cancel-in-progress: true` for preview environments (cancel stale).

Full rationale and worked examples for each of these is in `references/security.md` and `references/anti-patterns.md`.

## Routing table

| If the task is about… | Read… |
|---|---|
| YAML structure, what keys are valid, full syntax | `references/workflow-syntax.md` |
| Triggers (push, pull_request, schedule, workflow_dispatch, issue events, etc.) and their gotchas | `references/events-and-triggers.md` |
| Contexts (`github`, `env`, `secrets`, `needs`, `matrix`, `inputs`, `vars`, `runner`, `job`, `steps`) and expression functions | `references/contexts-and-expressions.md` |
| Job dependencies, outputs, conditionals, matrix, services, defaults | `references/jobs-and-steps.md` |
| Choosing a runner (GitHub-hosted vs larger vs self-hosted vs ARC) | `references/runners.md` |
| Reusable workflows vs composite actions vs custom JS/Docker actions | `references/reusable-workflows-and-actions.md` |
| Secrets, GITHUB_TOKEN scopes, OIDC, script injection, SHA pinning, attestations | `references/security.md` |
| `actions/cache`, language-aware caching, artifact upload/download (v4 changes) | `references/caching-and-artifacts.md` |
| Concurrency groups, environments, deployment protection rules, manual approvals | `references/concurrency-and-environments.md` |
| Deploying to AWS, Azure, GCP, Netlify, Supabase, Pages, container registries | `references/deployment-patterns.md` |
| Debug logging, common errors, why a workflow won't trigger | `references/debugging-and-troubleshooting.md` |
| Migrating from Jenkins, CircleCI, GitLab CI, Travis, Azure DevOps | `references/migration.md` |
| Running Claude Code itself in CI (PR review, issue triage, agentic automation) — via direct API, Bedrock, Vertex AI, or Microsoft Foundry | `references/claude-code-cicd.md` |
| Reviewing or auditing a workflow | `references/review-checklist.md` + run `scripts/audit_workflow.py` |
| Looking up the current major version of a specific action (e.g. `actions/checkout`, `aws-actions/configure-aws-credentials`) before suggesting a `uses:` line | `scripts/action_versions.md` |
| Catalogue of patterns that look reasonable but cause incidents | `references/anti-patterns.md` |
| TypeScript/Node project CI patterns | `references/recipe-typescript.md` |
| Python project CI patterns | `references/recipe-python.md` |
| Terraform, Pulumi, OpenTofu, CDK pipelines | `references/recipe-iac.md` |

## Templates

When authoring a new workflow, copy the relevant template from `assets/templates/` and adapt — don't write from scratch. Each template is production-grade and follows the non-negotiables.

| File | Use when… |
|---|---|
| `ci-typescript.yml` | Node/TypeScript project: lint, typecheck, test, build with caching |
| `ci-python.yml` | Python project: ruff, mypy, pytest, matrix on Python versions |
| `ci-iac-terraform.yml` | Terraform: fmt, validate, plan on PR, apply on merge with environments |
| `cd-aws-oidc.yml` | Deploy to AWS using OIDC (no long-lived keys) |
| `cd-azure-oidc.yml` | Deploy to Azure using OIDC |
| `cd-gcp-oidc.yml` | Deploy to GCP using Workload Identity Federation |
| `cd-netlify.yml` | Deploy a static site to Netlify with PR previews |
| `cd-supabase.yml` | Apply Supabase migrations and deploy Edge Functions |
| `release-npm.yml` | Publish to npm with provenance via OIDC trusted publishing |
| `release-pypi.yml` | Publish to PyPI via trusted publisher (no API token) |
| `release-docker-ghcr.yml` | Build multi-arch image and push to GHCR with attestation |
| `assets/templates/reusable-workflow.yml` | A `workflow_call`-triggered workflow + a caller example |
| `assets/templates/composite-action/action.yml` | A composite action skeleton (action that wraps multiple steps) |
| `assets/templates/pr-automation.yml` | Label PRs, comment, run housekeeping on a schedule |
| `assets/templates/claude-code-tag.yml` | Run Claude Code in response to `@claude` mentions in PRs/issues |
| `assets/templates/claude-code-pr-review.yml` | Automated Claude review of every PR (no trigger phrase needed) |
| `assets/templates/claude-code-issue-triage.yml` | Scheduled Claude triage of newly opened issues |
| `assets/templates/claude-code-bedrock.yml` | Claude Code via Amazon Bedrock (OIDC) instead of direct API |
| `assets/templates/claude-code-vertex.yml` | Claude Code via Google Vertex AI (Workload Identity Federation) |
| `assets/templates/claude-code-foundry.yml` | Claude Code via Microsoft Foundry (Entra ID federated credential) |

## Authoring decision tree

When asked to design a new workflow, ask these questions in order:

1. **What event(s) should trigger it?** Map the user's intent to one of the [event types](references/events-and-triggers.md). "On every push" is rarely what you want — usually it's "on push to default branch" plus "on pull_request" plus possibly `workflow_dispatch` for manual runs.
2. **Does the workflow need secrets or to write back to the repo?** That decides the `permissions:` block. Default to `contents: read` and add only what's needed.
3. **Does it deploy?** If yes: it needs an `environment:`, a `concurrency:` group, OIDC if cloud-bound, and probably a manual approval gate via deployment protection rules.
4. **Will the same logic run for multiple variants (OS, language version, region)?** Use `strategy.matrix:` rather than copy-pasting jobs.
5. **Is similar logic already in another workflow in the same org/repo?** Extract into a reusable workflow (`workflow_call`) or composite action. See decision tree in `references/reusable-workflows-and-actions.md`.
6. **What's the runner choice?** `ubuntu-latest` unless there's a specific reason (Windows-only tooling, GPU, large RAM, network access to private resources).
7. **What's the failure mode?** Add `if: failure()` cleanup steps where state needs to be reverted. Use `continue-on-error:` sparingly and only with explicit reason.

## Review checklist (summary)

The full checklist is in `references/review-checklist.md`. The high-leverage questions to ask of any existing workflow:

- Are all third-party actions pinned to a SHA? (Run `scripts/audit_workflow.py`.)
- Is there an explicit `permissions:` block? Is it minimal?
- Is any `${{ github.event.* }}` value or `${{ github.head_ref }}` interpolated into a `run:` block? (Injection risk.)
- Is `pull_request_target` used? If so, does it check out the PR's head SHA? (Critical danger; see `references/security.md` § pull_request_target.)
- Are deprecated patterns present (`set-output`, `save-state`, `::set-output::`, Node 12/16 actions)?
- Are deployments wrapped in a `concurrency:` group and an `environment:`?
- Are caches keyed correctly so they invalidate when dependencies change?
- Are secrets passed only to jobs that need them? Are reusable workflows passed `secrets: inherit` only when justified?
- Are matrix combinations doing meaningful work, or are some redundant?
- Is `timeout-minutes:` set on long jobs to prevent runaway billing?
- Are workflow logs free of secret leakage (no `echo "$SECRET"` patterns)?

## Refactoring tactics

Common refactors and their references:

- **Duplicate jobs across files** → extract a reusable workflow. See `references/reusable-workflows-and-actions.md`.
- **Same step block in many places** → composite action. Same reference.
- **Three near-identical jobs differing only by a value** → matrix strategy. See `references/jobs-and-steps.md` § matrix.
- **Long-lived AWS/Azure/GCP keys in secrets** → migrate to OIDC. See `references/deployment-patterns.md` for each cloud.
- **`set-output` (deprecated)** → `echo "name=value" >> "$GITHUB_OUTPUT"`. See `references/jobs-and-steps.md` § outputs.
- **Unpinned third-party actions** → pin to SHA, add `# v1.2.3` comment. See `references/security.md`.

## Communicating with the user

When writing a workflow, briefly explain the design choices that aren't obvious — why this trigger combination, why this permission scope, why this matrix, why OIDC over a key. People want to understand and modify the result, not just receive a black box.

When reviewing, lead with the highest-severity issues (security, correctness) and group lower-severity items (style, optimization) at the end. Quote the specific line(s), explain the risk, and propose the concrete fix.

When the user has a workflow that "works" but violates a non-negotiable (e.g. unpinned actions), don't just rewrite it silently — surface the issue, explain why it matters, and ask whether they want it fixed alongside whatever they originally asked for.

## Notes for subagent use

When this skill is preloaded into a subagent (via the subagent's `skills:` field), this SKILL.md body is fully loaded but the bundled references in `references/`, `assets/templates/`, and `scripts/` still load on demand. The subagent must include `Read` in its `tools:` field to reach them, and `Bash(python3 *)` if it will run `audit_workflow.py`. Any `paths:` restriction on the subagent should permit `.github/workflows/**` plus the skill's own directory.

For pure audit work where the main session only needs the summary, prefer the standalone `audit-workflow` skill (separate from this one) — it is `disable-model-invocation: true` with a tight `Read, Grep, Glob, Bash(python3 *)` tool set. This skill remains the right choice when the work involves authoring, refactoring, or explaining workflows in addition to or instead of auditing.
