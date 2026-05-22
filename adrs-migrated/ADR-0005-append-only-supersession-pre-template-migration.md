# ADR-0005: Pipeline artifacts are append-only with bidirectional supersession links

## Status
Accepted — 2026-05-12

## Context
The user explicitly required that "the resolution needs to be aware of the synthesis → prior blueprint changes from first critique and current blueprint → sequential phased build plan with validation hierarchy that also accounts for any issues of the first critique to prevent that context from being lost." This is the cross-stage context-loss problem.

The literature converges on a single discipline: append-only artifacts with bidirectional supersession links. Architecture Decision Records (ADRs) are immutable once accepted; if the decision changes, a new ADR is written that supersedes the old one. OpenSpec's spec-driven-with-adr schema (April 2026) explicitly addresses the case where design rationale lives in archived change artifacts and becomes invisible to future proposals — exactly our concern.

## Decision
Every artifact this pipeline produces is **immutable once written**. The resolution loops (triage after Critique-1; reconcile after Critique-2) do not edit upstream artifacts. They produce *new artifacts* with explicit `supersedes` metadata.

Specific shape:
- Every pipeline artifact carries frontmatter with `id`, `version` (semver), `supersedes: [{id, version}]` (array, may be empty), and `superseded_by: [{id, version}]` (back-populated when later artifacts supersede).
- A `traceability.json` index in the run dir maps `requirement_id ↔ adr_id ↔ implementation_artifact_id` bidirectionally.
- A `synth-reconcile` sub-agent (invoked in the resolution loop) walks the full supersession chain when producing reconciled artifacts. Its job is explicitly to ensure prior decisions are not silently dropped: each new version's frontmatter must enumerate which prior decisions it carries forward (or explicitly supersedes with rationale).

## Consequences

Positive:
- Cross-stage context loss is structurally impossible: every artifact links back to its predecessors.
- Auditable: a reviewer can trace any final task back to the synthesis claim that justified it.
- Reconcile is a real check, not an unstructured re-prompt.

Negative:
- More file objects in the run dir (potentially several versions of the blueprint, plan, etc.). Mitigated by file-system-as-state being cheap.
- Frontmatter discipline burden on every sub-agent. Mitigated by `document-conventions-knowledge` skill loaded by every sub-agent enforcing the convention.
- Reading the full chain at reconcile time consumes context budget. Mitigated by Critique-2's diff-mode (ADR-0003): the critic reads the diff between versions, not all versions.

## Alternatives considered

- **Adapter (mutable with diff history)**: viable, cheaper, loses the structural-impossibility-of-context-loss property. Diffs require the diff tool to be working correctly; immutable+linked artifacts make context-loss visibly impossible.
- **Substrate change (external traceability tool like a Git-history walker)**: viable but adds complexity contrary to hard constraint.

## Evidence

Backed by C-0014 (ADR immutability with bidirectional supersession — verified, multi-source convergence), C-0015 (OpenSpec spec-driven-with-adr addressing this exact problem — verified, within cutoff April 2026).

## Substrate registry version
v1.0 (2026-05-12)
