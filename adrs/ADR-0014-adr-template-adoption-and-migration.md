---
id: ADR-0014
version: 2.0.0
status: Accepted
generated: 2026-05-19
generated_by: finalize-reconciler (v4.3.0 naming-convention retroactive update per ADR-0019)
supersedes: []
adrs_inherited:
  - ADR-0005 (append-only supersession)
  - ADR-0011 (canonical document skill)
applies_to:
  - feature-pipeline (blueprint v4, forthcoming)
  - retroactive: ADRs 0001 through 0010 in this pipeline's design conversation
template_format: per ADR.txt v1.0 (this ADR is itself authored in the template)
superseded_by_consolidation: 2026-05-25
superseded_canonical_archived_to: adrs/superseded/ADR-0014-pre-consolidation-canonical.md
---

# ADR-0014: Adoption of the uploaded ADR template + retroactive migration of ADRs 0001-0010

## Status

Accepted — 2026-05-12

## Context

The user provided an ADR template (uploaded as `ADR.txt`) with explicit structural elements not consistently captured in this pipeline's existing ADRs (0001 through 0010, plus 0007 v2). The template's distinguishing features:

- **Decision Details table** with four required fields: `Why now` (timing rationale), `Why this` (1-3 line justification vs alternatives), `Known unknowns` (at least one stated uncertainty), `Kill criteria` (a signal that should trigger reversal).
- **Separate Architecture Impact section** covering components that change, new dependencies introduced, architectural constraints added/removed.
- **Implementation Guidance section** with explicit principle-only constraint ("Use dependency injection" ✓ vs "Implement in Phase 1" ✗) — no implementation procedures.
- **Options Considered** with explicit Pros/Cons per option and a "Selected" marker on the chosen option.

Existing ADRs 0001-0010 use a less-structured format derived ad-hoc during blueprint v2 and v3 design. Some content maps cleanly to the new template; some does not (`Kill criteria` was never authored; `Architecture Impact` was folded into `Consequences`).

Per Q-v4-5 Option A (user-confirmed): retroactively migrate all existing ADRs to the new template.

## Decision

Adopt the uploaded ADR template as the canonical structure for all ADRs produced by the pipeline going forward. Retroactively migrate the 11 existing ADR files (0001 through 0010, plus ADR-0007 v1 which is superseded but preserved per ADR-0005) to the new template structure. The template lives in `KB-documentation-criteria` per ADR-0011.

## Decision Details

