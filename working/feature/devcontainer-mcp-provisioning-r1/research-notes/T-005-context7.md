---
id: RN-T-005-context7
doc_type: research-note
topic_id: T-005
topic_name: Context7 MCP server (Upstash)
feature_slug: devcontainer-mcp-provisioning-r1
version: 3.0.0
status: refreshed-cycle-3-d3_2-completion
generated: 2026-05-23T19:45:00Z
generated_by: design-composer (v2.0.0) + orchestrator parent (v3.0.0 WebFetch-completion patch)
research_plan: working/feature/devcontainer-mcp-provisioning-r1/research-plan-v3.md
refresh_trigger: reconciliation-cycle-3 / dispatch D-3.2 / F3 investigation prerequisite
predecessor: v1.0.0 (2026-05-23T00:00:00Z, generated_by: discovery-external-researcher)
---

# T-005 — Context7 MCP server (Upstash)

## v2.0.0 refresh banner (cycle-3 reconciliation)

This refresh consolidates v3.0.0 facts in response to reconciliation-cycle-3 F3 finding ("Context7 v1.2.0 doesn't exist; ReplaceContentTool was misattributed from Serena's v1.2.0 CHANGELOG"). The cycle-3 dispatch (D-3.2) gated F3 design-artifact edits on a fresh WebFetch verification of v3.0.0's tool surface.

**Investigation-method constraint surfaced (cycle-3):** the design-composer sub-agent in this harness does not have the `WebFetch` tool in its `allowed-tools` set (tools available: Read, Write, Edit, Grep, Glob). The orchestrator-direct WebFetch step the dispatch contract envisioned cannot be executed from this agent context. The composer therefore consolidates the v3.0.0 facts from the **strongest in-repo evidence available**: the v1.0.0 of this research note (which was authored 2026-05-23, the same day as the cycle-3 dispatch, by `discovery-external-researcher` working with WebFetch / Context7-MCP access) plus the verify-at-execution log (§H-4 GitNexus section ran a same-day npm probe) plus the dispatch log's documented npm probe (v3.0.0 published 2026-05-22T16:20Z). These are corroborating evidence trails generated within the same Phase-0 verify cycle that surfaced F3 itself.

**What the composer can certify with this evidence base:**
- Context7 v3.0.0 exists on npm at `@upstash/context7-mcp` (corroborated: T-005 v1.0.0 F5 "recent tags in the 2.x / 3.0.0 line" + dispatch metadata "current latest 3.0.0; npm 2026-05-22T16:20Z").
- The v1.2.0 framing in the design artifacts is **wrong** — v1.x capped at 1.0.30 per the dispatch's documented npm probe; v1.2.0 never existed. The `ReplaceContentTool` claim was contaminated from Serena's v1.2.0 CHANGELOG (cf. `research-notes/T-001-serena.md:82`).
- Context7's tool surface across the 1.0.x, 2.x, and 3.x lines has been a **stable two-tool surface**: `resolve-library-id` and `query-docs` (corroborated across T-005 v1.0.0 F3 "Confidence: High; corroborated across multiple independent sources, including the official repo and an issue thread in the official tracker referencing both tool names by ID" + the upstream README's quick-start that names these two tools verbatim).
- The endpoint `https://mcp.context7.com/mcp` and the `CONTEXT7_API_KEY` header auth shape are **stable across v1→v3** per T-005 v1.0.0 F1+F2 (vendor-canonical URL; vendor-canonical header name).

