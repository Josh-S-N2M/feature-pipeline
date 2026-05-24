---
id: README-mcp-provisioning-postmortem-2026-05-24
doc_type: postmortem-index
status: draft
generated: 2026-05-24
generated_by: forensic-postmortem-pass (claude-opus-4-7)
feature_under_review: devcontainer-mcp-provisioning-r1
trigger: live MCP failure observed in .claude/runtime/mcp-events.jsonl on 2026-05-24
---

# MCP Provisioning Postmortem — 2026-05-24

## TL;DR

The `devcontainer-mcp-provisioning-r1` feature shipped a configuration in which **5 of 7 MCP servers were broken** at the configuration, install, or transport layer. The pipeline's hard gate (PV-5.C-HARDGATE per ADR-0043) returned exit 0 against this broken state. The hard gate was authored explicitly to prevent this class of failure; it failed silently in exactly the way the user's verbatim ADR-0043 rationale warned about.

The forensic root-cause pass identified **12 distinct defects** across the codebase, the audit machinery, and the pipeline process. **Four defects are BLOCKER**; the other 8 are MAJOR. None were caught by any automated audit. The execution pipeline never ran past Phase 0 in this run; the feature was effectively hand-finished and the deliverable packager accepted `delivery_status: ready-for-execution-validation` as shippable.

## Files in this postmortem

| File | Audience | Purpose |
|---|---|---|
| [`01-error-log.json`](01-error-log.json) | AI agents | Machine-actionable structured defect log. Each entry is self-contained (evidence, root cause, reproduction command, fix). Designed so a future agent loading a single record has everything it needs. |
| [`02-pipeline-trace.md`](02-pipeline-trace.md) | Humans (engineers + AI architects) | For each defect: which pipeline stage, agent, audit, or gate should have caught it, and why it didn't. Identifies 5 cross-cutting patterns. |
| [`03-hardening-recommendations.md`](03-hardening-recommendations.md) | Humans (engineers + pipeline maintainers) | Eight concrete changes (H1–H8) ordered by leverage and cost. Closes 11 of 12 defects with low-to-medium cost; the 12th requires a high-cost orchestrator capability. |
| [`README.md`](README.md) | All | This document — index + executive summary. |

## The 12 defects, ranked

| ID | Severity | One-line description |
|---|---|---|
| DEF-01 | BLOCKER | Probe script reads `.transport` but `.mcp.json` schema uses `.type` |
| DEF-02 | BLOCKER | Probe omits MCP `initialize` handshake before `tools/list` |
| DEF-03 | BLOCKER | `.mcp.json` invokes `mcp-openapi-schema` with no schema-path arg |
| DEF-04 | BLOCKER | `.mcp.json` calls `uvx` but `uv`/`uvx` is not installed in the image |
| DEF-05 | MAJOR | Serena invocation missing `start-mcp-server` argv prescribed by ADR-0041 |
| DEF-06 | MAJOR | Sentinel naming/location diverge from ADR-0041 §Decision §2 |
| DEF-07 | MAJOR | Exa agent allowlist names tools the live server doesn't expose |
| DEF-08 | MAJOR | `audit_mcp.py --with-runtime` is misnamed — performs no live MCP-server probe |
| DEF-09 | BLOCKER | Feature shipped `ready-for-execution-validation` without running PV-5 live checks |
| DEF-10 | MAJOR | Architecture audit verdict approved despite known design-vs-implementation drift |
| DEF-11 | MAJOR | Cross-artifact audit cycle 4 `needs_reconciliation` with 0 findings — accepted as pass |
| DEF-12 | MAJOR | Execution pipeline ran in `single-agent-fallback` mode — quality verdicts never issued |

Detailed evidence and fixes in [`01-error-log.json`](01-error-log.json).

## The 5 cross-cutting patterns

