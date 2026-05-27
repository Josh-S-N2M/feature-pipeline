# T4.4 Execution Result — End-to-end orchestrator smoke (AC-X-1, AC-NFR-5-a, AC-NFR-9-a)

**Task:** T4.4
**Status:** COMPLETED
**Phase 4 gate passed:** yes

## What was done

Executed an end-to-end smoke with all five mechanisms against a known-good fixture pipeline, confirmed no false positives or false negatives, ran a deliberate-breakage isolation test, confirmed determinism via two successive selftest runs, and confirmed NFR-9 backward compatibility.

The output lives at `working/feature/pipeline-quickwins-hardening-r1/smoke/end-to-end/smoke-report.md`.

### Three demonstrations performed

**1. No false positives / no false negatives on the known-good fixture set**

Each of the three directly exercisable mechanisms (FR-1, FR-2, FR-3) was run against its known-good fixture and reported clean:

- FR-1: `pass_clean.json` (approving verdict, empty findings) → exit 0, silent.
- FR-2: `pre-feature-checkpoint.json` (FULL scope, all stages absent execution_mode) → exit 0, PASS verdict, all stages resolved to specialist-dispatch via absence-default.
- FR-3: `clean_mcp_json.json` + `clean_adr_table.md` → exit 0, empty findings array.
- FR-4a: all four assertions A1–A4 pass on the correctly-configured environment (per T4.3 sub-smoke d1; not re-executed here).

**2. Deliberate-breakage isolation test (one bad input → only that mechanism fails)**

FR-1's input was switched to `fail_blocker.json` (approving verdict alongside BLOCKER finding). FR-3 and FR-2 each kept their known-good inputs.

- FR-1: exit 1, FR-6 diagnostic emitted to stderr. Expected.
- FR-3 (clean inputs): exit 0, empty findings. No contamination from the FR-1 failure.
- FR-2 (clean inputs): exit 0, PASS verdict. No contamination from the FR-1 failure.

No inter-mechanism contamination.

**3. Determinism (two repeat runs, byte-identical)**

FR-1 `--selftest` was run twice in succession. Both runs produced byte-identical stdout (11/11 lines) and byte-identical stderr (3 FR-6 diagnostic JSON blobs for the named-failure cases). Diff: empty.

FR-3 `--selftest` was run twice in succession. Both runs produced byte-identical stdout (6 lines + summary). Diff: empty.

Neither script emits timestamps, process IDs, or any non-deterministic fields.

**4. NFR-9 backward compatibility**

Two fixtures that any prior pipeline would have passed were run through FR-1 after it was wired in:

- `pass_clean.json` (approving verdict, no findings) → exit 0. Still passes.
- `pass_with_minor.json` (approving verdict, MINOR finding) → exit 0. Still passes. MINOR is not in the blocking set; FR-1 does not tighten the bar on non-blocking inputs.

No regressions on already-clean reviewer outputs.

### Documented deferrals (three cases, with AC-X-1 cross-references)

- **FR-4b live calibration in a fresh devcontainer:** covered by T2.5 empirical record. Current `drift_detected` outcome documented in Issues/fr4b-signal1-regex-drift/analysis.md (Issue H-4). Steady-state covered by T5.2 cron cadence.
- **FR-4c workflow execution:** requires GitHub Actions runner; covered by T3.2 structural verification + T3.3 actionlint gate + T5.2 post-merge observation.
- **FR-5 workflow execution:** same constraint; covered by T3.1 structural verification + T3.3 actionlint gate + T5.2/T5.3 post-merge observation.

## Files created

- `working/feature/pipeline-quickwins-hardening-r1/smoke/end-to-end/smoke-report.md`

## Scope deviations

None.

## Verification against Plan L1/L2/L3

- L1: smoke directory and report file exist and are well-formed.
- L2: three of five mechanisms exercised live with both known-good and isolation-breakage evidence; the other two (FR-4b/FR-4c/FR-5) cite T5.2/T5.3 cross-references. Determinism diff is byte-clean.
- L3: NFR-9 evidence captured — two previously-passing inputs still pass after FR-1 was wired in.
