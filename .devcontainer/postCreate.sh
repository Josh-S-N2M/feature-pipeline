#!/usr/bin/env bash
# .devcontainer/postCreate.sh
#
# Per Plan T3.4 + ADR-0041 v1.0.1 hybrid posture + sentinel+binary-presence
# pattern for idempotency. Installs the 4 OSS-local MCP servers, emits one
# `install_complete` JSONL record per server, then runs auth-probes against
# the 2 HTTP servers (context7, exa) with MCP_AUTH_PROBE=1.
#
# Servers installed here (4 — post-2026-05-24 postmortem; was 5):
#   - serena              (uv tool install -p 3.13 serena-agent==${SERENA_VERSION} --prerelease=allow;
#                          canonical upstream install per MCP-provisioning-postmortem 2026-05-24)
#   - actionlint-mcp      (go install github.com/hongkongkiwi/actionlint-mcp@${ACTIONLINT_MCP_SHA})
#   - terraform-mcp       (via .devcontainer/install/terraform-mcp.sh — binary + sha256 + gpg)
#   - gitnexus            (npm install -g gitnexus@${GITNEXUS_TAG} with GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1)
#
# mcp-openapi-schema removed 2026-05-24 per postmortem: no spec source available;
# upstream npm package abandoned; design-api had no working spec server anyway.
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
# Post-install: gitnexus hook setup + index pre-warm
# Federated-crystal patch (2026-05-26): runs `gitnexus setup` to install
# the upstream PreToolUse/PostToolUse hook scripts into ~/.claude/hooks/, then
# `gitnexus analyze` to populate the code graph so first-call agents never
# see "no indexed repositories." Both steps are idempotent (setup writes
# files; analyze early-exits if lastCommit == HEAD). The PreToolUse augment
# hook is neutralized by GITNEXUS_DISABLE_PRETOOL_AUGMENT_WHEN_MCP=1 (per
# devcontainer.json containerEnv) to avoid the issue-#1492 KuzuDB lock
# conflict with the long-lived MCP server.
# ---------------------------------------------------------------------------
gitnexus_post_install_warm() {
  local start; start=$(date +%s%3N)
  local setup_status="ok" analyze_status="ok"

  if ! npx -y "gitnexus@${GITNEXUS_TAG}" setup >/dev/null 2>&1; then
    setup_status="failed"
  fi
  local setup_end; setup_end=$(date +%s%3N)
  log_mcp_event "$(jq -n -c --arg v "${GITNEXUS_TAG}" --arg s "${setup_status}" --argjson dur "$((setup_end - start))" \
    '{event:"install_complete", timestamp:(now|todateiso8601), server:"gitnexus", install_method:"npx-setup", version:$v, duration_ms:$dur, status:$s, note:"npx gitnexus setup — writes ~/.claude/hooks/gitnexus/gitnexus-hook.cjs"}')"

  # Analyze can run from any directory but uses CWD-detection; cd into repo root
  local analyze_start; analyze_start=$(date +%s%3N)
  if ! (cd "${REPO_ROOT}" && npx -y "gitnexus@${GITNEXUS_TAG}" analyze >/dev/null 2>&1); then
    analyze_status="failed"
  fi
  local analyze_end; analyze_end=$(date +%s%3N)
  log_mcp_event "$(jq -n -c --arg v "${GITNEXUS_TAG}" --arg s "${analyze_status}" --argjson dur "$((analyze_end - analyze_start))" \
    '{event:"install_complete", timestamp:(now|todateiso8601), server:"gitnexus", install_method:"npx-analyze", version:$v, duration_ms:$dur, status:$s, note:"npx gitnexus analyze — populates .gitnexus/ graph index (idempotent: early-exit if lastCommit == HEAD)"}')"

  # Warn-and-continue: never fail the codespace creation for analyze
  return 0
}

# ---------------------------------------------------------------------------
# Run installs (warn-and-continue posture — single failure shouldn't bring
# the Codespace down per ADR-0037 banner pattern)
# ---------------------------------------------------------------------------
echo "[postCreate] installing 4 OSS-local MCP servers..."

install_serena              || emit_degraded_banner "serena"              "<no fallback>"
install_actionlint_mcp      || emit_degraded_banner "actionlint-mcp"      "<no fallback>"
install_terraform_mcp       || emit_degraded_banner "terraform-mcp"       "<no fallback>"

