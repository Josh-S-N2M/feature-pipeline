---
feature_slug: audit-machinery-fixes-r1
version: 1.0.0
status: approved
derived_from: working/feature/audit-machinery-fixes-r1/intent-clarification.md
approved_at: 2026-05-21T02:05:00Z
gate_passed: 2
---

# PRD — audit-machinery-fixes-r1

## Problem

The v4.4.0 execution surfaced four machinery defects in the project's audit + scan tooling (`auditing-skills/scripts/` and `auditing-cc-configs/scripts/`):

1. **DE-2 over-matching.** Credential-file regex `\.env(?!\w)` false-matched `process.env.X` patterns. Workaround in v4.4.0: bracket notation. Burden on future authors.
2. **BACKTICK_PATH cross-KB resolution gap.** Backticked references like `` `KB-storybook-platform/references/story-format.md` `` failed to resolve from sibling KBs. Workaround in v4.4.0: rewritten references. 16 sites affected.
3. **Summary count divergence.** JSON summary's `deductions_by_severity` read raw `severity` (pre-triage); markdown report's `## Summary` used `final_severity` (post-triage). Diverged by ~2.
4. **Pedagogical-marker backfill** (deferred). Existing platform KBs predate the marker spec; ~25 baseline BLOCKERs are real pedagogical content lacking declarations.

Defects 1-3 are in-scope for v4.4.1. Defect 4 deferred to v4.5.0.

## Solution

Three targeted code edits in the auditor + scan layer:

1. Harden DE-2 regex to require path-component context (lookbehind for start/whitespace/path-separator/quote).
2. Extend `normalize()` in `lint_references.py` to try `<skills-root>/<path>` when a backticked path starts with `KB-`.
3. Change `deductions_by_severity()` to read `final_severity` with `severity` as fallback.

Plus one follow-on (discovered during testing):

4. Scope the depth-2-nesting check in `lint_references.py` to within-skill targets only. (Cross-KB references resolve outside `skill_dir`; they're inter-skill navigation, not intra-skill depth-2 nesting.)

Plus reverts of v4.4.0 workarounds (2 process.env sites; 16 cross-KB reference sites).

## Acceptance criteria (EARS format)

- **AC-1 (DE-2 hardening):** When the auditor runs against a project containing `process.env.X`, `inputs.env == X`, or `context.env.X` patterns, then it shall not report DE-2 BLOCKERs for those patterns.
- **AC-2 (DE-2 preservation):** When the auditor runs against a project containing legitimate credential-file references (`.env`, `~/.aws/credentials`, `cat .env`, etc.), then it shall continue to report DE-2 BLOCKERs for those patterns.
- **AC-3 (Cross-KB resolution):** When a backticked path starting with `KB-` references a file that exists in a sibling KB, then the auditor shall resolve the path correctly and not report a Reference Illusion BLOCKER.
- **AC-4 (Summary alignment):** After fixes, the JSON summary's `deductions_by_severity` BLOCKER count shall equal the count of `[BLOCKER]` lines in the markdown report.
- **AC-5 (Baseline reduction):** The audit baseline (line-count BLOCKERs) shall strictly decrease from v4.4.0's 95.
- **AC-6 (Workaround reversion):** v4.4.0 workarounds (bracket-notation `process['env']['X']`; rewritten cross-KB references) shall be reverted to natural dot-notation and backticked-full-path forms, with the new machinery producing zero false-positive findings for these patterns.
- **AC-7 (Discipline documentation):** ADR-0026 shall be authored capturing the four fixes, the regex test cases for AC-1/AC-2, and the validation evidence for AC-3/AC-4/AC-5/AC-6.

## Non-goals

- No new content in any KB.
- No agent surface changes.
- No Blueprint structure change.
- No pedagogical-marker backfill for existing platform KBs (deferred to v4.5.0).
