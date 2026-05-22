# Cross-Artifact Audit — CMC + Diff-Mode + Convergence

## Contents

- When this runs
- The three techniques in combination
- Posture 1 — CMC (Cross-Model Critique)
- Posture 2 — Diff-Mode Input
- Posture 3 — Convergence-Based Termination
- Output JSON
- Iteration with finalize-reconciler
- Anti-patterns specific to Cross-Artifact Audit
- When NOT to apply this discipline

The cross-artifact consistency discipline used by `review-cross-artifact-auditor` during the Cross-Artifact Audit phase of the feature-pipeline. Verifies that the Blueprint, Plan, Acceptance Tests, and Phase Validators all tell the same story.

## When this runs

The Cross-Artifact Audit pass runs after:

- the Architecture Audit verdict is `approved` or `approved_with_conditions`
- Plan Authoring (`plan-author`) produced the Plan
- Acceptance Test Authoring (`test-acceptance-author`) and Phase Validator Authoring (`test-phase-validator`) produced acceptance tests and phase validators

It iterates with `finalize-reconciler` (Reconciliation) when issues need resolution. Same four-cycle hard cap as the Architecture Audit.

## The three techniques in combination

CMC + diff-mode + convergence is one auditor running with three deliberate postures, not three separate audits.

```
Inputs: Blueprint diff (vN vs vN-1), Plan, ACs, Phase validators, prior-round critique
            │
            ▼
    ┌──────────────────────────────────────┐
    │  Posture 1: CMC (cross-model)        │
    │  Posture 2: Diff-mode (limited ctx)  │
    │  Posture 3: Convergence termination  │
    └──────────────────────────────────────┘
            │
            ▼
   Single issues array + verdict + convergence signal
```

## Posture 1 — CMC (Cross-Model Critique)

**Goal:** see the cross-artifact consistency through a model different from the one that authored the Blueprint and Plan.

### Frontmatter declaration

`review-cross-artifact-auditor.md` declares `model: opus` in its frontmatter when the main agent is Sonnet (and vice versa). This is part of the subagent definition, not runtime. The auditor's sub-agent file explicitly says:

```yaml
model: opus  # cross-model posture; main agent is typically Sonnet
```

If the main agent is already Opus, declare `model: sonnet`. The principle: the auditor uses a different model family than the document authors, so it sees consistency through a different optimization landscape.

### Why this matters

Same-model critique tends to smooth over its own systematic biases. A model that wrote the Blueprint will be likelier to read past inconsistencies it would have introduced. Cross-model critique catches more — at the cost of some model-mismatch noise (one model may flag stylistic differences the other accepts; these are filtered by severity).

### What CMC checks

Cross-artifact consistency, specifically:

| Pair | Consistency check |
|---|---|
| Blueprint ↔ PRD | Functional requirements in PRD all have corresponding ACs in Blueprint; NFRs preserved; layer scope aligned |
| Blueprint ↔ Plan | Every Blueprint AC maps to one or more Plan tasks; every Plan task references a Blueprint section; phase ordering matches Implementation Plan |
| Plan ↔ Tests | Every Plan task has at least one acceptance test (EARS-format); every test has a phase-validator trigger |
| Tests ↔ Phase Validators | Phase Validator can detect failure of every test in its phase; no orphan tests |
| Cross-document numbers | Performance numbers, retention windows, rate limits, etc. agree across all four documents |
| Cross-document terminology | Same entity/term used consistently (e.g. "User" not also "Customer" not also "Account" without explanation) |

## Posture 2 — Diff-Mode Input

**Goal:** prevent the auditor from accumulating context across iterations, which would let it silently smooth over real inconsistencies.

### What "diff-mode" means

The auditor receives:

- **Blueprint diff** v(N) vs v(N-1) — only the lines that changed
- **Full Plan v(N)** (Plan is typically smaller than Blueprint)
- **Full Tests v(N)**
- **Full Phase Validators v(N)**
- **Prior round's critique JSON** — not the prior round's Blueprint
- **Issues-ledger entries** for category `cross_artifact`

