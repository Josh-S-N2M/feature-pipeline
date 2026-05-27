# End-to-End Orchestrator Smoke Report

**Task:** T4.4
**AC:** AC-X-1, AC-NFR-5-a, AC-NFR-9-a
**AT coverage:** AT-007, AT-008, AT-013, AT-024, AT-063
**Executed at:** 2026-05-27
**Executed by:** execute-task-code-producer (ai-development-guide mode)
**Status:** PASS

---

## 1. Known-Good Pipeline Fixture Set

This section defines the "known-good" input for each mechanism and documents that all five report clean on that input.

### Fixture set description

| Mechanism | Fixture / Input | Why it is known-good |
|---|---|---|
| FR-1 (verdict_findings_parity.py) | `fixtures/fr1/pass_clean.json` with agent `shared-document-reviewer` | Approving verdict `pass`, empty findings array — structurally consistent |
| FR-2 (dispatch self-check) | `fixtures/pre-feature-checkpoint.json` | FULL scope, all stages absent the execution_mode field → all resolve to specialist-dispatch via absence-default; zero offenders |
| FR-3 (audit_op11_adr_parity.py) | `fixtures/fr3/clean_mcp_json.json` + `fixtures/fr3/clean_adr_table.md` | Every .mcp.json server has a matching active ADR row with consistent invocation form |
| FR-4a (postCreate.sh static-shape check) | GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1, GITNEXUS_TAG matches versions.env, npm root present | All four assertions A1–A4 pass |
| FR-4b / FR-4c | T2.5 live run evidence + T3.2 structural verification | See documented-deferral section 5 |
| FR-5 | T3.1 structural verification | See documented-deferral section 5 |

### Per-mechanism known-good run results

#### FR-1

```
Command: python3 .claude/skills/auditing-shared/scripts/verdict_findings_parity.py \
           working/feature/pipeline-quickwins-hardening-r1/fixtures/fr1/pass_clean.json \
           shared-document-reviewer
Exit code: 0
Stdout: (empty)
Stderr: (empty)
```

Result: PASS — no parity error on a clean approving input.

#### FR-2

```
Command: python3 working/feature/pipeline-quickwins-hardening-r1/smoke/t4-6/fr2_self_check.py \
           working/feature/pipeline-quickwins-hardening-r1/fixtures/pre-feature-checkpoint.json

Output:
  fixture: .../pre-feature-checkpoint.json
  scope_class: FULL
  verdict: PASS

  stage resolution (absence-default applied):
    intent_clarification: specialist-dispatch [absent→default]
    prd_authoring: specialist-dispatch [absent→default]
    research_planning: specialist-dispatch [absent→default]
    per_layer_design: specialist-dispatch [absent→default]
    design_composition: specialist-dispatch [absent→default]
    plan_authoring: specialist-dispatch [absent→default]
    execution: specialist-dispatch [absent→default]

  diagnostic: none

Exit code: 0
```

Result: PASS — absence-default applies across all 7 stages; FULL scope with all specialist-dispatch passes the FR-2 gate.

#### FR-3

```
Command: python3 .claude/skills/auditing-mcp/scripts/audit_op11_adr_parity.py \
           working/feature/pipeline-quickwins-hardening-r1/fixtures/fr3/clean_mcp_json.json \
           working/feature/pipeline-quickwins-hardening-r1/fixtures/fr3/clean_adr_table.md

Output:
  {
    "rule": "OP-11",
    "name": ".mcp.json ↔ ADR-0041 invocation-form parity",
    "mcp_json": ".../clean_mcp_json.json",
    "adr_0041": ".../clean_adr_table.md",
    "findings": []
  }

Exit code: 0
Stderr: (empty)
```

Result: PASS — no BLOCKER findings on the clean fixture pair.

#### FR-4a

Per T4.3 sub-smoke (d1), confirmed live via isolated bash evaluation of the `_fr4a_check()` function from postCreate.sh against an environment where GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1, GITNEXUS_TAG matches the versions.env pin, and npm global root is present and writable. All four assertions A1–A4 passed. Exit 0, silent. That evidence is not re-executed here; the T4.3 smoke-report.md is the record.

#### FR-4b and FR-4c

Deferred — see section 5.

#### FR-5

Deferred — see section 5.

---

## 2. Deliberate-Breakage Isolation Test

One breakage is introduced in FR-1's input (`fail_blocker.json` — an approving verdict `pass` alongside a BLOCKER-severity finding). FR-3 and FR-2 each receive their known-good inputs simultaneously. The expected outcome: only FR-1 reports failure; FR-3 and FR-2 remain clean.

### FR-1 with bad input (expected: exit 1)

```
Command: python3 .claude/skills/auditing-shared/scripts/verdict_findings_parity.py \
           working/feature/pipeline-quickwins-hardening-r1/fixtures/fr1/fail_blocker.json \
           shared-document-reviewer

Stderr:
  {
    "mechanism": "FR-1 verdict-vs-findings parity check",
    "offending_artifact": "...fail_blocker.json",
    "rule_violated": "agent shared-document-reviewer declared approving verdict 'pass' alongside finding with severity 'BLOCKER'",
    "remedial_hint": "reviewer shared-document-reviewer must either downgrade verdict to non-approving OR escalate/remove the blocking finding before re-submission"
  }

Exit code: 1
```

