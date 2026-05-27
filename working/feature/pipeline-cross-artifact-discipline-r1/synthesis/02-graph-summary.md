# Entity Graph Summary — pipeline-cross-artifact-discipline-r1

**Source:** 372 merged atomic claims across 5 sources (codebase-analysis, T-001, T-002, T-003, T-004)
**Graph:** 124 entities, 131 edges
**Scale band:** medium (>100 entities) — used hand-curated topical grouping rather than formal community detection. Louvain is not available in the substrate; this grapher fell back to manual clustering by relation-density and topical co-occurrence.

## Top entities by claim count

| Rank | Entity | Type | Claim count | Notes |
|---|---|---|---|---|
| 1 | FR-9 (Blocks-X markers) | control | 14 | Strongest connector — bridges Discovery, gates, FR-1, FR-2 |
| 2 | FR-1 (design-realization audit) | control | 12 | Cross-cuts R2a/R2b; canonical example (mcp-openapi-schema stale ref) |
| 3 | architecture-audit-issues.json | standard | 12 | Schema touched by FR-1/FR-4/FR-5/FR-9/FR-10 — bridge between halves |
| 4 | OI-A4 (Contingency Split threshold) | control | 11 | Already pre-fired (14 cumulative > threshold of 12) |
| 5 | Packwerk (Shopify retrospective) | tool | 11 | Closest documented denormalized↔central migration |
| 6 | FR-11 (§O posture) | control | 10 | Purely additive — zero prior post-ship discipline-text |
| 7 | hybrid invariant model | pattern | 10 | T-004 unanimous synthesis verdict |
| 8 | FR-6 (agent-roster matrix mandatory) | control | 9 | R2a anchor; mutual cross-ref with FR-8 |
| 9 | OI-A1 (companion vs NLP) | control | 9 | T-002 nine-system unanimous: companion-file path |
| 10 | Why/How/Anti-patterns trifecta | pattern | 10 | T-003 novelty-as-codification verdict |
| 11 | oasdiff | tool | 9 | T-001 severity-catalog model |
| 12 | NLP-parse path | pattern | 13 | T-002 finds it absent at production scale |
| 13 | companion-file path | pattern | 14 | T-002 nine-system consensus winner |
| 14 | Anthropic Agent Skills | service | 6 | Substrate-native skill mechanism |

## Top edges by claim count

| From | To | Relation | Claim count | Notes |
|---|---|---|---|---|
| FR-9 | Blocks-X precedent grammar | implements | 4 | n=1 prior occurrence → establishing not reconciling |
| FR-4 | audit_mcp.py (--with-runtime) | supersedes | 3 | FR-4 corrects the misnaming |
| FR-5 | four-stage drift-detection pipeline | implements | 3 | T-001's structural recipe |
| FR-1 | mcp-openapi-schema (stale) | conflicts_with | 3 | Canonical FR-1 example |
| Perplexity | tool-proliferation anti-pattern | conflicts_with | 3 | Three named anti-patterns |
| FR-6 | agent-roster-impact-matrix.md | requires | 3 | Mandatory deliverable bond |
| four-stage drift-detection | RFC 6902 + JCS + oasdiff + MCP | requires | 2 each | Four-way dependency chain |
| FR-11 | event/honest/concrete framings | implements | 1 each | Three-way posture decomposition |
| {6 reviewer/auditor agents} | Principle 9 | requires | 1 each | xhigh effort tier dependency cluster |
| FR-1 / FR-6 / FR-7 / FR-8 / FR-9 / FR-10 | R2a cluster | instance_of | 1 each | Cluster membership |
| FR-2 / FR-3 / FR-4 / FR-5 / FR-11 | R2b cluster | instance_of | 1 each | Cluster membership |

## Identified clusters

### Cluster 1 — R2a (design-time discipline)
**Members:** FR-6, FR-7, FR-8, FR-9, FR-10, with FR-1 cross-cutting.
**Anchor entities:** FR-6 (agent-roster matrix mandatory), Principle 9, agent-roster-impact-matrix.md, Issues/per-agent-design-evaluation-gap.
**Internal density:** FR-6↔FR-7 (trigger 4), FR-6↔FR-8 (mutual cross-ref per AC-FR-8-b), FR-6↔FR-10 (backstop), FR-8 implements Principle 9.
**Why this cluster:** all touch design-time artifacts (matrix authoring, skill-coverage rationales, KB-cc-design wording). The R2a cluster maps onto a candidate "feature-pipeline design discipline" feature half.

