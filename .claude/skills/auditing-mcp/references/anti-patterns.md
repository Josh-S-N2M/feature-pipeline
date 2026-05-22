# MCP Anti-Patterns

## Contents

- 10 named MCP anti-patterns (MC-1 through MC-10)
- Detection map

## MC-1: Literal credential in env — BLOCKER (security_critical)

Symptom: server's `env` block has a real-looking credential value.

```audit-example -- anti-pattern catalog demonstrating scanner-flagged content; documents what the auditor scanner detects
{
  "env": { "GITHUB_PAT": "ghp_actualValue..." }
}
```

Why bad: Credential committed to config.

Fix: Use `${VAR}` reference.

## MC-2: Toxic combination by name — MAJOR (BLOCKER with runtime confirmation)

Symptom: server name combines two risky capabilities (filesystem + web, etc.).

Why bad: Single server can chain exfiltration.

Fix: Use separate servers; review which combo is needed.

## MC-3: Unknown publisher — MINOR

Symptom: `npx <package>` where `<package>` is not in the well-known publishers list.

Why bad: Supply-chain risk.

Fix: Verify the publisher; check the package source.

## MC-4: curl/wget in command — BLOCKER (security_critical)

Symptom: `command: "curl"`, `command: "bash"` with pipe.

Why bad: Download-and-execute pattern.

Fix: Use a published MCP server package.

## MC-5: Typo-squat indicator — BLOCKER

Symptom: server name matches a famous publisher (e.g. "modelcontextprotocol") but the actual package in `args` is a slight misspelling.

```audit-example -- anti-pattern catalog demonstrating scanner-flagged content; documents what the auditor scanner detects
{
  "name": "modelcontextprotocol-github",
  "command": "npx",
  "args": ["-y", "modelcontextprotcol-github"]    // misspelled
}
```

Why bad: Likely typo-squat package.

Fix: Verify exact package name.

## MC-6: http:// transport — MAJOR

Symptom: `type: "sse"` or `"http"` with `url: "http://..."` (not https, not localhost).

Why bad: Network credentials sent in clear.

Fix: Use https://.

## MC-7: Headers with literal credentials — BLOCKER (security_critical)

Symptom: `headers: { "Authorization": "Bearer abc123actualToken..." }`.

Why bad: Same as MC-1 but for HTTP transports.

Fix: Use `${VAR}` reference in headers.

## MC-8: Missing command for stdio — BLOCKER

Symptom: `type: "stdio"` (default) but no `command` field.

Why bad: Server can't be launched.

Fix: Add the command path.

## MC-9: `args` is a string instead of list — MAJOR

Symptom: `args: "-y @org/server foo"` instead of `args: ["-y", "@org/server", "foo"]`.

Why bad: Treated as a single arg; the command fails.

Fix: Use a JSON list.

## MC-10: Server name shadowed across scopes — MINOR

Symptom: same server name configured at multiple scopes.

Why bad: Higher-scope wins silently.

Fix: Choose one canonical scope.

## Detection map

| Pattern | Detected by |
|---|---|
| MC-1, MC-7 | `scripts/scan_mcp_secrets.py` (env + headers credential scan) |
| MC-2 | `scripts/check_toxic_combinations.py` (name heuristic) + runtime mode |
| MC-3 | `scripts/validate_mcp_config.py` (publisher allow-list check) |
| MC-4 | `scripts/validate_mcp_config.py` (command allow-list) |
| MC-5 | `scripts/validate_mcp_config.py` (typo-squat heuristic) |
| MC-6 | `scripts/validate_mcp_config.py` (transport check) |
| MC-8 | `scripts/validate_mcp_config.py` (required-field check) |
| MC-9 | `scripts/validate_mcp_config.py` (args type check) |
| MC-10 | cross-file check (in project mode, multi-scope visibility) |
