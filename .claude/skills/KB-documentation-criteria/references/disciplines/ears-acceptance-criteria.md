# EARS Acceptance Criteria Authoring

The discipline for authoring acceptance criteria in EARS (Easy Approach to Requirements Syntax) format. Per ADR-0015, EARS is the canonical AC format across the feature-pipeline.

## Contents

- Why EARS
- The five canonical patterns
- Choosing which pattern fits
- Common mistakes
- AC ID convention
- Layer organization
- Cross-layer and operational ACs
- Testability check
- AC count and granularity
- Interaction with the templates

## Why EARS

Pre-EARS AC authoring tended toward two failure modes: ambiguous prose ("the system should handle errors gracefully") and contractual templating with unclear triggers ("Given X, When Y, Then Z" used inconsistently). Neither scales to AI-driven authoring or AI-driven testing.

EARS solves both:

- Five canonical patterns, each unambiguous about WHEN the assertion applies.
- The word **shall** marks every assertion as binding.
- Triggers are explicit and testable.
- An AI author can pattern-match the five forms; an AI tester can map each form to a test type.

## The five canonical patterns

### Pattern 1: Event-driven (When)

```
When <event>, the system shall <expected behavior>
```

Use when behavior is triggered by a discrete event — user action, scheduled tick, message arrival, API call.

**Examples:**

- When the user clicks the Submit button with a valid form, the system shall persist the form data and display the success state.
- When a `payment.captured` event arrives on the webhook endpoint, the system shall record the payment in the ledger and emit a `payment.confirmed` event downstream.
- When the cron tick fires at 03:00 UTC, the system shall run the daily reconciliation job.

**Test type:** event-driven test (trigger the event; assert the outcome).

### Pattern 2: State-driven (While)

```
While <state>, the system shall <expected behavior>
```

Use when behavior holds continuously during a state — a flag is set, a session is active, a timer is running.

**Examples:**

- While the user is logged in, the system shall maintain the session for the configured timeout period (default 30 minutes idle).
- While a deployment is in progress, the system shall not accept new deployment requests for the same environment.
- While the feature flag `experimental-search` is enabled, the system shall route search queries through the new ranking service.

**Test type:** state-condition test (set the state; assert the invariant holds; transition out; assert the behavior ceases).

### Pattern 3: Optional feature (Where)

```
Where <option/configuration/feature flag>, the system shall <expected behavior>
```

Use when behavior is conditional on a configuration or feature being enabled. Differs from "While" in that "Where" applies for the lifetime of the configuration, not transiently.

**Examples:**

- Where the project has SSO configured, the system shall use the SSO provider for authentication instead of the local password store.
- Where the deployment target is a region with data-residency restrictions, the system shall route all user data through that region's database.

**Test type:** feature-toggle test (enable; verify behavior; disable; verify default behavior).

### Pattern 4: Unwanted behavior (If-Then)

```
If <unwanted event/condition>, then the system shall <recovery or rejection action>
```

Use for handling unwanted, exceptional, or error conditions. The two-keyword form (`If`/`then`) distinguishes from event-driven "When" — "If" implies an exceptional path, "When" implies an expected path.

**Examples:**

- If credentials are invalid, then the system shall return HTTP 401 with the error body `{"error": "invalid_credentials"}` and shall not include a session token.
- If the Terraform plan shows destructive changes to stateful resources, then the system shall block apply pending manual approval.
- If a Codespace creation exceeds the configured timeout, then the system shall surface a clear error to the user and shall not leave a partial environment.

**Test type:** branch coverage test (trigger the exceptional condition; assert the recovery/rejection behavior).

### Pattern 5: Ubiquitous (no keyword)

```
The system shall <expected behavior>
```

Use for invariant behavior that holds at all times. No trigger, no state, no condition — just "this is always true."

**Examples:**

- The system shall log every state-changing operation with the actor, target entity, and operation type.
- The system shall not store passwords in plaintext.
- The system shall display a pagination control on any list view with more than 10 items.

**Test type:** basic functionality test (assert the invariant in any context where the assertion applies).

## Choosing which pattern fits

Most ACs fit naturally into one pattern. The decision tree:

1. **Does it describe what happens at all times?** → Ubiquitous (Pattern 5)
2. **Does it describe what happens on an exceptional condition or error?** → If-then (Pattern 4)
3. **Does it describe what happens during the lifetime of a configuration?** → Where (Pattern 3)
4. **Does it describe what holds continuously during a transient state?** → While (Pattern 2)
5. **Does it describe what happens when a discrete event fires?** → When (Pattern 1)

When two patterns seem to fit equally, prefer the more specific one. "When the user logs in, the system shall maintain the session" is poorly chosen — the maintaining isn't a one-shot event. Better: "While the user is logged in, the system shall maintain the session for the configured timeout period."

## Common mistakes

### Mistake 1: Missing "shall"

```
When the user clicks Submit, the system should validate the form.
```

`should` is non-binding. EARS uses `shall` for binding assertions. `should` is acceptable only in non-normative guidance — never in an AC.

### Mistake 2: Vague trigger

```
When errors occur, the system shall handle them.
```

What error? What does "handle" mean? Both are unanswered. Test author has nothing concrete to test. Fix: name the specific error class and the specific action.

```
If the database connection fails, then the system shall retry up to 3 times with exponential backoff before surfacing an error to the caller.
```

### Mistake 3: Mixing patterns in one AC