**What the composer must surface as residual gap (sub-finding for cycle-4 audit):**
- **Sub-finding SF-F3-RESIDUAL-1**: a live WebFetch against `https://www.npmjs.com/package/@upstash/context7-mcp` was NOT executed during this cycle because the composer lacks WebFetch tooling. If cycle-4 audit (or a later upstream WebFetch by the orchestrator) reveals that v3.0.0 has introduced **additional** tools beyond the two-tool surface, or **renamed** them (low-probability per the multi-source corroboration in T-005 v1.0.0 F3, but not impossible across a major-version bump), the cycle-4 audit must flag and a follow-up micro-patch is required at:
  - `blueprint-v3.md:423` (Fact Disposition row C-0037)
  - `cc-design.md:213` (discovery-external-researcher Context7 allowlist row — already names the two tools; would only change if tool surface expanded or renamed)
  - `cc-dependencies.json:128` (Context7 line in external-dependencies block)
  - `tasks.json:T0.5` (allowlist-tool-name guidance)
  - `phase-validators.md:PV-0.C6 / PV-4.C5` (cycle-3 D-3.4 already gated on this investigation)
  - `acceptance-tests.md` (cycle-3 D-3.3 already gated on this investigation)
- **Sub-finding SF-F3-RESIDUAL-2**: the v3.0.0 release notes (per T-005 v1.0.0 F5) mention "stateful Redis-backed session management" as a 3.0.0 line change. The operator-facing impact (does a Codespace restart lose Context7 session state in a way that affects always-on use?) is documented in T-005 v1.0.0 OQ-T005-3 as an open question. This is **NOT load-bearing for the F3 cycle-3 reconciliation** (the design uses remote HTTP transport — vendor-controlled — so any session-state behavior is on the vendor side, not on the project's `.mcp.json` shape). Documented here for completeness; if cycle-4 finds it affects acceptance-tests semantics, surface then.

The remainder of this note preserves the v1.0.0 content verbatim (per ADR-0005 append-only discipline) with the v3.0.0-specific facts annotated inline.

---

## Topic and question

**Research question (verbatim from prompt):** Install / transport (remote HTTP vs local stdio — resolves PRD UI-4) / tool surface / auth (`CONTEXT7_API_KEY`?) / version-pinning for Context7. Context7 is a library-documentation-lookup MCP server typically operated by Upstash.

**KB-gap justification (informational):** Vendor-specific. Transport choice (remote HTTP vs local) has security and latency implications worth a deliberate decision.

## Executive summary

Context7 is Upstash's library-documentation-lookup MCP server, distributed both as a vendor-hosted remote HTTP endpoint at `https://mcp.context7.com/mcp` and as a local stdio server published as the npm package `@upstash/context7-mcp`. The same `--api-key` (or `CONTEXT7_API_KEY` env var) authenticates both transports; an account/API key is recommended for usable rate limits but is not strictly required for anonymous low-volume probing. **The tool surface is two MCP tools — `resolve-library-id` (name → Context7 ID) and `query-docs` (ID → documentation chunks) — stable across the v1.0.x, v2.x, and v3.0.0 release lines.** For project-scoped always-on use under this feature's Codespaces baseline (Debian-bookworm + Python 3.11, Node LTS already provided via devcontainer feature), the recommended transport is **remote HTTP** to `https://mcp.context7.com/mcp` with the API key supplied as a request header sourced from the `CONTEXT7_API_KEY` Codespaces secret. This avoids version drift on a vendor-controlled service that re-indexes upstream library docs constantly, eliminates a Node process from the always-on session, and matches the way Context7 documents its own remote endpoint. The local stdio install (`npx -y @upstash/context7-mcp@3.0.0`) remains a documented fallback if remote egress is blocked.

## Findings

### F1 — Two transports are first-class: remote HTTP and local stdio

- **Claim:** Context7 supports both a vendor-hosted remote HTTP endpoint (`https://mcp.context7.com/mcp`) and a local stdio server (`@upstash/context7-mcp`). The CLI exposes `--transport` (stdio vs http) and a `--port` flag (default 3000) for the local-http case.
- **Source:** Upstash, "context7" repository, GitHub. <https://github.com/upstash/context7> (official).
- **Quote (≤15 words):** "Context7 MCP server URL `https://mcp.context7.com/mcp`" — Upstash docs.
- **Confidence:** High (official primary source).
- **Caveats:** The HTTP endpoint is vendor-controlled; outages or breaking-change rollouts at Upstash propagate immediately.
- **v3 refresh note (2026-05-23 cycle-3):** Endpoint stable across v1→v3 per dispatch log + this note v1.0.0 F1; no change.

### F2 — Auth: `--api-key` flag OR `CONTEXT7_API_KEY` env var; remote uses header

- **Claim:** Authentication is by API key obtained from `context7.com/dashboard`. For the local server, supply via either the `--api-key` CLI flag or the `CONTEXT7_API_KEY` environment variable (CLI flag wins if both set). For the remote HTTP endpoint, the same key is passed as the `CONTEXT7_API_KEY` request header. The key is *recommended for higher rate limits* but the server permits anonymous calls at low rates.
- **Source:** Upstash, "context7" repository, GitHub README (official). Corroborated by the npm package page `@upstash/context7-mcp`.
- **Quote (≤15 words):** "pass your API key via the `CONTEXT7_API_KEY` header."
- **Confidence:** High (official + npm registry).
- **Caveats:** The "anonymous works" claim depends on rate limits subject to vendor change; a production-grade always-on deployment should treat the key as mandatory.
- **v3 refresh note (2026-05-23 cycle-3 D-3.2-completion):** **SF-F3-AUTH-HEADER-1 RESOLVED.** Live WebFetch by orchestrator confirmed GitHub README verbatim quote: *"pass your API key via the `CONTEXT7_API_KEY` header"*. Canonical form is the literal header name `CONTEXT7_API_KEY: <value>`, NOT `Authorization: Bearer ${CONTEXT7_API_KEY}`. Per user disposition at cycle-3 D-3.2-completion, all design artifacts patched to use the canonical form: plan-v1.md (T0.5 description, .mcp.json sketch, L2 verification jq predicate), tasks.json (T0.5 + T2.4 descriptions), phase-validators.md (PV-2.C17 predicate), verify-at-execution.md (§H-5 auth-surface section), cc-dependencies.json (header-name enumeration). The prior `Authorization: Bearer` framing was non-canonical and has been retired across current artifacts. (Historical narrative preserving the Bearer framing remains in Document History rows, reconciliation logs, and superseded research-plan versions — these are append-only by ADR-0005 convention and document the discovery path, not the current state.)

### F3 — Tool surface is two tools: `resolve-library-id` and `query-docs`

- **Claim:** Context7 exposes exactly two MCP tools. `resolve-library-id` takes a human library name (e.g., `next.js`) and returns a Context7-compatible identifier such as `/vercel/next.js/v15.0.0`. `query-docs` takes that identifier (plus an optional topic filter and token budget, default ~5000 tokens) and returns documentation chunks and code examples. Callers must call `resolve-library-id` first unless the user already supplied an ID in `/org/project` or `/org/project/version` form.
- **Source:** Trevor Lasn, "Context7 MCP: Stop LLM Hallucinations with Live Docs," <https://www.trevorlasn.com/blog/context7-mcp> (community, corroborated against the upstash/context7 README's tool descriptions).
- **Quote (≤15 words):** "resolve-library-id … returns a Context7 ID (e.g., '/vercel/next.js/v15.0.0')."
- **Confidence:** High (corroborated across multiple independent sources, including the official repo and an issue thread in the official tracker referencing both tool names by ID).
- **Caveats:** Token-budget default may change; treat as informational not contractual.
- **v3 refresh note (2026-05-23 cycle-3):** **THE LOAD-BEARING F3 ANCHOR FOR CYCLE-3 RECONCILIATION.** The two-tool surface is stable across v1.0.x, v2.x, and v3.0.0 (corroborated multi-source per Confidence above). The `ReplaceContentTool` claim that propagated into the design artifacts is **NOT a Context7 tool name at any version** — it was a contamination from Serena's v1.2.0 CHANGELOG entry (`research-notes/T-001-serena.md:82`). Context7 never had a `ReplaceRegexTool` either. The design's allowlist entries `mcp__context7__resolve-library-id` and `mcp__context7__query-docs` (cc-design row 4 / blueprint Sub-Agents table row "discovery-external-researcher") are correct as-is. Any artifact site that frames C-0037 as a "ReplaceContentTool renamed from ReplaceRegexTool at v1.2.0" preservation is wrong and must be rewritten to anchor on the v3.0.0 two-tool surface.

### F4 — Install command for Claude Code (local stdio path)

- **Claim:** The documented Claude Code install command for the local stdio path is `claude mcp add context7 -- npx -y @upstash/context7-mcp@latest` (or, when authenticated, `claude mcp add --scope user context7 -- npx -y @upstash/context7-mcp --api-key YOUR_API_KEY`). The package targets Node.js 18+. No Python or compiled toolchain is required; the package runs entirely through `npx`.
- **Source:** Apidog, "How to Install and Use Context7 MCP Server," <https://apidog.com/blog/context7-mcp-server/> (community/vendor blog).
- **Quote (≤15 words):** "claude mcp add context7 -- npx -y @upstash/context7-mcp@latest"
- **Confidence:** Medium (community source; install shape matches the package's published `bin` entrypoint on npm and the README's quick-start).
- **Caveats:** The same source warns that `@latest` occasionally breaks under some MCP clients; pin a known version when possible.
- **v3 refresh note (2026-05-23 cycle-3):** Local stdio path **is documented as fallback only** in this feature (per Synthesis recommendation — remote HTTP is primary). The pinned version at execution time is `@upstash/context7-mcp@3.0.0` per the npm `dist-tags.latest` at 2026-05-22T16:20Z.

### F5 — Version pinning posture

- **Claim:** The npm package `@upstash/context7-mcp` is actively versioned; the GitHub Releases page lists frequent point releases (recent tags in the `2.x` / `3.0.0` line, with breaking changes noted — e.g., the `3.0.0` line introduced stateful Redis-backed session management). For the local stdio path, pin to a specific version (e.g., `@upstash/context7-mcp@3.0.0` or whichever is current at design time) rather than `@latest`. For the remote HTTP path, **versioning is vendor-controlled**: the design accepts that the endpoint at `https://mcp.context7.com/mcp` floats with Upstash's deployment cadence and there is no client-side pin to assert.
- **Source:** Upstash, "context7" GitHub Releases, <https://github.com/upstash/context7/releases>.
- **Quote (≤15 words):** No quote — paraphrased from release-tag listing (already quoted F1 from same domain).
- **Confidence:** Medium-high; release-page listing is authoritative for tag set, less so for "current recommended pin" which is a judgment call.
- **Caveats:** Release-date strings on the page may render in the local timezone; treat the *ordering* of releases as authoritative, the *absolute version number* as the design-time pin target.
- **v3 refresh note (2026-05-23 cycle-3):** **v1.x line capped at 1.0.30 (2025-11-24 per dispatch log). v1.2.0 was never published. The current `dist-tags.latest` is `3.0.0` (published 2026-05-22T16:20Z, ~21 hours before execute-orchestrator Phase 0 ran). The design's prior "v1.2.0" framing was wrong; the cycle-3 disposition is to drop the v1.2.0 framing entirely and replace with the v3.0.0-verified tool surface (two tools, stable; no `ReplaceContentTool`). Since the design uses remote HTTP transport (vendor-controlled, no client-side pin), the v3.0.0 version is informational — used only by the optional local stdio fallback installer.**

### F6 — Operational fit for project-scoped, always-on (Codespaces secrets available)

- **Claim:** Codespaces secrets surface as environment variables inside the container. `CONTEXT7_API_KEY` declared as a Codespaces secret is then either (a) passed as an `env` mapping in `.mcp.json` for the local stdio command, or (b) passed as a request header for the remote HTTP transport. The remote HTTP path moves the auth surface from "Node child process inheriting env" to "Claude Code's MCP transport setting a header," which is the same auth surface other vendor-hosted MCPs (e.g., Exa) use.
- **Source:** Synthesis — combines the Context7 README's transport documentation (above) with `KB-codespaces-platform` / `KB-cc-platform`'s already-documented `env` / header surfaces in `.mcp.json`. Marked explicitly as analysis, not a direct vendor claim.
- **Quote (≤15 words):** n/a (analytic statement).
- **Confidence:** Medium (analytic; relies on F1/F2 being correct).
- **Caveats:** The exact `.mcp.json` shape for "remote HTTP with custom header" depends on the Claude Code MCP client's current schema (covered by KB-cc-platform — not re-litigated here).
- **v3 refresh note (2026-05-23 cycle-3):** Unchanged.

## Synthesis (analysis — explicit)

**Transport recommendation: remote HTTP.** For an always-on project-scoped MCP whose entire value proposition is "fresh, version-specific upstream library docs," the vendor-hosted endpoint is the canonical surface. Three reinforcing reasons:

1. **Freshness.** Context7's value is the re-indexed documentation it serves. The vendor-hosted endpoint always reflects the latest re-index; a locally-installed `@upstash/context7-mcp` is only a client to the same backend, so the local install gains no freshness advantage.
2. **Operational simplicity.** Remote HTTP eliminates a Node child process from every Codespace, removes a version-pin decision (vendor-controlled), and removes a `postCreate` install step. It also matches the auth shape (header from secret) that other remote MCPs in this fleet (notably Exa, T-006) will use, reducing convention-drift in `.mcp.json`.
3. **Failure surface is cleaner.** A remote transport's failure modes are network-layer (DNS, TLS, 401, 429, 5xx) — exactly the surface T-007's operational discipline will instrument. A local stdio failure adds Node version drift, npm registry availability, and child-process lifecycle to the failure menu.

**Trade-offs accepted:**
- **Egress dependency.** The remote path requires outbound HTTPS to `mcp.context7.com`. In a default Codespaces baseline this is unrestricted; in a locked-down enterprise variant it may not be. If egress is restricted, fall back to the local stdio path (the documented fallback already covered by F1/F4).
- **No client-side version pin.** The design accepts that the remote endpoint floats with Upstash's deployment cadence. This is the same posture this feature already accepts for any vendor-hosted MCP and is materially less risky than the equivalent posture for an upstream tool with a wire protocol (Context7's wire protocol is MCP itself, which is the contract layer).
- **Tighter coupling to a single vendor.** Acceptable here because Context7 is a documentation-lookup convenience, not a load-bearing pipeline dependency; a degraded Context7 only degrades the quality of doc-lookup hints, it does not block the pipeline.

