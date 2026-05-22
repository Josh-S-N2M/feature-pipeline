# Severity Taxonomy

## Contents

- The three values
- How severity interacts with verdict
- When to use `critical` vs `important`
- Category dimension (separate from severity)
- Severity inflation: how to avoid it
- Severity downgrade rules
- Severity upgrade rules
- Threshold mapping reference (canonical)

Three severity values, used identically by all three reviewers. This file is the canonical source for severity definitions and the score-to-verdict mapping.

## The three values

| Value | Use when... | Example |
|---|---|---|
| `critical` | The issue blocks acceptance. Architecturally wrong, security-breaking, contract violation, or fundamentally infeasible. Cannot be deferred or accepted with conditions — must be fixed. | Real credential in a sample; fabricated API call; AC contradicts an FR; Gate 0 structural failure |
| `important` | The issue should be fixed before approval but isn't architecturally fatal. Degrades the score. Can be deferred only with explicit user approval and a tracked ledger entry. | Missing dependency declaration; ambiguous error contract; cross-artifact terminology mismatch; missing N/A justification on an out-of-scope section |
| `recommended` | Improvement suggestion. Non-blocking. Documents are approvable with `recommended` issues outstanding. | Clarity polish; alternative formulation; forward-link suggestion; stylistic improvement |

## How severity interacts with verdict

Verdict (`approved` / `approved_with_conditions` / `needs_revision` / `rejected`) is determined by severity counts and quality scores TOGETHER, per the mapping below.

| Severity present | Quality scores | Verdict |
|---|---|---|
| Any `critical` | Any | `needs_revision` (or `rejected` for fundamental problems) |
| No `critical`; `important` only; small count | Consistency > 80 AND Completeness > 75 AND no rule violations of high severity | `approved_with_conditions` |
| No `critical`; only `recommended` | Consistency > 90 AND Completeness > 85 AND no rule violations | `approved` |
| Many `critical` issues; fundamental rework needed | Any | `rejected` |

A reviewer cannot override this mapping. If the issue counts and scores indicate `needs_revision`, the verdict is `needs_revision` regardless of the reviewer's overall impression.

## When to use `critical` vs `important`

The line: "would I refuse to merge a PR with this issue?"

- Yes → `critical`
- "I'd merge it but file a follow-up ticket" → `important`
- "I'd merge it; the follow-up is optional" → `recommended`

Common false-`critical` patterns:

- "This style is wrong" — not critical unless it violates an explicit project rule. Usually `recommended`.
- "I'd have done this differently" — preference, not a defect. `recommended` or omit.
- "This is technically correct but suboptimal" — `important` or `recommended`, never `critical`.

Common under-severity patterns:

- "There's a typo in a function name in the sample" — if the function name is referenced elsewhere in the doc with the correct spelling, that's a `critical` consistency violation, not a typo. Reader cannot tell which is canonical.
- "The Layer Scope says Frontend is in scope but no Frontend AC exists" — `critical` completeness, not `important`. A scoped layer with no AC will silently get no per-layer Design designer.

## Category dimension (separate from severity)

Each issue ALSO has a category — what kind of issue, not how bad. Five values:

| Category | Meaning |
|---|---|
| `consistency` | Document contradicts itself or another document |
| `completeness` | Required element missing or insufficiently developed |
| `compliance` | Violates a project rule, template requirement, or KB convention |
| `clarity` | Document is ambiguous or hard to act on |
| `feasibility` | Technical or resource concerns about the proposal |

Severity and category are independent — you can have a `recommended/clarity` issue (e.g. suggesting better section title) and a `critical/consistency` issue (e.g. AC contradicts FR) in the same document.

## Severity inflation: how to avoid it

A reviewer who marks everything `critical` produces unactionable output. The orchestrator sees 27 critical issues and has no way to prioritize. Calibration anchors:

- **`critical` budget per document review:** at most 5. If more issues qualify, the document is likely fundamentally broken — emit `rejected` and stop.
- **`important` budget per document review:** at most 15. More than 15 important issues suggests the document needs `needs_revision` regardless of severity.
- **`recommended`:** no budget, but cluster related recommendations (one issue saying "five terminology improvements" is better than five separate issues).

These are calibration targets, not hard limits. Exceptional documents may warrant more issues; the budget is a sanity check.

## Severity downgrade rules

Auditors MAY downgrade a severity when:

1. The issue is mitigated elsewhere in the document (e.g. an `important` consistency issue is downgraded to `recommended` if a later section reconciles it explicitly)
2. The issue is bounded by an existing ADR or open item that captures the followup
3. The user has explicitly accepted the deviation in the rationale brief

Auditors MUST NOT downgrade when:

- The issue is one of the three auto-fail conditions in KB-general-coding-principles (real credentials, fabricated API, naked production URL)
- The issue is a Gate 0 structural failure
- The issue contradicts a user-confirmed decision in the rationale brief

## Severity upgrade rules

Auditors MAY upgrade a severity when:

1. The issue interacts with an unresolved prior issue, making both more serious in combination
2. The issue blocks a downstream layer or stage that's already started work
3. The issue affects external consumers (other teams, partners, end users)

Each upgrade or downgrade is recorded in the issue's `severity_history` field if the reviewer adjusted from the auto-derived value.

## Threshold mapping reference (canonical)

For convenience, the score→verdict mapping from the shared-document-reviewer template, restated here:

```
APPROVED
  Gate 0: all pass
  Consistency > 90
  Completeness > 85
  Rule compliance: no severity:high
  Issues: no `critical`
  Prior context: all critical/major resolved

APPROVED_WITH_CONDITIONS
  Gate 0: all pass
  Consistency > 80
  Completeness > 75
  Rule compliance: only severity:medium or below
  Issues: only easily-fixable
  Prior context: at most 1 important unresolved

NEEDS_REVISION
  Gate 0: any fail OR
  Consistency < 80 OR
  Completeness < 75 OR
  Rule compliance: any severity:high OR
  Issues: any `critical`, or many `important` OR
  Prior context: 2+ important unresolved OR any critical unresolved OR
  complexity_level medium/high but complexity_rationale insufficient

REJECTED
  Fundamental problems
  Requirements not met
  Major rework needed
```

All three reviewers share this mapping. The architecture and cross-artifact auditors typically don't score `clarity` (their concern is correctness, not prose), so their score totals weight consistency, completeness, and rule compliance more heavily.
