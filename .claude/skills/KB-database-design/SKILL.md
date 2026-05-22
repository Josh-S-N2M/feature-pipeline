---
name: kb-database-design
description: >-
  Design discipline for the Database layer — the persistent storage. Covers
  schema design (normalization, denormalization for performance), indexes,
  constraints, primary-key and foreign-key strategy, migrations, atomic
  schema-change patterns, time/timezone discipline, and the per-layer
  designer's workflow for producing the Database Design subsection of a
  Blueprint. Use when the feature touches storage. Pairs with KB-query-design
  (the layer that talks to this storage) and KB-iac-design (when storage
  infrastructure is provisioned through code).
allowed-tools: Read, Grep, Glob
---

# KB-database-design — Database Layer Design Discipline

Design discipline for the Database layer. The per-layer Database Designer (`design-database`) loads this KB during per-layer Design to produce the `### Database Design` subsection of the Blueprint. Design-discipline-only — specific DB engines (Postgres, MySQL, MongoDB, DynamoDB, etc.) are platform-level concerns the Designer pulls from Synthesis output as needed.

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

- A feature's PRD or Blueprint declares the **Database** layer in scope (per `layer-taxonomy.md` in KB-documentation-criteria)
- A per-layer Designer is producing the Database Design subsection of the Blueprint
- Plan Authoring produces tasks that touch schema, migrations, indexes, or constraints
- `shared-document-reviewer` or `review-architecture-auditor` is auditing artifacts that include Database Design

Sub-agents that reference this KB (per Blueprint v4.3.1):

- `design-database` (per-layer Design, when Database layer is in scope)
- `design-composer` (Design Composition, integrating Database design with cross-cutting concerns)
- `plan-author` (when tasks touch migrations or schema)
- `shared-document-reviewer` (Gate 1 Database-specific checks)
- `review-architecture-auditor` (CoVe checks on Database claims)

## The layer's responsibility

The Database layer owns the application's persistent state. It owns:

- **Schema.** Tables / collections / structures, columns / fields with types, primary keys.
- **Constraints.** NOT NULL, UNIQUE, FOREIGN KEY, CHECK constraints — the DB-level guarantees that protect the data even when application code has bugs.
- **Indexes.** What's indexed, for which queries. Index maintenance cost vs. read-time benefit.
- **Migrations.** How schema evolves over time. The atomicity, reversibility, and zero-downtime characteristics of each change.
- **Transactional semantics.** Isolation levels, lock scope, MVCC vs. lock-based concurrency.
- **Data lifecycle.** Retention, archival, deletion (hard vs. soft), GDPR/CCPA-grade purge mechanisms.

The Database layer does NOT own:

- The application logic that decides what to write (Backend's job).
- The queries used to read (Query layer's job).
- The storage hardware / provisioning (IaC's job).

## Design decisions this layer owns

The Database Designer makes (or surfaces) these decisions:

| Decision | Forced if … |
|---|---|
| Engine (Postgres, MySQL, MongoDB, DynamoDB, etc.) | Greenfield; brownfield usually inherits |
| Normalization level (3NF strict, pragmatic, denormalized for read perf) | Schema design is a from-scratch choice |
| Primary key strategy (auto-increment, UUID, ULID, content hash) | New entity types |
| Foreign-key enforcement (DB-level, app-level, none) | Cross-table relationships exist |
| Indexing plan (which columns, which composite indexes, partial indexes, expression indexes) | Any non-trivial read pattern |
| Constraints (CHECK, UNIQUE, NOT NULL, exclusion constraints) | The schema can express domain invariants |
| Soft-delete vs. hard-delete | Data needs auditability or deletion has compliance requirements |
| Time and timezone strategy (UTC everywhere, with-timezone vs. without) | Any timestamps |
| ID exposure (use internal autoinc externally vs. opaque public IDs) | Resources are externally referenced |
| Multi-tenancy strategy (shared schema with tenant column, schema-per-tenant, DB-per-tenant) | Multi-tenant product |
| Encryption at rest | Compliance requirement or sensitive data |
| Column-level encryption | PII or secrets stored |
| Partitioning / sharding strategy | Table is expected to grow beyond ~10M rows or hot row contention exists |

Designers do NOT author ADRs (per FR-5). Cross-cutting database decisions (canonical timestamp policy, system-wide multi-tenancy strategy) get surfaced as open items.

## Patterns and anti-patterns at a glance

The full discipline lives in `references/principles.md` and `references/patterns-and-anti-patterns.md`. Quick reference:

**Patterns to favor:**

- **DB-level constraints, not just app-level.** NOT NULL, UNIQUE, FOREIGN KEY, CHECK constraints catch bugs the app would let through. Defense in depth.
- **Migration atomicity discipline.** Zero-downtime migrations are a sequence: add nullable column → backfill → tighten constraint. Each step is atomic and safe to roll back.
- **Indexes for the actual queries.** Every WHERE / JOIN / ORDER BY column on a hot path has an index aligned to the predicate.
- **UTC, always.** All timestamps in UTC. Display-time conversion only.
- **ULIDs or UUIDs for externally referenced IDs.** Internal autoinc IDs are fine for joins; never expose them.
- **Audit columns: `created_at`, `updated_at`, `created_by`, `updated_by`.** On every mutable table. Set by the DB (trigger) or by a unified app-side audit layer.
- **Soft-delete only when needed.** Default to hard-delete. Soft-delete is a discipline (every query filters `deleted_at IS NULL`) and easy to get wrong.

**Anti-patterns to flag:**

- **App-level "validation" without DB constraint.** App may have bugs; DB shouldn't allow invariant violations.
- **Adding NOT NULL without default + backfill.** Production downtime.
- **`timestamp without time zone` in Postgres.** Source of timezone bugs.
- **Float types for money.** Use decimal/numeric with explicit precision.
- **Long-running transactions.** Lock contention; deadlock risk; long replication lag.
- **Schema migrations that lock for >5s.** Forces a maintenance window.

## Interaction with other layers

```
Backend ──► Query ──► [Database]
                          │
                          ├──► Replicas (managed by IaC)
                          ├──► Backups (managed by IaC)
                          └──► Migrations (run by CI/CD)
```

The Database Designer's responsibility:

- **Query (consumer)** — the schema is the interface. The Database Designer documents the schema; the Query Designer reads from it. Coupling the schema to specific Query patterns is fine; the same schema can serve multiple Query patterns.
- **IaC (provisioning)** — the Database layer documents the infrastructure requirements (engine version, instance class, replica count, backup retention, parameter groups). The IaC layer provisions those.
- **CI/CD (deploys)** — the CI/CD layer runs migrations. The Database Designer documents the migration ordering, the rollback strategy, and any zero-downtime patterns required.

## Surfacing architectural questions

```markdown
## Architectural Questions for Composer

- **Q-DB-1**: Should we standardize on ULID primary keys across new tables? The choice affects how IDs are exposed (ULID is URL-safe; autoinc requires a separate public ID), join performance (ULID is 16 bytes vs. 8 for bigint), and storage size. Evidence: 4 new tables in this feature; 3 of 4 reference each other; all 4 are externally addressed. Options: (a) ULIDs as the only PK type going forward; (b) bigint PKs with separate ULID public_id column; (c) UUIDv7 (close to ULID, ordered). Recommended: (c). Defer to composer.
```

## When to load each reference file

| Load this file | When the task involves |
|---|---|
| `references/principles.md` | Authoring or reviewing a Database Design subsection — covers the foundational principles (constraints first, atomic migrations, indexes for actual queries, UTC, audit columns, hard-delete default) |
| `references/patterns-and-anti-patterns.md` | Choosing between schema patterns, indexing strategies, migration strategies — covers common patterns with when-to-use and the anti-patterns reviewers should flag |
