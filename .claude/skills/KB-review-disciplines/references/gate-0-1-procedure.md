# Gate 0 / Gate 1 Procedure

## Contents

- Why two gates
- Gate 0 — Structural Existence
- Gate 1 — Quality Assessment
- Iteration with prior context
- Output JSON
- Failure modes to avoid

The structural-then-quality two-gate procedure used by `shared-document-reviewer` on every pipeline document.

## Why two gates

Quality review is expensive: it reads adjacent documents, runs Grep/Glob against the codebase, and may invoke WebSearch. Running it against a document missing required sections is wasted budget. Gate 0 is a cheap structural pass that filters out documents that cannot pass quality review regardless of their content.

```
target document
      │
      ▼
   Gate 0  ──fail──►  needs_revision  (return immediately; do not run Gate 1)
      │
     pass
      ▼
   Gate 1  ──score──►  verdict per severity-taxonomy.md
```

## Gate 0 — Structural Existence

**Goal:** confirm the document's required structural elements are present. Not their quality — just their presence.

### Step 1: Identify the document type

`doc_type` is provided as input. One of: `IntentClarification`, `PRD`, `ADR`, `DesignDoc`, `Plan`, `UISpec`.

### Step 2: Load the canonical template

From `KB-documentation-criteria/references/templates/<doc_type>-template.md`. The template defines the required structural elements.

### Step 3: Check each required element

Required elements are the sections that the template marks REQUIRED (vs. OPTIONAL). For each:

- [ ] Section heading present at the expected level
- [ ] Section body non-empty (more than just the heading)
- [ ] Required sub-elements present (e.g. table rows, frontmatter fields, EARS keywords)

### Step 3b: Use the `## Contents` checklist as the structural-presence anchor (when present)

Pipeline documents authored from `KB-documentation-criteria` templates include a `## Contents` section with a checklist of the document's top-level (H2) sections. When present, the reviewer uses it as an additional structural anchor:

- Every checklist box should be marked `[x]` (or explicitly `N/A — out of scope` for layers the Layer Scope excluded). Unchecked boxes → Gate 0 fail.
- Every checked item should correspond to a non-empty section in the document body. Checked-but-missing → Gate 0 fail with category `consistency`.
- Every H2 section in the body should appear in the checklist. Body-section-not-in-checklist → MINOR `recommended` issue ("update checklist to reflect added section").

Documents missing the `## Contents` section entirely → Gate 0 fail (the template requires it).

### Step 4: Document-type-specific additional checks

| `doc_type` | Additional Gate 0 checks |
|---|---|
| `IntentClarification` | All clarifying questions answered (no `[ ]` checkbox items left unfilled); user confirmation token present |
| `PRD` | Layer Scope checked (≥1 layer); at least one stakeholder in Stakeholder Inventory; at least one Functional Requirement; no `[ ]` items in Undetermined Items (or section deleted) |
| `ADR` | Frontmatter complete (id, version, status, supersedes if applicable); Decision Details table has all 4 rows (Why now / Why this / Known unknowns / Kill criteria); Options Considered has ≥2 options |
| `DesignDoc` | Frontmatter complete; Layer Scope ≥1 layer; Design Summary YAML present; all 9 per-layer Design subsections present (each either substantive or marked `N/A — out of scope`); Fact Disposition Table covers every `codebase_analysis.focusAreas` entry (if codebase_analysis input provided); Verification Strategy section has all four subsections (Correctness Proof Method, Early Verification Point, Output Comparison or N/A, Operational Verification or N/A); EARS keywords (When/While/If-then or ubiquitous) intact in ACs |
| `Plan` | Phase 0 through last-phase explicit; each task has L1/L2/L3 verification criteria; dependencies declared; no orphan tasks |
| `UISpec` | Component inventory complete; state matrix (loading/empty/error/partial) for each component; routing if SPA |

### Step 5: Verdict

Any required element missing → Gate 0 fails. Emit `verdict.decision: needs_revision`, populate `gate0.status: fail` and `gate0.missing_elements: [...]`. **Do not run Gate 1.**

