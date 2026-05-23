---
id: AT-devcontainer-mcp-provisioning-r1
version: 1.0.3
status: draft
doc_type: AcceptanceTests
feature_slug: devcontainer-mcp-provisioning-r1
derived_from:
  - working/feature/devcontainer-mcp-provisioning-r1/prd-v3.md
  - working/feature/devcontainer-mcp-provisioning-r1/blueprint-v3.md
  - working/feature/devcontainer-mcp-provisioning-r1/plan-v1.md
generated: 2026-05-23T00:00:00Z
generated_by: test-acceptance-author
---

# Acceptance Tests — devcontainer-mcp-provisioning-r1

## Overview

This document specifies concrete verification paths for the **51 Acceptance Criteria** authored in `blueprint-v3.md` §Acceptance Criteria (11 AC-FR-*, 10 AC-CC-*, 7 AC-CS-*, 6 AC-NFR-*, 2 AC-X-*; plan-v1 reviewer-verified count 51/51). Each AC is mapped to one or more tests below. Tests use these types:

- **inspection** — file-existence / frontmatter / grep / `yq` / `jq` assertion; runs in seconds (L1).
- **lifecycle-script-run** — execute a devcontainer lifecycle script (`postCreate.sh`, `postStart.sh`, `mcp-ping.sh`) against a real or stubbed environment; observe output + side-effects (L2/L3).
- **audit-run** — invoke `python .claude/skills/auditing-mcp/scripts/audit_mcp.py --with-runtime` (or a specific OP rule script) against repo state; observe exit code + report contents (L2/L3).
- **integration** — script-level unit-style test with synthetic fixtures (L2).
- **e2e** — live Codespace rebuild / postStart cycle / failure-mode rehearsal (L3); converges on plan tasks T5.2–T5.5.
- **manual** — operator-interactive verification (e.g., `claude mcp list` from inside Claude Code session); recorded in `verify-at-execution.md`.
- **rebuild-measurement** — measured-duration variant of e2e for NFR-1 timing ACs.

Each test names the plan task(s) that produce the artifact under test (per the plan-v1 Acceptance Test Cross-Reference, lines 1083–1167). The **Hard-Gate Enforcement Test** (§ Hard-Gate Enforcement Test) is one shared verification covering the triplet AC-CC-5 + AC-FR-11-c + AC-NFR-2-c per MINOR-V3-001 disposition, anchored at plan task T5.4 (seeded-BLOCKER simulation).

Coverage: **51 / 51 ACs covered**, **0 ACs orphaned**.

## AC Coverage Matrix

| AC ID | Test ID(s) | Test type | Layer (L1/L2/L3) |
|---|---|---|---|
| AC-FR-1-a | AT-001 | manual + e2e | L3 |
| AC-FR-1-b | AT-002 | lifecycle-script-run | L2/L3 |
| AC-FR-1-c | AT-003 | lifecycle-script-run | L2/L3 |
| AC-CC-1 | AT-004 | inspection + manual | L1/L3 |
| AC-FR-2-a | AT-005 | inspection | L1 |
| AC-FR-2-b | AT-006 | e2e | L3 |
| AC-CC-2 | AT-007 | inspection | L1 |
| AC-CC-3 | AT-008 | inspection (grep-sweep) | L1 |
| AC-FR-4-a | AT-009 | lifecycle-script-run | L2 |
| AC-FR-4-b | AT-010 | lifecycle-script-run | L2 |
| AC-FR-5-a | AT-011 | inspection (grep) | L1 |
| AC-FR-5-b | AT-012 | lifecycle-script-run | L2/L3 |
| AC-X-1 | AT-013 | lifecycle-script-run | L2/L3 |
| AC-CC-4 | AT-014 | inspection (grep) | L1 |
| AC-CS-6 | AT-015 | inspection | L1 |
| AC-FR-8-a | AT-016 | lifecycle-script-run | L2/L3 |
| AC-FR-8-b | AT-017 | lifecycle-script-run | L2/L3 |
| AC-FR-8-c | AT-018 | lifecycle-script-run | L2/L3 |
| AC-FR-8-d | AT-019 | lifecycle-script-run | L2/L3 |
| AC-FR-8-e | AT-020 | manual | L2/L3 |
| AC-CS-4 | AT-021 | lifecycle-script-run | L2/L3 |
| AC-CS-5 | AT-022 | lifecycle-script-run | L2/L3 |
| AC-CC-6 | AT-023 | inspection (jsonl parse) | L2/L3 |
| AC-FR-9-a | AT-024 | lifecycle-script-run | L3 |
| AC-FR-9-b | AT-025 | lifecycle-script-run | L3 |
| AC-FR-9-c | AT-026 | lifecycle-script-run | L3 |
| AC-FR-9-d | AT-027 | audit-run + inspection | L2 |
| AC-CC-7 | AT-028 | inspection | L1 |
| AC-FR-10-a | AT-029 | inspection + lifecycle-script-run | L1/L2 |
| AC-FR-10-b | AT-030 | inspection (jsonl parse) | L2 |
| AC-FR-10-c | AT-031 | inspection + manual | L1/L2 |
| AC-FR-10-d | AT-032 | audit-run (OP-6) | L2/L3 |
| AC-FR-11-a | AT-033 | inspection | L1 |
| AC-FR-11-b | AT-034 | inspection | L1 |
| AC-FR-11-c | AT-HG (Hard-Gate Enforcement) | audit-run + e2e | L3 |
| AC-FR-11-d | AT-035 | inspection (grep cross-ref) | L1 |
| AC-CC-5 | AT-HG (Hard-Gate Enforcement) | audit-run + e2e | L3 |
| AC-CC-8 | AT-036 | inspection (frontmatter + dir) | L1 |
| AC-CC-9 | AT-037 | inspection (grep ADR cite) | L1 |
| AC-CC-10 | AT-038 | inspection (frontmatter + body) | L1 |
| AC-NFR-1-a | AT-039 | rebuild-measurement | L3 |
| AC-NFR-1-b | AT-040 | rebuild-measurement | L3 |
| AC-NFR-2-a | AT-041 | inspection + audit-run | L1/L2 |
| AC-NFR-2-c | AT-HG (Hard-Gate Enforcement) | audit-run + e2e | L3 |
| AC-NFR-2-d | AT-042 | audit-run (OP-6) + inspection | L2 |
| PRD-NFR-4 / UI-7 / OI-4 | AT-043 | manual (measurement) | L2 |
| AC-CS-1 | AT-044 | manual | L2 |
| AC-CS-2 | AT-045 | rebuild-measurement | L3 |
| AC-CS-3 | AT-046 | lifecycle-script-run | L2/L3 |
| AC-CS-7 | AT-047 | inspection | L1 |
| AC-CS-8 | AT-039 + AT-040 (shared) | rebuild-measurement | L3 |
| AC-CS-9 | AT-048 | lifecycle-script-run | L2/L3 |
| AC-X-2 | AT-049 | inspection + audit-run | L1/L2 |

**Total: 50 unique test IDs (AT-001..AT-049 + AT-HG).** The shared AT-HG verifies the AC-CC-5 + AC-FR-11-c + AC-NFR-2-c triplet per the MINOR-V3-001 disposition adopted at Plan v1.

> Note: AT-043 maps to **PRD-NFR-4 / UI-7 / OI-4** rather than to a Blueprint AC ID. Blueprint v3 declares no Blueprint-AC equivalent of the PRD's NFR-4: that PRD commitment was reframed at PRD v2 (per I-DR-006) into a Blueprint-author instruction inside UI-7's Owner/Needed-by note; Blueprint v3 tracks the measurement under OI-4 (Open Items). The methodology is operationalized via Plan T4.7 + PV-4.C19/C20 + PV-5.C21 per PA-OI-3 (RESOLVED-METHODOLOGY-ALIGNED). AT-043's methodology coverage is real and necessary; only the AC label is corrected here. AC-CS-8 shares verification with AC-NFR-1-a / AC-NFR-1-b (the cold + warm measurements). All 51 Blueprint v3 ACs covered.

## Functional Tests

### AT-001 — Seven MCP servers listed `connected` after fresh build

