---
id: ADR-0038
version: 1.0.0
status: Accepted
generated: 2026-05-23
generated_by: design-composer
supersedes:
  - id: ADR-0018
    version: 1.0.0
adrs_inherited: [ADR-0018]
applies_to:
  - codebase-analysis.json consumers (discovery-codebase-researcher, review-architecture-auditor)
  - devcontainer-mcp-provisioning-r1
template_format: per KB-documentation-criteria ADR template v1.0
change_summary: >-
  Bumps ADR-0018 codebase-analysis schema to v1.1.0 with explicit blast-radius
  extension, schema-version history table, and downstream-consumer
  re-validation requirement. Also relocates / cross-references ADR-0007 from
  adrs-migrated/ to adrs/ per ADR-0036 single-canonical-location convention
  (E-0080).
---

# ADR-0038: codebase-analysis.json schema v1.1.0 — blast-radius extension and downstream-consumer realignment

## Contents

- [x] Status
- [x] Context
- [x] Decision
- [x] Decision Details
- [x] Rationale
- [x] Options Considered
- [x] Consequences
- [x] Architecture Impact
- [x] Implementation Guidance
- [x] Related Information

## Status

Accepted — 2026-05-23. Supersedes ADR-0018 v1.0.0 (which remains preserved per ADR-0005 append-only supersession).

## Context

Codebase analysis (claim C-0441 / C-0495, verified-high) directly identified a schema-version drift: ADR-0018 declares `schema_version: 1.0.0` in both its frontmatter and its in-body JSON example, while two downstream consumers — `.claude/skills/KB-codebase-research/SKILL.md` and `.claude/agents/discovery-codebase-researcher.md` — both reference v1.1.0 with the phrase "extended for blast-radius." The mid-confidence severity (C-0496) and synthesis D-0012 (decision substrate frame, two-way reversible, effort 0.5) frame this as drift-remediation: the ADR is the contract; the KB and the agent file have already adopted v1.1.0 in practice.

A second, low-severity adjacent finding (E-0080 / C-0498) is that ADR-0007 (the GitNexus / codebase-memory-mcp primary/fallback policy) lives in `adrs-migrated/`, not in `adrs/`. ADR-0036 (single-location ADR placement convention) names `adrs/` as the canonical location.

Per FR-5, the design-composer is the only ADR-authoring agent in this pipeline; the design-cc per-layer designer correctly surfaced this as Q-CC-8 / synthesis §7 risk #2 / ADR candidate.

## Decision

1. Bump the `codebase-analysis.json` schema to **v1.1.0**.
2. Codify the **blast-radius extension** as the load-bearing addition:
   - `focusAreas[].blast_radius` (object, optional) with sub-fields `consumers` (array of identifiers), `radius_class` (enum: `file / module / service / tenant / org`), and `evidence` (array of file:line refs).
   - `extraction_method` (already in v1.0.0; clarified per terminology table) — the closed enum is preserved as `static_grep / verified_grep / source_inspection / vendor_doc / single_sourced_inference`.
