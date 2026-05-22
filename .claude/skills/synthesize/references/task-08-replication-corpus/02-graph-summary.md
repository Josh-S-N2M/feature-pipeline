# Entity Graph Summary

**Run:** `task-08-replication-20260501-021500`
**Sources:** 2 docs (`technical-designer.md` + `synthesis-pipeline-technical-design.md`)
**Claims:** 53 (27 + 26 after merge)
**Entities:** 42
**Edges:** 29
**Coverage:** 52/53 claims referenced (98%)

This file is for human review. Critic, Framer, Substrate, and Synthesizer consume `02-graph.json` directly.

## Top entities by claim count

| Entity | Type | # claims | Notes |
|---|---|---|---|
| E-0024 Synthesize orchestrator skill | tool | 6 | The brain — referenced across run-id, glob, manifest, resume claims |
| E-0007 Existing Code Investigation | control | 5 | Multi-step technical-designer process |
| E-0001 Design Doc | standard | 5 | Cross-source — both sources discuss design-doc structure |
| E-0012 Verification Strategy | control | 3 | Cross-source — present in both, but with different emphases |
| E-0039 Knowledge skills | pattern | 3 | Pipeline-internal pattern |
| E-0005 Standards Identification Gate | control | 3 | technical-designer discipline |

## Top edges by claim count

Most edges have 1 claim_id (relations established by single claims). Notable multi-claim edges:

| from → to | relation | claim_ids |
|---|---|---|
| E-0024 → E-0035 | implements | C-0007, C-0019 — recursion safety implemented in two complementary ways |
| E-0007 → E-0009 | requires | C-0039, C-0040 — reuse-vs-new criteria are integral to investigation |

## Identified clusters (hand-curated, ≤100 entities so no formal community detection)

### Cluster A: Pipeline architecture (synthesis-pipeline source)
**Anchor:** E-0024 Synthesize orchestrator skill
**Members:** E-0017 (six-phase pipeline), E-0022 (slash command), E-0023 (tell-microsoft-joke precedent), E-0024 (orchestrator), E-0025 (AskUserQuestion), E-0026 (Confirmation Gate), E-0027 (manifest), E-0028 (Task tool), E-0029 (checkpoint), E-0030 (bounded retry), E-0031 (synth-extractor), E-0032 (synth-synthesizer), E-0035 (recursion safety)
**Theme:** the pipeline's *runtime mechanics* in Claude Code primitives.

### Cluster B: Substrate & alternatives
**Anchor:** E-0018 Claude Code
**Members:** E-0017 (pipeline), E-0018 (Claude Code), E-0019 (LangGraph), E-0020 (Temporal), E-0021 (Step Functions), E-0033 (substrate registry), E-0034 (90-day staleness)
**Theme:** what substrate the pipeline targets, and what alternatives are explicitly out of scope.

### Cluster C: Memory & knowledge
**Anchor:** E-0036 Two memory tiers
**Members:** E-0036 (memory tiers), E-0037 (MEMORY.md), E-0038 (sub-agent memory), E-0039 (knowledge skills), E-0040 (assumed_substrate field)
**Theme:** how the pipeline accumulates knowledge across runs.

### Cluster D: Design discipline (technical-designer source)
**Anchor:** E-0001 Design Doc
**Members:** E-0001 (Design Doc), E-0002 (ADR), E-0005 (Standards Gate), E-0006 (QA mechanism record), E-0007 (Existing Code Investigation), E-0008 (Fact Disposition Table), E-0009 (Reuse-vs-new), E-0010 (Agreement Checklist), E-0011 (Implementation approach), E-0015 (Acceptance criteria), E-0016 (architecture diagrams)
**Theme:** the meta-discipline of producing design docs.

### Cluster E: Verification (cross-source bridge)
**Anchor:** E-0012 Verification Strategy
**Members:** E-0012 (Verification Strategy), E-0013 (Early verification point), E-0014 (Output comparison method)
**Theme:** the mechanism by which design correctness is established before scaling. **Bridge entity** — verification appears in both source documents and connects clusters A (pipeline) and D (design discipline).

## Cross-source unifications (per §7.4 partial-overlap requirement)

The following entities appear with claims from BOTH sources, validating the §7.4 corpus-shape requirement that the two documents have partially-overlapping claims:

| Entity | Claims from synthesis-pipeline | Claims from technical-designer |
|---|---|---|
| E-0001 Design Doc | (mentioned but not extracted as claims in source 1) | C-0031, C-0032, C-0036, C-0041, C-0051 |
| E-0002 ADR | — | C-0035, C-0048, C-0049, C-0050 |
| E-0011 Implementation approach selection | (referenced via E-0003 Vertical Slice in design choices) | C-0042 |
| E-0012 Verification Strategy | C-0046, C-0047 (early verification point) | C-0045 |
| E-0013 Early verification point | C-0046, C-0047 | (referenced as part of Verification Strategy) |

The **Verification Strategy** entity is the most significant cross-source bridge: both documents identify "early verification point" as a load-bearing concept, with synthesis-pipeline-technical-design specifying the §7.4 vertical-slice gate (the very work this run replicates) as a concrete instance of the abstract concept defined by technical-designer.

## Unreferenced claim

C-0014 ("User-defined agents are placed at /mnt/user-config/.claude/agents/<name>.md...") is a configuration/path claim. It does not assert a relation between named entities; it specifies a deployment convention. Per Grapher discipline (knowledge skill anti-pattern #6 "Promoting findings to entities"), this stays as a claim attached to no specific entity rather than being elevated.

## Notes for downstream phases

- **For Critic:** Cluster A (pipeline mechanics) has many factual claims to verify against the source. Cluster D (design discipline) has many process-rule claims that are self-asserting in the source — verification is straightforward (does the source say this rule applies?).
- **For Framer:** the cross-source bridge at Verification Strategy is the strongest signal of an architectural decision: "what verification regime do we adopt for our design process?" with concrete instantiation as "the §7.4 vertical-slice gate".
- **For Substrate:** none of these entities require substrate translation (target is already `claude_code` and the entities describe how to USE Claude Code). No native/adapter/substrate-change tension surfaces in this corpus — this is a same-substrate analysis.
