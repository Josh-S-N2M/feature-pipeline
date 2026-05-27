---
id: CC-DESIGN-pipeline-design-time-discipline-r1
version: 1.0.0
status: draft
doc_type: per-layer-design
feature_slug: pipeline-design-time-discipline-r1
layer: claude-code
parent_run: pipeline-cross-artifact-discipline-r1
inherited_adrs: [ADR-0059, ADR-0061, ADR-0063]
derived_from:
  - working/feature/pipeline-design-time-discipline-r1/prd-v1.md
  - working/feature/pipeline-design-time-discipline-r1/synthesis.md
  - working/feature/pipeline-design-time-discipline-r1/codebase-analysis.json
  - working/feature/pipeline-design-time-discipline-r1/codebase-analysis-report.md
  - working/feature/pipeline-design-time-discipline-r1/intent-clarification.md
predecessor: working/feature/pipeline-cross-artifact-discipline-r1/cc-design.md
generated: 2026-05-26T17:30:00Z
generated_by: design-cc
---

# Claude Code Design — Pipeline Design-Time Discipline (R2a)

## Brief-honor citation

The user's verbatim thesis from the rationale brief, which every architectural decision in this design must honor:

> "the pipeline must verify relationships across artifacts, not just per-artifact correctness — cancels the structural defect-class behind r1's shipment and the recurrence risk every agent-surface feature inherits."

This R2a design ships **six** mechanisms inside the `.claude/` configuration (FR-1, FR-6, FR-7, FR-8, FR-9, FR-10) — the design-time-discipline half of the parent run's eleven, split at Gate 4 per the user's R2a/R2b decision. The Claude Code layer is the sole activated layer; all six FRs land here.

## Inheritance posture

This document is materially shorter than the parent's 15-section design because most foundational work is inherited:

| Inherited from parent (`pipeline-cross-artifact-discipline-r1/cc-design.md`) | Status here |
|---|---|
| Brief-honor citation discipline | Re-cited verbatim above |
| FR-1 / FR-6 / FR-7 / FR-8 / FR-9 / FR-10 per-FR file-targeting | Inherited near-verbatim; R2a-specific tightening recorded below |
| Companion-file schema (D-1 → ADR-0059) | Closed by inherited ADR-0059; cited not re-authored |
| Blocks-X marker grammar (D-4 → ADR-0063) | Closed by inherited ADR-0063; cited not re-authored |
| Severity bridge table HOST (D-10 → ADR-0061) | Host fixed by inherited ADR-0061; this design authors the **content** below |
| Agent-roster matrix template + cell discipline | Inherited verbatim |
| Skill-coverage decision substance heuristic (D-8) | Inherited verbatim |
| Open Items routing to design-composer | New Q-CC-N set tailored to R2a's 6 FRs (5 questions) |

The R2a-only additions (not present in parent design) are:

1. **Severity bridge table content** — the parent established the host (KB-review-disciplines per ADR-0061); R2a authors the actual five-column mapping plus the Weight Preservation Note.
2. **Marker-parser realization location (D-R2a-3)** — `.claude/skills/auditing-shared/scripts/parse_blocks_x_markers.py`.
3. **FR-7 artifact location (D-R2a-4)** — section embedded in `synthesis.md`, not standalone file.
4. **FR-10 rule realization (D-R2a-5)** — new rule entry (SA-14), not extension of existing rule.
5. **Plan-stage sequencing recommendation (D-R2a-6)** — bridge first, then FR-1/9/10 consumers.
6. **Six explicit skill-coverage decisions** for R2a's six new domain concepts (eat-own-dogfood).
7. **Agent-roster matrix contract** for this run's 37-row deliverable.

## KBs loaded for this design pass

| KB / discipline | Why loaded |
|---|---|
| `KB-cc-platform` | Platform half — primitive syntax, frontmatter contracts, current-detail lookup chain. Anchors FR-by-FR file targeting. |
| `KB-cc-design` | Design half — lowest-cost-primitive, path-gating, enforce-vs-instruct, intentional sub-agent reasoning. FR-8 modifies Principle 9 in this KB. |
| `KB-documentation-criteria` | Template + conventions. FR-9 marker grammar already canonicalized in inherited ADR-0063. |
| `KB-review-disciplines` | FR-1 attaches a new audit dimension; D-10 bridge table content lands here (`references/severity-taxonomy.md` per ADR-0061). |
| `KB-task-decomposition` | FR-7 skill-coverage decision frame attaches at synthesis/design stages this KB references. |

## Per-FR design

Each FR section below names: (a) target file(s); (b) shape of the change; (c) decisions adopted; (d) OI(s) it closes / depends on. design-cc authors design contract, not implementation — concrete edits land at Plan / Task-Decomposition time.

