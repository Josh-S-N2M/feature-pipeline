#!/usr/bin/env bash
# .devcontainer/scripts/calibrate-gitnexus-grammar-skip.sh
#
# FR-4b — opt-in behavioral calibration of the GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1
# contract for GitNexus.
#
# Performs a scratch-directory npm install and asserts two upstream-observable
# signals when GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1 is set:
#
#   Signal 1 (stderr regex): both
#     [tree-sitter-dart] Skipping build (GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1)
#     [tree-sitter-proto] Skipping build (GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1)
#   must appear in captured stderr exactly once each.
#
#   Signal 3 (artifact absence): tree_sitter_dart_binding.node and
#   tree_sitter_proto_binding.node must NOT exist under the install prefix.
#
#   Negative assertion (default ON): a second install with
#   GITNEXUS_SKIP_OPTIONAL_GRAMMARS=0 must produce both .node artifacts,
#   defending against the contract being silently disabled at a future tag.
#
# Outcomes: pass | fail | drift_detected
#   pass           — Signal 1 + Signal 3 both succeeded; negative assertion OK.
#   drift_detected — Signal 1 regex no longer matches (upstream format changed).
#   fail           — Signal 1 matched but Signal 3 failed, or negative assertion
#                    failed, or npm install itself errored.
#
# Exit codes: 0 = pass, 1 = fail, 2 = drift_detected (also used for pre-flight errors).
#
# Emits exactly one calibration_result event to .claude/runtime/mcp-events.jsonl
# per ADR-0037 + ADR-0058 via log_mcp_event (from .devcontainer/lib/log-mcp-event.sh).
#
# CLI flags:
#   --no-calibrate   Skip the negative assertion (faster; default OFF).
#   --help           Print usage and exit 0.
#
# Usage:
#   bash .devcontainer/scripts/calibrate-gitnexus-grammar-skip.sh
#   bash .devcontainer/scripts/calibrate-gitnexus-grammar-skip.sh --no-calibrate

set -euo pipefail

# ---------------------------------------------------------------------------
# Resolve paths
# ---------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/../.." && pwd)"
LIB_DIR="${REPO_ROOT}/.devcontainer/lib"
VERSIONS_ENV="${REPO_ROOT}/.devcontainer/versions.env"

# ---------------------------------------------------------------------------
# Usage / help
# ---------------------------------------------------------------------------
usage() {
  cat <<'EOF'
Usage: calibrate-gitnexus-grammar-skip.sh [OPTIONS]

FR-4b behavioral calibration of GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1 for GitNexus.

Options:
  --no-calibrate   Skip the negative assertion (faster run; default: OFF).
  --help           Print this usage message and exit 0.

Exit codes:
  0   pass           — all signals confirmed.
  1   fail           — a required signal is absent or npm install failed.
  2   drift_detected — Signal 1 stderr regex no longer matches (upstream changed).
EOF
}

# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------
RUN_NEGATIVE_ASSERTION=true

for arg in "$@"; do
  case "${arg}" in
    --no-calibrate)
      RUN_NEGATIVE_ASSERTION=false
      ;;
    --help)
      usage
      exit 0
      ;;
    *)
      echo "calibrate-gitnexus-grammar-skip: unknown option: ${arg}" >&2
      echo "Run with --help for usage." >&2
      exit 2
      ;;
  esac
done

# ---------------------------------------------------------------------------
# Source log helper
# ---------------------------------------------------------------------------
# shellcheck disable=SC1091
source "${LIB_DIR}/log-mcp-event.sh"

# ---------------------------------------------------------------------------
# Pre-flight checks
# ---------------------------------------------------------------------------
if ! command -v npm >/dev/null 2>&1; then
  echo "calibrate-gitnexus-grammar-skip: npm not found on PATH. Cannot run calibration." >&2
  exit 2
fi

test_dir="$(mktemp -d 2>/dev/null)" || {
  echo "calibrate-gitnexus-grammar-skip: mktemp -d failed. Cannot create scratch directory." >&2
  exit 2
}
rm -rf "${test_dir}"

# ---------------------------------------------------------------------------
# Read GITNEXUS_TAG from versions.env
# ---------------------------------------------------------------------------
if [[ ! -f "${VERSIONS_ENV}" ]]; then
  echo "calibrate-gitnexus-grammar-skip: versions.env not found at ${VERSIONS_ENV}" >&2
  exit 2
fi

GITNEXUS_TAG=""
# shellcheck disable=SC1090
while IFS='=' read -r key value; do
  # Strip comments and whitespace
  key="${key%%#*}"
  key="${key// /}"
  value="${value%%#*}"
  value="${value// /}"
  if [[ "${key}" == "GITNEXUS_TAG" && -n "${value}" ]]; then
    GITNEXUS_TAG="${value}"
    break
  fi
done < "${VERSIONS_ENV}"

