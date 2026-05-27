---
id: SYNTHESIS-pipeline-design-time-discipline-r1
version: 1.0.2
status: draft
doc_type: synthesis
feature_slug: pipeline-design-time-discipline-r1
derived_from:
  - working/feature/pipeline-design-time-discipline-r1/prd-v1.md
  - working/feature/pipeline-design-time-discipline-r1/synthesis/01-claims.json
  - working/feature/pipeline-design-time-discipline-r1/synthesis/02-graph.json
  - working/feature/pipeline-design-time-discipline-r1/synthesis/03-critique-inherited.json
  - working/feature/pipeline-design-time-discipline-r1/synthesis/04-decision-frames.json
  - working/feature/pipeline-design-time-discipline-r1/synthesis/05-implementation-strategies.json
  - working/feature/pipeline-design-time-discipline-r1/codebase-analysis.json
parent_run: pipeline-cross-artifact-discipline-r1
related_run: pipeline-gate-validator-hardening-r1
inherited_adrs: [ADR-0059, ADR-0061, ADR-0063]
generated: 2026-05-26
generated_by: synth-synthesizer
audience: design-cc (primary), design-composer (primary)
---

# Synthesis: Pipeline Design-Time Discipline (R2a)

## Executive Summary

R2a ships the design-time-discipline half of the parent run's split — six PRD mechanisms (FR-1, FR-6, FR-7, FR-8, FR-9, FR-10) that move per-agent design evaluation and ADR design-realization audit from aspiration to structural prevention (prd-v1.md §Overview, §Layer Scope). The inheritance posture is heavy and load-bearing: three accepted parent ADRs close the prescription-extraction question (ADR-0059), pin the severity-vocabulary bridge host (ADR-0061), and canonicalize the Blocks-X marker grammar (ADR-0063), so R2a does not re-derive those decisions (prd-v1.md §Inheritance Manifest). The 48-claim T-002 prior-art corpus (design-realization audit literature) and 56-claim T-003 prior-art corpus (skill-coverage rubric patterns) are inherited verbatim by reference from the parent's CoVe; R2a did NOT re-run critique (03-critique-inherited.json §verification-by-reference).

Eleven decisions sit between this synthesis and design-cc / design-composer. **Five are closed**: D-1 / D-4 by inherited ADRs (0059, 0063), D-6 by user split decision at parent Gate 4, D-10 partially-closed (host pinned in parent; this run authors the bridge content), plus the parent-resolved D-8 substance-vs-mandate framing carried forward (04-decision-frames.json §closed_vs_open). **Six are open** for design-composer to arbitrate: D-3, D-5, D-R2a-3, D-R2a-4, D-R2a-5 at Design Composition; D-R2a-6 at Plan authoring. All seven open-decision recommendations match the framer's recorded lean — no synthesizer-dissent (05-implementation-strategies.json §recommendation_divergence_from_framer_lean). The single most consequential R2a decision is **D-8 (FR-7 substance heuristic vs structural mandate)**: FR-7 is the heaviest entity in the R2a graph at 23 claim back-pointers, and the framing choice ripples through FR-7 ACs, the dogfood deliverable, and downstream consumer expectations (02-graph-summary.md §Top entities by claim count; 04-decision-frames.json D-8 §risks).

## Inheritance Manifest

R2a's inheritance shape is narrower than its parent because the parent's accepted ADRs already closed three load-bearing questions. The manifest below names each inherited artifact and what each parent-resolved decision means for R2a (prd-v1.md §Inheritance Manifest, expanded with graph anchors).

| Inherited artifact | R2a meaning |
|---|---|
| **ADR-0059** (`.prescriptions.yaml` companion-file schema) | Closes parent OI-A1. FR-1's contract points at the companion file rather than naming an open OI. Anchored by 9-of-9 unanimous companion-artifact convergence across surveyed production systems (T-002; C-0017, C-0018, C-0019, C-0020, C-0021) and the arXiv 2602.07609 44.57% LLM-misinterpretation finding that rules out the NLP-parse-of-prose branch (C-0128, C-0134, C-0144) (05-implementation-strategies.json D-1 §summary_paragraph). |
| **ADR-0061** (severity-vocabulary bridge table host) | Pins the canonical host at `.claude/skills/KB-review-disciplines/references/severity-taxonomy.md`. R2a authors the bridge content (see Severity Bridge Content section below). Cross-cutting with R2b (FR-4, FR-5) — R2b inherits R2a's populated content (prd-v1.md §Technical Considerations / Dependencies). |
| **ADR-0063** (Blocks-X marker grammar) | Closes parent OI-A5. FR-9's contract points at the canonical grammar `<!-- BLOCKS: <stage-slug>-completion -->` (uppercase token, colon-suffixed, HTML-comment container, optional em-dash-separated payload). Parser regex `<!--\s*BLOCKS:\s*([a-z0-9-]+)-completion(?:\s+—\s+[^\n]*)?\s*-->` is canonical (05-implementation-strategies.json D-4 §summary_paragraph). Realization location is a separate decision (D-R2a-3 below). |
| **T-002 research-note corpus** (48 inherited claims; design-realization audit prior art) | Inherited verbatim by reference from parent's CoVe (03-critique-inherited.json §T-002 verifications). Anchors FR-1's companion-file route and rules out NLP-parse. R2a did NOT re-run verification — load-bearing verifications carry forward unchanged. |
| **T-003 research-note corpus** (56 inherited claims; skill-coverage rubric patterns) | Inherited verbatim by reference (03-critique-inherited.json §T-003 verifications). 6 platforms verified W/H/A substance is well-trodden community ground (C-0190, C-0192, C-0193, C-0194, C-0256); 7-platform survey confirms no platform mandates the trifecta as a structured artifact (C-0257) — making FR-7's codification novel. |
| **Parent prd-v2.md FR/AC scaffolding** | FR-1, FR-6, FR-7, FR-8, FR-9, FR-10 sections and ACs inherited near-verbatim; NFRs narrowed to NFR-1, NFR-7, NFR-8, NFR-9 (R2b-only NFRs dropped); Stakeholder Inventory and Layer Scope = Claude Code only carried forward (prd-v1.md §Changelog). |
| **Parent codebase-analysis.json + report.md** | Full inheritance per SPLIT-RECORD. R2a's Discovery layers on only what FR-1/6/7/8/9/10 specifically need; the 96-claim codebase-analysis-r2a corpus is additive, not a re-derivation (codebase-analysis-report.md §Inheritance Disposition). |
| **Parent synthesis decisions D-1, D-3, D-4, D-5, D-8** | Resolved synthesis decisions inherited. D-1 → ADR-0059. D-4 → ADR-0063. D-3 → OI-R2a-2 (reverse-check carried as Blueprint OQ). D-5 → OI-R2a-1 (trigger 3/4 mechanical evaluator). D-8 → FR-7 substance heuristic carried forward as recommended (prd-v1.md §Inheritance Manifest). |

