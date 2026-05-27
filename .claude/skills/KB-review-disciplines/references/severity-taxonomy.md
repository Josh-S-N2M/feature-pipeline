# Severity Taxonomy

## Contents

- The three values
- How severity interacts with verdict
- When to use `critical` vs `important`
- Category dimension (separate from severity)
- Severity inflation: how to avoid it
- Severity downgrade rules
- Severity upgrade rules
- Threshold mapping reference (canonical)

Three severity values, used identically by all three reviewers. This file is the canonical source for severity definitions and the score-to-verdict mapping.

## The three values

| Value | Use when... | Example |
|---|---|---|
| `critical` | The issue blocks acceptance. Architecturally wrong, security-breaking, contract violation, or fundamentally infeasible. Cannot be deferred or accepted with conditions — must be fixed. | Real credential in a sample; fabricated API call; AC contradicts an FR; Gate 0 structural failure |
| `important` | The issue should be fixed before approval but isn't architecturally fatal. Degrades the score. Can be deferred only with explicit user approval and a tracked ledger entry. | Missing dependency declaration; ambiguous error contract; cross-artifact terminology mismatch; missing N/A justification on an out-of-scope section |
| `recommended` | Improvement suggestion. Non-blocking. Documents are approvable with `recommended` issues outstanding. | Clarity polish; alternative formulation; forward-link suggestion; stylistic improvement |

## How severity interacts with verdict

Verdict (`approved` / `approved_with_conditions` / `needs_revision` / `rejected`) is determined by severity counts and quality scores TOGETHER, per the mapping below.

| Severity present | Quality scores | Verdict |
|---|---|---|
| Any `critical` | Any | `needs_revision` (or `rejected` for fundamental problems) |
| No `critical`; `important` only; small count | Consistency > 80 AND Completeness > 75 AND no rule violations of high severity | `approved_with_conditions` |
| No `critical`; only `recommended` | Consistency > 90 AND Completeness > 85 AND no rule violations | `approved` |
| Many `critical` issues; fundamental rework needed | Any | `rejected` |

A reviewer cannot override this mapping. If the issue counts and scores indicate `needs_revision`, the verdict is `needs_revision` regardless of the reviewer's overall impression.

## When to use `critical` vs `important`

The line: "would I refuse to merge a PR with this issue?"

- Yes → `critical`
- "I'd merge it but file a follow-up ticket" → `important`
- "I'd merge it; the follow-up is optional" → `recommended`

Common false-`critical` patterns:

- "This style is wrong" — not critical unless it violates an explicit project rule. Usually `recommended`.
- "I'd have done this differently" — preference, not a defect. `recommended` or omit.
- "This is technically correct but suboptimal" — `important` or `recommended`, never `critical`.

Common under-severity patterns:

- "There's a typo in a function name in the sample" — if the function name is referenced elsewhere in the doc with the correct spelling, that's a `critical` consistency violation, not a typo. Reader cannot tell which is canonical.
- "The Layer Scope says Frontend is in scope but no Frontend AC exists" — `critical` completeness, not `important`. A scoped layer with no AC will silently get no per-layer Design designer.

## Category dimension (separate from severity)

Each issue ALSO has a category — what kind of issue, not how bad. Five values:

| Category | Meaning |
|---|---|
| `consistency` | Document contradicts itself or another document |
| `completeness` | Required element missing or insufficiently developed |
| `compliance` | Violates a project rule, template requirement, or KB convention |
| `clarity` | Document is ambiguous or hard to act on |
| `feasibility` | Technical or resource concerns about the proposal |

Severity and category are independent — you can have a `recommended/clarity` issue (e.g. suggesting better section title) and a `critical/consistency` issue (e.g. AC contradicts FR) in the same document.

## Severity inflation: how to avoid it

A reviewer who marks everything `critical` produces unactionable output. The orchestrator sees 27 critical issues and has no way to prioritize. Calibration anchors:

- **`critical` budget per document review:** at most 5. If more issues qualify, the document is likely fundamentally broken — emit `rejected` and stop.
- **`important` budget per document review:** at most 15. More than 15 important issues suggests the document needs `needs_revision` regardless of severity.
- **`recommended`:** no budget, but cluster related recommendations (one issue saying "five terminology improvements" is better than five separate issues).

These are calibration targets, not hard limits. Exceptional documents may warrant more issues; the budget is a sanity check.

## Severity downgrade rules

Auditors MAY downgrade a severity when:

1. The issue is mitigated elsewhere in the document (e.g. an `important` consistency issue is downgraded to `recommended` if a later section reconciles it explicitly)
2. The issue is bounded by an existing ADR or open item that captures the followup
3. The user has explicitly accepted the deviation in the rationale brief

Auditors MUST NOT downgrade when:

- The issue is one of the three auto-fail conditions in KB-general-coding-principles (real credentials, fabricated API, naked production URL)
- The issue is a Gate 0 structural failure
- The issue contradicts a user-confirmed decision in the rationale brief

## Severity upgrade rules

Auditors MAY upgrade a severity when:

1. The issue interacts with an unresolved prior issue, making both more serious in combination
2. The issue blocks a downstream layer or stage that's already started work
3. The issue affects external consumers (other teams, partners, end users)

Each upgrade or downgrade is recorded in the issue's `severity_history` field if the reviewer adjusted from the auto-derived value.

## Threshold mapping reference (canonical)

For convenience, the score→verdict mapping from the shared-document-reviewer template, restated here:

```
APPROVED
  Gate 0: all pass
  Consistency > 90
  Completeness > 85
  Rule compliance: no severity:high
  Issues: no `critical`
  Prior context: all critical/major resolved

APPROVED_WITH_CONDITIONS
  Gate 0: all pass
  Consistency > 80
  Completeness > 75
  Rule compliance: only severity:medium or below
  Issues: only easily-fixable
  Prior context: at most 1 important unresolved

NEEDS_REVISION
  Gate 0: any fail OR
  Consistency < 80 OR
  Completeness < 75 OR
  Rule compliance: any severity:high OR
  Issues: any `critical`, or many `important` OR
  Prior context: 2+ important unresolved OR any critical unresolved OR
  complexity_level medium/high but complexity_rationale insufficient

REJECTED
  Fundamental problems
  Requirements not met
  Major rework needed
```

All three reviewers share this mapping. The architecture and cross-artifact auditors typically don't score `clarity` (their concern is correctness, not prose), so their score totals weight consistency, completeness, and rule compliance more heavily.

---

## Cross-Surface Severity Bridge Table

> **Authoritative source:** [ADR-0061](../../../../adrs/ADR-0061-severity-vocabulary-bridge-table.md) — prescribes this file as the canonical host.
>
> **Derivation sources:** `working/feature/pipeline-design-time-discipline-r1/cc-design.md` §Severity bridge table content; `working/feature/pipeline-design-time-discipline-r1/synthesis.md` §Severity Bridge Content (D-10 substrate); `working/feature/pipeline-design-time-discipline-r1/blueprint-v1.md` §Severity bridge content.
>
> **Phase:** pipeline-design-time-discipline-r1 (R2a) / Plan §Phase 1 / T1.1

Three severity vocabularies coexist in the pipeline. Each serves a different audience and must NOT be collapsed into a single vocabulary (ADR-0061 rationale: audience-fit is load-bearing). This section documents the monotonic mappings and explicitly enumerates the non-monotonic edges.

| Vocabulary surface | Values | Primary consumer |
|---|---|---|
| **Auditor vocabulary** | `BLOCKER` / `MAJOR` / `MINOR` / `NIT` / `INFO` | `review-architecture-auditor`, `review-cross-artifact-auditor`, `auditing-mcp`, `auditing-cc-configs`, `auditing-shared`, `auditing-subagents`, `auditing-skills` |
| **Reviewer vocabulary** | `critical` / `important` / `recommended` | `shared-document-reviewer`; Gate 0/1 procedure in `KB-review-disciplines` |
| **Phase-Validator (PV) vocabulary** | `blocking` / `warning` / `informational` | `test-phase-validator-author`; stage-transition gate decisions in `execute-orchestrator` |

