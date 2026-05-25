---
id: PV-adr-placement-mechanism-repair-r1
version: 1.0.0
status: draft
doc_type: phase-validators
feature_slug: adr-placement-mechanism-repair-r1
derived_from:
  - working/feature/adr-placement-mechanism-repair-r1/plan-v1.md
  - working/feature/adr-placement-mechanism-repair-r1/prd-v1.md
  - working/feature/adr-placement-mechanism-repair-r1/blueprint-v1.md
  - working/feature/adr-placement-mechanism-repair-r1/acceptance-tests.md
prd_version: 1.0.2
blueprint_version: 1.2.0
plan_version: 1.0.1
acceptance_tests_version: 1.0.0
scope_class: FULL
layer_scope: ["claude-code"]
total_validators: 11
generated: 2026-05-25T03:30:00Z
generated_by: test-phase-validator-author
---

# Phase Validators — ADR Placement Mechanism Repair

## Contents

- [x] Purpose
- [x] Severity rules (project-wide)
- [x] Validator dependency graph
- [x] PV-0 — Discovery+Setup
- [x] PV-1 — Operator-file repairs
- [x] PV-2a — Byte-identical dedupes
- [x] PV-2b — Status-lift dedupe + renumber
- [x] PV-2c — Feature-scoped relocations
- [x] PV-2d — adrs-migrated/ consolidation
- [x] PV-3 — Cross-reference sweep
- [x] PV-4 — Validator authoring + smoke test
- [x] PV-5 — Wiring + skill audit
- [x] PV-6 — Verification (integrated final-state)
- [x] PV-R — Rollout
- [x] Cross-validator coordination
- [x] Validator runbook (operator-facing)
- [x] Update History

## Purpose

This document specifies the per-phase Phase Validators that gate phase-to-phase advance for `adr-placement-mechanism-repair-r1`. Each validator entry pins:

- The phase exit criteria from `plan-v1.md` (operationalized as observable assertions).
- The Acceptance Tests (`acceptance-tests.md`) that must pass for the phase's binding semantic claims.
- The automation hook (concrete command or script invocation) that produces the validator verdict.
- Severity rules — which criterion failures BLOCK advance vs. surface as WARNING for deferral.

The validator entries are consumed by:

- `review-cross-artifact-auditor` — for Plan ↔ Phase Validators alignment.
- `finalize-task-decomposer` — to ensure validator-setup tasks are present in the task DAG.
- The human operator during execution — to gate phase-to-phase advance using the runbook in §Cross-validator coordination.

Phase Validators do NOT change the Plan; they operationalize the verification of phases the Plan already defines.

## Severity rules (project-wide)

Each criterion within a validator is tagged with one of:

| Severity | Definition | Effect on phase advance |
|---|---|---|
| `BLOCKER` | Failure means the phase's load-bearing claim is unmet. Advance to the next phase is impossible without remediation. | Hard block. Roll back per Phase rollback. |
| `MAJOR` | Failure means a significant claim is unmet but the phase's primary deliverable may still be partially usable. | Block by default. Operator may override with explicit rationale recorded to `migration-log.md`. |
| `MINOR` | Failure means a tertiary claim is unmet (e.g., audit-trail completeness; documentation polish). | Surface as warning. Operator may defer with rationale; deferred items roll into Phase 6 closeout. |
| `NIT` | Failure means a non-substantive issue (style, formatting). | Informational only; never blocks advance. |

Each Plan phase's "load-bearing check" — the criterion that proves the phase's primary deliverable landed — MUST be `BLOCKER`. A validator with no `BLOCKER` criterion is malformed.

## Validator dependency graph

```
PV-0 ──┬─→ PV-1 ──┐
       │          │
       └─→ PV-2a ─┤
       └─→ PV-2b.1 (status-lift sub-step) ─┤
       └─→ PV-2c ─┤
       └─→ PV-2d ─┤
                  │
                  └─→ PV-2b.2 (renumber sub-step; depends on PV-2c + PV-2d per ADR-0053)
                                                  │
                                                  └─→ PV-3 ──→ PV-4 ──→ PV-5 ──→ PV-6 ──→ PV-R
```

Notes:
- PV-2b is split internally: PV-2b.1 (T2b.1 ADR-0024 status-lift) is parallelizable with PV-2a / PV-2c / PV-2d.1-3; PV-2b.2 (T2b.2 renumber) sequences after PV-2c AND PV-2d.4 (ADR-0053 algorithm).
- PV-2d itself contains an intra-validator ordering (T2d.1 → T2d.2 → T2d.3 → T2d.4) because Phase 2d's sub-procedures share the `adrs-migrated/` directory and T2d.4 sequences last (removes the now-empty directory).
- PV-6 is the integrated final-state check: every prior validator's load-bearing criterion must still hold at the moment PV-6 runs (drift-detection responsibility lives at PV-6).

## PV-0 — Discovery+Setup (carry-over formalization)

- **phase_id**: P-0
- **phase_name**: Discovery + Setup (carry-over formalization)
- **plan_reference**: `plan-v1.md` §Phase 0 — Discovery + Setup
- **validator_goal**: Prove that the Discovery substrate (codebase-analysis.json, Blueprint Migration map, ADRs 0053/54/55 at canonical, migration-log.md scaffold) is on disk and loadable by downstream phases.
- **when_run**: Post-T0.3 completion, before Phase 1 dispatch.
- **expected_duration**: < 1 minute.
- **prerequisites**: None.

### Pass criteria

| ID | Description | Assertion | Source | Automation hook | Severity |
|---|---|---|---|---|---|
| PV-0.C1 | Migration-map inputs loadable | `codebase-analysis.json` exists and parses; `data['information_needs']` has ≥12 entries (IN-001 through IN-012). | T0.1 L2 | `python3 -c "import json,sys; d=json.load(open('working/feature/adr-placement-mechanism-repair-r1/codebase-analysis.json')); sys.exit(0 if len(d['information_needs'])>=12 else 1)"` | BLOCKER |
| PV-0.C2 | Three authored ADRs present at canonical | `adrs/ADR-0053-*.md`, `adrs/ADR-0054-*.md`, `adrs/ADR-0055-*.md` exist (each v1.0.1 per Plan source). | T0.1 L1 | `ls adrs/ADR-0053-*.md adrs/ADR-0054-*.md adrs/ADR-0055-*.md` returns 3 paths. | BLOCKER |
| PV-0.C3 | Path-form cross-reference inventory loadable | `codebase-analysis.json` IN-008 enumerates ≥32 reference entries (14 feature-scoped + 18 `adrs-migrated/`). | T0.2 L1 | `python3 -c "import json,sys; d=json.load(open('working/feature/adr-placement-mechanism-repair-r1/codebase-analysis.json')); in8=[x for x in d['information_needs'] if x.get('id')=='IN-008']; sys.exit(0 if in8 and len(in8[0].get('reference_sites',[]))>=32 else 1)"` | BLOCKER |
| PV-0.C4 | Migration-log scaffolding present | `working/feature/adr-placement-mechanism-repair-r1/migration-log.md` exists with per-ADR table scaffolds. | T0.3 L2 | `ls working/feature/adr-placement-mechanism-repair-r1/migration-log.md` + content shape grep. | MAJOR |
| PV-0.C5 | Blueprint Migration map enumerates every off-canonical ADR | Blueprint §Migration map references every ADR in IN-001 through IN-004. | T0.1 L3 | Manual cross-reference check; assertion recorded in migration-log entry. | MAJOR |

### Acceptance tests scheduled for this phase

- AT-019 (AC-FR-6-a — Blueprint enumerates every off-canonical ADR with classification) — structural / L2.
- AT-020 (AC-FR-6-b — Blueprint documents migration disposition) — structural / L2.
- AT-041 (AC-FR-9-c — Cross-reference inventory; path-form subset) — structural / L2.

### Operational checks

- Setup: confirm `working/feature/adr-placement-mechanism-repair-r1/` directory is writable and committed to Git.
- Confirm no pre-existing `migration-log.md` content (the scaffold is fresh, not a re-author).