```
When the user is logged in, while their session is active, the system shall ...
```

This conflates Pattern 1 (event) and Pattern 2 (state). Split into two:

```
When the user logs in, the system shall create a session and start the idle timer.
While the user's session is active, the system shall accept authenticated requests.
```

### Mistake 4: Implementation in the AC

```
When the user submits the form, the system shall call `OrderService.create()` and write to the `orders` table.
```

ACs describe observable behavior, not implementation. Method names and table names are HOW; ACs are WHAT. Fix:

```
When the user submits a valid order form, the system shall create a new order and confirm to the user that the order was received.
```

### Mistake 5: Multiple assertions hiding in one AC

```
When the user submits the form, the system shall validate it, persist it, send a confirmation email, and log the operation.
```

Four behaviors in one AC. Each may pass or fail independently. Split:

```
When the user submits a valid form, the system shall persist the form data.
When the user submits a valid form, the system shall send a confirmation email to the form's primary contact.
When the user submits a form (valid or invalid), the system shall log the operation with the actor, timestamp, and outcome.
```

### Mistake 6: Future-tense or aspirational language

```
The system will eventually scale to handle 10,000 requests per second.
```

ACs assert verifiable behavior, not aspirations. Either the behavior is required now (and verifiable) or it doesn't belong in this PRD/Blueprint. Fix: state the actual current requirement and the conditions.

```
The system shall handle 1,000 requests per second sustained on a 2-vCPU instance with p95 latency under 200ms.
```

## AC ID convention

ACs get stable IDs of the form `AC-FR-<requirement-id>-<letter>`:

- `AC-FR-1-a` — the first AC for Functional Requirement 1
- `AC-FR-1-b` — the second AC for FR-1
- `AC-FR-2-a` — the first AC for FR-2
- `AC-NFR-3-a` — for non-functional requirements

Cross-layer or operational ACs use `AC-XL-N-letter` (cross-layer) or `AC-OP-N-letter` (operational).

IDs are stable across versions. If an AC is rephrased without changing meaning, the ID stays. If an AC is split into multiple, the original ID is retired and new IDs are minted.

## Layer organization

When a feature spans multiple layers (per the 9-layer taxonomy in `../layer-taxonomy.md`), group ACs by layer:

```markdown
### Functional ACs

#### FR-1: User can submit a feedback form — Layer: Frontend, Backend, API, Database

- [ ] AC-FR-1-a (Frontend): When the user clicks the Submit button with a valid form, the frontend shall display the submitting state until the API responds.
- [ ] AC-FR-1-b (API): When a valid POST /feedback request arrives, the API shall return HTTP 201 with the new feedback ID.
- [ ] AC-FR-1-c (Backend): When the feedback API endpoint is invoked, the backend shall validate the payload against the schema and reject invalid input with HTTP 422.
- [ ] AC-FR-1-d (Database): When a feedback record is created, the database shall enforce the uniqueness constraint on (user_id, submission_token).
```

Grouping by layer makes coverage gaps visible (a layer with no AC for a feature that spans it) and makes per-layer designers' work scope explicit.

## Cross-layer and operational ACs

Not every AC sits in one layer. Cross-cutting concerns get their own section:

```markdown
### Cross-Layer / Operational ACs

- [ ] AC-OP-1: When the migration runs on a production-sized dataset, the system shall complete within 10 minutes and produce zero data loss.
- [ ] AC-OP-2: When the deploy workflow runs on `main`, the system shall promote the image to staging and run smoke tests before promoting to production.
- [ ] AC-XL-1: If the Terraform plan shows destructive changes to stateful resources, then the system shall block apply pending manual approval.
```

## Testability check

Every AC should pass the "what would I test?" check. Read the AC and immediately know:

- What's the precondition / setup?
- What's the trigger (event, state, condition, or "any time")?
- What's the assertion?
- What's the boundary (timeout, rate, exact value)?

If any of those four are unclear, the AC needs revision. Fuzzy ACs ("the system shall be performant") fail this test.

## AC count and granularity

A typical FR has 1–5 ACs. More than 5 usually indicates:

- The FR itself is too coarse (split it into multiple FRs)
- ACs are too granular (combine related assertions)

Less than 1 (i.e., zero ACs for an FR) is a `critical` completeness issue at Gate 0.

For NFRs, AC count is similar. An NFR like "Performance: p95 latency under 200ms" might have one AC ("The system shall return responses with p95 latency under 200ms under a sustained load of 1,000 rps") or several ACs covering different operations.

## Interaction with the templates

PRD template (`../templates/prd-template.md`) and Blueprint template (`../templates/blueprint-template.md`) both have ACs sections in EARS format. The discipline above applies identically to both.

The PRD's ACs are derived from User Stories. The Blueprint's ACs are derived from the PRD's ACs (with layer-specific refinement). Cross-document AC consistency is checked by `review-cross-artifact-auditor` during the Cross-Artifact Audit pass — see `cross-artifact-audit.md` in KB-review-disciplines.

## Authoring discipline summary

For every AC the author emits:

1. Pick the EARS pattern that fits (1 of 5).
2. Trigger is explicit and unambiguous.
3. Action uses `shall` (not should/may/will).
4. Assertion is observable and testable.
5. ID assigned per the AC-FR-N-letter convention.
6. Group by layer when feature spans multiple layers.
7. Pass the "what would I test?" check.

If any of those is missing, revise before emitting.
