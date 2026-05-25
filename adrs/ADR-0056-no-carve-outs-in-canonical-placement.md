---
id: ADR-0056
title: No carve-outs in canonical-placement rules — uniform rules over named exceptions
status: accepted
date: 2026-05-25
accepted: 2026-05-25
deciders: [user, claude (orchestrator)]
supersedes: []
superseded_by: []
related: [ADR-0005, ADR-0036, ADR-0054]
authored_in_feature: adr-placement-mechanism-repair-r1 (post-execution amendment)
pairs_synthesis_decisions: []
subsumes: []
change_summary: |
  Codifies a project-wide design discipline: when a canonical-placement rule
  exists (ADR-0036 for ADRs is the precedent), no naming-convention,
  extension-based, or allowlist-based exception is permitted to evade the
  rule. Audit trails live in `git log` and in canonical migration-log files,
  never as scattered breadcrumb files at the legacy locations. Retires the
  ".tombstone" redirect-file sub-decision from the
  `adr-placement-mechanism-repair-r1` Plan + Blueprint (T2c.1 surface c)
  retroactively; the five tombstone files written by that feature have been
  deleted under this ADR.
---

# ADR-0056: No carve-outs in canonical-placement rules — uniform rules over named exceptions

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

Accepted — 2026-05-25. Authored as a post-execution amendment to `adr-placement-mechanism-repair-r1` after user durable feedback surfaced the principle.

## Context

`adr-placement-mechanism-repair-r1` shipped the canonical-only ADR placement enforcement per ADR-0036 (the validator + three wired surfaces per ADR-0054). The Plan + Blueprint of that feature also specified a `.tombstone` redirect-file pattern: when an ADR was relocated from `working/feature/<slug>/adrs/ADR-NNNN-<slug>.md` to canonical `adrs/`, the Plan instructed the agent to write a 3-line `.tombstone` file at the old location pointing at the new canonical path. The `.tombstone` extension was intentional — `validate_adr_placement.py`'s `rglob('ADR-*.md')` would not match it, so the validator was satisfied.

This is a carve-out. The placement rule says "ADRs live in `adrs/`." The tombstones are files-named-after-ADRs that don't live in `adrs/`. The rule was preserved only by an extension-based naming convention that exists *specifically to evade the rule*.

The user surfaced this during post-execution review of `adr-placement-mechanism-repair-r1`. Plain-English summary of the durable feedback: *"Over time this makes a system fragile as the system evolves. It's small now but do this 100 times and it just creates complexity, waste and confusion."* Each carve-out is a future maintenance tax — a thing future readers and agents must learn before they can reason about the system, a thing the validator must special-case, a thing the documentation must caveat. The cost compounds.

This ADR codifies the principle so future Plans / Blueprints can't reach for the same shape of escape valve.

## Decision

1. **Uniform rules.** When a canonical-placement rule exists for an artifact class, every file in that class lives at the canonical location. No naming-convention, extension-based, or allowlist-based exception is permitted to evade the rule.

2. **Audit trails by reference, not by breadcrumb.** Provenance for migrations, relocations, or supersessions lives in `git log` (for the file-move event itself) and in `working/feature/<slug>/migration-log.md` (for the feature-run audit narrative). Stale-location breadcrumb files are not authored.

3. **Retroactive application.** The five `.tombstone` files written by `adr-placement-mechanism-repair-r1` Phase 2c (T2c.1) at `working/feature/issue-capture-mechanism-r1/adrs/ADR-{0046,0047,0048,0049,0050}.tombstone` are retired under this ADR. They have been deleted. Provenance for those five moves is preserved by the existing `git log adrs/ADR-004{6..9}-*.md` rename detection plus the `migration-log.md` Phase-2c table in `adr-placement-mechanism-repair-r1`'s working directory.

