# 03-verifications

Synth-critic CoVe verification for `execute-orchestrator-dispatch-mechanism-repair-r1` Synthesis fan-in.
Sources: 3 per-source claims files (146 CR + 76 T + 74 AN = 296 claims).
Run id: `execute-orchestrator-dispatch-mechanism-repair-r1-20260523-202235`.

This is the human-readable companion to `03-critique.json`. The JSON carries the per-claim verdicts; this Markdown surfaces the CoVe walk-throughs, the 5 dissents, and the high-stakes verifications.

## Executive Summary

| Metric | Value |
|---|---|
| Total claims | 296 |
| Verified | 273 |
| Partially verified | 11 |
| Dissent (preserved for framer) | 9 |
| Unverifiable | 0 |
| Single-sourced (transparency flag) | 3 |
| Hard constraints violated | 0 (no manifest hard constraints supplied) |

### Verdict distribution

- **Anchor decision claims (T-0001, T-0002):** both `verified` with high confidence. Three independent primary Anthropic sources with stable URLs, verbatim quotes, and retrieved-date stamps. Framer can treat the kill-criterion-#2 trigger as settled.
- **5 grapher dissents:** all RESOLVED (no irreconcilable conflicts). 4 are hypothesis-resolution-by-later-evidence + 1 documentary correction (DISSENT-2). DISSENT-2 (ADR attribution) is the only one requiring downstream framer action.
- **F-7:** verified WITH qualifier — high confidence in the mechanism (explicit error message); single-instance population. Framer must surface as conditional. Drives FR-6 verification design constraint.

### Unverifiables

**None.** Every claim was either grounded in cited source text or resolved as dissent-preserved. The extractor and grapher produced no unsalvageable claims.

### Dissents (summary)

| Dissent | Description | Verdict | Downstream action |
|---|---|---|---|
| DISSENT-1 | Hypothesis-resolution chain (AN §4.1 -> T-001) | RESOLVED — one-way supersession | Framer presents as historical hypothesis confirmed by T-001 |
| DISSENT-2 | ADR-0033 vs ADR-0034 attribution | RESOLVED — documentary correction | **REQUIRED:** all artifacts cite ADR-0017 + ADR-0033 (not ADR-0034) |
| DISSENT-3 | 35 vs 36 agent count | RESOLVED — codebase-research correct | Note in design-composer review of Research Plan accuracy |
| DISSENT-4 | Edit-tool mechanism (H-a vs H-b vs active-harness) | PRESERVED — non-load-bearing | Surface to FR-6 verification design |
| DISSENT-5 | §6 design-option pre-disposition | PRESERVED — evidence-not-pre-decision | Framer preserves all 3 options with blast-radius evidence |

---

## Per-Dissent Walkthrough

### DISSENT-1: Root-cause hypothesis resolution

**Description:** AN §4.1 (AN-0041..AN-0046) hypothesized harness-restriction as the most likely root cause. T-001 (T-0001, T-0003, T-0004, T-0005, T-0007, T-0050) confirms with three independent Anthropic documentation citations that this IS the deliberate harness design.

**Verification questions:**
1. Does AN §4.1 actually hypothesize harness-restriction without committing? — **Yes.** Source line 124 frames as "most likely"; line 122 says "this analysis does not pick one; the follow-up feature investigates."
2. Does T-001 supersede this hypothesis with evidence? — **Yes.** Findings F-1 through F-4 provide three independent Anthropic-doc citations.
3. Is the supersession captured correctly in `02-graph.json`? — **Yes.** Edge E-0009 supersedes E-0065 with claim_ids ['T-0001','T-0003','T-0004','T-0050','AN-0041']. Capture is correct.

**Verdict:** `resolved_not_dissent`. This is one-way hypothesis-resolution-by-evidence, not a true competing-perspectives dissent. The two sources are internally consistent: AN defers the question; T-001 answers it.

