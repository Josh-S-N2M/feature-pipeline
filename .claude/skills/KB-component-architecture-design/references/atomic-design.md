# Atomic Design

Brad Frost's atomic design methodology (introduced 2013; book *Atomic Design* 2016) supplies a decomposition vocabulary for UI components. The model is a mental tool, not a file-structure prescription — its dominant misuse is treating the tiers as a folder organization.

## Contents

- [x] The five tiers
- [x] Tier 1: atoms
- [x] Tier 2: molecules
- [x] Tier 3: organisms
- [x] Tier 4: templates
- [x] Tier 5: pages
- [x] Mental model, not file structure
- [x] When the model breaks down
- [x] Patterns and anti-patterns
- [x] Cross-references

## The five tiers

| Tier | Definition | Examples |
|---|---|---|
| Atoms | Foundational UI primitives that can't be broken down further without losing function | Button, Input, Label, Icon, Avatar |
| Molecules | Small functional groupings of atoms working together | SearchField (Input + Button + Icon), FormRow (Label + Input + ErrorMessage) |
| Organisms | Substantial sections; multiple molecules and atoms composed | Header (Logo + Nav + SearchField + UserMenu), ProductCard, DataTable |
| Templates | Page-level layouts without specific content; the structure | DashboardLayout, ArticleLayout, AuthLayout |
| Pages | Templates filled with real content | ProductsPage, AccountSettingsPage |

The tiers are a continuum, not discrete categories. An "organism" might be small enough to feel like a molecule in a different system; an "atom" might be composed of internal pieces that aren't called atoms.

## Tier 1: atoms

Atoms are the smallest meaningful UI units. The discipline:

- **Single-purpose.** A Button is a button. A Button-that-toggles-a-menu is a molecule, not an atom.
- **Composable.** Atoms accept variant props (`variant="primary"`), state props (`disabled`, `loading`), and content (`children`). They don't accept structural composition; that's what slots and molecules are for.
- **Token-consuming.** Atoms render with token-based styles. The Button's background is `var(--button-primary-bg)`, not a hardcoded color.
- **Accessibility-complete.** A Button atom must handle focus, keyboard activation, ARIA correctly. Atoms are NOT a place to "ship and add a11y later."

Examples of atoms with the boundary clearly drawn:

- **`Button`** — visual button with variant, size, state props. Renders `<button>` or (with polymorphism) other elements.
- **`Input`** — single text input. Doesn't include a label; that's molecule territory.
- **`Icon`** — single icon from the icon set. Accepts size and color props.
- **`Avatar`** — user representation. Accepts src + fallback + size.
- **`Badge`** — status indicator. Accepts variant + children.
- **`Spinner`** — loading indicator. Accepts size + color.

Atoms NOT in this list: `LoadingButton` (a Button with a Spinner is composition — handle via state, not a new atom), `IconButton` (Button with Icon child is composition).

## Tier 2: molecules

Molecules are small functional groupings — multiple atoms working together to deliver a single coherent unit of UI.

The discipline:

- **One job.** A SearchField does ONE thing: lets the user enter a query and submit it. If it grows responsibility (manage search history; show suggestions), it's becoming an organism.
- **Reusable.** Molecules are designed for reuse across pages. One-off groupings shouldn't be molecules; they should be inline composition in the consuming organism or page.
- **Mostly stateless or simply stateful.** Molecules manage their own UI state (open/closed; focused) but don't carry business state (which user is logged in).

Examples:

- **`SearchField`** — Input + Button + Icon configured as a search control. Manages its own value; emits a `submit` event.
- **`FormField`** — Label + Input + ErrorMessage + HelpText, with accessibility associations (id linking, aria-describedby). Carries the field's value.
- **`Dropdown`** — Trigger button + popover menu. Manages open/closed; renders children as menu items.
- **`Toast`** — visual notification with optional icon + close button. Auto-dismisses on a timer.
- **`Breadcrumbs`** — separator + path items + current page indicator.

## Tier 3: organisms

Organisms are substantial sections of an interface — multiple molecules and atoms composed into a coherent area.

The discipline:

- **Has identity.** A Header is recognizable as "the header"; a ProductCard is recognizable as "a product card." Organisms have visual and behavioral identity beyond their constituent parts.
- **May carry business state.** Organisms can be coupled to specific data shapes (the ProductCard knows about product objects). This is the tier where business coupling begins.
- **Composable but rarely re-composed.** Organisms appear in templates; they're not typically nested inside other organisms.

Examples:

- **`Header`** — site navigation, logo, search, user menu. Application-coupled.
- **`ProductCard`** — image, title, price, action button. Coupled to product shape.
- **`DataTable`** — column headers, rows, pagination, sorting, filtering. May be generic over row shape (a "headless data table" passing render props) or coupled to specific data.
- **`CommentThread`** — list of Comment components plus a Reply form.
- **`Sidebar`** — navigation tree + collapse affordance.

