# Claude Code Dynamic Workflows as the orchestration layer — research findings (for review)

> Output of a `claude-code-guide` investigation (2026-05-30) against the official Claude Code docs, on whether/how to adopt Dynamic Workflows as the pipeline's orchestration layer. Read-only — informs a proposed architecture/plan design change; nothing edited yet. Pair with the decision-graph research (Part VII) before the combined design proposal.

## Verdict: a good fit for the *dispatcher*, not a complete orchestration *system* on its own — which is exactly what our architecture already assumes.

### Confirmed capabilities
- **Primitives:** `agent()` (one subagent, optional JSON-Schema structured output with retry-on-mismatch), `parallel()` (barrier), `pipeline()` (no-barrier streaming), `phase()` (progress grouping). Concurrency cap ~16, hard cap 1,000 agents/run.
- **Single-dispatcher (our TB7): fully satisfied.** The script is the sole dispatcher; spawned agents cannot spawn agents; `workflow()` nesting is one level only.
- **File-handoff (our TB6): fits.** The script has no filesystem/shell; agents do the I/O and the script passes paths/results. Matches "stateless actors, file-path handoff."
- **Manifest-driven: feasible (manual).** No built-in routing DSL, but the script can read a static topology manifest (YAML/JSON) and implement state-conditional routing itself — exactly the "deterministic shell wrapping a probabilistic core" (our D2/D14).
- **Headless/scheduled:** runs via `claude -p` (keeps local `.mcp.json` servers) or cloud Routines (cloud connectors only — local MCP unavailable).

### Confirmed limits (the load-bearing ones)
- **Crash recovery: does NOT span a process restart.** Resume (`resumeFromRunId` + the completed-agent cache) works **only within the same session**; the journal's persistence/location is undocumented and is almost certainly session-local (lost on Codespace stop/start). **It does not satisfy D-DR-1 on its own.**
- **No mid-run human input.** Only agent permission prompts pause a run. A stage needing a human sign-off must be its **own workflow invocation** — you cannot hold an approval gate inside one script.
- **No persistent phase state across invocations**, no declarative phase gates.
- **Token cost is substantial** (Anthropic: "substantially more than a typical session"); research-preview status; best for bounded tasks, not overnight runs.
- **Sub-pipelines that spawn agents** must be flattened (one-level nesting) or wrapped as non-spawning subagents.

## Why this *confirms* our architecture rather than breaking it
1. **D-DR-1 is the needed complement, not redundant.** The engine orchestrates *within* a run; our **run-event JSONL log doubles as the recovery journal** (D-DR-1) to survive restart/rebuild. The two compose exactly as designed: workflow = in-session dispatcher; our log + coordinator = the durable, cross-restart spine.
2. **The pipeline is a sequence of per-gate workflow *segments*, not one monolith.** Because a human approval gate can't live inside a script, each gated segment is its own workflow invocation; a thin coordinator (reading `pipelines.yaml`, resuming state from the run-event log) sequences the segments across the six human gates. This is the hybrid orchestrator (D14) made concrete.
3. **TB6/TB7 hold cleanly.** Single dispatcher + file-handoff are native to the model.

## Architectural implications to fold into the design
- **D2/D14/D15:** name Dynamic Workflows as the concrete orchestration substrate; the manifest-reading + state-conditional routing is script logic; Strangler-Fig migration still applies (prose SKILL → per-segment workflow scripts).
- **D-DR-1:** keep the run-event log as the recovery journal — the engine explicitly does not provide cross-restart durability. Idempotency keys + replay live in our layer.
- **Human gates:** the orchestration decomposes into one workflow per gated segment; the coordinator owns sequencing + state persistence between them.
- **Cost + research-preview:** treat as a real risk — bounded segments, warn-before-enforce, and the JSONL log as the always-available record if a run is interrupted.
- **Headless:** prefer `claude -p` in the Codespace (keeps local MCP: serena/context7/exa) over cloud Routines for any run that needs the project's MCP servers.

## Sources
code.claude.com/docs/en/workflows.md · /headless.md · /routines.md · /sub-agents · anthropic.com/news/claude-opus-4-8 · claude.com/blog/introducing-dynamic-workflows-in-claude-code
