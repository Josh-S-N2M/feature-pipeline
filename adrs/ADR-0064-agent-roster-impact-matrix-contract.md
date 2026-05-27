---
id: ADR-0064
version: 1.0.1
status: Accepted
generated: 2026-05-26
generated_by: design-composer
supersedes: []
adrs_inherited:
  - {id: ADR-0017, version: 1.0.0}
  - {id: ADR-0040, version: 1.0.0}
  - {id: ADR-0044, version: 1.0.0}
applies_to:
  - pipeline-design-time-discipline-r1
  - all-future-features-that-touch-agent-surface
template_format: per KB-documentation-criteria ADR template v1.0
change_summary: Establishes the mandatory `agent-roster-impact-matrix.md` deliverable contract — four-condition trigger, full-inventory row count, five explicit dimensions per row, positive-evidence-string cell discipline, advisory mechanical-predicate evaluator with human ratification — applied whenever a feature touches the agent surface.
---

# ADR-0064: Agent-Roster Impact Matrix Contract

## Contents

- [x] Status
- [x] Context
- [x] Decision
- [x] Decision Details
- [x] Rationale
- [x] Options Considered
- [x] Consequences
- [x] Architecture Impact
- [x] Implementation Guidance
- [x] Related Information

## Status

Accepted — 2026-05-26

## Update History

| Version | Date | Change | Driver |
|---|---|---|---|
| 1.0.0 | 2026-05-26 | Initial ADR authored by `design-composer` at Design Composition. | R2a Design Composition stage. |
| 1.0.1 | 2026-05-26 | Clause 3 + Options Considered Option B: corrected "Blueprint's Skill-Coverage Decisions section" → "synthesis.md Skill-Coverage Decisions section" to align with ADR-0065 Clause 1 (the load-bearing artifact-location decision). Editorial in-place edit per ADR-0005 (no supersession). | Audit finding I-AA-001 (architecture-audit cycle 1); reconciliation cycle 1 dispatch to `design-composer`. |

## Context

The `per-agent-design-evaluation-gap` analysis traced the `devcontainer-mcp-provisioning-r1` shipment incident to a structural defect on the design-time side: the pipeline iterated the *changed* agent surface (8 of 36 agents got the new MCP tools) without ever enumerating the full inventory to confirm the other 28 should not change. The gap was caught at Gate 4 by the user, not by any pipeline mechanism. A retroactive sweep happened to confirm the supply-driven set, but no structural mechanism would have surfaced a wrong answer if the set had been incomplete.

FR-6 of `pipeline-design-time-discipline-r1` closes this gap by making a full-inventory `agent-roster-impact-matrix.md` artifact mandatory whenever a feature touches the agent surface. The artifact is load-bearing across the pipeline:

- It is reviewed at `shared-document-reviewer` invocation 3 (per ADR-0017).
- Its presence is enforced at Design Composition close (design-time block).
- Its presence + row-count parity is enforced at pre-deliverable-packaging time by `auditing-subagents` rule SA-14 (FR-10 backstop).
- Its per-cell positive-evidence-string discipline is the substance test for FR-8's active-framing of KB-cc-design Principle 9.

Without a normative contract for what counts as "touching the agent surface," what the matrix must contain, and how triggers 3 and 4 (which require interpretive reads) are evaluated, future feature runs will produce uneven matrices — the very recurrence mode FR-6 exists to prevent.

The contract surface decomposes into four normative questions:

1. **Trigger surface.** What concretely constitutes "touching the agent surface"?
2. **Artifact shape.** How many rows; what columns; what cell discipline?
3. **Trigger evaluation.** How are interpretive triggers (3 and 4) consistently evaluated across runs?
4. **Override discipline.** When designer judgment disagrees with mechanical advice, how is the override recorded?

The cross-decision dependency table (synthesis §Cross-Decision Dependencies) binds D-5 (trigger evaluator) and D-8 (substance heuristic) at a load-bearing seam: the mechanical predicate scores SHAPE; the human's substance judgment cannot collapse into the predicate. This ADR records the contract so the seam is preserved.

## Decision

The `agent-roster-impact-matrix.md` deliverable contract is hereby normative. Four normative clauses:

**Clause 1 — Four-condition trigger.** A feature is deemed to "touch the agent surface" if any of the following hold during the run:

1. The feature's diff modifies, creates, or removes any file under `.claude/agents/*.md`.
2. The feature's diff modifies `.mcp.json` in a way that adds, removes, or changes the tool surface of any MCP server already allowlisted to one or more agents.
3. The feature's diff creates a new skill (`.claude/skills/<name>/SKILL.md`) that the feature's design indicates one or more existing agents will load.
4. The feature's design or PRD declares a new domain concept whose skill-coverage decision (per ADR-0065) names an existing agent as a downstream consumer.

Triggers 1 and 2 are mechanical (file-diff and JSON-shape parseable). Triggers 3 and 4 are interpretive.

**Clause 2 — Artifact shape.** The matrix lives at `working/feature/<slug>/agent-roster-impact-matrix.md` and obeys:

- **Row count:** exactly equal to the count of `.claude/agents/*.md` files at matrix authoring time. No more, no fewer.
- **Five explicit dimensions per row:** `tools`, `skills`, `model`, `effort`, `prompt body`. One cell per dimension per row.
- **Per-cell discipline:** every cell contains `<value> — <positive-evidence-string>`. The `<value>` is one of: `no-change` | `tools-add: <list>` | `tools-remove: <list>` | `skills-add: <list>` | `skills-remove: <list>` | `model-change: <old>→<new>` | `effort-change: <old>→<new>` | `prompt-edit: <one-line-summary>`. The `<positive-evidence-string>` is a short rationale derived from inspectable evidence (the agent's prompt body; tools list; surrounding context).
- **Bare `no-change` without an evidence string is structurally insufficient** and fails both the FR-6 design-time block and the FR-10 packaging-time backstop.

At the current 37-agent inventory, the matrix is 37 rows × 5 cells = 185 cells per run.

**Clause 3 — Advisory mechanical predicate + human ratification.** A new advisory predicate at `.claude/skills/auditing-subagents/scripts/check_feature_touch_predicate.py` evaluates the four trigger conditions. For triggers 1 and 2, the predicate emits a definitive yes/no. For triggers 3 and 4, the predicate emits an advisory annotation by scanning the synthesis.md Skill-Coverage Decisions section for trigger-shaped tokens. `design-composer` (human) ratifies whether the matrix is required.

The predicate does NOT mandate the matrix on its own — its output is advisory. The human ratifies.

**Clause 4 — Override-event discipline.** When the human designer disagrees with the predicate's classification of any trigger condition, the disagreement is logged to `state-transitions.log` via `auditing-shared/scripts/log_state_transition.py` with `transition_name: TRIGGER_OVERRIDE`, and the `context` field names the trigger condition + the human rationale. Per ADR-0044 v1, `transition_name` is free-string; this value lands without schema evolution.

Override events are the corpus future tuning of the predicate reads from. Silent overrides (no log entry) are structurally indistinguishable from "no trigger fired"; the log entry IS the override.

## Decision Details

| Detail | Specification |
|---|---|
| **Why now** | The defect class is recurrent: `devcontainer-mcp-provisioning-r1` shipped MCP-tool drift behind a green gate; the `per-agent-design-evaluation-gap` analysis names the same shape on the design-time side. Without a normative contract, every future agent-surface-touching feature inherits the recurrence risk. |
| **Why this** | The four-condition trigger directly mirrors the four-dimension pattern the gap analysis identifies (`per-agent-design-evaluation-gap` §2). The full-inventory row count makes "evaluated by absence" structurally impossible. The positive-evidence-string discipline forces substance not presence. The advisory+human seam preserves the predicate-vs-substance separation that T-003's 0/6 mandate-as-artifact finding (C-0257) warns must not collapse. |
| **Known unknowns** | Triggers 3 and 4 are interpretive; the advisory predicate is a first-cut heuristic that may produce false positives or false negatives until override-event data accumulates. The first ~3 agent-surface-touching feature runs are the calibration corpus. |
| **Kill criteria** | If, after the next ~3 agent-surface-touching feature runs, the matrix discipline demonstrably increases authoring time beyond NFR-7's 30-min-at-100-agents budget without preventing any detectable defect, the FR-6 cell-granularity default (positive-evidence-required) is revisited. If override-events accumulate at a rate that suggests the trigger conditions themselves are wrong (>30% override rate sustained across N≥3 runs), the four-condition trigger is re-litigated. |

## Rationale

The contract surface above is the lowest-cost, highest-leverage normative recording of FR-6 + D-5 + D-8 that the design-composer can author. Five rationale strands:

1. **The four-condition trigger derives from observed defect surface, not abstract reasoning.** The `per-agent-design-evaluation-gap` §2 enumerates exactly four dimensions on which the gap manifests: tools, skills, model, effort. Each maps to one of the four trigger conditions. A narrower trigger (e.g., file-diff only) would replay the same defect on the non-file-diff dimensions.

2. **Full-inventory row count is the only structural defense against "evaluated by absence."** The original defect was 28 agents evaluated by absence (no row, no consideration). Requiring exactly-N rows where N = current agent file count makes absence detectable: any row count below N means an agent was skipped.

3. **Positive-evidence-string discipline mirrors FR-8's active-framing posture.** A bare `no-change` cell is structurally indistinguishable from "never evaluated." The evidence string IS the substance test for whether the per-agent consideration FR-8's active Principle 9 requires actually happened.

4. **Hybrid predicate+human seam preserves substance discipline.** T-003 verified across 6 platforms that mechanical-mandate-as-artifact is novel (C-0257). The hybrid keeps cheap pre-screening cheap (predicate handles triggers 1 and 2 deterministically) and keeps authoritative judgment human (designer ratifies triggers 3 and 4). Collapsing them into a single mechanical gate is the exact failure mode T-003 names.

5. **Override-event logging makes the predicate tunable without re-litigating the contract.** Silent overrides leave no audit trail. Logged overrides become the corpus future predicate-tuning reads.

## Options Considered

**Option A — Mechanical-predicate only, no human ratification (REJECTED).** Trigger 3 and 4 require interpretive reads (the predicate cannot reliably tell "design indicates one or more existing agents will load" from "design names a skill the predicate could possibly load"). Predicate-only forces every interpretive trigger into one of two failure modes: false-positive (matrix mandated when not needed; authoring burden creep) or false-negative (matrix skipped when needed; recurrence). 0/6 surveyed platforms enforce mechanical-mandate-as-artifact (C-0257); the platform consensus is against this option.

**Option B — Human-judgment only, no mechanical advisory (REJECTED).** Wastes the FR-7 table's mechanical parseability (C-0071). Forces the human to read the whole synthesis.md Skill-Coverage Decisions section every run before deciding whether the matrix is needed. Inconsistent application across runs is the predicted outcome.

**Option C — Three-dimension matrix (tools / model / effort), folding skills into tools (REJECTED).** The IC OI-9 resolution explicitly normalized the parent's "four-with-prompt-body folded in" phrasing to **five-explicit** (tools, skills, model, effort, prompt body). Folding obscures the skills dimension (which is independently load-bearing per ADR-0040's narrowed-allowlist precedent).

