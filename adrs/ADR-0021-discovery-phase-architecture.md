---
id: ADR-0021
version: 1.0.0
status: Accepted
generated: 2026-05-19
generated_by: finalize-reconciler (v4.3.0 production session)
supersedes: []
adrs_inherited:
  - ADR-0006 (synthesis inlined — discovery output feeds the inlined synthesis pipeline at Stage 4)
  - ADR-0007 v2.0.0 (GitNexus primary, codebase-memory-mcp fallback — discovery-codebase-researcher uses these)
  - ADR-0009 (rationale brief 3-layer enforcement — discovery-plan-author receives rationale brief listing KBs and ADRs to consult)
  - ADR-0018 (codebase-analysis JSON schema — discovery-codebase-researcher produces this)
  - ADR-0019 (naming convention — uses the discovery- prefix)
  - ADR-0020 (KB structure — discovery-plan-author consults the KBs defined here)
applies_to:
  - feature-pipeline blueprint v4.3.0
  - Stage 2 (discovery-plan-author)
  - Stage 3 (discovery-codebase-researcher + discovery-external-researcher fan-out)
template_format: per ADR.txt v1.0
---

# ADR-0021: Discovery phase architecture — KB+ADR consultation, conditional external research, fan-out execution

## Status

Accepted — 2026-05-19

## Context

In blueprint v4.2 and prior, the "research" phase (Stages 2 and 3) was described topologically but its substantive architecture was hand-waved:

- Stage 2 had a single sub-agent (`synth-research-planner`, renamed `discovery-plan-author` per ADR-0019) whose output was "a research plan." The plan's content structure was not specified beyond "topics to research."
- Stage 3 had `synth-researcher` (renamed `discovery-external-researcher`) shown as `×N up to 6 in parallel` and `synth-codebase-researcher` (renamed `discovery-codebase-researcher`). The fan-out was implied but its semantics were not specified — how is N determined? Are the external researchers specialized per domain or generic? What if the research plan needs zero external research?
- The plan author received only the PRD as input. It had no explicit mandate to consult existing KBs or existing ADRs. This omission meant the plan author could (and did, in practice through round 1-3 sessions) propose external research on topics that were already covered by existing KBs, wasting tool calls and session budget.

The user (Q-v4.3-discovery) clarified the architecture in three substantive ways:

(1) "Research is not a phase. Discovery is a phase." The phase encompasses BOTH plan-authoring AND execution, with the plan-authoring step itself being a meaningful discovery activity (discovering what we already know via KBs and ADRs, then discovering what we don't know via external/internal research).

(2) The plan author MUST consult existing KBs to decide if external research is warranted at all, AND MUST consult existing ADRs to prevent the plan from proposing research that would conflict with already-made architectural decisions.

(3) Stage 3 execution is a fan-out strategy. The external researcher is `generic-with-N-invocations` (a single sub-agent template invoked N times in parallel, one invocation per research topic) rather than N specialized per-domain researchers. This was explicitly chosen over the specialized alternative for flexibility.

## Decision

Refactor the discovery phase architecture across three commitments:

### Commitment 1 — Stage 2 input contract requires KB+ADR consultation

`discovery-plan-author`'s input prompt (the rationale brief per ADR-0009) MUST include:
- Path to the approved PRD (existing).
- **Paths to all KBs in scope for the feature's Layer Scope** (new — orchestrator computes this from `00-feature-scope.json` Layer Scope flags + ADR-0020's KB inventory).
- **Paths to all existing ADRs in the working ADR set** (new — orchestrator passes `adrs/` directory contents).

The sub-agent MUST:
- Inventory existing KBs that touch the feature's open questions.
- Inventory existing ADRs that constrain the feature's design space or that might conflict with research-driven proposals.
- Identify **KB-gaps** — areas where existing KBs DO NOT already answer the open questions. KB-gaps drive external research scope.
- Identify **ADR-conflicts** — areas where research could yield findings that contradict an accepted ADR. The plan flags these as "research-with-conflict-awareness" topics, requiring the synthesizer to either reconcile or escalate.

### Commitment 2 — External research is conditional

If KB-gap analysis shows existing KBs already address all open questions in the PRD AND no ADR-conflict-warranting topics remain, the Research Plan declares `external_research: skipped` with explicit per-question rationale citing the answering KB. Stage 3 in this case invokes ONLY `discovery-codebase-researcher`. This eliminates wasted external-research tool-call budget on topics the pipeline already understands.

### Commitment 3 — Stage 3 fan-out semantics are explicit

