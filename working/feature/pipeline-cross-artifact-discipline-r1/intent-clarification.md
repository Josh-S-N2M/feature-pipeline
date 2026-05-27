---
id: IC-pipeline-cross-artifact-discipline-r1
version: 0.1.0
status: draft
doc_type: intent-clarification
feature_slug: pipeline-cross-artifact-discipline-r1
user_token: <pending — recorded at Intent Confirmation Gate>
generated: 2026-05-26T12:38:37Z
generated_by: intake-intent-clarifier
---

# Intent Clarification: Cross-Artifact + Design-Time Discipline (R2)

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

This document captures user intent for the second-run hardening of the feature pipeline following the `devcontainer-mcp-provisioning-r1` shipment incident. It is the gating artifact between the user's consolidated R2 brief and the PRD that the next stage will author. It is not a requirements document and not a design document — it pins down what the user wants the pipeline to start doing differently, with ambiguities surfaced, before any FR/AC or per-layer design work begins.

## Source

User's consolidated R2 brief, delivered as the orchestrator's `raw_request` for run `pipeline-cross-artifact-discipline-r1-20260526-123837`. The brief is itself a synthesis across three pre-existing Issue records, treated here as authoritative prior context:

- `Issues/cross-artifact-divergence-detection-gap/analysis.md` plus its companion `proposal.md` and `evidence/` directory — the H-mechanism family (H1, H3, H6, H8, H9). Captures the unified pattern that gates check artifacts in isolation rather than in relation, with two grounded instances (PV-1 spec-vs-templates divergence and the MCP 5-of-7-servers-broken shipment).
- `Issues/per-agent-design-evaluation-gap/analysis.md` — the B-mechanism family (B1, B2, B3, B4, B5). Captures the pipeline's supply-driven (not demand-driven) treatment of the agent surface and the absence of skill-coverage checks at synthesis/design time.
- `Issues/devcontainer-mcp-provisioning-r1-deferrals/register.md` — the §O posture observation. Captures the project's pattern of writing time-based "post-ship / N days post-ship" triggers that have no firing mechanism, naming the specific rows (E-3, A-3, D-5, I-1) that should switch to event-triggered or honest-acceptance framings.

Verbatim user thesis from the brief: *"the pipeline must verify relationships across artifacts, not just per-artifact correctness — cancels the structural defect-class behind r1's shipment and the recurrence risk every agent-surface feature inherits."*

Note: this run is not seeded by an outside-pipeline `Issues/<topic>/proposal.md` forwarded as `--raw-request`. It is a normal feature run whose brief consolidates three Issue records by reference; the proposal-seed Phase 0 detection does not apply.

## Initial Interpretation

The user is asking for a single feature that ships approximately 11 mechanisms which together implement one thesis: the pipeline should verify *relationships across artifacts*, not just per-artifact internal correctness. The mechanisms span three pre-existing root-cause analyses but converge on Claude Code surfaces only (KB-cc-design, the recipe-feature-pipeline skill, the design-cc agent, the discovery-codebase-researcher agent, the review-architecture-auditor agent, the auditing-subagents and auditing-mcp skills, and the PV-author rubric). The user has explicitly bundled them, named the watch-item (potential R2a/R2b split if synthesis explodes the open-item count past the 4-cycle reconciliation cap), and excluded H2 (the orchestrator-driven Codespace rebuild loop) as future R4 scope. The user has also chosen the scope class implicitly via the mechanism count and cross-pipeline reach — likely FULL, possibly MINOR if the per-mechanism implementations stay narrowly scoped.

## Clarifying Questions and Answers

Auto Mode is active and the brief plus its three source Issue dirs are unusually complete: the user has named the mechanisms, their sources, their costs, the in-scope layer, the out-of-scope item, and the split contingency. No question's answer is strictly necessary to write this document — the reasonable call on each potential ambiguity is recorded below as the inference and surfaced as an Open Item for explicit user confirmation at the Intent Confirmation Gate.

