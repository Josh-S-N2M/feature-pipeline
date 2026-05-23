---
id: ADR-0036
title: Single-location ADR placement convention — adrs/ project-wide registry only
status: accepted
date: 2026-05-22
accepted: 2026-05-22
deciders: [user, claude (orchestrator)]
supersedes: []
superseded_by: []
related: [ADR-0005, ADR-0011, ADR-0023, ADR-0027, ADR-0031, ADR-0032]
authored_in_feature: execution-pipeline-design-r1
pairs_synthesis_decisions: []
subsumes: ["deliverable-archive-spec.md §ADR placement convention (pre-amendment dual-location language)"]
change_summary: |
  Amends the deliverable-archive-spec to declare a single canonical location
  for Architectural Decision Records: `adrs/<ADR-NNNN-title>.md` at the
  project root. Eliminates the prior dual-location convention that required a
  duplicate copy at `working/feature/<slug>/adrs/`. The feature archive
  references ADRs by path; readers traverse to `adrs/` for the canonical
  source.
---

# ADR-0036: Single-location ADR placement convention — `adrs/` project-wide registry only

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

Accepted — 2026-05-22.

Ratified at Gate-6 Final Approval of the `execution-pipeline-design-r1` feature run. Effective immediately for new feature runs; existing archives that contain `working/feature/<slug>/adrs/` directories are not retroactively cleaned (the dual-location remained for those archives because the ADRs were authored under the pre-amendment spec).

## Context

The deliverable-archive-spec.md (`.claude/skills/KB-documentation-criteria/references/deliverable-archive-spec.md`, lines 136-143 pre-amendment) required ADRs to live in two locations: the project-wide registry at `adrs/ADR-NNNN-<title>.md` AND a feature-scoped copy at `working/feature/<slug>/adrs/ADR-NNNN-<slug>.md`. The rationale given was that the feature archive should be self-contained without forcing readers to traverse the project registry.

This convention surfaced as a Gate-6 BLOCKER (packager-report I-DR-DA-002) during the `execution-pipeline-design-r1` feature run: all four new ADRs (ADR-0032, ADR-0033, ADR-0034, ADR-0035) were authored in `adrs/` only, with no feature-scoped copies. The packager flagged the deliverable archive as non-conforming.

Three remediation options were considered:

1. **Copy the 4 ADRs into `working/feature/execution-pipeline-design-r1/adrs/`** — closes the immediate BLOCKER but accepts the duplication cost going forward.
2. **Symlink instead of copy** — avoids drift but introduces tooling-compatibility concerns (not all readers/validators follow symlinks).
3. **Amend the spec to declare single-location canonical** — addresses root cause; eliminates the duplication-and-drift cycle going forward.

The user selected option 3 at the Gate-6 disposition. This ADR ratifies that decision.

The pre-amendment rationale ("feature archive should be self-contained") is plausible but the cost-benefit analysis at scale favors single-location:

- ADRs in the project-wide registry are NEVER feature-scoped semantically — they reflect cross-feature architectural decisions. Per ADR-0011's KB-structure conventions, cross-feature artifacts live at project root, not under `working/feature/<slug>/`.
- Cross-feature traversal is the normal access pattern for ADRs (a reader on feature B routinely consults ADRs authored under feature A); the "self-contained archive" framing fights that pattern.
- Duplication creates drift risk: when an ADR is revised in-place (per ADR-0005 proposed-status exception, as ADR-0033 and ADR-0034 were during this feature run), the dual-location convention requires keeping the duplicate in sync — easy to forget; deliverable-archive validator does not currently diff the two copies.
- The "bulk-copy via cp" pattern documented at deliverable-archive-spec.md line 157 is a manual step easily skipped (as this feature run demonstrated — the cp was never run; the BLOCKER surfaced only at Gate-6).

The deliverable-archive validator can verify ADR references by reading the `adrs_authored` field of each Blueprint frontmatter and confirming each named ADR exists at `adrs/<ADR-NNNN-*>.md`. The feature-scoped copy adds no additional verification value.

## Decision

**Architectural Decision Records (ADRs) live in exactly one canonical location: the project-wide registry at `adrs/ADR-NNNN-<title>.md` at the repository root.** No feature-scoped duplicate is required, expected, or recommended.

The deliverable-archive-spec.md §"ADR placement convention" is amended to reflect this single-location convention. The spec's old dual-location language is preserved as historical context (lines superseded; see Implementation Guidance below).

