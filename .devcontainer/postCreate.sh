#!/usr/bin/env bash
# .devcontainer/postCreate.sh
#
# Per Plan T3.4 + ADR-0041 v1.0.1 hybrid posture + sentinel+binary-presence
# pattern for idempotency. Installs the 5 OSS-local MCP servers, emits one
# `install_complete` JSONL record per server, then runs auth-probes against
# the 2 HTTP servers (context7, exa) with MCP_AUTH_PROBE=1.
#
# Servers installed here (5):
#   - serena              (uvx --from git+https://github.com/oraios/serena@${SERENA_REF})
#   - mcp-openapi-schema  (npm install -g; STALE_PACKAGE per H-3)
#   - actionlint-mcp      (go install github.com/hongkongkiwi/actionlint-mcp@${ACTIONLINT_MCP_SHA})
#   - terraform-mcp       (via .devcontainer/install/terraform-mcp.sh — binary + sha256 + gpg)
#   - gitnexus            (npm install -g gitnexus@${GITNEXUS_TAG} with GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1)
#
# context7 and exa are HTTP-transport hosted servers — no install step (but auth-probed at end).

set -euo pipefail

# Path resolution
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
LIB_DIR="${SCRIPT_DIR}/lib"

# shellcheck disable=SC1091
source "${LIB_DIR}/log-mcp-event.sh"

# Source the version pins
VERSIONS_ENV="${SCRIPT_DIR}/versions.env"
if [[ ! -f "${VERSIONS_ENV}" ]]; then
  echo "[postCreate] FATAL: ${VERSIONS_ENV} missing" >&2
  exit 1
fi
# shellcheck disable=SC1090
source "${VERSIONS_ENV}"

# Sentinel directory
SENTINEL_DIR="${REPO_ROOT}/.claude/runtime"
mkdir -p "${SENTINEL_DIR}"

# Idempotency helper: returns 0 if (sentinel exists AND binary on PATH); 1 otherwise.
check_installed() {
  local sentinel="$1"
  local binary="$2"
  [[ -f "${sentinel}" ]] && command -v "${binary}" >/dev/null 2>&1
}

# ---------------------------------------------------------------------------
# Install: serena (uvx)
# ---------------------------------------------------------------------------
install_serena() {
  local sentinel="${SENTINEL_DIR}/.install-sentinel-serena-${SERENA_REF}"
  if check_installed "${sentinel}" "uvx"; then
    log_mcp_event "$(jq -n -c --arg v "${SERENA_REF}" \
      '{event:"install_complete", timestamp:(now|todateiso8601), server:"serena", install_method:"uvx", version:$v, duration_ms:0, status:"ok", note:"sentinel present; install skipped"}')"
    return 0
  fi

  local start; start=$(date +%s%3N)
  # uvx --from git pulls + builds on first use; we just verify it resolves
  if uvx --from "git+https://github.com/oraios/serena@${SERENA_REF}" serena --version >/dev/null 2>&1; then
    touch "${sentinel}"
    local end; end=$(date +%s%3N)
    log_mcp_event "$(jq -n -c --arg v "${SERENA_REF}" --argjson dur "$((end - start))" \
      '{event:"install_complete", timestamp:(now|todateiso8601), server:"serena", install_method:"uvx", version:$v, duration_ms:$dur, status:"ok"}')"
  else
    log_mcp_event "$(jq -n -c --arg v "${SERENA_REF}" \
      '{event:"install_complete", timestamp:(now|todateiso8601), server:"serena", install_method:"uvx", version:$v, duration_ms:0, status:"failed", note:"uvx serena --version failed"}')"
    echo "[postCreate] serena install failed" >&2
    return 1
  fi
}

# ---------------------------------------------------------------------------
# Install: mcp-openapi-schema (npm)
# ---------------------------------------------------------------------------
install_mcp_openapi_schema() {
  local sentinel="${SENTINEL_DIR}/.install-sentinel-mcp-openapi-schema-${MCP_OPENAPI_SCHEMA_VERSION}"
  if check_installed "${sentinel}" "mcp-openapi-schema"; then
    log_mcp_event "$(jq -n -c --arg v "${MCP_OPENAPI_SCHEMA_VERSION}" \
      '{event:"install_complete", timestamp:(now|todateiso8601), server:"mcp-openapi-schema", install_method:"npm", version:$v, duration_ms:0, status:"ok", note:"STALE_PACKAGE per H-3; sentinel present"}')"
    return 0
  fi

  local start; start=$(date +%s%3N)
  if npm install -g "mcp-openapi-schema@${MCP_OPENAPI_SCHEMA_VERSION}" >/dev/null 2>&1; then
    touch "${sentinel}"
    local end; end=$(date +%s%3N)
    log_mcp_event "$(jq -n -c --arg v "${MCP_OPENAPI_SCHEMA_VERSION}" --argjson dur "$((end - start))" \
      '{event:"install_complete", timestamp:(now|todateiso8601), server:"mcp-openapi-schema", install_method:"npm", version:$v, duration_ms:$dur, status:"ok", note:"STALE_PACKAGE per H-3"}')"
  else
    log_mcp_event "$(jq -n -c --arg v "${MCP_OPENAPI_SCHEMA_VERSION}" \
      '{event:"install_complete", timestamp:(now|todateiso8601), server:"mcp-openapi-schema", install_method:"npm", version:$v, duration_ms:0, status:"failed", note:"npm install -g failed"}')"
    return 1
  fi
}

