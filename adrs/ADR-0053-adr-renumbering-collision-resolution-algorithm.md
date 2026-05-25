---
id: ADR-0053
version: 1.0.1
status: Accepted
generated: 2026-05-24
generated_by: design-composer
revised: 2026-05-25
revised_after: architecture-audit-r1
revised_by: design-composer
supersedes: []
adrs_inherited: [ADR-0019, ADR-0036, ADR-0005]
applies_to:
  - adr-placement-mechanism-repair-r1
  - working/feature/issue-capture-mechanism-r1/adrs/ADR-0044-per-issue-folder-model.md (renumber source)
  - working/feature/issue-capture-mechanism-r1/adrs/ADR-0045-three-doctypes-preserved.md (renumber source)
  - canonical adrs/ (renumber target)
  - future numbering-collision incidents in the pipeline
template_format: per KB-documentation-criteria ADR template v1.0
change_summary: >-
  Establishes the canonical algorithm for resolving ADR-NNNN numbering collisions
  surfaced by canonical/feature-scoped, archive/canonical, or any other dual-source
  ADR-ID overlap. Defines the post-consolidation max-ID+1 monotonicity rule (with
  v1.0.1 baseline clarification: the algorithm's baseline EXCLUDES ADRs authored
  by this feature's own design-composer run, so the renumber targets resolve to
  the pre-this-feature canonical max-ID + 1), the provenance-frontmatter convention
  (original_id) preserving the source identity, and the prerequisite-phase ordering
  (renumber-after-archive-consolidation) that makes the algorithm deterministic.
  Resolves Q-CC-1 from the adr-placement-mechanism-repair-r1 Blueprint. v1.0.1
  resolves AA-006 (self-referential ordering bug surfaced by architecture-audit-r1).
---

# ADR-0053: ADR-NNNN numbering-collision resolution algorithm and provenance-frontmatter convention

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

Accepted — 2026-05-24 (authored during Design Composition of `adr-placement-mechanism-repair-r1`).

## Context

ADR-0019 (naming convention) establishes monotonic ADR-NNNN identifiers project-wide. ADR-0036 (single-location placement) requires a single canonical home at `adrs/`. In practice, the prior dual-location convention (now retired) plus the legacy `adrs-migrated/` archive produced cases where two distinct decisions accidentally carry the same numeric ID:

- **Discovery IN-002** for `adr-placement-mechanism-repair-r1` confirmed two such collisions: canonical `ADR-0044-flatten-execution-dispatch-hierarchy` (different decision) vs feature-scoped `ADR-0044-per-issue-folder-model` (different decision); same shape for ADR-0045 (canonical `subagent-agent-tool-grant-prohibition` vs feature-scoped `three-doctypes-preserved`).
- **Discovery IN-004** confirmed eight archive/canonical collisions for IDs 0011–0018 where ADR-0055 (the consolidation policy) prescribes archive-wins archival; those are not new IDs, but their resolution shifts the post-consolidation next-available-ID computation.

The PRD's FR-8b framing ("pick canonical body, archive rejected body") is structurally inapplicable to numbering collisions — there is no rejected body to archive; both decisions remain valid; one must move to a new ID.

The decision space has three options (see Options Considered). The recommended option (post-consolidation max-ID+1) requires sequencing the renumber phase after the legacy-archive consolidation phase so the next-available ID is computed deterministically. Without an explicit algorithm + provenance convention, future contributors encountering a similar collision will re-derive ad-hoc and the provenance chain (which feature originally introduced the ADR under its original ID) will be lost.

## Decision

When two distinct ADRs share a numeric ID due to a discovery surfaced during pipeline consolidation, the **feature-scoped** (or non-canonical-source) ADR shall be renumbered to the next-available canonical ID computed AFTER all consolidation phases for the affected ID space have completed. The renumbered ADR shall carry an `original_id: ADR-NNNN` frontmatter field preserving the source identity, and all in-repository references shall be updated via the cross-reference sweep mechanism.

## Decision Details

