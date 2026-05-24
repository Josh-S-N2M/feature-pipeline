---
id: PIPELINE-TRACE-mcp-provisioning-postmortem-2026-05-24
doc_type: postmortem-pipeline-trace
status: draft
generated: 2026-05-24
generated_by: forensic-postmortem-pass (claude-opus-4-7)
feature_under_review: devcontainer-mcp-provisioning-r1
companion_artifacts:
  - Issues/mcp-provisioning-postmortem-2026-05-24/01-error-log.json
  - Issues/mcp-provisioning-postmortem-2026-05-24/03-hardening-recommendations.md
  - Issues/mcp-provisioning-postmortem-2026-05-24/README.md
---

# Pipeline Trace — how each defect cleared every gate

For each defect catalogued in [`01-error-log.json`](01-error-log.json), this document names the pipeline stage(s) and the responsible artifact / agent / gate that *should have* caught it, and explains *why it didn't*. The feature pipeline has six human gates and three audit stages. Every defect cleared all of them.

## Pipeline reference

| # | Stage | Artifact produced | Audit / gate that protects it |
|---|---|---|---|
| 1 | Intent Clarification | `intent-clarification.md` | Gate 1 (human) |
| 2 | PRD Authoring | `prd-v<N>.md` | Gate 2 (human); `shared-document-reviewer` |
| 3 | Discovery Planning | `research-plan.md` | Gate 3 (human); `shared-document-reviewer` |
| 4 | Discovery Research | `codebase-analysis.json`, `research-notes/T-*.md` | `synth-critic` (CoVe on claims) |
| 5 | Synthesis | `synthesis.md`, framing JSONs | (none — internal) |
| 6 | Per-layer Design | `<layer>-design.md` × N | `shared-document-reviewer` |
| 7 | Design Composition | `blueprint-v<N>.md`, ADRs | Gate 4 (human); `shared-document-reviewer`; **`review-architecture-auditor`** |
| 8 | Plan Authoring | `plan-v<N>.md` | Gate 5 (human); `shared-document-reviewer` |
| 9 | Test Authoring (parallel) | `acceptance-tests.md`, `phase-validators.md` | `shared-document-reviewer` |
| 10 | Cross-Artifact Audit | `cross-artifact-audit-issues.json` | **`review-cross-artifact-auditor`** (diff-mode, 4-cycle cap) |
| 11 | Reconciliation | `reconciliation-log-cycle-<N>.md` | (loop until pass or cap) |
| 12 | Task Decomposition | `tasks.json` | `shared-document-reviewer` |
| 13 | Deliverable Packaging | `deliverable-archive.md`, `packager-report.json` | `finalize-deliverable-packager` validation |
| 14 | Gate 6 (final approval) | (human signal) | — |
| 15 | Execution Pipeline | per-task results, code commits | **`execute-phase-quality-reviewer`** → **`execute-finalize-reconciler`** → **PV-5 hard-gate** per ADR-0043 |

## Defect-by-defect trace

### DEF-01 `.transport` vs `.type` schema mismatch in `mcp-ping.sh`

| Gate / artifact | Should have caught it? | Why it didn't |
|---|---|---|
| **Per-layer design (codespaces-design.md)** | YES — this layer owns lifecycle scripts | The design described mcp-ping.sh's *purpose* (probe each server) but never named the *schema field* it would parse. The KB-codespaces-design pairing did not require this level of detail in design artifacts. |
| **Blueprint v3** | YES — Blueprint should reflect the .mcp.json schema choice | Blueprint declares server inventory and transport semantics, but does not pin a probe-side parse contract. The mismatch is between two implementation artifacts that the Blueprint treats as independent. |
| **ADR-0041** | NO — out of scope (install-mechanism ADR) | ADR-0041 is about *how to install*, not *how to probe*. No ADR owns the probe-side schema contract. |
| **`shared-document-reviewer` (cc-design / codespaces-design review)** | NO — document-level reviewer, not code-level | This reviewer cannot validate a yet-to-be-written shell script against a yet-to-be-written .mcp.json schema. Both files appear in Phase 1+ execution, after document review closes. |
| **`review-architecture-auditor`** | YES (theoretically) — should verify design realization against codebase facts | Did not include a 'design-realization-check' axis. CoVe + blast-radius + brief-honor dimensions don't include "are the two files this design produces internally consistent?" |
| **`auditing-mcp` `validate_mcp_config.py`** | NO — only validates .mcp.json | Lines 48-55 catch the **opposite** error (`transport` in .mcp.json, no `type`) — useful but doesn't help here because .mcp.json is correct; the bug is in the consumer script. |
| **PV-5.C-HARDGATE** | YES — should catch any unreachable server | DEF-08: `--with-runtime` is misnamed; it does NOT probe the registered servers. Returned exit 0 against the broken state. |
| **Execute-task-quality-handler** | YES — would run end-to-end checks on T3.1 (probe script) | DEF-12: never invoked. Single-agent-fallback mode. |

