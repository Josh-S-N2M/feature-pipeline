---
id: ADR-0043
version: 1.0.0
status: Accepted
generated: 2026-05-23
generated_by: design-composer
supersedes: []
adrs_inherited: [ADR-0042]
applies_to:
  - devcontainer-mcp-provisioning-r1
  - the augmented `auditing-mcp` skill (10 rule families OP-1..OP-10)
  - the feature-pipeline orchestrator's Gate 6 (Deliverable Packaging)
  - any future pipeline run that invokes `auditing-mcp`
template_format: per KB-documentation-criteria ADR template v1.0
change_summary: >-
  Codifies the Gate-4 user override making `auditing-mcp` a **hard gate**
  at orchestrator Gate 6: any BLOCKER finding halts the orchestrator;
  no operator-bypass is permitted at the gate. User rationale preserved
  verbatim: "MCPs can cause a lot of problems if they are not stable and
  the system fails silently or the devcontainer and docker fail."
---

# ADR-0043: Augmented `auditing-mcp` is a hard gate at orchestrator Gate 6

## Contents

Section completion checklist — each box must be checked (including `N/A — out of scope` rows) before this document leaves draft. The reviewer's Gate 0 check uses this list as the structural-presence anchor.

- [x] Status
- [x] Context
- [x] Decision
- [x] Decision Details
- [x] Rationale
- [x] Options Considered
- [x] Consequences
- [x] Architecture Impact
- [x] Implementation Guidance
- [x] Related Information

## Status

Accepted — 2026-05-23 (user decision at Gate 4 of `devcontainer-mcp-provisioning-r1`)

## Context

The `devcontainer-mcp-provisioning-r1` Blueprint v2 codified the **bar** that the augmented `auditing-mcp` skill (10 rule families OP-1..OP-10) must produce zero BLOCKER findings against the post-feature devcontainer — see AC-FR-11-c, AC-CC-5, and AC-NFR-2-c. The Blueprint, however, left the **gating semantics** open: AC-CC-5 specified the bar but not whether a BLOCKER finding halts the orchestrator (hard gate) or is operator-advisable-but-overridable (advisory).

The open question was tracked as **OI-3 / Q-CC-9**. The design-composer's pre-decision recommendation was hard gate, but the recommendation was explicitly tagged as a user policy decision rather than a composer judgment, because it affects the orchestrator's halt semantics at Gate 6 (Deliverable Packaging) and the phase-validator that plan-author writes for that gate.

At Gate 4 of this feature, the user resolved OI-3 with the verbatim response:

> "I agree hard gate. MCPs can cause a lot of problems if they are not stable and the system fails silently or the devcontainer and docker fail"

This ADR codifies that resolution. Per FR-5, the design-composer is the only sub-agent in this pipeline that authors ADRs. The decision is one-way for orchestrator gating-policy because it sets the precedent for future MCP-touching feature runs that inherit `auditing-mcp` invocation.

Background facts loaded into the option space:

- The augmented `auditing-mcp` has four severity classes: BLOCKER, MAJOR, MINOR, NIT. Only BLOCKER is at issue for the hard-gate vs advisory decision; MAJOR / MINOR / NIT are advisory by default and not gated.
- The 10 rule families cover static config (OP-1, OP-2, OP-3, OP-4, OP-8, OP-9, OP-10), runtime events (OP-6 redaction integrity), and cross-layer / lifecycle consistency (OP-5 lifecycle completeness, OP-7 trifecta consistency). A BLOCKER from any family means the post-feature devcontainer is in a state the audit explicitly cannot reconcile.
- Silent MCP failures (per ADR-0037's NO CONSENSUS finding) are a real failure mode of this project's pipeline: stdio servers do not auto-reconnect (C-0301); operator-recovery is the recovery path; without `mcp-events.jsonl` surfacing, failures vanish into the void.
- The user's reasoning ("devcontainer and docker fail") is grounded in the project's documented Dockerfile fragility history (E-0081) and the feature's load-bearing FR-9 contract (operator-visible mid-run failure).
- ADR-0042 (`auditing-mcp` family graduation) is the paired Gate-4 decision; the hard-gate semantics combined with graduation produce a coherent posture — a graduated family hard-gating its own audit is structurally clean, while a sub-skill of `auditing-cc-configs` hard-gating would create an awkward asymmetry with its five other siblings.

## Decision

1. **Hard gate at Gate 6.** When the augmented `auditing-mcp` (rule families OP-1 through OP-10) runs as part of orchestrator Gate 6 and reports one or more BLOCKER findings, the orchestrator **halts** the gate progression. No operator-bypass is permitted at the gate. The findings must be remediated and the audit re-run to clear before Gate 6 advances.
2. **No advisory mode.** AC-CC-5 / AC-FR-11-c / AC-NFR-2-c retain the "zero BLOCKER findings" bar with strict enforcement semantics. The advisory alternative (operator may proceed past with rationale documentation) is explicitly rejected.
3. **MAJOR / MINOR / NIT remain non-gating.** These three severity levels are advisory; they surface in the audit report but do not halt the orchestrator. Operators may choose to address them or defer.
4. **The phase-validator records the hard-gate status.** The phase-validator that plan-author writes for Gate 6 explicitly invokes the augmented `auditing-mcp` and treats any BLOCKER finding as gate-blocking (exit non-zero / halt orchestrator), per the established convention.
5. **Kill criteria record the future-revisit signal.** This ADR's kill criteria (see Decision Details) define the conditions under which the hard-gate posture would be revisited; until those conditions trigger, the hard gate is the project's standing policy for any feature run that invokes `auditing-mcp`.

## Decision Details

| Item | Content |
|---|---|
| Decision | Augmented `auditing-mcp` BLOCKER findings hard-gate orchestrator Gate 6; no operator-bypass at the gate; MAJOR/MINOR/NIT remain advisory. |
| Why now | OI-3 was the load-bearing policy decision left open in Blueprint v2; closing it at Gate 4 is the right point. Deferring would either freeze the composer's hard-gate recommendation by default (the user agreed with that direction, but the user's explicit assent makes the decision a user-policy artifact rather than a composer judgment) or leave plan-author writing a phase-validator with TBD gating semantics. |
| Why this | User rationale (verbatim): "MCPs can cause a lot of problems if they are not stable and the system fails silently or the devcontainer and docker fail." The failure modes the augmented `auditing-mcp` catches (credential leak per OP-6, broken consumer-mapping per OP-2/3, missing lifecycle coverage per OP-5, supply-chain anti-patterns per OP-9/10) are not the kind of issues that should be allowed to ship past Gate 6 with operator override. The hard-gate posture is symmetric with the user's parallel ADR-0042 graduation decision (graduated families hard-gating their own audits is structurally clean). |
| Known unknowns | (a) Whether a BLOCKER finding from a single low-impact rule family (e.g., OP-7 trifecta-consistency on a benign cross-reference drift) is gating-worthy at the same level as a credential-leak BLOCKER (OP-6). The audit-skill's severity assignment is the governing artifact; if a particular rule family's BLOCKER severity proves over-broad in practice, the audit-skill's rule definitions are the right place to refine (not the gating policy). (b) Whether the orchestrator's halt-behavior at Gate 6 is operator-resumable (after remediation, re-run and continue) or full-restart. **Current convention:** operator-resumable; plan-author confirms the orchestrator's resume semantics at task time. (c) Whether other audit-skills with comparable BLOCKER discipline (e.g., `auditing-github-actions`) should adopt the same hard-gate posture at their respective gates. **Out of scope** for this ADR; deferred to the future review run captured in `Issues/proposal-auditing-family-graduation-review.md` or a separate pipeline. |
| Kill criteria | If after twelve months of post-ship operation, the hard-gate has fired N times where N ≥ 5 and ≥ 80% of those fires were on issues that retrospectively did not warrant halting the orchestrator (false-positive blocks), an amendment ADR may demote the posture to advisory. The judgment of "did not warrant halting" requires explicit case-by-case retrospective with rationale. Conversely, if a real BLOCKER (credential leak, broken consumer-mapping, missing lifecycle coverage) ever bypasses the gate due to operator override of a hypothetical advisory-mode, the hard-gate posture is vindicated. |

## Rationale

The user's stated reasoning ("MCPs can cause a lot of problems if they are not stable and the system fails silently or the devcontainer and docker fail") is grounded in three load-bearing facts:

1. **Silent failure is a documented and previously-unsolved problem.** ADR-0037's NO CONSENSUS finding (C-0349, verified-high) shows that this project is the first place this pattern is being solved in a principled way. An advisory-mode hard-gate alternative would create a pre-mature exit ramp from the new contract.

2. **Devcontainer and docker fragility is a documented project history.** E-0081 (the Yarn-key Dockerfile failure) is the canonical cited example; ADR-0041 codifies "no new Dockerfile work" to avoid re-litigating it. The augmented `auditing-mcp` is the project's principal defense against silent devcontainer breakage caused by MCP misconfiguration; weakening that defense at the gate level would undermine the entire feature's reliability commitment.

