---
id: IC-frontend-design-knowledge-r1
version: 1.0.0
status: draft
feature_slug: frontend-design-knowledge-r1
user_token: <pending Intent Confirmation Gate>
generated: 2026-05-20T22:00:00Z
generated_by: intake-intent-clarifier
---

# Intent Clarification: Frontend Design Knowledge Enhancement — Round 1

## Contents

- [x] Purpose
- [x] Source
- [x] Initial Interpretation
- [x] Clarifying Questions and Answers
- [x] Clarified Intent
- [x] Scope Posture
- [x] Stakeholder Posture (Preliminary)
- [x] Success Posture (Preliminary)
- [ ] Confirmation
- [x] Open Items (Pending PRD Authoring)

## Purpose

The Intent Clarification document is the first artifact in the feature-pipeline. It captures the user's intent before any PRD or design work begins. It is NOT a requirements document. It is NOT a design document. It is a structured record of: what does the user want, in their own words, with ambiguities surfaced and resolved.

This document gates progression to PRD Authoring. The user must explicitly confirm the clarified intent via the Intent Confirmation Gate before the orchestrator proceeds.

## Source

The user wants the feature pipeline to "incorporate Anti-slop and proper UX/UI design knowledge; understand design system architecture, component architecture, and Storybook." The accompanying session-continuation prompt elaborates the six topic areas the existing `KB-frontend-design` does not yet cover and frames this run as the project's first real (non-synthetic) execution of `recipe-feature-pipeline`, doubling as integration test #2 after the `/healthz` simulation.

## Initial Interpretation

Before clarifying questions, the clarifier read the raw request as: enhance the project's frontend knowledge by authoring (or extending) KBs and possibly sub-agents that cover six topic areas absent from the current `KB-frontend-design` — anti-slop aesthetic discipline, UX design, UI/visual design, design system architecture, component architecture, and Storybook. The current KB covers state separation, colocation, accessibility baseline, performance budgets, error boundaries, typing, and framework grain; the visual, interaction, system-architecture, and tooling layers are absent. The feature itself runs through `recipe-feature-pipeline`. Because it edits `.claude/skills/` and `.claude/agents/` (and not application UI), the **Claude Code / Project Filesystem** layer is in scope and the **Frontend** layer is out of scope.

What the initial interpretation was about to bake in without confirmation: that the new knowledge would be React-first (the implicit lean of the existing KB), that it would teach UX/UI foundations from scratch, and that "anti-slop" might silently absorb adjacent territory like UX writing or brand identity. Those assumptions are exactly what the three clarifying questions surfaced.

## Clarifying Questions and Answers

| # | Ambiguity | Question Asked | User Answer | Resolved? |
|---|---|---|---|---|
| 1 | Framework / platform posture (the existing KB hedges "framework-agnostic" but its examples lean React) | Framework / platform scope. Which framework posture and which platforms? Options: (a) React-first web only; (b) Framework-agnostic, web only (React in examples); (c) Framework-agnostic, web + mobile/native (SwiftUI, Compose, RN). | (b) Framework-agnostic, web only (React in examples) | [x] |
| 2 | Audience depth — senior-engineer-handbook bar versus pedagogical introduction of fundamentals | Audience depth. How much foundational material should the new KBs introduce? Options: (a) Senior-handbook (assume fundamentals); (b) Pedagogical (teach Nielsen's 10, atomic design, token tiers from scratch); (c) Mixed (brief foundations callouts, deep on opinions). | (c) Mixed — brief foundations callouts, deep on opinions | [x] |
| 3 | Scope boundary against adjacent topics (UX writing, brand identity, scroll-driven hero motion) and the existing accessibility-as-baseline material | Scope boundary. What's the hard fence around the six named topics? Options: (a) Strictly the six topics; (b) Six topics + accessibility-as-flow merged into UX; (c) Six + something else (reply explaining). | (b) Six topics + accessibility-as-flow (merged into UX) | [x] |

## Clarified Intent

Enhance this project's frontend-design knowledge by authoring KB content (and making whatever `.claude/agents/` skill-list edits are required) that covers six topic areas: (1) anti-slop aesthetic discipline — resistance to generic AI-UI aesthetics; (2) UX design — information architecture, user flows, usability heuristics, cognitive load, error prevention and recovery, and accessibility-as-flow (cognitive load on AT users, keyboard task completion, error recovery for screen-reader paths) merged in as a UX concern; (3) UI / visual design — type scales, color systems, spacing, iconography, motion, hierarchy, density, responsive; (4) design system architecture — tokens primitive → semantic → component, theming, semver; (5) component architecture — atomic design, compound, headless, controlled/uncontrolled, polymorphic, slot, ref forwarding, prop API; (6) Storybook — CSF3, args/argTypes, play functions, decorators, MDX, addons, composition, visual regression. The knowledge is framework-agnostic in its discipline statements but uses React in illustrative code; mobile/native is out of scope. Audience is the working pipeline (and senior engineers behind it): brief foundations callouts where needed, deep on opinionated takes — matching the senior-handbook voice of `KB-cc-platform`. The structural choice about KB shape (split into multiple KBs vs. expand `KB-frontend-design`; whether a `KB-storybook-platform` joins `KB-cc-platform` / `KB-github-actions-platform` / `KB-codespaces-platform` as the project's fourth platform-knowledge KB) is **deferred to Stage 5 (per-layer Design)** — `design-claude-code` will decide with reviewer pressure.

