---
doc_type: synthesis
feature_slug: execute-orchestrator-dispatch-mechanism-repair-r1
version: 1.0.0
status: ready-for-design-composer
generated: 2026-05-23T20:22:35Z
generated_by: synth-synthesizer
run_id: execute-orchestrator-dispatch-mechanism-repair-r1-20260523-202235
derived_from:
  - working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/synthesis/01-claims-codebase-analysis-report.json
  - working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/synthesis/01-claims-T-001-claude-code-subagent-tool-grant-semantics.json
  - working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/synthesis/01-claims-analysis-execute-orchestrator-dispatch-limitation.json
  - working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/synthesis/02-graph.json
  - working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/synthesis/03-critique.json
  - working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/synthesis/04-decision-frames.json
  - working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/synthesis/05-decision-substrate.json
companion_artifacts:
  - working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/synthesis/02-graph-summary.md
  - working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/synthesis/03-verifications.md
  - working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/prd-v1.md
  - working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/research-plan.md
  - Issues/analysis-execute-orchestrator-dispatch-limitation.md
audience: design-composer + per-layer cc Designer
audience_depth: engineering
---

# Synthesis — execute-orchestrator Dispatch Mechanism Repair (r1)

## 1. Executive Summary

The Synthesis fan-in for `execute-orchestrator-dispatch-mechanism-repair-r1` is anchored on two settled facts and one live design decision. The settled facts are `dispatch_supported: false` and `kill_criterion_triggered: 2`: Claude Code's sub-agents cannot dispatch other sub-agents at runtime, even when `Agent` is declared in the `tools:` frontmatter array (claim T-0001, verified across three independent Anthropic primary sources; claim T-0002, deductive consequence verified per PRD FR-2). These resolve the hypothesis chain in `analysis-execute-orchestrator-dispatch-limitation.md` §4.1 (harness-restriction was the "most likely" hypothesis; T-001's documentation evidence confirms it as deliberate harness design) and commit the feature to the FULL repair pathway.

The live design decision (D-001) is the §6 option selection. Both the framer and the substrate analysis recommend **option (a) — flatten dispatch hierarchy** as the load-bearing choice. Option (b) (retire execute-orchestrator) escapes the PRD FR-4 8-file inventory by 5+ files and breaks the state-transitions-log v1 `invoking_agent` invariant; option (c) (Bash-script dispatch) degrades the specialist-isolation audit-trail (the very property the repair must preserve) for the same outside-inventory cost as (a). Four supporting decisions follow: D-002 recommends two-session FR-6 verification to honor the F-7 mid-session agent registry constraint; D-003 removes the parallel `Agent` declaration from `execute-finalize-reconciler` in lockstep with the primary repair; D-004 closes the recipe-feature-pipeline canonical-reference schema gap in the same plan phase as D-001 (the two share `recipe-feature-pipeline/SKILL.md`); D-005 defers the documentation-conventions ADR to a separate feature. F-7 is novel, single-instance, and constrains downstream verification sequencing — design-composer and plan-author must respect it.

---

## 2. Anchor Evidence

The two anchor claims (T-0001, T-0002) underwrite the entire feature; together they convert §4.1 of the original analysis from "most likely" hypothesis into settled fact and trigger PRD FR-2 kill-criterion-#2.

### 2.1 T-0001 — `dispatch_supported: false`

**Claim:** Claude Code sub-agent -> sub-agent dispatch is not supported at runtime, even when the sub-agent declares `Agent` in its `tools:` array (claim T-0001; T-001 research-note frontmatter line 13; critique verdict: verified, confidence: high).

Three independent Anthropic-controlled primary sources corroborate the claim. The critique verified each URL, section, and verbatim quote on 2026-05-23:

| # | URL | Section | Verbatim quote (≤15 words) | Length |
|---|---|---|---|---|
| 1 | https://code.claude.com/docs/en/sub-agents | "Choose between subagents and main conversation" | "Subagents cannot spawn other subagents." | 5 words |
| 2 | https://code.claude.com/docs/en/agent-sdk/subagents | "Subagents in the SDK / Programmatic definition" | "Subagents cannot spawn their own subagents. Don't include Agent in a subagent's tools array." | 14 words |
| 3 | https://github.com/anthropics/claude-code/issues/29677 | Issue title | "Task->Agent tool rename in v2.1.63 breaks hook payloads" | 9 words (rename-date corroborator only) |

