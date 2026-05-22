# ADR-0004: Test generation split — Acceptance-Tester reads blueprint only; Phase-Validator reads plan

## Status
Accepted — 2026-05-12

## Context
The user spec called for a Test-Generator agent that "adds validation steps for each phase. Also an end-to-end test." The natural reading is one agent producing both phase validators and end-to-end tests from the plan. But the literature names "test inversion" as a failure mode: when AI generates both code and tests, tests validate what was built, not what was specified.

The MinimumCD ACD workflow separates Acceptance Criteria (derived from the spec / User-Facing Behavior, observable by an independent observer) from implementation validation (derived from the plan/code).

## Decision
Two sub-agents, with strict input separation:

1. **synth-acceptance-tester** reads the *approved blueprint only*. It does NOT see the build plan. It emits `acceptance-tests.md` containing BDD-shaped Gherkin scenarios where each scenario is verifiable by someone who has never seen the implementation plan. Each scenario maps back to a blueprint requirement ID.

2. **synth-phase-validator** reads the *plan*. It emits per-phase validators inline in `plan.json` (one validator entry per phase) plus an `e2e-test.md` test sequence that runs across all phases.

Both feed Critique-2. Cross-consistency check (enforced by Critique-2): every acceptance scenario must be reachable by at least one phase-validator path; every phase artifact must be exercised by at least one validator.

## Consequences

Positive:
- Prevents test inversion: acceptance tests cannot be shaped by the plan, because the agent that writes them does not see the plan.
- Acceptance criteria become a real spec gate: if the plan can pass phase validators but fail acceptance, the plan is wrong (not the tests).
- Maps cleanly to ACD workflow stages — the design has named external validation.

Negative:
- Two sub-agent invocations instead of one. Modest cost increase.
- Requires the blueprint to be expressive enough to drive BDD scenarios independently. The Designer sub-agent (ADR-0001 derived) must produce blueprints with explicit User-Facing Behavior sections, not just architecture sketches.

## Alternatives considered

- **Adapter (one combined Test-Generator)**: viable, simpler, defeats the discipline. Test inversion is the documented risk.
- **Substrate change (external test-generation framework like Specmatic)**: viable but adds dependency without proportional value at this stage.

## Evidence

Backed by C-0021 (test inversion is a named failure mode — verified), C-0022 (ACD 4-stage workflow with observable acceptance criteria — verified).

## Substrate registry version
v1.0 (2026-05-12)
