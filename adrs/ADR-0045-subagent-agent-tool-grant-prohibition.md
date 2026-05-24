---
id: ADR-0045
version: 1.0.0
status: Accepted
generated: 2026-05-23
generated_by: design-composer
supersedes: []
adrs_inherited: [ADR-0019, ADR-0022, ADR-0044]
applies_to:
  - all .claude/agents/*.md sub-agent definitions
  - any future sub-agent authored under this project
  - SA-13 audit scope (sub-agent reasoning-configuration audit under ADR-0022)
template_format: per KB-documentation-criteria ADR template v1.0
change_summary: |
  Establishes a project-wide convention: sub-agents in this project MUST NOT
  declare `Agent` in their `tools:` frontmatter array. Generalizes the
  cleanup applied to execute-orchestrator and execute-finalize-reconciler in
  ADR-0044 into a roster-wide rule. Grounded in Claude Code's documented
  substrate constraint (T-001 — three independent Anthropic primary sources).
  Audit-extension scope to enforce the convention is named but its
  implementation is deferred to a follow-on feature.
---

# ADR-0045: Sub-agents MUST NOT declare `Agent` in their `tools:` frontmatter array

## Contents

Section completion checklist — each box must be checked (including `N/A — out of scope` rows) before this document leaves draft. The reviewer's Gate 0 check uses this list as the structural-presence anchor.

- [x] Status
- [x] Context
- [x] Decision
- [x] Decision Details
- [x] Rationale
- [x] Options Considered
- [x] Consequences
- [x] Architecture Impact
- [x] Implementation Guidance
- [x] Related Information

## Status

Accepted — 2026-05-23.

Authored at the Design Composition stage of the `execute-orchestrator-dispatch-mechanism-repair-r1` feature run, ratifying the per-layer cc-design Q-CC-1 recommendation (option a — author the convention ADR in this feature). The Composer ratifies the divergence from synthesis D-005 (which had recommended deferral to a separate documentation-conventions feature) on the rationale captured in the Decision section.

## Context

Discovery Research T-001 documented a Claude Code substrate constraint: **sub-agents cannot dispatch other sub-agents at runtime, even when `Agent` is declared in the `tools:` frontmatter array.** Three independent Anthropic-controlled primary sources establish this as deliberate architectural design (not an oversight, not a flag-toggle), with the second source providing the direct developer instruction: "Don't include Agent in a subagent's tools array."

The FR-5 inventory sweep (codebase-analysis.json `fr5_inventory_sweep`) enumerated all 36 sub-agent files under `.claude/agents/*.md` and found exactly two that declare `Agent` in `tools:`:

1. `execute-orchestrator` (`tools: [Read, Glob, Grep, Write, Bash(python3:*), Agent, TaskUpdate]`)
2. `execute-finalize-reconciler` (`tools: [Read, Glob, Grep, Write, Agent]`)

Both are dispatcher sub-agents whose dispatch is materially broken by the substrate constraint. ADR-0044 ratifies the per-feature cleanup: both `Agent` declarations are removed under the §6 option (a) design pathway, in a bundled commit, with the commit message documenting "FR-5 sweep closure: affected set = 2."

The remaining 34 sub-agents do not currently declare `Agent`. The convention this ADR captures is therefore a **forward-looking guardrail**, not a retroactive cleanup: it prevents a future sub-agent author from re-introducing the misleading runtime no-op.

Synthesis §3.5 (D-005) recommended deferring this convention to a separate documentation-conventions feature on RICE grounds (RICE=0.625; scope-creep risk; user-memory preference for "belongs in a separate feature"). The per-layer cc-design Q-CC-1 surfaced a counter-recommendation (option a — author in this feature) on three grounds the Composer ratifies:

- T-001's three-source citation work is already done in this feature.
- The D-003 cleanup of both `Agent`-declaring sub-agents is already shipped in this feature.
- A deferral feature would re-incur T-001's source-citation work and would re-litigate the cleanup precedent.

The reviewer's `shared-document-reviewer` evaluation (cc-design-review-issues.json I-DR-003) flagged the divergence as "well-rationalized — Composer's call." The Composer ratifies option (a).

## Decision

**Sub-agents in this project MUST NOT declare `Agent` in their `tools:` frontmatter array.** Authors of new sub-agents and reviewers of existing sub-agents enforce this rule. The two pre-existing violations (`execute-orchestrator` and `execute-finalize-reconciler`) are cleaned up under ADR-0044's option (a) implementation.

Three accompanying clarifications:

- **`TaskCreate` and `TaskUpdate` are out of scope.** These are Claude Code's built-in agent-task-tracking primitives, semantically distinct from the `Agent` dispatch tool. They remain declarable in sub-agent `tools:` arrays subject to ADR-0022 audit.
- **The parent orchestrator skill (e.g., `recipe-feature-pipeline/SKILL.md`) and the main-conversation orchestrator are NOT sub-agents.** The convention applies only to files under `.claude/agents/*.md`. Main-conversation dispatch of sub-agents via `Agent` is supported per T-001 Finding F-1 and is not constrained by this convention.
- **The convention applies to all future feature runs without grandfathering exceptions.** If a future Claude Code harness update changes the substrate constraint, this ADR is reconsidered (see kill criteria below).

## Decision Details

| Item | Content |
|---|---|
| Decision | Sub-agents in this project MUST NOT declare `Agent` in their `tools:` frontmatter array. |
| Why now | T-001's three-source evidence base and the ADR-0044 cleanup of the two violations are both shipped in this feature. Deferring the convention re-incurs the citation work and re-litigates the cleanup precedent. |
| Why this | The substrate constraint is documented Claude Code design ("Subagents cannot spawn other subagents"). Declaring `Agent` in a sub-agent's `tools:` array is a misleading runtime no-op — the YAML parses, the agent loads, the runtime grant is silently absent. Forward-looking prohibition is the lowest-cost guardrail. |
| Known unknowns | The audit-extension scope (whether SA-13's check under ADR-0022 is extended to enforce this, or whether a new audit rule family is added) is named but not implemented in this feature. The audit-extension feature scope is deferred. |
| Kill criteria | If a future Claude Code harness update enables true sub-agent → sub-agent dispatch (i.e., `Agent` in a sub-agent's `tools:` becomes operational at runtime), this ADR is reconsidered — possibly with a per-sub-agent opt-in for the new affordance rather than a global lift of the prohibition. |

## Rationale

The convention reflects a documented substrate constraint, not a project preference. T-001's executive summary names the constraint as a deliberate architectural design choice with three corroborating Anthropic-controlled primary sources:

1. https://code.claude.com/docs/en/sub-agents — "Subagents cannot spawn other subagents." (5 words verbatim)
2. https://code.claude.com/docs/en/agent-sdk/subagents — "Subagents cannot spawn their own subagents. Don't include Agent in a subagent's tools array." (14 words verbatim)
3. https://github.com/anthropics/claude-code/issues/29677 — corroborates the v2.1.63 Task → Agent rename date.

Source 2 is the direct developer instruction. This convention captures that instruction as a project-level commitment so future sub-agent authors do not re-litigate it. The user-memory preference cited in synthesis D-005 ("belongs in a separate feature") is honored in spirit (this ADR is small, scoped, and does NOT bundle a broader sub-agent governance overhaul) but inverted in letter (this ADR ships in the present feature rather than a follow-on) because the evidence base and cleanup precedent are both already present in this run.

The convention is forward-looking. Existing sub-agents that currently honor the rule require no change. The two violations are cleaned up under ADR-0044. The audit-extension scope (a SA-13-style automated check that scans every sub-agent's `tools:` for `Agent`) is named here for traceability and is left to a follow-on feature to implement; manual review enforces the convention in the interim.

## Options Considered

### Option 1: Defer convention to a separate documentation-conventions feature (synthesis D-005 — rejected here)

**Pros:**
- Honors user-memory preference literally ("belongs in a separate feature").
- Keeps this feature's ADR count to one (ADR-0044 only) and avoids scope-creep risk.
- The cleanup precedent in ADR-0044 stands without requiring a roster-wide rule.

**Cons:**
- The follow-on feature re-runs T-001's three-source citation work (verifying the URLs and quotes are still live; framing the substrate constraint).
- The cleanup precedent in ADR-0044 is implicit ("this feature removed two violations") without a project-wide guardrail that future violations would also be removed.
- Increases the chance of a future sub-agent author adding `Agent` to `tools:` without the documented prohibition to cite against.

### Option 2: Capture as a non-ADR constraint statement in the Blueprint or in a contributor doc (synthesis Q-CC-1 option c — rejected)

**Pros:**
- Lighter-weight than an ADR.
- Still captures the rule somewhere readable.

**Cons:**
- Project-wide conventions belong in ADRs per the ADR-0011 / ADR-0019 / ADR-0031 / ADR-0032 precedents (every cross-feature convention in this project has its own ADR).
- A constraint statement in a Blueprint is feature-scoped; the Blueprint can be archived or superseded, leaving the convention adrift.
- A contributor doc lacks the audit-discoverability of an ADR.

### Option 3 (Selected): Author the convention ADR in this feature (cc-design Q-CC-1 option a)

**Pros:**
- T-001's three-source citation work is already done.
- The ADR-0044 cleanup is already in this run; the convention codifies the rule the cleanup honored.
- Avoids re-incurring source-citation work in a follow-on feature.
- Aligns with project ADR-discipline precedents (cross-feature conventions get their own ADR).
- Forward-looking guardrail prevents future re-introduction of the violation pattern.

**Cons:**
- The audit-extension implementation is named but deferred — the convention is enforced by manual review until the audit lands.
- Adds a second ADR to the feature; the cc-design Q-CC-1 framing acknowledged this as a Composer judgment call.
- The reviewer flagged the divergence from synthesis D-005 as "well-rationalized — Composer's call" (I-DR-003), implying the option was non-obvious but defensible.

## Consequences

### Positive Consequences

- **Forward-looking guardrail** captured at ADR scope — discoverable by future sub-agent authors and by audit tooling.
- **T-001 citation work is preserved** as a stable reference inside the ADR rather than as ephemeral synthesis content.
- **ADR-0044 cleanup is generalized** into a roster-wide rule, closing the FR-5 inventory question for future runs.
- **Audit-extension scope is named** so a follow-on feature can pick up the implementation without re-discovering the rule.

### Negative Consequences

- The convention is enforced manually until the audit-extension feature lands. Future sub-agent authors may still introduce `Agent` declarations until then; manual reviewer attention catches them.
- This ADR adds to the project's ADR count; readers must now consult ADR-0044 (the cleanup) and ADR-0045 (the convention) together for the full picture.

### Neutral Consequences

- The 34 sub-agents that currently honor the rule require no change.
- No frontmatter schema changes; the rule constrains the values, not the structure.
- The audit-extension scope is at SA-13's discretion (extension of the existing reasoning-config audit) or as a new audit rule family — deferred.

## Architecture Impact

### Components that change

- This ADR is authored at `adrs/ADR-0045-subagent-agent-tool-grant-prohibition.md` per ADR-0036 single-location convention.
- No other file is modified by this ADR. ADR-0044 captures the cleanup of the two pre-existing violations.

### New dependencies introduced

None at the runtime level. One forward dependency: a follow-on feature that extends SA-13 (or authors a new audit rule family) to enforce this convention automatically.

### Architectural constraints added

- Project-wide rule: no sub-agent file under `.claude/agents/*.md` declares `Agent` in `tools:`.
- The rule does NOT apply to `TaskCreate` / `TaskUpdate` (out of scope).
- The rule does NOT apply to the main-conversation orchestrator or to parent skills (those are not sub-agent files).

### Architectural constraints removed

None.

### Layers affected (9-layer taxonomy)

- **Claude Code / Project Filesystem** — sole affected layer.
- All other layers — N/A — out of scope.

## Implementation Guidance

Principled direction only — procedures live in the Blueprint and Plan.

- **For sub-agent authors:** when authoring a new file under `.claude/agents/*.md`, the `tools:` array MUST NOT include `Agent`. If the agent's responsibility requires dispatching another sub-agent, the dispatch happens at the main-conversation level (parent skill or main orchestrator), and the new agent emits a `dispatch_directives[]`-style structured hand-off (the pattern ADR-0044 establishes for `execute-finalize-reconciler`).
- **For reviewers:** when reviewing any new or modified sub-agent file under `.claude/agents/*.md`, verify the `tools:` array does not include `Agent`. If it does, flag as a critical issue citing this ADR.
- **For the audit-extension follow-on feature:** the recommended approach is to extend SA-13 (under ADR-0022's reasoning-configuration audit) with a new check that greps every `.claude/agents/*.md` frontmatter `tools:` array for the literal `Agent` token. Output: BLOCKER finding per match. Alternative: author a new audit rule family `auditing-cc-tool-grants` if SA-13's scope is judged orthogonal to the new check.
- **For Claude Code harness updates:** if a future release enables sub-agent → sub-agent dispatch (verifiable via T-001-style probe), this ADR is reconsidered. Reconsideration includes the possibility of per-sub-agent opt-in for the new affordance rather than a global lift of the prohibition.

## Related Information

### Related ADRs

- **ADR-0019** — sub-agent naming convention. Inherited; preserved.
- **ADR-0022** — sub-agent reasoning configuration is intentional and audited. The audit-extension scope this ADR names slots into the ADR-0022 framework or sits alongside it.
- **ADR-0036** — single-location ADR placement. This ADR lives only at `adrs/ADR-0045-subagent-agent-tool-grant-prohibition.md`.
- **ADR-0044** — flatten execution-phase dispatch hierarchy. Cleans up the two pre-existing violations; this ADR codifies the forward-looking convention.

### Referenced specs and files

- `working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/research-notes/T-001-claude-code-subagent-tool-grant-semantics.md` — anchor evidence with three Anthropic-controlled primary sources.
- `working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/codebase-analysis.json` § `fr5_inventory_sweep` — affected-set enumeration (closed at 2).
- `working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/cc-design.md` § Q-CC-1 — Designer's recommendation to author the convention ADR in this feature.
- `working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/synthesis.md` § D-005 — the deferral recommendation this ADR explicitly diverges from (Composer ratification).
- `working/feature/execute-orchestrator-dispatch-mechanism-repair-r1/cc-design-review-issues.json` § I-DR-003 — reviewer's "well-rationalized — Composer's call" assessment.

### Related KBs

- `KB-cc-platform` — Claude Code primitive surface, including the sub-agent definition syntax.
- `KB-cc-design` — per-layer design discipline, Principle 1 (lowest-cost primitive), Principle 9 (sub-agent reasoning configuration).