## Decision Substrate

Each subsection summarizes the decision frame, status, and either the closure pointer (for closed decisions) or the option enumeration + recommendation + rejection rationale (for open decisions). All 11 decisions and 24 option enumerations are sourced from 04-decision-frames.json and 05-implementation-strategies.json.

### D-1 — FR-1 ADR prescription-extraction mechanism — CLOSED (inherited)

Closed in the parent by ADR-0059. The R2a PRD inherits the companion `.prescriptions.yaml` sibling file as the canonical machine-checkable prescription source; `review-architecture-auditor` reads the companion as ground truth and no-ops on absence (AC-FR-1-b in prd-v1.md). No re-litigation in R2a — the contract already cites the companion file (05-implementation-strategies.json D-1).

### D-3 — FR-10 `auditing-skills` reverse-check posture (OI-R2a-2) — OPEN

**Decision question.** Should `auditing-skills` get a reverse-check rule parallel to FR-10's matrix-presence predicate (when a new skill is authored, audit whether existing agents' `skills:` arrays should include it)? Open for design-composer at the Blueprint stage. Single-sourced supporting claim: C-0072 (investigation deferred this run) (04-decision-frames.json D-3 §risks).

**Options.**

- **Separate parallel rule in `auditing-skills` (RECOMMENDED).** Author a new reverse-check rule mirroring FR-10's matrix-presence predicate at the skill side. Separation of concerns: `auditing-subagents` covers agent-side matrix presence; `auditing-skills` covers skill-side `skills:`-array completeness. Low blast radius (one new rule file); two-way reversible. Re-affirms parent's D-3 lean (05-implementation-strategies.json D-3).
- **Fold into FR-10's `auditing-subagents` rule (REJECTED).** Conflates two audit dimensions (matrix presence vs skill-array completeness) that PRD §Product Policy explicitly keeps separate (prd-v1.md §Product Policy Decisions, `auditing-skills` reverse-check row).
- **Defer to a future feature (REJECTED).** Acceptable fallback but contradicts the parent lean R2a is re-affirming; leaves an asymmetric audit surface indefinitely.

**Recommendation rationale.** Symmetric audit surfaces; low cost; reversible. Single-sourced status (C-0072) is acknowledged in Limitations — the codebase facts (audit-family separation is the existing pattern) make this the lowest-risk path forward, but the Blueprint composer MAY downgrade to defer if the audit gap is judged unlikely to materialize (05-implementation-strategies.json D-3 §rationale).

### D-4 — FR-9 Blocks-X marker grammar canonicalization — CLOSED (inherited)

Closed in the parent by ADR-0063. R2a inherits the canonical grammar; the n=1 prior prose occurrence at `working/feature/devcontainer-mcp-provisioning-r1/codebase-analysis-report.md:198-202` is NOT migrated (non-retroactive policy). Realization concerns (parser placement) are decided separately under D-R2a-3 (05-implementation-strategies.json D-4 §summary_paragraph).

### D-5 — FR-6 trigger conditions 3 & 4 mechanical evaluator (OI-R2a-1) — OPEN

**Decision question.** FR-6's four trigger conditions for "feature touches the agent surface" include two (trigger 3: new skill that the feature's design indicates one or more existing agents will load; trigger 4: new domain concept whose skill-coverage decision names an existing agent as a downstream consumer) that require interpretive reads of Blueprint/Skill-Coverage Decisions text rather than pure file-diff checks (prd-v1.md FR-6 trigger conditions; 04-decision-frames.json D-5). Codebase researcher confirmed (C-0071) the FR-7 table is mechanically parseable — HIGH suitability for the deterministic-predicate route.

**Options.**

- **Hybrid: machine-checkable advisory predicate + human ratification (RECOMMENDED).** Mechanical predicate scans Blueprint's Skill-Coverage Decisions table for trigger-shaped tokens and surfaces an advisory annotation at the Design Composition gate; `design-composer` (human) ratifies whether the FR-6 matrix is required. Override events log to `state-transitions.log` for retrospective tuning. Couples cleanly with D-8 (substance-not-presence heuristic) — predicate checks shape, human checks substance (05-implementation-strategies.json D-5 §pros).
- **Full machine-checkable predicate only (REJECTED).** Interpretive triggers do not survive predicate-only enforcement. Even with high FR-7 table quality (C-0071), trigger 3's "design indicates one or more existing agents will load" requires interpretive read of design context the table cell may not capture (05-implementation-strategies.json D-5 §cons of predicate-only).
- **Human-in-loop checkpoint only (REJECTED).** Wastes the table's mechanical parseability (C-0071); reviewer reads the whole section every time; inconsistent application across runs.

