# Anti-Slop — Refusing the AI-Default Aesthetic

This document names a particular failure mode of AI-assisted design — convergence on a recognizable default aesthetic the design layer should explicitly recognize and refuse — and supplies the discipline for doing so.

**Source dependency:** the Anthropic `frontend-design` skill at `/mnt/skills/public/frontend-design/SKILL.md` (released 2025-11-12) is the authoritative primary source. This file cites it, summarizes its taxonomy, and adds project-local pedagogical framing.

> **Pedagogical framing for this file.** This file deliberately NAMES specific fonts, colors, and aesthetic patterns that are common AI-default reaches. The naming IS the discipline — the design layer needs to RECOGNIZE these signatures to refuse them. Where this file lists specific font names, color values, or visual patterns, those names are reference content (signatures to recognize), not project-prescribed defaults (names to use).
>
> Per mechanism α (ADR-0030), no pedagogical marker wraps this file's content because the content is documentation prose, not credential-shaped or finding-triggering content. The named signatures here are plain text — the auditor doesn't flag them, and no demotion is needed.

## Contents

- [x] Why anti-slop is a discipline
- [x] The five aesthetic dimensions (Anthropic taxonomy)
- [x] Named signatures to recognize
- [x] Calibration exemplars
- [x] Process discipline
- [x] When defaults are appropriate
- [x] Source dependencies
- [x] Cross-references

## Why anti-slop is a discipline

Models trained on the web's surface tend to converge on a narrow visual default. The training distribution overrepresents certain aesthetic choices (whatever was popular in 2018-2023 design Twitter; the Tailwind UI marketing style; the bootcamp-tutorial sensibility); models reach for those choices when not directed otherwise. The result is a recognizable AI-default look — interfaces with no aesthetic identity, distinguishable only by content.

The Anthropic Cookbook's October 2025 piece on AI-generated frontend coined the term "distributional convergence" for this. Their `frontend-design` skill (released November 2025) codifies the refusal discipline as a production-grade reference. This file extends that work for this project's design-agent network.

The discipline is NOT anti-default-fonts or anti-particular-colors. It's anti-DEFAULTING. A project deliberately choosing Inter for legitimate brand reasons is fine. A project using Inter because the agent reached for the default and no one challenged the choice is the failure mode.

## The five aesthetic dimensions (Anthropic taxonomy)

The Anthropic frontend-design skill organizes aesthetic decisions into five dimensions. Each dimension has AI-default signatures the discipline learns to recognize:

1. **Typography** — typeface choice, scale, weight, pairing.
2. **Color & theme** — palette structure, contrast, semantic colors, dark mode.
3. **Motion** — animation duration, easing, presence of motion at all.
4. **Spatial composition** — layout, density, hierarchy, alignment.
5. **Backgrounds & visual details** — gradients, textures, illustrations, decorative elements.

Each dimension's defaults are explored below. The discipline: when a design surface is presented for review, walk each dimension and ask "is this a considered choice or a defaulted one?"

## Named signatures to recognize

### Typography signatures

The dominant AI-default font reaches:

- Inter — the most-reached-for sans-serif. Originally designed by Rasmus Andersson for UI rendering at small sizes. Excellent typeface; overused as a default. When a project's design layer reaches for it without articulating why, that's the signal.
- Roboto — Google's Material default; reached for in Android-adjacent and Google-Cloud-adjacent contexts. Same overuse pattern.
- San Francisco / -apple-system — the macOS / iOS default. Defensible as a system-font fallback; AI-default when used as the primary brand face for cross-platform products.
- Space Grotesk — has emerged as the "modern-looking" reach since ~2022. Its geometric shapes signal "design-aware product" without committing to identity. The tell.
- Segoe UI — the Windows system font; AI-default in Microsoft-adjacent contexts.

The pattern: fonts engineered for system-default ubiquity get reached for as if they were brand decisions. They aren't. They're the typography equivalent of "we'll figure out brand later."

Brand-distinctive faces: serifs with personality (Tiempos; Lyon; GT Sectra); humanist sans-serifs (Söhne; Inter Tight with deliberate weight choices; custom drawn faces). The presence of a deliberate choice is the marker of consideration; the specific choice matters less than the act of choosing.

### Color & theme signatures

The dominant AI-default palette reaches:

