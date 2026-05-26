# ADR-002: Memory architecture — two-tier (orchestrator + per-sub-agent)

**Status:** Accepted (with surfaced uncertainty)
**Date:** 2026-05-01
**Deciders:** synthesis-pipeline run `task-08-replication-20260501-021500`

## Context

Sub-agents in Claude Code run in isolated contexts and have no native auto-loaded memory file [synthesis-pipeline-technical-design.md](/mnt/user-data/uploads/synthesis-pipeline-technical-design.md). The pipeline must decide how (or whether) to preserve per-agent learnings across runs. The corpus proposes a two-tier convention: substrate-native `MEMORY.md` for the orchestrator, and a file-system convention at `.memories/agents/<name>/` for per-sub-agent memory [synthesis-pipeline-technical-design.md](/mnt/user-data/uploads/synthesis-pipeline-technical-design.md).

This is the corpus's **single most consequential single-sourced claim** — flagged 🔶 "Engineering proposal — no precedent" in the source. It must be surfaced as such, not smoothed over.

## Decision Drivers

- Preserve runtime observations across runs (otherwise every run re-discovers vendor-specific patterns)
- Keep curated taxonomies (knowledge skills) separate from accumulated learnings (sub-agent memories) [synthesis-pipeline-technical-design.md](/mnt/user-data/uploads/synthesis-pipeline-technical-design.md)
- Minimize substrate-level proposals that have no precedent (this one does — accept the risk explicitly)
- Allow reversibility — if the convention proves unmaintainable, the fallback (single-tier) must remain straightforward to adopt

## Considered Options

- **Option 1: Native** — Two-tier (orchestrator MEMORY.md + per-sub-agent file-system convention). Effort: 1 week. Loss: pattern_fidelity (convention requires agent discipline rather than substrate enforcement).
- **Option 2: Adapter** — Single-tier MEMORY.md only; orchestrator slices and passes per-agent memory at task start. Effort: 0.5 weeks. Loss: pattern_fidelity (orchestrator's context grows O(num_agents × memory_size); degrades at scale).
- **Option 3: Substrate change** — Switch to a framework with native multi-tier memory (e.g., LangGraph TypedDict per-node fields). Effort: 16 weeks. Loss: none.

## Decision Outcome

Chosen option: **Native (two-tier engineering proposal)**.

This decision is two-way reversible — the convention can be revised in place without breaking the pipeline's external interface. If accumulated experience reveals the per-sub-agent memory files become unmaintainable, single-tier is a one-week migration.

### Positive Consequences

- Knowledge skills carry curated content; sub-agent memories accumulate runtime observations — clean separation per the routing rule [synthesis-pipeline-technical-design.md](/mnt/user-data/uploads/synthesis-pipeline-technical-design.md)
- Authoring order is well-defined: knowledge skills first, agent definitions second, sub-agent memories accumulate organically without pre-population [synthesis-pipeline-technical-design.md](/mnt/user-data/uploads/synthesis-pipeline-technical-design.md)
- Per-agent memory READMEs encode the read protocol locally with each agent

### Negative Consequences

- **Engineering proposal — no substrate-validated precedent.** Source flagged this 🔶. The convention's correctness depends on agent discipline rather than substrate enforcement.
- Single-sourced claim — RICE confidence calibrated to 0.5 (vendor-only-equivalent provenance, since the source is the team itself)
- Sub-agent memory files may accumulate stale entries without periodic pruning discipline (the 'do not pre-populate' rule mitigates initial bloat, but ongoing curation is on the maintainer)

## Validation

The convention is validated by the next 2-3 real synthesis runs producing observably-useful sub-agent memory entries (and observably-useless ones being prunable without breaking runs). If after 3 runs the per-agent memory files are either empty or full of noise, this decision is wrong — fall back to single-tier (Option 2).

## Provenance

- Decision frame: `D-0002` (in `04-decision-frames.json`)
- Claims supporting: `C-0020`, `C-0021` (single_sourced + medium confidence), `C-0022`, `C-0023`, `C-0024`
- Substrate registry version: `2026-04-30.1`
- Synthesis run: `task-08-replication-20260501-021500`
- **Uncertainty flag:** This decision rests on a single-sourced claim flagged 🔶 in source. Surfaced in [Limitations](../report.md#limitations) of the main report.
