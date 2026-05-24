---
id: SPEC-issue-doctypes
version: 1.0.0
status: Proposed
doc_type: reference-spec
feature_slug: issue-capture-mechanism-r1
generated: 2026-05-24
generated_by: execute-task-code-producer
---

# Issue Doctypes Structural Spec

Canonical structural spec for outside-pipeline `Issues/<topic-slug>/<doctype>.md` files.
This is the single source-of-truth consumed by:

- The validator extension (`validate_pipeline_frontmatter.py`) — Phase 2 T2.1 populates
  `ISSUE_PER_STATE_REQUIRED_FIELDS` and related constants from this file.
- The issue-capture-author agent body — reads this spec at runtime (Phase 4 T4.4b).
- The three sibling templates (issue-register, issue-analysis, issue-proposal) — reference
  this spec for all structural assertions.

## Contents

- [x] §1 Purpose
- [x] §2 Three Doctypes (per ADR-0045)
- [x] §3 5-State Lifecycle Vocabulary (per ADR-0050)
- [x] §4 Per-State Required Companion Fields (D-05 Authoritative Table)
- [x] §5 Optional Cross-Link Fields (per ADR-0046 + ADR-0050)
- [x] §6 `proposes_future_feature` Advisory Posture (per ADR-0050)
- [x] §7 ID Derivation Rule (per ADR-0050)
- [x] §8 Distinct From
- [x] §9 Cross-References

## §1 Purpose

This spec is the single source-of-truth for the structural shape of outside-pipeline
`Issues/<topic-slug>/<doctype>.md` files. It codifies the three recognized doctypes, the
5-state lifecycle vocabulary, the per-state required companion fields (the load-bearing
D-05 table), the optional cross-link fields, the ID derivation rule, and the advisory
posture for `proposes_future_feature`. Both the validator extension (which enforces these
rules programmatically) and the issue-capture-author agent body (which produces conforming
files at runtime) consume this spec as their structural authority. The three sibling
templates under `KB-documentation-criteria/references/templates/` encode the body skeleton
for each doctype and reference this spec for all frontmatter assertions.

## §2 Three Doctypes (per ADR-0045)

### 2.1 First-Class Doctypes

Three doctypes are defined and preserved as structurally distinct (ADR-0045 Decision §1).
Each has its own canonical template and its own validator branch. No unified `issue`
doctype exists; captured issues MUST be classified into one of the three.

| `doc_type` value | Cognitive job | Canonical template |
| --- | --- | --- |
| `issue-register` | Tabular scan of many deferred items | `issue-register-template.md` |
| `issue-analysis` | Deep-dive into one phenomenon | `issue-analysis-template.md` |
| `issue-proposal` | Seed a future feature run | `issue-proposal-template.md` |

### 2.2 Canonical Filename Pattern

Files live at: `Issues/<topic-slug>/<doctype>.md`

Where `<doctype>` is the base name without the `issue-` prefix:

- `Issues/<topic-slug>/register.md`
- `Issues/<topic-slug>/analysis.md`
- `Issues/<topic-slug>/proposal.md`

Example: `Issues/adr-placement-rootcause/analysis.md`

### 2.3 Non-Validated Subdirectories

`evidence/` and `updates/` subdirectories within a topic folder carry no doctype
constraint and are excluded from validation. The validator's outer-dispatch path-prefix
skip handles this (v3 pattern per I-AA-002):

```python
ISSUE_NON_VALIDATED_PATH_PREFIXES = (
    "Issues/*/evidence/",
    "Issues/*/updates/",
)
```

Files under `Issues/<topic-slug>/evidence/` or `Issues/<topic-slug>/updates/` are
returned as an empty findings list without doctype validation.

## §3 5-State Lifecycle Vocabulary (per ADR-0050)

### 3.1 State Diagram

```text
draft → open → adopted
              → complete
              → superseded
              → wontfix-with-rationale
```

Six valid states:

- `draft` — newly captured; the agent has written the file but the user may still revise.
- `open` — actively tracked; the issue is real and warrants future attention.
- `adopted` — a feature run is in flight or has shipped that addresses this issue.
- `complete` — the underlying concern is resolved without an adoption pathway.
- `superseded` — a different file replaces this one as the canonical record.
- `wontfix-with-rationale` — deliberate decision not to address.

