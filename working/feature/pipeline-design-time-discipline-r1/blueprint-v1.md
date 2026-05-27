---
id: BP-pipeline-design-time-discipline-r1
version: 1.0.1
status: draft
doc_type: blueprint
feature_slug: pipeline-design-time-discipline-r1
scope_class: MINOR
derived_from:
  - working/feature/pipeline-design-time-discipline-r1/prd-v1.md
  - working/feature/pipeline-design-time-discipline-r1/intent-clarification.md
  - working/feature/pipeline-design-time-discipline-r1/synthesis.md
  - working/feature/pipeline-design-time-discipline-r1/cc-design.md
  - working/feature/pipeline-design-time-discipline-r1/cc-dependencies.json
  - working/feature/pipeline-design-time-discipline-r1/codebase-analysis.json
parent_run: pipeline-cross-artifact-discipline-r1
related_run: pipeline-gate-validator-hardening-r1
inherited_adrs: [ADR-0059, ADR-0061, ADR-0063]
adrs_authored_this_run: [ADR-0064, ADR-0065]
adr_range_reserved: 0064-0069
predecessor: working/feature/pipeline-cross-artifact-discipline-r1/blueprint-v1.md
generated: 2026-05-26T17:45:00Z
generated_by: design-composer
---

# Blueprint: Pipeline Design-Time Discipline (R2a)

## Update history

| Version | Date | Author | Summary |
|---|---|---|---|
| 1.0.0 | 2026-05-26 | design-composer | Initial composition for R2a — design-time-discipline half of the parent R2 split. Integrates `cc-design.md` (single-layer R2a). Authors two new ADRs (0064, 0065) and inherits three (0059, 0061, 0063). Includes severity bridge content (D-10 substrate). |
| 1.0.1 | 2026-05-26 | design-composer | Reconciliation cycle 1 patches per architecture-audit findings: (a) bridge-consumer count corrected 20 → 24 (I-AA-003); (b) inline 6-row Skill-Coverage Decisions table removed and replaced with a paragraph pointer to the canonical artifact in `synthesis.md` per ADR-0065 Clause 1, with back-fill landed in companion synth-synthesizer dispatch (I-AA-004); (c) Executive Summary phrasing updated to reflect cycle-1 back-fill timing (I-AA-004). In-place edits per ADR-0005 (no supersession). Companion in-place patches to ADR-0064 v1.0.1 (I-AA-001), ADR-0065 v1.0.1 (I-AA-002), and codebase-analysis.json (I-AA-006) land in the same revision pass. |

## Brief-honor citation

The user's verbatim thesis from the parent rationale brief, which every architectural decision in this Blueprint honors:

> "the pipeline must verify relationships across artifacts, not just per-artifact correctness — cancels the structural defect-class behind r1's shipment and the recurrence risk every agent-surface feature inherits."

