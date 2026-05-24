---
id: HARDENING-mcp-provisioning-postmortem-2026-05-24
doc_type: pipeline-hardening-recommendations
status: draft
generated: 2026-05-24
generated_by: forensic-postmortem-pass (claude-opus-4-7)
feature_under_review: devcontainer-mcp-provisioning-r1
companion_artifacts:
  - Issues/mcp-provisioning-postmortem-2026-05-24/01-error-log.json
  - Issues/mcp-provisioning-postmortem-2026-05-24/02-pipeline-trace.md
  - Issues/mcp-provisioning-postmortem-2026-05-24/README.md
---

# Pipeline Hardening — concrete changes to prevent recurrence

Recommendations are ranked by **leverage** (how many of the 12 defects each change prevents) and **cost** (effort to land). The five patterns identified in [`02-pipeline-trace.md`](02-pipeline-trace.md) are addressed by changes H1–H8 below.

## H1 — Make the "hard gate" an actual hard gate

**Pattern addressed:** P1 (specified-but-never-run criteria) + P2 (static auditor mistaken for runtime).
**Defects prevented:** DEF-01, DEF-02, DEF-03, DEF-04, DEF-05, DEF-07, DEF-09. **7 of 12.**

### What changes

1. **Rename `--with-runtime` to `--with-toxic-runtime`** in `audit_mcp.py` and `check_toxic_combinations.py`. Adjust the few places that reference it (`phase-validators.md` PV-5.C-HARDGATE, `gate-6-hard-gate-contract.md`).
2. **Add `--with-mcp-reachability`** as a new orthogonal flag on `audit_mcp.py`. This flag:
   - Reads each `.mcp.json` server entry.
   - For stdio servers: launches the server via the exact `command + args + env` from .mcp.json, performs the canonical 3-message MCP handshake (`initialize` → `notifications/initialized` → `tools/list`), records the returned tool catalog.
   - For HTTP servers (`"type": "http"`): POSTs the same 3-message sequence (or just `initialize`) with the configured headers (env-vars resolved); records the returned tool catalog and HTTP status.
   - Emits BLOCKER findings for any: (a) server that fails to start; (b) server whose handshake fails; (c) tool named in a per-agent `mcp__<server>__<tool>` allowlist but missing from that server's tools/list.
3. **Wire the new flag into PV-5.C-HARDGATE.** PV-5 must run `audit_mcp.py --with-mcp-reachability` AND it must execute against a freshly-rebuilt Codespace (see H2).

### Why this works

The current `audit_mcp.py` audits source files. The new check audits **live system behavior**. The combination protects against both ADR-vs-implementation drift (static side) and protocol-/install-/transport-level breakage (live side).

### Cost

Medium — one new Python script that reuses the in-repo MCP handshake protocol code (the one currently bug-laden in mcp-ping.sh, but the bugs there can be fixed in the same pass). Roughly 200-300 LoC.

### Risk to land

Low. The flag is additive; existing callers continue to work; opt-in semantics during a rollout window.

---

## H2 — Drive a "Codespace rebuild loop" from the orchestrator

**Pattern addressed:** P1 (specified-but-never-run criteria).
**Defects prevented:** DEF-09. The enabling change behind H1.

### What changes

The orchestrator gains the ability to:
1. Trigger a Codespace rebuild via the **GitHub Codespaces REST API** (`POST /user/codespaces/{name}/start`) or the `gh codespace rebuild` CLI from outside the active Codespace.
2. Wait for the new Codespace's `postCreate.sh` and `postStart.sh` to complete (via lifecycle hooks or polling `.claude/runtime/mcp-events.jsonl`).
3. SSH or `gh codespace exec` into the rebuilt Codespace to run `audit_mcp.py --with-mcp-reachability`.
4. Collect the audit output. Exit 0 → resume; exit !=0 → halt with the findings.

Alternative — if a full Codespace rebuild is too costly per gate, use a **container-in-container or docker-compose** local rebuild that exercises the same lifecycle scripts in an isolated environment. The trade-off is fidelity vs cost; for a hard gate on devcontainer changes, full fidelity is worth it.

### Why this works

The current pipeline lives INSIDE the Codespace it would test, which is the topological reason live verification was deferred to humans. Driving from outside the artifact-under-test eliminates the conflict.

### Cost

High — new orchestrator capability, network/auth plumbing for the GH API, latency budget (Codespace cold-cache rebuilds take ~10 min per run). Justified by the fact that this gate is the load-bearing protection for the entire MCP/devcontainer surface.

### Risk to land

Medium. Requires a GH PAT scope or OIDC integration. Reuses existing `verify-at-execution.md` documentation discipline for what to check.

---

## H3 — Add a "design-realization" audit dimension to `review-architecture-auditor`

**Pattern addressed:** P3 (ADR-to-implementation gap).
**Defects prevented:** DEF-03, DEF-05, DEF-06, DEF-10. **4 of 12.**