| Item | Content |
|---|---|
| Decision | All ADRs use the uploaded template structure. Existing ADRs 0001-0010 (11 files) are retroactively migrated. New ADRs 0011-0018 are authored in the template from the start. |
| Why now | Adopting the template before blueprint v4 ensures every ADR v4 inherits is in the canonical structure. Migrating existing ADRs in the same batch avoids hybrid format states that complicate shared-document-reviewer's ADR review (doc_type: ADR). |
| Why this | The template's `Decision Details` fields (especially `Kill criteria`) and separate `Architecture Impact` section provide structured surfaces that shared-document-reviewer can validate; existing ADR format requires per-ADR judgment of where content sits. The structured form is materially better for AI-driven review (claim C-R3-0023: template conformance enabled by application-layer enforcement). |
| Known unknowns | Whether all 11 existing ADRs have content that meaningfully maps to `Kill criteria` (some decisions may not have a clear reversal signal — e.g., ADR-0005's append-only invariant is foundational and reversal would require redesigning the pipeline). For such ADRs, `Kill criteria` will be authored as "Not applicable — foundational invariant; reversal requires whole-pipeline redesign." |
| Kill criteria | If retroactive migration produces ADRs where 50%+ of the template fields are placeholder content ("Not applicable" or "TBD"), the template is over-engineered for our decision shape and a slimmer template should supersede this one. |

## Rationale

Structural ADRs pay specific dividends in this pipeline:

(1) Document-reviewer's `doc_type: ADR` Gate 0 check needs structural required-element verification. With a canonical template, "required elements" is well-defined; without, it's per-ADR judgment.

(2) The `Kill criteria` field forces author discipline. Per claim C-R3-0014 (AI tendency to fabricate over-precision and over-confidence), explicit kill-criteria is a counter-pressure: the author must name a signal that would invalidate the decision, which surfaces hidden assumptions.

(3) The `Why now` field prevents premature decisions. Decisions made because "it seemed good at the time" but with no timing rationale tend to be the first to bit-rot.

(4) Architecture Impact as a separate section makes blast-radius explicit and reviewable, complementing the review-architecture-auditor's analysis.

The migration cost is one-time. The structural benefit is permanent.

## Options Considered

**Option 1: New ADRs only (forward-only adoption).** ADRs 0011-0018 use the new template; 0001-0010 grandfathered with their current structure.
- Pros: no migration work; existing artifacts unchanged.
- Cons: hybrid format in the same pipeline's ADR set; shared-document-reviewer must support multiple structures; ADR cross-references are weakened when target ADR has different fields than source.

**Option 2: Full migration including content rewrite.** Rewrite all 11 existing ADRs from scratch using the new template, with original content reorganized + new fields populated.
- Pros: complete consistency; every ADR has all template fields.
- Cons: high migration effort; risk of altering original decisions through "rewriting" (Theseus' Ship problem — at what point is the rewritten ADR no longer the original?).

**Option 3 (Selected): Structural migration preserving original content.** Reorganize existing ADR content into the new template structure. Original decision text preserved verbatim where it fits a template field. Add missing fields (`Kill criteria`, `Why now`, separate `Architecture Impact`) by authoring new content grounded in the original ADR's context. Mark fields where original ADR provides no basis as "Not specified in original; inferred from context" or "Not applicable — foundational invariant."
- Pros: consistency without rewriting decisions; original content preserved; new fields force articulation of previously implicit decisions (especially Kill criteria and Architecture Impact).
- Cons: some hybrid content (original prose + new template structure); the inference step for missing fields requires care.

## Consequences

### Positive Consequences

- All ADRs in the pipeline are structurally consistent.
- Document-reviewer's `doc_type: ADR` Gate 0 check has a fixed required-element target.
- Kill criteria field forces explicit articulation of reversal signals — improves long-term decision quality.
- Architecture Impact section makes blast-radius reviewable per ADR independently of review-architecture-auditor analysis.
- New contributors learn one ADR format, not two.

### Negative Consequences

- Migration effort: 11 ADRs (10 unique IDs plus ADR-0007 v1) need restructuring in this same turn.
- Some retrofitted ADRs will have "Not specified in original" placeholders where the new template requires content the original didn't capture. This is honest but visible artifact debt.
- Versioning: per ADR-0005 (append-only), each migrated ADR is a NEW version of that ADR, with `supersedes:` pointing to the pre-migration version. The pre-migration versions remain as `*-pre-template-migration.md` files.

### Neutral Consequences

- The ADR.txt template adopts `Kill criteria` as a required field; many software engineering teams use ADR formats (MADR, Y-statements) that don't require this. The pipeline diverges from the broader ADR ecosystem here, but the divergence is intentional — `Kill criteria` is the most important addition.

## Architecture Impact

**Components that change:**
- `KB-documentation-criteria`: extended with ADR template (per ADR-0011).
- All existing ADR files (0001-0010, plus ADR-0007 v1): retroactive migration produces new versions in the canonical template structure.
- ADRs added in v4 (0011-0018, this ADR being one of them): authored directly in the canonical template.
- finalize-reconciler: when producing new ADRs during resolution loops, must use the canonical template.
- design-composer (per ADR-0016): when introducing new ADRs at Stage 5b, must use the canonical template.
- shared-document-reviewer: `doc_type: ADR` Gate 0 verifies presence of template's required sections (Status, Context, Decision, Decision Details with 4 rows, Rationale, Options Considered, Consequences with 3 sub-sections, Architecture Impact, Implementation Guidance, Related Information).

**New dependencies introduced:**
- None new; ADR structure depends on `KB-documentation-criteria` skill which is already a pipeline dependency.

**Architectural constraints added:**
- All ADRs MUST follow the canonical template structure.
- `Kill criteria` field MUST be authored (may be "Not applicable — foundational invariant" with rationale, but cannot be left blank).
- `Why now` and `Why this` fields MUST be authored.
- Original ADR content is preserved verbatim during retroactive migration where it fits a template field — no content rewriting unless explicitly required to fit the new structure.

**Architectural constraints removed:**
- Ad-hoc ADR structures used in v2/v3 are no longer permitted.

## Implementation Guidance

For retroactive migration of ADRs 0001-0010:

1. For each existing ADR, identify which template fields the original content populates and which require new authoring.
2. Preserve original Context, Decision, Rationale, and Consequences text where it fits cleanly. Reorganize only where the template structure requires.
3. Author `Decision Details` table by extracting one-sentence Decision, identifying timing rationale from Context (`Why now`), summarizing Rationale (`Why this`), naming uncertainties from Consequences (`Known unknowns`), and inferring reversal signals (`Kill criteria`).
4. Move components-and-dependencies content from Consequences into a separate `Architecture Impact` section.
5. Confirm `Implementation Guidance` is principle-only — if original ADRs contain implementation procedures, move those to a separate note rather than including them in this section.
6. Version each migrated ADR: pre-migration becomes `<original-filename>-pre-template-migration.md`; new version uses the original filename and includes `supersedes: [{id: ADR-<N>, version: <prev>}]` frontmatter.

For new ADRs (0011-0018, this one included):
- Author directly in the canonical template.
- Use this ADR (0014) as a reference example.

## Related Information

- User-provided template: ADR.txt (uploaded; canonical from this ADR forward).
- ADR-0011: template lives in `KB-documentation-criteria`.
- ADR-0005: append-only supersession applies to ADR migration — original ADR versions preserved.
- ADR-0017 (forthcoming): shared-document-reviewer's `doc_type: ADR` Gate 0 check operates against this template's required-element list.
- Claim C-R3-0023: template conformance requires application-layer enforcement; the shared-document-reviewer provides this.

## v4.3.0 retroactive naming-convention update

Per ADR-0019, all sub-agent, knowledge skill, and orchestrator skill references in this ADR have been updated to the v4.3.0 naming convention (phase-prefixed sub-agents, KB-prefixed knowledge skills, recipe-prefixed orchestrator, shared-prefixed cross-phase sub-agents). The pre-update version is preserved at `ADR-0014-adr-template-adoption-and-migration-pre-naming-convention.md`. The decision recorded in this ADR is unchanged; only entity names are updated for cross-document consistency.
