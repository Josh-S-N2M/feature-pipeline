---
id: SPLIT-pipeline-cross-artifact-discipline-r1
version: 1.0.0
status: terminal
doc_type: split-record
feature_slug: pipeline-cross-artifact-discipline-r1
generated: 2026-05-26T15:35:00Z
generated_by: recipe-feature-pipeline orchestrator
gate_decision_reference: Gate 4 (Blueprint Approval), 2026-05-26
---

# Split Record — pipeline-cross-artifact-discipline-r1 → R2a + R2b

## Decision

At Gate 4 (Blueprint Approval), the user chose to **split this feature into two separate feature-pipeline runs** rather than continue as a single bundle.

The watch-item the user named in the original brief — "if synthesis surfaces too many distinct decisions for the 4-cycle reconciliation cap, the natural split is R2a (design-time discipline) and R2b (gate/validator hardening). Surface this to me at the PRD or Design Composition gate if the open-item count threatens the cap" — fired at the codebase researcher's expansive 14-OI reading. The composer recommended continuing as single feature with a reversibility argument; the user chose split anyway, preferring the two halves to ship on independent timelines.

## Also resolved at Gate 4

The user ratified the PRD AC-FR-11-c enumeration correction: the §O posture discipline applies to all **5** post-ship deferral entries in the devcontainer-mcp-provisioning-r1-deferrals register (A-3, D-5, **E-2**, E-3, I-1), not the 4 the PRD originally listed. This ratification carries forward into the R2b follow-up run (FR-11 lives in R2b).

## Mechanism / FR assignment to each follow-up run

| Mechanism | FR | Original source | Goes to | Rationale |
|---|---|---|---|---|
| Design-realization audit dimension | FR-1 (H3) | Cross-artifact-divergence-detection-gap | **R2a** | Per the original brief's split membership; cross-cuts but design-time-leaning. |
| Protocol Conformance subsection | FR-2 (H6) | Cross-artifact-divergence-detection-gap | **R2b** | Per original split membership. |
| Cross-file consistency invariant catalog | FR-3 (H9) | Cross-artifact-divergence-detection-gap | **R2b** | Per original split membership. |
| `--with-mcp-reachability` rename + handshake | FR-4 (H1) | Cross-artifact-divergence-detection-gap | **R2b** | Per original split membership. |
| Live tool-surface drift detection | FR-5 (H8) | Cross-artifact-divergence-detection-gap | **R2b** | Per original split membership. |
| Agent-roster impact matrix artifact contract | FR-6 (B1) | Per-agent-design-evaluation-gap | **R2a** | Per original split membership. |
| Skill-coverage decision check at Synthesis/Design | FR-7 (B3) | Per-agent-design-evaluation-gap | **R2a** | Per original split membership. |
| Principle 9 active reframing | FR-8 (B2) | Per-agent-design-evaluation-gap | **R2a** | Per original split membership. |
| Blocks-X marker grammar | FR-9 (B4) | Per-agent-design-evaluation-gap | **R2a** | Per original split membership. |
| `auditing-subagents` matrix-missing rule | FR-10 (B5) | Per-agent-design-evaluation-gap | **R2a** | Per original split membership. |
| Event-triggered deferral discipline | FR-11 (§O) | Devcontainer-mcp-provisioning-r1-deferrals | **R2b** | Per original split membership. |

## ADRs authored in this run (5)

All 5 ADRs landed at canonical `adrs/` per ADR-0036 + ADR-0054 + ADR-0056. They remain valid architectural commitments and should be **inherited by the follow-up runs** rather than retracted, since each codifies a sound decision grounded in research and synthesis evidence. The runs that implement the FRs each ADR closes inherit the corresponding ADR.

| ADR | Closes | Inherited by |
|---|---|---|
| [ADR-0059 — Companion-file `.prescriptions.yaml`](../../../adrs/ADR-0059-adr-prescriptions-companion-file.md) | FR-1 design-realization audit | **R2a** |
| [ADR-0060 — Cross-file invariant catalog hybrid](../../../adrs/ADR-0060-cross-file-invariant-catalog-hybrid.md) | FR-3 PV-tier invariants | **R2b** |
| [ADR-0061 — Severity vocabulary bridge table](../../../adrs/ADR-0061-severity-vocabulary-bridge-table.md) | FR-1/4/5/9/10 (cross-cutting) | **Both R2a and R2b** (FR-1, FR-9, FR-10 are R2a; FR-4, FR-5 are R2b) |
| [ADR-0062 — MCP `tools/list` drift-detection pipeline](../../../adrs/ADR-0062-mcp-tool-surface-drift-detection-pipeline.md) | FR-5 four-stage drift detection | **R2b** |
| [ADR-0063 — Blocks-X marker grammar canonicalization](../../../adrs/ADR-0063-blocks-x-marker-grammar.md) | FR-9 marker grammar | **R2a** |

**ADR-0061 is the only genuinely cross-cutting one.** R2a and R2b both reference it; neither owns it exclusively. The bridge table at `KB-review-disciplines/references/severity-taxonomy.md` is authored once (whichever run runs first), and the other run inherits it.

## Recommended ordering for follow-up runs

**R2a first, R2b second** — for two reasons:

1. R2a establishes the agent-roster-impact-matrix.md artifact contract (FR-6) and the eat-own-dogfood discipline. R2b touches several agents (auditing-mcp, recipe-feature-pipeline orchestrator, KB-task-decomposition PV-author rubric) and will exercise the new matrix contract. Running R2a first means R2b's matrix is the discipline-correct version, not a retrofit.

2. ADR-0061 (severity bridge table) is touched by R2a's FR-1/9/10 AND R2b's FR-4/5. Running R2a first means R2b inherits a populated bridge table; running R2b first means R2a inherits a partially-populated table that R2a then completes. The former is cleaner.