### Failure response

- C1/C2 failure → Halt; this is a Discovery-substrate gap. Re-run `discovery-codebase-researcher` or restore from earlier-version artifact.
- C3 failure → Halt; IN-008 inventory is required by Phase 3. Surface to user via `AskUserQuestion`.
- C4/C5 failure (MAJOR) → Surface to operator with deferral option; if deferred, must be re-checked at PV-6.

## PV-1 — Operator-file repairs (FR-1 through FR-5)

- **phase_id**: P-1
- **phase_name**: Operator-file repairs (FR-1 through FR-5)
- **plan_reference**: `plan-v1.md` §Phase 1 — Operator-file repairs
- **validator_goal**: Prove that the four operator files express one internally-consistent ADR-placement convention (AC-OP-2 first-pass satisfaction).
- **when_run**: Post-T1.5 completion, before Phase 2 dispatch.
- **expected_duration**: < 2 minutes (mostly grep + read).
- **prerequisites**: PV-0 passed.

### Pass criteria

| ID | Description | Assertion | Source | Automation hook | Severity |
|---|---|---|---|---|---|
| PV-1.C1 | No "dual-location" prose in any operator file | `grep -rn "dual-location" .claude/agents/ .claude/skills/recipe-feature-pipeline/` returns 0 matches. | T1.1, T1.2, T1.5 | Single grep invocation; exit 1 (no matches) is the PASS condition. | BLOCKER |
| PV-1.C2 | Packager file no longer contains retired BLOCKER prose | `grep -n "dual-location" .claude/agents/finalize-deliverable-packager.md` returns 0 matches; placeholder anchor "ADR placement validator" present pointing at FR-10-d. | T1.1 L2 | Grep + content read of section between former lines 56–63. | BLOCKER |
| PV-1.C3 | Reviewer file: line 349 dual-location prose deleted; canonical-only at 470–472 retained | `grep -n "dual-location" .claude/agents/shared-document-reviewer.md` returns 0; post-ADR-0036 prose at the documented anchor is intact. | T1.2 L2 | Grep + anchor verification. | BLOCKER |
| PV-1.C4 | Orchestrator SKILL.md codifies canonical-root default | `grep -n 'default: "adrs/"' .claude/skills/recipe-feature-pipeline/SKILL.md` returns ≥1 match near line 273; ADR-0036 citation present; pass-through-fidelity prose present. | T1.3 L1+L2 | `grep -c 'ADR-0036' .claude/skills/recipe-feature-pipeline/SKILL.md` ≥1. | BLOCKER |
| PV-1.C5 | design-composer.md updated at 3 anchors + override subsection | `grep -cn "ADR-0036" .claude/agents/design-composer.md` returns ≥4 (3 anchor edits + 1 in new override subsection); "Test-only override" subsection exists. | T1.4 L1+L2 | Grep count + section-header probe. | BLOCKER |
| PV-1.C6 | Phase-1 convergence-check entry exists in migration-log | `migration-log.md` Phase-1 closeout entry timestamped post-T1.4; enumerates each of 4 files + post-edit convention statement. | T1.5 L1+L2 | `grep -A 20 "Phase 1 closeout" migration-log.md` shows the entry. | MAJOR |
| PV-1.C7 | `output_adrs_dir` parameter not eliminated | Parameter still present in both `design-composer.md` and `recipe-feature-pipeline/SKILL.md`. | T1.4 (composer); T1.3 (SKILL.md) | `grep -c "output_adrs_dir" .claude/agents/design-composer.md .claude/skills/recipe-feature-pipeline/SKILL.md` returns ≥1 per file. | BLOCKER |

### Acceptance tests scheduled for this phase

- AT-004 (AC-US-2-b — four operator files express one convention) — structural / L2.
- AT-009 (AC-FR-1-a — packager no longer contains dual-location prose) — structural / L1.
- AT-011 (AC-FR-2-a — reviewer no longer contains line-349 prose) — structural / L1.
- AT-013 (AC-FR-3-a — orchestrator passes canonical-root by default; structural half) — structural / L2.
- AT-014 (AC-FR-3-b — orchestrator forwards explicit override unmodified) — structural / L2.
- AT-015 (AC-FR-4-a — design-composer.md cites ADR-0036) — structural / L1.
- AT-016 (AC-FR-4-b — Test-only override subsection present) — structural / L2.
- AT-017 (AC-FR-5-a — parameter not eliminated) — structural / L1.
- AT-018 (AC-FR-5-b — explicit override honored; structural half) — structural / L2.

### Operational checks

- Confirm no unintended edit landed elsewhere in any of the four operator files (diff the post-Phase-1 files against pre-Phase-1 HEAD; only the documented edits should appear).
- Confirm no `--no-verify` slipped in (NFR-7; covered by PV-6 audit but spot-check here).

### Failure response

- C1–C5 failure (BLOCKER) → Roll back the per-task edit (`git restore <file>`); re-author per the Plan task description; re-run PV-1.
- C6 failure (MAJOR) → Append the missing migration-log entry; re-run PV-1. If the convergence check itself is unreachable (the four files are not in the expected post-edit state), escalate to C1–C5 failure path.
- C7 failure (BLOCKER) → Restore the parameter to both files per AC-FR-5-a; this is a regression that would break test-time override surfaces.

## PV-2a — Byte-identical dedupes (12 ADRs)

- **phase_id**: P-2a
- **phase_name**: Byte-identical dedupes (12 ADRs)
- **plan_reference**: `plan-v1.md` §Phase 2 — Migration / Phase 2a / T2a.1
- **validator_goal**: Prove that 12 byte-identical feature-scoped ADR duplicates have been deleted (canonical retained) with per-ADR byte-equality verification logged.
- **when_run**: Post-T2a.1 completion. Parallelizable with PV-2b.1, PV-2c, PV-2d.1.
- **expected_duration**: < 1 minute.
- **prerequisites**: PV-0 passed.

### Pass criteria

| ID | Description | Assertion | Source | Automation hook | Severity |
|---|---|---|---|---|---|
| PV-2a.C1 | 12 feature-scoped duplicate copies deleted | For each of 12 IDs (0026, 0028, 0029, 0030, 0031, 0037, 0038, 0039, 0040, 0041, 0042, 0043): no file exists at `working/feature/{audit-machinery-fixes-r1,pipeline-skill-design-fixes-r1,audit-findings-remediation-r1,devcontainer-mcp-provisioning-r1}/adrs/ADR-NNNN-*.md`. | T2a.1 L1 | Bash loop: `for id in 0026 0028 0029 0030 0031 0037 0038 0039 0040 0041 0042 0043; do test -z "$(ls working/feature/*/adrs/ADR-${id}-*.md 2>/dev/null)" || exit 1; done` | BLOCKER |
| PV-2a.C2 | 12 canonical copies retained | For each of the 12 IDs: `adrs/ADR-NNNN-*.md` exists. | T2a.1 L1 | `for id in 0026 0028 0029 0030 0031 0037 0038 0039 0040 0041 0042 0043; do ls adrs/ADR-${id}-*.md >/dev/null || exit 1; done` | BLOCKER |
| PV-2a.C3 | Per-ADR byte-equality + deletion entries in migration-log | `migration-log.md` contains 12 per-ADR entries (one per dedupe) each with byte-equality timestamp + deletion timestamp. | T2a.1 L2 | `grep -c "byte-equality" migration-log.md` returns ≥12; grep verifies all 12 IDs appear. | MAJOR |
| PV-2a.C4 | Validator scan returns no finding for these 12 IDs at deleted paths | `validate_adr_placement.py` (if already authored — only true at PV-6) flags no `working/feature/*/adrs/ADR-NNNN-*.md` for these IDs. | T2a.1 L3 | Cross-checked at PV-6 (validator not yet authored at PV-2a time). | (deferred to PV-6) |

### Acceptance tests scheduled for this phase

