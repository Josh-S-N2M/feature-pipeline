#!/usr/bin/env bash
# intercept-issue-capture-agent.sh — PreToolUse hook for issue-capture-author intercept
# Per Plan T5.1 + cc-design §Hook Patterns + ADR-0047 three-layer enforcement.
#
# Contract: Input = PreToolUse event JSON on stdin; Output = hookSpecificOutput JSON on stdout.
# All paths exit 0 (fail-OPEN per NFR-2 — hook MUST NEVER block legitimate flows).
#
# Behavior:
#   subagent_type == "issue-capture-author" → permissionDecision: "ask" + spawn-prompt preview
#   any other subagent_type               → permissionDecision: "allow" (silent fast-path)
#   error (missing jq, malformed stdin)   → stderr diagnostic + permissionDecision: "allow"
#
# Stateless: each invocation is a fresh process; safe under any concurrency model.
# Tools: bash, jq (devcontainer-standard; verified Phase 0 T0.5).

set -u  # set NOT -e — we want to handle errors explicitly and fail-OPEN

# ---- Read event from stdin ----
EVENT_JSON="$(cat 2>/dev/null || true)"

if [ -z "$EVENT_JSON" ]; then
    echo "[intercept-issue-capture-agent] empty stdin; fail-OPEN with allow" >&2
    printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"allow","permissionDecisionReason":"hook received empty stdin; fail-open"}}\n'
    exit 0
fi

# ---- Extract subagent_type via jq ----
if ! command -v jq >/dev/null 2>&1; then
    echo "[intercept-issue-capture-agent] jq not on PATH; fail-OPEN with allow" >&2
    printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"allow","permissionDecisionReason":"hook prerequisite missing (jq); fail-open"}}\n'
    exit 0
fi

SUBAGENT_TYPE="$(echo "$EVENT_JSON" | jq -r '.tool_input.subagent_type // empty' 2>/dev/null)"

if [ -z "$SUBAGENT_TYPE" ]; then
    # Not a Task event OR malformed; fast-path allow.
    printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"allow","permissionDecisionReason":"no subagent_type in event; fast-path allow"}}\n'
    exit 0
fi

# ---- Branch on subagent_type ----
if [ "$SUBAGENT_TYPE" = "issue-capture-author" ]; then
    # Intercept: ask user before the spawn.
    PROMPT_PREVIEW="$(echo "$EVENT_JSON" | jq -r '.tool_input.prompt // "(no prompt)"' 2>/dev/null | head -c 500)"
    DESC_PREVIEW="$(echo "$EVENT_JSON" | jq -r '.tool_input.description // "(no description)"' 2>/dev/null | head -c 200)"

    # Compose the ask-reason text (shown to user). Use jq to safely JSON-encode the string.
    REASON_JSON="$(jq -n --arg desc "$DESC_PREVIEW" --arg prompt "$PROMPT_PREVIEW" \
      '"About to spawn issue-capture-author sub-agent.\n\nDescription:\n" + $desc + "\n\nPrompt preview:\n" + $prompt + "\n\nProceed?"')"

    # Emit ask decision with the composed reason.
    jq -n --argjson reason "$REASON_JSON" \
      '{hookSpecificOutput: {hookEventName: "PreToolUse", permissionDecision: "ask", permissionDecisionReason: $reason}}'
    echo "[intercept-issue-capture-agent] ask emitted for issue-capture-author spawn" >&2
    exit 0
fi

# ---- All other subagent_types: fast-path allow ----
printf '{"hookSpecificOutput":{"hookEventName":"PreToolUse","permissionDecision":"allow","permissionDecisionReason":"subagent_type %s not intercepted; fast-path allow"}}\n' "$SUBAGENT_TYPE"
exit 0
