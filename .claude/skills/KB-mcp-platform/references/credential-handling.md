# Credential Handling — Redact-At-Source Discipline

## Contents

- The discipline
- Anti-patterns the auditor flags
- The five servers auth shapes (after compliant patterns applied)
- Redaction at the JSONL helper (per ADR-0039)
- Cross-references


Per **ADR-0039** (credential redaction posture). All MCP credentials must enter the runtime via env-block indirection from Codespaces secrets; never via URL-query parameters (OP-9) or argv-passed flags (OP-10).

> **Pedagogical note:** This document contains anti-pattern examples showing URL-query embedded API keys and argv-passed API keys. These exist to demonstrate what to REFUSE during audit, not what to execute. The example credential values use placeholder strings (e.g., `sk-...`, `eyJhbG...`) that are obvious placeholders, not real secrets.

## The discipline

Credentials enter `.mcp.json` ONLY via env-block indirection. The shape:

```jsonc
{
  "mcpServers": {
    "context7": {
      "type": "http",
      "url": "https://mcp.context7.com/mcp",
      "headers": { "CONTEXT7_API_KEY": "${CONTEXT7_API_KEY}" }
    }
  }
}
```

The env-var name (`CONTEXT7_API_KEY`) appears literally in `.mcp.json`. The actual value is sourced from `containerEnv` (devcontainer.json) which in turn sources from Codespaces secrets via `${localEnv:CONTEXT7_API_KEY}`.

**Schema note (cycle-3 D-3.2-completion + Phase 5 post-rebuild correction):** Claude Code's `.mcp.json` schema uses the field name **`type`** for HTTP/SSE servers (not `transport`). The CLI flag is `--transport http` — that's the flag name. The serialized file format uses `type`. Earlier drafts of this template used `transport` and were silently rejected by Claude Code's MCP loader. Verify with `claude mcp add --transport http <name> <url> --scope project` in a scratch directory and inspecting the resulting `.mcp.json` — the serialized form is `"type": "http"`.

## Anti-patterns the auditor flags

### OP-9 BLOCKER — URL-query embedded credentials

**REFUSE this shape:**

```jsonc
{
  "mcpServers": {
    "context7": {
      "type": "http",
      "url": "https://mcp.context7.com/mcp?apiKey=sk-...REPLACED...",
      "headers": {}
    }
  }
}
```

Reasons it's a BLOCKER:
- URLs are logged everywhere (proxies, browser histories, server access logs, HTTP-debug tooling).
- URLs appear in error messages and exception traces.
- URLs in process listings (`ps`, `/proc/`) are not redacted.
- Once leaked, the credential is in many logs simultaneously.

The augmented `auditing-mcp` rule **OP-9** flags any `url` containing `apiKey=`, `api_key=`, `token=`, `Bearer%20` (URL-encoded space), or any query parameter matching a credential-shaped pattern.

### OP-10 BLOCKER — argv-passed credentials

**REFUSE this shape:**

```jsonc
{
  "mcpServers": {
    "exa": {
      "command": "npx",
      "args": ["-y", "exa-mcp-server", "--api-key", "sk-eyJ...REPLACED..."]
    }
  }
}
```

Reasons it's a BLOCKER:
- `args` array values are visible in `ps`, `/proc/<pid>/cmdline`, container inspection tools.
- They appear in process trees and audit logs.
- Container runtimes (Docker, runc, containerd) often log launched commands verbatim.

The augmented `auditing-mcp` rule **OP-10** flags any `args` element matching `--api-key`, `--apikey`, `--api_key`, `--token`, `--auth`, `--bearer`, or a positional argument that looks like a credential (long string with `sk-`, `eyJ`, `ghp_`, etc. prefixes).

## The five servers' auth shapes (after compliant patterns applied)

| Server | Auth method | env-var name | Where it enters .mcp.json |
|---|---|---|---|
| actionlint-mcp | none | — | — |
| context7 | `CONTEXT7_API_KEY` header (canonical per Upstash README) | `CONTEXT7_API_KEY` | `headers: {"CONTEXT7_API_KEY": "${CONTEXT7_API_KEY}"}` |
| exa | `x-api-key` header | `EXA_API_KEY` | `headers: {"x-api-key": "${EXA_API_KEY}"}` |
| serena | none | — | — |
| terraform-mcp | optional `TFE_TOKEN` (local-only is no-auth) | `TFE_TOKEN` | `env: {"TFE_TOKEN": "${TFE_TOKEN}"}` (optional block) |

## Redaction at the JSONL helper (per ADR-0039)

The `.devcontainer/lib/log-mcp-event.sh` helper redacts credential-shaped values from any record before appending to `.claude/runtime/mcp-events.jsonl`. The redaction pattern matches:

- Header values with names matching `api[-_]?key|token|bearer|auth|credential` (case-insensitive)
- Substring patterns `sk-[A-Za-z0-9_-]{16,}`, `eyJ[A-Za-z0-9_-]{8,}`, `ghp_[A-Za-z0-9]{16,}`
- Any env-var dereference that resolved to a value matching the above

When redacted, the value is replaced with `<REDACTED>` (literal) and the record gains a `redaction_applied: true` annotation.

## Cross-references

- **ADR-0039** — full redaction posture rationale.
- **OP-9 / OP-10** — see `auditing-mcp` SKILL.md for the full rule catalog.
- **references/seven-named-servers.md** — per-server auth detail.
- **references/mcp-events-jsonl.md** — event surface schema.
- **SF-F3-AUTH-HEADER-1** (resolved cycle-3) — Context7 canonical header form.