| Item | Content |
|---|---|
| Decision | Renumber the feature-scoped (non-canonical-source) ADR to `max(canonical_ids that pre-existed this feature's design-composer run) + 1` AFTER all consolidation phases for the affected ID space have completed; preserve provenance via `original_id` frontmatter. The baseline EXCLUDES ADRs authored by this feature's design-composer (which carry their own monotonic-next-ID assignment via the same algorithm applied at design-composer authoring time). |
| Why now | The `adr-placement-mechanism-repair-r1` feature has two live collisions (ADR-0044, ADR-0045) requiring deterministic resolution. Without a canonical algorithm, every future collision re-litigates the question. |
| Why this | Monotonicity (ADR-0019) plus deterministic ordering plus auditable provenance. Alternative algorithms either break monotonicity (offset-with-room) or risk re-collision (immediate-renumber-before-consolidation). The "pre-this-feature baseline" refinement (v1.0.1) resolves the self-referential ordering bug where a literal post-consolidation max-ID would include the design-composer's own newly-authored ADRs and shift renumber targets forward each run. |
| Known unknowns | (1) Whether the `original_id` frontmatter field is honored by any current frontmatter validator (it is not). (2) Whether future archive consolidations expose more than 2 simultaneous collisions, complicating the ordering proof. (3) Whether a future feature authoring more than ~5 ADRs simultaneously could compress the bootstrap window such that the design-composer's intra-run authoring sequence becomes order-sensitive. Mitigation: each design-composer run is single-threaded; intra-run authoring order is deterministic. |
| Kill criteria | If a renumbering operation produces a re-collision (next-available ID is already claimed by another concurrent phase), the algorithm is broken; halt and re-design. To date, the algorithm has been applied once (this feature) with two collisions and yields ADR-0051 + ADR-0052 deterministically against the pre-this-feature baseline (0050). |

## Rationale

The post-consolidation max-ID+1 rule is preferred over immediate-renumber because the legacy-archive consolidation (FR-8d in `adr-placement-mechanism-repair-r1`) shifts the canonical ID space: even though IDs 0011–0018 already exist in canonical, the archive-wins policy (ADR-0055) replaces those bodies and does not add new IDs. The actual next-available-ID for the renumbered feature-scoped ADRs depends on the highest canonical ID *after* consolidation completes. For this feature, canonical's pre-consolidation max-ID is 0045 (with ADR-0046–0050 landing via FR-8c relocation), so the renumber targets resolve to ADR-0051 (formerly feature-scoped ADR-0044) and ADR-0052 (formerly feature-scoped ADR-0045).

The provenance frontmatter (`original_id: ADR-0044`) preserves the originating-feature reference chain. Without it, a future contributor reading the renumbered ADR-0051 cannot trace back to the `issue-capture-mechanism-r1` feature's prose references to "ADR-0044" without resorting to git log archaeology.

The algorithm honors ADR-0019 (monotonic naming) by always assigning the next-available canonical ID, never an offset or reserved-range entry. It honors ADR-0036 (single-location) by ensuring the renumbered ADR lands at canonical `adrs/` only. It honors ADR-0005 (supersession discipline) by NOT treating the renumber as a supersession — both ADRs continue to apply; the renumber is purely a naming reconciliation.

## Options Considered

### Option A: Renumber immediately to next-available IDs (before consolidation)

**Pros:** Phase 2 can run in parallel; no serial dependency.

**Cons:** Risks re-collision if the consolidation phase introduces additional canonical IDs at the chosen offsets. The ADR-0044/0045 collision in `adr-placement-mechanism-repair-r1` co-occurs with FR-8c relocations of ADR-0046–0050 to canonical; immediate renumber would have to reserve 0051/0052 before knowing whether the relocation conflicts with anything.

### Option B: Renumber with a higher offset (e.g., ADR-0060, ADR-0061) to leave room

**Pros:** Eliminates near-term collision risk.

**Cons:** Breaks ADR-0019 monotonicity. Creates ID gaps that future authors must understand. Establishes a precedent that any contentious renumber gets an arbitrary high number, eroding the monotonic-ID invariant.

### Option C (Selected): Compute next-available number post-consolidation; honor monotonicity

**Pros:** Deterministic (max-ID+1 is unambiguous after consolidation settles). Honors ADR-0019. Auditable (the algorithm can be re-applied to any future collision). Provenance frontmatter preserves the source-feature reference chain.

**Cons:** Serializes the renumber phase after the consolidation phase (Phase 2b-renumber depends on Phase 2d completion). Adds a single dependency edge to the Plan's phase graph.

## Consequences

### Positive Consequences

- Future numbering-collision incidents resolve deterministically without re-litigation.
- Provenance chain via `original_id` keeps prose references in originating features traceable.
- Monotonic naming (ADR-0019) preserved.
- Single algorithm applies to canonical/feature-scoped, archive/canonical, and any future dual-source ID overlap.

### Negative Consequences

- Phase 2b-renumber serially depends on Phase 2d (archive consolidation), adding an edge to the Plan's phase graph.
- Frontmatter validators that don't recognize `original_id` will treat it as an unknown field (informational, not error); future validator work should explicitly permit it.

### Neutral Consequences

- The cross-reference sweep (FR-9) must update references to the renumbered IDs along with the path-only edits; one additional class of edit per renumbered ADR.

## Architecture Impact

