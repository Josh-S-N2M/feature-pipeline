---
name: feedback-kill-criterion-as-fr-not-section
description: Kill criteria that change scope-class mid-run must be authored as Functional Requirements with EARS ACs, not as a Rollout-Plan-only narrative
metadata:
  type: feedback
---

When an IC ratifies a kill-criterion that causes a mid-run termination (e.g., "pause-and-rescope into a follow-on feature rather than silent scope-shrink"), do NOT relegate it to the Rollout Plan section as narrative. Instead:

1. Author a dedicated FR (e.g., FR-2 in `execute-orchestrator-dispatch-mechanism-repair-r1` PRD) capturing the kill-criterion's *activation behavior*.
2. Give it EARS-format ACs covering: (a) the detection condition (`If <finding>, then …`), (b) the halt-at-next-gate behavior (`If <posture-marker>, then the system shall not advance to …`), (c) the artifact-emission requirement.
3. Cross-reference the kill-criterion FR from the Rollout Plan section (which then becomes a one-line "per FR-N" pointer rather than redundant narrative).

**Why:** Kill-criteria that change scope-class downstream affect every artifact's expected shape (per-layer design count, ADR count, plan phase count). They are testable behaviors of the pipeline itself, not aspirational milestones. The Plan author and the architecture-auditor need them as FRs with stable IDs to write phase-cycle behavior and cross-artifact consistency checks against.

**How to apply:** Whenever an IC's clarifying-questions table includes "scope-class activation behavior" or "kill criterion activation," produce an FR for each distinct activation branch. The Rollout Plan section's "Kill criteria" subsection becomes a pointer to those FRs, not a duplicate narrative.

Related: [[feedback-constraint-tension-preservation]] (load-bearing tensions also get FR ACs, not just constraint-section prose).
