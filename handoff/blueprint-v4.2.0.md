---
id: blueprint-feature-pipeline
version: 4.2.0
status: Draft (Phase 1 — Layer Scope correction in progress per v4-2-plan.md)
supersedes:
  - {id: blueprint-feature-pipeline, version: 3.0.0}
  - {id: blueprint-feature-pipeline, version: 4.0.0}
  - {id: blueprint-feature-pipeline, version: 4.1.0}
superseded_by: []
generated: 2026-05-12
generated_by: synth-reconcile (Layer Scope category-error fix; user-identified defect in v4.0.0 and v4.1.0 — all 9 layers in scope, not just Claude Code FS)
decisions_carried_forward_from_v4_1_0:
  - All 18 inherited ADRs (10 migrated v2.x + 8 new ADRs 0011-0018) — no changes
  - All 12 Functional Requirements — preserved verbatim
  - All EARS-format Acceptance Criteria — preserved verbatim
  - Stage 1.5 PRD generation topology — preserved
  - Stage 5a/5b fan-out-fan-in topology — preserved
  - 5 document-reviewer invocation points — preserved
  - Critic renames — preserved
  - Retroactive ADR migration scope — preserved
  - All 6 issue resolutions from v4.1.0 (I-CA-001, I-AA-001, I-AA-002, I-DR-002, I-DR-003, I-AA-003) — preserved
v4_1_0_to_v4_2_0_changes_summary:
  - Corrected Layer Scope semantic (user-identified): all 9 layers are in scope because the v4 pipeline can design FOR features touching any of the 9 layers (the 9 per-layer designers from ADR-0016 design for each). v4.0.0 and v4.1.0 mistakenly used Layer Scope as "what surfaces does this design artifact physically touch" (which is only Claude Code FS) rather than "what layers can the pipeline design FOR" (which is all 9). v4.2.0 corrects this throughout.
  - Filled 8 per-layer Design sections with substantive content (previously marked `N/A — out of scope`)
  - Updated Design Summary YAML `layers_touched` to all 9 layers
  - Updated Change Impact Map with substantive per-layer rows
  - Added per-layer designer agent files and per-layer knowledge skills as discrete rows in Implementation Path Mapping
  - Updated Security Considerations with substantive per-layer content
  - Updated Test Boundaries Per-Layer Test Strategy table for all 9 layers
  - Added per-layer Acceptance Criteria subsections
  - Updated Error Handling table to cover layer-specific error cases
  - Updated Risks and Mitigation table to cover layer-specific risks
v4_2_0_authoring_note: |
  Per-layer Design section content is authored from general design principles + the canonical Blueprint
  template's per-layer section structure. It is NOT research-grounded the way ADRs 0011-0018 are. The
  per-layer sections each include a `Research grounding` subsection explicitly acknowledging this. The
  actual layer-specific design discipline (i.e., the body of each `<layer>-design-knowledge` skill) is
  deferred to Phase 2 of the Implementation Plan, where research-grounded skill bodies will be authored
  in a separate session with proper research backing per the pipeline's own discipline.
v4_2_0_phase_4_deferred_items: |
  Per the v4-2-plan execution, Phase 4 (cross-section coherence pass) ran in COMPACT mode for session-budget
  reasons. Highest-value updates were completed: T4.1 (Security Considerations per-layer subsections,
  substantive content for all 8 layers) and T4.5 (per-layer AC subsection pattern documented).
  Deferred to a continuation session:
    - T4.2 (Test Boundaries table per-layer entries — currently table is sparse for non-Claude-Code-FS layers)
    - T4.3 (Error Handling table layer-specific rows beyond the generic per-layer designer rows already present)
    - T4.4 (Risks and Mitigation layer-specific entries — currently focused on Claude Code FS scope risks)
    - T4.6 (cross-check Change Impact Map for drift vs Phase 2-3 content)
    - T4.7 (cross-check Project Filesystem table for naming drift vs per-layer designer knowledge skill names)
    - T4.8 (Implementation Plan Phase 2 enrichment with per-layer-skill content drawn from Phase 2-3 authored sections)
  The document-reviewer flagged these as I-DR-004 (severity: recommended only). All review passes
  (document-reviewer, synth-architecture-auditor, synth-cross-artifact-auditor) confirm v4.2.0 is
  load-bearing-complete; deferred items are polish, not blockers.
template_format: per BluePrint.txt v1.0 (uploaded; adopted via ADR-0013)
derived_from:
  - /mnt/user-data/outputs/feature-pipeline-round-2/blueprint-v3.md
  - /mnt/user-data/outputs/feature-pipeline-round-3/research-claims.json
  - /mnt/user-data/outputs/feature-pipeline-round-3/adrs/ (ADR-0011 through ADR-0018)
  - /mnt/user-data/outputs/feature-pipeline-round-3/adrs-migrated/ (ADR-0001 through ADR-0010, template-migrated)
adrs_inherited_v3:
  - {id: ADR-0001, version: 2.0.0} (orchestrator placement — template-migrated)
  - {id: ADR-0002, version: 2.0.0} (critique-1 single-critic CoVe — template-migrated)
  - {id: ADR-0003, version: 2.0.0} (critique-2 CMC + diff-mode + convergence — template-migrated)
  - {id: ADR-0004, version: 2.0.0} (test split — template-migrated)
  - {id: ADR-0005, version: 2.0.0} (append-only supersession — template-migrated)
  - {id: ADR-0006, version: 2.0.0} (synthesis inlined — template-migrated)
  - {id: ADR-0007, version: 2.1.0} (GitNexus primary, codebase-memory-mcp fallback — template-migrated)
  - {id: ADR-0008, version: 2.0.0} (issue ledger per-feature — template-migrated)
  - {id: ADR-0009, version: 2.0.0} (rationale brief 3-layer enforcement — template-migrated)
  - {id: ADR-0010, version: 2.0.0} (knowledge-skill frontmatter correction — template-migrated)
adrs_added_in_v4:
  - {id: ADR-0011, version: 1.0.0} (documentation-criteria canonical document skill)
  - {id: ADR-0012, version: 1.0.0} (PRD generation as Stage 1.5 with synth-prd-author)
  - {id: ADR-0013, version: 1.0.0} (Blueprint template adoption)
  - {id: ADR-0014, version: 1.0.0} (ADR template adoption + retroactive migration)
  - {id: ADR-0015, version: 1.0.0} (EARS-format acceptance criteria)
  - {id: ADR-0016, version: 1.0.0} (per-layer fan-out + composer fan-in for Stage 5)
  - {id: ADR-0017, version: 1.0.0} (document-reviewer integration + critic renames)
  - {id: ADR-0018, version: 1.0.0} (synth-codebase-researcher output schema)
v3_to_v4_changes_summary:
  - Adopts canonical Blueprint template structure per ADR-0013 (this artifact follows the uploaded template)
  - Adds Stage 1.5 PRD generation with synth-prd-author sub-agent per ADR-0012
  - Adds new human gate: PRD Approval Gate (sixth human gate in the pipeline)
  - Inverts Stage 5 to fan-out (9 per-layer designers) + fan-in (synth-designer-composer) per ADR-0016
  - Renames synth-critic-1 → synth-architecture-auditor; synth-critic-2 → synth-cross-artifact-auditor per ADR-0017
  - Integrates document-reviewer at 5 invocation points per ADR-0017
  - Extends document-reviewer doc_type taxonomy with IntentClarification and Plan
  - Adopts EARS-format acceptance criteria pipeline-wide per ADR-0015
  - Specifies canonical synth-codebase-researcher output schema per ADR-0018
  - Consolidates all document templates in documentation-criteria skill per ADR-0011
  - Total sub-agents in v4 pipeline topology: 30 (was 19 in v3, counting document-reviewer existing-but-unintegrated) — added 9 per-layer designers, 1 composer (synth-designer-composer), 1 PRD author (synth-prd-author); removed 1 (synth-designer subsumed by composer + per-layer designers); integrated 1 existing agent (document-reviewer) at 5 invocation points; renamed 2 (synth-critic-1 → synth-architecture-auditor, synth-critic-2 → synth-cross-artifact-auditor) — net delta: +11 sub-agents
---

# Feature-Pipeline — Design Document v4.0.0

> **Notice:** This blueprint fully supersedes v3.0.0. The v3 architecture is preserved at `/mnt/user-data/outputs/feature-pipeline-round-2/blueprint-v3.md`. This v4 incorporates 8 new ADRs (0011 through 0018), retroactive template-migration of ADRs 0001-0010, fan-out-fan-in restructure of Stage 5, PRD generation as new Stage 1.5, document-reviewer integration at five invocation points, critic renames, and EARS-format acceptance criteria.

---

## Overview

The feature-pipeline accepts a vague feature request from a human user and produces a complete, executable, critiqued task plan. The user need may span code (frontend, backend, infrastructure, API), Claude Code filesystem configuration, GitHub CI/CD, GitHub Codespaces, or VS Code workflows. v4 of the pipeline adds a PRD authoring stage, inverts the design stage to per-layer fan-out plus composer fan-in, integrates document-reviewer at five invocation points, and adopts canonical document templates throughout.

### Layer Scope

This blueprint describes the design of the feature-pipeline tooling itself — a meta-design document about an AI pipeline that produces design documents for OTHER features. Layer Scope here is read with two semantics:

- **Pipeline capability scope:** which layers the v4 pipeline can produce design content FOR (via its 9 per-layer designers introduced in ADR-0016). All 9 layers are in this scope — the pipeline is designed to handle features spanning any combination of layers.
- **Artifact-physical scope:** which surfaces the v4 pipeline tooling itself physically modifies (the Claude Code project filesystem only). This is captured separately under "Project Filesystem & Claude Code Conventions" below.

The Layer Scope checklist below reflects **pipeline capability scope** — all 9 layers are checked because the v4 pipeline can design for features touching any of them.

- [x] **Claude Code / Project Filesystem** — `synth-designer-claude-code-fs` authors this section in blueprints. Covers Skills, Subagents, Slash Commands, Hooks, MCP configuration, and CLAUDE.md design.
- [x] **Frontend** — `synth-designer-frontend` authors this section for features touching UI. Covers component design, state management, accessibility, styling, client-side routing.
- [x] **Backend** — `synth-designer-backend` authors this section for features touching service runtime. Covers application logic, request/response handling, background jobs, internal modules.
- [x] **API** — `synth-designer-api` authors this section for features exposing or consuming APIs. Covers endpoint definitions, request/response contracts, versioning, authentication, rate limiting.
- [x] **Query / Data Access** — `synth-designer-query` authors this section for features touching data-access layers. Covers ORM patterns, query construction, transaction boundaries, caching.
- [x] **Database** — `synth-designer-database` authors this section for features touching database schema. Covers schema design, migrations, indexes, constraints, data integrity.
- [x] **CI/CD (GitHub Actions)** — `synth-designer-cicd` authors this section for features touching automation pipelines. Covers workflow files, action selection, secrets management, branch protections.
- [x] **Infrastructure as Code** — `synth-designer-iac` authors this section for features touching infra provisioning. Covers Terraform/CloudFormation/Pulumi modules, state management, environment promotion.
- [x] **Dev Environment (Codespaces / Devcontainer)** — `synth-designer-codespaces` authors this section for features touching the development environment. Covers devcontainer config, post-create hooks, port forwarding, tool installation.

**Note on this specific blueprint (the meta-blueprint authoring v4 of the pipeline itself):** Although Layer Scope is "all 9 layers in scope" because the pipeline can design for all 9, this particular blueprint's substantive changes happen to land mostly in the Claude Code / Project Filesystem layer (new agent files, new skill files, orchestrator update). The Project Filesystem & Claude Code Conventions section below details these physical changes. The per-layer Design sections below describe what each per-layer designer does when invoked for an ACTUAL user feature blueprint — not changes the v4 meta-blueprint itself makes to those layers.

### Referenced Specifications

- **UI Spec**: N/A — pipeline produces no UI.
- **API Spec**: N/A — pipeline exposes no APIs.
- **Data Model Spec**: N/A — pipeline has no persistent data model. Each run's working state lives in `working/feature/<feature-slug>/`.
- **Runbook / Operational Spec**: To be authored at `docs/ops/feature-pipeline-runbook.md` as part of Stage 0 preflight documentation.
- **Document templates**: PRD template, Blueprint template, ADR template, Intent Clarification document template, Plan template — all live in `documentation-criteria` skill per ADR-0011.

## Design Summary (Meta)

```yaml
design_type: "extension"  # v4 extends v3 of the feature-pipeline; not a new feature
risk_level: "medium"  # invasive topology changes; mitigated by ADR-0005 supersession discipline
complexity_level: "high"
complexity_rationale: |
  v4 introduces (1) a new pipeline stage (1.5 PRD generation) requiring orchestrator changes,
  (2) a fan-out-then-fan-in restructure at Stage 5 with 10 new sub-agents requiring coordination
  discipline, (3) document-reviewer integration at 5 invocation points requiring stage-handoff
  updates, (4) retroactive ADR template migration affecting 11 existing artifacts, (5) critic
  renames affecting all downstream references. The complexity addresses real architectural
  needs: structural template enforcement (ADR-0013), parallel-author coordination (ADR-0016),
  multi-stage review composition (ADR-0017), and consistent ADR structure (ADR-0014).
layers_touched:
  # Per-layer-designer capability — the v4 pipeline can produce design content for all 9 layers
  - "Claude Code / Project Filesystem"  # synth-designer-claude-code-fs
  - "Frontend"                            # synth-designer-frontend
  - "Backend"                             # synth-designer-backend
  - "API"                                 # synth-designer-api
  - "Query / Data Access"                 # synth-designer-query
  - "Database"                            # synth-designer-database
  - "CI/CD (GitHub Actions)"              # synth-designer-cicd
  - "Infrastructure as Code"              # synth-designer-iac
  - "Dev Environment (Codespaces)"        # synth-designer-codespaces
  # Note: For THIS meta-blueprint specifically, substantive physical changes land in Claude Code / Project Filesystem.
  # The other layers are in scope because the pipeline can design FOR them; per-layer Design sections below describe each designer's role.
blast_radius:
  runtime: |
    Affects every future feature-pipeline run; existing v3 runs are unaffected (v3 artifacts preserved
    per ADR-0005). Users running the synthesize skill standalone are unaffected (sub-agents shared
    per ADR-0006 remain backward-compatible; only the synth-critic-1/2 renames are runtime-visible
    and gracefully handled by reading new agent files at .claude/agents/synth-architecture-auditor.md
    and synth-cross-artifact-auditor.md).
  build_time: |
    Pipeline installation gains 9 per-layer designer agents, 1 composer agent, 1 PRD author agent,
    1 document-reviewer agent — total 12 new agent files. Knowledge skill inventory expands by ~10
    new skills (process-only, per ADR-0011) plus updates to existing documentation-criteria.
main_constraints:
  - "Compose only Claude Code primitives (no new runtime infrastructure)"
  - "Maintain backward compatibility for the synthesize skill (shared sub-agents per ADR-0006)"
  - "Preserve all v3 artifacts per append-only supersession (ADR-0005)"
  - "Document-reviewer template structure (uploaded) is the contract — extend doc_type taxonomy but do not break existing fields"
  - "Per-layer designer outputs MUST conform to canonical Blueprint template per-layer Design sections"
biggest_risks:
  - "Cross-layer dependency reconciliation at the composer may fail to catch contradictions per-layer designers introduced via independent assumptions (consistency gap, claim C-R3-0007 — 36.9% of multi-agent failures)"
  - "Per-feature ledger and documentation-criteria skill size growing beyond manageable limits over many runs (kill criteria in ADR-0008 and ADR-0011)"
  - "27-sub-agent inventory crossing implicit selection-degradation thresholds (claim C-R2-0010); mitigated because orchestrator picks agents directly, not via Tool RAG"
  - "Five document-reviewer invocation points per feature run increasing wall-clock time and cost; mitigated by Gate 0 fast-fail and per-stage early exit"
unknowns:
  - "Whether documentation-criteria skill at 5 templates will stress per-skill compaction budget (claim C-R2-0006: 5K tokens kept after compaction)"
  - "Whether per-layer designers will reliably emit useful `dependencies_on_other_layers` content without explicit examples in their knowledge skills"
  - "Whether the composer can resolve cross-layer contradictions in its own reasoning context (recursion-safe constraint) for very-multi-layer features (5+ layers active)"
```

## Background and Context

### Prerequisite ADRs

All 18 ADRs (0001-0018) are prerequisites. Full list with versions in the frontmatter `adrs_inherited_v3` and `adrs_added_in_v4` fields. ADRs 0001-0010 are inherited at template-migrated v2.x.x; ADRs 0011-0018 are new in v4.

Common ADRs across the pipeline:
- ADR-0001 (orchestrator placement) — anchors the topology
- ADR-0005 (append-only supersession) — anchors artifact discipline
- ADR-0009 (rationale brief 3-layer enforcement) — anchors handoff discipline
- ADR-0011 (canonical document skill) — anchors document infrastructure
- ADR-0014 (ADR template + retroactive migration) — anchors ADR structure

### External Resources Used

| Resource (project-tier label) | Feature-specific identifier | Notes |
|-------------------------------|-----------------------------|-------|
| GitNexus MCP | `abhigyanpatwari/GitNexus` configured in `.mcp.json` | Primary code-graph MCP per ADR-0007 v2.x. Used by synth-architecture-auditor (renamed from synth-critic-1), synth-codebase-researcher, synth-designer-composer for blast-radius analysis, Code Wiki reads, Cypher queries. |
| codebase-memory-mcp | `DeusData/codebase-memory-mcp` configured in `.mcp.json` | Fallback code-graph MCP per ADR-0007 v2.x. Used when GitNexus is degraded for the user's language stack or for explicit hop-tier risk output. |
| Claude Code platform primitives | `.claude/skills/*`, `.claude/agents/*`, `.claude/settings.json`, `.mcp.json` | Pipeline composes only these primitives per manifest hard constraint. |

### Agreement Checklist

#### Scope

- [x] Add Stage 1.5 PRD generation with new sub-agent `synth-prd-author`
- [x] Add new human gate: PRD Approval Gate
- [x] Invert Stage 5 to fan-out (9 per-layer designers) + fan-in (synth-designer-composer)
- [x] Add 9 per-layer designer sub-agents (synth-designer-claude-code-fs, synth-designer-frontend, synth-designer-backend, synth-designer-api, synth-designer-query, synth-designer-database, synth-designer-cicd, synth-designer-iac, synth-designer-codespaces)
- [x] Add 1 composer sub-agent (synth-designer-composer)
- [x] Rename synth-critic-1 → synth-architecture-auditor
- [x] Rename synth-critic-2 → synth-cross-artifact-auditor
- [x] Integrate document-reviewer sub-agent at 5 invocation points
- [x] Extend document-reviewer doc_type taxonomy with IntentClarification and Plan
- [x] Adopt EARS-format acceptance criteria pipeline-wide
- [x] Adopt canonical Blueprint template (uploaded BluePrint.txt) for all blueprints v4+
- [x] Adopt canonical ADR template (uploaded ADR.txt) for all ADRs v4+
- [x] Retroactively migrate ADRs 0001-0010 to canonical ADR template (Option A — Option 3 structural-preserving)
- [x] Extend documentation-criteria skill with all 5 templates (PRD, Blueprint, ADR, IntentClarification, Plan)
- [x] Specify canonical synth-codebase-researcher output schema (`03-codebase-analysis.json`)

#### Non-Scope (Explicitly not changing)

- [x] The 6 existing synth-* sub-agents from the synthesize pipeline (synth-extractor, synth-grapher, synth-critic, synth-framer, synth-substrate, synth-synthesizer) remain unchanged in their definitions; v4 continues to inline-invoke them per ADR-0006
- [x] ADR-0005 append-only supersession discipline remains unchanged
- [x] Stage 0 preflight, Stage 1 Intent Clarification, Stage 2 Research Planning, Stage 3 Research, Stage 4 Synthesis, Stages 6-11 remain functionally unchanged (Stage 6 and Stage 9 rename their critic sub-agents per ADR-0017 but discipline is preserved)
- [x] The 4-cycle fixed-point iteration cap from v3 remains unchanged; document-reviewer's iteration cap matches (4 cycles)
- [x] Per-feature issue ledger scope from ADR-0008 remains unchanged; document-reviewer integrates with the ledger via its prior_context_check

#### Constraints

- [x] Parallel operation: **Yes** — v3 pipelines can continue running on prior runs; v4 affects only new runs initiated after installation
- [x] Backward compatibility: **Required** — applies to: the synthesize skill (shared sub-agents per ADR-0006); not required for prior v3 run artifacts (preserved per ADR-0005 but no automatic upgrade)
- [x] Performance measurement: **Not required for v4 ship** — wall-clock and cost measurement deferred to post-deployment observation; kill criteria in respective ADRs define when revisit triggers
- [x] Zero-downtime deployment: **Not applicable** — the pipeline has no service runtime; "deployment" means installation of skills/agents into a Claude Code project
- [x] Forward-compatible migration: **Required** — old (v3) ADR formats must remain readable while new (v4) format is canonical for new authoring (achieved via retroactive migration per ADR-0014)

#### Applicable Standards

- [x] **Claude Code Skill+Subagent canonical pattern** `[explicit]` - Source: https://code.claude.com/docs/en/sub-agents (claim C-0001)
- [x] **Recursion-safe sub-agents** `[explicit]` - Source: https://code.claude.com/docs/en/sub-agents (claim C-0003 — Agent tool MUST NOT be in sub-agent's tools list)
- [x] **EARS notation for acceptance criteria** `[explicit]` - Source: Mavin et al. RE'09 2009; Amazon Kiro IDE adoption 2025 (claim C-R3-0003)
- [x] **ADR immutability with bidirectional supersession** `[explicit]` - Source: ADR-0005 (claim C-0014)
- [x] **Append-only artifact discipline** `[implicit]` - Evidence: blueprint v2 and v3 artifact chains - Confirmed: Yes (per ADR-0005)
- [x] **Knowledge skill frontmatter convention** `[explicit]` - Source: ADR-0010 v2.0.0 (claim C-R2-0002)

#### Quality Assurance Mechanisms

- [x] **document-reviewer (sub-agent)** — Enforces: template conformance per `documentation-criteria`, internal consistency, dependency realizability, fact disposition coverage — Config: `.claude/agents/document-reviewer.md` — Covers: all pipeline document artifacts (5 invocation points per ADR-0017) — Status: `adopted`
- [x] **synth-architecture-auditor (sub-agent)** — Enforces: substantive architectural correctness against synthesis claims, blast-radius analysis, brief-honor verification — Config: `.claude/agents/synth-architecture-auditor.md` (renamed from synth-critic-1) — Covers: blueprint at Stage 6 — Status: `adopted`
- [x] **synth-cross-artifact-auditor (sub-agent)** — Enforces: cross-artifact consistency (blueprint ↔ plan ↔ tests), cross-model critique, convergence-bounded iteration — Config: `.claude/agents/synth-cross-artifact-auditor.md` (renamed from synth-critic-2) — Covers: blueprint + plan + tests at Stage 9 — Status: `adopted`
- [x] **synth-phase-validator (sub-agent)** — Enforces: per-phase observable outcomes — Config: `.claude/agents/synth-phase-validator.md` — Covers: plan at Stage 8 — Status: `adopted`
- [x] **Stage 0 preflight skill-frontmatter verification** — Enforces: per ADR-0010, no knowledge skill combines `disable-model-invocation: true` with `skills:` preload — Config: orchestrator preflight logic — Covers: all knowledge skills referenced by sub-agents — Status: `adopted`
- [x] **Issues-ledger lifecycle (per ADR-0008)** — Enforces: every issue has state, transitions tracked, prior context preserved across runs — Config: `working/feature/<slug>/issues-ledger.json` — Covers: project-wide — Status: `adopted`

