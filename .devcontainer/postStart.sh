#!/usr/bin/env bash
# .devcontainer/postStart.sh
#
# Per Plan T3.5. Runs at every container start (including resume from stop).
# Emits exactly 7 readiness_probe JSONL records per cycle — one per server in
# .mcp.json. Per AC-X-2 (7 readiness_probe records bootstrap semantics).
#
# Per ADR-0041 D-0008: postStart runs with MCP_AUTH_PROBE=0 (avoid burning a
# rate-limited call on every Codespace start; postCreate's auth probe is the
# primary verification).
#
# Per §D-6 resolution (plan T3.5): postAttach staleness threshold = 5 minutes.
# postStart emits the readiness_probe records and writes a staleness timestamp;
# postAttach (user shell startup) reads the most-recent records if fresh (<5min)
# OR triggers a fresh probe if stale.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
LIB_DIR="${SCRIPT_DIR}/lib"

# shellcheck disable=SC1091
source "${LIB_DIR}/log-mcp-event.sh"

MCP_JSON="${REPO_ROOT}/.mcp.json"
RUNTIME_DIR="${REPO_ROOT}/.claude/runtime"
STALENESS_FILE="${RUNTIME_DIR}/.poststart-timestamp"

mkdir -p "${RUNTIME_DIR}"

# postStart-default: no auth probe (per ADR-0041 D-0008)
export MCP_AUTH_PROBE=0

# Enumerate the 7 server names from .mcp.json
mapfile -t SERVERS < <(jq -r '.mcpServers | keys[]' "${MCP_JSON}")

if [[ ${#SERVERS[@]} -ne 7 ]]; then
  emit_degraded_banner "<config>" "<n/a>"
  log_mcp_event "$(jq -n -c --argjson n ${#SERVERS[@]} \
    '{event:"structured_failure", timestamp:(now|todateiso8601), server:"<config>", failure_layer:"config", primary_degraded:false, fallback_invoked:false, fallback_server:null, redaction_applied:false, message:("expected 7 servers in .mcp.json; found " + ($n | tostring))}')"
  echo "[postStart] WARN: expected 7 servers, found ${#SERVERS[@]}" >&2
fi

echo "[postStart] probing ${#SERVERS[@]} MCP servers..."

# Probe each server; emit one readiness_probe record per
for server in "${SERVERS[@]}"; do
  ping_result="$(bash "${LIB_DIR}/mcp-ping.sh" "${server}")"

  # Convert mcp-ping output → readiness_probe record per ADR-0037 schema
  # ping output: {server, result:pass|fail, failure_layer, latency_ms, message_redacted}
  # readiness_probe schema: {event, timestamp, server, probe_method, latency_ms, status, error?}
  record="$(echo "${ping_result}" | jq -c '
    {
      event: "readiness_probe",
      timestamp: (now | todateiso8601),
      server: .server,
      probe_method: "json-rpc-tools-list",
      latency_ms: .latency_ms,
      status: (if .result == "pass" then "ok" elif .failure_layer == "transport" then "unreachable" else "degraded" end)
    } + (if .result != "pass" then {error: .message_redacted, failure_layer: .failure_layer} else {} end)
  ')"

  log_mcp_event "${record}"

  # Banner on degraded/unreachable (warn-and-continue per ADR-0037)
  if [[ "$(echo "${ping_result}" | jq -r '.result')" != "pass" ]]; then
    emit_degraded_banner "${server}" "<no fallback registered>"
  fi
done

# Record postStart timestamp for §D-6 staleness check
date -u +%s > "${STALENESS_FILE}"

echo "[postStart] complete — see .claude/runtime/mcp-events.jsonl"
