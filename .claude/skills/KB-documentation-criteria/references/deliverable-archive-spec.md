# Deliverable-archive spec

A feature run's deliverable archive lives at `working/feature/<slug>/`. Different scope classes (per ADR-0023) execute different stages of the 13-stage pipeline; the expected-artifact set therefore varies by scope. This document specifies what artifacts each scope class must produce, what artifacts are conditional, and how the deliverable-archive validator (`shared-document-reviewer` invoked with `doc_type: DeliverableArchive`) checks the archive against this spec.

## Contents

- [x] Scope classes and their stage sets
- [x] FULL scope — all 13 stages
- [x] MINOR scope — shortened sequence
- [x] PATCH scope — minimal sequence
- [x] Versioning convention for `*-v<N>.md` files
- [x] ADR placement convention
- [x] Handoff document convention
- [x] Patterns and anti-patterns
- [x] Cross-references

## Scope classes and their stage sets

ADR-0023 defines three scope classes for feature runs. Each runs a subset of the pipeline:

| Scope | Use when | Stages |
|---|---|---|
| FULL | New capability; new architectural surface; >1 layer affected | All 13 |
| MINOR | New sub-agent OR new KB OR backward-compatible extension to existing surfaces | Skip Discovery / Research / Synthesis if requirements already known |
| PATCH | Bug fix; documentation; small-scope edits to existing artifacts | Skip Discovery / Synthesis / per-layer Design / Architecture Audit / Cross-Audit / Reconciliation / Task Decomposition |

The scope class is declared in `intent-clarification.md`'s `scope_class:` frontmatter field. The validator reads it from there.

**Inference fallback (pre-v4.5.0 archives).** Archives created before v4.5.0 may lack the `scope_class:` declaration (the field convention was introduced in v4.5.0). When absent, the validator infers scope class from the archive contents:

- If `research-plan.md` + `synthesis.md` present → inferred FULL.
- If `<layer>-design.md` present but `research-plan.md` absent → inferred MINOR.
- Otherwise → inferred PATCH.

Inferred scope is treated as MINOR finding ("scope_class not declared; inferred as <CLASS> from archive contents — declare explicitly in future runs"). Validation proceeds against the inferred class.

## FULL scope — all 13 stages

Required artifacts (BLOCKER if missing):

| Artifact | Stage that produces it |
|---|---|
| `intent-clarification.md` | Intent Clarification |
| `prd-v<N>.md` (highest N) | PRD Authoring |
| `research-plan.md` | Discovery Planning |
| `research-notes/<topic>.md` (at least one) | Discovery Research |
| `codebase-analysis.json` + `codebase-analysis-report.md` | Discovery Research |
| `synthesis.md` (or `synthesis/`) | Synthesis |
| `<layer>-design.md` + `<layer>-dependencies.json` (at least one layer) | per-layer Design |
| `blueprint-v<N>.md` | Design Composition |
| `architecture-audit-issues.json` | Architecture Audit |
| `plan-v<N>.md` | Plan Authoring |
| `acceptance-tests.md` | Acceptance Test Authoring |
| `phase-validators.md` | Phase Validator Authoring |
| `cross-artifact-audit-issues.json` | Cross-Artifact Audit |
| `tasks.json` | Task Decomposition |
| `checkpoint.json` | (continuously updated) |
| `packager-report.json` | Deliverable Packaging (added in v4.5.0; see backward-compat note below) |

**Backward-compat note (v4.5.0 transition):** Archives created before v4.5.0 (e.g., `frontend-design-knowledge-r1` and `audit-machinery-fixes-r1` in v4.4.x) do not have `packager-report.json`. The validator treats missing `packager-report.json` as MINOR (not BLOCKER) if `working/feature/<slug>/checkpoint.json` shows a `current_stage: complete` timestamp predating v4.5.0's release. New runs (post-v4.5.0) treat missing `packager-report.json` as BLOCKER.

Conditional artifacts (MAJOR if missing without justification):

| Artifact | Condition for being expected |
|---|---|
| `adrs/ADR-NNNN-<slug>.md` | Required if `adrs_authored` non-empty in Blueprint frontmatter |
| Multiple `<layer>-design.md` files | One per activated layer in the Blueprint |
| `prd-v<N>.md` with N > 1 | Required if Reconciliation cycle re-authored the PRD |
| `blueprint-v<N>.md` with N > 1 | Same |
| `plan-v<N>.md` with N > 1 | Same |
| `intent-clarification.v<X>.<Y>.<Z>.md` versioned copies | Allowed when intent was iterated pre-Gate-1 approval |

## MINOR scope — shortened sequence