- **Maps to AC:** AC-FR-1-a
- **Test type:** manual + e2e
- **Layer:** L3 (cross-layer; observed in live Codespace)
- **Preconditions:** Fresh Codespace built from feature branch; `postCreate.sh` + `postStart.sh` have run to completion (T1.4 + T2.4 + T3.4 + T3.5 artifacts present).
- **Steps:**
  1. Open a Claude Code session inside the freshly-built Codespace.
  2. Run `claude mcp list`.
  3. Capture stdout.
- **Expected outcome:** stdout lists exactly 7 entries (`serena`, `mcp-openapi-schema`, `actionlint-mcp`, `terraform-mcp`, `gitnexus`, `context7`, `exa`); each carries `connected` status. No entry omitted; no extra entry (no `codebase-memory-mcp` per Gate-4 OI-1 closure).
- **Plan task refs:** T1.3, T2.4, T3.3, T3.4, T5.2.

### AT-002 — Per-server probe returns success for every server

- **Maps to AC:** AC-FR-1-b, AC-FR-4-a
- **Test type:** lifecycle-script-run
- **Layer:** L2 (script invocation) → L3 (live Codespace at T5.2)
- **Preconditions:** `.devcontainer/lib/mcp-ping.sh` exists (T3.1); `.mcp.json` registers 7 servers (T2.4); all 7 binaries on PATH (T3.4).
- **Steps:**
  1. From a shell inside the Codespace, run `.devcontainer/lib/mcp-ping.sh all`.
  2. Capture stdout JSON output and exit code.
- **Expected outcome:** Exit code 0. stdout contains 7 JSON objects, one per server, each with `result: "pass"` and a non-null `response` field. No JSON object carries `result: "fail"`.
- **Plan task refs:** T3.1, T3.2, T5.2.

### AT-003 — Probe failure surfaces specific server name + failure layer

- **Maps to AC:** AC-FR-1-c
- **Test type:** lifecycle-script-run (negative path; failure-injected)
- **Layer:** L2 (synthetic) → L3 (live rehearsal at T5.5)
- **Preconditions:** All artifacts from AT-002; one server deliberately broken (e.g., `terraform-mcp` binary path shadowed off PATH per T5.5 description).
- **Steps:**
  1. Move or rename the `terraform-mcp` binary so it is not on PATH.
  2. Run `.devcontainer/lib/mcp-ping.sh terraform-mcp`.
  3. Capture stdout JSON + stderr.
- **Expected outcome:** stdout JSON record carries `server: "terraform-mcp"`, `result: "fail"`, `failure_layer` field set to one of `{transport, auth, runtime}` (here, expected `transport` since binary missing). Either stderr or stdout `message_redacted` field names the specific server (`terraform-mcp`). The output is operator-actionable: a reader can identify which server failed and which layer to investigate.
- **Plan task refs:** T3.1, T3.5, T5.5.

### AT-004 — `.mcp.json` declares exactly seven `mcpServers` entries; all connect

- **Maps to AC:** AC-CC-1
- **Test type:** inspection + manual
- **Layer:** L1 (file inspection) + L3 (live `claude mcp list` confirmation)
- **Preconditions:** `.mcp.json` exists at repo root (T2.4).
- **Steps:**
  1. Run `jq '.mcpServers | keys | length' .mcp.json`.
  2. Run `jq -r '.mcpServers | keys[]' .mcp.json | sort` and capture.
  3. (L3) From a fresh Codespace, run `claude mcp list` and confirm all 7 connect.
- **Expected outcome:** Step 1 returns `7`. Step 2 returns the sorted list: `actionlint-mcp`, `context7`, `exa`, `gitnexus`, `mcp-openapi-schema`, `serena`, `terraform-mcp`. Step 3 (L3) shows all 7 `connected`.
- **Plan task refs:** T2.4, T5.2.

### AT-005 — Each affected agent file shows MCP tool entries

- **Maps to AC:** AC-FR-2-a
- **Test type:** inspection
- **Layer:** L1
- **Preconditions:** 8 agent files edited per T4.1.
- **Steps:**
  1. For each of the 8 affected agents (`design-api.md`, `design-cicd.md`, `design-iac.md`, `discovery-external-researcher.md`, `discovery-codebase-researcher.md`, `review-architecture-auditor.md`, `design-cc.md`, `design-codespaces.md`): run `yq '.tools[]' .claude/agents/<agent>.md | grep -c '^mcp__'`.
- **Expected outcome:** Each of the 8 invocations returns a count ≥ 1; the entries match the consumer-mapping table in Blueprint v3 §Claude Code Design.
- **Plan task refs:** T4.1.

### AT-006 — MCP tools callable from affected agents

- **Maps to AC:** AC-FR-2-b
- **Test type:** e2e
- **Layer:** L3
- **Preconditions:** AT-005 passes; live Codespace post-Phase-5 with `.mcp.json` registered + agent allowlists in place.
- **Steps:**
  1. In a live Claude Code session, dispatch one of the 8 affected sub-agents (e.g., `design-iac`).
  2. From within that agent's context, attempt to invoke a tool from its mcp__ allowlist (e.g., a `mcp__terraform-mcp__*` call).
  3. Observe whether the tool invocation succeeds (returns a non-error response from the MCP server).
- **Expected outcome:** Tool call returns successfully (no "tool not in allowlist" error); the response demonstrates the MCP server processed the call.
- **Plan task refs:** T2.4, T4.1.

### AT-007 — Affected agents carry prescribed entries; no others

- **Maps to AC:** AC-CC-2
- **Test type:** inspection
- **Layer:** L1
- **Preconditions:** T4.1 complete.
- **Steps:**
  1. For each of the 8 affected agents, run `yq '.tools[]' .claude/agents/<agent>.md | grep '^mcp__' | sort > /tmp/<agent>-actual.txt`.
  2. Compare to the prescribed list (per consumer-mapping table in Blueprint §Claude Code Design + ADR-0040 Serena narrowing).
- **Expected outcome:** For each of the 8 agents: actual mcp__ entries == prescribed entries (set-equal). No extra entries (e.g., no `mcp__codebase-memory-mcp__*` anywhere).
- **Plan task refs:** T4.1.

### AT-008 — 28 non-consumer agents preserve zero `mcp__` entries (C-0445 invariant)

- **Maps to AC:** AC-CC-3
- **Test type:** inspection (grep-sweep)
- **Layer:** L1
- **Preconditions:** T4.1 + T4.2 complete; 36 total agent files in `.claude/agents/`.
- **Steps:**
  1. Run the grep-sweep script from plan T4.2:
     ```bash
     CONSUMERS="design-api|design-cicd|design-iac|discovery-external-researcher|discovery-codebase-researcher|review-architecture-auditor|design-cc|design-codespaces"
     for f in .claude/agents/*.md; do
       base=$(basename "$f" .md)
       if ! echo "$base" | grep -qE "^($CONSUMERS)$"; then
         if grep -q '^[[:space:]]*-[[:space:]]*mcp__' "$f"; then
           echo "REGRESSION: $f"
         fi
       fi
     done
     ```
- **Expected outcome:** Zero `REGRESSION:` lines emitted. (Asserts AC-CC-3 invariant: 28 of 36 agents carry no mcp__ entries.)
- **Plan task refs:** T4.2, T4.3 (OP-3 audit rule).

### AT-009 — Per-server probe acceptance returns success (all 7)

- **Maps to AC:** AC-FR-4-a (also covered by AT-002 for AC-FR-1-b)
- **Test type:** lifecycle-script-run
- **Layer:** L2
- **Preconditions:** All 7 servers reachable; `mcp-ping.sh` exists.
- **Steps:**
  1. Run `.devcontainer/lib/mcp-ping.sh all` and capture exit code + per-server output.
- **Expected outcome:** Exit code 0; 7 entries with `result: "pass"`.
- **Plan task refs:** T3.1, T3.2, T5.2.

### AT-010 — Probe failure record contains server name, input, response/error

- **Maps to AC:** AC-FR-4-b
- **Test type:** lifecycle-script-run (negative path)
- **Layer:** L2
- **Preconditions:** `mcp-ping.sh` exists; one server fault-injected per AT-003.
- **Steps:**
  1. Break one server (e.g., shadow binary).
  2. Run `.devcontainer/lib/mcp-ping.sh terraform-mcp`.
  3. Inspect the failure record (stdout JSON).
- **Expected outcome:** Failure record carries: `server: "terraform-mcp"`, `probe_input` (the JSON-RPC payload sent), `response_or_error` (the error response or transport-level error string, redacted per ADR-0039), `failure_layer` (`transport`/`auth`/`runtime`). All three named pieces present.
- **Plan task refs:** T3.1, T3.2, T5.5.

