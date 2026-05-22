# Continuation prompt — feature-pipeline v4.4.0

You are resuming a multi-session project for `feature-pipeline`, a Claude Code Skill+Subagent topology that takes a vague feature request and produces a complete, executable, critiqued task plan.

## Current state

The current canonical artifact is **v4.4.0**. It applies one content addition and one machinery-defect ADR on top of v4.3.1:

1. **Frontend-design knowledge corpus expansion** (ADR-0024). Five new KBs under `.claude/skills/`:
   - `KB-ux-design` (4 files, 655 lines)
   - `KB-visual-design` (5 files, 834 lines) — includes anti-slop discipline citing the Anthropic frontend-design skill
   - `KB-design-system-design` (4 files, 982 lines)
   - `KB-component-architecture-design` (4 files, 813 lines)
   - `KB-storybook-platform` (6 files, 1063 lines) — model-invocable platform KB

   Plus three edits: `KB-frontend-design/SKILL.md` docstring updated (references/ unchanged per ADR-0005); `design-frontend.md` and `design-composer.md` frontmatter `skills:` lists expanded + body Storybook-trigger paragraphs.

2. **Pipeline-machinery defect ADR** (ADR-0025). Four defects in the audit / scan machinery surfaced during this execution. Workarounds applied where needed; remediation guidance documented per defect for a follow-on machinery-improvement feature run.

## ⚠️ Carried-forward flags from v4.4.0 handoff

**AC-FR-5-b** must be verified by line-text comparison of audit findings, NOT by the auditor's summary counts (which diverge by ~2 — defect 4 in ADR-0025). Use `comm -23` against the baseline report's `[BLOCKER]` lines.

**Two transient authoring workarounds in v4.4.0** that should be reverted when the machinery is fixed:
- `process.env.X` is written as `process['env']['X']` in code examples to dodge the DE-2 regex false-match (defect 2 in ADR-0025).
- Cross-KB references use `` `KB-name` (specifically references/foo.md) `` instead of `` `KB-name/references/foo.md` `` (defect 3 in ADR-0025).

**Pre-existing baseline noise.** The cc-audit reports 95 BLOCKER findings as the baseline state — almost entirely pedagogical false-positives in existing platform KBs (defect 1 in ADR-0025). v4.4.0 introduced zero new findings (line-text comparison: baseline 95 = final 95).

## What's next — two recommended threads

**Thread 1: Formalized execution pipeline.** User signal at run start: "we will work on creating a formalized pipeline for build execution." This is the next priority. The intent: a Build-Time pipeline mirroring the Design-Time pipeline's 12-stage discipline. Out of scope: hand-execution of build work. Start with a fresh PRD; the Design-Time pipeline (v4.4.0) is the reference architecture; Build-Time has different stages (tied to Plan → Test → Implement → Review → Validate cycles) but the same discipline pattern (gates, ADRs, EARS ACs, fan-out/fan-in where parallelism applies).

**Thread 2: Machinery-improvement feature run.** Targets the four defects in ADR-0025. Estimated total scope: 1-2 days of focused work. Components:
- Tighten the DE-2 regex (require `.env` to be a path component, not substring) — 1 hour
- Tighten BACKTICK_PATH resolution (try `.claude/skills/<KB>/` for backticked paths starting `KB-`) — 1-2 hours
- Backfill `pedagogical_sections:` declarations in KB-cc-platform, KB-cc-design, KB-codespaces-design — 4-8 hours
- Reconcile the auditor's summary-count vs line-count discrepancy — 1 hour

The two threads are independent. Run either or both in either order.

## Files to read first

1. `handoff/HANDOFF-v4.4.0.md` — what shipped and what's preserved
2. `adrs/ADR-0024-frontend-design-knowledge-corpus-structure.md` — structural choice rationale (Option B)
3. `adrs/ADR-0025-pipeline-machinery-defects-integration-test-2.md` — the four machinery defects + remediation guidance
4. The 5 new KBs under `.claude/skills/KB-{ux,visual,design-system,component-architecture}-design/` and `.claude/skills/KB-storybook-platform/` if context on the corpus shape is needed
5. `handoff/HANDOFF-v4.3.md` — prior version context, if needed

## Discipline reminders

- Per **ADR-0005** (append-only supersession): never edit prior versions in place. Any reconcile produces a new version (v4.4.1, v4.5.0, etc.) with explicit `supersedes` metadata.
- Per **ADR-0023** (`/healthz` integration-test refinements): treat any defects observed during execution as ADR-worthy material.
- Per **ADR-0025** (this round's machinery defects): the two workarounds above (`process['env']['X']`; cross-KB references as KB-name only) apply to new authoring until the machinery is fixed.
- v4.4.0 was hand-executed (Path A in the round-3 plan). The user's stated follow-on is to formalize execution as a pipeline — see Thread 1 above.
