---
id: Plan-pipeline-quickwins-hardening-r1
version: 1.0.2
status: draft
feature_slug: pipeline-quickwins-hardening-r1
derived_from: working/feature/pipeline-quickwins-hardening-r1/blueprint-v2.md
phases: 6
total_tasks: 36
generated: 2026-05-26T00:00:00Z
generated_by: plan-author
revision_history:
  - version: 1.0.2
    date: 2026-05-26
    author: plan-author
    cycle: cross-artifact reconciliation cycle 1
    source: working/feature/pipeline-quickwins-hardening-r1/reconciliation-log-r3.md
    edits:
      - "I-CA-003 (Plan side) — bumped Blueprint pointer references from v2.1 to v2.2.0 across §Source (line 62), §Purpose (line 54), and all in-body citations (Phase descriptions, task descriptions). Plan is now aligned to the current Blueprint version. Historical revision_history v1.0.0 source field preserved as authored against v2.1 (honest historical record); narrative pointers updated to v2.2.0."
      - "I-CA-004 — amended §Update History v1.0.0 row to inline-flag the 47→36 task count correction (originally counted as 47; corrected in v1.0.1 per I-DR-001 — counter error, no tasks added or removed). Prevents Update History readers from seeing a contradiction between the v1.0.0 and v1.0.1 rows."
      - "I-CA-005 — marked Open Item OI-1 (Concrete NFR-1 / NFR-2 latency thresholds) as RESOLVED, citing Blueprint v2.2 §NFR-1 / §NFR-2 inline thresholds (250 ms p95 for NFR-1, 100 ms p95 for NFR-2) and Acceptance Tests AT-075 / AT-076 which assert them. The cc-design v0.2.0 extraction was completed as part of the v2.1→v2.2 lift cycle."
  - version: 1.0.1
    date: 2026-05-26
    author: plan-author
    cycle: reconciliation cycle 1
    source: working/feature/pipeline-quickwins-hardening-r1/reconciliation-log-r2.md
    edits:
      - "I-DR-001 — corrected task count 47 → 36 (frontmatter total_tasks and Estimation Methodology). The 47 was a counter error during authoring (actual rendered count: Phase 0: 5 + Phase 1: 9 + Phase 2: 8 + Phase 3: 3 + Phase 4: 7 + Phase 5: 4 = 36). No tasks added or removed."
      - "I-DR-005 — clarified T2.6 server-count disposition. Inspection of .devcontainer/postCreate.sh confirms line 5 still reads '5 OSS-local MCP servers' (stale; correct value is 4 per lines 9 and 193 which already reflect the post-2026-05-24 postmortem). The original '5→4 servers' wording stands; inspection finding now documented in the task body so the implementor does not re-investigate. The dispatch prompt's '6 servers' figure refers to total .mcp.json server count (4 OSS-local + 2 HTTP); postCreate.sh line 5's scope is narrower (OSS-local only), so 4 is the correct target."
      - "I-DR-003 — added Phase 5 Goal clarification distinguishing T5.2 (terminal write-action) from T5.3 and T5.4 (post-action observation tasks)."
  - version: 1.0.0
    date: 2026-05-26
    author: plan-author
    cycle: initial authoring
    source: working/feature/pipeline-quickwins-hardening-r1/blueprint-v2.md (v2.1; reconciled to v2.2.0 in v1.0.2 per I-CA-003)
    edits:
      - "Initial Plan derived from Blueprint v2.1 (post-Architecture-Audit cycle 2 pass). Plan-body pointers subsequently updated to Blueprint v2.2.0 in v1.0.2 per cross-artifact audit cycle 1 (I-CA-003)."
---

# Plan: Pipeline Quick-Wins Hardening (Round 1)

## Contents

Section completion checklist — each box must be checked (including `N/A — out of scope` rows) before this document leaves draft. The reviewer's Gate 0 check uses this list as the structural-presence anchor.

- [x] Purpose
- [x] Source
- [x] Phase 0 — Setup
- [x] Phase 1 — Claude Code foundation (ADRs, FR-1, FR-3, FR-2 orchestrator)
- [x] Phase 2 — Codespaces (OP-7 schema extension, FR-4a static-shape, FR-4b calibration script, Q-CS-1b banner, KB doc updates)
- [x] Phase 3 — CI/CD (FR-5 connectivity smoke, FR-4c calibration workflow)
- [x] Phase 4 — Bundle finalization (FR-7 register, CLAUDE.md counter, Q-CS-3 cosmetic fix, pre-merge validation)
- [x] Phase 5 — Rollout (post-merge banner-retirement workflow run, observability)
- [x] Cross-Phase Dependencies
- [x] L1/L2/L3 Verification Discipline
- [x] Acceptance Test Cross-Reference
- [x] Estimation Methodology
- [x] Resourcing Posture
- [x] Open Items (Pending Cross-Artifact Audit)
- [x] Update History

## Purpose

This Plan decomposes the approved Blueprint v2.2.0 into executable phases and tasks. It is the executable map of how this feature ships, not a re-statement of the Blueprint's design.

The Blueprint sequences delivery via a single bundled PR per D-0008 / Q-CC-4. This Plan keeps that PR shape, treats each Phase below as a coherent commit (or commit group) within the single PR, and orders the Phases by Blueprint-layer dependency: Claude Code foundation first (the parity validator, the new audit rule, the orchestrator self-check, both ADRs), then Codespaces (which depends on ADR-0058 + the OP-7 schema being extended), then CI/CD (which depends on the FR-4b script existing in the devcontainer image), then bundle finalization, then post-merge rollout.

Every Plan task carries L1/L2/L3 verification. Every PRD/Blueprint Acceptance Criterion maps to at least one task. The bundle is two-way reversible per NFR-11 — each of the five mechanisms (and within the FR-4 family, each sub-mechanism) is independently revertable.

## Source

- **Blueprint**: `working/feature/pipeline-quickwins-hardening-r1/blueprint-v2.md` (v2.2.0, status: approved — Gate 4 + Architecture Audit cycle 2 pass; v2.1 → v2.2.0 lifted the NFR-1 / NFR-2 concrete thresholds and the AC-NFR-14 / AC-NFR-15 cross-cutting ACs inline, per I-CA-005 close).
- **PRD**: `working/feature/pipeline-quickwins-hardening-r1/prd-v1.md` (v0.3.0, status: approved).
- **ADRs in scope**: ADR-0005, ADR-0017, ADR-0029, ADR-0033, ADR-0036, ADR-0037 (v1.0.2), ADR-0039, ADR-0040, ADR-0041 (rows 70 + 71 carry `[DEPRECATED INVOCATION FORM]` annotations), ADR-0042, ADR-0043, ADR-0044, ADR-0056, ADR-0057 (v1.0.1), ADR-0058 (NEW — authored Blueprint v2).
- **Codebase analysis**: `working/feature/pipeline-quickwins-hardening-r1/codebase-analysis.json`.
- **Phase taxonomy used**: Phase 0 (setup) → Phase 1 (Claude Code foundation) → Phase 2 (Codespaces) → Phase 3 (CI/CD) → Phase 4 (bundle finalization) → Phase 5 (rollout). Phases 1-4 land in a single bundled PR per D-0008; Phase 5 is the one explicit post-merge action.

## Phase 0 — Setup

### Goal

Set up the working branch, confirm tool availability, and resolve the small set of pre-implementation discovery items (SHA values for third-party Actions; current ADR-0041 row anchors) so that subsequent tasks have stable inputs.

### Tasks

#### T0.1: Create feature branch and confirm clean working tree

- **Layer:** Claude Code / Project Filesystem (workflow housekeeping).
- **Description:** Create branch `feature/pipeline-quickwins-hardening-r1` from `main`. Confirm `git status` clean and that `.claude/`, `.devcontainer/`, `.github/workflows/`, `adrs/`, `Issues/`, and `working/feature/pipeline-quickwins-hardening-r1/` are all present.
- **Dependencies:** none.
- **Estimate:** XS.
- **Satisfies AC:** N/A — setup.
- **L1 verification:** `git branch --show-current` returns `feature/pipeline-quickwins-hardening-r1`; `git status` reports clean.
- **L2 verification:** `ls .claude/skills/auditing-mcp/` returns the existing OP-1..OP-10 script set; `ls .devcontainer/scripts/` is reachable; `ls .github/workflows/` is reachable.
- **L3 verification:** branch pushes successfully to remote.

#### T0.2: Resolve SHA pins for `actions/checkout` and `devcontainers/ci`

