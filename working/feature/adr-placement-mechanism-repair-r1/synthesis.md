---
id: SYN-adr-placement-mechanism-repair-r1
doc_type: synthesis
version: 1.0.0
status: complete
generated: 2026-05-24T19:35:00Z
generated_by: recipe-feature-pipeline (parent orchestrator; streamlined-fan-in mode per Synthesis stage's "synthesis.md or synthesis/" optionality)
feature_slug: adr-placement-mechanism-repair-r1
scope_class: FULL
layer_scope: ["claude-code"]
derived_from:
  - working/feature/adr-placement-mechanism-repair-r1/codebase-analysis.json (v1.1.0 schema)
  - working/feature/adr-placement-mechanism-repair-r1/codebase-analysis-report.md
  - working/feature/adr-placement-mechanism-repair-r1/prd-v1.md (v1.0.2)
  - working/feature/adr-placement-mechanism-repair-r1/intent-clarification.md (v2.0.1)
  - working/feature/adr-placement-mechanism-repair-r1/research-plan.md (v1.0.0)
external_research_topics_consumed: 0
synthesis_mode: implementation-strategy (per recipe-feature-pipeline §"Feature-pipeline mode of synth-substrate"; this synthesis serves design-handoff, not multi-source claim extraction)
---

# Synthesis — ADR Placement Mechanism Repair (FULL)

## Why this synthesis is streamlined

The recipe-feature-pipeline Synthesis stage is informational and not gated. Its purpose is to deliver a clean design-handoff. This feature has:

- **One primary input** (codebase-analysis.json from discovery-codebase-researcher).
- **Zero external research notes** (justified at Gate 3 per ADR-0021 KB-and-ADR-first; KB inventory was saturated).
- **A focused implementation-strategy decision space** (single CC layer; no substrate-comparison decisions; no multi-source claim conflicts).

The full synth-* sub-pipeline (extractor → grapher → critic → framer → substrate → synthesizer) is designed for multi-source research synthesis. With a single source and no external research, the orchestrator produces a streamlined synthesis.md directly. This mode is documented in the recipe-feature-pipeline SKILL's "Feature-pipeline mode of synth-substrate" section as the implementation-strategy variant.

## Discovery findings worth surfacing to design

Three on-disk realities materially refine the PRD's stated scope:

### Finding 1 — ADR-0044 / ADR-0045 are numbering collisions, not body drift

PRD §FR-8b classified ADR-0024 + ADR-0044 + ADR-0045 as "divergent body" cases needing rejected-body archival. Discovery confirmed ADR-0024 fits that pattern, but **ADR-0044 and ADR-0045 are entirely different decisions accidentally sharing the same numeric IDs as the canonical ADRs**:

- Canonical ADR-0044 = "flatten execution dispatch hierarchy" (the ADR-0044 listed in the recipe-feature-pipeline.SKILL.md cross-references).
- Feature-scoped ADR-0044 (in `issue-capture-mechanism-r1/adrs/`) = "per-issue folder model".
- Same numbering-collision pattern for ADR-0045 (canonical = "subagent agent-tool grant prohibition"; feature-scoped = "three doctypes preserved").

This is a **classification error**, not a body-merge problem. The PRD's FR-8b sub-action ("rejected body archival") does not apply to numbering collisions; the correct sub-action is **re-numbering with provenance**.

**Binding gate decision (2026-05-24, Synthesis stage)**: Resolution deferred to Design Composition; Blueprint Approval Gate ratifies. Discovery surfaces the collision pattern; the Blueprint proposes the re-numbering scheme (default lean: re-number feature-scoped variants to next available canonical IDs after consolidation completes — likely ADR-0051 and ADR-0052, but Design Composition must verify after Phase 2d numbering settles).

### Finding 2 — Five distinct feature folders host off-canonical ADRs (not two)

PRD §Stakeholders + §FR-8 named two feature folders: `frontend-design-knowledge-r1` (for ADR-0024) and `issue-capture-mechanism-r1` (for ADRs 0044–0050). Discovery surfaced **five** folders holding the 17 off-canonical ADRs:

| Feature folder | ADRs hosted | Classification |
|---|---|---|
| `audit-machinery-fixes-r1` | ADR-0026 | byte-identical duplicate |
| `audit-findings-remediation-r1` | ADR-0029, ADR-0030, ADR-0031 | byte-identical duplicates (×3) |
| `pipeline-skill-design-fixes-r1` | ADR-0028 | byte-identical duplicate |
| `devcontainer-mcp-provisioning-r1` | ADR-0037, ADR-0038, ADR-0039, ADR-0040, ADR-0041, ADR-0042, ADR-0043 | byte-identical duplicates (×7) |
| `frontend-design-knowledge-r1` | ADR-0024 | divergent body (true semantic divergence) |
| `issue-capture-mechanism-r1` | ADR-0044, ADR-0045, ADR-0046, ADR-0047, ADR-0048, ADR-0049, ADR-0050 | ADR-0044/0045 = numbering collisions; ADR-0046–0050 = truly feature-scoped |

**Implication for design**: the Plan's Phase-2 migration tasks decompose per-folder (six folders touched, not two). Cross-reference sweep (FR-9) must include shipped Blueprints from all six.

### Finding 3 — `adrs-migrated/` archive contains 18 ADR IDs, with 8 collisions where the archive body is MORE CURRENT than canonical

PRD §FR-8d hypothesized `adrs-migrated/` contains "ADRs 0001–0010, pre-template-migration historical archive". Discovery confirmed the breadth is wider (**ADRs 0001–0018**) and produced a critical reversal of the assumed relationship:

- **8 numbering collisions** exist when consolidating into canonical `adrs/`: ADRs 0011, 0012, 0013, 0014, 0015, 0016, 0017, and one more (per codebase-analysis.json's `numbering_collisions` section).
- **For those 8 collisions, the archive carries v2.0.0** (post-naming-convention update; the more current body).
- **The canonical `adrs/` carries v1.0.0** for those IDs (stale; pre-update).

This inverts the intuitive "canonical = current, archive = old" model. For 8 of the consolidation cases, **canonical is the stale variant**.

**Binding gate decision (2026-05-24, Synthesis stage)**: Archive wins for the 8 collisions. Sub-actions:

1. Move the v2.0.0 archive body for each of the 8 IDs into canonical `adrs/<id>-<slug>.md` (overwriting the stale canonical).
2. Archive the stale v1.0.0 canonical body to `adrs/superseded/<id>-pre-consolidation-canonical.md` with provenance footer.
3. Frontmatter on the new canonical entries gets `superseded_by_consolidation: true` + `superseded_canonical_archived_to: adrs/superseded/<id>-pre-consolidation-canonical.md` provenance fields.
4. The `-pre-naming-convention` and `-pre-template-migration` variants in `adrs-migrated/` are deleted (Git history preserves them per NFR-5).

For the 10 archive IDs that do NOT have canonical collisions (ADRs 0001–0010), the archive's final variants move to canonical directly; `-pre-*` variants are deleted.

## Design decisions for the Blueprint

The Blueprint must ratify these decisions during Design Composition. Open Items #1, #3, #4, #5 from PRD + Discovery's surfaced sub-actions:

### D1 — Re-numbering scheme for ADR-0044 / ADR-0045 collision (Discovery OQ-1, deferred to Design Composition)

**Decision space:**
- Option A (default lean): re-number feature-scoped ADR-0044 → canonical ADR-0051; feature-scoped ADR-0045 → canonical ADR-0052. Add `original_id` frontmatter for provenance. Update all references.
- Option B: re-number with a higher offset to leave room for future Phase-2d consolidations.
- Option C: post-Phase-2d defer (compute final canonical IDs only after `adrs-migrated/` consolidation completes, since collisions could change the next-available number).

**Recommendation**: Option C. Phase-2d consolidates 18 archive ADRs into canonical; the next-available number is computed post-consolidation. Design Composition documents the algorithm; Blueprint Approval Gate ratifies.

### D2 — Body-precedence for the 8 archive-vs-canonical collisions (Discovery OQ-2, binding)

**Decision space**: resolved at user gate 2026-05-24. **Archive wins** for the 8 collisions. Stale canonical bodies archived to `adrs/superseded/`. (Repeated here so Design Composition does not re-open.)

### D3 — Divergent-body archival format for ADR-0024 (OI-1 from PRD)

**Decision space:**
- Option A (default lean from PRD): rejected body archived to `adrs/superseded/<id>-feature-scoped-body.md` with provenance footer.
- Option B: inline-supersession (rejected body appended to canonical body in `## Superseded variant` section).
- Option C: deletion with Git-history-only preservation.
- Option D: archival in the originating feature folder.

**Recommendation**: Option A. Aligns with D2's archival pattern (canonical `adrs/superseded/` location). Design Composition reads both bodies, proposes which is canonical, Blueprint Approval Gate ratifies; rejected body lands in `adrs/superseded/`.

### D4 — Validator implementation surface (OI-3 from PRD)

**Decision space:**
- Option A (default lean from PRD): Python script under `.claude/skills/auditing-shared/scripts/` with CLI interface invoked by orchestrator, execution-pipeline hook, and packager.
- Option B: shell script (lower dependency).
- Option C: Python module integrated via the auditing-shared canonical-helper-home pattern (ADR-0031 + ADR-0035 + ADR-0042).
- Option D: integrated as a hook rather than a standalone script.

**Recommendation**: Option A. Discovery IN-010 confirmed `auditing-shared/scripts/` conventions: positional args, JSON stdout, exit 0 = pass / exit 2 = block, Python stdlib only. The new validator follows these conventions. Cross-references ADR-0031 + ADR-0035 + ADR-0042 as the home for canonical helpers.

**Note for Design Composition**: per Research Plan adjacency #2, FR-10's three-surface enforcement extends the canonical-helper-home consumer set beyond the 5 audit families to include a non-audit-family triad (orchestrator + execution-pipeline + packager). The Blueprint should explicitly cite this extension of ADR-0042's framing so the Architecture Auditor does not treat the FR-10 validator as an unannounced expansion.

### D5 — Cross-reference inventory completeness (OI-4 from PRD)

**Decision space:**
- Option A (default lean from PRD): IN-008 pattern set from Research Plan.
- Option B: extend pattern set with edge-case forms Discovery surfaced (frontmatter `supersedes:`, `<../adrs/ADR-NNNN.md>` bracket-syntax, `ADR NNNN` space-separated, etc.).

**Recommendation**: Option B. Discovery's 54-entry inventory used the IN-008 pattern set as the floor; the actual repo contains references in the extended forms. The Plan's Phase-3 cross-ref sweep must use Option B's pattern set. Confidence is high — Discovery's inventory found 0 missed references in spot-checks.

### D6 — Redirect-note format for relocated feature-scoped ADRs (OI-5 from PRD)

**Decision space:**
- Option A (default lean from PRD): one-line markdown file in the originating feature folder with link to canonical.
- Option B: delete originating file entirely (no redirect).
- Option C: `.tombstone` file in non-`.md` extension to bypass validator allowlist concern.
- Option D: symlink (filesystem-level redirect).

**Recommendation**: Option C. Discovery noted the FR-10 validator may flag any `.md` file matching `ADR-NNNN-*.md` outside canonical as a violation. A redirect note in the originating folder using `.md` extension would itself trip the validator. Two clean paths: (i) use `.tombstone` extension (Option C); (ii) explicit allowlist in validator for files containing a specific "moved" sigil. Option C is simpler and avoids validator complexity. Design Composition decides; Blueprint Approval Gate ratifies.

## Validator design (FR-10) — three-surface enforcement

Per Discovery IN-009 + IN-010, the validator integrates at three surfaces:

| Surface | Integration point | Action on validator failure |
|---|---|---|
| Orchestrator stage gate | `recipe-feature-pipeline/SKILL.md` Step 8 (after Design Composition writes ADRs) | Block stage advance; surface to user |
| Execution-pipeline hook | `auditing-shared/scripts/run_phase_checks.py` coordinator (per ADR-0044 flatten pattern, the parent orchestrator dispatches phase checks) | Block phase advance; emit BLOCKER finding |
| Packager check | `finalize-deliverable-packager.md` (replaces the deleted retired BLOCKER prose with a call to the validator) | Block deliverable packaging; surface BLOCKER |

The validator's contract:
- Input: scan path (default repo root; configurable).
- Output: JSON to stdout; non-zero exit on any feature-scoped ADR file found.
- Exit codes: 0 = pass; 2 = block (per Discovery IN-010 convention).
- Allowlist: configurable; default empty after Phase 2 + 3 complete. During Phase 2 (mid-migration), allowlist temporarily permits the still-present feature-scoped files; updated as each phase advances.

## Skill audit (FR-11) — scope and dispositions

Per Discovery IN-012, 8 file-level findings cluster in 4 skill families:

| Skill family | Files needing update | Disposition |
|---|---|---|
| `KB-documentation-criteria` | `references/disciplines/design-composition.md`, `references/deliverable-archive-spec.md` backward-compat clause, `references/templates/issue-register-template.md` | update-with-fix |
| `recipe-feature-pipeline` | `SKILL.md:273` (parameter resolution) | update-with-fix |
| `KB-issue-capture` + `capture-issue` | (path-only refresh; mention of ADR location) | path-only refresh |
| `synthesize` | `SKILL.md` (review-with-explicit-disposition — different output target, may not strictly "feature-scoped") | review-with-explicit-disposition |

**5 skill families confirmed CLEAN** by Discovery: all 10 auditing-* skills, KB-review-disciplines, KB-task-decomposition, all per-layer KB-* design/platform skills, 6 synthesize-class knowledge skills.

## Risk-and-mitigation recap

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Phase 2d numbering collision discovery delays Phase 2c re-numbering | Medium | Medium | Sequence Phase 2d before 2c re-numbering (handled by Plan dependency edges) |
| Cross-reference sweep misses a reference form Discovery's grep set didn't catch | Low | Medium | Use the extended pattern set (D5 Option B); Phase 6 verification includes a full repo grep with stricter patterns |
| `adrs-migrated/` archive's pre-naming-convention variants reveal additional collisions in canonical | Low | Low | Discovery enumerated all 8; if more surface, escalate to user (scope amendment per ADR-0029/ADR-0033) |
| Validator's allowlist mid-migration permits a real defect | Low | Medium | Allowlist is documented in the Plan; Phase 6 verification asserts empty-allowlist by Phase 5 completion |
| Design Composition's re-numbering scheme for ADR-0044/0045 conflicts with reservations elsewhere | Low | Low | Verify against `adrs/`, `adrs-migrated/`, and any reserved-ID convention before assigning new numbers |

## Handoff to per-layer Design

Per FR-3 + ADR-0016 the orchestrator activates per-layer designers for each layer in scope. For this feature, **only the Claude Code / Project Filesystem layer is in scope** (per PRD `layer_scope: ["claude-code"]` and the Intent Clarification's gate-confirmed CC-only decision). The orchestrator therefore dispatches `design-cc` (filename `design-claude-code`) only.

The design-cc agent reads this synthesis along with PRD + codebase-analysis.json. The Blueprint produced by Design Composition then ratifies D1–D6 and produces any ADRs that cross-layer reconciliation requires (FR-7 supersession; the FR-10 three-surface enforcement extension of ADR-0042; the OI-2 consolidation policy; and the re-numbering scheme for ADR-0044/0045).

## Provenance

- **Synthesis mode**: streamlined (single-source codebase-analysis + 0 external research). The full synth-* sub-pipeline (extractor → grapher → critic → framer → substrate → synthesizer) was not invoked; the orchestrator produced this synthesis directly per the recipe-feature-pipeline's "synthesis.md or synthesis/" optionality. Rationale: implementation-strategy decisions for a single-source CC-only feature do not benefit from multi-source claim extraction or substrate-comparison framing.
- **Generated by**: parent orchestrator (recipe-feature-pipeline.SKILL.md) at the Synthesis stage of run `adr-placement-mechanism-repair-r1-20260524-183201`.
- **Discovery findings consumed**: codebase-analysis.json (812 lines, schema v1.1.0) + codebase-analysis-report.md (206 lines), produced by discovery-codebase-researcher 2026-05-24.
- **Gate decisions integrated**:
  - Intent Confirmation Gate (2026-05-24T18:55Z): OI-2 = consolidate `adrs-migrated/`.
  - PRD Approval Gate (2026-05-24T19:10Z): PRD v1.0.2 ratified.
  - Research Plan Approval Gate (2026-05-24T19:20Z): 0 external research topics.
  - Synthesis-stage Discovery Findings Gate (2026-05-24T19:40Z, this synthesis):
    - Discovery-OQ-1 (ADR-0044/0045 collision): deferred to Design Composition.
    - Discovery-OQ-2 (archive vs canonical for 8 collisions): archive wins.
