---
id: PhaseValidators-pipeline-quickwins-hardening-r1
version: 1.0.1
status: draft
feature_slug: pipeline-quickwins-hardening-r1
derived_from: working/feature/pipeline-quickwins-hardening-r1/plan-v1.md
plan_version: 1.0.1
validators: 6
generated: 2026-05-26T00:00:00Z
generated_by: test-phase-validator-author
revision_history:
  - version: 1.0.1
    date: 2026-05-26
    summary: |
      Cross-Artifact Audit cycle 1 reconciliation (per reconciliation-log-r3.md).
      Three surgical edits, no structural or substantive changes:
      (1) I-CA-003 (Validators side) — bumped §Source pointer from
      "Blueprint v2.1" to "Blueprint v2.2.0" to reflect the v2.2 lift cycle.
      (2) I-CA-006 — added AT-NNN cross-references in each phase's
      "Acceptance tests scheduled for this phase" subsection by mapping the
      cited AC IDs to AT IDs per the Acceptance Tests v1.0.1 Coverage Matrix
      (AT-001 through AT-079). Marked the corresponding §Open items entry
      complete.
      (3) I-CA-008 — added a one-line cross-reference to PV-5.C4 pointing at
      Plan T5.4's open-ended observation framing so a future reader can
      trace why the severity is compound rather than singular.
      The 6 validator structures (PV-0..PV-5), the 30 pass criteria, the
      dependency chain, the shared infrastructure inventory, the 7-step
      operator runbook, and the failure responses are unchanged.
  - version: 1.0.0
    date: 2026-05-26
    summary: |
      Initial authoring. Six validators (PV-0..PV-5), one per Plan phase.
---

# Phase Validators: Pipeline Quick-Wins Hardening (Round 1)

## Contents

- Purpose
- Source
- Conventions
- PV-0 — Setup validator
- PV-1 — Claude Code foundation validator
- PV-2 — Codespaces validator
- PV-3 — CI/CD validator
- PV-4 — Bundle finalization validator
- PV-5 — Rollout validator
- Cross-validator coordination
- Open items

## Purpose

This document defines six Phase Validators (PV-0 through PV-5), one per Plan phase. Each Phase Validator is the gate that must pass before the next phase may begin. The validators are coarser-grained than the per-task L1/L2/L3 verification steps already in the Plan and coarser-grained than the per-AC acceptance tests authored in parallel. They answer one question: "Is this phase complete enough that the next phase can safely start?"

The validators are designed to be runnable as a discrete operational step at each phase boundary — not as continuous checks woven into individual tasks. Each criterion is concrete enough to be automated or manually checked against an unambiguous artifact, and each has a severity that determines whether failure blocks the phase or only warns.

## Source

- **Plan**: `working/feature/pipeline-quickwins-hardening-r1/plan-v1.md` (v1.0.1; 36 tasks across 6 phases).
- **PRD**: `working/feature/pipeline-quickwins-hardening-r1/prd-v1.md` (v0.3.0).
- **Blueprint**: `working/feature/pipeline-quickwins-hardening-r1/blueprint-v2.md` (v2.2.0).
- **Acceptance tests**: authored in parallel by `test-acceptance-author`; AC IDs in this document cite the PRD/Blueprint directly. When the acceptance-test document is finalized, the AC IDs map 1-to-1 to its `AT-NNN` entries.

## Conventions

### Criterion IDs

Each criterion carries an ID of the form `PV-<phase>.C<n>` (e.g. `PV-1.C3`). Stable across revisions; new criteria append at the end of each validator.

### Severity

| Severity | Meaning | Effect on phase advancement |
|---|---|---|
| BLOCKER | Load-bearing for the phase. Failure means the phase has not met its exit criteria. | Phase cannot advance until resolved. |
| MAJOR | Phase is functionally complete but a check the Plan called out has not been confirmed. | Phase may advance only with an explicit operator deferral decision (recorded). |
| MINOR | Cosmetic or informational; the Plan would not be blocked by this alone. | Recorded; does not block advancement. |

The severity rules below follow the Plan's `L3 verification` and "Phase Exit Criteria" sections: anything the Plan calls a phase exit criterion is BLOCKER; anything called out as cosmetic or "informational budget" is MINOR; the in-between is MAJOR.

### Automation hooks

Each criterion lists where the check runs: a script path, a workflow file, an MCP tool invocation, or a manual checklist by a named role. Where the auditing-mcp script set is referenced, the script is at `.claude/skills/auditing-mcp/scripts/<name>.py` or `.claude/skills/auditing-shared/scripts/<name>.py`.

### Failure response

Each validator's "Failure response" section names the rollback / remediation path the Plan implies. For Phases 0-4, failure rolls back at the task level (no commit yet to revert) — the implementor fixes the failing criterion and re-runs the validator. For Phase 5, failure invokes the PRD's kill-criteria procedure (revert the offending mechanism via the bundled-PR per-mechanism revert path, open a follow-up Issue).

---

## PV-0 — Setup validator

### Phase reference

Plan §Phase 0 — Setup. Five tasks: T0.1 (branch + clean tree), T0.2 (SHA pins), T0.3 (ADR-0041 row anchors), T0.4 (`postCreate.sh` line 197-198 anchor), T0.5 (tool availability).

### Validator goal

Confirm the working branch is set up and the four required pre-implementation discovery artifacts (SHA pins, ADR-0041 row anchors, `postCreate.sh` anchor, tooling check) all exist on disk and are well-formed. After this validator passes, Phase 1 has stable inputs.

### Pass criteria

#### PV-0.C1 — Working branch exists and is pushed

- **Description:** Branch `feature/pipeline-quickwins-hardening-r1` exists locally, is checked out, and has been pushed to remote.
- **Assertion:** `git branch --show-current` returns `feature/pipeline-quickwins-hardening-r1`; `git status` reports a clean working tree; `git ls-remote --heads origin feature/pipeline-quickwins-hardening-r1` returns a SHA.
- **Source:** T0.1 L1/L3.
- **Automation hook:** manual check by implementor at phase boundary; trivially scriptable as a shell one-liner.
- **Severity:** BLOCKER.

#### PV-0.C2 — SHA pins resolved and well-formed

- **Description:** SHA pins for `actions/checkout` and `devcontainers/ci` are recorded and match the 40-char hex format.
- **Assertion:** `working/feature/pipeline-quickwins-hardening-r1/sha-pins.md` exists; contains two SHA values each matching `^[a-f0-9]{40}$`; each SHA is annotated with its source URL.
- **Source:** T0.2 L1/L2.
- **Automation hook:** shell — `grep -Eo '[a-f0-9]{40}' working/feature/pipeline-quickwins-hardening-r1/sha-pins.md | wc -l` returns at least 2; `grep -E '^[a-f0-9]{40}$' working/feature/pipeline-quickwins-hardening-r1/sha-pins.md` produces only valid hex SHAs (no version tags like `v4` or `v0.3.1900000417`).
- **Severity:** BLOCKER. Per Blueprint Implementation Plan §SHA-pinning and per KB-github-actions-platform non-negotiable #1, tag pins for `devcontainers/ci` are unacceptable.

#### PV-0.C3 — ADR-0041 row 70 + row 71 anchors captured verbatim

- **Description:** The current Form-column text for ADR-0041 rows 70 (Serena) and 71 (`mcp-openapi-schema`) is captured to a working note so T1.5 can apply the `[DEPRECATED INVOCATION FORM]` annotations without re-reading the ADR.
- **Assertion:** `working/feature/pipeline-quickwins-hardening-r1/adr-0041-anchors.md` exists; records both row 70's and row 71's verbatim Form-column text; the recorded text string-matches against the live `adrs/ADR-0041-install-mechanism-hybrid.md`.
- **Source:** T0.3 L1/L2.
- **Automation hook:** shell — for each captured anchor, `grep -F "<captured-fragment>" adrs/ADR-0041-install-mechanism-hybrid.md` returns at least one match.
- **Severity:** BLOCKER.

#### PV-0.C4 — `postCreate.sh` line 197-198 insertion anchor captured

- **Description:** The FR-4a insertion site between `install_terraform_mcp` and `install_gitnexus` is captured (line number + 3-line context fragment above and below) so T2.2 can insert the FR-4a block at the correct location.
- **Assertion:** `working/feature/pipeline-quickwins-hardening-r1/postcreate-anchor.md` exists; records a line number plus 3-line context fragments; the context fragments string-match against the current `.devcontainer/postCreate.sh`.
- **Source:** T0.4 L1/L2.
- **Automation hook:** shell — `grep -F "$(head -1 working/feature/pipeline-quickwins-hardening-r1/postcreate-anchor.md context section)" .devcontainer/postCreate.sh` returns a match. Implementation may use a small Python script that loads the anchor note and grep-matches the fragments.
- **Severity:** BLOCKER.

#### PV-0.C5 — Required tooling present (or fallbacks documented)

- **Description:** The six tools the Plan invokes (`actionlint`, `jq`, `python3`, `bash`, `mktemp`, `gh`) are on PATH or have a documented fallback.
- **Assertion:** `working/feature/pipeline-quickwins-hardening-r1/tooling-check.md` exists and records, for each of the six tools, either a `--version` output or an explicit fallback path. The first three of those (`jq`, `python3`, `npx`) MUST be on PATH (no fallback acceptable) per the dispatch prompt's named-tool check; `actionlint` may rely on the `mcp__actionlint-mcp__lint_workflow` MCP fallback.
- **Source:** T0.5 L1/L2.
- **Automation hook:** shell — `for t in jq python3 npx; do command -v "$t" >/dev/null || { echo "missing: $t"; exit 1; }; done`; `command -v actionlint || grep -q "fallback available" working/feature/pipeline-quickwins-hardening-r1/tooling-check.md`.
- **Severity:** BLOCKER for `jq`, `python3`, `npx` (no fallback). MAJOR for `actionlint` (MCP fallback acceptable). MINOR for `gh`/`bash`/`mktemp` (universally available on dev environments — recorded for completeness).

