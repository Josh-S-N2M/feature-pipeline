# Plan Authoring Discipline

The discipline used by `plan-author` during Plan Authoring. Produces a phase-decomposed, task-level Plan from the approved Blueprint, with L1/L2/L3 verification and full AC cross-reference.

## Contents

- Inputs
- Outputs
- Phase taxonomy
- Task structure
- L1/L2/L3 verification discipline
- AC cross-reference (the binding contract)
- Dependency graph construction
- Phase exit criteria
- Handling Blueprint gaps
- Estimation discipline
- Cross-pass interactions
- Honoring the Rationale Brief
- Anti-patterns
- Output expectations

## Inputs

`plan-author` receives:

| Input | Source | Purpose |
|---|---|---|
| Approved Blueprint | `blueprint-v<N>.md` (latest accepted version) | Primary input — defines scope, design, ACs |
| Codebase analysis JSON | `codebase-analysis.json` | Existing code that tasks must integrate with |
| Rationale brief | Orchestrator-supplied | User-confirmed decisions, open items, resolved issues |
| Issues-ledger | `working/feature/<slug>/issues-ledger.json` | Prior reviewer-surfaced issues with `category: plan` |
| KBs in scope | Per Blueprint's `adrs_referenced` and the rationale brief | Domain knowledge for the layers involved |

## Outputs

A single Plan file at `working/feature/<slug>/plan-v<N>.md`, conforming to `../templates/plan-template.md`.

The Plan is reviewed by `shared-document-reviewer` immediately after authoring (per ADR-0017 invocation point 4). If revisions are needed, the plan-author iterates.

## Phase taxonomy

A Plan decomposes into phases. The taxonomy is:

| Phase | Purpose | Always present? |
|---|---|---|
| **Phase 0 — Setup** | Groundwork: dependencies, infrastructure, dev environment, feature flags, scaffolding | Yes for any non-trivial feature |
| **Phase 1..N — Feature delivery** | The feature itself, decomposed by the Blueprint's Implementation Plan section | Yes |
| **Phase N+1 — Rollout / Observability** | Feature-flag flip, dashboard verification, alert configuration, partner notification | When applicable (most production features) |

