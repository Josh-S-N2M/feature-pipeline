---
id: ADR-0005
version: 2.1.0
status: Accepted
generated: 2026-05-19
generated_by: finalize-reconciler (v4.3.0 naming-convention retroactive update per ADR-0019)
supersedes:
  - {id: ADR-0005, version: 1.0.0}
adrs_inherited:
  - ADR-0001 (orchestrator placement)
applies_to:
  - feature-pipeline
template_format: per ADR.txt v1.0
---

# ADR-0005: Pipeline artifacts are append-only with bidirectional supersession links

## Status

Accepted — 2026-05-12 (template-migrated from v1.0.0 of the same date)

## Context

The user explicitly required that "the resolution needs to be aware of the synthesis → prior blueprint changes from first critique and current blueprint → sequential phased build plan with validation hierarchy that also accounts for any issues of the first critique to prevent that context from being lost." This is the cross-stage context-loss problem.

The literature converges on a single discipline: append-only artifacts with bidirectional supersession links. Architecture Decision Records (ADRs) are immutable once accepted; if the decision changes, a new ADR is written that supersedes the old one. OpenSpec's spec-driven-with-adr schema (April 2026) explicitly addresses the case where design rationale lives in archived change artifacts and becomes invisible to future proposals — exactly our concern.

## Decision

Every artifact this pipeline produces is **immutable once written**. The resolution loops (triage after Critique-1; reconcile after Critique-2) do not edit upstream artifacts. They produce *new artifacts* with explicit `supersedes` metadata.

Specific shape:
- Every pipeline artifact carries frontmatter with `id`, `version` (semver), `supersedes: [{id, version}]` (array, may be empty), and `superseded_by: [{id, version}]` (back-populated when later artifacts supersede).
- A `traceability.json` index in the run dir maps `requirement_id ↔ adr_id ↔ implementation_artifact_id` bidirectionally.
- A `finalize-reconciler` sub-agent (invoked in the resolution loop) walks the full supersession chain when producing reconciled artifacts. Its job is explicitly to ensure prior decisions are not silently dropped: each new version's frontmatter must enumerate which prior decisions it carries forward (or explicitly supersedes with rationale).

## Decision Details

| Item | Content |
|---|---|
| Decision | All pipeline artifacts are append-only and immutable once written. Resolution loops produce NEW versions with explicit `supersedes` metadata; never edit upstream artifacts in place. |
| Why now | This is a foundational invariant; every downstream ADR depends on stable artifact IDs being available for supersession links and diff-mode (ADR-0003). |
| Why this | Cross-stage context loss is structurally impossible when every artifact links back to its predecessors; literature convergence on this pattern (ADR discipline + OpenSpec spec-driven-with-adr); auditable provenance for every final decision. |
| Known unknowns | Whether run directory grows excessively over many iterations (many superseded versions accumulate); whether reading full chain at reconcile time becomes a context-budget problem. Mitigations exist (file-system-as-state is cheap; diff-mode from ADR-0003 reads diffs not full chains) but practical limits not yet measured. |
| Kill criteria | Not applicable — foundational invariant. Reversal requires redesigning the entire pipeline's state model. |

## Rationale

The user's explicit requirement on context preservation is load-bearing — the resolution loops MUST be aware of prior context. Append-only with bidirectional supersession links is the cleanest design that makes context-loss structurally impossible rather than merely discouraged.

Literature convergence: claim C-0014 documents ADR immutability and bidirectional supersession as established practice across multiple sources. Claim C-0015 documents OpenSpec's spec-driven-with-adr (April 2026, within cutoff) addressing this exact problem.

The alternative — mutable artifacts with diff history — is cheaper in file count but relies on a working diff tool and discipline. Diffs require the diff tool to be working correctly; immutable+linked artifacts make context-loss visibly impossible.

## Options Considered

**Option 1: Mutable artifacts with diff history.** Edit artifacts in place; rely on git history for prior versions.
- Pros: fewer file objects in run dir; git is the canonical source of truth for history.
- Cons: loses the structural-impossibility-of-context-loss property; depends on the diff tool being correctly used; requires every reader to know to consult git history; doesn't compose with non-git-aware tooling.

**Option 2: Substrate change — external traceability tool (e.g., Git-history walker, Datasette).**
- Pros: rich query capability; structured queries.
- Cons: adds complexity contrary to manifest's no-new-runtime-infrastructure constraint; one more failure point.