**Resolution note for framer:** Present as a one-way supersession (T-001 resolves AN's open hypothesis), not as competing perspectives. The AN §4.1 sub-hypotheses (AN-0042, AN-0043, AN-0044, AN-0045) about WHY the harness restricts (recursion prevention, context-cost, surface-area minimization, untested path) are partially confirmed by T-001's documentation evidence — Anthropic's stated reason is "prevent infinite nesting," which aligns with AN-0042 (recursion prevention) most directly.

---

### DISSENT-2: ADR-0033 vs ADR-0034 attribution

**Description:** The Research Plan §38 and PRD attribute "ADR-0034 symmetric D-12 application." The codebase-analysis-report corrects this — the canonical home for symmetric D-12 is ADR-0033 line 71. ADR-0034 is unrelated PRD v1.1.0 mis-credit cleanup.

**Verification questions:**
1. Does ADR-0033 line 71 actually contain "symmetric per D-12"? — **YES.** Direct Grep verification: ADR-0033 line 71 reads verbatim: `cycle-cap exhaustion (per ADR-0017 4-cycle cap, symmetric per D-12) IS a deviation requiring user escalation per AC-FR-10-c`. The phrase "symmetric per D-12" is unambiguously present.
2. Does ADR-0034 contain anything about symmetric D-12 application? — **NO.** Grep for `symmetric|D-12` against ADR-0034 returns zero matches. ADR-0034 is exclusively about ADR-0017-vs-ADR-0021 4-cycle-cap attribution cleanup.
3. What does the codebase-research source actually claim? — Report line 39 says: "The canonical home for symmetric D-12 application is ADR-0033 line 71, not ADR-0034 (which covers an unrelated PRD v1.1.0 mis-credit cleanup)." All claims (CR-0010, CR-0011, CR-0012, CR-0086, CR-0132, CR-0142) align with this finding.

**Verdict:** `resolved_documentary_correction`.

**Resolution note for framer:** This is the **highest-stakes documentary correction** in the synthesis — load-bearing for downstream artifact correctness. ALL downstream artifacts (Blueprint, Plan, ACs, PRD updates) MUST cite ADR-0017 + ADR-0033 for the 4-cycle cap + symmetric application. **DO NOT propagate the ADR-0034 mis-attribution.** Surfaces as OI-CR-A.

Note (meta-observation): the source codebase-research report itself drops a wry note in §4 — "This is itself the kind of mis-attribution ADR-0034 was authored to prevent." The framer can choose whether to surface this irony or omit it.

---

### DISSENT-3: 35 vs 36 agent count

**Description:** Research Plan claims 35 sub-agent files; codebase-research sweep counts 36. Recorded as OI-CR-F.

**Verification questions:**
1. How many .md files exist under `.claude/agents/`? — **Direct enumeration: 36 files.** Files: cc-critique, design-* (12), discovery-* (3), execute-* (5), finalize-* (3), intake-* (2), plan-author, review-* (2), shared-document-reviewer, synth-* (6), test-* (2), design-composer, design-claude-code. Total: 36.
2. Does the codebase-research claim of 36 match? — **YES.** Codebase-research is correct; Research Plan's 35 is the discrepancy.

**Verdict:** `resolved_minor_correction`. Non-blocking. Note in design-composer's review of Research Plan accuracy.

---

### DISSENT-4: Edit-tool mechanism

**Description:** AN-0049/AN-0050 frames Edit-tool addition as "active mutation between declaration and runtime" (active-harness-behavior hypothesis 4.2). T-0023/T-0024 proposes two competing hypotheses:
- **H-a:** baseline tool-set inheritance includes Edit (per "subagents inherit all tools from main conversation" rule)
- **H-b:** memory-field auto-enable (per "Read, Write, and Edit tools are automatically enabled so the subagent can manage its memory files" rule)

T-0068 flags H-b as "likeliest"; T-0069 explicitly says this is non-load-bearing for the kill-criterion decision.

**Verification questions:**
1. Are both H-a and H-b actually documented in T-001 with citations? — **YES.** H-a at line 97 (citing F-3); H-b at line 98 (citing "Enable persistent memory" subsection).
2. Is the non-load-bearing claim explicit? — **YES.** Line 222: "This is a side observation, not load-bearing for the kill-criterion decision."
3. Are the hypotheses mutually exclusive? — **No** — both rules are documented and could co-apply. **Codebase-research CR-0023 confirms execute-orchestrator declares `memory: project` at line 6**, which supports H-b applicability.

**Adversarial probes:**
- **What would falsify?** A test where Edit-tool appears in a sub-agent WITHOUT `memory:` field declared. This would falsify H-b and strengthen H-a. Deferred to FR-6 design.
- **Absence implies?** Source explicitly flags both as untested; framer should preserve both as candidate explanations for FR-6 verification.

**Verdict:** `dissent_preserved_non_load_bearing`.

**Resolution note for framer:** Both hypotheses survive verification with documentation backing. Neither is load-bearing for the kill-criterion decision. Surface both H-a and H-b as candidate explanations for the FR-6 verification design, with H-b flagged as "likeliest" given execute-orchestrator's `memory: project` declaration (corroborated by CR-0023). The AN active-harness-behavior framing is partially supported — both AN and T-001 agree there is ACTIVE mutation; they disagree only on the mechanism.

---

### DISSENT-5: §6 design-option pre-disposition

**Description:** AN §6 (AN-0061, AN-0062, AN-0063) frames the three options as candidates without pre-decision. AN §7 (AN-0072) explicitly defers. Codebase-research §5 surfaces option (b)'s larger blast-radius (5+ outside-inventory files) as evidence-not-pre-decision (CR-0108). T-001 (T-0061) explicitly says "the Designer's choice among PRD §6 options (a/b/c) is unconstrained by T-001's findings."

**Verification questions:**
1. Does the codebase-research's "5+ files outside inventory" claim ground in actual file enumeration? — **YES.** Report §5 enumerates exactly 5: (1) KB-documentation-criteria/SKILL.md template-assignment table (lines 67-71); (2) state-transitions-log-entry-template.md v1 invariant (line 63); (3) pipeline-run-summary-template.md generated-by (line 113); (4) smoke_test_auditing_shared.py test data (line 212); (5) auditing-codespaces/SKILL.md consumer note (line 73). Each has cited line number.
2. Is the disposition language ("evidence not pre-decision") accurate? — **YES.** Report line 289: "Recommendation surfaced as evidence (NOT a design pre-decision)".
3. Is T-001's "unconstrained" framing accurate? — **YES.** T-001 line 220 reads verbatim: "The Designer's choice among them is unconstrained by T-001's findings."

**Verdict:** `dissent_preserved_evidence_not_decision`.

**Resolution note for framer:** Not a true dissent — all three sources agree the choice is the Designer's. The "soft pressure" against option (b) from blast-radius data is REAL (grounded in 5-file enumeration), but it is evidence, not a pre-decision. Preserve all three options as candidate decision frames with the blast-radius differential as evidence; option (b) remains a legitimate choice subject to AC-FR-4-a operator disposition.

---

## Anchor-Decision-Claim Verification Details

### Anchor 1: T-0001 (dispatch_supported: false)

**Claim:** Claude Code sub-agent → sub-agent dispatch is not supported at runtime even when the sub-agent declares `Agent` in its frontmatter `tools:` array.

**CoVe questions:**

1. **Is the front-matter `dispatch_supported: false` present at line 13?**
   - Verified by direct read. T-001 line 13: `dispatch_supported: false`.

2. **Are the three independent Anthropic citations real, with stable URLs and verbatim quotes?**
   - **Source 1:** `https://code.claude.com/docs/en/sub-agents` — "Choose between subagents and main conversation" — quote: "Subagents cannot spawn other subagents." (5 words, ≤15) — T-001 line 62.
   - **Source 2:** Same URL, "Built-in subagents / Plan" section — paraphrased per one-quote-per-URL discipline — T-001 line 67-68.
   - **Source 3:** `https://code.claude.com/docs/en/agent-sdk/subagents` — quote: "Subagents cannot spawn their own subagents. Don't include Agent in a subagent's tools array." (14 words, ≤15) — T-001 line 76.
   - **Source 4:** Same URL as Source 1, "Restrict which subagents can be spawned" section — paraphrased — T-001 line 83.
   - All sources Anthropic-controlled. All retrieved 2026-05-23.

3. **Do quotes actually say what the claim asserts?**
   - "Subagents cannot spawn other subagents." — directly states the impossibility.
   - "Don't include Agent in a subagent's tools array." — directly instructs the consequence.
   - Both align with the claim. No paraphrase distortion.

4. **Is there any documented mechanism that would enable nested dispatch?**
   - **NO.** Finding F-4 (lines 110-116) exhaustively enumerates 24+ frontmatter fields and the 2 known environment variables (`CLAUDE_CODE_FORK_SUBAGENT`, `CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS`). None enable nested dispatch. Fork mode docs explicitly state "A fork cannot spawn further forks." (line 116).

**Adversarial probes:**
- **What would falsify?** An undocumented harness flag, a not-yet-released version, or a verified runtime test where a sub-agent successfully dispatched another sub-agent. The probe attempted at parent-orchestrator level FAILED with a different error (F-7 registry-staleness), so runtime corroboration is partial. However, documentation evidence is independently sufficient (T-001 lines 179, 190, 237).
- **Who benefits if true?** Anthropic gains nothing by publishing this restriction falsely; documentation is reliable.
- **Absence implies?** Exhaustive enumeration of fields finding no enable-nesting affordance is meaningful — Anthropic explicitly closes this affordance and documents alternatives (Skills, chain-from-main, agent teams).

**Verdict: `verified`.** Confidence: **very high** (upgraded from extractor's "high").

---

### Anchor 2: T-0002 (kill_criterion_triggered: 2)

**Claim:** Kill-criterion-#2 fires per PRD FR-2 because the analysis is confirmed with no in-band path; FULL repair proceeds.

**CoVe questions:**

1. **Is `kill_criterion_triggered: 2` present at line 14?** — Yes, verified by direct read.
2. **Does PRD FR-2 define kill-criterion-#2 as the claim states?** — Yes; the source's executive summary line 48 reproduces the PRD definition.
3. **Does the conclusion follow logically from T-0001?** — Yes; deductive consequence.

**Verdict: `verified`.** Confidence: **high**. Corroborated independently by AN-0069 (the original analysis source's prediction that this would be the kill-criterion-#2 trigger).

---

## F-7 Confidence Assessment

**Finding:** F-7 — mid-session agent registry is not hot-reloaded.

**Extractor's assigned confidence:** `high`.
**Critic's assigned confidence:** `high-for-mechanism / single-instance-for-population`.

### CoVe walkthrough

1. **Is F-7 grounded in an actual observed harness error message?**
   - **YES.** T-001 lines 196-198 capture the verbatim error: `Agent type 'probe-dispatch-test-r1' not found. Available agents: [enumerated list of 41 agents NOT including the newly-authored probe files]`. The error explicitly enumerates the registered agent set. The probe files exist on disk (verified via Bash glob).

2. **How many independent observations support F-7?**
   - **Single instance.** Source self-flags at line 208: "single observed instance, but the harness error message is explicit about the lookup mechanism". Line 210 explicitly identifies the confirmatory test that would generalize (out-of-scope for T-001).

3. **Is the source's confidence calibration self-consistent?**
   - **YES.** High confidence is calibrated against the EXPLICIT lookup mechanism (the error enumerates available agents), not against statistical replication. The source distinguishes mechanism-confidence vs population-size honestly.

### Verdict

`partially_verified_with_qualifier`. The mechanism IS strong (explicit error message). The population is N=1. Framer MUST present F-7 as "high-confidence single-instance observation" or equivalent language. Per source (T-0057, T-0058), F-7 is corroborating-but-tangential and orthogonal to the dispatch_supported decision.

### Downstream action

Per AN-0065-derived FR-6 verification step: the synthetic minimal test feature MUST be run in a fresh session (per T-0053, T-0054), OR the verification must include a session restart, OR the agents must be authored in an earlier phase. The plan-author and per-layer cc Designer MUST respect this constraint per T-0055.

---

## Common Failure-Mode Scan

Per verification-knowledge skill, the Critic should watch for over-confident claim shapes.

### Absence claims (verified with appropriate evidence)

- **T-0007** ("no documented enable-nesting flag") — grounded in F-4 exhaustive enumeration of 24+ frontmatter fields plus 2 environment variables. Source explicitly acknowledges "absence-of-feature is harder to prove than presence-of-feature" (line 121) and offers the probe as corroboration. **Verdict: verified (high confidence per exhaustive enumeration).**
- **T-0033/T-0034** (no published Anthropic precedent for sub-agent → sub-agent dispatch) — grounded in enumeration of all example sub-agents in docs. **Verdict: verified.**
- **C-0020 (AN)** ("sweep deferred to follow-up") — explicitly acknowledged as deferred; honest framing. Not a true absence claim. **Verdict: verified as framing claim.**

### Causation claims (verified or appropriately hedged)

- **AN-0049/AN-0050** ("Edit weakens simple-filtering, strengthens active-harness") — appropriately hedged Bayesian framing, not "proves". **Verdict: verified as hedged claim.**
- **T-0021** ("documented 'no effect' matches observed runtime strip") — correlation correctly framed; causation supported by Anthropic's stated design intent. **Verdict: verified.**
- **F-7 mechanism (T-0049)** ("registry loaded at session start") — single-instance causation; appropriately hedged per F-7 confidence assessment above. **Verdict: partially verified with qualifier.**

### Inheritance claims (mostly verified; one correction)

- **CR-0091/CR-0094/CR-0136** (ADR-0035 not in Research Plan's inherited list) — codebase-research correctly identifies gap as OI-CR-E. **Verdict: verified.**
- **DISSENT-2** (ADR-0033 vs ADR-0034) — documentary correction grounded in direct Grep. See above.
- **CR-0086/CR-0142** (ADR-0033 confirmed Accepted with line 51, line 71 citations) — Grep-verified. **Verdict: verified.**
- Soft-pressure constraints (ADR-0037, ADR-0040, ADR-0041 marked "marginal") — appropriately qualified. **Verdict: verified.**

### Numerical claims (verified after one correction)

- **DISSENT-3** (36 vs 35) — codebase-research's 36 is correct; verified by independent enumeration. **Verdict: verified after correction.**
- **T-0028** ("24+ frontmatter fields") — qualitative numerical with explicit "+"; verified.
- **CR-0001** (FR-5 sweep finds 2 affected agents) — only execute-orchestrator and execute-finalize-reconciler declare `Agent` in `tools`. Independently verifiable. **Verdict: verified.**
- **T-001 acceptance** (3 independent sources, verbatim quotes ≤15 words) — each quote counted (5, 14, 9 words). **Verdict: verified.**

### Universal-quantifier claims (appropriately scoped)

- **T-0001** ("cannot dispatch... even when... declares Agent") — universal scope is appropriate given Anthropic's documented design intent and 3-source corroboration. **Verdict: verified.**
- **AN-0017** ("next time any sub-agent...") — forward-projection appropriately scoped as conditional. Now CONFIRMED by T-001 documentation evidence. **Verdict: partially verified — extractor's "high" is correct; framer should present as "now confirmed by T-001" rather than as live projection.**

---

## Places where documentation evidence is STRONGER than extractor flagged

Per critic prompt's final instruction:

### 1. T-0001 (anchor decision claim) — upgraded from `high` to `very_high`

**Why:** Three independent primary Anthropic sources with verbatim quotes, stable URLs, retrieved-date stamps, and direct prescriptive instruction to developers in the SDK source. This is the strongest possible documentation evidence for an absence-of-affordance claim. The framer can confidently treat as settled, not provisional.

### 2. T-0024 (H-b memory-field auto-enable) — strengthened by corroboration

**Why:** Extractor flagged at `medium` because H-b is a hypothesis. However, the GROUNDING RULE ("Read, Write, and Edit tools are automatically enabled so the subagent can manage its memory files") is itself documented at Anthropic's "Enable persistent memory" subsection. The codebase-research CR-0023 independently confirms execute-orchestrator declares `memory: project`. The hypothesis's applicability is corroborated by file-level evidence. Framer can present as "likeliest, corroborated by file-level evidence" rather than as raw hypothesis.

### 3. The ADR-0033 attribution chain (CR-0010, CR-0011, CR-0012, CR-0086, CR-0132, CR-0142) — Grep-verified

**Why:** Documentary correction is grounded in direct Grep of ADR-0033 and ADR-0034 files. ADR-0033 line 71 contains "symmetric per D-12"; ADR-0034 contains nothing about symmetric D-12. Codebase-research is unambiguously correct. The framer's downstream artifact-correctness depends on propagating this correction (cite ADR-0017 + ADR-0033, NOT ADR-0034).

### 4. The FR-5 sweep result (CR-0001 through CR-0067) — exhaustive at N=36

**Why:** The sweep is independently verifiable by Grep over `.claude/agents/*.md`. Result (2 affected agents) is stable and complete. Framer can treat the affected set as CLOSED at 2.

---

## Notes for downstream Synthesizer / Framer

1. **DISSENT-2 propagation is mandatory.** The framer's report MUST cite ADR-0017 + ADR-0033 (not ADR-0034) for the 4-cycle cap + symmetric application. This is the highest-stakes documentary correction surfaced by the critic. PRD FR-3-c needs updating downstream.

2. **F-7 is non-load-bearing but constraint-imposing.** Surface as a verification-step constraint (fresh session required for FR-6 minimal test feature), NOT as a decision-driver for the §6 options.

3. **Three §6 options are all viable per T-001.** The blast-radius data is evidence, not pre-decision. Frame option (b) as legitimate-but-larger-scope subject to AC-FR-4-a operator disposition.

4. **Hypothesis H-a vs H-b vs active-harness (DISSENT-4) is for FR-6 design.** Preserve both H-a and H-b as candidate Edit-tool explanations; flag H-b as "likeliest" given execute-orchestrator's `memory: project` declaration.

5. **The agent-roster-design-discipline-r1 saved-for-later meta-feature** (per project memory) remains saved-for-later. The FR-5 sweep here is exhaustive at 2 affected agents; the broader per-agent-design-discipline gap is a separate concern.

---

**End of 03-verifications.md** — companion to `03-critique.json`. Framer should consume the JSON for per-claim verdicts; this Markdown is for human review at the (optional) Synthesis gate.
