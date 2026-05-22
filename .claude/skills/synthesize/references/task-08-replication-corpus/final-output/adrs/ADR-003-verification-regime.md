# ADR-003: Verification regime — vertical-slice early verification gate

**Status:** Accepted
**Date:** 2026-05-01
**Deciders:** synthesis-pipeline run `task-08-replication-20260501-021500`

## Context

A pipeline like this can fail in two ways: at the *interface* level (one phase produces output the next phase can't consume) or at the *substrate* level (the substrate's primitive set can't realize a load-bearing pattern). Per-phase tests catch interface failures; only end-to-end runs against real corpora catch substrate failures.

The corpus's two source documents converge on an early-verification-point discipline: define what to verify and how *before* scaling [technical-designer.md](/mnt/user-data/uploads/technical-designer.md), and for replacements or modifications, the early verification point must be an output comparison of at least one representative case [technical-designer.md](/mnt/user-data/uploads/technical-designer.md). The synthesis-pipeline-technical-design source applies this concretely as the §7.4 vertical-slice gate, with six falsifiable success criteria on a 2-document corpus.

This decision is the **strongest cross-source signal in the corpus** (E-0012 Verification Strategy is the cluster bridge between the design-discipline cluster and the pipeline-architecture cluster).

## Decision Drivers

- Substrate-level mismatches must be caught before scaling (cost of late detection is full design rework)
- Verification must be falsifiable, not asserted — the output comparison method is the binding mechanism [technical-designer.md](/mnt/user-data/uploads/technical-designer.md)
- Reference artifacts must be capturable to enable smoke-run regression testing on later runs [technical-designer.md](/mnt/user-data/uploads/technical-designer.md)
- LLM non-determinism makes bit-exact replay impossible — the regime must accept ±10% tolerance per Design §7.2

## Considered Options

- **Option 1: Native** — Vertical-slice early gate (orchestrator + Extractor + claim-extraction-knowledge run end-to-end on a 2-document corpus). Effort: 2 weeks. Loss: replay_determinism (bit-exact replay impossible; tolerance-based matching).
- **Option 2: Adapter** — Phase-by-phase incremental verification (each phase agent ships with integration tests against synthetic upstream artifacts; no end-to-end gate). Effort: 8 weeks. **Non-viable** — per-phase isolation cannot reveal substrate-level integration failures, exactly the failure mode this regime is designed to catch.
- **Option 3: Substrate change** — Use a framework with built-in verification hooks (LangGraph state-validation, Temporal deterministic replay). Effort: 16 weeks.

## Decision Outcome

Chosen option: **Native (vertical-slice early verification gate)**.

### Positive Consequences

- Both source documents recommend this path — strongest cross-source corroboration in the corpus
- Falsifiable acceptance: the §7.4 success criteria are concrete (manifest validates, per-source files produced, schema conforms, source URIs gated, spot-check passes, reference captured)
- Reference artifacts captured per criterion 6 enable Layer C smoke-run regression checks on every later run via [smoke-run-diff.sh](/mnt/user-data/uploads/synthesis-pipeline-technical-design.md)
- Cheap to fail: the gate runs on a 2-document corpus, not the full production input set

### Negative Consequences

- ±10% tolerance is the substitute for bit-exact replay — drifts within tolerance can mask real regressions; investigators must inspect changes that approach the tolerance edge
- Reference corpus selection matters: a poorly-chosen reference (one where claims don't partially overlap, per the §7.4 corpus-shape requirement) reduces the gate's discriminating power
- The gate can pass and the substrate can still later fail on a more demanding corpus — the gate is necessary but not sufficient

## Validation

This very run is the gate's first execution. Phase 1 + Phase 2 results: Layer A passes on every artifact; six §7.4 success criteria all met; three reachable §7.1 invariants pass; smoke-run-diff against captured reference passes. **Verdict: PASS.**

If a future run against a different corpus fails the gate, the substrate-level invariants in the design need re-examination, not the gate's mechanism.

## Provenance

- Decision frame: `D-0003` (in `04-decision-frames.json`)
- Claims supporting: `C-0045`, `C-0046`, `C-0047`, `C-0053`
- Substrate registry version: `2026-04-30.1`
- Synthesis run: `task-08-replication-20260501-021500`
