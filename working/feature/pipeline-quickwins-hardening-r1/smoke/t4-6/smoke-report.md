---
task_id: T4.6
smoke_type: fixture-based simulation
ac_coverage: AC-CC-2-g
adr_reference: ADR-0057 (absence-default rule)
authored: 2026-05-27
---

# T4.6 Smoke Report — Pre-feature Checkpoint Resume

## Purpose

This smoke verifies that a `checkpoint.json` written before `pipeline-quickwins-hardening-r1` shipped (and therefore lacking the `execution_mode` field on every stage) is handled correctly by the FR-2 dispatch self-check. The key property under test is ADR-0057's absence-default rule: a missing `execution_mode` field on any stage is treated as `specialist-dispatch`, not as an error and not as `parent-driven-workaround`.

The test also validates the counter-case: an explicit `execution_mode: parent-driven-workaround` on any stage in a FULL-scope run must trigger a refusal with the four FR-6 diagnostic fields. This confirms that absence and explicit workaround have distinct semantics.

## Fixtures

| Fixture | Path | scope_class | Stages with execution_mode | Expected verdict |
|---|---|---|---|---|
| A: pre-feature | `fixtures/pre-feature-checkpoint.json` | FULL | none (all absent) | PASS |
| B: with-workaround | `fixtures/pre-feature-checkpoint-with-workaround.json` | FULL | prd_authoring = parent-driven-workaround | REFUSE |

Fixture A models a realistic pre-feature checkpoint: a completed FULL-scope feature run with seven stages (intent_clarification through execution) where no stage was ever assigned an `execution_mode` field because the field did not exist as a first-class schema entry before ADR-0057.

Fixture B is the counter-fixture. It has the same structure but with `prd_authoring` explicitly carrying `execution_mode: parent-driven-workaround`. This demonstrates that the absence-default rule applies only to absent fields — an explicit workaround declaration is never silently normalized away.

## Harness

`smoke/t4-6/fr2_self_check.py` — a standalone Python script that:

1. Loads a checkpoint fixture from the path given on the command line.
2. Reads `scope_class` from the fixture (fail-closed if missing).
3. Resolves each stage's effective `execution_mode` by applying the absence-default rule (`stage.get("execution_mode", "specialist-dispatch")`).
4. Applies the FR-2 gate logic: for FULL scope, refuse if any resolved mode is `parent-driven-workaround`; for MINOR/PATCH, pass unconditionally.
5. Prints a structured report and exits 0 (PASS) or 1 (REFUSE).

## Test Run — Fixture A (pre-feature-checkpoint.json)

Command:
```
python3 smoke/t4-6/fr2_self_check.py fixtures/pre-feature-checkpoint.json
```

Output:
```
fixture: fixtures/pre-feature-checkpoint.json
scope_class: FULL
verdict: PASS

stage resolution (absence-default applied):
  intent_clarification: specialist-dispatch [absent→default]
  prd_authoring: specialist-dispatch [absent→default]
  research_planning: specialist-dispatch [absent→default]
  per_layer_design: specialist-dispatch [absent→default]
  design_composition: specialist-dispatch [absent→default]
  plan_authoring: specialist-dispatch [absent→default]
  execution: specialist-dispatch [absent→default]

diagnostic: none
```

Exit code: 0

All seven stages resolved to `specialist-dispatch` via the absence-default rule. scope_class is FULL, so the FR-2 gate evaluated the full pipeline. No stage triggered a refusal. The self-check passed.

## Test Run — Fixture B (pre-feature-checkpoint-with-workaround.json)

Command:
```
python3 smoke/t4-6/fr2_self_check.py fixtures/pre-feature-checkpoint-with-workaround.json
```

Output:
```
fixture: fixtures/pre-feature-checkpoint-with-workaround.json
scope_class: FULL
verdict: REFUSE

stage resolution (absence-default applied):
  intent_clarification: specialist-dispatch [absent→default]
  prd_authoring: parent-driven-workaround
  research_planning: specialist-dispatch [absent→default]
  per_layer_design: specialist-dispatch [absent→default]
  design_composition: specialist-dispatch [absent→default]
  plan_authoring: specialist-dispatch [absent→default]
  execution: specialist-dispatch [absent→default]

diagnostic:
  mechanism: FR-2 dispatch self-check
  offending_artifact: prd_authoring
  rule_violated: FULL-scope features prohibit parent-driven-workaround execution mode per PRD §FR-2 and ADR-0057
  remedial_hint: either change scope_class to MINOR/PATCH OR reconfigure the stage to specialist-dispatch
```

Exit code: 1

The explicitly declared workaround on `prd_authoring` triggered a refusal. All four FR-6 diagnostic fields were emitted. The six other stages (absent → default) did not interfere with the refusal of the one stage that was explicitly set.

## Verification Grid (per Plan L1/L2/L3)

| Level | Criterion | Status |
|---|---|---|
| L1 | `fixtures/pre-feature-checkpoint.json` created and well-formed JSON | PASS |
| L1 | `fixtures/pre-feature-checkpoint-with-workaround.json` created and well-formed JSON | PASS |
| L2 | Harness applies absence-default: absent field resolves to `specialist-dispatch` | PASS |
| L2 | Harness does not treat absent field as `parent-driven-workaround` | PASS |
| L2 | scope_class FULL gates the full FR-2 check (not bypassed as MINOR/PATCH) | PASS |
| L3 | Fixture A (all absent, FULL scope): self-check passes, no diagnostic | PASS |
| L3 | Fixture B (one explicit workaround, FULL scope): self-check refuses with FR-6 diagnostic | PASS |
| L3 | Absence and explicit workaround produce different outcomes (semantic distinction confirmed) | PASS |

## AC-CC-2-g Coverage

AC-CC-2-g requires that the orchestrator correctly handles a pre-feature checkpoint on resume — specifically, that the absence of `execution_mode` fields does not cause a refusal or incorrect behavior. This smoke confirms:

- A FULL-scope pre-feature checkpoint with no `execution_mode` fields on any stage is accepted by the FR-2 self-check.
- The acceptance is because absence maps to `specialist-dispatch` (the safe default), not because the check is skipped.
- The counter-fixture confirms the check is still live: an explicit workaround on even one stage triggers a refusal with the correct diagnostic.

All three verification levels pass.
