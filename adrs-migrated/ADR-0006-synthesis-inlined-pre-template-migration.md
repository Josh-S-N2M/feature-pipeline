# ADR-0006: Synthesis stages are inlined into the feature-pipeline orchestrator

## Status
Accepted — 2026-05-12

## Context
The original v1 blueprint specified Stage 4 as `/synthesize --from-manifest` — invoking the existing synthesize skill from inside the feature-pipeline orchestrator skill. Critique-1 issue I-0002 surfaced that this is not a documented invocation pattern: Claude Code's skill model supports skill→sub-agent invocation (via the Agent tool), but not skill→skill invocation in the way the v1 blueprint assumed.

Cross-stage supersession discipline per ADR-0005 requires that resolutions introducing new architectural changes write a new ADR rather than silently editing prior ones.

## Decision
The feature-pipeline orchestrator directly drives the 6 existing synth-* sub-agents (`synth-extractor`, `synth-grapher`, `synth-critic`, `synth-framer`, `synth-substrate`, `synth-synthesizer`) in the same sequence the existing synthesize skill uses. No `/synthesize` invocation. No skill-to-skill call.

The 6 sub-agent definitions in `.claude/agents/` are shared between two orchestrators: the existing `synthesize` skill (for standalone synthesis runs) and the new `feature-pipeline` skill (for end-to-end feature runs). Per the manifest's "no fork" interpretation (resolved via I-0003): sharing sub-agents across orchestrators is allowed; forking the sub-agent definitions would not be.

## Consequences

Positive:
- One source of truth for synthesis logic (the synth-* sub-agent definitions themselves).
- No new platform mechanism required.
- The existing `synthesize` skill continues to work unchanged for standalone synthesis users.
- The feature-pipeline gains synthesis capability without depending on an undocumented invocation pattern.

Negative:
- The feature-pipeline orchestrator's body grows: it must know how to drive 6 stages of synthesis in addition to its 11 own stages. The orchestrator skill becomes longer.
- Two orchestrators driving the same sub-agents creates a discipline burden: changes to sub-agent contracts must consider both callers. Mitigated by treating the sub-agent contracts as a stable API and documenting the contracts in `*-knowledge` skills.
- The "extends without forking" constraint is interpreted to allow sub-agent sharing across orchestrators. A stricter interpretation might forbid this; we adopt the looser one and document it explicitly.

## Alternatives considered

- **Option A: v1's `/synthesize --from-manifest`.** Rejected because skill-to-skill invocation is not documented in Claude Code; would require an undocumented or unsupported mechanism.
- **Option B: Inline only the orchestrator's logic, fork the sub-agents.** Rejected because this violates the manifest's "no fork" hard constraint and creates two divergent maintenance burdens.
- **Option C: Make synthesize a sub-agent.** Rejected because the synthesis pipeline itself fans out into 6 sub-agents; making the orchestrator a sub-agent would require sub-agents to spawn sub-agents (violates C-0003 platform constraint).
- **Substrate change: Run synthesis externally and import results.** Rejected because the manifest forbids new runtime infrastructure.

Inlining (this ADR's decision) is the only option that satisfies all constraints.

## Cross-stage supersession marker

`cross_stage_supersession: false` — this ADR is introduced at Stage 10 (Reconcile after Critique-1 triage) of the feature-pipeline-design run, but it does not supersede any synthesis-stage ADR. It supplements D-0005 (which framed the reuse question but did not specify the inlining mechanism).

## Evidence

Backed by claims:
- C-0003: sub-agents cannot spawn sub-agents (verified) — rules out Option C
- C-0001: Skill+Subagent is the canonical pattern (verified) — supports the chosen inlining approach
- C-0032: $ARGUMENTS / $1 mechanism (verified) — would have supported Option A IF skill-to-skill invocation were documented, but it is not

Critique-1 finding I-0002 (severity: major) is the trigger for this ADR. Triage approved.

## Substrate registry version
v1.0 (2026-05-12)
