---
id: ADR-0029
title: No-silent-scope-changes principle — every scope deviation must surface
status: accepted
date: 2026-05-21
deciders: [user, claude]
supersedes: []
superseded_by: []
related: [ADR-0021, ADR-0023, ADR-0027]
---

# ADR-0029: No-silent-scope-changes principle

## Context

During Gate 3 (Research Plan Approval) for the `audit-findings-remediation-r1` feature, the research plan surfaced an open question OQ-002 narrowly scoped to one information need (IN-008): if discovery reveals that the Category C "genuinely stale links" actually point to deprecated skills, the disposition for those refs shifts from "delete the refs" to "delete entire skills" — expanding the feature's scope beyond the 18 Category C findings the PRD planned for.

The recommended disposition was option (a) — escalate to PRD amendment if scope shifts more than ~5 findings worth.

The user's answer generalized the principle: "a but for all findings. nothing should be silent because 1 could be major."

This generalization is large enough to warrant its own discipline document — applies to every category, every stage, every feature run — so capturing it as an ADR rather than burying it as a single research-plan question's resolution.

## Decision

**Adopt the no-silent-scope-changes principle as a project-wide cross-stage discipline:**

> Any discovery, design, or implementation finding that would expand, contract, or reinterpret the PRD's scope — for ANY category of finding, in ANY stage — MUST be surfaced explicitly for human resolution. No silent absorption. No silent deferral. No silent expansion. "Just one extra finding" is not a valid reason to skip surfacing.

### Operational rules

1. **Universal application.** The principle applies to all 13 pipeline stages (Intent through Deliverable Packaging) and to any post-pipeline hand-execution that follows the same discipline.

2. **Surfacing mechanism per stage.** Each stage's canonical output document gains a Scope-Deviation surfacing section when a deviation is observed:

   | Stage | Where to surface |
   |---|---|
   | Intent Clarification | (N/A — intent itself defines scope) |
   | PRD Authoring | "Undetermined Items" section + explicit annotation |
   | Discovery Planning | "Open questions for human resolution" |
   | Discovery Research (codebase) | `codebase-analysis-report.md` — new "Scope-deviation findings" section |
   | Discovery Research (external) | Per-topic research note — explicit annotation |
   | Synthesis | `synthesis.md` — "Surfaced scope deviations" section |
   | Per-layer Design | `<layer>-design.md` — "Q-`<LAYER>`-N" open questions; mark as `scope-deviation: yes` |
   | Design Composition | `blueprint-v<N>.md` — "Architectural Questions" carries forward layer deviations |
   | Architecture Audit | `architecture-audit-issues.json` — gains `scope_deviation` boolean per issue |
   | Plan Authoring | `plan-v<N>.md` — "Risks" section flags any plan-time scope discoveries |
   | Acceptance Test / Phase Validator Authoring | Document any AC or validator that can't be authored as PRD-stated; surface as a deviation |
   | Cross-Artifact Audit | `cross-artifact-audit-issues.json` — gains `scope_deviation` boolean per issue; MUST also check upstream artifacts for unsurfaced deviations |
   | Reconciliation | `reconciliation-log-r<R>.md` — surface any unresolved deviation as a reconciliation cycle blocker |
   | Task Decomposition | `tasks.json` — any task that exceeds PRD scope is a deviation |
   | Deliverable Packaging | `packager-report.json` — final check; flag any deviation not visible in prior surfacing |

3. **Audit-stage enforcement.** Both the Architecture Audit and Cross-Artifact Audit stages gain a new check: scan upstream artifacts for evidence of scope deviation that was NOT surfaced (e.g., a `codebase-analysis.json` finding that materially expands scope but doesn't appear in `codebase-analysis-report.md`'s scope-deviation section). Unsurfaced deviations are BLOCKER findings.

