---
id: ADR-0024
version: 1.0.0
status: Proposed
generated: 2026-05-20
generated_by: design-composer
supersedes: []
adrs_inherited: [ADR-0005, ADR-0011, ADR-0013, ADR-0016, ADR-0017, ADR-0019, ADR-0020, ADR-0021, ADR-0022, ADR-0023]
applies_to:
  - frontend-design-knowledge-r1
  - .claude/skills/KB-frontend-design/
  - .claude/skills/KB-ux-design/ (new)
  - .claude/skills/KB-visual-design/ (new)
  - .claude/skills/KB-design-system-design/ (new)
  - .claude/skills/KB-component-architecture-design/ (new)
  - .claude/skills/KB-storybook-platform/ (new)
template_format: per KB-documentation-criteria ADR template v1.0
change_summary: Adopts four sibling design KBs (Option B) plus one new platform KB (KB-storybook-platform) for the frontend-design knowledge corpus. Preserves existing KB-frontend-design unchanged per ADR-0005 supersession discipline.
---

# ADR-0024: Frontend-design knowledge corpus structural choice — four sibling design KBs (Option B)

## Contents

- [x] Status
- [x] Context
- [x] Decision
- [x] Decision Details
- [x] Rationale
- [x] Options Considered
- [x] Consequences
- [x] Architecture Impact
- [x] Implementation Guidance
- [x] Related Information

## Status

**Proposed** — 2026-05-20

Status moves to **Accepted** at the Blueprint Approval Gate (Gate 4) if approved.

## Context

The project's existing `KB-frontend-design` covers backend-of-the-frontend discipline (state management, colocation, perf budgets, error boundaries, typing, framework grain, progressive enhancement) plus accessibility-as-baseline. The SKILL.md docstring explicitly states "no platform partner KB (frontend platforms vary widely)" — recognizing that React / Vue / Svelte / SwiftUI / Jetpack Compose split the frontend landscape.

The corpus does NOT cover the substantive bodies of frontend *design* knowledge: anti-slop aesthetic discipline, UX heuristics + accessibility-as-flow, UI / visual design (type / color / motion / spacing / responsive), design system architecture (tokens / theming / semver), component architecture (atomic / headless / compound / polymorphic / slot / ref / prop-API), or Storybook tooling. When `design-frontend` invokes for a feature requiring these, it has no preloaded knowledge to ground its design decisions.

The PRD-driven scope (per `prd-v1.md@1.0.0`) adds content across these six topical areas. The structural question — single KB vs. multiple — is the load-bearing decision.

Three load-bearing facts from Discovery Research:

1. Mature design systems (IBM Carbon, Material Design 3, GitHub Primer, Salesforce Lightning, Atlassian) consistently treat tokens and components as **distinct foundations** with separate documentation areas. The coupling is at the consumption layer (component tokens are the third token tier), not the conceptual layer (research-notes/T-004; research-notes/T-005).
2. Anthropic ships an official `frontend-design` skill at `/mnt/skills/public/frontend-design/SKILL.md` (Nov 12, 2025) that carries the load-bearing anti-slop discipline. Project anti-slop content amounts to summary + project-specific calibration, NOT independent derivation (research-notes/T-001; codebase-analysis FA-006).
3. `KB-frontend-design`'s existing docstring rejects a paired-platform partner. Option B (sibling design KBs only) does NOT introduce a platform partner — it adds design-side siblings, leaving the rejection in place. The constraint is honored, not violated.

## Decision

The frontend-design knowledge corpus expands via **four sibling design KBs** plus **one new platform KB**:

