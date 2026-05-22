# Feature-Pipeline v4.4.1 — Handoff

**Run-id:** audit-machinery-fixes-r1-20260521
**Completed:** 2026-05-21
**Status:** Accepted (pending Final Approval Gate)

## What v4.4.1 contains

The v4.4.1 release is a **PATCH bump over v4.4.0** — pure machinery fixes. No KB content changes, no agent surface changes, no Blueprint structure changes. The audit-machinery defects identified in ADR-0025 (during the v4.4.0 execution) are addressed:

1. **DE-2 regex hardened** (closes ADR-0025 defect 2). The `\.env(?!\w)` pattern false-matched `process.env.X`, `inputs.env == ...`, and similar identifier-style usages. Hardened to require path-component context (preceded by start / whitespace / `/` / `~` / quote-like chars). Eliminates 18 baseline BLOCKER false-positives. Workaround in v4.4.0 (bracket notation `process['env']['X']`) reverted.

2. **BACKTICK_PATH cross-KB resolution added** (closes ADR-0025 defect 3). When a backticked path starts with `KB-`, the auditor now tries resolving it against the project's skills root before falling back to skill_dir-relative resolution. Cross-KB references like `` `KB-storybook-platform/references/story-format.md` `` now resolve correctly. Workaround in v4.4.0 (16 cross-KB references rewritten as `` `KB-X` (specifically references/Y.md) ``) reverted.

3. **JSON summary aligns with line count** (closes ADR-0025 defect 4). `deductions_by_severity()` in `verdict_compute.py` now reads `final_severity` (post-pedagogical-triage) instead of raw `severity`, matching the markdown report's `## Summary` logic. AC-FR-5-b can use either count reliably.

4. **Depth-2 nesting check scoped to within-skill** (bonus fix discovered during testing). When fix 2 made cross-KB references resolve, the depth-2-nesting check began firing on them as MAJOR findings. The check is conceptually intra-skill; it now skips cross-KB targets.

## Baseline reduction

| Severity | v4.4.0 baseline (line-count) | v4.4.1 final | Delta |
|---|---|---|---|
| BLOCKER | 95 | **77** | **-18** |
| MAJOR | 71 | **69** | **-2** |
| MINOR | 28 | 28 | 0 |

Summary count now matches line count exactly (defect 4 closed): JSON summary BLOCKER 77 = line count 77.

## ⚠️ What remains open

**ADR-0025 defect 1 (pedagogical-marker backfill) carries forward to v4.5.0.** The remaining 77 baseline BLOCKERs are predominantly real pedagogical content in existing platform KBs (`KB-cc-platform`, `KB-codespaces-platform`, `KB-github-actions-platform`, `KB-codespaces-design`) — legitimate mentions of `.env`, `~/.aws/credentials`, `curl ... | sh` patterns in documentation about user-side configuration. These trigger DE-2 / CE-1 / DE-1 patterns correctly but need to be dispositioned via the `pedagogical-marker-spec.md` discipline (declare files in `pedagogical_sections:`, wrap dangerous-looking code blocks in `audit-example` fences).

Estimated v4.5.0 scope: 6-10 platform-KB files; frontmatter declarations + per-block fence wrapping. Net effect: another ~25 BLOCKERs drop to INFO; baseline should reach a small residual of genuinely-broken references that needs file-by-file attention.

## Files in this handoff

### Modified files (audit scripts)

| Path | Change |
|------|--------|
| `.claude/skills/auditing-skills/scripts/scan_security.py` | DE-2 regex hardened (lines 57-66) |
| `.claude/skills/auditing-skills/scripts/lint_references.py` | `normalize()` adds KB- prefix branch (lines 105-128); depth-2 check scoped to within-skill (lines 193-209) |
| `.claude/skills/auditing-cc-configs/scripts/verdict_compute.py` | `deductions_by_severity()` uses `final_severity` (lines 133-145) |

### Reverted workarounds (KB content restored to natural form)

| Path | Change |
|------|--------|
| `.claude/skills/KB-design-system-design/references/governance.md` | `process['env']['NODE_ENV']` → `process.env.NODE_ENV` |
| `.claude/skills/KB-storybook-platform/references/composition.md` | Same |
| All new KBs' Cross-references sections | `` `KB-X` (specifically references/Y.md) `` → `` `KB-X/references/Y.md` `` (16 sites) |

### New ADR

| Path | Purpose |
|------|---------|
| `adrs/ADR-0026-audit-machinery-fixes-v4-4-1.md` | Documents the fixes, validation, remaining v4.5.0 scope |

### Preserved artifacts (per ADR-0005)

All v4.4.0 artifacts preserved unchanged except for the workaround reverts noted above. No SKILL.md content semantically changed.

## Decisions carried forward unchanged from v4.4.0

- All Functional Requirements + EARS Acceptance Criteria
- 5 new KBs from v4.4.0 (KB-ux-design, KB-visual-design, KB-design-system-design, KB-component-architecture-design, KB-storybook-platform) — content unchanged
- 27 sub-agents + invocation points
- Append-only supersession discipline (ADR-0005)
- Layer Scope decisions
- ADR-0024 (frontend-design knowledge corpus structure) — accepted
- ADR-0025 (machinery defects) — defects 2, 3, 4 now closed by ADR-0026; defect 1 remains open

## What's next

**Two recommended threads (unchanged from v4.4.0 handoff):**

**Thread 1: Formalized execution pipeline** (user's stated next priority). Build-Time pipeline mirroring the Design-Time pipeline's 12-stage discipline. Independent of pipeline-machinery work; design begins from a fresh PRD.

**Thread 2: v4.5.0 marker-backfill feature run.** Targets the remaining ADR-0025 defect 1. Estimated scope: 1-2 days of file-by-file work in existing platform KBs to apply `pedagogical_sections:` declarations + `audit-example` fence wrapping.

Both threads are independent and can run in either order.