1. **Specified-but-never-run gate criteria.** PV-5.C1..C21 are BLOCKER-tagged but require a live Codespace the pipeline can't drive. They were deferred to humans who didn't execute them.
2. **Static auditors mistaken for runtime auditors.** `--with-runtime` on `audit_mcp.py` does NOT probe the registered MCP servers; it only spawns servers for toxic-combinations categorization. The naming created a false belief that live behavior was verified.
3. **ADR-to-implementation gap.** ADRs (especially ADR-0041) prescribed concrete commands, paths, and argv strings. No auditor compared the prescriptions against the eventual implementation.
4. **Verdict-without-finding paradoxes accepted.** A reviewer emitted `verdict: "needs_reconciliation"` with `findings.length == 0`. The orchestrator accepted this as pass.
5. **Emergency modes used on canonical paths.** Single-agent-fallback was designed for emergencies (tool grants missing). It was used on the canonical happy path of a FULL-scope feature; the recipe orchestrator did not block it.

Pattern analysis in [`02-pipeline-trace.md`](02-pipeline-trace.md) §"Cross-cutting pattern observations".

## The 8 hardening changes

Ordered by leverage (defects prevented per dollar). Composite roadmap in [`03-hardening-recommendations.md`](03-hardening-recommendations.md):

1. **H5** — Verdict invariant validation (Trivial cost; closes DEF-11).
2. **H4** — Forbid `single-agent-fallback` for FULL-scope features (Low; DEF-12).
3. **H7** — `.mcp.json` ↔ ADR-0041 install-taxonomy parity OP rule (Low; DEF-03, DEF-05).
4. **H3** — Design-realization audit dimension for `review-architecture-auditor` (Medium; DEF-03, DEF-05, DEF-06, DEF-10).
5. **H6** — Discovery-research §Protocol Conformance section (Low; DEF-02).
6. **H1** — `--with-mcp-reachability` audit flag + live handshake check (Medium; DEF-01, DEF-02, DEF-04, DEF-07, DEF-08).
7. **H8** — Live tool-surface drift detection (Low when composed with H1; DEF-07).
8. **H2** — Orchestrator-driven Codespace rebuild loop (High; DEF-09).

## Recommended sequence

### This week — Quick wins (4 defects closed)

- H5: verdict invariants
- H4: forbid single-agent-fallback on FULL
- H7: install-taxonomy parity OP

These three are low-cost and immediately reduce the surface area where the next slip could clear the gates.

### This month — Pipeline hardening (11 of 12 defects closed)

- H3: design-realization audit dimension
- H6: protocol-conformance research subsection
- H1: `--with-mcp-reachability` audit
- H8: tool-surface drift (compose with H1)

After this sequence, the only remaining gap is DEF-09 (the live-Codespace-verification gap), which H2 addresses.

### Long-term — Close the loop (12 of 12)

- H2: orchestrator-driven Codespace rebuild loop.

Until H2 lands, the canonical posture for FULL-scope devcontainer-touching features is: **the pipeline ships without live verification, and the deliverable archive must mark this explicitly** — not soft-pedal it as "User-driven; not blocking ship."

## What this postmortem deliberately does not do

- It does **not** patch the four broken files (`.mcp.json`, `.devcontainer/lib/mcp-ping.sh`, `.devcontainer/Dockerfile`, `.devcontainer/postCreate.sh`). Per [`03-hardening-recommendations.md`](03-hardening-recommendations.md) §"What NOT to do" — patching before hardening risks re-running the same gates that approved the original bug.
- It does **not** assign blame to ADR-0043 or to any specific authoring agent. The defects are systemic. The fix is at the pipeline-architecture level, not at the per-document level.
- It does **not** propose retiring auditing-mcp. The auditor's static dimensions (OP-1..OP-10) catch important things and should remain. The issue is what it doesn't check, not what it does.

## Status

- **Defects:** identified, documented, evidence captured, reproductions recorded.
- **Pipeline failure modes:** traced and mapped to the 5 patterns.
- **Hardening:** recommended in priority order; not yet implemented.
- **Code patches:** not yet authored, by design (see §"What this postmortem deliberately does not do").

Next steps require user prioritization across:
- (a) Land H5 + H4 + H7 this week and then patch the four broken files; OR
- (b) Patch the four broken files immediately (operational urgency) AND open follow-on issues for H1–H8; OR
- (c) Defer pipeline hardening; treat this as a one-off operational fix.

Recommendation: **(a)**. The pipeline's central purpose is to prevent exactly this class of failure. The week's worth of work to make it actually do so before patching is the highest-leverage use of effort.
