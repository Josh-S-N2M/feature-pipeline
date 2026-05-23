---
id: ADR-0034
title: PRD v1.1.0 narrative housekeeping — ADR-0017 is canonical home for the 4-cycle reconciliation cap
status: accepted
date: 2026-05-22
accepted: 2026-05-22
deciders: [user, claude (as design-composer)]
supersedes: []
superseded_by: []
related: [ADR-0005, ADR-0017, ADR-0021, ADR-0029, ADR-0032]
authored_in_feature: execution-pipeline-design-r1
pairs_synthesis_decisions: []
corrects: ["PRD-execution-pipeline-design-r1 v1.1.0 narrative attribution (frontmatter amendment_log + FR-10 prose)"]
revised: 2026-05-22T18:30:00Z
revision_reason: |
  In-place edit per blueprint-v2.md cycle, addressing audit finding I-AA-002.
  Original Context + Decision incorrectly characterized ADR-0021 as "inheritor"
  of the 4-cycle cap. Full-text search of ADR-0021 returns zero references to
  the cap; the only cap in ADR-0021 is the unrelated ≤6 parallel external-research
  cap from ADR-0006. Context, Decision, Future references, and Validation evidence
  subsections all updated to drop the unsupported inheritance claim. In-place edit
  acceptable because status: proposed (per ADR-0032 per-doc-type ADR vocabulary,
  the proposed → accepted transition has not yet occurred at the Architecture
  Audit pass).
---

# ADR-0034: PRD v1.1.0 narrative housekeeping — ADR-0017 is canonical home for the 4-cycle reconciliation cap

## Context

PRD v1.1.0 (`prd-v1.1.0.md`, gate_passed=2) contains narrative references to the 4-cycle reconciliation cap that informally credit **ADR-0021** (`discovery-phase-architecture.md`) as the canonical home. Observable locations:

- Frontmatter `amendment_log` field (text discussion of pipeline reconciliation discipline)
- FR-10 prose (commentary on the execution-side reconciliation budget)

The actual canonical home is **ADR-0017** (`document-reviewer-integration.md`), which introduces the 4-cycle reconciliation cap as part of the document-reviewer flow (Decision section line 155: "Iteration cap: 4 cycles..."). PRD v1.1.0's attribution of the cap to ADR-0021 is unsupported by ADR-0021's actual text — ADR-0021 (`discovery-phase-architecture.md`) does NOT in fact reference or apply the 4-cycle reconciliation cap. A full-text search of ADR-0021 returns zero matches for `4-cycle`, `4 cycle`, `cycle cap`, or `reconciliation cap`; the only cap referenced in ADR-0021 is the ≤6 parallel external-research cap from ADR-0006 (line 85), which is unrelated to reconciliation. The PRD's attribution of the cap to ADR-0021 is therefore a documentary error this ADR corrects, not (as a reader might assume from common ADR-inherits-ADR patterns) a case of one ADR applying another's discipline.

Provenance footnote: ADR-0017's own text (line 155) describes the cap as "matching the pipeline's broader fixed-point iteration discipline from blueprint v3 §3.7" — i.e., ADR-0017 itself adopts an earlier blueprint-v3 discipline. For most downstream-citation purposes, ADR-0017 is the canonical addressable ADR-form artifact (it's the only ADR that names "4 cycles" explicitly); the deeper provenance in blueprint v3 §3.7 is the underlying source.

