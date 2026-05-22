---
name: decision-framing-knowledge
description: Knowledge skill loaded by synth-framer. Carries ADR/MADR templates, decision-class taxonomy, reversibility framing, blast-radius scale, Wardley evolution stages, RICE rubric, and routing rules from claim cluster to output artifact type.
user-invocable: false
---

# Decision Framing Knowledge

Loaded by `synth-framer` via `skills: [decision-framing-knowledge]`. Provides the rubrics for transforming a verified, graphed claim corpus into actionable decision frames.

## Decision-class taxonomy

Every decision the report surfaces is one of three classes:

| Class | Meaning | Output artifact |
|---|---|---|
| `architectural` | Touches system structure, integration boundaries, or cross-cutting concerns | ADR (Architecture Decision Record) |
| `implementation` | Choice of library, tool, or pattern within a fixed architecture | Inline in main report (no ADR) |
| `operational` | Process, runbook, or governance change | Inline in main report; backlog item if action required |

**Routing rule:** ADR-worthiness (per Design §9 Q5) is determined by:
- Reversibility (one-way doors get ADRs)
- Blast radius ≥ "service" scope
- Cross-team coordination required

If 2 of the 3 hold → architectural → ADR. Otherwise → implementation or operational.

## Reversibility framing (Bezos one-way / two-way doors)

For each decision, classify:

- **Two-way door** — easily reversible. Try it; revisit if it doesn't work. Bias toward action; minimal up-front analysis.
- **One-way door** — hard to reverse. Costly to undo (data migration, customer communication, regulatory commitment). Demand high confidence and explicit alternatives analysis.

Decision frame's `reversibility` field takes values `one_way` or `two_way`.

## Blast-radius scale

`blast_radius` field captures the scope of impact if the decision goes wrong:

| Value | Scope |
|---|---|
| `component` | Affects a single module/component within a service |
| `service` | Affects an entire service |
| `tenant` | Affects multiple services within one organization |
| `org` | Affects external stakeholders, customers, or regulators |

Larger blast radius → ADR-worthy regardless of reversibility.

## Wardley evolution stages

For each decision touching a capability, classify the capability's maturity:

| Stage | Meaning | Strategic implication |
|---|---|---|
| `genesis` | Novel, experimental | Build custom; expect rework |
| `custom` | Bespoke implementations exist | Build vs. buy is a real question |
| `product` | Productized, multiple vendors | Buy; differentiate elsewhere |
| `commodity` | Utility, undifferentiated | Buy on price; do not build |

Decision frame's `wardley_stage` field. Use the dominant stage observed across cited claims; if claims disagree, surface the disagreement (often signals a market in transition).

## RICE scoring rubric

For prioritization, score each decision on Reach × Impact × Confidence ÷ Effort:

| Dimension | Scale | Anchor |
|---|---|---|
| Reach | persons or services affected per quarter | Cite the source |
| Impact | massive (3) / high (2) / medium (1) / low (0.5) / minimal (0.25) | Per affected unit |
| Confidence | 100% / 80% / 50% (anchor on Critic verdict + provenance) | `verified` + `independent` provenance ⇒ 80%; `single_sourced` ⇒ 50% |
| Effort | person-weeks | Engineer-only; exclude review/coordination |

**Confidence calibration:** map Critic verdicts → RICE confidence:
- `verified` AND independent provenance ⇒ 80% (default high; only 100% with multiple independent sources)
- `verified` AND vendor-only provenance ⇒ 50%
- `single_sourced` ⇒ 50%
- `unverifiable` claims do not enter decision frames at all (invariant 5)
- `contradicted` claims with dissent_evidence ⇒ both perspectives carry their own RICE score; surface the choice

## ADR template (MADR-shaped)

Per Design §9 Q5, MADR is the recommended format. The Synthesizer uses this template (defined in `report-composition-knowledge`). Framer doesn't render the ADR — it produces the *decision frame* that the Synthesizer renders. The frame contains:

- `decision_id` (D-NNNN)
- `title` — short, decision-shaped ("Use OAuth 2.0 for service-to-service auth")
- `context` — why this decision is being made now
- `claim_cluster_ids` — the C-NNNN values that informed this decision
- `class` — `architectural` / `implementation` / `operational`
- `reversibility` — `one_way` / `two_way`
- `blast_radius` — `component` / `service` / `tenant` / `org`
- `wardley_stage` — `genesis` / `custom` / `product` / `commodity`
- `rice` — `{reach: int, impact: float, confidence: float, effort: float}`
- `options_summary` — high-level option labels (Substrate phase enumerates the three concrete options)
- `risks` — list of risks if this decision goes wrong

## Critic verdict integrity (invariant 5)

Per Design §7.1 invariant 5, this Framer:
- **Excludes** claims with `verdict == "unverifiable"` from `claim_cluster_ids` UNLESS `dissent_evidence` is populated (in which case the claim is one side of a documented disagreement and stays in cluster).
- **Includes** claims with `verdict == "single_sourced"` but flags them in the decision frame's `risks` field ("Decision rests on a single-sourced claim: C-NNNN").
- **Surfaces** `verdict == "contradicted"` claims as risks unless dissent is established.

## Scope filtering

Read `00-manifest.json` `constraints.scope` at task start:
- `narrow` → produce 3–5 decision frames covering only the topic's central decisions.
- `broad` → produce 8–15 frames covering central + adjacent decisions.
- `exploratory` → produce 15–25 frames including tangential observations as candidate decisions.

Within scope, prefer high-blast-radius / high-RICE / one-way-door decisions.

## Output contract

Write to `04-decision-frames.json`:
```json
{
  "decisions": [ <decision_frame>, ... ]
}
```
where each `<decision_frame>` conforms to `decision-frame.schema.json`.

## See also

- `references/examples.md` — 6–8 worked decision-framing examples
- `references/anti-patterns.md` — common mistakes (mis-classifying implementation as architectural; missing Wardley stage)
