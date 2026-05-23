---
id: research-note-T-002
topic: hannesj/mcp-openapi-schema MCP server
feature: devcontainer-mcp-provisioning-r1
version: 1.0.0
status: complete
generated: 2026-05-23T00:00:00Z
generated_by: discovery-external-researcher
---

# T-002 — `hannesj/mcp-openapi-schema` MCP server

## Topic and question

**Topic:** `hannesj/mcp-openapi-schema` MCP server.

**Research question:** Install / transport / tool surface / auth / version-pinning for `hannesj/mcp-openapi-schema`. This server exposes OpenAPI specs to MCP clients for schema lookup.

**KB-gap justification (from Research Plan):** Vendor-specific; not covered in KB.

## Executive summary

`mcp-openapi-schema` is a Node.js (ESM) MCP server authored by Hannes Junnila that loads a local OpenAPI 3.x file (JSON or YAML) and exposes 10 read-only schema-lookup tools to MCP clients. It is published on npm as `mcp-openapi-schema@0.0.1` (MIT, single release dated 2025-03-13) and is run via `npx -y mcp-openapi-schema <path-to-spec>`. Transport is **stdio** (confirmed in source via `StdioServerTransport` from `@modelcontextprotocol/sdk`). It has **no authentication**: the server reads a local spec file and emits schema fragments — no outbound HTTP, no credentials. On the project's `python:1-3.11-bookworm` base image, `nodejs` + `npm` must be present (devcontainer feature `ghcr.io/devcontainers/features/node` is the standard path). Version-pinning recommendation: pin to `mcp-openapi-schema@0.0.1` explicitly (the only published version) rather than relying on `npx -y` resolving "latest", because future releases may change tool shapes and `0.0.1` is a pre-1.0 zero-version that could undergo breaking churn.

## Findings

### F-1 — Package identity, license, and release state

**Claim.** The npm package `mcp-openapi-schema` is at version `0.0.1`, MIT-licensed, authored by Hannes Junnila, first and only published on 2025-03-13. Dependencies are `@apidevtools/swagger-parser ^10.1.1`, `@modelcontextprotocol/sdk ^1.7.0`, `js-yaml ^4.1.0`, `zod ^3.24.2`. Entry point is `index.mjs`; `bin` exposes a `mcp-openapi-schema` command.

**Source.** npm registry — `https://registry.npmjs.org/mcp-openapi-schema` (accessed 2026-05-23); GitHub repo `package.json` at `https://github.com/hannesj/mcp-openapi-schema/blob/master/package.json` (accessed 2026-05-23). Author: Hannes Junnila.

**Quote (≤15 words).** Package description: "A Model Context Protocol server that exposes OpenAPI schema information to Large Language Models" (≤15 words; from `package.json`).

**Confidence.** High — official primary source (npm registry + repository `package.json`).

**Caveats.** Pre-1.0 version (0.0.1) with no release history. Single published version means there is no observed track record of API stability. The package has been static since March 2025 (~14 months as of research date) — could indicate either "stable enough" or "abandoned"; no further signal available.

### F-2 — Transport is stdio

**Claim.** The server communicates over stdio. The `index.mjs` source imports `StdioServerTransport` from `@modelcontextprotocol/sdk/server/stdio.js` and connects the server to it as the sole transport. There is no HTTP/SSE option.

**Source.** Repository source `https://github.com/hannesj/mcp-openapi-schema/blob/master/index.mjs` (accessed 2026-05-23).

**Quote (≤15 words).** `import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";` (14 tokens; identifies the transport import).

**Confidence.** High — verified in source code of the repository.

**Caveats.** No HTTP/SSE transport is available; an HTTP wrapper would have to be built externally. For a local devcontainer scenario, stdio is the standard and recommended MCP transport — no caveat for this project.

### F-3 — Tool surface (10 read-only schema-inspection tools)

**Claim.** The server exposes 10 tools, all read-only against the loaded OpenAPI spec, with no mutation/write operations:

1. `list-endpoints` — list all API paths + HTTP methods with summaries.
2. `get-endpoint` — full detail for one endpoint (parameters, responses).
3. `get-request-body` — request body schema for an endpoint/method.
4. `get-response-schema` — response schema for an endpoint/method/status.
5. `get-path-parameters` — parameters for a given path.
6. `list-components` — list `components/*` (schemas, responses, parameters, etc.).
7. `get-component` — fetch one component definition.
8. `list-security-schemes` — list the spec's declared security schemes.
9. `get-examples` — examples attached to components or endpoints.
10. `search-schema` — full-text search across paths, operations, and schemas.

Output is rendered as YAML for LLM consumption.

