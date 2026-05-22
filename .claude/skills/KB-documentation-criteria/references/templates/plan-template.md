---
id: Plan-<feature-slug>
version: 1.0.0
status: draft
feature_slug: <feature-slug>
derived_from: <blueprint-path>
phases: <integer-count>
total_tasks: <integer-count>
generated: <ISO-8601-UTC>
generated_by: plan-author
---

# Plan: [Feature Name]

## Contents

Section completion checklist — each box must be checked (including `N/A — out of scope` rows) before this document leaves draft. The reviewer's Gate 0 check uses this list as the structural-presence anchor.

- [ ] Purpose
- [ ] Source
- [ ] Phase 0 — Setup
- [ ] Phase 1, 2, ..., N — Feature delivery *(one checklist entry per phase in the actual plan)*
- [ ] Phase N+1 — Rollout / Observability *(include only when applicable)*
- [ ] Cross-Phase Dependencies
- [ ] L1/L2/L3 Verification Discipline
- [ ] Acceptance Test Cross-Reference
- [ ] Estimation Methodology
- [ ] Resourcing Posture
- [ ] Open Items (Pending Cross-Artifact Audit)
- [ ] Update History

**Note to authoring sub-agent:** update this list if you add or remove top-level (H2) sections from the document. Do NOT remove the `## Contents` heading — it is required for Gate 0 structural review. Mark each box `[x]` when the corresponding section is complete (or contains an explicit `N/A — out of scope` marker for layers not in scope).

## Purpose

The Plan is the executable decomposition of the Blueprint into phases and tasks. It is NOT a copy of the Blueprint's Implementation Plan section — that section is a sketch authored by `design-composer`. The Plan is authored by `plan-author` after the Blueprint is approved, and it carries full task-level detail with L1/L2/L3 verification criteria.

## Source

- **Blueprint**: `blueprint-v<N>.md`
- **Phase taxonomy used**: Phase 0 (setup) through Phase N (feature delivery), then optional Phase N+1 (rollout / observability hookups). All phases inherit the EARS-format Acceptance Criteria from the Blueprint.

## Phase 0 — Setup

### Goal

[What this phase accomplishes in 1 sentence. Phase 0 is for groundwork: dependencies, infrastructure, dev environment, feature flags.]

### Tasks

#### T0.1: [Task name]

- **Layer:** [layer from the 9-layer taxonomy]
- **Description:** [What the task does]
- **Dependencies:** [Other tasks this depends on; `none` if standalone]
- **Estimate:** [time or t-shirt size]
- **Satisfies AC:** [`AC-FR-N-letter` or `N/A` for setup-only tasks]
- **L1 verification:** [Lowest-cost check that this task is done — typically file-existence, syntax check, lint pass]
- **L2 verification:** [Functional check — unit test, smoke test, manual click-through]
- **L3 verification:** [Integration / acceptance check — full pipeline run, end-to-end test, real-data validation]

#### T0.2: [Task name]

- **Layer:** ...
- **Description:** ...
- (etc.)

### Phase 0 Exit Criteria

- [Observable outcome 1 that says Phase 0 is complete]
- [Outcome 2]

Phase Validator (per `KB-task-decomposition`): the Phase Validator for Phase 0 tests these exit criteria. If the Phase Validator fails, Phase 0 isn't done.

## Phase 1 — [Phase 1 name from Blueprint Implementation Plan]

### Goal

[1 sentence]

### Tasks

#### T1.1: [Task name]

- **Layer:** ...
- **Description:** ...
- **Dependencies:** [e.g., T0.2]
- **Estimate:** ...
- **Satisfies AC:** ...
- **L1 verification:** ...
- **L2 verification:** ...
- **L3 verification:** ...

#### T1.2: [...]

[etc.]

### Phase 1 Exit Criteria

- [Outcome 1]
- [Outcome 2]

## Phase 2 — [Phase 2 name]

