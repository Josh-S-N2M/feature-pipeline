---
id: ADR-0006
version: 2.1.0
status: Accepted
generated: 2026-05-19
generated_by: finalize-reconciler (v4.3.0 naming-convention retroactive update per ADR-0019)
supersedes:
  - {id: ADR-0006, version: 1.0.0}
adrs_inherited:
  - ADR-0001 (orchestrator placement)
  - ADR-0005 (append-only supersession)
applies_to:
  - feature-pipeline
template_format: per ADR.txt v1.0
---

# ADR-0006: Synthesis stages are inlined into the feature-pipeline orchestrator

## Status

Accepted — 2026-05-12 (template-migrated from v1.0.0 of the same date)

## Context

The original v1 blueprint specified Stage 4 as `/synthesize --from-manifest` — invoking the existing synthesize skill from inside the feature-pipeline orchestrator skill. Critique-1 issue I-0002 surfaced that this is not a documented invocation pattern: Claude Code's skill model supports skill→sub-agent invocation (via the Agent tool), but not skill→skill invocation in the way the v1 blueprint assumed.

Cross-stage supersession discipline per ADR-0005 requires that resolutions introducing new architectural changes write a new ADR rather than silently editing prior ones.

## Decision

The feature-pipeline orchestrator directly drives the 6 existing synth-* sub-agents (`synthesis-claim-extractor`, `synthesis-entity-grapher`, `synthesis-internal-critic`, `synthesis-decision-framer`, `synthesis-substrate-mapper`, `synthesis-report-author`) in the same sequence the existing synthesize skill uses. No `/synthesize` invocation. No skill-to-skill call.

The 6 sub-agent definitions in `.claude/agents/` are shared between two orchestrators: the existing `synthesize` skill (for standalone synthesis runs) and the new `recipe-feature-pipeline` skill (for end-to-end feature runs). Per the manifest's "no fork" interpretation: sharing sub-agents across orchestrators is allowed; forking the sub-agent definitions would not be.

## Decision Details

| Item | Content |
|---|---|
| Decision | Synthesis stages inlined: feature-pipeline orchestrator drives the 6 existing synth-* sub-agents directly in sequence. No `/synthesize` invocation. Sub-agent definitions shared with the standalone synthesize skill. |
| Why now | Stage 4 mechanism must be resolved before downstream stages can be designed; the v1 spec's skill-to-skill invocation pattern is not platform-supported. |
| Why this | Skill-to-skill invocation is not documented in Claude Code (load-bearing fact); inlining preserves the manifest's "no fork" constraint while making the feature-pipeline self-contained; sub-agent sharing across two orchestrators is the lower-cost interpretation of "extend without forking." |
| Known unknowns | Whether the feature-pipeline orchestrator's body grows beyond manageable size as it absorbs all 6 synthesis stages plus its own 11 stages; whether the two orchestrators driving the same sub-agents will diverge in expectations over time. |
| Kill criteria | If sub-agent contracts diverge (e.g., synthesize-pipeline-only requirements added to a synth-* agent that break feature-pipeline usage), the sub-agents must be forked OR Claude Code adds skill-to-skill invocation. The kill criterion: 3+ instances of feature-pipeline-breaking changes to shared synth-* sub-agents within a 90-day period. |

## Rationale

