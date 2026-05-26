---
name: feedback-cadence-split-reshape
description: When a user-direction reshape splits one FR into per-cadence sub-mechanisms (e.g., per-rebuild static-shape vs periodic behavioral), use sub-letter FR numbering (FR-4a/4b/4c), keep the parent count stable in carve-out summaries, and propagate to NFRs/policy/risks/diagnostics consistently.
metadata:
  type: feedback
---

When the user reshapes an FR by splitting it into sub-mechanisms distinguished by cadence (per-rebuild vs periodic, sync vs async, blocking vs observable), the structural pattern that preserves traceability is:

1. **Use sub-letter FR numbering (FR-4a, FR-4b, FR-4c) — not new FR-N IDs.** Renumbering would imply scope-class growth and break references in downstream artifacts (Plan, Tests, ADRs, Phase Validators). Sub-letters keep the "this run ships five mechanisms" carve-out summary stable while exposing internal structure.

2. **Each sub-mechanism gets its own AC family (AC-FR-Xa-a, AC-FR-Xa-b, ...), in EARS format, with the cadence assumption in the trigger clause.** Per-rebuild ACs use `When <postCreate runs>`; periodic ACs use `When <cron triggers>` or `When <PR modifies <pin file>>`; opt-in ones use `When <maintainer invokes ...>`. The cadence is the AC's first identifier.

3. **Cross-cutting policy goes in the Product Policy Decisions table as a single row, not duplicated across ACs.** The row names the cadence split as a policy commitment (e.g., "per-rebuild and behavioral not collapsed") with the rationale (cost budget) and the affected layers (now multi-layer).

4. **NFR knock-ons usually hit three places:**
   - The per-rebuild performance NFR tightens (the static-shape check is cheaper than the full mechanism was).
   - The CI workflow NFR widens to cover the new behavioral workflow alongside the prior smoke workflow.
   - Any event-surface / observability NFR acknowledges the new event type the behavioral mechanism emits, and flags it as an additive-extension question for the canonical event-surface ADR.

5. **Undetermined Items: resolve the prior unified-mechanism U-item by structural argument, not by silently deleting it.** Mark as `[x] RESOLVED in v<N> by the split:` and explain how each prong of the prior U-item now lands in a specific AC of the new sub-mechanisms. This preserves audit trail.

6. **Risks table grows.** The split introduces new failure modes the unified version did not have: per-rebuild passes while behavioral is failing (deliberate; not a bug; but document); behavioral check observability dependency on the event surface; trigger-set coverage of every path that can change the pinned state.

7. **Deliverable inventory expands.** A split FR ships more files (a script + a workflow + an ADR amendment) than the unified version. State this explicitly in Rollout Plan so design-composer and plan-author can plan the artifacts.

**Why:** the v0.3.0 revision of `pipeline-quickwins-hardening-r1` was driven by exactly this pattern — user pointed out that conflating per-rebuild (static-shape) with periodic (behavioral) was costing budget for no signal, and the maintainer-only-script trap requires CI wiring and event observability. The structural moves above preserved the carve-out posture (still "five mechanisms") while honoring the cadence-split insight.

**How to apply:** when a user reshape direction names "different cadence" or "different question" as the rationale for splitting an FR, do not collapse the two into a single mechanism. Use sub-letter FR numbering, give each cadence its own AC family in EARS, route the cross-cutting policy through Product Policy Decisions, and propagate to NFR/Risks/Deliverables consistently. Related: [[feedback-constraint-tension-preservation]].
