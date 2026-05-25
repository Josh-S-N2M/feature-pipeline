---
id: ADR-0048
version: 1.0.0
status: Proposed
generated: 2026-05-23
generated_by: design-composer
supersedes: []
adrs_inherited: []
applies_to:
  - issue-capture-mechanism-r1
  - intake-intent-clarifier sub-agent (Stage 1 of the Feature Pipeline)
  - intent-clarification-template.md
  - recipe-feature-pipeline/SKILL.md
  - any future pipeline run seeded by an Issues/<topic>/proposal.md
template_format: per KB-documentation-criteria ADR template v1.0
change_summary: >-
  When recipe-feature-pipeline is invoked with --raw-request pointing at an
  Issues/<topic>/proposal.md file (doc_type:issue-proposal), the pipeline's
  Stage 1 (intake-intent-clarifier) treats the proposal body as authoritative
  prior context — eliciting ONLY the fields the proposal lacks. The handoff
  uses the existing --raw-request + prior_context mechanism. NO new pipeline
  stage is introduced. NO gate is bypassed. The proposal path is cited
  verbatim in the run's intent-clarification.md Source section.
---

# ADR-0048: Prior-context handoff via existing `--raw-request` mechanism

## Contents

- [x] Status
- [x] Context
- [x] Decision
- [x] Decision Details
- [x] Rationale
- [x] Options Considered
- [x] Consequences
- [x] Architecture Impact
- [x] Implementation Guidance
- [x] Related Information

## Status

Proposed — 2026-05-23 (issue-capture-mechanism-r1; pending Gate 4 user ratification). Validating example: THIS pipeline run (issue-capture-mechanism-r1) is itself seeded by `Issues/issue-capture-mechanism/proposal.md`; the design pattern is in use during its own design.

## Context

The outside-pipeline issue-capture mechanism produces `Issues/<topic>/proposal.md` files that are explicit candidates for future feature-pipeline runs. The frontmatter field `proposes_future_feature:` (advisory per ADR-0050 / D-06) carries a suggested slug; the body of the proposal contains substantive design content (FRs, ACs, layer scope, scope class, success criteria) that — if the proposal is well-formed — should not be re-elicited when the feature run actually starts.

Without a handoff mechanism, the pipeline would re-elicit decisions already made in the proposal at Stage 1 (`intake-intent-clarifier`). This is:

- **Costly for the user.** The proposal-author already decided the scope, layer breakdown, and key constraints; re-litigating these at Stage 1 wastes the user's time.
- **Brittle.** Re-elicitation may diverge from the proposal in subtle ways (different layer disposition, different won't-have list); the proposal and the eventual intent-clarification.md drift apart, even though the proposal IS the authoritative prior decision.
- **Discoverability-broken.** A future reader of the intent-clarification.md cannot trace back to the proposal that motivated the run; the Source section is generic text.

Three handoff designs were considered:

1. **A new pipeline stage** between recipe invocation and Stage 1 that ingests the proposal. Rejected: introduces new infrastructure for a one-line behavioral change.
2. **A gate bypass** at Stage 1 that skips elicitation when a proposal is supplied. Rejected: violates PRD §Constraints "Must preserve all 6 mandatory human gates of the feature pipeline; no bypass."
3. **Use the existing `--raw-request` + `prior_context` mechanism.** The recipe-feature-pipeline orchestrator already accepts `--raw-request <text-or-path>` (line 14) and already passes `prior_context` through to intake-intent-clarifier (line 145, with default "empty on fresh run"). The intent-clarifier already has an optional `prior_context` parameter (line 28). The wire is in place. The required edit is purely body-level: a ~15-line "Phase 0 — Detect proposal seed" branch in the agent's procedure section.

Option 3 is the chosen design. Codebase-analysis findings F-013 (signature already supports it) and F-014 (template Source section structurally ready) confirm the wire is in place. The proposal seed for THIS feature run already uses the pattern — the proposal at `Issues/issue-capture-mechanism/proposal.md` was supplied as `--raw-request` and the run's `intent-clarification.md` cites the proposal path verbatim in Source. The dogfood validation is real-time.

The PRD §FR-10, FR-11, FR-12 codify the handoff. This ADR makes the architectural commitment explicit and locks in the "no new stage, no gate bypass" constraint.

## Decision

1. **Use the existing `--raw-request` + `prior_context` mechanism.** When `recipe-feature-pipeline <slug> --raw-request <path>` is invoked and the file at `<path>` carries `doc_type: issue-proposal` in its frontmatter, intake-intent-clarifier detects the proposal seed in a new Phase 0 step and treats the proposal body as authoritative prior context.
2. **No new pipeline stage.** The handoff is a procedure-section edit inside intake-intent-clarifier (~15 lines). No new agent, no new sub-stage, no new gate.
3. **No gate bypass.** All 6 mandatory human gates remain. Stage 1's Gate 1 (user reviews intent-clarification.md) still fires — the user has the final word on the elicited fields, regardless of how much came from the proposal vs. interactive elicitation.
4. **Proposal-supplied fields are not re-elicited.** When the proposal supplies an FR, an AC, a layer scope row, a scope class, or any other Stage-1 required field, intake-intent-clarifier carries that field forward without asking the user again. Only missing fields are elicited.
5. **Source section cites the proposal verbatim.** The intent-clarification.md `Source` section includes the verbatim proposal path (e.g., `Source: Issues/<topic>/proposal.md (proposal-seeded run)`) when a proposal seeds the run. The intent-clarification-template.md gains a ~5-line addition documenting this.
6. **Recipe SKILL.md gains one bullet** documenting the proposal-seed invocation pattern (FR-12b, ~5 lines under the existing `--raw-request` description). No other recipe edit.
7. **Phase 0 is non-destructive on miss.** When `raw_request` is not a path, or the file at the path lacks `doc_type: issue-proposal` frontmatter, Phase 0 falls through to existing Phase 1 (interactive elicitation) unchanged. The handoff is opt-in by file content, not by flag.

## Decision Details

| Item | Content |
|---|---|
| Decision | Proposal-as-prior-context handoff via existing --raw-request + prior_context; no new stage, no gate bypass; procedure-section edit only. |
| Why now | This run is itself seeded by a proposal; the handoff pattern is in active use during the run's design; without an ADR, the pattern remains implicit in the intake-intent-clarifier body and the template's Source-section guidance. |
| Why this | Existing mechanism (--raw-request + prior_context) accommodates the new behavior without parameter changes or new infrastructure; the constraint "no new pipeline stage, no gate bypass" is honored; signature-level edits to the orchestrator or intake agent are explicitly rejected as exceeding FR-11/FR-12 scope. |
| Known unknowns | (a) If a future proposal has gaps the checklist doesn't anticipate (a wholly new section), Phase 0 may silently miss them. Mitigation: Stage 1's existing Gate 1 confirmation surface (user reviews intent-clarification before approval) catches this. (b) Whether the checklist itself drifts from the canonical Stage-1 required-fields list over time. Mitigation: the checklist lives in intent-clarification-template.md (per ADR-0049's templates-here-discipline-elsewhere split), not in the agent body — it stays in sync with the template by construction. |
| Kill criteria | If real-world use shows that proposal-seeded runs systematically miss critical Stage-1 fields (Gate 1 catches the gaps but at unacceptable user-time cost), revisit. If the existing prior_context mechanism is ever superseded by a stricter handoff (e.g., a typed proposal-import API), this ADR is superseded by the new mechanism's ADR. |

## Rationale

Three load-bearing reasons the existing-mechanism reuse wins over new infrastructure:

1. **The wire is already in place.** F-013 and F-014 confirm that the recipe orchestrator, intake-intent-clarifier, and intent-clarification-template all accommodate the proposal-seed pattern with no new parameters. A new pipeline stage would re-litigate decisions already made (the wire), introduce new failure modes (a new stage can fail), and create coordination overhead (the recipe + 28+ agents would need to know about it).

2. **No gate bypass preserves the safety property.** The 6 mandatory human gates are the user's primary control surface over pipeline correctness. Bypassing Gate 1 when a proposal is supplied would force the user to trust the proposal verbatim — but proposals are authored at one point in time and the user's view at run time may differ. Keeping Gate 1 active means the user reviews the elicited fields (including those carried from the proposal) before pipeline progress.

3. **The dogfood test is in flight.** THIS pipeline run (issue-capture-mechanism-r1) was seeded by `Issues/issue-capture-mechanism/proposal.md`. The proposal supplied ~80% of the Stage-1 elicitation; the intake-intent-clarifier asked 7 clarifying questions for the remaining 20%; Gate 1 closed cleanly. The pattern is validated by the very feature run that designs it — a stronger empirical signal is not available in-project.

The decision honors KB-cc-design Principle 1 (skill-localized knowledge — the Phase 0 procedure lives in the intake-intent-clarifier body; the field checklist lives in intent-clarification-template.md; the orchestrator-level pattern documentation lives in recipe-feature-pipeline/SKILL.md). It also honors KB-cc-design Principle 5 (one source of truth — the checklist is in the template, not duplicated in the agent body).

## Options Considered

### Option 1: New pipeline stage between recipe invocation and Stage 1

A "proposal-ingest" stage that reads the proposal, transforms it into elicited fields, and hands the result to Stage 1.

**Pros:** Explicit transformation; auditable as a stage; testable in isolation.

**Cons:** New stage means new infrastructure (recipe wiring, new agent, new gate or non-gate decision); a new agent means new failure modes; coordination with 28+ existing agents; over-engineering for a behavioral change that fits in 15 lines of procedure text.

### Option 2: Gate bypass at Stage 1 when proposal supplied

Recipe detects the proposal, sets a flag, and Stage 1 skips Gate 1 if the flag is set.

**Pros:** Lowest user friction (user doesn't see Gate 1 again on a proposal-seeded run).

**Cons:** Violates PRD §Constraints "Must preserve all 6 mandatory human gates of the feature pipeline; no bypass." The user's gate-1 review is the safety surface against proposal drift (the proposal was authored at one time; the user at run time may want to revise). Rejected on safety grounds.

### Option 3 (Selected): Use existing `--raw-request` + `prior_context` mechanism; procedure-section edit only

intake-intent-clarifier Phase 0 detects the proposal seed; treats the body as prior context; elicits only missing fields. No new stage, no gate bypass.

**Pros:** Existing wire (no new infrastructure); Gate 1 preserved; checklist lives in template (single source of truth); dogfood-validated by this very run; ~15-line edit fits the scope.

**Cons:** Phase 0 is a body-text edit; readers of the agent must read the new branch to understand the behavior; if the checklist drifts from the canonical Stage-1 required-fields list, Phase 0 silently misses fields. Mitigation: template-bound checklist + Gate 1's user review catches gaps.

### Option 4: Signature-level edit — new `proposal_path` parameter on intake-intent-clarifier

Add a typed parameter; orchestrator detects the proposal and passes it explicitly.

**Pros:** Type-safer than relying on `--raw-request` + frontmatter detection.

**Cons:** Exceeds FR-11/FR-12 scope (which is procedure-only); requires orchestrator-side edit beyond the one-bullet FR-12b allows; F-013 confirms the existing `prior_context` parameter already accommodates the new behavior. Rejected as over-scope.

## Consequences

### Positive Consequences

- Proposal-seeded runs experience low-friction Stage 1: ~80% elicitation comes from the proposal; only missing fields are asked.
- The proposal-to-feature handoff is traceable via the intent-clarification.md `Source` section.
- The 6 mandatory human gates are preserved; safety properties of the pipeline are unaffected.
- Future pipeline runs can adopt the same pattern with no additional infrastructure — the wire is in place.
- Dogfood validation is real (this run uses the pattern during its own design).

### Negative Consequences

- Phase 0 is a body-text edit; a reader of intake-intent-clarifier must read the branch to understand the behavior. Mitigation: the branch is explicitly documented and the validating example (this run) is named in the body.
- If a proposal has substantive Stage-1 gaps the checklist doesn't anticipate, Phase 0 silently misses them. Mitigation: Gate 1's user review catches gaps; the user retains final authority.
- The handoff depends on `doc_type: issue-proposal` in the proposal frontmatter — a proposal mis-typed (e.g., `doc_type: proposal` from the pre-migration files) would not trigger Phase 0. Mitigation: FR-8 migration back-fills the canonical doc_type values; the four pre-migration proposals all gain `doc_type: issue-proposal` post-migration.

### Neutral Consequences

- The recipe-feature-pipeline/SKILL.md gains one bullet documenting the pattern. No other recipe edit.
- The intent-clarification-template.md gains a ~5-line addition to the Source-section guidance. No structural change.
- The orchestrator's `--raw-request` invocation contract is unchanged.

## Architecture Impact

1. **Layers affected.** Claude Code only.
2. **Components that change.**
   - `.claude/agents/intake-intent-clarifier.md` — ~15-line Phase 0 addition (procedure-section edit; FR-11).
   - `.claude/skills/KB-documentation-criteria/references/templates/intent-clarification-template.md` — ~5-line Source-section guidance addition (FR-12a).
   - `.claude/skills/recipe-feature-pipeline/SKILL.md` — one-bullet additive edit under existing `--raw-request` documentation (FR-12b).
3. **New dependencies introduced.** None.
4. **Architectural constraints added.** Any future change to intake-intent-clarifier's procedure-section MUST preserve the Phase 0 branch (or supersede this ADR explicitly with a new handoff mechanism). The `--raw-request` + `prior_context` wire is now load-bearing for the proposal-seed pattern.

## Implementation Guidance

**For the intake-intent-clarifier body (CC layer).** Phase 0 inserts BEFORE existing Phase 1. The branch:

```
If raw_request is a path (not free-form text):
  Read the file; parse frontmatter.
  If frontmatter contains `doc_type: issue-proposal`:
    Treat the body as authoritative prior context.
    Cite the path verbatim in intent-clarification.md Source section.
    Iterate through the Stage-1 required-fields checklist (lives in
      intent-clarification-template.md).
    Elicit ONLY the fields the proposal lacks.
    Proceed to Phase 1 with proposal-supplied content as the elicited
      substrate.
If raw_request is free-form text OR the file at the path lacks
  doc_type: issue-proposal: proceed to existing Phase 1 unchanged.
```

**For the intent-clarification-template.md (CC layer template).** Append to the existing Source section:

> **When `--raw-request` is a path to a file with `doc_type: issue-proposal`:** cite the proposal path verbatim in this section (e.g., `Source: Issues/<topic>/proposal.md (proposal-seeded run)`). The proposal body itself is authoritative prior context for the elicited fields — see intake-intent-clarifier's Phase 0.

**For the recipe-feature-pipeline/SKILL.md (CC layer skill).** Append one bullet under the existing `--raw-request` description:

> **Proposal-seed pattern:** when `<text-or-path>` points to an `Issues/<topic>/proposal.md` file with `doc_type: issue-proposal` in its frontmatter, intake-intent-clarifier detects this in Phase 0 and treats the proposal body as authoritative prior context (no re-elicitation of already-decided design). This pattern produces no new pipeline stage and bypasses no gate.

**Required-fields checklist location.** The checklist (FRs, NFRs, EARS ACs, exhaustive 9-layer scope, stakeholder table, scope class per ADR-0023, success-criteria posture) lives in the intent-clarification-template.md, NOT in the intake-intent-clarifier body. The agent body REFERENCES the template's checklist by reading it. This keeps the checklist canonical and prevents drift.

No procedural detail beyond the above — exact wording of the Phase 0 branch is in Blueprint §Mechanism Designs D-14.

## Related Information

- Related ADRs:
  - ADR-0051 (per-issue folder model — proposal paths are `Issues/<topic>/proposal.md`)
  - ADR-0052 (three doctypes preserved — only `issue-proposal` triggers Phase 0)
  - ADR-0047 (three-layer enforcement — independent of this handoff)
  - ADR-0050 (5-state lifecycle — proposals have `proposes_future_feature:` advisory field; D-06 advisory posture)
- Referenced specs / docs: PRD §FR-10 (source-citation discipline); PRD §FR-11 (proposal-as-prior-context detection); PRD §FR-12 (template + recipe edits); PRD §Constraints "Must preserve all 6 mandatory human gates; no bypass"; Blueprint §Mechanism Designs D-14; codebase-analysis F-013 (intake-intent-clarifier already supports prior_context); F-014 (template Source structurally ready); the dogfood example: this run's `intent-clarification.md` at `working/feature/issue-capture-mechanism-r1/intent-clarification.md`.
- Issues / PRs: `Issues/issue-capture-mechanism/proposal.md` (the seed proposal that bootstrapped this very run; lines 138-142 already anticipate the post-migration layout this ADR depends on).
- Related KBs: KB-cc-design (Principles 1, 5); KB-documentation-criteria (intent-clarification-template.md).
