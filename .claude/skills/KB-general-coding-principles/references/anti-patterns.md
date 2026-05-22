# Anti-Patterns in Design-Time Code Samples

## Contents

- AP-1: The plausible-but-fake API
- AP-2: The realistic-looking placeholder
- AP-3: The error-swallow
- AP-4: The cross-language mash-up
- AP-5: The drive-by `eval`
- AP-6: The naked production URL
- AP-7: The 200-line "minimal example"
- AP-8: The "we'll figure it out" idempotency dodge
- AP-9: The race condition the sample hides
- AP-10: The forgotten language fence
- How to use this list

Common samples that look fine to a reader skimming the document but fail one or more rubric dimensions. Each entry shows the offending pattern, why it fails, and the rewrite that passes.

## AP-1: The plausible-but-fake API

**Symptom:** A method call that reads naturally and matches the library's vibe, but the method doesn't exist.

```python
# Bad
from sqlalchemy.orm import Session
session.bulk_upsert(User, records, conflict_columns=["email"])
```

**Why it fails:** SQLAlchemy has no `bulk_upsert` method on `Session`. The pattern exists, but the API for it is `dialect.insert(...).on_conflict_do_update(...)` or similar. A reader copying this gets `AttributeError`.

**Fix:** Use the real API, or — if the design intent is to abstract over the dialect — explicitly say so:

```python
# Good — uses the real API
from sqlalchemy.dialects.postgresql import insert
stmt = insert(User).values(records).on_conflict_do_update(
    index_elements=["email"], set_={"updated_at": func.now()}
)
session.execute(stmt)
```

Or — if the design intent is abstraction:

```python
# Good — clearly an abstraction over the real API
# (UserRepository.upsert is a new method this design introduces; SQL details below)
user_repo.upsert(records, conflict_columns=["email"])
```

Auto-fail trigger: yes, dimension 4 (fabricated API).

## AP-2: The realistic-looking placeholder

**Symptom:** A "fake" credential or hostname that any reasonable security scanner will treat as real.

```yaml
# Bad
env:
  GITHUB_TOKEN: ghp_a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8
```

**Why it fails:** That token is the right length and prefix. It will trigger secret scanners, won't be obviously a placeholder to a skim reader, and may even be a real revoked token someone pasted.

**Fix:** Use an unmistakable placeholder:

```yaml
# Good
env:
  GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}  # provisioned via repo secret
```

Or, if showing the shape is genuinely necessary:

```yaml
# Good
# Token shape: 'ghp_' + 36 alphanumeric chars. Set via repo secret GITHUB_TOKEN.
```

Auto-fail trigger: depends on whether the string is a real revoked token. Score 0–3 even if known-fake.

## AP-3: The error-swallow

**Symptom:** Try/catch that drops the error to make the sample shorter.

```go
// Bad
data, _ := json.Marshal(payload)
io.Copy(w, bytes.NewReader(data))
```

**Why it fails:** Reader has no idea what the design says about marshal errors. In Go, this is more egregious because `_` is the explicit "I am dropping this" syntax.

**Fix:** Either show the error path or note it:

```go
// Good — error path shown
data, err := json.Marshal(payload)
if err != nil {
    return fmt.Errorf("marshal payload: %w", err)
}
io.Copy(w, bytes.NewReader(data))
```

Or:

```go
// Good — error path explicitly elided
data, err := json.Marshal(payload)  // err handling elided; see Error Handling section
io.Copy(w, bytes.NewReader(data))
```

## AP-4: The cross-language mash-up

**Symptom:** Sample purports to be Python but uses TypeScript-style syntax or vice versa.

```python
# Bad
async function processOrder(order: Order): Promise<Receipt> {
    const validated = await validate(order)
    return await save(validated)
}
```

**Why it fails:** That's not Python; it's TypeScript in a python-fenced block. Either the fence is wrong or the syntax is. A reader copying it gets an immediate syntax error.

**Fix:** Pick one language and commit to its syntax.

```python
# Good
async def process_order(order: Order) -> Receipt:
    validated = await validate(order)
    return await save(validated)
```

