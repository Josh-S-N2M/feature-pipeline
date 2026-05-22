# API Patterns and Anti-Patterns

Patterns the API Designer favors, anti-patterns to flag, and decision frames.

## Contents

- Contract-style patterns (REST / GraphQL / gRPC)
- Resource modeling patterns (REST)
- Schema patterns (GraphQL)
- RPC patterns (gRPC)
- Versioning patterns
- Pagination patterns
- Rate-limiting patterns
- Anti-patterns reviewers should flag
- Decision frames

## Contract-style patterns

### REST

**Pattern.** Resources at URLs, manipulated with HTTP methods (`GET`, `POST`, `PUT`, `PATCH`, `DELETE`). JSON bodies. Stateless.

**When to use.** Public APIs, partner APIs, internet-facing systems where HTTP semantics, caching, and broad tooling matter. Default choice unless there's a reason otherwise.

**Strengths.** Universal client support; cacheable; firewall-friendly; well-understood. OpenAPI tooling mature.

**Weaknesses.** Over-fetching (returns more than needed); under-fetching (multiple round trips for related resources). Both addressable with sparse-fieldsets and embedded representations.

### GraphQL

**Pattern.** Single endpoint; clients send queries describing exactly what they want; server returns matching shape. Strongly typed schema.

**When to use.** Multiple clients with diverging data needs (web + mobile + partner). Heavy aggregation across many resources per view. Internal APIs with high-velocity contract evolution.

**Strengths.** Client-driven shape; no over/under-fetching; strong types; introspection. Schema evolution is additive-friendly.

**Weaknesses.** Caching is harder (POST with body, not URL-based). Authorization at field level is non-trivial. N+1 query patterns are easy to write; require dataloader discipline at the Backend. Operational complexity (query cost analysis, depth limits, persisted queries).

### gRPC

**Pattern.** Service-defined RPCs over HTTP/2 with Protocol Buffers serialization. Bidirectional streaming.

**When to use.** Internal service-to-service communication. High-performance / low-latency needs. Streaming.

**Strengths.** Compact binary protocol; codegen for ~10 languages; built-in streaming; strong types.

**Weaknesses.** Limited browser support (gRPC-Web is a bridge but adds complexity). Less friendly to debugging (binary protocol). Less ecosystem for external API exposure.

### Hybrid

**Pattern.** Use REST for external/public surface; GraphQL for internal aggregation; gRPC for service-to-service. Each layer has the right protocol for its audience.

**When to use.** Mature systems with multiple consumer profiles.

**Risk.** More to learn and maintain. Spec-first discipline must apply uniformly.

## Resource modeling patterns (REST)

### Collection + item

```
GET    /orders          → list orders (with cursor pagination)
POST   /orders          → create order
GET    /orders/{id}     → fetch order
PATCH  /orders/{id}     → update order
DELETE /orders/{id}     → delete order
```

**When to use.** Default REST shape. Every resource that's individually addressable + listable.

### Sub-resources for one-to-many

```
GET    /orders/{id}/items
POST   /orders/{id}/items
DELETE /orders/{id}/items/{item_id}
```

**When to use.** The child resource's lifecycle is bound to the parent (cascade delete, no orphans).

**Anti-pattern.** Deep nesting beyond 2 levels (`/orders/{id}/items/{item_id}/notes/{note_id}/replies/...`) makes URLs unmanageable. Flatten with top-level endpoints once the relationship is established.

### Action endpoints (controllers)

For state transitions that aren't naturally a PATCH (`cancel an order`, `approve a transfer`):

```
POST /orders/{id}/cancel    → 200 OK with updated order
POST /transfers/{id}/approve
```

**When to use.** When the action has additional parameters, side effects, or business meaning beyond "set this field." `PATCH /orders/{id}` with `{status: "cancelled"}` looks similar but obscures the business operation; `POST /orders/{id}/cancel` is explicit.

