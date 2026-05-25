# Design Composition Discipline

The discipline used by `design-composer` during Design Composition. Integrates per-layer Design outputs into a single coherent Blueprint, authors cross-cutting sections, authors ADRs, and produces the Fact Disposition Table.

## Contents

- Inputs
- Outputs
- What the composer does (and what it doesn't)
- Cross-cutting Blueprint sections
- The Fact Disposition Table (per ADR-0018)
- Evidence-based arbitration when per-layer outputs disagree
- ADR authoring (per FR-5)
- Honoring the Rationale Brief
- Composition order and dependencies
- Interaction with the canonical template
- Anti-patterns
- Output expectations

## Inputs

`design-composer` receives:

| Input | Source | Purpose |
|---|---|---|
| Approved PRD | `prd-v<N>.md` (latest accepted) | Scope, layer scope, ACs |
| Per-layer Design outputs | `<layer>-design.md` (one per activated layer) | The substantive design for each layer in scope |
| Codebase analysis JSON | `codebase-analysis.json` | Focus areas, existing patterns, dependencies |
| Synthesis output | `synthesis.md` | Claims that ground design decisions |
| Rationale brief | Orchestrator-supplied | User-confirmed decisions, open items, resolved issues |
| KBs in scope | Per PRD's Layer Scope, at minimum `KB-documentation-criteria` | Templates and disciplines |
| Prior Blueprint (when iterating) | `blueprint-v<N-1>.md` | Predecessor for supersession + delta |

## Outputs

A single Blueprint file at `working/feature/<slug>/blueprint-v<N>.md`, conforming to `../templates/blueprint-template.md`. Plus zero or more ADR files at `adrs/ADR-NNNN-<slug>.md` (canonical project-wide registry per ADR-0036).

The Blueprint is reviewed by `shared-document-reviewer` immediately (per ADR-0017 invocation point 3). Each ADR is reviewed individually (per invocation point 5). Then the Blueprint enters Architecture Audit.

## What the composer does (and what it doesn't)

### The composer DOES

1. **Compose** the Blueprint by integrating per-layer Design outputs into the template's structure.
2. **Author cross-cutting sections** — sections whose content spans multiple layers and cannot be the product of any single per-layer designer.
3. **Author ADRs** for decisions that the per-layer designers surfaced as needing architectural commitment.
4. **Build the Fact Disposition Table** covering every entry in `codebase_analysis.focusAreas`.
5. **Arbitrate** when per-layer designers' outputs conflict, using evidence-based criteria.
6. **Preserve per-layer subsections** — the composer copies per-layer outputs into `### <Layer> Design` subsections largely intact; it does NOT rewrite them.
7. **Surface open items** that emerged from composition (e.g., a cross-layer concern that no per-layer designer addressed).

### The composer DOES NOT

1. **Re-author per-layer Design subsections.** Per-layer designers own their slices; the composer integrates, doesn't rewrite. If a per-layer subsection has problems, the composer surfaces them and the orchestrator routes back to the relevant per-layer designer.
2. **Make per-layer design decisions** beyond what's needed for cross-cutting integration.
3. **Invent ACs.** ACs come from the PRD; the Blueprint refines them per-layer; the composer assembles, doesn't create new ones.
4. **Skip the Fact Disposition Table.** Every `focusAreas` entry gets a row. Skipping is a `critical` completeness violation.
5. **Defer ADRs.** If a decision needs an ADR, the ADR is authored at Design Composition, not later. Per FR-5, only the composer authors ADRs during the Design phase.

## Cross-cutting Blueprint sections

These are sections the composer authors because they integrate across layers. Per the template:

| Section | What it covers |
|---|---|
| **Overview** | Why the feature exists, in one paragraph |
| **Design Summary (Meta)** | Layers in scope, layers explicitly out of scope, ADRs referenced and authored |
| **Background and Context** | Synthesis claims, prerequisite ADRs, external resources |
| **Acceptance Criteria** | EARS-format ACs grouped by layer (carried from PRD + per-layer refinement) |
| **Existing Codebase Analysis** | Implementation paths, integration points, code-inspection evidence, **Fact Disposition Table** |
| **Design** | Per-layer subsections + cross-cutting Architecture Overview, Change Impact Map, Field Propagation Map |
| **Implementation Plan** | Phases (high-level sketch; the full Plan is authored later at Plan Authoring) |
| **Security Considerations** | Threats, mitigations, auth model |
| **Test Boundaries** | What unit/integration/E2E tests cover; what's out of scope for automated testing |
| **Verification Strategy** | Correctness Proof Method; Early Verification Point; Output Comparison; Operational Verification |
| **Future Extensibility, Alternative Solutions, Risks and Mitigation, References, Update History** | Per the template |

Per-layer designers author the `### <Layer> Design` subsections inside `## Design`. The composer wraps those with the cross-cutting parts of `## Design` (Architecture Overview, Change Impact Map, etc.) and authors all other top-level sections.

## The Fact Disposition Table (per ADR-0018)

The single binding between existing-behavior facts (from Discovery Research's `codebase_analysis.focusAreas`) and the Blueprint's design. Every focus area gets one row.

### Row structure

```markdown
| Fact ID | Focus Area | Disposition | Rationale | Evidence |
|---|---|---|---|---|
| FACT-001 | Existing health-check pattern in `services/api/healthz.go` | preserve | The pattern is correct; we're extending it, not replacing | `services/api/healthz.go:14-42` (carried verbatim from focusAreas) |
| FACT-002 | The current `/status` endpoint returns shape `{healthy: bool}` | transform | New shape `{healthy: bool, components: [...]}` adds component-level detail without breaking the boolean field | `services/api/healthz.go:80` |
| FACT-003 | The session-token validation in `middleware/auth.go` | out-of-scope | Auth is not in Layer Scope for this feature | `middleware/auth.go:104-180` |
```

### Disposition values

Four values:

| Disposition | Meaning |
|---|---|
| **preserve** | The existing behavior is correct; the feature does not change it. Brief rationale required. |
| **transform** | The existing behavior changes. State the new outcome. |
| **remove** | The existing behavior is removed. State why. |
| **out-of-scope** | The fact is real but irrelevant to this feature. State which scope boundary excludes it. |

### Discipline

- One row per `focusAreas` entry. No skipping.
- `Fact ID` carried verbatim from `focusAreas[*].fact_id`.
- `Evidence` carried verbatim from `focusAreas[*].evidence`.
- `Rationale` is the composer's contribution — what makes this disposition correct.
- For `transform`, the new outcome MUST be specific enough that a reader can verify "yes, the Design subsection reflects this."

### Cross-reference

Every Design subsection that describes existing behavior references the Fact ID:

```markdown
### Backend Design

The existing health-check pattern (FACT-001) is preserved. The new `/healthz` endpoint extends it by adding component-level details (FACT-002 → transform).
```

`shared-document-reviewer`'s Gate 1 DesignDoc-specific check verifies:

- Every `focusAreas` entry has a Fact Disposition row.
- Every Design subsection that describes existing behavior references at least one Fact ID.

## Evidence-based arbitration when per-layer outputs disagree

Per-layer designers occasionally produce overlapping or conflicting subsections. Examples:

- Backend Design says "caching at the service layer with TTL=60s"
- Query Design says "caching at the data-access layer with TTL=300s"

Both can't be right. The composer arbitrates using evidence-based criteria:

### Arbitration criteria (in priority order)

1. **Honoring the rationale brief.** If the brief commits to one approach, the other is rejected.
2. **Synthesis claims.** A claim from `synthesis.md` that grounds one approach over the other.
3. **Codebase analysis evidence.** If the existing codebase patterns favor one approach (and the feature is meant to be consistent with existing patterns), that approach wins.
4. **Stakeholder concerns from PRD.** If a PRD NFR or Product Policy Decision constrains the choice.
5. **The principle of single responsibility.** If two layers are doing the same job, one should own it. The owner is usually the layer closest to the data.

### Process

1. Identify the conflict explicitly. Quote both per-layer outputs.
2. Apply the criteria above in order. Document which criterion broke the tie.
3. Author the integrated decision in the cross-cutting section (Architecture Overview or a new ADR).
4. Update the affected per-layer subsections to reflect the integrated decision (this is the ONE case where the composer modifies per-layer outputs — and the modification is explicit, with a marker).

If no criterion resolves the conflict, surface to user via the orchestrator's AskUserQuestion. Do NOT silently pick.

### Markers for composer-modified per-layer content

When the composer modifies a per-layer subsection (rare; only for arbitration), the modification is marked:

```markdown
### Backend Design

> **Composer note:** This subsection was updated by `design-composer` to align with the arbitrated caching decision in Architecture Overview. The original per-layer designer's text proposed service-layer caching; the composition decision (per ADR-NNNN) places caching at the data-access layer. See per-layer-designer-output at `backend-design.md` for the original.
```

This keeps the audit trail transparent.

## ADR authoring (per FR-5)

Only the composer authors ADRs during Design Composition. Per-layer designers MUST NOT author ADRs.

### When to author an ADR

Author an ADR when:

- A cross-cutting decision is made that the Blueprint cannot fully explain in prose without losing the rationale
- A decision is made that future iterations might reverse — the ADR records the kill criteria
- A decision is made over alternatives that need to be documented (not just for this run but for future reference)
- A composer arbitration resolved a conflict between per-layer outputs — the ADR records the resolution

### When NOT to author an ADR

Do NOT author an ADR for:

- A decision that's purely within one layer (that's per-layer Design content)
- A decision that's already covered by a prior ADR (reference it; don't duplicate)
- A "documentation" decision (use the Blueprint's prose; ADRs are for architectural commitments)

### ADR template

Per `../templates/adr-template.md`. Frontmatter requires `id`, `version`, `status`, `supersedes`, `adrs_inherited`, `applies_to`, `template_format`, `change_summary`.

### ADR review

Each ADR is reviewed by `shared-document-reviewer` immediately after authoring (per ADR-0017 invocation point 5). Architecture Audit may surface ADR-level concerns later.

## Honoring the Rationale Brief

Per `../rationale-brief.md`, the composer honors the brief. For composition specifically:

- **User-confirmed decisions** from prior phases of the pipeline (Intent Clarification, PRD Approval, per-layer Design dispositions) are binding. The Blueprint must reflect them.
- **Open items** from per-layer Design outputs are integrated: either resolved by the composer (with rationale), deferred to Plan Authoring (with forward pointer), or escalated to user.
- **Resolved issues from prior Blueprint iterations** stay resolved. The composer's brief-honor lens at Architecture Audit explicitly checks for re-surfacing — pre-empt this by carrying resolved-issue references forward.

## Composition order and dependencies

The composer works in a specific order:

1. **Frontmatter and Overview** — quick orientation.
2. **Design Summary (Meta)** — declares layers in scope, ADRs in play.
3. **Background and Context, including Prerequisite ADRs** — sets up the design space.
4. **Acceptance Criteria** — carried from PRD with layer-grouping refinement.
5. **Existing Codebase Analysis + Fact Disposition Table** — grounds the design in existing facts.
6. **Design** — per-layer subsections wrapped with cross-cutting parts (Architecture Overview, Change Impact Map, Field Propagation Map).
7. **Implementation Plan** — high-level phase sketch.
8. **Security, Test Boundaries, Verification Strategy** — cross-cutting concerns.
9. **Future Extensibility, Alternative Solutions, Risks and Mitigation, References, Update History** — closing.
10. **ADRs** — authored in parallel with the relevant sections. Each ADR is a separate file.

The composer iterates: write a draft pass, run an internal CoVe check (does every Blueprint claim ground in a synthesis claim or codebase fact?), revise.

## Interaction with the canonical template

`../templates/blueprint-template.md` has the canonical structure. The discipline above applies to the SUBSTANCE that fills each section; the template provides the STRUCTURE.

Gate 0 checks structural conformance. Gate 1 checks substantive quality (per `gate-0-1-procedure.md` in KB-review-disciplines's DesignDoc-specific checks). Architecture Audit then runs CoVe + blast-radius + brief-honor (per `architecture-audit.md` in KB-review-disciplines).

## Anti-patterns

### Anti-pattern 1: Rewriting per-layer subsections

```markdown
### Backend Design

[The composer rewrote this subsection because the per-layer designer's prose was rough...]
```

The composer's job is integration, not rewriting. Rough per-layer outputs go BACK to the per-layer designer via the orchestrator. The only allowed modification is composer-arbitration of conflicts (with explicit marker).

### Anti-pattern 2: Skipping the Fact Disposition Table

If the PRD says no codebase research was needed (rare; usually only for greenfield features), the Fact Disposition Table is `N/A — no focus areas`. But this MUST be explicit. A missing table without explicit N/A is `critical` completeness.

### Anti-pattern 3: ADR-per-decision

```
ADR-0023: Use Redis for session storage
ADR-0024: TTL of 60s on Redis sessions
ADR-0025: Eviction policy is LRU
```

Three ADRs for what's really one decision (the session-storage approach). Consolidate.

### Anti-pattern 4: Cross-cutting section that's just a list of per-layer outputs

```markdown
## Architecture Overview

Frontend uses React. Backend uses Go. API uses OpenAPI. Database uses Postgres.
```

That's not an Architecture Overview — that's a stack inventory. Architecture Overview describes how the layers integrate, what the data flow is, where the boundaries are.

### Anti-pattern 5: Composer making per-layer decisions

```markdown
## Architecture Overview

The frontend component will be a React functional component using useState for local state.
```

That's a per-layer Frontend decision, not a cross-cutting concern. It belongs in `### Frontend Design`, where the per-layer Frontend designer authored it (or should have).

### Anti-pattern 6: Silent open-item drop

A per-layer subsection says "Open: caching strategy TBD." The composer integrates the subsection but doesn't carry the open item forward. By Architecture Audit, the open item is lost.

Discipline: every per-layer open item appears in the Blueprint's Undetermined Items or is explicitly resolved with rationale. None are silently dropped.

## Output expectations

A complete Blueprint has:

1. Valid frontmatter per `../shared-conventions.md`
2. `## Contents` checklist with each box that will be `[x]` when the section is filled
3. `### Layer Scope` matching the PRD's Layer Scope (using the 9 canonical engineering layers)
4. Design Summary (Meta) declaring layers in scope, ADRs referenced, ADRs authored
5. Acceptance Criteria carried from PRD with per-layer grouping
6. Existing Codebase Analysis with complete Fact Disposition Table (every `focusAreas` entry has a row)
7. `## Design` with 9 per-layer subsections (each substantive or marked `N/A — out of scope`) + cross-cutting Architecture Overview, Change Impact Map, Field Propagation Map
8. Implementation Plan (high-level sketch)
9. Security Considerations
10. Test Boundaries
11. Verification Strategy (Correctness Proof Method, Early Verification Point, Output Comparison or N/A, Operational Verification or N/A)
12. Future Extensibility, Alternative Solutions, Risks and Mitigation, References, Update History

Plus, separately, zero or more ADR files at `adrs/ADR-NNNN-<slug>.md` (canonical project-wide registry per ADR-0036).

Output goes to `working/feature/<slug>/blueprint-v<N>.md`. `shared-document-reviewer` invoked immediately for Gate 0/1 (with `codebase_analysis` populated from `codebase-analysis.json`). Each ADR is reviewed individually. After all approvals, the Blueprint enters Architecture Audit.