## AP-5: The drive-by `eval`

**Symptom:** Quick string-to-code shortcut hidden in the sample.

```javascript
// Bad
const handler = eval(`(${spec.handler_code})`);
return handler(req);
```

**Why it fails:** Dimension 6 (hidden control flow). The reader cannot tell what runs without seeing `spec.handler_code`. In a design sample, this kills the illustration's purpose — the sample is supposed to make the contract obvious.

**Fix:** Either show the dispatch table explicitly, or move to a real plugin architecture.

```javascript
// Good
const handlers = { create: createOrder, refund: refundOrder, void: voidOrder };
const handler = handlers[spec.action];
if (!handler) throw new UnknownActionError(spec.action);
return handler(req);
```

## AP-6: The naked production URL

**Symptom:** A real, public endpoint sitting in a sample.

```python
# Bad
requests.post("https://api.acme-corp-prod.example.com/v1/charges", ...)
```

**Why it fails:** Even if the URL is fake, samples get copy-pasted. If it's a real production URL, the sample is now a foot-gun.

**Fix:** Parameterize with a config variable, or use a clearly-illustrative host:

```python
# Good
requests.post(f"{config.charges_url}/v1/charges", ...)
# config.charges_url = "https://api.example.com/charges" (illustrative)
```

## AP-7: The 200-line "minimal example"

**Symptom:** A single code block long enough to be its own module.

**Why it fails:** Dimension 10. A reader's eye stops grokking around line 40–50. Anything longer is a draft, not an illustration.

**Fix:** Break into labeled blocks separated by prose explaining each piece. If the design genuinely needs 200 lines to express a contract, the design is too complex for a single section — split it.

## AP-8: The "we'll figure it out" idempotency dodge

**Symptom:** A state-changing operation with no idempotency posture.

```sql
-- Bad
INSERT INTO billing_events (user_id, amount, event_type)
VALUES ($1, $2, 'charge')
RETURNING id;
```

**Why it fails:** Dimension 7. Two reads of the same upstream message will produce two `billing_events` rows. The design needs to declare whether that's intentional.

**Fix:** Either show the idempotency mechanism or state the posture:

```sql
-- Good — idempotent via unique constraint
INSERT INTO billing_events (user_id, amount, event_type, dedup_key)
VALUES ($1, $2, 'charge', $3)
ON CONFLICT (dedup_key) DO NOTHING
RETURNING id;
```

Or:

```sql
-- Good — idempotency unspecified at this layer; dedup happens in caller
INSERT INTO billing_events (...) VALUES (...);
```

## AP-9: The race condition the sample hides

**Symptom:** Multi-step state machine shown as straight-line code, with no mention that concurrent callers will trash it.

```python
# Bad
def reserve_seat(seat_id):
    if seat_repo.is_available(seat_id):
        seat_repo.mark_reserved(seat_id)
        return True
    return False
```

**Why it fails:** Dimension 8. Two concurrent calls between the `is_available` and `mark_reserved` will both see "available" and both reserve. Sample makes the design look correct when it isn't.

**Fix:** Show the locking or state the posture:

```python
# Good — atomic via row-level lock
def reserve_seat(seat_id):
    with seat_repo.transaction():
        seat = seat_repo.lock_for_update(seat_id)
        if seat.available:
            seat.mark_reserved()
            return True
    return False
```

## AP-10: The forgotten language fence

**Symptom:** Fence is blank or wrong (` ``` ` instead of ` ```python `).

**Why it fails:** Syntax highlighters fail; readers and reviewers can't quickly orient. Also, dimension 9 scoring depends on language matching project — if the fence is blank, the reviewer can't even check.

**Fix:** Always include a language tag matching the layer's stack.

## How to use this list

- **As an author:** scan before emitting. Any AP-N you'd be embarrassed to defend → fix.
- **As a reviewer:** when a block scores < 80 on the rubric, find the AP-N it matches and cite by number in the issue (`issues[*].description = "AP-3 pattern in Sample 2: error swallowed"`).
- **As an updater:** when you find a new AP that recurs in three or more documents, add it here.
