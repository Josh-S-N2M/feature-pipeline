---
id: ADR-0019
version: 1.0.0
status: Accepted
generated: 2026-05-19
generated_by: finalize-reconciler (v4.3.0 production session)
supersedes: []
adrs_inherited:
  - ADR-0001 v2.0.0 (orchestrator placement — naming applies to the orchestrator skill)
  - ADR-0006 (synthesis inlined — naming applies to the 6 inlined synthesis sub-agents)
  - ADR-0016 (per-layer fan-out — naming applies to all 9 per-layer designers)
  - ADR-0017 (document-reviewer + critic renames — extends with the shared- prefix and replaces synth-architecture-auditor/synth-cross-artifact-auditor with review-architecture-auditor/review-cross-artifact-auditor)
applies_to:
  - feature-pipeline blueprint v4.3.0
  - all sub-agents in the v4.3 pipeline topology
  - all knowledge skills (KBs) in the v4.3 pipeline
  - orchestrator skill folder name
template_format: per ADR.txt v1.0
---

# ADR-0019: Naming convention — phase-prefixed sub-agents, KB-prefixed knowledge skills, recipe-prefixed orchestrator

## Status

Accepted — 2026-05-19

## Context

Through v4.0–v4.2, the pipeline accumulated 27 sub-agents and ~13 knowledge skills with naming inconsistencies that obscure intent:

- Some sub-agents carry a `synth-` prefix that originated from the synthesize pipeline (e.g., `synth-extractor`, `synth-designer`), but the prefix doesn't communicate which stage/phase the agent runs in.
- Per-layer designers are named `synth-designer-frontend`, `synth-designer-backend`, etc. — the layer is the meaningful axis, but `synth-designer-` repeats redundantly.
- Knowledge skills end with `-knowledge` (e.g., `frontend-design-knowledge`, `documentation-criteria` — the latter without `-knowledge`, inconsistently).
- The orchestrator is just `feature-pipeline` — easy to confuse with the project name.
- `document-reviewer` is a single sub-agent used across multiple phases, but its cross-cutting nature isn't signaled in the name.

The user (Q-v4.3-naming) explicitly requested a naming convention that (a) makes phase-belonging visible in sub-agent names, (b) distinguishes knowledge skills from orchestrator skills, and (c) signals when a sub-agent is shared across phases vs phase-specific.

Phase taxonomy was also re-cut in v4.3 (Q-v4.3-phases): "research" was the wrong category name because the discovery phase encompasses BOTH plan-authoring (where KBs and ADRs are consulted to decide if research is even warranted) AND execution. The corrected phase taxonomy is intake / discovery / synthesis / design / review / plan / test / finalize.

## Decision

Adopt a uniform naming convention applied retroactively to all sub-agents, knowledge skills, and the orchestrator skill in v4.3.0+:

1. **Sub-agents**: prefixed by phase. Format: `{phase}-{role}.md`. Phases: `intake-`, `discovery-`, `synthesis-`, `design-`, `review-`, `plan-`, `test-`, `finalize-`. Cross-phase sub-agents (currently only `shared-document-reviewer`) use the `shared-` prefix.

2. **Knowledge skills**: prefixed `KB-`. Format: `KB-{topic}/SKILL.md`. The `KB-` prefix immediately distinguishes them from orchestrator and recipe skills in `.claude/skills/` listings.

3. **Orchestrator skill**: prefixed `recipe-`. The user-facing slash command stays `/feature-pipeline` (API stability); only the skill folder name carries the `recipe-` prefix: `.claude/skills/recipe-feature-pipeline/SKILL.md`. The `recipe-` prefix signals "this skill is the recipe that orchestrates a multi-stage workflow" and distinguishes it from KB-skills (knowledge) and any future recipe skills.

## Decision Details

| Item | Content |
|---|---|
| Decision | All sub-agents, KBs, and orchestrator skill folders adopt the prefix scheme above. v4.3.0 ships with renames applied across the blueprint, all 21 ADRs (3 new + 18 retroactively-updated), and the Implementation Plan. |
| Why now | The pipeline crossed a complexity threshold in v4.0 (27 sub-agents) where ad-hoc names began obscuring topology. v4.3 is the natural inflection point — before Phase 2 implementation begins — to lock the convention. Renaming after implementation would cascade across `.claude/agents/*.md`, `.claude/skills/*/SKILL.md`, the orchestrator body's invocation references, and any external integrations. |
| Why this scheme | Phase prefixes map to the pipeline's phase taxonomy (which itself maps to the user's mental model of "what stage is this in"). KB- and recipe- prefixes distinguish three skill kinds (knowledge / recipe-orchestrator / regular-skills) at folder-listing time. `shared-` signals cross-cutting concerns explicitly rather than implicitly. The convention is uniform — no special cases — which means future sub-agents and KBs can be named by mechanical rule without re-arguing the convention each time. |
| Known unknowns | Whether `recipe-` will collide with future Anthropic-introduced naming conventions for Claude Code skills (no current collision; risk is low). Whether `shared-` will need sub-categories if cross-phase sub-agents proliferate (currently only one). |
| Kill criteria | If a future ADR demonstrates that two sub-agents legitimately straddle exactly two adjacent phases AND the `shared-` prefix obscures rather than clarifies their belonging, revisit whether `cross-phase-{phase1}-{phase2}-` is needed. Currently no such case exists. |