All required elements present → Gate 0 passes. Proceed to Gate 1.

## Gate 1 — Quality Assessment

**Goal:** evaluate the document's quality across four scoring dimensions plus document-type-specific checks.

### The four scoring dimensions

Each dimension scores 0–100. Total of all four is the document's quality score.

| Dimension | What it measures |
|---|---|
| **Consistency** | Does the document agree with itself? Does it agree with adjacent documents (PRD ↔ Blueprint ↔ Plan)? Are terminology, numbers, and stakeholder references aligned? |
| **Completeness** | Are required-element bodies thorough enough to act on? Are dependencies declared, edge cases addressed, success criteria measurable? |
| **Rule compliance** | Does the document follow project rules (frontmatter format, EARS syntax, supersession discipline) and KB-documentation-criteria conventions? Does it pass `KB-general-coding-principles` on any code samples? |
| **Clarity** | Is the document readable? Does prose match the precision of the spec? Are key terms used consistently? Can a new contributor act on this document without asking? |

### Scoring → verdict (per severity-taxonomy.md)

| Score range | Verdict |
|---|---|
| Consistency > 90 AND Completeness > 85 AND no rule violations AND no `critical` issues | `approved` |
| Consistency > 80 AND Completeness > 75 AND only `important` rule violations AND only easily-fixable issues | `approved_with_conditions` |
| Consistency < 80 OR Completeness < 75 OR `critical` rule violations OR blocking issues | `needs_revision` |
| Fundamental problems; requirements not met | `rejected` |

Score thresholds are the canonical mapping. Reviewers may surface additional severity considerations but cannot bypass the threshold mapping.

### Substantive checks (always run in Gate 1)

These run regardless of doc_type:

- **Consistency check:** detect contradictions between this document and adjacent ones
- **Completeness check:** confirm depth and coverage of required elements
- **Rule compliance check:** apply project rules, KB-documentation-criteria conventions, EARS syntax
- **Feasibility check:** technical and resource feasibility of stated requirements
- **Rationale verification:** decisions must reference identified standards or existing patterns
- **Technical information verification:** when sources cited, verify via WebSearch
- **Failure scenario review:** enumerate failure scenarios across normal usage, high load, external failures; identify the bottleneck design element for each
- **Numeric internal consistency check:** when the document contains both an annotated count (e.g., "5 new files", "(4) modified", "total_tasks: 14") and an enumerated list of the items being counted, the reviewer enumerates the list and compares to the annotation. Mismatches are `important`/`consistency` issues. Examples this catches: parenthetical counts inconsistent with bulleted lists; frontmatter `total_tasks` differing from `#### T*` count; "N tests" claim differing from actual test-spec count. *Belongs here, not in architecture audit* — annotation-vs-enumeration mismatches are structural-numeric, not architectural.
- **Per-FR AC enumeration check (when the document references PRD acceptance criteria):** for any document that maps PRD ACs to downstream artifacts (Plan task lists, test specifications, audit checklists), the reviewer enumerates ACs **per FR** from the source PRD, then verifies each FR's full AC set is covered. A naive total-count check is not sufficient — fabricated ACs in one FR can offset missing ACs in another and produce the same total. Procedure: (a) extract `FR-<N>.AC-<M>` pattern from source PRD via grep; (b) extract same pattern from target document; (c) for each FR present in PRD, compare per-FR coverage. Surface fabricated AC references (target lists `FR-X.AC-Y` that PRD does not define) as `critical`/`consistency`; surface omitted AC references as `important`/`completeness`. This check also walks individual task bodies (e.g., per-task `Satisfies AC:` fields), not just top-level cross-reference tables — a fix to a table can leave the same fabrications inside task bodies.
- **Canonical-source-reference check (per KB-cc-design Principle 11):** the project keeps shared vocabularies in `.claude/canonical/*.yaml` (tool names, hook events, severity levels, naming patterns, frontmatter fields, doc-type / state enums, skill thresholds, the audit-rule registry, and the engineering domain layers). When a document under review **enumerates a member set of one of these vocabularies inline** (e.g., lists the engineering layers, the severity levels, the doc-type enum), the reviewer checks whether the document also **references the canonical source** (the `.claude/canonical/<name>.yaml` path or its declared prose companion). If it references the source, the inline list is an acceptable derived view — note it as `recommended` only if it risks drifting. If it does NOT reference the source, flag as `important`/`consistency`: the inline enumeration is a drift surface that should be replaced with a reference (or have a canonical pointer added if a functional inline view is genuinely needed). This is the human-review mirror of the automated CANON-2 audit (`audit_canonical_doc_drift.py`); the reviewer catches new hard-codings in documents the audit does not yet watch. The triggering principle: shared vocabulary has one home; everything else points at it.