- **Layer:** CI/CD.
- **Description:** Resolve the current major-version SHA for `actions/checkout` (first-party; major-version tag acceptable but SHA preferred) and for `devcontainers/ci` (third-party; SHA pin REQUIRED per KB-github-actions-platform non-negotiable #1 and per Blueprint Implementation Plan §SHA-pinning). Both workflows (FR-5 and FR-4c) MUST use the same resolved SHA for each action — one resolution effort per action, two reuses. Record the resolved SHAs in a working note under `working/feature/pipeline-quickwins-hardening-r1/sha-pins.md`.
- **Dependencies:** T0.1.
- **Estimate:** XS.
- **Satisfies AC:** AC-CICD-5-a (transitively — FR-5 workflow file authoring requires the SHAs); AC-CICD-4c-1, AC-CICD-4c-6 (transitively — FR-4c workflow file authoring requires the SHAs).
- **L1 verification:** `working/feature/pipeline-quickwins-hardening-r1/sha-pins.md` exists and lists two SHA values with their source URLs (GitHub release pages for `actions/checkout` and `devcontainers/ci`).
- **L2 verification:** Each SHA matches the format `^[a-f0-9]{40}$` (full Git SHA).
- **L3 verification:** Both Phase 3 workflow files (T3.1, T3.4) cite the same SHA for `actions/checkout` and the same SHA for `devcontainers/ci`.

#### T0.3: Confirm current ADR-0041 row anchors (rows 70 and 71)

- **Layer:** Claude Code.
- **Description:** Read `adrs/ADR-0041-install-mechanism-hybrid.md` lines 68-71 (invocation taxonomy table) and confirm that row 70 (Serena) and row 71 (mcp-openapi-schema) are present and addressable. The Blueprint v2.2.0 specifies both rows will receive `[DEPRECATED INVOCATION FORM]` annotations in Phase 1. Capture the current row contents verbatim in the working note `working/feature/pipeline-quickwins-hardening-r1/adr-0041-anchors.md` for use by T1.5.
- **Dependencies:** T0.1.
- **Estimate:** XS.
- **Satisfies AC:** N/A — setup (input gathering for T1.5).
- **L1 verification:** `working/feature/pipeline-quickwins-hardening-r1/adr-0041-anchors.md` exists.
- **L2 verification:** The note records row 70's verbatim Form column text (currently documents `uvx --from "git+https://github.com/oraios/serena@${SERENA_REF}" serena start-mcp-server`) and row 71's verbatim Form column text (currently documents the `mcp-openapi-schema` invocation, server removed from `.mcp.json` 2026-05-24).
- **L3 verification:** T1.5 uses the captured anchors to apply the `[DEPRECATED INVOCATION FORM]` annotations without re-reading the ADR.

#### T0.4: Confirm `postCreate.sh` line 197-198 anchor still resolves

- **Layer:** Codespaces / Devcontainer.
- **Description:** Read `.devcontainer/postCreate.sh` lines 195-201 and confirm the FR-4a insertion site is still between `install_terraform_mcp || ...` (line 197) and `install_gitnexus || ...` (line 198), with the existing `gitnexus_post_install_warm` block at line 201 unchanged. Per Blueprint §Existing Codebase Analysis fact C-NEW-01, the line numbers are anchors per the live file at 2026-05-26; if the file has drifted since the Blueprint was authored, the anchor must be re-discovered by string match. Capture the resolved anchor (line number AND adjacent string fragments) in `working/feature/pipeline-quickwins-hardening-r1/postcreate-anchor.md`.
- **Dependencies:** T0.1.
- **Estimate:** XS.
- **Satisfies AC:** N/A — setup (input gathering for T2.2, T2.3).
- **L1 verification:** `working/feature/pipeline-quickwins-hardening-r1/postcreate-anchor.md` exists and records: the line number where the FR-4a block will be inserted (between `install_terraform_mcp` and `install_gitnexus`); a 3-line context fragment above and below.
- **L2 verification:** The captured context fragments string-match against the current `.devcontainer/postCreate.sh` content.
- **L3 verification:** T2.2 uses the captured anchor to insert the FR-4a block at the correct location without re-reading the file.

#### T0.5: Confirm tool availability — `actionlint`, `jq`, `python3`, `bash`, `mktemp`, `gh`

- **Layer:** Claude Code / Project Filesystem.
- **Description:** Confirm the local environment has the tools the Plan's tasks invoke: `actionlint` (binary or via `mcp__actionlint-mcp__lint_workflow` if the MCP server is restored from the earlier schema validation issue), `jq` (Q-CS-1b banner + FR-4b signal assertions), `python3` (FR-1 validator + FR-3 OP-11 audit script), `bash` (FR-4b script + FR-4a inline block), `mktemp` (FR-4b scratch directories), `gh` CLI (Phase 5 post-merge workflow run). Note any missing tool in `working/feature/pipeline-quickwins-hardening-r1/tooling-check.md`.
- **Dependencies:** T0.1.
- **Estimate:** XS.
- **Satisfies AC:** N/A — setup.
- **L1 verification:** `working/feature/pipeline-quickwins-hardening-r1/tooling-check.md` exists.
- **L2 verification:** Each of the six tools either reports a version (`<tool> --version`) or is annotated "fallback available" with the fallback path noted. (`actionlint` may rely on the MCP server fallback; the others have no fallback.)
- **L3 verification:** All Phase 1-4 tasks that invoke these tools succeed at their L2 step.

### Phase 0 Exit Criteria

- All five Phase 0 tasks' L3 verifications pass.
- The feature branch exists, is current with `main`, and is pushed.
- SHA pins for `actions/checkout` and `devcontainers/ci` are resolved and recorded.
- ADR-0041 row 70 and row 71 anchors are recorded.
- The `postCreate.sh` line 197-198 anchor is recorded (or the drifted anchor re-discovered).
- The required tooling is confirmed present (or fallback paths documented).

Phase Validator (per `KB-task-decomposition`): the Phase 0 validator tests that the working notes (T0.2, T0.3, T0.4, T0.5) all exist and are non-empty.

## Phase 1 — Claude Code foundation (ADRs, FR-1, FR-3, FR-2 orchestrator)

### Goal

Land the Claude-Code-layer foundation: both new ADRs at their canonical paths; the FR-1 verdict-vs-findings parity validator; the FR-3 OP-11 audit rule with the `[DEPRECATED INVOCATION FORM]` annotations on ADR-0041 rows 70 and 71; the FR-2 orchestrator dispatch self-check with the `scope_class` hoist and the `checkpoint.execution_mode` schema documentation per ADR-0057.

### Tasks

#### T1.1: Author ADR-0057 (`checkpoint.execution_mode` first-class field) at v1.0.1

- **Layer:** Claude Code.
- **Description:** Write `adrs/ADR-0057-checkpoint-execution-mode-first-class-field.md` at v1.0.1. The decision content is established in Blueprint v1 / v2 §ADR-0057; the v2.1 amendment reworded §Context from "introduce" to "promote-and-formalize" per Architecture Audit cycle 1 finding I-AA-004 (the `execution_mode` field is pre-existing in `recipe-feature-pipeline/SKILL.md:138` and 412 and present-but-nulled in this feature's working `checkpoint.json:106`). ADR file at `adrs/` per ADR-0036 + ADR-0056. Frontmatter: `version: 1.0.1`, `status: accepted`, `change_summary: "Prose-only amendment v1.0.0 → v1.0.1: §Context reworded 'introduce' → 'promote-and-formalize' per Architecture Audit cycle 1 finding I-AA-004. No decision-content change."`.
- **Dependencies:** T0.1.
- **Estimate:** S.
- **Satisfies AC:** AC-CC-2-a (the FR-2 self-check reads `checkpoint.execution_mode` per ADR-0057).
- **L1 verification:** `adrs/ADR-0057-checkpoint-execution-mode-first-class-field.md` exists; frontmatter parses; status `accepted`; version `1.0.1`.
- **L2 verification:** The ADR body documents (i) the closed enum for `execution_mode` (`specialist-dispatch`, `parent-driven-workaround`, any additional values per Blueprint v2 §ADR-0057 decision content), (ii) the writer (orchestrator dispatch step), (iii) the reader (FR-2 self-check), (iv) the absence-default rule (pre-feature checkpoints lacking the field map to `specialist-dispatch`).
- **L3 verification:** T1.7 (orchestrator dispatch self-check) reads the field as documented; T4.6 (resume pre-feature checkpoint smoke per AC-CC-2-g) passes.

#### T1.2: Author ADR-0058 (`calibration_result` event-type additive extension to ADR-0037)

- **Layer:** Claude Code.
- **Description:** Write `adrs/ADR-0058-calibration-result-event-type-additive-extension.md` at v1.0.0 (revised in draft per v2.1; final status `accepted` at Phase 4 close). The decision content is established in Blueprint v2 §Data Representation Decision and the Contract Definitions block. Frontmatter: `version: 1.0.0`, `status: accepted`, `supersedes: none`, `change_summary: "Additive extension of ADR-0037's event-type vocabulary admitting calibration_result as the fourth value."`. Body documents: cite-and-extend (not in-place) relationship to ADR-0037; canonical payload `{event: "calibration_result", timestamp, server, mechanism, version, duration_ms, outcome ∈ {pass, fail, drift_detected}, signals: <per-mechanism map>, note}`; the `mechanism:` field as namespace discriminator (`fr-4b-gitnexus-grammar-skip` for this feature); the closed-enum discipline preserved at four values; OP-7 (schema validation; `audit_op7_events_schema.py`) extended to admit the type; OP-6 (credential redaction) unaffected; existing consumers ignore unknown types per ADR-0037 forward-compatibility.
- **Dependencies:** T0.1.
- **Estimate:** S.
- **Satisfies AC:** AC-X-2 (event surface admits exactly four types); AC-CS-4b-1, AC-CS-4b-5 (FR-4b script emits one event conforming to this payload shape); AC-CS-4b-2 (event-as-primary-channel).
- **L1 verification:** `adrs/ADR-0058-calibration-result-event-type-additive-extension.md` exists; frontmatter parses; status `accepted`; version `1.0.0`.
- **L2 verification:** Body documents the four-value closed enum (`install_complete`, `readiness_probe`, `structured_failure`, `calibration_result`); explicitly cites ADR-0037 v1.0.2; declares the canonical payload shape; declares the `mechanism:` discriminator.
- **L3 verification:** T2.1 (OP-7 schema extension) admits the type as documented; T2.4 (FR-4b script) emits events conforming to the payload; T2.5 (Q-CS-1b banner) reads the type correctly.

#### T1.3: Implement `verdict_findings_parity.py` (FR-1 validator)

- **Layer:** Claude Code.
- **Description:** Author `.claude/skills/auditing-shared/scripts/verdict_findings_parity.py`. CLI contract per Blueprint v1 §Main Components — UNCHANGED in v2: inputs are a reviewer-output path and the agent name; behavior is to read the verdict+findings JSON, apply the structural check, and exit with the standard 0/1/2 code set (0 = pass-through, 1 = blocking finding present alongside approving verdict, 2 = internal error). Blocking-severity set per cc-design v0.2.0 (U-1 resolved) — exact tokens from `cc-design.md`. Diagnostic on exit 1 includes the four FR-6 fields (mechanism = "FR-1"; offending artifact = reviewer-output path; rule = the verdict+severity pair; remedial-action hint).
- **Dependencies:** T0.1, T0.5 (python3 confirmed).
- **Estimate:** M.
- **Satisfies AC:** AC-FR-1-a, AC-FR-1-b, AC-FR-1-c, AC-CC-1-a, AC-CC-1-b, AC-CC-1-c, AC-CC-1-d, AC-CC-1-e, AC-CC-1-f, AC-CC-1-g, AC-CC-1-h; AC-NFR-1-a, AC-NFR-5-a (partial), AC-NFR-6-a (partial), AC-NFR-9-a, AC-FR-6-a (FR-1 surface).
- **L1 verification:** `.claude/skills/auditing-shared/scripts/verdict_findings_parity.py` exists; `python3 -c "import ast; ast.parse(open('.claude/skills/auditing-shared/scripts/verdict_findings_parity.py').read())"` succeeds; `python3 verdict_findings_parity.py --help` exits 0.
- **L2 verification:** Fixture-driven unit-style tests under `working/feature/pipeline-quickwins-hardening-r1/fixtures/fr1/` — one fixture per AC-FR-1-a/b/c case (pass-through, blocking, no-finding) — return the expected exit codes and diagnostics.
- **L3 verification:** A real reviewer-output JSON from an existing pipeline run is consumed by the validator and produces the same verdict the prior pipeline accepted (NFR-9 / AC-NFR-9-a).

#### T1.4: Implement `audit_op11_adr_parity.py` (FR-3 OP-11 audit rule)

- **Layer:** Claude Code.
- **Description:** Author `.claude/skills/auditing-mcp/scripts/audit_op11_adr_parity.py`. CLI contract per Blueprint v1 §Main Components — UNCHANGED in v2. The script iterates every `.mcp.json` server entry, locates the corresponding non-deprecated row in ADR-0041, and applies the canonicalize+opaque-tokens comparison algorithm (per U-3 resolved by cc-design v0.2.0). Exit codes per the existing OP-rule contract: 0 = no findings, 1 = blocker present, 2 = internal error. Rows annotated `[DEPRECATED INVOCATION FORM]` (rows 70 and 71 after T1.5) are skipped — the algorithm treats them as out-of-scope for parity. Diagnostic on exit 1 includes the four FR-6 fields (mechanism = "FR-3 / OP-11"; offending artifact = server name + .mcp.json line; rule = the diff dimension (argv / env-var-indirection / sentinel-path); remedial-action hint).
- **Dependencies:** T0.1, T0.5 (python3 confirmed), T1.5 (the `[DEPRECATED]` annotations must exist for the rule to correctly skip them — but T1.5 can be authored before T1.4 lands its fixture suite; the L2 fixture tests below assume T1.5 has landed).
- **Estimate:** M.
- **Satisfies AC:** AC-FR-3-a, AC-FR-3-b, AC-FR-3-c, AC-CC-3-a, AC-CC-3-b through AC-CC-3-l (see blueprint-v1 §FR-3 ACs for the full set); AC-NFR-5-a (partial), AC-NFR-6-a (partial), AC-NFR-10-a, AC-FR-6-a (FR-3 surface).
- **L1 verification:** `.claude/skills/auditing-mcp/scripts/audit_op11_adr_parity.py` exists; parses; `--help` exits 0. The complementary `.claude/skills/auditing-mcp/references/adr-parity.md` reference doc also exists, documenting the canonicalization rules and the `[DEPRECATED]` convention.
- **L2 verification:** Fixture-driven tests under `working/feature/pipeline-quickwins-hardening-r1/fixtures/fr3/`: one fixture per AC-FR-3 case (matching entry, drifted argv, drifted env-var, missing prescription, deprecated row skip) return the expected exit codes.
- **L3 verification:** Running the rule against the live `.mcp.json` + ADR-0041 (with the row 70 + row 71 `[DEPRECATED]` annotations from T1.5 applied) produces exit 0 (no findings) — confirms NFR-10 backward compatibility and the day-one false-positive surface is closed.

#### T1.5: Annotate ADR-0041 rows 70 and 71 with `[DEPRECATED INVOCATION FORM]` markers

- **Layer:** Claude Code.
- **Description:** Edit `adrs/ADR-0041-install-mechanism-hybrid.md` to add inline `[DEPRECATED INVOCATION FORM]` annotations to row 70 (Serena) and row 71 (`mcp-openapi-schema`). Annotations are inline markers; decision-text is preserved verbatim per ADR-0005 append-only discipline. Row 71 annotation: `[DEPRECATED — removed 2026-05-24]` (server fully removed from `.mcp.json` on that date). Row 70 annotation: `[DEPRECATED INVOCATION FORM — actual installed via uv-tool; runtime invocation is `serena start-mcp-server` from PATH after `uv tool install`; see postCreate.sh:82 + .mcp.json:28-31]` per Blueprint §Background and Context. Use the row anchors captured in T0.3.
- **Dependencies:** T0.3.
- **Estimate:** XS.
- **Satisfies AC:** AC-CC-3-l (FR-3 deprecated-row skip behavior); AC-FR-3-c (the unmatched-side surface for `mcp-openapi-schema` is not raised because the row carries the deprecated marker).
- **L1 verification:** `adrs/ADR-0041-install-mechanism-hybrid.md` contains the literal string `[DEPRECATED INVOCATION FORM` on both row 70 and row 71. The ADR's frontmatter version is bumped if cc-design / Blueprint v2.2.0 requires a version increment; otherwise inline annotations require no version bump per ADR-0005 (annotation is not decision-text mutation).
- **L2 verification:** A diff against `main` shows changes only to lines 70 and 71 of the invocation-taxonomy table (and any frontmatter version line if applicable); no other lines changed.
- **L3 verification:** T1.4's L3 (running OP-11 against live `.mcp.json` + this annotated ADR-0041) returns exit 0.

#### T1.6: Modify `recipe-feature-pipeline/SKILL.md` — hoist `scope_class` for FR-2 self-check

- **Layer:** Claude Code.
- **Description:** Edit `.claude/skills/recipe-feature-pipeline/SKILL.md`. Today `scope_class` is read at line 350 (inside Stage 13 — Deliverable Packaging) per codebase-C-0028. The FR-2 dispatch self-check runs at orchestrator entry (after Stage 1 — Intent Clarification completes), so `scope_class` must be hoisted to the dispatch-entry section. Per cc-design v0.2.0 §FR-2 (U-2 resolved), the hoist lives inline in the orchestrator SKILL.md rather than in a separate gate script. The line 350 read site remains as the Stage 13 consumer.
- **Dependencies:** T0.1.
- **Estimate:** S.
- **Satisfies AC:** AC-FR-2-a (the self-check enumerates every stage's per-stage agent configuration after Stage 1); AC-CC-2-a (read `scope_class` and enumerate `checkpoint.execution_mode`).
- **L1 verification:** `recipe-feature-pipeline/SKILL.md` contains `scope_class` references at both the new dispatch-entry section and the existing line ~350 (Stage 13) site.
- **L2 verification:** `gitnexus_impact` on the modified SKILL.md returns no HIGH/CRITICAL findings beyond the documented hoist (per CLAUDE.md MCP discipline).
- **L3 verification:** Pipeline smoke (T4.6) runs end-to-end with the hoisted scope_class read site and produces the same Stage 13 outcome it produced pre-feature.

#### T1.7: Modify `recipe-feature-pipeline/SKILL.md` — add FR-2 dispatch self-check block

- **Layer:** Claude Code.
- **Description:** Add the FR-2 dispatch self-check to `recipe-feature-pipeline/SKILL.md` per cc-design v0.2.0 §FR-2 placement (inline at orchestrator entry, after the hoisted `scope_class` read from T1.6). The self-check enumerates every stage's `checkpoint.execution_mode` value per ADR-0057. If `scope_class == "FULL"` and any stage's `execution_mode == "parent-driven-workaround"`, the orchestrator refuses to enter the dispatch loop and surfaces a diagnostic naming the offending stage + the configuration. MINOR and PATCH scopes permit single-agent-fallback configurations (AC-FR-2-c). Diagnostic includes the four FR-6 fields.
- **Dependencies:** T1.1 (ADR-0057 schema must be documented), T1.6 (scope_class must be hoisted).
- **Estimate:** M.
- **Satisfies AC:** AC-FR-2-a, AC-FR-2-b, AC-FR-2-c, AC-CC-2-a, AC-CC-2-b, AC-CC-2-c, AC-CC-2-d, AC-CC-2-e, AC-CC-2-f, AC-CC-2-g; AC-NFR-2-a; AC-FR-6-a (FR-2 surface).
- **L1 verification:** `recipe-feature-pipeline/SKILL.md` contains the new self-check block with all four FR-6 diagnostic fields present in the on-refusal path.
- **L2 verification:** Fixture-driven smoke: a fixture `checkpoint.json` with `scope_class: FULL` and one stage `execution_mode: parent-driven-workaround` triggers the refusal; a counter-fixture with `scope_class: MINOR` and the same `execution_mode` passes (AC-FR-2-c).
- **L3 verification:** AC-CC-2-g resume-pre-feature-checkpoint smoke (running the orchestrator against a checkpoint authored before this feature shipped; absence-default for `execution_mode` maps to `specialist-dispatch` per ADR-0057) succeeds.

#### T1.8: Modify `recipe-feature-pipeline/SKILL.md` — wire FR-1 validator at all 9 reviewer-completion sites

- **Layer:** Claude Code.
- **Description:** Per cc-design v0.2.0 §FR-1 (Discovery scope sweep per codebase-C-0018), the FR-1 validator runs at 9 reviewer-completion invocation sites across 5 reviewer-shaped agents: `shared-document-reviewer` (5 sites per ADR-0017), `review-architecture-auditor` (1), `review-cross-artifact-auditor` (1), `execute-phase-quality-reviewer` (1), `execute-task-quality-handler` (1). Edit `recipe-feature-pipeline/SKILL.md` to add the `python3 verdict_findings_parity.py <output-path> <agent-name>` invocation immediately after each reviewer's output is written to disk, before the orchestrator advances to the next stage. On exit code 1, halt orchestrator advance and surface the validator's diagnostic.
- **Dependencies:** T1.3 (validator script must exist).
- **Estimate:** M.
- **Satisfies AC:** AC-CC-1-a (the orchestrator invokes the validator at every reviewer-completion site); AC-NFR-11-a (per-mechanism isolation — FR-1 alone exercisable).
- **L1 verification:** `recipe-feature-pipeline/SKILL.md` contains exactly 9 invocations of `verdict_findings_parity.py` (one per reviewer-completion site).
- **L2 verification:** Fixture-driven smoke at each invocation site: a fixture reviewer output with an approving verdict + blocking finding triggers the halt; the counter-fixture (no blocking finding) passes through.
- **L3 verification:** Running an end-to-end pipeline smoke with all 9 sites enabled produces the same advance behavior pre-vs-post-feature for known-good fixture inputs (NFR-9).

#### T1.9: Update `auditing-mcp/SKILL.md` routing table for OP-11

- **Layer:** Claude Code.
- **Description:** Edit `.claude/skills/auditing-mcp/SKILL.md` to add OP-11 to the OP-rule routing table per ADR-0042 (auditing-mcp family graduation contract). OP-11 entry references `audit_op11_adr_parity.py` and `references/adr-parity.md`. The CLAUDE.md `OP-1..OP-10` counter update is deferred to T4.2 (single-character update lands in Phase 4).
- **Dependencies:** T1.4.
- **Estimate:** XS.
- **Satisfies AC:** AC-FR-3-a (audit skill is the dispatch point for OP-11); AC-NFR-11-a (FR-3 alone exercisable via the audit skill).
- **L1 verification:** `auditing-mcp/SKILL.md` references OP-11 in the routing table.
- **L2 verification:** Invoking the audit skill family-coordinator (per ADR-0042 / Gate-6 per ADR-0043) dispatches to `audit_op11_adr_parity.py` and the script runs.
- **L3 verification:** Gate-6 hard-gate per ADR-0043 includes OP-11 in its rule set; T4.6 smoke runs OP-11 alongside OP-1..OP-10.

### Phase 1 Exit Criteria

- All nine Phase 1 tasks' L3 verifications pass.
- ADR-0057 (v1.0.1) and ADR-0058 (v1.0.0) exist at `adrs/` with `status: accepted` frontmatter.
- `verdict_findings_parity.py` exists, passes its fixture suite, and is wired at all 9 reviewer-completion invocation sites.
- `audit_op11_adr_parity.py` exists, passes its fixture suite, and produces exit 0 against the live `.mcp.json` + ADR-0041 (with the row 70 + row 71 `[DEPRECATED]` annotations applied).
- `recipe-feature-pipeline/SKILL.md` carries the hoisted `scope_class` read site, the FR-2 dispatch self-check block, and the 9 FR-1 invocations.
- ADR-0041 rows 70 and 71 carry the `[DEPRECATED INVOCATION FORM]` annotations.

## Phase 2 — Codespaces (OP-7 schema extension, FR-4a, FR-4b, Q-CS-1b banner, KB docs)

### Goal

Land the Codespaces layer: extend the OP-7 schema validator to admit `calibration_result` BEFORE the FR-4b script emits its first event (Blueprint §Implementation Plan task 12 sequencing constraint); insert the FR-4a static-shape check at top-level in `postCreate.sh`; author the FR-4b calibration script with the full AC-CS-4b-1..7 contract; add the Q-CS-1b staleness banner adjacent to FR-4a; update the KB documentation that documents the event-surface schema's four-type vocabulary.

### Tasks

#### T2.1: Extend `audit_op7_events_schema.py` to admit `calibration_result`

- **Layer:** Claude Code (script lives in `auditing-mcp`; logically Codespaces because it gates the FR-4b emission's correctness — sequenced here per Blueprint v2.2.0 §Implementation Plan task 12).
- **Description:** Edit `.claude/skills/auditing-mcp/scripts/audit_op7_events_schema.py`. Extend the `VALID_EVENT_TYPES` set to add `"calibration_result"` and extend the `REQUIRED_FIELDS` dict to admit `calibration_result`'s canonical fields per ADR-0058: `event`, `timestamp`, `server`, `mechanism`, `version`, `duration_ms`, `outcome`, `signals`, `note`. The existing three event types (`install_complete`, `readiness_probe`, `structured_failure`) are preserved verbatim per ADR-0037 v1.0.2. Per Blueprint §Implementation Plan task 12: this task MUST complete in the same PR as the FR-4b script (T2.4) and the new ADR-0058 record (T1.2) — otherwise every FR-4b emission triggers an OP-7 MAJOR finding. Single-PR D-0008 decision encloses this dependency.
- **Dependencies:** T1.2 (ADR-0058 must be authored so the payload shape is canonical).
- **Estimate:** S.
- **Satisfies AC:** AC-X-2 (the OP-7 schema admits exactly four event types post-extension); AC-CS-4b-5 (the script emits an event conforming to the schema-admitted shape).
- **L1 verification:** `python3 -c "import ast; ast.parse(open('.claude/skills/auditing-mcp/scripts/audit_op7_events_schema.py').read())"` succeeds; the file contains the literal string `"calibration_result"` in the `VALID_EVENT_TYPES` set definition.
- **L2 verification:** A fixture `mcp-events.jsonl` containing one well-formed `calibration_result` event passes OP-7 with exit 0; a fixture containing a `calibration_result` event missing one of the nine required fields produces exit 1 with a MAJOR finding naming the missing field.
- **L3 verification:** After T2.4 ships and the first real `calibration_result` event is written to `mcp-events.jsonl` (during T2.4's L3 step), OP-7 produces no findings against the event.

#### T2.2: Insert FR-4a static-shape check block in `postCreate.sh` at top-level

- **Layer:** Codespaces / Devcontainer.
- **Description:** Edit `.devcontainer/postCreate.sh`. Insert the FR-4a static-shape check as a discrete top-level block between current lines 197 (`install_terraform_mcp || ...`) and 198 (`install_gitnexus || ...`), using the anchor captured in T0.4. Block performs the four assertions per AC-CS-4a-1: A1 `$GITNEXUS_SKIP_OPTIONAL_GRAMMARS == "1"`; A2 `$GITNEXUS_TAG` matches `^v?[0-9]+\.[0-9]+\.[0-9]+(-[A-Za-z0-9.-]+)?$`; A3 `$GITNEXUS_TAG` matches the value in `.devcontainer/versions.env`; A4 `npm root -g` returns non-empty with writable parent. On fail: emit one `structured_failure` event via `log_mcp_event` whose `note:` encodes the four FR-6 elements (mechanism = "FR-4a"; offending artifact; failing signal token from the fixed set `signal-a1-env-var-unset-or-wrong` / `signal-a2-tag-pin-malformed` / `signal-a3-versions-env-mismatch` / `signal-a4-artifact-paths-unpredictable`; remedial hint); echo plain-text diagnostic to stderr; `set -euo pipefail` halts the script before `install_gitnexus` is invoked. On pass: silent green-light. No network access. No sentinel file. Top-level placement (not inside `install_gitnexus()`) ensures `set -euo pipefail` enforces fail-closed without function-internal `|| emit_degraded_banner` masking.
- **Dependencies:** T0.4 (anchor captured).
- **Estimate:** M.
- **Satisfies AC:** AC-FR-4a-a, AC-FR-4a-b, AC-FR-4a-c, AC-FR-4a-d, AC-CS-4a-1, AC-CS-4a-2, AC-CS-4a-3, AC-CS-4a-4, AC-CS-4a-5, AC-CS-4a-6, AC-CS-4a-7; AC-NFR-3-a; AC-NFR-6-a (partial — FR-4a fail-closed); AC-FR-6-a (FR-4a surface).
- **L1 verification:** `bash -n .devcontainer/postCreate.sh` (syntax check) succeeds; the FR-4a block is inserted between lines 197 and 198 (string-match against the T0.4 anchor); the block does not invoke `npm install`.
- **L2 verification:** Fixture rebuilds against four broken-static-shape environments (one per A1/A2/A3/A4 failing) each halt `postCreate.sh` non-zero with the correct signal-named diagnostic on stderr and one matching `structured_failure` event in `mcp-events.jsonl`. A control rebuild (all assertions hold) green-lights into `install_gitnexus`.
- **L3 verification:** AC-CS-4a-6 budget check: 10 consecutive rebuilds on the configured `hostRequirements.cpus: 4` machine measure the FR-4a block's p95 wall-clock under 100 ms (no network access).

#### T2.3: Insert Q-CS-1b staleness banner block in `postCreate.sh` adjacent to FR-4a

- **Layer:** Codespaces / Devcontainer.
- **Description:** Edit `.devcontainer/postCreate.sh`. Add the Q-CS-1b staleness banner block immediately after the FR-4a block from T2.2 and before `install_gitnexus`. Block per AC-X-4: `jq` the most recent `calibration_result` event for `mechanism: "fr-4b-gitnexus-grammar-skip"` from `.claude/runtime/mcp-events.jsonl`; compare timestamp to `now - 2 weeks`. If absent: emit `[postCreate] FR-4b calibration: NEVER RUN. Suggest: gh workflow run gitnexus-grammar-skip-calibration.yml` to stderr. If ≥ 2 weeks old: emit `[postCreate] FR-4b calibration: STALE (last run <timestamp>, >2w ago). Suggest: gh workflow run gitnexus-grammar-skip-calibration.yml` to stderr. If < 2 weeks old: silent. Banner is informational — does NOT cause fail-close (no `set -e` violation; banner uses `|| true` guard on the `jq` invocation). Banner does NOT emit an `mcp-events.jsonl` event (banners are existing logged-at-rebuild observability convention).
- **Dependencies:** T2.2 (FR-4a block in place; banner sits adjacent).
- **Estimate:** S.
- **Satisfies AC:** AC-X-4 (Q-CS-1b banner contract); AC-FR-6-a (banner carries three of four FR-6 fields per AC-X-4 — rule-violated field intentionally omitted because no rule is violated).
- **L1 verification:** `bash -n .devcontainer/postCreate.sh` succeeds; the banner block is inserted between the FR-4a block and `install_gitnexus`; the block uses `jq` with `|| true` guard.
- **L2 verification:** Three fixture rebuilds against pre-populated `mcp-events.jsonl` states: (i) no `calibration_result` event → "NEVER RUN" banner; (ii) `calibration_result` event timestamped 3 weeks ago → "STALE" banner with the timestamp; (iii) `calibration_result` event timestamped < 2 weeks ago → silent. All three rebuilds complete successfully (banner never fail-closes).
- **L3 verification:** Phase 5 post-merge workflow run (T5.1) writes the first `calibration_result` event; on the next operator's first rebuild, the banner is silent (event < 2 weeks old).

#### T2.4: Author `.devcontainer/scripts/calibrate-gitnexus-grammar-skip.sh` (FR-4b script)

- **Layer:** Codespaces / Devcontainer.
- **Description:** Author the FR-4b opt-in behavioral calibration script per AC-CS-4b-1..7 contract. Standalone bash script, no arguments. Steps per Blueprint §Data Flow: (i) read `GITNEXUS_TAG` from `.devcontainer/versions.env`; (ii) `scratch1=$(mktemp -d)`; `trap 'rm -rf "${scratch1}" "${scratch2:-}"' EXIT`; export `NPM_CONFIG_PREFIX="${scratch1}/npm-global"`; (iii) `GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1 npm install -g "gitnexus@${TAG}" 2> "${scratch1}/stderr.log"`; (iv) Signal 1: `grep -E '\[tree-sitter-(dart|proto)\] Skipping build \(GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1\)' "${scratch1}/stderr.log"` — at least one match for each of `dart` and `proto`; (v) Signal 3: stat the predicted `tree-sitter-{dart,proto}` artifact paths — artifacts MUST be absent; (vi) Optional negative-assertion (enabled by default per AC-CS-4b-1 step vi): `scratch2=$(mktemp -d)`; `GITNEXUS_SKIP_OPTIONAL_GRAMMARS=0 npm install -g "gitnexus@${TAG}"`; assert artifacts ARE built; (vii) compute outcome ∈ {pass, fail, drift_detected}; emit exactly one `calibration_result` event per ADR-0058 via `log_mcp_event`; (viii) cleanup via the `trap EXIT`; exit 0 on pass, non-zero on any signal failure. Script's stdout names the offending grammar (Dart or Proto) + the failing Signal-N on fail (per Blueprint §Implementation Plan task 6 Plan task contract — so the FR-4c workflow's `$GITHUB_STEP_SUMMARY` can surface it).
- **Dependencies:** T1.2 (ADR-0058 payload shape canonical), T2.1 (OP-7 schema extension lands first or simultaneously).
- **Estimate:** L.
- **Satisfies AC:** AC-FR-4b-a, AC-FR-4b-b, AC-FR-4b-c, AC-FR-4b-d, AC-CS-4b-1, AC-CS-4b-2, AC-CS-4b-3, AC-CS-4b-4, AC-CS-4b-5, AC-CS-4b-6, AC-CS-4b-7; AC-NFR-6-a (partial — FR-4b fail-closed on internal error); AC-NFR-7-a, AC-NFR-8-a (no credentials in diagnostics); AC-X-2 (event surface); AC-FR-6-a (FR-4b surface).
- **L1 verification:** `bash -n .devcontainer/scripts/calibrate-gitnexus-grammar-skip.sh` succeeds; the script exists at the exact path; the script is executable (mode 0755).
- **L2 verification:** Local invocation `bash .devcontainer/scripts/calibrate-gitnexus-grammar-skip.sh` against `gitnexus@1.6.5` (the current pin) exits 0; writes exactly one `calibration_result` event with `outcome: "pass"` to `mcp-events.jsonl`; scratch directories are cleaned. A drift-fixture (constructed pin where Signal 1 / Signal 3 fail) produces exit non-zero with the offending grammar + Signal-N on stdout and a `calibration_result` event with `outcome: "fail"` or `"drift_detected"`.
- **L3 verification:** OP-7 audit rule (extended in T2.1) admits the emitted event without findings. AC-CS-4b-7 informational budget: full script wall-clock under 60 seconds on `ubuntu-latest`-class hardware (informational; the load-bearing budget is NFR-4's per-workflow 5-minute ceiling enforced by FR-4c).

#### T2.5: Verify FR-4b script's event-emission integration with `mcp-events.jsonl`

- **Layer:** Codespaces / Devcontainer.
- **Description:** End-to-end verification task: invoke the FR-4b script (from T2.4) against the current `gitnexus@1.6.5` pin; confirm it writes exactly one `calibration_result` event to `.claude/runtime/mcp-events.jsonl`; confirm the event payload conforms to ADR-0058's canonical shape under OP-7 (from T2.1); confirm the Q-CS-1b banner (from T2.3), on the next rebuild after this run, reports silent (event < 2 weeks old). This task is the "second verification target" per Blueprint §Verification Strategy — Early Verification Point.
- **Dependencies:** T2.1, T2.2, T2.3, T2.4.
- **Estimate:** S.
- **Satisfies AC:** AC-CS-4b-1 (full contract honored); AC-X-4 (banner gracefully consumes the event); AC-X-2 (event surface admits the new type).
- **L1 verification:** Exactly one new line in `.claude/runtime/mcp-events.jsonl` after the invocation; line parses as JSON.
- **L2 verification:** The JSON line has all nine required fields per ADR-0058 (`event`, `timestamp`, `server`, `mechanism`, `version`, `duration_ms`, `outcome`, `signals`, `note`); `event == "calibration_result"`; `mechanism == "fr-4b-gitnexus-grammar-skip"`; `version` matches the pinned `GITNEXUS_TAG`.
- **L3 verification:** Running `python3 .claude/skills/auditing-mcp/scripts/audit_op7_events_schema.py .claude/runtime/mcp-events.jsonl` exits 0 (no schema findings). A fresh devcontainer rebuild triggers the Q-CS-1b banner check and the banner is silent (event timestamp < 2 weeks old).

#### T2.6: Cosmetic "5→4 servers" fix in `postCreate.sh:5`

- **Layer:** Codespaces / Devcontainer.
- **Description:** Edit `.devcontainer/postCreate.sh` line 5 to update the head-comment OSS-local-server count from "5" to "4". This brings line 5 into alignment with lines 9 and 193 of the same file, which already reflect the post-2026-05-24 postmortem state (4 OSS-local servers installed: serena, actionlint-mcp, terraform-mcp, gitnexus; mcp-openapi-schema removed 2026-05-24). Single-word edit per Blueprint §Q-CS-3 disposition; cosmetic only.

  **Inspection finding (recorded 2026-05-26 during reconciliation cycle 1 per I-DR-005):** Direct read of `.devcontainer/postCreate.sh` confirms the live state at the time of this Plan revision:
  - Line 5: `# pattern for idempotency. Installs the 5 OSS-local MCP servers, emits one` — STALE (says "5"; should say "4").
  - Line 9: `# Servers installed here (4 — post-2026-05-24 postmortem; was 5):` — already correct.
  - Line 193: `echo "[postCreate] installing 4 OSS-local MCP servers..."` — already correct.
  - The 4 servers enumerated at lines 9-14: serena, actionlint-mcp, terraform-mcp, gitnexus.
  - Lines 7 and 19 separately reference the 2 HTTP servers (context7, exa) which are auth-probed, not installed.

  The "6 servers" figure in CLAUDE.md and `.mcp.json` counts all registered MCP servers (4 OSS-local + 2 HTTP). Line 5's scope is narrower — explicitly "OSS-local MCP servers" — so the correct target value is 4, not 6. The implementor changes a single digit on line 5: `5` → `4`. No other lines change.
- **Dependencies:** T0.1.
- **Estimate:** XS.
- **Satisfies AC:** N/A — setup (cosmetic cleanup; bundled per Q-CS-3 disposition).
- **L1 verification:** Line 5 of `.devcontainer/postCreate.sh` reads `# pattern for idempotency. Installs the 4 OSS-local MCP servers, emits one` (matching the count on lines 9 and 193).
- **L2 verification:** No other lines in `postCreate.sh` change from this edit (verified by `git diff --stat .devcontainer/postCreate.sh` showing only line 5 modified).
- **L3 verification:** N/A — cosmetic.

#### T2.7: Update `KB-mcp-design/references/principles.md` for four-type vocabulary

- **Layer:** Claude Code (KB doc edit on the Codespaces-event-surface schema home).
- **Description:** Per Blueprint v2.2.0 §Implementation Plan task 11 — Plan-task KB doc updates for ADR-0058. Edit `.claude/skills/KB-mcp-design/references/principles.md` to document the four-type vocabulary: `install_complete`, `readiness_probe`, `structured_failure`, `calibration_result`. Add the fourth-type entry alongside the three existing entries; cite ADR-0058 and ADR-0037 v1.0.2. Preserve all existing prose verbatim. Mechanical edit.
- **Dependencies:** T1.2 (ADR-0058 must exist to cite).
- **Estimate:** XS.
- **Satisfies AC:** AC-X-2 (the schema home documents the four-type vocabulary as Blueprint v2.2.0 §AC-X-2 requires).
- **L1 verification:** `KB-mcp-design/references/principles.md` contains the literal string `calibration_result` and the literal string `ADR-0058`.
- **L2 verification:** Diff shows additions only (no removals from the three pre-existing type entries).
- **L3 verification:** A future reader of the event-surface schema finds the fourth type documented alongside the three pre-existing types.

#### T2.8: Update `KB-mcp-platform/references/mcp-events-jsonl.md` with `calibration_result` example

- **Layer:** Claude Code (KB doc edit on the Codespaces-event-surface usage docs).
- **Description:** Per Blueprint v2.2.0 §Implementation Plan task 11. Edit `.claude/skills/KB-mcp-platform/references/mcp-events-jsonl.md` to add a `calibration_result` example record and document the `mechanism:` field as the namespace discriminator. Cite ADR-0058. Preserve all existing prose verbatim. Mechanical edit.
- **Dependencies:** T1.2 (ADR-0058 must exist to cite), T2.4 (the FR-4b script's payload is the example source).
- **Estimate:** XS.
- **Satisfies AC:** AC-X-2 (the usage docs document the fourth event type with example record).
- **L1 verification:** `KB-mcp-platform/references/mcp-events-jsonl.md` contains an example `calibration_result` record in JSON Lines format and references the `mechanism:` discriminator.
- **L2 verification:** The example record parses as JSON and conforms to ADR-0058's payload shape.
- **L3 verification:** Future readers see the fourth-type usage example alongside the three pre-existing types' examples.

### Phase 2 Exit Criteria

- All eight Phase 2 tasks' L3 verifications pass.
- `audit_op7_events_schema.py` admits `calibration_result` as the fourth valid event type.
- `postCreate.sh` carries the FR-4a top-level static-shape block, the Q-CS-1b staleness banner adjacent to it, and the cosmetic 5→4 fix.
- `.devcontainer/scripts/calibrate-gitnexus-grammar-skip.sh` exists, is executable, and passes its first invocation against the current `gitnexus@1.6.5` pin.
- The FR-4b script's emission integration is confirmed end-to-end (write → OP-7 admit → Q-CS-1b banner silent on next rebuild).
- The KB documentation for the four-type event-surface vocabulary is updated in both schema home and usage docs.

## Phase 3 — CI/CD (FR-5 connectivity smoke, FR-4c calibration workflow)

### Goal

Author both new GitHub Actions workflows: FR-5 (`mcp-connectivity-smoke.yml`) and FR-4c (`gitnexus-grammar-skip-calibration.yml`). Both use the SHA pins resolved in T0.2. Both pass `actionlint` before being committed (per Blueprint v2.2.0 §Implementation Plan Cross-Layer Sequencing Note — "Two workflows land atomically per actionlint discipline"). FR-5 + FR-4c pre-merge validation per cicd-design v0.3.0 §D-0010 (three `workflow_dispatch` runs each against the draft branch) gates the merge.

### Tasks

#### T3.1: Author `.github/workflows/mcp-connectivity-smoke.yml` (FR-5)

- **Layer:** CI/CD.
- **Description:** Author the FR-5 workflow per Blueprint v1 §Main Components and the reconciled AC-CICD-5-a..g. Triggers: `pull_request.paths: ['.mcp.json', '.devcontainer/**', 'adrs/ADR-0041-*.md', '.claude/skills/auditing-mcp/**']` + `workflow_dispatch`. Runner: `ubuntu-latest`. `timeout-minutes: 8`. `permissions: contents: read` only. Steps: `actions/checkout@<SHA>` (T0.2 SHA) → `devcontainers/ci@<SHA>` (T0.2 SHA) builds the project's devcontainer image → inside the image, run `claude --bare -p "noop" --output-format stream-json | jq <filter>` to extract the `system/init` event's `mcp_servers[].status` per Anthropic Agent SDK contracts. Empty bad-set (no server with `status != "connected"`) → PASS; non-empty → FAIL with FR-6 diagnostic (mechanism = "FR-5 MCP connectivity smoke"; offending artifact = server names; rule = the non-`connected` status value; remedial hint) to `$GITHUB_STEP_SUMMARY`.
- **Dependencies:** T0.2 (SHAs).
- **Estimate:** M.
- **Satisfies AC:** AC-FR-5-a, AC-FR-5-b, AC-FR-5-c, AC-CICD-5-a, AC-CICD-5-b, AC-CICD-5-c, AC-CICD-5-d, AC-CICD-5-e, AC-CICD-5-f, AC-CICD-5-g; AC-NFR-4-a; AC-NFR-7-a, AC-NFR-8-a (no credentials surface); AC-FR-6-a (FR-5 surface).
- **L1 verification:** `.github/workflows/mcp-connectivity-smoke.yml` exists; YAML parses; `actionlint .github/workflows/mcp-connectivity-smoke.yml` (or `mcp__actionlint-mcp__lint_workflow`) exits 0; the file string-matches both SHAs from T0.2.
- **L2 verification:** Co-validation with T3.4 — both workflow files lint clean together (actionlint discipline requires both to pass before either is committed).
- **L3 verification:** Pre-merge `workflow_dispatch` run against the draft branch — per cicd-design v0.3.0 §D-0010, three runs measure wall-clock; p95 under 4 minutes; all three exit green; the `system/init`-event parsing path is confirmed (Q-CICD-8 pre-merge validation).

#### T3.2: Author `.github/workflows/gitnexus-grammar-skip-calibration.yml` (FR-4c)

- **Layer:** CI/CD.
- **Description:** Author the FR-4c workflow per Blueprint v2 §Main Components and AC-CICD-4c-1..11. Triggers: `schedule: '0 7 * * 1'` (Monday 07:00 UTC) + `pull_request.paths: ['.devcontainer/versions.env', '.devcontainer/scripts/calibrate-gitnexus-grammar-skip.sh']` + `workflow_dispatch`. Runner: `ubuntu-latest`. `timeout-minutes: 5`. `permissions: contents: read` only. `concurrency: { group: gitnexus-calibration, cancel-in-progress: false }`. Steps: `actions/checkout@<SHA>` (T0.2 SHA, same as FR-5) → `devcontainers/ci@<SHA>` (T0.2 SHA, same as FR-5) builds the project's devcontainer image with `runCmd: bash .devcontainer/scripts/calibrate-gitnexus-grammar-skip.sh`. The workflow consumes the script's exit code only (does NOT re-implement Signal 1 / Signal 3 logic per AC-CICD-4c-9; does NOT write any `mcp-events.jsonl` event per AC-CICD-4c-10 — script is the authoritative emitter). On exit non-zero: write FR-6-shaped Markdown to `$GITHUB_STEP_SUMMARY` naming mechanism ("FR-4c calibration CI wiring"); calibration script path; offending grammar (Dart or Proto) re-surfaced from script stdout; failing Signal-N; remedial hint (pin back / amend script / open follow-on).
- **Dependencies:** T0.2 (SHAs), T2.4 (the FR-4b script must exist in the devcontainer image).
- **Estimate:** M.
- **Satisfies AC:** AC-FR-4c-a, AC-FR-4c-b, AC-FR-4c-c, AC-FR-4c-d, AC-CICD-4c-1, AC-CICD-4c-2, AC-CICD-4c-3, AC-CICD-4c-4, AC-CICD-4c-5, AC-CICD-4c-6, AC-CICD-4c-7, AC-CICD-4c-8, AC-CICD-4c-9, AC-CICD-4c-10, AC-CICD-4c-11; AC-NFR-4-b; AC-NFR-7-a, AC-NFR-8-a (no credentials surface); AC-FR-6-a (FR-4c surface).
- **L1 verification:** `.github/workflows/gitnexus-grammar-skip-calibration.yml` exists; YAML parses; `actionlint .github/workflows/gitnexus-grammar-skip-calibration.yml` exits 0; the file string-matches both SHAs from T0.2 (same SHAs as T3.1); the file declares the `concurrency` block, the `timeout-minutes: 5`, and `permissions: contents: read`.
- **L2 verification:** Co-validation with T3.1 — both workflow files lint clean together. The `cron: '0 7 * * 1'` expression is valid (verified by `actionlint`'s cron-expression check or manual cron parser).
- **L3 verification:** Pre-merge `workflow_dispatch` run against the draft branch — per cicd-design v0.3.0 §D-0010, three runs measure wall-clock; p95 under 2 minutes; all three exit green (running against `gitnexus@1.6.5` should produce calibration `outcome: "pass"`); the `concurrency` group is observed in the GitHub Actions UI; a fixture PR opening with a `versions.env` change confirms the trigger fires.

#### T3.3: Lint both workflow files atomically with `actionlint`

- **Layer:** CI/CD.
- **Description:** Per Blueprint v2.2.0 §Implementation Plan Cross-Layer Sequencing Note and cicd-design v0.3.0 §Plan task — actionlint deferral: BOTH workflow files must pass `actionlint` (or `mcp__actionlint-mcp__lint_workflow`) before EITHER is committed. A half-committed `.github/workflows/` directory is not a valid intermediate state. This task is the lint gate that wraps T3.1 and T3.2's exit before they land in the bundled PR.
- **Dependencies:** T3.1, T3.2.
- **Estimate:** XS.
- **Satisfies AC:** AC-FR-5-a (workflow well-formed); AC-FR-4c-a (workflow well-formed); transitively all AC-CICD-* (the workflows must lint clean to satisfy any of their ACs).
- **L1 verification:** `actionlint .github/workflows/mcp-connectivity-smoke.yml .github/workflows/gitnexus-grammar-skip-calibration.yml` (or the MCP equivalent) exits 0 with no findings.
- **L2 verification:** No SHA-pin findings; no untrusted-input-interpolation findings; no permissions-block findings.
- **L3 verification:** Both workflow files are committed in the same commit (or commit group) within the bundled PR; the bundled PR's CI shows no actionlint failures in the post-commit lint step.

### Phase 3 Exit Criteria

- All three Phase 3 tasks' L3 verifications pass.
- `.github/workflows/mcp-connectivity-smoke.yml` (FR-5) and `.github/workflows/gitnexus-grammar-skip-calibration.yml` (FR-4c) both exist, both lint clean under `actionlint`, both use the same SHA pins (one per action) from T0.2.
- Pre-merge validation per cicd-design v0.3.0 §D-0010 has been performed: three `workflow_dispatch` runs each for FR-5 and FR-4c against the draft branch; p95 for FR-5 < 4 min, p95 for FR-4c < 2 min; all six runs exit green; cron expression verified by `actionlint` parser.

## Phase 4 — Bundle finalization (FR-7 register, CLAUDE.md counter, pre-merge integration smoke)

### Goal

Land the bundle's small finalization tasks: FR-7 deferral-register verify-and-tighten; CLAUDE.md single-character counter update (`OP-1..OP-10` → `OP-1..OP-11`); pre-merge integration smoke that exercises every mechanism in isolation per NFR-11 / AC-X-1 and end-to-end per Blueprint §Integration Verification Points. Open the single bundled PR per D-0008.

### Tasks

#### T4.1: FR-7 deferral-register verify-and-tighten — rows H-4 and B-1

- **Layer:** Claude Code.
- **Description:** Edit `Issues/devcontainer-mcp-provisioning-r1-deferrals/register.md` to verify and tighten rows H-4 (GitNexus install smoke) and B-1 (CI `claude mcp list` smoke) as adopted-by `pipeline-quickwins-hardening-r1`. Per Blueprint v1 §FR-7, these rows already carry the adoption parenthetical at lines 56 and 141 (codebase-confirmed); this task verifies the existing entries and tightens any prose that has drifted since the adoption parenthetical was added. Per Blueprint §Cross-references — Resolved Q-items / D-0009: the register update lives in this feature's deliverable archive (NOT a separate housekeeping commit) — that disposition is honored by landing the change in this same bundled PR.
- **Dependencies:** T0.1.
- **Estimate:** XS.
- **Satisfies AC:** AC-FR-7-a, AC-CC-7-a, AC-CC-7-b, AC-CC-7-c, AC-CC-7-d (see blueprint-v1 §FR-7 ACs).
- **L1 verification:** `Issues/devcontainer-mcp-provisioning-r1-deferrals/register.md` contains both rows H-4 and B-1 with the adopted-by line referencing `pipeline-quickwins-hardening-r1`.
- **L2 verification:** Diff against `main` shows changes only to rows H-4 and B-1 (line 56, line 141, and any adjacent prose tightening); no other rows changed.
- **L3 verification:** The deliverable archive at deliverable-archive time captures this register state as the "rows adopted" snapshot.

#### T4.2: Update `CLAUDE.md` — `OP-1..OP-10` → `OP-1..OP-11` counter

- **Layer:** Claude Code / Project Filesystem.
- **Description:** Edit `CLAUDE.md` (which is a git-tracked symlink to `AGENTS.md` per the project's single-source-of-truth convention; edit `AGENTS.md`). Single-character counter update at the auditing-mcp OP-rule reference site (per Blueprint §Change Impact Map): `OP-1..OP-10` → `OP-1..OP-11`. No other prose changes per Blueprint §Non-Scope.
- **Dependencies:** T1.4 (the OP-11 rule must exist for the counter to point at), T1.9 (the routing table must reference OP-11).
- **Estimate:** XS.
- **Satisfies AC:** AC-FR-3-a (transitively — the new OP-11 rule is reflected in the project-wide agent context); AC-NFR-15 (agent-driven workflow remains accessible — no ceremony added).
- **L1 verification:** `CLAUDE.md` (via the symlink → `AGENTS.md`) contains the literal string `OP-1..OP-11` and does NOT contain `OP-1..OP-10` at the same site.
- **L2 verification:** Diff against `main` shows a single-character change (the digit `0` → `1`) at the OP-rule counter reference.
- **L3 verification:** Any sub-agent reading `CLAUDE.md` sees the OP-11 counter and can find the rule under `auditing-mcp/`.

#### T4.3: Per-mechanism isolation smoke — each of the five mechanisms run alone (AC-X-1)

- **Layer:** Cross-cutting (orchestrator-level smoke).
- **Description:** Per Blueprint §Integration Verification Points and AC-X-1 (NFR-11 per-mechanism isolation): exercise each of the five mechanisms in isolation against a workspace where the other four are disabled, and confirm each produces the expected behavior for its named failure mode. Five sub-smokes: (a) FR-1 alone — disable FR-2/FR-3/FR-4 family/FR-5; pipeline run with a fixture reviewer-output containing an approving verdict + BLOCKER finding triggers FR-1 halt. (b) FR-2 alone — disable the others; FULL-scope fixture with one stage `execution_mode: parent-driven-workaround` triggers FR-2 refusal. (c) FR-3 alone — disable the others; run OP-11 against a fixture `.mcp.json` with a drifted entry triggers FR-3 blocker. (d) FR-4 family alone — three sub-sub-smokes for FR-4a / FR-4b / FR-4c per AC-X-1 second sentence: FR-4a alone runs on rebuild; FR-4b alone runs by maintainer invocation; FR-4c alone triggers from `workflow_dispatch` against draft branch. (e) FR-5 alone — disable the others; fixture PR with a non-connected server triggers FR-5 fail.
- **Dependencies:** T1.3, T1.4, T1.7, T1.8, T2.2, T2.4, T3.1, T3.2.
- **Estimate:** M.
- **Satisfies AC:** AC-X-1 (NFR-11 per-mechanism isolation); AC-NFR-11-a (each single mechanism produces its expected behavior in isolation).
- **L1 verification:** Each of the five sub-smokes (plus three sub-sub-smokes for the FR-4 family) is executed and its output captured.
- **L2 verification:** Each sub-smoke produces its expected fail/refuse/halt outcome on the named failure mode and its expected pass outcome on the negation.
- **L3 verification:** All five mechanisms' isolation smokes pass; no sub-smoke produces an unexpected interaction with the disabled mechanisms.

#### T4.4: End-to-end orchestrator smoke — all five mechanisms enabled

- **Layer:** Cross-cutting (orchestrator-level smoke).
- **Description:** Per Blueprint §Integration Verification Points: run the orchestrator end-to-end against a known-good fixture pipeline with ALL five mechanisms enabled. Confirm no false positives, no false negatives, no interaction failures. This is the "all five mechanisms enabled" smoke that complements T4.3's "one at a time" smoke.
- **Dependencies:** T4.3 (per-mechanism isolation confirmed first).
- **Estimate:** M.
- **Satisfies AC:** AC-FR-6-a (every mechanism's diagnostics include the four FR-6 fields; verified by inspecting all five mechanisms' on-fail outputs); AC-NFR-5-a (determinism — same input produces same outcome on repeat); AC-NFR-9-a (existing reviewer outputs the prior pipeline accepted continue to pass).
- **L1 verification:** End-to-end orchestrator run completes; no unexpected errors in any stage.
- **L2 verification:** Each of the five mechanisms' on-pass paths fires (FR-1 pass-through; FR-2 dispatch enters loop for MINOR-scope fixture; FR-3 OP-11 returns no findings; FR-4a green-lights into `install_gitnexus`; FR-5 reports all servers connected).
- **L3 verification:** A repeat run against the same fixture inputs produces byte-identical orchestrator outputs (determinism); a fixture reviewer output the prior pipeline accepted continues to pass FR-1 (NFR-9).

#### T4.5: Q-CS-1b banner integration smoke (NEW v2 verification point)

- **Layer:** Cross-cutting (devcontainer rebuild × event-surface integration).
- **Description:** Per Blueprint §Integration Verification Points: a real devcontainer rebuild with `.claude/runtime/mcp-events.jsonl` carrying both a < 2-week-old and a > 2-week-old `calibration_result` event verifies the Q-CS-1b banner logic. Three rebuild fixtures: (i) `mcp-events.jsonl` empty / no `calibration_result` events → banner emits "NEVER RUN"; (ii) most recent `calibration_result` timestamped 3 weeks ago → banner emits "STALE (last run <timestamp>, >2w ago)"; (iii) most recent `calibration_result` timestamped 3 days ago → banner is silent.
- **Dependencies:** T2.3, T2.5.
- **Estimate:** S.
- **Satisfies AC:** AC-X-4 (Q-CS-1b banner contract).
- **L1 verification:** Three rebuild fixtures execute; each rebuild completes (banner never causes fail-close).
- **L2 verification:** Banner output matches the expected variant for each fixture (NEVER RUN / STALE / silent).
- **L3 verification:** Banner is confirmed informational — none of the three rebuilds exits non-zero from `postCreate.sh` because of the banner block.

#### T4.6: Pipeline migration verification — resume pre-feature checkpoint (AC-CC-2-g)

- **Layer:** Claude Code.
- **Description:** Per Blueprint §Verification Strategy and AC-CC-2-g: run the orchestrator against a checkpoint authored before this feature shipped. The pre-feature checkpoint lacks the `execution_mode` field on each stage; per ADR-0057's absence-default, each stage maps to `execution_mode == "specialist-dispatch"`. The FR-2 dispatch self-check accepts this configuration (no `parent-driven-workaround` stages) and enters the dispatch loop normally. This task is the explicit migration smoke per ADR-0057.
- **Dependencies:** T1.1, T1.7.
- **Estimate:** S.
- **Satisfies AC:** AC-CC-2-g (resume-pre-feature-checkpoint).
- **L1 verification:** A pre-feature `checkpoint.json` fixture (no `execution_mode` field on any stage) exists at `working/feature/pipeline-quickwins-hardening-r1/fixtures/pre-feature-checkpoint.json`.
- **L2 verification:** Running the orchestrator with this fixture as the resume target produces the same Stage 13 outcome the pre-feature orchestrator would produce; FR-2 self-check passes (no refusal).
- **L3 verification:** The full pipeline run-to-completion with the resumed checkpoint exits clean.

#### T4.7: Open single bundled PR per D-0008

- **Layer:** Cross-cutting (workflow housekeeping).
- **Description:** Open the single bundled PR per D-0008 / Q-CC-4 / Q-CS-5 dispositions. PR title: `feat(pipeline-quickwins-hardening-r1): five-mechanism MCP-incident hardening carve-out`. PR description references the PRD, the Blueprint v2.2.0, ADR-0057 v1.0.1, ADR-0058 v1.0.0, and the deferral-register row H-4 + B-1 adoption. PR enumerates per-phase commits inside the bundle for reviewer ergonomics. Confirm both Phase 3 CI workflows fire on the PR open (FR-5 because `.mcp.json` and `.devcontainer/**` may be in the diff; FR-4c because `.devcontainer/versions.env` and `.devcontainer/scripts/calibrate-gitnexus-grammar-skip.sh` are in the diff). Both workflows must pass before merge.
- **Dependencies:** T4.1, T4.2, T4.3, T4.4, T4.5, T4.6.
- **Estimate:** S.
- **Satisfies AC:** N/A — workflow housekeeping (per D-0008 single-bundled-PR shape).
- **L1 verification:** The PR is open with a title and description matching the canonical shape; the PR's commit list reflects the Phase 0..4 commit grouping.
- **L2 verification:** Both Phase 3 workflows (FR-5 and FR-4c) fire on the PR open and run to completion.
- **L3 verification:** Both workflows exit green; reviewer (the user, as feature-pipeline maintainer) approves the PR; PR is mergeable.

### Phase 4 Exit Criteria

- All seven Phase 4 tasks' L3 verifications pass.
- The deferral register marks rows H-4 and B-1 as adopted-by this feature.
- `CLAUDE.md` (via `AGENTS.md`) reflects the OP-1..OP-11 counter update.
- Per-mechanism isolation smoke (T4.3) and all-five-enabled end-to-end smoke (T4.4) both pass.
- Q-CS-1b banner integration smoke (T4.5) passes for all three fixture states.
- Pre-feature checkpoint resume smoke (T4.6) passes (AC-CC-2-g).
- The single bundled PR is open, both new CI workflows pass on it, and it is approved for merge.

## Phase 5 — Rollout (post-merge banner-retirement workflow run, observability)

### Goal

Execute the one explicit post-merge operational action: invoke the FR-4c workflow on `main` once to write the first `calibration_result` event to `.claude/runtime/mcp-events.jsonl`, retiring the Q-CS-1b "NEVER RUN" banner before any operator's first devcontainer rebuild. Confirm steady-state observability via the weekly cron schedule.

T5.2 is the terminal write-action of the run; T5.3 and T5.4 are post-action observation tasks that watch for the first cron-tick and capture post-launch evidence against PRD §Success Criteria.

### Tasks

#### T5.1: Merge the bundled PR to `main`

- **Layer:** Cross-cutting (workflow housekeeping).
- **Description:** Merge the bundled PR opened in T4.7 to `main`. The two new workflows are now on `main`'s ref and the calibration script + FR-4a block + banner + ADRs + audit rule + FR-1 validator + orchestrator changes are live.
- **Dependencies:** T4.7.
- **Estimate:** XS.
- **Satisfies AC:** N/A — workflow housekeeping.
- **L1 verification:** `git log --oneline main -5` shows the merged commit.
- **L2 verification:** `gh workflow list` shows both `mcp-connectivity-smoke.yml` and `gitnexus-grammar-skip-calibration.yml` registered.
- **L3 verification:** Post-merge, the workflow files are on `main`'s ref and `gh workflow run gitnexus-grammar-skip-calibration.yml --ref main` would resolve.

#### T5.2: Immediate post-merge invocation — `gh workflow run gitnexus-grammar-skip-calibration.yml --ref main`

- **Layer:** CI/CD (workflow invocation) + Codespaces (observable banner side-effect).
- **Description:** Per Blueprint v2.2.0 §Implementation Plan task 13 and Architecture Audit cycle 1 finding I-AA-005: immediately after T5.1's merge, invoke `gh workflow run gitnexus-grammar-skip-calibration.yml --ref main` once to land the first `calibration_result` event in `.claude/runtime/mcp-events.jsonl`. This retires the Q-CS-1b "NEVER RUN" banner before any operator's first post-merge devcontainer rebuild — the operational handoff is "merge → run workflow → operators rebuild." From this point onward the Monday 07:00 UTC cron tick covers steady-state observability cadence.
- **Dependencies:** T5.1.
- **Estimate:** XS.
- **Satisfies AC:** AC-CICD-4c-5 (workflow_dispatch path); AC-CS-4b-1, AC-CS-4b-5 (first real `calibration_result` event written and conforms to ADR-0058 shape); AC-X-4 transitive (banner no longer reports "NEVER RUN" on the next operator rebuild).
- **L1 verification:** `gh run list --workflow=gitnexus-grammar-skip-calibration.yml --limit 1` shows a recently-triggered run on `main`.
- **L2 verification:** The run completes with conclusion `success`; the run's `$GITHUB_STEP_SUMMARY` shows a PASS block; one new `calibration_result` event is committed to `.claude/runtime/mcp-events.jsonl` (or the event surface that ADR-0037's Implementation Guidance designates; the file is gitignored per ADR-0037 — verify the event was written via the calibration's own logs).
- **L3 verification:** An operator's first post-merge devcontainer rebuild sees the Q-CS-1b banner silent (event < 2 weeks old) — verified by an opportunistic rebuild within the week of merge.

#### T5.3: Confirm Monday 07:00 UTC cron tick fires on first scheduled invocation

- **Layer:** CI/CD.
- **Description:** Observe the first Monday 07:00 UTC cron tick after T5.1's merge. The cron-triggered FR-4c workflow run should appear in `gh run list --workflow=gitnexus-grammar-skip-calibration.yml`. Confirm it ran, exited successfully (current `gitnexus@1.6.5` pin still honors the env-var contract → calibration `outcome: "pass"`), and wrote a second `calibration_result` event. This task is the steady-state observability confirmation per PRD Success Criteria.
- **Dependencies:** T5.2.
- **Estimate:** XS (observation only; no implementation).
- **Satisfies AC:** AC-CICD-4c-1 (weekly cron trigger); AC-FR-4c-a (cron-triggered invocation surfaces script exit code as job status).
- **L1 verification:** A run with `event: schedule` appears in `gh run list --workflow=gitnexus-grammar-skip-calibration.yml` within the first Monday after T5.1.
- **L2 verification:** That run's conclusion is `success`.
- **L3 verification:** A second `calibration_result` event timestamped at the cron tick is now in `mcp-events.jsonl`; Q-CS-1b banner remains silent on subsequent rebuilds.

#### T5.4: Post-launch verification per PRD Success Criteria

- **Layer:** Cross-cutting.
- **Description:** Per PRD §Success Criteria, observe the first N feature runs / first three FULL-scope runs / first 20 PRs after ship to confirm: (i) zero reviewer outputs with approving verdict + blocking findings reach the orchestrator (FR-1 working); (ii) zero FULL-scope dispatches with single-agent fallback enter the loop (FR-2 working); (iii) any present ADR-0041-to-`.mcp.json` drift surfaces as a blocking finding (FR-3 working); (iv) per-rebuild static-shape drift halts the devcontainer build in sub-100 ms (FR-4a working); (v) behavioral calibration drift fails the FR-4c workflow and emits a fail event (FR-4b+FR-4c working); (vi) non-connected servers in `.mcp.json` fail FR-5 (FR-5 working); (vii) no new flaky-test sources; (viii) no new credential prompts.
- **Dependencies:** T5.2, T5.3.
- **Estimate:** S (ongoing observation over the first weeks post-merge).
- **Satisfies AC:** PRD §Success Criteria quantitative + qualitative metrics; AC-NFR-5-a (determinism — confirmed by observing no flakes); AC-NFR-7-a (no new credential prompts — confirmed by inspection of credential inventory).
- **L1 verification:** PRD §Success Criteria observation log captured at `working/feature/pipeline-quickwins-hardening-r1/post-launch-observations.md`.
- **L2 verification:** Each of the eight success criteria items has at least one observed data point recorded.
- **L3 verification:** No item produces a "kill criteria" trigger per PRD §Rollout Plan within the observation window; if a kill criterion fires, the corresponding mechanism is reverted per the kill-criteria procedure and a follow-up Issue is opened.

### Phase 5 Exit Criteria

- The bundled PR is merged to `main`.
- One `calibration_result` event has been written via the immediate post-merge `gh workflow run` (T5.2); the Q-CS-1b banner reports silent on the next rebuild.
- The Monday 07:00 UTC cron tick fires on its first scheduled invocation post-merge and the FR-4c workflow exits green (T5.3).
- Post-launch observation log is open and populated against the PRD §Success Criteria (T5.4).

---

## Cross-Phase Dependencies

```
Phase 0 (Setup)
  T0.1 ─┬─► T0.2 ─► (SHA pins) ──────────────────────────┐
        │                                                 │
        ├─► T0.3 ─► (ADR-0041 row anchors) ──┐            │
        │                                     ▼            │
        ├─► T0.4 ─► (postCreate.sh anchor) ──┼──┐         │
        │                                     │  │         │
        └─► T0.5 ─► (tool availability) ──────┼──┼─────────┼────┐
                                              │  │         │    │
Phase 1 (Claude Code foundation)              │  │         │    │
  T1.1 (ADR-0057 v1.0.1) ────────────┐        │  │         │    │
  T1.2 (ADR-0058 v1.0.0) ─────────┐  │        │  │         │    │
  T1.3 (verdict_findings_parity)  │  │        │  │         │    │
  T1.4 (audit_op11_adr_parity) ◄──┼──┼────────┘  │         │    │
  T1.5 (ADR-0041 row 70+71 annot)◄┴──┘           │         │    │
  T1.6 (scope_class hoist)        │              │         │    │
  T1.7 (FR-2 self-check) ◄────────┴──────────────┘         │    │
  T1.8 (FR-1 wire-in @ 9 sites) ◄── T1.3                   │    │
  T1.9 (auditing-mcp routing) ◄── T1.4                     │    │
                                                            │    │
Phase 2 (Codespaces)                                        │    │
  T2.1 (OP-7 schema extension) ◄── T1.2                    │    │
  T2.2 (FR-4a block) ◄────────────────────────────────────┘    │
  T2.3 (Q-CS-1b banner) ◄── T2.2                                 │
  T2.4 (FR-4b script) ◄── T1.2, T2.1                             │
  T2.5 (FR-4b emission integration) ◄── T2.1, T2.2, T2.3, T2.4   │
  T2.6 (cosmetic 5→4 fix)                                        │
  T2.7 (KB-mcp-design update) ◄── T1.2                           │
  T2.8 (KB-mcp-platform update) ◄── T1.2, T2.4                   │
                                                                  │
Phase 3 (CI/CD)                                                   │
  T3.1 (FR-5 workflow) ◄── T0.2 ────────────────────────────────┘
  T3.2 (FR-4c workflow) ◄── T0.2, T2.4
  T3.3 (actionlint both) ◄── T3.1, T3.2

Phase 4 (Bundle finalization)
  T4.1 (FR-7 register)
  T4.2 (CLAUDE.md counter) ◄── T1.4, T1.9
  T4.3 (per-mechanism isolation) ◄── T1.3, T1.4, T1.7, T1.8, T2.2, T2.4, T3.1, T3.2
  T4.4 (end-to-end smoke) ◄── T4.3
  T4.5 (Q-CS-1b smoke) ◄── T2.3, T2.5
  T4.6 (pre-feature checkpoint resume) ◄── T1.1, T1.7
  T4.7 (open bundled PR) ◄── T4.1..T4.6

Phase 5 (Rollout)
  T5.1 (merge to main) ◄── T4.7
  T5.2 (immediate post-merge workflow run) ◄── T5.1
  T5.3 (first cron tick observation) ◄── T5.2
  T5.4 (post-launch observation log) ◄── T5.2, T5.3
```

### Parallelization opportunities

Within Phase 1, the following tasks can run in parallel (no intra-phase dependencies between them):
- T1.1 (ADR-0057) and T1.2 (ADR-0058) — independent ADR authoring.
- T1.3 (FR-1 validator), T1.4 (FR-3 OP-11 rule), T1.5 (ADR-0041 annotations), T1.6 (scope_class hoist) — independent scripts/edits; T1.4 logically reads cleaner after T1.5 but the L1/L2 checks don't strictly require it.
- T1.7 depends on T1.1 and T1.6; T1.8 depends on T1.3; T1.9 depends on T1.4 — but T1.7, T1.8, T1.9 themselves are independent.

Within Phase 2:
- T2.6 (cosmetic 5→4 fix) is independent of everything else in Phase 2.
- T2.7 and T2.8 (KB doc updates) depend only on T1.2 (and T2.8 also on T2.4 for the example record source) — can run in parallel with each other.
- T2.1 → T2.4 → T2.5 is the critical-path chain inside Phase 2.

Within Phase 3:
- T3.1 and T3.2 can run in parallel; T3.3 gates both.

Within Phase 4:
- T4.1 and T4.2 are independent of each other and can run in parallel.
- T4.3, T4.5, T4.6 are independent of each other and can run in parallel after their respective Phase 1/2/3 prerequisites land.
- T4.4 depends on T4.3; T4.7 depends on all of T4.1..T4.6.

Phase 5 is strictly sequential: T5.1 → T5.2 → T5.3 → T5.4.

### Critical path

The critical path through this Plan:
T0.1 → T1.2 → T2.1 → T2.4 → T2.5 → T3.2 → T3.3 → T4.3 → T4.4 → T4.7 → T5.1 → T5.2.

The longest single chain inside the PR is the Codespaces × CI/CD coupling: ADR-0058 → OP-7 schema extension → FR-4b script → FR-4b emission integration → FR-4c workflow → actionlint gate → integration smokes → PR open.

## L1/L2/L3 Verification Discipline

Every task above carries three verification criteria per the canonical L1/L2/L3 discipline:

- **L1 (cheapest, seconds):** File exists at expected path; YAML/JSON parses; lint passes; type-check passes; the artifact is well-formed.
- **L2 (functional, minutes):** Unit-style fixture test green; one-off script returns expected output for representative inputs; manual click-through succeeds for the artifact's local behavior.
- **L3 (integration, tens of minutes to hours):** End-to-end test or smoke that exercises the artifact in its production-shaped context; the Blueprint AC this task satisfies passes its acceptance test (authored downstream by `test-acceptance-author`); the Phase Validator (authored downstream by `test-phase-validator-author`) aggregates these L3s across the phase.

A task is **complete** when all three pass. L1 passing but L2 failing means the artifact exists but doesn't work; L1+L2 passing but L3 failing means the local behavior works but breaks in integration. Phase Validators consume the L3 verifications for each phase.

## Acceptance Test Cross-Reference

Every Blueprint Acceptance Criterion maps to at least one Plan task. Every Plan task either satisfies at least one AC or is explicitly tagged `N/A — setup` (Phase 0 / housekeeping). The `review-cross-artifact-auditor` Cross-Artifact Audit verifies this mapping is exhaustive and non-orphan in both directions.

### FR-1 — Verdict-vs-findings parity validator

| AC ID | Satisfied by task(s) |
|---|---|
| AC-FR-1-a / AC-CC-1-a | T1.3, T1.8 |
| AC-FR-1-b / AC-CC-1-b | T1.3 |
| AC-FR-1-c | T1.3 |
| AC-CC-1-c through AC-CC-1-h | T1.3, T1.8 |

### FR-2 — Orchestrator dispatch self-check

| AC ID | Satisfied by task(s) |
|---|---|
| AC-FR-2-a / AC-CC-2-a | T1.6, T1.7 |
| AC-FR-2-b / AC-CC-2-b | T1.7 |
| AC-FR-2-c | T1.7 |
| AC-CC-2-c through AC-CC-2-f | T1.7 |
| AC-CC-2-g (resume pre-feature checkpoint) | T1.1, T4.6 |

### FR-3 — `.mcp.json` ↔ ADR-0041 parity audit rule OP-11

| AC ID | Satisfied by task(s) |
|---|---|
| AC-FR-3-a / AC-CC-3-a | T1.4, T1.9 |
| AC-FR-3-b / AC-CC-3-b | T1.4 |
| AC-FR-3-c | T1.4, T1.5 |
| AC-CC-3-c through AC-CC-3-k | T1.4 |
| AC-CC-3-l (deprecated row skip) | T1.4, T1.5 |

### FR-4a — Per-rebuild static-shape check

| AC ID | Satisfied by task(s) |
|---|---|
| AC-FR-4a-a / AC-CS-4a-1 | T2.2 |
| AC-FR-4a-b | T2.2 |
| AC-FR-4a-c / AC-CS-4a-3 | T2.2 |
| AC-FR-4a-d / AC-CS-4a-2 | T2.2 |
| AC-CS-4a-4 (no Swift assertion) | T2.2 |
| AC-CS-4a-5 (sentinel-less) | T2.2 |
| AC-CS-4a-6 (sub-100 ms budget) | T2.2 |
| AC-CS-4a-7 (FR-6 diagnostic) | T2.2 |

### FR-4b — Opt-in behavioral calibration script

| AC ID | Satisfied by task(s) |
|---|---|
| AC-FR-4b-a / AC-CS-4b-1 | T2.4 |
| AC-FR-4b-b | T2.4 |
| AC-FR-4b-c / AC-CS-4b-2 | T2.1, T2.4, T2.5 |
| AC-FR-4b-d | T2.4 |
| AC-CS-4b-3 (not invoked from postCreate.sh) | T2.2, T2.4 (negative; verified by absence of invocation in T2.2's block) |
| AC-CS-4b-4 (no Swift assertion) | T2.4 |
| AC-CS-4b-5 (ADR-0058 payload conformance) | T1.2, T2.4, T2.5 |
| AC-CS-4b-6 (FR-6 diagnostic) | T2.4 |
| AC-CS-4b-7 (under 60s wall-clock informational) | T2.4 |

### FR-4c — GitHub Actions workflow driving FR-4b

| AC ID | Satisfied by task(s) |
|---|---|
| AC-FR-4c-a / AC-CICD-4c-1 (cron) | T3.2, T5.3 |
| AC-FR-4c-b / AC-CICD-4c-2 (on-change-to-versions.env) | T3.2 |
| AC-FR-4c-c / AC-CICD-4c-3 (fail surfaces in summary) | T3.2 |
| AC-FR-4c-d / AC-CICD-4c-4 (trigger-restriction) | T3.2 |
| AC-CICD-4c-5 (workflow_dispatch) | T3.2, T5.2 |
| AC-CICD-4c-6 (NFR-4 budget) | T3.2 |
| AC-CICD-4c-7 (concurrency) | T3.2 |
| AC-CICD-4c-8 (no credentials) | T3.2 |
| AC-CICD-4c-9 (exit-code-as-contract; no Signal re-implementation) | T3.2 |
| AC-CICD-4c-10 (no duplicate event emission) | T3.2 |
| AC-CICD-4c-11 (timeout-minutes: 5) | T3.2 |

### FR-5 — MCP connectivity smoke workflow

| AC ID | Satisfied by task(s) |
|---|---|
| AC-FR-5-a / AC-CICD-5-a | T3.1 |
| AC-FR-5-b / AC-CICD-5-b | T3.1 |
| AC-FR-5-c / AC-CICD-5-c | T3.1 |
| AC-CICD-5-d through AC-CICD-5-g | T3.1 |

### FR-6 — Actionable diagnostics (cross-cutting)

| AC ID | Satisfied by task(s) |
|---|---|
| AC-FR-6-a / AC-6-a | T1.3 (FR-1), T1.4 (FR-3), T1.7 (FR-2), T2.2 (FR-4a), T2.3 (Q-CS-1b banner — three of four fields per AC-X-4), T2.4 (FR-4b), T3.1 (FR-5), T3.2 (FR-4c), T4.4 (verified end-to-end) |

### FR-7 — Deferral-register tightening

| AC ID | Satisfied by task(s) |
|---|---|
| AC-FR-7-a / AC-CC-7-a through AC-CC-7-d | T4.1 |

### Cross-layer / Operational

| AC ID | Satisfied by task(s) |
|---|---|
| AC-X-1 (NFR-11 per-mechanism isolation) | T4.3 |
| AC-X-2 (NFR-13 event surface — four-type closed enum) | T1.2, T2.1, T2.4, T2.7, T2.8 |
| AC-X-3 (NFR-15 allowlists unchanged) | (verified by absence of allowlist modification — T0.1's clean-tree check + Phase 4's diff review confirms) |
| AC-X-4 (Q-CS-1b banner) | T2.3, T2.5, T4.5 |

### Non-Functional ACs

| AC ID | Satisfied by task(s) |
|---|---|
| AC-NFR-1-a (FR-1 validator overhead) | T1.3 (per cc-design v0.2.0 concrete threshold per U-8) |
| AC-NFR-2-a (FR-2 self-check overhead) | T1.7 (per cc-design v0.2.0 concrete threshold per U-8) |
| AC-NFR-3-a (FR-4a sub-100 ms) | T2.2 |
| AC-NFR-3-b (FR-4b budget folded into NFR-4) | T2.4 |
| AC-NFR-4-a (FR-5 under 5 min) | T3.1 |
| AC-NFR-4-b (FR-4c under 5 min) | T3.2 |
| AC-NFR-5-a (determinism) | T1.3, T1.4, T2.2, T2.4, T3.1, T3.2, T4.4 |
| AC-NFR-6-a (fail-closed on internal errors) | T1.3, T1.4, T2.2, T2.4 |
| AC-NFR-7-a (no new credential surface) | T2.4, T3.1, T3.2 |
| AC-NFR-8-a (no credentials in diagnostics) | T1.3, T1.4, T2.2, T2.4, T3.1, T3.2 |
| AC-NFR-9-a (backward compat — existing reviewer outputs) | T1.3, T4.4 |
| AC-NFR-10-a (backward compat — `.mcp.json` matches) | T1.4 |
| AC-NFR-11-a (per-mechanism isolation) | T4.3 |
| AC-NFR-13-a / AC-NFR-13-b (event surface — four-type closed enum) | T1.2, T2.1, T2.4 |
| AC-NFR-14 (Codespace boot cost bounded) | T2.2 (FR-4a sub-100 ms), T2.3 (banner negligible) |
| AC-NFR-15 (agent-driven workflow remains accessible) | T4.2 (no ceremony added) |

### Setup-only tasks (Phase 0, plus housekeeping)

The following tasks are explicitly tagged `N/A — setup` and intentionally do not satisfy any AC; they exist to set up downstream work:

- T0.1 (branch creation)
- T0.2 (SHA resolution) — transitive enabler for AC-CICD-5-a, AC-CICD-4c-1; itself setup
- T0.3 (ADR-0041 anchor capture)
- T0.4 (postCreate.sh anchor capture)
- T0.5 (tool availability check)
- T2.6 (cosmetic 5→4 fix per Q-CS-3)
- T4.7 (open bundled PR)
- T5.1 (merge to main)

## Estimation Methodology

T-shirt sizes XS / S / M / L based on representative comparable work in this codebase:

- **XS** — single-line / single-character edits; documentation pointer updates; branch creation; SHA resolution; anchor capture (< 30 min).
- **S** — single-file scripts under ~100 lines; targeted edits to existing scripts; ADR authoring at v1.0.0 / v1.0.1; smoke task with established fixtures (30 min – 2h).
- **M** — multi-file edits (e.g., orchestrator SKILL.md wire-in across 9 sites); new Python script with fixture suite; new workflow file with `actionlint` discipline and pre-merge validation; multi-fixture smoke task (2h – 6h).
- **L** — the FR-4b calibration script (T2.4) is the only L-sized task: full scratch-install + Signal 1 + Signal 3 + optional negative-assertion + ADR-0058-conformant event emission + trap-based cleanup; ~150 lines of careful bash + AC-CS-4b-1..7 coverage (6h+).

Total estimate across all 36 tasks: ~5-7 working days of single-author effort for the bundled PR (Phases 0-4) + ~1 hour of post-merge operations (Phase 5) + open-ended observation window for T5.4.

These estimates are not for velocity tracking. They exist to flag tasks that should be split (the L-sized T2.4 is at the upper bound of what a single task should carry; if implementation reveals it's larger, split into "Signal 1 + Signal 3 only" and "negative-assertion + event emission + cleanup" sub-tasks).

## Resourcing Posture

Single-maintainer (the user, as feature-pipeline maintainer per PRD §Primary Users) executes the full Plan. No separate team capacity is assumed (per PRD §Constraints — Resource constraints). Task descriptions are written assuming the maintainer has domain knowledge of the repository's `.devcontainer/`, `.claude/skills/auditing-mcp/`, `.claude/skills/recipe-feature-pipeline/`, and ADR conventions — i.e., this is NOT a "any contributor" Plan; it is a Plan for the maintainer of this codebase.

Tasks that benefit from sub-agent delegation (per the CLAUDE.md sub-agent delegation reference):
- T1.4 + T1.5 (FR-3 OP-11 + ADR-0041 annotations) — `design-claude-code` could co-author if a future round needs it.
- T3.1 + T3.2 (the two workflows) — `design-cicd` has `actionlint-mcp` allowlist; T3.3's lint gate naturally routes there.
- T2.2 + T2.3 + T2.4 (Codespaces work) — `design-codespaces` has `serena` allowlist; useful for the `postCreate.sh` edits and the script authoring.

The Plan does not mandate sub-agent delegation; the single maintainer can execute every task directly.

## Open Items (Pending Cross-Artifact Audit)

The Plan author identified the following items that the Plan cannot resolve from the Blueprint alone. Each becomes an item the Cross-Artifact Audit (`review-cross-artifact-auditor`) will check against the acceptance tests and phase validators:

- **OI-1: Concrete NFR-1 / NFR-2 latency thresholds. [RESOLVED at cross-artifact audit cycle 1 — see I-CA-005 in `reconciliation-log-r3.md`].** Originally deferred to cc-design v0.2.0 per PRD §U-8 (unresolved at Plan v1.0.0 / v1.0.1 authoring). RESOLUTION: Blueprint v2.2.0 §NFR-1 and §NFR-2 now define concrete inline thresholds — 250 ms p95 for NFR-1 (FR-1 validator overhead) and 100 ms p95 for NFR-2 (FR-2 self-check overhead). Acceptance Tests AT-075 (NFR-1) and AT-076 (NFR-2) assert these thresholds against the running validator / self-check. The cc-design v0.2.0 extraction was completed as part of the v2.1 → v2.2.0 lift cycle; T1.3 / T1.7 L3 checks reference the same thresholds via the Blueprint v2.2.0 §NFR section. No further extraction required; no Blueprint gap remains. The Cross-Artifact Audit cycle 2 reviewer can confirm closure via Blueprint v2.2.0 §NFR-1 / §NFR-2 and Acceptance Tests AT-075 / AT-076.
- **OI-2: Exact blocking-severity set for FR-1.** Per PRD §U-1 (resolved at cc-design per the Blueprint's claim). The Plan trusts cc-design v0.2.0 has named the exact severity tokens. If `test-acceptance-author` cannot extract the literal severity tokens from cc-design, this is a Blueprint completeness gap.
- **OI-3: Exact canonicalization rules and `[DEPRECATED]` skip semantics for OP-11.** Per PRD §U-3 (resolved at cc-design). The Plan trusts cc-design has documented the canonicalize+opaque-tokens algorithm. The Plan's T1.4 L2 fixture suite assumes the rules are documented; if they are not, T1.4 cannot author the fixture suite without re-engaging design.
- **OI-4: Whether the auditing-mcp Gate-6 hard gate per ADR-0043 already encloses all OP-rules or requires an explicit OP-11 registration step beyond T1.9's routing table update.** The Plan assumes the routing-table update in T1.9 is sufficient; if Gate-6 requires an additional registration (e.g., a manifest file), the Plan must add a task.
- **OI-5: Verification of the `.devcontainer/postCreate.sh` line 197-198 anchor stability through the duration of the implementation window.** T0.4 captures the anchor at T0.1's start; if intervening commits to `main` drift the file between T0.4 and T2.2, the anchor needs re-discovery. This is a process risk, not a design gap, but the Cross-Artifact Audit may want to flag it as a sequencing constraint for the implementor.

## Update History

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-05-26 | plan-author | Initial Plan derived from Blueprint v2.1 (post-Architecture-Audit cycle 2 pass). Six phases (Phase 0 setup → Phase 1 Claude Code → Phase 2 Codespaces → Phase 3 CI/CD → Phase 4 finalization → Phase 5 rollout); 36 tasks (originally counted as 47; corrected to 36 in v1.0.1 per I-DR-001 — counter error during authoring, no tasks added or removed; actual rendered count: Phase 0: 5 + Phase 1: 9 + Phase 2: 8 + Phase 3: 3 + Phase 4: 7 + Phase 5: 4 = 36); single bundled PR per D-0008; immediate post-merge `gh workflow run` per Blueprint §Implementation Plan task 13; OP-7 schema extension sequenced before first FR-4b emission per task 12. |
| 1.0.1 | 2026-05-26 | plan-author | Reconciliation cycle 1 (Plan Gate-1 reviewer family) — three surgical edits: I-DR-001 task count corrected 47 → 36 (counter error; no tasks added/removed); I-DR-005 T2.6 server-count disposition clarified (postCreate.sh line 5 stale at "5 OSS-local", correct value is 4 per lines 9 / 193); I-DR-003 Phase 5 Goal clarification distinguishing T5.2 terminal write-action from T5.3 / T5.4 post-action observation tasks. Source: `reconciliation-log-r2.md`. |
| 1.0.2 | 2026-05-26 | plan-author | Cross-Artifact Audit cycle 1 reconciliation — three surgical edits: I-CA-003 Blueprint pointer references bumped v2.1 → v2.2.0 across §Source, §Purpose, and in-body citations (Plan narrative aligned to current Blueprint); I-CA-004 v1.0.0 Update History row amended to inline-flag the 47→36 correction (preventing reader-visible contradiction between v1.0.0 and v1.0.1 rows); I-CA-005 Open Item OI-1 marked RESOLVED with citations to Blueprint v2.2.0 §NFR-1/§NFR-2 inline thresholds (250 ms p95 / 100 ms p95) and Acceptance Tests AT-075 / AT-076. No task-content changes, no AC-citation changes, no phase decomposition changes, no exit-criteria changes. Source: `reconciliation-log-r3.md`. |
