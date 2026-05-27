---
id: ATests-pipeline-design-time-discipline-r1
version: 1.0.0
status: draft
doc_type: acceptance-tests
feature_slug: pipeline-design-time-discipline-r1
derived_from:
  - working/feature/pipeline-design-time-discipline-r1/prd-v1.md
  - working/feature/pipeline-design-time-discipline-r1/blueprint-v1.md
  - working/feature/pipeline-design-time-discipline-r1/plan-v1.md
predecessor: null
parent_run: pipeline-cross-artifact-discipline-r1
related_run: pipeline-gate-validator-hardening-r1
total_tests: 38
ac_count_covered: 22
generated: 2026-05-26T19:15:00Z
generated_by: test-acceptance-author
---

# Acceptance Tests: Pipeline Design-Time Discipline (R2a)

## Purpose

Concrete test specifications for every EARS Acceptance Criterion in PRD v1.0.0 (FR-1, FR-6, FR-7, FR-8, FR-9, FR-10; NFR-1, NFR-7, NFR-8, NFR-9). One row per AC at minimum; multiple rows where the AC's EARS form (multi-trigger `When`, multi-configuration `Where`, multi-condition `Ubiquitous`) demands it. Test specs are consumed by `review-cross-artifact-auditor` (Blueprint ↔ Tests alignment) and by `finalize-task-decomposer` (which decomposes each test into a test-implementation task).

The PRD's ACs cluster into five mechanism families plus four NFR ACs:

- FR-1 (3 ACs) — auditor design-realization dimension
- FR-6 (4 ACs) — agent-roster-impact-matrix contract
- FR-7 (3 ACs) — skill-coverage decision discipline
- FR-8 (2 ACs) — Principle 9 active reframing
- FR-9 (3 ACs) — Blocks-X marker enforcement
- FR-10 (3 ACs) — SA-14 audit-subagents rule
- NFR-1 / NFR-7 / NFR-8 / NFR-9 (1 AC each) — performance, scalability, operability, devex

Total: 22 PRD ACs → 38 acceptance tests.

## Coverage matrix

| AC ID | EARS form | Test IDs | Layer |
|---|---|---|---|
| AC-FR-1-a | When | AT-001, AT-002 | Claude Code |
| AC-FR-1-b | When | AT-003 | Claude Code |
| AC-FR-1-c | When (ubiquitous structural) | AT-004 | Claude Code |
| AC-FR-6-a | When (4 distinct trigger conditions) | AT-005, AT-006, AT-007, AT-008 | Claude Code |
| AC-FR-6-b | When | AT-009 | Claude Code |
| AC-FR-6-c | If…then | AT-010 | Claude Code |
| AC-FR-6-d | If…then | AT-011 | Claude Code |
| AC-FR-7-a | When | AT-012 | Claude Code |
| AC-FR-7-b | If…then | AT-013, AT-014 | Claude Code |
| AC-FR-7-c | When | AT-015 | Claude Code |
| AC-FR-8-a | When | AT-016 | Claude Code |
| AC-FR-8-b | When (mutual cross-reference) | AT-017 | Claude Code |
| AC-FR-9-a | When | AT-018, AT-019 | Claude Code |
| AC-FR-9-b | If…then | AT-020 | Claude Code |
| AC-FR-9-c | Ubiquitous | AT-021 | Claude Code |
| AC-FR-10-a | When | AT-022, AT-023 | Claude Code |
| AC-FR-10-b | When | AT-024, AT-025 | Claude Code |
| AC-FR-10-c | When (negative path) | AT-026 | Claude Code |
| AC-NFR-1-a | When (performance) | AT-027 | Claude Code |
| AC-NFR-7-a | When (scalability) | AT-028 | Claude Code |
| AC-NFR-8-a | When (ubiquitous shape) | AT-029, AT-030, AT-031, AT-032 | Claude Code |
| AC-NFR-9-a | Ubiquitous (grep predicate) | AT-033, AT-034 | Claude Code |

Plus 4 cross-cutting / dogfood verification tests (AT-035..AT-038) that exercise the FR-6/FR-7/FR-10 contracts against this run's own artifacts.

## Test suite overview

| Test type | Count | Notes |
|---|---|---|
| Unit (Python script tests) | 17 | Parser / predicate / validator / audit-script tests; pattern matches existing `smoke_test_auditing_shared.py` |
| Integration (end-to-end against synthetic feature-run fixtures) | 9 | Fixture-based feature-directory + ADR-set inputs through full audit / orchestrator / design-cc procedures |
| Structural / grep-based (file-content assertions) | 8 | NFR-9 grep predicate, AC-FR-8-a / b cross-reference assertions, template structural checks |
| Performance | 1 | AC-NFR-1-a 5000 ms budget |
| Scalability / wall-clock budget | 1 | AC-NFR-7-a authoring-time budget (manual-observation supplement) |
| Eat-own-dogfood self-verification | 2 | This run's own matrix + skill-coverage decisions exercised by SA-14 + design-composer substance review |

Layer distribution: 38 / 38 Claude Code (single-layer feature).

## Test specifications

---

### AT-001 — FR-1 auditor emits BLOCKER when ADR prescription diverges from eventual file

- **Maps to AC:** AC-FR-1-a
- **Test type:** Integration
- **Layer:** Claude Code
- **Preconditions:**
  - Phase 1 (severity bridge content) and Phase 4 (FR-1 design-realization audit dimension) are landed.
  - Synthetic feature fixture exists at `tests/fixtures/at-001-fr-1-divergence/` containing: one ADR file with a `.prescriptions.yaml` companion declaring `target_path: foo.txt` and `assertion: contains "active"`; one `foo.txt` file containing `defensive` (not `active`).
- **Steps:**
  1. Arrange: load the synthetic fixture as the auditor's input feature directory.
  2. Act: invoke `review-architecture-auditor` Lens 4 (design-realization audit) inline against the fixture.
  3. Assert: emitted `audit-issues.json` contains exactly one issue with `severity: BLOCKER`, `rule` referencing the ADR's id, `target` equal to `foo.txt`, `divergence` naming "expected `active`, found `defensive`", and `next_action` populated with a concrete action.