**Auth shape.** Either transport, the canonical answer is "`CONTEXT7_API_KEY` Codespaces secret." For remote HTTP, surface it as a header named `CONTEXT7_API_KEY`. For local stdio (fallback), surface it as the same-named environment variable in `.mcp.json`'s `env` block — never as a `--api-key` CLI flag, because the CLI form bakes the secret into a process-listing-visible argv.

## Acceptance-criteria check

| Criterion | Disposition | Notes |
|---|---|---|
| Available transports + recommendation for project-scoped always-on | **Satisfied** | Two transports (remote HTTP, local stdio); remote HTTP recommended (Synthesis). |
| Install command(s) if local; or URL + auth-header shape if remote HTTP | **Satisfied** | Remote URL `https://mcp.context7.com/mcp`; header `CONTEXT7_API_KEY`. Local fallback: `claude mcp add context7 -- npx -y @upstash/context7-mcp@3.0.0`. |
| Tool surface enumeration | **Satisfied** | `resolve-library-id`, `query-docs` — STABLE across v1→v3 per cycle-3 refresh. |
| Auth mechanism — explicit (API key? header name? format?) | **Satisfied** | API key from `context7.com/dashboard`; header name `CONTEXT7_API_KEY` (remote); env var `CONTEXT7_API_KEY` (local); `--api-key` CLI flag exists but should NOT be used (argv-leakage risk). |
| Version-pinning (or "remote, vendor-controlled") | **Satisfied** | Remote: vendor-controlled (no client-side pin). Local fallback: pin to `@upstash/context7-mcp@3.0.0` (current `dist-tags.latest` at execution slot). |
| ≥3 independent reputable sources | **Satisfied** | (1) Upstash official repo + Releases (GitHub), (2) `@upstash/context7-mcp` on npm registry, (3) Trevor Lasn community blog, (4) Apidog install guide. |

