# Query Patterns and Anti-Patterns

## Contents

- Access-style patterns
- N+1 prevention patterns
- Caching patterns
- Pagination patterns
- Read-model patterns
- Bulk-operation patterns
- Anti-patterns reviewers should flag
- Decision frames

## Access-style patterns

### Raw SQL

**Pattern.** Hand-written SQL strings (often parameterized) in the application.

**When to use.** Performance-critical paths. Complex queries the ORM can't express cleanly. Reporting and analytics.

**Strengths.** Full control over the SQL plan; no ORM overhead; the SQL in the code is the SQL the DB runs.

**Weaknesses.** No compile-time safety unless wrapped (e.g., sqlc, sqlx, Diesel for type-safe SQL). Repetition across the codebase.

### Query builder

**Pattern.** A fluent API constructs SQL programmatically: `db.select(...).from_('orders').where(...).limit(50)`.

**When to use.** When queries are parameterized along multiple axes (dynamic filters, sort orders). When type-safety matters but full ORM is too heavy.

**Strengths.** Type-safe at compile time (in typed languages). Composable. Closer to the SQL than an ORM.

**Examples.** Kysely (TypeScript), SQLAlchemy Core (Python), JOOQ (Java), Diesel (Rust).

### ORM (object-relational mapper)

**Pattern.** Domain objects map to DB rows; relationships expressed as navigable references.

**When to use.** CRUD-heavy applications with conventional access patterns. Rapid prototyping.

**Strengths.** Convenient. Migrations integrated. Standard patterns for common operations.

**Weaknesses.** N+1 is the default; performance reasoning gets harder; complex queries hit the ORM's edges.

**Examples.** Django ORM, ActiveRecord, Hibernate, Entity Framework, SQLAlchemy ORM, Prisma.

### Embedded query language

**Pattern.** Queries expressed in a DSL or compiled form: GraphQL on the wire compiled to SQL; LINQ in C#; HQL/JPQL in JVM.

**When to use.** When the consumer-facing query language differs from the storage language.

## N+1 prevention patterns

### Eager loading via `JOIN`

```sql
SELECT o.id, o.status, c.id AS customer_id, c.name AS customer_name
FROM orders o
JOIN customers c ON c.id = o.customer_id
WHERE o.created_at > $1
```

**When to use.** One-to-one or many-to-one relationships. Few related rows.

**Risk.** With many-to-many or one-to-many joins, the result set grows multiplicatively (1 order × 5 items × 3 payments = 15 rows). Use the next pattern instead.

### Batch loading (separate queries, single round-trip per relationship)

```python
orders = repo.find_orders(...)  # 1 query
customer_ids = list({o.customer_id for o in orders})
customers = repo.find_customers_by_ids(customer_ids)  # 1 query
# Stitch in Python
```

**When to use.** One-to-many or many-to-many relationships. Multiple relationships per entity.

**Trade-off.** N+1 becomes 1 + 1 + 1 + ... (one query per relationship instead of per row).

### DataLoader

**Pattern.** A per-request loader batches calls within a single event-loop tick and dedupes.

```typescript
const customerLoader = new DataLoader(async (ids) => {
  const customers = await db.customers.findByIds(ids);
  return ids.map(id => customers.find(c => c.id === id));
});

// In resolvers, just call:
await customerLoader.load(order.customer_id);
// DataLoader batches across all resolver calls in the same tick.
```

**When to use.** GraphQL resolvers. Per-item lookups inside loops. Any code path with structurally similar repeated fetches.

### Subquery / lateral / window functions

**Pattern.** Use SQL features to compute related data in one query.

```sql
-- Top 5 items per order in one query (window function)
SELECT * FROM (
  SELECT o.*, oi.*, ROW_NUMBER() OVER (PARTITION BY o.id ORDER BY oi.priority DESC) AS rn
  FROM orders o
  JOIN order_items oi ON oi.order_id = o.id
) WHERE rn <= 5
```