The first two are prescriptive ("Don't include Agent in a subagent's tools array" is direct developer instruction); the third corroborates only the v2.1.63 Task -> Agent rename date and is not load-bearing for the dispatch finding. T-001's Finding F-4 (lines 110–116) exhaustively enumerates the documented frontmatter field surface (24+ fields including `permissionMode`, `mcpServers`, `hooks`, `maxTurns`, `skills`, `memory`, `effort`, `background`, `isolation`, `color`, `initialPrompt`) plus the only two relevant environment variables (`CLAUDE_CODE_FORK_SUBAGENT`, `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS`) and finds no enable-nesting affordance. Fork mode docs are explicit: "A fork cannot spawn further forks." (T-001 line 116, paraphrased per one-quote-per-URL discipline).

Adversarial probes recorded in `03-critique.json` confirm: (a) no undocumented harness flag is known to enable nesting; (b) Anthropic has no incentive to falsely publish this restriction (it constrains product expressiveness rather than expanding it); (c) the absence of any "enable-nesting" flag across the exhaustive field enumeration is itself evidence — Anthropic explicitly closes the affordance and documents alternatives (Skills, chain-from-main, agent teams) instead.

### 2.2 T-0002 — `kill_criterion_triggered: 2`

**Claim:** kill-criterion-#2 fires per PRD FR-2 because the dispatch limitation is confirmed with no in-band path to fix sub-agent -> sub-agent dispatch, so FULL repair proceeds (claim T-0002; T-001 line 14; PRD FR-2; critique verdict: verified, confidence: high).

This is a deductive consequence of T-0001 plus PRD FR-2's gating definition ("the analysis is confirmed: no in-band path to fix it; FULL repair proceeds", T-001 executive summary line 48 citing FR-2 verbatim). Independent corroboration: AN-0069 from `analysis-execute-orchestrator-dispatch-limitation.md` reaches the same disposition from the original analysis source. The two sources agree the trigger expands repair scope (rather than minimizing it), so there is no benefit-of-the-doubt concern.

### 2.3 Resolution of DISSENT-1

`analysis-execute-orchestrator-dispatch-limitation.md` §4.1 (claims AN-0041..AN-0046) hypothesized "harness-restriction" as "most likely" but did not commit; T-001's Findings F-1 through F-4 confirm the hypothesis with documentation evidence. The critique records this as `verdict: resolved_not_dissent` — one-way supersession, not competing perspectives. The graph captures the resolution as edge `E-0009 supersedes E-0065` with supporting claims `[T-0001, T-0003, T-0004, T-0050, AN-0041]`. Downstream artifacts should present the resolution as settled, not as ongoing disagreement.

## 3. The 5 Decision Frames

The framer (`04-decision-frames.json`) and substrate (`05-decision-substrate.json`) agree on all five recommendations. The substrate analysis surfaces one new sequencing insight (D-001 and D-004 share `recipe-feature-pipeline/SKILL.md`) and one new schema-invariant consideration that strengthens the case against D-001 option (b) (state-transitions-log v1 `invoking_agent` invariant breaks).

### 3.1 D-001 — §6 dispatch mechanism choice (architectural, ADR-worthy)

**Recommendation:** option (a) — flatten dispatch hierarchy.
**Class:** architectural | **Reversibility:** one_way | **Blast radius:** tenant | **RICE:** 21.0 (R=35, I=3.0, C=0.8, E=4.0).
**Routing:** primary = ADR (design-composer authors); secondary = Blueprint cc-design subsection.

**Framing.** T-001 (claim T-0061) explicitly says the Designer's choice among PRD §6 options is unconstrained by T-001's findings — so this is a true design decision, not a forced consequence. The differentiator is the codebase-analysis-report's per-option blast-radius enumeration (claims CR-0095..CR-0109), surfaced by the framer as evidence-not-pre-decision per DISSENT-5's resolution.

