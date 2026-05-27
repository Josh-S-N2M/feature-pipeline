# feature-pipeline — context for AI coding agents

**Single source of truth.** This file is the canonical context document. `CLAUDE.md` is a git-tracked symlink to `AGENTS.md` — edit here, never there. Both Claude Code and Codex / Cursor / Copilot / Windsurf read the same bytes, so they never drift.

## MCP servers in this project

Six MCP servers are registered at project scope in [.mcp.json](.mcp.json). Each has a sharp job — they don't substitute for each other. Choose using the matrix; combine using the section after it.

> Note: `mcp-openapi-schema` was removed 2026-05-24 (see [.devcontainer/postCreate.sh](.devcontainer/postCreate.sh#L16)). The `KB-mcp-platform` skill still references it as one of seven — that's a stale-doc issue, not an active server. Treat the six below as the ground truth.

### When to reach for which

| If you're about to... | Use | Notes |
| --- | --- | --- |
| Edit any function / class / method | `gitnexus_impact` first | **Always.** See the GitNexus block below. HIGH/CRITICAL risk must be reported to the user before edits. |
| Find where a symbol is defined or referenced | `serena.find_symbol` / `find_referencing_symbols` | LSP-grade exact; faster than grep when the question is about symbols. |
| Trace "how does feature X work?" | `gitnexus_query` (process-grouped) | Returns execution flows; beats grep when the question is behavioral. |
| Look up a library API / syntax / migration | `context7.resolve-library-id` → `query-docs` | Knowledge cutoff is January 2026; libraries move. Use even when you think you know. |
| Research a vendor, technique, or current state-of-the-art | `exa.web_search_exa` (or `crawling_exa` for a known URL) | Cited results; treat as input to verify, not as truth. |
| Touch a file under `.github/workflows/` | `actionlint-mcp.lint_workflow` before commit | Catches YAML, action-pinning, and shell-injection issues. |
| Write or review Terraform | `terraform-mcp.get_provider_details` / `search_modules` | Registry-current and version-aware. |
| Rename a symbol | `gitnexus_rename` **or** `serena.rename_symbol` | Both understand the call graph — never find-and-replace. |
| Recall a project decision, postmortem, or onboarding note | `serena.read_memory` / `list_memories` | Project knowledge that isn't in the code. |
| Check what changed in your working tree before commit | `gitnexus_detect_changes` | Surfaces affected symbols and execution flows. |

### Combine, don't substitute

MCPs layer well — each answers a different question about the same change. The combinations below routinely beat using any one in isolation.

- **GitNexus + Serena for safe edits.** GitNexus gives you the *blast radius* (which processes / clusters break). Serena gives you the *symbol surface* (exact references to update). Flow: `gitnexus_impact` → assess risk → `serena.find_referencing_symbols` → make the edits.
- **Context7 + Exa for unfamiliar libraries.** Context7 first for the contract (official API, current version, migration notes). Exa second for community context (gotchas, GitHub issues, blog writeups). Don't skip the first; don't stop at it.
- **Actionlint + GitNexus when a workflow calls scripts.** Lint the YAML **and** run impact on any helper functions the workflow invokes — workflows are silent integration points that grep won't reveal.
- **Terraform-MCP + Context7 for provider/SDK alignment.** When a feature spans Terraform-provisioned infra and runtime SDK code, provider-vs-SDK version mismatch is the most common foot-gun. Cross-check both.
- **Serena memory + GitNexus context for refactors.** Read `serena.read_memory` first for prior decisions and constraints, then `gitnexus_context` for the current call graph. Serena tells you *why* the code is the way it is; GitNexus tells you *what* it does now.

### Anti-patterns (don't do these)

- **NEVER find-and-replace rename.** Use `gitnexus_rename` or `serena.rename_symbol`. Find-and-replace silently breaks string-name references, dynamic dispatch, and tests that reference the symbol by name.
- **NEVER commit a workflow change without `actionlint-mcp.lint_workflow`.** Silent YAML and shell-injection breakage is the #1 cause of CI surprises.
- **NEVER trust Context7 or Exa output without verification.** They fetch; they don't validate. Read the actual code / primary source before acting on any recommendation that affects the repo.
- **Don't use Exa for library docs** (Context7's job) or **Context7 for vendor research** (Exa's job). They overlap ~5%; the rest of the time the wrong tool is just slower with worse results.
- **Don't use `serena.execute_shell_command` when Bash is in your allowlist.** Bash runs under the harness sandbox and permission rules; Serena's shell bypasses some of that. Reserve it for cases where Bash genuinely can't reach.
- **Don't put credentials in `.mcp.json` argv or URL queries.** Env-block indirection only — this is enforced by [ADR-0039](adrs/) and the `auditing-mcp` OP-9 / OP-10 rules.
- **Don't skip `gitnexus_detect_changes` before commit.** It catches edits that touched more than you thought, which is how surprise regressions get committed.
- **Don't ask context7 about stdlib or a library that hasn't moved in years.** Read + Grep is faster. Context7 shines on actively-developed APIs.

### Sub-agent delegation reference

When delegating via the Agent tool, these are the sub-agents that already have MCP allowlists — useful when you want the work done in a separate context without re-justifying tool access.

| Server | Sub-agents with access | Allowlist |
| --- | --- | --- |
| `gitnexus` | `discovery-codebase-researcher`, `review-architecture-auditor` | whole-server (`mcp__gitnexus__*`) |
| `serena` | `discovery-codebase-researcher`, `review-architecture-auditor`, `design-cicd`, `design-codespaces`, `design-claude-code` | whole-server (per ADR-0040 — narrowed always-on, 5-agent canonical list) |
| `context7` | `discovery-external-researcher` | narrow (`resolve-library-id`, `query-docs`) |
| `exa` | `discovery-external-researcher` | narrow (`web_search_exa`, `company_research_exa`, `crawling_exa`) |
| `actionlint-mcp` | `design-cicd` | narrow (`lint_workflow`, `check_all_workflows`) |
| `terraform-mcp` | `design-iac` | whole-server (`mcp__terraform-mcp__*`) |

The main agent (this session) has access to all six. Most workflows route through the sub-agents above when the scope justifies context isolation.

### Deeper reference

| Topic | Skill / file |
| --- | --- |
| GitNexus deep dives — exploring, refactoring, debugging, impact | [.claude/skills/gitnexus/](.claude/skills/gitnexus/) (and the block below) |
| MCP platform facts — install, lifecycle hooks, event surface, credentials | [KB-mcp-platform](.claude/skills/KB-mcp-platform/SKILL.md) skill |
| MCP design discipline — when to add a server, allowlist sizing, OP-rule catalog | [KB-mcp-design](.claude/skills/KB-mcp-design/SKILL.md) skill |
| MCP audit ruleset (OP-1..OP-11) | [auditing-mcp](.claude/skills/auditing-mcp/) skill |
| MCP event surface (`.claude/runtime/mcp-events.jsonl`) | [KB-mcp-platform/references/mcp-events-jsonl.md](.claude/skills/KB-mcp-platform/references/mcp-events-jsonl.md) |

---

<!-- markdownlint-disable MD025 -- The GitNexus block below has its own h1, giving the file two h1s by design. The block is regenerated by `npx gitnexus analyze` and must not be edited inside its markers. -->
<!-- gitnexus:start -->
# GitNexus — Code Intelligence

This project is indexed by GitNexus as **feature-pipeline** (11494 symbols, 11508 relationships, 0 execution flows). Use the GitNexus MCP tools to understand code, assess impact, and navigate safely.

> If any GitNexus tool warns the index is stale, run `npx gitnexus analyze` in terminal first.

## Always Do

- **MUST run impact analysis before editing any symbol.** Before modifying a function, class, or method, run `gitnexus_impact({target: "symbolName", direction: "upstream"})` and report the blast radius (direct callers, affected processes, risk level) to the user.
- **MUST run `gitnexus_detect_changes()` before committing** to verify your changes only affect expected symbols and execution flows.
- **MUST warn the user** if impact analysis returns HIGH or CRITICAL risk before proceeding with edits.
- When exploring unfamiliar code, use `gitnexus_query({query: "concept"})` to find execution flows instead of grepping. It returns process-grouped results ranked by relevance.
- When you need full context on a specific symbol — callers, callees, which execution flows it participates in — use `gitnexus_context({name: "symbolName"})`.

## Never Do

- NEVER edit a function, class, or method without first running `gitnexus_impact` on it.
- NEVER ignore HIGH or CRITICAL risk warnings from impact analysis.
- NEVER rename symbols with find-and-replace — use `gitnexus_rename` which understands the call graph.
- NEVER commit changes without running `gitnexus_detect_changes()` to check affected scope.

## Resources

| Resource | Use for |
|----------|---------|
| `gitnexus://repo/feature-pipeline/context` | Codebase overview, check index freshness |
| `gitnexus://repo/feature-pipeline/clusters` | All functional areas |
| `gitnexus://repo/feature-pipeline/processes` | All execution flows |
| `gitnexus://repo/feature-pipeline/process/{name}` | Step-by-step execution trace |

## CLI

| Task | Read this skill file |
|------|---------------------|
| Understand architecture / "How does X work?" | `.claude/skills/gitnexus/gitnexus-exploring/SKILL.md` |
| Blast radius / "What breaks if I change X?" | `.claude/skills/gitnexus/gitnexus-impact-analysis/SKILL.md` |
| Trace bugs / "Why is X failing?" | `.claude/skills/gitnexus/gitnexus-debugging/SKILL.md` |
| Rename / extract / split / refactor | `.claude/skills/gitnexus/gitnexus-refactoring/SKILL.md` |
| Tools, resources, schema reference | `.claude/skills/gitnexus/gitnexus-guide/SKILL.md` |
| Index, status, clean, wiki CLI commands | `.claude/skills/gitnexus/gitnexus-cli/SKILL.md` |

<!-- gitnexus:end -->
<!-- markdownlint-enable MD025 -->
