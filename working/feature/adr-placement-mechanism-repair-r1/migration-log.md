---
doc_type: migration-log
feature_slug: adr-placement-mechanism-repair-r1
version: 1.0.0
created: 2026-05-25
purpose: Plan-execution audit substrate. Per-task per-ADR + per-file dispositions appended at each Phase 1-5 task; Phase-6 verification records empirical confirmations.
---

# Migration Log — adr-placement-mechanism-repair-r1

## Phase 0 — Setup

_(no entries yet — populated as tasks land)_

## Phase 1 — Operator-file repairs (FR-1..FR-5)

| task_id | target_file | action | result |
|---------|-------------|--------|--------|
| T1.1 | .claude/agents/finalize-deliverable-packager.md | replace dual-location BLOCKER prose with FR-10-d anchor (parent-orchestrator applied; sub-agent Edit soft-blocked by auto-mode self-mod classifier) | COMPLETED |
| T1.2 | .claude/agents/shared-document-reviewer.md | delete dual-location line; preserve canonical-only statement | COMPLETED |
| T1.3 | .claude/skills/recipe-feature-pipeline/SKILL.md | annotate output_adrs_dir default + pass-through prose per ADR-0036 | COMPLETED |
| T1.4 | .claude/agents/design-composer.md | update 3 output_adrs_dir mentions + add Test-only override subsection per ADR-0036 | COMPLETED |

### Phase 1 closeout (T1.5)

- Dual-location prose check: one match across all 4 files — `finalize-deliverable-packager.md` line 59 contains the phrase "The dual-location convention has been retired per ADR-0036" (historical-retirement citation, not a prescription). Zero prescriptive dual-location matches. Files `shared-document-reviewer.md`, `design-composer.md`, and `recipe-feature-pipeline/SKILL.md` return zero matches.
- ADR-0036 citation check: 9 citations across the 4 files (finalize-deliverable-packager.md: 2; design-composer.md: 5; shared-document-reviewer.md: 1; recipe-feature-pipeline/SKILL.md: 1).
- Cross-file convergence: all 4 files agree on canonical-only ADR placement. finalize-deliverable-packager.md §3 states canonical-root is the single valid location; shared-document-reviewer.md line 471 instructs reviewers not to flag absence of a working/feature mirror; design-composer.md lines 48/59/139/197 anchor output_adrs_dir to adrs/ with test-only override discipline; recipe-feature-pipeline/SKILL.md line 273 annotates the default as "adrs/" per ADR-0036. No inter-file contradictions found.
- AT-004 + AT-059 first-pass: PARTIAL — intent satisfied (no file prescribes dual-location; all files citing the convention reference ADR-0036; no cross-file contradictions found), but the literal AT-004 expected outcome requires `grep -rn "dual-location" .claude/agents/ .claude/skills/recipe-feature-pipeline/` to return zero matches. One match exists in finalize-deliverable-packager.md line 59 as a retirement-citation sentence. Recommend T1.1 follow-up to rephrase to "The convention requiring two locations has been retired per ADR-0036" or equivalent to eliminate the literal token and achieve a clean zero-match grep. Full PASS gated on that one-line adjustment.

## Phase 2a — Byte-identical dedupes (12 ADRs: 0026, 0028, 0029, 0030, 0031, 0037, 0038, 0039, 0040, 0041, 0042, 0043)

| adr_id | byte_equality_check | feature_scoped_source | action | result |
|--------|---------------------|-----------------------|--------|--------|
| ADR-0026 | byte-identical-confirmed | working/feature/audit-machinery-fixes-r1/adrs/ADR-0026-audit-machinery-fixes-v4-4-1.md | git rm | COMPLETED |
| ADR-0028 | byte-identical-confirmed | working/feature/pipeline-skill-design-fixes-r1/adrs/ADR-0028-skill-design-fixes-v4-5-0.md | git rm | COMPLETED |
| ADR-0029 | byte-identical-confirmed | working/feature/audit-findings-remediation-r1/adrs/ADR-0029-no-silent-scope-changes-principle.md | git rm | COMPLETED |
| ADR-0030 | byte-identical-confirmed | working/feature/audit-findings-remediation-r1/adrs/ADR-0030-mechanism-alpha-pedagogical-marker-justification.md | git rm | COMPLETED |
| ADR-0031 | byte-identical-confirmed | working/feature/audit-findings-remediation-r1/adrs/ADR-0031-auditing-shared-skill-module.md | git rm | COMPLETED |
| ADR-0037 | byte-identical-confirmed | working/feature/devcontainer-mcp-provisioning-r1/adrs/ADR-0037-mcp-events-jsonl-transition-surfacing.md | git rm | COMPLETED |
| ADR-0038 | byte-identical-confirmed | working/feature/devcontainer-mcp-provisioning-r1/adrs/ADR-0038-codebase-analysis-schema-v1-1-0.md | git rm | COMPLETED |
| ADR-0039 | byte-identical-confirmed | working/feature/devcontainer-mcp-provisioning-r1/adrs/ADR-0039-credential-redaction-posture.md | git rm | COMPLETED |
| ADR-0040 | byte-identical-confirmed | working/feature/devcontainer-mcp-provisioning-r1/adrs/ADR-0040-serena-narrowed-always-on.md | git rm | COMPLETED |
| ADR-0041 | byte-identical-confirmed | working/feature/devcontainer-mcp-provisioning-r1/adrs/ADR-0041-install-mechanism-hybrid.md | git rm | COMPLETED |
| ADR-0042 | byte-identical-confirmed | working/feature/devcontainer-mcp-provisioning-r1/adrs/ADR-0042-auditing-mcp-family-graduation.md | git rm | COMPLETED |
| ADR-0043 | byte-identical-confirmed | working/feature/devcontainer-mcp-provisioning-r1/adrs/ADR-0043-auditing-mcp-gate-6-hard-gate.md | git rm | COMPLETED |

