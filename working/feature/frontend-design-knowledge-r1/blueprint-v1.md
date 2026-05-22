---
id: BP-frontend-design-knowledge-r1
version: 1.0.0
status: draft
feature_slug: frontend-design-knowledge-r1
derived_from: working/feature/frontend-design-knowledge-r1/prd-v1.md
codebase_analysis: working/feature/frontend-design-knowledge-r1/codebase-analysis.json
adrs_referenced: [ADR-0005, ADR-0011, ADR-0013, ADR-0016, ADR-0017, ADR-0019, ADR-0020, ADR-0021, ADR-0022, ADR-0023]
adrs_authored: [ADR-0024]
generated: 2026-05-20T23:55:00Z
generated_by: design-composer
---

# Frontend Design Knowledge Enhancement (Round 1) — Design Document

## Contents

- [x] Overview
- [x] Design Summary (Meta)
- [x] Background and Context
- [x] Acceptance Criteria (AC) — EARS Format
- [x] Existing Codebase Analysis
- [x] Design
- [x] Implementation Plan
- [x] Security Considerations
- [x] Test Boundaries
- [x] Verification Strategy
- [x] Future Extensibility
- [x] Alternative Solutions
- [x] Risks and Mitigation
- [x] References
- [x] Update History

## Overview

This feature enhances the project's frontend-design knowledge corpus by adding new KB content across six topical areas (anti-slop discipline, UX + accessibility-as-flow, UI / visual design, design system architecture, component architecture, and Storybook tooling) and the supporting sub-agent preload wiring. Existing `KB-frontend-design` (backend-of-the-frontend discipline + accessibility-as-baseline) is preserved unchanged; the new content extends it through four sibling design KBs plus one new platform KB.

This is also integration test #2 for the v4.3.1 pipeline (first real, non-synthetic feature; `/healthz` was integration test #1). Findings from the run feed back into pipeline-machinery refinement.

### Layer Scope

- [x] **Claude Code / Project Filesystem** — KB authoring (5 new KBs); sub-agent preload list edits (2 agents); docstring update (1 KB)
- [ ] **Frontend** — N/A — out of scope. This feature authors KNOWLEDGE about frontend; no application UI is produced.
- [ ] **Backend** — N/A — out of scope.
- [ ] **API** — N/A — out of scope.
- [ ] **Query / Data Access** — N/A — out of scope.
- [ ] **Database** — N/A — out of scope.
- [ ] **CI/CD (GitHub Actions)** — N/A — out of scope.
- [ ] **Infrastructure as Code** — N/A — out of scope.
- [ ] **Dev Environment (Codespaces / Devcontainer)** — N/A — out of scope.

### Referenced Specifications

None applicable. This feature is knowledge content; no UI / API / data-model / runbook specifications apply.

## Design Summary (Meta)

```yaml
design_type: "new_feature"
risk_level: "low"
complexity_level: "medium"
complexity_rationale: "Medium because (1) the structural choice between Options A/B/B' is the load-bearing decision and is documented in ADR-0024 with explicit fallback paths; (2) 5 new KBs is a substantial corpus addition (+5 SKILL.md descriptions to the preload set for design-frontend, modest token cost ~400-800); (3) anti-slop content references AI-default aesthetics by name which requires pedagogical-marker discipline application. Risk remains low because all changes are knowledge content / sub-agent metadata with no runtime impact and no cross-layer dependencies."
layers_touched:
  - "Claude Code / Project Filesystem"
blast_radius:
  runtime: "None — no runtime surface touched"
  build_time: "None — KB content is read at sub-agent invocation time; no build pipeline impact"
main_constraints:
  - "Framework-agnostic, web only (no mobile/native)"
  - "Design-side KBs prose-first; inline code RARE except in KB-storybook-platform where syntax IS the knowledge"
  - "ADR-0005 append-only supersession (preserved by D-004: extend Principle 3, do not restructure)"
  - "Voice bar: KB-cc-platform senior-engineer-handbook"
biggest_risks:
  - "KB-count growth (+5 in one round) may exceed project's discipline appetite for new KBs per round — mitigation: ADR-0024 documents the rationale and the Option A / B' fallbacks for future revisions"
  - "Anthropic frontend-design skill versioning is not under project control — mitigation: cite by name + acknowledge upstream dependency in references/anti-slop.md"
unknowns:
  - "CSF Factories community adoption curve through 2026-2027 — non-blocking; v1 documents both CSF3 and CSF Factories"
```