**Option 3 (Selected): Append-only with bidirectional supersession links + traceability index.**
- Pros: structural impossibility of context loss; every artifact links back to predecessors; auditable; composes with file-system-as-state.
- Cons: more file objects; frontmatter discipline burden; reading the full chain consumes context budget (mitigated by ADR-0003's diff-mode).

## Consequences

### Positive Consequences

- Cross-stage context loss is structurally impossible: every artifact links back to its predecessors.
- Auditable: a reviewer can trace any final task back to the synthesis claim that justified it.
- Reconcile is a real check, not an unstructured re-prompt.
- Diff-mode in Critique-2 (ADR-0003) is enabled by stable IDs.
- Issue ledger persistence (ADR-0008) inherits this discipline for issue-state preservation across runs.

### Negative Consequences

- More file objects in the run dir (potentially several versions of the blueprint, plan, etc.). Mitigated by file-system-as-state being cheap.
- Frontmatter discipline burden on every sub-agent. Mitigated by `KB-documentation-criteria` skill (per ADR-0011) loaded by every sub-agent enforcing the convention.
- Reading the full chain at reconcile time consumes context budget. Mitigated by Critique-2's diff-mode (ADR-0003): the critic reads the diff between versions, not all versions.

### Neutral Consequences

- The pipeline's many ADRs (currently 18 at v4) all benefit from this discipline — each ADR has a stable ID and version that subsequent supersessions reference.

## Architecture Impact

**Components that change:**
- Every sub-agent that produces an artifact: must use the frontmatter discipline (`id`, `version`, `supersedes`, `superseded_by`).
- New artifact: `traceability.json` per run, maintained by orchestrator.
- New sub-agent: `finalize-reconciler` — walks supersession chain when producing reconciled artifacts.
- Knowledge skill: `KB-documentation-criteria` (per ADR-0011, canonical document skill) — teaches the frontmatter convention.

**New dependencies introduced:**
- Every downstream sub-agent depends on the frontmatter discipline being enforced; failure to honor it causes cross-stage context loss.

**Architectural constraints added:**
- All pipeline artifacts MUST carry the supersession frontmatter (`id`, `version`, `supersedes`, `superseded_by`).
- Pipeline artifacts MUST NOT be edited in place once written. Resolution loops produce new versions.
- `traceability.json` MUST be maintained per run by the orchestrator.
- finalize-reconciler MUST enumerate carried-forward decisions in each new version's frontmatter.

**Architectural constraints removed:**
- Implicit "edit in place when refining" behavior is forbidden.

## Implementation Guidance

- Frontmatter format: YAML at top of each markdown artifact; required fields `id`, `version`, `supersedes`, optional `superseded_by` (back-populated).
- Supersession ID format: `{id: ADR-0007, version: 2.0.0}` — both id and version required to disambiguate.
- traceability.json shape: per-feature index mapping requirement_id ↔ ADR ids ↔ blueprint section ids ↔ task ids.
- finalize-reconciler invocation: orchestrator passes existing chain + new evidence; agent produces new version with explicit "decisions carried forward" enumeration.

## Related Information

- Original ADR-0005 v1.0.0: preserved at `ADR-0005-append-only-supersession-pre-template-migration.md` per ADR-0014.
- ADR-0003: diff-mode for Critique-2 — depends on stable IDs from this ADR.
- ADR-0008: issue ledger — extends this supersession discipline to issue state.
- ADR-0011: KB-documentation-criteria canonical document skill — teaches the frontmatter convention.
- ADR-0014: retroactive template migration — this very file is an example of supersession discipline (v2.0.0 supersedes v1.0.0).
- Claims: C-0014 (ADR immutability with bidirectional supersession), C-0015 (OpenSpec spec-driven-with-adr).

## v4.3.0 retroactive naming-convention update

Per ADR-0019, all sub-agent, knowledge skill, and orchestrator skill references in this ADR have been updated to the v4.3.0 naming convention (phase-prefixed sub-agents, KB-prefixed knowledge skills, recipe-prefixed orchestrator, shared-prefixed cross-phase sub-agents). The pre-update version is preserved at `ADR-0005-append-only-supersession-pre-naming-convention.md`. The decision recorded in this ADR is unchanged; only entity names are updated for cross-document consistency.
