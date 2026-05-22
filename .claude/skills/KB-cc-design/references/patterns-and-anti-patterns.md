# Claude Code Patterns and Anti-Patterns

## Contents

- Primitive-selection patterns
- CLAUDE.md refactoring patterns
- Rule patterns
- Skill patterns
- Subagent patterns
- Hook patterns
- MCP integration patterns
- Plugin patterns
- Anti-patterns reviewers should flag
- Decision frames

## Primitive-selection patterns

### Decision matrix

| Goal | Primitive | Why |
|---|---|---|
| Always-on guidance for every session | CLAUDE.md (sparingly) | Loads every request; keep short |
| Guidance that only matters for specific files | Rule with `paths:` | Free when paths don't match |
| Reusable knowledge Claude pulls in when relevant | Model-invocable skill | Description-matched; loaded on demand |
| Workflow the user triggers explicitly | Skill with `disable-model-invocation: true` | `/skill-name` invocation; zero context until used |
| Work that reads many files; main session wants the summary | Subagent | Isolated context; returns summary |
| Specialized worker with restricted tools | Subagent with `tools:` | Per-agent tool restriction |
| Subagent that remembers across runs | Subagent with `memory:` scope | Persistent MEMORY.md |
| Deterministic side effect on every edit/commit | Hook | Outside the loop; zero context cost |
| Block dangerous commands | Hook (`PreToolUse` denying) or `permissions.deny` | Enforced regardless of model decision |
| Connect to external service | MCP server | Standard protocol; tool schemas deferred |
| Bundle multiple primitives for distribution | Plugin | Packaging layer |
| Adapt Claude for non-coding work | Output style | Modifies system prompt |

### Layered defense for safety

Combine instruction + enforcement:

- **CLAUDE.md note**: "Never modify production secrets paths."
- **Rule with `paths:`** for the secrets directory: "Read-only; alert if a modification is proposed."
- **Hook**: `PreToolUse` denies Write/Edit in the secrets path.
- **`permissions.deny`**: explicit deny rule for the path.

The instruction makes the right path obvious; the enforcement prevents the wrong path.

## CLAUDE.md refactoring patterns

### Move reference material to skills

CLAUDE.md should hold high-frequency, always-relevant guidance: "we use Vitest, not Jest"; "tests live in `tests/`"; "use the canonical error envelope."

Move out of CLAUDE.md:

- Reference material (architecture docs, library APIs, design patterns).
- File-specific conventions (move to path-gated rules).
- Tutorials or how-to sequences (skills with `disable-model-invocation: true`).
- One-off project-specific knowledge that's rarely relevant (skills, model-invocable).

A 500-line CLAUDE.md is too long. Target: under 150 lines for most projects.

### Split into levels

CLAUDE.md loads additively across user, project, and (rarely) managed levels:

- **User CLAUDE.md** (`~/.claude/CLAUDE.md`): personal preferences (commit message style, language choice for ambiguous prompts). Applies across all projects.
- **Project CLAUDE.md** (`.claude/CLAUDE.md`): project-wide norms. Shared with the team.
- **Local override** (`CLAUDE.local.md`, git-ignored): personal overrides for this project.

The Designer documents which content belongs at which level. Putting team norms in user CLAUDE.md spreads them only to that user; putting personal preferences in project CLAUDE.md imposes them on everyone.

## Rule patterns

### Path-gated rule

```markdown
---
paths:
  - "**/migrations/*.sql"
  - "**/migrations/*.py"
---

# Migration conventions

- Every migration is reversible.
- Use expand-then-contract for breaking schema changes.
- Backfill in batches; never `UPDATE ... WHERE` against unbounded sets.
```

**When to use.** Anywhere the guidance is file-domain-specific.

### Unconditional rule (use sparingly)

For genuinely cross-cutting concerns that don't fit CLAUDE.md (e.g., team-wide engineering principles too long for CLAUDE.md but always relevant).

**Risk.** Every unconditional rule loads every session. Audit periodically; demote to path-gated where possible.

## Skill patterns

### Model-invocable knowledge skill

A skill Claude pulls in when the description matches:

```markdown
---
name: postgres-tuning
description: Use whenever the task involves Postgres performance: query plans, index design, EXPLAIN ANALYZE output, connection pooling, vacuum tuning, or replication lag. Trigger on slow query reports, plan output, or any mention of pg_stat_*, pg_locks, autovacuum, statement_timeout.
---

# Postgres tuning

(content)
```