### Cluster 2 — R2b (gate/validator discipline)
**Members:** FR-2, FR-3, FR-4, FR-5, FR-11.
**Anchor entities:** FR-4+FR-5 (shared --with-mcp-reachability handshake on auditing-mcp), test-phase-validator-author, .mcp.json.
**Internal density:** FR-4↔FR-5 (same file, shared handshake), FR-3↔FR-11 (PV inherits §O framings), FR-2↔FR-9 (Discovery output is Blocks-X emission site — cross-cluster bridge), FR-1↔(FR-4, FR-5) via architecture-audit-issues.json (cross-cluster bridge).
**Why this cluster:** all touch runtime validation/gate machinery and the audit surface.

### Cluster 3 — Audit-issues schema convergence
**Members:** architecture-audit-issues.json, review-architecture-auditor, review-cross-artifact-auditor, auditing-shared, auditing-mcp, auditing-cc-configs, three severity vocabularies (auditor / reviewer / phase-validator), finalize-reconciler, finalize-deliverable-packager.
**Anchor entities:** architecture-audit-issues.json (12 claims), severity vocabulary divergence (Known Issue 2).
**Why this cluster:** known-issue 2 surfaces a 3-vocabulary divergence design-composer must reconcile; FR-1, FR-4, FR-5, FR-9, FR-10 all touch this schema.

### Cluster 4 — Drift-detection technical heritage (T-001)
**Members:** oasdiff, OpenAPITools/openapi-diff, Buf, Pact, RFC 8785 (JCS), RFC 6902 (JSON Patch), RFC 6901 (JSON-Pointer), MCP specification, MCP SEP-2549, four-stage drift-detection pipeline, FR-5.
**Anchor entities:** four-stage drift-detection pipeline (synthesis recommendation), MCP specification (bridge between standards and FR-5).
**Why this cluster:** T-001 surveys five adjacent production approaches and synthesizes a defensible four-stage pipeline (JCS normalize → baseline → RFC 6902 diff → severity catalog modeled on oasdiff). All entities here cite primary sources (RFC IDs, MCP spec rev).

### Cluster 5 — Design-realization prior art (T-002)
**Members:** companion-file path, NLP-parse path, Nygard ADR template, MADR, Archgate, kschlt/adr-kit, DECIDER, rvdbreemen/adr-kit, ArchUnit, Schemathesis, Spectral, Terraform Sentinel, OPA, Pact, arXiv 2602.07609, Reflexion Modelling (Rosik 2011), OI-A1, FR-1.
**Anchor entities:** companion-file path (14 claims), NLP-parse path (13 claims), OI-A1 (open item the cluster resolves).
**Why this cluster:** T-002's nine-system survey converges unanimously on companion-file path; NLP-parse rejected at production scale (arXiv 2602.07609 quantifies LLM failure modes; 44.57% semantic misinterpretation). Surfaces OI-A1 as effectively pre-decided by the prior art.

### Cluster 6 — Skill-coverage rubric heritage (T-003)
**Members:** Why/How/Anti-patterns trifecta, Anthropic Agent Skills, LangGraph, OpenAI Agents SDK, Microsoft Agent Framework, AutoGen, CrewAI, Semantic Kernel, Perplexity, progressive disclosure, tool-proliferation anti-pattern, premature specialization anti-pattern, Berkeley Function Calling Leaderboard, FR-7.
**Anchor entities:** Why/How/Anti-patterns trifecta (10 claims), tool-proliferation anti-pattern (8 claims), Perplexity (9 claims).
**Why this cluster:** every surveyed agent platform prescribes prose principles but mandates no structured per-capability artifact. FR-7's trifecta is substance-as-community, codification-as-novel. Tool-proliferation is the cross-platform 4-source consensus failure mode.

