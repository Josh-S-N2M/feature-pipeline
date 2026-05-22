# Governance

How a design system evolves without breaking its consumers. Covers semver applied to design systems, scope decisions (what belongs in the system vs the application), migration discipline (breaking changes with codemod support), deprecation cycles, and the ADR-equivalent for design-system decisions.

## Contents

- [x] Why governance is load-bearing
- [x] Semver for design systems
- [x] Scope boundaries
- [x] Migration discipline
- [x] Deprecation cycles
- [x] Design-system ADRs / decision records
- [x] Changelogs
- [x] Patterns and anti-patterns
- [x] Cross-references

## Why governance is load-bearing

A design system without governance fragments rapidly. Consumers fork; components proliferate; tokens drift. The discipline keeps the system coherent across teams and over time.

The signals that governance is missing:

- The same component exists in three slightly different forms across the codebase.
- Token values are duplicated as hardcoded literals because "I needed a slightly different blue."
- Breaking changes ship without warning; downstream teams discover them in production.
- The design system has no clear answer to "should I add this here or in my app?"

Governance is the answer to "who decides, on what evidence, with what process." It's most useful when the system is shared across teams; less critical for a single-team system but still beneficial.

## Semver for design systems

Semantic versioning (`MAJOR.MINOR.PATCH`) applies to design systems with specific interpretations:

| Version bump | Triggers |
|---|---|
| **MAJOR** | Token names removed or changed; component props removed or renamed; component visual changes that break consumer layouts; pattern structure changes that require consumer updates |
| **MINOR** | New tokens added; new components added; new component variants; new props with defaults; visual refinements that don't break layouts |
| **PATCH** | Bug fixes; accessibility fixes; performance improvements; visual fixes that match the documented spec |

Worked examples:

- `1.2.3 → 1.2.4` — fixed focus ring on `Button` to meet WCAG 2.4.7 contrast requirements (patch — accessibility fix matching documented intent).
- `1.2.3 → 1.3.0` — added `Tooltip` component; added `--color-info-subtle` token (minor — additions).
- `1.2.3 → 2.0.0` — renamed `--color-text` to `--color-foreground`; removed `Card.shadow` prop in favor of `elevation` token; visual update changes default Button padding (major — breaking).

The discipline of separating MINOR from MAJOR: a MINOR release should never require consumer changes. If consumers must update code to receive the change, it's MAJOR.

Visual refinements are the ambiguous case. A subtle color shift (`oklch(60% 0.18 260)` → `oklch(62% 0.17 260)`) might be MINOR if no consumer layout depends on the exact value, or MAJOR if a marketing page's hero gradient is composed against a specific token value. The discipline: treat visual change as breaking when it could plausibly break a layout someone depends on.

## Scope boundaries

The design system carries patterns and components used by multiple applications. Application-specific patterns stay in the application.

The discipline at the boundary:

**Belongs in the design system:**

- Components and tokens used by 2+ applications today.
- Patterns the brand requires consistency on (the primary CTA button; the system error toast).
- Generic patterns the design team has invested in tuning (form fields with their full a11y discipline).

**Belongs in the application:**

- Components used by exactly one application (single-purpose; single-product feature).
- Page-specific layouts.
- Business-logic-coupled components ("OrderCard" — knows about orders).
- Experimental patterns under evaluation.

**Ambiguous (decide explicitly):**

- A "DataTable" used by two applications but with different requirements per use. Often resolved by extracting the common substrate to the design system and letting applications wrap it.
- A "UserAvatar" component — generic in shape, but the data it consumes (user objects) is app-specific. Resolved by putting the visual primitive in the system and the data integration in apps.
- A pattern used by one application TODAY but expected to spread. Tempting to put in the system; usually better kept in the application until the second consumer arrives (premature abstraction).

The two-consumer rule: a component or pattern enters the design system when at least two distinct consumers need it. Single-consumer components have not yet proven their interface; the system shouldn't absorb risk-free.

## Migration discipline

When a breaking change ships, the consumer effort to migrate determines adoption. The discipline:

**Codemods where possible.** Token renames, prop renames, simple structural changes can be automated. Ship the codemod with the breaking-change release.

```bash
# Example: rename --color-text → --color-foreground across consumer codebases
npx @design-system/codemods rename-color-token \
  --from color-text \
  --to color-foreground \
  --paths "src/**/*.{ts,tsx,css}"
```

Most modern codebases have a codemod-friendly tooling layer (jscodeshift; ast-grep). Investment in codemod authoring pays back on every consumer.

**Migration guides for changes that can't be automated.** When a component's API changes shape such that no codemod can produce the right result (e.g., a prop is replaced by a composition pattern), publish a migration guide showing before/after.

**Deprecation period.** Don't ship a breaking change without a prior deprecation. The cycle: deprecate in version N (with warning); remove in version N+1 (or N+2 for slower-moving consumers).

**Bundle breaking changes.** If multiple breaking changes are planned, ship them in one MAJOR release rather than across several. Consumers update once.

## Deprecation cycles

A deprecation cycle:

1. **Deprecation announced** in version N. The old API still works; using it emits a console warning in development.
2. **Migration guide published** alongside the deprecation. Consumers know what to do.
3. **Codemod available** if the migration is mechanical.
4. **Removal in version N+1 (MAJOR)** for fast-moving consumers, or N+2 for slower-moving consumers (publish a calendar so consumers can plan).

