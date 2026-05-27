---
id: SYNTHESIS-pipeline-cross-artifact-discipline-r1
version: 1.0.0
status: draft
doc_type: synthesis
feature_slug: pipeline-cross-artifact-discipline-r1
derived_from:
  - working/feature/pipeline-cross-artifact-discipline-r1/prd-v2.md
  - working/feature/pipeline-cross-artifact-discipline-r1/synthesis/01-claims.json
  - working/feature/pipeline-cross-artifact-discipline-r1/synthesis/02-graph.json
  - working/feature/pipeline-cross-artifact-discipline-r1/synthesis/03-critique.json
  - working/feature/pipeline-cross-artifact-discipline-r1/synthesis/04-decision-frames.json
  - working/feature/pipeline-cross-artifact-discipline-r1/synthesis/05-implementation-strategies.json
  - working/feature/pipeline-cross-artifact-discipline-r1/codebase-analysis.json
generated: 2026-05-26
generated_by: synth-synthesizer
audience: design-cc (primary), design-composer (primary), review-architecture-auditor + plan-author (secondary)
---

# Synthesis: Cross-Artifact + Design-Time Discipline (R2)

## Executive Summary

The 11 PRD mechanisms collectively shift the feature pipeline from per-artifact correctness to **cross-artifact and cross-stage correctness** — verifying that ADR prescriptions match the files that ship, that the agent surface is enumerated rather than evaluated-by-absence, that new domain concepts produce explicit skill-coverage decisions, and that "post-ship / N days post-ship" deferral framings are replaced with event-triggered, honest-acceptance, or concrete-machinery framings. The thesis is structural rather than cosmetic: every recurrence path the user named in the brief (the MCP shipment incident, the 28-untouched-agents evaluation gap, the §O.1 register of unfired post-ship triggers) is a per-artifact-validator missing a cross-artifact relationship check (Issues/cross-artifact-divergence-detection-gap/analysis.md; PRD-v2 §Overview).

Ten decisions sit between this synthesis and design-cc / design-composer. Five are externally pre-decided by cross-source evidence and need design-cc to apply them at the cc layer (D-1, D-2, D-7, D-8, D-9). Three are interpretive or implementation-scoped and need design-cc judgment (D-3, D-4, D-5). Two route to design-composer because they cross layers or sit at Gate 4 (D-6 Contingency Split; D-10 severity vocabulary reconciliation) (synthesis/04-decision-frames.json; synthesis/05-implementation-strategies.json).

The single most load-bearing structural fact for design-composer: **the Contingency Split watch-item is genuinely ambiguous, not pre-decided.** The orchestrator's currently-open-OI count (6) does not trip the threshold of 12; the codebase researcher's cumulative count (14 = 8 IC + 6 PRD-v2) does. Both readings have direct PRD evidence; this synthesis recommends the single-feature posture absent contradicting evidence at Gate 4 but routes the decision rather than ratifying it (synthesis/03-critique.json C-0004 / C-0005 / C-0006; PRD-v2 §Contingency Split).

## Decision Substrate

Each subsection below summarizes the decision frame, the framer's classification, the implementation-strategy enumeration, the recommended option, and the rejection rationale for each non-recommended branch. All ten recommendations align with the framer's recorded lean per the implementation-strategies file's `recommendation_divergence_from_framer_lean: []` summary; no synthesizer-dissent notes are warranted.

### D-1 — OI-A1: Prescription-extraction path for FR-1 design-realization audits

**Decision question.** When `review-architecture-auditor` (FR-1, mechanism H3) compares an ADR's prescriptions against the file the feature ships, where does it read those prescriptions from — a machine-checkable companion file sibling to the ADR, or an NLP parse of the ADR's prose body? (PRD-v2 OI-A1; synthesis/04-decision-frames.json D-0001.)

**Framer's classification.** Architectural; one-way reversibility; tenant blast radius; product Wardley stage; RICE = (reach 50, impact 2.0, confidence 0.8, effort 8). Externally pre-decided: companion-file. Decision owner: design-cc.

**Option enumeration (implementation-strategies D-0001).**

