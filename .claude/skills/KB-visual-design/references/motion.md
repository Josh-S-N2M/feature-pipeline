# Motion

UI motion is communicative, not decorative. State changes, affordance appearances, and feedback all carry information that motion can convey faster and more accurately than static change. This document covers the disciplines that distinguish considered motion from gratuitous animation.

## Contents

- [x] What UI motion does
- [x] Material 3 motion system
- [x] Apple HIG motion principles
- [x] Disney's twelve principles applied to UI
- [x] Easing curves with semantic names
- [x] Duration scales
- [x] `prefers-reduced-motion`
- [x] Patterns and anti-patterns
- [x] Cross-references

## What UI motion does

Three load-bearing roles for motion in interfaces:

1. **Explains causality.** When a button click opens a modal, the modal sliding up from the button location explains "this came from that." A modal that pops into the center of the screen invites the question "where did this come from?"
2. **Maintains spatial orientation.** When transitioning between screens, motion preserves the user's sense of where they are. Sliding left = forward; sliding right = back; expanding = drilling in; contracting = stepping out.
3. **Provides feedback.** State changes (loading → loaded; error appearing; success confirming) use motion to draw attention to what changed.

Motion that does none of these is decorative and almost always a net negative — it costs performance, costs `prefers-reduced-motion` user attention, and competes for visual attention with the content.

## Material 3 motion system

Google's Material 3 codifies motion as a system: tokens for duration, easing, and patterns. Worth knowing in detail because it's well-tuned and broadly applicable beyond Material projects.

**Duration tokens:**

| Token | Duration | Use |
|---|---|---|
| `motion-duration-short1` | 50ms | Tiny acknowledgments (button press) |
| `motion-duration-short2` | 100ms | Quick selection states |
| `motion-duration-short3` | 150ms | Small expansions |
| `motion-duration-short4` | 200ms | Medium component changes |
| `motion-duration-medium1` | 250ms | Bottom sheets opening |
| `motion-duration-medium2` | 300ms | Modal opening |
| `motion-duration-medium3` | 350ms | Larger transitions |
| `motion-duration-medium4` | 400ms | Full-screen transitions |
| `motion-duration-long1` | 450ms | Persistent navigation drawer |
| `motion-duration-long2` | 500ms | Large complex transitions |

**Easing curves:**

- **`emphasized`** (`cubic-bezier(0.2, 0, 0, 1)`) — the default for most transitions. Begins fast; eases out at the end. Drawing attention to the destination.
- **`emphasized-decelerate`** (`cubic-bezier(0.05, 0.7, 0.1, 1)`) — for elements entering the screen. Starts fast (off-screen); decelerates as it settles.
- **`emphasized-accelerate`** (`cubic-bezier(0.3, 0, 0.8, 0.15)`) — for elements leaving the screen. Starts slow; accelerates off.
- **`standard`** (`cubic-bezier(0.2, 0, 0, 1)`) — the older Material default; equivalent to emphasized.

The Material 3 documentation includes a complete motion specification at `m3.material.io/styles/motion`. Worth bookmarking.

## Apple HIG motion principles

Apple's Human Interface Guidelines treat motion as ambient atmosphere rather than codified system. Three principles distilled from the HIG:

1. **Motion communicates the system's structure.** Sheets slide up because content "comes from below"; navigation pushes left-to-right because forward is to the right. The motion expresses where things ARE in the system's mental model.
2. **Motion respects physics.** Inertia, momentum, gravity. Scroll views bounce when they hit boundaries; sheets settle into place with subtle overshoot. Motion that feels physical is more legible than motion that feels mechanical.
3. **Motion accommodates user preferences.** "Reduce Motion" is a system-level accessibility setting on Apple platforms. Apps that respect it (replacing slide transitions with cross-fades; suppressing parallax) work for users who experience motion sickness or vestibular sensitivity. Web equivalent: `prefers-reduced-motion` media query.

Apple's discipline is most visible in how persistent navigation animates: the sliding push, the navigation bar's title cross-fading, the sheet's drag-to-dismiss. These are useful references even for non-Apple platforms.

## Disney's twelve principles applied to UI

Disney animators codified twelve principles in *The Illusion of Life* (Thomas & Johnston, 1981). Not all apply to UI, but several are foundational:

1. **Squash and stretch.** Elements deform during fast motion to convey weight. UI application: subtle scale-down during button press; momentary scale-up during item appearance.
2. **Anticipation.** A small reverse-motion before the main action ("wind-up"). UI application: a button settling slightly before launching its target action.
3. **Staging.** Directing attention to the relevant element. UI application: dimming surrounding content when a modal opens; isolating the focus area.
4. **Slow-in and slow-out.** Motion accelerates then decelerates rather than running at constant speed. The fundamental easing principle; embedded in every UI easing curve.
5. **Arcs.** Natural motion follows arcs, not straight lines. UI application: subtle curve in the path of dragged items.
6. **Secondary action.** Supporting motion that reinforces the main action. UI application: when a card flips, the shadow shifts in tandem.
7. **Timing.** Faster motion = lighter; slower motion = heavier. The duration scale (above) embeds this.
8. **Exaggeration.** Push expressive motion further than physics for clarity. UI application: subtle bouncing on a notification badge to draw attention.
9. **Solid drawing.** Elements have weight and form. UI application: elevation tokens (shadows; layered surfaces) express depth.
10. **Appeal.** The animation is pleasant to watch. UI application: avoid jerky transitions; avoid distracting durations (too short = startling; too long = annoying).