3. **The bar is already in the Blueprint.** AC-CC-5 / AC-FR-11-c / AC-NFR-2-c specify zero BLOCKER findings as the **bar**. Leaving the gating semantics advisory would create a structural asymmetry where the bar is published but unenforced — a worst-case condition for any quality-assurance contract.

The hard-gate semantics also resolve the **gating-asymmetry** that ADR-0042 would otherwise have created: hard-gating a single sub-skill of `auditing-cc-configs` would have been structurally awkward (one of six sub-skills gates, five do not). The paired graduation + hard-gate posture is internally coherent: a graduated family hard-gates its own audit. Symmetry with `auditing-github-actions` (already de-facto graduated; its own gating posture is a separate consideration captured in the follow-up Issue) is also restored.

## Options Considered

### Option 1: Advisory mode (operator may proceed past BLOCKER with rationale documentation)

**Pros:** Allows operator judgment for edge cases; lower friction for low-confidence BLOCKER findings.

**Cons:** Creates the worst-case condition for the AC-CC-5 bar (published but unenforced); the failure modes `auditing-mcp` catches are categorically the kind that should not be operator-overridable (credential leak, missing redaction, broken lifecycle, supply-chain anti-patterns); the user's rationale explicitly cites silent failures and devcontainer/docker breakage as the reason for hard-gating; the gating asymmetry with ADR-0042 graduation is unresolved.

### Option 2 (Selected): Hard gate — BLOCKER findings halt the orchestrator at Gate 6

**Pros:** Enforces the AC-CC-5 bar; symmetric with ADR-0042 graduation; the audit-skill's severity discipline is the only adjustment lever (clean separation of policy from implementation); user rationale is satisfied; future feature runs that invoke `auditing-mcp` inherit a clear contract.

**Cons:** No operator-bypass at the gate (operator must remediate + re-run, even for edge cases); a single over-broad BLOCKER severity assignment in the audit-skill could surface as friction; if the audit's BLOCKER triggers prove over-eager in practice, the rule-definitions in `auditing-mcp` are the only adjustment lever (not the gate).

### Option 3: Tiered gate (a subset of rule families hard-gate; others advise)

**Pros:** Granular: e.g., OP-6 (credential redaction) hard-gates, OP-7 (trifecta consistency) advises.

**Cons:** The audit-skill's severity model already provides tiering (BLOCKER/MAJOR/MINOR/NIT); creating a second tiering at the gate level duplicates and conflicts with the severity model. If a rule family's BLOCKER is genuinely lower-stakes, the right fix is at the rule definition (demote to MAJOR), not at the gate. Rejected as design-smell.

## Consequences

### Positive Consequences

- The AC-CC-5 / AC-FR-11-c / AC-NFR-2-c bar is enforced with strict semantics; the audit contract has teeth.
- The plan-author's Gate-6 phase-validator has unambiguous gating semantics; no TBD in the orchestrator hook.
- The user's substantive concern (silent MCP failures + devcontainer/docker breakage) is structurally defended.
- The ADR-0042 graduation + ADR-0043 hard-gate pair forms a coherent posture: graduated family hard-gates its own audit.
- Future MCP-touching pipeline runs inherit a clear gating contract.

### Negative Consequences

- No operator-bypass at the gate; remediation is required for any BLOCKER, regardless of edge-case context. (Operator-resumable after remediation per Decision Details Known Unknowns (b).)
- The audit-skill's severity model becomes load-bearing: a BLOCKER assignment in `auditing-mcp` is operationally equivalent to "halts the pipeline." This forces the audit-skill's rule definitions to be thoughtful about severity, which is healthy but raises the maintenance bar.
- A single misclassified BLOCKER in `auditing-mcp` (severity assignment error) could halt unrelated work until the audit-skill is patched. Mitigated by routine review of the audit-skill's rule definitions during operator-feedback windows.

### Neutral Consequences

- The 10 rule families' severity assignments are reviewed routinely as part of the augmented `auditing-mcp` maintenance; this is unchanged in scope but elevated in stakes.
- The orchestrator's halt-on-Gate-6-BLOCKER behavior is consistent with how other hard gates in the pipeline (e.g., Gate 1 review-failure) behave; no novel orchestrator pattern.

## Architecture Impact

