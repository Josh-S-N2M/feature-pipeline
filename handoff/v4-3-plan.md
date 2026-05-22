# v4.3.0 Production Plan — naming convention + KB restructure + discovery refactor

**Run-id:** feature-pipeline-design-r3-v4-3-20260519
**Started:** 2026-05-19
**Plan owner:** finalize-reconciler (this session, applying the very rename being designed)
**Predecessor:** blueprint-v4.2.0.md (preserved per ADR-0005)
**Scope of changes:**
1. Naming convention: phase-prefixed sub-agents, KB-prefixed knowledge skills, recipe-prefixed orchestrator
2. KB structural consolidation: documentation-criteria absorbs PRD-authoring + design-composition; new KB-review-disciplines absorbs 3 audit skills
3. Platform/design KB split for 3 platforms (claude-code, github-actions, codespaces)
4. Discovery phase refactor: plan-author must consult KBs+ADRs; Stage 3 fan-out explicit (1 codebase + N external researchers)
5. Three new ADRs (0019 naming, 0020 KB structure, 0021 discovery architecture)
6. Retroactive name updates to ADRs 0001-0018

## Phase 1 — Working file setup

- **T1.1** — Copy v4.2.0 to v4.3.0 working file
- **T1.2** — Update frontmatter (version, supersedes, changes summary)
- **T1.3** — Stage to outputs as v4.3.0-wip.md

## Phase 2 — Naming rename (mechanical, sed-based)

- **T2.1** — Run sub-agent renames (20 patterns, longest-first to avoid prefix collisions)
- **T2.2** — Run knowledge skill renames (~12 patterns)
- **T2.3** — Run orchestrator rename (1 pattern — skill folder only, slash command stays)
- **T2.4** — Verify no old names remain (grep check)
- **T2.5** — Stage interim v4.3.0-wip.md

## Phase 3 — KB structural restructure (substantive)

- **T3.1** — Rewrite KB inventory section: 15 KBs total (3 foundational, 6 platform pairs, 6 design-only)
- **T3.2** — Document KB-documentation-criteria as absorbing PRD-authoring + design-composition
- **T3.3** — Document KB-review-disciplines as new consolidated skill absorbing 3 audit skills
- **T3.4** — Document new KB-github-actions-platform and KB-codespaces-platform
- **T3.5** — Update Implementation Path Mapping table
- **T3.6** — Update sub-agent skill references (which KB each loads)

## Phase 4 — Discovery phase refactor

- **T4.1** — Update Stage 2 section: discovery-plan-author MUST consult KBs + existing ADRs as inputs; output research plan
- **T4.2** — Update Stage 3 section: explicit fan-out (1 × discovery-codebase-researcher + N × discovery-external-researcher); generic external researcher invoked per topic
- **T4.3** — Update orchestrator section to describe Stage 3 fan-out coordination
- **T4.4** — Update FR list if new FRs are warranted (FR-13 for discovery KB consultation?)

## Phase 5 — Author 3 new ADRs

- **T5.1** — ADR-0019: Naming convention (phase prefixes + KB-/shared-/recipe-)
- **T5.2** — ADR-0020: KB structure (consolidation + platform/design split)
- **T5.3** — ADR-0021: Discovery phase architecture (KB+ADR consultation; conditional external research; fan-out)

## Phase 6 — Retroactive ADR name updates

For each of ADRs 0001-0018 that references renamed entities, issue v2 with name updates per ADR-0014's retroactive migration pattern.

- **T6.1** — Audit which ADRs reference renamed entities (likely all 18)
- **T6.2** — Apply renames in each ADR; produce v2 of each (per ADR-0014)
- **T6.3** — Original-named ADR files become "{name}-pre-naming-convention.md" for audit trail
- **T6.4** — Stage all ADRs to adrs-migrated/

## Phase 7 — Cross-section coherence + verification

- **T7.1** — grep verification: no old sub-agent names, no old KB names remain (except in pre-rename-pattern files)
- **T7.2** — ADR reference resolution check (21 ADRs total = 18 + 3 new)
- **T7.3** — EARS keyword preservation check
- **T7.4** — Section count check
- **T7.5** — Update History entry for v4.3.0
- **T7.6** — Stage final v4.3.0.md

## Phase 8 — 3-stage review chain on v4.3.0

- **T8.1** — document-reviewer Pass 1
- **T8.2** — review-architecture-auditor Pass 2 (note: renamed in v4.3.0 from synth-architecture-auditor)
- **T8.3** — review-cross-artifact-auditor Pass 3 (note: renamed in v4.3.0 from synth-cross-artifact-auditor)
- **T8.4** — Aggregate verdicts

## Phase 9 — Handoff package

- **T9.1** — Final state.json
- **T9.2** — HANDOFF-v4.3.md
- **T9.3** — CONTINUE_PROMPT-v4.3.md
- **T9.4** — Zip all v4.3 artifacts + v4.0/v4.1/v4.2 preserved
- **T9.5** — Present to user

## State tracking

Every phase completion updates state.json. All files staged to `/mnt/user-data/outputs/feature-pipeline-round-3/` immediately after creation to survive session boundaries.

## Out of scope

- Implementing the actual sub-agents/KBs/orchestrator (Implementation Plan phase work, separate session)
- Running v4 pipeline against a real feature (integration test, separate session)
