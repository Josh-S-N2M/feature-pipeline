---
id: ADR-0007
version: 2.1.0
status: Accepted
generated: 2026-05-12
generated_by: synth-designer (retroactive template migration per ADR-0014)
supersedes:
  - {id: ADR-0007, version: 1.0.0}
  - {id: ADR-0007, version: 2.0.0}
adrs_inherited:
  - ADR-0001 (orchestrator placement)
  - ADR-0005 (append-only supersession)
applies_to:
  - feature-pipeline
template_format: per ADR.txt v1.0
---

# ADR-0007 (v2.1, template-migrated): Code-graph MCP selection — GitNexus primary, codebase-memory-mcp fallback

## Status

Accepted — 2026-05-12 (template-migrated from v2.0.0 of the same date).

Supersedes ADR-0007 v1.x and v2.0.0. v1.x is preserved as historical reference. The substantive decision is unchanged from v2.0.0; only the structure is migrated.

## Context

Blueprint v2 ADR-0001 commits the pipeline to using a code-graph MCP for blast-radius analysis in Critique-1 and codebase research in Stage 3. The choice between candidates determines: (a) operational rigor of blast-radius analysis (the multi-turn requirement), (b) setup friction for users adopting the pipeline, (c) maintenance cost as the MCP ecosystem evolves, (d) coverage across the user's actual programming language stack.

ADR-0007 v1 selected codebase-memory-mcp as primary on grounds that included a constraint not in the manifest: commercial-use license compatibility. The user explicitly clarified that commercial-use is not a hard constraint for this pipeline. Removing that filter changes the comparison.

The original argument for codebase-memory-mcp — its hop-based risk tier output mapping 1:1 to "multi-turn blast radius" — remains valid. But it loses to GitNexus on three other dimensions when license is not a filter: ecosystem maturity, Claude Code integration depth, and platform-level features (skills auto-install, Code Wiki, PreToolUse hooks).

## Decision

**Primary: GitNexus** (`abhigyanpatwari/GitNexus`)

