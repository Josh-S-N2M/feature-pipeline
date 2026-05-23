# Discovery Planning Discipline

Operational rules for the Discovery Planning stage, authored by `discovery-plan-author`. Per ADR-0021, this stage is **KB-and-ADR-first**: before authorizing external research, the plan author maps every information need onto the existing knowledge corpus.

This discipline file complements `references/templates/research-plan-template.md` (the structural contract). The template says what sections must exist; this discipline says how each section is populated.

## Contents

- Core principle: KB-and-ADR-first
- Five-way disposition triage (the central rubric)
- When to choose `designer-general-knowledge` vs other dispositions
- KB gap-analysis discipline
- ADR substrate analysis
- External-research authorization criteria
- Research budget discipline
- Anti-patterns

## Core principle: KB-and-ADR-first

Every information need produced by reading the PRD goes through a **five-way disposition triage**:

1. **Covered by an existing KB?** Walk SKILL.md descriptions; identify candidate KBs; within each candidate KB, spot-check files like its "principles" reference and "patterns-and-anti-patterns" reference (canonical layer file names vary across KBs). If a KB covers it, the need is resolved; mark `disposition: covered-by-KB:<KB-name>:<reference-file>`. No external research.
2. **Covered by an existing ADR?** Walk ADR titles and decision statements in the project's `adrs/` directory. If an ADR establishes the answer, mark `disposition: covered-by-ADR:<ADR-id>`. No external research.
3. **Is this a codebase fact?** If the answer is "what does our codebase currently do?", route to `discovery-codebase-researcher` (mark `disposition: codebase-topic`). Never an external research topic.
4. **Is this well-trodden community knowledge a competent designer can apply?** If the question has a standard, widely-documented answer that no project-specific KB has captured but that's not novel enough to warrant external research (e.g., conventional Kubernetes probe parameter defaults, standard Docker build-arg patterns, REST status code semantics), mark `disposition: designer-general-knowledge`. The downstream per-layer designer applies the convention with **explicit rationale documented in the design section** — the designer's prose carries the source authority rather than a binding KB or external citation. No external research. *This is a positive disposition, not a fallback: claiming it commits the designer to documenting the convention's rationale in the per-layer Design section so reviewers can audit.*
5. **Genuine gap?** Only if 1-4 all fail does this become a candidate external-research topic. The justification is recorded explicitly: which KBs were checked, what they cover, what they specifically don't cover, AND why this isn't `designer-general-knowledge` either (i.e., why the question is novel or specialized enough to require external sources rather than convention).

Skipping step 1, 2, or 4 is a violation. The Research Plan must show its work — the explicit "Topics explicitly NOT researched" section is a positive deliverable, not optional.

### When to choose `designer-general-knowledge` vs other dispositions

The four prior dispositions exist; this fifth one is the honest path when none fits without distortion. Use the following filter to decide:

- **vs. `covered-by-KB`**: if a project KB genuinely documents the answer in `principles.md` or `patterns-and-anti-patterns.md`, prefer `covered-by-KB`. Use `designer-general-knowledge` only when the KB is silent AND the answer is industry-standard widely-known knowledge.
- **vs. `codebase-topic`**: if the answer depends on what THIS codebase does, it's `codebase-topic`. If the answer would be the same in any codebase using this stack, it's `designer-general-knowledge`.
- **vs. `external-research-topic`**: if a competent designer would just *know* the answer (Kubernetes liveness probe defaults; Express middleware ordering; standard semver semantics), it's `designer-general-knowledge`. If the answer requires sourcing from documentation, benchmarks, or specialist community knowledge that the designer would not be expected to carry, it's `external-research-topic`.
- **Smell that you're misusing this**: if you find yourself reaching for `designer-general-knowledge` for >50% of information needs, the feature is probably more novel than you think (or the KBs need expansion). Re-audit.

## How to extract information needs from the PRD

Read the PRD with three questions for every section:

- **"What does Synthesis need to know that the PRD doesn't already state?"** Synthesis consumes Discovery Research outputs. If a synthesis claim will depend on a fact not yet established, that fact is an information need.
- **"What does each in-scope per-layer Designer need to know to design their layer?"** Per-layer Designers read PRD + research outputs. If a designer's section requires a decision based on technology, library, or pattern characteristics, that's an information need.
- **"What does the Plan need to know about codebase blast-radius?"** Plan sequencing depends on what's affected. If the PRD's behavior changes touch points whose blast radius is unknown, that's a codebase research need.

Don't fish for information needs. A vague "research best practices for X" is a smell. Each need has a named downstream consumer.

## Disposition rules: when KB coverage is "good enough"

A KB covers an information need when **a per-layer Designer (or the composer) could make the decision by consulting the KB without needing additional sources**.

A KB does NOT cover an information need when:

- The KB describes the general pattern, but the feature requires a specific version's behavior the KB doesn't pin down.
- The KB names a trade-off but the feature's constraints force a non-default choice the KB doesn't elaborate on.
- The KB is silent on a relevant edge case the PRD makes load-bearing.

In these cases, the information need becomes an external research topic with explicit justification: "KB-X covers the general pattern but does NOT cover behavior under condition Y, which the PRD requires."

## Disposition rules: when ADR coverage is "good enough"

An ADR resolves an information need when its Decision statement directly answers the question, OR when its Decision Details table addresses the specific scenario.

An ADR does NOT resolve an information need when:

- The ADR addresses a related but distinct decision.
- The ADR is older than the feature's context and a kill criterion now applies (e.g., the ADR predates a regulatory change).
- The ADR's scope explicitly excludes the feature's domain.

Mark these explicitly: don't claim ADR coverage when the ADR is merely adjacent.

## External research budget

Default: **6 external topics maximum** per Research Plan. The cap is per-Plan, not per-run.

Why 6? Each external researcher invocation runs in parallel (per ADR-0021 fan-out), but the synthesis fan-in cost grows non-linearly with topic count. 6 is the empirical knee in the curve.

Override path: `--max-external-research-topics N` at orchestrator invocation. Larger overrides should be discussed at the Research Plan Approval Gate.

If the Plan would naturally have more than 6 topics, the discipline is to **consolidate**: collapse topics that share sources or have overlapping research questions into a single richer topic. The acceptance criteria for the consolidated topic are stricter (e.g., "covers 2 sub-questions explicitly") but the budget pressure forces sharper scoping.

## Codebase research scope: always non-empty

`discovery-codebase-researcher` always runs. Even for features that seem "small" or "self-contained," blast-radius preview catches surprises before per-layer Design.

The Codebase Research Scope section names:

- **Touch points**: specific files/modules/services likely in scope. Drawn from the PRD's Layer Scope + named systems + user stories.
- **Blast-radius questions**: who depends on the touch points (1-hop, 3-hop). Per ADR-0018, hop_tier_distribution captured.
- **Convention discovery**: per in-scope layer, what existing patterns the design must respect.
- **Specific queries** (optional): named Cypher queries or grep targets when the topic is precise.

If the touch points are unknown ("the PRD doesn't name specific files"), the scope is broader: "Identify candidate touch points by grepping for terms `<term1>`, `<term2>` in the codebase, then trace dependencies." The researcher's first phase converts the broad scope into a concrete inventory.

## External research topic structure: each topic carries 5 fields

Per the Research Plan template:

1. **Topic name and ID** (`T-<NNN>`).
2. **Research question** — one sentence. Specific enough that an external researcher knows what "done" looks like.
3. **KB gap justification** — explicit. Which KB(s) checked, what they cover, what they don't.
4. **Acceptance criteria** — concrete and verifiable: "names 3 reputable sources" / "identifies 2 trade-offs" / "quotes specific version numbers or limits."
5. **Source constraints** — authoritative sources only. Topic-specific guidance: "official docs only" / "RFCs + standards bodies" / "peer-reviewed papers" / "reputable engineering blogs from companies operating the tech at scale."

Bad acceptance criteria: "thoroughly research X." Good: "names 3 production-tested approaches with their throughput characteristics under similar workloads."

Bad source constraints: "good sources." Good: "official MongoDB documentation, MongoDB Engineering Blog, peer-reviewed papers from VLDB/SIGMOD."

## "Topics explicitly NOT researched" — anti-scope-creep

The Research Plan's `Topics explicitly NOT researched` section is the visible artifact of the KB-and-ADR-first discipline. For each information need with disposition `covered-by-KB` or `covered-by-ADR`, the section records:

- The Need ID.
- The resolving artifact (KB reference file OR ADR ID + version).
- A 1-2 sentence resolution summary.

This section serves three purposes:

1. **Audit trail** at the Research Plan Approval Gate: humans can verify the KB/ADR coverage claim by checking the cited file.
2. **Anti-scope-creep**: future revisits of "should we research X?" go to this section first.
3. **KB validation**: if the section becomes consistently long with the same KB references, that KB is doing its job. If it's consistently short or routinely overridden, the KB has a gap that should be closed.

## At the Research Plan Approval Gate

The user reviews the Research Plan. The key things they evaluate:

- **External topic budget**: is 6 the right cap for this feature? Larger or smaller?
- **Specific external topics**: do these match the user's mental model of what needs research?
- **Topics explicitly NOT researched**: is the KB/ADR coverage claim trustworthy for each?
- **Codebase research scope**: are the touch points correctly identified?
- **Open questions for human**: are there ambiguities the user must resolve before research?

User answers feed back: the Plan is updated; research begins.

## Common mistakes (and how to avoid them)

- **Default to external research.** Habit, not discipline. Always check KBs and ADRs first; the explicit triage prevents this.
- **Vague research questions.** "Investigate Postgres performance." Bad — what aspect? Under what conditions? Sharpen to: "Identify Postgres 16 query-planner behavior for `GIN` indexes on JSONB under writes >10K/sec, citing official documentation + 2 production case studies."
- **Skipping the explicit-NOT-researched section.** It feels like overhead. It's the visible-evidence-of-discipline that the Approval Gate depends on.
- **Treating every PRD section as an information need.** Many PRD sections are user-side decisions, not research needs. Filter: does any downstream sub-agent need a fact that isn't already in the PRD or a KB?
- **Inflating the external topic budget to feel thorough.** Six well-scoped topics > sixteen vague ones. The budget cap forces sharpness.

## Cross-references

- **Research Plan template**: `references/templates/research-plan-template.md` (structural contract).
- **ADR-0021**: codifies KB-and-ADR-first + Discovery Research fan-out.
- **Discovery Research stage**: 1 × `discovery-codebase-researcher` + N × `discovery-external-researcher` (max 6 in parallel).
- **PRD template**: `references/templates/prd-template.md` (upstream input the Research Plan reads).
- **codebase-analysis.json schema**: in KB-codebase-research; the downstream consumer of the Codebase Research Scope section.