- **Option 1 — companion_file (RECOMMENDED).** Sibling YAML/JSON file next to each `ADR-*.md` lists the ADR's machine-checkable predicates: invariants, must-hold-after-implementation assertions, file-pattern guards. The architecture auditor reads the companion as the canonical prescription source; ADR prose remains canonical for the decision narrative per ADR-0036 (single canonical location) and ADR-0056 (no carve-outs). The companion must not duplicate the decision; only its check-shaped predicates.
  - *Pros:* 9 of 9 surveyed production systems use this shape (synthesis/03-critique.json C-0034 [T-002 source]); avoids the 44.57% LLM misinterpretation rate documented for NLP parsing of decision prose (synthesis/03-critique.json C-0239 citing arXiv 2602.07609); predicates are reviewable in PR diff like any artifact and lint-able with schema validation; decouples audit-tooling evolution from ADR-prose evolution.
  - *Cons:* establishes a new repo convention — no `*.yaml` siblings to `ADR-*.md` exist today (synthesis/03-critique.json C-0136); legacy ADRs (ADR-0001..ADR-0056) require either incremental backfill or an explicit FR-1-scope deprecation window; risk of companion drifting from ADR prose (mitigation: `auditing-shared` script that diffs companion against ADR's machine-checkable section).
  - *Evidence anchors:* C-0034 (9/9 surveyed); C-0239 (44.57% misinterpret); C-0246 (Rosik 2011 "detection insufficient"); C-0136 (no yaml siblings today); C-0154 (Discovery routes for human resolution).

- **Option 2 — nlp_parse_adr_prose (REJECTED).** Architecture auditor extracts prescriptions from ADR prose at audit time using LLM-based parsing.
  - *Rejection rationale:* Documented 44.57% misinterpretation rate on the exact "semantic/logical misinterpretation" category (synthesis/03-critique.json C-0239) and 0 of 9 surveyed precedent (synthesis/03-critique.json C-0034 [T-002 source]) make this branch uncompetitive. Audit non-determinism (parsing twice yields different prescription sets) falsifies NFR-5 (auditor idempotency, AC-NFR-5-a) (PRD-v2 NFR-5). PRD-v2 OI-A1 explicitly named both branches, so this option is enumerated for design-composer visibility per framer instruction.

- **Option 3 — hybrid_nlp_drafting_companion_canonical (viable alternative; deferred).** NLP-parse used only at ADR draft time to generate a starter predicate set; ADR author reviews and ratifies into the companion file. Audit reads the companion as canonical.
  - *Disposition:* Worth keeping in reserve if the legacy-ADR backfill cost in Option 1 proves prohibitive in practice. Not recommended initially because it adds two-system maintenance burden for a problem (authoring burden) that does not exist until the backfill workload is observed. Deferral framing should be event-triggered per FR-11 ("when an FR-1 audit hits an ADR without a companion AND author burden NFR is breached") (PRD-v2 FR-11).

**Recommendation.** **Option 1 — companion_file.** Strong cross-source triple (T-002 nine-system unanimity + peer-reviewed counter-evidence + low blast radius for the new convention). Hybrid is the natural escape hatch if authoring burden bites; not needed up front.

**Constraint propagation check.** PRD-v2 §Constraints (Claude Code layer only, no new sub-agents, no retroactive register edits): companion files live under `adrs/` and read by `review-architecture-auditor` — Claude Code layer only; no new agent; no retroactive edits to `Issues/devcontainer-mcp-provisioning-r1-deferrals/register.md`. **No violation.**

### D-2 — OI-A2: FR-3 PV-tier cross-file invariant authoring shape

**Decision question.** When a phase validator (FR-3, mechanism H9) declares the cross-file relationships its deliverables share, are those invariants authored denormalized (each PV declares and defines its invariants in-line), centralized (one catalog file owns all invariants), or hybrid (each PV declares which invariants it owns; the catalog hosts the predicate bodies)? (PRD-v2 OI-A2; synthesis/04-decision-frames.json D-0002.)

**Framer's classification.** Architectural; one-way reversibility; service blast radius; product Wardley stage; RICE = (reach 30, impact 2.0, confidence 0.8, effort 6). Externally pre-decided: hybrid. Decision owner: design-cc.

**Option enumeration (implementation-strategies D-0002).**

- **Option 1 — hybrid_denormalized_declaration_centralized_body (RECOMMENDED).** PVs declare which invariants they own/honor at the artifact (YAML stanza or markdown table at the PV header); invariant body — predicate logic, error-message text, severity — lives in a central catalog (host candidate: `.claude/skills/KB-task-decomposition/cross-file-invariants.md`). Declarations reference catalog entries by ID (e.g., CFI-NNN).
  - *Pros:* 6 of 6 surveyed systems land at this sweet spot — Terraform, dbt, OpenAPI, JSON Schema, ArchUnit, Bazel (synthesis/03-critique.json C-0367); Shopify Packwerk migration retrospective is the strongest available counter to fully-centralized and is preempted by this choice (synthesis/03-critique.json C-0350, C-0352, C-0365, C-0366); locality at declaration site, DRY at body site; cross-file invariants structurally need cross-file coordination.
  - *Cons:* two-file coordination at edit time; catalog grows monotonically and needs deprecation discipline; T-004 explicitly caveats that surveyed domains are code/data/API not pipeline-document content (synthesis/03-critique.json C-0367 notes); C-0366 "different teams" framing is the T-004 author's gloss (partially_verified).
  - *Evidence anchors:* C-0367 (6/6 sweet spot); C-0350/C-0352/C-0365 (Packwerk migration retrospective); C-0368 (recommendation framing); C-0116 (FR-3 cluster).

- **Option 2 — denormalized_inline (REJECTED).** Each PV declares and defines its invariants in-line; no central catalog.
  - *Rejection rationale:* Cross-file invariants without a central body invite per-PV drift — the same invariant defined N times across N PVs (synthesis/03-critique.json C-0367); severity / error-message text scattered, which worsens the D-10 severity-vocabulary divergence directly. The point of FR-3 is to enforce cross-file consistency; denormalized-inline structurally fights the goal.

- **Option 3 — centralized (REJECTED).** Single catalog file owns all invariants; PVs do not declare; catalog declares which PVs each invariant applies to.
  - *Rejection rationale:* Shopify Packwerk retrospective is the strongest available counterexample — privacy checks were removed in Packwerk v3.0 because fully-centralized authoring fights the grain (synthesis/03-critique.json C-0350, C-0352, C-0365); JSON Schema's $defs (the closest-to-centralized surveyed pattern) is per-document, not cross-document (synthesis/03-critique.json C-0367). PV authors lose locality and the catalog becomes a bottleneck artifact. Even with the T-004 transferability caveat, the negative signal is preserved across the analogical mapping.

**Recommendation.** **Option 1 — hybrid_denormalized_declaration_centralized_body.** 6/6 surveyed sweet spot plus the only documented migration retrospective in the corpus walks back from centralized. Implementation-strategies records this as the framer's strong, externally-decided lean.

**Constraint propagation check.** Hybrid catalog lives in `.claude/skills/KB-task-decomposition/` per the PRD's dependency declaration (PRD-v2 §Technical Considerations / Dependencies); PV-author rubric host is `.claude/agents/test-phase-validator-author.md` per codebase-analysis Known Issue 3. Claude Code layer only; no new agent; no retroactive edits. **No violation.**

### D-3 — OI-A3: Scope of auditing-skills reverse-check

**Decision question.** FR-10 (mechanism B5) adds a feature-touch-coverage rule on `auditing-subagents` (sub-agent file → owning skill family back-reference). Should an analogous reverse-check live in `auditing-skills` (skill file → owning agent or recipe back-reference), or is FR-10 sufficient? (PRD-v2 OI-A3 / Product Policy Decision §auditing-skills reverse-check; synthesis/04-decision-frames.json D-0003.)

**Framer's classification.** Implementation; two-way reversibility; component blast radius; custom Wardley stage; RICE = (reach 5, impact 1.0, confidence 0.5, effort 2). Externally undecided; weak recommendation strength. Decision owner: design-cc.

**Option enumeration (implementation-strategies D-0003).**

- **Option 1 — separate_rule_in_auditing_skills (RECOMMENDED).** Author a new reverse-check rule inside `.claude/skills/auditing-skills/` that mirrors FR-10's SA-13 at the skill level. One rule file; one new audit dimension.
  - *Pros:* Separation of concerns (auditing-subagents covers agent-side reverse refs; auditing-skills covers skill-side); low blast radius; reversible; makes the §O posture for FR-11 cleaner because each posture decision attaches to its own audit family without cross-family conditional logic.
  - *Cons:* externally undecided, no T-corroborator (synthesis/03-critique.json claims C-0123, C-0131 internal-only); two audit families end up with structurally-similar rules — manual sync risk if either evolves.

- **Option 2 — extend_fr10_scope_to_cover_auditing_skills (viable alternative).** FR-10's rule explicitly enumerates both audit surfaces.
  - *Disposition:* Defensible if design-composer prefers minimum-surface-area FR scope. Not recommended because the framer's separation-of-concerns lean is the cleaner architectural choice; cost delta is ~0.

- **Option 3 — defer (viable alternative).** Ship FR-10 alone now; revisit only if the audit gap is observed in practice.
  - *Disposition:* Acceptable fallback if design-composer wants to compress FR scope. Documented deferral framing must be event-triggered ("when an FR-10 audit miss surfaces a skill-side reverse-ref gap") per FR-11. Adds a deferral entry, which competes with FR-11's goal of reducing reflexive deferrals (PRD-v2 FR-11).

**Recommendation.** **Option 1 — separate_rule_in_auditing_skills.** Symmetric audit surfaces; low cost; reversible. Per PRD Product Policy Decision (auditing-skills reverse-check carried as Blueprint Open Question), design-cc proposes; design-composer ratifies the placement.

**Constraint propagation check.** Rule lives under `.claude/skills/auditing-skills/`. Claude Code layer only; no new sub-agent; no retroactive edits. **No violation.**

### D-4 — OI-A5: Blocks-X marker grammar

**Decision question.** FR-9 (mechanism B4) requires `Blocks <stage>` markers emitted from Discovery output to be parseable by the orchestrator at stage-transition checkpoints. The codebase has exactly one prior occurrence (devcontainer-mcp-provisioning-r1 codebase-analysis-report lines 198-202). Should the grammar be the prose precedent verbatim, a structured pragma, or a YAML-frontmatter field? (PRD-v2 FR-9 + A-5; synthesis/04-decision-frames.json D-0004.)

**Framer's classification.** Implementation; two-way reversibility; service blast radius; genesis Wardley stage; RICE = (reach 20, impact 1.0, confidence 0.65, effort 2). Externally undecided; moderate recommendation strength. Decision owner: design-cc.

**Option enumeration (implementation-strategies D-0004).**

- **Option 1 — structured_html_comment_pragma (RECOMMENDED).** Adopt `<!-- BLOCKS: <stage-slug>-completion -->` embedded in Discovery output. Single canonical shape parsed by the gate/validator cluster.
  - *Pros:* n=1 prior occurrence means no grammar to honor — establishing a structured shape now costs nothing in compatibility (synthesis/03-critique.json C-0122); HTML comments are invisible in rendered markdown but greppable from CI; structured shape supports multi-slug from day one; downstream consumers (FR-2 §Protocol Conformance schema, AC-FR-9-* assertions, FR-3 PV-tier invariants) inherit a stable wire format; easier mechanical evaluator for D-5's predicate.
  - *Cons:* slight authoring overhead; lock-in if downstream FR-2 ships before grammar revision; diverges from the n=1 prose precedent ("Blocks <stage-slug>-completion." period-terminated) — small migration if retained anywhere.

- **Option 2 — yaml_frontmatter_field (viable alternative).** Add a `blocks:` field to Discovery output frontmatter.
  - *Disposition:* Strongest structured shape but Discovery output is not currently frontmatter-bearing for this metadata; less discoverable in prose review; over-engineered relative to n=1 baseline.

- **Option 3 — preserve_n1_prose_grammar_verbatim (REJECTED).** Adopt "Blocks <stage-slug>-completion." verbatim with a regex parser.
  - *Rejection rationale:* n=1 is not a grammar — it is an occurrence. Honoring it verbatim ossifies a parser that was never designed for multi-slug or grammar variation ("Blocks the stage-x-completion." would fail the regex). Premature lock-in to a precedent of one. The structured pragma form preserves the readable intent (the `BLOCKS:` token is still skim-greppable) without the regex fragility.

**Recommendation.** **Option 1 — structured_html_comment_pragma.** Greppable, multi-slug-ready, invisible in rendered output, and cheap. The grammar spec hosts in `.claude/skills/KB-documentation-criteria/` per the framer's claude_code_layer_attachment.

**Constraint propagation check.** Grammar spec lives in `.claude/skills/KB-documentation-criteria/`; stage slugs in `recipe-feature-pipeline/SKILL.md`. Claude Code layer only; no new sub-agent. **No violation.**

### D-5 — OI-A6: Mechanical evaluator for FR-6 trigger conditions 3 and 4

**Decision question.** FR-6 (mechanism B1) makes the agent-roster-impact-matrix mandatory whenever a feature touches the agent surface. Trigger conditions 3 and 4 (new skill loaded by existing agents; new-domain-concept skill-coverage decision naming an agent) are interpretive. Should the evaluator be a pure mechanical predicate, a pure human-in-loop checkpoint, or a hybrid (predicate fires advisory; human ratifies)? (PRD-v2 FR-6 + Risks-table OI-A6 row; synthesis/04-decision-frames.json D-0005.)

**Framer's classification.** Implementation; two-way reversibility; service blast radius; custom Wardley stage; RICE = (reach 25, impact 1.5, confidence 0.5, effort 4). Externally undecided; moderate recommendation strength. Decision owner: design-cc.

**Option enumeration (implementation-strategies D-0005).**

- **Option 1 — hybrid_advisory_predicate_with_human_ratification (RECOMMENDED).** Mechanical predicate scans Blueprint's Skill-Coverage Decisions section for trigger-shaped tokens and surfaces an advisory annotation at the Design Composition gate; design-composer (human) ratifies whether the matrix is required. Predicate false-negatives surface as human-override events logged to `state-transitions.log`.
  - *Pros:* balances mechanical determinism with human judgment on interpretive triggers; couples cleanly with D-8 (substance-not-presence) — predicate checks shape, human checks substance; logs override events for retrospective tuning; cheap to ship and tune.
  - *Cons:* two-system maintenance (predicate + checklist); externally undecided, no T-corroborator (synthesis/03-critique.json claims C-0119, C-0120 internal); risk of human ratification becoming a rubber stamp.

- **Option 2 — machine_checkable_predicate_only (REJECTED).** Pure mechanical predicate gates the matrix-mandatory check.
  - *Rejection rationale:* Triggers 3 and 4 are interpretive — pattern-match brittleness yields false negatives ("cross-skill impact" phrased five different ways); conflicts with D-8's substance-not-presence heuristic (the predicate would check phrasing, not substance of intent); single point of failure — a missed trigger is silently un-audited. The documented FR-7 anti-ritualism trade-off (synthesis/03-critique.json C-0257) applies symmetrically here.

- **Option 3 — human_in_loop_only_at_design_composition_gate (viable alternative).** design-composer (human) checks Blueprint's Skill-Coverage Decisions section at Design Composition gate; no mechanical evaluator.
  - *Disposition:* Defensible if design-composer prefers zero tool debt. Not recommended because the advisory predicate is cheap and directly reduces reviewer cognitive load without claiming the predicate is authoritative; inconsistent application across runs (reviewer-dependent) is the documented failure mode.

**Recommendation.** **Option 1 — hybrid_advisory_predicate_with_human_ratification.** Predicate hosts in `.claude/skills/auditing-subagents/`; ratification step extends `design-claude-code.md` procedure; override events logged via `auditing-shared/log_state_transition.py`.

**Cross-decision dependency.** Couples to D-8 (substance-not-presence): the predicate here MUST NOT score substance; it scores shape only. The human ratification scores substance.

**Constraint propagation check.** Predicate and ratification step both Claude Code layer; logging hook extends existing `auditing-shared` utility. No new sub-agent. **No violation.**

### D-6 — OI-A4 / Contingency Split: R1 single feature vs R2a/R2b split

**Decision question.** PRD §Contingency Split sets a threshold of 12 cumulative open items; if exceeded, the feature splits into R2a (FR-1, FR-6, FR-7, FR-8, FR-9, FR-10) and R2b (FR-2, FR-3, FR-4, FR-5, FR-11). Two readings of "cumulative" coexist: the orchestrator's currently-open count is 6 (PRD-v2 OI-A1..OI-A6); the codebase researcher's cumulative-across-stages count is 14 (8 IC OIs + 6 PRD-v2 OIs). Both readings have direct PRD evidence. (PRD-v2 §Contingency Split; synthesis/04-decision-frames.json D-0006.)

**Framer's classification.** Architectural; one-way reversibility; tenant blast radius; custom Wardley stage; RICE = (reach 40, impact 3.0, confidence 0.8, effort 12). Recommendation strength: **route-to-gate**. Decision owner: **design-composer at Gate 4**, NOT design-cc. The framer surfaces both readings as admissible inputs to Gate 4 without recommending one.

D-6 has its own subsection below (§Contingency-Split Resolution Substrate) because the user's brief named the watch-item explicitly. The summary recommendation surfaced there: **ship single-feature (R1) absent contradicting evidence at Gate 4**, per the framer's instruction that the orchestrator's reading prevails when both readings are well-evidenced and no Gate-4 evidence falsifies it. The implementation-strategies file records this as `recommended_option: null` and `deferred_to: Gate 4 (design-composer)`.

**Constraint propagation check.** Whichever reading design-composer ratifies, all 11 mechanisms remain Claude Code layer; no new sub-agents in either R1 or split scope; no retroactive register edits. **No violation under either reading.**

### D-7 — FR-5: Four-stage drift-detection pipeline

**Decision question.** FR-5 (mechanism H8) requires drift detection over MCP `tools/list` responses with NFR-4 target <5% false-positive rate across 50 consecutive audits. What pipeline architecture? (PRD-v2 FR-5 + NFR-4; synthesis/04-decision-frames.json D-0007.)

**Framer's classification.** Architectural; one-way reversibility; service blast radius; product Wardley stage; RICE = (reach 30, impact 2.0, confidence 0.8, effort 8). Externally pre-decided. Decision owner: design-cc.

**Option enumeration (implementation-strategies D-0007).**

- **Option 1 — four_stage_pipeline (RECOMMENDED).** Stage 1: RFC 8785 JSON Canonicalization Scheme normalizes `tools/list` payloads (whitespace, key-ordering, number representation). Stage 2: persisted canonical baseline (oasdiff change-fingerprint pattern, baseline-as-bytes; one file per MCP server). Stage 3: RFC 6902 JSON-Patch diff with identity-keyed array diff (MCP spec guarantees tool names are unique). Stage 4: locally-enumerated severity catalog modeled on oasdiff — remove → BLOCKER (AC-FR-5-a); signature change → MAJOR (AC-FR-5-e); addition → MAJOR (AC-FR-5-d); description/title/icon → INFO.
  - *Pros:* strong cross-source triple — each stage grounded in an independent primary (synthesis/03-critique.json C-0193 four-stage verified; C-0194 catalog mapping to AC-FR-5-a/d/e); FP-suppression located where evidence supports it — normalization (step 1) + catalog routing (step 4), not diff defaults (synthesis/03-critique.json C-0195; openapi-diff Issue #673 cautionary tale); identity-keyed array diff grounded in MCP spec; each stage replaceable without re-architecting the others.
  - *Cons:* <5% FP claim (NFR-4) is single-sourced (synthesis/03-critique.json C-0201) — no primary measures the exact FP rate under these exact conditions; the composition step (oasdiff catalog → MCP `tools/list`) is novel; pilot validation required at Phase Validator time to confirm <5% FP target.

- **Option 2 — naive_object_diff_with_heuristic_severity (REJECTED).** Direct object-diff over raw `tools/list` JSON; severity inferred by ad-hoc heuristics.
  - *Rejection rationale:* openapi-diff Issue #673 is the documented evidence that naive diff fails the exact use case (synthesis/03-critique.json C-0195); without normalization, formatting differences become false positives — fails NFR-4 on any realistic upstream; description-polishing and CDN-URL rewrites (synthesis/03-critique.json C-0202) read as drift, not as INFO; heuristic severity is per-author per-audit with no auditable contract.

- **Option 3 — vendor_tool_reuse_oasdiff_or_openapi_diff (REJECTED).** Adopt oasdiff or openapi-diff directly.
  - *Rejection rationale:* Neither tool natively understands the MCP `tools/list` schema — they target OpenAPI / Swagger; an adapter layer (translate MCP → OpenAPI → vendor diff → translate severity back) is more code than the bespoke four-stage pipeline AND inherits vendor-tool quirks (synthesis/03-critique.json C-0193 — T-001 explicitly cites oasdiff as model, not target for adoption).

**Recommendation.** **Option 1 — four_stage_pipeline.** Strong cross-source triple; each underlying primitive well-cited; novel composition defensible because each primitive is sound.

**Open sub-decision.** NFR-4 (<5% FP) measurement strategy. No surveyed source publishes a quantitative benchmark; the achievability claim is mechanistic (the normalization + catalog moves remove the dominant FP sources) but the number is extrapolated. Recommend a **pilot run at Phase Validator authoring time**: 50 audits against the current stable MCP server set; measure FP rate; refine catalog if measured FP > 5%. Surfaced in §Limitations.

**Constraint propagation check.** Drift detection hosts in `.claude/skills/auditing-mcp/` (PRD-v2 §Dependencies); canonical input is `.mcp.json`. Claude Code layer only; no new sub-agent; NFR-3 (drift detection wall-clock <500 ms/server) and NFR-2 (3000 ms reachability timeout) are honored by the staged pipeline architecture. **No violation.**

### D-8 — FR-7: W/H/A trifecta as substance vs mandate

**Decision question.** FR-7 (mechanism B3) requires a Why/How/Anti-patterns trifecta for each skill-coverage decision. Is W/H/A a substance reviewers check for (substance-not-presence heuristic), or a mandated three-headed artifact (mandate-as-artifact)? (PRD-v2 FR-7; synthesis/04-decision-frames.json D-0008.)

**Framer's classification.** Implementation; two-way reversibility; service blast radius; product Wardley stage; RICE = (reach 25, impact 1.5, confidence 0.8, effort 4). Externally pre-decided: substance-as-rubric with a carve-out mandate for new-skill proposals. Decision owner: design-cc.

**Option enumeration (implementation-strategies D-0008).**

- **Option 1 — substance_as_rubric_with_mandate_for_new_skill_proposals (RECOMMENDED).** W/H/A is the substance reviewers check for. Reviewers apply a substance-not-presence heuristic: the trifecta is satisfied if substance is present, regardless of whether three labelled headings exist. EXCEPTION: when a new skill is proposed, a structured W/H/A artifact is mandated, because new-skill proposals carry higher review cost and explicit shape lowers it.
  - *Pros:* preserves T-003's cross-platform substance convergence across 6 platforms (synthesis/03-critique.json C-0256) without inheriting the novel-ritualism risk that T-003 explicitly identifies (synthesis/03-critique.json C-0257); reviewer cost is lowered exactly where it is highest; substance heuristic aligns with how reviewers actually catch missing rationale; coheres with D-5's advisory-predicate design (machine checks shape; human checks substance).
  - *Cons:* substance heuristic is reviewer-dependent and harder to mechanically evaluate; "new skill proposal" boundary requires a clear definition (likely: "creates a new directory under `.claude/skills/`"); the BFCL quantitative evidence (synthesis/03-critique.json C-0293: 96% → 13-15%) is single-sourced and directional, not a measured threshold for this pipeline.

- **Option 2 — mandate_as_artifact_universally (REJECTED).** Every skill-coverage decision MUST produce a structured W/H/A artifact with three labelled headings.
  - *Rejection rationale:* 0 of 6 surveyed platforms mandate this — codification-as-mandate is the novel and risky move per T-003 (synthesis/03-critique.json C-0257); presence-not-substance (three filled headings can be empty of content and still pass the gate); drives authors toward ritualistic minimum-viable filings, undermining the actual goal of need-justification + scope hygiene + anti-pattern awareness.

- **Option 3 — principle_only_no_mandate (viable alternative).** W/H/A is a principle in KB-cc-design; reviewers apply substance heuristic to all cases including new-skill proposals; no mandate anywhere.
  - *Disposition:* Defensible if design-composer wants zero structural artifacts. Not recommended because the new-skill-proposal carve-out is where structure pays for itself.

**Recommendation.** **Option 1 — substance_as_rubric_with_mandate_for_new_skill_proposals.** Hosts in `.claude/skills/KB-cc-design/` (Principle 9 + W/H/A rubric) plus `.claude/agents/design-claude-code.md` (author-side procedure).

**Cross-decision dependency.** Couples to D-5: the advisory predicate there scores shape; the human ratification step scores substance.

**Constraint propagation check.** All hosts are Claude Code layer. No new sub-agent. Coheres with PRD Product Policy "Per-agent-evidence-cell granularity" (positive-evidence-required, bare values insufficient). **No violation.**

### D-9 — FR-11 §O posture placement

**Decision question.** FR-11 (mechanism §O) replaces "post-ship / N days post-ship" framings with three permitted postures: event-triggered, honest-acceptance, concrete-machinery. Where in the discipline-text surface should the posture wording live? (PRD-v2 FR-11; synthesis/04-decision-frames.json D-0009.)

**Framer's classification.** Implementation; two-way reversibility; component blast radius; custom Wardley stage; RICE = (reach 15, impact 1.0, confidence 0.65, effort 3). Moderate recommendation strength. Decision owner: design-cc (placement); design-composer (E-2 inclusion scope).

**Option enumeration (implementation-strategies D-0009).**

- **Option 1 — three_host_placement (RECOMMENDED).** Place §O wording in three host surfaces: (a) KB-cc-design — Principle 9 placement for cc-layer designers; (b) PV-author rubric in `test-phase-validator-author` — for PV authors who decide deferral framings; (c) KB-documentation-criteria — deferral conventions section so all discipline texts share the same posture grammar. Apply to discipline texts identified by §O.1 register (currently 5 rows: A-3, D-5, E-2, E-3, I-1) pending design-composer's E-2 inclusion-scope decision.
  - *Pros:* purely additive — zero "post-ship" precedent in `.claude/skills/` and `.claude/agents/` today (synthesis/03-critique.json C-0110, C-0113); three hosts cover three distinct audiences (cc-layer designers, PV authors, discipline-text authors) without cross-host conditional logic; coheres with FR-11 goal; each host owns its surface — clean ownership boundaries.
  - *Cons:* three locations to keep coherent (sync risk, minor); E-2 inclusion is a separate sub-decision routed to design-composer (synthesis/03-critique.json C-0153); partially-verified count mismatch — register §O.1 names 5 rows, PRD AC-FR-11-c enumerates 4 (synthesis/03-critique.json C-0033) — exact discipline-text set depends on design-composer ratification.

- **Option 2 — kb_cc_design_only (viable alternative).** Place §O wording in KB-cc-design only.
  - *Disposition:* Acceptable minimum-scope choice. Not recommended because broadening costs almost nothing and the additive opportunity is high.

- **Option 3 — kb_cc_design_plus_pv_author_rubric (viable alternative).** Two-host placement.
  - *Disposition:* Acceptable middle path. Not recommended because adding KB-documentation-criteria costs ~0.5w and meaningfully improves discipline-text-author guidance.

**Recommendation.** **Option 1 — three_host_placement.** Purely additive; three-host covers three distinct audiences; sync risk minimal because all hosts share the same posture vocabulary.

**Open sub-decision (routed to design-composer).** E-2 inclusion in AC-FR-11-c scope. The §O.1 register names FIVE rows (A-3, D-5, E-2, E-3, I-1) but AC-FR-11-c enumerates four (E-3, A-3, D-5, I-1). FR-11 must update its enumeration to either preserve four (with explicit rationale why E-2 differs) or expand to five. Surfaced in §Open Items.

**Constraint propagation check.** All three hosts Claude Code layer. **FR-11 explicitly forbids retroactive edits to register §O.1 rows (E-3, A-3, D-5, I-1) per PRD AC-FR-11-c.** This recommendation honors that constraint: §O wording goes into discipline texts that govern *going-forward* authoring, not into the register itself. **No violation.**

### D-10 — Severity vocabulary reconciliation across FR-1 / FR-4 / FR-5 / FR-9 / FR-10

**Decision question.** Three coexisting severity vocabularies sit on the audit/reviewer/validator surface: (a) auditor BLOCKER/MAJOR/MINOR/NIT (used by review-architecture-auditor, auditing-mcp, auditing-cc-configs, auditing-shared); (b) reviewer critical/important/recommended (used by shared-document-reviewer, KB-review-disciplines); (c) phase-validator blocking/warning/informational (used by test-phase-validator-author). FR-1/FR-4/FR-5/FR-9/FR-10 all emit findings consumed across these surfaces. Reconcile by unify, partition with bridge table, or canonicalize with translator? (synthesis/04-decision-frames.json D-0010; codebase-analysis Known Issue 2.)

**Framer's classification.** Architectural; one-way reversibility; tenant blast radius; custom Wardley stage; RICE = (reach 40, impact 2.0, confidence 0.5, effort 10). Externally undecided; moderate recommendation strength. Decision owner: **design-composer (cross-cuts layers); design-cc proposes for the cc layer.**

**Option enumeration (implementation-strategies D-0010).**

- **Option 1 — preserve_trifecta_with_explicit_bridge_table (RECOMMENDED).** Each surface keeps its current vocabulary. A bridge table — authored by design-composer and hosted in `KB-review-disciplines/severity-taxonomy.md` (or `auditing-shared/` as the cross-surface utility host) — documents the cross-vocabulary mapping with explicit notes on non-monotonic edges (e.g., BLOCKER → critical → blocking is monotonic; NIT → recommended is borderline).
  - *Pros:* each vocabulary serves a different audience — auditor output drives tooling (numeric verdict scoring per `auditing-cc-configs/scripts/verdict_compute.py`); reviewer output drives humans; PV output drives gate decisions. Forcing convergence destroys audience-fit. Bridge table is purely additive — no migration cost on existing audit outputs, reviewer outputs, or PV outputs. Externally undecided (no T-corroborator) means preferring lowest-irreversibility option.
  - *Cons:* three vocabularies stay in repo; readers must consult the bridge to translate; bridge becomes stale if any vocabulary evolves independently; single-sourced support (synthesis/03-critique.json C-0108 is the only direct claim, no T-corroborator); translator semantics are non-trivial (NIT vs recommended vs informational are not strictly equivalent).

- **Option 2 — canonicalize_with_translator (viable alternative).** Pick auditor BLOCKER/MAJOR/MINOR/NIT as canonical (widest in-repo footprint). Reviewer and PV vocabularies map to canonical via a documented translator.
  - *Disposition:* Defensible if design-composer prioritizes canonical tooling input over audience-fit. Not recommended because irreversibility cost is high (touches KB-review-disciplines, test-phase-validator-author, shared-document-reviewer), audience-fit cost is real (humans don't naturally read BLOCKER on review output), and the externally-undecided status counsels reversibility.

- **Option 3 — unify_one_vocabulary_across_all_surfaces (REJECTED).** Pick one vocabulary and migrate all surfaces to it.
  - *Rejection rationale:* highest migration cost (touches at minimum auditing-mcp, auditing-subagents, auditing-cc-configs, auditing-shared, KB-review-disciplines, test-phase-validator-author, shared-document-reviewer); destroys audience-fit (humans on review output and PV authors lose tailored vocabulary); one-way per framer's reversibility classification; externally undecided + one-way + tenant-blast-radius is the worst configuration for forcing convergence.

**Recommendation.** **Option 1 — preserve_trifecta_with_explicit_bridge_table.** Bridge table hosted in `KB-review-disciplines/severity-taxonomy.md` (canonical host candidate per framer) with an optional `auditing-shared` utility to mechanically translate at `audit-issues.json` emission time. **Design-composer ratifies the bridge wording** because the decision cross-cuts layers.

**Constraint propagation check.** Bridge table Claude Code layer; additive; touches no existing schemas. **No violation.**

## Cross-Decision Dependencies

Three cross-decision seams must be visible to design-composer at integration time. These are not optional — implementation order and contract surface depend on them.

**D-5 ↔ D-8: mechanical predicate vs substance heuristic.** The FR-6 trigger-evaluation predicate (D-5) and the FR-7 W/H/A substance heuristic (D-8) form a complementary pair: the predicate scores shape (presence of trigger-shaped tokens, structural mandate when a new skill is proposed); the human reviewer scores substance (is the rationale substantively present, is the trigger substantively met?). Implementation must preserve this split — if D-5's predicate begins scoring substance, the D-8 substance principle is hollowed out by mechanical pre-judgment; if D-8 begins mandating shape universally, the D-5 advisory annotation becomes redundant ritualism (implementation-strategies D-0005 cross_decision_dependency; D-0008 cross_decision_dependency).

**D-10's bridge table consumed by FR-1 / FR-4 / FR-5 / FR-9 / FR-10.** All five findings-emitting FRs in this feature write severities into outputs consumed across the three vocabulary surfaces. The bridge table (recommended in D-10) is the single artifact that lets a FR-1 BLOCKER on `architecture-audit-issues.json` translate to a reviewer's "critical" or a phase-validator's "blocking" without loss of monotonicity. If D-10 is deferred or rejected, every one of FR-1/4/5/9/10 must either pick a vocabulary unilaterally (introducing audience-fit cost) or emit findings into a vocabulary that downstream consumers do not understand (introducing translation cost at every consumption site). The bridge is load-bearing for all five FRs (synthesis/04-decision-frames.json D-0010; codebase-analysis Known Issue 2; implementation-strategies summary.cross_decision_dependencies).

**D-6's gating effect on R2a/R2b sequencing.** If design-composer ratifies the single-feature reading at Gate 4, all 11 FRs ship together and the dependency table is implementation-order guidance only. If design-composer ratifies the split reading, R2a (FR-1, FR-6, FR-7, FR-8, FR-9, FR-10) and R2b (FR-2, FR-3, FR-4, FR-5, FR-11) may ship asynchronously; in that case, the **cross-cluster bridges** (FR-1 ↔ FR-4 + FR-5 via `architecture-audit-issues.json` schema; FR-9 ↔ FR-2 via Discovery-output marker emission) must be coordinated as shared contracts authored in whichever cluster ships first (codebase-analysis mechanism-dependency table; synthesis/03-critique.json C-0114, C-0125, C-0126, C-0127). D-6's downstream effect: the schema bridge is unavoidable; the choice is whether it ships as one feature's internal contract or two features' shared contract.

## Contingency-Split Resolution Substrate

The Contingency Split (D-6 / OI-A4) was named in the user's brief as a watch-item and deserves its own subsection. The decision is not technical — it is interpretive — and both interpretations have direct PRD evidence.

**Reading A — orchestrator's currently-open count = 6.** PRD-v2 declares OI-A1..OI-A6 at PRD time (synthesis/03-critique.json C-0144 verified; codebase-analysis-report line 263). The synthesis-stage view: IC OIs are resolved upstream by the PRD's authoring; PRD-v2 OIs are the live count entering Design. Six does not trip the threshold of 12. This reading reflects the orchestrator's current routing posture and avoids the one-way irreversibility of splitting (synthesis/04-decision-frames.json D-0006 option `orchestrators_currently_open_reading_6_ois`).

**Reading B — codebase researcher's cumulative count = 14.** The codebase researcher counts cumulatively: 8 IC OIs + 6 PRD-v2 OIs = 14 (synthesis/03-critique.json C-0004 verified verbatim from codebase-analysis-report.md line 263; C-0145 same arithmetic). PRD calibration text (codebase-analysis-report.md line 472) reads "the threshold of 12 is calibrated as follows: the 4-cycle reconciliation cap, empirically across recent feature runs, terminates around 12–15 active open items; choosing 12 gives a margin and surfaces the question before the cap is hit." Under this reading the threshold is already met at synthesis dispatch — the split-recommendation has pre-fired (synthesis/03-critique.json C-0005 verified; entailment mechanical given C-0004).

**Mechanical input for design-composer (codebase-analysis mechanism-dependency table).** If split: R2a = FR-1 (cross-cutting, relocatable), FR-6, FR-7, FR-8, FR-9, FR-10; R2b = FR-2, FR-3, FR-4, FR-5, FR-11. Cross-cluster bridges that must be coordinated either way: FR-1 ↔ FR-4 + FR-5 via `architecture-audit-issues.json` schema additions; FR-9 ↔ FR-2 via Discovery-output marker emission (synthesis/03-critique.json C-0114, C-0125, C-0126, C-0127 verified). The cluster boundaries are evidence-grounded, not arbitrary — but they were drawn under Reading B's premise, so adopting Reading A makes them implementation-order guidance rather than feature-boundary lines.

**Discovery's framer routing.** The codebase researcher's recommendation, quoted verbatim: "design-composer must apply the threshold mechanically at Gate 4" (synthesis/03-critique.json C-0006 verified verbatim from codebase-analysis-report.md line 39). The framer's classification confirms: route-to-gate, design-composer at Gate 4, not design-cc (synthesis/04-decision-frames.json D-0006). The orchestrator instruction for this synthesis is consistent: "design-composer decides at Gate 4; this synthesis recommends single-feature posture unless a new factor surfaces."

**Synthesis recommendation.** Ship as **single-feature R1** absent contradicting evidence at Gate 4. The framer's instruction is that the orchestrator's reading prevails when both readings are well-evidenced and Gate-4 evidence does not falsify it. Contradicting evidence would look like: R1 design-time scope exceeds reviewer capacity, R1 ADR count exceeds the 4-cycle cap at Gate 4, or design-composer's review of the mechanism-dependency table reveals coordination cost between R2a/R2b clusters that exceeds the cost of one larger feature.

**Reversibility cost note.** R1 → R2 split later is mechanical: the cluster boundaries are already drawn and evidence-grounded. R2 → R1 merge later is the one-way path because downstream artifacts (Blueprints, ADRs, phase-validators) will have been authored separately. This asymmetry weights the recommendation toward Reading A even before applying the framer's instruction.

## Per-Mechanism Implementation Pointers

Short table for design-cc: which decision(s) close each FR's open sub-decisions; which research finding informs implementation; which file(s) design-cc will touch. This is the layer-design hand-off; design-cc authors the implementation, not this synthesis.

| FR | Mechanism | Closes via decision(s) | Informing research / claim | design-cc touchpoints (PRD §Dependencies) |
|---|---|---|---|---|
| FR-1 | H3 — design-realization audit | D-1 (OI-A1 path) + D-10 (severity vocabulary, partial) | T-002 nine-system survey (C-0034); arXiv 2602.07609 (C-0239); Rosik 2011 (C-0246) | `.claude/agents/review-architecture-auditor.md` (audit dimension); `adrs/` (companion-file convention, new sibling YAML/JSON); `.claude/skills/KB-review-disciplines/architecture-audit.md` (companion schema host) |
| FR-2 | H6 — §Protocol Conformance subsection | D-4 (Blocks-X grammar consumed by §Protocol Conformance schema) | codebase-analysis Known Issue 1 (mcp-openapi-schema stale ref); A-2 (MCP transport handshake) | `.claude/agents/discovery-codebase-researcher.md` (new subsection contract); `.claude/skills/KB-documentation-criteria/` (subsection schema) |
| FR-3 | H9 — PV-tier cross-file invariants | D-2 (OI-A2 hybrid shape) + D-10 (severity vocabulary, partial) | T-004 six-system survey (C-0367); Shopify Packwerk retrospective (C-0350, C-0352, C-0365) | `.claude/agents/test-phase-validator-author.md` (PV-author rubric — note: rubric host is the agent, not KB-task-decomposition, per codebase-analysis Known Issue 3); `.claude/skills/KB-task-decomposition/cross-file-invariants.md` (catalog body) |
| FR-4 | H1 — `--with-mcp-reachability` rename + handshake | (no open sub-decisions) | A-2 (claude mcp ping or JSON-RPC fallback per PRD-v2 §Assumptions) | `.claude/skills/auditing-mcp/` (runner); `.mcp.json` (target inventory) |
| FR-5 | H8 — tool-surface drift detection | D-7 (four-stage pipeline) + D-10 (severity vocabulary) | T-001 cross-source triple (C-0193, C-0194, C-0195); RFC 8785, RFC 6902, oasdiff; openapi-diff Issue #673 (cautionary) | `.claude/skills/auditing-mcp/` (drift detection); baseline storage subdir; severity catalog under `auditing-mcp/references/` |
| FR-6 | B1 — agent-roster-impact-matrix mandatory | D-5 (OI-A6 mechanical evaluator) + D-8 (substance heuristic, cross-coupling) | per-agent-design-evaluation-gap §2 (four-dimension pattern per PRD §Background) | `.claude/agents/design-claude-code.md` (authoring procedure); `.claude/skills/auditing-subagents/` (mechanical predicate host); `.claude/skills/KB-cc-design/` (FR-6 cell-discipline cross-reference per AC-FR-8-b) |
| FR-7 | B3 — skill-coverage decisions | D-8 (substance-as-rubric + new-skill mandate carve-out) | T-003 six-platform convergence (C-0256); T-003 anti-ritualism trade-off (C-0257); BFCL (C-0293) | `.claude/skills/KB-cc-design/` (W/H/A rubric); `.claude/agents/design-claude-code.md` (author-side) |
| FR-8 | B2 — Principle 9 active rewording | D-8 (substance heuristic informs wording) | per-agent-design-evaluation-gap (B2 thesis); FR-6 cross-reference per AC-FR-8-b | `.claude/skills/KB-cc-design/` (Principle 9 text) |
| FR-9 | B4 — Blocks-X markers as gates | D-4 (grammar) | codebase-analysis OI-A5 watch-item evidence (n=1 prior occurrence); FR-2 conformance schema consumer | `.claude/skills/KB-documentation-criteria/` (grammar spec); `.claude/agents/discovery-codebase-researcher.md` (emission site); orchestrator state-transitions log (consumer per PRD §Dependencies) |
| FR-10 | B5 — auditing-subagents feature-touch-coverage | D-3 (auditing-skills reverse-check scope) | codebase-analysis Known Issue 2 (reverse-check generalization) | `.claude/skills/auditing-subagents/` (SA-13); `.claude/skills/auditing-skills/` (parallel rule if D-3 ratifies separate rule) |
| FR-11 | §O — replace post-ship framings | D-9 (three-host placement); E-2 inclusion routes to design-composer | codebase-analysis-report.md line 285 (zero post-ship precedent in current skills/agents); §O.1 register five rows | `.claude/skills/KB-cc-design/`; `.claude/agents/test-phase-validator-author.md` (PV-author rubric); `.claude/skills/KB-documentation-criteria/` (deferral conventions section) |

## Open Items Carried to Design Composition

Items this synthesis cannot close that design-composer or downstream stages must.

1. **D-3 — Auditing-skills reverse-check scope.** Per PRD Product Policy, carried as Blueprint Open Question. Recommendation here is separate rule under `auditing-skills`; design-composer ratifies.

2. **D-4 — Blocks-X grammar choice.** Recommendation is structured HTML-comment pragma over n=1 prose precedent. design-cc selects the wire format at the cc layer; downstream FR-2 conformance schema and FR-9 gate emitter consume it.

3. **D-5 — FR-6 trigger 3+4 mechanical evaluator.** Recommendation is hybrid (predicate fires advisory; human ratifies). design-cc authors the predicate; design-composer ratifies the ratification hand-off at the gate.

4. **D-6 — Contingency Split (OI-A4) at Gate 4.** Recommendation surfaces single-feature R1 as default; **design-composer applies the threshold mechanically at Gate 4** per Discovery's verbatim instruction. Both readings (6-OI orchestrator, 14-OI cumulative) preserved as admissible inputs.

5. **D-9 — E-2 inclusion in AC-FR-11-c verbatim-preservation scope.** Register §O.1 names five rows (A-3, D-5, E-2, E-3, I-1); PRD AC-FR-11-c enumerates four (E-3, A-3, D-5, I-1). FR-11 must update its enumeration to either four-with-rationale-for-E-2-exclusion or five. Routes to design-composer (synthesis/03-critique.json C-0153).

6. **D-10 — Severity vocabulary reconciliation across FR-1/4/5/9/10.** Recommendation is preserve-trifecta-with-bridge-table. design-cc proposes the bridge for the cc layer; **design-composer ratifies the bridge wording because the decision cross-cuts layers.**

7. **arXiv 2602.07609 ID resolution.** Critic resolved the ID as structurally valid (YY=26 = 2026, MM=02 = February; not future-year-format) (synthesis/03-critique.json C-0239 verification answer 1). The paper's existence and the 44.57% percentage remain externally unverified in this sweep — the source is one paper with no corroborating independent measurement found in T-002. If a Synthesis or Design-Composition decision becomes load-bearing on the specific 44.57% number (rather than on the qualitative "NLP-parse of decision prose is fragile" claim), recommend a targeted external fetch before Gate sign-off. Surfaced in §Limitations.

8. **FR-5 NFR-4 < 5% FP measurement.** No surveyed source publishes a quantitative benchmark for drift-detection FP rate on MCP `tools/list`. The achievability is mechanistic (normalization + catalog routing remove the dominant FP sources) but the number is extrapolated. **Pilot at Phase Validator authoring time:** run 50 audits against the current stable MCP server set; measure FP rate; refine the severity catalog if measured FP > 5%. Surfaced in §Limitations.

9. **§O.1 row count discrepancy.** PRD AC-FR-11-c enumerates 4 rows; register §O.1 contains 5 (codebase-analysis Known Issue 4; synthesis/03-critique.json C-0033 partially_verified — 5-row count confirmed directly, 4-row enumeration trusted from codebase-analysis without direct PRD re-read). FR-11 must update its enumeration. Routes to design-composer with D-9.

## Limitations

Single-sourced claims that became load-bearing for a recommendation, and measurement gaps the synthesis cannot close.

1. **arXiv 2602.07609 single-sourcing.** The 44.57% LLM-misinterpretation-rate number for ADR-prose parsing (synthesis/03-critique.json C-0239) is the strongest specific counter-evidence against D-1's NLP-parse branch. The paper's existence and content were not externally re-verified in this synthesis run (no external HTTP authorized). The qualitative claim "NLP parsing of decision prose is fragile" is corroborated by Rosik 2011 (synthesis/03-critique.json C-0246) and the 9/9 surveyed-system unanimity for companion-file (C-0034), so the D-1 recommendation does not collapse if the specific 44.57% number is wrong — but if a downstream decision turns specifically on that number, recommend an external fetch first.

2. **FR-5 NFR-4 < 5% FP measurement gap.** Claims C-0201 (achievability) and C-0202 (50-audit description-polishing/CDN failure-mode warning) are both single-sourced in T-001. No primary measures the FP rate under the exact conditions of the recommended four-stage pipeline on MCP `tools/list`. The recommendation depends on a mechanistic argument (normalization + catalog routing remove the dominant FP sources) plus a pilot validation deferred to Phase Validator authoring time. If the pilot exceeds 5% FP, the severity catalog is the first dial to tune; if catalog tuning does not close the gap, the pipeline architecture itself is the second.

3. **D-3 (auditing-skills reverse-check) externally undecided.** No T-001..T-004 finding corroborates; sole supporting claims are internal (synthesis/03-critique.json C-0123, C-0131). The recommendation rests on symmetry with FR-10's existing SA-13 rule, not on external precedent. Reversible (two-way), low blast radius, so the cost of getting this wrong is bounded.

4. **D-5 (mechanical evaluator) externally undecided.** No T-corroborator for the trigger-evaluation pattern. Recommendation rests on the cross-decision coupling with D-8 (predicate scores shape; human scores substance) and on the FR-7 anti-ritualism trade-off. The advisory annotation is itself a hypothesis to validate against operational use — track override-event frequency in `state-transitions.log` and re-tune the predicate if false-negative rate exceeds reviewer tolerance.

5. **D-10 (severity vocabulary) externally undecided.** No T-corroborator for vocabulary reconciliation. Sole direct claim is C-0108 (synthesis/03-critique.json). Recommendation (preserve trifecta with bridge) is grounded in audience-fit and reversibility arguments, not external precedent. Bridge maintenance becomes a Limitations-class burden if any of the three vocabularies evolves independently — D-10's risk surface scales with how often the surfaces evolve.

6. **T-004 transferability caveat (D-2).** T-004 surveyed code/data/API artifacts (Terraform, dbt, OpenAPI, JSON Schema, ArchUnit, Bazel) and the Shopify Packwerk dependency-graph migration — NOT pipeline-document content. The hybrid pattern is robustly observed in the surveyed domain; transfer to PV-tier cross-file invariants is a design judgment (synthesis/03-critique.json C-0367 note; C-0368 explicit transferability disclosure). The Packwerk lesson generalizes structurally (fully-centralized authoring fights the grain with multi-author surfaces) but does not measure the same artifact category.

7. **C-0366 partially-verified gloss.** The "different teams" framing of the Packwerk lesson is the T-004 author's gloss, not a verbatim retrospective quote (synthesis/03-critique.json C-0366 partially_verified). The direction (central authoring is hard with multi-team authors) is defensible; the specific framing is the author's analytical move. The D-2 recommendation does not depend on this specific framing, only on the documented Packwerk privacy-check removal (C-0352 verified).

## Sources

| Source | Type | Claims contributing | One-line summary |
|---|---|---|---|
| `working/feature/pipeline-cross-artifact-discipline-r1/prd-v2.md` | PRD | (all 11 FRs + 9 NFRs + 6 OI-A* + Product Policy Decisions) | Canonical requirement set; 11 mechanisms named with mechanism letters H/B/§O |
| `working/feature/pipeline-cross-artifact-discipline-r1/codebase-analysis.json` | codebase analysis | 7 known issues; mechanism-dependency table; OI-A1/A2/A4/A5 watch-item evidence | Discovery-stage codebase grounding; FR-to-touchpoint mapping |
| `working/feature/pipeline-cross-artifact-discipline-r1/codebase-analysis-report.md` | codebase analysis (human-readable) | Cluster reading; cross-cluster bridges; verbatim "design-composer must apply the threshold mechanically at Gate 4" instruction (line 39) | Companion to the JSON sidecar |
| T-001 external research (drift-detection) | research finding | C-0193..C-0202 (four-stage pipeline; FP-suppression locus; achievability + warning) | RFC 8785, RFC 6902, oasdiff, openapi-diff Issue #673 |
| T-002 external research (design-realization audits) | research finding | C-0034 [T-002 source], C-0239, C-0246 | Nine-system survey (9/9 companion-file); arXiv 2602.07609 (44.57% NLP misinterpret); Rosik 2011 |
| T-003 external research (skill-coverage rubric) | research finding | C-0256, C-0257, C-0283, C-0291, C-0293 | Six-platform W/H/A convergence; novel-as-codification; BFCL directional evidence |
| T-004 external research (cross-file invariant catalogs) | research finding | C-0350, C-0352, C-0365, C-0366, C-0367, C-0368 | Six-system hybrid sweet spot; Shopify Packwerk migration retrospective |
| `Issues/cross-artifact-divergence-detection-gap/analysis.md` | issue analysis | Provenance for mechanisms H1/H3/H6/H8/H9 (C-0034 provenance backstop) | Unifying-thesis source per PRD §Background |
| `Issues/per-agent-design-evaluation-gap/analysis.md` | issue analysis | Provenance for mechanisms B1..B5; four-dimension trigger pattern | Parallel converging analysis per PRD §Background |
| `Issues/devcontainer-mcp-provisioning-r1-deferrals/register.md` | discipline register | §O.1 five rows (A-3, D-5, E-2, E-3, I-1); §O.5 user direction "no retroactive edits" | Anchor for FR-11; explicit no-retroactive-edits constraint |
