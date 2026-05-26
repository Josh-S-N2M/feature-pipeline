---
id: ADR-0057
version: 1.0.1
status: Accepted
generated: 2026-05-26
generated_by: design-composer
supersedes: []
adrs_inherited:
  - ADR-0044
  - ADR-0005
applies_to:
  - pipeline-quickwins-hardening-r1
  - recipe-feature-pipeline orchestrator
  - checkpoint.json schema (project-wide)
template_format: per KB-documentation-criteria ADR template v1.0
change_summary: Promote-and-formalize checkpoint.execution_mode from a documented-but-aspirational field (already present in recipe-feature-pipeline/SKILL.md:138 and in the live checkpoint.json) to a first-class load-bearing audit surface, with canonical enum {specialist-dispatch, parent-driven-workaround} and absence-equals-specialist-dispatch backward-compatibility rule. v1.0.1 prose-only amendment per pipeline-quickwins-hardening-r1 Architecture Audit cycle 1 finding I-AA-004 (recommended-severity): the v1.0.0 §Context overclaimed novelty by stating "no existing execution_mode field on checkpoint.json today"; the field is in fact documented in SKILL.md:138 and 412 and is present (currently nulled) in the live checkpoint.json. Reworded to accurately describe pre-existing state ("promote-and-formalize" rather than "introduce"). The decision content of this ADR (the closed enum, the single writer, the reader, the absence-default rule, the OP-6-style audit posture) is unchanged.
---

# ADR-0057: `checkpoint.execution_mode` as a First-Class Documented Field

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

Accepted — 2026-05-26

## Context

FR-2 of the `pipeline-quickwins-hardening-r1` feature requires the orchestrator's dispatch step to refuse the dispatch loop when the feature's scope class is FULL and any stage is configured for "single-agent fallback." To do that, the orchestrator needs to inspect a configuration surface that today is implicit rather than explicit.

The synthesis (D-0003) and the per-layer cc-design analysis both observed: "single-agent fallback" is not currently a named, inspectable on-disk configuration. The dispatch-mode posture is implicit in the orchestrator's stage-graph. ADR-0044's flatten decision preserves a historical `parent-driven-workaround` behavioral posture, but that posture is not a serialized field on `checkpoint.json`.