1. `KB-ux-design` — UX heuristics, journey/IA frameworks, accessibility-as-flow patterns.
2. `KB-visual-design` — type / color / motion / spacing / density / responsive design. Hosts `references/anti-slop.md` (per D-002).
3. `KB-design-system-design` — token tier model, theming, semver discipline for design systems.
4. `KB-component-architecture-design` — atomic design, headless libraries, compound / slot / polymorphic / controlled / ref / prop-API patterns.
5. `KB-storybook-platform` — Storybook 9+ floor; CSF3 + CSF Factories; addons; MDX docs; Chromatic VRT + test-runner; composition via `refs`. Model-invocable (not always-preloaded) per KB-cc-design Principle 1.

`KB-frontend-design` is **preserved unchanged** as the backend-of-the-frontend + a11y-baseline KB. Its SKILL.md docstring receives a metadata-only update naming the new sibling KBs; the `references/principles.md` and `references/patterns-and-anti-patterns.md` files are not modified (honoring ADR-0005 supersession).

## Decision Details

| Item | Content |
|---|---|
| Decision | Adopt Option B: four sibling design KBs + `KB-storybook-platform`. KB count: 17 → 22. |
| Why now | The PRD's six topical areas are the substance of the feature; the structural choice cannot be deferred without leaving the per-layer designers without preload targets. |
| Why this | Aligns with mature-design-system field practice (Carbon / Material 3 / Primer / Salesforce all treat tokens and components as distinct foundations); each KB stays right-sized; preloadability per-domain; existing `KB-frontend-design` docstring's "no platform partner KB" constraint preserved. Option A's single-KB growth would push past 3000+ lines and hit navigability limits; Option B' merges design-system + component-architecture, losing some domain separation that the field treats as meaningful. |
| Known unknowns | Practical context-cost impact of +4 SKILL.md descriptions in `design-frontend`'s preload set (estimated 400-800 tokens; below measurement threshold but unmeasured). CSF Factories adoption curve through 2026-2027 (non-blocking; `KB-storybook-platform` documents both CSF3 and CSF Factories). |
| Kill criteria | If a future Round's research surfaces that >50% of `design-frontend` invocations only consume content from one of the four new design KBs, the corpus is over-fragmented and a consolidation revision (toward Option B' or Option A) supersedes this ADR. Alternatively: if KB-count growth causes measurable degradation in `design-frontend` performance (e.g., context overruns), the corpus must consolidate. |

## Rationale

Mature design systems' choice to separate tokens (foundations) from components is not arbitrary — it reflects a real coupling structure: tokens are decisions about visual language; components are decisions about interaction surfaces; the coupling at the consumption layer (component tokens = the third token tier) is one of many couplings, not the dominant one. Carbon's documentation, Material 3's documentation, and GitHub Primer's documentation all separate token reference from component reference. The project's KBs should follow this established pattern for the same reasons the field does.

The "single KB grows unmanageable" failure mode for Option A is concrete: `KB-frontend-design`'s current size is ~500 lines across 3 files; adding 5 content areas (~600-1200 lines each) would push the single KB to 3500-6500 lines. At that size, navigability and reload-cost become substantive problems — the cognitive load of finding the right reference file balloons, and `design-frontend`'s context cost grows whether or not the relevant section is needed.

Option B' (merging design-system + component-architecture) is honest about token-component coupling but trades away the field-practice alignment. The synthesis surfaced it as an acceptable alternative; the decision to favor B over B' is judgment-call territory. B is favored because:

- The four-way separation makes future Round 2 / Round 3 content additions cleaner (each KB has clear scope; new content slots into the right KB without re-litigating scope).
- The token-component coupling is one of many cross-references; KBs cross-reference each other freely (see KB-cc-design ↔ KB-cc-platform precedent).

`KB-storybook-platform` is model-invocable (not always-preloaded) because Storybook is relevant to a subset of frontend-touching features. Per KB-cc-design Principle 1, model-invocable skills cost zero context until invoked — the right primitive for "sometimes-relevant" knowledge.

## Options Considered

### Option A: Single expanded `KB-frontend-design`