### FR-1 — Design-realization audit dimension on `review-architecture-auditor`

**Decisions adopted:** D-1 (companion file = ADR-0059) + D-10 (severity bridge content authored here). **OI closures:** Parent OI-A1 closed by inherited ADR-0059.

- **Target files (per codebase-analysis mechanism_dependency_table[FR-1]):**
  - `.claude/agents/review-architecture-auditor.md` — add the new audit phase **inline** (the agent has no Agent/Task tool per ADR-0045; the new dimension fits as a new procedure phase, additive to today's 6-phase procedure).
  - `.claude/skills/KB-review-disciplines/references/architecture-audit.md` — add **Lens 4: Design Realization** alongside existing CoVe / Blast-Radius / Brief-Honor lenses.
  - `.claude/skills/KB-review-disciplines/references/severity-taxonomy.md` — author the D-10 five-column bridge table (see §Severity bridge table content below).
  - `adrs/ADR-NNNN-<slug>.prescriptions.yaml` — companion-file pattern set by inherited ADR-0059. Optional per ADR.
  - `.claude/skills/auditing-shared/scripts/validate_adr_prescriptions.py` — new linter (schema-validates companion-file YAML; verifies `adr_path` / slug match; verifies `target_path` existence).

- **Canonical example (authoring anchor):** `auditing-cc-configs/scripts/audit_op2_consumer_mapping.py` still references the removed `mcp-openapi-schema` server. This is the exact defect class FR-1 catches: ADR-0041 prescribes a 6-server `.mcp.json`; the audit script references 7. The companion file `ADR-0041-install-mechanism-hybrid.prescriptions.yaml` declares the 6-server prescription; the design-realization audit emits a `BLOCKER` finding naming (i) `ADR-0041`, (ii) the prescription (6-server expected), (iii) the diverging file (`audit_op2_consumer_mapping.py`), (iv) the diff (7-server reference). Per NFR-8, the BLOCKER carries `rule` / `target` / `divergence` / `next_action` fields.

- **Auditor-vocabulary semantics (per inherited ADR-0061 vocabulary):**
  - **Missing prescribed file** → `BLOCKER` (the prescription names a `target_path` that does not exist when it must).
  - **Schema mismatch** (target file exists but its content fails the declared `assertion`) → `MAJOR` by default; `BLOCKER` if the companion file declares `severity_floor: BLOCKER`.
  - **No companions present** in the run's ADR set → no-op diagnostic (AC-FR-1-b).

- **Lowest-cost primitive justification (Principle 1):** Procedure-phase edit on an existing agent + new content in an existing KB + new companion-file convention. No new sub-agent, no new hook, no new MCP. Companion file is structured data read by the auditor, not a Claude Code primitive — minimum-surface change.

- **Reasoning configuration justification (Principle 9, post-FR-8 active wording):** `review-architecture-auditor` retains `model: opus`, `effort: xhigh`, `memory: project`. Considered: the new design-realization dimension adds cross-document reconciliation reasoning over ADR prescriptions × implementation files; xhigh remains warranted. `skills:` list unchanged (KB-review-disciplines already loaded).

### FR-6 — Mandatory `agent-roster-impact-matrix.md` artifact

**Decisions adopted:** D-5 (hybrid advisory-predicate + human ratification for triggers 3+4) + D-8 (substance heuristic + mandate-for-structural-template). **OI closures:** Parent OI-A6 closed by D-5 (carried into R2a's OI-R2a-1).

- **Target files:**
  - `.claude/agents/design-claude-code.md` — Phase 2 extension: new mandatory output `working/feature/<slug>/agent-roster-impact-matrix.md`, conditional on the four-condition trigger. Cross-references post-FR-8 Principle 9 text.
  - `.claude/skills/recipe-feature-pipeline/SKILL.md` — outputs table for design-cc gets a third deliverable row (matrix); Design Composition close (Stage 7) gate refuses if trigger fired and matrix absent.
  - `.claude/skills/auditing-subagents/scripts/check_feature_touch_predicate.py` — new advisory predicate (D-5 hybrid). Override events log to `state-transitions.log` via existing `auditing-shared/scripts/log_state_transition.py`.
  - `.claude/skills/KB-documentation-criteria/references/templates/agent-roster-impact-matrix-template.md` — new template.
  - `.claude/skills/KB-cc-design/references/principles.md` (Principle 9) — mutual cross-reference per AC-FR-8-b.

- **Per-cell discipline (canonical schema):**

```text
<value> — <positive-evidence-string>
```

Where `<value>` is one of: `no-change` | `tools-add: <list>` | `tools-remove: <list>` | `skills-add: <list>` | `skills-remove: <list>` | `model-change: <old>→<new>` | `effort-change: <old>→<new>` | `prompt-edit: <one-line-summary>`. Bare `no-change` without a positive-evidence-string fails both the FR-6 design-time block and the FR-10 packaging-time backstop.

- **Five-explicit dimensions (per IC OI-9 resolution in PRD Product Policy):** tools, skills, model, effort, prompt body. Each row → 5 cells. At the current 37-agent inventory → 185 cells per run.

- **Lowest-cost primitive justification (Principle 1):** Extends existing agent procedure; new template in existing KB; new advisory predicate under an existing audit skill. No new sub-agent. NFR-9 grep-check passes: design-cc already loads KB-documentation-criteria.

- **Reasoning configuration justification (Principle 9):** `design-cc` retains `model: opus`, `effort: high`. Matrix authoring is bounded by NFR-7's 30-min-at-100-agents budget; effort: high covers it. No `skills:` array change.

### FR-7 — Skill-coverage check at Synthesis / Design for new domain concepts

**Decisions adopted:** D-8 (substance heuristic with mandate-for-new-skill-proposals carve-out) + **D-R2a-4 (FR-7 artifact location — embed in synthesis.md)**.

- **Target files:**
  - `working/feature/<slug>/synthesis.md` — **embed a new section** "Skill-Coverage Decisions" with one decision row per new domain concept. Per D-R2a-4, this is **not a standalone file** — embedding in synthesis.md keeps the decisions co-located with the synthesis that surfaces the concepts.
  - `.claude/skills/KB-cc-design/references/principles.md` — extend Principle 9's neighborhood with the W/H/A rubric and substance-not-presence heuristic.
  - `.claude/agents/synth-synthesizer.md` — synthesis-side trigger: when synthesis identifies a new domain concept, emit a Skill-Coverage Decisions section row.
  - `.claude/agents/design-composer.md` — Blueprint composition reads each row; blocks completion if a row is missing required justification per AC-FR-7-b.
  - `.claude/skills/KB-documentation-criteria/references/templates/` — new sub-template `skill-coverage-decisions-section-template.md` (consumed when authoring the embedded section).

- **D-R2a-4 rationale (artifact location):** Embedding in synthesis.md (a) keeps decisions with the concept-surface where they are generated, (b) avoids a sparse standalone file in runs where concepts are few, (c) reuses synthesis.md's existing review path (`shared-document-reviewer` invocation 2), and (d) leaves a single rendered location for downstream consumers (design-composer at Blueprint composition) to read. Routed to Composer as Q-CC-3 for ratification.

- **Eat-own-dogfood: this run's 6 decisions** (one per new R2a domain concept) — authored as the embedded section in synthesis.md. Per-decision rationale captured in §Skill-coverage decisions for THIS run below.

- **Lowest-cost primitive justification (Principle 1):** Discipline-text additions to existing KB + procedure extensions to existing agents + new template in existing KB. No new sub-agent. No new file when concepts are absent (the section is conditional).

- **Reasoning configuration justification (Principle 9):** Consuming agents (synth-synthesizer, design-composer, design-cc) keep current reasoning config; no rebalance needed.

### FR-8 — Strengthen KB-cc-design Principle 9 from defensive to active

**Decisions adopted:** D-8 (substance heuristic informs the active wording).

- **Target files (per codebase-analysis concentrated blast-radius — 2 sites):**
  - `.claude/skills/KB-cc-design/references/principles.md:182` — replace Principle 9's leading sentence (defensive framing) with the active framing below.
  - `.claude/agents/design-claude-code.md:56` — update verbatim citation to match new wording and add mutual cross-reference to FR-6 matrix-cell-discipline per AC-FR-8-b.

**Proposed verbatim sentence-replacement for Principle 9 leading sentence:**

Current (line 182): *"Every sub-agent's reasoning capacity is determined by three independent frontmatter fields: `model:`, `effort:`, and `skills:`. They control different things, and the Designer makes each choice deliberately — not by inheriting whatever default the carry-in template happened to use."*

**Replace with (active framing):**

> "For every agent on the touched agent surface — changed and unchanged alike — the Designer records the consideration performed on that agent's three independent reasoning fields (`model:`, `effort:`, `skills:`), even when the recorded outcome is no change. The artifact of the consideration is the `agent-roster-impact-matrix.md` cell (FR-6 of `pipeline-design-time-discipline-r1`); the matrix's positive-evidence-string discipline is the substance test for whether the consideration happened. Bare 'no change' is structurally indistinguishable from 'never evaluated' and is therefore insufficient."

The existing body of Principle 9 (field-by-field discipline on `model:` / `effort:` / `skills:`) is retained verbatim — it remains correct; only the *opening posture* shifts from defensive to active.

**Cross-reference at `.claude/agents/design-claude-code.md:56`:** Update the verbatim citation to the new active framing and add the AC-FR-8-b mutual reference: "the matrix-cell discipline (FR-6 §Per-cell discipline) is the substance test for the per-agent consideration this principle requires."

- **Lowest-cost primitive justification (Principle 1):** Concentrated 2-site edit in existing files. No new artifact.

### FR-9 — Enforce "Blocks downstream" markers as stage-transition gates

**Decisions adopted:** D-4 → **inherited ADR-0063** (canonical grammar) + **D-R2a-3 (marker-parser realization location)**.

- **Target files (per codebase-analysis mechanism_dependency_table[FR-9]):**
  - `.claude/skills/KB-documentation-criteria/references/blocks-x-marker-grammar.md` — already canonicalized by inherited ADR-0063. R2a does not re-author the grammar; it cites ADR-0063.
  - `.claude/skills/auditing-shared/scripts/parse_blocks_x_markers.py` — **new helper** implementing the canonical parser (per D-R2a-3 below). One source of truth for the regex; consumed by orchestrator gating and any audit rule that needs to enumerate markers.
  - `.claude/agents/discovery-codebase-researcher.md` — emission site: when discovery surfaces a question whose answer is required before a named stage can complete, emit the marker per the ADR-0063 grammar.
  - `.claude/agents/execute-orchestrator.md` — gating logic at stage-transition checkpoints: invoke `parse_blocks_x_markers.py` to enumerate markers from upstream outputs; refuse to mark the named stage complete until each marker has transitioned.
  - `.claude/skills/recipe-feature-pipeline/SKILL.md` — checkpoint logic reference.
  - `.claude/skills/KB-documentation-criteria/references/templates/state-transitions-log-entry-template.md` — extend `transition_name` enumeration with the three values reserved by ADR-0063: `BLOCKS_X_RESOLVED`, `BLOCKS_X_DEFERRED_WITH_OI`, `BLOCKS_X_FALSE_POSITIVE`.
  - `.claude/skills/auditing-shared/scripts/log_state_transition.py` — accepts the new `transition_name` values without code change (free-string per ADR-0044 v1).

- **D-R2a-3 (marker-parser realization location):** The parser lives at `.claude/skills/auditing-shared/scripts/parse_blocks_x_markers.py`. Rationale: (a) the regex is shared across the orchestrator gating call site AND any future audit-rule that needs marker enumeration; centralizing it prevents two-regex-implementations drift; (b) `auditing-shared/scripts/` is the existing host for shared parsing helpers (sibling to `log_state_transition.py`); (c) hosting in the orchestrator agent prompt embeds the regex in markdown — harder to test in isolation; (d) hosting in the auditing rule itself binds the parser to one consumer. The shared-helper location is the lowest-cost-and-most-reusable choice. Routed to Composer as **Q-CC-2** for ratification.

- **Marker form (per ADR-0063, cited not re-derived):** `<!-- BLOCKS: <stage-slug>-completion -->`. HTML-comment pragma, invisible in rendered markdown, greppable. Optional payload after `—`.

- **Lowest-cost primitive justification (Principle 1):** Procedure edits in existing agents + new shared helper in existing skill scripts directory + free-string schema-value additions. No new sub-agent.

- **Reasoning configuration justification (Principle 9):** Discovery + orchestrator agents unchanged.

### FR-10 — `auditing-subagents` feature-touch-coverage rule

**Decisions adopted:** **D-R2a-5 (new rule entry, not extension)**. Reverse-check posture (parent OI-A3) carried as R2a's OI-R2a-2 to Blueprint Open Questions.

- **Target files:**
  - `.claude/skills/auditing-subagents/SKILL.md` — **new rule entry `SA-14`** (per D-R2a-5; next available number after the existing SA-13 from the ADR-0040 era): "feature-touch-coverage — when a feature's working directory indicates the agent surface was touched (per FR-6 trigger conditions), verify presence of `agent-roster-impact-matrix.md` and row-count parity with `.claude/agents/*.md` at audit time."
  - `.claude/skills/auditing-subagents/scripts/audit_feature_touch_coverage.py` — new script. Reads `working/feature/<slug>/` for trigger evidence; checks matrix presence + row count; emits `BLOCKER` finding per AC-FR-10-a/-b.
  - `.claude/skills/auditing-subagents/references/` — new reference text for SA-14 discipline.

- **D-R2a-5 rationale (new rule, not extension):** Extending an existing SA-NN rule's predicate would (a) couple two unrelated audit dimensions (the existing rules audit per-agent frontmatter properties; SA-14 audits a per-feature-run artifact), (b) make the audit catalog harder to grep by ID-to-purpose mapping, and (c) muddy the SA-NN versioning posture (existing rules predate this discipline). A new entry is the cleanest realization. Routed to Composer as **Q-CC-4** for ratification.

- **Reverse-check posture (R2a OI-R2a-2):** Whether `auditing-skills` gets a parallel reverse-check (audit whether existing agents' `skills:` arrays should include a newly-authored skill) is carried as a Blueprint Open Question rather than folded into SA-14's scope. Rationale per PRD Product Policy: conflating roster-matrix-presence enforcement with skills-array reverse-checks blurs two distinct audit dimensions.

- **Lowest-cost primitive justification (Principle 1):** New audit rule + script under existing audit skill. Backstops FR-6's design-time gate at packaging time (defense-in-depth pattern from KB-cc-design Principle 6 — permissions as safety net).

- **Reasoning configuration justification:** N/A (script-only; no sub-agent reasoning surface).

## Severity bridge table content (D-10)

Per inherited ADR-0061, the bridge table lives at `.claude/skills/KB-review-disciplines/references/severity-taxonomy.md`. The parent design fixed the host; **R2a authors the actual content** below. Both weight sets remain because they serve different mathematical roles (see §Weight Preservation Note).

### Five-column bridge table

| auditor_vocab | reviewer_vocab | pv_vocab | non_monotonic_edges | iteration_delta_weight |
|---|---|---|---|---|
| `BLOCKER` | `critical` | `blocking` | — (monotonic; forces refuse-to-advance across all surfaces) | **10** |
| `MAJOR` | `important` | `blocking` (outright assertion failure) OR `warning` (partial/soft failure) | **MAJOR → {blocking, warning}** — PV-side branch depends on whether the failure is an outright assertion miss or a soft/partial finding | **3** |
| `MINOR` | `recommended` | `warning` | — (monotonic) | **1** |
| `NIT` (auditing-mcp) | `recommended` | `informational` | **NIT ↔ recommended** — reviewer vocabulary lacks a sub-`recommended` grade; NIT translates to `recommended` with explicit "non-actionable" marker | **0** |
| `INFO` (architecture / cross-artifact auditors) | (no direct equivalent — surfaced as diagnostic, not issue) | `informational` | **NIT vs INFO intra-auditor divergence** — same severity floor (`-0.5` and `0` respectively) but auditing-mcp uses NIT while architecture / cross-artifact auditors use INFO; codebase-analysis Known Issue 2 documents this | **0** |

### Verdict-compute weights (the OTHER weight set)

These are the points the verdict-compute machinery deducts when computing the gate-pass score (per `auditing-cc-configs/scripts/verdict_compute.py`):

| Severity | Verdict-compute deduction |
|---|---|
| `BLOCKER` | **-12** (with **additional -12 escalation penalty = -24 total** when the BLOCKER persists across iterations — the iteration-delta weight is separately tracked) |
| `MAJOR` | **-5** |
| `MINOR` | **-2** |
| `NIT` | **-0.5** |
| `INFO` | **0** (diagnostic only; surfaced but not score-impacting) |

### Weight Preservation Note

**Both weight sets remain in this design because they encode different mathematical roles:**

- **Verdict-compute weights** (-12 / -5 / -2 / -0.5 / 0) drive the **single-iteration gate-pass / fail computation**. They answer "is this iteration's audit verdict pass or fail?" by summing per-finding deductions against a fixed score floor. The deduction values are calibrated against the existing pipeline's gate-pass thresholds and removing or rebalancing them would force every downstream gate-pass rubric to be re-calibrated.
- **Iteration-delta weights** (10 / 3 / 1 / 0 / 0) drive the **convergence / cap-tripping logic across iterations** in the 4-cycle reconciliation cap (per KB-review-disciplines cross-artifact-audit). They answer "is the audit converging or oscillating?" by tracking total-weight-resolved vs total-weight-introduced per cycle. The values here are about reconciliation effort, not gate-pass arithmetic.

The two roles are independent. Collapsing them into one weight set would force one of two losses: (a) gate-pass thresholds become a function of how many cycles have run (breaks per-iteration determinism), or (b) convergence-tracking becomes coarse-grained on the BLOCKER vs MAJOR distinction (breaks 4-cycle cap intent). Preserving both is the cleanest separation of concerns.

### Non-monotonic edges (explicit enumeration)

1. **NIT vs INFO intra-auditor divergence.** Auditing-mcp uses `NIT` (carrying -0.5 verdict-compute deduction); architecture-auditor and cross-artifact-auditor use `INFO` (carrying 0 verdict-compute deduction). Same conceptual severity floor; different naming and score impact. The translator helper at `auditing-shared/scripts/translate_severity.py` (recommended but not required by R2a) records the source-auditor surface as context.
2. **NIT ↔ recommended.** Reviewer vocabulary's `recommended` is the closest match for auditing-mcp's `NIT`, but reviewer-side `recommended` is intended to be actionable while NIT-class findings are explicitly low-priority. Translator outputs include "NIT — non-actionable in reviewer surface" rationale.
3. **MAJOR → {blocking, warning}.** PV vocabulary collapses to two grades when receiving a MAJOR finding: `blocking` if the failure is an outright assertion-not-satisfied (e.g., a required predicate emitted False), `warning` if the failure is partial (e.g., the predicate emitted True but with caveat notes). The translator requires the assertion-failure-mode as an input parameter; ambiguity surfaces an explicit translator error rather than a silent collapse.

### Translator utility (optional helper)

Optional `.claude/skills/auditing-shared/scripts/translate_severity.py` at audit-issues.json emission time. Reads the source vocabulary + the target audience; emits the target vocabulary per the bridge table. Non-monotonic edges require explicit rationale in the translator output. This is a convenience helper, not load-bearing — the bridge table itself in `severity-taxonomy.md` is the single source of truth.

## Skill-coverage decisions for THIS run (eat-own-dogfood per FR-7)

Per FR-7's substance heuristic (D-8) and D-R2a-4 (embed in synthesis.md), each new domain concept introduced by this R2a run is paired with an explicit skill-coverage decision. **All six concepts** below resolve to **option (a) — covered by existing skills**. The actual embedded section lives in `synthesis.md`; design-cc records the per-decision rationale here:

| # | New domain concept | Decision | Host skill — positive evidence |
|---|---|---|---|
| 1 | **design-realization audit** (FR-1) | (a) covered by `KB-review-disciplines` | The audit dimension extends `architecture-audit.md`'s existing lens enumeration (CoVe, Blast-Radius, Brief-Honor) with Lens 4. The KB already governs auditor discipline; brief-honor + CoVe disciplines are the established home of audit-dimension expansion. Additive content; no new skill. |
| 2 | **agent-roster impact matrix** (FR-6) | (a) covered by `KB-cc-design` (active Principle 9) + `KB-documentation-criteria` (template) | The active reframing of Principle 9 (FR-8) makes KB-cc-design the home of "evaluated every agent" framing. The matrix template lives in KB-documentation-criteria (already loaded by design-cc). No new skill. |
| 3 | **skill-coverage decision** (FR-7) | (a) covered by `KB-cc-design` (Principle 2 "skill loading on-demand") | The lowest-cost-primitive discipline is the natural home of skill-vs-no-skill rationale: the question "should this become a skill?" is the inverse of Principle 2's "is loading this content always-on worth its context cost?" No new skill. |
| 4 | **Principle 9 active reframing** (FR-8) | (a) covered by `KB-cc-design` | Trivial — the principle being reframed IS Principle 9 of this KB. The sentence-replacement IS the discipline. No new skill. |
| 5 | **Blocks-X marker grammar** (FR-9) | (a) covered by `KB-documentation-criteria` | The grammar is a documentation convention; the host is the documentation-criteria KB's `references/` directory (per inherited ADR-0063). The state-transitions-log-entry-template and canonical-conventions discipline already host other marker grammars in this KB. No new skill. |
| 6 | **agent-roster matrix-missing audit rule** (FR-10) | (a) covered by `auditing-subagents` (new SA-14 rule) | The auditing-subagents skill family is the natural home of audit rules over subagents (rule names are namespaced `SA-NN`). A new rule entry (per D-R2a-5) is additive to the existing SA-1..SA-13 catalog. No new skill. |

**Eat-own-dogfood compliance:** All 6 decisions resolve to option (a) — covered by existing skills. Zero new skills proposed; zero "no skill warranted" rationales. The substance-not-presence heuristic (D-8) passes trivially because each decision cites concrete file paths + positive evidence per the W/H/A rubric.

## Agent-roster impact for THIS run (eat-own-dogfood per FR-6)

This run touches the agent surface per FR-6's four-condition trigger — **specifically condition 1** (`.claude/agents/*.md` modifications): the FR-1/6/7/8/10 implementations modify `review-architecture-auditor.md`, `discovery-codebase-researcher.md`, `design-claude-code.md`, `execute-orchestrator.md`, `synth-synthesizer.md`, `design-composer.md`, plus indirect modifications via skill-load changes. Therefore this run **must** produce `working/feature/pipeline-design-time-discipline-r1/agent-roster-impact-matrix.md` before Design Composition can mark its stage complete (FR-6 self-application).

- **Matrix authoring is a Plan / Task-Decomposition deliverable**, not a per-layer-design output. This document records the contract under which the matrix is authored:
  - Row count: equal to `ls .claude/agents/*.md | wc -l` at authoring time (currently 37 per codebase-analysis).
  - Five cells per row: tools / skills / model / effort / prompt body.
  - Per-cell schema: `<value> — <positive-evidence-string>` (no bare `no-change`).
  - Authoring-time budget: NFR-7 (30 min wall-clock at 100-agent inventory; 37 agents → ~11 min at the linear-extrapolation rate).
  - Exemplar shape: `Issues/per-agent-design-evaluation-gap/evidence/agent-roster-impact-matrix.md` (the retroactive Track-A2 matrix from devcontainer-mcp-provisioning-r1; cells use `EXPLICIT_NO — <evidence>`).

- **Mechanical-evaluator override-event posture (per D-5):** If the design-cc author at Plan time disagrees with the advisory predicate's classification of any of the four trigger conditions for this run, the override event is logged to `state-transitions.log` via `log_state_transition.py` as `transition_name: TRIGGER_OVERRIDE`, with context naming the trigger condition + the human rationale. For this R2a run: condition 1 fires unambiguously (mechanical file-diff observation); no override expected.

## Plan-stage sequencing recommendation (D-R2a-6)

**Bridge first, then FR-1/9/10 consumers.** Concretely: the Plan should sequence severity-taxonomy bridge content authoring (D-10 → `KB-review-disciplines/references/severity-taxonomy.md`) **before** the FR-1, FR-9, and FR-10 implementation tasks that emit findings using the bridge vocabulary.

**Rationale:**

- FR-1 emits `BLOCKER`/`MAJOR` findings per the bridge mapping (design-realization audit).
- FR-9 emits `BLOCKER` findings on unresolved markers (Blocks-X gates).
- FR-10 emits `BLOCKER` findings on missing matrix / row-count mismatch (SA-14 audit rule).
- If consumers are authored before the bridge content, the implementations risk encoding ad-hoc severity-mapping assumptions that contradict the eventually-authored bridge table — replaying the cross-artifact-divergence defect class this very run exists to prevent.
- Authoring the bridge first lets consumer implementations cite the bridge table by-section-reference rather than inlining their own severity rubrics.

**Routed to Composer as Q-CC-5** for plan-author to honor. The plan-author (not design-cc) is the agent that materializes this sequencing in concrete task ordering.

## Closed-by-inheritance decisions (brief reference)

Five parent-run decisions are closed for R2a's purposes; they remain valid commitments but require no R2a authoring:

| Parent decision | Resolution | R2a posture |
|---|---|---|
| **D-1** (FR-1 prescription-extraction) | Inherited **ADR-0059** (companion `.prescriptions.yaml`) | Cited in FR-1 above; no re-authoring |
| **D-4** (FR-9 marker grammar) | Inherited **ADR-0063** (`<!-- BLOCKS: <stage-slug>-completion -->`) | Cited in FR-9 above; no re-authoring |
| **D-10 HOST** (severity bridge publication target) | Inherited **ADR-0061** (`KB-review-disciplines/references/severity-taxonomy.md`) | Bridge **host** fixed by ADR-0061; bridge **content** authored by R2a above |
| **D-2, D-7** (FR-3, FR-5 — R2b-only) | Out of R2a scope | Routed to queued R2b run; no R2a touch |
| **D-9** (FR-11 §O placement — R2b-only) | Out of R2a scope | Routed to queued R2b run; no R2a touch |

## Open Items (Q-CC-N) for design-composer

Per FR-5 invariant (design-cc does NOT author ADRs), these questions surface to design-composer for ratification and potential ADR authoring:

| ID | Question | Recommended | Routes to |
|---|---|---|---|
| **Q-CC-1** | D-10 severity bridge publication target — confirm closure-by-inheritance | Closed by inherited ADR-0061 (`KB-review-disciplines/references/severity-taxonomy.md`). R2a authors the **content** above per ADR-0061. No further composer routing needed; surfaced here only to confirm the parent-conversation closure carries into R2a unchanged. | design-composer at Blueprint composition (confirm) |
| **Q-CC-2** | D-R2a-3 marker-parser realization location ratification | `.claude/skills/auditing-shared/scripts/parse_blocks_x_markers.py` (shared helper sibling to `log_state_transition.py`). Alternative: embed regex in `execute-orchestrator.md` prompt. Recommended: shared helper. | design-composer at Blueprint composition |
| **Q-CC-3** | D-R2a-4 FR-7 artifact location ratification | Embed Skill-Coverage Decisions section in `synthesis.md` (not standalone file). Alternatives: standalone `skill-coverage-decisions.md` or section in Blueprint. Recommended: synthesis.md embedding. | design-composer at Blueprint composition |
| **Q-CC-4** | D-R2a-5 FR-10 rule realization — new rule entry vs extend existing | New rule entry `SA-14` (per D-R2a-5). Alternative: extend an existing SA-NN predicate. Recommended: new entry. | design-composer at Blueprint composition |
| **Q-CC-5** | D-R2a-6 plan-stage sequencing — bridge first vs consumers first | Bridge first (severity-taxonomy.md content), then FR-1/9/10 consumers. plan-author honors the sequencing. | design-composer at Blueprint composition + plan-author |

Five questions — narrower than the parent's eight (the parent's Q-CC-1/3/4/6/7/8 were tied to R2b-only FRs or already-closed inheritance items).

## Cross-references to ADRs the design depends on

- **ADR-0005** — Append-only supersession discipline; FR-8's Principle 9 rewording is an in-place leading-sentence replacement with a § Change Log entry, NOT a supersession (the principle's heading and field-by-field body are retained).
- **ADR-0009** — Rationale brief honor discipline; the brief-honor citation at the head of this design satisfies the L3 brief-honor check.
- **ADR-0017** — `shared-document-reviewer` invocation points; FR-6's matrix is reviewed at invocation 3 (per-layer Design outputs).
- **ADR-0030** — pedagogical-section discipline; the new template `agent-roster-impact-matrix-template.md` in KB-documentation-criteria conforms to the pedagogical-marker spec.
- **ADR-0040** — Serena narrowed-allowlist precedent; the canonical exemplar of the per-agent-design-evaluation-gap that FR-6 closes.
- **ADR-0044** — state-transitions log v1 invariant (execute-orchestrator is the sole writer); FR-9 reserves three new `transition_name` string values consistent with the invariant (no schema evolution; field is free-string).
- **ADR-0045** — `review-architecture-auditor` has no Agent/Task tool; FR-1's new dimension runs inline, not via sub-agent spawn-out.
- **ADR-0059** *(inherited)* — Companion `.prescriptions.yaml` schema. Closes parent OI-A1 / R2a FR-1 extraction-mechanism question.
- **ADR-0061** *(inherited)* — Severity-vocabulary bridge table HOST. Fixes publication target; R2a authors the content per the host's location.
- **ADR-0063** *(inherited)* — Blocks-X marker grammar canonicalization. Closes parent OI-A5 / R2a FR-9 grammar question.

## Dependencies on other layers

**None active.** Per PRD Layer Scope, the only activated layer for this R2a run is Claude Code. All 8 other layers are explicitly marked `N/A — out of scope`. No `depends_on` or `provides_to` edges to other-layer designs.

The sibling sidecar `cc-dependencies.json` enumerates intra-CC-layer file dependencies + reverse-blast-radius edges per codebase-analysis.

## Self-review checklist (Phase 4 mental Gate 0)

- [x] Brief-honor citation present at head of document (re-cited from parent rationale brief).
- [x] All 6 R2a FRs land in per-FR subsections (FR-1, FR-6, FR-7, FR-8, FR-9, FR-10).
- [x] All AC references are EARS-form (consumed from PRD-v1 verbatim; no AC restated).
- [x] Every new primitive has a lowest-cost-primitive justification (Principle 1).
- [x] CLAUDE.md is NOT modified (Principle 5 — single source of truth; KBs suffice).
- [x] Path-gating used wherever applicable; new helpers scoped under existing skill paths.
- [x] Permission policy: no new mutating-tool entries required by R2a. Audit scripts read state and emit JSON; no permission-deny additions.
- [x] Q-CC-N items complete (5 items: Q-CC-1 .. Q-CC-5).
- [x] Reasoning-configuration justifications recorded for every modified sub-agent: `review-architecture-auditor` (unchanged at opus/xhigh), `design-cc` (unchanged at opus/high), `synth-synthesizer` / `design-composer` (unchanged).
- [x] Severity vocabulary handled via D-10 bridge table — **content authored above** with Weight Preservation Note.
- [x] All 7 open/partial decisions adopted (D-3 carried as R2a OI-R2a-2, D-5 adopted, D-8 adopted, D-10 content authored, D-R2a-3/4/5/6 adopted with composer ratification routing).
- [x] 5 closed-by-inheritance decisions referenced briefly (D-1, D-4, D-10 host, plus D-2/D-7/D-9 as R2b-out-of-scope).
- [x] No ADRs authored (FR-5 invariant; design-composer owns ADR authoring).
- [x] Length target met: ~6 major sections + per-FR subsections, materially shorter than parent's 15-section design.
- [x] Eat-own-dogfood compliance documented for both FR-6 (matrix contract recorded; matrix authoring deferred to Plan stage) and FR-7 (six skill-coverage decisions tabled with per-decision rationale).

---

*End of Claude Code per-layer Design subsection for R2a. Awaiting design-composer integration into the Blueprint at Stage 7, then shared-document-reviewer at invocation 3, then review-architecture-auditor at Stage 8.*
