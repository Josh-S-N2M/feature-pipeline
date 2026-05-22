---
feature_slug: pipeline-skill-design-fixes-r1
version: 1.0.0
status: approved
approved_at: 2026-05-21T05:00:00Z
gate_passed: 1
scope_class: MINOR
---

# Intent Clarification — pipeline-skill-design-fixes-r1

## User intent

> "Thread 3 and 2 only." (User chose to skip the formalized execution pipeline thread and proceed with the two pipeline-quality threads. This is Thread 3 — pipeline skill-design fixes per ADR-0027.)

User signal type: ordered continuation. ADR-0027 was authored in v4.4.2 documenting three skill-design improvements; this feature implements them.

## Scope

In-scope (ADR-0027's three improvements):

1. **Cwd precondition + fail-fast.** Edit `recipe-feature-pipeline/SKILL.md` to add an explicit precondition: orchestrator's `cwd` MUST equal the repo root (the directory containing `.claude/`). Add a Stage 0 fail-fast check.
2. **Deliverable-archive packager agent.** New sub-agent `finalize-deliverable-packager`. Invoked after `finalize-task-decomposer`. Verifies the canonical artifact set is present at `working/feature/<slug>/`; reports gaps; optionally produces a versioned handoff archive.
3. **Deliverable-archive validator.** Extension to `shared-document-reviewer` (or new sibling agent). Checks that `working/feature/<slug>/` contains the expected artifact set for the feature's scope class. PATCH-scope features get a shortened expected set per ADR-0023.

Plus a fourth, deferred concern surfaced in ADR-0027:

4. **Handoff document ownership.** Currently `handoff/HANDOFF-v<X.Y.Z>.md` and `handoff/CONTINUE_PROMPT-v<X.Y.Z>.md` are entirely human-authored. ADR-0027's notes section flagged this. Decision: fold this into the packager agent's responsibilities — packager produces the handoff doc draft alongside the archive verification.

Out of scope:

- ADR-0025 defect 1 (pedagogical-marker backfill). Belongs to v4.6.0 (Thread 2).
- The formalized execution pipeline (Thread 1) — user explicitly chose to skip.
- Any change to existing agent surfaces beyond the orchestrator precondition.
- Implementing the cwd check as a hard runtime gate (the orchestrator is a SKILL.md not executable code; the precondition is documented + the first stage adds a verification step).

## Acceptance signal

- The orchestrator's SKILL.md explicitly states the `cwd == repo-root` precondition with rationale referring to ADR-0027.
- `finalize-deliverable-packager` exists, is documented, and is referenced from the orchestrator's stage sequence.
- The deliverable-archive validator behavior is specified (whether implemented in `shared-document-reviewer` or as a new agent).
- Expected-artifact spec is documented and tied to scope class (FULL / MINOR / PATCH per ADR-0023 shortcuts).
- A retroactive validation pass against v4.4.2's `working/feature/frontend-design-knowledge-r1/` and `working/feature/audit-machinery-fixes-r1/` confirms both pass under the new validator (proves the validator's spec is accurate against real archives, including the PATCH-scope shortcut path).

## Scope class

**MINOR.** Adds a new sub-agent (one new file in `.claude/agents/`) and extends `shared-document-reviewer` (existing agent surface). Adds documented precondition to orchestrator. No breaking changes; no existing agent contracts altered.

## Discovery shortcut

This is an ADR-driven implementation feature. Discovery / Research / Synthesis stages skipped per ADR-0023 shortcut for ADR-implementation features: the root cause analysis and remediation guidance are already in ADR-0027.

Stages executed:

- Intent Clarification (this document)
- PRD
- Blueprint
- Per-layer Design (`cc-design.md` — Claude Code agent + skill changes)
- Architecture Audit (against existing pipeline structure)
- Plan
- Acceptance Tests
- Phase Validators
- (Implementation phases)
- ADR-0028 documenting the v4.5.0 fixes

Stages skipped (ADR-0023 ADR-driven shortcut):

- Discovery Planning / Research / Synthesis
- Cross-Artifact Audit (single-domain feature; surface is contained in `.claude/agents/` + `.claude/skills/recipe-feature-pipeline/`)
- Reconciliation (no reviewer cycle needed)
- Task Decomposition (Plan tasks are well-sized at this scope)

## ADRs

- **ADR-0027** (inherited): Pipeline skill-design gap — deliverable-archive (authored in v4.4.2; provides the three improvements this feature implements).
- **ADR-0023** (inherited): Discipline refinements from integration test (provides the scope-class shortcut framework).
- **ADR-0028** (to be authored): Skill-design fixes shipped in v4.5.0 — closes ADR-0027.
