---
id: Synthesis-execution-pipeline-design-r1
version: 1.1.0
status: draft
feature_slug: execution-pipeline-design-r1
generated: 2026-05-22T04:00:00Z
revised: 2026-05-22T04:30:00Z
revision_reason: Post-synthesis pressure-test (user-prompted, 2026-05-22T04:30:00Z) surfaced five substantive problems and two anchoring concerns. Both high-value and medium-value fixes applied. Net structural changes - (1) D-9 demoted from solo keystone to part of joint architectural-shape trio with D-6 and D-10; (2) D-1's misapplied 4-phase-from-ai-development-guide option removed and recast around finding-organization dimensions; (3) D-15 broadened from "discipline-5 enforcement" to systematic "discipline enforcement mechanism" with discipline-5 as worked example; (4) D-16 (FR-5 state-transition hooks contract) added - FR-coverage gap; (5) D-17 (FR-12 audit-counter-delta computation contract) added - FR-coverage gap; (6) D-18 (FR-11 canonical state vocabulary scope) added - distinct from D-4's extension-fields scope; (7) Mechanical-application #2 noted as conditional on D-15. Substrate inventory updated 15 to 18 substantive decisions. Deliberation sequence re-keyed around joint architectural-shape Pass 1; D-16/D-17/D-18 integrated across passes. Substantive content additions warrant minor version bump.
generated_by: claude (acting as Synthesis stage fan-in, single-pass)
derived_from:
  - working/feature/execution-pipeline-design-r1/codebase-analysis.md (v1.1.1)
  - working/feature/execution-pipeline-design-r1/research-plan.md (v1.1.0)
  - working/feature/execution-pipeline-design-r1/prd-v1.1.0.md (v1.1.0)
  - working/feature/execution-pipeline-design-r1/intent-clarification.md (v1.0.0)
  - adrs/ADR-0017-document-reviewer-integration.md
  - adrs/ADR-0021-discovery-phase-architecture.md
  - adrs/ADR-0029-no-silent-scope-changes-principle.md
  - adrs/ADR-0030-mechanism-alpha-pedagogical-marker-justification.md
  - adrs/ADR-0031-auditing-shared-skill-module.md
reviewer_verdict: approved (Gate 0 pass, Gate 1 pass — Consistency 95, Completeness 94, Rule compliance 95, Clarity 93)
reviewed_at: 2026-05-22T04:50:00Z
amendment_log:
  - v1.0.1 at 2026-05-22T04:15:00Z — Discipline-5 violation correction. The original frontmatter `generated_by` field used "Stage 5 fan-in" (stage-by-number reference); replaced with "Synthesis stage fan-in" (stage-by-name). Per recipe-feature-pipeline/SKILL.md discipline 5: "No pipeline-stage references by number. Stage taxonomy is by name only." Patch-level per shared-conventions.md versioning rules.
  - v1.0.2 at 2026-05-22T04:22:00Z — Added D-15 (Discipline-5 enforcement mechanism) as substantive Blueprint decision surfaced from v1.0.1 remediation session. Substrate inventory updated 14 → 15.
  - v1.1.0 at 2026-05-22T04:30:00Z — Post-pressure-test substantive revision. Five problems and two anchoring concerns surfaced; both high-value and medium-value fixes applied. Changes - D-9 keystone language replaced with joint architectural-shape trio framing (D-6+D-9+D-10); D-1 re-framed to remove misapplied ai-development-guide 4-phase option; D-15 broadened from discipline-5-only to systematic discipline-enforcement question with discipline 5 as worked example; D-16 (FR-5 state-transition hooks) + D-17 (FR-12 audit-counter-delta) + D-18 (FR-11 canonical state vocabulary) added to close FR-coverage gaps; mechanical-application #2 noted as conditional on D-15. Substrate inventory updated 15 → 18 substantive decisions. Deliberation sequence re-keyed.
---

# Synthesis — execution-pipeline-design-r1

## Note on synthesis-machinery scope

The project's `synth-*` agent chain (substrate → framer → grapher → extractor → synthesizer → critic) is built for multi-source research synthesis with claim-level CoVe verification and three-option substrate enumeration per architectural decision. That machinery applies to research-heavy features with many external sources and contested claims.

This feature's research surface is small and uncontested: zero external research topics consumed (per `research-plan.md` v1.1.0 + per ADR-0021's "external research is conditional" — all 17 INs covered by codebase research or designer-general-knowledge), one codebase analysis surfacing 16 IN findings plus a revised 14-decision distillation, and the PRD/IC/ADR inputs. Running the full 6-agent claims-extraction chain would consume more context than it produces value. This synthesis is a single-pass fan-in: structured decisions + design implications + sequencing for the single activated layer (Claude Code).

**No scope deviation surfaced for the single-pass choice** — same precedent as `audit-findings-remediation-r1/synthesis.md`'s opening note. The recipe says "synth-* fan-in" without prescribing depth; lightweight fan-in is appropriate for the input size.

## Source map

