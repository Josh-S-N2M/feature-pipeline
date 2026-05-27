# Per-Mechanism Isolation Smoke Report

**Task:** T4.3  
**AC:** AC-X-1  
**Executed at:** 2026-05-27  
**Executed by:** execute-task-code-producer (ai-development-guide mode)

This report documents one sub-smoke per mechanism. Each sub-smoke exercises exactly one mechanism against a constructed scenario where the other four are not in play, and confirms both the named-failure path and its negation.

---

## Sub-smoke (a): FR-1 alone — verdict-findings parity

**Mechanism:** `verdict_findings_parity.py`  
**Script:** `.claude/skills/auditing-shared/scripts/verdict_findings_parity.py`  
**Method:** `--selftest` flag runs 11 fixture cases spanning all named-failure and negation paths. The other four mechanisms (FR-2 dispatch self-check, FR-3 ADR-parity audit, FR-4 install pre-flight / calibration, FR-5 connectivity smoke) are not invoked during this test.

**Execution:**
```
python3 .claude/skills/auditing-shared/scripts/verdict_findings_parity.py --selftest
```

**Named-failure scenarios (expected exit 1):**
- `fail_blocker.json` + agent `shared-document-reviewer`: approving verdict `pass` alongside BLOCKER finding. Observed exit 1. Stderr diagnostic includes `offending_artifact`, `rule_violated`, and `remedial_hint`. Matches expected.
- `fail_critical.json` + agent `shared-document-reviewer`: approving verdict `approved` alongside finding with severity `critical`. Observed exit 1. Diagnostic emitted. Matches expected.
- `agent_execute_task_quality_handler_fail.json` + agent `execute-task-quality-handler`: approving verdict `APPROVED` alongside BLOCKER finding. Observed exit 1. Matches expected.

**Negation scenarios (expected exit 0):**
- `pass_clean.json`: approving verdict, no findings at all. Exit 0. Silent.
- `pass_with_minor.json`: approving verdict, only MINOR finding (non-blocking severity). Exit 0. Silent.
- `non_approving_with_blocker.json`: non-approving verdict with BLOCKER present — parity is fine because verdict is already non-approving. Exit 0. Silent.
- `agent_execute_phase_quality_reviewer_pass.json`: approving verdict `PASS` (correct case), no blocking findings. Exit 0.
- `agent_execute_phase_quality_reviewer_case_wrong.json`: lowercase `pass` is non-approving for `execute-phase-quality-reviewer` (case-sensitive lookup), so BLOCKER present doesn't trigger a reject. Exit 0.
- `agent_execute_task_quality_handler_pass.json`: approving verdict `APPROVED`, no blocking findings. Exit 0.
- `agent_review_cross_artifact_auditor_conditional_pass.json`: approving verdict `conditional_pass` for `review-cross-artifact-auditor`, no blocking findings. Exit 0.

**Malformed input scenario (expected exit 2):**
- `malformed.json`: invalid JSON. Exit 2. Stderr reports parse error.

**Result:** 11/11 cases passed. Sub-smoke PASS.

---

## Sub-smoke (b): FR-2 alone — dispatch self-check

**Mechanism:** FR-2 dispatch self-check (absence-default rule, ADR-0057)  
**Harness:** `smoke/t4-6/fr2_self_check.py`  
**Fixtures:** `fixtures/pre-feature-checkpoint-with-workaround.json` (named-failure) and `fixtures/pre-feature-checkpoint.json` (negation)  
**Method:** The harness is run directly against each fixture. The other four mechanisms are not involved.

**Named-failure scenario:**

Fixture: `pre-feature-checkpoint-with-workaround.json`  
Shape: `scope_class=FULL`, stage `prd_authoring` carries `execution_mode: parent-driven-workaround`.

```
python3 smoke/t4-6/fr2_self_check.py fixtures/pre-feature-checkpoint-with-workaround.json
```

Observed output:
```
scope_class: FULL
verdict: REFUSE

stage resolution (absence-default applied):
  intent_clarification: specialist-dispatch [absent→default]
  prd_authoring: parent-driven-workaround
  research_planning: specialist-dispatch [absent→default]
  ...

diagnostic:
  mechanism: FR-2 dispatch self-check
  offending_artifact: prd_authoring
  rule_violated: FULL-scope features prohibit parent-driven-workaround execution mode per PRD §FR-2 and ADR-0057
  remedial_hint: either change scope_class to MINOR/PATCH OR reconfigure the stage to specialist-dispatch
```

Exit code: 1. Matches expected.

**Negation scenario:**

Fixture: `pre-feature-checkpoint.json`  
Shape: `scope_class=FULL`, no stage carries an `execution_mode` field (pre-ADR-0057 checkpoint). Per the absence-default rule, each absent field maps to `specialist-dispatch`.