**Verdict:** The pipeline has multiple places that *could* have caught this but none whose contract *required* them to. The DEF-01 defect is precisely the kind of code-level cross-file consistency check that nobody owns.

---

### DEF-02 Probe omits MCP `initialize` handshake

| Gate / artifact | Should have caught it? | Why it didn't |
|---|---|---|
| **Research notes (T-001..T-008)** | YES — per-server research notes should record protocol facts | The research notes documented install paths and tool surfaces but did NOT call out the spec-level requirement that `tools/list` requires prior `initialize`. The MCP spec was not exhaustively researched at the protocol-handshake level. |
| **Synthesis claims** | YES — verified claims about MCP protocol behavior | No claim records the 3-message-handshake requirement. The synthesis frames were oriented toward server-selection and toxicity, not protocol conformance. |
| **Plan-author** | YES — T3.1 (`mcp-ping.sh`) specifies what the script does | Plan specifies the script's *outputs* (JSON record shape per ADR-0037) but not the *protocol* it speaks. |
| **Acceptance test AT-002** | YES — 'Per-server probe returns success for every server' | AT-002 specifies the *expected outcome* (exit 0, 7 result:pass objects) but not the *protocol* the probe must speak. A probe that returned 7 result:fail objects would also fail AT-002, but the test does not isolate handshake-omission from any other failure. |
| **Phase validator PV-3.C-*** | YES (lifecycle-script-run dimension) | PV-3 (Lifecycle Scripts phase) was specified but never run live; see DEF-09. |
| **`review-architecture-auditor`** | NO — protocol-level conformance is below the architecture-audit grain | The auditor doesn't model the MCP wire protocol; it verifies design-vs-claim consistency. |

**Verdict:** This defect required pre-existing protocol knowledge that the discovery-research stage did not surface. The pipeline trusts implementers to "know MCP" — and the implementer didn't.

---

### DEF-03 mcp-openapi-schema missing schema-path arg

| Gate / artifact | Should have caught it? | Why it didn't |
|---|---|---|
| **Research note T-002 (mcp-openapi-schema)** | YES — should describe canonical invocation | Did record the install method but did not record the load-bearing fact that the server requires argv[2] (or a CWD-side openapi.yaml) to start. Upstream README does mention this but research-note depth was insufficient. |
| **ADR-0041** | YES — install-taxonomy explicitly says `npx -y "mcp-openapi-schema@${MCP_OPENAPI_SCHEMA_VERSION}" <spec-path>` | The ADR correctly named the `<spec-path>` token. **The implementation dropped it.** No audit compared .mcp.json args against the ADR taxonomy. |
| **Blueprint v3** | YES — fact-disposition row references the install path | Same as ADR-0041: correctly framed; not enforced. |
| **`shared-document-reviewer` Gate 4** | NO — doc-level only | Cannot anticipate that .mcp.json (yet to be written) will diverge from the ADR. |
| **Phase-0 verify-at-execution H-3** | YES — STALE_PACKAGE disposition was recorded | H-3 noted staleness but did NOT verify the resolved invocation form on a probe run. Verify-at-execution treats install-method correctness as a research question, not a runtime question. |
| **PV-1.C-***, **PV-2.C-***  | YES — .mcp.json shape check | PV-1 verifies file existence + 7-entry count + JSON validity; does NOT compare each entry's args against any spec. |
| **`auditing-mcp` OP-2 consumer-mapping** | NO — checks per-agent allowlists vs server names | Only validates that named servers are referenced; doesn't verify that the named servers can actually start. |

