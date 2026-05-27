---
id: IC-pipeline-design-time-discipline-r1
version: 1.0.0
status: draft
doc_type: intent-clarification
feature_slug: pipeline-design-time-discipline-r1
scope_class: minor
derived_from: split-record
parent_run: pipeline-cross-artifact-discipline-r1
split_record_path: working/feature/pipeline-cross-artifact-discipline-r1/SPLIT-RECORD.md
inherited_adrs: [ADR-0059, ADR-0061, ADR-0063]
adr_range_reserved: 0064-0069
user_token: pending
generated: 2026-05-26T16:23:13Z
generated_by: intake-intent-clarifier
---

# Intent Clarification: Pipeline Design-Time Discipline (R2a)

## Contents

Section completion checklist — each box must be checked (including `N/A — out of scope` rows) before this document leaves draft. The reviewer's Gate 0 check uses this list as the structural-presence anchor.

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

Capture the user's intent for the R2a follow-up run of the terminated parent `pipeline-cross-artifact-discipline-r1` before any new PRD or design work begins. R2a ships the **design-time discipline** half of the parent's split (6 of the original 11 mechanisms). The companion R2b run will follow with the gate/validator hardening half. This document scopes the inherited PRD scaffolding, inherited ADRs, and the self-application ("eat own dogfood") discipline that this run uniquely introduces.

## Source

The raw request for this run, verbatim:

> R2a — design-time discipline half of the R2 split. Inherits from the terminated parent run `pipeline-cross-artifact-discipline-r1`.
>
> Mechanism subset for this run (6 of the original 11):
> - FR-1 (H3) — Design-realization audit dimension for review-architecture-auditor: when an ADR prescribes a concrete file/command, the auditor verifies the eventual file matches. Companion-file path per inherited ADR-0059.
> - FR-6 (B1) — Mandatory agent-roster-impact-matrix.md artifact contract whenever a feature touches the agent surface (four-dimension trigger: tools, skills, model, effort, prompt body).
> - FR-7 (B3) — Skill-coverage decision check at Synthesis/Design: every new domain concept the feature introduces must name an existing skill, propose a new one with W/H/A trifecta, or document why no skill is warranted.
> - FR-8 (B2) — KB-cc-design Principle 9 active reframing: from defensive ("we didn't change anything") to active ("we evaluated every agent and recorded the conclusion").
> - FR-9 (B4) — Blocks-X marker grammar canonicalization (n=1 prior occurrence — establishing the grammar). Per inherited ADR-0063.
> - FR-10 (B5) — auditing-subagents rule that catches a missing agent-roster matrix before deliverable packaging.
>
> Out of scope for this run (assigned to R2b follow-up):
> FR-2 (H6), FR-3 (H9), FR-4 (H1), FR-5 (H8), FR-11 (§O).
>
> Inherited ADRs: ADR-0059, ADR-0061, ADR-0063. ADR numbering: reserve 0064-0069 for this run. Layer Scope: Claude Code only.

Authoritative prior-context source: [SPLIT-RECORD.md](../pipeline-cross-artifact-discipline-r1/SPLIT-RECORD.md). The parent run's intent-clarification, prd-v2, synthesis, codebase-analysis, blueprint, and the five accepted ADRs are reference inputs per the SPLIT-RECORD's "Artifacts the follow-up runs can inherit" table.