```
python3 smoke/t4-6/fr2_self_check.py fixtures/pre-feature-checkpoint.json
```

Observed output:
```
scope_class: FULL
verdict: PASS

stage resolution (absence-default applied):
  intent_clarification: specialist-dispatch [absent→default]
  prd_authoring: specialist-dispatch [absent→default]
  ...

diagnostic: none
```

Exit code: 0. Matches expected.

**Result:** Both paths match expected. Sub-smoke PASS.

---

## Sub-smoke (c): FR-3 alone — ADR-0041 parity audit

**Mechanism:** OP-11 `.mcp.json` ↔ ADR-0041 invocation-form parity  
**Script:** `.claude/skills/auditing-mcp/scripts/audit_op11_adr_parity.py`  
**Method:** `--selftest` flag runs 6 fixture cases covering all three named-failure scenarios and three negation scenarios. The other four mechanisms are not invoked.

**Execution:**
```
python3 .claude/skills/auditing-mcp/scripts/audit_op11_adr_parity.py --selftest
```

**Named-failure scenarios (expected exit 1):**
- `missing_in_adr.json` + `missing_in_adr_table.md`: server present in `.mcp.json` with no row in ADR-0041. Script exits 1 with BLOCKER finding. Matches expected.
- `absent_from_mcp.json` + `absent_from_mcp_table.md`: server has an active ADR row but is absent from `.mcp.json`. Script exits 1 with BLOCKER finding. Matches expected.
- `form_mismatch.json` + `form_mismatch_table.md`: server present in both but invocation form in `.mcp.json` does not match any backtick-quoted block in the ADR row. Script exits 1 with BLOCKER finding. Matches expected.

**Negation scenarios (expected exit 0):**
- `clean_mcp_json.json` + `clean_adr_table.md` (clean pair): every `.mcp.json` server has a matching active ADR row with consistent form. Exit 0. Matches expected.
- `deprecated_row_skip.json` + `deprecated_row_skip_table.md`: server's only ADR row carries the `[DEPRECATED INVOCATION FORM]` annotation — form-parity comparison is skipped, no BLOCKER raised. Exit 0. Matches expected.
- `live_mcp.json` + `live_adr_table.md` (live-repo state fixture): models the actual current project state after this feature ships. Exit 0. Matches expected.

**Result:** 6/6 cases passed. Sub-smoke PASS.

---

## Sub-smoke (d): FR-4 family alone

FR-4 covers three distinct sub-mechanisms. Each is exercised independently below.

### (d1) FR-4a alone — static-shape check

**Mechanism:** `_fr4a_check()` in `.devcontainer/postCreate.sh` (lines 200–270)  
**Method:** The four assertions (A1–A4) were extracted and run in an isolated bash subshell against two environment configurations. No network requests. No npm install. No FR-1/FR-2/FR-3/FR-5 involvement.

**Named-failure scenario:**

Environment: `GITNEXUS_SKIP_OPTIONAL_GRAMMARS` unset, `GITNEXUS_TAG` set to the value in `versions.env`.

Observed:
- Assertion A1 fires immediately: `GITNEXUS_SKIP_OPTIONAL_GRAMMARS=<unset> (expected 1)`.
- Stderr output: `structured_failure` event with `mechanism: FR-4a GitNexus install pre-flight check`, `assertion: A1`.
- Return code: 1.

Matches expected: harness exits 1, structured_failure emitted to stderr with FR-6 diagnostic shape.

**Negation scenario:**

Environment: `GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1`, `GITNEXUS_TAG` matches the pin in `versions.env`, npm global root present and writable.

Observed:
- All four assertions (A1–A4) pass.
- No stderr output.
- Return code: 0.

Matches expected: harness exits 0, silent.

**Result:** Both paths match expected. Sub-smoke PASS.

### (d2) FR-4b alone — calibration script

**Mechanism:** `.devcontainer/scripts/calibrate-gitnexus-grammar-skip.sh`  
**Method:** This sub-smoke is covered by the T2.5 live run rather than re-executed here, for the reasons explained below.

**Named-failure scenario (live evidence from T2.5):**

T2.5 ran the calibration script against real upstream npm output for `gitnexus@1.6.5`. The script exited 2 (`drift_detected`). The outcome was emitted as one `calibration_result` event at line 21 of `.claude/runtime/mcp-events.jsonl` with all 9 ADR-0058 required fields present and `outcome: drift_detected`. This is the documented failure path: real upstream stderr divergence causes the script to exit 2 and emit a single well-formed event.

Evidence: `working/feature/pipeline-quickwins-hardening-r1/integration-smoke-fr4-end-to-end.md` § Calibration Invocation and § New Event Payload.

**Negation scenario:**

