---
id: ADR-0060
version: 1.0.0
status: Accepted
generated: 2026-05-26
generated_by: design-composer
supersedes: []
adrs_inherited:
  - {id: ADR-0020, version: 1.0.0}
applies_to:
  - pipeline-cross-artifact-discipline-r1
  - all-future-phase-validators
template_format: per KB-documentation-criteria ADR template v1.0
change_summary: Establishes the hybrid authoring shape for FR-3 cross-file invariants — denormalized declaration per phase validator with a centralized catalog body in `KB-task-decomposition`.
---

# ADR-0060: Cross-File Invariant Catalog Authoring Shape

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

Phase 1 of `issue-capture-mechanism-r1` produced a structural spec whose §7 ID-derivation rule contradicted its three sibling templates and five empirical precedents. PV-1 passed cleanly because no phase validator compared the spec to the templates. The defect was caught by human post-phase review, not by pipeline machinery.

FR-3 of the `pipeline-cross-artifact-discipline-r1` feature establishes the PV-tier cross-file consistency invariant catalog. When a phase ships two or more deliverable files, the phase validator must declare every cross-file relationship and contain one assertion per relationship. Three authoring shapes were enumerated in PRD-v2 OI-A2:

1. **Denormalized inline** — each phase validator declares AND defines its invariants in-line; no central catalog.
2. **Centralized** — one catalog file owns all invariants; phase validators do not declare; catalog enumerates which PVs each invariant applies to.
3. **Hybrid** — phase validators declare which invariants they own (denormalized declaration); the centralized catalog hosts predicate bodies, severity, and error-message text.

T-004 in this feature's research notes surveyed six cross-file-invariant systems (Terraform, dbt, OpenAPI, JSON Schema, ArchUnit, Bazel). All six land at the hybrid sweet spot. The Shopify Packwerk v3.0 migration retrospective is the strongest available counter-evidence — they removed fully-centralized privacy checks because centralization fights the grain of locality-of-reference at the declaration site.

The catalog is hosted in `KB-task-decomposition` (the KB consumed by `finalize-task-decomposer` and consulted by `test-phase-validator-author`). Per codebase-analysis Known Issue 3, the PV-author rubric body lives inlined in `.claude/agents/test-phase-validator-author.md` — not in KB-task-decomposition — so the rubric prompt edits go in the agent body and the catalog file goes in the KB.

## Decision

FR-3 cross-file invariants are authored as a **hybrid**:

1. **Denormalized declaration.** Each phase validator declares which invariants it honors by ID (e.g., `CFI-003`, `CFI-007`) in a required "Cross-File Invariants" section in its body. Single-deliverable phases declare `N/A — single-deliverable phase` rather than omit silently.
2. **Centralized body.** Each `CFI-NNN` invariant's full body — predicate logic, error-message template, severity floor, applicable-phases list — lives in `.claude/skills/KB-task-decomposition/cross-file-invariants.md`.

The catalog grows additively. Deprecation of a catalog entry follows the same supersession discipline as ADRs (ADR-0005): a catalog entry is never deleted; it is marked `superseded_by: CFI-NNN` and the new entry is appended.

The cross-file finding's severity, when fired, is the maximum of its component per-file assertions per AC-FR-3-c (the no-downgrade rule). The catalog records the severity floor; the assertion machinery enforces the no-downgrade rule.

## Decision Details

| Item | Content |
|---|---|
| Decision | Hybrid catalog — denormalized declaration in each PV body; centralized predicate bodies in `KB-task-decomposition/cross-file-invariants.md`. |
| Why now | FR-3 ships in `pipeline-cross-artifact-discipline-r1`; phase validators authored after the feature ships need a known authoring shape. |
| Why this | 6/6 surveyed systems use this shape; Packwerk v3.0 retrospective is the strongest counter to fully-centralized; locality at declaration + DRY at body site. |
| Known unknowns | T-004 caveats that surveyed domains are code/data/API not pipeline-document content — transferability of the analogical mapping is partial. Operational use of the first 5–10 invariants will measure whether the hybrid shape fits this domain. |
| Kill criteria | If the catalog grows beyond ~30 entries without obvious deprecation pressure, the denormalized half is reconsidered (locality may be paying off less than the DRY discipline costs at that scale). |

## Rationale

Cross-source triple:

1. **Survey evidence** — T-004's six systems (Terraform, dbt, OpenAPI, JSON Schema, ArchUnit, Bazel) all land at the hybrid sweet spot. None mandate fully-centralized authorship; none accept fully-denormalized.
2. **Counter-evidence** — Shopify Packwerk v3.0 migration retrospective documents the centralized-back-to-hybrid migration. Privacy checks were removed from Packwerk's central rule set precisely because the centralized authorship pattern fought locality. JSON Schema's `$defs` (the closest-to-centralized pattern surveyed) is per-document, not cross-document, and is functionally hybrid at scale.
3. **Constraint propagation** — FR-3's goal is enforcing cross-file consistency. Denormalized-inline structurally fights that goal: each PV defines its own version of a shared invariant, with predictable drift. Centralized fights authoring locality. Hybrid is the only shape that serves both ends.

