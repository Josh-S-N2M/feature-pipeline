# Claim Extraction Examples

Worked good/bad pairs across the seven `source_type` values. Loaded on demand by the Extractor when the source-type taxonomy or claim-shape rule is ambiguous.

## Vendor whitepaper

**Source:** "Acme Cloud achieves 99.99% uptime backed by a financial SLA, processes over 10 billion events per day, and is trusted by Fortune 500 companies."

✅ **Three separate claims:**
- "Acme Cloud achieves 99.99% uptime backed by a financial SLA." (high confidence)
- "Acme Cloud processes over 10 billion events per day." (medium; marketing aggregate)
- "Acme Cloud is trusted by Fortune 500 companies." (low; consider dropping — non-assertive marketing)

❌ **Bad — compound claim:** "Acme is fast, reliable, and Fortune 500-trusted."

## Academic paper

**Source:** "GraphRAG improves QA accuracy by 23% over baseline RAG (p < 0.01, n=1000) on the Wikipedia subset."

✅ Verbatim, including statistical metadata. `source_provenance: academic_peer_reviewed`.

❌ **Bad — inference:** "GraphRAG is the best RAG variant." Source asserts a bounded improvement; "best" is unsupported.

## Regulator publication

**Source:** "CISA recommends MFA on all administrative accounts within 90 days of this advisory."

✅ Verbatim — regulatory wording is consequential.

## Internal audit (year-only date)

**Source:** From "2024 SOC 2 Type II Report": "Control CC6.1 was tested across 47 systems and operates effectively."

✅ Set `date: "2024-01-01"` with note "Source dated to year only."

## Community blog (vendor employee)

**Source:** Substack post by a Datadog engineer: "Aggregating logs at the collector saves 40% bandwidth on egress."

✅ `source_type: community_blog`, `source_provenance: vendor` — provenance reflects affiliation, not platform.

## API documentation

**Source:** "/v2/users returns up to 100 per page; pagination via `page` and `per_page`."

✅ Close-paraphrase: "The /v2/users endpoint returns up to 100 users per page with pagination via page and per_page query parameters."

## Telemetry summary

**Source:** "Q3 2025: incident count 12 (down from 18 in Q2); MTTR median 47 minutes (down from 62)."

✅ Two separate claims (count + MTTR). Each has `confidence: high` (numbers are precise).
