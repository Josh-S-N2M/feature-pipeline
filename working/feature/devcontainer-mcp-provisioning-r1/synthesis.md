# Synthesis — devcontainer-mcp-provisioning-r1

**Generated:** 2026-05-23
**Audience:** designer (per-layer designers in Stage 6)
**Pipeline mode:** feature-pipeline (single synthesis.md; no per-decision ADRs — ADR authorship is reserved to design-composer per FR-5 of recipe-feature-pipeline)
**Sources:** 9 (8 research notes + codebase-analysis-report)
**Claims:** 545 merged
**Decision frames:** 13 (5 architectural, 5 implementation, 3 operational)

---

## 1. Executive Summary

This feature provisions seven MCP servers (Serena, mcp-openapi-schema, actionlint-mcp, Terraform MCP, Context7, Exa, GitNexus with codebase-memory-mcp as ADR-0007-canonical fallback) into a single Debian-bookworm Python 3.11 devcontainer, exposes them to 36 Claude Code sub-agents under a least-privilege `mcp__<server>__<tool>` allowlist, and adds the W/H/A trifecta halves (KB-mcp-platform, KB-mcp-design) that complete the audit-only auditing-mcp skill family (C-0458, in synthesis pipeline). The pipeline has framed 13 decisions: five architectural (install-path posture, transport choice, UI-15 transition surfacing, credential redaction, Serena posture), five implementation (Node runtime feature, lifecycle-hook placement, log surface, health-check primitive, agent allowlist mapping), and three operational (KB authoring, version pinning, ADR-0018 drift remediation). All 13 carry a recommended option; one carries an unresolved human-required sub-question (auditing-mcp family-coordinator placement under D-0010).

The top-three risks are: (1) the F5.4 **no-consensus** finding on primary-to-fallback transition surfacing (C-0349, verbatim "NO CONSENSUS PATTERN" across 5 source categories) makes UI-15 a genuine novel-design call rather than a pattern lift; (2) **OWASP MCP01 Token Mismanagement** is the highest-ranked MCP risk (C-0333) and combines two anti-patterns (argv-leakage E-0094 and URL-embedded keys E-0095) that cannot be fixed at the log layer alone; (3) the **stdio no-reconnect** ground truth (C-0301, verbatim Anthropic) means six of seven servers fail open to operator recovery, which is what makes FR-9's structured-failure-record contract load-bearing rather than nice-to-have.

---

## 2. Source Inventory

