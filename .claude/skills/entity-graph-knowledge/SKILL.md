---
name: entity-graph-knowledge
description: Knowledge skill loaded by synth-grapher. Carries entity-type taxonomy, relation-type taxonomy, unification heuristics, and GraphRAG-lite community-detection notes.
user-invocable: false
---

# Entity Graph Knowledge

Loaded by `synth-grapher` via `skills: [entity-graph-knowledge]`. Provides the rules and rubrics the Grapher applies when transforming `01-claims.json` (a flat list of claims) into `02-graph.json` (entities + edges with claim back-pointers).

## Entity-type taxonomy

The `entity.type` field takes one of seven values:

| Value | Meaning | Example |
|---|---|---|
| `pattern` | Architectural/design pattern | "circuit breaker", "saga pattern", "event sourcing" |
| `service` | Concrete software product or service | "AWS Lambda", "Claude Code", "Datadog" |
| `control` | Governance, security, or operational control | "MFA enforcement", "data residency", "rate limiting" |
| `standard` | Standard, framework, or specification | "OAuth 2.0", "NIST AI RMF", "ISO 27001" |
| `finding` | Empirical result or measured outcome | "99.99% uptime", "latency p99 < 200ms" |
| `tool` | Concrete tool or implementation | "Terraform", "kubectl", "ajv" |
| `role` | Organizational or functional role | "SRE", "Compliance Officer", "Security Architect" |

**Disambiguation rule:** when an entity could fit two categories, prefer the more specific. "OAuth 2.0" is `standard`; "Auth0's OAuth 2.0 implementation" is `service`.

## Relation-type taxonomy

The `edge.relation` field takes one of five values:

| Value | Semantic | Example |
|---|---|---|
| `implements` | Subject realizes object | (Service: Auth0) `implements` (Standard: OAuth 2.0) |
| `requires` | Subject depends on object to function | (Pattern: saga) `requires` (Pattern: idempotency) |
| `conflicts_with` | Subject and object cannot coexist as designed | (Control: data residency EU) `conflicts_with` (Service: us-east-1 region) |
| `supersedes` | Subject replaces or deprecates object | (Standard: OAuth 2.0) `supersedes` (Standard: OAuth 1.0) |
| `instance_of` | Subject is a specific case of object | (Service: AWS Lambda) `instance_of` (Pattern: FaaS) |

Edges always carry `claim_ids` — the claim(s) that establish the relation. Edges with empty `claim_ids` are forbidden.

## Unification heuristics

When two claims reference what *appears* to be the same entity, decide whether to merge into one node with multiple aliases, or keep separate:

**Merge when** (any of):
- Canonical reference matches (`AWS Lambda` and `Lambda by AWS` → same)
- Vendor brand + technical descriptor (`Datadog APM` and `Datadog's APM offering` → same)
- Acronym ↔ expansion (`MFA` and `multi-factor authentication` → same; record `aliases: ["MFA"]`)

**Keep separate when** (any of):
- Different versions with material capability differences (`OAuth 1.0` ≠ `OAuth 2.0`)
- Vendor product vs. open-source equivalent (`Datadog APM` ≠ `OpenTelemetry APM`)
- Same name, different scope (`Service Mesh` as pattern vs. `Service Mesh` as Istio-the-product)

**Recommended workflow:**
1. Assign canonical name per most-formal source available.
2. Populate `aliases` with all encountered surface forms.
3. Aggregate `claims` (claim back-pointers) onto the merged node.

## GraphRAG-lite community detection

For graphs with >100 entities, identify clusters that share dense edge structure. These clusters tend to map to topical themes that the Synthesizer surfaces as report sections. Heuristics:

- **Connected component analysis** — start with simple connected-components; refine via Louvain modularity if the substrate provides it (it doesn't, currently — falls back to manual clustering for now).
- **Bridge entities** — entities with edges to multiple clusters are usually load-bearing standards (e.g., OAuth 2.0 bridges identity and integration clusters).
- **Cluster naming** — use the highest-PageRank entity's `name` as the cluster label; surface in `02-graph-summary.md`.

For graphs with ≤100 entities (the typical case for a 5–10 source corpus), formal community detection is overkill — a hand-curated topical grouping by the Grapher in `02-graph-summary.md` suffices.

## Output contract

Write to `02-graph.json`:
```json
{
  "entities": [
    {
      "id": "E-0001",
      "name": "Canonical Name",
      "type": "service",
      "canonical_uri": "<optional URI>",
      "aliases": ["..."],
      "claims": ["C-0023", "C-0041"]
    }
  ],
  "edges": [
    {
      "from": "E-0001",
      "to": "E-0007",
      "relation": "implements",
      "claim_ids": ["C-0023"]
    }
  ]
}
```

Plus `02-graph-summary.md` (human-readable): top entities by claim count, top edges by claim count, identified clusters. This file is for human review — Critic and Framer ignore it.

## Output integrity

- Every `entity.claims[]` value resolves to a `claim.id` in `01-claims.json`.
- Every `edge.from` / `edge.to` resolves to an `entity.id` in this file.
- Every `edge.claim_ids[]` value resolves to a `claim.id`.
- No orphan entities (entities with empty `claims[]`) — drop them.

## See also

- `references/examples.md` — 6–8 worked unification examples
- `references/anti-patterns.md` — over-merging, missing back-pointers, edges without claim_ids
