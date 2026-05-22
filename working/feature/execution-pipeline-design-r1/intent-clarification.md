---
id: IC-execution-pipeline-design-r1
version: 1.0.0
status: accepted
feature_slug: execution-pipeline-design-r1
user_token: IC-CONFIRM-execution-pipeline-design-r1-20260522T024500Z
generated: 2026-05-22T02:42:00Z
generated_by: claude (acting as intake-intent-clarifier, continuation session)
approved_at: 2026-05-22T02:45:00Z
gate_passed: 1
---

# Intent Clarification: Execution Pipeline Design (r1)

## Contents

- [x] Purpose
- [x] Source
- [x] Initial Interpretation
- [x] Clarifying Questions and Answers
- [x] Clarified Intent
- [x] Scope Posture
- [x] Stakeholder Posture (Preliminary)
- [x] Success Posture (Preliminary)
- [x] Confirmation
- [x] Open Items (Pending PRD Authoring)

## Purpose

This document captures the user's intent for the next feature in the project: designing the execution side of the feature pipeline. The planning side is in place and matured through multiple recent runs; the execution side has been improvised. This run formalizes it.

## Source

User said (paraphrased from a multi-turn design conversation across the prior session and this one): "After we complete task decomposition phase we have a task execution phase, then we need a quality phase that runs all tests, audits (think cc-audit, we also need github codespace audit and github actions audit). Of course we need to ensure all of the tests for frontend, backend, API, Query, Database and other layers pass. We also need to ensure all documents are managed using our existing skills. Also … we need an approach to incorporate any concerns the quality phase finds. For example, what point in the pipeline do these re-enter to get addressed? How does this impact the PRD, Blueprint, Plan and task documents? … I like (a) state-transition hooks tied to gate approvals and (b) a frontmatter validator. Also, it would help if I actually designed the execution part of the pipeline. Which is something we will do next."

## Initial Interpretation

The execution side of the feature pipeline (everything after Task Decomposition through Deliverable Packaging) currently exists as ad-hoc orchestration improvised during each run. The user wants it formally designed: explicit stages with explicit gates, named agents per stage, defined artifacts at each gate, a per-task execution loop, a phase-level quality stage that covers all layer tests plus the project's three platform-audit families (cc, codespaces, GitHub Actions), and a reconciliation loop that routes quality findings back to the right upstream artifact (task → plan → blueprint → PRD → intent) based on finding depth. The two specific implementation choices already named — gate-tied state-transition hooks (a) and a frontmatter validator (b) — solve the document-lifecycle drift problem surfaced in the prior `audit-findings-remediation-r1` run.

## Clarifying Questions and Answers

| # | Ambiguity | Question Asked | User Answer | Resolved? |
|---|---|---|---|---|
| 1 | Whether (a) and (b) are confirmed in scope or up for design re-evaluation | Implicit through prior turn — user said "yes incorporate a and b" | (a) state-transition hooks and (b) frontmatter validator are both binding inclusions | [x] |
| 2 | Whether per-task quality and phase-level quality are both needed, or just one | Surfaced in design conversation as a distinction; user did not push back | Both are needed; not a design decision to revisit at PRD time | [x] |
| 3 | Whether the audit scripts called by phase-level quality need to be built in this feature, or are assumed-existing | "Pipeline structure but if we already have an audit function for codespace and actions inside the skill. Is this a pattern we should consider to separate similar to cc?" | Pipeline structure is the primary deliverable. Existing audit scripts that live inside KB-github-actions-platform and KB-codespaces-platform should be extracted into peer `auditing-github-actions` and `auditing-codespaces` skills, mirroring the cc-style three-way split (KB-platform = what, KB-design = how, auditing-X = audit, with canonical helpers in auditing-shared per ADR-0031). This extraction is in scope. Net-new audit scripts beyond what already exists are NOT in scope. | [x] |
| 4 | Feature slug | Asked directly | `execution-pipeline-design-r1` | [x] |
| 5 | Whether any prior scaffolding for execution-phase work exists | Asked directly | No prior scaffolding | [x] |
| 6 | Whether the `ai-development-guide` skill (uploaded reference) carries a binding role in the feature | "We need to ensure this skill is included in the sub agent. It is very important." | `ai-development-guide` is a binding constraint: every execution-phase sub-agent that produces or modifies code MUST load it. Carried through PRD as a functional requirement and through Blueprint as a binding constraint on agent design. | [x] |

## Clarified Intent

Design the execution side of the feature pipeline as a formal multi-stage structure with explicit gates, named sub-agents, defined artifacts, and a reconciliation loop. The pipeline runs after Task Decomposition completes and ends with the existing Deliverable Packaging stage. It consists of a per-task execution-and-quality inner loop, a phase-level quality stage that covers all layer tests (frontend, backend, API, query, database, and other activated layers) plus the project's three platform-audit families (cc-audit, GitHub Actions audit, GitHub Codespaces audit) plus a frontmatter validator across all feature-pipeline artifacts, and a quality-reconciliation outer loop that classifies findings by depth and dispatches them back to the appropriate upstream authoring agent (task-decomposer, plan-author, design-composer, intake-prd-author, intake-intent-clarifier). Document lifecycle is automated via state-transition hooks fired at each gate boundary. As a structural prerequisite, the cc-style three-way split (`KB-X-platform` / `KB-X-design` / `auditing-X`) is applied to GitHub Actions and GitHub Codespaces by extracting their existing audit scripts into peer skills with canonical helpers in `auditing-shared`. All execution-phase sub-agents that produce or modify code load `ai-development-guide`.

