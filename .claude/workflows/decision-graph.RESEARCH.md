# Decision log + decision graph for AI interfacing — research findings (for review)

> Output of `research-and-verify` run 2026-05-30 (run wf_f4764221-834; 56 agents, ~2.3M tokens). Read-only — informs the Part VII (knowledge governance) design. Load-bearing claims are the verified subset; the could-not-verify list is provenance hygiene.

I have all the verification data I need. Let me synthesize the consensus answer.

---

## Consensus: Evolving an ADR Index into an AI-Queryable Decision Graph

### (1) The consensus in plain English

**Model decisions as a graph, but derive it — don't extract it.** The strongest practitioner position (NILUS, June 2025) is that ADRs gain real operational value when treated as a connected graph of decision nodes plus typed edges (`supersedes`, `constrains`, `influences`, `depends_on`, `conflicts_with`), letting you answer questions a flat list cannot: "which superseded decisions are still in production?", "what blocks this migration?". But the same source — and the wider field — warns against reaching for a graph database "merely because the article has the word graph in it."

**For your situation, the expensive, brittle part of GraphRAG does not apply.** Full GraphRAG's cost and failure modes come from using an LLM to extract entities and relationships from prose. Your 68 ADRs already carry explicit `supersedes`/`depends-on` edges in YAML frontmatter — the structure is *authored, not inferred*. A graph derived from frontmatter skips extraction and most of its failure modes entirely. Academic work (Nov 2025) confirms an ontology-guided graph from a structured source matches GraphRAG accuracy at a fraction of the maintenance cost.

**The bi-temporal supersession pattern is settled.** Track two time axes per edge — when a decision was valid in the real world vs. when the system recorded it — and handle supersession by *invalidating* edges (stamping `invalid_at`), never deleting them, so both "what is true now" and "what did we believe at time T" stay queryable. This is implemented identically across Graphiti/Zep, the OpenAI Temporal Agents cookbook, and several 2026 tools.

**For AI consumption, expose typed MCP tools, not raw Cypher.** The 2025 shift is away from one-shot natural-language-to-Cypher toward predefined, parameterized graph-query tools. Keep responses context-budget-disciplined (timeouts, truncation, drop oversized fields).

### (2) Settled vs. contested

| Settled | Contested |
|---|---|
| Bi-temporal model; supersession = invalidation, not deletion | Whether GraphRAG beats vector RAG (task-dependent; loses on single-hop) |
| You usually don't need a dedicated graph DB; Postgres/files suffice under ~1M entities | Whether "ADRs-as-graph" is true *consensus* (largely one strong blog + emerging tools) |
| Derived-from-structured-source beats LLM-extraction-from-prose | Exact precision/latency penalties of GraphRAG (figures vary by source) |
| Start simple; add graph only where retrieval fails for structural reasons | |
| MCP typed-tool surface over arbitrary query generation | |

### (3) Confidence per major claim (verified citations only)

- **High** — MCP reference memory server is a file-backed, no-DB knowledge graph (single process); directly fits "derived graph over frontmatter via MCP." *(verified)*
- **High** — Bi-temporal/supersession-as-invalidation is cross-vendor (Zep paper arXiv 2501.13956; Graphiti docs; OpenAI cookbook). *(all verified)*
- **High** — You usually don't need a graph DB (Hamel/Bergum; Jacar; To Data & Beyond — all verified).
- **High** — LLM extraction is the costly part; structured-source graphs avoid it (Microsoft LazyGraphRAG; arXiv 2511.05991; arXiv 2506.05690 — verified).
- **High** — Existing ADR tooling (log4brains, adr-log) is flat-index-only — the gap is real *(verified)*.
- **Medium-High** — Working git-native, MCP-exposed derived-graph tools already exist: `dg` (verified), `mcp-adr` (verified), `adr-governance`/`structured-madr` (verified), `markedup` (verified). All are young/low-adoption.
- **Medium** — Graphiti MCP runs single-container (FalkorDB) but adds an LLM/embeddings ingest dependency and is experimental *(verified)*.

### (4) Could-not-verify — do NOT rely on these

- **`nodex` as "AI-agent native" with `graph.json` + `backlinks.json`** — *refuted*: its README says "no AI dependencies"; only `graph.json` exists. The tool is real; the framing is wrong.
- **tianpan.co "GraphRAG-Bench −13%/−16%"** — *unverified*: the article's directional argument is genuine, but those specific figures are not on the page.
- **FalkorDB four-point "consensus"** — *unverified*: source backs only the queryable/debuggable framing; it actually disfavors hybrid retrieval. A single vendor blog cannot establish field consensus.
- **MachineLearningMastery "single question" quote** — *unverified*: the framing quote and the "/ DEV" co-attribution don't appear in the cited page (substance otherwise holds).

### Bottom line

Not a product, and not heavyweight GraphRAG. The right answer is a **pattern: a derived graph over your committed ADR frontmatter + canonical YAML, exposed through a typed MCP query surface**, with bi-temporal supersession (invalidate, never delete) and a **validator enforcing cross-link integrity** (bidirectional links, supersession resolution) — not just a JSON schema. Build it in-container with no graph database; reach for Postgres/SQLite recursive CTEs or a graph DB only if edge counts ever cross hundreds of thousands. Existing tools (`dg`, `mcp-adr`) are proof-of-pattern references, not yet mature dependencies.

---

## Could-not-verify (provenance hygiene)

1. **nodex is a current open-source tool that scans a project's markdown, extracts YAML frontmatter and link relationships, and builds an immutable in-memory document graph (supersession chains, backlinks,**
   - verdict: unverified — URL resolves to a real repo: nodex, a Rust CLI that "turns markdown files into a queryable, validated document graph." Most technical claims are confirmed verbatim from the README: scans markdown, extracts YAML frontmatter + link relationships; immutable in-memory typed graph with supersession chain
2. **Strong practitioner consensus: do NOT build the graph first. Start with the simplest thing, instrument failures, and add graph structure only for the specific query patterns where retrieval demonstrab**
   - verdict: unverified — URL resolves to a real, matching article: "GraphRAG vs. Vector RAG: The Architecture Decision Teams Make Too Late" by Tian Pan, dated 2026-04-19 (confirmed via fetch and independent search). Date is plausible (recent past relative to today 2026-05-30; not future).

The page SUPPORTS the qualitative 
3. **The MachineLearningMastery / DEV practitioner guides frame the decision as a single question — 'Is the answer I need in a piece of text, or in the relationship between pieces of text?' — and note the **
   - verdict: unverified — The page is real (MachineLearningMastery, author Matthew Mayo, dated 2026-03-05 — matches the stated date) and the substantive technical claims are well supported, several nearly verbatim: the cold-start problem ("a knowledge graph requires substantial upfront effort to populate before it can answer
4. **The 2025-2026 consensus on what makes a knowledge graph 'good for AI interfacing' / agent consumption is: (1) expose it through an MCP query surface of typed tools so the client integration is standar**
   - verdict: unverified — URL resolves to a real FalkorDB blog page titled exactly as cited ("MCP for agent memory: Graphiti + FalkorDB for persistent, multi-tenant knowledge graphs"), corroborated independently by FalkorDB docs, an OpenPR press release, and FalkorDB's own X post. Stated date 2025-12-14 is plausible and conf