**Recommendation rationale.** Predicate-only loses signal on interpretive triggers; human-only wastes reviewer attention on shape-checks the machine can pre-filter. The hybrid pairs cheap pre-screening with authoritative human ratification and logs overrides for tuning. Predicate hosted in `.claude/skills/auditing-subagents/scripts/` (consistent with D-R2a-5's rule realization); FR-7 table shape (concept | covering-skill | confidence | dogfood-decision | rationale) must stabilize before predicate authoring (05-implementation-strategies.json D-5 §preconditions).

### D-6 — R2a/R2b contingency split — CLOSED (user decision)

Closed by user at parent Gate 4 (Blueprint Approval). R2a is the design-time half (this run); R2b is queued as `pipeline-gate-validator-hardening-r1` (FR-2, FR-3, FR-4, FR-5, FR-11). Canonical lineage in `working/feature/pipeline-cross-artifact-discipline-r1/SPLIT-RECORD.md`. Recorded here for archeological completeness (05-implementation-strategies.json D-6).

### D-8 — FR-7 W/H/A trifecta: substance heuristic vs structural mandate — OPEN (heaviest decision)

**Decision question.** FR-7's Skill-Coverage Decisions section mandates Why/How/Anti-patterns justification for each new domain concept. Should the trifecta be enforced as a full structural mandate (every row populates three labelled cells), a pure substance heuristic (judge by whether the cell reads as actually answering W/H/A), or a hybrid (mandate for new-skill proposals only; substance heuristic for existing-skill and "no-skill-warranted" rows)? **This is the most consequential R2a architectural choice** — FR-7 is the heaviest node in the R2a entity graph at 23 claim back-pointers (02-graph-summary.md §Top entities; 04-decision-frames.json D-8 §risks). The framing choice ripples through FR-7 ACs, dogfood deliverable validation, and every downstream feature run's authoring shape.

**Cross-source ground state.** T-003 verified across 6 platforms (Anthropic Agent Skills, LangChain/LangGraph, OpenAI Assistants/Agents SDK, Microsoft Agent Framework, CrewAI, Semantic Kernel) that W/H/A substance is well-trodden community ground (C-0190, C-0192, C-0193, C-0194, C-0256). Critically, the 7-platform survey also confirms **0/6 surveyed platforms mandate the trifecta as a structured artifact** (C-0257) — the codification-as-mandate is the novel and risky move that anti-ritualism trade-off identifies. PRD §Product Policy already codifies "substance over form" — a decision row is satisfactory iff its justification cell can be read as actually answering the W/H/A questions, not merely populating cells (prd-v1.md §Product Policy Decisions, FR-7 substance vs mandate row).

**Options.**

- **Hybrid: mandate for new-skill proposals, substance heuristic elsewhere (RECOMMENDED).** W/H/A substance is the principle reviewers check for; EXCEPTION: when a Skill-Coverage Decision row proposes a NEW skill (dogfood_decision = `propose-new-skill`), a structured W/H/A artifact with three labelled headings is mandated. For "existing-skill" rows and "no-skill-warranted" rows, the substance principle governs. Preserves T-003's cross-platform-convergent substance without inheriting the novel-ritualism risk; reviewer cost is lowered exactly where it's highest (new-skill proposals are the most expensive review surface — they introduce ongoing maintenance debt) (05-implementation-strategies.json D-8 §pros of hybrid).
- **Full structural mandate universally (REJECTED).** 0/6 surveyed platforms mandate this (C-0257) — explicit anti-ritualism trade-off. Presence-not-substance: three filled headings can be empty of meaningful content and still pass the gate, recreating the exact failure mode FR-7 is designed to prevent. Fights PRD §Product Policy's substance-over-form codification.
- **Principle/substance heuristic only, no mandate anywhere (REJECTED).** Loses the audit anchor for new-skill proposals where structure pays for itself. The new-skill-proposal surface is the highest review-cost ROI; abandoning structure there sacrifices a useful audit anchor for marginal additional substance-preservation.

**Recommendation rationale.** Re-affirms parent's hybrid lean with R2a graph-structural-novelty observation: heaviest-node status (23 back-pointers) corroborates the parent's framing that codification-as-artifact is the novel move warranting explicit risk-mitigation. The hybrid concentrates structural mandate where it has the highest review-cost ROI (new-skill proposals) and preserves substance for the well-trodden cases. Couples explicitly and load-bearingly to D-5: D-5's predicate scores shape only; D-8's substance heuristic is the human's responsibility (05-implementation-strategies.json D-8 §rationale, §cross_decision_dependency). KB-cc-design hosts the W/H/A rubric + substance heuristic; FR-7 section template extended with three labelled headings (Why / How / Anti-patterns) for new-skill rows only.

### D-10 — Severity-vocabulary bridge content — PARTIALLY CLOSED (host inherited; R2a authors content)

Host decided by inherited ADR-0061 (`.claude/skills/KB-review-disciplines/references/severity-taxonomy.md`). R2a authors the bridge content per SPLIT-RECORD's R2a-runs-first ordering. Substrate work-type is content authoring, not option-choice — the actual 5-column bridge mapping is enumerated in the Severity Bridge Content section below. Recommended option: **preserve both weight sets with explicit documentation** (05-implementation-strategies.json D-10 §recommended_option).

### D-R2a-3 — FR-9 marker-parser realization location (OI-R2a-3) — OPEN

**Decision question.** ADR-0063 sets the Blocks-X grammar; the parser/regex that recognizes the marker on stage-transition checkpoints is a separate realization decision. Codebase researcher confirmed zero existing parser (C-0073, C-0074: grep returns no matches across `auditing-shared`, `review-architecture-auditor`, `auditing-subagents`), so this is greenfield placement. Single-sourced supporting claim: C-0073 (04-decision-frames.json D-R2a-3 §risks).

**Options.**

- **Shared helper at `auditing-shared/scripts/parse_blocks_x_markers.py` (RECOMMENDED).** Exposes the canonical regex as a reusable function. Consumers (orchestrator gating logic, `review-architecture-auditor` optional checks, future `auditing-subagents` rule, R2b FR-3 PV-tier invariants) import/invoke via subprocess. Pattern matches existing `auditing-shared` scripts (`log_state_transition.py`, `validate_adr_placement.py`); `auditing-shared` is the canonical library-only home per ADR-0031 + ADR-0042 (05-implementation-strategies.json D-R2a-3 §pros).
- **Inline in `review-architecture-auditor` agent prompt (REJECTED).** Couples parser to one agent; orchestrator gate (the actual parser host per ADR-0063) cannot reuse; LLM-side regex execution is less deterministic than Python regex for em-dash payload edge cases.
- **Inside an `auditing-subagents` rule (REJECTED).** Wrong host per researcher (C-0073): `auditing-subagents` audits `.claude/agents/*.md` quality; marker parsing is an orchestrator concern. Conflates two responsibilities (audit predicate + grammar parsing).

**Recommendation rationale.** Reuse across multiple consumers is the load-bearing argument; auditing-shared is the established canonical-library-home pattern; greenfield placement (no extension constraint per C-0074) means clean separation. Single-sourced status (C-0073) acknowledged in Limitations — but the recommendation derives from inspectable codebase facts (zero existing parser; multiple prospective consumers) (05-implementation-strategies.json D-R2a-3 §rationale).

### D-R2a-4 — FR-7 artifact location (OI-R2a-4) — OPEN

**Decision question.** Is FR-7's Skill-Coverage Decisions section a standalone file (`working/feature/<slug>/skill-coverage-decisions.md`) or a section embedded in existing synthesis/blueprint/cc-design templates? (04-decision-frames.json D-R2a-4.)

**Options.**

- **Section embedded in `synthesis.md` (RECOMMENDED).** Section template hosted at `.claude/skills/KB-documentation-criteria/references/templates/skill-coverage-decisions-section.md`. Surfaces in existing authoring workflow (synthesis.md is already authored every run) — zero discovery cost on authors. Two-way reversible: if substance-heuristic enforcement (D-8) later requires a more visible artifact, the embedded section can be promoted to standalone with mechanical migration. Researcher's recommendation per C-0069, C-0075, C-0076 (zero existing `skill-coverage*` files — greenfield).
- **Standalone `skill-coverage-decisions.md` (REJECTED).** Greenfield artifact convention with no precedent (C-0076); higher irreversibility once authors are trained on it; adds a new artifact to the feature-directory shape competing with FR-11's posture of minimizing post-ship rituals.
- **Embed in `cc-design.md` or `blueprint.md` (REJECTED).** Loses synthesis-stage locality — candidates surface during Synthesis but resolution happens later. Doesn't serve D-5's advisory predicate (which needs the table at the moment FR-6 matrix-mandatory check fires, when synthesis.md has already been authored).

**Recommendation rationale.** Lower-irreversibility path for a novel codification (genesis stage per D-8). Couples cleanly with D-5 (predicate reads from synthesis.md table) and D-8 (section template scopes the W/H/A mandate for new-skill rows only) (05-implementation-strategies.json D-R2a-4 §cross_decision_dependency).

### D-R2a-5 — FR-10 audit rule realization (OI-R2a-5) — OPEN

**Decision question.** Is FR-10's `auditing-subagents` rule added as a new rule entry (SA-NN) or extends an existing rule's predicate? (04-decision-frames.json D-R2a-5.)

**Options.**

- **Add new rule entry SA-NN + new script (RECOMMENDED).** New SA-NN entry under `.claude/skills/auditing-subagents/SKILL.md` plus a new script at `audit_feature_touch_coverage.py` accepting a `--feature-slug` parameter. Three converging codebase facts argue for new rule: zero existing rules predicate on "feature working directory shape" (C-0066, C-0078); script signature mismatch — new script accepts feature-slug parameter, differing from existing scripts' `.claude/agents/<file>.md` shape (C-0067); discoverability under SA-NN sequence is the established pattern. Severity emission references the D-10 bridge by name (05-implementation-strategies.json D-R2a-5 §pros).
- **Extend an existing rule's predicate (REJECTED).** Script signature mismatch (C-0067) means bolting on either touches all callers of an existing script or adds a dispatching script that defeats the simplification. Conflates two audit dimensions in one rule — future readers can't distinguish "predicate fires for agent-file shape issue" from "predicate fires for matrix-missing."

**Recommendation rationale.** Three converging codebase facts (C-0066, C-0067, C-0078) all point one way. Reversibility cost is symmetric; extending an existing rule offers no real economy because the new script signature differs regardless. Couples to D-5 (predicate the new rule invokes), D-R2a-3 (if shared marker-parser script is used by this rule), and D-10 (severity emission references bridge) (05-implementation-strategies.json D-R2a-5 §cross_decision_dependency).

### D-R2a-6 — Plan-stage sequencing: severity-bridge content before FR-1/9/10 consumers (OI-R2a-6) — OPEN (plan-stage)

**Decision question.** How does Plan sequence severity-bridge content authoring versus FR-1/9/10 sections that cite it? (04-decision-frames.json D-R2a-6.)

**Options.**

- **Bridge content first, then FR-1/9/10 emitters (RECOMMENDED).** Plan-stage Phase A authors D-10 severity-bridge content in `severity-taxonomy.md` (design-composer); Phases B/C/D author FR-1 audit-issues schema extension, FR-9 marker-parser realization, and FR-10 audit rule — each citing the bridge by name per ADR-0061's "reference by name, not by copy" guidance. Codebase researcher confirmed bridge content is purely additive at HEAD (C-0079, C-0080: `git diff --stat` returns empty) — no collision surface to manage (05-implementation-strategies.json D-R2a-6 §pros).
- **FR sections first with bridge placeholders, then back-fill (REJECTED).** Discipline risk: if back-fill is missed, placeholders leak into shipped artifacts — exactly the failure mode FR-1's design-realization audit is designed to catch. R2a's own deliverables exhibiting the failure mode FR-1 is designed to catch would be the worst possible dogfood signal.
- **Parallel with stub bridge (REJECTED).** Defers the load-bearing parts of D-10 (non-monotonic edges, two weight sets) to the back-end; FR sections may be approved against the parts that don't matter and re-litigated against the parts that do.

**Recommendation rationale.** Consumers reference real content rather than placeholders, eliminating the discipline risk that would undermine R2a's dogfood signal. Plan author finalizes (05-implementation-strategies.json D-R2a-6 §rationale; deferred_to: plan-author).

## Cross-Decision Dependencies

The open R2a decisions are not independent — six explicit cross-decision dependencies bind them, and design-composer's arbitration must preserve the coupling rather than resolving decisions in isolation (05-implementation-strategies.json §cross_decision_dependencies).

- **D-5 ↔ D-8 (the mechanical-predicate / substance-heuristic seam).** D-5's advisory predicate scores SHAPE; D-8's substance heuristic is the HUMAN's responsibility. This separation is load-bearing — collapsing predicate and substance into a single mechanical gate is the exact anti-pattern T-003 identifies (C-0257) and the failure mode FR-7 is designed to prevent. The predicate hosted at `auditing-subagents/scripts/` MUST NOT attempt to score substance (04-decision-frames.json D-5 §framer_notes; 05-implementation-strategies.json D-8 §cross_decision_dependency).
- **D-R2a-3 ↔ D-R2a-5 (shared marker-parser invocation).** The shared marker-parser script under `auditing-shared/scripts/parse_blocks_x_markers.py` may be invoked by FR-10's new audit rule (`audit_feature_touch_coverage.py`). Design-composer must specify the invocation contract — subprocess vs import — so that consumers don't reimplement the regex inline (05-implementation-strategies.json §cross_decision_dependencies, D-R2a-3 ↔ D-R2a-5).
- **D-R2a-4 ↔ D-5 ↔ D-8 (synthesis.md is the shared substrate).** The Skill-Coverage Decisions section embedded in synthesis.md is what D-5's predicate reads AND what D-8's W/H/A template scopes (for new-skill rows only). All three decisions converge on the same artifact location; section-template authoring touches all three (05-implementation-strategies.json D-R2a-4 §cross_decision_dependency).
- **D-10 ↔ D-R2a-6 (bridge content first, then consumers).** D-10's bridge content is the input to FR-1, FR-9, FR-10 finding-severity emission (per ADR-0061 "reference by name, not by copy"). D-R2a-6's sequencing decision (Phase A bridge content; Phases B/C/D consumers) is the Plan-stage embodiment of this dependency direction (05-implementation-strategies.json D-R2a-6 §preconditions).
- **D-R2a-5 ↔ D-10 (severity emission references bridge).** FR-10's matrix-missing finding severity emission references the bridge by name. Bridge authoring must precede rule authoring so the rule's severity citation resolves to real content (05-implementation-strategies.json §cross_decision_dependencies, D-R2a-5 ↔ D-10).
- **D-R2a-6 sequences the entire R2a Plan.** D-10 bridge content authoring is Phase A; D-R2a-3 / D-R2a-5 realization is Phases C/D after FR sections reference real bridge content. Plan-author owns the sequencing discipline (05-implementation-strategies.json §cross_decision_dependencies, D-R2a-6 sequencing summary).

## Severity Bridge Content (D-10 substrate)

This is the actual content design-cc / design-composer authors into `.claude/skills/KB-review-disciplines/references/severity-taxonomy.md` per inherited ADR-0061. Structural form: a 5-column markdown table (3 vocabulary columns + 1 non-monotonic-edge column + 1 iteration-delta-weight column) plus an explicit Weight Preservation Note. Content sourced from 05-implementation-strategies.json D-10 §bridge_mapping_shape.

| auditor_vocab | reviewer_vocab | pv_vocab | non_monotonic_edges | iteration_delta_weight |
|---|---|---|---|---|
| **BLOCKER** (verdict-compute weight `-12`; additional `-12` flat penalty per occurrence per `verdict_compute.py:97, :158-160`) | **critical** (blocks acceptance; cannot be deferred — must be fixed) | **blocking** (gate refuses to advance) | `BLOCKER ↔ critical ↔ blocking` — strictest tier in each vocabulary; consistent intent (gate-blocking); monotonic | `10` |
| **MAJOR** (`-5`) | **important** (should be fixed before approval; degrades score; defer only with explicit user approval) | **blocking** OR **warning** (branches by PV-tier invariant class — see edge `MAJOR_branching_PV` below) | `MAJOR → {blocking, warning}` — auditor MAJOR branches in PV vocab; default `MAJOR → blocking`; downgrade to `warning` only with explicit per-finding rationale | `3` |
| **MINOR** (`-2`) | **recommended** (improvement; documents approvable with recommended outstanding) | **warning** | `MINOR ↔ recommended ↔ warning` — lowest non-zero severity; consistent intent (non-blocking but actionable); monotonic | `1` |
| **NIT** (`-0.5`; used by `auditing-mcp` SKILL.md:100-105) | **recommended** (taste vs improvement — see edge `NIT_vs_recommended`) | **informational** (closest analog) | `NIT ↔ recommended` translation difficulty: NIT carries "taste" framing (subjective); recommended carries "improvement" framing (actionable). Optional `translate_severity.py` surfaces "taste-vs-improvement" as explicit rationale field. **Reverse mapping (recommended → NIT) loses actionability.** | (not used in iteration-delta math; absent) |
| **INFO** (`0`; used by `review-architecture-auditor.md:27`, `review-cross-artifact-auditor.md:143-145`) | (no direct analog; neutral observation) | **informational** | `NIT ↔ INFO` intra-auditor edge: `auditing-mcp` uses NIT (-0.5); architecture/cross-artifact auditors use INFO (0). Preserve both: NIT for taste/style, INFO for neutral observations (different intent). Parent's Known Issue 2 — documented rather than collapsed. | `0` |

**Intra-auditor divergence note.** `review-architecture-auditor.md` and `review-cross-artifact-auditor.md` emit BLOCKER/MAJOR/MINOR/INFO (no NIT); `auditing-mcp` SKILL.md uses BLOCKER/MAJOR/MINOR/NIT (no INFO). `verdict_compute.py:54-58` is the canonical union: BLOCKER/MAJOR/MINOR/NIT/INFO (05-implementation-strategies.json D-10 §intra_auditor_divergence_note).

### Weight Preservation Note — Why Both Weight Sets Remain

The bridge documents TWO distinct severity-weight mappings because they serve different mathematical roles, and **collapsing to one weight set would silently break the iteration-delta math** (05-implementation-strategies.json D-10 §weight_preservation_note):

1. **Verdict-compute weights** (`{BLOCKER: -12, MAJOR: -5, MINOR: -2, NIT: -0.5, INFO: 0}`) drive absolute verdict scoring in `verdict_compute.py`. They answer "is this audit a PASS?" The signs are negative (penalties accumulate downward against a verdict threshold).
2. **Iteration-delta weights** (`{BLOCKER: 10, MAJOR: 3, MINOR: 1, INFO: 0}`) drive severity-weighted count deltas across review iterations in `review-cross-artifact-auditor.md:93`. They answer "did this iteration improve relative to the previous?" The signs are positive (magnitudes register improvement direction).

These are different mathematical roles. The R2a graph surfaces this as a `conflicts_with` edge: E-0049 (iteration-delta weights) ↔ E-0046 (auditor vocabulary as verdict-compute weight source), with claim backings C-0042, C-0043, C-0092, C-0094 (02-graph-summary.md §Top edges by claim count). The framer's instruction is explicit: surface, not collapse. The inverse-sign relationship between absolute scoring and delta improvement is load-bearing — both sets MUST remain.

### NFR-8 Four-Field Finding Shape (Co-located in Bridge Host File)

Per ADR-0061, the bridge host file also documents the NFR-8 four-field finding shape that downstream FR-1/9/10 emitters use: **`rule`, `target`, `divergence`, `next_action`**. These fields are NOT currently in `audit-issues.json` schema; design-composer adds them as additive sub-fields under `issues[]`. Parent analysis confirmed schema extension is structurally safe across the 12 known downstream consumers (05-implementation-strategies.json D-10 §nfr8_four_field_shape_co_located).

### Bridge Consumers

24 agents load KB-review-disciplines (per codebase-analysis blast_radius_new_confirmations[4], post-cycle-1 reconciliation correction citing I-AA-003 + I-AA-008; adds execute-orchestrator, review-cross-artifact-auditor, intake-intent-clarifier, test-acceptance-author to the prior 20-agent count) — bridge propagates broadly with no separate propagation work. FR-1 (`review-architecture-auditor`), FR-9 (orchestrator Blocks-X resolution events), and FR-10 (matrix-missing finding emission) all reference the bridge by name. R2b consumers (FR-4, FR-5) inherit the populated bridge (05-implementation-strategies.json D-10 §consumers).

## Per-Mechanism Implementation Pointers

Short table mapping each PRD FR to the decision(s) that close its open sub-decisions, the research finding that informs implementation, and the files design-cc will touch. Sourced from prd-v1.md §Functional Requirements + 04-decision-frames.json + codebase-analysis.json.

| FR | Closing decision(s) | Informing research finding | Files design-cc touches |
|---|---|---|---|
| **FR-1** (design-realization audit) | D-1 (closed by ADR-0059); D-R2a-6 (sequencing) | T-002: 9/9 companion-file unanimity (C-0017–C-0021); arXiv 2602.07609 44.57% NLP-misinterpretation (C-0128, C-0134, C-0144) | `.claude/agents/review-architecture-auditor.md` (consumer + audit-dimension); `.claude/skills/auditing-shared/scripts/validate_adr_prescriptions.py` (new); `audit-issues.json` schema (additive 4-field extension per NFR-8) |
| **FR-6** (agent-roster impact matrix) | D-5 (trigger evaluator); D-8 (substance heuristic scopes evidence-cell discipline) | Codebase: 37 agents currently enumerable (`A-4`); KB-cc-design Principle 9 active reframing (C-0033) | `.claude/agents/design-cc.md` (matrix-authoring procedure); `.claude/skills/KB-cc-design/references/principles.md` (Principle 9 text); `.claude/skills/auditing-subagents/scripts/` (advisory predicate per D-5) |
| **FR-7** (skill-coverage decisions) | D-8 (substance heuristic + new-skill mandate); D-R2a-4 (embedded section in synthesis.md) | T-003: 6-platform W/H/A substance convergence (C-0190, C-0192, C-0193, C-0194, C-0256); 0/6 mandate as artifact (C-0257) | `.claude/skills/KB-documentation-criteria/references/templates/skill-coverage-decisions-section.md` (new); `.claude/agents/synthesize-framer.md`; `.claude/agents/design-composer.md` |
| **FR-8** (Principle 9 active reframing) | D-8 cross-reference (cell-discipline text mirrors Principle 9 active framing) | Codebase: `per-agent-design-evaluation-gap` §6.3 non-recommendation (no new sub-agents) | `.claude/skills/KB-cc-design/references/principles.md` (Principle 9 text — defensive → active); `.claude/agents/design-cc.md` (cross-reference per AC-FR-8-b) |
| **FR-9** (Blocks-X stage-transition gates) | D-4 (closed by ADR-0063); D-R2a-3 (parser realization location) | T-002: companion-artifact / structured-pragma pattern (C-0058); ADR-0063 grammar (C-0026–C-0030) | `.claude/skills/auditing-shared/scripts/parse_blocks_x_markers.py` (new); orchestrator state-transitions log shape extension; `.claude/skills/KB-documentation-criteria/references/blocks-x-marker-grammar.md` (consumer-facing reference) |
| **FR-10** (matrix-missing audit rule) | D-R2a-5 (new rule entry + new script); D-3 (parallel `auditing-skills` reverse-check posture) | Codebase: 3 converging facts (C-0066, C-0067, C-0078) all point to new rule entry | `.claude/skills/auditing-subagents/SKILL.md` (new SA-NN rule entry); `.claude/skills/auditing-subagents/scripts/audit_feature_touch_coverage.py` (new; accepts `--feature-slug`); references D-10 bridge for severity |

## Eat-Own-Dogfood Deliverables

Per prd-v1.md §Eat-Own-Dogfood Deliverables, R2a applies its own FR-6 and FR-7 contracts to itself. These deliverables are PRD-level commitments whose concrete file paths land in the Plan and Task Decomposition stages, but the Synthesis surfaces the obligation explicitly so design-composer can route it.

1. **This run's own `agent-roster-impact-matrix.md`** — produced under `working/feature/pipeline-design-time-discipline-r1/` exercising the FR-6 contract on this run's own agent-touching diff. Trigger conditions 1 and 4 fire (the FR-10 audit rule modifies `.claude/agents/` consumers and `.claude/skills/auditing-subagents/`; FR-1/6/7/8 modify `.claude/agents/review-architecture-auditor.md`, `design-cc.md`, `design-composer.md`, `synthesize-*.md`; FR-8 modifies KB-cc-design Principle 9 text loaded by `design-cc`). Row count = current `.claude/agents/*.md` count (~37 per A-4); per-row evidence cells per the positive-evidence-string discipline (prd-v1.md FR-6 §Per-agent-evidence cell granularity).
2. **Six FR-7 skill-coverage decisions** — one per new domain concept this run introduces: (a) design-realization audit (FR-1; E-0034 in graph); (b) agent-roster impact matrix (FR-6; E-0035); (c) skill-coverage decision check (FR-7; E-0036); (d) Principle 9 active reframing (FR-8; E-0033); (e) Blocks-X marker grammar (FR-9; E-0037); (f) agent-roster matrix-missing audit rule (FR-10; E-0038). Per the inherited D-8 substance heuristic, each decision's justification cell must actually answer the W/H/A questions — graph reading confirms all 6 are dogfood-centroid entities bridging Clusters 1–4 (02-graph-summary.md §Cluster 4: Eat-own-dogfood cluster).

**Meta-discipline call-out for design-composer.** D-R2a-6's sequencing recommendation (bridge content first, then FR-1/9/10 emitters) is the specific mechanism that prevents R2a's own deliverables from exhibiting the failure mode FR-1 is designed to catch — i.e., placeholder citations leaking into shipped artifacts. If design-composer relaxes that sequencing (e.g., for parallelism), the dogfood signal is at risk. Preserve the sequencing.

## Skill-Coverage Decisions

*Per ADR-0065 Clause 1; substance-heuristic review applies (all 6 rows resolve to existing-skill).*

For each new domain concept this feature introduces, one of:
- **(a) existing-skill** — name the existing skill that covers the concept + positive-evidence string
- **(b) propose-new-skill** — W/H/A trifecta (Why this needs a new skill; How it would be authored; Anti-patterns it defends against)
- **(c) no-skill-warranted** — rationale for why no skill coverage is needed

| Domain concept | Resolution type | Covering skill (a) / Proposed skill name (b) / Rationale (c) | Positive evidence |
|---|---|---|---|
| design-realization audit | (a) existing-skill | KB-review-disciplines | Auditor lens hosts audit-dimension expansion per CoVe + brief-honor + blast-radius disciplines |
| agent-roster impact matrix | (a) existing-skill | KB-cc-design | Active Principle 9 is the home of "we evaluated every agent" framing |
| skill-coverage decision | (a) existing-skill | KB-cc-design | Principle 2 "skill loading on-demand" hosts skill-vs-no-skill rationale |
| Principle 9 active reframing | (a) existing-skill | KB-cc-design | This IS Principle 9 (trivially covered) |
| Blocks-X marker grammar | (a) existing-skill | KB-documentation-criteria | state-transitions-log-entry-template + canonical conventions are the home of marker grammars |
| agent-roster matrix-missing audit rule | (a) existing-skill | auditing-subagents | Audit-skill family is the home of audit rules over subagents |

**Review posture.** Rows with resolution type (a) or (c) are reviewed via the substance heuristic ("does this make sense?"; substance-not-presence) — the majority case here, with all 6 rows resolving to (a). Rows with resolution type (b) would be reviewed via structural mandate (W/H/A trifecta required, validated by FR-7 review machinery); zero such rows in this run.

## Open Items Carried to Design Composition

The six open decisions route forward as follows. All recommendations match the framer's recorded lean; design-composer's role is to ratify or override, not to re-derive (05-implementation-strategies.json §recommendation_divergence_from_framer_lean).

- **D-3** — substance choice: separate parallel rule in `auditing-skills` vs Blueprint OQ vs defer. Recommended: separate parallel rule. Owner: design-composer at Blueprint. (Single-sourced — see Limitations.)
- **D-5** — substance choice: hybrid advisory predicate + human ratification. Owner: design-composer at Design Composition. Depends on D-8 (substance separation) and D-R2a-4 (table substrate location).
- **D-8** — substance choice: hybrid new-skill mandate + substance heuristic for existing-skill rows. Owner: design-composer at Design Composition. Highest-leverage decision; couples to D-5 and D-R2a-4.
- **D-R2a-3** — substance choice: shared helper at `auditing-shared/scripts/parse_blocks_x_markers.py`. Owner: design-composer at Design Composition. (Single-sourced — see Limitations.)
- **D-R2a-4** — substance choice: section embedded in synthesis.md (template hosted in KB-documentation-criteria). Owner: design-composer at Design Composition. Depends on D-8 (template scopes new-skill mandate).
- **D-R2a-5** — substance choice: add new rule entry SA-NN + new script. Owner: design-composer at Design Composition. Depends on D-R2a-3 (shared parser invocation) and D-10 (bridge severity citation).
- **D-R2a-6** — plan-stage sequencing: bridge content first, then FR-1/9/10 emitters. Owner: plan-author at Plan stage. Sequences the entire R2a Plan.

## Limitations

This section captures the load-bearing caveats design-composer must read transparently. Per the report-composition discipline, single-sourced claims and inherited-by-reference verifications are surfaced rather than smoothed over.

- **Single-sourced supporting claim, D-3 (`auditing-skills` reverse-check posture).** Only C-0072 in the R2a corpus supports the recommendation; investigation was deferred this run rather than researched (04-decision-frames.json D-3 §risks; 05-implementation-strategies.json D-3 §single_sourced_flag). The recommendation re-affirms parent's D-3 lean, but design-composer should treat this as an open question subject to revision if the audit gap proves unlikely to materialize.
- **Single-sourced supporting claim, D-R2a-3 (marker-parser realization location).** Only C-0073 in the R2a corpus supports the recommendation. The codebase-researcher's lean derives from inspectable codebase facts (zero existing parser per C-0074; multiple prospective consumers), but no external corroboration was sourced (04-decision-frames.json D-R2a-3 §risks; 05-implementation-strategies.json D-R2a-3 §single_sourced_flag).
- **Inherited verifications, T-002 (48 claims) and T-003 (56 claims).** These corpora were verified by the parent's CoVe critic and are inherited verbatim by reference into R2a. **R2a did NOT re-run critique.** Load-bearing claims that anchor D-1 (companion-file unanimity), D-4 (Blocks-X grammar precedent), and D-8 (W/H/A substance convergence + anti-mandate trade-off) all derive from these inherited verifications (03-critique-inherited.json §verification-by-reference). If the parent's verification methodology is later found to have a defect, R2a's inheritance chain inherits that defect.
- **D-8 codification is novel (genesis Wardley stage).** No production precedent exists for the exact shape of FR-7's codified skill-coverage decision artifact — 0/6 surveyed platforms mandate the trifecta as a structured artifact (C-0257). The hybrid recommendation is risk-mitigation, not best-practice transfer. The dogfood deliverable (6 skill-coverage decisions on this run's own concepts) is the first production observation of the contract.
- **OI-R2a-2 carried as Blueprint Open Question, not closed.** Per PRD §Product Policy, the `auditing-skills` reverse-check is deliberately carried as a Blueprint OQ rather than folded into FR-10's scope. D-3's recommendation is the suggested resolution but the OQ remains open at Blueprint entry.

