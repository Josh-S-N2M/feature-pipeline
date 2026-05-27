# Per-Task Execution Result — T2.3

**Status**: COMPLETED
**Phase 4 gate**: PASSED

## Files Modified

1. `.devcontainer/postCreate.sh`

## Files Created

None.

## Scope Deviations

None.

## Changes Applied

Added the Q-CS-1b stale-calibration banner block to `.devcontainer/postCreate.sh`. The insertion point is immediately after `_fr4a_check` (the FR-4a block T2.2 landed) and before `install_gitnexus`, per spec.

The block consists of:

- `_fr4b_calibration_banner()` function — checks `.claude/runtime/mcp-events.jsonl` for the most-recent `calibration_result` event with `mechanism == "fr-4b-gitnexus-grammar-skip"` and emits one of three outcomes to stderr.
- `_fr4b_calibration_banner || true` call site.

### Three banner variants

**NEVER RUN** — emitted when the events file is absent or contains no `calibration_result` event for the mechanism:
```
[postCreate] FR-4b calibration: NEVER RUN. Run 'gh workflow run gitnexus-grammar-skip-calibration.yml --ref main' OR './.devcontainer/scripts/calibrate-gitnexus-grammar-skip.sh' to retire this banner.
```

**STALE** — emitted when the most-recent event timestamp is older than 14 days (day count interpolated):
```
[postCreate] FR-4b calibration: STALE. Most recent calibration_result event is N days old (threshold: 14). Re-run 'gh workflow run gitnexus-grammar-skip-calibration.yml --ref main'.
```

**Silent** — no output when within the 14-day threshold.

### Compliance points

- Never fail-close: `_fr4b_calibration_banner || true` at the call site; internal `return 0` on all paths; `jq` absence and `date -d` conversion failure both degrade to no-output via `|| return 0`.
- No `mcp-events.jsonl` writes: the function only reads the file, never calls `log_mcp_event` (AC-X-4).
- Three-field framing per Blueprint v2.3 AC-X-4: mechanism + staleness-age-as-offending-state + remedial hint; "rule violated" intentionally absent because no rule is violated.

## 4-Phase Gate

- **Phase 1 (lint/format)**: `bash -n .devcontainer/postCreate.sh` — clean.
- **Phase 2 (build)**: Shell syntax verified; no compilation step applicable.
- **Phase 3 (test)**: L2 grep confirms both banner strings present at correct position. L3 simulation of all three cases:
  - (a) file absent: NEVER RUN banner emitted, exit 0.
  - (b) stale event 30 days old: STALE banner emitted with "30 days old", exit 0.
  - (c) recent event 2 days old: no output, exit 0.
  All three proceed through to `install_gitnexus` without fail-close.
- **Phase 4 (final gate)**: PASSED. `bash -n` clean post-edit.
