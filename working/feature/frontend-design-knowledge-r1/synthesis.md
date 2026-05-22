---
id: SYN-frontend-design-knowledge-r1
version: 1.0.0
status: draft
feature_slug: frontend-design-knowledge-r1
run_id: frontend-design-knowledge-r1-20260520-220000
audience_depth: mixed
derived_from:
  - prd-v1.md@1.0.0
  - research-plan.md@1.0.0
  - codebase-analysis.json@1.0.0
  - codebase-analysis-report.md@1.0.0
  - research-notes/T-001-anti-slop.md@1.0.0
  - research-notes/T-002-ux-and-a11y-flow.md@1.0.0
  - research-notes/T-003-ui-visual-design.md@1.0.0
  - research-notes/T-004-design-system-architecture.md@1.0.0
  - research-notes/T-005-component-architecture.md@1.0.0
  - research-notes/T-006-storybook.md@1.0.0
generated: 2026-05-20T23:30:00Z
generated_by: synth-synthesizer (6-agent fan-in collapsed for walkthrough)
---

# Synthesis: Frontend Design Knowledge Enhancement — Round 1

## Contents

- [x] Executive Summary
- [x] Findings
- [x] Decisions
- [x] Constraints Honored
- [x] Limitations
- [x] Sources

## Executive Summary

This synthesis consolidates 7 Discovery Research artifacts (1 codebase analysis + 6 external research notes; all acceptance-criteria checks satisfied) into a decision frame for the per-layer Design stage. The feature enhances the project's frontend-design knowledge corpus across six topical areas — anti-slop aesthetic discipline, UX and accessibility-as-flow, UI / visual design, design system architecture, component architecture, and Storybook tooling. Existing `KB-frontend-design` (backend-of-the-frontend discipline plus accessibility-as-baseline) is preserved; the new content extends it.

The load-bearing finding is structural rather than topical: **Anthropic ships an official `frontend-design` skill at `/mnt/skills/public/frontend-design/SKILL.md`** (Nov 12, 2025), naming AI-slop signatures and the five aesthetic dimensions of intentional design. This is the most authoritative anti-slop reference available and is directly citable from project KB content. T-001's authoring task transforms from "derive a discipline from scratch" to "cite the Anthropic discipline and add project-specific calibration." Anti-slop content lands as a `references/anti-slop.md` reference file rather than a standalone KB.

The primary decision the per-layer Design stage (`design-claude-code`) must resolve is **D-001 — single-vs-multiple KB structure**. Three options are honest: **Option A** (absorb all new content into a single expanded `KB-frontend-design`; conservative, KB count 17 → 18); **Option B** (four sibling design KBs aligned with mature-design-system field practice; KB count 17 → 22); **Option B'** (three sibling design KBs with design-system and component-architecture merged to reflect their natural coupling; KB count 17 → 21). Synthesis recommends **Option B**; Option B' is an acceptable alternative; Option A is the fallback if KB-count growth proves excessive.

`KB-storybook-platform` is locked separately as the project's fourth platform KB (user constraint at intake); D-003 sets its depth target at 2000-3500 lines, matching `KB-cc-platform`'s shape rather than the outsized `KB-github-actions-platform`. Storybook current version state is Storybook 10 (Nov 2025, ESM-only, typesafe CSF Factories); the KB targets Storybook 9+ as supported floor and documents CSF3 alongside the CSF Factories evolution.

## Findings

### F-001: Anti-slop has an authoritative Anthropic upstream reference

Anthropic's `frontend-design` skill (Nov 12, 2025) names AI-slop signatures (Inter, Roboto, system fonts; purple-on-white gradients; predictable layouts; cookie-cutter design; convergence on common choices including Space Grotesk) and the five aesthetic dimensions: Typography, Color & Theme, Motion, Spatial Composition, Backgrounds & Visual Details [research-notes/T-001-anti-slop.md]. The Anthropic frontend_aesthetics cookbook (Prithvi Rajasekaran, October 2025) names the underlying mechanism as **distributional convergence** [research-notes/T-001-anti-slop.md].

**Implication:** project anti-slop content is summary + project-specific calibration, not derivation. This is significantly lighter-weight than the PRD's original scoping suggested and reshapes D-002 (anti-slop placement) toward a reference file rather than a standalone KB.

### F-002: The existing `KB-frontend-design` is prose-first by design