4. **Legitimate exceptions are not carve-outs.** Two patterns remain valid because they are not exceptions to a rule but distinct structural categories:
   - `adrs/superseded/` is a recognized structural category (codified in ADR-0005 + `validate_adr_placement.py`'s parent-directory check), not a carve-out. It has its own well-defined semantics.
   - `--allowlist` flags exist for cross-tool integration where two systems own distinct namespaces (e.g., `--allowlist 'output/synthesis-*/adrs/'` for the synthesize skill's distinct output tree). The allowlist exists to integrate two systems whose namespaces are independent by design, not to evade a uniform rule.

   The test for "is this a legitimate distinction or a carve-out?": does it have a uniform internal rule, or is it a one-off escape valve? `adrs/superseded/` has uniform internal semantics (archived bodies of replaced ADRs, validated against the same field schema). `--allowlist` integrates with a sibling system that owns its own validator. Both are durable. Tombstones-as-breadcrumbs is not — it exists *only* to make one rule pass.

## Decision Details

### What gets retired

- The `.tombstone` redirect-file pattern as a tool for ADR migration. Future feature runs that relocate or rename ADRs do NOT author `.tombstone` files. The Plan-task pattern that includes "write a .tombstone redirect note" is retired.

### What stays in effect

- ADR-0036 (single-location canonical ADR placement) — unchanged.
- ADR-0054 (canonical helper subprocess wiring at three surfaces) — unchanged. ADR-0054 governs the validator-script integration with orchestrator / phase-checks / packager; that machinery is not affected by retiring the tombstone sub-decision. ADR-0054 itself never specified `.tombstone` files; the tombstone instruction lived in the Plan of `adr-placement-mechanism-repair-r1`.
- `validate_adr_placement.py` — unchanged. Its `rglob('ADR-*.md')` already enforces the uniform rule; no exception logic exists in the code to remove.

### Provenance preserved

For the 5 retired tombstones, provenance lives in two redundant places:

- **`git log adrs/ADR-004{6..9}-*.md`** + **`git log adrs/ADR-0050-*.md`** with `--follow` shows the rename from `working/feature/issue-capture-mechanism-r1/adrs/` to canonical `adrs/`. Git's automatic rename detection makes this loss-free.
- **`working/feature/adr-placement-mechanism-repair-r1/migration-log.md`** Phase-2c table records every disposition: source path, target path, sub-procedure, timestamp.

Neither requires the tombstone files to exist.

## Rationale

The cost of each carve-out is hidden at authoring time and surfaces during evolution. Concrete failure modes the project has already seen or would predictably see:

- **Validator discipline erosion.** Once an extension-based exception exists, the next feature to need an exception will reach for the same pattern. Five exceptions later, the validator's scan-pattern is a maze of special cases and future authors don't know which rules are uniform.
- **Reader confusion.** Anyone seeing `working/feature/<slug>/adrs/ADR-0046.tombstone` for the first time has to learn the tombstone concept before they can interpret what they're looking at. This cost is paid once per reader-encounter, forever.
- **Drift surface.** A breadcrumb file pointing at a canonical location is a synchronization burden — if the canonical location ever changes, every breadcrumb is stale.
- **Compound complexity.** The user's stated framing: *"do this 100 times and it just creates complexity, waste and confusion."* Each individual carve-out looks principled; the aggregate is a tax.

`git log` already solves the provenance problem. The `migration-log.md` already records the audit narrative. The tombstone files added a third redundant signal whose only durable function was to satisfy a validator's naming pattern.

## Options Considered

### Option A — Keep the tombstones, treat the extension-naming-as-evasion as principled (rejected)

**Description:** Argue that `.tombstone` is a distinct artifact class with its own (informal) semantics, and the validator correctly ignores it.

**Why rejected:** This is the post-hoc rationalization shape that hides every carve-out. The test for "distinct class vs. evasion" is whether the artifact has a uniform internal rule. The tombstones had no schema, no required fields, no validator, no upgrade path. They existed to be ignored. That's the definition of evasion.

### Option B — Add tombstone-detection logic to the validator (rejected)

**Description:** Extend `validate_adr_placement.py` to actively reject any `*.tombstone` file at a former ADR location.

**Why rejected:** This is adding an exception to detect an exception — explicitly anti-principle. The clean solution removes the artifact, not adds detection logic.

### Option C — Centralize redirects in `adrs/REDIRECTS.md` (rejected)

**Description:** Replace the 5 scattered tombstone files with a single canonical redirect file in `adrs/` listing every historical move.

**Why rejected:** Still adds a special concept ("the REDIRECTS.md file is a special canonical file you must consult before assuming an ADR is at its filename"). `git log` already solves this and doesn't add new concepts.

### Option D — Delete the tombstones; codify "no carve-outs" as project discipline (accepted)

**Description:** Remove the 5 tombstone files. Author this ADR. Reference `git log` and `migration-log.md` for provenance.

**Why accepted:** Smallest mechanism. No new artifact class. No new validator logic. No new file-to-consult. Provenance is preserved by mechanisms that already exist for other reasons. Pre-empts every future carve-out by giving authors a principle to defer to.

## Consequences

### Positive

- **One fewer concept to learn.** New readers of the repo never encounter the tombstone pattern.
- **Validator stays uniform.** `rglob('ADR-*.md')` is the rule, and it's the whole rule.
- **Pre-empts future carve-outs.** Plan-authors and Blueprint-authors can defer to this ADR when a future feature run is tempted to specify naming-convention exceptions.
- **Cleaner working tree.** No empty `working/feature/<slug>/adrs/` directories with tombstones inside.

### Negative

- **Direct lookup of an old path now returns 404.** Anyone reading old design docs that reference `working/feature/issue-capture-mechanism-r1/adrs/ADR-0046-*.md` will not find the file at that path. They will need to consult `git log` or the `migration-log.md` to learn it moved.
- **The cost is paid once per stale-path encounter.** Mitigation: `Phase 3 of adr-placement-mechanism-repair-r1` already rewrote all known consumers' references; future encounters are rare and limited to deep historical artifacts (which are themselves preserved with their original references intact per ADR-0005).

### Neutral

- ADR-0054's three-surface enforcement pattern is unchanged. The wiring that ADR governs (orchestrator stage gate / run_phase_checks dispatch / packager subprocess) remains the canonical helper integration.

## Architecture Impact

This ADR is a discipline-level decision. It does not change executable code. It changes:

- The set of files in the repo (5 tombstones removed).
- The Plan / Blueprint pattern catalog: tombstone-as-redirect is retired and should not appear in future Plans.
- The KB-cc-design principles set: a new principle ("uniform placement rules; no extension-based carve-outs") is added per this ADR.

## Implementation Guidance

### Immediate (this commit)

1. Delete `working/feature/issue-capture-mechanism-r1/adrs/ADR-{0046,0047,0048,0049,0050}.tombstone` (5 files). Done via `git rm`.
2. Remove the now-empty `working/feature/issue-capture-mechanism-r1/adrs/` directory.
3. Add a one-line entry to `working/feature/adr-placement-mechanism-repair-r1/migration-log.md` noting the post-execution retirement of the tombstone files per this ADR.
4. Add the uniform-rule principle to `.claude/skills/KB-cc-design/references/principles.md` with a cross-reference to this ADR.

### Future (every Plan / Blueprint going forward)

When authoring a Plan or Blueprint that proposes a placement convention, the author MUST check whether the proposal introduces:

- An extension-based exception to a canonical-placement rule (smell)
- An allowlist entry that exists to evade a uniform rule rather than integrate two systems (smell)
- A scattered breadcrumb pattern in the legacy location (smell)
- A "treat X as not-really-a-Y" naming convention (smell)

If any of these is proposed, the proposal must be either (a) restructured to eliminate the carve-out, or (b) explicitly justified against the "uniform internal rule vs. one-off escape valve" test from this ADR's §Decision item 4.

### How the reviewer enforces

`shared-document-reviewer` at Gate 0/1 reviews of Plan / Blueprint documents should flag any proposed carve-out shape and cite this ADR. Future updates to `KB-cc-design/references/principles.md` (the discipline KB consulted by per-layer designers and the composer) will make this enforcement load-bearing rather than aspirational.

## Related Information

### Related ADRs

| ADR | Subject | Relation |
| --- | --- | --- |
| ADR-0005 | Append-only supersession | Provenance via `adrs/superseded/` is the canonical pattern; tombstones-as-redirect is the *anti-*pattern this ADR retires |
| ADR-0036 | Single-location ADR placement | The canonical-placement rule that the retired tombstones were carving an exception around |
| ADR-0054 | Canonical helper three-surface enforcement | Unchanged; the validator-wiring machinery is not affected by retiring the tombstone sub-decision in the Plan that ADR-0054 supported |

### Triggering feedback

User durable feedback at session-end of `adr-placement-mechanism-repair-r1` post-execution review (2026-05-25). Verbatim summary preserved in this session's memory:

> "I do not like exceptions. Over time this makes a system fragile over time as the system evolves. Its small now but do this 100 times and it just creates complexity, waste and confusion."

### Cross-references

- `working/feature/adr-placement-mechanism-repair-r1/blueprint-v1.md` — original Plan + Blueprint that specified the `.tombstone` redirect-file pattern (T2c.1 surface c). Preserved unmodified per ADR-0005 supersession discipline; this ADR is the forward-signal that retires the pattern, not a rewrite of history.
- `working/feature/adr-placement-mechanism-repair-r1/migration-log.md` — Phase-2c table records every relocation disposition. Now extended with a Phase-R-postscript noting the tombstones' retirement per this ADR.
- `.claude/skills/KB-cc-design/references/principles.md` — discipline home where the "no carve-outs" principle is being codified (updated under the same commit as this ADR).