### Acceptance tests scheduled for this phase

None — Phase 0 is setup-only. The Plan marks every Phase 0 task `Satisfies AC: N/A — setup` except T0.2 which is transitive-only.

### Operational checks

- Working branch is current with `main` (no rebase debt before Phase 1 starts).
- The codebase-analysis JSON (`working/feature/pipeline-quickwins-hardening-r1/codebase-analysis.json`) is reachable for downstream phases' fact-citation needs.
- The Plan v1.0.1, Blueprint v2.2.0, and PRD v0.3.0 are all in `working/feature/pipeline-quickwins-hardening-r1/` (no broken references).

### Failure response

Task-level: if any criterion fails, the implementor re-runs the corresponding T0.x task. No commits exist to revert. Phase 0 has no rollback; it is the rollback baseline for Phase 1.

### Validator metadata

- **When run:** after T0.5 completes, before T1.1 starts.
- **Expected duration:** under 60 seconds (all checks are file-presence + grep + version-string).
- **Prerequisites:** none.

---

## PV-1 — Claude Code foundation validator

### Phase reference

Plan §Phase 1 — Claude Code foundation. Nine tasks: T1.1 (ADR-0057), T1.2 (ADR-0058), T1.3 (FR-1 validator script), T1.4 (FR-3 OP-11 audit script), T1.5 (ADR-0041 row 70+71 annotations), T1.6 (`scope_class` hoist), T1.7 (FR-2 self-check), T1.8 (FR-1 wire-in at 9 reviewer-completion sites), T1.9 (`auditing-mcp/SKILL.md` OP-11 routing).

### Validator goal

Confirm the Claude-Code-layer foundation is in place: both new ADRs exist at their canonical paths with `status: accepted`, both new scripts exist and pass their fixture suites, the orchestrator SKILL.md carries the FR-1 wire-in at 9 sites + the FR-2 self-check + the hoisted `scope_class` read, and ADR-0041 carries the `[DEPRECATED INVOCATION FORM]` annotations on rows 70 and 71.

### Pass criteria

#### PV-1.C1 — ADR-0057 v1.0.1 exists at canonical path with `status: accepted`

- **Description:** `adrs/ADR-0057-checkpoint-execution-mode-first-class-field.md` is on disk with the v1.0.1 frontmatter and is placement-compliant per ADR-0036 + ADR-0056.
- **Assertion:** File exists; frontmatter parses; `version: 1.0.1`; `status: accepted`; `change_summary` matches the v1.0.0 → v1.0.1 prose-only amendment text the Plan T1.1 specifies; `python3 .claude/skills/auditing-shared/scripts/validate_adr_placement.py` returns exit 0 with no findings against this ADR.
- **Source:** T1.1 L1.
- **Automation hook:** `python3 .claude/skills/auditing-shared/scripts/validate_adr_placement.py` (placement); shell — `python3 -c "import yaml; d = yaml.safe_load(open('adrs/ADR-0057-checkpoint-execution-mode-first-class-field.md').read().split('---')[1]); assert d['version'] == '1.0.1' and d['status'] == 'accepted'"`.
- **Severity:** BLOCKER.

#### PV-1.C2 — ADR-0058 v1.0.0 exists at canonical path with `status: accepted`

- **Description:** `adrs/ADR-0058-calibration-result-event-type-additive-extension.md` is on disk with v1.0.0 frontmatter, `status: accepted`, citing ADR-0037 v1.0.2, declaring the four-value closed enum and the `mechanism:` discriminator.
- **Assertion:** File exists; frontmatter parses; `version: 1.0.0`; `status: accepted`; `supersedes: none`; body contains the four enum values verbatim (`install_complete`, `readiness_probe`, `structured_failure`, `calibration_result`); body contains the literal string `ADR-0037`; body documents the canonical payload shape; placement validator passes.
- **Source:** T1.2 L1/L2.
- **Automation hook:** `python3 .claude/skills/auditing-shared/scripts/validate_adr_placement.py`; shell — `grep -c -E '(install_complete|readiness_probe|structured_failure|calibration_result)' adrs/ADR-0058-calibration-result-event-type-additive-extension.md` returns >= 4.
- **Severity:** BLOCKER.

#### PV-1.C3 — `verdict_findings_parity.py` exists and passes the 4-phase quality check

- **Description:** `.claude/skills/auditing-shared/scripts/verdict_findings_parity.py` exists, parses as Python, exposes a `--help` and runs a `--selftest` against the fixture suite covering AC-FR-1-a (pass-through), AC-FR-1-b (blocking finding + approving verdict), AC-FR-1-c (no findings).
- **Assertion:** File exists; `python3 -c "import ast; ast.parse(open('.claude/skills/auditing-shared/scripts/verdict_findings_parity.py').read())"` returns exit 0; `python3 .claude/skills/auditing-shared/scripts/verdict_findings_parity.py --help` returns exit 0; `python3 .claude/skills/auditing-shared/scripts/verdict_findings_parity.py --selftest` (or the equivalent fixture-runner per T1.3 L2) returns exit 0.
- **Source:** T1.3 L1/L2/L3.
- **Automation hook:** the four-phase quality check from the dispatch prompt — `python3 .claude/skills/auditing-shared/scripts/verdict_findings_parity.py --selftest`.
- **Severity:** BLOCKER.

#### PV-1.C4 — `audit_op11_adr_parity.py` exists, passes fixture suite, and integrates with the auditing-mcp dispatch

- **Description:** `.claude/skills/auditing-mcp/scripts/audit_op11_adr_parity.py` exists, parses, runs its fixture suite (matching entry / drifted argv / drifted env-var / missing prescription / deprecated row skip) clean, and is dispatched from `.claude/skills/auditing-mcp/SKILL.md`'s OP-rule routing table.
- **Assertion:** File exists; ast-parses; `--selftest` exits 0; `.claude/skills/auditing-mcp/SKILL.md` contains the literal string `OP-11` and references `audit_op11_adr_parity.py`; `.claude/skills/auditing-mcp/references/adr-parity.md` exists.
- **Source:** T1.4 L1/L2; T1.9 L1.
- **Automation hook:** `python3 .claude/skills/auditing-mcp/scripts/audit_op11_adr_parity.py --selftest`; shell — `grep -E 'OP-11.*audit_op11_adr_parity' .claude/skills/auditing-mcp/SKILL.md`.
- **Severity:** BLOCKER.

#### PV-1.C5 — ADR-0041 rows 70 and 71 carry `[DEPRECATED INVOCATION FORM]` annotations

- **Description:** Both deprecated-form rows in ADR-0041's invocation-taxonomy table carry the inline annotation marker per Plan T1.5.
- **Assertion:** `adrs/ADR-0041-install-mechanism-hybrid.md` contains the literal string `[DEPRECATED INVOCATION FORM` on both row 70 (Serena) and row 71 (`mcp-openapi-schema`). For row 71, the annotation must include the `removed 2026-05-24` qualifier per T1.5 description; for row 70, the annotation must reference the canonical invocation path per `postCreate.sh:82 + .mcp.json:28-31`.
- **Source:** T1.5 L1/L2.
- **Automation hook:** shell — `grep -c '\[DEPRECATED INVOCATION FORM' adrs/ADR-0041-install-mechanism-hybrid.md` returns >= 2; `grep -F 'removed 2026-05-24' adrs/ADR-0041-install-mechanism-hybrid.md` returns at least one match.
- **Severity:** BLOCKER. Required by both T1.4's L3 (OP-11 against live `.mcp.json` returns exit 0 only when the deprecated rows are skipped) and T1.5's L3.

#### PV-1.C6 — OP-11 against live `.mcp.json` + ADR-0041 returns exit 0 (day-one no-false-positives)

- **Description:** Closing the loop: with `audit_op11_adr_parity.py` and the ADR-0041 annotations both in place, running the rule against the live `.mcp.json` produces no findings. This proves NFR-10 backward compatibility on day one.
- **Assertion:** `python3 .claude/skills/auditing-mcp/scripts/audit_op11_adr_parity.py` (no fixture arg; default = repo `.mcp.json` + repo `adrs/ADR-0041-*.md`) exits 0 with no findings on stderr.
- **Source:** T1.4 L3.
- **Automation hook:** `python3 .claude/skills/auditing-mcp/scripts/audit_op11_adr_parity.py`.
- **Severity:** BLOCKER. This is the load-bearing NFR-10 check.

#### PV-1.C7 — `recipe-feature-pipeline/SKILL.md` carries `scope_class` hoist + FR-2 self-check + 9 FR-1 invocations