NOT included:
- Full Blueprint
- Synthesis claims (those were the Architecture Audit's input)
- Codebase analysis (the Design phase/6 territory)
- Rationale brief (referenced by ID only; auditor doesn't load it)

### Why deliberate input limitation

If the auditor sees the full Blueprint every iteration, two failure modes accumulate:

1. **Anchor effect:** the auditor remembers reading "this is fine" in iteration 1 and reads past the same passage in iteration 4 even after it changed
2. **Context bloat:** by iteration 4 the auditor has 4× the context, with diminishing per-iteration discrimination

Diff-mode forces the auditor to re-evaluate only the changes, which is cheaper AND less anchored.

### What the auditor cannot do in diff-mode

- Make claims about parts of the Blueprint that didn't change in this iteration (must qualify any such observation as "from prior critique" with reference to the prior issue ID)
- Re-litigate decisions resolved in prior iterations (the Architecture Audit's brief-honor lens handles re-surfacing; the Cross-Artifact Audit trusts that resolution unless the diff explicitly reopens it)

### What the auditor CAN do

- Verify the diff itself for cross-artifact consistency
- Check that Plan/Tests/Phase Validators reflect any cross-cutting changes in the diff
- Surface convergence concerns (see below)

## Posture 3 — Convergence-Based Termination

**Goal:** halt the iteration loop when issues stop changing meaningfully, not just when no new ones appear.

### Iteration accounting

Each invocation of this pass records:

- `iteration_number` (1, 2, 3, or 4)
- `issues_new` — issues raised this iteration that did not exist last iteration
- `issues_resurfaced` — issues that were resolved in a prior iteration and re-appear (with reference to prior ID)
- `issues_resolved` — prior-iteration issues that this iteration confirms resolved
- `issues_persisting` — prior-iteration issues still unresolved

### Convergence signals

Four signals indicate convergence and warrant `verdict: approved`:

1. `issues_new = 0` AND `issues_persisting ≤ 2 recommended` → approved
2. `issues_new = 0` AND `issues_persisting` has all-recommended-severity → approved
3. `issues_new = 0` AND `issues_resurfaced = 0` two iterations in a row → approved
4. Iteration 4 reached AND `issues_resolved > issues_new` (more is getting fixed than added) → approved_with_conditions, escalate to user

### Divergence signals — escalate to user

- Iteration 4 reached AND `issues_new > issues_resolved` → halt, surface to user; the design is not converging
- Same `important` or `critical` issue persists across 3 iterations → halt, surface to user
- `issues_resurfaced > 0` two iterations in a row → halt; prior-context-check is failing (see `prior-context-check.md` for debugging)

### Four-cycle hard cap

Regardless of signals, iteration count cannot exceed 4. At iteration 4 the auditor MUST emit a final verdict and the orchestrator MUST present to user. No fifth iteration.

Per ADR-0006 §invocation-budget, the four-cycle cap is non-negotiable across the pipeline.

## Output JSON

Per the standard reviewer output protocol. Issue IDs use prefix `CA` (cross-artifact):

```json
{
  "metadata": {
    "stage": 9,
    "auditor": "review-cross-artifact-auditor",
    "model_posture": "opus" | "sonnet",
    "iteration_number": 1 | 2 | 3 | 4,
    "input_mode": "diff",
    "blueprint_diff_lines": 142,
    "convergence": {
      "issues_new": N,
      "issues_resurfaced": N,
      "issues_resolved": N,
      "issues_persisting": N,
      "signal": "converged" | "diverging" | "in_progress"
    }
  },
  "verdict": {"decision": "approved_with_conditions"},
  "issues": [
    {"id": "I-CA-NNN", "severity": "important", "category": "consistency", "artifact_pair": "Blueprint ↔ Plan", ...}
  ],
  "prior_context_check": {...}
}
```

The `artifact_pair` field is auditor-specific and identifies which two artifacts the issue spans.

## Iteration with finalize-reconciler

Issues with severity `critical` or `important` route to `finalize-reconciler` (Reconciliation), which dispatches to `plan-author` (for Plan issues), the relevant test author (for Test/Phase-Validator issues), or `design-composer` (for cross-cutting Blueprint issues). The revised artifacts go back to Cross-Artifact Audit.

## Anti-patterns specific to Cross-Artifact Audit

- **Re-running architecture-audit checks** — those are architecture audits, not cross-artifact audits. the Cross-Artifact Audit trusts the Architecture Audit's verdict and focuses on artifact-pair consistency.
- **Failing the document for prose style** — Gate 1 (Design Composition reviewer) handles clarity. Cross-Artifact Audit should only flag style when it causes a cross-artifact misunderstanding.
- **Accumulating context across iterations** — by design, diff-mode prevents this. If the auditor finds itself wanting to re-read the full Blueprint, that's a signal something's wrong with the diff input.

## When NOT to apply this discipline

- Design Composition — Gate 0/1, not cross-artifact
- Architecture Audit — architecture audit, different lens
- Initial PRD/Blueprint/Plan/Tests authoring — the artifacts must exist before they can be cross-audited
