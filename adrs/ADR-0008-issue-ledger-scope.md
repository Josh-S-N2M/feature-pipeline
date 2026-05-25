---
id: ADR-0008
version: 2.1.0
status: Accepted
generated: 2026-05-19
generated_by: finalize-reconciler (v4.3.0 naming-convention retroactive update per ADR-0019)
supersedes:
  - {id: ADR-0008, version: 1.0.0}
adrs_inherited:
  - ADR-0005 (append-only supersession)
  - ADR-0006 (synthesis stages inlined into feature-pipeline)
applies_to:
  - feature-pipeline
template_format: per ADR.txt v1.0
---

# ADR-0008: Issue ledger scope — per-feature with cross-feature pattern surfacing

## Status

Accepted — 2026-05-12 (template-migrated from v1.0.0 of the same date)

## Context

Blueprint v3 introduces a formal issue lifecycle with a state machine (open → triaged → addressed → verifying → verified → closed, plus side states). Issues are written to an `issues-ledger.json` file. The lifecycle and ledger were specified in the critique-discipline-upgrade deliverable.

A question that the upgrade deliverable raised but did not resolve: what is the scope of the ledger? Three plausible options exist:

- **Per-run scope:** each pipeline invocation gets its own ledger. Simple. Loses institutional memory between runs.
- **Per-feature scope:** all runs against the same feature share a ledger. Resume and re-invocation accumulate context.
- **Project-wide scope:** all features in a project share one ledger. Maximum memory; high noise risk.

User Q-3 clarification: cross-feature learning IS valuable, AND each feature's critique context should not be polluted by unrelated history.

## Decision

**Per-feature scope** for the active issue ledger. **Plus** a separate, project-level cross-feature-patterns file for pattern accumulation.

Specifically:
- Active issue ledger: `working/feature/<feature-slug>/issues-ledger.json`, accumulates across runs of the same feature, stable feature-slug across runs.
- Cross-feature patterns file: `.claude/feature-pipeline/cross-feature-patterns.md`, plain markdown, append-only, human-curated.

## Decision Details

| Item | Content |
|---|---|
| Decision | Issue ledger is per-feature (keyed by stable feature-slug). Cross-feature patterns live in a separate human-curated file. Pipeline surfaces patterns; does not auto-curate. |
| Why now | Issue lifecycle was specified before this; the scope question was deferred. Settling scope before shared-document-reviewer integration (ADR-0017 forthcoming at the time) so the reviewer can interact with the ledger correctly. |
| Why this | Per-run loses verified-issue continuity (MAST FM-1.3 step repetition at 15.7%); project-wide drowns critics in irrelevant noise (claim C-R2-0011 knowledge budget consumption); per-feature with separate cross-feature surface satisfies the user's two requirements (cross-feature learning + clean per-feature context). |
| Known unknowns | Whether per-feature ledger files grow unbounded across many runs (archival policy mitigates but not yet operationalized); whether cross-feature pattern text-similarity detection has acceptable false-positive/false-negative rates (deferred to practical experience). |
| Kill criteria | If per-feature ledgers reach unwieldy sizes (>10MB or >1000 issues) without archival policy enforcement working, OR if cross-feature pattern detection produces enough false positives that humans stop reviewing surfaced patterns (3+ instances of dismissed-as-noise in a 30-day window), supersede with a revised scope and surfacing design. |

## Rationale

The three scope options have different failure modes (per the original v1.0.0 reasoning, preserved verbatim):

**Per-run scope fails on continuity.** A user who resumes a feature after a week loses all the per-issue rationale from the first run. Critique-2 in the resumed run might rediscover and re-open issues that the first run had verified. This is MAST FM-1.3 (step repetition, 15.7% of multi-agent failures per claim C-R2-0024) at the meta level — the system as a whole repeating work because of state loss between sessions.

**Project-wide scope fails on relevance.** A critic running on feature Z sees issues from features A–Y. Most are irrelevant. The critic's context budget fills with noise; per claim C-R2-0018, attention degrades; per claim C-R2-0011, the ~30-40% knowledge budget is consumed by irrelevant entries; the critic does worse on its actual job.

**Per-feature with cross-feature pattern surfacing satisfies both.** Each feature's ledger contains exactly the issues relevant to that feature's history. The cross-feature-patterns file holds the meta-pattern signal in a separate, smaller, human-curated artifact.

The pipeline's job is to make patterns *visible enough for humans to curate*, not to auto-curate. Automatic cross-feature pattern detection is a hard problem with high false-positive cost.

## Options Considered

**Option 1: Per-run scope.** Each invocation has its own ledger.
- Pros: simple; no state across runs.
- Cons: rejected — loses verified-issue continuity across resumes; contradicts pipeline's resume semantics.

**Option 2: Project-wide scope with relevance filtering at read time.** Each critique reads the full project ledger but filters by feature-relevance.
- Pros: maximum institutional memory.
- Cons: rejected — filtering heuristics weaker than keeping feature-scoped ledgers separate; adds per-critique compute cost.

**Option 3: Per-feature with automatic cross-feature pattern detection.** Algorithm auto-flags recurring patterns.
- Pros: full automation.
- Cons: rejected — false-positive cost is high; premature automation. The cross-feature-patterns file with human curation is the v3 design; if it works well, a future ADR could promote some patterns to auto-detection.

