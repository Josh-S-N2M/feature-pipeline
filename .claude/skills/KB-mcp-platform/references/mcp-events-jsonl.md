# `mcp-events.jsonl` — Event Surface Schema

Per **ADR-0037**. Canonical event surface for MCP lifecycle and runtime events. Per-Codespace, never committed (per `.gitignore`).

## File location

`.claude/runtime/mcp-events.jsonl`

Created (empty) at `.claude/runtime/.gitkeep` Phase-0 bootstrap per Plan T0.10. Grows from postCreate onward; survives Codespace restarts (it lives on the persistent workspace volume).

## Format

One JSON object per line (JSONL). Append-only. Records are immutable once written. Schema below.

## Four event types

### `install_complete`

Emitted once per OSS-local server install (5 records per postCreate run; context7 + exa are HTTP-transport with no install step).

```jsonl
{
  "event": "install_complete",
  "timestamp": "2026-05-23T21:30:00Z",
  "server": "gitnexus",
  "install_method": "npm",
  "version": "1.6.5",
  "duration_ms": 57430,
  "status": "ok"
}
```

Fields:
- `event`: literal `install_complete`
- `timestamp`: ISO 8601 UTC
- `server`: one of the 4 OSS-local server names (actionlint-mcp, gitnexus, serena, terraform-mcp). The 2 HTTP servers (context7, exa) do not emit this event.
- `install_method`: `npm` | `uvx` | `go install` | `binary-download`
- `version`: pin string from versions.env
- `duration_ms`: elapsed time
- `status`: `ok` | `failed` (failed emits structured_failure too)

### `readiness_probe`

Emitted once per registered server at every postStart run (6 records per cycle for the 6 named servers).

```jsonl
{
  "event": "readiness_probe",
  "timestamp": "2026-05-23T21:31:00Z",
  "server": "context7",
  "probe_method": "json-rpc-tools-list",
  "latency_ms": 142,
  "status": "ok"
}
```

Fields:
- `event`: literal `readiness_probe`
- `timestamp`: ISO 8601 UTC
- `server`: one of the 6 registered server names
- `probe_method`: `claude-mcp-ping` (if CLI available) | `json-rpc-tools-list` (per ADR-0041 fallback when `claude mcp ping` is absent per cycle-3 T0.6 verify)
- `latency_ms`: end-to-end latency
- `status`: `ok` | `degraded` | `unreachable`
- `error`: optional error message string for `degraded` / `unreachable`

### `structured_failure`

Emitted on any MCP error condition: auth-fail, timeout, redaction-applied event, primary-degraded fallback invocation, etc.

```jsonl
{
  "event": "structured_failure",
  "timestamp": "2026-05-23T21:32:15Z",
  "server": "gitnexus",
  "failure_layer": "transport",
  "primary_degraded": true,
  "fallback_invoked": false,
  "fallback_server": null,
  "redaction_applied": false,
  "message": "GitNexus stdio process exited with code 137 (likely OOM); restart attempt 1/3"
}
```

Fields:
- `event`: literal `structured_failure`
- `timestamp`: ISO 8601 UTC
- `server`: server name (or `<unknown>` if pre-handshake)
- `failure_layer`: `transport` | `auth` | `tool` | `install` | `runtime` | `unknown`
- `primary_degraded`: boolean — true if this is the primary in a primary/fallback pair (e.g., GitNexus per ADR-0007 v2.2.0)
- `fallback_invoked`: boolean — true if the fallback was actually called
- `fallback_server`: string or null — name of the fallback if invoked
- `redaction_applied`: boolean — true if the helper redacted any credential-shaped values from this record's substrate
- `message`: one-line human-readable summary

### `calibration_result`

Emitted by FR-4b calibration mechanisms (per ADR-0058, the additive extension to ADR-0037 v1.0.2).

```jsonl
{"event": "calibration_result", "timestamp": "2026-05-26T08:15:00Z", "server": "gitnexus", "mechanism": "fr-4b-gitnexus-grammar-skip", "version": "1.6.5", "duration_ms": 3210, "outcome": "pass", "signals": {"signal_1_stderr_match_dart": "pass", "signal_1_stderr_match_proto": "pass", "signal_3_artifact_absence_dart": "pass", "signal_3_artifact_absence_proto": "pass", "negative_assertion_artifacts_built": "pass"}, "note": "All grammar-skip signals confirmed for gitnexus@1.6.5"}
```

Fields:
- `event`: literal `calibration_result`
- `timestamp`: ISO 8601 UTC
- `server`: server being calibrated (e.g., `gitnexus`)
- `mechanism`: namespace discriminator — distinguishes multiple calibration sources in the same event surface; current value `fr-4b-gitnexus-grammar-skip` for the GitNexus contract verification. Future calibration mechanisms use a different namespace string; consumers filtering on `signals.*` sub-fields should check `mechanism:` first.
- `version`: server version or tag string under test
- `duration_ms`: elapsed time for the calibration run
- `outcome`: `pass` | `fail` | `drift_detected`
- `signals`: map of per-mechanism signal names to `pass` | `fail` | `skipped`; keys are mechanism-specific (discriminated by `mechanism:`)
- `note`: one-line human-readable summary; includes a remedial hint on `fail` or `drift_detected`

## Bootstrap semantics

Per ADR-0037 Implementation Guidance, the bootstrap produces **six `readiness_probe` records** (one per named server; the 2026-05-23 cycle-3 OI-1 closure dropped the eighth previously-planned record for the codebase-memory-mcp fallback that's no longer registered; the 2026-05-24 postmortem then dropped the seventh planned record by removing `mcp-openapi-schema`). Per AC-X-2.

## Consumer agents

- `discovery-codebase-researcher` reads the most recent `structured_failure` records before invoking GitNexus traversals to detect primary-degraded conditions (per ADR-0007 v2.2.0 + ADR-0037).
- Operators read the JSONL during troubleshooting (see `references/operator-runbook.md`).
- The augmented `auditing-mcp` skill family reads the JSONL during runtime audits (`--with-runtime` mode) to verify schema conformance + redaction discipline.

## Cross-references

- **ADR-0037** — full schema + bootstrap semantics; establishes the three pre-existing event types.
- **ADR-0058** — additive extension adding the fourth event type (`calibration_result`); canonical payload shape and `mechanism:` discriminator discipline.
- **ADR-0039** — credential redaction discipline.
- **ADR-0007 v2.2.0** — primary_degraded provenance.
- **Plan T3.6** — `.devcontainer/lib/log-mcp-event.sh` helper authoring task.
- **PV-3.* (phase-validators)** — JSONL schema conformance checks at Gate 5.
