---
id: PValidators-pipeline-design-time-discipline-r1
version: 1.0.0
status: draft
doc_type: phase-validators
feature_slug: pipeline-design-time-discipline-r1
derived_from:
  - working/feature/pipeline-design-time-discipline-r1/plan-v1.md
  - working/feature/pipeline-design-time-discipline-r1/acceptance-tests.md
  - working/feature/pipeline-design-time-discipline-r1/blueprint-v1.md
  - working/feature/pipeline-design-time-discipline-r1/prd-v1.md
predecessor: null
parent_run: pipeline-cross-artifact-discipline-r1
related_run: pipeline-gate-validator-hardening-r1
total_validators: 10
generated: 2026-05-26T19:45:00Z
generated_by: test-phase-validator-author
---

# Phase Validators: Pipeline Design-Time Discipline (R2a)

## Purpose

One validator entry per Plan phase. Each validator gates the exit from its phase and the entry into the next phase. Validator severity uses the PV vocabulary (`blocking` / `warning` / `informational`) from `KB-review-disciplines/references/severity-taxonomy.md` (populated at Phase 1 / T1.1); criteria that consume emitter-side findings inherit the auditor `BLOCKER` / `MAJOR` / `MINOR` / `NIT` / `INFO` vocabulary and map through the bridge.

## Severity vocabulary used

- **PV vocabulary (this document):** `blocking` (phase cannot exit), `warning` (deferral requires explicit user decision), `informational` (recorded; non-blocking).
- **Auditor vocabulary (inherited from emitter findings):** `BLOCKER` / `MAJOR` / `MINOR` / `NIT` / `INFO` per ADR-0061. Any `BLOCKER` emitted by an audit script / auditor procedure invoked by a criterion maps to PV `blocking`.
- **Reviewer vocabulary (inherited from doc-review findings):** `critical` → PV `blocking`; `important` → PV `warning`; `recommended` → PV `informational`.