Stage 3 has the following topology:

```
                   [Research Plan]
                          │
                          ▼
              ┌───────────┴───────────┐
              │                       │
              ▼                       ▼  (fan-out)
   [discovery-codebase-          [discovery-external-
    researcher × 1]               researcher × N]
              │                       │
              └───────────┬───────────┘
                          ▼
                  [Stage 4: Synthesis]
```

- **Always-invoked**: `discovery-codebase-researcher` × 1. Always runs; the codebase is always the implicit internal substrate even when external research is skipped. Produces `03-codebase-analysis.json` + sibling markdown.
- **Conditionally-invoked**: `discovery-external-researcher` × N. N is the number of external topics declared in `02-research-plan.md` (zero when external research is skipped; ≤6 per the ADR-0006 invocation-budget cap; batched sequentially if the plan declares >6 topics).
- **Generic-with-N-invocations pattern** (chosen over specialized researchers per the user): a single sub-agent template named `discovery-external-researcher` is invoked once per topic in parallel. Each invocation receives:
  - One research topic from the plan's topics list.
  - One tool selection (web_search / Context7 / Microsoft Learn / vendor docs / specifications site).
  - The rationale brief.
  And produces one research findings file `03-research-findings-N.md`.

## Decision Details

| Item | Content |
|---|---|
| Decision | Discovery phase becomes a substantive 2-stage architecture (plan → execute) with explicit KB+ADR consultation, conditional external research, and generic-fan-out execution. Stage 2 produces a Research Plan with declared internal/external scope, tool-per-topic selection, KB-gap rationale, and ADR-conflict notes. Stage 3 always runs codebase analysis once; runs external research zero-to-N times per plan declaration. |
| Why now | The pipeline's discovery phase was the least-specified part of v4.2's architecture and the part most likely to waste session budget if left under-specified. v4.3 surfaces the architecture before Phase 2 implementation. |
| Why generic-with-N-invocations | The user explicitly chose this over N specialized researchers. Rationale: (a) flexibility — adding a new research domain doesn't require a new sub-agent definition, just a new tool selection; (b) reusability — the same generic researcher can use web_search for one topic and Context7 for another; (c) simpler orchestrator code path — orchestrator dispatches the same agent N times rather than dispatching N different agents; (d) easier to add new MCP tools — a new MCP just becomes a new tool-selection option, not a new sub-agent. The cost is that the generic researcher must be prompted with tool-selection guidance per invocation; this is a minor prompt-design cost. |
| Why KB+ADR consultation upfront | Without it, the plan author proposes research on already-answered questions (wasting budget) or proposes architecturally-conflicting decisions (causing rework downstream). Upfront consultation is cheaper than downstream reconciliation. |
| Known unknowns | (a) Whether KB-gap analysis can be done reliably without false-positives (declaring a gap that the KB actually covers in a subsection the analyzer didn't read). Mitigation: shared-document-reviewer's Gate 0 review of `02-research-plan.md` validates KB-gap rationale against actual KB content. (b) Whether the ≤6 parallel cap is the right bound; future load tests may suggest 4 or 8. |
| Kill criteria | If 3+ feature runs produce Research Plans where ≥30% of declared external research topics are later re-classified as KB-already-covered (post-hoc), the KB-gap analysis is unreliable and a separate KB-gap-analyzer sub-agent should be introduced via follow-up ADR. |

## Rationale

**KB+ADR consultation is the "what do we already know" loop.** Discovery is fundamentally about gap-filling: figure out what's known (KBs + ADRs), then figure out what's not (codebase + external). Skipping the "what's known" step means the gap-filling step proposes work that's already done.

**Conditional external research saves budget.** A typical feature spans 2-4 layers. If existing KBs cover those layers' design discipline and existing ADRs cover platform-mechanic decisions, the feature may need only codebase research (e.g., a feature like "add user.last_login_at field and display it on the profile page" needs no external research — only codebase analysis to find the existing User schema, profile-page component, and migration patterns). External research is for novel-to-the-pipeline topics, not for topics the pipeline already handles.

**Generic-with-N-invocations matches research-as-execution semantics.** A research topic is a unit of work: "find me what X is and how it works." The unit is the same shape regardless of topic — input is a research question + tool, output is a findings document. Specializing researchers per domain would impose a taxonomy on research topics (web research vs vendor docs vs specifications) that doesn't match how a research plan is actually structured (one topic might span multiple domains; one researcher per topic is cleaner than splitting one topic across multiple specialized researchers).

**Plan-then-execute matches discoverability.** The plan author can be loaded with KBs and ADRs to make scope decisions; the execution researchers don't need that load. Separating planning from execution lets each sub-agent's context window focus on its actual work.

## Consequences

### Positive

- Wasted external-research tool calls eliminated when KBs cover the questions.
- ADR conflicts surfaced at plan-time, not at synthesis-time.
- Stage 3 fan-out semantics are explicit (1 codebase + N external in parallel, ≤6 parallel cap, batched if >6).
- Generic researcher pattern is extensible (new MCP tools = new tool-selection options).
- Plan-author's context contains decision-relevant KBs/ADRs; researcher context is minimal.

### Negative

- discovery-plan-author's rationale brief grows (must list KB paths + ADR paths in scope). For a feature spanning all 9 layers, this could be ~20+ paths. Mitigation: paths are lightweight; sub-agent uses Read tool to load on-demand.
- KB-gap analysis is a judgment call; false-positives possible (declaring a gap that KB covers in a section the analyzer missed). Mitigated by shared-document-reviewer's review of the Research Plan.
- Generic researcher's prompt design carries the per-topic tool-selection guidance; this is a one-time prompt-engineering cost.

### Neutral

- The architecture change is visible at the topology level (Stage 3 now has explicit fan-out semantics rather than implied) and at the input-contract level (Stage 2 now requires KB+ADR consultation rather than just PRD).

## Implementation Guidance

- discovery-plan-author MUST emit `02-research-plan.md` conforming to a structure with sections:
  - **Open Questions** (from PRD)
  - **Existing KBs Consulted** (paths + which questions each addresses)
  - **Existing ADRs Consulted** (paths + which questions each constrains)
  - **KB Gaps** (questions not addressed by existing KBs)
  - **ADR Conflicts** (questions where research may yield ADR-conflicting findings)
  - **Internal Research Scope** (always non-empty — codebase analysis topics)
  - **External Research Scope** (may be `skipped` with rationale; otherwise lists topics with per-topic tool selection)
  - **Tool Selection Rationale** (per external topic, why this tool was chosen)
- The Research Plan template is added to KB-documentation-criteria per ADR-0020 (which absorbs the planning discipline).
- shared-document-reviewer's Gate 0 / Gate 1 review of the Research Plan validates KB-gap rationale against KB content (uses Read tool to spot-check claimed gaps).
- Stage 3 fan-out is orchestrator-coordinated:
  - Orchestrator reads `02-research-plan.md`.
  - If `external_research: skipped`, orchestrator invokes ONLY discovery-codebase-researcher.
  - Else, orchestrator dispatches discovery-codebase-researcher + N × discovery-external-researcher in parallel (N ≤ 6; batched if N > 6).
  - Each external researcher invocation gets exactly one topic + one tool selection in its prompt.
- Stage 3 outputs aggregated by orchestrator and passed to Stage 4 synthesis as a bundle (one codebase analysis JSON + N research findings markdowns).

## Related Decisions

- ADR-0006 (synthesis inlined) — discovery outputs feed Stage 4's inlined synthesis pipeline.
- ADR-0007 v2.0.0 (GitNexus / codebase-memory-mcp) — discovery-codebase-researcher uses these MCPs.
- ADR-0009 (rationale brief 3-layer) — discovery-plan-author's rationale brief gets the KB+ADR paths under "Inputs to consult" section.
- ADR-0017 (document-reviewer) — shared-document-reviewer reviews `02-research-plan.md` at Stage 2 (extends the review-points list; tracked separately if needed).
- ADR-0018 (codebase-analysis schema) — discovery-codebase-researcher's output schema, unchanged here.
- ADR-0019 (naming convention) — provides the discovery- prefix.
- ADR-0020 (KB structure) — defines the KBs that discovery-plan-author consults.

## Open Questions

- Should shared-document-reviewer be invoked at Stage 2 (after Research Plan production) as a 6th review point? Currently v4.3 has 5 review points (after Intent Clarification, PRD, Blueprint, Plan, and per-ADR). Adding Research Plan would make 6. Deferred to a follow-up ADR if the practical experience shows the Research Plan needs Gate 0 review beyond just the user's approval gate. Initial v4.3 ships without it; the user's Research Plan Approval Gate is the only review.
- What happens if the codebase-researcher discovers facts that contradict the Research Plan's KB-gap analysis? Currently the synthesizer handles contradiction at Stage 4 (per ADR-0006). A future ADR may introduce a feedback loop from Stage 3 back to Stage 2 for plan revision.
