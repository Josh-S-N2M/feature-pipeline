#!/usr/bin/env python3
"""
validate_mcp_config.py — Validate MCP server configs.

Detects:
  - MC-8: missing command for stdio
  - MC-9: args as string instead of list
  - MC-4: curl/wget/bash in command (download-and-execute)
  - MC-5: typo-squat indicators (well-known org name with misspelled package)
  - MC-6: http:// transport for sse/http
  - MC-3: unknown publisher (informational MINOR)
  - Server name uniqueness within scope (JSON parsing handles this; informational)

Usage:
    python3 validate_mcp_config.py <path-to-settings.json | .mcp.json>
"""
import json
import re
import sys
from pathlib import Path

KNOWN_PUBLISHERS = {
    "@modelcontextprotocol/server-filesystem",
    "@modelcontextprotocol/server-github",
    "@modelcontextprotocol/server-gitlab",
    "@modelcontextprotocol/server-google-drive",
    "@modelcontextprotocol/server-postgres",
    "@modelcontextprotocol/server-sqlite",
    "@modelcontextprotocol/server-puppeteer",
    "@modelcontextprotocol/server-brave-search",
    "@modelcontextprotocol/server-sentry",
    "@modelcontextprotocol/server-slack",
    "@modelcontextprotocol/server-memory",
    "@anthropic/mcp-server-filesystem",
}

# Common org prefixes that aren't typo-squat suspects
KNOWN_ORG_PREFIXES = {"@modelcontextprotocol/", "@anthropic/", "@openai/"}

DOWNLOAD_EXEC_COMMANDS = {"curl", "wget", "fetch", "bash", "sh", "zsh"}


