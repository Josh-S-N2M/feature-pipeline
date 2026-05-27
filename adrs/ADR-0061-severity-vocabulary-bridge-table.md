---
id: ADR-0061
version: 1.0.0
status: Accepted
generated: 2026-05-26
generated_by: design-composer
supersedes: []
adrs_inherited: []
applies_to:
  - pipeline-cross-artifact-discipline-r1
  - all-cross-surface-finding-emitters
template_format: per KB-documentation-criteria ADR template v1.0
change_summary: Establishes `KB-review-disciplines/references/severity-taxonomy.md` as the canonical host for the cross-surface severity vocabulary bridge table, preserving the auditor / reviewer / phase-validator trifecta with explicit monotonic + non-monotonic mappings.
---

# ADR-0061: Severity Vocabulary Bridge Table Host

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

Three severity vocabularies coexist in the pipeline:

- **Auditor vocabulary** — `BLOCKER` / `MAJOR` / `MINOR` / `NIT` (or `INFO`) — used by `review-architecture-auditor`, `review-cross-artifact-auditor`, `auditing-mcp`, `auditing-cc-configs`, `auditing-shared`, `auditing-subagents`, `auditing-skills`.
- **Reviewer vocabulary** — `critical` / `important` / `recommended` — used by `shared-document-reviewer` and the `KB-review-disciplines` Gate 0/1 procedure.
- **Phase-Validator vocabulary** — `blocking` / `warning` / `informational` — used by `test-phase-validator-author` and the phase-validator-emitted findings.

This trifecta is not arbitrary — each vocabulary fits its audience. Auditor output drives numeric verdict scoring in `auditing-cc-configs/scripts/verdict_compute.py`; reviewer output drives human PR review; phase-validator output drives stage-transition gate decisions.

FR-1, FR-4, FR-5, FR-9, and FR-10 of `pipeline-cross-artifact-discipline-r1` all emit findings that are consumed across these vocabulary surfaces. Without a documented bridge, each FR must either (a) pick a vocabulary unilaterally, introducing audience-fit cost; or (b) emit findings into a vocabulary that some downstream consumer does not understand, introducing translation cost at every consumption site. Codebase-analysis Known Issue 2 surfaces the auditor-surface sub-divergence (`NIT` in `auditing-mcp` vs. `INFO` in architecture/cross-artifact auditors) as further evidence that the trifecta itself has internal seams.

Three reconciliation paths exist:

1. **Unify** — pick one vocabulary; migrate all surfaces to it. Highest cost; destroys audience-fit; one-way per the framer's reversibility classification.
2. **Canonicalize with translator** — pick the auditor vocabulary as canonical (widest footprint); other vocabularies map via documented translator. Lower cost than unify; still touches reviewer and PV surfaces.
3. **Preserve trifecta + bridge table** — each surface keeps its vocabulary; one bridge table documents cross-vocabulary mapping with explicit notes on non-monotonic edges. Lowest cost; purely additive; no migration of existing audit/review/PV outputs.

## Decision

The pipeline preserves the auditor / reviewer / phase-validator severity-vocabulary trifecta. A canonical bridge table is authored at `.claude/skills/KB-review-disciplines/references/severity-taxonomy.md`. The bridge table records monotonic mappings (`BLOCKER` ↔ `critical` ↔ `blocking`; `MINOR` ↔ `recommended` ↔ `warning`) and explicitly enumerates non-monotonic edges (`NIT` vs. `recommended`; the `MAJOR` → `blocking`-vs-`warning` branch in the PV vocabulary).

An optional translator utility `auditing-shared/scripts/translate_severity.py` is documented as the cross-surface utility for tools that need to mechanically translate at `audit-issues.json` emission time. The translator surfaces non-monotonic edges as explicit rationale fields in its output rather than collapsing them silently.

NFR-8's four-field finding shape (`rule`, `target`, `divergence`, `next_action`) lands in the same `severity-taxonomy.md` file as the canonical structure for blocking findings emitted by FR-1/4/5/6/9/10.

## Decision Details

| Item | Content |
|---|---|
| Decision | Preserve trifecta; host bridge table at `KB-review-disciplines/references/severity-taxonomy.md`. |
| Why now | Five FRs in this feature emit findings consumed across all three vocabulary surfaces; without a documented bridge, each FR's contract is under-specified. |
| Why this | All three reviewer-surface agents (shared-document-reviewer, review-architecture-auditor, review-cross-artifact-auditor) already load `KB-review-disciplines`; the bridge lives where its primary consumers already look. Purely additive — no migration cost. |
| Known unknowns | Non-monotonic edge translation (NIT ↔ recommended; MAJOR ↔ {blocking, warning}) requires per-translation context; the translator's accuracy is bounded by how well callers supply context. |
| Kill criteria | If two or more vocabularies converge naturally during a future feature (e.g., reviewer adopts `BLOCKER` for parity with auditor), the bridge table is collapsed accordingly — but the trifecta's persistence is the load-bearing default. |

## Rationale

The trifecta is not a bug; it is the audience-fit pattern that lets each surface serve its consumer:

- Auditor output drives **machines** (verdict-compute scripts). Numeric severity weights (`BLOCKER` = -12 points; `MAJOR` = -5; `MINOR` = -2; `NIT`/`INFO` = -0.5/0) are the load-bearing input to the verdict.
- Reviewer output drives **humans** (PR reviewers reading Gate 1 findings). `critical` / `important` / `recommended` matches the grammar humans use to prioritize.
- Phase-Validator output drives **stage-transition gates** (orchestrator deciding whether to advance). `blocking` / `warning` / `informational` matches the binary decision the gate makes.