### Cluster 7 — Cross-file invariant catalog heritage (T-004)
**Members:** hybrid invariant model, Terraform, dbt, OpenAPI, JSON Schema, ArchUnit, Bazel, Packwerk, OI-A2, FR-3.
**Anchor entities:** hybrid invariant model (10 claims), Packwerk (11 claims — only documented migration case).
**Why this cluster:** every surveyed system uses the hybrid pattern (denormalized declaration with centralized invariant body). Packwerk is the lone "tried fully-central, walked back" datapoint; OI-A2 is functionally pre-decided toward hybrid.

### Cluster 8 — §O posture vocabulary (FR-11)
**Members:** FR-11, event-triggered framing, honest-acceptance framing, concrete-machinery framing, Issues/devcontainer-mcp-provisioning-r1-deferrals/register.md.
**Anchor entities:** FR-11 (10 claims).
**Why this cluster:** FR-11 is structurally simpler than the PRD framing suggests — zero prior post-ship discipline-text means purely additive prescription. Three sub-framings sit inside FR-11's scope.

## Surprising / load-bearing patterns

- **FR-9 is establishing not reconciling.** Blocks-X grammar has n=1 prior occurrence (devcontainer-mcp-provisioning-r1 lines 198-202). The graph's heaviest entity (14 claims) operates on functionally-absent vocabulary.
- **FR-1 cross-cuts R2a and R2b.** The PRD already flags FR-1 as cross-cutting; the graph confirms via edges into both clusters (R2a via architecture-audit-issues.json schema; R2b via mcp-openapi-schema stale-ref example sitting in audit_op2_consumer_mapping.py).
- **Contingency Split is already triggered.** OI-A4 evidence (cumulative 14 > threshold 12) intersects FR-9 and FR-1 cluster bridges — graphically this means design-composer faces both schema deltas and marker grammar simultaneously.
- **Severity vocabulary divergence is graphically central.** Auditor (BLOCKER/MAJOR/MINOR/INFO|NIT), reviewer (critical/important/recommended), and phase-validator (blocking/warning/informational) vocabularies all connect to architecture-audit-issues.json — the canonical "what severity does this finding use?" question is unresolved.
- **OI-A1 and OI-A2 are externally pre-decided.** T-002 nine-system unanimous (companion-file) and T-004 hybrid-model consensus mean the two largest design open items have strong external recommendations even before design-composer runs.
- **Cross-source corroboration triples** (highest-confidence finding triangulation):
  - FR-5 / four-stage pipeline / MCP specification — T-001 synthesis recommendation cites MCP spec primary, RFC 8785 primary, RFC 6902 primary; corroborated by oasdiff severity-catalog primary.
  - FR-1 / companion-file path / nine surveyed systems — T-002 unanimous nine-system finding (Nygard, MADR, Archgate, ADR-Kit kschlt, DECIDER, ADR-Kit rvdbreemen, ArchUnit, Pact, OpenAPI/Schemathesis/Dredd, Spectral, Terraform Sentinel/OPA).
  - FR-7 trifecta / community substance / proliferation anti-pattern — T-003 four-source corroboration (aipatternbook.com, agentpatterns.tech, tianpan.co, kvg.dev).

## Method notes

- Unification heuristics applied consistently: PRD FR-N entities carry their mechanism letters (H/B/§O) as aliases.
- ADRs each became their own `standard` entity (ADR-0017, 0018, 0030, 0036, 0038, 0042, 0054, 0056) rather than being collapsed under "ADR system".
- The six R2a/R2b cluster relationships are encoded as `instance_of` edges into two cluster-pattern entities (E-0122, E-0123). This is unusual but supports query-by-cluster directly from the graph rather than only via the summary.
- Severity vocabularies kept as three separate `standard` entities (not merged), per the "material capability differences" unification rule — auditor/reviewer/PV vocabularies disagree on names, count, and bridging.
- `mcp-openapi-schema` retained as a `service` entity despite being removed 2026-05-24, because it is the canonical FR-1 conflict_with example and appears in five claims.
- Findings (arXiv papers, BFCL benchmark, Rosik 2011) promoted to `finding`-typed entities because each is referenced by multiple claims (per the entity-graph-knowledge anti-patterns rule).
