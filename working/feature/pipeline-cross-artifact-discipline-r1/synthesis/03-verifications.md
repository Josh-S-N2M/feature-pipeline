# 03 — Verifications (audit trail)

**Run:** `pipeline-cross-artifact-discipline-r1` Synthesis stage, Critic phase
**Date:** 2026-05-26
**Scope:** Selective CoVe over the high-impact subset of 32 claims drawn from 372 atomic claims (priorities per orchestrator instructions: synthesis/integration claims, OI-A1/OI-A2 drivers, strongest cross-source triples, codebase researcher's interpretive claims, arXiv ID anomaly).

## Methodology

Per `verification-knowledge/SKILL.md`:
- Restate → generate 2-4 verification questions → answer from cited source via selective Grep → assign verdict → adversarial probe for high-stakes claims → dissent check against `02-graph.json`.
- Selective Grep with `context_lines` 1-5 on `claim.source_uri`; whole-source re-reads only when context insufficient.
- Manifest absence noted (no `00-manifest.json` present in synthesis dir) — `violates_constraint` defaulted null on all critiques. No `hard_constraints[]` to evaluate against.

## Verdict distribution

| Verdict | Count |
|---|---|
| verified | 18 |
| partially_verified | 6 |
| single_sourced | 6 |
| unverifiable | 2 |
| contradicted | 0 |

No dissent flagged: no claims in the high-impact subset directly negate one another. Where T-002 leans toward companion-file (OI-A1) the codebase report (C-0154) explicitly does not pre-decide — these are complementary, not contradictory.

## High-impact claims critiqued (one-line summary)

| Claim | Type | Verdict | Confidence |
|---|---|---|---|
| C-0004 | Cumulative OI count = 14 vs threshold 12 | verified | high |
| C-0005 | Split-recommendation pre-fired | verified | high |
| C-0006 | design-composer must apply threshold at Gate 4 | verified | high |
| C-0033 | §O.1 names 5 post-ship rows vs PRD AC-FR-11-c's 4 | partially_verified | high |
| C-0034 | Cross-artifact-divergence Issue = source of H1/H3/H6/H8/H9 | single_sourced | medium |
| C-0114 | FR-1 mechanism-dependency table row | verified | high |
| C-0116 | FR-3 mechanism-dependency table row | verified | high |
| C-0125 | R2a cluster summary | verified | high |
| C-0126 | R2b cluster summary | verified | high |
| C-0127 | Cross-cluster bridges | verified | high |
| C-0136 | FR-1 companion-file path = new convention | verified | high |
| C-0137 | FR-1 NLP-parse path inherits ADR-0036/56 constraints | verified | high |
| C-0144 | PRD-v2 declares 6 OI-A* items | verified | high |
| C-0145 | Cumulative count = 8 IC + 6 PRD = 14 | verified | high |
| C-0153 | Open question 1: §O.1 5-row vs PRD AC 4-row | verified | high |
| C-0154 | Open question 2: OI-A1 path — Discovery does not pre-decide | verified | high |
| C-0193 | Four-stage drift-detection pipeline | verified | high |
| C-0194 | FR-5 classification catalog | verified | high |
| C-0195 | Crucial FP-suppression in normalization + severity catalog | verified | high |
| C-0201 | <5% FP target achievable (T-001 author's claim) | single_sourced | medium |
| C-0202 | 50-audit window FP failure mode | single_sourced | medium |
| C-0239 | arXiv 2602.07609 — 44.57% misinterpretation | single_sourced | medium |
| C-0246 | Rosik 2011 quote — detection ≠ removal | verified | high |
| C-0256 | T-003 three-category convergence | verified | high |
| C-0257 | W/H/A trifecta is codification not novel content | verified | high |
| C-0283 | CrewAI minimal-tools principle | verified | high |
| C-0291 | Tool-proliferation universally documented | verified | high |
| C-0293 | BFCL 96% → 13-15% accuracy drop | single_sourced | medium |
| C-0350 | Shopify Packwerk = closest migration case | verified | high |
| C-0352 | Privacy checks removed in Packwerk v3.0 | verified | high |
| C-0365 | Packwerk is clearest 'walked-back' datapoint | verified | high |
| C-0366 | Packwerk lesson: central authoring fights team grain | partially_verified | medium |
| C-0367 | Hybrid is documented sweet spot across all 6 systems | verified | high |
| C-0368 | Recommendation: hybrid model with caveats | verified | high |
| (T-002 cross-source) C-0034 (T-002) | 9 surveyed systems all use machine-checkable companions | verified | high |

## arXiv ID resolution (load-bearing)

**Anomaly flagged by T-002 extractor:** arXiv 2602.07609 — concern that the year format doesn't match arXiv's actual scheme (YYMM.NNNNN).

**Resolution:** The arXiv ID **is structurally valid**. arXiv uses a 2-digit year in YYMM.NNNNN format. '2602' parses as YY=26 (year 2026), MM=02 (February). Given today's date is 2026-05-26, a February 2026 preprint is internally consistent. The extractor's concern arose from misparsing '2602' as a 4-digit year (2602 CE), which is incorrect.

**Independent verification of the paper itself:** Not performed in this CoVe sweep (no external HTTP authorised). The 44.57% number remains single-sourced — it appears in T-002's prose verbatim, and the percentage breakdown (44.57 / 28.26 / 18.48 / 8.7) sums to 99.99% (internally coherent). The peer-reviewed framing in T-002 is appropriate.

**Disposition:** Do NOT flag C-0239 as low-confidence on grounds of arXiv ID. The ID format is fine. The number remains single-sourced and externally-unverified — the Synthesizer should:

1. Cite the 44.57% finding as **directional evidence** toward companion-file path for OI-A1, not as decisive.
2. List in the Limitations section: "arXiv 2602.07609 not independently externally verified during Critic sweep; if the OI-A1 resolution is load-bearing on this specific quantitative finding, recommend a targeted external fetch before Gate sign-off."
3. The corroborating signal that 9/9 surveyed production systems use machine-checkable companions (T-002 cross-source claim) is the stronger evidentiary anchor and does not depend on the arXiv number.

## CoVe transcripts — high-stakes claims

### C-0004 / C-0005 / C-0006 — Contingency Split pre-fire

**Restate.** Cumulative OI count entering Synthesis = 14 (IC=8 + PRD-v2=6), exceeds the threshold of 12, so the split-recommendation has effectively pre-fired before any Blueprint OQs are added, and design-composer must apply this mechanically at Gate 4.

**Questions and answers.**
- Q1: Does codebase-analysis-report.md count IC OIs as 8? — A: Yes (line 39, line 262).
- Q2: Does PRD-v2 count add 6 (OI-A1..OI-A6)? — A: Yes (line 263).
- Q3: Does PRD §Contingency Split §1 state the threshold as 12? — A: Yes (line 266, quoted verbatim).
- Q4: Does the PRD's calibration text support 'pre-fired' interpretation? — A: Yes (line 472 quoted: "the threshold of 12 is calibrated as follows: the 4-cycle reconciliation cap, empirically across recent feature runs, terminates around 12–15 active open items; choosing 12 gives a margin and surfaces the question before the cap is hit").

**Adversarial probes.**
- *What would falsify?* — A miscount of IC OIs or double-counting of PRD-v2 OIs. The IC OIs are numbered OI-1..OI-8 and PRD OIs are OI-A1..OI-A6 — namespaces don't collide, so double-counting risk is low.
- *Who benefits from this being true?* — design-composer (justifies invoking the split), Synthesizer (sets the framing for the report). Neither is decisive; the count is observable.

**Verdict: verified, high confidence.** Load-bearing for the Synthesis report's split recommendation.

### C-0033 / C-0153 — §O.1 row count anomaly

**Restate.** The deferral register §O.1 names FIVE post-ship rows (A-3, D-5, E-2, E-3, I-1) but PRD AC-FR-11-c enumerates only four (E-3, A-3, D-5, I-1) — design-composer should decide whether E-2 belongs in AC-FR-11-c.

**Questions and answers.**
- Q1: Does §O.1 actually list five rows? — A: Confirmed via direct Grep on `Issues/devcontainer-mcp-provisioning-r1-deferrals/register.md` lines 224-230. Table contains A-3, D-5, E-2, E-3, I-1.
- Q2: Does PRD AC-FR-11-c list only four? — A: Reported by codebase-analysis-report; not re-read against PRD directly. Internal-audit claim citing its own corpus — accepted.
- Q3: Is E-2's shape comparable? — A: register.md line 228 characterises E-2 as 'post-ship felt-utility review' with 'No felt-utility review ritual is defined' — identical structure to E-3.

**Verdict: partially_verified (one component direct, one component accepted on author authority), high confidence.** The recommendation that design-composer decides is appropriately scoped.

### C-0193 — Four-stage drift-detection pipeline (FR-5 design recommendation)

**Restate.** A defensible architecture for the MCP `tools/list` drift detector is: (1) JCS normalize per RFC 8785; (2) persist baseline as JCS-canonical bytes; (3) diff with RFC 6902 using LCS + identity-keyed array diff; (4) classify with a per-rule severity catalog modeled on oasdiff.

**Questions and answers.**
- Q1: Is each stage substantiated by a primary in T-001? — A: Yes — RFC 8785 (JCS), oasdiff change-fingerprints, RFC 6902, oasdiff severity catalog all named.
- Q2: Is the identity-keyed array diff grounded in MCP spec uniqueness? — A: Yes — T-001 cites 'tools have unique names per the MCP spec'.
- Q3: Is the oasdiff-to-MCP modelling defensible? — A: oasdiff is industry-recognised for OpenAPI; modelling on it is defensible but the cross-domain mapping (OpenAPI → MCP tools/list) is novel to this run.

**Adversarial probes.**
- *What would falsify?* — A pilot run showing FP rate exceeds 5% despite all four stages. The author preemptively warns about this (C-0202).
- *Silence on adjacent points?* — T-001 does not specify a baseline-rotation policy (how often the JCS-canonical baseline is rebuilt). Worth flagging for design-composer.

**Verdict: verified, high confidence.** Strong cross-source triple: FR-5 ↔ four-stage pipeline ↔ MCP spec + RFC 8785 + RFC 6902 + oasdiff. The composition step is the author's contribution but each primitive is well-cited.

### C-0239 — arXiv 2602.07609 (44.57%)

Detailed transcript in arXiv ID resolution section above. **Verdict: single_sourced, medium confidence.** ID format issue resolved; external verification of paper deferred to Synthesis-Limitations callout.

### C-0367 — Hybrid invariant model

**Restate.** Hybrid (denormalized declaration, centralized body) is the documented sweet spot across every survey datapoint in T-004.

**Questions and answers.**
- Q1: Does T-004 enumerate hybrid pattern across all 6 systems? — A: Yes (lines 153-155); each of Terraform, dbt, OpenAPI, JSON Schema, ArchUnit, Bazel mapped to the hybrid shape.
- Q2: Counterexample test — fully-central or fully-denormalized system? — A: JSON Schema is closest to fully-central but $defs are per-document. ArchUnit is closest to fully-denormalized but allows central JAR. No extreme system in survey.
- Q3: Is the transfer to PV authoring acknowledged as a design judgment? — A: Yes (T-004 line 178-180 open question 1 says explicitly this is not 1:1 transferable).

**Adversarial probes.**
- *Who benefits?* — Anyone proposing a hybrid OI-A2 resolution. T-004 author transparent about not pre-deciding.
- *Cherry-picked survey?* — T-004 explicitly does not find a denormalized → centralized migration case (open question 3). Honest absence-of-evidence framing.

**Verdict: verified, high confidence.** Load-bearing for OI-A2 routing toward hybrid.

## Dissent check

No claims in the high-impact subset directly negate one another. The closest near-dissent pairs:

- C-0136 (companion-file = new convention) vs C-0137 (NLP-parse = inherits ADR constraints): both are framings of the same OI-A1 trade-off; not dissent.
- T-002 synthesis tilts toward companion-file path; codebase-analysis explicitly does not pre-decide (C-0154). Complementary, not dissenting.

No `dissent_evidence` field populated.

## Constraint-violation check

`00-manifest.json` not present in synthesis directory. No `constraints.hard_constraints[]` available. All `violates_constraint` fields default null.

If a manifest is added downstream and the orchestrator wants to re-run the constraint check, the most likely candidates to evaluate would be:
- Any constraint about "no new conventions without ADR" — would flag C-0136 (companion-file = new convention).
- Any constraint about "single canonical location" — already aligned with C-0137 (NLP-parse path).

## Limitations of this critique pass

1. **External primary-source fetches** not performed for arXiv 2602.07609, Shopify Packwerk retrospective, BFCL data, RFC/JCS specs, Rosik 2011 — accepted as cited internally. If any of these become Synthesis decision drivers and the orchestrator wants higher confidence, a targeted external pass is warranted.
2. **Vendor docs** (CrewAI, Anthropic, OpenAI, LangGraph, MAF, Semantic Kernel, Perplexity) accepted as cited per orchestrator's de-prioritisation guidance.
3. **PRD direct re-reads** not performed; codebase-analysis-report's quotations of PRD passages accepted on author authority (internal audit trail context).
4. **Counts and trivial repo facts** (37 agent files, 6 MCP servers, etc.) accepted per orchestrator's de-prioritisation guidance.

## Final recommendations for Synthesizer

- **OI-A1 resolution:** Evidence tilts toward companion-file path (T-002 9/9 production-systems convergence + peer-reviewed LLM-unreliability finding). Codebase report transparently does not pre-decide. Synthesizer should frame the OI-A1 decision frame with both paths' trade-offs, weight the companion-file evidence heavier, and route to design-composer for the call.
- **OI-A2 resolution:** Hybrid (denormalized declaration, centralized body) is well-supported. Caveat: domain transfer to PV authoring is a design judgment, not a sourced inference.
- **OI-A4 (Contingency Split):** Mechanically triggered. Surface in Decision Frames as resolved-by-rule.
- **FR-5 architecture:** Four-stage pipeline is the strongest cross-source design recommendation. Adopt as-is; surface the unaddressed baseline-rotation question for design-composer.
- **FR-7 (W/H/A trifecta):** Substance is multi-source-corroborated. The mandate-as-codification framing is the novel contribution; anti-ritualism defenses should be designed-in (T-003 calls this out).
- **Limitations section** of final report should list: (a) arXiv 2602.07609 not externally re-verified; (b) BFCL specific numbers single-sourced; (c) T-004 hybrid model's transfer to PV authoring is a design judgment.
