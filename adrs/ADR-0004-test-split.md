---
id: ADR-0004
version: 2.1.0
status: Accepted
generated: 2026-05-19
generated_by: finalize-reconciler (v4.3.0 naming-convention retroactive update per ADR-0019)
supersedes:
  - {id: ADR-0004, version: 1.0.0}
adrs_inherited:
  - ADR-0001 (orchestrator placement)
applies_to:
  - feature-pipeline
template_format: per ADR.txt v1.0
notes_post_v4: Acceptance criteria now in EARS format per ADR-0015; BDD scenarios mentioned in original ADR were the v2/v3-era choice. v4 adopts EARS strictly. This ADR's core decision (test split with strict input separation) is preserved; the AC syntax changes.
---

# ADR-0004: Test generation split — Acceptance-Tester reads blueprint only; Phase-Validator reads plan

## Status

Accepted — 2026-05-12 (template-migrated from v1.0.0 of the same date)

## Context

The user spec called for a Test-Generator agent that "adds validation steps for each phase. Also an end-to-end test." The natural reading is one agent producing both phase validators and end-to-end tests from the plan. But the literature names "test inversion" as a failure mode: when AI generates both code and tests, tests validate what was built, not what was specified.

The MinimumCD ACD workflow separates Acceptance Criteria (derived from the spec / User-Facing Behavior, observable by an independent observer) from implementation validation (derived from the plan/code).

## Decision

Two sub-agents, with strict input separation:

1. **`test-acceptance-author`** reads the *approved blueprint only*. It does NOT see the build plan. It emits `acceptance-tests.md` containing acceptance scenarios where each scenario is verifiable by someone who has never seen the implementation plan. Each scenario maps back to a blueprint requirement ID. **Per ADR-0015, acceptance scenarios are authored in EARS format** (originally BDD Gherkin; superseded for v4).

2. **`test-phase-validator`** reads the *plan*. It emits per-phase validators inline in `plan.json` (one validator entry per phase) plus an `e2e-test.md` test sequence that runs across all phases.

Both feed Critique-2 (renamed review-cross-artifact-auditor per ADR-0017). Cross-consistency check: every acceptance scenario must be reachable by at least one phase-validator path; every phase artifact must be exercised by at least one validator.

## Decision Details

| Item | Content |
|---|---|
| Decision | Two sub-agents with strict input separation: acceptance-tester reads blueprint only; phase-validator reads plan. Cross-consistency enforced by Critique-2. |
| Why now | Test generation strategy must be settled before plan and acceptance-test sub-agents are built; input separation is a structural property requiring orchestration support, not a content choice. |
| Why this | Prevents test inversion (a named failure mode per claim C-0021); maps to ACD workflow (claim C-0022) which has explicit External Validation stage; modest cost increase (one extra sub-agent invocation) for substantial discipline gain. |
| Known unknowns | Whether the blueprint will be expressive enough to drive acceptance scenarios independently — depends on synth-designer (and per ADR-0016, the composer) producing User-Facing Behavior content with sufficient detail; whether cross-consistency check at Critique-2 will catch all the misalignment cases. |
| Kill criteria | If 3+ consecutive feature runs show acceptance-tester unable to author meaningful acceptance scenarios from blueprint alone (e.g., produces only trivial "system exists" scenarios because blueprint lacks observable-behavior content), the design has shifted to where blueprint and plan are inseparable; revisit with a unified test-author or restructure blueprint authoring to ensure observable-behavior content is present. |

## Rationale

The test-inversion failure mode (claim C-0021) is documented: when AI generates both code and tests, tests validate what was built, not what was specified. Strict input separation at the agent level prevents this structurally — the agent that writes acceptance tests cannot see the plan it might otherwise shape its tests around.

ACD workflow (claim C-0022) is the production-validated template: External Validation stage operates from the spec, separately from Implementation Validation stage which operates from the plan/code. The pipeline mirrors this structure.

The cost is modest — one extra sub-agent invocation. The benefit is that acceptance criteria become a real spec gate: if the plan can pass phase validators but fail acceptance, the plan is wrong, not the tests.

## Options Considered

**Option 1: One combined Test-Generator (the simpler choice).** A single sub-agent reads both blueprint and plan, emits all tests.
- Pros: simpler; one sub-agent; lower latency.
- Cons: defeats the discipline; test inversion is the documented risk.

