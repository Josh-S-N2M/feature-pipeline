---
name: kb-query-design
description: >-
  Design discipline for the Query layer — the data-access surface between
  Backend services and the Database. Covers query construction (raw SQL vs.
  ORM vs. query builder), caching strategy, N+1 prevention, projection control,
  read/write split, materialized views, and the per-layer designer's workflow
  for producing the Query Design subsection of a Blueprint. Use when the
  feature touches how data is fetched. Pairs with KB-backend-design (the
  consumer) and KB-database-design (the underlying storage).
allowed-tools: Read, Grep, Glob
---

# KB-query-design — Query Layer Design Discipline

Design discipline for the Query layer. The per-layer Query Designer (`design-query`) loads this KB during per-layer Design to produce the `### Query Design` subsection of the Blueprint. This layer sits between Backend (which asks "give me this data") and Database (which stores rows); the Query layer decides how the question becomes SQL (or document queries, or whatever the storage speaks).

## Contents

- When this KB is loaded
- The layer's responsibility
- Design decisions this layer owns
- Patterns and anti-patterns at a glance
- Interaction with other layers
- Surfacing architectural questions
- When to load each reference file

## When this KB is loaded

This KB is in scope when:

- A feature's PRD or Blueprint declares the **Query** layer in scope (per `layer-taxonomy.md` in KB-documentation-criteria)
- A per-layer Designer is producing the Query Design subsection of the Blueprint
- Plan Authoring produces tasks that touch data-access code, ORMs, query builders, or caching layers
- `shared-document-reviewer` or `review-architecture-auditor` is auditing artifacts that include Query Design

Sub-agents that reference this KB (per Blueprint v4.3.1):

- `design-query` (per-layer Design, when Query layer is in scope)
- `design-composer` (Design Composition, integrating Query design with cross-cutting concerns)
- `plan-author` (when tasks touch data-access code)
- `shared-document-reviewer` (Gate 1 Query-specific checks)
- `review-architecture-auditor` (CoVe checks on Query claims)

## The layer's responsibility

The Query layer translates "the Backend needs this data" into "concrete database queries." It owns:

- **Query construction.** How requests for data become SQL (or NoSQL queries, or graph traversals, or whatever the storage speaks).
- **N+1 prevention.** When a single logical operation accidentally becomes many database round-trips.
- **Caching.** Where data is cached, how it's invalidated, what the staleness contract is.
- **Projection control.** What columns / fields are returned for which use case. Over-fetching costs latency and memory.
- **Read/write split.** Whether reads go to replicas; how the application chooses primary vs. replica per request.
- **Read-model materialization.** When and how to maintain pre-computed views of expensive aggregations.

The Query layer does NOT own:

- The schema — that belongs to the Database layer (`KB-database-design`). The Query layer reads the schema; it doesn't define it.
- The domain rules — that belongs to the Backend (`KB-backend-design`). The Query layer fetches data; the Backend decides what to do with it.
- The transaction boundary — the Backend defines the transaction scope; the Query layer participates within it.

## Design decisions this layer owns

The Query Designer makes (or surfaces) these decisions:

| Decision | Forced if … |
|---|---|
| Access style (raw SQL, query builder, ORM, embedded query language) | Greenfield; brownfield usually inherits |
| Repository granularity (per-aggregate, per-use-case, generic) | The codebase has more than ~5 aggregates |
| N+1 prevention strategy (eager loading, dataloader, joins, projection objects) | Any list endpoint with relationships |
| Caching layer (none, in-process, distributed, write-through, read-through) | Read-heavy traffic or expensive queries |
| Cache invalidation strategy (TTL, event-driven, write-through, versioned keys) | A caching layer exists |
| Read/write split (none, opt-in per query, by default with primary on session start) | Replicas are deployed and replication lag is acceptable |
| Read models / materialized views (none, ad-hoc, fully materialized read side) | Read patterns diverge significantly from write patterns |
| Pagination implementation (offset, keyset, cursor) | Listing queries exist |
| Bulk operations strategy (per-row, batch, COPY/MERGE/UPSERT) | Bulk inserts or updates anticipated |
| Query timeouts and statement-level retries | Long-running queries are possible |