## Phase 2b — Status-lift dedupe + numbering-collision renumber

| adr_id | sub_action | source | target | original_id | result |
|--------|------------|--------|--------|-------------|--------|
| ADR-0024 | status-lift-only divergence | working/feature/frontend-design-knowledge-r1/adrs/ADR-0024-frontend-design-knowledge-corpus-structure.md | adrs/ADR-0024-frontend-design-knowledge-corpus-structure.md | N/A | COMPLETED |

## Phase 2c — Feature-scoped relocations (ADRs 0046–0050)

| adr_id | source | target | tombstone_path | result |
|--------|--------|--------|----------------|--------|
| ADR-0046 | working/feature/issue-capture-mechanism-r1/adrs/ | adrs/ | ADR-0046.tombstone | COMPLETED |
| ADR-0047 | working/feature/issue-capture-mechanism-r1/adrs/ | adrs/ | ADR-0047.tombstone | COMPLETED |
| ADR-0048 | working/feature/issue-capture-mechanism-r1/adrs/ | adrs/ | ADR-0048.tombstone | COMPLETED |
| ADR-0049 | working/feature/issue-capture-mechanism-r1/adrs/ | adrs/ | ADR-0049.tombstone | COMPLETED |
| ADR-0050 | working/feature/issue-capture-mechanism-r1/adrs/ | adrs/ | ADR-0050.tombstone | COMPLETED |

## Phase 2d — adrs-migrated/ consolidation

Sub-procedures: i (0001-0006, 0008-0010), ii (0011-0017), iii (0018), iv (0007)