if [[ -z "${GITNEXUS_TAG}" ]]; then
  echo "calibrate-gitnexus-grammar-skip: GITNEXUS_TAG not found in ${VERSIONS_ENV}" >&2
  exit 2
fi

# ---------------------------------------------------------------------------
# Scratch directories + cleanup trap
# ---------------------------------------------------------------------------
scratch1="$(mktemp -d)"
scratch2="$(mktemp -d)"

cleanup() {
  # shellcheck disable=SC2317  # false-positive: function is invoked via trap EXIT
  rm -rf "${scratch1}" "${scratch2}"
}
trap cleanup EXIT

# ---------------------------------------------------------------------------
# Positive run — GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1
# ---------------------------------------------------------------------------
echo "calibrate-gitnexus-grammar-skip: installing gitnexus@${GITNEXUS_TAG} with GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1 ..."

start_epoch_ms=$(date +%s%3N)

(
  cd "${scratch1}"
  npm init -y >/dev/null 2>&1
  GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1 npm install --prefix "${scratch1}" "gitnexus@${GITNEXUS_TAG}" \
    2> "${scratch1}/stderr.log" \
    >/dev/null
) || {
  end_epoch_ms=$(date +%s%3N)
  duration_ms=$(( end_epoch_ms - start_epoch_ms ))
  note="npm install failed (positive run)"
  echo "calibrate-gitnexus-grammar-skip: ${note}" >&2
  log_mcp_event "$(jq -n -c \
    --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    --arg ver "${GITNEXUS_TAG}" \
    --argjson dur "${duration_ms}" \
    --arg note "${note}" \
    '{
      event: "calibration_result",
      timestamp: $ts,
      server: "gitnexus",
      mechanism: "fr-4b-gitnexus-grammar-skip",
      version: $ver,
      duration_ms: $dur,
      outcome: "fail",
      signals: {signal_1: "not_run", signal_3: "not_run", negative_assertion: "not_run"},
      note: $note
    }')"
  exit 1
}

end_epoch_ms=$(date +%s%3N)
duration_ms=$(( end_epoch_ms - start_epoch_ms ))

# ---------------------------------------------------------------------------
# Signal 1 — stderr regex check
# ---------------------------------------------------------------------------
# Per T-001 research: only dart + proto are gated by GITNEXUS_SKIP_OPTIONAL_GRAMMARS
# at GitNexus v1.6.5. Swift is NOT asserted here.
STDERR_LOG="${scratch1}/stderr.log"
signal_1_status="pass"
signal_1_note=""

dart_matches=0
proto_matches=0

if [[ -f "${STDERR_LOG}" ]]; then
  dart_matches=$(grep -cE '\[tree-sitter-dart\] Skipping build \(GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1\)' "${STDERR_LOG}" 2>/dev/null || true)
  proto_matches=$(grep -cE '\[tree-sitter-proto\] Skipping build \(GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1\)' "${STDERR_LOG}" 2>/dev/null || true)
fi

if [[ "${dart_matches}" -eq 0 && "${proto_matches}" -eq 0 ]]; then
  # Neither pattern matched — upstream format may have changed
  signal_1_status="drift_detected"
  signal_1_note="Neither tree-sitter-dart nor tree-sitter-proto skip messages found in stderr. Upstream format may have changed."
elif [[ "${dart_matches}" -eq 0 ]]; then
  signal_1_status="drift_detected"
  signal_1_note="tree-sitter-dart skip message not found in stderr."
elif [[ "${proto_matches}" -eq 0 ]]; then
  signal_1_status="drift_detected"
  signal_1_note="tree-sitter-proto skip message not found in stderr."
else
  signal_1_note="dart=${dart_matches} proto=${proto_matches} skip messages found"
fi

# ---------------------------------------------------------------------------
# Signal 3 — artifact absence check
# ---------------------------------------------------------------------------
signal_3_status="pass"
signal_3_note=""

dart_artifacts=0
proto_artifacts=0

if [[ -d "${scratch1}/node_modules/gitnexus" ]]; then
  dart_artifacts=$(find "${scratch1}/node_modules/gitnexus" -name "tree_sitter_dart_binding.node" 2>/dev/null | wc -l)
  proto_artifacts=$(find "${scratch1}/node_modules/gitnexus" -name "tree_sitter_proto_binding.node" 2>/dev/null | wc -l)
fi

if [[ "${dart_artifacts}" -gt 0 || "${proto_artifacts}" -gt 0 ]]; then
  signal_3_status="fail"
  signal_3_note="Artifact(s) unexpectedly present: dart=${dart_artifacts} proto=${proto_artifacts}"
else
  signal_3_note="Both dart and proto binding artifacts absent (expected)"
fi

# ---------------------------------------------------------------------------
# Negative assertion — GITNEXUS_SKIP_OPTIONAL_GRAMMARS=0
# ---------------------------------------------------------------------------
negative_assertion_status="skipped"
negative_assertion_note="--no-calibrate passed; negative assertion skipped"