**Recommended — option (a) Flatten dispatch hierarchy.** `recipe-feature-pipeline/SKILL.md` becomes the top-level dispatcher invoking the four specialists (`execute-task-code-producer`, `execute-task-quality-handler`, `execute-phase-quality-reviewer`, `execute-finalize-reconciler`) directly via `Agent` at the main-conversation level (where dispatch IS supported). `execute-orchestrator.md` is **retained** but re-scoped as an advisory / state-machine reference; its YAML frontmatter `Agent` tool grant is removed (parallel cleanup to D-003). The 14-row state machine relocates into a new "Execution Phase Dispatch" section of `recipe-feature-pipeline/SKILL.md`. `checkpoint.json` fields stay in their current location (NFR-6-a satisfied). Affected: 3 in-inventory + 1 outside-inventory = 4 files; AC-FR-4-a open-item count = 1; effort ~3 PW.

**Rejected — option (b) Retire execute-orchestrator entirely.** Escapes the FR-4 8-file inventory by 5+ files: `KB-documentation-criteria/SKILL.md` (template-assignment table per CR-0097), `state-transitions-log-entry-template.md` (CR-0079/CR-0080/CR-0135 — `invoking_agent` v1 invariant currently hard-coded to "execute-orchestrator"), `pipeline-run-summary-template.md` (CR-0098), `quality-reconciliation-log-template.md` (CR-0101), `smoke_test_auditing_shared.py` (CR-0102), and `auditing-codespaces/SKILL.md` (CR-0103). Triggers AC-FR-4-a scope-expansion gate with the widest possible operator surface and conflicts with PRD FR-4 (graph edge `E-0014 conflicts_with E-0032`, 4 supporting claims). **New substrate insight:** breaking the state-transitions-log v1 `invoking_agent` invariant promotes D-004 to ADR-worthy schema-ownership transfer — a non-trivial second-order cost the framer's frame did not fully surface. Roughly 2× the effort of (a) for the same functional outcome.

