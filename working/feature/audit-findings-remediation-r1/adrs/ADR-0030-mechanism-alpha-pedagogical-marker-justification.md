---
id: ADR-0030
title: Mechanism α — inline justification required per pedagogical marker
status: accepted
date: 2026-05-21
deciders: [user, claude]
supersedes: []
superseded_by: []
related: [ADR-0029, ADR-0011, ADR-0013, ADR-0023]
authored_during: audit-findings-remediation-r1 (Stage 7 Design Composition)
---

# ADR-0030: Mechanism α — inline justification required per pedagogical marker

## Context

The project's `pedagogical-marker-spec.md` (in `auditing-cc-configs/references/`) introduced two marker forms: file-level `pedagogical_sections:` frontmatter and block-level ` ```audit-example ` fences. Both demote findings inside marked content from BLOCKER to informational. The spec includes anti-laundering rules that prevent bare wrapping of genuine credentials.

What the existing spec does NOT prevent: an author (or future agent) treating "got a BLOCKER → add a marker" as a workflow reflex. Markers become rote. Real defects get silently swallowed when an author wraps content faster than they think about it.

This is the failure mode the user named explicitly during intent refinement for the `audit-findings-remediation-r1` feature:

> "Markers OK but we need to validate and ensure markers do not become a default to actually broken links. We can not silently fail."

External research (T-001) surveyed 5 comparable static-analysis ecosystems (ESLint, Pylint, Bandit, Semgrep, RuboCop). Three findings:

1. **All 5 ecosystems have a justification convention**, recommended in official docs or first-party plugins.
2. **None of the 5 enforce justification by default** — all are opt-in. Bandit, Pylint, RuboCop have open feature requests (some 10+ years old) to add enforcement.
3. **The convergence pattern is: structured form + `--` separator + machine-parseable**, with explicit "describe WHY not WHAT" guidance (Semgrep's rule-ID-stability warning).

The project should adopt enforcement by default — not opt-in — because the discipline only holds if every marker has paper trail.

## Decision

Adopt **mechanism α** as the project-wide pedagogical-marker discipline:

> Every pedagogical marker (frontmatter `pedagogical_sections:` entry OR block-level `audit-example` fence) MUST carry an inline justification. The auditor REJECTS markers lacking justification — treats the marker as if absent, so the underlying finding surfaces at its original severity.

### Syntactic forms

**Frontmatter (structured dict):**

```yaml
---
name: <skill-name>
description: ...
pedagogical_sections:
  - path: references/credential-patterns.md
    justification: "Documents credential string patterns the auditor's DE-2 scanner looks for; not real credentials. Reference catalog for security training and auditor tests."
  - path: examples/bad-mcp-config.md
    justification: "Negative-example MCP config illustrating the tool-poisoning attack pattern; demonstrates what the auditor's MCP scanner detects."
---
```

The bare-list form (`pedagogical_sections: [path1, path2]`) is REJECTED — has no justification slot.

**Fence (with `--` separator):**

````
```audit-example -- credential-shaped string is illustrative; documents the pattern DE-2 detects
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
```
````

The bare fence (` ```audit-example ` with no `--` annotation) is REJECTED — no justification.

The `--` separator convention matches ESLint and RuboCop. It's machine-parseable, allowing future tooling to audit justifications.

### Justification validity rules

A justification is valid if and only if all of:

1. **Length floor:** ≥ 5 words AND ≥ 30 characters.
2. **Not a banned bare word:** justification consisting solely of one of {"pedagogical", "example", "illustrative", "documentation", "not real", "fake", "test"} (or trivial concatenations like "pedagogical example") is rejected.
3. **Substance requirement:** justification references EITHER (a) the content type ("credential patterns", "vulnerable URL examples", "intentional anti-pattern") OR (b) the document's role ("anti-laundering catalog", "negative-example reference"). Enforced loosely via keyword presence; extension procedure documented in the spec.

### Enforcement

**Primary (auditor):** `pedagogical_marker_check.py` (canonical implementation in `auditing-shared` per ADR-0031) checks every marker's justification on every audit run. Invalid → marker rejected → underlying finding surfaces at original severity.

**Secondary (reviewer):** `shared-document-reviewer.md` gains a new `PedagogicalMarkerJustification` doc_type. When invoked during review cycles, validates target's markers. Redundant with auditor but catches the case where someone bypasses scan (e.g., new content not yet scanned).

### Retroactive application — no grandfathering

Markers shipped before this ADR (notably v4.4.0's `<pedagogical-example>` HTML-tag form in `KB-visual-design/references/anti-slop.md`, plus existing `pedagogical_sections:` bare-list declarations in 9+ files) MUST be brought up to the new standard. No exemption. FR-8 of the `audit-findings-remediation-r1` PRD owns this work.

Rationale for no grandfathering: an exemption creates two classes of marker (justified / legacy), degrading the discipline's integrity over time. The cost of retroactive upgrade is bounded (~20 files) and one-time.

## Consequences

### Positive

- **Closes the silent-suppression vector.** A marker without justification is now an audit error, not a free pass. Authors must articulate WHY each marker is appropriate; future maintainers can read the WHY without re-litigating the disposition.
- **Aligns with cross-ecosystem best practice.** T-001's 5-ecosystem survey converges on this pattern; the project is adopting what mature tools recommend (and what 3 of those tools have open feature requests to enforce).
- **Defense in depth.** Auditor + reviewer enforcement means the discipline holds even when one path is bypassed.
- **Machine-parseable justification text.** The `--` separator allows future tooling (unused-marker detection; justification-quality analysis; periodic audit-of-justifications mode).
- **Aligns with ADR-0029 (no-silent-scope-changes).** Mechanism α IS a no-silent-failure mechanism applied at the marker level; ADR-0029 is the same principle applied at the stage level. Symmetric discipline.

### Negative

- **Authoring friction.** Every new marker requires a thought-out sentence. For genuine pedagogical content the author already has the explanation in mind; for rote markers the friction is the point.
- **Justification quality cannot be machine-verified perfectly.** The substance rule is loose (keyword presence). An author determined to game the discipline can write "documents the auditor pattern" verbatim 20 times. Mitigation: Cross-Artifact Audit sample-checks (per Synthesis surfacing item 3); future periodic justification-quality review.
- **Retroactive upgrade is real work.** ~20 existing markers across the project need justification text. Bounded but non-zero. In scope for `audit-findings-remediation-r1` FR-8.

### Forward implications

- **Spec authoring:** A new file `KB-documentation-criteria/references/pedagogical-marker-justification-spec.md` codifies the syntactic forms, validity rules, and extension procedure. Authored under FR-7-a of `audit-findings-remediation-r1`.
- **Auditor changes:** `pedagogical_marker_check.py` gains the validity-rule check. Uniform enforcement across all 3 audit paths is the prerequisite (FR-12 + ADR-0031).
- **Future enhancement:** ESLint's `eslint-comments/no-unused-disable` analog — detect markers that don't correspond to any current finding (auto-cleanup). Out of scope for current feature; queued for v4.7.0 candidate.

## Alternatives considered

### Alternative 1 — Mechanism β: post-hoc validator that flags rote patterns

A new audit check would sample N markers per file and use heuristics (similarity of justifications, presence of named reason, etc.) to flag suspicious patterns. Issued as MAJOR, not BLOCKER.

**Rejected** because:
- Post-hoc; mechanism α blocks bad patterns at scan time (strictly stronger)
- Heuristics for "suspicious pattern" are hard to specify precisely; false-positive rate would erode trust in the check
- Doesn't prevent an individual rote marker from passing; mechanism α does

### Alternative 2 — Mechanism γ: feature-scoped ADR required for each marker disposition

Every marker addition requires a feature-scoped ADR justifying why the disposition is appropriate.

**Rejected** because:
- ADRs are for cross-cutting strategic decisions, not tactical single-file dispositions
- Cost prohibitive — would dwarf the actual content work
- Creates two-tier ADR namespace (strategic vs tactical) that degrades ADR discoverability

### Alternative 3 — Grandfather existing markers

Apply mechanism α to new markers only; leave the ~20 existing markers untouched.

**Rejected** because:
- Creates two-tier marker namespace (justified / legacy)
- Discipline integrity degrades over time as the legacy class grows or persists
- Cost of retroactive upgrade is bounded (one-time, ~20 files) and known
- User intent constraint 7 (in `audit-findings-remediation-r1` intent) explicitly forbids

### Alternative 4 — Opt-in enforcement (match ecosystem default)

All 5 surveyed ecosystems make justification enforcement opt-in. The project could too — ship the spec, add a config flag, default off.

**Rejected** because:
- The opt-in default is exactly what causes the failure mode we're trying to prevent (Pylint's 10-year-old open issue; Bandit's open feature request)
- The project is small enough that opt-in / opt-out has no meaningful migration cost; default-on is just as easy
- Aligns with user intent constraint ("nothing should be silent") more cleanly than opt-in

## Notes

This ADR was authored at Stage 7 (Design Composition) of the `audit-findings-remediation-r1` feature run. The decision-substance was framed during intent clarification and PRD authoring; this ADR records the cross-cutting policy in a discoverable, durable location.

The mechanism-α name was assigned during intent refinement because three alternatives (β, γ, plus the rejected opt-in default) were under consideration. The Greek-letter convention is informal and unique to this feature; future cross-cutting marker policies need not use it.

T-001's external research is summarized in the per-feature `research-notes/T-001.md` and is the primary evidence base for the design choices above.
