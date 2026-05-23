#!/usr/bin/env bash
# .devcontainer/lib/mcp-ping.sh
#
# Per-server ping primitive. Per Plan T3.1 + verify-at-execution §H-6 finding:
# `claude mcp ping` subcommand does NOT exist in current Claude Code CLI; this
# script implements the ADR-0041 fallback path (direct JSON-RPC `tools/list`
# probe over stdio for stdio servers, HTTP POST for HTTP servers).
#
# Output: one-line JSON to stdout with shape:
#   { "server": "...", "result": "pass|fail", "failure_layer": "transport|auth|startup|tool|config",
#     "latency_ms": N, "message_redacted": "..." }
#
# Exit codes: 0 always (the result is in the JSON; the orchestrator reads it).
#
# Usage:
#   mcp-ping.sh <server-name>

set -euo pipefail

LIB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${LIB_DIR}/../.." && pwd)"
MCP_JSON="${REPO_ROOT}/.mcp.json"

# Source the log helper (for redaction)
# shellcheck disable=SC1091
source "${LIB_DIR}/log-mcp-event.sh"

SERVER="${1:-}"
if [[ -z "${SERVER}" ]]; then
  echo '{"server":"<missing>","result":"fail","failure_layer":"config","latency_ms":0,"message_redacted":"server name not provided"}'
  exit 0
fi

# Read the server config from .mcp.json
SERVER_CONFIG="$(jq -e -c --arg name "${SERVER}" '.mcpServers[$name] // empty' "${MCP_JSON}" 2>/dev/null || true)"
if [[ -z "${SERVER_CONFIG}" ]]; then
  result_json=$(jq -n -c --arg s "${SERVER}" '{server:$s, result:"fail", failure_layer:"config", latency_ms:0, message_redacted:("server not registered in .mcp.json: " + $s)}')
  echo "${result_json}"
  exit 0
fi

# Transport detection
TRANSPORT="$(echo "${SERVER_CONFIG}" | jq -r 'if .transport == "http" then "http" else "stdio" end')"

start_ms=$(date +%s%3N)

probe_stdio() {
  # Direct JSON-RPC tools/list over stdio
  local cmd args env_block
  cmd="$(echo "${SERVER_CONFIG}" | jq -r '.command // empty')"
  if [[ -z "${cmd}" ]]; then
    echo "config|stdio entry has no command field"
    return 1
  fi
  args="$(echo "${SERVER_CONFIG}" | jq -r '.args // [] | join(" ")')"
  env_block="$(echo "${SERVER_CONFIG}" | jq -r '.env // {} | to_entries | map(.key + "=" + .value) | join(" ")')"

  # Construct JSON-RPC tools/list request
  local req='{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'

  # Run with a 10-second timeout; capture stdout
  local response
  if response="$(echo "${req}" | timeout 10 env ${env_block} ${cmd} ${args} 2>/dev/null | head -1)"; then
    # Check if response is valid JSON-RPC with tools
    if echo "${response}" | jq -e '.result.tools // .result' >/dev/null 2>&1; then
      echo "ok|tools/list returned"
      return 0
    fi
    if echo "${response}" | jq -e '.error' >/dev/null 2>&1; then
      local err
      err="$(echo "${response}" | jq -r '.error.message // "unknown error"')"
      echo "tool|${err}"
      return 1
    fi
    echo "tool|invalid JSON-RPC response shape"
    return 1
  else
    echo "transport|stdio server did not respond within 10s"
    return 1
  fi
}

probe_http() {
  local url headers_block
  url="$(echo "${SERVER_CONFIG}" | jq -r '.url // empty')"
  if [[ -z "${url}" ]]; then
    echo "config|http entry has no url field"
    return 1
  fi

  # Build -H flags from headers object (env-var indirection resolved by shell expansion)
  headers_block="$(echo "${SERVER_CONFIG}" | jq -r '.headers // {} | to_entries | map("-H \"" + .key + ": " + .value + "\"") | join(" ")')"

  # Expand env vars in headers (e.g., ${CONTEXT7_API_KEY})
  headers_block="$(eval "echo \"${headers_block}\"")"

  local req='{"jsonrpc":"2.0","id":1,"method":"tools/list","params":{}}'
  local response http_status
  # shellcheck disable=SC2086
  response="$(eval curl -sS --max-time 10 -w '"\n%{http_code}"' -X POST -H '"Content-Type: application/json"' ${headers_block} -d "'${req}'" "'${url}'" 2>/dev/null || true)"
  http_status="$(echo "${response}" | tail -1)"
  local body
  body="$(echo "${response}" | head -n -1)"

  case "${http_status}" in
    200)
      if echo "${body}" | jq -e '.result' >/dev/null 2>&1; then
        echo "ok|tools/list returned"
        return 0
      fi
      echo "tool|200 but no .result in body"
      return 1
      ;;
    401|403)
      echo "auth|HTTP ${http_status}: credentials rejected"
      return 1
      ;;
    "")
      echo "transport|no response (timeout or connection failure)"
      return 1
      ;;
    *)
      echo "transport|HTTP ${http_status}"
      return 1
      ;;
  esac
}

if [[ "${TRANSPORT}" == "http" ]]; then
  result="$(probe_http || true)"
else
  result="$(probe_stdio || true)"
fi

end_ms=$(date +%s%3N)
latency_ms=$((end_ms - start_ms))

# Parse result into status + message
status_layer="${result%%|*}"
msg="${result#*|}"

if [[ "${status_layer}" == "ok" ]]; then
  result_kind="pass"
  failure_layer="none"
else
  result_kind="fail"
  failure_layer="${status_layer}"
fi

# Apply redaction to the message before embedding in JSON
msg_redacted="$(redact_credentials "$(jq -n --arg m "${msg}" '$m')")"

# Construct final result JSON
jq -n -c \
  --arg s "${SERVER}" \
  --arg r "${result_kind}" \
  --arg fl "${failure_layer}" \
  --argjson lat "${latency_ms}" \
  --arg msg "${msg}" \
  '{server:$s, result:$r, failure_layer:$fl, latency_ms:$lat, message_redacted:$msg}'