### AT-011 — No literal credential values in committed files

- **Maps to AC:** AC-FR-5-a (also see AT-014 for AC-CC-4)
- **Test type:** inspection (grep)
- **Layer:** L1
- **Preconditions:** Repo at any commit after T2.4 + T4.1.
- **Steps:**
  1. Run `git grep -E '(AKIA|ASIA|ghp_|gho_|ghu_|ghs_|ghr_|sk_(live|test)_|-----BEGIN.*PRIVATE KEY-----)'` over the working tree.
  2. Inspect `.mcp.json`, `.claude/agents/*.md`, `.devcontainer/*` specifically.
- **Expected outcome:** Zero matches. `.mcp.json` references env-vars via `${VAR}` substitution only (e.g., `${CONTEXT7_API_KEY}`, `${EXA_API_KEY}`, `${TFE_TOKEN}`), no literal values.
- **Plan task refs:** T1.4, T2.4.

### AT-012 — Unset credential env-var → clearly named "missing credential" probe failure

- **Maps to AC:** AC-FR-5-b
- **Test type:** lifecycle-script-run (negative path)
- **Layer:** L2 → L3 (T5.5)
- **Preconditions:** `.mcp.json` references `${CONTEXT7_API_KEY}`; `mcp-auth-probe.sh` exists (T3.2).
- **Steps:**
  1. Explicitly `unset CONTEXT7_API_KEY` in shell environment (or remove from Codespaces secrets in T5.5 live).
  2. Run `.devcontainer/lib/mcp-ping.sh context7`.
  3. Inspect the JSON output.
- **Expected outcome:** Output record carries `server: "context7"`, `result: "fail"`, `failure_layer: "auth"`, `message_redacted` containing the phrase `missing env-var CONTEXT7_API_KEY` (or equivalent canonical "missing credential" string). Failure is operator-actionable — the failure message names the env-var.
- **Plan task refs:** T3.1, T3.2, T5.5.

### AT-013 — Env-var-absent failure distinguishable from auth-with-key-rejected failure

- **Maps to AC:** AC-X-1
- **Test type:** lifecycle-script-run (negative path; two variants)
- **Layer:** L2 → L3 (T5.5)
- **Preconditions:** `.mcp.json` references `${CONTEXT7_API_KEY}`; `postStart.sh` writes through redaction filter (T3.5).
- **Steps:**
  1. **Variant A (env-var absent):** `unset CONTEXT7_API_KEY`; run `postStart.sh`; tail `.claude/runtime/mcp-events.jsonl`.
  2. **Variant B (auth rejected):** Set `CONTEXT7_API_KEY` to a syntactically-valid-but-invalid value (e.g., `invalid-key-for-test`); run `postStart.sh`; tail `mcp-events.jsonl`.
  3. Compare the two `readiness_probe` records.
- **Expected outcome:**
  - Variant A record: `result: "fail"`, `failure_layer: "auth"`, `message_redacted` matches `missing env-var <NAME>` (per AC-X-1 contract); stderr banner names the missing env-var.
  - Variant B record: `result: "fail"`, `failure_layer: "auth"`, `message_redacted` matches a different canonical string (e.g., `auth rejected by server`).
  - The two records are textually distinguishable by `message_redacted` content (per AC-X-1 distinguishability requirement). No literal API-key value appears in either record (per AC-NFR-2-d redaction).
- **Plan task refs:** T3.1, T3.2, T3.5, T5.5.

### AT-014 — Zero literal credentials in `.mcp.json` / agent files / devcontainer / mcp-events.jsonl

- **Maps to AC:** AC-CC-4
- **Test type:** inspection (grep)
- **Layer:** L1
- **Preconditions:** Repo post-Phase-3 (T3.6 verified `.gitignore` carries `mcp-events.jsonl`).
- **Steps:**
  1. Run `git grep -nE '(AKIA[0-9A-Z]{16}|ASIA[0-9A-Z]{16}|ghp_[A-Za-z0-9]{36,}|sk_(live|test)_[A-Za-z0-9]{20,}|-----BEGIN [A-Z ]*PRIVATE KEY-----)' -- .mcp.json '.claude/agents/*.md' '.devcontainer/' '.claude/runtime/mcp-events.jsonl'`.
  2. Confirm `.claude/runtime/mcp-events.jsonl` is `.gitignore`'d via `git check-ignore .claude/runtime/mcp-events.jsonl`.
- **Expected outcome:** Step 1: zero matches. Step 2: `git check-ignore` prints the path (confirming ignore rule active).
- **Plan task refs:** T2.4, T3.6, T4.1, T4.3 (OP-9/OP-10).

### AT-015 — `.devcontainer/devcontainer.json` resolves env vars via `containerEnv`

- **Maps to AC:** AC-CS-6
- **Test type:** inspection
- **Layer:** L1
- **Preconditions:** T1.4 complete.
- **Steps:**
  1. Run `jq '.containerEnv' .devcontainer/devcontainer.json`.
- **Expected outcome:** Output is a JSON object that maps at minimum `CONTEXT7_API_KEY`, `EXA_API_KEY`, `TFE_TOKEN` to `${localEnv:<NAME>}` (or equivalent Codespaces-secret-resolution syntax). No literal values present.
- **Plan task refs:** T1.4.

### AT-016 — postCreate emits consolidated health-check output for all seven servers

- **Maps to AC:** AC-FR-8-a
- **Test type:** lifecycle-script-run
- **Layer:** L2 → L3 (T5.2)
- **Preconditions:** `postCreate.sh` exists (T3.4); `.mcp.json` registers 7 servers.
- **Steps:**
  1. Run `bash .devcontainer/postCreate.sh` in a fresh container or rehearsed environment.
  2. Capture stdout + stderr + the resulting `.claude/runtime/mcp-events.jsonl`.
- **Expected outcome:** stdout contains a consolidated summary covering all 7 servers (e.g., per-server completion lines or a final summary table). `mcp-events.jsonl` contains **5 `install_complete` records** (one per OSS-local install: `serena`, `mcp-openapi-schema`, `actionlint-mcp`, `terraform-mcp`, `gitnexus`). The 2 HTTP-transport servers (`context7`, `exa`) have no `install_complete` record; their availability is exercised by the postCreate auth-probe (T3.2) and the postStart readiness_probe (T3.5). The consolidated stdout summary still covers all 7. Exit code 0 on success. Aligns with Plan T3.4 + PV-5.C5.
- **Plan task refs:** T3.4, T5.2.

### AT-017 — postStart re-runs the readiness check

- **Maps to AC:** AC-FR-8-b
- **Test type:** lifecycle-script-run
- **Layer:** L2 → L3 (T5.2 + T5.3)
- **Preconditions:** `postStart.sh` exists (T3.5); `.mcp.json` registers 7 servers.
- **Steps:**
  1. Run `bash .devcontainer/postStart.sh` once; capture jsonl record count.
  2. Run it a second time (simulating session re-attach beyond staleness threshold).
  3. Recount jsonl records.
- **Expected outcome:** First run appends 7 `readiness_probe` records; second run appends 7 *additional* `readiness_probe` records (total 14, two cycles). Each cycle is a coherent group of 7 records sharing a `cycle_id` or close timestamps. Exit code 0 both runs.
- **Plan task refs:** T3.5, T5.2, T5.3.

### AT-018 — postAttach surfaces most-recent result or re-runs beyond 5-min staleness threshold

- **Maps to AC:** AC-FR-8-c (per PA-OI-2)
- **Test type:** lifecycle-script-run
- **Layer:** L2 → L3 (T5.5)
- **Preconditions:** `postStart.sh` exists; `lifecycle-hooks.md` documents the 5-minute staleness threshold (T2.2); `postAttach` hook wired to read most-recent probe block.
- **Steps:**
  1. Run `postStart.sh`; record timestamp on latest `readiness_probe` block.
  2. **Fresh case:** Within 5 minutes, simulate postAttach (re-read the most-recent block); observe behavior.
  3. **Stale case:** Backdate the latest block's timestamps to >5 min ago (or wait ≥5 min); simulate postAttach again.
