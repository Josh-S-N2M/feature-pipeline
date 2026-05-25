# feature-pipeline (round 3 — Phase 2 implementation)

Production-ready Claude Code configuration for a 12-stage feature-design pipeline. 30 sub-agents across 12 stages, 6 human approval gates, 5 shared-document-reviewer invocation points, 22 ADRs.

**Status:** Phase 2 implementation complete (v4.3.1). All 9 batches signed off through 2026-05-20. Ready for Phase 3 (runtime execution against real features).

## Repository layout

```
feature-pipeline-round-3/
├── .claude/                       # The deployable artifact — copy this into any project's root
│   ├── agents/                    # 30 sub-agent definitions
│   ├── skills/                    # 17 KBs + 1 orchestrator + 7 auditing + 1 synthesize + 6 *-knowledge = 32 skills
│   ├── commands/                  # (slash commands, if any)
│   └── scripts/                   # (project-level scripts, if any)
│
├── adrs/                          # 12 production ADRs (ADR-0011 through ADR-0022)
│
├── handoff/                       # Versioned blueprints + continuation prompts + prior-session state
│   ├── blueprint-v4.3.1.md        # ← CURRENT blueprint (224 KB)
│   ├── blueprint-v4.3.0.md        # archived predecessor
│   ├── blueprint-v4.2.0.md        # ... older rounds
│   ├── HANDOFF-v4.3.md            # Phase 2 handoff doc
│   ├── CONTINUE_PROMPT-v4.3.md    # session-continuation prompt
│   └── ...
│
├── integration-tests/             # End-to-end pipeline walkthroughs
│   └── healthz-walkthrough.md     # 12-stage trace for the /healthz sample feature
│
├── state.json                     # Phase 2 implementation state (9 batches, all complete)
└── README.md                      # this file
```

## What "the pipeline" does

Given a feature request, the pipeline drives a 12-stage authoring + audit + decomposition flow:

1. **Intent Clarification** — `intake-intent-clarifier` disambiguates the user request.
2. **PRD Authoring** — `intake-prd-author` produces a PRD with EARS-format acceptance criteria.
3. **Discovery Planning** — `discovery-plan-author` produces a research plan with KB-gap + ADR-conflict analysis (per ADR-0021).
4. **Discovery Research** — `discovery-codebase-researcher` + N parallel `discovery-external-researcher` invocations.
5. **Synthesis** — 6-agent synthesize sub-pipeline (extractor → grapher → critic → framer → substrate → synthesizer).
6. **Per-layer Design** — up to 9 per-layer designers (frontend / backend / api / query / database / iac / cc / cicd / codespaces) fan out in parallel.
7. **Design Composition** — `design-composer` fans in and produces the Blueprint (+ any new ADRs). Only sub-agent that authors ADRs per FR-5.
8. **Architecture Audit** — `review-architecture-auditor` performs brief-honor L3 + blast-radius + synthesis-claim re-verification.
9. **Plan Authoring** — `plan-author` produces the implementation plan.
10. **Test Authoring** — `test-acceptance-author` + `test-phase-validator-author` in parallel.
11. **Cross-Artifact Audit** — `review-cross-artifact-auditor` with CMC posture + 4-cycle convergence.
12. **Task Decomposition** — `finalize-task-decomposer` produces `tasks.json`.

Reconciliation (`finalize-reconciler`) runs as-needed between any two stages when audits return `fail` or `conditional_pass`.

The orchestrator skill (`.claude/skills/recipe-feature-pipeline/SKILL.md`) coordinates the 12 stages and the 6 human approval gates.

## Sub-agent reasoning configuration (per ADR-0022)

All 30 sub-agents use `model: opus`. Reasoning gradient is shaped by `effort:`:

- **Tier A (effort: xhigh)** — 5 terminal compositional / gatekeeping agents:
  - `design-composer`, `synth-synthesizer`, `finalize-task-decomposer` (terminal authoring)
  - `review-architecture-auditor`, `review-cross-artifact-auditor` (gatekeepers)

- **Tier B (effort: high)** — 25 bounded-scope agents (intake, discovery, per-layer designers, plan, tests, reconciler, synth-*).

Discipline: KB-cc-design Principle 9 + auditing-subagents SA-13 enforce that the `skills:` array preloads SKILL.md *content* only — never use it to express reasoning depth (that's what `model:` and `effort:` are for).

## How to use this repo

For a project that wants to adopt the pipeline:

1. Copy `.claude/` into the project root.
2. Copy the relevant ADRs from `adrs/` into your project's `adrs/` (or however your project tracks ADRs).
3. Reference `handoff/blueprint-v4.3.1.md` for the authoritative architecture spec.
4. Invoke the orchestrator via the skill: `/skill recipe-feature-pipeline` (or equivalent).

The orchestrator handles agent dispatch, gate triggering, and state checkpointing.

## Notable design decisions (ADRs to read first)

- **ADR-0019** — naming convention (`intake-`, `discovery-`, `design-`, `review-`, `finalize-`, `synth-`, `shared-` prefixes).
- **ADR-0020** — KB structure (`KB-` prefix; one canonical SKILL.md per domain).
- **ADR-0021** — Discovery phase architecture (KB+ADR consultation before research; conditional external research; generic-fan-out execution).
- **ADR-0022** — Sub-agent reasoning configuration is intentional and audited.
- **ADR-0017** — shared-document-reviewer integration (5 invocation points).
- **ADR-0016** — per-layer fan-out + composer fan-in (Component 5 → 6 → 7 topology).
- **ADR-0009** — rationale brief 3-layer enforcement (sub-agent prompt structure).

## State.json — current state

Phase 2 complete. 9 batches signed off:

| Batch | Scope |
|---|---|
| 1 | Foundational KBs (documentation-criteria + review-disciplines + general-coding-principles) |
| 2 | Platform KBs (cc, github-actions, codespaces) |
| 3 | Design-only KBs (6 per-layer) |
| 4 | Platform-design KBs + stage-specific KBs |
| 5 | Intake + discovery sub-agents (5) |
| 6 | Design sub-agents (10) |
| 7 | Review + plan + test + finalize sub-agents (7) |
| 8 | Orchestrator + blueprint polish + 4-layer deep-reasoning fix + pipeline-wide reasoning-configuration sweep |
| 9 | Integration test against /healthz |

Carried-forward disciplines (7 standing): no silent expansions, surface subtle errors, update state.json after each phase, reference stages by name (never by number), templates carry Contents checklist, sub-agents do not author ADRs (FR-5) except design-composer, sub-agent reasoning configuration must be intentional and calibrated.

## Phase 3 — next

Phase 3 is runtime execution: take this repo into a Claude Code-capable environment, run the pipeline against real features, and empirically calibrate the Tier A/B reasoning-configuration split based on production output quality.
