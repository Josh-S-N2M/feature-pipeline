# Backend Patterns and Anti-Patterns

Patterns the Backend Designer favors, anti-patterns to flag, and decision frames for choosing among them.

## Contents

- Service-granularity patterns
- Persistence patterns
- Transaction and consistency patterns
- Domain modeling patterns
- Cross-cutting patterns
- Anti-patterns reviewers should flag
- Decision frames

## Service-granularity patterns

### Monolith

**Pattern.** Single deployable unit; all bounded contexts in one process.

**When to use.** Early-stage product (team < 8). Team independence not yet required. Operational simplicity matters more than team scalability.

**Risks.** Module boundaries blur over time; reorganization is harder than choosing well up front. Mitigate by enforcing bounded-context boundaries within the monolith (import rules, linting).

### Modular monolith

**Pattern.** One deployable unit, but modules respect bounded-context boundaries. Inter-module communication is explicit (in-process method calls through defined interfaces).

**When to use.** Team 8–30. Looking to extract services later. Want monolith operational simplicity now and the option to split later.

**Risks.** Slightly more upfront design effort. Boundaries can still erode if not enforced.

### Microservices

**Pattern.** Each bounded context (or smaller) is its own deployable, each owning its data store.

**When to use.** Team 30+. Independent deploys matter (compliance, scale, team autonomy). Polyglot persistence or runtime is necessary.

**Risks.** Operational overhead (service mesh, distributed tracing, deployment coordination). Latency from inter-service calls. Distributed-system failure modes.

The Backend Designer's default: start with modular monolith. Extract services only when the friction of NOT extracting exceeds the cost of extracting. Premature microservices is a documented anti-pattern.

## Persistence patterns

### Repository

**Pattern.** Domain interacts with a Repository interface (`findById`, `save`, `delete`). The adapter implementation contains the SQL / ORM / NoSQL specifics.

**When to use.** Default for any non-trivial domain. Keeps domain code free of persistence concerns.

**Anti-pattern.** Repository that exposes "all the queries" (`findByEmail`, `findActiveUsersInRegionXWithSubscriptionY`). The interface grows unboundedly. Two reasonable patterns to bound the growth:

- **Specification pattern.** Repository takes a `Specification<T>` object; domain composes specifications.
- **CQRS read models.** Reads bypass the repository entirely; writes go through the repository. (See "Transaction and consistency patterns" below.)

### Unit of Work

**Pattern.** A scope that aggregates all repository operations into a single atomic commit at scope end.

**When to use.** When the framework or language doesn't make transactions explicit, OR when the operation touches multiple repositories that must commit atomically.

**Example.** SQLAlchemy session, Hibernate session, .NET `DbContext`.

### Active Record

**Pattern.** Domain objects expose their own persistence: `user.save()`, `user.delete()`.

**When to use.** Small apps; rapid prototyping. Frameworks like Rails default to this.

**Risks.** Couples domain to persistence; harder to test domain logic in isolation. Generally inferior to repository for non-trivial domains.

### CQRS (Command Query Responsibility Segregation)

**Pattern.** Writes (commands) go through one model; reads (queries) go through a different, often materialized, model.

**When to use.** Read patterns diverge significantly from write patterns (e.g., complex analytics over a transactional store). When eventual consistency on the read side is acceptable.

**Risks.** Two models to keep in sync; staleness on the read side.

## Transaction and consistency patterns

### Single DB transaction

**Pattern.** Wrap the work in `BEGIN ... COMMIT`. All-or-nothing.

**When to use.** All work touches one DB. Default choice when applicable.

### Saga

**Pattern.** Sequence of local transactions across services, each with a compensating action that undoes its effect.

**When to use.** Long-running flow across services where a single DB transaction is impossible.

**Variants.**

- **Orchestrated saga.** A central coordinator calls each service and handles compensations.
- **Choreographed saga.** Each service listens for events and reacts; no central coordinator.

**Risks.** Compensations rarely undo perfectly (email sent, money moved). Document what each compensation actually does.

### Outbox

**Pattern.** In the same DB transaction that updates the domain state, write the event-to-emit to an `outbox` table. A separate publisher reads from outbox and emits to the queue (with at-least-once delivery and an idempotency key).

**When to use.** Any "update DB and emit event atomically" scenario. The most reliable way to avoid the dual-write problem.

### Two-phase commit (2PC)

**Pattern.** Coordinator asks every participant to prepare; if all prepared, commit; if any rejected, abort.

**When to use.** Rarely. Most distributed systems avoid 2PC because of operational fragility and performance cost. The exception is when participants are within a single distributed-transaction-capable platform (e.g., XA-aware databases in a tightly controlled environment).

### Read-after-write consistency

**Pattern.** After a write, the writer reads from the primary (not a replica) to guarantee they see their own write.

**When to use.** Replicas exist and replication lag is non-zero. Without this, the user submits an update and the next read shows the old value because the replica hasn't caught up.

## Domain modeling patterns

### Anemic data model + service layer

**Pattern.** Domain objects are bags of fields with no behavior; services contain all logic.

**When to use.** Genuinely simple domains. Stateless transformations. CRUD-like services.

**Risks.** As domains grow, logic scatters across many services. Hard to find "where does this rule live?"

### Rich domain objects