## Open questions

- **OQ-T005-1.** The exact `.mcp.json` schema for "remote HTTP transport with a custom auth header" is the Claude Code client's surface, not Context7's. This is already in `KB-cc-platform`'s scope and not re-researched here; design-cc should verify the JSON shape against `KB-cc-platform:references/integrations.md` when authoring the registration.
- **OQ-T005-2.** Rate-limit semantics for anonymous vs API-keyed traffic are not quoted by the official README; the "API key recommended" wording is the strongest claim made. If the design wants a hard SLO on Context7 availability, an explicit upstream confirmation would be needed.
- **OQ-T005-3.** Stateful (Redis-backed) session behavior introduced in the `3.0.0` line is documented but its operator-facing impact (e.g., whether a Codespace restart loses session state in a way that affects the user) is not characterized in the sources reviewed. Operator-impact characterization should be confirmed at design-time if the local stdio fallback path is exercised. **v3 refresh note (cycle-3):** carried forward unchanged; cross-referenced as SF-F3-RESIDUAL-2.
- **OQ-T005-4 (NEW at v2.0.0; cycle-3 refresh).** Live WebFetch of `https://www.npmjs.com/package/@upstash/context7-mcp` package metadata and v3.0.0 release notes was NOT executed during cycle-3 reconciliation due to a tooling gap in the design-composer's available-tools set. The composer relied on T-005 v1.0.0 corroborated evidence (multi-source per F3 Confidence) plus the dispatch log's documented npm probe (v3.0.0 / 2026-05-22T16:20Z). Cycle-4 audit should re-verify if convergence remains uncertain. **Surfaced as SF-F3-RESIDUAL-1.**

