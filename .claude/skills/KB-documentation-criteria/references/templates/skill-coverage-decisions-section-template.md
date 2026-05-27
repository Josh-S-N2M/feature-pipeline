---
id: skill-coverage-decisions-section-template
version: 1.0.0
status: template
template_for: skill-coverage-decisions-section
derived_from: ADR-0065
generated_by: synth-synthesizer
embeds_in: synthesis.md
---

# Skill-Coverage Decisions — Section Template

## Contents

- [Purpose and embed context](#purpose-and-embed-context)
- [When to author this section](#when-to-author-this-section)
- [Three resolution types](#three-resolution-types)
- [Row schema](#row-schema)
- [Authoring discipline](#authoring-discipline)
- [Review path](#review-path)
- [Severity calibration](#severity-calibration)
- [Worked example](#worked-example)
- [Cross-references](#cross-references)
- [Update history](#update-history)

---

## Purpose and embed context

The `## Skill-Coverage Decisions` section is a **conditional embedded section** in `working/feature/<slug>/synthesis.md`. It records one decision row for every new domain concept the feature introduces, answering the question: does the project's skill inventory cover this concept, should a new skill be proposed, or is no skill warranted?

The governing contract is **ADR-0065** (Skill-Coverage Decision Discipline — W/H/A Trifecta Hybrid). Three normative clauses:

- **Clause 1** — The section is embedded in `synthesis.md`, not a standalone file, not in the Blueprint, not in `cc-design.md`. The template for the section shape is this file.
- **Clause 2** — Hybrid W/H/A enforcement: structural mandate for `propose-new-skill` rows; substance heuristic for `existing-skill` and `no-skill-warranted` rows.
- **Clause 3** — Dogfood: the run that establishes the discipline must apply it to its own new domain concepts.

**Location in synthesis.md:** Place the `## Skill-Coverage Decisions` section after `## Eat-Own-Dogfood Deliverables` and before `## Open Items Carried to Design Composition`. The section is omitted entirely when the feature introduces zero new domain concepts.

**Key coupling (per ADR-0065 Clause 1 + ADR-0064 Clause 3):** The FR-6 advisory predicate reads this section at Design Composition to evaluate trigger condition 4 ("new domain concept names an existing agent as a downstream consumer"). The section must be authored and present in `synthesis.md` before Design Composition begins.

---

## When to author this section

The section is **mandatory** whenever the feature introduces one or more new domain concepts — i.e., the feature's PRD or design surfaces a new conceptual primitive not previously named in the project's KB / skill inventory.

**Trigger detection per ADR-0065 Clause 1:** A domain concept qualifies as "new" when it appears in one or more of:

- The PRD's Glossary (a term defined there that has no prior cross-reference in an existing skill)
- The Blueprint's Component table (a component whose purpose is not captured by an existing skill)
- Any design subsection that introduces a named mechanism, artifact type, or discipline that downstream agents or skill authors may need to learn from a KB

**Scope of "new."** Incremental additions to a well-covered concept (e.g., adding a new audit rule to an existing audit skill family) are NOT new domain concepts — they are extensions of existing coverage. Only genuinely novel conceptual primitives require a Skill-Coverage Decision row.

**When zero new concepts:** Omit the section entirely. Do not author an empty table or a "no new concepts" placeholder — absence of the section is the correct signal.

---

## Three resolution types

For each new domain concept, choose exactly one resolution type.

### (a) existing-skill

The concept is already covered by an existing skill in `.claude/skills/`. Name the skill and provide a positive-evidence string showing the coverage.

Per ADR-0065 Clause 2: the substance heuristic governs. The row MUST contain the existing skill's path AND a positive-evidence string. A citation without evidence (e.g., "KB-cc-design covers it" with no supporting detail) fails the substance heuristic.

**Author format:**

```
Resolution type:   (a) existing-skill
Covering skill:    .claude/skills/<skill-name>/SKILL.md  (or the specific reference file)
Positive evidence: <one to two sentences explaining what section/principle/rule of the
                   cited skill already covers this concept — be specific enough that a
                   reviewer can verify the claim without loading the full skill>
```

### (b) propose-new-skill

No existing skill credibly covers the concept. A new skill should be authored in a future (or current) feature run.

Per ADR-0065 Clause 2: the W/H/A trifecta is a **structural mandate** for this row type. All three labelled headings MUST be present and non-empty. Missing any one of the three blocks causes Design Composition to refuse completion (the mandate fails closed regardless of the quality of the partial content).

**Author format:**

```
Resolution type:   (b) propose-new-skill
Proposed skill:    <proposed skill directory name, e.g., KB-<domain-name>>

Why:   <The skill's purpose — what conceptual territory it covers and why that
        territory is not already served by an existing skill. Must be specific enough
        to distinguish this skill from neighbors.>

How:   <At least one downstream agent or pipeline stage that would load this skill,
        and what decision or action the skill would inform. Naming the loading agent
        is the minimum bar.>

Anti-patterns: <At least one anti-pattern or failure mode the skill would prevent.
                "Without this skill, authors would..." is a useful frame.>
```

The future feature run that authors the new skill is responsible for the full SKILL.md content. This row is the authorization and justification stub, not the skill itself.

### (c) no-skill-warranted

The concept is real but does not benefit from a dedicated skill — e.g., it is operational discipline already captured in an agent's prompt, a purely run-time artifact that agents produce rather than consume, or a concept so narrow that it would be maintained in one place anyway.

Per ADR-0065 Clause 2: the substance heuristic governs. The row MUST contain an explicit rationale (one or more sentences). "Not needed" without explanation fails the heuristic.

**Author format:**

```
Resolution type:   (c) no-skill-warranted
Rationale:         <One or more sentences explaining why no skill is needed. Useful frames:
                   "This concept is operational discipline, not reusable knowledge";
                   "This concept is produced by agents, not consumed as reference material";
                   "This concept is already fully specified in <specific ADR/contract> and
                   a skill would duplicate that source of truth.">
```

---

## Row schema

The canonical table shape for the embedded section:

```markdown
## Skill-Coverage Decisions

*Per ADR-0065 Clause 1; <review posture summary, e.g., "substance-heuristic review applies (all N rows resolve to existing-skill)">.*

For each new domain concept this feature introduces, one of:
- **(a) existing-skill** — name the existing skill that covers the concept + positive-evidence string
- **(b) propose-new-skill** — W/H/A trifecta (Why this skill exists; How agents use it; Anti-patterns it defends against)
- **(c) no-skill-warranted** — rationale for why no skill coverage is needed

| Domain concept | Resolution type | Covering skill (a) / Proposed skill name (b) / Rationale (c) | Positive evidence |
|---|---|---|---|
| <concept name> | (a) existing-skill | <skill path> | <positive-evidence string> |
| <concept name> | (b) propose-new-skill | <proposed-skill-name> — W/H/A in cell or below table | (see W/H/A block below) |
| <concept name> | (c) no-skill-warranted | <rationale> | — |
```

**For (b) rows,** if the W/H/A trifecta is too long for a table cell, place the three labelled blocks immediately below the table, keyed to the concept name. The table cell then contains the proposed skill name plus a pointer such as "(W/H/A below)".

**Positive evidence column for (b) rows:** Use "— (see W/H/A block)" or similar pointer. Do not leave the cell blank; blank cells fail the structural mandate check.

---

## Authoring discipline

Six authoring rules, derived from ADR-0065 Clauses 1 and 2:

1. **Default to (a) when an existing skill credibly covers the concept.** Resolution type (b) is for genuinely new territory; type (a) with a strong positive-evidence string is preferable to a low-substance (b) proposal.

2. **Type (b) requires all three W/H/A blocks — no partial compliance.** The structural mandate fails closed: one missing block is the same as all three missing. "Why:" without "How:" and "Anti-patterns:" fails the gate.

3. **Type (c) requires an explicit rationale sentence, not a label.** "No skill warranted" with no further explanation is a substance-heuristic failure. Write the sentence.

4. **The synth-synthesizer authors this section during synthesis composition.** The section is available to `design-composer` at Design Composition. If a concept surfaces at Design Composition that was missed at Synthesis, the `design-composer` backfills the row and notes it in the synthesis.md Update History.

5. **One row per new domain concept, not per feature requirement.** FR-7 may introduce one or several new concepts; each concept gets its own row. Do not aggregate concepts into a single row.

6. **The section is conditional — present only when the feature introduces one or more new domain concepts.** A run with zero new domain concepts has no section. The section header itself (`## Skill-Coverage Decisions`) MUST NOT be present in a run with zero new concepts.

---

## Review path

Per ADR-0065 Clause 2, the review path for this section has two tiers:

**All rows — substance heuristic review** at `shared-document-reviewer` invocation 3 (Blueprint review, per ADR-0017). The Blueprint's Eat-Own-Dogfood content cites the `synthesis.md` Skill-Coverage Decisions section, bringing it within reviewer scope at invocation 3. The reviewer's rubric is: "Does this row's justification cell actually answer the coverage claim?" Not: "Is the cell populated?" — presence is not substance.

**Type (b) rows — structural mandate check additionally.** Before or at Design Composition, `design-composer` verifies that every `propose-new-skill` row contains all three labelled headings (Why / How / Anti-patterns). This is a machine-checkable floor; the composer blocks on absence regardless of the partial content quality. Structural completeness is the precondition for the substance review that follows.

**Override logging.** If `design-composer` overrides a structural mandate failure (e.g., accepts a (b) row with only two of three headings), the override event is logged to `state-transitions.log` with `transition_name: TRIGGER_OVERRIDE` and a rationale. Overrides are surfaced at the inter-reviewer calibration corpus for future tuning.

---

## Severity calibration

Per ADR-0065 + `.claude/skills/KB-review-disciplines/references/severity-taxonomy.md`:

| Failure | Severity | Emitter |
|---|---|---|
| `## Skill-Coverage Decisions` section absent when feature introduces one or more new domain concepts | **MAJOR** | `design-composer` at Design Composition; SA-14 at packaging time |
| Type (b) row missing any of the three W/H/A headings (structural mandate violation) | **MAJOR** | `design-composer` at Design Composition (fails closed) |
| Type (a) row with vacuous positive evidence (e.g., "covered" with no supporting detail) | **MINOR** | `shared-document-reviewer` invocation 3 (substance heuristic flagged) |
| Type (c) row with vacuous rationale (e.g., "not needed" with no explanation) | **MINOR** | `shared-document-reviewer` invocation 3 (substance heuristic flagged) |
| Section present in a run with zero new domain concepts | **MINOR** | `shared-document-reviewer` invocation 3 (false positive section) |

Severity vocabulary follows the bridge table in `severity-taxonomy.md`. MAJOR maps to `important` in reviewer vocabulary and `blocking` in PV vocabulary by default. MINOR maps to `recommended` / `warning`.

---

## Worked example

This example shows three rows of different resolution types using realistic concepts from a hypothetical feature run that introduces: (1) a new "circuit-breaker timeout" concept in a reliability mechanism, (2) a new "agent-chain dependency graph" concept with no existing coverage, and (3) a "run-specific scratch artifact" concept that is operational only.

```markdown
## Skill-Coverage Decisions

*Per ADR-0065 Clause 1; mixed review: rows (a) and (c) use substance heuristic; row (b) uses structural mandate.*

For each new domain concept this feature introduces, one of:
- **(a) existing-skill** — name the existing skill that covers the concept + positive-evidence string
- **(b) propose-new-skill** — W/H/A trifecta (Why this skill exists; How agents use it; Anti-patterns it defends against)
- **(c) no-skill-warranted** — rationale for why no skill coverage is needed

| Domain concept | Resolution type | Covering skill (a) / Proposed skill name (b) / Rationale (c) | Positive evidence |
|---|---|---|---|
| circuit-breaker timeout | (a) existing-skill | `.claude/skills/KB-review-disciplines/references/severity-taxonomy.md` | The bridge table's BLOCKER / MAJOR / MINOR tiers + gate-refusal semantics are the canonical home for reliability-gate thresholds; the "blocking" PV vocabulary row is the relevant anchor. |
| agent-chain dependency graph | (b) propose-new-skill | KB-agent-chain-discipline | (W/H/A below) |
| run-specific scratch artifact | (c) no-skill-warranted | This concept is a transient output produced during execution and consumed immediately; it is not reusable reference material. No skill can improve authoring of something that does not persist across runs. | — |
```

**W/H/A block for "agent-chain dependency graph" (row b):**

```
Why:   No existing skill documents how to represent, audit, or validate the
       dependency ordering of agents invoked in a multi-stage pipeline chain.
       KB-cc-design covers per-agent reasoning configuration but not the
       cross-agent dependency graph shape or its invariants.

How:   design-composer loads this skill when authoring the Blueprint's
       Architecture Overview section; review-architecture-auditor loads it
       at Lens 4 (Design Realization) to verify that the plan's phase
       sequencing honors the declared agent dependencies.

Anti-patterns: Without this skill, plan authors sequence agent invocations
               by convention without declaring the dependency explicitly —
               resulting in silent inversion bugs when two agents that depend
               on the same intermediate artifact run in parallel.
```

The three worked rows illustrate: (a) a credible existing-skill citation with a specific section pointer; (b) the full structural mandate for a proposal, with W/H/A broken out below the table; (c) a one-sentence rationale that explains the "no skill warranted" judgment on its own terms.

---

## Cross-references

| Artifact | Relationship |
|---|---|
| `adrs/ADR-0065-skill-coverage-decision-discipline.md` | Governing contract. Hybrid mandate-substance framing is load-bearing; 23 claim back-pointers in R2a synthesis graph. |
| `.claude/skills/KB-cc-design/references/principles.md` Principle 2 | "Skill loading on-demand" — the principle that motivates recording whether a skill exists for a concept vs. loading everything always. |
| `.claude/skills/KB-review-disciplines/references/severity-taxonomy.md` | NFR-8 four-field finding shape (`rule`, `target`, `divergence`, `next_action`); severity bridge for MAJOR/MINOR emission. |
| `.claude/agents/synth-synthesizer.md` | Emitter of this section. When synthesis identifies a new domain concept, synth-synthesizer emits a row per ADR-0065 Clause 1. |
| `.claude/agents/design-composer.md` | Reviewer of (b) row structural mandate at Design Composition; blocks completion on missing W/H/A headings. |
| `working/feature/pipeline-design-time-discipline-r1/synthesis.md §Skill-Coverage Decisions` | Cycle-1 back-fill exemplar — 6 rows for R2a's own domain concepts; all resolve to type (a). Reference when authoring a run with only existing-skill rows. |

---

## Update history

| Version | Date | Change | Driver |
|---|---|---|---|
| 1.0.0 | 2026-05-27 | Initial template authored per FR-7 / AC-FR-7-a / AC-FR-7-b / AC-FR-7-c. Encodes ADR-0065 hybrid mandate-substance framing, three resolution types, row schema, authoring discipline, review path, severity calibration, and worked example. | T6.1 / Phase 6 / pipeline-design-time-discipline-r1 |
