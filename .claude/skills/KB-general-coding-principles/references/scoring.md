# Scoring Rubric — Design-Time Code Samples

## Contents

- How scoring works
- The 10 dimensions
- How designers self-check
- How `shared-document-reviewer` scores

The 10-dimension scoring used by `shared-document-reviewer` Gate 1 and by per-layer designers self-checking their own output before handoff.

## How scoring works

Each dimension scores 0–10. The total is the sum (max 100). Weights are equal — there is no dimension worth double. Equal weighting is deliberate: in design-sample evaluation, a single failed dimension can break the whole illustration (e.g. fabricated API), so weighting one over another would create false confidence.

| Total score | Verdict band | Reviewer action |
|---|---|---|
| 95–100 | Exemplar | Pass; quote in any related "good example" reference |
| 80–94 | Pass | Approved; minor notes optional |
| 60–79 | Pass with conditions | One `important` issue; fix-then-approve |
| 40–59 | Needs revision | Multiple `important` issues OR one `critical` |
| 0–39 | Reject | Rewrite required; do not iterate |

Auto-fail bypasses bands entirely — see SKILL.md "non-negotiables."

## The 10 dimensions

### 1. Names match contract (0–10)

The function names, type names, and variable names in the code sample correspond to the names used in the prose of the same section. If the prose says "the `OrderRepository.findActive` method," the sample shows `OrderRepository.findActive`, not `OrderRepo.getActiveOrders`.

Scoring:
- 10: every name in sample appears in prose, and vice versa for prose names that are illustrated
- 7–9: minor naming drift (case, abbreviation) but contract is recoverable
- 4–6: at least one name in sample is unfamiliar from prose; reader has to guess
- 0–3: substantial naming mismatch between sample and prose

### 2. Types are explicit (0–10)

In typed languages, signatures show types for arguments and return. In dynamic languages, type expectations are stated in comments or a docstring. Ambiguous types (`any`, `object`, untyped `dict`) named explicitly and justified.

### 3. Error contract visible (0–10)

The sample makes clear how errors flow. Three accepted patterns:

- explicit error type in return position (Rust `Result`, Go `(T, error)`, etc.)
- typed exception(s) raised, named in a `throws`/`raises` annotation or comment
- documented error sentinel value with the prose explaining its meaning

A sample that silently does `try { ... } catch { /* nothing */ }` is dimension-3 zero unless the prose explicitly defends swallowing.

### 4. No fabricated APIs (0–10)

This is the dimension that turns into auto-fail if the violation is severe (see SKILL.md). Soft scoring:

- 10: every external call cites a real, current method on its library
- 7–9: one call uses a deprecated-but-real method; should update
- 4–6: one call uses a method that exists in a different library with the same name (cross-contamination)
- 0–3: at least one call hits no real method (auto-fail territory)

Verification protocol in `fabricated-api-detection.md`.

### 5. No copy-pasted secrets (0–10)

Auto-fail on real credentials per SKILL.md. Soft scoring for the cases that are close:

- 10: no credential-shaped strings at all
- 7–9: placeholder strings that look like placeholders (`<YOUR_TOKEN>`, `***`, `xxx`)
- 4–6: placeholder strings that LOOK realistic but are confirmed-fake (e.g. `ghp_aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa`)
- 0–3: realistic credential shapes (auto-fail territory)

### 6. No hidden control flow (0–10)

Reflection, dynamic dispatch, monkey-patching, `eval`, exec-via-string, conditional imports that change behavior — any of these is a control-flow shortcut that hides what runs. Acceptable in production code; misleading in a design sample. Scoring:

- 10: every line's effect is visible
- 7–9: one piece of dynamic behavior, called out with a comment
- 4–6: dynamic behavior without a comment
- 0–3: multiple layers of dynamic behavior (sample is unreadable as illustration)

### 7. Idempotency stated (0–10)

Only applies to samples showing state-changing operations (writes, deletes, external calls). Read-only samples score 10 by default.

State-changing samples need an explicit posture: `// idempotent: same input → same outcome`, `// not idempotent; caller must dedupe`, or `// idempotency unspecified — out of scope here`.

### 8. Concurrency posture stated (0–10)

Only applies to samples where two callers could plausibly run at once. Single-caller samples score 10.

Multi-caller samples need a posture: transactional, locked, optimistic, or "single-writer assumed."

### 9. Language matches project (0–10)

The sample's language matches the layer's stack as discovered by `discovery-codebase-researcher` (during Discovery Research). Mismatch is acceptable only when accompanied by a comment justifying the divergence (e.g. "shown in TypeScript for cross-layer consistency; final Python implementation will follow").

### 10. Sample is minimal (0–10)

One code block ≤ 40 lines, or split into named blocks each ≤ 40 lines with prose between. Long unbroken samples are dimension-10 zero — break them.

Rationale: a reader's eye refocuses every 30–50 lines. Anything longer crosses that boundary and stops being a sample, starts being a draft implementation.

## How designers self-check

Before writing the design block, the per-layer designer runs the rubric mentally:

```
For each dimension 1–10:
  - Identify how this sample addresses it
  - If unaddressed and applicable, fix before emitting
  - If unaddressed and N/A, note inline (e.g. "concurrency: N/A — read-only path")
```

This avoids the failure mode where the reviewer's Gate 1 surfaces issues the designer could have caught.

## How `shared-document-reviewer` scores

Reviewer treats each code block independently. Block scores aggregate to a document-level "implementation samples" score that feeds the `scores.rule_compliance` field in the output JSON (per the shared-document-reviewer template). A single dimension-4 auto-fail in any block fails the whole document.