**Option 4: Append-only event log with derived-state views.** True event-sourcing.
- Pros: maximum auditability.
- Cons: deferred — adds implementation complexity disproportionate to current need. Current ledger IS append-only at the transition level; full event-sourcing is the next level of rigor.

**Option 5 (Selected): Per-feature ledger + project-wide human-curated cross-feature-patterns file.**
- Pros: satisfies user's two requirements; bounded context per critique; human agency at pattern curation.
- Cons: feature-slug collision risk (mitigated by intent-clarifier check); per-feature files grow unbounded across runs (mitigated by archival policy).

## Consequences

### Positive Consequences

- Resume/re-entry semantics preserve verified-issue history. Reduces step repetition (the highest-frequency multi-agent failure mode at 15.7%).
- Cross-feature patterns remain visible without polluting per-feature critique context.
- Human triage retains agency. Pipeline surfaces signal; humans decide.
- The feature-slug namespacing means project-level operations are simple (each feature is a self-contained subtree under `working/feature/`).
- `cross-feature-patterns.md` is a discoverable, editable artifact — users can add patterns themselves between runs.

### Negative Consequences

- Per-feature ledger files grow unbounded across many runs. Mitigation: archival policy — after a feature is `closed` and N days pass (suggested: 90), orchestrator archives the working directory to `working/feature/_archived/<feature-slug>-<archive-date>/`.
- Cross-feature pattern detection depends on text-similarity heuristics, which have known false-positive and false-negative rates. The pipeline does NOT claim these are reliable; it surfaces candidates to human triage.
- Feature-slug collision is possible. Mitigation: intake-intent-clarifier checks against existing feature-slugs at Stage 1 and asks the user if there's ambiguity.

### Neutral Consequences

- The decision is reversible if pain emerges in practice. The ledger format is JSON; migration to project-wide scope (if needed) is a one-time merge operation. Per-run scope (if needed) is a one-time partition.

## Architecture Impact

**Components that change:**
- New artifact: `working/feature/<feature-slug>/issues-ledger.json` (per feature).
- New artifact: `.claude/feature-pipeline/cross-feature-patterns.md` (project-wide).
- Stage 0 preflight: extended to load existing ledger (if present) and read cross-feature patterns.
- All critique sub-agents: read both artifacts as part of their context.
- finalize-reconciler: appends transitions to the ledger rather than rewriting.
- intake-intent-clarifier: checks against existing feature-slugs and asks user on ambiguity.

**New dependencies introduced:**
- Per-feature ledger persistence depends on a stable feature-slug derivation at Stage 1.
- Cross-feature surfacing depends on text-similarity computation (cosine on embedded issue evidence).

**Architectural constraints added:**
- Feature-slug MUST be stable across runs of the same feature (canonical, derived once at Stage 1, reused).
- New issues opened in Run N MUST continue the issue-ID sequence from prior runs (no reset).
- Verified/closed/dismissed issues from prior runs MUST remain visible to current run's critiques.
- Reopened-issue transitions MUST include `reopened_reason` with evidence.

**Architectural constraints removed:**
- Per-run ledger isolation (the simpler default) is forbidden by this ADR.

## Implementation Guidance

- Feature-slug derivation: intake-intent-clarifier produces canonical slug at Stage 1 (e.g., `add-healthz-endpoint`); collision-handled with numerical suffix.
- Ledger entry schema: per blueprint v3 §3.7 fixed-point iteration discipline.
- Cross-feature surfacing: when new issue's `origin.evidence` text is >0.7 cosine similar to a verified/dismissed issue in same feature OR a pattern entry in cross-feature-patterns.md, new issue includes `similar_to` field.
- Archival: orchestrator archives after `closed` + 90 days; active features (most recent run within 90 days) stay in live working tree.

## Related Information

- Original ADR-0008 v1.0.0: preserved at `ADR-0008-issue-ledger-scope-pre-template-migration.md` per ADR-0014.
- ADR-0005: append-only supersession (governs ledger entries' immutability — each transition is a new entry).
- ADR-0009: rationale brief — surfaces previously-resolved issues from this ledger to each sub-agent invocation.
- ADR-0017: shared-document-reviewer integration — reviewer's prior_context_check mechanism integrates with this ledger.
- Claims: C-R2-0024 (MAST FM-1.3 step repetition 15.7%), C-R2-0017 (external memory as source of truth), C-R2-0029 (defect lifecycle), C-R2-0026 (agent drift).
- User decision: per-Q3 clarification on cross-feature learning + clean per-feature context.

## v4.3.0 retroactive naming-convention update

Per ADR-0019, all sub-agent, knowledge skill, and orchestrator skill references in this ADR have been updated to the v4.3.0 naming convention (phase-prefixed sub-agents, KB-prefixed knowledge skills, recipe-prefixed orchestrator, shared-prefixed cross-phase sub-agents). The pre-update version is preserved at `ADR-0008-issue-ledger-scope-pre-naming-convention.md`. The decision recorded in this ADR is unchanged; only entity names are updated for cross-document consistency.