## Background and Context

### Prerequisite ADRs

- **ADR-0005:** Append-only supersession discipline. Honored by D-004 (extend Principle 3, do not restructure).
- **ADR-0011:** KB-documentation-criteria as canonical templates skill. Honored — Blueprint follows the canonical template.
- **ADR-0013:** Blueprint template adoption. This document conforms.
- **ADR-0016:** Per-layer fan-out / composer fan-in. Honored — single per-layer designer (design-cc) activated; design-composer integrates.
- **ADR-0017:** shared-document-reviewer integration. This Blueprint will be reviewed at invocation point 3 (DesignDoc).
- **ADR-0019:** Naming convention. `KB-` prefix; kebab-case. New KBs conform: `KB-ux-design`, `KB-visual-design`, `KB-design-system-design`, `KB-component-architecture-design`, `KB-storybook-platform`.
- **ADR-0020:** KB structure (SKILL.md + references/). Honored by all 5 new KBs.
- **ADR-0021:** Discovery phase architecture. Honored — KB-and-ADR-first triage applied in Research Plan.
- **ADR-0022:** Sub-agent reasoning configuration. Honored — no reasoning-configuration changes to existing sub-agents; new content does not introduce new sub-agents.
- **ADR-0023:** Discipline refinements from `/healthz` integration test. Honored — 5-way disposition triage applied in Research Plan; per-FR AC check passed; substrate in implementation-strategy mode for D-001.

### External Resources Used

None applicable. The feature is internal knowledge authoring; no external services / endpoints / IaC modules / GitHub Actions / Docker images are referenced.

### Agreement Checklist

#### Scope

- [x] Add 5 new KBs to `.claude/skills/`
- [x] Update `skills:` frontmatter of `design-frontend.md` and `design-composer.md`
- [x] Update docstring of `KB-frontend-design/SKILL.md` (metadata only; content preserved)
- [x] Apply pedagogical markers per `pedagogical-marker-spec.md` to anti-slop content

#### Non-Scope (Explicitly not changing)

