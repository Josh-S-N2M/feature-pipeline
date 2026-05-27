# R2a Entity Graph — Summary

Human-readable companion to `02-graph.json`. Critic, Framer, Substrate, and Synthesizer consume the JSON, not this file.

- **Entities:** 103
- **Edges:** 100
- **Claims covered:** 200 (codebase-analysis-r2a 96, T-002 48, T-003 56)
- **Clusters identified:** 6 (hand-curated, ≤100 entities so no formal community detection)

## Top entities by claim count

| Rank | ID | Entity | Type | Claim count |
|---|---|---|---|---|
| 1 | E-0003 | FR-7 (skill-coverage decisions) | control | 23 |
| 2 | E-0014 | ADR-0061 (severity-vocabulary bridge) | standard | 15 |
| 3 | E-0025 | KB-review-disciplines | tool | 12 |
| 4 | E-0044 | severity-taxonomy.md | tool | 11 |
| 5 | E-0046 | Auditor severity vocabulary | standard | 11 |
| 6 | E-0045 | verdict_compute.py | tool | 11 |
| 7 | E-0047 | Reviewer severity vocabulary | standard | 10 |
| 8 | E-0005 | FR-9 | control | 10 |
| 9 | E-0097 | Tool-proliferation anti-pattern | pattern | 9 |
| 10 | E-0013 | ADR-0059 (FR-1 prescription extractor) | standard | 8 |
| 11 | E-0049 | Iteration-delta severity weights | standard | 8 |
| 12 | E-0095 | Perplexity Agent-Skills guidance | standard | 8 |
| 13 | E-0034 | Design-realization audit (domain concept) | pattern | 7 |
| 14 | E-0080 | arXiv 2602.07609 (LLM-ADR study) | finding | 7 |

## Top edges by claim count

Edges with the heaviest claim-id backing — these are the load-bearing relations in R2a.

| From | Relation | To | Claim count |
|---|---|---|---|
| E-0046 (Auditor vocab) | implements | E-0045 (verdict_compute.py) | 6 |
| E-0049 (Iteration-delta weights) | requires | E-0020 (cross-artifact auditor) | 4 |
| E-0047 (Reviewer vocab) | requires | E-0025 (KB-review-disciplines) | 4 |
| E-0049 | conflicts_with | E-0046 | 4 |
| E-0025 | implements | E-0047 | 4 |
| E-0058 (Companion-artifact pattern) | conflicts_with | E-0059 (NLP-parse anti-pattern) | 4 |
| E-0005 (FR-9) | requires | E-0028 (auditing-shared) | 1 |
| E-0005 | requires | E-0043 (blocks-x-marker-grammar.md) | 2 |
| E-0014 (ADR-0061) | implements | E-0052 (severity-vocab trifecta) | 2 |
| E-0080 (arXiv 2602.07609) | conflicts_with | E-0059 | 3 |

## Identified clusters

### Cluster 1: R2a design-time discipline core (FR-6 / FR-7 / FR-8 / FR-10 + Principle 9)

The densest cluster. Captures the four design-time-discipline FRs that demand authored design artifacts (impact matrix, skill-coverage rubric, active-Principle-9, matrix-missing audit rule) and the Principle 9 reframing that mutually cross-references FR-6.

