---
id: ADR-0042
version: 1.0.0
status: Accepted
generated: 2026-05-23
generated_by: design-composer
supersedes: []
adrs_inherited: [ADR-0031, ADR-0033]
applies_to:
  - devcontainer-mcp-provisioning-r1
  - .claude/skills/auditing-mcp/ (graduating from auditing-cc-configs family to its own family)
  - .claude/skills/auditing-cc-configs/ (family-coordinator membership list updated)
  - .claude/skills/auditing-shared/ (consumer-list cross-reference updated)
  - future auditing-* graduation decisions (precedent-setting per Issues/proposal-auditing-family-graduation-review.md)
template_format: per KB-documentation-criteria ADR template v1.0
change_summary: >-
  Graduates `auditing-mcp` from membership in the `auditing-cc-configs`
  sub-skill family into its own family-coordinator status, per the
  Gate-4 user override of the design-composer's Path B recommendation
  (which would have preserved family membership). Establishes the
  security-distinct-domain precedent that future `auditing-*` family
  decisions will inherit, captured for downstream pipeline review in
  `Issues/proposal-auditing-family-graduation-review.md`.
---

# ADR-0042: `auditing-mcp` graduated from `auditing-cc-configs` family to its own family-coordinator

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

Accepted — 2026-05-23 (user decision at Gate 4 of `devcontainer-mcp-provisioning-r1`)

## Context

The `devcontainer-mcp-provisioning-r1` Blueprint v2 carried an open question (OI-2 / Q-CC-1) on family-coordinator placement for the augmented `auditing-mcp` skill. The design-composer's pre-decision posture had been **Path B (preserve family membership)** — `auditing-mcp` remains a sub-skill of `auditing-cc-configs`, minimum convention change. The rationale for Path B was repo-discipline conservatism: the three existing trifectas (CC, Codespaces, GHA) showed inconsistent family treatment, and the per-layer Designer had taken no position.

The user, at Gate 4, overrode Path B in favor of **Path A (graduate to its own family)**. The user's verbatim resolution:

> "graduate and then write an issue on whether we need to look at github codespace and the others in an issue report under Issues/ for future consideration of a pipeline run"

Coupled with the user's OI-3 hard-gate decision (see ADR-0043), the substantive position is that MCP failures occupy a **materially distinct risk surface** from `.claude/`-config correctness: MCP servers are external processes with their own protocol, credentials, and supply-chain attack vectors; their BLOCKER findings can break devcontainer / docker / pipeline operation, which is not what `auditing-cc-configs` was designed to detect.

Per FR-5, the design-composer is the only sub-agent in this pipeline that authors ADRs. This decision is one-way for the project's auditing-skill family-structure convention — once `auditing-mcp` is graduated, the precedent applies to future graduation candidates per the `Issues/proposal-auditing-family-graduation-review.md` companion artifact.

Background facts loaded into the option space:

- `auditing-cc-configs/SKILL.md` lines 144–153 currently list six sub-skills, of which `auditing-mcp` is one. Two siblings (`auditing-github-actions`, `auditing-codespaces`) already sit outside this list as de-facto graduated families.
- `auditing-shared/SKILL.md` (per ADR-0031) is the cross-audit-module shared-utility home, currently naming four consumers; gaining `auditing-mcp` as a fifth, now-graduated consumer.
- `auditing-codespaces` is a STUB per ADR-0033; when filled, it is the obvious next graduation candidate. This ADR's precedent governs that future decision.
- Two related Issues frame the broader question: `Issues/proposal-auditing-family-graduation-review.md` (which this ADR triggers as a follow-up) and `Issues/analysis-per-agent-design-evaluation-gap.md` (which contextualizes why structural decisions like family placement are easy to miss without explicit demand-driven sweeps).

## Decision