(Carried verbatim per ADR-0009; first cited in parent `pipeline-cross-artifact-discipline-r1/blueprint-v1.md`; re-cited here because R2a is the design-time half of the parent's split and the thesis is structurally load-bearing on every R2a FR.)

## Executive summary

R2a ships the design-time-discipline half of the parent run's split — six PRD mechanisms (FR-1, FR-6, FR-7, FR-8, FR-9, FR-10) that move per-agent design evaluation and ADR design-realization audit from aspiration to structural prevention. Three parent-run ADRs (0059, 0061, 0063) close the prescription-extraction question, pin the severity-vocabulary bridge host, and canonicalize the Blocks-X marker grammar — R2a inherits these unchanged. Two new ADRs land in this run (0064 — agent-roster impact matrix contract; 0065 — skill-coverage decision discipline) that codify the two heaviest R2a decisions for future feature runs. The remaining decisions resolve as Blueprint commitments (severity bridge content authored; marker-parser placed at `auditing-shared/scripts/`; Skill-Coverage Decisions embedded in `synthesis.md`; FR-10 realized as new SA-14 audit rule; plan sequences bridge content before FR-1/9/10 consumers).

R2a applies its own contracts to itself: this run produces an `agent-roster-impact-matrix.md` (per ADR-0064) and six skill-coverage decisions (per ADR-0065) (back-filled at Cycle-1 reconciliation per audit I-AA-004; see `synthesis.md` §Skill-Coverage Decisions), validating the contracts before they're imposed on future authors.

## Background

### What exists today

The pipeline's design-time stage has structural defects that have surfaced in two recent runs:

- **`devcontainer-mcp-provisioning-r1`** shipped MCP-tool drift (5 of 7 MCP servers broken at the eventual `.mcp.json`) because no auditor compared ADR-0041's prescribed invocations against the eventual implementation files. The defect was caught post-ship; forensic recovery was required.
- **`per-agent-design-evaluation-gap`** analysis (parallel investigation of the same run) found a sibling defect on the design-time side: the pipeline iterated the *changed* agent surface (8 of 36 agents got the new MCP tools) without ever enumerating the full inventory to confirm the other 28 should not change. The gap was caught at Gate 4 by the user.
- **`issue-capture-mechanism-r1`** Phase 1 produced a structural spec whose §7 ID-derivation rule contradicted its three sibling templates and five empirical precedents; PV-1 passed cleanly because no validator compared the spec to the templates.

Three failures, one shape: per-artifact correctness gates passed; cross-artifact relationships were not verified.

The parent run `pipeline-cross-artifact-discipline-r1` planned eleven mechanisms to address this defect class. The parent was split at Gate 4 (Blueprint Approval) by user decision when the open-item count threatened the cross-artifact-audit's 4-cycle reconciliation cap. Five ADRs (0059, 0060, 0061, 0062, 0063) were accepted in the parent run before the split. R2a (this run) is the design-time-discipline half; R2b is queued as `pipeline-gate-validator-hardening-r1`.

### What this Blueprint ships

Six mechanisms inside the `.claude/` configuration:

1. **FR-1 — Design-realization audit dimension** on `review-architecture-auditor`. Inputs the ADR-0059 companion `.prescriptions.yaml`; emits BLOCKER findings on prescription-vs-implementation divergence.
2. **FR-6 — Mandatory `agent-roster-impact-matrix.md`** when a feature touches the agent surface. Full-inventory rows × five dimensions × positive-evidence cells. Contract codified in **ADR-0064**.
3. **FR-7 — Skill-coverage decision check** for new domain concepts. Hybrid W/H/A trifecta (structural mandate for new-skill proposals; substance heuristic elsewhere). Embedded section in `synthesis.md`. Discipline codified in **ADR-0065**.
4. **FR-8 — KB-cc-design Principle 9 active reframing** from defensive to active framing — the per-agent consideration is recorded even when the outcome is no change.
5. **FR-9 — Blocks-X marker enforcement** as stage-transition gates. Grammar inherited from ADR-0063; parser realized at `auditing-shared/scripts/parse_blocks_x_markers.py`.
6. **FR-10 — `auditing-subagents` matrix-missing audit rule** (new SA-14 entry) — backstop to FR-6 at packaging time.

Plus one cross-cutting deliverable:

- **Severity bridge content** authored into `.claude/skills/KB-review-disciplines/references/severity-taxonomy.md` per inherited ADR-0061 (the host is fixed; this run authors the actual five-column table + Weight Preservation Note).

## Layer Scope

| Layer | In scope | Designer | Section |
|---|---|---|---|
| **Claude Code / Project Filesystem** | YES | `design-cc` | §Claude Code Design |
| Frontend | NO | — | N/A — out of scope per PRD Layer Scope |
| Backend | NO | — | N/A — out of scope per PRD Layer Scope |
| API | NO | — | N/A — out of scope per PRD Layer Scope |
| Query / Data Access | NO | — | N/A — out of scope per PRD Layer Scope |
| Database | NO | — | N/A — out of scope per PRD Layer Scope |
| CI/CD (GitHub Actions) | NO | — | N/A — out of scope per PRD Layer Scope |
| Infrastructure as Code | NO | — | N/A — out of scope per PRD Layer Scope |
| Dev Environment (Codespaces / Devcontainer) | NO | — | N/A — out of scope per PRD Layer Scope |

Single-layer feature. Eight of nine taxonomy layers explicitly out of scope per the parent brief's direction.

## Design summary

```yaml
design_type: claude-code-configuration
risk_level: medium  # touches review/audit machinery; defect-prevention surface
complexity_level: medium  # 6 mechanisms; 3 inherited ADRs; 2 new ADRs
blast_radius:
  changed_agents: 6  # review-architecture-auditor, design-cc, design-composer, synth-synthesizer, discovery-codebase-researcher, execute-orchestrator
  changed_skills: 4  # KB-cc-design, KB-review-disciplines, KB-documentation-criteria, auditing-subagents
  new_scripts: 4  # parse_blocks_x_markers.py, check_feature_touch_predicate.py, audit_feature_touch_coverage.py, validate_adr_prescriptions.py
  new_templates: 3  # agent-roster-impact-matrix-template.md, skill-coverage-decisions-section-template.md, severity-taxonomy.md content
  new_adrs: 2  # ADR-0064, ADR-0065
  inherited_adrs: 3  # ADR-0059, ADR-0061, ADR-0063
dependencies:
  inherited_from_parent_run: pipeline-cross-artifact-discipline-r1
  feeds_queued_run: pipeline-gate-validator-hardening-r1  # via populated severity bridge
  internal_only: true  # no cross-layer edges; single-layer feature
```

## Architecture overview

The R2a feature lands as a discipline layer over the existing pipeline. No new sub-agents, no new orchestrator stages, no new layer.

```
                          ┌──────────────────────────────────┐
                          │     Existing pipeline stages     │
                          │                                  │
   Discovery ──► Synthesis ──► per-layer Design ──► Design Composition ──► Plan ──► Tests/PVs ──► Execute
                          │       │       │              │              │              │
                          │       │       │              │              │              │
                          ▼       ▼       ▼              ▼              ▼              ▼
                       FR-9    FR-7    FR-1/8         FR-6/7         FR-1/9         FR-10
                       (Blocks (Skill  (Principle 9   (matrix       (audit + gate)  (matrix-
                        markers cov.   active +       deliverable                   missing
                        as gates) decisions)  audit dim)   blocked   gate)         rule)
                                       (R-AA)        if matrix
                                                    missing)
                                  ┌─────────────────────────────┐
                                  │   Cross-cutting deliverable │
                                  │  Severity bridge (D-10)     │
                                  │  in KB-review-disciplines    │
                                  │  per ADR-0061               │
                                  └─────────────────────────────┘
```

**Key architectural observation.** The six mechanisms cluster around three pipeline transition points:

- **Synthesis → Design Composition:** FR-7 (skill-coverage decisions) + FR-6 trigger evaluation (advisory predicate reads the FR-7 section). ADR-0065 codifies the FR-7 contract; ADR-0064 codifies the FR-6 contract; both bind at this transition.
- **Design Composition → Audit:** FR-1 (design-realization audit) reads ADR-0059 companion files. FR-8 (active Principle 9) is the substance test applied during Design Composition that produces the matrix FR-1 then audits.
- **Pre-deliverable packaging:** FR-9 (Blocks-X markers) + FR-10 (matrix-missing audit rule). Both are last-line backstops.

The severity bridge content (D-10) is the cross-cutting glue — FR-1, FR-9, and FR-10 all reference it for severity emission per ADR-0061's "reference by name, not by copy" guidance.

## Data flow (top-level)

Single primary scenario: **a future feature run that touches the agent surface and introduces a new domain concept** (the worst-case load on this Blueprint's disciplines).

```
1. Discovery: codebase-researcher writes "Blocks <stage>" markers if needed (FR-9 / ADR-0063).
   ─► Orchestrator records markers in state-transitions.log via parse_blocks_x_markers.py.

2. Synthesis: synth-synthesizer identifies new domain concept(s).
   ─► Synthesis emits Skill-Coverage Decisions section (FR-7 / ADR-0065).
   ─► For each concept: (a) existing-skill, (b) propose-new-skill, or (c) no-skill-warranted.

3. per-layer Design: per-layer designers run as usual. design-cc consults active Principle 9 (FR-8).

4. Design Composition: design-composer integrates per-layer outputs.
   ─► FR-6 advisory predicate evaluates trigger conditions 1-4 (per ADR-0064 Clause 3).
   ─► If trigger fires: design-cc MUST author agent-roster-impact-matrix.md before completion.
   ─► design-composer arbitrates Q-CC-N items; may author ADRs.
   ─► Blueprint produced.

5. shared-document-reviewer (Gate 0 + Gate 1): reviews Blueprint.
   ─► Reviewer verifies matrix presence, row count, cell discipline if trigger fired.

6. review-architecture-auditor (FR-1): runs design-realization audit.
   ─► For each ADR with a .prescriptions.yaml companion: compare prescription vs eventual file.
   ─► Emit BLOCKER findings per ADR-0061 severity bridge if divergence.

7. Orchestrator: at each stage-transition checkpoint, invokes parse_blocks_x_markers.py.
   ─► Refuses to advance until all Blocks-X markers transition to RESOLVED / DEFERRED / FALSE_POSITIVE.

8. Plan → Tests → PVs → Execute (existing stages, unchanged).

9. Pre-deliverable packaging: auditing-subagents runs SA-14 (FR-10).
   ─► If feature touched agent surface: verify matrix presence + row count.
   ─► Emit BLOCKER finding on absence / mismatch per ADR-0061 severity bridge.
```

## Change impact map

Files modified by this run, grouped by surface:

### Agents (6 modified, 0 new)

| File | Change shape |
|---|---|
| `.claude/agents/review-architecture-auditor.md` | Add design-realization audit phase (FR-1) as additive procedure phase. Reasoning config unchanged. |
| `.claude/agents/design-claude-code.md` | Phase 2 extension: matrix authoring procedure (FR-6 / ADR-0064). Verbatim citation of Principle 9 updated to active framing (FR-8 AC-FR-8-b). |
| `.claude/agents/design-composer.md` | Blueprint composition reads Skill-Coverage Decisions section; blocks on missing (b) trifecta headings (FR-7 / ADR-0065). |
| `.claude/agents/synth-synthesizer.md` | Emit Skill-Coverage Decisions section row when new concept identified (FR-7 / ADR-0065). |
| `.claude/agents/discovery-codebase-researcher.md` | Emit Blocks-X markers per ADR-0063 grammar (FR-9). |
| `.claude/agents/execute-orchestrator.md` | Stage-transition gate logic invokes parse_blocks_x_markers.py (FR-9). |

### Skills (4 modified, 0 new skill directories)

| File | Change shape |
|---|---|
| `.claude/skills/KB-cc-design/references/principles.md` | Principle 9 leading sentence: defensive → active (FR-8). Mutual cross-reference with FR-6 cell discipline (AC-FR-8-b). |
| `.claude/skills/KB-review-disciplines/references/architecture-audit.md` | Lens 4: Design Realization added (FR-1). |
| `.claude/skills/KB-review-disciplines/references/severity-taxonomy.md` | Author the D-10 severity bridge content (five-column table + Weight Preservation Note). Host fixed by inherited ADR-0061. |
| `.claude/skills/auditing-subagents/SKILL.md` | New rule entry SA-14 (FR-10). |
| `.claude/skills/auditing-subagents/references/` | New SA-14 discipline reference (FR-10). |
| `.claude/skills/recipe-feature-pipeline/SKILL.md` | Outputs table for design-cc gets matrix row; Design Composition close gate description updated. |
| `.claude/skills/KB-documentation-criteria/references/templates/agent-roster-impact-matrix-template.md` | NEW template (FR-6 / ADR-0064). |
| `.claude/skills/KB-documentation-criteria/references/templates/skill-coverage-decisions-section-template.md` | NEW template (FR-7 / ADR-0065). |
| `.claude/skills/KB-documentation-criteria/references/templates/state-transitions-log-entry-template.md` | Documentation update: enumerate `BLOCKS_X_RESOLVED`, `BLOCKS_X_DEFERRED_WITH_OI`, `BLOCKS_X_FALSE_POSITIVE`, `TRIGGER_OVERRIDE` as valid `transition_name` values (FR-9, FR-6/ADR-0064). Schema unchanged (ADR-0044 v1). |

### Scripts (4 new, 0 modified)

| File | Purpose |
|---|---|
| `.claude/skills/auditing-shared/scripts/parse_blocks_x_markers.py` | Canonical marker parser per ADR-0063 grammar. Consumed by orchestrator + future audit rules. (FR-9) |
| `.claude/skills/auditing-subagents/scripts/check_feature_touch_predicate.py` | Advisory predicate for FR-6 trigger conditions (per ADR-0064 Clause 3). |
| `.claude/skills/auditing-subagents/scripts/audit_feature_touch_coverage.py` | SA-14 audit script: presence + row-count parity (FR-10). |
| `.claude/skills/auditing-shared/scripts/validate_adr_prescriptions.py` | Schema-validates ADR-0059 companion files (FR-1 support). |

### ADRs (2 new, 3 inherited)

| ADR | Status | Authored by |
|---|---|---|
| **ADR-0064** | NEW — Authored this run | `design-composer` |
| **ADR-0065** | NEW — Authored this run | `design-composer` |
| ADR-0059 | Inherited from parent run | Parent `design-composer` |
| ADR-0061 | Inherited from parent run | Parent `design-composer` |
| ADR-0063 | Inherited from parent run | Parent `design-composer` |

## Interface change matrix

Single-layer feature → no cross-layer interface changes. The relevant intra-CC-layer interfaces:

| Interface | Producer | Consumer | Change |
|---|---|---|---|
| `agent-roster-impact-matrix.md` | `design-cc` at Design Composition | `shared-document-reviewer` inv. 3; SA-14 audit; FR-8 substance test | NEW deliverable per ADR-0064 |
| `Skill-Coverage Decisions` section in `synthesis.md` | `synth-synthesizer` | `design-composer`; FR-6 advisory predicate; `shared-document-reviewer` inv. 2 | NEW section per ADR-0065 |
| `ADR-NNNN.prescriptions.yaml` (companion file) | `design-composer` (when authoring an ADR that prescribes implementation artifacts) | `review-architecture-auditor` Lens 4 | NEW pattern per inherited ADR-0059 |
| `state-transitions.log` `transition_name` values | `execute-orchestrator` | log readers | Four new values: `BLOCKS_X_RESOLVED`, `BLOCKS_X_DEFERRED_WITH_OI`, `BLOCKS_X_FALSE_POSITIVE`, `TRIGGER_OVERRIDE`. Free-string per ADR-0044 v1; no schema evolution. |
| `audit-issues.json` finding shape | All FR-1 / FR-9 / FR-10 emitters | downstream consumers | Additive NFR-8 four-field shape (`rule`, `target`, `divergence`, `next_action`) per inherited ADR-0061. |
| Severity vocabulary translation | source-vocab emitters | target-vocab consumers (PV, reviewer) | NEW bridge table content at `KB-review-disciplines/references/severity-taxonomy.md`. Optional translator helper at `auditing-shared/scripts/translate_severity.py`. |

## Fact disposition table

The codebase-analysis.json focus areas (R2a-additive corpus; 96 claims layered on inherited parent corpus). Each focus area enumerated with disposition.

| focusArea | Disposition | Rationale |
|---|---|---|
| `mechanism_dependency_table[FR-1]` | **preserve + extend** | FR-1 implementation reads the table; the table identifies the new audit-dimension target files. |
| `mechanism_dependency_table[FR-6]` | **preserve + extend** | FR-6 implementation reads the table; ADR-0064 codifies the contract over the table's identified target files. |
| `mechanism_dependency_table[FR-7]` | **preserve** | FR-7's mechanical parseability claim (C-0071) supports D-5 hybrid; no extension needed. |
| `mechanism_dependency_table[FR-8]` | **preserve** | Concentrated 2-site edit (line 182 in principles.md + line 56 in design-claude-code.md) per FR-8 design. |
| `mechanism_dependency_table[FR-9]` | **preserve + extend** | Realization-location decision (D-R2a-3) extends the table with `auditing-shared/scripts/parse_blocks_x_markers.py`. |
| `mechanism_dependency_table[FR-10]` | **preserve + extend** | New rule entry (D-R2a-5) extends the auditing-subagents catalog with SA-14. |
| `blast_radius_new_confirmations[1]` (37-agent count) | **preserve** | Drives matrix row count per AC-FR-6-b. |
| `blast_radius_new_confirmations[4]` (24-agent KB-review-disciplines load; count corrected from inherited 20 at reconciliation cycle 1 per audit I-AA-003) | **preserve** | Severity bridge propagates broadly with no separate propagation work. |
| `severity_vocabulary_facts` | **transform → bridge table content** | Source corpus is the auditor and verdict-compute source files; transformation = the bridge table author this run lands. |
| `parser_existing_state[FR-9]` (zero parser; C-0073) | **preserve (greenfield)** | D-R2a-3 places greenfield parser at canonical library home. |
| `audit_catalog_existing_state[FR-10]` (no existing rule predicating on feature working-dir; C-0066/C-0078) | **preserve (greenfield)** | D-R2a-5 adds new SA-14 entry without conflating with existing rules. |
| `kb_review_disciplines_load_count` | **preserve** | 24 agents inherit the bridge (count corrected from inherited 20 at reconciliation cycle 1 per audit I-AA-003); no additional propagation surface. |
| `ic_oi_9_resolution_evidence` | **preserve** | Five-explicit dimension count carries forward to ADR-0064 Clause 2. |
| All inherited parent focusAreas (PRD §Inheritance Manifest) | **preserve** | Inherited verbatim per ADR-0009 brief-honor + parent decisions D-1/D-4/D-8. |

No focusArea is removed or marked out-of-scope. R2a's discovery layered additively on the parent's analysis; nothing was contradicted.

## Per-layer Design

### Claude Code Design

The Claude Code per-layer design subsection is authored at `working/feature/pipeline-design-time-discipline-r1/cc-design.md` v1.0.0 by `design-cc` and is integrated by reference into this Blueprint. The subsection provides per-FR design (FR-1, FR-6, FR-7, FR-8, FR-9, FR-10) including target files, decisions adopted, primitive justifications, reasoning-configuration justifications, and surfaced Q-CC-N items.

This Blueprint integrates the per-layer design verbatim by reference. Key integration anchors:

- **FR-1** — Design-realization audit dimension; new audit phase on `review-architecture-auditor`; depends on inherited ADR-0059 companion file. Severity bridge consumer (per ADR-0061).
- **FR-6** — Mandatory matrix; contract codified in **ADR-0064** (this run). Resolution: full-inventory + five explicit dimensions + positive-evidence-string cells + hybrid advisory predicate + human ratification + override logging.
- **FR-7** — Skill-coverage decisions embedded in `synthesis.md`; hybrid W/H/A discipline codified in **ADR-0065** (this run).
- **FR-8** — Principle 9 active reframing at `KB-cc-design/references/principles.md:182` + cross-reference at `design-claude-code.md:56`. Verbatim sentence replacement per cc-design §FR-8.
- **FR-9** — Marker grammar inherited from ADR-0063; parser realized at `auditing-shared/scripts/parse_blocks_x_markers.py` (D-R2a-3 ratified). Three new `transition_name` values reserved per ADR-0063.
- **FR-10** — New SA-14 audit rule (D-R2a-5 ratified); backstops FR-6 at packaging time. Severity bridge consumer.

### All other layers — N/A

Frontend, Backend, API, Query, Database, CI/CD, IaC, Codespaces: **N/A — not in scope per PRD Layer Scope**. No per-layer design subsection authored. No cross-layer interface changes (single-layer feature).

## Cross-cutting concerns

### Severity bridge content (D-10 substrate)

Per inherited ADR-0061, the severity-vocabulary bridge table lives at `.claude/skills/KB-review-disciplines/references/severity-taxonomy.md`. The parent run fixed the host; this run authors the actual content.

**Five-column bridge table:**

| auditor_vocab | reviewer_vocab | pv_vocab | non_monotonic_edges | iteration_delta_weight |
|---|---|---|---|---|
| `BLOCKER` | `critical` | `blocking` | — (monotonic; forces refuse-to-advance across all surfaces) | **10** |
| `MAJOR` | `important` | `blocking` OR `warning` (branches by PV-tier invariant class — see `MAJOR_branching_PV` edge below) | `MAJOR → {blocking, warning}` — default `blocking`; downgrade to `warning` only with explicit per-finding rationale | **3** |
| `MINOR` | `recommended` | `warning` | — (monotonic) | **1** |
| `NIT` (auditing-mcp) | `recommended` | `informational` | `NIT ↔ recommended`: NIT carries "taste" framing (subjective); `recommended` carries "improvement" framing (actionable). Reverse mapping (recommended → NIT) loses actionability. | **0** |
| `INFO` (architecture / cross-artifact auditors) | (no direct analog; neutral observation) | `informational` | `NIT vs INFO` intra-auditor divergence: same severity floor (-0.5 and 0 verdict-compute weight respectively); auditing-mcp uses NIT, architecture/cross-artifact auditors use INFO. Preserve both per Known Issue 2. | **0** |

**Verdict-compute weights (the OTHER weight set):**

| Severity | Verdict-compute deduction |
|---|---|
| `BLOCKER` | **-12** (with additional -12 escalation penalty = -24 total when the BLOCKER persists across iterations) |
| `MAJOR` | **-5** |
| `MINOR` | **-2** |
| `NIT` | **-0.5** |
| `INFO` | **0** (diagnostic only; surfaced but not score-impacting) |

**Weight Preservation Note.** Both weight sets remain because they encode different mathematical roles:

- **Verdict-compute weights** (-12 / -5 / -2 / -0.5 / 0) drive the **single-iteration gate-pass / fail computation** in `auditing-cc-configs/scripts/verdict_compute.py`. They answer "is this iteration's audit verdict pass or fail?" by summing per-finding deductions. The values are calibrated against existing gate-pass thresholds; removing or rebalancing them would force every downstream rubric to be re-calibrated.
- **Iteration-delta weights** (10 / 3 / 1 / 0 / 0) drive the **convergence / cap-tripping logic across iterations** in the 4-cycle reconciliation cap (per KB-review-disciplines cross-artifact-audit). They answer "is the audit converging or oscillating?" by tracking total-weight-resolved vs total-weight-introduced per cycle.

The two roles are independent. Collapsing into one weight set would force either: (a) gate-pass thresholds become a function of how many cycles have run (breaks per-iteration determinism), or (b) convergence-tracking becomes coarse-grained on the BLOCKER vs MAJOR distinction (breaks 4-cycle cap intent). Preserving both is the cleanest separation of concerns.

**Non-monotonic edges (explicit enumeration):**

1. **NIT vs INFO intra-auditor divergence.** `auditing-mcp` uses `NIT` (-0.5 verdict-compute deduction); `review-architecture-auditor.md` and `review-cross-artifact-auditor.md` use `INFO` (0 deduction). Same conceptual severity floor; different names and score impacts. Optional translator helper at `auditing-shared/scripts/translate_severity.py` records source-auditor surface as context.
2. **NIT ↔ recommended translation difficulty.** Reviewer-side `recommended` is the closest match for `NIT`, but `recommended` is intended actionable while `NIT` is explicitly low-priority. Translator outputs include "NIT — non-actionable in reviewer surface" rationale.
3. **MAJOR → {blocking, warning}.** PV vocabulary collapses to two grades on MAJOR: `blocking` if outright assertion-not-satisfied; `warning` if partial (predicate True with caveat). Translator requires assertion-failure-mode as input; ambiguity surfaces explicit translator error rather than silent collapse.

**NFR-8 four-field finding shape (co-located in bridge host file).** Per inherited ADR-0061, the bridge host also documents the NFR-8 four-field shape that FR-1, FR-9, FR-10 emitters use: `rule`, `target`, `divergence`, `next_action`. These are additive sub-fields under `issues[]` in `audit-issues.json`. Schema extension is structurally safe across the 12 known downstream consumers (parent analysis).

**Bridge consumers.** 24 agents load KB-review-disciplines (`execute-orchestrator`, `review-cross-artifact-auditor`, `intake-intent-clarifier`, `test-acceptance-author` added per cycle-1 reconciliation grep verification; per codebase-analysis `blast_radius_new_confirmations[4]` + grep at reconciliation cycle 1 per audit I-AA-003) — bridge propagates broadly with no separate propagation work. FR-1, FR-9, FR-10 reference the bridge by name. R2b consumers (FR-4, FR-5) inherit the populated bridge unchanged.

### Eat-own-dogfood deliverables (this run)

R2a applies its own FR-6 and FR-7 contracts to itself. Two deliverables produced at Plan / Task-Decomposition time:

**1. `working/feature/pipeline-design-time-discipline-r1/agent-roster-impact-matrix.md`** (per ADR-0064).

- **Trigger:** condition 1 (the FR-1/6/7/8/10 implementations modify `.claude/agents/*.md` files) and condition 4 (six new domain concepts each name agents as downstream consumers). Multiple triggers fire; mechanical observation per ADR-0064 Clause 3.
- **Row count:** equal to `ls .claude/agents/*.md | wc -l` at authoring time (currently 37 per codebase-analysis A-4).
- **Five cells per row:** `tools` / `skills` / `model` / `effort` / `prompt body`.
- **Per-cell schema:** `<value> — <positive-evidence-string>` per ADR-0064 Clause 2.
- **Authoring-time budget:** NFR-7 (30 min wall-clock at 100-agent inventory; 37 agents → ~11 min at the linear-extrapolation rate).
- **Exemplar:** `Issues/per-agent-design-evaluation-gap/evidence/agent-roster-impact-matrix.md` (Track-A2 retroactive matrix from `devcontainer-mcp-provisioning-r1`).

**2. Six FR-7 skill-coverage decisions** embedded in `working/feature/pipeline-design-time-discipline-r1/synthesis.md` (per ADR-0065).

Per ADR-0065 Clause 1, the canonical Skill-Coverage Decisions for this run are embedded in `synthesis.md` §Skill-Coverage Decisions (synthesis.md v1.0.1+; back-filled cycle 1 per audit I-AA-004). See that section for the 6-row table; all 6 resolve to type (a) existing-skill (substance-heuristic review). Zero new skills proposed; zero "no skill warranted" rationales. Substance heuristic (D-8 / ADR-0065) passes because each decision cites concrete file paths + positive evidence.

The Blueprint previously embedded an inline 6-row table at this position; the table is removed at reconciliation cycle 1 because ADR-0065 Clause 1 forbids the Blueprint as the embedding location (the canonical artifact is `synthesis.md`). The Blueprint's reference + the bundled deliverable check are the substance review path at `shared-document-reviewer` invocation 3 (Blueprint review).

### Reasoning-configuration audit (FR-8 active framing dogfood)

Per FR-8's active framing of Principle 9, this Blueprint records the reasoning-configuration consideration performed on every modified agent for this run:

| Agent | `model:` | `effort:` | `skills:` | Consideration outcome |
|---|---|---|---|---|
| `review-architecture-auditor` | `opus` (unchanged) | `xhigh` (unchanged) | unchanged | xhigh remains warranted: the new Lens 4 dimension adds cross-document reconciliation reasoning over ADR prescriptions × implementation files. KB-review-disciplines already loaded. |
| `design-claude-code` | `opus` (unchanged) | `high` (unchanged) | unchanged | Matrix authoring is bounded by NFR-7's 30-min budget at 100 agents; effort: high covers it at the current 37-agent inventory (~11 min). |
| `design-composer` | `opus` (unchanged) | `xhigh` (unchanged) | unchanged | Cross-layer integration unchanged in shape; the new FR-7 substance review per ADR-0065 fits within existing reasoning surface. |
| `synth-synthesizer` | unchanged | unchanged | unchanged | New emission of Skill-Coverage Decisions section row is procedural; reasoning surface unchanged. |
| `discovery-codebase-researcher` | unchanged | unchanged | unchanged | New Blocks-X marker emission is procedural; reasoning surface unchanged. |
| `execute-orchestrator` | unchanged | unchanged | unchanged | New parser invocation is procedural; no reasoning surface added. |

Six agents touched; all six retain current reasoning configuration. The consideration is recorded per FR-8 / Principle 9 active framing — the artifact of consideration is THIS TABLE plus the full per-row matrix produced at Plan time per ADR-0064.

### Constraint propagation check

| Constraint | Source | Honored by |
|---|---|---|
| Single-layer (Claude Code only) | PRD Layer Scope | All design decisions; no cross-layer edges introduced. |
| No new sub-agents | PRD §Product Policy; `per-agent-design-evaluation-gap` §6.3 | Six existing agents modified; zero new agents authored. |
| No retroactive register edits | PRD §Constraints | No edits to parent's deferrals register. |
| 4-cycle reconciliation cap | KB-review-disciplines | Eat-own-dogfood deliverables are Plan-stage outputs, not Design-stage; do not consume Design reconciliation cycles. |
| NFR-7 (30 min at 100 agents) | PRD NFR-7 | Matrix authoring discipline scales linearly; 37 agents → ~11 min. |
| NFR-8 (clear failure messages) | PRD NFR-8 | All FR-1/6/9/10 emitters carry `rule`, `target`, `divergence`, `next_action`. |
| NFR-9 (grep-checkable affordance referencing) | PRD NFR-9 | New templates live in KB-documentation-criteria (loaded by design-cc, synth-synthesizer, design-composer); new scripts live under skills these agents reach via Bash. |
| Brief-honor (ADR-0009) | parent rationale brief | Re-cited at Background; every R2a FR maps to a cross-artifact-relationship-verification mechanism. |
| ADR-0005 (append-only supersession) | inherited | FR-8 Principle 9 leading-sentence replacement is in-place edit with Change Log entry, NOT supersession. |
| ADR-0044 (state-transitions log v1 free-string) | inherited | Four new `transition_name` values land without schema evolution. |
| ADR-0045 (review-architecture-auditor has no Agent/Task tool) | inherited | FR-1's new Lens 4 runs inline, not via sub-agent spawn-out. |

All constraints honored.

## Top-level components

| Component | Layer | Responsibility |
|---|---|---|
| **Severity bridge content** | KB-review-disciplines | Five-column translation table + Weight Preservation Note. Cross-cutting glue for FR-1, FR-9, FR-10. |
| **Agent-roster impact matrix template** | KB-documentation-criteria | Canonical shape of `agent-roster-impact-matrix.md` per ADR-0064. |
| **Skill-Coverage Decisions section template** | KB-documentation-criteria | Canonical shape of the embedded synthesis.md section per ADR-0065. |
| **Blocks-X marker parser** | `auditing-shared/scripts/` | Single source-of-truth regex; consumed by orchestrator + future audit rules. |
| **Feature-touch advisory predicate** | `auditing-subagents/scripts/` | FR-6 trigger evaluation (deterministic for 1+2; advisory for 3+4). |
| **SA-14 matrix-missing audit script** | `auditing-subagents/scripts/` | Pre-deliverable packaging-time backstop. |
| **ADR-prescriptions validator** | `auditing-shared/scripts/` | Schema-validates ADR-0059 companion files (FR-1 support). |
| **Active Principle 9** | KB-cc-design | Substantive framing of per-agent consideration discipline. |

## Verification strategy

How this Blueprint's claims are verified:

- **EARS acceptance tests** authored downstream at `acceptance-tests.md` (per the test-acceptance-author stage). One AT per PRD AC (AC-FR-1-a..c, AC-FR-6-a..d, AC-FR-7-a..c, AC-FR-8-a..b, AC-FR-9-a..c, AC-FR-10-a..c, AC-NFR-1-a, AC-NFR-7-a, AC-NFR-8-a, AC-NFR-9-a).
- **Phase validators** authored downstream at `phase-validators.md`. PVs per phase per the Plan's phase decomposition.
- **Eat-own-dogfood validation** — at packaging time, the SA-14 audit fires against this run's own working directory. If R2a's own `agent-roster-impact-matrix.md` is missing or row-count-mismatched, the run fails its own discipline (validation event by design).
- **Inter-document consistency** — `review-cross-artifact-auditor` (post-Plan/post-Tests/post-PVs) verifies Blueprint ↔ Plan ↔ Tests ↔ PVs consistency in diff-mode.

The two-ADR addition (0064, 0065) is verified at `shared-document-reviewer` invocation 4 (ADR review), which uses the canonical ADR template from KB-documentation-criteria.

## Risks and mitigations

Carried from PRD §Risks and Mitigation with R2a-specific augmentation:

| Risk | Severity | Probability | Mitigation |
|---|---|---|---|
| Authoring-burden creep on roster matrix + skill-coverage decisions slows every future agent-surface-touching feature | Medium | Medium | NFR-7's 30-min-at-100-agents budget is the ceiling; if exceeded, cell-granularity is the first dial to relax (per ADR-0064 kill criteria). |
| FR-6 triggers 3/4 produce uneven enforcement across runs | Medium | Medium | Hybrid predicate+human ratification per ADR-0064 Clause 3. Override events logged for tuning. First ~3 runs are the calibration corpus. |
| Eat-own-dogfood reveals an unforeseen FR-6/FR-7 contract weakness on this run | Medium | Low-Medium | This is by design — applying the contract to its own definer is the validation event. In-run revision is acceptable; Blueprint OI captures any contract amendment with rationale. |
| Severity bridge content collides with concurrent R2b edits | Low | Low | SPLIT-RECORD's "R2a-runs-first" ordering recommendation; R2b kickoff gated on this run's deliverable archive. |
| FR-7 substance heuristic for (a)/(c) rows produces inter-reviewer disagreement | Low-Medium | Medium | ADR-0065 kill criteria: >30% inter-reviewer disagreement sustained across N≥3 runs triggers extension of structural mandate to (a) and (c) rows. |
| New advisory predicate has no calibration corpus on day 1 (greenfield) | Low | High | Predicate emits advisory annotation only; human ratifies. First ~3 runs build the corpus per ADR-0064. |
| FR-8 Principle 9 sentence replacement creates a brief documentation seam (active framing applied; older defensive framing may still be cited in stale notes) | Low | Low | ADR-0005 append-only supersession discipline — Principle 9's leading-sentence replacement is in-place edit with Change Log entry. No surface-level reference rot expected. |

## Implementation plan (top-level)

The Plan stage authors detailed phases. Top-level phase decomposition:

- **Phase A — Severity bridge content authoring** (per D-R2a-6 sequencing). Author `KB-review-disciplines/references/severity-taxonomy.md` content per the §Severity bridge content section above. **Sequenced first** because FR-1, FR-9, FR-10 consumers cite the bridge by name; authoring consumers first risks placeholder leakage (the exact failure mode FR-1 catches — would undermine dogfood signal).
- **Phase B — FR-1 design-realization audit dimension.** New phase on `review-architecture-auditor`; Lens 4 added to `architecture-audit.md`; ADR-prescriptions validator script. Consumes bridge content.
- **Phase C — FR-9 Blocks-X marker enforcement.** New parser script at `auditing-shared/scripts/`; orchestrator stage-transition gate; discovery-codebase-researcher emission. Consumes bridge content (for severity emission) and ADR-0063 grammar.
- **Phase D — FR-10 SA-14 audit rule.** New rule entry + new audit script. Consumes bridge content; depends on FR-6 working-directory shape (Phase F output).
- **Phase E — FR-7 + FR-8 (KB content + agent procedure edits).** Principle 9 active reframing; Skill-Coverage Decisions section template; synth-synthesizer + design-composer procedure extensions. ADR-0065 codifies the contract.
- **Phase F — FR-6 mandatory matrix.** Template + design-cc procedure + advisory predicate. ADR-0064 codifies the contract. Triggers depend on Phase E's Skill-Coverage Decisions section (condition 4).
- **Phase G — Eat-own-dogfood deliverables for this run.** Author this run's own matrix + Skill-Coverage Decisions section (per dogfood discipline; six concept rows + 37-agent matrix).

Phase A is sequenced before B/C/D explicitly (D-R2a-6 binding). Phases E and F are dependency-linked (F's trigger 4 reads E's output). Phase G is the final phase before deliverable packaging.

## ADRs authored in this run

Two new ADRs land in this run, both authored by `design-composer` per FR-5 invariant:

| ADR | Title | Closes / Resolves | Summary |
|---|---|---|---|
| **ADR-0064** | Agent-Roster Impact Matrix Contract | FR-6 + D-5 + D-8 (matrix-side) + OI-R2a-1 (mechanical evaluator) | Codifies the four-condition trigger, full-inventory row count, five explicit dimensions, positive-evidence-string cells, advisory predicate + human ratification, override-event logging. |
| **ADR-0065** | Skill-Coverage Decision Discipline (W/H/A Trifecta Hybrid) | FR-7 + D-8 (substance side) + D-R2a-4 (artifact location) | Codifies hybrid W/H/A enforcement (structural mandate for new-skill proposals; substance heuristic for existing-skill / no-skill rows) embedded as section in `synthesis.md`. |

Files: `/workspaces/feature-pipeline/adrs/ADR-0064-agent-roster-impact-matrix-contract.md`, `/workspaces/feature-pipeline/adrs/ADR-0065-skill-coverage-decision-discipline.md`. Canonical project-root placement per ADR-0036; no carve-outs per ADR-0056.

## Inheritance manifest (from parent run)

Three ADRs inherited from `pipeline-cross-artifact-discipline-r1`, cited NOT re-authored. Per PRD §Inheritance Manifest + SPLIT-RECORD.

| ADR | Title | R2a posture |
|---|---|---|
| **ADR-0059** | ADR-prescriptions companion-file pattern | Cited at FR-1. Closes parent OI-A1 / R2a FR-1 prescription-extraction question. R2a does NOT re-author. |
| **ADR-0061** | Severity-vocabulary bridge table HOST | Cited at FR-1, FR-9, FR-10, and §Severity bridge content. Fixes publication target (`KB-review-disciplines/references/severity-taxonomy.md`). R2a authors the content per the host's location. |
| **ADR-0063** | Blocks-X marker grammar | Cited at FR-9. Closes parent OI-A5 / R2a FR-9 grammar question. R2a does NOT re-author the grammar; D-R2a-3 resolves the realization location independently. |

R2a does NOT modify any inherited ADR. Per ADR-0005 (append-only supersession), inherited ADRs remain valid commitments.

Out-of-scope inherited decisions:

| Inherited decision | R2a posture |
|---|---|
| D-2, D-7 (FR-3, FR-5 — R2b-only) | Out of R2a scope. Routed to queued R2b run; no R2a touch. |
| D-9 (FR-11 §O placement — R2b-only) | Out of R2a scope. Routed to queued R2b run; no R2a touch. |
| ADR-0060 (cross-file invariant catalog hybrid — R2b-only) | Inherited as accepted but not referenced by R2a's FRs. |
| ADR-0062 (MCP tool surface drift detection — R2b-only) | Inherited as accepted but not referenced by R2a's FRs. |

See `working/feature/pipeline-cross-artifact-discipline-r1/SPLIT-RECORD.md` for full lineage.

## Open items and Q-CC arbitration

Five Q-CC-N items surfaced by `design-cc` for composer arbitration. Disposition recorded below.

| ID | Item | Composer disposition | Routes to |
|---|---|---|---|
| **Q-CC-1** | D-10 severity bridge publication target — confirm closure-by-inheritance | **Closed by inherited ADR-0061**. Host fixed (`KB-review-disciplines/references/severity-taxonomy.md`). R2a authors the content per the host (see §Severity bridge content). No new ADR. | — (closed) |
| **Q-CC-2** | D-R2a-3 marker-parser realization location ratification | **Ratified.** Place at `.claude/skills/auditing-shared/scripts/parse_blocks_x_markers.py`. Three converging arguments: shared regex across multiple consumers (orchestrator + future audit rules + R2b FR-3 PV-tier invariants); existing canonical-library-home pattern per ADR-0031 + ADR-0042; greenfield placement (C-0073 confirmed zero existing parser). Not ADR-worthy — small implementation-location choice with full rationale in cc-design §FR-9. | plan-author (Plan-stage realization) |
| **Q-CC-3** | D-R2a-4 FR-7 artifact location ratification | **Ratified — codified in ADR-0065 Clause 1.** Embed Skill-Coverage Decisions section in `synthesis.md` (not standalone, not in Blueprint, not in cc-design.md). This decision IS load-bearing (cross-cuts FR-6 predicate, FR-7 review path, future tuning) and warrants the ADR — see ADR-0065 for full rationale. | — (codified in ADR-0065) |
| **Q-CC-4** | D-R2a-5 FR-10 rule realization — new rule entry vs extend existing | **Ratified.** New rule entry `SA-14` per cc-design §FR-10 rationale (three converging codebase facts C-0066, C-0067, C-0078). Not ADR-worthy on its own — the choice is auditing-subagents catalog discipline, not architectural. | plan-author (Plan-stage realization) |
| **Q-CC-5** | D-R2a-6 plan-stage sequencing — bridge first vs consumers first | **Ratified.** Bridge content first (Phase A), then FR-1/9/10 consumers (Phases B/C/D). Recorded in §Implementation plan above. The sequencing prevents R2a's own deliverables from exhibiting the failure mode FR-1 is designed to catch (placeholder citation leakage). Not ADR-worthy — Plan sequencing discipline, not architectural decision. | plan-author (honors sequencing) |

Open items carried forward from PRD §Undetermined Items:

- **OI-R2a-1 (FR-6 mechanical evaluator)** — **Resolved by ADR-0064 Clause 3** (hybrid advisory predicate + human ratification + override-event logging).
- **OI-R2a-2 (`auditing-skills` reverse-check)** — **Carried forward as Blueprint Open Question.** Not folded into FR-10's SA-14 scope (per PRD §Product Policy). Recommended posture: separate parallel rule in `auditing-skills`. Composer disposition: defer the substance choice to a future feature run; this Blueprint records the recommended posture but does not commit to implementation in R2a. **Routed to:** future-feature-run (not in R2a or R2b scope).
- **OI-R2a-3 (FR-9 marker-parser realization location)** — **Resolved by Q-CC-2 disposition above** (shared helper at `auditing-shared/scripts/parse_blocks_x_markers.py`).

No unresolved open items at Blueprint composition close. Five Q-CC-N dispositioned; three OI-R2a-N closed (one explicitly deferred to future feature with recorded posture).

## Cross-references

### Inherited ADRs applied
- ADR-0005 (append-only supersession discipline)
- ADR-0008 (issues-ledger lifecycle)
- ADR-0009 (rationale brief honor)
- ADR-0011 (canonical template embedding)
- ADR-0013 (Blueprint canonical structure)
- ADR-0017 (`shared-document-reviewer` invocation points)
- ADR-0020 (KB consolidation discipline)
- ADR-0030 (pedagogical-section discipline)
- ADR-0031, ADR-0042 (`auditing-shared/scripts/` canonical library home)
- ADR-0036 (canonical ADR placement at `adrs/` project root)
- ADR-0040 (Serena narrowed-allowlist precedent; per-agent-design-evaluation-gap exemplar)
- ADR-0044 (state-transitions log v1 free-string `transition_name`)
- ADR-0045 (`review-architecture-auditor` has no Agent/Task tool)
- ADR-0056 (no carve-outs in canonical-placement rules)
- **ADR-0059 (R2a-inherited)** — companion `.prescriptions.yaml` schema
- **ADR-0061 (R2a-inherited)** — severity-vocabulary bridge table host
- **ADR-0063 (R2a-inherited)** — Blocks-X marker grammar

### New ADRs authored (this run)
- **ADR-0064** — Agent-Roster Impact Matrix Contract
- **ADR-0065** — Skill-Coverage Decision Discipline (W/H/A Trifecta Hybrid)

### Q-CC-N items resolved
- Q-CC-1: closed by ADR-0061 inheritance (no new ADR needed)
- Q-CC-2: ratified — marker parser at `auditing-shared/scripts/parse_blocks_x_markers.py`
- Q-CC-3: ratified and codified in ADR-0065 Clause 1
- Q-CC-4: ratified — new SA-14 rule entry
- Q-CC-5: ratified — bridge first sequencing

### OI items disposition
- OI-R2a-1: resolved by ADR-0064 Clause 3
- OI-R2a-2: explicit deferral to future feature with recommended posture recorded
- OI-R2a-3: resolved by Q-CC-2 disposition

### Closed-by-inheritance decisions
- D-1 (FR-1 prescription extraction): closed by ADR-0059
- D-4 (FR-9 marker grammar): closed by ADR-0063
- D-6 (R2a/R2b split): closed by user at parent Gate 4
- D-10 host: closed by ADR-0061; **content authored in this run** (§Severity bridge content)

### Decisions adopted summary
- **D-1** → ADR-0059 (inherited)
- **D-3** → carried forward as Blueprint OI; recommended posture: separate parallel rule in `auditing-skills`; deferred to future feature
- **D-4** → ADR-0063 (inherited)
- **D-5** → ADR-0064 Clause 3 (hybrid advisory predicate + human ratification + override logging)
- **D-6** → closed by user at parent Gate 4 (R2a/R2b split)
- **D-8** → ADR-0064 (matrix side: positive-evidence-string discipline) + ADR-0065 (skill side: hybrid trifecta)
- **D-10** → ADR-0061 (host inherited) + §Severity bridge content (content authored this run)
- **D-R2a-3** → Q-CC-2 ratified (parser at `auditing-shared/scripts/parse_blocks_x_markers.py`)
- **D-R2a-4** → ADR-0065 Clause 1 (embed in `synthesis.md`)
- **D-R2a-5** → Q-CC-4 ratified (new SA-14 rule entry)
- **D-R2a-6** → Q-CC-5 ratified (bridge content first, then FR-1/9/10 consumers) — Plan-stage honored

---

*End of Blueprint v1.0.0 for `pipeline-design-time-discipline-r1`. Composed by `design-composer` 2026-05-26. Next stages: `shared-document-reviewer` (Gate 0/1 on this Blueprint + Gate 4 on ADR-0064/0065), then `review-architecture-auditor` (architecture audit), then `plan-author` (Plan authoring honoring the §Implementation plan sequencing).*