## Rationale

**Phase prefixes communicate topology at glance.** A user reading `.claude/agents/` should be able to tell from filenames alone which sub-agents run when. `synth-prd-author` doesn't communicate that the PRD author runs in the intake phase; `intake-prd-author` does. Same for `discovery-codebase-researcher` vs the v4.2 name `synth-codebase-researcher` — the latter implied the synthesize pipeline, but it actually runs in discovery (Stage 3) and feeds synthesis (Stage 4).

**KB- prefix matches an established pattern.** Many AI engineering teams use `KB-` for knowledge bases. The convention signals "look here for declarative content; the agent that loads me will do the procedural work" — useful when triaging skill bodies.

**recipe- prefix anticipates future orchestrators.** Currently `recipe-feature-pipeline` is the only orchestrator. If the user later builds `recipe-implementation-pipeline` or `recipe-deployment-pipeline`, the convention extends naturally.

**Slash command vs skill folder name decoupling.** The slash command `/feature-pipeline` is the user-facing API; renaming it would break user muscle memory and any external documentation. The skill folder name is internal-only and can rename safely. This decoupling is a pattern worth committing to: when an internal naming convention shifts, the user-facing API stays put.

**Retroactive application to all v4.x ADRs.** Per the user's direction, ADRs 0001-0018 are issued v2 versions with name updates per ADR-0014's retroactive-migration pattern. This avoids the cognitive cost of readers having to mentally translate `synth-critic-1` → `synth-architecture-auditor` → `review-architecture-auditor` when working with v4.3+. Pre-v2 versions of each ADR are preserved per ADR-0005's append-only supersession discipline.

## Consequences

### Positive

- Sub-agent names instantly communicate phase belonging; topology is readable from `.claude/agents/` listings.
- KB- and recipe- prefixes make three skill kinds visually distinct in `.claude/skills/` listings.
- `shared-` prefix flags cross-cutting concerns to future maintainers.
- Slash command preserved → no user-visible breaking change.
- Retroactive ADR migration eliminates name-translation cognitive overhead.

### Negative

- One-time rename cost: 27 sub-agents, 17 KBs, 1 orchestrator folder, 18 retroactive ADR migrations, all blueprint references. Mitigated by v4.3 being executed before Phase 2 implementation (no `.claude/agents/*.md` or `.claude/skills/*/SKILL.md` files exist on disk yet — the renames are blueprint-text-only).
- Slight verbosity increase for some names (e.g., `discovery-codebase-researcher` is 28 chars vs `synth-codebase-researcher` at 25). Acceptable cost for phase clarity.
- Convention adds a constraint: future sub-agent introductions must fit one of the 8 phase prefixes or use `shared-`. If a new phase is genuinely needed, the taxonomy must be extended via a follow-up ADR.

### Neutral

- Discovery phase rename ("research" → "discovery") is partly a naming change and partly a taxonomy clarification. ADR-0021 addresses the discovery-phase architecture substantively; this ADR only locks the naming.

## Implementation Guidance

- All v4.3.0 blueprint text uses new names exclusively (no historical name references except in changelog entries that document the rename itself).
- ADRs 0001-0018 issue v2 versions with name substitutions; pre-v2 versions preserved as `{name}-pre-naming-convention.md` in `adrs-migrated/`.
- Phase 2 implementation (out of scope for this ADR; tracked in Implementation Plan) will create `.claude/agents/*.md` and `.claude/skills/*/SKILL.md` files using the new names directly — no rename-on-disk step needed.
- Any new sub-agent or KB introduced after v4.3 MUST follow the convention. Pre-existing references in non-v4.3 artifacts (v3, v4.0, v4.1, v4.2 — preserved per ADR-0005) are NOT retroactively edited.

## Related Decisions

- ADR-0001 v2 (orchestrator placement) — applies to the renamed `recipe-feature-pipeline` skill.
- ADR-0006 (synthesis inlined) — applies to the renamed 6 synthesis-* sub-agents.
- ADR-0014 (ADR retroactive migration) — the retroactive ADR name updates follow this ADR's migration pattern.
- ADR-0017 (document-reviewer + critic renames) — extended in v4.3: the critic renames continue (synth-critic-1 → synth-architecture-auditor → review-architecture-auditor), and document-reviewer renames to shared-document-reviewer.
- ADR-0020 (KB structure) — uses the KB- prefix established here.
- ADR-0021 (discovery phase architecture) — uses the discovery- prefix established here.

## Open Questions

None at v4.3.0 acceptance time. The convention is uniform and exhaustive over current sub-agents/skills.
