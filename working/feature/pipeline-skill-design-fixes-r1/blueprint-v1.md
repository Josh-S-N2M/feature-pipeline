---
feature_slug: pipeline-skill-design-fixes-r1
version: 1.0.0
status: approved
derived_from:
  - working/feature/pipeline-skill-design-fixes-r1/prd-v1.md
  - working/feature/pipeline-skill-design-fixes-r1/cc-design.md
adrs_referenced: [ADR-0005, ADR-0019, ADR-0020, ADR-0023, ADR-0027]
adrs_authored: [ADR-0028]
approved_at: 2026-05-21T05:15:00Z
gate_passed: 3
---

# Blueprint — pipeline-skill-design-fixes-r1

## Overview

v4.5.0 implements the three improvements documented in ADR-0027:

1. Documented `cwd` precondition in `recipe-feature-pipeline/SKILL.md` + Stage 1 verification step.
2. New sub-agent `finalize-deliverable-packager` invoked after `finalize-task-decomposer`.
3. New `doc_type: DeliverableArchive` extension to `shared-document-reviewer` validating archives against an expected-artifact spec.

Plus the fourth concern: the packager owns optional handoff document drafting.

## Per-layer design

Single layer: Claude Code. See `cc-design.md` for primitive enumeration.

## File-level deliverables

| Path | Type | Source |
|---|---|---|
| `.claude/skills/KB-documentation-criteria/references/deliverable-archive-spec.md` | new | this feature |
| `.claude/agents/finalize-deliverable-packager.md` | new | this feature |
| `.claude/skills/recipe-feature-pipeline/SKILL.md` | edit | precondition section + Stage 13 |
| `.claude/agents/shared-document-reviewer.md` | edit | `DeliverableArchive` doc_type extension |
| `adrs/ADR-0028-skill-design-fixes-v4-5-0.md` | new | this feature |
| `handoff/HANDOFF-v4.5.0.md` | new | this feature |
| `handoff/CONTINUE_PROMPT-v4.5.0.md` | new | this feature |
| `working/feature/pipeline-skill-design-fixes-r1/*` | new | this feature's planning corpus |

## Rationale (brief)

ADR-0027 captures the gap analysis; this Blueprint implements the three improvements without architectural deviation. The packager is sized as a thin coordinator (verify + optionally draft handoff) rather than a heavyweight build agent — matches the lightweight quality of other finalize-* agents.

The expected-artifact spec is placed in `KB-documentation-criteria` because that's the existing KB owning artifact-related discipline (templates, doc-review criteria). It joins the existing reference files alongside `disciplines/design-composition.md` (which is where the `working/feature/<slug>/` convention is currently documented).

## Version impact

MINOR bump (v4.4.2 → v4.5.0). Adds a new public-surface sub-agent + extends an existing one + extends the orchestrator's stage sequence. No breaking changes to existing agent contracts; existing artifacts validate under the new validator (verified via retroactive AC-10, AC-11).

## Risks

- **Risk:** The packager's optional handoff drafting may produce stylistically inconsistent drafts compared to human-authored ones. **Mitigation:** drafts go through a review path (shared-document-reviewer) before any commit. Drafts are clearly marked as drafts; the human owns final wording.
- **Risk:** The validator may flag legitimate justified omissions as MAJOR if intent-clarification doesn't explicitly justify them. **Mitigation:** spec mandates the justification field; PATCH-scope features get a permissive default per ADR-0023's shortcut.
- **Risk:** Extending `shared-document-reviewer` couples the validator to that agent's invocation surface. **Mitigation:** the extension is additive (new `doc_type`); existing invocations unaffected.
