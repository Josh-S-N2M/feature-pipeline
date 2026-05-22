# Entity Graph Anti-patterns

## 1. Over-merging

Treating "Service Mesh" (architectural pattern) and "Istio" (specific product) as the same entity.

**Discipline:** if surface forms have material capability differences, keep separate. Use `instance_of` edge.

## 2. Missing back-pointers

Entity has empty `claims[]`.

**Discipline:** drop orphan entities. Every entity has at least one claim back-pointer.

## 3. Edges without claim_ids

`{"relation": "implements", "claim_ids": []}` — no claim, no edge.

## 4. Inventing relations

Adding `"relation": "uses"` because no listed relation seems to fit.

**Discipline:** stick to the 5-value taxonomy. If none fits, the assertion is probably about a property, not a relation — record as a claim back-pointer on the entity, not as an edge.

## 5. Forcing community structure on small corpora

Running formal community detection on a 30-entity graph.

**Discipline:** for ≤100 entities, hand-curate clusters in `02-graph-summary.md`.

## 6. Promoting findings to entities

Treating "99.99% uptime" as an entity.

**Discipline:** findings are claims attached to service entities, not entities themselves. Exception: a finding referenced by multiple claims (e.g., a benchmark cited across sources) can become a `finding`-typed entity.
