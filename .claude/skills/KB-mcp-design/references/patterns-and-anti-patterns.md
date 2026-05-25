# Patterns and Anti-Patterns — MCP Layer Design Catalog

Pattern catalog (✓) + anti-pattern catalog (✗) for MCP layer design. Authored per Plan T2.3.

> **Pedagogical note:** Contains anti-pattern examples (URL-embedded credentials, argv-leaked API keys per C-0259/C-0260/C-0094/E-0094) the auditor flags as DE-2 scanner anti-patterns. These exist to demonstrate what to refuse during review, not what to author.

## Patterns (✓ — do these)

### `.mcp.json` env-block credential indirection

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

The env-var name appears literally; the actual value comes from `containerEnv` (devcontainer.json) → `${localEnv:CONTEXT7_API_KEY}` → Codespaces secret. Per ADR-0039.

**Schema note (post-Phase-5 correction):** Claude Code's `.mcp.json` schema uses **`type`** (not `transport`) for HTTP/SSE servers. `--transport` is the CLI flag name; the serialized file format uses `type`. Earlier drafts of this reference used `transport` and were silently rejected by Claude Code's MCP loader. Verify with `claude mcp add --transport http <name> <url> --scope project` in a scratch directory and inspecting the resulting `.mcp.json` — the serialized form is `"type": "http"`.

### Narrowed per-tool allowlist

```yaml
# .claude/agents/discovery-external-researcher.md frontmatter
tools:
  - mcp__context7__resolve-library-id
  - mcp__context7__query-docs
  - mcp__exa__web_search_exa
  - mcp__exa__company_research_exa
  - mcp__exa__crawling_exa
```

Five explicit tools. Whole-server would expose Context7's experimental tools and Exa's full surface; narrow is the right discipline for an external-research agent.

### Whole-server allowlist for tight tool sets

```yaml
# .claude/agents/design-iac.md frontmatter
tools:
  - mcp__terraform-mcp__*
```

Whole-server allowlist is appropriate when the server's tool set is tight and all-relevant. terraform-mcp exposes a Terraform-reasoning tool set, all relevant to IaC design.

### Pin form variations (one per server type)

```env
# .devcontainer/versions.env
SERENA_REF=v1.2.0                                              # GitHub tag
ACTIONLINT_MCP_SHA=7441fe042c995cbb1bb4b97fce71f9ed3b36d5ef    # GitHub commit SHA
TERRAFORM_MCP_VERSION=0.5.2                                    # HashiCorp release (+ SHA256 in install script)
GITNEXUS_TAG=1.6.5                                              # npm package + version
```

### Primary/fallback registration with event-surface support

When a future feature registers codebase-memory-mcp as the GitNexus fallback per ADR-0007 v2.2.0:

```jsonc
{
  "mcpServers": {
    "gitnexus": { ... },
    "codebase-memory-mcp": { ... }
  }
}
```

Plus `mcp-events.jsonl` records emit `primary_degraded: true` + `fallback_invoked: true` + `fallback_server: "codebase-memory-mcp"` when the primary fails.

## Anti-patterns (✗ — refuse these)

### URL-query embedded credentials (OP-9 BLOCKER)

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

The URL ends up in logs, proxy traces, error messages, and process listings. Per C-0259 / C-0260, URL-query credentials are a known leakage vector. **OP-9 flags this as BLOCKER.**

### argv-passed credentials (OP-10 BLOCKER)

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

`args` array values are visible in `ps`, `/proc/<pid>/cmdline`, container inspection tools. Per C-0094 / E-0094, argv-leaked credentials are a known leakage vector. **OP-10 flags this as BLOCKER.**

### Whole-server allowlist for broad tool surfaces (MAJOR)

```yaml
# .claude/agents/discovery-external-researcher.md frontmatter
tools:
  - mcp__context7__*  # ✗ — exposes experimental tools
  - mcp__exa__*       # ✗ — exposes the full Exa surface
```

When the server has > 2 tools AND the agent only needs a strict subset, whole-server is a MAJOR finding. The fix is to enumerate the specific tools needed.

### Pinning to `latest` (MAJOR)

```env
# .devcontainer/versions.env
GITNEXUS_TAG=latest                  # ✗ — pin to specific version
```

`latest` floats; reproducibility breaks across postCreate runs. **MAJOR finding** per the augmented `auditing-mcp` OP-N reproducibility rule.

### Mixing transports in a single entry (BLOCKER)

```jsonc
{
  "mcpServers": {
    "broken": {
      "transport": "stdio",
      "command": "some-binary",
      "url": "https://example.com/mcp"   // ✗ — both stdio and http
    }
  }
}
```

`.mcp.json` schema rejects this; an entry has stdio (command+args) OR http (url+headers), not both. **BLOCKER** at schema validation.

### Authorization: Bearer for Context7 (non-canonical; pre-cycle-3 framing)

```jsonc
{
  "mcpServers": {
    "context7": {
      "headers": { "Authorization": "Bearer ${CONTEXT7_API_KEY}" }   // ✗ — non-canonical
    }
  }
}
```

The Upstash README canonical form is `CONTEXT7_API_KEY: <value>` (literal header name). Per SF-F3-AUTH-HEADER-1 resolution at cycle-3 (devcontainer-mcp-provisioning-r1), the Bearer form is retired from current design. The non-canonical form may work practically but carries silent-failure risk.

### Server-name typo in agent allowlist (MAJOR)

```yaml
# .claude/agents/some-agent.md frontmatter
tools:
  - mcp__context-7__resolve-library-id   # ✗ — server is `context7`, not `context-7`
```

Tool entries are case- and dash-sensitive. The audit rule grep checks each allowlist entry against the `.mcp.json` server keys; mismatches surface as MAJOR.

## Cross-references

- **`references/principles.md`** — canonical principle catalog.
- **`auditing-mcp` SKILL.md** — OP-1..OP-10 rule catalog (the audit-side enforcement).
- **KB-mcp-platform/references/credential-handling.md** — OP-9/OP-10 detail.
- **ADR-0039** — credential redaction posture.
- **ADR-0040** — Serena narrowed-allowlist precedent.
- **C-0259, C-0260** — URL-query credential leakage research evidence.
- **C-0094, E-0094** — argv-leaked credential research evidence.
- **SF-F3-AUTH-HEADER-1** — Context7 canonical header form resolution.
