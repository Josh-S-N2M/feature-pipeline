# Operator Runbook — Routine MCP Actions

Day-to-day operator actions for the MCP layer. Authored per Plan T2.2.

> **Pedagogical note:** Contains example shell commands the auditor may flag (curl pipes, redaction-test patterns, base64-shaped retry-token examples in API-error scenarios). These are reference content for troubleshooting, not executable installers.

## Checking MCP server health

### List registered servers

```bash
claude mcp list
```

Should show the 6 named servers from `.mcp.json`. If a server is missing, check the entry exists and is syntactically valid (`jq '.mcpServers | keys' .mcp.json`).

### Check most recent readiness probes

```bash
tail -n 6 .claude/runtime/mcp-events.jsonl | jq 'select(.event == "readiness_probe")'
```

Returns the most recent 6 `readiness_probe` records (one per server from the most recent postStart). Look for `status: "ok"` on each.

### Inspect a failure

```bash
jq 'select(.event == "structured_failure")' .claude/runtime/mcp-events.jsonl | tail -n 10
```

The 10 most recent failures with their `failure_layer`, `message`, and `redaction_applied` annotation.

## Routine actions

### Restart a degraded stdio server

stdio servers are spawned by Claude Code on demand. To force a restart, restart Claude Code itself (Cmd-Shift-P → "Reload Window" in VS Code; or exit and re-run the CLI).

### Re-run postCreate after install drift

If the install step for an OSS-local server failed at first postCreate (e.g., transient npm registry outage), re-run:

```bash
bash .devcontainer/postCreate.sh
```

Note: postCreate is normally one-shot; it's idempotent in this design — re-running won't break anything but may re-install dependencies. Check `mcp-events.jsonl` for fresh `install_complete` records afterwards.

### Re-run postStart manually

```bash
bash .devcontainer/postStart.sh
```

Emits a fresh batch of 7 `readiness_probe` records.

### Refresh Codespaces secrets locally

If `CONTEXT7_API_KEY` or `EXA_API_KEY` rotates and the Codespace is mid-session:

1. Update the secret at github.com/settings/codespaces.
2. In the Codespace: `gh codespace ssh -c <name>` and run `export CONTEXT7_API_KEY=$(gh secret get CONTEXT7_API_KEY)` (if `gh` CLI is configured).
3. Verify by re-running postStart and checking the next `readiness_probe` for context7 returns `status: "ok"`.

## Verifying redaction is working

To smoke-test redaction-at-source (per ADR-0039):

```bash
echo '{"event":"structured_failure","server":"test","message":"saw sk-FAKE12345abcdef67890 in payload"}' | \
  bash .devcontainer/lib/log-mcp-event.sh --stdin
```

Then check the last record:

```bash
tail -1 .claude/runtime/mcp-events.jsonl | jq .
```

The `sk-FAKE12345abcdef67890` substring should be replaced with `<REDACTED>` and the record should carry `"redaction_applied": true`.

## Augmented `auditing-mcp` invocation

To run the augmented audit (the canonical Gate-6 check per AC-CC-5 + ADR-0043 hard-gate):

```bash
python .claude/skills/auditing-mcp/scripts/audit_mcp.py --with-runtime
```

This invokes OP-1..OP-10 plus the runtime probes (reading `mcp-events.jsonl`). A clean run returns exit 0 + report "no BLOCKER findings." Any BLOCKER halts the orchestrator at Gate 6 per ADR-0043 (hard gate, no operator-bypass).

## When something looks wrong

See `references/troubleshooting.md` for the failure-mode catalog and diagnostic flow.

## Cross-references

- **references/troubleshooting.md** — failure → diagnosis → fix catalog
- **references/lifecycle-hooks.md** — what postCreate / postStart do
- **references/credential-handling.md** — redaction + OP-9/OP-10 discipline
- **ADR-0043** — hard-gate semantics
