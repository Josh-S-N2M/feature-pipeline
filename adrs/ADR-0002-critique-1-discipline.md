---
id: ADR-0002
version: 2.1.0
status: Accepted
generated: 2026-05-19
generated_by: finalize-reconciler (v4.3.0 naming-convention retroactive update per ADR-0019)
supersedes:
  - {id: ADR-0002, version: 1.0.0}
adrs_inherited:
  - ADR-0001 (orchestrator placement)
applies_to:
  - feature-pipeline
template_format: per ADR.txt v1.0
notes_post_v4: Critic was renamed to review-architecture-auditor per ADR-0017; this ADR continues to describe the CoVe discipline that the renamed agent implements.
---

# ADR-0002: Critique-1 uses single-critic CoVe; asymmetric debate is reserved for Critique-2

## Status

Accepted — 2026-05-12 (template-migrated from v1.0.0 of the same date)

## Context

After the blueprint is drafted, a critic reviews it in clean context. The original spec called for "multi-turn blast-radius analysis to ensure there are no hidden changes." The literature offers a spectrum: simple checklist critique → CoVe (chain-of-verification, single critic) → asymmetric debate (context-deprived critic vs context-aware defender + judge) → cross-model critic.

The choice for Critique-1 trades off rigor against LLM-call cost and latency. Critique-1's output feeds a human triage gate. Critique-2 (later in the pipeline) is the stronger gate.

## Decision

Critique-1 uses **single-critic CoVe**: one `synth-critic-1` sub-agent (renamed to `review-architecture-auditor` per ADR-0017) runs CoVe-style verification on each blueprint decision, augmented by a code-graph MCP for blast-radius queries and a checklist of issue types (correctness, missing decisions, contradictions with synthesis, blast-radius gaps).

Critique-2 (ADR-0003) uses the stronger discipline: Cross-Model Critic + diff-mode + convergence-termination.

## Decision Details

| Item | Content |
|---|---|
| Decision | Critique-1 = single-critic CoVe + code-graph blast-radius queries + structured checklist. NOT asymmetric debate (reserved for Critique-2). |
| Why now | Critique discipline choice cascades into critique-1-knowledge skill content, the synth-critic-1 sub-agent definition, and the iteration loop budget. Made before knowledge skills authored. |
| Why this | Critique-1 output flows through a human triage gate; partial automated rigor + human review is more cost-effective than full automated rigor + human review; asymmetric debate (~3× cost) reserved where stakes are highest (Critique-2, no human triage between it and Build Approval). |
| Known unknowns | Whether single-critic CoVe will catch enough issues to keep human triage tractable; whether the eventual blast-radius integration (GitNexus per ADR-0007) compensates for CoVe's weaker rigor relative to asymmetric debate. |
| Kill criteria | If 3+ consecutive runs surface critical issues at Critique-2 that single-critic CoVe at Critique-1 demonstrably missed (e.g., the missed issue is in the blueprint at Stage 5 but not flagged by Critique-1), promote Critique-1 to asymmetric debate. |

## Rationale

The literature names asymmetric debate (SR-DCR, claim C-0018) as ~2× more effective at reducing prior-bias than single-critic patterns. The cost is also ~3×. The decision is whether the ~2× rigor improvement justifies the ~3× cost at Critique-1 specifically.

Two factors tip the balance toward single-critic CoVe at Critique-1:

(1) **The human triage gate is a real backstop.** Issues that survive single-critic CoVe land in front of a human reviewer before any downstream work proceeds. The asymmetric-debate value at this stage is partially redundant with human review.

(2) **The strong discipline lives downstream where it matters more.** Critique-2 has no human gate between it and Build Approval (the final gate before execution). That's where asymmetric-debate's stronger error-detection should be invested.

The dissent: claim C-0018's 2× prior-bias reduction is single-sourced and benchmark-specific. This informs the choice — we invest the strong-evidence pattern where stakes are highest.

## Options Considered

**Option 1: Asymmetric debate at Critique-1 (the "native" rigor choice).** Same discipline as Critique-2.
- Pros: maximum automated rigor; catches more issues before human review.
- Cons: ~3× LLM call cost; latency cost; partially redundant with human triage gate.

