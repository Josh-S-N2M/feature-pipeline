# ADR-004: Recursion safety — hard rule with defense-in-depth

**Status:** Accepted
**Date:** 2026-05-01
**Deciders:** synthesis-pipeline run `task-08-replication-20260501-021500`

## Context

The pipeline reads `output/**/*.md` as its primary input source and writes to `output/synthesis-<topic>/`. Without a rigid exclusion mechanism, every re-run of `/synthesize` would ingest its own prior output, treating yesterday's synthesis report as input to today's run. This is unrecoverable corruption: by the time it's noticed, the claim corpus has degraded across multiple generations.

The corpus is unambiguous on the rule [synthesis-pipeline-technical-design.md](/mnt/user-data/uploads/synthesis-pipeline-technical-design.md): the input scan is `output/**/*.md` minus `output/synthesis-*/**` as a hard rule. The namespace prefix `synthesis-` is reserved.

## Decision Drivers

- The failure mode (silent corpus pollution via re-ingestion) is irreversible by the time it's noticed
- Deterministic file-ops (Glob with exclusion, prefix string check) are cheap — both substrate primitives are direct
- Defense-in-depth at two layers (orchestrator + per-agent secondary check) doubles the cost of one cheap check, yielding meaningfully better robustness against future code paths forgetting the convention

## Considered Options

- **Option 1: Native** — Hard rule with defense-in-depth (orchestrator's input glob excludes `output/synthesis-*/**` AND each sub-agent's body re-checks `output/synthesis-*/` prefix on source paths before extracting). Effort: 0.5 weeks. Loss: none.
- **Option 2: Adapter** — Soft rule via naming convention only (prefix `synthesis-` documented but not enforced; rely on agents to follow). Effort: 0 weeks. **Non-viable** — the failure mode is silent and irreversible.
- **Option 3: Substrate change** — n/a — recursion safety is an architectural concern within Claude Code's file-system model and does not require substrate change.

## Decision Outcome

Chosen option: **Native (hard rule with defense-in-depth)**.

### Positive Consequences

- Orchestrator-level Glob exclusion catches the most common case (input discovery)
- Per-agent secondary check catches code paths that don't go through the orchestrator's discovery (e.g., a future operator-supplied source path)
- Both checks are cheap deterministic file-ops; the cost is negligible
- Verifiable: Invariant 7 of §7.1 (recursion safety) is checked by [invariant-7-recursion.sh](/mnt/user-data/uploads/synthesis-pipeline-technical-design.md) on every run

### Negative Consequences

- Two-place enforcement means two places to maintain; if the convention changes (e.g., a different namespace prefix), both must update
- Defense-in-depth has no measurable upside in the common case where the orchestrator's glob is correct — the value is in the failure mode it prevents

## Validation

Invariant 7 (recursion safety) script execution on this run's output: PASS (no `01-claims*.json` `source_uri` matches `output/synthesis-*/`). The check would also execute on every future run via the in-skill validator and (when probe-confirmed) the `PostToolUse` hook.

## Provenance

- Decision frame: `D-0004` (in `04-decision-frames.json`)
- Claims supporting: `C-0007`, `C-0019`
- Substrate registry version: `2026-04-30.1`
- Synthesis run: `task-08-replication-20260501-021500`
