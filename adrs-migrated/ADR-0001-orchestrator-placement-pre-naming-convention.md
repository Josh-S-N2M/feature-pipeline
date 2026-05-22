---
id: ADR-0001
version: 2.0.0
status: Accepted
generated: 2026-05-12
generated_by: synth-designer (retroactive template migration per ADR-0014)
supersedes:
  - {id: ADR-0001, version: 1.0.0}
adrs_inherited: []
applies_to:
  - feature-pipeline
template_format: per ADR.txt v1.0 (adopted via ADR-0014)
---

# ADR-0001: Pipeline orchestrator is a Skill at the main session, not a sub-agent

## Status

Accepted — 2026-05-12 (template-migrated from v1.0.0 of the same date)

## Context

The feature-pipeline runs ~7 stages (research-plan → research → synthesis → design → critique-1 → triage → plan → tests → critique-2 → reconcile → tasks). Each stage is realized by one or more sub-agents. Where does the top-level orchestrator live?

Three options were enumerated. Claude Code's platform-level constraint that **sub-agents cannot spawn their own sub-agents** (the Agent tool must not appear in a sub-agent's tools array) is the load-bearing fact.

## Decision

The top-level orchestrator is a Skill (`feature-pipeline`, `user-invocable: true`) at the main session. It uses the Agent tool to invoke each stage's sub-agent(s) directly. There are no intermediate sub-orchestrators. All ~12 sub-agents report up to this one orchestrator.

## Decision Details

| Item | Content |
|---|---|
| Decision | Orchestrator lives as a Skill at the main session; all sub-agents are invoked directly via Agent tool from this single orchestrator. |
| Why now | This is the foundational topology decision; every downstream architectural commitment depends on the orchestrator's invocation point. Made early to anchor the rest of the design. |
| Why this | Matches Claude Code's documented Skill+Subagent pattern; respects the hard platform constraint that sub-agents cannot spawn sub-agents; one source of cross-stage state. |
| Known unknowns | Whether the orchestrator's body grows beyond manageable size as new stages are added; whether main-session context budget will eventually be the limiting factor for very long feature runs. |
| Kill criteria | Not applicable — foundational invariant. Reversal would require the platform to permit sub-agents to spawn sub-agents (a Claude Code platform change), at which point a hierarchical orchestrator design becomes viable. |

## Rationale

Claude Code documents the Skill+Subagent topology as the canonical pattern for multi-stage agentic workflows (claim C-0001). The platform also prohibits sub-agents from spawning sub-agents (claim C-0003 — Agent tool must not appear in a sub-agent's tools list). These two facts collapse the design space: any topology requiring multi-level fan-out must place the orchestrator at the main session (Skill level), not as a sub-agent.

The alternative — sub-agent orchestrators with simulated grandchild fan-out — is technically possible but violates the spec's intent and adds an indirection layer with no compensating benefit. The substrate-change alternative (Temporal, LangGraph) violates the manifest's hard constraint of no new runtime infrastructure.

## Options Considered

**Option 1: Orchestrator-as-sub-agent with simulated grandchild fan-out.**
- Pros: keeps the orchestrator inside a sub-agent's well-defined context boundary.
- Cons: violates the platform's documented sub-agent invocation pattern; adds indirection without benefit; spec intent is for orchestrators to live at the Skill level.

**Option 2: Substrate change to external workflow runtime (Temporal, LangGraph).**
- Pros: rich state-management primitives; durable execution; better observability.
- Cons: violates the manifest's hard constraint of no new runtime infrastructure; adds dependency, learning curve, and operational burden disproportionate to need.

**Option 3 (Selected): Orchestrator is a Skill at the main session, invoking sub-agents directly via Agent tool.**
- Pros: matches existing synthesis pipeline topology; no platform exceptions or substrate changes; one place owns cross-stage state.
- Cons: orchestrator skill body grows with stage count; main-session context carries inter-stage handoff metadata.

## Consequences

### Positive Consequences

- Matches the existing synthesis pipeline's topology — feature-pipeline is a straight extension, not a new pattern.
- One place owns the cross-stage state machine; debugging is centralized.
- No platform exceptions or substrate changes required.
- Sub-agents have clean, bounded responsibilities; the orchestrator's coordination logic is visible and traceable.

### Negative Consequences

- The orchestrator skill's body grows to coordinate ~12 sub-agents — risk of long SKILL.md. Mitigated by keeping invocation steps as a phase-table reference and pushing per-phase detail into sub-agents themselves.
- The main session's context carries all inter-stage handoff metadata. If the pipeline grows to many phases, the orchestrator's context budget is the limit. Mitigated by handing off via file paths (not file contents), which the existing synthesis pipeline already practices.

### Neutral Consequences

- The orchestrator's SKILL.md becomes a critical-path artifact that must be authored with care. The pipeline's own discipline (ADR-0014 for templates, ADR-0011 for canonical document skill) ultimately governs how the orchestrator skill is maintained.

## Architecture Impact

**Components that change:**
- New component: `feature-pipeline` Skill at `.claude/skills/feature-pipeline/SKILL.md`.
- New component class: sub-agents under `.claude/agents/synth-*.md`, invoked directly by the orchestrator.

**New dependencies introduced:**
- The orchestrator skill depends on Claude Code's Agent tool primitive being available.
- All downstream stage decisions inherit this topology (every ADR after this one builds on the single-orchestrator structure).

**Architectural constraints added:**
- Sub-agents MUST NOT have `Agent` in their tools list (recursion-safe). Enforced per claim C-0003.
- Cross-stage coordination MUST happen via the orchestrator; sub-agents do not directly invoke other sub-agents.
- Stage handoff MUST go through file-system artifacts plus an orchestrator-generated rationale brief (codified later in ADR-0009).

**Architectural constraints removed:**
- None (this is the foundational ADR).

## Implementation Guidance

- Use file-paths-not-contents for inter-stage handoff (the existing synthesis pipeline pattern).
- Keep the orchestrator's SKILL.md focused on stage sequencing and gate logic; push detailed per-stage knowledge into sub-agents' knowledge skills.
- Add a preflight stage that verifies all required sub-agents and skills are installed before run begins.
- Use the Skill's `user-invocable: true` so users can launch the pipeline directly via `/feature-pipeline`.

## Related Information

- Original ADR-0001 v1.0.0: preserved at `ADR-0001-orchestrator-placement-pre-template-migration.md` per ADR-0014.
- Claims grounding the decision: C-0001 (Skill+Subagent canonical pattern), C-0003 (sub-agents cannot spawn sub-agents).
- ADR-0014: retroactive template migration that produced this v2.0.0.
- ADR-0006: synthesis stages inlined into orchestrator — directly extends this ADR's "no skill-to-skill invocation" implication.
- ADR-0016: per-layer fan-out at Stage 5 — fan-out happens at the orchestrator level (Skill), not at sub-agent level.
