# Prior Context Check

## Contents

- Why this step exists
- Procedure
- Prior context (issues from previous iterations)
- Output schema
- Interaction with the main issue list
- Why this matters for convergence
- Common failure modes
- Time budget
- What prior-context-check does NOT do

The mandatory step every reviewer runs before its main checks on iteration N ≥ 2. Defined in the `shared-document-reviewer-template.md` as Step 0 ("Input Context Analysis") and applied identically by `review-architecture-auditor` and `review-cross-artifact-auditor`.

## Why this step exists

Without prior-context check, reviewers re-surface issues that were already resolved. This produces iteration loops where the same issue is raised, fixed, then raised again. By the time the loop is detected, multiple cycles have been wasted.

The check is cheap (≤30 seconds typical) and prevents the most common iteration pathology.

## Procedure

### Step 0a: Scan the invocation prompt for prior context

The orchestrator includes prior-iteration open issues in the prompt under a section header like:

```
## Prior context (issues from previous iterations)
```

Or as a structured JSON block. The reviewer's first job is to parse this.

### Step 0b: Extract actionable items

For each prior-context item, normalize to:

```json
{
  "id": "I-DR-005",
  "description": "...",
  "location": "Blueprint § ...",
  "severity": "important"
}
```

Record the count as `prior_context_count: N` for the output JSON.

### Step 0c: Record before proceeding

The reviewer notes `prior_context_count` and the list of items in its working state. The main checks (Gate 1, CoVe, CMC, etc.) run after, but the check itself happens at the end before output.

### Step 4 of the reviewer flow: Resolution Classification

After main checks, for each prior-context item:

1. **Locate the referenced section** in the current document
2. **Read what's there now** — is the issue addressed?
3. **Classify** into one of:

| Classification | Criterion |
|---|---|
| `resolved` | The issue's specific concern is fully addressed in the current artifact. No follow-up needed. |
| `partially_resolved` | Some but not all of the issue's concern is addressed. Specify what remains. |
| `unresolved` | The issue is not addressed in the current artifact, OR is addressed in a way that introduces a new concern (which gets a new issue ID). |

4. **Record evidence** — what specifically in the current document confirms the classification

## Output schema

Include the `prior_context_check` block in the output JSON when `prior_context_count > 0`:

```json
{
  "prior_context_check": {
    "items_received": 3,
    "resolved": 2,
    "partially_resolved": 1,
    "unresolved": 0,
    "items": [
      {
        "id": "I-DR-005",
        "status": "resolved",
        "location": "Blueprint § Backend Design para 4",
        "evidence": "Names now consistent — `OrderService` used in both Backend Design and Architecture Overview."
      },
      {
        "id": "I-AA-003",
        "status": "partially_resolved",
        "location": "Blueprint § Implementation Plan",
        "evidence": "Phase ordering updated, but the new Phase 2 still depends on Phase 4 (circular).",
        "remaining": "Resolve the Phase 2 → Phase 4 dependency."
      }
    ]
  }
}
```

If `prior_context_count = 0`, include the block with `items: []` for traceability:

```json
{
  "prior_context_check": {
    "items_received": 0,
    "resolved": 0,
    "partially_resolved": 0,
    "unresolved": 0,
    "items": []
  }
}
```

## Interaction with the main issue list

The prior-context-check is SEPARATE from the main `issues` array in the output. Items that are `resolved` or `partially_resolved` do NOT re-appear in `issues`. Items that are `unresolved` go in BOTH:

- `prior_context_check.items[*]` with `status: "unresolved"`
- `issues[*]` with the same `id` (the existing ID, not a new one) and updated description

This ensures the orchestrator knows to keep the same ledger entry rather than creating a duplicate.

## Why this matters for convergence

The cross-artifact auditor's convergence-based termination (Cross-Artifact Audit) depends on accurate prior-context tracking. If a reviewer skips this check or misclassifies items:

- `issues_resolved` count is wrong → convergence signal misfires
- `issues_resurfaced` count is wrong → divergence isn't detected
- Iteration loop continues until 4-cycle hard cap, then surfaces to user with stale information

## Common failure modes

### Failure mode 1: Skipping the check entirely

Symptom: every iteration's `issues` array contains the same items with new IDs.

Cause: reviewer didn't run Step 0 / Step 4. Probably treated prior context as just text in the prompt and ignored it.

Fix: Step 0 is MANDATORY — reviewer self-validates this before emitting output (`Step 5: Self-Validation` in the template).

### Failure mode 2: Lazy classification (everything marked `resolved`)

Symptom: prior context shows all-resolved but the same issues re-appear next iteration.

Cause: reviewer didn't actually verify resolution — just trusted that the document was iterated upon.

Fix: the classification REQUIRES evidence. An item with `status: "resolved"` and empty or generic evidence ("issue addressed in iteration 3") is a failure of this step. Specific evidence is required.

### Failure mode 3: Strict classification (everything marked `unresolved`)

Symptom: prior context shows all-unresolved even though the diff shows changes addressing them.

Cause: reviewer is conservative — flags as `unresolved` anything it can't strongly verify.

Fix: `partially_resolved` exists for the in-between case. Use it.

### Failure mode 4: New issues get prior IDs

Symptom: ledger has duplicate IDs because the reviewer re-used an existing ID for a different concern.

Cause: reviewer matched an issue by topic similarity rather than by the prior-context list.

Fix: only re-use an existing ID for items that appear in the prior-context list. New concerns — even if related — get fresh IDs.

## Time budget

Prior-context check should be ≤ 30 seconds for a typical N-iteration handoff (3–10 prior items). If a reviewer is spending more than 2 minutes on this step, it's either:

- Re-reading prior context that wasn't sent (failure mode 5: ignoring the list, doing it manually)
- Treating the check as a substantive re-audit (failure mode 6: overscoping)

In either case, surface the issue with the orchestrator's prompt construction — the prior-context format may need adjustment.

## What prior-context-check does NOT do

- It does not surface NEW issues — that's Gate 1 / CoVe / CMC
- It does not re-audit resolved items — they're trusted past `resolved`
- It does not write to the ledger — the orchestrator handles ledger updates based on the output

The check is strictly about classification of what came in, plus producing the `prior_context_check` output block.
