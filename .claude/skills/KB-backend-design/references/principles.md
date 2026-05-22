# Backend Design Principles

The foundational principles a Backend Designer applies when authoring the `### Backend Design` subsection of the Blueprint.

## Contents

- Principle 1: Bounded contexts and module boundaries
- Principle 2: Hexagonal architecture (ports and adapters)
- Principle 3: Idempotency by default
- Principle 4: Errors as first-class citizens
- Principle 5: Transactions: scope to the data store, not the request
- Principle 6: Observability is part of the design, not bolted on
- Principle 7: Concurrency model declared explicitly
- Principle 8: External calls are timeouts + retries + circuit breakers

## Principle 1: Bounded contexts and module boundaries

A **bounded context** is a region of the system where domain terms have unambiguous meaning. The Backend Designer identifies the bounded contexts the feature touches and respects their boundaries.

Inside a bounded context: free to share types, services, and data structures.
Between bounded contexts: communicate via well-defined contracts (event, API call, message), not by sharing types.

Concretely, when designing a new feature:

- Identify the bounded context(s) the feature lives in.
- If the feature spans multiple contexts, document the cross-context interactions (which context owns what; how they synchronize).
- Module / package layout (whether the codebase is a monolith, modular monolith, or microservices) should reflect the bounded-context graph.

Anti-pattern: features that ignore context boundaries. Example: `OrderService` directly reads from the `users` table to get a billing address. Better: `OrderService` calls `UsersContext.getBillingAddress(userId)` — even if it's an in-process call, the boundary is named and can be moved to a remote call later.

## Principle 2: Hexagonal architecture (ports and adapters)

Hexagonal architecture separates the domain (the core, where business rules live) from the adapters (HTTP handlers, database access, message consumers, external API clients). The domain defines **ports** (interfaces); the adapters implement them.

```
            [HTTP adapter]    [Message-bus adapter]
                  │                    │
                  ▼                    ▼
            ┌────────────────────────────┐
            │       Domain core          │
            │   (use cases, aggregates,  │
            │     domain services)       │
            └────────────────────────────┘
                  ▲                    ▲
                  │                    │
            [Repository port]    [HTTP client port]
                  │                    │
            ┌─────┴────┐       ┌───────┴────────┐
            │  Postgres │       │  External API   │
            │  adapter  │       │  adapter        │
            └──────────┘       └────────────────┘
```

Why this matters:

- The domain is testable in isolation. Replace adapters with in-memory fakes; the domain logic runs without a DB, network, or queue.
- Adapter swaps don't require domain changes. Switching from Postgres to MongoDB, or from REST to gRPC, doesn't touch domain code.
- External-service contracts are owned by the domain (the port), not dictated by the external system. The adapter translates.

The Backend Designer documents the ports and adapters in the per-layer Design subsection. For a small feature, the layout might be implicit (one module, one adapter each direction). For a larger feature, the boundary is explicit.

## Principle 3: Idempotency by default

A mutation is **idempotent** if applying it twice has the same effect as applying it once. Idempotency lets clients (and load balancers, retry layers, and queue consumers) retry safely.

The Backend Designer specifies the idempotency strategy for every mutating endpoint:

| Strategy | When to use |
|---|---|
| **Natural idempotency** | The mutation's effect is already idempotent: setting a status, updating a field to a specific value. |
| **Idempotency key (header)** | The mutation creates or modifies a resource and the client supplies a unique key. The server stores `(key, result)` for the retention window and short-circuits duplicates. |
| **Conditional update (If-Match / version)** | The mutation requires the resource to be in a specific state; concurrent edits return 412/409. |
| **Tombstones** | Hard deletes leave a record marking the deletion; replays don't recreate the resource. |
| **Outbox + dedup downstream** | Async event emissions are deduplicated by the consumer using a stable event ID. |

For non-idempotent mutations (the rare case: e.g., "transfer $X with a side effect that must happen exactly once"), the Backend Designer documents the rationale and the compensating mechanism (saga, two-phase commit, manual reconciliation).

Acceptance Criteria for idempotency become EARS-format ACs:

- When the client retries a POST `/orders` with the same `Idempotency-Key` header within 24h, the system shall return the original response without creating a duplicate order.
- If the client sends a PUT `/orders/{id}/status` with a status value that already matches the current status, then the system shall return 200 OK without recording a state change.

## Principle 4: Errors as first-class citizens

Errors are not exceptions to deal with reluctantly — they are part of the contract. The Backend Designer documents the error model:

| Element | Decision |
|---|---|
| Error categories | Validation / NotFound / Conflict / Unauthorized / Forbidden / Unavailable / Internal — minimum set; pick a finite list |
| Error envelope | Either RFC 7807 Problem Details, or a custom envelope with the same fields (code, message, retriable, details). Document the choice. |
| Retriability | Each error carries `retriable: bool` (or implicit-by-category). Clients use this to drive retry behavior. |
| Logging | Errors logged with category, request context (request ID, user ID), and exception type. Application errors at WARN; system errors at ERROR; expected validation failures at INFO or DEBUG. |
| Metrics | Counter by category; histogram of error rate per endpoint per minute. |
| Tracing | Errors annotate the trace span with `error: true` and the category. |

