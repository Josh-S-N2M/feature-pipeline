---
id: ADR-0016
version: 1.0.0
status: Accepted
generated: 2026-05-12
generated_by: synth-designer (new ADR for blueprint v4)
supersedes: []
adrs_inherited:
  - ADR-0001 (orchestrator placement)
  - ADR-0005 (append-only supersession)
  - ADR-0009 (rationale brief at stage handoff)
  - ADR-0013 (Blueprint template adoption)
applies_to:
  - feature-pipeline (blueprint v4, forthcoming)
template_format: per ADR.txt v1.0
---

# ADR-0016: Per-layer fan-out + composer fan-in for Stage 5 (Design)

## Status

Accepted — 2026-05-12

## Context

Blueprint v3 placed a single `synth-designer` sub-agent at Stage 5, responsible for the entire blueprint. The user (Q-v4-3 inverted) confirmed: fan out across layers first, then fan in to synthesize. This matches the canonical Blueprint template's structure (ADR-0013), which has 9 per-layer Design sections that map naturally to per-layer designer sub-agents.

Research findings ground the design:

- **Fan-out-then-synthesize is a documented pattern** (claim C-R3-0008). N=3-5 is the efficient range; we use up to 9 designers but scope detection (per blueprint v3 Stage 0) selects only the ones whose layers are in scope.
- **Diamond topology delivers measured benefits** (claim C-R3-0009: AdaptOrch +11.4pp).
- **Consistency gap is the primary risk** (claim C-R3-0007: 36.9% of multi-agent failures from inter-agent misalignment; claim C-R3-0013: four documented patterns for parallel-agent contradiction resolution).
- **Filesystem isolation matters** (claim C-R3-0011: parallel agents sharing filesystem corrupt each other's work; one-agent-per-zone discipline required).
- **Production sequential alternatives exist for cost reasons** (claim C-R3-0030: Barnacle.ai chose sequential 15-agent execution over parallel due to rate limits and cost predictability).

## Decision

Stage 5 (Design) is split into Stage 5a (fan-out) and Stage 5b (fan-in):

**Stage 5a — Fan-out:** Up to 9 per-layer designer sub-agents run in parallel, each authoring the corresponding per-layer Design section of the canonical Blueprint template. Only designers whose layers are in scope (per Stage 0 feature-scope.json) are activated. Each per-layer designer:
- Authors ONLY its assigned per-layer Design section
- Authors layer-scoped EARS-format acceptance criteria
- Emits a `dependencies_on_other_layers` structured field naming cross-layer dependencies it has made assumptions about
- Does NOT author ADRs; ADRs are composer-only (Q-v4-8)
- Does NOT author cross-cutting sections (Overview, Design Summary, Background, Change Impact Map, etc.)

**Stage 5b — Fan-in:** `synth-designer-composer` runs after Stage 5a completes. The composer:
- Receives all per-layer designer outputs as input
- Authors the cross-cutting Blueprint sections (Overview, Design Summary YAML, Background, Architecture Overview, Data Flow top-level, Change Impact Map, Interface Change Matrix, Fact Disposition Table, top-level Components, Verification Strategy)
- Resolves cross-layer dependencies surfaced by per-layer designers using evidence-based arbitration (claim C-R3-0013)
- Detects and flags inter-section contradictions as critique issues
- Introduces any new ADRs that the cross-layer reconciliation requires
- Produces the final, integrated `05-blueprint-v1.md` artifact conforming to the Blueprint template

The 9 potential per-layer designers (matching the Blueprint template's Layer Scope checklist):
- `synth-designer-claude-code-fs`
- `synth-designer-frontend`
- `synth-designer-backend`
- `synth-designer-api`
- `synth-designer-query`
- `synth-designer-database`
- `synth-designer-cicd`
- `synth-designer-iac`
- `synth-designer-codespaces`

## Decision Details

| Item | Content |
|---|---|
| Decision | Fan out across up to 9 per-layer designers (conditional on scope), then fan in to a single composer for cross-cutting authoring and integration. Composer is the only author of ADRs at Stage 5. |
| Why now | Adopting the Blueprint template (ADR-0013) before Stage 5 is restructured would force composer-driven authoring at the wrong topology; locking in the fan-out-then-fan-in topology before the template's per-layer sections become load-bearing prevents rework. |
| Why this | Maps 1:1 with Blueprint template's per-layer Design sections; each layer's domain knowledge skill loads in only the relevant designer (focused context per claim C-R3-0029); parallelism reduces wall-clock time for multi-layer features; cross-layer dependency reconciliation centralized in composer prevents the consistency gap (claim C-R3-0007). |
| Known unknowns | Whether the 9-designer ceiling is right (template defines 9 layers; future layers like ML deployment, data warehouse may emerge); whether per-layer designers will reliably emit useful `dependencies_on_other_layers` content without explicit guidance (synth-designer-* knowledge skills must teach this); whether the composer can resolve cross-layer contradictions without spawning sub-agents (it cannot — recursion-safe — so all resolution is composer's own reasoning). |
| Kill criteria | If 3+ feature runs produce blueprints where the composer's cross-layer reconciliation produces critique-1 issues at the same rate as a single-designer v3 baseline, the fan-out is not buying additional quality and the topology should revert to single-designer (or move to alternative parallelism, e.g., per-layer review of a single-author blueprint). |

## Rationale

The strongest case for fan-out is structural alignment with the Blueprint template. The template defines per-layer Design sections; per-layer designers map directly. The alternative (one designer authoring all 9 sections sequentially) creates a single-agent bottleneck that the template's structure does not require.

The strongest risk against fan-out is the consistency gap (claim C-R3-0007 — 36.9% of multi-agent failures from inter-agent misalignment). Mitigated by:

(1) **Entity canonicalization before fan-out** (claim C-R3-0013 pattern a): the orchestrator's rationale brief (per ADR-0009) is generated once and passed to all per-layer designers, providing a single structured representation of the feature's intent, PRD requirements, and inherited ADRs. Each designer reads the same brief.

(2) **Explicit cross-layer dependency declarations** (Q-v4-10 confirmed assumption-based approach): per-layer designers emit `dependencies_on_other_layers` fields documenting assumptions they made about other layers' decisions. The composer reconciles.

(3) **Evidence-based arbitration at the composer** (claim C-R3-0013 pattern b): when two per-layer designers' outputs conflict, the composer assesses evidence strength rather than picking one designer's output by default. Conflicts that cannot be resolved by evidence are flagged as critique-1 issues for human triage.

(4) **Filesystem isolation** (claim C-R3-0011): each per-layer designer writes ONLY to its corresponding section of the blueprint. The orchestrator coordinates by assigning each designer a section identifier; designers cannot write outside their section. The composer integrates by reading all section files and writing the final blueprint.

The composer-only ADR authorship (Q-v4-8) is the right discipline: ADRs are cross-cutting decisions. A per-layer designer introducing an ADR about its layer in parallel with another per-layer designer introducing a contradicting ADR would create irreconcilable artifacts. Centralizing ADR authorship at the composer prevents this.

## Options Considered

**Option 1: Single synth-designer (v3 status quo).** One sub-agent authors entire blueprint.
- Pros: simple topology; no consistency-gap risk; unified voice.
- Cons: single-agent bottleneck for large multi-layer features; per-layer domain knowledge loading is conditional on scope but all loaded into one agent's context budget; no parallelism gain.

**Option 2: Sequential per-layer authoring.** synth-designer-* run one at a time in dependency order (Database → Query → Backend → API → Frontend, etc.).
- Pros: each layer can read previous layer's output as ground truth (no assumptions needed); no consistency gap.
- Cons: no parallelism gain; depth-of-pipeline grows with layer count; one bad layer blocks all downstream layers.

**Option 3 (Selected): Fan-out then fan-in (Diamond topology) with composer-only ADR authorship and assumption-based dependency resolution.**
- Pros: parallelism for multi-layer features (claim C-R3-0009 measured benefit); each per-layer designer has focused context with relevant domain skills; composer centralizes cross-layer reconciliation; matches Blueprint template structure; consistency gap mitigated by entity canonicalization + evidence-based arbitration.
- Cons: 27 total sub-agents in inventory (existing 18 + new 9); composer must handle cross-layer reconciliation without spawning sub-agents (composer's own context budget bears the integration cost); production research (claim C-R3-0030) shows some teams choose sequential over parallel for cost predictability.

## Consequences

### Positive Consequences

- Parallelism for multi-layer features: typical scoped feature activating 2-4 designers can run them concurrently, reducing wall-clock time meaningfully.
- Each per-layer designer's context budget is dedicated to its layer's domain knowledge — no cross-contamination from unrelated domain skills.
- Composer's job is well-scoped: integrate per-layer outputs, author cross-cutting sections, resolve dependencies. Smaller than "design everything."
- Cross-layer dependency assumptions are explicit (per-layer designers emit `dependencies_on_other_layers`), making them reviewable and reconcilable rather than hidden in prose.
- ADR authorship is centralized at the composer, preventing parallel-author ADR contradictions.
- Maps cleanly to the Blueprint template's per-layer Design sections — structural enforcement is straightforward.

### Negative Consequences

- Total sub-agent inventory grows: blueprint v3 had 18 named sub-agents; v4 adds 9 per-layer designers + 1 composer (subtracting the single synth-designer from v3) = 27 net. Per claim C-R2-0010, large agent catalogs can degrade selection accuracy — but agent enum is not browsed by Claude at orchestrator level (orchestrator picks agents directly), so the concern is less acute than for tool catalogs.
- Composer must reconcile cross-layer contradictions in its own reasoning, without sub-agent help (recursion-safe constraint). For features with many cross-layer dependencies, composer's context budget may strain.
- Per-layer designers can produce contradictory outputs about shared entities; reconciliation work at the composer can be substantial. Cost not measured for this pipeline yet.
- Some features have cross-cutting decisions that don't map to any single layer (e.g., authentication strategy spans Frontend + Backend + API + Database). The composer authors these in cross-cutting sections, but per-layer designers may have already assumed conflicting versions.

### Neutral Consequences

- Stage 5 wall-clock increases relative to single-designer when only one layer is in scope (overhead of fan-out + fan-in machinery for trivial parallelism). Acceptable for the multi-layer cases.
- The synth-designer-* knowledge skills become more numerous but each one is focused. May actually be easier to maintain than one large `design-knowledge` skill.

## Architecture Impact

**Components that change:**
- Stage 5 topology: split into 5a (fan-out) and 5b (fan-in).
- Sub-agent inventory: `synth-designer` (v3) removed; 9 new per-layer designers + `synth-designer-composer` added.
- `design-knowledge` (v3): replaced with `design-composition-knowledge` (composer-only) and 9 per-layer `<layer>-design-knowledge` skills (or alternatively, the existing domain knowledge skills serve dual purpose with extended content covering blueprint-section authoring).
- Stage 5b output: still a single `05-blueprint-v1.md`; internal complexity (multiple authors) is invisible to downstream stages.
- Stage 0 (Preflight): produces `00-feature-scope.json` with per-layer-designer activation flags (already in v3 plan; now load-bearing).
- document-reviewer: receives a single blueprint document for review; no awareness of per-layer authoring required.

**New dependencies introduced:**
- Each per-layer designer depends on its corresponding domain knowledge skill (from blueprint v3's stub-skill inventory) AND on `documentation-criteria` (for Blueprint template per ADR-0011).
- `synth-designer-composer` depends on `design-composition-knowledge` (new), `documentation-criteria`, and the output artifacts of all activated per-layer designers.

**Architectural constraints added:**
- Per-layer designers MUST NOT write outside their assigned per-layer Design section.
- Per-layer designers MUST NOT author ADRs (composer-only).
- Per-layer designers MUST emit `dependencies_on_other_layers` for any cross-layer assumption.
- Composer MUST run after all activated per-layer designers complete.
- Composer MUST resolve cross-layer contradictions via evidence-based arbitration; unresolvable contradictions become Critique-1 input.

**Architectural constraints removed:**
- Single-author Stage 5 from blueprint v3.

## Implementation Guidance

- Each per-layer designer's tools: Read (rationale brief + PRD + relevant codebase analysis); Write (its per-layer Design section file). NO Agent tool (recursion-safe).
- Per-layer designer skill loadout: `documentation-criteria`, `claude-code-filesystem-knowledge`, `general-coding-principles-knowledge`, and the layer-specific domain knowledge skill. 3-5 skills total per designer (per blueprint v3 §3.3 rule of thumb).
- Per-layer designer maxTurns: 40.
- synth-designer-composer's tools: Read (all per-layer outputs + rationale brief + PRD); Write (full integrated blueprint). NO Agent tool.
- synth-designer-composer skill loadout: `documentation-criteria`, `claude-code-filesystem-knowledge`, `design-composition-knowledge`, `general-coding-principles-knowledge`. Composer may also load relevant domain knowledge skills based on which cross-layer reconciliations are likely.
- synth-designer-composer maxTurns: 60 (composer authors more content than any single per-layer designer).
- The `dependencies_on_other_layers` field shape: list of `{depends_on_layer: <layer>, assumption: <statement>, fallback_if_wrong: <action>}` entries.
- Per the Blueprint template, mark per-layer sections corresponding to unchecked Layer Scope checkboxes as `N/A — out of scope`. Composer authors these section markers — per-layer designers for unchecked layers do not run.

## Related Information

- ADR-0013: Blueprint template adoption — per-layer Design sections map to per-layer designers.
- ADR-0009: rationale brief — orchestrator generates once per stage handoff; provides entity canonicalization (claim C-R3-0013 pattern a) at fan-out.
- ADR-0017 (forthcoming): document-reviewer integration — reviews the integrated blueprint, not per-layer outputs individually.
- Claims C-R3-0007 through C-R3-0013: fan-out-fan-in patterns, consistency gap, dependency resolution patterns.
- Claim C-R3-0030: production tradeoffs (Barnacle chose sequential over parallel for cost predictability) — informs our kill criteria.
- User-confirmed: Q-v4-3 inverted (fan-out then fan-in), Q-v4-8 (composer-only ADR authorship), Q-v4-9 (9 per-layer designers), Q-v4-10 (assumption-based cross-layer resolution).
