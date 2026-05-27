# feature-pipeline — context for AI coding agents

**Single source of truth.** This file is the canonical context document. `CLAUDE.md` is a git-tracked symlink to `AGENTS.md` — edit here, never there. Both Claude Code and Codex / Cursor / Copilot / Windsurf read the same bytes, so they never drift.

## Talking to the user

This project produces dense, code-heavy artifacts on purpose — Issues, ADRs, Blueprints, Plans, and the `FR-` / `H-` / `OI-` / `PV-` / `D-` code systems exist so reviewers and automation can cross-reference them precisely. **Conversation with the user is the opposite job.** Status updates, summaries, plans, and reports must read in plain English, not in the project's internal shorthand.

### Voice, tone, and style

- **Assume intelligence; do not assume knowledge.** The user is technical. They have not necessarily seen *this* artifact, *this* Issue, or *this* corner of the pipeline before. Explain the thing in plain words on first reference; do not lecture once they have seen it.
- **Be direct.** Active voice. Lead with the answer or the change; put the reasoning after, not before.
- **Write for the first-time reader.** Every response should make sense to someone who has not seen the prior turn. No undefined codes, no orphan acronyms, no "as I mentioned earlier."
- **Trim, don't pad.** Omit needless words. Drop hedges ("maybe", "potentially", "it seems"). One clear sentence beats three qualified ones.
- **Match the weight.** Routine status: terse. A decision the user must make, or a risk they need to see: explicit, named, and unhurried.
- **Prefer visuals over code citations.** A small table, a short bulleted list, or a `path:line` link to the source is easier to scan than a dense run of project identifiers. Reach for structure before you reach for labels.

### Reach for a diagram

A diagram is a faster path to intuition than three paragraphs of prose. Reach for one whenever you are about to explain architecture, a flow with branches, a sequence of calls, or a state machine. Use Mermaid in a fenced code block — it renders inline in this IDE and on GitHub, lives in version control, and the user can copy and edit it.

