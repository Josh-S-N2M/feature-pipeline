---
id: ADR-0059
version: 1.0.0
status: Accepted
generated: 2026-05-26
generated_by: design-composer
supersedes: []
adrs_inherited:
  - {id: ADR-0036, version: 1.0.0}
  - {id: ADR-0054, version: 1.0.0}
  - {id: ADR-0056, version: 1.0.0}
applies_to:
  - pipeline-cross-artifact-discipline-r1
  - all-future-ADRs-with-machine-checkable-prescriptions
template_format: per KB-documentation-criteria ADR template v1.0
change_summary: Establishes the canonical `.prescriptions.yaml` companion-file pattern sibling to each ADR for machine-checkable prescription extraction by `review-architecture-auditor`.
---

# ADR-0059: Companion-File Schema for ADR Design-Realization Audits

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

The `devcontainer-mcp-provisioning-r1` shipment defect surfaced a structural gap: ADR-0041 prescribed specific MCP-server install invocations, but no audit mechanism compared those prescriptions against the eventual `.mcp.json` and `postCreate.sh` files. Five of seven servers shipped broken; the divergence was caught only by forensic post-ship investigation.

FR-1 of the `pipeline-cross-artifact-discipline-r1` feature adds a design-realization audit dimension to `review-architecture-auditor`. The auditor must read prescriptions from somewhere. Two paths were enumerated in PRD-v2 OI-A1:

1. **NLP parse of ADR prose** — extract prescriptions from the natural-language body of each ADR at audit time.
2. **Machine-checkable companion file** — a sibling YAML/JSON file next to each ADR enumerates the prescriptions explicitly.