| File | Claims | Source type | Verification posture |
|---|---|---|---|
| T-001-serena.md | 57 | research note (community + vendor) | verified-high (canonical uvx install, stdio default) |
| T-002-mcp-openapi-schema.md | 67 | research note (vendor + source-code) | verified-high (StdioServerTransport quoted from index.mjs, C-0062) |
| T-003-actionlint-mcp.md | 32 | research note (source-code + GH releases page) | verified-high incl. time-sensitive 'no releases' attestation (C-0133, verify-at-execution caveat) |
| T-004-terraform-mcp.md | 45 | research note (HashiCorp vendor docs) | verified-high (releases.hashicorp.com SHA256SUMS + GPG, C-0157/C-0190) |
| T-005-context7.md | 50 | research note (Upstash vendor docs + GitHub) | verified-high (https://mcp.context7.com/mcp, C-0203) |
| T-006-exa.md | 38 | research note (docs.exa.ai + GitHub + DeepWiki) | verified-high primary; one single-sourced precedence claim flagged fragile (C-0266) |
| T-007-mcp-operational.md | 87 | research note (Anthropic spec + OWASP + Fast.io + vendor blogs) | verified-high primary + four medium (Velida/Fast.io single-vendor pattern guides, C-0295/C-0296/C-0330/C-0361); F5.4 no-consensus survives scrutiny (C-0349) |
| T-008-gitnexus.md | 53 | research note (Mintlify-mirrored upstream) | partially_verified-medium for two skip-grammars claims (C-0388/C-0411 — Mintlify mirror; smoke-test required at install) |
| codebase-analysis-report.md | 116 | direct repo inspection | verified-high primary (grep-verified zero mcp__ usage C-0445; .mcp.json absent C-0462); two single-sourced file-count figures C-0484/C-0485 |

**Verification headline:** 98 critiques across 5 batches. Tally V=93, P=2 (partial — GitNexus Mintlify-mirrored skip-grammars), S=5 (single-sourced — DeepWiki precedence, two file-counts, OWASP taxonomy-by-definition, two medium-vendor pattern guides). **C=0 contradictions, D=0 dissent pairs.** The corpus is internally consistent; the only schema-level disagreement is ADR-0018 v1.0.0 vs KB/agent v1.1.0 drift (C-0441/C-0495) which is handled as a remediation frame (D-0012), not as dissent.

---

## 3. Decision Substrate

Source for this section: `04-decision-frames.json` (frames + rationale, in pipeline output) and `05-substrate-map.json` (recommended/rejected options with per-server tables, in pipeline output). One subsection per frame; option-count enumeration follows the implementation-strategy mode noted in `05-substrate-map.json` (`mode_note`, in pipeline output) — three-option-enumeration invariant does NOT apply.

### D-0001 — Install-path discipline (lifecycle-hook orchestration over Dockerfile-bake)

**Class:** architectural · **Reversibility:** two-way · **Blast radius:** service · **Wardley stage:** product · **RICE:** reach 7, impact 3.0, confidence 0.8, effort 3.0

**Decision statement.** Adopt a hybrid posture: devcontainer features for runtimes and CLIs (Node, Go, github-cli, claude-code), `postCreateCommand` idempotent script for the seven MCP-server installs, with per-server overrides for the binary-fetch (Terraform MCP) and go-install (actionlint-mcp) cases. No new project Dockerfile beyond what already exists ([T-001](T-001-serena.md) install paths, [codebase-analysis-report.md](codebase-analysis-report.md) Dockerfile-Yarn-key history).

**Options enumerated (4 — substrate map records 4 distinct postures plus the recommended hybrid).**
- **Recommended — `hybrid_features_plus_postcreate`** — Features for stable runtimes; postCreate for the seven server installs. Rationale: pushes idempotent work into postCreate where re-run is safe; keeps runtime provisioning in features where ghcr handles versioning; avoids re-litigating the E-0081 stale-Yarn-apt-key failure mode ([codebase-analysis-report.md](codebase-analysis-report.md)).
- **Rejected — `dockerfile_bake_everything`** — already-broken-once posture on this base image; mixed package managers inflate Dockerfile complexity ([codebase-analysis-report.md](codebase-analysis-report.md)).
- **Rejected — `features_only`** — no upstream features for 6 of 7 servers; authoring + maintaining seven feature repos is grossly disproportionate.
- **Rejected — `postcreate_for_everything`** — re-invents what ghcr.io/devcontainers/features/node and /go provide for free.

**Source-cited evidence.** Canonical install commands per server: Serena uvx (C-0002, [T-001-serena.md](research-notes/T-001-serena.md)); mcp-openapi-schema `npx -y` (C-0061, [T-002-mcp-openapi-schema.md](research-notes/T-002-mcp-openapi-schema.md)); actionlint-mcp `go install` (C-0125/C-0126, [T-003-actionlint-mcp.md](research-notes/T-003-actionlint-mcp.md)); Terraform MCP pre-built binary verified by SHA256SUMS + GPG (C-0157/C-0190/C-0193, [T-004-terraform-mcp.md](research-notes/T-004-terraform-mcp.md)); GitNexus uvx/npx with `GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1` (C-0388/C-0411, [T-008-gitnexus.md](research-notes/T-008-gitnexus.md)).

**Open dependencies on later frames.** D-0003 (Node feature must be present before npx installs), D-0004 (which hook hosts the install script), D-0011 (pin form per server).

### D-0002 — Transport (stdio vs remote HTTP) per server

**Class:** architectural · **Reversibility:** two-way · **Blast radius:** service · **Wardley stage:** product · **RICE:** reach 7, impact 2.0, confidence 0.8, effort 1.0

**Decision statement.** Per-server table: stdio for the five OSS-local servers; remote HTTP for the two SaaS-canonical servers (Context7, Exa). Transport selection is driven by what each vendor canonically publishes; "all stdio" and "all remote" are pseudo-options because five of seven are stdio-native and two of seven have vendor-canonical remote endpoints.

**Options enumerated (2 — pseudo-options collapse).**
- **Recommended — `per_server_vendor_canonical`** — Serena stdio (C-0009, [T-001-serena.md](research-notes/T-001-serena.md)); mcp-openapi-schema stdio via StdioServerTransport (C-0062, [T-002-mcp-openapi-schema.md](research-notes/T-002-mcp-openapi-schema.md)); actionlint-mcp stdio (C-0143, [T-003-actionlint-mcp.md](research-notes/T-003-actionlint-mcp.md)); Terraform MCP stdio (binary on PATH); GitNexus stdio; Context7 remote HTTP at `https://mcp.context7.com/mcp` (C-0203/C-0208, [T-005-context7.md](research-notes/T-005-context7.md)); Exa remote HTTP at `https://mcp.exa.ai/mcp` (C-0256/C-0279/C-0284, [T-006-exa.md](research-notes/T-006-exa.md)). HTTP servers inherit Claude Code's 5-attempt exponential-backoff reconnect (C-0300, [T-007-mcp-operational.md](research-notes/T-007-mcp-operational.md)).
- **Rejected — `all_stdio_with_local_fallback_binaries`** — loses the HTTP auto-reconnect safety net for the two SaaS-canonical servers; forces us to maintain local-fallback infrastructure for vendor-SaaS-canonical surfaces ([T-007-mcp-operational.md](research-notes/T-007-mcp-operational.md)).

**Source-cited evidence.** Stdio-no-reconnect ground truth: "Stdio servers are local processes and are not reconnected automatically." (C-0301 verbatim Anthropic, [T-007-mcp-operational.md](research-notes/T-007-mcp-operational.md)). HTTP/SSE retry: 5 attempts mid-session + 3 initial-connect retries on v2.1.121 (C-0300/C-0302, [T-007-mcp-operational.md](research-notes/T-007-mcp-operational.md)).

**Open dependencies.** D-0007 (HTTP servers need header-name redaction added to allowlist); D-0008 (probe primitive must work across both transports).

### D-0003 — Node.js runtime via devcontainer feature

**Class:** implementation · **Reversibility:** two-way · **Blast radius:** service · **Wardley stage:** commodity · **RICE:** reach 4, impact 2.0, confidence 0.8, effort 0.25

**Decision statement.** Add `ghcr.io/devcontainers/features/node:1` with an explicit Node LTS major pin (Node 20) to `devcontainer.json`. Four of seven MCP servers transitively require Node (mcp-openapi-schema via npx, Context7/Exa local fallbacks, GitNexus TS-first stdio); the base image ships no Node ([T-002-mcp-openapi-schema.md](research-notes/T-002-mcp-openapi-schema.md), [T-008-gitnexus.md](research-notes/T-008-gitnexus.md)).

**Options enumerated (3).**
- **Recommended — `ghcr_node_feature`** — declarative, ghcr-hosted, LTS-pinnable. Matches precedent of ghcr.io/devcontainers/features/github-cli already in use ([codebase-analysis-report.md](codebase-analysis-report.md)).
- **Rejected — `dockerfile_apt_nodesource`** — already-burned-on-apt-keys posture (E-0081).
- **Rejected — `nvm_postcreate`** — nvm is right for multi-version Node workflows; we need one pinned LTS.

**Source-cited evidence.** Node-requirement on four servers (C-0061/C-0064/C-0096/C-0097/C-0098/C-0099/C-0100, [T-002-mcp-openapi-schema.md](research-notes/T-002-mcp-openapi-schema.md)); base-image runtimes-absent enumeration (E-0015, E-0016 conflicts_with, in pipeline output). Tree-sitter C++ toolchain cost mitigated by `GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1` (C-0388/C-0411, [T-008-gitnexus.md](research-notes/T-008-gitnexus.md) — partially_verified-medium; smoke-test required).

**Open dependencies.** D-0001 (postCreate hook invokes npx after feature provisions Node).

### D-0004 — Lifecycle-hook placement (postCreate install + postStart probe)

**Class:** implementation · **Reversibility:** two-way · **Blast radius:** service · **Wardley stage:** product · **RICE:** reach 7, impact 1.0, confidence 0.8, effort 0.5

**Decision statement.** `postCreateCommand` runs the idempotent install script and an initial install-verification ping for all seven servers (one-shot, idempotent). `postStartCommand` runs a fast readiness probe (ping each server) and writes the result to `.claude/runtime/mcp-events.jsonl`. `onCreateCommand` is unused (too early for stdio servers needing project mount); `postAttachCommand` is unused.

**Options enumerated (2 — substrate map collapses 4 hook-points into the meaningful split).**
- **Recommended — `layered_postcreate_install_poststart_probe`** — separates once-per-create install from every-start readiness, captures both classes of FR-8 failure. Aligns with claims attributing install completion to postCreate and recurring readiness to postStart ([T-007-mcp-operational.md](research-notes/T-007-mcp-operational.md)).
- **Rejected — `single_poststart_only`** — conflates two failure modes; risks masking install-time failures when postStart re-run silently passes.

**Source-cited evidence.** postCreate semantics (C-0156/C-0240, in claims corpus); postStart readiness wiring (C-0344/C-0367/C-0436, [T-007-mcp-operational.md](research-notes/T-007-mcp-operational.md)). Note: lifecycle-hook semantics are single-sourced (devcontainer.json docs interpretation; flagged in frame risks).

**Open dependencies.** D-0008 (probe primitive — JSON-RPC ping); D-0005 (mcp-events.jsonl event-shape); D-0006 (log surface).

### D-0005 — Primary-to-fallback transition surfacing (UI-15)

**Class:** architectural · **Reversibility:** ONE-WAY · **Blast radius:** tenant · **Wardley stage:** genesis · **RICE:** reach 36, impact 2.0, confidence 0.8, effort 2.0

**Decision statement.** On every primary-to-fallback transition, append a structured JSON record to `.claude/runtime/mcp-events.jsonl` (fields: `ts`, `event=primary_degraded`, `primary_server`, `fallback_server`, `reason`, `agent`, `extraction_method`). Paired with a one-line stderr banner from whichever MCP component detects the transition (ephemeral operator hint). Agents do NOT template-print transition acknowledgements in their own output — the jsonl is the FR-9 contract.

**This is the load-bearing one-way design call in this feature.** [T-007-mcp-operational.md](research-notes/T-007-mcp-operational.md) F5.4 verifies verbatim "NO CONSENSUS PATTERN" across five surveyed source categories (C-0349, verdict verified-high).

**Options enumerated (4).**
- **Recommended — `combined_jsonl_plus_stderr_banner`** — combines machine-readability with ephemeral operator hint; avoids the uniformity risk of 36 agents adopting a free-text convention.
- **Rejected — `jsonl_only`** — operator-invisible until someone tails the file.
- **Rejected — `stderr_banner_only`** — loses machine-readability; FR-9 falls back on ad-hoc stderr parsing.
- **Rejected — `agent_level_acknowledgement`** — uniformity risk across 36 agents (C-0357, [T-007-mcp-operational.md](research-notes/T-007-mcp-operational.md)).
- **Rejected — `frontmatter_convention_only`** — declarative-only; doesn't solve the transition-event surface.

**Source-cited evidence.** F5.4 NO CONSENSUS verbatim (C-0349, [T-007-mcp-operational.md](research-notes/T-007-mcp-operational.md)). Three corpus-surfaced options (C-0352 stderr banner; C-0353 jsonl; C-0354 agent-level ack — [T-007-mcp-operational.md](research-notes/T-007-mcp-operational.md)). Closest analogue is microservice circuit-breaker, explicitly disclaimed as "not MCP-specific" (C-0351, [T-007-mcp-operational.md](research-notes/T-007-mcp-operational.md)). Current wiring is prose-only across ADR-0007 → ADR-0018 → KB → agent (C-0448, [codebase-analysis-report.md](codebase-analysis-report.md)).

**Open dependencies.** D-0006 (log surface — jsonl reserved for coarse events, not per-line mirror); D-0010 (KB-mcp-design owns the schema documentation); D-0012 (ADR-0018 schema bump — the jsonl event-shape is a natural new field).

### D-0006 — Runtime log surface

**Class:** implementation · **Reversibility:** two-way · **Blast radius:** service · **Wardley stage:** product · **RICE:** reach 7, impact 1.0, confidence 0.8, effort 1.5

**Decision statement.** All seven servers log to stderr (the MCP-spec default for stdio; HTTP servers' logs come through Claude Code's HTTP client logging). Claude Code captures stderr automatically. The shared `.claude/runtime/mcp-events.jsonl` is reserved for cross-server event correlation (UI-15 transitions, FR-8 readiness probe results, FR-9 structured failure records) — NOT a per-line log mirror.

**Options enumerated (3).**
- **Recommended — `stderr_default_plus_mcp_events_jsonl_for_transitions`** — aligns with MCP spec, gets auto-capture for free, reserves jsonl for actually-structured events.
- **Rejected — `structured_json_stderr_per_server`** — seven upstream servers don't agree on log format; wrapping each is disproportionate.
- **Rejected — `proxy_supervisor_toolhive_style`** — new long-running process; crash blast-radius wider than the seven it wraps ([T-007-mcp-operational.md](research-notes/T-007-mcp-operational.md)).

**Source-cited evidence.** Stdio stderr-not-stdout: Anthropic Debugging quote "Local MCP servers should not log messages to stdout." (C-0313, [T-007-mcp-operational.md](research-notes/T-007-mcp-operational.md)). **Calibration note:** source uses "should not" not RFC-2119 "MUST NOT"; the claim's paraphrase "must" is acceptable but the synthesizer does not represent this as a literal protocol MUST. Stderr auto-capture by host (C-0314, [T-007-mcp-operational.md](research-notes/T-007-mcp-operational.md)).

**Open dependencies.** D-0005 (jsonl event-shape contract); D-0007 (redaction at log-surface boundary).

### D-0007 — Credential redaction (redact-at-source from .mcp.json env block)

**Class:** architectural · **Reversibility:** ONE-WAY · **Blast radius:** org · **Wardley stage:** product · **RICE:** reach 36, impact 3.0, confidence 0.8, effort 1.5

**Decision statement.** At the log-surface boundary, apply a redaction filter keyed on the env-var NAMES declared in `.mcp.json`'s `env:` block plus HTTP-header names for HTTP transports (CONTEXT7_API_KEY, Authorization, x-api-key). Replace matched values with the literal `[REDACTED:<envvar>]`. Reject Exa's `exaApiKey` query-param URL form at `.mcp.json` validation time, not at log time.

**Single-option decision with credible no-alternatives rationale.** The frame-enumerated "alternatives" reduce to deferral or duplication; OWASP MCP01 prescribes the property, not the mechanism.

**Source-cited evidence.** OWASP MCP01 Token Mismanagement is the highest-ranked MCP risk (C-0333) with verbatim guidance "Redact or mask secrets before writing to logs or telemetry" (C-0335, [T-007-mcp-operational.md](research-notes/T-007-mcp-operational.md)). argv-leakage anti-pattern E-0094 (C-0248/C-0261, in pipeline output) — OS-level; redaction at log surface cannot fix process-listing exposure (composes with secret-via-env-only invocation discipline). URL-embedded-credential anti-pattern E-0095 (C-0259/C-0260/C-0280, [T-006-exa.md](research-notes/T-006-exa.md)) — Exa's exaApiKey query-param form must be rejected at config validation, not at log layer. Strongest pattern endorsement: at-instrumentation-source by header/env-var name (C-0330, Velida + [T-007-mcp-operational.md](research-notes/T-007-mcp-operational.md), verdict verified-medium because Velida is single-vendor blog but principle multi-source-corroborated by OWASP MCP01).

**Open dependencies.** D-0002 (HTTP-transport header names must be enumerated in allowlist); D-0006 (this filter lives at the log-surface boundary chosen there); D-0009 (mcp__ tools allowlist must not surface raw credentials in tool args).

### D-0008 — Health-check primitive (MCP JSON-RPC ping + authenticated probe for HTTP servers)

**Class:** implementation · **Reversibility:** two-way · **Blast radius:** service · **Wardley stage:** product · **RICE:** reach 7, impact 1.0, confidence 0.8, effort 0.5

**Decision statement.** Use the MCP-spec JSON-RPC ping (C-0290/C-0291) as the canonical readiness primitive in `postStartCommand` for all seven servers. For Context7 and Exa, supplement with one explicit authenticated read-only probe call (Context7: `resolve-library-id` with a known id; Exa: `web_search_exa` with a trivial query) gated behind an environment flag so probes can be disabled when API quotas matter.

**Options enumerated (2).**
- **Recommended — `json_rpc_ping_plus_optional_probe`** — spec-canonical, transport-agnostic, endorsed by Fast.io monitoring guidance.
- **Rejected — `claude_mcp_list_parsing`** — brittle host-side CLI scraping; no SemVer contract on Claude Code's output format.

**Source-cited evidence.** Spec verbatim "The receiver MUST respond promptly with an empty response" (C-0290, [T-007-mcp-operational.md](research-notes/T-007-mcp-operational.md)). Ping uniformity across stdio and HTTP (C-0291, [T-007-mcp-operational.md](research-notes/T-007-mcp-operational.md)). Fast.io endorsement of 30s interval + 2-5s timeout + 3-failure threshold (C-0295/C-0296, [T-007-mcp-operational.md](research-notes/T-007-mcp-operational.md), verdict verified-medium because Fast.io is single-vendor pattern guide; numbers consistent with industry liveness-probe heuristics). The auth-probe supplement addresses the frame-noted risk that ping does not validate auth (e.g., bad CONTEXT7_API_KEY ping-responds fine).

**Open dependencies.** D-0004 (probe runs in postStart); D-0005 (probe result appended to mcp-events.jsonl).

### D-0009 — Tool-to-agent allowlist (mcp__ namespace, UI-1)

**Class:** implementation · **Reversibility:** two-way · **Blast radius:** tenant · **Wardley stage:** custom · **RICE:** reach 36, impact 2.0, confidence 0.8, effort 2.0

**Decision statement.** Each agent's `tools` allowlist gets exactly the `mcp__<server>__<tool>` entries its role requires. Non-consumers get no MCP tools added. All 36 sub-agents currently have ZERO mcp__ entries (C-0445, grep-verified, [codebase-analysis-report.md](codebase-analysis-report.md)); this feature introduces the mcp__ pattern for the first time (C-0446, [codebase-analysis-report.md](codebase-analysis-report.md)).

**Single-option decision.** "Broad wildcard" violates the existing least-privilege convention; "narrow per-agent" is the convention. The work is producing the table.

**Mapping table (from substrate-map):**
| Agent | mcp__ entries |
|---|---|
| design-api | `mcp__mcp-openapi-schema__*` |
| design-cicd | `mcp__actionlint-mcp__*` |
| design-iac | `mcp__terraform-mcp__*` |
| discovery-external-researcher | `mcp__context7__resolve-library-id`, `mcp__context7__get-library-docs`, `mcp__exa__web_search_exa`, `mcp__exa__company_research_exa`, `mcp__exa__crawling_exa` |
| discovery-codebase-researcher | `mcp__gitnexus__*`, `mcp__codebase-memory-mcp__*` (fallback per ADR-0007 v2.2.0) |
| review-architecture-auditor | `mcp__gitnexus__*`, `mcp__codebase-memory-mcp__*` (fallback per ADR-0007 v2.2.0) |
| (Serena) | conditional on D-0013 outcome — narrowed to ~6 Python-touching agents |
| (all other 30+ agents) | no mcp__ entries (zero existing usage preserved) |

**Source-cited evidence.** Zero existing mcp__ usage (C-0445, [codebase-analysis-report.md](codebase-analysis-report.md)). Per-agent consumer claims: design-api/mcp-openapi-schema (C-0450); design-cicd/actionlint-mcp (C-0451); design-iac/Terraform MCP (C-0452); discovery-external-researcher/Context7+Exa (C-0453/C-0454, [codebase-analysis-report.md](codebase-analysis-report.md)); discovery-codebase-researcher and review-architecture-auditor primary/fallback per ADR-0007 v2.2.0 (C-0447/C-0448, [codebase-analysis-report.md](codebase-analysis-report.md)).

**Open dependencies.** D-0013 (Serena row); D-0011 (tool-id changes — Context7 v1.2.0 ReplaceContentTool replaces ReplaceRegexTool means the entries are version-coupled).

### D-0010 — KB-mcp-platform + KB-mcp-design authoring (FR-11)

**Class:** operational · **Reversibility:** two-way · **Blast radius:** tenant · **Wardley stage:** custom · **RICE:** reach 36, impact 1.0, confidence 0.8, effort 3.0

**Decision statement.** Author `KB-mcp-platform/SKILL.md` and `KB-mcp-design/SKILL.md` following the `KB-cc-platform` + `KB-cc-design` template verbatim: ADR-0020 frontmatter, ADR-0030 pedagogical_sections, sister-cross-reference convention (auditing-mcp <-> KB-mcp-platform/design), body-prose family membership. Augment auditing-mcp.

**Single-option decision** — three existing W/H/A trifectas (CC, Codespaces, GHA) pass review with consistent convention (C-0455/C-0456/C-0457/C-0458, [codebase-analysis-report.md](codebase-analysis-report.md)); varying for MCP creates a 4th template to maintain with zero benefit.

**HUMAN DECISION POINT (surfaced from substrate-map).** The family-coordinator question must be resolved before authoring: should auditing-mcp graduate to its own family with KB-mcp-platform/design as its sister halves, OR keep auditing-mcp in the auditing-cc-configs family (current state, declared at line 30 of auditing-mcp per C-0460, [codebase-analysis-report.md](codebase-analysis-report.md)) with KB-mcp-platform/design as sibling knowledge skills with explicit cross-refs? The synthesizer does NOT decide this — surface to user / design-composer.

**Source-cited evidence.** auditing-mcp exists; KB-mcp-platform and KB-mcp-design are absent (C-0458 grep-verified, [codebase-analysis-report.md](codebase-analysis-report.md)). Trifecta structural convention: design halves carry exactly two reference files (patterns-and-anti-patterns.md + principles.md) and no assets/ (C-0478/C-0479, [codebase-analysis-report.md](codebase-analysis-report.md)); platform halves carry many topic references plus assets/templates/ (C-0480, [codebase-analysis-report.md](codebase-analysis-report.md)); audit halves carry Python scripts/ (C-0481, [codebase-analysis-report.md](codebase-analysis-report.md)). ADR-0020 skill-naming with lone deviation auditing-cc-configs (C-0471/C-0535, [codebase-analysis-report.md](codebase-analysis-report.md)). Sister-cross-reference convention universal across 3 trifectas (C-0482, [codebase-analysis-report.md](codebase-analysis-report.md)). auditing-codespaces STUB per ADR-0033 directly re-verified (C-0499, [codebase-analysis-report.md](codebase-analysis-report.md)).

**Open dependencies.** D-0005 (KB-mcp-design owns the mcp-events.jsonl schema); D-0009 (KB-mcp-platform owns the .mcp.json template); D-0012 (auditing-mcp will reference the ADR-0018 v1.1.0 contract); D-0007 (KB-mcp-platform documents the redaction allowlist contract).

### D-0011 — Version-pinning policy (exact-tag where available, commit-SHA for actionlint-mcp)

**Class:** operational · **Reversibility:** two-way · **Blast radius:** service · **Wardley stage:** commodity · **RICE:** reach 7, impact 1.0, confidence 0.8, effort 0.25

**Decision statement.** Per-server pinning where each server's pin form is driven by its upstream release shape. Exact tag where releases exist; commit SHA where no tags exist (actionlint-mcp). Pin-then-review discipline (E-0074) is mandatory.

**Per-server pin table:**
| Server | Pin form | Rationale |
|---|---|---|
| Serena | exact tag (pin pre-v1.3.0 pending base_modes→added_modes review) | C-0040/C-0042 |
| mcp-openapi-schema | exact tag `0.0.1` (single-release static ~14 months) | C-0060/C-0073/C-0110 |
| actionlint-mcp | commit SHA via `go install <repo>@<sha>` | C-0133/C-0153 (no tagged releases as of 2026-05-23 — verify-at-execution) |
| Terraform MCP | exact tag matching pre-built-binary release asset | C-0158 (e.g., `0.5.2`) |
| Context7 | vendor-controlled at remote endpoint | C-0232 |
| GitNexus | exact tag per ADR-0007 v2.2.0 | C-0421/C-0422/C-0423 |
| Exa | vendor-controlled at remote endpoint | (vendor SaaS) |

**Source-cited evidence.** Repo convention E-0073 with periodic-supply-chain-review E-0074. Witnessed breaking changes: Serena v1.3.0 base_modes→added_modes (C-0036/C-0041, [T-001-serena.md](research-notes/T-001-serena.md)); Context7 v1.2.0 ReplaceContentTool replaces ReplaceRegexTool (C-0037, [T-005-context7.md](research-notes/T-005-context7.md)).

**Open dependencies.** D-0009 (Context7 tool-id breaking change drives allowlist coupling).

### D-0012 — ADR-0018 schema-drift remediation (bump to v1.1.0)

**Class:** operational · **Reversibility:** two-way · **Blast radius:** tenant · **Wardley stage:** product · **RICE:** reach 3, impact 1.0, confidence 0.8, effort 0.5

**Decision statement.** Bump ADR-0018 schema_version frontmatter and JSON example body to 1.1.0. Add a section explicitly documenting the blast-radius extension. Add a schema-version history table. Update the two downstream consumers (discovery-codebase-researcher, review-architecture-auditor) to validate against v1.1.0. Adjacent fix: relocate or cross-reference ADR-0007 from `adrs-migrated/` to `adrs/` (E-0080, low severity per C-0498, [codebase-analysis-report.md](codebase-analysis-report.md)).

**Options enumerated (2).**
- **Recommended — `bump_adr_0018_to_v_1_1_0`** — eliminates drift at source; ADR is the contract.
- **Rejected — `clarify_in_adr_kb_is_v_1_1_0_source`** — splits contract across two documents.

**Source-cited evidence.** Drift directly verified: ADR-0018 declares v1.0.0 (frontmatter + JSON example body); KB-codebase-research/SKILL.md and discovery-codebase-researcher.md both reference v1.1.0 with "extended for blast-radius" (C-0441/C-0495, [codebase-analysis-report.md](codebase-analysis-report.md)). Medium severity (C-0496, [codebase-analysis-report.md](codebase-analysis-report.md)). ADR-0007 lives in adrs-migrated/ (five variants, current v2.2.0 Accepted; absent from adrs/ — C-0442/C-0497, [codebase-analysis-report.md](codebase-analysis-report.md)).

**Open dependencies.** D-0005 (jsonl event-shape is a natural new schema field for v1.1.0); D-0010 (auditing-mcp documentation references the v1.1.0 contract).

### D-0013 — Serena always-on posture (UI-8: narrowed)

**Class:** architectural · **Reversibility:** two-way · **Blast radius:** tenant · **Wardley stage:** product · **RICE:** reach 36, impact 2.0, confidence 0.5 (calibrated lower due to single-sourced file-counts), effort 1.0

**Decision statement.** Keep Serena in `.mcp.json` (always-on at the project level) but restrict `mcp__serena__*` tool entries in the 36 agent allowlists to only those whose role actually touches Python code: review-architecture-auditor, the design-* agents that touch tooling Python, and any code-spelunking discovery agent. Markdown-dominant agents get no Serena tools. Pin Serena pre-v1.3.0 while base_modes→added_modes breaking change is reviewed (E-0098).

**Options enumerated (3).**
- **Recommended — `narrowed_always_on_python_audit_surface_only`** — 73.8% markdown corpus means Serena's LSP-symbol value-prop is narrow but non-zero; the 52 Python audit scripts are the real symbol-rich surface.
- **Rejected — `full_always_on`** — mismatch with markdown-dominant corpus; violates least-privilege; every agent inherits Serena's breaking-change blast-radius.
- **Rejected — `drop_from_always_on`** — loses the LSP-symbol value-prop for the 52 Python audit-script surface where it genuinely helps. GitNexus is repo-graph-canonical not in-file-LSP-canonical; the two are complementary.

**Source-cited evidence.** Repo composition: 468 markdown / 634 non-git non-node_modules = 73.8% (C-0484/C-0485, single_sourced-medium, [codebase-analysis-report.md](codebase-analysis-report.md)). Symbol density concentrated in 52 Python audit scripts (C-0490 verified, [codebase-analysis-report.md](codebase-analysis-report.md)). GitNexus canonical primary per ADR-0007 v2.2.0 (C-0447/C-0491, [codebase-analysis-report.md](codebase-analysis-report.md)). UI-8 contingency hedge (C-0449, [codebase-analysis-report.md](codebase-analysis-report.md)). Serena v1.3.0 breaking change (E-0098, [T-001-serena.md](research-notes/T-001-serena.md)).

**Open dependencies.** D-0009 (Serena row in agent allowlist mapping); D-0011 (pin pre-v1.3.0).

---

## 4. Per-Server Implementation Brief

A single reference table that the per-layer designers should treat as the source of truth for what each server costs and produces.

### Per-server matrix

| Server | Transport | Install command | Auth env-var | Tools (allowlist surface) | Pin form | Primary consumer agent(s) | Base-image impact |
|---|---|---|---|---|---|---|---|
| **Serena** | stdio | `uvx --from git+https://github.com/oraios/serena serena start-mcp-server` (C-0002, [T-001-serena.md](research-notes/T-001-serena.md)) | none | `mcp__serena__*` (narrowed per D-0013) | exact tag pre-v1.3.0 (C-0040/C-0042) | review-architecture-auditor + Python-touching design agents (D-0013) | requires `uv` (not in base; `pip install uv` or astral.sh installer — C-0005 verified-medium) |
| **mcp-openapi-schema** | stdio (`StdioServerTransport` from @modelcontextprotocol/sdk — C-0062 verified-high, source-code-anchored) | `npx -y mcp-openapi-schema <path-to-spec>` (C-0061, [T-002-mcp-openapi-schema.md](research-notes/T-002-mcp-openapi-schema.md)) | none (C-0063, [T-002-mcp-openapi-schema.md](research-notes/T-002-mcp-openapi-schema.md)) | `mcp__mcp-openapi-schema__*` | exact tag `0.0.1` (C-0060; 14-month static, abandonment-vs-stable ambiguity surfaced) | design-api (C-0450) | requires Node (added by D-0003 feature) |
| **actionlint-mcp** | stdio (C-0143 verified-high) | `go install github.com/2manymws/actionlint-mcp/cmd/actionlint-mcp@<sha>` (C-0125/C-0134, [T-003-actionlint-mcp.md](research-notes/T-003-actionlint-mcp.md)) | none (C-0147, [T-003-actionlint-mcp.md](research-notes/T-003-actionlint-mcp.md)) | `mcp__actionlint-mcp__lint_workflow`, `mcp__actionlint-mcp__check_all_workflows` (exactly two tools — C-0144) | **commit SHA** (no tagged releases — C-0133/C-0153, verify-at-execution) | design-cicd (C-0451) | requires Go toolchain (added by D-0001 feature) |
| **Terraform MCP** | stdio | wget pre-built binary + SHA256SUMS + GPG verify (C-0157/C-0190/C-0193, [T-004-terraform-mcp.md](research-notes/T-004-terraform-mcp.md)) | TFE_TOKEN (only for Terraform Cloud/Enterprise; local-only operation is no-auth) | `mcp__terraform-mcp__*` | exact tag (e.g., `0.5.2`, C-0158) | design-iac (C-0452) | no toolchain (statically-linked Go binary); conflicts with no-DinD (C-0193, no Docker path) |
| **Context7** | remote HTTP (`https://mcp.context7.com/mcp` — C-0203 verified-high, [T-005-context7.md](research-notes/T-005-context7.md)) | `.mcp.json` HTTP entry with `CONTEXT7_API_KEY` header (C-0208) | CONTEXT7_API_KEY (Codespaces secret) | `mcp__context7__resolve-library-id`, `mcp__context7__get-library-docs`; **tool-id breaking change in v1.2.0: ReplaceContentTool replaces ReplaceRegexTool** (C-0037) | vendor-controlled at endpoint | discovery-external-researcher (C-0453); KB-cc-platform:109 lists Context7 as a fallback consumer | none (no local install for HTTP path) |
| **Exa** | remote HTTP (`https://mcp.exa.ai/mcp` — C-0256/C-0279, [T-006-exa.md](research-notes/T-006-exa.md)) | `claude mcp add --transport http exa https://mcp.exa.ai/mcp --header "x-api-key: ${EXA_API_KEY}"` (C-0284; OQ: --header CLI support unconfirmed; if unsupported, header lives in .mcp.json) | EXA_API_KEY (Codespaces secret); URL-embedded `exaApiKey` query-param form REJECTED at config validation (E-0095 anti-pattern, C-0259/C-0280) | `mcp__exa__web_search_exa`, `mcp__exa__company_research_exa`, `mcp__exa__crawling_exa` | vendor-controlled at endpoint | discovery-external-researcher (C-0454) | none |
| **GitNexus** | stdio (TS-first stdio process) | `uvx`/`npx` invocation with `GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1` (C-0388/C-0411, [T-008-gitnexus.md](research-notes/T-008-gitnexus.md); partially_verified-medium; **smoke-test required**) | none | `mcp__gitnexus__*` | exact tag per ADR-0007 v2.2.0 (C-0421/C-0422/C-0423) | discovery-codebase-researcher (primary), review-architecture-auditor (primary) per ADR-0007 v2.2.0 (C-0447) | requires Node (added by D-0003); skip-grammars flag drops Dart/Proto/Swift C++ build cost (C-0411) |
| **codebase-memory-mcp** (fallback only) | stdio | (per ADR-0007 v2.2.0 / ADR-0018 fallback wiring) | none | `mcp__codebase-memory-mcp__*` (fallback only, per primary-degraded transition surfacing D-0005) | per ADR-0007 v2.2.0 | discovery-codebase-researcher (fallback), review-architecture-auditor (fallback) per ADR-0007 v2.2.0 (C-0448) | (per ADR-0007 v2.2.0) |

### Per-server open questions for execution-time verification

- **mcp-openapi-schema:** confirm 0.0.1 still latest at install time (14-month static; abandonment-vs-stable ambiguity, C-0073).
- **actionlint-mcp:** re-verify "no releases" at install time — maintainer can publish at any time (C-0133 time-sensitive).
- **Exa:** confirm Claude Code CLI `--header` flag support (OQ-T006-1, [T-006-exa.md](research-notes/T-006-exa.md)); if unsupported, header lives in `.mcp.json` block.
- **GitNexus:** smoke-test `GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1` works on pinned tag (C-0388/C-0411 partially_verified-medium, Mintlify-mirrored).
- **Terraform MCP:** confirm `0.5.2` is current stable at execution time (C-0158, published 2026-04-28).

---

## 5. Operational Discipline Brief

Synthesized from T-007 (87 claims, 5 batches verified). The per-layer designers should treat this as the contract surface.

- **Ping is the canonical health-check primitive.** MCP spec JSON-RPC `ping`; receiver MUST respond promptly with an empty response (C-0290 verbatim, [T-007-mcp-operational.md](research-notes/T-007-mcp-operational.md)). Works uniformly across stdio and HTTP transports (C-0291) — the only spec-canonical primitive with this property. The HTTP `/health` convention is HTTP-only and does not generalize.
- **Stdio servers are NOT auto-reconnected by Claude Code.** Verbatim Anthropic: "Stdio servers are local processes and are not reconnected automatically." (C-0301, [T-007-mcp-operational.md](research-notes/T-007-mcp-operational.md)). Six of seven servers in this feature are stdio → most failure modes are operator-recovered → FR-9 structured-failure-record is load-bearing, not nice-to-have.
- **HTTP/SSE retry behavior (Claude Code v2.1.121).** Initial-connect: 3 retries (C-0302). Mid-session: 5 attempts, exponential backoff from 1s (C-0300). Design should not hard-code dependence on exact retry counts (version-pinned behavior).
- **Stdio MUST log to stderr (calibrated).** Anthropic Debugging guide modal: "Local MCP servers should not log messages to stdout." (C-0313, [T-007-mcp-operational.md](research-notes/T-007-mcp-operational.md)) — strong engineering recommendation, **NOT RFC-2119 MUST NOT**. Claude Code captures stderr automatically (C-0314).
- **Redaction at log-surface boundary, env-var-name-keyed.** OWASP MCP01 verbatim: "Redact or mask secrets before writing to logs or telemetry" (C-0335). The .mcp.json env: block is the single source of truth for the redaction allowlist. Velida's at-instrumentation-source-by-header/env-var-name pattern is the strongest implementation (C-0330, verified-medium because Velida is single-vendor blog but principle multi-source corroborated).
- **`.claude/runtime/mcp-events.jsonl` is the durable cross-server event surface.** Reserved for: UI-15 primary-to-fallback transitions (D-0005); FR-8 readiness probe results (D-0004/D-0008); FR-9 structured failure records. NOT a per-line log mirror. Schema is owned by KB-mcp-design (D-0010).
- **Local-only runtime monitoring.** No long-running supervisor (ToolHive-style proxy rejected at D-0006 — new long-running process whose crash blast-radius is wider than the seven it wraps). Fast.io's 30s ping interval, 2-5s timeout, 3-failure threshold (C-0295/C-0296, [T-007-mcp-operational.md](research-notes/T-007-mcp-operational.md), verified-medium) are reference numbers for the postStartCommand readiness probe; the lifecycle hook is one-shot and does NOT run an active ping-loop sidecar (E-0084 supervisor pattern is out of scope).
- **The two anti-patterns that the design must defend against.** (a) argv-leaked secrets E-0094 — OS-level process-listing exposure; cannot be fixed at log layer; composes with "secrets via env-var only, never CLI flag" invocation discipline (C-0205 note: Context7 `--api-key` flag form is rejected for this reason). (b) URL-embedded credential E-0095 — Exa's `exaApiKey` query-param form leaks via browser history / proxy logs / server access logs / MCP client config dumps (C-0280); rejected at .mcp.json validation time.

---

## 6. Pattern Archaeology — W/H/A Trifecta Structural Convention

Synthesized from Batch 3 + Batch 5 (37 claims grep-verified against repo state). These are the structural inputs the FR-11 design must mirror.

### The trifecta skeleton

The three existing W/H/A trifectas (Claude Code, Codespaces, GitHub Actions) follow a consistent structural skeleton. The MCP trifecta (KB-mcp-platform, KB-mcp-design + existing auditing-mcp) should mirror it.

| Dimension | Design half (KB-*-design) | Platform half (KB-*-platform) | Audit half (auditing-*) |
|---|---|---|---|
| **Reference files** | exactly 2: `patterns-and-anti-patterns.md` + `principles.md` (C-0478, [codebase-analysis-report.md](codebase-analysis-report.md)) | many topic-specific .md (cc=7, codespaces=10, gha=19) (C-0480, [codebase-analysis-report.md](codebase-analysis-report.md)) | variable; topic-specific |
| **assets/templates/** | NONE (C-0479, [codebase-analysis-report.md](codebase-analysis-report.md)) | present, many .example/.yml templates (cc=9, codespaces=5 incl. subdirs, gha=21) (C-0480, [codebase-analysis-report.md](codebase-analysis-report.md)) | none |
| **scripts/ (Python)** | none | none (C-0481, [codebase-analysis-report.md](codebase-analysis-report.md)) | present (cc-configs=6, gha=1, codespaces=1 stub, mcp=4) (C-0481, [codebase-analysis-report.md](codebase-analysis-report.md)) |
| **Skill name convention** | `kb-<topic>-design` (ADR-0020 lowercase-hyphenated) (C-0471/C-0535, [codebase-analysis-report.md](codebase-analysis-report.md)) | `kb-<topic>-platform` | `auditing-<topic>` (bare topic; `auditing-cc-configs` is the lone deviation) (C-0471, [codebase-analysis-report.md](codebase-analysis-report.md)) |
| **Sister cross-reference** | description names sister platform-half ("Pairs with KB-<topic>-platform") (C-0482, [codebase-analysis-report.md](codebase-analysis-report.md)) | description names sister design-half ("Pairs with KB-<topic>-design") | description names paired KB halves |
| **Family membership** | body-prose, NOT a frontmatter field (C-0483/C-0537, [codebase-analysis-report.md](codebase-analysis-report.md)) | body-prose | body-prose ("This skill is part of the **<family>** family.") — auditing-mcp at line 30: "auditing-cc-configs" family (C-0460, [codebase-analysis-report.md](codebase-analysis-report.md)) |
| **Pedagogical sections** | per ADR-0030 `pedagogical_sections` frontmatter convention (C-0528, [codebase-analysis-report.md](codebase-analysis-report.md)) | per ADR-0030 | per ADR-0030 |

### Trifecta completeness state (pre-feature)

| Family | Design half | Platform half | Audit half | State |
|---|---|---|---|---|
| Claude Code | KB-cc-design (exists) | KB-cc-platform (exists) | auditing-cc-configs (exists; lone naming deviation) | COMPLETE (C-0455, [codebase-analysis-report.md](codebase-analysis-report.md)) |
| Codespaces | KB-codespaces-design (exists) | KB-codespaces-platform (exists) | auditing-codespaces (**STUB per ADR-0033**; emits `{"stub": true, "findings": []}`, C-0499 directly ADR-re-verified) | COMPLETE-WITH-STUB (C-0456, [codebase-analysis-report.md](codebase-analysis-report.md)) |
| GitHub Actions | KB-github-actions-design (exists) | KB-github-actions-platform (exists) | auditing-github-actions (exists; consumes auditing-shared per ADR-0031) | COMPLETE (C-0457, [codebase-analysis-report.md](codebase-analysis-report.md)) |
| **MCP** | **KB-mcp-design (ABSENT — greenfield)** | **KB-mcp-platform (ABSENT — greenfield)** | auditing-mcp (exists; FR-11 augments) | **AUDIT-ONLY — to be completed by this feature** (C-0458, grep-verified, [codebase-analysis-report.md](codebase-analysis-report.md)) |

### What design must mirror

- Two reference files exactly in `KB-mcp-design/references/`: `patterns-and-anti-patterns.md`, `principles.md`. No assets/.
- `KB-mcp-platform/` carries topic-specific references (transports, install paths, redaction, lifecycle hooks, etc.) plus `assets/templates/` containing the .mcp.json template (one of the family-coordinator-question outputs — see D-0010 human decision point).
- Skill naming: `kb-mcp-design`, `kb-mcp-platform` (lowercase-hyphenated, ADR-0020). `auditing-mcp` retains current bare-topic name (no `-configs` suffix needed — that's the documented deviation).
- Sister-cross-reference: KB-mcp-design and KB-mcp-platform must name each other in their descriptions, AND auditing-mcp's existing description must be updated to name both new sister halves (currently broken because the halves don't exist).
- Family-coordinator: **unresolved human decision** (see D-0010). Two paths: (a) graduate auditing-mcp to its own family with KB-mcp-* as sisters; (b) keep auditing-mcp in auditing-cc-configs family with KB-mcp-* as sibling knowledge skills with explicit cross-refs.

---

## 7. Risks and Open Questions

### Medium-confidence / single-sourced findings (5 surfaced by Critic)

| Finding | Verdict | Source | Mitigation |
|---|---|---|---|
| C-0266 — Exa query-param-precedence-over-header (DeepWiki only source) | single_sourced / medium | [T-006-exa.md](research-notes/T-006-exa.md) F4 | Recommendation (header-only) sidesteps the fragility. |
| C-0295/C-0296 — Fast.io ping interval/timeout/failure-threshold (single-vendor pattern guide) | verified / medium | [T-007-mcp-operational.md](research-notes/T-007-mcp-operational.md) F1.2 | Numbers are reference, not contract. Design should not hard-code Fast.io values. |
| C-0330 — Velida at-source-redaction pattern (personal blog single-vendor) | verified / medium | [T-007-mcp-operational.md](research-notes/T-007-mcp-operational.md) F4.2 | Principle multi-source-corroborated by OWASP MCP01; implementation example is single-source. |
| C-0388/C-0411 — GitNexus skip-grammars env-var (Mintlify mirror; HTTP 410 from primary) | partially_verified / medium | [T-008-gitnexus.md](research-notes/T-008-gitnexus.md) F5 | **Smoke-test required at install** — assert env var works on pinned tag. |
| C-0484/C-0485 — file-count figures (634 total / 468 markdown / 73.8%) | single_sourced / medium | [codebase-analysis-report.md](codebase-analysis-report.md) | Recount via `find` / `wc` is cheap if becomes load-bearing in design. |

### Time-sensitive verification at execution

- **C-0133** — actionlint-mcp "no releases" attested for snapshot 2026-05-23. Maintainer may publish at any time; re-verify before pinning commit SHA.
- **C-0158** — Terraform MCP 0.5.2 current stable at 2026-04-28; confirm latest at execution.
- **C-0073** — mcp-openapi-schema 0.0.1 static ~14 months; abandonment-vs-stable ambiguity preserved (do not flatten in design narrative).

### Cross-cutting risks that may warrant ADRs (for design-composer to author per FR-5)

1. **UI-15 primary-to-fallback transition surfacing (D-0005).** Reversibility=ONE-WAY, blast-radius=tenant, Wardley=genesis, C-0349 NO-CONSENSUS. The .jsonl event-shape is a first-time convention that future MCP additions will inherit. **Recommended for ADR.**
2. **ADR-0018 bump to v1.1.0 (D-0012).** The drift itself is the ADR; this is straightforward ADR work.
3. **Credential redaction posture (D-0007).** Reversibility=ONE-WAY, blast-radius=org, OWASP MCP01 ranking. The redaction-list-equals-env-vars invariant proposed at the per-layer level deserves ADR-level codification. **Recommended for ADR.**
4. **Serena posture (D-0013, UI-8).** Reversibility=two-way but coupling to D-0009 agent allowlist amplifies rework cost if narrowing decision changes. **Recommended for ADR** (the narrowing decision itself).
5. **Install-mechanism strategy (D-0001).** Reversibility=two-way at the hook layer but the "no project Dockerfile changes; postCreate is the single touchpoint" posture is a load-bearing repo-discipline decision. **Recommended for ADR** if design-composer judges it crosses the ADR threshold.

### Human decision point surfaced from substrate-map

**D-0010: auditing-mcp family-coordinator resolution.** Two paths exist; the synthesizer does NOT select between them. The user (or design-composer) must decide:
- Path A: graduate auditing-mcp to its own family with KB-mcp-platform + KB-mcp-design as sister halves.
- Path B: keep auditing-mcp in auditing-cc-configs family (current state per C-0460) with KB-mcp-platform + KB-mcp-design as sibling knowledge skills with explicit cross-refs.

The rest of D-0010 (template-following, ADR-0020 naming, ADR-0030 pedagogical sections, sister-cross-reference) is unblocked by either path.

---

## 8. Constraint Propagation Brief

The constraints the per-layer designers MUST honor. Sourced from `04-decision-frames.json` risks, [codebase-analysis-report.md](codebase-analysis-report.md), and the substrate-map `substrate_context` block.

| # | Constraint | Source | How design must honor |
|---|---|---|---|
| 1 | **Base image:** `mcr.microsoft.com/devcontainers/python:1-3.11-bookworm`. Ships python 3.11, git, github-cli (feature). Absent: Node, Go, DinD. | [codebase-analysis-report.md](codebase-analysis-report.md); substrate-map.substrate_context | Add runtimes via devcontainer features (D-0003). No project Dockerfile bake (D-0001). |
| 2 | **No Go in base image.** actionlint-mcp requires Go toolchain. | [T-003-actionlint-mcp.md](research-notes/T-003-actionlint-mcp.md) C-0125/C-0134 | Add `ghcr.io/devcontainers/features/go` feature OR fetch pre-built binary (no releases exist — C-0133 — so go install via feature is the only deterministic path). |
| 3 | **No Docker-in-Docker.** | substrate-map.substrate_context.runtimes_absent | Terraform MCP must use pre-built binary path, not Docker (C-0193 explicit). |
| 4 | **Node not yet in base image** — will be added by this feature. | [T-002-mcp-openapi-schema.md](research-notes/T-002-mcp-openapi-schema.md) C-0064; substrate-map | Add `ghcr.io/devcontainers/features/node:1` with explicit LTS pin (D-0003). Required before postCreate runs npx/uvx invocations. |
| 5 | **No mcp__ namespace usage in current 36 agents** — grep-verified zero hits. | [codebase-analysis-report.md](codebase-analysis-report.md) C-0445 | This feature introduces the pattern. Design-cc must add entries narrowly per-agent (D-0009); preserve "no mcp__ entries" state for non-consumer agents. |
| 6 | **ADR-0018 schema-version drift** (v1.0.0 in ADR vs v1.1.0 in KB/agent) | [codebase-analysis-report.md](codebase-analysis-report.md) C-0441/C-0495 | D-0012 bump ADR-0018 to v1.1.0; update two downstream consumers (discovery-codebase-researcher, review-architecture-auditor). |
| 7 | **ADR-0007 location surprise** — lives in `adrs-migrated/`, not `adrs/`. 5 variants; current v2.2.0 Accepted. | [codebase-analysis-report.md](codebase-analysis-report.md) C-0442/C-0497 | Adjacent D-0012 fix: relocate or cross-reference (low severity per C-0498). |
| 8 | **73.8% markdown corpus.** Symbol density in 52 Python audit scripts only. | [codebase-analysis-report.md](codebase-analysis-report.md) C-0485/C-0490 | D-0013: Serena always-on must be narrowed to Python-touching agents. |
| 9 | **Codespaces secrets surface.** EXA_API_KEY, CONTEXT7_API_KEY, TFE_TOKEN are Codespaces secrets. | [T-005-context7.md](research-notes/T-005-context7.md), [T-006-exa.md](research-notes/T-006-exa.md), [T-004-terraform-mcp.md](research-notes/T-004-terraform-mcp.md); substrate-map.substrate_context.secrets_surface | Design-codespaces must wire secrets through devcontainer.json `containerEnv` or `secrets`; .mcp.json reads them by env-var name. |
| 10 | **OWASP MCP01 Token Mismanagement** ranked highest MCP risk. | [T-007-mcp-operational.md](research-notes/T-007-mcp-operational.md) C-0333/C-0335 | D-0007 redaction at log-surface; D-0007 reject Exa exaApiKey URL-form at config validation; secret-via-env-only invocation (no `--api-key` argv flag — Context7 C-0205 note). |
| 11 | **Stdio servers not auto-reconnected by Claude Code.** | [T-007-mcp-operational.md](research-notes/T-007-mcp-operational.md) C-0301 verbatim Anthropic | 6 of 7 servers fail open to operator recovery. FR-9 structured-failure-record contract is load-bearing (D-0005 .jsonl). |
| 12 | **Three trifecta convention precedents.** | [codebase-analysis-report.md](codebase-analysis-report.md) Batch 5 | D-0010: follow KB-cc-platform + KB-cc-design template verbatim; mirror structural skeleton (Pattern Archaeology §6 table). |
| 13 | **Existing E-0081 Dockerfile-Yarn-key failure history.** | [codebase-analysis-report.md](codebase-analysis-report.md) | D-0001: avoid Dockerfile-bake posture; D-0003: avoid NodeSource apt path. |
| 14 | **C-0444 universal-frontmatter calibration:** medium-confidence that all 36 agents have identical frontmatter fields. | [codebase-analysis-report.md](codebase-analysis-report.md) C-0444 | Design-cc must validate per-agent frontmatter shape before adding `mcp__` tools entries; do not assume universal field presence. |

**Constraint-propagation invariant check.** Every constraint in this table is referenced explicitly in at least one §9 per-layer recommendation. (Constraint 1 → design-codespaces base-image work; 2 → design-codespaces Go feature; 3 → design-codespaces no-DinD enforcement; 4 → design-codespaces Node feature; 5 → design-cc allowlist work; 6/7 → design-composer ADR work; 8/13 → design-cc Serena narrowing; 9 → design-codespaces Codespaces-secret wiring; 10 → design-cc redaction allowlist + design-composer ADR; 11 → design-cc mcp-events.jsonl contract; 12 → design-cc KB authoring; 14 → design-cc per-agent frontmatter validation.)

---

## 9. Recommendations to Per-Layer Designers

The per-layer designers in Stage 6 will receive this synthesis as input. This section is the explicit handoff.

### 9.1 design-cc (Claude Code / Project Filesystem)

The Claude Code / project-filesystem layer owns: the `.mcp.json` declarative config, the 36 agent allowlist updates, the new KB-mcp-platform + KB-mcp-design skills, the auditing-mcp augmentation, and the mcp-events.jsonl contract.

**Headline recommendation.** Author `.mcp.json` with seven server entries (six stdio + Context7/Exa remote HTTP), an explicit `env:` block declaring the three credential env vars (CONTEXT7_API_KEY, EXA_API_KEY, TFE_TOKEN — the SSOT for redaction allowlist), per-agent allowlist edits to 7 agent files (no broad wildcard; preserve zero-mcp__ state for the other 29), and KB-mcp-platform + KB-mcp-design skills following KB-cc-platform template verbatim.

**Specific work items:**

1. **`.mcp.json` schema.** Project-scoped at repo root. Seven server entries:
   - Stdio entries for Serena (uvx), mcp-openapi-schema (npx), actionlint-mcp (binary on PATH), Terraform MCP (binary on PATH), GitNexus (uvx/npx with `GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1`).
   - HTTP entries for Context7 (`https://mcp.context7.com/mcp` with `CONTEXT7_API_KEY` header) and Exa (`https://mcp.exa.ai/mcp` with `x-api-key: ${EXA_API_KEY}` header).
   - `env:` block enumerates CONTEXT7_API_KEY, EXA_API_KEY, TFE_TOKEN by name (D-0007 SSOT for redaction).
   - Reject Exa's exaApiKey URL-query-param form at config validation (D-0007, E-0095).
   - Honors constraint #1, #5, #9, #10.
2. **Agent allowlist updates.** Edit 7 of 36 agents (preserve zero-mcp__ state for the other 29):
   - design-api → `mcp__mcp-openapi-schema__*`
   - design-cicd → `mcp__actionlint-mcp__lint_workflow`, `mcp__actionlint-mcp__check_all_workflows`
   - design-iac → `mcp__terraform-mcp__*`
   - discovery-external-researcher → 5 explicit Context7+Exa tool ids (D-0009 mapping table)
   - discovery-codebase-researcher → `mcp__gitnexus__*`, `mcp__codebase-memory-mcp__*`
   - review-architecture-auditor → `mcp__gitnexus__*`, `mcp__codebase-memory-mcp__*`
   - (~6 Python-touching agents) → `mcp__serena__*` per D-0013 narrowing
   - Validate each agent's frontmatter shape before editing (constraint #14).
3. **KB-mcp-platform authoring.** Follow KB-cc-platform template: ADR-0020 frontmatter, ADR-0030 pedagogical_sections, sister-cross-reference convention. Topic references: `transports.md`, `install-mechanisms.md`, `auth-and-redaction.md`, `lifecycle-hooks.md`, `version-pinning.md`, `mcp-events-jsonl.md`. `assets/templates/.mcp.json.example` (the canonical template). Honors constraint #12.
4. **KB-mcp-design authoring.** Two references exactly: `patterns-and-anti-patterns.md` (argv-leakage, URL-embedded-credentials, broad-allowlist, ToolHive-proxy-supervisor, single-poststart-conflation) + `principles.md` (redact-at-source, ping-canonical, stdio-not-reconnected, postCreate-install-postStart-probe, .jsonl-is-coarse-events). No assets/. Honors constraint #12.
5. **auditing-mcp augmentation.** Add audit rules covering the new surface (mcp__ allowlist least-privilege; .mcp.json schema validation including env-var SSOT; redaction-list-equals-env-vars invariant; primary/fallback declaration completeness). Update sister-cross-reference to name new KB-mcp-* halves. Family-coordinator placement awaits human decision (D-0010 path A or B).
6. **mcp-events.jsonl contract.** File at `.claude/runtime/mcp-events.jsonl`. JSONL schema (one record per line):
   - Common fields: `ts` (ISO 8601), `event` (one of `primary_degraded`, `readiness_probe`, `structured_failure`), `server`, `agent` (optional), `extraction_method` (optional — for primary_degraded, distinguishes which detection path triggered).
   - `primary_degraded` extra fields: `primary_server`, `fallback_server`, `reason`.
   - `readiness_probe` extra fields: `probe_method` (ping/auth-probe), `latency_ms`, `result`.
   - `structured_failure` extra fields: `failure_class`, `message_redacted`.
   - Schema lives in KB-mcp-design `principles.md`. Honors constraint #11.

### 9.2 design-codespaces (Dev Environment)

The Codespaces / devcontainer layer owns: Dockerfile/devcontainer.json changes, base-image features (Node, Go, github-cli), lifecycle hooks (postCreate / postStart), prebuild contents, and Codespaces secrets wiring.

**Headline recommendation.** No new project Dockerfile work. Add three devcontainer features (Node, Go, github-cli already present), implement two lifecycle-hook scripts (`postCreateCommand` install + verify, `postStartCommand` readiness probe writing to mcp-events.jsonl), wire three Codespaces secrets through `containerEnv`. Per-server install commands are documented; smoke-test GitNexus skip-grammars at install time.

**Specific work items:**

1. **devcontainer.json features block.**
   - `ghcr.io/devcontainers/features/node:1` with explicit Node 20 LTS major pin (D-0003).
   - `ghcr.io/devcontainers/features/go:1` (for actionlint-mcp `go install`).
   - github-cli feature (already present — preserve).
   - Honors constraint #2, #4.
2. **postCreateCommand script (`.devcontainer/postCreate.sh` or similar).** Idempotent. Executes seven install commands (D-0001 hybrid):
   - `pip install uv` (or astral.sh installer) if `uv` is not on PATH — C-0005 verified-medium; smoke-test via `which uv`.
   - Serena: `uvx --from git+https://github.com/oraios/serena@<pinned-pre-v1.3.0-tag> serena start-mcp-server` registration (not actually start — the install side).
   - mcp-openapi-schema: `npx -y mcp-openapi-schema@0.0.1` cache warm.
   - actionlint-mcp: `go install github.com/2manymws/actionlint-mcp/cmd/actionlint-mcp@<pinned-commit-sha>`.
   - Terraform MCP: `wget` pre-built binary → `sha256sum -c SHA256SUMS` → GPG verify (HashiCorp public key) → place on PATH (C-0157/C-0190).
   - Context7: no install (remote HTTP).
   - Exa: no install (remote HTTP).
   - GitNexus: `GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1 uvx/npx <pinned-tag>` — **explicit smoke-test required**, fail postCreate if smoke-test fails (C-0388/C-0411 partially_verified-medium).
   - Followed by initial install-verification ping for all 7 servers.
   - Honors constraint #1, #2, #3, #4, #13.
3. **postStartCommand script (`.devcontainer/postStart.sh` or similar).** Fast readiness probe. For each of 7 servers:
   - JSON-RPC ping (D-0008).
   - For Context7 and Exa, optional authenticated probe gated on env flag (D-0008).
   - Append result to `.claude/runtime/mcp-events.jsonl` as a `readiness_probe` event (D-0005/D-0006).
   - Non-fatal on transient failures (per D-0004 risk note); a stderr banner mentions the count of degraded servers.
   - Total time budget ~2s (7 pings + 2 optional probes).
4. **Codespaces secrets wiring.** `containerEnv` block in devcontainer.json maps the three Codespaces secrets to env vars: CONTEXT7_API_KEY, EXA_API_KEY, TFE_TOKEN. .mcp.json reads them by name (D-0007 SSOT). Honors constraint #9.
5. **Prebuild contents (if Codespaces prebuilds are in scope).** Cache the `go install` toolchain, `uvx` cache for Serena, `npm` cache for mcp-openapi-schema. Honors constraint #1 (image-layer is built once; postCreate stays fast).
6. **What design-codespaces does NOT do.** No project Dockerfile changes beyond what already exists (D-0001). No Docker-in-Docker (constraint #3). No `nvm` shim (D-0003 rejected nvm option). No NodeSource apt (D-0003 rejected apt option; constraint #13 history).

### 9.3 design-composer (cross-layer reconciliation + ADR authorship)

The composer layer owns cross-layer reconciliation. Per FR-5 of recipe-feature-pipeline, **design-composer is the sole author of ADRs** in this pipeline run.

**Headline recommendation.** Author up to five ADRs from this synthesis (UI-15 transition surfacing; ADR-0018 v1.1.0 bump; credential redaction posture; Serena UI-8 narrowing; install-mechanism strategy if judged ADR-worthy). Reconcile the design-cc and design-codespaces handoffs: the postStart probe (codespaces) writes to mcp-events.jsonl (cc-owned contract); the .mcp.json env: block (cc-owned) is the redaction SSOT consumed at the log-surface boundary (whose code-location is a composer call). Resolve the D-0010 family-coordinator question with the user.

**Specific work items:**

1. **ADR candidates** (composer judges threshold; recommended list from §7):
   - **ADR — UI-15 primary-to-fallback transition surfacing** (D-0005, one-way, novel-design from F5.4 NO CONSENSUS). The .jsonl event-shape is the load-bearing contract.
   - **ADR-0018 bump to v1.1.0** (D-0012, drift remediation).
   - **ADR — Credential redaction posture** (D-0007, one-way, OWASP MCP01 top-rank). Redaction-list-equals-env-vars invariant.
   - **ADR — Serena UI-8 narrowing posture** (D-0013, two-way but coupled to D-0009).
   - **ADR — Install-mechanism strategy** (D-0001, judged by composer; the "no Dockerfile changes; postCreate is the single touchpoint" posture).
2. **Cross-layer reconciliation.**
   - **mcp-events.jsonl contract owner.** design-cc defines schema in KB-mcp-design; design-codespaces postStart writes to it. Composer ensures the schema and the writer agree.
   - **Redaction allowlist code-site.** The .mcp.json env: block is the SSOT (cc-owned). The log-surface boundary that consumes it is a composer decision: is it a wrapper script in design-codespaces' postStart? An in-process filter in the host? Surface this as a sub-decision and pick a code-site that composes with constraint #11 (stdio not auto-reconnected; failures emerge via stderr capture).
   - **mcp__ tool-id breakage.** Context7 v1.2.0 ReplaceContentTool replaces ReplaceRegexTool (D-0011 C-0037). The pinned Context7 version (or vendor-endpoint API version header) and the tool ids in the discovery-external-researcher allowlist must agree. Composer enforces.
3. **Human decision points to surface to user.**
   - **D-0010 family-coordinator** (path A: auditing-mcp graduates; path B: stays in auditing-cc-configs family with KB-mcp-* as siblings). Required before D-0010 authoring can proceed.
4. **Verification at execution time.** Composer's review-architecture-auditor pass should explicitly verify:
   - `which uv` returns a valid path after postCreate (C-0005).
   - actionlint-mcp releases-page check (C-0133 time-sensitive).
   - GitNexus skip-grammars smoke-test passed (C-0388/C-0411).
   - Exa CLI `--header` support confirmed or .mcp.json fallback path taken (OQ-T006-1).
   - C-0444 universal-frontmatter (medium-confidence) holds across all 36 agents after design-cc edits.
   - `mcp__` allowlist entries match consumer-claim mapping table; no broad wildcards; no entries on non-consumer agents.
5. **What design-composer does NOT do.** Does not write new Dockerfile RUN layers (D-0001 hybrid posture). Does not introduce a ToolHive-style proxy (D-0006 rejected). Does not introduce a long-running active ping-loop supervisor (D-0008 rejected). Does not introduce agent-level acknowledgement convention for UI-15 (D-0005 rejected for uniformity risk across 36 agents).

---

## 10. Limitations

This section follows the report-composition-knowledge skill's transparency discipline.

- **Five medium-confidence findings** are enumerated in §7 (C-0266 Exa precedence; C-0295/C-0296 Fast.io values; C-0330 Velida pattern; C-0388/C-0411 GitNexus skip-grammars; C-0484/C-0485 file-counts).
- **No claim has verdict `unverifiable` and no `dissent_evidence` populated** across the 98-critique corpus. C=0, D=0.
- **Zero decision frames have `recommended_option: null`.** All 13 frames carry a recommended option; the only unresolved sub-question is D-0010's family-coordinator path (surfaced as a human decision point, not as null).
- **Single-sourced taxonomies acceptable by definition:** C-0333 (OWASP MCP01 ranking — OWASP IS the authority for the taxonomy).
- **Time-sensitive verifications:** C-0133 (actionlint-mcp releases), C-0158 (Terraform MCP version-current), C-0073 (mcp-openapi-schema staleness). Carry forward as "verify at execution time" notes to the per-layer designers.

---

## 11. Sources

| # | Source file | Source type | Claim count | Verification headline |
|---|---|---|---|---|
| 1 | [T-001-serena.md](research-notes/T-001-serena.md) | community blog + vendor README | 57 | verified-high (canonical uvx install) |
| 2 | [T-002-mcp-openapi-schema.md](research-notes/T-002-mcp-openapi-schema.md) | vendor + source-code anchored | 67 | verified-high (StdioServerTransport quoted from index.mjs) |
| 3 | [T-003-actionlint-mcp.md](research-notes/T-003-actionlint-mcp.md) | source-code + GH releases | 32 | verified-high incl. time-sensitive 'no releases' (C-0133) |
| 4 | [T-004-terraform-mcp.md](research-notes/T-004-terraform-mcp.md) | HashiCorp vendor docs | 45 | verified-high (releases.hashicorp.com SHA256SUMS + GPG) |
| 5 | [T-005-context7.md](research-notes/T-005-context7.md) | Upstash vendor docs + GitHub | 50 | verified-high (mcp.context7.com/mcp + shared API key) |
| 6 | [T-006-exa.md](research-notes/T-006-exa.md) | docs.exa.ai + GitHub + DeepWiki | 38 | verified-high primary; C-0266 single-sourced precedence flagged |
| 7 | [T-007-mcp-operational.md](research-notes/T-007-mcp-operational.md) | Anthropic spec + OWASP + Fast.io + vendor blogs | 87 | verified-high primary + 4 medium; F5.4 NO CONSENSUS survives scrutiny |
| 8 | [T-008-gitnexus.md](research-notes/T-008-gitnexus.md) | Mintlify-mirrored upstream | 53 | partially_verified-medium for skip-grammars (smoke-test required) |
| 9 | [codebase-analysis-report.md](codebase-analysis-report.md) | direct repo inspection (grep-verified) | 116 | verified-high primary; two single-sourced file-counts |

---

## Provenance

- Synthesis run: devcontainer-mcp-provisioning-r1
- Decision frames: `synthesis/04-decision-frames.json` (13 frames)
- Substrate map: `synthesis/05-substrate-map.json` (implementation-strategy mode; option counts 1-4 with rationale)
- Critique log: `synthesis/03-critique.json` (98 critiques, 5 batches)
- Verification audit trail: `synthesis/03-verifications.md`
- Entity graph: `synthesis/02-graph.json` (111 entities, 117 edges, 7 hand-curated communities)
- Claims corpus: `synthesis/01-claims.json` (545 merged claims, 9 sources)
- PRD: `prd-v3.md` (11 FRs, 35 ACs)
- Research plan: `research-plan-v3.md`
- Pipeline recipe: `recipe-feature-pipeline` (single-synthesis.md variant, no per-decision ADRs at this stage; ADR authorship deferred to design-composer per FR-5)
