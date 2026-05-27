---
id: CC-DESIGN-pipeline-cross-artifact-discipline-r1
version: 1.0.0
status: draft
doc_type: per-layer-design
feature_slug: pipeline-cross-artifact-discipline-r1
layer: claude-code
derived_from:
  - working/feature/pipeline-cross-artifact-discipline-r1/prd-v2.md
  - working/feature/pipeline-cross-artifact-discipline-r1/synthesis.md
  - working/feature/pipeline-cross-artifact-discipline-r1/codebase-analysis.json
  - working/feature/pipeline-cross-artifact-discipline-r1/codebase-analysis-report.md
generated: 2026-05-26T15:10:00Z
generated_by: design-cc
---

# Claude Code Design — Cross-Artifact + Design-Time Discipline (R2)

## Brief-honor citation

The user's verbatim thesis from the rationale brief, which every architectural decision in this design must honor:

> "the pipeline must verify relationships across artifacts, not just per-artifact correctness — cancels the structural defect-class behind r1's shipment and the recurrence risk every agent-surface feature inherits."

This design ships 11 mechanisms inside the `.claude/` configuration that lift that thesis from aspirational to structural. The Claude Code layer is the sole activated layer for this feature run; all 11 FRs land here.

## KBs loaded for this design pass

| KB / discipline | Why loaded |
|---|---|
| `KB-cc-platform` | Platform half — primitive syntax, frontmatter contracts, current-detail lookup chain. Anchors the FR-by-FR file-targeting below. |
| `KB-cc-design` | Design half — the decision discipline (lowest-cost primitive, path-gating, enforce-vs-instruct, intentional sub-agent reasoning config). Anchors every "design choice" rationale. FR-8 modifies Principle 9 in this KB; FR-6 cross-references it. |
| `KB-documentation-criteria` | Template + structural conventions. FR-9 marker grammar lands in its references/ subdir; FR-11 deferral-framing conventions land in its `disciplines/` subdir. |
| `KB-review-disciplines` | FR-1 attaches a new audit dimension on `review-architecture-auditor` whose discipline lives in this KB's `architecture-audit.md`. D-10 bridge table also lands here. |
| `KB-task-decomposition` | D-2 hybrid catalog body for FR-3 cross-file invariants. Per codebase-analysis Known Issue 3, the PV-author rubric itself is inlined in `test-phase-validator-author.md`, NOT in KB-task-decomposition — the catalog file goes here but the rubric prompt edits go in the agent body. |
| `KB-mcp-design` + `KB-mcp-platform` | FR-4 (rename + handshake), FR-5 (drift detection) live in `auditing-mcp`. These KBs anchor the OP-rule catalog and platform facts that FR-4/5 lean on. |

## Per-FR design

Each FR section below names: (a) target file(s); (b) surface-level shape of the change; (c) decision(s) from synthesis it depends on; (d) OI(s) it depends on; (e) mechanism-dependency-table reference per codebase-analysis. design-cc authors design, not implementation — concrete edits are produced at Plan time.

### FR-1 — Design-realization audit dimension on `review-architecture-auditor`

**Mechanism code:** H3. **Decisions adopted:** D-1 (companion file) + D-10 (severity bridge table). **OI dependencies:** OI-A1 (closed by D-1 = companion file). **Mechanism-dependency table:** R2a; cross-cutting candidate per PRD §Contingency Split.

