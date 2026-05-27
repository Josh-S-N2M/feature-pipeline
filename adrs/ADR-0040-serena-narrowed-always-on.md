---
id: ADR-0040
version: 1.0.1
status: Accepted
generated: 2026-05-23
generated_by: design-composer
supersedes: []
adrs_inherited: [ADR-0007]
applies_to:
  - devcontainer-mcp-provisioning-r1
  - the project-scoped .mcp.json Serena registration
template_format: per KB-documentation-criteria ADR template v1.0
change_summary: >-
  Codifies the Serena MCP posture (UI-8): registered always-on at project scope
  in .mcp.json, but mcp__serena__* tool entries restricted to the agents that
  actually touch Python audit-script surface (review-architecture-auditor +
  audit-script-touching design agents). Pinned pre-v1.3.0 pending
  base_modes→added_modes review. Resolves D-0013 (narrowed-always-on) per
  Q-CC-8 ADR candidate #4.
---

# ADR-0040: Serena MCP — narrowed always-on; Python-audit-surface allowlist; pinned pre-v1.3.0

## Contents

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

Accepted — 2026-05-23

## Context

PRD v3 narrows UI-8 to a single question: with GitNexus explicitly filling the code-graph-traversal slot per ADR-0007 v2.2.0, what is Serena's symbol-level value on a markdown-heavy repo? The codebase analysis (claims C-0484 / C-0485, single-sourced-medium) records the repo composition as 468 markdown / 634 non-git non-node_modules = **73.8% markdown**. Symbol density concentrates in the **52 Python audit scripts** (C-0490 verified). Serena's LSP-symbol value-prop is narrow but non-zero on this corpus.

