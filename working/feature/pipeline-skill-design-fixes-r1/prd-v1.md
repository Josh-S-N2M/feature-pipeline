---
feature_slug: pipeline-skill-design-fixes-r1
version: 1.0.0
status: approved
derived_from: working/feature/pipeline-skill-design-fixes-r1/intent-clarification.md
approved_at: 2026-05-21T05:05:00Z
gate_passed: 2
---

# PRD — pipeline-skill-design-fixes-r1

## Problem

ADR-0027 (authored in v4.4.2) documents three skill-design issues that compound to produce the gap observed in v4.4.0 and v4.4.1: planning artifacts didn't land in the deliverable archive.

| Issue | Symptom | Why discipline didn't catch it |
|---|---|---|
| Implicit `cwd` anchor | `working/feature/<slug>/` resolves wherever the orchestrator's `cwd` happens to be | Orchestrator's SKILL.md doesn't specify the precondition |
| No packaging agent | After Task Decomposition, nothing assembles the deliverable archive | Implicit assumption "repo IS the deliverable" |
| No validator | Nothing checks "is the archive complete?" | `shared-document-reviewer` reviews individual docs, not the corpus |

Plus a fourth, related observation from ADR-0027's notes: `handoff/HANDOFF-v<X.Y.Z>.md` and `handoff/CONTINUE_PROMPT-v<X.Y.Z>.md` are entirely human-authored — no sub-agent owns producing handoff docs.

## Solution

Four coordinated changes:

1. **Orchestrator precondition.** Add a precondition section to `recipe-feature-pipeline/SKILL.md` documenting the `cwd == repo-root` assumption. Add a Stage 0 step where the orchestrator verifies the precondition before proceeding.

2. **Packager sub-agent.** New `.claude/agents/finalize-deliverable-packager.md`. Invoked by the orchestrator after `finalize-task-decomposer`. Reads the expected-artifact spec for the feature's scope class; enumerates `working/feature/<slug>/`; reports missing artifacts; optionally produces a versioned handoff document draft.

3. **Validator extension.** Extend `shared-document-reviewer` with a new `doc_type: DeliverableArchive` that checks the archive against the expected-artifact spec. Same severity taxonomy as other `shared-document-reviewer` invocations (BLOCKER if required artifact missing; MAJOR if conditional artifact missing without justification).

4. **Expected-artifact spec.** New file at `.claude/skills/KB-documentation-criteria/references/deliverable-archive-spec.md`. Documents the canonical artifact set per scope class (FULL / MINOR / PATCH). Tied to ADR-0023's scope-class framework.

## Acceptance criteria (EARS format)

### Orchestrator precondition

- **AC-1 (precondition documented):** When a reader opens `recipe-feature-pipeline/SKILL.md`, then they shall find an explicit precondition stating `cwd` MUST equal the repo root with rationale referring to ADR-0027.
- **AC-2 (precondition verified):** When the orchestrator begins Stage 1, then it shall verify the precondition by checking for `.claude/` in the current directory; if absent, halt with a clear error message naming ADR-0027.

### Packager sub-agent

- **AC-3 (packager exists):** When a reader inspects `.claude/agents/`, then they shall find `finalize-deliverable-packager.md` matching the existing sub-agent file format (frontmatter with `name`, `description`, `model`, `tools`, `skills`, `memory`).
- **AC-4 (packager scope documented):** When a reader opens the packager file, then they shall find its responsibilities documented: (a) verify deliverable-archive completeness, (b) optionally produce versioned handoff document drafts, (c) emit a structured report listing present + missing artifacts.
- **AC-5 (orchestrator invokes packager):** When a reader inspects the orchestrator's stage sequence in `recipe-feature-pipeline/SKILL.md`, then they shall find `finalize-deliverable-packager` invoked after `finalize-task-decomposer`.

### Validator extension

- **AC-6 (doc_type extended):** When `shared-document-reviewer` is invoked with `doc_type: DeliverableArchive`, then it shall validate `working/feature/<slug>/` against the spec at `KB-documentation-criteria/references/deliverable-archive-spec.md` for the declared scope class.
- **AC-7 (validator integrated):** When `finalize-deliverable-packager` runs, then it shall invoke `shared-document-reviewer` with `doc_type: DeliverableArchive` and incorporate findings into its report.

### Expected-artifact spec

- **AC-8 (spec exists):** When a reader inspects `KB-documentation-criteria/references/`, then they shall find `deliverable-archive-spec.md` matching the existing reference-file format (`## Contents` H2; prose + tables; cross-references to other KBs).
- **AC-9 (spec covers scope classes):** When a reader opens the spec, then they shall find separate expected-artifact lists for FULL, MINOR, and PATCH scope classes per ADR-0023.

### Retroactive validation

- **AC-10 (existing archives validate):** When the validator runs against v4.4.2's `working/feature/frontend-design-knowledge-r1/`, then it shall report a PASS verdict (declaring scope class MINOR per the feature's intent-clarification).
- **AC-11 (PATCH archives validate):** When the validator runs against v4.4.2's `working/feature/audit-machinery-fixes-r1/`, then it shall report a PASS verdict (declaring scope class PATCH).

### Discipline closure

- **AC-12 (ADR-0028 authored):** When this feature ships, then `adrs/ADR-0028-skill-design-fixes-v4-5-0.md` shall exist documenting the four changes and their validation evidence per AC-1 through AC-11.

## Non-goals

- No change to the existing 12-stage pipeline structure (only adds 1 stage post-task-decomposition).
- No change to how existing sub-agents author their artifacts.
- No automated repair (validator reports gaps; packager does not retroactively fill them — that's a deliberate cycle-creating activity that needs human review).
- No replacement of the existing `handoff/` directory convention; packager-generated handoff drafts go through the existing review path.
