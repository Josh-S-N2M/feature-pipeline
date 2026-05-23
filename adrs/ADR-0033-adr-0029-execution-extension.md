---
id: ADR-0033
title: ADR-0029 execution-phase extension — Scope-Deviation surfacing for execution-pipeline artifacts
status: accepted
date: 2026-05-22
accepted: 2026-05-22
deciders: [user, claude (as design-composer)]
supersedes: []
superseded_by: []
related: [ADR-0029, ADR-0030, ADR-0031, ADR-0032, ADR-0035]
authored_in_feature: execution-pipeline-design-r1
pairs_synthesis_decisions: [D-7]
closes: ["ADR-0029 Forward Implications anticipated extension"]
revised: 2026-05-22T22:00:00Z
revision_reason: |
  In-place edit per blueprint-v5.md authoring (reconciliation cycle 3),
  addressing audit finding I-AA-606. The Context section gains two cross-
  reference sentences pointing at the Blueprint AC-FR-7 floor coverage
  subsection: (1) pipeline-run-summary serves as the PRD AC-FR-7-c
  "execution-reconciliation log" floor item per Blueprint Path B disposition;
  (2) the "frontmatter-validation report" floor item exists as a JSON-output
  schema in validate_pipeline_frontmatter.py source rather than as a pair-
  pattern artifact — outside ADR-0033's per-artifact Scope-Deviation surfacing
  scope. In-place edit acceptable because status: proposed (per ADR-0032's
  per-doc-type ADR vocabulary, the proposed → accepted transition has not yet
  occurred at the Architecture Audit pass); same exception used for ADR-0034's
  revision at 2026-05-22T18:30:00Z. Also adds ADR-0035 to the related field
  (new this run; ADR-0035 ratifies the auditing-shared skill-binding
  convention referenced indirectly by the deviation-surfacing principles
  in this ADR).
---

# ADR-0033: ADR-0029 execution-phase extension — Scope-Deviation surfacing for execution-pipeline artifacts

## Context

ADR-0029 (no-silent-scope-changes principle) was authored during `audit-findings-remediation-r1` Gate 3 and codified the discipline as project-wide cross-stage. Its operational rules included a per-stage Scope-Deviation surfacing table covering 13 pipeline stages (Intent Clarification through Deliverable Packaging), with each stage's canonical output document gaining a Scope-Deviation surfacing section when a deviation is observed.

ADR-0029's Forward Implications section explicitly anticipated future extensions:

> Several existing stage templates (`codebase-analysis-report.md`, `synthesis.md`, audit JSON schemas, packager-report.json) need a new "Scope-Deviation" structural element. Out of scope for this ADR (which only adopts the principle); a follow-on machinery feature run implements the templates + audit checks.