- **Expected outcome:** Auditor emits one BLOCKER finding bound to the ADR id; finding carries the NFR-8 four-field shape; no other issues raised.
- **Negative-path companion:** AT-003 (no-companion case).
- **Data dependencies:** Synthetic ADR + `.prescriptions.yaml` + diverging implementation file.
- **Determinism notes:** Deterministic file-content compare; no time-of-day dependency.

---

### AT-002 — FR-1 auditor BLOCKER finding cites the inherited ADR-0061 severity vocabulary

- **Maps to AC:** AC-FR-1-a
- **Test type:** Unit (assertion on severity-emission code path)
- **Layer:** Claude Code
- **Preconditions:** Phase 1 bridge content (T1.1) and Phase 4 auditor procedure (T4.3) landed.
- **Steps:**
  1. Arrange: build the auditor's severity emitter against an in-memory divergence record.
  2. Act: emit a finding for the divergence.
  3. Assert: the `severity` field equals `BLOCKER` (auditor vocabulary); grep the bridge file (`KB-review-disciplines/references/severity-taxonomy.md`) for `BLOCKER` returns the row; cross-link is intact.
- **Expected outcome:** Severity literal `BLOCKER` emitted; bridge table contains a `BLOCKER` row mapping to `critical` / `blocking`.
- **Negative-path companion:** N/A (positive-only assertion).
- **Data dependencies:** Bridge file populated per T1.1.
- **Determinism notes:** Deterministic literal compare.

---

### AT-003 — FR-1 auditor completes as no-op when feature has zero `.prescriptions.yaml` companions

- **Maps to AC:** AC-FR-1-b
- **Test type:** Integration
- **Layer:** Claude Code
- **Preconditions:** Phase 4 landed; synthetic feature fixture exists at `tests/fixtures/at-003-fr-1-no-companions/` with one or more ADRs but no `.prescriptions.yaml` files.
- **Steps:**
  1. Arrange: load fixture as auditor's feature directory input.
  2. Act: invoke Lens 4 design-realization audit phase.
  3. Assert: no design-realization issue emitted (issue list filtered by `rule starts with "FR-1"` is empty); auditor exits successfully; other lenses run unaffected.
- **Expected outcome:** Lens 4 is a no-op; auditor's overall verdict not changed by Lens 4.
- **Negative-path companion:** AT-001 (positive divergence case).
- **Data dependencies:** Fixture with ADRs but no companions.
- **Determinism notes:** Deterministic.

---

### AT-004 — FR-1 auditor's contract document names the companion-file mechanism

- **Maps to AC:** AC-FR-1-c
- **Test type:** Structural (grep)
- **Layer:** Claude Code
- **Preconditions:** Phase 4 T4.2 (Lens 4 added to KB) landed.
- **Steps:**
  1. Arrange: read `.claude/skills/KB-review-disciplines/references/architecture-audit.md`.
  2. Act: grep for "Lens 4" and "ADR-0059" within the file.
  3. Assert: both matches present in the same section; `.prescriptions.yaml` literal also present; cross-reference to ADR-0059 resolves to a real file in `adrs/`.
- **Expected outcome:** Contract document names the companion-file mechanism by ADR id and by file-extension literal.
- **Negative-path companion:** N/A.
- **Data dependencies:** Architecture-audit reference file.
- **Determinism notes:** Deterministic grep.

---

### AT-005 — FR-6 trigger condition 1 (agent file diff) fires the matrix requirement

- **Maps to AC:** AC-FR-6-a
- **Test type:** Unit (`check_feature_touch_predicate.py`)
- **Layer:** Claude Code
- **Preconditions:** Phase 5 T5.2 (predicate script) landed.
- **Steps:**
  1. Arrange: build a fixture diff that modifies `.claude/agents/example-agent.md`.
  2. Act: invoke `check_feature_touch_predicate.py` against the fixture.
  3. Assert: predicate returns `triggered=True` with `condition=1` and deterministic (not advisory) classification.
- **Expected outcome:** Boolean True with condition=1; deterministic flag set.
- **Negative-path companion:** AT-026 (no-trigger case).
- **Data dependencies:** Synthetic diff fixture.
- **Determinism notes:** Deterministic.

---

### AT-006 — FR-6 trigger condition 2 (`.mcp.json` tool-surface diff) fires the matrix requirement

- **Maps to AC:** AC-FR-6-a
- **Test type:** Unit
- **Layer:** Claude Code
- **Preconditions:** Phase 5 T5.2 landed.
- **Steps:**
  1. Arrange: build a fixture diff that modifies `.mcp.json` to add a tool to an allowlisted MCP server's surface.
  2. Act: invoke predicate.
  3. Assert: `triggered=True` with `condition=2` and deterministic.
- **Expected outcome:** Boolean True with condition=2; deterministic.
- **Negative-path companion:** AT-026.
- **Data dependencies:** Two `.mcp.json` versions for diff.
- **Determinism notes:** Deterministic diff compare.

---

### AT-007 — FR-6 trigger condition 3 (new skill loaded by existing agents) fires as advisory

- **Maps to AC:** AC-FR-6-a
- **Test type:** Unit
- **Layer:** Claude Code
- **Preconditions:** Phase 5 T5.2 landed.
- **Steps:**
  1. Arrange: build a fixture diff that creates `.claude/skills/new-skill/SKILL.md` AND a design document indicating an existing agent loads it.
  2. Act: invoke predicate.
  3. Assert: `triggered=True` with `condition=3`, `mode=advisory` (per ADR-0064 Clause 3 hybrid contract); human-ratification flag set.
- **Expected outcome:** Advisory annotation; not a hard deterministic signal.
- **Negative-path companion:** AT-026.
- **Data dependencies:** Synthetic skill + design-doc fixture.
- **Determinism notes:** Output is advisory by design — predicate's text is deterministic, but the trigger semantics include explicit "requires human ratification."

---

### AT-008 — FR-6 trigger condition 4 (new domain concept naming existing agent as consumer) fires as advisory