### 3.2 Parallel-But-Distinct From ADR-0008

This vocabulary is parallel-but-distinct from ADR-0008's intra-pipeline 4-state ledger
(`open → resolved | wontfix-with-rationale | superseded`). The two vocabularies share
three literal state-name strings (`open`, `superseded`, `wontfix-with-rationale`) as a
learnability feature — readers who know one vocabulary recognize the shared semantics in
the other. The overlap is intentional and not a coupling defect.

The two vocabularies operate on disjoint entities with disjoint ID prefixes and MUST
NEVER share IDs:

- Intra-pipeline: `I-<DR|AA|CA>-NNN` (issues-ledger.json records; feature-scoped).
- Outside-pipeline: `<UPPERCASE-DOCTYPE>-<kebab-topic-slug>` (Issues/ files; project-scoped).

No automated cross-reference is introduced between the two vocabularies.

### 3.3 Validator Dispatch as a Fourth Category

The validator enforces this vocabulary as a fourth category alongside the existing three
(GATED / ANALYSIS / ADR) per ADR-0032. When `doc_type ∈ ISSUE_DOC_TYPES`, the
`validate_issue_artifact(fm, path)` branch is invoked; the existing three branches are
unaffected (NFR-8 backward compatibility).

```python
ISSUE_DOC_TYPES = {"issue-register", "issue-analysis", "issue-proposal"}
ISSUE_STATES = {
    "draft", "open", "adopted", "complete",
    "superseded", "wontfix-with-rationale",
}
```

## §4 Per-State Required Companion Fields (D-05 Authoritative Table)

### 4.1 Universal-Required Frontmatter Fields

The following fields are required on every outside-pipeline issue file regardless of state:

`id`, `version`, `doc_type`, `status`, `feature_slug`, `generated`, `generated_by`

### 4.2 Per-State Companion Fields

This table is the load-bearing assertion of PV-1.C3. The validator's
`ISSUE_PER_STATE_REQUIRED_FIELDS` constant (Phase 2 T2.1) is populated from this table.
Any divergence between this table and the validator constants is a defect.

| State | Required companion fields (in addition to universal) | Severity if missing |
| --- | --- | --- |
| `draft` | None | n/a |
| `open` | `since` | blocker |
| `adopted` | `since`, `adopted_by_feature_slug`, `adopted_at` | blocker |
| `complete` | `since`, `resolved_by`, `resolved_at`, `resolution_summary` | blocker |
| `superseded` | `since`, `superseded_by_issue_id`, `superseded_at` | blocker |
| `wontfix-with-rationale` | `since`, `wontfix_rationale`, `decided_at` | blocker |

Field name lock (per Q-BE-1/Q-BE-2/Q-BE-3 resolution; locked by ADR-0050): the strings
`since`, `adopted_by_feature_slug`, `adopted_at`, `resolved_by`, `resolved_at`,
`resolution_summary`, `superseded_by_issue_id`, `superseded_at`, `wontfix_rationale`,
`decided_at` are canonical. Note: `superseded_by_issue_id` is a DISTINCT field name from
ADR-0005's `superseded_by` — this preserves category separation between outside-pipeline
issue supersession and ADR supersession.

## §5 Optional Cross-Link Fields (per ADR-0046 + ADR-0050)

The following fields are optional. When present they are validated syntactically (regex
match against `<UPPERCASE-DOCTYPE>-<kebab-topic-slug>`); they are NEVER required.

| Field | Direction | Source ADR | Notes |
| --- | --- | --- | --- |
| `escalates_from: <id>` | Forward link on the newer file | ADR-0046 | Bidirectional sibling-evolution pattern |
| `escalated_to: <id>` | Back-link on the older file | ADR-0046 | Added by evolution transaction |
| `rolled_into_register: <id>` | Advisory cross-topic relationship | ADR-0050 | Syntactic check only |

Both `escalates_from` and `escalated_to` are written in a single approved transaction
(ADR-0046 Decision §3). The older file's `status:` field is never mutated by evolution —
only the `escalated_to` back-link is added. Optional fields support list values where
multiple evolution events touch the same file.

## §6 `proposes_future_feature` Advisory Posture (per ADR-0050)