**Pattern.** Domain objects own their behavior. `order.cancel()` validates state, transitions, emits events. Services orchestrate across multiple objects.

**When to use.** Domain has invariants worth enforcing in one place. Logic is complex enough that scattering it across services would create bugs.

**Risks.** Requires more upfront modeling. Methods on domain objects can balloon if not split into aggregate boundaries.

### Aggregates

**Pattern.** Cluster of domain objects with a single root entity. The root enforces invariants over the cluster; external code only references the root.

**When to use.** Domain has invariants spanning multiple objects (`Order` + `OrderLine` + `OrderPayment` all evolve together).

**Risks.** Aggregate boundaries matter. Too-large aggregates lock too much (contention). Too-small aggregates leak invariants across boundaries.

### Event sourcing

**Pattern.** Persist the sequence of events, not the current state. The current state is a projection (left fold) of events.

**When to use.** Audit-by-construction is required. Temporal queries ("what was the state at time T") are first-class. Event-driven downstream systems.

**Risks.** Schema evolution is hard (events from years ago must still replay correctly). Projections must be kept current. Operational complexity higher than CRUD.

## Cross-cutting patterns

### Idempotency-key middleware

**Pattern.** A middleware reads `Idempotency-Key` header, checks a key→response store, short-circuits duplicates.

**Storage.** Redis or DB table with TTL (24h–7d typical).

**Document.** What gets cached (request + response or just response), what counts as "same request" (key alone, or key + request body hash), retention.

### Outbox-with-debezium

**Pattern.** Outbox table; Debezium (or equivalent CDC tool) tails the WAL and emits to Kafka.

**When to use.** Already running Kafka + CDC infrastructure. Want truly at-least-once event emission tied to DB commits.

### Feature flags at the Backend layer

**Pattern.** Backend reads feature flags from a flag service (LaunchDarkly, Unleash, self-hosted) and varies behavior per request.

**Design points.**

- Flag evaluation should be local (cached) to avoid per-request external calls.
- Default-off for new code paths; default-on once stable.
- Flag cleanup discipline (stale flags get deleted; the codebase doesn't accumulate dead branches indefinitely).

## Anti-patterns reviewers should flag

| Anti-pattern | Why it's bad | Typical fix |
|---|---|---|
| God service | Couples bounded contexts; deployment risk; team contention | Decompose by bounded context |
| Direct ORM access from domain code | Couples domain to persistence; can't test in isolation | Repository pattern; hexagonal architecture |
| External call inside a DB transaction | Holds locks while waiting for remote system; deadlock-prone; partial-failure-prone | Move external call outside; use outbox if event-emission must be atomic |
| `except Exception: pass` | Swallows real failures | Catch specific exceptions; log + rethrow or handle explicitly |
| `if user.is_admin or user.is_superuser or user.is_owner or ...` everywhere | Authorization logic scattered | Centralize in a policy / authorization module |
| Mutating endpoints without idempotency | Duplicate side effects on retry | Idempotency key, natural keys, or tombstones |
| Sync HTTP call to "fire and forget" | Caller blocks; failure of receiver propagates back; misuse of HTTP | Queue / event bus |
| Background worker that crashes loses work | Single-execution semantics; no recovery | Durable queue; explicit retries; dead-letter handling |
| Polling for state change | High load, high latency, racy | Webhook or event-driven |
| `time.sleep(60)` in production code | Blocks a worker; usually papering over a race | Proper waiting primitive (queue subscription, event, retry-with-backoff) |
| Single transaction wrapping everything | Lock contention; long transactions; deadlock risk | Scope transactions narrowly; commit early when work doesn't need atomicity |
| Error message that includes a stack trace in HTTP response | Information disclosure | Log the trace; return only category + message |
| Logging at ERROR for "user supplied bad input" | Alert fatigue | INFO/WARN for user errors; ERROR for system failures |
| Unbounded `LIMIT`-less queries | Memory exhaustion on large tables | Explicit `LIMIT`; pagination |
| Hardcoded timeout = 30s | Calling service exhausts its budget waiting | Per-dependency timeout + retry + circuit breaker |
| Catch-all `try` wrapping the whole handler | Hides where failures actually occurred | Targeted catches with categorized handling |
| Domain logic in HTTP handlers | Untestable; couples transport to domain | Push logic to domain; handlers translate transport ↔ domain |
| Mixed unit-of-work scopes (some operations commit, others stay open) | Inconsistent atomicity | One unit of work per use case |
| `assert` for production validation | Strippable with `-O`; bypassable | `if not valid: raise ValidationError(...)` |

## Decision frames

When the Backend Designer faces a choice (service boundary, persistence, transaction strategy, error model), apply this frame:

1. **What's the bounded context?** The boundary often dictates the answer (don't reach across).
2. **What's the failure mode?** Designs that look identical at the happy path differ wildly under failure.
3. **What's the load shape?** Read-heavy vs. write-heavy. Burst vs. steady. Per-request latency budget.
4. **What's the consistency requirement?** Strong consistency narrows options dramatically; eventual consistency widens them.
5. **What's the operational maturity?** A two-phase commit needs deep ops capability. A modular monolith needs less.

The Designer documents the argument — not just the conclusion — in the per-layer Design subsection's "Rationale" portion.