### What changes

`review-architecture-auditor` gains an audit axis: for every ADR in the feature's `adrs/` folder, identify all **concrete artifacts the ADR names verbatim** — file paths, command strings, function names, schema fields, sentinel names. For each named artifact:
- If the eventual codebase contains a file/string at that path: diff the ADR's prescription against the actual contents; emit MAJOR on any divergence.
- If the ADR-named path doesn't exist in the codebase yet: emit INFO (this is the normal state during design); the diff fires at the cross-artifact audit stage once code is written.

A practical implementation: a YAML/JSON appendix to each ADR template (`adr_prescriptions.yaml`) listing the concrete artifacts the ADR commits to. The audit reads this list. Authors fill it in when writing the ADR. This is a contract artifact, not an inferential pass.

### Why this works

ADRs are load-bearing documents in this pipeline. Today they describe decisions but have no enforcement mechanism beyond human review. This change makes ADRs *executable contracts*.

### Cost

Medium — new audit dimension + ADR template addendum. Existing ADRs need a one-time backfill of the `adr_prescriptions.yaml` block for any concrete artifact they name. The audit script itself is ~100-200 LoC.

### Risk to land

Low. Pure addition. Existing ADRs without the appendix simply skip the new audit dimension.

---

## H4 — Forbid `single-agent-fallback` for FULL-scope features

**Pattern addressed:** P5 (emergency modes on canonical paths).
**Defects prevented:** DEF-12 (and the quality-control collapse that enabled DEF-01 through DEF-07).

### What changes

The recipe-feature-pipeline orchestrator inspects the feature's `scope_class` (per ADR-0023: FULL / MINOR / PATCH). If `scope_class == FULL` AND the orchestrator detects a missing dispatch tool:
- The orchestrator must HALT and surface a structured user-escalation: *"Cannot dispatch execute-task-quality-handler / execute-phase-quality-reviewer. FULL-scope features require multi-agent quality enforcement. Re-invoke this pipeline with the correct tool grants."*
- The fallback path remains available for `scope_class == MINOR | PATCH` features where the cost-benefit may flip.

The orchestrator also records the dispatch mode in `checkpoint.json` and emits a state-transitions log entry tagged `mode_change`. Audits at downstream stages can read this and BLOCKER-fail if mode==single-agent-fallback and scope==FULL.

### Why this works

The fallback was designed for emergencies. Using it on the canonical path of a FULL-scope feature defeats the pipeline's defense-in-depth and is a process violation. Make the violation visible and blocking.

### Cost

Low — orchestrator-level branch; checkpoint.json schema addition.

### Risk to land

Low. Backward-compatible; only adds halts where the current behavior was a silent degradation.

---

## H5 — Verdict invariant validation

**Pattern addressed:** P4 (verdict-without-finding paradoxes accepted).
**Defects prevented:** DEF-11.

### What changes

A small post-write validator on every reviewer output (`shared-document-reviewer`, `review-architecture-auditor`, `review-cross-artifact-auditor`, `finalize-deliverable-packager`):

| Invariant | Rule |
|---|---|
| INV-1 | `verdict == "pass"` ⇒ `findings.length == 0` OR all findings are NIT |
| INV-2 | `verdict == "needs_reconciliation"` ⇒ `findings.length > 0` |
| INV-3 | `verdict == "approved_with_conditions"` ⇒ at least one finding with severity ∈ {MAJOR, MINOR} (no BLOCKER) |
| INV-4 | `findings[*].severity == "BLOCKER"` ⇒ `verdict != "pass"` AND `verdict != "approved_with_conditions"` |

The orchestrator runs these invariants on every audit JSON before consuming the verdict. Any violation surfaces as `audit-verdict-malformed` and halts.

### Why this works

The current pipeline trusts auditor output structurally. Adding invariant checks prevents the "verdict says X, findings say Y" silent acceptance pattern observed in DEF-11.

### Cost

Trivial — ~30 LoC validator; runs in microseconds.

### Risk to land

Trivial. Pure invariant enforcement.

---

## H6 — Discovery-research must produce a "protocol facts" section per server

**Pattern addressed:** the pipeline trusts implementers to "know the protocol."
**Defects prevented:** DEF-02 (and reduces probability of similar protocol-level slips).

### What changes

The `KB-codebase-research` (or a new `KB-protocol-conformance`) skill adds a required subsection to `research-notes/T-<NNN>-<server>.md`: **§Protocol Conformance**. The author records:
- The server's required handshake sequence (citing the spec version).
- Whether the server enforces or relaxes spec-required ordering.
- Whether the server emits non-protocol output (stderr logs, banner lines, etc.) that probe scripts must handle.
- The exact known-good probe command (an executable line that an implementer can paste).

For MCP servers specifically, the §Protocol Conformance section MUST cite the MCP spec lifecycle requirement and provide the 3-message-handshake template.