- **Maps to AC:** AC-FR-6-a
- **Test type:** Unit
- **Layer:** Claude Code
- **Preconditions:** Phase 5 T5.2 landed; Phase 6 T6.1 (Skill-Coverage Decisions template) landed so the predicate has a section shape to read.
- **Steps:**
  1. Arrange: build a fixture `synthesis.md` containing a Skill-Coverage Decisions section whose row names an existing `.claude/agents/<name>.md` agent as a downstream consumer.
  2. Act: invoke predicate.
  3. Assert: `triggered=True` with `condition=4`, `mode=advisory`.
- **Expected outcome:** Advisory annotation citing the concept and the agent it names.
- **Negative-path companion:** AT-026.
- **Data dependencies:** Synthetic synthesis.md fixture.
- **Determinism notes:** Advisory by design.

---

### AT-009 — FR-6 matrix row count and cell discipline validate

- **Maps to AC:** AC-FR-6-b
- **Test type:** Unit (matrix-validation helper, exercised by SA-14)
- **Layer:** Claude Code
- **Preconditions:** Phase 5 T5.1 (template) landed; SA-14 audit script (T7.1) landed.
- **Steps:**
  1. Arrange: synthetic feature fixture at `tests/fixtures/at-009-fr-6-valid-matrix/` containing a valid `agent-roster-impact-matrix.md` whose row count equals `ls .claude/agents/*.md | wc -l` at audit time, and whose every cell carries `<value> — <evidence>` form.
  2. Act: invoke `audit_feature_touch_coverage.py` against the fixture.
  3. Assert: no findings emitted; SA-14 reports pass.
- **Expected outcome:** Validation passes; row count = agent count; each cell has the dash-separator + non-empty evidence.
- **Negative-path companion:** AT-010 (row-count mismatch), AT-011 (bare `no-change`).
- **Data dependencies:** Synthetic feature fixture with valid matrix.
- **Determinism notes:** Deterministic.

---

### AT-010 — FR-6 row-count divergence blocks Design Composition with BLOCKER

- **Maps to AC:** AC-FR-6-c
- **Test type:** Integration
- **Layer:** Claude Code
- **Preconditions:** Phase 5 T5.4 (recipe Stage 7 gate) landed; T7.1 (audit script) landed.
- **Steps:**
  1. Arrange: synthetic feature fixture whose `agent-roster-impact-matrix.md` has row count 35 while `.claude/agents/*.md` has 37 files at audit time.
  2. Act: invoke `audit_feature_touch_coverage.py`.
  3. Assert: exactly one finding with `severity: BLOCKER`, `rule: feature-touch-coverage`, `target` naming the matrix file, `divergence` reporting "matrix rows=35 ; .claude/agents count=37", `next_action` naming the rows to add.
- **Expected outcome:** BLOCKER emitted; Design Composition gate (recipe Stage 7) refuses close.
- **Negative-path companion:** AT-009 (matched case).
- **Data dependencies:** Mismatched-row-count fixture.
- **Determinism notes:** Deterministic.

---

### AT-011 — FR-6 bare `no change` cell triggers revision requirement

- **Maps to AC:** AC-FR-6-d
- **Test type:** Unit (cell-content validator)
- **Layer:** Claude Code
- **Preconditions:** Phase 5 T5.1 (template) + T5.3 (design-cc procedure) landed.
- **Steps:**
  1. Arrange: synthetic matrix file where one row contains a cell with literal `no change` (no dash, no evidence string).
  2. Act: invoke cell-content validation (component of SA-14 or design-cc gate logic).
  3. Assert: validation flags the offending cell with `severity: BLOCKER`, `target` naming the row+column, `next_action: "add positive-evidence string per ADR-0064 Clause 2"`.
- **Expected outcome:** Bare `no change` rejected; design-cc procedure refuses to mark Design Composition complete.
- **Negative-path companion:** AT-009.
- **Data dependencies:** Matrix fixture with bare-value cell.
- **Determinism notes:** Deterministic regex-based check (positive-evidence string = cell content matching `.+ — .+` and the right-hand side non-empty after trim).

---

### AT-012 — FR-7 synthesis with new domain concept emits Skill-Coverage Decisions section

- **Maps to AC:** AC-FR-7-a
- **Test type:** Integration
- **Layer:** Claude Code
- **Preconditions:** Phase 6 T6.1 (template) + T6.2 (synthesizer procedure) landed.
- **Steps:**
  1. Arrange: synthetic synthesis input naming one new domain concept ("rate-limit budgeting") not in the project's KB inventory.
  2. Act: invoke `synth-synthesizer` procedure (or dry-run the new procedure block).
  3. Assert: emitted `synthesis.md` contains a `## Skill-Coverage Decisions` section with exactly one decision row matching the template (columns: concept, decision, justification).
- **Expected outcome:** Section present with one row keyed to the new concept.
- **Negative-path companion:** N/A (positive-only; absent-concept case is silently no-op).
- **Data dependencies:** Synthesis fixture introducing one new concept.
- **Determinism notes:** Deterministic.

---

### AT-013 — FR-7 design-composer blocks on Skill-Coverage row missing W/H/A trifecta for (b) decision

- **Maps to AC:** AC-FR-7-b
- **Test type:** Integration
- **Layer:** Claude Code
- **Preconditions:** Phase 6 T6.3 (design-composer procedure) landed.
- **Steps:**
  1. Arrange: synthetic `synthesis.md` containing a Skill-Coverage row of type (b) "propose new skill" whose justification is missing one or more of the W / H / A headings.
  2. Act: invoke design-composer Blueprint-composition pre-check.
  3. Assert: composer emits a blocker; finding names which heading is missing; composition does not advance.
- **Expected outcome:** Composition blocked at structural check (mandate for type (b)).
- **Negative-path companion:** AT-014 (substance-heuristic path), AT-015 (W/H/A complete case).
- **Data dependencies:** Synthesis fixture with incomplete (b) row.
- **Determinism notes:** Deterministic structural check (regex / heading presence).

---

### AT-014 — FR-7 design-composer applies substance heuristic to (a) / (c) decision rows

