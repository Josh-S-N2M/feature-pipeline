---
id: PROPOSAL-cross-artifact-divergence-detection-gap
version: 0.1.0
doc_type: issue-proposal
status: adopted
feature_slug: pipeline-wide
generated: 2026-05-25
generated_by: claude (main agent) — promotion-prep from sibling analysis, scope narrowed to first-run quick wins per user direction
proposes_future_feature: pipeline-quickwins-hardening-r1
# --- status: adopted companion fields ---
since: 2026-05-25
adopted_by_feature_slug: pipeline-quickwins-hardening-r1
adopted_at: 2026-05-25
# --- Cross-link fields ---
escalates_from: ANALYSIS-cross-artifact-divergence-detection-gap
# escalated_to: <none — this is one of multiple proposals that will be authored against this analysis;
#                 the analysis remains open because the remaining hardening (design-realization audit,
#                 cross-file invariant catalog, reachability handshake, drift detection, agent-roster
#                 discipline) will be the subject of a follow-on proposal for a separate feature run>
companion_artifacts:
  - Issues/cross-artifact-divergence-detection-gap/analysis.md
  - Issues/cross-artifact-divergence-detection-gap/evidence/mcp-postmortem-2026-05-24/03-hardening-recommendations.md
  - Issues/cross-artifact-divergence-detection-gap/evidence/pv1-spec-vs-templates-divergence.md
  - Issues/devcontainer-mcp-provisioning-r1-deferrals/register.md  (rows H-4 and B-1 adopted by this same feature)
---

# Proposal — First-Run Quick-Wins Hardening After the MCP Shipment Incident

## Contents

- [x] TL;DR
- [x] Proposed Feature
- [x] In-Scope Mechanisms
- [x] Out-of-Scope (Deferred to Follow-On)
- [x] Motivation
- [x] Acceptance Sketch
- [x] Cross-links

## TL;DR

The MCP provisioning feature shipped with five of seven servers broken because the pipeline's gates check each artifact in isolation and never compare an ADR's prescription against the file that actually shipped. The full systemic fix is large and is captured in the sibling analysis. **This proposal carves out the quick-wins subset only** — five low-cost mechanisms that close the most acute exposures without requiring architectural change. The remainder (design-realization audit dimension, cross-file invariant catalog, live reachability handshake, tool-surface drift detection, the per-agent design discipline) is deferred to a follow-on feature run with a separate proposal.

Closing scope here:
1. **Verdict-vs-findings consistency check** — today a reviewer can return "approved" with blocking findings still in the list and nothing rejects that. Make it impossible.
2. **Forbid single-agent fallback for full-scope features** — the MCP shipment went through a single-agent execution path that bypassed the multi-agent review the gates assumed.
3. **Parity rule: the live `.mcp.json` must match what the install-taxonomy ADR prescribes** — the narrow, mechanical version of the larger design-realization audit that comes later. Authored as a new audit rule in the MCP audit skill.
4. **GitNexus install smoke test** — guard the load-bearing `GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1` environment variable so an upstream change doesn't silently break the install path.
5. **CI smoke test asserting `claude mcp list` connects** — a GitHub Actions workflow that fails loud if any configured MCP server is unreachable after a fresh provision.

## Proposed Feature

**Suggested slug:** `pipeline-quickwins-hardening-r1`
**Scope class:** MINOR (estimated 1–2 days of work; five discrete mechanisms, each bounded).
**Layers touched:** Claude Code (audit skill, reviewer discipline, orchestrator self-check, install script) and CI/CD (one new workflow file).

## In-Scope Mechanisms

### 1. Verdict-vs-findings consistency check
- **Where:** the phase-quality reviewer and any other reviewer that emits a verdict with a findings array.
- **What:** a deterministic check — if the findings array contains any entry with severity `BLOCKER` (or equivalent), the verdict cannot be `APPROVED` / `PASS`. Implemented as a structural validator on the reviewer's output JSON, run before the verdict is accepted upstream.
- **Why:** the MCP shipment passed gates that returned approved with non-empty blocking findings — the contract was honored on paper, broken in practice.

### 2. Forbid single-agent fallback for full-scope features
- **Where:** the feature-pipeline orchestrator's dispatch self-check.
- **What:** if the feature's scope class is FULL, the orchestrator refuses to dispatch any stage in single-agent-fallback mode. The check fires before dispatch; the fallback path is reserved for minor and patch scope features.
- **Why:** single-agent execution skips the cross-agent review structure the gates assume exists. For full features, that structure is load-bearing.

