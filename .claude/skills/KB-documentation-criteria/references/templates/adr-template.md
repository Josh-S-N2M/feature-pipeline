---
id: ADR-NNNN
version: 1.0.0
status: Proposed
generated: <ISO-8601-date>
generated_by: <sub-agent-name>
supersedes: []
adrs_inherited: []
applies_to:
  - <feature-slug or project component>
template_format: per KB-documentation-criteria ADR template v1.0
change_summary: <one-line summary of what this ADR establishes or changes>
---

# ADR-NNNN: [Title]

## Contents

Section completion checklist — each box must be checked (including `N/A — out of scope` rows) before this document leaves draft. The reviewer's Gate 0 check uses this list as the structural-presence anchor.

- [ ] Status
- [ ] Context
- [ ] Decision
- [ ] Decision Details
- [ ] Rationale
- [ ] Options Considered
- [ ] Consequences
- [ ] Architecture Impact
- [ ] Implementation Guidance
- [ ] Related Information

**Note to authoring sub-agent:** update this list if you add or remove top-level (H2) sections from the document. Do NOT remove the `## Contents` heading — it is required for Gate 0 structural review. Mark each box `[x]` when the corresponding section is complete (or contains an explicit `N/A — out of scope` marker for layers not in scope).

## Status

[Proposed | Accepted | Deprecated | Superseded | Rejected] — <date>

If `Superseded`, the frontmatter `supersedes:` list identifies the prior ADR(s); the current ADR is the canonical one. If `Deprecated`, no replacement exists yet but the decision is no longer in force.

## Context

[Describe the background and reasons why this decision is needed. Include the essence of the problem, current challenges, and constraints. State load-bearing facts — environmental, platform-level, or codebase-level — that constrain the option space.]

## Decision

[State the actual decision in 1–3 sentences. Be specific. If the decision has multiple parts, enumerate them.]

## Decision Details

| Item | Content |
|---|---|
| Decision | [The decision in one sentence] |
| Why now | [Why this needs to happen now — timing rationale] |
| Why this | [Why this option over alternatives — 1–3 lines] |
| Known unknowns | [At least one uncertainty at this point] |
| Kill criteria | [One signal that should trigger reversal of this decision] |

## Rationale

[Explain why this decision was made and why it is the best option compared to alternatives. Reference the constraints from Context. If the decision honors a rationale brief commitment, name it.]

## Options Considered

### Option 1: [Description]

**Pros:** [List advantages]

**Cons:** [List disadvantages]

### Option 2: [Description]

**Pros:** [List advantages]

**Cons:** [List disadvantages]

### Option 3 (Selected): [Description]

**Pros:** [List advantages]

**Cons:** [List disadvantages]

## Consequences

### Positive Consequences

- [Positive impact 1]
- [Positive impact 2]

### Negative Consequences

- [Negative impact or trade-off 1]
- [Negative impact or trade-off 2]

### Neutral Consequences

- [Change that is neither good nor bad 1]

## Architecture Impact

[Describe how this decision affects existing architecture:
1. Components that change
2. New dependencies introduced
3. Architectural constraints added or removed
4. Layers affected (use the 9-layer taxonomy from `../layer-taxonomy.md`)]

## Implementation Guidance

[Principled direction only. Implementation procedures go to the Blueprint or per-layer Design sections.]

Example: "Use dependency injection" ✓
Example: "Implement in Phase 1" ✗ — that's a Plan concern, not an ADR concern.

## Related Information

- Related ADRs: ADR-NNNN, ADR-NNNN
- Referenced specs / docs: [paths]
- Issues / PRs: [links]
- Related KBs: [list]

---

## Authoring notes (delete this section in the final ADR)

**Frontmatter discipline:**
- `id`: zero-padded four-digit. Assigned monotonically across the project (not per-feature). Allocator: orchestrator at ADR-write time.
- `version`: semver. Initial is `1.0.0` once `status: Accepted`. Drafts use `0.1.0`, `0.2.0`, etc.
- `supersedes`: list of `{id, version}` tuples for ADRs this one replaces. Empty list `[]` if not superseding anything.
- `adrs_inherited`: list of ADRs whose decisions this one carries forward without re-litigation. Used when an ADR explicitly relies on a prior decision without restating it.
- `applies_to`: scope of the ADR. Can be a feature-slug, a project component, or a coarser scope like "the entire pipeline."
- `change_summary`: one line. Read by the orchestrator and by downstream documents that reference this ADR.

**Length budget:**
- Aim for under 200 lines. ADRs longer than 200 lines usually indicate the decision should be split.
- Context and Rationale together: ~60% of body.
- Options Considered: ≥2 options, including the selected one. A single-option ADR is suspicious — surface the alternatives explicitly even if they were obviously rejected.

**When ADRs are authored:**
- Per FR-5: only `design-composer` authors ADRs during Design Composition. Per-layer designers MUST NOT author ADRs — they surface the need; the composer writes the ADR.
- Exception: ADRs that capture orchestrator-level or process-level decisions may be authored outside Design Composition by direct human or `finalize-reconciler` action (this is the v4.x retroactive ADR migration pattern).

**Review:**
- Every ADR is reviewed by `shared-document-reviewer` (Gate 0/1) per ADR-0017 invocation point 5 ("after each individual ADR write").
- Architecture Audit may surface ADR-level concerns, but the ADR's reviewer remains `shared-document-reviewer`, not the architecture auditor.
