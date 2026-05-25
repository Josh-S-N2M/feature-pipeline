---
id: BP-adr-placement-mechanism-repair-r1
version: 1.2.0
status: draft
feature_slug: adr-placement-mechanism-repair-r1
derived_from: working/feature/adr-placement-mechanism-repair-r1/prd-v1.md
predecessor: blueprint-v1.md (v1.1.0)
reconciliation_cycle: 2
codebase_analysis: working/feature/adr-placement-mechanism-repair-r1/codebase-analysis.json
prd_version: 1.0.2
intent_clarification_version: 2.0.1
research_plan_version: 1.0.0
synthesis_version: 1.0.0
codebase_analysis_schema: v1.1.0
cc_design_version: 1.0.0
scope_class: FULL
layer_scope: ["claude-code"]
adrs_referenced:
  - ADR-0005
  - ADR-0017
  - ADR-0019
  - ADR-0027
  - ADR-0031
  - ADR-0035
  - ADR-0036
  - ADR-0042
  - ADR-0044
adrs_authored:
  - ADR-0053  # amended to v1.0.1 in reconciliation cycle 1 (frontmatter-stable; per ADR-0005); unchanged in cycle 2
  - ADR-0054  # amended to v1.0.1 in reconciliation cycle 1; unchanged in cycle 2
  - ADR-0055  # amended to v1.0.1 in reconciliation cycle 1; unchanged in cycle 2
generated: 2026-05-24T20:15:00Z
revised: 2026-05-25T00:00:00Z
revised_after: architecture-audit-r2
generated_by: design-composer
---

# ADR Placement Mechanism Repair — Design Document (Blueprint v1)

## Contents

Section completion checklist — each box must be checked (including `N/A — out of scope` rows) before this document leaves draft. The reviewer's Gate 0 check uses this list as the structural-presence anchor.

- [x] Overview
- [x] Design Summary (Meta)
- [x] Background and Context
- [x] Acceptance Criteria (AC) - EARS Format
- [x] Existing Codebase Analysis
- [x] Design
- [x] Implementation Plan
- [x] Security Considerations
- [x] Test Boundaries
- [x] Verification Strategy
- [x] Future Extensibility
- [x] Alternative Solutions
- [x] Risks and Mitigation
- [x] References
- [x] Update History

## Overview

This Blueprint integrates the per-layer `cc-design.md` (the sole per-layer design) into the canonical Blueprint structure and composes the cross-cutting sections required to deliver `adr-placement-mechanism-repair-r1`. The feature repairs the ADR placement mechanism so the canonical-only convention codified by ADR-0036 is structurally enforced at three independent surfaces, every off-canonical ADR is migrated into canonical `adrs/`, every cross-reference is swept to the consolidated location, and every skill that could re-introduce feature-scoped placement is audited and remediated.

### Layer Scope

Declare which layers this feature touches. Sections under Design, Security, Test Boundaries, and Verification corresponding to unchecked layers may be marked `N/A — out of scope` without further elaboration.

- [x] **Claude Code / Project Filesystem** — operator files (`.claude/agents/finalize-deliverable-packager.md`, `.claude/agents/shared-document-reviewer.md`, `.claude/agents/design-composer.md`), orchestrator skill (`.claude/skills/recipe-feature-pipeline/SKILL.md`), new validator (`.claude/skills/auditing-shared/scripts/validate_adr_placement.py`), skill audit + remediation across `.claude/skills/**/*.md`, canonical ADR tree (`adrs/`, plus `adrs/superseded/` for divergent-body archival), feature-scoped ADR sources (`working/feature/**/adrs/`), legacy archive (`adrs-migrated/` consolidation), shipped Blueprint/Plan cross-references, Issues files, README.
- [ ] **Frontend** — N/A — out of scope (no UI surface in this feature).
- [ ] **Backend** — N/A — out of scope.
- [ ] **API** — N/A — out of scope.
- [ ] **Query / Data Access** — N/A — out of scope.
- [ ] **Database** — N/A — out of scope.
- [ ] **CI/CD (GitHub Actions)** — N/A — out of scope. (Codebase analysis confirms no `.github/workflows/*.yml` currently invokes Claude Code or any auditing-shared script. The validator runs locally in Codespace and at three CC-internal surfaces; no CI integration is needed.)
- [ ] **Infrastructure as Code** — N/A — out of scope.
- [ ] **Dev Environment (Codespaces / Devcontainer)** — N/A — out of scope.

**Deviation flag**: scope class is FULL but layer count is one. The single layer's breadth (validator script, repo-wide cross-reference sweep, multi-surface enforcement integration, skill audit and remediation, four-sub-phase migration including legacy-archive consolidation) is substantially larger than a typical single-layer feature. Architecture Auditor should treat the breadth-within-layer as the deviation signal, not the layer count.

### Referenced Specifications