Observed: exit 1. FR-6 diagnostic emitted. Matches expected.

### FR-3 with clean input during FR-1 breakage (expected: exit 0, no contamination)

```
Command: python3 .claude/skills/auditing-mcp/scripts/audit_op11_adr_parity.py \
           working/feature/pipeline-quickwins-hardening-r1/fixtures/fr3/clean_mcp_json.json \
           working/feature/pipeline-quickwins-hardening-r1/fixtures/fr3/clean_adr_table.md

Output:
  {
    "rule": "OP-11",
    "name": ".mcp.json ↔ ADR-0041 invocation-form parity",
    "mcp_json": ".../clean_mcp_json.json",
    "adr_0041": ".../clean_adr_table.md",
    "findings": []
  }

Exit code: 0
Stderr: (empty)
```

Observed: exit 0. No contamination from the FR-1 bad input. Matches expected.

### FR-2 with clean input during FR-1 breakage (expected: exit 0, no contamination)

```
Command: python3 working/feature/pipeline-quickwins-hardening-r1/smoke/t4-6/fr2_self_check.py \
           working/feature/pipeline-quickwins-hardening-r1/fixtures/pre-feature-checkpoint.json

Output:
  fixture: .../pre-feature-checkpoint.json
  scope_class: FULL
  verdict: PASS
  ...
  diagnostic: none

Exit code: 0
```

Observed: exit 0. No contamination from the FR-1 bad input. Matches expected.

### Isolation result

Only FR-1 (the mechanism whose input was deliberately broken) reports failure. FR-3 and FR-2, each given their known-good inputs, both remain clean. No inter-mechanism contamination. Isolation confirmed.

---

## 3. Determinism Evidence (AC-NFR-5-a)

FR-1 and FR-3 were each run twice in succession (no source changes between runs). The full stdout and stderr of run 1 and run 2 were captured for each mechanism via `--selftest`.

### FR-1 (verdict_findings_parity.py --selftest) — two runs

Run 1 stdout (via selftest harness, relevant lines):

```
  PASS  pass_clean.json (shared-document-reviewer) -> exit 0
  PASS  pass_with_minor.json (shared-document-reviewer) -> exit 0
  PASS  fail_blocker.json (shared-document-reviewer) -> exit 1
  PASS  fail_critical.json (shared-document-reviewer) -> exit 1
  PASS  non_approving_with_blocker.json (shared-document-reviewer) -> exit 0
  PASS  malformed.json (shared-document-reviewer) -> exit 2
  PASS  agent_execute_phase_quality_reviewer_pass.json (execute-phase-quality-reviewer) -> exit 0
  PASS  agent_execute_phase_quality_reviewer_case_wrong.json (execute-phase-quality-reviewer) -> exit 0
  PASS  agent_execute_task_quality_handler_pass.json (execute-task-quality-handler) -> exit 0
  PASS  agent_execute_task_quality_handler_fail.json (execute-task-quality-handler) -> exit 1
  PASS  agent_review_cross_artifact_auditor_conditional_pass.json (review-cross-artifact-auditor) -> exit 0

11/11 cases passed
```

Run 2: byte-identical to run 1. Both runs produced the same 11 PASS/FAIL lines, the same error JSON on stderr for the three failure-path cases, and the same final `11/11 cases passed` summary. No timestamps, PIDs, or other non-deterministic fields in the output.

Diff between run 1 and run 2: empty (zero bytes differ).

### FR-3 (audit_op11_adr_parity.py --selftest) — two runs

Run 1 stdout:

```
[selftest] PASS  clean pair (exit 0)
[selftest] PASS  missing in ADR (exit 1)
[selftest] PASS  absent from mcp (exit 1)
[selftest] PASS  form mismatch (exit 1)
[selftest] PASS  deprecated row skip (exit 0)
[selftest] PASS  live repo state (exit 0)

[selftest] 6/6 passed
```

Run 2: byte-identical to run 1. Same six PASS lines, same `6/6 passed` summary.

Diff between run 1 and run 2: empty (zero bytes differ).

Determinism confirmed for both FR-1 and FR-3 (the two mechanisms that have explicit selftest harnesses with captured stdout). Neither script emits timestamps, process IDs, or other non-deterministic fields in its output stream.

---

## 4. NFR-9 Backward Compatibility Evidence (AC-NFR-9-a)

The question NFR-9 asks: does a reviewer-output fixture that the prior pipeline would have accepted still pass FR-1 after FR-1 was wired in?

Two fixtures represent inputs that any prior pipeline would have accepted — they carry an approving verdict with no blocking findings, which is the canonical "clean reviewer output" shape:

**Fixture 1:** `fixtures/fr1/pass_clean.json`