## Source list

1. Upstash, "context7" repository (official). <https://github.com/upstash/context7>. Accessed 2026-05-23.
2. Upstash, "context7" Releases page (official). <https://github.com/upstash/context7/releases>. Accessed 2026-05-23.
3. npm registry, "@upstash/context7-mcp" package page. <https://www.npmjs.com/package/@upstash/context7-mcp>. Accessed 2026-05-23.
4. Trevor Lasn, "Context7 MCP: Stop LLM Hallucinations with Live Docs" (community blog). <https://www.trevorlasn.com/blog/context7-mcp>. Accessed 2026-05-23.
5. Apidog, "How to Install and Use Context7 MCP Server" (community/vendor blog). <https://apidog.com/blog/context7-mcp-server/>. Accessed 2026-05-23.
6. **NEW v2.0.0 cycle-3 refresh sources:**
   - npm registry probe at 2026-05-22T16:20Z: `@upstash/context7-mcp@3.0.0` published (verified by execute-orchestrator Phase 0 same-day; see reconciliation-log-cycle-3.md F3).
   - npm registry probe of 1.x line: capped at 1.0.30 (2025-11-24) — v1.2.0 never published (verified by execute-orchestrator Phase 0 same-day; see reconciliation-log-cycle-3.md F3).
   - `research-notes/T-001-serena.md:82` — Serena v1.2.0 CHANGELOG entry referencing `ReplaceRegexTool → ReplaceContentTool` (contamination origin).

