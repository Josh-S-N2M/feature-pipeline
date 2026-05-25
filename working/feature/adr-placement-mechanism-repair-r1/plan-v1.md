---
id: Plan-adr-placement-mechanism-repair-r1
version: 1.0.1
status: draft
doc_type: plan
feature_slug: adr-placement-mechanism-repair-r1
scope_class: FULL
layer_scope: ["claude-code"]
derived_from: working/feature/adr-placement-mechanism-repair-r1/blueprint-v1.md
prd_version: 1.0.2
blueprint_version: 1.2.0
intent_clarification_version: 2.0.1
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
  - ADR-0053
  - ADR-0054
  - ADR-0055
phases: 8
total_tasks: 40
generated: 2026-05-25T01:30:00Z
generated_by: plan-author
---

# Plan: ADR Placement Mechanism Repair (adr-placement-mechanism-repair-r1)

## Contents

Section completion checklist — each box must be checked (including `N/A — out of scope` rows) before this document leaves draft. The reviewer's Gate 0 check uses this list as the structural-presence anchor.

- [x] Purpose
- [x] Source
- [x] Phase 0 — Discovery + Setup (carry-over formalization)
- [x] Phase 1 — Operator-file repairs (FR-1 through FR-5)
- [x] Phase 2 — Migration (FR-8a/b/c/d)
- [x] Phase 3 — Cross-reference sweep (FR-9)
- [x] Phase 4 — Validator authoring + smoke test (FR-10-a)
- [x] Phase 5 — Validator wiring + skill audit + remediation (FR-10-b/c/d, FR-11)
- [x] Phase 6 — Verification (AC-OP-N)
- [x] Rollout — Closeout + deferral closure
- [x] Cross-Phase Dependencies
- [x] L1/L2/L3 Verification Discipline
- [x] Acceptance Test Cross-Reference
- [x] Estimation Methodology
- [x] Resourcing Posture
- [x] Open Items (Pending Cross-Artifact Audit)
- [x] Update History

## Purpose