When `scope_class: MINOR` is declared, the following stages MAY be skipped (with justification in intent-clarification's `discovery_shortcut` section). If skipped, the corresponding artifact is omitted from the expected set:

| Skippable stage | Skipped-when |
|---|---|
| Discovery Planning + Research + Synthesis | Requirements already documented (e.g., from an upstream ADR) |
| Cross-Artifact Audit | Single-domain feature with no cross-layer interactions |
| Task Decomposition | Plan tasks atomic enough at this scope |

Required artifacts for MINOR (BLOCKER if missing):

- `intent-clarification.md` (with `scope_class: MINOR` declared)
- `prd-v<N>.md`
- At least one `<layer>-design.md` + `<layer>-dependencies.json` (the activated layer)
- `blueprint-v<N>.md`
- `plan-v<N>.md`
- `acceptance-tests.md`
- `phase-validators.md`
- `packager-report.json`

Conditional artifacts (MAJOR if missing without justification): same as FULL.

## PATCH scope — minimal sequence

When `scope_class: PATCH` is declared, this set of stages MAY be skipped per ADR-0023:

| Skippable stage | Always skipped for PATCH |
|---|---|
| Discovery Planning + Research + Synthesis | Yes |
| per-layer Design | Yes (no architectural surface change) |
| Architecture Audit | Yes |
| Cross-Artifact Audit | Yes |
| Reconciliation | Yes (no reviewer cycle) |
| Task Decomposition | Yes |

Required artifacts for PATCH (BLOCKER if missing):

- `intent-clarification.md` (with `scope_class: PATCH` declared + `discovery_shortcut` section enumerating skipped stages)
- `prd-v<N>.md`
- `blueprint-v<N>.md`
- `plan-v<N>.md`
- `acceptance-tests.md`
- `phase-validators.md`
- `packager-report.json`

Conditional artifacts:

| Artifact | Condition |
|---|---|
| `adrs/ADR-NNNN-<slug>.md` | Required if `adrs_authored` non-empty in Blueprint |

Even at PATCH scope, the irreducible artifact set is six markdown files (intent + PRD + blueprint + plan + acceptance-tests + phase-validators) plus the packager report. This is the discipline floor.

## Versioning convention for `*-v<N>.md` files

`prd-v<N>.md`, `blueprint-v<N>.md`, `plan-v<N>.md` files are version-suffixed. Conventions:

- **Initial version is `v1`.** First approved iteration is `prd-v1.md`, etc.
- **Reconciliation cycles bump N.** When `finalize-reconciler` directs re-authoring of an artifact, the new version supersedes (per ADR-0005 append-only) and is written as `prd-v2.md`, etc. Prior versions remain in the archive.
- **Typically aligned.** If PRD reaches v3, Blueprint and Plan are usually v2 or v3 (one cycle behind, since Blueprint and Plan are re-derived from PRD).
- **Validator reads highest N.** When checking "PRD present," the validator finds the highest-N file. Lower-N versions remain as historical record.

## ADR placement convention

ADRs land in two locations:

1. **Project-wide registry:** `adrs/ADR-NNNN-<title>.md`. Numbered sequentially across the entire project's lifetime. The canonical location for cross-feature ADR reference.
2. **Feature-scoped copy:** `working/feature/<slug>/adrs/ADR-NNNN-<slug>.md`. Same file copied (per ADR-0005 append-only — both locations preserved). Allows the feature archive to be self-contained without forcing readers to traverse the project registry.

The validator checks both locations for each ADR listed in the Blueprint's `adrs_authored` frontmatter field.

## Handoff document convention

Versioned handoff documents at `handoff/HANDOFF-v<X.Y.Z>.md` + `handoff/CONTINUE_PROMPT-v<X.Y.Z>.md` are project-level (not feature-scoped). The packager can produce drafts of these from a template; drafts are reviewed before final commit.

`<X.Y.Z>` matches the project version, not the feature slug. A single feature run can bump the project from v4.4.2 to v4.5.0; the handoff document is named for the new project version.

## Patterns and anti-patterns

**Pattern: declare scope class explicitly.** Always set `scope_class:` in intent-clarification frontmatter. The validator depends on it. Defaulting to FULL is the safest choice when uncertain.

**Pattern: justify skipped stages in `discovery_shortcut`.** When a stage is skipped, explain why in intent-clarification's `## Discovery shortcut` section. The validator reads this to disposition conditional artifacts.

**Pattern: feature-scoped ADRs at both locations.** When an ADR is authored, write it once at `working/feature/<slug>/adrs/` AND copy to `adrs/`. Bulk-copy via `cp` after each ADR ratification.

**Anti-pattern: archive without intent-clarification.** Without `intent-clarification.md` declaring scope class, the validator can't determine the expected-artifact set. Every feature run starts with intent-clarification; no exceptions.

**Anti-pattern: PATCH scope hiding architectural change.** PATCH skips per-layer Design and Architecture Audit. If a "PATCH" feature actually introduces architectural change, it should escalate to MINOR or FULL. The validator can't detect this directly; reviewers should challenge questionable scope declarations.

**Anti-pattern: missing packager report.** Even at PATCH scope, the packager runs and emits `packager-report.json`. This is the validator's own audit trail; its absence indicates the packager never ran (a process gap).

**Anti-pattern: orphan archive (artifacts present but no intent-clarification).** Archives created outside the formal pipeline (manual hand-execution; partial migrations) often lack intent-clarification. The validator reports these as BLOCKER. The fix is to author retroactive intent-clarification declaring the actual scope, then re-validate.

## Cross-references

- **`KB-documentation-criteria/references/disciplines/design-composition.md`** — where the `working/feature/<slug>/` convention is documented for the design-composition stage specifically.
- **`KB-review-disciplines/references/issue-lifecycle.md`** — issues ledger at `working/feature/<slug>/issues-ledger.json`.
- **ADR-0023** — Discipline refinements from integration test (the scope-class taxonomy this spec implements).
- **ADR-0027** — Pipeline skill-design gap (the gap discovery that motivated this spec).
- **ADR-0028** — Skill-design fixes shipped in v4.5.0 (the implementation closure).
- **`finalize-deliverable-packager.md`** in `.claude/agents/` — the agent that invokes the validator with this spec.
- **`shared-document-reviewer.md`** in `.claude/agents/` — the validator agent with the `DeliverableArchive` doc_type.