1. **`auditing-mcp` graduates to its own family-coordinator status.** Its `SKILL.md` frontmatter `family:` field changes from `auditing-cc-configs` to `auditing-mcp`. The body gains a `## Sub-skill family` section (initially empty — there are no sub-skills under `auditing-mcp` yet — but declaring the coordinator pattern reserves the structural slot for future additions).
2. **`auditing-cc-configs` family list updated.** The line-148–153 enumeration in `auditing-cc-configs/SKILL.md` removes the `auditing-mcp` row. The coordinator's body documents the graduation inline (one sentence with cross-reference to this ADR).
3. **`auditing-shared` consumer-list expanded.** `auditing-shared/SKILL.md`'s description (per ADR-0031) currently lists four consumers; `auditing-mcp` is added as a graduated-family consumer alongside the others, with the same shared-utility cross-reference convention.
4. **Orchestrator handling.** Project conventions that refer to "the auditing family" must now handle multiple families cleanly (singular → plural convention drift). Pipeline orchestrator references update accordingly; details land in the implementation Plan.
5. **Precedent established for future graduation candidates.** When `auditing-codespaces` (currently STUB per ADR-0033) is filled by a future feature pipeline, the placement default is **graduation into its own family** (mirroring this ADR) unless the future feature surfaces evidence of tight coupling to `auditing-cc-configs` that this precedent did not anticipate. The graduation-criteria rubric for other ambiguous siblings (e.g., `auditing-hooks`) is deferred to the future pipeline run captured in `Issues/proposal-auditing-family-graduation-review.md` (suggested slug: `auditing-family-structure-review-r1`).

## Decision Details

| Item | Content |
|---|---|
| Decision | Graduate `auditing-mcp` to its own family-coordinator; update `auditing-cc-configs` family list and `auditing-shared` consumer-list accordingly; establish security-distinct-domain precedent for future auditing-family decisions. |
| Why now | The augmented `auditing-mcp` ships as part of this feature's W/H/A trifecta completion; the family-placement decision is forced at the same time. Deferring would either freeze the design-composer's Path B (preserve family) by default — which the user has explicitly rejected — or leave a TBD in the trifecta documentation. Either is worse than codifying now. |
| Why this | The user's substantive reasoning (MCP failures break devcontainer/docker, not just `.claude/`-config correctness) reflects a real distance in mission, blast radius, and protocol surface from `auditing-cc-configs`'s native domain. The graduation is symmetric with `auditing-github-actions` (already de-facto graduated) and the future `auditing-codespaces` stub-fill. |
| Known unknowns | (a) Whether other current siblings (especially `auditing-hooks` — adjacent failure domain via arbitrary shell execution) warrant the same graduation under the precedent set here. **Deferred** to the future pipeline run captured in `Issues/proposal-auditing-family-graduation-review.md`. (b) Whether the empty `## Sub-skill family` section on the new `auditing-mcp` family-coordinator is a structural smell or a healthy reservation of the slot — current judgment: healthy reservation, since future MCP-audit sub-skills (e.g., per-server probe-suite families) are plausible. (c) Whether the orchestrator's "auditing family" singular-vs-plural convention requires a separate ADR — current judgment: no, the Plan absorbs the convention update inline. |
| Kill criteria | If after one year of post-ship operation, `auditing-mcp` retains zero sub-skills AND is never invoked outside the `devcontainer-mcp-provisioning-r1`-derived pipelines, the empty-coordinator pattern is vestigial; an additive amendment ADR may demote it back to a leaf sub-skill (re-joining `auditing-cc-configs` or a successor family) per the criteria-rubric authored by the future `auditing-family-structure-review-r1` run. |

## Rationale

The composer's pre-decision Path B recommendation was anchored in repo-discipline conservatism (minimum convention change; the three existing trifectas were structurally inconsistent and didn't force a precedent). The user's override is anchored in **failure-domain distance**: BLOCKER findings from `auditing-mcp` indicate broken external processes, supply-chain compromise, or credential leakage — failure modes that `auditing-cc-configs` was not designed to triage. Co-locating them in the same family would dilute both coordinator missions.

The user's parallel OI-3 hard-gate decision (ADR-0043) reinforces the substantive distance: hard-gating `auditing-mcp` at Gate 6 is justified only if its findings are categorically different from `.claude/`-config findings; co-locating in the same family would create an awkward gating asymmetry (one sub-skill hard-gates, five do not). Graduating `auditing-mcp` resolves the asymmetry cleanly.

The Issues-follow-up artifact (`Issues/proposal-auditing-family-graduation-review.md`, authored at Gate-4 closure) captures the broader question — which other siblings warrant graduation under this precedent — without forcing this feature's scope to grow beyond `auditing-mcp` itself. That artifact is the canonical input for the future `auditing-family-structure-review-r1` pipeline run.