Origin issue dirs (authoritative for mechanism framings):
- `Issues/per-agent-design-evaluation-gap/` — origin of B1/B2/B3/B4/B5 (this run's FR-6/8/7/9/10).
- `Issues/cross-artifact-divergence-detection-gap/` — origin of H3 (this run's FR-1).

This is a NORMAL feature run, not a proposal-seeded invocation (the SPLIT-RECORD is the prior-context source but is not a `Issues/<topic>/proposal.md`).

## Initial Interpretation

The user is reconstituting the design-time-leaning half of an 11-mechanism feature that was split at Gate 4 of the parent run because the open-item count threatened the cross-artifact-audit's 4-cycle reconciliation cap. The six mechanisms in this run share a common shape: each adds a **design-time check, contract, or grammar** that the pipeline currently lacks. They cluster around two themes: (a) **architectural audit hardening** (FR-1 design-realization audit, FR-9 marker grammar) and (b) **per-agent design evaluation discipline** (FR-6 agent-roster matrix contract, FR-7 skill-coverage decision check, FR-8 Principle 9 active reframing, FR-10 the audit rule that enforces FR-6). This run inherits three already-accepted ADRs (0059, 0061, 0063) and a populated PRD/Blueprint scaffold from the parent — the run is mostly about **scoping down** to the design-time subset, not about re-deriving from scratch. The Layer Scope is Claude Code only. The run uniquely faces an **eat-own-dogfood** condition: it both *establishes* the FR-6 mandatory matrix contract AND must itself deliver an agent-roster impact matrix as one of its artifacts.

## Clarifying Questions and Answers

Per Auto Mode, no clarifying questions were posed via AskUserQuestion. The inferences the user may want to redirect at the Intent Confirmation Gate are surfaced explicitly below; each row records an inferred answer that the user can override.

| # | Ambiguity | Inferred Answer (Auto Mode) | Resolved? |
|---|---|---|---|
| 1 | Should scope_class be MINOR or MAJOR given 6 mechanisms vs the parent's 11, mostly-inherited decisions, and ~3 new ADRs reserved (0064-0066)? | **MINOR** — bounded mechanism count, prior decisions resolved by inherited ADRs, single layer (Claude Code only), and inherited PRD scaffolding mean this run does not meet the MAJOR threshold. PRD author validates against the rubric. | [x] |
| 2 | What is the FR-6 agent-roster matrix's coverage at runtime (how many agents must the matrix evaluate)? | **37 agents** as of 2026-05-26 (verified via `.claude/agents/*.md` glob in this run's working directory). NFR-7 from the parent's PRD assumes 100-agent budget; the 37-agent reality remains within budget by 2.7×. | [x] |
| 3 | Which "domain concepts" introduced by this run must themselves pass FR-7's skill-coverage decision (the self-application question)? | **Six concepts** this run introduces: (a) design-realization audit dimension; (b) agent-roster impact matrix; (c) skill-coverage decision check; (d) Principle 9 active reframing; (e) Blocks-X marker grammar; (f) agent-roster matrix-missing audit rule. Each gets a W/H/A trifecta decision (existing skill / propose new / explicitly no skill) at Synthesis or Design. | [x] |
| 4 | Does this run author the severity-vocabulary bridge-table content (D-10 from the parent's synthesis, anchored by inherited ADR-0061), or defer to R2b? | **This run authors the bridge content** at `KB-review-disciplines/references/severity-taxonomy.md`. Rationale: SPLIT-RECORD's "R2a-runs-first" ordering recommendation #2 — running R2a first gives R2b a populated bridge table to inherit; deferring would invert that. | [x] |
| 5 | Should the queued R2b run be referenced explicitly in this run's PRD (as a "blocks" / "blocked-by" relationship), or treated as out-of-scope context only? | **Out-of-scope context, with a single forward-reference in PRD's Open Items.** Rationale: this run must stay self-contained for its own Plan/Test/Audit phases; R2b's mechanisms are not preconditions for this run's deliverables. The SPLIT-RECORD already documents the lineage for archeological reading. | [x] |
| 6 | Are decisions D-1 (companion file), D-3 (auditing-skills reverse-check), D-4 (Blocks-X grammar), D-5 (FR-6 trigger mechanical-evaluator hybrid), and D-8 (W/H/A substance vs mandate) from the parent's synthesis inherited verbatim, or re-derived? | **Inherited as resolved decisions**, cited in this run's Blueprint as such. D-1 → resolved by ADR-0059. D-4 → resolved by ADR-0063. D-3, D-5, D-8 → carried as decided synthesis claims feeding the Blueprint. Only D-10 (severity bridge) requires authoring work in this run (per row 4). | [x] |
| 7 | Does the eat-own-dogfood discipline (this run authors an agent-roster impact matrix for itself) become a PRD requirement, or is it a process discipline outside the PRD? | **Both.** FR-6's AC requires the matrix to be authored for any feature touching the agent surface; this run touches the agent surface (it adds the FR-10 audit rule and modifies reviewer/composer agents to honor FR-1/6/7/8). Therefore the matrix is a deliverable of this run, exercising the very contract FR-6 establishes. The PRD's Deliverable Archive section names the matrix as an artifact. | [x] |

If the user wants any of these inferences overridden at Gate 1, the orchestrator's Intent Confirmation Gate is the right pause point; the inferences above are auto-mode best calls, not user-confirmed answers.

## Clarified Intent

Ship the six design-time-discipline mechanisms from the parent's split — FR-1, FR-6, FR-7, FR-8, FR-9, FR-10 — as a self-contained MINOR-scope feature run, inheriting ADR-0059 (companion file), ADR-0061 (severity bridge), and ADR-0063 (Blocks-X grammar) and reserving ADR numbers 0064-0069. The run hardens two adjacent disciplines: (1) the **review-architecture-auditor**'s design-realization audit dimension (FR-1) and the canonical Blocks-X marker grammar that audit consumes (FR-9), plus the audit rule that enforces matrix presence at packaging (FR-10); and (2) the **per-agent design-evaluation contract** comprising the mandatory `agent-roster-impact-matrix.md` artifact (FR-6), the Synthesis/Design skill-coverage decision check (FR-7), and the KB-cc-design Principle 9 active reframing (FR-8). Layer scope is Claude Code only. The run additionally authors the severity-vocabulary bridge-table content (closing parent decision D-10 via the inherited ADR-0061) so that R2b inherits a populated bridge. The run applies its own FR-6/FR-7 contracts to itself: it authors an agent-roster impact matrix as a deliverable and performs a W/H/A skill-coverage decision for each new domain concept it introduces.

## Scope Posture

### What's in scope

- **FR-1** — design-realization audit dimension for `review-architecture-auditor`; reads the companion `.prescriptions.yaml` (per ADR-0059) for any ADR that prescribes a concrete file/command and verifies the realized artifact matches the prescription. Inherits NFR-1 (auditor 5000ms budget) from parent PRD.
- **FR-6** — mandatory `agent-roster-impact-matrix.md` artifact contract; the four-dimension trigger (tools, skills, model, effort, prompt body — five dimensions per parent raw-request enumeration, but the parent's PRD treats prompt-body changes as part of the four-dimension matrix). Inherits NFR-7 (30-min budget at 100 agents — 37 agents today, within budget).
- **FR-7** — skill-coverage decision check at Synthesis and Design stages; every new domain concept must name an existing skill, propose a new one with W (what), H (how), A (audience) trifecta, or document why no skill is warranted.
- **FR-8** — KB-cc-design Principle 9 active-reframing edit: replace defensive "we didn't change anything" with active "we evaluated every agent in the roster and recorded the conclusion (change / no change with reason)."
- **FR-9** — Blocks-X marker grammar canonicalization per inherited ADR-0063 (n=1 prior occurrence in the codebase; this run establishes the canonical grammar for future occurrences). Inherits NFR-9 (grep-checkable affordance).
- **FR-10** — `auditing-subagents` rule that catches a missing agent-roster impact matrix during the deliverable-packaging review, before archive sealing.
- **D-10 bridge-table content** — author the severity-vocabulary bridge at `KB-review-disciplines/references/severity-taxonomy.md` per inherited ADR-0061, so that R2b inherits a populated bridge.
- **Eat-own-dogfood deliverables** — this run produces (a) its own `agent-roster-impact-matrix.md` exercising the FR-6 contract, and (b) explicit FR-7 skill-coverage decisions for each new domain concept it introduces.

### What's NOT in scope (explicitly excluded)

- **FR-2 (H6) Protocol Conformance subsection** — assigned to R2b.
- **FR-3 (H9) cross-file consistency invariant catalog** — assigned to R2b.
- **FR-4 (H1) `--with-mcp-reachability` rename + handshake** — assigned to R2b.
- **FR-5 (H8) live tool-surface drift detection** — assigned to R2b.
- **FR-11 (§O) event-triggered deferral discipline including the ratified 5-row enumeration (A-3, D-5, E-2, E-3, I-1)** — assigned to R2b.
- **Re-deriving the inherited ADRs (0059, 0061, 0063)** — these are accepted; this run cites them, does not re-author them.
- **Re-deriving the parent run's synthesis decisions D-1, D-3, D-4, D-5, D-8** — these are inherited as resolved.
- **Re-running the parent's codebase research** — the 21 components / 21 dependency edges / blast-radius reading is inheritable per SPLIT-RECORD. This run's `discovery-codebase-researcher` may layer on only what FR-1/6/7/8/9/10 specifically need.
- **Any layer other than Claude Code** — frontend, backend, API, query, database, IAC, CI/CD, codespaces are explicitly out of scope.
- **Cross-run state-transition coordination with R2b** — the R2b run is a separate pipeline invocation; this run does not gate on it.

### What's undecided (deferred to PRD or later)

- Exact text of the FR-8 Principle 9 active-reframing edit (PRD-stage authoring).
- Exact grammar surface of FR-9 Blocks-X (ADR-0063 sets the spirit; the grammar's regex/parsing surface is a Design-stage detail).
- Whether the FR-10 `auditing-subagents` rule is added as a new rule entry or extends an existing rule's predicate (Design-stage).
- Whether FR-7's skill-coverage decision check produces a standalone artifact or appends to the synthesis/design documents (Design-stage).
- The exact ordering between authoring the severity-vocabulary bridge content and the FR-1/9/10 sections that consume it (Plan-stage sequencing).

## Stakeholder Posture (Preliminary)

- **Pipeline maintainer (user):** wants the design-time-discipline half shipped on an independent timeline from the gate/validator hardening half, with R2b unblocked by R2a's bridge-table authoring.
- **`review-architecture-auditor` sub-agent:** gains a new audit dimension (FR-1) and a canonical marker grammar to parse (FR-9); needs the work to stay within NFR-1's 5000ms latency budget.
- **`design-composer` sub-agent:** gains the FR-6 matrix-authoring responsibility and the FR-7 skill-coverage decision responsibility for any feature touching the agent surface.
- **`finalize-deliverable-packager` sub-agent:** gains the FR-10 matrix-presence check via `auditing-subagents`.
- **Future feature runs:** every future feature that touches an agent now owes a matrix, a skill-coverage decision per new concept, and audit-realizable ADRs — design-time cost rises slightly, ambiguity downstream drops.
- **R2b queued run:** depends on this run for the populated severity-vocabulary bridge table and for the matrix contract it will itself exercise.

## Success Posture (Preliminary)

This run is "done" when: (a) the six FRs land with PRD ACs satisfied and Plan tasks closed; (b) the severity-vocabulary bridge at `KB-review-disciplines/references/severity-taxonomy.md` is populated and cited by ADR-0061; (c) this run's own `agent-roster-impact-matrix.md` is produced as a deliverable, demonstrating the FR-6 contract on itself; (d) skill-coverage decisions are recorded for each of the six new domain concepts this run introduces, demonstrating FR-7 on itself; (e) the Gate 4 Blueprint Approval passes without a re-split (the 4-cycle reconciliation cap is comfortable at 6 mechanisms); (f) downstream R2b can cite this run's bridge table and FR-6 matrix-contract artifacts as inherited prior context.

## Confirmation

The orchestrator's Intent Confirmation Gate captures the user's confirmation token, which replaces `user_token: pending` in this document's frontmatter. The user is expected to redirect any of the 7 Auto-Mode inferences in the "Clarifying Questions and Answers" table at this gate if needed.

## Open Items (Pending PRD Authoring)

- **OI-1.** PRD author must validate the inferred `scope_class: minor` against the canonical rubric and either confirm or upgrade to `major`. Confirmation likely; mechanism count and decision-inheritance support MINOR.
- **OI-2.** PRD author must inherit the parent's PRD FR-1, FR-6, FR-7, FR-8, FR-9, FR-10 sections + ACs + relevant NFRs (NFR-1 5000ms auditor; NFR-7 30-min matrix at 100 agents; NFR-9 grep-checkable affordance) and slim down to this run's scope; the other FR sections must be removed cleanly with no dangling cross-references.
- **OI-3.** PRD author must add a Deliverable Archive entry for this run's own `agent-roster-impact-matrix.md` and for the FR-7 skill-coverage decisions of the six new concepts, making the eat-own-dogfood discipline visible in the deliverable contract.
- **OI-4.** PRD author must add a Deliverable Archive entry for the severity-vocabulary bridge content at `KB-review-disciplines/references/severity-taxonomy.md` (closing parent D-10), since this run ships the bridge first per SPLIT-RECORD ordering.
- **OI-5.** PRD author must surface the relationship to R2b once in Open Items / Cross-Run Context (single forward reference; R2b is not a blocking dependency from this run's direction).
- **OI-6.** Discovery / Synthesis must verify the current agent-roster count (37 verified at intent-clarification time, 2026-05-26) feeds the FR-6 NFR-7 budget realistically; the 30-min-at-100-agents budget has 2.7× headroom today.
- **OI-7.** Design-stage decision: whether the FR-9 Blocks-X grammar's parser/regex implementation surface lives in the `review-architecture-auditor` agent prompt, in a shared parsing helper, or in the auditing rule itself. ADR-0063 sets the grammar; the realization location is a Design-time call.
- **OI-8.** Design-stage decision: whether FR-7's skill-coverage decision check is a synthesis-stage artifact, a design-stage artifact, or both (with the synthesis surfacing candidates and design recording the trifecta resolution). The parent's D-8 leaned toward substance-over-mandate; this run's Design composer makes the realization call.
- **OI-9.** Confirm whether the FR-6 four-dimension trigger should be stated as four dimensions (tools, skills, model, effort) with prompt-body changes folded in, or explicitly as five dimensions. Parent raw-request enumerated five; parent PRD treated as four-with-prompt-body. This run's PRD must pick one phrasing and apply it consistently.