1. **Components that change**: `working/feature/issue-capture-mechanism-r1/adrs/ADR-0044-per-issue-folder-model.md` (renames to `adrs/ADR-0051-per-issue-folder-model.md`); `working/feature/issue-capture-mechanism-r1/adrs/ADR-0045-three-doctypes-preserved.md` (renames to `adrs/ADR-0052-three-doctypes-preserved.md`). Both get `original_id` frontmatter added.
2. **New dependencies introduced**: None. The algorithm reuses existing `git mv` (per NFR-5) and the cross-reference sweep mechanism (per FR-9).
3. **Architectural constraints added or removed**: Adds the constraint that any future renumber operation must be sequenced after consolidation of the affected ID space. Adds the convention that `original_id` is a recognized provenance frontmatter field.
4. **Layers affected**: Claude Code / Project Filesystem only. No other layer is touched.

## Implementation Guidance

- **Algorithm** (v1.0.1 clarified baseline): Compute `next_id = max({int(id) for id in canonical_adrs_ids that pre-existed this feature's design-composer run}) + 1` AFTER all consolidation phases for the affected ID space have completed. The baseline EXCLUDES ADRs authored by this feature's design-composer (those are assigned via the SAME max+1 algorithm applied at design-composer authoring time, pre-renumber, in deterministic intra-run order). Assign renumbered ADRs in deterministic order (smallest source ID first, then ASCII order on slug).

  **Worked example (this feature, `adr-placement-mechanism-repair-r1`)**:
  - Pre-feature canonical max-ID = **0045** (state before this feature's design-composer ran).
  - FR-8c relocations land canonical IDs **0046–0050** (from `working/feature/issue-capture-mechanism-r1/adrs/`).
  - The 3 ADRs authored during Design Composition of THIS feature (**0053, 0054, 0055**) are assigned via the SAME max+1 algorithm at design-composer authoring time (pre-renumber); these ADRs are NOT part of the renumber baseline.
  - Renumber baseline = `max(pre-this-feature canonical ID space ∪ FR-8c relocations) = max(0045, 0050) = 0050`.
  - Renumber targets = **0051** (formerly feature ADR-0044) and **0052** (formerly feature ADR-0045).
  - The renumber phase does NOT re-derive against ADR-0053/0054/0055 even though they sit at canonical at renumber time.

- **Provenance frontmatter**: Add `original_id: ADR-NNNN` to the renumbered ADR's frontmatter. The field value is the source ID before renumbering.
- **Cross-reference sweep**: The cross-reference sweep mechanism (per FR-9 in this feature) must include the renumbered IDs in its update pass. Both the path-form references (e.g., `working/feature/issue-capture-mechanism-r1/adrs/ADR-0044-*`) and the bare-ID references (e.g., prose "see ADR-0044") MUST be updated. The bare-ID update is a deliberate exception to FR-9's path-only rule because the ID itself has moved; without the bare-ID update, prose references to "ADR-0044" in issue-capture-mechanism-r1's shipped Blueprint silently mean a different decision than they did at authoring time. Per the v2.0 user binding decision on AA-011, the full 368-occurrence bare-ID sweep across the repo is in-scope for this feature's FR-9 (ADR-0044: 223 mentions; ADR-0045: 145 mentions).
- **Validator interaction**: The FR-10 validator (per ADR-0054) scans for `ADR-*.md` placement. The renumbered ADR satisfies the validator by landing at canonical `adrs/`. The provenance frontmatter is informational only; the validator does not consume it.

Procedures (which file is renamed first, which commit boundary applies) belong to the Plan, not this ADR.

## Revision History

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-05-24 | design-composer | Initial authoring during Design Composition of `adr-placement-mechanism-repair-r1`. |
| 1.0.1 | 2026-05-25 | design-composer | Frontmatter-stable amendment per ADR-0005, in response to architecture-audit-r1 finding AA-006 (self-referential ordering bug). Clarified the algorithm's baseline as "max of canonical IDs that pre-existed this feature's design-composer run" — EXCLUDING ADRs authored by the same design-composer run. Added worked example demonstrating the bootstrap-self-reference case. Added Known Unknown #3 (intra-run authoring order). No supersession; Decision text unchanged in spirit (Option C still selected); Decision Details rows clarified; Implementation Guidance expanded. |

## Related Information

- Related ADRs: ADR-0019 (naming convention — monotonicity preserved), ADR-0036 (single-location — destination is canonical), ADR-0005 (supersession — this is NOT supersession), ADR-0054 (three-surface validator — the destination is validator-clean), ADR-0055 (archive-wins consolidation — the dependency edge originates here).
- Referenced specs / docs: `working/feature/adr-placement-mechanism-repair-r1/blueprint-v1.md` (this feature's Blueprint), `working/feature/adr-placement-mechanism-repair-r1/codebase-analysis.json` IN-002 (collision discovery), Synthesis D1.
- Issues / PRs: `Issues/adr-placement-rootcause/proposal.md` (originating proposal; renumber not in original scope but became binding under v2.0.0 directive).
- Related KBs: `KB-documentation-criteria` (ADR template), `KB-cc-design` (numbering-as-CC-convention).
