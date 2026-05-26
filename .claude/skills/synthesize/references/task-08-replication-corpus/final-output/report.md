# Synthesis Report: Task-08 Vertical-Slice Replication

**Run ID:** `task-08-replication-20260501-021500`
**Generated:** 2026-05-01T02:15:00Z
**Audience depth:** engineering
**Scope:** narrow
**Sources:** 2 (technical-designer.md, synthesis-pipeline-technical-design.md)
**Claims:** 53 | **Entities:** 42 | **Decisions:** 5 | **Constraints honored:** 0

## Executive Summary

Five architectural decisions emerged from the corpus, partitioned by Bezos reversibility. Four are **one-way doors** (substrate choice, verification regime, recursion safety, user-confirmation gate) — they shape the pipeline's contract with users and the file system, and reversing any of them later carries significant cost. One is a **two-way door** (memory architecture) — the convention can be revised in place without breaking the pipeline's external interface.

The strongest cross-source signal is **D-0003: the vertical-slice early verification gate** [synthesis-pipeline-technical-design.md](/mnt/user-data/uploads/synthesis-pipeline-technical-design.md). Both source documents converge on this discipline; the technical-designer source defines it abstractly while the synthesis-pipeline-technical-design source applies it concretely (this run is its instance). The gate's binding mechanism — output comparison with captured reference artifacts — is the load-bearing primitive that makes the pipeline's correctness falsifiable rather than asserted [technical-designer.md](/mnt/user-data/uploads/technical-designer.md).

**D-0002 (memory architecture)** carries the corpus's only flagged uncertainty (🔶 engineering proposal — no precedent), and the Synthesizer surfaces this in Limitations rather than treating it as settled [synthesis-pipeline-technical-design.md](/mnt/user-data/uploads/synthesis-pipeline-technical-design.md). Every other decision rests on `verified` Critic verdicts with `high` confidence and independent corroboration where applicable.

The recommended option is `native` for all five decisions. This is unsurprising — the corpus is *about* implementing in Claude Code primitives, so the substrate-decision frame is largely confirmatory. Where it would matter is in cross-substrate work; for that, the corpus's substrate registry [substrate-registry.md](/mnt/user-data/uploads/synthesis-pipeline-technical-design.md) provides the loss-vs-pattern framing the next decision generation would consume.

## Findings

### Pipeline architecture (Cluster A)

The pipeline is realized as a six-phase sequential composition of sub-agents — Extractor, Grapher, Critic, Decision Framer, Constraint/Substrate, and Synthesizer — using only Claude Code primitives [synthesis-pipeline-technical-design.md](/mnt/user-data/uploads/synthesis-pipeline-technical-design.md). Each phase agent runs in an isolated context window via the Task tool; the orchestrator passes only the run-id and the previous-phase artifact path, never the contents, preserving context budget [synthesis-pipeline-technical-design.md](/mnt/user-data/uploads/synthesis-pipeline-technical-design.md).

The orchestrator owns three substrate-level invariants: run-id allocation, recursion-safety glob exclusion, and checkpoint state for `--resume` semantics [synthesis-pipeline-technical-design.md](/mnt/user-data/uploads/synthesis-pipeline-technical-design.md). The bounded retry rule (at most one Critic-driven Extractor retry; at most one Substrate-driven Framer retry) is enforced via a counter on the `params.max_iterations` field — equivalent correctness to declared cycles, manual termination [synthesis-pipeline-technical-design.md](/mnt/user-data/uploads/synthesis-pipeline-technical-design.md).

### Memory and knowledge (Cluster C)

The pipeline distinguishes two tiers: a substrate-native main-agent memory (`MEMORY.md`) and a per-sub-agent memory layered as a file-system convention at `.memories/agents/<name>/` [synthesis-pipeline-technical-design.md](/mnt/user-data/uploads/synthesis-pipeline-technical-design.md). The two tiers serve different purposes — knowledge skills carry curated taxonomies and rubrics that rarely change; sub-agent memories accumulate runtime observations across runs [synthesis-pipeline-technical-design.md](/mnt/user-data/uploads/synthesis-pipeline-technical-design.md). The recommended authoring order is knowledge skills first, agent definitions second, sub-agent memories accumulating organically through real runs without pre-population [synthesis-pipeline-technical-design.md](/mnt/user-data/uploads/synthesis-pipeline-technical-design.md).