## Sources

| Source | Claim count | Role |
|---|---|---|
| `working/feature/pipeline-design-time-discipline-r1/codebase-analysis.json` (R2a codebase analysis) | 96 | R2a-specific codebase facts: agent-roster enumeration, auditing-shared script inventory, KB-review-disciplines bridge host state, FR-7 table parseability, FR-10 script signature mismatch (C-0001–C-0096) |
| `working/feature/pipeline-cross-artifact-discipline-r1/synthesis/01-claims.json` (inherited T-002) | 48 | Design-realization audit prior-art corpus: 9/9 companion-file unanimity, arXiv 2602.07609 NLP-misinterpretation finding, Nygard/MADR ADR-tool ecosystem (C-0097–C-0144) |
| `working/feature/pipeline-cross-artifact-discipline-r1/synthesis/01-claims.json` (inherited T-003) | 56 | Skill-coverage rubric prior-art corpus: 6-platform W/H/A substance convergence, 0/6 mandate-as-artifact finding, Anthropic Skill Quality Checklist, Crews-vs-Flows / tool-proliferation patterns (C-0145–C-0200) |
| `working/feature/pipeline-design-time-discipline-r1/prd-v1.md` | n/a (PRD; not claim-counted) | FR/AC scaffold + Product Policy Decisions + Inheritance Manifest; canonical contract source |
| `adrs/ADR-0059-adr-prescriptions-companion-file.md` (inherited) | n/a (ADR) | Closes D-1; canonical prescription-extraction mechanism |
| `adrs/ADR-0061-severity-vocabulary-bridge-table.md` (inherited) | n/a (ADR) | Pins D-10 host; cross-cutting with R2b |
| `adrs/ADR-0063-blocks-x-marker-grammar.md` (inherited) | n/a (ADR) | Closes D-4; canonical Blocks-X grammar |

## Update History

| Version | Date | Change | Driver |
|---|---|---|---|
| 1.0.0 | 2026-05-26 | Initial synthesis emitted by `synth-synthesizer`. | Synthesis stage of R2a run. |
| 1.0.1 | 2026-05-26 | Added formal `## Skill-Coverage Decisions` section with the 6-row template-shape table (all rows resolve to existing-skill / substance-heuristic review). Narrative reference in Eat-Own-Dogfood Deliverables retained for context; the structured section is the canonical artifact. | Audit finding I-AA-004 (ADR-0065 Clause 3 mandates the template-shape section in synthesis.md; Blueprint inline table relocation tracked separately). Reconciliation cycle 1. |
| 1.0.2 | 2026-05-26 | Updated §Bridge Consumers count from 20 to 24 with the four newly-confirmed agents enumerated, matching Blueprint v1.0.1 + codebase-analysis.json updates from cycle 1. | Audit finding I-AA-008 (gap-fill of one location missed in cycle-1 cross-artifact patch). Reconciliation cycle 2. |

---

*End of synthesis. Awaiting design-cc / design-composer stage entry. Per FR-5 invariant, ADRs are NOT authored at Synthesis — `design-composer` authors any new ADRs at Stage 7 (Design Composition).*
