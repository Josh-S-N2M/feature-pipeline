# ADR-005: User confirmation — required AskUserQuestion gate

**Status:** Accepted
**Date:** 2026-05-01
**Deciders:** synthesis-pipeline run `task-08-replication-20260501-021500`

## Context

Three concurrent inputs need user confirmation before the pipeline runs: the input set (which discovered files to use), the target substrate (which substrate registry to load), and any hard constraints (compliance, vendor-locked, budget). Without explicit confirmation, the pipeline either uses defaults that may not match user intent, or fails partway when the constraints aren't honored.

The corpus mandates an `AskUserQuestion` gate as a required interrupt before Phase 1, with three concurrent questions on a single card [synthesis-pipeline-technical-design.md](/mnt/user-data/uploads/synthesis-pipeline-technical-design.md). Cancellation is dismissal-with-empty-answers; the orchestrator acknowledges and exits cleanly without allocating a run-id [synthesis-pipeline-technical-design.md](/mnt/user-data/uploads/synthesis-pipeline-technical-design.md). This shapes the pipeline's contract with the user.

## Decision Drivers

- User intent must be confirmed before allocating run-id and writing the manifest (manifest is read-only thereafter per invariant 3 of §7.1)
- Cancellation semantics must be explicit — empty answers should not silently default to "proceed"
- Substrate registry selection depends on `target_substrate` answer — wrong default could load the wrong registry and produce nonsense substrate mappings
- Hard constraints affect viability flags in the Substrate phase — wrong default could miss compliance violations

## Considered Options

- **Option 1: Native** — Required `AskUserQuestion` gate with three concurrent questions on a single card. Cancellation is dismissal-with-empty-answers, no run-id allocated. Effort: 0.5 weeks. Loss: none.
- **Option 2: Adapter** — Configuration file read at orchestrator start with prompt-on-missing for unspecified fields. Effort: 1 week. Loss: pattern_fidelity (UX ambiguity around cancellation — does an empty config file mean cancel, or use defaults?).
- **Option 3: Substrate change** — n/a — confirmation gates are application-level, not substrate-level.

## Decision Outcome

Chosen option: **Native (required AskUserQuestion gate)**.

### Positive Consequences

- Substrate-direct: `AskUserQuestion` is a documented Claude Code primitive [substrate-registry.md](/mnt/user-data/uploads/synthesis-pipeline-technical-design.md)
- Cancellation semantics are unambiguous (corpus-defined): empty answers = exit without allocating run-id
- User sees all three constraint dimensions on one card — cognitive load is bounded
- Manifest is written only AFTER the gate, ensuring the read-only invariant 3 holds from the moment the manifest exists

### Negative Consequences

- Scripted invocation needs a bypass mechanism (out of scope for this design — the corpus does not address it; future work)
- Three concurrent questions on a single card may be a UX mismatch for very simple cases (e.g., user invoking with all defaults); the gate runs even when the answers would all be defaults

## Validation

A scripted invocation should fail with a clear error indicating the gate cannot be bypassed in this version. A real interactive invocation should produce a card with exactly three questions in the order: input set, target substrate, hard constraints. Cancellation (empty answers) should produce no `working/synthesis/<run-id>/` directory. These are gate verifications that would be exercised on every real run.

## Provenance

- Decision frame: `D-0005` (in `04-decision-frames.json`)
- Claims supporting: `C-0008`, `C-0009`
- Substrate registry version: `2026-04-30.1`
- Synthesis run: `task-08-replication-20260501-021500`
