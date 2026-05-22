---
id: ADR-0018
version: 2.0.0
status: Accepted
generated: 2026-05-19
generated_by: finalize-reconciler (v4.3.0 naming-convention retroactive update per ADR-0019)
supersedes: []
adrs_inherited:
  - ADR-0007 v2.0.0 (GitNexus primary, codebase-memory-mcp fallback)
  - ADR-0011 (canonical document skill)
  - ADR-0013 (Blueprint template adoption — Fact Disposition Table consumes this schema)
  - ADR-0017 (shared-document-reviewer integration — consumes codebase_analysis JSON)
applies_to:
  - feature-pipeline (blueprint v4, forthcoming)
template_format: per ADR.txt v1.0
---

# ADR-0018: discovery-codebase-researcher output schema (codebase_analysis JSON)

## Status

Accepted — 2026-05-12

## Context

Two pipeline components require a structured codebase analysis artifact:

(1) The Blueprint template (uploaded `BluePrint.txt`, adopted via ADR-0013) includes a "Fact Disposition Table" that requires one row per "codebase analysis `focusAreas` entry," with fields `Fact ID`, `Focus Area`, `Disposition` (preserve/transform/remove/out-of-scope), `Rationale`, and `Evidence`.

(2) The shared-document-reviewer (uploaded template, integrated via ADR-0017) accepts an optional `codebase_analysis` JSON input with `focusAreas` (each with `fact_id` and `evidence`) and `dataTransformationPipelines`. Gate 0 / Gate 1 Fact Disposition checks require this input to validate the Blueprint's Fact Disposition Table coverage.

Both reference a structured codebase analysis output. The pipeline's `discovery-codebase-researcher` (Stage 3, blueprint v3) currently produces an unstructured markdown research report. To bridge the gap, the researcher's output format must be specified.

Research finding (claim C-R3-0028): no industry-standard schema for codebase analysis output exists. Implementations vary (Qodo, Skopx, GitNexus, codebase-memory-mcp each have different structures). The pipeline must specify its own.

## Decision

Define a canonical JSON output schema for `discovery-codebase-researcher` (and the codebase analysis stage more broadly). The schema lives in `KB-documentation-criteria` per ADR-0011 alongside the Blueprint and shared-document-reviewer template references. discovery-codebase-researcher produces this JSON as a sibling artifact to its markdown research report.

## Decision Details

| Item | Content |
|---|---|
| Decision | discovery-codebase-researcher emits `03-codebase-analysis.json` conforming to a pipeline-canonical schema with `focusAreas`, `dataTransformationPipelines`, `dependencies`, and `evidence` structures. Schema lives in `KB-documentation-criteria`. |
| Why now | Blueprint template (ADR-0013) and shared-document-reviewer integration (ADR-0017) both reference a `codebase_analysis` input with specific field names; committing to the schema before these downstream consumers are wired in prevents schema-drift across stages. |
| Why this | No industry-standard schema exists (claim C-R3-0028); the shared-document-reviewer template's expected fields (`focusAreas` with `fact_id` and `evidence`; `dataTransformationPipelines`) provide a starting structure already validated by an existing pipeline component; aligning discovery-codebase-researcher to produce exactly what shared-document-reviewer expects eliminates translation overhead. |
| Known unknowns | Whether `dataTransformationPipelines` is the right abstraction for non-data-flow-shaped codebases (e.g., a feature that's primarily configuration changes); whether the schema needs extension for features that touch infrastructure-as-code or CI/CD (which don't have "data flow" in the traditional sense). |
| Kill criteria | If 3+ feature runs produce `codebase_analysis.json` outputs where 50%+ of `focusAreas` have empty or N/A `dataTransformationPipelines`, the field is over-scoped and a slimmer schema variant for non-data-flow features should supersede this ADR. |

## Rationale

The shared-document-reviewer template already specifies the consumed field names (`focusAreas`, `fact_id`, `evidence`, `dataTransformationPipelines`). Adopting these directly:

(1) Eliminates translation between the producer (discovery-codebase-researcher) and the consumer (shared-document-reviewer at invocation point 3, blueprint Fact Disposition Table at Stage 5b composer).

(2) Provides a fixed structural contract that discovery-codebase-researcher's knowledge skill (`KB-codebase-research`) can teach explicitly: "Your output JSON has these required fields with these meanings."

(3) Makes design-composer's Fact Disposition Table authoring mechanical: read each focusArea from the JSON, decide disposition per the Blueprint template's rules (preserve/transform/remove/out-of-scope), write the table row.

