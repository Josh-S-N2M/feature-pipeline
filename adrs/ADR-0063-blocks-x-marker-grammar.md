---
id: ADR-0063
version: 1.0.0
status: Accepted
generated: 2026-05-26
generated_by: design-composer
supersedes: []
adrs_inherited:
  - {id: ADR-0044, version: 1.0.0}
applies_to:
  - pipeline-cross-artifact-discipline-r1
  - all-future-discovery-emissions
template_format: per KB-documentation-criteria ADR template v1.0
change_summary: Canonicalizes the Blocks-X marker grammar as a structured HTML-comment pragma `<!-- BLOCKS: <stage-slug>-completion -->` and reserves three `transition_name` values in the state-transitions log for marker closures.
---

# ADR-0063: Blocks-X Marker Grammar Canonicalization

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

Accepted — 2026-05-26

## Context

FR-9 of `pipeline-cross-artifact-discipline-r1` makes "Blocks downstream" markers — phrases of the form `Blocks <stage>` (e.g., `Blocks design-cc-completion`) — into actual stage-transition gates. When the discovery research stage produces an output containing such a marker, the orchestrator must refuse to advance past the named stage until the marker is closed (resolved with rationale, deferred with explicit Open Item, or marked false-positive with rationale).

The codebase has exactly **one prior occurrence** of the marker pattern, at `working/feature/devcontainer-mcp-provisioning-r1/codebase-analysis-report.md` lines 198-202. The prior prose form is `Blocks <stage-slug>-completion.` (period-terminated kebab-case). N=1 is not a grammar — it is an occurrence — but the fact that prior emission exists in the repo means the canonical grammar must be chosen with awareness of the existing pattern.

Three grammar shapes were enumerated in PRD-v2 (and cc-design Q-CC-8 / D-4):

1. **Preserve N=1 prose grammar verbatim** — adopt `Blocks <stage-slug>-completion.` with a regex parser.
2. **YAML-frontmatter field** — add a `blocks:` array to Discovery output frontmatter.
3. **Structured HTML-comment pragma** — `<!-- BLOCKS: <stage-slug>-completion -->` embedded in Discovery output.