| # | Ambiguity | Question that would have been asked | Inferred answer (from brief + source Issues) | Resolved? |
|---|---|---|---|---|
| 1 | Is this one feature or two from the start (R2a design-time discipline / R2b gate-and-validator hardening)? | "Do you want a single PRD covering all ~11 mechanisms, or two PRDs from the outset?" | One feature. The user's brief explicitly bundles them under one thesis and frames the split as a contingency to "surface to me at the PRD or Design Composition gate if the open-item count threatens the cap." Default to single; let synthesis re-raise if the cap is at risk. | [x] |
| 2 | Scope class — MINOR or FULL per KB-documentation-criteria rubric? | "Which scope class should this run carry — MINOR or FULL?" | FULL. The mechanism count (~11), the multi-stage reach (discovery, synthesis, design, audit, validator authoring), the cross-pipeline thesis, and the explicit posture change (§O) all push past MINOR's "bounded, 1–2 day" envelope. Recorded as an Open Item for PRD confirmation. | [x] |
| 3 | Is the §O posture change a discipline-text-only edit or does it touch existing artifacts? | "Should §O cause edits to E-3, A-3, D-5, and I-1 in the existing deferral register, or only set the going-forward posture?" | Discipline-text-only. The register's §O.5 records the user's Gate-4-v3 direction explicitly: "no changes to the feature scope. Blueprint v3 keeps the '90 days post-ship' phrasing in OI-6 and the Risks-table cold-cache row verbatim. The pattern observation is captured here as the project's posture going forward; future features adopt it, this feature ships as-designed." So R2 establishes the posture in the relevant KB / discipline texts; it does not retroactively rewrite the register rows. | [x] |
| 4 | Does H1 rename `--with-runtime` or add `--with-mcp-reachability` as a new flag? | "Rename the existing flag or introduce a sibling?" | Rename. The brief says verbatim "H1 — --with-mcp-reachability audit flag (rename --with-runtime)." | [x] |
| 5 | Is the agent-roster-impact-matrix.md artifact (B1) mandatory for *any* feature touching agents, or only when the activation is on a specific dimension? | "Trigger: any `.claude/agents/*.md` touch, or only `tools:` changes?" | Any touch of the agent surface (the four dimensions named in the per-agent-design-evaluation-gap analysis: `tools:`, `skills:`, `model:`, `effort:`, or the prompt body). The analysis §2 frames the gap as a four-dimension pattern, not a tools-only pattern. | [x] |

None of the rows required a live `AskUserQuestion` invocation under Auto Mode. The Intent Confirmation Gate will be the user's first opportunity to redirect any inference recorded above.

## Clarified Intent

Ship a single feature that makes the pipeline verify *relationships across artifacts* — both at gate time (so a shipped artifact cannot diverge from the ADR that prescribed it) and at design time (so a feature touching the agent surface cannot ship without explicit per-agent evaluation, and a feature introducing a new domain concept cannot ship without naming or justifying a skill that covers it). The feature bundles approximately 11 mechanisms drawn from three converging root-cause analyses, but its central commitment is structural: the pipeline's existing per-artifact internal-consistency checks remain unchanged, and a new layer of cross-artifact and cross-stage relational checks is added on top. The work is Claude Code only — KB-cc-design, the recipe-feature-pipeline skill, the design-cc agent, the discovery-codebase-researcher agent, the review-architecture-auditor agent, the auditing-subagents and auditing-mcp skills, and the PV-author rubric — and explicitly does not touch CI/CD, infrastructure, devcontainer rebuild orchestration, or any product-surface layer. The §O posture (replace "post-ship / N days post-ship" deferral triggers with event-triggered or honest-acceptance framings) is captured as a going-forward discipline-text change, not a retroactive rewrite of the existing devcontainer-mcp-provisioning-r1 register.

## Scope Posture

### What's in scope

The ~11 mechanisms named in the consolidated brief, grouped by source:

**From `Issues/cross-artifact-divergence-detection-gap/` (H-family):**
- **H3** — Add a design-realization audit dimension to `review-architecture-auditor`: when an ADR prescribes a concrete file or command, the auditor verifies the eventual file matches.
- **H6** — Require a §Protocol Conformance subsection in `discovery-codebase-researcher` output for each external interface in scope. (The MCP feature missed this.)
- **H9** — Add a phase-validator-tier cross-file consistency invariant catalog: every phase declares the relationships its deliverables share, with one assertion per relationship. Updates the PV-author rubric prompt.
- **H1** — Rename the existing `--with-runtime` audit flag to `--with-mcp-reachability` and have it perform a live handshake against each MCP server.
- **H8** — Live tool-surface drift detection: catch when an MCP server's tool list changes upstream.

