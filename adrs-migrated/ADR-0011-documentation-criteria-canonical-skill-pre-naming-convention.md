---
id: ADR-0011
version: 1.0.0
status: Accepted
generated: 2026-05-12
generated_by: synth-designer (new ADR for blueprint v4)
supersedes: []
adrs_inherited:
  - ADR-0001 (orchestrator placement)
  - ADR-0010 (knowledge skill frontmatter correction)
applies_to:
  - feature-pipeline (blueprint v4, forthcoming)
template_format: per ADR.txt v1.0 (uploaded; adopted via ADR-0014)
---

# ADR-0011: Adoption of `documentation-criteria` as the canonical document skill

## Status

Accepted — 2026-05-12

## Context

Multiple pipeline stages produce structured documents: Intent Clarification (Stage 1), PRD (new Stage 1.5), Blueprint (Stage 5), ADRs (added throughout), and Plan (Stage 7). The user has provided high-quality templates for PRD, Blueprint, and ADR. The Intent Clarification document template and the Plan document template still need to be derived.

Without a single canonical home for document templates and conventions, the pipeline risks template duplication across per-document-type knowledge skills, drift between templates, inconsistent enforcement, and skill description budget bloat (each per-document-type skill carrying its own copy of conventions).

An existing knowledge skill, `documentation-criteria`, is described as "Use when creating or reviewing technical documents, or determining which documents are required." It is referenced by the `document-reviewer` sub-agent's `skills:` frontmatter. It is the natural home for templates and conventions.

## Decision

Adopt `documentation-criteria` as the single canonical document skill for the pipeline. All document templates (PRD, Blueprint, ADR, Intent Clarification, Plan) live in this skill, organized by document type. All sub-agents that author or review documents reference `documentation-criteria`; per-document-type knowledge skills (`intent-clarification-knowledge`, `prd-authoring-knowledge`, `design-knowledge`, etc.) carry process knowledge (how to elicit content, what good content looks like, common failure modes) but do NOT carry the templates themselves — they reference templates from `documentation-criteria`.

## Decision Details

| Item | Content |
|---|---|
| Decision | All document templates and document-authoring conventions live in a single canonical knowledge skill, `documentation-criteria`; per-document-type skills carry process knowledge only. |
| Why now | The pipeline is moving from JSON-shaped intent output to markdown-shaped templated documents at multiple stages (Intent Clarification, PRD, Blueprint, ADR, Plan). Establishing the single-source-of-truth pattern before stage proliferation prevents fragmentation. |
| Why this | Avoids template duplication; single update point for template revisions; aligns with existing `documentation-criteria` skill already referenced by `document-reviewer`; preserves the per-document-type knowledge skills for process/elicitation content. |
| Known unknowns | The combined skill size will grow with each template added; whether the platform's per-skill compaction budget (5K tokens kept after compaction per claim C-R2-0006) materially affects long-running sub-agents that invoke this skill repeatedly. |
| Kill criteria | If `documentation-criteria` exceeds ~50K tokens AND practical experience shows downstream sub-agents losing template fidelity after auto-compaction, supersede this ADR with a multi-skill-by-document-type split. |

## Rationale

The fan-out alternative (one skill per document type carrying its own template) was rejected because: (a) each template's conventions (frontmatter format, supersession rules, traceability discipline) are common across document types — duplicating them increases drift risk; (b) the document-reviewer already references `documentation-criteria` — extending the existing skill is lower-friction than adding new skills the reviewer must learn about; (c) the skill description budget (per claim C-R2-0004, 1% of context window, 1536 chars per entry hard cap) is consumed once for one well-described canonical skill instead of many vaguer per-template descriptions.

The risk of skill bloat is real but mitigated. Templates organized as referenced sections within the skill allow sub-agents to focus on the specific template they need without loading the others fully into reasoning. Per claim C-R3-0029 (Codified Context paper), production agent specifications routinely run 327-711 lines; templates exceeding that are signal that organization needs work, not that the architecture needs splitting.

## Options Considered

