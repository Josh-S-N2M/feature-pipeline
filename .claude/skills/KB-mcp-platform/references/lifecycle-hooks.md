# Lifecycle Hooks — postCreate + postStart Runbook

How the MCP layer wires into the devcontainer lifecycle. Authored per Plan T2.2 + ADR-0037 (event surface) + ADR-0041 (install mechanism).

## Lifecycle order (per KB-codespaces-platform)

1. `onCreateCommand` — runs once per container creation. Lightweight version probes only.
2. `updateContentCommand` — NOT used by this feature.
3. `postCreateCommand` — runs once per container creation after `onCreate`. Heavy install work.
4. `postStartCommand` — runs at every container start (including resume from stop). Lightweight readiness probes.
5. `postAttachCommand` — NOT directly used; postAttach behavior covered by user-shell startup.

## Our wiring (per `.devcontainer/devcontainer.json`)

```jsonc
{
  "onCreateCommand": "claude --version && python3 --version && node --version && go version && gh --version",
  "postCreateCommand": ".devcontainer/postCreate.sh",
  "postStartCommand": ".devcontainer/postStart.sh"
}
```

## `postCreate.sh` responsibilities (Plan T3.4)

1. Source `.devcontainer/versions.env` — establishes the 5 OSS-local pins.
2. Install Serena via `uvx --from git+https://github.com/oraios/serena@${SERENA_REF} serena`.
3. Install mcp-openapi-schema via `npm install -g mcp-openapi-schema@${MCP_OPENAPI_SCHEMA_VERSION}` (or run via `npx -y`).
4. Install actionlint-mcp via `go install github.com/hongkongkiwi/actionlint-mcp@${ACTIONLINT_MCP_SHA}`.
5. Install terraform-mcp via `.devcontainer/install/terraform-mcp.sh` (binary + sha256 + gpg).
6. Install gitnexus via `npm install -g gitnexus@${GITNEXUS_TAG}` (with `GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1` exported).
7. Emit one `install_complete` record per OSS-local server to `.claude/runtime/mcp-events.jsonl` (5 records total).
8. Note: context7 and exa are HTTP-transport hosted servers; no install step.

## `postStart.sh` responsibilities (Plan T3.5)

1. For each of the 7 registered servers in `.mcp.json`, probe readiness:
   - If `claude mcp ping <server>` is available (per verify-at-execution §H-6), use it.
   - Else fall back to direct JSON-RPC `tools/list` per ADR-0041 (cycle-3 T0.6 verified `claude mcp ping` is NOT available in current Claude Code CLI — fallback applies).
2. Emit one `readiness_probe` record per server to `.claude/runtime/mcp-events.jsonl` (7 records per postStart).
3. Each record has `status: ok | degraded | unreachable` + a `latency_ms` field + optional `error` field for non-ok.
4. The script SHOULD NOT fail-closed on any single server's degradation — emit the record and continue (postStart must complete to make the Codespace usable).

## Cross-script discipline

- Both `postCreate.sh` and `postStart.sh` use the helper at `.devcontainer/lib/log-mcp-event.sh` for JSONL emission (per Plan T3.6).
- The helper applies redaction-at-source per ADR-0039: any header/env-var value matching a credential-shaped pattern (`api[-_]?key`, `token`, `bearer`, etc.) is replaced with `<REDACTED>` before the JSONL record is appended.
- The helper is idempotent on repeated postStart invocations (Codespace resume): the JSONL file is append-only; the 7 `readiness_probe` records add per cycle, the consumer reads the most recent batch.

## Stderr surfacing for degraded states

When the primary server degrades (e.g., GitNexus crashes mid-session), the helper emits the structured failure to `mcp-events.jsonl` AND writes a one-line banner to stderr per ADR-0037:

```
[mcp:gitnexus] primary degraded → falling back to <fallback>; see .claude/runtime/mcp-events.jsonl
```

This is the only stderr surface the helper uses — verbose error chatter goes to the JSONL file, not the terminal.

## Cross-references

- **ADR-0037** — `mcp-events.jsonl` event surface.
- **ADR-0039** — credential redaction at the helper.
- **ADR-0041** — install-mechanism hybrid (per-server installer tools) + JSON-RPC ping fallback when `claude mcp ping` is absent.
- **KB-codespaces-platform** — lifecycle hook ordering + composition.
- **Plan T3.4, T3.5, T3.6** — implementation tasks for these scripts.
- **verify-at-execution.md §H-6** — Phase 0 finding that `claude mcp ping` is unavailable in current Claude Code CLI.
