# Architecture Audit — CoVe + Blast-Radius + Brief-Honor

## Contents

- When this runs
- The three techniques in combination
- Lens 1 — CoVe (Chain of Verification)
- Lens 2 — Blast-Radius Analysis
- Lens 3 — Brief-Honor Verification (per ADR-0009)
- Output JSON
- Iteration with finalize-reconciler
- When NOT to apply this discipline

The substantive audit discipline used by `review-architecture-auditor` during the Architecture Audit phase of the feature-pipeline. Runs after the Design Composition document-reviewer pass on the Blueprint has succeeded (Gate 0/1 verdict ≥ `approved_with_conditions`). This stage is about architectural correctness, not structural correctness.

## When this runs

The Architecture Audit pass is invoked once after Design Composition's `shared-document-reviewer` returns `approved` or `approved_with_conditions`. It runs against:

- the Blueprint v(N) — the document under audit
- the synthesis claims from Synthesis — the ground truth this Blueprint should reflect
- the rationale brief — the commitments the orchestrator carried forward
- the codebase analysis JSON from Discovery Research — facts about what exists today
- the issues-ledger — prior open issues with `category: architecture`

It iterates with `finalize-reconciler` (Reconciliation) when issues need resolution. Four-cycle hard cap per ADR-0006.

## The three techniques in combination

The discipline name "CoVe + blast-radius + brief-honor" is one auditor running three lenses in sequence on the same Blueprint. They are not three separate passes — they share input loading and produce a single output JSON.

```
Inputs: Blueprint v(N), synthesis claims, rationale brief, codebase analysis
                                  │
                                  ▼
              ┌──────────────────────────────────────┐
              │  Lens 1: CoVe (decision verification)│
              │  Lens 2: Blast-radius analysis       │
              │  Lens 3: Brief-honor verification    │
              └──────────────────────────────────────┘
                                  │
                                  ▼
                       Single issues array + verdict
```

## Lens 1 — CoVe (Chain of Verification)

**Goal:** verify every substantive architectural claim in the Blueprint can be re-grounded against the synthesis claims and the codebase.

### Procedure

For each substantive claim in the Blueprint (claims about behavior, performance, dependencies, integration points):

1. **Generate a verification question.** "If this claim is true, what evidence in synthesis or codebase would confirm it?"
2. **Answer the question independently** using the synthesis claims index and Grep/Glob against the codebase. Do NOT just re-read the Blueprint — that would be circular.
3. **Compare** the independent answer to what the Blueprint claims.

Three outcomes:

| Comparison | Action |
|---|---|
| Independent answer matches Blueprint claim | Pass; record the verification (for traceability) |
| Independent answer contradicts Blueprint claim | `critical` issue, category `consistency` |
| Independent answer is inconclusive (no evidence either way) | `important` issue, category `feasibility` — claim is unverified, may be speculation |

### What counts as a "substantive claim" requiring verification

- Statements about existing system behavior ("the cache invalidates on write")
- Claims about external dependencies' contracts ("the Stripe API returns ... on this code path")
- Performance assertions ("query completes in p95 < 50ms with the new index")
- Compatibility claims ("the migration is backward-compatible for old readers")
- Cross-layer assumptions ("the API rate-limits at 100 req/s per the API design")

What does NOT need CoVe (covered by other lenses or by Gate 0/1):

