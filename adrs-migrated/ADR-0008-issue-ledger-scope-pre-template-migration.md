---
id: ADR-0008
version: 1.0.0
status: Accepted
generated: 2026-05-12
generated_by: synth-designer (new ADR for blueprint v3)
supersedes: []
adrs_inherited:
  - ADR-0005 (append-only supersession)
  - ADR-0006 (synthesis stages inlined into feature-pipeline)
---

# ADR-0008: Issue ledger scope — per-feature with cross-feature pattern surfacing

## Status
Accepted — 2026-05-12

## Context

Blueprint v3 (forthcoming) introduces a formal issue lifecycle with a state machine (open → triaged → addressed → verifying → verified → closed, plus side states). Issues are written to an `issues-ledger.json` file. The lifecycle and ledger were specified in the critique-discipline-upgrade deliverable.

A question that the upgrade deliverable raised but did not resolve: what is the scope of the ledger? Three plausible options exist, with different operational and learning properties:

- **Per-run scope:** each pipeline invocation gets its own ledger, scoped to `working/feature/<run-id>/`. Simple. Loses institutional memory between runs.
- **Per-feature scope:** all runs against the same feature share a ledger at `working/feature/<feature-slug>/`. Resume and re-invocation accumulate context. Adds re-entry complexity.
- **Project-wide scope:** all features in a project share one ledger at `.claude/feature-pipeline/`. Maximum memory; high noise risk.

The decision affects how the pipeline handles repeated feature work, how patterns surface across features, how the orchestrator initializes a new run, and how downstream critique stages weigh prior-resolution context.

## Decision

**Per-feature scope** for the active issue ledger. **Plus** a separate, project-level cross-feature-patterns file for pattern accumulation.

Specifically:

### Active issue ledger (per-feature)

Lives at `working/feature/<feature-slug>/issues-ledger.json` where `<feature-slug>` is the intent-derived slug stable across runs.

This file accumulates across runs of the same feature:
- Run 1 of "add /healthz endpoint" creates the ledger.
- Run 2 (resume, retry, or extension) reads the existing ledger and appends new transitions.
- Verified issues from Run 1 are still verified in Run 2. Dismissed issues are still dismissed.
- Run 2's critiques see the full history.

`<feature-slug>` derivation: synth-intent-clarifier produces a slug at Stage 1 (e.g., `add-healthz-endpoint`). The slug is canonical for the feature; runs against the same feature use the same slug. A new feature with similar intent gets a different slug (potentially with a numerical suffix if collision: `add-healthz-endpoint-2`).

### Cross-feature patterns file (project-wide)

Lives at `.claude/feature-pipeline/cross-feature-patterns.md`.

Plain markdown, append-only, human-curated. Format: one section per pattern, with the pattern description, the features where it surfaced, and the recommended pipeline-level resolution.

```markdown
# Cross-feature patterns

## Pattern: synth-acceptance-tester confused about plan vs blueprint inputs
**First observed:** add-healthz-endpoint (Run 2, Iteration 1)
**Re-observed:** add-webhooks (Run 1, Iteration 1)
**Hypothesis:** Tool allowlist enforcement via prompt-level prohibition is not sufficient.
**Recommended pipeline-level resolution:** Investigate path-restricted Read tool when Claude Code supports it.
**Status:** Open
```

The pipeline does NOT auto-populate this file. Sub-agents that surface a new issue can suggest "this looks like pattern X from cross-feature-patterns.md," and the human triage gate is where humans recognize patterns and add new entries to the file.

This separation is deliberate: automatic cross-feature pattern detection is a hard problem (false positives produce noise; false negatives lose signal). The pipeline's job is to make patterns *visible enough for humans to curate*, not to auto-curate.

## Why per-feature with cross-feature pattern surfacing

The three scope options have different failure modes. The user's clarifying answer (Q-3) emphasized two requirements: cross-feature learning IS valuable, AND each feature's critique context should not be polluted by unrelated history.

These are in tension. The resolution:

**Per-run scope fails on continuity.** A user who resumes a feature after a week loses all the per-issue rationale from the first run. Critique-2 in the resumed run might rediscover and re-open issues that the first run had verified. This is MAST FM-1.3 (step repetition, 15.7% of multi-agent failures per claim C-R2-0024) at the meta level — the system as a whole repeating work because of state loss between sessions.

**Project-wide scope fails on relevance.** A critic running on feature Z sees issues from features A–Y. Most are irrelevant. The critic's context budget fills with noise; per claim C-R2-0018, attention degrades; per claim C-R2-0011, the ~30-40% knowledge budget is consumed by irrelevant entries; the critic does worse on its actual job.

**Per-feature with cross-feature pattern surfacing satisfies both.** Each feature's ledger contains exactly the issues relevant to that feature's history — past runs that produced verified resolutions are still visible. The cross-feature-patterns file holds the meta-pattern signal in a separate, smaller, human-curated artifact. Sub-agents read both, weight the patterns appropriately, and don't drown in noise.

### Operational semantics

**Stage 0 preflight extension:**