**Option 1: One skill per document type.** Per-document-type knowledge skill carries both template AND process knowledge.
- Pros: smaller individual skills; tighter scope per skill.
- Cons: template duplication of common conventions (frontmatter, supersession, traceability); document-reviewer would need to load multiple skills to validate any document; skill description budget consumed faster.

**Option 2: Templates as bundled files in skill directories.** Each template lives as a separate `.md` file inside `.claude/skills/documentation-criteria/templates/`; the skill body references files.
- Pros: easy to maintain; clean diff history per template.
- Cons: Claude Code's skill bundle support for `.md` files inside skill directories is not standard for inline reading from sub-agent context (skills loaded via `skills:` frontmatter inject the SKILL.md body; bundled files require additional Read tool calls). Adds runtime cost.

**Option 3 (Selected): Single `documentation-criteria` skill with templates organized as referenced sections within SKILL.md.**
- Pros: matches existing convention; document-reviewer already loads this skill; templates available in context at sub-agent startup without additional tool calls; single update point.
- Cons: skill grows large over time; future templates compound the issue. Mitigated by kill criteria above.

## Consequences

### Positive Consequences

- Single source of truth for document templates and conventions.
- `document-reviewer` already integrated; no architectural change required for the reviewer to validate new document types — only template content added.
- Per-document-type knowledge skills become smaller (process only), aligning with the 327-711 line range that production research shows works well.
- Frontmatter, supersession, and traceability conventions are defined exactly once.

### Negative Consequences

- Single skill becomes large. Five document templates (PRD, Blueprint, ADR, Intent Clarification, Plan) plus shared conventions section likely lands at 40-60K tokens total.
- Sub-agents loading `documentation-criteria` carry the full content even when authoring only one document type. Per claim C-R2-0011 (30-40% of context budget for knowledge), this consumes a meaningful share of the working budget.
- Updates to one template are committed alongside any others modified at the same time; harder to isolate version-control diffs per template than if they were separate files.

### Neutral Consequences

- Naming stays `documentation-criteria` (existing convention) rather than something like `document-skill` or `documents-knowledge`. Existing references in `document-reviewer.md` continue to work.

## Architecture Impact

**Components that change:**
- `documentation-criteria` skill: extended with templates section containing PRD, Blueprint, ADR, Intent Clarification, and Plan templates. Shared conventions section remains.
- Per-document-type knowledge skills (`intent-clarification-knowledge`, `prd-authoring-knowledge`, `design-knowledge`, `planning-knowledge`): shrink. Templates removed. Process knowledge retained.
- Every sub-agent that authors documents: loads `documentation-criteria` always-preload (in addition to its role-specific knowledge skill).

**New dependencies introduced:**
- None. The skill exists; only its content scope is extended.

**Architectural constraints added:**
- All document templates MUST be authored within `documentation-criteria` — no per-skill template hosting is permitted.
- All per-document-type knowledge skills MUST reference `documentation-criteria` for template structure, not duplicate it.

**Architectural constraints removed:**
- None.

## Implementation Guidance

- Templates inside `documentation-criteria` should be organized as `## Template: <DocType>` sections, with each section containing the full template structure as a fenced code block or inline reference.
- The shared conventions section should sit above the templates (frontmatter format, supersession discipline, traceability rules) so it's read first.
- Per-document-type knowledge skills should reference templates by skill section name (e.g., "See `documentation-criteria` → Template: PRD") rather than copying template content.
- Use dependency injection conceptually: the per-document-type skill teaches *how* to fill the template, not what the template looks like.

## Related Information

- ADR-0010 (frontmatter correction): `documentation-criteria` must use `user-invocable: false` without `disable-model-invocation: true`.
- ADR-0014 (forthcoming): ADR template adoption — uses the ADR template from `documentation-criteria`.
- ADR-0013 (forthcoming): Blueprint template adoption — uses the Blueprint template from `documentation-criteria`.
- ADR-0017 (forthcoming): document-reviewer integration — `document-reviewer` references `documentation-criteria` for all template structures.
- Claim C-R3-0028: codebase analysis schemas vary; no industry-standard schema. Documentation schemas are similar — defining our own and committing to one canonical home is the right call.
