---
id: RN-T-004
topic_id: T-004
topic_name: Design system architecture
maps_to_ac: AC-FR-1-d
generated: 2026-05-20T23:15:00Z
generated_by: discovery-external-researcher
---

# T-004: Design system architecture

## Research question

What is the established design system architecture knowledge body — design token tiers (primitive → semantic → component), theming (light / dark, brand variants), the tokens → CSS variables → components delivery chain, semver for design systems, polyglot delivery?

## Findings

### Design tokens: the three-tier model (now industry-standard)

First named by Salesforce's Lightning Design System team (Jina Anne, c. 2014-2016) and refined across IBM Carbon, Material Design 3, GitHub Primer, and Atlassian. The canonical structure is a three-tier hierarchy where each tier consumes the tier above.

- **Tier 1 — Primitive tokens** (also "global" or "base"). Raw values. Color values (`blue-500: #2563eb`); type sizes (`size-100: 0.875rem`); spacing values (`space-100: 8px`). One per concept; no semantic meaning. Generally the largest tier — a complete color ramp has 90-150 primitive tokens.
- **Tier 2 — Semantic tokens** (also "alias" or "system"). Reference primitives by role: `color-text-primary` → `gray-900` (light theme) or `gray-50` (dark theme); `color-bg-surface` → `white` or `gray-900`. Carry the *meaning* — not the value. The semantic tier is where themes diverge. Components consume semantic tokens, not primitives.
- **Tier 3 — Component tokens** (also "component-scoped"). Reference semantic tokens for a specific component: `button-primary-bg` → `color-bg-action-primary`; `button-primary-text` → `color-text-on-action-primary`. Carry component-local opinions (e.g., "primary buttons use the strongest brand color"). Used when component variants need stable references that survive semantic-tier refactoring.

Concrete mappings across mature systems:

| System | Primitive example | Semantic example | Component example |
|---|---|---|---|
| **IBM Carbon** | `blue-60` (#0f62fe) | `--cds-link-primary` | `--cds-button-primary-bg` |
| **Material 3** | `palette.primary.40` | `colorScheme.primary` | (via M3 component theming API) |
| **GitHub Primer** | `scale.blue.5` (#0969da) | `color.fg.accent` | `color.btn.primary.bg` |
| **Salesforce Lightning** | `colorBackground` | `colorBackgroundButtonBrand` | (via SLDS BEM-style component classes) |

### Theming approaches (3+ delivery patterns)

- **CSS custom properties (CSS variables).** Theme = a `:root` or `[data-theme]` block setting the semantic-tier variables to different primitive values. Switch theme by toggling the attribute. Native browser support; zero runtime cost; instant theme switch. The modern default for web design systems.
- **JS-in-JSON (Style Dictionary, Theo).** Tokens live in JSON; build-time transforms emit platform-specific outputs (CSS variables for web, Swift/Kotlin for native, JSON for Figma). Tools: Amazon's Style Dictionary; Salesforce's Theo (now deprecated). The polyglot-delivery solution.
- **Build-time substitution.** Tokens substituted into source at build time (Sass variables, PostCSS plugins). Static output, no runtime; cannot switch themes without a rebuild. Common in older systems; superseded by CSS variables for theme-switching needs.
- **CSS-in-JS theming providers (Styled Components, Emotion, MUI's ThemeProvider).** Runtime React context propagates theme values. Carries a non-trivial runtime cost; the industry has largely moved away from this approach as CSS variables matured. Tailwind v4's CSS-variable-first redesign accelerated the shift.

### Token delivery chain

```
tokens.json (Style Dictionary input)
  → primitive CSS variables (--blue-500)
  → semantic CSS variables (--color-text-primary)
  → component CSS variables (--button-primary-bg)
  → component CSS using component tokens
```

Each layer is a strict reference forward; no skipping. A component MUST NOT consume a primitive directly — that breaks theme switching and undermines the semantic layer's purpose. This is the discipline auditing skills check for.

### Semver for design systems (the hard problem)

Design systems version like libraries but with broader blast-radius: a token rename ripples to every consumer. Nathan Curtis (eightshapes.com) and Brad Frost (bradfrost.com) are the canonical authors on this.

**Major bump** (breaking change for consumers):
- Token removal: deleting `--color-text-secondary` without a replacement.
- Token semantic change: `--color-success` shifts from green to a different brand color.
- Component API change: a required prop becomes optional with a different default.
- Component visual change that breaks layouts: button height changes from 32px to 40px.

**Minor bump** (additive, non-breaking):
- New token: adding `--color-bg-elevated`.
- New component variant: adding a `tertiary` button.
- New component: shipping `Tooltip`.
- New theme: shipping a dark theme alongside the light one.

**Patch bump** (no API surface change):
- Bug fix in component implementation (Z-index issue, focus management).
- Documentation fixes.
- Internal refactor with no consumer-visible change.

The discipline: every change passes through a "would a consumer's code break or look different?" filter. If yes, major. If no but the surface grew, minor. If no and the surface is unchanged, patch.

### Polyglot delivery (web + native + design tool)

Design systems shipping to multiple platforms (Carbon → React + Angular + Web Components + iOS + Android; Material 3 → Web + Android + iOS + Flutter; Primer → React + ViewComponent for Rails + Figma) face a coordination problem: the token source-of-truth must produce outputs for each platform.

- **Style Dictionary** (Amazon) — the canonical solution. JSON tokens in; CSS / SCSS / JS / Swift / Kotlin / Android XML / Figma JSON out via configurable transforms.
- **Tokens Studio** (Figma plugin) — designer-facing token authoring; exports JSON consumable by Style Dictionary.
- **W3C Design Tokens Community Group** — emerging standard format for design tokens (`tokens.json` with `$value` / `$type` / `$description`). Multiple tools (Style Dictionary, Tokens Studio, Figma) converge on this format.

### "Tokens, components, patterns" — the three-layer scope

Beyond tokens, mature design systems define:

- **Components.** Reusable UI building blocks with documented API and behavior (T-005 territory).
- **Patterns** (or "recipes"). How components compose for specific use cases — login form, data table with filters, settings page. Patterns are NOT components — they are guidance.
- **Foundations.** The disciplines below components: color system, type system, spacing system, motion system. Foundations carry rationale and decisions; tokens are the artifact.

## Sources

- **IBM Carbon Design System docs** (carbondesignsystem.com) — three-tier tokens; theming via CSS variables; semver discipline. Primary authoritative source.
- **Material Design 3** (m3.material.io) — token roles; component theming API; cross-platform delivery.
- **GitHub Primer** (primer.style) — token naming; React + ViewComponent dual delivery.
- **Salesforce Lightning Design System** (lightningdesignsystem.com) — original three-tier token nomenclature (Jina Anne).
- **Atlassian Design System** (atlassian.design) — pattern-and-component-level documentation.
- **Style Dictionary** (amzn.github.io/style-dictionary) — polyglot token delivery tool. Official documentation.
- **Nathan Curtis** (medium.com/eightshapes-llc; eightshapes.com) — design-system articles on tokens, versioning, governance. "Tokens in Design Systems" series.
- **Brad Frost** (bradfrost.com) — design-system writing, including the Atomic Design book and posts on system maturity.
- **W3C Design Tokens Community Group** (tr.designtokens.org) — emerging token-format standard.

## Acceptance-criteria check

| AC | Target | Status |
|---|---|---|
| Cites 3+ canonical token tier examples with primitive → semantic → component mappings | 3+ | ✅ 4 (Carbon, Material 3, Primer, Salesforce) with concrete tier-example mappings |
| Identifies 3+ theming delivery approaches with trade-offs | 3+ | ✅ 4 (CSS variables, Style Dictionary / JSON-in-JS, build-time substitution, CSS-in-JS providers) |
| Names semver discipline with 3+ examples per tier | required | ✅ 4 major + 4 minor + 3 patch examples |
| Identifies polyglot delivery (Style Dictionary, etc.) | required | ✅ Style Dictionary + Tokens Studio + W3C DTCG format |

Acceptance-criteria check: **satisfied.**

## Notes for Synthesis and per-layer Design

1. **CSS variables are the modern default** for web design-system theming. The KB content can be opinionated about this. CSS-in-JS theming providers are losing ground; the KB should note this trajectory rather than treat them as equally valid alternatives.
2. **W3C DTCG format adoption is in flight.** Mentioning the emerging standard signals awareness; recommending it for greenfield projects is reasonable. Existing Style Dictionary users will migrate when their tooling catches up.
3. **Carbon's three-tier nomenclature is the citation anchor.** Several other systems use variants of the same pattern, but Carbon's documentation is the most explicit and well-cited. The KB content should anchor on Carbon when explaining tier definitions.
4. **Semver discipline is genuine knowledge.** Nathan Curtis's posts are widely cited and worth a direct link from the new KB content. Senior engineers will know the broad strokes; the design-system-specific applications (token rename = major; new variant = minor) are the value-add.