### Design discipline (Cluster D)

The technical-designer skill mandates several gates before Design Doc creation: a Standards Identification Gate (explicit/implicit standards classification with adopted/noted QA mechanisms), an Existing Code Investigation phase (with similar-functionality search and reuse-vs-new criteria), an Agreement Checklist marked Most Important, and an Implementation Approach decision per the implementation-approach skill's Phase 1-4 [technical-designer.md](/mnt/user-data/uploads/technical-designer.md). The Fact Disposition Table is the single mechanism that binds existing-behavior facts to the design [technical-designer.md](/mnt/user-data/uploads/technical-designer.md). ADRs include decisions, rationale, and principled guidelines, and exclude schedules and specific code [technical-designer.md](/mnt/user-data/uploads/technical-designer.md). ADR option comparison requires a minimum of three options [technical-designer.md](/mnt/user-data/uploads/technical-designer.md) — this rule aligns conceptually with the synthesis pipeline's three-option substrate enumeration discipline.

### Verification (Cluster E — cross-source bridge)

Both source documents converge on the early-verification-point discipline [technical-designer.md](/mnt/user-data/uploads/technical-designer.md). For replacements or modifications, the early verification point must be an output comparison of at least one representative case [technical-designer.md](/mnt/user-data/uploads/technical-designer.md). The output comparison method specifies identical input, expected output fields and format, and how to diff [technical-designer.md](/mnt/user-data/uploads/technical-designer.md). This run is itself the early verification point's instance — the §7.4 vertical-slice gate's first execution against real source content.

## Decisions

### D-0001: Substrate choice — Claude Code primitives

**Class:** Architectural (one-way) | **Blast radius:** Tenant | **Wardley:** Product
**Recommendation:** `native` (Claude Code primitives only) — see [ADR-001](adrs/adr-001-substrate-choice.example.md)

The corpus is grounded entirely in Claude Code primitives, with LangGraph, Temporal, and AWS Step Functions explicitly named as out-of-scope alternatives [synthesis-pipeline-technical-design.md](/mnt/user-data/uploads/synthesis-pipeline-technical-design.md). Native realization is direct; substrate change would be 16 effort-weeks for properties (deterministic replay, declared cycles) the corpus has already accepted as out-of-scope.

### D-0002: Memory architecture — two-tier (orchestrator + per-sub-agent)

**Class:** Architectural (two-way) | **Blast radius:** Service | **Wardley:** Custom
**Recommendation:** `native` (two-tier engineering proposal) — see [ADR-002](adrs/adr-002-memory-architecture.example.md)
**Risk surfaced:** This decision rests on a single-sourced claim flagged 🔶 engineering proposal. See Limitations.

The corpus proposes layering per-sub-agent memory as a file-system convention because Claude Code's documented memory system is main-agent oriented [synthesis-pipeline-technical-design.md](/mnt/user-data/uploads/synthesis-pipeline-technical-design.md). The convention is two-way reversible — if it doesn't work, single-tier MEMORY.md remains a viable fallback at lower implementation cost.

### D-0003: Verification regime — vertical-slice early verification gate

**Class:** Architectural (one-way) | **Blast radius:** Tenant | **Wardley:** Product
**Recommendation:** `native` (vertical-slice gate) — see [ADR-003](adrs/adr-003-verification-regime.example.md)

Both source documents converge here [technical-designer.md](/mnt/user-data/uploads/technical-designer.md), [synthesis-pipeline-technical-design.md](/mnt/user-data/uploads/synthesis-pipeline-technical-design.md). The output comparison method is the binding mechanism; reference artifacts captured per the gate's success criteria become the smoke-run baseline for future runs [technical-designer.md](/mnt/user-data/uploads/technical-designer.md). Adapter (per-phase incremental verification) is non-viable because per-phase isolation cannot reveal substrate-level integration failures — exactly the failure mode the gate is designed to catch.

