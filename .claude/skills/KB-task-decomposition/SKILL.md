---
name: kb-task-decomposition
description: >-
  Discipline for translating an approved Plan into a tasks.json DAG during
  the Task Decomposition stage. Covers task identification, dependency edge
  inference, work-unit sizing, parallelizability detection, the canonical
  tasks.json schema, and quality criteria for a DAG that can drive automated
  execution. Loaded by the finalize-task-decomposer sub-agent. The output is
  the contract handed to downstream execution (whether automated agents or
  human reviewers).
allowed-tools: Read, Grep, Glob
---

# KB-task-decomposition — Task Decomposition Discipline

Discipline KB consumed by the `finalize-task-decomposer` sub-agent during the Task Decomposition stage — the final pipeline stage before execution. The sub-agent reads the approved Plan, the Blueprint, the ADRs, the acceptance tests, the phase validators, and any cross-artifact reconciliation outputs, then writes `tasks.json` — a directed-acyclic-graph (DAG) of work units that downstream execution consumes.

## Contents

- When this KB is loaded
- The sub-agent's responsibility
- Task identification
- Dependency-edge inference
- Work-unit sizing
- Parallelizability detection
- The canonical tasks.json schema
- Quality criteria
- Common pitfalls

## When this KB is loaded

This KB is loaded by:

- `finalize-task-decomposer` (single sub-agent per pipeline run; sole consumer of this KB)

The sub-agent loads this KB at the start of Task Decomposition and consults it throughout. Other sub-agents do NOT load this KB — they read or write the resulting `tasks.json`.

## The sub-agent's responsibility

The `finalize-task-decomposer` translates the Plan into machine-actionable form:

- **Identify the tasks.** The Plan is organized by phase (e.g., Phase 0 — Setup, Phase 1 — Feature delivery, Phase N+1 — Rollout). Each Plan phase contains tasks; the decomposer ensures every task in the Plan is represented in the DAG, and breaks down compound tasks where needed.
- **Infer dependencies.** Which tasks must complete before which others can start? Dependencies come from explicit Plan ordering, artifact dependencies (a migration must run before code that queries the new column), test-coverage relationships, and resource constraints.
- **Size work units.** Each task is sized for execution: small enough to track meaningfully, large enough to be coherent.
- **Detect parallelism.** Tasks with no dependency between them can run in parallel. The DAG makes parallelism explicit.
- **Encode quality gates.** Phase validators from the Plan map to gate-checks in the DAG; downstream execution can verify each gate before progressing.

The sub-agent does NOT:

- Add new design decisions. If a task surfaces a missing decision, surface it as an open question; don't resolve it.
- Skip Plan phases. Every phase is represented (even Rollout, even Setup).
- Re-order in ways that contradict the Plan's stated sequence.

## Task identification

A task is a single, completable unit of work:

- Has a clear "done" condition (binary; passes or fails a verification step).
- Produces a discrete artifact OR makes a discrete change.
- Names the layer(s) it touches.
- References the Plan section that authorized it.

Identification process:

1. Walk the Plan section by section. For each section, list the work items it implies.
2. For each work item, ask: "Is this one task or many?" Split if it's many (multi-file edit, multi-system change).
3. For each work item, ask: "Does this map to a Phase Validator?" If yes, the validator is the gate-check for this task or for the phase containing it.
4. Capture all acceptance-test references: each AC in the Acceptance Tests artifact must map to at least one task that satisfies it.

### When to split a task

Split when:

- The work spans multiple files in non-trivial ways (move shared logic + update consumers).
- The work spans multiple layers (a migration + the Backend code that uses it + the API contract changes).
- The work has internal phases with different verification (write code; write tests; integrate; gate-check).
- The work is large enough that partial completion would be ambiguous.

### When NOT to split

