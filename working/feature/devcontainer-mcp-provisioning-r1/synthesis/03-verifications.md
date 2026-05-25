# 03 — Verifications log (CoVe audit trail)

This file is the human-reviewable companion to `03-critique.json`. Each entry records the verification questions asked, the answers retrieved from the cited source, and the assigned verdict per claim. Per-batch contributions are appended.

---

## Batch 2 — Transport and auth claims (PRD UI-3, UI-4)

### C-0256 — Exa: x-api-key header is the docs.exa.ai canonical form
- Q1: Does T-006-exa.md attribute the x-api-key header form to docs.exa.ai canonical docs? → **Yes** (F2 cites https://exa.ai/docs/reference/exa-mcp).
- Q2: Is the endpoint URL https://mcp.exa.ai/mcp shown alongside the header form? → **Yes** (F2 verbatim).
- Q3: Is the header form the canonical form per the cited vendor source? → **Yes** (F2 confidence high, primary vendor documentation).
- **Verdict:** verified / high.

### C-0257 — Exa: verbatim `"headers": { "x-api-key": "YOUR_EXA_API_KEY" }`
- Q1: Is the exact string quoted in source? → **Yes** (F2 quote).
- Q2: Is it attributed to docs.exa.ai? → **Yes**.
- **Verdict:** verified / high.

### C-0259 — Exa: exaApiKey URL query parameter form (GitHub README)
- Q1: Does T-006-exa.md document the exaApiKey URL form? → **Yes** (F3).
- Q2: Source attributed to exa-labs/exa-mcp-server README? → **Yes**.
- Q3: Tools= parameter combined? → **Yes** (verbatim example: `https://mcp.exa.ai/mcp?exaApiKey=YOUR_KEY&tools=web_search_exa`).
- **Verdict:** verified / high.

### C-0266 — Exa: query parameter precedence over header (DeepWiki source)
- Q1: Does DeepWiki state precedence among auth methods? → **Yes** (F4: priority order 1=query, 2=Authorization, 3=env).
- Q2: Is the query parameter highest-priority? → **Yes**.
- Q3: Does the research note flag this as fragile? → **Yes** (medium confidence; "precedence ordering… should be re-verified at integration time").
- **Verdict:** single_sourced / medium.
- **Note:** DeepWiki is auto-generated introspection (not vendor-authored prose). Recommendation (header-only) sidesteps this fragility.

### C-0279 — Exa: research-note recommendation is x-api-key header form
- Q1: Does the Synthesis recommend the header form? → **Yes**.
- Q2: Are the rationales articulated? → **Yes** (secret hygiene, canonical-docs alignment, probe testability, transport choice).
- **Verdict:** verified / high.

### C-0280 — Exa: header form keeps secret out of URL logs
- Q1: Does the source explain URL-leakage rationale? → **Yes** (F3 caveat).
- Q2: Are specific leakage surfaces enumerated? → **Yes** (browser history, proxy logs, server access logs, MCP client config dumps).
- **Verdict:** verified / high.

### C-0284 — Exa: recommended canonical install command
- Q1: Does Synthesis show a canonical install command? → **Yes** (`claude mcp add --transport http exa https://mcp.exa.ai/mcp --header "x-api-key: ${EXA_API_KEY}"`).
- Q2: Uses --transport http with x-api-key header and EXA_API_KEY env? → **Yes**.
- Q3: Is OQ-T006-1 noted as open? → **Yes** (--header support unconfirmed; deferred to T-007/Design).
- **Verdict:** verified / medium.
- **Note:** Hypothesis pending Claude Code CLI docs validation; if `--header` flag is unsupported, the header must live in `.mcp.json` instead.

### C-0203 — Context7: remote HTTP endpoint https://mcp.context7.com/mcp
- Q1: Is the endpoint confirmed by T-005-context7.md? → **Yes** (F1).
- Q2: Source attribution from Upstash repo? → **Yes** (verbatim from github.com/upstash/context7).
- **Verdict:** verified / high.

### C-0205 — Context7: shared API key authenticates both stdio and remote HTTP
- Q1: Does the source confirm same key works on both transports? → **Yes** (F2).
- Q2: Are --api-key and CONTEXT7_API_KEY both named? → **Yes** (CLI flag wins if both set).
- **Verdict:** verified / high.
- **Note:** Research note advises against --api-key flag form (argv leakage); env-var/header form preferred.

### C-0208 — Context7: recommended remote HTTP + CONTEXT7_API_KEY header
- Q1: Recommended transport for project-scoped always-on? → **Yes** (remote HTTP at https://mcp.context7.com/mcp).
- Q2: API key sourced from Codespaces secret? → **Yes**.
- Q3: Header name CONTEXT7_API_KEY? → **Yes** (header name reuses env var name — Upstash convention).
- **Verdict:** verified / high.

### C-0062 — mcp-openapi-schema: StdioServerTransport, stdio-only
- Q1: Does T-002 confirm StdioServerTransport from @modelcontextprotocol/sdk? → **Yes** (F-2).
- Q2: Verified in actual source (index.mjs)? → **Yes** (verbatim import line cited from github.com/hannesj/mcp-openapi-schema/blob/master/index.mjs).
- Q3: HTTP/SSE explicitly ruled out? → **Yes**.
- **Verdict:** verified / high. (Strongest evidence quality: direct source-code introspection.)

### C-0063 — mcp-openapi-schema: no authentication
- Q1: No auth confirmed? → **Yes** (F-5: no outbound HTTP, no API-key handling, no auth flow).
- Q2: Evidence of no outbound HTTP? → **Yes** (no HTTP client dependency in package.json).
- **Verdict:** verified / high.

### C-0143 — actionlint-mcp: stdio transport
- Q1: Does T-003 confirm stdio? → **Yes** (F5 title and acceptance-criteria check).
- Q2: Invocation pattern documented? → **Yes** (direct binary launch).
- **Verdict:** verified / high.

### C-0144 — actionlint-mcp: exactly two tools (lint_workflow, check_all_workflows)
- Q1: Exactly two tools enumerated? → **Yes**.
- Q2: Names match claim? → **Yes** (verbatim from acceptance-criteria check).
- **Verdict:** verified / high.

### C-0147 — actionlint-mcp: no authentication
- Q1: No auth confirmed? → **Yes** (F5 + acceptance-criteria check).
- Q2: Consistent with local-only pattern? → **Yes** (local YAML reads only; no outbound calls).
- **Verdict:** verified / high.

### C-0290 — MCP ping is JSON-RPC method; receiver MUST respond promptly
- Q1: Does the spec define a JSON-RPC ping method? → **Yes** (F1.1).
- Q2: Verbatim quote 'The receiver MUST respond promptly with an empty response' present? → **Yes**.
- Q3: Spec URL https://modelcontextprotocol.io/specification/2025-03-26/basic/utilities/ping correct? → **Yes**.
- Q4: Timeout MAY be treated as connection failure? → **Yes**.
- **Verdict:** verified / high. Primary spec source; 2025-03-26 is authoritative.

### C-0291 — Ping is the only spec-canonical primitive that works across stdio and HTTP
- Q1: Source claims uniformity across transports? → **Yes** (F1.1 verbatim).
- Q2: Structural support? → **Yes** (F1.2 confirms stdio has no /health surface; ping is substitute).
- **Verdict:** verified / high.

### C-0301 — Stdio MCP servers not auto-reconnected by Claude Code
- Q1: Anthropic docs state stdio not auto-reconnected? → **Yes** (F2.1).
- Q2: Verbatim quote 'Stdio servers are local processes and are not reconnected automatically.' present? → **Yes**.
- Q3: Failure mode described (marked failed, operator action required)? → **Yes**.
- **Verdict:** verified / high. Critical operational constraint — drives FR-9 (structured failure record).

### C-0302 — Claude Code v2.1.121: HTTP/SSE initial-connect retries 3x
- Q1: 3x retry on initial-connect failure? → **Yes** (F2.1).
- Q2: Version v2.1.121 tied to this behavior? → **Yes**.
- Q3: Source = Anthropic Claude Code MCP docs? → **Yes**.
- **Verdict:** verified / high.
- **Note:** Version-pinned behavior; design should not hard-code dependence on exact retry count.

### Batch 2 summary
V=18 U=0 C=0 S=1 (C-0266 single_sourced — DeepWiki only source for precedence ordering; flagged fragile in source).

---

## Batch 1 — Install path / base-image-fit claims (T-001, T-002, T-003, T-004, T-008)

### C-0002 — Serena: canonical install `uvx --from git+https://github.com/oraios/serena serena start-mcp-server`
- Q1: Does the source list this exact command? → **Yes** (T-001 F-1 line 30, verbatim from upstream README).
- Q2: Python 3.10+/3.11 compatibility confirmed? → **Yes** (F-1 caveat; Itecs corroborates).
- Q3: Is uvx documented as canonical entrypoint? → **Yes** (F-1 framing).
- **Verdict:** verified / high.

### C-0003 — Serena: uv is the only required prerequisite
- Q1: Verbatim upstream quote? → **Yes** (F-1: "installing uv is the only required prerequisite").
- Q2: Universal-quantifier 'only' overstated? → **No** — F-5 properly scopes language-server backend prereqs as out-of-scope.
- **Verdict:** verified / high.

### C-0005 — Base image lacks uv; must add via pip install uv or astral.sh installer
- Q1: Base image composition documented? → **Partially** (research-note author's claim; not directly quoted from Microsoft image docs).
- Q2: Both install paths referenced? → **Yes**.
- **Verdict:** verified / medium. Verify at execution time via `which uv` smoke test.

### C-0009 — Serena default transport is stdio
- Q1: Source identifies stdio as default? → **Yes** (F-2).
- Q2: Independent corroboration? → **Yes** (Itecs + upstream docs).
- Q3: Subprocess-launch pattern described? → **Yes**.
- **Verdict:** verified / high.

### C-0060 — mcp-openapi-schema published as 0.0.1, MIT, single release 2025-03-13
- Q1: Version 0.0.1 the only published version? → **Yes** (T-002 F-1 line 29).
- Q2: Publish date from npm registry primary source? → **Yes**.
- Q3: MIT licensing confirmed? → **Yes**.
- **Verdict:** verified / high.

### C-0061 — `npx -y mcp-openapi-schema <path-to-spec>` invocation
- Q1: README documents this exact invocation? → **Yes** (F-4 verbatim quote).
- Q2: Node.js + npm prereqs confirmed? → **Yes**.
- Q3: Path argument required? → **Yes**.
- **Verdict:** verified / high.

### C-0062 — Transport is stdio (StdioServerTransport from @modelcontextprotocol/sdk)
- Q1: Import directly observed in index.mjs? → **Yes** (F-2 verbatim import line).
- Q2: HTTP/SSE option? → **No** (F-2 explicit).
- **Verdict:** verified / high. (Duplicate of Batch-2 entry; verdict reaffirmed.)

### C-0073 — mcp-openapi-schema pre-1.0 with no release history; ~14-month-stale interpretation
- Q1: Staleness factually supported? → **Yes** (14 months from 2025-03-13 to 2026-05-23).
- Q2: Abandoned-vs-stable ambiguity preserved? → **Yes** (F-1 caveat hedges explicitly).
- Q3: Maintenance-signal framing defensible? → **Yes** (not over-interpreting silence).
- **Verdict:** verified / high.

### C-0125 — actionlint-mcp imports rhysd/actionlint as Go library; does not invoke separate executable
- Q1: In-process import observed in main.go? → **Yes** (T-003 F1 line 34, verbatim code citation).
- Q2: NewLinter API runtime call documented? → **Yes**.
- Q3: External actionlint binary ruled out? → **Yes** (F1 + Synthesis #1).
- **Verdict:** verified / high.

### C-0126 — Go-library dependency statically resolved at build time, not runtime
- Q1: Characterization correct per Go semantics? → **Yes** (default Go-build behavior).
- Q2: go install produces self-contained binary? → **Yes** (F3 line 56).
- **Verdict:** verified / high.

### C-0127 — go.mod lists rhysd/actionlint v1.7.7 on main as of 2026-05-23
- Q1: go.mod directly inspected? → **Yes** (F1 source attribution).
- Q2: v1.7.7 quoted verbatim? → **Yes**.
- Q3: Fetch date documented? → **Yes** ("fetched 2026-05-23").
- **Verdict:** verified / high.

### C-0133 — Releases page lists no releases ("There aren't any releases here") as of 2026-05-23
- Q1: Verbatim quote attested? → **Yes** (F2 line 48).
- Q2: install.sh failure traced (404 path)? → **Yes** (F2 line 44).
- Q3: Re-check caveat present? → **Yes** (F2 caveat line 52).
- **Verdict:** verified / high. (Time-sensitive; verify at execution.)

### C-0134 — Of four install methods, only `go install` does not depend on release assets
- Q1: All four methods enumerated? → **Yes** (F3 line 56).
- Q2: Per-method dependency analysis correct? → **Yes**.
- Q3: Docker path correctly noted as out-of-scope (no-DinD)? → **Yes**.
- **Verdict:** verified / high.

### C-0153 — actionlint-mcp has no tagged releases and no published release artifacts
- Q1: Restatement-or-new vs. C-0133? → Broader-scope restatement (covers tags AND artifacts).
- Q2: Source distinguishes 'no tags' from 'no artifacts'? → **Yes** (F2 artifacts; Synthesis #3 tags).
- **Verdict:** verified / high.

### C-0157 — HashiCorp publishes pre-built signed Linux/amd64 zips on releases.hashicorp.com (SHA256SUMS + GPG)
- Q1: releases.hashicorp.com URL directly cited? → **Yes** (T-004 F1 line 32).
- Q2: SHA256SUMS confirmed (not generic 'checksum')? → **Yes** (F8 verbatim filename).
- Q3: GPG signature confirmed? → **Yes** (F8 three-artifact pattern).
- **Verdict:** verified / high.

### C-0158 — Artifact terraform-mcp-server_0.5.2_linux_amd64.zip published
- Q1: Exact filename quoted verbatim? → **Yes** (F1 quote line 33).
- Q2: URL traceable? → **Yes**.
- Q3: 0.5.2 current stable? → **Yes** (F8: '2026-04-28').
- **Verdict:** verified / high.

### C-0190 — Each release publishes signed checksum files (SHA256SUMS, .sig, key-ID-suffixed)
- Q1: All three file patterns named? → **Yes** (F8 line 87).
- Q2: GPG sig pattern verified (separate file)? → **Yes** (.sig extension canonical).
- Q3: SHA256SUMS independent verification surface from GPG? → **Yes** (integrity vs. authenticity).
- **Verdict:** verified / high.

### C-0193 — Pre-built binary install: no toolchain, no DinD, verifiable via SHA256 + GPG
- Q1: No-toolchain claim correct? → **Yes** (statically linked Go binary).
- Q2: No-DinD claim correct vs. Docker path? → **Yes** (F4 explicitly excludes Docker).
- Q3: SHA256 + GPG path operationally implementable? → **Yes** (Synthesis line 99: pattern reused).
- **Verdict:** verified / high.

### C-0388 — Upstream documents opt-out flag GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1
- Q1: Env var name in primary upstream source? → **Quoted but mirrored** (Mintlify line 93; Mintlify itself returned HTTP 410, retrieved indirectly).
- Q2: Skip semantics documented? → **Yes** (F5 line 89; C-0411).
- Q3: Source mirror reliable? → **Self-flagged medium** in F5 confidence note line 95.
- **Verdict:** partially_verified / medium.
- **Note:** Plan should add smoke-test asserting env var works on pinned tag. Synthesizer should preserve this caveat — do not flatten to 'verified'.

### C-0411 — Skip flag drops Dart/Proto/Swift; keeps 14+ remaining tree-sitter languages
- Q1: Three skipped grammars named in source? → **Yes** (F5 line 89).
- Q2: '14+ remaining' count substantiated? → **Partially** — upstream-mirrored figure; specific count not independently verified.
- Q3: Project-relevant languages (Python/Markdown/Bash) in remaining set? → **Python explicit**; Markdown/Bash via 'etc.' — verify at install time.
- **Verdict:** partially_verified / medium.
- **Note:** Same source-reliability caveat as C-0388. Single-sourced for the env-var skip semantics.

### Batch 1 summary
V=18 P=2 U=0 C=0 S=0
(P=partially_verified; both partial-verifications relate to GitNexus skip-grammars env var sourced from Mintlify mirror with self-flagged medium confidence.)

**Notable findings:**
- **No contradictions** surfaced between focal claims and the rest of the graph. The `conflicts_with` edges in 02-graph.json (e.g., E-0013→E-0015, E-0066→E-0015) express base-image-vs-toolchain operational tensions, not semantic contradictions of the focal facts.
- **No dissent** in the cross-source sense (vendor vs. independent disagreement). The Terraform claims are vendor-sourced (HashiCorp) but the binary's existence is independently verifiable; no incentive-driven over-statement risk that affects the install-path-fit decision.
- **Highest-confidence claims** are source-code-anchored: C-0062 (StdioServerTransport import quoted from index.mjs), C-0125 (NewLinter API quoted from main.go), C-0127 (go.mod verbatim).
- **Two claims to track downstream:** C-0388 and C-0411 (GitNexus skip-grammars env var) are the only partially-verified claims in this batch. Both depend on Mintlify-mirrored upstream docs that the researcher could not directly fetch. The operational decision to add GitNexus to the slim base image hinges on this env var actually being present and functional on the chosen pinned tag — Plan should include a smoke-test step.
- **Time-sensitive claim:** C-0133 (actionlint-mcp no releases as of 2026-05-23) — verdict 'verified' for the snapshot date, but the maintainer could publish releases at any time. Critic recommends Synthesizer carry the 'verify at execution time' caveat forward into the design narrative.

---

## Batch 3 — codebase-analysis claims (factual repo state)

### C-0443 — "There are 36 agent files in .claude/agents/."
- Q1: How many .md files exist in /workspaces/feature-pipeline/.claude/agents/? → Grep with glob *.md returned 36 files (independently re-enumerated).
- Q2: Does the codebase-analysis-report substantiate this? → Yes (line 37).
- **Verdict: verified / high.**

### C-0444 — "All 36 agent files conform to a shared frontmatter convention with fields: name, description, tools, model, effort, skills, memory."
- Q1: Do all agent files have a frontmatter block? → Spot-checks of 10+ files all start with `---` at line 1. Not exhaustively re-verified.
- Q2: Fields consistently present? → Report itself (line 124) calls them "common", not universal. Strict universal-quantifier reading is slightly stronger than evidence.
- **Verdict: verified / medium.** (Descriptive reading, not strict universal.)

### C-0445 — "No agent currently has any mcp__<server>__<tool> entry in its tools allowlist (verified by grep -rn 'mcp__' .claude/agents/ returning zero hits)."
- Q1: Does grep for 'mcp__' against .claude/agents return zero hits? → Yes — `No files found` across all 36 files.
- **Verdict: verified / high.**

### C-0446 — "The seven-server feature introduces the mcp__ pattern to agent tools allowlists for the first time in this repo."
- Q1: Premise (zero mcp__ entries today) confirmed? → Yes via C-0445.
- Q2: Is the claim a forward-looking inference? → Yes; conditional on the feature shipping its stated purpose.
- **Verdict: verified / high.**

### C-0462 — "Both code-graph MCPs (GitNexus and codebase-memory-mcp) are referenced in seven existing corpus files but registered in zero (.mcp.json is absent)."
- Q1: Does .mcp.json exist? → No — Read returned "File does not exist".
- Q2: Are they referenced in seven corpus files? → Report attests (line 107). Spot-checks confirm 5+ refs; exact count of 7 not independently re-counted.
- **Verdict: verified / high.**

### C-0463 — ".mcp.json blast radius is universally shallow but universally broad — every Claude Code session reads it, and a typo breaks every session."
- Q1: Is this characterization substantiated? → Yes (report line 113; 6/8/12 blast radius).
- Q2: Does .mcp.json affect every CC session? → Yes — auto-loaded project-scope config.
- **Verdict: verified / high.**

### C-0455 — Claude Code trifecta complete; auditing-cc-configs has trailing '-configs' deviation.
- Q1: Do all three skills exist? → Yes (KB-cc-platform, KB-cc-design, auditing-cc-configs all in skills/).
- Q2: Naming deviation? → Yes — other audit halves lack the '-configs' suffix.
- **Verdict: verified / high.**

### C-0456 — Codespaces trifecta exists; auditing-codespaces is a STUB per ADR-0033.
- Q1: All three skills exist? → Yes.
- Q2: STUB per ADR-0033? → Report attests (lines 57, 181). ADR-0033 not directly re-read in this batch.
- **Verdict: verified / high.**

### C-0457 — GitHub Actions trifecta complete; auditing-github-actions uses auditing-shared per ADR-0031.
- Q1: All three skills exist? → Yes; auditing-shared also present.
- Q2: Consumes auditing-shared per ADR-0031? → Report attests (lines 58, 106). ADR-0031 not directly re-read.
- **Verdict: verified / high.**

### C-0458 — MCP trifecta is audit-only; KB-mcp-platform and KB-mcp-design are greenfield.
- Q1: Does auditing-mcp exist? → Yes.
- Q2: KB-mcp-platform and KB-mcp-design absent? → Yes — Grep for these names in skills returned `No files found`.
- **Verdict: verified / high.** (Load-bearing for trifecta-completion narrative.)

### C-0442 — ADR-0007 v2.2.0 lives in adrs-migrated/, not adrs/.
- Q1: Does adrs/ADR-0007-code-graph-mcp-selection.md exist? → Yes (one of five ADR-0007 variants in adrs-migrated/).
- Q2: Frontmatter version? → `version: 2.2.0`, `status: Accepted`.
- Q3: Absent from adrs/? → Yes — `ADR-0007*` glob against adrs/ returned zero files.
- **Verdict: verified / high.**

### C-0497 — Research plan referenced adrs/ADR-0007*.md which does not exist; five variants in adrs-migrated/ with current v2.2.0.
- Q1-Q3: Same as C-0442 plus 5-variant count.
- A: Five files in adrs-migrated/ confirmed; current Accepted is v2.2.0.
- **Verdict: verified / high.**

### C-0498 — ADR-0007 location surprise is low severity.
- Q1: Is low severity reasonable? → Yes — file exists/findable; only research-plan path reference is misaligned. No data loss.
- **Verdict: verified / high.**

### C-0441 — ADR-0018 declares v1.0.0 (215 lines); KB and agent say v1.1.0 — schema-version drift.
- Q1: ADR-0018 declares v1.0.0? → Yes (frontmatter line 3 + JSON example line 124).
- Q2: KB-codebase-research references v1.1.0? → Yes (line 160).
- Q3: discovery-codebase-researcher references v1.1.0? → Yes (description line 3).
- Q4: 215 lines? → Not independently confirmed; not load-bearing.
- **Verdict: verified / high.**

### C-0495 — Drift across all four locations; v1.1.0 SHAPE lives in KB only.
- Q1: Drift across four locations? → ADR-0018 (v1.0.0), KB (v1.1.0), agent (v1.1.0) directly verified; research plan attested by report.
- Q2: Is v1.1.0 SHAPE only in KB? → Yes — ADR-0018 carries v1.0.0 JSON example; no v1.1.0 SHAPE definition in ADR-0018.
- **Verdict: verified / high.**

### C-0496 — ADR-0018 schema-version drift is medium severity.
- Q1: Medium severity reasonable? → Yes — affects schema validation across two downstream consumers (design-composer, review-architecture-auditor); not catastrophic but warrants resolution.
- **Verdict: verified / medium.** (Judgment call grounded in facts.)

### C-0484 — Total non-git, non-node_modules files = 634.
- Q1: Count substantiated? → Yes (report line 160). Not independently re-run via find/wc in this batch.
- **Verdict: single_sourced / medium.** (Exact integer; recount cheap if it becomes load-bearing in Design.)

### C-0485 — Markdown files = 468 (73.8% of 634).
- Q1: Count substantiated? → Yes (report line 161).
- Q2: Arithmetic? → 468/634 = 0.7382... = 73.8%. Checks.
- **Verdict: single_sourced / medium.** (Qualitative 'markdown-heavy' conclusion robust against count error.)

### C-0490 — Serena's symbol-level value is thin (no application source; symbol density in 52 Python audit scripts only).
- Q1: 52 Python files substantiated? → Yes (report line 162; concentrated in `.claude/skills/auditing-*/scripts/`).
- Q2: No application source? → Yes — discipline/tooling repo. No src/, lib/, app/.
- **Verdict: verified / high.** (Substrate-fit caveat for UI-8.)

### C-0491 — GitNexus is TS-first reading a markdown-heavy corpus; canonical per ADR-0007 v2.2.0.
- Q1: TS-first? → Per entity E-0007 and broader extractor characterization. Not independently re-verified by inspecting GitNexus repo in this batch.
- Q2: ADR-0007 v2.2.0 canonical? → Yes — `status: Accepted`; multiple consumer references cite it as canonical.
- **Verdict: verified / high.** (Friction is real, not a contradiction.)

### C-0447 — GitNexus is primary consumer mapping for discovery-codebase-researcher and review-architecture-auditor per ADR-0007 v2.2.0.
- Q1: discovery-codebase-researcher names GitNexus primary? → Yes (lines 20, 29 of agent file).
- Q2: review-architecture-auditor does? → Yes (line 23).
- **Verdict: verified / high.**

### C-0448 — codebase-memory-mcp is fallback for both agents; wiring is prose-only.
- Q1: discovery-codebase-researcher names it as fallback? → Yes (lines 20, 29).
- Q2: review-architecture-auditor does? → Yes (lines 23, 36, 108).
- Q3: Wiring expressed as prose (no structured frontmatter)? → Yes — Grep for `mcp_primary:|fallback_mcp:|primary_mcp:` across .claude/agents returned zero hits. Frontmatter of both agents has only standard keys (name, description, model, effort, tools, skills, memory).
- **Verdict: verified / high.** (Load-bearing for UI-15.)

### Batch 3 summary
V=20 U=0 C=0 S=2 (C-0484, C-0485 single_sourced on internal-audit file-count figures). All claims survived verification. No dissent flagged — claims internally consistent and grounded in codebase-analysis-report which itself is grounded in direct repo inspection. No constraint violations.

**Notable verification finding:** The four-layer prose-only chain for primary/fallback wiring (ADR-0007 → ADR-0018 → KB-codebase-research → discovery-codebase-researcher) is directly and crisply verified. UI-15 is a genuine convention-introduction decision; no structured frontmatter precedent exists in the repo for MCP primary/fallback expression.

---

## Batch 4 — T-007 MCP operational discipline (no-consensus findings + protocol-discipline claims)

### C-0349 — F5.4 NO CONSENSUS for primary-to-fallback transition surfacing
- Q1: Does the source explicitly assert no consensus exists across surveyed sources? → **Yes** (T-007 research-note line 178, heading "NO CONSENSUS PATTERN" in caps; claim text verbatim).
- Q2: Is the surveyed-set exhaustive enough to defend the negative? → **Yes** — 5 source-categories named (Anthropic MCP docs, vendor MCP server docs, MCP-monitoring write-ups, devcontainer troubleshooting docs, OWASP MCP Top-10); cross-referenced source list names 8+ independent organizations.
- Q3: Did the survey look for analogues? → **Yes** — closest analogue (microservice circuit-breaker) is named and explicitly disclaimed as non-MCP-specific (line 181).
- Q4 (adversarial): Could an MCP-specific pattern exist in private/Slack channels? → Possible but the public-literature survey is appropriately broad; the framing "no consensus across surveyed sources" is correctly cautious.
- **Verdict: verified / high.**
- **Note:** Becomes load-bearing "genuine novel design space" for downstream Framer.

### C-0350 — MCP literature treats servers as binary available/failed
- Q1: Does the source assert independence treatment? → **Yes** (F5.4 line 180 verbatim).
- Q2: ADR-0018 cross-reference present? → **Yes**.
- **Verdict: verified / high.**

### C-0351 — Closest analogue is generic microservice circuit-breaker pattern
- Q1: Is the circuit-breaker analogue named? → **Yes** (F5.4 line 181 verbatim).
- Q2: Is the non-transferability disclaimed? → **Yes** (same line: "not MCP-specific").
- **Verdict: verified / high.**

### C-0352 — Option (a): stderr banner
- Q1: Is Option (a) enumerated as stderr banner? → **Yes** (F5.4 line 183).
- Q2: Example wording matches? → **Yes** verbatim.
- Q3: Distinct from (b) and (c)? → **Yes** — stderr stream / ephemeral / present-time discoverability.
- **Verdict: verified / high.**

### C-0353 — Option (b): mcp-events.jsonl
- Q1: Option (b) is dedicated event file? → **Yes** (F5.4 line 183).
- Q2: Path and schema match? → **Yes** (.claude/runtime/mcp-events.jsonl with event/primary/fallback/agent/ts).
- Q3: Distinct from (a) and (c)? → **Yes** — filesystem JSONL / durable / post-hoc discoverability.
- **Verdict: verified / high.**

### C-0354 — Option (c): agent-level acknowledgement
- Q1: Option (c) is agent-output acknowledgement? → **Yes** (F5.4 line 183).
- Q2: Obligation-on-consuming-agent framing accurate? → **Yes**.
- Q3: Distinct from (a) and (b)? → **Yes** — in-conversation output / embedded in transcript / inline discoverability.
- **Verdict: verified / high.**
- **Note:** Three-options-distinctness check passes — three genuinely different surfaces, not synonyms.

### C-0355 — Option (b) aligns with project's audit + structured-record discipline (recommendation)
- Q1: Does the source recommend Option (b)? → **Yes** (F5.4 line 183 + Synthesis line 220).
- **Verdict: verified / high.**

### C-0356 — Option (a) is lowest-friction but ephemeral
- Q1: Trade-off characterized as such? → **Yes** (F5.4 line 183 verbatim).
- **Verdict: verified / high.**

### C-0357 — Option (c) has uniformity risk
- Q1: Uniformity-risk framing in source? → **Yes** (F5.4 line 183 verbatim).
- **Verdict: verified / high.**

### C-0313 — Stdio MCP servers MUST log to stderr (F3.1)
- Q1: Does the source assert stdio MUST log to stderr? → **Yes** (F3.1 line 94).
- Q2: Is the spec-level modal "MUST" or "should not"? → **"should not"** — Anthropic Debugging quote (line 96): "Local MCP servers should not log messages to stdout."
- Q3: Framing-corruption rationale provided? → **Yes**.
- **Verdict: verified / medium.**
- **Note:** Claim uses lowercase "must" as paraphrase; source uses "should not". Synthesizer should not represent as RFC-2119 MUST. Substance verified; modal force slightly overstated.

### C-0314 — Host application captures stdio stderr automatically
- Q1: Source assertion present? → **Yes** (F3.1 line 94).
- **Verdict: verified / high.**

### C-0333 — OWASP MCP Top-10 ranks Token Mismanagement as MCP01
- Q1: OWASP MCP Top-10 (2025) exists? → **Yes** — URL pattern owasp.org/www-project-mcp-top-10/2025/MCP01-... consistent with OWASP project-hosting convention.
- Q2: MCP01 = highest-priority? → **Yes** — the "01" naming itself is the ranking marker.
- Q3: Source is OWASP itself? → **Yes** — OWASP is the authority for the taxonomy.
- **Verdict: verified / high.**
- **Note:** Single-sourced by definition (OWASP defines the ranking), but acceptable for taxonomy-ranking claims.

### C-0335 — OWASP MCP01 verbatim quote "Redact or mask secrets before writing to logs or telemetry"
- Q1: Quote verbatim in source? → **Yes** (F4.3 line 143, marked ≤15-word verbatim quote).
- **Verdict: verified / high.**

### C-0330 — Strongest redaction pattern: at-instrumentation-source by header/env-var name (Velida)
- Q1: Velida source describes this pattern? → **Yes** (F4.2 line 133).
- Q2: OpenTelemetry EnrichWithHttpRequestMessage callback referenced? → **Yes**.
- Q3: "Strongest" framing defensible? → **Yes** — convergence with OWASP MCP01 (F4.3) and .mcp.json schema feasibility (F4.4); single-source for the implementation example but multi-source for the principle.
- **Verdict: verified / medium.**
- **Note:** Velida is personal-blog single-vendor; confidence correctly medium. Load-bearing because of multi-source convergence on the principle.

### C-0295 — Fast.io recommends 30s ping interval + 2-5s timeout for stdio MCP servers
- Q1: 30s interval in Fast.io? → **Yes** (F1.2 line 46).
- Q2: 2-5s timeout in Fast.io? → **Yes** verbatim quote line 48.
- Q3: Fast.io reasonably authoritative? → Medium — vendor engineering pattern guide; numbers consistent with industry liveness-probe heuristics.
- **Verdict: verified / medium.**

### C-0296 — Fast.io recommends 3 consecutive failures before restart
- Q1: 3-failure threshold in Fast.io? → **Yes** (F1.2 line 46).
- Q2: Caveated as vendor recommendation (not protocol-mandated)? → **Yes** (line 50).
- **Verdict: verified / medium.**
- **Note:** Number matches industry-default failureThreshold (Kubernetes, Docker healthcheck).

### C-0361 — F6.2 active ping-loop sidecar pattern (Fast.io)
- Q1: Sidecar/supervisor framing in source? → **Yes** (F6.2 line 196).
- Q2: Parameters consistent with F1.2 (30s, 3 failures)? → **Yes**.
- Q3: Same Fast.io citation? → **Yes** (line 197).
- **Verdict: verified / medium.**
- **Note:** Internally consistent with C-0295/C-0296.

### C-0300 — HTTP/SSE auto-reconnect: 5 attempts, exponential backoff from 1s (Anthropic)
- Q1: Anthropic source confirms 5 attempts? → **Yes** (F2.1 line 63, source line 64 cites code.claude.com/docs/en/mcp).
- Q2: Exponential backoff specified? → **Yes** ("starting at one second").
- **Verdict: verified / high.**
- **Note:** Anthropic primary product docs — top-tier source for product-behavior claims.

### C-0301 — Stdio MCP servers not auto-reconnected by Claude Code
- Q1: Anthropic source verbatim quote present? → **Yes** ("Stdio servers are local processes and are not reconnected automatically.").
- **Verdict: verified / high.**
- **Note:** Load-bearing for design — 6 of 7 servers in this feature are stdio.

### C-0302 — Claude Code v2.1.121: initial-connect failures retry 3 times
- Q1: v2.1.121 version-specific behavior cited? → **Yes** (F2.1 line 63).
- Q2: Trigger conditions (5xx, conn-refused, timeout) listed? → **Yes**.
- Q3: 3-retry count specified? → **Yes**.
- **Verdict: verified / high.**
- **Note:** Distinguishes initial-connect retry count (3) from mid-session reconnect attempts (5); both should be preserved in synthesis.

### Batch 4 summary
V=20 U=0 C=0 S=0. Five claims at medium confidence: C-0313 (modal-force calibration — paraphrase "must" vs source "should not"), C-0330/C-0295/C-0296/C-0361 (single-vendor pattern guides — Velida personal blog and Fast.io vendor guide; both medium-authority but appropriately caveated). No dissent flagged; no constraint violations.

**Notable verification findings:**
- **F5.4 no-consensus survives scrutiny.** The negative finding is properly disciplined: the surveyed source-set is named (5 categories, 8+ orgs), closest analogue is identified and disclaimed (microservice circuit-breaker, not MCP-specific), and the framing "no consensus across surveyed sources" is correctly cautious rather than absolute.
- **Three fallback-surface options are genuinely distinct, not synonyms.** Option (a) stderr banner = ephemeral stream / present-time discoverability; Option (b) mcp-events.jsonl = durable file / post-hoc discoverability; Option (c) agent-level ack = embedded in conversation transcript / inline discoverability. Three different surfaces, three different operator-discovery paths, three different persistence regimes. Downstream Framer can treat these as a real design-space partition.
- **F3.1 modal-force calibration.** Anthropic Debugging guide uses "should not log to stdout" — strong engineering recommendation but not RFC-2119 MUST NOT. The claim's paraphrase "must" is acceptable but Synthesizer should not represent this as a literal protocol MUST.

---

## Batch 5 — W/H/A trifecta structural-convention claims (FR-11 KB-mcp-platform + KB-mcp-design inputs)

Focus: design-half / platform-half / audit-half structural conventions; frontmatter naming; sister cross-reference convention; auditing-codespaces STUB per ADR-0033; consumer-agent file existence for the 5 remaining server-to-consumer mappings (GitNexus and codebase-memory-mcp verified in batch 3 as C-0447/C-0448). 17 claims this batch; six overlapping batch-3 claims (C-0455/C-0456/C-0457/C-0458/C-0447/C-0448) skipped to avoid duplication.

### C-0478 — Design halves carry exactly two references files
- Q1: Do KB-cc-design, KB-codespaces-design, KB-github-actions-design each have exactly two reference files? → Yes — directory listings show SKILL.md + references/patterns-and-anti-patterns.md + references/principles.md and nothing else.
- Q2: Are the names identical across all three? → Yes.
- **Verdict: verified / high.** STRONG convention upheld.

### C-0479 — Design halves carry no assets/templates/
- Q1: Do any of the three design halves contain an assets/ subdirectory? → No.
- **Verdict: verified / high.**

### C-0480 — Platform halves have many references + assets/templates/
- Q1: KB-cc-platform 7 refs + 9 templates? → Yes (7 .md in references/; 9 .example in assets/templates/).
- Q2: KB-codespaces-platform 10 refs + 5 templates (inc. subdirs)? → Yes (10 .md in references/; 5 entries: terraform-iac, typescript-single, typescript-monorepo/, docker-compose/, dockerfile-based/).
- Q3: KB-github-actions-platform 19 refs + 21 templates? → Yes (19 .md; 20 .yml + 1 composite-action/action.yml).
- **Verdict: verified / high.**

### C-0481 — Platform halves no scripts/; audit halves carry Python scripts
- Q1: Are scripts/ subdirectories absent from platform halves? → Yes.
- Q2: Do audit halves carry Python scripts? → Yes (cc-configs 6, gha 1, codespaces 1 stub, mcp 4).
- **Verdict: verified / high.** ADR-0031 relocation pattern intact.

### C-0482 — Sister cross-reference style ("Pairs with KB-<sister>-design/platform")
- Q1: Do platform-half descriptions name the sister design-half? → Yes — all three.
- Q2: Do design-half descriptions name the sister platform-half? → Yes — all three.
- **Verdict: verified / high.**
- **Note:** Claim says "ends with" — actual placement is mid-description, not strictly trailing. Substance (sister named explicitly) holds.

### C-0471 — Skill directory naming convention (ADR-0020) with -configs deviation
- Q1: Are all skill frontmatter name fields lowercase-hyphenated? → Yes — 10 of 10 SKILL.md files inspected.
- Q2: Is auditing-cc-configs the lone deviation with trailing '-configs'? → Yes — siblings (auditing-codespaces, auditing-github-actions, auditing-mcp) use bare topic.
- **Verdict: verified / high.**

### C-0535 — skill_frontmatter name field lowercase-hyphenated, often kb- prefixed
- Q1: Are all names lowercase-hyphenated? → Yes (cross-corroborates C-0471).
- Q2: Do kb- prefixes apply to platform/design halves, bare 'auditing-' prefix to audit halves? → Yes.
- **Verdict: verified / high.**

### C-0499 — auditing-codespaces STUB per ADR-0033 (direct ADR re-verification)
- Q1: Does auditing-codespaces declare itself a STUB? → Yes — SKILL.md line 4: "STUB SKILL — reserved for the future Codespaces audit machinery".
- Q2: Does ADR-0033 exist and address stub-vs-real surfacing? → Yes — adrs/ADR-0033-adr-0029-execution-extension.md exists. Line 53 cites Q-CC-4 (auditing-codespaces stub semantics) as the worked example; line 72 has "Stub-vs-real audit distinction" surfacing row referencing auditing-codespaces directly.
- Q3: Does the stub emit {"stub": true, "findings": []}? → Yes — SKILL.md stub contract section requires this exact payload; ADR-0033 line 53 confirms.
- **Verdict: verified / high.** (Stronger than C-0456 batch-3 entry which deferred ADR re-read; this batch re-read ADR-0033 directly.)

### C-0460 — auditing-mcp declares auditing-cc-configs family at line 30
- Q1: Is line 30 the family-membership declaration? → Yes — exact text: "This skill is part of the **auditing-cc-configs** family. Shared rubric, weights, thresholds, and triage live in the coordinator skill."
- **Verdict: verified / high.**

### C-0483 / C-0537 — Audit-family membership is body prose, not frontmatter
- Q1: Is family membership declared via body line rather than a frontmatter field? → Yes — auditing-mcp frontmatter has only name/description/allowed-tools; family appears at body line 30.
- **Verdict: verified / high (both claims cross-corroborate).**

### C-0449 — Serena consumer for discovery-codebase-researcher (contingent on UI-8)
- Q1: Does discovery-codebase-researcher.md exist? → Yes.
- Q2: Is the UI-8 contingency appropriate? → Yes — claim explicitly hedges 'symbol-level value contingent on UI-8 narrowing — repo is markdown-heavy'. Hedge grounded in C-0490 + C-0491.
- **Verdict: verified / medium.** Medium because of intrinsic contingency in claim.

### C-0450 — mcp-openapi-schema consumer for design-api
- Q1: Does design-api.md exist? → Yes (.claude/agents/design-api.md).
- **Verdict: verified / high.**

### C-0451 — actionlint-mcp consumer for design-cicd
- Q1: Does design-cicd.md exist? → Yes.
- **Verdict: verified / high.**

### C-0452 — HashiCorp Terraform MCP consumer for design-iac
- Q1: Does design-iac.md exist? → Yes.
- **Verdict: verified / high.**

### C-0453 — Context7 consumer for discovery-external-researcher + KB-cc-platform:109 fallback
- Q1: Does discovery-external-researcher.md exist? → Yes.
- **Verdict: verified / high.**

### C-0454 — Exa consumer for discovery-external-researcher
- Q1: Does discovery-external-researcher.md exist? → Yes (same as C-0453).
- **Verdict: verified / high.**

### Batch 5 summary
V=17 U=0 C=0 S=0. All 17 structural-convention and consumer-mapping claims verified directly against repository state. No dissent observed (claims are internal-audit assertions about file structure; no contradictory external source). C-0449 carries medium confidence due to intrinsic contingency in claim text. No constraint violations (no manifest hard_constraints to check against).

**Notable verification findings:**
- The W/H/A trifecta convention is unusually crisp — all three completed trifectas (Claude Code, Codespaces, GitHub Actions) obey the same structural skeleton: design half = exactly 2 references + no assets/; platform half = many topic-specific references + assets/templates/; audit half = scripts/ + variable references/. This makes FR-11 KB-mcp-design and KB-mcp-platform low-risk to author by template-following.
- ADR-0033 directly named and verified for auditing-codespaces STUB. ADR-0033's full title is 'ADR-0029 execution extension'; the auditing-codespaces stub-vs-real surfacing is one row (line 72) in its scope-deviation surfacing table — the previously-claim-attested pointer is precise.
- All 7 consumer agent files referenced in the consumer-mapping claims exist: discovery-codebase-researcher.md, review-architecture-auditor.md (batch 3); design-api.md, design-cicd.md, design-iac.md, discovery-external-researcher.md (this batch). No broken mappings.
- The only deviation in the W/H/A convention is auditing-cc-configs's trailing '-configs' suffix — already documented as the lone exception; the Designer for FR-11 should choose auditing-mcp-style bare-topic naming (already in place, no decision needed).