Designers do NOT author ADRs (per FR-5). Cross-cutting decisions (canonical caching policy, repository pattern across the codebase) get surfaced as open items.

## Patterns and anti-patterns at a glance

The full discipline lives in `references/principles.md` and `references/patterns-and-anti-patterns.md`. Quick reference:

**Patterns to favor:**

- **Eager-load by intent, not by reflex.** The Query Designer specifies for each list endpoint which relationships are loaded together (joined or batched). Lazy loading is a default that hides N+1 problems.
- **Dataloader / batch-and-cache.** For GraphQL or any per-item resolution, dataloader batches calls into a single query per tick and dedupes within a request.
- **Projection objects.** A query returns only the columns the caller needs, not `SELECT *`. Reduces transfer, parsing, and memory cost.
- **Keyset (cursor) pagination over offset.** Stable under concurrent writes; consistent performance.
- **Cache keys include all query parameters that affect the result.** Including auth context if results vary by actor.
- **TTL + explicit invalidation.** Even with event-driven invalidation, a TTL is the safety net.
- **Read-after-write goes to primary.** If the caller just wrote, the immediate read goes to primary, not a replica.
- **Statement-level timeouts on every query.** Don't let a runaway query block a connection indefinitely.

**Anti-patterns to flag:**

- **N+1 query patterns.** A loop that fetches one row per iteration.
- **`SELECT *` in production code.** Couples the query result to the schema; breaks when columns are added or removed.
- **Cache populated from one place, invalidated from another.** Almost guarantees drift.
- **Cache-aside without TTL.** Stale data lingers when invalidation logic has bugs.
- **Joining 8 tables to render a list page.** Often a sign the schema isn't shaped for this access pattern; consider a read model.
- **ORM lazy loading triggering queries in template/view rendering.** Where the Backend thinks "the data is here" but each `.field` accessor triggers a query.

## Interaction with other layers

```
Backend ──► [Query layer] ──► Database
                │
                ├──► Cache (in-process / Redis / Memcached)
                ├──► Read replicas (for read traffic)
                └──► Materialized view tables / external read stores
```

The Query Designer's responsibility:

- **Backend (consumer)** — the Query layer's interface (`OrderRepository.findByCustomerWithLineItems`) is what the Backend codes against. The Designer documents that interface in the per-layer subsection.
- **Database (storage)** — the Query layer is the only code that should talk to the Database directly. Direct Database access from Backend or API code is a smell.
- **Cache** — caches are the Query layer's responsibility. The Backend doesn't know whether a result came from cache or the source.
- **Read replicas** — same: the Query layer routes; the Backend just asks.

## Surfacing architectural questions

```markdown
## Architectural Questions for Composer

- **Q-QY-1**: Should we adopt a system-wide caching layer (Redis), or per-service in-process LRU caches? The choice affects deployment topology (new component vs. zero), invalidation discipline (cross-process events vs. local-only), and cost. Evidence: 3 services have hot reads with >100rps; current p95 latency is dominated by DB time. Options: (a) shared Redis with key namespacing; (b) per-service in-process LRU; (c) no caching for now, scale DB. Recommended: (a). Defer to composer.
```

## When to load each reference file

| Load this file | When the task involves |
|---|---|
| `references/principles.md` | Authoring or reviewing a Query Design subsection — covers the foundational principles (N+1 prevention, projection control, cache discipline, read/write split, query timeouts) |
| `references/patterns-and-anti-patterns.md` | Choosing between ORM / query builder / raw SQL approaches, picking caching and pagination strategies — covers common patterns with when-to-use and the anti-patterns reviewers should flag |