- The "task" is a single file change with a single test.
- Splitting would create two tasks with strong sequential coupling and no parallelism benefit.
- The Plan already presents it as one item (don't second-guess the Plan).

## Dependency-edge inference

Edges in the DAG represent "must complete before." Sources of edges:

### Explicit Plan ordering

The Plan lists phases in sequence (Phase 0 → Phase 1 → … → Phase N+1). Tasks in Phase N depend on Phase N-1's completion.

Within a phase, the Plan may state explicit ordering ("after migration runs, deploy the new Backend"). Capture as edges.

### Artifact dependencies

- A task that adds a DB column must complete before a task that queries it.
- A task that adds an API endpoint must complete before a task that calls it from the Frontend.
- A task that introduces a Feature flag must complete before tasks that gate on it.

These are inferred from the artifact graph the Plan describes.

### Test-coverage dependencies

- An acceptance test for behavior B can only run after the code that implements B is in place.
- A phase validator for phase N runs after phase N's tasks complete.

### Resource constraints

- Two tasks that modify the same file with non-trivial logic should serialize (the second consumes the first's changes); the DAG captures this with an edge.
- A task requiring a manual gate (e.g., production deploy approval) depends on the manual gate's resolution.

### Edges that should NOT exist

- "A and B both touch the codebase, so A should go before B" — not a dependency unless A and B share a file/symbol meaningfully.
- "A is more important than B" — priority isn't a dependency edge; it's a separate field.
- "A is easier than B, so do A first" — sequence preference; not a dependency.

## Work-unit sizing

A task should typically:

- Touch 1–5 files (compatible with reasonable review and a single PR).
- Have one or two verification steps (the test or check that confirms done).
- Take an executor a few hours of focused work, OR be a clean atomic change (migration, config update) that takes minutes.

If a task is much larger, split it. If a task is much smaller, consider merging it with an adjacent task (but only if they have the same dependencies).

For each task, capture an **effort estimate** (small / medium / large) so downstream sequencing can use it. Estimates are advisory, not contractual.

## Parallelizability detection

Two tasks can run in parallel if:

1. Neither depends on the other (directly or transitively in the DAG).
2. They don't modify the same file in a way that would create a merge conflict.
3. They don't compete for an exclusive resource (e.g., both modify the same DB schema in conflicting ways).

The DAG makes this explicit: tasks at the same depth with no edges between them are parallelizable. Downstream execution can dispatch them concurrently.

Anti-pattern: serial dependencies that don't need to be. If task B has only one edge to A and that edge represents a non-essential ordering preference, drop the edge.

Parallelizable tasks should be flagged in the schema with `parallelizable_with: [other_task_ids]` for downstream consumers that may not compute the topological structure.

## The canonical tasks.json schema

The sub-agent writes `tasks.json` matching this schema:

```json
{
  "schema_version": "1.0.0",
  "pipeline_run_id": "<run id>",
  "generated_at": "<ISO 8601>",
  "source_artifacts": {
    "plan_version": "v3",
    "blueprint_version": "v5.1.0",
    "acceptance_tests_revision": "<git SHA or version>"
  },
  "tasks": [
    {
      "id": "T001",
      "title": "Add `cancelled_at` column to orders table",
      "description": "Add nullable TIMESTAMPTZ column. Per Database Design subsection in Blueprint § 4.5. Migration uses expand-then-contract sequence per KB-database-design principles.",
      "layer": "database",
      "plan_reference": "Phase 1.2",
      "depends_on": [],
      "produces_artifact": "migrations/20260520_add_cancelled_at.sql",
      "verifies_acceptance_criterion": [],
      "gates": ["phase-validator-1.2-migration-applies"],
      "effort": "small",
      "parallelizable_with": ["T002", "T003"]
    },
    {
      "id": "T002",
      "title": "Add `cancelled_at` field to Order domain model",
      "description": "Per Backend Design subsection in Blueprint § 4.2.",
      "layer": "backend",
      "plan_reference": "Phase 1.2",
      "depends_on": [],
      "produces_artifact": "src/orders/domain/Order.ts",
      "verifies_acceptance_criterion": [],
      "gates": [],
      "effort": "small",
      "parallelizable_with": ["T001", "T003"]
    },
    {
      "id": "T010",
      "title": "Implement OrderService.cancel idempotency",
      "description": "Idempotency-Key middleware accepts the key and stores response for 24h. Per Backend Design § 4.2 + API Design § 4.3.",
      "layer": "backend",
      "plan_reference": "Phase 1.4",
      "depends_on": ["T001", "T002", "T005"],
      "produces_artifact": "src/orders/service.ts, src/middleware/idempotency.ts",
      "verifies_acceptance_criterion": ["AC-3", "AC-4"],
      "gates": ["phase-validator-1.4-idempotency-test"],
      "effort": "medium",
      "parallelizable_with": []
    }
  ],
  "phases": [
    {
      "name": "Phase 0 — Setup",
      "tasks": ["T000"],
      "validator": "phase-validator-0-setup"
    },
    {
      "name": "Phase 1 — Feature delivery",
      "tasks": ["T001", "T002", "T003", "T005", "T010"],
      "validator": "phase-validator-1-feature-delivery"
    }
  ],
  "open_questions_for_human": [
    {
      "question": "Plan § 3.4 references a 'webhook retry test' but the acceptance tests don't define one. Should I add a task to create it?",
      "context": "Plan ambiguity.",
      "blocks": "task-decomposition-completion"
    }
  ]
}
```

### Field semantics

- `id` — unique within the file. Convention: `T<NNN>` zero-padded.
- `title` — short, executor-facing.
- `description` — full context. References Plan, Blueprint, ADRs, and KBs as needed.
- `layer` — one of {frontend, backend, api, query, database, iac, cicd, cc, codespaces, cross-cutting}.
- `plan_reference` — pointer back to the Plan section that authorized this task.
- `depends_on` — list of task IDs that must complete first.
- `produces_artifact` — what the task creates or modifies.
- `verifies_acceptance_criterion` — list of AC IDs from the Acceptance Tests artifact this task contributes to.
- `gates` — phase-validator IDs that gate completion of this task's phase.
- `effort` — small / medium / large (advisory).
- `parallelizable_with` — list of task IDs that can run concurrently with this one.

## Quality criteria

A good `tasks.json`:

1. **Every Plan task is represented.** No silent drops.
2. **Every AC has at least one task that contributes to it.** ACs without tasks are not implemented; surface as an open question.
3. **The DAG is acyclic.** A cycle indicates a circular dependency that needs resolution (often: split one of the tasks).
4. **Edges are real.** Every edge in `depends_on` has a justification (artifact, ordering, resource).
5. **Phases align with the Plan.** The `phases` array mirrors the Plan's phase structure.
6. **Open questions are surfaced.** Anything ambiguous or missing from upstream artifacts is in `open_questions_for_human`, not papered over.
7. **Parallelism is visible.** `parallelizable_with` is populated for tasks at the same depth without inter-edges.
8. **Sizing is consistent.** Effort estimates are calibrated within the run (no "this small is the size of all the others' medium").

## Common pitfalls

- **Over-splitting.** A task per file is too fine-grained; merge changes that belong together.
- **Under-splitting.** A multi-layer task is hard to verify; split by layer.
- **Inferring edges that aren't there.** "Both touch the user model" isn't an edge unless the changes interact. The DAG should reflect real dependencies.
- **Missing tasks for ACs.** An AC without a task means the AC isn't implemented; that's a planning gap to surface.
- **Forgetting Phase 0 (Setup) and Phase N+1 (Rollout).** Both phases produce tasks (feature flags, deploy steps, monitoring config).
- **Silent assumption resolution.** When upstream artifacts are ambiguous, the decomposer asks; doesn't guess.
- **Phase validators not represented.** Each phase from the Plan should have a `validator` in `phases`, even if it's just "manual sign-off."

The output is the contract handed to execution. Quality of this DAG directly determines downstream throughput, parallelism, and gate-check reliability.
