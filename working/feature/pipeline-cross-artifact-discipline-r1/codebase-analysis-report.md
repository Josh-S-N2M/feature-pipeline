---
id: CA-pipeline-cross-artifact-discipline-r1
version: 1.0.0
status: draft
doc_type: codebase-analysis
feature_slug: pipeline-cross-artifact-discipline-r1
derived_from:
  - working/feature/pipeline-cross-artifact-discipline-r1/research-plan.md
  - working/feature/pipeline-cross-artifact-discipline-r1/prd-v2.md
sidecar: working/feature/pipeline-cross-artifact-discipline-r1/codebase-analysis.json
generated: 2026-05-26T13:30:00Z
generated_by: discovery-codebase-researcher
extraction_method: mixed
---

# Codebase Analysis Report — Cross-Artifact + Design-Time Discipline (R2)

## Contents

- Executive summary
- Component inventory (20 components across the 11 mechanisms)
- Dependency map (Claude Code in-scope edges)
- Blast-radius summary per touch point (7 PRD-named touch points)
- Conventions observed at the Claude Code layer
- Known issues and recommended caution areas (7 items)
- Mechanism-dependency table (FR-1 .. FR-11 — load-bearing for Contingency Split)
- Watch-item evidence (OI-A1, OI-A2, OI-A4, OI-A5)
- Open questions for human resolution
- Cross-reference: sidecar JSON

---

## Executive summary

Discovery confirms the 11 mechanisms in PRD-v2 each have a stable attachment point in the codebase — every FR can be mechanically placed today. The substrate is documentation-heavy (markdown agent prompts, KB references, python audit scripts, JSON config), so traversal used grep + targeted Read rather than the symbol-graph MCPs (no symbol semantics to exploit on markdown / yaml frontmatter); extraction_method is recorded as `mixed` per ADR-0018 provenance discipline.

Five Discovery findings warrant Synthesis attention:

1. The **cumulative open-item count entering Synthesis is already 14** (IC carries 8 + PRD-v2 adds 6), which **already exceeds the Contingency Split threshold of 12** declared in PRD §Contingency Split §1. The split-recommendation condition has effectively pre-fired before any Blueprint Open Questions are added. design-composer must apply the threshold mechanically at Gate 4.
2. The **Blocks-X marker grammar is effectively absent** (n=1 prior occurrence across all `working/feature/*/codebase-analysis*.md` and `working/feature/*/research-plan*.md`), so FR-9 is **establishing** a canonical grammar rather than reconciling heterogeneity. The precedent grammar is `Blocks <stage-slug>-completion.` (period-terminated, kebab-case).
3. The **PV-author rubric is inlined in `.claude/agents/test-phase-validator-author.md`** (Phase 2), not in `KB-task-decomposition` as Research Plan IN-009 line 134 stated. FR-3 must attach at the agent-prompt level, not the KB. This is a correction Synthesis should propagate.
4. **`Issues/devcontainer-mcp-provisioning-r1-deferrals/register.md` §O.1 names FIVE rows with post-ship triggers** (A-3, D-5, E-2, E-3, I-1), not four as the PRD AC-FR-11-c enumerates (E-3, A-3, D-5, I-1). The fifth row (E-2 "post-ship felt-utility review") has the same anti-pattern shape; design-composer should decide whether AC-FR-11-c covers E-2 too.
5. **Discipline-text grep for "post-ship" trigger language in `.claude/skills/` and `.claude/agents/` returned ZERO occurrences** — meaning FR-11's posture is purely additive prescription. There is no pre-existing prose to negate. This makes FR-11 structurally simpler than the PRD framing suggests.

Additional facts: the **agent inventory is 37, not 36** (PRD Background reflects a stale snapshot); the **agent-roster-impact-matrix.md exemplar is now at `Issues/per-agent-design-evaluation-gap/evidence/`** (migrated by `issue-capture-mechanism-r1` FR-9); **six MCP servers** active in `.mcp.json` (post-2026-05-24 `mcp-openapi-schema` removal — though `audit_op2_consumer_mapping.py` still references the removed server, exactly the design-realization gap FR-1 closes).

---

## Component inventory

Twenty components captured. Full structured data is in the sidecar JSON under `components[]`. Tabular summary:

