#!/usr/bin/env bash
# .devcontainer/postCreate.sh
#
# Per Plan T3.4 + ADR-0041 v1.0.1 hybrid posture + sentinel+binary-presence
# pattern for idempotency. Installs the 3 OSS-local MCP servers, emits one
# `install_complete` JSONL record per server, then runs auth-probes against
# the 2 HTTP servers (context7, exa) with MCP_AUTH_PROBE=1.
#
# Servers installed here (3 — post-2026-05-27 gitnexus removal; was 4):
#   - serena              (uv tool install -p 3.13 serena-agent==${SERENA_VERSION} --prerelease=allow;
#                          canonical upstream install per MCP-provisioning-postmortem 2026-05-24)
#   - actionlint-mcp      (go install github.com/hongkongkiwi/actionlint-mcp@${ACTIONLINT_MCP_SHA})
#   - terraform-mcp       (via .devcontainer/install/terraform-mcp.sh — binary + sha256 + gpg)
#
# mcp-openapi-schema removed 2026-05-24 per postmortem: no spec source available;
# upstream npm package abandoned; design-api had no working spec server anyway.
# gitnexus removed 2026-05-27 per ADR-0066: empirical unreliability; the two
# dependent sub-agents (discovery-codebase-researcher, review-architecture-auditor)
# fall back to Read/Grep/Glob + serena symbol tools per ADR-0007's documented fallback.
#
# context7 and exa are HTTP-transport hosted servers — no install step (but auth-probed at end).
#
# Tool prerequisites (image-build-time, NOT installed by this script):
#   - jq, ripgrep, bat, tree, less    installed via .devcontainer/Dockerfile RUN apt-get
#   - shellcheck                       installed via .devcontainer/Dockerfile RUN apt-get
#                                      (added in Phase 8 of feature issue-capture-mechanism-r1
#                                      — persists the install so future codespace rebuilds
#                                      pre-install shellcheck for hook-script linting.)

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
# Install: serena (uv tool install — canonical upstream method)
# Per MCP-provisioning-postmortem 2026-05-24:
#   - upstream README explicitly disrecommends `uvx --from git+...@<ref>`
#   - canonical install: `uv tool install -p 3.13 serena-agent==${SERENA_VERSION} --prerelease=allow`
#   - PyPI package name is `serena-agent`; the installed binary is `serena`
#   - runtime invocation: `serena start-mcp-server` (per .mcp.json)
# ---------------------------------------------------------------------------
install_serena() {
  local sentinel="${SENTINEL_DIR}/.install-sentinel-serena-${SERENA_VERSION}"
  if check_installed "${sentinel}" "serena"; then
    log_mcp_event "$(jq -n -c --arg v "${SERENA_VERSION}" \
      '{event:"install_complete", timestamp:(now|todateiso8601), server:"serena", install_method:"uv-tool", version:$v, duration_ms:0, status:"ok", note:"sentinel present; install skipped"}')"
    return 0
  fi

  if ! command -v uv >/dev/null 2>&1; then
    log_mcp_event "$(jq -n -c --arg v "${SERENA_VERSION}" \
      '{event:"install_complete", timestamp:(now|todateiso8601), server:"serena", install_method:"uv-tool", version:$v, duration_ms:0, status:"failed", note:"uv binary not on PATH; Dockerfile uv install missing or image not rebuilt"}')"
    echo "[postCreate] serena install failed: uv not installed (rebuild Codespace for Dockerfile changes to take effect)" >&2
    return 1
  fi

  local start; start=$(date +%s%3N)
  if uv tool install -p 3.13 "serena-agent==${SERENA_VERSION}" --prerelease=allow >/dev/null 2>&1; then
    touch "${sentinel}"
    local end; end=$(date +%s%3N)
    log_mcp_event "$(jq -n -c --arg v "${SERENA_VERSION}" --argjson dur "$((end - start))" \
      '{event:"install_complete", timestamp:(now|todateiso8601), server:"serena", install_method:"uv-tool", version:$v, duration_ms:$dur, status:"ok"}')"
  else
    log_mcp_event "$(jq -n -c --arg v "${SERENA_VERSION}" \
      '{event:"install_complete", timestamp:(now|todateiso8601), server:"serena", install_method:"uv-tool", version:$v, duration_ms:0, status:"failed", note:"uv tool install serena-agent failed"}')"
    echo "[postCreate] serena install failed" >&2
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
# Run installs (warn-and-continue posture — single failure shouldn't bring
# the Codespace down per ADR-0037 banner pattern)
# ---------------------------------------------------------------------------
echo "[postCreate] installing 3 OSS-local MCP servers..."

install_serena              || emit_degraded_banner "serena"              "<no fallback>"
install_actionlint_mcp      || emit_degraded_banner "actionlint-mcp"      "<no fallback>"
install_terraform_mcp       || emit_degraded_banner "terraform-mcp"       "<no fallback>"

echo "[postCreate] OSS-local install pass complete; running auth-probes for HTTP servers..."

# Auth probes for context7 + exa (per ADR-0041 D-0008: postCreate runs with MCP_AUTH_PROBE=1)
export MCP_AUTH_PROBE=1
for server in context7 exa; do
  probe_result="$(bash "${LIB_DIR}/mcp-auth-probe.sh" "${server}")"
  # Log as readiness_probe (not install_complete; HTTP servers don't install)
  echo "${probe_result}" | jq -c '. + {event:"readiness_probe", timestamp:(now|todateiso8601), probe_method:"json-rpc-tools-list"}' | log_mcp_event --stdin
done

echo "[postCreate] complete — see .claude/runtime/mcp-events.jsonl"
