---
id: ADR-0055
version: 1.0.1
status: Accepted
generated: 2026-05-24
generated_by: design-composer
revised: 2026-05-25
revised_after: architecture-audit-r1
revised_by: design-composer
supersedes: []
adrs_inherited: [ADR-0005, ADR-0019, ADR-0036]
applies_to:
  - adr-placement-mechanism-repair-r1
  - adrs/ADR-0011 through ADR-0018 (the 8 archive/canonical collisions)
  - adrs-migrated/ (consolidation source; eliminated after Phase 2d)
  - adrs/superseded/ (archival destination for stale canonical bodies)
  - future archive-consolidation incidents
template_format: per KB-documentation-criteria ADR template v1.0
change_summary: >-
  Codifies the gate-binding decision (2026-05-24) that, when consolidating a
  legacy ADR archive into canonical adrs/, the archive body wins for cases
  where the archive carries a more current version than canonical. Defines
  the stale-canonical-body archival convention (adrs/superseded/<id>-pre-
  consolidation-canonical.md with provenance footer), the frontmatter
  provenance fields (superseded_by_consolidation, superseded_canonical_archived_to),
  and the deletion convention for pre-naming-convention / pre-template-migration
  variants AND the v1-superseded variant (Git history preserves them). Resolves
  OI-2 from the PRD and Discovery IN-004's 8 collisions. v1.0.1 corrects the
  archive-wins count (7 cases ADRs 0011-0017; not 8), the no-collision count
  (9 IDs 0001-0006, 0008-0010; not 10), and extends the canonical-only
  deletion glob to include the v1-superseded variant (per architecture-audit-r1
  findings AA-003, AA-008).
---

# ADR-0055: Archive-wins consolidation policy for version-divergent ADR collisions

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

Accepted — 2026-05-24 (gate-binding user decision at Intent Confirmation Gate; codified in this ADR during Design Composition of `adr-placement-mechanism-repair-r1`).

## Context

The `adrs-migrated/` directory at the repo root is a 47-file legacy archive containing multiple version snapshots of ADRs 0001–0018 (per Discovery IN-003). The PRD's FR-8d hypothesized this archive contained "ADRs 0001–0010, pre-template-migration historical archive" — i.e., no overlap with canonical and a straightforward "move final variants to canonical" disposition.

Discovery IN-004 reversed that assumption. For 8 of the 18 archive ADR IDs (ADRs 0011–0017), both canonical `adrs/` AND `adrs-migrated/` contain a final-variant file. Critically, **the archive's body is v2.0.0 (post-naming-convention update) while the canonical body is v1.0.0 (stale)**. This inverts the intuitive "canonical = current, archive = old" model: for these 8 collisions, canonical is the stale variant.

ADR-0018 is a related but distinct case: collision exists, but canonical carries the supersession-by-ADR-0038 marker (the more current semantic state), so canonical wins. ADR-0007 has no archive final variant; canonical's body is authoritative; archive's pre-* variants are deleted.

The PRD's FR-8d framing ("final variants move with -superseded suffix; pre-naming-convention and pre-template-migration variants are deleted") does not specify the resolution for the 8 archive-wins collisions. Without an explicit ADR, the consolidation either (a) silently overwrites canonical with archive (no provenance), (b) silently keeps stale canonical (forfeits the v2.0.0 naming-convention updates), or (c) re-litigates each case in the Plan executor's task description.

The user resolved this at the Intent Confirmation Gate on 2026-05-24 with a binding directive: **archive wins for the 8 version-divergent collisions; stale canonical bodies are archived to `adrs/superseded/` with provenance footer**. This ADR codifies that directive and establishes the convention for future archive-consolidation incidents.

## Decision

When consolidating a legacy ADR archive into canonical `adrs/` and a numbering collision exists between an archive final-variant and a canonical entry, the resolution proceeds per the version-precedence rule below. The default rule is **archive-wins for version-divergent cases where the archive carries the more current body**; the rule has a documented exception (canonical-wins when canonical carries a supersession marker or other semantic-update marker the archive lacks).

Specifically for the `adr-placement-mechanism-repair-r1` consolidation (Phase 2d):

1. **7 archive-wins cases (ADRs 0011–0017)**: archive body replaces canonical; stale canonical body archived to `adrs/superseded/<id>-pre-consolidation-canonical.md` with provenance footer; new canonical's frontmatter adds `superseded_by_consolidation: true` + `superseded_canonical_archived_to: adrs/superseded/<id>-pre-consolidation-canonical.md`.

   **Note**: Discovery IN-004 surfaced **8 total collisions** across IDs 0011–0018; of those, **7 are archive-wins (0011–0017)** and **1 is canonical-wins (0018, retained because canonical carries a supersession-by-ADR-0038 marker the archive lacks)**. Prior v1.0.0 phrasing "8 archive-wins (ADRs 0011-0017)" conflated the total-collision count (8) with the archive-wins count (7); v1.0.1 corrects.