### D-0004: Recursion safety — hard rule with defense-in-depth

**Class:** Architectural (one-way) | **Blast radius:** Tenant | **Wardley:** Commodity
**Recommendation:** `native` (hard rule, orchestrator + agent both check) — see [ADR-004](adrs/adr-004-recursion-safety.example.md)

The corpus states the input scan is `output/**/*.md` minus `output/synthesis-*/**` as a hard rule [synthesis-pipeline-technical-design.md](/mnt/user-data/uploads/synthesis-pipeline-technical-design.md). Adapter (soft rule via naming convention) is non-viable because the failure mode — silent corpus pollution via re-ingestion — is irreversible by the time it's noticed. Defense-in-depth costs ~0.5 effort-weeks; the irreversibility cost of getting this wrong is significant.

### D-0005: User confirmation — required AskUserQuestion gate

**Class:** Architectural (one-way) | **Blast radius:** Tenant | **Wardley:** Product
**Recommendation:** `native` (required AskUserQuestion gate with three concurrent questions) — see [ADR-005](adrs/adr-005-confirmation-gate.example.md)

The Confirmation Gate is a required interrupt before Phase 1 with three concurrent questions covering input set, target substrate, and hard constraints [synthesis-pipeline-technical-design.md](/mnt/user-data/uploads/synthesis-pipeline-technical-design.md). Cancellation is dismissal-with-empty-answers, exiting cleanly without allocating a run-id [synthesis-pipeline-technical-design.md](/mnt/user-data/uploads/synthesis-pipeline-technical-design.md). Adapter (configuration file with prompt-on-missing) is viable but introduces UX ambiguity around cancellation that the corpus explicitly resolves.

## Constraints Honored

The run manifest declared `hard_constraints: []`. No hard constraints were specified by the user. All five decision recommendations are unconstrained by user-stated requirements; were a constraint such as `vendor-locked:microsoft` or `compliance:SOC2` added in a future run, the substrate phase would re-evaluate viability flags accordingly per the substrate-translation-knowledge skill's hard-constraint-downgrade discipline.

## Limitations

This synthesis surfaces two single-sourced claims that the source documents themselves flagged as carrying uncertainty. Each is preserved here transparently rather than smoothed over:

| Claim | Verdict | Confidence | Source flag | Implication |
|---|---|---|---|---|
| **C-0014** — User-defined agent file-system path (`/mnt/user-config/.claude/agents/<name>.md`) | `single_sourced` | medium | ⚠️ "Documented, not locally verified" | The path convention should be confirmed against the production tenant's Claude Code documentation before deployment. |
| **C-0021** — Sub-agents lack a native auto-loaded memory file (informs D-0002) | `single_sourced` | medium | 🔶 "Engineering proposal — no precedent" | The two-tier memory architecture is novel for this substrate. The two-way reversibility of D-0002 mitigates the risk; if the convention proves unmaintainable, single-tier fallback is available. |

The corpus contains no `unverifiable` or `contradicted` claims. The 51-of-53 verified rate (96%) reflects the corpus's structural property: it consists of two internal-audit-type documents that explicitly assert their own discipline. A more diverse corpus (mixing vendor whitepapers, regulator publications, and community blogs) would be expected to produce more `single_sourced`, `unverifiable`, and `contradicted` verdicts.

This run is the §7.4 vertical-slice early verification gate's first execution against real source content. Its passage validates the substrate-level invariants but does not validate Phases 4-6 of the pipeline against more demanding corpora — that is acceptance work for a future run.

## Sources

| File | Type | Provenance | Claims |
|---|---|---|---|
| [`/mnt/user-data/uploads/technical-designer.md`](/mnt/user-data/uploads/technical-designer.md) | internal_audit | internal | 26 |
| [`/mnt/user-data/uploads/synthesis-pipeline-technical-design.md`](/mnt/user-data/uploads/synthesis-pipeline-technical-design.md) | internal_audit | internal | 27 |

Full claim-to-source mapping is in [`citations.md`](citations.md). Three-option substrate enumerations for each decision are in [`substrate-options.md`](substrate-options.md).