### Five-Column Bridge Table

| `auditor_vocab` | `reviewer_vocab` | `pv_vocab` | `non_monotonic_edges` | `iteration_delta_weight` |
|---|---|---|---|---|
| `BLOCKER` | `critical` | `blocking` | — Monotonic; forces refuse-to-advance across all three surfaces. `BLOCKER ↔ critical ↔ blocking` is the strictest tier in each vocabulary with consistent gate-blocking intent. | **10** |
| `MAJOR` | `important` | `blocking` OR `warning` | **MAJOR → {blocking, warning}** — PV-side branch by failure class: `blocking` when the failure is an outright assertion-not-satisfied (required predicate emitted False); `warning` when failure is partial or soft (predicate emitted True with caveat notes). Default: `MAJOR → blocking`; downgrade to `warning` only with explicit per-finding rationale. Translator requires the `assertion_failure_mode` as an input parameter; ambiguity surfaces as an explicit translator error rather than a silent collapse. | **3** |
| `MINOR` | `recommended` | `warning` | — Monotonic. Lowest non-zero severity tier; consistent non-blocking-but-actionable intent across all three surfaces. | **1** |
| `NIT` (used by `auditing-mcp`) | `recommended` | `informational` | **NIT ↔ recommended translation difficulty.** Reviewer `recommended` carries "improvement" framing (actionable); `NIT` carries "taste" framing (subjective / low-priority). Reverse mapping `recommended → NIT` loses actionability. A notional `translate_severity.py` (see §Translator Utility below) would surface "taste-vs-improvement" as an explicit rationale field in its output. | **0** (not used in iteration-delta math) |
| `INFO` (used by `review-architecture-auditor`, `review-cross-artifact-auditor`) | (no direct equivalent — surfaced as neutral diagnostic, not an issue) | `informational` | **NIT vs INFO intra-auditor divergence.** `auditing-mcp` uses `NIT` (verdict-compute weight -0.5); architecture-auditor and cross-artifact-auditor use `INFO` (weight 0). Same conceptual severity floor; different naming and score impact. `verdict_compute.py` is the canonical union: BLOCKER/MAJOR/MINOR/NIT/INFO. Documented per codebase-analysis Known Issue 2 — preserved rather than collapsed. | **0** |

**Intra-auditor divergence note.** `review-architecture-auditor` and `review-cross-artifact-auditor` emit BLOCKER/MAJOR/MINOR/INFO (no NIT); `auditing-mcp` uses BLOCKER/MAJOR/MINOR/NIT (no INFO). `verdict_compute.py` is the canonical union of both.

### Verdict-Compute Weights

These are the points the verdict-compute machinery deducts when computing the gate-pass score (per `auditing-cc-configs/scripts/verdict_compute.py`). These are a **separate weight set** from the iteration-delta weights above — see the Weight Preservation Note.

| Severity | Verdict-compute deduction | Notes |
|---|---|---|
| `BLOCKER` | **-12** per occurrence | Additional **-12 escalation penalty** when the BLOCKER persists across iterations = **-24 total** for a persisting BLOCKER |
| `MAJOR` | **-5** | |
| `MINOR` | **-2** | |
| `NIT` | **-0.5** | |
| `INFO` | **0** | Diagnostic only; surfaced but not score-impacting |

**Verdict thresholds:**

| Score range | Verdict |
|---|---|
| 95+ | PASS |
| 85–94 | PASS-WITH-MINOR-FIXES |
| 70–84 | NEEDS-WORK |
| < 70 | FAIL |

### Weight Preservation Note

**Both weight sets remain because they encode mathematically independent roles. DO NOT collapse them into one set.**

