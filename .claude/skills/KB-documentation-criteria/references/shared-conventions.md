# Shared Conventions

The rules that apply to every pipeline document (Intent Clarification, PRD, Blueprint, ADR, Plan) regardless of its type. Loaded by every authoring sub-agent and by `shared-document-reviewer`.

## Contents

- Frontmatter format
- Per-document-type frontmatter fields
- Supersession discipline (per ADR-0005)
- Versioning rules
- Traceability rules (PRD → Blueprint → Plan → Tests)
- File-naming convention
- Path discipline
- YAML pitfalls

## Frontmatter format

Every document begins with YAML frontmatter between `---` delimiters on lines of their own. The opening `---` must be the very first line of the file — no leading whitespace, no BOM.

```yaml
---
id: <doc-type-id>
version: <semver>
status: draft | proposed | accepted | superseded | rejected
generated: <ISO-8601-UTC-timestamp>
generated_by: <sub-agent-name>
---
```

Required for every document type: `id`, `version`, `status`, `generated`, `generated_by`. Status values:

| Status | Meaning |
|---|---|
| `draft` | Authored but not yet reviewed |
| `proposed` | Reviewed by `shared-document-reviewer`; awaiting user gate (or, for ADRs, awaiting Architecture Audit) |
| `accepted` | Approved through the relevant gate; canonical until superseded |
| `superseded` | Replaced by a newer document of the same type; preserved per ADR-0005 |
| `rejected` | Reviewed and rejected; not promoted |

## Per-document-type frontmatter fields

In addition to the universal fields, each doc type adds its own required fields:

### Intent Clarification

```yaml
feature_slug: <slug>
user_token: <token-from-user-confirmation>
```

### PRD

```yaml
feature_slug: <slug>
derived_from: <intent-clarification-doc-path>
```

### Blueprint

```yaml
feature_slug: <slug>
derived_from: <prd-path>
predecessor: <previous-blueprint-version-path>   # only when version > 1.0.0
codebase_analysis: <codebase-analysis.json-path>
adrs_referenced: [ADR-NNNN, ADR-NNNN, ...]       # ADRs this Blueprint depends on
adrs_authored: [ADR-NNNN, ADR-NNNN, ...]         # ADRs authored alongside this Blueprint
```

### ADR

```yaml
id: ADR-NNNN
supersedes: ADR-NNNN | null
change_summary: <one-line>
```

Per ADR-0019 naming convention, ADR IDs are zero-padded four-digit and assigned monotonically across the project (not per-feature).

### Plan

```yaml
feature_slug: <slug>
derived_from: <blueprint-path>
phases: <integer-count>
total_tasks: <integer-count>
```

## Supersession discipline (per ADR-0005)

When a document is replaced by a new version, the prior version is NOT deleted. It is marked `status: superseded` and preserved at its original filename. The new version's frontmatter declares `predecessor: <prior-version-path>` and bumps `version`. The old version's frontmatter is updated to declare `superseded_by: <new-version-path>`.

This applies to:

- Blueprints: each iteration creates a new file (`blueprint-v1.md`, `blueprint-v2.md`); prior versions kept
- PRDs: similarly versioned (`prd-v1.md`, `prd-v2.md`)
- ADRs: when an ADR is superseded, the new ADR's `supersedes` field references the old ADR's `id`; the old ADR's status changes to `superseded` but its file is preserved

Plans and Intent Clarification docs are typically not versioned mid-pipeline — they have one canonical version per feature run. Mid-pipeline edits update version in-place.

### Why preserve superseded versions

- Decisions made in superseded versions may still be referenced by other documents.
- The supersession chain is the audit trail.
- Re-reading a superseded version is sometimes necessary to understand what was rejected and why.

### Anti-pattern: silent overwrite

Overwriting a document's content without bumping version and marking the prior version superseded breaks the audit trail. `shared-document-reviewer` flags this as a `critical` consistency issue when it detects:

- A document at the expected filename whose `version` is unchanged but whose content has diverged from the prior reviewed snapshot
- A new document whose `version` is N+1 but no predecessor file exists at version N