## Artifacts the follow-up runs can inherit verbatim

Most of the upstream artifacts in this run are general enough that the two follow-up runs can cite them as prior context without re-running the corresponding stages:

| Artifact | Inheritability | Notes |
|---|---|---|
| `intent-clarification.md` | **Reference only** | Each follow-up run authors its own intent clarification scoped to its mechanism subset. |
| `prd-v2.md` | **Partial inheritance** | The FR sections corresponding to the run's mechanism subset are inherited; the run authors a slimmer PRD scoped to its FRs. |
| `research-plan.md` | **Reference** | The codebase-research scope and external research topics (T-001..T-004) are useful for both runs. Each follow-up run authors its own Research Plan but cites this one for KB-gap discipline. |
| `codebase-analysis.json` + `codebase-analysis-report.md` | **Full inheritance** | The 21 components, 21 dependency edges, blast-radius, mechanism-dependency table, and watch-item evidence are reusable. R2a uses the FR-1/3/6/7/8/9/10 + cross-cutting touch points; R2b uses the FR-2/3/4/5/11 + cross-cutting touch points. |
| `research-notes/T-001-tool-surface-drift-detection.md` | **R2b only** | Informs FR-5 drift detection. |
| `research-notes/T-002-design-realization-audit-prior-art.md` | **R2a only** | Informs FR-1 (in R2a per the split membership). |
| `research-notes/T-003-skill-coverage-rubric-patterns.md` | **R2a only** | Informs FR-7. |
| `research-notes/T-004-cross-file-invariant-catalog-patterns.md` | **R2b only** | Informs FR-3. |
| `synthesis.md` | **Reference** | The 10 decisions D-1..D-10 are partitionable: D-1, D-4, D-8 → R2a; D-2, D-7, D-9 → R2b; D-3, D-5 → R2a; D-6 (the split decision itself) → resolved by this record; D-10 (severity bridge) → cross-cutting via ADR-0061. |
| `cc-design.md` + `cc-dependencies.json` | **Partial** | The R2a follow-up cites the FR-1/6/7/8/9/10 sections; R2b cites the FR-2/3/4/5/11 sections. Each follow-up authors its own per-layer design. |
| `blueprint-v1.md` | **Reference only** | Each follow-up authors its own Blueprint scoped to its FRs and inheriting the relevant ADRs. |
| `synthesis/01-claims.json`, `02-graph.json`, `03-critique.json`, `04-decision-frames.json`, `05-implementation-strategies.json` | **Reference only** | Reusable as evidence backing for the inherited decisions. |
| `adrs/ADR-0059, ADR-0060, ADR-0061, ADR-0062, ADR-0063` | **Inherited** | Each follow-up run cites the relevant ADR(s) as inherited; no re-authoring needed. |

## Suggested follow-up-run slugs

- **R2a — design-time discipline**: `pipeline-design-time-discipline-r1` (the "r1" reflects that this is the first run of this slug; the original "r2" framing collapses now that we've split)
- **R2b — gate/validator hardening**: `pipeline-gate-validator-hardening-r1`

Alternative slug forms (if the user prefers a name that preserves the "R2" lineage):
- `pipeline-cross-artifact-discipline-r2a-r1`
- `pipeline-cross-artifact-discipline-r2b-r1`

The first form (clean slugs without the R2 lineage prefix) is cleaner; the second preserves the audit trail to this run if that's valuable for archeological reading later.

## Kickoff commands for the user

When ready to start the follow-up runs (Auto Mode optional):

```
# R2a — design-time discipline
/feature-pipeline pipeline-design-time-discipline-r1 --raw-request "Ship the design-time discipline half of the R2 bundle from pipeline-cross-artifact-discipline-r1: FR-1 (H3 design-realization audit), FR-6 (B1 agent-roster matrix), FR-7 (B3 skill-coverage check), FR-8 (B2 Principle 9 active reframing), FR-9 (B4 Blocks-X marker grammar), FR-10 (B5 auditing-subagents matrix-missing rule). Inherit ADR-0059, ADR-0061, ADR-0063 from the parent run. See working/feature/pipeline-cross-artifact-discipline-r1/SPLIT-RECORD.md for the split lineage and inheritable artifacts."

# R2b — gate/validator hardening (after R2a ships)
/feature-pipeline pipeline-gate-validator-hardening-r1 --raw-request "Ship the gate/validator hardening half of the R2 bundle from pipeline-cross-artifact-discipline-r1: FR-2 (H6 Protocol Conformance), FR-3 (H9 cross-file invariants), FR-4 (H1 reachability handshake), FR-5 (H8 drift detection), FR-11 (§O event-triggered deferral discipline including the ratified 5-row enumeration A-3, D-5, E-2, E-3, I-1). Inherit ADR-0060, ADR-0061 (now populated by R2a), ADR-0062 from the parent run. See working/feature/pipeline-cross-artifact-discipline-r1/SPLIT-RECORD.md."
```

## Status of this run

This run (`pipeline-cross-artifact-discipline-r1`) is **terminated at Gate 4** by user decision. Stages 8 (Architecture Audit), 9 (Plan Authoring), 10 (Tests), 11 (Cross-Artifact Audit), 12 (Task Decomposition), and 13 (Deliverable Packaging) are **not executed in this run**. They will execute independently in the two follow-up runs.

The artifacts in `working/feature/pipeline-cross-artifact-discipline-r1/` remain on disk as the source of truth for the split decision and as inheritable reference material for the two follow-up runs.

## Update history

- 2026-05-26 — Split decision recorded by orchestrator after user ratification at Gate 4.