### 3. Parity rule between `.mcp.json` and the install-taxonomy ADR
- **Where:** the MCP audit skill (`auditing-mcp`).
- **What:** a new rule that, for each MCP server entry in `.mcp.json`, fetches the invocation form prescribed in the install-taxonomy ADR (ADR-0041) and verifies they match — argv strings, env var indirection, sentinel paths. Fails as `BLOCKER` on mismatch.
- **Why:** this is the narrowest possible version of the larger design-realization audit deferred to the follow-on run. It closes the specific defect that broke five servers without waiting for the broader audit dimension to land.

### 4. GitNexus install smoke test
- **Where:** the devcontainer post-create install script (or a separate pre-install verification block).
- **What:** a dry-run that asserts `GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1 npx gitnexus --version` (or equivalent) succeeds against the pinned GitNexus tag, and that the env var actually skips the C++ toolchain path. Failure halts install with a clear message about pin-tag drift.
- **Why:** flagged as the single high-forgetting-risk row in the MCP feature's deferral register. The env var is load-bearing; an upstream change would silently break the codespace.

### 5. CI smoke test for `claude mcp list` connectivity
- **Where:** a new GitHub Actions workflow under `.github/workflows/`.
- **What:** after a fresh provision (or against a known-good baseline), runs `claude mcp list` and asserts every entry in `.mcp.json` returns connected. Fails the job on any non-connected server. Triggered on PRs that touch `.mcp.json`, the devcontainer, or any of the audit skills.
- **Why:** today MCP-config drift can land in a PR and only surfaces at the next codespace rebuild. The deferral register flagged this as a medium-forgetting-risk item (B-1).

## Out-of-Scope (Deferred to Follow-On)

The sibling analysis catalogs a larger remediation set. **These items are explicitly deferred to a future feature run** (working title: cross-artifact and design-time discipline). They are not in scope here:

- Design-realization audit dimension for the architecture-audit reviewer (the broader version of the parity rule).
- Discovery-research protocol-conformance subsection requirement.
- Phase-validator-tier cross-file consistency invariant catalog.
- Live MCP reachability handshake (`--with-mcp-reachability` audit flag).
- Live tool-surface drift detection.
- Per-agent design discipline: mandatory agent-roster impact matrix, strengthened "preserve invariant" principle, skill-coverage check at design time, real gating on "blocks downstream" markers, and a feature-touch-coverage audit rule. (These come from the sibling per-agent-design-evaluation-gap analysis.)
- The post-ship trigger discipline observation in the deferral register's section O.
- The orchestrator-driven codespace rebuild loop.

The sibling analysis remains in `status: open` because of this carve-out; a follow-on proposal will adopt those items into the second run.

## Motivation

The MCP shipment incident is documented in the postmortem under this issue's evidence directory. Four blocking defects and eight major defects shipped past every gate. Partial patches landed afterward (commit `5a80122`) but the *mechanism that let it happen* is unchanged. The postmortem's "what NOT to do" section is explicit: do not patch the remaining broken files further until the audit hardening lands first, because patches will clear the same paper gates the original bugs cleared.

The five mechanisms above are the postmortem's named quick-wins plus the highest-forgetting-risk deferral plus the CI smoke test. Together they close roughly a third of the catalogued defects and the single highest-risk deferral, at low total cost.

## Acceptance Sketch

The pipeline's intent-clarification stage will refine these; rough shape:

- A reviewer that produces `verdict: APPROVED` with any `BLOCKER` finding in its output is rejected by an automated structural check before the verdict propagates.
- A full-scope feature run cannot enter the dispatch loop with any stage configured for single-agent fallback; the orchestrator self-check refuses.
- Running the MCP audit skill against the current repository state surfaces any drift between an ADR-prescribed invocation and the live `.mcp.json` entry as a blocking finding.
- A fresh codespace build runs the GitNexus dry-run check; the build fails with a diagnostic if the env-var contract no longer holds.
- A pull request that breaks any `.mcp.json` server's connectivity fails the new CI workflow before merge.

## Cross-links

- **Sibling analysis (root):** `Issues/cross-artifact-divergence-detection-gap/analysis.md` — full systemic capture; remains open.
- **Evidence (incident root cause):** `Issues/cross-artifact-divergence-detection-gap/evidence/mcp-postmortem-2026-05-24/`.
- **Evidence (parallel-scope instance):** `Issues/cross-artifact-divergence-detection-gap/evidence/pv1-spec-vs-templates-divergence.md`.
- **Deferral rows adopted into this same feature:** `Issues/devcontainer-mcp-provisioning-r1-deferrals/register.md` rows H-4 (GitNexus env-var smoke test) and B-1 (CI MCP-list smoke test).
- **Related deferred analysis (separate future run):** `Issues/per-agent-design-evaluation-gap/analysis.md`.
- **Related deferred proposal (separate future run):** `Issues/auditing-family-graduation-review/proposal.md`.

---

*End of proposal. The follow-on proposal for the remaining systemic items will be authored when that feature run is scheduled.*