- [x] `KB-frontend-design` principles and reference-file content (preserved per ADR-0005)
- [x] Application UI / Frontend layer (the feature's knowledge ABOUT frontend, not a UI)
- [x] Mobile / native UI patterns
- [x] UX writing / microcopy
- [x] Brand identity / marketing-style motion / pedagogical-from-scratch teaching
- [x] Sub-agent reasoning configuration (`model:`, `effort:`, `tools:`, `memory:` all unchanged)

#### Constraints

- [x] Parallel operation: N/A (no runtime parallelism concern; KBs are static content)
- [x] Backward compatibility: Required — existing `KB-frontend-design` preload references must continue working; existing sub-agents must continue invoking successfully
- [x] Performance measurement: Not required (no runtime performance surface; design-time token cost ~400-800 tokens additional is below measurement threshold)
- [x] Zero-downtime deployment: N/A (no deployment; .claude/ changes are session-local)
- [x] Forward-compatible migration: N/A (no migration concept)

#### Applicable Standards

- [x] KB authoring conventions `[explicit]` — Source: `KB-cc-design/references/patterns-and-anti-patterns.md`
- [x] Pedagogical-marker discipline `[explicit]` — Source: `auditing-cc-configs/references/pedagogical-marker-spec.md`
- [x] Naming convention `[explicit]` — Source: ADR-0019
- [x] KB structure `[explicit]` — Source: ADR-0020
- [x] Append-only supersession `[explicit]` — Source: ADR-0005

#### Quality Assurance Mechanisms

- [x] `auditing-cc-configs` skill — Enforces: KB structural and frontmatter conformance — Config: `.claude/skills/auditing-cc-configs/` — Covers: all `.claude/skills/*` and `.claude/agents/*` — Status: `adopted` (existing infrastructure; runs at end of execution per FR-5-b)
- [x] `auditing-skills` skill — Enforces: cross-file skill conventions, including pedagogical-marker handling — Covers: project-wide — Status: `adopted`
- [x] `shared-document-reviewer` — Enforces: Gate 0 (structural presence) and Gate 1 (semantic correctness) on the Blueprint — Status: `adopted` per ADR-0017 invocation point 3

### Problem to Solve

The existing `KB-frontend-design` covers backend-of-the-frontend discipline (state, perf, errors, typing, framework grain) and accessibility-as-baseline. It does NOT cover the substantive bodies of frontend design knowledge: aesthetic discipline (anti-slop), UX heuristics + accessibility-as-flow, visual design (type / color / motion / spacing / density / responsive), design system architecture (tokens / theming / semver), component architecture (atomic / headless / compound / polymorphic / slot / ref / prop-API), or Storybook tooling. When `design-frontend` invokes for a feature requiring these, it has no preloaded knowledge to ground its design decisions.

### Current Challenges

1. `KB-frontend-design`'s implicit scope (backend-of-frontend discipline) is not signalled clearly to consumers — the description suggests broader coverage than the principles actually deliver.
2. AI-default aesthetics ("AI slop": Inter / purple-on-white / shadcn defaults / convergence on Space Grotesk) are the model's natural output without explicit aesthetic discipline. The project has no preloaded anti-slop knowledge to push against this distributional convergence.
3. Storybook is not covered by any existing KB; features involving Storybook stories receive no preloaded tooling guidance.

### Requirements

#### Functional Requirements

Per PRD §Functional Requirements:

- FR-1: Author KB content across 6 topical areas (anti-slop; UX + a11y-flow; UI / visual; design-system; component-architecture; Storybook).
- FR-2: Honor design-side KB prose-first convention (Storybook KB exception per intake).
- FR-3: Apply project's naming + structure conventions (ADR-0019, ADR-0020).
- FR-4: Update `design-frontend.md` and `design-composer.md` `skills:` lists to preload new design-side KBs.
- FR-5: Apply pedagogical markers per spec; new ADR (only design-composer authors) documents the structural choice.
- FR-6: Match the senior-engineer-handbook voice of `KB-cc-platform`.
- FR-7: Preserve append-only supersession discipline (ADR-0005).
- FR-8 (P3): Capture pipeline-machinery defects in a sibling ADR (mirroring ADR-0023's pattern from integration test #1).

#### Non-Functional Requirements

- **Performance:** No runtime impact. Design-time token cost adds ~400-800 tokens to `design-frontend` and `design-composer` invocations (4 SKILL.md descriptions × 100-200 tokens each). Below measurement threshold.
- **Scalability:** N/A (knowledge corpus, not a load-bearing runtime surface).
- **Reliability:** All new content is read-only at sub-agent invocation; no failure modes beyond standard skill-loading errors (which the existing audit catches).
- **Maintainability:** New KBs follow established conventions; pedagogical markers applied surgically per D-006. Future revisions follow ADR-0005 append-only supersession.
- **Operability:** No observability surface; debugging is via `/skill KB-<name>` inspection in any Claude Code session.

## Acceptance Criteria (AC) — EARS Format

ACs traced through from PRD's ACs, refined with the structural choice now resolved (Option B; see ADR-0024). Grouped by Functional Requirement.

### FR-1: Author KB content across 6 topical areas

- [ ] **AC-FR-1-a:** When `design-frontend` invokes for any frontend-touching feature, the system shall be able to preload anti-slop content via `KB-visual-design/references/anti-slop.md` (citing Anthropic's `frontend-design` skill upstream).
- [ ] **AC-FR-1-b:** When `design-frontend` invokes, the system shall be able to preload UX content (Nielsen's 10 heuristics, journey/IA frameworks) and accessibility-as-flow patterns via `KB-ux-design/references/`.
- [ ] **AC-FR-1-c:** When `design-frontend` invokes, the system shall be able to preload UI / visual design content (type scales, color systems, motion, spacing, responsive) via `KB-visual-design/references/`.
- [ ] **AC-FR-1-d:** When `design-frontend` invokes, the system shall be able to preload design-system architecture content (token tiers, theming, semver) via `KB-design-system-design/references/`.
- [ ] **AC-FR-1-e:** When `design-frontend` invokes, the system shall be able to preload component architecture content (atomic, headless, compound, polymorphic, slot, ref, prop-API) via `KB-component-architecture-design/references/`.
- [ ] **AC-FR-1-f:** When `design-frontend` invokes for a feature including Storybook stories, the system shall be able to model-invoke `KB-storybook-platform` for CSF3 / CSF Factories / addons / docs / VRT / composition knowledge.

### FR-2: Honor design-side KB conventions

- [ ] **AC-FR-2-a:** While the 4 new design-side KBs are authored, the system shall keep code-block density in line with the existing design-KB convention (≤1.5 per 100 lines as a soft cap; departures call out reason).
- [ ] **AC-FR-2-b:** While `KB-storybook-platform` is authored, the system shall allow code-block density in the 3-5 per 100 lines range (intake exception: syntax IS the knowledge).

### FR-3: Apply naming + structure conventions

- [ ] **AC-FR-3-a:** The system shall name new KBs per ADR-0019: `KB-ux-design`, `KB-visual-design`, `KB-design-system-design`, `KB-component-architecture-design`, `KB-storybook-platform`.
- [ ] **AC-FR-3-b:** Each of the 5 new KBs shall have the structure `SKILL.md` + `references/*.md` per ADR-0020.
- [ ] **AC-FR-3-c:** Each SKILL.md and each reference file shall lead with `## Contents` H2 checklist.

### FR-4: Update sub-agent preload lists

- [ ] **AC-FR-4-a:** The system shall expand `design-frontend.md`'s `skills:` frontmatter from 4 entries to 8 entries (adding the 4 new design-side KBs; NOT adding `KB-storybook-platform` which is model-invocable).
- [ ] **AC-FR-4-b:** The system shall expand `design-composer.md`'s `skills:` frontmatter to include the 4 new design-side KBs.

### FR-5: Pedagogical markers + ADR authoring discipline

- [ ] **AC-FR-5-a:** Where new content references AI-default aesthetics by name (Inter, Roboto, purple-gradient-on-white, etc.), the system shall apply pedagogical markers per `pedagogical-marker-spec.md`.
- [ ] **AC-FR-5-b:** The system shall pass `cc-audit` (full audit via `auditing-cc-configs`) with zero new violations after all changes are applied.
- [ ] **AC-FR-5-c:** Only `design-composer` shall author the new ADR (ADR-0024) documenting the structural choice.

### FR-6: Voice and depth bar

- [ ] **AC-FR-6-a:** The new content shall match the senior-engineer-handbook voice of `KB-cc-platform` (declarative, opinionated, no tutorial framing; tables for trade-offs; prose for discipline).

### FR-7: Preserve supersession discipline

- [ ] **AC-FR-7-a:** The existing `KB-frontend-design` `references/principles.md` and `references/patterns-and-anti-patterns.md` shall be unmodified after the feature's execution (verified by `git diff`). The SKILL.md docstring update is metadata only.

### FR-8 (P3): Pipeline-machinery defect capture

- [ ] **AC-FR-8-a:** If pipeline-machinery defects are surfaced during execution (mirroring ADR-0023's pattern from integration test #1), the system shall record them in a sibling ADR. If no defects surface, this AC is satisfied trivially.

## Existing Codebase Analysis

Per `codebase-analysis.json` and `codebase-analysis-report.md`. Six focus areas identified (FA-001 through FA-006). Disposition table:

| Focus Area | Description | Disposition |
|---|---|---|
| FA-001 | Existing `KB-frontend-design` shape (500 lines, 0.8 code blocks / 100 lines, 8 backend-of-frontend principles + a11y baseline) | **preserve** — Option B keeps this KB intact |
| FA-002 | Platform-KB pattern (cc / github-actions / codespaces; SKILL.md + topical references/) | **preserve as template** — `KB-storybook-platform` follows this shape |
| FA-003 | Pedagogical-marker-spec format + the 3 KBs with pedagogical body content | **preserve as precedent** — new anti-slop content applies same marker discipline |
| FA-004 | 2 sub-agents preload `KB-frontend-design` (design-frontend, design-composer) | **transform** — `skills:` lists expanded to preload new design-side KBs (FR-4) |
| FA-005 | KB structural conventions (frontmatter, references/ flat layout, `## Contents` checklist) | **preserve as binding convention** — all 5 new KBs conform |
| FA-006 | Anthropic `frontend-design` skill at `/mnt/skills/public/` (external authoritative anti-slop reference) | **cite from new content** — `KB-visual-design/references/anti-slop.md` cites this upstream |

Blast-radius: bounded. 2 sub-agent files (frontmatter edits, mechanical); 1 KB file (docstring update only); 5 new KB directories (greenfield). No risk of breaking existing preload references.

## Design

### Claude Code Design

[See `cc-design.md` — integrated below in summary; full content in the sibling artifact.]

**Resolved decisions:**

- **D-001 (structural):** Option B — four sibling design KBs + `KB-storybook-platform`. Documented in ADR-0024.
- **D-002 (anti-slop):** `references/anti-slop.md` inside `KB-visual-design`. Cites Anthropic upstream.
- **D-003 (Storybook depth):** 2000-3500 lines at v1; matching `KB-cc-platform` shape.
- **D-004 (Principle 3 + a11y-flow):** Extend, don't restructure.
- **D-005 (sibling sub-agents):** No — defer.
- **D-006 (pedagogical markers):** Surgical — heavy in anti-slop, medium in visual, minimal elsewhere.

**Inventory of changes:** 5 new skills + 2 modified agent frontmatters + 1 modified KB docstring. Full primitive enumeration in `cc-design.md`.

### Frontend Design

N/A — out of scope. This feature is knowledge ABOUT frontend, not a Frontend layer change.

### Backend Design

N/A — out of scope.

### API Design

N/A — out of scope.

### Query / Data Access Design

N/A — out of scope.

### Database Design

N/A — out of scope.

### CI/CD Design

N/A — out of scope.

### Infrastructure as Code Design

N/A — out of scope.

### Dev Environment Design

N/A — out of scope.

## Implementation Plan

High-level sequencing. Per-task decomposition follows in Plan Authoring stage (`plan-authoring` agent produces `plan-v1.md`).

1. **Author `KB-storybook-platform` first.** Greenfield; no dependencies on other new KBs. Largest single KB (~2000-3500 lines). Includes the SKILL.md + 5 reference files.
2. **Author the 4 design-side KBs in parallel** (logical parallelism; serialized in execution): `KB-ux-design`, `KB-visual-design` (with `references/anti-slop.md`), `KB-design-system-design`, `KB-component-architecture-design`. Each ~600-1200 lines. Cross-reference each other where appropriate (e.g., `KB-component-architecture-design` references `KB-design-system-design`'s token tier model).
3. **Update `KB-frontend-design/SKILL.md` docstring.** Single metadata edit; no content changes. Document the new sibling KBs.
4. **Update `design-frontend.md` `skills:` frontmatter.** Expand from 4 entries to 8. Add a paragraph in the body documenting model-invocation of `KB-storybook-platform`.
5. **Update `design-composer.md` `skills:` frontmatter.** Add the 4 new design-side KBs.
6. **Apply pedagogical markers** to `references/anti-slop.md` and any other content that names AI-default aesthetics by way of negative example.
7. **Run `cc-audit`.** Full audit via `auditing-cc-configs/scripts/audit_project.py . --report /tmp/audit-report.md --json`. Resolve any new violations.
8. **(Conditional, per FR-8)** Capture any pipeline-machinery defects surfaced during execution in a sibling ADR.

## Security Considerations

None. This feature is internal knowledge content; no new attack surface, no new permissions, no new external integrations.

## Test Boundaries

N/A. The feature has no executable code surface beyond the `cc-audit` invocation (which is the verification mechanism, not a test).

## Verification Strategy

- **Structural verification:** `cc-audit` (full audit via `auditing-cc-configs`). Catches frontmatter violations, naming-convention violations, structural-pattern violations, and pedagogical-marker miss-applications.
- **Semantic verification:** manual review of the 5 new KBs against the voice/depth bar (AC-FR-6-a). The user verifies at the Final Approval Gate.
- **Append-only verification:** `git diff .claude/skills/KB-frontend-design/references/` returns empty after execution (AC-FR-7-a).
- **Regression verification:** `design-frontend` and `design-composer` continue to invoke successfully with the expanded `skills:` lists. Verified at next pipeline run.

## Future Extensibility

This is **Round 1** of a multi-round plan (per intent-clarification §Round-based roadmap). Future rounds may:

- **Round 2:** Expand each KB's reference content depth where Round 1 reaches the floor (e.g., `KB-component-architecture-design` may add a `references/composition-patterns.md` for higher-order patterns).
- **Round 3:** Cross-link KB content with adjacent platform KBs (e.g., `KB-storybook-platform` cross-references CI/CD patterns for VRT-in-CI). Out of scope for Round 1's Claude-Code-only scope.
- **Round N:** Sibling sub-agents (D-005's deferred decision) if parallel domain-specific drafting becomes a bottleneck.

## Alternative Solutions

Considered at synthesis; documented in `synthesis.md` Decisions section.

- **Option A (single expanded `KB-frontend-design`):** All 5 content areas absorbed into the existing KB. Pros: conservative; minimal sub-agent edits. Cons: single KB grows to ~3000+ lines, navigability suffers; loses field-standard separation of foundations / tokens / components. **Considered as fallback if KB-count growth proves excessive.**
- **Option B (chosen):** Four sibling design KBs + `KB-storybook-platform`. KB count 17 → 22. **Selected** for field-practice alignment and per-domain preloadability.
- **Option B' (3 sibling design KBs):** Same as B but design-system + component-architecture merged into one KB (token-component coupling). Pros: KB count 17 → 21; honest reflection of coupling. Cons: loses some domain separation. **Considered as acceptable alternative.**

## Risks and Mitigation

| Risk | Impact | Probability | Mitigation |
|---|---|---|---|
| KB-count growth (+5) exceeds project's discipline appetite | medium | low-medium | ADR-0024 documents rationale + Option A / B' fallbacks; future rounds can consolidate |
| Anthropic `frontend-design` skill is updated or removed | low | low | `references/anti-slop.md` carries "Source dependencies" note acknowledging upstream; project KB content stands on its own without the cite if needed |
| Pedagogical markers misapplied — `cc-audit` raises false-positive violations on anti-slop content | low | medium | D-006's surgical-marker discipline; audit's Step 4 verification already handles this pattern (FA-003 precedent) |
| New design-side KBs cross-reference each other inconsistently | low | low | Cross-references reviewed at Cross-Artifact Audit (`shared-document-reviewer` invocation point 4 per ADR-0017) |
| Voice drift between the 5 new KBs (each authored separately) | low | medium | AC-FR-6-a explicit; manual review at Final Approval Gate; voice convergence checked against `KB-cc-platform` |

## References

- **PRD:** `working/feature/frontend-design-knowledge-r1/prd-v1.md` (v1.0.0; approved 2026-05-20T22:45:00Z)
- **Research Plan:** `working/feature/frontend-design-knowledge-r1/research-plan.md` (v1.0.0; approved 2026-05-20T23:00:00Z)
- **Codebase Analysis:** `working/feature/frontend-design-knowledge-r1/codebase-analysis.json` + `codebase-analysis-report.md`
- **Research Notes:** `working/feature/frontend-design-knowledge-r1/research-notes/T-001` through `T-006` (all AC-satisfied)
- **Synthesis:** `working/feature/frontend-design-knowledge-r1/synthesis.md` (v1.0.0)
- **Per-layer Design:** `working/feature/frontend-design-knowledge-r1/cc-design.md` + `cc-dependencies.json`
- **New ADR:** ADR-0024 — Structural choice for frontend-design knowledge corpus (Option B)
- **Inherited ADRs:** ADR-0005, ADR-0011, ADR-0013, ADR-0016, ADR-0017, ADR-0019, ADR-0020, ADR-0021, ADR-0022, ADR-0023
- **External authoritative reference:** `/mnt/skills/public/frontend-design/SKILL.md` (Anthropic-managed; cited from `KB-visual-design/references/anti-slop.md`)

## Update History

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.0 | 2026-05-20 | design-composer | Initial Blueprint authored; Option B selected; ADR-0024 authored |