The alternative — letting discovery-codebase-researcher produce unstructured prose and having design-composer extract focusAreas via LLM parsing — would introduce a 5-15% reasoning-tax (claim C-R3-0018: JSON vs markdown for reasoning) at the parsing step. Better to commit to a structured producer.

## Options Considered

**Option 1: Free-form markdown research report (v3 status quo).** discovery-codebase-researcher produces prose; downstream consumers parse via LLM.
- Pros: simple producer; rich expressiveness.
- Cons: each consumer pays parsing cost; structural drift between what producer emits and what consumers extract; shared-document-reviewer's `codebase_analysis` input parameter cannot be populated cleanly.

**Option 2: Adopt an industry-standard schema (e.g., Qodo's, GitNexus's).**
- Pros: alignment with established tools; potential ecosystem benefits.
- Cons: claim C-R3-0028 documents no industry-standard schema exists; adopting one vendor's shape couples the pipeline to that vendor's evolution.

**Option 3 (Selected): Pipeline-canonical schema matching shared-document-reviewer's expected fields.**
- Pros: no translation overhead between producer and consumer; shared-document-reviewer integration is mechanical; Blueprint Fact Disposition Table population is mechanical; schema versioning is owned by `KB-documentation-criteria` skill.
- Cons: requires explicit schema specification work (this ADR + content in KB-documentation-criteria); future stages consuming codebase analysis must adopt this schema.

## Consequences

### Positive Consequences

- shared-document-reviewer's `codebase_analysis` input parameter is populated directly from discovery-codebase-researcher's output — no translation step.
- Blueprint Fact Disposition Table authoring is mechanical: one row per `focusAreas` entry.
- discovery-codebase-researcher's knowledge skill (`KB-codebase-research`) can teach the schema explicitly with examples.
- Schema versioning lives in `KB-documentation-criteria` skill changelog; updates are pipeline-wide events.
- review-cross-artifact-auditor (renamed critic-2) can use the schema for diff-mode analysis between codebase analyses across runs.

### Negative Consequences

- discovery-codebase-researcher must emit BOTH the markdown research report (for human and rationale-brief consumption) AND the structured JSON. Two artifacts per run.
- The schema's `dataTransformationPipelines` field is well-suited to data-flow features but may be empty/N/A for configuration-only or UI-only features. Acceptable but watched per kill criteria.
- Schema evolution requires coordinated updates: KB-documentation-criteria (schema spec) + KB-codebase-research (producer guidance) + shared-document-reviewer template (consumer integration) + blueprint template (Fact Disposition Table format).

### Neutral Consequences

- The schema mirrors fields the shared-document-reviewer expects; if shared-document-reviewer changes its expected input shape in the future, this ADR is superseded by a new version aligning to the new shape.

## Architecture Impact

**Components that change:**
- `discovery-codebase-researcher`: output expanded from markdown research report only to (a) markdown research report + (b) structured JSON conforming to the canonical schema.
- `KB-codebase-research`: extended with schema specification and producer guidance.
- `KB-documentation-criteria`: extended with the canonical codebase_analysis schema specification.
- Stage 5b design-composer: consumes `03-codebase-analysis.json` for Fact Disposition Table population.
- shared-document-reviewer (invocation point 3, doc_type: DesignDoc): receives `03-codebase-analysis.json` as the `codebase_analysis` parameter.

**New dependencies introduced:**
- Stage 5b composer depends on Stage 3's `03-codebase-analysis.json` output.
- shared-document-reviewer (at invocation point 3) depends on Stage 3's `03-codebase-analysis.json` output.
- Both dependencies are runtime-only; no new compile-time dependencies.

**Architectural constraints added:**
- discovery-codebase-researcher MUST produce `03-codebase-analysis.json` conforming to the canonical schema in addition to its markdown research report.
- The schema's required fields MUST be present even when their values are empty or N/A for the specific feature (explicit N/A is permitted; silent omission is not).
- Schema updates are coordinated changes to `KB-documentation-criteria`, `KB-codebase-research`, `shared-document-reviewer` template, and Blueprint template — no partial updates.

**Architectural constraints removed:**
- discovery-codebase-researcher is no longer permitted to emit only markdown without the structured JSON.

## Implementation Guidance

### Canonical schema shape

