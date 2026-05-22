---
id: ADR-0027
title: Pipeline skill-design gap — feature artifacts didn't land in deliverable archive
status: accepted
date: 2026-05-21
deciders: [user, claude]
supersedes: []
superseded_by: []
related: [ADR-0023, ADR-0025, ADR-0026]
---

# ADR-0027: Pipeline skill-design gap — feature artifacts didn't land in deliverable archive

## Context

After v4.4.1 shipped, the user asked: "Are all the feature documents in 4.4 proper locations?"

Investigation revealed that **none** of the v4.4.0 planning artifacts (26 documents: intent-clarification, PRD, research plan, research notes, codebase analysis, synthesis, per-layer design, blueprint, plan, acceptance-tests, phase-validators, tasks.json, audit issues JSONs, checkpoint, ADR-0024 feature-scoped copy) made it into the v4.4.0 deliverable archive. Same for v4.4.1 — zero planning artifacts shipped in the archive.

The convention is documented in existing KBs:

- `KB-documentation-criteria/references/disciplines/design-composition.md`: Blueprint at `working/feature/<slug>/blueprint-v<N>.md`; feature-scope ADRs at `working/feature/<slug>/adrs/ADR-NNNN-<slug>.md`.
- `KB-review-disciplines/references/issue-lifecycle.md`: issues ledger at `working/feature/<slug>/issues-ledger.json`.
- `recipe-feature-pipeline/SKILL.md`: "Working artifacts under `working/feature/<slug>/`"; the orchestrator creates `working/feature/<slug>/` if absent and each sub-agent writes to `working/feature/<slug>/<artifact>`.

So the convention is correct and consistent. The gap is elsewhere.

## Root cause analysis

Three distinct skill-design issues compound to produce the observed gap.

### Issue 1: Path-relativity is implicit

The orchestrator instructs sub-agents to write to `working/feature/<slug>/<artifact>` — a relative path. The anchor is `cwd` at the time of write. When the orchestrator's `cwd` equals the repo root, artifacts land in the repo's `working/` tree (correct). When the orchestrator runs in a separate planning workspace (as happened in this round, where planning happened in `/mnt/user-data/outputs/.../` and execution happened in `/home/claude/work/`), artifacts land in the workspace, not the repo.

The orchestrator's SKILL.md doesn't surface this. There's no fail-fast precondition that `cwd` must equal the repo root, no documented assumption about workspace topology, no instruction to copy artifacts into the repo if they were authored elsewhere.

### Issue 2: No agent owns "package the deliverable archive"

The pipeline's stages:

> Intent → PRD → Discovery → Synthesis → per-layer Design → Composition → Architecture Audit → Plan → AC → Phase Validators → Cross-Artifact Audit → Reconciliation → Task Decomposition

None is "assemble the final deliverable archive." The implicit assumption: the repo IS the deliverable once stages have written to `working/feature/<slug>/`. This assumes Issue 1 doesn't apply — that the orchestrator's `cwd` was the repo root throughout.

The `finalize-*` agents (`finalize-reconciler`, `finalize-task-decomposer`) sound like they might own packaging by their names, but their actual scope is narrower (reconciliation review; task decomposition). Neither verifies "is the deliverable archive complete?"

### Issue 3: No validator checks deliverable-archive completeness

`shared-document-reviewer` reviews individual documents against their templates. `architecture-auditor` and `cross-artifact-auditor` review the design layer. None checks "does the deliverable archive contain the canonical artifact set for this feature?"

If such a validator existed, the v4.4.0 gap would have been a BLOCKER finding instantly: "expected `working/feature/<slug>/{intent-clarification, prd-v<N>, blueprint-v<N>, plan-v<N>, acceptance-tests, phase-validators}.md`; found none."

## Decision

Adopt three pipeline skill-design improvements. Each is independently shippable; recommended bundling order: 1 → 3 → 2 (smallest invasive change first, validator before packager since the validator answers "what's expected" which the packager needs).

### Improvement 1: Make path-relativity explicit in the orchestrator

**Change.** `recipe-feature-pipeline/SKILL.md` to add a precondition section:

> **Working directory precondition.** Before running, `cwd` MUST equal the repo root (the directory containing `.claude/`). All `working/feature/<slug>/` paths in this orchestrator and downstream agents resolve relative to `cwd`. If planning happens in a separate workspace (e.g., an LLM ephemeral filesystem), the orchestrator's first step is to ensure `working/feature/<slug>/` is anchored at the repo root.