- **Expected outcome:**
  - Fresh case: postAttach surfaces the cached result (does NOT re-fire `postStart`); operator-visible stderr banner shows cached state.
  - Stale case: postAttach detects staleness (delta > 5 min), automatically re-runs `postStart.sh`; new 7-record block is appended.
- **Plan task refs:** T3.5 (§D-6 resolution).

### AT-019 — Failure at any lifecycle boundary surfaces server name + failing layer + remediation hint

- **Maps to AC:** AC-FR-8-d
- **Test type:** lifecycle-script-run (negative path)
- **Layer:** L2 → L3 (T5.5)
- **Preconditions:** `postStart.sh` exists; `KB-mcp-platform/references/operator-runbook.md` exists (T2.2) and contains remediation entries keyed by `failure_layer`.
- **Steps:**
  1. Inject a failure at one of the boundaries (e.g., make `terraform-mcp` binary fail at probe time).
  2. Run `postStart.sh`.
  3. Inspect both the stderr banner and the jsonl record.
- **Expected outcome:** stderr banner names the specific server (`terraform-mcp`) and the failing layer (`transport`/`auth`/`runtime`). jsonl record carries `server`, `failure_layer`, and a `remediation_hint_ref` that points to a section in `KB-mcp-platform/references/operator-runbook.md`. The remediation hint is operator-actionable.
- **Plan task refs:** T3.1, T3.5, T2.2.

### AT-020 — Operator can invoke health-check on demand

- **Maps to AC:** AC-FR-8-e
- **Test type:** manual
- **Layer:** L2/L3
- **Preconditions:** `.devcontainer/lib/mcp-ping.sh` exists; `KB-mcp-platform/references/operator-runbook.md` documents the on-demand invocation per T3.5 §D-6 resolution.
- **Steps:**
  1. From an operator shell in the Codespace, run `.devcontainer/lib/mcp-ping.sh all`.
  2. Observe stdout JSON + exit code.
- **Expected outcome:** Same shape as AT-002 (7 JSON objects); the command is operator-discoverable from the runbook; no extra setup required at invocation time.
- **Plan task refs:** T3.5 (operator-on-demand command).

### AT-021 — postStart appends exactly seven `readiness_probe` JSONL records per cycle

- **Maps to AC:** AC-CS-4
- **Test type:** lifecycle-script-run + jsonl inspection
- **Layer:** L2 → L3 (T5.2)
- **Preconditions:** `postStart.sh` exists; `.mcp.json` declares 7 servers; `.claude/runtime/mcp-events.jsonl` writable.
- **Steps:**
  1. Truncate `.claude/runtime/mcp-events.jsonl` (test setup).
  2. Run `postStart.sh` once.
  3. `grep -c '"event":"readiness_probe"' .claude/runtime/mcp-events.jsonl`.
  4. `jq -c 'select(.event=="readiness_probe") | .server' .claude/runtime/mcp-events.jsonl | sort -u | wc -l`.
- **Expected outcome:** Step 3 returns `7` (exactly seven readiness_probe records). Step 4 returns `7` (seven distinct server names — one record per server). Per Gate-4 OI-1 closure, no record for `codebase-memory-mcp`.
- **Plan task refs:** T3.5, T5.2.

### AT-022 — Partial probe failure → stderr banner names degraded count + exit 0

- **Maps to AC:** AC-CS-5
- **Test type:** lifecycle-script-run (negative path)
- **Layer:** L2 → L3 (T5.5)
- **Preconditions:** `postStart.sh` exists; one or more servers fault-injected.
- **Steps:**
  1. Break 2 of 7 servers (e.g., shadow `terraform-mcp` + unset `CONTEXT7_API_KEY`).
  2. Run `postStart.sh`; capture stderr + exit code.
- **Expected outcome:** stderr banner matches the pattern `MCP readiness: <N>/7 degraded` where `<N>=2`. Exit code is `0` (warn-and-continue per AC-CS-5). The 7 `readiness_probe` records are still written (5 with `result=pass`, 2 with `result=fail`).
- **Plan task refs:** T3.5, T5.5.

### AT-023 — Seven JSONL records carry `result` + `failure_layer` after postStart

- **Maps to AC:** AC-CC-6
- **Test type:** inspection (jsonl parse)
- **Layer:** L2 → L3 (T5.2)
- **Preconditions:** `postStart.sh` has run once on a real or simulated environment.
- **Steps:**
  1. Parse the last 7 `readiness_probe` records from `.claude/runtime/mcp-events.jsonl`:
     ```bash
     jq -c 'select(.event=="readiness_probe")' .claude/runtime/mcp-events.jsonl | tail -7
     ```
  2. For each record, confirm `.result in {"pass","fail"}` and (if `fail`) `.failure_layer` is present and non-empty.
- **Expected outcome:** All 7 records carry `result` ∈ {`pass`, `fail`}. Any record with `result: "fail"` ALSO carries `failure_layer` ∈ {`transport`, `auth`, `runtime`}. No record carries `result: "fail"` without a `failure_layer`.
- **Plan task refs:** T3.5, T5.2.

### AT-024 — Mid-run server failure surfaces structured record at next operator-visible surface

- **Maps to AC:** AC-FR-9-a
- **Test type:** lifecycle-script-run (failure-injected)
- **Layer:** L3 (T5.5)
- **Preconditions:** A real Codespace post-Phase-5 with all 7 servers healthy; one server is induced to fail mid-session.
- **Steps:**
  1. In a live session, kill or break a running MCP server process (e.g., `pkill -f gitnexus`).
  2. Trigger postStart re-run (or operator-on-demand probe).
  3. Inspect `.claude/runtime/mcp-events.jsonl` + stderr.
- **Expected outcome:** A new `readiness_probe` record for the broken server appears with `result: "fail"` and a `failure_layer`. A stderr banner names the degraded count. The operator can locate the failure from these two surfaces.
- **Plan task refs:** T3.5, T5.5.

### AT-025 — Tool-level error response includes server name + tool name + error

- **Maps to AC:** AC-FR-9-b
- **Test type:** lifecycle-script-run (synthetic) → e2e (T5.5)
- **Layer:** L3
- **Preconditions:** `.mcp.json` registered; one tool deliberately invoked against a broken server.
- **Steps:**
  1. From a Claude Code agent context that has a `mcp__terraform-mcp__*` tool allowlisted, invoke that tool while the server is broken (post fault-injection from AT-024).
  2. Capture the tool's error response surfaced to the agent.
- **Expected outcome:** The error response payload contains: (a) the server name (`terraform-mcp`), (b) the tool name invoked, (c) the underlying error string (transport-level or RPC error, redacted per ADR-0039). All three named pieces present.
- **Plan task refs:** T3.1, T5.5.

### AT-026 — Healthy→unhealthy transition visible in runtime log with timestamp + triggering event

- **Maps to AC:** AC-FR-9-c
- **Test type:** lifecycle-script-run (state-transition probe)
- **Layer:** L3 (T5.5)
- **Preconditions:** All 7 servers initially healthy (one healthy postStart cycle completed); fault is then injected.
- **Steps:**
  1. Run postStart with all servers healthy; observe the all-pass record block.
  2. Inject a server failure (per AT-024).
  3. Re-run postStart (or wait for the next cycle); observe the now-failing record.
- **Expected outcome:** The two postStart cycles in jsonl carry distinct timestamps; the second cycle's record for the affected server has changed from `result: "pass"` to `result: "fail"`; a `triggering_event` or equivalent field (or the cycle's `postStart` timestamp itself) marks the transition. An operator reading the jsonl tail can reconstruct the healthy→unhealthy transition without re-running anything.
- **Plan task refs:** T3.5, T5.5.

### AT-027 — No silent fallback — schema-level provision preserved, no runtime fires

- **Maps to AC:** AC-FR-9-d
- **Test type:** audit-run + inspection
- **Layer:** L2
- **Preconditions:** `KB-mcp-design/references/principles.md` exists (T2.3); `auditing-mcp/scripts/` contains OP-4 (T4.3); no fallback-registration code exists in this feature's runtime.
- **Steps:**
  1. Run `grep -E 'primary_degraded' .claude/skills/KB-mcp-design/references/principles.md` — confirm the schema-level provision is present.
  2. Run `grep -c 'primary_degraded' .claude/runtime/mcp-events.jsonl` (over a full post-T5.3 jsonl).
  3. Run the OP-4 audit rule against the repo.