- **Verdict-compute weights** (-12 / -5 / -2 / -0.5 / 0) drive the **single-iteration gate-pass / fail computation**. They answer "is this iteration's audit verdict PASS or FAIL?" by summing per-finding deductions against a fixed score floor. The deduction values are calibrated against the pipeline's existing gate-pass thresholds; collapsing or rebalancing them would require recalibrating every downstream gate-pass rubric.

- **Iteration-delta weights** (10 / 3 / 1 / 0 / 0) drive the **convergence / cap-tripping logic across iterations** in the 4-cycle reconciliation cap (per `review-cross-artifact-auditor`). They answer "is the audit converging or oscillating?" by tracking total-weight-resolved vs total-weight-introduced per cycle. These values encode reconciliation effort, not gate-pass arithmetic.

The two roles are mathematically independent. Collapsing them forces one of two losses: (a) gate-pass thresholds become a function of how many cycles have run — breaking per-iteration determinism; or (b) convergence-tracking becomes coarse-grained on the BLOCKER vs MAJOR distinction — breaking 4-cycle cap intent. Preserving both is the required separation of concerns.

### Non-Monotonic Edges (Explicit Enumeration)

The following edges are explicitly NOT monotonic and must be documented at every translation site. A future optional translator utility (if authored under `.claude/skills/auditing-shared/scripts/`) should surface each as an explicit rationale field rather than silently collapsing.

1. **NIT vs INFO intra-auditor divergence.** `auditing-mcp` uses `NIT` (verdict-compute deduction -0.5); `review-architecture-auditor` and `review-cross-artifact-auditor` use `INFO` (deduction 0). Same conceptual severity floor; different naming and score impact. The translator records the source-auditor surface as context. Documented per codebase-analysis Known Issue 2 — preserved, not collapsed.

2. **NIT ↔ recommended.** Reviewer vocabulary's `recommended` is the closest match for `auditing-mcp`'s `NIT`, but reviewer-side `recommended` is intended as actionable; NIT-class findings are explicitly low-priority / subjective. The translator outputs an explicit "NIT — non-actionable in reviewer surface" rationale. Reverse mapping `recommended → NIT` is lossy (loses actionability).

3. **MAJOR → {blocking, warning}.** PV vocabulary branches on `MAJOR`: `blocking` if failure is an outright assertion-not-satisfied; `warning` if partial / soft failure. The translator requires the `assertion_failure_mode` as an input parameter; ambiguity surfaces as an explicit translator error rather than a silent default.

### Bridge Consumers

24 agents load `KB-review-disciplines` (per codebase-analysis `blast_radius_new_confirmations[4]`, post-cycle-1 reconciliation — adds `execute-orchestrator`, `review-cross-artifact-auditor`, `intake-intent-clarifier`, `test-acceptance-author` to the prior 20-agent count). The bridge propagates broadly with no separate propagation work.

Primary finding-emitting consumers that reference this bridge by name:

- **FR-1** (`review-architecture-auditor`) — design-realization audit findings (BLOCKER / MAJOR per companion-file assertions)
- **FR-9** (`execute-orchestrator`) — Blocks-X unresolved-marker findings (BLOCKER)
- **FR-10** (`auditing-subagents` SA-14 rule) — matrix-missing / row-count-mismatch findings (BLOCKER)
- **R2b** (FR-4, FR-5 — queued `pipeline-gate-validator-hardening-r1`) — inherits the populated bridge

### Translator Utility (Optional)

An optional helper (notional file under `.claude/skills/auditing-shared/scripts/`) could perform mechanical cross-surface translation at `audit-issues.json` emission time — reading source vocabulary + target audience and emitting target vocabulary per this bridge table, with non-monotonic edges surfaced as explicit rationale fields. No such helper has been authored yet; this paragraph documents the design intent for the future implementer. This bridge table is the single source of truth either way.

---

## NFR-8 Four-Field Finding Shape