| Source | Contribution to substrate |
|---|---|
| `prd-v1.1.0.md` | 13 FRs (11 P1 + 1 P2 + 1 P3); 60 ACs in EARS form; single-layer Layer Scope (Claude Code); Won't-Have boundary including narrow stub-skill carve-out |
| `intent-clarification.md` | 6 clarifying questions resolved; binding decision that `ai-development-guide` is a required skill on execution-phase code-producing sub-agents |
| `research-plan.md` v1.1.0 | 17 INs spanning convention, agent landscape, audit script landscape, ADR inheritances, template conventions, archive precedents |
| `codebase-analysis.md` v1.1.0 | 16 IN findings + revised distillation of 14 substantive Blueprint decisions + 4 mechanical applications + 1 scope-deviation surfaced (ADR-0017 vs ADR-0021 mis-credit) + 3 meta-discipline patterns confirmed |
| ADR-0017 | Canonical home of the 4-cycle reconciliation cap (blueprint v3 §3.7 fixed-point iteration) |
| ADR-0021 | Discovery phase architecture; KB+ADR-consultation principle reusable in execution-phase reviewers |
| ADR-0029 | No-silent-scope-changes principle; 14 surfacing locations enumerated planning-side; execution-phase locations gap |
| ADR-0030 | Mechanism α (pedagogical-marker justification) — symmetric meta-discipline with ADR-0029 at marker level |
| ADR-0031 | `auditing-shared` canonical helper home — extension target for FR-8 + any new FR-6 audit utilities |

## Substrate inventory

Total design surfaces carried into per-layer Design (Claude Code):

- **18 substantive Blueprint decisions** with 4 sub-decisions under D-2 (= 21 decision targets).
  - D-15 added 2026-05-22T04:18:00Z post-discipline-5-remediation (and broadened 2026-05-22T04:30:00Z post-pressure-test).
  - D-16 (FR-5 hooks), D-17 (FR-12 audit-counter-delta), D-18 (FR-11 vocabulary) added 2026-05-22T04:30:00Z post-pressure-test — closes FR-coverage gaps that the single-pass synthesis missed.
