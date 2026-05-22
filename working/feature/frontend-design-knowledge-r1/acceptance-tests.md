---
id: AT-frontend-design-knowledge-r1
version: 1.0.0
status: draft
feature_slug: frontend-design-knowledge-r1
derived_from: working/feature/frontend-design-knowledge-r1/blueprint-v1.md
blueprint_version: 1.0.0
generated: 2026-05-21T00:50:00Z
generated_by: test-acceptance-author
---

# Acceptance Tests: Frontend Design Knowledge Enhancement (Round 1)

## Contents

- [x] Test taxonomy and discipline
- [x] Test specifications (one per AC; 19 total)
- [x] AC coverage matrix
- [x] Limitations

## Test taxonomy and discipline

The feature is knowledge-content authoring. The dominant test type is **structural verification** (file existence, frontmatter conformance, content-pattern checks) executed by the existing `cc-audit` machinery. Three test categories:

- **STRUCT** — structural check. Automated by `cc-audit` (`auditing-cc-configs/scripts/audit_project.py`). Layer: filesystem.
- **CONTENT** — content-presence / content-shape check. Mix of automated grep / wc and manual review. Layer: KB content.
- **MANUAL** — voice / depth review. Layer: editorial. Verified by the user at the Final Approval Gate; no automation.

Each test specification includes: AC ID, category, preconditions, steps, expected outcome, automation hook (where applicable).

## Test specifications

### AC-FR-1-a — Anti-slop preload via KB-visual-design/references/anti-slop.md

- **Category:** STRUCT + CONTENT
- **Preconditions:** Phase 2 + Phase 3 complete.
- **Steps:**
  1. `test -f .claude/skills/KB-visual-design/references/anti-slop.md` exists.
  2. `grep -lE 'frontend-design' .claude/skills/KB-visual-design/references/anti-slop.md` matches (citation to Anthropic upstream).
  3. `grep -cE '(Inter|Roboto|Space Grotesk|purple.*gradient)' .claude/skills/KB-visual-design/references/anti-slop.md` returns ≥5 (slop-signature naming).
- **Expected outcome:** all 3 steps pass. File exists, cites upstream, names ≥5 slop signatures.
- **Automation hook:** part of cc-audit Step 4 verification + this acceptance test runs as bash spot-check.

### AC-FR-1-b — UX + a11y-flow via KB-ux-design