**Verdict:** ADR-0041 prescribed the correct invocation. Implementation drifted. No auditor compared the two. This is the **clearest single-gate-missing case**.

---

### DEF-04 uvx prerequisite missing

| Gate / artifact | Should have caught it? | Why it didn't |
|---|---|---|
| **ADR-0041 §Decision §1 (Hybrid Features posture)** | YES — declares "Devcontainer Features for runtime managers" | Names node:1 and go:1 features explicitly; does NOT name uv. The ADR author treated uvx as if it were universally available. |
| **`design-codespaces` per-layer design** | YES — Codespaces design owns runtime managers | The design lists Node 20 and Go 1.22 prerequisites; uv is unmentioned. |
| **`review-architecture-auditor` brief-honor** | YES — should verify install paths are coherent | The audit didn't run `command -v uvx` against the image; design-realization-check axis is missing (DEF-10). |
| **Phase-0 verify-at-execution** | YES — load-bearing for AC-CS-9 (gitnexus skip-grammars) and serena install | T0.4 caught the gitnexus-install-method category error (Python→npm). It did NOT catch that serena's still-Python install path required uvx that was never installed. The verify-at-execution sweep checks identifiers and command success but not transitive prerequisites. |
| **`postCreate.sh` install_serena()** | DID catch it (lines 67-71 emit status:failed) | The status was logged but the orchestrator continued. The "warn-and-continue" posture at line 163 (`install_serena || emit_degraded_banner`) means a primary-degraded banner emits and execution proceeds. No phase validator halts on this. |
| **PV-3.C-* / PV-5.C2 (cold-cache postCreate completes)** | YES — would surface install_complete:failed in mcp-events.jsonl | Never executed live; see DEF-09. |

**Verdict:** The pipeline correctly *records* the install failure but has no mechanism to *halt* on it. The "warn-and-continue per ADR-0037" posture is appropriate for resilience but lethal when the gate that should re-evaluate is itself paper.

---

### DEF-05 Missing `start-mcp-server` argv (serena)

Identical trace pattern to DEF-03. ADR-0041 prescribed; implementation diverged; no auditor compares the two.

---

### DEF-06 Sentinel naming/location divergence from ADR-0041

| Gate / artifact | Should have caught it? | Why it didn't |
|---|---|---|
| **ADR-0041 §Decision §2** | Authoritative — names `<server>@<version>.installed` under `.claude/runtime/install-sentinels/` | Self-consistent ADR. Not enforced anywhere. |
| **postCreate.sh** | Should match | Author either used a draft ADR or independently invented a naming. Diverged in 3 ways: location (no install-sentinels/ subdir), separator (dash instead of @), suffix (no `.installed`). |
| **Architecture audit** | DEF-10 same pattern as DEF-05 |

**Verdict:** Same as DEF-05.

---

### DEF-07 Exa allowlist names tools the server doesn't expose

| Gate / artifact | Should have caught it? | Why it didn't |
|---|---|---|
| **`auditing-mcp` OP-2 (consumer-mapping)** | PARTIALLY — verifies server-name references | Checks `mcp__<server>__*` references the allowlist names against the .mcp.json server inventory. Does NOT verify the `<tool>` portion against the live server's tools/list. |
| **Research note T-006 (exa)** | YES — should record current tool surface | Documented an older Exa tool inventory. Server has evolved; allowlist hasn't. |
| **`auditing-mcp` `--with-runtime`** | YES (theoretically) | DEF-08: misnamed; no live probe of the named servers. |

**Verdict:** No automated mechanism cross-references per-agent `mcp__<server>__<tool>` entries against the actual server tools/list. Drift is inevitable.