**Source.** GitHub README at `https://github.com/hannesj/mcp-openapi-schema` (accessed 2026-05-23). Cross-confirmed by Awesome MCP Servers listing at `https://mcpservers.org/servers/hannesj/mcp-openapi-schema` and Playbooks listing at `https://playbooks.com/mcp/hannesj/mcp-openapi-schema`.

**Quote (≤15 words).** README on `search-schema`: "Searches across paths, operations, and schemas" (6 tokens; verbatim short fragment).

**Confidence.** High — tool list reproduced consistently across primary repo, two independent third-party catalogs.

**Caveats.** Tool names use hyphenated kebab-case (`list-endpoints`, not `listEndpoints`). Clients that munge tool names should be checked.

### F-4 — Installation on Debian-bookworm + Node toolchain

**Claim.** Installation requires Node.js + npm. The standard invocation is `npx -y mcp-openapi-schema /absolute/path/to/openapi.yaml`. For Claude Code CLI registration: `claude mcp add openapi-schema npx -y mcp-openapi-schema`. For declarative config (e.g., Claude Desktop / `.mcp.json`):

```json
{
  "mcpServers": {
    "openapi-schema": {
      "command": "npx",
      "args": ["-y", "mcp-openapi-schema", "/ABSOLUTE/PATH/TO/openapi.yaml"]
    }
  }
}
```

The project's base image (`mcr.microsoft.com/devcontainers/python:1-3.11-bookworm`) does **not** include Node.js by default. The devcontainer must add `ghcr.io/devcontainers/features/node:1` (or install Node via apt/nodesource) to make `npx` available.

**Source.** GitHub README at `https://github.com/hannesj/mcp-openapi-schema` (accessed 2026-05-23); Microsoft devcontainer Python image documentation (general knowledge of `python:*-bookworm` images — they ship Python toolchain but not Node).

**Quote (≤15 words).** README install: `npx -y mcp-openapi-schema [path-to-schema-file]` (≤15 words; verbatim install line).

**Confidence.** High for the install command (from README). Medium for the bookworm-base statement — based on the well-documented composition of `mcr.microsoft.com/devcontainers/python` images, but not directly cited here.

**Caveats.** `package.json` does not declare an `engines.node` constraint. The `@modelcontextprotocol/sdk@^1.7.0` requires Node ≥18 in practice. Recommend Node 20 LTS via the devcontainer feature.

### F-5 — No authentication, local-only data plane

**Claim.** The server reads a local OpenAPI file path passed as a CLI argument and exposes schema fragments to the MCP client over stdio. There is no outbound HTTP, no API-key handling, no auth flow. The `list-security-schemes` tool reports the security schemes **declared in the spec** — it does not authenticate against the API the spec describes.

**Source.** GitHub README at `https://github.com/hannesj/mcp-openapi-schema` (single quote from this source already used in F-3); cross-confirmed by Playbooks listing `https://playbooks.com/mcp/hannesj/mcp-openapi-schema` which paraphrases: "None required (schema files are local; no external API credentials needed)".

**Quote (≤15 words).** From Playbooks listing: "No external API credentials needed" (5 tokens; paraphrased confirmation).

**Confidence.** High — consistent with the read-only stdio architecture and the absence of any HTTP client dependency in `package.json`.

**Caveats.** Operator must still treat the spec file as in-scope data. If the loaded spec contains sensitive endpoint paths or examples (real customer IDs, internal-only URLs), those become visible to the LLM via this server. Choice of which spec to load is a sensitive design decision.

### F-6 — Version-pinning posture

**Claim.** Only one version (`0.0.1`) has been published. `npx -y mcp-openapi-schema` will resolve to whatever is "latest" at the moment of invocation. For reproducible devcontainer provisioning, pin the version explicitly: `npx -y mcp-openapi-schema@0.0.1 …`. The pre-1.0 version number is a signal that breaking changes may land without semver protection in any future release; pinning is recommended both for reproducibility and to avoid a future tool-shape change silently breaking client configurations.

**Source.** npm registry `https://registry.npmjs.org/mcp-openapi-schema` (single release listed); semver convention for `0.x.y` versions per npm semver docs (general practice).

**Quote (≤15 words).** No additional quote — both supporting sources have already been quoted under F-1; per discipline, claim is paraphrased.

**Confidence.** Medium — sources confirm "one version exists"; the pinning recommendation is the researcher's synthesis based on standard supply-chain hygiene, not a quote from the project.

**Caveats.** If the project remains unmaintained, a pinned `0.0.1` will eventually develop CVE exposure via its transitive deps (notably `js-yaml`, `swagger-parser`). The devcontainer should treat MCP server packages as periodic-review supply-chain dependencies.

## Synthesis (researcher analysis)

For this feature, `mcp-openapi-schema` is a near-perfect fit on architectural grounds:

- **Transport alignment.** Stdio is the canonical local-devcontainer MCP transport — no HTTP listener, no port to manage, no auth surface.
- **Read-only by construction.** The tool surface is entirely schema-inspection. There is no attack path where an LLM call mutates a remote system through this server. The only sensitivity is which spec file is loaded (F-5 caveat).
- **Zero auth simplifies provisioning.** No secret needs to live in the devcontainer image or in `.mcp.json` for this server, which contrasts favorably with vendor MCP servers that require API tokens.
- **Toolchain cost.** The project's base image does not ship Node; adding the Node devcontainer feature is a one-line addition but is a real dependency that must be tracked.

The dominant risk is **project maintenance**: a single `0.0.1` release from March 2025 with no follow-ups. Two reasonable mitigations: (a) pin `@0.0.1` and accept that a periodic supply-chain review is required; (b) fork to an org-owned mirror if longer-term reliance is anticipated. The feature design should call this out explicitly in the ADR that selects this server.

The version-pin recommendation is also the most defensible posture even if the project later resumes releases — pre-1.0 versions provide no semver guarantees, so unpinned use is unsafe for a reproducible devcontainer.

## Acceptance-criteria check

| # | Criterion | Disposition | Notes |
|---|---|---|---|
| 1 | Install command workable on Debian-bookworm + Node/Python toolchain | **Satisfied** | `npx -y mcp-openapi-schema@0.0.1 <path>` works once `ghcr.io/devcontainers/features/node:1` is added; Python toolchain not required (Node-only). See F-4. |
| 2 | Transport recommendation (stdio vs HTTP) | **Satisfied** | Stdio only; this is also the recommended transport for the local-devcontainer use case. See F-2. |
| 3 | Tool surface enumeration with descriptions | **Satisfied** | 10 tools enumerated with descriptions. See F-3. |
| 4 | Auth mechanism | **Satisfied** | None. No credentials, no outbound network. Local file read + stdio only. See F-5. |
| 5 | Version-pinning recommendation | **Satisfied** | Pin `@0.0.1` explicitly; do not rely on `npx -y`'s latest-resolution. Pre-1.0 = no semver protection. See F-6. |
| 6 | ≥3 independent reputable sources | **Satisfied** | (1) GitHub repo + source code (hannesj/mcp-openapi-schema) — primary; (2) npm registry — primary; (3) mcpservers.org Awesome MCP Servers — independent catalog; (4) playbooks.com MCP catalog — independent catalog. Four sources, three independent of the author. |

## Open questions

1. **Maintenance signal.** No way to tell from sources whether the absence of releases since 2025-03-13 reflects "done, no changes needed" or "abandoned". Recommend the design ADR pick this up as a known risk to revisit periodically.
2. **Maximum spec size.** No documented limit on the size of the loaded OpenAPI file. `@apidevtools/swagger-parser` parses the entire spec into memory; very large specs (multi-MB) could affect MCP server startup latency. Not benchmarked here.
3. **Multiple-spec support.** The server takes a single file path as a CLI argument. To expose multiple specs simultaneously, multiple server instances must be registered (each as a separate MCP server with a distinct name). Confirmed by the install examples but not stress-tested.
4. **Bookworm specifics.** The "Debian-bookworm" line of the acceptance criterion is satisfied via the Node devcontainer feature, not via apt directly. If the design instead requires installation from Debian's `nodejs` apt package, that path was not researched (Debian bookworm ships Node 18 LTS; the SDK should work but was not verified).

## Source list

1. **GitHub — `hannesj/mcp-openapi-schema` repository.** `https://github.com/hannesj/mcp-openapi-schema` — README, source code, `package.json`. Accessed 2026-05-23. Primary/official.
2. **GitHub — `index.mjs`.** `https://github.com/hannesj/mcp-openapi-schema/blob/master/index.mjs` — used to verify `StdioServerTransport` import. Accessed 2026-05-23. Primary/official.
3. **GitHub — `package.json`.** `https://github.com/hannesj/mcp-openapi-schema/blob/master/package.json` — dependency list, license, version. Accessed 2026-05-23. Primary/official.
4. **npm registry — `mcp-openapi-schema`.** `https://registry.npmjs.org/mcp-openapi-schema` — version history (only 0.0.1), publish date (2025-03-13), MIT license. Accessed 2026-05-23. Primary registry source.
5. **Awesome MCP Servers — listing.** `https://mcpservers.org/servers/hannesj/mcp-openapi-schema` — independent catalog. Accessed 2026-05-23. Secondary; reputable community catalog.
6. **Playbooks — MCP catalog entry.** `https://playbooks.com/mcp/hannesj/mcp-openapi-schema` — independent catalog. Accessed 2026-05-23. Secondary; community catalog.