## Options Considered

### Option 1: Path B — preserve family membership (composer's pre-decision recommendation; rejected by user)

**Pros:** Minimum convention change; honors the design-composer's brief commitment to "minimum convention change" repo-discipline; defers the broader graduation question without forcing a precedent now.

**Cons:** The substantive distance argument (MCP failure domain vs `.claude/`-config failure domain) is real and would still need addressing later; the family list grows by one sub-skill with a materially distinct mission, eroding the coordinator's coherence over time. The OI-3 hard-gate decision (ADR-0043) creates a gating asymmetry that Path B does not resolve.

### Option 2 (Selected): Path A — graduate to its own family-coordinator

**Pros:** Aligns the family structure with the substantive failure-domain distance; resolves the hard-gate-asymmetry cleanly (ADR-0043); creates a clear precedent for future graduation candidates, captured for downstream review in the companion Issues artifact; mirrors the de-facto already-graduated `auditing-github-actions` posture and the future `auditing-codespaces` stub-fill posture; reserves the structural slot for future MCP-audit sub-skills.

**Cons:** Empty `## Sub-skill family` section on day one is a slight structural smell; orchestrator-side singular-to-plural convention update is non-trivial (paid once, regardless of future graduations). The composer's Path B recommendation is overridden; the design-composer must publicly accept the override (this ADR is that acceptance).

### Option 3: Dissolve `auditing-cc-configs` entirely; graduate all current sub-skills to peer families

**Pros:** Eliminates the coordinator pattern altogether; every audit-domain stands on its own.

**Cons:** Far more expensive (six structural moves; orchestrator-side changes for all six); the four "tightly coupled to coordinator" siblings (`auditing-skills`, `auditing-context-files`, `auditing-subagents`, `auditing-settings`) share the `.claude/`-config-correctness mission cleanly — dissolution loses real coordination value. Not in scope for this feature; deferred to the future review run as a separate consideration.

## Consequences

### Positive Consequences

- The family structure now reflects the substantive failure-domain distinction between MCP audit and `.claude/`-config audit.
- The OI-3 hard-gate-asymmetry resolves cleanly: hard-gating a graduated family is conventional; hard-gating one sub-skill of a six-sub-skill family would be structurally awkward.
- The precedent for future graduations is recorded, with companion Issues artifact for downstream review.
- The graduation symmetry with `auditing-github-actions` (already de-facto graduated) and future `auditing-codespaces` stub-fill is restored.

### Negative Consequences

- The orchestrator's "the auditing family" singular-vs-plural convention requires an audit and update (paid once; small but non-trivial).
- The `auditing-mcp` family-coordinator starts with zero sub-skills (an empty `## Sub-skill family` body section) — readers unfamiliar with the precedent may read this as a structural smell.
- The design-composer's pre-decision recommendation is publicly overridden; the precedent that composers may be overridden at Gate 4 is itself a meta-pattern that future composer runs will internalize.

### Neutral Consequences

- `auditing-shared` (per ADR-0031) gains one consumer (`auditing-mcp`). No API change; the cross-reference is descriptive.
- Six existing sub-skills of `auditing-cc-configs` remain unchanged in family membership. The future review run revisits.

## Architecture Impact

1. **Layers affected.** Claude Code / Project Filesystem (the family-structure convention is a `.claude/skills/` concern). No other layer is impacted.
2. **Components that change.**
   - `.claude/skills/auditing-mcp/SKILL.md` — frontmatter `family:` field changes from `auditing-cc-configs` to `auditing-mcp`; body gains a `## Sub-skill family` section (initially empty).
   - `.claude/skills/auditing-cc-configs/SKILL.md` — lines 144–153 (Sub-skill family enumeration) loses the `auditing-mcp` row; coordinator body documents the graduation inline with cross-reference to this ADR.
   - `.claude/skills/auditing-shared/SKILL.md` — description updated to add `auditing-mcp` as a graduated-family consumer per ADR-0031 cross-reference convention.
   - Pipeline orchestrator / project conventions referring to "the auditing family" singular — audit and update for plural handling (precise file list is Plan-author responsibility).