- **Description:** The three orchestrator-SKILL.md edits (T1.6, T1.7, T1.8) have landed; one file inspection covers all three.
- **Assertion:** `.claude/skills/recipe-feature-pipeline/SKILL.md` (i) contains `scope_class` at a new dispatch-entry section AND at the existing line ~350 (Stage 13) site (two read sites); (ii) contains the FR-2 dispatch self-check block with the four FR-6 diagnostic fields named (mechanism, offending artifact, rule, remedial hint) in the on-refusal path; (iii) contains exactly 9 invocations of `verdict_findings_parity.py`.
- **Source:** T1.6 L1; T1.7 L1; T1.8 L1.
- **Automation hook:** shell — `grep -c 'scope_class' .claude/skills/recipe-feature-pipeline/SKILL.md` returns >= 2; `grep -c 'verdict_findings_parity.py' .claude/skills/recipe-feature-pipeline/SKILL.md` returns exactly 9; `grep -E 'parent-driven-workaround|scope_class.*FULL' .claude/skills/recipe-feature-pipeline/SKILL.md` returns at least one match for the FR-2 self-check.
- **Severity:** BLOCKER.

#### PV-1.C8 — FR-2 self-check fixture smoke + AC-CC-2-g pre-feature checkpoint resume both pass

- **Description:** T1.7's fixture smoke is exercised end-to-end: a FULL-scope fixture with one stage `execution_mode: parent-driven-workaround` triggers the refusal; a counter-fixture with MINOR-scope passes (AC-FR-2-c); a pre-feature checkpoint (no `execution_mode` field) maps to `specialist-dispatch` per ADR-0057 absence-default and passes the self-check (AC-CC-2-g).
- **Assertion:** Three orchestrator runs against the three fixtures (under `working/feature/pipeline-quickwins-hardening-r1/fixtures/fr2/`) produce the expected refuse / pass / pass outcomes.
- **Source:** T1.7 L2/L3.
- **Automation hook:** fixture-driven test harness — implementor invokes the orchestrator against each fixture and captures the orchestrator's `system/init`-equivalent output. May be deferred to T4.6 for the full AC-CC-2-g smoke; the BLOCKER bar here is the fixture-driven L2.
- **Severity:** BLOCKER for the L2 fixture smoke. MAJOR for the AC-CC-2-g pre-feature resume smoke (the Plan defers the load-bearing smoke to T4.6; if T4.6 has not yet run, surface as MAJOR rather than BLOCKER at this phase boundary).

### Acceptance tests scheduled for this phase

AT-NNN cross-references per Acceptance Tests v1.0.1 Coverage Matrix. PRD-original `AC-FR-N-x` IDs are aliases for their Blueprint-expanded forms (per Acceptance Tests v1.0.1 §Coverage Matrix preamble); the AT IDs below are the canonical mapping.