### Problem to Solve

Blueprint v3's design stage was authored by a single `synth-designer` sub-agent. For multi-layer features, this creates a single-agent bottleneck: one agent must load knowledge skills for every active layer, hold the full blueprint structure in its working context, and reason about cross-layer dependencies in a single linear pass. The user explicitly requested (Q-v4-3 inverted) a fan-out-then-fan-in structure that maps cleanly to the canonical Blueprint template's per-layer Design sections.

Concurrently, the pipeline lacked: (a) a structured business-requirements artifact between intent and research planning (Q-v4-1 introduces a PRD stage); (b) canonical document templates with structural-enforcement mechanism (Q-v4-2, Q-v4-5 and ADR-0011 address this); (c) explicit document-review discipline before substantive critique (the document-reviewer sub-agent exists but had no integration points); (d) standardized acceptance criteria syntax for AI-driven workflow (Q-v4-4 adopts EARS).

### Current Challenges

v3's `synth-designer` produces a single-author blueprint; cross-section voice consistency is preserved but parallelism is foregone. For multi-layer features, the single agent's context window holds all of: rationale brief + PRD + research synthesis + relevant codebase analysis + design-knowledge skill + N domain knowledge skills + the blueprint being authored. This stresses the working context budget per claim C-R2-0011 (20-30% of effective context for active work) and increases the surface area where cross-cutting concerns and per-layer concerns can interfere.

v3 also lacked an explicit document-reviewer integration. Critique-1 and Critique-2 operated as substantive critics; structural conformance to a template was not enforced because there was no canonical template (v3's blueprint structure was ad-hoc). Adding the canonical Blueprint template (ADR-0013) creates the need and the opportunity to integrate document-reviewer's Gate 0 structural check.

### Requirements

#### Functional Requirements

- **FR-1** The pipeline MUST produce a PRD as a versioned artifact at Stage 1.5, authored by `synth-prd-author`, conforming to the canonical PRD template from `documentation-criteria`.
- **FR-2** The pipeline MUST gate PRD content through a new PRD Approval human gate before Research Planning (Stage 2) begins.
- **FR-3** Stage 5 (Design) MUST decompose into Stage 5a (fan-out: up to 9 per-layer designers conditional on Layer Scope) and Stage 5b (fan-in: synth-designer-composer integrates per-layer outputs and authors cross-cutting blueprint sections).
- **FR-4** Per-layer designers MUST emit `dependencies_on_other_layers` declarations for any cross-layer assumptions; the composer MUST reconcile via evidence-based arbitration.
- **FR-5** Only synth-designer-composer authors ADRs at Stage 5; per-layer designers MUST NOT author ADRs.
- **FR-6** document-reviewer MUST run at five invocation points: (1) after Intent Clarification doc, (2) after PRD, (3) after Blueprint composition at Stage 5b, (4) after Plan production at Stage 7, (5) after each individual ADR write.
- **FR-7** document-reviewer's `doc_type` taxonomy MUST be extended to include `IntentClarification` and `Plan` in addition to existing `PRD`, `ADR`, `UISpec`, `DesignDoc`.
- **FR-8** All acceptance criteria across PRD functional requirements, Blueprint Acceptance Criteria section, and acceptance test artifacts MUST use EARS format.
- **FR-9** Sub-agent `synth-critic-1` MUST be renamed `synth-architecture-auditor`; sub-agent `synth-critic-2` MUST be renamed `synth-cross-artifact-auditor`. Knowledge skills renamed correspondingly.
- **FR-10** All document templates (PRD, Blueprint, ADR, Intent Clarification, Plan) MUST live in the `documentation-criteria` skill per ADR-0011.
- **FR-11** synth-codebase-researcher MUST emit `03-codebase-analysis.json` conforming to the canonical schema (ADR-0018) in addition to its markdown research report.
- **FR-12** Existing ADRs 0001-0010 (11 files total including ADR-0007 v1) MUST be retroactively migrated to the canonical ADR template (Option 3 structural-preserving); pre-migration versions preserved per ADR-0005.

#### Non-Functional Requirements

- **Performance**: Stage 5b (composer fan-in) MUST complete within composer's `maxTurns: 60` budget; if exceeded, escalate to Cycle-Cap gate. Stage 5a per-layer designers MUST complete within `maxTurns: 40` each. document-reviewer Gate 0 checks SHOULD complete within ~10 turns; Gate 1 quality assessment within ~25 turns.
- **Scalability**: The pipeline SHOULD gracefully handle features touching all 9 layers (worst case: 9 per-layer designers + composer + all 5 document-reviewer invocations + all other stages). Resource cost grows with active layers; only scoped layers activate designers.
- **Reliability**: The pipeline MUST recover from any single sub-agent failure via the existing fixed-point iteration discipline (4-cycle cap); document-reviewer's prior_context_check carries forward unresolved issues across iterations.
- **Maintainability**: All ADRs MUST conform to the canonical template structure. The 8 new ADRs and 11 retroactively-migrated ADRs MUST be consistent in structure. New ADRs MUST author Decision Details table including Kill criteria (no placeholder content unless explicitly marked "Not applicable — foundational invariant").
- **Operability**: All pipeline artifacts MUST be inspectable via filesystem reads. Issues-ledger MUST be JSON-readable. Run state MUST be resumable across sessions per v3's resume semantics.

## Project Filesystem & Claude Code Conventions

### Repository Layout Touched

| Path | Purpose | Change Type |
|------|---------|-------------|
| `.claude/skills/feature-pipeline/SKILL.md` | Orchestrator skill body | modified — adds Stage 1.5 sequencing, fan-out-fan-in coordination at Stage 5, document-reviewer invocations at 5 points |
| `.claude/skills/documentation-criteria/SKILL.md` | Canonical document skill | modified — extended with 5 templates (PRD, Blueprint, ADR, IntentClarification, Plan) and shared rationale-brief instruction |
| `.claude/skills/<other knowledge skills>/SKILL.md` | Per-sub-agent knowledge skills | modified — frontmatter corrected per ADR-0010; "Honoring the Rationale Brief" instruction references documentation-criteria |
| `.claude/skills/prd-authoring-knowledge/SKILL.md` | New: process knowledge for PRD authoring | new |
| `.claude/skills/design-composition-knowledge/SKILL.md` | New: integration/composition guidance for composer | new |
| `.claude/skills/<layer>-design-knowledge/SKILL.md` (×9) | Per-layer design knowledge skills | new — one per layer designer |
| `.claude/agents/synth-prd-author.md` | New sub-agent | new |
| `.claude/agents/synth-designer-composer.md` | New sub-agent | new |
| `.claude/agents/synth-designer-<layer>.md` (×9) | Per-layer designer sub-agents | new |
| `.claude/agents/synth-architecture-auditor.md` | Renamed from synth-critic-1.md | rename (preserving content with rename-related updates) |
| `.claude/agents/synth-cross-artifact-auditor.md` | Renamed from synth-critic-2.md | rename |
| `.claude/agents/document-reviewer.md` | Existing sub-agent | modified — doc_type taxonomy extended with IntentClarification and Plan |
| `working/feature/<slug>/` | Run working directory | new artifacts: `01-5-prd-v1.md`, `05a-<layer>-design.md` (per active layer), `05b-blueprint-composer-input.json`, `03-codebase-analysis.json` |

### CLAUDE.md Updates

| File | Change | Rationale |
|------|--------|-----------|
| `CLAUDE.md` at repo root | Reference v4 sub-agent inventory and document-reviewer integration points | New contributors need to discover the renamed critics and the new fan-out-fan-in topology |

### Slash Commands

| Command Path | Trigger | Purpose | Notes |
|--------------|---------|---------|-------|
| `.claude/commands/feature-pipeline.md` | `/feature-pipeline` | Launch the pipeline with user intent | Unchanged from v3; orchestrator-skill-as-Skill (per ADR-0001) is `user-invocable: true` so this slash command is automatic |

### Hooks

| Hook Event | Script | Behavior | Failure Mode |
|------------|--------|----------|--------------|
| PreToolUse (when GitNexus configured) | GitNexus auto-augment | Injects blast-radius context before tools that modify code | Non-blocking; missing hook reverts to explicit critique-time queries |

### Skills

| Skill | Location | When Triggered | What It Provides |
|-------|----------|----------------|------------------|
| feature-pipeline | `.claude/skills/feature-pipeline/SKILL.md` | `/feature-pipeline` invocation | Orchestrator body; coordinates all 12 stages and 27 sub-agents |
| documentation-criteria | `.claude/skills/documentation-criteria/SKILL.md` | Auto-invoked when authoring or reviewing documents | All 5 document templates + shared conventions; loaded by every sub-agent that authors documents |
| prd-authoring-knowledge | `.claude/skills/prd-authoring-knowledge/SKILL.md` | Loaded by synth-prd-author | PRD authoring process; AI-PRD failure-mode avoidance (per claim C-R3-0014) |
| design-composition-knowledge | `.claude/skills/design-composition-knowledge/SKILL.md` | Loaded by synth-designer-composer | Integration patterns; evidence-based arbitration for cross-layer conflicts; Fact Disposition Table authoring; cross-cutting section authoring |
| `<layer>-design-knowledge` (×9) | `.claude/skills/<layer>-design-knowledge/SKILL.md` | Loaded by corresponding per-layer designer | Layer-specific design discipline (frontend patterns, API contracts, etc.) |
| architecture-audit-knowledge | `.claude/skills/architecture-audit-knowledge/SKILL.md` (renamed from critique-1-knowledge) | Loaded by synth-architecture-auditor | CoVe + blast-radius + brief-honor discipline |
| cross-artifact-audit-knowledge | `.claude/skills/cross-artifact-audit-knowledge/SKILL.md` (renamed from critique-2-knowledge) | Loaded by synth-cross-artifact-auditor | CMC + diff-mode + convergence discipline |
| codebase-research-knowledge | `.claude/skills/codebase-research-knowledge/SKILL.md` | Loaded by synth-codebase-researcher | Extended per ADR-0018 with canonical output schema |
| (N/A as separate skill) | Gate 0 + Gate 1 discipline lives in `document-reviewer.md` body; templates referenced from `documentation-criteria`; coding-principles and testing-principles skills loaded for implementation-sample verification | Auto-loaded by document-reviewer | document-reviewer does NOT have its own dedicated knowledge skill; discipline is split across the agent body (procedure), documentation-criteria (templates), and coding-principles + testing-principles (implementation-sample compliance) per the uploaded document-reviewer template's `skills:` frontmatter |

### MCP Servers

| Server | Configuration | Tools Exposed | Auth Method |
|--------|---------------|---------------|-------------|
| GitNexus | `.mcp.json` entry (primary) | 16 tools incl. `analyze_impact`, Cypher resources, Code Wiki | None / local |
| codebase-memory-mcp | `.mcp.json` entry (fallback) | 14 tools incl. `detect_changes`, `trace_call_path` with risk_labels | None / local |

### File Naming & Layout Conventions Introduced

- **Stage 1.5 PRD output**: `working/feature/<slug>/01-5-prd-v<N>.md` — Applies to: PRD artifacts only — Enforcement: orchestrator-side filename convention
- **Stage 5a per-layer design outputs**: `working/feature/<slug>/05a-<layer>-design.md` — Applies to: per-layer designer outputs — Enforcement: per-layer designer's knowledge skill teaches the filename
- **Stage 3 codebase analysis JSON**: `working/feature/<slug>/03-codebase-analysis.json` — Applies to: synth-codebase-researcher's structured output — Enforcement: per ADR-0018 schema specification
- **ADR retroactive migration**: pre-migration versions stored as `<original-filename>-pre-template-migration.md` — Applies to: ADRs 0001-0010 — Enforcement: ADR-0014 §Implementation Guidance

## Acceptance Criteria (AC) - EARS Format

### Functional ACs

#### FR-1: PRD generation — Layer: Claude Code / Project Filesystem

- [ ] **When** Stage 1.5 begins, the system shall invoke `synth-prd-author` with the approved Intent Clarification document as input
- [ ] **When** `synth-prd-author` produces its output, the system shall write `01-5-prd-v1.md` to `working/feature/<slug>/` conforming to the canonical PRD template from `documentation-criteria`
- [ ] **If** the produced PRD does not include required template sections (Layer Scope, Stakeholder Inventory, User Stories, FRs, NFRs, Success Criteria), **then** document-reviewer's Gate 0 shall fail and synth-reconcile shall produce a revised PRD version

#### FR-2: PRD Approval Gate — Layer: Claude Code / Project Filesystem

- [ ] **When** document-reviewer's verdict on the PRD is `approved` or `approved_with_conditions`, the system shall present the PRD to the user for approval via AskUserQuestion with options [approve / refine / cancel]
- [ ] **While** the PRD Approval Gate is pending user response, the system shall NOT begin Stage 2 (Research Planning)
- [ ] **If** the user selects `refine`, **then** the system shall invoke synth-reconcile with the user's refinement direction and produce `01-5-prd-v(N+1).md`

#### FR-3: Stage 5 fan-out-fan-in — Layer: Claude Code / Project Filesystem

- [ ] **When** Stage 5a begins, the system shall determine activated per-layer designers from `00-feature-scope.json` Layer Scope flags
- [ ] **When** Layer Scope flags activate one or more per-layer designers, the system shall invoke them in parallel via Agent tool with their corresponding per-layer Design section as output target
- [ ] **When** all activated per-layer designers complete, the system shall transition to Stage 5b and invoke `synth-designer-composer` with all per-layer outputs as input
- [ ] **If** a per-layer designer's output references a cross-layer dependency via `dependencies_on_other_layers`, **then** synth-designer-composer shall resolve via evidence-based arbitration and flag unresolvable conflicts as critique-1 issues

#### FR-4: Cross-layer dependency declarations — Layer: Claude Code / Project Filesystem

- [ ] **When** a per-layer designer assumes a value or behavior in another layer's scope, the system shall require the designer to emit a `dependencies_on_other_layers` entry with `depends_on_layer`, `assumption`, and `fallback_if_wrong` fields
- [ ] **If** the composer detects a contradiction between two per-layer designers' assumptions, **then** the system shall flag the contradiction explicitly in the blueprint and provide both designers' evidence to the auditor

#### FR-5: Composer-only ADR authorship — Layer: Claude Code / Project Filesystem

- [ ] **While** Stage 5a is active, per-layer designers shall NOT produce ADR files
- [ ] **When** synth-designer-composer determines a cross-layer decision requires ADR documentation, the system shall produce the ADR file at `working/feature/<slug>/adrs/ADR-<N>-<slug>.md` conforming to the canonical ADR template

#### FR-6: Five document-reviewer invocations — Layer: Claude Code / Project Filesystem

- [ ] **When** Stage 1 produces an Intent Clarification document, the system shall invoke document-reviewer with `doc_type: IntentClarification`
- [ ] **When** Stage 1.5 produces a PRD, the system shall invoke document-reviewer with `doc_type: PRD`
- [ ] **When** Stage 5b produces a Blueprint, the system shall invoke document-reviewer with `doc_type: DesignDoc` and `codebase_analysis` populated from `03-codebase-analysis.json`
- [ ] **When** Stage 7 produces a Plan, the system shall invoke document-reviewer with `doc_type: Plan`
- [ ] **When** any sub-agent produces an individual ADR, the system shall invoke document-reviewer with `doc_type: ADR` and incorporate issues into the per-feature issues-ledger

#### FR-7: doc_type extension — Layer: Claude Code / Project Filesystem

- [ ] **When** document-reviewer receives a `doc_type: IntentClarification` invocation, the system shall use the IntentClarification template-conformance rules from `documentation-criteria`
- [ ] **When** document-reviewer receives a `doc_type: Plan` invocation, the system shall use the Plan template-conformance rules from `documentation-criteria`

#### FR-8: EARS-format ACs — Layer: Claude Code / Project Filesystem

- [ ] **When** any sub-agent produces an Acceptance Criteria section (in PRD, Blueprint, or acceptance test artifacts), the system shall use EARS format strictly (Ubiquitous, When, While, If-then, or Where)
- [ ] **If** document-reviewer Gate 1 detects a non-EARS AC (e.g., BDD Given/When/Then or freeform prose), **then** the system shall flag it as `important` issue (category: `compliance`)

#### FR-9: Critic renames — Layer: Claude Code / Project Filesystem

- [ ] **When** Stage 6 invokes the architectural critique sub-agent, the system shall invoke `synth-architecture-auditor` (not `synth-critic-1`)
- [ ] **When** Stage 9 invokes the cross-artifact critique sub-agent, the system shall invoke `synth-cross-artifact-auditor` (not `synth-critic-2`)
- [ ] **While** v3 artifacts (preserved per ADR-0005) reference `synth-critic-1` or `synth-critic-2`, the system shall NOT edit those v3 artifacts in place — name updates are forward-only

#### FR-10: Templates in documentation-criteria — Layer: Claude Code / Project Filesystem

- [ ] **When** any sub-agent authoring a document is invoked, the system shall preload `documentation-criteria` skill via the agent's `skills:` frontmatter
- [ ] **When** `documentation-criteria` loads, it shall provide all 5 template structures (PRD, Blueprint, ADR, IntentClarification, Plan) plus shared conventions
- [ ] **If** `documentation-criteria` exceeds 50K tokens AND practical experience surfaces compaction-related fidelity issues, **then** the system shall trigger the kill criterion in ADR-0011 for re-evaluation

#### FR-11: codebase-analysis JSON schema — Layer: Claude Code / Project Filesystem

- [ ] **When** synth-codebase-researcher completes its research, the system shall emit `03-codebase-analysis.json` conforming to the canonical schema (per ADR-0018)
- [ ] **When** document-reviewer is invoked with `doc_type: DesignDoc`, the system shall pass `03-codebase-analysis.json` content as the `codebase_analysis` parameter
- [ ] **When** synth-designer-composer authors the Blueprint's Fact Disposition Table, the system shall populate one row per `focusAreas` entry from the JSON with disposition values from {preserve, transform, remove, out-of-scope}

#### FR-12: Retroactive ADR migration — Layer: Claude Code / Project Filesystem

- [ ] **When** the v4 installation completes, the system shall have produced 11 template-migrated ADR files (ADR-0001 through ADR-0010, plus ADR-0007 v1) following the canonical template
- [ ] **While** retroactive migration is in progress, the system shall preserve pre-migration versions as `<original-filename>-pre-template-migration.md` per ADR-0014

### Per-Layer ACs (illustrative pattern — applies to user-feature blueprints, not this meta-blueprint)

For user features the v4 pipeline designs, each per-layer designer produces a `## Acceptance Criteria — <Layer>` subsection. The patterns for each layer's ACs are described in the corresponding per-layer Design section above. For this self-referential meta-blueprint, the substantive AC content is in the Functional ACs above (which cover the v4 pipeline's tooling changes, all landing in the Claude Code FS layer). Future user-feature blueprints produced by v4 will populate per-layer AC subsections like:

- `## Acceptance Criteria — Frontend` (EARS-format ACs for Frontend-layer behaviors)
- `## Acceptance Criteria — Backend` (EARS-format ACs for Backend-layer behaviors)
- `## Acceptance Criteria — API` (EARS-format ACs for API-layer behaviors)
- `## Acceptance Criteria — Query` (EARS-format ACs for Query-layer behaviors)
- `## Acceptance Criteria — Database` (EARS-format ACs for Database-layer behaviors)
- `## Acceptance Criteria — CI/CD` (EARS-format ACs for CI/CD-layer behaviors)
- `## Acceptance Criteria — IaC` (EARS-format ACs for IaC-layer behaviors)
- `## Acceptance Criteria — Dev Environment` (EARS-format ACs for Dev Environment behaviors)

Each subsection is authored by the corresponding per-layer designer; cross-layer ACs (below) are authored by the composer.

### Cross-Layer / Operational ACs

- [ ] **When** the pipeline starts a feature run, the system shall load any existing `issues-ledger.json` for that feature-slug and integrate previously-resolved issues into the rationale brief
- [ ] **When** document-reviewer's verdict is `needs_revision` or `rejected`, the system shall invoke synth-reconcile to produce a new version and re-invoke document-reviewer with `prior_context_check` populated
- [ ] **If** the iteration cap of 4 cycles is hit at any stage, **then** the system shall escalate to the Cycle-Cap Escalation Gate
- [ ] **When** Stage 0 preflight runs, the system shall verify all sub-agent definitions exist and all referenced knowledge skills exist with correct frontmatter (per ADR-0010)
- [ ] **When** a Codespace is created from a project with this pipeline installed, the system shall require no Codespace-specific configuration beyond the base Claude Code project setup
## Existing Codebase Analysis

### Implementation Path Mapping

| Layer | Type | Path | Description |
|-------|------|------|-------------|
| Claude Code / Project Filesystem | Existing | `.claude/skills/feature-pipeline/SKILL.md` | Orchestrator skill body (v3); v4 modifies in place via new version |
| Claude Code / Project Filesystem | Existing | `.claude/agents/synth-*.md` (18 files in v3) | Existing sub-agent definitions; v4 renames 2 (synth-critic-1/2) and adds 12 new |
| Claude Code / Project Filesystem | Existing | `.claude/skills/<name>-knowledge/SKILL.md` (multiple) | Existing knowledge skills; v4 updates frontmatter per ADR-0010 (already applied in v3 to new skills; retroactive fix to synthesize-pipeline skills) |
| Claude Code / Project Filesystem | Existing | `.claude/skills/documentation-criteria/SKILL.md` | Existing canonical document skill; v4 extends with 5 templates per ADR-0011 |
| Claude Code / Project Filesystem | Existing | `.claude/agents/document-reviewer.md` | Existing sub-agent (uploaded template); v4 extends doc_type taxonomy with IntentClarification and Plan |
| Claude Code / Project Filesystem | New | `.claude/agents/synth-prd-author.md` | New per FR-1 |
| Claude Code / Project Filesystem | New | `.claude/agents/synth-designer-composer.md` | New per FR-3 |
| Claude Code / Project Filesystem | New | `.claude/agents/synth-designer-claude-code-fs.md` | New per FR-3 — per-layer designer for Claude Code / Project Filesystem layer |
| Claude Code / Project Filesystem | New | `.claude/agents/synth-designer-frontend.md` | New per FR-3 — per-layer designer for Frontend layer |
| Claude Code / Project Filesystem | New | `.claude/agents/synth-designer-backend.md` | New per FR-3 — per-layer designer for Backend layer |
| Claude Code / Project Filesystem | New | `.claude/agents/synth-designer-api.md` | New per FR-3 — per-layer designer for API layer |
| Claude Code / Project Filesystem | New | `.claude/agents/synth-designer-query.md` | New per FR-3 — per-layer designer for Query / Data Access layer |
| Claude Code / Project Filesystem | New | `.claude/agents/synth-designer-database.md` | New per FR-3 — per-layer designer for Database layer |
| Claude Code / Project Filesystem | New | `.claude/agents/synth-designer-cicd.md` | New per FR-3 — per-layer designer for CI/CD layer |
| Claude Code / Project Filesystem | New | `.claude/agents/synth-designer-iac.md` | New per FR-3 — per-layer designer for IaC layer |
| Claude Code / Project Filesystem | New | `.claude/agents/synth-designer-codespaces.md` | New per FR-3 — per-layer designer for Dev Environment layer |
| Claude Code / Project Filesystem | New | `.claude/skills/prd-authoring-knowledge/SKILL.md` | New per FR-1 |
| Claude Code / Project Filesystem | New | `.claude/skills/design-composition-knowledge/SKILL.md` | New per FR-3 |
| Claude Code / Project Filesystem | New | `.claude/skills/claude-code-fs-design-knowledge/SKILL.md` | New per FR-3 — knowledge for Claude Code FS per-layer designer (skill, sub-agent, slash command, hook, MCP authoring patterns) |
| Claude Code / Project Filesystem | New | `.claude/skills/frontend-design-knowledge/SKILL.md` | New per FR-3 — knowledge for Frontend per-layer designer (component design, state management, accessibility, styling) |
| Claude Code / Project Filesystem | New | `.claude/skills/backend-design-knowledge/SKILL.md` | New per FR-3 — knowledge for Backend per-layer designer (request handling, internal modules, background jobs) |
| Claude Code / Project Filesystem | New | `.claude/skills/api-design-knowledge/SKILL.md` | New per FR-3 — knowledge for API per-layer designer (endpoint contracts, versioning, auth, rate limiting) |
| Claude Code / Project Filesystem | New | `.claude/skills/query-design-knowledge/SKILL.md` | New per FR-3 — knowledge for Query per-layer designer (ORM patterns, query construction, caching, transactions) |
| Claude Code / Project Filesystem | New | `.claude/skills/database-design-knowledge/SKILL.md` | New per FR-3 — knowledge for Database per-layer designer (schema design, migrations, indexes, integrity) |
| Claude Code / Project Filesystem | New | `.claude/skills/cicd-design-knowledge/SKILL.md` | New per FR-3 — knowledge for CI/CD per-layer designer (workflow files, action SHA-pinning, branch protections) |
| Claude Code / Project Filesystem | New | `.claude/skills/iac-design-knowledge/SKILL.md` | New per FR-3 — knowledge for IaC per-layer designer (module structure, state management, environment promotion) |
| Claude Code / Project Filesystem | New | `.claude/skills/codespaces-design-knowledge/SKILL.md` | New per FR-3 — knowledge for Codespaces per-layer designer (devcontainer config, post-create hooks, port forwarding) |
| Claude Code / Project Filesystem | Renamed | `.claude/agents/synth-architecture-auditor.md` | Renamed from synth-critic-1.md per FR-9 |
| Claude Code / Project Filesystem | Renamed | `.claude/agents/synth-cross-artifact-auditor.md` | Renamed from synth-critic-2.md per FR-9 |
| Claude Code / Project Filesystem | Renamed | `.claude/skills/architecture-audit-knowledge/SKILL.md` | Renamed from critique-1-knowledge per FR-9 |
| Claude Code / Project Filesystem | Renamed | `.claude/skills/cross-artifact-audit-knowledge/SKILL.md` | Renamed from critique-2-knowledge per FR-9 |
| Claude Code / Project Filesystem | Existing | `working/feature/<slug>/issues-ledger.json` | Existing per-feature ledger from ADR-0008; v4 integrates with document-reviewer issues |
| Claude Code / Project Filesystem | New | `working/feature/<slug>/01-5-prd-v<N>.md` | New artifact per FR-1 |
| Claude Code / Project Filesystem | New | `working/feature/<slug>/03-codebase-analysis.json` | New artifact per FR-11 / ADR-0018 |
| Claude Code / Project Filesystem | New | `working/feature/<slug>/05a-<layer>-design.md` (per active layer) | New per-layer designer output per FR-3 |