4. **Resolution paths.** When a deviation is surfaced, the user (or another authorized decision-maker) chooses among:
   - **(a) PRD amendment.** Update the PRD to absorb the deviation, with explicit version bump and re-approval.
   - **(b) Defer to follow-on feature.** Note the deviation as out-of-scope for current run; queue as follow-on. MUST be recorded in the handoff document so it doesn't get lost.
   - **(c) Reject the deviation.** The current scope stands; the deviation is not addressed in this run or a future one. MUST be recorded with rationale.

   Silent absorption is NOT among the resolution paths.

5. **Triviality is not a shortcut.** "It's only one extra finding" / "It's a trivial change" / "It naturally fits the current work" do not justify skipping the surfacing. The user's exact framing: "nothing should be silent because 1 could be major." A single deviation may be the canary for a larger pattern; the discipline only holds with zero unilateral scope decisions.

## Consequences

**Positive:**

- Every scope deviation has paper trail. Future audits of the project's history can reconstruct WHY scope changed at any point.
- The audit stages gain a real check against silent expansion — a class of defect that's been latent in past runs.
- The discipline is symmetric: it constrains agents (no silent expansion) but also gives them a clear path (surface + let the user decide).
- Aligns with the project's broader "no silent suppression" principle from `audit-findings-remediation-r1`'s intent constraint 3.

**Negative:**

- Adds friction. Every "small" finding becomes a surfacing decision; some agents may over-surface, producing noise.
- Counter-design: the surfacing must be cheap (one line in the right section), and the audit-stage checks should distinguish meaningful deviations from trivial ones via a documented threshold.

**Forward implications:**

- Several existing stage templates (`codebase-analysis-report.md`, `synthesis.md`, audit JSON schemas, packager-report.json) need a new "Scope-Deviation" structural element. Out of scope for this ADR (which only adopts the principle); a follow-on machinery feature run implements the templates + audit checks.
- The `audit-findings-remediation-r1` feature run that surfaced this ADR is itself bound by the principle going forward. Discovery, per-layer design, and downstream stages MUST surface any deviation observed.

**Risk of over-application:**

- Authors may mistake "any unexpected detail" for "scope deviation" and surface trivia. The rule of thumb: a finding is a scope deviation when it would change what the PRD's acceptance criteria require, or when it would change the count of files / agents / specs the feature must touch by ≥1 (regardless of magnitude). Authors who are unsure should surface and let the user decide rather than absorb.

## Alternatives considered

**Alternative 1: Threshold-based surfacing ("only surface if deviation > N findings worth").** Rejected by the user's "1 could be major" framing. Thresholds invite hairsplitting and create a class of "small deviations" that are by-construction never surfaced.

**Alternative 2: Surface only at gate boundaries (next human approval).** Rejected because the discipline needs to apply WITHIN stages too, not just at handoffs. An audit stage seeing an unsurfaced deviation must flag it BEFORE the next gate.

**Alternative 3: Trust agents to surface "important" deviations subjectively.** This is the current de facto practice and is exactly what the user's principle rejects. The whole point of the principle is to remove the agent's discretion.

## Notes

This ADR was authored at Gate 3 of the `audit-findings-remediation-r1` feature run because the user's answer to a feature-scoped question generalized into a cross-feature principle. The author's instinct to absorb the answer as a research-plan resolution (the original location of OQ-002) was itself a small instance of the pattern the principle is designed to prevent — a discipline change being silently absorbed into a single artifact rather than promoted to a discoverable location.

The principle's wording is the user's; the operational rules are the author's mechanical translation. If the user revises the wording, the operational rules adjust accordingly.

Audit-machinery template + JSON schema changes are deferred to a follow-on machinery feature run. This ADR captures the principle so that subsequent stages of `audit-findings-remediation-r1` (and other features) operate under it immediately, even before the template changes land. Stages with no "Scope-Deviation" structural element yet should surface deviations in the closest existing section (Open Questions, Risks, Notes) and reference this ADR.