3. Add a **schema-version history table** to the ADR body (this ADR's Implementation Guidance section).
4. Update both downstream consumers (`KB-codebase-research/SKILL.md`, `.claude/agents/discovery-codebase-researcher.md`) to validate against v1.1.0 explicitly (rather than the bare-mention of "extended for blast-radius" that motivated this ADR).
5. Adjacent fix per E-0080: **relocate ADR-0007 from `adrs-migrated/` to `adrs/`** (or, if relocation is deferred, add a forward-cross-reference stub in `adrs/` per ADR-0036). The current-Accepted version is ADR-0007 v2.2.0.
6. The augmented `auditing-mcp` skill (rule OP-7 — trifecta consistency) references the v1.1.0 schema when validating that the W/H/A trifecta is consistent across `.mcp.json`, KB-mcp-platform, and KB-mcp-design.

## Decision Details

| Item | Content |
|---|---|
| Decision | ADR-0018 schema v1.1.0 with `blast_radius` extension; downstream consumers re-validate; ADR-0007 relocated to `adrs/`. |
| Why now | The drift was directly identified by codebase analysis (C-0441/C-0495); design-cc explicitly depends on the v1.1.0 contract for the augmented `auditing-mcp` OP-7 rule and for KB-mcp-platform's documentation of GitNexus's primary-graph role (which leans on blast-radius reasoning). Leaving the drift in place means each downstream re-states "v1.1.0" without a contract to honor. |
| Why this | Eliminating drift at source (the ADR) is the only option that keeps "ADR is the contract" intact (synthesis D-0012). The alternative — "clarify in ADR that KB is v1.1.0 source of truth" — splits the contract across two documents and inverts the ADR-as-source-of-truth posture. |
| Known unknowns | Whether the relocation of ADR-0007 should be paired with a content refresh (the v2.2.0 wording predates this feature's GitNexus install-path details). Tracked as an open item; relocation itself is independent and uncontroversial. |
| Kill criteria | If a future consumer requires schema fields beyond `blast_radius`, this ADR may need a further bump (v1.2.0) — that's normal schema evolution, not a kill criterion. The kill criterion is "if `blast_radius` proves to be the wrong abstraction (e.g., consumers want graph-edge enumeration instead)" — then a future ADR may supersede this one. |

## Rationale

Synthesis §7 ADR candidate #2 names this remediation. The drift is directly evidenced (claim C-0441 / C-0495, batch 4 verified-high). The remediation is straightforward (two-way reversible, effort 0.5 per synthesis RICE). The composer's authoring of this ADR honors FR-5 (per-layer designers cannot author ADRs) and ADR-0009 evidence-based arbitration (claim-grounded resolution). Per ADR-0005 (append-only supersession), the prior v1.0.0 ADR-0018 remains preserved at its filesystem location and in the history; this ADR-0038 is the canonical schema-bearer going forward.

## Options Considered

### Option 1: Bump ADR-0018 to v1.1.0 (selected)

**Pros:** Eliminates drift at source. ADR is the contract; downstream re-validates against the canonical document. Allows the schema-version history table to live in one place.

**Cons:** Requires updating two downstream files in lockstep.

### Option 2: Clarify in ADR that KB is v1.1.0 source of truth

**Pros:** No ADR bump required; minimum-touch.

**Cons:** Splits the contract across two documents. The ADR becomes an index, not a contract. Violates "ADR is the source of truth" discipline.

### Option 3: Status quo (do nothing)

**Pros:** Zero cost.

**Cons:** Drift persists; downstream consumers will diverge further over time. Auditing skills lack a contract to validate against.

## Consequences

### Positive Consequences

- Single canonical schema location restored.
- Downstream consumers validate against a real schema field, not a phrase.
- The `auditing-mcp` augmentation can reference the schema unambiguously.
- ADR-0007 relocation aligns the project with ADR-0036 (single canonical ADR location).

### Negative Consequences

- Three files change in lockstep (ADR-0018 → ADR-0038 supersession marker; KB-codebase-research/SKILL.md; discovery-codebase-researcher.md). Plan-author must sequence these to avoid a windowed inconsistency.
- The relocation of ADR-0007 may surface deferred questions about its content (v2.2.0 was authored before GitNexus install-path was scoped) — but the content itself remains correct; only the location moves.

### Neutral Consequences

- The `extraction_method` enum is preserved as-is; this ADR clarifies its closed-enum nature in the schema-version-history table.
- The `mcp-events.jsonl` schema (ADR-0037) reuses the `extraction_method` field name for terminology consistency, but the two schemas remain separate (different contracts; different files).

## Architecture Impact

1. **Layers affected.** Claude Code / Project Filesystem (the schema lives in KB and agent files); no Dev Environment / Codespaces impact. ADR registry housekeeping.
2. **Components that change.**
   - `adrs/ADR-0018-codebase-analysis-schema.md` — marked `Superseded by ADR-0038`. ADR-0005 keeps the file in place.
   - `adrs/ADR-0038-codebase-analysis-schema-v1-1-0.md` (this file) — new canonical.
   - `adrs/ADR-0007-code-graph-mcp-selection.md` (NEW location) — relocated from `adrs-migrated/`; current-Accepted version is v2.2.0. (Or, if the relocation is deferred to a follow-up, a forward-cross-reference stub at `adrs/ADR-0007-code-graph-mcp-selection.md` pointing to `adrs-migrated/`.)
   - `.claude/skills/KB-codebase-research/SKILL.md` — update `schema_version: 1.0.0` references to `1.1.0` and cite ADR-0038.
   - `.claude/agents/discovery-codebase-researcher.md` — same.
   - `.claude/agents/review-architecture-auditor.md` — confirm its blast-radius validation references the v1.1.0 schema (it already does per claim C-0495).
3. **New dependencies introduced.** None.
4. **Architectural constraints added.** New `focusAreas[]` entries authored after this ADR ships MUST include `blast_radius` when the focus area is non-trivially cross-cutting. Old entries are not retroactively required to backfill the field (per ADR-0005 append-only spirit).

## Implementation Guidance

**Schema-version history table (canonical home):**

| Version | Status | Notes |
|---|---|---|
| 1.0.0 | Superseded | Original; defined in ADR-0018; `focusAreas[]` lacked `blast_radius`. |
| 1.1.0 | Accepted (current) | Adds `blast_radius` object to `focusAreas[]`; clarifies `extraction_method` closed enum; defined here in ADR-0038. |

**Migration discipline:** new `codebase-analysis.json` outputs include `schema_version: "1.1.0"` and `focusAreas[].blast_radius` where applicable. Old outputs (pre-feature) remain valid v1.0.0 — readers tolerant of missing `blast_radius` per "additive schema evolution" discipline.

**ADR-0007 relocation:** preferred is to move the canonical file from `adrs-migrated/ADR-0007-code-graph-mcp-selection.md` to `adrs/ADR-0007-code-graph-mcp-selection.md` and leave a redirect-stub in `adrs-migrated/`. If a plan-author judges the move out-of-scope for this feature, a forward-cross-reference stub at `adrs/` is acceptable as an interim — but the long-term direction is co-location at `adrs/` per ADR-0036.

**No procedural detail.** Per ADR template guidance, sequencing of the three downstream-consumer updates lives in the Plan, not in this ADR.

## Related Information

- Related ADRs: ADR-0018 (superseded by this), ADR-0007 (relocation target; current Accepted v2.2.0), ADR-0005 (append-only supersession discipline), ADR-0036 (single-canonical-ADR-location), ADR-0037 (MCP events JSONL — reuses `extraction_method` field name).
- Referenced specs / docs: synthesis.md §3 D-0012, §7 ADR candidate #2; codebase-analysis-report.md C-0441 / C-0495 / C-0496 / C-0497 / C-0498 / E-0080.
- Issues / PRs: I-DR-001 (server-count contradiction — partially related via cross-reference; primary resolution lives in this Blueprint's Open Items disposition).
- Related KBs: KB-codebase-research (downstream consumer), KB-mcp-platform (consumes the schema indirectly via the `auditing-mcp` augmentation OP-7 rule).