- **UI Spec**: N/A.
- **API Spec**: N/A.
- **Data Model Spec**: N/A.
- **Runbook / Operational Spec**: N/A (this feature's verification harness is itself an operational artifact, captured in §Verification Strategy).

## Design Summary (Meta)

```yaml
design_type: "tooling_change"
risk_level: "medium"
complexity_level: "high"
complexity_rationale: |
  HIGH per the breadth-within-layer deviation: 7-phase decomposition (Phase 0 Discovery
  + setup; Phase 1 operator file repairs; Phase 2 four-sub-phase migration; Phase 3
  cross-reference sweep; Phase 4 validator authoring; Phase 5 surface wiring + skill
  audit; Phase 6 verification). Drives FR-1 through FR-11 and NFR-1 through NFR-8.
  Necessary because the originating failure mode (PKG-BLOCKER-001 at devcontainer-mcp-
  provisioning-r1 Gate-6) demonstrated a single declarative source of truth contradicting
  itself; structural three-surface enforcement is the smallest robust solution that
  prevents recurrence (NFR-6).
layers_touched:
  - "Claude Code / Project Filesystem"
blast_radius:
  runtime: "All future feature-pipeline runs (validator gates + canonical-only default); all future execution-pipeline runs (validator at run_phase_checks.py)"
  build_time: "None — no build pipeline touched; validator runs locally in Codespace"
main_constraints:
  - "Layer scope is CC-only (per PRD; per Intent Clarification CC-only confirmation)"
  - "All file relocations under FR-8b/c/d use git mv to preserve history (NFR-5)"
  - "Validator dependency posture: Python stdlib only (NFR-8); validator latency <5s (NFR-2)"
  - "No --no-verify git commands without explicit user authorization (NFR-7)"
  - "Cross-reference sweep is path-only; semantic edits to shipped artifacts remain out of scope (Q5 revision)"
  - "Three-surface enforcement must be non-redundant and non-contradictory (NFR-6)"
biggest_risks:
  - "Hidden cross-reference form not caught by Phase 0 grep patterns (Assumption A3) → mitigated by D5 Option B extended pattern set + Phase 6 verification"
  - "Divergent-body reconciliation hypothesis from PRD reframed: ADR-0024 is status-lift only (no body archival needed per Discovery IN-002; AC-FR-8b-1.1 fail-safe per AA-014 provides safety net if Discovery claim is wrong); ADR-0044/0045 are numbering collisions (renumber per ADR-0053 v1.0.1, not divergent-body) — risk reframing per Discovery IN-002"
  - "Three enforcement surfaces are redundant rather than defensive → mitigated by NFR-6 non-redundancy proof (see §Design / Three-surface non-redundancy proof)"
  - "Phase 2d archive-wins collision policy produces a frontmatter inconsistency in 7 canonical ADRs (per ADR-0055 v1.0.1; not 8) → mitigated by ADR-0055 provenance frontmatter convention"
  - "Bare-ID semantic-disambiguation sweep across 368 occurrences (per AA-011 user binding decision) inflates Phase 3 Plan effort by orders of magnitude vs the pre-cycle-1 32-edit estimate → mitigated by AC-FR-9-b.1 baseline-heuristic procedure + per-occurrence judgment + AskUserQuestion escalation for ambiguous cases"
unknowns:
  - "Whether ADR-0053's original_id / ADR-0055's superseded_by_consolidation frontmatter fields are honored by any future validator (current expectation: informational only)"
  - "Whether the 'archive carries v2.0.0; canonical carries v1.0.0' pattern was specific to this archive or extends to future consolidations (per ADR-0055 known unknowns)"
```

## Background and Context

### Prerequisite ADRs

- **ADR-0036** (single-location ADR placement, accepted 2026-05-22) — the spec amendment this feature aligns the operators with. The originating directive.
- **ADR-0019** (ADR-NNNN naming convention) — the monotonic ID convention this feature preserves; ADR-0053's renumbering algorithm honors it.
- **ADR-0005** (supersession discipline) — relevant to divergent-body archival under FR-8b and to the archive-wins consolidation per ADR-0055.
- **ADR-0017** (reviewer invocation points) — relevant to AC-US-2 expectations and to the orchestrator-stage gate placement (per ADR-0054, the FR-10 validator gate sits between Design Composition and reviewer invocation, before the 5th reviewer point).
- **ADR-0027** (cwd precondition) — the FR-10 validator's default scan path is the repo root, honoring ADR-0027.
- **ADR-0031** (auditing-shared skill module) — the canonical home for cross-skill helper scripts; the FR-10 validator lives here per ADR-0054.
- **ADR-0035** (auditing-shared skill binding convention) — the subprocess + JSON + exit-code conventions the FR-10 validator follows.
- **ADR-0042** (auditing-mcp family graduation) — extended by ADR-0054 to non-audit-family consumers (the FR-10 validator is the first such consumer).
- **ADR-0044** (flatten execution dispatch hierarchy) — the execution-pipeline surface for the FR-10 validator lives at `run_phase_checks.py`, which the parent orchestrator dispatches per ADR-0044.

### New ADRs authored in this feature (this run)

- **ADR-0053** — ADR-NNNN numbering-collision resolution algorithm + provenance-frontmatter convention. Resolves Q-CC-1.
- **ADR-0054** — Three-surface enforcement pattern for canonical-helper validators (extension of ADR-0042 to non-audit consumers). Resolves the Research-Plan-adjacency-#2 concern and codifies the structural commitments behind FR-10.
- **ADR-0055** — Archive-wins consolidation policy for version-divergent ADR collisions. Resolves OI-2 / Discovery IN-004's 8 collisions and codifies the gate-binding user directive (2026-05-24).

### External Resources Used

| Resource (project-tier label) | Feature-specific identifier | Notes |
|-------------------------------|-----------------------------|-------|
| Python 3 runtime | `python3` (Codespace default) | Stdlib only per NFR-8; needed for `validate_adr_placement.py` |
| Git | `git mv`, `git rm`, `git log --follow` | FR-8 migration mechanism; NFR-5 history preservation; NFR-7 no `--no-verify` |

### Agreement Checklist

#### Scope

- [x] 4 operator files edited: `finalize-deliverable-packager.md`, `shared-document-reviewer.md`, `recipe-feature-pipeline/SKILL.md`, `design-composer.md`.
- [x] 1 new validator script + 2 modified auditing-shared scripts (run_phase_checks.py, smoke_test_auditing_shared.py).
- [x] 8 skill-file remediations (4 in `KB-documentation-criteria`; 1 each in `recipe-feature-pipeline`, `KB-issue-capture`, `capture-issue`, `synthesize`).
- [x] Migration of all off-canonical ADRs (12 byte-identical dedupes; 1 status-lift dedupe; 2 numbering-collision renumbers; 5 feature-scoped relocations; **47 source files in `adrs-migrated/` touched by Phase 2d** decomposing into 7 archive-wins + 1 canonical-wins + 9 no-collision + 1 canonical-only + 30 variant deletions = 48 file-touching operations per ADR-0055 v1.0.1). The 47 figure refers to source files in `adrs-migrated/`, NOT the number of file-touching operations (per AA-012 disambiguation). (47 source files → 48 operations because each of the 7 archive-wins cases is one `mv` of the archive into canonical + one write of the prior canonical body to `adrs/superseded/`, so those 7 sources double-count once; per I-AA-R2-003 cycle-2 clarification.)
- [x] Cross-reference sweep — **expanded in cycle 1 per AA-011 user binding decision**: 32 mechanical path-form edits (14 feature-scoped + 18 `adrs-migrated/`) **+ 368 bare-ID semantic-disambiguation occurrences** (ADR-0044: 223 mentions; ADR-0045: 145 mentions) for the renumbered IDs (ADR-0051 / ADR-0052).
- [x] 3 ADRs authored (ADR-0053, ADR-0054, ADR-0055).
- [x] `.claude/settings.json` narrow Bash allowlist entry for the packager.

#### Non-Scope (Explicitly not changing)

- [ ] Semantic rewrites of shipped Blueprint prose (per Q5 revision; only path-only edits in scope).
- [ ] Phantom-promotion misreading at `working/feature/devcontainer-mcp-provisioning-r1/blueprint-v2.md:1226` (semantic misreading, not a path reference).
- [ ] ADR-NNNN numbering convention (ADR-0019 remains canonical).
- [ ] Promotion-step automation (canonical-only is the only path; validator enforces).
- [ ] Any changes outside the Claude Code / Project Filesystem layer.

#### Constraints

- [x] Parallel operation: N/A (this is a tooling repair; no old/new runtime parallelism).
- [x] Backward compatibility: Not required — applies to: N/A. The feature is itself a migration that eliminates the prior dual-location pattern.
- [x] Performance measurement: Required — NFR-2 validator latency < 5s.
- [x] Zero-downtime deployment: N/A (CC-internal artifacts; no runtime deploy).
- [x] Forward-compatible migration: Not required (the FR-8d archive consolidation is a one-shot; no schema evolution).

#### Applicable Standards

- [x] ADR-0036 (single-location placement) `[explicit]` — Source: `adrs/ADR-0036-single-location-adr-placement.md`.
- [x] ADR-0035 (auditing-shared binding) `[explicit]` — Source: `adrs/ADR-0035-auditing-shared-skill-binding-convention.md`.
- [x] ADR-0019 (naming convention) `[explicit]` — Source: `adrs/ADR-0019-naming-convention.md`.
- [x] Subprocess + JSON + exit 0/2 convention `[explicit]` — Source: `.claude/skills/auditing-shared/scripts/run_phase_checks.py` line 59 (per ADR-0035 + IN-010).
- [x] `git mv` for relocations `[implicit observed]` — Evidence: prior plans (execution-pipeline-design-r1/plan-v2.md, devcontainer-mcp-provisioning-r1/plan-v1.md, issue-capture-mechanism-r1/plan-v1.md). Confirmed: Yes (per NFR-5; codebase-analysis.json `conventions.cc.git_mv_usage_convention`).

#### Quality Assurance Mechanisms

- [x] `validate_adr_placement.py` — Enforces: canonical-only ADR placement — Config: `.claude/skills/auditing-shared/scripts/validate_adr_placement.py` — Covers: repo-wide rglob — Status: `adopted` (this feature introduces it).
- [x] `run_phase_checks.py` dispatch + `validator` dimension rollup — Enforces: aggregate validator findings per phase — Config: existing — Covers: execution-pipeline — Status: `adopted` (FR-10-c).
- [x] `smoke_test_auditing_shared.py` extension — Enforces: positive + negative path smoke for validator — Config: `.claude/skills/auditing-shared/scripts/smoke_test_auditing_shared.py` — Covers: auditing-shared family — Status: `adopted` (FR-10 NFR-2 verification).
- [x] `shared-document-reviewer` (Gate 0/1) — Enforces: structural + quality review of authored artifacts — Config: `.claude/agents/shared-document-reviewer.md` — Covers: 5 invocation points per ADR-0017 — Status: `adopted` (existing; this feature corrects FR-2 contradiction).
- [x] `finalize-deliverable-packager` — Enforces: canonical-only ADR placement at finalize time via FR-10 validator — Config: `.claude/agents/finalize-deliverable-packager.md` (post-FR-1 edit) — Covers: per-feature Gate 6 — Status: `adopted` (this feature reshapes the existing packager check from dual-location to canonical-only).

### Problem to Solve

The originating failure (PKG-BLOCKER-001 raised at `devcontainer-mcp-provisioning-r1` Gate-6) demonstrated that the four operator files governing ADR authoring + review + finalize contradicted ADR-0036 and contradicted each other. The `design-composer` continued to write feature-scoped ADRs because `recipe-feature-pipeline` passed no canonical default; the `finalize-deliverable-packager` continued to BLOCK on the now-impossible dual-location case; the `shared-document-reviewer` carried internally contradictory ADR-placement statements (line 349 vs lines 470–472).

The v2.0.0 user directive at the Intent Confirmation Gate expanded the scope from "four surgical edits + grandfather" to a comprehensive repair: migrate every off-canonical ADR; sweep every cross-reference; wire enforcement at three independent surfaces; audit every skill that could re-introduce the feature-scoped behavior.

### Current Challenges

- **Cross-layer contradiction within a single layer.** Four operator files governing the same convention disagree; no enforcement gate catches the disagreement until Gate-6 surfaces it as a BLOCKER.
- **Stale legacy archive (`adrs-migrated/`).** 47 files spanning 18 ADR IDs; 8 of those collide with canonical with archive-wins content divergence (per Discovery IN-004).
- **Numbering collisions (ADR-0044, ADR-0045).** Two distinct decisions accidentally share each ID; the PRD's "rejected body archival" framing does not apply.
- **No persistent enforcement mechanism.** Today the canonical-only convention lives in three places (ADR-0036 itself, deliverable-archive-spec.md post-amendment, shared-conventions.md:302) but is enforced by zero independent surfaces.

### Requirements

#### Functional Requirements

See PRD §"Functional Requirements" for FR-1 through FR-11. Each is addressed in this Blueprint's §Design / Per-FR realization, with cross-references to the per-layer `cc-design.md` §3 per-FR design table.

#### Non-Functional Requirements

- **Performance**: FR-10 validator latency < 5s on a typical Codespace (NFR-2). The validator emits `elapsed_ms` so latency is observable.
- **Scalability**: N/A — repo-wide scan is bounded by the file count (~few thousand `.md` files); `rglob` completes in <1s on current repo.
- **Reliability**: Each migrated ADR is one atomic Plan task per NFR-1; rollback documented per FR-8 sub-phase.
- **Maintainability**: NFR-3 cross-reference sweep has zero false-negatives (D5 Option B extended pattern set + Phase 6 verification). NFR-4 skill audit findings are remediable (no TBDs in Blueprint per AC-NFR-4-a). NFR-8 validator stays stdlib-only.
- **Operability**: Three-surface enforcement is non-redundant and non-contradictory (NFR-6; proof in §Design / Three-surface non-redundancy proof). NFR-7 no `--no-verify`.

## Acceptance Criteria (AC) - EARS Format

Each AC is written in EARS format per the PRD. This section integrates the PRD's AC-US-N, AC-FR-N, AC-NFR-N, AC-OP-N (full set in `prd-v1.md`) with the CC-design-layer-specific ACs (AC-CC-1 through AC-CC-7 from `cc-design.md` §7).

**EARS Keywords**:
| Keyword | Usage | Test Type |
|---------|-------|-----------|
| **When** | Event-triggered behavior | Event-driven test |
| **While** | State-dependent behavior | State condition test |
| **If-then** | Conditional behavior | Branch coverage test |
| (none) | Ubiquitous behavior | Basic functionality test |

### Functional ACs

#### FR-1 (Delete retired dual-location BLOCKER prose in packager) — Layer: Claude Code

- [ ] **AC-FR-1-a (CC)**: When `.claude/agents/finalize-deliverable-packager.md` is read after this feature ships, the system shall not contain the retired dual-location BLOCKER prose text (the text currently at lines 56–63).
- [ ] **AC-FR-1-b (CC)**: When `finalize-deliverable-packager` runs on a feature whose ADRs were authored only to canonical root `adrs/`, the system shall not raise PKG-BLOCKER-001 or any equivalent dual-location BLOCKER, and the replacement canonical-only check (per FR-10) shall pass.

#### FR-2 (Delete contradictory dual-location prose in reviewer) — Layer: Claude Code

- [ ] **AC-FR-2-a (CC)**: When `.claude/agents/shared-document-reviewer.md` is read after this feature ships, the system shall not contain the contradictory dual-location BLOCKER check at line 349 (or its equivalent location).
- [ ] **AC-FR-2-b (CC)**: When `shared-document-reviewer` reviews a Blueprint that references ADRs at canonical root only, the system shall not flag the canonical-only placement as a violation.

#### FR-3 (Orchestrator `output_adrs_dir` default = canonical root) — Layer: Claude Code

- [ ] **AC-FR-3-a (CC)**: When the orchestrator invokes `design-composer` without an explicit caller-supplied `output_adrs_dir` override, the system shall pass canonical-root `adrs/` (relative to repo root), not a feature-scoped path.
- [ ] **AC-FR-3-b (CC)**: When the orchestrator forwards an explicit caller-supplied `output_adrs_dir` to `design-composer`, the orchestrator shall pass that value unmodified.

#### FR-4 (Design-composer parameter description) — Layer: Claude Code

- [ ] **AC-FR-4-a (CC)**: When `.claude/agents/design-composer.md` is read after this feature ships, the `output_adrs_dir` parameter description shall cite ADR-0036 explicitly and shall state that canonical-root `adrs/` is the default.
- [ ] **AC-FR-4-b (CC)**: The system shall document, in `design-composer.md`, the test-only override mechanism for `output_adrs_dir`.

#### FR-5 (`output_adrs_dir` remains a parameter) — Layer: Claude Code

- [ ] **AC-FR-5-a (CC)**: The system shall retain `output_adrs_dir` as a parameter on `design-composer` (it shall not be eliminated).
- [ ] **AC-FR-5-b (CC)**: Where a caller passes `output_adrs_dir` explicitly, the system shall honor the passed value rather than the default.

#### FR-6 (Blueprint documents migration disposition) — Layer: Claude Code

- [ ] **AC-FR-6-a (CC)**: The Blueprint authored in this feature shall contain a section enumerating every ADR currently outside canonical `adrs/`, classified into one of the 6 categories per Phase 0 Discovery. (Satisfied by §Existing Codebase Analysis / Fact Disposition Table + §Design / Migration map.)
- [ ] **AC-FR-6-b (CC)**: The Blueprint shall document the migration disposition per FR-8 (dedupe / semantic-reconcile / `git mv` / consolidate-with-suffix / delete-with-Git-history-preservation) for each classified ADR. (Satisfied by §Design / Migration map + §Implementation Plan.)

#### FR-7 (SUPERSEDED) — Layer: Claude Code

- [ ] **AC-FR-7-a (CC)**: No acceptance criteria — slot reserved.

#### FR-8 (Migration) — Layer: Claude Code

- [ ] **AC-FR-8a-1 (CC)**: When this feature ships, the 12 byte-identical duplicate ADRs (0026, 0028, 0029, 0030, 0031, 0037, 0038, 0039, 0040, 0041, 0042, 0043) shall exist at canonical `adrs/` only; feature-scoped copies deleted.
- [ ] **AC-FR-8a-2 (CC)**: Where a duplicate is deduplicated under FR-8a, the system shall log the byte-equality verification step in the Plan's per-task execution result.
- [ ] **AC-FR-8b-1 (CC)**: When this feature ships, ADR-0024 (status-lift dedupe) shall exist at canonical `adrs/` only; the rejected body shall be archived to `adrs/superseded/<id>-feature-scoped-body.md` per OI-1 default. **Note**: for ADR-0024, per Discovery IN-002, only the frontmatter `status:` differs (Accepted vs Proposed); no body archival is required (no body content is lost). The PRD AC remains as a placeholder; the actual disposition is dedupe with status-precedence.
- [ ] **AC-FR-8b-1.1 (CC) — OI-1 fail-safe operationalization (per AA-014)**: Where Phase 2b processes ADR-0024 (status-lift case), the Plan task shall include a re-verification step (`diff` against canonical excluding the frontmatter `status:` field) prior to delete. If any non-frontmatter body line differs, the task shall halt and apply OI-1's `adrs/superseded/<id>-feature-scoped-body.md` archival default before proceeding. This closes the fail-safe gap surfaced by architecture-audit-r1: if Discovery's "status-lift only" claim is wrong and there IS a body diff, FR-8a's byte-equality re-check (Assumption A2) does not apply to ADR-0024 (A2 only covers byte-identical cases), so this AC provides the missing safety net.
- [ ] **AC-FR-8b-2 (CC)**: When ADR-0044 and ADR-0045 (numbering collisions, per ADR-0053 v1.0.1) are renumbered, the system shall present `original_id: ADR-0044` and `original_id: ADR-0045` provenance frontmatter on the renumbered canonical entries (ADR-0051, ADR-0052). Per ADR-0053 v1.0.1, the renumber baseline is `max(canonical IDs that pre-existed this feature's design-composer run) + 1` AFTER FR-8c relocations land (= 0050 + 1 = 0051), yielding ADR-0051 + ADR-0052. The 3 ADRs authored by this feature's design-composer (ADR-0053, ADR-0054, ADR-0055) are EXCLUDED from the renumber baseline (they were assigned via the same algorithm applied at design-composer authoring time, pre-renumber, in deterministic intra-run order).
- [ ] **AC-FR-8c-1 (CC)**: When this feature ships, ADR-0046 through ADR-0050 shall exist at canonical `adrs/` only; the feature-scoped originals shall have been relocated via `git mv` (preserving Git history).
- [ ] **AC-FR-8c-2 (CC)**: Where an ADR is relocated under FR-8c, the originating feature folder shall contain a `.tombstone` redirect note per Q-CC-2 / D6 Option C.
- [ ] **AC-FR-8d-1 (CC)**: When this feature ships, the `adrs-migrated/` directory shall be empty (removed); every final-variant file shall exist at canonical `adrs/` per ADR-0055's precedence rule; every `-pre-naming-convention`, `-pre-template-migration`, and `-v1-superseded` variant shall have been deleted (variant enumeration aligned with ADR-0055 v1.0.1 §Decision item 5 per I-AA-R2-004 cycle-2 fix; the v1-superseded variant scope is procedurally elaborated in AC-FR-8d-2.1).
- [ ] **AC-FR-8d-2 (CC)**: For each of the **7 archive-wins collisions (ADRs 0011–0017)** (per ADR-0055 v1.0.1; Discovery IN-004 surfaced 8 total collisions across IDs 0011-0018, of which 7 are archive-wins and 1 is canonical-wins), the system shall archive the stale canonical body to `adrs/superseded/<id>-pre-consolidation-canonical.md` per ADR-0055; the new canonical's frontmatter shall include `superseded_by_consolidation: true` and `superseded_canonical_archived_to: ...`.
- [ ] **AC-FR-8d-2.1 (CC) — ADR-0007 v1-superseded variant deletion (per AA-003)**: When Phase 2d processes the canonical-only case (ADR-0007), the system shall `git rm` not only the `-pre-*` variants but also the `adrs-migrated/ADR-0007-code-graph-mcp-selection-v1-superseded.md` variant (per ADR-0055 v1.0.1 canonical-only-procedure glob extension). Git history preserves the supersession event per NFR-5. Without this AC, the FR-10 validator would flag the stray ADR-0007-*.md in `adrs-migrated/` post-Phase-2d.
- [ ] **AC-FR-8d-3 (CC)**: When the FR-10 validator scans the post-feature repository, the system shall not allowlist `adrs-migrated/` (the directory no longer exists after FR-8d completes).

#### FR-9 (Cross-reference sweep) — Layer: Claude Code

- [ ] **AC-FR-9-a (CC)**: When this feature ships, no in-repository reference shall point to a relocated or deduplicated ADR at its former (feature-scoped or `adrs-migrated/`) path. A grep for the known former paths shall return zero matches (excluding redirect notes and audit trail).
- [ ] **AC-FR-9-b (CC) — REVISED in cycle 1 per user binding decision on AA-011**: The cross-reference sweep is **path-only for the 32 path-form references** (14 feature-scoped + 18 `adrs-migrated/` per IN-008); **AND additionally includes per-occurrence semantic disambiguation across all 368 bare-ID occurrences of `ADR-0044` (223 mentions) and `ADR-0045` (145 mentions)** in repo prose. For each bare-ID occurrence, the Plan task shall determine whether the prose refers to (a) the renumbered feature-scoped ADR (now ADR-0051 / ADR-0052) — in which case the bare-ID shall be updated — or (b) the canonical ADR with a different meaning (e.g., canonical ADR-0044 = `flatten-execution-dispatch-hierarchy`; canonical ADR-0045 = `subagent-agent-tool-grant-prohibition`) — in which case the bare-ID shall NOT be updated. This expansion was directed by the user at the architecture-audit-r1 reconciliation gate (2026-05-25) overriding the prior v1.0.0 "No Ripple Effect" assertion.
- [ ] **AC-FR-9-b.1 (CC) — Disambiguation procedure**: For each of the 368 bare-ID occurrences, the Plan executor shall:
  - (i) Read surrounding prose (≥3 lines of context) to determine semantic intent.
  - (ii) Apply the following baseline heuristic as a starting point (NOT an exemption from per-occurrence judgment): bare-ID references inside `working/feature/issue-capture-mechanism-r1/*` default to feature-meaning (renumber to ADR-0051 / ADR-0052); bare-ID references inside `adrs/ADR-0044-flatten-execution-dispatch-hierarchy.md` or `adrs/ADR-0045-subagent-agent-tool-grant-prohibition.md` default to canonical-meaning (no edit); bare-IDs in cross-feature Blueprint prose require explicit per-occurrence judgment.
  - (iii) Where ambiguous, surface to user via `AskUserQuestion` rather than guess.
  - (iv) Record the disposition per-occurrence in the Plan's per-task execution result (path, line, original ID, new ID or "preserved", rationale).
- [ ] **AC-FR-9-c (CC)**: The Phase 0 Discovery output shall include a cross-reference inventory enumerating every reference site by file and line; the Phase 3 sweep shall update every entry. (Satisfied by codebase-analysis.json IN-008.) **Cycle-1 expansion**: the IN-008 inventory's 32 path-form entries are joined by the 368 bare-ID enumeration for the renumbered IDs; the Plan stage owns producing the 368-entry inventory at the start of Phase 3 (via `grep -rn "ADR-0044\|ADR-0045"` against repo, minus the path-form entries already in IN-008).

#### FR-10 (Validator and three-surface enforcement) — Layer: Claude Code

- [ ] **AC-FR-10-a (CC)**: The system shall provide `validate_adr_placement.py` that scans the repository for `ADR-*.md` files and returns non-zero exit status if any are found outside canonical `adrs/` (and outside the hard-coded `adrs/superseded/` structural exception and the documented allowlist entries per AC-FR-10-f).
- [ ] **AC-FR-10-b (CC)**: When the feature pipeline orchestrator reaches Step 8 (Design Composition; per ADR-0054), the system shall invoke the validator between `design-composer` return and `shared-document-reviewer` invocation and shall block stage progression on non-zero exit.
- [ ] **AC-FR-10-c (CC)**: When the execution pipeline reaches `execute-phase-quality-reviewer` (which dispatches `run_phase_checks.py`), the system shall include `validate_adr_placement.py` in the parallel-dispatch set and shall fold findings into the existing `validator` dimension per Q-CC-7 / Option A; non-zero exit blocks phase progression.
- [ ] **AC-FR-10-d (CC)**: When `finalize-deliverable-packager` runs, the system shall invoke the validator (via the new narrow `Bash(python3 .claude/skills/auditing-shared/scripts/validate_adr_placement.py*)` grant) in place of the deleted dual-location BLOCKER and shall raise a BLOCKER finding on non-zero exit.
- [ ] **AC-FR-10-e (CC)**: Where a test fixture deliberately writes an `ADR-*.md` file to a feature-scoped path, the validator shall return non-zero and the corresponding gate(s) shall block.
- [ ] **AC-FR-10-f (CC)**: When the validator's allowlist is non-empty, the system shall enumerate every allowlist entry explicitly in this Blueprint with justification. (Satisfied below in §Design / Allowlist enumeration: one entry — `output/synthesis-*/adrs/` per Q-CC-4.)

#### FR-11 (Skill audit and remediation) — Layer: Claude Code

- [ ] **AC-FR-11-a (CC)**: When this feature ships, the audit log (this Blueprint §Design / Skill audit table) shall enumerate every skill reviewed and the disposition of each (8 file-level updates; 5 skill families confirmed CLEAN).
- [ ] **AC-FR-11-b (CC)**: Where a skill contains prose that could permit feature-scoped placement, the system shall update the skill so canonical-only is the only documented path.
- [ ] **AC-FR-11-c (CC)**: This Blueprint records the skill audit findings and remediation summary in §Design / Skill audit table.

#### CC-design-layer-specific ACs (from `cc-design.md` §7)

- [ ] **AC-CC-1 (Validator script structure)**: When `validate_adr_placement.py` is invoked with no args on the post-feature repository, the system shall return exit code 0 with `{"verdict": "PASS", "findings": []}` and `elapsed_ms < 5000`.
- [ ] **AC-CC-2 (Validator negative path)**: Where a test fixture writes `ADR-9999-fixture.md` to `working/feature/test-fixture/adrs/`, the system shall return exit code 2 with `verdict: BLOCK` and a `findings[]` entry citing the path and category `feature-scoped`.
- [ ] **AC-CC-3 (auditing-shared dispatch integration)**: When `run_phase_checks.py` is invoked after this feature ships, the system shall include `validate_adr_placement` in its dispatch set and fold findings into the `validator` dimension.
- [ ] **AC-CC-4 (Packager tool grant)**: The system shall list `Bash` in `.claude/agents/finalize-deliverable-packager.md` frontmatter `tools:` field, and `.claude/settings.json` shall contain a narrow allow-list entry permitting `python3 .claude/skills/auditing-shared/scripts/validate_adr_placement.py*`.
- [ ] **AC-CC-5 (Orchestrator gate integration)**: When `recipe-feature-pipeline/SKILL.md` Step 8 is read after this feature ships, the system shall describe the validator subprocess invocation between design-composer return and shared-document-reviewer invocation.
- [ ] **AC-CC-6 (No CLAUDE.md addition)**: When this feature ships, the system shall not add a CLAUDE.md entry, rule, output style, MCP server, or plugin (per KB-cc-design Principle 5 + Principle 1 + Principle 7).
- [ ] **AC-CC-7 (Skill audit completeness)**: When this Blueprint is read, the system shall enumerate the 8 file-level findings (each with disposition) and shall mark 5 skill families as confirmed-clean.

### Cross-Layer / Operational ACs

- [ ] **AC-OP-1 (CC)**: When a fresh feature-pipeline run completes after this feature ships and does not pass an explicit `output_adrs_dir` override, the system shall write any authored ADRs only to canonical-root `adrs/` and the packager shall PASS. Satisfies FR-1, FR-3, FR-4, FR-10 in composition.
- [ ] **AC-OP-2 (CC)**: When the four operator files are read after this feature ships, the system shall present a single internally-consistent ADR-placement convention (no file contradicts ADR-0036 or another).
- [ ] **AC-OP-3 (CC)**: When the FR-10 validator is invoked on the post-feature repository state, the system shall return zero exit status.
- [ ] **AC-OP-4 (CC)**: When a deliberate negative-path test writes an ADR to a feature-scoped path, all three enforcement surfaces shall block.
- [ ] **AC-OP-5 (CC)**: When the cross-reference sweep completes (Phase 3) and the Phase 0 inventory is re-run, the system shall report zero remaining references to former ADR paths.

### Non-Functional ACs

NFR-1 through NFR-8 per PRD §Non-Functional Requirements; reproduced verbatim is unnecessary here. The Plan must trace each NFR AC to a verifiable Phase-6 step.

## Existing Codebase Analysis

### Implementation Path Mapping

| Layer | Type | Path | Description |
|-------|------|------|-------------|
| Claude Code | Existing | `.claude/agents/finalize-deliverable-packager.md` | Packager sub-agent; FR-1 + FR-10-d targets at lines 56–63 + tools frontmatter |
| Claude Code | Existing | `.claude/agents/shared-document-reviewer.md` | Reviewer sub-agent; FR-2 target at line 349 |
| Claude Code | Existing | `.claude/agents/design-composer.md` | Composer sub-agent; FR-4 targets at lines 48, 129, 187 |
| Claude Code | Existing | `.claude/skills/recipe-feature-pipeline/SKILL.md` | Orchestrator skill; FR-3 + FR-10-b targets at line 273 + Step 8 area |
| Claude Code | Existing | `.claude/skills/auditing-shared/scripts/` | Canonical helper home (ADR-0031 / ADR-0035 / ADR-0042) |
| Claude Code | New | `.claude/skills/auditing-shared/scripts/validate_adr_placement.py` | FR-10 validator (Python stdlib only) |
| Claude Code | Existing | `.claude/skills/auditing-shared/scripts/run_phase_checks.py` | FR-10-c target at dispatch block lines 39–44 |
| Claude Code | Existing | `.claude/skills/auditing-shared/scripts/smoke_test_auditing_shared.py` | FR-10 verification target (smoke test extension) |
| Claude Code | Existing | `.claude/skills/KB-documentation-criteria/references/` | FR-11 targets (design-composition.md, deliverable-archive-spec.md, issue-register-template.md) |
| Claude Code | Existing | `.claude/skills/KB-issue-capture/SKILL.md` | FR-11 target at line 72 |
| Claude Code | Existing | `.claude/skills/capture-issue/SKILL.md` | FR-11 target at line 44 |
| Claude Code | Existing | `.claude/skills/synthesize/SKILL.md` | FR-11 review target at lines 22, 240 (per Q-CC-4 allowlist) |
| Claude Code | Existing | `adrs/` | Canonical ADR tree; destination for all migrations |
| Claude Code | New (created by feature) | `adrs/superseded/` | Archival destination for ADR-0024 (n/a; status-lift) and 7 stale canonical bodies (per ADR-0055 v1.0.1; cycle-1 AA-008 correction 8→7) |
| Claude Code | Existing → Deleted | `adrs-migrated/` | Legacy archive; consolidated per ADR-0055 and removed |
| Claude Code | Existing | `working/feature/*/adrs/` | 6 feature folders; sources for FR-8a/8b/8c migrations |
| Claude Code | New | `.claude/settings.json` `allow` entry | Narrow Bash grant for packager subprocess (per ADR-0054) |

### Integration Points (Include even for new implementations)

- **Integration Target 1 (FR-10-b)**: `recipe-feature-pipeline/SKILL.md` Step 8 — Orchestrator stage gate.
- **Integration Target 2 (FR-10-c)**: `run_phase_checks.py` parallel-dispatch set — Execution-pipeline hook.
- **Integration Target 3 (FR-10-d)**: `finalize-deliverable-packager.md` "### 3. ADR placement validator" section — Packager check.
- **Invocation Method**: All three via subprocess (`subprocess.run` with 120s timeout per ADR-0035) per ADR-0054's same-script-same-args commitment.

### Code Inspection Evidence

| File/Function | Relevance |
|---------------|-----------|
| `.claude/agents/finalize-deliverable-packager.md:56-63` | Retired dual-location BLOCKER prose (FR-1 target); pinned by IN-006 |
| `.claude/agents/shared-document-reviewer.md:349` vs `:470-472` | Internal contradiction (FR-2 target); pinned by IN-006 |
| `.claude/skills/recipe-feature-pipeline/SKILL.md:273` | Parameter list with no default (FR-3 target); pinned by IN-005 |
| `.claude/agents/design-composer.md:48, 129, 187` | Three `output_adrs_dir` mentions; pinned by IN-007 |
| `.claude/skills/auditing-shared/scripts/run_phase_checks.py:39-44, 59` | Dispatch + exit-code convention (FR-10-c integration); pinned by IN-009/IN-010 |
| `.claude/agents/execute-phase-quality-reviewer.md:18, 54` | Invokes `run_phase_checks.py`; transitive wiring for FR-10-c |
| `.claude/agents/execute-task-quality-handler.md:62-63` | Alternative FR-10-c surface (rejected per IN-009) |
| `adrs-migrated/` (47 files) | Source for FR-8d consolidation; collisions per IN-004 |
| `working/feature/issue-capture-mechanism-r1/adrs/ADR-0044, 0045` | Numbering collisions (per IN-002); resolved per ADR-0053 |
| `Issues/adr-placement-rootcause/proposal.md, analysis.md` | Originating proposal + companion analysis; the source of intent |

### Fact Disposition Table

One row per codebase-analysis `focusArea` / `information_needs` entry. This table is the binding between existing-behavior facts and the design.

| Fact ID | Focus Area | Disposition | Rationale | Evidence |
|---------|------------|-------------|-----------|----------|
| IN-001 | 12 byte-identical ADR pairs across 4 feature folders | preserve (canonical) + remove (feature-scoped) | FR-8a: dedupe per byte-equality re-verification at edit time | `codebase-analysis.json` IN-001; `diff -q` per ADR |
| IN-002 | ADR-0024 status-lift; ADR-0044/0045 numbering collisions | transform (ADR-0024 dedupe with status precedence; ADR-0044/0045 renumber per ADR-0053) | PRD FR-8b "divergent body" framing structurally inapplicable to numbering collisions; ADR-0053 codifies the renumber algorithm | `codebase-analysis.json` IN-002; diff confirms |
| IN-003 | adrs-migrated/ 47 files spanning IDs 0001–0018 | transform per ADR-0055 four sub-procedures (no-collision / archive-wins / canonical-wins / canonical-only) + remove (`-pre-*` variants); remove directory after consolidation | PRD FR-8d hypothesis ("0001–0010") corrected to 0001–0018 by Discovery; ADR-0055 codifies precedence rule | `codebase-analysis.json` IN-003 |
| IN-004 | 8 archive/canonical collisions (IDs 0011–0018) decomposing into 7 archive-wins (IDs 0011–0017, archive carries v2.0.0 current) + 1 canonical-wins (ID 0018) per ADR-0055 v1.0.1 | transform per ADR-0055 archive-wins (for 0011–0017) + canonical-wins (for 0018); archive 7 stale canonical bodies to `adrs/superseded/` | Binding user directive 2026-05-24; codified in ADR-0055 v1.0.1 (cycle-1 8→7 archive-wins correction per AA-008) | `codebase-analysis.json` IN-004 + Synthesis D2 |
| IN-005 | Orchestrator `output_adrs_dir` resolves implicitly today; no default specified at SKILL.md:273 | transform (codify canonical-root default per FR-3) | Originating defect: implicit default produces feature-scoped writes | `codebase-analysis.json` IN-005 |
| IN-006 | Operator file line ranges for retired BLOCKER + contradictory check + post-ADR-0036 statement | transform (delete + replace per FR-1, FR-2) | Pinned line ranges exact; no drift | `codebase-analysis.json` IN-006 |
| IN-007 | design-composer.md line ranges for `output_adrs_dir` mentions | transform (in-place edit per FR-4) | Pinned line ranges exact | `codebase-analysis.json` IN-007 |
| IN-008 | 14 path-form feature-scoped references + 18 `adrs-migrated/` path-form references | transform (path-only sweep per FR-9 using D5 Option B extended pattern set) | Per FR-9-b path-only; bare-ID exception for renumbered IDs per ADR-0053 | `codebase-analysis.json` IN-008 |
| IN-009 | Three FR-10 enforcement-surface integration points (orchestrator Step 8; run_phase_checks.py; packager :56–63) | transform (codify three-surface enforcement per ADR-0054) | Non-redundancy proof required per NFR-6 | `codebase-analysis.json` IN-009 |
| IN-010 | auditing-shared CLI shape + JSON + exit-code conventions | preserve (validator conforms) | Per ADR-0035 binding convention | `codebase-analysis.json` IN-010 |
| IN-011 | 8 skill-file findings clustered in 4 families; 5 families CLEAN | transform (8 file-level updates per FR-11) + preserve (5 families CLEAN) | Per Discovery's per-skill audit | `codebase-analysis.json` IN-011 |
| IN-012 | Per-skill disposition table | transform (8 update-with-fix + 1 no-change in deliverable-archive-spec.md) | No TBDs per AC-NFR-4-a | `codebase-analysis.json` IN-012 |

## Design

### Change Impact Map

```yaml
Change Target: ADR placement mechanism (cross-operator-file + cross-skill + validator)
Direct Impact:
  frontend: N/A
  backend: N/A
  api: N/A
  query: N/A
  database: N/A
  cicd: N/A
  iac: N/A
  codespaces: N/A
  cc:
    - .claude/agents/finalize-deliverable-packager.md (FR-1 + FR-10-d + tools list)
    - .claude/agents/shared-document-reviewer.md (FR-2)
    - .claude/agents/design-composer.md (FR-4; 3 anchor edits + new "Test override" subsection)
    - .claude/skills/recipe-feature-pipeline/SKILL.md (FR-3 + FR-10-b)
    - .claude/skills/auditing-shared/scripts/validate_adr_placement.py (NEW; FR-10-a)
    - .claude/skills/auditing-shared/scripts/run_phase_checks.py (FR-10-c)
    - .claude/skills/auditing-shared/scripts/smoke_test_auditing_shared.py (FR-10 verification)
    - .claude/skills/KB-documentation-criteria/references/disciplines/design-composition.md (FR-11)
    - .claude/skills/KB-documentation-criteria/references/deliverable-archive-spec.md (FR-11; remove stale clause)
    - .claude/skills/KB-documentation-criteria/references/templates/issue-register-template.md (FR-11; path-only refresh)
    - .claude/skills/KB-issue-capture/SKILL.md (FR-11; path-only refresh)
    - .claude/skills/capture-issue/SKILL.md (FR-11; path-only refresh)
    - .claude/skills/synthesize/SKILL.md (FR-11; review-with-disposition + validator allowlist entry)
    - .claude/settings.json (narrow Bash allow-list entry per ADR-0054)
    - adrs/ (FR-8a/b/c/d destination; 3 new ADRs ADR-0053/54/55; ADR-0051/52 from renumber; ADR-0046–0050 from relocation; 9 from archive consolidation no-collision adds; the 7 archive-wins cases overwrite existing canonical bodies, not net-add files)
    - adrs/superseded/ (NEW directory; 7 stale canonical bodies archived to superseded/ per ADR-0055 v1.0.1; cycle-1 AA-008 correction 8→7)
    - adrs-migrated/ (REMOVED after Phase 2d)
    - working/feature/{audit-machinery-fixes-r1, pipeline-skill-design-fixes-r1, audit-findings-remediation-r1, devcontainer-mcp-provisioning-r1}/adrs/ (FR-8a; deleted copies)
    - working/feature/frontend-design-knowledge-r1/adrs/ADR-0024-* (FR-8b status-lift dedupe; deleted)
    - working/feature/issue-capture-mechanism-r1/adrs/ (FR-8b renumber + FR-8c relocate; 5 .tombstone redirect notes left behind per ADR-0054-compatible Q-CC-2 default)
    - 32 cross-reference sites (FR-9; path-only edits)
Indirect Impact:
  - All future feature-pipeline runs (validator gates + canonical default)
  - All future execution-pipeline runs (validator at run_phase_checks)
  - devcontainer-mcp-provisioning-r1 Gate-6 PKG-BLOCKER-001 deferral closes
  - Authors of frontend-design-knowledge-r1 + issue-capture-mechanism-r1 are informed of divergent-body / renumber decisions
  - "368 bare-ID prose occurrences across the repo (ADR-0044: 223 mentions; ADR-0045: 145 mentions per IN-008) — per the cycle-1 AA-011 user binding decision (2026-05-25), each occurrence requires per-occurrence semantic disambiguation as part of FR-9 / Phase 3. This materially expands Phase 3 effort from the pre-cycle-1 32-edit estimate to 32 + 368 = 400 candidate sites (of which an unknown subset of the 368 will require actual edits depending on semantic intent)."
No Ripple Effect:
  - All non-CC layers (no Frontend, Backend, API, Query, Database, CI/CD, IaC, Codespaces touch)
  - The phantom-promotion misreading at devcontainer-mcp-provisioning-r1/blueprint-v2.md:1226 (out of scope per PRD §Won't Have)
  - "Note (cycle-1 revision): the prior v1.0.0 'No Ripple Effect' assertion that the 4000+ bare-ID prose references were out-of-scope is REMOVED. The user's binding decision on AA-011 made the 368-occurrence bare-ID sweep for the renumbered IDs (ADR-0044, ADR-0045) in-scope for Phase 3. The remaining bare-ID references to canonical ADRs whose IDs are not changing (e.g., ADR-0001-0043 retained, ADR-0046-0050 newly-relocated-but-same-ID) remain genuinely out-of-scope; only the 368 renumber-affected occurrences require sweep."
```

### Interface Change Matrix

| Existing | New | Conversion Required | Compatibility Method |
|----------|-----|--------------------|--------------------|
| `output_adrs_dir` (no default; implicit caller-supplied) | `output_adrs_dir` (default `"adrs/"` per ADR-0036) | No (parameter unchanged; default added) | Pass-through fidelity at orchestrator (AC-FR-3-b); explicit override honored (AC-FR-5-b) |
| Packager `### 3. ADR cross-location check` (dual-location BLOCKER prose) | Packager `### 3. ADR placement validator` (subprocess call to `validate_adr_placement.py`) | Yes — section name + body | Same `packager-report.json` schema (BLOCKER finding shape preserved per IN-009 / ADR-0054) |
| Reviewer line 349 (dual-location check) | (deleted; lines 470–472 are sole canonical convention) | Yes — deletion | Internal-consistency restored; no API change to downstream consumers |
| `recipe-feature-pipeline` Step 8 (design-composer → reviewer flow) | Step 8 (design-composer → validator gate → reviewer flow) | Yes — insertion | Existing reviewer invocation unchanged; new gate is pre-reviewer |
| `run_phase_checks.py` dispatch set (5 scripts) | dispatch set (6 scripts; +validate_adr_placement) | Yes — addition | Existing dimensions unchanged; new validator folds into `validator` dimension per Q-CC-7 |
| `working/feature/issue-capture-mechanism-r1/adrs/ADR-0044-per-issue-folder-model.md` | `adrs/ADR-0051-per-issue-folder-model.md` (renumber per ADR-0053) | Yes — `git mv` + frontmatter `original_id` | All references updated via FR-9 sweep (bare-ID exception per ADR-0053) |
| `working/feature/issue-capture-mechanism-r1/adrs/ADR-0045-three-doctypes-preserved.md` | `adrs/ADR-0052-three-doctypes-preserved.md` | Same as ADR-0044 | Same |
| 12 feature-scoped byte-identical ADRs | (deleted) | Yes — `git rm` | Canonical version's history is authoritative |
| `adrs-migrated/` (47 files) | (removed after Phase 2d) | Yes — per ADR-0055 four sub-procedures | Git history preserves `-pre-*` variants; stale canonical bodies archived to `adrs/superseded/` |
| `finalize-deliverable-packager.md` tools: `Read, Glob, Grep, Write, TaskCreate, TaskUpdate` | tools: `Read, Glob, Grep, Write, TaskCreate, TaskUpdate, Bash` | Yes — addition | `.claude/settings.json` narrow allow-list entry constrains the grant to the specific script path (per ADR-0054) |

### Architecture Overview

This feature spans a single layer (Claude Code / Project Filesystem) but touches four sub-categories of CC primitives:

```
                           ┌─────────────────────────────────────────┐
                           │  recipe-feature-pipeline (orchestrator) │
                           └─────────────┬───────────────────────────┘
                                         │
              ┌──────────────────────────┼──────────────────────────────┐
              │ Step 8 (Design Compose)  │ Step 14 (Packaging)          │
              ▼                          ▼                              │
   ┌──────────────────────┐  ┌─────────────────────────────────┐         │
   │ design-composer       │  │ finalize-deliverable-packager  │         │
   │ writes ADRs to        │  │ invokes validator (Bash grant)  │         │
   │ output_adrs_dir       │  │ folds findings → packager-report│         │
   │ (default: "adrs/"     │  └────────────────┬────────────────┘         │
   │  per ADR-0036)        │                   │                          │
   └───────┬───────────────┘                   │                          │
           │                                   │                          │
           ▼                                   ▼                          │
   ┌─────────────────────────────────────────────────────────────┐        │
   │ validate_adr_placement.py (FR-10 validator; auditing-shared) │◄──────┘
   │ scans for ADR-*.md outside adrs/ (with adrs/superseded/      │
   │ structural exception + Q-CC-4 synthesize allowlist)          │
   │ exit 0 = clean / exit 2 = block / JSON to stdout             │
   └─────────────────────────────────────────────────────────────┘
           ▲                                       ▲
           │                                       │ (subprocess; 120s timeout)
           │ Step 8 stage gate                     │ Per-phase
           │ (between composer & reviewer)         │
           │                                       │
   ┌───────┴───────────────┐         ┌─────────────┴─────────────────┐
   │ Orchestrator gate     │         │ run_phase_checks.py (exec     │
   │ (surface a; ADR-0054) │         │ pipeline; surface b; ADR-0044 │
   │                       │         │ flatten + ADR-0054 extension) │
   └───────────────────────┘         └───────────────────────────────┘

   ┌───────────────────────────────────────────────────────────────┐
   │ shared-document-reviewer (Gate 0/1 per ADR-0017; 5 invocations)│
   │ Post-FR-2: only canonical convention (lines 470-472) remains   │
   └───────────────────────────────────────────────────────────────┘

   Filesystem state (post-feature) — recomputed in cycle 1 per AA-001/AA-002 arithmetic correction:
     adrs/                — canonical (55 files: 36 pre-existing + 5 relocated (0046-0050) +
                            2 renumbered (0051,0052) + 3 new ADRs (0053,0054,0055) +
                            9 no-collision archive-adds (0001-0006, 0008-0010))
                            Note: 7 archive-wins (0011-0017) REPLACE existing canonical bodies; no net add.
                            Note: 1 canonical-only (0007) leaves canonical untouched; no add.
                            Note: 1 canonical-wins (0018) leaves canonical untouched; no add.
                            Total adds = 5+2+3+9 = 19; pre-existing 36; net = 55.
     adrs/superseded/     — 7 stale-canonical bodies (per ADR-0055 v1.0.1; not 8)
     adrs-migrated/       — REMOVED
     working/feature/**/adrs/ — empty (only .tombstone redirect notes per Q-CC-2)
```

### Data Flow

```
[User invokes pipeline]
        │
        ▼
[recipe-feature-pipeline Step 1..7]
        │
        ▼
[Step 8: Design Composition]
        │
        ├── design-composer authors ADR(s) → writes to output_adrs_dir (default: adrs/)
        │
        ├── validate_adr_placement.py invoked (subprocess; ADR-0054 surface a)
        │       │
        │       ├── exit 0 → continue
        │       └── exit 2 → halt stage; surface JSON findings via AskUserQuestion
        │
        ▼
[shared-document-reviewer (Gate 0/1; post-FR-2 single-convention prose)]
        │
        ▼
[Steps 9..13: Plan + Tests + Phase Validators]
        │
        ▼
[Phase execution: per-task]
        │
        ├── execute-task-code-producer writes artifacts
        ├── execute-task-quality-handler validates frontmatter
        ├── execute-phase-quality-reviewer dispatches run_phase_checks.py (ADR-0054 surface b)
        │       │
        │       ├── parallel dispatch: 5 existing scripts + validate_adr_placement.py
        │       └── rollup into 5-dimension verdict (validator dimension includes ADR-placement)
        │
        ▼
[Step 14: Deliverable Packaging]
        │
        ├── finalize-deliverable-packager invokes validate_adr_placement.py (ADR-0054 surface c; via narrow Bash grant)
        │       │
        │       ├── exit 0 → packager-report.json has no ADR-placement BLOCKER
        │       └── exit 2 → packager-report.json includes BLOCKER finding(s)
        │
        ▼
[Gate 6 (Final Approval)]
```

### Integration Points List

| Integration Point | Location | Old Implementation | New Implementation | Switching Method | Verification Method |
|-------------------|----------|-------------------|-------------------|------------------|-------------------|
| Orchestrator stage gate (FR-10-b) | `recipe-feature-pipeline/SKILL.md` Step 8 | (none) | Subprocess invocation of validate_adr_placement.py between composer return & reviewer invocation | Single-pass edit (Phase 1; ADR-0054 codifies pattern) | AC-CC-5; Phase 6 negative-path test |
| Execution-pipeline hook (FR-10-c) | `run_phase_checks.py` dispatch block (lines 39–44) | 5-script parallel dispatch | 6-script parallel dispatch (+validate_adr_placement); validator dimension extended | One-line addition + dimension rollup edit (Phase 5) | AC-CC-3; smoke test |
| Packager check (FR-10-d) | `finalize-deliverable-packager.md` lines 56–63 (post-FR-1 deletion) | Dual-location BLOCKER prose (8 lines) | Subprocess invocation via narrow Bash grant; JSON findings folded into packager-report.json | Section replacement (Phase 1; coordinated with Phase 4 validator authoring) | AC-FR-10-d; AC-CC-4 |
| `output_adrs_dir` default (FR-3) | `recipe-feature-pipeline/SKILL.md:273` | Bare parameter name; no default | Explicit `default: "adrs/" per ADR-0036` annotation | In-place line edit (Phase 1) | AC-FR-3-a |
| Design-composer parameter description (FR-4) | `design-composer.md:48, 129, 187` | Bare parameter mention | Default + ADR-0036 citation + test-override subsection | In-place edits (Phase 1) | AC-FR-4-a, AC-FR-4-b |

### Main Components

#### Component 1: `validate_adr_placement.py` (NEW)

- **Responsibility**: Scan repository for `ADR-*.md` files outside canonical `adrs/`; emit JSON findings; exit 0 = clean / 2 = block.
- **Interface**: CLI (positional `[scan_path]` default `.`; optional `--allowlist <comma-separated-paths>`). Output: JSON to stdout (`{"validator": "validate_adr_placement", "verdict": "PASS"|"BLOCK", "findings": [...], "scan_path": "...", "elapsed_ms": N}`).
- **Dependencies**: Python 3 stdlib only (`argparse`, `pathlib`, `json`, `sys`, `time`) per NFR-8.

#### Component 2: Three-surface enforcement integration (ADR-0054)

- **Responsibility**: Non-redundant, non-contradictory enforcement at orchestrator Step 8, execution-pipeline `run_phase_checks.py`, and packager Step 14.
- **Interface**: Subprocess invocation of `validate_adr_placement.py` with identical args + identical exit-code semantics + identical JSON shape across all three surfaces.
- **Dependencies**: `validate_adr_placement.py` (Component 1); existing `subprocess.run` patterns (per ADR-0035).

#### Component 3: Operator file post-edit consistency

- **Responsibility**: Four operator files express a single internally-consistent ADR-placement convention (per AC-US-2-b + AC-OP-2).
- **Interface**: Prose only (no API). Verified by reading the four files in sequence.
- **Dependencies**: ADR-0036 (the convention itself).

#### Component 4: Migration map (FR-8a/b/c/d) realized

- **Responsibility**: Move every off-canonical ADR to canonical `adrs/` (or delete duplicates); preserve `git mv` history; archive stale canonical bodies per ADR-0055.
- **Interface**: Filesystem state (post-feature: `adrs/` populated; `adrs/superseded/` populated; `adrs-migrated/` removed; `working/feature/**/adrs/` empty except `.tombstone` notes).
- **Dependencies**: ADR-0053 (renumber algorithm), ADR-0055 (archive-wins policy), git tooling.

#### Component 5: Cross-reference sweep (FR-9)

- **Responsibility**: Update 32 path-form references (14 feature-scoped + 18 archive) to canonical paths; update bare-ID references for renumbered ADRs (per ADR-0053).
- **Interface**: Filesystem state (post-feature: zero remaining references to former paths per AC-FR-9-a; zero remaining bare-ID references to old ADR-0044/0045 IDs in non-renumbered contexts).
- **Dependencies**: D5 Option B extended pattern set (per Synthesis D5).

#### Component 6: Skill audit + remediation (FR-11)

- **Responsibility**: 8 file-level updates per the audit table; 5 skill families confirmed CLEAN.
- **Interface**: Modified skill prose; no behavioral change beyond documentation alignment.
- **Dependencies**: None (prose edits only).

### Migration map (per-ADR; per ADR-0053 + ADR-0055)

Per AC-FR-6-a + AC-FR-6-b, this Blueprint enumerates every ADR currently outside canonical `adrs/` with classification + disposition.

#### FR-8a — Byte-identical dedupes (12 ADRs)

All 12 verified byte-identical per IN-001; disposition: delete feature-scoped copy.

| ADR | Current feature-scoped location | Disposition |
|---|---|---|
| ADR-0026 | `working/feature/audit-machinery-fixes-r1/adrs/` | delete copy; canonical retained |
| ADR-0028 | `working/feature/pipeline-skill-design-fixes-r1/adrs/` | delete copy; canonical retained |
| ADR-0029 | `working/feature/audit-findings-remediation-r1/adrs/` | delete copy |
| ADR-0030 | `working/feature/audit-findings-remediation-r1/adrs/` | delete copy |
| ADR-0031 | `working/feature/audit-findings-remediation-r1/adrs/` | delete copy |
| ADR-0037 | `working/feature/devcontainer-mcp-provisioning-r1/adrs/` | delete copy |
| ADR-0038 | `working/feature/devcontainer-mcp-provisioning-r1/adrs/` | delete copy |
| ADR-0039 | `working/feature/devcontainer-mcp-provisioning-r1/adrs/` | delete copy |
| ADR-0040 | `working/feature/devcontainer-mcp-provisioning-r1/adrs/` | delete copy |
| ADR-0041 | `working/feature/devcontainer-mcp-provisioning-r1/adrs/` | delete copy |
| ADR-0042 | `working/feature/devcontainer-mcp-provisioning-r1/adrs/` | delete copy |
| ADR-0043 | `working/feature/devcontainer-mcp-provisioning-r1/adrs/` | delete copy |

Per-ADR Plan task with byte-equality re-verification (per Assumption A2).

#### FR-8b — Status-lift dedupe (ADR-0024) + numbering-collision renumber (ADR-0044, ADR-0045 per ADR-0053)

| ADR | Classification | Disposition |
|---|---|---|
| ADR-0024 | status-lift (Accepted vs Proposed; body identical) | Delete feature-scoped copy in `working/feature/frontend-design-knowledge-r1/adrs/`; canonical (Accepted) retained. **No body archival** — no body content is lost. |
| ADR-0044 (feature) `per-issue-folder-model` | numbering-collision (canonical = `flatten-execution-dispatch-hierarchy`, different decision) | Per ADR-0053: renumber feature ADR to **ADR-0051** post-Phase-2d; `git mv` to `adrs/ADR-0051-per-issue-folder-model.md`; add `original_id: ADR-0044` frontmatter; update all references (path-form + bare-ID per ADR-0053 Implementation Guidance) |
| ADR-0045 (feature) `three-doctypes-preserved` | numbering-collision (canonical = `subagent-agent-tool-grant-prohibition`, different decision) | Per ADR-0053: renumber feature ADR to **ADR-0052** post-Phase-2d; `git mv`; add `original_id: ADR-0045`; update all references |

#### FR-8c — Feature-scoped relocations (5 ADRs: 0046–0050)

| ADR | Source | Destination | Redirect note (per Q-CC-2 / ADR-0054-compatible) |
|---|---|---|---|
| ADR-0046 | `working/feature/issue-capture-mechanism-r1/adrs/ADR-0046-add-new-sibling-file-evolution.md` | `adrs/ADR-0046-add-new-sibling-file-evolution.md` (git mv) | `working/feature/issue-capture-mechanism-r1/adrs/ADR-0046.tombstone` |
| ADR-0047 | `working/feature/issue-capture-mechanism-r1/adrs/ADR-0047-three-layer-enforcement.md` | `adrs/ADR-0047-three-layer-enforcement.md` | `ADR-0047.tombstone` |
| ADR-0048 | `working/feature/issue-capture-mechanism-r1/adrs/ADR-0048-prior-context-handoff.md` | `adrs/ADR-0048-prior-context-handoff.md` | `ADR-0048.tombstone` |
| ADR-0049 | `working/feature/issue-capture-mechanism-r1/adrs/ADR-0049-structural-vs-discipline-kb-split.md` | `adrs/ADR-0049-structural-vs-discipline-kb-split.md` | `ADR-0049.tombstone` |
| ADR-0050 | `working/feature/issue-capture-mechanism-r1/adrs/ADR-0050-5-state-issues-vocabulary.md` | `adrs/ADR-0050-5-state-issues-vocabulary.md` | `ADR-0050.tombstone` |

Tombstone format (per Q-CC-2 Option C): 3-line file:
```
# Moved

This ADR was relocated to canonical `adrs/ADR-NNNN-<slug>.md` on 2026-05-24
per feature `adr-placement-mechanism-repair-r1` (per ADR-0036).
```
The `.tombstone` extension is unambiguous, doesn't match the validator's `ADR-*.md` rglob pattern, and provides redirect traceability.

#### FR-8d — `adrs-migrated/` consolidation (47 files; per ADR-0055)

Four sub-procedures per ADR-0055 v1.0.1 (cycle-1 count corrections applied per AA-002, AA-008):

**(i) No-collision (9 IDs: 0001-0006, 0008-0010)** — `git mv` archive final-variant to canonical; delete `-pre-*` variants. (Cycle-1 correction per AA-002: range 0001-0010 inclusive is 10 IDs total; minus 0007 = 9. Prior v1.0.0 phrasing "10 IDs (0001-0010, excluding 0007)" was off-by-one.)

**(ii) Archive-wins collisions (7 IDs: 0011-0017)** — Per ADR-0055 v1.0.1 archive-wins procedure: (a) read canonical body; (b) write to `adrs/superseded/<id>-pre-consolidation-canonical.md` with provenance footer; (c) `git mv adrs-migrated/<id>-final*.md adrs/`; (d) add frontmatter fields `superseded_by_consolidation: true` + `superseded_canonical_archived_to: adrs/superseded/<id>-pre-consolidation-canonical.md`. Delete `-pre-*` variants. (Cycle-1 correction per AA-008: 7 archive-wins; Discovery IN-004 surfaced 8 TOTAL collisions, of which 7 are archive-wins and 1 is canonical-wins.)

**(iii) Canonical-wins (ID 0018)** — canonical retained (has ADR-0038 supersession marker); `git rm` archive final + `-pre-*` variants.

**(iv) Canonical-only (ID 0007)** — canonical untouched; `git rm` archive `-pre-*` variants **AND the `v1-superseded` variant** (per AA-003 / ADR-0055 v1.0.1 glob extension). The archive's ADR-0007-* file inventory per Discovery IN-003 includes 1 `v1-superseded` file (`adrs-migrated/ADR-0007-code-graph-mcp-selection-v1-superseded.md`) in addition to `-pre-naming-convention` and `-pre-template-migration` variants. Under literal v1.0.0 "-pre-* only" glob reading the executor would leave the v1-superseded file in place; the FR-10 validator would then flag the stray ADR-0007-*.md post-Phase-2d. The glob extension closes this gap.

After all four sub-procedures: `adrs-migrated/` is empty; `git rm -r adrs-migrated/`. Total variant deletions across all four sub-procedures: **30** (per Discovery IN-003: 18 `-pre-naming-convention` + 11 `-pre-template-migration` + 1 `v1-superseded`); prior v1.0.0 figure of "29 `-pre-*` variants" was off-by-one and is corrected.

### Three-surface enforcement non-redundancy proof (NFR-6 / per ADR-0054)

Per AC-NFR-6-a, the three surfaces' purposes are distinct and the same validator + same allowlist apply uniformly. Per AC-NFR-6-b, the Architecture Audit should confirm each catches a failure window the others cannot.

| Surface | Catches violations introduced by … | Time window | Failure-surfacing mechanism |
|---|---|---|---|
| (a) Orchestrator Step 8 gate (per ADR-0054) | `design-composer` writing ADRs to a wrong path (e.g., a regression to the pre-feature implicit-default behavior); per-author-time | After design-composer return, before reviewer invocation | `AskUserQuestion` with JSON findings |
| (b) Execution-pipeline `run_phase_checks.py` | `execute-task-code-producer` or other execution-phase writes; per-phase-runtime | During per-feature plan execution (every phase) | Roll into 5-dimensional verdict; `validator` dimension non-zero → phase blocks |
| (c) Packager Step 14 | Any artifact present in `working/feature/<slug>/` at finalize time that bypassed (a) and (b); last-line-of-defense | At finalize / Gate 6 | `packager-report.json` BLOCKER finding |

Each surface invokes `validate_adr_placement.py` with the same default args + same exit-code semantics + same JSON shape (per ADR-0054 commitment 1). The only inter-surface difference is the failure-surfacing mechanism — which is by design; each surface lives in its own context.

**Non-redundancy proof**: surface (a) catches the case where a designer regression silently re-introduces feature-scoped placement at author time, before any other artifact reads the ADR. Without (a), the violation persists until (b) runs the next phase, polluting the reviewer's input. Surface (b) catches the case where per-task code (not the designer) writes an ADR — e.g., a generated migration that authors an ADR as a side effect. Without (b), the violation persists until packaging. Surface (c) catches the case where an artifact was authored before any other surface was active (e.g., this feature's own execution per §Bootstrapping, where surfaces (a) and (b) are not yet wired during Phase 1–3).