```json
{
  "schema_version": "1.0.0",
  "run_id": "<run-id>",
  "scanned_at": "<ISO-8601>",
  "feature_slug": "<feature-slug>",
  "focusAreas": [
    {
      "fact_id": "FA-001",
      "area_name": "<short name, e.g., 'Existing auth middleware'>",
      "description": "<what this focus area is about>",
      "files": ["<path>", "<path>"],
      "evidence": "<verbatim code snippet or signature carrying through to Blueprint's Fact Disposition Table evidence column>",
      "relevance_to_feature": "<why this matters for the planned feature>",
      "current_behavior": "<what the code currently does>"
    }
  ],
  "dataTransformationPipelines": [
    {
      "pipeline_id": "DTP-001",
      "name": "<short name, e.g., 'User signup → DB persistence'>",
      "stages": [
        {
          "stage": 1,
          "component": "<file or module>",
          "transformation": "<input → output transformation>",
          "evidence": "<code reference>"
        }
      ],
      "endpoints_of_interest": ["<endpoint or entry point>"],
      "feature_intersects_at_stages": [1, 3]
    }
  ],
  "dependencies": {
    "external_services": [
      {"name": "<service>", "files_referencing": ["<path>"], "version_or_endpoint": "<value>"}
    ],
    "internal_modules": [
      {"name": "<module>", "files": ["<path>"], "stability": "stable | unstable | deprecated"}
    ]
  },
  "scope_observations": {
    "layers_in_scope_evidence": {
      "frontend": "<evidence of frontend code touching the feature area, or N/A>",
      "backend": "<...>",
      "api": "<...>",
      "query": "<...>",
      "database": "<...>",
      "cicd": "<...>",
      "iac": "<...>",
      "codespaces": "<...>",
      "claude-code-fs": "<...>"
    }
  },
  "potential_blast_radius_hints": [
    {
      "symbol_or_file": "<symbol>",
      "callers_count": 12,
      "callees_count": 5,
      "risk_class_estimate": "high | medium | low"
    }
  ]
}
```

### Producer guidance (KB-codebase-research)

- One `focusAreas` entry per identified piece of existing code that is relevant to the feature. Identify these by querying GitNexus (primary per ADR-0007 v2) for code symbols matching the feature's keywords, then expanding via call-graph traversal.
- `evidence` field carries verbatim code or signature so downstream consumers can reference exactly what was found.
- `dataTransformationPipelines` populated for features that involve data flow (input → processing → output across multiple components). Set to empty array `[]` for features that don't.
- `scope_observations` populated by examining whether code in each layer-relevant directory exists and is touched by the feature; explicit "N/A — no <layer> directory in this repo" or "N/A — feature does not touch <layer>" preferred over silent omission.
- `potential_blast_radius_hints` is a preliminary estimate from discovery-codebase-researcher; review-architecture-auditor will do the deep blast-radius analysis with GitNexus tools per ADR-0007 v2. These hints orient the auditor; not authoritative.

### Consumer guidance

**design-composer (Stage 5b):**
- Read `03-codebase-analysis.json` to populate the Blueprint's Fact Disposition Table.
- For each `focusAreas` entry, decide disposition: `preserve` (feature uses the existing code as-is), `transform` (feature modifies the existing code; state new behavior), `remove` (feature replaces or deletes; state reason), `out-of-scope` (relevant but not touched; state which scope boundary excludes it).
- Each Fact Disposition Table row's `Evidence` column carries through the `evidence` field verbatim from the JSON.

**shared-document-reviewer (invocation point 3):**
- Receive `03-codebase-analysis.json` as the `codebase_analysis` parameter (or its content embedded in the invocation prompt).
- Validate Fact Disposition Table coverage: every `focusAreas` entry must have a corresponding row.
- Validate Fact Disposition Table content: `fact_id` carries through; `Evidence` column carries through verbatim; disposition is one of the four permitted values; rationale present for transform/remove/out-of-scope.

## Related Information

- ADR-0007 v2.0.0: GitNexus primary, codebase-memory-mcp fallback — both can populate the canonical schema.
- ADR-0011: schema lives in `KB-documentation-criteria` skill.
- ADR-0013: Blueprint template's Fact Disposition Table consumes this schema.
- ADR-0017: shared-document-reviewer's `codebase_analysis` input consumes this schema at invocation point 3.
- User-provided shared-document-reviewer template: defines expected field names (`focusAreas`, `fact_id`, `evidence`, `dataTransformationPipelines`) — schema aligned to these.
- Claim C-R3-0028: no industry-standard schema for codebase analysis output exists; defining our own canonical schema is the right call.

## v4.3.0 retroactive naming-convention update

Per ADR-0019, all sub-agent, knowledge skill, and orchestrator skill references in this ADR have been updated to the v4.3.0 naming convention (phase-prefixed sub-agents, KB-prefixed knowledge skills, recipe-prefixed orchestrator, shared-prefixed cross-phase sub-agents). The pre-update version is preserved at `ADR-0018-codebase-analysis-schema-pre-naming-convention.md`. The decision recorded in this ADR is unchanged; only entity names are updated for cross-document consistency.
