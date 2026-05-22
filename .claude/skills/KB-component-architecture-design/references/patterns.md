# Composition Patterns

Six canonical patterns shape how component APIs are designed: compound components, slot patterns (with both senses including Radix-style `asChild`), polymorphic components (`as` prop), controlled vs uncontrolled state, ref forwarding (forwardRef in React 18; implicit ref-as-prop in React 19), and prop API design. Each pattern is a vocabulary for solving a recurring shape problem; this file covers what each is, when to reach for it, and how the patterns combine.

## Contents

- [x] Compound components
- [x] Slot patterns (render prop slot + Radix `asChild`)
- [x] Polymorphic components (`as` prop)
- [x] Controlled vs uncontrolled state
- [x] Ref forwarding (forwardRef + React 19 implicit ref)
- [x] Prop API design discipline
- [x] Combining patterns
- [x] Cross-references

## Compound components

The compound-component pattern: a single logical component is exposed as **several sub-components that share state through context**. Consumers compose them; the parent component supplies state, sub-components read from it.

```tsx
// Consumer
<Tabs defaultValue="account">
  <Tabs.List>
    <Tabs.Trigger value="account">Account</Tabs.Trigger>
    <Tabs.Trigger value="password">Password</Tabs.Trigger>
  </Tabs.List>
  <Tabs.Content value="account">...</Tabs.Content>
  <Tabs.Content value="password">...</Tabs.Content>
</Tabs>
```

Implementation outline:

```tsx
const TabsContext = createContext<TabsContextValue | null>(null);

function Tabs({ defaultValue, children }: TabsProps) {
  const [value, setValue] = useState(defaultValue);
  return (
    <TabsContext.Provider value={{ value, setValue }}>
      <div>{children}</div>
    </TabsContext.Provider>
  );
}

function TabsList({ children }: { children: ReactNode }) {
  return <div role="tablist">{children}</div>;
}

function TabsTrigger({ value, children }: { value: string; children: ReactNode }) {
  const ctx = useContext(TabsContext);
  if (!ctx) throw new Error('TabsTrigger must be inside Tabs');
  return (
    <button
      role="tab"
      aria-selected={ctx.value === value}
      onClick={() => ctx.setValue(value)}
    >
      {children}
    </button>
  );
}

// (TabsContent similar)

Tabs.List = TabsList;
Tabs.Trigger = TabsTrigger;
Tabs.Content = TabsContent;
```

When to reach for compound components:

- Several elements coordinate (selection state shared across triggers and content; expansion state shared across header and panel; menu state shared across button and items).
- The consumer needs to control composition (which trigger contains which icon; where labels appear; conditional visibility of some sub-elements).
- A single monolithic component with deeply-nested props would lose flexibility (`<Tabs items={[...]} renderContent={...} />` quickly bloats).