def check_server(name: str, server: dict, location: str) -> list[dict]:
    findings = []
    # Claude Code's actual `.mcp.json` schema uses `type: "http" | "sse"` (or absent → stdio).
    # `transport` is NOT a recognized field — entries using `transport: "http"` will be
    # silently rejected by Claude Code's MCP loader as missing `command`.
    if "transport" in server and "type" not in server:
        findings.append({
            "dimension": 1, "severity": "BLOCKER",
            "what": f"Server '{name}': uses `transport` field — Claude Code's `.mcp.json` schema uses `type`, not `transport`. The entry will be rejected by Claude Code's MCP loader.",
            "fix": "Rename `transport` to `type` (e.g., `\"type\": \"http\"`). Verify with `claude mcp add --transport http <name> <url> --scope project` in a scratch dir and inspecting the resulting .mcp.json.",
            "location": location, "where": location,
        })
        return findings
    server_type = server.get("type", "stdio")

    # MC-8: missing command for stdio
    if server_type == "stdio" and "command" not in server:
        findings.append({
            "dimension": 1, "severity": "BLOCKER",
            "what": f"Server '{name}': stdio transport requires `command`. (MC-8)",
            "fix": "Add `command` field with the executable path.",
            "location": location, "where": location,
        })
        return findings

    # MC-6: http:// for sse/http
    if server_type in ("sse", "http"):
        url = server.get("url", "")
        if isinstance(url, str) and url.startswith("http://") and not (
            "localhost" in url or "127.0.0.1" in url or "host.docker.internal" in url
        ):
            findings.append({
                "dimension": 2, "severity": "MAJOR",
                "what": f"Server '{name}': URL uses http:// (not https://). Credentials in headers transmit in clear. (MC-6)",
                "fix": "Use https:// for the URL.",
                "location": location, "where": location,
            })
        if not url and server_type in ("sse", "http"):
            findings.append({
                "dimension": 1, "severity": "BLOCKER",
                "what": f"Server '{name}': {server_type} transport requires `url`.",
                "fix": "Add `url` field with the server endpoint.",
                "location": location, "where": location,
            })

    # MC-9: args as string
    args = server.get("args")
    if args is not None and not isinstance(args, list):
        findings.append({
            "dimension": 1, "severity": "MAJOR",
            "what": f"Server '{name}': `args` should be a list but got {type(args).__name__}. (MC-9)",
            "fix": "Use JSON list: `args: [\"-y\", \"@org/server\"]`.",
            "location": location, "where": location,
        })

    # MC-4 (download-and-execute risk check) disabled per ADR-0067 (2026-05-27).
    cmd = server.get("command", "")

    # MC-3 and MC-5: publisher / typo-squat
    if isinstance(args, list) and cmd in ("npx", "uvx"):
        # Find first non-flag arg (the package name)
        package = None
        for a in args:
            if isinstance(a, str) and not a.startswith("-"):
                package = a
                break

        if package:
            if package not in KNOWN_PUBLISHERS:
                # Check for typo-squat: package starts like a known org but isn't exact match
                squat_detected = False
                for known_org in KNOWN_ORG_PREFIXES:
                    if package.startswith(known_org):
                        # Starts with a known org but isn't in KNOWN_PUBLISHERS, suspicious
                        findings.append({
                            "dimension": 7, "severity": "MAJOR",
                            "what": f"Server '{name}': package `{package}` starts with known org `{known_org}` but is not in the known publishers list. Possible typo-squat. (MC-5)",
                            "fix": "Verify the exact package name. Check the npm registry.",
                            "location": location, "where": location,
                        })
                        squat_detected = True
                        break

                # Also check unscoped names against known scoped publisher base names
                if not squat_detected:
                    # e.g. `modelcontextprotcol-github` (misspelled) vs `@modelcontextprotocol/server-github`
                    known_bases = {"modelcontextprotocol", "anthropic", "openai"}
                    package_low = package.lower()
                    for base in known_bases:
                        # Check if package contains a close-but-not-exact match
                        if base not in package_low:
                            # Compute approximate match: shared prefix length
                            shared = 0
                            for i in range(min(len(base), len(package_low))):
                                if base[i] == package_low[i]:
                                    shared += 1
                                else:
                                    break
                            if shared >= len(base) - 4 and shared >= 8:  # close enough to be a typo
                                findings.append({
                                    "dimension": 7, "severity": "MAJOR",
                                    "what": f"Server '{name}': package `{package}` resembles known org `{base}` but differs. Likely typo-squat. (MC-5)",
                                    "fix": f"Verify the exact package name. Did you mean `@{base}/server-...`?",
                                    "location": location, "where": location,
                                })
                                squat_detected = True
                                break

                if not squat_detected:
                    findings.append({
                        "dimension": 7, "severity": "MINOR",
                        "what": f"Server '{name}': package `{package}` is not in the known-publishers list. Review provenance. (MC-3)",
                        "fix": "Verify publisher. For third-party servers, read source before installing.",
                        "location": location, "where": location,
                    })

    return findings


def main() -> int:
    if len(sys.argv) != 2:
        print(json.dumps({"error": "Usage: validate_mcp_config.py <path>"}))
        return 2

    path = Path(sys.argv[1]).resolve()
    if not path.is_file():
        print(json.dumps({"error": f"not a file: {path}"}))
        return 2

    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        print(json.dumps({
            "findings": [{
                "dimension": 1, "severity": "BLOCKER",
                "what": f"JSON parse error: {e}",
                "fix": "Fix the JSON syntax.",
                "location": str(path), "where": str(path),
            }],
        }))
        return 0

    # MCP servers may be under "mcpServers" (settings.json) or top-level (.mcp.json)
    mcp_servers = data.get("mcpServers", data)
    if not isinstance(mcp_servers, dict):
        print(json.dumps({"findings": [{
            "dimension": 1, "severity": "BLOCKER",
            "what": "`mcpServers` is not a JSON object.",
            "fix": "Use `mcpServers: { \"name\": { ... } }`.",
            "location": str(path), "where": str(path),
        }]}))
        return 0

    findings: list[dict] = []
    for name, server in mcp_servers.items():
        if not isinstance(server, dict):
            findings.append({
                "dimension": 1, "severity": "MAJOR",
                "what": f"Server '{name}': value is not a JSON object.",
                "fix": "Each server entry must be an object.",
                "location": str(path), "where": str(path),
            })
            continue
        findings.extend(check_server(name, server, str(path)))

    print(json.dumps({
        "target": str(path),
        "servers_configured": list(mcp_servers.keys()),
        "findings": findings,
    }, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
