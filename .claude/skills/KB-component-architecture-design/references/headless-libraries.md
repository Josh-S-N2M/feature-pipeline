# Headless Libraries

"Headless" component libraries supply behavior and accessibility without prescribing visual styling. They handle the hard parts — keyboard navigation, focus management, ARIA attributes, state machines — and let consumers style as they wish. The landscape has matured substantially since 2020; in 2026 the choice between five mature options shapes most projects' component foundations.

## Contents

- [x] What "headless" means
- [x] The five libraries
- [x] Radix UI
- [x] React Aria (Adobe)
- [x] Headless UI (Tailwind Labs)
- [x] Ariakit
- [x] shadcn/ui — vendoring approach
- [x] Choosing between them
- [x] Patterns and anti-patterns
- [x] Cross-references

## What "headless" means

A headless component library:

- **Implements behavior + a11y** — keyboard interactions, focus management, ARIA attributes, state coordination.
- **Does not implement visuals** — no opinionated CSS; consumers style entirely.
- **Exposes primitives** — building-block components that compose into the consumer's intended structure.
- **Composes with the consumer's design system** — tokens, themes, and styling decisions stay with the consumer.

The contrast: "styled" libraries (Material UI, Chakra, Mantine) ship opinionated visual decisions; replacing the styling is hard. Headless libraries leave visuals open by design.

The value: implementing accessible custom controls (combobox, listbox, tabs, dialog, popover, menu, tree) correctly is hard. The ARIA Authoring Practices Guide documents the keyboard expectations and ARIA attribute requirements per pattern; getting them right requires sustained attention. Headless libraries provide vetted implementations of the hard patterns; consumers compose them with their own visual decisions.

## The five libraries

The 2026 landscape has five major options. They differ in scope, maturity, and the surface area they cover.

| Library | Origin | Scope | API style |
|---|---|---|---|
| **Radix UI** | Workos (formerly indie) | ~30 primitives | Compound components |
| **React Aria** | Adobe | ~50 hooks + components | Hook-based + components |
| **Headless UI** | Tailwind Labs | ~15 primitives | Compound + render-prop |
| **Ariakit** | Indie (Ariakit team) | ~50 primitives | Compound + custom hooks |
| **shadcn/ui** | Indie (shadcn) | Distribution + vendoring | Component sources copy-pasted |

shadcn/ui is structurally different — it's a distribution mechanism that vendors Radix-based components into your project rather than a runtime library. Worth its own section.

## Radix UI

Radix UI provides unstyled, accessible component primitives. Each component family (Dialog, Dropdown Menu, Popover, etc.) exposes compound parts.

```tsx
import * as Dialog from '@radix-ui/react-dialog';

function MyDialog() {
  return (
    <Dialog.Root>
      <Dialog.Trigger>Open</Dialog.Trigger>
      <Dialog.Portal>
        <Dialog.Overlay className="bg-black/50 fixed inset-0" />
        <Dialog.Content className="bg-white p-6 rounded-md fixed top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2">
          <Dialog.Title>Confirm action</Dialog.Title>
          <Dialog.Description>This will delete the item.</Dialog.Description>
          <Dialog.Close>Cancel</Dialog.Close>
          <button onClick={confirm}>Delete</button>
        </Dialog.Content>
      </Dialog.Portal>
    </Dialog.Root>
  );
}
```

Strengths:

- **Comprehensive a11y.** Focus management, focus trap, scroll lock, keyboard handling all correct.
- **Compound API.** Each part is a separate component; consumers compose freely.
- **`asChild` slot pattern.** Lets consumers swap the underlying element while keeping behavior. Powerful for integration with other libraries (e.g., `<Dialog.Trigger asChild><Button>Open</Button></Dialog.Trigger>`).
- **Active maintenance.** Acquired by Workos in 2024; sustained investment.

Limitations:

- **React only.** No Vue / Svelte / vanilla equivalent (community ports exist but aren't first-party).
- **Some primitives lack scope.** No data table, no virtualized list. Covers interactive primitives, not data-display.

When to reach for Radix: React projects needing high-quality accessible primitives for dialogs, popovers, menus, tabs, selects, etc. The default for new React projects in 2026.

## React Aria (Adobe)

Adobe's React Spectrum project produces React Aria — a comprehensive set of hooks + components for building accessible UI. The hook API (`useDialog`, `useButton`, `useComboBox`) supplies behavior to consumer-provided JSX; the component API (Spectrum-style) provides ready-to-use components.

```tsx
import { useButton } from 'react-aria';
import { useRef } from 'react';

function MyButton(props) {
  const ref = useRef(null);
  const { buttonProps } = useButton(props, ref);
  return (
    <button {...buttonProps} ref={ref} className="...">
      {props.children}
    </button>
  );
}
```

Or with the component API:

```tsx
import { Button } from 'react-aria-components';

function MyButton(props) {
  return <Button {...props} className="..." />;
}
```

Strengths:

- **Most comprehensive a11y implementation in the ecosystem.** Adobe invests heavily; covers patterns Radix doesn't (date pickers, color pickers, drag-and-drop, virtualized lists).
- **Hook-based API for full control.** Consumers control the markup completely; hooks supply the behavior.
- **Internationalization built-in.** RTL, locale-aware date/number formatting, locale-aware keyboard handling.
- **Adobe's design system (Spectrum) backs it.** Real-world hardened.

Limitations:

- **Steeper learning curve.** Hook APIs are more verbose than compound-component APIs.
- **API churn historically.** Less so since 2024; stable now.
- **React only.**

When to reach for React Aria: projects needing the absolute best a11y (Adobe-grade); projects with international audience (i18n is first-class); projects needing exotic patterns (date pickers; drag-and-drop) Radix doesn't cover.

## Headless UI (Tailwind Labs)

Headless UI is Tailwind Labs' component library. Smaller in scope than Radix or React Aria; focused on common patterns. Pairs naturally with Tailwind CSS but doesn't require it.

```tsx
import { Dialog } from '@headlessui/react';

function MyDialog({ isOpen, onClose }) {
  return (
    <Dialog open={isOpen} onClose={onClose}>
      <Dialog.Overlay className="fixed inset-0 bg-black/50" />
      <Dialog.Panel className="bg-white p-6 rounded-md">
        <Dialog.Title>Confirm</Dialog.Title>
        <Dialog.Description>This will delete the item.</Dialog.Description>
        <button onClick={onClose}>Cancel</button>
      </Dialog.Panel>
    </Dialog>
  );
}
```

Strengths:

- **Compact API.** Easier to learn than Radix or React Aria.
- **Tailwind integration.** Tailwind-friendly defaults (the library doesn't enforce Tailwind but pairs cleanly).
- **Vue version available** (`@headlessui/vue`). One of few libraries with first-party Vue support.

Limitations:

- **Narrower scope.** ~15 primitives vs Radix's ~30 or React Aria's ~50. Some patterns absent.
- **Less active development.** Sustained but slower-moving than Radix or React Aria.

When to reach for Headless UI: projects on Tailwind; projects on Vue that want first-party Vue support; projects whose component needs fit within Headless UI's scope.

## Ariakit

Ariakit (formerly Reakit) is an independent React headless library with broad scope similar to Radix. Hook-based API plus compound components.

```tsx
import { Dialog, useDialogStore } from '@ariakit/react';

function MyDialog() {
  const dialog = useDialogStore();
  return (
    <>
      <button onClick={dialog.toggle}>Open</button>
      <Dialog store={dialog} className="...">
        <h2>Confirm</h2>
        <p>This will delete the item.</p>
        <button onClick={dialog.hide}>Cancel</button>
      </Dialog>
    </>
  );
}
```

Strengths:

- **Comprehensive a11y.** On par with Radix.
- **Store-based API.** Behavior state lives in a store; multiple components share it. Cleaner for complex interactions (composite widgets that span multiple visual components).
- **Strong patterns docs.** The site documents ARIA patterns clearly, separate from the library.

Limitations:

- **Smaller community.** Less ecosystem support; fewer examples to crib from.
- **React only.**

When to reach for Ariakit: projects valuing the store-based API; projects whose composer prefers Ariakit's documentation style.

## shadcn/ui — vendoring approach

shadcn/ui is structurally different from the libraries above. It's a CLI distribution that VENDORS component sources into your project. The components are built on Radix primitives + Tailwind CSS; the CLI copies the component files into your repo where you own them.

```bash
npx shadcn-ui@latest add button dialog tabs
```

Output: `components/ui/button.tsx`, `components/ui/dialog.tsx`, `components/ui/tabs.tsx` in your project. You modify them as needed.

Strengths:

- **Full ownership of component code.** No runtime dependency; no version upgrades; no library API changes affecting you.
- **Reasonable defaults.** The Radix + Tailwind composition is pre-built; you don't start from zero.
- **Customizable.** Components are yours; modify freely.

Limitations:

- **Maintenance burden moves to you.** When shadcn updates components, you re-vendor (or stay on old versions). No automatic upgrades.
- **No actual library to publish.** You can't easily share customizations across projects without re-establishing the vendoring pattern.
- **Couples to Tailwind.** The components assume Tailwind; switching styling approach requires rewrites.

When to reach for shadcn/ui: projects on Tailwind that want a head-start on component implementation; projects that prefer owning component code over depending on a library.

## Choosing between them

Decision factors:

| Factor | Radix | React Aria | Headless UI | Ariakit | shadcn/ui |
|---|---|---|---|---|---|
| React-only ok? | ✓ | ✓ | + Vue | ✓ | ✓ |
| Tailwind-coupled? | no | no | natural fit | no | yes |
| Compound vs hooks? | compound | both | compound | both | compound (vendored) |
| a11y depth | high | highest | high | high | inherits Radix |
| i18n built-in? | basic | yes | basic | basic | inherits Radix |
| Scope (# of primitives) | ~30 | ~50 | ~15 | ~50 | inherits Radix |
| Maintenance burden on consumer | low | low | low | low | high (vendoring) |

Defaults for 2026:

- **React + custom styling**: Radix UI. The compound API and `asChild` pattern are the comfortable default.
- **React + need exotic patterns (date pickers; drag-drop)**: React Aria.
- **Vue or Tailwind-first projects**: Headless UI.
- **Tailwind + want a head-start**: shadcn/ui (vendoring approach).
- **Existing Ariakit codebase**: Ariakit.

Most projects use ONE of these libraries plus their own component layer on top. Mixing multiple headless libraries within one project produces inconsistency in patterns.

## Patterns and anti-patterns

**Pattern: wrap headless primitives in project-specific components.** Don't expose Radix's `<Dialog.Root>` directly to consumers; wrap it in your project's `<Modal>` component that applies your styling, your defaults, and your domain language.

**Pattern: use `asChild` (Radix) or polymorphism for integration.** When you need a Radix trigger to be your `<Button>` component, `asChild` is the integration. Don't fight the pattern by re-implementing.

**Pattern: keep all headless primitives in one centralized layer.** A `components/primitives/` or `components/ui/` directory hosts the wrappers. Consumers reach for the wrappers, not the headless library directly.

**Anti-pattern: mixing headless libraries.** Half the modals are Radix; half are Headless UI. Patterns diverge; muscle memory fails. Pick one library and migrate inherited code to it.

**Anti-pattern: rebuilding what the headless library provides.** A custom dialog component because "Radix is overkill" almost always misses some a11y discipline (focus restoration; focus trap; scroll lock; keyboard handling). The libraries exist because the patterns are HARD; reach for them.

**Anti-pattern: tight coupling to library internals.** Importing from `@radix-ui/react-dialog/dist/...` rather than the public API. Internals change; your code breaks.

## Cross-references

- **Component decomposition that headless libraries serve:** see `atomic-design.md`.
- **Component patterns (compound; slot; polymorphic) that headless libraries embody:** see `patterns.md`.
- **Storybook patterns for testing headless-based components:** see `KB-storybook-platform/references/testing.md`.
- **ARIA Authoring Practices Guide:** `w3.org/WAI/ARIA/apg`. The vendor-neutral source for what "accessible custom control" means.
- **Radix UI documentation:** `radix-ui.com/primitives/docs`.
- **React Aria documentation:** `react-spectrum.adobe.com/react-aria`.
- **Headless UI documentation:** `headlessui.com`.
- **Ariakit documentation:** `ariakit.org`.
- **shadcn/ui documentation:** `ui.shadcn.com`.