## Scope Posture

### What's in scope

- Anti-slop aesthetic discipline as authored knowledge content
- UX design knowledge (incl. accessibility-as-flow merged into the UX discipline)
- UI / visual design knowledge
- Design system architecture knowledge
- Component architecture knowledge
- Storybook knowledge (specific tool, natural fit for the platform-knowledge KB pattern if Stage 5 elects it)
- Whatever `.claude/agents/` edits the resulting Blueprint requires — minimally to `design-frontend.md`'s `skills:` preload list; possibly `design-composer.md`; possibly new sibling sub-agents if Stage 5 elects them
- Pedagogical-marker application per `auditing-cc-configs/references/pedagogical-marker-spec.md` for anti-slop "don't do this" examples and similar
- Authoring at `KB-cc-platform`'s voice / depth bar
- Layer Scope: **Claude Code / Project Filesystem** layer ONLY

### What's NOT in scope (explicitly excluded)

- The **Frontend** layer itself — no UI is being built; we are authoring knowledge content
- Mobile / native UI knowledge (SwiftUI, Jetpack Compose, React Native)
- React-framework-specific knowledge beyond illustrative code examples (no React-Server-Components deep-dives, no React-specific concurrent-mode chapters)
- UX writing / microcopy / content strategy
- Brand identity and logo systems
- Marketing-style scroll-driven hero animations and other purely-presentational motion territory
- Pedagogical-from-scratch teaching of fundamentals (Nielsen's 10 referenced briefly, not taught from zero)
- The structural KB-shape decision itself (this is a Stage 5 design output, not an intake pre-decision)

### What's undecided (deferred to PRD or later)

- Whether the existing `KB-frontend-design` content is preserved verbatim, restructured, or partially absorbed into successor KBs
- Whether Storybook is authored as its own KB (`KB-storybook-platform`) or folded into a design-layer KB
- Whether `design-frontend` gains sibling sub-agents (e.g., a hypothetical `design-frontend-visual`) or remains a single per-layer Designer with an expanded preload list
- Which specific Nielsen heuristics, atomic-design tiers, and design-token specifics get cited (level of curation)
- Whether the project's pedagogical-marker-spec needs additions for design-language anti-pattern content

## Stakeholder Posture (Preliminary)

- **Future `design-frontend` (the per-layer Designer sub-agent):** the primary consumer; needs actionable design discipline at preload time for any future Frontend-touching feature
- **Future `design-composer`:** needs cross-layer integration patterns (e.g., how Frontend design-system token decisions integrate with API contracts and Backend session models)
- **Future `plan-author` / reviewers (`shared-document-reviewer`, `review-architecture-auditor`):** need shared vocabulary for UI-quality and Storybook-coverage acceptance checks
- **The user (project owner) and any future contributors:** need a precedent for how UX/UI knowledge is structured in this project; this run sets it

## Success Posture (Preliminary)

- A future Frontend-touching pipeline run produces design recommendations that resist generic AI-UI aesthetics (anti-slop discipline applied and visible in the Blueprint's Frontend Design subsection).
- Acceptance Criteria authored for Frontend features include explicit token-system, component-architecture, and Storybook commitments — not just functional ACs.
- The new KB content passes `cc-audit` cleanly (post Step-4 verification); anti-slop pedagogical content carries the markers from `pedagogical-marker-spec.md` so future audits don't re-flag it.
- KB voice matches `KB-cc-platform`'s senior-engineer-handbook bar.
- The pipeline run itself, viewed as integration test #2, surfaces any v4.3.1 machinery defects into a sibling ADR alongside ADR-0024 (same pattern as ADR-0023 after `/healthz`).

## Confirmation

[Awaiting user at the Intent Confirmation Gate. The orchestrator's `AskUserQuestion` captures the confirmation token, which is recorded in the frontmatter `user_token` field on this document at Gate pass.]

## Open Items (Pending PRD Authoring)

- Precise topic enumeration within each of the six areas (which Nielsen heuristics get explicit treatment; which atomic-design tiers warrant standalone sections; which design-token specifics to cite)
- Whether existing `KB-frontend-design` content is preserved verbatim or restructured (Stage 5 decides shape; PRD captures the in-scope set)
- Which acceptance test patterns the pipeline should require of Frontend features going forward (e.g., must any Frontend AC declare a token-system commitment? a Storybook-story commitment?)
- Whether `auditing-cc-configs`'s pedagogical-marker-spec needs new marker types for design-language anti-pattern content
- Whether this run produces v4.3.2 (knowledge-content addition, semver patch) or v4.4.0 (per ADR-0005 — if Stage 5 elects structural changes substantial enough to warrant a minor bump)
