# feature-pipeline — context for AI coding agents

**Single source of truth.** This file is the canonical context document. `CLAUDE.md` is a git-tracked symlink to `AGENTS.md` — edit here, never there. Both Claude Code and Codex / Cursor / Copilot / Windsurf read the same bytes, so they never drift.

## MCP servers in this project

Five MCP servers are registered at project scope in [.mcp.json](.mcp.json). Each has a sharp job — they don't substitute for each other. Choose using the matrix; combine using the section after it.

> Note: `mcp-openapi-schema` was removed 2026-05-24 (see [.devcontainer/postCreate.sh](.devcontainer/postCreate.sh#L16)). `gitnexus` was removed 2026-05-27 per [ADR-0066](adrs/ADR-0066-gitnexus-removal.md) — empirical unreliability; the two dependent sub-agents fall back to Read/Grep/Glob + serena symbol tools per ADR-0007's documented fallback. The five below are the ground truth.

### When to reach for which

| If you're about to... | Use | Notes |
| --- | --- | --- |
| Find where a symbol is defined or referenced | `serena.find_symbol` / `find_referencing_symbols` | LSP-grade exact; faster than grep when the question is about symbols. |
| Trace "how does feature X work?" | Glob to enumerate candidates → Grep for behavioral keywords → `serena.find_referencing_symbols` to confirm the call edges | Grep + serena beats grep alone when the question is behavioral. |
| Look up a library API / syntax / migration | `context7.resolve-library-id` → `query-docs` | Knowledge cutoff is January 2026; libraries move. Use even when you think you know. |
| Research a vendor, technique, or current state-of-the-art | `exa.web_search_exa` (or `crawling_exa` for a known URL) | Cited results; treat as input to verify, not as truth. |
| Touch a file under `.github/workflows/` | `actionlint-mcp.lint_workflow` before commit | Catches YAML, action-pinning, and shell-injection issues. |
| Write or review Terraform | `terraform-mcp.get_provider_details` / `search_modules` | Registry-current and version-aware. |
| Rename a symbol | `serena.rename_symbol` | Understands the call graph — never find-and-replace. |
| Recall a project decision, postmortem, or onboarding note | `serena.read_memory` / `list_memories` | Project knowledge that isn't in the code. |
| Check what changed in your working tree before commit | `git diff` + targeted `serena.find_referencing_symbols` on changed symbols | Confirms the change set's blast radius before commit. |

### Combine, don't substitute

MCPs layer well — each answers a different question about the same change. The combinations below routinely beat using any one in isolation.

- **Serena + targeted Grep for safe edits.** Use `serena.find_referencing_symbols` to enumerate the exact reference set; use Grep as a coverage check for string-name references the LSP may miss (logged identifiers, dict keys, test parametrize tables).
- **Context7 + Exa for unfamiliar libraries.** Context7 first for the contract (official API, current version, migration notes). Exa second for community context (gotchas, GitHub issues, blog writeups). Don't skip the first; don't stop at it.
- **Actionlint + Grep when a workflow calls scripts.** Lint the YAML **and** grep for any helper functions the workflow invokes — workflows are silent integration points that the linter alone won't reveal.
- **Terraform-MCP + Context7 for provider/SDK alignment.** When a feature spans Terraform-provisioned infra and runtime SDK code, provider-vs-SDK version mismatch is the most common foot-gun. Cross-check both.
- **Serena memory + serena symbols for refactors.** Read `serena.read_memory` first for prior decisions and constraints, then walk the call graph via `find_symbol` / `find_referencing_symbols`. Memory tells you *why* the code is the way it is; the symbol tools tell you *what* it does now.

### Anti-patterns (don't do these)

- **NEVER find-and-replace rename.** Use `serena.rename_symbol`. Find-and-replace silently breaks string-name references, dynamic dispatch, and tests that reference the symbol by name.
- **NEVER commit a workflow change without `actionlint-mcp.lint_workflow`.** Silent YAML and shell-injection breakage is the #1 cause of CI surprises.
- **NEVER trust Context7 or Exa output without verification.** They fetch; they don't validate. Read the actual code / primary source before acting on any recommendation that affects the repo.
- **Don't use Exa for library docs** (Context7's job) or **Context7 for vendor research** (Exa's job). They overlap ~5%; the rest of the time the wrong tool is just slower with worse results.
- **Don't use `serena.execute_shell_command` when Bash is in your allowlist.** Bash runs under the harness sandbox and permission rules; Serena's shell bypasses some of that. Reserve it for cases where Bash genuinely can't reach.
- **Don't put credentials in `.mcp.json` argv or URL queries.** Env-block indirection only — this is enforced by [ADR-0039](adrs/) and the `auditing-mcp` OP-9 / OP-10 rules.
- **Don't skip a pre-commit `git diff` review.** It catches edits that touched more than you thought, which is how surprise regressions get committed.
- **Don't ask context7 about stdlib or a library that hasn't moved in years.** Read + Grep is faster. Context7 shines on actively-developed APIs.

### Sub-agent delegation reference

When delegating via the Agent tool, these are the sub-agents that already have MCP allowlists — useful when you want the work done in a separate context without re-justifying tool access.

| Server | Sub-agents with access | Allowlist |
| --- | --- | --- |
| `serena` | `discovery-codebase-researcher`, `review-architecture-auditor`, `design-cicd`, `design-codespaces`, `design-claude-code` | whole-server (per ADR-0040 — narrowed always-on, 5-agent canonical list) |
| `context7` | `discovery-external-researcher` | narrow (`resolve-library-id`, `query-docs`) |
| `exa` | `discovery-external-researcher` | narrow (`web_search_exa`, `company_research_exa`, `crawling_exa`) |
| `actionlint-mcp` | `design-cicd` | narrow (`lint_workflow`, `check_all_workflows`) |
| `terraform-mcp` | `design-iac` | whole-server (`mcp__terraform-mcp__*`) |

The main agent (this session) has access to all five. Most workflows route through the sub-agents above when the scope justifies context isolation.

### Deeper reference

| Topic | Skill / file |
| --- | --- |
| MCP platform facts — install, lifecycle hooks, event surface, credentials | [KB-mcp-platform](.claude/skills/KB-mcp-platform/SKILL.md) skill |
| MCP design discipline — when to add a server, allowlist sizing, OP-rule catalog | [KB-mcp-design](.claude/skills/KB-mcp-design/SKILL.md) skill |
| MCP audit ruleset (OP-1..OP-11) | [auditing-mcp](.claude/skills/auditing-mcp/) skill |
| MCP event surface (`.claude/runtime/mcp-events.jsonl`) | [KB-mcp-platform/references/mcp-events-jsonl.md](.claude/skills/KB-mcp-platform/references/mcp-events-jsonl.md) |