| Component | Path | Role for the feature |
|---|---|---|
| `review-architecture-auditor` | `.claude/agents/review-architecture-auditor.md` | FR-1 attachment — new audit dimension |
| `KB-review-disciplines` | `.claude/skills/KB-review-disciplines/` | FR-1 lens extension (architecture-audit.md) |
| `auditing-shared` | `.claude/skills/auditing-shared/` | Severity vocabulary + shared scripts (audit-issues.json schema is in agent prompts, not here) |
| `discovery-codebase-researcher` | `.claude/agents/discovery-codebase-researcher.md` | FR-2 §Protocol Conformance attachment |
| `KB-codebase-research` | `.claude/skills/KB-codebase-research/` | FR-2 schema extension (codebase-analysis.json v1.1.0) |
| `recipe-feature-pipeline` | `.claude/skills/recipe-feature-pipeline/SKILL.md` | FR-6 + FR-9 gate attachment (13-stage state machine, 5 reviewer invocation points) |
| `design-cc` | `.claude/agents/design-claude-code.md` | FR-6 mandatory artifact attachment |
| `KB-cc-design` | `.claude/skills/KB-cc-design/` | FR-8 Principle 9 rewording target |
| `auditing-subagents` | `.claude/skills/auditing-subagents/` | FR-10 rule attachment |
| `auditing-mcp` | `.claude/skills/auditing-mcp/` | FR-4 rename + FR-5 drift |
| `auditing-cc-configs` | `.claude/skills/auditing-cc-configs/` | FR-4 flag forwarding coordination |
| `.mcp.json` | `.mcp.json` | FR-4 + FR-5 baseline (6 servers) |
| `Issues/devcontainer-mcp-provisioning-r1-deferrals/register.md` | (same) | FR-11 §O posture canonical source + AC-FR-11-c verbatim anchor |
| `Issues/cross-artifact-divergence-detection-gap/` | (same) | Source for H1, H3, H6, H8, H9 |
| `Issues/per-agent-design-evaluation-gap/` | (same) | Source for B1..B5; hosts agent-roster-impact-matrix.md exemplar |
| `state-transitions-log-entry-template` | `.claude/skills/KB-documentation-criteria/references/templates/state-transitions-log-entry-template.md` | FR-9 transition_name extension target |
| `test-phase-validator-author` | `.claude/agents/test-phase-validator-author.md` | FR-3 cross-file invariant attachment (the actual "PV-author" agent) |
| `KB-task-decomposition` | `.claude/skills/KB-task-decomposition/` | NOT the PV-author rubric home (correction noted) |
| `agent-inventory` | `.claude/agents/*.md` (37 files) | FR-6 row count baseline (37 at HEAD; moving target by design) |
| `ADR-locus` | `adrs/` | FR-1 prescription locus (per ADR-0036/0054/0056; no companion-file precedent exists) |

### Six MCP servers in `.mcp.json` (FR-4 / FR-5 baseline)

| Server | Transport | Command |
|---|---|---|
| `actionlint-mcp` | stdio | `actionlint-mcp` |
| `context7` | http | n/a (remote URL) |
| `exa` | http | n/a (remote URL) |
| `gitnexus` | stdio | `npx` |
| `serena` | stdio | `serena` |
| `terraform-mcp` | stdio | `terraform-mcp` |

The seventh historical server (`mcp-openapi-schema`) was removed 2026-05-24 per `.devcontainer/versions.env` lines 17-18. The removal is documented in `KB-mcp-platform/SKILL.md` (lines 16, 33, 61). **`audit_op2_consumer_mapping.py` lines 11 + 36 still reference `mcp__mcp-openapi-schema__*`** as a tool surface for `design-api` — stale and would be caught by FR-1's design-realization audit if it ran today.

### 37 agents in `.claude/agents/`

Full list captured in the sidecar JSON (`components[].notes` for the `agent-inventory` entry). FR-6 AC-FR-6-b binds the matrix row count to the authoring-time `.claude/agents/*.md` count — the discrepancy between PRD Background's "36" and the current "37" is documentary drift, not a structural defect (the matrix is bound to current count by design).

---

## Dependency map (Claude Code edges)