## Versioning rules

| Change | Version bump |
|---|---|
| Substantive content change (new section, changed requirement, changed decision) | minor or major |
| Structural change (sections added/removed, frontmatter fields changed) | major |
| Typo, formatting, clarification of an existing statement without changing meaning | patch |
| Status change only (draft → proposed → accepted) | none — same version, status field updated |

Semver-style: MAJOR.MINOR.PATCH. Initial version is always `1.0.0` once `status: accepted`. Drafts use `0.1.0`, `0.2.0`, etc., until first acceptance.

## Traceability rules

Every requirement and decision flows through the pipeline. The trace chain:

```
Intent Clarification doc  →  PRD (Functional Requirements)
                             ↓
                          Blueprint (Acceptance Criteria + Design)
                             ↓
                          Plan (Tasks with L1/L2/L3 verification)
                             ↓
                          Acceptance Tests (EARS, per Blueprint AC)
                             +
                          Phase Validators (per Plan phase)
```

### Trace ID requirements

| Document | Trace IDs it carries |
|---|---|
| PRD | `FR-N` (Functional Requirement) and `NFR-N` (Non-Functional Requirement) |
| Blueprint | References each `FR-N` in its Functional Requirements section; each AC references its FR; each Design subsection references the FRs it implements |
| Plan | Each task references the AC it satisfies (e.g., `satisfies: AC-FR-1-a`) and the Blueprint section it implements |
| Acceptance Tests | Each test references the AC it covers |
| Phase Validators | Each validator references the Plan phase and the ACs covered in that phase |

### Why this matters

`review-cross-artifact-auditor` runs at the Cross-Artifact Audit pass after the Plan and Tests are authored. Its primary check is that every PRD FR has a Blueprint AC, every Blueprint AC has a Plan task, every Plan task has an Acceptance Test or Phase Validator. Missing links → `critical` consistency issues.

## File-naming convention

Per ADR-0019 (naming convention) and the orchestrator's working-directory layout:

```
working/feature/<feature-slug>/
├── feature-scope.json              # orchestrator-side scope tracking
├── intent-clarification.md         # output of Intent Clarification
├── prd-v<N>.md                   # output of PRD Authoring (versioned)
├── research-plan.md                # output of Discovery Planning
├── codebase-analysis.json          # output of Discovery Research (codebase researcher)
├── external-research/              # output of Discovery Research (external researchers)
│   └── <topic>.md                     # one file per external research topic
├── synthesis.md                    # output of Synthesis
├── <layer>-design.md              # output of per-layer Design (one per activated layer)
├── blueprint-v<N>.md              # output of Design Composition (versioned)
├── adrs/                          # ADRs authored in Design Composition
│   └── ADR-NNNN-<slug>.md
├── architecture-audit-issues.json  # output of Architecture Audit
├── plan-v<N>.md                    # output of Plan Authoring (versioned)
├── acceptance-tests.md             # output of Acceptance Test Authoring
├── phase-validators.md             # output of Phase Validator Authoring
├── cross-artifact-audit-issues.json  # output of Cross-Artifact Audit
├── reconciliation-log.md           # output of Reconciliation
├── task-dag.json                   # output of Task Decomposition
└── issues-ledger.json                 # cross-pass issue tracker (per ADR-0008)
```

The numeric prefix is for sort order in directory listings, not for "referencing the stage by number" in any document or KB. Per the standing discipline, all prose references pipeline phases by name.

## Path discipline

Documents reference each other by path. Two patterns:

1. **Project-relative paths** for files under the project root: `working/feature/<slug>/blueprint-v1.md`
2. **Skill-relative paths** for KB references: `references/templates/blueprint-template.md`

Avoid absolute paths in document content — they break when the repo is moved or cloned. Frontmatter `predecessor:` and `derived_from:` use project-relative paths.

## YAML pitfalls

Most failures come from edge cases in YAML that look fine but parse unexpectedly:

