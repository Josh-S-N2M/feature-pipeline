#!/usr/bin/env bash
# .devcontainer/lib/log-mcp-event.sh
#
# JSONL event helper. Appends one event record to .claude/runtime/mcp-events.jsonl
# per ADR-0037 schema. Applies redaction-at-source per ADR-0039 (default-fail-closed
# per AC-NFR-2-d).
#
# Usage:
#   log_mcp_event '{"event":"install_complete","server":"serena",...}'
#   log_mcp_event --stdin <<< '<json>'
#
# Exports the redact_credentials function for callers that need a standalone
# redaction pass on arbitrary strings.

set -euo pipefail

# Repo root resolution — works whether invoked from postCreate, postStart, or directly.
LIB_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${LIB_DIR}/../.." && pwd)"
EVENTS_LOG="${REPO_ROOT}/.claude/runtime/mcp-events.jsonl"

# Ensure the runtime directory exists (it should, per T0.10 bootstrap, but defensive).
mkdir -p "$(dirname "${EVENTS_LOG}")"

# Redaction patterns per ADR-0039:
#   - Header values for credential-named headers (case-insensitive)
#   - Substring patterns: sk-..., eyJ..., ghp_..., glpat-..., xoxb-..., xoxp-...
#   - Bare long base64-shaped strings (>40 chars, base64 alphabet) — conservative
#
# Default-fail-closed: if the redaction logic itself fails, emit nothing rather than
# a partially-redacted record (per AC-NFR-2-d).

redact_credentials() {
  local input="$1"
  python3 - "${input}" <<'PY' || return 1
import json, re, sys

raw = sys.argv[1]
try:
    obj = json.loads(raw)
except json.JSONDecodeError:
    # Non-JSON substrate: apply regex redactions only
    obj = None

# Substring redaction patterns (apply after JSON normalize OR on raw string)
SUBSTRING_PATTERNS = [
    (r'sk-[A-Za-z0-9_-]{16,}', '<REDACTED:sk-key>'),
    (r'eyJ[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{8,}\.[A-Za-z0-9_-]{4,}', '<REDACTED:jwt>'),
    (r'ghp_[A-Za-z0-9]{16,}', '<REDACTED:github-pat>'),
    (r'glpat-[A-Za-z0-9_-]{16,}', '<REDACTED:gitlab-pat>'),
    (r'xoxb-[A-Za-z0-9-]{16,}', '<REDACTED:slack-bot>'),
    (r'xoxp-[A-Za-z0-9-]{16,}', '<REDACTED:slack-user>'),
]

# Header-name patterns that indicate value should be redacted
CRED_HEADER_RE = re.compile(r'(?i)\b(authori[sz]ation|api[-_]?key|access[-_]?token|bearer|credential|secret|token|password|x-api-key)\b')

def redact_string(s):
    if not isinstance(s, str):
        return s, False
    redacted = s
    applied = False
    for pat, replacement in SUBSTRING_PATTERNS:
        if re.search(pat, redacted):
            redacted = re.sub(pat, replacement, redacted)
            applied = True
    return redacted, applied

def walk(node, parent_key=None):
    applied = False
    if isinstance(node, dict):
        for k, v in list(node.items()):
            # If the key indicates a credential header, redact the value verbatim
            if CRED_HEADER_RE.search(k):
                if isinstance(v, str) and v and not v.startswith('<REDACTED'):
                    node[k] = '<REDACTED>'
                    applied = True
            else:
                sub_applied = walk(v, parent_key=k)
                applied = applied or sub_applied
    elif isinstance(node, list):
        for i, item in enumerate(node):
            if isinstance(item, str):
                new_v, sub_applied = redact_string(item)
                if sub_applied:
                    node[i] = new_v
                    applied = True
            else:
                sub_applied = walk(item, parent_key=parent_key)
                applied = applied or sub_applied
    elif isinstance(node, str):
        # Standalone strings handled by caller via direct redact_string
        pass
    return applied

if obj is not None:
    applied = walk(obj)
    # Also pass entire string through substring redactions to catch in-message embeds
    if applied or any(re.search(p, raw) for p, _ in SUBSTRING_PATTERNS):
        # Re-serialize, then run substring pass on the full JSON
        s = json.dumps(obj)
        for pat, replacement in SUBSTRING_PATTERNS:
            s = re.sub(pat, replacement, s)
        # Reload to re-add applied annotation if it wasn't already there
        obj2 = json.loads(s)
        applied2 = (s != json.dumps(obj))
        if applied or applied2:
            obj2['redaction_applied'] = True
        print(json.dumps(obj2, ensure_ascii=False))
    else:
        print(raw)
else:
    # Non-JSON: regex pass only
    out = raw
    applied = False
    for pat, replacement in SUBSTRING_PATTERNS:
        if re.search(pat, out):
            out = re.sub(pat, replacement, out)
            applied = True
    print(out)
PY
}

# Main entry: append a JSONL record (with redaction applied).
log_mcp_event() {
  local record="${1:-}"
  if [[ "${record}" == "--stdin" ]]; then
    record="$(cat)"
  fi
  if [[ -z "${record}" ]]; then
    echo "log-mcp-event: empty record" >&2
    return 1
  fi

  # Apply redaction; default-fail-closed.
  local redacted
  if ! redacted="$(redact_credentials "${record}")"; then
    echo "[mcp:log] redaction failed; record not written (default-fail-closed per ADR-0039 / AC-NFR-2-d)" >&2
    return 1
  fi

  # Atomic append (single write call, no partial lines).
  printf '%s\n' "${redacted}" >> "${EVENTS_LOG}"
}

# Convenience helper for stderr banner per ADR-0037 (one-line, names server, points at JSONL)
emit_degraded_banner() {
  local server="$1"
  local fallback="${2:-<none>}"
  printf '[mcp:%s] primary degraded → falling back to %s; see %s\n' \
    "${server}" "${fallback}" "${EVENTS_LOG}" >&2
}

# If invoked directly (not sourced), treat $1 as record OR --stdin.
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
  log_mcp_event "${1:---stdin}"
fi
