# Query Layer Design Principles

## Contents

- Principle 1: Eager-load by intent, not by reflex
- Principle 2: Projections, not `SELECT *`
- Principle 3: Cache discipline: keys, TTL, invalidation
- Principle 4: Read/write split with explicit primary-routing
- Principle 5: Statement-level timeouts on every query
- Principle 6: Bulk operations beat per-row loops
- Principle 7: Repository is an interface, not a base class
- Principle 8: Read models when reads diverge from writes

## Principle 1: Eager-load by intent, not by reflex

ORMs default to lazy loading: accessing a relationship triggers a query. This produces the N+1 pattern almost by accident:

```python
# Looks innocent. Runs 1 + N queries: 1 for orders, N for each order's customer.
orders = Order.objects.all()
for order in orders:
    print(order.customer.name)
```

The fix is to specify the loading shape:

```python
# 1 query with a JOIN
orders = Order.objects.select_related('customer').all()
```

Or batch-load with a dataloader:

```python
# 1 query for orders + 1 query for all customers
orders = Order.objects.all()
customer_ids = [o.customer_id for o in orders]
customers = {c.id: c for c in Customer.objects.filter(id__in=customer_ids)}
```

The Query Designer specifies, for each list operation, the explicit loading shape — what's joined, what's batched, what's lazy. Documenting this in the per-layer Design subsection's "Query Plans" section prevents N+1 from being introduced later.

## Principle 2: Projections, not `SELECT *`

`SELECT *` fetches every column, even ones the caller doesn't need. For wide tables (TEXT columns, JSONB blobs, computed columns), this is wasteful and couples the query to the schema (adding a column changes every consumer).

Projections fix both:

```sql
SELECT id, status, total
FROM orders
WHERE customer_id = $1 AND created_at > $2
```

The Query Designer documents the projection for each query — what columns are returned for what use case. Different consumers of the same table get different projections; that's fine.

For ORMs that support it:

```python
# Only fetches the listed columns
Order.objects.filter(customer_id=cid).only('id', 'status', 'total')
```

For GraphQL, the projection is implicit in the query — but the Query layer's resolver should translate it into a precise SQL projection, not load everything.

## Principle 3: Cache discipline: keys, TTL, invalidation

Caching is the source of more "works on my machine" bugs than almost anything else. The Query Designer specifies, for each cache:

- **Key shape.** Every parameter that affects the result is in the key. Including authorization context if the same query returns different data per actor.
- **Value shape.** What's stored. Whether it's serialized JSON, MessagePack, application objects, or raw rows.
- **TTL.** Maximum staleness. Use a TTL even with event-driven invalidation, as the safety net.
- **Invalidation triggers.** Write through? Write-around with explicit invalidation? Event-driven? The Designer documents every write path and the corresponding cache-update path.
- **Negative caching.** Whether "not found" is cached (it should be, with a short TTL, to absorb stampedes).
- **Cache stampede prevention.** When the cache expires and 1000 requests race to repopulate, do they all hit the DB? Use single-flight (one request rebuilds; others wait) or probabilistic early refresh.

Acceptance Criteria for caching become EARS-format ACs:

- When the `GET /products/{id}` cache entry is present and not expired, the system shall return the cached value without consulting the Database.
- When the `PUT /products/{id}` mutation succeeds, the system shall invalidate the `products:{id}` cache entry before returning.
- While the `products:{id}` cache entry is stale (past TTL), the system shall refetch on next access and store the fresh value.

## Principle 4: Read/write split with explicit primary-routing

When read replicas exist, the default is: writes go to primary; reads go to a replica. But replication is asynchronous; reads may see slightly stale data.

Two failure modes:

1. **Read-after-write inconsistency.** User saves a profile change; immediately reloads; sees old value because the replica hasn't caught up.
2. **Transaction inconsistency.** Within a transaction, switching from primary to replica mid-transaction is incoherent.

The Query Designer's discipline:

- **Within a transaction: primary only.** Don't route reads inside a transaction to replicas.
- **Read-after-write: primary for a window.** After a write from the same session/user/request, subsequent reads go to primary for N seconds (or until session ends).
- **Explicit hint in the API.** Backend code can request primary explicitly for cases where freshness matters: `repository.find(..., read_preference=PRIMARY)`.

The Query Designer documents the routing policy in the per-layer subsection. "Read replicas exist; reads default to replica; the following situations route to primary instead: ..."

## Principle 5: Statement-level timeouts on every query

A query without a timeout is an outage waiting to happen. One slow query holds a connection; the connection pool exhausts; the service stops serving traffic.

The Query Designer specifies, for each query class:

- **Per-statement timeout.** In Postgres: `SET LOCAL statement_timeout = '500ms';`. In application code: connection-level timeout, statement-level timeout, or both.
- **Per-connection timeout.** Connection-pool checkout timeout, idle-in-transaction timeout.
- **Per-query category.** Interactive queries (user-facing) get short timeouts (~500ms-1s). Background queries (reports, exports) get longer timeouts but separate connection pools so they don't compete with interactive traffic.

Document the timeouts:

| Query class | Timeout | Pool |
|---|---|---|
| Interactive read | 500ms | primary-interactive (size 50) |
| Interactive write | 1s | primary-interactive |
| Background read (report) | 30s | replica-background (size 5) |
| Background bulk import | 5min | primary-batch (size 2) |

## Principle 6: Bulk operations beat per-row loops

When the Backend needs to write 1000 records, the Query layer should expose a bulk operation, not a single-row interface that the Backend calls 1000 times.

Per-row insert: 1000 round-trips × ~1ms each = 1 second of network + 1000 transaction commits.
Bulk insert: 1 round-trip, 1 transaction = ~50ms total.

The same applies to updates and deletes. For relational DBs:

- `INSERT INTO ... VALUES (...), (...), (...)` for batches.
- `COPY ... FROM STDIN` for very large inserts (Postgres).
- `UPDATE ... FROM (VALUES ...)` for batch updates.
- `DELETE FROM ... WHERE id IN (...)` for batch deletes.

The Query Designer exposes bulk operations in the repository interface where the use case calls for them. Anti-pattern: a `repository.save(record)` that gets called in a loop.

## Principle 7: Repository is an interface, not a base class

Some ORMs encourage "extend `BaseRepository` and get 30 methods for free." Most of those methods will be unused or misused. The Designer favors:

- Repository interfaces designed per use case (or per aggregate). Methods reflect the application's actual queries, not "every possible query you might want."
- Implementation hidden behind the interface. The Backend doesn't know whether the repository uses SQL, an ORM, a document store, or a cache.
- Specification or query-object pattern for complex queries, instead of a sprawling method-per-shape API.

```python
class OrderRepository(Protocol):
    def find_by_id(self, order_id: OrderId) -> Order | None: ...
    def find_pending_for_customer(self, customer_id: CustomerId) -> list[Order]: ...
    def save(self, order: Order) -> None: ...
    def find_by(self, spec: OrderSpecification) -> list[Order]: ...
```

The Designer keeps the interface narrow and growth deliberate.

## Principle 8: Read models when reads diverge from writes

When the read pattern differs fundamentally from the write pattern (e.g., writes are normalized OLTP; reads are dashboard aggregates), the Designer considers a separate read model:

- **Materialized views.** A view computed from the source tables, refreshed on a schedule or on write. The query against the view is fast; staleness is bounded by refresh interval.
- **Read-side projections (CQRS).** Write side produces events; a read-side projector consumes events and updates denormalized read tables.
- **Search index.** Reads against Elasticsearch/OpenSearch/etc. for full-text and faceted search; writes update the index asynchronously.
- **Analytical store.** Reads against a column-store (BigQuery, Snowflake, Redshift) for analytics; OLTP for transactional reads.

Each adds operational complexity. The Designer documents:

- The trigger for adopting a read model (the query patterns that justify it).
- The staleness contract (how stale can the read model be?).
- The catch-up mechanism after a failure (rebuild from source? replay events?).

Without these, the read model becomes a permanent source of consistency bugs.
