# Issue Lifecycle (per ADR-0008)

## Contents

- The issue identifier
- The ledger record
- Lifecycle states
- Transitions
- How reviewers interact with the ledger
- Prior context (issues from previous iterations)
- Cross-referencing related issues
- Issue ledger and `wontfix-with-rationale`
- Persistence across pipeline sessions
- What to NOT track in the issues-ledger

How issues are created, tracked, resolved, and superseded across the feature-pipeline's iterations. The issues-ledger discipline from ADR-0008, applied to the three reviewers.

## The issue identifier

Every issue has a stable ID of the form `I-<prefix>-NNN`:

| Prefix | Source |
|---|---|
| `DR` | `shared-document-reviewer` |
| `AA` | `review-architecture-auditor` |
| `CA` | `review-cross-artifact-auditor` |

`NNN` is zero-padded three-digit, monotonically incrementing per-feature within each prefix. The orchestrator assigns the next number when the issue is first written to the ledger.

Examples seen in v4.3.0 review verdicts:

- `I-DR-005`, `I-DR-006` — surfaced by shared-document-reviewer
- `I-AA-004`, `I-AA-005` — surfaced by review-architecture-auditor
- `I-CA-002`, `I-CA-003` — surfaced by review-cross-artifact-auditor

## The ledger record

The issues-ledger lives at `working/feature/<slug>/issues-ledger.json` for the feature. Each issue is one record:

```json
{
  "id": "I-DR-007",
  "feature_slug": "add-healthz-endpoint",
  "first_seen": {
    "stage": "Design Composition",
    "iteration": 1,
    "reviewer": "shared-document-reviewer",
    "timestamp": "2026-05-20T14:23:11Z"
  },
  "current_status": "open",
  "severity": "important",
  "category": "consistency",
  "location": "Blueprint § Backend Design para 4",
  "description": "Backend Design references `OrderService` but Architecture Overview uses `OrdersHandler`. Same component, two names.",
  "suggestion": "Pick one name; update the other section.",
  "history": [
    {"iteration": 1, "status": "open", "severity": "important"},
    {"iteration": 2, "status": "open", "severity": "important", "note": "Not addressed in iteration 2 diff"}
  ],
  "resolution": null
}
```

When the issue is resolved:

```json
{
  "current_status": "resolved",
  "resolution": {
    "iteration": 3,
    "method": "design-composer renamed to `OrderService` throughout",
    "verified_by": "shared-document-reviewer",
    "timestamp": "2026-05-20T15:01:42Z"
  },
  "history": [
    ...,
    {"iteration": 3, "status": "resolved", "severity": "important", "note": "Rename applied; reviewer confirmed"}
  ]
}
```

## Lifecycle states

| Status | Meaning | Set by |
|---|---|---|
| `open` | Issue is active; needs resolution | Reviewer that surfaces it |
| `resolved` | Issue is fixed; reviewer confirmed | Reviewer at iteration N+1 after fix at iteration N |
| `wontfix-with-rationale` | Issue acknowledged but deliberately not fixed; rationale recorded | User (via orchestrator AskUserQuestion) only |
| `superseded` | Issue replaced by a different one (typically because the underlying design changed) | Reviewer; references the superseding issue ID |

`wontfix-with-rationale` requires user approval — a reviewer alone cannot move an issue to this status. The orchestrator surfaces the issue to user, captures the rationale, and updates the ledger.

## Transitions

```
                ┌────────────┐
   created  ───►│    open    │───► resolved
                └────────────┘     (terminal)
                       │
                       ├────────► wontfix-with-rationale (user-approved)
                       │           (terminal)
                       │
                       └────────► superseded (by issue I-XX-NNN)
                                   (terminal)
```

No transition out of any terminal state. If a "resolved" issue re-appears, it gets a NEW ID — and the reviewer must reference the prior ID as `references_prior: I-XX-NNN` in the new issue. This is the re-surfaced verified issue Lens-3 brief-honor check catches.

## How reviewers interact with the ledger

### When invoking a reviewer

The orchestrator passes prior-iteration open issues as `prior_context` in the invocation prompt:

```
## Prior context (issues from previous iterations)

The following issues were open at the end of iteration N-1. Please check whether
each has been addressed in the current iteration's artifact:

- I-DR-005 (important, consistency): [description]; suggestion: [...]
- I-AA-003 (important, completeness): [description]; suggestion: [...]
```

The reviewer runs the prior_context_check per `prior-context-check.md` and includes the result in its output JSON.

### When the reviewer emits issues

Each issue in the output JSON has either:

- No `id` field — a NEW issue; orchestrator assigns next ID and writes to ledger
- An existing `id` field with `references_prior` — a re-surfaced previously-resolved issue; orchestrator creates a NEW record with a NEW ID and notes the reference

### When the orchestrator writes to the ledger

After each reviewer pass:

1. For new issues (no ID): assign `I-<prefix>-NNN` (next available); write record with `first_seen` populated
2. For existing-ID issues that the reviewer says are resolved: update `current_status`, populate `resolution`
3. For existing-ID issues the reviewer says are still open: append to `history` array; do not duplicate the record
4. For re-surfaced issues with `references_prior`: create new record; add cross-reference to prior

## Cross-referencing related issues

When two issues are related but distinct, link them via `related_issues: [I-XX-NNN, ...]` in the record. Common cases:

- Two issues with the same root cause (one in Blueprint, one in Plan)
- A `critical` issue that turned into multiple `important` issues after partial fix
- A re-surfaced issue (`references_prior: I-XX-NNN`)

Cross-references are for downstream consumers (`finalize-reconciler`, user-facing reports). They do not affect verdict.

## Issue ledger and `wontfix-with-rationale`

When a reviewer surfaces an issue that user has previously deferred:

- The reviewer DOES re-surface (it doesn't know about user's prior wontfix decision)
- The orchestrator detects the match (by description similarity or explicit `references_prior`)
- The orchestrator skips re-asking the user; reuses the prior wontfix rationale
- The issue gets `current_status: wontfix-with-rationale` automatically

If the underlying design has changed such that the issue now matters again, the reviewer can flag this explicitly with `requests_user_re_review: true` in the issue, and the orchestrator surfaces it to user.

## Persistence across pipeline sessions

The issues-ledger is per-feature, not per-session. If the user resumes the pipeline mid-iteration in a new session, the ledger is loaded from disk. Issue IDs are stable across sessions.

If the user starts a fresh pipeline run for the same feature-slug, the orchestrator (per ADR-0005's append-only supersession) archives the prior ledger and starts a new one. Prior IDs are NOT reused; if a new run surfaces a similar-looking issue, it gets a fresh ID.

## What to NOT track in the issues-ledger

- Open items in the rationale brief — those are forward-looking decisions, not defects. Tracked in the rationale brief itself.
- Pending TODO comments in code samples — those are documented in the document, not the ledger
- User decisions and approvals — those are captured in the rationale brief and the orchestrator's session state

The ledger is strictly for reviewer-surfaced defects. Mixing in other concerns dilutes its discrimination.
