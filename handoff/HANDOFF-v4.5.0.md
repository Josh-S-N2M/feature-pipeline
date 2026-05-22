# Feature-Pipeline v4.5.0 — Handoff

**Run-id:** pipeline-skill-design-fixes-r1-20260521
**Completed:** 2026-05-21
**Status:** Accepted (pending Final Approval Gate)

## What v4.5.0 contains

The v4.5.0 release is a **MINOR bump over v4.4.2** — feature additions to the pipeline machinery (new sub-agent, new orchestrator stage, new validator doc_type) plus one auditor parser fix surfaced during closeout. No breaking changes; all v4.4.x artifacts remain valid.

### Closes ADR-0027 (three skill-design fixes)

1. **Working-directory precondition** (closes ADR-0027 Issue 1). `recipe-feature-pipeline/SKILL.md` now documents the `cwd == repo-root` requirement and adds a Stage 1 step-0 precondition check.

2. **Deliverable-archive packager agent** (closes ADR-0027 Issue 2). New `finalize-deliverable-packager` sub-agent at Stage 13 (after Task Decomposition, before Gate 6). Verifies `working/feature/<slug>/` contains the expected artifact set per declared scope class; invokes `shared-document-reviewer` for validation; optionally drafts versioned handoff documents; emits `packager-report.json`.

3. **Deliverable-archive validator** (closes ADR-0027 Issue 3). `shared-document-reviewer` extended with new `doc_type: DeliverableArchive`. Reads spec at `KB-documentation-criteria/references/deliverable-archive-spec.md`; validates archive completeness against per-scope-class expected artifact set.

### Bonus: auditor parser fix (addendum to ADR-0028)

While validating v4.5.0, the auditor false-flagged 28 MAJOR findings as "Body references tools not in declared `tools:` list" — root cause was `parse_tools_from_frontmatter` in `auditing-subagents/scripts/analyze_subagent.py` not handling YAML bracketed-list syntax (`tools: [A, B, C]`). Three-line fix to strip brackets before splitting. The bug had been latent in the auditor; the fix eliminated 28 false positives across the 27 existing agents.

## Baseline reduction

| Severity | v4.4.2 baseline | v4.5.0 final | Delta |
|---|---|---|---|
| BLOCKER | 77 | 77 | 0 |
| MAJOR | 70 | **42** | **-28** |
| MINOR | 29 | 29 | 0 |

The MAJOR drop is entirely attributable to the auditor parser fix; the v4.5.0 skill-design fixes themselves are additive (no existing findings could fix-by-existing).

**One remaining genuine MAJOR** surfaced after false positives cleared: `review-cross-artifact-auditor.md` body references `Bash` without declaring it in `tools:`. Pre-existing; not in v4.5.0 scope; queued for future small fix.

## ⚠️ What's still open

**ADR-0025 defect 1** (pedagogical-marker backfill in existing platform KBs) — v4.5.1 or v4.6.0 scope. ~25 baseline BLOCKERs remain attributable to this. Estimated 6-10 platform-KB files needing `pedagogical_sections:` declarations + `audit-example` fence wrapping.

**One pre-existing genuine MAJOR** in `review-cross-artifact-auditor.md` (Bash body-reference without declaration).

**Stage 13 retroactive run.** v4.4.0, v4.4.1, v4.4.2 were authored before Stage 13 existed. Their archives now exist in canonical form (per v4.4.2's documentation patch). Running the new Stage 13 packager against them retroactively would surface any gaps; recommended as a one-off discipline-validation pass before the next feature run.

## Files in this handoff

### Modified files (pipeline machinery)

| Path | Change |
|------|--------|
| `.claude/skills/recipe-feature-pipeline/SKILL.md` | cwd precondition + Stage 13 added; "Thirteen-stage" updated |
| `.claude/agents/finalize-deliverable-packager.md` | New agent (143 lines) |
| `.claude/agents/shared-document-reviewer.md` | DeliverableArchive doc_type added |
| `.claude/skills/KB-documentation-criteria/references/deliverable-archive-spec.md` | New spec (defines expected artifact sets per scope class) |
| `.claude/skills/auditing-subagents/scripts/analyze_subagent.py` | `parse_tools_from_frontmatter` handles YAML flow-sequence |

### Planning artifacts (canonical location per ADR-0027 discipline)

| Path | Status |
|------|--------|
| `working/feature/pipeline-skill-design-fixes-r1/intent-clarification.md` | |
| `working/feature/pipeline-skill-design-fixes-r1/prd-v1.md` | |
| `working/feature/pipeline-skill-design-fixes-r1/blueprint-v1.md` | |
| `working/feature/pipeline-skill-design-fixes-r1/plan-v1.md` | |
| `working/feature/pipeline-skill-design-fixes-r1/acceptance-tests.md` | |
| `working/feature/pipeline-skill-design-fixes-r1/phase-validators.md` | |
| `working/feature/pipeline-skill-design-fixes-r1/cc-design.md` | (per-layer for Claude Code surface — the only layer this feature touches) |
| `working/feature/pipeline-skill-design-fixes-r1/adrs/ADR-0028-*.md` | Feature-scoped copy (includes parser-fix addendum) |

### New ADR

| Path | Purpose |
|------|---------|
| `adrs/ADR-0028-skill-design-fixes-v4-5-0.md` | Documents the three fixes + the auditor parser addendum |

## Decisions carried forward unchanged

- All v4.4.x KB content + agent surfaces + audit-machinery fixes (ADR-0024, ADR-0026)
- v4.4.0 + v4.4.1 planning artifacts (landed in v4.4.2)
- ADR-0023 PATCH-scope shortcut still valid; now formalized in the deliverable-archive spec via `scope_class: PATCH` conditional checks
- ADR-0027 fully closed by ADR-0028

## What's next — three threads, revised priority

**Thread 1: Formalized execution pipeline** (user's originally-stated priority). Now safe to start: ADR-0027 closed; new feature runs will land planning artifacts in canonical location automatically via Stage 13.

**Thread 2: v4.5.1 or v4.6.0 marker backfill.** Address ADR-0025 defect 1 (~25 pedagogical false-positives in existing platform KBs).

**Thread 3: Small cleanup.** Fix the pre-existing `review-cross-artifact-auditor.md` Bash declaration. ~5 minute change. Can ride along with any subsequent feature run.

**Recommended order:** Thread 1 (formalized execution pipeline) — the gating reason to delay it (ADR-0027) is now closed. Thread 2 can run in parallel; Thread 3 absorbed into either.
