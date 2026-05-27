# Research Plan Template

Canonical structure for `research-plan.md`, the Discovery Planning stage's output. Per ADR-0021, the Research Plan documents the KB-and-ADR gap analysis that justifies any external research; it also bounds codebase research scope for `discovery-codebase-researcher`.

`discovery-plan-author` authors this artifact. Each section below is required (Gate 0 structural check); the per-section content rules are in `../disciplines/discovery-planning.md`.

## Contents

- [ ] Feature reference (PRD path, version, gate state)
- [ ] Information needs inventory
- [ ] Codebase research scope
- [ ] External research topics (may be empty if KBs answer all open questions)
- [ ] Topics explicitly NOT researched (KB/ADR-resolved)
- [ ] Estimated effort
- [ ] Open questions for human resolution

---

## Feature reference

Stable cross-references for downstream consumers:

- **Feature slug**: `<slug>`
- **PRD path**: `working/feature/<slug>/prd-v<N>.md`
- **PRD version**: `<N>`
- **PRD gate state**: approved at `<ISO timestamp>` (PRD Approval Gate)
- **Inherited ADRs in scope**: `[ADR-<NNNN>, ...]` (those that constrain or inform research scope)
- **Applicable KBs**: `[KB-<name>, ...]` (those whose principles or patterns touch the feature's layer scope)

## Information needs inventory

Every downstream stage (Synthesis, per-layer Design, Plan, etc.) reads upstream artifacts to make decisions. The Research Plan inventories the information those stages will need.

For each information need, document:

- **Need ID**: `IN-<NNN>` (zero-padded; sequential).
- **Description**: One sentence — the question the downstream stage will need answered.
- **Downstream consumer(s)**: Which sub-agent(s) need this — e.g., "design-backend (transactional outbox decision)" or "design-database (index strategy for ORDERS table)".
- **Disposition**: One of:
  - `covered-by-KB:<KB-name>:<reference-file>` — the existing KB already answers this. No research needed.
  - `covered-by-ADR:<ADR-id>` — an inherited ADR establishes the answer. No research needed.
  - `codebase-topic` — the answer is "what does our codebase currently do?" Routed to `discovery-codebase-researcher`.
  - `designer-general-knowledge` — well-trodden community knowledge a competent designer applies with documented rationale in the per-layer Design section (e.g., conventional K8s probe parameters, standard Docker build-arg patterns, REST status code semantics). No research needed. Per `../disciplines/discovery-planning.md`, this disposition commits the downstream designer to explicit rationale in their design subsection — the designer's prose carries authority.
  - `external-research-topic:<topic-id>` — a documented KB gap; routed to `discovery-external-researcher` as topic `T-<NNN>`.
- **Justification (only for external-research-topic)**: Per ADR-0021, every external topic carries explicit justification: which KB(s) you checked, what they cover, what they DO NOT cover, why the gap is novel for this feature AND why `designer-general-knowledge` doesn't apply (i.e., why this isn't a question a competent designer would just know).

## Codebase research scope

This section is the contract with `discovery-codebase-researcher`. The researcher's `research_plan_path` input is this file; the researcher's `output_json_path` is `codebase-analysis.json`.

### Touch points

Specific files, modules, or services likely in scope for this feature. From the PRD's Layer Scope + any explicit mentions in user stories. Format:

- `<path>` — `<why this is a touch point>`

The researcher uses these as starting points for graph traversal.

### Blast-radius questions

What's downstream of each touch point? Per ADR-0018, blast-radius analysis is part of codebase analysis. The questions to ask:

- Which components import / call into the touch points? (1-hop dependents)
- Which components are reachable from there within 3 hops?
- Which test files cover the touch points and their dependents?

The researcher records these in `codebase-analysis.json`'s `blast_radius` section.

### Convention discovery

What existing patterns must the design respect? Per-layer convention discovery (file-naming, module layout, error-handling idioms, logging conventions, testing framework). These constrain per-layer Designers.

### Specific queries or grep targets (optional)

If the topic is precise enough to specify, list the `grep` / Glob pattern or the serena symbol-query (e.g. `find_referencing_symbols('OrderService.cancel')`) the researcher should run. Otherwise, the researcher chooses based on the touch points.

## External research topics

Per ADR-0021, external research is conditional on documented KB gaps. The default external-research budget is **6 topics maximum** (override via `--max-external-research-topics N`).

For each topic:

- **Topic ID**: `T-<NNN>` (zero-padded; sequential).
- **Name**: Short label.
- **Research question**: One-sentence question.
- **KB gap justification**: Which KB(s) were checked; what they cover; what specifically they DO NOT cover; why this is novel.
- **Acceptance criteria**: What makes this topic "done"? Example: "names 3 reputable sources; identifies 2 trade-offs; quotes specific version numbers or limits where applicable."
- **Source constraints**: Authoritative sources only. The Plan may specify "official documentation only" / "RFCs + standards bodies" / "peer-reviewed papers" / "reputable engineering blogs from companies operating the tech at scale" — depending on the topic.

If there are no external research topics: state explicitly "No external research authorized; all information needs covered by KBs and ADRs." This is a positive design state, not a gap.

## Topics explicitly NOT researched

Anti-scope-creep mechanism. For each information need with disposition `covered-by-KB` or `covered-by-ADR`, list:

- **Need ID** (from inventory above).
- **Resolving artifact**: KB reference file OR ADR ID + version.
- **Resolution summary**: 1-2 sentences explaining what the artifact says.

This section prevents future revisits of the same question.

## Estimated effort

- **Codebase research effort**: small / medium / large (informs scheduling).
- **External research topic count**: `<N>` of `<max>` budget.
- **Estimated wall-clock**: optional; bounded by external-research-parallelism (up to 6 in parallel) + codebase-research single-instance time.

## Open questions for human resolution

Anything the Research Plan can't resolve without input. Examples:

- Genuinely ambiguous PRD passages.
- Topic ideas that may or may not be worth researching depending on user preference.
- Budget questions (e.g., "Should we research vendor X's pricing vs. vendor Y's, given the PRD doesn't constrain vendor choice?").

These surface at the Research Plan Approval Gate. User answers update the Plan before research begins.

---

## Authoring rules (for `discovery-plan-author`)

1. **KB-and-ADR-first**: every information need MUST be checked against existing KBs and ADRs before being assigned an external-research topic. Per ADR-0021.
2. **No external topic without justification**: each `T-<NNN>` includes explicit KB gap reasoning.
3. **External topic budget**: 6 maximum, unless overridden.
4. **Acceptance criteria are concrete**: "names 3 sources" / "identifies 2 trade-offs" — not "thoroughly investigates X".
5. **Codebase research scope is non-empty**: even small features benefit from blast-radius preview. The Research Plan always activates `discovery-codebase-researcher`.
6. **Section order matters for review**: human reviewers at the Research Plan Approval Gate scan top-down; lead with what's confirmed (Information needs + dispositions), then the proposed research (Codebase + External), then the explicit exclusions.

---

## Related artifacts

- **Discovery Planning discipline**: `references/disciplines/discovery-planning.md` (operational rules for `discovery-plan-author`).
- **PRD template**: `references/templates/prd-template.md` (the upstream input).
- **codebase-analysis.json schema**: defined in KB-codebase-research (the downstream consumer of the Codebase research scope section).
- **Discovery Research fan-out**: per ADR-0021, runs `discovery-codebase-researcher` + N × `discovery-external-researcher` invoked once per topic.
