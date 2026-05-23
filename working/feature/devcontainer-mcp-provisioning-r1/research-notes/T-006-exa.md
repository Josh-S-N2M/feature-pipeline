---
id: RN-T-006-exa
doc_type: research-note
version: 1.0.0
status: draft
feature_slug: devcontainer-mcp-provisioning-r1
topic_id: T-006
topic_name: Exa MCP server
generated: 2026-05-23T00:00:00Z
generated_by: discovery-external-researcher
---

# T-006 — Exa MCP server

## Topic and question

**Topic:** Exa MCP server (web research / search MCP).

**Research question:** Install / transport / tool surface / **auth shape** (header vs URL query parameter — resolves PRD UI-3) / version-pinning for Exa MCP.

**KB-gap justification (from Research Plan v3):** Wrong transport-auth choice causes FR-4 per-server probe to fail at acceptance — release-blocker risk per PRD Risks.

**Source constraints:** docs.exa.ai / Exa github / at least one community reference.

## Executive summary

Exa's hosted MCP server is at `https://mcp.exa.ai/mcp` and is invoked over the streamable-HTTP MCP transport. The server **accepts both an `x-api-key` HTTP header and an `exaApiKey` URL query parameter**; the two upstream-canonical sources each show one form (docs.exa.ai shows the header; the `exa-labs/exa-mcp-server` GitHub README shows the query parameter), and the DeepWiki cross-reference confirms both are wired in the server's auth resolver, with query parameter taking precedence over header. **Recommendation for this feature: use the `x-api-key` HTTP header form.** Reasons: (a) it keeps the secret out of the URL (logs, ps listings, server access logs), (b) the docs.exa.ai canonical example uses it, (c) it aligns with the way Codespaces secrets are normally injected (env var → header at probe time), and (d) the FR-4 probe is a one-shot HTTP request where header injection is the standard pattern. The npx-based local server (`exa-mcp-server` on npm) is an alternate stdio transport that takes `EXA_API_KEY` as an env var; for a Codespaces devcontainer with a Codespaces secret already exposed as `EXA_API_KEY`, the hosted-HTTP-with-header form is simpler and has fewer moving parts than spawning a Node process. Version-pinning for the hosted endpoint is server-side (no client pin); for the npm fallback, pin to a specific `exa-mcp-server@<version>` if used.

## Findings

### F1 — Hosted MCP endpoint URL and transport

**Claim.** Exa publishes a hosted MCP server at `https://mcp.exa.ai/mcp` served over the MCP streamable-HTTP transport. The canonical Claude Code install is `claude mcp add --transport http exa https://mcp.exa.ai/mcp`.

**Source.** Exa Docs — "Web Search MCP" reference (docs.exa.ai redirects to exa.ai/docs/reference/exa-mcp); GitHub `exa-labs/exa-mcp-server` README.

- https://exa.ai/docs/reference/exa-mcp — "Web Search MCP — Exa", Exa Labs, current as of 2026-05-23.
- https://github.com/exa-labs/exa-mcp-server — "exa-labs/exa-mcp-server: Exa MCP for web search and web crawling", Exa Labs.

**Quote (≤15 words; from docs.exa.ai).** `claude mcp add --transport http exa https://mcp.exa.ai/mcp`

**Confidence.** High — primary vendor docs and vendor-owned GitHub repo.

**Caveats.** Hosted endpoint is a managed SaaS; Exa controls server-side version. Network must reach mcp.exa.ai. For air-gapped or offline Codespaces, only the local npx mode works (see F4).

### F2 — Auth shape: `x-api-key` HTTP header (canonical docs.exa.ai form)

**Claim.** The docs.exa.ai canonical MCP-client configuration shows the API key passed as an HTTP header named `x-api-key`, with the bare URL `https://mcp.exa.ai/mcp` as the endpoint. No query string is shown in this form.