Forcing convergence destroys audience-fit. The bridge table preserves audience-fit while making the cross-surface translation explicit. Externally-undecided in the research corpus (no T-corroborator forces one shape) counsels preferring the lowest-irreversibility option, which is the additive bridge.

The bridge table's host is `KB-review-disciplines` because the three reviewer-surface agents already load that KB — the bridge lives where its primary consumers look. The alternative host (`auditing-shared/`) was considered for the cross-surface utility framing, but `KB-review-disciplines` has stronger audience-fit because the bridge's primary readers are reviewers and auditors who already consult that KB's existing references.

## Options Considered

### Option 1: Unify (pick one vocabulary across all surfaces)

**Pros:** Single canonical vocabulary; no translation needed.

**Cons:** Highest migration cost; destroys audience-fit (humans on review output and PV authors lose tailored vocabulary); one-way per reversibility classification; externally-undecided + one-way + tenant-blast-radius is the worst configuration for forcing convergence.

### Option 2: Canonicalize auditor vocabulary with translator

**Pros:** Auditor vocabulary has the widest in-repo footprint; tool-input convergence is improved.

**Cons:** Reviewer and PV vocabularies must migrate (irreversibility cost); humans don't naturally read `BLOCKER` on review output (audience-fit cost); the canonicalization choice is itself externally-undecided.

### Option 3 (Selected): Preserve trifecta + bridge table at `KB-review-disciplines/references/severity-taxonomy.md`

**Pros:** Each vocabulary serves a different audience — auditor output drives tooling; reviewer output drives humans; PV output drives gate decisions; forcing convergence destroys audience-fit. Bridge table is purely additive — no migration cost on existing audit outputs, reviewer outputs, or PV outputs. Externally-undecided counsels reversibility.

**Cons:** Three vocabularies stay in repo; readers must consult the bridge to translate; bridge becomes stale if any vocabulary evolves independently; translator semantics are non-trivial (NIT vs. recommended vs. informational are not strictly equivalent).

## Consequences

### Positive Consequences

- FR-1, FR-4, FR-5, FR-9, FR-10 inherit a single source of truth for severity mapping across surfaces.
- Each consuming surface keeps its audience-fit vocabulary without translation pressure.
- The non-monotonic edges (NIT, MAJOR-branching) gain explicit treatment rather than being silently collapsed.
- The auditor sub-divergence (`NIT` in `auditing-mcp` vs. `INFO` in other auditors per codebase-analysis Known Issue 2) is documented and translatable rather than ambient.

### Negative Consequences

- Three vocabularies persist in the repo; new pipeline contributors must learn all three (mitigated by the bridge table itself, which is the onboarding artifact).
- Bridge maintenance is a new ongoing cost — if any vocabulary evolves, the bridge needs an update.
- Translator semantics are non-trivial; non-monotonic edges may require human review at translation time.

### Neutral Consequences

- `auditing-shared/scripts/translate_severity.py` becomes available but optional.
- NFR-8's four-field finding shape (`rule`, `target`, `divergence`, `next_action`) co-locates with the bridge table.

## Architecture Impact

**Components that change:**

1. `.claude/skills/KB-review-disciplines/references/severity-taxonomy.md` — gains the bridge table + NFR-8 four-field shape spec.
2. (Optional) `.claude/skills/auditing-shared/scripts/translate_severity.py` — new utility for mechanical translation at finding-emission time.

**New dependencies introduced:**

- FR-1/4/5/9/10 finding-emitting code paths → bridge table (reference by name, not by copy).
- Verdict-compute scripts → bridge table (severity → numeric weight mapping).

**Architectural constraints added:**

- New finding-emitting tools document which vocabulary they emit and reference the bridge table for cross-surface consumption.
- Severity-vocabulary evolution on any surface requires updating the bridge table in the same change.

**Layers affected:**

- Claude Code / Project Filesystem (only in-scope layer).

## Implementation Guidance

The bridge table is the **canonical source** for cross-surface severity translation. Tools that need to translate severities at runtime should consult the bridge (or invoke the translator utility); they should not hardcode mappings.

When emitting findings, prefer the **audience-fit vocabulary** for the immediate consumer. A finding emitted by `review-architecture-auditor` for human-readable consumption may use auditor vocabulary; the same finding, if forwarded to `shared-document-reviewer` for Gate 1 ratification, translates via the bridge.

Non-monotonic edges (NIT ↔ recommended; MAJOR ↔ {blocking, warning}) require explicit rationale at translation time. The translator utility surfaces these as rationale fields in its output; downstream consumers must inspect the rationale rather than treating the translation as transparent.

## Related Information

- Related ADRs: ADR-0017 (shared-document-reviewer invocation points), ADR-0020 (KB consolidation — bridge placement under existing KB).
- Referenced specs / docs: `working/feature/pipeline-cross-artifact-discipline-r1/cc-design.md` §Severity vocabulary bridge table; `working/feature/pipeline-cross-artifact-discipline-r1/synthesis.md` D-10.
- Issues / PRs: codebase-analysis Known Issue 2 (auditor surface NIT/INFO sub-divergence).
- Related KBs: `KB-review-disciplines`, `auditing-shared`, `auditing-mcp`, `auditing-cc-configs`.
