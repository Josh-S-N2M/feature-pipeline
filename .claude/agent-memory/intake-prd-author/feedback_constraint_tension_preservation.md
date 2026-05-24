---
name: feedback-constraint-tension-preservation
description: When the IC explicitly preserves a tension between two constraints (rather than picking one), the PRD must record both as constraints to be resolved at downstream Design — not pre-decide the tension via PRD prose
metadata:
  type: feedback
---

When an Intent Clarification ratifies an answer of the form "defer to per-layer Design — open item" with both sides of a tension named (e.g., workaround-acceptability vs. specialist-isolation invariants in `execute-orchestrator-dispatch-mechanism-repair-r1`), the PRD must:

1. Record BOTH constraints in the Constraints section explicitly (as Constraint A and Constraint B, not as one-line bullets).
2. Add a Product Policy Decision row that *names the deferral as the policy* and points to the resolving downstream stage (per-layer cc Design in this case).
3. Add an AC that requires the downstream stage's rationale to explicitly weigh both constraints (e.g., AC-FR-N-a referencing "the rationale tying the choice to (i) the investigation finding, (ii) the specialist-isolation invariants enumerated in the Constraints section").

**Why:** The default PRD-author instinct is to either pick one side ("specialist-isolation is required, workaround is unacceptable") or to omit the tension entirely. Both undermine the IC's explicit preservation. The orchestrator's dispatch prompt for `execute-orchestrator-dispatch-mechanism-repair-r1` called this out as the "Workaround vs. specialist-isolation tension (IC Q5 ratified)" special discipline; the same pattern recurs whenever an IC leaves a load-bearing tension for downstream resolution.

**How to apply:** Whenever an IC table row contains "Defer to … — open item" with two named constraints, treat it as a discipline trigger. Mirror the constraints into the PRD's Constraints section, the Product Policy Decisions table, and an AC that audits the downstream rationale.

Related: [[feedback-kill-criterion-as-fr-not-section]] (kill criteria are FRs/NFRs with EARS ACs, not a Rollout-Plan-only narrative).