Twenty edges captured in `dependencies[]`. The load-bearing ones for this feature:

**audit-issues.json consumer chain.** `review-architecture-auditor` writes `architecture-audit-issues.json`. `finalize-reconciler` consumes it on `fail` / `conditional_pass` verdicts. `finalize-deliverable-packager` consumes it as archived state. The schema (lines 120-155 of the agent prompt) is `{schema_version, audit_id, audited_artifact, audited_at, code_graph_used, checks_performed[], issues[{id, severity, category, summary, evidence[], recommended_resolution}], summary{}, verdict}`. FR-1 adds `design_realization` to `checks_performed[]` and `issue.category` (additive). NFR-8 adds `rule / target / divergence / next_action` sub-fields under `issues[]` (also additive).

**`codebase-analysis.json` consumer chain.** Twelve agents read it directly: `review-architecture-auditor`, `design-composer`, `design-cc`, eight per-layer design-* agents, `plan-author`, `test-acceptance-author`, `finalize-task-decomposer`. None index into a fixed-shape `protocol_conformance[]` today, so FR-2's §Protocol Conformance subsection is structurally safe to add.

**`--with-runtime` flag.** Fourteen first-class call sites enumerated (see Blast Radius below). The flag is parsed at `audit_mcp.py:36` but ONLY forwarded to `check_toxic_combinations.py` (lines 56-58 of `audit_mcp.py`). Per the MCP-postmortem evidence (DEF-08), this is the misnaming FR-4 corrects.

**`shared-document-reviewer` invocations.** Five points per ADR-0017: after Intent Clarification, after PRD, after each per-layer Design, after Design Composition, after Plan. FR-6's mandatory matrix attaches at invocation 4 (Design Composition). FR-9's Blocks-X gate attaches at every inter-stage checkpoint, not at the reviewer.

---

## Blast-radius summary per touch point

Per ADR-0018, blast radius with `hop_tier_distribution`. Seven touch points from PRD §Blast-radius questions and Research Plan §Blast-radius questions:

| # | Touch point | 1-hop | 2-hop | 3-hop | hop_tier_distribution |
|---|---|---|---|---|---|
| 1 | `review-architecture-auditor` | 2 | 2 | 1 | `{"1": 2, "2": 2, "3": 1}` |
| 2 | `auditing-mcp --with-runtime` | 14 | 3 | 0 | `{"1": 14, "2": 3, "3": 0}` |
| 3 | `codebase-analysis.json` schema | 12 | 3 | 0 | `{"1": 12, "2": 3, "3": 0}` |
| 4 | `design-cc` deliverable set | 2 | 2 | 0 | `{"1": 2, "2": 2, "3": 0}` |
| 5 | KB-cc-design Principle 9 | 2 | 0 | 0 | `{"1": 2, "2": 0, "3": 0}` |
| 6 | PV-author rubric (Phase 2 of `test-phase-validator-author`) | 2 | 2 | 0 | `{"1": 2, "2": 2, "3": 0}` |
| 7 | `state-transitions.log` schema | 2 | 2 | 0 | `{"1": 2, "2": 2, "3": 0}` |

The concentration is at touch point 2 (the `--with-runtime` flag — 14 1-hop call sites including agent prompts, audit scripts, KB references, and runbooks). FR-4-d's "fail loudly on legacy flag" must cover all 14 — full enumeration captured under `blast_radius[1].direct_dependents` in the sidecar JSON.

The KB-cc-design Principle 9 touch point is the most concentrated: only 2 sites total (the principles.md TOC entry at line 15 + the verbatim citation in `design-claude-code.md:56`). FR-8 has a tiny blast radius.

### Schema-assumption check (per PRD blast-radius question)

