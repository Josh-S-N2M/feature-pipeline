# Q-CS-1b Banner Integration Smoke Report

**Task:** T4.5  
**Date run:** 2026-05-27  
**Approach:** Option B — standalone test script sources the `_fr4b_calibration_banner` function body and accepts a fixture path argument. Three fixture directories each contain an `mcp-events.jsonl` file pre-populated to represent a distinct banner state. The script is run once per fixture; stderr and exit code are captured and checked against the expected behaviour.

---

## Fixture layout

```
smoke/qcs1b/
  run-banner-smoke.sh          standalone test harness (verbatim banner logic, path-argument override)
  never-run/mcp-events.jsonl   no calibration_result event for the mechanism
  stale/mcp-events.jsonl       calibration_result event timestamped 2026-05-06T02:41:19Z  (21 days before run)
  fresh/mcp-events.jsonl       calibration_result event timestamped 2026-05-24T02:41:22Z  (3 days before run)
```

---

## Fixture i — `never-run`

**File:** `never-run/mcp-events.jsonl`  
**Contents:** two `install_complete` events; no `calibration_result` event for mechanism `fr-4b-gitnexus-grammar-skip`.

**Expected:** stderr contains `NEVER RUN`, exit 0.

**Observed stderr:**
```
[postCreate] FR-4b calibration: NEVER RUN. Run 'gh workflow run gitnexus-grammar-skip-calibration.yml --ref main' OR './.devcontainer/scripts/calibrate-gitnexus-grammar-skip.sh' to retire this banner.
```

**Observed exit code:** 0

**Result: PASS** — output contains `NEVER RUN`, exits 0.

---

## Fixture ii — `stale`

**File:** `stale/mcp-events.jsonl`  
**Contents:** one `calibration_result` event for `fr-4b-gitnexus-grammar-skip` with `timestamp: 2026-05-06T02:41:19Z` (21 days before the run date; threshold is 14 days).

**Expected:** stderr contains `STALE` and the age count (number of days), exit 0.

**Observed stderr:**
```
[postCreate] FR-4b calibration: STALE. Most recent calibration_result event is 21 days old (threshold: 14). Re-run 'gh workflow run gitnexus-grammar-skip-calibration.yml --ref main'.
```

**Observed exit code:** 0

**Result: PASS** — output contains `STALE` and `21 days old`, exits 0.

---

## Fixture iii — `fresh`

**File:** `fresh/mcp-events.jsonl`  
**Contents:** one `calibration_result` event for `fr-4b-gitnexus-grammar-skip` with `timestamp: 2026-05-24T02:41:22Z` (3 days before the run date; within the 14-day threshold).

**Expected:** stderr is silent (no output), exit 0.

**Observed stderr:** *(empty)*

**Observed exit code:** 0

**Result: PASS** — no stderr output, exits 0.

---

## Summary

| Fixture     | Expected stderr           | Observed                                | Exit | Result |
|-------------|---------------------------|-----------------------------------------|------|--------|
| `never-run` | contains `NEVER RUN`      | `[postCreate] FR-4b calibration: NEVER RUN. ...` | 0    | PASS   |
| `stale`     | contains `STALE` + age    | `[postCreate] FR-4b calibration: STALE. Most recent calibration_result event is 21 days old ...` | 0    | PASS   |
| `fresh`     | silent (no output)        | *(empty)*                               | 0    | PASS   |

**3 / 3 passed.**

---

## Verification against Plan L1/L2/L3

**L1:** Three fixture directories exist with their JSONL files.
- `smoke/qcs1b/never-run/mcp-events.jsonl` — present.
- `smoke/qcs1b/stale/mcp-events.jsonl` — present, contains `calibration_result` event at `2026-05-06T02:41:19Z`.
- `smoke/qcs1b/fresh/mcp-events.jsonl` — present, contains `calibration_result` event at `2026-05-24T02:41:22Z`.

**L2:** Banner function invoked three times; outputs match expected per fixture.
- All three confirmed in the table above.

**L3:** All three exits 0. Informational discipline honored — the banner never causes a non-zero exit regardless of calibration state.
- Confirmed: every invocation exited 0.

---

## Notes on test method

The test script (`run-banner-smoke.sh`) is a verbatim copy of the `_fr4b_calibration_banner` body from `.devcontainer/postCreate.sh` with one change: the events file path comes from `$1` (the first argument) rather than being derived from `${SENTINEL_DIR}`. This is the simplest possible faithful test that avoids sourcing the full `postCreate.sh` (which would require `jq`, `log-mcp-event.sh`, `versions.env`, and other dependencies present only in a devcontainer).

The banner logic is **informational only**. All three variants return exit 0, consistent with AC-X-4 (never fail-close) and the `|| true` guard on the call site in `postCreate.sh` (line 324).