> **Authoritative sources:** [ADR-0061](../../../../adrs/ADR-0061-severity-vocabulary-bridge-table.md) §Co-location rationale; `working/feature/pipeline-design-time-discipline-r1/blueprint-v1.md` §Severity bridge content.
>
> **Co-location rationale (ADR-0061):** The same agents that consume the bridge (severity translation) also need the field shape (finding emission). Co-locating both in this file keeps the dependency local and avoids a cross-file lookup at emission time.
>
> **Phase:** pipeline-design-time-discipline-r1 (R2a) / Plan §Phase 1 / T1.2

Every finding emitted by the three BLOCKER-emitting rules (FR-1, FR-9, FR-10) MUST include all four fields. The fields are additive sub-fields under `issues[]` in `audit-issues.json`; the schema extension is structurally safe across all known downstream consumers.

| Field | Semantics | Example |
|---|---|---|
| `rule` | The rule identifier — namespaced by emitter family | `FR-1.audit.design_realization_mismatch` |
| `target` | The file path or symbol the finding addresses | `audit_op2_consumer_mapping.py` |
| `divergence` | What is wrong — the observed-vs-expected mismatch, stated concretely | `script references removed server mcp-openapi-schema; ADR-0041 removed it on 2026-05-24` |
| `next_action` | What the consumer should do to resolve the finding | `Remove the consumer-mapping entry or restore the server with explicit justification` |

### Field rules

- **`rule`** MUST be non-empty and use dot-separated namespacing. Pattern: `<emitter-family>.<category>.<specific-rule>`. Examples: `FR-1.audit.design_realization_mismatch`, `SA-14.matrix_missing`, `BX.malformed_marker`.
- **`target`** MUST be non-empty. Use a relative file path when the finding addresses a file; use a symbol identifier (e.g. `ClassName.method_name`) when the finding addresses a symbol. Do NOT use placeholder strings (`TODO`, `TBD`, empty string).
- **`divergence`** MUST state the observed state AND the expected state. Do not re-state the rule name. Provide enough detail that a reader without context can understand what is wrong.
- **`next_action`** MUST be actionable. Do not use passive constructions such as "this should be reviewed". Use imperative constructions: "Remove X", "Add Y to Z", "Restore W with explicit justification".

### Consumers

The following emitters are bound to this four-field shape. Acceptance tests verify that each emitter's BLOCKER findings honor the contract:

| Emitter | Rule family | Acceptance tests |
|---|---|---|
| **FR-1** (`review-architecture-auditor`) — design-realization audit findings | `FR-1.audit.*` | AT-029 |
| **FR-9** (`execute-orchestrator`) — Blocks-X unresolved-marker findings | `BX.*` | AT-030 |
| **FR-10** (`auditing-subagents` SA-14 rule) — matrix-missing / row-count-mismatch findings | `SA-14.*` | AT-031 |
| **FR-6** (`design-claude-code` gate) — agent-roster-impact-matrix cell-discipline findings | `FR-6.*` | AT-032 |

All four emitters are verified by AC-NFR-8-a (AT-029..AT-032). A finding from any of these emitters that is missing any of the four fields, or that contains a placeholder value, is a rule violation.

---

## Update History

| Version | Date | Change | Reference |
|---|---|---|---|
| Added §Cross-Surface Severity Bridge Table | 2026-05-27 | Additive: five-column bridge table, verdict-compute weights, weight preservation note, non-monotonic edges enumeration, bridge consumer set. Authored per ADR-0061 + pipeline-design-time-discipline-r1 (R2a) Plan §Phase 1 / T1.1. | ADR-0061; cc-design.md §Severity bridge table content; synthesis.md §Severity Bridge Content (D-10 substrate) |
| Added §NFR-8 Four-Field Finding Shape | 2026-05-27 | Additive: four-field shape table (rule / target / divergence / next_action), field rules, consumer table with AT-029..AT-032 cross-references. Authored per ADR-0061 + pipeline-design-time-discipline-r1 (R2a) Plan §Phase 1 / T1.2 / AC-NFR-8-a. | ADR-0061; blueprint-v1.md §Severity bridge content |