The negation (script exits 0, outcome `pass`) requires a live npm install whose stderr matches the expected grammar-skip regex patterns. That cannot be synthesized in agent context without mocking the upstream stderr. The negation path is therefore documented rather than live-executed. It would be triggered when the upstream `gitnexus` package's install stderr matches the expected patterns for both the skip run (artifacts absent) and the default run (artifacts present).

Deferred to: post-merge observation (T5.2 cron run) — if upstream restores the expected stderr format, the script will exit 0 on the next scheduled calibration run.

**Result:** Named-failure path empirically confirmed by T2.5. Negation path documented with deferred-to-T5.2 cross-reference.

### (d3) FR-4c alone — calibration workflow

**Mechanism:** `.github/workflows/gitnexus-grammar-skip-calibration.yml`  
**Method:** This workflow requires a GitHub Actions runner and cannot be executed in agent context. The sub-smoke relies on static structural verification (T3.3) and the T2.5 empirical evidence.

**Named-failure scenario:**

The workflow invokes `calibrate-gitnexus-grammar-skip.sh` and propagates its exit code per AC-CICD-4c-9. Because the current script exits 2 (`drift_detected`) against `gitnexus@1.6.5` (per T2.5), any workflow run against the current `versions.env` + script will produce a workflow-level failure. T3.3 confirmed the workflow correctly maps the script's exit code to a workflow failure step.

**Negation scenario:**

A passing run requires the script to exit 0, which requires the upstream stderr format to match the calibration regex. This is documented as covered by T5.2 post-merge cron observation: when the upstream contract is restored, the scheduled workflow will pass.

**Result:** Named-failure path supported by T2.5 evidence + T3.3 structural verification. Negation path deferred to T5.2.

---

## Sub-smoke (e): FR-5 alone — connectivity smoke workflow

**Mechanism:** `.github/workflows/mcp-connectivity-smoke.yml`  
**Method:** This workflow runs `claude --bare -p "noop" --output-format stream-json | jq` against `.mcp.json` in a CI runner. It cannot be executed in agent context. The sub-smoke relies on static structural verification from T3.1/T3.2 and the deferred post-merge observation from T5.2/T5.3.

**Named-failure scenario:**

If any server in `.mcp.json` reports `status != "connected"`, the workflow will emit a FR-6 diagnostic and fail. T3.1 confirmed the workflow's jq filter correctly detects non-connected server statuses and routes to a failure step with the appropriate diagnostic.

**Negation scenario:**

All six servers connected → workflow passes silently. This is the expected state post-merge in the provisioned devcontainer environment.

Deferred to: T5.2/T5.3 post-merge workflow observation.

**Result:** Both paths documented. Named-failure path supported by T3.1 structural verification. Negation path deferred to T5.2/T5.3.

---

## Summary

| Sub-smoke | Mechanism | Named-failure path | Negation path | Live-executed? |
|---|---|---|---|---|
| (a) FR-1 | verdict_findings_parity.py | Exit 1 + FR-6 diagnostic on stderr | Exit 0, silent | Yes — 11/11 selftest cases |
| (b) FR-2 | fr2_self_check.py | Exit 1 + REFUSE verdict + diagnostic | Exit 0, PASS verdict | Yes — both fixture paths |
| (c) FR-3 | audit_op11_adr_parity.py | Exit 1 + BLOCKER finding | Exit 0, no findings | Yes — 6/6 selftest cases |
| (d1) FR-4a | postCreate.sh _fr4a_check | Exit 1 + structured_failure on stderr | Exit 0, silent | Yes — both inline scenarios |
| (d2) FR-4b | calibrate-gitnexus-grammar-skip.sh | Exit 2 drift_detected (T2.5 evidence) | Deferred to T5.2 | Named-failure: T2.5 live run |
| (d3) FR-4c | gitnexus-grammar-skip-calibration.yml | Workflow fails (T3.3 + T2.5 evidence) | Deferred to T5.2 | Static verification only |
| (e) FR-5 | mcp-connectivity-smoke.yml | Workflow fails (T3.1 structural) | Deferred to T5.2/T5.3 | Static verification only |

Five of eight cases are live-executed (FR-1, FR-2, FR-3, FR-4a, plus FR-4b's named-failure evidence from T2.5). Three cases (FR-4b negation, FR-4c both, FR-5 both) are covered by static structural verification plus documented deferred-to-T5.2 cross-references, as specified in AC-X-1's documentation discipline for mechanisms that require live CI.

All L1/L2/L3 verification criteria are satisfied:
- L1: smoke directory and report exist at `working/feature/pipeline-quickwins-hardening-r1/smoke/per-mechanism/smoke-report.md`.
- L2: each sub-smoke either runs live or documents the deferred-to-T5.2 cross-reference.
- L3: report is traceable to AC-X-1 — each sub-smoke names the mechanism, the scenario, the observed outcome, and the expected outcome.
