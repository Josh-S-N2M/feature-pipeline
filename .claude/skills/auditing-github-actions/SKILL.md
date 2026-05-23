---
name: auditing-github-actions
description: >-
  Audits GitHub Actions workflows for security pinning, secrets discipline,
  OIDC posture, and structural correctness. ALWAYS invoke when reviewing,
  auditing, evaluating, scoring, vetting, fixing, or critiquing GitHub
  Actions workflow files (anything under `.github/workflows/`), composite
  actions, or reusable workflows. Use when triaging "is my workflow
  secure?" or "do my action versions follow the pinning rules?". Produces
  per-workflow findings with severity, file path, and recommended-fix
  guidance. Report-only — does not modify the audited files.
allowed-tools: Read, Grep, Glob, Bash(python3 *)
---

# Auditing GitHub Actions Workflows

This skill is the audit half of the cc-style three-way split for GitHub
Actions:

- `KB-github-actions-platform` — platform knowledge (syntax, primitives,
  security rules, decision trees)
- `KB-github-actions-design` — design discipline (when to choose what)
- `auditing-github-actions` — **this skill** — mechanical audit of existing
  workflow files

Per ADR-0031 canonical-helper-home, cross-cutting helper utilities
(JSON-finding schema, severity taxonomy, deny-baseline checks) live in
`auditing-shared`. This skill consumes those utilities; it owns the
GitHub-Actions-specific scan logic and the curated `action_versions.md`
reference list.

## Contents

- `SKILL.md` — this file
- `scripts/audit_workflow.py` — the audit entry point (relocated from
  `KB-github-actions-platform/scripts/` per ADR-0031 + AC-FR-8-a)
- `references/action_versions.md` — curated list of known third-party
  action versions and their pinning posture (relocated alongside the
  audit script)

## When to invoke

- A feature touches `.github/workflows/` files
- The user asks "is my workflow secure?" / "audit my GitHub Actions setup"
- A sub-agent (e.g., `design-cicd`) needs to scan existing workflows
  before authoring a Blueprint section that references them
- Periodic project-wide audits per `auditing-cc-configs` dispatch

## What it checks

- Action-version pinning posture per `references/action_versions.md`
  (commit-SHA vs. tag; known-vulnerable ranges)
- `permissions:` block presence and scope (least-privilege per the
  workflow's actual needs)
- Secrets handling: no plaintext secrets; `secrets:` block scoped per
  job; no echoing into logs
- OIDC posture for cloud auth: `id-token: write` only when needed;
  `aud:` claim narrowed
- Step `uses:` referential integrity: action exists, version exists,
  pinning satisfies the project's policy
- Structural correctness: YAML parses; required top-level keys present;
  no orphaned references

## What it does NOT check

- Whether the workflow's intent is correct (a workflow can be perfectly
  secure and still do the wrong thing). Intent review is the human
  reviewer's job; this skill is mechanical.
- Whether the underlying actions themselves are trustworthy. The
  `action_versions.md` reference is curated, not exhaustive; new actions
  surface as findings for human review.
- Code quality inside the actions' run scripts. That's the script's own
  language audit (Python/shell/etc.), not this skill's scope.

## Invocation

```bash
python3 .claude/skills/auditing-github-actions/scripts/audit_workflow.py \
  .github/workflows/<file>.yml
```

Output: structured JSON findings on stdout, conforming to the
auditing-shared finding schema (per Blueprint Field Propagation Map
finding schema):

```json
{
  "findings": [
    {
      "domain": "audits",
      "severity": "blocker | major | minor | info",
      "source_activity": "gha-audit",
      "file_path": "<path>",
      "message": "<description>",
      "dispatch_hint": "<upstream stage suggestion>",
      "depth_level": "0..8"
    }
  ]
}
```

## Relationship to KB-github-actions-platform

Before this skill existed (pre-execution-pipeline-design-r1), the audit
script and `action_versions.md` reference lived under
`KB-github-actions-platform/scripts/`. Per IN-002 + ADR-0031 +
AC-FR-8-a, those files were relocated here (via `git mv` to preserve
history) so that:

1. Platform knowledge and audit machinery have distinct homes (the
   cc-style three-way split).
2. Cross-skill helpers (in `auditing-shared`) can be consumed by all
   `auditing-*` skills uniformly.
3. The pattern is symmetric across audit families (cc, gha, codespaces).

`KB-github-actions-platform/SKILL.md` Contents list points to this skill
for audit functionality.

## See also

- `auditing-shared` — canonical helpers, finding schema, severity taxonomy
- `auditing-cc-configs` — sibling pattern; pre-existing reference for
  three-way-split discipline
- `auditing-codespaces` — sibling stub (per AC-FR-8-b + Q-CC-4)
- `KB-github-actions-platform` — platform-knowledge half
- `KB-github-actions-design` — design-discipline half
