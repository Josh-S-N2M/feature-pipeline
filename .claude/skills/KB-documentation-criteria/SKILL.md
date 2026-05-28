---
name: kb-documentation-criteria
description: >-
  Canonical templates, authoring disciplines, and shared conventions for
  every document the feature-pipeline produces: Intent Clarification doc,
  PRD, Blueprint, ADRs, and Plan. Load when authoring any of these
  documents, when configuring a sub-agent that authors one, or when
  shared-document-reviewer needs to know what a "correct" document of a
  given type looks like. Houses the 5 canonical templates, the 9-layer
  taxonomy used by Layer Scope, the rationale-brief instruction
  (per ADR-0009), supersession and frontmatter conventions, and the
  authoring disciplines for PRD, Design Composition, Plan, and EARS
  acceptance criteria. Absorbs (per ADR-0020) the v4.2-era
  prd-authoring-knowledge, design-composition-knowledge,
  planning-knowledge, and acceptance-testing-knowledge skills.
pedagogical_sections:
  - path: references/layer-taxonomy.md
    justification: "Layer-taxonomy reference for the doc system; references .claude/commands/deploy.md as an exemplar slash command (auditor flags non-existent path)"
  - path: references/templates/blueprint-template.md
    justification: "Blueprint document template; contains .devcontainer/devcontainer.json and docker-compose.yml example references in the design-doc placeholder text (auditor flags non-existent demo paths)"
---

# Documentation Criteria

This KB is the single source of truth for what every pipeline document should look like and how to author it. It is loaded by the sub-agents that author documents and by `shared-document-reviewer` when it checks them.

The body below is the router. Each substantive concern lives in `references/`.

## When this KB is loaded

| Caller | When | Purpose |
|---|---|---|
| `intake-intent-clarifier` | Intent Clarification | Author the Intent Clarification document |
| `intake-prd-author` | PRD Authoring | Author the PRD with AI-PRD failure-mode avoidance |
| `design-frontend`, `design-backend`, `design-api`, `design-query`, `design-database`, `design-cicd`, `design-iac`, `design-codespaces`, `design-claude-code` | per-layer Design | Author per-layer Design subsections that conform to the Blueprint template |
| `design-composer` | Design Composition | Author cross-cutting Blueprint sections, ADRs, and the Fact Disposition Table |
| `plan-author` | Plan Authoring | Author the Plan from the approved Blueprint |
| `test-acceptance-author` | Acceptance Test Authoring | Author EARS-format acceptance tests |
| `shared-document-reviewer` | Every reviewed document | Verify the document conforms to its template (Gate 0) and shared conventions |

## What's in this KB

| Concern | Reference |
|---|---|
| Canonical templates: PRD, Blueprint, ADR, Intent Clarification, Plan | `references/templates/` |
| The 9-layer engineering taxonomy used by Layer Scope | `references/layer-taxonomy.md` |
| Shared conventions: frontmatter format, supersession discipline, traceability rules | `references/shared-conventions.md` |
| Honoring the Rationale Brief (per ADR-0009) | `references/rationale-brief.md` |
| PRD authoring discipline (AI-PRD failure mode avoidance per claim C-R3-0014) | `references/disciplines/prd-authoring.md` |
| Design composition discipline (integration, arbitration, Fact Disposition Table) | `references/disciplines/design-composition.md` |
| Plan authoring discipline (phase-based decomposition, L1/L2/L3 verification) | `references/disciplines/plan-authoring.md` |
| EARS acceptance criteria authoring | `references/disciplines/ears-acceptance-criteria.md` |
| Discovery planning discipline (used by `discovery-plan-author`) | `references/disciplines/discovery-planning.md` |
| Pedagogical marker justification spec (per ADR-0030 / FR-12) | `references/pedagogical-marker-justification-spec.md` |
| Deliverable archive spec (audit-trail packaging) | `references/deliverable-archive-spec.md` |
| Issue doctype structural spec (frontmatter lifecycle, body shape, cross-link fields for all 3 outside-pipeline issue doctypes; per ADR-0049) | `references/issue-doctypes-spec.md` |

## Canonical templates

| Document type | Template | Authored by |
|---|---|---|
| Intent Clarification | `references/templates/intent-clarification-template.md` | `intake-intent-clarifier` |
| Research Plan | `references/templates/research-plan-template.md` | `discovery-plan-author` |
| PRD | `references/templates/prd-template.md` | `intake-prd-author` |
| Blueprint (DesignDoc) | `references/templates/blueprint-template.md` | `design-composer` (cross-cutting) + per-layer designers (per-layer subsections) |
| ADR | `references/templates/adr-template.md` | `design-composer` (per FR-5) |
| Plan | `references/templates/plan-template.md` | `plan-author` |
| Per-task execution result (execution-phase) | `references/templates/per-task-execution-result-template.md` | `execute-task-code-producer` |
| Phase quality report (execution-phase) | `references/templates/phase-quality-report-template.md` | `execute-phase-quality-reviewer` |
| Quality reconciliation log (execution-phase) | `references/templates/quality-reconciliation-log-template.md` | `execute-finalize-reconciler` |
| State-transitions log entry (execution-phase) | `references/templates/state-transitions-log-entry-template.md` | `execute-orchestrator` (via `auditing-shared/scripts/log_state_transition.py`) |
| Pipeline run summary (execution-phase) | `references/templates/pipeline-run-summary-template.md` | `execute-orchestrator` |
| Issue Register (outside-pipeline issue capture) | `references/templates/issue-register-template.md` | `issue-capture-author` |
| Issue Analysis (outside-pipeline issue capture) | `references/templates/issue-analysis-template.md` | `issue-capture-author` |
| Issue Proposal (outside-pipeline issue capture) | `references/templates/issue-proposal-template.md` | `issue-capture-author` |