# ---------------------------------------------------------------------------
# Install: actionlint-mcp (go install)
# ---------------------------------------------------------------------------
install_actionlint_mcp() {
  local sentinel="${SENTINEL_DIR}/.install-sentinel-actionlint-mcp-${ACTIONLINT_MCP_SHA}"
  if check_installed "${sentinel}" "actionlint-mcp"; then
    log_mcp_event "$(jq -n -c --arg v "${ACTIONLINT_MCP_SHA}" \
      '{event:"install_complete", timestamp:(now|todateiso8601), server:"actionlint-mcp", install_method:"go install", version:$v, duration_ms:0, status:"ok", note:"sentinel present; install skipped"}')"
    return 0
  fi

  local start; start=$(date +%s%3N)
  # Per cycle-3 reconciliation F1: hongkongkiwi/actionlint-mcp (NOT 2manymws/); no /cmd/ subpath
  if go install "github.com/hongkongkiwi/actionlint-mcp@${ACTIONLINT_MCP_SHA}" >/dev/null 2>&1; then
    touch "${sentinel}"
    local end; end=$(date +%s%3N)
    log_mcp_event "$(jq -n -c --arg v "${ACTIONLINT_MCP_SHA}" --argjson dur "$((end - start))" \
      '{event:"install_complete", timestamp:(now|todateiso8601), server:"actionlint-mcp", install_method:"go install", version:$v, duration_ms:$dur, status:"ok"}')"
  else
    log_mcp_event "$(jq -n -c --arg v "${ACTIONLINT_MCP_SHA}" \
      '{event:"install_complete", timestamp:(now|todateiso8601), server:"actionlint-mcp", install_method:"go install", version:$v, duration_ms:0, status:"failed", note:"go install failed"}')"
    return 1
  fi
}

# ---------------------------------------------------------------------------
# Install: terraform-mcp (binary + sha256 + gpg)
# ---------------------------------------------------------------------------
install_terraform_mcp() {
  # Delegated to dedicated script — handles its own log_mcp_event call
  bash "${SCRIPT_DIR}/install/terraform-mcp.sh"
}

# ---------------------------------------------------------------------------
# Install: gitnexus (npm with GITNEXUS_SKIP_OPTIONAL_GRAMMARS)
# ---------------------------------------------------------------------------
install_gitnexus() {
  local sentinel="${SENTINEL_DIR}/.install-sentinel-gitnexus-${GITNEXUS_TAG}"
  if check_installed "${sentinel}" "gitnexus"; then
    log_mcp_event "$(jq -n -c --arg v "${GITNEXUS_TAG}" \
      '{event:"install_complete", timestamp:(now|todateiso8601), server:"gitnexus", install_method:"npm", version:$v, duration_ms:0, status:"ok", note:"sentinel present; install skipped"}')"
    return 0
  fi

  local start; start=$(date +%s%3N)
  # Per cycle-3 reconciliation F2: npm install (NOT uvx); env-var BEFORE install per AC-CS-9 wrapping intent
  export GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1
  if npm install -g "gitnexus@${GITNEXUS_TAG}" >/dev/null 2>&1; then
    touch "${sentinel}"
    local end; end=$(date +%s%3N)
    log_mcp_event "$(jq -n -c --arg v "${GITNEXUS_TAG}" --argjson dur "$((end - start))" \
      '{event:"install_complete", timestamp:(now|todateiso8601), server:"gitnexus", install_method:"npm", version:$v, duration_ms:$dur, status:"ok", note:"GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1 honored per AC-CS-9"}')"
  else
    log_mcp_event "$(jq -n -c --arg v "${GITNEXUS_TAG}" \
      '{event:"install_complete", timestamp:(now|todateiso8601), server:"gitnexus", install_method:"npm", version:$v, duration_ms:0, status:"failed", note:"npm install -g failed"}')"
    return 1
  fi
}

# ---------------------------------------------------------------------------
# Run installs (warn-and-continue posture — single failure shouldn't bring
# the Codespace down per ADR-0037 banner pattern)
# ---------------------------------------------------------------------------
echo "[postCreate] installing 5 OSS-local MCP servers..."

install_serena              || emit_degraded_banner "serena"              "<no fallback>"
install_mcp_openapi_schema  || emit_degraded_banner "mcp-openapi-schema"  "<no fallback>"
install_actionlint_mcp      || emit_degraded_banner "actionlint-mcp"      "<no fallback>"
install_terraform_mcp       || emit_degraded_banner "terraform-mcp"       "<no fallback>"
install_gitnexus            || emit_degraded_banner "gitnexus"            "<no fallback>"

echo "[postCreate] OSS-local install pass complete; running auth-probes for HTTP servers..."

# Auth probes for context7 + exa (per ADR-0041 D-0008: postCreate runs with MCP_AUTH_PROBE=1)
export MCP_AUTH_PROBE=1
for server in context7 exa; do
  probe_result="$(bash "${LIB_DIR}/mcp-auth-probe.sh" "${server}")"
  # Log as readiness_probe (not install_complete; HTTP servers don't install)
  echo "${probe_result}" | jq -c '. + {event:"readiness_probe", timestamp:(now|todateiso8601), probe_method:"json-rpc-tools-list"}' | log_mcp_event --stdin
done

echo "[postCreate] complete — see .claude/runtime/mcp-events.jsonl"
