---
id: CCD-frontend-design-knowledge-r1
version: 1.0.0
status: draft
feature_slug: frontend-design-knowledge-r1
layer: claude-code
derived_from:
  - prd-v1.md@1.0.0
  - synthesis.md@1.0.0
  - codebase-analysis.json@1.0.0
generated: 2026-05-20T23:45:00Z
generated_by: design-cc (per-layer Design)
---

# Claude Code Design — Frontend Design Knowledge Enhancement (Round 1)

## Contents

- [x] Layer responsibility scope
- [x] Decisions resolved
- [x] Inventory of new primitives
- [x] Inventory of modified primitives
- [x] CLAUDE.md changes
- [x] Rule patterns
- [x] Skill patterns
- [x] Subagent patterns
- [x] Hook patterns
- [x] Permission policy
- [x] MCP server policy
- [x] Plugin packaging
- [x] Command-to-skill migration
- [x] Acceptance criteria contribution (EARS)
- [x] Dependencies on other layers
- [x] Architectural Questions for Composer (Q-CC-N)
- [x] Open items

## Layer responsibility scope

The Claude Code / Project Filesystem layer is the sole layer activated by this feature. All changes are to `.claude/skills/*` (new KBs) and `.claude/agents/*` (modified sub-agent frontmatter). No application code, no infrastructure, no CI/CD changes.

## Decisions resolved

Resolved by this layer designer, drawing on synthesis.md's recommendations:

- **D-001 (structural choice):** Option B. Four sibling design KBs added; `KB-frontend-design` preserved as the backend-of-frontend + a11y-baseline KB. `KB-storybook-platform` added as the fourth platform KB. Total KB-count delta: +5 (17 → 22).
- **D-002 (anti-slop placement):** `references/anti-slop.md` inside `KB-visual-design`. Cites Anthropic's upstream `frontend-design` skill at `/mnt/skills/public/frontend-design/SKILL.md` as the load-bearing source. Standalone anti-slop KB ruled out.
- **D-003 (Storybook KB depth):** Target 2000-3500 lines at v1, matching `KB-cc-platform`'s shape. SKILL.md + 5-7 reference files. Code-block density 3-5 / 100 lines.
- **D-004 (Principle 3 + a11y-flow):** Extend. `KB-frontend-design` Principle 3 (a11y-as-baseline) preserved as-is. New a11y-as-flow content joins `KB-ux-design`. No supersession of existing content (ADR-0005 overhead avoided).
- **D-005 (sibling sub-agents):** No. `design-frontend` continues as the single Frontend layer designer; the new KBs join its preload list via `skills:` frontmatter.
- **D-006 (pedagogical markers):** Surgical. Heavy in `references/anti-slop.md`; medium in `KB-visual-design/SKILL.md` and `references/principles.md` where AI-default aesthetics are negative-referenced; minimal/none elsewhere.

## Inventory of new primitives

5 new knowledge skills (KBs). Each is project-scoped; activation differs by use case (see Skill patterns).

### Primitive 1 — `KB-ux-design` (new skill)