- AT-022 (AC-FR-8a-1 — 12 duplicates deleted; canonicals retained) — structural / L1.
- AT-023 (AC-FR-8a-2 — per-ADR byte-equality verification logged) — structural / L2.

### Operational checks

- If the byte-equality re-check inside T2a.1 fails for any ADR, the Plan halts the task and surfaces via `AskUserQuestion` per Blueprint §Error Handling. PV-2a will not be reached if that happens.
- Confirm Git history preserves the deleted files: `git log --diff-filter=D --name-only HEAD~N..HEAD -- working/feature/` for the recently-committed range shows the 12 deletions.

### Failure response

- C1/C2 failure (BLOCKER) → Restore from Git (`git restore <path>`) and re-run T2a.1's per-ADR routine. If byte-equality re-check fails, surface via `AskUserQuestion` for re-discovery decision (per Blueprint §Error Handling).
- C3 failure (MAJOR) → Append missing migration-log entries; re-run PV-2a.

## PV-2b — Status-lift dedupe + numbering-collision renumber

- **phase_id**: P-2b
- **phase_name**: ADR-0024 status-lift dedupe (T2b.1) + ADR-0044/0045 renumber (T2b.2)
- **plan_reference**: `plan-v1.md` §Phase 2 — Migration / Phase 2b
- **validator_goal**: Prove (1) ADR-0024 deduped with status precedence (no body archival unless fail-safe triggered); (2) ADR-0044/0045 renumbered to ADR-0051/0052 with `original_id` provenance frontmatter.
- **when_run**: Two-step: PV-2b.1 post-T2b.1; PV-2b.2 post-T2b.2 (which itself runs AFTER PV-2c and PV-2d). The combined PV-2b passes only when both sub-validators pass.
- **expected_duration**: < 2 minutes per sub-validator.
- **prerequisites**: PV-0 passed; PV-2c + PV-2d.4 passed for PV-2b.2.

### Pass criteria

| ID | Description | Assertion | Source | Automation hook | Severity |
|---|---|---|---|---|---|
| PV-2b.C1 (sub-PV-2b.1) | ADR-0024 feature-scoped copy deleted | `ls working/feature/frontend-design-knowledge-r1/adrs/ADR-0024-*.md` returns no files. | T2b.1 L1 | `test -z "$(ls working/feature/frontend-design-knowledge-r1/adrs/ADR-0024-*.md 2>/dev/null)"` | BLOCKER |
| PV-2b.C2 (sub-PV-2b.1) | ADR-0024 canonical retained at Accepted status | `adrs/ADR-0024-*.md` exists; frontmatter `status:` = "Accepted". | T2b.1 L1+L2 | `grep "^status:" adrs/ADR-0024-*.md` shows "Accepted". | BLOCKER |
| PV-2b.C3 (sub-PV-2b.1) | Disposition recorded (dedupe-clean OR fail-safe-archive) | `migration-log.md` ADR-0024 entry shows disposition; if "fail-safe-archive", `adrs/superseded/ADR-0024-feature-scoped-body.md` exists with provenance footer. | T2b.1 L2 | Grep ADR-0024 entry; conditional `ls` on archive path. | MAJOR |
| PV-2b.C4 (sub-PV-2b.2) | ADR-0044 → ADR-0051 renumber complete | `adrs/ADR-0051-per-issue-folder-model.md` exists; `working/feature/issue-capture-mechanism-r1/adrs/ADR-0044-*.md` does not. | T2b.2 L1 | `ls adrs/ADR-0051-per-issue-folder-model.md && test -z "$(ls working/feature/issue-capture-mechanism-r1/adrs/ADR-0044-*.md 2>/dev/null)"` | BLOCKER |
| PV-2b.C5 (sub-PV-2b.2) | ADR-0045 → ADR-0052 renumber complete | `adrs/ADR-0052-three-doctypes-preserved.md` exists; `working/feature/issue-capture-mechanism-r1/adrs/ADR-0045-*.md` does not. | T2b.2 L1 | Symmetric to C4. | BLOCKER |
| PV-2b.C6 (sub-PV-2b.2) | `original_id` provenance frontmatter present | `grep -n "original_id: ADR-0044" adrs/ADR-0051-*.md` returns 1 match; `grep -n "original_id: ADR-0045" adrs/ADR-0052-*.md` returns 1 match. | T2b.2 L2 | Combined grep. | BLOCKER |
| PV-2b.C7 (sub-PV-2b.2) | `id:` frontmatter on each renumbered file equals new canonical ID | `grep -n "^id: ADR-0051" adrs/ADR-0051-*.md` returns 1; same for ADR-0052. | T2b.2 L2 | Grep. | BLOCKER |
| PV-2b.C8 (sub-PV-2b.2) | Git history preserved across the rename | `git log --follow adrs/ADR-0051-*.md` traces back to `working/feature/issue-capture-mechanism-r1/adrs/ADR-0044-*.md`; same for 0052/0045. | T2b.2 L3 | `git log --follow` exit 0 + trace assertion (NFR-5-b). | BLOCKER |

### Acceptance tests scheduled for this phase

- AT-024 (AC-FR-8b-1 — ADR-0024 dedupes with status precedence) — structural / L1.
- AT-025 (AC-FR-8b-1.1 happy path — diff excluding status confirms no divergence) — structural / L2.
- AT-026 (AC-FR-8b-1.1 fail-safe path — non-frontmatter divergence triggers archival) — structural / L2 (conditional).
- AT-027 (AC-FR-8b-2 existence — renumbered files at canonical) — structural / L1.
- AT-028 (AC-FR-8b-2 provenance — `original_id` frontmatter) — structural / L1.

### Operational checks

- AC-FR-8b-1.1 fail-safe: if the `diff` excluding frontmatter `status:` shows any body line difference, T2b.1 halts and writes `adrs/superseded/ADR-0024-feature-scoped-body.md`. PV-2b.C3 includes this conditional branch.
- The renumber baseline computation (per ADR-0053 v1.0.1) assumes ADR-0050 is the highest post-FR-8c canonical. If PV-2c determined a different highest ID, the renumber targets shift; this MUST be re-checked before T2b.2 runs.

### Failure response

- C1–C3 failure → Investigate T2b.1 (status-lift). If body diff was actually present and fail-safe should have triggered but didn't, restore feature-scoped copy from Git, apply fail-safe path, re-run.
- C4–C8 failure → If `git mv` did not preserve history (rare), the renumber must be redone via Git operations rather than copy-and-delete. NFR-5 forbids the latter.

## PV-2c — Feature-scoped relocations (ADRs 0046–0050)

- **phase_id**: P-2c
- **phase_name**: Relocation of ADRs 0046–0050 with `.tombstone` redirect notes
- **plan_reference**: `plan-v1.md` §Phase 2 — Migration / Phase 2c / T2c.1
- **validator_goal**: Prove 5 feature-scoped ADRs (0046–0050) relocated via `git mv` to canonical with `.tombstone` redirect notes left behind, Git history preserved.
- **when_run**: Post-T2c.1 completion. Parallelizable with PV-2a, PV-2b.1, PV-2d.1-3.
- **expected_duration**: < 2 minutes.
- **prerequisites**: PV-0 passed.

### Pass criteria

