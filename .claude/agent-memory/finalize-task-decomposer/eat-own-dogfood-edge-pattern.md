---
name: eat-own-dogfood-edge-pattern
description: When a pipeline run's contracts self-apply, dogfood-deliverable tasks must depend on the contract-realization tasks but NOT on the contract's audit task (the audit runs against the dogfood output at rollout, not before authoring).
metadata:
  type: feedback
---

When a pipeline run ships contracts that self-apply (eat-own-dogfood), the dogfood-deliverable task must depend on the contract-establishment tasks (template + procedure + predicate authoring) but should NOT depend on the contract's audit/validator task. The audit task takes the dogfood output as INPUT at rollout time.

Concrete pattern from R2a (pipeline-design-time-discipline-r1):
- T5.1 (matrix template) + T5.2 (advisory predicate) + T5.3 (design-cc procedure) → T8.1 (this run's matrix)
- T7.1 (SA-14 audit script) is created independently and runs T8.1's output at T9.1 (rollout)
- Putting T7.1 → T8.1 would make the audit a precondition rather than a validator

**Why:** The pipeline ships the audit, exercises the audit on its own deliverable, and the resulting pass IS the dogfood validation event (per the Plan's I-AA-007 closure semantics).

**How to apply:** When you see "this run produces its own X to validate the X contract," the deliverable task depends on the contract-author tasks; the contract-audit task depends on the deliverable; the audit invocation is a separate downstream rollout task.