2. **1 canonical-wins case (ADR-0018)**: canonical body retained (carries ADR-0038 supersession marker); archive's final variant deleted; archive's `-pre-*` variants deleted.
3. **9 no-collision cases (ADRs 0001-0006, 0008-0010)**: archive final-variant `git mv`ed to canonical; archive's `-pre-*` variants deleted. (Note: the range 0001-0010 is 10 IDs total inclusive; one ID — 0007 — is the canonical-only case below; so the no-collision count is 9, not 10. Prior v1.0.0 phrasing "10 no-collision (ADRs 0001-0010)" was off-by-one.)
4. **1 canonical-only case (ADR-0007)**: archive has no final variant; canonical untouched; archive's `-pre-*` variants AND `v1-superseded` variant deleted (the archive carries an `ADR-0007-code-graph-mcp-selection-v1-superseded.md` file alongside its `-pre-*` variants; v1.0.1 extends the deletion glob to cover this distinct variant).
5. **All `-pre-naming-convention`, `-pre-template-migration`, and `-v1-superseded` variants are deleted via `git rm`**; Git history preserves them per NFR-5. Total variant deletions: **30** (per Discovery IN-003: 18 `-pre-naming-convention` + 11 `-pre-template-migration` + 1 `v1-superseded`). Prior v1.0.0 prose said "29 `-pre-*` variants"; v1.0.1 corrects to 30 to reflect inclusion of the v1-superseded variant.

After Phase 2d completes, `adrs-migrated/` is empty and removed (`git rm -r adrs-migrated/`).

## Decision Details

| Item | Content |
|---|---|
| Decision | Archive-wins for version-divergent collisions; canonical-wins when canonical carries a semantic-update marker the archive lacks; stale canonical bodies archived to `adrs/superseded/` with provenance frontmatter; pre-* variants deleted (Git history preserves). |
| Why now | The `adr-placement-mechanism-repair-r1` feature must consolidate `adrs-migrated/` (per binding Intent Confirmation Gate decision); 8 collisions force a precedence rule; without an ADR, the Plan executor re-derives per case. |
| Why this | The archive's v2.0.0 bodies are objectively more current for the 7 archive-wins collisions (carry the naming-convention update per ADR-0019); canonical's v1.0.0 bodies are stale. Keeping stale canonical forfeits the naming-convention work. Preserving stale canonical to `adrs/superseded/` keeps both bodies retrievable for forensic / audit purposes. The post-Phase-2d max-ID computation for the ADR-0053 renumber algorithm operates on the same canonical ID space this ADR reshapes (the renumber baseline is computed after this consolidation completes, against the pre-this-feature canonical IDs plus FR-8c relocations). |
| Known unknowns | (1) Whether `superseded_by_consolidation` and `superseded_canonical_archived_to` are honored by any current frontmatter validator (they are not; will appear as unknown fields, informational only). (2) Whether the precedent extends to future archive consolidations with different version-divergence patterns (current expectation: yes, with the canonical-wins exception applying when canonical has a semantic update marker). |
| Kill criteria | If a future consolidation reveals that the "archive carries v2.0.0; canonical carries v1.0.0" pattern was specific to this archive (not a general invariant), the policy must be re-examined per archive. The default rule (archive-wins for version-divergent) holds; canonical-wins remains the documented exception. |

## Rationale

The user's directive at the Intent Confirmation Gate is binding. This ADR codifies the directive so the Plan executor and future archive-consolidation runs apply the same rule without re-eliciting the user.