**Option D — Matrix optional; advisory-only (no design-time block) (REJECTED).** Re-creates the parent defect: optional artifacts are skipped under deadline pressure; the discipline becomes aspiration not structure. The design-time block at Design Composition close is the lever; removing it removes the contract.

**Option E (CHOSEN) — Four-condition trigger + full-inventory matrix + advisory predicate + human ratification + override logging.** Combines the strengths of A and B without their failure modes. Recommended.

## Consequences

**Positive:**

- The `28 agents evaluated by absence` failure mode is structurally impossible: any row-count divergence from `.claude/agents/*.md` is a `BLOCKER` finding.
- Triggers 1 and 2 fire deterministically; mechanical evidence is logged.
- Triggers 3 and 4 fire with human judgment recorded; future tuning has data.
- The matrix doubles as the substance test for FR-8's active Principle 9.
- The contract is dogfooded on its own run: R2a authors `working/feature/pipeline-design-time-discipline-r1/agent-roster-impact-matrix.md` as a Plan-stage deliverable.

**Negative / cost-bearing:**

- Authoring burden grows linearly with agent inventory (37 agents → ~11 min per NFR-7 extrapolation; 100 agents → ≤30 min). Kill criteria above bound this risk.
- Override events accumulate metadata in `state-transitions.log`; per ADR-0044 v1 the log is free-string-tolerant but the volume increases.
- The advisory predicate is greenfield (no precedent in existing audit catalog); its calibration depends on the first ~3 run corpus.