## Tier 4: templates

Templates are page-level layouts without specific content — the skeleton that pages fill in.

The discipline:

- **Composition only.** Templates are structural; they don't carry data or business logic.
- **Named slots.** Templates accept content into named regions ("header content," "main content," "sidebar content").
- **Few of them.** A product typically has 4-8 templates total; most pages use one of a few standard templates.

Examples:

- **`DashboardLayout`** — sidebar + main content area with sticky header.
- **`AuthLayout`** — centered card on a branded background.
- **`ArticleLayout`** — narrow content column with optional sidebar.
- **`SettingsLayout`** — sidebar with section navigation + main content area.

## Tier 5: pages

Pages are templates filled with specific content. The leaves of the component tree from the user's perspective.

The discipline:

- **One per route.** A page corresponds to a URL.
- **Composes organisms + templates.** A page knows what data it needs and which organisms to compose.
- **Owns data fetching.** Most projects scope data fetching to pages (route loaders; server components; page-level effects). Organisms below receive data via props.

Examples: `HomePage`, `ProductsPage`, `ProductDetailPage`, `AccountSettingsPage`.

In framework terms: pages correspond to route components in React Router / TanStack Router; to page modules in Next.js / Remix / SvelteKit; to view components in routing-based architectures broadly.

## Mental model, not file structure

The most common misuse of atomic design: organizing the codebase into `atoms/`, `molecules/`, `organisms/`, `templates/`, `pages/` folders. The problems:

- Files move tiers as the system matures (a molecule becomes an organism when it grows; a new atom is needed to support a complex molecule). File-moving as the dominant refactor is friction.
- The tier boundaries are fuzzy. Disagreements about whether SearchField is a molecule or an atom waste cycles.
- The tiers don't map well to feature boundaries. A "Checkout" feature might have its own Button (the checkout-specific submit button) — putting it under `atoms/` separates it from the feature.

Better organization: by feature or by component type, not by atomic tier:

```
components/
├── core/           # shared primitives (Button, Input, etc.)
├── feedback/       # Toast, Alert, Banner
├── navigation/     # Tabs, Breadcrumbs, Sidebar
├── data-display/   # Table, Card, List
├── overlays/       # Modal, Drawer, Popover
└── forms/          # Form, Field, Select

features/
├── checkout/       # checkout-specific components
├── account/        # account-specific components
```

Atomic design serves the conversation; the folder structure serves the developer experience. Don't conflate them.

## When the model breaks down

Atomic design works well for product UIs with broad component reuse. It works less well for:

- **Highly specialized tools** (CAD software; audio editors; CRMs with hundreds of unique controls). The bulk of the surface area is bespoke; the atom/molecule distinction is mostly irrelevant.
- **Data-heavy interfaces.** Dashboards with custom visualizations have many "organisms" that aren't reusable — they're project-specific.
- **Generative or content-first interfaces.** Static-site-generator-driven content layouts care about templates and pages; atom/molecule distinction is mostly invisible to consumers.

The model is a tool, not a doctrine. Apply where it helps; ignore where it doesn't.

## Patterns and anti-patterns

**Pattern: clear atom boundaries.** Every atom in the system has a documented single-purpose role. New atoms aren't added casually.

**Pattern: molecules emerge from observed reuse.** A pattern appearing in 2+ places gets extracted to a molecule. Pre-extraction (anticipating molecules that haven't appeared yet) produces wrong abstractions.

**Pattern: organisms own data coupling.** Organisms know about business objects; atoms and molecules don't. The line between molecules and organisms is often "does this know about the user / product / order shape?"

**Pattern: templates as composition primitives.** Pages compose templates and supply content; templates don't know what content fills them.

**Anti-pattern: file structure by atomic tier.** As above. Folders by tier produce friction without benefit.

**Anti-pattern: "atom" as universal primitive.** Calling everything reusable an "atom" dilutes the term. Reserve "atom" for single-purpose primitives; use "molecule" or other terms for composite reusables.

**Anti-pattern: enforcing strict tier boundaries via lint rules.** Disallowing "atoms importing molecules" or similar produces edge cases that fight productive composition. The tiers are heuristics, not laws.

**Anti-pattern: skipping tiers.** Going from page directly to atoms (no molecules or organisms) produces page-files of thousands of lines. The intermediate tiers exist to manage complexity.

## Cross-references

- **Component API patterns these tiers express:** see `patterns.md`.
- **Headless libraries supplying atom-level a11y discipline:** see `headless-libraries.md`.
- **Token consumption per tier:** see `KB-design-system-design/references/tokens.md`.
- **Visual design choices flowing through atomic tiers:** see `KB-visual-design/references/type-color-space.md`.
- **Atomic design foundational text:** Frost, Brad. *Atomic Design*. 2016. `atomicdesign.bradfrost.com`.