- **`audit-issues.json`**: schema is `{id, severity, category, summary, evidence[], recommended_resolution}`. FR-1 / FR-4 / FR-5 / FR-9 / FR-10's new finding types are additive (new severity values or new category values). NFR-8's `rule / target / divergence / next_action` fields are NEW — must be added as sub-fields under `issues[]`. Backward-compatible.
- **`codebase-analysis.json` v1.1.0**: schema is `{schema_version, scope, components[], dependencies[], blast_radius[], conventions{}, known_issues[], open_questions_for_human[]}`. FR-2's §Protocol Conformance subsection is either a new key under `conventions{}` or a new top-level array `protocol_conformance[]`. Either path is additive; no breaking change for the 12 downstream consumers.
- **`design-cc` deliverable set**: today `cc-design.md + cc-dependencies.json`. FR-6 adds `agent-roster-impact-matrix.md` (conditional on trigger). `design-composer` fan-in input list must accept the third file. `recipe-feature-pipeline` outputs table needs a row.
- **`state-transitions.log`**: `transition_name` field is a free-form string with conventional T0..T13 + `-prime` suffix vocabulary. FR-9's Blocks-X transitions (`BLOCKS_X_RESOLVED` / `BLOCKS_X_DEFERRED` / `BLOCKS_X_FALSEPOSITIVE`) fit the existing schema without evolution.

---

## Conventions observed at the Claude Code layer

Full text in `conventions.cc.*` of the sidecar JSON. Highlights:

### Agent file frontmatter conventions

Required: `name`, `description`, `model`, `tools`, optional `effort`, `skills`, `memory`, `user-invocable`. All 37 agents use `model: opus`. Effort distribution: 5 agents at `xhigh` (per KB-cc-design Principle 9 worked example: `design-composer`, `review-architecture-auditor`, `review-cross-artifact-auditor`, `synth-synthesizer`, `finalize-task-decomposer`); remainder at `high`. Filename convention: kebab-case with stage prefix (`intake-*` / `discovery-*` / `synth-*` / `design-*` / `review-*` / `execute-*` / `finalize-*` / `test-*` / `issue-*` / `cc-*` / `shared-*` / `plan-*`).

### Skill file conventions

`SKILL.md` at `.claude/skills/<name>/SKILL.md`. Required frontmatter: `name`, `description`, `allowed-tools`. Optional: `family` (per ADR-0042 graduated families), `pedagogical_sections` (per ADR-0030 with path + justification), `user-invocable`. Subdirectory pattern: `references/` (discipline texts), `scripts/` (runnable), `assets/` (templates), `examples/` (positive + negative fixtures). KB-* are knowledge-bases; auditing-* are runnable audits; recipe-* are orchestrators.

### KB cross-reference conventions

Principles cross-reference each other by "Principle N" (numbered), with the TOC listing all principles at the top of `references/principles.md`. The `skills:` array in agent frontmatter resolves to existing `SKILL.md` files (the SA-13 audit-subagents check enforces this). Discipline texts cite ADRs inline as `ADR-NNNN` or via "per ADR-NNNN" parentheticals.

### `audit-issues.json` finding shape (two divergent conventions)

The codebase has **two distinct finding-shape conventions**:

1. **Auditor-style** (used by `review-architecture-auditor`, `review-cross-artifact-auditor`): `{id, severity, category, summary, evidence[], recommended_resolution}` with severity in `{BLOCKER, MAJOR, MINOR, INFO}`. Schema lives in agent prompts (not in `auditing-shared`).
2. **Reviewer-style** (used by `shared-document-reviewer` + documented in `KB-review-disciplines/references/severity-taxonomy.md`): same shape but severity in `{critical, important, recommended}` + category in `{consistency, completeness, compliance, clarity, feasibility}` (a separate dimension).

NFR-8's prescribed `rule / target / divergence / next_action` fields are NOT in either current schema. They are additive.

### Severity-string conventions (three surfaces, three vocabularies)

| Surface | Vocabulary |
|---|---|
| Auditor agents (architecture, cross-artifact) | `BLOCKER / MAJOR / MINOR / INFO` |
| `auditing-mcp` SKILL.md "Severity meanings (v2)" | `BLOCKER / MAJOR / MINOR / NIT` (slight divergence — NIT not INFO) |
| `shared-document-reviewer` + KB-review-disciplines | `critical / important / recommended` |
| `test-phase-validator-author` Phase 2 | `blocking / warning / informational` |

`auditing-cc-configs/scripts/verdict_compute.py` bridges the auditor vocabulary into point deductions (`BLOCKER -12, MAJOR -5, MINOR -2, NIT -0.5, INFO 0`). PRD AC text for FR-1/4/5/9/10 uses the **auditor vocabulary explicitly** (BLOCKER / MAJOR). FR-3 interacts with the PV vocabulary (`blocking / warning / informational`).