Bridge resolution: `KB-review-disciplines/references/severity-taxonomy.md` (the artifact authored at Phase 1 T1.1 / T1.2 — this run is the bridge's first populator and first consumer).

## Validator dependency graph

```
PV-0 ─┬─► PV-1 ─┬─► PV-3 ─┐
      │         ├─► PV-4 ─┤
      │         └─► PV-7 ─┤
      │                   ├─► PV-8 ─► PV-9
      ├─► PV-2 ─► PV-5 ───┤
      │                   │
      └─► PV-6 ───────────┘
```

- **PV-0** is the universal precondition; every downstream validator presumes Phase 0 baselines.
- **PV-1** gates PV-3 / PV-4 / PV-7 (severity bridge content needed by Blocks-X / Lens 4 / SA-14 emitters).
- **PV-2** gates PV-5 (Principle 9 active wording cited by design-cc procedure extension).
- **PV-5** + **PV-6** both gate PV-8 (eat-own-dogfood requires both contracts in place).
- **PV-8** gates PV-9 (rollout requires successful self-application).
- Parallelizable within Phase 1 ratification: PV-2, PV-3, PV-6 can run independently after PV-1.

Critical-path validators (whose failure most delays rollout): PV-1, PV-5, PV-8.

---

## PV-0 — Phase 0 Setup baselines confirmed

- **Phase reference:** Plan §Phase 0 — Setup (tasks T0.1, T0.2, T0.3).
- **Validator goal:** Inherited-ADR availability and agent/KB inventory baselines exist before any feature-delivery phase begins.
- **Acceptance tests in scope:** None — Phase 0 tasks have no PRD AC bindings. Their L1/L2/L3 checks are the validator evidence.
- **Severity vocabulary applied:** PV vocabulary.

### Pass criteria

- **PV-0.C1** — Three inherited ADRs present and `status: accepted`. Assertion: `adrs/ADR-0059-adr-prescriptions-companion-file.md`, `adrs/ADR-0061-severity-vocabulary-bridge-table.md`, `adrs/ADR-0063-blocks-x-marker-grammar.md` all parse as YAML frontmatter and the `status` field equals `accepted`. Source: T0.1 L2. Automation hook: shell `for f in adrs/ADR-005{9,1}-*.md adrs/ADR-0063-*.md; do grep -E '^status: accepted$' "$f"; done`. Severity: `blocking`.
- **PV-0.C2** — Agent inventory baseline pinned. Assertion: `working/feature/pipeline-design-time-discipline-r1/inventory-baseline.txt` exists; line count equals `ls .claude/agents/*.md | wc -l`; expected value 37 per codebase-analysis A-4. Source: T0.2 L1/L3. Automation hook: shell diff `wc -l < inventory-baseline.txt` vs `ls .claude/agents/*.md | wc -l`. Severity: `blocking`.
- **PV-0.C3** — Canonical script-host directories exist. Assertion: `test -d .claude/skills/auditing-shared/scripts` and `test -d .claude/skills/auditing-subagents/scripts`. Source: T0.3 L1. Automation hook: shell directory-existence check. Severity: `blocking`.

### Operational checks

Setup-phase: no observability, migrations, or feature-flag work applies (R2a is design-time documentation discipline only; no runtime affordance). Per OP-Plan-1, this validator is intentionally lightweight (file/inventory existence). Downstream validators presume PV-0 passed.

### Failure response

Plan does not provide a rollback path for Phase 0 (no edits are made). On failure: halt Phase 1 dispatch; report missing baselines to user; re-run T0.1 / T0.2 / T0.3 after the underlying gap is resolved (e.g., parent run's deliverable not yet landed → wait for it).

### Validator metadata

- **When run:** Once at Phase 0 close, before Phase 1 dispatch.
- **Expected duration:** <5 s (all checks are file-existence / line-count).
- **Prerequisites:** Parent run `pipeline-cross-artifact-discipline-r1` deliverable archive landed (provides the three inherited ADRs).

---

## PV-1 — Severity bridge foundation published

- **Phase reference:** Plan §Phase 1 — Severity bridge foundation (D-R2a-6) (tasks T1.1, T1.2).
- **Validator goal:** The severity-taxonomy bridge content is citable in its canonical location before any FR-1 / FR-9 / FR-10 emitter references it.
- **Acceptance tests in scope:** AT-002 (bridge cited by auditor severity emitter), AT-029, AT-030, AT-031, AT-032 (NFR-8 four-field shape consumers — all cite the bridge host).
- **Severity vocabulary applied:** PV vocabulary; reviewer vocabulary for any document-review issues on the bridge file itself.

### Pass criteria

- **PV-1.C1** — Bridge file exists with required structure. Assertion: `.claude/skills/KB-review-disciplines/references/severity-taxonomy.md` exists; markdown parses; contains a five-row × five-column table with rows `BLOCKER`, `MAJOR`, `MINOR`, `NIT`, `INFO` and columns including `auditor`, `reviewer`, `pv`, `non-monotonic-edges`, `iteration-delta-weight`. Source: T1.1 L1/L2. Automation hook: regex check + table-structure parser. Severity: `blocking`.
- **PV-1.C2** — Weight Preservation Note + Verdict-Compute weights table present. Assertion: grep for `Weight Preservation Note` and `iteration_delta_weight` returns hits; iteration-delta weights row read as `10 / 3 / 1 / 0 / 0`. Source: T1.1 L2. Automation hook: grep + numeric assertion. Severity: `blocking`.
- **PV-1.C3** — NFR-8 four-field finding shape documented inline. Assertion: grep for `NFR-8 four-field finding shape` heading; each of `rule`, `target`, `divergence`, `next_action` named with one-sentence semantics. Source: T1.2 L2. Automation hook: grep chain. Severity: `blocking`.
- **PV-1.C4** — Bridge file passes Gate 0 / Gate 1 document review. Assertion: `shared-document-reviewer` invocation against the file returns `approved` or `approved_with_conditions`; no `critical`-severity issues open. Source: KB-review-disciplines Gate 0/1 procedure. Automation hook: `shared-document-reviewer` subagent. Severity: `blocking` on `critical`; `warning` on `important`.

### Operational checks

- The bridge file is the canonical citation target for ADR-0061's host clause; verify the ADR-0061 `host_file` field (if present) or body text resolves to this exact path.
- Bridge content must be R2b-readable: file path is stable, no rename pending in deliverable archive packaging.

### Failure response

Per Plan §Cross-Phase Dependencies load-bearing dependency 1: consumers-first ordering would replay the placeholder-leakage failure mode FR-1 is designed to catch. On failure: halt Phases 3, 4, 7 dispatch; revise bridge content; re-validate.

### Validator metadata

- **When run:** Once at Phase 1 close, before Phases 3 / 4 / 7 dispatch.
- **Expected duration:** <10 s (grep + structural parse + document-review subagent).
- **Prerequisites:** PV-0 passed.

---

## PV-2 — Principle 9 active reframing landed with mutual cross-reference

- **Phase reference:** Plan §Phase 2 — FR-8 Principle 9 active reframing (tasks T2.1, T2.2).
- **Validator goal:** Principle 9's leading sentence reads in active framing; mutual cross-reference between Principle 9 and the FR-6 matrix-cell discipline is bidirectional.
- **Acceptance tests in scope:** AT-016 (active leading sentence), AT-017 (mutual cross-reference both directions).
- **Severity vocabulary applied:** PV vocabulary.

### Pass criteria

- **PV-2.C1** — Active framing leading sentence present at `.claude/skills/KB-cc-design/references/principles.md` (Principle 9). Assertion: grep for the active-framing sentence (containing "record the consideration" per cc-design §FR-8); defensive-framing sentence absent in Principle 9's leading position. Source: AT-016. Automation hook: grep + negative-grep. Severity: `blocking`.
- **PV-2.C2** — `.claude/agents/design-claude-code.md` references Principle 9 with updated wording at the cited region (~line 56). Assertion: grep on `Principle 9` in design-claude-code.md returns the citation; cited text matches new active wording. Source: T2.2 L1/L2. Automation hook: grep. Severity: `blocking`.
- **PV-2.C3** — Mutual cross-reference bidirectional. Assertion: `principles.md` Principle 9 section grep returns `matrix-cell discipline` or `FR-6 §Per-cell discipline`; `design-claude-code.md` grep returns `Principle 9`; both directions resolve. Source: AT-017. Automation hook: dual grep chain. Severity: `blocking`.

### Operational checks

- No stale defensive-framing wording remains in either file's leading sentence (negative-grep assertion in PV-2.C1).

### Failure response

Per Plan §Cross-Phase Dependencies dependency 3: Phase 5 T5.3 (design-cc procedure extension) cites the active wording verbatim. On failure: halt Phase 5 dispatch; revise T2.1 / T2.2; re-validate.

### Validator metadata

- **When run:** Once at Phase 2 close, before Phase 5 dispatch.
- **Expected duration:** <5 s (pure grep).
- **Prerequisites:** PV-0 passed. (PV-1 not required — Phase 2 is independent of bridge content.)

---

## PV-3 — FR-9 Blocks-X marker mechanism end-to-end

- **Phase reference:** Plan §Phase 3 — FR-9 Blocks-X marker mechanism (tasks T3.1, T3.2, T3.3, T3.4).
- **Validator goal:** Blocks-X markers function as stage-transition gates end-to-end: parser enumerates per ADR-0063 grammar; orchestrator halts on unresolved; three closure values transition cleanly.
- **Acceptance tests in scope:** AT-018, AT-019 (parser positive/negative), AT-020 (orchestrator BLOCKER emission), AT-021 (three closure values), AT-030 (NFR-8 four-field shape on FR-9 emitter).
- **Severity vocabulary applied:** PV vocabulary; auditor vocabulary on emitter findings (BLOCKER from orchestrator).

### Pass criteria

- **PV-3.C1** — `parse_blocks_x_markers.py` exists and smoke-tests pass. Assertion: AT-018 (positive enumeration) and AT-019 (malformed-marker rejection) both pass. Source: AT-018, AT-019. Automation hook: `python .claude/skills/auditing-shared/scripts/smoke_test_parse_blocks_x_markers.py`. Severity: `blocking`.
- **PV-3.C2** — Four new `transition_name` values documented in template. Assertion: grep `state-transitions-log-entry-template.md` for `BLOCKS_X_RESOLVED`, `BLOCKS_X_DEFERRED_WITH_OI`, `BLOCKS_X_FALSE_POSITIVE`, `TRIGGER_OVERRIDE`. Source: T3.2 L1, AT-021. Automation hook: grep. Severity: `blocking`.
- **PV-3.C3** — Discovery-researcher emission procedure present. Assertion: grep `.claude/agents/discovery-codebase-researcher.md` for `Blocks` marker emission reference. Source: T3.3 L2. Automation hook: grep. Severity: `blocking`.
- **PV-3.C4** — Orchestrator stage-transition gate logic present. Assertion: grep `.claude/agents/execute-orchestrator.md` for `parse_blocks_x_markers.py` invocation in stage-transition procedure block. Source: T3.4 L2. Automation hook: grep. Severity: `blocking`.
- **PV-3.C5** — End-to-end gate behavior validated. Assertion: AT-020 (orchestrator emits BLOCKER on unresolved marker) and AT-021 (all three closure values log + advance) pass. Source: AT-020, AT-021. Automation hook: integration tests under `tests/fixtures/`. Severity: `blocking`.
- **PV-3.C6** — NFR-8 four-field shape on FR-9 emitter. Assertion: AT-030 passes; finding JSON has `rule`, `target`, `divergence`, `next_action` non-empty. Source: AT-030. Automation hook: JSON-shape assertion. Severity: `blocking`.

### Operational checks

- No schema change required to `log_state_transition.py` (ADR-0044 v1 free-string compatibility preserved); confirm script file unmodified vs baseline diff at Phase 3 close.

### Failure response

Plan's rollback path for Phase 3: marker procedure additions are pure-additive procedure-text in agent prompts; revert by reverse-applying the patches. Parser script is new-file and can be removed without dependency conflict. On failure: halt Phases 4 / 8 / 9 dispatch where they depend on FR-9 mechanics; address findings.

### Validator metadata

- **When run:** Once at Phase 3 close.
- **Expected duration:** <2 min (unit + integration tests).
- **Prerequisites:** PV-0, PV-1 passed.

---

## PV-4 — FR-1 design-realization audit dimension operational

- **Phase reference:** Plan §Phase 4 — FR-1 design-realization audit dimension (tasks T4.1, T4.2, T4.3).
- **Validator goal:** `review-architecture-auditor` Lens 4 emits BLOCKER on ADR-prescription / eventual-file divergence within the 5000 ms budget; companion-file validator script in place.
- **Acceptance tests in scope:** AT-001 (BLOCKER on divergence), AT-002 (severity vocab citation), AT-003 (no-companion no-op), AT-004 (KB document names the mechanism), AT-027 (NFR-1 performance 5000 ms), AT-029 (NFR-8 four-field shape on FR-1 emitter).
- **Severity vocabulary applied:** PV vocabulary; auditor vocabulary on Lens 4 findings.

### Pass criteria

- **PV-4.C1** — `validate_adr_prescriptions.py` exists and smoke-tests pass. Assertion: T4.1 L2 fixture-based smoke test returns OK on well-formed companion + specific error on malformed. Source: T4.1 L2. Automation hook: `smoke_test_validate_adr_prescriptions.py`. Severity: `blocking`.
- **PV-4.C2** — Lens 4 documented in KB-review-disciplines. Assertion: AT-004 passes (grep for `Lens 4` + `ADR-0059` + `.prescriptions.yaml` in `architecture-audit.md`). Source: AT-004. Automation hook: grep chain. Severity: `blocking`.
- **PV-4.C3** — Auditor agent procedure extended. Assertion: grep `review-architecture-auditor.md` for `Lens 4` / `design-realization` references. Source: T4.3 L2. Automation hook: grep. Severity: `blocking`.
- **PV-4.C4** — End-to-end Lens 4 emits BLOCKER on synthetic divergence. Assertion: AT-001 passes — finding emitted with `severity: BLOCKER`, four-field shape, bound to ADR id. Source: AT-001. Automation hook: integration test. Severity: `blocking`.
- **PV-4.C5** — Lens 4 no-op on zero-companion case. Assertion: AT-003 passes. Source: AT-003. Automation hook: integration test. Severity: `blocking`.
- **PV-4.C6** — NFR-1 5000 ms budget honored. Assertion: AT-027 passes — median of 3 runs against 20-prescription fixture under 5000 ms wall-clock. Source: AT-027. Automation hook: performance test on a controlled execution lane (per OP-Plan-2: inline timing in auditor's own logging). Severity: `warning` on first failure (jitter possible); `blocking` if median across 3 separate runs >5000 ms.
- **PV-4.C7** — NFR-8 four-field shape on FR-1 emitter. Assertion: AT-029 passes. Source: AT-029. Automation hook: JSON-shape assertion. Severity: `blocking`.

### Operational checks

- Auditor procedure phase is **inline** (per ADR-0045 no Agent/Task tool); confirm no `Agent` / `Task` invocation in the new phase block.
- Companion-file lint clears on synthetic well-formed and malformed `.prescriptions.yaml` test fixtures — manual confirmation that fixture set exists under `tests/fixtures/adr-prescriptions/`.

### Failure response

Plan rollback for Phase 4: Lens 4 procedure-text additions are revertible; `validate_adr_prescriptions.py` and KB Lens 4 section are pure-additive. On failure: halt Phase 9 (rollout) dispatch; revise; re-validate. Performance failure (PV-4.C6) is the most likely live-fire failure mode — first occurrence routes to `warning` with explicit deferral decision; sustained failure is `blocking`.

### Validator metadata

- **When run:** Once at Phase 4 close.
- **Expected duration:** ~30 s (unit + integration); ~15 s extra for AT-027 3-run median.
- **Prerequisites:** PV-0, PV-1 passed.

---

## PV-5 — FR-6 agent-roster matrix contract codified

- **Phase reference:** Plan §Phase 5 — FR-6 agent-roster matrix contract (tasks T5.1, T5.2, T5.3, T5.4).
- **Validator goal:** Matrix template authored, advisory predicate operational on all four trigger conditions, design-cc procedure + recipe Stage 7 gate enforce matrix presence on trigger-fired feature runs.
- **Acceptance tests in scope:** AT-005, AT-006 (deterministic triggers 1, 2), AT-007, AT-008 (advisory triggers 3, 4), AT-009 (matrix valid passes), AT-010 (row-count divergence blocks), AT-011 (bare `no change` rejected), AT-032 (NFR-8 four-field shape on FR-6 emitter), AT-033 (NFR-9 affordance grep-reachable from design-claude-code).
- **Severity vocabulary applied:** PV vocabulary; auditor vocabulary on SA-14 / design-cc gate findings.

### Pass criteria

- **PV-5.C1** — Matrix template exists. Assertion: `.claude/skills/KB-documentation-criteria/references/templates/agent-roster-impact-matrix-template.md` exists; five-column header present; worked example row present; "no bare no-change" rule documented. Source: T5.1 L1/L2. Automation hook: grep + structural parse. Severity: `blocking`.
- **PV-5.C2** — Advisory predicate exists and passes conditions 1 + 2 deterministic tests. Assertion: AT-005 + AT-006 pass — `triggered=True`, `mode=deterministic`. Source: AT-005, AT-006. Automation hook: `smoke_test_check_feature_touch_predicate.py`. Severity: `blocking`.
- **PV-5.C3** — Advisory predicate passes conditions 3 + 4 advisory tests. Assertion: AT-007 + AT-008 pass — `triggered=True`, `mode=advisory`. Source: AT-007, AT-008. Automation hook: same smoke test. Severity: `blocking`.
- **PV-5.C4** — design-claude-code Phase 2 procedure extended. Assertion: grep `design-claude-code.md` for `agent-roster-impact-matrix.md` and `Principle 9`. Source: T5.3 L2. Automation hook: grep. Severity: `blocking`.
- **PV-5.C5** — Recipe Stage 7 outputs table + gate updated. Assertion: grep `.claude/skills/recipe-feature-pipeline/SKILL.md` for matrix row + Stage 7 close-gate clause. Source: T5.4 L2. Automation hook: grep. Severity: `blocking`.
- **PV-5.C6** — Valid matrix passes audit. Assertion: AT-009 passes. Source: AT-009. Automation hook: unit test. Severity: `blocking`.
- **PV-5.C7** — Row-count divergence blocks composition. Assertion: AT-010 passes — BLOCKER emitted; recipe Stage 7 close refused. Source: AT-010. Automation hook: integration test. Severity: `blocking`.
- **PV-5.C8** — Bare `no change` rejected. Assertion: AT-011 passes. Source: AT-011. Automation hook: unit test. Severity: `blocking`.
- **PV-5.C9** — NFR-8 four-field shape on FR-6 emitter. Assertion: AT-032 passes. Source: AT-032. Automation hook: JSON-shape assertion. Severity: `blocking`.
- **PV-5.C10** — NFR-9 grep-reachable affordance from design-claude-code. Assertion: AT-033 passes. Source: AT-033. Automation hook: structural grep chain through `skills:` frontmatter. Severity: `blocking`.

### Operational checks

- Mutual cross-reference (PV-2.C3 ↔ PV-5.C4) confirmed bidirectional at this phase close — coordination with Phase 2's PV-2.C3.
- `TRIGGER_OVERRIDE` transition-name (T3.2) emit path verified — predicate exercises it via existing `log_state_transition.py`.

### Failure response

Plan rollback for Phase 5: template is new-file (removable); design-cc + recipe procedure additions are revertible. Most likely failure: advisory predicate logic error on conditions 3/4 (interpretive). On failure: halt Phase 7 dispatch (SA-14 depends on matrix template + predicate); revise; re-validate.

### Validator metadata

- **When run:** Once at Phase 5 close.
- **Expected duration:** ~1 min (8 deterministic checks + 2 grep chains).
- **Prerequisites:** PV-0, PV-2 passed. (PV-1 not strictly required at this phase but bridge consumed indirectly via downstream PV-7.)

---

## PV-6 — FR-7 skill-coverage discipline wired both ends

- **Phase reference:** Plan §Phase 6 — FR-7 skill-coverage discipline (tasks T6.1, T6.2, T6.3).
- **Validator goal:** Skill-Coverage Decisions section template authored; synthesizer emission procedure + design-composer substance-review procedure both extended; ADR-0065 Clause 1 honored (section embedded in `synthesis.md`).
- **Acceptance tests in scope:** AT-012 (emission), AT-013 (structural mandate blocks (b) row missing W/H/A), AT-014 (substance heuristic on (a)/(c) — **manual review**), AT-015 (complete (b) row passes), AT-034 (NFR-9 affordance grep-reachable from synth-synthesizer).
- **Severity vocabulary applied:** PV vocabulary; reviewer vocabulary on substance-heuristic findings (which are reviewer-judgment per ADR-0065 D-8).

### Pass criteria

- **PV-6.C1** — Section template exists. Assertion: `.claude/skills/KB-documentation-criteria/references/templates/skill-coverage-decisions-section-template.md` exists; grep returns `W/H/A` + decision types `(a)`, `(b)`, `(c)`. Source: T6.1 L2. Automation hook: grep + structural parse. Severity: `blocking`.
- **PV-6.C2** — synth-synthesizer emission procedure extended. Assertion: grep `.claude/agents/synth-synthesizer.md` for `Skill-Coverage Decisions` + `ADR-0065`. Source: T6.2 L2. Automation hook: grep. Severity: `blocking`.
- **PV-6.C3** — design-composer substance-review procedure extended. Assertion: grep `.claude/agents/design-composer.md` for `substance-heuristic` / `structural mandate` distinction + `ADR-0065` citation. Source: T6.3 L2. Automation hook: grep. Severity: `blocking`.
- **PV-6.C4** — Emission positive path. Assertion: AT-012 passes — synthesizer emits `## Skill-Coverage Decisions` section with one row keyed to a new concept. Source: AT-012. Automation hook: integration test. Severity: `blocking`.
- **PV-6.C5** — Structural mandate blocks incomplete (b) row. Assertion: AT-013 passes — design-composer blocks composition; missing heading named in finding. Source: AT-013. Automation hook: integration test. Severity: `blocking`.
- **PV-6.C6** — Complete (b) row passes. Assertion: AT-015 passes. Source: AT-015. Automation hook: unit test. Severity: `blocking`.
- **PV-6.C7** — Substance heuristic on (a)/(c) rows — **manual-review checkpoint**. Assertion: AT-014 reviewer-rubric pass; fixture A (concrete file path + positive evidence) passes; fixture B (bare cell) flagged. Source: AT-014. Automation hook: documented reviewer rubric — **not machine-verifiable** per ADR-0065 D-8 framing. Severity: `warning` on inconclusive reviewer judgment; `blocking` only on reviewer consensus that (a) fixture passes AND (b) fixture flags as needs-revision; per ADR-0065 kill-criteria, inter-reviewer disagreement >30% sustained across N≥3 runs triggers extension to structural mandate (a Plan revision, not a PV-6 failure).
- **PV-6.C8** — NFR-9 grep-reachable affordance from synth-synthesizer. Assertion: AT-034 passes. Source: AT-034. Automation hook: structural grep chain. Severity: `blocking`.

### Operational checks

- ADR-0065 Clause 1 honored: confirm section template embeds in `synthesis.md`, not a standalone file — grep template body for "embedded in `synthesis.md`" or equivalent location anchor.
- **Manual-review checkpoint named explicitly:** PV-6.C7 is the substance-heuristic gate; a named reviewer (or design-composer running the rubric) records their judgment in the validator-output ledger. Reviewer-judgment events are also logged for ADR-0065 kill-criteria tracking.

### Failure response

Plan rollback for Phase 6: template is new-file; procedure additions revertible. Substance-heuristic failure (PV-6.C7) at `warning` severity flows to user for explicit deferral decision; at `blocking` severity halts Phase 8 dispatch (eat-own-dogfood requires composer's substance review to be operational against this run's own Skill-Coverage section).

### Validator metadata

- **When run:** Once at Phase 6 close. PV-6.C7 manual checkpoint may run async if reviewer not available; other criteria run inline.
- **Expected duration:** ~30 s (automated); +reviewer-cycle (manual).
- **Prerequisites:** PV-0 passed. (PV-1 / PV-2 / PV-5 not required — Phase 6 is independent of Phases 1-5.)

---

## PV-7 — FR-10 SA-14 audit-subagents rule in catalog

- **Phase reference:** Plan §Phase 7 — FR-10 SA-14 audit-subagents rule (tasks T7.1, T7.2).
- **Validator goal:** SA-14 rule catalog entry exists; audit script operational on positive (BLOCKER on missing matrix), negative (no-op on no-trigger), and parity (row-count mismatch BLOCKER) paths; I-AA-005 SA-NN count fix applied.
- **Acceptance tests in scope:** AT-022 (BLOCKER on missing matrix), AT-023 (catalog entry grep), AT-024 (row-count parity BLOCKER), AT-025 (parity match no-op), AT-026 (no-trigger no-op — critical false-positive guard), AT-031 (NFR-8 four-field shape on FR-10 emitter).
- **Severity vocabulary applied:** PV vocabulary; auditor vocabulary on SA-14 findings.

### Pass criteria

- **PV-7.C1** — `audit_feature_touch_coverage.py` exists and smoke-tests pass on all three fixtures. Assertion: AT-022 (missing matrix → BLOCKER), AT-024 (row-count mismatch → BLOCKER), AT-025 (parity → no finding), AT-026 (no trigger → no finding). Source: AT-022, AT-024, AT-025, AT-026. Automation hook: `smoke_test_audit_feature_touch_coverage.py` covering all four fixtures. Severity: `blocking`.
- **PV-7.C2** — SA-14 catalog entry present. Assertion: AT-023 passes — grep `auditing-subagents/SKILL.md` for `SA-14` and `feature-touch-coverage`; reference file present under `auditing-subagents/references/`. Source: AT-023. Automation hook: grep + file-existence. Severity: `blocking`.
- **PV-7.C3** — I-AA-005 fold-in: SA-NN count fix applied. Assertion: `auditing-subagents/SKILL.md` description string SA-NN count is consistent with SA-14 as the latest rule (no orphaned `SA-15+` references; description count matches actual rule count). Source: T7.2 L2. Automation hook: grep + count-consistency check. Severity: `blocking` (this is the inherited I-AA-005 closure event).
- **PV-7.C4** — NFR-8 four-field shape on FR-10 emitter. Assertion: AT-031 passes. Source: AT-031. Automation hook: JSON-shape assertion. Severity: `blocking`.

### Operational checks

- Bridge severity vocabulary citation: SA-14 emits `BLOCKER` per the bridge; confirm script's emit-path imports / references the bridge file path (not a hard-coded literal divorced from the bridge).
- False-positive guard (PV-7.C1 via AT-026) is load-bearing: SA-14 must be silent when feature didn't touch the agent surface — this is the most consequential negative-path test in the entire run.

### Failure response

Plan rollback for Phase 7: catalog entry + audit script are new-additive; can be removed. I-AA-005 fold-in is a description-string edit; revertible. On failure: halt Phase 8 / 9 dispatch (eat-own-dogfood requires SA-14 operational; rollout depends on Phase 7's SA-14 run against this directory).

### Validator metadata

- **When run:** Once at Phase 7 close.
- **Expected duration:** ~20 s (four-fixture smoke test + grep).
- **Prerequisites:** PV-0, PV-1, PV-5 passed.

---

## PV-8 — Eat-own-dogfood self-application passes

- **Phase reference:** Plan §Phase 8 — Eat-own-dogfood (this run's matrix + decisions) (tasks T8.1, T8.2).
- **Validator goal:** This run's actual `agent-roster-impact-matrix.md` exists with 37 rows × 5 cells of positive-evidence content; this run's `synthesis.md` Skill-Coverage Decisions section verified at 6 rows; both self-applied contracts pass.
- **Acceptance tests in scope:** AT-035 (this run's matrix passes SA-14), AT-036 (37 rows × 5 cells × non-empty evidence), AT-037 (6-row Skill-Coverage section verification), AT-038 (design-composer substance review against this run's section — **manual review**), AT-028 (NFR-7 wall-clock measurement proxy).
- **Severity vocabulary applied:** PV vocabulary; auditor vocabulary on SA-14 findings against this directory.

### Pass criteria

- **PV-8.C1** — This run's matrix file exists. Assertion: `working/feature/pipeline-design-time-discipline-r1/agent-roster-impact-matrix.md` exists; markdown parses; five-column header present. Source: T8.1 L1. Automation hook: file-existence + structural parse. Severity: `blocking`.
- **PV-8.C2** — Matrix row + cell discipline. Assertion: AT-036 passes — row count = 37 (or T0.2 baseline); 185 cells each match `.+ — .+` with non-empty right-hand side; no bare `no change`. Source: AT-036. Automation hook: file-content parser. Severity: `blocking`.
- **PV-8.C3** — Matrix self-application passes SA-14. Assertion: AT-035 passes — `audit_feature_touch_coverage.py` invoked against this run's directory exits 0; no BLOCKER findings. Source: AT-035. Automation hook: integration self-test. Severity: `blocking`.
- **PV-8.C4** — Skill-Coverage Decisions section present in this run's `synthesis.md`. Assertion: AT-037 passes — 6 rows; all 6 type (a); each names skill path + positive-evidence justification; six concepts match Blueprint §Eat-own-dogfood Deliverables. Source: AT-037. Automation hook: file-content parser. Severity: `blocking`.
- **PV-8.C5** — Substance review against this run's Skill-Coverage section — **manual-review checkpoint**. Assertion: AT-038 reviewer-rubric pass; all six (a) rows pass W/H/A substance heuristic. Source: AT-038. Automation hook: documented reviewer rubric (per ADR-0065 D-8). Severity: `warning` on inconclusive reviewer judgment; `blocking` if reviewer flags any of the six rows as needs-revision (would re-open the in-run contract per Risk row 3 kill-criteria).
- **PV-8.C6** — NFR-7 wall-clock measurement evidence captured. Assertion: AT-028 passes (proxy form) — this run's matrix authoring first-write to last-write timestamps recorded; linear-extrapolation to 100 agents < 30 minutes. Source: AT-028. Automation hook: timestamp log entry (per OP-Plan-3: T8.1 L2 evidence is the proxy until run-state-log emission path is committed). Severity: `warning` on proxy-only measurement (acceptable per Plan disposition); `informational` on the linear-extrapolation result itself.

### Operational checks

- **Self-application is the contract-validation event by design** (Blueprint §Eat-own-dogfood Deliverables). PV-8 is the most critical-path validator in this run because failure here means the contracts as authored cannot self-apply — an in-run Blueprint revision per Risk row 3 kill-criteria, captured as a Blueprint Open Item.
- Dogfood validation evidence captured for I-AA-007 closure (rolled forward into PV-9).
- **Manual-review checkpoint:** PV-8.C5 is the substance-heuristic gate on this run's own Skill-Coverage section; reviewer-judgment events logged for kill-criteria tracking.

### Failure response

Plan rollback for Phase 8: matrix and section-verification are deliverables-only (no agent / KB file edits). On failure of PV-8.C1-C4 (mechanical checks): re-author the matrix or fix the section; re-validate. On failure of PV-8.C5 (substance review): open a Blueprint OI per Risk row 3 kill-criteria; possibly revise the contracts in-run; this is a recognized Blueprint risk path, not a hard rollback. PV-9 dispatch halted on any blocking PV-8 failure.

### Validator metadata

- **When run:** Once at Phase 8 close.
- **Expected duration:** ~1 min (matrix parse + SA-14 self-test + Skill-Coverage parse); +reviewer-cycle (manual PV-8.C5).
- **Prerequisites:** PV-0, PV-5, PV-6, PV-7 passed.

---

## PV-9 — Rollout / deliverable packaging sealed

- **Phase reference:** Plan §Phase 9 — Rollout / deliverable packaging (tasks T9.1, T9.2, T9.3).
- **Validator goal:** SA-14 audit against this run's directory passes; "What changed" communication summary archived; run-summary success-criteria evidence captured; I-AA-005 (closed Phase 7) and I-AA-007 (closed here) both reflected in deliverable archive; R2b kickoff unblocked per SPLIT-RECORD.
- **Acceptance tests in scope:** AT-035, AT-036, AT-037, AT-038 (eat-own-dogfood re-exercised at packaging time — overlaps PV-8 but rolled forward for archive evidence); all other ATs read-only at this phase.
- **Severity vocabulary applied:** PV vocabulary.

### Pass criteria

- **PV-9.C1** — SA-14 audit against this run's directory passes (re-exercised at packaging time). Assertion: T9.1 L1/L2/L3 — `audit_feature_touch_coverage.py` exits 0; no BLOCKER entries; I-AA-007 INFO entry transitioned to `closed` in audit-issues. Source: T9.1, AT-035. Automation hook: shell invocation + audit-issues.json grep. Severity: `blocking`.
- **PV-9.C2** — "What changed for future feature authors" summary exists. Assertion: file present in deliverable archive directory; FR-1, FR-6, FR-7, FR-8, FR-9, FR-10 all named; both new ADRs (0064, 0065) cited; severity-bridge publication for R2b noted; three inherited ADRs (0059, 0061, 0063) cited. Source: T9.2 L2. Automation hook: grep chain over summary file. Severity: `blocking`.
- **PV-9.C3** — Run-summary success-criteria evidence captured. Assertion: pipeline-run-summary file present per template; each PRD §Success Criteria row points to a file path + a date. Source: T9.3 L2. Automation hook: structural parse of run summary. Severity: `blocking`.
- **PV-9.C4** — Deliverable archive sealed per `deliverable-archive-spec.md`. Assertion: archive directory matches the spec; bridge content (`severity-taxonomy.md`) included for R2b inheritance per SPLIT-RECORD. Source: T9.3 L3. Automation hook: archive-spec validator + manual confirmation. Severity: `blocking`.
- **PV-9.C5** — I-AA-005 + I-AA-007 closure reflected in deliverable archive. Assertion: audit-issues ledger shows both issues `status: closed`; closure evidence (script pass output for I-AA-007, count-fix patch for I-AA-005) attached. Source: T9.1 L3, Plan §Update History. Automation hook: ledger query. Severity: `blocking`.
- **PV-9.C6** — Packager smoke checks clear. Assertion: standard packaging smoke (frontmatter parses; supersedence chain intact; no orphan working-directory files) runs without error. Source: deliverable-archive-spec. Automation hook: packager smoke-test script. Severity: `blocking`.

### Operational checks

- SPLIT-RECORD R2a-runs-first ordering honored: bridge file (`severity-taxonomy.md`) is in the published archive; R2b kickoff (which inherits the bridge) can read the content without further work.
- This run is single-layer (Claude Code only) → no cross-layer feature-flag, no rollout-percentage dial, no monitoring-period equivalent. The rollout discipline is publication + archive sealing, not deploy + observation.
- "Feature flag at target percentage" / "monitoring period elapsed" criteria from the standard Phase N+1 template are **N/A for this run** — surfaced explicitly so reviewers don't treat their absence as a gap.

### Failure response

Plan rollback for Phase 9: deliverable archive is the terminal artifact; failure means archive not yet sealed → no rollback needed, only re-author the failing deliverable. On failure: address findings; re-run PV-9; only after PV-9 passes does the R2b kickoff signal go out. R2b consumers (FR-4, FR-5 of R2b) are gated on the bridge file's archive publication; PV-9.C4 is the gate they read.

### Validator metadata

- **When run:** Once at Phase 9 close — the final gate for the run.
- **Expected duration:** ~1 min (SA-14 re-run + grep + archive validator).
- **Prerequisites:** PV-0..PV-8 all passed.

---

## Cross-validator coordination

### Critical-path validators

In order of failure-blast-radius:

1. **PV-1** (severity bridge) — failure cascades to PV-3 / PV-4 / PV-7 / PV-8 / PV-9 (every downstream emitter cites the bridge).
2. **PV-5** (matrix contract) — failure cascades to PV-7 (SA-14 needs the predicate + template) and PV-8 (dogfood requires the template to author the matrix against).
3. **PV-8** (eat-own-dogfood) — failure means contracts as authored do not self-apply; triggers Risk row 3 kill-criteria (in-run Blueprint revision).

### Parallelizable validator checks

Within a single validator, several criteria can run in parallel:

- PV-3 criteria C1, C2, C3, C4 (parser + template + agent procedure edits — independent grep / smoke checks).
- PV-5 criteria C1, C2-C3, C4, C5 (template + predicate-deterministic + predicate-advisory + agent edits — independent).
- PV-6 criteria C1, C2, C3 (template + synthesizer + composer edits — independent).
- All NFR-8 four-field-shape checks (PV-3.C6, PV-4.C7, PV-5.C9, PV-7.C4) can run in parallel as a single batch.
- All NFR-9 grep-reachable checks (PV-5.C10, PV-6.C8) can run in parallel.

### Shared validator infrastructure

- **Fixture directory:** `tests/fixtures/<at-NNN>-<short-name>/` per acceptance-tests.md §Test infrastructure required. Validators reuse fixtures across criteria.
- **Smoke-test pattern:** Sibling `smoke_test_*.py` files per acceptance-tests.md convention. Reused for unit-criteria across PV-3 / PV-4 / PV-5 / PV-7.
- **Severity bridge file:** `KB-review-disciplines/references/severity-taxonomy.md` — read by PV-3.C6, PV-4.C7, PV-5.C9, PV-7.C4 for emit-path verification.
- **Audit-issues ledger:** Closure evidence captured for I-AA-005 (PV-7) and I-AA-007 (PV-9).
- **Manual-review rubric:** PV-6.C7 + PV-8.C5 share the substance-heuristic rubric documented in design-composer.md (per T6.3); reviewer-judgment events logged consistently.

### Validator runbook (human operator)

To execute the validator suite during a real run:

1. At each Phase close, run the corresponding PV criteria. Automated criteria first (parallel where possible); manual checkpoints async.
2. Capture `blocking` failures immediately; do not dispatch downstream phase until resolved.
3. Capture `warning` failures with explicit user deferral decision recorded in the run state log.
4. Capture `informational` outcomes in the deliverable archive's evidence trail.
5. At PV-9, the deliverable-archive-spec validator is the terminal acceptance gate; only PV-9 pass signals R2b kickoff per SPLIT-RECORD.

## Phases hard to validate mechanically

- **PV-6.C7** — substance heuristic for FR-7 (a)/(c) decision rows. Per ADR-0065 D-8 framing, judgment-based. Mitigated by reviewer-rubric + kill-criteria tracking; not a coverage gap.
- **PV-8.C5** — substance review against this run's own Skill-Coverage section. Same posture as PV-6.C7; this run is the first reviewer-rubric exercise event for the rubric itself.
- **PV-8.C6** — NFR-7 wall-clock proxy. Per OP-Plan-3, run-state-log emission path not Plan-committed; T8.1 L2 timestamps are the proxy. Linear-extrapolation from 37 → 100 agents is the documented assertion form; a 100-agent operational measurement is the natural future validation (not in this run's scope).
- **PV-4.C6** — NFR-1 5000 ms budget. Jitter-sensitive; median-of-3 mitigation + controlled execution lane. First-occurrence `warning` posture acknowledges the flake risk per AT-027 determinism notes.

## Open Items (Pending Cross-Artifact Audit)

- **OP-PV-1 — PV-0 lightweight scope ratification.** Per OP-Plan-1 disposition, PV-0 is intentionally lightweight (file/inventory existence) since Phase 0 has no PRD AC bindings. Surfaced for cross-artifact-auditor confirmation that this discharges the plan-template's "validator per phase" rule without folding Phase 0 into Phase 1 scope.
- **OP-PV-2 — Manual-review checkpoint logging convention.** PV-6.C7 and PV-8.C5 require a reviewer-judgment record in the validator-output ledger. The ledger schema for `reviewer_judgment` events is not Plan-committed (per OP-Plan-3 cousin). Routed to `review-cross-artifact-auditor` for ratification or punt to operational discretion.
- **OP-PV-3 — PV-4.C6 controlled-execution-lane definition.** Per OP-Plan-2 disposition, AT-027 inline timing lives in the auditor's own logging; the "controlled execution lane" naming convention for the performance test is not codified. Routed to `test-acceptance-author` for AT-027 harness mechanics or `review-cross-artifact-auditor` for ratification.

## Update History

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-05-26 | test-phase-validator-author | Initial Phase Validators for R2a — 10 validators (PV-0..PV-9), one per Plan phase. PV vocabulary applied; auditor + reviewer vocabularies bridged via `severity-taxonomy.md` (this run's Phase 1 deliverable). PV-6.C7 and PV-8.C5 documented as manual-review checkpoints per ADR-0065 D-8 substance-heuristic posture. PV-4.C6 NFR-1 performance criterion uses `warning`-then-`blocking` escalation per AT-027 jitter mitigation. Three OP items surfaced for cross-artifact-auditor disposition. |

---

*End of Phase Validators v1.0.0 for `pipeline-design-time-discipline-r1`. Next stage: `review-cross-artifact-auditor` runs diff-mode consistency check across Blueprint ↔ Plan ↔ Tests ↔ PVs.*