[same structure]

## Phase N — [Final phase name]

[same structure]

## Phase N+1 — Rollout / Observability (when applicable)

[Same structure. Often includes feature-flag flip, dashboard verification, alert configuration.]

---

## Cross-Phase Dependencies

```
T0.1 ─┬─► T1.1 ─► T2.1 ─► T3.1
      │
T0.2 ─┴─► T1.2 ─► T2.2
```

[Mermaid or ASCII; the dependency graph the orchestrator uses for parallelization.]

## L1/L2/L3 Verification Discipline

Every task carries three verification criteria. The discipline:

- **L1 (cheapest):** Can be checked in seconds. Examples: file exists at expected path; YAML/JSON parses; lint passes; type-check passes.
- **L2 (functional):** Can be checked in minutes. Examples: unit test green; one-off script returns expected output; manual click-through succeeds.
- **L3 (integration):** Can be checked in tens of minutes to hours. Examples: end-to-end test; pipeline run on real data; canary deploy survives 24h.

The implementor working on a task knows the task is "done" when all three pass for that task. The Phase Validator for the containing phase aggregates L3 verifications across the phase's tasks.

## Acceptance Test Cross-Reference

| AC ID (from Blueprint) | Satisfied by task(s) |
|---|---|
| AC-FR-1-a | T1.1, T1.2 |
| AC-FR-1-b | T1.3 |
| AC-FR-2-a | T2.1 |
| (etc.) | |

Every AC in the Blueprint MUST have at least one task. Every task MUST satisfy at least one AC OR be explicitly tagged setup-only (Phase 0). `review-cross-artifact-auditor` flags orphan ACs (no task) and orphan tasks (no AC).

## Estimation Methodology

[1–2 sentences: how task estimates were derived. E.g., "T-shirt sizes XS/S/M/L based on similar features in this codebase; no precise hour estimates."]

## Resourcing Posture

[Optional: who will execute this plan (specific team, individual, or "any contributor"). Affects how task descriptions are written — for a specific team, can assume domain knowledge; for "any contributor," each task must be more self-contained.]

## Open Items (Pending Cross-Artifact Audit)

[Items the plan-author surfaced but couldn't resolve from the Blueprint alone. Each becomes an open item for the Cross-Artifact Audit.]

- [Open item 1]
- [Open item 2]

## Update History

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | [date] | plan-author | Initial Plan |

---

## Authoring notes (delete in the final document)

**Length budget:** Plans are long. A typical feature Plan runs 200–500 lines depending on task count. There is no upper bound, but if the Plan exceeds 1000 lines, the feature is probably too large for a single pipeline run — surface to user.

**Authored by:** `plan-author`. This sub-agent:
1. Reads the Blueprint (specifically: Implementation Plan section + Acceptance Criteria + Architecture Overview)
2. Decomposes into phases. Phase 0 = setup; Phase 1..N = feature delivery as the Blueprint sequences it; Phase N+1 = rollout (when applicable).
3. Within each phase, enumerates tasks. Each task has L1/L2/L3 verification.
4. Builds the dependency graph.
5. Builds the AC cross-reference.

What plan-author MUST NOT do:
- Re-design — if the Plan reveals a Blueprint gap, surface as open item; do NOT silently re-design
- Skip the AC cross-reference — orphan ACs and orphan tasks are `critical` issues at Cross-Artifact Audit
- Use ambiguous verbs like "implement" or "handle" — be specific about what the task produces

**Phase Validator authoring** (a separate sub-agent at Phase Validator Authoring, `test-phase-validator`):
- For each Phase in this Plan, the Phase Validator authoring step produces a phase validator that tests the Phase Exit Criteria
- Phase validators live in `phase-validators.md` (per the working-directory layout in `shared-conventions.md`)
- plan-author and test-phase-validator collaborate via the Plan's Phase Exit Criteria section — author them carefully, they're the contract