### Blocks-X marker grammar (OI-A5)

**Effectively absent.** Grep over `working/feature/*/codebase-analysis*.md` + `working/feature/*/research-plan*.md` found exactly ONE prior occurrence — `working/feature/devcontainer-mcp-provisioning-r1/codebase-analysis-report.md` lines 198-202. Grammar: `Blocks <stage-slug>-completion.` (period-terminated; kebab-case stage suffixed with `-completion`). State-transition logs, agent prompts, and skill bodies contain zero such markers. **FR-9 is therefore establishing the canonical grammar**, not reconciling heterogeneity. The Research Plan's A-5 framing "if heterogeneous, Design proposes the grammar" applies — the grammar is functionally absent.

---

## Known issues and recommended caution areas

Seven items, full details in `known_issues[]` of the sidecar JSON.

| # | Severity | Issue |
|---|---|---|
| 1 | medium | `audit_op2_consumer_mapping.py` lines 11+36 still reference `mcp__mcp-openapi-schema__*` for design-api after the 2026-05-24 server removal — stale design-realization. **This is the canonical FR-1 example.** |
| 2 | medium | Severity-vocabulary divergence across audit surface (3 vocabularies — auditor / reviewer / phase-validator). design-composer must reconcile. |
| 3 | low | PV-author rubric is in `.claude/agents/test-phase-validator-author.md` Phase 2, NOT in `KB-task-decomposition` as Research Plan IN-009 claimed. FR-3 attaches at the agent level. |
| 4 | low | Register §O.1 names FIVE post-ship rows; PRD AC-FR-11-c enumerates four. The fifth row (E-2) may need same treatment. |
| 5 | low | Research Plan line 275 references `working/feature/devcontainer-mcp-provisioning-r1/agent-roster-impact-matrix.md` — file was migrated to `Issues/per-agent-design-evaluation-gap/evidence/agent-roster-impact-matrix.md`. |
| 6 | low | PRD Background says "8 of 36 agents" — agent count at HEAD is 37 (documentary drift; AC-FR-6-b is bound to authoring-time count by design). |
| 7 | info | Discipline texts in `.claude/skills/` and `.claude/agents/` contain ZERO occurrences of "post-ship" / "N days post-ship" — FR-11 is purely additive prescription. |

---

## Mechanism-dependency table (FR-1 .. FR-11)

Per the orchestrator prompt's special discipline for this run, this is the load-bearing table `design-composer` reads to apply the Contingency Split. Full structured data is in `mechanism_dependency_table[]` of the sidecar JSON. Compact view:

| FR | Mech | Name | Shared OI | Cluster (shared touch points / gate) | R2a/R2b claim |
|---|---|---|---|---|---|
| FR-1 | H3 | Design-realization audit dimension | OI-A1 | FR-4, FR-5 (architecture-audit-issues.json schema), FR-9 (Blocks-X markers in findings) | R2a (cross-cutting — relocatable per PRD) |
| FR-2 | H6 | §Protocol Conformance subsection | — | FR-9 (Discovery output is Blocks-X emission site) | R2b |
| FR-3 | H9 | PV-tier cross-file invariants | OI-A2 | FR-2, FR-9 (invariant assertions) | R2b |
| FR-4 | H1 | `--with-mcp-reachability` rename + handshake | — | FR-5 (shared handshake), FR-1 (design-realization audit may verify .mcp.json) | R2b |
| FR-5 | H8 | Tool-surface drift detection | — | FR-4 (shares handshake) | R2b |
| FR-6 | B1 | Agent-roster-impact-matrix mandatory | OI-A6 | FR-7 (trigger 4), FR-8 (mutual cross-ref), FR-10 (backstop) | R2a |
| FR-7 | B3 | Skill-coverage decisions | OI-A6 | FR-6, FR-8 | R2a |
| FR-8 | B2 | KB-cc-design Principle 9 active rewording | — | FR-6 (mutual cross-ref per AC-FR-8-b), FR-7 | R2a |
| FR-9 | B4 | Blocks-X markers as stage-transition gates | OI-A5 | FR-1, FR-2 | R2a |
| FR-10 | B5 | auditing-subagents feature-touch-coverage rule | OI-A3 | FR-6 (backstop) | R2a |
| FR-11 | §O | Replace post-ship with event/honest/concrete framings | — | FR-3 (PV inherits framings) | R2b |