1. **Layers affected.** Claude Code / Project Filesystem (the augmented `auditing-mcp` skill and the orchestrator's Gate 6 phase-validator). No other layer is directly impacted.
2. **Components that change.**
   - The Gate-6 phase-validator (authored by plan-author) — its specification incorporates "any BLOCKER finding from `auditing-mcp` halts the orchestrator at Gate 6."
   - The pipeline orchestrator — its Gate 6 step explicitly invokes `auditing-mcp` and treats non-zero exit as gate-blocking; the operator workflow on a halt is "remediate + re-run."
   - The augmented `auditing-mcp` skill — the gating ramification of its BLOCKER severity is documented in its `SKILL.md` body (one paragraph noting the hard-gate contract per this ADR).
3. **New dependencies introduced.** None at the runtime level. The change is policy + phase-validator wiring.
4. **Architectural constraints added.** Any future change to the augmented `auditing-mcp`'s BLOCKER definitions must consider the gating ramification: every BLOCKER assignment is operationally equivalent to a pipeline-halt condition. The audit-skill's rule-definition maintenance discipline absorbs this constraint.

## Implementation Guidance

**Phase-validator wiring (plan-author).** The Gate-6 phase-validator is a script (typically Python or bash) invoked by the orchestrator. Its specification incorporates:

```bash
# Pseudo-code; plan-author writes the concrete validator
python .claude/skills/auditing-mcp/scripts/audit_mcp.py --with-runtime
audit_exit_code=$?
if [ "$audit_exit_code" -ne 0 ]; then
  # auditing-mcp exit code non-zero signals BLOCKER finding(s);
  # halt the orchestrator at Gate 6 per ADR-0043.
  exit "$audit_exit_code"
fi
```

The exit-code-to-severity mapping is the audit-skill's responsibility; the validator merely treats non-zero as gate-blocking.

**Orchestrator hook (plan-author).** The orchestrator's Gate 6 (Deliverable Packaging) step invokes the phase-validator above. A halt at this point surfaces the failure to the operator with the audit-report path; the operator workflow is "remediate the BLOCKER per the audit report → re-run the phase-validator → orchestrator resumes Gate 6 step."

**`auditing-mcp/SKILL.md` body update.** Add a paragraph (or short section) noting:

> Per ADR-0043, any BLOCKER finding from this skill is a **hard gate** at orchestrator Gate 6 of any pipeline run that invokes it. Operators may NOT bypass the gate; remediation + re-run is the required path. MAJOR / MINOR / NIT severity findings are advisory and do not gate.

**Operator-resumable semantics.** The orchestrator's halt-on-Gate-6-BLOCKER is operator-resumable — i.e., the operator remediates the BLOCKER, re-runs the phase-validator, and the orchestrator resumes Gate 6 from the resume-point (not full-restart). Plan-author confirms the orchestrator's resume primitives at task time per Decision Details Known Unknowns (b).

**No procedural detail beyond the above.** Step-by-step orchestrator wiring, exact file paths, and exit-code conventions are Plan-author concerns.

## Related Information

- Related ADRs: ADR-0042 (`auditing-mcp` family graduation — paired Gate-4 user decision; the hard-gate posture is structurally coherent with graduation); ADR-0037 (the `mcp-events.jsonl` event surface that `auditing-mcp --with-runtime` reads); ADR-0039 (credential redaction posture; OP-6 BLOCKER findings audit redaction integrity); ADR-0041 (install-mechanism strategy; OP-5 BLOCKER findings audit lifecycle completeness).
- Referenced specs / docs: Blueprint v3 §Open Items / OI-3 closure (this ADR is its codification); Blueprint v3 §Acceptance Criteria (AC-CC-5, AC-FR-11-c, AC-NFR-2-c — the bar this ADR enforces); Blueprint v3 §Risks and Mitigation (the OI-3 row's disposition flips from TBD to hard-gate per this ADR closure); Blueprint v3 §Implementation Plan (phase-validator step gains gate-blocking severity); Blueprint v3 §State Transitions and Invariants (the augmented `auditing-mcp` BLOCKER row updated per this ADR).
- Issues / PRs: `Issues/proposal-auditing-family-graduation-review.md` (the broader gating-policy question across other graduated families is captured for downstream review).
- Related KBs: KB-cc-design (audit-skill BLOCKER discipline; phase-validator pattern), KB-documentation-criteria (ADR template, supersession discipline per ADR-0005), KB-review-disciplines (Gate-4 user-decision artifact discipline; severity-to-gate mapping conventions).