| adr_id | sub_procedure | source_variant_files | canonical_target | superseded_archive | result |
|--------|---------------|----------------------|------------------|--------------------|--------|
| ADR-0001 | (i) no-collision | ADR-0001-orchestrator-placement.md, ADR-0001-orchestrator-placement-pre-naming-convention.md, ADR-0001-orchestrator-placement-pre-template-migration.md | adrs/ADR-0001-orchestrator-placement.md | N/A | COMPLETED |
| ADR-0002 | (i) no-collision | ADR-0002-critique-1-discipline.md, ADR-0002-critique-1-discipline-pre-naming-convention.md, ADR-0002-critique-1-discipline-pre-template-migration.md | adrs/ADR-0002-critique-1-discipline.md | N/A | COMPLETED |
| ADR-0003 | (i) no-collision | ADR-0003-critique-2-discipline.md, ADR-0003-critique-2-discipline-pre-naming-convention.md, ADR-0003-critique-2-discipline-pre-template-migration.md | adrs/ADR-0003-critique-2-discipline.md | N/A | COMPLETED |
| ADR-0004 | (i) no-collision | ADR-0004-test-split.md, ADR-0004-test-split-pre-naming-convention.md, ADR-0004-test-split-pre-template-migration.md | adrs/ADR-0004-test-split.md | N/A | COMPLETED |
| ADR-0005 | (i) no-collision | ADR-0005-append-only-supersession.md, ADR-0005-append-only-supersession-pre-naming-convention.md, ADR-0005-append-only-supersession-pre-template-migration.md | adrs/ADR-0005-append-only-supersession.md | N/A | COMPLETED |
| ADR-0006 | (i) no-collision | ADR-0006-synthesis-inlined.md, ADR-0006-synthesis-inlined-pre-naming-convention.md, ADR-0006-synthesis-inlined-pre-template-migration.md | adrs/ADR-0006-synthesis-inlined.md | N/A | COMPLETED |
| ADR-0008 | (i) no-collision | ADR-0008-issue-ledger-scope.md, ADR-0008-issue-ledger-scope-pre-naming-convention.md, ADR-0008-issue-ledger-scope-pre-template-migration.md | adrs/ADR-0008-issue-ledger-scope.md | N/A | COMPLETED |
| ADR-0009 | (i) no-collision | ADR-0009-rationale-brief-discipline.md, ADR-0009-rationale-brief-discipline-pre-naming-convention.md, ADR-0009-rationale-brief-discipline-pre-template-migration.md | adrs/ADR-0009-rationale-brief-discipline.md | N/A | COMPLETED |
| ADR-0010 | (i) no-collision | ADR-0010-knowledge-skill-frontmatter-correction.md, ADR-0010-knowledge-skill-frontmatter-correction-pre-naming-convention.md, ADR-0010-knowledge-skill-frontmatter-correction-pre-template-migration.md | adrs/ADR-0010-knowledge-skill-frontmatter-correction.md | N/A | COMPLETED |
| ADR-0011 | (ii) archive-wins | adrs-migrated/ADR-0011-documentation-criteria-canonical-skill.md, adrs-migrated/ADR-0011-documentation-criteria-canonical-skill-pre-naming-convention.md | adrs/ADR-0011-documentation-criteria-canonical-skill.md | adrs/superseded/ADR-0011-pre-consolidation-canonical.md | COMPLETED |
| ADR-0012 | (ii) archive-wins | adrs-migrated/ADR-0012-prd-stage.md, adrs-migrated/ADR-0012-prd-stage-pre-naming-convention.md | adrs/ADR-0012-prd-stage.md | adrs/superseded/ADR-0012-pre-consolidation-canonical.md | COMPLETED |
| ADR-0013 | (ii) archive-wins | adrs-migrated/ADR-0013-blueprint-template-adoption.md, adrs-migrated/ADR-0013-blueprint-template-adoption-pre-naming-convention.md | adrs/ADR-0013-blueprint-template-adoption.md | adrs/superseded/ADR-0013-pre-consolidation-canonical.md | COMPLETED |
| ADR-0014 | (ii) archive-wins | adrs-migrated/ADR-0014-adr-template-adoption-and-migration.md, adrs-migrated/ADR-0014-adr-template-adoption-and-migration-pre-naming-convention.md | adrs/ADR-0014-adr-template-adoption-and-migration.md | adrs/superseded/ADR-0014-pre-consolidation-canonical.md | COMPLETED |
| ADR-0015 | (ii) archive-wins | adrs-migrated/ADR-0015-ears-acceptance-criteria.md, adrs-migrated/ADR-0015-ears-acceptance-criteria-pre-naming-convention.md | adrs/ADR-0015-ears-acceptance-criteria.md | adrs/superseded/ADR-0015-pre-consolidation-canonical.md | COMPLETED |
| ADR-0016 | (ii) archive-wins | adrs-migrated/ADR-0016-per-layer-fanout-composer-fanin.md, adrs-migrated/ADR-0016-per-layer-fanout-composer-fanin-pre-naming-convention.md | adrs/ADR-0016-per-layer-fanout-composer-fanin.md | adrs/superseded/ADR-0016-pre-consolidation-canonical.md | COMPLETED |
| ADR-0017 | (ii) archive-wins | adrs-migrated/ADR-0017-document-reviewer-integration.md, adrs-migrated/ADR-0017-document-reviewer-integration-pre-naming-convention.md | adrs/ADR-0017-document-reviewer-integration.md | adrs/superseded/ADR-0017-pre-consolidation-canonical.md | COMPLETED |
| ADR-0018 | (iii) canonical-wins | adrs-migrated/ADR-0018-* variants | adrs/ADR-0018-codebase-analysis-schema.md (retained) | N/A | COMPLETED |

## Phase 3 — Cross-reference sweep

| task_id | file | line | before | after | sweep_type |
|---------|------|------|--------|-------|------------|
| _(populated as tasks land in this phase)_ | | | | | |

## Phase 4 — Validator authoring

| task_id | file_authored | LOC | test_result |
|---------|---------------|-----|-------------|
| _(populated as tasks land in this phase)_ | | | |

## Phase 5 — Validator wiring + skill audit remediation

| task_id | file_edited | wiring_surface_or_audit_finding | result |
|---------|-------------|----------------------------------|--------|
| _(populated as tasks land in this phase)_ | | | |

## Phase 6 — Verification

| check_id | description | empirical_result | references_test |
|----------|-------------|------------------|-----------------|
| _(populated as tasks land in this phase)_ | | | |

## Phase R — Rollout

| task_id | feature_target | notification_path | result |
|---------|----------------|-------------------|--------|
| _(populated as tasks land in this phase)_ | | | |
