# Database Patterns and Anti-Patterns

## Contents

- Schema patterns (normalization, denormalization, polymorphism, JSONB)
- Indexing patterns
- Migration patterns
- Multi-tenancy patterns
- Partitioning patterns
- Constraint patterns
- Anti-patterns reviewers should flag
- Decision frames

## Schema patterns

### Normalization (3NF as default)

**Pattern.** Each fact stored once. Tables normalized to Third Normal Form: no repeating groups, no partial-key dependencies, no transitive dependencies.

**When to use.** Default. Transactional systems where the cost of updating duplicated data exceeds the cost of joins.

**Strengths.** Updates touch one row; no consistency drift between copies; smaller storage; constraints enforceable.

**Weaknesses.** Read-heavy queries join across many tables; deep joins can be slow without good indexes.

### Denormalization for read performance

**Pattern.** Duplicate selected columns into a table to avoid joins on hot read paths.

**Examples.**

- `orders.customer_name` cached from `customers.name` so the order list doesn't join `customers`.
- A precomputed `daily_aggregates` table that summarizes raw event rows.
- Materialized views (Postgres `CREATE MATERIALIZED VIEW`) refreshed on schedule.

**When to use.** Read pattern dominates; the join cost is measurable; the data being denormalized changes infrequently or staleness is acceptable.

**Discipline.** Document the source of truth and the propagation mechanism (trigger? application code? scheduled refresh?). Without this, the denormalized copy drifts and bugs follow.

### Polymorphic association (avoid)

**Pattern.** A child table references multiple possible parent types via `(parent_type, parent_id)` columns.

```
comments
  id, parent_type, parent_id, body
  (parent_type IN ('post', 'photo', 'video'))
```

**When to avoid.** Default. Foreign keys can't enforce the reference (no FK to "post OR photo OR video"); queries become complex; constraint drift inevitable.

**Better.** Per-parent-type child tables (`post_comments`, `photo_comments`, `video_comments`), or a comment table with a single foreign key to a unified `commentables` parent.

### JSONB / document columns

**Pattern.** Store semi-structured data as a JSON column (Postgres JSONB, MySQL JSON, etc.).

**When to use.**

- Attributes that vary per row and don't need to be queried frequently.
- External-system payloads stored verbatim for audit.
- Schema-flexible parts of an otherwise structured model.

**When not.**