(Principles 11 — "follow through and overlapping action" — and 12 — "straight ahead vs pose to pose" — are more relevant to character animation than UI.)

## Easing curves with semantic names

CSS supports cubic-bezier custom curves and several named keywords (`linear`, `ease`, `ease-in`, `ease-out`, `ease-in-out`). The default `ease` is acceptable for most cases but lacks intent. A semantic naming pattern:

```css
:root {
  /* Entering — starts off-screen / scaled-down; decelerates as it settles */
  --ease-enter: cubic-bezier(0.05, 0.7, 0.1, 1);

  /* Exiting — starts visible; accelerates off-screen */
  --ease-exit: cubic-bezier(0.3, 0, 0.8, 0.15);

  /* Emphasized — balanced curve drawing attention to destination */
  --ease-emphasized: cubic-bezier(0.2, 0, 0, 1);

  /* Smooth — symmetric ease-in-out for in-place transitions */
  --ease-smooth: cubic-bezier(0.4, 0, 0.6, 1);
}
```

The semantic names map to use cases: `--ease-enter` for elements appearing; `--ease-exit` for elements disappearing; `--ease-emphasized` for state changes that draw attention; `--ease-smooth` for in-place transformations (rotation; color shift).

## Duration scales

The Material 3 scale (above) covers the full range. A simpler 4-step scale works for many projects:

```css
:root {
  --duration-fast: 100ms;    /* small acknowledgments */
  --duration-base: 200ms;    /* default for most transitions */
  --duration-slow: 350ms;    /* larger transitions; modals */
  --duration-stately: 500ms; /* full-screen; complex */
}
```

Durations under 100ms feel instantaneous; durations over 500ms feel slow. The 100-500ms range is the sweet spot for UI motion.

Long durations (>500ms) are appropriate for unusual moments — first-time onboarding animations; deliberate "wow" moments — but should be the exception.

## `prefers-reduced-motion`

`@media (prefers-reduced-motion: reduce)` queries the user's OS-level reduce-motion preference. The discipline:

- **Don't disable motion entirely.** Cross-fades and opacity changes are usually fine; what users with vestibular sensitivities object to is *translation* motion (sliding; scrolling parallax; bouncing).
- **Replace translations with fades or instant changes.** A modal that slides up becomes a modal that fades in.
- **Reduce durations across the board.** If you keep some motion, make it shorter (50-100ms range).

```css
.modal {
  animation: slide-up 300ms var(--ease-enter);
}

@media (prefers-reduced-motion: reduce) {
  .modal {
    animation: fade-in 100ms ease;
  }
}
```

Note: `prefers-reduced-motion` is a USER preference, not an a11y compliance checkbox. Some users without diagnosed conditions simply prefer reduced motion. Respect it as a first-class accommodation.

## Patterns and anti-patterns

**Pattern: state-driven motion via CSS transitions.** Mount components in their final state; let CSS transitions animate property changes. Easier to reason about than imperative animation; respects `prefers-reduced-motion` if the transition is declared inside the media query.

**Pattern: motion explains causality.** Modal opens from the button that opened it; menu appears from its trigger; sheet slides from its edge.

**Pattern: spring physics for natural motion.** When CSS transitions feel too mechanical, spring-based animations (React Spring; Framer Motion; CSS scroll-driven animations with timeline) feel more organic. Use sparingly; springs are computationally heavier and harder to reason about.

**Anti-pattern: motion as decoration.** Pulse animations on icons with no semantic meaning; gradient sheens sliding across buttons; particles. Costs attention; provides no information; aggravates motion-sensitive users.

**Anti-pattern: ignoring `prefers-reduced-motion`.** Every motion in the project should either respect the preference or have a documented exception.

**Anti-pattern: bouncy easing on routine transitions.** Bounce/overshoot easing is appropriate for moments of emphasis; routine usage (every modal opens with a bounce) becomes exhausting.

**Anti-pattern: durations >500ms on routine transitions.** Slow transitions add up. The user clicks a button, waits 600ms for the modal, fills the form, dismisses the modal (600ms), and has spent 1.2 seconds just watching animations. Multiply across a session.

**Anti-pattern: parallax in product UIs.** Scroll-linked parallax is a marketing-page pattern. Product UIs that adopt it confuse spatial reasoning (the scroll position no longer maps to content position) and aggravate motion sensitivity.

## Cross-references

- **Visual choices motion is applied to:** see `type-color-space.md`.
- **Responsive behavior and motion interaction:** see `responsive.md`.
- **Material 3 motion documentation:** `m3.material.io/styles/motion/overview`.
- **Apple HIG motion section:** `developer.apple.com/design/human-interface-guidelines/motion`.
- **MDN `prefers-reduced-motion`:** `developer.mozilla.org/en-US/docs/Web/CSS/@media/prefers-reduced-motion`.
- **Disney's twelve principles (foundational):** Thomas, Frank and Johnston, Ollie. *The Illusion of Life: Disney Animation*. 1981.