### Integration Points (Include even for new implementations)

- **Integration Target**: The Claude Code platform — specifically Skill+Subagent invocation, MCP configuration loading, and skill frontmatter parsing.
- **Invocation Method**: User invokes `/feature-pipeline` slash command, which loads the orchestrator skill into the main session context. Orchestrator drives sub-agents via the Agent tool. No external service calls; no scheduled execution; no webhooks.
- **Integration Target**: The existing synthesize pipeline — specifically the 6 shared synth-* sub-agents.
- **Invocation Method**: Inline-invoke per ADR-0006 — feature-pipeline orchestrator directly invokes synth-extractor, synth-grapher, synth-critic, synth-framer, synth-substrate, synth-synthesizer at Stage 4. No skill-to-skill invocation.
- **Integration Target**: GitNexus MCP and codebase-memory-mcp MCP — for blast-radius analysis and codebase structural research.
- **Invocation Method**: Both configured concurrently in `.mcp.json`; Stage 0 preflight detects availability and routing per ADR-0007 v2.x; sub-agents access via standard MCP tool calls.

### Code Inspection Evidence

| File/Function | Relevance |
|---------------|-----------|
| `/mnt/user-data/outputs/feature-pipeline-round-2/blueprint-v3.md` | v3 of this blueprint (predecessor); 885 lines covering Stage 0-11 topology, sub-agent inventory, knowledge skill placement, fixed-point iteration discipline. v4 inherits Stages 0, 1, 2, 3, 4, 6, 7, 8, 9, 10, 11 from v3 functionally; modifies Stage 5 substantially; adds Stage 1.5. |
| `/mnt/user-data/uploads/document_reviewer_template.txt` | Source template for document-reviewer sub-agent definition; specifies Gate 0 / Gate 1 discipline, doc_type taxonomy (PRD/ADR/UISpec/DesignDoc — extended in v4 with IntentClarification/Plan), JSON output schema with verdict and prior_context_check. |
| `/mnt/user-data/uploads/BluePrint.txt` | Canonical Blueprint template (892 lines); adopted as structure for all v4+ blueprints per ADR-0013. This blueprint v4 follows the template's structure. |
| `/mnt/user-data/uploads/ADR.txt` | Canonical ADR template; adopted via ADR-0014; all v4 ADRs (0011-0018) authored in this template; retroactive migration of 0001-0010 to this template (Option 3 structural-preserving). |
| `/mnt/user-data/uploads/PDR.txt` | Canonical PRD template; adopted as PRD output structure per ADR-0012; lives in documentation-criteria skill per ADR-0011. |
| `.claude/agents/synth-critic-1.md`, `synth-critic-2.md` | Existing sub-agent definitions to be renamed per FR-9 / ADR-0017; discipline preserved (CoVe + blast-radius for the former; CMC + diff-mode + convergence for the latter). |

### Fact Disposition Table

This blueprint is self-referential (the pipeline designing the pipeline) rather than a feature against an external codebase. There is no synth-codebase-researcher output (`03-codebase-analysis.json`) for v4 because v4 IS the pipeline being designed, not a feature using the pipeline. The Fact Disposition Table therefore has no `focusAreas` to bind to.

**Status: Not applicable for self-referential pipeline-design blueprint.** This is the one structural difference between this meta-blueprint and a user-feature blueprint. When the pipeline is invoked to design a user feature in the future, synth-codebase-researcher will produce `03-codebase-analysis.json` and the Blueprint will populate this table from its `focusAreas`.

For traceability against v3 artifacts (the closest analog to "existing codebase facts"), the Implementation Path Mapping table above captures path-level dispositions implicitly (Type column: Existing / New / Renamed). No further Fact Disposition Table population is warranted for v4.

## Design

### Change Impact Map

```yaml
Change Target: Feature-pipeline tooling — orchestrator, sub-agent inventory, knowledge skill inventory
Direct Impact (this meta-blueprint's physical changes):
  claude-code-fs:
    - Orchestrator skill body modified (Stage 1.5 sequencing, Stage 5 fan-out-fan-in coordination, 5 document-reviewer invocations)
    - Sub-agent inventory: 12 new agents (synth-prd-author, synth-designer-composer, 9 per-layer designers, document-reviewer integration)
    - Sub-agent inventory: 2 renames (synth-critic-1 → synth-architecture-auditor, synth-critic-2 → synth-cross-artifact-auditor)
    - Knowledge skill inventory: ~12 new skills (prd-authoring-knowledge, design-composition-knowledge, 9 per-layer design knowledge, plus rename of 2 existing)
    - documentation-criteria skill extended with 5 templates and shared rationale-brief instruction
    - document-reviewer template extended with IntentClarification and Plan doc_type values
Capability Impact (what the v4 pipeline can now produce for user features in each layer):
  frontend:
    - synth-designer-frontend authors Frontend Design sections in user-feature blueprints
    - frontend-design-knowledge skill teaches frontend design discipline for Phase 2 authoring
    - Frontend per-layer EARS-format ACs grouped under Frontend AC subsection in user blueprints
    - Document-reviewer Gate 1 validates Frontend Design section structure per Blueprint template
  backend:
    - synth-designer-backend authors Backend Design sections in user-feature blueprints
    - backend-design-knowledge skill teaches backend design discipline (request handling, internal modules, background jobs)
    - Backend per-layer EARS-format ACs grouped under Backend AC subsection
    - Cross-layer dependencies surfaced via dependencies_on_other_layers (e.g., Backend depends on API contract)
  api:
    - synth-designer-api authors API Design sections in user-feature blueprints
    - api-design-knowledge skill teaches API contract discipline (versioning, auth, rate limiting, error responses)
    - API contracts feed Frontend's API consumption + Backend's API surface
    - Cross-layer dependencies: API ↔ Backend (contract), API ↔ Frontend (consumption)
  query:
    - synth-designer-query authors Query / Data Access Design sections in user-feature blueprints
    - query-design-knowledge skill teaches data-access patterns (ORM, query construction, caching, transactions)
    - Cross-layer dependencies: Query ↔ Database (schema), Query ↔ Backend (consumer)
  database:
    - synth-designer-database authors Database Schema & Migration Design sections in user-feature blueprints
    - database-design-knowledge skill teaches schema design discipline (normalization, indexes, migrations, integrity constraints)
    - Cross-layer dependencies: Database ↔ Query (schema contract for ORM/queries)
  cicd:
    - synth-designer-cicd authors CI/CD Design sections in user-feature blueprints
    - cicd-design-knowledge skill teaches GitHub Actions workflow discipline (jobs, secrets, branch rules, action SHA-pinning)
    - Cross-layer dependencies: CI/CD reads all other layers for build/test/deploy steps
  iac:
    - synth-designer-iac authors Infrastructure as Code Design sections in user-feature blueprints
    - iac-design-knowledge skill teaches IaC discipline (Terraform/CloudFormation/Pulumi module structure, state management, environment promotion)
    - Cross-layer dependencies: IaC provisions resources Backend, Database, CI/CD depend on
  codespaces:
    - synth-designer-codespaces authors Dev Environment Design sections in user-feature blueprints
    - codespaces-design-knowledge skill teaches devcontainer discipline (base image, post-create hooks, port forwarding, extensions)
    - Cross-layer dependencies: Codespaces sets up local environment matching production for all other layers
Indirect Impact:
  - Synthesize pipeline (existing): receives knowledge-skill frontmatter fix per ADR-0010 retroactively; shared sub-agents unchanged but the synth-critic-* renames do not affect synthesize-pipeline references (those names were specific to feature-pipeline, NOT shared)
  - User documentation: pipeline-setup README and user-facing guides need updates for v4 sub-agent inventory and PRD Approval Gate addition
  - Future blueprints: every blueprint v4+ produced by this pipeline follows the canonical template
  - Future ADRs: every ADR v4+ follows the canonical ADR template with Kill criteria
No Ripple Effect:
  - Prior v3 runs and v3 artifacts (preserved per ADR-0005 append-only supersession)
  - The 6 shared synth-* sub-agents from the synthesize pipeline (definitions unchanged; only their knowledge-skill frontmatter is patched per ADR-0010, which was already declared in v3)
  - User projects that do not install v4 (continue running v3 if installed)
```

### Interface Change Matrix

| Existing | New | Conversion Required | Compatibility Method |
|----------|-----|---------------------|----------------------|
| synth-critic-1 sub-agent name | synth-architecture-auditor sub-agent name | Yes (rename) | Forward-only rename per FR-9; v3 artifacts continue to reference old name (preserved per ADR-0005); new orchestrator (v4) references new name; no symlink or alias needed because v4 supersedes v3 entirely |
| synth-critic-2 sub-agent name | synth-cross-artifact-auditor sub-agent name | Yes (rename) | Same as above |
| critique-1-knowledge skill name | architecture-audit-knowledge skill name | Yes (rename) | Forward-only; v4 sub-agents reference new name |
| critique-2-knowledge skill name | cross-artifact-audit-knowledge skill name | Yes (rename) | Forward-only; v4 sub-agents reference new name |
| document-reviewer doc_type taxonomy (PRD/ADR/UISpec/DesignDoc) | doc_type taxonomy extended (+ IntentClarification, Plan) | No (additive) | document-reviewer body extended with new doc_type values; existing values unchanged; existing invocations remain valid |
| Stage 5 single synth-designer | Stage 5a (per-layer designers) + Stage 5b (composer) | Yes (topology change) | v4 orchestrator dispatches per-layer-designers based on Layer Scope flags from Stage 0; composer fan-in produces single blueprint artifact per existing v3 contract; downstream stages (6 through 11) see the same blueprint-shape input, just produced by a different internal topology |
| Blueprint structure (v3 ad-hoc) | Blueprint structure (canonical template per ADR-0013) | Yes (structure change) | v4 blueprints follow canonical template strictly; v3 blueprint preserved unchanged; downstream stages parse the new structure (planner, task-decomposer adapt to per-layer Design sections) |
| ADR structure (v3 ad-hoc) | ADR structure (canonical template per ADR-0014) | Yes (structure change, retroactive) | 11 existing ADRs migrated structurally (content preserved verbatim where it fits); pre-migration versions preserved as `*-pre-template-migration.md`; new ADRs (0011-0018) authored directly in canonical template |
| AC syntax (v3 BDD Gherkin) | AC syntax (EARS strict per ADR-0015) | Yes (syntax change) | v4 acceptance tests, blueprint ACs, PRD FRs all use EARS; v3 artifacts preserved with their BDD syntax |
| Stages 1 → 2 direct handoff | Stages 1 → 1.5 → 2 handoff via PRD | Yes (new intermediary stage) | Stage 2 now consumes the approved PRD instead of the Intent Clarification doc; Stage 1's output (Intent Clarification doc) becomes Stage 1.5's input; the PRD Approval Gate sits between 1.5 and 2 |

### Architecture Overview

The pipeline is a Claude Code Skill that orchestrates 27 sub-agents across 12 stages with 6 human approval gates. The orchestrator runs in the main session; sub-agents are invoked via the Agent tool. Knowledge skills are preloaded via sub-agent `skills:` frontmatter (per ADR-0010 corrected pattern). MCPs (GitNexus primary, codebase-memory-mcp fallback) provide code-graph analysis for the auditing stages.

```
USER
  │
  │ /feature-pipeline "I want X"
  ▼
┌────────────────────────────────────────────────────────────────┐
│  Orchestrator (feature-pipeline skill, main session)           │
│  - Generates rationale brief per ADR-0009 at every handoff     │
│  - Tracks issue lifecycle per ADR-0008                         │
│  - Maintains traceability.json per ADR-0005                    │
└────────────────────────────────────────────────────────────────┘
  │
  ├─ Stage 0: Preflight (inline in orchestrator)
  │    └─ scope detection, MCP health check, ledger init, skill frontmatter verify
  │
  ├─ Stage 1: synth-intent-clarifier → Intent Clarification doc
  │    └─ document-reviewer (doc_type: IntentClarification) ─→ Intent Confirmation Gate ←─ USER
  │
  ├─ Stage 1.5: synth-prd-author → PRD                                                   [NEW v4]
  │    └─ document-reviewer (doc_type: PRD) ─→ PRD Approval Gate ←─ USER                 [NEW v4]
  │
  ├─ Stage 2: synth-research-planner → Research Plan
  │    └─ Research Plan Approval Gate ←─ USER
  │
  ├─ Stage 3: synth-researcher (×N up to 6 in parallel) + synth-codebase-researcher
  │    └─ synth-codebase-researcher emits 03-codebase-analysis.json (canonical schema)   [NEW v4]
  │
  ├─ Stage 4: 6 inlined synthesis sub-agents
  │    └─ synth-extractor → synth-grapher → synth-critic → synth-framer → synth-substrate → synth-synthesizer
  │
  ├─ Stage 5a: Fan-out per-layer designers (up to 9, conditional on Layer Scope)         [NEW v4]
  │    └─ synth-designer-claude-code-fs / -frontend / -backend / -api / -query           [NEW v4]
  │       / -database / -cicd / -iac / -codespaces                                       [NEW v4]
  │
  ├─ Stage 5b: synth-designer-composer (fan-in, cross-cutting authoring, ADRs)           [NEW v4]
  │    └─ document-reviewer (doc_type: DesignDoc) ─→ Blueprint Approval Gate ←─ USER
  │
  ├─ Stage 6: synth-architecture-auditor                                            [renamed v4]
  │    └─ CoVe + blast-radius + brief-honor verification
  │    └─ ↺ iterate (4-cycle cap) via synth-reconcile if needed
  │
  ├─ Stage 7: synth-planner → Plan
  │    └─ document-reviewer (doc_type: Plan)                                             [NEW v4]
  │
  ├─ Stage 8: synth-acceptance-tester (reads blueprint only) + synth-phase-validator (reads plan)
  │    └─ acceptance tests in EARS format per ADR-0015                                   [NEW v4]
  │
  ├─ Stage 9: synth-cross-artifact-auditor                                          [renamed v4]
  │    └─ CMC + diff-mode + convergence-based termination
  │    └─ ↺ iterate via synth-reconcile if needed
  │
  ├─ Stage 10: synth-reconcile (invoked from Stages 6 and 9 when issues need resolution)
  │
  └─ Stage 11: synth-task-decomposer → final task DAG → BUILD APPROVAL GATE ←─ USER
```

document-reviewer runs at 5 invocation points (marked above with "document-reviewer (doc_type: X)"); each invocation can trigger synth-reconcile if verdict is `needs_revision` or `rejected`, with prior_context_check carrying forward unresolved issues across iterations.

### Data Flow

```
USER INTENT (free-form text)
    │
    ▼
[Stage 0 preflight] → 00-feature-scope.json {feature_slug, layers_in_scope, mcp_status, skill_frontmatter_status}
    │
    ▼
[Stage 1: synth-intent-clarifier] → 01-intent-clarification.md
    │   ▶ [document-reviewer doc_type:IntentClarification] → verdict
    │   ▶ INTENT CONFIRMATION GATE ← USER
    ▼
[Stage 1.5: synth-prd-author] → 01-5-prd-v1.md                              ← NEW v4
    │   ▶ [document-reviewer doc_type:PRD] → verdict
    │   ▶ PRD APPROVAL GATE ← USER                                          ← NEW v4
    ▼
[Stage 2: synth-research-planner] → 02-research-plan.md
    │   ▶ RESEARCH PLAN APPROVAL GATE ← USER
    ▼
[Stage 3: synth-researcher × N(≤6) + synth-codebase-researcher]
    │   ├→ 03-research-findings-N.md (per researcher)
    │   └→ 03-codebase-analysis.json (canonical schema per ADR-0018)        ← NEW v4
    │   └→ 03-codebase-analysis-report.md (markdown sibling)
    ▼
[Stage 4: 6-stage synthesis (inlined)] → 04-synthesis/report.md + 04-synthesis/adrs/*.md
    │
    ▼
[Stage 5a: Per-layer designers (up to 9 parallel)]                          ← NEW v4
    │   ├→ 05a-claude-code-fs-design.md (if scope checked)                  ← NEW v4
    │   ├→ 05a-frontend-design.md (if scope checked)                        ← NEW v4
    │   ├→ ... (other layers as scoped)                                     ← NEW v4
    │   └→ Each emits dependencies_on_other_layers field                    ← NEW v4
    ▼
[Stage 5b: synth-designer-composer]                                         ← NEW v4
    │   ├ inputs: all per-layer outputs + rationale brief + PRD + codebase analysis
    │   ├ resolves cross-layer dependencies via evidence-based arbitration
    │   ├ authors cross-cutting sections (Overview, Design Summary YAML, Background, Architecture
    │   │  Overview, Data Flow, Change Impact Map, Interface Change Matrix, Fact Disposition Table,
    │   │  Main Components, Verification Strategy)
    │   ├ authors ADRs (per-layer designers MUST NOT)
    │   └ produces 05-blueprint-v1.md (canonical template per ADR-0013)
    │   ▶ [document-reviewer doc_type:DesignDoc with codebase_analysis input] → verdict
    │   ▶ BLUEPRINT APPROVAL GATE ← USER
    ▼
[Stage 6: synth-architecture-auditor]                                       ← renamed v4
    │   ├ CoVe + blast-radius via GitNexus + brief-honor verification
    │   └ produces 06-architecture-audit-issues.json
    │   ↺ if needs_revision → synth-reconcile → 05-blueprint-v(N+1).md → re-review (4-cycle cap)
    ▼
[Stage 7: synth-planner] → 07-plan.md (or plan.json depending on serialization)
    │   ▶ [document-reviewer doc_type:Plan] → verdict
    ▼
[Stage 8: synth-acceptance-tester + synth-phase-validator (concurrent)]
    │   ├→ 08a-acceptance-tests.md (EARS-format scenarios per ADR-0015)     ← NEW syntax v4
    │   └→ 08b-phase-validators inline in plan.json + e2e-test.md
    ▼
[Stage 9: synth-cross-artifact-auditor]                                     ← renamed v4
    │   ├ CMC (model: opus override) + diff-mode + convergence
    │   └ produces 09-cross-artifact-audit-issues.json
    │   ↺ if needs_revision → synth-reconcile → re-review (4-cycle cap)
    ▼
[Stage 10: synth-reconcile] (invoked from 6 and 9 as needed; produces new versions
    of blueprint / plan / tests carrying forward prior decisions per ADR-0005)
    │
    ▼
[Stage 11: synth-task-decomposer] → 11-tasks.json (final task DAG)
    │   ▶ BUILD APPROVAL GATE ← USER
    │
    ▼
EXECUTION (out of pipeline scope; pipeline output is the approved task DAG)

ADR authorship at every stage that introduces architectural decisions:
- synth-reconcile, synth-designer-composer write ADRs in canonical template
- Each ADR write → [document-reviewer doc_type:ADR] → issue ledger integration
```

### Integration Points List

| Integration Point | Location | Old Implementation | New Implementation | Switching Method | Verification Method |
|-------------------|----------|--------------------|--------------------|-------------------|---------------------|
| Stage 1 → Stage 2 handoff | Orchestrator | Direct (clarified intent → research plan) | Via Stage 1.5 PRD (clarified intent → PRD → research plan) | Pipeline topology change in orchestrator skill body | Trace through v4 run: orchestrator MUST invoke synth-prd-author after synth-intent-clarifier completes |
| Stage 5 Design authoring | Orchestrator | Single synth-designer | Stage 5a fan-out + Stage 5b composer | Orchestrator skill body change; dispatches based on `00-feature-scope.json` Layer Scope flags | Trace: 5a invocations match scoped layers; 5b receives all 5a outputs |
| document-reviewer integration | Various stages | Not previously integrated (v3 had no canonical templates to review against) | Invoked at 5 points after each document artifact | Orchestrator inserts document-reviewer invocation after each templated-doc-producing stage | Each of 5 invocation points produces a document-reviewer JSON output with verdict |
| Blueprint AC syntax | Inside blueprint document | BDD Gherkin (Given/When/Then) in v3 | EARS (Ubiquitous/When/While/If-then/Where) in v4 | knowledge skill change (acceptance-testing-knowledge teaches EARS; prd-authoring-knowledge teaches EARS); document-reviewer Gate 1 validates EARS keyword usage | Document-reviewer flags non-EARS ACs as `important` issue category `compliance` |
| Critic invocation by name | Orchestrator | `synth-critic-1`, `synth-critic-2` | `synth-architecture-auditor`, `synth-cross-artifact-auditor` | Sub-agent file rename + skill file rename + orchestrator references updated | v4 orchestrator runs end-to-end with new agent names; old names not referenced in v4 |
| Codebase analysis output | synth-codebase-researcher | Markdown research report only | Markdown report + canonical JSON schema (`03-codebase-analysis.json`) | codebase-research-knowledge skill extended with schema specification | document-reviewer at Stage 5b receives JSON; blueprint composer reads JSON to populate Fact Disposition Table |

