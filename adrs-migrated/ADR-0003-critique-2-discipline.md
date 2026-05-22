---
id: ADR-0003
version: 2.1.0
status: Accepted
generated: 2026-05-19
generated_by: finalize-reconciler (v4.3.0 naming-convention retroactive update per ADR-0019)
supersedes:
  - {id: ADR-0003, version: 1.0.0}
adrs_inherited:
  - ADR-0001 (orchestrator placement)
  - ADR-0002 (critique-1 single-critic CoVe)
applies_to:
  - feature-pipeline
template_format: per ADR.txt v1.0
notes_post_v4: Critic was renamed to review-cross-artifact-auditor per ADR-0017; this ADR continues to describe the CMC + diff-mode + convergence discipline that the renamed agent implements.
---

# ADR-0003: Critique-2 uses Cross-Model Critic with diff-mode input and convergence-based termination

## Status

Accepted — 2026-05-12 (template-migrated from v1.0.0 of the same date)

## Context

Critique-2 is the final automated gate before human approval of the build plan. Its job: review the plan + acceptance tests + phase validators against the blueprint, surface issues, and prevent silent loss of decisions made in earlier stages. Inputs are potentially large (synthesis + critique-1 + blueprint + plan + tests).

The proposed pipeline's original critique called for "any issues are fed back to be resolved" with awareness of "synthesis → prior blueprint changes from first critique and current blueprint → sequential phased build plan with validation hierarchy that also accounts for any issues of the first critique to prevent that context from being lost."

## Decision

Critique-2 uses three composed techniques:

1. **Diff-mode input.** The critic does not see the full upstream context. It sees: blueprint diff (v1 → v2), critique-1 issues with their resolution status, plan.json, acceptance-tests.md, phase-validator entries. Full synthesis report is referenced by ID; available on demand via Read but not pre-loaded.

2. **Cross-Model Critic (CMC).** If the main agent is Sonnet, the `synth-critic-2` sub-agent (renamed `review-cross-artifact-auditor` per ADR-0017) declares `model: opus` in its frontmatter. Different model family catches correlated training-data errors that same-family review misses. Real-world evidence: ~3% of false-positives caught by CMC that survived same-family review (Refute-or-Promote, CVE-2026-34183 case).

3. **Convergence-based termination.** If the resolution loop iterates (Critique-2 → Reconcile → Critique-2 again), measure issues-list similarity. Terminate when round-N similarity vs round-(N-1) exceeds 0.9 (no new issues being introduced). Hard cap at 3 resolution rounds regardless.

## Decision Details

| Item | Content |
|---|---|
| Decision | Critique-2 = CMC (cross-model) + diff-mode input + convergence-based termination + hard 3-round cap. |
| Why now | Critique-2 is the last automated gate; choosing its discipline before plan and test sub-agents are built ensures their outputs are designed for this critique's inputs (diff-mode requires stable supersession IDs upstream). |
| Why this | Diff-mode bounds context; CMC catches orthogonal errors same-family critique misses; convergence termination + hard cap prevents infinite loops; production CMC evidence (CVE-2026-34183) validates the orthogonal-error-detection property. |
| Known unknowns | Whether convergence threshold (0.9 similarity) is right — too tight terminates prematurely, too loose runs longer than valuable; whether the hard cap (3 rounds) is right — may need adjustment per feature complexity. |
| Kill criteria | If 3+ runs hit the hard 3-round cap with substantive unresolved issues (rather than nit-picking), the convergence mechanism is insufficient and the cap-cycle gate should escalate to human review earlier (e.g., after round 2). |

## Rationale

Three findings ground each composed technique:

(1) **Diff-mode input** addresses context budget. Per claim C-R2-0027, multi-agent token duplication runs 53-86% across handoffs; Critique-2 at full-context would carry the brunt of that overhead. Diff-mode reduces input to changes-only while still allowing full-context Read on demand.

(2) **Cross-Model Critic** has real-world evidence (claim C-0019): ~3% of false-positives caught by CMC that survived same-family review (Refute-or-Promote, CVE-2026-34183 case). Different model families have differently-correlated errors; orthogonal error detection is a structural property of the architecture.

(3) **Convergence-based termination** (claim C-0020) prevents the iteration-loop pathology: critiques can find nits indefinitely if no termination is enforced. Similarity-based termination + hard cap ensures bounded effort.

The dissent: claim C-0018 (SR-DCR 2× bias reduction) is single-sourced; the CMC pattern here does not depend on that magnitude, only on the directional finding that cross-model adds orthogonal coverage. The CVE case (claim C-0019) is concrete enough to anchor the choice.

## Options Considered