- **Expected outcome:** Step 1 returns at least one match (`primary_degraded` schema documented). Step 2 returns `0` (no runtime primary_degraded event ever fires in this feature, since no fallback is provisioned per Gate-4 OI-1 closure). Step 3 (OP-4): audit reports PASS for the prose primary/fallback documentation requirement; no BLOCKER.
- **Plan task refs:** T2.3, T4.3 (OP-4), T5.5.

### AT-028 — primary_degraded schema-level provision present in `KB-mcp-design/references/principles.md`

- **Maps to AC:** AC-CC-7
- **Test type:** inspection
- **Layer:** L1
- **Preconditions:** T2.3 complete.
- **Steps:**
  1. Run `grep -nE '"event":[[:space:]]*"primary_degraded"' .claude/skills/KB-mcp-design/references/principles.md`.
  2. Confirm the schema block names the required fields (server, fallback, timestamp, etc., per ADR-0037).
- **Expected outcome:** Match found; the schema block enumerates the required fields per ADR-0037 schema definition.
- **Plan task refs:** T2.3.

### AT-029 — Per-server transport events captured at documented log location

- **Maps to AC:** AC-FR-10-a
- **Test type:** inspection + lifecycle-script-run
- **Layer:** L1 + L2
- **Preconditions:** `KB-mcp-platform/references/operator-runbook.md` documents `.claude/runtime/mcp-events.jsonl` as the canonical log location (T2.2); `postStart.sh` writes to that path (T3.5).
- **Steps:**
  1. Confirm runbook reference: `grep -n 'mcp-events.jsonl' .claude/skills/KB-mcp-platform/references/operator-runbook.md`.
  2. Run `postStart.sh`; confirm the file exists and contains transport-level event records.
- **Expected outcome:** Runbook names the path. Post-postStart, the file exists and contains 7 `readiness_probe` records (transport-level events).
- **Plan task refs:** T3.5, T2.2.

### AT-030 — Structured failure records reconstructable post-failure

- **Maps to AC:** AC-FR-10-b
- **Test type:** inspection (jsonl parse)
- **Layer:** L2
- **Preconditions:** `mcp-events.jsonl` contains records from at least one fault-injected postStart cycle (combined with AT-022 setup).
- **Steps:**
  1. `jq -c 'select(.result=="fail")' .claude/runtime/mcp-events.jsonl`.
  2. For each failure record, verify required fields: `event`, `timestamp`, `server`, `result`, `failure_layer`, `message_redacted`, `cycle_id` (or equivalent grouping field).
- **Expected outcome:** Every failure record carries all named fields; a developer or operator can reconstruct what happened (which server, when, which layer, what was tried) without re-running the failure.
- **Plan task refs:** T2.3, T3.5.

### AT-031 — "Tail MCP logs" command makes per-server log content readable

- **Maps to AC:** AC-FR-10-c
- **Test type:** inspection + manual
- **Layer:** L1/L2
- **Preconditions:** `operator-runbook.md` documents a tail command (T2.2).
- **Steps:**
  1. `grep -nE 'tail.*mcp-events.jsonl' .claude/skills/KB-mcp-platform/references/operator-runbook.md`.
  2. Run the documented command (e.g., `tail -f .claude/runtime/mcp-events.jsonl | jq -c 'select(.server=="gitnexus")'`).
- **Expected outcome:** Step 1: match. Step 2: command runs without error; per-server filtering works (jq filter produces server-scoped output).
- **Plan task refs:** T2.2, T3.5.

### AT-032 — Credential values redacted in runtime log (per ADR-0039)

- **Maps to AC:** AC-FR-10-d
- **Test type:** audit-run (OP-6)
- **Layer:** L2 → L3 (T5.4)
- **Preconditions:** `auditing-mcp/scripts/` contains OP-6 (T4.3); jsonl contains records from real postStart cycles (or synthetic credential-containing fixtures).
- **Steps:**
  1. Place a synthetic credential-shape string (e.g., `ghp_FAKE_TEST_CREDENTIAL_FOR_FIXTURE_001`) into a test fixture path covered by OP-6 (per PA-OI-5 test-fixtures setup).
  2. Run `python .claude/skills/auditing-mcp/scripts/audit_op6_runtime_log_redaction.py` (or invoke via `audit_mcp.py --rule OP-6`).
  3. Capture audit report.
- **Expected outcome:** OP-6 fires BLOCKER on the seeded credential (proving the rule works); after the fixture is removed, OP-6 passes against the live `mcp-events.jsonl`. (The live-pass case is what counts for AC-FR-10-d; the seeded-fail case proves the rule is real.)
- **Plan task refs:** T3.4, T3.5, T4.3 (OP-6).

### AT-033 — `KB-mcp-platform/SKILL.md` exists in trifecta shape

- **Maps to AC:** AC-FR-11-a
- **Test type:** inspection
- **Layer:** L1
- **Preconditions:** T2.1 + T2.2 complete.
- **Steps:**
  1. Confirm file exists: `test -f .claude/skills/KB-mcp-platform/SKILL.md`.
  2. Run `yq '.name, .description' .claude/skills/KB-mcp-platform/SKILL.md`.
  3. Confirm directory layout: `references/` exists; expected reference files present (`operator-runbook.md`, `gitnexus-and-fallback.md`, etc., per Blueprint Skills table).
- **Expected outcome:** File exists; frontmatter `name` lowercase-hyphenated; `description` field present and ends with sister-cross-reference to `KB-mcp-design`; `references/` directory populated.
- **Plan task refs:** T2.1, T2.2, T5.4.

### AT-034 — `KB-mcp-design/SKILL.md` exists in trifecta shape

- **Maps to AC:** AC-FR-11-b
- **Test type:** inspection
- **Layer:** L1
- **Preconditions:** T2.3 complete.
- **Steps:**
  1. Confirm file: `test -f .claude/skills/KB-mcp-design/SKILL.md`.
  2. Confirm exactly two reference files: `ls .claude/skills/KB-mcp-design/references/ | sort` → expect `patterns-and-anti-patterns.md` + `principles.md` only.
  3. Confirm no `assets/` directory: `! test -d .claude/skills/KB-mcp-design/assets`.
  4. Frontmatter `description` ends with sister-cross-reference to `KB-mcp-platform`.
- **Expected outcome:** All four checks pass.
- **Plan task refs:** T2.3, T5.4.

### AT-035 — KB-mcp-platform ↔ KB-mcp-design cross-reference; both name GitNexus

- **Maps to AC:** AC-FR-11-d
- **Test type:** inspection (grep cross-ref)
- **Layer:** L1
- **Preconditions:** T2.1 + T2.2 + T2.3 complete.
- **Steps:**
  1. `grep -n 'KB-mcp-design' .claude/skills/KB-mcp-platform/SKILL.md`.
  2. `grep -n 'KB-mcp-platform' .claude/skills/KB-mcp-design/SKILL.md`.
  3. `grep -in 'gitnexus' .claude/skills/KB-mcp-platform/SKILL.md .claude/skills/KB-mcp-design/SKILL.md`.
- **Expected outcome:** Steps 1 + 2: each SKILL.md contains an explicit cross-reference to its sister. Step 3: both files name `gitnexus` among the covered servers.
- **Plan task refs:** T2.1, T2.2, T2.3, T5.4.

### AT-036 — Trifecta structural conventions honored

- **Maps to AC:** AC-CC-8
- **Test type:** inspection (frontmatter + directory)
- **Layer:** L1
- **Preconditions:** T2.1 + T2.2 + T2.3 complete.
- **Steps:**
  1. For both `KB-mcp-platform/SKILL.md` and `KB-mcp-design/SKILL.md`: run `yq '.name' <file>` and assert lowercase-hyphenated; run `yq '.description' <file>` and assert it ends with the sister cross-reference phrase (e.g., "see also KB-mcp-design" / vice versa).
  2. For `KB-mcp-design/references/`: assert exactly two files (`patterns-and-anti-patterns.md`, `principles.md`).
  3. For `KB-mcp-design/`: assert no `assets/` directory.
- **Expected outcome:** All checks pass per the trifecta convention.
- **Plan task refs:** T2.1, T2.2, T2.3, T5.4.

### AT-037 — `gitnexus-and-fallback.md` names GitNexus + cites ADR-0007 v2.2.0; preserves primary_degraded provision