```json
{
  "verdict": "pass",
  "findings": []
}
```

```
Command: python3 .../verdict_findings_parity.py fixtures/fr1/pass_clean.json shared-document-reviewer
Exit code: 0
Stderr: (empty)
```

Result: PASS. The simplest possible clean reviewer output still passes.

**Fixture 2:** `fixtures/fr1/pass_with_minor.json`

This fixture has an approving verdict alongside a MINOR-severity finding. Any prior pipeline that forwarded reviewer output without a parity check would have passed this through (MINOR is not blocking). FR-1 also passes it through because MINOR is not in the blocking-severity set {BLOCKER, CRITICAL}.

```
Command: python3 .../verdict_findings_parity.py fixtures/fr1/pass_with_minor.json shared-document-reviewer
Exit code: 0
Stderr: (empty)
```

Result: PASS. Non-blocking findings do not cause FR-1 to reject.

FR-1 introduces no regressions on already-clean inputs. The stricter check applies only to the previously-undetected parity contradiction (approving verdict alongside BLOCKER or CRITICAL finding), which is a new structural safeguard, not a tighter bar on inputs that were already clean.

---

## 5. Documented Deferrals

Three categories of live execution that cannot be performed in agent context are formally deferred here with explicit cross-references.

### FR-4b live calibration in a fresh devcontainer

The calibration script (`calibrate-gitnexus-grammar-skip.sh`) requires npm, a live npm install, and two scratch directories. It cannot be re-executed in agent context without a real devcontainer build.

The T2.5 empirical record covers this: the script was invoked live against `gitnexus@1.6.5`, exited 2 (`drift_detected`), and emitted exactly one conforming `calibration_result` event to `.claude/runtime/mcp-events.jsonl`. The `drift_detected` outcome reflects the current upstream stderr format change, not a defect in the integration mechanics.

The current `drift_detected` signal is documented in `Issues/fr4b-signal1-regex-drift/analysis.md` (Issue H-4 adopted by this feature per the deferral-register, row H-4).

Cross-references: T2.5 live run evidence, T5.2 post-merge cron observation (steady-state observability).

### FR-4c workflow execution

The `gitnexus-grammar-skip-calibration.yml` workflow requires a GitHub Actions runner. It cannot be executed in agent context.

Structural verification was completed in T3.2 (workflow file authored) and T3.3 (actionlint lint gate). The workflow correctly maps the calibration script's exit code to a workflow-level outcome per AC-CICD-4c-9 and does not re-implement Signal 1/3 logic per AC-CICD-4c-10.

Cross-references: T3.2 structural verification, T3.3 actionlint gate, T5.2 post-merge workflow observation.

### FR-5 workflow execution

The `mcp-connectivity-smoke.yml` workflow runs `claude --bare` in a CI runner and cannot be executed in agent context.

Structural verification was completed in T3.1 (workflow file authored) and T3.3 (actionlint gate). The jq filter and failure-routing logic were verified structurally against the expected FR-6 diagnostic shape.

Cross-references: T3.1 structural verification, T3.3 actionlint gate, T5.2 post-merge workflow observation, T5.3 Monday cron tick observation.

---

## 6. Summary

| Verification | Source | Result |
|---|---|---|
| FR-1 known-good passes | Live run | PASS — exit 0, silent |
| FR-2 known-good passes | Live run | PASS — exit 0, PASS verdict |
| FR-3 known-good passes | Live run | PASS — exit 0, empty findings |
| FR-4a known-good passes | T4.3 sub-smoke (d1) | PASS — all four assertions |
| FR-4b known-good passes | T2.5 live run (deferred) | Deferred to T5.2 |
| FR-4c known-good passes | T3.2 structural (deferred) | Deferred to T5.2 |
| FR-5 known-good passes | T3.1 structural (deferred) | Deferred to T5.2/T5.3 |
| Isolation: only FR-1 fails when FR-1 input is broken | Live run | PASS — FR-3 exit 0, FR-2 exit 0 |
| FR-1 determinism (run 1 vs run 2, byte diff) | Two live runs | PASS — zero diff |
| FR-3 determinism (run 1 vs run 2, byte diff) | Two live runs | PASS — zero diff |
| NFR-9: pass_clean.json still passes after FR-1 wired in | Live run | PASS — exit 0 |
| NFR-9: pass_with_minor.json still passes after FR-1 wired in | Live run | PASS — exit 0 |

L1/L2/L3 verification status:
- L1: smoke directory and report exist at `working/feature/pipeline-quickwins-hardening-r1/smoke/end-to-end/smoke-report.md`. Report is well-formed.
- L2: three of five mechanisms exercised live with both known-good and isolation-breakage evidence (FR-1, FR-2, FR-3). FR-4b, FR-4c, and FR-5 cite T5.2/T5.3 cross-references per AC-X-1 discipline. Determinism diff is byte-clean for FR-1 and FR-3.
- L3: NFR-9 evidence captured — two previously-passing inputs (pass_clean.json and pass_with_minor.json) both still pass FR-1 after it was wired in.
