---
id: ADR-0007
version: 2.0.0
status: Accepted
generated: 2026-05-12
generated_by: synth-reconcile (post-user-review of ADR-0007 v1.0.0)
supersedes:
  - {id: ADR-0007, version: 1.0.0}
adrs_inherited:
  - ADR-0001 (orchestrator placement)
  - ADR-0005 (append-only supersession)
---

# ADR-0007 (v2): Code-graph MCP selection — GitNexus as primary, codebase-memory-mcp as fallback

## Status
Accepted — 2026-05-12, supersedes ADR-0007 v1.0.0

## Why this supersedes v1

ADR-0007 v1 selected codebase-memory-mcp as primary on grounds that included a constraint not in the manifest: commercial-use license compatibility. The user explicitly clarified that commercial-use is not a hard constraint for this pipeline. Removing that filter changes the comparison.

The original argument for codebase-memory-mcp — its hop-based risk tier output mapping 1:1 to "multi-turn blast radius" — remains valid. But it loses to GitNexus on three other dimensions when license is not a filter: ecosystem maturity, Claude Code integration depth, and platform-level features (skills auto-install, Code Wiki, PreToolUse hooks).

ADR-0007 v1 is now Superseded. Its rationale chain is preserved in the file; downstream artifacts referencing v1 retain those references but should adopt v2's recommendations going forward.

## Context

Blueprint v2 ADR-0001 commits the pipeline to using a code-graph MCP for blast-radius analysis in Critique-1 and codebase research in Stage 3. The choice between candidates determines:
- Operational rigor of blast-radius analysis (the multi-turn requirement)
- Setup friction for users adopting the pipeline
- Maintenance cost as the MCP ecosystem evolves
- Coverage across the user's actual programming language stack

Six MCP candidates were evaluated. Three are competitive for primary; three are not.

## Candidates evaluated (license-neutral)

| Server | Stars | Tools | Language coverage | Blast-radius primitive | Claude Code integration |
|---|---|---|---|---|---|
| **GitNexus** | 28.9K | 16 | TS-first + tree-sitter multi-language | `analyze_impact` + 7 Cypher resources + 2 prompt workflows (impact analysis, architecture mapping) | **Full: MCP + skills + PreToolUse hooks** (the only candidate with hook support) |
| **codebase-memory-mcp** | 1.8K | 14 | 155 languages via tree-sitter | `detect_changes` with explicit CRITICAL/HIGH/MEDIUM/LOW risk tiers | MCP only |
| **code-review-graph** | 13K | 28 | 21 languages | blast radius + community detection + execution flow | MCP only |
| locus | small | ~5 namespaced | 5 bundled LSP + manual install | `analysis impact` action | MCP only |
| CodeGraphContext | ~3K | 14 | 66 languages | `get_change_impact` (Python AST primary; regex for others) | MCP only |
| syms / symbols | small | 7 | 14 languages | `syms_impact` file-level only — no call graph | MCP only |

Sources: claims C-R2-0019 through C-R2-0022; ChatForest April 25 2026 comparison; vendor docs for each.

## Decision

**Primary: GitNexus** (`abhigyanpatwari/GitNexus`)