- **Maps to AC:** AC-CC-9
- **Test type:** inspection (grep ADR citation)
- **Layer:** L1
- **Preconditions:** T2.2 + T2.3 complete.
- **Steps:**
  1. `grep -nE 'GitNexus' .claude/skills/KB-mcp-platform/references/gitnexus-and-fallback.md`.
  2. `grep -nE 'ADR-0007.*v2\.2\.0' .claude/skills/KB-mcp-platform/references/gitnexus-and-fallback.md`.
  3. `grep -nE 'codebase-memory-mcp' .claude/skills/KB-mcp-platform/references/gitnexus-and-fallback.md` — confirm fallback policy documented at project level.
  4. `grep -nE 'primary_degraded' .claude/skills/KB-mcp-design/references/principles.md` — confirm schema-level provision preserved.
- **Expected outcome:** All four greps match (≥1 hit each).
- **Plan task refs:** T2.2, T2.3.

### AT-038 — auditing-mcp family-graduation structural complete

- **Maps to AC:** AC-CC-10
- **Test type:** inspection (frontmatter + body)
- **Layer:** L1
- **Preconditions:** T4.4 + T4.5 + T4.6 complete.
- **Steps:**
  1. `yq '.family' .claude/skills/auditing-mcp/SKILL.md` → expect `auditing-mcp`.
  2. `grep -nE '^## Sub-skill family' .claude/skills/auditing-mcp/SKILL.md` → expect match.
  3. `grep -nE 'auditing-mcp' .claude/skills/auditing-cc-configs/SKILL.md` in lines 144–155 area → expect NO match in the sub-skill enumeration (the line should be absent post-graduation).
  4. `grep -nE 'auditing-mcp' .claude/skills/auditing-shared/SKILL.md` → expect match in the graduated-family consumer list.
- **Expected outcome:** Step 1: returns `auditing-mcp`. Step 2: at least one match. Step 3: line removed (no match in the sub-skill enumeration region). Step 4: match present.
- **Plan task refs:** T4.4, T4.5, T4.6, T5.4.

## Non-Functional Tests

### AT-039 — Cold-cache build + lifecycle setup ≤ ~10 min on 4 vCPU / 8 GB host

- **Maps to AC:** AC-NFR-1-a (and AC-CS-8 cold-cache portion)
- **Test type:** rebuild-measurement
- **Layer:** L3 (T5.2)
- **Preconditions:** Fresh Codespace from feature branch; host at the specified 4 vCPU / 8 GB envelope.
- **Steps:**
  1. Note the wall-clock at Codespace-create-click.
  2. Wait until both `postCreate.sh` and `postStart.sh` have completed (observable via lifecycle output + `mcp-events.jsonl` showing 5 `install_complete` records — one per OSS-local server — plus 7 `readiness_probe` records).
  3. Record total wall-clock duration.
  4. Log measurement in `verify-at-execution.md`.
- **Expected outcome:** Total cold-cache duration ≤ ~10 minutes. If measurement reads 10–12 min (near upper bound), record + flag; if > 12 min (≥ 2× target / sustained breach per Plan §Risks row), open downscoping consideration.
- **Plan task refs:** T1.4, T3.4, T5.2.

### AT-040 — Warm-cache rebuild ≤ ~2 min; no re-download / re-compile of MCP binaries

- **Maps to AC:** AC-NFR-1-b (and AC-CS-8 warm-cache portion)
- **Test type:** rebuild-measurement
- **Layer:** L3 (T5.3)
- **Preconditions:** AT-039 completed on the same Codespace; sentinels + binaries present.
- **Steps:**
  1. Trigger a Codespace rebuild (without deleting sentinels).
  2. Time the rebuild end-to-end.
  3. Observe `postCreate.sh` stdout for the per-server `[skip] sentinel+binary present` (or equivalent) lines.
  4. Confirm no `apt install`, `npm install`, `go build`, or binary download events in postCreate stdout.
- **Expected outcome:** Total warm-cache duration ≤ ~2 min. All 5 OSS-local servers report `[skip] sentinel+binary present`. No binary re-downloaded or re-compiled.
- **Plan task refs:** T3.4, T5.3.

### AT-041 — Zero literal credentials in any committed file at any commit

- **Maps to AC:** AC-NFR-2-a
- **Test type:** inspection (git-grep) + audit-run (OP-9 / OP-10)
- **Layer:** L1 + L2
- **Preconditions:** Repo at any tag / commit produced by this feature.
- **Steps:**
  1. Run `git log --all --pretty=format:%H | xargs -I {} git grep -E '<credential-shape regex>' {}` for the credential-shape patterns (subset of patterns from KB-general-coding-principles `references/secrets-rubric.md`). If too expensive, sample the last 50 commits.
  2. Run `python .claude/skills/auditing-mcp/scripts/audit_op9_url_credential_rejection.py` over the repo.
  3. Run `python .claude/skills/auditing-mcp/scripts/audit_op10_argv_leakage.py` over the repo.
- **Expected outcome:** Step 1: zero matches over the sampled history. Steps 2 + 3: both audit rules report PASS (no BLOCKER).
- **Plan task refs:** T2.4, T3.6, T4.1, T4.3 (OP-6/9/10).

### AT-042 — Redact-at-source filter applied at every `mcp-events.jsonl` write; default-fail-closed if allowlist empty

- **Maps to AC:** AC-NFR-2-d
- **Test type:** audit-run (OP-6) + inspection (script grep)
- **Layer:** L2
- **Preconditions:** T3.4 + T3.5 + T4.3 complete; `postCreate.sh` + `postStart.sh` each pipe through the redaction filter; OP-6 exists.
- **Steps:**
  1. `grep -nE 'redact|allowlist' .devcontainer/postCreate.sh .devcontainer/postStart.sh` — confirm both scripts wire the redaction filter before write.
  2. Confirm the filter implements default-fail-closed: simulate an empty allowlist (test fixture) and run the filter on input containing a credential-shape string. The output should be empty / blocked (NOT pass-through).
  3. Run OP-6 over the live `mcp-events.jsonl` post-T5.3.
- **Expected outcome:** Step 1: both scripts grep-positive for redact + allowlist references. Step 2: with empty allowlist, the filter blocks all content (default-fail-closed). Step 3: OP-6 reports PASS — no credential-shape strings present in live jsonl.
- **Plan task refs:** T3.4, T3.5, T4.3 (OP-6).

### AT-043 — Per-agent context overhead within NFR-4 tolerable envelope

- **Maps to AC:** PRD-NFR-4 / UI-7 / OI-4 (no Blueprint AC ID; methodology coverage via T4.7 + PV-4.C19+C20 + PV-5.C21 per PA-OI-3 RESOLVED-METHODOLOGY-ALIGNED)
- **Test type:** manual (measurement)
- **Layer:** L2
- **Preconditions:** `.mcp.json` exists (T2.4); 8 agent allowlists complete (T4.1).
- **Steps:**
  1. Per T4.7 methodology: for each of the 36 agents, capture baseline token count of session-startup context (the `.claude/agents/<agent>.md` + its loaded skills + ADRs).
  2. Add the `.mcp.json` content's token-contribution per-agent (one-time per session; Claude Code loads `.mcp.json` into every agent context).
  3. Per cc-design Principle 1, do NOT count per-tool schema cost (deferred until tool invocation).
  4. Record per-agent overhead in `verify-at-execution.md` §OI-4.
  5. Compare against PRD NFR-4 envelope.
- **Expected outcome:** Per-agent overhead within the PRD NFR-4 envelope. If breach detected, plan halts Phase 4 pending re-scope decision (downscoping to conditional activation per server) — this is the T4.7 escape hatch and acceptable test failure mode. Measurement methodology documented in `verify-at-execution.md` per PA-OI-3.
- **Plan task refs:** T4.7.

### AT-044 — Node 20 + Go on PATH after Feature install

- **Maps to AC:** AC-CS-1
- **Test type:** manual
- **Layer:** L2
- **Preconditions:** `devcontainer.json` Features declared (T1.4); Codespace built (T5.2).
- **Steps:**
  1. From a shell in the Codespace, run `node --version` and `go version`.
- **Expected outcome:** `node --version` returns a string matching `^v20\.` (semver minor/patch may vary). `go version` returns a non-error response (any version line containing `go version go1.`). Both commands exit 0.
- **Plan task refs:** T0.9, T1.4, T5.2.