# ---------------------------------------------------------------------------
# FR-4a static-shape check — AC-CS-4a-1 (four assertions A1–A4)
# Runs BEFORE install_gitnexus; fail-closed per NFR-6.
# No network, no install attempts — env-var lookups + 1 file read + npm root.
# NFR-3 ≤100 ms cost target: all checks are local, no I/O beyond reading
# versions.env from disk (already sourced above; re-sourced in subshell for A3).
# ---------------------------------------------------------------------------
_fr4a_check() {
  local _fail_assertion="" _fail_detail=""

  # A1: GITNEXUS_SKIP_OPTIONAL_GRAMMARS must be exported and equal "1".
  # Set via devcontainer.json containerEnv; install_gitnexus re-exports it but
  # that hasn't run yet — this confirms the container env is correctly shaped.
  local _skip_grammars="${GITNEXUS_SKIP_OPTIONAL_GRAMMARS:-}"
  if [[ "${_skip_grammars}" != "1" ]]; then
    _fail_assertion="A1"
    _fail_detail="GITNEXUS_SKIP_OPTIONAL_GRAMMARS=${_skip_grammars:-<unset>} (expected 1)"
  fi

  # A2: GITNEXUS_TAG must be non-empty and match a semver-like format.
  if [[ -z "${_fail_assertion}" ]]; then
    local _tag="${GITNEXUS_TAG:-}"
    if [[ -z "${_tag}" ]] || ! [[ "${_tag}" =~ ^v?[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
      _fail_assertion="A2"
      _fail_detail="GITNEXUS_TAG=${_tag:-<unset>} does not match expected version format (e.g. 1.6.5)"
    fi
  fi

  # A3: GITNEXUS_TAG must match the value declared in versions.env.
  if [[ -z "${_fail_assertion}" ]]; then
    local _versions_env="${SCRIPT_DIR}/versions.env"
    local _pinned_tag
    _pinned_tag="$(bash -c "source ${_versions_env} 2>/dev/null && printf '%s' \"\${GITNEXUS_TAG:-}\"")"
    if [[ "${GITNEXUS_TAG}" != "${_pinned_tag}" ]]; then
      _fail_assertion="A3"
      _fail_detail="live GITNEXUS_TAG=${GITNEXUS_TAG} diverges from versions.env pin ${_pinned_tag:-<unreadable>}"
    fi
  fi

  # A4: npm root -g must return a non-empty path AND that path must be writable.
  if [[ -z "${_fail_assertion}" ]]; then
    local _npm_root
    _npm_root="$(npm root -g 2>/dev/null || true)"
    if [[ -z "${_npm_root}" ]]; then
      _fail_assertion="A4"
      _fail_detail="npm root -g returned empty path; npm global install location is unusable"
    elif [[ ! -w "${_npm_root}" ]]; then
      _fail_assertion="A4"
      _fail_detail="npm root -g path ${_npm_root} is not writable; install_gitnexus will fail"
    fi
  fi

  if [[ -n "${_fail_assertion}" ]]; then
    local _note
    _note="$(printf '{"mechanism":"FR-4a GitNexus install pre-flight check","offending_artifact":"%s","rule_violated":"AC-CS-4a-1 sub-assertion %s","remedial_hint":"%s"}' \
      "${_fail_detail}" \
      "${_fail_assertion}" \
      "$(case "${_fail_assertion}" in
           A1) printf 'Export GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1 in devcontainer.json containerEnv and rebuild the devcontainer' ;;
           A2) printf 'Set a valid GITNEXUS_TAG (e.g. 1.6.5) in versions.env and rebuild the devcontainer' ;;
           A3) printf 'Unset stale GITNEXUS_TAG override in the environment or update versions.env to match; rebuild the devcontainer' ;;
           A4) printf 'Ensure npm is installed and the global lib directory is writable (check npm config prefix); rebuild the devcontainer' ;;
         esac)")"
    log_mcp_event "$(jq -n -c \
      --arg note "${_note}" \
      --arg detail "${_fail_detail}" \
      '{event:"structured_failure", timestamp:(now|todateiso8601), server:"gitnexus", failure_layer:"pre-install-static-check", primary_degraded:false, fallback_invoked:false, note:$note}')"
    printf '[postCreate] FR-4a pre-flight FAILED (%s): %s\n' "${_fail_assertion}" "${_fail_detail}" >&2
    printf '[postCreate] Remediation: see note field in mcp-events.jsonl; rebuild devcontainer after fix.\n' >&2
    return 1
  fi
}
_fr4a_check