---

### DEF-08 `--with-runtime` flag is misnamed

This is **the meta-defect**. It's not a single-stage failure; it's a *design defect of the pipeline's enforcement surface itself*.

- **`audit_mcp.py`** parses `--with-runtime` and forwards it to **`check_toxic_combinations.py` only**.
- **`check_toxic_combinations.py --with-runtime`** does spawn servers and call tools/list — but only to *categorize* them for toxic-pair detection (filesystem-plus-web, database-plus-network, etc.). It does NOT verify that THIS project's 7 servers match THIS project's per-agent allowlists or are reachable.
- **`phase-validators.md` PV-5.C-HARDGATE** trusts `audit_mcp.py --with-runtime --severity-threshold BLOCKER exits 0` as proof of live MCP-server health.
- The two contracts (PV-5's "runtime" intent vs audit_mcp's "runtime" implementation) silently disagree on what "runtime" means.

The pipeline therefore had a gate whose name promised what it could not deliver. ADR-0043 cited the user rationale verbatim: *"MCPs can cause a lot of problems if they are not stable and the system fails silently or the devcontainer and docker fail."* The gate that was meant to prevent exactly this failed silently in exactly the way the user feared.

---

### DEF-09 Pipeline shipped feature without running PV-5 live verification

This defect required tracing every state transition. Reconstructed timeline:

1. **2026-05-23T03:15** — Gate-6 approved (`gate_6_decision: approved`).
2. **2026-05-23T03:20** — Execution pipeline T0 transition (INIT → pending).
3. **2026-05-23T03:21** — Execute-orchestrator self-reports a tool-grant blocker (`missing-dispatch-tool`); transitions to TERMINATED.
4. **2026-05-23T03:25** — User corrective brief voids T13; orchestrator re-enters pending in **single-agent-fallback mode** (DEF-12).
5. **2026-05-23T03:26** — Phase-0 parallel-frontier dispatched: T0.1..T0.10.
6. **2026-05-23T18:20** — Phase-0 escalates to user (`escalated_stub`): supply-chain findings F1/F2/F3. Only T0.1, T0.3 PASS; T0.2, T0.4, T0.5 surfaced findings; T0.6..T0.10 never executed.
7. **2026-05-23T19:30** — Reconciliation cycle 3 produced; design-side fixes dispatched.
8. **2026-05-23T20:30** — Packager cycle 2 produced verdict `approved_with_conditions`.
9. **2026-05-23T21:10** — User-driven Phase-0 RE-VERIFY recorded in verify-at-execution.md (`§H-1 / §H-4 / §H-5 re-verified by orchestrator using npm + Node in current devcontainer`).
10. **Final state per checkpoint.json**: `current_stage: execution_pipeline`, `stage_status: cycle_3_complete_awaiting_user_disposition_on_cycle_4`. **Execution pipeline Phases 1-5 NEVER ran via the orchestrator.**
11. **Git log** shows commits `6f46d14` ("Phase 0-4 — modifications to existing files") and `094d47e` ("Phase 5 — rollout + hard-gate exercise") landing later — written by manual user effort, not by the execution pipeline that the deliverable-archive claims drove them.

The deliverable-archive.md frontmatter declares `delivery_status: ready-for-execution-validation` and `Three Phase 5 tasks (T5.2 cold-cache, T5.3 warm-cache, T5.5 failure-mode rehearsals) require a fresh Codespace rebuild to execute their observation steps; documented in verify-at-execution.md §T5.2/§T5.3/§T5.5 with expected outcomes. User-driven; not blocking ship.`

**Translation:** the BLOCKER-tagged PV-5.C1..C21 criteria were collectively marked "user-driven; not blocking ship" by the packager itself. This is the gate-bypass.

---

### DEF-10 Architecture audit verdict `approved_with_conditions`

The architecture-audit-issues.json verdict explicitly says *"No BLOCKER issues. [...] Recommend a focused in-place amendment dispatch."* This is correct for the dimensions the auditor checks (I-AA-001 filename drift, I-AA-002 consumer-set math). The auditor never went looking for ADR-0041 vs .mcp.json invocation-string drift. The gate was satisfied; the failure mode was below the gate's resolving power.