Plus a fail-fast check at orchestrator start: `assert (cwd / ".claude").exists(), "Orchestrator must run from repo root."`

**Effort.** ~30 minutes (one SKILL.md edit + one assertion).

### Improvement 2: Add a deliverable-archive packager agent

**Change.** New sub-agent `finalize-deliverable-packager` invoked after `finalize-task-decomposer`. Responsibilities:

- Verify `working/feature/<slug>/` contains the expected artifact set (see Improvement 3 for the spec).
- Optionally produce a tagged archive zip if the project's convention includes one (the current repo's `handoff/` directory hints at this convention via versioned blueprint copies).

**Effort.** ~2-4 hours (agent authoring + 1 invocation point change in orchestrator + testing).

### Improvement 3: Add a deliverable-archive validator

**Change.** Extend `shared-document-reviewer` (or add a new `deliverable-archive-validator`) with a check:

- Inputs: feature slug; expected-artifact spec (declared per-feature, defaults inherited).
- Procedure: enumerate `working/feature/<slug>/`; compare against expected set; report missing or unexpected artifacts as BLOCKER findings.

The expected-artifact spec defaults:

| Artifact | Required? |
|---|---|
| `intent-clarification.md` | yes |
| `prd-v<N>.md` (highest N) | yes |
| `blueprint-v<N>.md` (highest N) | yes |
| `plan-v<N>.md` (highest N) | yes |
| `acceptance-tests.md` | yes |
| `phase-validators.md` | yes |
| `research-plan.md` | conditional (skipped for PATCH-scope per ADR-0023 shortcut) |
| `research-notes/*.md` | conditional (same) |
| `synthesis.md` | conditional (same) |
| `codebase-analysis.json` + `codebase-analysis-report.md` | conditional (same) |
| Per-layer designs (`*-design.md` + `*-dependencies.json`) | conditional (only layers actually involved) |
| `tasks.json` | yes |
| `checkpoint.json` | yes |
| `architecture-audit-issues.json` | conditional |
| `cross-artifact-audit-issues.json` | conditional |
| `adrs/ADR-NNNN-<slug>.md` for each ADR authored this run | yes |

The "conditional" markers tie back to ADR-0023's PATCH-scope shortcut: a PATCH-scope feature legitimately skips Discovery / Synthesis / Architecture Audit / Cross-Audit. The validator should accept the absence of those when the feature declares PATCH scope in intent-clarification.

**Effort.** ~3-5 hours (spec authoring + validator implementation + tests).

## Consequences

**Backward applicability.** v4.4.0 and v4.4.1 are being documentation-patched in v4.4.2 to retroactively land their planning artifacts in the canonical location. This ADR is the design-side companion: the patch fixes the artifacts; this ADR fixes the discipline that allowed the gap.

**Forward applicability.** A future machinery-improvement run can implement improvements 1, 2, 3 as a single feature. Estimated total work: 1-2 days. Recommended target: v4.6.0 or alongside the v4.5.0 marker-backfill run.

**No urgency.** The gap is recoverable (v4.4.2 demonstrates). It's not blocking work. But it should be fixed before the formal execution pipeline is built (Thread 1 in the v4.4.x handoff) — the formal execution pipeline will compound the gap if it inherits the same pattern.

**Discipline already documented.** This ADR does not introduce a new convention; the existing KBs already document `working/feature/<slug>/` correctly. The improvements make the discipline enforced by machinery rather than honored by convention.

## Notes

The gap surfaced because Round 3 was hand-executed (Path A). When the formal pipeline is invoked with `cwd=repo-root`, Issues 1-3 don't manifest. So the bug is latent in the formal pipeline but only surfaces when execution diverges from the canonical workspace assumption.

This is a recurring pattern in pipeline integration testing: gaps that don't matter when everything happens in one workspace become acute when workspaces diverge. Future testing should deliberately introduce workspace divergence as a stress test.

There's a fourth, smaller observation worth recording: the `handoff/` convention (versioned blueprint copies; HANDOFF-vX.Y.Z.md; CONTINUE_PROMPT.md) is currently entirely human-authored. None of the sub-agents owns producing handoff documents. This is consistent with the "manual packaging" gap and could be folded into the Improvement 2 packager agent.