- **Category:** STRUCT
- **Preconditions:** Phase 2 Stream A complete.
- **Steps:**
  1. `test -d .claude/skills/KB-ux-design && test -f .claude/skills/KB-ux-design/SKILL.md && test -f .claude/skills/KB-ux-design/references/principles.md && test -f .claude/skills/KB-ux-design/references/journey-and-ia.md && test -f .claude/skills/KB-ux-design/references/accessibility-as-flow.md`.
  2. `grep -cE '^## ' .claude/skills/KB-ux-design/references/principles.md` ≥ 10 (Nielsen's 10 heuristics each as H2 or anchored in content).
- **Expected outcome:** SKILL.md + 3 reference files exist; principles file enumerates the 10 heuristics.
- **Automation hook:** bash spot-check.

### AC-FR-1-c — UI/visual via KB-visual-design

- **Category:** STRUCT
- **Preconditions:** Phase 2 Stream B complete.
- **Steps:**
  1. SKILL.md + `references/type-color-space.md` + `references/motion.md` + `references/responsive.md` + `references/anti-slop.md` exist.
  2. Each reference file ≥ 150 lines.
- **Expected outcome:** all 5 files present with substantive content.
- **Automation hook:** bash spot-check.

### AC-FR-1-d — Design-system via KB-design-system-design

- **Category:** STRUCT
- **Preconditions:** Phase 2 Stream C complete.
- **Steps:**
  1. SKILL.md + `references/tokens.md` + `references/theming.md` + `references/governance.md` exist.
  2. `grep -cE '(primitive|semantic|component)' .claude/skills/KB-design-system-design/references/tokens.md` ≥ 10 (three-tier model coverage).
- **Expected outcome:** all 4 files present; three-tier model substantively covered.
- **Automation hook:** bash spot-check.

### AC-FR-1-e — Component-architecture via KB-component-architecture-design

- **Category:** STRUCT
- **Preconditions:** Phase 2 Stream D complete.
- **Steps:**
  1. SKILL.md + `references/atomic-design.md` + `references/headless-libraries.md` + `references/patterns.md` exist.
  2. `grep -cE '(Radix|React Aria|Headless UI|Ariakit|shadcn)' .claude/skills/KB-component-architecture-design/references/headless-libraries.md` ≥ 5.
- **Expected outcome:** all 4 files present; 5+ canonical headless libraries named.
- **Automation hook:** bash spot-check.

### AC-FR-1-f — Storybook model-invocable

- **Category:** STRUCT + CONTENT
- **Preconditions:** Phase 1 complete; Phase 4 complete.
- **Steps:**
  1. `KB-storybook-platform/` exists with SKILL.md + 5 reference files.
  2. `grep -cE '^disable-model-invocation:' .claude/skills/KB-storybook-platform/SKILL.md` returns 0 (NOT disabled).
  3. `grep -lE 'KB-storybook-platform' .claude/agents/design-frontend.md` returns the file (body paragraph documenting model-invocation, NOT in `skills:` frontmatter list).
  4. `grep -E '^skills:' .claude/agents/design-frontend.md | grep -v 'KB-storybook-platform'` confirms it's NOT always-preloaded.
- **Expected outcome:** Storybook KB exists; not always-preloaded; documented as model-invocable in design-frontend.md body.
- **Automation hook:** bash spot-check.

### AC-FR-2-a — Design-KB code-block density ≤ 1.5 per 100 lines

- **Category:** CONTENT
- **Preconditions:** Phase 2 complete.
- **Steps:**
  1. For each of the 4 design-side KBs: count code blocks (`grep -cE '^\`\`\`'`) and total lines; compute density.
  2. Density ≤ 1.5 per 100 lines as soft cap; departures call out reason in the file itself.
- **Expected outcome:** all 4 design KBs at or below the soft cap, OR explicit rationale documented.
- **Automation hook:** bash arithmetic; manual review.

### AC-FR-2-b — Storybook KB code-block density 3-5 per 100 lines

- **Category:** CONTENT
- **Preconditions:** Phase 1 complete.
- **Steps:**
  1. Count code blocks and total lines across `KB-storybook-platform/`.
  2. Compute density; verify in range.
- **Expected outcome:** density 3-5 per 100 lines (syntax IS the knowledge per intake).
- **Automation hook:** bash arithmetic.

### AC-FR-3-a — Naming convention

- **Category:** STRUCT
- **Preconditions:** Phase 1 + Phase 2 complete.
- **Steps:**
  1. New KBs are named: `KB-ux-design`, `KB-visual-design`, `KB-design-system-design`, `KB-component-architecture-design`, `KB-storybook-platform`. Verify directory names exactly.
- **Expected outcome:** all 5 directories present with exact names per ADR-0019.
- **Automation hook:** cc-audit naming-convention check.

### AC-FR-3-b — KB structure (SKILL.md + references/)

- **Category:** STRUCT
- **Preconditions:** Phase 1 + Phase 2 complete.
- **Steps:**
  1. For each new KB: SKILL.md exists at top level; references/ directory exists with at least 3 files.
- **Expected outcome:** all 5 KBs conform to ADR-0020 structure.
- **Automation hook:** cc-audit structural check.

### AC-FR-3-c — `## Contents` H2 checklist

- **Category:** STRUCT
- **Preconditions:** Phase 1 + Phase 2 complete.
- **Steps:**
  1. For each new KB SKILL.md AND each reference file: `grep -c '^## Contents$'` returns 1.
- **Expected outcome:** every file has exactly one `## Contents` H2.
- **Automation hook:** cc-audit + bash.

### AC-FR-4-a — design-frontend.md skills list expansion (4 → 8 entries)

- **Category:** STRUCT
- **Preconditions:** Phase 4 complete.
- **Steps:**
  1. `grep -E '^skills:' .claude/agents/design-frontend.md` returns a line containing all of: KB-frontend-design, KB-ux-design, KB-visual-design, KB-design-system-design, KB-component-architecture-design, KB-documentation-criteria, KB-general-coding-principles, KB-review-disciplines.
- **Expected outcome:** 8 entries present in exact form.
- **Automation hook:** bash + cc-audit frontmatter check.

### AC-FR-4-b — design-composer.md skills list expansion

- **Category:** STRUCT
- **Preconditions:** Phase 4 complete.
- **Steps:**
  1. `grep -E '^skills:' .claude/agents/design-composer.md` returns a line containing the 4 new design-side KBs in addition to its existing entries.
- **Expected outcome:** existing entries preserved + 4 new entries added.
- **Automation hook:** bash + cc-audit.

### AC-FR-5-a — Pedagogical markers per spec

- **Category:** CONTENT + STRUCT
- **Preconditions:** Phase 3 complete.
- **Steps:**
  1. `KB-visual-design/references/anti-slop.md` contains marker patterns per `pedagogical-marker-spec.md`.
  2. cc-audit Step 4 verification disposes correctly of regex matches on slop-signature names (Inter, Roboto, etc.).
- **Expected outcome:** zero false-positive cc-audit failures on pedagogical content.
- **Automation hook:** cc-audit Step 4.

### AC-FR-5-b — cc-audit zero new violations

- **Category:** STRUCT
- **Preconditions:** Phase 6 complete.
- **Steps:**
  1. Run `python3 .claude/skills/auditing-cc-configs/scripts/audit_project.py . --report /tmp/audit-final.md --json`.
  2. Compare new violation count against `/tmp/audit-baseline.md` (Phase 0 baseline).
  3. Delta is zero.
- **Expected outcome:** zero new violations introduced by this feature.
- **Automation hook:** cc-audit.

### AC-FR-5-c — Only design-composer authored ADR-0024

- **Category:** MANUAL (provenance check)
- **Preconditions:** Design Composition stage complete (already complete).
- **Steps:**
  1. ADR-0024 frontmatter declares `generated_by: design-composer`.
- **Expected outcome:** provenance documented.
- **Automation hook:** none (provenance is by design of the pipeline; auditing would be detecting forgery).

### AC-FR-6-a — Voice matches KB-cc-platform senior-engineer-handbook

- **Category:** MANUAL
- **Preconditions:** Phase 1 + Phase 2 complete.
- **Steps:**
  1. User reads each new KB SKILL.md (5 files) and ≥1 reference file per KB.
  2. User judges voice against KB-cc-platform: declarative, opinionated, no tutorial framing, tables for trade-offs, prose for discipline.
- **Expected outcome:** user-approved at Final Approval Gate.
- **Automation hook:** none (editorial judgment).

### AC-FR-7-a — KB-frontend-design content preserved (ADR-0005 honored)

- **Category:** STRUCT
- **Preconditions:** Phase 5 complete.
- **Steps:**
  1. `git diff .claude/skills/KB-frontend-design/references/` returns empty.
  2. `git diff .claude/skills/KB-frontend-design/SKILL.md` shows ONLY frontmatter `description:` changes (no body changes).
- **Expected outcome:** reference files untouched; SKILL.md changes are metadata only.
- **Automation hook:** git diff + bash.

### AC-FR-8-a — Pipeline-machinery defect capture (conditional)

- **Category:** CONTENT
- **Preconditions:** Execution complete.
- **Steps:**
  1. Inspect execution-phase outputs for pipeline-machinery defects (artifact-shape mismatches, sub-agent invocation errors, etc.).
  2. If any defects surfaced: a sibling ADR exists documenting them. If no defects: AC trivially satisfied.
- **Expected outcome:** conditional satisfaction.
- **Automation hook:** manual review of execution logs.

## AC coverage matrix

| AC | Test ID | Test category | Layer |
|---|---|---|---|
| AC-FR-1-a | this doc | STRUCT + CONTENT | KB content |
| AC-FR-1-b | this doc | STRUCT | filesystem |
| AC-FR-1-c | this doc | STRUCT | filesystem |
| AC-FR-1-d | this doc | STRUCT | filesystem |
| AC-FR-1-e | this doc | STRUCT | filesystem |
| AC-FR-1-f | this doc | STRUCT + CONTENT | KB content + agent frontmatter |
| AC-FR-2-a | this doc | CONTENT | KB content |
| AC-FR-2-b | this doc | CONTENT | KB content |
| AC-FR-3-a | this doc | STRUCT | filesystem |
| AC-FR-3-b | this doc | STRUCT | filesystem |
| AC-FR-3-c | this doc | STRUCT | filesystem |
| AC-FR-4-a | this doc | STRUCT | agent frontmatter |
| AC-FR-4-b | this doc | STRUCT | agent frontmatter |
| AC-FR-5-a | this doc | CONTENT + STRUCT | KB content + audit |
| AC-FR-5-b | this doc | STRUCT | audit machinery |
| AC-FR-5-c | this doc | MANUAL (provenance) | ADR metadata |
| AC-FR-6-a | this doc | MANUAL | editorial review |
| AC-FR-7-a | this doc | STRUCT | git diff |
| AC-FR-8-a | this doc | CONTENT (conditional) | execution log |

Coverage: 19 of 19 ACs (100%). No orphan ACs.

## Limitations

- **AC-FR-6-a is not automatable.** Voice convergence across 5 separately-authored KBs is an editorial judgment. The user verifies at the Final Approval Gate. If voice drift is detected, Reconciliation cycle would request re-authoring of the offending KB(s).
- **AC-FR-5-c is provenance-by-design.** Pipeline architecture ensures only `design-composer` authors ADRs; auditing this would be detecting forgery (out of scope for normal operation).
- **AC-FR-8-a is conditional.** Trivially satisfied if no pipeline-machinery defects surface during execution.