| ID | Description | Assertion | Source | Automation hook | Severity |
|---|---|---|---|---|---|
| PV-2c.C1 | 5 ADRs present at canonical | `ls adrs/ADR-0046-*.md adrs/ADR-0047-*.md adrs/ADR-0048-*.md adrs/ADR-0049-*.md adrs/ADR-0050-*.md` returns 5 files. | T2c.1 L1 | One-line ls + count assertion. | BLOCKER |
| PV-2c.C2 | 5 `.tombstone` redirect notes present in originating folder | `ls working/feature/issue-capture-mechanism-r1/adrs/ADR-{0046,0047,0048,0049,0050}.tombstone` returns 5 files. | T2c.1 L2 | ls + count assertion. | BLOCKER |
| PV-2c.C3 | Each `.tombstone` matches the 3-line template | Each file: contains "# Moved" header + redirect prose + ADR-0036 citation per Blueprint §Migration map FR-8c template. | T2c.1 L2 | Loop over 5 files; grep template lines. | MAJOR |
| PV-2c.C4 | No `.md` files for these 5 IDs remain in feature folder | `ls working/feature/issue-capture-mechanism-r1/adrs/ADR-{0046,0047,0048,0049,0050}-*.md` returns no files. | T2c.1 L1 | Symmetric check; ensures `git mv` (not copy) was used. | BLOCKER |
| PV-2c.C5 | Git history preserved for each relocation | `git log --follow adrs/ADR-NNNN-*.md` (each of 5 IDs) traces back to original feature-scoped path. | T2c.1 L3 (NFR-5-b) | Loop over 5 IDs; `git log --follow` exit + path trace. | BLOCKER |
| PV-2c.C6 | Per-ADR migration-log entries present | `migration-log.md` contains 5 entries (one per relocated ADR) each with source path, destination path, tombstone-write timestamp. | T2c.1 L2 | Grep per ADR ID in migration-log. | MAJOR |

### Acceptance tests scheduled for this phase

- AT-029 (AC-FR-8c-1 — 5 ADRs at canonical; Git history preserved) — structural + integration / L2+L3.
- AT-030 (AC-FR-8c-2 — `.tombstone` redirect notes per template) — structural / L2.

### Operational checks

- The validator (when authored in Phase 4) intentionally does NOT match `.tombstone` files because they lack the `.md` extension (per Q-CC-2 / D6 Option C). Verify PV-4.C-VALIDATOR-RUN does not flag the tombstones.
- AC-NFR-5-a: `git mv` (not copy-and-delete) is the only sanctioned mechanism here; if PV-2c.C5 fails (history broken), investigate whether T2c.1 used the wrong mechanism.

### Failure response

- C1–C5 failure → Restore feature-scoped originals from Git, re-execute T2c.1 with proper `git mv` semantics, re-run PV-2c.
- C6 failure (MAJOR) → Append missing migration-log entries; re-run.

## PV-2d — `adrs-migrated/` consolidation (4 sub-procedures per ADR-0055 v1.0.1)

- **phase_id**: P-2d
- **phase_name**: `adrs-migrated/` consolidation (47 source files → 48 ops; 4 sub-procedures)
- **plan_reference**: `plan-v1.md` §Phase 2 — Migration / Phase 2d / T2d.1–T2d.4
- **validator_goal**: Prove all 47 source files in `adrs-migrated/` have been processed per ADR-0055 v1.0.1 four sub-procedures (no-collision / archive-wins / canonical-wins / canonical-only); the directory is removed; 7 stale canonical bodies archived to `adrs/superseded/`.
- **when_run**: Post-T2d.4 completion (T2d.4 is the last task in Phase 2d). Internally PV-2d depends on T2d.1 → T2d.2 → T2d.3 → T2d.4 having run in that order.
- **expected_duration**: < 3 minutes.
- **prerequisites**: PV-0 passed.

### Pass criteria

| ID | Description | Assertion | Source | Automation hook | Severity |
|---|---|---|---|---|---|
| PV-2d.C1 | `adrs-migrated/` directory removed | `test ! -d adrs-migrated/` returns exit 0. | T2d.4 L1 | Single test. | BLOCKER |
| PV-2d.C2 | Sub-procedure (i) no-collision: 9 ADRs at canonical | `ls adrs/ADR-{0001,0002,0003,0004,0005,0006,0008,0009,0010}-*.md` returns 9 files. | T2d.1 L1 | Single ls + count. | BLOCKER |
| PV-2d.C3 | Sub-procedure (ii) archive-wins: 7 canonical bodies archived | `ls adrs/superseded/ADR-{0011,0012,0013,0014,0015,0016,0017}-pre-consolidation-canonical.md` returns 7 files. | T2d.2 L1 | Single ls + count. | BLOCKER |
| PV-2d.C4 | Sub-procedure (ii) archive-wins: new canonical frontmatter fields present | For each of IDs 0011–0017: `grep -n "superseded_by_consolidation: true" adrs/ADR-NNNN-*.md` returns 1; `grep -n "superseded_canonical_archived_to: adrs/superseded" adrs/ADR-NNNN-*.md` returns 1. | T2d.2 L2 | Loop + grep. | BLOCKER |
| PV-2d.C5 | Sub-procedure (ii) archive-wins: provenance footer in each archived body | Each `adrs/superseded/ADR-NNNN-pre-consolidation-canonical.md` contains provenance footer naming the pre-consolidation canonical version, this-feature slug, and consolidation date. | T2d.2 L2 | Loop + content grep. | MAJOR |
| PV-2d.C6 | Sub-procedure (iii) canonical-wins: ADR-0018 untouched at canonical | `adrs/ADR-0018-codebase-analysis-schema.md` exists; `diff` against pre-Phase-2d HEAD shows no change. | T2d.3 L2 | `git diff HEAD~N -- adrs/ADR-0018-codebase-analysis-schema.md` empty (where N covers Phase 2d). | BLOCKER |
| PV-2d.C7 | Sub-procedure (iv) canonical-only: ADR-0007 untouched at canonical; v1-superseded variant deleted | `adrs/ADR-0007-code-graph-mcp-selection.md` exists (unchanged); `git log --diff-filter=D --name-only` shows `adrs-migrated/ADR-0007-code-graph-mcp-selection-v1-superseded.md` deletion. | T2d.4 L1+L2 (AA-003 critical) | `ls` + `git log --diff-filter=D` grep. | BLOCKER |
| PV-2d.C8 | All `-pre-naming-convention`, `-pre-template-migration`, `-v1-superseded` variants removed from working tree | `git ls-files \| grep -E "(pre-naming-convention\|pre-template-migration\|v1-superseded)"` returns no matches. | T2d.1–T2d.4 L2 | Single git ls-files + grep. | BLOCKER |
| PV-2d.C9 | `migration-log.md` enumerates all per-ADR Phase 2d operations | Migration-log contains per-ADR entries for: 9 no-collision + 7 archive-wins (with 2 ops each) + 1 canonical-wins + 1 canonical-only = at least 18 ADR-touching log entries for Phase 2d. | T2d.1–T2d.4 L2 | Grep per ID. | MAJOR |

### Acceptance tests scheduled for this phase

- AT-031 (AC-FR-8d-1 — `adrs-migrated/` removed) — structural / L1.
- AT-032 (AC-FR-8d-1 — final variants at canonical with suffix policy) — structural / L2.
- AT-033 (AC-FR-8d-2 — 7 archive-wins frontmatter + superseded-canonical archival) — structural / L2.
- AT-034 (AC-FR-8d-2.1 — ADR-0007 v1-superseded variant deleted per AA-003) — structural / L1.

### Operational checks

- The "47 source files → 48 operations" expansion (per AA-012 / I-AA-R2-003) is honored because each archive-wins case is two file-touching ops (one `mv` of archive + one write of prior canonical body to superseded). PV-2d.C3 + PV-2d.C4 collectively verify both halves of those 7 cases.
- The Plan exit criteria state `adrs/superseded/` contains exactly 7 stale-canonical bodies (cycle-1 AA-008 correction 8→7); the AC-FR-8d-2 finding count is 7, not 8.

### Failure response

- C1 failure (BLOCKER) → `adrs-migrated/` non-empty; investigate which sub-procedure didn't run to completion; re-run that sub-task; do NOT proceed to PV-2b.2 (renumber) until PV-2d passes (per ADR-0053 algorithm).
- C3/C4/C5 failure → Re-run T2d.2 for the affected ID; recover prior canonical bodies from Git history if necessary.
- C7 failure → The AA-003 v1-superseded deletion is critical: without it, PV-6's validator scan will flag the stray file. Re-execute T2d.4's glob extension.
- C8 failure → Variant deletions incomplete; re-run T2d.1–T2d.4 for the affected ID(s).

## PV-3 — Cross-reference sweep (FR-9)