3. **New dependencies introduced.** None at the runtime level. The structural changes are documentation and frontmatter.
4. **Architectural constraints added.** Future auditing-skill additions inherit the precedent: graduation is the default for skills whose failure-domain is materially distinct from `.claude/`-config correctness; preservation in `auditing-cc-configs` is the default for skills whose failure-domain is tightly coupled to `.claude/` configuration. The graduation-criteria rubric is formalized by the future `auditing-family-structure-review-r1` pipeline run.

## Implementation Guidance

**Frontmatter change to `auditing-mcp/SKILL.md`:**

```yaml
# before:
family: auditing-cc-configs

# after:
family: auditing-mcp
```

**Body change to `auditing-mcp/SKILL.md`** — add a `## Sub-skill family` section after the existing body, with this content (initial empty-coordinator declaration):

```markdown
## Sub-skill family

This coordinator currently has no sub-skills. The slot is reserved for future MCP-audit sub-skills (e.g., per-server probe-suite families, transport-specific audit modules). Until populated, `auditing-mcp` acts as a single-skill family-coordinator.

Cross-references:
- `auditing-shared` — cross-audit-module shared utilities (per ADR-0031); this family is a consumer.
- `auditing-cc-configs` — the prior family; this skill graduated per ADR-0042 of the `devcontainer-mcp-provisioning-r1` feature.
```

**Body change to `auditing-cc-configs/SKILL.md`** — lines 144–155 area, after the family enumeration table:

- Remove `- **auditing-mcp** — .mcp.json, optional runtime audit` row from the list (currently line 153).
- Update the lead-in sentence count from "six sibling skills" to "five sibling skills."
- Add a paragraph below the list (or in the most logically adjacent location):

```markdown
**Family graduation history:**
- `auditing-mcp` graduated to its own family-coordinator on 2026-05-23 per ADR-0042 (`devcontainer-mcp-provisioning-r1` feature). Rationale: security-distinct failure domain (external-process, supply-chain, credential-leak risks vs `.claude/`-config correctness).
```

**Body change to `auditing-shared/SKILL.md`** — its description currently lists four consumers (`auditing-cc-configs, auditing-skills, auditing-subagents, auditing-context-files`); add `auditing-mcp` as a fifth consumer, noting "graduated family-coordinator" status.

**Orchestrator-side update.** The plan-author audits project files for references to "the auditing family" (singular) and updates to plural where multiple families are now in play. Precise scope of files requiring update is left to plan-author per `Issues/proposal-auditing-family-graduation-review.md` §3 item 6.

**Step list (canonical sequence):** See the consolidated step list in this Blueprint v3 §Implementation Plan; the step list there mirrors `Issues/proposal-auditing-family-graduation-review.md` §3 items 1–6, scoped to the `auditing-mcp` graduation specifically.

**No procedural detail beyond the above.** Sequencing, task decomposition, and per-file edits are Plan-author concerns.

## Related Information

- Related ADRs: ADR-0031 (`auditing-shared` cross-audit-module convention — consumer list updated by this ADR), ADR-0033 (`auditing-codespaces` STUB — future graduation candidate per the precedent set here), ADR-0043 (`auditing-mcp` Gate-6 hard gate — paired Gate-4 user decision; the hard-gate-asymmetry argument depends on graduation).
- Referenced specs / docs: Blueprint v3 §Open Items / OI-2 closure (this ADR is its codification); Blueprint v3 §Acceptance Criteria (AC-CC-1, AC-X-2 — inventory references stay consistent with the family-graduation); Blueprint v3 §Claude Code / Project Filesystem Design (the structural-change narrative).
- Issues / PRs: `Issues/proposal-auditing-family-graduation-review.md` (companion follow-up artifact; captures the broader graduation-criteria-rubric question for downstream pipeline run); `Issues/analysis-per-agent-design-evaluation-gap.md` (contextualizes why structural decisions like this are easy to miss without explicit demand-driven sweeps).
- Related KBs: KB-cc-design (skill-family conventions; sub-skill family pattern), KB-documentation-criteria (ADR template, supersession discipline per ADR-0005), KB-review-disciplines (Gate-4 user-decision artifact discipline).
