# Decision Framing Examples

## Architectural — one-way door

**Cluster:** Claims about identity provider choice.

```json
{
  "id": "D-0001",
  "title": "Use OAuth 2.0 with provider X for service-to-service auth",
  "context": "Six services need uniform auth; current ad-hoc approaches diverge.",
  "claim_cluster_ids": ["C-0030", "C-0031", "C-0035"],
  "class": "architectural",
  "reversibility": "one_way",
  "blast_radius": "tenant",
  "wardley_stage": "commodity",
  "rice": {"reach": 200, "impact": 2.0, "confidence": 0.8, "effort": 6},
  "options_summary": ["OAuth 2.0 + provider X", "OAuth 2.0 + provider Y", "Custom scheme"],
  "risks": ["Vendor lock-in", "Provider X authentication outage = full tenant outage"]
}
```

ADR-worthy (one_way + blast_radius=tenant + cross-team).

## Implementation — two-way door

**Cluster:** Claims about logging library.

```json
{
  "id": "D-0010",
  "title": "Use structured logging library Z",
  "class": "implementation",
  "reversibility": "two_way",
  "blast_radius": "service",
  "rice": {"reach": 50, "impact": 0.5, "confidence": 0.8, "effort": 1}
}
```

Inline in report; no ADR.

## Operational — backlog

**Cluster:** Claims about runbook gaps.

```json
{
  "id": "D-0020",
  "title": "Add runbook for partial-outage scenario",
  "class": "operational",
  "reversibility": "two_way",
  "blast_radius": "tenant",
  "wardley_stage": "custom"
}
```

Inline; backlog-task surfaced in report.

## Confidence calibration to Critic verdicts

- 3 claims `verified` with independent provenance → `rice.confidence: 0.8`
- 2 of 3 claims `verified` from same vendor → `rice.confidence: 0.5`
- 1 claim `single_sourced` (consequential) → `rice.confidence: 0.5` and add risk: "Decision rests on a single-sourced claim: C-NNNN"