Code-block density 0.8 per 100 lines — the lowest of any KB in the project [codebase-analysis.json]. 8 principles all backend-of-the-frontend (state, colocation, perf budgets, error boundaries, typing, framework grain, progressive enhancement, accessibility-as-baseline). The docstring explicitly states "no platform partner KB (frontend platforms vary widely: React, Vue, Svelte, SwiftUI, Jetpack Compose)" — a constraint that Option B's sibling-design-KB structure does not violate (no platform partner KB is being added; only design-side KBs).

### F-003: The platform-KB pattern is mature and unambiguous

Three existing platform KBs (cc, github-actions, codespaces) share a single shape: SKILL.md as the index/router + topical `references/<topic>.md` files. Code-block density 2.2-4.1 per 100 lines [codebase-analysis-report.md]. `KB-storybook-platform` slots in cleanly with no structural design questions outstanding.

### F-004: Field-standard design systems treat tokens and components as distinct foundations

Carbon, Material 3, GitHub Primer, and Salesforce Lightning all document design tokens as a separate concern from components, with the three-tier model (primitive → semantic → component) [research-notes/T-004-design-system-architecture.md]. Components consume the third token tier; the coupling is at the consumption layer, not at the conceptual layer. Mature systems treat tokens and components as distinct documentation areas — this is the field practice Option B aligns with [research-notes/T-005-component-architecture.md].

### F-005: UX + accessibility-as-flow extends, does not contradict, Principle 3

Existing `KB-frontend-design` Principle 3 covers accessibility-as-baseline (WCAG 2.2 AA conformance, semantic HTML, contrast, `prefers-reduced-motion`, focus indicators) [codebase-analysis.json:FA-001]. T-002's accessibility-as-flow is the cognitive-load and task-completion dimension — focus restoration after modal close, live-region choreography, error recovery for AT users [research-notes/T-002-ux-and-a11y-flow.md]. The two are complementary: baseline = "usable at all by AT users"; flow = "efficiently completable within their cognitive budget." Principle 3 stays in place; new flow content joins wherever D-001's chosen option places UX material.

### F-006: Storybook version state shifted between Research Plan authoring and Discovery Research

Storybook 9 (June 4, 2025) is the supported floor; Storybook 10 (November 5, 2025) is the current "latest" with typesafe CSF Factories as the next-generation API beyond CSF3 [research-notes/T-006-storybook.md]. CSF3 remains the broadly-deployed format. `KB-storybook-platform` targets Storybook 9+ floor and documents both CSF3 (current default) and CSF Factories (v10 evolution).

### F-007: FR-4 blast-radius bounded at exactly 2 sub-agents

`grep -lE 'KB-frontend-design' .claude/agents/*.md` returns precisely `design-frontend.md` and `design-composer.md` [codebase-analysis.json:FA-004]. No other agent file or orchestrator surface preloads `KB-frontend-design`. The FR-4 edits to add new KB references to these agents' `skills:` frontmatter is mechanical and bounded.

### F-008: Pedagogical-marker discipline already established as precedent

Zero KBs carry `disable-model-invocation: true` in actual frontmatter — the prior-session fix held [codebase-analysis.json:FA-003]. The 3 grep hits for that string in `KB-cc-design`, `KB-cc-platform`, and `KB-github-actions-platform` are all pedagogical body content (describing when the field WOULD be used) with markers per `pedagogical-marker-spec.md`. New anti-slop content (which names "AI slop" patterns like Inter / purple-gradient-on-white by name) follows the same marker discipline; the audit's Step 4 verification handles regex hits on pedagogical content correctly.

## Decisions

### D-001 (ADR-class): Structural choice for non-Storybook design content

**Frame.** New content from T-001 (anti-slop), T-002 (UX + a11y-flow), T-003 (UI/visual), T-004 (design-system), T-005 (component-architecture) must land in some KB structure. The decision: single-vs-multiple KB.

**Considered options:**

- **Option A — Single expanded `KB-frontend-design`.** All 5 areas absorbed as new reference files. Existing principles preserved. KB count: 17 → 18 (only `KB-storybook-platform` added).
- **Option B — Four sibling design KBs.** New: `KB-ux-design` (T-002), `KB-visual-design` (T-003 + anti-slop reference), `KB-design-system-design` (T-004), `KB-component-architecture-design` (T-005). Existing `KB-frontend-design` retained for backend-of-frontend + a11y baseline. KB count: 17 → 22.
- **Option B' — Three sibling design KBs.** Same as B but `KB-design-system-design` absorbs both T-004 and T-005 content (reflecting token-component coupling). KB count: 17 → 21.

**Recommended option: Option B.**

