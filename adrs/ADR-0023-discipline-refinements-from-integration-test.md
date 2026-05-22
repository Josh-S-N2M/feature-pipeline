---
id: ADR-0023
title: Discipline refinements from /healthz integration-test simulation
status: accepted
date: 2026-05-20
deciders: [user, claude]
supersedes: []
superseded_by: []
related: [ADR-0017, ADR-0021]
---

# ADR-0023: Discipline refinements from /healthz integration-test simulation

## Context

After Phase 2 implementation (Batches 1-9) completed and the repo was zipped, an end-to-end simulation of the 12-stage feature pipeline was run against a synthetic `/healthz` feature against a Node + Express + PostgreSQL target codebase. The simulation walked all 12 stages, fired all 6 user gates, and exercised every reviewer and auditor invocation point.

Four discipline gaps surfaced that the existing artifacts do not address. Three were caught by the audit machinery during the simulation (validating that the machinery works), but each defect class would benefit from being codified as an explicit check rather than relying on reviewer thoroughness. The fourth gap is a documentation-level impedance mismatch between the `synthesize` skill's original purpose and the feature pipeline's reuse of its agents.

### What the simulation observed

| Gap | Where it surfaced | Severity of consequences if not codified |
|---|---|---|
| 1. Per-FR AC count check not formalized | REV-PLAN-r1 caught fabricated `FR-5.AC-3, AC-4` references via per-FR enumeration; CA-F-001 then caught the same fabrications still present in individual task bodies after the cross-reference table was fixed | Without an explicit check, the per-FR enumeration depends on reviewer thoroughness; naive total-count matching (19=19) would have passed both |
| 2. Disposition taxonomy lacks `designer-general-knowledge` | REV-RP-r1 caught two false `covered-by-KB:...` claims (K8s probe params, BUILD_SHA injection); author was forced to demote to awkward `codebase-topic` framing | Future Research Plans will continue to either fabricate KB coverage or over-research well-trodden patterns |
| 3. Numeric annotation checks ambiguously owned | AA-F-001 (Tier A xhigh auditor) caught `(4)` vs. 5-item enumeration in Blueprint — annotation-level work for the highest-cost reasoning lane | Continues to misuse architecture auditor budget on counts; substantive architectural checks crowded out |
| 4. `synth-substrate` three-option requirement mismatched feature-pipeline use | Simulation produced straw-man "Option C" entries for D-2, D-4, D-5 (within-substrate tactical decisions) to satisfy the synthesize skill's hard exclusion | Future feature pipelines either produce dishonest straw-men or violate the synthesize skill's contract |

## Decision

Four targeted discipline changes, scoped narrowly to their respective files, plus this ADR for the audit trail.

### Decision 1: Codify per-FR AC enumeration check as a Gate 1 substantive check

`KB-review-disciplines/references/gate-0-1-procedure.md` gains a new substantive check (always run, not doc-type-specific):

> **Per-FR AC enumeration check** — for any document referencing PRD acceptance criteria, the reviewer enumerates ACs per FR from the source PRD and compares per-FR coverage in the target document. Naive total-count matching is not sufficient — fabricated ACs in one FR can offset missing ACs in another. The check walks individual task bodies (e.g., per-task `Satisfies AC:` fields), not only top-level cross-reference tables.

Fabricated AC references → `critical`/`consistency`. Omitted AC references → `important`/`completeness`.

### Decision 2: Add `designer-general-knowledge` as the fifth Research Plan disposition

`KB-documentation-criteria/references/disciplines/discovery-planning.md` extends the four-way triage to five:

5. **Is this well-trodden community knowledge a competent designer can apply?** If the question has a standard, widely-documented answer (e.g., conventional K8s probe parameters, standard Docker build-arg patterns, REST status code semantics), mark `disposition: designer-general-knowledge`. The downstream designer applies the convention with **explicit rationale in the per-layer Design section**. No external research.

`research-plan-template.md` adds the disposition to the enumerated options. A decision filter is documented for choosing between `designer-general-knowledge` and the other dispositions (KB-coverage, codebase-topic, external-research).

This is a positive disposition, not a fallback — claiming it commits the designer to documenting rationale so reviewers can audit.

### Decision 3: Reassign annotation-level numeric checks from architecture audit to Gate 1

Two reciprocal edits:

(a) `gate-0-1-procedure.md` gains a **numeric internal consistency check** as a substantive Gate 1 check — annotated counts (`(N)`, `total_tasks: N`, "N tests") are compared to enumerated items; mismatches are `important`/`consistency`.