- **Target files (per codebase-analysis mechanism_dependency_table[FR-1] + watch_item_evidence):**
  - `.claude/agents/review-architecture-auditor.md` — add the new audit phase **inline** (the agent has no Agent/Task tool per ADR-0045; the new dimension fits as a new procedure phase, additive to today's 6-phase procedure).
  - `.claude/skills/KB-review-disciplines/references/architecture-audit.md` — add **Lens 4: Design Realization** alongside the existing three lenses (CoVe, Blast-Radius, Brief-Honor).
  - `.claude/skills/KB-review-disciplines/references/severity-taxonomy.md` — add the D-10 bridge table (see §Severity bridge table).
  - `adrs/*.prescriptions.yaml` — new companion file pattern (sibling to each `ADR-NNNN-<slug>.md`). Companion-file schema below.
  - `.claude/skills/auditing-shared/scripts/` — new helper `validate_adr_prescriptions.py` lints companion-file schema and surfaces a Gate-0-style structural error if the companion diverges from the ADR's own machine-checkable sections (the D-1 staleness mitigation in synthesis §D-1).
- **Surface shape:** The auditor reads the companion files at audit time; for each entry in each companion file, the auditor opens the eventual `target_path` and applies the declared `assertion` (e.g., grep / equals / regex / substring). Mismatches emit `BLOCKER` findings with the NFR-8 four-field structure (`rule`, `target`, `divergence`, `next_action`). Per AC-FR-1-b, when no companion files exist or contain zero predicates, the auditor records a `no-op` diagnostic and proceeds.
- **Lowest-cost primitive justification (KB-cc-design Principle 1):** New audit dimension is a procedure-phase edit on an existing agent + new content in an existing KB + new companion-file convention. No new sub-agent (per PRD Won't-Have). No new hook. No new MCP. Companion file is a structured-data file read by the auditor, not a Claude Code primitive — minimum-surface change.
- **Reasoning configuration justification (KB-cc-design Principle 9, post-FR-8 wording):** `review-architecture-auditor` keeps `model: opus`, `effort: xhigh`, `memory: project`. Considered: stays at xhigh because the new design-realization audit dimension adds cross-document reconciliation reasoning over ADR prescriptions × implementation files; effort: xhigh remains warranted. `skills:` list adds nothing new (KB-review-disciplines already loaded).

### FR-2 — §Protocol Conformance subsection in `discovery-codebase-researcher` output

**Mechanism code:** H6. **Decisions adopted:** D-4 (HTML-comment pragma consumed by §Protocol Conformance schema). **OI dependencies:** none directly; couples to FR-9 via marker grammar. **Mechanism-dependency table:** R2b.

- **Target files:**
  - `.claude/agents/discovery-codebase-researcher.md` — add a new procedure step inside the existing 6-phase procedure (after Phase 5 Conventions). Required when codebase-analysis enumerates ≥1 external interface in scope; emit `§Protocol Conformance — N/A (no external interfaces in scope)` otherwise, per AC-FR-2-b.
  - `.claude/skills/KB-codebase-research/SKILL.md` — extend the canonical `codebase-analysis.json` schema additively (per ADR-0018 + ADR-0038, additive extensions preserve compat). New top-level array: `protocol_conformance[]` with shape `{interface_name, transport, contract_dimensions[], evidence_refs[], blocks_markers[]}`. The `blocks_markers[]` field carries D-4 structured pragmas verbatim so FR-9 can parse them.
  - `.claude/skills/KB-documentation-criteria/references/templates/` — new subsection template `protocol-conformance-subsection-template.md` referenced from KB-codebase-research SKILL.md (NFR-9 grep-checkability).
- **Surface shape:** Per-interface subsection enumerating: (i) interface name + transport (stdio / HTTP / SSE / CLI / library SDK); (ii) the protocol/contract dimensions the feature relies on (auth, request shape, response shape, error semantics, idempotency, rate-limiting, version pinning); (iii) discovery-time evidence anchor for each dimension; (iv) any unresolved questions emitted as `<!-- BLOCKS: <stage>-completion -->` pragmas (D-4).
- **Lowest-cost primitive justification:** Additive procedure phase + additive schema extension. The 12 downstream consumers of `codebase-analysis.json` (per blast-radius §3) all index into existing array/object members; a new top-level array adds zero breakage.
- **Reasoning configuration justification:** `discovery-codebase-researcher` stays at `model: opus`, `effort: high`. No effort change — protocol-conformance enumeration is bounded per-interface; the existing high effort covers it. `skills:` list unchanged.

### FR-3 — PV-tier cross-file consistency invariant catalog

**Mechanism code:** H9. **Decisions adopted:** D-2 (hybrid: denormalized declaration + centralized body) + D-10 (severity vocabulary for PV findings is `blocking / warning / informational` per AC-FR-3-c). **OI dependencies:** OI-A2 (closed by D-2). **Mechanism-dependency table:** R2b.

- **Target files:**
  - `.claude/agents/test-phase-validator-author.md` — extend Phase 2 (the inlined PV-author rubric per codebase-analysis Known Issue 3) with a new required section heading **"Cross-File Invariants"**. Authors enumerate each `CFI-NNN` invariant the phase honors (denormalized declaration); single-deliverable phases record `N/A — single-deliverable phase` per AC-FR-3-b.
  - `.claude/skills/KB-task-decomposition/cross-file-invariants.md` — new catalog file (centralized body per D-2). Each `CFI-NNN` entry has `{id, predicate_logic, error_message_template, severity, applicable_phases[]}`. Hosted in KB-task-decomposition per synthesis §D-2 constraint propagation; consumed by reference from the agent body.
  - `.claude/skills/KB-review-disciplines/references/architecture-audit.md` — cross-reference to the catalog under the cross-artifact lens.
- **Surface shape:** PV declares "Phase 2 honors CFI-003 and CFI-007"; catalog hosts the predicate body and severity. Per AC-FR-3-c, the cross-file finding's severity is the maximum of its component per-file assertions — the catalog records the floor, the assertion machinery enforces the no-downgrade rule.
- **Lowest-cost primitive justification:** Denormalized declaration in the existing agent body (no new agent) + a new catalog file co-located with the KB the consuming agent already loads (`KB-review-disciplines`, which `test-phase-validator-author` already loads — see codebase-analysis dependencies §test-phase-validator-author). NFR-9 grep-check passes: catalog reachable via `KB-review-disciplines` SKILL.md cross-reference + `KB-task-decomposition` if PV authors also load it.
- **Reasoning configuration justification:** `test-phase-validator-author` stays at `model: opus`, `effort: high`. Cross-file invariant authoring is bounded; current effort sufficient.

### FR-4 — Rename `--with-runtime` to `--with-mcp-reachability` + live handshake

**Mechanism code:** H1. **Decisions adopted:** none (no open sub-decisions per synthesis). **OI dependencies:** none. **Mechanism-dependency table:** R2b; bundled with FR-5.

- **Target files (per codebase-analysis blast_radius[2] — 14 first-class call sites):**
  - `.claude/skills/auditing-mcp/scripts/audit_mcp.py` (line ~36) — rename flag; add a new reachability dispatch (handshake stage; new sub-script `check_mcp_reachability.py` under `scripts/`).
  - `.claude/skills/auditing-mcp/scripts/check_toxic_combinations.py` (lines 9, 14, 113, 117) — update flag references.
  - `.claude/skills/auditing-mcp/SKILL.md` (lines 8, 37, 55, 79, 85) — update routing table dimension 10 + Runtime mode section.
  - `.claude/skills/auditing-mcp/examples/good-mcp-annotated.md` (lines 62, 73, 75) — update example invocation.
  - `.claude/skills/auditing-mcp/references/common-failures.md` (line 53) — update reference.
  - `.claude/skills/auditing-mcp/references/toxic-combinations.md` (lines 17, 59, 88) — update references.
  - `.claude/skills/auditing-cc-configs/scripts/audit_project.py` (lines 247, 407-408, 418, 433) — update flag forwarding; coordinate rename + AC-FR-4-d loud-fail behavior.
  - `.claude/skills/auditing-cc-configs/SKILL.md` (lines 42, 182), `assets/audit-checklist.md` (line 9), `references/audit-rubric.md` (line 125), `references/common-failures.md` (line 133) — documentation updates.
  - `.claude/skills/KB-mcp-platform/references/operator-runbook.md` (line 87), `mcp-events-jsonl.md` (line 103), `troubleshooting.md` (line 109) — runbook updates.
  - `.claude/agents/cc-critique.md` (lines 45, 74) — agent prompt updates.
- **Surface shape:** New `check_mcp_reachability.py` calls `claude mcp ping` (or transport-equivalent JSON-RPC) per-server with the NFR-2 3000 ms timeout; emits per-server `{server, status: reachable|unreachable|transport-error, transport_error: <redacted-string>}`. Legacy `--with-runtime` flag raises a `SystemExit(2)` with a clear migration message per AC-FR-4-d.
- **Lowest-cost primitive justification:** Edits to existing skill scripts + documentation. The rename is mechanical; the handshake is a new sub-script under an existing skill. No new sub-agent, no new MCP server, no new permission policy.
- **Reasoning configuration justification:** N/A — this is a script + docs change, no sub-agent reasoning surface to configure.

### FR-5 — Live tool-surface drift detection (four-stage pipeline)

**Mechanism code:** H8. **Decisions adopted:** D-7 (four-stage RFC-grounded pipeline) + D-10 (severity catalog). **OI dependencies:** none. **Mechanism-dependency table:** R2b; bundled with FR-4.

- **Target files:**
  - `.claude/skills/auditing-mcp/scripts/audit_mcp.py` — new drift-detection dispatch after the FR-4 handshake.
  - `.claude/skills/auditing-mcp/scripts/check_tool_surface_drift.py` — new script implementing the four-stage pipeline (Stage 1 RFC 8785 canonicalize → Stage 2 baseline lookup → Stage 3 RFC 6902 JSON-Patch diff → Stage 4 severity-catalog routing).
  - `.claude/skills/auditing-mcp/baselines/<server-name>.json` — **new subdirectory** for canonical baseline storage (one baseline file per MCP server entry in `.mcp.json`). Each baseline is the RFC 8785-canonicalized `tools/list` response; file content is the only-source-of-truth. **Open as Q-CC-4** for design-composer ratification.
  - `.claude/skills/auditing-mcp/references/drift-severity-catalog.md` — new reference enumerating the severity-catalog mapping (Stage 4 of the pipeline): tool-remove-when-allowlisted → `BLOCKER` (AC-FR-5-a); tool-added → `MAJOR` (AC-FR-5-d); signature-change-on-allowlisted → `MAJOR` (AC-FR-5-e); unparseable → `MAJOR` (AC-FR-5-c); first-encounter → `INFO` (AC-FR-5-b); description/title/icon → `INFO`.
- **Drift-detection algorithm flow:** See §Drift-detection algorithm below.
- **Lowest-cost primitive justification:** Same skill as FR-4; algorithm composes well-cited RFCs. No new sub-agent, no new server.
- **Reasoning configuration justification:** N/A (script-only).

### FR-6 — Mandatory `agent-roster-impact-matrix.md` artifact

**Mechanism code:** B1. **Decisions adopted:** D-5 (hybrid advisory-predicate-with-human-ratification for triggers 3+4) + D-8 (substance heuristic for matrix cells; mandate the structural template). **OI dependencies:** OI-A6 (closed by D-5). **Mechanism-dependency table:** R2a.

- **Target files:**
  - `.claude/agents/design-claude-code.md` — extend Phase 2 (Author the CC Design subsection) with a new mandatory output: `working/feature/<slug>/agent-roster-impact-matrix.md`, conditional on the four-condition trigger. Procedure cross-references the (post-FR-8) Principle 9 text.
  - `.claude/skills/recipe-feature-pipeline/SKILL.md` — outputs table for design-cc gets a third deliverable row (matrix); Design Composition close (Stage 7) gate refuses to mark complete if trigger fired and matrix absent.
  - `.claude/skills/auditing-subagents/scripts/check_feature_touch_predicate.py` — new advisory predicate (D-5 hybrid) that scans `working/feature/<slug>/synthesis.md` + `blueprint.md` for trigger-shaped tokens and emits an advisory annotation to the Design Composition stage state-transition log. design-composer (human) ratifies; override events log to `state-transitions.log` via existing `auditing-shared/scripts/log_state_transition.py`.
  - `.claude/skills/KB-documentation-criteria/references/templates/agent-roster-impact-matrix-template.md` — new template (one row per `.claude/agents/*.md`; one cell per dimension: tools / skills / model / effort / prompt body; positive-evidence-string required per PRD Product Policy + D-8 mandate-for-structural-template).
  - `.claude/skills/KB-cc-design/references/principles.md` (Principle 9) — mutual cross-reference per AC-FR-8-b.
- **Trigger evaluation:** Four conditions per PRD-v2 FR-6 (agent file diff; `.mcp.json` tool-surface diff for already-allowlisted servers; new skill loaded by existing agents; new domain-concept skill-coverage decision naming an agent). Conditions 1–2 are mechanical (file diff). Conditions 3–4 use D-5's hybrid: advisory predicate fires; human ratifies at Design Composition Gate.
- **Per-cell discipline:** Per PRD Product Policy ("structural value plus positive-evidence string"; bare `no change` insufficient). Cell discipline is enforced by `auditing-subagents` script (FR-10 backstop).
- **Lowest-cost primitive justification:** Extends an existing agent's procedure; new template in existing KB; new advisory predicate under an existing audit skill. No new sub-agent. Matrix template lives in KB-documentation-criteria (NFR-9 grep-check: `design-cc` already loads it via `KB-documentation-criteria` skill).
- **Reasoning configuration justification:** `design-cc` stays at `model: opus`, `effort: high`. Matrix authoring is bounded by NFR-7's 30-min-at-100-agents budget; effort: high covers it.

### FR-7 — Skill-coverage check at Synthesis / Design for new domain concepts

**Mechanism code:** B3. **Decisions adopted:** D-8 (substance-as-rubric with mandate-for-new-skill-proposals carve-out). **OI dependencies:** none. **Mechanism-dependency table:** R2a.

- **Target files:**
  - `.claude/skills/KB-cc-design/references/principles.md` — add (or extend Principle 9's neighborhood with) the W/H/A rubric and the substance-not-presence heuristic. Records the new-skill-proposal carve-out: a structured W/H/A artifact is mandated when the decision proposes a *new* skill (creates a new directory under `.claude/skills/`).
  - `.claude/agents/design-claude-code.md` — author-side procedure: when authoring `cc-design.md`, enumerate new domain concepts (Skill-Coverage Decisions section in §10 of this document is the dogfood instance); produce decision row per concept. design-composer reads at composition time.
  - `.claude/agents/synth-synthesizer.md` (or `synth-framer.md`) — synthesis-side trigger: when synthesis identifies a new domain concept, emit a Skill-Coverage Decision row in the synthesis output. (Synthesis agent name selection routes to design-composer — see Q-CC-6.)
  - `.claude/agents/design-composer.md` — Blueprint composition reads each skill-coverage decision row; blocks completion if a row is missing required justification per AC-FR-7-b.
  - `.claude/skills/KB-documentation-criteria/references/templates/` — new sub-template `skill-coverage-decisions-section-template.md`.
- **Substance heuristic:** Per D-8, reviewers apply substance-not-presence — three filled headings can be empty of substance and still pass mandate-as-artifact; substance heuristic catches this. Mandate-for-new-skill-proposals is the exception that pays for itself (review cost is highest on new skill proposals).
- **Lowest-cost primitive justification:** Discipline-text additions to existing KB + procedure extensions to existing agents + new template in existing KB. No new sub-agent.
- **Reasoning configuration justification:** Consuming agents (synth-*, design-composer, design-cc) keep current reasoning config; no rebalance needed.

### FR-8 — Strengthen KB-cc-design Principle 9 from defensive to active

**Mechanism code:** B2. **Decisions adopted:** D-8 (substance heuristic informs the active wording). **OI dependencies:** none. **Mechanism-dependency table:** R2a.

- **Target files (per codebase-analysis blast_radius[5] — concentrated, 2 sites):**
  - `.claude/skills/KB-cc-design/references/principles.md` — rewrite Principle 9 from defensive to active framing.
  - `.claude/agents/design-claude-code.md` (line 56) — update the verbatim citation to match the new wording and to add the AC-FR-8-b mutual cross-reference to FR-6's matrix cell discipline.

**Proposed verbatim sentence-replacement for Principle 9 (per PRD AC-FR-8-a):**

Current Principle 9 leading sentence (line 184): *"Every sub-agent's reasoning capacity is determined by three independent frontmatter fields: `model:`, `effort:`, and `skills:`. They control different things, and the Designer makes each choice deliberately — not by inheriting whatever default the carry-in template happened to use."*

**Replace with (active framing):**

> "For every agent on the touched agent surface — changed and unchanged alike — the Designer records the consideration performed on that agent's three independent reasoning fields (`model:`, `effort:`, `skills:`), even when the recorded outcome is no change. The artifact of the consideration is the `agent-roster-impact-matrix.md` cell (FR-6 of `pipeline-cross-artifact-discipline-r1`); the matrix's positive-evidence-string discipline is the substance test for whether the consideration happened. Bare 'no change' is structurally indistinguishable from 'never evaluated' and is therefore insufficient."

Followed by the existing body of Principle 9 (the `model:` / `effort:` / `skills:` field-by-field discipline, retained verbatim because it remains correct).

**Cross-reference targets (the codebase-analysis blast-radius identified 2 sites; both update):**

1. `.claude/skills/KB-cc-design/references/principles.md` line 15 (TOC entry) — update if leading-sentence shift changes the heading; expected: same heading text "Sub-agent reasoning configuration is intentional, not default" remains — only the *body* shifts from defensive to active framing.
2. `.claude/agents/design-claude-code.md` line 56 — update the verbatim citation to reflect the new active framing AND add the mutual cross-reference to the FR-6 matrix-cell-discipline section (per AC-FR-8-b: "the wording of Principle 9 and the FR-6 cell-discipline text [shall be] cross-referenced (each citing the other by name)").

- **Lowest-cost primitive justification:** Concentrated 2-site edit in existing files. No new artifact.

### FR-9 — Enforce "Blocks downstream" markers as stage-transition gates

**Mechanism code:** B4. **Decisions adopted:** D-4 (structured HTML-comment pragma). **OI dependencies:** OI-A5 (closed by D-4). **Mechanism-dependency table:** R2a.

- **Target files (per codebase-analysis mechanism_dependency_table[FR-9]):**
  - `.claude/skills/KB-documentation-criteria/references/blocks-x-marker-grammar.md` — **new file** authoring the canonical grammar (see §Blocks-X marker grammar below).
  - `.claude/agents/discovery-codebase-researcher.md` — emission site: when discovery surfaces a question whose answer is required before a named stage can complete, emit the marker per the grammar.
  - `.claude/agents/execute-orchestrator.md` — gating logic at stage-transition checkpoints: parse markers from upstream stage outputs; refuse to mark the named stage complete until each marker has transitioned.
  - `.claude/skills/recipe-feature-pipeline/SKILL.md` — checkpoint logic reference.
  - `.claude/skills/KB-documentation-criteria/references/templates/state-transitions-log-entry-template.md` — extend the canonical `transition_name` string-value enumeration with `BLOCKS_X_RESOLVED` / `BLOCKS_X_DEFERRED_WITH_OI` / `BLOCKS_X_FALSE_POSITIVE`. Per codebase-analysis blast_radius[7]: the field is free-string today; no schema evolution required.
  - `.claude/skills/auditing-shared/scripts/log_state_transition.py` — accepts the new `transition_name` values without code change (field is free-string per ADR-0044 v1).
- **Surface shape:** Marker emitted as `<!-- BLOCKS: <stage-slug>-completion -->` (HTML-comment pragma, invisible in rendered markdown, greppable). Orchestrator scans upstream outputs at each stage-transition; per AC-FR-9-a, refuses to mark the named stage complete until each marker transitions. Per AC-FR-9-c, transition rationale logged to state-transitions log.
- **Lowest-cost primitive justification:** New grammar spec file + procedure edits in existing agents + free-string schema-value additions. Grammar pragma is invisible to rendered output but greppable from CI — zero markdown-rendering cost.
- **Reasoning configuration justification:** Discovery + orchestrator agents unchanged.

### FR-10 — `auditing-subagents` feature-touch-coverage rule

**Mechanism code:** B5. **Decisions adopted:** D-3 (separate rule under `auditing-skills` for the reverse-check — surfaced to composer per PRD Product Policy "Open Question"). **OI dependencies:** OI-A3 (recommended resolution: separate rule). **Mechanism-dependency table:** R2a.

- **Target files:**
  - `.claude/skills/auditing-subagents/SKILL.md` — add new rule `SA-14` (next available number after SA-13 from ADR-0040 era): "feature-touch-coverage — when a feature's working directory indicates the agent surface was touched (per FR-6 trigger conditions), verify presence of `agent-roster-impact-matrix.md` and row-count parity with `.claude/agents/*.md` at audit time."
  - `.claude/skills/auditing-subagents/scripts/audit_feature_touch_coverage.py` — new script. Reads `working/feature/<slug>/` for trigger evidence; checks matrix presence + row count; emits `BLOCKER` finding per AC-FR-10-a/-b.
  - `.claude/skills/auditing-subagents/references/` — new reference text for SA-14 discipline.
  - `.claude/skills/auditing-skills/` — (D-3 recommended) **separate** parallel reverse-check rule under auditing-skills (when a new skill is authored, audit whether existing agents' `skills:` arrays should include it). Surfaced as Q-CC-7 for design-composer ratification per PRD Product Policy.
- **Lowest-cost primitive justification:** New audit-rule script under existing audit skill. Backstops FR-6's design-time gate at packaging time (defense-in-depth pattern from KB-cc-design Principle 6 — permissions as safety net).
- **Reasoning configuration justification:** N/A (script-only).

### FR-11 — Replace post-ship time-based deferral triggers with event/honest/concrete framings

**Mechanism code:** §O. **Decisions adopted:** D-9 (three-host placement: KB-cc-design + PV-author rubric + KB-documentation-criteria deferral conventions). **OI dependencies:** none directly; §O.1 row-count discrepancy surfaces as Q-CC-5. **Mechanism-dependency table:** R2b.

- **Target files (per D-9 three-host placement):**
  - `.claude/skills/KB-cc-design/references/principles.md` — append a new section under Principle 9 (or as Principle 11 — see Q-CC-8) enumerating the three permitted framings: event-trigger / honest-acceptance / concrete-machinery. Cross-references the §O.1 register exemplar as the going-forward posture source.
  - `.claude/agents/test-phase-validator-author.md` — PV-author rubric (Phase 2) adds a deferral-framing check: when PV authors a finding with a deferral, the finding's framing must be one of the three permitted (per AC-FR-11-b).
  - `.claude/skills/KB-documentation-criteria/references/disciplines/` — new file `deferral-framing-conventions.md` (or extend the existing disciplines/ directory; current files: `ears-acceptance-criteria.md`, `prd-authoring.md`, `design-composition.md`, `plan-authoring.md`, `discovery-planning.md`). The new file is the canonical posture source consumed by `intake-prd-author` (Undetermined Items section) + `design-composer` (Open Items section).
  - `.claude/agents/intake-prd-author.md` — Undetermined Items prompt cross-references the new conventions file.
  - `.claude/agents/design-composer.md` — Open Items prompt cross-references the new conventions file.
- **Verbatim-preservation discipline (AC-FR-11-c):** Per the register's §O.5, **no retroactive edits** to `Issues/devcontainer-mcp-provisioning-r1-deferrals/register.md` §O.1 rows. Per the codebase-analysis Known Issue 4 + Q-CC-5: the register's §O.1 names FIVE rows (A-3, D-5, E-2, E-3, I-1); PRD AC-FR-11-c enumerates FOUR (E-3, A-3, D-5, I-1). This design preserves all FIVE rows verbatim (the additive cost is zero; the omission of E-2 from the PRD AC is a PRD-mismatch the design-composer surfaces to the user — see Q-CC-5). The FR-11 implementation grep-tests against all five rows.
- **Lowest-cost primitive justification:** Three-host placement is additive (per codebase-analysis Known Issue 7: zero "post-ship" precedent exists in `.claude/skills/` and `.claude/agents/` today). No negation of existing prose required.

## Decisions adopted (D-1 .. D-10)

| Decision | Topic | Adoption in this design |
|---|---|---|
| **D-1 (OI-A1)** | FR-1 prescription-extraction mechanism | **Companion file** sibling to each ADR — pattern `adrs/ADR-NNNN-<slug>.prescriptions.yaml`. Schema in §Companion-file schema. |
| **D-2 (OI-A2)** | FR-3 invariant authoring shape | **Hybrid** — denormalized declaration in each PV body + centralized catalog at `.claude/skills/KB-task-decomposition/cross-file-invariants.md`. |
| **D-3 (OI-A3)** | auditing-skills reverse-check scope | **Separate rule** under `auditing-skills` (parallel to FR-10's SA-14). Surfaced as Q-CC-7 per PRD Product Policy. |
| **D-4 (OI-A5)** | Blocks-X marker grammar | **Structured HTML-comment pragma** `<!-- BLOCKS: <stage-slug>-completion -->`. Grammar in §Blocks-X marker grammar. |
| **D-5 (OI-A6)** | FR-6 trigger 3+4 evaluator | **Hybrid advisory predicate + human ratification** at Design Composition Gate. Override events log to `state-transitions.log`. |
| **D-6 (Contingency Split)** | R2a vs R2b posture | **Forwarded to design-composer at Gate 4** per PRD Product Policy + synthesis §Contingency-Split Resolution Substrate. Synthesis recommendation (single-feature R1, absent contradicting Gate-4 evidence) carried forward. Q-CC-1 surfaces the routing. |
| **D-7 (FR-5 algorithm)** | Drift-detection pipeline | **Four-stage** RFC 8785 canonicalize → baseline lookup → RFC 6902 JSON-Patch diff → severity catalog. Flow in §Drift-detection algorithm. |
| **D-8 (FR-7 W/H/A)** | Skill-coverage trifecta posture | **Substance-as-rubric** for skill-coverage decisions generally; **mandate-as-artifact** for new-skill proposals (carve-out). Couples to D-5 (machine checks shape; human checks substance). |
| **D-9 (FR-11 §O placement)** | Posture wording host | **Three-host placement** — KB-cc-design + test-phase-validator-author + KB-documentation-criteria deferral conventions. E-2 inclusion in AC-FR-11-c scope routes to design-composer (Q-CC-5). |
| **D-10 (severity vocabulary)** | Reconciliation across FR-1/4/5/9/10 | **Preserve trifecta + explicit bridge table** hosted in `KB-review-disciplines/references/severity-taxonomy.md`. design-composer ratifies bridge wording. Q-CC-2 routes the publication target. |

## Companion-file schema (D-1 / FR-1)

**Location pattern:** `adrs/ADR-NNNN-<slug>.prescriptions.yaml` (sibling to each `adrs/ADR-NNNN-<slug>.md`). Lowercase slug per ADR filename convention. The companion is optional — ADRs without machine-checkable prescriptions have no companion file (per AC-FR-1-b, the auditor no-ops).

**Placement discipline:** Per ADR-0036 (single canonical location), ADR-0054 (canonical-helper validator), and ADR-0056 (no carve-outs in canonical-placement rules) — the companion lives at `adrs/`, same root as the ADR it accompanies. No subdirectory; no carve-out for "machine-checkable" siblings; the helper `validate_adr_placement.py` continues to enforce the canonical location and the new helper `validate_adr_prescriptions.py` enforces the companion's schema independently.

**Schema (v1.0):**

```yaml
# adrs/ADR-0041-install-mechanism-hybrid.prescriptions.yaml
adr_id: ADR-0041
adr_path: adrs/ADR-0041-install-mechanism-hybrid.md
schema_version: 1.0.0
prescriptions:
  - id: P-1
    summary: ".mcp.json must contain six MCP server entries (post-2026-05-24 state)"
    target_path: .mcp.json
    assertion:
      kind: jsonpath_count
      jsonpath: $.mcpServers
      expected: 6
    severity_floor: BLOCKER
  - id: P-2
    summary: "postCreate.sh must NOT install mcp-openapi-schema"
    target_path: .devcontainer/postCreate.sh
    assertion:
      kind: regex_not_present
      pattern: "mcp-openapi-schema"
    severity_floor: BLOCKER
```

**Field semantics:**

- `adr_id`, `adr_path` — back-reference; the linter `validate_adr_prescriptions.py` checks `adr_path` resolves to an existing ADR-NNNN-<slug>.md and the slug matches the companion's slug.
- `schema_version` — additive evolution per ADR-0018 / ADR-0038 precedent.
- `prescriptions[]` — array of machine-checkable predicates. The auditor iterates each entry; for each, it opens `target_path` and applies `assertion` per `assertion.kind`.
- `assertion.kind` — initial vocabulary: `regex_present` / `regex_not_present` / `jsonpath_equals` / `jsonpath_count` / `file_exists` / `file_not_exists` / `substring_present` / `substring_absent`. Additive; new kinds bump schema_version's minor field.
- `severity_floor` — the severity emitted on mismatch. Floor (not ceiling): the auditor MAY upgrade based on D-10 bridge-table mapping but never downgrades.

**Versioning policy:** Additive minor bumps for new `assertion.kind` values; major bump only for incompatible reorganization. This is surfaced as Q-CC-3 for design-composer ratification.

**Linter responsibilities (`validate_adr_prescriptions.py` in `auditing-shared/scripts/`):**

1. Schema-validate companion-file YAML against the documented shape (Gate 0 structural).
2. Verify `adr_path` resolves and slug matches.
3. Verify each `target_path` exists at audit time (warning if missing; the audit itself surfaces the violation).
4. Reject duplicate `id` values within a companion (BLOCKER finding).

## Drift-detection algorithm flow (D-7 / FR-5)

**Inputs:** `.mcp.json` (one entry per MCP server); live `tools/list` response per server (from the FR-4 handshake); per-server baseline file at `.claude/skills/auditing-mcp/baselines/<server-name>.json`.

**Stage 1 — RFC 8785 canonicalize.** Apply JSON Canonicalization Scheme (RFC 8785) to the live `tools/list` response: sort object keys lexicographically; normalize numbers; normalize whitespace; UTF-8 NFC normalization. This is the dominant FP-suppression locus per synthesis §D-7 (Cons section: openapi-diff Issue #673 cautionary tale).

**Stage 2 — Baseline lookup.** Read `.claude/skills/auditing-mcp/baselines/<server-name>.json`. If the file does not exist: write the Stage 1 canonical output as the new baseline; emit AC-FR-5-b `INFO` diagnostic; skip Stages 3–4.

**Stage 3 — RFC 6902 JSON-Patch diff.** Compute the JSON-Patch diff between the canonical baseline (Stage 2) and the canonical live response (Stage 1). MCP spec guarantees tool names are unique, so use identity-keyed array diff (key = `name` field). Output is a list of `{op, path, value, oldValue?}` patch operations.

**Stage 4 — Severity-catalog routing.** Apply the catalog from `.claude/skills/auditing-mcp/references/drift-severity-catalog.md`:

| Patch op | Path target | Allowlisted to ≥1 agent? | Severity | AC anchor |
|---|---|---|---|---|
| `remove` | `/<tool_name>` (tool removed) | Yes | `BLOCKER` | AC-FR-5-a |
| `remove` | `/<tool_name>` (tool removed) | No | `MAJOR` | AC-FR-5-a partial |
| `add` | `/<tool_name>` (new tool) | N/A (new) | `MAJOR` | AC-FR-5-d |
| `replace` | `/<tool_name>/inputSchema` (signature change) | Yes | `MAJOR` | AC-FR-5-e |
| `replace` | `/<tool_name>/inputSchema` (signature change) | No | `MINOR` | AC-FR-5-e partial |
| `replace` | `/<tool_name>/description` | N/A | `INFO` | (NFR-4 FP-suppression) |
| `replace` | `/<tool_name>/title` or `/<tool_name>/icon` | N/A | `INFO` | (NFR-4 FP-suppression) |
| Unparseable response | (parse error) | N/A | `MAJOR` | AC-FR-5-c |

**NFR-4 (<5% FP rate) pilot:** Per synthesis §Open Items item 8, no surveyed source publishes a quantitative benchmark for this exact use case. Run a pilot at Phase Validator authoring time: 50 audits against the current stable MCP server set; measure FP rate; refine the severity catalog if FP > 5%. Surfaced in §Open Items.

**Baseline-write convention:** Baselines update on explicit `--accept-drift` flag (operator-acknowledged); never on silent observation. Baselines are committed to the repo so drift detection is reproducible.

## Agent-roster impact matrix schema (FR-6)

**Filename:** `working/feature/<slug>/agent-roster-impact-matrix.md`. One file per feature run that fires the four-condition trigger.

**Required sections:**

1. **Header** — frontmatter `id`, `version`, `feature_slug`, `generated`, `generated_by: design-cc`. Includes the trigger that fired (which of the four conditions) and the verbatim citation of Principle 9.
2. **Summary findings** — count of agents in each category (changed / unchanged with evidence / no evaluation possible — the last category should be zero).
3. **Per-agent matrix** — one row per `.claude/agents/*.md` file at authoring time. The row count must equal `ls .claude/agents/*.md | wc -l` per AC-FR-6-b. **Each row has five required cells:**

| # | Agent file | Tools | Skills | Model | Effort | Prompt body |
|---|---|---|---|---|---|---|

Per the PRD Product Policy + D-8 mandate-for-structural-template, **each cell carries a structural value + a positive-evidence string**. Cell schema (canonical):

```text
<value> — <positive-evidence-string>
```

Where `<value>` is one of: `no-change` | `tools-add: <list>` | `tools-remove: <list>` | `skills-add: <list>` | `skills-remove: <list>` | `model-change: <old>→<new>` | `effort-change: <old>→<new>` | `prompt-edit: <one-line-summary>`. Bare `no-change` without a positive-evidence-string fails the FR-10 backstop audit + the FR-6 design-time block.

**Positive-evidence-string discipline (per Principle 9 post-FR-8 wording):** "no responsibility intersect with feature scope (verified against agent prompt body + tools list)"; or "loads KB-X, which receives a new section in this feature — but the consuming procedure step in this agent does not invoke that section (verified against Phase N of the agent body)"; or similar.

**Exemplar reference:** `Issues/per-agent-design-evaluation-gap/evidence/agent-roster-impact-matrix.md` (the retroactive Track-A2 matrix from devcontainer-mcp-provisioning-r1, migrated per issue-capture-mechanism-r1 FR-9; 39602 bytes; 36-row matrix at the time of authoring; current actual inventory is 37 per codebase-analysis Known Issue 6). Cells in the exemplar use `EXPLICIT_NO — <evidence>` shape; the FR-6 template generalizes this pattern.

**Authoring-time budget:** NFR-7 caps wall-clock at 30 min for a 100-agent inventory. The template ships with column widths sized for terminal rendering + grep-friendly cell delimiters.

## Blocks-X marker grammar (D-4 / FR-9)

**Grammar specification (canonical):**

```
<!-- BLOCKS: <stage-slug>-completion -->
```

**Form rules:**

- **Token:** literal `BLOCKS:` (uppercase, colon-suffixed).
- **Stage slug:** kebab-case identifier matching the stage's `recipe-feature-pipeline` slug, suffixed with `-completion`. Valid examples: `discovery-completion`, `synthesis-completion`, `design-cc-completion`, `design-composition-completion`, `plan-authoring-completion`, `phase-validator-authoring-completion`.
- **Container:** HTML comment `<!-- ... -->`. Invisible in rendered markdown; greppable from CI; multi-slug-ready by repeating the comment.
- **Optional payload:** the marker MAY include a one-line description after the slug, separated by ` — ` (em-dash-space surrounded by spaces): `<!-- BLOCKS: design-cc-completion — A-5 grammar undecided -->`. The parser extracts only the slug; the description is for human review.
- **Multiplicity:** multiple markers MAY appear in one output; each is parsed independently.

**Parser shape:** regex `<!--\s*BLOCKS:\s*([a-z0-9-]+)-completion(?:\s+—\s+[^\n]*)?\s*-->`. Captures the stage slug. The orchestrator iterates captures.

**Emission examples:**

```markdown
<!-- BLOCKS: design-cc-completion — OI-A5 grammar undecided -->
<!-- BLOCKS: synthesis-completion -->
```

**State-transitions log integration (per IN-013 of research plan):** Per codebase-analysis blast_radius[7], the `transition_name` field in state-transitions log entries is free-string (per ADR-0044 v1). FR-9 reserves these `transition_name` string values:

- `BLOCKS_X_RESOLVED` — marker closed with rationale; downstream stage may proceed.
- `BLOCKS_X_DEFERRED_WITH_OI` — marker converted to an explicit Open Item; downstream stage may proceed; OI tracked.
- `BLOCKS_X_FALSE_POSITIVE` — marker withdrawn with rationale; downstream stage may proceed.

The `context` field of the log entry carries the marker's stage slug + the closure rationale. No schema evolution required (per `state-transitions-log-entry-template.md` v1 free-string `transition_name`).

**Migration note:** The single existing prior occurrence at `working/feature/devcontainer-mcp-provisioning-r1/codebase-analysis-report.md:198-202` uses the prose form `Blocks design-composition-completion.` / `Blocks design-cc-completion.` (period-terminated kebab-case). This is *not retroactively migrated* (per Won't-Have analog of FR-11 — no retroactive edits to prior feature deliverables); future emissions use the structured grammar.

**Grammar spec host:** `.claude/skills/KB-documentation-criteria/references/blocks-x-marker-grammar.md` (new file). Per synthesis §D-4 constraint propagation, this is the natural home given Discovery output is one of the documentation-criteria KB's consumers.

## Severity vocabulary bridge table (D-10)

Three coexisting vocabularies persist (per codebase-analysis Known Issue 2 + KB-cc-design Principle 1's audience-fit rationale). FR-1, FR-4, FR-5, FR-9, FR-10 emit auditor-vocabulary. FR-3 interacts with PV-vocabulary.

| Auditor vocabulary | Reviewer vocabulary | Phase-Validator vocabulary | Verdict-compute impact | Notes |
|---|---|---|---|---|
| `BLOCKER` | `critical` | `blocking` | -12 points | Monotonic across surfaces. Forces `needs_revision` / refuse-to-advance. |
| `MAJOR` | `important` | `blocking` (when assertion fails outright) or `warning` (when partial) | -5 points | PV vocabulary collapses to two grades when MAJOR — context-dependent. |
| `MINOR` | `recommended` | `warning` | -2 points | Monotonic. |
| `NIT` (auditing-mcp) / `INFO` (architecture/cross-artifact auditors) | `recommended` (NIT) / N/A (INFO) | `informational` | -0.5 (NIT) / 0 (INFO) | Auditor surface itself has a NIT/INFO sub-divergence (codebase-analysis Known Issue 2). |

**Bridge-table publication target:** `.claude/skills/KB-review-disciplines/references/severity-taxonomy.md`. Per D-10 synthesis recommendation: hosting in `KB-review-disciplines` is the natural single source of truth because all three reviewer-surface agents (shared-document-reviewer, review-architecture-auditor, review-cross-artifact-auditor) already load this KB. **Q-CC-2 routes the final publication target to design-composer** because the decision cross-cuts layers per synthesis §D-10.

**Translator utility:** Optional `auditing-shared/scripts/translate_severity.py` at audit-issues.json emission time. Reads the source vocabulary + the target audience; emits the target vocabulary per the bridge table. Non-monotonic edges (NIT vs recommended; the MAJOR→{blocking, warning} branch) require explicit rationale in the translator output.

**Non-monotonic notes:**

- `NIT` → `recommended`: the reviewer vocabulary lacks a sub-`recommended` grade; NIT-class findings translate to `recommended` but the translator records "NIT — non-actionable in reviewer surface" so the reviewer can deprioritize.
- `MAJOR` → `blocking` vs `warning` in PV vocabulary: depends on whether the MAJOR finding represents an outright assertion failure (blocking) or a partial / soft failure (warning). The translator requires this context as an input parameter.

## Skill-coverage decisions for THIS feature (eat-own-dogfood per FR-7)

Per FR-7's substance heuristic (D-8), each new domain concept introduced by this feature is paired with an explicit skill-coverage decision: (a) name the existing skill, (b) propose a new skill with W/H/A trifecta, or (c) record "no skill warranted" with rationale.

| New domain concept | Decision | Existing skill / rationale |
|---|---|---|
| **"design-realization audit"** (FR-1) | (a) covered by `KB-review-disciplines` | The audit dimension extends `architecture-audit.md`'s existing lens enumeration (CoVe, Blast-Radius, Brief-Honor) with Lens 4. The KB already governs auditor discipline; the new lens is additive content. No new skill warranted. |
| **"protocol conformance"** (FR-2) | (a) covered by `KB-codebase-research` | The subsection extends the codebase-analysis schema's existing convention-recording shape. The KB already governs the researcher's output contract. No new skill warranted. |
| **"cross-file invariant catalog"** (FR-3) | (a) covered by `KB-task-decomposition` (catalog body) + `KB-review-disciplines` (severity discipline) | Synthesis §D-2 constraint propagation places the catalog at `KB-task-decomposition/cross-file-invariants.md`; severity floor / no-downgrade discipline lives in `KB-review-disciplines`. No new skill warranted. |
| **"MCP reachability"** (FR-4) | (a) covered by `KB-mcp-platform` + `KB-mcp-design` + `auditing-mcp` | The handshake mechanic is a new sub-script under `auditing-mcp`; the discipline (what reachability means; when to use it) lives in `KB-mcp-design` operator runbook. No new skill warranted. |
| **"tool-surface drift detection"** (FR-5) | (a) covered by `auditing-mcp` (new reference `drift-severity-catalog.md`) | The four-stage pipeline is implementation inside an existing audit skill. The severity catalog is a new `references/` file inside an existing skill — additive, not a new skill. No new skill warranted. |
| **"agent-roster impact matrix"** (FR-6) | (a) covered by `KB-cc-design` (Principle 9) + `KB-documentation-criteria` (template) | The matrix template lives in KB-documentation-criteria; the rationale + cell-discipline lives in KB-cc-design Principle 9. Both KBs are already loaded by `design-cc`. No new skill warranted. |
| **"skill-coverage decision"** (FR-7) | (a) covered by `KB-cc-design` (W/H/A rubric in Principle 9 neighborhood) + `KB-documentation-criteria` (template) | Same hosts as FR-6; rubric is a new section in KB-cc-design. No new skill warranted. |
| **"Principle 9 active reframing"** (FR-8) | (a) covered by `KB-cc-design` | In-place edit of the existing principle. No new skill. |
| **"Blocks-X marker grammar"** (FR-9) | (a) covered by `KB-documentation-criteria` (new reference `blocks-x-marker-grammar.md`) | New reference file in an existing KB. No new skill warranted. |
| **"agent-roster matrix audit rule"** (FR-10) | (a) covered by `auditing-subagents` (new SA-14) | New audit rule in an existing audit skill. No new skill warranted. |
| **"§O event-triggered framings"** (FR-11) | (a) covered by `KB-cc-design` + `KB-documentation-criteria` (deferral conventions) + `test-phase-validator-author` (PV rubric, inlined per Known Issue 3) | Three-host placement per D-9; all hosts exist. No new skill warranted. |

**Eat-own-dogfood compliance:** All 11 new domain concepts decided via option (a) — covered by existing skills. Zero new skill proposals. Zero "no skill warranted" rationales required. The substance-not-presence heuristic (D-8) passes trivially because the decisions are concrete file-and-line citations.

## Agent-roster impact for THIS feature (eat-own-dogfood per FR-6)

This feature touches the agent surface per FR-6's four-condition trigger (specifically condition 1 — modifies several `.claude/agents/*.md` files: review-architecture-auditor, discovery-codebase-researcher, design-claude-code, test-phase-validator-author, execute-orchestrator, intake-prd-author, design-composer, cc-critique, synth-synthesizer-or-framer, and indirectly via skill loads). Therefore the feature MUST produce `working/feature/pipeline-cross-artifact-discipline-r1/agent-roster-impact-matrix.md` before Design Composition can mark its stage complete (FR-6 self-application).

**Posture for this design's deliverable archive:** The FR-6 design-time block applies to *this* feature run too (eat-own-dogfood; FR-6 is established by this feature, but the establishment shipment itself must comply — the same logic that motivates FR-6 applies to the feature that ships FR-6). **The actual roster matrix authoring is therefore a deliverable of this feature run, produced at Design Composition close by design-cc** (an authoring step in the Plan / Task Decomposition stages, not the Per-Layer Design stage where this document lives).

The matrix's 37-row content (per codebase-analysis Known Issue 6) is enumerated at Plan / Task Decomposition time per the matrix template defined in §FR-6. This document records the contract under which the matrix is authored; it does not author the matrix itself (which would be a Plan-stage output).

**Mechanical-evaluator override-event posture (per D-5):** If the design-cc author at Plan time disagrees with the advisory predicate's classification of any of the four trigger conditions for this feature, the override event is logged to `state-transitions.log` via `auditing-shared/scripts/log_state_transition.py` as `transition_name: TRIGGER_OVERRIDE`, with context naming the trigger condition + the human rationale.

## §O.1 row count discrepancy and correction

Per codebase-analysis Known Issue 4 + synthesis §Open Items item 9 + the PRD's own AC-FR-11-c verbatim-preservation requirement, there is a row-count mismatch:

- **PRD AC-FR-11-c enumerates FOUR rows** to preserve verbatim: E-3, A-3, D-5, I-1.
- **Register §O.1 actually contains FIVE rows**: A-3, D-5, E-2, E-3, I-1. The fifth row (E-2 — "Serena felt-utility review post-ship") has the same post-ship anti-pattern shape as the other four.

**Design posture (per synthesis D-9 recommendation):** Preserve all FIVE rows verbatim. The PRD's omission of E-2 from AC-FR-11-c is best read as oversight rather than deliberate exclusion (the synthesizer's verification surfaced this discrepancy and routed it to design-composer; no PRD-level rationale for excluding E-2 exists in the PRD prose).

**Correction routed via Q-CC-5** (below). design-composer surfaces this to the user at Gate 4 as a PRD-mismatch (small but factual). If the user ratifies "preserve five" — the design ships as written. If the user ratifies "preserve four (E-2 excluded by design)" — AC-FR-11-c stays at four-row enumeration and the design adjusts the FR-11 implementation grep-test accordingly.

## Open Items (Q-CC-N) for design-composer

| ID | Question | Rationale | Recommended | Routes to |
|---|---|---|---|---|
| **Q-CC-1** | D-6 Contingency Split posture (R1 single vs R2a/R2b) | Two well-evidenced readings (orchestrator-currently-open = 6; cumulative = 14); both have direct PRD evidence. Per synthesis §Contingency-Split Resolution Substrate, the framer's instruction is to route to Gate 4. | Ship single-feature R1 absent contradicting Gate 4 evidence | design-composer at Gate 4 |
| **Q-CC-2** | D-10 severity vocabulary bridge table publication target | Recommended host is `KB-review-disciplines/references/severity-taxonomy.md`. Alternative: `auditing-shared/` as cross-surface utility. Decision cross-cuts layers per synthesis §D-10. | `KB-review-disciplines/references/severity-taxonomy.md` | design-composer at Blueprint composition |
| **Q-CC-3** | FR-1 companion-file schema versioning policy | Additive minor for new `assertion.kind`; major for incompatible reorganization. Confirm vs. alternative (single-rev-only). | Additive minor / breaking major | design-composer (ADR candidate) |
| **Q-CC-4** | FR-5 baseline storage location | `.claude/skills/auditing-mcp/baselines/<server-name>.json` is the design's recommendation. Alternatives: `.claude/runtime/mcp-baselines/` (runtime-scoped, gitignored variant) or repo-root. | `.claude/skills/auditing-mcp/baselines/` (committed) | design-composer (ADR candidate) |
| **Q-CC-5** | §O.1 row count correction (5 not 4) | PRD AC-FR-11-c enumerates 4 rows; register actually has 5 (E-2 missing from PRD). Small but factual PRD-mismatch. | Preserve all 5 rows; user ratifies at Gate 4 | design-composer at Gate 4 (user-facing) |
| **Q-CC-6** | FR-7 synthesis-side emission site (synth-synthesizer.md vs synth-framer.md) | Skill-coverage decision row emitted at Synthesis; which synth-* agent is the canonical producer? | synth-synthesizer.md (primary; framer.md cross-references) | design-composer at Blueprint composition |
| **Q-CC-7** | D-3 auditing-skills reverse-check separation | Per PRD Product Policy: separate sibling rule under `auditing-skills` vs. extend FR-10 scope vs. defer. Synthesis recommends separate rule. | Separate rule under `auditing-skills` | design-composer at Blueprint composition |
| **Q-CC-8** | FR-11 §O posture wording — inline in Principle 9 vs. new Principle 11 | The discipline could amend Principle 9 (defer-framings as sub-section) or stand as Principle 11 (parallel to Principle 10's canonical-placement rule). | Sub-section under Principle 9 (avoids principle proliferation) | design-composer at Blueprint composition |

## Cross-references to ADRs the design depends on

- **ADR-0005** — Append-only supersession discipline; FR-8's Principle 9 rewording either edits in place + amendment note OR supersedes with a new Principle 11 (Q-CC-8 ratifies).
- **ADR-0009** — Rationale brief honor discipline; the brief-honor citation at the top of this design satisfies the L3 brief-honor check.
- **ADR-0017** — shared-document-reviewer invocation points (5 points); FR-6's matrix is reviewed at invocation 3 (per-layer Design outputs).
- **ADR-0018** — codebase-analysis.json provenance + additive-extension discipline; FR-2's schema extension is governed by it.
- **ADR-0020** — KB consolidation discipline; FR-3's `cross-file-invariants.md` lives in KB-task-decomposition per the same discipline (existing KBs absorb new content; no new KB for one catalog file).
- **ADR-0027** — cwd == repo-root precondition; baseline storage uses repo-relative path.
- **ADR-0030** — pedagogical-section discipline; the new templates in KB-documentation-criteria conform to the pedagogical-marker spec.
- **ADR-0036** + **ADR-0054** + **ADR-0056** — ADR placement canonical-rule + canonical-helper validator + no-carve-outs principle; FR-1 companion file lives at `adrs/` per the same rule, with no extension-based carve-out (Principle 10 from KB-cc-design).
- **ADR-0038** — codebase-analysis schema v1.1.0; FR-2's additive extension goes to v1.2.0 or v1.1.x.
- **ADR-0039** — credential indirection; NFR-6 redaction posture rides on it.
- **ADR-0040** — Serena narrowed-allowlist precedent; the canonical exemplar of the per-agent-design-evaluation-gap that FR-6 closes.
- **ADR-0041** — install-mechanism-hybrid; the canonical ADR-prescription that FR-1 + the companion-file convention closes.
- **ADR-0042** — graduated-family skill discipline; `auditing-mcp` family hosts FR-4 + FR-5 edits.
- **ADR-0044** — state-transitions log v1 invariant (execute-orchestrator is the sole writer); FR-9 reserves new `transition_name` string values consistent with the invariant.
- **ADR-0045** — review-architecture-auditor has no Agent/Task tool; FR-1's new dimension runs inline, not via sub-agent spawn-out.

## Dependencies on other layers

**None active.** Per PRD Layer Scope, the only activated layer for this feature is Claude Code. The 8 other layers are explicitly marked `N/A — out of scope`. No `depends_on` or `provides_to` edges to other-layer designs in this feature run.

(The dependencies manifest sidecar `cc-dependencies.json` enumerates intra-layer file dependencies and reverse-blast-radius edges per the codebase-analysis blast-radius entries.)

## Dependencies manifest summary

The sibling `cc-dependencies.json` enumerates every file this design touches, by FR responsibility, with reverse dependents per the codebase-analysis blast-radius. Categories:

- **edits** — existing files modified in place: 24 files (touchpoints per `mechanism_dependency_table`).
- **creates** — new files authored: 11 files (companion schema host, drift catalog, baselines/ subdir + baseline files, blocks-x grammar spec, deferral conventions discipline text, advisory predicate script, SA-14 audit rule script, prescription linter, agent-roster matrix template, skill-coverage decisions template, protocol-conformance subsection template).
- **annotates** — discipline / KB cross-reference additions (no structural edit): 3 sites.

See `cc-dependencies.json` for the precise enumeration with FR ownership + reverse dependents.

## Self-review checklist (Phase 4 mental Gate 0)

- [x] All 11 FRs land in this CC design subsection (FR-1 … FR-11 each have a per-FR sub-section).
- [x] Every AC referenced is in EARS form (consumed from PRD-v2 verbatim; no AC restated).
- [x] Every new primitive has a lowest-cost-primitive justification (Principle 1).
- [x] CLAUDE.md is NOT modified (KB-cc-design Principle 5 — single source of truth; no need to add to CLAUDE.md when KBs and discipline texts suffice).
- [x] Path-gating is used wherever applicable (auditing-mcp scripts; new SKILL.md additions are scoped under existing skill paths).
- [x] Permission policy: no new mutating-tool entries required by this feature. Audit scripts read state and emit JSON; the new `--with-mcp-reachability` flag invokes a live JSON-RPC handshake with the existing `.mcp.json` indirection per ADR-0039 (credentials via env-block only). NFR-6 redaction is design-mandated for FR-4/FR-5 output emission.
- [x] Q-CC-N items complete (8 items: Q-CC-1 .. Q-CC-8).
- [x] Brief-honor citation present at head of document and re-referenced in FR-1, FR-6 procedure citations.
- [x] Reasoning-configuration justifications recorded for every modified sub-agent (per FR-8 / Principle 9 post-active framing): `review-architecture-auditor`, `discovery-codebase-researcher`, `test-phase-validator-author`, `design-cc` — all unchanged from current frontmatter; reasoning load increment evaluated.
- [x] Severity vocabulary handled via D-10 bridge table (auditor vocabulary for FR-1/4/5/9/10; PV vocabulary interaction for FR-3).
- [x] §O.1 row-count correction surfaced (Q-CC-5) without retroactively editing the register itself (FR-11 / AC-FR-11-c discipline preserved).

---

*End of Claude Code per-layer Design subsection. Awaiting design-composer integration into the Blueprint at Stage 7, then shared-document-reviewer at invocation 3, then review-architecture-auditor at Stage 8.*