The orchestrator must mechanically parse markers from upstream outputs at stage-transition checkpoints. The grammar must be machine-parseable, grep-friendly, multi-marker-ready (Discovery output may contain multiple Blocks-X markers), and invisible-in-rendered-markdown (so the marker doesn't pollute human review).

State-transitions log integration is a separate sub-decision: the `transition_name` field in `auditing-shared/scripts/log_state_transition.py` is free-string per ADR-0044 v1. FR-9 reserves three new string values for marker closures without requiring schema evolution.

## Decision

The canonical Blocks-X marker grammar is:

```
<!-- BLOCKS: <stage-slug>-completion -->
```

**Form rules:**

- **Token:** literal `BLOCKS:` (uppercase, colon-suffixed).
- **Stage slug:** kebab-case identifier matching the stage's `recipe-feature-pipeline` slug, suffixed with `-completion`. Valid examples: `discovery-completion`, `synthesis-completion`, `design-cc-completion`, `design-composition-completion`, `plan-authoring-completion`, `phase-validator-authoring-completion`.
- **Container:** HTML comment `<!-- ... -->`. Invisible in rendered markdown; greppable from CI.
- **Optional payload:** the marker MAY include a one-line description after the slug, separated by ` — ` (em-dash-space surrounded by spaces): `<!-- BLOCKS: design-cc-completion — A-5 grammar undecided -->`. The parser extracts only the slug; the description is for human review.
- **Multiplicity:** multiple markers MAY appear in one output; each is parsed independently.

**Parser shape:** regex `<!--\s*BLOCKS:\s*([a-z0-9-]+)-completion(?:\s+—\s+[^\n]*)?\s*-->`. The orchestrator iterates captures.

**State-transitions log integration.** FR-9 reserves three `transition_name` string values in `state-transitions-log-entry-template.md`:

- `BLOCKS_X_RESOLVED` — marker closed with rationale; downstream stage may proceed.
- `BLOCKS_X_DEFERRED_WITH_OI` — marker converted to an explicit Open Item; downstream stage may proceed; OI tracked.
- `BLOCKS_X_FALSE_POSITIVE` — marker withdrawn with rationale; downstream stage may proceed.

Per ADR-0044 v1, `transition_name` is free-string; these new values land without schema evolution. The `context` field of the log entry carries the marker's stage slug + the closure rationale.

**Migration discipline.** The single existing prior occurrence at `working/feature/devcontainer-mcp-provisioning-r1/codebase-analysis-report.md:198-202` is **not retroactively migrated** — future Discovery emissions use the structured grammar; the prior occurrence stays in the prose form it was authored in.

The grammar spec hosts at `.claude/skills/KB-documentation-criteria/references/blocks-x-marker-grammar.md` — a new reference file in the KB the discovery and orchestrator agents already load.

## Decision Details

| Item | Content |
|---|---|
| Decision | `<!-- BLOCKS: <stage-slug>-completion -->` is the canonical Blocks-X marker grammar; three `transition_name` values reserved for closures. |
| Why now | FR-9 requires a parseable grammar before the orchestrator's stage-transition checkpoint logic can fire. N=1 prior occurrence means no compatibility cost to canonicalize now. |
| Why this | HTML comments are invisible in rendered markdown but greppable from CI; structured shape supports multi-slug from day one; downstream consumers inherit a stable wire format; easier mechanical evaluator. |
| Known unknowns | The em-dash-space separator (` — `) for optional payloads is unusual; some markdown editors may auto-convert em-dashes. The regex tolerates whitespace variation but assumes the em-dash is the literal `—` character (U+2014). |
| Kill criteria | If, during operational use, the em-dash payload separator causes parser brittleness across editor environments, the separator is reconsidered (e.g., ` -- ` two-hyphen-space fallback). |

## Rationale

N=1 is not a grammar — it is an occurrence. Honoring the prior prose form verbatim would ossify a parser that was never designed for multi-slug or grammar variation ("Blocks the stage-x-completion." would fail the regex). Premature lock-in to a precedent of one is the documented anti-pattern.

The structured HTML-comment pragma form preserves readable intent (the `BLOCKS:` token is still skim-greppable in raw markdown) while making the grammar parseable. HTML comments are part of CommonMark and are universally invisible in rendered markdown — the marker doesn't pollute human PR review. Multi-marker support is free (each comment is independent).

The YAML-frontmatter alternative is technically the strongest structured shape, but Discovery output is not currently frontmatter-bearing for this metadata, and adding frontmatter to a markdown output for a single field is over-engineered relative to the N=1 baseline.

State-transitions log integration uses ADR-0044's free-string `transition_name` invariant — no schema evolution required. The three reserved values (`BLOCKS_X_RESOLVED`, `BLOCKS_X_DEFERRED_WITH_OI`, `BLOCKS_X_FALSE_POSITIVE`) name the three legal closure transitions; the log entry's `context` field carries the slug + rationale.

The non-retroactive-migration discipline mirrors FR-11's preserve-verbatim posture for the §O.1 register — historical artifacts are preserved as authored; the going-forward grammar applies to new emissions.

## Options Considered

### Option 1: Preserve N=1 prose grammar verbatim

**Pros:** Zero migration; honors the single prior occurrence.

**Cons:** N=1 is not a grammar; ossifies a parser that wasn't designed for multi-slug; "Blocks the stage-x-completion." would fail the regex; premature lock-in.

### Option 2: YAML-frontmatter field (`blocks: [...]`)

**Pros:** Strongest structured shape; explicit array supports multi-marker.

**Cons:** Discovery output is not currently frontmatter-bearing for this metadata; less discoverable in prose review; over-engineered relative to N=1 baseline; requires the markdown reader to parse frontmatter to find blockers, vs. greppable in-text.

### Option 3 (Selected): Structured HTML-comment pragma `<!-- BLOCKS: <slug>-completion -->`

**Pros:** Greppable from CI; invisible in rendered markdown; multi-slug-ready; downstream consumers (FR-2 §Protocol Conformance schema, AC-FR-9-* assertions, FR-3 PV-tier invariants) inherit a stable wire format; easier mechanical evaluator for D-5's predicate; slight authoring overhead is the only cost.

**Cons:** Slight authoring overhead; diverges from the N=1 prose precedent (small migration if retained anywhere); em-dash payload separator may be editor-environment-fragile.

## Consequences

### Positive Consequences

- The Blocks-X marker becomes a load-bearing stage-transition gate, not advisory prose.
- Discovery agents gain a canonical emission grammar; orchestrator gains a stable parser contract.
- The marker is invisible in human PR review (no pollution of rendered markdown) but greppable from CI (full automation surface).
- Three reserved `transition_name` values give the state-transitions log a stable schema for marker closures without ADR-0044 v1 schema evolution.

### Negative Consequences

- Authoring overhead: discovery agents must remember to use the structured form rather than prose.
- Em-dash payload separator (` — `) may be editor-environment-fragile in rare cases.
- The single prior occurrence in `devcontainer-mcp-provisioning-r1/codebase-analysis-report.md` remains in prose form; a reader who searches for the structured grammar across all historical Discovery outputs will miss it.

### Neutral Consequences

- `.claude/skills/KB-documentation-criteria/references/blocks-x-marker-grammar.md` becomes a new well-known reference file.
- `.claude/agents/discovery-codebase-researcher.md` and `.claude/agents/execute-orchestrator.md` cross-reference the grammar spec.

## Architecture Impact

**Components that change:**

1. `.claude/skills/KB-documentation-criteria/references/blocks-x-marker-grammar.md` — new file (canonical grammar spec).
2. `.claude/agents/discovery-codebase-researcher.md` — emission discipline added.
3. `.claude/agents/execute-orchestrator.md` — parser + gating logic added at stage-transition checkpoints.
4. `.claude/skills/recipe-feature-pipeline/SKILL.md` — checkpoint logic reference.
5. `.claude/skills/KB-documentation-criteria/references/templates/state-transitions-log-entry-template.md` — `transition_name` enumeration extended with three new values.

**New dependencies introduced:**

- Orchestrator parser → grammar spec (read-only at parse time).
- Discovery emission → grammar spec (reference at authoring time).

**Architectural constraints added:**

- Discovery emissions that need to gate a downstream stage use the canonical grammar; prose forms do not satisfy FR-9.
- Marker closures log to `state-transitions.log` via the three reserved `transition_name` values.

**Layers affected:**

- Claude Code / Project Filesystem (only in-scope layer).

## Implementation Guidance

The HTML-comment container is **load-bearing** — it is what makes the marker invisible in rendered markdown while greppable in raw source. Authors should not move the `BLOCKS:` token outside the HTML comment.

The optional payload (` — <description>`) is for human review only; the orchestrator ignores it. Authors should use it to give reviewers context on why the marker exists.

Multiple markers in one Discovery output are independent — each is parsed and gated independently. The orchestrator must collect all markers from all upstream emissions before advancing any downstream stage.

State-transitions log entries for marker closures use the `context` field to carry the slug + rationale. The format is convention, not schema: `<stage-slug>: <closure-rationale-one-liner>`.

## Related Information

- Related ADRs: ADR-0044 (execute-orchestrator is sole writer of state-transitions log; free-string `transition_name`), ADR-0046 (new sibling file evolution discipline — the grammar spec is a new sibling under KB-documentation-criteria/references/).
- Referenced specs / docs: `working/feature/pipeline-cross-artifact-discipline-r1/cc-design.md` §Blocks-X marker grammar; `working/feature/pipeline-cross-artifact-discipline-r1/synthesis.md` D-4.
- Issues / PRs: `Issues/cross-artifact-divergence-detection-gap/analysis.md`.
- Related KBs: `KB-documentation-criteria`.
