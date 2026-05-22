# Report Composition Examples

## Three opening paragraphs (same Findings section, three audience tones)

**Source:** decision-frames showing 6 architectural decisions, mix of reversible and one-way.

### audience_depth: executive

```markdown
Our synthesis identifies six architectural decisions central to the proposed system. Three are reversible — we can try them and revisit if they don't work. Three are one-way doors that warrant careful review before commitment. The strongest recommendation: adopt OAuth 2.0 for service-to-service auth (one-way; tenant-wide impact) [auth-research.md](output/auth-research.md). The weakest: caching-layer choice (two-way; service-scoped) is mostly a matter of operational preference [caching-survey.md](output/caching-survey.md).
```

### audience_depth: engineering

```markdown

Six architectural decisions emerged from the claim corpus, partitioned by Bezos reversibility. Two-way doors: caching layer (Redis vs. Memcached vs. ElastiCache), retry budget (token-bucket vs. exponential backoff), log aggregation (Datadog vs. Splunk vs. self-hosted ELK). One-way doors: identity provider (OAuth 2.0 + Auth0 recommended), data-residency boundary (EU-only deployment for SOC2 alignment), observability vendor (Datadog incumbent advantage). RICE-prioritized scoring lands the identity provider decision first [auth-research.md](output/auth-research.md).
```

### audience_depth: mixed

```markdown

Six architectural decisions surfaced — three reversible (caching layer, retry budget, log aggregation; collectively low blast radius) and three one-way doors (identity provider, data residency, observability vendor; tenant-wide impact). The identity-provider decision is the strongest standalone recommendation: OAuth 2.0 with Auth0 honors all hard constraints and scores highest on RICE [auth-research.md](output/auth-research.md). The caching layer is mostly an operational-preference question, with no significant technical differentiation across the three candidates [caching-survey.md](output/caching-survey.md).
```

## ADR-shaped section in main report

```markdown
## Decisions

### D-0001: Use OAuth 2.0 with Auth0 for service-to-service auth

**Class:** Architectural (one-way) | **Blast radius:** Tenant
**Recommendation:** OAuth 2.0 + Auth0 ([ADR-001](adrs/ADR-001-oauth2-auth0.md))

OAuth 2.0 is the established commodity for service-to-service auth [auth-research.md](output/auth-research.md). Auth0 is recommended over Okta and self-hosted Keycloak based on RICE scoring (lower effort, comparable confidence, similar reach). One risk: vendor lock-in to Auth0; mitigated by OAuth 2.0 standard portability.

[Full options enumeration in substrate-options.md → D-0001]
```

## Citation registry (citations.md)

```markdown
# Citations

| Claim | Source | Source URI |
|---|---|---|
| C-0001 | constraint-aware-synthesis.md | output/constraint-aware-synthesis.md |
| C-0002 | constraint-aware-synthesis.md | output/constraint-aware-synthesis.md |
| ... | ... | ... |
```
