# `.claude/settings.json` — Authorization & Policy Notes

Documentation for the `.claude/settings.json` file in this directory. Claude Code's settings loader silently drops fields it doesn't recognize (including `_notes`), so this trail lives in a sibling file the loader doesn't read.

## Purpose

Team-wide Claude Code settings for the feature-pipeline project. Authored by T0.5 of `working/feature/execution-pipeline-design-r1/plan-v2.md`.

## Permission policy

Narrow allow-list per KB-cc-design Principle 6 (permissions-as-safety-net). Each entry pins to a specific script path; the trailing `:*` permits arbitrary arguments to that script. Per Blueprint v5 § Security Considerations.

## User authorization

User explicitly authorized the creation of `settings.json` with 7 wildcard `Bash(...:*)` entries at T0.5 (2026-05-22) via Gate disposition during execution of `plan-v2.md`. The authorization specifically covered:

- Wildcard `:*` in each entry (permits arbitrary arguments to that named script)
- Script names match Plan v2 T0.4-T0.5 inventory exactly; no glob beyond named scripts

## Reserved future-extensibility

An 8th allow-list entry for `scan_unsurfaced_deviations.py` is intentionally NOT present. That script is flagged in Blueprint Future Extensibility (Risk 7 mitigation candidate) but NOT in scope for this feature. When/if that script lands in a follow-on feature, add:

```
"Bash(python3 .claude/skills/auditing-shared/scripts/scan_unsurfaced_deviations.py:*)"
```

## Why this file exists separately

Per cc-critique audit (2026-05-22): the `_notes` field originally embedded inside `settings.json` was silently dropped by the loader. The audit-trail documentation was therefore invisible to Claude Code at runtime. Moving the documentation to this sibling file preserves the trail in a human-readable, version-controlled location while keeping `settings.json` to the fields the loader actually consumes.

---

## issue-capture-mechanism-r1 (Phase 5, T5.6) — PreToolUse hook for issue-capture-author intercept

**Added**: 2026-05-25 (issue-capture-mechanism-r1 Phase 5)

**What changed**: Added top-level `hooks` block to `.claude/settings.json` with a `PreToolUse` entry matching `Task` and pointing to `${CLAUDE_PROJECT_DIR}/.claude/hooks/intercept-issue-capture-agent.sh`.

**Why**: Per Plan T5.6 + FR-3 + ADR-0047 three-layer enforcement. The hook intercepts Task tool dispatches and:

- For `subagent_type: issue-capture-author` → emits `permissionDecision: "ask"` with a spawn-prompt preview (forces user authorization BEFORE the agent runs; Layer 3 enforcement of AC-FR-3-b)
- For any other subagent_type → emits `permissionDecision: "allow"` (silent fast-path)
- On any error (missing jq, malformed stdin) → fail-OPEN with `allow` (per NFR-2; the hook MUST NEVER block legitimate flows)

**User authorization**: this is the first `hooks` entry in this project (project-first per F-002 — no `hooks` key existed in `settings.json` before this commit). The hook does NOT add a `permissions.allow` entry per cc-design §Permission Policy — hooks run via Claude Code's platform mechanism, not via Bash invocation.

**Performance budget**: per D-11, allow path p95 ≤ 200ms (measured: 143.7ms); ask path p95 ≤ 500ms (measured: 292.6ms). Latency results in `working/feature/issue-capture-mechanism-r1/hook-latency-results.json`.

**Hook script invariants** (per Plan T5.1):

- `set -u` (no `-e`) — explicit error handling; never silent termination
- All paths exit 0 — fail-OPEN per NFR-2
- jq used for input parsing AND output construction (safe JSON; no string-interpolation injection)

**Test harness**: `.claude/hooks/test_intercept_issue_capture_agent.py` runs a 5-fixture golden-file suite (ask path + 2 allow paths + 2 fail-open paths). Results in `working/feature/issue-capture-mechanism-r1/hook-golden-results.json`.