Phase numbering inside a Plan is internal (sequential ordering of THIS plan's phases). It is NOT a reference to pipeline phases. The pipeline phase that produced this Plan is "Plan Authoring" — a single phase from the pipeline's perspective that yielded a multi-phase Plan artifact.

### Naming phases

Each phase carries a short descriptive name that comes from the Blueprint's Implementation Plan section. Examples: "Setup", "Foundation", "Feature scaffolding", "Migration", "Cutover", "Rollout."

The phase name should be specific. "Phase 1 — Implementation" is bad (too vague). "Phase 1 — Database schema migration + index creation" is good (specific to what happens).

## Task structure

Each phase contains tasks. Each task carries:

| Field | Required | Notes |
|---|---|---|
| **Task ID** | Yes | `T<phase>.<seq>` — e.g., `T0.1`, `T1.3`, `T2.7` |
| **Title** | Yes | Imperative verb + object. "Create migration for `orders.refund_status`," not "Migrations." |
| **Layer** | Yes | One of the 9 engineering layers (per `../layer-taxonomy.md`). For cross-layer tasks, list multiple. |
| **Description** | Yes | 1–3 sentences. What the task accomplishes. |
| **Dependencies** | Yes | Other task IDs this task depends on, or `none` for standalone tasks |
| **Estimate** | Optional | T-shirt size (XS/S/M/L) or time estimate. Match the project's conventions. |
| **Satisfies AC** | Yes | The Blueprint AC IDs this task helps satisfy, or `N/A — setup` for setup-only tasks in Phase 0 |
| **L1 verification** | Yes | Cheapest check that the task is done |
| **L2 verification** | Yes | Functional check |
| **L3 verification** | Yes | Integration / acceptance check |

### Task title discipline

Task titles use imperative verbs (Create, Add, Refactor, Migrate, Remove, Document, Configure). Avoid:

- Nouns alone ("Migrations" — implementor doesn't know what to do)
- Vague verbs ("Handle", "Implement", "Work on" — what specifically?)
- Multi-task titles ("Migration and tests" — two tasks; split)

Good titles:

- "Create migration for `orders.refund_status` column"
- "Refactor `OrderService.refund()` to emit `refund_requested` event"
- "Configure GitHub Actions environment `staging-eu` with restricted secrets"

## L1/L2/L3 verification discipline

Every task carries three verification criteria. The discipline:

### L1 — cheapest possible check

L1 takes seconds. It answers "did this task produce its file/config artifact and is it well-formed?"

Examples:

- File exists at expected path
- YAML/JSON parses
- Lint passes (e.g., `ruff check`, `prettier --check`, `terraform fmt -check`)
- Type-check passes (e.g., `mypy`, `tsc`)
- Migration file is valid SQL syntax

L1 does NOT execute the code's behavior — it just confirms the artifact exists and parses.

### L2 — functional check

L2 takes minutes. It answers "does this task's behavior work in isolation?"

Examples:

- Unit test green
- Manual click-through succeeds for the new UI component
- One-off script returns expected output for a representative input
- New endpoint responds correctly to a curl request

L2 confirms the task's local behavior. It does NOT verify integration with other systems.

### L3 — integration / acceptance check

L3 takes tens of minutes to hours. It answers "does this task work end-to-end against the Acceptance Criteria?"

Examples:

- End-to-end test against a staging environment
- Pipeline run on real-shaped data
- Canary deploy survives 24h with no rollback signals
- The Blueprint AC this task satisfies passes its EARS test

L3 is the bar for "this task is genuinely done."

### How the levels interact

A task is **complete** when all three pass. A task with L1 passing but L2 failing is not done — the file exists but doesn't work. A task with L1 and L2 passing but L3 failing is also not done — the behavior works locally but breaks in integration.

Phase Validators (authored separately during Phase Validator Authoring by `test-phase-validator`) aggregate L3 verifications across a phase's tasks. The Phase Validator passing = the phase is done.

## AC cross-reference (the binding contract)

Every Blueprint AC must map to at least one Plan task. Every Plan task must either satisfy at least one AC OR be explicitly tagged `N/A — setup` in Phase 0. No orphans in either direction.

The Plan includes a cross-reference table:

| AC ID | Satisfied by task(s) |
|---|---|
| AC-FR-1-a | T1.1, T1.2 |
| AC-FR-1-b | T1.3 |
| AC-FR-2-a | T2.1 |

`review-cross-artifact-auditor` runs at the Cross-Artifact Audit pass and verifies:

- Every AC has at least one task (otherwise: `critical` completeness issue against the Plan)
- Every task has at least one AC or `N/A — setup` (otherwise: `critical` consistency issue — the task may have been added for reasons not anchored in the Blueprint)
- Setup-only tasks all live in Phase 0 (otherwise: `important` consistency issue — setup-tagged work outside Phase 0 suggests sequencing confusion)

## Dependency graph construction

Tasks have dependencies. The Plan includes a dependency graph (as Mermaid, ASCII art, or both):

```
T0.1 ─┬─► T1.1 ─► T2.1 ─► T3.1
      │
T0.2 ─┴─► T1.2 ─► T2.2
```

The graph drives parallelization. Tasks with no incoming dependency at a given moment can run in parallel.

### Dependency types

| Type | Symbol/Semantics |
|---|---|
| **Hard dependency** | T_b cannot start until T_a is complete (L3 passed). Default. |
| **L2 dependency** | T_b can start when T_a's L2 passes (e.g., T_b is testing T_a's local behavior; T_a's L3 not needed yet). Annotate explicitly. |
| **No dependency** | Tasks are independent. Default when not listed. |

### Cycles

Cycles in the dependency graph are `critical` consistency issues. The Plan must be acyclic. If a task seems to depend on something that depends on it, refactor — usually one task is doing too much.

## Phase exit criteria

Each phase has explicit exit criteria — the observable outcomes that say the phase is done. These feed into Phase Validators.

```markdown
### Phase 0 Exit Criteria

- All Phase 0 tasks' L3 verifications pass
- The dev environment runs `pnpm dev` successfully against the new feature flag (default off)
- The CI pipeline includes the new lint/typecheck steps and they pass on `main`
```

Exit criteria are observable, not subjective. "Phase complete when team is happy with it" is not an exit criterion.

## Handling Blueprint gaps

The Plan author may discover gaps in the Blueprint — missing ACs, ambiguous Design subsections, unstated dependencies. Three valid responses:

| Gap type | Response |
|---|---|
| Missing AC for a feature behavior the Blueprint clearly intends | Surface as `important` issue against Blueprint; do not invent the AC in the Plan |
| Ambiguous Design (e.g., "use a cache" without specifying location/eviction) | Surface as `important` issue; defer the task until the ambiguity resolves |
| Unstated dependency between Blueprint layers | Add the dependency to the Plan's graph with an explanatory note; surface as `recommended` issue against Blueprint |

What plan-author MUST NOT do:

- Invent ACs not present in the Blueprint
- Silently make design decisions to fill ambiguities
- Skip tasks for ACs the Plan can't see how to satisfy

Surface, don't paper over.

## Estimation discipline

Estimates are useful but should not be precise. Use T-shirt sizes (XS / S / M / L) by default. The mapping varies by project — the Plan's Estimation Methodology section explains.

When the project requires hour estimates, use ranges (4–8h) not points (6h). Single-point hour estimates imply false precision.

What estimates are for:

- Identifying tasks that should be split (an L-sized task in Phase 1 may be doing too much)
- Capacity-checking the phase
- NOT for tracking velocity (that's a separate concern, not this Plan's job)

## Cross-pass interactions

### With `test-acceptance-author` (Acceptance Test Authoring)

`test-acceptance-author` reads the Blueprint's ACs and authors acceptance tests. It does NOT read the Plan. The Plan's task structure does not constrain test authoring.

But the Plan's L3 verification criteria SHOULD reference the acceptance tests where applicable: "L3: the AC-FR-1-a acceptance test (authored in `acceptance-tests.md`) passes."

### With `test-phase-validator` (Phase Validator Authoring)

`test-phase-validator` reads the Plan's Phase Exit Criteria and authors a Phase Validator per phase. The Plan's exit criteria are the test-phase-validator's contract — author them carefully.

### With `review-cross-artifact-auditor` (Cross-Artifact Audit)

The Cross-Artifact Audit cross-checks Blueprint ↔ Plan ↔ Tests ↔ Phase Validators. The AC cross-reference table is the load-bearing structure that audit verifies. Get it right; the audit cycles quickly if not.

### With `finalize-reconciler` (Reconciliation)

When Cross-Artifact Audit surfaces Plan issues, `finalize-reconciler` routes back to plan-author with an updated brief. plan-author iterates within the 4-cycle cap.

## Honoring the Rationale Brief

Per `../rationale-brief.md`, every authoring sub-agent honors the brief. For plan-author specifically:

- **User-confirmed decisions** about phasing or sequencing (e.g., "User approved Phase 0 must include feature-flag setup") → reflected in the Plan
- **Open items** about scope (e.g., "Rate-limit policy for /healthz pending user input") → handled as either deferred (add `[ ] Open item to resolve before Phase N`) or escalated (surface to orchestrator)
- **Resolved issues from prior iterations** (e.g., "I-CA-002 resolved by adding L3 verification to T1.3") → preserved; do not regress

`review-architecture-auditor` does not audit the Plan (that's `shared-document-reviewer` + `review-cross-artifact-auditor`'s job). But the brief-honor discipline still applies — the Plan should reflect every commitment the brief lists.

## Anti-patterns

### Anti-pattern 1: "Implementation" as a task

```
T1.1: Implement the feature
```

Useless. Every Plan task is implementation. Specific verb + specific object required.

### Anti-pattern 2: L3 verification deferred to "phase complete"

```
T1.3: ...
L3: Verified when Phase 1 is complete.
```

Circular. The phase is complete when its tasks' L3s pass. L3 must be task-specific.

### Anti-pattern 3: Setup-only tasks outside Phase 0

```
Phase 3:
T3.5: Add the feature flag (Satisfies AC: N/A — setup)
```

If it's setup, it belongs in Phase 0. If it has to happen mid-pipeline because it depends on Phase 1 outcomes, it's not setup — it's mid-stream configuration, and should satisfy an AC.

### Anti-pattern 4: Tasks satisfying every AC

```
T1.1: Build the feature (Satisfies: AC-FR-1-a, AC-FR-1-b, AC-FR-1-c, AC-FR-2-a, AC-FR-2-b, AC-OP-1, AC-OP-2)
```

If one task satisfies 7 ACs, it's doing 7 things. Split.

### Anti-pattern 5: Dependency direction unclear

```
T1.3 depends on T1.5
T1.5 depends on T1.7
T1.7 depends on T1.3
```

Cycle. Refactor — usually one task is too large.

### Anti-pattern 6: Phase exit criteria that are subjective

```
Phase 1 Exit Criteria:
- Team is satisfied with the implementation
- Code quality is high
```

Neither is observable. Replace with concrete signals: "All Phase 1 task L3s pass; the integration test suite green on the feature branch."

## Output expectations

A complete Plan has:

1. Valid frontmatter (per `../shared-conventions.md`)
2. `## Contents` checklist with each section box that will be marked when the section is filled
3. Phase 0 through last phase, each with task list + exit criteria
4. Cross-Phase Dependencies graph
5. L1/L2/L3 Verification Discipline section (the discipline summary; can be inherited from this KB by reference)
6. Acceptance Test Cross-Reference table (every AC mapped to at least one task)
7. Estimation Methodology section (how estimates were derived)
8. Resourcing Posture section (optional)
9. Open Items (Pending Cross-Artifact Audit)
10. Update History (filled on each version)

Output goes to `working/feature/<slug>/plan-v<N>.md`. `shared-document-reviewer` invoked immediately for Gate 0/1.
