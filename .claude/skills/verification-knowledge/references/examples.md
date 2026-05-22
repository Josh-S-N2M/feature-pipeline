# CoVe Verification Examples

Worked CoVe sequences across the 5 verification-question shape patterns.

## Vendor benchmark

**Claim C-0001:** "Acme Cloud achieves 99.99% uptime backed by a financial SLA."

Questions:
1. Is the 99.99% uptime an SLA commitment or aspirational target?
2. Measurement window?
3. Exclusions?
4. Financial SLA capped or proportional?

Answers (from selective Grep on source):
1. SLA commitment, contractually binding.
2. Rolling 30-day window, per region.
3. Excludes planned maintenance ≥48h notice.
4. Capped at one month's service credit.

**Verdict:** `verified` with `confidence: medium` — surface claim implies stronger commitment than contract delivers.

## Single-sourced

**Claim C-0042:** "Service B is faster than Service A under high concurrency."
Source: community blog.

Questions:
1. Definition of "high concurrency"?
2. Apples-to-apples comparison?
3. Author affiliation?

Answers:
1. >100 concurrent users in their workload.
2. Same dataset and hardware, different Service tunings.
3. Independent practitioner, no vendor affiliation.

**Verdict:** `single_sourced` — verified on the source, but no other independent source corroborates.

## Conceptual contradiction

**Claim C-0080:** "Saga pattern is always preferable to two-phase commit for microservice transactions."

Question: "Is this universally true?"

Answer: source asserts universality but the graph contains C-0083 ("two-phase commit is preferable when latency is bounded and participants are reliable") from an independent academic source.

**Verdict:** `contradicted` with `dissent_evidence: "C-0083"`. Synthesizer surfaces both perspectives.

## Telemetry summary

**Claim C-0120:** "p99 latency was 180ms in Q3."

Questions:
1. Population (sampled or full)?
2. Outliers excluded?

Answers:
1. Full population per source.
2. No exclusion stated; assume p99 includes all observations.

**Verdict:** `verified`, `confidence: high`.

## Comparative — adversarial probe surfaces concern

**Claim C-0150:** "Vendor X is the fastest service mesh."

CoVe verifies the source asserts this; adversarial probe ("Who benefits from this being true?") notes Vendor X is the source author. Combined with single-source structure → `verdict: single_sourced`, `confidence: low`, note "Vendor self-comparison."