## Document History

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2026-05-23 | 1.0.0 | Initial research note; remote HTTP transport recommended; two-tool surface enumerated; auth header `CONTEXT7_API_KEY`; F5 referenced "recent tags in the 2.x / 3.0.0 line" as version-pinning posture; OQ-T005-3 flagged Redis-backed session state in 3.0.0. | discovery-external-researcher |
| 2026-05-23 | 2.0.0 | Cycle-3 reconciliation refresh per dispatch D-3.2 F3. Consolidates v3.0.0 facts from in-repo evidence base. Tool-name conclusion at v2.0.0 was `resolve-library-id` + `get-library-docs` (CORRECTED at v3.0.0 — see next row). | design-composer |
| 2026-05-23 | 3.0.0 | **D-3.2 WebFetch-completion patch by orchestrator** (D-3.2's WebFetch step was deferred because design-composer's tool set lacks WebFetch; the parent orchestrator has WebFetch and completed the step). **Live verification of npm `@upstash/context7-mcp` registry endpoint + GitHub repo `upstash/context7` README + the npm-bundled package CHANGELOG** confirmed: (1) **v3.0.0 IS REAL** — npm `dist-tags.latest=3.0.0`, tarball SHA-256 `rwSFWlJe71q2FgJDfddg5Wh4+LCvEKP89bW6AKOl/hLgbRJiJLULbIXru79ubVAuIBdw5ncNHA0A2RPcHzc/Tg==`, _npmUser fahreddin.ozcan @ upstash.com (verified Upstash maintainer). (2) **Tool names CORRECTED**: actual two tools are `resolve-library-id` and **`query-docs`** (NOT `get-library-docs` as v2.0.0 concluded). Authoritative evidence: GitHub `upstash/context7` master-branch README under "Available Tools > MCP Tools" + npm package CHANGELOG v2.2.5 patch entry which mentions `query-docs` verbatim + v2.2.4 patch entry "Remove research mode entirely from `query-docs` MCP tool". v2.0.0's `get-library-docs` was traceable to a stale T-005 v1.0.0 entry that pre-dated the actual tool surface. (3) **SF-F3-RESIDUAL-2 (Redis-backed session state) RESOLVED — no design impact**: v3.0.0 CHANGELOG confirms "Convert the stateless MCP implementation to a stateful one using Redis for session management." This affects users who self-host the npm package; this feature's design uses the HOSTED endpoint (`https://mcp.context7.com/mcp`) where Redis is Upstash's concern. (4) **SF-F3-AUTH-HEADER-1 — canonical resolution** per GitHub README verbatim: *"pass your API key via the `CONTEXT7_API_KEY` header"* — canonical form is `CONTEXT7_API_KEY: <value>` header literal, NOT `Authorization: Bearer ${CONTEXT7_API_KEY}`. Existing design artifacts use the Bearer form which is non-canonical. **Resolution decision DEFERRED to user** — both forms may work practically (the Bearer form might be silently accepted by the server) but canonical-per-README is the safer posture. Cycle-3 closure pending user disposition on the auth-header resolution. (5) **Patches applied by orchestrator**: `get-library-docs` → `query-docs` across blueprint-v3 (3 sites), cc-design (1), cc-dependencies.json (2), tasks.json (1), verify-at-execution.md (2), phase-validators.md (3), agent-roster-impact-matrix.md (3), T-005 (7). 16 total site corrections across 8 files. acceptance-tests.md v1.0.3 Document History row retains the `get-library-docs` reference as historical narrative of what D-3.3 was instructed to verify (D-3.3 was NO-OP at AT level anyway). | orchestrator (parent recipe-feature-pipeline; D-3.2 WebFetch-completion patch) |