- **Type:** skill (knowledge-only)
- **Path:** `.claude/skills/KB-ux-design/`
  - `SKILL.md` (index)
  - `references/principles.md` (Nielsen's 10 heuristics with one-line summaries; cognitive load discipline; error prevention/recovery)
  - `references/journey-and-ia.md` (Norman's 7 stages; service blueprint; customer journey map; JTBD; card sort; tree test; content inventory)
  - `references/accessibility-as-flow.md` (focus restoration; live-region choreography; error-recovery for AT users; keyboard task completion; cognitive-load reduction; focus indicators; heading hierarchy as navigation aid)
- **Purpose:** UX discipline + accessibility-as-flow content. Complements `KB-frontend-design` Principle 3 (a11y-as-baseline) without superseding it.
- **Scope:** project.
- **Activation:** always-preloaded by `design-frontend` and `design-composer` via `skills:` frontmatter (consistent with how `KB-frontend-design` currently preloads).
- **Lowest-cost-primitive justification (KB-cc-design Principle 1):** Knowledge skill is the lowest-cost primitive for design-discipline content. CLAUDE.md would bloat the always-loaded context; a rule isn't applicable (no enforcement); a subagent is overkill (the knowledge is consumed by existing designers).

### Primitive 2 — `KB-visual-design` (new skill)

- **Type:** skill (knowledge-only)
- **Path:** `.claude/skills/KB-visual-design/`
  - `SKILL.md` (index)
  - `references/type-color-space.md` (type scales: modular scale, Material 3, fluid `clamp()`, Apple Dynamic Type; color systems: OKLCH recommended with HSL and APCA context; spacing: 4pt vs 8pt; iconography)
  - `references/motion.md` (Material 3 motion tokens; Apple HIG motion intent; Disney 12 principles for UI; cubic-bezier curves and duration ranges; `prefers-reduced-motion` integration)
  - `references/responsive.md` (canonical breakpoints; container queries; fluid type/space with `clamp()` + Utopia; density spectrum)
  - `references/anti-slop.md` (per D-002: cites Anthropic upstream; names slop signatures; names intentional-design dimensions; carries pedagogical markers per D-006)
- **Purpose:** UI / visual design discipline + anti-slop calibration.
- **Scope:** project.
- **Activation:** always-preloaded by `design-frontend` and `design-composer`.
- **Lowest-cost-primitive justification:** Same as Primitive 1.

### Primitive 3 — `KB-design-system-design` (new skill)

- **Type:** skill (knowledge-only)
- **Path:** `.claude/skills/KB-design-system-design/`
  - `SKILL.md` (index)
  - `references/tokens.md` (three-tier model: primitive → semantic → component; concrete mappings from Carbon, Material 3, Primer, Salesforce; W3C DTCG format emerging)
  - `references/theming.md` (CSS variables as modern default; Style Dictionary for polyglot delivery; build-time substitution; CSS-in-JS providers as legacy)
  - `references/governance.md` (semver discipline for design systems; major / minor / patch with concrete examples; tokens-components-patterns three-layer scope)
- **Purpose:** Design system architecture discipline. Token tier organization, theming, semver, polyglot delivery.
- **Scope:** project.
- **Activation:** always-preloaded by `design-frontend` and `design-composer`.
- **Lowest-cost-primitive justification:** Same as Primitive 1.

### Primitive 4 — `KB-component-architecture-design` (new skill)

- **Type:** skill (knowledge-only)
- **Path:** `.claude/skills/KB-component-architecture-design/`
  - `SKILL.md` (index)
  - `references/atomic-design.md` (Frost's 5 tiers; mental-model-not-file-structure discipline)
  - `references/headless-libraries.md` (Radix UI, React Aria, Headless UI, Ariakit, shadcn/ui — pattern surfaces and trade-offs)
  - `references/patterns.md` (compound; slot — both `asChild` and named-slot senses; polymorphic `as`; controlled-vs-uncontrolled; ref forwarding incl. React 19 implicit; prop API design)
- **Purpose:** Component architecture discipline. Atomic / headless / compound / polymorphic / slot patterns.
- **Scope:** project.
- **Activation:** always-preloaded by `design-frontend` and `design-composer`.
- **Lowest-cost-primitive justification:** Same as Primitive 1.

### Primitive 5 — `KB-storybook-platform` (new skill, platform-KB shape)

- **Type:** skill (knowledge-only, platform-KB pattern)
- **Path:** `.claude/skills/KB-storybook-platform/`
  - `SKILL.md` (index)
  - `references/story-format.md` (CSF3 default; CSF Factories as v10 evolution; meta + args + argTypes + parameters + play; decorators)
  - `references/addons.md` (essentials, controls, a11y, viewport, interactions, docs, themes, coverage)
  - `references/docs.md` (MDX composition; Doc Blocks: Meta / Story / Canvas / Controls / Source / Description / Subtitle; decorator stacking)
  - `references/testing.md` (Chromatic VRT; `@storybook/test-runner`; Vitest integration from Storybook 9; axe-core via a11y addon)
  - `references/composition.md` (multi-package via `refs`; design-system + product Storybook topology)
- **Purpose:** Storybook platform knowledge. Per D-003: target 2000-3500 lines; KB-cc-platform-shaped, not KB-github-actions-platform-shaped.
- **Scope:** project.
- **Activation:** **Model-invocable, not always-preloaded.** Storybook is relevant only when a feature involves Storybook stories — a subset of frontend-touching features. Per KB-cc-design Principle 1 (lowest-cost primitive), do not always-preload knowledge that is only sometimes needed. The SKILL.md description explicitly states "Use when the feature includes Storybook stories, addons, or visual regression testing."
- **Lowest-cost-primitive justification:** Model-invocable skill costs zero context until invoked (per KB-cc-platform extensions.md). Always-preloading via skills frontmatter would carry the cost on every `design-frontend` invocation regardless of relevance — wasteful for non-Storybook features.
- **Code-block density allowance:** 3-5 per 100 lines (intake constraint: syntax IS the knowledge for the Storybook KB). Departs from design-side KBs' 0.8-2.0 density convention; consistent with other platform KBs' 2.2-4.1.

## Inventory of modified primitives

### Modification 1 — `design-frontend.md` sub-agent

- **File:** `.claude/agents/design-frontend.md`
- **Change:** `skills:` frontmatter expands from `[KB-frontend-design, KB-documentation-criteria, KB-general-coding-principles, KB-review-disciplines]` (4 entries) to `[KB-frontend-design, KB-ux-design, KB-visual-design, KB-design-system-design, KB-component-architecture-design, KB-documentation-criteria, KB-general-coding-principles, KB-review-disciplines]` (8 entries). `KB-storybook-platform` is NOT added — model-invocable per Primitive 5.
- **Rationale:** Each of the 4 new design-side KBs is universally relevant to Frontend Design subsection authoring; always-preload follows the existing `KB-frontend-design` precedent.
- **Body content addition:** The agent's prose adds a paragraph documenting when to model-invoke `KB-storybook-platform` ("Invoke `KB-storybook-platform` when the feature's frontend includes Storybook stories, custom addons, or visual regression test integration.").
- **Blast-radius:** bounded. The frontmatter `skills:` array is the single point of preload control; no other agent file references this list's specific contents.

### Modification 2 — `design-composer.md` sub-agent

- **File:** `.claude/agents/design-composer.md`
- **Change:** `skills:` frontmatter adds the 4 new design-side KBs (`KB-ux-design`, `KB-visual-design`, `KB-design-system-design`, `KB-component-architecture-design`). Current entries are preserved. `KB-storybook-platform` is NOT added — model-invocable.
- **Rationale:** `design-composer` preloads all per-layer design KBs to integrate cross-layer; the 4 new design-side KBs join this set.
- **Body content addition:** Same paragraph as Modification 1 documenting when to model-invoke `KB-storybook-platform`.
- **Blast-radius:** bounded. Same rationale as Modification 1.

### Modification 3 — `KB-frontend-design/SKILL.md` (docstring update only)

- **File:** `.claude/skills/KB-frontend-design/SKILL.md`
- **Change:** Frontmatter description updated to clarify the new sibling KBs and `KB-frontend-design`'s narrowed-but-preserved scope (backend-of-the-frontend discipline + accessibility-as-baseline). The current line "no platform partner KB (frontend platforms vary widely)" stays as-is; it remains accurate.
- **Rationale:** Per ADR-0005, content is NOT moved or removed; the docstring update is metadata clarification only. The existing 8 principles + 2 reference files remain untouched.
- **Append-only supersession discipline:** Not triggered. No content removal or restructure; the docstring is metadata, not principle content.

## CLAUDE.md changes

None. All new content is in skills (per KB-cc-design Principle 5: one source of truth; reference material in skills, not CLAUDE.md).

## Rule patterns

None. No new enforcement; the new KBs are knowledge, not enforcement.

## Skill patterns

Per the Inventory above. Recurring patterns worth surfacing:

- **Always-preload via `skills:` list:** the 4 design-side KBs (consistent with `KB-frontend-design` precedent).
- **Model-invocable:** `KB-storybook-platform` (per KB-cc-design Principle 1; zero-cost-until-invoked).
- **Knowledge-only:** all 5 new KBs. None carry `Bash` / `Edit` / `Write` tools (they're consumed by sub-agents that already have the right tools).
- **`allowed-tools`:** all 5 follow the design-KB convention of `Read, Grep, Glob` only.
- **`disable-model-invocation`:** explicitly NOT set in frontmatter for any of the 5. Per FA-003 finding: zero KBs in the project carry this in actual frontmatter; the field is reserved for action-skills with side effects.
- **`user-invocable`:** explicitly NOT set in frontmatter for any of the 5 (defaults to user-invocable per Claude Code's defaults; this allows users to inspect any KB via `/KB-<name>` if needed for debugging).

## Subagent patterns

Per Modifications 1 and 2 above. Recurring patterns:

- **Reasoning configuration unchanged.** Both `design-frontend` and `design-composer` retain their existing `model: opus` + `effort: high` (design-frontend) / `effort: xhigh` (design-composer). Per KB-cc-design Principle 9: reasoning configuration is intentional, justified at agent design time; this feature does NOT modify either.
- **`skills:` list grows; tool list unchanged.** Both agents already have `[Read, Glob, Grep, Write, TaskCreate, TaskUpdate]`; no new tools needed.
- **`memory:` scope unchanged** at `project` for both.

## Hook patterns

None. No new lifecycle hooks.

## Permission policy

No new mutating tools. The feature is knowledge content + sub-agent frontmatter edits — both handled by existing `Read`/`Write` permissions. No new allow/ask/deny entries needed.

## MCP server policy

None. No external service integration.

## Plugin packaging

None. The new KBs are project-scoped knowledge; not cross-project distribution candidates.

## Command-to-skill migration

None. No legacy `.claude/commands/*.md` being migrated.

## Acceptance criteria contribution (EARS)

EARS-format ACs the per-layer Design subsection contributes (subset of PRD's ACs, refined with the structural choice resolved):

- **AC-CC-1-a:** When `design-frontend` invokes for any frontend-touching feature, the system shall preload `KB-ux-design`, `KB-visual-design`, `KB-design-system-design`, `KB-component-architecture-design`, and `KB-frontend-design` (4 new + 1 existing) via the `skills:` frontmatter.
- **AC-CC-1-b:** When `design-frontend` invokes for a feature whose Frontend layer includes Storybook stories, the system shall be able to model-invoke `KB-storybook-platform`; the SKILL.md description shall explicitly direct this invocation.
- **AC-CC-2-a:** Where the 5 new KBs follow the structural convention codified in `KB-cc-design/references/patterns-and-anti-patterns.md`, each SKILL.md shall carry `name`, `description`, and `allowed-tools` frontmatter; each shall lead with a `## Contents` H2 checklist; design-side KBs shall include a `## When this KB is loaded` subsection.
- **AC-CC-3-a:** While the new content references AI-slop patterns (e.g., Inter, Roboto, purple-gradient-on-white) by name, the system shall apply pedagogical markers per `pedagogical-marker-spec.md` so the audit's Step 4 verification disposes of regex matches as benign.
- **AC-CC-4-a:** If `KB-frontend-design`'s SKILL.md docstring is updated (Modification 3), then the existing 8 principles and 2 reference files (`principles.md`, `patterns-and-anti-patterns.md`) shall remain unmodified, honoring ADR-0005's append-only supersession discipline.
- **AC-CC-5-a:** The system shall pass `cc-audit` (auditing-cc-configs SKILL.md's full audit) with zero new violations after all 5 new KBs are authored and the 2 sub-agents are modified.

## Dependencies on other layers

None. The CC layer is the sole activated layer; no cross-layer dependencies. Confirmed by the codebase analysis's `scope_observations.layers_in_scope_evidence` (8 layers N/A; only claude-code-fs touched).

## Architectural Questions for Composer (Q-CC-N)

None. The single-layer scope and synthesis-resolved decisions leave no cross-layer arbitration for `design-composer` to perform. `design-composer`'s role on this feature is:

1. Integrate `cc-design.md` into the Blueprint.
2. Author **ADR-0024** documenting the structural choice (Option B; per FR-5, only design-composer authors ADRs).
3. Compose the cross-cutting Blueprint sections (Overview, Background, Implementation Plan top-level, Verification Strategy, Risks).

## Open items

None substantive. Two minor follow-ups for future rounds (not blocking this Blueprint):

1. **CSF Factories adoption.** `KB-storybook-platform` v1 documents CSF3 (current default) + CSF Factories (v10 evolution). If the Storybook community heavily adopts CSF Factories through 2026-2027, a future revision may shift the emphasis. Not actionable now.
2. **Anthropic upstream skill versioning.** `references/anti-slop.md` cites `/mnt/skills/public/frontend-design/SKILL.md` (Anthropic-managed). If Anthropic updates or removes that skill, the citation chain needs refresh. Note in the reference file's "Source dependencies" section.
