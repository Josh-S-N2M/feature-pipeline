# T4.2 Execution Result

**Task:** Extend smoke_test_auditing_shared.py with positive + negative coverage for validate_adr_placement
**Status:** COMPLETED
**Phase 4 gate:** PASS

## Files Modified

- `.claude/skills/auditing-shared/scripts/smoke_test_auditing_shared.py`

## What Was Done

Added two test scenarios to the existing smoke test harness:

**Scenario L — positive test (AT-046)**
Runs `validate_adr_placement.py` against the full repo root with `--allowlist .claude/skills/synthesize/references/task-08-replication-corpus/final-output/adrs/` (to exempt the known corpus fixture). Asserts exit code 0, verdict PASS, and empty findings array.

**Scenario M — negative test (AT-052)**
Creates a transient fixture at `working/feature/test-fixture/adrs/ADR-9999-fixture-canonical-only-test.md` with minimal valid ADR frontmatter. Runs the same validator (corpus allowlist only — test-fixture dir not allowlisted). Asserts exit code 2, verdict BLOCK, and that findings contain an entry whose `adr_file` references the fixture path. Cleans up the fixture and parent directory in a `finally` block regardless of assertion outcome.

Also added `REPO_ROOT` and `CORPUS_ALLOWLIST` module-level constants to anchor these tests without hardcoding brittle absolute paths.

## 4-Phase Gate Results

| Phase | Tool | Result |
|-------|------|--------|
| 1 — Static analysis | `ast.parse` | PASS |
| 2 — Build | `python3 -m py_compile` | PASS |
| 3 — Tests | Full smoke suite (13 scenarios) | PASS — 13/13, 0 fail |
| 4 — Final gate | Re-run (same as phase 3) | PASS |

## Smoke Test Output (relevant excerpt)

```
  PASS  L: validate_adr_placement positive — clean repo → exit 0 / PASS / []
  PASS  M: validate_adr_placement negative — feature-scoped ADR → exit 2 / BLOCK / finding

Smoke test: 13 pass / 0 fail
EXIT: 0
```

## Cleanup Verification

`working/feature/test-fixture/` is absent after the test run — confirmed by directory listing.

## Migration Log Row

| T4.2 | .claude/skills/auditing-shared/scripts/smoke_test_auditing_shared.py | extended with positive + negative validate_adr_placement test cases | PASS |
