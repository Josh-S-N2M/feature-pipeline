# T3.3 Lint Report — Atomic Actionlint Gate

**Task:** T3.3 — Atomic actionlint gate over Phase 3 workflow files  
**Date:** 2026-05-27  
**Files under review:**
- `.github/workflows/mcp-connectivity-smoke.yml`
- `.github/workflows/gitnexus-grammar-skip-calibration.yml`

---

## Tier-fallback decision

**Tier 1 — Local actionlint binary:** `command -v actionlint` returned NOT FOUND. Binary absent from the devcontainer environment. Tier 1 not available.

**Tier 2 — `mcp__actionlint-mcp__lint_workflow` MCP tool:** The execute-task-code-producer agent does not have `mcp__actionlint-mcp__*` in its tool allowlist. Combined with the design-cicd-fallback history (schema-validation issue noted in T0.5), Tier 2 is not available in this agent context.

**Tier 3 — Hand-check against KB-github-actions-platform review checklist:** Applied. This is the actual lint method for this execution.

---

## Hand-check results

Checklist source: `.claude/skills/KB-github-actions-platform/SKILL.md` non-negotiables + `references/review-checklist.md`.

Severity legend: **Blocker** = must fix | **Major** = should fix | **Minor** = optional | **PASS** = compliant.

---

### File 1: `.github/workflows/mcp-connectivity-smoke.yml`

#### Security — Action pinning (Blocker if violated)

| Action | Pin style | Version comment | Result |
|--------|-----------|-----------------|--------|
| `actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5` | 40-char SHA | `# v4.3.1` | PASS |
| `devcontainers/ci@b63b30de439b47a52267f241112c5b453b673db5` | 40-char SHA | `# v0.3.1900000449` | PASS |

#### Security — `permissions:` (Blocker if missing)

- Explicit `permissions:` block at workflow level: `contents: read`. PASS.
- No `id-token: write` (OIDC not used). PASS.
- No `permissions: write-all`. PASS.

#### Security — Script injection (Blocker if violated)

- No `${{ github.event.* }}` or `${{ github.head_ref }}` interpolated into `run:` blocks. PASS.
- `BAD` variable is populated from `claude --bare` stdout piped through `jq`. This is tooling output, not user-controlled GitHub context. PASS.
- `"$BAD"` in the `if [ -n "$BAD" ]` test is double-quoted. PASS.

#### Security — Secrets handling

- No `echo "$SECRET"` or `echo "${{ secrets.X }}"` patterns. PASS.
- No secrets referenced. PASS.

#### Security — `pull_request_target`

- Not used. PASS.

#### Correctness — Triggers

- `pull_request` with `paths:` filter scoped to `.mcp.json`, `.devcontainer/**`, `adrs/ADR-0041-*.md`, `.claude/skills/auditing-mcp/**`. Appropriate for a smoke test gating MCP config changes. PASS.
- `workflow_dispatch` for manual runs. PASS.

#### Correctness — Outputs / deprecated patterns

- No `set-output` or `save-state` deprecated patterns. PASS.
- `>> "$GITHUB_STEP_SUMMARY"` used correctly. PASS.

#### Operational — Timeout

- `timeout-minutes: 8` set on the job. PASS.

#### Operational — Concurrency

- No `concurrency:` block. This workflow is a CI smoke test, not a deployment. The non-negotiable for `concurrency:` applies to deployment workflows. Absence is acceptable here. Minor note only; not a finding.

#### Shell safety

- `set -euo pipefail` present at top of `runCmd` shell script. PASS.
- `|| true` on the `jq` invocation is intentional and commented: jq exits 1 when no records match the filter (the PASS signal). The comment explains the intent. PASS.

**File 1 findings: 0 blockers, 0 majors, 0 minors requiring action.**

---

### File 2: `.github/workflows/gitnexus-grammar-skip-calibration.yml`

#### Security — Action pinning (Blocker if violated)

| Action | Pin style | Version comment | Result |
|--------|-----------|-----------------|--------|
| `actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5` | 40-char SHA | `# v4.3.1` | PASS |
| `devcontainers/ci@b63b30de439b47a52267f241112c5b453b673db5` | 40-char SHA | `# v0.3.1900000449` | PASS |

#### Security — `permissions:` (Blocker if missing)

- Explicit `permissions:` block at workflow level: `contents: read`. PASS.
- No `id-token: write`. PASS.
- No `permissions: write-all`. PASS.

#### Security — Script injection (Blocker if violated)

- No `${{ github.event.* }}` or `${{ github.head_ref }}` interpolated into `run:` blocks. PASS.
- `$SCRIPT_EXIT` is populated from `$?` (exit code of a local shell script), not from any GitHub context. PASS.

#### Security — Secrets handling

- No secrets referenced or echoed. PASS.

#### Security — `pull_request_target`

- Not used. PASS.

#### Correctness — Triggers

- `schedule: cron: '0 7 * * 1'` (Mondays 07:00 UTC) for recurring calibration. Appropriate cadence. PASS.
- `pull_request` with `paths:` filter scoped to `.devcontainer/versions.env` and `.devcontainer/scripts/calibrate-gitnexus-grammar-skip.sh`. Appropriate. PASS.
- `workflow_dispatch` for manual runs. PASS.

#### Correctness — Outputs / deprecated patterns

- No `set-output` or `save-state` deprecated patterns. PASS.
- `>> "$GITHUB_STEP_SUMMARY"` used correctly. PASS.

#### Correctness — Exit code propagation

- `SCRIPT_EXIT=$?` is assigned inside the `else` branch immediately after the failing `bash` invocation. `$?` at that point correctly holds the script's exit code. `exit "$SCRIPT_EXIT"` re-propagates it. PASS.

#### Operational — Timeout

- `timeout-minutes: 5` set. PASS.

#### Operational — Concurrency

- `concurrency: { group: gitnexus-calibration, cancel-in-progress: false }` present. Prevents overlapping calibration runs from the weekly schedule or concurrent PR triggers. PASS.

#### Shell safety

- `set -euo pipefail` present. PASS.

**File 2 findings: 0 blockers, 0 majors, 0 minors requiring action.**

---

## Summary

| File | Tier used | Findings | Fixes applied | Final state |
|------|-----------|----------|---------------|-------------|
| `mcp-connectivity-smoke.yml` | Tier 3 (hand-check) | 0 | None | PASS |
| `gitnexus-grammar-skip-calibration.yml` | Tier 3 (hand-check) | 0 | None | PASS |

**Atomic gate result: BOTH files pass. Neither is blocked.**

No edits were required to either workflow file. The hand-check covered all security blockers (SHA pinning, least-privilege permissions, script injection, pull_request_target, secrets handling), correctness items (triggers, output patterns, exit code propagation), and operational items (timeout, concurrency, step summary).

---

## Verification against Plan L1/L2/L3

- **L1:** Hand-check (Tier 3) executed against both files against the KB-github-actions-platform review checklist. Covered all blocker-severity items and major-severity items.
- **L2:** Both files report zero findings. No fixes were applied because none were needed.
- **L3:** This report documents the tier-fallback decision (Tier 1 binary absent → Tier 2 MCP not in agent allowlist → Tier 3 applied), per-file results, and the atomic gate outcome.