**From `Issues/per-agent-design-evaluation-gap/` (B-family):**
- **B1** — Make `agent-roster-impact-matrix.md` a mandatory artifact whenever a feature touches the agent surface (the four dimensions `tools:`, `skills:`, `model:`, `effort:`, plus the prompt body).
- **B2** — Strengthen KB-cc-design Principle 9 from defensive ("we didn't change anything") to active ("we evaluated every agent and recorded the conclusion").
- **B3** — Add a skill-coverage check at Synthesis / Design: every new domain concept the feature introduces must name an existing skill, propose a new one with a why/how/anti-patterns trifecta justification, or document why no skill is warranted.
- **B4** — Enforce "Blocks downstream" markers the research stage can already write as actual stage-transition gates.
- **B5** — Add an `auditing-subagents` rule that catches a missing agent-roster matrix before deliverable packaging.

**From `Issues/devcontainer-mcp-provisioning-r1-deferrals/` (§O posture):**
- **§O posture** — Going forward, the relevant discipline texts (KB-cc-design, the deferral / open-items conventions, the PV-author rubric) replace "post-ship / N days post-ship" time-based deferral triggers with event-triggered or honest-acceptance framings. Captures the user's Gate-4-v3 direction so future features inherit the posture.

### What's NOT in scope (explicitly excluded)