**Risk.** Don't slip into RPC-over-REST. If most of your endpoints are `POST /resource/action`, REST may not be the right protocol.

### Filtering, sorting, sparse fieldsets

```
GET /orders?status=pending&sort=-created_at&fields=id,status,total
```

**When to use.** Listing endpoints with multiple consumer profiles. Sparse fieldsets help reduce payload for mobile clients.

**Document.** Allowed filter keys; allowed sort keys; default fields if `fields` omitted.

## Schema patterns (GraphQL)

### Per-domain types

```graphql
type Order {
  id: ID!
  status: OrderStatus!
  total: Money!
  items: [OrderItem!]!
}

enum OrderStatus { DRAFT, PENDING, FULFILLED, CANCELLED }
```

**When to use.** Default. Domain objects as types; relationships as fields returning lists or single objects.

### Connections for pagination

```graphql
type Query {
  orders(first: Int, after: String): OrderConnection!
}

type OrderConnection {
  edges: [OrderEdge!]!
  pageInfo: PageInfo!
}

type OrderEdge {
  node: Order!
  cursor: String!
}
```

**When to use.** Any field returning a list of more than a handful of items. The Relay-style Connection pattern is the canonical GraphQL pagination.

### Input types for mutations

```graphql
input CreateOrderInput {
  customerId: ID!
  items: [OrderItemInput!]!
}

type Mutation {
  createOrder(input: CreateOrderInput!): CreateOrderPayload!
}
```

**When to use.** Always. Wrapping arguments in a typed `Input` keeps mutation signatures stable when adding optional fields.

### Field-level authorization

```graphql
type User {
  id: ID!
  email: String @auth(requires: SELF_OR_ADMIN)
}
```

**When to use.** Required for any GraphQL API with mixed-actor access. Implemented via directives, resolvers with auth checks, or framework support.

**Risk.** Without field-level auth discipline, GraphQL queries leak data. Auth must be a first-class part of the schema.

## RPC patterns (gRPC)

### Unary RPC

```proto
service OrderService {
  rpc GetOrder(GetOrderRequest) returns (Order);
  rpc CreateOrder(CreateOrderRequest) returns (Order);
}
```

**When to use.** Default. One request, one response.

### Server streaming

```proto
service OrderService {
  rpc WatchOrder(WatchOrderRequest) returns (stream OrderUpdate);
}
```

**When to use.** Server-pushed updates over time (status changes, log tail).

### Client streaming

**When to use.** Client uploads a sequence (large file in chunks, batch of events).

### Bidirectional streaming

**When to use.** Long-lived interactive sessions (chat, real-time collaboration).

**Risk.** Streaming is harder to operate; document timeout, retry, and reconnection semantics carefully.

## Versioning patterns

### URL path versioning

`/v1/orders` → `/v2/orders`

**When to use.** Most common; very visible; easy to operate; supports parallel maintenance.

### Header versioning

`Accept: application/vnd.example.v2+json`

**When to use.** When URL stability matters (e.g., resource URIs are referenced from elsewhere). Less visible to ops.

### Never-break / additive-only

Single version forever; only add fields; never remove or change.

**When to use.** Internal APIs with rapid iteration. Public APIs with extreme stability commitments (PayPal famously runs v1 of its API for 20+ years).

**Risk.** Schema bloat over time; technical debt accumulates.

## Pagination patterns

### Cursor

```
GET /orders?cursor=abc&limit=50
```

**When to use.** Default. Survives concurrent inserts and deletes.

### Page + size

```
GET /orders?page=2&size=50
```

**When to use.** UI shows page numbers ("page 5 of 23"). Total count required.

**Risk.** Same as offset: broken under concurrent writes. Acceptable when the underlying list is stable or the user accepts occasional dupes.

### Time-based

```
GET /events?since=2026-05-19T12:00:00Z
```

**When to use.** Time-ordered streams (event logs, audit trails). The cursor is implicit in the timestamp.

