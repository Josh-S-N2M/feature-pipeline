# API Design Principles

The foundational principles an API Designer applies when authoring the `### API Design` subsection of the Blueprint.

## Contents

- Principle 1: The contract is a commitment, not a guideline
- Principle 2: Pessimistic versioning
- Principle 3: Stable error envelope across the API
- Principle 4: Idempotency is part of the contract, not optional
- Principle 5: Pagination that survives concurrent writes
- Principle 6: HTTP / protocol semantics mean what they mean
- Principle 7: Authentication and authorization at the edge, not sprinkled
- Principle 8: Documentation generated from the contract, not hand-maintained

## Principle 1: The contract is a commitment, not a guideline

An API contract is a promise to every client that has ever read your documentation. Once a client integrates against `GET /orders/{id}` returning `{id, status, total}`, every word of that shape is load-bearing — clients may rely on field names, types, ordering, error codes, status codes, header names, anything.

This means:

- **Every field is intentional.** Adding optional fields is generally safe (additive); removing or renaming fields is not.
- **Every status code is intentional.** Returning 200 instead of 204 changes parsing behavior in some clients.
- **Every error code is intentional.** Once `code: "INSUFFICIENT_FUNDS"` exists, removing it is breaking even if the situation never re-arises.

The API Designer specifies the contract precisely — schemas, examples, error categories, status codes — and treats the result as a contract, not a sketch.

## Principle 2: Pessimistic versioning

Versioning matters because clients can't be coordinated in lock-step. Three observable strategies:

| Strategy | Mechanic | Cost / Benefit |
|---|---|---|
| **Never break** | Only additive changes; never rename / remove / retype | Maximum client compatibility; long-term schema drift accumulates |
| **Versioned URLs** | `/v1/orders` → `/v2/orders` with parallel maintenance | Clear migration boundary; multiple versions live in parallel |
| **Versioned media types** | `Accept: application/vnd.example.v2+json` | Same URL, content-negotiated; less visible to ops |

Pessimistic means: assume the API will need versions. Pick the strategy at design time, document the policy, and apply it consistently.

A few rules that fall out of pessimistic versioning:

- **Breaking changes go to a new version.** Adding required fields, removing fields, changing field types, changing required/optional, changing error categories — all v2 events.
- **Deprecation runs through a window.** Deprecation announcement → continued support for N months → sunset. The window is documented; clients have time.
- **Don't break v1 in v1.** Even if v2 is launched, v1 stays exactly as documented until sunset.
- **`Deprecation` and `Sunset` headers** (RFC 8594) announce removal dates programmatically; clients can warn or alert ahead of time.

## Principle 3: Stable error envelope across the API

Errors are part of the contract. Every endpoint that can fail returns errors in the same shape, with documented categories.

A canonical shape (close to RFC 7807 Problem Details):

```json
{
  "type": "https://api.example.com/errors/insufficient_funds",
  "title": "Insufficient funds",
  "status": 402,
  "code": "INSUFFICIENT_FUNDS",
  "detail": "Account balance is $42.00; transfer requested $100.00.",
  "instance": "/transfers/abc123",
  "retriable": false,
  "details": {
    "account_id": "acc_xyz",
    "available": 42.00,
    "requested": 100.00
  }
}
```

The fields:

- **`code`** — machine-readable identifier. Clients branch on this. Stable across versions of the same error.
- **`message` / `title` / `detail`** — human-readable. UI shows this. Not stable across versions; can be re-worded.
- **`retriable`** — boolean. Drives client retry behavior. Errors caused by transient failure (network blip, downstream timeout) are retriable; errors caused by client mistake or business state aren't.
- **`details`** — structured supplementary data. Specific to the error code.

The API Designer specifies the finite set of error codes, the matching HTTP status codes, and the conditions under which each is returned.

Anti-pattern: each endpoint inventing its own error shape. Clients have to write a parser per endpoint; observability dashboards can't aggregate.

## Principle 4: Idempotency is part of the contract, not optional

Networks fail. Retries are inevitable. The API Designer specifies, for every endpoint:

- **Is it idempotent?** GET, HEAD, OPTIONS, PUT (when used to set state) are idempotent. POST, PATCH (when used to modify) are typically not, unless the API provides a mechanism.
- **If not, what's the idempotency mechanism?** Idempotency key header is the standard. Stripe, AWS, GitHub, and most modern APIs implement `Idempotency-Key`:

```http
POST /transfers HTTP/1.1
Idempotency-Key: 7f3a9c1b-...

{ "amount": 100.00, "to": "acc_xyz" }
```

The server stores `(key, response)` for a 24h–7d window. Duplicate `Idempotency-Key` returns the original response; the duplicate body is rejected with 409 if it differs.

The contract documents:

- Which endpoints accept `Idempotency-Key`.
- Required vs. optional.
- The retention window.
- What constitutes "same request" (key alone, or key + body hash).
- Behavior when key is missing on a non-idempotent endpoint (warn? reject? proceed without guarantee?).

## Principle 5: Pagination that survives concurrent writes

Offset-based pagination (`?offset=20&limit=10`) is broken under concurrent writes. If the list grows or shrinks between page 2 and page 3, items are skipped or duplicated.

