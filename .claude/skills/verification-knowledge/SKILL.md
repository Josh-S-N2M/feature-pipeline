---
name: verification-knowledge
description: Knowledge skill loaded by synth-critic. Carries the Chain-of-Verification (CoVe) protocol, adversarial-prompt patterns, verdict criteria, dissent-flagging rules, and common over-confident claim shapes.
user-invocable: false
---

# Verification Knowledge

Loaded by `synth-critic` via `skills: [verification-knowledge]`. Provides the rubrics for Chain-of-Verification (CoVe) per claim, adversarial probing, verdict assignment, and dissent flagging.

## Chain-of-Verification (CoVe) protocol

For each claim in a batch:

1. **Restate the claim** — re-read `claim.text` and confirm understanding of what is being asserted.
2. **Generate verification questions** — produce 2–4 questions whose answers, *if affirmative*, would substantiate the claim. Question shapes vary by claim type (see below).
3. **Answer each question** — using only the cited source (Grep on `claim.source_uri` for the relevant passage; do NOT re-read whole sources unless the claim is foundational).
4. **Assign verdict** — based on the verification answers, assign one of `verified`, `unverifiable`, `contradicted`, `single_sourced` (see Verdict criteria below).
5. **Flag dissent** — if another claim in `02-graph.json` asserts the contrary and is from a different source (independent provenance), mark `dissent_evidence` in both critiques.

## Verification-question shapes by claim type

| Claim type | Question pattern |
|---|---|
| **Vendor benchmark** ("Service X has 99.99% uptime") | "Is the SLA contractually binding? What's the measurement window? What exclusions apply?" |
| **Regulatory citation** ("CISA recommends quarterly credential rotation") | "Is this an actual published recommendation? What is the publication date? Is it advisory or binding?" |
| **Telemetry summary** ("p99 latency was 180ms in Q3") | "What was the population? Was the data sampled or full-population? Were outliers excluded?" |
| **Conceptual claim** ("Saga pattern requires idempotent operations") | "Is this universally true or context-dependent? What counterexamples exist?" |
| **Comparative claim** ("Service A is faster than Service B") | "Under what workload? What metric? Was the comparison apples-to-apples?" |

When a claim doesn't fit a clear category, use the conceptual-claim pattern as a fallback.

## Adversarial-prompt patterns

For high-stakes claims (those that will likely drive architectural decisions), supplement CoVe with adversarial probes:

- **"What would falsify this?"** — what evidence would invalidate the claim?
- **"Who benefits from this being true?"** — does the source have an incentive to overstate?
- **"What does the absence of <X> imply?"** — is silence on a related point telling?

Adversarial probes do NOT change the verdict directly but inform `confidence` (low when adversarial probes surface concerns even though CoVe questions are answered).

## Verdict criteria

| Verdict | Criteria |
|---|---|
| `verified` | All CoVe verification questions answered affirmatively from the cited source; no contradicting evidence in graph. |
| `unverifiable` | Required answers are absent from the cited source (the source doesn't contain enough information to substantiate). |
| `contradicted` | At least one CoVe answer is negative or another claim in `02-graph.json` directly negates this one (and the contradicting claim is itself substantiated). |
| `single_sourced` | The claim is verified, but no other independent source corroborates it. Use this verdict instead of `verified` when the claim is consequential AND only one source supports it. |

**`single_sourced` is not a failure verdict.** It is a transparency verdict — the report should surface single-sourced claims explicitly so readers know what isn't independently corroborated.

## Dissent-flagging rules

A claim has dissent if **all** of the following hold:

1. Another claim in `02-graph.json` asserts the contrary (not just orthogonal — directly negates).
2. The two claims have different `source_provenance` (e.g., `vendor` vs. `independent`).
3. Both claims are individually verifiable on their own sources.

When dissent is found:
- Populate `dissent_evidence` field in both critiques (each pointing to the other's `claim_id`).
- Do NOT auto-resolve. The Synthesizer reports both perspectives in the final report, transparently.

**Anti-pattern:** marking dissent when one of the contradictory claims is itself `unverifiable`. That's not dissent, it's just one claim being wrong — keep the verifiable one and let the unverifiable one carry its own verdict.

## Constraint-violation flagging

Read `00-manifest.json` `constraints.hard_constraints[]` at task start. For each claim, if its assumed substrate / behavior / requirement violates a hard constraint, mark the violation in critique notes. The Framer (downstream) uses this when filtering claim clusters into decision frames.

Example: hard_constraint = `compliance:SOC2`; claim text = "stores PII in unencrypted log streams". This claim is `verified` (the source is accurate) but `violates_constraint`. Both signals propagate.

## Common over-confident claim shapes

Watch for and flag these — extractor sometimes lets them through, and Critic should downgrade `confidence` even when verdict is `verified`:

- **Universal quantifiers** — "always", "never", "all customers", "every workload". Real-world systems have edge cases; verify scope.
- **Marketing comparatives** — "industry-leading", "best-in-class". Often unmeasured; downgrade to `low` confidence.
- **Numeric vagueness** — "significantly faster", "much more reliable". Demand specific numbers; if unavailable, `unverifiable`.
- **Implied causation** — "X enables Y" when source only shows correlation. Verify mechanism.

## Selective re-reading discipline

CoVe answers come from selective Grep on the cited source, NOT whole-source re-read. Per Design §4.11:

```
Grep(pattern=<key term from claim.text>, path=claim.source_uri, output_mode='content', context_lines=3)
```

If the Grep result is insufficient and a whole-source re-read seems warranted, that is a signal the claim was poorly extracted (text too vague). Mark `verdict: unverifiable` with a note explaining "source context insufficient to verify; consider re-extraction."

## Output contract

Write to per-batch `03-critique-batch-N.json`:
```json
{
  "critiques": [
    {
      "claim_id": "C-0023",
      "verification_questions": ["...", "..."],
      "verification_answers": ["...", "..."],
      "verdict": "verified",
      "confidence": "high",
      "dissent_evidence": null,
      "violates_constraint": null,
      "notes": "..."
    }
  ]
}
```

Orchestrator merges per-batch files into `03-critique.json`.

## See also

- `references/examples.md` — 6–8 worked CoVe sequences across claim types
- `references/anti-patterns.md` — rubber-stamping, dissent-marking on unverifiable claims
