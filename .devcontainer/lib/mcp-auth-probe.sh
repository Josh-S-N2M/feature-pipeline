#!/usr/bin/env bash
# .devcontainer/lib/mcp-auth-probe.sh
#
# Supplementary auth probe for Context7 + Exa (the 2 remote-HTTP servers).
# Per Plan T3.2 + ADR-0041 D-0008: postCreate runs with MCP_AUTH_PROBE=1
# (after install, before postStart); postStart runs with MCP_AUTH_PROBE=0
# (avoid burning a rate-limited call every Codespace start).
#
# Usage:
#   MCP_AUTH_PROBE=1 mcp-auth-probe.sh <server>     (run the probe)
#   MCP_AUTH_PROBE=0 mcp-auth-probe.sh <server>     (skipped — emit "skipped" record)
#
# Output: JSON to stdout (same shape as mcp-ping.sh).

set -euo pipefail

LIB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${LIB_DIR}/../.." && pwd)"
MCP_JSON="${REPO_ROOT}/.mcp.json"

# shellcheck disable=SC1091
source "${LIB_DIR}/log-mcp-event.sh"

SERVER="${1:-}"
PROBE_FLAG="${MCP_AUTH_PROBE:-0}"

if [[ -z "${SERVER}" ]]; then
  echo '{"server":"<missing>","result":"fail","failure_layer":"config","latency_ms":0,"message_redacted":"server name not provided","probe":"auth"}'
  exit 0
fi

# Only Context7 + Exa are auth-probed (the HTTP-transport servers with API key auth)
if [[ "${SERVER}" != "context7" && "${SERVER}" != "exa" ]]; then
  jq -n -c --arg s "${SERVER}" \
    '{server:$s, result:"skipped", failure_layer:"none", latency_ms:0, message_redacted:"auth probe only applies to context7 and exa", probe:"auth"}'
  exit 0
fi

if [[ "${PROBE_FLAG}" != "1" ]]; then
  jq -n -c --arg s "${SERVER}" \
    '{server:$s, result:"skipped", failure_layer:"none", latency_ms:0, message_redacted:"MCP_AUTH_PROBE=0; skipping (postStart default per ADR-0041 D-0008)", probe:"auth"}'
  exit 0
fi

# Delegate to mcp-ping.sh — for HTTP servers, ping IS effectively an auth probe
# (it sends the auth header + tools/list; 401/403 = auth fail).
result_json="$(bash "${LIB_DIR}/mcp-ping.sh" "${SERVER}")"

# Annotate with probe:"auth"
echo "${result_json}" | jq -c '. + {probe:"auth"}'