- **Maps to AC:** AC-FR-7-b
- **Test type:** Manual review checklist (substance heuristic is not fully machine-testable; D-8 / ADR-0065 framing)
- **Layer:** Claude Code
- **Preconditions:** Phase 6 T6.3 landed; reviewer-side procedure documented in `design-composer.md`.
- **Steps:**
  1. Arrange: two synthetic `synthesis.md` files — fixture A has an (a) row whose justification cites a concrete file path + positive evidence; fixture B has an (a) row whose justification is bare ("skill X covers it").
  2. Act: a human reviewer (or a reviewer running design-composer's substance heuristic per ADR-0065) evaluates each row.
  3. Assert: fixture A passes (justification answers W/H/A questions in substance); fixture B is flagged as needing revision.
- **Expected outcome:** Substance review distinguishes cell-stuffing from genuine answer-shaped justification.
- **Negative-path companion:** AT-013 (structural mandate path).
- **Data dependencies:** Two synthesis fixtures.
- **Determinism notes:** Substance is judgment-based; per ADR-0065 kill-criteria, inter-reviewer disagreement >30% sustained across N≥3 runs triggers extension of structural mandate. The test is reviewer-administered with documented rubric.

---

### AT-015 — FR-7 (b) decision row with complete W/H/A trifecta passes

- **Maps to AC:** AC-FR-7-c
- **Test type:** Unit (structural check on (b)-row format)
- **Layer:** Claude Code
- **Preconditions:** Phase 6 T6.1 (template) landed.
- **Steps:**
  1. Arrange: synthetic (b)-decision row whose justification contains:
     - Why: a one-sentence purpose statement.
     - How: at least one named downstream agent or stage that loads it.
     - Anti-patterns: at least one named anti-pattern.
  2. Act: invoke trifecta-completeness checker (regex over heading presence + non-empty body).
  3. Assert: validator returns OK; all three sub-fields populated.
- **Expected outcome:** Row passes structural mandate.
- **Negative-path companion:** AT-013.
- **Data dependencies:** Complete (b)-row fixture.
- **Determinism notes:** Deterministic.

---

### AT-016 — FR-8 Principle 9 leading sentence is in active framing

- **Maps to AC:** AC-FR-8-a
- **Test type:** Structural (grep / line-content assertion)
- **Layer:** Claude Code
- **Preconditions:** Phase 2 T2.1 landed.
- **Steps:**
  1. Arrange: read `.claude/skills/KB-cc-design/references/principles.md`.
  2. Act: grep for the new active-framing leading sentence (e.g., "record the consideration"); separately grep for the defensive-framing sentence ("don't change … lightly").
  3. Assert: active sentence present; defensive sentence (verbatim or paraphrase) absent in Principle 9's leading position.
- **Expected outcome:** Principle 9 leads with the active framing per cc-design §FR-8.
- **Negative-path companion:** N/A (replacement is in-place; pre-state cannot be tested post-landing).
- **Data dependencies:** Updated `principles.md` file.
- **Determinism notes:** Deterministic grep.

---

### AT-017 — FR-8 Principle 9 and FR-6 cell discipline cross-reference each other by name

- **Maps to AC:** AC-FR-8-b
- **Test type:** Structural (grep both directions)
- **Layer:** Claude Code
- **Preconditions:** Phase 2 T2.2 + Phase 5 T5.3 landed.
- **Steps:**
  1. Arrange: read `.claude/skills/KB-cc-design/references/principles.md` and `.claude/agents/design-claude-code.md`.
  2. Act: in `principles.md` Principle 9 section, grep for "matrix-cell discipline" or "FR-6 §Per-cell discipline"; in `design-claude-code.md` line ~56 region, grep for "Principle 9".
  3. Assert: both directions return matches; the cross-reference is bidirectional and citation-named (not implicit).
- **Expected outcome:** Mutual cross-reference exists; designers consulting either file are routed to the other.
- **Negative-path companion:** N/A.
- **Data dependencies:** Updated files in both target paths.
- **Determinism notes:** Deterministic grep.

---

### AT-018 — FR-9 parser enumerates `<!-- BLOCKS: <stage-slug>-completion -->` markers

- **Maps to AC:** AC-FR-9-a
- **Test type:** Unit (`parse_blocks_x_markers.py` smoke test)
- **Layer:** Claude Code
- **Preconditions:** Phase 3 T3.1 landed.
- **Steps:**
  1. Arrange: synthetic discovery output file containing two well-formed markers: `<!-- BLOCKS: design-completion -->` and `<!-- BLOCKS: plan-completion -->`.
  2. Act: invoke `parse_blocks_x_markers.py` against the fixture.
  3. Assert: returns two records; record[0] has `stage="design"`, record[1] has `stage="plan"`; both include `raw_line`, `file_path`, `line_no`.
- **Expected outcome:** Parser returns one record per marker; canonical grammar honored per ADR-0063.
- **Negative-path companion:** AT-019 (malformed marker case).
- **Data dependencies:** Synthetic discovery fixture.
- **Determinism notes:** Deterministic regex.

---

### AT-019 — FR-9 parser rejects malformed markers (regression against ADR-0063 grammar)

- **Maps to AC:** AC-FR-9-a
- **Test type:** Unit
- **Layer:** Claude Code
- **Preconditions:** Phase 3 T3.1 landed.
- **Steps:**
  1. Arrange: synthetic fixture containing three malformed candidates — `BLOCKS: design` (no HTML comment), `<!-- BLOCKS: -->` (no stage slug), `<!-- BLOCKS: design-COMPLETION -->` (case violation if grammar pins lowercase).
  2. Act: invoke parser.
  3. Assert: zero records returned for the three malformed lines; parser does not raise an exception (it filters and continues).
- **Expected outcome:** Strict grammar; malformed candidates silently skipped.
- **Negative-path companion:** AT-018.
- **Data dependencies:** Malformed marker fixture.
- **Determinism notes:** Deterministic.

---

### AT-020 — FR-9 orchestrator emits BLOCKER and halts at stage-transition when unresolved marker present

- **Maps to AC:** AC-FR-9-b
- **Test type:** Integration
- **Layer:** Claude Code
- **Preconditions:** Phase 3 T3.1 + T3.4 landed; Phase 1 bridge content landed.
- **Steps:**
  1. Arrange: synthetic feature run state where discovery output contains one `<!-- BLOCKS: design-completion -->` marker that has not been transitioned in state-transitions.log.
  2. Act: simulate orchestrator advance-to-design-completion attempt.
  3. Assert: orchestrator refuses to mark stage complete; emits one BLOCKER finding via `audit-issues.json` carrying `rule: blocks-x-marker-unresolved`, `target` naming the marker line + file, `divergence` naming the unresolved stage, `next_action: "transition marker to RESOLVED / DEFERRED_WITH_OI / FALSE_POSITIVE in state-transitions log"`.
- **Expected outcome:** Stage-transition halted; finding emitted in bridge severity vocabulary.
- **Negative-path companion:** AT-021 (closure path).
- **Data dependencies:** Synthetic run-state + unresolved marker.
- **Determinism notes:** Deterministic.

---

### AT-021 — FR-9 transition rationale recorded in state-transitions log under one of the three closure values

- **Maps to AC:** AC-FR-9-c
- **Test type:** Integration
- **Layer:** Claude Code
- **Preconditions:** Phase 3 T3.1 + T3.2 + T3.4 landed.
- **Steps:**
  1. Arrange: synthetic run-state with a marker that the orchestrator transitions to `BLOCKS_X_RESOLVED`. Repeat the test parameterized over `BLOCKS_X_DEFERRED_WITH_OI` and `BLOCKS_X_FALSE_POSITIVE`.
  2. Act: invoke `log_state_transition.py` with each `transition_name` value.
  3. Assert: each entry written to state-transitions.log carries the named `transition_name`; the orchestrator subsequently advances past the named stage; grep on the log returns the entry.
- **Expected outcome:** All three closure values logged successfully; advance permitted post-closure.
- **Negative-path companion:** AT-020.
- **Data dependencies:** Synthetic run-state.
- **Determinism notes:** Deterministic; verifies ADR-0044 v1 free-string compatibility.

---

### AT-022 — FR-10 SA-14 emits BLOCKER when matrix is missing on a triggered feature

- **Maps to AC:** AC-FR-10-a
- **Test type:** Integration
- **Layer:** Claude Code
- **Preconditions:** Phase 7 T7.1 + T7.2 landed; Phase 5 T5.2 (predicate, for trigger evidence) landed.
- **Steps:**
  1. Arrange: synthetic feature working directory at `tests/fixtures/at-022-sa-14-missing-matrix/` whose diff fixture exhibits trigger-condition-1 evidence but the directory contains no `agent-roster-impact-matrix.md`.
  2. Act: invoke `audit_feature_touch_coverage.py` against the directory.
  3. Assert: exactly one BLOCKER finding; `rule: feature-touch-coverage`; `target` naming the working-directory path; `divergence: "agent-roster-impact-matrix.md missing"`; `next_action` naming the matrix authoring procedure.
- **Expected outcome:** SA-14 fires; backstop catches missed-at-design-time matrix.
- **Negative-path companion:** AT-026 (no-trigger case).
- **Data dependencies:** Synthetic working-directory fixture.
- **Determinism notes:** Deterministic.

---

### AT-023 — FR-10 SA-14 rule entry is enumerated in the auditing-subagents catalog

- **Maps to AC:** AC-FR-10-a
- **Test type:** Structural (grep)
- **Layer:** Claude Code
- **Preconditions:** Phase 7 T7.2 landed.
- **Steps:**
  1. Arrange: read `.claude/skills/auditing-subagents/SKILL.md`.
  2. Act: grep for `SA-14` and "feature-touch-coverage".
  3. Assert: both found; SKILL.md description's SA-NN count is consistent (I-AA-005 closed); the referenced discipline file under `auditing-subagents/references/` exists.
- **Expected outcome:** Catalog entry exists; description count matches the latest rule number.
- **Negative-path companion:** N/A.
- **Data dependencies:** Updated SKILL.md + references file.
- **Determinism notes:** Deterministic grep.

---

### AT-024 — FR-10 row-count parity check fires BLOCKER on mismatch

- **Maps to AC:** AC-FR-10-b
- **Test type:** Unit (audit script)
- **Layer:** Claude Code
- **Preconditions:** Phase 7 T7.1 landed.
- **Steps:**
  1. Arrange: synthetic feature directory with matrix present, but row count = 35 while audit-time `.claude/agents/*.md` count = 37.
  2. Act: invoke audit script.
  3. Assert: one BLOCKER emitted; `rule: feature-touch-coverage`; `divergence` reports the two integers; `next_action` names "add rows for the 2 missing agents."
- **Expected outcome:** Row-count parity check fires.
- **Negative-path companion:** AT-025 (matched case).
- **Data dependencies:** Synthetic mismatched-matrix fixture.
- **Determinism notes:** Deterministic.

---

### AT-025 — FR-10 row-count parity check passes on match

- **Maps to AC:** AC-FR-10-b
- **Test type:** Unit
- **Layer:** Claude Code
- **Preconditions:** Phase 7 T7.1 landed.
- **Steps:**
  1. Arrange: synthetic feature directory with matrix present + row count = `ls .claude/agents/*.md | wc -l`.
  2. Act: invoke audit script.
  3. Assert: no findings; exit 0.
- **Expected outcome:** Audit passes silently.
- **Negative-path companion:** AT-024.
- **Data dependencies:** Synthetic matched-matrix fixture.
- **Determinism notes:** Deterministic.

---

### AT-026 — FR-10 SA-14 is no-op when working directory shows no agent-surface trigger

- **Maps to AC:** AC-FR-10-c
- **Test type:** Integration (negative-path)
- **Layer:** Claude Code
- **Preconditions:** Phase 7 T7.1 + Phase 5 T5.2 landed.
- **Steps:**
  1. Arrange: synthetic feature directory whose diff fixture exhibits no trigger-condition evidence (no `.claude/agents/*.md` diff, no `.mcp.json` tool-surface diff, no new skill, no new domain concept naming an agent).
  2. Act: invoke audit script.
  3. Assert: no findings emitted; matrix is not required for this feature; audit exits 0.
- **Expected outcome:** No false positives — SA-14 is silent when feature didn't touch the agent surface.
- **Negative-path companion:** AT-022 (positive trigger).
- **Data dependencies:** No-trigger fixture.
- **Determinism notes:** Deterministic; this is the critical false-positive guard for SA-14.

---

### AT-027 — NFR-1 auditor design-realization pass completes within 5000 ms on 20-prescription input

- **Maps to AC:** AC-NFR-1-a
- **Test type:** Performance
- **Layer:** Claude Code
- **Preconditions:** Phase 4 T4.3 landed.
- **Steps:**
  1. Arrange: synthetic feature fixture containing exactly 20 ADRs, each with a `.prescriptions.yaml` companion; mix of matching and diverging implementation files.
  2. Act: invoke Lens 4 design-realization audit phase; record wall-clock from phase-start to phase-end via inline timing (per OP-Plan-2 — inline timing in the auditor's logging).
  3. Assert: elapsed wall-clock < 5000 ms.
- **Expected outcome:** Pass completes within budget.
- **Negative-path companion:** N/A.
- **Data dependencies:** 20-ADR synthetic fixture.
- **Determinism notes:** Performance test — repeat 3 times and use median to dampen jitter; record raw timings in test output. Flake risk: shared CI runner contention. Mitigation: tag test as "performance" and pin to a controlled execution lane.

---

### AT-028 — NFR-7 matrix authoring at 100-agent inventory remains under 30 minutes wall-clock

- **Maps to AC:** AC-NFR-7-a
- **Test type:** Manual-observation supplement (operational-use measurement)
- **Layer:** Claude Code
- **Preconditions:** Phase 8 T8.1 landed (37-agent measurement); operational deployment supplies the 100-agent observation later.
- **Steps:**
  1. Arrange: for this run's own Phase 8 dogfood (37 agents), record matrix file's first-write to last-write timestamps in the run state log.
  2. Act: compute elapsed time; linearly extrapolate to 100 agents (37 → 100 ≈ 2.7× scaling).
  3. Assert (for this run): extrapolated 100-agent time < 30 minutes; (proxy assertion until a 100-agent feature actually exercises the contract). Record measured 37-agent time as evidence.
- **Expected outcome:** Linear-extrapolation proxy passes the 30-min budget at 100 agents; cell-granularity remains the dial-to-relax per Risk row 1 kill-criteria if exceeded.
- **Negative-path companion:** N/A.
- **Data dependencies:** This run's matrix-authoring timestamps; future feature run's actual 100-agent measurement.
- **Determinism notes:** Wall-clock measurement; depends on operator pace, not machine performance. Documented as a non-deterministic operational observation.

---

### AT-029 — NFR-8 FR-1 BLOCKER finding carries `rule` / `target` / `divergence` / `next_action`

- **Maps to AC:** AC-NFR-8-a
- **Test type:** Unit (assertion on finding-shape JSON)
- **Layer:** Claude Code
- **Preconditions:** Phase 1 T1.2 (four-field shape documented) + Phase 4 T4.3 landed.
- **Steps:**
  1. Arrange: invoke AT-001's divergence fixture.
  2. Act: capture the emitted finding JSON.
  3. Assert: top-level keys include `rule` (non-empty), `target` (non-empty), `divergence` (non-empty), `next_action` (non-empty); no placeholder strings (`TODO`, `TBD`, empty string).
- **Expected outcome:** Four-field shape honored.
- **Negative-path companion:** N/A.
- **Data dependencies:** AT-001 fixture.
- **Determinism notes:** Deterministic.

---

### AT-030 — NFR-8 FR-9 BLOCKER finding carries the four-field shape

- **Maps to AC:** AC-NFR-8-a
- **Test type:** Unit
- **Layer:** Claude Code
- **Preconditions:** Phase 1 T1.2 + Phase 3 T3.4 landed.
- **Steps:**
  1. Arrange: AT-020 unresolved-marker fixture.
  2. Act: capture emitted finding.
  3. Assert: four fields populated; no placeholders.
- **Expected outcome:** Same as AT-029, scoped to FR-9 emitter.
- **Negative-path companion:** N/A.
- **Data dependencies:** AT-020 fixture.
- **Determinism notes:** Deterministic.

---

### AT-031 — NFR-8 FR-10 BLOCKER finding carries the four-field shape

- **Maps to AC:** AC-NFR-8-a
- **Test type:** Unit
- **Layer:** Claude Code
- **Preconditions:** Phase 1 T1.2 + Phase 7 T7.1 landed.
- **Steps:**
  1. Arrange: AT-022 missing-matrix fixture.
  2. Act: capture emitted finding.
  3. Assert: four fields populated; no placeholders.
- **Expected outcome:** Same as AT-029, scoped to FR-10 emitter.
- **Negative-path companion:** N/A.
- **Data dependencies:** AT-022 fixture.
- **Determinism notes:** Deterministic.

---

### AT-032 — NFR-8 FR-6 design-cc gate-blocker carries the four-field shape

- **Maps to AC:** AC-NFR-8-a
- **Test type:** Unit
- **Layer:** Claude Code
- **Preconditions:** Phase 5 T5.3 + T5.4 landed.
- **Steps:**
  1. Arrange: AT-010 row-count divergence fixture.
  2. Act: capture emitted finding.
  3. Assert: four fields populated.
- **Expected outcome:** Same shape across all four FR emitters.
- **Negative-path companion:** N/A.
- **Data dependencies:** AT-010 fixture.
- **Determinism notes:** Deterministic.

---

### AT-033 — NFR-9 matrix-template affordance reachable from `design-claude-code` `skills:` frontmatter

- **Maps to AC:** AC-NFR-9-a
- **Test type:** Structural (grep predicate)
- **Layer:** Claude Code
- **Preconditions:** Phase 5 T5.1 landed.
- **Steps:**
  1. Arrange: read `.claude/agents/design-claude-code.md` frontmatter `skills:` array.
  2. Act: for each skill path, read its `SKILL.md` (and referenced files) and grep for `agent-roster-impact-matrix-template.md`.
  3. Assert: at least one skill path leads (directly or via reference) to a file mentioning the template; the template file itself exists at `.claude/skills/KB-documentation-criteria/references/templates/agent-roster-impact-matrix-template.md`.
- **Expected outcome:** Affordance is grep-reachable from the consuming agent.
- **Negative-path companion:** N/A.
- **Data dependencies:** Agent frontmatter + KB-documentation-criteria SKILL.md.
- **Determinism notes:** Deterministic grep chain.

---

### AT-034 — NFR-9 Skill-Coverage-Decisions affordance reachable from `synth-synthesizer` `skills:` frontmatter

- **Maps to AC:** AC-NFR-9-a
- **Test type:** Structural (grep predicate)
- **Layer:** Claude Code
- **Preconditions:** Phase 6 T6.1 landed.
- **Steps:**
  1. Arrange: read `.claude/agents/synth-synthesizer.md` frontmatter `skills:` array.
  2. Act: for each skill, grep for `skill-coverage-decisions-section-template.md` in its SKILL.md / referenced files.
  3. Assert: at least one skill leads to a file mentioning the template; the template file exists at `.claude/skills/KB-documentation-criteria/references/templates/skill-coverage-decisions-section-template.md`.
- **Expected outcome:** Affordance is grep-reachable from synthesizer.
- **Negative-path companion:** N/A.
- **Data dependencies:** synth-synthesizer frontmatter + KB-documentation-criteria SKILL.md.
- **Determinism notes:** Deterministic.

---

### AT-035 — Eat-own-dogfood: this run's `agent-roster-impact-matrix.md` passes SA-14

- **Maps to AC:** AC-FR-10-a + AC-FR-10-b (dogfood evidence)
- **Test type:** Integration (self-application)
- **Layer:** Claude Code
- **Preconditions:** Phase 8 T8.1 landed; Phase 7 T7.1 landed; this run is the input feature.
- **Steps:**
  1. Arrange: this run's actual working directory at `working/feature/pipeline-design-time-discipline-r1/`.
  2. Act: invoke `audit_feature_touch_coverage.py` against the directory.
  3. Assert: exit 0; no `audit-issues.json` BLOCKER entries; stdout names the directory + matrix file + row count = 37 (or whatever T0.2 baseline pinned).
- **Expected outcome:** Self-applied contract passes; dogfood validation event recorded for I-AA-007 closure.
- **Negative-path companion:** N/A (in-run validation event by design).
- **Data dependencies:** This run's actual deliverable.
- **Determinism notes:** Deterministic against the run's own state at packaging time.

---

### AT-036 — Eat-own-dogfood: this run's matrix has 37 rows × 5 cells × non-empty evidence

- **Maps to AC:** AC-FR-6-b (dogfood structural-discipline evidence)
- **Test type:** Structural (file-content grep + count)
- **Layer:** Claude Code
- **Preconditions:** Phase 8 T8.1 landed.
- **Steps:**
  1. Arrange: read `working/feature/pipeline-design-time-discipline-r1/agent-roster-impact-matrix.md`.
  2. Act: count rows in the table body; for each row, parse the five dimension cells; for each cell, assert `value — evidence` shape with non-empty evidence.
  3. Assert: row count = 37; every one of the 185 cells satisfies the regex `.+ — .+` with non-empty right-hand side; no cell is bare `no change`.
- **Expected outcome:** Dogfood matrix passes the FR-6-b/d discipline.
- **Negative-path companion:** N/A.
- **Data dependencies:** This run's matrix.
- **Determinism notes:** Deterministic file parse.

---

### AT-037 — Eat-own-dogfood: this run's `synthesis.md` Skill-Coverage Decisions section has 6 rows

- **Maps to AC:** AC-FR-7-a (dogfood evidence)
- **Test type:** Structural (file-content)
- **Layer:** Claude Code
- **Preconditions:** Phase 8 T8.2 landed (verification-only); cycle-1 back-fill (I-AA-004) in synthesis.md v1.0.1+ already present.
- **Steps:**
  1. Arrange: read `working/feature/pipeline-design-time-discipline-r1/synthesis.md`.
  2. Act: locate `## Skill-Coverage Decisions` section; count rows; for each row, identify decision type (a/b/c).
  3. Assert: exactly six rows; all six are type (a) "existing skill"; each row names a concrete skill path and one-sentence positive-evidence justification; the six concepts named match Blueprint §Eat-own-dogfood Deliverables (design-realization audit / agent-roster matrix / skill-coverage decision / Principle 9 active reframing / Blocks-X marker grammar / matrix-missing audit rule).
- **Expected outcome:** Dogfood Skill-Coverage section present and substance-passing.
- **Negative-path companion:** N/A.
- **Data dependencies:** This run's synthesis.md.
- **Determinism notes:** Deterministic.

---

### AT-038 — Eat-own-dogfood: design-composer substance review against this run's Skill-Coverage section returns no blocker

- **Maps to AC:** AC-FR-7-b (dogfood evidence)
- **Test type:** Manual review checklist (per ADR-0065 substance-heuristic posture)
- **Layer:** Claude Code
- **Preconditions:** Phase 6 T6.3 + Phase 8 T8.2 landed.
- **Steps:**
  1. Arrange: this run's `synthesis.md` Skill-Coverage Decisions section.
  2. Act: human reviewer (or design-composer running the documented substance heuristic) evaluates each of the six (a) rows against the rubric "does the justification actually answer the W/H/A question, not merely populate the cell?"
  3. Assert: all six rows pass substance review; no row triggers a "needs revision" verdict.
- **Expected outcome:** Dogfood passes the substance heuristic (a) / (c) reviewer path.
- **Negative-path companion:** N/A.
- **Data dependencies:** This run's synthesis.md.
- **Determinism notes:** Substance is judgment-based per ADR-0065 D-8 framing; documented in the test as a reviewer-administered check, not a machine assertion.

---

## Test infrastructure required

| Infrastructure element | Status in codebase | Action required |
|---|---|---|
| Python test framework (smoke-test pattern) | Present — `auditing-shared/scripts/smoke_test_auditing_shared.py` is the existing pattern | Adopt the same pattern for new scripts: `parse_blocks_x_markers.py`, `check_feature_touch_predicate.py`, `audit_feature_touch_coverage.py`, `validate_adr_prescriptions.py` each get a sibling `smoke_test_*.py`. |
| Synthetic feature-run fixtures (working-directory shape) | Partial — `Issues/per-agent-design-evaluation-gap/evidence/agent-roster-impact-matrix.md` is the exemplar; no formal fixture-runner | Create `tests/fixtures/<at-NNN>-<short-name>/` per integration test. Each fixture is a minimal `working/feature/<slug>/` skeleton + synthetic ADR set + synthetic diff log. |
| ADR + `.prescriptions.yaml` companion fixtures | None | Author 2-3 reusable companion-file fixtures (matched / diverging / malformed) under `tests/fixtures/adr-prescriptions/`. |
| Synthesis-doc fixtures with Skill-Coverage Decisions section | None | Author 3 fixtures: (a) complete W/H/A trifecta (b)-row; (b) incomplete (b)-row (missing one heading); (c) substance-passing (a)-row; (d) substance-failing (a)-row. Under `tests/fixtures/skill-coverage/`. |
| Wall-clock timing harness | Partial (inline `time.perf_counter()` in existing scripts is convention) | Per OP-Plan-2 disposition: inline timing in `review-architecture-auditor`'s own logging; test consumes the logged timestamps. |
| State-transitions log fixture | Present — `auditing-shared/scripts/log_state_transition.py` | Reuse for AT-021 closure-value parameterization. |
| Frontmatter / `skills:`-array parsing | Present — `auditing-subagents/scripts/validate_subagent_frontmatter.py` pattern | Reuse parsing logic for AT-033, AT-034 NFR-9 grep-predicate chain. |

## CI execution plan

Per `KB-review-disciplines` and standard project convention:

- **Per-PR (fast):** AT-002, AT-004, AT-005, AT-006, AT-009, AT-011, AT-015, AT-016, AT-017, AT-018, AT-019, AT-021 (parameterized), AT-023, AT-024, AT-025, AT-026, AT-029, AT-030, AT-031, AT-032, AT-033, AT-034. (~22 unit + structural tests — each <1 s.)
- **Pre-merge (medium):** AT-001, AT-003, AT-007, AT-008, AT-010, AT-012, AT-013, AT-020, AT-022. (Integration tests with fixture-loading; <30 s each.)
- **Nightly / scheduled:** AT-027 (performance, 5000 ms budget — repeat-3 with median). AT-014, AT-038 (manual review checklist tasks queued for human review).
- **Pre-release / packaging-time:** AT-028 (operational-time-budget proxy), AT-035, AT-036, AT-037, AT-038 (eat-own-dogfood self-application against this run's working directory at Phase 9 packaging).

## Determinism and isolation commitments

Per `KB-general-coding-principles`:

- **Deterministic assertions.** All 36 of the 38 tests use deterministic file/regex/JSON checks. Two exceptions: AT-027 (performance — wall-clock; repeat-3 median mitigation) and AT-028 (NFR-7 operational-time proxy; explicitly named as non-deterministic operator-pace observation).
- **No shared state across tests.** Each fixture lives in its own `tests/fixtures/<at-NNN>-*/` directory. Tests neither read nor write outside their fixture root.
- **No real credentials in fixtures.** All synthetic ADRs, agents, and skills carry placeholder names (`example-*`, `at-NNN-*`); no real keys, tokens, internal URLs, or PII.
- **No real production paths.** Fixtures route only to `tests/fixtures/` and the run's own `working/feature/pipeline-design-time-discipline-r1/` (which is the dogfood subject). No fixture writes to `adrs/`, `.claude/agents/`, or `.claude/skills/`.
- **AAA structure.** Every test spec is Arrange-Act-Assert; preconditions = arrange context; steps 1-3 map directly.

## Open coverage gaps

Three coverage notes for the cross-artifact auditor to verify on review:

1. **AT-014 and AT-038 (FR-7 substance heuristic, AC-FR-7-b dogfood)** — substance is reviewer-judgment per ADR-0065 / D-8 framing. The tests are documented as reviewer-administered with explicit rubric ("does the justification actually answer the W/H/A question?"). ADR-0065 kill-criteria handle the drift case (>30% inter-reviewer disagreement sustained across N≥3 runs). This is **deliberate**, not a coverage gap — the substance heuristic is named in the Blueprint as not fully machine-testable.

2. **AT-028 (NFR-7 30-min-at-100-agents budget)** — proxied by this run's 37-agent measurement + linear extrapolation. A 100-agent operational measurement is the natural future validation; the test is documented as a wall-clock observation with documented non-determinism. Per OP-Plan-3 disposition, the run-state-log emission path for matrix authoring-time is recorded as "T8.1's L2 evidence is the proxy until then."

3. **NFR-8 four-field shape on FR-6 trigger-override events.** The Blueprint reserves `TRIGGER_OVERRIDE` as a state-transitions log entry, but trigger-override is not classified as a BLOCKER-emitting event in PRD NFR-8's wording. AT-032 covers the FR-6 cell-discipline BLOCKER path; trigger-override is observability-only and not in NFR-8's scope. No gap, but flagged here for auditor confirmation.

No PRD AC is uncovered. The 22 ACs map to 38 acceptance tests with no orphan tests (every AT maps to at least one AC) and no orphan ACs (every AC is named by at least one AT).

## References

- PRD: `working/feature/pipeline-design-time-discipline-r1/prd-v1.md` (FR/NFR ACs)
- Blueprint: `working/feature/pipeline-design-time-discipline-r1/blueprint-v1.md` v1.0.1 (§Verification strategy + §Severity bridge content + §Change impact map)
- Plan: `working/feature/pipeline-design-time-discipline-r1/plan-v1.md` v1.0.0 (§Acceptance Test Cross-Reference table)
- EARS discipline: `.claude/skills/KB-documentation-criteria/references/disciplines/ears-acceptance-criteria.md`
- Test convention exemplar: `.claude/skills/auditing-shared/scripts/smoke_test_auditing_shared.py`
- ADR-0059 (companion `.prescriptions.yaml`), ADR-0061 (severity bridge host), ADR-0063 (Blocks-X grammar), ADR-0064 (matrix contract), ADR-0065 (skill-coverage discipline)

---

*End of Acceptance Tests v1.0.0 for `pipeline-design-time-discipline-r1`. Next stage: `review-cross-artifact-auditor` runs diff-mode consistency check across Blueprint ↔ Plan ↔ Tests ↔ PVs after `test-phase-validator-author` completes in parallel.*