- **AC-FR-1-a, AC-FR-1-b, AC-FR-1-c** (FR-1 validator structural cases — exit codes for the three reviewer-output shapes) → aliased to AC-CC-1-a/b/c → AT-001, AT-002, AT-003, AT-004.
- **AC-CC-1-a through AC-CC-1-h** (FR-1 orchestrator wire-in; AC-CC-1-a is the "9 invocation sites" check) → AT-001 (AC-CC-1-a), AT-002 + AT-003 (AC-CC-1-b), AT-004 (AC-CC-1-c and AC-CC-1-d), AT-005 (AC-CC-1-e), AT-006 (AC-CC-1-f), AT-007 (AC-CC-1-g), AT-008 (AC-CC-1-h).
- **AC-FR-2-a, AC-FR-2-b, AC-FR-2-c** (FR-2 self-check structural cases) → aliased to AC-CC-2-a/b/c → AT-009, AT-010, AT-011.
- **AC-CC-2-a through AC-CC-2-f** (FR-2 orchestrator integration; AC-CC-2-g is reserved for Phase 4's T4.6 smoke) → AT-009 (AC-CC-2-a), AT-010 (AC-CC-2-b), AT-011 (AC-CC-2-c), AT-012 (AC-CC-2-d), AT-013 (AC-CC-2-e), AT-014 (AC-CC-2-f).
- **AC-FR-3-a, AC-FR-3-b, AC-FR-3-c** (FR-3 OP-11 rule structural cases) → aliased to AC-CC-3-a/b/c → AT-016, AT-017, AT-018.
- **AC-CC-3-a through AC-CC-3-l** (FR-3 audit-skill integration) → AT-016 (AC-CC-3-a), AT-017 (AC-CC-3-b), AT-018 (AC-CC-3-c), AT-019 (AC-CC-3-d), AT-020 (AC-CC-3-e), AT-021 (AC-CC-3-f), AT-022 (AC-CC-3-g), AT-023 (AC-CC-3-h), AT-024 (AC-CC-3-i), AT-025 (AC-CC-3-j), AT-026 (AC-CC-3-k), AT-027 (AC-CC-3-l).
- **AC-NFR-1-a** (FR-1 latency threshold) → AT-075.
- **AC-NFR-2-a** (FR-2 self-check determinism / latency) → AT-076.
- **AC-NFR-10-a** (FR-3 day-one no-false-positives — load-bearing for PV-1.C6) → AT-022 (shared with AC-CC-3-g).

### Operational checks

- The FR-1 validator's fixture suite includes one fixture per Discovery-scope reviewer-output shape (the 9-sites sweep per cc-design v0.2.0).
- The FR-3 OP-11 rule's canonicalize+opaque-tokens algorithm matches the U-3 resolution recorded in cc-design v0.2.0 (verified by inspection of `audit_op11_adr_parity.py` against the reference doc `references/adr-parity.md`).
- `auditing-mcp/SKILL.md`'s OP-rule routing table references OP-11 (the CLAUDE.md counter bump is deferred to Phase 4 T4.2 — not a PV-1 BLOCKER).

### Failure response

Task-level. Re-run the failing T1.x task. If multiple criteria fail, attend to them in dependency order: ADR files first (PV-1.C1, PV-1.C2), then scripts (PV-1.C3, PV-1.C4), then the SKILL.md edits (PV-1.C7), then the smoke (PV-1.C8). PV-1.C6 typically fails because PV-1.C5 has not landed yet — fix PV-1.C5 first.

### Validator metadata

- **When run:** after T1.9 completes, before T2.1 starts.
- **Expected duration:** under 5 minutes (script `--selftest` calls + grep + one OP-11 invocation against the live repo).
- **Prerequisites:** PV-0 passed.

---

## PV-2 — Codespaces validator

### Phase reference

Plan §Phase 2 — Codespaces. Eight tasks: T2.1 (OP-7 schema extension), T2.2 (FR-4a static-shape block), T2.3 (Q-CS-1b banner adjacent to FR-4a), T2.4 (FR-4b calibration script), T2.5 (FR-4b emission integration), T2.6 (cosmetic 5→4 fix), T2.7 (KB-mcp-design update), T2.8 (KB-mcp-platform update).

### Validator goal

Confirm the Codespaces layer is in place: OP-7 admits `calibration_result`; `postCreate.sh` carries the FR-4a static-shape block and the Q-CS-1b staleness banner adjacent to it; the FR-4b calibration script exists, is executable, and produces a well-formed `calibration_result` event admitted by OP-7; the cosmetic 5→4 fix has landed; the KB documentation reflects the four-type vocabulary.

### Pass criteria

#### PV-2.C1 — OP-7 schema admits `calibration_result` as the fourth valid event type

- **Description:** `audit_op7_events_schema.py` admits `calibration_result` and its nine canonical fields per ADR-0058. The three pre-existing event types are preserved.
- **Assertion:** `.claude/skills/auditing-mcp/scripts/audit_op7_events_schema.py` contains the literal string `"calibration_result"` in the `VALID_EVENT_TYPES` set; a fixture `mcp-events.jsonl` containing a well-formed `calibration_result` event passes OP-7 (exit 0); a fixture missing one of the nine required fields produces exit 1 with a MAJOR finding naming the missing field.
- **Source:** T2.1 L1/L2.
- **Automation hook:** `python3 .claude/skills/auditing-mcp/scripts/audit_op7_events_schema.py working/feature/pipeline-quickwins-hardening-r1/fixtures/op7/well-formed-calibration.jsonl` (expect 0); same with `.../missing-field.jsonl` (expect 1 with MAJOR finding).
- **Severity:** BLOCKER. Per Blueprint §Implementation Plan task 12 sequencing constraint — without this, every FR-4b emission triggers an OP-7 MAJOR finding.

#### PV-2.C2 — FR-4a static-shape block present at the captured anchor in `postCreate.sh`

- **Description:** The FR-4a block is inserted between `install_terraform_mcp` (line ~197) and `install_gitnexus` (line ~198) at the anchor captured by PV-0.C4. Block performs the four assertions A1/A2/A3/A4 per AC-CS-4a-1 and emits a `structured_failure` event with the four FR-6 fields on any failure.
- **Assertion:** `bash -n .devcontainer/postCreate.sh` exits 0; the FR-4a block string-matches the PV-0.C4 anchor (insertion point preserved); the block contains the four signal-token literals (`signal-a1-env-var-unset-or-wrong`, `signal-a2-tag-pin-malformed`, `signal-a3-versions-env-mismatch`, `signal-a4-artifact-paths-unpredictable`); the block does NOT invoke `npm install`; top-level placement (not inside `install_gitnexus()`).
- **Source:** T2.2 L1.
- **Automation hook:** `bash -n .devcontainer/postCreate.sh`; shell — `grep -c -F 'signal-a' .devcontainer/postCreate.sh` returns >= 4; `awk` block that confirms the FR-4a block sits at top level (zero indentation; not nested in a function body).
- **Severity:** BLOCKER.

#### PV-2.C3 — Q-CS-1b staleness banner block adjacent to FR-4a, informational (does not fail-close)

- **Description:** The Q-CS-1b banner sits between the FR-4a block and `install_gitnexus`, reads the most recent `calibration_result` event for `mechanism: "fr-4b-gitnexus-grammar-skip"`, emits one of three banner variants, and uses `|| true` to guarantee it cannot fail-close under `set -euo pipefail`.
- **Assertion:** The banner block in `.devcontainer/postCreate.sh` uses `jq` with `|| true`; emits to stderr (not stdout); does not write to `mcp-events.jsonl`; three fixture rebuilds (no event / 3-week-old event / 3-day-old event) produce the expected NEVER RUN / STALE / silent variants and all three rebuilds complete exit 0.
- **Source:** T2.3 L1/L2.
- **Automation hook:** shell — `grep -E 'jq.*\|\| true' .devcontainer/postCreate.sh` returns at least one match in the banner block; three-fixture rebuild smoke (the full smoke is also T4.5; the PV-2 bar is the L2 fixture rebuild).
- **Severity:** BLOCKER for the structural checks (jq+`|| true` guard; banner-not-event); MAJOR for the three-fixture rebuild smoke at PV-2 boundary (full smoke is T4.5; if not yet run, surface as MAJOR).

#### PV-2.C4 — FR-4b script exists, executable, emits one schema-valid `calibration_result` event

- **Description:** `.devcontainer/scripts/calibrate-gitnexus-grammar-skip.sh` exists, is `mode 0755`, parses as bash, and when invoked against the current `gitnexus@1.6.5` pin: (i) exits 0; (ii) writes exactly one new line to `.claude/runtime/mcp-events.jsonl`; (iii) the line is a valid `calibration_result` event per ADR-0058 (nine required fields present); (iv) the line passes OP-7 schema validation.
- **Assertion:** File exists at the exact path; `bash -n .devcontainer/scripts/calibrate-gitnexus-grammar-skip.sh` exits 0; `[ -x .devcontainer/scripts/calibrate-gitnexus-grammar-skip.sh ]` is true; one invocation produces exactly one new JSONL line; the line has `event == "calibration_result"`, `mechanism == "fr-4b-gitnexus-grammar-skip"`, `version` matching the pinned `GITNEXUS_TAG`, and all of `timestamp`/`server`/`duration_ms`/`outcome`/`signals`/`note` present; OP-7 admits the event.
- **Source:** T2.4 L1/L2; T2.5 L1/L2/L3.
- **Automation hook:** `bash .devcontainer/scripts/calibrate-gitnexus-grammar-skip.sh` (capture exit code and the diff in `mcp-events.jsonl`); `python3 .claude/skills/auditing-mcp/scripts/audit_op7_events_schema.py .claude/runtime/mcp-events.jsonl` (expect 0); `jq '.event,.mechanism,.version' <new-event-line>`.
- **Severity:** BLOCKER.

#### PV-2.C5 — Cosmetic 5→4 fix landed on line 5 of `postCreate.sh`

- **Description:** Line 5 of `.devcontainer/postCreate.sh` reads `# pattern for idempotency. Installs the 4 OSS-local MCP servers, emits one` (digit `4`, not `5`).
- **Assertion:** `awk 'NR==5' .devcontainer/postCreate.sh` returns a line containing the literal `4 OSS-local MCP servers`; no other lines changed in this edit (`git diff --stat .devcontainer/postCreate.sh` shows line 5 modified; other line changes in the same file are attributable to T2.2/T2.3/T2.4 only).
- **Source:** T2.6 L1/L2.
- **Automation hook:** shell — `awk 'NR==5' .devcontainer/postCreate.sh | grep -F '4 OSS-local MCP servers'`.
- **Severity:** MINOR. Cosmetic per Blueprint §Q-CS-3 disposition. Does not block phase advance.

#### PV-2.C6 — KB-mcp-design and KB-mcp-platform documentation reflects the four-type vocabulary

- **Description:** Both KB doc updates (T2.7 and T2.8) have landed; the schema-home reference adds the fourth-type entry with citations to ADR-0058 and ADR-0037 v1.0.2; the usage-docs reference adds an example `calibration_result` record and documents `mechanism:` as discriminator.
- **Assertion:** `.claude/skills/KB-mcp-design/references/principles.md` contains `calibration_result` and `ADR-0058`; `.claude/skills/KB-mcp-platform/references/mcp-events-jsonl.md` contains a JSON Lines `calibration_result` example record and references `mechanism:`; both files' diffs are additive (no removals from the three pre-existing type entries).
- **Source:** T2.7 L1/L2; T2.8 L1/L2.
- **Automation hook:** shell — `grep -l calibration_result .claude/skills/KB-mcp-design/references/principles.md .claude/skills/KB-mcp-platform/references/mcp-events-jsonl.md` returns both files; `git diff main -- .claude/skills/KB-mcp-design/references/principles.md` shows only additions (no `-` lines outside metadata).
- **Severity:** MAJOR. The Plan classifies these as mechanical edits; if missed the feature still ships but the schema-home documentation drifts.

### Acceptance tests scheduled for this phase

AT-NNN cross-references per Acceptance Tests v1.0.1 Coverage Matrix. PRD-original `AC-FR-4a-x` / `AC-FR-4b-x` IDs are aliases for their Blueprint-expanded `AC-CS-4a-y` / `AC-CS-4b-y` forms; the AT IDs below are the canonical mapping.

- **AC-FR-4a-a through AC-FR-4a-d** (FR-4a fail-closed structural cases) → aliased to AC-CS-4a-1 fan-out → AT-028, AT-029, AT-030, AT-031 (one per A1/A2/A3/A4 signal).
- **AC-CS-4a-1 through AC-CS-4a-7** (FR-4a integration cases including the four signal tokens and the p95 < 100 ms budget at AC-CS-4a-6) → AT-028 + AT-029 + AT-030 + AT-031 (AC-CS-4a-1 A1..A4 fan-out), AT-032 (AC-CS-4a-2), AT-033 (AC-CS-4a-3), AT-034 (AC-CS-4a-4), AT-035 (AC-CS-4a-5), AT-036 (AC-CS-4a-6), AT-037 (AC-CS-4a-7).
- **AC-FR-4b-a through AC-FR-4b-d** (FR-4b script structural cases) → aliased to AC-CS-4b-1..AC-CS-4b-4 → AT-038, AT-039, AT-040, AT-041.
- **AC-CS-4b-1 through AC-CS-4b-7** (FR-4b integration cases including the optional negative-assertion at AC-CS-4b-1 step vi) → AT-038 (AC-CS-4b-1), AT-039 (AC-CS-4b-2), AT-040 (AC-CS-4b-3), AT-041 (AC-CS-4b-4), AT-042 (AC-CS-4b-5), AT-043 (AC-CS-4b-6), AT-044 (AC-CS-4b-7).
- **AC-X-2** (event surface admits exactly four types — the cross-feature contract) → AT-070.
- **AC-X-4** (Q-CS-1b banner contract) → AT-072, AT-073, AT-074 (three banner-variant fixtures).
- **AC-NFR-3-a** (FR-4a fail-closed determinism / sub-100 ms budget) → AT-036 (shared with AC-CS-4a-6).
- **AC-NFR-6-a** (fail-closed-vs-tracker discipline) → AT-005, AT-014, AT-026 (per-mechanism aggregator).
- **AC-NFR-7-a, AC-NFR-8-a** (no credentials in diagnostics — applies to FR-4a/FR-4b/FR-4c) → AC-NFR-7-a: AT-052 + AT-062 + AT-077; AC-NFR-8-a: AT-078.

### Operational checks

- The FR-4b script's `trap 'rm -rf' EXIT` covers both `scratch1` and `scratch2` (the optional negative-assertion's scratch dir).
- The FR-4b script does NOT write any `mcp-events.jsonl` event other than the single `calibration_result` (no `install_complete` or `readiness_probe` emissions from this script — those remain `install-mcp-server.sh`'s responsibility).
- The Q-CS-1b banner block's three banner variants exactly match the AC-X-4 prose (`NEVER RUN`, `STALE (last run <timestamp>, >2w ago). Suggest: ...`, silent).

### Failure response

Task-level. The Plan's critical path inside Phase 2 is T2.1 → T2.4 → T2.5; if PV-2.C1 fails, OP-7 schema extension must land before re-attempting PV-2.C4. If PV-2.C4 fails because the emitted event misses a required field, fix the FR-4b script's `log_mcp_event` call (do not work around by extending OP-7 to admit a partial event — that breaks ADR-0058's nine-field contract).

### Validator metadata

- **When run:** after T2.8 completes, before T3.1 starts.
- **Expected duration:** under 10 minutes (one FR-4b script invocation + OP-7 validation + grep checks; the longest step is the FR-4b script itself, AC-CS-4b-7 budget under 60 seconds).
- **Prerequisites:** PV-1 passed.

---

## PV-3 — CI/CD validator

### Phase reference

Plan §Phase 3 — CI/CD. Three tasks: T3.1 (FR-5 connectivity smoke workflow), T3.2 (FR-4c calibration workflow), T3.3 (atomic actionlint over both workflows).

### Validator goal

Confirm both new workflows exist, both lint clean under `actionlint`, both use the SHA pins resolved in PV-0.C2, and both have been exercised in pre-merge validation per cicd-design v0.3.0 §D-0010 (three `workflow_dispatch` runs each against the draft branch, all green, within p95 budgets).

### Pass criteria

#### PV-3.C1 — `mcp-connectivity-smoke.yml` (FR-5) exists, well-formed, and SHA-pinned

- **Description:** `.github/workflows/mcp-connectivity-smoke.yml` is on disk; YAML parses; declares `timeout-minutes: 8`, `permissions: contents: read`, the documented triggers (`pull_request.paths` + `workflow_dispatch`); cites the resolved SHAs for `actions/checkout` and `devcontainers/ci` (matching PV-0.C2).
- **Assertion:** File exists; `python3 -c "import yaml; yaml.safe_load(open('.github/workflows/mcp-connectivity-smoke.yml'))"` exits 0; `grep -E 'timeout-minutes:\s*8' .github/workflows/mcp-connectivity-smoke.yml`; `grep -E 'permissions:' -A 2 .github/workflows/mcp-connectivity-smoke.yml` shows `contents: read` and no other permissions; the two SHAs from PV-0.C2 each string-match in the file.
- **Source:** T3.1 L1.
- **Automation hook:** YAML parser + shell greps; SHA comparison against PV-0.C2's `sha-pins.md`.
- **Severity:** BLOCKER.

#### PV-3.C2 — `gitnexus-grammar-skip-calibration.yml` (FR-4c) exists, well-formed, and SHA-pinned

- **Description:** `.github/workflows/gitnexus-grammar-skip-calibration.yml` is on disk; YAML parses; declares `timeout-minutes: 5`, `permissions: contents: read`, `concurrency: { group: gitnexus-calibration, cancel-in-progress: false }`, the documented triggers (`schedule: '0 7 * * 1'` + `pull_request.paths` + `workflow_dispatch`); cites the same two SHAs as FR-5 (one per action).
- **Assertion:** File exists; YAML parses; `grep -E 'timeout-minutes:\s*5' .github/workflows/gitnexus-grammar-skip-calibration.yml`; `grep -E 'cron:.*0 7 \* \* 1' .github/workflows/gitnexus-grammar-skip-calibration.yml`; `grep -E 'concurrency:' -A 2 .github/workflows/gitnexus-grammar-skip-calibration.yml` shows `group: gitnexus-calibration` and `cancel-in-progress: false`; SHAs match PV-0.C2.
- **Source:** T3.2 L1.
- **Automation hook:** YAML parser + shell greps + cron-expression check (any parser).
- **Severity:** BLOCKER.

#### PV-3.C3 — Both workflows lint clean under `actionlint` atomically

- **Description:** Per Plan T3.3 and Blueprint Cross-Layer Sequencing Note: BOTH workflow files must pass `actionlint` together (or via the `mcp__actionlint-mcp__lint_workflow` MCP fallback). A half-committed `.github/workflows/` directory is not a valid intermediate state.
- **Assertion:** `actionlint .github/workflows/mcp-connectivity-smoke.yml .github/workflows/gitnexus-grammar-skip-calibration.yml` exits 0 with no findings; if the binary is absent, `mcp__actionlint-mcp__lint_workflow` invoked against each file returns no findings. No SHA-pin findings; no untrusted-input-interpolation findings; no permissions-block findings.
- **Source:** T3.3 L1/L2.
- **Automation hook:** `actionlint .github/workflows/*.yml` (primary); `mcp__actionlint-mcp__lint_workflow` per file (fallback, with graceful degradation if the MCP server's schema-validation issue is unresolved). On MCP fallback degrading, surface as MAJOR rather than BLOCKER per the dispatch prompt note.
- **Severity:** BLOCKER if `actionlint` binary is available; MAJOR if forced onto the MCP fallback and the MCP fallback degrades gracefully.

#### PV-3.C4 — Pre-merge `workflow_dispatch` validation per cicd-design v0.3.0 §D-0010

- **Description:** Three `workflow_dispatch` runs each for FR-5 and FR-4c against the draft branch. All six runs exit green. FR-5 p95 < 4 minutes; FR-4c p95 < 2 minutes. The `system/init`-event parsing path is confirmed for FR-5 (Q-CICD-8 pre-merge validation). The `concurrency` group is observed in the GitHub Actions UI for FR-4c. A fixture PR opening with a `versions.env` change confirms the FR-4c trigger fires.
- **Assertion:** `gh run list --workflow=mcp-connectivity-smoke.yml --branch feature/pipeline-quickwins-hardening-r1 --limit 3` returns three runs all with conclusion `success`; same for FR-4c; the runs' durations meet the p95 budgets; the `$GITHUB_STEP_SUMMARY` of one FR-5 run shows the `system/init`-event parsing output.
- **Source:** T3.1 L3; T3.2 L3.
- **Automation hook:** `gh run list` + `gh run view` for inspection; the p95 budget is checked manually against the three run durations or via a small `jq` script over `gh run list --json conclusion,duration`.
- **Severity:** BLOCKER. The cicd-design v0.3.0 §D-0010 pre-merge validation is the gate the Plan calls out for advancing to Phase 4.

### Acceptance tests scheduled for this phase

AT-NNN cross-references per Acceptance Tests v1.0.1 Coverage Matrix. PRD-original `AC-FR-5-x` / `AC-FR-4c-x` IDs are aliases for their Blueprint-expanded `AC-CICD-5-y` / `AC-CICD-4c-y` forms; the AT IDs below are the canonical mapping.

- **AC-FR-5-a, AC-FR-5-b, AC-FR-5-c** (FR-5 workflow structural) → aliased to AC-CICD-5-a/b/c → AT-056, AT-057, AT-058.
- **AC-CICD-5-a through AC-CICD-5-g** (FR-5 integration cases) → AT-056 (AC-CICD-5-a), AT-057 (AC-CICD-5-b), AT-058 (AC-CICD-5-c), AT-059 (AC-CICD-5-d), AT-060 (AC-CICD-5-e), AT-061 (AC-CICD-5-f), AT-062 (AC-CICD-5-g).
- **AC-FR-4c-a through AC-FR-4c-d** (FR-4c workflow structural) → aliased to AC-CICD-4c-1..AC-CICD-4c-4 → AT-045, AT-046, AT-047, AT-048.
- **AC-CICD-4c-1 through AC-CICD-4c-11** (FR-4c integration cases including AC-CICD-4c-9 — workflow does NOT re-implement Signal 1/3 logic — and AC-CICD-4c-10 — workflow does NOT write any `mcp-events.jsonl` event) → AT-045 (AC-CICD-4c-1), AT-046 (AC-CICD-4c-2), AT-047 (AC-CICD-4c-3), AT-048 (AC-CICD-4c-4), AT-049 (AC-CICD-4c-5), AT-050 (AC-CICD-4c-6), AT-051 (AC-CICD-4c-7), AT-052 (AC-CICD-4c-8), AT-053 (AC-CICD-4c-9), AT-054 (AC-CICD-4c-10), AT-055 (AC-CICD-4c-11).
- **AC-NFR-4-a** (FR-5 p95 budget) → AT-061 (shared with AC-CICD-5-f).
- **AC-NFR-4-b** (FR-4c p95 budget) → AT-050 (shared with AC-CICD-4c-6).
- **AC-FR-6-a** (FR-5 + FR-4c surfaces both carry the four FR-6 fields in their `$GITHUB_STEP_SUMMARY` on fail) → aliased to AC-6-a → AT-063 (cross-cutting aggregator across all five mechanisms; FR-5 + FR-4c facets exercised here).

### Operational checks

- FR-5 and FR-4c cite the SAME SHA for `actions/checkout` and the SAME SHA for `devcontainers/ci` (one resolution effort per action, two reuses — verified by SHA string-comparison across both files).
- FR-4c does not surface any signal-extraction logic that duplicates the FR-4b script (AC-CICD-4c-9).
- FR-4c does not write any `mcp-events.jsonl` event (AC-CICD-4c-10) — the script is the authoritative emitter.

### Failure response

Task-level. If `actionlint` surfaces a finding on either workflow, fix the workflow before committing (per Plan T3.3 — half-committed `.github/workflows/` is not a valid intermediate state). If pre-merge `workflow_dispatch` runs reveal p95 budget overruns, profile the offending step and either tune (e.g. enable devcontainer image caching via `cacheFrom`) or open a follow-up Issue and surface to user.

### Validator metadata

- **When run:** after T3.3 completes, before T4.1 starts.
- **Expected duration:** under 30 minutes (six `workflow_dispatch` runs cumulatively; runs themselves total ~18 min at the upper p95).
- **Prerequisites:** PV-2 passed (FR-4c depends on T2.4's FR-4b script existing in the devcontainer image).

---

## PV-4 — Bundle finalization validator

### Phase reference

Plan §Phase 4 — Bundle finalization. Seven tasks: T4.1 (FR-7 deferral-register), T4.2 (CLAUDE.md OP-counter bump), T4.3 (per-mechanism isolation smoke), T4.4 (end-to-end all-five smoke), T4.5 (Q-CS-1b banner integration smoke), T4.6 (pre-feature checkpoint resume smoke), T4.7 (open bundled PR).

### Validator goal

Confirm the bundle is finalized and ready to merge: FR-7 deferral-register rows H-4 and B-1 are adopted-by this feature; CLAUDE.md (via AGENTS.md) reflects the OP-1..OP-11 counter; all three pre-merge smokes (per-mechanism isolation, end-to-end all-five, Q-CS-1b banner integration, pre-feature checkpoint resume) pass; the single bundled PR is open and both CI workflows pass on it.

### Pass criteria

#### PV-4.C1 — FR-7 deferral-register rows H-4 and B-1 carry the adopted-by annotation

- **Description:** Both register rows reference `pipeline-quickwins-hardening-r1` as the adopting feature.
- **Assertion:** `Issues/devcontainer-mcp-provisioning-r1-deferrals/register.md` contains row H-4 and row B-1; both carry an adopted-by line referencing `pipeline-quickwins-hardening-r1`; diff against `main` shows changes only to those two rows (and any adjacent prose tightening).
- **Source:** T4.1 L1/L2.
- **Automation hook:** shell — `grep -E '(H-4|B-1).*pipeline-quickwins-hardening-r1' Issues/devcontainer-mcp-provisioning-r1-deferrals/register.md`; `git diff --stat main -- Issues/devcontainer-mcp-provisioning-r1-deferrals/register.md` confirms a minimal diff.
- **Severity:** BLOCKER. Per Blueprint §D-0009, the register update lands in this bundle.

#### PV-4.C2 — CLAUDE.md (via AGENTS.md) reflects OP-1..OP-11

- **Description:** The single-character counter update has landed at the auditing-mcp OP-rule reference site.
- **Assertion:** `AGENTS.md` (the canonical file behind the `CLAUDE.md` symlink) contains the literal `OP-1..OP-11` and does NOT contain `OP-1..OP-10` at the same site; `git diff main -- AGENTS.md` shows a single-character change.
- **Source:** T4.2 L1/L2.
- **Automation hook:** shell — `grep -F 'OP-1..OP-11' AGENTS.md`; `grep -F 'OP-1..OP-10' AGENTS.md` returns no match at the auditing-mcp counter site (one historical mention in a different context is acceptable; the load-bearing check is the counter site).
- **Severity:** BLOCKER.

#### PV-4.C3 — Per-mechanism isolation smoke (T4.3) passes for all five mechanisms

- **Description:** Each mechanism (FR-1, FR-2, FR-3, FR-4 family, FR-5) is exercised in isolation against a workspace where the other four are disabled. The FR-4 family is sub-divided into FR-4a / FR-4b / FR-4c sub-sub-smokes per AC-X-1.
- **Assertion:** A captured smoke log under `working/feature/pipeline-quickwins-hardening-r1/smoke/per-mechanism/` records each of the five sub-smokes (plus three FR-4 family sub-sub-smokes) and the captured output matches the expected fail/refuse/halt outcome on the named failure mode and the expected pass outcome on the negation.
- **Source:** T4.3 L1/L2/L3.
- **Automation hook:** smoke harness (Plan T4.3) — implementor records outputs to the per-mechanism directory; PV-4.C3 inspects the directory for the eight expected log files.
- **Severity:** BLOCKER. The Plan's AC-X-1 / NFR-11 per-mechanism isolation is load-bearing for the single-bundled-PR shape per D-0008.

#### PV-4.C4 — End-to-end all-five smoke (T4.4) passes, determinism confirmed

- **Description:** Orchestrator end-to-end with all five mechanisms enabled produces no false positives, no false negatives, no interaction failures; a repeat run produces byte-identical orchestrator outputs (determinism per AC-NFR-5-a); a fixture reviewer output the prior pipeline accepted continues to pass FR-1 (NFR-9 / AC-NFR-9-a).
- **Assertion:** Two consecutive end-to-end smoke runs against the same fixture produce identical orchestrator outputs; each of the five mechanisms' on-pass paths fires; the smoke log includes the FR-6-shaped diagnostics inspection for each mechanism.
- **Source:** T4.4 L1/L2/L3.
- **Automation hook:** orchestrator-driven smoke (Plan T4.4) + `diff` between the two run outputs; FR-6 inspection via `grep -E 'mechanism:|offending artifact:|rule:|remedial'` over the captured outputs.
- **Severity:** BLOCKER.

#### PV-4.C5 — Q-CS-1b banner integration smoke (T4.5) passes for all three fixture states

- **Description:** Three real devcontainer rebuilds with `.claude/runtime/mcp-events.jsonl` pre-populated in three states (no `calibration_result` event / 3-week-old event / 3-day-old event) produce the three expected banner variants. None of the three rebuilds fail-close because of the banner.
- **Assertion:** Smoke log under `working/feature/pipeline-quickwins-hardening-r1/smoke/qcs1b/` records three rebuilds; each rebuild's stderr matches the expected banner variant (NEVER RUN / STALE / silent); each rebuild exits 0.
- **Source:** T4.5 L1/L2/L3.
- **Automation hook:** smoke harness (Plan T4.5).
- **Severity:** BLOCKER.

#### PV-4.C6 — Pre-feature checkpoint resume smoke (T4.6) passes (AC-CC-2-g)

- **Description:** Orchestrator resumes against a pre-feature `checkpoint.json` (no `execution_mode` field on any stage). Per ADR-0057 absence-default, each stage maps to `execution_mode == "specialist-dispatch"`. The FR-2 self-check passes; the orchestrator runs to completion.
- **Assertion:** A fixture pre-feature checkpoint exists at `working/feature/pipeline-quickwins-hardening-r1/fixtures/pre-feature-checkpoint.json`; orchestrator resumed against this fixture exits clean; the FR-2 self-check did not refuse; the run-to-completion log is captured.
- **Source:** T4.6 L1/L2/L3.
- **Automation hook:** orchestrator-driven smoke (Plan T4.6).
- **Severity:** BLOCKER. AC-CC-2-g is the explicit migration smoke per ADR-0057.

#### PV-4.C7 — Single bundled PR open; both CI workflows green; all bundle files present

- **Description:** The single bundled PR per D-0008 is open on GitHub. PR title and description match the canonical shape (per Plan T4.7). The PR's diff includes every file the bundle requires; the two new CI workflows (FR-5 and FR-4c) both fire on the PR open and both exit green.
- **Assertion:** `gh pr view --json title,body,headRefName,state,statusCheckRollup` shows the PR is open on `feature/pipeline-quickwins-hardening-r1`; the title contains `feat(pipeline-quickwins-hardening-r1)`; the body references the PRD, Blueprint v2.2.0, ADR-0057 v1.0.1, ADR-0058 v1.0.0, and the deferral-register adoption; the `statusCheckRollup` shows both `mcp-connectivity-smoke` and `gitnexus-grammar-skip-calibration` with conclusion `success`. `gh pr view --json files` confirms the bundle's file list: at minimum the two ADR files, the two new scripts, the two new workflow files, the modified `postCreate.sh`, the modified `recipe-feature-pipeline/SKILL.md`, the modified `ADR-0041`, the modified `auditing-mcp/SKILL.md`, the modified `AGENTS.md`, the modified `register.md`, the modified two KB doc files, and (if T2.6 ran) the cosmetic 5→4 edit.
- **Source:** T4.7 L1/L2/L3.
- **Automation hook:** `gh pr view --json title,body,headRefName,state,statusCheckRollup,files`.
- **Severity:** BLOCKER.

### Acceptance tests scheduled for this phase

AT-NNN cross-references per Acceptance Tests v1.0.1 Coverage Matrix. PRD-original `AC-FR-7-a` / `AC-FR-6-a` / `AC-NFR-15` IDs are aliases for their Blueprint-expanded forms (`AC-CC-7-a..d` / `AC-6-a` / `AC-X-3`); the AT IDs below are the canonical mapping.

- **AC-FR-7-a, AC-CC-7-a through AC-CC-7-d** (FR-7 register adoption) → AT-064 (AC-CC-7-a), AT-065 (AC-CC-7-b), AT-066 (AC-CC-7-c), AT-067 (AC-CC-7-d).
- **AC-X-1** (NFR-11 per-mechanism isolation — load-bearing for PV-4.C3) → AT-068, AT-069.
- **AC-CC-2-g** (pre-feature checkpoint resume — load-bearing for PV-4.C6) → AT-015.
- **AC-X-4** (Q-CS-1b banner contract end-to-end via T4.5) → AT-072, AT-073, AT-074.
- **AC-NFR-5-a** (determinism — load-bearing for PV-4.C4) → AT-007 + AT-013 + AT-024 (per-mechanism aggregator across FR-1/FR-2/FR-3 facets).
- **AC-NFR-9-a** (existing-reviewer-output backward compatibility — load-bearing for PV-4.C4) → AT-008 (shared with AC-CC-1-h).
- **AC-NFR-11-a** (per-mechanism isolation — load-bearing for PV-4.C3) → AT-068, AT-069 (shared with AC-X-1).
- **AC-FR-6-a** (every mechanism's diagnostics include the four FR-6 fields — confirmed in PV-4.C4) → aliased to AC-6-a → AT-063.
- **AC-NFR-15** (agent-driven workflow remains accessible — confirmed by the CLAUDE.md counter bump being a single-character change) → aliased to AC-X-3 → AT-071.

### Operational checks

- The PR's commit list reflects a per-phase grouping for reviewer ergonomics (Plan T4.7).
- Both CI workflows fire on PR-open (FR-5 because `.mcp.json` and `.devcontainer/**` are in the diff; FR-4c because `.devcontainer/versions.env` and `.devcontainer/scripts/calibrate-gitnexus-grammar-skip.sh` are in the diff).
- The PR is approvable; the maintainer-reviewer (user) has approved (or is ready to approve).

### Failure response

Task-level until T4.7. If PV-4.C3 or PV-4.C4 fails (a smoke fails), the offending mechanism is fixed at the task level inside the bundle (no rollback yet — the bundle is not merged). If PV-4.C7 fails because CI on the PR is red, fix the offending mechanism, push, and re-run the validator. The single-bundled-PR shape is preserved.

### Validator metadata

- **When run:** after T4.7 completes (PR open + CI green), before T5.1.
- **Expected duration:** under 1 hour (the three smokes are the longest steps; per-mechanism isolation T4.3 with its eight sub-smokes is the longest single step).
- **Prerequisites:** PV-3 passed.

---

## PV-5 — Rollout validator

### Phase reference

Plan §Phase 5 — Rollout. Four tasks: T5.1 (merge to main), T5.2 (immediate post-merge `gh workflow run` for FR-4c), T5.3 (first cron tick observation), T5.4 (post-launch verification per PRD §Success Criteria).

### Validator goal

Confirm the bundle is merged, the post-merge banner-retirement workflow run has fired and produced the first real `calibration_result` event, the first Monday 07:00 UTC cron tick fires successfully, and the post-launch observation log against PRD §Success Criteria is open and accumulating evidence within the observation window.

### Pass criteria

#### PV-5.C1 — Bundle merged to `main`

- **Description:** The single bundled PR (per D-0008) is merged to `main`. The workflow files, scripts, ADRs, and all SKILL.md/KB.md edits are on `main`'s ref.
- **Assertion:** `git log --oneline main -5` shows the merge commit; `gh workflow list` shows both `mcp-connectivity-smoke.yml` and `gitnexus-grammar-skip-calibration.yml` registered on `main`.
- **Source:** T5.1 L1/L2.
- **Automation hook:** `gh pr view --json mergedAt,mergeCommit` returns a non-null `mergedAt`; `gh workflow list` returns both workflows.
- **Severity:** BLOCKER.

#### PV-5.C2 — Immediate post-merge `gh workflow run` succeeded; first `calibration_result` event landed

- **Description:** `gh workflow run gitnexus-grammar-skip-calibration.yml --ref main` was invoked within minutes of the merge. The run completed with conclusion `success`. One `calibration_result` event is now in `.claude/runtime/mcp-events.jsonl` (or recoverable from the workflow's run log per ADR-0037 implementation guidance; the file is gitignored).
- **Assertion:** `gh run list --workflow=gitnexus-grammar-skip-calibration.yml --limit 1 --branch main --json conclusion,event,createdAt` shows a recent run; `event` is `workflow_dispatch`; `conclusion` is `success`; the run's `$GITHUB_STEP_SUMMARY` shows a PASS block from the FR-4b script; the `mcp-events.jsonl` line (or the workflow log) confirms one new `calibration_result` event was written.
- **Source:** T5.2 L1/L2/L3.
- **Automation hook:** `gh run list --workflow=gitnexus-grammar-skip-calibration.yml --limit 1 --branch main`; `gh run view <run-id> --log` to confirm the event-write; grep the `mcp-events.jsonl` line for `event: "calibration_result"` if the file is locally reachable.
- **Severity:** BLOCKER. This is the terminal write-action of the entire feature — without it, the Q-CS-1b banner emits "NEVER RUN" on every operator's first post-merge rebuild.

#### PV-5.C3 — First Monday 07:00 UTC cron tick fires successfully within 2 weeks of merge

- **Description:** Within the first two Mondays after T5.1's merge, at least one `event: schedule` run of `gitnexus-grammar-skip-calibration.yml` appears in `gh run list`, with conclusion `success`. A second `calibration_result` event is now in the event surface.
- **Assertion:** `gh run list --workflow=gitnexus-grammar-skip-calibration.yml --limit 10 --json conclusion,event,createdAt` includes at least one run with `event == "schedule"` and `conclusion == "success"` dated within the two-week observation window; `mcp-events.jsonl` (or the run's log) confirms a second `calibration_result` event.
- **Source:** T5.3 L1/L2/L3.
- **Automation hook:** `gh run list --workflow=gitnexus-grammar-skip-calibration.yml --json event,conclusion,createdAt | jq '[.[] | select(.event=="schedule" and .conclusion=="success")] | length'` returns >= 1.
- **Severity:** BLOCKER for the criterion-itself if the cron does not fire OR fires non-success within 2 weeks of merge. If the cron simply has not yet fired because the observation window has not yet elapsed (e.g. PV-5 is being run on the same day as merge), surface as MAJOR-deferred-pending-observation rather than BLOCKER, with an explicit check-back date.

#### PV-5.C4 — Post-launch observation log open and populated against PRD §Success Criteria

- **Description:** `working/feature/pipeline-quickwins-hardening-r1/post-launch-observations.md` exists. Each of the eight PRD success-criteria items (i–viii in Plan T5.4 description) has at least one observed data point recorded within the post-launch observation window. No kill criteria have fired.
- **Assertion:** File exists; each of the eight items has a non-empty observation block; no observation references a kill-criteria trigger.
- **Source:** T5.4 L1/L2/L3.
- **Automation hook:** manual inspection by the maintainer (the user) using a checklist derived from PRD §Success Criteria; trivially scriptable as a section-presence check.
- **Severity:** MAJOR for the log existing with at least one data point per item (the observation is ongoing — fully complete coverage may extend beyond the PV-5 boundary). BLOCKER if a kill-criteria trigger has fired and is not yet acted on per the PRD's kill-criteria procedure.
- **Note on compound severity:** PV-5.C4's compound severity ("MAJOR for log existence; BLOCKER if kill-criterion fires") reflects Plan T5.4's open-ended observation framing — T5.4 is an ongoing post-merge observation task whose full-coverage window extends beyond the PV-5 phase boundary (cross-reference Plan §Phase 5 Goal preamble: "T5.2 is the terminal write-action of the run; T5.3 and T5.4 are post-action observation tasks"). The compound severity is intentional rather than singular: MAJOR is acceptable at the PV-5 boundary because completeness can extend beyond it; BLOCKER fires only on a kill-criterion trigger that demands immediate action regardless of observation window state. See Plan T5.4 `Description` field for the open-ended observation framing this severity rule operationalizes.

### Acceptance tests scheduled for this phase

AT-NNN cross-references per Acceptance Tests v1.0.1 Coverage Matrix. PRD-original `AC-FR-4c-a` is an alias for `AC-CICD-4c-1`; the AT IDs below are the canonical mapping.

- **AC-CICD-4c-1** (weekly cron trigger — load-bearing for PV-5.C3) → AT-045.
- **AC-CICD-4c-5** (`workflow_dispatch` path — load-bearing for PV-5.C2) → AT-049.
- **AC-FR-4c-a** (cron-triggered invocation surfaces script exit code — load-bearing for PV-5.C3) → aliased to AC-CICD-4c-1 → AT-045 (shared with AC-CICD-4c-1).
- **AC-X-4** (banner transitions from "NEVER RUN" to silent on first operator rebuild post-merge — load-bearing for PV-5.C2 transitive) → AT-072, AT-073, AT-074.
- **AC-NFR-5-a** (determinism — observed via T5.4 over the first N runs) → AT-007 + AT-013 + AT-024 (per-mechanism aggregator).
- **AC-NFR-7-a** (no new credential prompts — observed via T5.4) → AT-052 + AT-062 + AT-077.
- **PRD §Success Criteria** items i–viii — primary acceptance target for the whole feature (no AT-NNN; observed via T5.4's post-launch observation log per PV-5.C4).

### Operational checks

- The `gh workflow run` invocation in T5.2 occurs as soon as practical after the merge (target: within the hour) so that any operator rebuild after the merge sees the silent banner rather than "NEVER RUN".
- The observation log captures absolute dates (per the user's plain-English-feedback memory — no relative-date references in the log without a parenthetical absolute date).
- Kill criteria per PRD §Rollout Plan are monitored continuously throughout the observation window; any trigger surfaces immediately, not at PV-5.C4 boundary.

### Failure response

This phase has the only meaningful rollback path in the feature lifecycle. If a kill criterion fires:

1. **Per-mechanism revert** — Use the bundled PR's per-mechanism revert path. Each mechanism (FR-1, FR-2, FR-3, FR-4 family, FR-5) is independently revertable per NFR-11 / AC-X-1 / the Plan's two-way-reversibility commitment.
2. **Open follow-up Issue** — Record the kill-criterion trigger, the affected mechanism, the revert path applied, and the diagnostic captured.
3. **Re-attempt only after root-cause** — Do not re-merge the reverted mechanism without an updated Plan that addresses the root cause.

For PV-5.C2 failure (the workflow run failed): inspect the run log; if it's a calibration script bug rather than a workflow-wiring bug, fix the script and re-invoke. If it's a workflow-wiring bug, the FR-4c workflow itself is the offending mechanism — apply the per-mechanism revert.

For PV-5.C3 failure (cron does not fire within window): inspect the cron expression for off-by-one issues; verify `permissions:` block has not been modified by a subsequent PR; verify the workflow is not paused. If the cron fires but fails (`conclusion: failure`), inspect the failing signal-N on stdout from the FR-4b script — this is the steady-state drift-detection mechanism working as designed; open a follow-up Issue for the upstream gitnexus pin update.

### Validator metadata

- **When run:** PV-5.C1 + PV-5.C2 immediately after the merge + workflow run (within the same operational session). PV-5.C3 within 2 weeks of merge (observation-window check). PV-5.C4 continuously throughout the observation window with a formal check-back at 2 weeks and at 4 weeks post-merge.
- **Expected duration:** PV-5.C1+C2: under 15 minutes. PV-5.C3: instantaneous (read `gh run list`). PV-5.C4: ongoing observation.
- **Prerequisites:** PV-4 passed.

---

## Cross-validator coordination

### Validator dependency graph

```
PV-0 (Setup) ──► PV-1 (Claude Code) ──► PV-2 (Codespaces) ──► PV-3 (CI/CD) ──► PV-4 (Bundle finalization) ──► PV-5 (Rollout)
```

Each phase validator depends on the prior phase validator having passed. The dependencies are strict (no skipping forward) because the Plan's cross-phase dependencies form a strict chain: Phase 1's ADRs are inputs to Phase 2's OP-7 schema extension and FR-4b script; Phase 2's FR-4b script is an input to Phase 3's FR-4c workflow; Phase 3's CI workflows are inputs to Phase 4's PR-open smoke; Phase 4's merged bundle is the input to Phase 5's post-merge workflow run.

The one optional skip-edge is PV-0 → PV-2 if Phase 1 has been performed by a different agent and verified independently — but in this Plan's single-implementor flow, the strict chain applies.

### Critical-path validators

The validators whose failure most delays the feature:

1. **PV-1.C6** (OP-11 against live `.mcp.json` returns exit 0). Failure means either the OP-11 algorithm misclassifies a live entry (algorithm bug) or the ADR-0041 annotations are missing or wrongly placed. Either way, blocks Phase 2 advance because the AC-NFR-10 day-one no-false-positives guarantee is load-bearing.

2. **PV-2.C4** (FR-4b script emits one schema-valid `calibration_result` event). Failure blocks Phase 3 advance because the FR-4c workflow has no script to invoke. Also blocks Phase 5 because no `calibration_result` event = "NEVER RUN" banner persistent.

3. **PV-3.C4** (pre-merge `workflow_dispatch` validation). Failure blocks Phase 4 advance because cicd-design v0.3.0 §D-0010 makes this the gate for opening the PR.

4. **PV-4.C7** (single bundled PR open with both CI workflows green). Failure blocks Phase 5 entirely; no merge possible.

5. **PV-5.C2** (post-merge workflow run succeeded; first `calibration_result` event landed). Failure means the feature ships but the Q-CS-1b banner emits "NEVER RUN" to every operator's first rebuild — a poor first-operator experience that the Plan explicitly designed against.

### Parallelizable validator checks (within-phase)

Within each phase validator, the criteria can run in parallel where indicated:

- **PV-1:** PV-1.C1 (ADR-0057), PV-1.C2 (ADR-0058), PV-1.C3 (FR-1 script), PV-1.C4 (FR-3 script), PV-1.C5 (ADR-0041 annotations) are independent — run in parallel. PV-1.C6 depends on PV-1.C4 + PV-1.C5. PV-1.C7 depends on PV-1.C3 + PV-1.C4. PV-1.C8 depends on PV-1.C7.
- **PV-2:** PV-2.C5 (cosmetic) and PV-2.C6 (KB doc updates) are independent of the rest — run in parallel. PV-2.C1 → PV-2.C4 is the critical chain; PV-2.C2 → PV-2.C3 can run after PV-2.C4 lands.
- **PV-3:** PV-3.C1 and PV-3.C2 are independent — run in parallel. PV-3.C3 depends on both. PV-3.C4 depends on PV-3.C3.
- **PV-4:** PV-4.C1 (register), PV-4.C2 (CLAUDE.md), PV-4.C5 (Q-CS-1b smoke), PV-4.C6 (checkpoint resume smoke) are independent — run in parallel. PV-4.C3 (per-mechanism isolation) and PV-4.C4 (end-to-end) must run sequentially (per Plan T4.4 depending on T4.3). PV-4.C7 depends on all the others.
- **PV-5:** strictly sequential.

### Shared validator infrastructure

The following infrastructure is shared across multiple validators:

| Resource | Used by | Notes |
|---|---|---|
| Fixture directory `working/feature/pipeline-quickwins-hardening-r1/fixtures/` | PV-1.C3, PV-1.C4, PV-1.C8, PV-2.C1, PV-4.C3, PV-4.C5, PV-4.C6 | Fixture-driven smokes share this directory; sub-directories per mechanism. |
| Smoke log directory `working/feature/pipeline-quickwins-hardening-r1/smoke/` | PV-4.C3, PV-4.C4, PV-4.C5 | Phase 4 smoke logs captured here for audit-trail. |
| Anchor working notes (`sha-pins.md`, `adr-0041-anchors.md`, `postcreate-anchor.md`, `tooling-check.md`) | PV-0.C2..C5, referenced by PV-1.C5, PV-2.C2, PV-3.C1, PV-3.C2 | Phase 0 outputs become Phase 1-3 inputs. |
| `.claude/runtime/mcp-events.jsonl` | PV-2.C4, PV-2 banner fixtures via PV-2.C3, PV-4.C5, PV-5.C2, PV-5.C3 | The event surface itself; gitignored per ADR-0037. |
| OP-7 schema validation (`audit_op7_events_schema.py`) | PV-2.C4, PV-5.C2 | Reused at every event emission. |
| `auditing-mcp/scripts/audit_op11_adr_parity.py` | PV-1.C4, PV-1.C6, PV-4.C3 (FR-3 sub-smoke) | The new OP-11 rule itself. |
| `verdict_findings_parity.py` | PV-1.C3, PV-1.C7, PV-4.C3 (FR-1 sub-smoke), PV-4.C4 | The new FR-1 validator. |
| `gh` CLI | PV-3.C4, PV-4.C7, PV-5.C1, PV-5.C2, PV-5.C3 | Required for Phase 3 onward; documented in PV-0.C5. |

### Validator runbook

When a human operator runs a phase validator during real execution, the procedure is:

1. **Confirm prerequisites.** The prior phase's validator must have passed (or this is PV-0). Confirm by reading the validator log from the prior phase.

2. **Run BLOCKER criteria first.** Run them in dependency order within the phase (use the parallelization map above for opportunities to run in parallel where independent). On any BLOCKER failure, halt; do not proceed to MAJOR or MINOR criteria.

3. **Run MAJOR criteria.** Record each as PASS / FAIL / DEFERRED. A FAIL on a MAJOR criterion does not block advancement on its own; document the operator's deferral decision with a reason and a check-back date.

4. **Run MINOR criteria.** Record each as PASS / FAIL / RECORDED. Failure of a MINOR criterion never blocks; the record exists for follow-up.

5. **Surface to user when:** any BLOCKER fails; multiple MAJORs accumulate (≥ 2 in a single validator); a MINOR has been deferred more than once.

6. **Write validator log.** A per-validator log at `working/feature/pipeline-quickwins-hardening-r1/validator-logs/PV-<phase>.md` captures: which criteria were run, their outcomes, automation-hook output, any deferrals, the operator's decision to advance (or not).

7. **Advance to next phase** only after either (a) all BLOCKER criteria PASS and no MAJOR has been left unaddressed without operator deferral, or (b) for PV-5, the observation window has elapsed and the kill-criteria have not fired.

### Validator-to-task back-pointers (quick reference)

| Validator | Maps to Plan tasks | Maps to Phase Exit Criteria |
|---|---|---|
| PV-0 | T0.1, T0.2, T0.3, T0.4, T0.5 | Plan §Phase 0 Exit Criteria |
| PV-1 | T1.1..T1.9 | Plan §Phase 1 Exit Criteria |
| PV-2 | T2.1..T2.8 | Plan §Phase 2 Exit Criteria |
| PV-3 | T3.1, T3.2, T3.3 | Plan §Phase 3 Exit Criteria |
| PV-4 | T4.1..T4.7 | Plan §Phase 4 Exit Criteria |
| PV-5 | T5.1, T5.2, T5.3, T5.4 | Plan §Phase 5 Exit Criteria |

---

## Open items

None at authoring time. The validators operationalize the Plan's existing Phase Exit Criteria and per-task L3 verification; no new validation scope is introduced.

Items that may need attention from the cross-artifact auditor (`review-cross-artifact-auditor`) when this document is reviewed alongside the acceptance-tests document:

- ~~Once `test-acceptance-author` finalizes its document, the AC-IDs cited throughout these validators should map 1-to-1 to `AT-NNN` test IDs. The mapping is currently implicit (AC-IDs cite PRD/Blueprint directly).~~ **RESOLVED in v1.0.1** (per Cross-Artifact Audit cycle 1 / I-CA-006). The Acceptance Tests document is now v1.0.1 (AT-001 through AT-079); each phase's "Acceptance tests scheduled" subsection now carries inline AT-NNN cross-references per the Acceptance Tests Coverage Matrix.
- PV-3.C3's "MAJOR fallback when actionlint binary is absent" depends on whether the `mcp__actionlint-mcp__lint_workflow` MCP server's earlier schema-validation issue has been resolved by execution time. If still unresolved, the operator should treat PV-3.C3 as BLOCKER even on MCP-fallback degradation (no advance until a working actionlint path is restored).
- PV-5.C3 ("first Monday cron tick within 2 weeks of merge") has a soft real-time dependency the validator framework does not natively express. The runbook step 7 carve-out (option b — observation window elapsed) is the authoritative handling.

## Update History

| Version | Date | Author | Summary |
|---|---|---|---|
| 1.0.0 | 2026-05-26 | test-phase-validator-author | Initial authoring. Six validators (PV-0..PV-5), one per Plan phase. |
| 1.0.1 | 2026-05-26 | test-phase-validator-author | Cross-Artifact Audit cycle 1 reconciliation (per reconciliation-log-r3.md). Three surgical edits: (1) I-CA-003 — bumped §Source Blueprint pointer from v2.1 to v2.2.0 (also updated the two other Blueprint v2.1 references in §Operational checks and PV-4.C7 Assertion); (2) I-CA-006 — added AT-NNN cross-references in each phase's "Acceptance tests scheduled" subsection mapped to the Acceptance Tests v1.0.1 Coverage Matrix; marked the corresponding §Open items entry resolved; (3) I-CA-008 — added a one-line cross-reference note to PV-5.C4 pointing at Plan T5.4's open-ended observation framing. The 6 validator structures, 30 pass criteria, dependency chain, shared infrastructure inventory, 7-step operator runbook, and failure responses are unchanged. |