### Why this works

DEF-02 was caused by an absence of protocol knowledge in the design artifacts. Pushing this knowledge into the research-notes — under a structured, mandatory section — means the implementer has the protocol fact in hand when writing the probe.

### Cost

Low — KB update plus a research-note template change. Existing notes need a one-time backfill.

### Risk to land

Low. Pure addition.

---

## H7 — `auditing-mcp` OP-N rule for `.mcp.json` ↔ ADR-0041 install-taxonomy parity

**Pattern addressed:** P3 (ADR-to-implementation gap), narrower than H3 but more directly enforceable.
**Defects prevented:** DEF-03, DEF-05 (and any future ADR-taxonomy drift).

### What changes

Add a new OP rule script `audit_op_install_taxonomy_parity.py`:
1. Parse the install-taxonomy table from ADR-0041 (or whatever ADR holds it; the rule is "find the canonical install-taxonomy ADR for this feature").
2. For each row, compare the ADR's prescribed `command + args` against `.mcp.json` entry for the same server.
3. Emit MAJOR on any token-level divergence (missing arg, extra arg, different command).

### Why this works

H3 is the general case; H7 is the specific MCP case that this postmortem identifies as load-bearing.

### Cost

Low — ~80 LoC. Reuses the existing OP-rule dispatcher in `audit_mcp.py`.

### Risk to land

Low.

---

## H8 — Live tool-surface drift detection for HTTP MCP servers

**Pattern addressed:** P3 + P2 (drift between agent allowlists and live server surface).
**Defects prevented:** DEF-07.

### What changes

The `--with-mcp-reachability` audit from H1 already calls `tools/list` against each registered server. Extend it to:
1. Collect the live tool catalog.
2. Cross-reference against every agent's `tools:` allowlist matching `mcp__<server>__<tool>`.
3. Emit MAJOR for any allowlist token whose `<tool>` portion is not in the live catalog.
4. Emit MINOR for any live tool that no agent allowlists (potential under-utilization; informational).

### Why this works

Hosted HTTP MCP servers (exa, context7) evolve their tool surface without the consumer's knowledge. Static audits can never catch this; only a live probe can.

### Cost

Low if H1 is in flight (it's a 20-LoC extension to the same script).

### Risk to land

Low (composes with H1).

---

## Composite roadmap

If implemented in priority order:

| # | Change | Defects prevented | Cost | Cumulative coverage |
|---|---|---|---|---|
| 1 | H5 verdict invariants | DEF-11 | Trivial | 1 / 12 |
| 2 | H4 forbid single-agent-fallback for FULL | DEF-12 | Low | 2 / 12 |
| 3 | H7 install-taxonomy parity OP | DEF-03, DEF-05 | Low | 4 / 12 |
| 4 | H3 design-realization audit dimension | DEF-03, DEF-05, DEF-06, DEF-10 | Medium | 6 / 12 |
| 5 | H6 protocol-conformance research subsection | DEF-02 | Low | 7 / 12 |
| 6 | H1 `--with-mcp-reachability` audit + rename `--with-runtime` | DEF-01, DEF-02, DEF-04, DEF-07, DEF-08 | Medium | 11 / 12 |
| 7 | H8 live tool-surface drift (compose with H1) | DEF-07 | Low | 11 / 12 |
| 8 | H2 orchestrator-driven Codespace rebuild loop | DEF-09 | High | **12 / 12** |

### Quick wins (this week)

H5, H4, H7 — all low-cost, prevent 4 defects collectively, no new infrastructure.

### Medium-term (this month)

H3, H6, H1, H8 — adds the missing audit dimensions and the live-reachability check. Closes 11 of 12 defects.

### Long-term

H2 — the only genuinely expensive change, but the only one that closes DEF-09 (the deliverable-status loophole). Until H2 lands, the pipeline must explicitly accept that "ship without live verification" is the canonical happy path for FULL-scope features — and that admission should appear in the deliverable-archive frontmatter as a structured warning, not a soft-pedaled "User-driven; not blocking ship" sentence.

---

## What NOT to do

- **Do not** add more BLOCKER criteria to PV-5 without first wiring an enforcement mechanism (H1 + H2). Tagging things BLOCKER without enforcement is what produced DEF-09.
- **Do not** patch the four immediately-broken files (.mcp.json, mcp-ping.sh, Dockerfile, postCreate.sh) without first landing H5 + H4 + H7 + H3. Patching now risks re-running the same gate sequence that approved the original bug; the next slip would clear the same way. Land the audit hardening first; then patch and observe whether the new audits would have caught the original bugs.
- **Do not** treat this as a "ADR-0043 was the gate; it failed; tighten ADR-0043" problem. ADR-0043 declared a contract. The pipeline did not deliver against the contract. The failure is in the delivery surface, not in the declared discipline.