**Option 1: Same-model critic, full-context input.**
- Pros: simpler; one model family throughout the pipeline; no Opus pricing premium.
- Cons: loses orthogonal-error-detection property; correlated training-data errors slip through; full context blows budget.

**Option 2: Substrate change — external multi-model debate framework.**
- Pros: rich orchestration of multiple model families; specialized debate protocols.
- Cons: violates manifest's no-new-runtime-infrastructure constraint.

**Option 3 (Selected): CMC + diff-mode + convergence-based termination + hard cap.**
- Pros: context-bounded; orthogonal error detection; bounded iteration; uses platform's existing model-override mechanism.
- Cons: higher LLM cost per invocation (Opus > Sonnet); diff-mode requires upstream supersession discipline; if user environment is Opus-locked, CMC degenerates to same-model.

## Consequences

### Positive Consequences

- Context-bounded: Critique-2 operates on diffs, not full artifacts; input fits even for large features.
- Orthogonal error detection: CMC catches what same-family critics miss.
- Bounded iteration: convergence-termination + hard cap prevents infinite loops.
- Aligns with Critique-1's lighter discipline (ADR-0002): rigor scales with stage stakes.

### Negative Consequences

- Higher LLM cost per Critique-2 invocation (Opus > Sonnet pricing).
- Diff-mode requires upstream artifacts to maintain stable IDs and supersession links — adds discipline burden upstream (codified in ADR-0005).
- If the user's environment is Opus-locked, the cross-model property degenerates to same-model; the diff-mode + convergence value remains but the CMC value is lost.

### Neutral Consequences

- The renaming to review-cross-artifact-auditor (per ADR-0017) does not change this discipline; the renamed agent still implements CMC + diff-mode + convergence.

## Architecture Impact

**Components that change:**
- Sub-agent: `synth-critic-2` (later renamed `review-cross-artifact-auditor` per ADR-0017) — implements CMC + diff-mode + convergence.
- Knowledge skill: `critique-2-knowledge` (later renamed `KB-review-disciplines`) — teaches the discipline.
- Stage 9 iteration loop: depends on convergence-similarity measurement and hard cap enforcement.

**New dependencies introduced:**
- The pipeline depends on a different model family being available for the cross-model property. Typically `model: opus` in the sub-agent's frontmatter overrides the main agent's model. If only one model family is available, CMC degenerates gracefully (but the property is lost).
- Diff-mode depends on upstream artifacts maintaining stable supersession links (codified in ADR-0005).

**Architectural constraints added:**
- Critique-2 sub-agent MUST declare `model: opus` (or another cross-family override) in its frontmatter when the main agent is Sonnet.
- The resolution loop MUST measure issues-list similarity round-N vs round-(N-1) and terminate at >0.9 similarity or hard cap of 3 rounds.
- Upstream artifacts MUST carry stable IDs to enable diff-mode (this is reinforced by ADR-0005).

**Architectural constraints removed:**
- None.

## Implementation Guidance

- Diff-mode mechanism: orchestrator computes the diff between blueprint v(N) and v(N-1) at handoff time; passes the diff plus critique-1 issues + plan + tests to Critique-2's invocation.
- CMC mechanism: declare `model: opus` (or appropriate cross-family override) in the sub-agent's YAML frontmatter.
- Convergence measurement: cosine similarity between issues-list vectors (embedding each issue's `origin.evidence` field).
- Hard cap: 3 rounds. If hit with substantive unresolved issues, escalate to Cycle-Cap Escalation Gate.

## Related Information

- Original ADR-0003 v1.0.0: preserved at `ADR-0003-critique-2-discipline-pre-template-migration.md` per ADR-0014.
- ADR-0002: Critique-1 uses the lighter discipline (single-critic CoVe).
- ADR-0005: Append-only supersession provides the stable IDs that diff-mode requires.
- ADR-0017: rename of synth-critic-2 to review-cross-artifact-auditor.
- Claims: C-0019 (CMC real-world evidence — CVE-2026-34183), C-0020 (convergence-based termination), C-0014 (ADR immutability), C-0015 (OpenSpec spec-driven-with-adr).

## v4.3.0 retroactive naming-convention update

Per ADR-0019, all sub-agent, knowledge skill, and orchestrator skill references in this ADR have been updated to the v4.3.0 naming convention (phase-prefixed sub-agents, KB-prefixed knowledge skills, recipe-prefixed orchestrator, shared-prefixed cross-phase sub-agents). The pre-update version is preserved at `ADR-0003-critique-2-discipline-pre-naming-convention.md`. The decision recorded in this ADR is unchanged; only entity names are updated for cross-document consistency.