**Rationale.** Aligns with mature-design-system field practice (Carbon / Material 3 / Primer / Salesforce all treat tokens and components as distinct foundations) [research-notes/T-004-design-system-architecture.md]. Each KB stays right-sized (the alternative — a single 3000+ line `KB-frontend-design` under Option A — hits navigability limits quickly). Preloadability per-domain at design-time: a future feature that only touches component-architecture can preload `KB-component-architecture-design` without paying for design-system or UX content. The existing `KB-frontend-design` docstring's "no platform partner KB" constraint is not violated by adding design-side siblings.

**Costs to acknowledge.** KB-count growth (+5 in this round: four design siblings plus `KB-storybook-platform`) is significant. `design-frontend.md`'s `skills:` list grows from 4 to 8+ items. Each new SKILL.md adds 100-200 tokens of preload cost. The per-layer Designer must accept this growth budget.

**Fallback paths.** If KB-count growth is unacceptable: Option B' merges T-004 + T-005 (lose some domain separation; honest reflection of the coupling); Option A absorbs all (most conservative; bet against the single-KB navigability problem). The per-layer Designer should choose with the codebase-analysis-report.md's "blast-radius assessment" in hand — Option B's 22-KB count is the upper bound being proposed.

**ADR.** Per FR-5, only `design-composer` authors ADRs. The chosen option becomes **ADR-0024** in the design-composer's output.

### D-002: Anti-slop placement

**Frame.** Where does anti-slop content live, given the Anthropic upstream reference does most of the load-bearing work?

**Considered options:**