**Fallback (configured concurrently, used when GitNexus fails for the user's stack): codebase-memory-mcp** (`DeusData/codebase-memory-mcp`)

**Explicitly rejected as primary:**
- code-review-graph — strong feature set but smaller ecosystem and no Claude Code integration depth.
- locus — narrower bundled-LSP coverage; setup friction per additional language.
- CodeGraphContext — regex fallback for non-Python languages is an accuracy hazard.
- syms — file-level only, no call graph; cannot serve the blast-radius requirement.

## Decision Details

| Item | Content |
|---|---|
| Decision | GitNexus primary; codebase-memory-mcp fallback (configured concurrently). Both available; runtime routing per language coverage detection. |
| Why now | License filter was clarified by user; re-evaluation surfaces GitNexus as superior on the corrected constraint set. Locking in primary/fallback before critique-1-knowledge skill content authoring is finalized. |
| Why this | GitNexus ecosystem maturity (28.9K stars vs 1.8K); Claude Code integration depth (only candidate with PreToolUse hook support); auto-installs agent skills reducing setup burden; Code Wiki provides architectural surface. codebase-memory-mcp's wider language coverage (155 langs) and hop-tier risk output covers the fallback case. |
| Known unknowns | Whether GitNexus's TS-first language focus produces meaningfully worse structural data for non-TS stacks; whether the two-MCP configuration crosses the 20-tool threshold (claim C-R2-0010) and degrades selection accuracy; whether GitNexus's PolyForm Noncommercial licensing is acceptable for the user's commercial-use intent. |
| Kill criteria | If GitNexus becomes unmaintained (no commits for 6+ months) OR PolyForm licensing changes block the user's commercial use AND the user clarifies commercial-use is now a hard filter, supersede with v3 reverting to codebase-memory-mcp as primary. |

## Rationale

Four factors are decisive when license is not a filter:

(1) **Ecosystem maturity.** 28.9K stars vs codebase-memory-mcp's 1.8K. 767 commits, 3.3K forks. Sustained development with commercial backing (akonlabs.com). The maturity gap matters for a pipeline that depends critically on the MCP's correctness — bugs in younger projects are more frequent and longer-lived.

(2) **Deepest Claude Code integration of any candidate.** Per the GitNexus MCP docs (chatforest review April 25 2026): full support for MCP + skills + PreToolUse hooks. No other candidate supports PreToolUse hooks. Auto-augment hooks can inject blast-radius context before any tool that modifies code, without explicit agent invocation.

(3) **Auto-installs agent skills.** `gitnexus analyze` indexes the repo AND installs agent skills that teach Claude Code how to use the tools. Reduces pipeline setup-instruction burden materially.

(4) **Code Wiki + auto-doc.** GitNexus generates an auto-updating Code Wiki of the repository's architecture. synth-designer (and per ADR-0016, the per-layer designers + composer) can read this Wiki via MCP resources before drafting the blueprint.

The fallback (codebase-memory-mcp) is positioned for two specific cases: (a) when GitNexus's TS-first coverage is thin for the user's stack, (b) when explicit hop-tier risk output is needed and computing it on GitNexus's primitives is too costly.

## Options Considered

**Option 1: Use codebase-memory-mcp as sole primary (ADR-0007 v1 position).**
- Pros: hop-tier semantic match; 155-language coverage; MIT licensed.
- Cons: rejected on user feedback that license-blocking GitNexus is not appropriate.

**Option 2: Use GitNexus alone, drop the fallback.**
- Pros: simpler configuration.
- Cons: rejected because GitNexus's TS-first language focus leaves coverage gaps; the fallback's language-coverage backstop is worth the setup cost.

**Option 3: Build a thin MCP proxy that fronts both with a uniform interface.**
- Pros: clean abstraction; one tool surface for downstream agents.
- Cons: rejected — violates manifest's no-new-runtime-infrastructure constraint.

**Option 4: Use Cypher queries directly via GitNexus, ignoring codebase-memory-mcp entirely.**
- Pros: single MCP; simpler tool catalog.
- Cons: pipeline must teach the Cypher pattern; loses language-coverage backstop.

**Option 5 (Selected): GitNexus primary + codebase-memory-mcp fallback, both configured concurrently with runtime routing.**
- Pros: maturity + integration depth from GitNexus; language coverage from codebase-memory-mcp; graceful degradation.
- Cons: 30 code-graph tools total (16 + 14) crosses the ~20-tool threshold (claim C-R2-0010); setup friction higher than single-MCP.

## Consequences

### Positive Consequences

- Pipeline benefits from the most mature code-graph MCP ecosystem in the space (28.9K stars vs 13K nearest competitor).
- PreToolUse hooks enable an ambient-intelligence pattern no other candidate supports.
- Auto-installed GitNexus skills reduce pipeline setup-instruction burden.
- Code Wiki provides an architectural-documentation surface synth-designer-composer can consume without additional infrastructure.
- 155-language fallback via codebase-memory-mcp covers stacks where GitNexus's TS-first focus is thin.
- Both MCPs run locally; no network egress required for code-graph queries.

### Negative Consequences

- **License: GitNexus uses PolyForm Noncommercial.** For users intending commercial use of the pipeline, this requires either (a) the GitNexus enterprise tier from akonlabs.com or (b) avoiding GitNexus and using codebase-memory-mcp as primary. The pipeline should document this clearly in setup guides. Users in research, education, personal projects, and open-source contexts have no license burden.
- The pipeline must own the risk-tier mapping on top of GitNexus's primitives, rather than consuming a named tier output. This is critique-1-knowledge (post-rename architecture-audit-knowledge) content that needs to be written and maintained.
- Two MCPs configured concurrently doubles the MCP-related context overhead (per claim C-R2-0010). GitNexus (16 tools) + codebase-memory-mcp (14 tools) = 30 code-graph tools, crossing the ~20-tool threshold. Mitigation: knowledge skill explicitly routes to GitNexus by default; codebase-memory-mcp tools only in fallback section.
- Setup friction higher than single-MCP.

### Neutral Consequences

- The code-graph MCP space is fast-moving. This ADR should be revisited in ~6 months when both projects have additional release history.
- If GitNexus discontinues PolyForm and switches to MIT-equivalent licensing, the commercial-use concern evaporates and the recommendation gets stronger.

## Architecture Impact

**Components that change:**
- `.mcp.json` configures both MCPs concurrently.
- Stage 0 preflight: detects MCP configuration and tests responsiveness.
- critique-1-knowledge (renamed architecture-audit-knowledge per ADR-0017): routes to GitNexus by default; documents fallback path to codebase-memory-mcp.
- synth-codebase-researcher (Stage 3): uses GitNexus's Code Wiki + Cypher queries for structural codebase analysis; falls through to codebase-memory-mcp's search_graph / get_architecture when GitNexus thin.

**New dependencies introduced:**
- Pipeline depends on GitNexus availability for primary path.
- Pipeline depends on codebase-memory-mcp availability for fallback path.
- Both MCPs must be installable by the user; setup documentation specifies install procedure.

**Architectural constraints added:**
- Both MCPs MUST be configured in `.mcp.json` (or one with documented degraded-mode behavior).
- Stage 0 preflight MUST test both MCPs' responsiveness and detect which is primary for this run.
- Knowledge skills MUST explicitly route to GitNexus by default; codebase-memory-mcp only in fallback section.

**Architectural constraints removed:**
- The v1.0.0 reasoning that filtered candidates on license is no longer applied.

## Implementation Guidance

### Stage 0 preflight configuration check

```
1. Is GitNexus MCP configured AND responding? → primary path.
2. If GitNexus configured but degraded for detected language → primary still GitNexus, supplement with codebase-memory-mcp for risk-tier analysis.
3. If GitNexus unavailable → primary becomes codebase-memory-mcp.
4. If neither → degraded mode per blueprint v2 §3.8 (native Grep/Glob + meta_warning).
```

Detection of "GitNexus is degraded for this language" is heuristic — if `analyze_impact` returns fewer than 3 affected symbols on a change set that touched non-trivial code, and codebase-memory-mcp's `detect_changes` on the same input returns more, the pipeline marks GitNexus as degraded-for-this-run and routes blast-radius queries to the fallback.

### Risk-tier mapping on GitNexus

Since GitNexus does not natively output hop-based risk tiers but the pipeline depends on them, architecture-audit-knowledge specifies the mapping:

```
For each changed symbol:
  hop 1 callers/callees → mark CRITICAL
  hop 2 reachable symbols → mark HIGH
  hop 3 reachable symbols → mark MEDIUM
  hop 4+ reachable symbols → mark LOW
```

## Related Information

- Pre-migration version: `ADR-0007-code-graph-mcp-selection-v2-pre-template-migration.md` (v2.0.0 content).
- v1.1.0 (template-migrated v1, superseded): `ADR-0007-code-graph-mcp-selection-v1-superseded.md`.
- ADR-0001: orchestrator placement.
- ADR-0005: append-only supersession (governs this ADR's own version chain).
- ADR-0014: retroactive template migration producing this v2.1.0.
- ADR-0017: rename of critique-1-knowledge to architecture-audit-knowledge (the consumer of the risk-tier mapping above).
- Claims: C-R2-0019 through C-R2-0022.