Synthesis D-0013 (architectural, two-way reversible, blast-radius=tenant, but the coupling to D-0009 agent-allowlist mapping amplifies rework cost) frames this as ADR-worthy (synthesis §7 ADR candidate #4). Per FR-5, the design-composer authors.

Per-layer Design surfaced two coupled questions:
- **Q-CC-3:** the exact agent list for the Serena-narrowed allowlist (row 7 of the per-agent table is TBD).
- **I-DR-002 (important):** the TBD row blocks plan-author from generating the per-agent edit instructions.

The Q4 PRD Product Policy decision ("all seven always-on at project scope") forecloses "drop Serena entirely from .mcp.json." The remaining choice is between full-always-on (every agent gets `mcp__serena__*`) and narrowed-always-on (project-scoped registration but per-agent allowlist restricted to the Python-audit-surface).

A second coupling exists: Serena v1.3.0 introduces a breaking change (`base_modes` → `added_modes` per E-0098 / claim C-0036, C-0041). Pinning pre-v1.3.0 is required until the project reviews and adapts.

## Decision

1. **Serena is registered always-on at project scope** in `.mcp.json` (honoring Q4 PRD Product Policy: all seven always-on).
2. **`mcp__serena__*` tool entries are narrowed** in the per-agent `tools:` allowlists to **exactly the agents whose role touches Python audit-script surface**:
   - `review-architecture-auditor` (already in the consumer-mapping for GitNexus/codebase-memory-mcp; touches audit-scripts via blast-radius analysis).
   - **The design agents that touch `.claude/skills/auditing-*/scripts/` Python files**, namely: `design-cc` (this layer's per-feature owner — may edit `auditing-mcp/scripts/`), `design-cicd` (may touch `auditing-github-actions/scripts/`), `design-codespaces` (may touch `auditing-codespaces/scripts/` if/when the stub becomes real per ADR-0033).
   - `discovery-codebase-researcher` MAY receive Serena tools when its symbol-level operations on Python audit scripts add value during research (composer-decision: include it; the 52-Python-audit-script surface is the same surface this agent operates against during research).
   - **The exact final list is 5 agents:** `review-architecture-auditor`, `design-cc`, `design-cicd`, `design-codespaces`, `discovery-codebase-researcher`. This resolves I-DR-002 and Q-CC-3 with a concrete-default-overridable list.
3. **All other 31 agents** (of 36 total) receive ZERO `mcp__serena__*` entries. The C-0445 zero-`mcp__` invariant is preserved for non-consumers per KB-cc-design Principle 5 (one source of truth) and per the broader Serena-narrowing principle.
4. **Serena is pinned to a tag strictly before v1.3.0** (the exact tag is verify-at-execution per synthesis D-0011 — operator selects the latest sub-v1.3.0 stable at install time). The pin is recorded in `.devcontainer/versions.env` as `SERENA_TAG=<pre-v1.3.0-tag>`. A separate follow-up feature reviews `base_modes`→`added_modes` and may then bump.
5. **`auditing-mcp` augmentation rule OP-8 (GitNexus-specific) extends** to also audit the Serena allowlist: confirm `mcp__serena__*` appears in exactly the five named agent files and zero others. (This is OP-2 / OP-3 in the augmented `auditing-mcp` per cc-design.)

## Decision Details

| Item | Content |
|---|---|
| Decision | Serena registered always-on at project scope; per-agent `mcp__serena__*` allowlist restricted to 5 named agents covering the 52-Python-audit-script surface; pinned pre-v1.3.0. |
| Why now | The PRD UI-8 narrows the question; D-0013 surfaces it; plan-author cannot proceed without the concrete agent list (I-DR-002). |
| Why this | The 5-agent list is the smallest superset that covers every Python-touching agent identified in the codebase analysis (52 Python audit scripts; the listed agents are the ones that read/write them). Broader allowlist violates least-privilege; narrower drops `review-architecture-auditor`'s blast-radius work or `discovery-codebase-researcher`'s symbol-level research. Pinning pre-v1.3.0 honors the verified breaking change without forcing a same-feature migration. |
| Known unknowns | (a) Whether `design-iac` and `design-api` also occasionally touch audit-script Python (no current evidence; if true, they would be added in a follow-up — easy additive change). (b) Whether the Serena symbol-level operations on a markdown-heavy corpus produce *enough* value to warrant the augmented `auditing-mcp` audit cost; this is a felt-utility metric to revisit post-ship. |
| Kill criteria | If Serena fires no tool invocations across the five named agents for >90 days post-ship, downscope to `drop_from_always_on` (a future ADR would supersede this one). The kill criterion is utility-driven, not cost-driven; the always-on context cost is minimal because MCP tool schemas are deferred until invoked (cc-design Principle 1). |

## Rationale

Synthesis D-0013 recommended `narrowed_always_on_python_audit_surface_only` as the only option that honors three constraints simultaneously: (a) Q4 PRD policy preserves always-on; (b) the 73.8% markdown corpus means full-always-on is wasted scope; (c) GitNexus filling the code-graph slot means Serena's *unique* value-prop is symbol-level operations on the 52 Python audit scripts — and that surface is where Serena pays.

The agent list selection follows the codebase analysis evidence:
- `review-architecture-auditor` reads audit-script outputs during blast-radius analysis (C-0447 / KB-codebase-research evidence).
- The three `design-*` agents listed are the only design agents whose `.claude/agents/*.md` body or `skills:` array references the `auditing-<topic>` skill family (design-cc references `auditing-cc-configs`; design-cicd references `auditing-github-actions`; design-codespaces references `auditing-codespaces`).
- `discovery-codebase-researcher` is added because it operates against the same Python audit-script surface during research (Q-CC-3 candidate list explicitly named).

Pinning pre-v1.3.0 follows the synthesis D-0011 per-server pin table and E-0098 (Serena v1.3.0 base_modes→added_modes breaking change verified).

## Options Considered

### Option 1: Narrowed always-on; Python-audit-surface allowlist (selected)

**Pros:** Honors least-privilege; respects the 73.8% markdown corpus; gives Serena's symbol-level value-prop a real audience without spraying tools across 36 agents.

**Cons:** Requires the augmented `auditing-mcp` to maintain the 5-agent list; agent-list changes require an audit-rule update.

### Option 2: Full always-on (every agent gets `mcp__serena__*`)

**Pros:** No allowlist-list maintenance; uniform.

**Cons:** Violates least-privilege; 31 of 36 agents inherit Serena's blast-radius (including the v1.3.0 breaking-change surface) for zero value. Breaks the C-0445 zero-`mcp__` invariant unnecessarily.

### Option 3: Drop Serena from .mcp.json

**Pros:** Eliminates the v1.3.0 risk; reduces always-on count from 7 to 6.

**Cons:** Forecloses by Q4 PRD Product Policy ("all seven always-on"). Would require a PRD amendment. Loses the symbol-level value-prop on the 52 Python audit scripts.

### Option 4: Scope Serena to downstream feature-codebase runs only (per-feature overlay .mcp.json)

**Pros:** Aligns Serena's activation with markdown-light feature codebases.

**Cons:** Project does not currently have per-feature overlay .mcp.json conventions. Inventing one for one server is disproportionate.

## Consequences

### Positive Consequences

- Five agents gain Serena's symbol-level operations; the others remain at zero `mcp__` entries (C-0445 invariant preserved for 31 of 36).
- Allowlist drift is auditable: rule OP-2 (consumer-mapping validation) + OP-3 (zero-`mcp__` preservation for non-consumers) covers the entire 36-agent surface.
- The v1.3.0 breaking-change risk is bounded; pin discipline lives in `.devcontainer/versions.env`.

### Negative Consequences

- The 5-agent list is a maintenance surface; if a new agent needs Serena, the list (and the audit rule) update in lockstep.
- The "Python audit-script surface" definition is operational — if the project's audit-script footprint changes substantially, this ADR may need revisiting.

### Neutral Consequences

- The .mcp.json `mcpServers.serena` entry shape is unaffected by the allowlist narrowing; the narrowing lives entirely in the agent-file `tools:` arrays.
- The pin discipline matches the broader per-server pin table (synthesis D-0011); no Serena-specific pin convention is introduced.

## Architecture Impact

1. **Layers affected.** Claude Code / Project Filesystem (the agent-file edits; the `auditing-mcp` rules); Dev Environment / Codespaces (the postCreate install uses the SERENA_TAG pin).
2. **Components that change.**
   - `.claude/agents/review-architecture-auditor.md` — add `mcp__serena__*` to `tools:`.
   - `.claude/agents/design-claude-code.md` — add `mcp__serena__*` to `tools:`. (Note: filename is `design-claude-code.md`; the agent's frontmatter `name:` is `design-cc` per Path-A reserved-word workaround.)
   - `.claude/agents/design-cicd.md` — add `mcp__serena__*` to `tools:`.
   - `.claude/agents/design-codespaces.md` — add `mcp__serena__*` to `tools:`.
   - `.claude/agents/discovery-codebase-researcher.md` — add `mcp__serena__*` to `tools:` (alongside the GitNexus + codebase-memory-mcp entries).
   - `.devcontainer/versions.env` — declare `SERENA_TAG=<pre-v1.3.0-tag>`.
   - `auditing-mcp` augmentation rules OP-2 / OP-3 — list extension to include `mcp__serena__*` consumers.
3. **New dependencies introduced.** None at the runtime level.
4. **Architectural constraints added.** The Python-audit-surface allowlist (5 agents) is the only set of agents that may carry `mcp__serena__*`. Any addition requires an ADR update or an additive amendment.

## Implementation Guidance

**Concrete agent list (canonical):**
1. `review-architecture-auditor`
2. `design-cc`
3. `design-cicd`
4. `design-codespaces`
5. `discovery-codebase-researcher`

These five files get `mcp__serena__*` added to their `tools:` arrays. The other 31 agents (of 36) do not.

**Pin form.** `SERENA_TAG` in `.devcontainer/versions.env`. The exact tag is verify-at-execution: select the latest tagged release strictly below v1.3.0 at install time. If no such release exists at execution, fall back to commit-SHA pinning of the last commit before the v1.3.0 release-tag.

**Migration path post-v1.3.0.** A separate follow-up feature reviews `base_modes`→`added_modes` and (if the change is benign for this project's usage) bumps the pin and supersedes this ADR with a new one specifying the v1.3.0+ migration.

**No procedural detail in the ADR.** Sequencing of the five agent-file edits + the `versions.env` declaration + the audit-rule update lives in the Plan.

## Related Information

- Related ADRs: ADR-0007 (GitNexus primary / codebase-memory-mcp fallback; Serena fills a distinct slot), ADR-0037 (mcp-events.jsonl event surface — Serena failures emit `structured_failure` records too), ADR-0039 (credential redaction — Serena has no credentials so this ADR is unaffected).
- Referenced specs / docs: synthesis.md §3 D-0013, §4 per-server matrix Serena row, §7 ADR candidate #4; cc-design.md Subagent patterns (UI-15 + Serena narrowing); PRD UI-8 narrowed-in-v3.
- Issues / PRs: I-DR-002 (TBD agent row — resolved here), Q-CC-3 (exact agent list — resolved here), I-DR-CS-004 (codebase-memory-mcp probe coverage — independent; resolved in Blueprint inventory dispositioning).
- Related KBs: KB-mcp-platform (Serena reference page), KB-mcp-design (least-privilege-per-agent pattern), `auditing-mcp` (OP-2 / OP-3 rules).

## Document History

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2026-05-23 | 1.0.0 | Initial ADR authoring during Blueprint v1 composition. Codifies the Serena narrowed-always-on posture, 5-agent Python-audit-surface allowlist, pin pre-v1.3.0 with verify-at-execution selection. | design-composer |
| 2026-05-23 | 1.0.1 | Implementation Guidance edit (in-place, no decision-content change): line 137 filename corrected from `design-cc.md` → `design-claude-code.md` with explanatory note about the Path-A reserved-word workaround (the agent's frontmatter `name:` is `design-cc`, but the on-disk filename is `design-claude-code.md`). Trigger: architecture-audit finding I-AA-001 + user disposition at Gate-6 prep ("Fix both via patch-level reconciliation"). Decision content (5-agent allowlist, pin, kill criterion) unchanged. See reconciliation-log-cycle-2.md. | orchestrator (direct mechanical-edit patch) |
| 2026-05-26 | 1.0.2 | Doc-reconciliation note (no decision-content change): AGENTS.md row 54 (the Sub-agent delegation reference / Serena row) was reconciled with §Decision item 2 by removing `design-iac` from the listed agents. The drifted row had been introduced by chore commit `c53631b` (KB-mcp 7→6 backfill) which inadvertently listed 6 agents while annotating the row "5-agent precedent." The AGENTS.md edit is alignment with §Decision item 2; it is NOT a new exclusion. §"Known unknowns" point (a) — flagging `design-iac` and `design-api` as future-additive evaluation candidates pending evidence of Python-audit-surface touch — remains explicitly open. Trigger: federated-crystal patch plan (Phase 1). | mcp-init-enforcement patch |
