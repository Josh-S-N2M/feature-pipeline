# Phase 3 Quality Report — pipeline-quickwins-hardening-r1

**Phase:** phase-3 (CI/CD)
**Verdict:** PASS
**Tasks:** T3.1, T3.2, T3.3 — all APPROVED, zero revision cycles consumed.

## Per-dimension status

| Dimension | Status |
|---|---|
| tests | PASS |
| audits | PASS |
| validator | PASS |
| discipline | PASS |
| scope_deviations | PASS |

## Verdict rationale

All three Phase 3 tasks completed cleanly. Both new GitHub Actions workflow files exist with the correct shape and pass the atomic actionlint gate. The single MAJOR-severity finding is a known carryover from Phase 2 (the upstream gitnexus stderr regex drift); the workflow itself is correctly authored, so the drift is surfaced for Phase 5 / follow-on remediation rather than treated as a Phase 3 blocker.

## PV-3 pass criteria

- **PV-3.C1 — mcp-connectivity-smoke.yml exists, well-formed, SHA-pinned.** PASS. File is 49 lines, 1930 bytes. YAML parses. Triggers are `pull_request.paths` against four globs (`.mcp.json`, `.devcontainer/**`, `adrs/ADR-0041-*.md`, `.claude/skills/auditing-mcp/**`) plus `workflow_dispatch`. Top-level `permissions: contents: read` (single key). Single `smoke` job on `ubuntu-latest`, `timeout-minutes: 8`. Both action SHAs (`actions/checkout@34e114876b0b11c390a56381ad16ebd13914f8d5` v4.3.1, `devcontainers/ci@b63b30de439b47a52267f241112c5b453b673db5` v0.3.1900000449) match T0.2's `sha-pins.md`. `runCmd` parses `system/init.mcp_servers[]` status via `claude --bare -p "noop" --output-format stream-json | jq`. FR-6 four-field diagnostic to `$GITHUB_STEP_SUMMARY` on failure.
- **PV-3.C2 — gitnexus-grammar-skip-calibration.yml exists, well-formed, SHA-pinned.** PASS. File is 1758 bytes. YAML parses. Triggers are `schedule: cron '0 7 * * 1'` (Monday 07:00 UTC), `pull_request.paths` against `versions.env` plus the script, and `workflow_dispatch`. Top-level `permissions: contents: read`. `concurrency` is `group: gitnexus-calibration` with `cancel-in-progress: false`. `calibrate` job on `ubuntu-latest`, `timeout-minutes: 5`. Same two action SHAs as T3.1 — the one-resolution-two-reuses contract from cicd-design v0.3.0 is honored. `runCmd` is `bash .devcontainer/scripts/calibrate-gitnexus-grammar-skip.sh`. Both AC-CICD-4c-9 (workflow does not re-implement signal extraction; defers to the FR-4b script) and AC-CICD-4c-10 (workflow does not write to `mcp-events.jsonl`; the script is the authoritative emitter) honored.
- **PV-3.C3 — atomic actionlint gate.** PASS via Tier-3 hand-check. Tier 1 (local `actionlint` binary) unavailable per T0.5 tooling-check; Tier 2 (`mcp__actionlint-mcp__lint_workflow`) unavailable in the execute-task-code-producer allowlist plus has the design-cicd schema-validation history. The Plan T3.3 contract explicitly permits Tier-3 fallback when Tiers 1 and 2 are not available. Both workflow files passed every blocker-severity hand-check item: 40-character SHA pinning with version comments, `contents: read` only, no untrusted-input interpolation into `run:` blocks, no `pull_request_target`, no secrets exposure, `set -euo pipefail` in shell blocks, no deprecated `set-output`. Atomic contract honored — both files reviewed together. Detail at `t3-3-lint-report.md`.
- **PV-3.C4 — pre-merge workflow_dispatch validation.** DEFERRED-TO-POST-MERGE by design. The D-0010 three-dispatch validation requires the workflows to land on a branch that can be dispatched, which is the merge itself. The known first-invocation-failure of the FR-4c workflow (drift_detected, exit 2) is captured as deferred-MAJOR with the remediation path documented at `Issues/fr4b-signal1-regex-drift/analysis.md`. Not a Phase 3 blocker.

## Findings

### MAJOR (deferred)

- **FR-4c first-invocation-failure (T3.2 workflow).** The workflow YAML is correctly authored, but the script it invokes (`.devcontainer/scripts/calibrate-gitnexus-grammar-skip.sh`) currently returns `drift_detected` (exit 2) against the npm-distributed `gitnexus@1.6.5`. This is the same upstream contract drift that surfaced in Phase 2 (T2.5) — the FR-4b mechanism caught a real upstream divergence (the tree-sitter-dart/proto stderr no longer matches the regex T-001 captured). Phase 3 simply exposes the same problem at the CI surface. Remediation path is unchanged: either (a) re-research T-001 against live `gitnexus@1.6.5`, or (b) loosen `signal_1` to the original D-0006 recommendation pre-tightening. Belongs to a Phase 5 follow-on task or a follow-up Issue. NOT a Phase 3 regression — the workflow is doing what it was designed to do.

### INFO (carry-forward / documented degradation)

- **T3.3 Tier-3 hand-check.** Documented intended degradation per Plan T3.3 — Tiers 1 and 2 are unavailable in this environment by design. All blocker-severity hand-check items passed cleanly on both workflow files. Not a Phase 3 defect.
- **Pre-existing OP-7 baseline findings on `mcp-events.jsonl` lines 5, 6, 20.** Carry forward from Phase 1 / Phase 2; Phase 3 did not touch the event log. Project-wide housekeeping outside this feature's scope.
- **Pre-existing pipeline-frontmatter validator-targeting gap.** `validate_pipeline_frontmatter.py` emits false-positive MAJOR findings on any file lacking pipeline-doc YAML frontmatter; GitHub Actions YAML files inherently do not carry that frontmatter. The validator is scoped to PRD/Blueprint/Plan/Tests/Validators docs. Not a Phase 3-introduced defect.

## Audit-counter delta (Contract 3, gating: informational)

| Domain | Delta (P2 → P3) |
|---|---|
| tests | 0 → 0 |
| audits | 0 → 0 |
| validator | 0 → 0 |
| discipline | 0 → 0 |
| scope_deviations | 4 → 4 (severity mix simplified: 1 major + 3 info, down from 1 major + 5 info; the same upstream contract drift carries forward but is now also surfaced at the CI surface) |
| **aggregate** | **6 → 4** (two Phase-2-specific INFO items did not recur in Phase 3) |

`audit_severity_breakdown` reserved (null) per Q-CC-3.

## Next-phase readiness

Phase 4 (bundle finalization) is unblocked. The two new workflow files will be exercised as part of the Phase 4 bundled-PR CI runs. The MAJOR-deferred upstream contract drift remains the only carryover work item to address in Phase 5 or via a follow-on Issue.
