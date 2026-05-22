# ADR-0001: Pipeline orchestrator is a Skill at the main session, not a sub-agent

## Status
Accepted — 2026-05-12

## Context
The feature-pipeline runs ~7 stages (research-plan → research → synthesis → design → critique-1 → triage → plan → tests → critique-2 → reconcile → tasks). Each stage is realized by one or more sub-agents. Where does the top-level orchestrator live?

Three options were enumerated. Claude Code's platform-level constraint that **sub-agents cannot spawn their own sub-agents** (the Agent tool must not appear in a sub-agent's tools array) is the load-bearing fact.

## Decision
The top-level orchestrator is a Skill (`feature-pipeline`, `user-invocable: true`) at the main session. It uses the Agent tool to invoke each stage's sub-agent(s) directly. There are no intermediate sub-orchestrators. All ~12 sub-agents report up to this one orchestrator.

## Consequences

Positive:
- Matches the existing synthesis pipeline's topology, so the feature-pipeline is a straight extension of the same pattern, not a new pattern.
- One place owns the cross-stage state machine; debugging is centralized.
- No platform exceptions or substrate changes required.

Negative:
- The orchestrator skill's body grows to coordinate ~12 sub-agents — risk of long SKILL.md. Mitigated by keeping invocation steps as a phase-table reference and pushing per-phase detail into the sub-agents themselves.
- The main session's context carries all the inter-stage handoff metadata. If the pipeline grows to many phases, the orchestrator's context budget is the limit. Mitigated by handing off via file paths (not file contents), which the existing synthesis pipeline already practices.

## Alternatives considered

- **Orchestrator-as-sub-agent with simulated grandchild fan-out**: viable but violates spec intent and adds a layer of indirection. Cost-loss profile is dominated by `native`.
- **Substrate change to Temporal/LangGraph**: viable but violates the manifest's hard constraint of no new runtime infrastructure.

## Evidence

Backed by claims: C-0001 (Skill+Subagent is canonical pattern), C-0003 (sub-agents cannot spawn sub-agents).

Both verified.

## Substrate registry version
v1.0 (2026-05-12)