**Option 2: Substrate change — external test-generation framework like Specmatic.**
- Pros: specialized tool; mature.
- Cons: adds dependency without proportional value at this stage; violates the "compose only Claude Code primitives" hard constraint.

**Option 3 (Selected): Two sub-agents with strict input separation.**
- Pros: structural prevention of test inversion; maps to ACD workflow; cross-consistency check is the explicit safety net.
- Cons: two sub-agent invocations instead of one; modest cost increase; requires blueprint to be expressive enough for acceptance scenarios.

## Consequences

### Positive Consequences

- Prevents test inversion: acceptance tests cannot be shaped by the plan, because the agent that writes them does not see the plan.
- Acceptance criteria become a real spec gate: if the plan can pass phase validators but fail acceptance, the plan is wrong (not the tests).
- Maps cleanly to ACD workflow stages — the design has named external validation.
- Cross-consistency check (run by Critique-2) becomes an explicit, structured verification rather than implicit.

### Negative Consequences

- Two sub-agent invocations instead of one. Modest cost increase.
- Requires the blueprint to be expressive enough to drive acceptance scenarios independently. The Designer sub-agent (and per ADR-0016, the composer) must produce blueprints with explicit User-Facing Behavior sections, not just architecture sketches.
- The "concurrent" invocation requires orchestrator coordination — both sub-agents run from their respective inputs, then their outputs are reconciled.

### Neutral Consequences

- Original ADR specified BDD/Gherkin syntax for acceptance scenarios. Per ADR-0015 (EARS adoption for v4), the AC syntax is now EARS. This ADR's core decision (input separation, two sub-agents) is preserved; only the AC syntax changes.

## Architecture Impact

**Components that change:**
- Sub-agent: `test-acceptance-author` — reads blueprint only.
- Sub-agent: `test-phase-validator` — reads plan only.
- Knowledge skill: `KB-documentation-criteria` — teaches EARS-format AC authoring (post-v4).
- Knowledge skill: `phase-validation-knowledge` — teaches phase-validator authoring.
- Stage 8: runs both sub-agents concurrently with strict input separation.
- Stage 9 (Critique-2, renamed review-cross-artifact-auditor): adds cross-consistency check (every acceptance scenario reachable by ≥1 phase-validator; every phase artifact exercised by ≥1 validator).

**New dependencies introduced:**
- The orchestrator must enforce the input separation — it MUST NOT pass the plan to test-acceptance-author even if it's available.

**Architectural constraints added:**
- test-acceptance-author MUST NOT receive the plan as input. Enforced by orchestrator-side allowlist.
- test-phase-validator's input MUST include the plan and MAY include the blueprint (the latter for context only).
- Cross-consistency check at Critique-2 is mandatory.

**Architectural constraints removed:**
- The simplistic "one Test-Generator" model from the original spec.

## Implementation Guidance

- Orchestrator-level enforcement: when invoking test-acceptance-author, pass ONLY the blueprint path; do not pass plan path even if exists.
- Cross-consistency check pseudocode: for each acceptance-scenario, find a phase-validator path whose execution reaches the scenario's observable behavior; for each phase artifact, find ≥1 validator that exercises it.
- Per ADR-0015, the acceptance-tester emits EARS-format scenarios in the Acceptance Criteria section of the blueprint, or as a sibling artifact when blueprint reaches v(N) approved state.

## Related Information

- Original ADR-0004 v1.0.0: preserved at `ADR-0004-test-split-pre-template-migration.md` per ADR-0014.
- ADR-0015: EARS-format AC adoption — changes AC syntax from BDD to EARS (v4 onward).
- ADR-0017: rename of synth-critic-2 to review-cross-artifact-auditor — runs the cross-consistency check.
- Claims: C-0021 (test inversion named failure mode), C-0022 (ACD 4-stage workflow).

## v4.3.0 retroactive naming-convention update

Per ADR-0019, all sub-agent, knowledge skill, and orchestrator skill references in this ADR have been updated to the v4.3.0 naming convention (phase-prefixed sub-agents, KB-prefixed knowledge skills, recipe-prefixed orchestrator, shared-prefixed cross-phase sub-agents). The pre-update version is preserved at `ADR-0004-test-split-pre-naming-convention.md`. The decision recorded in this ADR is unchanged; only entity names are updated for cross-document consistency.
