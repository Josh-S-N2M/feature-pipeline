# Task T1.3 Execution Result — issue-proposal-template.md

## Status: COMPLETED

## Files Created

- `.claude/skills/KB-documentation-criteria/references/templates/issue-proposal-template.md`

## Files Modified

(none)

## Scope Deviations

(none)

## 4-Phase Gate Results

| Phase | Result | Notes |
|---|---|---|
| Phase 1 — Lint/Format | N/A | Markdown template; no linter applicable |
| Phase 2 — Build | N/A | Static document; no compilation step |
| Phase 3 — Test (L1+L2) | PASS | All L1 and L2 checks passed (see below) |
| Phase 4 — Final Gate | PASS | All checks green |

### L1 Results

- File exists at deliverable path: PASS
- YAML frontmatter structural check (no tabs; block extracted cleanly): PASS

### L2 Results

- Forbidden phrases grep (when to capture / invocation guidance / the agent should): PASS — no matches
- 7 universal-required fields present (id, version, doc_type, status, feature_slug, generated, generated_by): PASS — all 7 present
- `proposes_future_feature:` field documented (advisory): PASS
- `doc_type: issue-proposal` canonical value: PASS
- ADR-0046 cross-link fields documented (escalates_from, escalated_to): PASS
- Both precedent shapes accommodated (suggested-slug and fixed-slug): PASS
- info-severity advisory posture stated: PASS
- Line count: 120 (within 80–150 budget)

## Notes

The template follows the adr-template.md structural convention: YAML frontmatter with
placeholders, a Contents checklist, and H2 body sections. The body skeleton is modeled on
both empirical precedents — the auditing-family-graduation-review proposal and the
issue-capture-mechanism proposal — and distills their common section pattern into: TL;DR,
Proposed Feature, Motivation, Open Questions, Scope Considerations, and Cross-links.

The `proposes_future_feature` advisory field is documented entirely within a YAML comment
block in the frontmatter (three lines: the advisory posture with info-severity reference,
the two accepted precedent shapes with inline examples, and guidance on when to use the
suggested-slug annotation vs. a bare fixed slug). This placement ensures that readers who
only scan the frontmatter see the advisory documentation without needing to read the body.

The per-state companion field pattern is expressed as comment-examples inside the `status`
field block: each of the 6 states is listed on one line with its required companion fields,
keeping the pattern visible without duplication and without adding non-structural prose.
Cross-link fields (escalates_from, escalated_to, rolled_into_register) are documented both
as commented-out optional YAML fields in the frontmatter and as a Cross-links section in
the body, referencing ADR-0046.