- **Unquoted strings with colons** parse as keys: `description: This is the v1: initial draft` becomes a parse error. Quote: `description: "This is the v1: initial draft"`.
- **Unquoted strings starting with `[` or `{`** parse as flow sequences/maps. If your value starts with a bracket, quote it.
- **Multi-line strings** use `>-` (folded, no trailing newline) or `|-` (literal, no trailing newline). The default `>` keeps a trailing newline that may matter.
- **Booleans:** YAML 1.1 treats `yes`, `no`, `on`, `off`, `y`, `n` as booleans. Always use `true`/`false` explicitly.
- **Tabs:** YAML disallows tabs as indentation. Use spaces. (Most editors auto-convert but verify before commit.)
- **Trailing whitespace** on the closing `---` line breaks parsing in some YAML libraries.

`shared-document-reviewer`'s Gate 0 runs a YAML parse on every document's frontmatter. Failures → `critical` rule-compliance issue.

## Cross-references between documents

When one document references another by id:

```markdown
See Blueprint v1.2.0 (`blueprint-v1-2-0.md`) for the integration design.
Decided in ADR-0023.
Implements FR-3 from the PRD.
```

- File references use the project-relative path in backticks
- Document IDs are bare (`ADR-0023`, `FR-3`)
- Versions are explicit when the reference is to a specific version, omitted when "the latest accepted" is implied

`review-cross-artifact-auditor` checks that every reference resolves — broken references → `important` completeness issue.

## v2 Amendments (per ADR-0032 + ADR-0036)

This section codifies the 5 coordinated changes from **ADR-0032 (Conventions canonicalization)** plus the single-location ADR placement convention from **ADR-0036**. ADR-0032 is the authoritative source — consult it for full rationale and validation evidence. This section makes the changes load-bearing for `shared-document-reviewer` and the FR-6 frontmatter validator (`validate_pipeline_frontmatter.py`).

### Change 1 — Universal required frontmatter fields

In addition to `id`, `version`, `status`, `generated`, `generated_by` (already documented above), every pipeline-artifact frontmatter MUST carry:

- `feature_slug: <slug>` — universal required (was: only some doc types per old spec)
- `derived_from: <path|list>` — universal required for every non-Intent-Clarification artifact
- `doc_type: <enum>` — universal required (per Change 4 below)

Gated artifacts (per Change 3 below) additionally require after reviewer pass:

- `gate_passed: <integer>` — which gate the artifact passed (1, 2, 3, ...)
- `approved_at: <ISO-8601-UTC>` — when reviewer pass occurred
- `reviewer_verdict: <string>` — Gate 0/1 pass + scores

Optional companion fields for revised artifacts:

- `revised: <ISO-8601-UTC>` — last revision timestamp
- `revision_reason: |` — multi-line pipe-folded description of why the revision occurred

### Change 2 — User-token chain pattern

Each gated stage's artifact carries the prior stage's confirmation token. The pattern:

| Artifact | Carries |
|---|---|
| `intent-clarification.md` | `user_token:` (own confirmation) |
| `prd-v<N>.md` | `intent_user_token:` (prior) + `user_token:` (own) |
| `research-plan.md` | `prd_user_token:` (prior) + `user_token:` (own) |
| `codebase-analysis.md` | `research_plan_user_token:` (prior) — no own token since analysis/log artifacts are not gated |
| `blueprint-v<N>.md` | `research_plan_user_token:` (prior chain) + `user_token:` (own) |
| `plan-v<N>.md` | `blueprint_user_token:` (prior) + `user_token:` (own) |

Downstream sub-agents reference these tokens in their rationale briefs as confirmation that the user actively gated upstream stages.

### Change 3 — Per-doc-type state vocabulary (3-tier)

The single 5-state vocabulary in the original spec (`draft | proposed | accepted | superseded | rejected`) is replaced with **three category vocabularies** dispatched by `doc_type`:

| Category | doc_types | Vocabulary |
|---|---|---|
| **Gated** | `intent-clarification`, `prd`, `research-plan`, `blueprint`, `plan` | `draft → accepted → superseded \| rejected` (5-state including intermediate `proposed` for some; intermediate forms vary per type) |
| **Analysis/log** | `codebase-analysis`, `synthesis`, `<layer>-design`, `architecture-audit-issues`, `cross-artifact-audit-issues`, `acceptance-tests`, `phase-validators`, `reconciliation-log`, `task-dag`, plus execution-phase types (`per-task-execution-result`, `phase-quality-report`, `quality-reconciliation-log`, `state-transitions-log`, `pipeline-run-summary`) | `draft → complete \| superseded` (3-state — `complete` is the post-reviewer ratified state for non-gated artifacts) |
| **ADRs** | `adr` (single doc-type) | `proposed → accepted \| superseded \| rejected` (4-state, no `draft`) |

This dispatch resolves the prior drift where `codebase-analysis.md` carried `status: complete` (invalid under the old single-vocab) and `synthesis.md` would have stayed `status: draft` indefinitely.

### Change 4 — `doc_type` field as universal required (20+5 enum)

Every pipeline-artifact frontmatter MUST declare `doc_type:` from the canonical enum:

**Planning-side (20 values)**: `intent-clarification`, `prd`, `research-plan`, `codebase-analysis`, `synthesis`, `<layer>-design` (e.g., `claude-code-design`, `backend-design`), `blueprint`, `architecture-audit-issues`, `plan`, `acceptance-tests`, `phase-validators`, `cross-artifact-audit-issues`, `reconciliation-log`, `task-dag`, `adr`, plus suffix patterns like `*-report` and `*-result`.

**Execution-side (5 values, new with this convention)**: `per-task-execution-result`, `phase-quality-report`, `quality-reconciliation-log`, `state-transitions-log`, `pipeline-run-summary`.

`shared-document-reviewer` uses `doc_type` as the dispatch key for type-specific checks; `validate_pipeline_frontmatter.py` uses it to look up the per-doc-type vocabulary and required-field set.

### Change 5 — Execution-phase artifact frontmatter

Execution-phase artifacts (the 5 new `doc_type` values) follow the analysis/log vocabulary (3-state: `draft → complete | superseded`) and add execution-specific fields:

- `task_id:` — for `per-task-execution-result` artifacts
- `phase_id:` — for `phase-quality-report`, `quality-reconciliation-log` artifacts
- `cycle:` — for `quality-reconciliation-log` artifacts (per ADR-0017 cap)
- `feature_slug:` — universal
- `derived_from:` — for state-transitions-log + pipeline-run-summary, omits this field per their nature (cumulative logs, not derived)

The 5 execution-phase artifact templates live at:

- `KB-documentation-criteria/references/templates/per-task-execution-result-template.md`
- `KB-documentation-criteria/references/templates/phase-quality-report-template.md`
- `KB-documentation-criteria/references/templates/quality-reconciliation-log-template.md`
- `KB-documentation-criteria/references/templates/state-transitions-log-entry-template.md`
- `KB-documentation-criteria/references/templates/pipeline-run-summary-template.md`

### ADR placement convention (per ADR-0036)

ADRs live in exactly one canonical location: `adrs/ADR-NNNN-<slug>.md` at the project root. The dual-location convention from the original deliverable-archive-spec is retired. See ADR-0036 for full rationale.

### Migration / enforcement

- **Forward-scoped**: the FR-6 frontmatter validator enforces these conventions from this feature's ratification date forward. Historical artifacts authored before ratification are not retroactively flagged.
- **Planning-side agents**: the ~20+ planning-side agents that author pipeline artifacts need `doc_type:` emission added to their author-prompts. This is the deferred scope of the `planning-agent-doctype-backfill-r1` feature (see `working/feature/planning-agent-doctype-backfill-r1/intent-clarification.md`). Until that feature ships, new planning-side artifacts will surface a `doc_type missing` MAJOR finding at Gate 0 — surfaced explicitly per ADR-0033 no-silent-absorption.
- **Execution-side agents**: the 5 new `execute-*` agents author with `doc_type` from inception per Plan v2 Phase 3.