- Decisions the Blueprint is making (those go through brief-honor)
- New behavior the Blueprint is defining (no prior evidence exists; verify via brief)
- Style / prose / formatting (covered by Gate 1's clarity score)

### Time budget

CoVe is the most expensive lens. Budget proportionally to the Blueprint size:

- Small Blueprints (< 1000 lines): verify every substantive claim
- Medium (1000–3000): sample 70% of substantive claims, prioritizing claims that downstream layers depend on
- Large (> 3000): sample 50%, prioritize as above + claims about state-changing operations

Sampling strategy is recorded in the output JSON's `metadata` so the reviewer during the Cross-Artifact Audit pass can see what was checked.

## Lens 2 — Blast-Radius Analysis

**Goal:** enumerate everything that touches the components the Blueprint proposes to change, then confirm the Blueprint acknowledges those impacts (in Change Impact Map / Interface Change Matrix / Field Propagation Map).

### Procedure

1. **Identify "change targets"** — the components the Blueprint says it modifies. Source: Blueprint's Change Impact Map's `Change Target` field, and any component in Main Components whose subsection says "modified" or "replaced."

2. **Query serena** for the blast radius of each change target. Use `mcp__serena__find_referencing_symbols` against the target's identifier for the direct 1-hop reverse-dependency set; iterate per caller to discover 2- and 3-hop dependents. If serena is unavailable, fall back to Grep across the candidate import / call-site patterns and record the method as `manual`.

3. **Compare** the returned impact set to what the Blueprint's Change Impact Map / Interface Change Matrix already covers.

4. **For each blast-radius item not covered in the Blueprint:**
   - If clearly affected (the impact analysis says "this caller will see a different return type") → `critical` issue, category `completeness`
   - If maybe affected (impact analysis returns "this caller transitively reaches the change target") → `important` issue, category `completeness`

### What "covered" means

A blast-radius item is "covered" when:

- it appears in the Change Impact Map (direct or indirect), OR
- it appears in the Interface Change Matrix with a compatibility method, OR
- it appears in the Field Propagation Map, OR
- the Blueprint explicitly states it's unaffected (e.g. in `No Ripple Effect:` of Change Impact Map)

Items the Blueprint doesn't mention at all → uncovered.

### serena degradation

If serena is unavailable (Preflight should have caught this, but defense-in-depth), the auditor:

1. Records `metadata.blast_radius_method: "manual"` in output
2. Performs a best-effort manual blast-radius using Grep/Glob on the change targets' symbols
3. Surfaces an `important` issue noting the manual method, with severity downgrade-or-upgrade rationale

## Lens 3 — Brief-Honor Verification (per ADR-0009)

**Goal:** confirm every Blueprint decision honors what the rationale brief committed to. Detects three failure modes:

1. **Decision contradiction:** Blueprint makes a decision that contradicts a commitment in the brief
2. **Open-item handling:** brief lists an open item; Blueprint must either resolve it or explicitly defer (with rationale). Silently dropping the open item is a violation.
3. **Re-surfaced verified issue:** a prior issue marked `resolved` in the ledger appears again in the Blueprint as if unresolved

### Procedure

1. **Load the rationale brief.** Either embedded in the orchestrator's invocation prompt or referenced as a file path.
2. **Enumerate the brief's commitments.** Three categories:
   - Decisions confirmed by user (e.g. "User approved the per-layer fan-out at the Design phase")
   - Open items (e.g. "Layer Scope checkboxes pending user confirmation")
   - Resolved issues from prior iterations (e.g. "I-AA-002 resolved by adding Field Propagation Map")
3. **For each commitment, locate the Blueprint's treatment.**

4. **Classify the treatment:**

| Treatment | Verdict |
|---|---|
| Decision honored | Pass |
| Decision contradicted | `critical` issue, category `consistency` |
| Open item resolved with rationale | Pass; record resolution |
| Open item silently dropped | `critical` issue, category `completeness` |
| Open item explicitly deferred with rationale | Pass; note for downstream |
| Open item re-opened by Blueprint with new question | `important` issue, category `consistency` (may be legitimate but needs explicit user re-approval) |
| Resolved issue re-surfaced as if unresolved | `important` issue, category `consistency`; auditor surfaces with reference to prior ledger entry |

### What the rationale brief looks like

Per ADR-0009, every sub-agent invocation carries a rationale brief in the prompt. The brief during Design Composition's composer invocation contains:

- All user-approved decisions through per-layer Design
- The current open items from Intent Clarification through per-layer Design
- Prior iterations' resolved issues (referenced by ID)
- KB and ADR paths in scope for this feature

The auditor receives a snapshot of the brief during Design Composition (the composer's input), enriched with any decisions that arose during composition.

## Output JSON

Per the standard reviewer output protocol. Issue IDs use prefix `AA` (architecture audit):

```json
{
  "metadata": {
    "stage": 6,
    "auditor": "review-architecture-auditor",
    "blueprint_version": "vN",
    "blast_radius_method": "serena" | "manual",
    "cove_sample_rate": 0.7
  },
  "verdict": {"decision": "approved_with_conditions"},
  "issues": [
    {"id": "I-AA-NNN", "severity": "important", "category": "consistency", "lens": "cove", "location": "Blueprint § Frontend Design para 3", ...}
  ],
  "scores": {"consistency": ..., "completeness": ..., "rule_compliance": ..., "clarity": N/A},
  "prior_context_check": {...}
}
```

The `lens` field is auditor-specific (`cove` | `blast_radius` | `brief_honor`) so downstream consumers can see which lens surfaced an issue.

## Iteration with finalize-reconciler

Issues with severity `critical` or `important` trigger `finalize-reconciler` (Reconciliation), which works with the relevant per-layer designer or `design-composer` to revise the Blueprint. The revised Blueprint v(N+1) goes back to `shared-document-reviewer` (Gate 0/1) and then back to this auditor.

Four-cycle hard cap. If issues persist at iteration 4, halt and surface to user.

## When NOT to apply this discipline

- The Design Composition document-reviewer pass — that's Gate 0/1, not substantive architecture
- the Cross-Artifact Audit pass — different discipline (CMC + diff-mode + convergence), different reviewer
- ADR reviews mid-pipeline — `shared-document-reviewer` handles each ADR's Gate 0/1 per ADR-0017
- **Annotation-level numeric consistency checks** (e.g., "(4) listed items but list contains 5", `total_tasks: N` vs. actual `#### T` count). These belong to `shared-document-reviewer`'s Gate 1 "Numeric internal consistency check" — not to the architecture auditor. The auditor's three lenses (CoVe / blast-radius / brief-honor) are substantive, not annotation-level. If an annotation-vs-enumeration mismatch surfaces during this audit, downgrade to `MINOR` and reference the Gate 1 check that should have caught it; do not spend the auditor's xhigh reasoning budget on counts.

## Lens 4 — Design Realization (per ADR-0059)

**Goal:** verify that when an ADR's companion `.prescriptions.yaml` declares a prescription, the eventual implementation artifact matches it. Catches the defect class where an ADR prescribes a concrete implementation detail and the codebase quietly diverges.

### Purpose

Each ADR with machine-checkable prescriptions ships a sibling companion file at `adrs/ADR-NNNN-<slug>.prescriptions.yaml` (per ADR-0059). Lens 4 closes the loop: for every prescription declared in a companion file, the auditor verifies the codebase state satisfies the declared assertion. Prescriptions that fail realization become audit findings; ADRs without a companion file are a no-op (AC-FR-1-b).

### Inputs

1. **Companion files** — `adrs/ADR-NNNN-<slug>.prescriptions.yaml`, one per ADR that contains machine-checkable prescriptions (cardinality 0..N across the run's ADR set). The companion is the canonical prescription source; ADR prose is the canonical decision narrative. Neither derives from the other.
2. **Codebase state** — the repository files the prescriptions point to, accessed via `auditing-shared/scripts/validate_adr_prescriptions.py` (T4.1 deliverable). The validator handles schema validation, ADR-to-companion slug matching, and target-path existence checks before assertion evaluation.

### Process

1. **Enumerate companion files** in the run's ADR scope. If none are present, emit a no-op diagnostic and exit Lens 4 (AC-FR-1-b).
2. **Schema-validate each companion** by invoking `validate_adr_prescriptions.py`. A schema-invalid companion produces a `MAJOR` finding before prescription evaluation begins; evaluation for that companion stops.
3. **For each prescription entry** in a valid companion:
   a. Identify the `assertion.kind` (one of the 8 enumerated kinds: `file_exists`, `file_not_exists`, `regex_present`, `regex_not_present`, `substring_present`, `substring_absent`, `jsonpath_equals`, `jsonpath_count` — per ADR-0059 §Neutral Consequences).
   b. Evaluate the assertion against the codebase at the declared `target_path`.
   c. If the assertion passes: record as verified (for traceability); no finding emitted.
   d. If the assertion fails: emit a finding per the severity calibration below.
4. **Aggregate findings** into the shared issues array with `"lens": "design_realization"` (parallel to `"cove"` / `"blast_radius"` / `"brief_honor"` in the output JSON).

### Severity calibration (per severity-taxonomy.md §Cross-Surface Severity Bridge Table)

| Failure mode | Severity | Notes |
|---|---|---|
| Missing prescribed file (`file_exists` assertion fails) | `BLOCKER` | The prescription names a `target_path` that must exist but does not. |
| Schema mismatch on companion file | `MAJOR` | Companion YAML fails `validate_adr_prescriptions.py` schema check; prescriptions in that companion are unevaluated until the companion is corrected. |
| Prescription drift — content/output mismatch (`regex_present`, `regex_not_present`, `substring_present`, `substring_absent`, `jsonpath_equals`, `jsonpath_count` assertion fails) | `MAJOR` | File exists but its content diverges from the declared assertion. Override: `BLOCKER` if the companion entry declares `severity_floor: BLOCKER`. |
| `file_not_exists` assertion fails (prescribed removal not honored) | `MAJOR` | A file that was prescribed for removal still exists. |
| Other deviations | `MINOR` or `INFO` | Per the companion entry's `enforcement` field; default `MINOR` when `enforcement` is unset. |

### Output finding shape (per severity-taxonomy.md §NFR-8 Four-Field Finding Shape)

Each Lens 4 finding carries exactly the four NFR-8 fields:

| Field | Content |
|---|---|
| `rule` | `FR-1.design_realization.<kind>` — e.g., `FR-1.design_realization.file_missing`, `FR-1.design_realization.regex_mismatch`, `FR-1.design_realization.stale_reference`. The `<kind>` segment names the assertion kind that failed. |
| `target` | The prescribed file path, symbol, or command named in the companion entry's `target_path`. |
| `divergence` | Observed-vs-expected one-liner: what the codebase currently contains vs. what the prescription asserts. |
| `next_action` | Imperative remediation step: e.g., "Create `<path>` per ADR-NNNN §Implementation Guidance" or "Remove stale reference to `<symbol>` in `<file>` — prescribed by ADR-NNNN." |

The `lens` field in the output JSON is set to `"design_realization"` for all Lens 4 findings.

### Canonical example

ADR-0041 (install-mechanism-hybrid) prescribed the removal of the `mcp-openapi-schema` server; a six-server `.mcp.json` was the prescribed state as of 2026-05-24. After the removal, `.claude/skills/auditing-mcp/scripts/audit_op2_consumer_mapping.py` still referenced `mcp-openapi-schema` as a consumer of the `design-api` agent — a stale reference that no per-artifact gate caught.

A Lens 4 audit with the companion `ADR-0041-install-mechanism-hybrid.prescriptions.yaml` catches this as:

```json
{
  "id": "I-AA-NNN",
  "severity": "important",
  "lens": "design_realization",
  "rule": "FR-1.design_realization.stale_reference",
  "target": ".claude/skills/auditing-mcp/scripts/audit_op2_consumer_mapping.py",
  "divergence": "File references mcp-openapi-schema as a live server consumer; ADR-0041 prescribed removal on 2026-05-24 — server is absent from .mcp.json.",
  "next_action": "Remove mcp-openapi-schema from audit_op2_consumer_mapping.py consumer list; update any dependent mappings to reflect the six-server canonical set."
}
```

This is the structural defect class Lens 4 exists to surface: ADR prescription diverges from implementation; the gap was silent until this lens ran.

### No-op condition

When no companion files exist in the run's ADR set, Lens 4 emits a single `INFO`-level diagnostic (`"rule": "FR-1.design_realization.no_companions"`) and exits. This is not a finding; it does not affect the verdict score.

### Cross-references

- **ADR-0059** — Companion-file schema; `assertion.kind` vocabulary; canonical placement rule; schema evolution policy.
- **severity-taxonomy.md §Cross-Surface Severity Bridge Table** — severity vocabulary used above (`BLOCKER` / `MAJOR` / `MINOR` / `INFO`).
- **severity-taxonomy.md §NFR-8 Four-Field Finding Shape** — the `rule` / `target` / `divergence` / `next_action` shape all Lens 4 findings conform to.
- **`auditing-shared/scripts/validate_adr_prescriptions.py`** (T4.1) — schema validator invoked in step 2 of the process above.
- **Companion-file schema in ADR-0059** — `assertion.kind` enumeration (8 kinds), `severity_floor` override field, `enforcement` field semantics.

## Update History

| Change | Date | Notes | Sources |
|---|---|---|---|
| Added §Lens 4 — Design Realization | 2026-05-27 | Additive: new audit lens for ADR prescription vs. implementation verification. Authored per ADR-0059 + pipeline-design-time-discipline-r1 (R2a) Plan §Phase 4 / T4.2 / AC-FR-1-c (gate PV-4.C3). | ADR-0059; cc-design.md §FR-1; severity-taxonomy.md §Bridge Table + §NFR-8 |