The load-bearing fact: skill-to-skill invocation (the v1 blueprint's `/synthesize --from-manifest` mechanism) is not a documented Claude Code pattern (claim C-0001 documents Skill+Subagent as canonical; claim C-0003 documents the platform constraint that sub-agents cannot spawn sub-agents, but neither documents skill→skill). Without platform support, the v1 mechanism is not implementable.

The three viable alternatives:

(1) **Inline the synth-* sub-agent invocations into the feature-pipeline orchestrator's body** — this ADR's decision.
(2) **Fork the sub-agents** — violates manifest's "no fork" hard constraint.
(3) **Make synthesize a sub-agent** — would require sub-agents to spawn sub-agents, violating C-0003.

Inlining is the only option that satisfies all constraints. The interpretation of "extends without forking" to allow sub-agent sharing across orchestrators is the looser of two readings; the stricter reading (forbid sub-agent sharing) would make inlining infeasible too. The looser reading is adopted explicitly.

## Options Considered

**Option 1: v1's `/synthesize --from-manifest` (skill-to-skill invocation).** 
- Pros: cleanest separation of concerns; synthesize logic stays in one place.
- Cons: rejected because skill-to-skill invocation is not documented in Claude Code; would require an undocumented or unsupported mechanism.

**Option 2: Inline only the orchestrator's logic, fork the sub-agents.**
- Pros: each pipeline has independent sub-agent definitions; no cross-pipeline coupling.
- Cons: rejected because this violates the manifest's "no fork" hard constraint and creates two divergent maintenance burdens.

**Option 3: Make synthesize a sub-agent.**
- Pros: would compose cleanly as a single sub-agent call from feature-pipeline orchestrator.
- Cons: rejected because the synthesis pipeline itself fans out into 6 sub-agents; making the orchestrator a sub-agent would require sub-agents to spawn sub-agents (violates C-0003 platform constraint).

**Option 4: Substrate change — run synthesis externally and import results.**
- Pros: complete separation; no in-process coupling.
- Cons: rejected because the manifest forbids new runtime infrastructure.

**Option 5 (Selected): Inline synth-* sub-agent invocations into the feature-pipeline orchestrator, with sub-agent definitions shared.**
- Pros: only option satisfying all constraints; one source of truth for synthesis logic (the sub-agent definitions); no platform exceptions required.
- Cons: orchestrator skill body grows; two orchestrators driving the same sub-agents creates a discipline burden (contract stability).

## Consequences

### Positive Consequences

- One source of truth for synthesis logic (the synth-* sub-agent definitions themselves).
- No new platform mechanism required.
- The existing `synthesize` skill continues to work unchanged for standalone synthesis users.
- The feature-pipeline gains synthesis capability without depending on an undocumented invocation pattern.

### Negative Consequences

- The feature-pipeline orchestrator's body grows: it must know how to drive 6 stages of synthesis in addition to its 11 own stages. The orchestrator skill becomes longer.
- Two orchestrators driving the same sub-agents creates a discipline burden: changes to sub-agent contracts must consider both callers. Mitigated by treating the sub-agent contracts as a stable API and documenting the contracts in `*-knowledge` skills.
- The "extends without forking" constraint is interpreted to allow sub-agent sharing across orchestrators. A stricter interpretation might forbid this; we adopt the looser one and document it explicitly.

### Neutral Consequences

- This ADR was originally introduced at Stage 10 (Reconcile after Critique-1 triage) of the feature-pipeline-design run as a response to issue I-0002. Original `cross_stage_supersession: false` — supplemented D-0005 (which framed the reuse question but did not specify the inlining mechanism).

## Architecture Impact

**Components that change:**
- `feature-pipeline` orchestrator skill: absorbs the 6 synthesis-stage invocation sequence in addition to its 11 own stages.
- The 6 existing synth-* sub-agents: no changes to their definitions; they are now invoked by two orchestrators (synthesize skill + feature-pipeline skill).
- Pipeline stage inventory: Stage 4 of feature-pipeline is the inline synthesis sequence (6 sub-stages).

**New dependencies introduced:**
- feature-pipeline depends on the 6 synth-* sub-agents being installed. Stage 0 preflight verifies presence.
- A shared-contract discipline: any change to a synth-* sub-agent must consider both callers (synthesize skill + feature-pipeline skill).

**Architectural constraints added:**
- The feature-pipeline orchestrator MUST invoke synth-* sub-agents directly in sequence, not via `/synthesize` or skill-to-skill mechanism.
- Sub-agent definitions for synth-* MUST remain compatible with BOTH orchestrators (no forking).

**Architectural constraints removed:**
- The v1 mechanism (`/synthesize --from-manifest`) is no longer permitted.

## Implementation Guidance

- Sequence: `synthesis-claim-extractor` → `synthesis-entity-grapher` → `synthesis-internal-critic` → `synthesis-decision-framer` → `synthesis-substrate-mapper` → `synthesis-report-author`. Same order as standalone synthesize skill.
- Each sub-agent reads from its assigned working directory and writes to the next; orchestrator manages the file paths.
- When updating a synth-* sub-agent for one orchestrator, run regression tests against the other.

## Related Information

- Original ADR-0006 v1.0.0: preserved at `ADR-0006-synthesis-inlined-pre-template-migration.md` per ADR-0014.
- ADR-0001: orchestrator placement — establishes that there is one orchestrator (the feature-pipeline Skill); this ADR specifies what it does at Stage 4.
- ADR-0005: append-only supersession — applies to the synthesis-stage outputs as it does to all pipeline outputs.
- Claims: C-0001 (Skill+Subagent canonical pattern), C-0003 (sub-agents cannot spawn sub-agents), C-0032 ($ARGUMENTS / $1 mechanism — would have supported Option 1 IF skill-to-skill were documented).
- Critique-1 finding I-0002 (severity: major) is the original trigger for this ADR. Triage approved.

## v4.3.0 retroactive naming-convention update

Per ADR-0019, all sub-agent, knowledge skill, and orchestrator skill references in this ADR have been updated to the v4.3.0 naming convention (phase-prefixed sub-agents, KB-prefixed knowledge skills, recipe-prefixed orchestrator, shared-prefixed cross-phase sub-agents). The pre-update version is preserved at `ADR-0006-synthesis-inlined-pre-naming-convention.md`. The decision recorded in this ADR is unchanged; only entity names are updated for cross-document consistency.