## Scope Posture

### What's in scope

- Formal definition of the execution-pipeline stages from "Task Decomposition complete" through "Deliverable Packaging" (stage count and names to be settled in PRD).
- Per-stage explicit gates and named sub-agents for each stage.
- Per-task execution-and-quality inner loop pattern.
- Phase-level quality stage that calls all layer tests, the three platform audits (cc, GitHub Actions, GitHub Codespaces), and a new frontmatter validator across feature-pipeline artifacts.
- Quality-reconciliation loop with a finding-depth classifier and dispatch matrix routing findings back to the responsible upstream agent.
- State-transition hooks fired at each gate boundary (the (a) decision) — every gate pass updates the relevant artifact's frontmatter `status` field.
- Frontmatter validator (the (b) decision) — runs at every gate, checks required fields, status currency, supersession back-links, and execution-phase artifact schemas.
- Schemas and templates for execution-phase artifacts that were previously ad-hoc (`implementation-notes.md`, `observations.md`, `reconciliation-log-cycle*.md`, `final-audit-report.md`, `acceptance-matrix.md`, `cross-artifact-audit-final.md`, and any analogues this design adds).
- Extraction of `auditing-github-actions` and `auditing-codespaces` from their respective `KB-X-platform` skills, mirroring the existing cc 3-way split (with canonical helpers landing in `auditing-shared` per ADR-0031).
- `ai-development-guide` skill loaded by every execution-phase sub-agent that produces or modifies code, captured as an FR in the PRD and as a binding constraint in the Blueprint.
- A reconciliation-budget policy for the execution-side loop (separate budget from the planning-side budget defined in ADR-0021).

### What's NOT in scope (explicitly excluded)

- Authoring net-new audit scripts beyond what already exists in the project (e.g., no new "backend audit", no new "API contract audit", no new "database migration audit"). The pipeline can call audits that don't yet exist as the project later defines them; missing audits surface as findings during real execution, not as gaps in this design.
- Changes to the planning side of the pipeline (Intent through Task Decomposition). This feature builds on top of the planning side as it currently stands; it does not modify it.
- Changes to ADR-0021's planning-reconciliation budget. A new budget is defined for the execution side; the planning side is untouched.
- Implementation of the designed pipeline. This feature designs the pipeline (PRD + Blueprint + per-layer Designs + Plan + Acceptance Tests + Phase Validators) and ships those artifacts. Building the sub-agents and scripts that the design specifies is a follow-on feature.
- Migration of historical archives (e.g., `audit-findings-remediation-r1`) to the new execution-phase artifact schemas. Those archives stand as they were authored under the prior improvised model.

### What's undecided (deferred to PRD or later)

- Whether per-task quality runs a quick smoke regression in addition to its task-diff scope, or whether cross-task regression detection waits for phase-level quality (latency vs detection-completeness trade-off).
- Whether phase-level quality runs the full test suite or only suites touched by the run's changed files.
- Numeric reconciliation-budget cap for the execution loop (planning's cap is 4; execution may want different).
- Whether a user-approval gate sits between phase-level quality pass and Deliverable Packaging, or whether deliverable packaging proceeds automatically on quality pass.
- The exact set of execution-phase artifact templates beyond the ones already named — discovered during PRD / Blueprint authoring.

## Stakeholder Posture (Preliminary)

- **User (project owner):** wants the execution side of the pipeline to be as disciplined and inspectable as the planning side, with document state automation eliminating the manual frontmatter cleanup pain surfaced last run.
- **Future feature pipeline runs:** consume the designed execution pipeline directly; benefit from explicit gates, named agents, and a defined reconciliation pattern instead of ad-hoc orchestration.
- **Audit subsystem maintainers (cc / GHA / Codespaces):** gain a consistent location for audit scripts after the 3-way-split extraction.
- **Document-lifecycle reviewers (`shared-document-reviewer` family):** receive a new sibling — the frontmatter validator — and may share canonical helpers.

## Success Posture (Preliminary)

The feature is "working" when the execution-pipeline design is shipped as a coherent set of pipeline artifacts (PRD, Blueprint, per-layer Designs, Plan, Acceptance Tests, Phase Validators), audited clean through the existing planning-side gates, with no remaining BLOCKER findings and MAJOR findings either resolved or named-exempt. Concretely: a future feature pipeline run can be executed from Task Decomposition forward by following the design produced here, without improvisation; the frontmatter validator and state-transition hooks are specified clearly enough that a follow-on implementation feature could build them directly from the Blueprint and Plan; and the 3-way auditing-X split is applied to GitHub Actions and GitHub Codespaces, with canonical helpers in `auditing-shared`.

## Confirmation

Pending Intent Confirmation Gate. User to confirm by saying "approve" (or equivalent) — orchestrator will then generate `user_token` and stamp the frontmatter `user_token` field, and the document advances to PRD Authoring.

## Open Items (Pending PRD Authoring)

- The five items listed under "What's undecided" above each become open items in the PRD author's rationale brief; the PRD author resolves them as functional requirements or surfaces any that need further user input.
- The finding-depth classifier (Level 0 through Level 8, as discussed) needs PRD-level formalization as a functional requirement, with the dispatch matrix specified at Blueprint time.
- The reconciliation-budget cap for execution needs PRD-level decision; default-proposed value is one that the PRD author selects based on cascade-cost analysis.
- The full enumeration of execution-phase artifact templates needs Blueprint-level decision and KB-documentation-criteria authorship as part of the Plan.