Each template defines the document's REQUIRED structural elements. `shared-document-reviewer`'s Gate 0 check uses these REQUIRED markers to determine whether a document passes structural review before quality assessment begins.

## The engineering-layer taxonomy (Layer Scope)

Both PRD and Blueprint use the same engineering-layer taxonomy for their `### Layer Scope` section. No mapping table; no PRD-specific layer vocabulary.

**The machine-readable canonical layer list is maintained at [`.claude/canonical/engineering-domain-layers.yaml`](../../canonical/engineering-domain-layers.yaml)** (loaded by `auditing-shared/scripts/canonical.py`; per ADR-0069). Its prose companion — per-layer descriptions, boundary cases, disposition guidance — is [`references/layer-taxonomy.md`](references/layer-taxonomy.md). Every consumer of this SKILL (PRD authors, per-layer designers, design-composer, plan-author, reviewers) reads the layer list from the canonical YAML (or its companion, which mirrors it), not from this SKILL.md. If a layer is added, only the YAML and its companion change; downstream consumers pick up the change on next read.

This SKILL.md intentionally does NOT enumerate the layers inline — duplicating the list here would create a drift surface that the CANON-2 audit (`audit_canonical_doc_drift.py`) flags. When authoring or reviewing, Read the canonical YAML or its prose companion.

Product-surface concerns (end-user experience, release cadence, residency, etc.) live in the PRD's Stakeholders / User Stories / Non-Functional Requirements / Product Policy Decisions sections — NOT in Layer Scope. The PRD's Layer Scope answers the engineering question "which subsystems will this feature touch?" not the product question "whose experience does this affect?"

## Frontmatter convention (all document types)

Every document carries YAML frontmatter at the top. The minimum required fields:

```yaml
---
id: <doc-type-id>           # e.g., PRD-add-healthz-001, BP-add-healthz-001, ADR-0023
version: 1.0.0
status: draft | proposed | accepted | superseded | rejected
generated: 2026-05-20T14:23:11Z
generated_by: <sub-agent-name>
---
```

ADRs add: `supersedes: ADR-NNNN` (when applicable), `change_summary: <one-line>`.
Blueprint adds: `predecessor: <path-to-previous-version>` (when this is not v1).
Plan adds: `derived_from: <blueprint-path>`.

Full frontmatter spec, including supersession discipline and YAML pitfalls: `references/shared-conventions.md`.

## Routing: "which reference do I need?"

| You are… | Load this reference |
|---|---|
| Authoring an Intent Clarification doc | `references/templates/intent-clarification-template.md` + `references/shared-conventions.md` |
| Authoring a PRD | `references/templates/prd-template.md` + `references/disciplines/prd-authoring.md` + `references/disciplines/ears-acceptance-criteria.md` + `references/layer-taxonomy.md` + `references/shared-conventions.md` + `references/rationale-brief.md` |
| Authoring a per-layer Design subsection of the Blueprint | `references/templates/blueprint-template.md` (your subsection only) + `references/layer-taxonomy.md` + the corresponding `KB-<layer>-design` skill + `references/rationale-brief.md` |
| Composing the Blueprint from per-layer outputs | `references/templates/blueprint-template.md` (cross-cutting sections) + `references/disciplines/design-composition.md` + `references/templates/adr-template.md` + `references/layer-taxonomy.md` + `references/rationale-brief.md` |
| Authoring an ADR | `references/templates/adr-template.md` + `references/shared-conventions.md` |
| Authoring the Plan | `references/templates/plan-template.md` + `references/disciplines/plan-authoring.md` + `references/disciplines/ears-acceptance-criteria.md` + `references/rationale-brief.md` |
| Authoring Acceptance Tests in EARS | `references/disciplines/ears-acceptance-criteria.md` |
| Reviewing any document (Gate 0/1) | The template for the document's `doc_type` + `references/shared-conventions.md` |

## Where this KB is NOT used

- Phase Validator authoring — uses `KB-task-decomposition` (which lives outside this KB per ADR-0020)
- UI Spec authoring — has its own template and discipline, not housed here in v4.3 (slated for KB-frontend-design)
- Code style / lint configuration — lives in the project's own conventions and `KB-general-coding-principles` for design-time samples
- Triggering discipline for outside-pipeline issue capture (when to capture, doctype classification rubric, approval-prompt rubric) — lives in `KB-issue-capture`, NOT here (per ADR-0049; templates above are structural-only)

## Provenance

Status: Accepted — v1.0.0 (Phase 2 of feature-pipeline v4.3.0)
Absorbs (per ADR-0020):
- `prd-authoring-knowledge` v4.2 — discipline → `references/disciplines/prd-authoring.md`
- `design-composition-knowledge` v4.2 — discipline → `references/disciplines/design-composition.md`
- `planning-knowledge` v4.2 (previously implicit) — discipline → `references/disciplines/plan-authoring.md`
- `acceptance-testing-knowledge` v4.2 (previously implicit) — discipline → `references/disciplines/ears-acceptance-criteria.md`
- Embedded templates (per ADR-0011) — PRD, Blueprint, ADR, Intent Clarification, Plan
