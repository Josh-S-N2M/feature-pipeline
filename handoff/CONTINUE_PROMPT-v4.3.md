# Continue Prompt — feature-pipeline v4.3.0

You are resuming a multi-session design project for `feature-pipeline`, a Claude Code Skill+Subagent topology that takes a vague feature request and produces a complete, executable, critiqued task plan.

## Current state

The current canonical artifact is **`blueprint-v4.3.0.md`** in `/mnt/user-data/outputs/feature-pipeline-round-3/`. It was produced on 2026-05-19 in a session driven by `v4-3-plan.md` in the same directory. Three substantive changes were applied:

1. **Naming convention** (ADR-0019): phase-prefixed sub-agents (intake-, discovery-, synthesis-, design-, review-, plan-, test-, finalize-, shared-), KB-prefixed knowledge skills, recipe-prefixed orchestrator.
2. **KB structural restructure** (ADR-0020): 7 KBs absorbed into 2 consolidated KBs; 2 new platform KBs added. **Final count: 17 KBs.**
3. **Discovery phase architecture** (ADR-0021): Stage 2 plan-author consults KBs+ADRs; external research conditional; Stage 3 explicit fan-out (1 codebase + N external).

All 18 prior ADRs (0001-0018) were retroactively migrated to v4.3 naming per ADR-0014's pattern. Pre-naming-convention versions preserved.

## ⚠️ Open item from v4.3.0 handoff

The KB count is **17, not 15** as originally proposed. Two stage-specific KBs (`KB-codebase-research`, `KB-task-decomposition`) exist as v4.2 carry-forwards but were absent from the originally-proposed 15-count. The Update History entry and ADR-0020 surface this expansion explicitly. The user was flagged and asked to confirm/reject/defer the expansion. Check the most recent user message for their response and act accordingly:
- If **accept**: proceed normally; 17 is the locked count.
- If **reject**: fold one or both stage-specific KBs into KB-documentation-criteria; produce v4.3.1 with revised KB inventory.
- If **defer**: ship v4.3.0 as 17 KBs; mark this as a Phase 2 implementation decision.

## What's next (possible paths)

1. **Phase 2 — Implementation**: Create the 27 sub-agent files, 17 KB SKILL.md files, and the recipe-feature-pipeline orchestrator skill body. This is a substantial new project; start by reading `blueprint-v4.3.0.md` thoroughly.
2. **v4.3.1 patch**: Address the 6 non-blocking review issues (I-DR-005/006, I-AA-004/005, I-CA-002/003) if the user wants polish before Phase 2.
3. **v4.4.0 minor revision**: If the user surfaces new architectural concerns, start a new minor revision following the v4.2 → v4.3 pattern (preserve predecessor, apply changes, run review chain).
4. **Integration test against a sample feature**: Run the pipeline (once Phase 2 is implemented) against a real user feature to validate end-to-end.

## Files to read first

In order of importance for context restoration:
1. `state.json` — current state of v4.3.0 production
2. `HANDOFF-v4.3.md` — summary of what was produced and the open KB-count flag
3. `blueprint-v4.3.0.md` — the current artifact (long; 2458 lines)
4. `v4-3-review-verdicts.md` — 3-stage review results
5. `adrs/ADR-0019-naming-convention.md`, `ADR-0020-kb-structure.md`, `ADR-0021-discovery-phase-architecture.md` — the 3 new ADRs
6. `adrs-migrated/` — 18 retroactively-migrated ADRs + their pre-naming-convention preservation copies

## Preserved predecessor artifacts

`blueprint-v4.0.0.md`, `v4.1.0.md`, `v4.2.0.md` are all preserved per ADR-0005's append-only supersession discipline. Do NOT edit them in place. Any further revisions produce a v4.3.1 or v4.4.0 in the same directory.

## Discipline reminders

- **No silent expansions.** If a structural change goes beyond what the user explicitly confirmed, surface it for confirmation before proceeding. (The 15 → 17 KB count expansion was such an expansion; it was flagged appropriately in v4.3.0 handoff.)
- **Frequent staging.** Stage all working files to `/mnt/user-data/outputs/feature-pipeline-round-3/` after each meaningful checkpoint. Don't lose work to session boundaries.
- **Update state.json** after each phase.
- **Apply the pipeline's own discipline recursively** ("we eat our own dog food"): when designing this pipeline, follow the pipeline's stages — intake/discovery/synthesis/design/review/plan/test/finalize — for any non-trivial change to the design itself.

## User's deliberation pattern

The user catches subtle errors (Layer Scope category error at v4.2; missing platform/design split for GitHub Actions and Codespaces at v4.3; "research is not a phase, discovery is" at v4.3). The user wants exposed structural decisions, not silent expansions. The user accepts when convinced and rejects when overreach is detected. Apply this pattern: surface decisions explicitly, accept corrections gracefully, never add scope without confirmation.

## How to resume

Just start with what the user says next. They have full context from `HANDOFF-v4.3.md` and the open KB-count flag. Respond to whatever direction they take.