### Cluster reading

- **R2a cluster (design-time):** FR-6, FR-7, FR-8, FR-9, FR-10 share dense edges (FR-6 ↔ FR-7 via trigger 4; FR-6 ↔ FR-8 via mutual cross-reference per AC-FR-8-b; FR-6 ↔ FR-10 via backstop). FR-1 sits adjacent; the PRD already flags it as cross-cutting.
- **R2b cluster (gate/validator):** FR-4 + FR-5 are tightly coupled (shared handshake, same auditing-mcp file). FR-2, FR-3, FR-11 sit looser; FR-3 ↔ FR-11 via PV-author inherits deferral framings; FR-2 ↔ FR-9 via Discovery output is Blocks-X emission site.
- **Cross-cluster bridges:** FR-1 (in R2a) ↔ FR-4 + FR-5 (in R2b) via architecture-audit-issues.json schema additions. FR-9 (in R2a) ↔ FR-2 (in R2b) via Discovery-output marker emission. If split, design-composer must coordinate the schema deltas and marker grammar across both halves.

### OI-cluster reading

- **OI-A1** (machine-checkable companion vs NLP): blocks FR-1 only.
- **OI-A2** (denormalized vs centralized invariants): blocks FR-3 only.
- **OI-A3** (auditing-skills reverse-check): blocks FR-10 only (carried as Blueprint Open Question per PRD policy).
- **OI-A4** (4-cycle reconciliation cap): already at 14 cumulative going into Synthesis (see watch-item evidence below).
- **OI-A5** (Blocks-X grammar): blocks FR-9 only; grammar effectively absent — establishing rather than reconciling.
- **OI-A6** (mechanical evaluator for FR-6 triggers 3+4): blocks FR-6 + FR-7 jointly.

---

## Watch-item evidence

Per the orchestrator prompt, four PRD-resolved-but-Discovery-evidence-needed items.

### OI-A1 — companion-file convention precedent

**NO existing precedent.** The `adrs/` directory contains 56+ `ADR-*.md` files at HEAD and **zero** `*.yaml`, `*.json`, or `*.toml` siblings. Any FR-1 resolution choosing the companion-file path establishes a new convention. The NLP-parse path operates on existing ADR prose (single canonical location per ADR-0036, no carve-outs per ADR-0056).

### OI-A2 — existing cross-file PV checks

**NO existing cross-file checks at PV-author tier.** `test-phase-validator-author.md` Phase 2 specifies per-criterion Pass criteria (each criterion individually checked). The closest precedent is `review-cross-artifact-auditor.md` (cross-artifact at audit time, not PV time). Prior `working/feature/*/phase-validators.md` outputs show per-criterion structure without cross-file invariant sections.

### OI-A4 — OI count topology across recent runs (the 4-cycle cap signal)

**Already over the threshold of 12 going into Synthesis.** Survey across all `working/feature/*/prd-v*.md` PRDs at HEAD:

| Run | PRD version | OI checkboxes |
|---|---|---|
| adr-placement-mechanism-repair-r1 | v1 | 4 |
| audit-findings-remediation-r1 | v1 | 0 |
| audit-machinery-fixes-r1 | v1 | 0 |
| devcontainer-mcp-provisioning-r1 | v1, v2, v3 | 0 |
| execute-orchestrator-dispatch-mechanism-repair-r1 | v1 | 0 |
| execution-pipeline-design-r1 | v1, v1.1.0 | 0 |
| frontend-design-knowledge-r1 | v1 | 0 |
| issue-capture-mechanism-r1 | v1, v2 | 0 |
| pipeline-cross-artifact-discipline-r1 | v1, **v2** | 5, **6** |
| pipeline-quickwins-hardening-r1 | v1 | 0 |
| pipeline-skill-design-fixes-r1 | v1 | 0 |