**When to use.** Reference knowledge Claude should consult when relevant. Cost: only the description until invoked.

**Discipline.** Description is the load-bearing field; precise descriptions help the right skill load.

### User-invocable workflow skill

A skill the user triggers explicitly:

```markdown
---
name: prepare-release
description: Prepare a release: bump version, update CHANGELOG, tag, push.
disable-model-invocation: true
allowed-tools: Read, Edit, Bash(git *), Bash(npm version *)
---

# Prepare release

(prompt + supporting scripts in assets/)
```

**When to use.** Multi-step workflows the user invokes by name (`/prepare-release`).

### Skill with bundled supporting files

```
.claude/skills/api-review/
├── SKILL.md
├── assets/
│   ├── review-checklist.md
│   └── error-envelope.example.json
├── scripts/
│   └── lint_openapi.py
└── references/
    ├── rest-conventions.md
    └── graphql-conventions.md
```

**When to use.** Skill that needs ancillary content (templates, scripts, deeper references).

## Subagent patterns

### Research subagent

```markdown
---
name: codebase-explorer
description: Reads source files to answer questions about how the codebase is organized.
tools: Read, Grep, Glob
skills: postgres-tuning, frontend-conventions
---

You are a codebase explorer. Given a question about the codebase, read files,
return a structured summary, and cite files with line numbers.
```

**When to use.** "How does X work in this codebase?" — reads many files, returns summary.

### Restricted-tools reviewer

```markdown
---
name: code-reviewer
description: Reviews diffs for style, security, and correctness.
tools: Read, Grep
---

(prompt)
```

**Tools restricted to read-only.** The subagent can't modify files even if it tries.

**When to use.** Review workflows where the agent should not edit.

### Memory-enabled subagent

```markdown
---
name: debug-history
description: Tracks debugging sessions and patterns across runs.
memory: project
---

(prompt)
```

**`memory: project`** persists MEMORY.md in `.claude/agents/debug-history/MEMORY.md`. Surviving content is committed and shared.

**When to use.** Recurring workflows where past learning matters.

### Reasoning-configured subagent

```markdown
---
name: architecture-reviewer
description: Reviews proposed architectural changes across multiple system layers for internal consistency and risk.
model: opus
effort: high
tools: Read, Grep, Glob
skills:
  - system-architecture-principles
  - blast-radius-analysis
---

(prompt)
```

**Three independent reasoning knobs.** `model: opus` selects the strongest model; `effort: high` directs that model to spend more thinking tokens; `skills:` preload domain rubrics. Each is a deliberate choice; defaulting all three is the smell.

**When to use.** Cross-cutting reconciliation, multi-artifact arbitration, or any sub-agent whose reasoning quality is the load-bearing input — not its tool access or its prompt clarity alone.

**What to NOT do.** Do not use `skills: [deep-reasoning, …]` to express reasoning-depth intent. `deep-reasoning` is a literal skill identifier — if no such SKILL.md exists, Claude Code silently loads nothing, and the sub-agent runs at default reasoning while the design claims otherwise. Map reasoning-depth intent to `model:` and `effort:`. See the corresponding anti-pattern below.

## Hook patterns

### Lint / format on edit

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "match": "Write|Edit",
        "command": "prettier --write \"$file\""
      }
    ]
  }
}
```

**When to use.** Deterministic formatting; should never depend on context.

### Block dangerous commands

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "match": "Bash",
        "command": "scripts/deny-dangerous.sh \"$command\""
      }
    ]
  }
}
```

The script returns `{"permissionDecision": "deny", "permissionDecisionReason": "..."}` to block; otherwise allow.

**When to use.** Layered defense alongside `permissions.deny`.

### Session start banner

```json
{
  "hooks": {
    "SessionStart": [
      {
        "command": "echo 'Currently on branch: $(git branch --show-current)'"
      }
    ]
  }
}
```

**When to use.** Light operational reminders.

## MCP integration patterns

### Project-scoped MCP server

Configured in `.mcp.json` committed to the repo. Every team member who opens the project gets the server.

**When to use.** Project-wide tooling (database introspection, internal API).

### User-scoped MCP server

Configured globally. Only this user gets it.

**When to use.** Personal tools (cloud account access, individual integrations).

### MCP tool naming hygiene

The Designer documents:

- MCP server names (must be unique within scope).
- Tool naming conventions (tools appear as `mcp__<server>__<tool>`).
- Permission policies for high-impact MCP tools.

## Plugin patterns

### Single-project plugin (rare)

Skills + hooks + agents bundled, installed from a local path.

**When to use.** Rarely. Usually overkill for one project.

### Org-internal plugin

Plugin published in an internal marketplace, consumed by N projects.

**When to use.** Standardizing CC configuration across projects.

**Discipline.** Versioned; consumers pin to a version. Plugin's own CI runs on PRs.

### Public plugin

Open-source plugin published to a public marketplace.

**When to use.** Genuinely reusable, generic configuration.

**Discipline.** Public-quality docs; semver compliance; security review.

## Anti-patterns reviewers should flag

| Anti-pattern | Why it's bad | Typical fix |
|---|---|---|
| CLAUDE.md >300 lines | Token waste every request | Move reference material to skills |
| Unconditional rule for file-specific guidance | Loaded every session regardless of relevance | Add `paths:` |
| Skill description vague ("Use when relevant") | Skill never matches the right requests | Specific triggers, file globs, keyword phrases |
| Subagent for 2-tool-call task | Setup cost > benefit | Direct in lead agent |
| Subagent without `tools:` restriction | Inherits full tool surface; broader than needed | Scope tools to what's required |
| Subagent listing 15 skills | Subagent doesn't auto-load by description; lists explode | Smaller skill set; rely on subagent prompt for guidance |
| Subagent `skills:` array used to express reasoning depth (e.g., `skills: [deep-reasoning, …]`) | Category error — `skills:` preloads SKILL.md content; missing skill references load silently as nothing; the sub-agent runs at default reasoning while design claims otherwise | Map reasoning intent to `model:` (sonnet/opus/haiku) and `effort:` (low/medium/high/xhigh/max); reserve `skills:` for domain knowledge only |
| Subagent `skills:` array references non-existent SKILL.md | Loader silently skips; sub-agent quietly missing claimed capability | Author the missing skill, remove the reference, or correct the spelling (see auditing-subagents SA-13) |
| Hook running an LLM call | Hooks are deterministic, not for reasoning | Skill or subagent |
| Two sources of truth (same rule in CLAUDE.md and a skill) | Drift inevitable | Pick one; cross-reference |
| Sensitive credentials in CLAUDE.md or rules | Loaded into model context; visible in logs | External secret store; reference, don't include |
| `commands/*.md` instead of skills for new work | Misses bundling features | Skills with `disable-model-invocation: true` |
| Plugin bundling a single skill | Packaging overhead exceeds benefit | Direct skill commit |
| Plugin without version pinning by consumers | Cascading breakage on plugin updates | Pin via marketplace; document version compat |
| MCP server with `allowed-tools: *` | Overbroad permission surface | Scope to necessary tools |
| MCP server tool that mutates production data without `ask` permission | Unintended writes | Scope tools; require `ask` for mutations |
| Hook that silently rewrites Claude's output | Confuses the user; debugging nightmare | Hook should be visible (log to stderr) |
| Subagent reading 200+ files | Even with isolated context, the cost compounds | Narrow the search; iterative refinement |
| Rule that contradicts another rule | Model behavior unpredictable | Audit for conflicts; consolidate |
| Skill that duplicates official Claude Code docs | Drift as Claude Code evolves | Skill references docs; doesn't copy |
| `permissions.allow: ["Bash(*)"]` | No safety net | Explicit allow list; default-ask for unknowns |
| Hook with unhandled error | Blocks the tool call indefinitely | Hooks return promptly; explicit error handling |

## Decision frames

When the CC Designer faces a choice:

1. **What's the trigger?** Always-on / file-specific / user-invoked / model-invoked / lifecycle-event / external-service-driven. Trigger dictates primitive.
2. **What's the context cost?** Every CLAUDE.md line every request × team size × sessions per day = real tokens. Optimize the always-on cost.
3. **What's the failure mode?** Instruction failure (model didn't follow) vs. enforcement failure (hook crashed). Each has different mitigations.
4. **What's the share scope?** Single user / project team / org-wide / public. Drives scope choice and plugin decision.
5. **What's the evolution cadence?** High-velocity content (architecture changes weekly) belongs in skills (can be edited freely); stable content (engineering principles) belongs in CLAUDE.md or unconditional rules.

The Designer documents the choice and the rationale in the per-layer Design subsection.