- **H2** — Orchestrator-driven Codespace rebuild loop. The brief excludes this verbatim ("high cost, orthogonal, postmortem's own roadmap defers it. Treat as future R4 if felt-need emerges").
- **Retroactive rewriting of the devcontainer-mcp-provisioning-r1 register's §O.1 rows** (E-3, A-3, D-5, I-1). Per the register's own §O.5, the user already decided "no changes to the feature scope" for that prior feature. R2 establishes the going-forward posture in the discipline texts; it does not edit the existing register entries.
- **The five quick-win mechanisms already adopted by `pipeline-quickwins-hardening-r1`** (verdict-vs-findings consistency, single-agent-fallback ban for FULL features, `.mcp.json` ↔ install-taxonomy parity rule, GitNexus install smoke test, CI `claude mcp list` smoke test). These ship in the parallel quick-wins run; R2 is the deferred follow-on the proposal explicitly carves out. R2 must not duplicate.
- **Any non-Claude-Code layer.** The user's brief states "Layer Scope = Claude Code only." Frontend, Backend, API, Query, Database, CI/CD, IaC, and Codespaces are out-of-scope by direction.
- **Authoring new pipeline sub-agents** for any of the mechanisms. Per the per-agent-design-evaluation-gap analysis §6.3, the explicit non-recommendation is "a new sub-agent dedicated to agent-roster review. The existing `design-cc` is the correct owner." Same principle applies broadly: existing agents and skills are the owners; this feature modifies their contracts and disciplines, not the agent inventory.
- **Splitting the Claude Code layer** into sub-layers (also per the per-agent-design-evaluation-gap analysis §6.3 non-recommendation).
- **Pure issue-management hygiene** (e.g., closing the source Issues' status fields). Out-of-band to the pipeline run; happens after deliverable packaging if at all.

### What's undecided (deferred to PRD or later)

- **Q1 from the H-family analysis** — Is H9 (PV-tier cross-file invariants) authored as a new per-PV section in each phase validator (denormalized) or as a centralized `cross-file-invariants.md` reference cited by each PV (normalized)? Synthesis / Design Composition decides.
- **Q2 from the H-family analysis** — Does H3 (design-realization audit dimension) require ADRs to ship an `adr_prescriptions.yaml` companion file (machine-checkable), or extract prescriptions via NLP-style parsing of ADR prose? Synthesis / Design Composition decides.
- **Whether the feature splits into R2a (design-time discipline: B1+B2+B3+B4+B5+H3) and R2b (gate/validator hardening: H1+H6+H8+H9+§O)** if synthesis surfaces too many distinct decisions for the 4-cycle reconciliation cap. The user has named this watch-item explicitly. The PRD author should track open-item count; the Design Composition stage should surface to the user at gate time if the cap is at risk.
- **Granularity of the B1 per-agent-evidence cell** — "no change" as a valid value vs requiring positive evidence ("no responsibility intersect with feature scope"). Open Question 2 from the per-agent-design-evaluation-gap analysis §7.
- **Whether `auditing-skills` gets a reverse-check** parallel to B5 (when a new skill is authored, audit whether existing agents' `skills:` arrays should include it). Open Question 5 from the per-agent-design-evaluation-gap analysis §7.
- **What exactly counts as "touching the agent surface" for B1's trigger** — agent file edits clearly count; new skill that some agents will load probably counts; MCP server tool surface change almost certainly counts. Open Question 1 from the per-agent-design-evaluation-gap analysis §7.
- **Scope class confirmation** — MINOR or FULL. The Initial Interpretation infers FULL; the PRD author confirms against KB-documentation-criteria's scope-class rubric.

## Stakeholder Posture (Preliminary)

- **Pipeline maintainer (the user, primary):** Wants the structural defect-class behind the r1 shipment cancelled so future agent-surface features don't inherit the same recurrence risk. The thesis ("verify relationships, not just per-artifact correctness") is theirs.
- **Future feature authors (downstream consumers):** Inherit the new disciplines automatically — they will be asked to produce agent-roster impact matrices, skill-coverage justifications, and protocol-conformance subsections. Care about the burden being proportionate to the benefit.
- **Future reviewers (`review-architecture-auditor`, phase-quality reviewers, audit skills):** Inherit new check dimensions. Care about the new checks being machine-checkable or at least mechanically inspectable, not subjective.
- **Future synthesis and design composer agents:** Inherit the skill-coverage decision frame at Synthesis. Care about not having to invent the rubric per-feature.

## Success Posture (Preliminary)

The user will know this feature is working when, on the next feature run that touches the agent surface (whichever feature that is, whenever it happens), all four observable conditions hold simultaneously:

1. The pipeline refuses to advance past Design Composition without an `agent-roster-impact-matrix.md` authored against the then-current agent inventory.
2. Every new domain concept the feature introduces is paired with a skill-coverage decision (named existing skill, proposed new skill with W/H/A trifecta, or recorded "no skill warranted" rationale).
3. `review-architecture-auditor` flags any ADR prescription whose eventual implementation diverges from the prescription, surfacing the divergence as a blocking finding rather than approving the artifact.
4. No new "post-ship / N days post-ship" deferral language appears in any artifact authored by the new run; deferrals either name an event trigger or accept the cost honestly.

These are postures, not yet acceptance criteria. The PRD author formalizes them into FRs/NFRs and the Blueprint into AC-FR-N-x rows.

## Confirmation

Awaiting user confirmation at the Intent Confirmation Gate. The orchestrator's `AskUserQuestion` at the gate will record the `user_token` that propagates into PRD authoring and downstream stages.

## Open Items (Pending PRD Authoring)

The following items need explicit resolution by the PRD author (some carried forward from the Scope Posture's "undecided" section, plus the inferred answers from the Clarifying Questions table that the user should confirm or correct at the gate):

- **OI-1** — Single feature vs split (R2a/R2b). Inferred answer: single feature, with synthesis re-raising the split if the open-item count threatens the 4-cycle reconciliation cap. PRD author tracks the count from the start and surfaces to the user at PRD or Design Composition gate if the cap is at risk.
- **OI-2** — Scope class. Inferred answer: FULL. PRD author validates against KB-documentation-criteria's scope-class rubric and records in the PRD's scope-class frontmatter field.
- **OI-3** — H9 denormalized-vs-normalized authoring shape (per-PV section vs centralized reference). Defer to Synthesis / Design Composition.
- **OI-4** — H3 machine-checkable companion file vs NLP prescription extraction. Defer to Synthesis / Design Composition.
- **OI-5** — B1 per-agent-evidence-cell granularity (structural-only vs positive-evidence-required). PRD author proposes a default; Design Composition can revise.
- **OI-6** — B1 trigger granularity: precisely what counts as "touching the agent surface." PRD author drafts the precise trigger condition; the per-agent-design-evaluation-gap analysis §7 Open Question 1 enumerates the candidates.
- **OI-7** — Reverse-check for `auditing-skills` (parallel to B5 on the skills dimension). PRD author decides whether to fold this into B5's scope or carry as an Open Question for the Blueprint.
- **OI-8** — Watch-item for the 4-cycle reconciliation cap. The brief flags ~11 mechanisms across 3 source issues as potentially explosive at synthesis time. The PRD author tracks open-item count across stages and the Design Composer surfaces a split recommendation if the cap is at risk; natural split per the brief is R2a (design-time: B1+B2+B3+B4+B5+H3) and R2b (gate/validator: H1+H6+H8+H9+§O).

---

*End of intent clarification. Awaiting Intent Confirmation Gate before PRD authoring proceeds.*
