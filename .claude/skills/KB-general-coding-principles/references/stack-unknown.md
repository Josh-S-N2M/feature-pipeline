# Stack-Unknown Samples

## Contents

- When this applies
- The pattern
- What the rubric does with stack-unknown samples
- Anti-patterns specific to stack-unknown
- Crossover with ADR rationale

When the per-layer designer runs and the layer's concrete stack is genuinely undetermined (greenfield path, multi-language project where this section spans both, or an architectural decision that has not yet been made), the sample must be authored so it does not appear to pick a stack it hasn't.

## When this applies

- Greenfield sections of an otherwise-existing codebase (e.g. adding a frontend to a backend-only project)
- Multi-stack monorepos where a layer's specific stack depends on which sub-package the feature lives in
- Architectural decisions deferred by an ADR (e.g. ADR says "language choice TBD at integration time")

Does NOT apply when the stack is merely "not obvious" — that's the codebase researcher's failure, not a stack-unknown case. If the stack should be discoverable, escalate the gap to discovery rather than emit a stack-unknown sample.

## The pattern

```pseudo
# Layer: Backend
# Stack: TBD pending ADR-NNNN decision; this sample illustrates the contract
# in pseudocode. Final implementation may be Python/FastAPI, Go/chi, or Rust/axum.

function processOrder(input: OrderInput) -> Result<Order, ProcessError>:
    validated = validate(input)        # synchronous; raises on invalid
    persisted = orderRepo.create(validated)
    eventBus.publish("order.created", persisted)
    return Ok(persisted)
```

Key elements:
- Fence language is `pseudo` or the most-likely-final language with a comment
- First two comments make it explicit that this is stack-unknown
- Names use camelCase or whatever feels neutral; the prose doesn't claim a stack
- No library-specific calls; only language-neutral concepts (function, repository, event bus)

## What the rubric does with stack-unknown samples

- **Dimension 4 (fabricated API):** skip — no APIs are claimed. Auto-passes.
- **Dimension 9 (language matches project):** skip — the sample's own comment declares the divergence. Auto-passes.
- **All other dimensions:** apply normally. Types still need to be stated (1), error contract still needs to be visible (3), idempotency still needs a posture (7), etc.

## Anti-patterns specific to stack-unknown

- **Implying a stack via library names** — `import { useState } from 'react'` claims React; that's not stack-unknown anymore. If using React, dimension 9 applies fully.
- **Pseudocode that hides design questions** — pseudocode is for stack ambiguity, not design ambiguity. A pseudocode sample whose business logic itself is hand-wavy fails dimension 1 (names match contract — but there is no contract).
- **Too many "TBD"s** — if more than half the sample is placeholders, it's not a sample; it's an outline. Move the outline to prose.

## Crossover with ADR rationale

A stack-unknown sample in a Design section often signals an open architectural question. The right move is usually:

1. Surface the question as an entry in the Blueprint's "Undetermined Items" section.
2. Pre-author an ADR stub (`Proposed`) capturing the decision needed.
3. The composer during Design Composition decides whether to resolve the stub before publishing or to ship the Blueprint with the stub referenced.

This keeps stack-unknown samples from accumulating across documents.