**Fallback (configured concurrently, used when GitNexus fails for the user's stack): codebase-memory-mcp** (`DeusData/codebase-memory-mcp`)

**Explicitly rejected as primary:**
- code-review-graph — strong feature set (28 tools, community detection) but smaller ecosystem and no Claude Code integration depth.
- locus — narrower bundled-LSP coverage; setup friction per additional language.
- CodeGraphContext — regex fallback for non-Python languages is an accuracy hazard.
- syms — file-level only, no call graph. Cannot serve the blast-radius requirement.

## Why GitNexus is primary

Four factors decisive when license is not a filter:

**1. Ecosystem maturity.** 28.9K stars vs codebase-memory-mcp's 1.8K. 767 commits, 3.3K forks. Sustained development with commercial backing (akonlabs.com). The maturity gap matters for a pipeline that depends critically on the MCP's correctness — bugs in younger projects (codebase-memory-mcp's documented Cypher issues, per claim C-R2-0019 evidence trail) are more frequent and longer-lived.

**2. Deepest Claude Code integration of any candidate.** Per the GitNexus MCP docs (chatforest review April 25 2026): full support for MCP + skills + PreToolUse hooks. **No other candidate supports PreToolUse hooks.** This matters because:
   - Auto-augment hooks can inject blast-radius context before any tool that modifies code, without explicit agent invocation.
   - The pipeline's Critique-1 stage can hook GitNexus pre-tool to surface impact warnings before the agent commits to a recommendation.
   - This is the closest the MCP ecosystem comes to "ambient code intelligence" — the kind of friction-free presence the pipeline needs for the iterative-blast-radius loop.

**3. Auto-installs agent skills.** `gitnexus analyze` indexes the repo AND installs agent skills that teach Claude Code how to use the tools (per GitNexus docs). For our pipeline, this means a user running `gitnexus analyze` once gets all the integration: MCP tools, knowledge skills explaining when to use them, and AGENTS.md/CLAUDE.md context files. Reduces our pipeline's setup-instruction burden materially.

**4. Code Wiki + auto-doc.** GitNexus generates an auto-updating Code Wiki of the repository's architecture (per GitNexus docs). The synth-designer sub-agent can read this Wiki via MCP resources before drafting the blueprint, grounding architectural decisions in current code reality rather than stale assumptions. No other candidate ships this.

## Why codebase-memory-mcp is the fallback

Two factors that make it the right backup, not just a runner-up:

**1. 155-language coverage.** GitNexus's tree-sitter base supports many languages but its mature integrations are TS-first. Users with stacks like Java, Kotlin, Swift, R, MATLAB, Erlang, or other less-common languages may find GitNexus produces lower-quality structural data. codebase-memory-mcp's tree-sitter-everywhere approach has wider language reach. Configuring both means the pipeline degrades gracefully when GitNexus's coverage is thin for the user's stack.

**2. Explicit hop-based risk tier output.** codebase-memory-mcp's `trace_call_path` with `risk_labels=true` returns CRITICAL/HIGH/MEDIUM/LOW per hop (claim C-R2-0019). This is the exact shape multi-turn blast-radius needs. GitNexus's `analyze_impact` returns impact scope but not hop-based tiers as a named primitive — the pipeline would need to compute risk tiers from Cypher query results. Workable, but adds knowledge-skill content burden.

When GitNexus returns thin or empty results for the user's stack, the pipeline can fall through to codebase-memory-mcp's `detect_changes` for risk-tiered analysis. The fallback is purposeful, not contingency.

## How the pipeline uses both

Stage 0 preflight configuration check:

```
1. Is GitNexus MCP configured AND responding? → primary path.
2. If GitNexus configured but degraded for detected language → primary still GitNexus, supplement with codebase-memory-mcp for risk-tier analysis.
3. If GitNexus unavailable → primary becomes codebase-memory-mcp.
4. If neither → degraded mode per blueprint v2 §3.8 (native Grep/Glob + meta_warning).
```

Detection of "GitNexus is degraded for this language" is heuristic — if `analyze_impact` returns fewer than 3 affected symbols on a change set that touched non-trivial code, and codebase-memory-mcp's `detect_changes` on the same input returns more, the pipeline marks GitNexus as degraded-for-this-run and routes blast-radius queries to the fallback for the remainder.

The Critique-1 sub-agent (per its critique-1-knowledge skill, to be written) consults:
- **GitNexus tools** as primary: `analyze_impact`, Cypher queries on the knowledge graph, Code Wiki resource reads.
- **codebase-memory-mcp tools** when GitNexus is degraded or for explicit risk-tier output: `detect_changes`, `trace_call_path` with `risk_labels=true`.

Both MCPs configured in `.claude/settings.json`. Configuration burden is one-time per project.

## Risk-tier mapping from GitNexus to the pipeline's blast-radius schema

Since GitNexus does not natively output hop-based risk tiers but the pipeline depends on them, critique-1-knowledge will specify the mapping. The Critique-1 agent issues this Cypher pattern (or equivalent via analyze_impact + traversal depth parameter):

```
For each changed symbol:
  hop 1 callers/callees → mark CRITICAL
  hop 2 reachable symbols → mark HIGH
  hop 3 reachable symbols → mark MEDIUM
  hop 4+ reachable symbols → mark LOW
```

This is the same convention codebase-memory-mcp ships natively. Implementing it on top of GitNexus is straightforward Cypher traversal but represents real knowledge-skill content the pipeline must own.

## Consequences

**Positive:**

- Pipeline benefits from the most mature code-graph MCP ecosystem in the space (28.9K stars vs nearest competitor at 13K, primary at 1.8K).
- PreToolUse hooks enable an ambient-intelligence pattern no other candidate supports.
- Auto-installed GitNexus skills reduce pipeline setup-instruction burden.
- Code Wiki provides an architectural-documentation surface synth-designer can consume without additional infrastructure.
- 155-language fallback via codebase-memory-mcp covers stacks where GitNexus's TS-first focus is thin.
- Both MCPs run locally; no network egress required for code-graph queries.

**Negative:**

- **License: GitNexus uses PolyForm Noncommercial.** For users intending commercial use of the pipeline, this requires either (a) the GitNexus enterprise tier from akonlabs.com or (b) avoiding GitNexus and using codebase-memory-mcp as primary. The pipeline should document this clearly in setup guides. Users in research, education, personal projects, and open-source contexts have no license burden.
- The pipeline must own the risk-tier mapping on top of GitNexus's primitives, rather than consuming a named tier output. This is critique-1-knowledge content that needs to be written and maintained.
- Two MCPs configured concurrently doubles the MCP-related context overhead (per claim C-R2-0010, tool catalogs >20 tools begin to degrade selection accuracy). With GitNexus (16 tools) + codebase-memory-mcp (14 tools) = 30 code-graph tools, the threshold is crossed. Mitigation: the critique-1-knowledge skill should explicitly route agents to GitNexus by default and only mention codebase-memory-mcp tools in the fallback section.
- Setup friction is higher than single-MCP. Users must install both (or configure for graceful degradation when only one is present).

**Neutral:**

- The code-graph MCP space is fast-moving. This ADR should be revisited in ~6 months when both projects have additional release history.
- If GitNexus discontinues PolyForm and switches to MIT-equivalent licensing, the commercial-use concern evaporates and the recommendation gets stronger.

## Alternatives considered (paragraph each)

**Use codebase-memory-mcp as sole primary (ADR-0007 v1 position).** Rejected on user feedback that license-blocking GitNexus is not appropriate. The hop-tier semantic match was the primary technical argument; that's preserved by configuring codebase-memory-mcp as fallback rather than primary.

**Use GitNexus alone, drop the fallback.** Considered but rejected because GitNexus's TS-first language focus leaves coverage gaps for some user stacks. The fallback configuration adds setup complexity but the language-coverage backstop is worth it.

**Build a thin MCP proxy that fronts both with a uniform interface.** Rejected. Violates the manifest's "no new runtime infrastructure" constraint. The Critique-1 knowledge skill providing routing logic is content, not infrastructure.

**Use Cypher queries directly via GitNexus to compute hop tiers, ignoring codebase-memory-mcp entirely.** Considered. The pipeline's critique-1-knowledge would have to teach the Cypher pattern; that's manageable. But this loses the language-coverage backstop. Two-MCP configuration is the more robust choice.

## Evidence

Claims C-R2-0019 through C-R2-0022 (cited in v1).

Additional evidence weighed in this revision:

- GitNexus PreToolUse hook capability — chatforest April 25 2026 comparison table; GitNexus mintlify docs MCP Integration Overview page.
- GitNexus star count 28.9K, fork count 3.3K, commit count 767 — chatforest April 25 2026 comparison table.
- GitNexus auto-installs agent skills — GitNexus docs "How It Works" section: "Installs agent skills to teach AI agents how to use the tools" + "Creates context files (AGENTS.md, CLAUDE.md) for immediate use."
- GitNexus Code Wiki — GitNexus enterprise tier description, with OSS version including "Code Wiki is also available in OSS."

## Substrate registry version

v1.2 (2026-05-12) — supersedes v1.1 (ADR-0007 v1.0.0).

## Cross-stage supersession marker

`cross_stage_supersession: false` — this ADR supersedes ADR-0007 v1.0.0 within the same architectural stage (substrate selection). No earlier-stage decisions are invalidated. Synthesis claims C-R2-0019 through C-R2-0022 remain verified; their interpretation in light of the no-license-filter manifest is what changes.