Most recent runs declare zero OI checkboxes at PRD time (they accumulate downstream). The CURRENT run (`pipeline-cross-artifact-discipline-r1` PRD-v2) declares 6 OI-A* items at PRD time.

**Cumulative count entering Synthesis:**
- IC carries: **8 OIs** (OI-1 .. OI-8).
- PRD-v2 adds: **6 OIs** (OI-A1 .. OI-A6).
- **Total: 14 cumulative OIs** before any Blueprint-stage Open Questions are added.

The PRD's Contingency Split threshold §1 ("cumulative count of open items exceeds 12 at any point during synthesis or design composition") is **already met at the Synthesis dispatch threshold**. The PRD's calibration text (line 472) reads: "the threshold of 12 is calibrated as follows: the 4-cycle reconciliation cap, empirically across recent feature runs, terminates around 12–15 active open items; choosing 12 gives a margin and surfaces the question before the cap is hit."

Discovery surfaces this as a **first-class signal for design-composer** to apply Contingency Split mechanically at Gate 4. The PRD anticipates exactly this — the split-recommendation is the contingency, not a failure mode.

### OI-A5 — Blocks-X grammar survey

**Effectively absent.** Grep across all `working/feature/*/codebase-analysis*.md` and `working/feature/*/research-plan*.md` returned exactly ONE prior occurrence:

- `working/feature/devcontainer-mcp-provisioning-r1/codebase-analysis-report.md` lines 198-202: `Blocks design-composition-completion.` / `Blocks design-cc-completion.` (period-terminated, kebab-case stage slug suffixed with `-completion`).

State-transition logs, agent prompts, skill bodies: **zero matches.** A-5's "if heterogeneous, Design proposes the grammar" applies; FR-9 establishes the canonical grammar from this single precedent. Recommendation for Synthesis: adopt `Blocks <stage-slug>-completion.` (period-terminated) as the canonical grammar.

---

## Open questions for human resolution

Four items surface at the Discovery Research close. Full data in `open_questions_for_human[]` of the sidecar.

1. **AC-FR-11-c row enumeration.** The register's §O.1 names FIVE rows (A-3, D-5, E-2, E-3, I-1); the PRD's AC-FR-11-c names four (E-3, A-3, D-5, I-1). Should E-2 ("post-ship felt-utility review") be added to AC-FR-11-c's verbatim-preservation requirement? Blocks: design-composition-completion.
2. **OI-A1 path with no codebase precedent.** No `*.yaml` siblings to ADR-*.md exist in `adrs/`. Choosing the companion-file resolution creates a new convention; choosing NLP-parse operates on the stable prose surface. Discovery does not pre-decide. Blocks: design-composition-completion.
3. **FR-9 grammar choice.** Adopt the precedent `Blocks <stage-slug>-completion.` from the single prior occurrence, or invent a new canonical grammar? Discovery recommends the precedent. Blocks: design-cc-completion.
4. **FR-1 scope on stale-doc drift.** `audit_op2_consumer_mapping.py` references the removed `mcp-openapi-schema` server. If FR-1's mechanism scans argv strings only, it misses this; if it covers any structured server references, it catches it. The OI-A1 resolution likely determines coverage. Blocks: design-composition-completion.

Note on the Research Plan's open question 3 (dogfooding FR-2 §Protocol Conformance in this output): NOT dogfooded. The §Protocol Conformance contract is not yet shipped; this Discovery run produces the canonical v1.1.0 schema only. Dogfooding would require defining the subsection's shape, which is exactly what FR-2 ships.

---

## Cross-reference: sidecar JSON

This Markdown report is the human-readable summary. The structured data — components[], dependencies[], blast_radius[] (with `hop_tier_distribution`), conventions{}, known_issues[], open_questions_for_human[], **mechanism_dependency_table[]** (the load-bearing Contingency Split input), and **watch_item_evidence{}** (OI-A1, OI-A2, OI-A4, OI-A5) — lives in:

`working/feature/pipeline-cross-artifact-discipline-r1/codebase-analysis.json`

Schema version 1.1.0 per ADR-0018 + ADR-0038. Extraction method: `mixed` (grep + Read on markdown/json/python substrate; MCP symbol-graph tools available but not exercised this run — appropriate for documentation-heavy touch points).

*End of codebase analysis report.*