### AT-045 — `postCreate.sh` re-invocation without sentinel deletion observes already-satisfied for each server

- **Maps to AC:** AC-CS-2
- **Test type:** rebuild-measurement (idempotence)
- **Layer:** L3 (T5.3)
- **Preconditions:** AT-039 + AT-040 completed; sentinels written to `<server>@<version>.installed`; binaries present.
- **Steps:**
  1. Without deleting any sentinel, re-run `bash .devcontainer/postCreate.sh`.
  2. Inspect stdout for per-server already-satisfied markers.
  3. Inspect `.claude/runtime/mcp-events.jsonl` — confirm no duplicate `install_complete` records for the same `<server>@<version>` are appended.
  4. Record wall-clock duration.
- **Expected outcome:** Each per-server install step short-circuits with an already-satisfied (sentinel-present AND binary-present) log line; no actual install runs. Total wall-clock well under cold-cache time (consistent with AC-NFR-1-b ≤ ~2 min). The `install_complete` records are not duplicated (or are explicitly versioned with run-id so they don't double-count).
- **Plan task refs:** T3.4, T5.3.

### AT-046 — Per-server install failure in `postCreate.sh` → name surfaced + non-zero exit

- **Maps to AC:** AC-CS-3
- **Test type:** lifecycle-script-run (negative path)
- **Layer:** L2 → L3 (T5.5)
- **Preconditions:** `postCreate.sh` exists; one per-server install step fault-injected (e.g., make `install/terraform-mcp.sh` exit 1).
- **Steps:**
  1. Override one per-server install script (e.g., `install/terraform-mcp.sh`) to `exit 1`.
  2. Run `postCreate.sh`.
  3. Capture exit code + terminal output.
- **Expected outcome:** Exit code is non-zero. stderr (or stdout) contains the failing server name (`terraform-mcp`) and a clear failure message. The lifecycle halts (subsequent install steps do NOT run silently).
- **Plan task refs:** T3.3, T3.4, T5.5.

### AT-047 — `forwardPorts: []` — no port forwarded by default

- **Maps to AC:** AC-CS-7
- **Test type:** inspection
- **Layer:** L1
- **Preconditions:** T1.4 complete.
- **Steps:**
  1. `jq '.forwardPorts' .devcontainer/devcontainer.json`.
- **Expected outcome:** Returns `[]` (empty array). No port forwarding configured.
- **Plan task refs:** T1.4.

### AT-048 — `postCreate.sh` invokes GitNexus with `GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1`; smoke-test failure halts postCreate

- **Maps to AC:** AC-CS-9
- **Test type:** lifecycle-script-run
- **Layer:** L2 → L3 (T5.2)
- **Preconditions:** T0.4 (Phase 0 GitNexus smoke-test pre-verified); T3.4 includes the GitNexus smoke-test invocation; `postCreate.sh` exists.
- **Steps:**
  1. **Happy path:** Run `postCreate.sh` against a working GitNexus install. Inspect the GitNexus smoke-test invocation: `grep -nE 'GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1' .devcontainer/postCreate.sh`. Confirm `--help` smoke-test invoked.
  2. **Failure-injected:** Force GitNexus `--help` to fail (e.g., shadow the binary with a stub that exits 1); re-run `postCreate.sh`.
- **Expected outcome:**
  - Happy path: grep matches; postCreate exits 0; GitNexus smoke-test succeeds.
  - Failure-injected: postCreate exits non-zero; stderr names the GitNexus smoke-test failure. Lifecycle halts at the smoke-test boundary.
- **Plan task refs:** T0.4, T3.4, T5.2.

## Cross-Layer Tests

### AT-049 — Canonical inventory disposition: 7 entries, no fallback

- **Maps to AC:** AC-X-2
- **Test type:** inspection + audit-run (OP-2 / OP-3 / OP-8)
- **Layer:** L1 + L2
- **Preconditions:** T2.4 + T4.3 complete.
- **Steps:**
  1. `jq -r '.mcpServers | keys[]' .mcp.json | sort > /tmp/actual-inventory.txt`.
  2. Compare against the canonical 7: `serena`, `mcp-openapi-schema`, `actionlint-mcp`, `terraform-mcp`, `gitnexus`, `context7`, `exa`.
  3. Run `python .claude/skills/auditing-mcp/scripts/audit_op2_consumer_mapping.py` — should PASS (no codebase-memory-mcp special-casing needed per Gate-4 OI-1 closure).
  4. Run `audit_op3_zero_mcp_invariant.py` and `audit_op8_gitnexus.py` similarly.
  5. Confirm OP-4 still includes the forward-looking primary/fallback prose audit rule: `grep -nE 'primary_degraded|primary/fallback' .claude/skills/auditing-mcp/scripts/audit_op4_primary_fallback_prose.py`.
- **Expected outcome:** Step 2: set-equal (exactly 7 entries; no `codebase-memory-mcp` entry). Steps 3–4: all three OPs PASS. Step 5: match present (forward-looking OP-4 rule retained).

  AC-X-1 (companion to this AC) covered separately in AT-013.
- **Plan task refs:** T2.4, T4.3 (OP-2/OP-3/OP-8).

## Hard-Gate Enforcement Test

### AT-HG — Seeded-BLOCKER simulation: auditing-mcp hard-gate halts orchestrator; remediation resumes

This is the **unified verification** for the triplet **AC-CC-5 + AC-FR-11-c + AC-NFR-2-c** per MINOR-V3-001 disposition (Blueprint v3 §Acceptance Criteria notes the triplet; PRD-inherited AC-FR-11-c is anchored by the CC-5 + NFR-2-c hard-gate semantics; one shared enforcement-verification test satisfies all three).

- **Maps to AC:** **AC-CC-5** (auditing-mcp 10 OPs zero BLOCKER; hard gate per ADR-0043) + **AC-FR-11-c** (auditing-mcp augmented; runnable end-to-end with no BLOCKER findings) + **AC-NFR-2-c** (zero BLOCKER at Gate 6; hard gate).
- **Test type:** audit-run + e2e (seeded-BLOCKER simulation, per plan T5.4)
- **Layer:** L3
- **Preconditions:**
  - T4.3 complete: `auditing-mcp/scripts/audit_mcp.py` + 10 OP rule scripts exist; `python -m py_compile`-clean.
  - T5.1 complete: Gate-6 phase-validator contract declared (this acceptance test exercises the contract end-to-end live; the phase-validator implementation is downstream `test-phase-validator-author`).
  - T5.2 + T5.3 complete: live repo state post-postCreate + warm-cache state + fresh `.claude/runtime/mcp-events.jsonl`.
  - Test fixtures directory (per PA-OI-5) exists for seeded-BLOCKER setup.

- **Steps (live verification per T5.4):**

  **Phase A — Establish clean baseline:**
  1. Run `python .claude/skills/auditing-mcp/scripts/audit_mcp.py --with-runtime --severity-threshold BLOCKER`.
  2. Capture exit code + the report.
  3. Inspect: all 10 OP rules (OP-1 env-block coverage, OP-2 consumer-mapping, OP-3 zero-mcp__ preservation, OP-4 primary/fallback prose, OP-5 lifecycle completeness, OP-6 runtime log redaction, OP-7 trifecta consistency, OP-8 GitNexus-specific, OP-9 URL-credential rejection, OP-10 argv-leakage absence) report results. OP-6 specifically confirms no credential-shape strings in live `mcp-events.jsonl`. OP-7 confirms trifecta consistency. AC-CC-10 family-graduation structural test passes inside the audit-run.

  **Phase B — Seed a BLOCKER:**
  4. Deliberately introduce a fake BLOCKER finding into a scratch test fixture path within `auditing-mcp`'s monitored scope. Concrete choice: write a synthetic literal credential (e.g., `ghp_FAKE_TEST_CREDENTIAL_FOR_SEEDED_BLOCKER_001`) into a known-monitored test-fixture file path established per PA-OI-5.
  5. Re-run `python .claude/skills/auditing-mcp/scripts/audit_mcp.py --with-runtime --severity-threshold BLOCKER`.
  6. Capture exit code + report.

  **Phase C — Confirm hard-gate halts:**
  7. Confirm the seeded BLOCKER is reported by OP-6 (or equivalent rule) with severity `BLOCKER`. Exit code is non-zero.
  8. Confirm: by ADR-0043 contract, the orchestrator's Gate-6 phase-validator (downstream `test-phase-validator-author` artifact) would halt at this exit code. If the phase-validator wiring is not yet in place at the time of this test, the `audit_mcp.py` exit code is the source of truth (per plan T5.4).
  9. Confirm: there is NO operator-bypass option exercised (per ADR-0043 Decision).

  **Phase D — Remediate + re-run + resume:**
  10. Remove the seeded BLOCKER (revert the synthetic credential).
  11. Re-run `audit_mcp.py --with-runtime --severity-threshold BLOCKER`.
  12. Confirm exit code 0; orchestrator would resume past Gate 6.

- **Expected outcome:**

  | Phase | Exit code | Hard-gate behavior |
  |---|---|---|
  | A (clean baseline) | 0 | Gate 6 passes; orchestrator proceeds; AC-CC-5 + AC-FR-11-c + AC-NFR-2-c initial-state satisfied |
  | B+C (seeded BLOCKER) | non-zero | Gate 6 halts (per ADR-0043 contract); no operator bypass; rule fires on the seeded credential |
  | D (remediated + re-run) | 0 | Gate 6 resumes; orchestrator proceeds; full hard-gate cycle exhibited end-to-end |

  AC-CC-5: zero BLOCKER findings (Phase A) ✓; hard-gate semantics confirmed (Phase B+C → D) ✓.
  AC-FR-11-c: runnable end-to-end + zero BLOCKER (Phase A) ✓; GitNexus-rule coverage exercised via OP-8 inside `audit_mcp.py --with-runtime` ✓.
  AC-NFR-2-c: hard-gate at Gate 6 (Phase B+C demonstrates halt; Phase D demonstrates resume) ✓.

  All three ACs in the triplet satisfied by this one shared test, per MINOR-V3-001 disposition.

- **Plan task refs:** T4.3 (audit_mcp.py + 10 OPs), T5.1 (contract declaration), T5.4 (live seeded-BLOCKER simulation).

## Test Fixtures and Infrastructure

Per PA-OI-5 (T4.3 auditing-mcp test-fixtures), the audit-rule scripts (OP-1..OP-10) require test-fixtures to exercise positive + negative paths in synthetic-fixture form before live-state invocation. The fixtures live under `.claude/skills/auditing-mcp/test-fixtures/` (or equivalent path established at T4.3 authoring time):

- **OP-6 fixtures:** credential-shape strings embedded in synthetic `mcp-events.jsonl` segments for redaction-integrity exercise.
- **OP-2 / OP-3 fixtures:** synthetic agent files with prescribed / non-prescribed `mcp__` entry shapes.
- **OP-9 fixtures:** synthetic URLs with embedded credentials.
- **OP-10 fixtures:** synthetic argv-with-credential strings.

The seeded-BLOCKER simulation in AT-HG re-uses the OP-6 fixture pattern (synthetic credential shaped as `ghp_FAKE_TEST_CREDENTIAL_*` to make it grep-visible as a test fixture, distinct from a real ghp_ key).

## Determinism + Repeatability Notes

- **AT-039, AT-040, AT-045 (rebuild-measurement):** measurements are wall-clock-dependent; record observed value + flag if near upper bound rather than treating soft target as a binary pass/fail. Hard breach (≥2× target) is plan-defined escalation.
- **AT-001, AT-006, AT-024–AT-026 (live e2e):** depend on Codespace network reachability for Context7 + Exa + Terraform MCP server registries; if external services are flaky, retry up to 3× before recording as failure.
- **AT-013, AT-022 (failure-mode):** require strict fixture restoration after each rehearsal to avoid contaminating downstream tests.
- **AT-HG (seeded-BLOCKER):** must remove the seeded credential before any commit; the test fixture is scratch-only and never committed.

## Document History

| Version | Date | Author | Notes |
|---|---|---|---|
| 1.0.0 | 2026-05-23 | test-acceptance-author | Initial draft. 51 of 51 Blueprint v3 ACs covered by 49 unique tests + 1 shared triplet test (AT-HG) per MINOR-V3-001 disposition. Hard-gate verification anchored at plan T5.4 seeded-BLOCKER simulation. Cross-references plan-v1 §Acceptance Test Cross-Reference (lines 1083–1167). Incorporates 5 PA-OI items from plan-v1: PA-OI-3 (T4.7 NFR-4 methodology in AT-043), PA-OI-2 (5-min postAttach staleness in AT-018), PA-OI-5 (test-fixtures setup in §Test Fixtures and Infrastructure + AT-HG). |
| 1.0.1 | 2026-05-23 | test-acceptance-author (cycle-1 amendment) | Focused amendment per reconciliation-dispatch-cycle-1.json. Resolves I-CA-001 (AT-016 install_complete 7→5; HTTP servers context7+exa have no install step), I-CA-002 (OP-script rename to canonical `audit_op<N>_<descriptor>.py` across AT-032/AT-041/AT-049), I-CA-003 (AT-043 AC-NFR-4 phantom remap to PRD-NFR-4 / UI-7 / OI-4 per PA-OI-3 resolution chain), I-CA-004 (test-count phrasing clarified to "50 unique test IDs"). No upstream artifact churn. |
| 1.0.2 | 2026-05-23 | orchestrator (direct mechanical-edit patch) | Patch-level reconciliation closing **PKG-MAJOR-003** surfaced by finalize-deliverable-packager cycle 2: AT-005 line 155 `design-cc.md` → `design-claude-code.md` with Path-A explanatory note (the agent's frontmatter `name:` is `design-cc`; the on-disk filename is `design-claude-code.md`). Sibling to the cycle-2 architecture-audit patch (I-AA-001) — that round's dispatch_targets list omitted acceptance-tests.md, leaving this one site un-propagated. See reconciliation-log-cycle-2.md (updated). |
| 1.0.3 | 2026-05-23 | test-acceptance-author (cycle-3 dispatch D-3.3) | Focused in-place amendment per `reconciliation-dispatch-cycle-3.json` D-3.3 and `reconciliation-log-cycle-3.md`. Three sweeps applied: **F1 (actionlint-mcp upstream identifier `2manymws` → `hongkongkiwi/actionlint-mcp`)** — NO-OP: this artifact references `actionlint-mcp` only at the MCP-server-name (`.mcp.json` key) level, never at the upstream package identifier; no `2manymws` or `/cmd/actionlint-mcp` occurrences found. **F2 (GitNexus install-method `uvx` → npm/npx)** — NO-OP: this artifact references `gitnexus` only at the server-name + `GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1` env-flag level (AT-048), never at the install-recipe level; no `uvx --from gitnexus` occurrences found. **F3 (Context7 v3.0.0 tool surface: 2 tools `resolve-library-id` + `get-library-docs`; `ReplaceContentTool` does not exist; v3.0.0 published 2026-05-22T16:20Z)** — NO-OP: this artifact references `context7` only at the server-name + `CONTEXT7_API_KEY` env-var + auth-layer-failure-mode level (AT-001, AT-004, AT-011, AT-012, AT-013, AT-015, AT-049); no Context7 tool-name assertions, no tool-count assertions, no Context7 version pins, no occurrences of `ReplaceContentTool` / `ReplaceRegexTool` / `Context7 v1.2.0`. Canonical Context7 fact source: `research-notes/T-005-context7.md` v2.0.0 (refreshed by D-3.2). **Tests amended: 0** (all three sweeps NO-OP — the acceptance-test predicates were authored at exactly the abstraction layer the cycle-3 dispatch contract anticipated, so the v3.0.0 verified facts produced no AT-text divergence). **Frontmatter corrigendum:** version field reflected `1.0.1` in v1.0.2's amendment (the cycle-2 mechanical-edit patch updated the body's history table but did not propagate to frontmatter); this v1.0.3 amendment advances frontmatter directly to `1.0.3` to re-align frontmatter with body. **Out of scope (preserved):** auth-header form `Authorization: Bearer ${CONTEXT7_API_KEY}` vs `CONTEXT7_API_KEY: <value>` divergence — flagged as SF-F3-AUTH-HEADER-1 in cycle-3 for cycle-4 reconciliation; this dispatch does not resolve. SF-F3-AUTH-HEADER-1 did NOT surface in this sweep (no `Authorization: Bearer` literal appears in this artifact; AT-013 cites the `failure_layer: "auth"` semantic only). |