(b) `KB-review-disciplines/references/architecture-audit.md` "When NOT to apply this discipline" gains an explicit exclusion: annotation-level numeric consistency belongs to Gate 1, not to the architecture auditor's three lenses (CoVe / blast-radius / brief-honor). If such a mismatch surfaces in the auditor, downgrade to `MINOR` and reference the Gate 1 check that should have caught it. Substantive cross-layer numeric consistency (e.g., "DB-check 500ms nests within probe timeout 2s") remains in the auditor's `cross_section_consistency` lens.

### Decision 4: Document `synth-substrate` two-mode operation in recipe-feature-pipeline

`recipe-feature-pipeline/SKILL.md` Step 6 gains a "Feature-pipeline mode of `synth-substrate`" subsection that explicitly documents:

- The agent has two modes: **substrate-comparison** (used by `synthesize` skill, hard three-option enumeration) and **implementation-strategy** (used by feature pipeline, variable option count 1-N with explicit rationale for the count).
- The synthesize skill's "three options enumerated" hard exclusion applies to substrate-comparison mode only.
- Implementation-strategy mode's output is folded into `synthesis.md` as a decision-substrate section, not validated against `substrate-mapping.schema.json`.
- Discipline rules for implementation-strategy mode: option count justified by genuine option space (not quota); straw-men are an anti-pattern; single-option decisions are acceptable with credible "no alternatives" rationale.

The `synthesize` skill itself is **not** modified — its contract for substrate-comparison mode (3 hard options of native/adapter/substrate_change) is correct for its original multi-substrate research-synthesis purpose. The mode-switch documentation lives in the recipe-feature-pipeline skill because it describes how the feature pipeline reuses an existing agent in a different mode.

## Options Considered

### For Decision 1 (per-FR check)

| Option | Selected? | Rationale |
|---|---|---|
| Codify in `gate-0-1-procedure.md` as a Gate 1 substantive check | ✓ | Catches the defect at single-doc review (Stage 9), one stage earlier than cross-artifact audit (Stage 11). Cheaper |
| Add to architecture audit's brief-honor lens | ✗ | Wastes xhigh reasoning on enumeration; mismatched with auditor's substantive focus |
| Build a separate AC-validation pre-flight script | ✗ | Adds tooling overhead for a check that fits cleanly in existing reviewer prose |

### For Decision 2 (fifth disposition)