When NOT to: when the component has no internal coordination (a `Button` doesn't need `Button.Label` and `Button.Icon` as compound parts — just accept `children`).

Three considerations:

- **Type safety on context.** TypeScript's `createContext<X | null>(null)` is canonical; consumers' hook checks ensure non-null. Don't ship a Context with a "default value" — make absence a runtime error.
- **Anonymous children vs named slots.** The pattern shown above uses named sub-components (`Tabs.Trigger`). An alternative passes structured children (`<Tabs triggers={[...]} contents={[...]} />`). The named-sub-component form is more flexible; the structured-children form is less ceremonious for simple cases.
- **Export pattern.** `Tabs.List` (attached to the function) vs separate exports (`{ Tabs, TabsList }`). Attached-form is more discoverable in IDE autocomplete; separate-exports-form plays better with named imports. Choose project-level convention.

## Slot patterns

Two distinct senses of "slot" exist in the React ecosystem.

**Sense 1: render-prop slot.** A component accepts a function-as-child or a render prop that controls a specific region. Headless UI uses this form widely:

```tsx
<Combobox value={selected} onChange={setSelected}>
  {({ open }) => (
    <>
      <Combobox.Button>{open ? 'Hide' : 'Show'}</Combobox.Button>
      <Combobox.Options>...</Combobox.Options>
    </>
  )}
</Combobox>
```

The slot here is the children render-prop; its argument is the component's internal state (`{ open }`). Consumer-side, the function-as-children carries the state-dependent rendering.

**Sense 2: Radix-style `asChild`.** A component accepts an `asChild` boolean. When true, the component does NOT render its own DOM element; instead, it clones its single child element and merges props onto it.

```tsx
<Dialog.Trigger asChild>
  <button className="my-button">Open</button>
</Dialog.Trigger>
```

Without `asChild`, Radix renders a `<button>` (the trigger's default). With `asChild`, Radix merges the trigger's props onto the consumer's `<button>` — same accessibility, same event handlers, but no wrapper element.

Implementation: Radix exports a `<Slot>` primitive (in `@radix-ui/react-slot`) that the trigger uses internally when `asChild` is true. The Slot's job: clone child; merge props (including refs, event handlers — with proper composition for double-fired events).

When to reach for slot patterns:

- **Render-prop slot:** when the consumer needs to read internal state to render conditionally (open/closed; selected; loading). Render props are flexible but verbose — they introduce a function call layer in JSX.
- **`asChild`:** when the consumer wants to use a custom element (their own `<Button>`, a Next.js `<Link>`) without adding wrapper DOM. The pattern is now standard in Radix-style libraries and is the dominant pattern in 2024-2026 design systems.

The `asChild` pattern's advantages:

- No wrapper DOM (better for semantics and styling).
- Composes with any existing component (no per-component "as" boilerplate).
- Refs and event handlers merge properly via `<Slot>` machinery.

When NOT to use `asChild`: when the component's default rendering is genuinely fixed (an `<Avatar>` always renders an `<img>`-equivalent; consumers don't need to substitute). Forced `asChild` everywhere creates noise.

## Polymorphic components (`as` prop)

A polymorphic component accepts an `as` prop that determines the rendered element. The component preserves its visual style; the underlying tag changes.

```tsx
<Heading as="h1">Page Title</Heading>
<Heading as="h2">Section</Heading>
<Heading as="p">Visually-styled paragraph</Heading>
```

Implementation:

```tsx
type HeadingProps<C extends ElementType = 'h1'> = {
  as?: C;
  children: ReactNode;
} & Omit<ComponentPropsWithoutRef<C>, 'as' | 'children'>;

function Heading<C extends ElementType = 'h1'>({
  as,
  children,
  ...rest
}: HeadingProps<C>) {
  const Component = as || 'h1';
  return <Component {...rest}>{children}</Component>;
}
```

Type safety requires generics to thread the `as` value through to the underlying element's props. The pattern is well-known but tricky; libraries like `@radix-ui/react-polymorphic` or `react-polymorphic-types` provide reusable helpers.

When to reach for polymorphism:

- Visual style and semantic element are independent (a "button-looking" element that's actually a link; a "heading-styled" element that should be a `<p>` for semantic correctness).
- The component is broadly reused with varied underlying elements.

When NOT to:

- When `asChild` is available (Radix-style). `asChild` is more flexible — it accepts any element, not just HTML tags — and avoids the generics complexity. Most modern projects use `asChild` over `as` for new code.
- When the polymorphism is a sign of misuse (a "card" component being asked to be a button, an anchor, AND a div — probably the component should be split).

The state of the practice in 2026: `asChild` is dominant; `as` survives in projects with significant Chakra UI legacy or in non-React frameworks where `asChild` patterns are less developed.

## Controlled vs uncontrolled state

A component's state can be owned by the component itself (uncontrolled) or by the parent (controlled). The canonical API supports both via `defaultValue` (uncontrolled initial) and `value` + `onChange` (controlled):

```tsx
// Uncontrolled
<Input defaultValue="hello" />

// Controlled
const [value, setValue] = useState('hello');
<Input value={value} onChange={(e) => setValue(e.target.value)} />
```

Implementation pattern (manually):

```tsx
function Input({
  value: valueProp,
  defaultValue,
  onChange,
}: InputProps) {
  const [internalValue, setInternalValue] = useState(defaultValue ?? '');
  const isControlled = valueProp !== undefined;
  const value = isControlled ? valueProp : internalValue;

  const handleChange = (e: ChangeEvent<HTMLInputElement>) => {
    if (!isControlled) setInternalValue(e.target.value);
    onChange?.(e);
  };

  return <input value={value} onChange={handleChange} />;
}
```

React provides `useControllableState` patterns in libraries (Radix exports `@radix-ui/react-use-controllable-state`); the principle is the same.

Discipline:

- **Never accept BOTH `value` and `defaultValue`.** If both are passed, prefer `value` (controlled wins) and warn in development. The "controlled component changing between controlled and uncontrolled" React warning is the consumer-facing version of this.
- **Don't expose internal state via uncontrolled-only API.** If consumers need to read the value (validation; submission), they need controlled mode. Don't ship `defaultValue` without `value` + `onChange`.
- **Honor the `onChange` contract.** In uncontrolled mode, `onChange` still fires (so consumers can observe without controlling). The component owns the value; the consumer observes.

## Ref forwarding (forwardRef + React 19 implicit ref)

A component that consumers need to ref must forward refs to the underlying DOM element.

**React 18 and earlier — `forwardRef`:**

```tsx
const Button = forwardRef<HTMLButtonElement, ButtonProps>(
  function Button(props, ref) {
    return <button {...props} ref={ref} />;
  }
);
```

The `forwardRef` HOC is required; without it, `ref` props are silently ignored. Refs are a second argument to the inner function, not a prop on the props object.

**React 19+ — implicit ref-as-prop:**

```tsx
function Button(props: ButtonProps & { ref?: Ref<HTMLButtonElement> }) {
  return <button {...props} />;
}
```

React 19 (October 2024) removed the need for `forwardRef`. Refs are passed as ordinary props; function components can declare `ref` in their props type and use it directly. `forwardRef` is now deprecated; new code should use the implicit-ref pattern.

Migration: existing `forwardRef`-using components continue to work (backwards compatible). A codemod (`npx codemod react/19/replace-use-form-state`-style; the official Codemod CLI has `react/19/replace-forwardRef`) automates the transition.

Discipline:

- **Always forward refs from components consumers may need to measure / focus / scroll.** Buttons, inputs, dialogs, scrollable containers, anchors — anything where consumer code may need to interact with the DOM directly.
- **Don't forward refs from purely presentational components.** A `<Spacer>` doesn't need ref forwarding; refs to it have no use.
- **Type the ref explicitly.** `Ref<HTMLButtonElement>` not `Ref<any>`. The type matters for consumer-side autocomplete (`ref.current?.focus()` discovers `focus()` only with the right type).

## Prop API design discipline

A component's prop surface is its contract. Six principles:

**1. Required vs optional props are deliberate.** Required props express the component's irreducible inputs. Optional props with sensible defaults express variation. Avoid required props that have a clear default — defaulting reduces caller boilerplate.

**2. Enum props use string literal unions, not strings.** `variant: 'primary' | 'secondary' | 'ghost'`, not `variant: string`. TypeScript surfaces typos as type errors; autocomplete enumerates options. This is the most impactful single discipline for prop APIs.

**3. Boolean props for binary; enum props for ternary+.** A `disabled` boolean is fine. A `size` shouldn't be `small={true}` + `large={true}` — use `size: 'sm' | 'md' | 'lg'`. Multiple booleans interacting (`isPrimary` + `isLarge` + `isOutlined`) become an explosion of states quickly; enums collapse the state space.

**4. Render-controlled content via children; data-controlled content via props.** A `Card` accepting `<Card.Title>` as children gives the consumer composition flexibility. A `Card` accepting `title="..."` as a prop is simpler when the title is always plain text. Choose based on whether the consumer needs flexibility.

**5. Event handler naming follows the on-event convention.** `onClick`, `onChange`, `onOpen`, `onClose`, `onValueChange`. Not `clickHandler`, not `handleClick`, not `whenChanged`.

**6. Resist prop bloat.** When a component has >12 props, it's probably under-decomposed. Consider compound components, slot patterns, or splitting into multiple components.

## Combining patterns

Real components combine multiple patterns. A canonical `Dialog`:

- **Compound** at the consumer level: `<Dialog.Root>`, `<Dialog.Trigger>`, `<Dialog.Content>`, `<Dialog.Close>`.
- **Slot pattern (`asChild`)** on `<Dialog.Trigger>` and `<Dialog.Close>`: consumers can use their own `<Button>` as the trigger/close without wrapper DOM.
- **Controlled vs uncontrolled** on `<Dialog.Root>`: `open` + `onOpenChange` (controlled) or `defaultOpen` (uncontrolled).
- **Ref forwarding** on `<Dialog.Content>`: consumers may need to ref for measurement or focus.
- **Prop API discipline:** required `open`/`defaultOpen` choice; enum for `size: 'sm' | 'md' | 'lg' | 'fullscreen'`; boolean `modal` for backdrop-blocking variant.

The patterns compose; a well-designed component uses several.

## Cross-references

- **Headless libraries that exhibit these patterns:** see `headless-libraries.md`. Radix, React Aria, Ariakit are the canonical references for compound + slot + controlled implementations.
- **Atomic design as a higher-level decomposition lens:** see `atomic-design.md`.
- **Storybook for surfacing pattern variants:** see `KB-storybook-platform/references/story-format.md` (every pattern variant becomes a story).
- **React 19 release notes for ref-as-prop migration:** `react.dev/blog/2024/12/05/react-19`.