# ---------------------------------------------------------------------------
# Q-CS-1b stale-calibration banner — AC-X-4 (informational only; never fail-close)
# Checks whether the FR-4b gitnexus-grammar-skip calibration result recorded in
# mcp-events.jsonl is absent or older than 14 days, and emits an advisory to
# stderr if so.  Three variants:
#   NEVER RUN  — no calibration_result event for this mechanism exists (or file absent)
#   STALE      — most-recent event is older than 14 days
#   silent     — most-recent event is within 14 days
#
# Intentionally omits "rule violated" field per Blueprint v2.3 AC-X-4 (staleness is
# not a rule violation; the banner carries: mechanism + staleness-age + remedial hint).
# Does NOT emit any mcp-events.jsonl record (observability-at-rebuild, not log noise).
# ---------------------------------------------------------------------------
_fr4b_calibration_banner() {
  local MCP_EVENTS_FILE="${SENTINEL_DIR}/mcp-events.jsonl"
  local MECHANISM="fr-4b-gitnexus-grammar-skip"
  local THRESHOLD_DAYS=14

  # If jq is not available, degrade silently — banner is advisory only.
  command -v jq >/dev/null 2>&1 || return 0

  # Extract the most-recent calibration_result timestamp for this mechanism.
  local latest_ts=""
  if [[ -f "${MCP_EVENTS_FILE}" ]]; then
    latest_ts="$(jq -r \
      'select(.event == "calibration_result" and .mechanism == "'"${MECHANISM}"'") | .timestamp' \
      "${MCP_EVENTS_FILE}" 2>/dev/null | tail -1)" || true
  fi

  if [[ -z "${latest_ts}" ]]; then
    # NEVER RUN variant
    echo "[postCreate] FR-4b calibration: NEVER RUN. Run 'gh workflow run gitnexus-grammar-skip-calibration.yml --ref main' OR './.devcontainer/scripts/calibrate-gitnexus-grammar-skip.sh' to retire this banner." >&2
    return 0
  fi

  # Convert ISO-8601 timestamp to epoch; degrade silently if date conversion fails.
  local event_epoch
  event_epoch="$(date -d "${latest_ts}" +%s 2>/dev/null)" || return 0

  local now_epoch threshold_epoch days_old
  now_epoch="$(date +%s)"
  threshold_epoch=$(( now_epoch - (THRESHOLD_DAYS * 86400) ))
  days_old=$(( (now_epoch - event_epoch) / 86400 ))

  if [[ "${event_epoch}" -lt "${threshold_epoch}" ]]; then
    # STALE variant
    echo "[postCreate] FR-4b calibration: STALE. Most recent calibration_result event is ${days_old} days old (threshold: ${THRESHOLD_DAYS}). Re-run 'gh workflow run gitnexus-grammar-skip-calibration.yml --ref main'." >&2
  fi
  # silent variant: no output when within threshold
  return 0
}
_fr4b_calibration_banner || true

install_gitnexus            || emit_degraded_banner "gitnexus"            "<no fallback>"

echo "[postCreate] running gitnexus setup + analyze pre-warm..."
gitnexus_post_install_warm  || emit_degraded_banner "gitnexus" "<post-install warm failed; runtime fallback path unchanged>"

echo "[postCreate] OSS-local install pass complete; running auth-probes for HTTP servers..."

# Auth probes for context7 + exa (per ADR-0041 D-0008: postCreate runs with MCP_AUTH_PROBE=1)
export MCP_AUTH_PROBE=1
for server in context7 exa; do
  probe_result="$(bash "${LIB_DIR}/mcp-auth-probe.sh" "${server}")"
  # Log as readiness_probe (not install_complete; HTTP servers don't install)
  echo "${probe_result}" | jq -c '. + {event:"readiness_probe", timestamp:(now|todateiso8601), probe_method:"json-rpc-tools-list"}' | log_mcp_event --stdin
done

echo "[postCreate] complete — see .claude/runtime/mcp-events.jsonl"
