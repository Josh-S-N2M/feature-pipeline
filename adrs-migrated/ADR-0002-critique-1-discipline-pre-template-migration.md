# ADR-0002: Critique-1 uses single-critic CoVe; asymmetric debate is reserved for Critique-2

## Status
Accepted — 2026-05-12

## Context
After the blueprint is drafted, a critic reviews it in clean context. The original spec called for "multi-turn blast-radius analysis to ensure there are no hidden changes." The literature offers a spectrum: simple checklist critique → CoVe (chain-of-verification, single critic) → asymmetric debate (context-deprived critic vs context-aware defender + judge) → cross-model critic.

The choice for Critique-1 trades off rigor against LLM-call cost and latency. Critique-1's output feeds a human triage gate. Critique-2 (later in the pipeline) is the stronger gate.

## Decision
Critique-1 uses **single-critic CoVe**: one synth-critic-1 sub-agent runs CoVe-style verification on each blueprint decision, augmented by a code-graph MCP for blast-radius queries (ADR-0004) and a checklist of issue types (correctness, missing decisions, contradictions with synthesis, blast-radius gaps).

Critique-2 (ADR-0003) uses the stronger discipline: Cross-Model Critic + diff-mode + convergence-termination.

This is the **only decision in the pipeline that lands on `adapter` rather than `native`** in the three-option enumeration. The `native` option (asymmetric debate at Critique-1) costs ~3× the LLM calls and adds latency without proportional value at a stage whose output flows through a human triage gate anyway.

## Consequences

Positive:
- ~3x cheaper than native for Critique-1.
- Human triage gate after Critique-1 catches anything the simpler critique missed; the asymmetric-debate value adds at this stage are partially redundant with the human review.
- Critique-2 retains the stronger discipline where it matters most (post-plan, pre-execution).

Negative:
- Single-critic CoVe is empirically weaker than asymmetric debate at the same stage. Risk: an issue silently passes Critique-1 and survives until Critique-2.
- Mitigation: the synth-critic-1 sub-agent's checklist must be comprehensive; the human triage gate is a real backstop.

## Alternatives considered

- **Native (asymmetric debate at Critique-1)**: viable, higher cost, marginal value gain.
- **Substrate change (external review service)**: violates hard constraint.

## Evidence

Backed by C-0018 (SR-DCR asymmetric debate, single-sourced), C-0019 (Cross-Model Critic real-world evidence), C-0020 (convergence-based termination).

Dissent surfaced: C-0018's 2x prior-bias reduction is single-sourced and benchmark-specific. The choice to use the stronger discipline at Critique-2 but not Critique-1 is partly informed by this — we invest the strong-evidence pattern where stakes are highest.

## Substrate registry version
v1.0 (2026-05-12)