**Rejected — option (c) Bash-script dispatch surface.** Mechanism is physically possible (execute-orchestrator's runtime tool surface includes Bash per E-0012), but introduces a new indirection layer: specialists invoked via Bash sub-process rather than agent-graph dispatch. The harness's per-agent transcript / per-agent state-transitions logging is bypassed — the script becomes the audit boundary, not the agent. AN-0037 names this as "real audit-trail losses, not just cleanliness". Equivalent outside-inventory cost to (a) (1 file per CR-0109) but lowest pattern fidelity. T-001 (claim T-0064) treats (c) as physically possible but not preferred; Anthropic's documented alternatives (Skills, chain-from-main) are stronger if indirection is desired.

**Carry-through risks.**
- DISSENT-2: every artifact produced by D-001 (Blueprint, ADRs, Plan) MUST cite ADR-0017 + ADR-0033 (NOT ADR-0034) for the 4-cycle cap + symmetric D-12 application.
- DISSENT-5: the recommendation against (b) is grounded in blast-radius evidence, not a pre-decision; Designer retains discretion subject to AC-FR-4-a operator disposition.
- Hard-constraint adjacency: NFR-5-a (canonical-reference documentation gap closure) — option (a) requires `recipe-feature-pipeline/SKILL.md` to absorb state-machine details (paired with D-004).

### 3.2 D-002 — F-7 handling for FR-6 verification (operational, Blueprint-only)

**Recommendation:** D-002.1 — two-session verification.
**Class:** operational | **Reversibility:** two_way | **Blast radius:** component | **RICE:** 2.0.
**Routing:** Blueprint constraint (verification-phase NFR); Plan phase-sequencing; potential PRD NFR amendment.
**ADR-worthy:** No (0/3 rules hold).

**Framing.** F-7 (`F-7 mid-session agent registry not hot-reloaded`, claim AN-0065 plus T-0046..T-0058) is a high-confidence single-instance observation: the harness loads its agent registry at session start and does not hot-reload mid-session. Newly-authored sub-agent files are not invocable in the same session that authored them. The critique's `f7_confidence_assessment` records `partially_verified` (mechanism explicit, population n=1).

**Recommended — D-002.1 two-session verification.** Plan-author sequences FR-6 with an explicit session boundary: an early phase authors any new test agents / synthetic minimal test feature files; a later phase begins with a session-restart prompt to the operator. T-001 lines 53–54 confirm "fresh session" is the documented sufficient remedy. No new harness behavior required. Effort ~0.5 PW.

**Rejected — D-002.2 session-restart-in-pipeline step.** Requires either a substrate-level harness change (Claude Code does not expose a programmatic session-restart hook) or an operator-in-the-loop mechanism that D-002.1 already achieves with less ceremony. No incremental benefit.

**Rejected as default — D-002.3 fragment verification across two pipeline runs.** Fragments kill-criterion-#2 closure across two feature run directories; doubles orchestration overhead. Preserve as fallback if single-run session-boundary scheduling proves infeasible.

**FR-6 implication.** The synthetic test feature MUST run in a fresh session. Plan-author cannot collapse the authoring task and the test-execution task into one phase.

**Carry-through risks.**
- DISSENT-4: the FR-6 synthetic-test SHOULD include a sub-question discriminating H-a (baseline-inheritance) vs H-b (memory-field auto-enable) for the Edit-tool mechanism. The codebase-research confirms execute-orchestrator declares `memory: project` (CR-0023), which supports H-b as likeliest — but a falsifying test (Edit-tool appearing without `memory:` declared) would settle it. Non-load-bearing for kill-criterion-#2 closure.
- F-7 is n=1; if the harness has per-session caching nuance beyond the error-message's framing, the verification protocol may need additional probes.

### 3.3 D-003 — Cleanup posture for execute-finalize-reconciler (implementation, Plan task)

**Recommendation:** D-003.1 — remove `Agent` declaration from `execute-finalize-reconciler.md` as part of this feature.
**Class:** implementation | **Reversibility:** two_way | **Blast radius:** component | **RICE:** 1.6.
**Routing:** Plan phase task; inline in main report (no ADR).
**ADR-worthy:** No (0/3 rules hold).

**Framing.** FR-5 sweep (claims CR-0001..CR-0067 batch B05+B07, critique verdict `stronger_than_extractor_flagged: affected set closed at 2`) found exactly two `Agent`-declaring sub-agents: `execute-orchestrator` (primary defect) and `execute-finalize-reconciler` (parallel defect, CR-0048..CR-0051 high-confidence inference). T-0072 confirms the `Agent` declaration is a misleading runtime no-op — cleanup-as-blocker applies.

**Recommended — D-003.1 remove in this feature.** One YAML frontmatter edit (~0.25 PW). Bundles naturally with D-001 option (a)'s `Agent`-removal from `execute-orchestrator` — both are dispatch-grant cleanups and SHOULD commit together. AN-0040 explicitly recommends broader cleanup.

**Rejected — D-003.2 inventory-only deferral.** Leaves a known parallel defect on the floor while shipping the primary repair. Re-incurs the FR-5 investigation cost in a follow-up.

### 3.4 D-004 — Schema gap closure (architectural, Plan + Blueprint NFR-5-a)

**Recommendation:** D-004.1 — close `recipe-feature-pipeline/SKILL.md` schema gap in lockstep with D-001 implementation.
**Class:** architectural | **Reversibility:** two_way | **Blast radius:** service | **RICE:** 28.8.
**Routing:** Plan phase task; Blueprint constraint (NFR-5-a). **Conditional ADR promotion** only if D-001 = (b).
**ADR-worthy under recommended path:** No.

**Framing.** Cluster 6 surfaces a pre-existing documentation gap: `recipe-feature-pipeline/SKILL.md` lines 96–128 reference a `checkpoint.json` schema that omits the execution-phase fields actually written in flight (`execution_pipeline_state_transitions`, `execution_mode`, `execution_pipeline_cycle_counters`, claims CR-0061..CR-0080 batch B08 verified by direct Grep). NFR-5-a explicitly requires the canonical reference to update in lockstep with any §6 option change. The documented schema is already stale independently of D-001.

**Recommended — D-004.1 close in lockstep.** Edit `recipe-feature-pipeline/SKILL.md` lines 96–128 to: (1) add the three missing execution-phase fields; (2) document the state-transitions.log v1 `invoking_agent` invariant (CR-0079/CR-0080/CR-0135); (3) document `void: true` + `void_reason` and `-prime` transition-name suffixes as de facto v1 extensions (closes OI-CR-D in lockstep). NFR-6-a (no-artifact-migration) satisfied — documentation-only. Effort ~1 PW.

**Rejected — D-004.2 defer.** Violates NFR-5-a lockstep requirement (option (a) DOES touch `recipe-feature-pipeline/SKILL.md`, so NFR-5-a fires). Known-defect-on-the-floor anti-pattern even if NFR-5-a didn't fire.

**Conditional ADR promotion.** If D-001 = (b) is selected against framer/substrate recommendation, schema ownership transfers (execute-orchestrator-owned -> recipe-feature-pipeline-owned) and the state-transitions.log v1 `invoking_agent` invariant must be revised. In that conditional path, D-004 promotes to architectural and design-composer authors an ADR for the schema-ownership transfer. Under the recommended D-001 = (a) path, **no ADR promotion is required**.

### 3.5 D-005 — ADR mis-attribution discipline (deferred)

**Recommendation:** D-005.1 — defer to a separate documentation-conventions feature. Already-corrected via surgical edit.
**Class:** operational | **Reversibility:** two_way | **Blast radius:** component | **RICE:** 0.625.
**Routing:** open-item; Synthesizer note (OI-FRAMER-1) carries the correction forward.
**ADR-worthy:** No (0/3 rules hold).

**Framing.** DISSENT-2 surfaced documentary mis-attribution (PRD FR-3-c cites ADR-0034 for symmetric D-12; correct citation is ADR-0017 + ADR-0033 per direct Grep on ADR file contents). Already corrected via surgical edit and dissent_evidence in the synthesis; the open question is whether to author a conventions ADR to prevent recurrence.

**Recommended — D-005.1 defer.** The corrective action is already encoded in OI-FRAMER-1: downstream artifacts MUST cite ADR-0017 + ADR-0033 going forward. A conventions ADR formalizes existing practice; deferring respects feature scope discipline (FR-2 + FR-4 + FR-5 + FR-6 + NFR-5-a only). Aligned with user-memory preference: "belongs in a separate feature, not bundled in dispatch-repair".

**Rejected — D-005.2 bundle in this feature.** Scope creep; widens beyond kill-criterion-#2 closure without strengthening it.

## 4. F-7 Detailed Treatment

F-7 was not in the original PRD scope. It was deliberately allowed to surface during the in-pipeline investigation (T-001) per the operator's routing decision. Because F-7 changes how downstream verification must be sequenced — and because it is single-instance, novel, and only weakly substituted for by documented alternatives — it gets its own treatment here.

**What F-7 is.** During execution of probe-dispatch-test-r1 / r2 (claims T-0046..T-0058), the harness produced an explicit error enumerating its loaded agent set and declining to invoke any newly-authored sub-agent file present on disk in the current session. The mechanism is explicit in the error message: the agent registry loads at session start and does not hot-reload. The remedy is also explicit (T-001 lines 53–54): fresh session.

**Why F-7 is novel.** None of the prior runs in this repository surfaced F-7 because none authored a sub-agent and then attempted to invoke it within the same session. The mechanism was latent until the T-001 probe forced the boundary condition. The critique records F-7 as `partially_verified` — mechanism explicit, population n=1.

**What F-7 constrains downstream.** Three artifacts depend on F-7:

1. **FR-6 verification protocol (D-002).** Authoring and execution of the synthetic minimal test feature MUST cross a session boundary. The two-session pattern (author in session 1, execute in session 2) is the recommended path.
2. **Plan phase sequencing (OI-FRAMER-3).** Plan-author MUST place an operator-facing session-restart instruction between any agent-authoring task and the corresponding agent-invoking task.
3. **PRD NFR amendment (optional but recommended).** The session-boundary constraint may warrant formalization as an NFR so future features encountering similar agent-authoring sequences inherit the discipline.

**Why two-session verification is the recommended path.** Alternatives are weaker. A pipeline-internal session-restart primitive (D-002.2) would require either an Anthropic-side harness change or operator-in-the-loop coordination that D-002.1 already achieves. Two-run fragmentation (D-002.3) doubles orchestration overhead for equivalent F-7 mitigation. The two-session pattern matches the only documented Claude Code remedy and adds zero new substrate dependencies.

**Carry-through to FR-6 design.** Per OI-FRAMER-2, the synthetic test SHOULD also include a sub-question discriminating H-a (baseline-inheritance) vs H-b (memory-field auto-enable) for the Edit-tool mechanism (DISSENT-4). Codebase-research (CR-0023) confirms `execute-orchestrator` declares `memory: project`, supporting H-b as likeliest; a sub-agent without `memory:` exhibiting the Edit-tool addition would falsify H-b. This is non-load-bearing for kill-criterion-#2 closure but valuable for future cc-design discipline.

## 5. Cross-Frame Sequencing Constraints

Two cross-frame sequencing constraints surface from the substrate analysis. Both are load-bearing for plan-author.

**Constraint 5.1 — Shared file pressure on `recipe-feature-pipeline/SKILL.md`.** Both D-001 option (a) (the new Execution Phase Dispatch section, ~14-row state machine + dispatch loop) and D-004 option (D-004.1) (the schema-section edit at lines 96–128) edit the same file. Plan-author MUST sequence these coherently. Recommended: same phase, dependent tasks (D-004 schema closure first to stabilize the documented schema, then D-001 dispatch-section absorption), OR a single combined task with explicit sub-sections. This is the single most important cross-decision insight from the substrate analysis and was not surfaced by the framer alone.

**Constraint 5.2 — Bundled `Agent`-removal commit.** Both D-001 option (a) (remove `Agent` from `execute-orchestrator.md` tools array) and D-003 option (D-003.1) (remove `Agent` from `execute-finalize-reconciler.md` tools array) are dispatch-grant cleanups. Plan-author SHOULD bundle them in one commit; the commit message documents the FR-5 sweep closure ("affected set closed at 2").

**Constraint 5.3 — F-7 session boundary (D-002).** If any new sub-agent file is authored as part of this feature (likely for FR-6 synthetic-test verification), the plan MUST place a session-restart instruction between the authoring task and the test-execution task. The two cannot collapse into one phase.

**Constraint 5.4 — DISSENT-2 carry-through.** Every artifact produced by this feature (Blueprint, ADRs, Plan, PRD amendments, test artifacts, finalize-reconciler updates) MUST cite ADR-0017 + ADR-0033 for the 4-cycle cap + symmetric D-12 application. The ADR-0034 mis-attribution from the PRD FR-3-c MUST NOT propagate.

## 6. Routing to Downstream Stages

**6.1 design-composer (per FR-5).** Authors the ADR(s) for this feature. The framer flags D-001 as the single ADR-worthy decision; design-composer SHOULD plan to author one ADR capturing the rationale for option (a) over (b) and (c) — anchored on (i) FR-4 8-file inventory compliance, (ii) state-transitions-log v1 invariant preservation, and (iii) specialist-isolation audit-trail preservation. **A second ADR may also be warranted** to codify a project-wide convention informed by T-001's findings — provisional title: "Sub-agents MUST NOT declare `Agent` in their `tools:` array (Claude Code substrate constraint)." This second ADR would generalize the D-001 + D-003 cleanups into a roster-wide rule. Composer decides whether the convention rises to ADR scope or is captured in a skill / contributor doc. The per-layer cc-design subsection consumes this synthesis as the rationale brief.

**6.2 per-layer cc Designer.** Consumes this synthesis as the rationale brief for the cc-design.md subsection. Load-bearing inputs: §3.1 (D-001 with rejection rationales), §4 (F-7 treatment), §5 (cross-frame sequencing). The four specialists' isolation boundaries remain — only the dispatcher changes location.

**6.3 plan-author.** Consumes §5 (cross-frame sequencing) directly. Load-bearing inputs: (a) shared-file pressure on `recipe-feature-pipeline/SKILL.md` requires task sequencing; (b) F-7 session boundary cannot be collapsed; (c) `Agent`-removal commits should bundle; (d) DISSENT-2 carry-through to every artifact. Open items OI-FRAMER-1, OI-FRAMER-3 are owned here.

**6.4 test-acceptance-author + test-phase-validator-author.** Consume §3.2 (D-002) + §4 (F-7 treatment) for the FR-6 synthetic minimal test feature design. The protocol document is the single load-bearing artifact (substrate `most_expensive_single_edit` for D-002). Must encode: (a) F-7 session-boundary constraint, (b) H-a vs H-b sub-question per OI-FRAMER-2, (c) two-session operator instruction.

**6.5 finalize-reconciler (downstream consumer).** Per DISSENT-2 carry-through, finalize-reconciler will receive artifacts citing ADR-0017 + ADR-0033 (not ADR-0034) for the 4-cycle cap + symmetric D-12 application. Reconciler should verify this across all produced artifacts as part of its consistency sweep.

## 7. Dissents Carried Forward

The critique recorded nine dissent entries; the framer disposed of them as follows. design-composer and plan-author MUST respect the carry-through actions on DISSENT-2, DISSENT-4, and the F-7 confidence assessment.

| Dissent ID | Description | Critique verdict | Carried as |
|---|---|---|---|
| DISSENT-1 | Root-cause hypothesis resolution (T-001 supersedes AN §4.1) | `resolved_not_dissent` | Settled. Graph edge `E-0009 supersedes E-0065`. No further action. |
| DISSENT-2 | ADR-0033 vs ADR-0034 attribution for symmetric D-12 | `resolved_documentary_correction` | **Active carry-through.** OI-FRAMER-1: every downstream artifact MUST cite ADR-0017 + ADR-0033. |
| DISSENT-3 | 35 vs 36 agent count | `resolved_minor_correction` | OI-CR-F / OI-FRAMER-4. Non-blocking. Update any documentation that mentions agent counts. |
| DISSENT-4 | Edit-tool mechanism (H-a vs H-b) | `dissent_preserved_non_load_bearing` | **Active carry-through.** OI-FRAMER-2: FR-6 synthetic-test SHOULD include the H-a vs H-b sub-question. |
| DISSENT-5 | §6 design-option pre-disposition | `evidence_not_decision` | Surfaces in D-001 as blast-radius evidence. Designer retains discretion subject to AC-FR-4-a. |
| F-7 confidence | F-7 single-instance observation | `partially_verified` (n=1) | **Active carry-through.** OI-FRAMER-3: plan-author MUST sequence FR-6 verification across a session boundary. |
| (others) | Three additional batch-level dissent flags resolved at verification stage | resolved | See `03-verifications.md`. No downstream action. |

Of the nine, three require active downstream action; one is the surfaced soft-pressure evidence for D-001; one is settled by supersession; the rest are minor corrections or batch-level resolutions.

## 8. Limitations

- **F-7 is single-instance (n=1).** The mechanism (registry loaded at session start; no hot-reload) is documented by the harness's own error message, but the population is one observation. The recommended verification protocol (D-002.1) inherits this limitation: it assumes the documented remedy ("fresh session") is sufficient. If the harness has per-session caching nuance beyond the error-message framing, the protocol may need additional probes. Plan-author should preserve this as a known limitation in the FR-6 protocol doc.
- **Absence-of-feature claims for documented workaround.** T-001 reports no documented "enable-nesting" frontmatter field, flag, or environment variable across exhaustive enumeration of the published Claude Code surface. This is an absence-of-feature claim — its falsification requires only a single undocumented affordance that the published docs did not surface. The probability is bounded by Anthropic's documentation discipline rather than mathematically zero. Adversarial-probe verification in `03-critique.json` records this as the strongest evidentiary posture available for an absence-of-affordance claim, but it remains an absence claim.
- **DISSENT-2 propagation is operator-discipline-bounded.** The corrective action (cite ADR-0017 + ADR-0033, not ADR-0034) is encoded in OI-FRAMER-1 and must propagate to every downstream artifact: Blueprint, ADRs, Plan, PRD amendments, test artifacts, finalize-reconciler outputs. The propagation is bounded by author discipline and reviewer attention rather than by a Grep-style invariant check. design-composer, plan-author, test-* authors, and finalize-reconciler MUST each verify their outputs.
- **H-a vs H-b for the Edit-tool mechanism remains open** (DISSENT-4). Both hypotheses survive verification with documentation backing; codebase-research (CR-0023) confirms `execute-orchestrator` declares `memory: project`, which supports H-b — but the hypothesis is not refuted. Resolution is deferred to FR-6's synthetic test. Non-load-bearing for kill-criterion-#2 closure.
- **D-005 deferral risk.** The recurrence risk for documentation mis-attribution is mitigated by OI-FRAMER-1 propagation but is not eliminated. If a future feature is authored without inheriting OI-FRAMER-1's discipline, the same mis-attribution pattern could recur. Bounded; not blocking this feature.
- **No hard constraints declared by run manifest** — the feature pipeline does not surface a separate `manifest.constraints.hard_constraints[]` list; the load-bearing constraints (PRD FR-4 8-file inventory, NFR-5-a lockstep, NFR-6-a no-migration, AC-FR-4-a scope gate, FR-2 kill criteria, F-7 session boundary) are documented in the PRD and are honored by the recommendations in §3 and the sequencing in §5. The Constraints Honored treatment is folded into the per-decision risks lines and §5 rather than presented as a separate section.

## 9. Source / Claim Inventory

| Metric | Value |
|---|---|
| Total claims (3 sources merged) | 296 (CR=146, T=76, AN=74) |
| Verified | 273 |
| Partially verified | 11 |
| Dissent (preserved) | 9 |
| Unverifiable | 0 |
| Single-sourced (transparency-flagged) | 3 |
| Graph entities | 105 |
| Graph edges (relations) | 121 |
| Hand-curated topical clusters | 7 |
| Orphan-entity drops | 0 |
| Decision frames | 5 |
| ADR-worthy frames (framer + substrate confirmed) | 1 (D-001) |
| Conditionally ADR-worthy | 1 (D-004 if D-001=(b)) |
| Open items for downstream | 5 (OI-FRAMER-1..5) |

**Sources confirmed.**

| Source file | Claims | Source type | Role |
|---|---|---|---|
| `01-claims-codebase-analysis-report.json` (`CR-` prefix) | 146 | codebase-research (Grep-grounded) | Per-option blast-radius evidence; FR-5 sweep; schema-gap (cluster 6); ADR-attribution correction (DISSENT-2) |
| `01-claims-T-001-claude-code-subagent-tool-grant-semantics.json` (`T-` prefix) | 76 | Anthropic-doc research (T-001) | Anchor evidence for T-0001 / T-0002; F-7 mechanism; H-a/H-b hypotheses |
| `01-claims-analysis-execute-orchestrator-dispatch-limitation.json` (`AN-` prefix) | 74 | Source analysis (`Issues/analysis-execute-orchestrator-dispatch-limitation.md`) | Original defect framing; §6 option enumeration; hypothesis chain superseded by T-001 |

**Top-claim entities** (full list in `02-graph-summary.md`): `Agent tool` (E-0008, 47 claims, bridge across all 3 sources), `execute-orchestrator` (E-0001, 55 claims), `Claude Code` (E-0007, 25 claims), `Anthropic Claude Code sub-agent documentation` (E-0046, 20 claims), `execute-finalize-reconciler` (E-0002, 19 claims), `dispatch_supported: false` (E-0009, 18 claims), `single-agent fallback mode` (E-0043, 19 claims), `§6 option (b)` (E-0014, 17 claims), `F-7 mid-session agent registry` (E-0011, 13 claims).

---

## Provenance footer

- Synthesis run: `execute-orchestrator-dispatch-mechanism-repair-r1-20260523-202235`
- Stage: `synth-synthesizer / compose-report`
- Inputs (six stage outputs): `01-claims-*.json` (3 files); `02-graph.json` + `02-graph-summary.md`; `03-critique.json` + `03-verifications.md`; `04-decision-frames.json`; `05-decision-substrate.json`
- Validators run before write: B-cite (citation-presence — every assertion grounded in a `CR-` / `T-` / `AN-` claim id or a primary URL); B-constr (constraint-propagation — PRD FR-2 / FR-4 / FR-5 / FR-6 / NFR-5-a / NFR-6-a all honored or surfaced as explicit exceptions in §3 risks lines)
- Per FR-5 of the feature pipeline, ADRs are authored by design-composer (not by synth-synthesizer). This synthesis flags D-001 as ADR-worthy and provides the rationale brief; design-composer authors the ADR file.