### Allowlist enumeration (per AC-FR-10-f / ADR-0054)

Allowlist policy (post-Phase-2d):
- **Empty default**. No persistent config file. No persistent allowlist entry.
- **Structural-not-contingent exception**: `adrs/superseded/` is hard-coded into the validator algorithm (treated as part of canonical structure, not as an allowlist entry).
- **One contingent allowlist entry** (per Q-CC-4 / per ADR-0054 structural commitment 2): `output/synthesis-*/adrs/` (the synthesize skill's ADR-output target). Rationale: synthesize is a separate skill that produces synthesis-pass research artifacts, not pipeline-governance ADRs; the two spaces should remain separate. This entry is expressed via the per-invocation CLI flag at the `run_phase_checks.py` dispatch site (per ADR-0054 commitment 2: no persistent config file).

The packager and orchestrator surfaces do NOT pass an allowlist; only the `run_phase_checks.py` execution-pipeline surface passes the `--allowlist output/synthesis-*/adrs/` flag (because synthesize-skill ADRs land at that location during execution-pipeline runs). The orchestrator and packager surfaces operate on feature-pipeline artifacts only, where the synthesize allowlist does not apply.

### Skill audit table (FR-11 / per AC-CC-7)

Per AC-NFR-4-a, every skill in audit scope carries a disposition (no TBDs).

#### Skill families with file-level findings (4 families; 8 file updates total)

| Skill family | File | Line(s) | Disposition | Remediation |
|---|---|---|---|---|
| `recipe-feature-pipeline` | `SKILL.md` | 273 | update-with-fix (FR-3) | Annotate `output_adrs_dir` with `default: "adrs/" per ADR-0036`; document test-override prose |
| `KB-documentation-criteria` | `references/disciplines/design-composition.md` | 36 | update-with-fix | Replace `working/feature/<slug>/adrs/ADR-NNNN-<slug>.md` with `adrs/ADR-NNNN-<slug>.md per ADR-0036` |
| `KB-documentation-criteria` | `references/disciplines/design-composition.md` | 295 | update-with-fix | Same substitution as line 36 |
| `KB-documentation-criteria` | `references/deliverable-archive-spec.md` | 150 | update-with-fix | Remove the backward-compat clause (now stale post-Phase-2d); the validator's empty-allowlist post-condition makes the clause inconsistent |
| `KB-documentation-criteria` | `references/templates/issue-register-template.md` | 96, 99 | update-with-fix (path-only) | Rewrite example paths to canonical `adrs/ADR-NNNN-*` form (or generic `<slug>/<id>` placeholders) |
| `KB-issue-capture` | `SKILL.md` | 72 | update-with-fix (path-only) | Rewrite worked-example header to canonical-path-form examples |
| `capture-issue` | `SKILL.md` | 44 | update-with-fix (path-only) | Same pattern as `KB-issue-capture` |
| `synthesize` | `SKILL.md` | 22, 240 | review-with-disposition (per Q-CC-4 resolution: keep as-is; allowlist `output/synthesis-*/adrs/` per the validator) | No SKILL.md prose edit needed; allowlist entry in validator (see §Allowlist enumeration) |

#### Skill families confirmed CLEAN (no FR-11 finding; 5 families)

| Skill family | Reason for CLEAN |
|---|---|
| `KB-documentation-criteria/references/shared-conventions.md:302` | Already aligned with ADR-0036 (per IN-012) |
| `auditing-*` family (10 skills) | No prose mentions ADR placement |
| `KB-review-disciplines` | No matches |
| `KB-task-decomposition` | No matches |
| Per-layer KB-* design/platform skills + 6 synthesize-class knowledge skills | No matches |

### Data Representation Decision (NEW frontmatter fields)

| Criterion | Assessment | Reason |
|-----------|-----------|--------|
| Semantic Fit | Yes | `original_id` (per ADR-0053) and `superseded_by_consolidation` + `superseded_canonical_archived_to` (per ADR-0055) all express provenance / supersession state — natural extensions of the existing frontmatter convention |
| Responsibility Fit | Yes | Same bounded context (ADR frontmatter) |
| Lifecycle Fit | Yes | Set at consolidation time; never mutated thereafter |
| Boundary/Interop Cost | Low | Informational only; no current validator consumes the fields; future validator work can opt-in |

**Decision**: extend existing ADR frontmatter convention with three new fields (`original_id`, `superseded_by_consolidation`, `superseded_canonical_archived_to`) — per ADR-0053 + ADR-0055.

### Contract Definitions

#### `validate_adr_placement.py` CLI contract

```
USAGE: validate_adr_placement.py [scan_path] [--allowlist PATH,PATH,...]

POSITIONAL ARGS:
  scan_path  Repo root to scan (default: . per ADR-0027 cwd precondition)

FLAGS:
  --allowlist  Comma-separated paths to allowlist (default: empty)

OUTPUT (stdout, JSON):
  {
    "validator": "validate_adr_placement",
    "verdict": "PASS" | "BLOCK",
    "findings": [
      {
        "path": "working/feature/foo/adrs/ADR-9999-fixture.md",
        "category": "feature-scoped" | "legacy-archive" | "unexpected-location",
        "remediation_hint": "Move to adrs/<filename> per ADR-0036."
      },
      ...
    ],
    "scan_path": "<resolved-abs-path>",
    "elapsed_ms": <int>
  }

EXIT CODES:
  0  PASS (no findings)
  2  BLOCK (one or more findings)
  Other non-zero  Error (per ADR-0035)
```

### State Transitions and Invariants

This feature has no runtime state machine. The post-feature filesystem invariants are:

```yaml
System Invariants (post-feature):
  - "Every ADR-*.md file in the repo lives at adrs/ or adrs/superseded/"
  - "Zero files exist at working/feature/**/adrs/ (only .tombstone notes remain for relocated ADRs)"
  - "adrs-migrated/ directory does not exist"
  - "validate_adr_placement.py on the repo returns exit 0"
  - "The four operator files express one consistent ADR-placement convention"
  - "Cross-references in shipped Blueprints/Plans/Issues/README point to canonical adrs/ paths"
```

---

### Claude Code / Project Filesystem Design

This subsection integrates the per-layer `cc-design.md` essentially verbatim (the per-layer design is the load-bearing primitive-selection document). Cross-references to the cc-design.md sections preserved.

#### Conventions Touched (snapshot)

| Path | Purpose | Change Type |
|---|---|---|
| `.claude/agents/` | Sub-agent files | 3 modified (packager, reviewer, composer) |
| `.claude/skills/recipe-feature-pipeline/` | Orchestrator skill | modified (SKILL.md:273 + Step 8) |
| `.claude/skills/auditing-shared/scripts/` | Canonical helper home | 1 new script + 2 modified scripts |
| `.claude/skills/KB-documentation-criteria/` | Documentation criteria KB | 4 reference files modified |
| `.claude/skills/KB-issue-capture/` | Issue capture KB | 1 SKILL.md modified |
| `.claude/skills/capture-issue/` | Capture-issue skill | 1 SKILL.md modified |
| `.claude/skills/synthesize/` | Synthesize skill | review-with-disposition (no edit) |
| `.claude/settings.json` | Permission policy | new narrow allow-list entry |
| `adrs/` | Canonical ADR tree | populated (**55 files post-feature**, per cycle-1 arithmetic correction: 36 pre-existing + 5 relocated + 2 renumbered + 3 new + 9 no-collision-adds; 7 archive-wins REPLACE existing bodies and do not add files) + new `superseded/` subdirectory (7 stale-canonical bodies per ADR-0055 v1.0.1) |
| `adrs-migrated/` | Legacy archive | REMOVED |
| `working/feature/**/adrs/` | Feature-scoped ADR sources | emptied (only `.tombstone` notes remain) |

#### CLAUDE.md Updates

**None.** Per KB-cc-design Principle 5 (one-source-of-truth) and Principle 1 (lowest-cost primitive), the canonical-only ADR convention already lives in (a) ADR-0036 itself, (b) `KB-documentation-criteria/references/deliverable-archive-spec.md` post-amendment, (c) `KB-documentation-criteria/references/shared-conventions.md:302`. Adding a CLAUDE.md directive duplicates three existing sources and incurs token cost on every request. The validator (FR-10) is the enforcement mechanism; no advisory CLAUDE.md/rule needed.

#### Slash Commands

**None modified or introduced.**

#### Hooks (Claude Code lifecycle hooks)

**None.** The "execution-pipeline hook" surface per FR-10-c is the existing `run_phase_checks.py` subprocess hook (an orchestration-time check), NOT a Claude Code `settings.json` lifecycle hook. A `PostToolUse` hook would only fire on model edit-tool usage, missing orchestrator-side writes; would also pollute every CC session in the repo.

#### Skills

| Skill | Location | When Triggered | What It Provides |
|---|---|---|---|
| `auditing-shared` (modified) | `.claude/skills/auditing-shared/` | Subprocess-dispatched by family-coordinators + execution-pipeline | Now hosts `validate_adr_placement.py` (new script); `run_phase_checks.py` extended with new validator in parallel dispatch |
| `recipe-feature-pipeline` (modified) | `.claude/skills/recipe-feature-pipeline/SKILL.md` | User-invoked orchestrator | Step 8 now includes validator stage gate; parameter list cites ADR-0036 |
| `KB-documentation-criteria` (modified) | `.claude/skills/KB-documentation-criteria/references/` | Loaded by document-authoring sub-agents | 4 reference files updated (path examples + stale clause removed) |
| `KB-issue-capture` (modified) | `.claude/skills/KB-issue-capture/SKILL.md` | Loaded by issue-capture-author | Path examples refreshed |
| `capture-issue` (modified) | `.claude/skills/capture-issue/SKILL.md` | Model-invocable | Path examples refreshed |
| `synthesize` (review-only) | `.claude/skills/synthesize/SKILL.md` | User-invocable for synthesis runs | No edit; validator allowlists its `output/synthesis-*/adrs/` path |

#### Sub-Agents

| Sub-Agent | Location | Phase | What It Does |
|---|---|---|---|
| `finalize-deliverable-packager` (modified) | `.claude/agents/finalize-deliverable-packager.md` | Step 14 (finalize) | Subprocess-invokes validator (via new Bash grant); folds findings into packager-report.json |
| `shared-document-reviewer` (modified) | `.claude/agents/shared-document-reviewer.md` | 5 invocation points per ADR-0017 | Post-FR-2: only canonical-only convention in prose |
| `design-composer` (modified) | `.claude/agents/design-composer.md` | Step 8 (Design Composition) | `output_adrs_dir` description cites ADR-0036; documents test-override surface |

#### MCP Servers

**None.** Validator is pure Python stdlib.

#### File Naming & Layout Conventions Introduced

- **Tombstone redirect note**: `working/feature/<slug>/adrs/ADR-NNNN.tombstone` (3-line markdown body). Applies to: FR-8c relocated ADRs. Enforcement: convention only; FR-10 validator's `ADR-*.md` rglob does not match `.tombstone` extension (per Q-CC-2 / D6 Option C design).
- **Stale-canonical archival**: `adrs/superseded/<id>-pre-consolidation-canonical.md` with provenance footer. Applies to: ADR-0055 archive-wins cases. Enforcement: convention only; the validator's structural-not-contingent exception treats `adrs/superseded/` as part of canonical.

#### Project Filesystem Error State Design

- **Validator returns unexpected exit code (not 0 or 2)**: `run_phase_checks.py` treats non-zero non-2 as an `_error` finding (per IN-010 convention); the orchestrator and packager surface it the same way; no silent failure.
- **Validator subprocess timeout**: `subprocess.run` 120s timeout per ADR-0035; the validator's NFR-2 budget is 5s, so timeout is a hard error indicating bug or runaway scan.
- **Tombstone note missing post-FR-8c**: not a validator failure (`.tombstone` extension is invisible to the validator). Phase 6 verification checks the redirect-note presence for traceability.
- **`adrs/superseded/` directory missing or removed by future contributor**: validator's structural-not-contingent exception is hard-coded; absence of the directory is not a failure, but presence of `ADR-*.md` files in a non-canonical location whose parent is no longer `adrs/superseded/` would be flagged.

### Frontend Design

N/A — out of scope.

### Backend Design

N/A — out of scope.

### API Design

N/A — out of scope.

### Query & Data Access Design

N/A — out of scope.

### Database Schema & Migration Design

N/A — out of scope.

### CI/CD Design (GitHub Actions)

N/A — out of scope. Codebase analysis confirms no `.github/workflows/*.yml` currently invokes Claude Code or any auditing-shared script. The validator runs locally in Codespace and at three CC-internal surfaces; no CI integration is needed.

### Infrastructure as Code Design

N/A — out of scope.

### Dev Environment (Codespaces) Design

N/A — out of scope. The validator's NFR-2 5-second latency budget assumes a "typical Codespace" but does not require any Codespaces config change; existing devcontainer remains sufficient.

---

### Bootstrapping note (FR-3 pre-codification) — added in cycle 1 per AA-013

This sub-section was added in reconciliation cycle 1 to close a forward-traceability gap surfaced by architecture-audit-r1 (AA-013): the Blueprint did not document how this run's `design-composer` landed ADR-0053, ADR-0054, ADR-0055 at canonical `adrs/` during the run that is itself adding the FR-3 canonical-root default to `recipe-feature-pipeline/SKILL.md:273`. Without this note, a future incident-reviewer cannot diagnose whether the canonical landing in this run validates or undermines the FR-3 hypothesis.

**How the 3 new ADRs landed at canonical in this run**:

- The `design-composer` sub-agent that ran during Design Composition of this feature was invoked by the orchestrator with `output_adrs_dir` resolving to canonical `adrs/`. This was a deliberate operator-time decision in the orchestrator invocation (not the historical implicit default per IN-005, which "historically has resolved to `working/feature/<slug>/adrs/`"). The composer wrote ADR-0053/0054/0055 to canonical at authoring time.
- Filesystem verification at architecture-audit-r1 time confirmed the three ADRs sit at canonical `adrs/ADR-0053-*.md`, `adrs/ADR-0054-*.md`, `adrs/ADR-0055-*.md` (and in cycle 1 the v1.0.1 amendments land at the same paths in place per ADR-0005 frontmatter-stable convention).
- Critically, this means surfaces (a) and (b) of FR-10 (orchestrator stage gate, execution-pipeline `run_phase_checks.py`) are NOT YET WIRED at the time of this run's ADR authoring — they are landed by FR-10-b and FR-10-c, which are Phase 5 tasks. Only the FR-1-deleted dual-location BLOCKER (the failure mode) and the future post-FR-10 canonical-only behavior bracket the gap.

**Forward-traceability for FR-3 reliability**:

- After FR-3's codification at `recipe-feature-pipeline/SKILL.md:273` lands (Phase 1), the orchestrator's `output_adrs_dir` default becomes canonical `adrs/` for every future feature-pipeline run.
- Combined with FR-10-b (Phase 5 orchestrator-stage gate), any future regression of the implicit default to a feature-scoped path is caught at design-composer return time, before any reviewer or packager sees the misplaced ADR.
- This run's canonical landing for ADR-0053/0054/0055 was therefore a deliberate operator-time decision (not luck); the post-FR-3 mechanism makes the canonical landing the structural default for every future run regardless of operator awareness.

**For incident-reviewers**: if a post-feature feature-pipeline run produces feature-scoped ADRs, investigate (a) whether `recipe-feature-pipeline/SKILL.md:273` reverted; (b) whether `design-composer.md:48/129/187` reverted; (c) whether FR-10-b was bypassed at the orchestrator. The triad makes silent regression observable.

### Error Handling

| Error Category | Example | Detection | Recovery Strategy | User Impact |
|---------------|---------|-----------|-------------------|-------------|
| Validator violation (FR-10) | ADR found at `working/feature/foo/adrs/` | `validate_adr_placement.py` rglob scan + parent-dir check | Per surface: orchestrator halts stage; run_phase_checks rolls into validator dimension; packager raises BLOCKER. Remediation: move ADR to canonical `adrs/` and re-run. | Author sees JSON finding + remediation hint |
| Validator infrastructure (exception) | Python error in validator | `subprocess.run` captures non-zero non-2 exit | `run_phase_checks.py` treats as `_error` finding; orchestrator + packager surface as BLOCKER with error context | Author sees Python traceback in finding; bug to fix |
| Byte-equality re-check failure (FR-8a Assumption A2) | Feature-scoped copy diverged from canonical between Discovery and execution | Per-task `diff -q` re-verification before delete | Plan task halts; surface to user; re-discovery may be needed | Author re-runs Phase 0 inventory for the affected ADR |
| Numbering collision discovered post-Phase-2d (Assumption beyond Discovery) | Phase 2d introduces a previously-unseen collision | Validator's exit 2 on post-consolidation scan | Per ADR-0053: compute next-available ID + renumber + provenance frontmatter | Author updates Plan with additional renumber task |
| Cross-reference sweep false-negative (NFR-3) | Grep pattern set missed a reference form | Phase 6 verification re-runs extended pattern set | Iterate sweep with additional pattern | Author surfaces new pattern as Open Item; gate review |
| Skill audit miss (Assumption A5 fails) | Discovery missed a skill in scope | Manual review during Phase 5; potential validator finding if skill's example trips check | Add skill to audit + remediate; Architecture Audit catches | Author adds Phase 5 task |
| Tombstone note missing (post-FR-8c) | Phase 2c execution skipped a redirect | Phase 6 verification checks `.tombstone` presence per FR-8c-2 | Add missing tombstone | Author re-runs missing task |
| Three-surface contradiction (NFR-6 violation) | Orchestrator says PASS, packager says BLOCK on same input | Per ADR-0054 NFR-6 proof: cannot occur structurally (same script, same args, same exit-code semantics) | If observed → kill criterion for ADR-0054 (pattern broken; halt + re-design) | Architecture Audit flags as critical |

### Logging and Monitoring

- **Log events**: `validate_adr_placement.py` emits structured JSON to stdout (per ADR-0035). `elapsed_ms` is the latency observable. `findings[]` shape standardized.
- **Log levels**: N/A (validator is a CLI tool; output is JSON, not human-log).
- **Sensitive data**: None. File paths only.
- **Metrics**: `run_phase_checks.py` rolls the validator's verdict into its 5-dimension verdict; the `validator` dimension's verdict is the rollup metric.
- **Traces**: N/A.
- **Alerts**: BLOCKER findings at any of the three surfaces are surfaced via the respective surface's mechanism (orchestrator → `AskUserQuestion`; run_phase_checks → phase-validators output; packager → `packager-report.json`).
- **Dashboards**: N/A.

## Implementation Plan

### Implementation Approach

**Selected Approach**: 7-phase decomposition per the Intent Clarification's binding decomposition (carried into PRD §Rollout Plan).

**Selection Reason**: The scope expansion from MINOR to FULL forced multi-phase decomposition. The phases are dependency-ordered (Phase 0 → 1 → 2 → 3 → 4 → 5 → 6); within Phase 2, sub-phases 2a + 2c can run in parallel with 2d; 2b-renumber depends on 2d completion (per ADR-0053). The Plan author owns the per-task decomposition; this Blueprint names the high-level phase graph.

### Technical Dependencies and Implementation Order

#### Required Implementation Order

1. **Phase 0 — Discovery + Setup** (already complete per codebase-analysis.json)
   - Layer: Claude Code
   - Technical Reason: All subsequent phases depend on the migration map and cross-reference inventory
   - Dependent Elements: Phases 1–6

2. **Phase 1 — Operator file repairs (FR-1, FR-2, FR-3, FR-4, FR-5)**
   - Layer: Claude Code
   - Technical Reason: Operator file consistency is the load-bearing precondition for future pipeline runs; can run independently of Phase 2 migrations
   - Prerequisites: Phase 0 complete

3. **Phase 2 — Migration (FR-8a/b/c/d)**
   - Layer: Claude Code
   - Technical Reason: Phases 2a + 2c can run in parallel with 2d (independent ID spaces). 2b-renumber depends on 2d completion (per ADR-0053). 2b-status-lift dedupe (ADR-0024) is independent.
   - Prerequisites: Phase 1 (optional ordering — operator-file edits can happen in parallel, but Plan-task scheduling clarity favors Phase 1 first)

4. **Phase 3 — Cross-reference sweep (FR-9)**
   - Layer: Claude Code
   - Technical Reason: Paths to rewrite are known only post-Phase 2
   - Prerequisites: Phase 2 complete

5. **Phase 4 — Validator authoring (FR-10-a)**
   - Layer: Claude Code
   - Technical Reason: The validator's first repository-wide run should be clean (post-Phase 2 + 3); authoring + smoke testing before wiring (per Q-CC-6 Option B mid-migration policy)
   - Prerequisites: Phase 3 complete (so the validator's first run is clean)

6. **Phase 5 — Validator wiring + skill audit + remediation (FR-10-b/c/d, FR-11)**
   - Layer: Claude Code
   - Technical Reason: Surface wiring is a no-op-on-current-state edit (the validator's output on the post-Phase-3 repo is empty); skill audit is parallel to wiring
   - Prerequisites: Phase 4 complete

7. **Phase 6 — Verification (per AC-OP-N)**
   - Layer: Claude Code
   - Technical Reason: Empirical confirmation requires all prior phases complete
   - Prerequisites: Phases 0–5 complete

#### Cross-Layer Sequencing Notes

- **All within CC layer**: No cross-layer sequencing concerns.
- **Phase 4 before Phase 5 (within CC)**: The validator must exist before being wired at three surfaces.
- **Phase 2d before Phase 2b-renumber (within Phase 2)**: ADR-0053 next-available-ID algorithm requires post-consolidation canonical state.
- **Phase 2 before Phase 3 (within CC)**: Path-rewrite targets depend on completed migrations.
- **Phase 3 before Phase 4 first-run** (within CC): Validator's first scan should be clean.

### Migration Strategy

Per ADR-0055 (archive-wins consolidation) and ADR-0053 (renumber algorithm); see §Design / Migration map for the per-ADR table.

### Feature Flags & Rollout

N/A — no runtime feature flag. Activation is the act of merging the operator-file edits + validator wiring; the next feature-pipeline run is the first beneficiary.

## Security Considerations

### Cross-Cutting

- **Authentication & Authorization**: N/A — no new auth surface.
- **Input Validation**: The validator's only input is `scan_path` (filesystem path); `pathlib.Path` resolves it; no command injection surface.
- **Sensitive Data Handling**: None — file paths only.

### Claude Code Layer

- **Tool grant expansion (per ADR-0054)**: `finalize-deliverable-packager` gains `Bash` tool grant. The grant is narrowly scoped via `.claude/settings.json` allow-list entry: `Bash(python3 .claude/skills/auditing-shared/scripts/validate_adr_placement.py*)`. The narrow form is preferred over a broader pattern (per KB-cc-design Principle 6 permissions-as-safety-net specificity).
- **No new MCP server, no new permission `deny` rule needed**: the validator-based enforcement covers the canonical-only invariant; a `permissions.deny` would have to be over-scoped (the orchestrator writes many artifacts to `working/feature/<slug>/`; a deny on `working/feature/*/adrs/` is too broad).
- **No `--no-verify` git invocations** (NFR-7). If Discovery surfaces a need to bypass a pre-commit hook during execution, the orchestrator's `AskUserQuestion` escalation is the only sanctioned path.

### Frontend / Backend / API / Query / Database / CI/CD / IaC / Codespaces

N/A — out of scope.

## Test Boundaries

### Mock Boundary Decisions

| Component/Dependency | Mock? | Rationale |
|---------------------|-------|-----------|
| Filesystem (validator's `rglob` against repo) | No | The validator runs against the real repo; mocking would defeat the purpose |
| `subprocess.run` (orchestrator/packager invoking validator) | No (integration); Yes (smoke test units) | Phase 6 verification uses real subprocess; smoke tests may stub |
| Git (FR-8 `git mv` / `git rm` operations) | No | Operations against the real repo; rollback is `git reset` / `git checkout` |
| shared-document-reviewer outputs | No | Real reviewer invocations during Phase 6 verification |

### Data Layer Testing Strategy

- **Schema dependencies**: N/A (no database).
- **Test data approach**: Negative-path test fixture is a contrived `ADR-9999-fixture.md` written to `working/feature/test-fixture/adrs/` (per AC-CC-2). Positive path is the post-Phase-5 repo state.
- **Mock limitations acknowledged**: None apply.

### Per-Layer Test Strategy

| Layer | Test Type | Tooling | Location |
|-------|-----------|---------|----------|
| Claude Code | Unit (validator algorithm) | Python `unittest` or simple smoke | `.claude/skills/auditing-shared/scripts/smoke_test_auditing_shared.py` extension |
| Claude Code | Integration (three-surface wiring) | Phase 6 negative-path harness | `working/feature/test-fixture/` (transient) |
| Claude Code | Acceptance (AC-OP-1 through AC-OP-5) | Fresh feature-pipeline run | Phase 6 verification step |

### Integration Verification Points

- Validator at orchestrator Step 8 (AC-FR-10-b, AC-CC-5)
- Validator at run_phase_checks.py (AC-FR-10-c, AC-CC-3)
- Validator at packager Step 14 (AC-FR-10-d, AC-CC-4)
- Cross-reference sweep completeness (AC-FR-9-a, AC-OP-5)
- Migration completeness (AC-OP-3)

## Verification Strategy

### Correctness Proof Method

- **Correctness definition**: (i) Four operator files express one consistent ADR-placement convention; (ii) zero ADRs exist outside canonical `adrs/` (and `adrs/superseded/`); (iii) zero in-repository cross-references point to former (feature-scoped or `adrs-migrated/`) paths; (iv) FR-10 validator returns exit 0 on the post-feature repo; (v) negative-path test fixture blocks at all three surfaces.
- **Verification method**: Phase 6 verification harness — (a) read the four operator files in sequence; (b) run `validate_adr_placement.py` on the post-feature repo and confirm exit 0 + empty findings; (c) run the extended grep pattern set (per D5 Option B) and confirm zero matches for former paths; (d) write `ADR-9999-fixture.md` to a contrived feature-scoped path and confirm all three surfaces (orchestrator stage gate simulator, `run_phase_checks.py`, packager) return non-zero / BLOCKER.
- **Verification timing**: Phase 6 (after all migrations + sweep + validator wiring complete).

### Early Verification Point

- **First verification target**: The validator's first run against the post-Phase-3 repo (Phase 4 smoke test).
- **Success criteria**: Exit 0; empty `findings[]`; `elapsed_ms < 5000`.
- **Failure response**: Investigate the failing finding(s); if a legitimate non-canonical ADR remains (e.g., a Phase 2 task didn't complete), repair before proceeding to Phase 5.

### Output Comparison

- **Comparison input** (revised in cycle 1 per AA-001/AA-002 arithmetic correction): Pre-feature canonical `adrs/` (36 files); post-feature canonical `adrs/` (**55 files** = 36 pre-existing + 5 from FR-8c relocation (ADR-0046-0050) + 2 from FR-8b renumber (ADR-0051, ADR-0052) + 3 new ADRs authored this run (ADR-0053, ADR-0054, ADR-0055) + 9 from FR-8d no-collision-adds (ADR-0001-0006, 0008-0010); the 7 FR-8d archive-wins (ADR-0011-0017) REPLACE existing canonical bodies and do NOT add files; the 1 FR-8d canonical-wins (ADR-0018) and 1 canonical-only (ADR-0007) leave canonical untouched). Total adds = 5+2+3+9 = 19; pre-existing 36; net = **55**. Prior v1.0.0 figure of 51 conflated archive-wins replacements (which do not add files) with archive-adds (which do); v1.1.0 corrects the arithmetic.
- **Expected output fields**: Per-ADR frontmatter `id`, `version`, `original_id` (if renumbered per ADR-0053), `superseded_by_consolidation` (if archive-wins per ADR-0055), body content.
- **Diff method**: `git log --follow` per relocated/renumbered ADR confirms history preservation; `diff -q` per byte-identical dedupe confirms zero divergence; `diff -u` per archive-wins case confirms body is now archive's v2.0.0 body and `adrs/superseded/` carries the prior canonical body.

### Operational Verification

- **Pre-merge gates**: Reviewer Gate 0/1 (per ADR-0017); Architecture Audit on this Blueprint; Cross-Artifact Audit post-Plan; AC-OP-N verification at Phase 6.
- **Post-deploy verification**: First subsequent feature-pipeline run after this feature ships (per AC-US-4-a — orchestrator passes canonical-root by default).
- **Migration verification**: Per ADR Plan task verifies `git log --follow` traceability (NFR-5).
- **Rollback rehearsal**: Per FR-8 sub-phase rollback documented (Phase 0 inventory + git history are the substrate); not pre-staged in a separate environment.

## Future Extensibility

- **Extension points**:
  - **Validator allowlist mechanism (per ADR-0054)**: future enforcement-class validators can adopt the same per-invocation CLI flag pattern.
  - **`original_id` frontmatter field (per ADR-0053)**: future renumbering incidents follow the same provenance convention.
  - **`adrs/superseded/` directory (per ADR-0055)**: future archive consolidations write stale canonical bodies here with provenance footer.
  - **Three-surface enforcement pattern (per ADR-0054)**: future pipeline-governance validators (e.g., "validate-no-feature-scoped-blueprints") follow the same triad.
- **Known future requirements**: None identified at Blueprint authoring.
- **Intentional limitations**: Validator's allowlist is per-invocation (no persistent config) by design (per ADR-0054 commitment 2). If future scale forces a config-file allowlist, that's an ADR-0054 kill criterion.

## Alternative Solutions

### Alternative 1: Single-surface enforcement (packager only)

- **Overview**: Replace the FR-1-deleted prose with a single packager-side validator check; no orchestrator gate, no execution-pipeline integration.
- **Advantages**: Minimum integration effort.
- **Disadvantages**: Defeats the explicit user directive at the Intent Confirmation Gate ("enforcement gates and validates the correct location"). Single surface failed empirically (the originating PKG-BLOCKER-001 was itself a single declarative source-of-truth contradicting itself).
- **Reason for Rejection**: Per ADR-0054 § Options Considered Option 1; rejected.

### Alternative 2: Keep `adrs-migrated/` as-is; do not consolidate

- **Overview**: Honor the v1.1.0 default lean (interpretation (b)) — `adrs-migrated/` stays in place; validator allowlists it.
- **Advantages**: Smaller scope; no FR-8d sub-phase.
- **Disadvantages**: Defeats the gate-binding user directive 2026-05-24 (interpretation (a) selected). Leaves 7 archive-wins collisions silently stale in canonical (the 8th collision, ID 0018, is canonical-wins per ADR-0055 v1.0.1 and would not be affected; cycle-1 AA-008 correction 8→7).
- **Reason for Rejection**: Gate-binding directive supersedes; codified as ADR-0055.

### Alternative 3: Eliminate `output_adrs_dir` parameter entirely

- **Overview**: Hard-code canonical `adrs/` everywhere; no parameter.
- **Advantages**: Smallest possible parameter surface.
- **Disadvantages**: Breaks the ability to negative-path-test the FR-10 validator (no override mechanism for fixtures). Per Q1 binding resolution (PRD), the parameter is retained.
- **Reason for Rejection**: Q1 binding resolution.

## Risks and Mitigation

| Risk | Layer | Impact | Probability | Mitigation |
|------|-------|--------|-------------|------------|
| Hidden cross-reference form not caught by Phase 0 grep patterns (Assumption A3) | CC | Medium | Medium | D5 Option B extended pattern set; Phase 6 re-runs the pattern set on post-sweep repo; non-zero matches trigger sweep iteration. NFR-3 captures the invariant. |
| Divergent-body reconciliation (ADR-0024) picks the wrong canonical body | CC | High | Low | ADR-0024 is a status-lift dedupe per Discovery IN-002 (not a true divergent body); AC-FR-8b-1.1 fail-safe (added cycle 1 per AA-014) provides safety net: per-task re-verification via `diff` excluding frontmatter `status:` field; if non-frontmatter divergence detected, apply OI-1 archival default. ADR-0044/0045 are numbering collisions (not divergent bodies); renumber per ADR-0053 v1.0.1. |
| Archive-wins consolidation produces frontmatter inconsistency in 7 canonical ADRs (per ADR-0055 v1.0.1; not 8) | CC | Medium | Low | ADR-0055 v1.0.1 codifies `superseded_by_consolidation` + `superseded_canonical_archived_to` frontmatter fields with explicit semantics; affected count corrected from 8 → 7 in cycle 1 per AA-008. |
| Renumbering algorithm (ADR-0053) collides with concurrent ID assignments | CC | High | Low | Post-Phase-2d max-ID+1 deterministic; phase ordering (2d before 2b-renumber) prevents collision. ADR-0053 kill criterion documented. |
| `--no-verify` slips into Plan or execution artifact | CC | High | Low (NFR-7 explicit AC) | NFR-7 ACs; reviewer Gate 1 flags any `--no-verify`; escalation to user is the only sanctioned path. |
| Skill audit misses a skill in scope (Assumption A5 fails) | CC | Medium | Low (Discovery confirmed 5 families CLEAN + 4 with findings) | Phase 0 Discovery + Phase 5 audit table; Architecture Audit verifies completeness. |
| Three-surface enforcement turns out to be redundant rather than defensive | CC | Low (latency) | Medium | NFR-6 ACs + ADR-0054 NFR-6 non-redundancy proof; if Audit finds true redundancy, the Blueprint may collapse with explicit rationale. |
| Validator's allowlist policy changes (need for `adrs-migrated/` allowlist re-emerges if FR-8d incomplete) | CC | Medium | Low (AC-FR-8d-1 requires empty archive) | FR-10 AC-FR-10-f requires explicit allowlist enumeration; AC-FR-8d-3 confirms no allowlist needed post-Phase-2d. |
| Bootstrapping: this feature's own execution Phase 2 + 3 have non-canonical ADRs present | CC | N/A (expected) | Certain | Per Q-CC-6 Option B: validator wired at Phase 5 (after Phase 2 + 3 complete); Phase 4 = author script + smoke-test only; Phase 5 wiring is no-op-on-current-state. |
| `synthesize` skill's `output/synthesis-*/adrs/` allowlist entry drifts (re-introduced into wrong context) | CC | Low | Low | Per ADR-0054 commitment 2: per-invocation CLI flag (not persistent config); orchestrator + packager surfaces do NOT pass the flag; only `run_phase_checks.py` (where synthesize-skill artifacts land) passes it. |
| Tombstone redirect note format diverges across the 5 FR-8c relocations | CC | Low | Low | Blueprint specifies 3-line template; Plan tasks reference template; reviewer Gate 1 catches divergence. |
| Bare-ID 368-occurrence sweep (per AA-011 user binding decision; cycle-1 addition) materially inflates Phase 3 effort beyond the pre-cycle-1 32-edit estimate; per-occurrence semantic disambiguation has non-trivial cognitive load | CC | Medium (effort) | Certain (scope is now committed) | AC-FR-9-b.1 baseline-heuristic procedure (folder-distribution heuristic as starting point; per-occurrence judgment as the requirement; `AskUserQuestion` escalation for ambiguous cases); Plan stage authors per-occurrence inventory at start of Phase 3 via grep + IN-008 join; per-occurrence dispositions recorded in per-task execution result for audit. |
| Misdisambiguation of a bare-ID (incorrect feature-vs-canonical determination) leaves prose referring to wrong ADR | CC | Medium | Low | Per-occurrence rationale recorded in per-task execution result; reviewer Gate 1 spot-checks; ambiguous cases escalated via `AskUserQuestion` rather than guessed. Plan stage may benefit from automated detection of high-confidence cases (path-based heuristic) and surfacing low-confidence cases to user. |

## References

- **PRD**: `working/feature/adr-placement-mechanism-repair-r1/prd-v1.md` (v1.0.2).
- **Intent Clarification**: `working/feature/adr-placement-mechanism-repair-r1/intent-clarification.md` (v2.0.1).
- **Research Plan**: `working/feature/adr-placement-mechanism-repair-r1/research-plan.md` (v1.0.0).
- **Synthesis**: `working/feature/adr-placement-mechanism-repair-r1/synthesis.md` (v1.0.0).
- **Codebase Analysis**: `working/feature/adr-placement-mechanism-repair-r1/codebase-analysis.json` (schema v1.1.0).
- **Per-layer Design (CC)**: `working/feature/adr-placement-mechanism-repair-r1/cc-design.md` (v1.0.0).
- **Per-layer Dependencies (CC)**: `working/feature/adr-placement-mechanism-repair-r1/cc-dependencies.json`.
- **Originating proposal**: `Issues/adr-placement-rootcause/proposal.md` (status `adopted`).
- **Companion analysis**: `Issues/adr-placement-rootcause/analysis.md`.
- **Load-bearing ADR**: `adrs/ADR-0036-single-location-adr-placement.md`.
- **ADRs authored in this run** (amended to v1.0.1 in cycle 1; frontmatter-stable per ADR-0005): `adrs/ADR-0053-adr-renumbering-collision-resolution-algorithm.md` (v1.0.1); `adrs/ADR-0054-canonical-helper-three-surface-enforcement-pattern.md` (v1.0.1); `adrs/ADR-0055-archive-wins-consolidation-policy-for-version-divergent-collisions.md` (v1.0.1).
- **Architecture Audit cycle 1**: `working/feature/adr-placement-mechanism-repair-r1/architecture-audit-issues.json`; reconciler dispatch: `working/feature/adr-placement-mechanism-repair-r1/dispatch-r1.json`; reconciliation log: `working/feature/adr-placement-mechanism-repair-r1/reconciliation-log-r1.md`.
- **Inherited ADRs**: ADR-0005, ADR-0017, ADR-0019, ADR-0027, ADR-0031, ADR-0035, ADR-0042, ADR-0044.
- **Empirical failure mode**: `devcontainer-mcp-provisioning-r1` Gate-6 PKG-BLOCKER-001.
- **Counter-demonstration**: `execute-orchestrator-dispatch-mechanism-repair-r1` Gate-7 ratification.

### Q-CC-N arbitration outcomes

| Q-ID | Disposition | Chosen option | ADR authored? | Rationale |
|---|---|---|---|---|
| Q-CC-1 | resolved | C (post-Phase-2d max-ID+1; provenance frontmatter); algorithm baseline clarified in ADR-0053 v1.0.1 (cycle 1) to EXCLUDE this-feature's design-composer authoring | **Yes — ADR-0053 v1.0.1** | Algorithm + provenance convention; warrants ADR for future-collision precedent; cycle-1 amendment per AA-006 |
| Q-CC-2 | resolved | C (`.tombstone` non-`.md` extension) | No | Design ratification at Blueprint Approval Gate suffices; pattern documented in §Migration map / FR-8c |
| Q-CC-3 | resolved | A (per-invocation CLI flag; empty default) | No (folded into ADR-0054 commitment 2) | Codified as structural commitment in ADR-0054 |
| Q-CC-4 | resolved | A (validator allowlists `output/synthesis-*/adrs/` per CLI flag at run_phase_checks.py dispatch) | No (folded into ADR-0054 + Blueprint allowlist enumeration) | One explicit allowlist entry; documented in §Allowlist enumeration |
| Q-CC-5 | resolved | A (add narrowly-scoped `Bash` to packager + matching `.claude/settings.json` allow-list) | No (folded into ADR-0054 commitment 3) | Smallest-grant principle; Bash grant + narrow allow-list |
| Q-CC-6 | resolved | B (wire validator at Phase 5, after Phase 2 + 3 complete) | No | Plan sequencing; bootstrapping note in §Risks |
| Q-CC-7 | resolved | A (fold into existing `validator` dimension) | No (folded into ADR-0054 commitment 4) | Dimension count stable; folded validators dimension consistent |

### Unresolved items deferred to user (Blueprint Approval Gate)

**None remain unresolved as of cycle 1.** All 7 Q-CC-N items have evidence-based dispositions ratified in this Blueprint or codified into ADR-0053/0054/0055 (each amended to v1.0.1 in cycle 1). The 5 PRD Open Items resolved:

- **OI-1** (divergent-body archival format) — resolved at design level; ADR-0024 is a status-lift dedupe (no body archival needed); cycle-1 AC-FR-8b-1.1 operationalizes the OI-1 fail-safe: per-task `diff` re-verification excluding frontmatter `status:` field; if non-frontmatter body line differs, halt and apply the `adrs/superseded/<id>-feature-scoped-body.md` archival default. Closes AA-014.
- **OI-2** (gate-resolved earlier; `adrs-migrated/` consolidation per ADR-0055 v1.0.1; counts corrected in cycle 1).
- **OI-3** (validator implementation surface) — resolved Option A (Python script under `auditing-shared/scripts/`); codified in ADR-0054 v1.0.1.
- **OI-4** (cross-reference inventory completeness) — resolved Option B (extended pattern set per Synthesis D5); cycle 1 expanded scope per AA-011 (368 bare-ID occurrences in-scope).
- **OI-5** (redirect-note format) — resolved Option C (`.tombstone` non-`.md` extension per Q-CC-2).

### Cycle-1 issue dispositions (Y/N + brief note)

Per the audit + reconciler dispatch:

| Issue ID | Severity | Resolved? | How |
|---|---|---|---|
| AA-001 | MAJOR | Y | 51 → 55 corrected at all 3 sites (Architecture Overview ASCII, Conventions Touched table, Output Comparison) |
| AA-002 | MAJOR | Y | "10 IDs (0001-0010 excluding 0007)" → "9 IDs (0001-0006, 0008-0010)" at Migration map FR-8d sub-procedure (i); ADR-0055 v1.0.1 corrects in source ADR |
| AA-003 | MAJOR | Y | ADR-0007 v1-superseded variant deletion added to Migration map FR-8d sub-procedure (iv); new AC-FR-8d-2.1; ADR-0055 v1.0.1 extends canonical-only-procedure glob |
| AA-006 | MAJOR | Y | ADR-0053 v1.0.1 clarifies algorithm baseline (Option a per dispatch); Blueprint AC-FR-8b-2 reaffirms 0051/0052 targets with v1.0.1 cross-reference |
| AA-008 | MAJOR | Y | "8 archive-wins (ADRs 0011-0017)" → "7 archive-wins (ADRs 0011-0017)" at AC-FR-8d-2, Migration map sub-procedure (ii), Risks table, biggest_risks; ADR-0055 v1.0.1 corrects in source ADR |
| AA-011 | MAJOR (BLOCKING) | Y | Full 368-occurrence bare-ID sweep added to FR-9 per user binding decision (2026-05-25); AC-FR-9-b revised; new AC-FR-9-b.1 disambiguation procedure; Change Impact Map "No Ripple Effect" assertion removed; new Risks-table rows; ADR-0053 v1.0.1 Implementation Guidance cross-references the user binding decision |
| AA-014 | MAJOR | Y | New AC-FR-8b-1.1 operationalizes OI-1 fail-safe: per-task `diff` excluding `status:` field; if divergent, apply archival default |
| AA-004 | MINOR | Y | biggest_risks ADR-0024 entry reframed per the dispatch-suggested rephrase |
| AA-005 | MINOR | N (deferred) | Auditor self-reported as VERIFIED PASS; no remediation needed |
| AA-007 | MINOR | Y | ADR-0054 v1.0.1 commitment 1 "same args" → "same default args; allowlist content per-surface contextual" |
| AA-009 | MINOR | N (deferred) | Auditor self-reported as PASS for ADR-0029/0033 adjacency |
| AA-010 | MINOR | N (deferred) | Auditor self-reported as PASS for ADR-0042 consumer-extension adjacency |
| AA-012 | MINOR | Y | "47 archive consolidation actions" → "47 source files in adrs-migrated/ touched by Phase 2d"; "29 -pre-* variants" → "30 variant deletions" |
| AA-013 | MINOR | Y | New Bootstrapping Note sub-section added documenting how ADR-0053/0054/0055 landed at canonical in this run + forward-traceability for FR-3 reliability |
| AA-015 | MINOR | Y | ADR-0054 v1.0.1 commitment 2 distinguishes steady-state allowlist usage (hard-coded dispatch site) from mid-migration usage (ephemeral) |

### Cycle-1 new Open Items (if any)

**None.** All 7 design-stage MAJORs and 8 MINORs resolved in this cycle. The 3 deferrals (AA-005, AA-009, AA-010) are auditor-self-recorded PASS entries with no remediation required.

The Plan stage receives the corrected Blueprint v1.1 + corrected ADRs v1.0.1 as input; per FR-9-b.1 the Plan stage owns producing the 368-entry bare-ID inventory at the start of Phase 3 and per-occurrence disambiguation thereafter.

### Cycle-2 issue dispositions (Y/N + brief note)

Per architecture-audit-r2 (focused delta re-audit; 4 propagation-gap findings; no architectural regressions; all Blueprint-only fixes — no ADR changes in cycle 2):

| Issue ID | Severity | Resolved? | How |
|---|---|---|---|
| I-AA-R2-001 | MAJOR | Y | 3 sites updated to "7 archive-wins" / "7 stale canonical bodies": (a) Fact Disposition Table IN-004 row reworded to "8 collisions decomposing into 7 archive-wins (0011-0017) + 1 canonical-wins (0018)"; (b) Change Impact Map `adrs/superseded/` line "8 stale canonical bodies" → "7 stale canonical bodies archived to superseded/ per ADR-0055 v1.0.1"; (c) Alternative 2 disadvantage prose "Leaves 8 archive-wins collisions" → "Leaves 7 archive-wins collisions silently stale (the 8th, ID 0018, is canonical-wins)". |
| I-AA-R2-002 | MINOR | Y | Change Impact Map `adrs/` line: "17 from archive consolidation" replaced with "9 from archive consolidation no-collision adds; the 7 archive-wins cases overwrite existing canonical bodies, not net-add files" — aligns with load-bearing 55-file arithmetic in Architecture Overview + Conventions Touched + Output Comparison. |
| I-AA-R2-003 | MINOR | Y | Agreement Checklist 47→48-ops row appended: "(47 source files → 48 operations because each of the 7 archive-wins cases is one `mv` + one canonical-body archive, so those 7 sources double-count once)". |
| I-AA-R2-004 | MINOR | Y | AC-FR-8d-1 variant-deletion enumeration broadened: "every `-pre-naming-convention`, `-pre-template-migration`, and `-v1-superseded` variant shall have been deleted" — aligned with ADR-0055 v1.0.1 §Decision item 5. AC-FR-8d-2.1 retained as procedural detail (canonical-only-procedure glob extension). |

### Cycle-2 new Open Items (if any)

**None.** Cycle 2 was a tightly-scoped propagation-gap cleanup; all 4 findings closed in one composer pass. Per the auditor's convergence assessment, trajectory is "converging"; 2 cycles remain in the ADR-0017 four-cycle cap; cycle-3 risk is low absent further user-scope expansion.

The Plan stage receives the cleaned-up Blueprint v1.2 + corrected ADRs v1.0.1 as input; per FR-9-b.1 the Plan stage owns producing the 368-entry bare-ID inventory at the start of Phase 3 and per-occurrence disambiguation thereafter.

## Update History

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2026-05-24 | 1.0.0 | Initial Blueprint composed from per-layer cc-design.md + cross-cutting sections. ADRs ADR-0053, ADR-0054, ADR-0055 authored in this run. All 7 Q-CC-N items arbitrated; all 5 PRD Open Items resolved. | design-composer |
| 2026-05-25 | 1.1.0 | Reconciliation cycle 1 (responding to architecture-audit-r1; 7 MAJOR / 8 MINOR issues; 1 user escalation AA-011 resolved by user binding decision = full sweep). MAJOR resolutions: AA-001+AA-002 arithmetic corrections (51 → 55 post-feature canonical file count at three sites; 10 no-collision → 9; 8 archive-wins → 7 per AA-008); AA-003 ADR-0007 v1-superseded variant deletion AC added; AA-006 ADR-0053 self-referential ordering bug clarified (algorithm baseline = max canonical IDs pre-existing THIS feature's design-composer run; AC-FR-8b-2 reaffirms 0051/0052 targets); AA-011 full 368-occurrence bare-ID sweep added to FR-9 scope per user binding decision (overrides v1.0.0 "No Ripple Effect" assertion); AA-014 OI-1 fail-safe operationalized via new AC-FR-8b-1.1. MINOR resolutions: AA-004 biggest_risks reframed; AA-007+AA-015 ADR-0054 commitment 1+2 prose refined; AA-012 "actions" vs "source files" disambiguated; AA-013 Bootstrapping Note added documenting how this run's design-composer landed ADR-0053/0054/0055 at canonical. Three ADR amendments authored at v1.0.1 (frontmatter-stable per ADR-0005): ADR-0053, ADR-0054, ADR-0055. | design-composer |
| 2026-05-25 | 1.2.0 | Reconciliation cycle 2 (responding to architecture-audit-r2; 4 propagation-gap fixes, all Blueprint-only — no ADR changes). I-AA-R2-001 MAJOR: 3 stragglers of the cycle-1 8→7 archive-wins correction fixed at Fact Disposition Table IN-004 row, Change Impact Map `adrs/superseded/` line, and Alternative 2 disadvantage prose. I-AA-R2-002 MINOR: Change Impact Map `adrs/` line "17 from archive consolidation" corrected to "9 no-collision adds + 7 archive-wins that overwrite (do not net-add)". I-AA-R2-003 MINOR: Agreement Checklist 47→48 arithmetic clarified with one-line explanation of the archive-wins double-count. I-AA-R2-004 MINOR: AC-FR-8d-1 variant enumeration broadened to include `-v1-superseded` to match ADR-0055 v1.0.1 §Decision item 5. ADRs ADR-0053/0054/0055 remain at v1.0.1 unchanged. | design-composer |