The `execution_mode` field is documented in the orchestrator's checkpoint schema (see `recipe-feature-pipeline/SKILL.md:138` for the schema example and `recipe-feature-pipeline/SKILL.md:412` for the writer that records `checkpoint.execution_mode = "specialist-dispatch"` at Stage 1) and is present (currently nulled) in this feature's working `checkpoint.json` — see the live `working/feature/pipeline-quickwins-hardening-r1/checkpoint.json:106` entry `"execution_mode": null`. The field is therefore not net-new in name; what is new is its status as a load-bearing audit surface that downstream sub-agents inspect. This ADR's contribution is **promote-and-formalize**: it canonicalizes the field as the FR-2 dispatch-self-check inspection surface, fixes the closed-enum values (`specialist-dispatch`, `parent-driven-workaround`), names the single writer (the orchestrator at dispatch time), names the reader (the FR-2 self-check), and fixes the absence-default rule (`absence-equals-specialist-dispatch`). The framing of "introduce as a new first-class documented field" used elsewhere in this ADR is therefore a slight overclaim of novelty — what is being introduced is the field's promotion to first-class documented schema status, not the field itself. [Framing correction inserted 2026-05-26 per pipeline-quickwins-hardening-r1 Architecture Audit cycle 1 finding I-AA-004 (recommended-severity). The decision content of ADR-0057 is unchanged; only the framing of the field's pre-existing state is corrected.]

Because `checkpoint.json` is the orchestrator's resume contract — it is what allows a paused or interrupted feature run to be resumed deterministically — adding a field to it is a cross-cutting schema decision that affects every component reading `checkpoint.json`: the orchestrator at dispatch time, the resume-handling logic at restart time, the deliverable packager at archive time, and any future cross-artifact auditor reading the run's state.

Two facts constrain the option space:

1. **ADR-0005 append-only supersession** — the schema can only evolve forward; existing `checkpoint.json` files written before this ADR lands cannot be retroactively edited.
2. **MINOR scope class for this feature** — anything we do here must be two-way reversible and not require coordinated changes across multiple components or human-coordination overhead.

## Decision

Introduce `execution_mode` as a first-class documented field on `checkpoint.json` with a canonical enum of `{specialist-dispatch, parent-driven-workaround}`. The field is written by the orchestrator at dispatch time, one value per stage tracked in the checkpoint's stage record. The FR-2 dispatch self-check reads the field to identify "single-agent fallback" configurations. Existing pre-feature `checkpoint.json` files that lack the field are treated as if `execution_mode == "specialist-dispatch"` on resume.

## Decision Details

| Item | Content |
|---|---|
| Decision | `execution_mode` is a first-class documented field on the `checkpoint.json` schema, canonical enum `{specialist-dispatch, parent-driven-workaround}`, written by the orchestrator at dispatch time. |
| Why now | FR-2 needs an inspectable configuration surface. Naming the field now (as part of FR-2) is cheaper than naming it under future pressure when more downstream consumers depend on the implicit form. |
| Why this | A named enum field has single-place canonicalization (one schema definition, one writer, one predicate reader); the alternative — hook + config file + new permission entry — duplicates the failure surface. ADR-0044's flatten decision already documents `parent-driven-workaround` as the named fallback posture; this ADR canonicalizes the on-disk surface that the dispatch logic inspects. |
| Known unknowns | Whether `parent-driven-workaround` is a permanent fallback or a transitional state. ADR-0044 treats it as durable; if a future feature retires the workaround entirely, the enum becomes a single-value enum and the rename is mechanical (one schema definition, one writer, one predicate reader). |
| Kill criteria | If any future stage's dispatch posture requires a state that does not cleanly map to the two-value enum (e.g., partial-fan-out, conditional-fallback, per-layer-override), this ADR's enum is too narrow and should be superseded with a richer schema (per ADR-0005 append-only). |

## Rationale

The decision honors three rationale-brief commitments:

1. **ADR-0044 (flatten dispatch hierarchy)** — already documents `parent-driven-workaround` as the named fallback. This ADR is a faithful on-disk realization of that prior decision, not a re-litigation.
2. **ADR-0005 (append-only supersession)** — handled by the absence-equals-specialist-dispatch backward-compatibility rule. Existing `checkpoint.json` files are not rewritten; new runs write the field; resumed runs that predate the field default to the safe value (the project's already-default behavior).
3. **MINOR scope class** — the change is two-way reversible (a future ADR can supersede it with a richer schema), local in blast radius (one writer, one predicate reader, one schema definition), and individually verifiable (the FR-2 self-check is the test of the field's correctness).

The single-source-of-truth principle from KB-cc-design Principle 5 applies: one canonical field name, one canonical enum, one writer, one reader. Naming the field once now beats letting downstream consumers discover the implicit form and copy the discovery into their own logic.

The alternative interpretations evaluated and rejected:

- **Hook-based check on dispatch entry** — adds a second failure path (hook misconfigured, hook silently skipped) and a second read site that would need to stay in sync with the orchestrator-internal logic. Cost: two sources of truth.
- **New gate script** — adds new file surface and a new permission entry for a configuration surface that has one value (today). Premature factoring per the synthesis's framing.
- **Leave the field implicit; encode `parent-driven-workaround` detection in orchestrator logic only** — the FR-2 predicate would have to enumerate the implicit behavioral conditions (which stages "look like" they're using the workaround), which is exactly the kind of stringly-typed logic that drifts silently as new stages are added. The field's existence as a named enum is what makes the check stable across future stage additions.

## Options Considered

### Option 1: Hook-based check with implicit field (rejected)

Implement the FR-2 check as a Claude Code `SessionStart` or `PreToolUse` hook that inspects the orchestrator's existing implicit dispatch state.

**Pros:** No schema change. Hook is reversible (remove the hook to revert).

**Cons:** Two failure paths (orchestrator logic + hook logic) that must stay in sync. Hook adds a second `scope_class` read site. Hook silently skipped if misconfigured. Cost-of-future-stage-additions: every new stage requires updating the hook's implicit-state-detection logic separately from the orchestrator.

### Option 2: New gate script with config file (rejected)

Introduce a new gate script (e.g., `auditing-shared/scripts/check_dispatch_mode.py`) plus a separate config file describing per-stage dispatch posture.

**Pros:** Externalizes the configuration surface; potentially extensible to multiple fallback modes.

**Cons:** Premature factoring — the surface has one value today. New file surface, new permission entry, new invocation path. Two writers (the orchestrator and the operator who edits the config) create coordination overhead. The MINOR-scope tiebreaker rules this out.

### Option 3 (Selected): First-class `execution_mode` field on `checkpoint.json`

Promote `execution_mode` to a documented, named field on `checkpoint.json` with a canonical enum. The orchestrator writes it at dispatch time; the FR-2 self-check reads it.

**Pros:** Single source of truth. Single writer (orchestrator). Single reader (FR-2 predicate). Cleanly extends if future fallback modes are needed (add enum value, update predicate). Honors ADR-0044's existing posture. Honors ADR-0005's append-only discipline via the absence-default rule.

**Cons:** Schema-surface change (a new field is added). Existing `checkpoint.json` files lack the field — the absence-default rule resolves this but the cost is one extra line of orchestrator logic. Naming `parent-driven-workaround` as a first-class field canonicalizes a historical workaround, which entrenches it slightly more than leaving it implicit; mitigated by the kill criterion above and by the rename-is-mechanical note.

## Consequences

### Positive Consequences

- The FR-2 self-check has a single, named, inspectable configuration surface.
- The orchestrator's dispatch posture becomes auditable from the `checkpoint.json` history — a future architecture auditor can inspect run history to verify dispatch posture without re-reading the orchestrator source.
- The Plan author has one schema definition to edit, one writer to wire, one reader to wire. No coordination across multiple components.
- Backward compatibility is preserved by the absence-default rule; no migration is required for pre-feature checkpoints.

### Negative Consequences

- `checkpoint.json` schema is now slightly larger. The new field is one string per stage record (typically tens of bytes per run).
- `parent-driven-workaround` is now a first-class documented value. If the project eventually decides this workaround should never be used (i.e., the enum collapses to one value), the rename is a mechanical edit but is still a change to a documented surface.

### Neutral Consequences

- The orchestrator's existing implicit dispatch posture is unchanged in behavior — new runs write the field, but the field's value reflects what the orchestrator was already doing implicitly. No agent's invocation count, gating posture, or dispatch order changes as a side effect.

## Architecture Impact

Components that change:

1. **`.claude/skills/recipe-feature-pipeline/SKILL.md`** — gains the FR-2 dispatch self-check at orchestrator entry (after Stage 1, per Q-CC-6 refinement); writes `execution_mode` to each stage's checkpoint record at dispatch time. The `scope_class` read site is hoisted from line 350 (Stage 13 Deliverable Packaging) to immediately after Stage 1 completes. Stage 13's later consumption reads the hoisted value from the checkpoint rather than re-reading `intent-clarification.md`.
2. **`checkpoint.json` schema (project-wide)** — gains a documented `execution_mode` field per stage record. The schema's documentation lives in the `recipe-feature-pipeline/SKILL.md` body (the orchestrator owns the contract).

Layers affected (per the 9-layer taxonomy):

- **Claude Code / Project Filesystem** — primary. The orchestrator skill and the checkpoint schema both live here.

New dependencies introduced: none. The change is local to the orchestrator's existing surface.

Architectural constraints added:

- Future stages that introduce new dispatch postures MUST extend the `execution_mode` enum and update the FR-2 predicate. This is mechanical (per the rename-is-mechanical note) but is now an explicit obligation.

Architectural constraints removed: none.

## Implementation Guidance

Principled direction only (procedures live in Plan):

- The field's writer is the orchestrator at dispatch time. No other writer is permitted.
- The field's reader is (currently) the FR-2 dispatch self-check predicate. Future readers (e.g., a deliverable packager that wants to surface dispatch posture in the archive summary) are explicitly permitted; the field is read-many.
- Absence-of-field at read time MUST be treated as `specialist-dispatch`. This is the safe default and matches the project's pre-feature behavior.
- The enum is closed: any value not in `{specialist-dispatch, parent-driven-workaround}` is a schema violation that the orchestrator MUST reject at write time and the FR-2 predicate MUST fail-closed on at read time (per NFR-6).

The Plan author owns the precise edits to `recipe-feature-pipeline/SKILL.md` (the hoist, the field-write call, the self-check predicate body) and the precise documentation prose in the orchestrator's schema reference.

## Related Information

- **Related ADRs**: ADR-0044 (flatten execution dispatch hierarchy; canonical source for `parent-driven-workaround` as a named posture); ADR-0005 (append-only supersession; constrains how this ADR can be superseded).
- **Referenced specs**: `.claude/skills/recipe-feature-pipeline/SKILL.md` line 350 (current `scope_class` read site, to be hoisted); `working/feature/pipeline-quickwins-hardening-r1/blueprint-v1.md` (this ADR is referenced in the Blueprint's FR-2 design).
- **Issues / PRs**: This ADR is authored as part of `pipeline-quickwins-hardening-r1` Design Composition.
- **Related KBs**: KB-cc-design (Principle 5 single-source-of-truth; Principle 9 sub-agent reasoning configuration); KB-cc-platform (orchestrator skill contract); KB-documentation-criteria (ADR-authoring discipline).