**Option 2: Substrate change — external review service (e.g., hosted review-as-a-service).**
- Pros: outsource the rigor question.
- Cons: violates manifest's no-new-runtime-infrastructure constraint; introduces network dependency.

**Option 3 (Selected): Single-critic CoVe + code-graph MCP + structured checklist.**
- Pros: ~3× cheaper than asymmetric debate; aligns rigor investment with stage stakes; human triage gate is the safety net.
- Cons: empirically weaker than asymmetric debate at the same stage; risk an issue silently passes Critique-1 and survives until Critique-2.

## Consequences

### Positive Consequences

- ~3× cheaper than asymmetric debate for Critique-1.
- Human triage gate after Critique-1 catches anything the simpler discipline missed; partial redundancy with human review is intentional.
- Critique-2 retains the stronger discipline where stakes are highest (post-plan, pre-execution).
- Sets up a defensible pattern: rigor scales with stake.

### Negative Consequences

- Single-critic CoVe is empirically weaker than asymmetric debate at the same stage. Risk: an issue silently passes Critique-1 and survives until Critique-2.
- Mitigation requires the synth-critic-1 (now review-architecture-auditor) sub-agent's checklist to be comprehensive; the human triage gate is a real backstop.
- The kill criterion (3+ runs surfacing missed issues at Critique-2) is the practical signal to revisit; until that signal fires, this decision holds.

### Neutral Consequences

- The renaming of synth-critic-1 → review-architecture-auditor (per ADR-0017) does not change this discipline; the renamed agent still implements single-critic CoVe.

## Architecture Impact

**Components that change:**
- Sub-agent: `synth-critic-1` (later renamed `review-architecture-auditor` per ADR-0017) — implements CoVe discipline.
- Knowledge skill: `critique-1-knowledge` (later renamed `KB-review-disciplines`) — teaches the checklist and CoVe procedure.

**New dependencies introduced:**
- Critique-1 depends on a code-graph MCP for blast-radius queries (specified later in ADR-0007 v2).

**Architectural constraints added:**
- Critique-1 MUST use single-critic CoVe; asymmetric-debate at Critique-1 forbidden by this ADR.
- Critique-1's checklist MUST cover: correctness, missing decisions, contradictions with synthesis, blast-radius gaps.

**Architectural constraints removed:**
- None.

## Implementation Guidance

- CoVe procedure: critic generates a list of verification questions about each blueprint decision; answers each independently; flags decisions where verification answers contradict the blueprint.
- Blast-radius queries via the code-graph MCP (GitNexus primary, codebase-memory-mcp fallback per ADR-0007 v2).
- Checklist content lives in `critique-1-knowledge` (renamed `KB-review-disciplines` per ADR-0017).
- Output JSON includes: per-issue severity, category, evidence, and proposed resolution direction.

## Related Information

- Original ADR-0002 v1.0.0: preserved at `ADR-0002-critique-1-discipline-pre-template-migration.md` per ADR-0014.
- ADR-0003: Critique-2 uses the stronger discipline (asymmetric debate + CMC + diff-mode).
- ADR-0007 v2.0.0: code-graph MCP selection — Critique-1's blast-radius queries use these MCPs.
- ADR-0017: rename of synth-critic-1 to review-architecture-auditor (does not change discipline).
- Claims: C-0018 (asymmetric debate effectiveness), C-0019 (Cross-Model Critic real-world evidence), C-0020 (convergence-based termination).

## v4.3.0 retroactive naming-convention update

Per ADR-0019, all sub-agent, knowledge skill, and orchestrator skill references in this ADR have been updated to the v4.3.0 naming convention (phase-prefixed sub-agents, KB-prefixed knowledge skills, recipe-prefixed orchestrator, shared-prefixed cross-phase sub-agents). The pre-update version is preserved at `ADR-0002-critique-1-discipline-pre-naming-convention.md`. The decision recorded in this ADR is unchanged; only entity names are updated for cross-document consistency.