This Blueprint's feature (`execution-pipeline-design-r1`) creates the execution-phase artifacts that ADR-0029's per-stage surfacing table did not anticipate (because they didn't exist yet):

- `per-task-execution-result.{json,md}` (per task)
- `phase-quality-report.{json,md}` (per phase-quality stage)
- `quality-reconciliation-log.{json,md}` (per reconciliation cycle)
- `state-transitions.log` (JSONL, per feature run)
- `pipeline-run-summary.json` (per feature run)

These artifacts need explicit Scope-Deviation surfacing locations per the no-silent-scope-changes principle. Absent this extension, execution-phase agents (`execute-orchestrator`, `execute-phase-quality-reviewer`, `execute-task-code-producer`, `execute-task-quality-handler`, `execute-finalize-reconciler`) would have no canonical statement of where to surface deviations — recreating the silent-absorption failure mode at the execution surface that ADR-0029 was specifically designed to prevent.

Additionally, Q-CC-4 arbitration in this Blueprint (auditing-codespaces stub semantics, decided `{"stub": true, "findings": []}`) cited this ADR-0033 as the principle's execution-side extension — the stub-vs-real distinction IS a Scope-Deviation that must surface per ADR-0029, and the execution-phase representation needs canonical documentation.

Two cross-references to the Blueprint AC-FR-7 floor coverage subsection are warranted for downstream-reader legibility (added 2026-05-22 per audit finding I-AA-606):

1. `pipeline-run-summary` serves as the PRD AC-FR-7-c "execution-reconciliation log" floor item — per Blueprint Path B disposition (the per-feature-run reconciliation aggregation is the same artifact under a different framing; see Blueprint §AC-FR-7 floor coverage). The 5-artifact enumeration above thus maps to PRD AC-FR-7-c's 5-item floor: per-task-execution-result = "per-task execution log"; phase-quality-report = "phase-quality report"; quality-reconciliation-log = "quality-reconciliation log (per cycle)"; pipeline-run-summary = "execution-reconciliation log"; state-transitions.log covers the beyond-floor artifact per AC-FR-7-d permission.
2. The PRD AC-FR-7-c "frontmatter-validation report" floor item exists as a JSON-output schema in `validate_pipeline_frontmatter.py` source rather than as a pair-pattern artifact — outside ADR-0033's per-artifact Scope-Deviation surfacing scope (script source is the canonical schema location; see Blueprint §AC-FR-7 floor coverage Path B rationale). This is why the enumeration above lists 5 artifacts and not 6: the 6th PRD floor item is intentionally not a pair-pattern artifact and therefore does not get a Scope-Deviation surfacing row in the table below.

## Decision

**Extend ADR-0029's per-stage Scope-Deviation surfacing table with execution-phase rows.** The principle is unchanged; only the per-stage surfacing locations gain new entries. ADR-0029 remains canonical for the principle; this ADR canonical for execution-phase application.

### Extended Scope-Deviation surfacing table (execution-phase additions)

| Execution stage | Canonical surfacing location | Notes |
|---|---|---|
| Per-task execution (`execute-task-code-producer` invocation through return) | `per-task-execution-result.md` — new "Scope-deviation findings" section | Code-producer surfaces any deviation from task-as-written (e.g., target-files scope expanded mid-task, implementation requires additional dependency not in task spec) |
| Per-task quality (`execute-task-quality-handler` verdict-issuance) | `per-task-execution-result.md` — same section; findings flagged with `scope-deviation: yes` boolean | Quality-handler verdict that requires reverting beyond per-task diff scope IS a deviation |
| Phase-level quality (`execute-phase-quality-reviewer` aggregating test layers + audit families + frontmatter validator + discipline check) | `phase-quality-report.md` — new "Scope-deviation findings" section | Reviewer surfaces any finding that implies upstream re-authoring (Level 4+) as a deviation; the deviation's resolution path is the dispatch matrix |
| Reconciliation cycle (`execute-finalize-reconciler` dispatch) | `quality-reconciliation-log.md` — per-cycle section explicitly flags scope-deviation findings | Reconciler surfaces any finding that was dispatched at Level 4 or higher; cycle-cap exhaustion (per ADR-0017 4-cycle cap, symmetric per D-12) IS a deviation requiring user escalation per AC-FR-10-c |
| Stub-vs-real audit distinction | `phase-quality-report.md` — audit-family section displays `{"stub": true}` indicator from auditing-codespaces (or any other stub audit) | Per Q-CC-4 resolution: stub returning `{"stub": true, "findings": []}` IS a Scope-Deviation surfacing — the run advertises a Codespaces audit but the stub-vs-real distinction must surface so downstream consumers (audit-counter delta, phase-quality verdict) can treat it appropriately |
| Discipline-5 mechanical findings (D-15) | `phase-quality-report.md` — discipline-check section displays findings from `check_pipeline_discipline.py` | A pipeline-stage-by-number reference in any artifact IS a discipline violation that surfaces (rather than being silently corrected); the dispatch matrix routes the finding at Level 0 (auto-fixable) or Level 1 (context-sensitive) per FR-4 |
| State-transition failures (AC-FR-5-e) | `state-transitions.log` — every transition logged; failed transitions trigger Level-1 finding routed through FR-4 dispatch matrix | A state-transition hook failure (file write error, missing target artifact) IS a deviation that must surface; silent skip would violate ADR-0029 |
| Run-termination (`execute-orchestrator` final state) | `pipeline-run-summary.json` — final check; flag any deviation not visible in prior surfacing artifacts | Mirrors ADR-0029's `packager-report.json` final-check role for execution-pipeline-side |

### Execution-side audit-stage enforcement

ADR-0029 specified that audit stages (Architecture Audit and Cross-Artifact Audit) scan upstream artifacts for unsurfaced deviations. **This extension applies symmetric enforcement at execution surface:**

- `execute-phase-quality-reviewer` MUST scan its inputs (per-task-execution-result artifacts from the phase) for deviation findings not surfaced in the per-task artifact's Scope-deviation findings section. Unsurfaced deviations are BLOCKER findings routed at Level 2 (test/implementation bug) or Level 5 (plan-level gap) depending on the deviation's nature.
- `execute-finalize-reconciler` MUST scan its inputs (phase-quality-report) for the same. Unsurfaced deviations route through the dispatch matrix.
- The cross-artifact-audit pass (existing planning-side discipline) extends symmetrically: execution-phase artifacts join the scanned set.

### Resolution paths (inherited from ADR-0029)

When an execution-phase deviation is surfaced, the resolution paths are the same three from ADR-0029, with execution-specific mappings:

- **(a) PRD amendment**: rare for execution-phase; would mean the deviation reveals a PRD requirement contradiction (Level 7 finding per FR-4) requiring re-authoring upstream.
- **(b) Defer to follow-on feature**: applicable for non-blocking deviations that don't prevent the current run's completion.
- **(c) Reject the deviation**: applicable for deviations the user explicitly accepts as named-exempt per mechanism α (ADR-0030).

Silent absorption is NOT among the resolution paths (inherited unchanged from ADR-0029).

## Validation evidence

### ADR-0029's anticipated extension

ADR-0029 Forward Implications explicitly anticipated this extension as future work. This Blueprint operationalizes that anticipation; the principle's coverage is now complete across all 17 named pipeline stages (13 planning-side from ADR-0029 + 4 execution-phase added here: per-task execution, per-task quality, phase-level quality, reconciliation cycle, plus run-termination).

### Q-CC-4 cross-link

Q-CC-4 arbitration in this Blueprint (auditing-codespaces stub semantics) cited this ADR as the principle's execution-side extension. The Q-CC-4 decision (`{"stub": true, "findings": []}`) and this ADR's Decision section are mutually grounding: the Q-CC-4 decision applies the principle; this ADR documents the application as a canonical case.

### cc-design.md Open items pre-declaration

`cc-design.md` v1.0.0 Open items section listed "ADR-B: ADR-0029 execution-phase extension (D-7)" as a planned ADR for this feature run, with D-7 as the pairing synthesis decision. This ADR-0033 fulfills that pre-declaration.

### Execution-phase artifact creation precondition

This Blueprint creates the execution-phase artifacts (per FR-7-c floor + 2 introduced beyond floor). Without ADR-0033's surfacing extension, the artifact templates (created per FR-7-a/b implementation tasks) would have no canonical statement of where Scope-Deviation sections belong. The temporal coupling is tight: this ADR is the substrate prerequisite for the FR-7 template content.

## Consequences

**Positive:**

- Closes ADR-0029's Forward Implications anticipated extension. The no-silent-scope-changes principle now has complete coverage across all pipeline stages (planning + execution).
- Provides explicit guidance for execution-phase agents on Scope-Deviation surfacing locations — no improvisation, no silent absorption.
- Audit-stage enforcement extends symmetrically: `execute-phase-quality-reviewer` and `execute-finalize-reconciler` gain the upstream-deviation-scan responsibility, mirroring the Architecture Audit + Cross-Artifact Audit pattern.
- Q-CC-4's stub semantics decision is well-grounded — `{"stub": true, "findings": []}` is the discipline-respecting representation per this ADR's "Stub-vs-real audit distinction" surfacing row.
- The execution-phase artifact templates (per FR-7 implementation tasks) gain a canonical Scope-Deviation section pattern; no per-template improvisation.

**Negative:**

- Adds enforcement workload to execution-side agents: they must scan their inputs for unsurfaced deviations. The cost is modest — the scan is a defined script invocation (`auditing-shared/scripts/scan_unsurfaced_deviations.py` is a candidate follow-on script; not in scope for this feature).
- Without the candidate follow-on script, the scan is performed by agent prompts which is less mechanical than the ADR-0030 substrate would prefer. The discipline-5 mechanical-enforcement model (D-15) is the eventual target; this ADR articulates the requirement without yet shipping the enforcement script.

**Forward implications:**

- The execution-phase artifact templates created per FR-7 implementation tasks include the Scope-Deviation section pattern documented here. The templates are authored in Plan + Execution; this ADR documents the requirement.
- The frontmatter validator (FR-6 / `validate_pipeline_frontmatter.py`) gains a check that execution-phase artifacts include the Scope-Deviation section (when applicable for the artifact type).
- A follow-on feature may ship `scan_unsurfaced_deviations.py` for mechanical enforcement of the audit-stage scan responsibility. Until then, agent prompts carry the discipline statement.

**Risk of over-application:**

- Execution-phase agents may flag every per-task finding as a "deviation" when most findings are routine (lint errors, test failures within scope). The threshold (inherited from ADR-0029): a finding is a deviation when it would (a) change the count of files/agents/specs the feature must touch, (b) require re-authoring an upstream artifact (Level 4+ in FR-4 dispatch), or (c) implies the artifact-as-written doesn't match observed reality. Routine in-scope findings are NOT deviations; they're routine dispatch matrix targets.

## Alternatives considered

**Alternative 1: Re-author ADR-0029 with execution-phase rows added (supersession).** Rejected: the principle is unchanged; only the per-stage surfacing table needs extension. Supersession would require restating the unchanged principle, reset the "Status: accepted" history, and risk losing the audit-trail context of why ADR-0029 was authored originally. Extension via a related ADR per the ADR-0029 Forward Implications anticipation is the lighter and more honest move.

**Alternative 2: Embed the execution-phase surfacing rules in this execution-pipeline Blueprint without a separate ADR.** Rejected: the no-silent-scope-changes principle is project-wide; encoding extensions in a single feature's Blueprint hides the rule from future features and makes it harder for them to apply. ADRs are the canonical home for project-wide disciplines per ADR-0019 (naming convention) discipline.

**Alternative 3: Defer to a follow-on feature; this Blueprint just notes the extension is pending.** Rejected: this Blueprint creates the execution-phase artifacts that the extension must cover. Without the ADR's extension, the artifact templates (FR-7 implementation tasks) have no canonical statement of where Scope-Deviations surface. The temporal coupling is tight — the ADR is the substrate prerequisite.

**Alternative 4: Add per-stage surfacing rules as a sub-section of ADR-0031 (auditing-shared skill module) since auditing-shared is the home for cross-cutting scripts.** Rejected: ADR-0031 governs script-module organization, not the no-silent-scope-changes discipline. Conflating the two would muddle the canonical homes of two distinct concerns.

## Notes

This ADR pairs synthesis-stage decision **D-7** ("ADR-0029 extension to execution-phase Scope-Deviation surfacing"). The pairing is direct: D-7's substrate is exactly the gap this ADR fills.

The Q-CC-4 stub semantics decision is the worked example of the principle applied at execution surface; reading Q-CC-4 arbitration alongside this ADR provides the round-trip from principle (ADR-0029) → extension (this ADR) → application (Q-CC-4 decision in Blueprint).

The audit-stage enforcement extension is symmetric with planning-side: just as Architecture Audit and Cross-Artifact Audit scan upstream artifacts for unsurfaced deviations, `execute-phase-quality-reviewer` and `execute-finalize-reconciler` scan their upstream execution-phase artifacts. The symmetry is structurally important — without it, execution-phase deviations could accumulate silently while the planning-side enforcement remains rigorous.