| Question the diagram answers | Diagram type |
| --- | --- |
| *"How are these components arranged, and what talks to what?"* | `flowchart` for small layouts; C4 *context* or *container* view for system-level |
| *"What does A say to B, and in what order?"* | `sequenceDiagram` (API calls, agent hand-offs, auth, retry loops) |
| *"What decisions does this process make next?"* | `flowchart` with decision diamonds |
| *"What states does this thing move through, and what triggers each transition?"* | `stateDiagram-v2` (the execute-orchestrator's substantive states are a textbook fit) |
| *"How are these things related — what depends on what?"* | `graph` for dependencies; `erDiagram` for data shapes |

Diagram discipline:

- **One diagram, one idea.** Five to ten nodes for a flowchart; eight to twelve participants for a sequence. If you need more, draw two diagrams or zoom out one level (the C4 lesson).
- **Pair with one or two sentences of context** *before* the diagram — say what it shows; let the picture do the rest.
- **Label edges with verbs, nodes with nouns.** *"user → API: send token"* beats *"user → API: token"*.
- **Use diagrams to build intuition, not to specify.** Conversation diagrams are throwaway aids for understanding; formal specification diagrams belong in the Blueprint.
- **Offer, don't impose.** For trivial questions a diagram is overhead. For anything spanning more than two components, more than three steps, or any kind of state transition — draw it.

### The frame — why / what / how / where / when

When explaining a change, decision, or finding, work the explanation through five plain-word questions:

| Lens | What to answer |
| --- | --- |
| **Why** | The reason the thing exists or the problem it solves — the motivation behind it. |
| **What** | The thing itself, named in normal English, **plus what happens if we do nothing**. The "do nothing" outcome makes the stakes concrete. |
| **How** | The mechanism in concrete terms — what runs, what changes, what the user would see. |
| **Where** | The location — a `path:line` link, a directory, a command, or a surface. |
| **When** | The trigger or timing — what fires it, what comes before, what comes after. |

Not every sentence needs all five — the lens is for explanations, not a forced template.

### Do

- Lead with the plain-English noun: *"the cross-artifact divergence Issue"* — not *"H1"*.
- Name passes, runs, and batches by what they do: *"the quick-wins hardening pass"* — not *"R1"*.
- Use a table, a short list, or a file link to structure the explanation. Visual scannability beats dense labels.
- When a sub-agent returns a structured verdict (e.g. `PASS`, `NEEDS_RECONCILIATION`, dimensional counts), **translate it for the user** in plain words — do not forward the raw enum as the answer.

### Don't

- **NEVER** string codes together as a substitute for a sentence (e.g. *"H1+H3+H5+H6 closes 11 of 12 defects"*). Say what each mechanism does in plain words.
- **NEVER** open a status update with a code-only header (e.g. *"FR-11, OI-4 closed"*). Lead with what changed.
- **Don't** invent run / cycle / batch labels (`R1`, `R2`, `C3`) without naming the underlying thing they refer to.
- **Don't** cite a project code unless the user asks for it or you are linking to a specific artifact for them to read. If a code does appear, it goes at the *end* of the sentence as a reference — never as the subject.

### Exemption — where codes belong

This rule applies to *conversation only* — the main agent's responses to the user. Artifacts that exist to formalize labels keep their codes: ADR bodies, Blueprint contract IDs, validator names, sub-agent verdict enums, JSON schemas, and everything under `working/feature/`, `Issues/`, and `adrs/`. The rule changes how Claude *talks about* those artifacts, not what is inside them.

## Before you commit

Multiple sessions, multiple agents, and the human all touch this repo. Treat the working tree as shared space — what is already modified when your session starts may not be yours to commit.

### Authorship rule

**A commit may only include changes this session made.** If `git status` shows files modified before this session started, those edits belong to whoever made them — another agent, a prior Claude Code session, the user mid-edit, or a partially-applied automated pass. Sweeping them into your own commit destroys the audit trail, ships an unfinished intermediate state someone else was about to revise, and may silently overwrite work you do not have the context to evaluate. ["Responsibility does not transfer to the model"](https://marketingagent.blog/2026/03/22/how-to-use-git-with-coding-agents-a-complete-2026-guide/) — it stays with the human reviewing the commit.

### Staging discipline

- Run `git status` and `git diff` at session start (or any time before commit) and note which files were already modified. Anything modified before this session touched it is not yours.
- Stage by explicit path: `git add path/to/file.ext`. Stage only files this session edited.
- If a file you touched was *also* modified at session start, **surface the overlap to the user** before committing. Offer (a) two separate commits in order — theirs first, then yours; (b) stash the pre-existing change, commit yours, restore theirs; or (c) pause for the user to clarify intent.
- Commit your own session's work as a self-contained unit, with a message that describes only what you did.

### Commit anti-patterns

- **NEVER** run `git add -A`, `git add .`, or `git commit -a` when pre-existing modifications you did not author are present in the working tree. These commands sweep indiscriminately.
- **NEVER** run destructive operations that could vaporize another session's uncommitted work: `git reset --hard`, `git checkout <ref> -- .`, `git restore .`, `git stash drop`, `git clean -fd`. A reported Claude Code bug ([anthropics/claude-code#55024](https://github.com/anthropics/claude-code/issues/55024)) silently overwrote 14 unstaged files with a single `git checkout` — assume the worst about destructive defaults.
- **Don't** treat "the file is already modified" as authorization to commit it. The session that authored a change is the only session that may commit it. This session may surface it; it may not take it.

### Exemption — when you *are* that session

The rule binds **authorship**, not freshness. If a prior turn of *this* session made an edit, you may continue to commit it as your own work — the conversation is one continuous author. The rule only applies to edits whose origin you cannot trace to this session's own tool calls.

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