- **Purple-on-white gradients.** The dominant marketing-aesthetic gradient since ~2020. Purple-to-blue, purple-to-pink, purple-to-indigo. When a product page opens with a purple gradient hero, that's the signal.
- **Subdued grayscale neutral palettes with one accent.** Often the accent is blue (#3B82F6 / Tailwind blue-500) or purple (#8B5CF6 / Tailwind violet-500). The "tasteful and safe" choice.
- **Tailwind default palette without remapping.** Tailwind's defaults are useful primitives. Using them as the semantic colors (text-gray-900 for body; bg-blue-500 for primary buttons) is the AI-default pattern. Tailwind expects projects to remap; not remapping is the tell.
- **Pure black-on-white** — when a project uses `#000` on `#FFF` for body text, it almost always wasn't a decision. True black creates excessive contrast; off-black (`oklch(15% 0 0)` ≈ #1F1F1F) is the considered choice.

The pattern: palette decisions imported wholesale from popular UI libraries become indistinguishable across products. The semantic layer (`--color-text-primary` mapped to brand-specific values) is where consideration shows.

### Motion signatures

The dominant AI-default motion reaches:

- **Generic `ease` or `ease-in-out` everywhere.** No semantic curves. Modal slides in with `ease`; toast appears with `ease`; button settles with `ease`. The default curve is acceptable; absence of curve VARIETY is the tell.
- **Fade-in-on-scroll.** The hero element fading in as it enters the viewport. Marketing-page motion imported to product UIs.
- **Hover scale transforms (`transform: scale(1.05)` on every interactive element).** Conveys "I'm interactive" but adds no other meaning. Over-applied.
- **Generic spring physics with default tension.** Framer Motion or React Spring defaults applied without tuning. Bouncy where bounce isn't called for.

The pattern: motion that doesn't communicate causality, orientation, or feedback (see `motion.md`) is decoration. Decorative motion is the marker of defaulting.

### Spatial composition signatures

The dominant AI-default layout reaches:

- **The shadcn/ui layout (centered max-width container; sidebar; main content area).** Excellent for many products; the AI-default reach when no consideration has been given. When every product looks like the shadcn examples, the look is no longer differentiated.
- **Card-grid everywhere.** Three-column card grid for every list. Lists aren't always grids; cards aren't always the right container.
- **Excessive shadowing.** Every container has a soft drop shadow. Depth without purpose.
- **Generous spacing as a substitute for hierarchy.** When elements have so much space between them that visual relationships are obscured, the layout is failing to communicate structure.

The pattern: spatial decisions defaulted to "modern-looking" templates without articulating what the spacing COMMUNICATES.

### Backgrounds & visual details signatures

The dominant AI-default detail reaches:

- **Gradient backgrounds (purple-to-blue; pink-to-orange) on hero sections.** Marketing-page convention transplanted.
- **Subtle grid backgrounds (faint dot or line grids).** The "developer tool" aesthetic.
- **Generic 3D illustrations of abstract concepts.** Pastel-colored isometric people-doing-tasks illustrations. The marketing-illustration default.
- **Geometric blob shapes.** Curved organic shapes overlaid on hero sections.
- **Emoji as illustration.** Using emoji to represent product features or status states. Sometimes appropriate; default-reached too often.

The pattern: visual details added to "fill space" rather than to express identity or aid comprehension.

## Calibration exemplars

Six interfaces worth studying for what considered visual design looks like in shipped products:

- **Linear** — the issue tracker. Distinctive monochrome aesthetic with carefully tuned typography (Inter, but with deliberate weight variation and a custom monospace for IDs). Compact density; high information per pixel; restrained motion. Defies the "dense = ugly" reflex.
- **Stripe** — the payments product. Sober color palette; mature typography (custom Sohne family); restrained gradients (when used, they communicate brand). Marketing motion is purposeful; product UI motion is minimal.
- **Vercel** — the deployment platform. Stark monochrome aesthetic with sparing accent color. Geist font family designed in-house. Marketing site that doesn't read AI-default.
- **Arc Browser** — the browser. Distinctive identity through layout and motion rather than typography; the sidebar-as-tab pattern is an identity. Color used purposefully (per-space coloring).
- **Figma** — the design tool. Dense, considered, internally consistent. Custom monospace; custom UI font (Whyte). Motion that communicates causality (canvas transformations).
- **Notion** — the document/database tool. Restrained palette; reading-optimized typography (custom serif for headings; system sans for body in many themes). Modest motion; high information per pixel without feeling dense.

The pattern across these exemplars: identity through choice (not template); restraint over expression in the product UI; motion that earns its place. None look like each other; none look AI-default.

## Process discipline

When the design layer encounters a feature, walk the five dimensions and ask, per dimension:

1. **What was the choice?** (Name it explicitly — "we used Inter at the default Tailwind sizes").
2. **What does the choice communicate?** (If you cannot articulate, the choice is undisciplined.)
3. **What would a brand-considered alternative be?** (Even rhetorical — "if this were a fintech product, we'd reach for a serif headline").
4. **Are we defaulting or deciding?** (The blunt question.)

Defaulting is acceptable when explicitly chosen ("we're prototyping; brand work is downstream"). Defaulting unaware is the failure mode this discipline addresses.

## When defaults are appropriate

Three contexts where AI-default aesthetics are fine:

- **Prototypes and proofs of concept.** The goal is validating the idea, not the aesthetics. Default everything; iterate visual choices when the concept is validated.
- **Internal tools.** Tools used by 5 engineers don't need brand identity. Defaulting saves time; the tool's user research isn't about aesthetics.
- **Pre-brand stage.** Some products ship without a brand by intent (developer tools; APIs; backend services with thin UIs). The discipline is acknowledging this is the stage, not pretending defaults are decisions.

The failure mode is the IMPLICIT defaulting — the project that thinks it has a designed aesthetic but is actually shipping the AI-default. This file is the diagnostic tool.

## Source dependencies

This file's primary authoritative source is the Anthropic `frontend-design` skill:

- **Location:** `/mnt/skills/public/frontend-design/SKILL.md` in this project's environment.
- **Released:** 2025-11-12.
- **Authors:** Anthropic Cookbook team (originating piece: Prithvi Rajasekaran, October 2025).
- **Contains:** the five aesthetic dimensions taxonomy; named AI-default signatures; the "distributional convergence" framing.

When the upstream skill evolves, this file may need refresh. Refreshes are additive (new content; preserve existing) per ADR-0005. The naming convention (`` markers around named-signature instances) is project-local and stays consistent.

## Cross-references

- **Type, color, space discipline this file references:** see `type-color-space.md`.
- **Motion discipline this file references:** see `motion.md`.
- **The five aesthetic dimensions in tabular form for design-layer reference:** see `SKILL.md` of this KB.
- **Anthropic Cookbook piece on AI-generated frontend (October 2025):** referenced by the upstream skill; cite from the skill rather than directly.
- **Design-system-level token discipline that operationalizes anti-slop:** see `KB-design-system-design/references/tokens.md` (semantic tokens force naming what colors COMMUNICATE).