- **phase_id**: P-3
- **phase_name**: Cross-reference sweep (32 path-form + 368 bare-ID disambiguations)
- **plan_reference**: `plan-v1.md` §Phase 3 — Cross-reference sweep / T3.1–T3.4
- **validator_goal**: Prove (1) 32 known former path-form references return zero matches in repo (excluding documented exclusions); (2) 368 bare-ID occurrences of ADR-0044/0045 each carry a per-occurrence disposition; (3) no new bare-ID occurrences outside the inventory's expected locations.
- **when_run**: Post-T3.4 completion. Sequenced after PV-2b.2, PV-2c, PV-2d.
- **expected_duration**: < 5 minutes (inventory parse + sample grep).
- **prerequisites**: PV-2b.2, PV-2c, PV-2d passed.

### Pass criteria

| ID | Description | Assertion | Source | Automation hook | Severity |
|---|---|---|---|---|---|
| PV-3.C1 | Bare-ID inventory exists with 368+ entries | `bare-id-inventory.json` exists; entries count ≥368. | T3.1 L1 | `python3 -c "import json,sys; d=json.load(open('working/feature/adr-placement-mechanism-repair-r1/bare-id-inventory.json')); sys.exit(0 if len(d['occurrences'])>=368 else 1)"` | BLOCKER |
| PV-3.C2 | Zero path-form references at 14 known feature-scoped sites | `grep -rn "working/feature/.*/adrs/ADR-" --include="*.md" .` (excluding tombstones / migration-log / per-task execution results / this Plan / Blueprint cycle-1/2 prose / ADRs 0053/54/55) returns 0 matches. | T3.2 L1 | Scripted grep with documented exclusion list. | BLOCKER |
| PV-3.C3 | Zero path-form references at 18 known `adrs-migrated/` sites | `grep -rn "adrs-migrated/" --include="*.md" .` (same exclusions) returns 0 matches. | T3.2 L1 | Symmetric grep. | BLOCKER |
| PV-3.C4 | All 368 bare-ID occurrences carry a disposition | Inventory entries each have `disposition` field set to one of (renumbered-to-0051 / renumbered-to-0052 / preserved / user-escalation-resolved); no "TBD". | T3.3 L1+L2 | Python parse + filter for "TBD" — must return 0. | BLOCKER |
| PV-3.C5 | All inventory entries carry rationale | Each entry has `rationale` ∈ (heuristic-clear / heuristic-confirmed / user-escalation-resolved). | T3.3 L2 | Python filter. | MAJOR |
| PV-3.C6 | Ambiguous cases escalated via AskUserQuestion (audit trail present) | For each entry with `rationale == "user-escalation-resolved"`: a corresponding `AskUserQuestion` invocation is recorded in the per-task execution result. | T3.3 L2 | Cross-check inventory vs. per-task execution result. | MAJOR |
| PV-3.C7 | Phase-3 convergence-check entry in migration-log | `migration-log.md` Phase-3 closeout entry shows the three pattern sets' outputs (32→0; 368→preserved-count; new-occurrences→0). | T3.4 L1+L2 | Grep "Phase 3 closeout" in migration-log. | MAJOR |
| PV-3.C8 | Bare-ID extraction match-count equals preserved-count + zero unexpected occurrences | Re-run `grep -rn "ADR-0044\|ADR-0045"` against repo (minus documented exclusions); count of matches equals the inventory's "preserved" disposition count. | T3.4 L3 | Scripted grep + Python join against inventory. | BLOCKER |

### Acceptance tests scheduled for this phase

- AT-036 (AC-FR-9-a — zero in-repo references to former ADR paths) — structural / L2.
- AT-037 (AC-FR-9-b — path-only constraint) — structural / L2.
- AT-038 (AC-FR-9-b — 368 bare-ID sweep, per-occurrence disposition) — structural / L2.
- AT-039 (AC-FR-9-b.1 — baseline-heuristic procedure applied per-occurrence) — structural / L2.
- AT-040 (AC-FR-9-b.1 — ambiguous cases escalated) — structural / L2.
- AT-041 (AC-FR-9-c — cross-reference inventory enumerates every site) — structural / L2.

### Operational checks

- The documented exclusion list for PV-3.C2/C3/C8 is load-bearing: errors in the exclusion list will produce false-positive failures. The exclusion list MUST mirror Plan T3.1's specification (`.tombstone` / `migration-log.md` / per-task execution result files / this Plan / Blueprint cycle-1/cycle-2 prose / ADRs 0053/54/55).
- T3.3's per-occurrence judgment is the largest single Plan task (L estimate; could be 18h+ wall-clock). PV-3 cannot run until the inventory is fully populated; partial runs are not a valid pass condition.

### Failure response

- C1 failure (BLOCKER) → T3.1 didn't complete; re-run inventory extraction.
- C2/C3 failure (BLOCKER) → At least one path-form reference was missed by T3.2; identify via grep output, edit per AC-FR-9-b path-only convention, re-run.
- C4 failure (BLOCKER) → T3.3 incomplete; complete remaining occurrences. If user-escalation is blocked (no decisive context for some occurrences), surface to operator via `AskUserQuestion` per AC-FR-9-b.1.
- C8 failure (BLOCKER) → New bare-ID occurrence introduced outside the inventory (likely because a Phase 3 edit accidentally created a fresh `ADR-0044` reference). Investigate, then re-run.

## PV-4 — Validator authoring + smoke test (FR-10-a)

- **phase_id**: P-4
- **phase_name**: Author `validate_adr_placement.py` + extend `smoke_test_auditing_shared.py`
- **plan_reference**: `plan-v1.md` §Phase 4 — Validator authoring / T4.1, T4.2
- **validator_goal**: Prove `validate_adr_placement.py` exists with the contracted CLI shape (Blueprint §Contract Definitions); runs against the post-Phase-3 repo with verdict PASS in <5s; smoke test includes positive + negative coverage.
- **when_run**: Post-T4.2 completion. Sequenced after PV-3 (so the first repo-wide validator run is clean per Q-CC-6).
- **expected_duration**: < 2 minutes.
- **prerequisites**: PV-3 passed.

### Pass criteria

| ID | Description | Assertion | Source | Automation hook | Severity |
|---|---|---|---|---|---|
| PV-4.C1 | Validator script exists | `.claude/skills/auditing-shared/scripts/validate_adr_placement.py` exists. | T4.1 L1 | `test -f .claude/skills/auditing-shared/scripts/validate_adr_placement.py` | BLOCKER |
| PV-4.C2 | Validator CLI contract honored | `python3 .claude/skills/auditing-shared/scripts/validate_adr_placement.py --help` exits 0 with the documented `scan_path` positional + `--allowlist` optional flag. | T4.1 L1+L2 | `--help` + grep for "scan_path" and "--allowlist" in output. | BLOCKER |
| PV-4.C3 | Validator returns PASS on post-Phase-3 repo | Run against repo root; exit 0; JSON `verdict == "PASS"`; `findings == []`. | T4.1 L2 | `python3 .claude/skills/auditing-shared/scripts/validate_adr_placement.py` + JSON parse. | BLOCKER |
| PV-4.C4 | Validator latency < 5s (NFR-2) | JSON `elapsed_ms < 5000`. | T4.1 L2 (NFR-2 proxy) | Parse `elapsed_ms` from JSON output. | MAJOR (BLOCKER if elapsed_ms > 10000, indicating systemic perf issue) |
| PV-4.C5 | Validator stdlib-only (NFR-8) | `grep -nE "^import\|^from" .claude/skills/auditing-shared/scripts/validate_adr_placement.py` shows only stdlib modules (argparse, pathlib, json, sys, time). | T4.1 L2 (NFR-8 proxy) | Grep + manual whitelist check. | BLOCKER |
| PV-4.C6 | Smoke test includes positive + negative coverage for validator | `grep -cn "validate_adr_placement" .claude/skills/auditing-shared/scripts/smoke_test_auditing_shared.py` returns ≥2 matches. | T4.2 L1 | Grep. | BLOCKER |
| PV-4.C7 | Smoke test passes end-to-end | `python3 .claude/skills/auditing-shared/scripts/smoke_test_auditing_shared.py` exits 0 with all test cases passing (including new validator-related cases). | T4.2 L2 | Smoke test invocation. | BLOCKER |
| PV-4.C8 | Smoke-test negative-path fixture cleaned up | After smoke test runs, no `working/feature/test-fixture/` directory remains. | T4.2 L2 | `test ! -d working/feature/test-fixture/` | MAJOR |

