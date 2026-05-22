# Good MCP: Annotated Example (95+/100)

## Contents

- The config
- Per-dimension findings
- Verdict

## The config

A well-formed MCP config block in settings.json:

```audit-example -- positive-example annotated fixture demonstrating scanner-flagged content; documents what the auditor scanner detects
{
  "mcpServers": {
    "filesystem": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-filesystem", "/Users/me/projects"]
    },
    "github": {
      "type": "stdio",
      "command": "npx",
      "args": ["-y", "@modelcontextprotocol/server-github"],
      "env": {
        "GITHUB_PERSONAL_ACCESS_TOKEN": "${GITHUB_TOKEN}"
      }
    }
  }
}
```

## Per-dimension findings

### Dimension 1: Config schema validity — 10/10
Both servers have required fields. `args` is a list. `command` is present.

### Dimension 2: Transport choice — 10/10
Both use stdio (the default and most reliable).

### Dimension 3: Credential handling — 10/10
`GITHUB_PERSONAL_ACCESS_TOKEN` references env var `${GITHUB_TOKEN}`.

### Dimension 4: Server-name uniqueness — 10/10
Two distinct names. No collision.

### Dimension 5: Toxic capability combinations — 10/10
Each server has a single, focused capability. No combination flagged.

### Dimension 6: Tool-description safety — N/A (static audit)
Cannot check without runtime mode. Note: assumed safe based on publisher reputation.

### Dimension 7: Supply-chain provenance — 10/10
Both packages from `@modelcontextprotocol/*` — the official MCP publisher.

### Dimension 8: Anti-pattern absence — 10/10
None of MC-1 through MC-10 present.

### Dimension 9: Cross-scope interactions — N/A
No multi-scope visibility from this single file.

### Dimension 10: Runtime behavior — N/A (--with-runtime not invoked)

## Total: 100/100 — PASS

## What this calibrates

- Single-capability servers (filesystem-only, github-only) are the safe pattern.
- Official `@modelcontextprotocol/*` packages get the trusted-publisher pass.
- `${VAR}` references for credentials.
- stdio is the recommended default.

## Optional: --with-runtime mode

When invoked with `--with-runtime`, the auditor would:
1. Spawn each server.
2. Query `tools/list`.
3. Verify the server's actual tools match the publisher's documented capabilities.
4. Scan tool descriptions for injection patterns.

The runtime check produces an INFO-level addendum to this static audit, since the static audit already scored 100.
