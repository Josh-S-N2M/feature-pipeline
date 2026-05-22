# Database Design Principles

## Contents

- Principle 1: Constraints at the DB, not just at the app
- Principle 2: Atomic, reversible, zero-downtime migrations
- Principle 3: Indexes for the actual queries, not for "completeness"
- Principle 4: UTC everywhere; convert at display time
- Principle 5: Hard-delete by default; soft-delete with discipline
- Principle 6: Audit columns on every mutable table
- Principle 7: Decimal for money; never float
- Principle 8: Externally addressable IDs are opaque

## Principle 1: Constraints at the DB, not just at the app

The application is the first line of defense; the database is the last. The two are complementary, not redundant.

Application-only validation fails when:

- A different service writes to the same table (microservices, scripts, manual ops).
- An ORM bug causes a partial write.
- A migration leaves rows in an unexpected state.
- A bulk import bypasses application code.

DB-level constraints catch all of these. The Designer specifies, for every table:

- **NOT NULL.** For columns that must always have a value. Default to NOT NULL; allow NULL only when "absent" is a meaningful state.
- **UNIQUE.** For columns where duplicates would be a domain violation (email, username, external_id).
- **FOREIGN KEY.** For references between tables. With `ON DELETE` clause: CASCADE (delete dependents), SET NULL (orphan with null), RESTRICT (prevent deletion).
- **CHECK.** For domain rules expressible in SQL: `CHECK (price >= 0)`, `CHECK (status IN ('draft','pending','approved','rejected'))`.
- **UNIQUE partial index** (Postgres): `CREATE UNIQUE INDEX ... WHERE deleted_at IS NULL` for "unique among non-deleted rows."
- **EXCLUSION** (Postgres, for non-overlap constraints): meeting-room booking, version-effective-dates, etc.

For document stores (MongoDB) and key-value stores (DynamoDB), constraint enforcement varies:

- MongoDB supports JSON schema validation, unique indexes, required-field rules.
- DynamoDB supports type validation, secondary indexes, conditional writes.

The Designer documents the constraint plan in the per-layer subsection, including which constraints are DB-enforced and which are app-enforced (with rationale for any app-only constraints).

## Principle 2: Atomic, reversible, zero-downtime migrations

A migration that requires downtime is a failure of design. The Designer follows the expand-then-contract pattern for any change in a deployed system:

**Adding a NOT NULL column.** A naive `ALTER TABLE ADD COLUMN x INT NOT NULL` rewrites the table (locks). Instead:

1. Add nullable column (`ADD COLUMN x INT`). Fast metadata-only operation.
2. Deploy app version that writes to `x`.
3. Backfill in batches (don't write a single big UPDATE).
4. Wait until all rows have `x` populated.
5. Tighten constraint: `ALTER COLUMN x SET NOT NULL`. Fast in Postgres 12+ if all rows already non-null.

**Renaming a column.** Don't.

1. Add new column with new name.
2. Deploy app version that writes to both columns and reads from new (with fallback to old).
3. Backfill new from old.
4. Deploy app version that reads only from new.
5. Drop old column.

**Removing a column.** First deploy the app version that doesn't reference it. Then drop the column.

**Changing a column type.** Like renaming: add new column with new type, dual-write, backfill, switch reads, drop old.

**Adding an index.** Use `CREATE INDEX CONCURRENTLY` (Postgres) or equivalent. Standard `CREATE INDEX` locks the table.

The Designer documents the migration sequence for each schema change, including:

- The exact SQL statements.
- The order (multi-step migrations specify what runs in which deployment).
- The backfill strategy (batch size, throttling, completion check).
- The rollback path (what to do if step N fails — usually: revert the application deploy that depended on this step).

## Principle 3: Indexes for the actual queries, not for "completeness"

Indexes have a cost: storage, write amplification, plan-cache complexity. The Designer indexes for the queries that exist (or are imminently planned), not for "every column anyone might filter on."

Discipline:

- **Every WHERE / JOIN / ORDER BY column on a hot path** has an index aligned to the predicate.
- **Composite indexes** match the leading columns of the query: an index on `(customer_id, created_at)` serves queries that filter by `customer_id` alone or by both. It does NOT serve queries that filter only by `created_at`.
- **Partial indexes** (Postgres) for "most rows don't satisfy this filter": `CREATE INDEX ... WHERE status = 'pending'`. Smaller; faster to maintain.
- **Expression indexes** for queries that filter by a computed value: `CREATE INDEX ON users (lower(email))` if queries do `WHERE lower(email) = ...`.
- **Covering indexes** when SELECT can be served entirely from the index (Postgres `INCLUDE` clause).

For each table, the Designer documents:

- The query patterns the schema serves (a small set of canonical queries).
- The indexes that serve them.
- The size estimate at design-time scale (so the cost is visible).

Anti-patterns:

- "Index every column." Storage and write cost; query planner confusion.
- Index on a low-cardinality column (e.g., a boolean) without a compound key. Doesn't help.
- Foreign-key columns without indexes. The FK constraint adds a check; queries by FK column scan without the index.
- Adding indexes "just in case." If no query uses it, drop it.

## Principle 4: UTC everywhere; convert at display time

Storing timestamps without time zones causes a category of bugs that's hard to diagnose: events appear to happen at the wrong time depending on which server processes the request, daylight-savings cliffs corrupt data, customer-support reports don't match server logs.

The Designer's discipline:

- **All timestamps stored in UTC.** Engine-specific: Postgres `timestamptz`, MySQL `TIMESTAMP` (which is UTC internally if `time_zone = 'UTC'`), MongoDB stores as UTC ms epoch.
- **Application code always uses timezone-aware datetimes.** Python `datetime.now(timezone.utc)`, Go `time.Now().UTC()`, etc.
- **Display-time conversion only.** The Frontend converts UTC → user's locale; the Backend doesn't.
- **No `timestamp` (without time zone) in Postgres.** It's a footgun. If you mean "wall-clock time at a specific place" (e.g., business hours), store the place separately and the wall-clock with explicit semantics.

Acceptance Criteria that fall out:

- The system shall store all event timestamps in UTC.
- When the user views a timestamp, the system shall display it in the user's configured timezone, defaulting to the browser's detected timezone.

## Principle 5: Hard-delete by default; soft-delete with discipline

Soft-delete (marking a row deleted with `deleted_at` rather than removing it) is a discipline. Every query must filter `WHERE deleted_at IS NULL`. One missed filter and the application "leaks" deleted records.

The Designer's defaults:

- **Hard-delete unless there's a reason for soft-delete.** Reasons: audit requirements, referential integrity with rows referenced elsewhere, ability to restore, GDPR-style "right to be forgotten" with soft-delete-then-purge windows.
- **When soft-delete is used:** unique constraints become partial (`UNIQUE ... WHERE deleted_at IS NULL`). Foreign keys may need to relax (or the FK target's soft-delete cascade is handled explicitly).
- **Index on `deleted_at` if soft-deleted rows are a small fraction.** Otherwise every query has to filter, and the planner needs help.
- **Document the soft-delete contract.** Which tables soft-delete; what happens at the boundaries (does a soft-deleted user's data also soft-delete?); how purge windows work.

For GDPR/CCPA compliance specifically: a soft-delete is not a delete. The Designer documents the actual purge pipeline: how soft-deleted rows are physically removed after the retention window, including from backups (the harder problem).

## Principle 6: Audit columns on every mutable table

Every mutable table carries:

- **`created_at` TIMESTAMPTZ NOT NULL DEFAULT now()** — when the row was inserted.
- **`updated_at` TIMESTAMPTZ NOT NULL DEFAULT now()** — when the row was last modified. Updated via trigger or app-side audit.
- **`created_by` ID** — actor who created the row (where applicable; for system inserts, a sentinel value).
- **`updated_by` ID** — actor who last modified.

These columns:

- Survive every bug. When something's wrong, "when did it last change and by whom?" is the first question to answer.
- Are invariably useful in postmortems.
- Don't cost much (16 bytes per row plus storage).

Anti-pattern: forgetting these and only adding them once they're needed for an incident.

For immutable tables (event tables, append-only logs): `created_at` only; `updated_at` is meaningless.

## Principle 7: Decimal for money; never float

`SELECT 0.1 + 0.2` in floating-point returns `0.30000000000000004`. For money, that's wrong by enough to fail audits.

The Designer's discipline:

- **Money columns use DECIMAL / NUMERIC with explicit precision and scale.** `NUMERIC(19, 4)` covers up to ~10^15 with 4 decimal places; sufficient for any reasonable use case.
- **The application uses a decimal type that round-trips faithfully.** Python `Decimal`, JS BigInt-based money library, Go `shopspring/decimal`, Java `BigDecimal`. Never float / double.
- **Document the precision.** All-prices-in-cents (integer pennies) is acceptable; document the choice. Mixing per-currency precision is a nightmare; either pick one canonical precision or store currency code alongside.
- **Same applies to scientific measurements**, latitude/longitude (where the precision matters), and any other domain where rounding errors compound.

## Principle 8: Externally addressable IDs are opaque

Internal autoincrement primary keys (`bigint`) are fine for joins. But exposing them externally is problematic:

- **Information leakage.** "Order ID 17" + "Order ID 18" tells competitors your daily order count.
- **Enumeration vulnerability.** Knowing one valid ID, an attacker can guess others.
- **Coupling.** Frontend / partner contracts reference these IDs; renumbering becomes impossible.

The Designer's options:

- **UUID v4** — random 128-bit. Globally unique. No ordering. Larger (16 bytes vs. 8).
- **UUID v7** — time-ordered UUID (recently standardized). UUID v4's properties + time-sortable. Better for indexes (sequential insertion).
- **ULID** — 128-bit, time-sortable, Crockford base32 string. Functionally similar to UUIDv7.
- **NanoID, KSUID, Snowflake** — other compact, sortable, random ID schemes.

The Designer picks one and applies it consistently. Hybrid is acceptable: internal `bigint` PK + external `ulid` column with a unique index. Joins go via PK; external references use ULID.

Document the choice in the per-layer Design subsection and make it an Acceptance Criterion:

- All new tables shall expose a ULID (or UUIDv7) `public_id` column used in external API responses.
- The system shall not expose internal numeric primary keys in API responses or URLs.