### Main Components

#### Component 1: Orchestrator skill (feature-pipeline)

- **Responsibility**: Top-level coordination of all 12 stages; constructs rationale briefs per ADR-0009; manages the per-feature issues-ledger per ADR-0008; maintains traceability.json per ADR-0005; enforces human gates (6 total); dispatches sub-agents via the Agent tool; coordinates fan-out at Stage 5a and fan-in at Stage 5b; invokes document-reviewer at 5 points.
- **Interface**: `/feature-pipeline` slash command; takes user intent as input ($1 / $ARGUMENTS); produces final task DAG at `working/feature/<slug>/11-tasks.json`. Internal interface: file-path-based handoff to all sub-agents per ADR-0006 inline-invoke pattern.
- **Dependencies**: All 27 sub-agents; all knowledge skills (loaded by sub-agents not directly by orchestrator); GitNexus and codebase-memory-mcp MCPs; Claude Code platform primitives (Skill, Agent tool, AskUserQuestion, Read, Write).

#### Component 2: synth-prd-author sub-agent (NEW v4)

- **Responsibility**: At Stage 1.5, consumes the approved Intent Clarification document and produces a PRD conforming to the canonical PRD template; addresses AI-PRD failure modes per claim C-R3-0014 by following prd-authoring-knowledge guidance (no fabricated customer reactions, no over-precise specs without rationale, no implementation suggestions in requirements).
- **Interface**: Invoked by orchestrator with input path to approved Intent Clarification doc; writes `01-5-prd-v<N>.md` to working directory. Single-author topology per ADR-0012.
- **Dependencies**: `documentation-criteria` skill (for PRD template); `prd-authoring-knowledge` skill (for process); Read, Write, AskUserQuestion tools.

#### Component 3: 9 per-layer designer sub-agents (NEW v4)

- **Responsibility**: At Stage 5a, each authors its corresponding per-layer Design section per the canonical Blueprint template. Emits `dependencies_on_other_layers` for any cross-layer assumption. Authors layer-scoped EARS-format acceptance criteria. Does NOT author ADRs (composer-only per FR-5). Does NOT author cross-cutting sections.
- **Interface**: Invoked by orchestrator in parallel based on `00-feature-scope.json` Layer Scope flags; each writes to its corresponding `05a-<layer>-design.md` and may emit a `05a-<layer>-dependencies.json` sidecar for cross-layer dependency declarations.
- **Dependencies**: `documentation-criteria` skill (for template); `<layer>-design-knowledge` skill (layer-specific patterns); `general-coding-principles-knowledge`; `claude-code-filesystem-knowledge` when applicable; Read, Write tools. NO Agent tool (recursion-safe per ADR-0001).

#### Component 4: synth-designer-composer sub-agent (NEW v4)

- **Responsibility**: At Stage 5b, integrates all per-layer designer outputs; authors cross-cutting Blueprint sections (Overview, Design Summary YAML, Background, Architecture Overview, Data Flow top-level, Change Impact Map, Interface Change Matrix, Fact Disposition Table, top-level Components, Verification Strategy); resolves cross-layer contradictions via evidence-based arbitration (claim C-R3-0013); flags unresolvable contradictions as critique input; authors ADRs that cross-layer reconciliation requires.
- **Interface**: Invoked by orchestrator after all activated per-layer designers complete; consumes all `05a-*-design.md` files + `01-5-prd-vN.md` + `03-codebase-analysis.json` + rationale brief; produces `05-blueprint-v1.md` conforming to canonical template.
- **Dependencies**: `documentation-criteria` skill; `design-composition-knowledge` skill (integration patterns + evidence-based arbitration discipline); selectively loads per-layer knowledge skills for the cross-layer reconciliations it must perform; Read, Write tools. NO Agent tool.

#### Component 5: document-reviewer sub-agent (EXTENDED in v4)

- **Responsibility**: Two-gate review of templated documents (Gate 0 structural existence; Gate 1 quality assessment including consistency, completeness, compliance, feasibility, dependency realizability, fact disposition coverage). Iterative invocation with prior_context_check for previously surfaced issues.
- **Interface**: Invoked by orchestrator at 5 points (after Intent Clarification doc, PRD, Blueprint composition at 5b, Plan production, and each individual ADR write); produces structured JSON verdict with severity-categorized issues.
- **Dependencies**: `documentation-criteria` skill (for templates); `coding-principles` and `testing-principles` skills (for verification of implementation samples); GitNexus / codebase-memory-mcp for Grep/Glob dependency realizability; Read, Grep, Glob, LS, Bash, TaskCreate, TaskUpdate, WebSearch tools. NO Agent tool (recursion-safe).

#### Component 6: synth-architecture-auditor sub-agent (RENAMED from synth-critic-1)

- **Responsibility**: At Stage 6, substantively audits the blueprint against synthesis claims; performs blast-radius analysis via GitNexus; verifies brief-honor per ADR-0009 Layer-3 checks (decision contradiction, open-item handling, re-surfaced verified issue); produces issues JSON for triage.
- **Interface**: Invoked by orchestrator after document-reviewer passes the Blueprint at Stage 5b; consumes blueprint + rationale brief + synthesis claims + GitNexus output.
- **Dependencies**: `architecture-audit-knowledge` skill (renamed from critique-1-knowledge); `documentation-criteria` skill; GitNexus MCP primary, codebase-memory-mcp fallback; Read, Grep, Glob, Bash, plus MCP tools. NO Agent tool.

#### Component 7: synth-cross-artifact-auditor sub-agent (RENAMED from synth-critic-2)

- **Responsibility**: At Stage 9, cross-artifact consistency check across blueprint + plan + acceptance tests + phase validators; CMC posture (declares `model: opus` for cross-family critique); diff-mode input (does not see full upstream context); convergence-based termination + 4-cycle hard cap.
- **Interface**: Invoked by orchestrator after Stages 6, 7, and 8 complete; consumes diffs (blueprint v(N) vs v(N-1)) + plan + tests + prior round's critique-2 issues.
- **Dependencies**: `cross-artifact-audit-knowledge` skill (renamed from critique-2-knowledge); `documentation-criteria` skill; Read tools. Declares `model: opus` in frontmatter when main agent is Sonnet. NO Agent tool.

### Data Representation Decision (New Structures Introduced)

| Criterion | Assessment | Reason |
|-----------|-----------|--------|
| Semantic Fit | Yes for canonical schema in `03-codebase-analysis.json` | The schema's `focusAreas`, `evidence`, `dataTransformationPipelines` fields are deliberately aligned with document-reviewer's expected input (uploaded template) — exact semantic match. |
| Responsibility Fit | Yes | The schema lives in `documentation-criteria` (per ADR-0011) which is the canonical home for document-related conventions. |
| Lifecycle Fit | Yes | The JSON's lifecycle mirrors its consumers: produced by synth-codebase-researcher at Stage 3, consumed by composer at 5b and document-reviewer at 5b's review invocation. |
| Boundary/Interop Cost | Low | The JSON is a structured handoff artifact within a single pipeline; no external consumer. |

**Decision**: new — define a pipeline-canonical schema in ADR-0018 because no industry-standard schema for codebase analysis output exists (claim C-R3-0028).

### Contract Definitions

```yaml
# Sub-agent invocation contract (orchestrator → sub-agent)
SubAgentInvocation:
  invocation:
    agent_name: string (e.g., "synth-prd-author")
    prompt: |
      ## Rationale Brief — Stage <N>: <stage-name>
      <required template per ADR-0009>

      ## Task
      <stage-specific instructions>

      ## Inputs (paths to read in order)
      <enumerated file paths>

      ## Output
      <expected output path and format>

  expected_output:
    artifact_path: string
    artifact_format: markdown | json (per stage)
    structured_output: JSON (when sub-agent produces structured side-channel data)

# document-reviewer invocation contract (per uploaded template)
DocumentReviewerInvocation:
  inputs:
    mode: "composite" (default per ADR-0017)
    doc_type: PRD | ADR | UISpec | DesignDoc | IntentClarification | Plan
    target: path/to/document.md
    code_verification: optional JSON (currently unused; reserved for future code-verification stages)
    codebase_analysis: optional JSON (per ADR-0018 schema; populated at Stage 5b for DesignDoc review)
  output:
    JSON per uploaded document_reviewer_template.txt Output Protocol section
    verdict.decision: approved | approved_with_conditions | needs_revision | rejected
    issues: array of {id, severity, category, location, description, suggestion}
    scores: {consistency, completeness, rule_compliance, clarity}
    prior_context_check (when prior_context_count > 0)

# Per-layer designer output contract (Stage 5a)
PerLayerDesignerOutput:
  primary:
    path: working/feature/<slug>/05a-<layer>-design.md
    structure: corresponds to "<Layer> Design" section of canonical Blueprint template
  sidecar:
    path: working/feature/<slug>/05a-<layer>-dependencies.json
    schema:
      dependencies_on_other_layers:
        - depends_on_layer: string  # e.g., "api"
          assumption: string  # e.g., "API exposes /users endpoint with POST creation"
          fallback_if_wrong: string  # e.g., "Use /accounts endpoint instead"
          evidence: string  # what grounded this assumption (research finding, PRD section, etc.)
```

### Data Contract

#### Component: synth-prd-author

```yaml
Input:
  Type: Approved Intent Clarification document path + run context
  Preconditions:
    - Intent Clarification doc exists at working/feature/<slug>/01-intent-clarification.md
    - document-reviewer has produced an `approved` or `approved_with_conditions` verdict on it
    - Intent Confirmation Gate has been cleared by the user
  Validation: Orchestrator-side check before invocation
Output:
  Type: Markdown PRD at working/feature/<slug>/01-5-prd-v<N>.md
  Guarantees:
    - Conforms to canonical PRD template structure
    - All required sections present (Stakeholder Inventory, Layer Scope, User Stories per stakeholder, Functional Requirements with EARS ACs, Non-Functional Requirements, Success Criteria, Rollout Plan)
    - No fabricated content (every user story grounded in stated intent; no invented customer quotes)
    - No implementation suggestions (no programming language picks; no code samples; no library names)
  On Error: synth-prd-author emits a partial PRD with explicit `[UNRESOLVED: <issue>]` markers; orchestrator does NOT advance to PRD Approval Gate; falls through to reconcile-iteration loop
Invariants:
  - Single-authored (one sub-agent invocation; no fan-out)
  - User stories are AT MOST 3-4 per stakeholder for MVP-scoped features (claim C-R3-0017 AI over-generation tendency mitigated by prd-authoring-knowledge guidance)
  - Feature-slug from Stage 0 is preserved verbatim in PRD frontmatter
```

#### Component: synth-designer-composer

```yaml
Input:
  Type:
    - All per-layer designer outputs (05a-*-design.md)
    - All per-layer dependencies sidecar files (05a-*-dependencies.json)
    - Approved PRD (01-5-prd-vN.md)
    - Codebase analysis (03-codebase-analysis.json)
    - Rationale brief
  Preconditions:
    - All activated per-layer designers have completed (no partial 5a output)
    - 00-feature-scope.json was used to determine which designers activated
    - Stage 4 synthesis ADRs are written and inherited via rationale brief
  Validation: Orchestrator checks per-layer designer completion before invoking composer
Output:
  Type: Single integrated Blueprint at working/feature/<slug>/05-blueprint-v1.md
  Guarantees:
    - Conforms to canonical Blueprint template structure (per ADR-0013)
    - All per-layer Design sections present (those marked N/A for unscoped layers)
    - Fact Disposition Table populated (one row per focusArea in codebase analysis JSON)
    - Cross-cutting sections authored by composer (Overview, Design Summary YAML, Architecture Overview, etc.)
    - All cross-layer dependency assumptions reconciled (or explicitly flagged as unresolvable critique-1 input)
    - Any new ADRs introduced by cross-layer reconciliation are in canonical ADR template
  On Error: composer produces a partial blueprint with `[UNRESOLVED: <contradiction>]` markers for flagged contradictions; orchestrator advances to document-reviewer review of the partial blueprint; document-reviewer will surface the markers as `critical` issues; reconcile-iteration loop handles
Invariants:
  - Composer-only ADR authorship at Stage 5 (per FR-5)
  - All per-layer designer outputs are integrated (no per-layer section silently omitted from the blueprint)
  - Cross-layer contradictions are flagged, never silently blended (per claim C-R3-0013 pattern)
```

### Field Propagation Map

| Field | Boundary | Status | Detail |
|-------|----------|--------|--------|
| `feature_slug` | Stage 0 → all subsequent stages | preserved | Generated at Stage 0; appears in every artifact's frontmatter; canonical across all run artifacts and per ADR-0008 across all runs of the same feature |
| `run_id` | Stage 0 → all subsequent stages | preserved | Generated at Stage 0 as `<feature-slug>-<timestamp>`; preserved verbatim in all artifact frontmatter and rationale briefs |
| `focusAreas[].fact_id` | Stage 3 (synth-codebase-researcher) → Stage 5b (composer Fact Disposition Table) → Stage 5b (document-reviewer Gate 0 check) | preserved | Carried verbatim through; required for cross-artifact reference per ADR-0018 |
| `focusAreas[].evidence` | Stage 3 → Stage 5b composer → Blueprint Fact Disposition Table Evidence column | preserved | Verbatim — code snippet or signature; document-reviewer Gate 1 validates the column carries through |
| Acceptance criteria EARS keyword | PRD FR section → Blueprint Acceptance Criteria section → acceptance test scenarios | preserved | Keyword (When/While/If-then/Where/no-keyword) preserved across documents; document-reviewer Gate 1 validates EARS keyword usage per ADR-0015 |
| `dependencies_on_other_layers[].assumption` | Stage 5a per-layer designer → Stage 5b composer reconciliation | transformed | Per-layer designer emits assumption as a tentative claim; composer either confirms (other layer's design supports it) or contradicts (other layer's design conflicts) — recorded in composer's reconciliation rationale |
| Issue `id` | Issue first opened → all subsequent transitions in issues-ledger.json | preserved | Per ADR-0008, issue IDs are sequential within feature-slug; never reset across runs |
| ADR `id` and `version` | ADR write → traceability.json → rationale briefs → downstream sub-agent reading | preserved | Per ADR-0005 immutability; supersession produces new version with explicit `supersedes` reference |

### State Transitions and Invariants

```yaml
State Definition:
  Pipeline run states:
    - Initial State: NOT_STARTED (no run directory)
    - Possible States:
      - STAGE_0_PREFLIGHT
      - STAGE_1_INTENT (with sub-state: REVIEWING | GATE_PENDING)
      - STAGE_1_5_PRD (with sub-state: AUTHORING | REVIEWING | GATE_PENDING)
      - STAGE_2_RESEARCH_PLAN (with sub-state: AUTHORING | GATE_PENDING)
      - STAGE_3_RESEARCH (with sub-state: FAN_OUT_RESEARCHERS | CODEBASE_RESEARCH | DONE)
      - STAGE_4_SYNTHESIS
      - STAGE_5A_FAN_OUT (with sub-state per active layer: PENDING | IN_PROGRESS | COMPLETE)
      - STAGE_5B_COMPOSER
      - STAGE_5_GATE_PENDING
      - STAGE_6_ARCHITECTURE_AUDIT (with sub-state: AUDITING | RECONCILE_LOOP | COMPLETE)
      - STAGE_7_PLAN
      - STAGE_8_TESTS_AND_VALIDATORS
      - STAGE_9_CROSS_ARTIFACT_AUDIT (with sub-state: AUDITING | RECONCILE_LOOP | COMPLETE)
      - STAGE_10_RECONCILE (transient, invoked from 6 or 9)
      - STAGE_11_TASKS
      - BUILD_GATE_PENDING
      - APPROVED (terminal, success)
      - CANCELLED (terminal, user cancellation at any gate)
      - CYCLE_CAP_ESCALATION (sub-state: awaiting user direction)

State Transitions:
  NOT_STARTED → STAGE_0_PREFLIGHT (on /feature-pipeline invocation)
  STAGE_0_PREFLIGHT → STAGE_1_INTENT (preflight passes)
  STAGE_0_PREFLIGHT → CANCELLED (preflight critical failure)
  STAGE_1_INTENT.GATE_PENDING → STAGE_1_5_PRD (user approves intent)
  STAGE_1_INTENT.GATE_PENDING → CANCELLED (user cancels)
  STAGE_1_5_PRD.GATE_PENDING → STAGE_2_RESEARCH_PLAN (user approves PRD)              # NEW v4 transition
  STAGE_5A_FAN_OUT (all layer designers complete) → STAGE_5B_COMPOSER                 # NEW v4 transition
  STAGE_5B_COMPOSER (composer produces blueprint, doc-reviewer passes) → STAGE_5_GATE_PENDING
  STAGE_5_GATE_PENDING → STAGE_6_ARCHITECTURE_AUDIT (user approves blueprint)
  STAGE_6_ARCHITECTURE_AUDIT.RECONCILE_LOOP (cycle cap hit) → CYCLE_CAP_ESCALATION
  CYCLE_CAP_ESCALATION → STAGE_6_ARCHITECTURE_AUDIT (user adjusts; loop continues with explicit user guidance)
  CYCLE_CAP_ESCALATION → CANCELLED (user gives up)
  STAGE_11_TASKS → BUILD_GATE_PENDING
  BUILD_GATE_PENDING → APPROVED (user approves; pipeline complete; task DAG ready for execution)
  BUILD_GATE_PENDING → CANCELLED (user cancels)

System Invariants:
  - The orchestrator MUST be at exactly one state at any time per run
  - Issues-ledger.json MAY be updated within a stage; transitions MUST be append-only per ADR-0005
  - traceability.json MUST be kept consistent across state transitions
  - Per-layer designer states at Stage 5a (PENDING → IN_PROGRESS → COMPLETE) MAY be concurrent across designers; all must reach COMPLETE before transition to STAGE_5B_COMPOSER
  - Each iteration loop at Stage 6 or Stage 9 MAY repeat up to 4 times (cap from blueprint v3 §3.7); a 5th iteration MUST escalate to CYCLE_CAP_ESCALATION
  - document-reviewer iteration MAY occur within a stage's loop (its own prior_context_check mechanism); composes with the outer fixed-point iteration cap
```

---

### Frontend Design

**Authoring status (v4.2.0):** Substantive content authored at Phase 2 (T2.1). Full draft; subject to review-chain refinement in Phase 6.

This section describes the role of the `synth-designer-frontend` per-layer designer when invoked for a user feature touching the Frontend layer. It does NOT describe Frontend changes the v4 meta-blueprint itself makes (the v4 meta-blueprint physically modifies only Claude Code FS — see Project Filesystem & Claude Code Conventions section).

#### Research grounding

This section is authored from general design principles and the canonical Blueprint template's per-layer section structure. It is NOT research-grounded the way ADRs 0011-0018 are. The actual layer-specific design discipline (i.e., the body of `frontend-design-knowledge` skill) is deferred to Phase 2 of the Implementation Plan, where research-grounded skill bodies will be authored in a separate session with proper research backing per the pipeline's own discipline. The structure below identifies what the per-layer designer should produce; the substantive frontend-design discipline (which UI framework patterns to favor, which state-management approaches the skill recommends, etc.) is for that future authoring session.

#### Responsibility scope

`synth-designer-frontend` is invoked at Stage 5a when `00-feature-scope.json` has `frontend: true`. Its sole responsibility is to author the Frontend Design section of the user-feature blueprint under composition. It does NOT:
- Author cross-cutting sections (Overview, Design Summary, etc. — composer-only per ADR-0016)
- Author ADRs (composer-only per FR-5)
- Modify other layers' Design sections
- Make decisions outside the Frontend scope (it surfaces cross-layer concerns via `dependencies_on_other_layers` sidecar for composer reconciliation)

#### Inputs

- Rationale brief (per ADR-0009; orchestrator-generated; customized to Frontend scope — Decisions Inherited filtered to frontend-relevant ADRs, Files You Should Read scoped to frontend-relevant codebase analysis findings)
- Approved PRD (`01-5-prd-vN.md`) — for Frontend-relevant FRs and NFRs
- Codebase analysis JSON (`03-codebase-analysis.json`) — `focusAreas` filtered to frontend code paths, `dataTransformationPipelines` where Frontend is an endpoint
- Synthesis report (Stage 4 output) — for synthesis claims grounding Frontend design choices

#### Output structure

`synth-designer-frontend` writes `05a-frontend-design.md` conforming to a Frontend per-layer section structure that includes:

- **Component Inventory** — components added, modified, or removed; for each, name, props, state, render output, parent components, child components
- **State Management** — global state changes, local state additions, derived state, state hydration sources
- **Routing** — new routes, route guards, route parameters, deep-linking concerns
- **API Consumption** — endpoints this Frontend layer consumes; expected request/response shapes; error handling per endpoint (cross-layer dependency on API layer flagged via sidecar)
- **Accessibility** — ARIA roles, keyboard navigation paths, screen reader announcements, focus management
- **Styling Architecture** — styling approach (CSS-in-JS, utility classes, CSS modules, etc.), theme integration, responsive breakpoints
- **Build / Bundle Impact** — new dependencies and their bundle size impact, code-splitting points, lazy-load boundaries
- **Browser Compatibility** — supported browser matrix, polyfills required, progressive enhancement vs graceful degradation strategy

The sidecar `05a-frontend-dependencies.json` lists cross-layer assumptions (typically: API contract assumptions, Backend session-handling assumptions, CDN/static-asset hosting assumptions).

#### Layer-specific concerns

Frontend designer's most common cross-layer dependencies:
- **Frontend ↔ API**: contract shape, error response format, authentication flow, pagination/streaming protocols. Composer reconciles with API designer's output.
- **Frontend ↔ Backend (when no API layer)**: session handling, CSRF, server-side rendering boundaries
- **Frontend ↔ CI/CD**: build pipeline, asset optimization, deployment artifact format
- **Frontend ↔ IaC**: CDN configuration, edge function deployment, static-asset hosting

Frontend-specific design pitfalls the designer should avoid (informed by general frontend practice; not research-cited):
- Premature framework choice when PRD doesn't specify
- Over-specifying component implementation rather than component contracts
- Coupling routing decisions to specific framework router APIs
- Missing accessibility ACs (must be in EARS form, not implicit)

#### Layer-specific EARS AC patterns

Common EARS patterns for Frontend ACs:
- **Ubiquitous**: "The Frontend shall display the user's name in the header." (no trigger — always true)
- **Event-driven (When)**: "When the user submits the form, the Frontend shall validate inputs before sending."
- **State-driven (While)**: "While the user is unauthenticated, the Frontend shall display the login page."
- **Unwanted/Error (If-then)**: "If the API returns 401, then the Frontend shall redirect to the login route and preserve the current location for post-login navigation."
- **Optional Feature (Where)**: "Where dark-mode is enabled, the Frontend shall apply the dark color palette."

The designer groups these under a `## Acceptance Criteria — Frontend` subsection within the user-feature blueprint's Acceptance Criteria section.

#### Knowledge skill outline

`frontend-design-knowledge` (body authored in Implementation Plan Phase 2) should teach:
- The output structure above (so the designer knows what sections to produce)
- Cross-layer assumption emission discipline (when to add a `dependencies_on_other_layers` entry vs when to defer to composer)
- Common Frontend design pitfalls and how to avoid them
- EARS AC patterns specific to Frontend behaviors
- Heuristics for when a Frontend concern crosses into Backend, API, or CI/CD territory (composer-side resolution trigger)
- Examples of well-formed Frontend Design sections from prior runs (when the pipeline accumulates a corpus)

The skill MUST NOT teach specific framework choices, library recommendations, or implementation-level code samples. Those are user/feature decisions, not pipeline decisions. The skill teaches design-process discipline, not technology choices.