Members:
- **Controls:** E-0002 (FR-6), E-0003 (FR-7), E-0004 (FR-8), E-0006 (FR-10), E-0033 (Principle 9)
- **Roles/skills:** E-0021 (design-claude-code), E-0024 (KB-cc-design), E-0027 (KB-documentation-criteria), E-0029 (auditing-subagents), E-0022 (test-phase-validator-author), E-0026 (KB-task-decomposition), E-0023 (finalize-task-decomposer)
- **Domain concepts:** E-0035 (agent-roster impact matrix), E-0036 (skill-coverage decision), E-0038 (matrix-missing audit rule)
- **OIs:** E-0007 (OI-R2a-1), E-0010 (OI-R2a-4), E-0011 (OI-R2a-5), E-0055 (OQ#1)

### Cluster 2: FR-1 + FR-9 sub-cluster (audit emission + marker grammar)

Pairs FR-1 (design-realization audit emission into review-architecture-auditor) with FR-9 (Blocks-X marker grammar) — both ride on the same auditing-shared script slot and both ultimately feed state-transitions.log style downstream consumers (PV/CCA reconcilers).

Members:
- **Controls:** E-0001 (FR-1), E-0005 (FR-9)
- **Standards:** E-0013 (ADR-0059), E-0015 (ADR-0063), E-0018 (ADR-0044)
- **Tools:** E-0039 (ADR prescriptions companion file), E-0040 (validate_adr_prescriptions.py), E-0042 (parse_blocks_x_markers.py), E-0043 (blocks-x-marker-grammar.md), E-0028 (auditing-shared), E-0019 (review-architecture-auditor)
- **Domain concepts:** E-0034 (Design-realization audit), E-0037 (Blocks-X marker grammar)
- **OIs:** E-0009 (OI-R2a-3), E-0057 (OQ#3)

### Cluster 3: Severity-vocabulary bridge cluster

The bridge-author work. Hosts ADR-0061 plus the three vocabularies, the bridge host file, the two weight sets (verdict-compute vs iteration-delta), and the auditor agents that emit findings.

Members:
- **Standard:** E-0014 (ADR-0061), E-0046 (Auditor vocab), E-0047 (Reviewer vocab), E-0048 (PV vocab), E-0049 (iteration-delta weights), E-0050 (Verdict thresholds), E-0051 (NFR-8 four-field shape)
- **Tools:** E-0044 (severity-taxonomy.md), E-0045 (verdict_compute.py), E-0041 (translate_severity.py), E-0025 (KB-review-disciplines), E-0031 (auditing-cc-configs), E-0032 (auditing-mcp)
- **Roles:** E-0019, E-0020, E-0022
- **Pattern:** E-0052 (Severity-vocabulary trifecta)
- **OIs:** E-0012 (OI-R2a-6), E-0056 (OQ#2), E-0103 (Issue #2)

### Cluster 4: Eat-own-dogfood cluster

FR-7's self-application: the 6 new domain concepts surface as a 6-row table of skill-coverage decisions in this very synthesis (all rows "existing-skill"). Bridges Clusters 1, 2, and 3 by re-asserting each domain concept lands in an existing skill.

Members:
- **Domain concepts (patterns):** E-0034, E-0035, E-0036, E-0037, E-0038, plus E-0033 (Principle 9 active reframing is the sixth concept)
- **Pattern bridge:** E-0036 (Skill-coverage decision) is the dogfood centroid — it conflicts_with the closest external analogs E-0096 (Crews-vs-Flows), E-0100 (Eval-first), E-0097 (tool-proliferation framing as anti-pattern)

### Cluster 5: T-002 prior-art cluster (design-realization audit literature)

Bridges into Cluster 2 via E-0034 (Design-realization audit) and the canonical claim that companion-artifact patterns universally beat NLP-parse-prose.

Members:
- **Patterns:** E-0058 (Companion-artifact), E-0059 (NLP-parse anti-pattern), E-0078 (Policy-as-code), E-0079 (Reflexion Modelling), E-0068 (FreezeRules)
- **Standards:** E-0060 (Nygard), E-0061 (MADR), E-0071 (OpenAPI), E-0076 (Rego)
- **Tools:** E-0062 (Structured MADR), E-0063 (Archgate), E-0064 (kschlt ADR Kit), E-0065 (DECIDER), E-0066 (rvdbreemen adr-kit), E-0067 (ArchUnit), E-0069 (Pact), E-0072 (Schemathesis), E-0073 (Spectral), E-0074 (HashiCorp Sentinel), E-0075 (OPA)
- **Service:** E-0077 (Terraform)
- **Findings:** E-0080 (arXiv 2602.07609), E-0081 (arXiv 2504.08207), E-0082 (DRMiner), E-0083 (Rosik 2011), E-0084 (60% reduction estimate)
- **Patterns:** E-0070 (Schema-based contracts)

### Cluster 6: T-003 prior-art cluster (skill-coverage rubric patterns)

Bridges into Cluster 1 via E-0036 (Skill-coverage decision). Documents the 7-platform survey showing no platform mandates the trifecta — making FR-7's codification novel.

Members:
- **Services:** E-0085 (Anthropic Agent Skills), E-0088 (LangChain/LangGraph), E-0090 (OpenAI Assistants/Agents SDK), E-0091 (Microsoft Agent Framework), E-0092 (AutoGen), E-0093 (CrewAI), E-0094 (Semantic Kernel)
- **Standards:** E-0095 (Perplexity guidance), E-0101 (MCP)
- **Tools:** E-0086 (Skill Quality Checklist), E-0089 (langgraph-bigtool)
- **Patterns:** E-0087 (Progressive disclosure), E-0096 (Crews-vs-Flows matrix), E-0097 (Tool-proliferation anti-pattern), E-0098 (Load-on-demand), E-0100 (Eval-first), E-0102 (MAF orchestration ladder)
- **Finding:** E-0099 (Berkeley Function Calling Leaderboard)

## Bridge entities (load-bearing across clusters)

| Entity | Clusters bridged | Why it bridges |
|---|---|---|
| E-0036 (Skill-coverage decision) | 1 ↔ 4 ↔ 6 | FR-7's self-applied dogfood concept; reviewed against external T-003 analogs |
| E-0034 (Design-realization audit) | 2 ↔ 4 ↔ 5 | FR-1's domain concept; reviewed against T-002 prior art |
| E-0037 (Blocks-X marker grammar) | 2 ↔ 4 | FR-9's domain concept that is its own deliverable |
| E-0014 (ADR-0061) | 3 ↔ 4 | Bridge host ADR; also the FR-9 partner via state-transitions.log adjacency |
| E-0028 (auditing-shared) | 2 ↔ 3 | Hosts ADR-0059 linter, ADR-0061 translator, and FR-9 parser |
| E-0027 (KB-documentation-criteria) | 1 ↔ 2 | Hosts FR-7's section template and FR-9's grammar reference |
| E-0058 (Companion-artifact pattern) | 2 ↔ 5 | The pattern ADR-0059 implements; reinforced by 9-system T-002 survey |
| E-0097 (Tool-proliferation anti-pattern) | 4 ↔ 6 | The proliferation defense the trifecta primarily defends against |

## Notes on graph integrity

- All 103 entities have at least one claim back-pointer.
- All 100 edges carry at least one `claim_ids` value.
- All edge endpoints resolve to entities in this graph.
- All claim IDs (C-0001..C-0200) referenced in entity back-pointers exist in `01-claims.json`.
- No invented relations (only the 5-value taxonomy: `implements`, `requires`, `conflicts_with`, `supersedes`, `instance_of`).

## Notes on scale

103 entities is just at the >100 threshold from `entity-graph-knowledge/SKILL.md`. The graph could nominally justify formal community detection, but Louvain isn't available in the substrate and the cluster structure is unambiguous to a hand-curated read. Clusters above mirror the orchestrator-provided expected-cluster sketch closely (R2a design-time cluster, FR-1/FR-9 sub-cluster, severity bridge cluster, eat-own-dogfood cluster) with two additional read-only clusters for T-002 and T-003 prior art that the parent graph mostly absorbed into the FR clusters.