Implementing the warning:

```ts
// In the deprecated component
function Card({ shadow, elevation, ...props }) {
  if (shadow !== undefined && elevation === undefined) {
    if (process.env.NODE_ENV !== 'production') {
      console.warn(
        '[design-system] <Card shadow={...}> is deprecated. ' +
        'Use <Card elevation={...}> instead. ' +
        'Migration: https://design-system.example.com/migrate/card-shadow-elevation'
      );
    }
    elevation = mapShadowToElevation(shadow);
  }
  // ...
}
```

The warning includes:

- Clear identification of the deprecated API.
- Replacement instruction.
- Link to migration guide.
- Behavior is preserved (the deprecated API still works during the cycle).

## Design-system ADRs / decision records

Significant design-system decisions deserve recorded rationale. The ADR pattern (Architecture Decision Record) applies — a Markdown file per decision in a `decisions/` directory, with template:

```
# ADR-NNN: Title

## Status
proposed | accepted | superseded by ADR-NNN

## Context
What problem are we solving? What constraints apply?

## Decision
What did we decide?

## Consequences
What follows from this? What's now easier? What's now harder?

## Alternatives considered
What did we evaluate and reject? Why?
```

Decisions that warrant ADRs in a design system:

- Token tier model (Carbon-style vs Primer-style vs hybrid).
- Choice of CSS technology (CSS Modules vs CSS-in-JS vs utility-first vs vanilla extract).
- Choice of headless component library (Radix vs React Aria vs in-house).
- Choice of testing tools (Chromatic vs Playwright vs Vitest).
- Decision to deprecate a major component family.
- Decision to adopt or refuse a new dependency.

Decisions that DON'T need ADRs:

- Token value adjustments.
- Component variant additions.
- Routine bug fixes.

ADRs aren't tutorials; they're decision logs for future readers. Keep them concise (1-2 pages); link out to longer documentation when needed.

## Changelogs

Every release ships a changelog entry. The convention (Keep a Changelog format):

```markdown
# Changelog

## [2.0.0] — 2026-04-15

### BREAKING CHANGES

- Renamed `--color-text` → `--color-foreground`. Codemod available:
  `npx @design-system/codemods rename-token --from color-text --to color-foreground`.
- Removed `Card.shadow` prop in favor of `elevation` token consumption.
  See migration guide: `design-system.example.com/migrate/card-shadow-elevation`.

### Added

- New `Tooltip` component (uses `@floating-ui/react` for positioning).
- New `--color-info-subtle` token for low-emphasis informational backgrounds.
- `Button` now supports `loading` prop with built-in spinner.

### Changed

- `Modal` overlay transition now respects `prefers-reduced-motion`.
- `Input` focus ring updated to meet WCAG 2.4.11 (focus appearance).

### Fixed

- `Select` keyboard navigation no longer skips items in long lists.
- `Badge` color-contrast on warning variant now meets WCAG AA in light mode.

### Deprecated

- `Card.shadow` will be removed in v3.0.0 (planned 2026-10). Use `elevation` token.
```

The structure: BREAKING CHANGES first (most consequential); Added (new capability); Changed (modified behavior); Fixed (bug fixes); Deprecated (planned removals).

For a design system shipped to multiple consumers, the changelog is the contract. Treat it as documentation, not as an afterthought.

## Patterns and anti-patterns

**Pattern: two-consumer rule for entering the system.** A pattern earns its way into the design system when two distinct consumers need it. Premature absorption produces APIs that don't fit the eventual second use case.

**Pattern: deprecation before removal.** Never ship a breaking removal without a prior deprecation. The deprecation cycle gives consumers time to migrate without emergency work.

**Pattern: codemods for mechanical migrations.** When a breaking change can be automated, ship the codemod. Reduces consumer effort to near-zero; accelerates adoption.

**Pattern: visible owner per design-system area.** "Who owns Form components?" "Who owns Tokens?" Clear ownership accelerates decisions; ambiguous ownership produces stalled improvements.

**Anti-pattern: silent breaking changes.** Renaming a token mid-MINOR-release breaks consumers without warning. If it's breaking, it's MAJOR; if it's not breaking, prove it.

**Anti-pattern: design-system PRs without changelog updates.** The changelog should land with the change, not after the release. Reviewers should reject PRs that don't update it.

**Anti-pattern: design-system that absorbs every app-specific pattern.** Every team's special-snowflake component pulled into the system bloats the surface area and produces conflicting requirements. The two-consumer rule is the defense.

**Anti-pattern: indefinite deprecation.** A deprecation that lingers for years without removal teaches consumers that deprecations don't mean anything. Set removal targets; honor them.

**Anti-pattern: no version cadence.** Releases happen sporadically; consumers don't know when to plan upgrades. Establish cadence (monthly minor; quarterly major) and stick to it.

## Cross-references

- **Token architecture governance applies to:** see `tokens.md`.
- **Theming governance for theme additions / removals:** see `theming.md`.
- **Component patterns the system codifies:** see `KB-component-architecture-design/references/patterns.md`.
- **Storybook publishing for the design system:** see `KB-storybook-platform/references/composition.md`.
- **Keep a Changelog format:** `keepachangelog.com`.
- **ADR pattern (foundational):** Nygard, Michael. "Documenting Architecture Decisions." 2011.
- **Semver specification:** `semver.org`.
