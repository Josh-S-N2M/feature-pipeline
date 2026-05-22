---
id: RP-frontend-design-knowledge-r1
version: 1.0.0
status: draft
feature_slug: frontend-design-knowledge-r1
derived_from_prd: working/feature/frontend-design-knowledge-r1/prd-v1.md
derived_prd_version: 1.0.0
derived_prd_user_token: confirmed-2026-05-20T22-30-00Z
generated: 2026-05-20T22:50:00Z
generated_by: discovery-plan-author
---

# Research Plan: Frontend Design Knowledge Enhancement — Round 1

## Contents

- [x] Feature reference
- [x] Information needs inventory
- [x] Codebase research scope
- [x] External research topics
- [x] Topics explicitly NOT researched
- [x] Estimated effort
- [x] Open questions for human resolution

## Feature reference

- **Feature slug:** `frontend-design-knowledge-r1`
- **PRD path:** `working/feature/frontend-design-knowledge-r1/prd-v1.md`
- **PRD version:** 1.0.0
- **PRD gate state:** approved at 2026-05-20T22:45:00Z (PRD Approval Gate); user_token `confirmed-2026-05-20T22-30-00Z`
- **Inherited ADRs in scope:**
  - **ADR-0005** — append-only supersession (constrains how existing `KB-frontend-design` content may be restructured)
  - **ADR-0011** — KB-documentation-criteria as canonical templates skill
  - **ADR-0017** — shared-document-reviewer integration (5 invocation points)
  - **ADR-0019** — naming convention (`KB-` prefix; phase-prefixed sub-agents)
  - **ADR-0020** — KB structure (SKILL.md + references/; one KB per domain)
  - **ADR-0021** — discovery phase architecture (this Plan's authoring discipline)
  - **ADR-0022** — sub-agent reasoning configuration (effort and skills semantics)
  - **ADR-0023** — discipline refinements from `/healthz` integration test (5th disposition `designer-general-knowledge`; per-FR AC check; annotation-check reassignment; substrate two-mode)
- **Applicable KBs:**
  - `KB-frontend-design` — existing design discipline (preserved/restructured)
  - `KB-cc-design` + `KB-cc-platform` — voice/depth/structure bar (the most mature paired KBs in the project)
  - `KB-github-actions-platform` + `KB-codespaces-platform` — platform-KB pattern (for `KB-storybook-platform`)
  - `KB-documentation-criteria` — templates, layer taxonomy, EARS, rationale brief
  - `KB-review-disciplines` — Gate 0/1 procedure, architecture audit
  - `auditing-cc-configs/references/pedagogical-marker-spec.md` — marker format for anti-slop content

## Information needs inventory

15 information needs extracted from PRD v1.0.0. Disposition triage per ADR-0021 (five-way: covered-by-KB / covered-by-ADR / codebase-topic / designer-general-knowledge / external-research-topic).

| Need ID | Description | Downstream consumer | Disposition |
|---|---|---|---|
| **IN-001** | What is the existing `KB-frontend-design` content shape, voice, code-density, and reference-file structure? | `design-claude-code` (per-layer Design — must match the bar); Synthesis (option enumeration A vs B) | `codebase-topic` |
| **IN-002** | What is the existing platform-KB pattern (SKILL.md frontmatter, `references/` layout, voice, code-density) as exemplified by `KB-cc-platform`, `KB-github-actions-platform`, `KB-codespaces-platform`? | `design-claude-code` (for `KB-storybook-platform`'s structural template); Synthesis | `codebase-topic` |
| **IN-003** | What is the `pedagogical-marker-spec.md` format, and how is existing pedagogical content marked across the project's KBs? | `design-claude-code` (must apply markers per FR-5); execution-phase audit | `codebase-topic` |
| **IN-004** | What is the established anti-slop / intentional-design discipline body of knowledge? What distinguishes intentional design from generic AI-default aesthetics? | `design-claude-code` (FR-1-a authoring); Synthesis (option framing) | `external-research-topic:T-001` |
| **IN-005** | What is the established UX design knowledge body — usability heuristics (Nielsen's 10), IA patterns, user-journey frameworks, cognitive load, error prevention/recovery, plus accessibility-as-flow patterns (AT cognitive load, keyboard task completion, focus management, error recovery for screen-reader paths)? | `design-claude-code` (FR-1-b authoring) | `external-research-topic:T-002` |
| **IN-006** | What is the established UI / visual design knowledge body — type scales, color systems (LCH/OKLCH/HSL with contrast), spacing systems (4pt/8pt grids), iconography, motion design (easing, duration, choreography), visual hierarchy, density, responsive design? | `design-claude-code` (FR-1-c authoring) | `external-research-topic:T-003` |
| **IN-007** | What is the established design system architecture knowledge body — design token tiers (primitive → semantic → component), theming (light/dark, brand variants), the tokens → CSS variables → components chain, semver for design systems, polyglot delivery? | `design-claude-code` (FR-1-d authoring) | `external-research-topic:T-004` |
| **IN-008** | What is the established component architecture knowledge body — atomic design (Frost's 5 tiers), compound components, headless components (Radix, React Aria), controlled vs uncontrolled, polymorphic / `as` prop, slot patterns, ref forwarding, prop API design? | `design-claude-code` (FR-1-e authoring) | `external-research-topic:T-005` |
| **IN-009** | What is the established Storybook 9 / CSF3 knowledge body — story format, args / argTypes / parameters / play functions, decorators, MDX docs composition, canonical addons (controls, a11y, viewport, interactions, docs), Chromatic visual regression, test-runner integration, multi-package composition? | `design-claude-code` (FR-1-f authoring; `KB-storybook-platform`'s contents) | `external-research-topic:T-006` |
| **IN-010** | What naming convention does the project apply to new KBs (specifically `KB-storybook-platform`)? | `design-claude-code` (FR-3-a) | `covered-by-ADR:ADR-0019` |
| **IN-011** | What is the structural pattern for new KBs (SKILL.md as entry point, `references/` directory)? | `design-claude-code` (FR-3-a) | `covered-by-ADR:ADR-0020` |
| **IN-012** | How does the project's append-only supersession discipline apply if existing `KB-frontend-design` content is restructured under Option A or Option B? | `design-claude-code` (structural decision); Plan Authoring (task ordering) | `covered-by-ADR:ADR-0005` |
| **IN-013** | Which sub-agents currently preload `KB-frontend-design` via their `skills:` frontmatter, and what is the blast-radius of modifying that frontmatter? | `design-claude-code` (FR-4); Plan Authoring | `codebase-topic` |
| **IN-014** | What is the project's KB authoring discipline — frontmatter schema, valid-vs-invalid field combinations (including the `disable-model-invocation` / `user-invocable` distinction), references-file conventions? | `design-claude-code` (FR-3, FR-4, FR-5) | `covered-by-KB:KB-cc-design:references/patterns-and-anti-patterns.md` + `codebase-topic` for verification |
| **IN-015** | What audit conventions apply to new KB content — which `auditing-*` skills run; how Step 4 verification disposes of regex hits on pedagogical content? | execution-phase audit pass | `covered-by-KB:auditing-cc-configs:SKILL.md` + `auditing-cc-configs/references/pedagogical-marker-spec.md` |

**Summary:** 5 codebase-topic, 6 external-research-topic (at the 6-topic budget), 3 ADR-covered, 1 KB-covered, 0 designer-general-knowledge.

**Why no `designer-general-knowledge` disposition.** Per ADR-0023's smell test ("if you find yourself reaching for `designer-general-knowledge` for >50% of information needs, re-audit"), I considered whether any of the six external topics could be `designer-general-knowledge`. The answer is no: each of the six is a substantial body of community knowledge that a competent generalist *might* partially know but that the pipeline needs *codified in KBs* at preload time so `design-frontend` doesn't have to reconstruct it. The user's intent — set at the Intent Confirmation Gate — is for this knowledge to live in KBs, not in implicit designer rationale.

## Codebase research scope

Single invocation of `discovery-codebase-researcher`. The codebase is the project's own `.claude/` directory (this is integration test #2 — the pipeline runs against itself).

### Touch points

- `.claude/skills/KB-frontend-design/` — existing content (SKILL.md, `references/principles.md`, `references/patterns-and-anti-patterns.md`). Subject of IN-001.
- `.claude/skills/KB-cc-platform/` — voice/depth bar reference per AC-FR-6-a. Subject of IN-002.
- `.claude/skills/KB-cc-design/` — paired discipline-side example; IN-014 reference for KB authoring conventions.
- `.claude/skills/KB-github-actions-platform/` and `.claude/skills/KB-codespaces-platform/` — platform-KB pattern examples for IN-002.
- `.claude/skills/auditing-cc-configs/references/pedagogical-marker-spec.md` — IN-003.
- `.claude/skills/auditing-cc-configs/SKILL.md` — IN-015 audit conventions.
- `.claude/agents/design-frontend.md` — current `skills:` list (already confirmed: `[KB-frontend-design, KB-documentation-criteria, KB-general-coding-principles, KB-review-disciplines]`). FR-4 edit target.
- `.claude/agents/design-composer.md` — current `skills:` list; FR-4 edit target if cross-layer integration warrants.

### Blast-radius questions

- Which sub-agents reference `KB-frontend-design` in their `skills:` frontmatter? (Pre-confirmed: `design-frontend`, `design-composer`. The researcher verifies and confirms no other references.)
- Which references to `KB-frontend-design` exist in agent prose, ADRs, or the orchestrator? (Plan-authoring concern: are any prose references brittle to a structural rename?)
- What is the blast-radius of restructuring `KB-frontend-design` content under Option B (e.g., moving accessibility material from `principles.md` to a new `KB-ux-design`)?
- What is the blast-radius of adding `KB-storybook-platform` to `design-frontend.md`'s `skills:` list — any agent-level token-budget concerns from the additional preload?

### Convention discovery

For each touch-point KB, the researcher records:

- **Frontmatter schema** — required fields (`name`, `description`, `allowed-tools`), optional fields (`user-invocable`, `disable-model-invocation`, etc.), and the project's convention on which combinations are valid for design KBs vs. platform KBs.
- **`references/` file naming** — current pattern is `principles.md` + `patterns-and-anti-patterns.md` for design KBs; platform KBs vary (`extensions.md`, etc.).
- **`## Contents` section convention** — each SKILL.md and reference file leads with a `## Contents` H2 checklist.
- **`## When this KB is loaded` section** — design KBs document which sub-agents preload them.
- **Prose voice indicators** — sentence length, paragraph density, use of imperative vs. descriptive, presence of `Discipline:` and `Anti-pattern:` labeled callouts.
- **Code-block density per 100 lines** (already characterized in the PRD's Background; researcher verifies the figures hold for the latest content).

### Specific queries

- `grep -lE 'KB-frontend-design' .claude/agents/` — exhaustive list of sub-agents preloading `KB-frontend-design`.
- `grep -lE 'KB-frontend-design' .claude/skills/*/SKILL.md .claude/skills/*/references/*.md` — exhaustive list of KBs cross-referencing `KB-frontend-design`.
- `grep -nE '^disable-model-invocation:' .claude/skills/*/SKILL.md` — verify no KB carries the field in frontmatter (the prior session's fix). Body-content references (per IN-003 pedagogical marker pattern) are acceptable.
- `wc -l .claude/skills/KB-cc-platform/SKILL.md .claude/skills/KB-cc-platform/references/*.md` — file-size distribution for `KB-cc-platform` to set a target shape for new KBs.
- Compare `## Contents` H2 patterns across all platform KBs to extract the canonical structure for `KB-storybook-platform`.

## External research topics

6 of 6 budget. Each topic is mapped to one FR-1 sub-AC.

### T-001: Anti-slop aesthetic discipline (maps to AC-FR-1-a)

- **Research question:** What distinguishes intentional, system-grounded UI design from generic AI-default aesthetics? What are the recognizable signatures of "AI slop" UI (purple-gradient-on-white, Inter-everywhere, default-rounded-shadcn, etc.) and what are the calibration points for intentional design (Linear, Stripe, Vercel, Arc, Notion, Figma)?
- **KB gap justification:** `KB-frontend-design` covers state separation, colocation, a11y baseline, perf budgets, error boundaries, typing, framework grain — explicitly nothing on aesthetic discipline or anti-slop. No other KB covers this either. Not `designer-general-knowledge` because the anti-slop framing is a recent, specialized discourse (post-2023 in response to AI-default UI tools) that a generalist designer cannot be expected to articulate without sourcing.
- **Acceptance criteria:**
  - Names 5+ recognizable AI-slop signatures with concrete pattern descriptions (typography choice, color palette, motion conventions, layout defaults).
  - Names 3+ intentional-design exemplars with 2+ specific design decisions each that distinguish them from slop.
  - Identifies 3-5 distinguishing principles of intentional design (bold conceptual direction; intentional typography choice; intentional color decisions; restrained / purposeful motion; spatial composition).
  - Cites 5+ reputable sources (designer-written essays / blog posts / podcasts) — not listicles.
- **Source constraints:** Designer-authored essays and blog posts (e.g., Refactoring UI, Brad Frost, Heydon Pickering, Linear blog, Figma blog, Stripe Press), design publications (A List Apart, Smashing Magazine where written by named designers). NOT marketing pages of design tools. NOT generic listicles.

### T-002: UX design + accessibility-as-flow (maps to AC-FR-1-b)

- **Research question:** What are Nielsen's 10 usability heuristics with one-line summaries each? What are canonical user-journey-mapping frameworks (Norman's 7 stages of action, Service Blueprint pattern)? What are the canonical IA patterns (card sort, tree test, content inventory)? Specifically for accessibility-as-flow: what patterns address cognitive load on AT users, keyboard task completion, focus management for modals/menus, error recovery for screen-reader paths, and validation announcement?
- **KB gap justification:** `KB-frontend-design` Principle 3 covers accessibility-as-baseline (WCAG 2.2 AA conformance, semantic HTML, contrast, `prefers-reduced-motion`, focus indicators). It does NOT cover accessibility-as-flow — the cognitive-load and task-completion dimension. No other KB covers UX heuristics or journey mapping.
- **Acceptance criteria:**
  - Lists Nielsen's 10 heuristics with one-line summaries each.
  - Names 3+ user-journey / IA frameworks with their canonical use cases.
  - Identifies 5+ accessibility-as-flow patterns with concrete examples (focus restoration after modal close; error-recovery for inline validation in screen-reader contexts; etc.).
  - Cites at least Nielsen Norman Group, WCAG 2.2 techniques, and 2+ accessibility-as-flow specialists (e.g., Heydon Pickering, Marcy Sutton).
- **Source constraints:** Nielsen Norman Group articles, WCAG official guidance, Inclusive Design Patterns (Pickering), Sarah Drasner / Marcy Sutton talks and posts, Service Design Network. Not academic-only — practitioner-authoritative.

### T-003: UI / visual design (maps to AC-FR-1-c)

- **Research question:** What are 3+ canonical type scale systems (modular scale ratios; fluid type with `clamp()`; Material Design type scale)? What are the modern color systems (LCH, OKLCH, HSL with contrast considerations) and when each applies? What is the 4pt/8pt grid discipline? What are 3+ motion choreography references (Material Motion, Apple HIG motion, Disney 12 principles applied to UI)? Responsive design — canonical breakpoints, container queries, fluid type/space?
- **KB gap justification:** `KB-frontend-design` has zero content on type, color, spacing, iconography, motion, or responsive design. No other KB covers this.
- **Acceptance criteria:**
  - Names 3+ type scale systems with example ratios / values.
  - Names 2-3 modern color systems with the rationale for choice (gamut, perceptual uniformity, contrast computation).
  - Identifies the 4pt vs 8pt grid trade-off and when each applies.
  - Names 3+ motion references with concrete easing / duration ranges and choreography patterns.
  - Identifies responsive design conventions: breakpoints vs. container queries, fluid type with `clamp()`.
- **Source constraints:** Material Design 3 official docs, Apple HIG, Refactoring UI (Adam Wathan / Steve Schoger), Practical Typography (Butterick), Modular Scale, OKLCH for the web (Lea Verou / Erik Kennedy). Official documentation primary.

### T-004: Design system architecture (maps to AC-FR-1-d)

- **Research question:** What are the canonical token tier examples (primitive → semantic → component)? Concrete examples from IBM Carbon, Material Design 3, GitHub Primer, Salesforce Lightning, Atlassian. What is the tokens → CSS variables → components delivery chain? Theming approaches (CSS variables, JS-in-JSON, build-time substitution). What is the semver discipline for design systems (breaking changes: removed tokens, renamed components, etc.)? Polyglot delivery (web + native).
- **KB gap justification:** Design system architecture is genuinely novel for this codebase — no KB covers tokens, theming, or design-system semver. Not `designer-general-knowledge` because token tier organization and semver-for-design-systems are specialist knowledge that varies meaningfully across mature systems (Carbon vs. Material vs. Primer all make different choices).
- **Acceptance criteria:**
  - Cites 3+ canonical token tier examples with concrete primitive → semantic → component mappings.
  - Identifies 3+ theming delivery approaches with trade-offs.
  - Names the semver discipline for design systems with 3+ examples of changes that warrant major / minor / patch bumps.
  - Identifies the polyglot delivery question (Style Dictionary, Theo, or build-time token transformation pipelines).
- **Source constraints:** IBM Carbon documentation, Material Design 3, GitHub Primer, Salesforce Lightning, Atlassian Design System, Style Dictionary docs. Brad Frost / Nathan Curtis posts on design systems. Official documentation primary.

### T-005: Component architecture (maps to AC-FR-1-e)

- **Research question:** What are Brad Frost's atomic design 5 tiers (atoms, molecules, organisms, templates, pages) with concrete examples? What are the canonical headless component libraries (Radix UI, React Aria, Headless UI) and their pattern surfaces? What is the compound component pattern, slot pattern, polymorphic / `as` prop pattern, controlled-vs-uncontrolled distinction, ref forwarding convention, and prop API design discipline (variant + size; truthy boolean props; consistent defaults)?
- **KB gap justification:** `KB-frontend-design`'s `patterns-and-anti-patterns.md` covers compound components and render-props briefly (one code block each). It does NOT cover atomic design tiers, headless libraries by name, slot patterns, polymorphic `as`, ref forwarding, or prop API design. The existing coverage is sparse compared to the body of community knowledge.
- **Acceptance criteria:**
  - Names atomic design's 5 tiers with one concrete example each.
  - Names 3+ headless component libraries with their canonical pattern (e.g., Radix UI's compound dialog primitives).
  - Identifies each of these patterns with one concrete usage example: compound, slot, polymorphic `as`, controlled/uncontrolled, ref forwarding, prop API design.
  - Cites 3+ specialist authors (e.g., Brad Frost on atomic design; Sébastien Lorber / Tanner Linsley / Diego Haz on component patterns).
- **Source constraints:** Radix UI docs, React Aria docs, Headless UI docs, Brad Frost's atomicdesign.bradfrost.com, specialist blog posts. Official library documentation primary.

### T-006: Storybook 9 / CSF3 + addons + composition + VRT (maps to AC-FR-1-f)

- **Research question:** What is CSF3 (Component Story Format 3) — the canonical story file shape, `args`, `argTypes`, `parameters`, `play` functions, decorators? What are the canonical addons (controls, a11y, viewport, interactions, docs, themes)? What is the MDX docs page composition and decorator stacking pattern? What is the Chromatic visual regression workflow and `@storybook/test-runner` integration? What is multi-package composition (Storybook `ref`) for design-system-level scaling?
- **KB gap justification:** Storybook is not covered by any existing KB. No ADR addresses it. The user explicitly elected `KB-storybook-platform` as a new platform KB at the Intent Confirmation Gate.
- **Acceptance criteria:**
  - Documents CSF3 story file shape with concrete example structure (no need to reproduce code in full — describe the shape).
  - Names 5+ canonical addons with their purpose.
  - Identifies MDX docs composition + decorator stacking patterns.
  - Names the Chromatic + test-runner visual regression workflow with the canonical integration points.
  - Identifies multi-package composition (`ref`) and when it applies.
  - Cites Storybook official documentation and Chromatic official documentation as primary sources.
- **Source constraints:** Storybook official documentation (storybook.js.org), Chromatic documentation, Storybook GitHub. NOT third-party tutorials as primary source.

## Topics explicitly NOT researched

Anti-scope-creep mechanism. For each information need with disposition `covered-by-KB` / `covered-by-ADR`, the resolution:

- **IN-010** (Naming convention for `KB-storybook-platform`) → **ADR-0019**. The naming convention is established: `KB-` prefix, kebab-case suffix matching the tool name. Storybook → `KB-storybook-platform`.
- **IN-011** (Structural pattern for new KBs) → **ADR-0020**. New KBs follow the SKILL.md + `references/` directory pattern; one canonical KB per domain. Platform KBs pair with design KBs but Storybook is platform-only (no `KB-storybook-design` because frontend design discipline already lives elsewhere).
- **IN-012** (Append-only supersession for `KB-frontend-design` restructure) → **ADR-0005**. If existing content is restructured, the predecessor is preserved (renamed to a `.v<N>.md` form or moved); the new version is authored fresh. Under Option A this is moot (KB stays in place, augmented); under Option B the existing file is preserved as the design-discipline KB and new sibling KBs are added.
- **IN-014** (KB authoring discipline) → **KB-cc-design:references/patterns-and-anti-patterns.md** plus codebase verification. The KB authoring patterns are codified — frontmatter schema, `disable-model-invocation` vs. `user-invocable: false` distinction (covered explicitly), references file conventions. Codebase verification at IN-001/IN-002 confirms latest practice.
- **IN-015** (Audit conventions for new KB content) → **`auditing-cc-configs/SKILL.md` + `auditing-cc-configs/references/pedagogical-marker-spec.md`**. The audit machinery is established: walker + 24 cross-file checks + LLM judge; Step 4 verification disposes of regex hits on pedagogical content. Anti-slop content's "don't do this" examples will carry markers per the spec — codebase verification (IN-003) confirms the spec is current.

## Estimated effort

- **Codebase research effort:** small. Most files are known and already touched in PRD authoring; the researcher's job is to formalize the touch-point inventory, run the blast-radius queries, and confirm the convention-discovery findings. Estimated single-instance work.
- **External research topic count:** 6 of 6 (at budget). All six topics are at the heart of the user's named scope; no consolidation possible without violating FR-1's coverage commitments.
- **Estimated wall-clock:** dominated by external research. Six topics in parallel (max parallelism 6 per ADR-0021); the longest individual topic likely T-005 (component architecture has the broadest pattern surface) or T-006 (Storybook docs are dense).

## Open questions for human resolution

- [ ] **OQ-1:** The 6-topic external-research budget is at the cap. If any topic surfaces a research subtopic deserving its own treatment (e.g., T-005 component architecture splitting cleanly into "atomic design" and "headless library patterns"), should the researcher consolidate into the parent topic's acceptance criteria or surface for budget override? Recommended: consolidate; the synthesize stage's substrate-comparison work absorbs minor sub-topics.
- [ ] **OQ-2:** Anti-slop research (T-001) names specific brand calibration points (Linear, Stripe, Vercel) by example. Is the user comfortable with these named-brand references appearing in the produced KB content, or should the KB use anonymized descriptions? Recommended: named references, since these are public design systems and the precedent for citing them is established (the PRD itself cites them).