- Detect existing `working/feature/<feature-slug>/issues-ledger.json` from prior runs.
- If exists: load. Mark all issues whose `current_state` is `verified`, `closed`, or `dismissed` as "carried forward."
- If not: initialize fresh ledger.
- Load `.claude/feature-pipeline/cross-feature-patterns.md` if present. Pass content (or a relevant excerpt) to downstream critique sub-agents via the rationale brief (ADR-0009).

**Issue identity across runs:**

- Each issue has a stable `id` (e.g., `I-0042`) within the feature-slug namespace.
- Re-entering the feature after closure does not reset IDs. The next issue opened in Run 2 is `I-0043` (continuing the sequence), not `I-0001`.
- This means: when a critique in Run 2 surfaces something the orchestrator wants to verify wasn't already addressed, it can search the ledger by content similarity (against issue `origin.evidence` text) and either reopen an existing issue or open a new one.

**Reopening verified issues:**

- A critique in Run N can transition a verified issue back to `open` (state: `reopened`).
- The transition entry MUST include `reopened_reason` with evidence of re-emergence.
- The next triage gate explicitly surfaces reopened issues to the user with the full prior resolution history visible.

**Pattern surfacing without auto-curation:**

- When a critique produces a new issue with `origin.evidence` text similar (>0.7 cosine) to a verified-or-dismissed issue from the *same* feature's ledger OR a pattern entry in `cross-feature-patterns.md`, the new issue includes a `similar_to` field listing the references.
- The triage gate surfaces this so the human can decide: is this a recurrence (reopen the old) or a new instance of a known pattern (open fresh, mark as instance of pattern)?
- No automatic action taken on similarity alone.

## Consequences

**Positive:**

- Resume/re-entry semantics preserve verified-issue history. Reduces step repetition (the highest-frequency multi-agent failure mode at 15.7%).
- Cross-feature patterns remain visible without polluting per-feature critique context.
- Human triage retains agency. Pipeline surfaces signal; humans decide.
- The feature-slug namespacing means project-level operations are simple (each feature is a self-contained subtree under `working/feature/`).
- `cross-feature-patterns.md` is a discoverable, editable artifact — users can add patterns themselves between runs without coordinating with the pipeline.

**Negative:**

- Per-feature ledger files grow unbounded across many runs. Mitigation: archival policy. After a feature is `closed` and N days pass (suggested: 90), the orchestrator can archive the working directory to `working/feature/_archived/<feature-slug>-<archive-date>/`. Active features (most recent run within N days) stay in the live working tree.
- Cross-feature pattern detection depends on text-similarity heuristics, which have known false-positive and false-negative rates. The pipeline does NOT claim these are reliable; it surfaces candidates to human triage, which is the curation layer.
- Feature-slug collision is possible (two features with similar intent get different slugs but might point at the same underlying concern). Mitigation: synth-intent-clarifier checks against existing feature-slugs at Stage 1 and either reuses or differentiates. The clarifier asks the user if there's ambiguity ("This feature has a similar slug to 'add-healthz-endpoint' from a prior run. Same feature or different?").

**Neutral:**

- The decision is reversible if pain emerges in practice. The ledger format is JSON; migration to project-wide scope (if needed) is a one-time merge operation. Per-run scope (if needed) is a one-time partition.

## Alternatives considered

**Per-run scope.** Simpler but loses verified-issue continuity across resumes. The pipeline's resume semantics (blueprint v2 §2) already imply state persistence; per-run scope contradicts that. Rejected.

**Project-wide scope with relevance filtering at read time.** Each critique would read the full project ledger but filter by feature-relevance before passing to its analysis. Possible but the filtering heuristics are weaker than just keeping feature-scoped ledgers separate. Adds per-critique compute cost. Rejected.

**Per-feature with automatic cross-feature pattern detection.** Tempting but the false-positive cost is high. Premature automation. The cross-feature-patterns.md file with human curation is the v3 design; if it works well, a future ADR could promote some patterns to auto-detection.

**Append-only event log with derived-state views.** True event-sourcing approach. The current ledger IS append-only at the transition level (each transition is a new entry). Going fully event-sourced (every state read computes from event replay) is the next level of rigor but adds implementation complexity disproportionate to current need. Deferred.

## Evidence

Claims grounding this decision:

- C-R2-0024: MAST FM-1.3 step repetition at 15.7% — highest single-mode failure rate. This decision is the strongest defense against the meta-level form of this failure (the system repeating work across runs).
- C-R2-0017: external memory should be source of truth for durable facts; compaction summary is navigation, not record. The ledger IS the external memory for issue state.
- C-R2-0029: standard defect lifecycle (Jira pattern) establishes the state machine the ledger encodes.
- C-R2-0026: agent drift over extended interactions includes coordination drift; per-feature continuity reduces this by giving downstream runs explicit prior state.

User decision: per-Q3 clarification, per-feature scope with cross-feature pattern recognition is the chosen design. This ADR documents the architectural commitment.

## Substrate registry version

v1.3 (2026-05-12)

## Cross-stage supersession marker

`cross_stage_supersession: false` — new architectural decision, not superseding any prior stage's commitment.