Cursor-based pagination is stable: the cursor is an opaque token pointing at a specific position in the underlying ordering.

```http
GET /orders?cursor=eyJpZCI6ICJvcmRfNzg5In0&limit=50
```

Response:

```json
{
  "data": [ ... ],
  "next_cursor": "eyJpZCI6ICJvcmRfODM5In0",
  "prev_cursor": "eyJpZCI6ICJvcmRfNzM5In0"
}
```

Properties:

- **Opaque to clients.** The encoding is the server's business; clients pass the cursor back unchanged.
- **Stable under inserts.** New items don't shift positions.
- **Bounded list size.** `limit` is capped at a sensible maximum (e.g., 100).

The API Designer documents:

- The page-size limit and default.
- The next/prev cursor presence (some APIs only support forward).
- Total-count availability (often omitted because computing a fresh count per page is expensive).
- Stable ordering (cursors require it; document the ordering criterion).

Offset pagination is acceptable when the list is small and bounded (e.g., user's own resources, capped at known maximum). For unbounded lists, cursor pagination is the default.

## Principle 6: HTTP / protocol semantics mean what they mean

In REST over HTTP, the protocol has shared semantics that clients, proxies, caches, and tooling rely on:

| Element | Meaning |
|---|---|
| `GET` | Safe (no side effects) and idempotent. Cacheable. |
| `HEAD` | Like GET but no body. For metadata only. |
| `POST` | Not safe, not idempotent. Creates / processes / triggers. |
| `PUT` | Idempotent. Replace target with provided representation. |
| `PATCH` | Modify partial state. Idempotency depends on patch language. |
| `DELETE` | Idempotent (re-deleting a deleted resource is the same). |
| `200 OK` | Success with body. |
| `201 Created` | Resource created; `Location` header points to it. |
| `204 No Content` | Success, no body. |
| `400 Bad Request` | Malformed syntax. |
| `401 Unauthorized` | Missing or invalid credentials. |
| `403 Forbidden` | Authenticated but not allowed. |
| `404 Not Found` | Resource doesn't exist. |
| `409 Conflict` | State conflict (e.g., version mismatch, idempotency-key mismatch). |
| `422 Unprocessable Entity` | Syntactically valid but semantically wrong. |
| `429 Too Many Requests` | Rate limited. |
| `500 Internal Server Error` | Server failure, no further info. |
| `502 Bad Gateway` | Upstream failure. |
| `503 Service Unavailable` | Temporarily down. |
| `504 Gateway Timeout` | Upstream timed out. |

Anti-patterns:

- **Returning 200 with `success: false` in the body.** Tools assume 200 = success.
- **404 for unauthorized.** Hides authorization; some style guides allow it for security but document the choice.
- **Treating 401 and 403 as interchangeable.** They mean different things and clients respond differently.
- **`POST /getOrder` instead of `GET /orders/{id}`.** Verbs in URLs; loses cacheability.

For GraphQL and gRPC, equivalent semantic conventions apply (GraphQL error categories; gRPC status codes). The API Designer documents the conventions explicitly.

## Principle 7: Authentication and authorization at the edge, not sprinkled

Auth concerns live in one place: the API edge. Every endpoint declares its auth requirements via metadata (decorators, middleware, OpenAPI security schemes), enforced by a single mechanism.

This means:

- **Bearer tokens in `Authorization` header**, not in URL or body.
- **Tokens scoped to operations** (OAuth scopes, JWT claims). The endpoint checks scope presence; the Backend trusts the check.
- **Authorization in middleware or guards**, not in business logic. Mixing "is this user allowed?" with "what should happen?" makes both harder to audit.
- **Single identity propagation mechanism.** The user/principal/actor reaches the Backend through one path; not "sometimes the JWT claim, sometimes a header, sometimes a fallback to query param."

The API Designer documents:

- The auth scheme(s).
- The scope / role model.
- Per-endpoint requirements (`security:` in OpenAPI; `@authorize` decorator; etc.).
- The unauthenticated path (does the API serve any public endpoints? if so, which?).
- How identity reaches downstream Backend code (header, context object, etc.).

## Principle 8: Documentation generated from the contract, not hand-maintained

Hand-written API docs drift. The contract (OpenAPI spec, GraphQL SDL, gRPC proto) is the source of truth.

The API Designer specifies:

- **The format.** OpenAPI 3.x for REST. GraphQL SDL (with comments). Protobuf `.proto` files. Pick one per API; don't mix.
- **The generation flow.** Spec → docs (static site); spec → server stubs; spec → client SDKs. The spec is authored once; everything else generates.
- **The CI gate.** The spec is parsed in CI; breaking changes (per a diff tool like `oasdiff` for OpenAPI) fail the build unless an explicit major-version label is applied.
- **Examples.** Every endpoint has at least one realistic example request and response. Examples are kept in the spec, not in side docs that can drift.

Anti-pattern: spec-second. Writing the code, then trying to retroactively document it. The doc and code drift; new fields are forgotten; deprecations are missed. Spec-first (or schema-first) is the discipline.
