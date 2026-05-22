---
id: ADR-0013
version: 1.0.0
status: Accepted
generated: 2026-05-12
generated_by: synth-designer (new ADR for blueprint v4)
supersedes: []
adrs_inherited:
  - ADR-0009 (rationale brief)
  - ADR-0011 (canonical document skill)
applies_to:
  - feature-pipeline (blueprint v4, forthcoming)
template_format: per ADR.txt v1.0
---

# ADR-0013: Adoption of the uploaded Blueprint template as canonical design-document structure

## Status

Accepted — 2026-05-12

## Context

Blueprint v3's design document (the v3 file itself) was authored in an ad-hoc structure derived from the synthesis pipeline's report shape. The user has provided a comprehensive 892-line Blueprint template (uploaded as `BluePrint.txt`) covering:

- Layer Scope checklist (9 layers)
- Referenced Specifications
- Design Summary YAML block (risk, complexity, blast_radius, constraints, risks, unknowns)
- Background and Context (Prerequisite ADRs, External Resources, Agreement Checklist, Quality Assurance Mechanisms)
- Project Filesystem & Claude Code Conventions
- Acceptance Criteria in EARS format
- Existing Codebase Analysis with Fact Disposition Table
- Top-level Design (Change Impact Map, Interface Change Matrix, Data Flow, Integration Points, Components, Data Contracts, Field Propagation, State Transitions)
- Per-layer Design sections (Frontend, Backend, API, Query, Database, CI/CD, IaC, Codespaces)
- Error Handling, Logging & Monitoring
- Implementation Plan
- Security Considerations per layer
- Test Boundaries
- Verification Strategy (Correctness Proof Method, Early Verification Point, Output Comparison, Operational Verification)
- Future Extensibility, Alternative Solutions, Risks and Mitigation

The template is significantly more structured than v3's blueprint and was explicitly designed to handle features spanning multiple layers — exactly the scope the pipeline targets.

## Decision

Adopt the uploaded Blueprint template (`BluePrint.txt`) as the canonical structure for all blueprints produced by Stage 5. The template lives in `documentation-criteria` per ADR-0011. synth-designer (and per ADR-0016, the per-layer fan-out designers + composer) MUST produce blueprints conforming to this template. Sections corresponding to layers not in scope are marked `N/A — out of scope` per the template's own convention.

## Decision Details

