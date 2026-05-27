---
id: ADR-0065
version: 1.0.1
status: Accepted
generated: 2026-05-26
generated_by: design-composer
supersedes: []
adrs_inherited:
  - {id: ADR-0017, version: 1.0.0}
applies_to:
  - pipeline-design-time-discipline-r1
  - all-future-features-introducing-new-domain-concepts
template_format: per KB-documentation-criteria ADR template v1.0
change_summary: Establishes the Skill-Coverage Decision discipline — a hybrid W/H/A trifecta mandate (structural mandate for new-skill proposals; substance heuristic for existing-skill and no-skill-warranted rows) — embedded as a section in `synthesis.md`, fired at Synthesis or Design for every new domain concept a feature introduces.
---

# ADR-0065: Skill-Coverage Decision Discipline (W/H/A Trifecta Hybrid)

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

## Update History

| Version | Date | Change | Driver |
|---|---|---|---|
| 1.0.0 | 2026-05-26 | Initial ADR authored by `design-composer` at Design Composition. | R2a Design Composition stage. |
| 1.0.1 | 2026-05-26 | Clause 2 + Architecture Impact row + Implementation Guidance + Related Information: corrected stale references to "shared-document-reviewer invocation 2 on synthesis.md" — per inherited ADR-0017, invocation 2 reviews the PRD; invocation 3 (Blueprint review) is the existing reviewer pass that touches the substance-bearing artifact via the Blueprint's Eat-Own-Dogfood reference to synthesis.md. Editorial in-place edit per ADR-0005 (no supersession of ADR-0017 required). | Audit finding I-AA-002 (architecture-audit cycle 1); reconciliation cycle 1 dispatch to `design-composer`. |

## Context