The catalog ID convention (`CFI-NNN`) follows the same monotonic-assignment pattern as ADRs. The first invariants authored under this discipline pre-fill the catalog with the cross-file relationships this feature's own deliverables share — eat-own-dogfood per FR-3.

## Options Considered

### Option 1: Denormalized inline (each PV defines its invariants)

**Pros:** No catalog discipline; minimum infrastructure.

**Cons:** Per-PV drift — same invariant defined N times across N PVs; severity / error-message text scattered, which worsens the D-10 severity-vocabulary divergence; structurally fights FR-3's enforcement goal.

### Option 2: Centralized (catalog declares both invariants AND PV applicability)

**Pros:** Single source of truth; no per-PV duplication.

**Cons:** Packwerk v3.0 retrospective is the strongest direct counter; PV authors lose locality of declaration; catalog becomes a bottleneck artifact; presence-not-substance failure mode (catalog row says "applies to PV-3" but PV-3 doesn't actually enforce it).

### Option 3 (Selected): Hybrid (denormalized declaration + centralized body)

**Pros:** 6/6 surveyed precedent; locality at declaration; DRY at body; cross-file invariants structurally need cross-file coordination; coheres with severity-vocabulary discipline because severity floors live in one place.

**Cons:** Two-file coordination at edit time; catalog grows monotonically and needs deprecation discipline; T-004 caveats transferability of the surveyed domains.

## Consequences

### Positive Consequences

- The PV-1-class spec-vs-templates divergence (the founding defect for FR-3) becomes structurally surfaced.
- Cross-file invariants gain a stable ID convention (`CFI-NNN`) that downstream artifacts can reference.
- The severity floor for each invariant is documented in one place; the no-downgrade rule (AC-FR-3-c) inherits a single source of truth.
- Future phase validators inherit a known authoring shape without per-author negotiation.

### Negative Consequences

- Two-file coordination at edit time (the PV declares; the catalog defines).
- Catalog grows monotonically; deprecation discipline becomes load-bearing as the catalog accumulates.
- The transferability of the cross-domain survey evidence (code/data/API → pipeline-document content) is partial; the first operational uses are the validation.

### Neutral Consequences

- `KB-task-decomposition/cross-file-invariants.md` becomes a new well-known file.
- `test-phase-validator-author` agent gains a new required section ("Cross-File Invariants") in its Phase 2 rubric.

## Architecture Impact

**Components that change:**

1. `.claude/agents/test-phase-validator-author.md` — Phase 2 (the inlined PV-author rubric per Known Issue 3) gains a required "Cross-File Invariants" section.
2. `.claude/skills/KB-task-decomposition/cross-file-invariants.md` — new catalog file (centralized body).
3. `.claude/skills/KB-review-disciplines/references/architecture-audit.md` — cross-reference to the catalog under the cross-artifact lens.

**New dependencies introduced:**

- Phase validators → catalog (reference by `CFI-NNN`).
- Auditing surfaces → catalog (read severity floors for the no-downgrade enforcement).

**Architectural constraints added:**

- Catalog entries are append-only; deprecation follows ADR-0005 supersession discipline.
- Cross-file finding severity is bound by the catalog's recorded floor (no-downgrade rule, AC-FR-3-c).

**Layers affected:**

- Claude Code / Project Filesystem (only in-scope layer).

## Implementation Guidance

PV authors declare invariants; they do not redefine them in-line. The discipline is: if the same invariant could plausibly fire in another phase's deliverables, it belongs in the catalog by ID; if it is genuinely unique to one phase, it still goes in the catalog but with a single-entry `applicable_phases` list.

The catalog body fields are: `id`, `predicate_logic` (natural-language description + machine-checkable assertion pattern), `error_message_template`, `severity_floor`, `applicable_phases[]`. Add fields additively; do not break existing structure.

Severity floors in the catalog establish the minimum; the cross-file finding may upgrade to a higher severity at firing time per the no-downgrade rule, but never downgrade.

## Related Information

- Related ADRs: ADR-0020 (KB consolidation — catalog placement under existing KB), ADR-0005 (append-only supersession for catalog entries).
- Referenced specs / docs: `working/feature/pipeline-cross-artifact-discipline-r1/cc-design.md` §FR-3; `working/feature/pipeline-cross-artifact-discipline-r1/synthesis.md` D-2.
- Issues / PRs: `Issues/cross-artifact-divergence-detection-gap/analysis.md`.
- Related KBs: `KB-task-decomposition`, `KB-review-disciplines`.