if [[ "${RUN_NEGATIVE_ASSERTION}" == "true" ]]; then
  echo "calibrate-gitnexus-grammar-skip: installing gitnexus@${GITNEXUS_TAG} with GITNEXUS_SKIP_OPTIONAL_GRAMMARS=0 (negative assertion) ..."

  neg_install_ok=true
  (
    cd "${scratch2}"
    npm init -y >/dev/null 2>&1
    GITNEXUS_SKIP_OPTIONAL_GRAMMARS=0 npm install --prefix "${scratch2}" "gitnexus@${GITNEXUS_TAG}" \
      >/dev/null 2>&1
  ) || neg_install_ok=false

  if [[ "${neg_install_ok}" == "true" ]]; then
    neg_dart_artifacts=0
    neg_proto_artifacts=0

    if [[ -d "${scratch2}/node_modules/gitnexus" ]]; then
      neg_dart_artifacts=$(find "${scratch2}/node_modules/gitnexus" -name "tree_sitter_dart_binding.node" 2>/dev/null | wc -l)
      neg_proto_artifacts=$(find "${scratch2}/node_modules/gitnexus" -name "tree_sitter_proto_binding.node" 2>/dev/null | wc -l)
    fi

    if [[ "${neg_dart_artifacts}" -gt 0 && "${neg_proto_artifacts}" -gt 0 ]]; then
      negative_assertion_status="pass"
      negative_assertion_note="Both artifacts present in default install (dart=${neg_dart_artifacts} proto=${neg_proto_artifacts})"
    elif [[ "${neg_dart_artifacts}" -eq 0 && "${neg_proto_artifacts}" -eq 0 ]]; then
      # Neither artifact present without the skip flag — contract may be gone upstream
      negative_assertion_status="fail"
      negative_assertion_note="Neither dart nor proto artifact found in default install. Contract may be silently disabled upstream."
    else
      negative_assertion_status="fail"
      negative_assertion_note="Partial artifact presence in default install: dart=${neg_dart_artifacts} proto=${neg_proto_artifacts}"
    fi
  else
    negative_assertion_status="fail"
    negative_assertion_note="npm install failed during negative assertion run"
  fi
fi

# ---------------------------------------------------------------------------
# Outcome computation
# ---------------------------------------------------------------------------
outcome="pass"
outcome_note=""

if [[ "${signal_1_status}" == "drift_detected" ]]; then
  outcome="drift_detected"
  outcome_note="${signal_1_note}"
elif [[ "${signal_1_status}" == "fail" || "${signal_3_status}" == "fail" ]]; then
  outcome="fail"
  outcome_note="signal_1=${signal_1_status} (${signal_1_note}); signal_3=${signal_3_status} (${signal_3_note})"
elif [[ "${negative_assertion_status}" == "fail" ]]; then
  outcome="fail"
  outcome_note="Negative assertion failed: ${negative_assertion_note}"
else
  outcome_note="All signals confirmed for gitnexus@${GITNEXUS_TAG}"
fi

# ---------------------------------------------------------------------------
# Human-readable summary to stdout
# ---------------------------------------------------------------------------
echo "calibrate-gitnexus-grammar-skip: outcome=${outcome}"
echo "  signal_1 (stderr regex): ${signal_1_status} — ${signal_1_note}"
echo "  signal_3 (artifact absence): ${signal_3_status} — ${signal_3_note}"
echo "  negative_assertion: ${negative_assertion_status} — ${negative_assertion_note}"
if [[ -n "${outcome_note}" ]]; then
  echo "  note: ${outcome_note}"
fi

# ---------------------------------------------------------------------------
# Emit calibration_result event per ADR-0037 + ADR-0058
# ---------------------------------------------------------------------------
event_json="$(jq -n -c \
  --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
  --arg ver "${GITNEXUS_TAG}" \
  --argjson dur "${duration_ms}" \
  --arg outcome "${outcome}" \
  --arg sig1 "${signal_1_status}: ${signal_1_note}" \
  --arg sig3 "${signal_3_status}: ${signal_3_note}" \
  --arg neg "${negative_assertion_status}: ${negative_assertion_note}" \
  --arg note "${outcome_note}" \
  '{
    event: "calibration_result",
    timestamp: $ts,
    server: "gitnexus",
    mechanism: "fr-4b-gitnexus-grammar-skip",
    version: $ver,
    duration_ms: $dur,
    outcome: $outcome,
    signals: {
      signal_1: $sig1,
      signal_3: $sig3,
      negative_assertion: $neg
    },
    note: $note
  }')"

log_mcp_event "${event_json}"

# ---------------------------------------------------------------------------
# Exit code
# ---------------------------------------------------------------------------
case "${outcome}" in
  pass)
    exit 0
    ;;
  drift_detected)
    exit 2
    ;;
  fail)
    exit 1
    ;;
  *)
    exit 1
    ;;
esac