---

### DEF-11 Cross-artifact audit cycle 4 verdict `needs_reconciliation` count 0

The pipeline accepted this paradoxical verdict ("needs_reconciliation" with zero findings is structurally invalid) as if it were `pass`. The 4-cycle reconciliation cap (per ADR-0017) was already exhausted, so the pipeline had no remaining budget. It chose to move forward rather than halt. **The convergence-or-cap discipline failed because the cap was treated as a permission slip.**

---

### DEF-12 Single-agent-fallback bypassed quality verdict separation

Per ADR-0044 and the execute-* subagent design, the per-task quality verdict is supposed to come from `execute-task-quality-handler`, a DIFFERENT agent than the one that authored the code. In single-agent-fallback mode, the same agent does both. This collapses two of the three quality-defense layers (per-task verdict + phase-quality review) into self-grading.

The fallback exists for emergency continuation. It was used on the canonical path of a FULL-scope feature. The recipe-feature-pipeline orchestrator did not block this.

---

## Cross-cutting pattern observations

### Pattern 1 — "Specified but never run" gate criteria

PV-5.C1..C21 are tagged **BLOCKER** severity but require a live Codespace. The pipeline has no machinery to drive a fresh Codespace from inside an active session (the work happens INSIDE that very Codespace). The criteria are therefore deferred to humans, who do not execute them. This pattern shows up repeatedly:

- PV-1.C5 ("install_complete records appear") — specified, not run live.
- PV-2.C-* ("postStart re-runs and writes 7 readiness_probe records") — specified, not run live.
- PV-5.C8..C12 (failure-mode rehearsals) — specified, not run live.

When a criterion is BLOCKER but unenforceable, it is functionally MINOR.

### Pattern 2 — Static auditors mistaken for runtime auditors

The naming `--with-runtime` and `--with-mcp-reachability` and similar imply behavior the code does not deliver. The whole auditing-mcp family is a static analyzer over JSON + agent file contents. Adding `--with-runtime` to a flag does not transform a static analyzer into an end-to-end tester.

### Pattern 3 — ADR-to-implementation gap

ADRs prescribe concrete commands (ADR-0041 install taxonomy), file paths (ADR-0041 sentinel location), and invariants (ADR-0044 invoking_agent). No auditor compares these prescriptions against the eventual implementation. The current audit dimensions stop at "the design artifacts are internally consistent."

### Pattern 4 — Verdict-without-finding paradoxes accepted

`needs_reconciliation` with `count: 0` is structurally impossible. The pipeline accepted it. The cap-or-converge discipline assumes verdicts are well-formed. Adversarial verdicts slipped through.

### Pattern 5 — Emergency modes used on canonical paths

`single-agent-fallback` was designed for emergencies (orchestrator can't dispatch). It was used on the canonical path. The pipeline did not distinguish.

---

## Summary

Of 12 defects, **0 were caught by the pipeline's automated audits or gates**. The pipeline cleared the feature for ship despite:

- The hard-gate audit being a paper tiger (DEF-08).
- The deliverable packager accepting `ready-for-execution-validation` as shippable (DEF-09).
- A non-pass cross-artifact verdict being interpreted as pass (DEF-11).
- The quality-separation discipline being bypassed by fallback mode (DEF-12).
- The architecture audit having no design-realization-check axis (DEF-10).
- ADRs prescribing implementation details that no auditor compared against the implementation (DEF-03, DEF-05, DEF-06).
- The probe code making protocol-level errors that no per-layer designer or research-note flagged (DEF-01, DEF-02).
- A tool surface that auditors don't verify against per-agent allowlists (DEF-07).

The system explicitly designed to prevent silent MCP failures **silently shipped a configuration in which 5 of 7 MCP servers were broken at the configuration or transport layer.**

[`03-hardening-recommendations.md`](03-hardening-recommendations.md) names concrete changes.