**When to use.** Per-group operations: top-N-per-group, running totals, ranks.

## Caching patterns

### Cache-aside (lazy)

**Pattern.** Read: check cache → miss → fetch from DB → populate cache → return. Write: update DB → invalidate cache.

**When to use.** Read-heavy workloads. Default starting point.

**Risk.** Race on write: process A writes DB then invalidates cache; process B reads (miss), fetches stale value, populates cache after A's invalidation. Mitigation: short TTL as safety net; version-stamped cache keys.

### Write-through

**Pattern.** Write: update DB and cache in the same operation. Read: cache (always hot for written keys).

**When to use.** When the write path knows exactly what shape will be read back. Predictable hot keys.

**Risk.** Tight coupling between write code and cache structure.

### Write-around

**Pattern.** Write: update DB only (don't populate cache). Read: cache-aside.

**When to use.** Write-once, read-many — but the write is unlikely to be immediately followed by reads.

**Risk.** First read after write is always a cache miss.

### Read-through

**Pattern.** The cache itself fetches from the DB on miss. Application sees only the cache.

**When to use.** When a managed cache (Redis modules, application-level cache library) supports it. Abstracts the cache miss handling.

### TTL-only (no explicit invalidation)

**Pattern.** Cache for a fixed window; let staleness be bounded by TTL.

**When to use.** Reference data with low write rate. Tolerable staleness (catalog, configuration).

### Refresh-ahead / probabilistic early refresh

**Pattern.** Before TTL expires, the cache asynchronously refetches.

**When to use.** Hot keys where a miss would cause a stampede.

## Pagination patterns

### Cursor (keyset) pagination

```sql
SELECT * FROM orders
WHERE (created_at, id) < ($cursor_created_at, $cursor_id)
ORDER BY created_at DESC, id DESC
LIMIT 50
```

**When to use.** Default for unbounded lists. Stable under inserts. Consistent performance regardless of page depth.

**Requires.** Stable ordering criterion. Index on the ordering columns.

### Offset pagination

```sql
SELECT * FROM orders ORDER BY created_at DESC LIMIT 50 OFFSET 200
```

**When to use.** Bounded lists where page count matters (UI shows "page 5 of 23").

**Risk.** Performance degrades with offset (the DB must scan and discard `offset` rows). Skipped / duplicated items under concurrent writes.

### Seek with composite key

For ordering by a non-unique column, the cursor uses (sort_column, primary_key):

```sql
ORDER BY created_at DESC, id DESC
```

This ensures stable ordering even when many rows share `created_at`.

## Read-model patterns

### Materialized view

**Pattern.** A view computed from base tables, persisted in the DB, refreshed on a schedule or trigger.

**When to use.** Read query is expensive (joins, aggregations); read frequency >> refresh need.

**Refresh strategies.**

- Full refresh on schedule: simple; staleness bounded by interval.
- Incremental refresh on write: complex; minimizes staleness.
- Lazy refresh on read: refresh-on-demand if older than threshold.

### Read-side projection (CQRS)

**Pattern.** Write side emits domain events; read side consumes events and updates denormalized read tables.

**When to use.** Write model and read model differ structurally. Eventual consistency on the read side is acceptable.

**Catch-up.** When the read store is rebuilt, replay events from the start (event-sourced) or seed from the source then process new events.

### Search index

**Pattern.** Writes go to the OLTP DB; an async pipeline updates a search index (Elasticsearch, OpenSearch, Meilisearch); reads for search go to the index.

**When to use.** Full-text search, faceted search, fuzzy matching.

**Discipline.** The pipeline must be idempotent (re-indexable from source). Document the index schema and the source-of-truth row → indexed-document mapping.

## Bulk-operation patterns

### Batched inserts

```sql
INSERT INTO events (ts, event_type, payload) VALUES
  ($1, $2, $3),
  ($4, $5, $6),
  ...
```

**When to use.** N > ~10. Single transaction wraps the batch.

### COPY / bulk-load

```sql
COPY events (ts, event_type, payload) FROM STDIN WITH (FORMAT csv)
```

**When to use.** N > ~10,000. Initial loads, backfills.

### Bulk upsert (MERGE / INSERT ... ON CONFLICT)

```sql
INSERT INTO products (sku, price, stock) VALUES (...)
ON CONFLICT (sku) DO UPDATE
  SET price = EXCLUDED.price, stock = EXCLUDED.stock
```

**When to use.** Sync from external source where rows may or may not exist.

### Chunked iteration for huge updates

```python
while True:
    rows_updated = db.execute("""
        UPDATE huge_table SET status = 'archived'
        WHERE id IN (
          SELECT id FROM huge_table WHERE status = 'pending' AND created_at < $1
          LIMIT 10000
        )
    """, cutoff_date)
    if rows_updated < 10000:
        break
```

**When to use.** Updating millions of rows. Avoids long-held locks and unmanageable transactions.

## Anti-patterns reviewers should flag

| Anti-pattern | Why it's bad | Typical fix |
|---|---|---|
| N+1 in loop | Per-row round-trips destroy latency | Eager load, batch load, or dataloader |
| `SELECT *` | Couples query to schema; over-fetches | Explicit projection |
| Cache populated by one place, invalidated by another | Drift inevitable | Centralize invalidation; use TTL safety net |
| Cache key missing a parameter that affects the result | Wrong results returned | Audit cache keys; include every result-affecting input |
| Offset pagination on a frequently-written list | Skipped / duplicated items under concurrent writes | Cursor pagination |
| `LIMIT 1000000` to "just get them all" | Memory blow-up; lock contention | Pagination or streaming |
| ORM lazy load in view template | Hidden queries; debug nightmare | Eager-load in the controller; assert in tests |
| Per-row insert in a loop | 1000× round-trip cost | Bulk insert |
| Query without statement timeout | Slow query holds connection forever | Statement-level timeout, per query class |
| Read replica in a write transaction | Mixed primary/replica; inconsistent | Reads in a write transaction go to primary |
| Read-after-write hitting replica | User sees stale data | Route subsequent reads to primary for a window |
| Cache stampede on TTL expiry | Thundering herd hits DB | Single-flight or probabilistic early refresh |
| Database connection pool sized = request thread count | Pool exhaustion under spikes | Pool sized for typical load + headroom; separate pools per query class |
| Single transaction for "create order + send email + charge card" | External calls inside transaction | Outbox pattern; commit DB, then publish event |
| Migration that adds NOT NULL without default + backfill | Production downtime | Add nullable; backfill; tighten constraint |
| Index added without `CONCURRENTLY` in production | Table lock; downtime | `CREATE INDEX CONCURRENTLY` (Postgres) or equivalent |
| Materialized view never refreshed | Stale data | Refresh strategy documented and tested |
| Cache eviction policy unspecified | Memory grows unbounded or wrong things evicted | LRU / LFU / FIFO documented; size cap set |
| `SELECT FOR UPDATE` without a `LIMIT` | Locks a large range | Add `LIMIT`; consider advisory locks |

## Decision frames

When the Query Designer faces a choice:

1. **What's the access pattern?** Point lookup, range scan, aggregation, full-text. Each calls for different storage / index / cache shape.
2. **What's the read/write ratio?** Heavy read favors caching and replicas; heavy write favors avoiding write-amplification (write-through cache, eager invalidation across many keys).
3. **What's the consistency requirement?** Strong consistency narrows the cache + replica options; eventual consistency widens them.
4. **What's the budget?** Latency budget per query; connection pool size; memory for caches.
5. **What's the cardinality?** Tables with 10M+ rows need indexed predicates; indexing wrong gets you sequential scans regardless of `WHERE`.

The Designer documents the argument and the resulting plan in the per-layer Design subsection.