- Anything queried frequently (JSON indexes are coarse compared to column indexes).
- Anything with cross-row invariants (constraints don't apply inside JSON).
- Anything that should obey schema migration discipline (JSON skirts schema migrations, which is the wrong kind of "flexibility").

**Discipline.** When using JSONB, document the JSON schema in the per-layer subsection. Implicit schemas drift; explicit ones can be migrated.

### Event tables (append-only)

**Pattern.** A table that receives only INSERTs, never UPDATE or DELETE. Each row is an immutable event.

**When to use.** Audit logs, event sourcing, time-series data, analytics ingestion.

**Discipline.**

- No `updated_at` (the row never changes; `created_at` only).
- Index on `(aggregate_id, sequence)` if event-sourced; `(timestamp)` if time-series.
- Partitioning by time becomes natural at scale.

## Indexing patterns

### B-tree (default)

Standard index supporting equality, range, prefix scans on most data types. The default for almost everything.

### Composite (multi-column)

```sql
CREATE INDEX idx_orders_customer_created ON orders (customer_id, created_at DESC);
```

Serves queries that:

- Filter by `customer_id` alone.
- Filter by `customer_id` and `created_at`.
- Filter by `customer_id` and sort by `created_at`.

Does NOT serve queries that filter only by `created_at` (leading column missing).

The column order matters: put equality filters first, then range filters, then sort columns.

### Partial index (Postgres)

```sql
CREATE INDEX idx_orders_pending ON orders (created_at) WHERE status = 'pending';
```

**When to use.** A small fraction of rows match the predicate. Hot queries always include the predicate.

**Strengths.** Much smaller than a full index; faster to maintain; the planner uses it when the WHERE clause matches.

### Expression index

```sql
CREATE INDEX idx_users_email_lower ON users (lower(email));
```

**When to use.** Queries filter by a computed value (lowercase, substring, function of a column).

**Discipline.** The query must use the same expression: `WHERE lower(email) = $1`, not `WHERE email = $1`.

### Covering index (Postgres `INCLUDE`)

```sql
CREATE INDEX idx_orders_customer_covering ON orders (customer_id) INCLUDE (status, total);
```

Lets the planner serve `SELECT status, total FROM orders WHERE customer_id = ?` entirely from the index (no table lookup).

**When to use.** Hot read path with a stable projection.

### GIN / GiST

For JSONB, array, full-text search, geometric data, ranges:

```sql
CREATE INDEX idx_documents_tags_gin ON documents USING GIN (tags);  -- array contains
CREATE INDEX idx_events_payload_gin ON events USING GIN (payload jsonb_path_ops);
```

**When to use.** Containment queries (`tags @> ARRAY['urgent']`), JSONB path queries, full-text.

### BRIN

For large tables where data has natural physical ordering correlated with a column (timestamp, sequence ID).

**When to use.** Time-series tables with billions of rows. BRIN indexes are tiny.

## Migration patterns

### Expand-then-contract (default)

For any change in a live system, the migration runs in stages, each safe to roll back:

1. **Expand.** Add the new shape (column, table, index) alongside the old.
2. **Dual-write.** Application writes to both.
3. **Backfill.** Populate the new shape from the old in batches.
4. **Switch reads.** Application reads from new shape.
5. **Contract.** Remove the old shape.

Between each step, the system is in a valid state and rollback is the reverse of the previous step.

### Backfill in batches

```python
last_id = 0
batch_size = 10000

while True:
    rows = db.execute("""
        UPDATE orders
        SET customer_name = c.name
        FROM customers c
        WHERE orders.customer_id = c.id
          AND orders.id > $1
          AND orders.customer_name IS NULL
        LIMIT $2
        RETURNING orders.id
    """, last_id, batch_size)

    if not rows:
        break
    last_id = max(r['id'] for r in rows)
    time.sleep(0.1)  # throttle
```

**Discipline.** Batch size keeps locks short. Throttling prevents replica lag. Idempotency (the WHERE filter checks "not yet backfilled") allows safe restart.

### `CREATE INDEX CONCURRENTLY` (Postgres)

```sql
CREATE INDEX CONCURRENTLY idx_orders_created ON orders (created_at);
```

Doesn't lock the table for writes. Slower to build than `CREATE INDEX`. Required for production tables.

If the operation fails mid-flight, the index is left in an invalid state. The Designer documents the recovery: `DROP INDEX CONCURRENTLY IF EXISTS idx_orders_created;` then retry.

### Dual-write during rename

```python
class Order:
    def save(self):
        # Old column still exists; new column also exists
        self.customer_email = self.customer_contact  # write to both
        self.customer_contact = self.customer_contact
        super().save()
```

The application writes to both; reads from new with fallback to old. After backfill completes and a deploy switches reads to new-only, the old column can be dropped.

## Multi-tenancy patterns

### Shared schema, tenant column

```sql
CREATE TABLE orders (
  id BIGSERIAL PRIMARY KEY,
  tenant_id UUID NOT NULL REFERENCES tenants(id),
  ...
);
CREATE INDEX idx_orders_tenant ON orders (tenant_id);
```

Every query filters by `tenant_id`. Row-level security (Postgres RLS) can enforce.

**When to use.** Many tenants (1000+); per-tenant data is small.

**Risks.** Missing tenant filter leaks data across tenants. Indexes must lead with `tenant_id` (or be partitioned).

### Schema-per-tenant

Each tenant gets their own DB schema (`tenant_alice.orders`, `tenant_bob.orders`).

**When to use.** Medium tenant count (10-1000); per-tenant customization (different columns per tenant).

**Risks.** Migrations replay across many schemas; schema drift if migrations fail partway.

### Database-per-tenant

Each tenant gets a separate database instance.

**When to use.** Large enterprise tenants; strict data-isolation requirements; per-tenant scaling.

**Risks.** Operational complexity; provisioning new tenants is heavyweight; migration runs become long.

## Partitioning patterns

### Range partitioning by time

```sql
CREATE TABLE events (
  ts TIMESTAMPTZ NOT NULL,
  ...
) PARTITION BY RANGE (ts);

CREATE TABLE events_2026_01 PARTITION OF events FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');
```

**When to use.** Time-series data; old partitions can be archived or dropped.

**Strengths.** Drop a partition in seconds (vs. `DELETE` taking hours). Queries filtered by time scan only relevant partitions.

### List partitioning by category

```sql
CREATE TABLE orders (
  region TEXT NOT NULL,
  ...
) PARTITION BY LIST (region);

CREATE TABLE orders_us PARTITION OF orders FOR VALUES IN ('us');
CREATE TABLE orders_eu PARTITION OF orders FOR VALUES IN ('eu');
```

**When to use.** Strong data-residency requirements; per-region operations.

### Hash partitioning

```sql
CREATE TABLE orders (...) PARTITION BY HASH (customer_id);
```

**When to use.** Uniform distribution; no natural range or list key.

## Constraint patterns

### CHECK constraint

```sql
ALTER TABLE orders ADD CONSTRAINT orders_status_valid
  CHECK (status IN ('draft', 'pending', 'approved', 'fulfilled', 'cancelled'));

ALTER TABLE orders ADD CONSTRAINT orders_total_nonneg
  CHECK (total >= 0);
```

**When to use.** Any rule expressible as a per-row predicate.

### Exclusion constraint (Postgres)

```sql
ALTER TABLE meeting_rooms ADD CONSTRAINT no_overlap
  EXCLUDE USING GIST (room_id WITH =, time_range WITH &&);
```

**When to use.** Non-overlap rules (booking systems, version-effective-date ranges).

### Deferred constraints

```sql
ALTER TABLE ... DEFERRABLE INITIALLY DEFERRED;
```

Constraint checked at transaction commit, not per-statement.

**When to use.** Circular foreign keys; complex multi-row updates.

**Risk.** Hides constraint violations until commit, which is harder to debug.

## Anti-patterns reviewers should flag

| Anti-pattern | Why it's bad | Typical fix |
|---|---|---|
| `timestamp` without time zone in Postgres | Implicit timezone; bugs depend on server config | `timestamptz` always |
| Floats for money | Rounding errors; audit failures | `NUMERIC(19,4)` or integer cents |
| Adding NOT NULL without default + backfill | Table-locking migration; downtime | Add nullable, backfill, tighten |
| `ALTER TABLE` without `CONCURRENTLY` (where applicable) | Table-level lock; production stall | `CONCURRENTLY` for indexes and similar |
| Foreign-key column without an index | Slow joins, slow DELETE on parent | Index the FK column |
| Schema without NOT NULL on required fields | Bad rows slip in | NOT NULL everywhere that "absent" is meaningless |
| Schema without UNIQUE on natural keys | Duplicate domain entities | UNIQUE constraint (with partial index if soft-deleted rows allowed) |
| Schema without FK constraint between related tables | Orphan rows accumulate | DB-level FK with explicit ON DELETE |
| Exposing autoincrement IDs externally | Enumeration; information leak | Opaque ID (ULID / UUIDv7) for external use |
| Soft-delete without partial unique constraint | Old "deleted" rows block new entries with same natural key | `UNIQUE ... WHERE deleted_at IS NULL` |
| Soft-delete column without an index | Every query filters; planner blind | Index on `deleted_at` (partial: `WHERE deleted_at IS NULL`) |
| Polymorphic association (parent_type + parent_id) | FK can't enforce; constraints drift | Per-parent-type table, or a unified parent table |
| JSONB columns for frequently-queried data | Slow without coarse indexes; no per-field constraints | Promote to real columns |
| Schema-less storage as a habit | Implicit schema drift | Define and enforce schema; migrate when it changes |
| Long-running transactions | Lock contention; deadlocks; replication lag | Short transactions; commit early |
| Cascading deletes on critical data | One bad mutation deletes a tree | `ON DELETE RESTRICT` for important relationships; explicit deletion logic |
| Indexes on every column "just in case" | Storage and write cost; planner confusion | Index for actual queries |
| Triggers for business logic | Hidden side effects; hard to test | Application logic; triggers only for invariants (e.g., `updated_at`) |
| Single huge migration script for many changes | All-or-nothing fail; hard to debug | One change per migration file |
| Migration that depends on a specific replica state | Race conditions; non-deterministic | Migrations idempotent and standalone |
| Direct DB access from production code outside the Query layer | Bypasses caching, instrumentation, observability | Repository pattern; all access through Query layer |

## Decision frames

When the Database Designer faces a choice:

1. **What are the read/write patterns?** OLTP (small reads/writes, high concurrency) vs. OLAP (large scans, low concurrency) vs. mixed.
2. **What's the consistency requirement?** Strong consistency narrows engine choices; eventual is broader.
3. **What's the size?** GB-scale is one problem; TB and PB are different problems with different solutions (partitioning, sharding, dedicated analytical stores).
4. **What's the team's ops capacity?** Postgres-self-hosted requires more ops than RDS; RDS requires more than DynamoDB managed; serverless requires the least.
5. **What's the change cadence?** High-velocity schema evolution needs migration discipline AND a tolerance for downtime windows (zero-downtime is achievable but expensive).

The Designer documents the schema, the indexes, the constraints, the migration plan, AND the rationale — in the per-layer Design subsection.