- Standalone `KB-anti-slop-design` (new sibling).
- `references/anti-slop.md` inside `KB-visual-design` (Option B's recommendation).
- Cross-cutting markers across multiple KBs (anti-slop content sprinkled where each topic mentions aesthetic defaults).

**Recommended option: `references/anti-slop.md` inside `KB-visual-design`** (or inside `KB-frontend-design` under Option A; inside the visual KB under Option B / B').

**Rationale.** Standalone KB is overkill — the Anthropic upstream carries the discipline; project-side content amounts to summary + calibration. Cross-cutting fragments the concern. A reference file inside the aesthetic-owning KB keeps the citation chain natural (visual KB → anti-slop reference → Anthropic upstream).

### D-003: `KB-storybook-platform` depth target

**Frame.** How deep does the v1 Storybook KB go?

**Recommended option:** 2000-3500 lines at v1, matching `KB-cc-platform`'s relative shape (2624 lines across 9 files) rather than the outsized `KB-github-actions-platform` (6719 lines across 20 files). Cover: story format (CSF3 default + CSF Factories evolution), addons (the canonical 8 — essentials, controls, a11y, viewport, interactions, docs, themes, coverage), MDX docs composition, VRT (Chromatic cloud + `@storybook/test-runner` local + Vitest integration from Storybook 9), composition via `ref`. Code-block density 3-5 per 100 lines (intake constraint: syntax IS the knowledge for the Storybook KB).

**Rationale.** `KB-cc-platform`'s shape is the proven precedent for a self-contained tool's platform KB. `KB-github-actions-platform` is outsized because GitHub Actions has a broader primitive surface (5 primitives + reusable workflows + composite actions + OIDC + matrix strategies + ...). Storybook's surface fits cc-platform's depth more closely.

### D-004: Existing Principle 3 (a11y baseline) + new accessibility-as-flow content

**Frame.** Does the new a11y-as-flow content restructure Principle 3, or extend it?

**Recommended option:** Extend. Principle 3 stays in `KB-frontend-design` as is. New a11y-as-flow content joins `KB-ux-design` under Option B (or stays in `KB-frontend-design` under Option A). No supersession of Principle 3 needed.

**Rationale.** ADR-0005 supersession overhead is avoided. The complementary framing (baseline vs. flow) is honest and well-grounded in field practice — Heydon Pickering's *Inclusive Components* makes exactly this distinction [research-notes/T-002-ux-and-a11y-flow.md].

### D-005: Sibling sub-agents for `design-frontend`

**Frame.** Should `design-frontend` gain sibling sub-agents (e.g., `design-ux`, `design-visual`) at this round?

**Recommended option:** No. Defer.

**Rationale.** This round adds *knowledge content*, not orchestration. The single `design-frontend` sub-agent preloads from multiple KBs under any option (FR-4's mechanism). Sibling sub-agents become useful if parallel domain-specific drafting becomes a bottleneck — a downstream architectural concern orthogonal to this feature.

### D-006: Pedagogical-marker application scope

**Frame.** Where do pedagogical markers go in the new content?

**Recommended option:** Surgical application. Anti-slop content gets the heaviest marker density (it names AI-slop patterns by name — Inter, Space Grotesk, purple-gradient-on-white). Visual content gets medium density (negative-references to AI defaults). Other content (UX, design-system, component-architecture, Storybook) gets minimal or no markers — the content doesn't trip audit regex checks.

**Rationale.** Per `pedagogical-marker-spec.md`, markers are surgical not blanket. The audit's Step 4 verification handles the high-marker areas correctly (precedent: 3 KBs already carry pedagogical references to `disable-model-invocation`); lower-marker areas don't need them.

## Constraints Honored

Hard constraints declared at intake:

1. **Framework-agnostic, web only.** Honored — T-002 through T-005 content is framework-agnostic; React used illustratively only where examples demand it. No mobile/native.
2. **Audience: mixed — brief foundations + deep opinions.** Honored — each research note leads with canonical references (foundations) and goes deep on opinions and discipline.
3. **Voice bar: `KB-cc-platform` senior-engineer-handbook.** Honored — research notes use declarative, opinionated voice; tables for trade-offs; prose for discipline; minimal code.
4. **Design-side KBs prose-first; inline code RARE.** Honored — research notes for T-002, T-004 carry zero code blocks; T-001, T-003 have 1-2 illustrative blocks; T-005 has the most given component-pattern syntax. KB authoring will follow.
5. **`KB-storybook-platform` locked as new platform KB.** Honored — D-003 builds on this; not re-litigated.
6. **Storybook KB allows code where syntax IS knowledge.** Honored — T-006 research note carries 4 code blocks; KB authoring will exceed design-KB density per intake.
7. **Scope explicitly OUT.** Honored — none of the 6 research notes drifts into mobile/native, UX writing/microcopy, brand identity, marketing-style motion, or pedagogical-from-scratch teaching.

## Limitations

1. **Substrate options for D-001 are not exhaustively enumerated.** Synthesis surfaces A, B, B'. A per-layer Designer may identify Option C / D variants (e.g., 2-KB split that merges UX + a11y-as-flow with visual). Recommendation: start from B; consolidate downward if KB-count growth feels excessive.
2. **No quantitative data on context-cost impact of KB-count growth.** Option B adds 4 SKILL.md descriptions to the `design-frontend` preload set. Practical token impact is small but unmeasured at synthesis time. Per-layer Design should accept (each SKILL.md description is 100-200 tokens; total 400-800 token overhead) or measure if concerned.
3. **CSF Factories adoption rate uncertain.** Storybook 10's CSF Factories is the next-generation API; broadly-deployed format remains CSF3. `KB-storybook-platform` documents both; a future revision may shift emphasis as CSF Factories adoption matures.
4. **Anthropic's `frontend-design` skill versioning is not under project control.** The skill at `/mnt/skills/public/` is Anthropic-managed; if Anthropic updates or removes it, the citation chain breaks. Project KB content should cite by name + acknowledge upstream dependency in a "References" section.
5. **No dissent_evidence recorded.** All 6 research notes' findings converge with the codebase-analysis findings; no significant disagreement between sources was surfaced during research. This is expected for a knowledge-authoring feature (the topic areas have stable canonical references), but worth noting as a clean state.

## Sources

| Source | Type | Disposition |
|---|---|---|
| `prd-v1.md@1.0.0` | feature input | upstream requirement |
| `research-plan.md@1.0.0` | discovery input | upstream scope |
| `codebase-analysis.json@1.0.0` (6 focusAreas) | codebase | confirmed |
| `codebase-analysis-report.md@1.0.0` | codebase | confirmed |
| `research-notes/T-001-anti-slop.md@1.0.0` | external research | AC satisfied; cites Anthropic upstream |
| `research-notes/T-002-ux-and-a11y-flow.md@1.0.0` | external research | AC satisfied; cites NN/g + WCAG 2.2 + Pickering + Sutton |
| `research-notes/T-003-ui-visual-design.md@1.0.0` | external research | AC satisfied; cites Material 3 + Apple HIG + Refactoring UI + Modular Scale + Utopia |
| `research-notes/T-004-design-system-architecture.md@1.0.0` | external research | AC satisfied; cites Carbon + Material 3 + Primer + Salesforce + Style Dictionary + Nathan Curtis |
| `research-notes/T-005-component-architecture.md@1.0.0` | external research | AC satisfied; cites Frost + Radix + React Aria + Headless UI + Kent C. Dodds + Sébastien Lorber |
| `research-notes/T-006-storybook.md@1.0.0` | external research | AC satisfied; cites storybook.js.org + chromatic.com + CSF Factories RFC |
| `/mnt/skills/public/frontend-design/SKILL.md` | external authoritative | upstream reference (Anthropic-managed) |