**Source.** Exa Docs — "Web Search MCP" (https://exa.ai/docs/reference/exa-mcp).

**Quote (≤15 words).** `"headers": { "x-api-key": "YOUR_EXA_API_KEY" }`

**Confidence.** High — primary vendor documentation.

**Caveats.** The header name is lowercase `x-api-key` (HTTP header names are case-insensitive in transit but the docs show this exact casing).

### F3 — Auth shape: `?exaApiKey=…` URL query parameter (GitHub README form)

**Claim.** The `exa-labs/exa-mcp-server` GitHub README documents an alternative form that embeds the API key in the URL itself as the `exaApiKey` query parameter, combined with a `tools=` parameter to enable specific tools.

**Source.** GitHub `exa-labs/exa-mcp-server` README (https://github.com/exa-labs/exa-mcp-server/blob/main/README.md).

**Quote (≤15 words).** `https://mcp.exa.ai/mcp?exaApiKey=YOUR_KEY&tools=web_search_exa`

**Confidence.** High — vendor-owned repository, README authored by Exa Labs.

**Caveats.** Query-parameter form leaks the key into URL logs (browser history, proxy logs, server access logs, MCP client config dumps). Acceptable for quick demos; not recommended for a persisted devcontainer configuration. The hosted server accepts both forms — see F4.

### F4 — Both auth shapes are supported; precedence rules

**Claim.** The Exa MCP server's auth resolver accepts (in priority order): (1) `exaApiKey` query parameter, (2) `Authorization: Bearer …` header (also accepts JWTs for OAuth flows), (3) `EXA_API_KEY` environment variable (for the local stdio/npx mode). The `x-api-key` header shown in the docs is the documented header form for the hosted endpoint. When more than one credential is present, the query parameter wins.

**Source.** DeepWiki — auto-generated reference for `exa-labs/exa-mcp-server` (https://deepwiki.com/exa-labs/exa-mcp-server/6.2-authentication-and-api-keys). Community-curated mirror of the codebase that introspects `src/utils/auth.ts` and `api/mcp.ts`.

**Quote (≤15 words).** "Both mechanisms are supported for flexibility, particularly in environments where header control is restricted."

**Confidence.** Medium — DeepWiki is a third-party introspection of the open-source code, not vendor-authored prose, but it cites specific source files (`src/utils/auth.ts`, `api/mcp.ts`) in the public repo, and the conclusion is corroborated by both vendor sources independently showing one each.

**Caveats.** DeepWiki content is auto-generated and could drift if the underlying repo changes. The precedence ordering is the most fragile claim and should be re-verified at integration time if it matters for the design.

### F5 — Local stdio mode via npm package `exa-mcp-server`

**Claim.** A local stdio-transport mode is available by running the `exa-mcp-server` npm package via `npx -y exa-mcp-server`, with the API key supplied via the `EXA_API_KEY` environment variable. This is the alternative to the hosted HTTP endpoint.

**Source.** GitHub `exa-labs/exa-mcp-server` README and the npm package page.

- https://github.com/exa-labs/exa-mcp-server
- https://www.npmjs.com/package/exa-mcp-server

**Quote (≤15 words; from GitHub README).** `npx -y exa-mcp-server`

**Confidence.** High — primary vendor sources.

**Caveats.** Requires Node.js in the devcontainer (the base is Debian-bookworm + Python 3.11 per PRD; Node is not in that base). Adds an installation surface and a spawned-process lifecycle the hosted form avoids. Use only if hosted endpoint is not reachable.

### F6 — Tool surface

**Claim.** Default-enabled tools on the hosted Exa MCP are:

- `web_search_exa` — web search returning clean extracted content.
- `web_fetch_exa` — full webpage content extraction (returned as markdown).

Optional (must be opted in via `?tools=…` or equivalent):

- `web_search_advanced_exa` — advanced search with filters, date ranges, and per-result summaries.

Deprecated but still resolvable (redirect to newer tools): `get_code_context_exa`, `company_research_exa`, `crawling_exa`, `people_search_exa`, `linkedin_search_exa`. The legacy `find_similar` named in the original research question is not present in the current default surface — Exa appears to have consolidated similarity into `web_search_advanced_exa`.

**Source.** docs.exa.ai (https://exa.ai/docs/reference/exa-mcp) and `exa-labs/exa-mcp-server` README.

**Quote (≤15 words; from docs.exa.ai).** `?tools=web_search_exa,web_search_advanced_exa,web_fetch_exa`

**Confidence.** High — both vendor sources agree on the current default set.

**Caveats.** Tool list evolves; the deprecated set may be removed without notice. For FR-4 probe purposes, probing `web_search_exa` (the default) is the safest bet.

### F7 — Version pinning

**Claim.** The hosted endpoint `https://mcp.exa.ai/mcp` is version-managed by Exa server-side; there is no client-visible version pin. The npm package `exa-mcp-server` is published on npm and can be version-pinned in the standard way (`exa-mcp-server@<semver>`); the README does not prescribe a recommended pin.

**Source.** docs.exa.ai, GitHub repo, npm registry page.

- https://www.npmjs.com/package/exa-mcp-server

**Quote (≤15 words; from npm package metadata, paraphrased — no short verbatim quote needed).** [No direct quote; observation from the package page.]

**Confidence.** Medium — absence of an explicit version-pinning section in vendor docs.

**Caveats.** For a "pinned-by-design" feature, prefer the hosted endpoint (server-managed) and rely on the FR-4 probe to detect regressions. If npx fallback is used, pin to a specific semver.

## Synthesis (analysis — not from sources)

The PRD UI-3 question — header vs URL query parameter — has a clear answer once the apparent contradiction between the two vendor sources is resolved: both work, the server accepts either, and the choice is one of operational hygiene. For this feature the deciding factors are:

1. **Secret hygiene.** Codespaces secrets are designed to be exposed as environment variables, not embedded in URLs. The `x-api-key` header form lets the orchestrator read `EXA_API_KEY` from env at probe time and inject it into a single HTTP request without ever writing it into a persisted config URL.
2. **Canonical-docs alignment.** docs.exa.ai (the user-facing reference) shows the header form first; aligning with this form keeps `claude mcp add` syntax in line with what an operator sees when they consult the docs.
3. **Probe testability for FR-4.** The probe is a one-shot HTTP call. Header injection is trivial; query-string injection means the probe has to construct and persist a URL containing the secret, which complicates log redaction.
4. **Transport choice.** Hosted streamable-HTTP at `https://mcp.exa.ai/mcp` is simpler than the npx stdio form (no Node install needed in the Debian-bookworm + Python 3.11 base image). Recommend hosted-HTTP unless network egress is constrained.

**Recommended canonical install (hypothesis for Design):**

```
claude mcp add --transport http exa https://mcp.exa.ai/mcp \
  --header "x-api-key: ${EXA_API_KEY}"
```

(Header-injection syntax for `claude mcp add` should be verified in the Claude Code CLI docs as part of T-007 / per-server install harness design — out of scope for this research note.)

## Acceptance-criteria check

| Criterion | Disposition | Reasoning |
|---|---|---|
| Transport options + recommendation | Satisfied | F1 (hosted HTTP) and F5 (local stdio via npx) enumerated; hosted HTTP recommended in Synthesis. |
| Authentication: header vs URL query — explicit, with canonical example | Satisfied | F2 (header `x-api-key` — docs.exa.ai canonical), F3 (query `?exaApiKey=` — GitHub README), F4 (both supported, precedence: query > Authorization > env). Recommendation: header form. |
| Install command(s) or URL config | Satisfied | F1 gives the `claude mcp add --transport http` form; F5 gives the npx form. |
| Tool surface enumeration | Satisfied | F6 — default set (`web_search_exa`, `web_fetch_exa`), optional (`web_search_advanced_exa`), deprecated list. Note: the original question's `find_similar` and `contents` are not the current tool names; the closest current equivalents are `web_search_advanced_exa` and `web_fetch_exa`. |
| Version-pinning | Partially satisfied | F7 — hosted endpoint is server-managed (no client pin); npm package supports standard semver pinning but no vendor-recommended pin. Marked partial because vendor docs do not prescribe a pin policy. |
| ≥3 independent reputable sources | Satisfied | docs.exa.ai (vendor docs); github.com/exa-labs/exa-mcp-server (vendor repo); deepwiki.com (third-party code introspection); npmjs.com (registry). Four sources. |

## Open questions

1. **OQ-T006-1:** Does `claude mcp add --transport http` accept `--header` (or equivalent) for injecting the `x-api-key` header at install time, or must the header live in a separate config file (e.g., `.claude/mcp.json`)? — Defer to the Claude Code CLI docs check in T-007 / Design.
2. **OQ-T006-2:** When both header and query parameter are present, F4 says query parameter wins. For the FR-4 probe, we should set exactly one. Confirmed — the recommended form is header-only.
3. **OQ-T006-3:** The Exa MCP tool surface evolves (find_similar consolidated into `web_search_advanced_exa`). Which tool name should the FR-4 health probe target? Recommendation: `web_search_exa` (default-enabled, stable name). — Defer to Design.
4. **OQ-T006-4:** Version-pinning for the hosted endpoint is impossible client-side. If the PRD's "pinned-by-design" requirement extends to hosted MCPs, this needs an ADR-level disposition. — Flag for Design composer.

## Source list

1. **Exa Docs — Web Search MCP reference.** https://exa.ai/docs/reference/exa-mcp (docs.exa.ai redirects here). Vendor docs; current as of 2026-05-23. Authoritative.
2. **GitHub `exa-labs/exa-mcp-server` README.** https://github.com/exa-labs/exa-mcp-server (and `/blob/main/README.md`). Vendor-owned repository. Authoritative.
3. **DeepWiki — `exa-labs/exa-mcp-server` § 6.2 Authentication and API Keys.** https://deepwiki.com/exa-labs/exa-mcp-server/6.2-authentication-and-api-keys. Third-party auto-generated reference grounded in the public source files `src/utils/auth.ts` and `api/mcp.ts`. Community-reference confidence; corroborates the dual-mechanism claim.
4. **npm package `exa-mcp-server`.** https://www.npmjs.com/package/exa-mcp-server. Registry metadata for the local stdio mode.