### Acceptance tests scheduled for this phase

- AT-042 (AC-FR-10-a — validator returns non-zero on any non-canonical ADR) — integration / L3.
- AT-051 (AC-CC-1 — validator returns exit 0 with PASS on clean repo) — integration / L3.
- AT-052 (AC-CC-2 — validator returns exit 2 BLOCK on negative fixture) — integration / L3.
- AT-076 (AC-NFR-8-a — validator stdlib-only) — structural / L1.

### Operational checks

- The validator's first repo-wide run at PV-4 MUST be PASS — this is Q-CC-6's deliberate sequencing (Phase 3 closes the repo before Phase 4 validator runs).
- The `adrs/superseded/` structural exception is hard-coded in the validator (not an allowlist entry per Blueprint §Allowlist enumeration); confirm by reading the script or via the absence of any flag against the 7 archived bodies in `adrs/superseded/`.

### Failure response

- C1/C2 failure → T4.1 didn't complete or CLI contract diverged; re-author per Blueprint §Component 1 + §Contract Definitions.
- C3 failure → Repository is NOT clean post-Phase-3; either a sweep miss (re-run PV-3) or a migration miss (re-run PV-2). Findings will name the offending paths.
- C4 (MAJOR with BLOCKER escalation) → If `elapsed_ms` slightly exceeds 5000, surface for deferral (could be Codespace contention). If >10000, BLOCK — there's a systemic performance issue (e.g., a non-stdlib import slipped in or rglob is misconfigured).
- C5 failure → A non-stdlib import slipped in; remove or surface to user with NFR-8 justification per AC-NFR-8-a.
- C6/C7 failure → Smoke test incomplete or failing; re-author T4.2 per Blueprint pattern.

## PV-5 — Validator wiring (3 surfaces) + skill audit + remediation

- **phase_id**: P-5
- **phase_name**: Three-surface wiring (T5.1–T5.3) + skill audit (T5.4–T5.6)
- **plan_reference**: `plan-v1.md` §Phase 5 — Validator wiring + skill audit
- **validator_goal**: Prove (1) all three enforcement surfaces invoke `validate_adr_placement.py` with the same-script-same-args commitment per ADR-0054; (2) packager has `Bash` tool grant + narrow `.claude/settings.json` allow-list entry; (3) all 8 file-level skill remediations landed; (4) 5 CLEAN families recorded.
- **when_run**: Post-T5.1–T5.6 completion. Sequenced after PV-4.
- **expected_duration**: < 5 minutes.
- **prerequisites**: PV-4 passed.

### Pass criteria

| ID | Description | Assertion | Source | Automation hook | Severity |
|---|---|---|---|---|---|
| PV-5.C1 | Surface (a) orchestrator Step 8: validator invocation prose present | `grep -n "validate_adr_placement" .claude/skills/recipe-feature-pipeline/SKILL.md` returns ≥1 match in the Step 8 area; prose names subprocess invocation + exit-code semantics + `AskUserQuestion` failure-surfacing. | T5.1 L1+L2 | Grep + section read. | BLOCKER |
| PV-5.C2 | Surface (b) run_phase_checks dispatch includes validator | `grep -n "validate_adr_placement" .claude/skills/auditing-shared/scripts/run_phase_checks.py` returns ≥1 match in dispatch block lines 39–44; dispatch invocation includes `--allowlist output/synthesis-*/adrs/` per Blueprint §Allowlist enumeration. | T5.2 L1+L2 | Grep + flag verification. | BLOCKER |
| PV-5.C3 | Surface (c) packager: validator subprocess prose + `Bash` tool grant + settings allow-list | `grep -n "validate_adr_placement" .claude/agents/finalize-deliverable-packager.md` ≥1; `grep -n "^tools:" .claude/agents/finalize-deliverable-packager.md` shows `Bash` in the list; `grep -n "validate_adr_placement.py" .claude/settings.json` ≥1 in an `allow` entry. | T5.3 L1+L2 | Three coordinated grep checks. | BLOCKER |
| PV-5.C4 | Three-surface same-script-same-args invariant (NFR-6-a) | All three surfaces reference the same script path (`.claude/skills/auditing-shared/scripts/validate_adr_placement.py`). Only surface (b) passes `--allowlist`. | T5.1+T5.2+T5.3 L2 | Cross-check the 3 grep matches; confirm script path identity. | BLOCKER |
| PV-5.C5 | Skill audit: 8 file-level remediations landed | (i) `KB-documentation-criteria/references/disciplines/design-composition.md:36, :295` — canonical-only edits; (ii) `KB-documentation-criteria/references/deliverable-archive-spec.md:150` — stale clause removed; (iii) `KB-documentation-criteria/references/templates/issue-register-template.md:96, :99` — example paths refreshed; (iv) `KB-issue-capture/SKILL.md:72` — refreshed; (v) `capture-issue/SKILL.md:44` — refreshed. | T5.4 + T5.5 L1+L2 | Per-file grep showing `working/feature/<slug>/adrs/` removed; canonical references in place. | BLOCKER |
| PV-5.C6 | `migration-log.md` Phase-5 section records 13 dispositions (8 updates + 5 CLEAN families) | Section enumerates each (file/family, line/scope, disposition); no "TBD" entries per AC-NFR-4-a. | T5.6 L2 | Grep "Phase 5" section; count dispositions. | MAJOR (closes AC-FR-11-a empirical) |
| PV-5.C7 | T1.3 cross-reference recorded for `recipe-feature-pipeline/SKILL.md:273` | Phase-5 migration-log entry for recipe-feature-pipeline cites T1.3 as executor (no double-edit). | T5.6 L2 | Grep "T1.3" in Phase-5 section. | MINOR |
| PV-5.C8 | `synthesize/SKILL.md` review-with-disposition recorded | Phase-5 migration-log entry for synthesize cites Q-CC-4 + ADR-0054 commitment 2 rationale (no edit). | T5.6 L2 | Grep "synthesize" in Phase-5 section. | MINOR |

### Acceptance tests scheduled for this phase

- AT-043 (AC-FR-10-b — orchestrator Step 8 invokes validator) — structural + integration / L2+L3.
- AT-044 (AC-FR-10-c — run_phase_checks dispatch includes validator with allowlist) — structural + integration / L3.
- AT-045 (AC-FR-10-d — packager invokes validator via Bash grant) — structural + integration / L3.
- AT-054 (AC-CC-4 — packager `Bash` in tools + `.claude/settings.json` allow-list entry) — structural / L1.
- AT-055 (AC-CC-5 — orchestrator gate integration in SKILL.md Step 8) — structural / L2.
- AT-047 (AC-FR-10-f — allowlist enumerated in Blueprint) — structural / L2 (Blueprint-resolved; verified at PV-5 via T5.2 dispatch flag).
- AT-048 (AC-FR-11-a — audit log enumerates every skill reviewed) — structural / L2.
- AT-049 (AC-FR-11-b — skills containing permit-prose updated) — structural / L2.

### Operational checks

- The `.claude/settings.json` allow-list entry MUST be narrow (`Bash(python3 .claude/skills/auditing-shared/scripts/validate_adr_placement.py*)`) per Q-CC-5 / ADR-0054 commitment 3 smallest-grant principle. A broader `Bash(*)` grant is a NFR violation (would surface at Architecture Audit re-pass).
- The `validator` dimension in `run_phase_checks.py` must aggregate the new validator's findings into the existing dimension (per Q-CC-7 Option A), not introduce a new dimension.