The mis-credit was surfaced during the Discovery Research stage (codebase-analysis.md IN-009 review) of this feature run and a corrective in-table caption was applied to `codebase-analysis.md` v1.1.1. (Note: the codebase-analysis.md v1.1.1 caption's framing of ADR-0021 as "inheritor" of the cap was itself imprecise — ADR-0021 does not in fact reference or inherit the cap; this Architecture-Audit-pass-induced refinement of ADR-0034 (the v2 Blueprint cycle) clarifies the more accurate framing above.) The PRD prose was NOT updated because PRD v1.1.0 is `gate_passed=2` and substantive supersession is reserved for normative-content changes per ADR-0005 append-only.

This ADR documents the canonical ownership in an addressable artifact so future Blueprint, Plan, and Test artifacts have a clean source to cite when referencing the 4-cycle cap, without being misled by the residual mis-credit in PRD v1.1.0 prose.

## Decision

**ADR-0017 is the canonical home for the 4-cycle reconciliation cap.** ADR-0021 has no actual relationship to the cap (the PRD's attribution to it is the documentary error this ADR corrects); future references should cite ADR-0017.

**No PRD v1.1.0 edit is performed.** The PRD's normative content (FRs and ACs) is unaffected by the mis-credit; the mis-credit is a narrative annotation, not a behavioral change. Per ADR-0005 append-only discipline, supersession is reserved for substantive content changes; documentary corrections of this nature do not warrant a v1.1.1 supersession.

**Future references**: any Blueprint, Plan, Acceptance Tests, Phase Validators, or downstream ADR that references the 4-cycle reconciliation cap MUST cite ADR-0017 as canonical home. ADR-0021 should NOT be cited for the cap (it has no content on this discipline); citing ADR-0021 alongside ADR-0017 perpetuates the original documentary error.

**Corrective sources** for the mis-credit:
1. This ADR-0034 (primary corrective artifact)
2. `codebase-analysis.md` v1.1.1 IN-009 review (where the correction was first surfaced and applied in-table)

Future authoring agents encountering the PRD v1.1.0 prose mis-credit should reference both sources when correcting downstream artifacts.

## Validation evidence

### ADR-0017 defines the cap

ADR-0017 (`document-reviewer-integration.md`) Decision section introduces the 4-cycle reconciliation cap as part of the document-reviewer flow specification. The cap is part of the document-reviewer's operational protocol; ADR-0017 is the originating definition.

### ADR-0021 does not reference or define the cap

ADR-0021 (`discovery-phase-architecture.md`) is the document PRD v1.1.0 mis-credits, but a full-text search of ADR-0021 returns zero matches for `4-cycle`, `4 cycle`, `cycle cap`, or `reconciliation cap`. Reading ADR-0021's Decision section confirms: no constructions of the cap; no references to it; no inheritance of it. The only cap referenced in ADR-0021 (line 85) is the ≤6 parallel external-research cap from ADR-0006, which governs research-stage fan-out, not reconciliation. The PRD v1.1.0's attribution of the reconciliation cap to ADR-0021 is therefore a clean documentary error, not a case of imprecise ADR pedigree.

### codebase-analysis.md v1.1.1 in-table correction

During the Discovery Research stage of this feature run (`codebase-analysis.md` v1.1.1, IN-009 review), the mis-credit was caught and corrected in-table:

> [IN-009 caption from codebase-analysis.md v1.1.1]: "ADR-0017 is canonical home for the 4-cycle reconciliation cap. ADR-0021 inherits and applies. Note: PRD v1.1.0 narrative informally credits ADR-0021; the correction is documented here and will be formalized in an ADR during Design Composition."

This ADR-0034 fulfills the "formalized in an ADR during Design Composition" commitment from the codebase-analysis correction.

### cc-design.md Open items pre-declaration

`cc-design.md` v1.0.0 Open items section listed "ADR-C: PRD v1.1.0 mis-credit cleanup" as a planned ADR for this feature run, with the explicit option to fold into ADR-0032 OR stand alone. The Blueprint Batch 4 decision (user option 1 — 2 separate ADRs) selected the stand-alone option; this ADR-0034 fulfills that pre-declaration.

## Consequences

**Positive:**

- Future references have an addressable canonical statement of 4-cycle cap ownership (ADR-0017 + ADR-0034 corrective annotation).
- The correction is preserved in an addressable artifact rather than buried in a single per-artifact in-table caption (codebase-analysis.md).
- ADR-0029's no-silent-scope-changes principle is honored: the mis-credit was a documentary deviation surfaced during Discovery; this ADR explicitly closes the loop rather than leaving it absorbed into the codebase-analysis caption alone.
- Avoids the heavier cost of PRD supersession (v1.1.0 → v1.1.1) for a non-behavioral correction.

**Negative:**

- Adds an ADR for documentary housekeeping. The discipline-5 mechanical-enforcement substrate (D-15) suggests mechanical correction is preferable to manual attribution; this ADR is manual attribution. (Mechanical attribution-checking is out of scope for this feature; would be a follow-on enhancement to the frontmatter validator that cross-references attributions against canonical ADR ownership.)
- Future readers of PRD v1.1.0 prose will encounter the mis-credit without context if they read PRD-only without checking ADR-0017/0034. The codebase-analysis.md and this ADR are the corrective references, but discoverability depends on the reader cross-checking. Mitigated by: downstream artifacts (this Blueprint, future Plan, etc.) cite ADR-0017 directly when referencing the cap, providing the corrective path for any reader following the artifact chain.

**Forward implications:**

- No further work required for this feature run. The PRD v1.1.0 prose remains as-authored; the canonical attribution is documented here.
- If a future feature re-authors the PRD substantively (e.g., for normative-content changes), the re-authored version should correct the prose during the substantive supersession. Until then, ADR-0034 + codebase-analysis.md serve as the corrective references.
- The pattern (ADR-as-corrective-reference for documentary mis-attribution caught during Discovery) may recur in future feature runs. If it recurs frequently, a follow-on feature could consider a more systematic mechanism (e.g., a per-artifact `errata:` frontmatter field listing post-acceptance corrections without supersession).

**Risk of over-application:**

- This ADR's pattern (ADR for documentary cleanup without artifact supersession) should NOT become a default escape from supersession discipline. Documentary corrections that DO change normative content (e.g., a typo in an AC that changes its meaning) STILL require supersession per ADR-0005. The mis-credit corrected here is attribution-narrative, not normative content; this distinction must be preserved.

## Alternatives considered

**Alternative 1: Supersede PRD v1.1.0 with v1.1.1 correcting the prose.** Rejected: the mis-credit doesn't change normative content (FRs and ACs are unaffected); supersession is over-heavy for a documentary fix. ADR-0005 append-only discipline applies, but supersession is reserved for substantive content changes. Performing supersession for documentary corrections would muddle the supersession threshold.

**Alternative 2: Fold into ADR-0032 as a fifth change category ("PRD v1.1.0 narrative housekeeping").** Available alternative pre-declared in ADR-0032's "Alternative 5" section. Rejected per user's Blueprint Batch 4 decision (option 1 — 2 separate ADRs). The "one decision per ADR" discipline pushed back: ADR-0032's three decision categories (frontmatter fields, vocabulary, doc_type) are joint dispatch-key concerns; the PRD mis-credit is conceptually distinct documentary attribution. Separating honors the "one decision per ADR" guideline.

**Alternative 3: Defer to a future feature.** Rejected: ADR-0029's no-silent-scope-changes principle suggests surfacing documentary clarifications when they arise rather than deferring. The deferral cost (PRD prose remains mis-credited) compounds over time as more downstream artifacts may pick up the wrong attribution; surfacing now stops the propagation.

**Alternative 4: Leave the codebase-analysis.md in-table correction as the sole corrective reference; no ADR needed.** Rejected: in-table corrections in a single feature's artifact have limited cross-feature discoverability. Future feature runs that reference the 4-cycle cap should find the canonical statement at the ADR layer, not buried inside a specific feature's codebase-analysis. The cost of authoring this short ADR is small relative to the discoverability benefit.

## Notes

This ADR is intentionally short relative to ADR-0032 and ADR-0033. It documents a single corrective attribution and explicitly does not perform PRD supersession.

The PRD v1.1.0 is preserved as-is per ADR-0005 append-only; this ADR-0034 is the corrective reference rather than a PRD modification. The pattern (ADR-as-corrective-reference for documentary mis-attribution) is novel enough to warrant the "Risk of over-application" framing above: this pattern is acceptable for documentary corrections but NOT for normative-content corrections.

No pairing with a synthesis-stage decision: the mis-credit was not surfaced at synthesis (it was surfaced earlier, at codebase-analysis IN-009 review). The synthesis stage operated on the corrected attribution. This ADR is end-of-pipeline housekeeping rather than a synthesis-decision pairing.
