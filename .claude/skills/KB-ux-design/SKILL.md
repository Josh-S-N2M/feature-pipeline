---
name: kb-ux-design
description: >-
  Design knowledge for user-experience discipline — how people understand,
  navigate, and complete tasks in software. Covers Nielsen's 10 heuristics
  (the durable evaluation lens since 1994), user journey + information
  architecture frameworks (Norman's 7 stages, service blueprints, JTBD,
  customer journey maps, card sorts, tree tests, content inventory), and
  accessibility-as-flow (how a11y is task completion for an audience that
  cannot rely on visual-default affordances — focus restoration, live-region
  choreography, error-recovery loops, keyboard task completion, cognitive
  load reduction). Always preloaded by `design-frontend` and `design-composer`
  alongside the other 3 design-side KBs.
allowed-tools: Read, Grep, Glob
---

# KB-ux-design — User Experience Design

## Contents

- [x] When this KB is loaded
- [x] What "UX" means at the Design layer in this project
- [x] The three durable lenses
- [x] Lookup chains by question type
- [x] Related KBs

## When this KB is loaded

This KB is always preloaded by:

- `design-frontend` — the per-layer Design agent for the Frontend layer.
- `design-composer` — the cross-layer Design fan-in agent.

It is consulted when the feature's design surface involves user-facing flows, navigation, task completion, error recovery, accessibility-as-flow, content organization, or any interaction where the question "can a person actually do the thing they came to do" is load-bearing. It is NOT consulted for pure visual style decisions (those go to `KB-visual-design`), pure structural decomposition (`KB-component-architecture-design`), or pure design-system-architecture concerns (`KB-design-system-design`).

When a feature has no user-facing surface (e.g., a backend-only data migration; a CLI utility that runs once), this KB still informs the Design layer's review of error messages, status output, and any documentation users will read — UX is broader than GUI.

## What "UX" means at the Design layer in this project

UX in this KB is **the discipline of designing for task completion** — for a person attempting to accomplish something through software. It is NOT:

- A synonym for "visual polish." Visual decisions live in `KB-visual-design`.
- A synonym for "user research." User research methods inform UX decisions but the discipline this KB covers is the design output, not the discovery methods.
- A synonym for accessibility-compliance-checking. A11y as a checklist is necessary but not sufficient; a11y as flow (what this KB covers) is how a11y becomes load-bearing in task completion.
- A pedagogical introduction to design. The voice here assumes a senior practitioner; the audience is the project's design-agent network and the engineers reading their outputs.

The discipline rests on three durable lenses, each documented in a reference file.

## The three durable lenses

### 1. Nielsen's 10 heuristics — `references/principles.md`

Jakob Nielsen's heuristics, published in 1994 and refined since, remain the most-cited UX evaluation framework. The ten heuristics name failure modes that recur across decades of software: visibility of system status, match between system and real world, user control and freedom, consistency and standards, error prevention, recognition rather than recall, flexibility and efficiency of use, aesthetic and minimalist design, help users recognize/diagnose/recover from errors, help and documentation.

They are evaluation criteria, not generation rules. Use them to interrogate a design surface (does this match the heuristic? if not, why not?), not to derive a design from scratch.

### 2. Journey and information architecture — `references/journey-and-ia.md`

How users move through a product and how content is organized for navigation. Frameworks covered: Norman's seven stages of action (goal → intention → action specification → execution → perception → interpretation → evaluation); service blueprints (mapping user-facing journey to backstage processes); Jobs-To-Be-Done (the user's task framed as a "job" the product is "hired" to do); customer journey maps (the multi-touchpoint journey with emotional states); card sorts and tree tests (empirical methods for IA validation); content inventory (what content exists and where).

These are decomposition tools. They take "the user wants to X" and reveal the substructure (sequence of steps; surface contact points; navigation prerequisites).

### 3. Accessibility as flow — `references/accessibility-as-flow.md`

Accessibility framed as task completion for an audience that cannot rely on visual-default affordances. Covers: focus restoration across navigation and modal dismissal; live-region choreography (`aria-live` regions for async updates); error-recovery loops (announcement, identification, correction); keyboard task completion (every flow completable without a pointing device); cognitive-load reduction (chunking, progressive disclosure, predictable patterns); focus indicators (visible, high-contrast); heading hierarchy (semantic structure as navigation).

This is the inverse of an a11y checklist. A WCAG checklist asks "does this element have alt text"; accessibility-as-flow asks "can a screen-reader user actually complete this task." The distinction matters because checklists pass while flows fail.

## Lookup chains by question type

- **"Is this design good?"** → `references/principles.md` → walk the 10 heuristics; identify which apply; surface gaps.
- **"How does the user get from A to B?"** → `references/journey-and-ia.md` → Norman's 7 stages OR customer journey map.
- **"What's the right navigation structure?"** → `references/journey-and-ia.md` → card sort + tree test; content inventory.
- **"Why does the user need to do this job?"** → `references/journey-and-ia.md` → Jobs-To-Be-Done framing.
- **"Can a screen-reader user complete this?"** → `references/accessibility-as-flow.md` → focus + live-regions + keyboard task completion.
- **"Is this error message any good?"** → `references/principles.md` → heuristic 9 (recognize/diagnose/recover) + `references/accessibility-as-flow.md` → error-recovery loops.

## Related KBs

- **`KB-visual-design`** — visual choices (type, color, motion, space) inform UX but UX is the layer above. A pretty interface that's unusable fails here; an ugly interface that works elegantly succeeds.
- **`KB-design-system-design`** — patterns the design system codifies (form patterns, navigation patterns, feedback patterns) embody UX decisions at scale.
- **`KB-component-architecture-design`** — components implement UX patterns. The compound-component pattern serves UX needs (compositional flexibility); polymorphic components serve UX needs (semantic correctness across contexts).
- **`KB-frontend-design`** — the broader frontend discipline (state, perf, errors, typing, framework grain, a11y baseline). UX is one lens among several in `KB-frontend-design`; this sibling KB elaborates.
- **`KB-storybook-platform`** — where UX work becomes visible for review. Storybook surfaces components in isolation; stories that drive `play` functions through realistic UX flows test the discipline.
