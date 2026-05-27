#!/usr/bin/env bash
# run-banner-smoke.sh — standalone smoke runner for _fr4b_calibration_banner
#
# Usage: ./run-banner-smoke.sh <path-to-mcp-events.jsonl>
#
# Copies the _fr4b_calibration_banner logic verbatim from postCreate.sh but
# accepts the events-file path as $1 instead of deriving it from SENTINEL_DIR.
# This lets the harness point the function at any fixture file.
#
# Exit behaviour:
#   - always exits 0 (the banner is informational; never fail-close)
#   - stderr carries the banner text (or nothing for the silent/fresh case)

set -euo pipefail

MCP_EVENTS_FILE="${1:?usage: $0 <path-to-mcp-events.jsonl>}"
MECHANISM="fr-4b-gitnexus-grammar-skip"
THRESHOLD_DAYS=14

# Abort loudly if jq is absent — this is a test harness, not the real banner.
if ! command -v jq >/dev/null 2>&1; then
  echo "ERROR: jq not found; cannot run banner smoke" >&2
  exit 1
fi

# Extract the most-recent calibration_result timestamp for this mechanism.
latest_ts=""
if [[ -f "${MCP_EVENTS_FILE}" ]]; then
  latest_ts="$(jq -r \
    'select(.event == "calibration_result" and .mechanism == "'"${MECHANISM}"'") | .timestamp' \
    "${MCP_EVENTS_FILE}" 2>/dev/null | tail -1)" || true
fi

if [[ -z "${latest_ts}" ]]; then
  # NEVER RUN variant
  echo "[postCreate] FR-4b calibration: NEVER RUN. Run 'gh workflow run gitnexus-grammar-skip-calibration.yml --ref main' OR './.devcontainer/scripts/calibrate-gitnexus-grammar-skip.sh' to retire this banner." >&2
  exit 0
fi

# Convert ISO-8601 timestamp to epoch; degrade silently if date conversion fails.
event_epoch=""
event_epoch="$(date -d "${latest_ts}" +%s 2>/dev/null)" || exit 0

now_epoch="$(date +%s)"
threshold_epoch=$(( now_epoch - (THRESHOLD_DAYS * 86400) ))
days_old=$(( (now_epoch - event_epoch) / 86400 ))

if [[ "${event_epoch}" -lt "${threshold_epoch}" ]]; then
  # STALE variant
  echo "[postCreate] FR-4b calibration: STALE. Most recent calibration_result event is ${days_old} days old (threshold: ${THRESHOLD_DAYS}). Re-run 'gh workflow run gitnexus-grammar-skip-calibration.yml --ref main'." >&2
fi
# silent variant: no output when within threshold
exit 0
