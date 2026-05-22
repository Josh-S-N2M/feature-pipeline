---
name: claim-extraction-knowledge
description: Knowledge skill loaded by synth-extractor. Carries source-type taxonomy, claim-shape rules with examples, provenance-tagging guide, date-extraction heuristics, and the verbatim-vs-close-paraphrase rule.
user-invocable: false
---

# Claim Extraction Knowledge

Loaded by `synth-extractor` via `skills: [claim-extraction-knowledge]`. The agent reads this SKILL.md in full at task start and consults `references/examples.md` and `references/anti-patterns.md` on demand.

## Source-type taxonomy

The `source_type` field in `claim.schema.json` takes one of seven values, drawn from this taxonomy:

| Value | Meaning | Typical signals |
|---|---|---|
| `vendor_whitepaper` | Vendor-authored marketing/technical doc | Product page, "Why <Vendor>", marketecture diagrams |
| `academic` | Peer-reviewed paper or preprint | DOI, arXiv ID, conference proceedings |
| `regulator` | Regulatory body publication | EU AI Act, NIST AI RMF, SEC filings |
| `internal_audit` | Internal compliance/security report | "Confidential", named auditor, reporting period |
| `community_blog` | Independent practitioner write-up | Substack, dev.to, personal blog with stated affiliation |
| `api_doc` | Reference documentation for an API | Endpoint tables, parameter specs, SDKs |
| `telemetry_summary` | Aggregated operational metrics | "Q3 SLO report", percentile latencies, incident counts |

**Disambiguation rule:** when a doc could fit two categories (e.g., a vendor whitepaper that includes telemetry), tag with the **primary** category that most accurately reflects authorship intent.

## Claim-shape rules

**Every claim has a `source_uri`.** No exceptions. If no `source_uri` is identifiable, the assertion is not a claim — drop it.

**One assertion per claim.** "Service X has 99.99% uptime and supports OAuth 2.0" → two claims (one about uptime, one about OAuth). Compound assertions are merge-bait for downstream phases.

**Verbatim or close-paraphrase only.** The `text` field is faithful to the source. "Close-paraphrase" means: same factual content, same entity references, same scope qualifiers; word reordering and pronoun resolution acceptable. Inference, generalization, or commentary is not permitted.

## Provenance-tagging guide

The `source_provenance` field captures *authorship context*, distinct from `source_type` (which captures document genre):

| `source_type` | Common `source_provenance` mappings |
|---|---|
| `vendor_whitepaper` | `vendor` (vendor authored for marketing) — almost always |
| `academic` | `academic_peer_reviewed` (published in venue) or `academic_preprint` (arXiv-only) |
| `regulator` | `regulator` |
| `internal_audit` | `internal` |
| `community_blog` | `community` (independent), `vendor` (employee blogging about employer's product), or `independent` (analyst/consultant) — disambiguate from author affiliation |
| `api_doc` | `vendor` (the vendor whose API it is) |
| `telemetry_summary` | `internal` (own metrics) or `vendor` (vendor publishing customer aggregate) |

**Edge case:** a vendor whitepaper *commissioned* by a regulator (e.g., a SOC 2 Type II report). The doc is `source_type: vendor_whitepaper` but `source_provenance: regulator` because the regulatory mandate is what makes the assertions consequential. Note this distinction explicitly in `notes`.

## Date-extraction heuristics

The `date` field is REQUIRED when extractable, explicitly `null` otherwise. Heuristics, in priority order:

1. **Stated publication date** — front-matter, masthead, "Last updated:" line. Strongest signal.
2. **Internal references to recency** — "as of Q2 2026", "in the last 12 months". Use the latest plausibly-stated date.
3. **Filename date hints** — `report-20260315.md`, `q3-2025-summary.pdf`. Use only when (1) and (2) are absent.
4. **None of the above** → set `date: null`. Do NOT infer from file mtime — file mtime is irrelevant to source date.

**Format:** ISO 8601 date (`YYYY-MM-DD`) or `null`. Year-only sources (e.g., "2024 SOC report") → `2024-01-01` with a note explaining the year-only granularity.

## Verbatim vs. close-paraphrase rule

**Verbatim:** copy the exact words. Use when the source's wording carries semantic weight beyond its plain meaning (legal text, vendor commitments, benchmark numbers).

**Close-paraphrase:** same factual content, lightly restructured. Use when the source uses rhetorical or stylistic devices that don't survive extraction.

**Three concrete examples:**

1. Source: "Our service maintains 99.99% uptime, backed by a financial SLA." → Verbatim. The numeric commitment + SLA reference are load-bearing.
2. Source: "We are excited to announce that Service X now supports OAuth 2.0, the industry-standard authorization protocol." → Close-paraphrase: "Service X supports OAuth 2.0." Strip marketing flourish.
3. Source: "CISA advises that organizations rotate credentials quarterly." → Verbatim. Regulatory advisory wording is consequential.

## Output contract

Write to `<output_path>` (orchestrator-supplied) a JSON object:
```json
{ "claims": [ <claim> , ... ] }
```
where each `<claim>` conforms to `claim.schema.json`. The Layer A validator runs after write.

## Recursion safety (secondary check)

Even though the orchestrator excludes `output/synthesis-*/` from discovery, this agent re-checks: if the `<source_path>` matches `output/synthesis-*/`, refuse to extract and emit an error to the orchestrator. Defense in depth for invariant 7.

## See also

- `references/examples.md` — 8–12 worked good/bad pairs (one per source type)
- `references/anti-patterns.md` — common mistakes the agent must avoid