## Rate-limiting patterns

### Per-actor token bucket

Each authenticated actor has a bucket of N tokens that refills at R per second. Each request consumes 1 token; empty bucket → 429.

**When to use.** Default. Fair across actors.

### Per-endpoint quota

Each endpoint has a global RPS cap. Excess traffic gets 429.

**When to use.** Endpoints that are expensive to serve (large queries, ML inference); protecting backend capacity.

### Per-tenant quota

For multi-tenant SaaS: rate limits per tenant, by plan tier.

**When to use.** SaaS APIs with paid tiers. The Designer documents the tier-to-limit mapping.

### Headers

```http
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 847
X-RateLimit-Reset: 1716139200
Retry-After: 60         # on 429
```

Document the headers as part of the contract.

## Anti-patterns reviewers should flag

| Anti-pattern | Why it's bad | Typical fix |
|---|---|---|
| Verbs in REST URLs (`/getUser`) | Breaks REST conventions; loses cacheability | Use HTTP method + noun |
| 200 OK with `success: false` in body | Breaks every standard HTTP client error path | Match status code to actual outcome |
| Auth token in URL query string | Logged everywhere; history-leaked; search-indexed | `Authorization: Bearer ...` header |
| Inconsistent error envelope across endpoints | Clients can't write one parser | One canonical envelope |
| `id` as both number and string in different endpoints | Type drift, deserialization bugs | Pick one; document |
| Field name in `snake_case` and `camelCase` mixed | Client deserialization bugs | One convention; document |
| Pagination via offset on unbounded list | Skipped / duplicated items under writes | Cursor pagination |
| `GET /users/list-all` with no pagination | Memory exhaustion for clients and server | Always paginate |
| Mutation without idempotency | Duplicate side effects on retry | Idempotency-Key header |
| Field renamed in same version | Breaking change snuck in | Add new field; deprecate old in this version; remove in next major |
| Required field added in same version | Breaking change snuck in | Make optional with default; require in next major |
| `204 No Content` with a body | Standards violation; some clients reject | `200 OK` if body, `204` if not |
| Sensitive errors include stack traces | Information disclosure | Log internally; return code + message |
| `429` without `Retry-After` header | Clients don't know when to retry | Always include `Retry-After` (seconds or HTTP-date) |
| `403` for "doesn't exist" vs "exists but not allowed" | Indistinguishable; security-by-obscurity in wrong place | Document choice; consistent across endpoints |
| GraphQL query without depth / cost limits | DoS vector | Depth limit, query cost analysis, persisted queries |
| gRPC `string` for what should be a typed enum | Loses type safety; values drift | `enum` definition |
| Webhook contract without HMAC signing | Spoofable | HMAC over body + timestamp; document the secret-rotation flow |
| API doc hand-written separately from code | Drifts | Generate from spec |
| No deprecation policy documented | Clients caught by surprise | Document policy; use `Deprecation` and `Sunset` headers |
| `POST /search` for what should be `GET /search?...` | Loses caching | Use GET unless body is genuinely required |

## Decision frames

When the API Designer faces a choice (contract style, versioning, pagination), apply this frame:

1. **Who consumes this API?** Internal services, internal UI, external partners, public consumers. Each has different stability and discoverability needs.
2. **What's the data shape?** Hierarchical with cross-resource aggregation favors GraphQL. Independent resources favor REST. Streaming favors gRPC.
3. **What's the deployment ecosystem?** HTTP/REST works everywhere; gRPC needs HTTP/2 and protobuf tooling; GraphQL needs client libraries.
4. **What's the team's experience?** REST is universally familiar; GraphQL has a learning curve; gRPC requires protobuf discipline.
5. **What's the change cadence?** GraphQL favors evolution; REST/gRPC favor explicit versioning.

The Designer writes the argument — not just the conclusion — in the per-layer Design subsection.