| Item | Content |
|---|---|
| Decision | All blueprints produced by the pipeline follow the uploaded Blueprint template structure verbatim. |
| Why now | Stage 5 is undergoing fan-out-then-fan-in restructure (ADR-0016); committing to template structure simultaneously means per-layer designers and the composer have a shared structural contract from the start. |
| Why this | The template explicitly handles multi-layer features (the pipeline's primary use case); has built-in `N/A — out of scope` convention for narrow features; includes Fact Disposition Table that integrates with document-reviewer's codebase-analysis input (ADR-0018); includes Verification Strategy section that gives synth-acceptance-tester and synth-phase-validator structured inputs. |
| Known unknowns | Whether the template's 9-layer scope checklist matches the pipeline's eventual support set (we currently target the same 9 — Claude Code, Frontend, Backend, API, Query, Database, CI/CD, IaC, Codespaces — but template adoption locks this in); whether the template's per-layer Design sections will need extension when the pipeline encounters layers the template doesn't anticipate (e.g., ML model deployment, data warehouse). |
| Kill criteria | If 3+ feature runs produce blueprints where 50%+ of the template sections are `N/A — out of scope`, the template is over-scoped for the actual use case and supersession with a slimmer template is warranted. |

## Rationale

The template's structural completeness pays specific dividends:

- **Layer Scope checklist** drives Stage 0 scope detection (claim C-R3-0009 — fan-out width determined by detected scope, not all 9 designers always activated).
- **Fact Disposition Table** integrates directly with document-reviewer's `codebase_analysis.focusAreas` input (per the uploaded reviewer template — every focusArea must have a Fact Disposition row).
- **EARS-format Acceptance Criteria** matches ADR-0015's adoption decision and provides structured input to synth-acceptance-tester.
- **Verification Strategy** section bridges blueprint to phase-validators (synth-phase-validator) with explicit correctness definitions and early verification points.
- **Design Summary YAML block** provides structured metadata downstream sub-agents can consume without parsing the full blueprint markdown.
- **Per-layer Design sections** map naturally to ADR-0016's per-layer designer fan-out — each designer produces its corresponding section.

The template's risk is over-engineering for narrow features. Mitigated by the `N/A — out of scope` convention: sections corresponding to unchecked Layer Scope checkboxes are marked once with no further elaboration. The skeleton stays comprehensive; the content shrinks to match the feature.

## Options Considered

**Option 1: Light template — minimal required sections, optional everything else.** Define a small core (Overview, Layer Scope, Architecture, Acceptance Criteria) and let synth-designer add sections as needed.
- Pros: smaller artifacts for narrow features; less template fatigue.
- Cons: structural inconsistency across features; downstream stages (planner, task-decomposer) can't rely on section presence; document-reviewer's Gate 0 structural check has no fixed target.

**Option 2: Multiple templates — different templates per feature scope class.** "Single-layer template" for features touching one layer; "multi-layer template" for cross-cutting features; "infra-only template" for IaC changes.
- Pros: each template right-sized for its use case.
- Cons: classification step needed; templates drift independently; document-reviewer must support multiple template structures.

**Option 3 (Selected): Adopt uploaded Blueprint template as single canonical structure with `N/A — out of scope` convention for inapplicable sections.**
- Pros: structural completeness; supports multi-layer features naturally; built-in convention for narrow features; integrates with document-reviewer, codebase analysis, EARS ACs, and Verification Strategy in one structural package; matches user-provided template (their preference is load-bearing).
- Cons: blueprints will be large even for narrow features (skeleton overhead); some sections will frequently be `N/A` (Codespaces, IaC for projects without those concerns).

## Consequences

### Positive Consequences

- Document-reviewer's Gate 0 structural existence check has a fixed, comprehensive target.
- Per-layer designer fan-out (ADR-0016) maps cleanly to the template's per-layer Design sections.
- Verification Strategy section gives synth-acceptance-tester and synth-phase-validator structured inputs.
- Fact Disposition Table integrates with codebase analysis schema (ADR-0018) — every focusArea has an explicit disposition.
- EARS-format ACs (ADR-0015) live in a defined section per the template.
- Downstream stages (planner, task-decomposer) can rely on consistent section presence.
- The Implementation Plan section within the Blueprint template eliminates the need for a separate plan template at v4 (plan content lives inside the blueprint per the template). [NOTE: this may be revisited if the pipeline's plan.md output diverges materially from the blueprint's Implementation Plan section.]

### Negative Consequences

- Blueprints become large even for narrow features. Synth-designer's working context budget must accommodate authoring a complete (even if many-sections-N/A) blueprint per claim C-R2-0011 (knowledge budget 30-40% of effective context).
- New pipeline contributors must learn the template structure before they can write or critique blueprints meaningfully.
- Template updates are pipeline-wide events — changing one section affects every future blueprint.

### Neutral Consequences

- Blueprint v3 (the current self-referential blueprint) is structurally inconsistent with this new template. Per ADR-0005 (append-only), v3 is preserved as-is; v4 (forthcoming) is the first blueprint produced under this ADR's discipline.

## Architecture Impact

**Components that change:**
- `documentation-criteria`: extended with Blueprint template (per ADR-0011).
- `design-knowledge`: rewritten to teach the template structure rather than ad-hoc design discipline.
- synth-designer (per ADR-0016, becomes synth-designer-composer): instructed to produce template-conforming output.
- Per-layer designer sub-agents (ADR-0016): each produces the corresponding per-layer Design section per the template.
- `document-reviewer`: Gate 0 structural check operates against the template's required-section list for `doc_type: DesignDoc`.

**New dependencies introduced:**
- Blueprint output structure depends on the canonical template version. Versioning of the template lives in `documentation-criteria` skill changelog.

**Architectural constraints added:**
- All blueprints MUST follow the template structure verbatim.
- Sections corresponding to unchecked Layer Scope checkboxes MUST be marked `N/A — out of scope` (not silently omitted).
- The Fact Disposition Table MUST be present when codebase analysis exists; one row per focusArea.

**Architectural constraints removed:**
- Blueprint v3's ad-hoc structure (numbered sections, free-form per-stage detail) is no longer permitted for v4 and beyond.

## Implementation Guidance

- Treat each Layer Scope checkbox as the trigger for a per-layer designer in Stage 5a (per ADR-0016). Unchecked → designer not invoked.
- The Design Summary YAML block (`design_type`, `risk_level`, `complexity_level`, `blast_radius`, `main_constraints`, `biggest_risks`, `unknowns`) is authored by synth-designer-composer in Stage 5b, not by per-layer designers.
- The Verification Strategy section is authored by synth-designer-composer, drawing on per-layer designers' contributions to test planning.
- Fact Disposition Table is authored by synth-designer-composer, populated from `synth-codebase-researcher`'s `focusAreas` output (per ADR-0018).
- Per-layer designers MUST scope their output to the corresponding per-layer Design section only; cross-cutting concerns are the composer's responsibility.
- EARS-format ACs (per ADR-0015) are authored per-layer by per-layer designers (their layer's ACs) and cross-cutting ACs by the composer.

## Related Information

- User-provided template: BluePrint.txt (uploaded; canonical from this ADR forward).
- ADR-0011: template lives in `documentation-criteria`.
- ADR-0015: EARS-format ACs are the AC syntax used in the Acceptance Criteria section.
- ADR-0016: per-layer fan-out + composer fan-in design — maps to template's per-layer Design sections.
- ADR-0017: document-reviewer uses template structure for `doc_type: DesignDoc` Gate 0 checks.
- ADR-0018: synth-codebase-researcher output schema — populates the Fact Disposition Table.
- Claim C-R3-0023: template conformance for markdown documents requires application-layer enforcement (i.e., document-reviewer Gate 0).