Anti-patterns:

- **Generic 500 with "Something went wrong."** Tells the caller nothing. Always categorize.
- **Stack traces in the response body.** Information disclosure; only return error codes and human-readable summaries.
- **Returning success when the operation partially failed.** Either the operation succeeded fully or it failed; partial states need explicit modeling.

## Principle 5: Transactions: scope to the data store, not the request

A single database transaction is the simplest atomic boundary. The Backend Designer's first instinct should be: keep the operation within one DB transaction.

When the operation spans multiple data stores or external services, transactions are NOT the right tool:

- **Distributed transactions / two-phase commit** — rarely the right answer; operational fragility, deadlock risk, performance cliff.
- **Saga pattern** — sequence of local transactions, each with a compensating action. Used for long-running multi-service flows.
- **Outbox pattern** — write to the DB and write the event-to-emit to an outbox table in the same DB transaction; a separate publisher reads the outbox and emits to the queue. Solves the "DB-and-event must happen together" problem.

The Backend Designer specifies:

- What's atomic (one DB transaction).
- What's eventually consistent (cross-store, eventually reconciled).
- How the eventually-consistent path detects and recovers from failure.

Anti-pattern: a "transaction" that wraps an HTTP call to a remote system. The remote call may succeed; the local DB may fail to commit; now the systems are out of sync. Move external calls outside the transaction; use the outbox pattern to make them transactionally tied.

## Principle 6: Observability is part of the design, not bolted on

Observability has three pillars: **logs** (events), **metrics** (aggregates), **traces** (causal chains). The Backend Designer specifies all three at design time, not after the service is in production.

For each new endpoint or background worker:

- **Logs.** What gets logged. At what severity. What context is included (request ID, user ID, correlation ID). Never log credentials, PII, or tokens.
- **Metrics.** Request count, error count by category, latency histogram (p50/p95/p99). Custom domain metrics if applicable (e.g., orders per hour).
- **Traces.** Span boundaries (one per request, one per external call, one per significant operation). Trace context propagated to downstream services.

The Backend Designer specifies the observability commitments as Acceptance Criteria:

- The system shall log every state-changing operation with `request_id`, `user_id`, `operation_type`, `outcome`, and `duration_ms`.
- The system shall emit a `requests_total{endpoint, status_code}` counter for every HTTP request.
- The system shall propagate the W3C `traceparent` header to all downstream calls.

## Principle 7: Concurrency model declared explicitly

Concurrency choices have cascading consequences. The Backend Designer declares:

- **Per-request execution model.** One thread per request (Java/Kotlin/.NET classic), event loop (Node, Python async), green threads (Go, Erlang/Elixir), structured concurrency (modern Java/Kotlin/Python). The choice constrains library selection and blocking-call discipline.
- **Background work model.** Synchronous (in the request), in-process worker pool, separate worker process consuming a queue, cron-driven, schedule-driven. Each has different operational characteristics.
- **State-sharing strategy across requests.** Stateless (preferred), per-request cache (acceptable for hot data), shared mutable state (rare; document the locking model).

Anti-pattern: using a blocking library on an event loop (or vice versa). The mismatch starves the runtime. Document the blocking-call discipline for the chosen runtime.

## Principle 8: External calls are timeouts + retries + circuit breakers

Every call to an external service (HTTP, gRPC, database, queue, third-party API) is a failure point. The Backend Designer specifies, for each external dependency:

- **Timeout.** A connection timeout AND a request timeout. Default `requests.get(url)` without a timeout will block forever; that's a service outage waiting to happen.
- **Retry policy.** How many attempts. With what backoff (exponential with jitter is the default). What error categories retry (network errors yes, 4xx no, 5xx case-by-case).
- **Circuit breaker.** After N failures in a window, fail fast for a cool-down period instead of hammering the failing service.
- **Fallback.** What does the service do when the dependency is unavailable? Return a degraded response? Cached value? Queue for later? Hard fail?
- **Dependency budget.** What's the latency budget for this dependency call? If the overall endpoint's SLO is 200ms p95 and this dependency typically takes 80ms, the rest of the request has 120ms to do everything else.

The Backend Designer documents these in the per-layer Design subsection's "External Dependencies" table:

| Dependency | Timeout | Retries | Circuit breaker | Fallback |
|---|---|---|---|---|
| `auth.example.com/validate` | 200ms / 500ms | 2x exponential, jitter | After 5 fails in 10s, open 30s | Reject (401) |
| `mailer.internal/send` | 1s / 5s | 3x, then enqueue | After 10 fails in 60s, open 5min | Enqueue to retry-later topic |
| `payments.stripe.com` | 1s / 10s | None (idempotency key required) | None (Stripe handles its own) | Surface 503; client retries with backoff |

This level of specificity at design time saves the team from production incidents that come from "we forgot to set a timeout."
