---
id: FOLLOW-UPS-devcontainer-mcp-provisioning-r1
doc_type: follow-up-register
status: draft
generated: 2026-05-23
generated_by: orchestrator (parent recipe-feature-pipeline; Phase 5 T5.6 + T5.7 drive)
feature_slug: devcontainer-mcp-provisioning-r1
scope: feature-specific (follow-ups for this feature's deferred items)
mode: report-only
companion_artifacts:
  - working/feature/devcontainer-mcp-provisioning-r1/blueprint-v3.md (§Open Items OI-4..OI-6)
  - Issues/register-devcontainer-mcp-provisioning-r1-deferrals.md
  - Issues/analysis-adr-placement-rootcause.md
  - Issues/analysis-execute-orchestrator-dispatch-limitation.md
  - Issues/proposal-auditing-family-graduation-review.md
---

# Follow-Up Register — `devcontainer-mcp-provisioning-r1`

Concrete follow-up features proposed by this feature run. Each entry names a
trigger event (per `Issues/register-...` §O event-trigger discipline — NO
calendar machinery), the scope, and the rationale.

## FU-1 — `adr-0007-content-review-r1`

**Trigger event**: next time ADR-0007 is touched by any feature (its content,
not just its location). Per the §O posture (no calendar). The Plan §OI-5 +
Blueprint Open Items defer this content review.

**Scope**: review ADR-0007 v2.2.0 content for any drift introduced by:
- The relocation from `adrs-migrated/` to `adrs/` (T1.2 of this feature; the
  relocation itself was mechanical — Git mv preserved content).
- ADR-0038's schema bump (v1.0.0 → v1.1.0 with blast-radius extension) which
  inherits from ADR-0007.
- Any post-relocation drift in cross-references that point at ADR-0007 from
  other ADRs.

**Out of scope**: re-deciding ADR-0007's load-bearing decision (GitNexus
primary / codebase-memory-mcp fallback). That decision stands per ADR-0007
v2.2.0 + this feature's Gate-4 OI-1 closure (fallback not registered, policy
preserved at project level).

**Cross-references**: Blueprint v3 §Open Items OI-5; Plan T1.2 + §OI-5; this
feature's `adrs/ADR-0007-code-graph-mcp-selection.md` (canonical post-T1.2);
ADR-0036 single-canonical-location convention.

## FU-2 — `adr-placement-mechanism-repair-r1`

**Trigger event**: user prioritization. Surfaced by this feature's
deliverable-packager (PKG-BLOCKER-001 at Gate 6; user waived for this
feature).

**Scope**: per `Issues/analysis-adr-placement-rootcause.md` §6 / §9 — repair
the orchestrator / composer / packager so future feature runs honor ADR-0036
single-canonical-location convention. Specifically:
- Update `recipe-feature-pipeline/SKILL.md` to specify ADR placement.
- Update `design-composer.md` to author ADRs at canonical `adrs/`.
- Update `finalize-deliverable-packager.md` to verify ADRs are at canonical
  location.
- Update `shared-document-reviewer.md` DeliverableArchive check to expect
  canonical placement.

**Out of scope**: re-litigating ADR-0036's single-vs-dual-location decision
(that's settled).

**Cross-references**: `Issues/analysis-adr-placement-rootcause.md` (full
diagnosis); ADR-0036.

## FU-3 — `execute-orchestrator-dispatch-mechanism-repair-r1`

**Trigger event**: user prioritization. Surfaced during this feature's
execution-pipeline drive when execute-orchestrator's runtime tool-grant
restricted it from dispatching the 4 specialist sub-agents.

**Scope**: per `Issues/analysis-execute-orchestrator-dispatch-limitation.md`
§6 — investigate whether sub-agent Agent dispatch is supported by the
harness; either fix the agent definitions to assume the limitation OR
re-architect the execution-pipeline to drive from a top-level agent that
DOES have Agent dispatch.

**Cross-references**:
`Issues/analysis-execute-orchestrator-dispatch-limitation.md` (full
diagnosis); the parent-driven workaround used in this feature's Phase 0–5
execution (this run is its evidence).

## FU-4 — `auditing-family-structure-review-r1`

**Trigger event**: user prioritization. Surfaced by this feature's Gate-4
OI-2 disposition (user chose Path A — graduate `auditing-mcp` to its own
family per ADR-0042).

**Scope**: per `Issues/proposal-auditing-family-graduation-review.md` — apply
the graduation rubric (failure-domain distance, blast radius, cross-feature
reuse) to the remaining `auditing-cc-configs` sub-skills and decide which
others should graduate. Likely candidates per the proposal's per-skill
analysis: `auditing-hooks` (medium case), `auditing-github-actions` (already
de-facto separate; formalize), `auditing-codespaces` (when stub is filled).

**Out of scope**: re-evaluating `auditing-mcp`'s graduation (decided in
THIS feature via ADR-0042). Re-evaluating `auditing-cc-configs` as a
coordinator pattern (separate concern; deferred).

**Cross-references**:
`Issues/proposal-auditing-family-graduation-review.md`; ADR-0042;
ADR-0033 (`auditing-codespaces` stub).

## FU-5 — `agent-roster-design-discipline-r1`

**Trigger event**: next time a feature touches the agent surface
(`.claude/agents/*.md`).

**Scope**: per `Issues/analysis-per-agent-design-evaluation-gap.md` §6 +
auto-memory `project_agent_design_gap.md`. Add a demand-driven per-agent
design checkpoint to the feature-pipeline so future features can't ship
without explicitly enumerating which agents they touch / leave untouched
+ why.

**Cross-references**:
`Issues/analysis-per-agent-design-evaluation-gap.md`; this feature's
`agent-roster-impact-matrix.md` (the artifact this future feature would
formalize as canonical).

## Carry-forward open items from THIS feature (not separate follow-up
features; just unresolved tracker entries)

- **Blueprint §OI-4 (per-agent NFR-4 context overhead)** — measured at Plan
  T4.7 / verify-at-execution §OI-4; PASS, no downscoping needed. CLOSED.
- **Blueprint §OI-6 (design-codespaces Serena entry kill criterion)** —
  honored per §O event-trigger discipline; trigger = "when
  auditing-codespaces stub-fill is undertaken" (per ADR-0033). NOT a
  separate follow-up feature; tracked here so its eventual re-evaluator
  knows the entry is forward-looking.