All 5 content areas absorbed into the existing `KB-frontend-design` as new reference files. Existing 8 principles + 2 reference files preserved; new files added (`references/anti-slop.md`, `references/ux-and-a11y-flow.md`, `references/visual.md`, `references/design-system.md`, `references/component-architecture.md`). Plus `KB-storybook-platform` as a new platform KB.

**Pros:**
- Conservative; minimal sub-agent edits (`design-frontend.md` `skills:` list unchanged beyond optional KB-storybook-platform addition).
- Single KB-count delta: 17 → 18.
- Preserves the existing single-source-of-truth for frontend design discipline.

**Cons:**
- KB grows to 3500-6500 lines; navigability suffers.
- All 5 content areas always-preload together; no per-domain selectivity.
- Cross-references between content areas (e.g., component-architecture references design-system tokens) become intra-file rather than inter-KB, requiring careful file-level organization.
- Departs from mature-design-system field practice (which separates tokens from components).

### Option B': Three sibling design KBs (design-system + component-architecture merged)

Same as Option B but `KB-design-system-design` absorbs both T-004 and T-005 content into a single KB recognizing token-component coupling. KB count: 17 → 21.

**Pros:**
- Honest reflection of token-component coupling at the consumption layer.
- Fewer KBs than Option B (21 vs 22).
- Cross-references between tokens and components become intra-KB.

**Cons:**
- Loses the field-standard separation of foundations from components.
- The merged KB grows to ~2400-2400 lines (largest of the new design KBs); approaches the size that Option A's all-in-one KB would have for component+system alone.
- Future content additions (e.g., a Round 2 expansion of component patterns) must decide between expanding the merged KB or splitting later (re-litigating this decision).

### Option B (Selected): Four sibling design KBs + `KB-storybook-platform`

Each of the 5 content areas gets its own KB. Existing `KB-frontend-design` preserved.

**Pros:**
- Aligns with mature-design-system field practice.
- Each KB stays right-sized (~600-1200 lines each).
- Per-domain preloadability at design-time.
- Existing `KB-frontend-design` docstring's "no platform partner KB" constraint preserved.
- Future Round 2 / 3 content additions slot cleanly into the right KB.

**Cons:**
- KB-count growth (+5 in one round; 17 → 22) is significant.
- `design-frontend` `skills:` list grows from 4 to 8 entries (4 new design-side KBs added; existing 4 preserved).
- Practical token cost on `design-frontend` invocations: ~400-800 additional tokens for the 4 new SKILL.md descriptions.

## Consequences

**Positive:**

- `design-frontend` can preload domain-relevant knowledge at invocation time — UX, visual, design-system, and component-architecture content all available without re-fetching.
- Future Round 2 / 3 content additions have clear destinations.
- The Anthropic `frontend-design` skill citation chain is clean — `KB-visual-design/references/anti-slop.md` is the single project-side surface that cites the upstream.
- Field-practice alignment makes onboarding easier for designers familiar with Carbon / Material / Primer terminology.

**Negative:**

- 5 new KB directories to create, populate, and maintain.
- 2 sub-agent files modified (`design-frontend.md`, `design-composer.md` frontmatter).
- Voice convergence across 5 separately-authored KBs requires explicit attention (mitigated by AC-FR-6-a; manual review at Final Approval Gate).

**Neutral:**

- The Anthropic `frontend-design` skill is Anthropic-managed; if Anthropic updates or removes it, the citation chain needs refresh. `references/anti-slop.md` carries a "Source dependencies" note acknowledging this.

## Architecture Impact

**Components that change:**