#### Test boundaries

For features touching the Frontend layer:
- **Unit tests**: components in isolation; mocked dependencies; tools per user's stack (Vitest, Jest, etc.)
- **Integration tests**: component composition; routing; state-management interactions
- **End-to-end tests**: full user flows; tools per stack (Playwright, Cypress, etc.) — these are typically covered in the e2e-test.md at Stage 8, not per-layer
- **Accessibility tests**: automated audit (axe, pa11y); keyboard-navigation tests

Mock boundary decisions for Frontend testing typically: mock API calls at the network layer (MSW or similar); use real component rendering; mock only third-party services with side effects.

#### Security considerations

For features touching the Frontend layer:
- **Input validation**: client-side validation is UX, not security; server-side validation is the security boundary (designer flags this as a Backend/API responsibility via cross-layer dependency)
- **XSS prevention**: framework-default escaping; no `dangerouslySetInnerHTML` or equivalent without explicit security justification
- **Sensitive data**: tokens, credentials never logged to console; never stored in localStorage if user agent is shared
- **CSRF**: same-site cookie defaults; explicit token handling if cross-origin

#### Integration with composer

Composer at Stage 5b consumes `05a-frontend-design.md` plus its dependencies sidecar. Composer's role for Frontend integration:
- Verify Frontend's API consumption assumptions match API designer's contract output (`05a-api-design.md`)
- Verify Frontend's CDN/static-asset assumptions match IaC designer's deployment topology
- Surface contradictions as `[UNRESOLVED]` markers if evidence-based arbitration cannot resolve
- Author cross-cutting sections (e.g., Architecture Overview's Frontend ↔ API ↔ Backend data flow) drawing on Frontend's Component Inventory and API Consumption sections

---

### Backend Design

**Authoring status (v4.2.0):** Substantive content authored at Phase 2 (T2.2).

This section describes the role of `synth-designer-backend` for user features touching the Backend layer. Does NOT describe changes the v4 meta-blueprint makes to Backend (none — meta-blueprint affects only Claude Code FS).

#### Research grounding

Same caveat as Frontend Design: authored from general principles; research-grounded `backend-design-knowledge` skill body is deferred to Implementation Plan Phase 2.

#### Responsibility scope

`synth-designer-backend` is invoked at Stage 5a when `00-feature-scope.json` has `backend: true`. Sole responsibility: author the Backend Design section of the user-feature blueprint. Does NOT author cross-cutting sections, ADRs, or other layers' sections.

#### Inputs

- Rationale brief (Backend-scoped)
- Approved PRD — Backend-relevant FRs/NFRs
- Codebase analysis JSON — `focusAreas` filtered to backend code paths; `dataTransformationPipelines` with Backend stages
- Synthesis report

#### Output structure

`synth-designer-backend` writes `05a-backend-design.md` covering:

- **Module Inventory** — modules added, modified, or removed; for each: name, responsibility, public surface, internal collaborators
- **Request / Response Handling** — for features with API surface: routing logic, middleware chain, request validation, response shaping (cross-layer dependency: actual endpoint contracts are API designer's responsibility)
- **Application Logic** — business-rule placement, domain model integration, service-layer boundaries
- **Background Jobs / Async Work** — queue mechanism, job scheduling, retry semantics, idempotency
- **Persistence Boundary** — how Backend invokes Query layer; transaction boundaries; consistency requirements (cross-layer dependency on Query, Database)
- **External Integrations** — third-party API calls, message queues, file storage; auth method; error handling
- **Concurrency Model** — threading, async/await, locking, distributed coordination
- **Observability Hooks** — log statements (semantic, not implementation), metric emission points, trace span boundaries
- **Configuration** — runtime configuration sources (env vars, config files), startup validation, hot-reload boundaries

Sidecar `05a-backend-dependencies.json` lists cross-layer assumptions (typically: API contract assumptions, Query interface assumptions, IaC service-discovery assumptions, Database schema availability).

#### Layer-specific concerns

Backend designer's most common cross-layer dependencies:
- **Backend ↔ API**: which endpoints Backend serves; Backend's response generation must match API's declared contract
- **Backend ↔ Query**: data access patterns Backend invokes; transaction scope ownership
- **Backend ↔ Database**: schema reliance; migration timing
- **Backend ↔ IaC**: service deployment topology, scaling characteristics, secret injection
- **Backend ↔ CI/CD**: build artifact format, test running, deployment trigger

Backend-specific pitfalls to avoid:
- Hidden coupling to Query implementation details (Backend should declare data needs, not query mechanics)
- Mixing transactional and non-transactional logic without explicit boundary
- Synchronous external API calls in request path without timeout/circuit-breaker
- Background-job invocation without idempotency guarantees

#### Layer-specific EARS AC patterns

- **Ubiquitous**: "The Backend shall reject requests larger than 10MB."
- **When**: "When a successful user-registration request completes, the Backend shall enqueue a welcome-email job."
- **While**: "While the database connection pool is exhausted, the Backend shall return 503 with Retry-After header."
- **If-then**: "If a downstream service returns 5xx, then the Backend shall retry with exponential backoff up to 3 times before failing the request."
- **Where**: "Where feature flag `new-checkout` is enabled for the user, the Backend shall route to the new checkout service."

Grouped under `## Acceptance Criteria — Backend` subsection.

#### Knowledge skill outline

`backend-design-knowledge` (body in Implementation Plan Phase 2) should teach:
- Output structure above
- Module-boundary discipline (when to add a new module vs extend existing)
- Cross-layer assumption emission (when Backend's design depends on Database, Query, API contract decisions)
- Async-work design patterns (queues, retries, idempotency, dead-letter handling)
- Configuration-as-code discipline (no hard-coded secrets, env-var validation at startup)
- EARS AC patterns specific to Backend behaviors

Skill MUST NOT teach specific framework choices (Express vs FastAPI vs Spring), language picks, or library-specific implementation. Those are user/feature decisions.

#### Test boundaries

- **Unit tests**: individual modules in isolation; dependency injection for collaborators
- **Integration tests**: module composition; real-or-mocked database (per user's test discipline); real Query layer
- **Contract tests**: Backend's responses match API designer's declared contracts (cross-layer test, surfaces in e2e-test.md)
- **Load tests**: where NFR specifies throughput/latency targets

Mock boundary decisions: mock external services with side effects (third-party APIs, payment processors); use real Query layer with test database; use real internal collaborators.

#### Security considerations

- **Authentication**: identity-establishment is cross-cutting; Backend enforces but doesn't define (per Architecture Auditor cross-cutting concern)
- **Authorization**: per-endpoint or per-resource enforcement; explicit policy declarations
- **Input validation**: server-side validation is the security boundary; Frontend validation is UX only
- **Secrets**: from configured secret store; never logged; never returned in responses
- **Dependency security**: declared in Configuration section; CVE scanning is CI/CD designer's concern
- **Rate limiting**: per-endpoint or global; coordinated with API layer's rate-limit contract

#### Integration with composer

Composer at Stage 5b:
- Verifies Backend's API surface matches API designer's contract
- Verifies Backend's Query usage matches Query designer's interface
- Verifies Backend's Database schema reliance matches Database designer's schema
- Surfaces inconsistencies as critique input
- Authors Architecture Overview's Backend-related data flows
- Authors top-level Components section drawing on Backend's Module Inventory

---

### API Design

**Authoring status (v4.2.0):** Substantive content authored at Phase 2 (T2.3).

This section describes the role of `synth-designer-api` for user features touching the API layer. Does NOT describe changes the v4 meta-blueprint makes to API (none — meta-blueprint affects only Claude Code FS).

#### Research grounding

Same caveat: authored from general principles; research-grounded `api-design-knowledge` skill body is deferred to Implementation Plan Phase 2.

#### Responsibility scope

`synth-designer-api` is invoked at Stage 5a when `00-feature-scope.json` has `api: true`. Sole responsibility: author the API Design section. Does NOT author cross-cutting sections, ADRs, or other layers.

#### Inputs

- Rationale brief (API-scoped)
- Approved PRD — endpoints, contracts, NFRs
- Codebase analysis JSON — existing API endpoints and their patterns
- Synthesis report — auth-strategy, versioning-strategy, rate-limiting findings if researched

#### Output structure

`synth-designer-api` writes `05a-api-design.md` covering:

- **Endpoint Inventory** — endpoints added, modified, deprecated, removed; for each: HTTP method + path (or RPC method), purpose, authentication requirement, authorization policy
- **Request Contracts** — per endpoint: request shape (params, query, headers, body), validation rules, content-type negotiation
- **Response Contracts** — per endpoint: success response shape and status codes, error response shape and status codes, headers, content-type
- **Versioning Strategy** — version mechanism (URI path, header, content-type), compatibility commitments, deprecation timeline
- **Authentication & Authorization** — auth mechanism per endpoint (or globally), token format, scope/role model; cross-layer dependency on Backend for enforcement
- **Rate Limiting** — limits per endpoint or globally, identification mechanism (API key, user ID, IP), response on exceeded
- **Pagination / Streaming** — pagination mechanism (cursor, offset, page), streaming endpoints (SSE, websocket, chunked), max-size limits
- **Error Response Conventions** — canonical error shape, error code taxonomy, retry-after semantics for transient errors
- **OpenAPI / Schema Output** — whether feature produces a machine-readable spec; format; consumers

Sidecar `05a-api-dependencies.json` lists cross-layer assumptions (typically: Backend implementation assumptions, IaC routing/gateway assumptions, Frontend consumption assumptions).

#### Layer-specific concerns

API designer's most common cross-layer dependencies:
- **API ↔ Backend**: Backend must serve the endpoints API defines; contract mismatch is a primary failure mode
- **API ↔ Frontend**: Frontend's API consumption assumptions must match API contracts
- **API ↔ IaC**: gateway/load-balancer configuration, TLS termination, ingress rules
- **API ↔ Database**: indirect — API contracts constrain Backend's data-access patterns

API-specific pitfalls to avoid:
- Inconsistent error response shapes across endpoints (caller code complexity explodes)
- Breaking changes without versioning
- Coupling auth to a specific Backend implementation rather than an abstract policy
- Specifying rate limits without specifying identification (key-by-IP vs key-by-user is a different policy)
- Missing pagination on potentially-large response lists

#### Layer-specific EARS AC patterns

- **Ubiquitous**: "The API shall include a `X-Request-ID` header in every response for correlation."
- **When**: "When a request lacks required authentication, the API shall respond 401 with `WWW-Authenticate` header."
- **While**: "While the rate limit for an API key is exceeded, the API shall respond 429 with `Retry-After` header set to seconds until reset."
- **If-then**: "If an endpoint version is deprecated, then the API shall include a `Deprecation` header naming the sunset date and successor endpoint."
- **Where**: "Where a request includes `Accept: application/vnd.example.v2+json`, the API shall serve the v2 response format."

Grouped under `## Acceptance Criteria — API` subsection.

#### Knowledge skill outline

`api-design-knowledge` (body in Implementation Plan Phase 2) should teach:
- Output structure above
- Contract-first vs implementation-first design (and which the pipeline favors)
- Versioning strategy tradeoffs (URI vs header vs content-type)
- Error response taxonomy (e.g., problem+json, custom format)
- Auth model design (bearer tokens, API keys, mTLS, OAuth flows) — at the contract level, not implementation
- Pagination patterns (cursor vs offset) and when each is appropriate
- OpenAPI/AsyncAPI spec authoring discipline
- EARS AC patterns for API behaviors

Skill MUST NOT teach specific framework choices (Express vs FastAPI vs Spring vs Hono), spec-format-tool choices (Swagger UI vs Redoc), or implementation libraries.

#### Test boundaries

- **Contract tests**: validate endpoint behavior matches declared contracts (request shape, response shape, status codes)
- **Auth tests**: every endpoint with auth requirement tested for: missing auth → 401, wrong auth → 403, expired auth → 401 with refresh hint
- **Rate-limit tests**: limits enforced; reset behavior correct; headers correct
- **Versioning tests**: deprecated endpoints still work until sunset; new versions don't break old clients (until intentional removal)
- **Error-shape tests**: error responses match canonical shape for all error paths

Mock boundary decisions: mock Backend implementation when testing API behavior at contract level; use real API when testing Backend integration.

#### Security considerations

- **Auth bypass**: every endpoint that requires auth tested for bypass attempts (missing token, invalid token, expired token, token-from-different-user)
- **Authorization bypass**: every endpoint that requires authorization tested for bypass (correct auth but wrong role/scope)
- **Injection surfaces**: query params, path params, request body — all are inputs; designer flags Backend's input-validation responsibility
- **Rate-limit bypass**: identification mechanism robust against trivial bypass (e.g., IP-only limits trivially bypassed; key-based is stronger)
- **CORS**: if API serves browser clients, CORS policy explicit; preflight handled
- **TLS**: HTTPS required for all production endpoints; TLS version floor (e.g., TLS 1.2 minimum)
- **Sensitive data in URLs**: tokens, credentials never in query params or path (always in headers or body)

#### Integration with composer

Composer at Stage 5b:
- Verifies API contracts match Frontend's API consumption assumptions (reconciles via evidence-based arbitration)
- Verifies API endpoints match Backend's served-endpoints declarations
- Verifies API routing matches IaC's ingress/gateway configuration
- Authors cross-cutting Interface Change Matrix rows for new/changed endpoints
- Authors Architecture Overview's API surface description

---

### Query & Data Access Design

**Authoring status (v4.2.0):** Substantive content authored at Phase 2 (T2.4).

This section describes the role of `synth-designer-query` for user features touching the Query / Data Access layer. Does NOT describe changes the v4 meta-blueprint makes to Query layer (none — meta-blueprint affects only Claude Code FS).

#### Research grounding

Same caveat: authored from general principles; research-grounded `query-design-knowledge` skill body is deferred to Implementation Plan Phase 2.

#### Responsibility scope

`synth-designer-query` is invoked at Stage 5a when `00-feature-scope.json` has `query: true`. Sole responsibility: author the Query & Data Access Design section. Does NOT author cross-cutting sections, ADRs, or other layers.

#### Inputs

- Rationale brief (Query-scoped)
- Approved PRD — data-related FRs/NFRs (latency targets, consistency requirements)
- Codebase analysis JSON — existing data-access patterns; ORM/query-builder choices
- Synthesis report — caching-strategy, transaction-model findings

#### Output structure

`synth-designer-query` writes `05a-query-design.md` covering:

- **Data-Access Method Inventory** — query/repository methods added, modified, removed; for each: name, parameters, return shape, called from (which Backend module)
- **Query Patterns** — read patterns (single-row, list with pagination, aggregations), write patterns (single-row, bulk, upsert), join patterns
- **Transaction Boundaries** — which methods are transactional; transaction propagation across calls; isolation-level requirements
- **Caching Strategy** — cache layer (in-memory, distributed cache), cache keys, invalidation triggers, stale-data tolerance
- **N+1 Avoidance** — explicit eager-loading or batch-loading strategies for relationship traversal
- **Query Performance Targets** — latency budgets per query class (read vs write vs aggregation); plan for measurement
- **Pagination Implementation** — cursor vs offset, ordering stability, total-count behavior
- **Data Migrations Triggered** — when Query layer needs Database schema changes (cross-layer dependency on Database designer)
- **ORM / Query-Builder Boundaries** — where raw SQL is acceptable, where ORM-only, why

Sidecar `05a-query-dependencies.json` lists cross-layer assumptions (typically: Database schema assumptions, Backend transaction-boundary assumptions, caching infrastructure assumptions).

#### Layer-specific concerns

Query designer's most common cross-layer dependencies:
- **Query ↔ Database**: schema shape; indexes available; database-specific feature reliance (e.g., PostgreSQL JSON ops, MySQL FULLTEXT)
- **Query ↔ Backend**: which methods Backend invokes; transaction-ownership model
- **Query ↔ IaC**: database connection pool sizing; read-replica routing; cache infrastructure
- **Query ↔ CI/CD**: migration execution timing; data-seeding for tests

Query-specific pitfalls to avoid:
- Returning ORM entities up the stack (couples Backend to ORM mechanics)
- N+1 queries hidden in relationship traversal
- Implicit transaction boundaries (every public method should declare its transactional behavior)
- Cache invalidation deferred to "later"
- Performance targets without measurement plan

#### Layer-specific EARS AC patterns

- **Ubiquitous**: "The Query layer shall return paginated lists with a maximum of 100 items per page."
- **When**: "When a record is updated, the Query layer shall invalidate dependent cache entries."
- **While**: "While a transaction is in progress, the Query layer shall serialize concurrent writes to the same row."
- **If-then**: "If a query exceeds 1000ms, then the Query layer shall log a slow-query warning with the parameterized query text."
- **Where**: "Where read replicas are configured, the Query layer shall route SELECT queries to the replica pool."

Grouped under `## Acceptance Criteria — Query` subsection.

#### Knowledge skill outline

`query-design-knowledge` (body in Implementation Plan Phase 2) should teach:
- Output structure above
- Method-boundary discipline (when to add a new repository method vs parameterize an existing one)
- Transaction-design patterns (per-request, saga, two-phase commit)
- Caching patterns (cache-aside, read-through, write-through) and invalidation strategies
- Pagination implementation tradeoffs
- N+1 detection and avoidance
- EARS AC patterns for Query behaviors

Skill MUST NOT teach specific ORM choices (Hibernate vs JPA vs ActiveRecord vs Drizzle vs Prisma), database-specific dialect tricks, or implementation-level code.

#### Test boundaries

- **Unit tests**: query methods in isolation; in-memory or test-double database
- **Integration tests**: real database with test schema; transaction rollback per test
- **Performance tests**: where NFR specifies latency targets; representative data volume
- **Migration tests**: forward and backward migrations exercised in CI

Mock boundary decisions: test against a real database (test-instance or container) rather than mocking the database; mock only when database integration is genuinely out of scope.

#### Security considerations

- **SQL injection**: parameterized queries only; no string concatenation of user input
- **Authorization in query**: row-level access control where required (multi-tenant scenarios); filter clauses always include tenant/owner predicates
- **Sensitive data**: PII fields masked or omitted in non-privileged query paths
- **Cache poisoning**: cache keys include security-relevant context (don't share cache entries across users for user-specific data)
- **Connection-pool exhaustion**: query timeouts; rejection at limit; observability for pool saturation

#### Integration with composer

Composer at Stage 5b:
- Verifies Query's Database schema assumptions match Database designer's schema
- Verifies Query's transaction model matches Backend's transaction-boundary expectations
- Surfaces inconsistencies as critique input
- Authors cross-cutting Data Flow descriptions involving Query-layer transformations

---

### Database Schema & Migration Design

**Authoring status (v4.2.0):** Substantive content authored at Phase 2 (T2.5).

This section describes the role of `synth-designer-database` for user features touching the Database layer. Does NOT describe changes the v4 meta-blueprint makes to Database (none — meta-blueprint affects only Claude Code FS).

#### Research grounding

Same caveat: authored from general principles; research-grounded `database-design-knowledge` skill body is deferred to Implementation Plan Phase 2.

#### Responsibility scope

`synth-designer-database` is invoked at Stage 5a when `00-feature-scope.json` has `database: true`. Sole responsibility: author the Database Schema & Migration Design section. Does NOT author cross-cutting sections, ADRs, or other layers.

#### Inputs

- Rationale brief (Database-scoped)
- Approved PRD — data model requirements; consistency requirements
- Codebase analysis JSON — existing schema; existing migrations; current data volumes (where known)
- Synthesis report — schema-design patterns, online-migration strategies (where researched)

#### Output structure

`synth-designer-database` writes `05a-database-design.md` covering:

- **Schema Changes** — tables added, modified, removed; columns added, modified, removed; for each: name, type, nullability, default, comment
- **Constraints** — primary keys, foreign keys, unique constraints, check constraints; deferred-vs-immediate
- **Indexes** — indexes added, modified, removed; for each: columns, type (B-tree, GIN, hash, partial, expression), purpose (query support, uniqueness enforcement), creation strategy (online vs offline)
- **Data Migrations** — data transformations required at migration time; batch size; rollback strategy
- **Backward Compatibility Window** — for online migrations: how long both old and new schema must coexist; what reads/writes are valid in each state
- **Migration Order** — for multi-step migrations: explicit ordering with dependencies between steps
- **Rollback Plan** — for each migration step: how to roll back; what data state is preserved vs lost on rollback
- **Data Retention / Archival** — for new data: retention policy; archival mechanism; GDPR-style deletion compliance
- **Database-Specific Features Used** — features tied to specific database engine (PostgreSQL JSONB, MySQL generated columns, etc.); flagged as portability constraints

Sidecar `05a-database-dependencies.json` lists cross-layer assumptions (typically: IaC database-engine-version assumptions, Query layer compatibility, CI/CD migration-execution timing).

#### Layer-specific concerns

Database designer's most common cross-layer dependencies:
- **Database ↔ Query**: schema is Query's contract; schema changes can break Query methods
- **Database ↔ Backend**: indirect via Query, but Backend transaction semantics rely on Database isolation guarantees
- **Database ↔ IaC**: database engine version, instance class, storage configuration, replication topology
- **Database ↔ CI/CD**: when migrations execute (deployment-time vs separately); test-database refresh strategy

Database-specific pitfalls to avoid:
- Non-online schema changes on production-scale tables without explicit downtime acknowledgment
- Missing indexes for foreign keys (delete cascades scan the dependent table)
- Adding NOT NULL constraint to existing column without backfill plan
- Deleting columns or tables without deprecation window for caller code
- Migration without rollback path
- Schema decisions that bake in single-tenant assumptions (when multi-tenancy might be needed)

#### Layer-specific EARS AC patterns

- **Ubiquitous**: "The Database shall enforce uniqueness on (tenant_id, slug) for all rows in the `features` table."
- **When**: "When a row is deleted from `users`, the Database shall cascade-delete dependent rows in `user_settings`."
- **While**: "While a long-running migration is in progress, the Database shall allow concurrent reads on the affected table."
- **If-then**: "If a write would violate a foreign key constraint, then the Database shall return an integrity error referencing the constraint name."
- **Where**: "Where the database engine is PostgreSQL 15 or later, the migration shall use `CREATE INDEX CONCURRENTLY`."

Grouped under `## Acceptance Criteria — Database` subsection.

#### Knowledge skill outline

`database-design-knowledge` (body in Implementation Plan Phase 2) should teach:
- Output structure above
- Normalization tradeoffs (when 3NF, when denormalize)
- Index design discipline (covering indexes, partial indexes, expression indexes)
- Online migration patterns (expand-contract / parallel change / one-way doors)
- Backward compatibility window discipline
- Rollback discipline for every migration step
- Data retention and archival patterns
- EARS AC patterns for Database behaviors

Skill MUST NOT teach specific database choices (PostgreSQL vs MySQL vs SQLite), engine-specific dialect, or implementation tools.

#### Test boundaries

- **Schema tests**: migrations run forward and backward; expected schema state asserted after each
- **Constraint tests**: each constraint exercises both valid and invalid inserts/updates
- **Index tests**: queries benefiting from indexes use them (EXPLAIN plans asserted)
- **Migration timing tests**: for online migrations, simulated concurrent traffic during migration

Mock boundary decisions: NO mocking of database engine for these tests — they require real engine to be meaningful. Use a containerized or in-memory version of the production engine.

#### Security considerations

- **Encryption at rest**: required for production databases; flagged as IaC concern
- **Encryption in transit**: TLS for connections; client certificate verification where appropriate
- **Access control**: principle of least privilege per database user; per-schema permissions
- **Sensitive data**: PII columns flagged for separate encryption (column-level or application-level); audit log
- **Backup security**: backups encrypted; backup access logged
- **Migration security**: migration user has minimum required permissions; never `SUPERUSER` unless unavoidable

#### Integration with composer

Composer at Stage 5b:
- Verifies Database schema matches Query designer's data-access assumptions
- Verifies Database engine version matches IaC designer's provisioned version
- Verifies migration timing matches CI/CD designer's deployment pipeline
- Surfaces inconsistencies as critique input
- Authors cross-cutting Data Contracts section drawing on Database schema

---

### CI/CD (GitHub Actions) Design

**Authoring status (v4.2.0):** Substantive content authored at Phase 3 (T3.1).

This section describes the role of `synth-designer-cicd` for user features touching the CI/CD layer. Does NOT describe changes the v4 meta-blueprint makes to CI/CD (none — meta-blueprint affects only Claude Code FS; future scope is to integrate the pipeline AS a CI workflow but that's deferred).

#### Research grounding

Same caveat: authored from general principles; research-grounded `cicd-design-knowledge` skill body is deferred to Implementation Plan Phase 2.

#### Responsibility scope

`synth-designer-cicd` is invoked at Stage 5a when `00-feature-scope.json` has `cicd: true`. Sole responsibility: author the CI/CD Design section. Does NOT author cross-cutting sections, ADRs, or other layers.

#### Inputs

- Rationale brief (CI/CD-scoped)
- Approved PRD — automation requirements, deployment cadence, environment-promotion model
- Codebase analysis JSON — existing workflows in `.github/workflows/`; reusable actions used
- Synthesis report — action SHA-pinning practice, secrets-management strategy

#### Output structure

`synth-designer-cicd` writes `05a-cicd-design.md` covering:

- **Workflow Inventory** — workflows added, modified, removed; for each: trigger events (push, PR, schedule, dispatch), purpose, success criteria
- **Job Structure** — within each workflow: jobs, their `needs` dependencies, matrix strategies, runner choices (ubuntu-latest, self-hosted, etc.)
- **Step Sequencing** — within each job: checkout, setup, build, test, deploy steps with explicit ordering
- **Secrets & Variables** — secrets referenced (organization, repository, environment-scoped); environment variables set
- **Action Pinning** — third-party actions used; pinning strategy (SHA, version tag, never `@main`); justification per ADR if non-SHA
- **Branch Protections** — required status checks; review requirements; merge-strategy constraints
- **Concurrency Controls** — workflow-level concurrency groups; cancel-in-progress semantics
- **Caching Strategy** — what's cached (dependencies, build artifacts), cache keys, restoration fallbacks
- **Artifact Outputs** — build artifacts produced; retention; consumers (release workflows, deployment workflows)
- **Reusable Workflows / Composite Actions** — extracted reusable units; their inputs/outputs

Sidecar `05a-cicd-dependencies.json` lists cross-layer assumptions (typically: Backend build-command assumptions, Frontend build-command assumptions, IaC deployment-mechanism assumptions, Database migration-execution timing).

#### Layer-specific concerns

CI/CD designer's most common cross-layer dependencies:
- **CI/CD ↔ Backend/Frontend**: build commands, test commands, lint commands per layer
- **CI/CD ↔ Database**: migration execution step; test database initialization
- **CI/CD ↔ IaC**: deployment mechanism (kubectl apply, terraform apply, deploy script invocation); promotion gates
- **CI/CD ↔ Codespaces**: shared base image where applicable; dev/prod parity

CI/CD-specific pitfalls to avoid:
- Action pinning by version tag (`@v3`) instead of SHA — supply-chain attack surface (claim research-direction; not specifically cited)
- Secrets passed via workflow logs (echo $TOKEN)
- Fork PR with privileged secrets (default behavior is safer; explicit opt-in required and justified)
- No concurrency control on deploy workflows (race conditions in deployments)
- Missing fail-fast on critical steps (workflows continue after failure)
- Branch protection requiring only checks that pass trivially (false sense of safety)

#### Layer-specific EARS AC patterns

- **Ubiquitous**: "The CI workflow shall block merge until all required status checks pass."
- **When**: "When a pull request is opened, the CI shall run the lint, test, and build jobs in parallel."
- **While**: "While a deployment workflow is in progress for an environment, subsequent deployments to that environment shall be queued, not parallelized."
- **If-then**: "If the deploy job fails, then the workflow shall create a GitHub issue with the run URL and failure summary."
- **Where**: "Where the changes touch the `backend/` directory, the CI shall run the backend integration test job."

Grouped under `## Acceptance Criteria — CI/CD` subsection.

#### Knowledge skill outline

`cicd-design-knowledge` (body in Implementation Plan Phase 2) should teach:
- Output structure above
- Workflow-vs-job-vs-step granularity discipline
- Secrets-handling discipline (org vs repo vs environment-scoped)
- Action SHA-pinning rationale and exceptions
- Branch-protection composition (what required checks should be)
- Fork PR security (default deny; explicit allow with justification)
- Concurrency control patterns
- EARS AC patterns for CI/CD behaviors

Skill MUST NOT teach specific tools (GitHub Actions vs CircleCI vs Jenkins — pipeline assumes GitHub Actions per Layer Scope) or workflow snippets.

#### Test boundaries

CI/CD testing has different shape than runtime layers:
- **Workflow syntax tests**: `act` or `actionlint` to validate workflow files locally
- **Dry-run tests**: deployment workflows runnable in dry-run mode against ephemeral environments
- **Action-update tests**: when third-party actions are updated, CI verifies behavior unchanged
- **End-to-end tests**: scheduled workflow that exercises full deploy-and-rollback cycle in a staging environment

Mock boundary decisions: where possible, use real CI infrastructure (GitHub-hosted runners); for syntax/validation testing, use `actionlint` and similar.

#### Security considerations

- **Action supply chain**: third-party actions pinned to SHA; pin justification documented; updates tracked in dependency security review
- **Secrets minimization**: only the secrets each job needs (no `secrets: inherit` for sensitive workflows)
- **Fork PR boundary**: PRs from forks do NOT receive privileged secrets by default; explicit allow-listing for trusted contributors only
- **OIDC vs PAT**: prefer OIDC for cloud deploys (no long-lived credentials); PAT only when OIDC unavailable
- **Approval gates for production**: production deploys require human approval (GitHub environment with required reviewers)
- **Audit log preservation**: workflow logs retained per compliance requirements

#### Integration with composer

Composer at Stage 5b:
- Verifies CI/CD build commands match Backend, Frontend, etc. designer's build outputs
- Verifies CI/CD deploy steps match IaC's deployment mechanism
- Verifies CI/CD migration step matches Database designer's migration timing
- Surfaces inconsistencies as critique input
- Authors cross-cutting Implementation Plan section drawing on CI/CD's workflow inventory

---

### Infrastructure as Code Design

**Authoring status (v4.2.0):** Substantive content authored at Phase 3 (T3.2).

This section describes the role of `synth-designer-iac` for user features touching the IaC layer. Does NOT describe changes the v4 meta-blueprint makes to IaC (none — meta-blueprint affects only Claude Code FS).

#### Research grounding

Same caveat: authored from general principles; research-grounded `iac-design-knowledge` skill body is deferred to Implementation Plan Phase 2.

#### Responsibility scope

`synth-designer-iac` is invoked at Stage 5a when `00-feature-scope.json` has `iac: true`. Sole responsibility: author the Infrastructure as Code Design section. Does NOT author cross-cutting sections, ADRs, or other layers.

#### Inputs

- Rationale brief (IaC-scoped)
- Approved PRD — infrastructure NFRs (scalability, availability, latency, geographic distribution)
- Codebase analysis JSON — existing IaC modules; tool in use (Terraform/CloudFormation/Pulumi/Bicep)
- Synthesis report — module-structure patterns, state-management strategies, secret-handling

#### Output structure

`synth-designer-iac` writes `05a-iac-design.md` covering:

- **Resource Inventory** — resources added, modified, removed; for each: cloud service, resource type, key properties, dependencies on other resources
- **Module Structure** — modules added, modified; their inputs (variables) and outputs; module composition
- **Environment Topology** — environments (dev, staging, prod, etc.); resource differentiation per environment; promotion mechanism
- **State Management** — state backend (remote state location); locking mechanism; state-file segmentation strategy
- **Secret Handling** — where secrets originate (KMS, Vault, cloud secret store); how IaC references them (data sources, not literals); rotation handling
- **Networking** — VPC/network topology, subnets, routing, security groups, ingress/egress rules
- **IAM / Access Control** — service identities, role assumptions, principle of least privilege
- **Observability Resources** — logging destinations, metric collection, alerting policies
- **Cost Considerations** — estimated cost impact; cost-optimization choices (instance class, storage tier, etc.)
- **Drift Detection** — mechanism for detecting manual changes; reconciliation strategy
- **Disaster Recovery** — backup configuration, multi-region setup (if applicable), recovery time/point objectives

Sidecar `05a-iac-dependencies.json` lists cross-layer assumptions (typically: Backend deployment-target assumptions, Database engine-version availability, CI/CD deployment-mechanism integration).

#### Layer-specific concerns

IaC designer's most common cross-layer dependencies:
- **IaC ↔ Backend**: where Backend runs (container, VM, serverless); scaling characteristics; configuration injection
- **IaC ↔ Database**: database engine + version provisioned; instance class; backup configuration; read-replica topology
- **IaC ↔ CI/CD**: deployment mechanism (how CI/CD invokes infrastructure changes); state-modification permissions
- **IaC ↔ API**: gateway/load-balancer configuration; TLS certificates; DNS records

IaC-specific pitfalls to avoid:
- Hard-coded secrets in IaC files (never; reference via data sources)
- Manual changes "fixing" IaC state (drift; document or revert)
- Missing environment isolation (dev resources writable from prod credentials)
- No state-file locking (concurrent applies corrupt state)
- IAM over-permission (`*:*` policies)
- Production resources without backup/snapshot configuration
- Cost-optimization deferred to "later" (compounds quickly)

#### Layer-specific EARS AC patterns

- **Ubiquitous**: "All production databases shall have automated backups configured with 7-day retention."
- **When**: "When a new environment is provisioned, the IaC shall create network isolation from other environments by default."
- **While**: "While a terraform apply is in progress, the state-file lock shall prevent concurrent modifications."
- **If-then**: "If a resource is removed from IaC, then the destroy plan shall require explicit user confirmation before execution."
- **Where**: "Where the environment is production, the IaC shall enforce multi-AZ deployment for stateful resources."

Grouped under `## Acceptance Criteria — IaC` subsection.

#### Knowledge skill outline

`iac-design-knowledge` (body in Implementation Plan Phase 2) should teach:
- Output structure above
- Module-boundary discipline (when to extract a module vs inline)
- State management discipline (segmentation, locking, backup)
- Secret-handling patterns (data sources, KMS integration)
- Environment promotion patterns
- IAM least-privilege discipline
- Drift detection and reconciliation
- Cost-awareness in design choices
- EARS AC patterns for IaC behaviors

Skill MUST NOT teach specific tool choices (Terraform vs CloudFormation vs Pulumi vs Bicep), cloud-provider specifics, or implementation-level HCL/YAML/code samples.

#### Test boundaries

- **Plan tests**: `terraform plan` (or equivalent) produces expected diff; no unexpected resource changes
- **Module tests**: unit tests for module inputs/outputs using framework-appropriate tool (Terratest, etc.)
- **Compliance tests**: policy-as-code checks (OPA, Sentinel, tfsec) enforce security and cost rules
- **Drift tests**: scheduled run detects manual changes; reports to ops channel
- **Disaster recovery tests**: periodic restore from backup; verify RTO/RPO targets

Mock boundary decisions: where possible, test against real cloud infrastructure (in ephemeral test environments); mock only when cloud-API rate limits or cost make real testing impractical.

#### Security considerations

- **Secrets**: never literal in IaC files; always referenced via secret-store data sources
- **State files**: encrypted at rest (S3 server-side encryption, etc.); encrypted in transit; access logged
- **IAM**: least privilege; no `*:*`; explicit principal allowlists
- **Network**: default-deny security groups; explicit allow rules; no `0.0.0.0/0` ingress without justification
- **TLS**: enforced for all network ingress; certificates managed (cert-manager, ACM, etc.)
- **Audit logging**: all IaC changes via CI/CD pipeline (no manual applies); pipeline runs logged with attribution
- **Disaster recovery**: backups encrypted; cross-region replication for critical state; restore procedure tested

#### Integration with composer

Composer at Stage 5b:
- Verifies IaC's provisioned database matches Database designer's engine version
- Verifies IaC's networking allows Backend's required egress (DNS, third-party APIs)
- Verifies IaC's secret-store configuration matches Backend's expected configuration source
- Surfaces inconsistencies as critique input
- Authors cross-cutting Security Considerations section drawing on IaC's network and IAM design

---

### Dev Environment (Codespaces) Design

**Authoring status (v4.2.0):** Substantive content authored at Phase 3 (T3.3).

This section describes the role of `synth-designer-codespaces` for user features touching the Dev Environment layer. Does NOT describe changes the v4 meta-blueprint makes to Dev Environment (none — meta-blueprint affects only Claude Code FS).

#### Research grounding

Same caveat: authored from general principles; research-grounded `codespaces-design-knowledge` skill body is deferred to Implementation Plan Phase 2.

#### Responsibility scope

`synth-designer-codespaces` is invoked at Stage 5a when `00-feature-scope.json` has `codespaces: true`. Sole responsibility: author the Dev Environment Design section. Does NOT author cross-cutting sections, ADRs, or other layers.

#### Inputs

- Rationale brief (Codespaces-scoped)
- Approved PRD — developer experience requirements, environment setup expectations
- Codebase analysis JSON — existing `.devcontainer/` configuration; current setup scripts
- Synthesis report — devcontainer patterns, post-create-hook discipline

#### Output structure

`synth-designer-codespaces` writes `05a-codespaces-design.md` covering:

- **Base Image / Image Selection** — base image (Microsoft, custom, or community); rationale; image-update strategy
- **Features Added** — devcontainer features (language toolchains, CLI tools); version pinning
- **Post-Create Hooks** — scripts run after container creation (one-time setup); idempotency requirements
- **Post-Start Hooks** — scripts run on each start; should be fast and idempotent
- **Port Forwarding** — ports forwarded to local; labels; auto-forward-on-start vs explicit
- **VS Code Configuration** — extensions installed by default; settings overrides; recommended extensions
- **Environment Variables** — variables set in devcontainer; secrets handling (Codespaces secrets vs env files)
- **Volume Mounts** — host-volume mounts; named volumes; persistence boundary
- **Multi-Service Composition** — Docker Compose for multi-container dev environments (e.g., app + database + cache)
- **Resource Allocation** — machine-type recommendations; memory/CPU/storage sizing
- **Onboarding Time Target** — expected time from "Open in Codespaces" click to functional dev environment

Sidecar `05a-codespaces-dependencies.json` lists cross-layer assumptions (typically: Backend dev-mode startup, Frontend dev-server startup, Database test-instance configuration, CI/CD parity expectations).

#### Layer-specific concerns

Codespaces designer's most common cross-layer dependencies:
- **Codespaces ↔ Backend**: development-mode invocation, hot-reload configuration, debugger attachment
- **Codespaces ↔ Frontend**: dev server invocation, hot module replacement, source-map serving
- **Codespaces ↔ Database**: dev database instance (containerized vs cloud); seed-data loading
- **Codespaces ↔ CI/CD**: parity between Codespaces and CI runtime (avoid "works on my Codespace" failures)

Codespaces-specific pitfalls to avoid:
- Heavy post-create scripts (long onboarding time discourages use)
- Unpinned tool versions (devcontainer behavior drifts)
- Missing port forwarding for in-development services
- Secrets in plaintext devcontainer files (always Codespaces secrets)
- Mixing host-volume mounts with cross-platform development (Linux vs Mac vs Windows differences)
- Resource specs too small for the actual workload

#### Layer-specific EARS AC patterns

- **Ubiquitous**: "The devcontainer shall expose port 3000 (frontend) and 8000 (backend) on Codespaces creation."
- **When**: "When a Codespace is created, the post-create script shall install dependencies, seed the test database, and validate environment in under 5 minutes."
- **While**: "While the dev container is running, the database container shall be healthy and accessible at `db:5432`."
- **If-then**: "If a required environment variable is unset on startup, then the post-start hook shall fail with a clear error message naming the missing variable."
- **Where**: "Where the project includes a Backend service, the devcontainer shall include the Backend's language toolchain and debugger."

Grouped under `## Acceptance Criteria — Dev Environment` subsection.

#### Knowledge skill outline

`codespaces-design-knowledge` (body in Implementation Plan Phase 2) should teach:
- Output structure above
- Devcontainer-feature selection and pinning
- Post-create vs post-start hook discipline (one-time vs every-start)
- Port-forwarding configuration
- Multi-service Docker Compose patterns
- Secrets handling (Codespaces secrets, environment files)
- Onboarding time minimization
- Cross-platform considerations (Linux container on Mac/Windows host)
- EARS AC patterns for Dev Environment behaviors

Skill MUST NOT teach specific tool versions, language picks, or implementation-level config snippets.

#### Test boundaries

- **Devcontainer build tests**: container builds from clean state; expected tools present
- **Post-create idempotency tests**: post-create script run twice produces same final state
- **Service-availability tests**: after creation, expected services responding on expected ports
- **Onboarding-time tests**: scheduled measure of "create to ready" duration
- **Cross-platform tests**: container behavior verified on Mac, Windows, and Linux hosts (where applicable)

Mock boundary decisions: use real Docker for these tests; mock only when external service dependencies make real testing impractical (e.g., cloud-backed secrets — use local secret simulation).

#### Security considerations

- **Secrets**: only via Codespaces secrets (organization or repo-scoped); never literal in devcontainer files
- **Base image source**: use trusted registries (Microsoft, GitHub, official Docker Hub publishers); pin to specific tags
- **Feature source**: devcontainer features from official catalog or pinned commits; review third-party features
- **Network egress**: dev environments may have broader egress than production; document and accept the gap
- **Persistent storage**: volumes are persistent across Codespace recreations only via named volumes; ephemeral by default
- **VS Code extension trust**: extensions installed by default reviewed for trust posture

#### Integration with composer

Composer at Stage 5b:
- Verifies Codespaces' Backend invocation matches Backend designer's dev-mode startup
- Verifies Codespaces' database setup matches Database designer's dev-instance requirements
- Verifies Codespaces' port forwarding covers all services declared by other layers
- Surfaces inconsistencies as critique input
- Authors cross-cutting Onboarding section in Implementation Plan (if needed)

---

### Claude Code / Project Filesystem Design (substantive content)

This is the only layer in scope for v4. The Project Filesystem & Claude Code Conventions section above covers the file-level changes. This subsection covers the design-level mechanics that span those files.

#### Orchestrator skill body modifications

The orchestrator skill body (at `.claude/skills/feature-pipeline/SKILL.md`) gains the following responsibility expansions in v4:

**Stage 1.5 sequencing.** After Stage 1 (Intent Clarification doc) completes and Intent Confirmation Gate clears, orchestrator:
1. Generates rationale brief per ADR-0009 for the document-reviewer invocation; brief includes inherited ADRs, the approved Intent Clarification doc as Files You Should Read, and the Open Item "verify template conformance per `doc_type: IntentClarification` rules in `documentation-criteria`".
2. Invokes document-reviewer with `doc_type: IntentClarification` on the approved doc.
3. If verdict is `needs_revision` or `rejected`, regenerates rationale brief (now carrying prior reviewer issues as Open Items) and invokes synth-reconcile to produce revised version; loops up to 4 cycles per fixed-point discipline.
4. When approved, generates fresh rationale brief for synth-prd-author; brief Decisions Inherited section lists all inherited ADRs including ADR-0012 (PRD as Stage 1.5), ADR-0015 (EARS for ACs); Files You Should Read names the approved Intent Clarification doc + PRD template reference in `documentation-criteria`; Open Items lists any user-clarification questions surfaced at Stage 1 that should inform PRD content.
5. Invokes synth-prd-author with the brief prepended to its invocation prompt; synth-prd-author writes `01-5-prd-v1.md`.
6. Generates rationale brief for the PRD-stage document-reviewer invocation (brief references the just-completed PRD authoring).
7. Invokes document-reviewer with `doc_type: PRD` on synth-prd-author's output.
8. Loops as above if needs revision (each iteration regenerates brief with prior issues as Open Items).
9. Presents PRD Approval Gate to the user via AskUserQuestion `[approve / refine / cancel]`.
10. If approved, transitions to Stage 2.
11. If `refine`, generates rationale brief incorporating user's refinement direction as a new Open Item; invokes synth-reconcile to produce `01-5-prd-v(N+1).md`.
12. If `cancel`, transitions to CANCELLED terminal state.

The same rationale-brief discipline applies to Stage 5a (per-layer designers) and Stage 5b (composer) per ADR-0009 Layer-1 enforcement. Specifically:
- Each per-layer designer at Stage 5a receives a layer-customized brief (Decisions Inherited filtered to layer-relevant ADRs; Files You Should Read scoped to layer-relevant codebase analysis sections; Open Items For Upstream surface any layer-specific concerns surfaced at PRD review).
- synth-designer-composer at Stage 5b receives a brief enumerating all activated layers and cross-layer dependency declarations from per-layer sidecars; Files You Should Read includes all `05a-*-design.md` outputs and `05a-*-dependencies.json` files.
- document-reviewer at all 5 invocation points receives a brief listing the stage's expected `doc_type` rules and any prior_context_check items from previous reviewer invocations on the same artifact.

**Stage 5a fan-out + Stage 5b fan-in coordination.** After Stage 4 (synthesis) completes, orchestrator:
1. Reads `00-feature-scope.json` Layer Scope flags.
2. For each flag set to `true`, dispatches the corresponding per-layer designer via Agent tool. Parallel dispatch using multiple Agent invocations (Claude Code platform supports concurrent sub-agent calls). Orchestrator generates rationale brief per ADR-0009 for each designer; brief is customized to that layer's scope (Decisions Inherited, Open Items From Upstream, Files You Should Read are filtered to layer-relevant content).
3. Waits for ALL activated designers to complete (synchronous join — claim C-R2-0030 Anthropic spawn guidance for moderately complex tasks).
4. **Per-layer designer structural check (orchestrator-side, addresses I-AA-001).** For each completed per-layer designer's output:
   - Read `05a-<layer>-design.md` and verify required sections exist per the canonical Blueprint template's `<Layer> Design` subsection structure.
   - Verify EARS-format AC keywords used (When/While/If-then/Where/Ubiquitous) per ADR-0015; no BDD or freeform ACs.
   - Verify `05a-<layer>-dependencies.json` exists (may be empty array if designer made no cross-layer assumptions) and conforms to schema in §Contract Definitions.
   - If structural check fails for a designer's output, invoke synth-reconcile scoped to that single designer's output; reconcile produces `05a-<layer>-design-v(N+1).md`; re-run structural check; loop with 4-cycle cap; on cap-hit, escalate to Cycle-Cap Escalation Gate with the failing layer named.
   - This is an orchestrator-side inline check, NOT a document-reviewer sub-agent invocation. document-reviewer invocation count remains at 5 per ADR-0017 (document-reviewer reviews the COMPOSED blueprint at Stage 5b, not per-layer outputs).
5. **Composer-only ADR authorship enforcement (orchestrator-side scan, addresses I-AA-002).** Before invoking composer, orchestrator scans `working/feature/<slug>/adrs/` for any new ADR files created at Stage 5a (i.e., created after the run's Stage 4 synthesis ADRs but before composer invocation). If any are found, this is a critical violation of FR-5 (composer-only ADR authorship). Orchestrator:
   - Records the violation in the issues-ledger with severity `critical`, category `compliance`
   - Moves the offending ADR files to `working/feature/<slug>/adrs/_violation-quarantine/` with a marker file naming the originating per-layer designer
   - Invokes synth-reconcile on the offending per-layer designer's output with the violation as prior_context, instructing the designer to surface the architectural concern as a `proposed_supersession` entry in its output rather than authoring an ADR directly
   - Re-runs the per-layer designer; if violation re-occurs, escalate to Cycle-Cap Escalation Gate
   - This enforcement is instruction-based at the knowledge-skill layer (per-layer design knowledge skills teach: "DO NOT author ADRs; surface architectural questions in your output for the composer to address") AND orchestrator-side scan-based. Future enhancement (if Claude Code adds path-restricted Write): tighten per-layer designer's Write tool to its layer-specific output paths only, making the violation structurally impossible rather than caught-after-the-fact.
6. Invokes synth-designer-composer with:
   - All per-layer outputs (`05a-*-design.md` files) that passed structural check
   - All per-layer dependency sidecars (`05a-*-dependencies.json` files)
   - Approved PRD path
   - Codebase analysis JSON path
   - Rationale brief (per ADR-0009; composer's brief enumerates all activated layers and cross-layer dependency declarations gathered from sidecars)
7. Composer produces `05-blueprint-v1.md`.
8. Invokes document-reviewer with `doc_type: DesignDoc` and `codebase_analysis` parameter populated from `03-codebase-analysis.json`.
9. Loops via synth-reconcile if needs revision.
10. Presents Blueprint Approval Gate.

**Five document-reviewer invocation points.** Codified per ADR-0017. Orchestrator manages each invocation's `prior_context_check` carry-forward when iterating.

#### Sub-agent definition discipline

All 12 new sub-agent files and 2 renamed sub-agent files follow the same discipline:
- YAML frontmatter: `name`, `description`, `tools`, `skills`, `memory` (project), `maxTurns`, `model` (only for synth-cross-artifact-auditor which declares `opus`).
- Body: stage-specific role, behavioral guidance, output format expectations.
- NO `Agent` in tools list (recursion-safe per ADR-0001).
- Knowledge skills referenced in `skills:` field must use correct frontmatter per ADR-0010 (no `disable-model-invocation: true`).

#### Knowledge skill discipline

All new and renamed knowledge skills follow ADR-0010 corrected frontmatter pattern:
- `user-invocable: false` (hidden from `/` menu)
- NO `disable-model-invocation: true` (would break sub-agent preload)
- Description tightly scoped to "Internal knowledge for the feature-pipeline's <X> stage. Loaded by sub-agents in that pipeline."
- Body content: stage-specific or layer-specific guidance, process discipline, common failure modes to avoid.

#### documentation-criteria extension

Per ADR-0011, the canonical document skill is extended with:
- `## Template: PRD` section containing the PRD template from uploaded PDR.txt.
- `## Template: Blueprint` section containing the Blueprint template from uploaded BluePrint.txt.
- `## Template: ADR` section containing the ADR template from uploaded ADR.txt.
- `## Template: IntentClarification` section — derived from v3's Intent Clarification doc format.
- `## Template: Plan` section — derived from v3's plan.json shape + Blueprint template's Implementation Plan section.
- `## Shared Conventions` section: frontmatter format, supersession discipline, traceability rules, the "Honoring the Rationale Brief" instruction text (Layer-2 enforcement from ADR-0009).

Estimated total size: 35-50K tokens. Within kill criterion threshold of 50K specified in ADR-0011.

#### document-reviewer template extension

The `document-reviewer` sub-agent definition (uploaded template adopted as-is, extended for v4) gains:
- `doc_type` taxonomy: `IntentClarification` and `Plan` added to existing `PRD`, `ADR`, `UISpec`, `DesignDoc`.
- For each new doc_type, corresponding Gate 0 required-element check list referenced from `documentation-criteria` skill.
- All other discipline (Gate 0/Gate 1 separation, JSON output, prior_context_check, severity/category taxonomy) preserved verbatim from the uploaded template.

---

### Error Handling

| Error Category | Example | Detection | Recovery Strategy | User Impact |
|---------------|---------|-----------|-------------------|-------------|
| Preflight failure | Skill frontmatter has `disable-model-invocation: true` + `skills:` preload | Stage 0 verification scan | Halt pipeline with clear error message identifying offending skill | User informed; user fixes skill before re-invocation |
| MCP unavailable | GitNexus configured but not responding | Stage 0 health check | Fall through to fallback MCP (codebase-memory-mcp); if neither, degraded mode with explicit `meta_warning` | User informed; pipeline proceeds in degraded mode |
| Sub-agent invocation failure | synth-prd-author returns malformed output (e.g., missing frontmatter) | document-reviewer Gate 0 fails | synth-reconcile loop produces new version; iteration cap 4 | User sees reconcile-iteration in progress messages |
| document-reviewer verdict: `rejected` | Document fails fundamental requirements (missing critical sections; major template violations) | document-reviewer JSON output `verdict.decision == "rejected"` | synth-reconcile loop; if 4 cycles hit without progress, escalate to Cycle-Cap Gate | User sees gate after cap |
| Cross-layer contradiction unresolvable at composer | Two per-layer designers' assumptions conflict; no evidence to arbitrate | Composer flags `[UNRESOLVED]` marker in blueprint | document-reviewer surfaces `critical` issue; synth-reconcile loop with explicit user guidance via prior_context | User informed via Critique-1 issue triage |
| Iteration cap reached | 4 cycles of critique-reconcile without convergence | Orchestrator counter | Escalate to Cycle-Cap Escalation Gate (5th human gate) | User sees gate; provides direction or cancels |
| User cancellation at any gate | User clicks `cancel` at any approval gate | AskUserQuestion response | Transition to CANCELLED state; preserve all artifacts per ADR-0005; emit run summary | Run terminates; user can resume via re-invocation with feature-slug |
| Sub-agent recursion attempt | Sub-agent attempts to use Agent tool | Tool-allowlist enforcement by Claude Code platform | Tool call fails with error; sub-agent must complete without sub-agent invocation | Sub-agent surfaces as `proposed_supersession` or `deferred_to_<stage>` in its output |
| Context budget exhausted | Sub-agent's working context fills before completion | Sub-agent context monitoring or hit maxTurns limit | Sub-agent emits partial output with `[INCOMPLETE: reason]` marker; orchestrator surfaces this to next critique stage | Critique stage detects, surfaces as `important` issue |
| Per-layer designer fails to emit `dependencies_on_other_layers` | Per-layer designer assumes cross-layer fact but emits no sidecar | Composer detects missing sidecar during fan-in | Composer treats absence as "no cross-layer dependencies"; if blueprint references cross-layer content without sidecar, document-reviewer Gate 1 flags it | Document-reviewer flags |
| Per-layer designer output fails structural check at Stage 5a | Designer's `05a-<layer>-design.md` missing required template subsections, or uses non-EARS AC syntax, or sidecar JSON malformed | Orchestrator-side inline structural check after each per-layer designer completes (addresses I-AA-001) | Invoke synth-reconcile scoped to that single designer; reconcile produces revised version; re-run structural check; 4-cycle cap; on cap-hit, escalate to Cycle-Cap Gate naming the failing layer | User sees reconcile-iteration for the specific layer; composer invocation deferred until all per-layer outputs pass |
| Per-layer designer attempts to author an ADR | Designer writes an ADR file to `working/feature/<slug>/adrs/` at Stage 5a despite knowledge-skill instruction to surface architectural questions for composer | Orchestrator-side scan post-Stage-5a (addresses I-AA-002) before composer invocation | Quarantine offending ADR; record `critical` violation in issues-ledger; invoke synth-reconcile on the offending designer with violation as prior_context; re-run designer; if violation re-occurs, escalate to Cycle-Cap Gate | User informed; designer iteration runs |

### Logging and Monitoring

The feature-pipeline produces filesystem artifacts as its primary observable output; logging is artifact-based rather than runtime-log-based. However:

- **Log events**: Stage transitions are recorded in `traceability.json`; issue transitions are recorded in `issues-ledger.json`; gate decisions are recorded in `gates-log.json` (new in v4).
- **Log levels**: Not applicable in conventional sense. All events are recorded at full fidelity in the run directory.
- **Sensitive data**: The pipeline does NOT log user-provided intent verbatim if it contains apparent PII; intent-clarifier's `01-intent-clarification.md` is the canonical record; orchestrator-side messages use feature-slug references.
- **Metrics**: Per-run metrics emitted as `metrics.json` at run completion: total turns per sub-agent, wall-clock duration per stage, iteration counts per critique loop, gate decision history.
- **Traces**: Each sub-agent invocation is traceable via its output artifact + traceability.json + (optionally) Claude Code's session log.
- **Alerts**: Not applicable — the pipeline is interactive; the user is the operator in real-time.
- **Dashboards**: Not applicable in v4. Future scope: per-feature dashboard surfacing run history.
## Implementation Plan

### Implementation Approach

**Selected Approach**: Phased rollout in 7 phases, each phase producing testable artifacts. Phases follow a dependency-ordered sequence: foundation skills first (documentation-criteria extension), then sub-agent inventory changes, then orchestrator updates, then retroactive ADR migration, then full pipeline integration test.

**Selection Reason**: This sequence minimizes the window in which the pipeline is in a hybrid state (some components v4, others v3). The documentation-criteria extension is foundational — every other change depends on the templates being available. Sub-agent inventory changes are next because the orchestrator update references the new sub-agents. The retroactive ADR migration is a parallel workstream that can proceed independently. Full pipeline integration test is last, ensuring all components compose correctly.

### Technical Dependencies and Implementation Order

#### Required Implementation Order

1. **Phase 1: documentation-criteria skill extension**
   - Layer: Claude Code / Project Filesystem
   - Technical Reason: Every subsequent change references templates from this skill (PRD authoring, Blueprint composition, ADR authoring, document-reviewer doc_type extension)
   - Dependent Elements: All sub-agents that author or review documents; all ADRs (new authoring) and old ADRs (retroactive migration)
   - Tasks:
     - Author IntentClarification template (derive from v3's intent-clarification doc shape)
     - Author Plan template (derive from v3's plan.json shape + Blueprint template's Implementation Plan section)
     - Embed uploaded PRD template (PDR.txt) as `## Template: PRD` section
     - Embed uploaded Blueprint template (BluePrint.txt) as `## Template: Blueprint` section
     - Embed uploaded ADR template (ADR.txt) as `## Template: ADR` section
     - Author `## Shared Conventions` section (frontmatter format, supersession discipline, traceability rules)
     - Embed the "Honoring the Rationale Brief" instruction text (Layer-2 enforcement from ADR-0009)

2. **Phase 2: New knowledge skills**
   - Layer: Claude Code / Project Filesystem
   - Technical Reason: New sub-agents reference these in their `skills:` frontmatter
   - Prerequisites: Phase 1 complete (skills reference documentation-criteria)
   - Tasks:
     - `prd-authoring-knowledge`: PRD authoring process, AI-PRD failure-mode avoidance content (per claim C-R3-0014 — fabrication, over-precision, implementation-leak avoidance; per claim C-R3-0017 user-story count guidance)
     - `design-composition-knowledge`: Integration patterns; evidence-based arbitration discipline for cross-layer conflicts; Fact Disposition Table authoring; cross-cutting section authoring; ADR introduction discipline
     - 9 layer-specific design knowledge skills (research-grounded skill bodies authored in this phase; blueprint v4.2.0 Per-Layer Design sections provide the structural target each skill teaches against):
       - `claude-code-fs-design-knowledge`: Skill, Subagent, Slash Command, Hook, MCP, CLAUDE.md authoring patterns; recursion-safety enforcement; skill frontmatter discipline per ADR-0010
       - `frontend-design-knowledge`: component design, state management, accessibility, styling architecture, client-side routing, build-tool integration
       - `backend-design-knowledge`: application logic structure, request/response handling, background jobs, internal module boundaries, service lifecycle
       - `api-design-knowledge`: endpoint definitions, request/response contracts, versioning strategies, authentication/authorization, rate limiting, error response conventions
       - `query-design-knowledge`: ORM patterns, query construction discipline, transaction boundaries, caching strategies, N+1 avoidance, query performance
       - `database-design-knowledge`: schema design, normalization tradeoffs, migration patterns (up + down), indexes, constraints, data integrity, online schema change discipline
       - `cicd-design-knowledge`: GitHub Actions workflow files, job structure, secrets management, branch protections, action SHA-pinning, OIDC vs PAT, fork PR handling
       - `iac-design-knowledge`: Terraform/CloudFormation/Pulumi module structure, state management, environment promotion, drift detection, secret handling
       - `codespaces-design-knowledge`: devcontainer config, post-create hooks, port forwarding, tool installation, multi-service Docker Compose, VS Code extensions
     - Rename `critique-1-knowledge` → `architecture-audit-knowledge` (content preserved)
     - Rename `critique-2-knowledge` → `cross-artifact-audit-knowledge` (content preserved)

3. **Phase 3: Sub-agent inventory changes**
   - Layer: Claude Code / Project Filesystem
   - Technical Reason: Orchestrator references these by name; agent files must exist at `.claude/agents/` paths before orchestrator updates
   - Prerequisites: Phase 1 + Phase 2 complete (sub-agents reference templates via documentation-criteria; reference knowledge skills via `skills:` field)
   - Tasks:
     - Create `synth-prd-author.md` (new sub-agent definition)
     - Create `synth-designer-composer.md` (new)
     - Create 9 per-layer designer sub-agents (`synth-designer-<layer>.md`)
     - Rename `synth-critic-1.md` → `synth-architecture-auditor.md` (content preserved with skill reference update)
     - Rename `synth-critic-2.md` → `synth-cross-artifact-auditor.md` (content preserved)
     - Update `document-reviewer.md`: doc_type taxonomy extended with `IntentClarification` and `Plan`; corresponding Gate 0 required-element checklists reference `documentation-criteria`

4. **Phase 4: ADR retroactive migration**
   - Layer: Claude Code / Project Filesystem
   - Technical Reason: Existing ADRs 0001-0010 should follow the canonical template for cross-ADR consistency before blueprint v4 ships
   - Prerequisites: Phase 1 complete (canonical template available in documentation-criteria)
   - Tasks (per ADR-0014 §Implementation Guidance):
     - For each ADR 0001 through 0010 (plus ADR-0007 v1):
       - Copy original to `<original-filename>-pre-template-migration.md`
       - Author new version structurally per canonical ADR template, preserving original Context/Decision/Rationale text verbatim where it fits
       - Add `Decision Details` table (4 rows: Why now / Why this / Known unknowns / Kill criteria)
       - Move Architecture Impact content to separate section
       - Confirm Implementation Guidance is principle-only (move procedures elsewhere if present)
       - Frontmatter: `version: 2.0.0`, `supersedes: [{id: ADR-XXXX, version: 1.0.0}]`
     - Note: This phase can proceed concurrently with Phases 2-3 (independent workstream)

5. **Phase 5: Orchestrator skill updates**
   - Layer: Claude Code / Project Filesystem
   - Technical Reason: Orchestrator is the last component because it references sub-agents (Phase 3) and templates (Phase 1)
   - Prerequisites: Phases 1-3 complete
   - Tasks:
     - Add Stage 1.5 sequencing logic
     - Add PRD Approval Gate logic
     - Add Stage 5a fan-out + Stage 5b fan-in coordination logic
     - Add document-reviewer invocations at 5 points
     - Update sub-agent name references (synth-critic-1 → synth-architecture-auditor; synth-critic-2 → synth-cross-artifact-auditor)
     - Extend Stage 0 preflight to verify v4 sub-agent and skill inventory presence

6. **Phase 6: Blueprint v4 finalization + downstream stage updates**
   - Layer: Claude Code / Project Filesystem
   - Technical Reason: Blueprint v4 (this document) is itself the artifact being produced; downstream stages must consume its structure correctly
   - Prerequisites: Phase 1 complete; Phase 4 complete (so blueprint v4's ADR references are to template-migrated versions)
   - Tasks:
     - Finalize blueprint v4 with document-reviewer review and synth-architecture-auditor review (as required by the pipeline's own discipline — "we eat our dog food" per user direction)
     - Update v3's downstream-stage knowledge skills (planning-knowledge, acceptance-testing-knowledge, task-decomposition-knowledge) to consume the canonical Blueprint template structure
     - Verify acceptance-testing-knowledge teaches EARS-format AC consumption

7. **Phase 7: Pipeline integration test (vertical slice)**
   - Layer: Claude Code / Project Filesystem
   - Technical Reason: End-to-end verification that all v4 changes compose correctly
   - Prerequisites: All prior phases complete
   - Tasks:
     - Run v4 pipeline against a small test feature (e.g., "add a /healthz endpoint" from blueprint v3's example)
     - Verify: Stage 1.5 produces PRD; PRD Approval Gate fires; Stage 5a activates appropriate per-layer designers; Stage 5b composer produces integrated blueprint conforming to template; document-reviewer fires at 5 points; renamed critics invoke correctly; EARS-format ACs produced
     - Verify: traceability.json captures the v4 topology correctly
     - Verify: issues-ledger.json receives document-reviewer issues
     - Document any discrepancies; iterate if necessary

#### Cross-Layer Sequencing Notes

- **Skills before sub-agents**: knowledge skills must exist with correct frontmatter (per ADR-0010) before sub-agents reference them; sub-agent dispatch fails fast if a referenced skill is missing or has broken frontmatter.
- **Sub-agents before orchestrator updates**: orchestrator references sub-agents by name; renamed agents (synth-architecture-auditor, synth-cross-artifact-auditor) must exist at new path before orchestrator updates reference them.
- **documentation-criteria extension before ADR retroactive migration**: the canonical template (lived in documentation-criteria after Phase 1) is the structural target for retroactive migration. Migration can't proceed without it.
- **Blueprint v4 publication is parallel with downstream-stage updates**: blueprint v4 is itself the test artifact for the v4 pipeline; downstream-stage knowledge skills (planning-knowledge, etc.) must be ready to consume its structure for integration test in Phase 7.

### Migration Strategy

**Backward compatibility with v3 runs:**
- v3 run artifacts at `working/feature/<slug>/` (any prior runs) are preserved per ADR-0005. The v4 installation does NOT migrate them.
- Resume semantics: if a user re-invokes the pipeline against a feature-slug that has a v3 run in progress, the orchestrator detects the v3 artifacts and offers two options: (a) continue the v3 run to completion via the v3 pipeline (if v3 sub-agents are still installed), (b) start a fresh v4 run with the same intent (preserves the v3 directory under `working/feature/_v3-archived/`).
- This is a user-facing decision presented via AskUserQuestion at Stage 0 preflight when v3 artifacts are detected.

**Synthesize pipeline coexistence:**
- The synthesize skill continues to work unchanged. Its 6 shared sub-agents (synth-extractor through synth-synthesizer) are not modified by v4.
- ADR-0010 frontmatter fix (already declared in v3) applies retroactively to the synthesize pipeline's 6 knowledge skills. This is a one-time, separate workstream documented in ADR-0010 §Implementation Guidance.

**ADR retroactive migration cutover:**
- Pre-migration ADR versions preserved as `<original-filename>-pre-template-migration.md` per ADR-0014. These are reference artifacts; v4 pipeline references the migrated versions only.
- Cross-references in v3 blueprint to ADRs 0001-0010 continue to resolve (v3 references are by ID, not by version; the migrated v2.0.0 versions are the current at any ID lookup).

### Feature Flags & Rollout

No feature flags. The pipeline is a developer tool; v4 supersedes v3 entirely once installed. Users choosing not to upgrade can keep v3 installed; the two are independent installations (different skill names or different `.claude/skills/feature-pipeline/` content depending on user preference).

For users who want a staged rollout:
- Phase A (validate): install v4 alongside v3 (rename v3 to `.claude/skills/feature-pipeline-v3/` and install v4 at `.claude/skills/feature-pipeline/`). Run a test feature through v4 to verify correctness against expectations. Both can coexist if skills are named differently.
- Phase B (commit): remove v3 installation once v4 is validated.

## Security Considerations

### Cross-Cutting

- **Authentication & Authorization**: The feature-pipeline runs inside a Claude Code session under the user's own credentials; no separate authentication. The pipeline does not introduce any service that needs auth. The user's own access controls (filesystem permissions, MCP credentials if any) are the only auth boundary.
- **Input Validation**: User intent at Stage 1 is free-form text. synth-intent-clarifier processes it; orchestrator does not interpret raw user intent for control flow. AskUserQuestion responses are constrained by the platform (option-selection or text-input as configured). No injection attack surfaces in pipeline control flow.
- **Sensitive Data Handling**: The pipeline does NOT exfiltrate user intent or run artifacts to any external service. All processing happens locally in the Claude Code session. MCPs (GitNexus, codebase-memory-mcp) are local processes; no network egress for code-graph queries.

### Frontend

For user features touching the Frontend layer, `synth-designer-frontend`'s Security Considerations subsection covers:
- **XSS prevention**: framework-default escaping; no unsafe-render APIs without explicit security justification
- **Sensitive data in client storage**: tokens not in localStorage if user agent might be shared; sensitive PII never logged to console
- **CSRF**: same-site cookie defaults; explicit token handling for cross-origin
- **Subresource integrity**: third-party scripts/styles loaded with SRI hashes
- **Content Security Policy**: CSP headers configured (cross-layer dependency on Backend or IaC for header injection)
- **Client-side validation NOT a security boundary**: server-side validation (Backend/API) is the boundary; Frontend validation is UX only

### Backend

For user features touching the Backend layer, `synth-designer-backend`'s Security Considerations subsection covers:
- **Authentication enforcement** (identity verification is cross-cutting; Backend enforces per endpoint)
- **Authorization policy**: per-endpoint or per-resource enforcement; explicit policy declarations
- **Input validation**: server-side validation is the security boundary; all inputs treated as untrusted
- **Secrets handling**: from configured secret store (never literal); never logged; never returned in responses
- **Dependency CVE management**: declared in Configuration section; scanning is CI/CD's concern (cross-layer)
- **Rate limiting**: per-endpoint or global; coordinated with API designer
- **Output encoding**: when Backend's response is consumed by Frontend or other consumers, encoding is explicit (JSON, etc.)

### API

For user features touching the API layer, `synth-designer-api`'s Security Considerations subsection covers:
- **Auth bypass tests**: every endpoint with auth requirement tested for missing/invalid/expired token
- **Authorization bypass tests**: every endpoint with authorization tested for cross-user / wrong-scope access
- **Injection surfaces**: query params, path params, body — designer flags Backend's input-validation responsibility
- **Rate-limit identification robustness**: not IP-only (trivially bypassed); prefer key-based
- **CORS policy**: explicit when serving browser clients; preflight handled
- **TLS enforcement**: HTTPS for all production endpoints; TLS 1.2 minimum
- **Sensitive data in URLs**: never (always in headers or body)

### Query

For user features touching the Query / Data Access layer, `synth-designer-query`'s Security Considerations subsection covers:
- **SQL injection prevention**: parameterized queries only; no string concatenation of user input
- **Row-level access control**: filter clauses always include tenant/owner predicates in multi-tenant scenarios
- **PII handling**: PII fields masked or omitted in non-privileged query paths
- **Cache key segmentation**: cache keys include security-relevant context (don't share cache across users for user-specific data)
- **Connection-pool exhaustion**: query timeouts; rejection at limit; observability for pool saturation

### Database

For user features touching the Database layer, `synth-designer-database`'s Security Considerations subsection covers:
- **Encryption at rest**: required for production; flagged as IaC concern
- **Encryption in transit**: TLS for connections; client certificate verification where appropriate
- **Principle of least privilege**: per-database-user permissions; per-schema permissions
- **PII columns**: separate encryption (column-level or application-level); audit log
- **Backup security**: backups encrypted; backup access logged
- **Migration security**: migration user has minimum required permissions; never `SUPERUSER` unless unavoidable

### CI/CD

For user features touching the CI/CD layer, `synth-designer-cicd`'s Security Considerations subsection covers:
- **Action supply chain**: third-party actions pinned to SHA; pin justification documented
- **Secrets minimization**: only the secrets each job needs; no `secrets: inherit` for sensitive workflows
- **Fork PR boundary**: fork PRs do NOT receive privileged secrets by default; explicit allow-listing required and justified
- **OIDC vs PAT**: prefer OIDC for cloud deploys (no long-lived credentials)
- **Production deploy approval gates**: human approval required via GitHub environment with required reviewers
- **Audit log preservation**: workflow logs retained per compliance

### IaC

For user features touching the IaC layer, `synth-designer-iac`'s Security Considerations subsection covers:
- **No literal secrets** in IaC files; always referenced via secret-store data sources
- **State file security**: encrypted at rest; encrypted in transit; access logged
- **IAM least privilege**: no `*:*`; explicit principal allowlists
- **Network default-deny**: explicit allow rules; no `0.0.0.0/0` ingress without justification
- **TLS enforced** for all network ingress; certificates managed
- **Audit logging**: all IaC changes via CI/CD pipeline (no manual applies); pipeline runs logged with attribution
- **Disaster recovery**: backups encrypted; cross-region replication for critical state

### Codespaces

For user features touching the Dev Environment layer, `synth-designer-codespaces`'s Security Considerations subsection covers:
- **Secrets**: only via Codespaces secrets (organization or repo-scoped); never literal in devcontainer files
- **Base image trust**: from trusted registries (Microsoft, GitHub, official Docker Hub publishers); pinned tags
- **Feature trust**: devcontainer features from official catalog or pinned commits; third-party reviewed
- **Network egress**: dev environments may have broader egress than production; document and accept the gap
- **VS Code extension trust**: default-installed extensions reviewed for trust posture

### Claude Code / Project Filesystem (in-scope security)

- **Skill auto-invocability**: Per ADR-0010, knowledge skills MUST set `user-invocable: false` AND MUST NOT set `disable-model-invocation: true`. The consequence (skills become auto-invocable by Claude in main session) is a minor security concern: a pipeline knowledge skill might fire spuriously in an unrelated session. Mitigated by tight description scoping ("Internal knowledge for the feature-pipeline's <X> stage. Loaded by sub-agents in that pipeline.").
- **MCP credential scope**: If GitNexus or codebase-memory-mcp are configured to access remote services (currently they run locally, but future versions may add cloud sync), the pipeline must NOT log MCP credentials in its artifacts or rationale briefs. Mitigated by document-reviewer's Gate 1 sensitive-data check.
- **Recursion safety**: Sub-agents MUST NOT have `Agent` in their tools list (ADR-0001). Enforced by Claude Code platform; verified by Stage 0 preflight.
- **User input in rationale briefs**: The brief includes the user's intent statement. If a user supplies PII in their intent, the brief carries that PII into every sub-agent's invocation. Mitigated by orchestrator-side prompt: "The user's intent statement may contain PII; sub-agents MUST NOT echo PII into their outputs unless functionally necessary."
- **document-reviewer's WebSearch tool**: document-reviewer has WebSearch in its tools list (per uploaded template). This is for technical-claim verification per the template's "Technical Information Verification Guidelines" section. WebSearch queries are logged by Claude Code's session log; user should be aware that document-reviewer may submit search queries derived from document content.

## Test Boundaries

### Mock Boundary Decisions

| Component/Dependency | Mock? | Rationale |
|---------------------|-------|-----------|
| GitNexus MCP | Yes (for unit testing sub-agent behavior) | Production GitNexus runs locally but may be unavailable in CI; mock fixtures provide reproducible test inputs. Real GitNexus used in integration tests. |
| codebase-memory-mcp MCP | Yes (same rationale as above) | Same. |
| User AskUserQuestion responses | Yes (for unit tests of gate logic) | Tests simulate gate decisions; real-user-driven integration tests cover the actual interactive behavior. |
| Filesystem (`working/feature/<slug>/`) | No | Real filesystem used; tests create temporary directories. Filesystem is the pipeline's state model; mocking it would test against a fiction. |
| Claude Code platform (Agent tool, Skill loader) | No | Real Claude Code used; tests run as actual pipeline invocations. |
| Sub-agent LLM outputs | Yes for orchestrator unit tests; no for integration tests | Orchestrator-unit tests use canned sub-agent outputs to verify orchestration logic; integration tests use real LLM with cost budget. |

### Data Layer Testing Strategy

N/A — pipeline has no database. State is filesystem-based. Testing strategy:
- **Filesystem state shape**: For each stage, verify the artifact files exist at expected paths with expected frontmatter and structure.
- **Issue ledger**: Verify state transitions are append-only; verify prior_context_check carry-forward across iterations.
- **Traceability.json**: Verify ADR ↔ requirement ↔ blueprint section ↔ task mappings are bidirectional and complete.

### Per-Layer Test Strategy

| Layer | Test Type | Tooling | Location |
|-------|-----------|---------|----------|
| Claude Code / Project Filesystem | Unit (sub-agent behavior with mocked inputs) | Manual via test scripts; canned input files | `tests/unit/` (new test directory) |
| Claude Code / Project Filesystem | Integration (full pipeline run against test feature) | Manual via `/feature-pipeline "test feature"` invocation; observe artifacts | `tests/integration/` |
| Claude Code / Project Filesystem | Template conformance | document-reviewer Gate 0 itself; produces JSON verdict per template structure | Implicit in pipeline runs |
| Claude Code / Project Filesystem | ADR template migration verification | Diff between pre-migration and migrated versions; verify content preservation | Per Phase 4 task |
| Claude Code / Project Filesystem | EARS keyword usage | document-reviewer Gate 1 quality check | Implicit in pipeline runs |

### Integration Verification Points

- **Stage 1 → Stage 1.5 → Stage 2**: Verify Intent Clarification → PRD → Research Plan handoff produces all expected artifacts with cross-references.
- **Stage 5a → 5b**: Verify per-layer designers produce expected per-layer outputs, composer produces integrated blueprint with all expected sections.
- **Stage 5b document-reviewer**: Verify `codebase_analysis` parameter populated correctly from `03-codebase-analysis.json`; Fact Disposition Table covers all `focusAreas`.
- **Stage 6 architecture-auditor**: Verify renamed sub-agent invoked; brief-honor verification fires; blast-radius queries return.
- **Stage 8 acceptance-tester output**: Verify EARS-format AC scenarios produced; mapping to blueprint requirement IDs preserved.
- **Stage 9 cross-artifact-auditor**: Verify CMC (model: opus) fires; diff-mode input; convergence-based termination measured.
- **5 document-reviewer invocations**: Verify each fires at correct stage; verdicts feed into correct downstream behavior (approval gate or reconcile loop).
- **Critic renames**: Verify orchestrator references new names; no v3 names (synth-critic-1, synth-critic-2) appear in v4 output artifacts.

## Verification Strategy

### Correctness Proof Method

- **Correctness definition**: "v4 of the pipeline produces all the artifacts of v3 plus the new v4 artifacts (PRD, per-layer Design sections, document-reviewer JSON verdicts at 5 points, codebase analysis JSON), with all artifacts conforming to the canonical templates (Blueprint, PRD, ADR, IntentClarification, Plan), and end-to-end pipeline run completes from intent to approved task DAG with all 6 human gates clearing on a representative test feature."
- **Verification method**: Run v4 against a representative test feature (e.g., "add a /healthz endpoint"); inspect each artifact for template conformance via document-reviewer Gate 0; verify gate sequence by traceability.json; verify renamed critics by sub-agent invocation logs; verify EARS-format ACs by Gate 1 keyword check.
- **Verification timing**: Phase 7 (integration test) of the implementation plan above. Before any v4 production-use claim.

### Early Verification Point

- **First verification target**: documentation-criteria skill extension (Phase 1). Verify the skill loads correctly with all 5 templates accessible; verify sub-agents that reference the skill can read template structures from it.
- **Success criteria**: Sub-agent invocation with `skills: documentation-criteria` succeeds; sub-agent body can read `Template: PRD` section content; document-reviewer can locate template-conformance rules per doc_type.
- **Failure response**: If documentation-criteria fails to load or templates aren't accessible, halt v4 rollout; investigate skill frontmatter (per ADR-0010) and content size (per ADR-0011 kill criterion).

### Output Comparison (When Replacing or Modifying Existing Behavior)

**Note (self-referential semantics, addresses I-DR-002):** For this meta-blueprint, output comparison is conducted during Phase 7 integration test (per Implementation Plan), not at this artifact's authoring time. The fields below describe the comparison procedure that will be executed at Phase 7, when v4 is run against a representative test feature and its output is compared to v3's output for the same intent. For user-feature blueprints produced by the v4 pipeline going forward, output comparison occurs at the user-feature's own verification stage, comparing the new design's output to the existing system's output for the same input.

**Comparison input**: Same user intent statement (e.g., "Add a /healthz endpoint with database connectivity check") run through v3 and v4 pipelines.

**Expected output fields**:
- v3 output: blueprint-v3.md, plan.json, acceptance-tests.md (BDD), phase-validators inline, tasks.json
- v4 output: PRD-v1.md (NEW), blueprint-v4.md (canonical template), plan.json or plan-v4.md, acceptance-tests.md (EARS), phase-validators inline, tasks.json, plus 5 document-reviewer verdict JSONs and 03-codebase-analysis.json

**Diff method**:
- Structural: verify v4 output includes all v3 output equivalents plus the v4-new artifacts.
- Content: v4 blueprint should cover the same architectural decisions as v3 blueprint, but with template-conformant structure. Decision content should match (or supersede with explicit rationale per ADR-0005).
- AC syntax: v3 BDD-format ACs map to v4 EARS-format ACs covering the same behavior (semantic equivalence; syntactic divergence is expected and acceptable per ADR-0015).

**Transformation pipeline coverage**: N/A — pipeline has no `dataTransformationPipelines` because this is a meta-pipeline-design artifact (no codebase analysis JSON to reference). When the v4 pipeline is invoked against an actual user feature, the user-feature's transformation pipelines will be covered by output comparison at that run.

### Operational Verification

- **Pre-merge gates**: This is a Claude Code skill installation, not a code merge. The "gate" is the user's decision to install v4. Pre-installation verification: review the v4 file inventory (12 new agents, ~12 new/renamed skills, 1 orchestrator update, 11 migrated ADRs).
- **Post-install verification**: Run the Phase 7 integration test (test feature end-to-end). If integration test passes, v4 is operationally verified.
- **Migration verification**: For ADR retroactive migration — verify all 11 migrated ADRs have all template fields populated (no missing Kill criteria; no missing Decision Details rows); verify pre-migration files preserved verbatim.
- **Rollback rehearsal**: Rollback procedure documented in `docs/ops/feature-pipeline-runbook.md` (referenced in Referenced Specifications above):
  - Remove v4 sub-agent files
  - Restore renamed sub-agent files to original names (synth-critic-1.md, synth-critic-2.md) — these still exist at their renamed paths so a rename-back is sufficient
  - Remove v4-new knowledge skill files
  - Restore orchestrator skill body to v3 version (preserved at `.claude/skills/feature-pipeline/SKILL.md.v3-backup` per implementation guidance)
  - documentation-criteria reverts via git (its v3 form is the predecessor commit)

## Future Extensibility

- **Extension points**:
  - Layer Scope checklist can extend beyond 9 layers as needed (e.g., ML model deployment, data warehouse, mobile-native). New per-layer designer sub-agents added with corresponding `<layer>-design-knowledge` skill.
  - document-reviewer `doc_type` taxonomy can extend beyond the 6 v4 values (PRD, ADR, UISpec, DesignDoc, IntentClarification, Plan) — e.g., `Runbook`, `OpenAPISpec`, `DatabaseSchema`.
  - synth-codebase-researcher output schema (per ADR-0018) can extend with new fields without breaking consumers; schema_version field gates compatibility.
  - The 6 human gates can be extended (e.g., a Stage-3 Research Approval Gate for very expensive research runs) without orchestrator architecture change.
  - MCP additions: future blast-radius MCPs (or specialized MCPs like security-scan MCPs) can be added to ADR-0007's selection without architectural change.

- **Known future requirements**:
  - **CI integration**: Future scope — running the pipeline as a CI workflow triggered by feature-branch creation. Would require: GitHub Action wrapper, non-interactive gate handling (perhaps via PR comments), result-as-PR-comment rendering.
  - **Multi-pipeline orchestration**: Future scope — running multiple feature-pipelines in parallel for features that depend on each other; cross-pipeline rationale brief sharing.
  - **Pattern auto-detection**: Per ADR-0008, automatic cross-feature pattern detection is deferred. Future scope: classifier trained on human-curated patterns to suggest pattern matches.
  - **Plan ↔ Blueprint separation**: Currently the plan content can live inside the Blueprint template (Implementation Plan section). If practical experience shows plans need to evolve independently, the pipeline can split them — Plan template would gain dedicated doc_type and separate review.

- **Intentional limitations**:
  - Pipeline does NOT execute the task DAG. Build Approval Gate's output is a plan; execution is out of scope.
  - Pipeline does NOT directly modify the user's codebase. All artifacts live in `working/feature/<slug>/`.
  - Pipeline does NOT auto-curate cross-feature patterns (ADR-0008 explicit kill on auto-curation; human triage retains agency).
  - Pipeline does NOT support live collaboration (one user per run). Multi-user features would require state-sync infrastructure outside Claude Code's primitives.

## Alternative Solutions

### Alternative 1: Light template adoption (skip retroactive migration)

- **Overview**: Adopt canonical templates for NEW ADRs (0011+) only; grandfather ADRs 0001-0010 in their original structure.
- **Advantages**: No retroactive migration work; existing artifacts unchanged; lower implementation cost.
- **Disadvantages**: Hybrid ADR format in same pipeline's set; document-reviewer must support both structures; cross-ADR references weakened (a v4 ADR referencing a v3-format ADR has different fields than expected); contributors learn two formats.
- **Reason for Rejection**: User explicitly approved Option A (full retroactive migration) per Q-v4-5. The hybrid format cost is higher than the one-time migration cost in the long run.

### Alternative 2: Single-author Stage 5 (preserve v3 topology)

- **Overview**: Keep synth-designer as single author; do not fan out across layers; just adopt the canonical Blueprint template for the single author to follow.
- **Advantages**: Simpler topology; no consistency-gap risk (claim C-R3-0007); no composer-side reconciliation overhead; unified authorial voice.
- **Disadvantages**: Single-agent bottleneck for multi-layer features; no parallelism gain; per-layer domain knowledge skills must all load into one agent's context (stresses claim C-R2-0011 working budget).
- **Reason for Rejection**: User explicitly inverted Q-v4-3 to fan-out-then-fan-in. The multi-layer features the pipeline targets benefit from per-layer parallelism enough to justify the consistency-gap mitigation cost.

### Alternative 3: BDD-only acceptance criteria (preserve v3 syntax)

- **Overview**: Continue using BDD Gherkin (Given/When/Then) for acceptance criteria; do not adopt EARS.
- **Advantages**: Familiar to many developers; rich expressiveness for multi-step user flows; maps to Cucumber/Specflow tooling.
- **Disadvantages**: AI agents fill `Given` with assumed context that isn't grounded (per claim C-R3-0014 fabrication tendency); BDD scenarios are less structurally enforceable than EARS keywords; the Blueprint template specifies EARS in its Acceptance Criteria section.
- **Reason for Rejection**: User explicitly chose EARS (Q-v4-4 Option A). Industry precedent for AI workflows (Amazon Kiro per claim C-R3-0003) is strong. The Blueprint template adoption (ADR-0013) further locks in EARS.

### Alternative 4: No document-reviewer integration (rely on substantive critique only)

- **Overview**: Skip document-reviewer integration entirely; rely on synth-architecture-auditor and synth-cross-artifact-auditor to catch structural issues alongside substantive ones.
- **Advantages**: Fewer sub-agent invocations per run; lower cost; simpler orchestrator topology.
- **Disadvantages**: Structural checks (template conformance, required-section presence, EARS keyword validation, Fact Disposition Table coverage) are intermixed with substantive checks; document-reviewer's prior_context_check mechanism is unused; the auditors' context budgets carry both concerns at once.
- **Reason for Rejection**: document-reviewer exists (uploaded template) and is well-designed for the structural concern; integrating it cleanly separates structural-correctness from substantive-correctness, which composes better (per claim C-R3-0024 Microsoft Conductor pattern and claim C-R3-0026 STOA Council 3-stage pattern). Cost of 5 invocations is manageable; Gate 0 fast-fail keeps the cost bounded.

## Risks and Mitigation

| Risk | Layer | Impact | Probability | Mitigation |
|------|-------|--------|-------------|------------|
| Cross-layer dependency contradictions unresolvable at composer | Claude Code / Project Filesystem | High (blueprint contains unresolved contradiction → blast-radius issues) | Medium | Composer flags as `[UNRESOLVED]` markers → document-reviewer surfaces as `critical` → synth-reconcile loop with user input via prior_context_check; up to 4 cycles before escalation |
| documentation-criteria skill size exceeds compaction budget | Claude Code / Project Filesystem | Medium (skill content lost after compaction in long-running sub-agents) | Medium | Kill criterion in ADR-0011 (50K tokens); monitor in practical use; mitigated by templates as referenced sections (sub-agents focus on the specific template they need) |
| Per-layer designers fail to emit useful `dependencies_on_other_layers` | Claude Code / Project Filesystem | Medium (composer can't reconcile silently-introduced contradictions) | Medium-High | Per-layer design knowledge skills MUST teach the sidecar emission with explicit examples; document-reviewer Gate 1 flags blueprint sections that reference cross-layer content without sidecar |
| Document-reviewer 5 invocations exceed cost/time budget | Claude Code / Project Filesystem | Medium (pipeline run is too slow or expensive for routine use) | Medium | Gate 0 fast-fail keeps per-invocation cost bounded; if practical run measurement shows budget breach, kill criterion in ADR-0017 triggers re-evaluation |
| Retroactive ADR migration introduces content drift from originals | Claude Code / Project Filesystem | High (decisions inadvertently altered) | Low (Option 3 structural-preserving is deliberately content-preserving) | Pre-migration versions preserved as `*-pre-template-migration.md`; reviewer can diff to confirm content equivalence; document-reviewer Gate 1 on each migrated ADR can flag content discrepancies |
| 27-sub-agent inventory crosses selection-degradation threshold | Claude Code / Project Filesystem | Medium (per claim C-R2-0010, large tool catalogs degrade selection accuracy) | Low | Orchestrator picks agents directly by name (not via Tool RAG); concern applies to LLM tool catalogs, not orchestrator-side agent selection. Document for clarity. |
| Composer fails on very-multi-layer features (5+ layers active) | Claude Code / Project Filesystem | Medium (composer context budget strained for cross-layer reconciliation) | Low-Medium | maxTurns: 60 for composer; reconcile loop catches incomplete output; kill criterion in ADR-0016 triggers re-evaluation if 3+ runs hit composer's context limit |
| EARS adoption produces forced Ubiquitous-form ACs | Claude Code / Project Filesystem | Low (ACs become verbose without structure benefit) | Medium | Kill criterion in ADR-0015 (30%+ Ubiquitous as signal); hybrid permitting BDD for non-event-driven would supersede |
| Critic renames break v3 cross-references | Claude Code / Project Filesystem | Low (v3 artifacts preserved; v3 references are by old names but artifacts are immutable) | Low | v3 artifacts preserved per ADR-0005; renames are forward-only; v4 references new names; no in-place edits to v3 |
| document-reviewer's doc_type extension breaks existing invocations | Claude Code / Project Filesystem | Low (additive extension) | Very low | doc_type taxonomy extended additively; existing values (PRD, ADR, UISpec, DesignDoc) unchanged; existing invocations remain valid |
| GitNexus license (PolyForm Noncommercial) blocks commercial users | Claude Code / Project Filesystem | High (specific users blocked from primary code-graph MCP) | Medium (depends on user population) | Documented in ADR-0007 v2.x; codebase-memory-mcp fallback configured concurrently; setup guide explicitly addresses commercial-use requirements |

## References

- ADR-0001 through ADR-0018: all 18 ADRs in the canonical template (ADR-0001 through ADR-0010 retroactively migrated per ADR-0014)
- `/mnt/user-data/uploads/BluePrint.txt`: canonical Blueprint template (adopted per ADR-0013)
- `/mnt/user-data/uploads/PDR.txt`: canonical PRD template (adopted per ADR-0011)
- `/mnt/user-data/uploads/ADR.txt`: canonical ADR template (adopted per ADR-0014)
- `/mnt/user-data/uploads/document_reviewer_template.txt`: document-reviewer sub-agent definition (extended per ADR-0017)
- `/mnt/user-data/outputs/feature-pipeline-round-2/blueprint-v3.md`: predecessor v3 blueprint (preserved per ADR-0005)
- `/mnt/user-data/outputs/feature-pipeline-round-3/research-claims.json`: 30 claims grounding ADRs 0011-0018
- Claim C-R3-0001 through C-R3-0030: research round 3 findings (EARS adoption, fan-out-fan-in patterns, consistency gap, PRD failure modes, format tradeoffs, template conformance, multi-stage review, codebase analysis schemas)

## Update History

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2026-05-13 | 4.2.0 | Layer Scope category-error correction (user-identified). v4.0.0 and v4.1.0 incorrectly used Layer Scope as "what surfaces this artifact physically modifies" (only Claude Code FS) instead of "what layers the v4 pipeline can design FOR" (all 9 layers). v4.2.0 corrects: Layer Scope shows all 9 layers in scope with pipeline-capability vs artifact-physical distinction explicit; Design Summary YAML layers_touched lists all 9; Change Impact Map split into Direct Impact (this meta-blueprint's physical changes) + Capability Impact (what v4 pipeline can produce for each layer); Implementation Path Mapping expanded with 9 discrete per-layer designer agent rows + 9 discrete per-layer knowledge skill rows; 8 per-layer Design sections (Frontend, Backend, API, Query, Database, CI/CD, IaC, Codespaces) substantively authored with research-grounding caveats per the Path A authoring discipline; Security Considerations per-layer authored with substantive content (8 layers, previously N/A); per-layer AC subsection pattern documented before Cross-Layer ACs; Implementation Plan Phase 2 expanded to enumerate 9 specific per-layer knowledge skills with content scope. All inherited decisions from v4.1.0 preserved. | synth-reconcile (this session, multi-phase plan execution per v4-2-plan.md) |
| 2026-05-12 | 4.1.0 | Reconcile pass after document-reviewer + synth-architecture-auditor + synth-cross-artifact-auditor review of v4.0.0. Resolves 6 issues: I-CA-001/I-DR-001 (sub-agent inventory arithmetic), I-AA-001 (per-layer designer failure handling at Stage 5a→5b transition), I-AA-002 (composer-only ADR authorship enforcement via orchestrator-side scan), I-DR-002 (Output Comparison self-referential semantics note), I-DR-003 (Skills table document-review-knowledge entry clarification), I-AA-003 (explicit rationale-brief enumeration for Stages 1.5, 5a, 5b). All inherited decisions preserved verbatim. | synth-reconcile (this session) |
| 2026-05-12 | 4.0.0 | Initial v4 supersession of v3. Adds Stage 1.5 PRD generation; fan-out-fan-in at Stage 5; 5 document-reviewer invocations; critic renames; EARS-format ACs; canonical template adoption; retroactive ADR migration; canonical codebase analysis schema. Eight new ADRs (0011-0018); 11 retroactive ADR migrations. | synth-designer (this session) |
| 2026-05-12 | 3.0.0 | (Predecessor — see blueprint-v3.md) | synth-designer (v3 session) |
