# Feature-Pipeline v4.3.0 — Handoff

**Run-id:** feature-pipeline-design-r3-v4-3-20260519
**Completed:** 2026-05-19
**Status:** Accepted (with one user-awareness flag below)

## What v4.3.0 contains

The v4.3.0 release applies three substantive changes to v4.2.0:

1. **Naming convention** (ADR-0019). All 27 sub-agents prefixed by phase (intake-, discovery-, synthesis-, design-, review-, plan-, test-, finalize-, shared-). All knowledge skills prefixed `KB-`. Orchestrator skill prefixed `recipe-`. User-facing slash command `/feature-pipeline` preserved.

2. **KB structural restructure** (ADR-0020). Two consolidated KBs absorb 7 prior skills (KB-documentation-criteria absorbs 4 doc-authoring skills; KB-review-disciplines absorbs 3 review skills). Two new platform KBs (KB-github-actions-platform, KB-codespaces-platform) complete the platform/design split for the 3 platform layers (Claude Code, GitHub Actions, Codespaces). **Final count: 17 KBs** (see flag below).

3. **Discovery phase architecture** (ADR-0021). Stage 2 (`discovery-plan-author`) now consults existing KBs + ADRs explicitly; external research is conditional on KB-gap analysis. Stage 3 explicit fan-out: 1 codebase researcher (always) + N external researchers (generic-with-N-invocations, ≤6 parallel cap).

## ⚠️ User-awareness flag

The KB count is **17, not 15** as I originally proposed and you confirmed. The expansion to 17 absorbs two stage-specific KBs (`KB-codebase-research` and `KB-task-decomposition`) that exist as v4.2 carry-forwards and don't fit the doc-authoring or review consolidations. Their disciplines (codebase analysis via GitNexus; task DAG construction with dependency analysis) are genuinely distinct from document authoring and review.

The v4.3.0 Update History entry and ADR-0020's Consequences section both surface this expansion explicitly. Three options:

- **Accept** the expansion to 17 KBs as the final state.
- **Reject** the expansion: fold one or both stage-specific KBs into KB-documentation-criteria (which would stretch its scope further), reducing back toward 15.
- **Defer**: ship v4.3.0 as 17 KBs; revisit during Phase 2 implementation when on-disk authoring makes the KB-bloat tradeoff concrete.

Please confirm or correct before treating v4.3.0 as fully ratified.

## Files in this handoff

### Primary deliverables

| Path | Purpose |
|------|---------|
| `blueprint-v4.3.0.md` | The current blueprint (2458 lines). Supersedes v4.2.0 (preserved). |
| `adrs/ADR-0019-naming-convention.md` | New ADR — naming convention. |
| `adrs/ADR-0020-kb-structure.md` | New ADR — KB consolidation + platform/design split. |
| `adrs/ADR-0021-discovery-phase-architecture.md` | New ADR — discovery refactor. |
| `adrs-migrated/ADR-0001 through ADR-0018 (renamed versions)` | 18 ADRs with v4.3 naming convention applied. |
| `adrs-migrated/ADR-NNNN-*-pre-naming-convention.md` (18 files) | Pre-v4.3 versions of each ADR, preserved per ADR-0005. |
| `v4-3-review-verdicts.md` | 3-stage review chain results (all 3 reviewers: approved). |
| `v4-3-plan.md` | The execution plan that drove this session. |
| `state.json` | Final state of v4.3.0 production (run-id, completion status, phase notes). |

### Preserved predecessor artifacts (per ADR-0005)

| Path | Status |
|------|--------|
| `blueprint-v4.0.0.md` | Preserved (1350 lines) |
| `blueprint-v4.1.0.md` | Preserved (1393 lines) |
| `blueprint-v4.2.0.md` | Preserved (2367 lines) |
| `state-v4.2-complete.json` | Archived v4.2 completion state |
| `00-research-plan.md` | Round-3 research plan |
| `research-claims.json` | Round-3 research claims |
| `v4-2-plan.md` | v4.2.0 production plan (archived) |

## Decisions carried forward unchanged from v4.2.0

- All 12 Functional Requirements (FRs)
- All EARS-format Acceptance Criteria
- 9 per-layer designers with fan-out/fan-in topology at Stage 5
- 5 shared-document-reviewer invocation points (Stages 1, 1.5, 5b, 7, per-ADR)
- 6 user gates (Intent Confirmation, PRD Approval, Research Plan Approval, Blueprint Approval, Build Approval, Phase Validation)
- Append-only supersession discipline (ADR-0005)
- 8 per-layer Design sections with research-grounding caveats
- Layer Scope: all 9 layers in scope
- Phase 4 deferred items from v4.2 (T4.2-T4.4, T4.6-T4.8) remain deferred

## What's next

v4.3.0 is the final design-iteration artifact for the feature-pipeline. The next step is **Phase 2 — Implementation**, which is OUT OF SCOPE for this design session. Phase 2 will:

- Create the 27 sub-agent files in `.claude/agents/` using the v4.3 names
- Author the 17 KB SKILL.md files in `.claude/skills/KB-*/`
- Implement the `recipe-feature-pipeline` orchestrator skill body
- Run integration tests using the pipeline against a sample feature
- Surface implementation-time issues for a possible v4.3.1 patch

Phase 2 work is a separate session per the discipline established at v4.0.0.

## Review chain summary

All three reviewers (shared-document-reviewer / review-architecture-auditor / review-cross-artifact-auditor) approved v4.3.0. Six non-blocking issues were surfaced (I-DR-005/006, I-AA-004/005, I-CA-002/003) — all are clarity or traceability improvements, none architectural. See `v4-3-review-verdicts.md`.

## To resume work

If you want to continue refining the design, start a new session with `CONTINUE_PROMPT-v4.3.md` (in this same directory). That prompt re-establishes context and lets the next Claude pick up from v4.3.0.
