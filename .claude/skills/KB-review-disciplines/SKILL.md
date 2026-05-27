---
name: kb-review-disciplines
description: >-
  Consolidated review disciplines for the three reviewer sub-agents in
  the feature-pipeline: shared-document-reviewer (Gate 0/1 structural
  and quality review of any pipeline document), review-architecture-auditor
  (substantive audit during the Architecture Audit pass using CoVe + blast-radius + brief-honor),
  and review-cross-artifact-auditor (performs the Cross-Artifact Audit consistency check using CMC
  + diff-mode + convergence). Load when authoring or running any of these
  three reviewers. Also defines the severity taxonomy, issue lifecycle,
  and prior_context_check semantics shared across all three. Absorbs the
  v4.2-era document-review-knowledge, architecture-audit-knowledge, and
  cross-artifact-audit-knowledge skills per ADR-0020.
---

# Review Disciplines

This KB consolidates the procedure, methodology, and severity taxonomy used by the three reviewer sub-agents in the feature-pipeline:

| Sub-agent | When invoked | Discipline | Reference |
|---|---|---|---|
| `shared-document-reviewer` | Per ADR-0017: after Intent Clarification, after PRD, after Blueprint composition, after Plan authoring, and after each ADR write | Gate 0 (structural) + Gate 1 (quality) | `references/gate-0-1-procedure.md` |
| `review-architecture-auditor` | After Blueprint composition + Gate 1, on the Blueprint | CoVe + blast-radius + brief-honor | `references/architecture-audit.md` |
| `review-cross-artifact-auditor` | After Plan + Tests + Phase Validators are authored | CMC + diff-mode + convergence | `references/cross-artifact-audit.md` |

Plus shared concerns used by all three:

| Concern | Reference |
|---|---|
| Severity values, when to use each, scoring → verdict mapping | `references/severity-taxonomy.md` |
| Issue ID format, lifecycle, ledger interaction (per ADR-0008) | `references/issue-lifecycle.md` |
| `prior_context_check` semantics across iterations | `references/prior-context-check.md` |

## The three reviewers, briefly

### `shared-document-reviewer` — Gate 0/1 on every pipeline document

Runs at the 5 invocation points per ADR-0017. Sees the document, the rationale brief, optionally a codebase analysis JSON (when reviewing a Blueprint), and any prior context from earlier iterations. Produces a structured JSON verdict (approved / approved_with_conditions / needs_revision / rejected) with issues, scores, and a `prior_context_check` block when relevant.

Gate 0 is purely structural: required sections present, frontmatter complete, EARS keywords intact. Gate 1 is quality: consistency, completeness, rule compliance, clarity, feasibility, plus document-type-specific checks (Fact Disposition Table coverage for DesignDoc, etc.).

Gate 0 failure → `needs_revision` immediately; Gate 1 is not run. Gate 1 produces the score-band verdict.

### `review-architecture-auditor` — substantive architectural audit on the Blueprint

The Design Composition document-reviewer pass is structural-and-quality. The Architecture Audit is the substantive audit: does the Blueprint reflect a sound architecture given the synthesis claims, the codebase analysis, and the prior ADRs?

Uses three techniques in combination:

- **CoVe (Chain of Verification):** the auditor produces verification questions for each substantive claim in the Blueprint, then answers them by re-grounding against synthesis claims and the codebase. Inconsistent answers → issue.
- **Blast-radius analysis:** uses Read+Grep+Glob plus serena's symbol-level MCP tools (`find_referencing_symbols` is the canonical reverse-dependency lookup) to enumerate everything that touches the components the Blueprint proposes to change. Surfaces any blast-radius items the Blueprint failed to acknowledge.
- **Brief-honor verification:** checks every Blueprint decision against the rationale brief's commitments. Decisions that contradict the brief, ignore an open item, or re-surface a previously-resolved issue → flagged.

### `review-cross-artifact-auditor` — cross-artifact consistency check

Runs after the Plan and the Tests are authored. Verifies cross-artifact consistency between Blueprint ↔ Plan ↔ Tests ↔ Phase Validators.

Uses:

- **CMC (Cross-Model Critique):** posture-declares `model: opus` in its frontmatter when the main agent is Sonnet, to get a different model's perspective on the consistency.
- **Diff-mode input:** does NOT see the full upstream context. Sees only the diff Blueprint v(N) vs v(N-1), plus the Plan, Tests, and the prior round's critique. This prevents the auditor from accumulating context and silently smoothing over real inconsistencies.
- **Convergence-based termination:** four-cycle hard cap. If the auditor surfaces new issues four iterations in a row without convergence, halt and surface to user.

## Severity taxonomy (used by all three)

Every issue carries a severity. Three values:

| Severity | Meaning | Verdict effect |
|---|---|---|
| `critical` | Blocks acceptance. Architecturally wrong, security-breaking, or a hard contract violation. | Forces `needs_revision` or `rejected` |
| `important` | Should be fixed before approval, but not architecturally fatal. Score-degrading. | Pushes verdict toward `approved_with_conditions` or `needs_revision` |
| `recommended` | Improvement suggestion. Non-blocking. | No verdict effect by itself |

Full taxonomy and the score-to-verdict mapping in `references/severity-taxonomy.md`.

## Issue lifecycle (used by all three)

Issues persist across iterations via the issues-ledger (per ADR-0008). Each issue has:

- a stable ID (`I-<reviewer-prefix>-NNN`, e.g. `I-DR-005`, `I-AA-004`, `I-CA-002`)
- a status (`open`, `resolved`, `wontfix-with-rationale`, `superseded`)
- a creation iteration and resolution iteration
- a category, severity, location, description, suggestion

Reviewer prefixes:

| Reviewer | Prefix |
|---|---|
| `shared-document-reviewer` | `DR` (document review) |
| `review-architecture-auditor` | `AA` (architecture audit) |
| `review-cross-artifact-auditor` | `CA` (cross-artifact audit) |

Full lifecycle in `references/issue-lifecycle.md`.

## Prior-context check (used by all three)

When a reviewer is invoked on the N-th iteration of a document, it receives the prior round's open issues as `prior_context`. The reviewer MUST, before running its main checks:

1. Parse the prior context (JSON or referenced issues-ledger entries)
2. For each prior-context item: locate the section it refers to and check whether it's been addressed
3. Classify each as `resolved` / `partially_resolved` / `unresolved`
4. Include a `prior_context_check` block in the output JSON

Reviewers that skip this step risk re-surfacing previously-resolved issues, which creates iteration loops. Full semantics in `references/prior-context-check.md`.

## When to load which reference

| You are… | Load this reference |
|---|---|
| Implementing or invoking `shared-document-reviewer` | `gate-0-1-procedure.md` + `severity-taxonomy.md` + `issue-lifecycle.md` + `prior-context-check.md` |
| Implementing or invoking `review-architecture-auditor` | `architecture-audit.md` + `severity-taxonomy.md` + `issue-lifecycle.md` + `prior-context-check.md` |
| Implementing or invoking `review-cross-artifact-auditor` | `cross-artifact-audit.md` + `severity-taxonomy.md` + `issue-lifecycle.md` + `prior-context-check.md` |
| Triaging issues from the ledger | `severity-taxonomy.md` + `issue-lifecycle.md` |
| Debugging an iteration loop (issues keep re-surfacing) | `prior-context-check.md` first; then the relevant reviewer's reference |

## Provenance

Status: Accepted — v1.0.0 (Phase 2 of feature-pipeline v4.3.0)
Absorbs (per ADR-0020):
- `document-review-knowledge` v4.2 — the Gate 0/1 procedure
- `architecture-audit-knowledge` (formerly `critique-1-knowledge`) v4.2 — CoVe + blast-radius + brief-honor
- `cross-artifact-audit-knowledge` (formerly `critique-2-knowledge`) v4.2 — CMC + diff-mode + convergence

Earlier rename history: `critique-1-knowledge` → `architecture-audit-knowledge` (v4.0); `critique-2-knowledge` → `cross-artifact-audit-knowledge` (v4.0). Both absorbed into this KB at v4.3 per ADR-0020.