When a feature run authors a new ADR:

1. Write the ADR once at `adrs/ADR-NNNN-<slug>.md` (next sequential N).
2. Reference the ADR by full path in feature artifacts (Blueprint, Plan, etc.).
3. Do NOT create `working/feature/<slug>/adrs/` directories or duplicate ADR files.

The deliverable-archive validator (per the amended spec) checks ADR presence only at the project-wide registry. The `adrs_authored` frontmatter field of each Blueprint enumerates which ADRs the feature authored; each named ADR must exist at `adrs/ADR-NNNN-*`.

## Decision Details

| Item | Content |
|---|---|
| Decision | ADRs live only at `adrs/ADR-NNNN-<title>.md`. No feature-scoped duplicate. |
| Why now | Surfaced as Gate-6 BLOCKER during execution-pipeline-design-r1; user-disposition selected root-cause amendment over in-place remediation. |
| Why this | Drift risk; cross-feature traversal is normal; "self-contained archive" framing fights ADR semantics. |
| Known unknowns | Whether any tool or skill outside `finalize-deliverable-packager` consumes the feature-scoped copy. Audit done at amendment time found none. |
| Kill criteria | If 3+ feature runs surface evidence that feature-scoped ADR copies are operationally needed (e.g., archive consumers can't traverse to project root), the convention is reversed. |

## Rationale

The deliverable-archive-spec's pre-amendment dual-location language asserted that the feature archive should be self-contained. This framing is plausible for some artifact types (an intent-clarification.md is genuinely feature-scoped; copying it to project root would be a category error), but ADRs are categorically different: they encode cross-feature architectural decisions, and consumers routinely reference ADRs from features they did not author. Forcing duplication contradicts the canonical-helper-home discipline ADR-0031 establishes for cross-cutting artifacts.

Drift is the operational cost. When ADR-0033 and ADR-0034 were revised in-place during this feature's cycle 1 and cycle 3 reconciliation, the spec required the duplicate to be re-synced. The duplicate was never created in the first place, so the drift never materialized — but in a steady-state world where the spec is honored, every in-place ADR revision would require a corresponding cp to the feature directory. That is a manual step easily missed; the deliverable-archive validator does not currently diff the two copies, so drift would not be detected by the validation tooling.

Single-location ADR placement aligns with:

- **ADR-0011 KB-structure conventions** (cross-feature artifacts at project root)
- **ADR-0031 canonical-helper-home discipline** (one location, well-known, well-named)
- **ADR-0005 append-only supersession** (the in-place edit exception for `proposed` status ADRs is simpler with a single file)

## Options Considered

**Option 1: Remediate in-place** — `cp adrs/ADR-003{2,3,4,5}*.md working/feature/execution-pipeline-design-r1/adrs/`. Closes the immediate BLOCKER but accepts the duplication-and-drift cycle going forward. Rejected per the analysis above.

**Option 2: Symlink** — `ln -s adrs/ADR-0032*.md working/feature/execution-pipeline-design-r1/adrs/ADR-0032-*.md`. Avoids drift but introduces tooling-compatibility concerns (Windows file systems, some Git operations, some validator implementations). Rejected as more complex than option 3 with no compensating benefit.

**Option 3 (Selected): Amend the spec to single-location** — addresses root cause. Eliminates the duplication-and-drift cycle going forward. Closes the immediate BLOCKER by changing the rule rather than complying with it. The amended spec is more honest about what ADRs are (cross-feature artifacts) and how they are accessed (by traversal to the project registry).

## Consequences

### Positive

- **One source of truth for every ADR.** No drift risk between locations.
- **Simpler authoring.** No bulk-copy step required after each ADR ratification.
- **Honest semantics.** ADRs are cross-feature artifacts; their single location reflects that.
- **Validator simplification.** The deliverable-archive validator checks one path per ADR, not two.
- **Removes a class of Gate-6 BLOCKER findings.** The dual-location BLOCKER cannot recur.

### Negative

- **Existing archives have feature-scoped copies that won't be cleaned.** Pre-ADR-0036 archives may still have `working/feature/<slug>/adrs/` directories. Those are not retroactively removed; they are inert historical artifacts.
- **Readers expecting self-contained archives must traverse to project root** to find ADRs. This is the normal pattern but represents a behavior change for any consumer who relied on the previous duplicate.

### Neutral

- The deliverable-archive-spec is amended (one section rewritten + one Pattern updated + cross-reference added).
- No existing ADRs are superseded by this convention change; they remain at `adrs/` as before.
- ADR-0032 (universal-required frontmatter fields) is unaffected; ADR doc_type still applies.

## Architecture Impact

### Files amended

- `.claude/skills/KB-documentation-criteria/references/deliverable-archive-spec.md` — §ADR placement convention rewritten; Pattern at the original line 157 rewritten; cross-reference to this ADR added.

### Files created

- `adrs/ADR-0036-single-location-adr-placement.md` (this file).

### Components unaffected

- All existing ADRs (ADR-0001..ADR-0035) remain unchanged at `adrs/`.
- `finalize-deliverable-packager` agent behavior unchanged at the code level; its operational rule changes via the spec amendment.
- `shared-document-reviewer` with `doc_type: DeliverableArchive` follows the amended spec.

### Blast radius

- Pre-amendment archives that contain `working/feature/<slug>/adrs/` directories: not retroactively cleaned. Inert.
- This feature run (`execution-pipeline-design-r1`): no feature-scoped copies needed; the BLOCKER (I-DR-DA-002 in packager-report) is closed by the spec amendment rather than by file creation.
- Future feature runs: do not author feature-scoped copies; reference ADRs by path.

## Implementation Guidance

### For authors writing new ADRs

1. Identify the next sequential ADR number by inspecting `ls adrs/ADR-*`.
2. Write the new ADR to `adrs/ADR-NNNN-<kebab-case-slug>.md` only.
3. Reference the ADR by full path in feature artifacts:
   - Blueprint `adrs_added_in_this_run` frontmatter: `- ADR-NNNN (<title>) [<status notes>]`
   - Blueprint body cross-references: `(per ADR-NNNN)` or `[ADR-NNNN](../../../adrs/ADR-NNNN-<slug>.md)`
   - Plan, Acceptance Tests, Phase Validators cross-references: same pattern.
4. Do NOT create `working/feature/<slug>/adrs/` directories.

### For the deliverable-archive validator

1. Read each Blueprint's `adrs_added_in_this_run` (or equivalent) frontmatter field.
2. For each ADR named, verify `adrs/ADR-NNNN-*.md` exists.
3. Do NOT check `working/feature/<slug>/adrs/`.
4. Pre-ADR-0036 archives that happen to have a `working/feature/<slug>/adrs/` directory: ignore. Do not flag presence or absence as a finding.

### For pre-amendment archives

No retroactive cleanup is required. Archives that contain `working/feature/<slug>/adrs/` directories may keep them as historical artifacts. The validator does not enforce removal.

### Cross-reference to amended spec text

The deliverable-archive-spec.md §"ADR placement convention" pre-amendment text is preserved via git history. The amendment changes the section to single-location language and updates the Pattern at the original line 157 ("Pattern: feature-scoped ADRs at both locations") to single-location language ("Pattern: ADRs at the project-wide registry only").

## Related Information

### Related ADRs

- **ADR-0005** (append-only supersession) — ADR in-place edit exception applies; ADR-0036 itself is `accepted` from authoring (not `proposed`-first) because it ratifies a Gate-6 disposition the user has already made.
- **ADR-0011** (KB-structure conventions) — Cross-feature artifacts at project root; this ADR extends the principle to ADRs.
- **ADR-0023** (scope classes) — Deliverable archive spec defines per-scope expected-artifact sets; this ADR amends the ADR placement portion of that spec.
- **ADR-0027** (cwd-repo-root precondition) — Ensures the relative path `adrs/` always resolves to the project-wide registry.
- **ADR-0031** (auditing-shared canonical-helper-home) — Pattern model: one canonical location for cross-cutting artifacts.
- **ADR-0032** (conventions canonicalization) — Pairs structurally; both amend project-wide conventions documented in the spec.

### Related files

- `.claude/skills/KB-documentation-criteria/references/deliverable-archive-spec.md` — amended.
- `working/feature/execution-pipeline-design-r1/packager-report.json` — finding I-DR-DA-002 closed by this ADR.

### Authoring context

This ADR was authored at Gate-6 Final Approval of the `execution-pipeline-design-r1` feature run, in direct response to the packager's BLOCKER finding. The user selected option 3 (amend spec) over options 1 (cp remediation) and 2 (symlink) at the disposition step. The amendment to the spec was applied in the same Gate-6 commit set.
