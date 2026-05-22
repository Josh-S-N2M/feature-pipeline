# Error-Contract Patterns

## Contents

- Pattern E1: Explicit error type in return position
- Pattern E2: Typed exceptions with `throws`/`raises` annotation
- Pattern E3: Documented sentinel return
- Pattern E4: Error elision with explicit pointer
- What fails dimension 3
- Pattern selection by layer

Accepted ways to show error handling in a design-time sample. Each pattern satisfies dimension 3 (error contract visible) without bloating the sample.

## Pattern E1: Explicit error type in return position

**Languages with a result/either type** (Rust, OCaml, Haskell, Scala with `Either`, Go with `(T, error)`, modern TypeScript with discriminated unions): use the language's idiom directly.

```rust
fn load_user(id: UserId) -> Result<User, LoadError> {
    let row = db.query_one("...").map_err(LoadError::Db)?;
    User::from_row(row).map_err(LoadError::Parse)
}

enum LoadError { Db(DbError), Parse(ParseError), NotFound }
```

The error type is right there in the signature. Reader knows exactly what can go wrong.

## Pattern E2: Typed exceptions with `throws`/`raises` annotation

**Languages where exceptions are the idiom** (Java, C#, Python, Kotlin): annotate the throw set.

```python
def load_user(user_id: UserId) -> User:
    """
    Raises:
        UserNotFound: no row matches user_id
        DatabaseUnavailable: connection or query failure
    """
    row = db.query_one(...)  # may raise DatabaseUnavailable
    if row is None:
        raise UserNotFound(user_id)
    return User.from_row(row)
```

The docstring is the contract. Reviewer checks each `Raises:` entry is actually raised somewhere reachable.

## Pattern E3: Documented sentinel return

**Languages with sentinel idioms** (older C, Lua, sometimes Python with `None`): make the sentinel meaning explicit in the signature comment.

```python
def find_user(email: str) -> User | None:
    """Returns None when no user with this email exists. Raises only for infrastructure failures."""
    return db.query_one(...)
```

The contract: `None` = legitimate not-found; exception = unexpected failure. Without the comment, dimension 3 score is 4–6 (reader has to guess).

## Pattern E4: Error elision with explicit pointer

When the sample needs to focus on the happy path, error handling can be elided — but with a pointer to where it lives.

```typescript
async function createOrder(input: OrderInput): Promise<Order> {
    const validated = await validate(input);  // throws on invalid input — see Error Handling section
    const order = await orderRepo.create(validated);  // throws on DB failure — same section
    await events.emit('order_created', order);  // fire-and-forget; see Background Work
    return order;
}
```

The reader knows the sample is happy-path because the comments point elsewhere. Reviewer checks that the pointed-to section actually covers those errors.

## What fails dimension 3

- `try { ... } catch (e) {}` with no comment and no further handling
- Returning `null` / `None` with no comment explaining what it means
- A function whose prose says "may fail" but whose sample shows no failure path or pointer
- `.unwrap()`, `!`, `?` in Rust/Swift/etc. with no rationale — these PROMISE success but the sample shouldn't promise something the design doesn't

## Pattern selection by layer

| Layer | Preferred pattern |
|---|---|
| Frontend (React/Vue/Svelte) | E2 with React error boundaries noted, or E1 with discriminated unions |
| Backend (Rust/Go) | E1 |
| Backend (Python/Node) | E2 |
| API contracts (OpenAPI/GraphQL) | E1 in schema (`oneOf` error union); E2 in server impl samples |
| Query / Data Access | E1 (`Result<Row, QueryError>`) or E2 in higher-level repo methods |
| Database (migration scripts) | E4 — elide with pointer to migration runbook |
| CI/CD (workflows) | YAML has no exception types; use `continue-on-error: false` + step-level `if:` — sample must show these |
| IaC (Terraform/etc.) | Provider errors propagate; sample shows `lifecycle.prevent_destroy` or `ignore_changes` when applicable |
| Codespaces | Lifecycle scripts use shell semantics; sample shows `set -euo pipefail` |
| Claude Code | Sub-agent errors: show the `verdict.decision = "rejected"` path and what the orchestrator does |
