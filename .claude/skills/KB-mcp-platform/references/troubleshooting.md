# Troubleshooting Catalog — MCP Failure Modes

Per Plan T2.2. Failure → diagnosis → fix mapping for the six named MCP servers (was seven; `mcp-openapi-schema` removed 2026-05-24 per postmortem).

> **Pedagogical note:** Contains anti-pattern examples (URL-query credential, argv-leaked API key) the auditor flags as DE-2 scanner anti-patterns — documenting what to refuse during debug, not what to execute. Also contains base64-shaped retry-token examples in API-error scenarios (e.g., `eyJhbG...` JWT-like strings) as illustrative payloads for `structured_failure` records, not live tokens.

## `claude mcp list` shows fewer than 6 servers

**Diagnosis**: `.mcp.json` syntax issue OR server entries removed.

```bash
jq '.mcpServers | keys' .mcp.json
```

Should return `["actionlint-mcp", "context7", "exa", "gitnexus", "serena", "terraform-mcp"]`. If the array is shorter, the missing servers' entries are absent or `jq` failed (invalid JSON).

**Fix**: restore from `KB-mcp-platform/assets/templates/mcp.json.tmpl` + re-apply your env-var substitutions.

## A stdio server fails to start at postStart

**Diagnosis**: probably an install gap (postCreate failed for that server). Check `mcp-events.jsonl` for an `install_complete` record:

```bash
jq 'select(.event == "install_complete" and .server == "gitnexus")' .claude/runtime/mcp-events.jsonl
```

If no record, postCreate didn't complete that install. Re-run postCreate manually:

```bash
bash .devcontainer/postCreate.sh
```

If install fails persistently, check the install step output. For gitnexus specifically: `GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1` must be exported BEFORE `npm install -g gitnexus@${GITNEXUS_TAG}` per ADR-0041.

## Context7 returns auth errors

**Diagnosis (first)**: `CONTEXT7_API_KEY` is unset or wrong.

```bash
[ -n "$CONTEXT7_API_KEY" ] && echo "set" || echo "UNSET"
```

If UNSET, the Codespaces secret isn't bound. Update the secret at github.com/settings/codespaces and `Rebuild Container` (Cmd-Shift-P → "Codespaces: Rebuild Container").

**Diagnosis (second)**: header form is non-canonical. Per the SF-F3-AUTH-HEADER-1 resolution (cycle-3 D-3.2-completion), Context7 uses the literal header name `CONTEXT7_API_KEY: <value>`, NOT `Authorization: Bearer ${CONTEXT7_API_KEY}`. Check `.mcp.json`:

```bash
jq '.mcpServers.context7.headers' .mcp.json
```

Should be `{"CONTEXT7_API_KEY": "${CONTEXT7_API_KEY}"}`. If it's `{"Authorization": "Bearer ${CONTEXT7_API_KEY}"}`, the design is non-canonical and the server may reject auth.

**Reference**: `references/credential-handling.md` for the full Context7 auth-shape discussion.

## Exa returns auth errors

**Diagnosis**: Exa's auth resolver priority is (1) `exaApiKey` URL-query (REJECTED per OP-9), (2) `Authorization: Bearer` header, (3) `EXA_API_KEY` env var (for stdio mode), (4) `x-api-key` header. Our design uses (4). If (4) returns auth-fail, switch to (2):

```jsonc
{
  "exa": {
    "headers": { "Authorization": "Bearer ${EXA_API_KEY}" }
  }
}
```

URL-query stays REJECTED regardless (OP-9).

## GitNexus emits `primary_degraded` in `mcp-events.jsonl`

**Diagnosis**: GitNexus's stdio process is unhealthy. Could be OOM (exit 137), unhandled exception, or transport-level disconnect.

```bash
jq 'select(.server == "gitnexus" and .primary_degraded == true)' .claude/runtime/mcp-events.jsonl | tail -5
```

If `fallback_invoked: false` (likely, since codebase-memory-mcp is not registered per Gate-4 OI-1), Discovery's code-graph traversals will fail until GitNexus is restored.

**Fix**: restart Claude Code (reloads stdio MCP servers). If the failure recurs, check the GitNexus indexer:

```bash
gitnexus analyze /workspaces/feature-pipeline  # one-time re-index
```

A future feature could register the codebase-memory-mcp fallback to restore Discovery operability during GitNexus outages.

## Redaction-applied alerts in JSONL

A `structured_failure` record with `redaction_applied: true` means the helper saw a credential-shaped value in the substrate and replaced it before append. **This is the intended behavior** (per ADR-0039). The record's `message` field tells you what was attempted.

Example (post-redaction):

```jsonl
{
  "event": "structured_failure",
  "server": "context7",
  "failure_layer": "auth",
  "redaction_applied": true,
  "message": "auth failed; submitted header: CONTEXT7_API_KEY: <REDACTED> (expected token shape: <opaque-token>)"
}
```

**Investigate ONLY if redaction was applied at an UNEXPECTED layer** (e.g., a `readiness_probe` record carries `redaction_applied: true` — that suggests credential-shaped substring in a non-credential field, which is concerning).

## Augmented `auditing-mcp` returns BLOCKER

Per ADR-0043 (hard gate at Gate 6): any BLOCKER halts the orchestrator. The remediation path:

1. Read the audit report (`.claude/skills/auditing-mcp/scripts/audit_mcp.py --with-runtime` output).
2. Resolve the BLOCKER per the report's specific rule (OP-1..OP-10).
3. Re-run the audit. Repeat until clean.
4. Orchestrator resumes Gate 6.

**No operator-bypass is permitted at Gate 6** per ADR-0043 (user rationale: *"MCPs can cause a lot of problems if they are not stable and the system fails silently or the devcontainer and docker fail."*).

## Cross-references

- **references/operator-runbook.md** — routine actions
- **references/credential-handling.md** — OP-9/OP-10 anti-patterns
- **references/mcp-events-jsonl.md** — event schema
- **ADR-0007 v2.2.0** — primary/fallback policy
- **ADR-0037** — event surface
- **ADR-0039** — redaction discipline
- **ADR-0043** — hard-gate semantics