- **4 mechanical applications** the Blueprint applies (not deliberates). Mechanical-app #2's filename is conditional on D-15; location is foregone.
- **1 scope deviation surfaced** (ADR-0017 vs ADR-0021 4-cycle-cap mis-credit) — folded into codebase-analysis.md v1.1.1 in-table caption; main narrative still defers to Blueprint per user direction
- **1 editorial expansion candidate** — FR-7-c floor 5 → 9-11 artifacts per AC-FR-7-d
- **3 meta-discipline patterns** confirmed and applied symmetrically at execution level
- **1 self-surfaced discipline failure** (Discipline-5 violation in claude's own working artifacts) — remediated via patch-level version bumps on synthesis.md (v1.0.0 → v1.0.1) and codebase-analysis.md (v1.1.0 → v1.1.1); surfaced D-15 as new Blueprint decision (since broadened to systematic in v1.1.0)
- **Joint architectural-shape framing** for D-6 + D-9 + D-10 (formerly D-9-as-keystone; re-framed 2026-05-22T04:30:00Z post-pressure-test)
- **D-1 re-framed** (formerly included misapplied ai-development-guide 4-phase option; that pattern is FR-2 design space, not FR-3)

## Decisions framed (carried to per-layer Design)

Decision IDs `D-N` map directly to the revised distillation in `codebase-analysis.md` v1.1.0. The substrate below adds dependency clustering, identifies keystone decisions, and proposes a deliberation sequence.

### Joint architectural-shape question — D-6 + D-9 + D-10

These three decisions together answer "what is the overall shape of the execution-side architecture?" — they are facets of one question, not three separate decisions with one being foundational. They jointly resolve FR-1's pipeline structure ("execution-pipeline stages with named gates"). D-6 (orchestration shape), D-9 (reviewer architecture), and D-10 (agent inventory) constrain each other in both directions: the orchestration shape determines what agents exist; the agents' shape determines the reviewer's locus; the reviewer's locus shapes what the orchestration coordinates. **Deliberate jointly in Pass 1.** D-8 (per-task loop topology) is downstream of D-6 (a DAG-walker orchestration implies serial; an orchestrator-agent permits any).

### D-9 — Execution-side reviewer architecture

**Source**: IN-005 (promoted from commentary). **Status**: open. **Joint with D-6, D-10.**

**Question**: Single `execute-phase-quality-reviewer` agent / extend `shared-document-reviewer` with execution-phase modes / multiple specialized reviewers per audit-family domain?

**Substrate for the deliberation**:
- Precedent: `shared-document-reviewer` is a single Opus/high-effort agent loading 3 KB skills, handling 4 document types via mode dispatch (Composite, Per-perspective, DeliverableArchive, PedagogicalMarkerJustification). The "single agent + multiple modes" precedent works.
- Counter-argument for multiple specialists: execution-side audits include cc-audit (cc-configs/skills/subagents/contexts/hooks/settings/mcp), GHA audit, Codespaces audit, plus test pass/fail consolidation, plus frontmatter-validator outputs. Each has a different evaluation shape. Multiple specialists may serve each shape better.
- Counter-counter: the planning-side review-architecture-auditor + review-cross-artifact-auditor + shared-document-reviewer is already a 3-reviewer architecture for the planning side; symmetry would suggest 3 execution-side reviewers. This pattern is established.

**Bidirectional dependencies (not strict-downstream)**:
- With D-10 (agent inventory): the reviewer is one of the agents — the choice of 1-vs-3 reviewers directly changes the inventory count by ±2.
- With D-13 (scoring dimensions): the reviewer applies the rubric, but the rubric design can proceed without the reviewer-shape question being settled. The two are interdependent rather than strictly ordered.
- With D-14 (FR-4 dispatch taxonomy): the reviewer's surfaced findings drive what's dispatched, but the taxonomy can be enumerated by walking actual finding categories first and then asking which reviewer surfaces each.

### D-6, D-8, D-10 — Orchestration cluster

**Sources**: IN-007 (D-6, D-10), IN-009 (D-8). **Status**: all open. **Joint with D-9** (see "Joint architectural-shape question" preface above). D-6 + D-10 are part of the architectural-shape trio with D-9; D-8 is downstream of D-6.

- **D-6 — Execution-side orchestration shape**: orchestrator agent / user-driven (planning-side precedent) / DAG-walker (per-task agent walks `tasks.json` forward without a dispatcher)?
- **D-8 — FR-2 per-task loop topology**: serial / DAG-parallel (per `tasks.json`) / batched?
- **D-10 — Execution-side agent inventory**: minimum named-agent set + responsibilities + frontmatter shape?

**Why coupled**:
- D-6 = DAG-walker implies D-8 ≠ DAG-parallel (a single walker is serial by construction). D-6 = orchestrator-agent permits any D-8.
- D-10 follows from D-6 + D-9 jointly: orchestrator-agent path adds 1 agent (orchestrator); reviewer-architecture-as-1-agent adds 1; reviewer-architecture-as-3-agents adds 3. The agent count is path-dependent.

**Implied minimum inventory** (regardless of D-6/D-9 choice):
- 1 × per-task runner (analog of `task-executor` in uploaded reference)
- 1 × phase-quality reviewer family (1 or 3 agents per D-9)
- 1 × execution-side reconciler (analog of `finalize-reconciler`)
- 1 × frontmatter-validator runner (or an existing agent loads `auditing-shared/scripts/validate_pipeline_frontmatter.py` directly)
- 0 or 1 × orchestrator (per D-6)

Lower bound: 3 agents. Upper bound (orchestrator + 3 reviewers + runner + reconciler + validator-runner): 7 agents.

### D-2a, D-2b, D-2c, D-2d — Sub-agent shape cluster

**Source**: IN-017 (un-lumped from prior #2). **Status**: all open. **Constrains**: D-10 (these are properties of the agents in the inventory) and D-11 (sub-agent shape informs the "code-producing" definition).

- **D-2a — BLOCKING gates pattern (from `task-executor`)**: Adopt for execution-phase agents? The pattern: explicit `[BLOCKING]` annotations at Phase Entry, Step Completion, Exit gates. The agent halts and returns escalation JSON rather than proceeding past an unmet gate.
- **D-2b — Escalation-type taxonomy (`task-executor` defines 6)**: Verbatim / subset / project-specific new set? The 6: Design Doc Deviation, Similar Function Discovery, Investigation Target Not Found, Dependency Version Uncertain, Out of Scope File, Binding Decision Violation. Some map naturally to FR-4 dispatch categories (D-14); others may not apply at this project's grain.
- **D-2c — Structured-JSON return schema**: `task-executor`'s schema (status field + completion/escalation responses) / simplified / new? Coupled to D-5 (FR-7 artifact pair-pattern question — JSON sidecar discipline).
- **D-2d — Stub detection (`quality-fixer` Step 1 BLOCKING)**: Incorporate into FR-2's per-task quality loop? The pattern: before running any quality checks, scan for incomplete-implementation markers (`TODO`, `pass`, `raise NotImplementedError`, etc.) and BLOCK with `stub_detected` status if found.

### D-1, D-3, D-13 — FR-3 phase-quality cluster

**Sources**: IN-016 (D-1, re-framed to 4-way), IN-014 (D-3), IN-005 (D-13, promoted). **Status**: all open. **Dependency**: D-13 depends on D-9 (reviewer architecture defines who applies the rubric).

- **D-1 — FR-3 finding-organization dimension**: FR-3 invokes 7 distinct activity types (3 test layers + 3 audit families + 1 frontmatter validator per AC-FR-3-b). The activity *invocation* can be parallel; the question is how *findings* are organized when reported to the phase-quality reviewer and dispatched to FR-4.
  - Option (a) **by domain**: cluster as { tests-cluster | audits-cluster | validator-cluster }
  - Option (b) **flat**: no clustering — all findings reported in a single list with severity + source-activity tags
  - Option (c) **by severity**: cluster as { blocker | major | minor | info }, source-activity as a tag
  - Option (d) **hybrid**: domain-cluster at the top level, severity-sorted within each cluster
  
  Note: the 4-phase pattern from `ai-development-guide` (Static → Build → Test → Final Gate) is code-level quality, not phase-level. It belongs to FR-2's per-task quality loop design space, NOT FR-3. The category error of mapping that pattern onto FR-3's organizing dimension was identified during the post-synthesis pressure-test (2026-05-22T04:30:00Z) and removed.
- **D-3 — FR-3 invocation model**: extend `auditing-cc-configs` dispatch table (unified entry) or 3 parallel audit invocations (current de-facto pattern)? This decision concerns how FR-3 invokes the new audit families that FR-8 extracts (`auditing-github-actions` from `KB-github-actions-platform/scripts/`, plus `auditing-codespaces` as a stub per AC-FR-8-b).
- **D-13 — Phase-quality scoring dimensions**: planning-side uses Consistency/Completeness/Rule-compliance/Clarity. Execution-side candidates: test pass rate, audit finding count, build correctness, validator-pass count. Exact rubric undefined.

### D-12, D-14 — Reconciliation cluster

**Sources**: FR-10 (D-12), IN-008 (D-14, promoted). **Status**: open. **Dependency**: D-14 depends on D-9 (reviewer's surfaced findings drive what's dispatched).

- **D-12 — Execution reconciliation budget value**: mirror planning-side at 4 (per ADR-0017 / blueprint v3 §3.7) / smaller (execution loops may be more expensive per cycle) / larger?
- **D-14 — FR-4 dispatch-matrix taxonomy**: finding categories driving re-author dispatch. Planning-side has 6+ (PRD revision, Blueprint cross-cutting, per-layer Design, Plan, Acceptance Tests, Phase Validators). Execution-side undefined.

### D-11 — "Code-producing" definition for FR-9-b

**Source**: FR-9-b + IN-007 (promoted). **Status**: open. **Constrains**: which agents in D-10's inventory must declare `ai-development-guide` in `skills:` (per AC-FR-9-a) and which are subject to FR-6's validator check (per AC-FR-9-c).

**Question**: Does the reconciler (writes log files) qualify? Does the frontmatter-validator (writes report files; itself is code, but outputs are reports) qualify? Does an orchestrator (if D-6 picks that path) qualify?

**Substrate**: The PRD says "every execution-phase sub-agent that produces or modifies code." Strict reading excludes log/report producers. Inclusive reading includes any agent whose output may contain code-shaped material. The Blueprint should pick a definition that aligns with the meta-discipline (no silent failures) — likely inclusive but with documented boundaries.

### D-4 — Convention drift / spec authority

**Source**: IN-004 (re-attributed from prior #5). **Status**: open. **Independent** (not coupled to other decisions; resolution is a spec-authority decision likely warranting a new ADR).

**Question**: Canonicalize 4 extension fields (`intent_user_token`, `gate_passed`, `reviewer_verdict`, `approved_at`) in `shared-conventions.md` via spec update + ADR, OR leave archive-practice extension fields off-spec?

**Substrate addition from this review pass**: The reviewer also surfaced that `shared-document-reviewer`'s `doc_type` taxonomy doesn't include `codebase-analysis` (or the execution-side artifacts FR-7 introduces). This is a related drift item — extending the taxonomy to recognize execution-phase doc types is a natural pair with the extension-field canonicalization.

**Resolution recommendation**: option (canonicalize) — author a new ADR alongside the Blueprint extending `shared-conventions.md` with the 4 fields AND extending the `doc_type` taxonomy. Single ADR; small scope; high traceability value.

### D-5 — FR-7 artifact format (pair pattern or unified)

**Source**: IN-011 + IN-010. **Status**: open. **Mostly independent** (couples lightly to D-2c via JSON-return convention).

**Question**: Follow existing "X.json + X.md" pair pattern, or unified single-format? This decision determines how FR-7's execution-phase artifacts and FR-13's machine-parseable reconciliation log are structured.

**Substrate addition from IN-010**: prior archive evidence shows mixed practice — `final-audit-report.md` + `final-audit.json` is paired; `packager-report-final.json` is JSON only. The Blueprint should canonicalize one direction.

**Resolution recommendation**: pair pattern, with the .md as the human-readable narrative and the .json as the machine-parseable sidecar. AC-FR-7-b's "≥1 machine-parseable per artifact" requirement is satisfied trivially by the pair; the unified-format alternative requires a serialization format that's both human-readable and machine-parseable, which adds friction without clear benefit.

### D-7 — ADR-0029 extension

**Source**: IN-012 + IN-009. **Status**: open. **Semi-independent** (touches reconciliation cluster but doesn't require D-9/D-14 to be settled first).

**Question**: Author explicit execution-phase surfacing locations as a new ADR (or amendment to ADR-0029), OR argue existing 14 locations cover execution implicitly via Reconciliation?

**Substrate addition**: ADR-0029's Forward Implications section explicitly anticipated this feature: *"Several existing stage templates... need a new 'Scope-Deviation' structural element. Out of scope for this ADR; a follow-on machinery feature run implements the templates + audit checks."* The Blueprint should explicitly trace this anticipation forward.

**Resolution recommendation**: new ADR — extend ADR-0029's per-stage table with execution-phase rows (per-task → `<TBD: per-task-execution-log>` Scope-Deviation entries; phase-quality → `observations.md`-style entries; quality-reconciliation → quality-reconciliation-log entries). Authored alongside the Blueprint; surfaces the discipline before execution-side templates ship.

### D-15 — Discipline enforcement mechanism (systematic)

**Source**: surfaced during synthesis.md/codebase-analysis.md remediation session 2026-05-22T04:18:00Z; broadened during post-synthesis pressure-test 2026-05-22T04:30:00Z. **Status**: open. **Coupled**: to D-10 (whether to add a discipline-check auditor as a named agent), to FR-6 validator scope (mechanical-application #2 ↔ D-15), and to D-1/D-3 (if option 2 is taken, FR-3 invokes the new auditor).

**Background**: `recipe-feature-pipeline/SKILL.md` enumerates multiple disciplines (at minimum: discipline 3 [4-cycle reconciliation cap], discipline 4 [no silent GitNexus→codebase-memory-mcp fallback], discipline 5 [no pipeline-stage references by number]; discipline numbering implies disciplines 1 and 2 also exist — Blueprint must inventory the full list). Mechanical enforcement is uneven:
- Discipline 3: enforced by `finalize-reconciler` Phase 5 (cycle_number == 4 hard cap).
- Discipline 4: enforceable via `extraction_method` field in `codebase-analysis.json` — IF something checks it.
- Discipline 5: no current enforcement. Just-demonstrated insufficient (claude committed 17 violations in this feature's own discovery artifacts despite knowing the discipline).
- Other disciplines: unknown enforcement status pending Blueprint inventory.

**Worked example — Discipline 5 ("no pipeline-stage references by number")**:

Three implementation options for discipline-5 specifically:

1. **Extend FR-6's frontmatter validator** to also scan body prose for `\bStage[ -]?[0-9]+\b` patterns. Pros: single validator agent owns multiple discipline checks; co-located. Cons: validator scope expands from "frontmatter" to "frontmatter + body" — name and scope misalignment; conflates two distinct validation domains. **Coupling**: if this option is taken, mechanical-application #2's filename `validate_pipeline_frontmatter.py` is misleading and should be renamed.

2. **Author a separate `auditing-shared/scripts/check_pipeline_discipline.py`** that performs body-prose discipline checks across all disciplines from `recipe-feature-pipeline/SKILL.md`. Pros: clean separation; the `auditing-shared/` canonical home pattern (ADR-0031) is the natural fit; FR-6 scope stays disciplined; one auditor enforces multiple disciplines uniformly. Cons: one more script and one more invocation point at the phase-quality stage.

3. **Decline mechanical enforcement; rely on the discipline statement + review-stage human enforcement**. Just-demonstrated insufficient.

**Systematic decision**: the Blueprint should produce a discipline-enforcement inventory — for each `recipe-feature-pipeline/SKILL.md` discipline, declare current enforcement status and target enforcement status. Discipline 5 is the worked example, but the systematic exercise is the actual decision surface.

**Substrate**: this systematic question is the symmetric extension of ADR-0030's mechanism α at a different surface. ADR-0030 made marker-justification mechanically enforced because the discipline was being silently bypassed. Disciplines from `recipe-feature-pipeline/SKILL.md` need parallel treatment.

**Resolution recommendation for the worked example (discipline 5)**: option 2 (separate `auditing-shared/` script). Rationale: keeps FR-6's scope clean, uses ADR-0031 pattern, naturally accommodates future discipline checks. **No resolution recommendation for the systematic question** — Blueprint inventories first.

**Forward implication for FR-3**: if option 2 is taken for discipline 5 (and parallel auditors for other disciplines), FR-3's phase-quality stage invokes those auditors as part of the sweep — input to D-1 (organizing dimension) and D-3 (invocation model).

### D-16 — FR-5 state-transition hooks contract

**Source**: FR-5 (PRD); identified during post-synthesis pressure-test 2026-05-22T04:30:00Z. **Status**: open. **Independent** (not coupled to other decisions; FR-5 is a discrete subsystem).

**Background**: FR-5 says "state-transition hooks fire at each gate." The PRD's ACs name the hook concept but leave the contract undefined. The Blueprint must specify:

**Sub-question (a) — Trigger semantics**: What event triggers a hook?
- Gate pass only
- Gate fail only
- Both
- Configurable per gate

**Sub-question (b) — Hook contract**: What does the hook do, and what contract does it obey?
- **Inputs**: gate name, transition direction (forward/back/reject), invoking agent name, artifact path(s) affected
- **Outputs**: hook return is void? Returns a status? Can the hook block the transition or only observe?
- **Synchronicity**: synchronous (blocks the transition until hook completes) or asynchronous (fire-and-forget)?

**Sub-question (c) — Hook implementation locus**: Where does the hook live?
- A new agent (`execute-state-transition-hook`)
- A script under `.claude/skills/auditing-shared/scripts/` (executed by some other agent)
- An inline procedure embedded in each gate-firing agent's prompt
- A combination (the contract is shared; the implementation can vary per gate)

**Sub-question (d) — Hook output**: Where does hook output land?
- An append-only per-feature `state-transitions.log` (machine-parseable JSONL?)
- Frontmatter update of the artifact whose gate fired (e.g., adding `gate_passed: N`, `transitioned_at: <timestamp>`)
- Both (transitions logged centrally AND frontmatter updated)

**Substrate**: The prior archive's frontmatter pattern already shows partial gate-tracking via `gate_passed`, `approved_at`, `user_token` fields. These are written by the user-confirming agent, not by a hook. The hook concept formalizes and centralizes this — currently distributed and inconsistent.

### D-17 — FR-12 audit-counter-delta computation contract

**Source**: FR-12 (PRD); identified during post-synthesis pressure-test 2026-05-22T04:30:00Z. **Status**: open. **Light coupling** to D-1 (FR-3 finding-organization dimension determines how counts are aggregated).

**Background**: FR-12 names "phase-quality-report audit-counter delta" but leaves the delta-computation contract undefined.

**Sub-question (a) — Baseline**: Delta against what?
- Prior phase within the same feature (most natural for tracking phase-over-phase progress)
- Start-of-feature baseline (delta from initial-state to current)
- Prior pipeline run's same-phase report (delta from prior shipped feature)
- Configurable per feature (intent-clarification declares the baseline)

**Sub-question (b) — Counter unit**: Counted how?
- Raw finding count
- Severity-weighted (blocker × 10, major × 3, minor × 1)
- Per-domain (test failures separate from audit findings separate from validator failures)
- Multiple counters reported in parallel (the report carries 3+ deltas, not one)

**Sub-question (c) — Report location**: Reported where?
- Phase-quality-report frontmatter (machine-parseable; D-5 pair-pattern compliant)
- Phase-quality-report body (narrative form for human review)
- Separate `audit-counter-delta.json` sidecar
- Both frontmatter (summary) AND body (narrative)

**Sub-question (d) — Gating role**: Used for what?
- Gating decision (phase-quality verdict considers delta direction — fail if delta-up; pass if delta-down)
- Informational only (humans read; orchestrator doesn't gate on it)
- Both (informational by default; gating-on-delta is an opt-in feature config)

**Substrate**: The prior archive's `final-audit-report.md` carries `reduction_from_baseline: 148 → 2 (99% reduction)` in frontmatter — precedent for delta-against-feature-start baseline and a single percentage-reduction counter. The Blueprint should consider whether to canonicalize this specific pattern or generalize.

### D-18 — Canonical state vocabulary scope (FR-11)

**Source**: FR-11 (PRD); identified during post-synthesis pressure-test 2026-05-22T04:30:00Z. **Status**: open. **Distinct from D-4** (D-4 is about extension *fields* `intent_user_token`/`gate_passed`/`reviewer_verdict`/`approved_at`; D-18 is about the state *vocabulary* itself).

**Background**: `shared-conventions.md` defines a 5-state vocabulary: `draft | proposed | accepted | superseded | rejected`. Archive practice diverges: codebase-analysis docs use `status: complete`; the prior archive's synthesis.md also uses `status: complete`. The reviewer's Gate 0 flagged this drift in codebase-analysis.md v1.1.0 as an advisory note. FR-11 calls for canonicalizing the state vocabulary.

**Question**: How is the canonical state vocabulary canonicalized?

**Options**:

1. **Strict — every doc uses one of the 5 canonical states**: codebase-analysis/synthesis migrate to `accepted` once their gate equivalent fires; use the `gate_passed` field (canonicalized via D-4) to distinguish "gate-passed accepted" from "draft accepted". Pros: smallest vocabulary, easiest validation. Cons: requires migrating archive practice; `accepted` semantics gets overloaded.

2. **Extension — add `complete` as a 6th canonical state explicitly for analysis/synthesis-style artifacts**: the 5-state vocabulary becomes a 6-state vocabulary. Pros: respects archive practice; `complete` carries a distinct semantic ("the work is done; not the kind of artifact that goes through accept/reject gate review") vs `accepted` ("gate-reviewed and approved"). Cons: bigger vocabulary; new state needs precise definition to avoid drift.

3. **Per-doc-type vocabulary**: different doc types have different valid state sets. PRDs/Blueprints/Plans use `{draft, proposed, accepted, superseded, rejected}`; analysis/synthesis docs use `{draft, complete, superseded}`; ADRs use `{proposed, accepted, superseded, rejected}` (already de-facto). Pros: each doc type's state space matches its lifecycle; FR-6 validator can enforce per-type. Cons: most complex; validator complexity grows.

**Substrate**: ADRs already de-facto use a different vocabulary subset (no `draft` state; ADRs go straight to `proposed` then `accepted`). So per-doc-type vocabulary is already partially observed. Option 3 may be more honest than option 1 about what archive practice has been.

**Resolution recommendation**: option 3 (per-doc-type vocabulary), paired with D-4's spec-authority decision. Both belong in the same new ADR.

## Mechanical applications (Blueprint applies, doesn't deliberate)

Lifted verbatim from `codebase-analysis.md` v1.1.0:

1. **Frontmatter fields for the `ai-development-guide` install task**: per `shared-conventions.md` (Plan-task specification detail; not Blueprint-time).
2. **FR-6 validator file location**: `auditing-shared/scripts/validate_pipeline_frontmatter.py` (foregone under ADR-0031; filename distinguishes from existing `auditing-skills/scripts/validate_frontmatter.py` which validates SKILL.md frontmatter, not pipeline-document frontmatter). **D-15 coupling note**: if D-15 picks option 1 (extend FR-6 to body-prose), this filename becomes misleading and should be renamed (e.g., `validate_pipeline_document.py`). The "mechanical application" status holds for the location (`auditing-shared/scripts/`) but the filename is conditional on D-15.
3. **Execution-phase template location**: Option A (add to `KB-documentation-criteria/references/templates/`) — default-by-precedent given KB-documentation-criteria's stated scope.
4. **Execution-phase template internal structure**: yes, same internal structure as existing 6 templates (frontmatter + `## Contents` checklist + section-by-section guide). Preserves Gate 0 reviewer's structural-presence anchor.

## Cross-cutting design implications

### Single-layer feature (Claude Code only) — what design-claude-code receives

`design-claude-code` is the only per-layer Designer this feature activates. It receives this synthesis substrate plus the PRD plus codebase-analysis.md. Its output is `cc-design.md` covering:

- Resolution of all 14 substantive Blueprint decisions (D-1 through D-14) per the dependency-cluster sequencing recommended below
- Concrete agent definitions for the execution-side inventory (D-10) with frontmatter, tools, skills bindings, and procedures
- Concrete execution-phase artifact templates (D-5 format applied, ≥9 artifacts per the editorial expansion candidate)
- Architectural Questions for `design-composer` to absorb (cross-feature concerns)
- Open questions for Plan stage (Plan-time specification details)

### Architectural Q items for design-composer

- **Q-COMPOSE-1**: D-4's spec-authority decision likely produces a new ADR. Should it be authored by design-composer alongside the Blueprint, or by design-claude-code alongside cc-design.md? Per ADR-0011-derived discipline, ADRs that affect cross-feature shared conventions belong to design-composer.
- **Q-COMPOSE-2**: D-7's ADR-0029 extension is similar — cross-feature reach (every feature surfaces deviations through this discipline). design-composer's responsibility.
- **Q-COMPOSE-3**: The execution-side reviewer architecture (D-9) is largely Claude-Code-layer scope, but if D-9 picks the "extend `shared-document-reviewer` with modes" option, that's a cross-feature artifact change requiring design-composer coordination.

### Open question for Plan stage (carried forward)

- **Q-PLAN-1**: The Plan should include the install task for `ai-development-guide` (per AC-FR-9-e). The exact field list to add to the uploaded reference's sparse frontmatter (`name:` + `description:` only) is per `shared-conventions.md` skill conventions. design-claude-code names the skill conventions; Plan applies.

### Proposed deliberation sequence for design-claude-code

Per the dependency analysis, design-claude-code should resolve decisions in this order to minimize re-work:

```
Pass 1 (joint architectural-shape — deliberate together):
  D-6   orchestration shape
  D-9   reviewer architecture
  D-10  agent inventory
  D-8   per-task loop topology (downstream of D-6)
        ↓
Pass 2 (downstream of architectural-shape):
  D-2a-d sub-agent shape         (needs D-10's agent list as targets)
  D-11  "code-producing" boundary (needs D-10)
        ↓
Pass 3 (FR-3 + FR-12 cluster):
  D-1   FR-3 finding-organization dimension  (light input from D-15 if option 2)
  D-3   FR-3 invocation model               (light input from D-15 if option 2)
  D-13  scoring dimensions       (interdependent with D-9)
  D-17  FR-12 audit-counter-delta contract (light input from D-1)
        ↓
Pass 4 (reconciliation + state-transition):
  D-14  FR-4 dispatch taxonomy   (interdependent with D-9 — review surfacing drives dispatch)
  D-12  reconciliation budget value
  D-16  FR-5 state-transition hooks contract (independent)
        ↓
Pass 5 (cross-feature concerns + enforcement + vocabulary):
  D-4   convention drift / spec authority (likely new ADR; pair with D-18)
  D-18  canonical state vocabulary scope  (pair with D-4 — same new ADR)
  D-5   FR-7 artifact format
  D-7   ADR-0029 extension       (likely new ADR)
  D-15  Discipline enforcement mechanism (systematic; discipline-5 worked example; influences D-1/D-3/D-10 lightly)
```

**Sequencing notes**:
- Pass 1 is the joint architectural-shape resolution. Pass 1 outputs constrain everything downstream.
- Passes 3 and 4 can in principle run in parallel (no cross-pass dependencies), but Pass 3's outputs feed Pass 4's dispatch taxonomy (D-14) so serial is safer.
- D-4 + D-18 pair into one ADR; the synthesis recommends co-authoring.
- D-7 + D-15 may also pair into one ADR (both extend discipline at the meta level); Blueprint discretion.

## Surfaced for cross-artifact audit

Per ADR-0029, items requiring downstream audit visibility:

1. **ADR-0017 vs ADR-0021 4-cycle-cap mis-credit in PRD v1.1.0** — resolution path (a) deferred to Blueprint per user direction (2026-05-22T03:42:00Z). Cross-artifact audit should verify that Blueprint cites ADR-0017 correctly.

2. **doc_type taxonomy gap** in `shared-document-reviewer` — `codebase-analysis` (this feature's discovery output) and the execution-side artifacts FR-7 introduces are not in the reviewer's known `doc_type` set. Carried forward into D-4 as part of the spec-authority canonicalization.

3. **`status: complete` vocabulary** — used by codebase-analysis.md and prior archive's synthesis.md, but not in canonical 5-state vocabulary per `shared-conventions.md`. Convention-drift item; carried forward into D-4.

4. **FR-7-c floor editorial expansion** — prior archive shows 4 Q-004 candidate artifacts + 2 additional artifacts beyond Q-004 are all substantive in practice. Cross-artifact audit should verify the Blueprint's FR-7 design either canonicalizes the expanded floor or explicitly defends the smaller 5-artifact floor with rationale.

5. **Self-applied discipline failure — recipe-feature-pipeline discipline 5 ("no pipeline-stage references by number")** — user-surfaced at 2026-05-22T04:12:00Z. Honest finding: while authoring synthesis.md v1.0.0 and editing codebase-analysis.md v1.1.0, claude (acting in the discovery-codebase-researcher / synthesis-fan-in roles) committed multiple stage-by-number references — 17 instances in codebase-analysis.md's IN-007 agent-role table + IN-009's ADR-0021 description, plus 1 instance in synthesis.md's `generated_by` frontmatter field. Compounding irony: this feature is *designing* the execution pipeline's "no silent failures" discipline (extending ADR-0029 + ADR-0030 patterns), and the discipline failure was in the working artifacts of the design effort itself. The prior archive's `audit-findings-remediation-r1/observations.md` OBS-PLAN-001 entry surfaced exactly this same pattern in plan-v1.md, which should have been a stronger prior signal. Remediation: patch-level version bumps on both files (synthesis.md v1.0.0 → v1.0.1; codebase-analysis.md v1.1.0 → v1.1.1) with explicit `amendment_log` entries. This entry serves as the symmetric self-application of ADR-0029's "no silent failures" discipline to claude's own working artifacts. Cross-artifact audit should verify no stage-number references remain in the synthesis or codebase-analysis after patch application.

## Synthesis completion checklist

- [x] All 18 substantive Blueprint decisions framed as D-1 through D-18 (with D-2 split into D-2a-d). D-15 added 2026-05-22T04:18:00Z; D-16/D-17/D-18 added 2026-05-22T04:30:00Z post-pressure-test.
- [x] Dependency clusters identified (Joint architectural-shape trio, Orchestration, Sub-agent shape, FR-3 + FR-12 cluster, Reconciliation + state-transition, Boundary, Independent, Enforcement, Vocabulary)
- [x] Joint architectural-shape framing (D-6 + D-9 + D-10) replaces solo-keystone framing
- [x] D-1 re-framed to remove misapplied ai-development-guide 4-phase option
- [x] Deliberation sequence proposed (5 passes; integrates all 18 decisions)
- [x] Mechanical applications enumerated (4 items; #2 conditional on D-15)
- [x] Cross-cutting design implications captured (single-layer feature; composer Qs; Plan-stage Qs)
- [x] Scope deviations surfaced for cross-artifact audit (5 items including self-applied discipline-5 failure)
- [x] FR-coverage check: all 13 PRD FRs cross-referenced in at least one decision. **Process note**: the pressure-test review identified FR-5 → D-16, FR-11 → D-18, FR-12 → D-17 as missing (caught at v1.0.2 → v1.1.0). The mechanical FR-coverage check applied post-pressure-test caught 3 ADDITIONAL gaps that the eyeball review missed: FR-1, FR-8, FR-13 had no explicit cross-reference. Fixed by adding FR-1 mention to the joint architectural-shape preface, FR-8 mention to D-3, FR-13 mention to D-5. This is direct substrate for D-15's "mechanical defenses catch what eyeballs miss" argument — the very check I named at the end of the pressure-test found errors the pressure-test review didn't.
- [x] No external research topics consumed; lightweight fan-in justified per precedent