When a feature introduces a new domain concept (a noun-phrase not previously named in the project's KB / skill inventory), three failure modes have historically occurred:

1. **The concept is introduced without skill coverage** — no existing skill teaches it, and no new skill is proposed. Future feature runs encounter the concept downstream without authoritative reference.
2. **A new skill is proposed without substance** — the proposal lists the skill's name but does not articulate why it exists, how agents would use it, or what anti-patterns it prevents. The skill becomes a placeholder.
3. **An existing skill is named as covering the concept, without evidence** — the cell-population happens but the substance of the coverage claim is never tested.

FR-7 of `pipeline-design-time-discipline-r1` closes these failure modes by requiring a skill-coverage decision for every new domain concept. The decision is one of:

- **(a)** Name the existing skill that covers it (with positive evidence of coverage).
- **(b)** Propose a new skill with a W/H/A trifecta justification (Why this skill exists / How agents use it / Anti-patterns to avoid).
- **(c)** Record "no skill warranted" with explicit rationale.

The contract surface decomposes into three questions:

1. **Where does the decision section live?** Standalone file, embedded in synthesis.md, embedded in the Blueprint, or embedded in cc-design.md?
2. **Is W/H/A enforced structurally (every row populates three labelled cells) or substantively (judge by whether the cell reads as actually answering W/H/A)?**
3. **How is FR-7 dogfooded for the run that establishes the discipline?**

T-003 verified across 6 platforms (Anthropic Agent Skills, LangChain/LangGraph, OpenAI Assistants/Agents SDK, Microsoft Agent Framework, CrewAI, Semantic Kernel) that W/H/A substance is well-trodden community ground (C-0190, C-0192, C-0193, C-0194, C-0256). Critically, the 7-platform survey also confirms **0/6 surveyed platforms mandate the trifecta as a structured artifact** (C-0257) — codification-as-mandate is the novel and risky move.

FR-7 is the heaviest entity in the R2a synthesis graph at 23 claim back-pointers — this is the most consequential R2a architectural choice (synthesis §D-8). PRD §Product Policy explicitly codifies "substance over form" — a decision row is satisfactory iff its justification cell can be read as actually answering the W/H/A questions, not merely populating cells (prd-v1.md §Product Policy Decisions).

## Decision

The Skill-Coverage Decision discipline is hereby normative. Three normative clauses:

**Clause 1 — Artifact location: embedded section in `synthesis.md`.** The Skill-Coverage Decisions section is embedded in the feature run's `synthesis.md` (not a standalone file, not in the Blueprint, not in cc-design.md). The template for the section lives at `.claude/skills/KB-documentation-criteria/references/templates/skill-coverage-decisions-section-template.md`.

The section is **conditional** — present only when the feature introduces one or more new domain concepts; absent otherwise.

**Clause 2 — Hybrid W/H/A enforcement.** The trifecta is enforced as follows:

- **For rows where the decision is "(b) propose a new skill"** (`dogfood_decision: propose-new-skill`): the W/H/A trifecta is a **structural mandate**. The row MUST contain three labelled headings: `Why:` (the skill's purpose), `How:` (at least one downstream agent or stage that loads it), `Anti-patterns:` (at least one anti-pattern the skill prevents). Missing any of the three blocks Design Composition completion.
- **For rows where the decision is "(a) existing skill covers it"** (`dogfood_decision: existing-skill`): the substance heuristic governs. The row MUST contain the existing skill's path AND a positive-evidence string showing the coverage. No structural-trifecta requirement.
- **For rows where the decision is "(c) no skill warranted"** (`dogfood_decision: no-skill`): the substance heuristic governs. The row MUST contain an explicit rationale (one or more sentences) for why no skill is needed. No structural-trifecta requirement.

Substance review (`shared-document-reviewer` invocation 3 — Blueprint review, which cites the synthesis.md Skill-Coverage Decisions section in its Eat-Own-Dogfood content) is the human's responsibility for (a) and (c). Per inherited ADR-0017, invocation 2 reviews the PRD; invocation 3 is the existing reviewer pass that touches the substance-bearing artifact via the Blueprint's reference and the bundled deliverable check. For (b), the structural mandate is the machine-checkable floor; substance is additionally reviewed at invocation 3.

**Clause 3 — Dogfood for this run.** R2a introduces six new domain concepts (design-realization audit, agent-roster impact matrix, skill-coverage decision check, Principle 9 active reframing, Blocks-X marker grammar, agent-roster matrix-missing audit rule). Per Clause 1, the embedded section is authored in this run's `synthesis.md` with one decision row per concept, each resolving per the per-concept rationale in the Blueprint's Eat-Own-Dogfood section. All six resolve to option (a) — covered by existing skills.

## Decision Details

| Detail | Specification |
|---|---|
| **Why now** | FR-7 is the heaviest decision in R2a (23 back-pointers); without a normative contract, the discipline drifts. Six R2a domain concepts must be dogfooded in this run to validate the contract before imposing on future runs. |
| **Why this** | Hybrid concentrates structural mandate where it has the highest review-cost ROI (new-skill proposals — they introduce ongoing maintenance debt) and preserves substance for the well-trodden cases (existing-skill coverage; no-skill rationale). Re-affirms parent's D-8 lean with graph-structural-novelty observation. Embedding in synthesis.md keeps decisions co-located with the synthesis that surfaces the concepts. |
| **Known unknowns** | The substance heuristic is human-judgment-bound for (a) and (c) rows; review consistency across runs depends on `shared-document-reviewer` calibration. The first ~3 feature runs that introduce new concepts are the calibration corpus. |
| **Kill criteria** | If the substance heuristic produces inconsistent review outcomes across runs (>30% inter-reviewer disagreement on the same row sustained across N≥3 runs), the discipline is re-litigated — the next move would be to extend the structural mandate to (a) and (c) rows. If (b) proposals routinely populate the three headings with empty content (presence-not-substance failure), the structural mandate itself is re-evaluated against T-003's anti-ritualism warning. |

## Rationale

Five rationale strands:

1. **The 6-platform W/H/A substance convergence (C-0190, C-0192, C-0193, C-0194, C-0256) supports the trifecta as the *substance*.** All surveyed platforms encode some form of why-how-anti-pattern reasoning into their skill discipline. The trifecta is not novel — what's novel is codifying it as a per-decision artifact.

2. **The 7-platform 0/6 mandate-as-artifact finding (C-0257) warns against universal structural mandate.** If 0 of 6 platforms found the structural mandate worth their cost, mandating it universally risks the anti-ritualism failure mode: three filled headings with empty content. Hybrid concentrates the structural cost where it pays for itself (new-skill proposals).

3. **New-skill proposals are the highest review-cost surface.** A new skill introduces ongoing maintenance debt (the skill must be maintained as the project evolves; its content can rot; future authors inherit it). Structural mandate at this surface is the audit anchor that prevents low-substance proposals from accumulating debt.

4. **Embedding in synthesis.md serves D-5's predicate.** The FR-6 advisory predicate (per ADR-0064 Clause 3) reads the Skill-Coverage Decisions section to evaluate trigger condition 4. Embedding in synthesis.md (which is authored before Design Composition) ensures the table is available when the predicate fires. Standalone file or Blueprint-embedded would delay availability.

5. **Two-way reversibility.** If substance-heuristic enforcement later requires a more visible artifact, the embedded section can be promoted to standalone with mechanical migration. The reverse path (standalone → embedded) is awkward because authors would have to be retrained.

## Options Considered

**Option A — Full structural mandate universally (REJECTED).** Every row populates three labelled cells regardless of decision type. 0/6 surveyed platforms mandate this (C-0257) — explicit anti-ritualism trade-off. Presence-not-substance: three filled headings can be empty of meaningful content and still pass the gate, recreating the exact failure mode FR-7 is designed to prevent.

**Option B — Principle/substance heuristic only, no structural mandate anywhere (REJECTED).** Loses the audit anchor for new-skill proposals where structure pays for itself. The new-skill-proposal surface is the highest review-cost ROI; abandoning structure there sacrifices a useful audit anchor for marginal additional substance-preservation.

**Option C — Standalone `skill-coverage-decisions.md` file (REJECTED).** Greenfield artifact convention with no precedent (researcher C-0076 confirmed zero existing `skill-coverage*` files). Higher irreversibility once authors are trained on it. Adds a new artifact to the feature-directory shape competing with the queued R2b's posture of minimizing post-ship rituals.

**Option D — Embed in Blueprint or cc-design.md (REJECTED).** Loses synthesis-stage locality — concepts surface during Synthesis but resolution happens later. Doesn't serve the FR-6 advisory predicate (which needs the table at the moment the FR-6 matrix-mandatory check fires, when synthesis.md has already been authored).

**Option E (CHOSEN) — Hybrid mandate + substance + embed-in-synthesis.md.** Concentrates structural cost where it pays; preserves substance where it doesn't; gives D-5's predicate the table at the right time. Re-affirms framer lean. Recommended.

## Consequences

**Positive:**

- New-skill proposals carry a structural audit anchor (W/H/A headings) that prevents low-substance proposals from accumulating maintenance debt.
- Existing-skill and no-skill-warranted rows are not over-engineered with structural mandates that 0/6 platforms found worth the cost.
- The FR-6 advisory predicate has the Skill-Coverage Decisions table available at the right moment (synthesis.md is authored before Design Composition).
- Two-way reversible: section can be promoted to standalone if future review experience warrants it.
- Dogfooded on this run: six decisions for six new R2a concepts validate the contract on a real run.

**Negative / cost-bearing:**

- Substance review for (a) and (c) rows is human-judgment-bound; inter-reviewer consistency depends on `shared-document-reviewer` calibration.
- Embedded sections in synthesis.md grow the file's size; large runs with many new concepts will produce long sections.
- The hybrid is a more-complex rule than option A or B; reviewer training cost is higher.

**Neutral / observability:**

- The section is conditional — runs that introduce no new concepts produce no section, no review cost.

## Architecture Impact

| Layer / artifact | Impact |
|---|---|
| `.claude/skills/KB-documentation-criteria/references/templates/skill-coverage-decisions-section-template.md` | New template (the section's canonical shape; encodes the hybrid rule). |
| `.claude/agents/synth-synthesizer.md` | Synthesis-side trigger: when synthesis identifies a new domain concept, emit a Skill-Coverage Decisions section row. |
| `.claude/agents/design-composer.md` | Blueprint composition reads each row; blocks completion if a (b) row is missing required W/H/A headings (per AC-FR-7-b). Substance review for (a) and (c) is the `shared-document-reviewer` invocation 3 (Blueprint review) responsibility, via the Blueprint's Eat-Own-Dogfood reference to the synthesis.md section. |
| `.claude/skills/KB-cc-design/references/principles.md` | Principle 2's neighborhood extended with the W/H/A rubric and substance-not-presence heuristic discipline. |
| `working/feature/<slug>/synthesis.md` | New conditional embedded section "Skill-Coverage Decisions" with one decision row per new domain concept. |
| `.claude/skills/auditing-subagents/scripts/check_feature_touch_predicate.py` (per ADR-0064) | Reads the Skill-Coverage Decisions section to evaluate trigger condition 4. Depends on the section's stable shape per this ADR's template. |

## Implementation Guidance

Principle-only. Procedures live in the Plan.

- **The template MUST surface the per-row decision-type-conditional shape in its header.** Authors should see "if propose-new-skill → fill Why/How/Anti-patterns headings; if existing-skill → fill skill path + evidence; if no-skill → fill rationale" from the template alone — not from external reference.
- **Substance review for (a) and (c) rows MUST be explicit, not implicit.** `shared-document-reviewer` invocation 3 (Blueprint review) reviews substance via the Blueprint's Eat-Own-Dogfood reference to the synthesis.md Skill-Coverage Decisions section; its rubric is "does this row's justification actually answer the coverage claim?" The reviewer's verdict block records the substance judgment per-row.
- **(b) structural mandate fails closed.** If a `propose-new-skill` row is missing any of Why/How/Anti-patterns, Design Composition refuses to complete. The block fires regardless of how good the partial content is — structural completeness is the floor.
- **Eat-own-dogfood is non-negotiable for the run establishing the discipline.** R2a's `synthesis.md` MUST contain six decision rows (one per new concept) before the run can ship. Compliance is verified at Design Composition close and again at packaging time.
- **Future tuning depends on logged inter-reviewer disagreement.** If `shared-document-reviewer` invocations disagree on a (a) or (c) row's substance, the disagreement is logged in the issues-ledger (per ADR-0008) with the row identifier. The ledger is the corpus future kill-criteria evaluation reads.

## Related Information

**Cross-references:**

- **FR-7** (`pipeline-design-time-discipline-r1` PRD) — the mechanism this ADR canonicalizes.
- **AC-FR-7-a / -b / -c** — the acceptance criteria this discipline satisfies.
- **ADR-0017** — `shared-document-reviewer` invocation 3 reviews the Blueprint; the Blueprint's Eat-Own-Dogfood content cites the `synthesis.md` Skill-Coverage Decisions section, bringing it within reviewer scope at invocation 3. (Invocation 2 reviews the PRD per ADR-0017.)
- **ADR-0064** (sibling, this run) — agent-roster impact matrix contract; trigger condition 4 reads ADR-0065's Skill-Coverage Decisions section.
- **Synthesis decision D-8** — the hybrid mandate-vs-substance decision this discipline embodies.
- **Synthesis decision D-R2a-4** — the artifact-location decision (embed in synthesis.md) this discipline embodies.

**Predecessor / inheritance:**

- T-003 prior-art corpus (56 inherited claims) — well-trodden W/H/A community ground; 0/6 mandate-as-artifact finding.
- The R2a run's own six new domain concepts (per Blueprint §Eat-Own-Dogfood) are the first dogfood instance.