| Option | Selected? | Rationale |
|---|---|---|
| Add `designer-general-knowledge` to the triage | ✓ | Honest about source of authority; commits designer to documenting rationale |
| Force `external-research-topic` for these cases | ✗ | Wastes external-research budget on conventional knowledge; produces low-value research notes |
| Force `codebase-topic` (the simulation's workaround) | ✗ | Lies about what the codebase research is actually doing; awkward for greenfield cases |
| Expand KBs to cover everything that would otherwise be `designer-general-knowledge` | ✗ | Infinite scope; KBs would balloon to encyclopedias of community knowledge |

### For Decision 3 (reviewer-scope reassignment)

| Option | Selected? | Rationale |
|---|---|---|
| Move annotation-level numeric checks to Gate 1; explicitly exclude from architecture audit | ✓ | Matches budget to task complexity; preserves auditor for substantive work |
| Keep dual ownership; let either reviewer catch | ✗ | Wastes xhigh reasoning when caught by auditor; non-deterministic which stage catches |
| Build a separate numeric-consistency pre-flight script | ✗ | Tooling overhead for a check that fits cleanly in Gate 1 |

### For Decision 4 (substrate mode-switch)

| Option | Selected? | Rationale |
|---|---|---|
| Document mode-switch in `recipe-feature-pipeline/SKILL.md` | ✓ | Localizes the change to the consuming skill; preserves the `synthesize` skill's contract |
| Modify the `synthesize` skill's hard exclusion to allow variable option count | ✗ | Damages the synthesize skill's correctness for its original purpose |
| Fork `synth-substrate` into two separate agents (`synth-substrate-substrate-comparison`, `synth-substrate-implementation-strategy`) | ✗ | More disciplined long-term but Phase-2 churn for a documentation-level fix; defer to a future ADR if simulation experience surfaces ongoing confusion |
| Leave undocumented; rely on agent prompts and prose | ✗ | This is what the simulation exposed — silent reuse produces straw-men |

## Decision Details

### Why now

The /healthz integration-test simulation was the first end-to-end exercise of the Phase 2 implementation. The four defect classes are exactly the kind of finding the simulation was designed to surface — discipline gaps that don't show up in isolated unit-test-style examples of any single stage but emerge from running the full chain. Codifying them now (a) closes the gaps before Phase 3 empirical calibration adds runtime cost; (b) preserves the audit-trail link between the simulation observation and the discipline change; (c) makes Phase 3 work easier because real runtime invocations honor these refinements from the start.

### Why this approach (versus more invasive changes)

Each of the four changes is a **documentation/discipline refinement** rather than a structural change. No agent contract changes, no new sub-agents, no schema migrations. The changes are:

- File edits to 4 discipline / template / SKILL.md files (~120 lines total)
- One new ADR (this one) recording rationale

The simulation found no BLOCKER-class defects — the pipeline structure is sound. These are all calibration-level refinements.

### Known unknowns

- **The `designer-general-knowledge` filter's calibration.** The "smell that you're misusing this" guidance (>50% of needs landing in this disposition) is a starting heuristic. Real-feature usage may need tighter or looser guidance. Plan to revisit after 3-5 real feature runs.
- **Synthesis mode-switch durability.** Documenting two modes in `recipe-feature-pipeline/SKILL.md` is the lower-cost path now. If real runs continue to confuse the modes, a future ADR may fork the agent into two distinct sub-agents with separate prompts and schemas.
- **Whether the per-FR check generalizes.** The check is specified for PRD-derived AC references. Other documents (test plans, audit checklists) also reference ACs and may benefit from the same per-FR walk; defer codifying until a real run surfaces an additional case.

### Kill criteria

This ADR should be reconsidered if:

- A real feature run surfaces a defect class that any of these four changes block legitimate work (false positive at Gate 1, over-restrictive triage, useful annotation checks moved out of the auditor's reach).
- The `synth-substrate` mode-switch documentation proves insufficient: real runs continue to produce straw-man options or violate the synthesize skill's schema. Then fork the agent.
- The `designer-general-knowledge` disposition becomes a routine workaround for KB gaps that should be closed — in which case the KBs need expansion, not the disposition.

## Consequences

### Positive

- Discipline gaps from the integration-test simulation are closed at the documentation level.
- Single-doc reviewer at Stage 9 now catches the AC-fabrication defect class one stage earlier than cross-artifact audit.
- Architecture auditor's xhigh reasoning budget no longer drained by annotation-level counts.
- Research Plan authors have a honest disposition for community-knowledge questions; reviewers have an auditable framing for them.
- Feature pipeline's use of `synth-substrate` is documented; future ambiguity about straw-men vs. genuine options is resolved.

### Negative

- Five small files now drift slightly from their pre-simulation contract. Anyone holding the Phase-2 zip will see version skew — minor.
- The `designer-general-knowledge` disposition adds one more triage decision the author must make per information need. Small cognitive cost.
- The per-FR AC check adds Gate 1 work proportional to FR count. For PRDs with 5-20 FRs (typical), the overhead is small; for larger PRDs (>50 FRs), reviewers may want to delegate to a pre-flight script.

### Neutral

- This ADR sits alongside the other Phase-2 pipeline-meta ADRs (0011-0022). No cross-feature ADR pollution.
- The `synthesize` skill's contract is unchanged; users invoking it directly see no difference.

## Implementation

Five files edited in this commit:

1. `.claude/skills/KB-review-disciplines/references/gate-0-1-procedure.md` — adds Per-FR AC enumeration check and Numeric internal consistency check to substantive Gate 1 checks (Decision 1 + Decision 3a)
2. `.claude/skills/KB-review-disciplines/references/architecture-audit.md` — adds exclusion for annotation-level numeric checks (Decision 3b)
3. `.claude/skills/KB-documentation-criteria/references/disciplines/discovery-planning.md` — extends triage to five dispositions; adds decision filter (Decision 2)
4. `.claude/skills/KB-documentation-criteria/references/templates/research-plan-template.md` — adds `designer-general-knowledge` to disposition enumeration; updates external-research justification requirement (Decision 2)
5. `.claude/skills/recipe-feature-pipeline/SKILL.md` — adds "Feature-pipeline mode of `synth-substrate`" subsection to Step 6 (Decision 4)

Plus this ADR.

No agent file changes, no schema changes, no template-structure-breaking changes.

## References

- Integration-test simulation: ran 2026-05-20, deleted post-review per user request
- ADR-0017 — document-reviewer integration (Gate 0/1 framework this refines)
- ADR-0021 — discovery phase architecture (disposition taxonomy this extends)
- `synthesize` skill SKILL.md — substrate-comparison mode's unchanged contract