This is the executable decomposition of `blueprint-v1.md` (v1.2.0, Architecture-Audit-PASS) into 7 internal phases plus a Rollout sub-phase, each with concrete tasks carrying L1/L2/L3 verification. The Plan is sequenced by Blueprint §Implementation Plan; it does NOT re-design. Where the Blueprint defines a behavior (e.g., the `.tombstone` redirect format, the validator's JSON shape, the archive-wins frontmatter convention, the disambiguation procedure for 368 bare-ID occurrences), this Plan references the Blueprint and decomposes the work into executable tasks; it does not invent new behavior.

The Plan covers all 11 PRD Functional Requirements (FR-1 through FR-11, with FR-7 SUPERSEDED to FR-10), all 8 PRD Non-Functional Requirements (NFR-1 through NFR-8), 7 CC-design-layer-specific ACs (AC-CC-1 through AC-CC-7), and 5 cross-layer/operational ACs (AC-OP-1 through AC-OP-5).

## Source

- **Blueprint**: `working/feature/adr-placement-mechanism-repair-r1/blueprint-v1.md` (v1.2.0, post-Architecture-Audit-r2 PASS, 2026-05-25).
- **PRD**: `working/feature/adr-placement-mechanism-repair-r1/prd-v1.md` (v1.0.2).
- **ADRs authored in this run** (consumed as design constraints, NOT as Plan deliverables — they were already authored in design-composer at canonical `adrs/`): ADR-0053 v1.0.1 (renumber algorithm), ADR-0054 v1.0.1 (three-surface enforcement), ADR-0055 v1.0.1 (archive-wins consolidation).
- **Phase taxonomy used**: Phase 0 (Discovery+Setup carry-over) → Phase 1 (operator-file repairs) → Phase 2 (migration; 4 sub-phases 2a/2b/2c/2d) → Phase 3 (cross-reference sweep, including 368-occurrence bare-ID disambiguation per AA-011 user binding decision) → Phase 4 (validator authoring + smoke) → Phase 5 (3-surface wiring + skill audit) → Phase 6 (verification) → Rollout (closeout + Gate-6 deferral closure).
- **Phase sequencing rationale** (per Blueprint §Implementation Plan / Q-CC-6): Phase 4 (validator authoring) is intentionally sequenced AFTER Phase 3 (cross-reference sweep) so the validator's first-ever run on the repository is clean. Phase 5 wiring is then no-op-on-current-state, eliminating bootstrap-loop concerns documented in Blueprint §Bootstrapping note.

## Phase 0 — Discovery + Setup (carry-over formalization)

### Goal

Formalize the Discovery + Setup work already completed by `discovery-codebase-researcher` and `design-composer` (codebase-analysis.json v1.1.0 schema; Blueprint v1.2.0; ADRs 0053/0054/0055 v1.0.1) as Phase 0 inputs to downstream phases. No new discovery work is authored here; this Phase records the discovery substrate and confirms it is available.

### Tasks

#### T0.1: Confirm migration map inputs are loadable

- **Layer:** Claude Code
- **Description:** Read `codebase-analysis.json` IN-001 through IN-012; confirm each row's data is loadable for downstream phases. Confirm `blueprint-v1.md` §Migration map enumerates every off-canonical ADR with disposition. Confirm `adrs/ADR-0053-*.md`, `adrs/ADR-0054-*.md`, `adrs/ADR-0055-*.md` are present at canonical (v1.0.1).
- **Dependencies:** none
- **Estimate:** XS
- **Satisfies AC:** `N/A — setup`
- **L1 verification:** `ls codebase-analysis.json blueprint-v1.md`; `ls adrs/ADR-005{3,4,5}-*.md` returns 3 files.
- **L2 verification:** `python3 -c "import json; json.load(open('codebase-analysis.json'))"` succeeds and `len(data['information_needs']) >= 12`.
- **L3 verification:** Phase 2 task author confirms migration-map rows are unambiguously sourced from §Migration map + IN-001/IN-003.

#### T0.2: Confirm 32-entry path-form cross-reference inventory is loadable

- **Layer:** Claude Code
- **Description:** Confirm `codebase-analysis.json` IN-008 enumerates 14 feature-scoped + 18 `adrs-migrated/` path-form references, complete with file + line for each. This is the Phase 3 path-form input.
- **Dependencies:** T0.1
- **Estimate:** XS
- **Satisfies AC:** `N/A — setup` (Discovery already satisfied AC-FR-9-c for path-form scope; T3.1 produces the bare-ID inventory which extends AC-FR-9-c)
- **L1 verification:** Grep IN-008 from codebase-analysis.json returns ≥32 reference entries.
- **L2 verification:** Spot-check 3 entries; each `<file>:<line>` returns the expected reference text via `Read`.
- **L3 verification:** T3.2 (path-form sweep execution) consumes the inventory without ambiguity.

#### T0.3: Establish working/feature/<slug>/migration-log.md scaffolding

- **Layer:** Claude Code
- **Description:** Create `working/feature/adr-placement-mechanism-repair-r1/migration-log.md` (Plan-execution audit substrate; per-task per-ADR entries will be appended at each Phase 2 task). Initial content: header + empty table per ADR ID.
- **Dependencies:** T0.1
- **Estimate:** XS
- **Satisfies AC:** `N/A — setup` (supports AC-FR-8a-2 audit-trail logging)
- **L1 verification:** `ls working/feature/adr-placement-mechanism-repair-r1/migration-log.md` returns the file.
- **L2 verification:** File contains a markdown table with per-ADR row scaffolds for the 12+1+2+5+18 = 38 ADR-touching operations (12 dedupes + 1 status-lift + 2 renumbers + 5 relocations + 18 archive ops; per-source-file counts apply at Phase 2 task time).
- **L3 verification:** Phase 2 tasks append per-ADR entries; Phase 6 verification reads the log to confirm audit completeness.

### Phase 0 Exit Criteria

- T0.1, T0.2, T0.3 L3 verifications all pass.
- Phase 0 substrate (codebase-analysis.json IN-001–IN-012; Blueprint Migration map; ADRs 0053/0054/0055; migration-log.md scaffolding) is on disk and loadable by downstream phases.
- The Phase Validator for Phase 0 (authored separately in `phase-validators.md`) confirms input substrate parses and ADR files exist.

## Phase 1 — Operator-file repairs (FR-1 through FR-5)

### Goal

Apply the four surgical edits + one parameter-default codification to the four operator files so the post-Phase-1 state expresses one internally-consistent ADR-placement convention (AC-OP-2).

### Tasks

#### T1.1: Delete retired dual-location BLOCKER prose in packager

- **Layer:** Claude Code
- **Description:** In `.claude/agents/finalize-deliverable-packager.md`, delete lines 56–63 (the retired dual-location BLOCKER check prose pinned by IN-006). Replace with a placeholder anchor (e.g., `### 3. ADR placement validator (see Phase 5 / FR-10-d)`) that names where the validator-call will be wired in Phase 5. The actual `Bash` subprocess invocation block is authored in T5.3 (Phase 5); Phase 1 deletes only the retired prose so the next packager run cannot raise the now-impossible dual-location BLOCKER.
- **Dependencies:** T0.1
- **Estimate:** S
- **Satisfies AC:** AC-FR-1-a, AC-FR-1-b (partial; AC-FR-1-b's "replacement check passes" half is satisfied jointly with T5.3)
- **L1 verification:** `grep -n "dual-location" .claude/agents/finalize-deliverable-packager.md` returns zero matches.
- **L2 verification:** Read the file; the section between former lines 56 and 63 now reads as a placeholder pointing at FR-10-d.
- **L3 verification:** Reviewer Gate 1 on the post-edit file passes (no internal contradiction); AC-OP-2 partial satisfaction confirmed.

#### T1.2: Delete contradictory dual-location BLOCKER prose in reviewer

- **Layer:** Claude Code
- **Description:** In `.claude/agents/shared-document-reviewer.md`, delete line 349 (the contradictory dual-location check pinned by IN-006). Leave lines 470–472 unchanged (sole canonical-only statement post-edit).
- **Dependencies:** T0.1
- **Estimate:** S
- **Satisfies AC:** AC-FR-2-a, AC-FR-2-b
- **L1 verification:** `grep -n "dual-location" .claude/agents/shared-document-reviewer.md` returns zero matches.
- **L2 verification:** Read the file; lines 470–472 (the post-ADR-0036 statement) are the sole ADR-placement statement in the file.
- **L3 verification:** A test invocation of `shared-document-reviewer` on a Blueprint with canonical-only ADRs returns no flag for ADR placement (verified by Phase 6 T6.1).

#### T1.3: Codify canonical-root default for `output_adrs_dir` in orchestrator SKILL.md

- **Layer:** Claude Code
- **Description:** In `.claude/skills/recipe-feature-pipeline/SKILL.md` at line 273, annotate the `output_adrs_dir` parameter with `default: "adrs/" per ADR-0036`. Use the existing parameter-table format. Per AC-FR-3-b, ensure pass-through fidelity is preserved (i.e., the SKILL.md prose specifies: if caller passes `output_adrs_dir` explicitly, orchestrator forwards unmodified; if absent, orchestrator passes `"adrs/"`).
- **Dependencies:** T0.1
- **Estimate:** S
- **Satisfies AC:** AC-FR-3-a, AC-FR-3-b
- **L1 verification:** `grep -n "default: \"adrs/\"" .claude/skills/recipe-feature-pipeline/SKILL.md` returns 1+ match near line 273.
- **L2 verification:** Read the file; the `output_adrs_dir` parameter row includes the default annotation + ADR-0036 citation + pass-through-fidelity prose.
- **L3 verification:** Phase 6 T6.2 (fresh pipeline-run probe) confirms orchestrator passes canonical-root when no override supplied.

#### T1.4: Update design-composer.md `output_adrs_dir` parameter description (3 anchors + override subsection)

- **Layer:** Claude Code
- **Description:** In `.claude/agents/design-composer.md`, edit lines 48, 129, 187 (the three `output_adrs_dir` mentions per IN-007). Each mention shall (a) cite ADR-0036, (b) state canonical-root as the default, (c) reference the test-only override mechanism. Additionally, add a new "### Test-only override for `output_adrs_dir`" subsection documenting the override surface (whatever the executor confirms; per Blueprint §Design / FR-5 the override surface is the same `output_adrs_dir` parameter — no env var or CLI flag — invoked from test harness or contrived caller).
- **Dependencies:** T0.1
- **Estimate:** M
- **Satisfies AC:** AC-FR-4-a, AC-FR-4-b, AC-FR-5-a, AC-FR-5-b
- **L1 verification:** `grep -cn "ADR-0036" .claude/agents/design-composer.md` returns ≥3 (one per anchor) + ≥1 in the new override subsection.
- **L2 verification:** Read the file; each of the three anchors mentions canonical default + ADR-0036; the new "Test-only override" subsection is present and describes the override surface.
- **L3 verification:** Reviewer Gate 1 on the post-edit file passes; AC-OP-2 partial satisfaction confirmed; the post-edit prose is internally consistent with T1.1, T1.2, T1.3 (all four files post-edit reflect canonical-only via ADR-0036).

#### T1.5: Convergence check across the four operator files (AC-OP-2 stand-up)

- **Layer:** Claude Code
- **Description:** After T1.1–T1.4 land, read the four edited files in sequence and verify: (a) no file mentions a dual-location convention; (b) each file that touches the convention cites ADR-0036; (c) no file contradicts another. Record the check result in `migration-log.md` as a Phase-1 closeout entry.
- **Dependencies:** T1.1, T1.2, T1.3, T1.4
- **Estimate:** S
- **Satisfies AC:** AC-US-2-b, AC-OP-2 (full)
- **L1 verification:** `migration-log.md` contains a Phase-1 closeout entry timestamped post-T1.4.
- **L2 verification:** The closeout entry enumerates each file + its post-edit ADR-placement statement and asserts internal consistency.
- **L3 verification:** Reviewer Gate 1 on a representative subsequent Blueprint passes without ADR-placement flag (Phase 6 T6.1 confirms structurally).

### Phase 1 Exit Criteria

- T1.1–T1.5 L3 verifications all pass.
- All four operator files express one internally-consistent ADR-placement convention (AC-OP-2 first-pass satisfaction; the full AC-OP-2 only finalizes once Phase 5 wires the validator and Phase 6 confirms empirically).
- `grep -rn "dual-location" .claude/agents/ .claude/skills/recipe-feature-pipeline/` returns zero matches.
- The Phase Validator for Phase 1 (authored separately) confirms the four-file convergence empirically.

## Phase 2 — Migration (FR-8a/b/c/d)

### Goal

Migrate every off-canonical ADR into canonical `adrs/` per Blueprint §Migration map. Four sub-phases (2a, 2b, 2c, 2d) with explicit intra-phase dependency ordering (2d before 2b-renumber per ADR-0053; 2a, 2b-status-lift, 2c, 2d in parallel-eligible groups).

### Phase 2a — Byte-identical dedupes (12 ADRs)

#### T2a.1: Byte-equality re-verification + delete for the 12 byte-identical ADRs

- **Layer:** Claude Code
- **Description:** For each of the 12 ADRs (0026, 0028, 0029, 0030, 0031, 0037, 0038, 0039, 0040, 0041, 0042, 0043), execute the per-ADR routine: (i) `diff -q adrs/ADR-NNNN-*.md working/feature/<source-folder>/adrs/ADR-NNNN-*.md` MUST return zero output (byte-identical re-verification per Assumption A2); (ii) `git rm working/feature/<source-folder>/adrs/ADR-NNNN-*.md`; (iii) append entry to `migration-log.md` with source path, byte-equality check timestamp, deletion timestamp. If (i) fails for any ADR, HALT the task and surface via `AskUserQuestion` (per Blueprint §Error Handling: byte-equality re-check failure → re-discovery). Per-ADR rows execute sequentially within this task; the 12 ADRs as a group constitute one Plan task with sub-verifications per the NFR-1 "12 byte-identical ADRs as one task with per-ADR sub-verification" exception.
- **Dependencies:** T0.1, T0.3
- **Estimate:** M (12 × ~5min per-ADR; total ~1h including audit log)
- **Satisfies AC:** AC-FR-8a-1, AC-FR-8a-2
- **L1 verification:** `ls working/feature/{audit-machinery-fixes-r1,pipeline-skill-design-fixes-r1,audit-findings-remediation-r1,devcontainer-mcp-provisioning-r1}/adrs/ADR-NNNN-*.md` for the 12 IDs returns zero files (all deleted).
- **L2 verification:** `migration-log.md` contains 12 per-ADR entries each with byte-equality check timestamp + deletion timestamp.
- **L3 verification:** Phase 6 T6.4 (validator scan) returns no findings for these 12 IDs at the deleted feature-scoped paths.

### Phase 2b — Status-lift dedupe (ADR-0024) + numbering-collision renumber (ADR-0044/0045)

#### T2b.1: ADR-0024 status-lift dedupe with fail-safe per AC-FR-8b-1.1

- **Layer:** Claude Code
- **Description:** For ADR-0024 (frontend-design-knowledge-r1): (i) `diff` the canonical and feature-scoped bodies EXCLUDING the frontmatter `status:` line (per AC-FR-8b-1.1 fail-safe — Blueprint §AC-FR-8b-1.1 specifies the procedure); (ii) if zero non-frontmatter divergence → proceed with `git rm working/feature/frontend-design-knowledge-r1/adrs/ADR-0024-*.md` (no body archival needed); (iii) if any non-frontmatter line differs → HALT, archive the feature-scoped body to `adrs/superseded/ADR-0024-feature-scoped-body.md` per OI-1 default (provenance footer naming originating feature folder + canonical-body-decision rationale), then `git rm` the feature-scoped source. Log the disposition (dedupe-clean OR fail-safe-archive) to `migration-log.md`.
- **Dependencies:** T0.1, T0.3
- **Estimate:** S
- **Satisfies AC:** AC-FR-8b-1, AC-FR-8b-1.1
- **L1 verification:** `ls working/feature/frontend-design-knowledge-r1/adrs/ADR-0024-*.md` returns zero files.
- **L2 verification:** `migration-log.md` contains the disposition (dedupe-clean OR fail-safe-archive) for ADR-0024; if fail-safe-archive, `ls adrs/superseded/ADR-0024-feature-scoped-body.md` returns the file with a provenance footer.
- **L3 verification:** Phase 6 T6.4 validator scan returns no finding for ADR-0024 at the deleted feature-scoped path.

#### T2b.2: ADR-0044 + ADR-0045 renumber per ADR-0053 (executed AFTER Phase 2d completes per ADR-0053 algorithm)

- **Layer:** Claude Code
- **Description:** Per ADR-0053 v1.0.1 (renumber baseline = max canonical IDs that pre-existed this feature's design-composer run + 1, AFTER FR-8c relocations land). With ADR-0050 the highest post-FR-8c canonical, the renumber targets are ADR-0051 (for feature ADR-0044 `per-issue-folder-model`) and ADR-0052 (for feature ADR-0045 `three-doctypes-preserved`). Procedure per ADR: (i) `git mv working/feature/issue-capture-mechanism-r1/adrs/ADR-0044-per-issue-folder-model.md adrs/ADR-0051-per-issue-folder-model.md`; (ii) edit the renumbered file's frontmatter to add `original_id: ADR-0044` and update the `id:` field to `ADR-0051`; (iii) repeat for ADR-0045 → ADR-0052 with `original_id: ADR-0045`. Append per-ADR entries to `migration-log.md` with the original ID, new ID, git mv timestamp, frontmatter edit confirmation. **Sequencing**: this task runs AFTER T2d.1–T2d.4 (Phase 2d) because the baseline computation requires post-FR-8c canonical state (per ADR-0053 explicit ordering).
- **Dependencies:** T0.1, T0.3, T2c.1 (FR-8c relocations must land first to claim 0046–0050 baseline), T2d.4 (Phase 2d must land first per ADR-0053 algorithm)
- **Estimate:** S
- **Satisfies AC:** AC-FR-8b-2
- **L1 verification:** `ls adrs/ADR-0051-per-issue-folder-model.md adrs/ADR-0052-three-doctypes-preserved.md` returns both; `ls working/feature/issue-capture-mechanism-r1/adrs/ADR-0044-*.md ADR-0045-*.md` returns zero.
- **L2 verification:** `grep -n "original_id: ADR-0044" adrs/ADR-0051-*.md` returns 1 match; same for ADR-0045 → ADR-0052; `id:` frontmatter on each renumbered file equals the new canonical ID.
- **L3 verification:** `git log --follow adrs/ADR-0051-*.md` traces back to the original feature-scoped path; same for ADR-0052 (NFR-5 history preservation).

### Phase 2c — Feature-scoped relocations (ADRs 0046–0050)

#### T2c.1: `git mv` ADRs 0046–0050 to canonical + write `.tombstone` redirect notes

- **Layer:** Claude Code
- **Description:** For each of ADR-0046, ADR-0047, ADR-0048, ADR-0049, ADR-0050 (all from `working/feature/issue-capture-mechanism-r1/adrs/`): (i) `git mv working/feature/issue-capture-mechanism-r1/adrs/ADR-NNNN-<slug>.md adrs/ADR-NNNN-<slug>.md`; (ii) write `working/feature/issue-capture-mechanism-r1/adrs/ADR-NNNN.tombstone` containing the 3-line template from Blueprint §Migration map FR-8c: `# Moved\n\nThis ADR was relocated to canonical \`adrs/ADR-NNNN-<slug>.md\` on 2026-05-24 per feature \`adr-placement-mechanism-repair-r1\` (per ADR-0036).\n`; (iii) append per-ADR entry to `migration-log.md`. NFR-5 dictates `git mv` (NOT copy-and-delete). Per AC-FR-8c-2 the `.tombstone` extension is intentional (per Q-CC-2 / D6 Option C) so the FR-10 validator's `ADR-*.md` rglob does not match it.
- **Dependencies:** T0.1, T0.3
- **Estimate:** M (5 × ~10min including tombstone writes + log entries)
- **Satisfies AC:** AC-FR-8c-1, AC-FR-8c-2, NFR-5-a, NFR-5-b
- **L1 verification:** `ls adrs/ADR-0046-*.md adrs/ADR-0047-*.md adrs/ADR-0048-*.md adrs/ADR-0049-*.md adrs/ADR-0050-*.md` returns 5 files; `ls working/feature/issue-capture-mechanism-r1/adrs/ADR-{0046,0047,0048,0049,0050}.tombstone` returns 5 files.
- **L2 verification:** Each `.tombstone` file matches the 3-line template; `migration-log.md` contains 5 per-ADR entries.
- **L3 verification:** `git log --follow adrs/ADR-0046-*.md` (and similarly for 0047–0050) traces back to the original feature-scoped path (NFR-5-b).

### Phase 2d — `adrs-migrated/` consolidation (47 source files → 48 operations per ADR-0055 v1.0.1)

Per Blueprint §Migration map FR-8d, four sub-procedures per ADR-0055 v1.0.1:

- (i) No-collision (9 IDs: 0001-0006, 0008-0010) — `git mv` final-variant to canonical; delete `-pre-*` variants.
- (ii) Archive-wins (7 IDs: 0011-0017) — archive stale canonical body to `adrs/superseded/`; `git mv` archive-final to canonical (overwrite); add provenance frontmatter; delete `-pre-*` variants.
- (iii) Canonical-wins (1 ID: 0018) — canonical retained; `git rm` archive final + `-pre-*` variants.
- (iv) Canonical-only (1 ID: 0007) — canonical untouched; `git rm` archive `-pre-naming-convention` + `-pre-template-migration` + `v1-superseded` variants (per AA-003 / ADR-0055 v1.0.1 glob extension).

#### T2d.1: Sub-procedure (i) — No-collision adds for ADRs 0001-0006, 0008-0010 (9 IDs)

- **Layer:** Claude Code
- **Description:** For each of the 9 IDs: (i) `git mv adrs-migrated/ADR-NNNN-<slug>-final.md adrs/ADR-NNNN-<slug>.md` (strip the `-final` suffix per ADR-0055 naming convention); (ii) `git rm adrs-migrated/ADR-NNNN-*-pre-naming-convention.md adrs-migrated/ADR-NNNN-*-pre-template-migration.md` (variant deletions; Git history preserves them per NFR-5); (iii) append per-ADR entry to `migration-log.md`. Total: 9 mvs + 18 variant rms (some IDs lack one variant; per IN-003 the count is exact: 9 final + 9 pre-naming + 9 pre-template = 27 source files → 9 canonical + 18 variant deletions).
- **Dependencies:** T0.1, T0.3
- **Estimate:** M (9 × ~10min including audit log; total ~1.5h)
- **Satisfies AC:** AC-FR-8d-1 (partial; full satisfaction at T2d.4)
- **L1 verification:** `ls adrs/ADR-{0001,0002,0003,0004,0005,0006,0008,0009,0010}-*.md` returns 9 files.
- **L2 verification:** `ls adrs-migrated/ADR-{0001,0002,0003,0004,0005,0006,0008,0009,0010}-*` returns zero files (all 27 source files removed: 9 moved + 18 deleted).
- **L3 verification:** Phase 6 T6.4 validator scan returns no finding for these 9 IDs at any `adrs-migrated/` path.

#### T2d.2: Sub-procedure (ii) — Archive-wins for ADRs 0011-0017 (7 IDs)

- **Layer:** Claude Code
- **Description:** For each of the 7 archive-wins IDs (0011, 0012, 0013, 0014, 0015, 0016, 0017): (i) read the existing canonical body at `adrs/ADR-NNNN-<canonical-slug>.md`; (ii) write that body to `adrs/superseded/ADR-NNNN-pre-consolidation-canonical.md` with provenance footer (per ADR-0055: identifies pre-consolidation canonical version, this-feature slug, consolidation date 2026-05-25); (iii) `git mv adrs-migrated/ADR-NNNN-<archive-slug>-final.md adrs/ADR-NNNN-<archive-slug>.md` (overwriting canonical body with the archive's v2.0.0 body); (iv) edit the new canonical file's frontmatter to add `superseded_by_consolidation: true` + `superseded_canonical_archived_to: adrs/superseded/ADR-NNNN-pre-consolidation-canonical.md`; (v) `git rm adrs-migrated/ADR-NNNN-*-pre-naming-convention.md` (and `-pre-template-migration.md` if present — per IN-003 the 7 archive-wins IDs lack `-pre-template-migration` variants); (vi) append per-ADR entry to `migration-log.md` with all 5 sub-steps + before/after slug if slug changed. Note: each archive-wins case is 1 `mv` + 1 canonical-body archive write = 2 file-touching operations per source (per I-AA-R2-003 cycle-2 clarification of 47 source files → 48 ops total).
- **Dependencies:** T0.1, T0.3
- **Estimate:** L (7 × ~20min per-ADR; canonical-body archive writes are non-trivial; total ~2.5h)
- **Satisfies AC:** AC-FR-8d-2, AC-FR-8d-1 (partial)
- **L1 verification:** `ls adrs/superseded/ADR-{0011..0017}-pre-consolidation-canonical.md` returns 7 files; `ls adrs-migrated/ADR-{0011..0017}-*` returns zero files.
- **L2 verification:** For each new canonical: `grep -n "superseded_by_consolidation: true" adrs/ADR-NNNN-*.md` returns 1 match; `grep -n "superseded_canonical_archived_to: adrs/superseded" adrs/ADR-NNNN-*.md` returns 1 match.
- **L3 verification:** `diff` between the new canonical and the prior `adrs-migrated/ADR-NNNN-*-final.md` (recoverable via `git show HEAD~1:adrs-migrated/ADR-NNNN-*-final.md`) shows the new canonical = archive's body + appended frontmatter fields.

#### T2d.3: Sub-procedure (iii) — Canonical-wins for ADR-0018

- **Layer:** Claude Code
- **Description:** Canonical `adrs/ADR-0018-codebase-analysis-schema.md` retained (carries an ADR-0038 supersession marker per IN-004; the supersession-by-ADR-0038 lineage is the load-bearing fact). `git rm adrs-migrated/ADR-0018-*` (final + pre-naming-convention variants; per IN-003 ADR-0018 lacks pre-template-migration variant). Append entry to `migration-log.md`.
- **Dependencies:** T0.1, T0.3
- **Estimate:** XS
- **Satisfies AC:** AC-FR-8d-1 (partial)
- **L1 verification:** `ls adrs-migrated/ADR-0018-*` returns zero files; `ls adrs/ADR-0018-codebase-analysis-schema.md` returns 1 file (unchanged).
- **L2 verification:** `diff` of `adrs/ADR-0018-codebase-analysis-schema.md` against the pre-Phase-2d HEAD~1 version returns no output (canonical untouched).
- **L3 verification:** Phase 6 T6.4 validator scan returns no finding for ADR-0018.

#### T2d.4: Sub-procedure (iv) — Canonical-only for ADR-0007 with v1-superseded variant deletion per AA-003

- **Layer:** Claude Code
- **Description:** Canonical `adrs/ADR-0007-code-graph-mcp-selection.md` retained (untouched). Per AA-003 / ADR-0055 v1.0.1 §Decision item 5 (canonical-only-procedure glob extension): `git rm adrs-migrated/ADR-0007-code-graph-mcp-selection-pre-naming-convention.md`, `git rm adrs-migrated/ADR-0007-*-pre-template-migration.md` (× any present), `git rm adrs-migrated/ADR-0007-code-graph-mcp-selection-v1-superseded.md` (the critical AA-003 inclusion; without this, the FR-10 validator would flag the stray v1-superseded file post-Phase-2d). Append entry to `migration-log.md`. After this task completes: `git rm -r adrs-migrated/` (the directory is now empty).
- **Dependencies:** T2d.1, T2d.2, T2d.3 (this task ALSO removes the empty `adrs-migrated/` directory; sequenced last in Phase 2d so the directory is the only Phase 2d operation that leaves a now-empty directory)
- **Estimate:** S
- **Satisfies AC:** AC-FR-8d-1 (full), AC-FR-8d-2.1, AC-FR-8d-3
- **L1 verification:** `ls adrs-migrated/` returns "No such file or directory" (directory removed); `ls adrs/ADR-0007-code-graph-mcp-selection.md` returns 1 file (unchanged).
- **L2 verification:** `git log --diff-filter=D --name-only HEAD~N..HEAD -- adrs-migrated/` shows all 47 source files deleted across T2d.1–T2d.4 (where N covers Phase 2d commits).
- **L3 verification:** Phase 6 T6.4 validator scan returns no finding involving any `adrs-migrated/` path.

### Phase 2 Exit Criteria

- T2a.1, T2b.1, T2b.2, T2c.1, T2d.1, T2d.2, T2d.3, T2d.4 L3 verifications all pass.
- Canonical `adrs/` contains 55 files (36 pre-existing + 5 relocated [0046–0050] + 2 renumbered [0051, 0052] + 3 new [0053, 0054, 0055] + 9 no-collision-adds [0001-0006, 0008-0010]; 7 archive-wins REPLACE existing canonical bodies and do not add files; 1 canonical-wins [0018] and 1 canonical-only [0007] leave canonical untouched). Per Blueprint §Architecture Overview ASCII state.
- `adrs/superseded/` contains 7 stale-canonical bodies (per ADR-0055 v1.0.1; AA-008 corrected 8 → 7).
- `adrs-migrated/` directory removed.
- `working/feature/issue-capture-mechanism-r1/adrs/` contains 5 `.tombstone` files (and nothing else with `.md` extension; ADR-0044/0045 moved out as part of T2b.2).
- Other `working/feature/<slug>/adrs/` directories (for the 4 dedupe-source folders) contain zero files (or are entirely empty — Phase 6 T6.5 reaps empty directories).
- `migration-log.md` contains audit entries for every per-ADR operation (12 + 1 + 2 + 5 + 9 + 7 + 1 + 1 = 38 ADR-touching operations).
- The Phase Validator for Phase 2 (authored separately) confirms canonical file count, archive removal, history preservation per `git log --follow`.

## Phase 3 — Cross-reference sweep (FR-9)

### Goal

Update every in-repository reference to a relocated, renumbered, or deduplicated ADR. Two sub-scopes per AC-FR-9-b: (a) 32 path-form mechanical edits (14 feature-scoped + 18 `adrs-migrated/`); (b) 368 bare-ID semantic-disambiguation occurrences for the renumbered IDs ADR-0044 (223 mentions) and ADR-0045 (145 mentions) per the AA-011 user binding decision (2026-05-25). Excludes `.tombstone` redirect notes (which legitimately reference former paths) and audit-trail files (the per-task execution result + this Plan + the migration-log).

### Tasks

#### T3.1: Enumerate the 368-occurrence bare-ID inventory at start of Phase 3

- **Layer:** Claude Code
- **Description:** Execute `grep -rn "ADR-0044\|ADR-0045" .` against the repo root, minus path-form entries already in IN-008 + minus excluded paths (`.tombstone` files; `migration-log.md`; per-task execution result files; this Plan; the Blueprint cycle-1 / cycle-2 prose that documents this very AA-011 decision; the originating ADRs ADR-0053/0054/0055 themselves that document the renumber decision). Produce `working/feature/adr-placement-mechanism-repair-r1/bare-id-inventory.json` enumerating per-occurrence: path, line number, surrounding ≥3 lines of context, preliminary baseline-heuristic classification per AC-FR-9-b.1 (i.e., bare-ID inside `working/feature/issue-capture-mechanism-r1/*` defaults to feature-meaning [renumber]; bare-ID inside `adrs/ADR-0044-flatten-execution-dispatch-hierarchy.md` or `adrs/ADR-0045-subagent-agent-tool-grant-prohibition.md` defaults to canonical-meaning [no edit]; cross-feature Blueprint prose flagged for explicit per-occurrence judgment). Expected total per Blueprint Risks-table: 368 occurrences (ADR-0044: 223; ADR-0045: 145).
- **Dependencies:** T2b.2 (renumber must land first so the inventory's edit-targets are known), T2c.1, T2d.4
- **Estimate:** M (1 grep + per-occurrence enumeration into JSON; ~2h for the enumeration writeup)
- **Satisfies AC:** AC-FR-9-c (cycle-1 expansion satisfaction — the IN-008 32-entry inventory plus this T3.1 368-entry inventory together satisfy the expanded AC-FR-9-c)
- **L1 verification:** `ls bare-id-inventory.json` returns the file; `python3 -c "import json; print(len(json.load(open('bare-id-inventory.json'))['occurrences']))"` returns ≥368.
- **L2 verification:** Inventory contains per-occurrence entries; spot-check 5 entries — each `<file>:<line>` matches an actual bare-ID reference; the baseline-heuristic classification field is populated.
- **L3 verification:** T3.3 (the bare-ID disambiguation execution) consumes the inventory without ambiguity; ambiguous entries are correctly flagged.

#### T3.2: Execute 32 path-form mechanical edits per IN-008

- **Layer:** Claude Code
- **Description:** For each of the 32 path-form references enumerated in `codebase-analysis.json` IN-008 (14 feature-scoped + 18 `adrs-migrated/`), execute path-only substitution per the D5 Option B extended pattern set (per Blueprint §Verification Strategy / Cross-reference sweep). Per-substitution: read the file at the target line; rewrite the path token to canonical; re-read to confirm only the path token changed (per AC-FR-9-b: path-only; no semantic edits). Update entries in a Phase 3 execution log section of `migration-log.md`.
- **Dependencies:** T2a.1, T2b.1, T2b.2, T2c.1, T2d.4 (all migration tasks must land first so the canonical destinations are stable; T3.2 cannot run before Phase 2 closes)
- **Estimate:** M (32 × ~10min including verify-only-path-changed; total ~5h)
- **Satisfies AC:** AC-FR-9-a (partial; T3.3 closes), AC-FR-9-b (partial; T3.3 closes), AC-FR-9-c (path-form subset)
- **L1 verification:** `grep -rn "working/feature/.*adrs/ADR-" --include="*.md" .` returns zero matches at the 14 known feature-scoped sites (or returns only matches inside `.tombstone` redirect notes / migration-log / per-task execution result, all of which are explicitly excluded per AC-FR-9-a). `grep -rn "adrs-migrated/" --include="*.md" .` returns zero matches at the 18 known archive sites (same exclusions).
- **L2 verification:** `migration-log.md` Phase-3 section contains 32 per-edit entries; each entry shows the diff was path-only.
- **L3 verification:** Phase 6 T6.6 (full inventory re-run per NFR-3) confirms zero matches for the 32 known former paths.

#### T3.3: Execute 368-occurrence bare-ID disambiguation per AC-FR-9-b.1

- **Layer:** Claude Code
- **Description:** Per AC-FR-9-b.1 procedure, for each of the 368 bare-ID occurrences enumerated in T3.1's inventory: (i) read surrounding prose (≥3 lines of context) per the inventory entry; (ii) apply baseline heuristic as STARTING POINT (not exemption) — folder-distribution heuristic from AC-FR-9-b.1; (iii) make per-occurrence judgment: feature-meaning (renumber ADR-0044 → ADR-0051 / ADR-0045 → ADR-0052) OR canonical-meaning (preserve bare ID); (iv) if ambiguous, surface to user via `AskUserQuestion` rather than guess; (v) record per-occurrence disposition in `bare-id-inventory.json` (path, line, original ID, new ID OR "preserved", rationale: heuristic-clear / heuristic-confirmed / user-escalation-resolved). This task is the LARGEST single Plan task in the Plan; the execution-time agent should consider sub-batching by source folder for tractability (4 main batches likely: issue-capture-mechanism-r1 source files; canonical adrs/ADR-0044 + adrs/ADR-0045 source files [usually "preserve"]; cross-feature Blueprint prose [requires careful judgment]; orchestrator / agent / skill prose [usually clear by context]). Per Blueprint Risks-table: this is a Medium-impact effort risk; expected runtime is large (368 × ~3min avg = ~18h, with ambiguous cases adding overhead).
- **Dependencies:** T3.1 (inventory must exist), T3.2 (path-form edits should land first so canonical paths are settled, though T3.2 and T3.3 are technically commutable in execution order)
- **Estimate:** L (could exceed L if many ambiguous cases force `AskUserQuestion` escalation; per the per-task execution result, the agent may iterate)
- **Satisfies AC:** AC-FR-9-a (full), AC-FR-9-b (full), AC-FR-9-b.1
- **L1 verification:** `bare-id-inventory.json` post-T3.3 contains a disposition for every one of the 368 occurrences (no "TBD" entries).
- **L2 verification:** For each occurrence marked "renumber-to-0051": grep the file at the target line confirms the bare ID is now `ADR-0051`. For each occurrence marked "preserved": grep the file at the target line confirms the bare ID is still `ADR-0044` (or `ADR-0045`). Sampling: spot-check 10 occurrences across the 4 batches.
- **L3 verification:** Phase 6 T6.6 re-runs the inventory-extraction grep and joins against the inventory's "preserved" flag: total `ADR-0044`/`ADR-0045` matches in the repo (excluding the canonical ADR files themselves + audit trail) equals the count of "preserved" entries in the inventory + 0 new bare IDs anywhere outside the inventory's expected locations.

#### T3.4: Cross-reference sweep convergence check

- **Layer:** Claude Code
- **Description:** After T3.2 + T3.3 land, re-run the IN-008 grep pattern set against the post-sweep repo + run T3.1's bare-ID extraction grep again. Confirm: zero matches for the 14 feature-scoped former paths (excluding tombstones + audit trail); zero matches for the 18 `adrs-migrated/` former paths (excluding audit trail); the bare-ID extraction's match count equals the disposition-tagged "preserved" count from the inventory plus zero new occurrences. Record the convergence-check result in `migration-log.md` Phase-3 closeout.
- **Dependencies:** T3.2, T3.3
- **Estimate:** S
- **Satisfies AC:** AC-OP-5 (partial; full satisfaction at Phase 6 T6.6 re-confirmation)
- **L1 verification:** `migration-log.md` contains a Phase-3 closeout entry timestamped post-T3.3.
- **L2 verification:** The closeout entry shows the three pattern sets ran with their expected counts (32 → 0; 368 → preserved-count; new-occurrences → 0).
- **L3 verification:** Phase 6 T6.6 re-runs the same convergence check empirically.

### Phase 3 Exit Criteria

- T3.1, T3.2, T3.3, T3.4 L3 verifications all pass.
- `grep` for the 32 known former path-form references returns zero matches (modulo permitted exclusions per AC-FR-9-a).
- `bare-id-inventory.json` has a disposition for every one of the 368 bare-ID occurrences; renumbered-to-feature-meaning edits applied; canonical-meaning preserved.
- `migration-log.md` Phase-3 closeout entry asserts convergence with three-pattern-set evidence.
- The Phase Validator for Phase 3 (authored separately) re-runs the convergence checks.

## Phase 4 — Validator authoring + smoke test (FR-10-a)

### Goal

Author `validate_adr_placement.py` (NEW; per Blueprint §Component 1) + extend `smoke_test_auditing_shared.py` with positive + negative path coverage. Per Q-CC-6 the wiring at the three surfaces is deferred to Phase 5 (so Phase 4's first repo-wide run is clean, post-Phase-3).

### Tasks

#### T4.1: Author `validate_adr_placement.py` per the §Contract Definitions CLI contract

- **Layer:** Claude Code
- **Description:** Create `.claude/skills/auditing-shared/scripts/validate_adr_placement.py` per Blueprint §Component 1 + §Contract Definitions. Implementation requirements: Python 3 stdlib only (NFR-8 — `argparse`, `pathlib`, `json`, `sys`, `time`); positional `scan_path` (default `.` per ADR-0027); optional `--allowlist PATH,PATH,...` flag; rglob for `ADR-*.md`; parent-directory check against canonical `adrs/` + structural exception for `adrs/superseded/` (hard-coded, not allowlist); emit `{"validator": "validate_adr_placement", "verdict": "PASS"|"BLOCK", "findings": [{"path": ..., "category": "feature-scoped"|"legacy-archive"|"unexpected-location", "remediation_hint": ...}], "scan_path": <resolved-abs-path>, "elapsed_ms": <int>}` to stdout; exit 0 = PASS, exit 2 = BLOCK, other non-zero = error per ADR-0035. NFR-2 target: `elapsed_ms < 5000` on the post-feature repo.
- **Dependencies:** T0.1
- **Estimate:** M (~3h: script ~50-100 LOC + ~1h test against existing fixtures)
- **Satisfies AC:** AC-FR-10-a, AC-CC-1 (partial; full satisfaction at T4.2), NFR-8-a
- **L1 verification:** `ls .claude/skills/auditing-shared/scripts/validate_adr_placement.py` returns the file; `python3 .claude/skills/auditing-shared/scripts/validate_adr_placement.py --help` returns the CLI usage matching the contract.
- **L2 verification:** Run `python3 .claude/skills/auditing-shared/scripts/validate_adr_placement.py` against the post-Phase-3 repo; output is well-formed JSON; verdict = "PASS"; findings = []; elapsed_ms < 5000.
- **L3 verification:** T4.2 smoke test passes both positive + negative path; AC-CC-1 fully satisfied.

#### T4.2: Extend `smoke_test_auditing_shared.py` with positive + negative coverage for validate_adr_placement

- **Layer:** Claude Code
- **Description:** In `.claude/skills/auditing-shared/scripts/smoke_test_auditing_shared.py`, add two test cases for `validate_adr_placement`: (a) positive — run against a clean fixture dir (or the live repo at this Phase 4 moment, which should be clean post-Phase-3) → expect exit 0 + verdict PASS + empty findings; (b) negative — create a transient `working/feature/test-fixture/adrs/ADR-9999-fixture.md` file, run validator, expect exit 2 + verdict BLOCK + findings[] entry citing the path with category `feature-scoped` and a remediation hint mentioning canonical `adrs/`. Cleanup the fixture after the test. Follow the existing smoke-test patterns in the file.
- **Dependencies:** T4.1
- **Estimate:** S
- **Satisfies AC:** AC-CC-2, AC-FR-10-e (partial; T6.7 negative-path harness fully validates), AC-CC-1 (full)
- **L1 verification:** `grep -n "validate_adr_placement" .claude/skills/auditing-shared/scripts/smoke_test_auditing_shared.py` returns ≥2 matches (one per test case).
- **L2 verification:** `python3 .claude/skills/auditing-shared/scripts/smoke_test_auditing_shared.py` exits 0 with all test cases (including the 2 new ones) passing.
- **L3 verification:** The smoke test's negative-path case structurally reproduces the AC-CC-2 scenario; Phase 6 T6.7 (full negative-path harness across 3 surfaces) builds on this.

### Phase 4 Exit Criteria

- T4.1, T4.2 L3 verifications all pass.
- `validate_adr_placement.py` exists, runs against the post-Phase-3 repo with verdict PASS in <5s.
- `smoke_test_auditing_shared.py` includes positive + negative coverage for the new validator; full smoke test passes.
- The Phase Validator for Phase 4 (authored separately) runs the smoke test + the live validator scan.

## Phase 5 — Validator wiring (3 surfaces) + Skill audit + remediation (FR-10-b/c/d, FR-11)

### Goal

Wire the validator at the three enforcement surfaces (orchestrator stage gate, execution-pipeline hook, packager) per ADR-0054's same-script-same-args commitment. Additionally execute the 8 file-level skill-audit remediations from Blueprint §Skill audit table. Wiring + skill audit are parallelizable within Phase 5 (independent file targets).

### Tasks

#### T5.1: Wire validator at orchestrator Step 8 (surface a per ADR-0054)

- **Layer:** Claude Code
- **Description:** In `.claude/skills/recipe-feature-pipeline/SKILL.md` Step 8 area, insert prose describing the validator subprocess invocation between `design-composer` return and `shared-document-reviewer` invocation. The orchestrator stage gate invokes `python3 .claude/skills/auditing-shared/scripts/validate_adr_placement.py` (no allowlist flag at this surface per Blueprint §Allowlist enumeration), with 120s subprocess timeout per ADR-0035, and halts the stage on exit 2 (surfaces JSON findings via `AskUserQuestion`). Per AC-FR-10-b + AC-CC-5.
- **Dependencies:** T4.1, T1.3 (orchestrator SKILL.md already touched at line 273 in Phase 1; this task adds the Step 8 gate description)
- **Estimate:** S
- **Satisfies AC:** AC-FR-10-b, AC-CC-5, NFR-6-a (partial)
- **L1 verification:** `grep -n "validate_adr_placement" .claude/skills/recipe-feature-pipeline/SKILL.md` returns ≥1 match in the Step 8 area.
- **L2 verification:** Read SKILL.md; the Step 8 prose names the validator path, subprocess invocation, exit-code semantics, and failure-surfacing mechanism (`AskUserQuestion`).
- **L3 verification:** Phase 6 T6.7 negative-path harness confirms the gate blocks at this surface.

#### T5.2: Wire validator at `run_phase_checks.py` dispatch (surface b per ADR-0054)

- **Layer:** Claude Code
- **Description:** In `.claude/skills/auditing-shared/scripts/run_phase_checks.py`, add `validate_adr_placement.py` to the parallel-dispatch set at lines 39–44 (per IN-009 anchor). The dispatch passes `--allowlist output/synthesis-*/adrs/` (per Blueprint §Allowlist enumeration — this surface is the ONLY one that passes the allowlist; per Q-CC-4 / ADR-0054 commitment 2). Findings fold into the existing `validator` dimension (per Q-CC-7 / Option A) — extend the dimension's rollup logic to include the new validator's verdict. Non-zero exit blocks phase progression per existing dispatch convention. Per AC-FR-10-c + AC-CC-3.
- **Dependencies:** T4.1
- **Estimate:** M (dispatch addition + rollup edit + verification; ~2h)
- **Satisfies AC:** AC-FR-10-c, AC-CC-3, NFR-6-a (partial)
- **L1 verification:** `grep -n "validate_adr_placement" .claude/skills/auditing-shared/scripts/run_phase_checks.py` returns ≥1 match in the dispatch block.
- **L2 verification:** `python3 .claude/skills/auditing-shared/scripts/run_phase_checks.py --help` (or equivalent existing invocation pattern) lists `validate_adr_placement` in the dispatch set; the dispatch invocation includes the `--allowlist output/synthesis-*/adrs/` flag.
- **L3 verification:** A controlled `run_phase_checks.py` invocation against a fixture with no ADR-placement violation returns exit 0 with the `validator` dimension showing the new validator's PASS; an invocation against a fixture with a feature-scoped ADR returns non-zero with the `validator` dimension showing BLOCK.

#### T5.3: Wire validator at packager + add `Bash` tool grant + `.claude/settings.json` allow-list entry (surface c per ADR-0054)

- **Layer:** Claude Code
- **Description:** Three coordinated edits: (a) in `.claude/agents/finalize-deliverable-packager.md`, replace the placeholder anchor from T1.1 (`### 3. ADR placement validator`) with the subprocess-invocation prose (`python3 .claude/skills/auditing-shared/scripts/validate_adr_placement.py`; no allowlist flag at this surface; 120s timeout per ADR-0035; non-zero exit raises BLOCKER finding into `packager-report.json`); (b) edit the packager's frontmatter `tools:` field to add `Bash` (in addition to the existing `Read, Glob, Grep, Write, TaskCreate, TaskUpdate`); (c) edit `.claude/settings.json` to add a narrow allow-list entry: `Bash(python3 .claude/skills/auditing-shared/scripts/validate_adr_placement.py*)` (per Q-CC-5 / ADR-0054 commitment 3 smallest-grant principle). Per AC-FR-10-d + AC-CC-4 + AC-FR-1-b (full closure of FR-1-b which Phase 1 started).
- **Dependencies:** T1.1 (placeholder anchor must already exist), T4.1
- **Estimate:** M (3 coordinated edits + verification; ~2h)
- **Satisfies AC:** AC-FR-10-d, AC-CC-4, AC-FR-1-b (full), NFR-6-a (partial; NFR-6-b checked at Phase 6 / Architecture Audit pass)
- **L1 verification:** `grep -n "validate_adr_placement" .claude/agents/finalize-deliverable-packager.md` returns ≥1 match; `grep -n "Bash" .claude/agents/finalize-deliverable-packager.md` returns a match in the frontmatter tools list; `grep -n "validate_adr_placement.py" .claude/settings.json` returns ≥1 match in an `allow` entry.
- **L2 verification:** Read all three files; the prose / list / allow-entry is internally consistent (same script path; subprocess pattern matches ADR-0035 convention).
- **L3 verification:** Phase 6 T6.7 negative-path harness confirms the packager surface blocks via the validator (BLOCKER finding in `packager-report.json`).

#### T5.4: Skill audit remediation — KB-documentation-criteria (4 file updates)

- **Layer:** Claude Code
- **Description:** Per Blueprint §Skill audit table, execute 4 file-level updates within `KB-documentation-criteria/references/`: (i) `disciplines/design-composition.md:36` — replace `working/feature/<slug>/adrs/ADR-NNNN-<slug>.md` with `adrs/ADR-NNNN-<slug>.md per ADR-0036`; (ii) `disciplines/design-composition.md:295` — same substitution; (iii) `deliverable-archive-spec.md:150` — remove the stale backward-compat clause (post-Phase-2d the empty-allowlist invariant makes the clause inconsistent); (iv) `templates/issue-register-template.md:96,99` — rewrite example paths to canonical `adrs/ADR-NNNN-*` form (or generic placeholders). Append per-file disposition to `migration-log.md` Phase-5 section.
- **Dependencies:** T0.1 (Blueprint §Skill audit table is the canonical disposition source); independent of T5.1, T5.2, T5.3 (parallelizable with them)
- **Estimate:** S (4 surgical edits; ~1h)
- **Satisfies AC:** AC-FR-11-a (partial; T5.5 + T5.6 close), AC-FR-11-b (partial; same), AC-FR-11-c, AC-CC-7 (partial), NFR-4-a (partial)
- **L1 verification:** For each target file: `grep -n "working/feature/<slug>/adrs/" <file>` returns zero matches; `grep -n "adrs/ADR-" <file>` returns ≥1 match in the previously-targeted context.
- **L2 verification:** Read the four target files; the 4 remediations match the Blueprint §Skill audit table prescription.
- **L3 verification:** Phase 6 T6.8 (skill-audit completeness check) confirms 4 of the 8 file-level updates landed in this task.

#### T5.5: Skill audit remediation — KB-issue-capture + capture-issue (2 file updates)

- **Layer:** Claude Code
- **Description:** Per Blueprint §Skill audit table: (i) `.claude/skills/KB-issue-capture/SKILL.md:72` — rewrite worked-example header to canonical-path-form examples; (ii) `.claude/skills/capture-issue/SKILL.md:44` — same pattern. Both are path-only refresh edits. Append per-file disposition to `migration-log.md` Phase-5 section.
- **Dependencies:** T0.1; independent of T5.1, T5.2, T5.3, T5.4
- **Estimate:** S (2 surgical edits; ~30min)
- **Satisfies AC:** AC-FR-11-a (partial), AC-FR-11-b (partial), AC-CC-7 (partial)
- **L1 verification:** `grep -n "working/feature/<slug>/adrs/" .claude/skills/KB-issue-capture/SKILL.md .claude/skills/capture-issue/SKILL.md` returns zero matches.
- **L2 verification:** Read both files; the example-header sections at lines 72 and 44 (respectively) now show canonical-path-form examples.
- **L3 verification:** Phase 6 T6.8 (skill-audit completeness check) confirms these 2 of the 8 file-level updates landed.

#### T5.6: Skill audit — recipe-feature-pipeline + synthesize disposition recording

- **Layer:** Claude Code
- **Description:** Two coordinated actions to close the audit table: (i) `.claude/skills/recipe-feature-pipeline/SKILL.md:273` — already updated in T1.3 (Phase 1); this task records the disposition entry in `migration-log.md` Phase-5 section pointing at T1.3 as the executor. (ii) `.claude/skills/synthesize/SKILL.md:22, 240` — per Q-CC-4 resolution (review-with-disposition; no edit). Validator allowlist entry covers the synthesize skill's `output/synthesis-*/adrs/` path; the SKILL.md prose stays as-is. Record the no-edit disposition in `migration-log.md` Phase-5 section with rationale citing Q-CC-4 + ADR-0054 commitment 2.
- **Dependencies:** T1.3 (referenced); T5.2 (the synthesize allowlist is at run_phase_checks dispatch in T5.2)
- **Estimate:** S (audit-trail recording; no file edits beyond migration-log.md; ~30min)
- **Satisfies AC:** AC-FR-11-a (full once T5.4 + T5.5 + this land), AC-FR-11-b (full), AC-FR-11-c (full), AC-CC-7 (full), NFR-4-a (full), NFR-4-b (N/A — no skill produced an unclassifiable finding)
- **L1 verification:** `migration-log.md` Phase-5 section contains disposition entries for all 8 file-level findings + 5 family-CLEAN entries (8 + 5 = 13 dispositions total per Blueprint §Skill audit table).
- **L2 verification:** The 13 dispositions enumerate each (file/family, line/scope, disposition: update-with-fix / no-change-with-rationale / review-with-disposition); no "TBD" or "needs investigation" entries.
- **L3 verification:** Phase 6 T6.8 reads the audit-trail entries + spot-checks each remediated file matches its disposition entry; AC-CC-7 fully satisfied.

### Phase 5 Exit Criteria

- T5.1, T5.2, T5.3, T5.4, T5.5, T5.6 L3 verifications all pass.
- All three enforcement surfaces invoke `validate_adr_placement.py` with the contract per ADR-0054 (same script, same default args, exit-code semantics, JSON shape).
- The `validator` dimension in `run_phase_checks.py` includes the new validator's findings in its rollup.
- The packager has the `Bash` tool grant + narrow `.claude/settings.json` allow-list entry.
- All 8 file-level skill remediations have landed; the 5 CLEAN families are recorded with rationale; `migration-log.md` Phase-5 section enumerates 13 dispositions.
- The Phase Validator for Phase 5 (authored separately) confirms the three-surface wiring is present and the skill audit table is complete.

## Phase 6 — Verification (AC-OP-N)

### Goal

Empirically verify every operational AC (AC-OP-1 through AC-OP-5) and every NFR AC by running the validator at all three surfaces against (a) the clean post-Phase-5 repo, (b) a controlled negative-path fixture. Additionally close out Plan-absorbed audit defer-items and reap empty feature-scoped `adrs/` directories.

### Tasks

#### T6.1: Reviewer Gate confirmation — Phase 1 operator-file convergence (AC-OP-2 / AC-FR-2-b empirical)

- **Layer:** Claude Code
- **Description:** Invoke `shared-document-reviewer` on a representative Blueprint with canonical-only ADR references (the current Blueprint v1.2.0 itself is the natural specimen) and confirm: zero flag for ADR-placement (AC-FR-2-b). Cross-check the four operator files in sequence; record empirical confirmation of AC-OP-2 in `migration-log.md` Phase-6 section. Note: this reviewer invocation is structural (the document-reviewer is invoked on this Plan/the Blueprint/an ADR; the verification is that the reviewer's prose no longer raises an ADR-placement BLOCKER for canonical placements).
- **Dependencies:** T1.5 (Phase 1 closeout)
- **Estimate:** S
- **Satisfies AC:** AC-OP-2 (empirical confirmation), AC-FR-2-b (empirical), AC-US-2-a, AC-US-2-b
- **L1 verification:** `migration-log.md` Phase-6 section contains a T6.1 entry.
- **L2 verification:** The entry shows the reviewer invocation + no ADR-placement flag.
- **L3 verification:** The reviewer's JSON output (captured in the entry) shows no `issue.category == "adr-placement"` entries.

#### T6.2: Fresh feature-pipeline-run probe — AC-OP-1 empirical

- **Layer:** Claude Code
- **Description:** Invoke a contrived `recipe-feature-pipeline` micro-run (or equivalent simulation) that exercises the Step 8 design-composer invocation with no `output_adrs_dir` override; confirm the orchestrator passes `"adrs/"` per FR-3 default; confirm any authored ADR lands at canonical; confirm the packager (T5.3-wired) returns zero ADR-placement BLOCKERs. If a full pipeline run is too costly, use a 2-step simulation: (i) print the value of `output_adrs_dir` the orchestrator would pass per its post-T1.3 SKILL.md prose; (ii) directly invoke `validate_adr_placement.py` against the post-Phase-5 repo; confirm exit 0.
- **Dependencies:** T1.3, T4.1, T5.1, T5.3
- **Estimate:** M (simulation harness setup + execution; ~2h)
- **Satisfies AC:** AC-OP-1, AC-US-1-a, AC-US-4-a, AC-FR-3-a, AC-FR-1-b (empirical)
- **L1 verification:** `migration-log.md` Phase-6 section contains a T6.2 entry.
- **L2 verification:** The entry shows the simulation steps + the orchestrator's `output_adrs_dir` value = `"adrs/"` + the validator output (exit 0, verdict PASS, empty findings).
- **L3 verification:** A subsequent real pipeline run (post-feature; first beneficiary) confirms the canonical-default behavior; observable in that run's Gate 6 packager report.

#### T6.3: Validator latency confirmation — NFR-2

- **Layer:** Claude Code
- **Description:** Time the validator's `elapsed_ms` from its own stdout JSON on the post-Phase-5 repo. Average across 5 invocations. Record in `migration-log.md` Phase-6 section. Confirm < 5000ms per NFR-2.
- **Dependencies:** T4.1
- **Estimate:** XS (~15min)
- **Satisfies AC:** AC-NFR-2-a, NFR-2
- **L1 verification:** `migration-log.md` Phase-6 section contains a T6.3 entry with timing.
- **L2 verification:** The entry shows the 5 invocations' `elapsed_ms` values + the average; average < 5000.
- **L3 verification:** Each individual run is < 5000ms (no outliers).

#### T6.4: Validator scan empirical — AC-OP-3

- **Layer:** Claude Code
- **Description:** Run `python3 .claude/skills/auditing-shared/scripts/validate_adr_placement.py` against the repo root; confirm exit 0 + verdict PASS + empty findings. Record output JSON in `migration-log.md` Phase-6 section. This is the highest-confidence empirical confirmation that Phase 2 (migration) + Phase 3 (sweep) closed cleanly.
- **Dependencies:** T2d.4 (Phase 2 closed), T3.4 (Phase 3 closed), T4.1 (validator exists)
- **Estimate:** XS
- **Satisfies AC:** AC-OP-3, AC-FR-10-a (empirical), AC-FR-8d-3, AC-CC-1
- **L1 verification:** Output JSON shows `"verdict": "PASS"`, `"findings": []`, exit code 0.
- **L2 verification:** `migration-log.md` Phase-6 section records the full JSON.
- **L3 verification:** Re-run after a 24h interval (smoke for stability) confirms identical result; no drift.

#### T6.5: Reap empty feature-scoped `working/feature/<slug>/adrs/` directories (Blueprint MINOR-3 absorption)

- **Layer:** Claude Code
- **Description:** After Phase 2 + Phase 3 land, several `working/feature/<slug>/adrs/` directories should be empty (the 4 dedupe-source folders for FR-8a; possibly the frontend-design-knowledge-r1 folder for FR-8b). `working/feature/issue-capture-mechanism-r1/adrs/` is NOT empty (contains 5 `.tombstone` files). For each empty directory: `rmdir working/feature/<slug>/adrs/` (uses `rmdir` not `rm -rf` for safety). Record per-directory action in `migration-log.md` Phase-6 section. **This task absorbs the Blueprint Reviewer MINOR-3 finding (reap empty feature-scoped `adrs/` directories) per Plan-absorbed audit findings.**
- **Dependencies:** T2d.4 (Phase 2 closed), T3.4 (Phase 3 closed; sweep doesn't leave new directory artifacts)
- **Estimate:** XS (~15min: 4-5 rmdir invocations)
- **Satisfies AC:** `N/A — cleanup` (no PRD AC; Plan-absorbed audit finding)
- **L1 verification:** `find working/feature -type d -name "adrs" -empty` returns zero directories (all empties removed).
- **L2 verification:** `working/feature/issue-capture-mechanism-r1/adrs/` still exists (contains 5 `.tombstone` files); other source folders' `adrs/` directories are removed.
- **L3 verification:** Phase 6 final-check confirms no orphan empty directories.

#### T6.6: Cross-reference sweep re-confirmation — AC-OP-5 empirical (NFR-3-b)

- **Layer:** Claude Code
- **Description:** Re-run the IN-008 path-form pattern set + the T3.1 bare-ID extraction grep against the post-Phase-5 repo. Confirm: zero matches for the 14 + 18 = 32 known former paths (excluding `.tombstone`, audit trail, this Plan, the migration-log, and the Blueprint's cycle-1/cycle-2 AA-011-documentation prose, and ADRs 0053/0054/0055 themselves); the bare-ID extraction's preserved-count matches the inventory's preserved disposition count. Record evidence in `migration-log.md` Phase-6 section. **This task absorbs the Blueprint Reviewer MINOR-2 finding (ADR count arithmetic reconciliation footnote)** by including a final-state arithmetic check: canonical `adrs/` contains exactly 55 files; `adrs/superseded/` contains exactly 7 files; `adrs-migrated/` does not exist; `working/feature/*/adrs/` contains exactly 5 `.tombstone` files and zero `.md` files.
- **Dependencies:** T3.4, T6.4, T6.5
- **Estimate:** S
- **Satisfies AC:** AC-OP-5, AC-NFR-3-b, AC-FR-9-a (empirical), AC-FR-9-b (empirical)
- **L1 verification:** `migration-log.md` Phase-6 section contains a T6.6 entry with the three pattern sets' outputs + the file-count arithmetic.
- **L2 verification:** Path-form grep counts: 0; bare-ID extraction count: equals inventory preserved-count; file-count arithmetic: 55 / 7 / 0 / 5 as expected.
- **L3 verification:** A third-party re-run (post-feature, in a fresh shell) confirms identical results.

#### T6.7: Three-surface negative-path harness — AC-OP-4 + AC-FR-10-e empirical

- **Layer:** Claude Code
- **Description:** Author + execute a contrived negative-path harness: (i) write `ADR-9999-fixture.md` to `working/feature/test-fixture/adrs/`; (ii) simulate / invoke each of the three surfaces against the post-Phase-5 repo with this fixture present and confirm each surface blocks: (a) orchestrator stage gate — run the validator standalone (proxy for the gate; the gate logic in T5.1 just invokes the validator) → expect exit 2 + JSON BLOCK; (b) `run_phase_checks.py` — invoke the dispatcher → expect non-zero exit with the `validator` dimension showing BLOCK; (c) packager — invoke the packager subprocess block via the same script invocation as T5.3 → expect exit 2 + BLOCKER finding shape consistent with `packager-report.json` schema; (iii) clean up the fixture (`git rm` or remove the fixture directory). Record per-surface outcomes in `migration-log.md` Phase-6 section.
- **Dependencies:** T5.1, T5.2, T5.3, T4.2 (smoke test provides the negative-path harness template)
- **Estimate:** M (harness authoring + 3-surface verification + cleanup; ~3h)
- **Satisfies AC:** AC-OP-4, AC-US-1-b, AC-US-3-b, AC-FR-10-e, AC-CC-2 (empirical at full three-surface scope; the smoke test in T4.2 satisfies the unit version)
- **L1 verification:** `migration-log.md` Phase-6 section contains a T6.7 entry with per-surface outcomes.
- **L2 verification:** The entry shows all 3 surfaces returning non-zero / BLOCK / BLOCKER as expected; the post-harness `working/feature/test-fixture/` is cleaned up.
- **L3 verification:** Re-run the harness in a fresh shell after fixture cleanup; identical results.

#### T6.8: Skill audit completeness empirical — AC-CC-7 + NFR-4

- **Layer:** Claude Code
- **Description:** Read `migration-log.md` Phase-5 section; confirm all 13 dispositions (8 file-level updates + 5 family-CLEAN entries) are present per AC-CC-7. Spot-check 3 of the 8 file-level remediations: re-read the target file, confirm the prescribed edit landed. Record completeness-check result in `migration-log.md` Phase-6 section. Per NFR-4-a all dispositions are no-TBD; per NFR-4-b no skill-audit finding was unclassifiable.
- **Dependencies:** T5.4, T5.5, T5.6
- **Estimate:** S (~1h)
- **Satisfies AC:** AC-CC-7 (full empirical), AC-NFR-4-a, AC-NFR-4-b, AC-FR-11-a (empirical), AC-FR-11-c
- **L1 verification:** `migration-log.md` Phase-6 section contains a T6.8 entry.
- **L2 verification:** The entry enumerates 13 dispositions + the 3 spot-checks each passed.
- **L3 verification:** Architecture Audit (if re-invoked) confirms the audit table is complete and remediable.

#### T6.9: NFR-1 atomicity verification + rollback documentation closure

- **Layer:** Claude Code
- **Description:** Per AC-NFR-1-a + AC-NFR-1-b: confirm each Phase 2 task in this Plan corresponds to one atomic git-reversible operation (or one logical group with explicit rationale; T2a.1's 12-ADR-as-one-task is the documented exception). For each FR-8 sub-phase, confirm the Blueprint's rollback subsection is reachable from this Plan's task descriptions (the Blueprint §Error Handling row "Byte-equality re-check failure" + the per-ADR `git log --follow` traceability per NFR-5 are the substrate). Record in `migration-log.md` Phase-6 section.
- **Dependencies:** all Phase 2 tasks closed; T6.4
- **Estimate:** S (~1h: audit-trail review + record-keeping)
- **Satisfies AC:** AC-NFR-1-a, AC-NFR-1-b, AC-NFR-5-a, AC-NFR-5-b
- **L1 verification:** `migration-log.md` Phase-6 section contains a T6.9 entry.
- **L2 verification:** The entry enumerates the per-Phase-2-task atomicity check + the per-sub-phase rollback-path confirmation.
- **L3 verification:** For 2 of the FR-8c relocations, run `git log --follow adrs/ADR-NNNN-*.md` and confirm history traces back to the feature-scoped path (NFR-5-b empirical).

#### T6.10: NFR-7 no-`--no-verify` audit + NFR-8 dependency-posture audit

- **Layer:** Claude Code
- **Description:** Grep the entire Plan + all per-task execution result files + the validator script for `--no-verify`; expect zero matches (NFR-7). Inspect `validate_adr_placement.py` imports; expect only Python stdlib (NFR-8). Record both checks in `migration-log.md` Phase-6 section.
- **Dependencies:** T4.1, all Phase 2/3/4/5 tasks closed
- **Estimate:** XS
- **Satisfies AC:** AC-NFR-7-a, AC-NFR-7-b (compliance proof; AC-NFR-7-b only triggers if a need was surfaced — Phase 0 confirmed none), AC-NFR-8-a
- **L1 verification:** `grep -rn "no-verify" working/feature/adr-placement-mechanism-repair-r1/ .claude/skills/auditing-shared/scripts/validate_adr_placement.py` returns zero matches.
- **L2 verification:** `migration-log.md` Phase-6 section records both grep outputs + the validator-import inspection (`grep -n "^import\|^from" .claude/skills/auditing-shared/scripts/validate_adr_placement.py` shows only stdlib modules: argparse, pathlib, json, sys, time).
- **L3 verification:** Reviewer Gate 1 on this Plan + the validator script confirms no NFR-7 / NFR-8 violation (this Plan itself should pass the check via reviewer pass).

### Phase 6 Exit Criteria

- T6.1–T6.10 L3 verifications all pass.
- AC-OP-1 through AC-OP-5 empirically confirmed.
- AC-NFR-1 through AC-NFR-8 empirically confirmed.
- `migration-log.md` Phase-6 section contains complete audit trail.
- The Phase Validator for Phase 6 (authored separately) re-runs the validator scan + the negative-path harness + the cross-reference sweep convergence check.

## Rollout — Closeout + deferral closure

### Goal

Close the `devcontainer-mcp-provisioning-r1` Gate-6 PKG-BLOCKER-001 deferral chain and notify informed stakeholders.

### Tasks

#### TR.1: Close the `devcontainer-mcp-provisioning-r1` Gate-6 PKG-BLOCKER-001 deferral

- **Layer:** Claude Code
- **Description:** Locate the deferral entry in `working/feature/devcontainer-mcp-provisioning-r1/` (Gate-6 audit-trail or per-task execution result documenting the deferral) and append a closure note: "Deferral closed by `adr-placement-mechanism-repair-r1` completion 2026-05-25; PKG-BLOCKER-001 replaced by validator-backed canonical-only check per FR-10-d." Per PRD §Communication plan.
- **Dependencies:** Phase 6 closed
- **Estimate:** S
- **Satisfies AC:** `N/A — communication` (closes a deferral chain; not a PRD AC)
- **L1 verification:** `grep -n "adr-placement-mechanism-repair-r1" working/feature/devcontainer-mcp-provisioning-r1/` returns ≥1 match in a Gate-6 audit-trail file.
- **L2 verification:** Read the appended closure note; it cites this feature's completion + the FR-10-d replacement.
- **L3 verification:** The deferral chain shows closed status; future reviewers reading the original PKG-BLOCKER-001 entry can trace to the closure.

#### TR.2: Informed-stakeholder notifications

- **Layer:** Claude Code
- **Description:** Append notification notes (one per informed stakeholder) per PRD §Communication plan:
  - To `working/feature/frontend-design-knowledge-r1/`: notify of ADR-0024 status-lift dedupe disposition (Discovery IN-002 framing; no body archival needed, OR fail-safe archival if T2b.1 triggered it).
  - To `working/feature/issue-capture-mechanism-r1/`: notify of (a) FR-8c relocation of ADRs 0046–0050 to canonical with `.tombstone` redirect notes; (b) FR-8b renumber of ADR-0044 → ADR-0051 and ADR-0045 → ADR-0052 per ADR-0053; (c) the 368-occurrence bare-ID sweep impact on this feature's prose (per T3.3 dispositions).
- **Dependencies:** Phase 6 closed (so the dispositions are final)
- **Estimate:** S
- **Satisfies AC:** `N/A — communication`
- **L1 verification:** Notification notes appended to the two informed-stakeholder feature folders.
- **L2 verification:** Each notification cites the specific dispositions taken.
- **L3 verification:** Informed stakeholders (future readers) can trace from their feature folder to the dispositions taken in this feature.

### Rollout Exit Criteria

- TR.1, TR.2 L3 verifications pass.
- `devcontainer-mcp-provisioning-r1` Gate-6 deferral closed.
- Informed stakeholders (2 features) have notification notes appended.

---

## Cross-Phase Dependencies

```text
                ┌──────────────────────────────────────────────────────────────┐
                │ Phase 0 — Discovery+Setup (carry-over)                       │
                │   T0.1 → T0.2, T0.3                                          │
                └────────────────────┬────────────────────────────┬────────────┘
                                     │                            │
                                     ▼                            ▼
   ┌─────────────────────────────────────────────────┐  ┌──────────────────────┐
   │ Phase 1 — Operator-file repairs                  │  │ Phase 2 — Migration  │
   │   T1.1 → T1.5                                    │  │                       │
   │   T1.2 → T1.5                                    │  │  ┌─ T2a.1 (12 dedupe)│
   │   T1.3 → T1.5  (and feeds T5.1)                  │  │  │   (parallelizable)│
   │   T1.4 → T1.5                                    │  │  ├─ T2b.1 (0024 SL)  │
   └────────────────────────┬────────────────────────┘  │  │   (parallelizable)│
                            │                            │  ├─ T2c.1 (0046-0050)│
                            │                            │  │   (parallelizable)│
                            │                            │  └─ T2d.1 → T2d.2 → │
                            │                            │      T2d.3 → T2d.4  │
                            │                            │      (intra-2d seq) │
                            │                            │                       │
                            │                            │  THEN sequenced last:│
                            │                            │   T2b.2 (renumber;   │
                            │                            │   depends on T2c.1+  │
                            │                            │   T2d.4 per ADR-0053)│
                            │                            └──────────┬──────────┘
                            │                                       │
                            └────────────┐                          │
                                         │                          ▼
                                         │     ┌──────────────────────────────┐
                                         │     │ Phase 3 — Cross-ref sweep    │
                                         │     │   T3.1 (bare-ID inventory)   │
                                         │     │   T3.2 (32 path-form edits)  │
                                         │     │   T3.3 (368 bare-ID disambig)│
                                         │     │   T3.4 (convergence check)   │
                                         │     └──────────────┬──────────────┘
                                         │                    │
                                         │                    ▼
                                         │     ┌──────────────────────────────┐
                                         │     │ Phase 4 — Validator authoring│
                                         │     │   T4.1 → T4.2                │
                                         │     └──────────────┬──────────────┘
                                         │                    │
                                         ▼                    ▼
                          ┌──────────────────────────────────────────────────┐
                          │ Phase 5 — Wiring + Skill audit (parallelizable)  │
                          │   T5.1 (orch gate; depends on T1.3 + T4.1)       │
                          │   T5.2 (run_phase_checks; depends on T4.1)       │
                          │   T5.3 (packager + settings.json; T1.1 + T4.1)   │
                          │   T5.4, T5.5, T5.6 (skill audit; all parallel    │
                          │     with T5.1/T5.2/T5.3 and with each other)     │
                          └──────────────────────┬──────────────────────────┘
                                                 │
                                                 ▼
                                ┌─────────────────────────────────────────┐
                                │ Phase 6 — Verification                  │
                                │   T6.1 → T6.10 (mostly parallel)         │
                                └────────────────┬────────────────────────┘
                                                 │
                                                 ▼
                                ┌─────────────────────────────────────────┐
                                │ Rollout — Closeout                       │
                                │   TR.1, TR.2                              │
                                └─────────────────────────────────────────┘
```

### Critical path

The longest sequential chain: T0.1 → T2c.1 → T2d.4 → T2b.2 → T3.1 → T3.3 → T4.1 → T4.2 → T5.3 → T6.7 → TR.1. T3.3 is the single largest task (368 bare-ID disambiguations).

### Parallel execution opportunities

- **Phase 1**: T1.1, T1.2, T1.3, T1.4 are all independent file edits; can run in parallel. T1.5 is a convergence check that depends on all four.
- **Phase 2**: T2a.1, T2b.1, T2c.1, T2d.1 are intra-Phase-2 parallelizable (each touches different ADR IDs / different feature folders / different archive sub-procedures). T2d.2, T2d.3 can run in parallel after T2d.1 lands (or even alongside T2d.1 — they touch different ID ranges). T2d.4 sequences last in Phase 2d (removes the empty directory). T2b.2 (renumber) sequences LAST in all of Phase 2 (per ADR-0053; depends on T2c.1 + T2d.4 to settle the baseline).
- **Phase 3**: T3.2 and T3.3 can run in parallel after T3.1 produces the inventory.
- **Phase 5**: T5.1, T5.2, T5.3 (wiring) parallel with T5.4, T5.5, T5.6 (skill audit). Within wiring, all three are independent file edits. Within skill audit, all three are independent file edits.
- **Phase 6**: T6.1, T6.3, T6.5, T6.8, T6.10 are parallelizable (independent verifications). T6.2, T6.4, T6.6, T6.7, T6.9 have light intra-Phase-6 dependencies but parallelize broadly.
- **Rollout**: TR.1 and TR.2 are independent communications; can run in parallel.

## L1/L2/L3 Verification Discipline

Per `KB-documentation-criteria/references/disciplines/plan-authoring.md` §L1/L2/L3 verification discipline. Summary:

- **L1 (cheapest)**: file exists; YAML/JSON parses; lint passes; grep returns expected count. Seconds.
- **L2 (functional)**: unit test green; script returns expected output; manual click-through succeeds. Minutes.
- **L3 (integration / acceptance)**: end-to-end test; pipeline run on real data; the AC's EARS test passes. Tens of minutes to hours.

A task is complete when all three pass. Phase Validators (authored in `phase-validators.md`) aggregate L3 verifications across each phase's tasks.

For this Plan's CC-only / tooling-repair character: L1 typically grep / `ls`; L2 typically diff against expected output or per-task `migration-log.md` entry; L3 typically the Phase 6 verification step that runs the same check empirically post-everything-else.

## Acceptance Test Cross-Reference

Every PRD + Blueprint AC mapped to the Plan task(s) that satisfy it. Per `KB-documentation-criteria/references/disciplines/plan-authoring.md`: no orphan ACs; no orphan tasks (or tasks tagged `N/A — setup` / `N/A — cleanup` / `N/A — communication`).

| AC ID | Satisfied by task(s) |
|---|---|
| AC-US-1-a (CC) | T6.2 |
| AC-US-1-b (CC) | T6.7 |
| AC-US-2-a (CC) | T6.1 |
| AC-US-2-b (CC) | T1.5, T6.1 |
| AC-US-3-a (CC) | T6.2 |
| AC-US-3-b (CC) | T6.7 |
| AC-US-4-a (CC) | T1.3, T6.2 |
| AC-US-4-b (CC) | T5.4, T5.5, T5.6 |
| AC-FR-1-a (CC) | T1.1 |
| AC-FR-1-b (CC) | T1.1, T5.3, T6.2 |
| AC-FR-2-a (CC) | T1.2 |
| AC-FR-2-b (CC) | T1.2, T6.1 |
| AC-FR-3-a (CC) | T1.3, T6.2 |
| AC-FR-3-b (CC) | T1.3 |
| AC-FR-4-a (CC) | T1.4 |
| AC-FR-4-b (CC) | T1.4 |
| AC-FR-5-a (CC) | T1.4 |
| AC-FR-5-b (CC) | T1.4 |
| AC-FR-6-a (CC) | Satisfied at Blueprint composition (§Existing Codebase Analysis / Fact Disposition Table + §Migration map). Plan re-verification: T0.1. |
| AC-FR-6-b (CC) | Satisfied at Blueprint composition (§Migration map). Plan re-verification: T0.1. |
| AC-FR-7-a (CC) | N/A — slot retained for traceability with PRD's superseded FR-7. |
| AC-FR-8a-1 (CC) | T2a.1 |
| AC-FR-8a-2 (CC) | T2a.1 |
| AC-FR-8b-1 (CC) | T2b.1 |
| AC-FR-8b-1.1 (CC) | T2b.1 |
| AC-FR-8b-2 (CC) | T2b.2 |
| AC-FR-8c-1 (CC) | T2c.1 |
| AC-FR-8c-2 (CC) | T2c.1 |
| AC-FR-8d-1 (CC) | T2d.1, T2d.2, T2d.3, T2d.4 |
| AC-FR-8d-2 (CC) | T2d.2 |
| AC-FR-8d-2.1 (CC) | T2d.4 |
| AC-FR-8d-3 (CC) | T2d.4, T6.4 |
| AC-FR-9-a (CC) | T3.2, T3.3, T6.6 |
| AC-FR-9-b (CC) | T3.2, T3.3, T6.6 |
| AC-FR-9-b.1 (CC) | T3.3 |
| AC-FR-9-c (CC) | T3.1, T3.2 |
| AC-FR-10-a (CC) | T4.1, T6.4 |
| AC-FR-10-b (CC) | T5.1, T6.7 |
| AC-FR-10-c (CC) | T5.2, T6.7 |
| AC-FR-10-d (CC) | T5.3, T6.7 |
| AC-FR-10-e (CC) | T4.2, T6.7 |
| AC-FR-10-f (CC) | Satisfied at Blueprint composition (§Allowlist enumeration). Plan re-verification: T5.2 records the allowlist flag in dispatch. |
| AC-FR-11-a (CC) | T5.4, T5.5, T5.6, T6.8 |
| AC-FR-11-b (CC) | T5.4, T5.5, T5.6 |
| AC-FR-11-c (CC) | T5.6, T6.8 |
| AC-CC-1 | T4.1, T4.2, T6.4 |
| AC-CC-2 | T4.2, T6.7 |
| AC-CC-3 | T5.2, T6.7 |
| AC-CC-4 | T5.3 |
| AC-CC-5 | T5.1, T6.2 |
| AC-CC-6 | Satisfied by design (no CLAUDE.md edit). Plan re-verification: implicit — no Plan task adds a CLAUDE.md entry. |
| AC-CC-7 | T5.6, T6.8 |
| AC-OP-1 | T6.2 |
| AC-OP-2 | T1.5, T6.1 |
| AC-OP-3 | T6.4 |
| AC-OP-4 | T6.7 |
| AC-OP-5 | T3.4, T6.6 |
| AC-NFR-1-a | T6.9 (validates the per-task atomicity; the actual atomicity is implicit in Plan task structure) |
| AC-NFR-1-b | Satisfied at Blueprint composition (§Error Handling rollback rows). Plan re-verification: T6.9. |
| AC-NFR-2-a | T6.3 |
| AC-NFR-3-a | Satisfied at Blueprint composition (§Verification Strategy / Output Comparison / D5 Option B extended pattern set). Plan re-verification: T3.1 documents the extended pattern set in inventory. |
| AC-NFR-3-b | T6.6 |
| AC-NFR-4-a | T5.6, T6.8 |
| AC-NFR-4-b | T5.6, T6.8 (no unclassifiable findings; precondition met) |
| AC-NFR-5-a | T2b.2, T2c.1 |
| AC-NFR-5-b | T2c.1, T6.9 |
| AC-NFR-6-a | T5.1, T5.2, T5.3 (collectively wire the three surfaces with same-script-same-args per ADR-0054) |
| AC-NFR-6-b | Verified by Architecture Audit (already PASSed at Blueprint v1.2.0). Plan re-verification: structural — T5.1+T5.2+T5.3 implement the same-script-same-args invariant. |
| AC-NFR-7-a | T6.10 |
| AC-NFR-7-b | T6.10 (compliance proof; precondition: Phase 0 confirmed no need surfaced) |
| AC-NFR-8-a | T4.1, T6.10 |

**Orphan-task check** (per Plan-authoring discipline anti-pattern 4): the only tasks not satisfying a PRD/Blueprint AC are setup-only / cleanup / communication tasks, each explicitly tagged: T0.1, T0.2, T0.3 (`N/A — setup`); T6.5 (`N/A — cleanup` — absorbs Blueprint Reviewer MINOR-3); TR.1, TR.2 (`N/A — communication`). All other tasks (34 of 40) satisfy ≥1 PRD AC.

**Orphan-AC check** (per Plan-authoring discipline): all 60 unique PRD + Blueprint ACs are mapped to ≥1 Plan task. AC-FR-7-a (SUPERSEDED), AC-CC-6 (no-CLAUDE.md), AC-FR-10-f (Blueprint-resolved), AC-FR-6-a, AC-FR-6-b, AC-NFR-1-b, AC-NFR-3-a, AC-NFR-6-b are Blueprint-composition-resolved and have explicit Plan-re-verification or "no Plan task needed; design precondition met" markers.

## Estimation Methodology

T-shirt sizes (XS / S / M / L) per `KB-documentation-criteria/references/disciplines/plan-authoring.md`:

- XS: < 30min (config edit, simple `git rm`, audit-trail entry)
- S: 30min–2h (single-file surgical edit + verification)
- M: 2–4h (multi-file coordinated edit, smoke test authoring, Phase 2 sub-task)
- L: 4h+ (T3.3 the 368-occurrence disambiguation is the only L; could exceed if many ambiguous cases require user escalation)

No precise hour estimates; T-shirts derived from comparable prior features (`devcontainer-mcp-provisioning-r1`, `issue-capture-mechanism-r1`, `audit-findings-remediation-r1`). The Plan's largest single task is T3.3 (L). The next-largest are T2d.2 (L) and the Phase 5 wiring/audit tasks (M each).

**Total task count**: **40 tasks** enumerated across 8 internal phases: 3 (Phase 0) + 5 (Phase 1) + 8 (Phase 2 = 1+2+1+4 across sub-phases 2a/2b/2c/2d) + 4 (Phase 3) + 2 (Phase 4) + 6 (Phase 5) + 10 (Phase 6) + 2 (Rollout). Frontmatter `total_tasks: 40` matches the enumeration.

## Resourcing Posture

Per-task execution by `execute-task-code-producer` agents under `execute-orchestrator-dispatch`. Phase 2 sub-tasks may benefit from parallel-fanout (T2a.1 / T2b.1 / T2c.1 / T2d.1-3 can run concurrently; T2b.2 and T2d.4 sequence last). Phase 5 likewise parallel-fanouts wiring + skill audit. The total runtime is dominated by T3.3 (368-occurrence disambiguation; estimated 18h+ wall-clock for a single execution-time agent; could parallelize across batches if multiple agents run with disjoint occurrence subsets).

Plan task descriptions assume any-contributor authoring (no domain-specialist assumption beyond CC + Python stdlib literacy).

## Open Items (Pending Cross-Artifact Audit)

The Blueprint at v1.2.0 resolved all PRD Open Items + all 7 Q-CC-N arbitration items + all design-stage MAJORs/MINORs across two reconciliation cycles. The following Plan-level items are surfaced for Cross-Artifact Audit consideration (none block Plan approval at draft):

- [ ] **OPI-1 — T3.3 execution-time discovery of ambiguous bare-ID cases.** Per AC-FR-9-b.1, the procedure escalates ambiguous cases via `AskUserQuestion`. The exact threshold (when does "context suggests both meanings" become "ambiguous"?) is judgment-bound. Phase 6 T6.6 confirms convergence regardless, but the per-task execution result will materialize the threshold empirically. Surface to Cross-Artifact Audit only if the audit detects a structural ambiguity in the Plan's framing.
- [x] ~~OPI-2 — frontmatter total_tasks reconciliation.~~ **CLOSED**: reconciliation landed at v1.0.1 patch (frontmatter = 40; matches enumerated count). No further action.
- [ ] **OPI-3 — pheonix-pipeline-style live-run probe in T6.2.** T6.2 proposes a 2-step simulation if a full pipeline run is too costly. The Cross-Artifact Audit may suggest the full pipeline run is the more rigorous L3 verification; defer to audit recommendation.

## Update History

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-05-25 | plan-author | Initial Plan composed from Blueprint v1.2.0 (post-Architecture-Audit-r2 PASS). 8 internal phases (Phase 0–6 + Rollout) decomposing into 40 enumerated tasks (frontmatter pending OPI-2 reconciliation). All 60 unique PRD + Blueprint ACs mapped via Acceptance Test Cross-Reference table; no orphan ACs. Plan-absorbed audit findings: Blueprint Reviewer MINOR-2 (file-count arithmetic reconciliation in T6.6) + MINOR-3 (reap empty feature-scoped `adrs/` directories in T6.5). Critical path: T0.1 → T2c.1 → T2d.4 → T2b.2 → T3.1 → T3.3 → T4.1 → T4.2 → T5.3 → T6.7 → TR.1; T3.3 (368-occurrence bare-ID disambiguation per AA-011 user binding) is the single largest task. Three open items surfaced for Cross-Artifact Audit (OPI-1 / OPI-2 / OPI-3). |