### Substantive checks (DesignDoc-only)

Per the shared-document-reviewer template's Gate 1 section, these additional checks run when `doc_type: DesignDoc`:

- **Code inspection evidence review:** files referenced in the Existing Codebase Analysis section are actually relevant; key files aren't missing
- **Dependency realizability check:** for each "existing" dependency in the codebase analysis, verify via Grep/Glob that the symbol exists at the claimed signature. Missing → `critical`/`feasibility`. Signature mismatch → `important`/`consistency`.
- **As-is implementation review:** when `code_verification` input provided, document must state code-observable behaviors as facts (not speculation)
- **Data design completeness:** if document mentions data-storage / data-access / data-schema keywords but lacks schema references, Test Boundaries with data strategy, or data model documentation → `important`/`completeness`
- **Code verification integration:** when `code_verification.undocumentedDataOperations` present, each absent item → `important`/`completeness`
- **Verification Strategy quality:** Correctness definition specific and measurable; Verification method sufficient for primary risk category; Early Verification Point identifies a concrete first target (not "TBD" or "final phase")
- **Output comparison:** when design replaces/modifies existing behavior, concrete output comparison method must be defined
- **Fact Disposition completeness:** every `codebase_analysis.focusAreas` entry → row in Fact Disposition Table with carried-through `fact_id` and `evidence`

Full detail of each check in the `shared-document-reviewer-template.md` Step 3 / Gate 1 section.

## Iteration with prior context

When invoked on iteration N ≥ 2, the reviewer receives prior-context issues from iteration N-1. Per `prior-context-check.md`:

1. Run Step 0 of the reviewer template (input context analysis)
2. Extract actionable items and record `prior_context_count`
3. After Gate 1, locate each prior item in the current document
4. Classify resolution status; populate `prior_context_check` block in output

A reviewer that fails to do prior-context check risks re-surfacing resolved issues. This is the most common cause of iteration loops.

## Output JSON

The output is a single JSON object per `shared-document-reviewer-template.md` Output Protocol section. Key fields:

```json
{
  "metadata": {"review_mode": "comprehensive", "doc_type": "DesignDoc", "target_path": "..."},
  "scores": {"consistency": 85, "completeness": 80, "rule_compliance": 90, "clarity": 75},
  "gate0": {"status": "pass", "missing_elements": []},
  "verdict": {"decision": "approved_with_conditions", "conditions": ["...", "..."]},
  "issues": [{"id": "I-DR-NNN", "severity": "important", "category": "consistency", ...}],
  "recommendations": ["..."],
  "prior_context_check": {"items_received": N, "resolved": X, "partially_resolved": Y, "unresolved": Z, "items": [...]}
}
```

Last message returned to orchestrator MUST start with `{` and end with `}` — JSON only, no prose wrapper.

## Failure modes to avoid

- **Skipping Gate 0** to "save time" — Gate 1 runs against a missing-section document produce spurious issues
- **Treating Gate 0 failures as low-severity** — Gate 0 is hard fail; severity does not apply
- **Re-surfacing prior issues without checking resolution** — creates iteration loops (see `prior-context-check.md`)
- **Inventing checks not in this procedure** — surface as `recommended` issue, but don't fail verdict on a check this procedure doesn't define