When `doc_type == issue-proposal`:

- **When absent**: the validator emits an `info`-severity finding (not `blocker`). The
  field is advisory; its absence does not invalidate the document.
- **When present**: any string value is accepted. No format enforcement is applied. Both
  precedent shapes from F-006 are valid:
  - Suggested-slug form: `auditing-family-structure-review-r1 (suggested slug)`
  - Fixed-slug form: `issue-capture-mechanism-r1`

The advisory posture is upgradable to `blocker` in a later ADR if real-world use shows
the field becomes load-bearing (ADR-0050 Decision §6). The independent `adopted_by_feature_slug`
requirement on `status: adopted` provides the load-bearing back-link; `proposes_future_feature`
is a forward-pointer signal only.

## §7 ID Derivation Rule (per ADR-0050)

Frontmatter `id` is derived from the file's path per ADR-0044:

```text
id: <UPPERCASE-DOCTYPE>-<kebab-topic-slug>
```

Where `<UPPERCASE-DOCTYPE>` is the `doc_type` value with `issue-` prefix uppercased and
hyphen-separated:

| `doc_type` | Uppercase prefix |
| --- | --- |
| `issue-register` | `ISSUE-REGISTER` |
| `issue-analysis` | `ISSUE-ANALYSIS` |
| `issue-proposal` | `ISSUE-PROPOSAL` |

Examples:

- `Issues/adr-placement-rootcause/analysis.md` with `doc_type: issue-analysis`
  → `id: ISSUE-ANALYSIS-adr-placement-rootcause`
- `Issues/devcontainer-mcp-provisioning-deferrals/register.md` with `doc_type: issue-register`
  → `id: ISSUE-REGISTER-devcontainer-mcp-provisioning-deferrals`
- `Issues/auditing-family-graduation/proposal.md` with `doc_type: issue-proposal`
  → `id: ISSUE-PROPOSAL-auditing-family-graduation`

The validator verifies this match at validation time; a mismatch emits a `blocker`
finding.

## §8 Distinct From

### 8.1 Distinct From ADR-0008's Intra-Pipeline `issues-ledger.json`

`Issues/<topic>/<doctype>.md` files are outside-pipeline, project-scoped, and persist
across feature runs. ADR-0008's `working/feature/<slug>/issues-ledger.json` records are
inside-pipeline, feature-scoped, and are created by pipeline reviewers (DR / AA / CA
prefixes). The two systems have disjoint entities, disjoint ID prefixes, and disjoint
lifecycles. No automated cross-reference is introduced between them (ADR-0050 Decision §2).

### 8.2 Distinct From `KB-issue-capture` Triggering Discipline

This spec is STRUCTURAL ONLY (per ADR-0049). It codifies the shape of issue files —
the doctypes, the lifecycle states, the required fields, the ID rule. It does NOT codify:

- Triage criteria for capturing an issue.
- Doctype-classification rubric.
- Approval-prompt wording.
- Worked examples.

That discipline lives exclusively in `KB-issue-capture/references/` (ADR-0049 Decision §2).
The structural-vs-discipline split prevents duplication and drift.

## §9 Cross-References

### Related ADRs

| ADR | Subject |
| --- | --- |
| ADR-0045 | Three doctypes preserved as distinct (register / analysis / proposal) |
| ADR-0046 | Add-new-sibling-file evolution pattern; `escalates_from` / `escalated_to` fields |
| ADR-0049 | Structural-vs-discipline KB split; templates are structural-only |
| ADR-0050 | 5-state lifecycle vocabulary; per-state companion fields; `proposes_future_feature` advisory |

### Sibling Templates

| Template file | Doctype |
| --- | --- |
| `KB-documentation-criteria/references/templates/issue-register-template.md` | `issue-register` |
| `KB-documentation-criteria/references/templates/issue-analysis-template.md` | `issue-analysis` |
| `KB-documentation-criteria/references/templates/issue-proposal-template.md` | `issue-proposal` |

### Validator Extension Target

`.claude/skills/auditing-shared/scripts/validate_pipeline_frontmatter.py`

Phase 2 T2.1 populates these constants from this spec:
`ISSUE_DOC_TYPES`, `ISSUE_STATES`, `ISSUE_PER_STATE_REQUIRED_FIELDS`