The version-precedence rule (archive-wins because archive carries v2.0.0 retroactive naming-convention updates per ADR-0019) is the objective tie-breaker. The canonical-wins exception (ADR-0018's supersession-by-ADR-0038 marker) is the principled exception: when canonical has a semantic update the archive lacks, the semantic state takes precedence over the version number.

Archiving the stale canonical body to `adrs/superseded/` (rather than `git rm`-ing it outright) preserves forensic retrievability. A reader of ADR-0011's new canonical body who wonders "what did the pre-consolidation canonical body say?" can read `adrs/superseded/ADR-0011-pre-consolidation-canonical.md` directly rather than reconstructing from git log. The provenance frontmatter (`superseded_by_consolidation: true` + `superseded_canonical_archived_to: ...`) makes the chain auditable.

The pre-naming-convention and pre-template-migration variants are deleted (not archived to `adrs/superseded/`) because they are historical noise — neither was ever an authoritative canonical body. Git history preserves them; an archaeologist with a real need can `git log --all` to find them.

## Options Considered

### Option 1: Canonical-wins for all 8 collisions

**Pros:** Preserves a "canonical is always the current truth" invariant (which currently DOES NOT hold for these 8 IDs — the invariant is the goal, not the present state).

**Cons:** Forfeits the archive's v2.0.0 naming-convention updates per ADR-0019. Requires re-doing the naming-convention update for the 8 IDs from scratch. Defeats the explicit user directive at the Intent Confirmation Gate.

### Option 2: Per-collision case-by-case (no default rule; Plan executor decides)

**Pros:** Maximum flexibility.

**Cons:** Each case re-litigates. No precedent for future consolidations. Plan executor (executing per the Plan, with limited context) does not have the authority to make this kind of architectural decision; it would surface to user every time. Defeats the purpose of an ADR.

### Option 3 (Selected): Archive-wins for version-divergent + canonical-wins exception when canonical has semantic-update marker + archival of stale canonical to `adrs/superseded/`

**Pros:** Codifies the binding user directive. Establishes a precedent for future archive consolidations. Preserves both bodies (forensic retrievability). Honors ADR-0019 (naming-convention updates land in canonical). Honors ADR-0005 (supersession discipline; the new canonical's `superseded_by_consolidation` frontmatter declares the supersession).

**Cons:** Adds two frontmatter fields (`superseded_by_consolidation`, `superseded_canonical_archived_to`) that current validators do not recognize (informational only). Requires the Plan to handle 8 archive-wins cases + 1 canonical-wins case + 10 no-collision + 1 canonical-only case — four distinct sub-procedures.

## Consequences

### Positive Consequences

- The 8 archive-wins cases land at canonical with the naming-convention updates intact.
- Future archive-consolidation incidents have a precedent rule (this ADR) and don't re-litigate.
- Forensic retrievability is preserved via `adrs/superseded/<id>-pre-consolidation-canonical.md` with provenance frontmatter.
- Honors the user's binding directive at the Intent Confirmation Gate.

### Negative Consequences

- `adrs/superseded/` accumulates 7 new files (one per archive-wins case). The directory's purpose is precisely this archival; not a new burden.
- Two new frontmatter fields (`superseded_by_consolidation`, `superseded_canonical_archived_to`) appear in 7 canonical ADRs; current validators treat them as unknown (informational only). Future validator work should explicitly permit them.
- The Plan must encode four distinct sub-procedures for FR-8d (one per category: archive-wins, canonical-wins, no-collision, canonical-only).

### Neutral Consequences

- The pre-naming-convention and pre-template-migration variants are deleted; Git history preserves them.
- After Phase 2d completes, `adrs-migrated/` is empty and removed; the FR-10 validator no longer needs an allowlist for that path.

## Architecture Impact

1. **Components that change**:
   - **7 canonical ADRs (0011–0017)** get archive-body replacement + new frontmatter fields (`superseded_by_consolidation`, `superseded_canonical_archived_to`).
   - **7 new files** under `adrs/superseded/<id>-pre-consolidation-canonical.md` (one per archive-wins case).
   - 1 canonical ADR (0018) untouched; its archive counterpart's final variant deleted.
   - **9 archive ADRs (0001-0006, 0008-0010)** `git mv`ed to canonical.
   - **30 archive variant files deleted** (`git rm`): 18 `-pre-naming-convention` + 11 `-pre-template-migration` + 1 `v1-superseded`.
   - `adrs-migrated/` directory removed.

2. **New dependencies introduced**: None. Reuses `git mv` (per NFR-5) and existing frontmatter conventions.

3. **Architectural constraints added or removed**:
   - **Added**: Archive-consolidation precedence rule (archive-wins for version-divergent; canonical-wins for semantic-update markers).
   - **Added**: Provenance frontmatter convention (`superseded_by_consolidation`, `superseded_canonical_archived_to`).
   - **Added**: Stale-canonical archival convention (`adrs/superseded/<id>-pre-consolidation-canonical.md`).
   - **Removed**: The `adrs-migrated/` directory's presence in the repo (eliminated after Phase 2d).

4. **Layers affected**: Claude Code / Project Filesystem only.

## Implementation Guidance

- **Precedence test**: for each collision, check whether canonical carries a semantic-update marker (supersession, frontmatter `supersedes:` referring to a later ADR, etc.) the archive lacks. If yes → canonical-wins. Otherwise (version-divergent or stale canonical) → archive-wins.
- **Archive-wins procedure**: (1) read canonical body; (2) write canonical body to `adrs/superseded/<id>-pre-consolidation-canonical.md` with a provenance footer (originating-feature reference + consolidation rationale); (3) `git mv adrs-migrated/<id>-final*.md adrs/<id>-<slug>.md`; (4) add `superseded_by_consolidation: true` + `superseded_canonical_archived_to: adrs/superseded/<id>-pre-consolidation-canonical.md` to the new canonical's frontmatter.
- **Canonical-wins procedure**: (1) `git rm` the archive's final variant; (2) `git rm` the archive's `-pre-*` variants; (3) canonical untouched.
- **No-collision procedure**: (1) `git mv adrs-migrated/<id>-final*.md adrs/<id>-<slug>.md`; (2) `git rm` the archive's `-pre-*` variants.
- **Canonical-only procedure**: (1) `git rm` the archive's `-pre-*` variants AND the `v1-superseded` variant if present (no final variant in archive); (2) canonical untouched.

  **v1.0.1 glob extension**: prior v1.0.0 phrasing "`git rm` the archive's `-pre-*` variants" matched only the `-pre-naming-convention` and `-pre-template-migration` patterns; the archive's ADR-0007 directory also contains an `ADR-0007-code-graph-mcp-selection-v1-superseded.md` file that does not match the `-pre-*` glob. Under literal v1.0.0 reading the Plan executor would leave a stray ADR-0007-*.md in `adrs-migrated/`, which the FR-10 validator would flag (no allowlist entry exists for `adrs-migrated/` post-Phase-2d). v1.0.1 explicitly extends the deletion scope to include the `v1-superseded` variant.
- **Provenance footer** for stale-canonical archival: include the originating feature slug (or "pre-consolidation canonical state"), the date of consolidation, and a one-line note identifying the consolidating feature.

Procedural details (per-task atomicity, commit-boundary granularity, verification steps) belong to the Plan, not this ADR.

## Related Information

- Related ADRs: ADR-0005 (supersession discipline — the `superseded_by_consolidation` frontmatter is an instance of supersession), ADR-0019 (naming convention — the archive's v2.0.0 bodies carry the naming-convention update this policy preserves), ADR-0036 (single-location placement — destination is canonical), ADR-0053 (renumbering algorithm — the post-Phase-2d max-ID computation depends on the post-consolidation canonical state this policy produces; the renumber baseline operates on the same canonical ID space this ADR reshapes), ADR-0054 (three-surface enforcement — the validator confirms post-consolidation canonical-only placement; allowlist for `adrs-migrated/` is unnecessary post-Phase-2d).
- Referenced specs / docs: `working/feature/adr-placement-mechanism-repair-r1/blueprint-v1.md` (this feature's Blueprint), `working/feature/adr-placement-mechanism-repair-r1/codebase-analysis.json` IN-003 + IN-004 (archive inventory + collision discovery), Synthesis D2 (binding gate decision).
- Issues / PRs: `Issues/adr-placement-rootcause/proposal.md` (originating proposal; archive consolidation not in original scope but became binding under v2.0.0 directive + Intent Confirmation Gate).
- Related KBs: `KB-documentation-criteria` (frontmatter convention extensions), `KB-cc-design` (canonical-only convention).

## Revision History

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-05-24 | design-composer | Initial authoring during Design Composition of `adr-placement-mechanism-repair-r1`; codifies the 2026-05-24 gate-binding user directive. |
| 1.0.1 | 2026-05-25 | design-composer | Frontmatter-stable amendment per ADR-0005, in response to architecture-audit-r1 findings AA-003 + AA-008. (1) Decision item 1: corrected archive-wins count from "8 archive-wins (ADRs 0011-0017)" to "7 archive-wins (ADRs 0011-0017)"; the 8 figure was the total-collision count (7 archive-wins + 1 canonical-wins). (2) Decision item 3: corrected no-collision count from "10 no-collision (ADRs 0001-0010)" to "9 no-collision (ADRs 0001-0006, 0008-0010)" to reflect the ADR-0007 carve-out (range 0001-0010 inclusive is 10 IDs; minus 0007 = 9). (3) Implementation Guidance / Canonical-only procedure: extended the deletion glob to include the `v1-superseded` variant in addition to `-pre-*` variants (closes AA-003 gap where the literal `-pre-*` glob would leave a stray ADR-0007-v1-superseded.md in `adrs-migrated/`). (4) Architecture Impact: updated component-change counts (7 canonical replacements, 7 new superseded files, 9 archive moves, 30 variant deletions including the +1 v1-superseded). (5) Cross-reference to ADR-0053's renumber-baseline relationship added. No supersession; Decision is unchanged in spirit (archive-wins policy stands). |
