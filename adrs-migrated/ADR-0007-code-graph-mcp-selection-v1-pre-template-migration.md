# ADR-0007: Code-graph MCP selection — codebase-memory-mcp as primary, locus as fallback

## Status
Accepted — 2026-05-12

## Context

Blueprint v2 ADR-0001 commits the pipeline to using a code-graph MCP for blast-radius analysis in Critique-1 and codebase research in Stage 3. The original substrate-map (D-0008, D-0009) named locus as the recommended choice based on first-round research. Second-round research surfaced additional candidates with materially different tradeoffs that warrant revisiting the selection and locking it down in an ADR.

## Candidates evaluated

Six code-graph MCPs published Feb-April 2026, plus one earlier survey:

| Server | Stars | License | Languages | Tools | MCP-native | Blast-radius primitive |
|---|---|---|---|---|---|---|
| **codebase-memory-mcp** (DeusData) | 1.8K | MIT | 155 | 14 | yes (static binary) | `detect_changes` with CRITICAL/HIGH/MEDIUM/LOW risk tiers + `trace_call_path` BFS depth 1-5 |
| **GitNexus** | 28.9K | **PolyForm Noncommercial** | TS-first multi-lang | 16 | yes (CLI + WASM) | `analyze_impact` + Cypher queries |
| **code-review-graph** | 13K | MIT | 21 (TS, Vue, Svelte, Go, Rust, Java, Scala, C#, Ruby, Python, Solidity, C/C++ ...) | 28 | yes | blast radius + community detection + execution flow |
| **locus** | (small) | MIT-equivalent | 5 bundled LSP (Go, Python, Rust, TS/JS, C/C++); more via manual LSP install | ~5 namespaced | yes | `analysis impact` action |
| **CodeGraphContext** | ~3K | MIT | 66 (tree-sitter + LSP hybrid for Go, C, C++) | 14 | yes | `get_change_impact` (Python AST-based; regex for others) |
| **syms (Jordan-Horner/symbols)** | small | MIT | 14 | 7 | yes | `syms_impact` file-level only (no call graph) |
| **JonnyDB/code-graph-mcp** (MRCIS) | small | MIT | 15+ | 6 | yes | Impact Analysis prompt workflow |

Source: claims C-R2-0019 through C-R2-0022; ChatForest comparison (April 25 2026, within cutoff).

## Decision

**Primary: `codebase-memory-mcp` (DeusData)**

**Recommended fallback: `locus`** for cases where codebase-memory-mcp fails to index, or where the user's stack overlaps locus's bundled LSP set well (Go/Python/Rust/TS-JS/C-C++).

**Explicitly NOT recommended: GitNexus** — PolyForm Noncommercial license prohibits commercial use without paid enterprise tier. The pipeline must work in commercial settings; license-restricted dependencies are blast-radius hazards of their own.

## Reasoning

### Why codebase-memory-mcp is primary

Three factors decisive:

1. **Direct alignment between its primitives and the pipeline's blast-radius semantics.** Claim C-R2-0019: codebase-memory-mcp's `trace_call_path` with `risk_labels=true` returns:
   - CRITICAL (hop 1) — direct callers/callees, will break
   - HIGH (hop 2) — indirect, likely affected
   - MEDIUM (hop 3) — may be affected
   - LOW (hop 4+) — unlikely but possible
   
   This is the *exact* shape Critique-1 needs. The "multi-turn blast radius" framing in the user's original spec maps 1:1 to hop-depth risk tiers. No translation layer required.

2. **`detect_changes` does git-diff → affected-symbols + blast-radius + risk classification in one tool call.** This is the right primitive for the iterative-blast-radius pattern (B5 in research round 2): pass `detect_changes` over each resolution attempt, get the new blast radius, compare to previous iteration's, terminate when stable.

3. **155-language coverage with single zero-dependency static binary.** Significantly broader than locus (5 bundled + manual install), broader than code-review-graph (21), broader than CodeGraphContext (66). MIT license. No runtime dependencies (per release notes).

### Why locus is recommended fallback

Three factors that make it useful even when codebase-memory-mcp is primary:

1. **LSP-backed analysis depth.** Locus uses real LSP servers (gopls, rust-analyzer, etc.) where they're available, falling back only when LSP isn't. For deep type-aware analysis in the 5 bundled languages, this is often more accurate than tree-sitter alone.

2. **"Architect's Book" knowledge graph.** Locus ships with a 28-entry knowledge graph of architectural diagnostics (violations, measured_by, confused_with, remediation) that can pair with Critique-1's checklist work. No other candidate has this.

3. **`render_diagram` capability across 16 diagram types.** Useful for the synth-designer sub-agent to attach architectural diagrams to blueprints. Not blast-radius-critical, but a nice secondary capability.

### Why not the others

- **GitNexus:** Dominant in star count but license-blocked for commercial use. The pipeline can't recommend a dependency that requires a paid commercial license for production work without significant warning. If a user has PolyForm-licensed GitNexus already running, the pipeline can adapt — but it cannot be the default.

- **code-review-graph:** Strong feature set (28 tools, including community detection and execution flow tracing) but 21-language coverage is narrower than codebase-memory-mcp's 155. Worth considering if the user's stack is specifically TS/Python/Go/Rust and they want the extra tools.

- **CodeGraphContext:** Sound architecture (Python AST primary, regex for other langs) but the regex fallback is a known accuracy hazard for non-Python languages. Codebase-memory-mcp's tree-sitter-everywhere approach is more uniform.

- **syms (symbols):** Explicitly file-level only, no call graph. The pipeline needs call-graph-level blast radius. Disqualifying.

- **MRCIS (JonnyDB/code-graph-mcp):** Smaller tool surface, fewer published benchmarks. Reasonable if the user has it installed but no advantage over codebase-memory-mcp for greenfield setup.

## Configuration

The pipeline's Stage 0 preflight detects MCP configuration. The recommended `.mcp.json` entry:

```json
{
  "mcpServers": {
    "codebase-memory": {
      "command": "codebase-memory-mcp",
      "args": ["--repo-root", "${PROJECT_ROOT}"]
    }
  }
}
```

Stage 0 preflight checks:
1. Is `codebase-memory` MCP configured and responding? → primary path.
2. If not, is `locus` configured and responding? → fallback path.
3. If neither, emit degraded-mode warning per blueprint v2 §3.8: Critique-1 falls back to native Grep/Glob with explicit `meta_warning` entry in `06-critique-1-issues.json`.

## Tools the pipeline uses

For Critique-1 blast-radius analysis (primary use case), the pipeline calls these tools on the configured MCP:

- **codebase-memory-mcp:** `detect_changes` (scope=`branch` against the working baseline), `trace_call_path` (with `risk_labels=true`, depth=3-4), `get_architecture` (once per run for high-level orientation).
- **locus (fallback):** `analysis impact` (depth=3), `analysis callers`, `analysis callees`.

For codebase research in Stage 3 (secondary use case):

- **codebase-memory-mcp:** `search_graph`, `get_architecture`, `query_graph` (Cypher) for structural queries; `search_code` for grep-shaped queries within indexed projects.
- **locus (fallback):** `analysis symbol_search`, `analysis search`, `book` for architectural diagnostics.

## Consequences

Positive:
- Aligns blast-radius semantics 1:1 with risk tiers Critique-1 needs. No translation layer.
- 155-language coverage minimizes the "user's stack outside our support" failure mode.
- MIT license enables commercial use.
- Static binary minimizes setup friction (download, run, done — per release notes claim C-R2-0019).
- Fallback to locus covers the case where codebase-memory-mcp fails to index a particular language well.

Negative:
- **codebase-memory-mcp has documented bugs as of April 2026** in Cypher query support: pipe-syntax label alternation, label tests in WHERE clauses, count(DISTINCT), WITH DISTINCT silent-ignore, DISTINCT-after-ORDER-BY bug, search_code with name_pattern slow on large datasets, segmentation faults reported. (Source: issues #237-#254 on the repo, April 2026, within cutoff.) The pipeline must use defensive query patterns and not rely on advanced Cypher features.
- Vendor benchmarks (claim C-R2-0020) are unverified independently. The "Linux kernel in 3 minutes" claim should not be treated as guaranteed performance.
- 155-language claim assumes tree-sitter grammar quality across all 155; in practice some languages have better support than others. The pipeline should not assume uniform analysis accuracy.

Neutral / monitored:
- The code-graph MCP space is fast-moving. This ADR should be revisited in 6 months. If a clear category winner emerges with stronger primitives, supersede this ADR.

## Alternatives considered (one paragraph each)

**Option: use multiple code-graph MCPs simultaneously.** Rejected. Per claim C-R2-0010 (Tool RAG threshold ~20 tools), each MCP adds ~14-28 tools to the catalog. Having two configured means 28-56 code-graph tools, well over the choice-overload threshold. Pick one primary, document one fallback, don't try to use both at runtime.

**Option: build a pipeline-specific code-graph layer.** Rejected. Violates the manifest's "no new runtime infrastructure" hard constraint. The MCP ecosystem already produced multiple viable candidates; the pipeline should consume, not produce.

**Option: rely on native Grep/Glob only.** Rejected as primary, kept as degraded-mode fallback (blueprint v2 §3.8). Per claim C-R2-0008's adjacent finding on agent capabilities, naive grep across a codebase produces 99%+ token waste compared to structural queries. Codebase-memory-mcp's own benchmark claims 99.2% token reduction (claim C-R2-0019). Native-only is a real backstop but not a working primary.

## Evidence

Claims C-R2-0019 (codebase-memory-mcp tool surface and risk tiers — verified vendor doc), C-R2-0020 (codebase-memory-mcp benchmarks — vendor source, treat as upper bound), C-R2-0021 (license comparison — verified secondary source), C-R2-0022 (locus LSP backing — verified vendor doc).

## Substrate registry version
v1.1 (2026-05-12 — supersedes ADR-0007 placeholder mention in blueprint v2 D-0008)

## Cross-stage supersession marker
`cross_stage_supersession: false` — this ADR supplements blueprint v2's D-0008 (which named locus pre-research-round-2) without invalidating any prior synthesis claim. The reason locus was named originally was its visibility in research round 1; round 2 surfaced codebase-memory-mcp's stronger alignment with the pipeline's specific needs. Both are tracked; primary changes.
