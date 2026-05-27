---
id: Plan-pipeline-design-time-discipline-r1
version: 1.0.0
status: draft
doc_type: plan
feature_slug: pipeline-design-time-discipline-r1
derived_from: working/feature/pipeline-design-time-discipline-r1/blueprint-v1.md
phases: 10
total_tasks: 31
parent_run: pipeline-cross-artifact-discipline-r1
related_run: pipeline-gate-validator-hardening-r1
inherited_adrs: [ADR-0059, ADR-0061, ADR-0063]
adrs_authored_this_run: [ADR-0064, ADR-0065]
generated: 2026-05-26T18:30:00Z
generated_by: plan-author
---

# Plan: Pipeline Design-Time Discipline (R2a)

## Contents

- [x] Purpose
- [x] Source
- [x] Phase 0 — Setup
- [x] Phase 1 — Severity bridge foundation (D-R2a-6)
- [x] Phase 2 — FR-8 Principle 9 active reframing
- [x] Phase 3 — FR-9 Blocks-X marker mechanism
- [x] Phase 4 — FR-1 design-realization audit dimension
- [x] Phase 5 — FR-6 agent-roster matrix contract
- [x] Phase 6 — FR-7 skill-coverage discipline
- [x] Phase 7 — FR-10 SA-14 audit-subagents rule
- [x] Phase 8 — Eat-own-dogfood (this run's matrix + decisions)
- [x] Phase 9 — Rollout / deliverable packaging
- [x] Cross-Phase Dependencies
- [x] L1/L2/L3 Verification Discipline
- [x] Acceptance Test Cross-Reference
- [x] Estimation Methodology
- [x] Resourcing Posture
- [x] Open Items (Pending Cross-Artifact Audit)
- [x] Update History

## Purpose

Executable phase-and-task decomposition of `blueprint-v1.md` (v1.0.1) for the R2a design-time-discipline run. Honors the Blueprint's §Implementation plan sequencing (Phase A bridge content → Phases B/C/D consumers; Phases E/F dependency-linked) and refines it into the 10-phase / 31-task delivery sequence below. Cycle-1 reconciliation patches (I-AA-001..006) are baked into the Blueprint; this Plan does NOT re-treat them. I-AA-005 (MINOR — SA-NN count fix in `auditing-subagents/SKILL.md`) is folded into Phase 7. I-AA-007 (INFO — dogfood validation evidence) is folded into Phase 9 packaging.

R2a is single-layer (Claude Code only). No cross-layer integration phases.

## Source

- **Blueprint**: `working/feature/pipeline-design-time-discipline-r1/blueprint-v1.md` (v1.0.1)
- **PRD**: `working/feature/pipeline-design-time-discipline-r1/prd-v1.md` (FR-1, FR-6, FR-7, FR-8, FR-9, FR-10; NFR-1, NFR-7, NFR-8, NFR-9)
- **Per-layer design**: `working/feature/pipeline-design-time-discipline-r1/cc-design.md`
- **Synthesis**: `working/feature/pipeline-design-time-discipline-r1/synthesis.md` (v1.0.2 — Skill-Coverage Decisions back-fill landed cycle 1)
- **Codebase analysis**: `working/feature/pipeline-design-time-discipline-r1/codebase-analysis.json` (v1.0.1)
- **Inherited ADRs**: ADR-0059 (companion `.prescriptions.yaml`), ADR-0061 (severity bridge host), ADR-0063 (Blocks-X grammar)
- **ADRs authored this run**: ADR-0064 (matrix contract), ADR-0065 (skill-coverage discipline)
- **Phase taxonomy used**: Phase 0 (setup) + Phases 1..8 (feature delivery, sequenced by Blueprint §Implementation plan) + Phase 9 (rollout / packaging).

## Phase 0 — Setup

### Goal

Confirm baselines and pre-feature scaffolding before any file is touched. Verifies inherited-ADR availability and the current agent / KB inventory used downstream by FR-6's row count and the change impact map.

### Tasks

#### T0.1: Verify inherited ADRs are accepted and accessible

- **Layer:** Claude Code
- **Description:** Confirm `adrs/ADR-0059-adr-prescriptions-companion-file.md`, `adrs/ADR-0061-severity-vocabulary-bridge-table.md`, and `adrs/ADR-0063-blocks-x-marker-grammar.md` exist with `status: accepted` (per parent run's deliverable). No edits.
- **Dependencies:** none
- **Estimate:** S
- **Satisfies AC:** N/A (setup-only — pre-condition for FR-1, FR-9, severity bridge content)
- **L1:** Three files present at `adrs/` project root; YAML parses.
- **L2:** Each ADR's frontmatter `status` field equals `accepted`.
- **L3:** Blueprint §Inheritance manifest's three ADR references resolve to these files.

#### T0.2: Snapshot the current agent / KB inventory

- **Layer:** Claude Code
- **Description:** Capture `ls .claude/agents/*.md | wc -l` (expected 37 per codebase-analysis A-4) and the canonical KB skill list. Pin to a baseline file `working/feature/pipeline-design-time-discipline-r1/inventory-baseline.txt` for later FR-6 row-count parity check.
- **Dependencies:** none
- **Estimate:** S
- **Satisfies AC:** N/A (setup, but baseline is consumed by AC-FR-6-b and AC-FR-10-b)
- **L1:** `inventory-baseline.txt` exists; line count equals `ls .claude/agents/*.md | wc -l`.
- **L2:** Each line is a valid path matching `.claude/agents/*.md`.
- **L3:** Line count equals the codebase-analysis-asserted figure (37).

#### T0.3: Pre-check `auditing-shared/scripts/` and `auditing-subagents/scripts/` directory existence

- **Layer:** Claude Code
- **Description:** Confirm both script directories exist (they host four new scripts in later phases). No edits.
- **Dependencies:** none
- **Estimate:** S
- **Satisfies AC:** N/A
- **L1:** Both directories present.
- **L2:** Existing scripts (e.g., `auditing-shared/scripts/log_state_transition.py`) confirm convention.
- **L3:** Importable from the eventual new scripts' relative-path resolution.

### Phase 0 Exit Criteria

- All three inherited ADRs confirmed accepted and citable.
- Agent inventory baseline pinned at 37 (or actual current count) for FR-6 / FR-10 parity checks.
- Canonical script-host directories confirmed.

## Phase 1 — Severity bridge foundation (D-R2a-6)

### Goal

Author the severity-vocabulary bridge content at `KB-review-disciplines/references/severity-taxonomy.md` before FR-1 / FR-9 / FR-10 consumers cite it. Sequencing per Blueprint Q-CC-5 ratification: consumers-first would risk placeholder citation leakage (the exact failure mode FR-1 catches).

### Tasks

#### T1.1: Author the five-column bridge table in `severity-taxonomy.md`

- **Layer:** Claude Code
- **Description:** Write the canonical bridge content into `.claude/skills/KB-review-disciplines/references/severity-taxonomy.md` per Blueprint §Severity bridge content (D-10 substrate). Five rows (BLOCKER / MAJOR / MINOR / NIT / INFO) × five columns (auditor / reviewer / pv / non-monotonic-edges / iteration-delta-weight). Include the Weight Preservation Note + Verdict-Compute weights table + Non-monotonic edges enumeration.
- **Dependencies:** T0.1
- **Estimate:** M
- **Satisfies AC:** AC-FR-1-a (severity vocabulary), AC-FR-9-b (severity vocabulary), AC-FR-10-a (severity vocabulary), AC-NFR-8-a (four-field finding shape colocated)
- **L1:** File exists; markdown parses; table has 5 rows × 5 columns.
- **L2:** Grep for `BLOCKER`, `MAJOR`, `MINOR`, `NIT`, `INFO` returns rows; Weight Preservation Note section header present; `iteration_delta_weight` column populated 10/3/1/0/0.
- **L3:** ADR-0061 (host fixer) references resolve to this file path; a future emitter citing "the severity bridge" can navigate to a real authored target with no placeholder.

#### T1.2: Document the NFR-8 four-field finding shape inline in the bridge host

- **Layer:** Claude Code
- **Description:** In the same `severity-taxonomy.md` file, document the additive NFR-8 four-field shape (`rule`, `target`, `divergence`, `next_action`) consumed by FR-1, FR-9, FR-10 emitters per inherited ADR-0061. Co-location is per Blueprint §Severity bridge content.
- **Dependencies:** T1.1
- **Estimate:** S
- **Satisfies AC:** AC-NFR-8-a
- **L1:** "NFR-8 four-field finding shape" section header present.
- **L2:** Each of `rule`, `target`, `divergence`, `next_action` named with one-sentence semantics.
- **L3:** A future emitter authored against this section can populate the four fields without ambiguity.

### Phase 1 Exit Criteria

- `severity-taxonomy.md` content present and citable by FR-1 / FR-9 / FR-10 consumers.
- Both weight sets (verdict-compute + iteration-delta) documented in the same file.
- NFR-8 four-field finding shape documented in the bridge host.

## Phase 2 — FR-8 Principle 9 active reframing

### Goal

Land the concentrated 2-site edit: Principle 9's defensive-→-active leading-sentence replacement, and the cross-reference at `design-claude-code.md:56`. Sequenced before FR-6 because the matrix discipline cites Principle 9 by name (AC-FR-8-b mutual cross-reference).

### Tasks

#### T2.1: Replace Principle 9 leading sentence at `KB-cc-design/references/principles.md:182`

- **Layer:** Claude Code
- **Description:** Verbatim sentence replacement per cc-design §FR-8: defensive framing → active framing, recording the consideration even when outcome is no change. Existing body of Principle 9 retained verbatim.
- **Dependencies:** none (independent of Phase 1)
- **Estimate:** S
- **Satisfies AC:** AC-FR-8-a
- **L1:** New sentence text present at line 182 (anchor may shift; grep on the new sentence).
- **L2:** Grep confirms the verbatim active-framing sentence; defensive-framing leading sentence removed.
- **L3:** A future designer consulting Principle 9 reads the active framing as the leading sentence; substance test (matrix cell) named.

#### T2.2: Update cross-reference at `.claude/agents/design-claude-code.md:56`

- **Layer:** Claude Code
- **Description:** Update the verbatim citation to match the new wording and add the AC-FR-8-b mutual reference: "the matrix-cell discipline (FR-6 §Per-cell discipline) is the substance test for the per-agent consideration this principle requires."
- **Dependencies:** T2.1
- **Estimate:** S
- **Satisfies AC:** AC-FR-8-b
- **L1:** Reference text at the cited line; markdown parses.
- **L2:** Both directions of the cross-reference present (design-claude-code → Principle 9 AND Principle 9 → matrix-cell discipline).
- **L3:** Grep on either direction's anchor phrase returns both files.

### Phase 2 Exit Criteria

- Principle 9 reads in the active framing.
- The two files cross-reference each other by name.
- No stale defensive-framing wording remains in either file's leading sentence.

## Phase 3 — FR-9 Blocks-X marker mechanism

### Goal

Realize the Blocks-X marker enforcement: shared parser script (per D-R2a-3 / Q-CC-2 ratification), orchestrator stage-transition gate logic, discovery-researcher emission procedure, state-transitions-log `transition_name` extension. Grammar inherited from ADR-0063 verbatim.

### Tasks

#### T3.1: Author `parse_blocks_x_markers.py` at `auditing-shared/scripts/`

- **Layer:** Claude Code
- **Description:** New shared parser per the ADR-0063 canonical grammar (`<!-- BLOCKS: <stage-slug>-completion -->`, HTML-comment pragma). Single source of truth for the regex; consumed by orchestrator gate + future audit rules. Output schema: list of `{stage, raw_line, file_path, line_no}` records.
- **Dependencies:** T0.3
- **Estimate:** M
- **Satisfies AC:** AC-FR-9-a, AC-FR-9-c
- **L1:** File exists; `python -c "import ast; ast.parse(open('.claude/skills/auditing-shared/scripts/parse_blocks_x_markers.py').read())"` succeeds.
- **L2:** Smoke test: invocation against a synthetic fixture containing one `<!-- BLOCKS: design-completion -->` marker returns one record with `stage=design`.
- **L3:** A future discovery output exercised end-to-end through the orchestrator's gate logic enumerates correctly.

#### T3.2: Extend `state-transitions-log-entry-template.md` with the four new transition names

- **Layer:** Claude Code
- **Description:** Document `BLOCKS_X_RESOLVED`, `BLOCKS_X_DEFERRED_WITH_OI`, `BLOCKS_X_FALSE_POSITIVE`, plus FR-6's `TRIGGER_OVERRIDE` (per ADR-0064) as valid `transition_name` values. Free-string per ADR-0044 v1; no schema evolution.
- **Dependencies:** none
- **Estimate:** S
- **Satisfies AC:** AC-FR-9-c
- **L1:** All four `transition_name` values appear in the template documentation block.
- **L2:** Grep confirms enumeration; no schema change to `log_state_transition.py` required.
- **L3:** A future orchestrator emitting any of the four values logs without rejection.

#### T3.3: Extend `discovery-codebase-researcher.md` with the marker-emission procedure

- **Layer:** Claude Code
- **Description:** Procedure-text addition in the discovery-codebase-researcher agent: when a question whose answer is required before a named stage can complete is surfaced, emit a marker per the ADR-0063 grammar in the discovery output.
- **Dependencies:** T0.1 (ADR-0063 accessibility)
- **Estimate:** S
- **Satisfies AC:** AC-FR-9-a
- **L1:** Procedure text present; agent's frontmatter unchanged (Principle 9 dogfood compliance — already recorded in Blueprint §Reasoning-configuration audit).
- **L2:** Grep on "Blocks" marker reference returns the new procedure.
- **L3:** Future discovery output containing such a marker is emitted in the canonical form.

#### T3.4: Add stage-transition gate logic to `execute-orchestrator.md`

- **Layer:** Claude Code
- **Description:** Procedure-text addition: at each stage-transition checkpoint, invoke `parse_blocks_x_markers.py` to enumerate unresolved markers in upstream outputs; refuse to mark the named stage complete until each marker has transitioned to RESOLVED / DEFERRED / FALSE_POSITIVE.
- **Dependencies:** T3.1, T3.2
- **Estimate:** M
- **Satisfies AC:** AC-FR-9-a, AC-FR-9-b
- **L1:** Procedure text present; agent frontmatter unchanged.
- **L2:** Grep on "parse_blocks_x_markers.py" returns the new procedure block.
- **L3:** An end-to-end run exercising an unresolved marker triggers the orchestrator's refuse-to-advance with a BLOCKER-severity finding per AC-FR-9-b.

### Phase 3 Exit Criteria

- Single-source-of-truth parser at `auditing-shared/scripts/parse_blocks_x_markers.py`.
- Four new `transition_name` values documented in the template.
- Orchestrator + discovery-researcher procedures extended.
- Blocks-X markers function as stage-transition gates end-to-end.

## Phase 4 — FR-1 design-realization audit dimension

### Goal

Add the new "Lens 4: Design Realization" audit dimension to `review-architecture-auditor` and the supporting companion-file validator. Consumes Phase 1 severity bridge for emission vocabulary. Realizes inherited ADR-0059.

### Tasks

#### T4.1: Author `validate_adr_prescriptions.py` at `auditing-shared/scripts/`

- **Layer:** Claude Code
- **Description:** New linter that schema-validates ADR-0059 companion `.prescriptions.yaml` files. Verifies (a) the companion file's `adr_path` / slug matches the partner ADR, (b) declared `target_path` exists, (c) required `assertion` field present.
- **Dependencies:** T0.1, T0.3
- **Estimate:** M
- **Satisfies AC:** AC-FR-1-c (supports auditor's mechanical-inspection contract)
- **L1:** File exists; syntax-parses.
- **L2:** Smoke test: invocation against a synthetic well-formed companion returns OK; invocation against a malformed one returns specific error.
- **L3:** Run against any existing `.prescriptions.yaml` companion in the repo (none expected at R2a author time; lint passes on the no-file case).

#### T4.2: Add Lens 4 to `KB-review-disciplines/references/architecture-audit.md`

- **Layer:** Claude Code
- **Description:** New "Lens 4: Design Realization" section alongside existing CoVe / Blast-Radius / Brief-Honor lenses. References the inherited ADR-0059 companion-file convention. References the severity bridge (Phase 1) by name for emission vocabulary.
- **Dependencies:** T1.1 (severity bridge content)
- **Estimate:** M
- **Satisfies AC:** AC-FR-1-c
- **L1:** "Lens 4: Design Realization" heading present.
- **L2:** Section references ADR-0059 companion file by name; references `severity-taxonomy.md` for BLOCKER emission vocabulary.
- **L3:** A future auditor consulting the KB reads four lenses; Lens 4 names the companion-file mechanism mechanically.

#### T4.3: Extend `review-architecture-auditor.md` with the new audit procedure phase

- **Layer:** Claude Code
- **Description:** Additive new procedure phase per cc-design §FR-1: inline phase (no Agent/Task tool per ADR-0045). For each ADR in the run's `adrs/` set with a `.prescriptions.yaml` companion, compare prescription vs eventual file; emit BLOCKER on divergence per the bridge vocabulary. No companions → no-op (AC-FR-1-b).
- **Dependencies:** T4.1, T4.2, T1.1
- **Estimate:** M
- **Satisfies AC:** AC-FR-1-a, AC-FR-1-b, AC-FR-1-c, AC-NFR-1-a (auditor 5000 ms budget per up-to-20 prescriptions), AC-NFR-8-a (four-field shape)
- **L1:** New procedure-phase section present in agent prompt.
- **L2:** Grep returns "design-realization" / "Lens 4" references; companion-file consumption procedure named.
- **L3:** Auditor run against a feature with one synthetic divergence emits a BLOCKER carrying `rule`, `target`, `divergence`, `next_action` within the 5000 ms budget.

### Phase 4 Exit Criteria

- `validate_adr_prescriptions.py` exists and runs.
- KB has four lenses; Lens 4 documented.
- Auditor agent procedure includes the design-realization phase.
- An end-to-end audit against a synthetic divergence emits a BLOCKER per the bridge vocabulary, satisfying NFR-1 / NFR-8.

## Phase 5 — FR-6 agent-roster matrix contract

### Goal

Codify the mandatory `agent-roster-impact-matrix.md` artifact: design-cc procedure extension, matrix template, advisory predicate. Implements ADR-0064.

### Tasks

#### T5.1: Author `agent-roster-impact-matrix-template.md` at `KB-documentation-criteria/references/templates/`

- **Layer:** Claude Code
- **Description:** New canonical template per ADR-0064 Clause 2. Row schema: one per `.claude/agents/*.md` file at authoring time. Cell schema: `<value> — <positive-evidence-string>`; five explicit dimensions (tools / skills / model / effort / prompt body). Headers + worked example row + the "no bare no-change" rule.
- **Dependencies:** none
- **Estimate:** M
- **Satisfies AC:** AC-FR-6-a (template), AC-FR-6-b (cell discipline), AC-FR-6-d (bare-`no-change` insufficient), AC-NFR-9-a (grep-checkable affordance referencing — design-cc loads KB-documentation-criteria)
- **L1:** File exists; markdown parses; five-column header present.
- **L2:** Grep returns "positive-evidence-string" + five dimension names.
- **L3:** Phase 8's eat-own-dogfood matrix can be authored against this template without further reference.

#### T5.2: Author `check_feature_touch_predicate.py` at `auditing-subagents/scripts/`

- **Layer:** Claude Code
- **Description:** Advisory predicate per ADR-0064 Clause 3. Deterministic for trigger conditions 1 (agent file diff) and 2 (`.mcp.json` tool-surface diff); advisory annotation for conditions 3 and 4 (interpretive read of design / Skill-Coverage Decisions text). Override events emit `transition_name: TRIGGER_OVERRIDE` to state-transitions log via existing `log_state_transition.py`.
- **Dependencies:** T0.3, T3.2 (TRIGGER_OVERRIDE in transition-name template)
- **Estimate:** L
- **Satisfies AC:** AC-FR-6-a (trigger evaluation), AC-FR-6-c (mismatch surfacing path)
- **L1:** File exists; syntax-parses.
- **L2:** Smoke test on a fixture diff exercising conditions 1 and 2 returns deterministic boolean; condition 3/4 fixture returns advisory annotation.
- **L3:** Phase 8 eat-own-dogfood run: predicate invocation correctly identifies condition 1 firing on this R2a run.

#### T5.3: Extend `design-claude-code.md` Phase 2 with the matrix-authoring procedure

- **Layer:** Claude Code
- **Description:** Per cc-design §FR-6: when the feature-touch advisory predicate (T5.2) fires, design-cc MUST author `working/feature/<slug>/agent-roster-impact-matrix.md` before its stage can complete. Cross-reference the active Principle 9 (Phase 2) by name. Mutual cross-reference at AC-FR-8-b also lands here.
- **Dependencies:** T2.2, T5.1, T5.2
- **Estimate:** M
- **Satisfies AC:** AC-FR-6-a, AC-FR-8-b
- **L1:** Phase 2 of design-cc prompt extended; cross-reference to Principle 9 present.
- **L2:** Grep returns "agent-roster-impact-matrix.md" + "Principle 9" references; matrix-deliverable description matches template.
- **L3:** A future feature run touching the agent surface produces the matrix as a Design Composition deliverable.

#### T5.4: Update `recipe-feature-pipeline/SKILL.md` outputs table and Design Composition close gate

- **Layer:** Claude Code
- **Description:** Add the matrix row to design-cc's outputs table; update Stage 7 (Design Composition close) gate description to refuse close if trigger fired and matrix is absent (per AC-FR-6-c).
- **Dependencies:** T5.1, T5.3
- **Estimate:** S
- **Satisfies AC:** AC-FR-6-c
- **L1:** Outputs table contains matrix row; gate-description text updated.
- **L2:** Grep on "agent-roster-impact-matrix" returns the recipe; the close-gate clause references it.
- **L3:** The orchestrator consulting the recipe at Stage 7 refuses close on trigger-fired + matrix-missing.

### Phase 5 Exit Criteria

- Matrix template authored, citable, and exemplary.
- Advisory predicate exists and tested on conditions 1 and 2.
- design-cc procedure and recipe Stage 7 gate enforce matrix presence when trigger fires.
- Mutual cross-reference between Principle 9 and matrix-cell discipline is bidirectional.

## Phase 6 — FR-7 skill-coverage discipline

### Goal

Land the W/H/A trifecta hybrid skill-coverage discipline. Synthesis emits the embedded section per ADR-0065 Clause 1; design-composer reads it for substance review. Section template authored.

### Tasks

#### T6.1: Author `skill-coverage-decisions-section-template.md` at `KB-documentation-criteria/references/templates/`

- **Layer:** Claude Code
- **Description:** New canonical sub-template for the section embedded in `synthesis.md`. One row per new domain concept; columns: concept, decision (a/b/c), justification. (b) rows require W/H/A trifecta (structural mandate per ADR-0065); (a)/(c) rows require substance-heuristic justification (per D-8).
- **Dependencies:** none
- **Estimate:** M
- **Satisfies AC:** AC-FR-7-a (section shape), AC-FR-7-b (justification required), AC-FR-7-c (W/H/A trifecta for new-skill proposals)
- **L1:** Template file exists; markdown parses.
- **L2:** Grep returns "W/H/A" + each of the three decision types (a/b/c).
- **L3:** Phase 8 synthesis back-fill can author six (a) decisions against this template without further reference.

#### T6.2: Extend `synth-synthesizer.md` with the Skill-Coverage Decisions emission procedure

- **Layer:** Claude Code
- **Description:** Procedure-text addition: when synthesis identifies one or more new domain concepts, emit the Skill-Coverage Decisions section in `synthesis.md` per the template. Section-name references ADR-0065 Clause 1 (canonical embedding location).
- **Dependencies:** T6.1
- **Estimate:** S
- **Satisfies AC:** AC-FR-7-a
- **L1:** Procedure block present in synth-synthesizer prompt.
- **L2:** Grep returns "Skill-Coverage Decisions" emission reference + ADR-0065 citation.
- **L3:** Future synthesis run identifying a new concept emits the section in `synthesis.md`.

#### T6.3: Extend `design-composer.md` with the substance-review procedure

- **Layer:** Claude Code
- **Description:** Procedure-text addition: at Blueprint composition, design-composer reads each Skill-Coverage Decisions row; blocks composition close if (b) row is missing W/H/A trifecta headings (structural mandate) or if (a)/(c) row's justification fails substance heuristic (per D-8). The substance heuristic is the inherited D-8 framing — justification text must actually answer the W/H/A questions.
- **Dependencies:** T6.1
- **Estimate:** M
- **Satisfies AC:** AC-FR-7-b
- **L1:** Procedure block present in design-composer prompt.
- **L2:** Grep returns substance-heuristic + structural-mandate distinction; ADR-0065 cited by name.
- **L3:** A future synthesis with an empty or bare-cell row causes design-composer to block composition close.

### Phase 6 Exit Criteria

- Skill-Coverage Decisions section template authored.
- Both ends (synthesizer emits; composer reads) have the procedure extension.
- ADR-0065 Clause 1 honored: section embedded in `synthesis.md`, not a standalone file.

## Phase 7 — FR-10 SA-14 audit-subagents rule

### Goal

Realize the FR-10 backstop: new SA-14 rule entry (per D-R2a-5 / Q-CC-4 ratification) plus its audit script. Folds I-AA-005 minor (SA-NN count fix in `SKILL.md` description string).

### Tasks

#### T7.1: Author `audit_feature_touch_coverage.py` at `auditing-subagents/scripts/`

- **Layer:** Claude Code
- **Description:** New script per cc-design §FR-10. Reads `working/feature/<slug>/` for trigger evidence (consults T5.2 predicate output if present); checks for `agent-roster-impact-matrix.md` presence; checks row count equals current `.claude/agents/*.md` count; emits `BLOCKER` finding per AC-FR-10-a / AC-FR-10-b carrying the NFR-8 four-field shape.
- **Dependencies:** T5.1 (matrix template; row-count reference), T5.2 (trigger evidence), T1.1 (severity vocabulary), T0.3
- **Estimate:** M
- **Satisfies AC:** AC-FR-10-a, AC-FR-10-b, AC-FR-10-c (no-op when surface not touched), AC-NFR-8-a
- **L1:** Script exists; syntax-parses.
- **L2:** Smoke test against (a) fixture with matrix present and row-count parity → no finding; (b) fixture with matrix missing AND trigger evidence → BLOCKER; (c) fixture with no trigger evidence → no finding (no-op per AC-FR-10-c).
- **L3:** Phase 9 deliverable packaging executes this rule against this run's own directory and passes.

#### T7.2: Add SA-14 rule entry to `auditing-subagents/SKILL.md` (and reference text)

- **Layer:** Claude Code
- **Description:** New rule entry SA-14 ("feature-touch-coverage") in the SKILL.md catalog. Includes I-AA-005 fold-in: correct any stale SA-NN count number in the SKILL.md description string to reflect SA-14 as the latest rule. Companion reference text under `auditing-subagents/references/` documents the rule's predicate, severity, and remediation steps.
- **Dependencies:** T7.1
- **Estimate:** S
- **Satisfies AC:** AC-FR-10-a, AC-FR-10-b
- **L1:** New SA-14 entry present in SKILL.md; reference file present.
- **L2:** Grep on "SA-14" returns the entry; SKILL.md description count is consistent (I-AA-005 closed); no orphaned SA-15+ references.
- **L3:** A future auditing-subagents invocation enumerates 14 rules and includes feature-touch-coverage.

### Phase 7 Exit Criteria

- SA-14 rule entry exists in catalog; audit script exists and tested.
- I-AA-005 minor closed (SA-NN count fix applied).
- Backstop fires at pre-deliverable packaging time on missing matrix.

## Phase 8 — Eat-own-dogfood (this run's matrix + decisions)

### Goal

Apply this run's own FR-6 and FR-7 contracts to itself. Authors the actual 37-row × 5-dimension matrix artifact under this run's working directory; ratifies the six skill-coverage decisions (already back-filled at cycle 1 into `synthesis.md` per I-AA-004). This is the contract-validation event by design.

### Tasks

#### T8.1: Author `working/feature/pipeline-design-time-discipline-r1/agent-roster-impact-matrix.md`

- **Layer:** Claude Code
- **Description:** Author this run's own roster matrix per Phase 5's template (T5.1). Row count = baseline-pinned `.claude/agents/*.md` count from T0.2 (37). Five cells per row: tools / skills / model / effort / prompt body. Per-cell schema: `<value> — <positive-evidence-string>`. The six agents touched by this run (`review-architecture-auditor`, `design-claude-code`, `design-composer`, `synth-synthesizer`, `discovery-codebase-researcher`, `execute-orchestrator`) carry concrete change values per Blueprint §Change impact map; the other 31 carry `no-change — <positive evidence string>` per the active Principle 9 substance test. Exemplar shape: `Issues/per-agent-design-evaluation-gap/evidence/agent-roster-impact-matrix.md`.
- **Dependencies:** T0.2, T5.1, T5.2, T5.3
- **Estimate:** L (37 rows × 5 cells = 185 cells; ~11 min wall-clock at NFR-7 linear-extrapolation rate)
- **Satisfies AC:** AC-FR-6-a, AC-FR-6-b, AC-FR-6-c, AC-FR-6-d, AC-NFR-7-a (authoring-time measurement evidence)
- **L1:** Matrix file present at the canonical working-directory path; row count = 37 (or T0.2 baseline); five-column header present.
- **L2:** Every cell carries `<value> — <evidence>` form; no bare `no-change`. Grep for ` — ` returns 185 hits in cell-position. First-write to last-write timestamps recorded for NFR-7 measurement.
- **L3:** SA-14 audit (T7.1) invoked against this directory passes (matrix present + row-count parity). Dogfood validation event records the pass per I-AA-007.

#### T8.2: Verify Skill-Coverage Decisions section in `synthesis.md` (back-filled cycle 1)

- **Layer:** Claude Code
- **Description:** Verification-only task per Blueprint §Eat-own-dogfood deliverables. The six skill-coverage decisions for this run's new domain concepts were back-filled into `synthesis.md` v1.0.1+ during cycle-1 reconciliation per I-AA-004 + ADR-0065 Clause 1. This task confirms (a) the section is present in `synthesis.md`, (b) it contains six rows, (c) all six resolve to type (a) existing-skill, (d) each justification passes the substance heuristic per D-8.
- **Dependencies:** T6.1, T6.3 (substance-heuristic procedure must exist for verification anchor)
- **Estimate:** S
- **Satisfies AC:** AC-FR-7-a, AC-FR-7-b
- **L1:** "Skill-Coverage Decisions" section header present in `synthesis.md`.
- **L2:** Six rows; each names a host skill + positive-evidence sentence; grep returns the six concept labels (design-realization audit / agent-roster matrix / skill-coverage decision / Principle 9 active reframing / Blocks-X marker grammar / matrix-missing audit rule).
- **L3:** design-composer's substance-review procedure (T6.3) executed against this section returns no blocker.

### Phase 8 Exit Criteria

- `agent-roster-impact-matrix.md` exists with 37 rows × 5 evidence-bearing cells.
- `synthesis.md` Skill-Coverage Decisions section verified.
- Self-applied contracts pass — no in-run contract revision required (or, if revision required, captured as Blueprint OI per kill-criteria — Risk row 3).
- Dogfood validation evidence captured for I-AA-007 closure at packaging.

## Phase 9 — Rollout / deliverable packaging

### Goal

Seal the deliverable archive; record success-criteria evidence; honor the SPLIT-RECORD R2a-runs-first ordering so the populated severity bridge is published for R2b inheritance. Folds I-AA-007 INFO closure.

### Tasks

#### T9.1: Run SA-14 audit against this run's working directory

- **Layer:** Claude Code
- **Description:** Execute `audit_feature_touch_coverage.py` (T7.1) against `working/feature/pipeline-design-time-discipline-r1/`. Expect no findings (matrix present + 37-row parity per T8.1). Records the dogfood-validation evidence per I-AA-007.
- **Dependencies:** T7.1, T8.1
- **Estimate:** S
- **Satisfies AC:** AC-FR-10-a, AC-FR-10-b (dogfood evidence path)
- **L1:** Script exits 0; no `audit-issues.json` BLOCKER entries.
- **L2:** Script's stdout names the directory + matrix file + row count.
- **L3:** I-AA-007 INFO entry transitioned to `closed` in audit-issues with the script's pass output as evidence.

#### T9.2: Author "What changed for future feature authors" communication summary

- **Layer:** Claude Code
- **Description:** One-page summary referenced from the deliverable archive. Names the six mechanisms by FR number, the two new ADRs (0064, 0065), the populated severity bridge for R2b inheritance, and the inherited three ADRs (0059, 0061, 0063).
- **Dependencies:** all prior phases
- **Estimate:** S
- **Satisfies AC:** N/A (PRD §Rollout Plan communication plan deliverable; no AC)
- **L1:** File present in the deliverable archive directory.
- **L2:** Each of FR-1/6/7/8/9/10 named; both new ADRs cited; severity-bridge publication noted.
- **L3:** A future feature author reading the summary can navigate to all named affordances.

#### T9.3: Record success-criteria evidence in the run summary

- **Layer:** Claude Code
- **Description:** PRD §Success Criteria evidence collection: (a) presence of `agent-roster-impact-matrix.md` for this run (T8.1 confirms); (b) skill-coverage decisions per new concept (T8.2 confirms); (c) eat-own-dogfood compliance; (d) severity-taxonomy bridge published for R2b (T1.1/T1.2 confirms). Recorded in pipeline-run-summary per template.
- **Dependencies:** T8.1, T8.2, T1.1, T1.2
- **Estimate:** S
- **Satisfies AC:** N/A (PRD §Success Criteria evidence)
- **L1:** Run summary file present.
- **L2:** Each success-criteria row points at a file path + a date.
- **L3:** Deliverable archive sealed per `deliverable-archive-spec.md`; queued R2b run can read the bridge content without further work.

### Phase 9 Exit Criteria

- SA-14 audit against this run's directory passes (dogfood pass recorded).
- "What changed" summary authored and archived.
- Run-summary success-criteria evidence captured.
- I-AA-005 (closed in Phase 7) and I-AA-007 (closed here) both reflected in deliverable archive.
- Deliverable archive sealed; R2b kickoff unblocked per SPLIT-RECORD.

---

## Cross-Phase Dependencies

Phase 0 (Setup) precedes all feature-delivery phases. Phase 1 (severity bridge content) precedes Phases 4 and 7 (FR-1 and FR-10 cite the bridge by name) and informs Phase 3 (FR-9 emits per the bridge vocabulary). Phases 2, 3, 5, 6 are independent of each other and can parallelize. Phase 7 depends on Phase 5 (matrix template + predicate). Phase 8 (eat-own-dogfood) depends on Phases 0, 5, 6 (the contracts being self-applied). Phase 9 (rollout) depends on every prior phase.

```
T0.1 ──┬─► T1.1 ─► T1.2 ─┬─► T4.1, T4.2 ──► T4.3 ──┐
       │                  │                          │
       │                  ├─► T7.1 (after T5.1+T5.2)─┤
       │                  │                          │
       │                  └─► T3.1..T3.4 (Phase 3)──┤
       │                                             │
T0.2 ──┤                                             ├─► T8.1 ─► T9.1 ─► T9.2 ─► T9.3
       │                                             │       │
       │   T2.1 ─► T2.2 ──────────► T5.3 ──► T5.4 ──┤       │
       │                                             │       │
       │   T5.1 ──┬───► T5.3 ─► T8.1 ────────────────┤       │
       │          │                                  │       │
       │          ├───► T7.1 ─► T7.2 ────────────────┤       │
       │                                             │       │
       │   T5.2 ──┘                                  │       │
       │                                             │       │
       │   T6.1 ──┬───► T6.2                         │       │
       │          │                                  │       │
       │          └───► T6.3 ──► T8.2 ───────────────┘       │
       │                                                     │
T0.3 ──┴─────────────────────────────────────────────────────┘
```

**Load-bearing cross-phase dependencies (orchestrator must honor):**

1. **Phase 1 → Phase 4 / Phase 7 / Phase 3.** Severity bridge content must land before FR-1, FR-10, and FR-9 reference it. The Blueprint's Q-CC-5 ratification makes this binding: consumers-first would replay the placeholder-leakage failure mode FR-1 is designed to catch.
2. **Phase 5 → Phase 7.** SA-14 audit (T7.1) needs the matrix template (T5.1) for the row-count reference and the predicate (T5.2) for trigger evidence. Without Phase 5, Phase 7's audit cannot mechanically determine which features need the matrix.
3. **Phase 2 → Phase 5.** AC-FR-8-b's mutual cross-reference requires Principle 9's active framing (T2.1) before design-cc's procedure extension (T5.3) can cite the matrix-cell discipline by name.
4. **Phases 5 + 6 → Phase 8.** Eat-own-dogfood matrix authoring (T8.1) and skill-coverage verification (T8.2) consume the contracts realized in Phases 5 and 6 respectively.

**Parallelization opportunities:**

- Phase 2 (FR-8) is independent of Phase 1; can run in parallel.
- Phase 3 (FR-9) depends only on Phase 1's bridge for severity vocabulary; tasks T3.1–T3.4 internally serialize.
- Phases 5 (FR-6) and 6 (FR-7) can run in parallel after Phase 2 lands (T2.2 → T5.3 is the only cross-phase tie).

**R2b consumer notes (informational; no R2a dependency):**

- T1.1 / T1.2 (severity bridge) is consumed by R2b's FR-4 and FR-5. R2b kickoff is gated on this run's deliverable archive per SPLIT-RECORD; no in-flight coordination needed.
- T5.1 (matrix template) is exercised by R2b on its own agent-touching diff. R2b consumes the template as-is; no R2a-side R2b accommodation needed.

## L1/L2/L3 Verification Discipline

Standard per `KB-documentation-criteria` plan-template — every task above carries L1/L2/L3 entries. The convention applied:

- **L1 (cheapest):** File presence, syntax/markdown parse, grep for a specific anchor string.
- **L2 (functional):** Smoke test against a synthetic fixture; cross-reference resolves; semantic content of the file confirmed (e.g., five-column table actually present, not just file-present).
- **L3 (integration):** End-to-end exercise — a future feature run, or this run's own dogfood execution, exercises the affordance as designed.

Phase Validators (`test-phase-validator-author`-authored downstream) aggregate the L3 verifications across each phase's tasks against the Phase Exit Criteria.

## Acceptance Test Cross-Reference

Every PRD AC is scheduled in exactly one Phase (the phase where it is first verifiable). The R2b-deferred / inherited ACs do not appear here.

| AC ID (from PRD) | Satisfied by task(s) | Phase |
|---|---|---|
| AC-FR-1-a | T1.1, T4.3 | 1 + 4 |
| AC-FR-1-b | T4.3 | 4 |
| AC-FR-1-c | T4.1, T4.2, T4.3 | 4 |
| AC-FR-6-a | T5.1, T5.2, T5.3, T8.1 | 5 + 8 |
| AC-FR-6-b | T5.1, T8.1 | 5 + 8 |
| AC-FR-6-c | T5.2, T5.4, T8.1 | 5 + 8 |
| AC-FR-6-d | T5.1, T8.1 | 5 + 8 |
| AC-FR-7-a | T6.1, T6.2, T8.2 | 6 + 8 |
| AC-FR-7-b | T6.1, T6.3, T8.2 | 6 + 8 |
| AC-FR-7-c | T6.1 | 6 |
| AC-FR-8-a | T2.1 | 2 |
| AC-FR-8-b | T2.2, T5.3 | 2 + 5 |
| AC-FR-9-a | T3.1, T3.3, T3.4 | 3 |
| AC-FR-9-b | T3.4, T1.1 (severity) | 3 |
| AC-FR-9-c | T3.1, T3.2 | 3 |
| AC-FR-10-a | T7.1, T7.2, T9.1 | 7 + 9 |
| AC-FR-10-b | T7.1, T7.2, T9.1 | 7 + 9 |
| AC-FR-10-c | T7.1 | 7 |
| AC-NFR-1-a | T4.3 | 4 |
| AC-NFR-7-a | T8.1 | 8 |
| AC-NFR-8-a | T1.2, T4.3, T7.1 | 1 + 4 + 7 |
| AC-NFR-9-a | T5.1, T6.1 | 5 + 6 |

Every PRD AC has at least one task. Every task satisfies at least one AC OR is explicit setup (Phase 0 tasks). `review-cross-artifact-auditor` will check this table for orphan ACs and orphan tasks.

## Estimation Methodology

T-shirt sizes S / M / L applied:

- **S (Small):** Single-file edit; <30 minutes wall-clock; no new logic. Example: T2.1 (one-sentence replacement) or T7.2 (rule-entry addition).
- **M (Medium):** Multi-file edit OR single new script with smoke test; 30 min – 2 hr wall-clock. Example: T3.1 (new parser script + smoke fixtures).
- **L (Large):** Substantive new artifact OR comprehensive task. Example: T5.2 (advisory predicate with deterministic + advisory branches) or T8.1 (37-row matrix authoring).

Phase total effort (sum of task sizes): Phase 0 (3×S), Phase 1 (M+S), Phase 2 (2×S), Phase 3 (M+S+S+M), Phase 4 (M+M+M), Phase 5 (M+L+M+S), Phase 6 (M+S+M), Phase 7 (M+S), Phase 8 (L+S), Phase 9 (3×S). Total: ~31 tasks; aggregate wall-clock comfortably within the 4-cycle reconciliation cap (per PRD §Constraints and Blueprint §Risks first row mitigation).

## Resourcing Posture

Single-layer (Claude Code only) → single owner stage: `design-claude-code` consumes this Plan via `finalize-task-decomposer`'s DAG output. No team / individual specialization is needed since every task touches Claude Code project filesystem assets. Tasks are written self-contained (no assumed cross-layer domain knowledge) so any contributor with project access can execute.

## Open Items (Pending Cross-Artifact Audit)

Items the plan-author surfaced but could not resolve from the Blueprint alone. Each becomes an open item for the Cross-Artifact Audit (review-cross-artifact-auditor at the next stage):

- **OP-Plan-1 — Phase-validator authoring timing for Phase 0 setup-only tasks.** The plan-template's Phase Validator note says validators "test the Phase Exit Criteria." Phase 0 exit criteria are observable but trivial (file-existence checks). The `test-phase-validator-author` may choose to fold Phase 0 into Phase 1's validator scope or author a stub validator. Routed to `test-phase-validator-author`.

- **OP-Plan-2 — NFR-1 5000 ms benchmarking harness location.** AC-NFR-1-a is verified at T4.3's L3 entry but the Plan does not commit to a benchmark fixture location. Either (a) inline timing in the auditor's own logging or (b) a benchmark script at `auditing-shared/scripts/`. Routed to `test-acceptance-author`.

- **OP-Plan-3 — Phase 8 wall-clock measurement methodology for AC-NFR-7-a.** The PRD's AC-NFR-7-a names "matrix file's first-write to last-write timestamps in the run state log" — Plan T8.1's L2 entry mirrors this but the run-state-log emission path is not Plan-committed. Routed to `test-acceptance-author` for the AT mechanics; T8.1's L2 evidence is the proxy until then.

## Update History

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-05-26 | plan-author | Initial Plan for R2a — 10 phases, 31 tasks. Honors Blueprint v1.0.1 §Implementation plan sequencing (D-R2a-6 bridge-first). Cycle-1 reconciliation patches (I-AA-001..006) baked into Blueprint; I-AA-005 fold-in scheduled at T7.2; I-AA-007 closure scheduled at T9.1. Eat-own-dogfood deliverables scheduled at Phase 8. AC-to-Phase mapping table covers all 22 ACs across FR-1, FR-6, FR-7, FR-8, FR-9, FR-10, NFR-1, NFR-7, NFR-8, NFR-9. |

---

*End of Plan v1.0.0 for `pipeline-design-time-discipline-r1`. Next stages (in parallel per recipe): `test-acceptance-author` consumes this Plan for EARS acceptance tests; `test-phase-validator-author` consumes this Plan for phase validators. After both complete, `review-cross-artifact-auditor` runs diff-mode consistency check across Blueprint ↔ Plan ↔ Tests ↔ PVs.*
