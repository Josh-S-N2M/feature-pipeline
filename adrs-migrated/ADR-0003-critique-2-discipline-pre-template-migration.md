# ADR-0003: Critique-2 uses Cross-Model Critic with diff-mode input and convergence-based termination

## Status
Accepted — 2026-05-12

## Context
Critique-2 is the final automated gate before human approval of the build plan. Its job: review the plan + acceptance tests + phase validators against the blueprint, surface issues, and prevent silent loss of decisions made in earlier stages. Inputs are potentially large (synthesis + critique-1 + blueprint + plan + tests).

The proposed pipeline's original critique called for "any issues are fed back to be resolved" with awareness of "synthesis → prior blueprint changes from first critique and current blueprint → sequential phased build plan with validation hierarchy that also accounts for any issues of the first critique to prevent that context from being lost."

## Decision
Critique-2 uses three composed techniques:

1. **Diff-mode input.** The critic does not see the full upstream context. It sees: blueprint diff (v1 → v2), critique-1 issues with their resolution status, plan.json, acceptance-tests.md, phase-validator entries. Full synthesis report is referenced by ID; available on demand via Read but not pre-loaded.

2. **Cross-Model Critic (CMC).** If the main agent is Sonnet, the synth-critic-2 sub-agent declares `model: opus` in its frontmatter. Different model family catches correlated training-data errors that same-family review misses. Real-world evidence: ~3% of false-positives caught by CMC that survived same-family review (Refute-or-Promote, CVE-2026-34183 case).

3. **Convergence-based termination.** If the resolution loop iterates (Critique-2 → Reconcile → Critique-2 again), measure issues-list similarity. Terminate when round-N similarity vs round-(N-1) exceeds 0.9 (no new issues being introduced). Hard cap at 3 resolution rounds regardless.

## Consequences

Positive:
- Context-bounded: Critique-2 operates on diffs, not full artifacts; the input fits even for large features.
- Orthogonal error detection: CMC catches what same-family critics miss.
- Bounded iteration: convergence-termination + hard cap prevents infinite loops.

Negative:
- Higher LLM cost per Critique-2 invocation (Opus > Sonnet pricing).
- Diff-mode requires upstream artifacts to maintain stable IDs and supersession links — adds discipline burden upstream.
- If the user's environment is Opus-locked, the cross-model property degenerates to same-model; the diff-mode + convergence value remains but the CMC value is lost.

## Alternatives considered

- **Adapter (same-model critic, full-context input)**: viable, simpler, loses the orthogonal-error-detection property.
- **Substrate change (external multi-model debate framework)**: violates hard constraint.

## Evidence

Backed by C-0019 (Cross-Model Critic with real CVE evidence — verified), C-0020 (convergence-based termination — verified), C-0014 (ADR immutability — verified, supports diff-mode), C-0015 (OpenSpec spec-driven-with-adr — verified).

C-0018 (SR-DCR 2x bias reduction) was single-sourced; the CMC pattern here does not depend on that magnitude, only on the directional finding that cross-model adds orthogonal coverage.

## Substrate registry version
v1.0 (2026-05-12)