### Failure response

- C1–C4 failure (BLOCKER) → A surface isn't wired or the same-script-same-args invariant is broken. Investigate the offending surface; re-execute the relevant T5.x task; re-run PV-5.
- C5 failure (BLOCKER) → A skill remediation didn't land; identify via per-file grep; re-execute T5.4 or T5.5 as appropriate.
- C6 failure (MAJOR) → Audit-trail gap; append missing dispositions; re-run.

## PV-6 — Verification (integrated final-state check)

- **phase_id**: P-6
- **phase_name**: Integrated final-state verification (AC-OP-1 through AC-OP-5; NFR-1 through NFR-8)
- **plan_reference**: `plan-v1.md` §Phase 6 — Verification / T6.1–T6.10
- **validator_goal**: Prove every prior phase's load-bearing claim still holds at the moment PV-6 runs; empirically confirm AC-OP-1 through AC-OP-5 and NFR-1 through NFR-8 via the Plan's T6.x verification tasks.
- **when_run**: Post-T6.10 completion. PV-6 is the integrated final-state check before Rollout.
- **expected_duration**: ~15 minutes (validator runs + negative-path harness + skill-audit re-check).
- **prerequisites**: PV-0 through PV-5 all passed (drift-detection responsibility: PV-6 re-runs every prior validator's load-bearing criterion).

### Pass criteria

| ID | Description | Assertion | Source | Automation hook | Severity |
|---|---|---|---|---|---|
| PV-6.C1 | AC-OP-1 empirical: fresh pipeline-run probe confirms canonical-default behavior | `migration-log.md` T6.2 entry records simulation: orchestrator `output_adrs_dir = "adrs/"`; validator returns exit 0 + verdict PASS. | T6.2 L3 | Read migration-log entry; reproduce simulation. | BLOCKER |
| PV-6.C2 | AC-OP-2 empirical: reviewer doesn't flag canonical-only Blueprint | T6.1 records `shared-document-reviewer` invocation; JSON shows no `issue.category == "adr-placement"`. | T6.1 L3 | Re-invoke reviewer on this feature's Blueprint v1.2.0; parse JSON. | BLOCKER |
| PV-6.C3 | AC-OP-3 empirical: validator returns PASS on post-feature repo | `python3 .claude/skills/auditing-shared/scripts/validate_adr_placement.py` returns exit 0 + verdict PASS + empty findings. | T6.4 L3 | Direct validator invocation. | BLOCKER |
| PV-6.C4 | AC-OP-4 empirical: three-surface negative-path harness blocks at all 3 surfaces | T6.7 records: contrived fixture written; each of 3 surfaces returns non-zero / BLOCK / BLOCKER; fixture cleaned up. | T6.7 L3 | Re-run negative-path harness; verify each surface; verify cleanup. | BLOCKER |
| PV-6.C5 | AC-OP-5 empirical: cross-reference sweep returns zero matches for former paths | T6.6 records re-run of 32-path + 368-bare-ID pattern sets; all match-counts equal expected (0/0/preserved-count). | T6.6 L3 | Re-run patterns; verify counts. | BLOCKER |
| PV-6.C6 | NFR-2 latency confirmed over 5 invocations | T6.3 records 5 invocations of validator; average `elapsed_ms < 5000`; no individual run >5000. | T6.3 L2+L3 | Re-run 5x; compute average. | MAJOR (per PV-4.C4 severity rule) |
| PV-6.C7 | Empty feature-scoped `adrs/` directories reaped (Plan-absorbed MINOR-3) | `find working/feature -type d -name "adrs" -empty` returns 0 directories. | T6.5 L1 | Find invocation. | MINOR |
| PV-6.C8 | File-count arithmetic final-state (Plan-absorbed MINOR-2) | `adrs/` contains exactly 55 `.md` files; `adrs/superseded/` contains exactly 7 `.md` files; `adrs-migrated/` does not exist; `working/feature/*/adrs/` contains exactly 5 `.tombstone` files and zero `.md` files. | T6.6 L2 | Per-directory counts. | BLOCKER |
| PV-6.C9 | AC-CC-7 + NFR-4 empirical: skill audit completeness | T6.8 records 13 dispositions present in Phase-5 section + 3 spot-check passes. | T6.8 L3 | Re-read Phase-5 section; spot-check 3 file-level edits. | BLOCKER |
| PV-6.C10 | NFR-1 atomicity + NFR-5 history preservation verification | T6.9 records per-Phase-2-task atomicity check + `git log --follow` on 2 of the FR-8c relocations traces back to feature-scoped path. | T6.9 L3 | Re-run `git log --follow`. | MAJOR |
| PV-6.C11 | NFR-7 no-`--no-verify` audit | T6.10 records `grep -rn "no-verify"` against Plan + per-task results + validator script returns 0 matches. | T6.10 L1 | Grep. | BLOCKER |
| PV-6.C12 | NFR-8 dependency-posture audit | T6.10 records validator imports = stdlib-only (argparse, pathlib, json, sys, time). | T6.10 L2 | Grep imports. | BLOCKER |
| PV-6.C13 | Drift-detection: every prior validator's BLOCKER criterion still holds | Re-run PV-1.C1, PV-2a.C1, PV-2b.C4–C8, PV-2c.C1, PV-2d.C1, PV-3.C2–C4, PV-4.C3, PV-5.C1–C5 against the current repo state. All must still PASS. | PV-1 through PV-5 re-execution | Scripted PV re-runner. | BLOCKER |

### Acceptance tests scheduled for this phase

- AT-001 (AC-US-1-a fresh pipeline-run probe) — empirical-run / L3.
- AT-002 (AC-US-1-b three-surface enforcement) — negative-path / L3.
- AT-003 (AC-US-2-a reviewer doesn't flag) — review-gate / L3.
- AT-005, AT-006 (AC-US-3-a/b — packager passes/blocks) — integration / L3.
- AT-007, AT-008 (AC-US-4-a/b — future-run orchestrator default + skills present canonical-only) — structural+empirical / L2+L3.
- AT-010 (AC-FR-1-b — PKG-BLOCKER-001 not raised; replacement validator passes) — integration / L3.
- AT-012 (AC-FR-2-b — reviewer no flag) — review-gate / L3.
- AT-035 (AC-FR-8d-3 — validator doesn't allowlist `adrs-migrated/`) — structural / L1.
- AT-046 (AC-FR-10-e — negative-path validator returns non-zero) — negative-path / L3.
- AT-050 (AC-FR-11-c — Blueprint records audit findings) — structural / L2.
- AT-053 (AC-CC-3 — run_phase_checks dispatch + validator dimension rollup) — integration / L3.
- AT-056 (AC-CC-6 — no CLAUDE.md addition) — structural / L1.
- AT-057 (AC-CC-7 — skill audit completeness) — structural / L2.
- AT-058 (AC-OP-1) through AT-062 (AC-OP-5) — empirical / L3.
- AT-063 (AC-NFR-1-a) through AT-076 (AC-NFR-8-a) — verification batch / L1–L3.

### Operational checks

- PV-6 is the only validator with drift-detection responsibility (PV-6.C13). If any prior validator's BLOCKER criterion has regressed between its original pass and PV-6 invocation, the regression must be investigated before Rollout.
- The negative-path harness in T6.7 MUST clean up the fixture; PV-6 should fail if `working/feature/test-fixture/` exists at validator time.
- The 24h-stability re-run of T6.4 (validator scan stability check, T6.4 L3) is OPTIONAL for the PV-6 gate; surface as MINOR if deferred.

### Failure response

- C1–C5 (BLOCKER) failure → The corresponding AC-OP-N is not empirically met. Identify which underlying phase or surface regressed. Re-execute the Plan task that produced the regression. Do NOT advance to Rollout.
- C8 failure (BLOCKER) → File-count arithmetic mismatch indicates a Phase 2 / Phase 3 / Phase 5 gap. Investigate via diff of expected vs. actual file lists; re-execute affected sub-task.
- C13 failure (drift) → A prior validator's load-bearing criterion has regressed. Investigate the regression's source commit; restore + re-execute the affected phase's tasks.
- C11/C12 failure (BLOCKER) → NFR-7 / NFR-8 violation; remove the offending content; re-run.

## PV-R — Rollout (closeout + deferral closure)

- **phase_id**: P-R
- **phase_name**: Closeout + deferral closure
- **plan_reference**: `plan-v1.md` §Rollout — Closeout + deferral closure
- **validator_goal**: Prove the `devcontainer-mcp-provisioning-r1` Gate-6 PKG-BLOCKER-001 deferral is closed and informed stakeholders have been notified (2 features).
- **when_run**: Post-TR.2 completion.
- **expected_duration**: < 2 minutes.
- **prerequisites**: PV-6 passed.

### Pass criteria

| ID | Description | Assertion | Source | Automation hook | Severity |
|---|---|---|---|---|---|
| PV-R.C1 | `devcontainer-mcp-provisioning-r1` Gate-6 deferral closure note appended | `grep -rn "adr-placement-mechanism-repair-r1" working/feature/devcontainer-mcp-provisioning-r1/` returns ≥1 match in a Gate-6 audit-trail file with the closure note. | TR.1 L1+L2 | Grep. | BLOCKER |
| PV-R.C2 | Informed-stakeholder notification: frontend-design-knowledge-r1 | Notification note appended to `working/feature/frontend-design-knowledge-r1/`; cites ADR-0024 status-lift disposition. | TR.2 L1+L2 | `grep -n "adr-placement-mechanism-repair-r1" working/feature/frontend-design-knowledge-r1/` returns ≥1 match. | MAJOR |
| PV-R.C3 | Informed-stakeholder notification: issue-capture-mechanism-r1 | Notification note appended to `working/feature/issue-capture-mechanism-r1/`; cites (a) FR-8c relocations + `.tombstone` notes; (b) FR-8b renumbers ADR-0044→0051, ADR-0045→0052; (c) 368-occurrence sweep impact. | TR.2 L1+L2 | Grep + content read. | MAJOR |
| PV-R.C4 | Deferral chain reachable from original PKG-BLOCKER-001 entry | Future readers of the original PKG-BLOCKER-001 entry in `devcontainer-mcp-provisioning-r1/` can follow the closure note to this feature's completion. | TR.1 L3 | Manual traceability check. | MINOR |

### Acceptance tests scheduled for this phase

- (No new AT-NNN tests; Rollout closes communications per PRD §Communication plan.)

### Operational checks

- The closure note MUST cite the FR-10-d replacement (validator-backed canonical-only check) so future readers understand WHY the deferral is closeable.
- If any informed-stakeholder feature folder has been archived/moved between the Plan-authoring date and PV-R execution date, surface to operator for revised notification target.

### Failure response

- C1 failure (BLOCKER) → Re-execute TR.1; the deferral is not yet closed.
- C2/C3 failure (MAJOR) → Re-execute TR.2; communication step incomplete.

## Cross-validator coordination

### Critical-path validators

The validators whose failure most delays the feature, ranked by Plan critical-path proximity:

1. **PV-3** — blocks PV-4 (validator authoring); T3.3 is the single largest task in the Plan (368 bare-ID disambiguations); a PV-3 failure is the highest-cost regression to recover from.
2. **PV-2d** — gates PV-2b.2 (renumber baseline computation per ADR-0053) AND PV-3. A regression here cascades to two downstream phases.
3. **PV-4** — gates PV-5 (no surface can be wired before the validator script exists). A validator-script regression invalidates all three surface wirings.
4. **PV-6** — integrated final-state check; the most ACs are scheduled here; drift-detection responsibility lives here.

### Parallelizable validator checks (intra-validator)

- Within PV-1: C1, C2, C3, C4, C5 are independent grep checks; can run concurrently.
- Within PV-2a, PV-2c, PV-2d: per-ADR-ID checks are independent; can run concurrently per ID.
- Within PV-5: C1, C2, C3 (surface wiring) parallel with C5 (skill audit).
- Within PV-6: C1–C5 (AC-OP-N empirical), C9 (skill audit), C11 (no-`--no-verify`), C12 (deps) can run concurrently. C13 (drift-detection) sequences last (depends on all prior validators' state).

### Parallelizable validators (inter-validator)

Per the Plan §Cross-Phase Dependencies, these validators can run concurrently (their underlying phases are parallelizable):

- PV-2a, PV-2b.1, PV-2c, PV-2d.1 (parallelizable Phase 2 sub-tasks).
- PV-2d.2, PV-2d.3 can run alongside PV-2d.1 (different ID ranges); PV-2d.4 sequences last in Phase 2d.
- PV-2b.2 sequences after PV-2c AND PV-2d.4 per ADR-0053.

### Shared validator infrastructure

| Resource | Used by | Notes |
|---|---|---|
| `migration-log.md` (audit substrate) | PV-0 through PV-R | The Plan's single audit substrate; every validator reads or asserts entries here. |
| `bare-id-inventory.json` | PV-3, PV-6.C5 | Authored at T3.1; consumed by T3.3, T3.4, T6.6. |
| `codebase-analysis.json` (IN-008) | PV-0, PV-3, PV-6.C5 | Path-form inventory source. |
| `validate_adr_placement.py` | PV-4, PV-5, PV-6 | Authored at T4.1; the load-bearing script for FR-10. |
| `smoke_test_auditing_shared.py` | PV-4 | The validator's negative-path harness template. |
| Negative-path fixture (`working/feature/test-fixture/`) | PV-4 (smoke), PV-6 (T6.7 harness) | Must be cleaned up after each use; orphaned fixtures will falsify positive-path tests. |

### Validator runbook (operator-facing)

The intended runtime procedure for a human operator running these validators during a live execution:

1. **Per-phase dispatch.** After the orchestrator (or human operator) marks all tasks in a phase complete, dispatch the corresponding Phase Validator. Phase advance is gated on PASS verdict.
2. **PASS / WARNING / BLOCK verdict.**
   - **PASS** — every criterion satisfies its severity rule (no BLOCKER fails; MAJOR/MINOR can be present-and-deferred with rationale).
   - **WARNING** — at least one MAJOR fails with operator deferral rationale recorded.
   - **BLOCK** — at least one BLOCKER fails; phase advance forbidden; trigger Phase rollback.
3. **Drift-detection at PV-6.** PV-6 is unique: it re-runs every prior validator's BLOCKER criterion. If any has regressed between original pass and PV-6 invocation, PV-6 BLOCKs even if all its own criteria pass.
4. **Audit-trail discipline.** Each validator invocation appends its verdict + criterion-by-criterion outcome to `migration-log.md` under a dedicated `## Phase Validator PV-X` section. This is the load-bearing audit trail for cross-artifact reviewers.
5. **Re-validation after rollback.** If a phase rollback is triggered, the affected validator MUST be re-run; subsequent validators that already passed against the pre-rollback state MUST also be re-run (drift may have been introduced).

## Update History

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-05-25 | test-phase-validator-author | Initial Phase Validators document composed from Plan v1.0.1 (8 internal phases + Rollout). 11 validator entries: PV-0 (Discovery+Setup), PV-1 (operator-file repairs), PV-2a/2b/2c/2d (4 sub-validators for Phase 2 sub-phases per the canonical template's special handling), PV-3 (cross-reference sweep), PV-4 (validator authoring + smoke), PV-5 (wiring + skill audit), PV-6 (integrated final-state check with drift-detection per the template's PV-6 special semantics), PV-R (Rollout). Per-validator criterion-by-criterion severity tagging; AT-NNN cross-references; automation hooks specified as concrete commands. PV-2b is internally split into PV-2b.1 (T2b.1 status-lift) and PV-2b.2 (T2b.2 renumber) because T2b.2 sequences after PV-2c + PV-2d per ADR-0053 v1.0.1 algorithm. PV-6.C13 codifies the drift-detection re-run discipline. |