- `.claude/skills/KB-ux-design/` — new directory + 4 files (SKILL.md + 3 reference files).
- `.claude/skills/KB-visual-design/` — new directory + 5 files (SKILL.md + 4 reference files, including `references/anti-slop.md`).
- `.claude/skills/KB-design-system-design/` — new directory + 4 files.
- `.claude/skills/KB-component-architecture-design/` — new directory + 4 files.
- `.claude/skills/KB-storybook-platform/` — new directory + 6 files (SKILL.md + 5 reference files).
- `.claude/agents/design-frontend.md` — frontmatter `skills:` list expanded; body adds one paragraph on `KB-storybook-platform` model-invocation.
- `.claude/agents/design-composer.md` — frontmatter `skills:` list expanded; body adds one paragraph on `KB-storybook-platform` model-invocation.
- `.claude/skills/KB-frontend-design/SKILL.md` — frontmatter description updated (metadata only); body content unchanged.

**New dependencies introduced:**

- Project-side dependency on Anthropic's `frontend-design` skill (`/mnt/skills/public/frontend-design/SKILL.md`) — cited from `KB-visual-design/references/anti-slop.md`. Cite-only dependency; no runtime requirement.

**Architectural constraints added:**

- New design-side KBs MUST cross-reference each other where the content naturally couples (e.g., `KB-component-architecture-design`'s discussion of component tokens MUST reference `KB-design-system-design`'s token tier model).
- `KB-storybook-platform`'s SKILL.md description MUST explicitly direct model-invocation (the "Use when..." sentence) so `design-frontend` knows when to invoke it.

**Architectural constraints removed:**

- None. `KB-frontend-design`'s "no platform partner KB" constraint is preserved.

## Implementation Guidance

For Plan Authoring (the next pipeline stage):

1. **Sequence new KBs largest-to-smallest.** `KB-storybook-platform` first (largest single KB at 2000-3500 lines). Then the 4 design-side KBs in parallel logical streams.
2. **Voice-anchor on `KB-cc-platform`.** Each new KB's SKILL.md and reference files should follow `KB-cc-platform`'s declarative, opinionated, no-tutorial-framing voice. Tables for trade-offs; prose for discipline; code minimal (except `KB-storybook-platform`'s syntax-IS-knowledge exception).
3. **Apply pedagogical markers surgically.** Heavy in `references/anti-slop.md`; medium in `KB-visual-design/SKILL.md` where it references AI-default aesthetics; minimal elsewhere. Per `pedagogical-marker-spec.md`.
4. **Cross-references between new KBs are required, not optional.** Each new KB's `## Related KBs` section names the siblings it overlaps with.
5. **Sub-agent edits last.** Author all 5 KBs first; then update `design-frontend.md` and `design-composer.md` `skills:` lists. Reduces the window in which sub-agents reference KBs that don't yet exist.
6. **Run `cc-audit` after each KB authoring step.** Catches frontmatter / structural violations early; per AC-FR-5-b, zero new violations at end of execution.

For future revisions:

- If consolidation toward Option B' or Option A is warranted (per Kill criteria), the supersession is handled per ADR-0005: this ADR (ADR-0024) is preserved; a new ADR-NNNN with `supersedes: [ADR-0024]` documents the consolidation rationale.
- The Anthropic `frontend-design` skill citation chain has a single project-side surface (`KB-visual-design/references/anti-slop.md`); update there if upstream changes warrant.

## Related Information

- **Synthesis report:** `working/feature/frontend-design-knowledge-r1/synthesis.md` (D-001 enumeration of Options A / B / B').
- **Discovery Research:** `working/feature/frontend-design-knowledge-r1/research-notes/T-001` through `T-006`.
- **Codebase Analysis:** `working/feature/frontend-design-knowledge-r1/codebase-analysis.json` (FA-001 existing KB-frontend-design shape; FA-006 Anthropic upstream reference).
- **Per-layer Design:** `working/feature/frontend-design-knowledge-r1/cc-design.md` (concrete primitive enumeration honoring this ADR).
- **Field references cited in Discovery:** IBM Carbon Design System; Material Design 3; GitHub Primer; Salesforce Lightning Design System; Brad Frost's Atomic Design book; Anthropic frontend-design skill at `/mnt/skills/public/frontend-design/SKILL.md`.
