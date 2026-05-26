# ADR-001: Substrate choice — Claude Code primitives only

**Status:** Accepted
**Date:** 2026-05-01
**Deciders:** synthesis-pipeline run `task-08-replication-20260501-021500`

## Context

The pipeline must run somewhere. The corpus explicitly names three out-of-scope alternatives — LangGraph, Temporal, AWS Step Functions — and grounds every architectural element in Claude Code primitives [synthesis-pipeline-technical-design.md](/mnt/user-data/uploads/synthesis-pipeline-technical-design.md). This decision sets the boundary for every downstream design choice.

The corpus is unusual in that it pre-justifies the decision. This ADR exists to make the rationale explicit and to record the alternatives so a future revisitation has the full picture.

## Decision Drivers

- Minimize tenant-specific dependencies that aren't already in scope
- Acknowledge known losses (cycle declaration, deterministic replay) as design boundaries rather than gaps
- Keep implementation cost proportionate to a single-pipeline use case
- Preserve traceability — every primitive used must map to an entry in the substrate registry

## Considered Options

- **Option 1: Native** — Claude Code primitives only (orchestrator skill, sub-agents via Task tool, file-system-as-state, hooks for QA, AskUserQuestion for the gate). Effort: 4 weeks. Loss: pattern_fidelity, cycle_declaration, replay_determinism.
- **Option 2: Adapter** — Hybrid Python wrapper invoking Claude API directly while preserving Claude Code primitives where possible. Effort: 12 weeks. **Non-viable** — bypasses native primitives (MEMORY.md, .memories/, hooks, AskUserQuestion); net cost greater than both alternatives.
- **Option 3: Substrate change** — Adopt LangGraph, Temporal, or AWS Step Functions; keep Claude as the LLM. Effort: 16 weeks. Recovers cycle declaration, typed state, deterministic replay.

## Decision Outcome

Chosen option: **Native (Claude Code primitives only)**.

### Positive Consequences

- Direct realization — every needed primitive is present per the substrate registry [substrate-registry.md](/mnt/user-data/uploads/synthesis-pipeline-technical-design.md)
- Lowest implementation cost (4 weeks vs. 12 or 16)
- Full access to substrate-native conveniences: `MEMORY.md`, `.memories/`, `AskUserQuestion`, `Task` tool with `subagent_type`
- Acknowledged losses are explicitly documented as out-of-scope in the corpus [synthesis-pipeline-technical-design.md](/mnt/user-data/uploads/synthesis-pipeline-technical-design.md) — not silent

### Negative Consequences

- Substrate-level pattern fidelity is partial: framework-level supervisor abstractions are simulated rather than declared (e.g., bounded retry via orchestrator counter rather than declared cycle)
- Deterministic replay is not achievable — Critic's Layer C smoke runs use ±10% tolerance per Design §7.2 instead of bit-exact match
- Tenant-specific dependencies: if Claude Code's primitive set changes materially, the registry's 90-day staleness gate will trigger refresh

## Validation

If the §7.4 vertical-slice gate (this run) fails its six success criteria, this decision is wrong and we return to design [synthesis-pipeline-technical-design.md](/mnt/user-data/uploads/synthesis-pipeline-technical-design.md). The gate's verdict on Phase 1 + Phase 2 of this corpus is **PASS**, so the substrate-level invariants the design depends on hold.

## Provenance

- Decision frame: `D-0001` (in `04-decision-frames.json`)
- Claims supporting: `C-0001`, `C-0002`, `C-0003`
- Substrate registry version: `2026-04-30.1`
- Synthesis run: `task-08-replication-20260501-021500`