**Neutral / observability:**

- Every future feature run inherits the discipline; no migration burden on past runs.

## Architecture Impact

| Layer / artifact | Impact |
|---|---|
| `.claude/agents/design-claude-code.md` | Phase 2 procedure extension: new mandatory output. Cross-references FR-8's active Principle 9. |
| `.claude/skills/recipe-feature-pipeline/SKILL.md` | Outputs table for design-cc gets the matrix row. Design Composition close gate refuses if trigger fired and matrix absent. |
| `.claude/skills/auditing-subagents/scripts/check_feature_touch_predicate.py` | New advisory predicate (greenfield). |
| `.claude/skills/auditing-subagents/scripts/audit_feature_touch_coverage.py` | New SA-14 audit script (per ADR-0065 sibling work) — packaging-time backstop. |
| `.claude/skills/KB-documentation-criteria/references/templates/agent-roster-impact-matrix-template.md` | New template (the matrix's canonical shape). |
| `.claude/skills/KB-cc-design/references/principles.md` (Principle 9) | Mutual cross-reference per FR-8 AC-FR-8-b. |
| `.claude/skills/auditing-shared/scripts/log_state_transition.py` | Accepts the new `TRIGGER_OVERRIDE` value without code change (free-string per ADR-0044 v1). |
| `.claude/skills/KB-documentation-criteria/references/templates/state-transitions-log-entry-template.md` | Documentation update: `TRIGGER_OVERRIDE` enumerated as a valid `transition_name`. |

## Implementation Guidance

Principle-only. Procedures live in the Plan.

- **Compose the predicate as a no-op-on-failure tool.** If the predicate cannot parse the Skill-Coverage Decisions section (e.g., section absent because the feature introduces no new concepts), it MUST emit "no trigger fired (interpretive triggers inapplicable)" rather than raise. False-negatives are recoverable via human ratification; predicate crashes are not.
- **The matrix template MUST surface the positive-evidence-string requirement in the table header.** Designers should not need to read the contract to know bare `no-change` is insufficient — the template's per-cell scaffold shows the `<value> — <evidence>` shape.
- **Override events MUST be machine-readable.** The `context` field carries `trigger_condition: <1|2|3|4>; rationale: <one-line>; advisory_predicate_output: <yes|no>`. Future tuning depends on the structure being parseable.
- **Pre-deliverable-packaging audit (SA-14) MUST be advisory-of-presence-only, not substance.** The packaging-time backstop checks that the matrix exists and has the right row count — not that the evidence strings are good. Substance is the Design Composition + reviewer concern.

## Related Information

**Cross-references:**

- **FR-6** (`pipeline-design-time-discipline-r1` PRD) — the mechanism this ADR canonicalizes.
- **AC-FR-6-a / -b / -c / -d** — the acceptance criteria this contract satisfies.
- **NFR-7** — matrix authoring-time budget (30 min at 100 agents).
- **NFR-8** — clear failure messages (rule / target / divergence / next_action).
- **ADR-0017** — `shared-document-reviewer` invocation 3 reviews the matrix.
- **ADR-0040** — Serena narrowed-allowlist precedent; the canonical exemplar of the gap this contract closes.
- **ADR-0044** — state-transitions log v1 (free-string `transition_name`).
- **ADR-0065** (sibling, this run) — FR-7 skill-coverage trifecta hybrid; trigger condition 4 reads ADR-0065's Skill-Coverage Decisions section.
- **Synthesis decision D-5** — the hybrid advisory-predicate + human-ratification decision this contract embodies.

**Predecessor / inheritance:**

- The `per-agent-design-evaluation-gap` analysis (`Issues/per-agent-design-evaluation-gap/analysis.md`) is the defect-class source.
- The retroactive matrix at `Issues/per-agent-design-evaluation-gap/evidence/agent-roster-impact-matrix.md` (Track-A2 from `devcontainer-mcp-provisioning-r1`) is the exemplar shape; cells use `EXPLICIT_NO — <evidence>` per its retrofit context.