Cross-source evidence is unambiguous: 9 of 9 production systems surveyed (T-002 in this feature's research notes) use companion-file or schema-anchored separation; the documented LLM misinterpretation rate on decision-prose semantic parsing is 44.57% (arXiv 2602.07609 cited in synthesis claim C-0239). NFR-5 (auditor idempotency, byte-identical output across runs) is falsified by non-deterministic prose parsing.

The decision is constrained by ADR-0036 (single canonical ADR location), ADR-0054 (canonical-helper enforcement pattern), and ADR-0056 (no carve-outs in canonical-placement rules). The companion must live alongside the ADR it accompanies, with the canonical-helper validator extended (not bypassed) to recognize the new sibling pattern.

## Decision

Each ADR that contains machine-checkable prescriptions ships with a sibling companion file at `adrs/ADR-NNNN-<slug>.prescriptions.yaml`. The companion is the canonical source the `review-architecture-auditor` reads for design-realization-audit predicates; the ADR's prose body remains canonical for the decision narrative. The companion file is **optional** — ADRs without machine-checkable prescriptions have no companion (the auditor no-ops per AC-FR-1-b).

The companion conforms to a documented YAML schema (initial `schema_version: 1.0.0`) with predicate entries that name `target_path`, `assertion.kind`, and `severity_floor`. Schema evolution is **additive minor** (new `assertion.kind` values, new optional fields); breaking changes require a major bump and a deprecation window for legacy companions.

A new linter `validate_adr_prescriptions.py` lands in `auditing-shared/scripts/` and enforces the schema, the ADR-to-companion slug match, and target-path existence. Companion-file placement is governed by the same canonical-placement rule as ADRs themselves — no subdirectory, no extension-based carve-out.

## Decision Details

| Item | Content |
|---|---|
| Decision | ADR-sibling companion file `adrs/ADR-NNNN-<slug>.prescriptions.yaml` is the canonical prescription source for FR-1's design-realization audit. |
| Why now | FR-1 ships in `pipeline-cross-artifact-discipline-r1`; the auditor cannot run without a defined prescription source. The MCP shipment incident makes the gap concrete, not hypothetical. |
| Why this | 9/9 surveyed production systems use schema-anchored separation; documented 44.57% NLP misinterpretation rate falsifies the alternative; NFR-5 idempotency requires deterministic input. |
| Known unknowns | Authoring burden of backfilling companion files for 58 legacy ADRs (ADR-0001..ADR-0058) is unmeasured. The hybrid escape hatch (NLP-as-draft, companion-as-canonical) is documented as a fallback if backfill cost bites. |
| Kill criteria | If, during FR-1 operational use, the schema vocabulary cannot express prescriptions in three or more real ADRs without forced fit, the schema's `assertion.kind` vocabulary is expanded — but if companion authoring time exceeds 30 minutes per ADR with prescriptions in steady state, the hybrid-draft path is reconsidered. |

## Rationale

Cross-source triple makes the choice unambiguous:

1. **Survey evidence** — T-002's nine surveyed systems (OpenAPI/Swagger, JSON Schema, ArchUnit, dbt, Terraform, Bazel, GitHub Actions schema, Packwerk, Open Policy Agent) all separate machine-checkable predicates from human-readable rationale. None of them re-derive predicates by parsing prose.
2. **Counter-evidence** — arXiv 2602.07609 documents a 44.57% misinterpretation rate for LLM-based parsing of decision-shaped prose on the exact "semantic/logical misinterpretation" failure category. Rosik 2011 ("Detection of architectural decisions is insufficient for re-running") provides the older complementary signal.
3. **Constraint propagation** — NFR-5 (byte-identical findings JSON across runs) cannot be satisfied if the prescription extraction step is non-deterministic. NLP parsing is non-deterministic; companion files are deterministic.

The companion's role is narrow: it carries only check-shaped predicates, not the decision's reasoning. The ADR's prose retains its canonical role as the human-readable record of why the decision exists. The two artifacts are diff-able against each other (Gate 0 structural check), so drift between prose and companion is itself auditable.

This decision honors the rationale brief's verbatim thesis ("the pipeline must verify relationships across artifacts, not just per-artifact correctness") — the companion file is the load-bearing artifact that makes the relationship `ADR ↔ implementation file` mechanically checkable.

## Options Considered

### Option 1: NLP parse of ADR prose

**Pros:** Zero new repo convention; legacy ADRs work as-is; no companion-file authoring burden.

**Cons:** 44.57% documented misinterpretation rate on decision-prose semantic parsing; non-deterministic output (parse twice, get two different prescription sets) falsifies NFR-5; zero of nine surveyed precedent systems use this shape; audit findings cannot be reproduced for triage.

### Option 2: Hybrid (NLP-as-draft, companion-as-canonical)

**Pros:** Reduces authoring burden at ADR-draft time by generating a starter predicate set; companion-file canonical role preserves determinism.

**Cons:** Two-system maintenance; the LLM-draft step adds non-determinism at authoring time (still need the human review to ratify); not warranted at v1 because authoring-burden is hypothetical until measured.

### Option 3 (Selected): Companion file at `adrs/ADR-NNNN-<slug>.prescriptions.yaml`

**Pros:** 9/9 surveyed precedent; deterministic; reviewable in PR diff like any artifact; lint-able with schema validation; decouples audit-tooling evolution from ADR-prose evolution; honors ADR-0036 + ADR-0054 + ADR-0056 single-canonical-location discipline (sibling lives at the same root).

**Cons:** New repo convention — no `.yaml` siblings to ADRs exist today; legacy ADR backfill cost is unmeasured (Option 2 is the documented escape hatch if backfill bites); risk of companion drifting from ADR prose (mitigation: linter diffs companion against any machine-checkable sections inline in the ADR body).

## Consequences

### Positive Consequences

- FR-1's design-realization audit becomes deterministic, idempotent, and reviewable.
- The MCP-shipment-class defect (ADR prescription diverges from implementation) becomes structurally surfaced rather than silent.
- Future ADRs that prescribe concrete implementation details inherit a clear, lint-checkable contract.
- Schema versioning policy is established upfront, preventing schema-evolution chaos as prescription patterns accumulate.

### Negative Consequences

- New repo convention requires onboarding pressure (documentation in `KB-review-disciplines`).
- Legacy ADRs (ADR-0001..ADR-0058) need backfill for those that contain prescriptions; this is event-triggered (per FR-11 framing) — backfill happens when an FR-1 audit hits a prescription-bearing ADR without a companion.
- Companion can drift from ADR prose if the prose is edited without updating the companion; mitigation is the linter's prose-vs-companion-diff check.

### Neutral Consequences

- `auditing-shared/scripts/validate_adr_prescriptions.py` becomes a new mandatory tool in the pre-deliverable-packaging pass.
- The schema vocabulary (`assertion.kind` values: `regex_present`, `regex_not_present`, `jsonpath_equals`, `jsonpath_count`, `file_exists`, `file_not_exists`, `substring_present`, `substring_absent`) becomes additive over time.

## Architecture Impact

**Components that change:**

1. `review-architecture-auditor` agent gains a new procedure phase (design-realization audit) that reads companion files.
2. `auditing-shared/scripts/` gains a new linter `validate_adr_prescriptions.py`.
3. `KB-review-disciplines/references/architecture-audit.md` gains Lens 4 (Design Realization) alongside the existing CoVe, Blast-Radius, and Brief-Honor lenses.
4. The `adrs/` registry gains an additional file-pattern (`.prescriptions.yaml` siblings).

**New dependencies introduced:**

- Auditor → companion-file YAML schema (read-only at audit time).
- Linter → ADR file existence (back-reference verification).

**Architectural constraints added:**

- ADRs with machine-checkable prescriptions MUST author a companion file (enforced at the ADR-authoring stage in `design-composer`).
- Companion file MUST live in `adrs/` (no subdirectory; ADR-0036 + ADR-0056 — no carve-out for "machine-checkable siblings").

**Layers affected:**

- Claude Code / Project Filesystem (the only in-scope layer for this feature).

## Implementation Guidance

The companion file is **canonical** for prescriptions; the ADR prose is **canonical** for decisions. The two roles are complementary, not redundant. The linter's job is to catch drift between them, not to derive one from the other.

`assertion.kind` vocabulary is extended additively. When a new prescription pattern emerges that no existing kind matches, propose a new kind in a follow-up ADR rather than overloading an existing kind.

Companion files are **optional**. An ADR without machine-checkable prescriptions has no companion. The auditor's no-op behavior on missing companions (per AC-FR-1-b) is the load-bearing affordance that makes the convention cheap to adopt.

The principle is: companion file = predicate; ADR prose = rationale.

## Related Information

- Related ADRs: ADR-0036 (single-location ADR placement), ADR-0054 (canonical-helper three-surface enforcement), ADR-0056 (no carve-outs), ADR-0041 (install-mechanism-hybrid — the canonical exemplar of prescription drift this companion closes), ADR-0018 + ADR-0038 (additive schema-extension discipline this ADR inherits).
- Referenced specs / docs: `working/feature/pipeline-cross-artifact-discipline-r1/cc-design.md` §Companion-file schema; `working/feature/pipeline-cross-artifact-discipline-r1/synthesis.md` D-1.
- Issues / PRs: `Issues/cross-artifact-divergence-detection-gap/analysis.md`.
- Related KBs: `KB-review-disciplines`, `KB-documentation-criteria`.
