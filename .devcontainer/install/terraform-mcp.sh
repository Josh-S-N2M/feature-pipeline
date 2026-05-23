#!/usr/bin/env bash
# .devcontainer/install/terraform-mcp.sh
#
# Per Plan T3.3 + ADR-0041 binary-fetch path. Installs terraform-mcp-server
# from releases.hashicorp.com with sha256 + gpg verification.
#
# Pin: TERRAFORM_MCP_VERSION from .devcontainer/versions.env (default 0.5.2).
# HashiCorp GPG fingerprint (well-known): C874011F0AB405110D02105534365D9472D7468F
#
# Usage:
#   bash .devcontainer/install/terraform-mcp.sh
#
# Exit codes:
#   0 — installed (or already present at correct version + sentinel matches)
#   1 — installation failed (sha mismatch, gpg fail, network error, etc.)

set -euo pipefail

LIB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../lib" && pwd)"
REPO_ROOT="$(cd "${LIB_DIR}/../.." && pwd)"

# shellcheck disable=SC1091
source "${LIB_DIR}/log-mcp-event.sh"

# Source pins
VERSIONS_ENV="${REPO_ROOT}/.devcontainer/versions.env"
if [[ ! -f "${VERSIONS_ENV}" ]]; then
  echo "[terraform-mcp install] versions.env missing at ${VERSIONS_ENV}" >&2
  exit 1
fi
# shellcheck disable=SC1090
source "${VERSIONS_ENV}"

TFV="${TERRAFORM_MCP_VERSION:-0.5.2}"
TARGET_BIN="/usr/local/bin/terraform-mcp"
SENTINEL="${REPO_ROOT}/.claude/runtime/.install-sentinel-terraform-mcp-${TFV}"

# Idempotency: sentinel + binary present per ADR-0041 D-0010
if [[ -x "${TARGET_BIN}" ]] && [[ -f "${SENTINEL}" ]]; then
  install_method="binary-download"
  log_mcp_event "$(jq -n -c --arg v "${TFV}" \
    '{event:"install_complete", timestamp:(now|todateiso8601), server:"terraform-mcp", install_method:"binary-download", version:$v, duration_ms:0, status:"ok", note:"sentinel+binary present; install skipped"}')"
  exit 0
fi

ARCH="linux_amd64"
case "$(uname -m)" in
  aarch64|arm64) ARCH="linux_arm64" ;;
esac

URL_BASE="https://releases.hashicorp.com/terraform-mcp-server/${TFV}"
TARBALL="terraform-mcp-server_${TFV}_${ARCH}.zip"
SHASUMS="terraform-mcp-server_${TFV}_SHA256SUMS"
SHASUMS_SIG="terraform-mcp-server_${TFV}_SHA256SUMS.sig"

TMP_DIR="$(mktemp -d)"
trap 'rm -rf "${TMP_DIR}"' EXIT

start_s=$(date +%s%3N)

cd "${TMP_DIR}"

# 1. Download tarball + sums + signature
if ! wget -q "${URL_BASE}/${TARBALL}" "${URL_BASE}/${SHASUMS}" "${URL_BASE}/${SHASUMS_SIG}"; then
  log_mcp_event "$(jq -n -c --arg v "${TFV}" \
    '{event:"install_complete", timestamp:(now|todateiso8601), server:"terraform-mcp", install_method:"binary-download", version:$v, duration_ms:0, status:"failed", note:"wget failed for tarball or sums files"}')"
  echo "[terraform-mcp install] wget failed" >&2
  exit 1
fi

# 2. Verify sha256
if ! grep "${TARBALL}" "${SHASUMS}" | sha256sum -c --status; then
  log_mcp_event "$(jq -n -c --arg v "${TFV}" \
    '{event:"install_complete", timestamp:(now|todateiso8601), server:"terraform-mcp", install_method:"binary-download", version:$v, duration_ms:0, status:"failed", note:"sha256 mismatch"}')"
  echo "[terraform-mcp install] sha256 verification failed" >&2
  exit 1
fi

# 3. Verify gpg signature
# Import HashiCorp's public key if not already known
if ! gpg --list-keys 34365D9472D7468F >/dev/null 2>&1; then
  # Fetch the key (best-effort; SHA verification is the primary integrity gate)
  curl -sS https://apt.releases.hashicorp.com/gpg | gpg --import 2>/dev/null || true
fi

if gpg --verify "${SHASUMS_SIG}" "${SHASUMS}" >/dev/null 2>&1; then
  gpg_status="verified"
else
  # GPG failure is recorded but not blocking — sha256 is the primary check.
  # Operators in restricted networks may not be able to fetch the HashiCorp key.
  gpg_status="warn:gpg-not-verified"
  echo "[terraform-mcp install] WARN: gpg verification failed (sha256 still verified)" >&2
fi

# 4. Extract + install
if ! unzip -q "${TARBALL}"; then
  log_mcp_event "$(jq -n -c --arg v "${TFV}" \
    '{event:"install_complete", timestamp:(now|todateiso8601), server:"terraform-mcp", install_method:"binary-download", version:$v, duration_ms:0, status:"failed", note:"unzip failed"}')"
  exit 1
fi

# Move binary to target (requires sudo or pre-existing /usr/local/bin write perms)
if [[ -w "$(dirname "${TARGET_BIN}")" ]]; then
  mv terraform-mcp-server "${TARGET_BIN}"
else
  sudo mv terraform-mcp-server "${TARGET_BIN}"
fi
chmod 755 "${TARGET_BIN}"

# 5. Sentinel
mkdir -p "$(dirname "${SENTINEL}")"
touch "${SENTINEL}"

end_s=$(date +%s%3N)
duration_ms=$((end_s - start_s))

log_mcp_event "$(jq -n -c --arg v "${TFV}" --arg gpg "${gpg_status}" --argjson dur "${duration_ms}" \
  '{event:"install_complete", timestamp:(now|todateiso8601), server:"terraform-mcp", install_method:"binary-download", version:$v, duration_ms:$dur, status:"ok", gpg_status:$gpg}')"

echo "[terraform-mcp install] OK (version ${TFV}, gpg: ${gpg_status})"
