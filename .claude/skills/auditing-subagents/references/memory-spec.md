# Subagent Memory Specification

## Contents

- What subagent memory is (and isn't)
- Scopes and paths
- Loading behavior
- Hygiene checks
- Anti-patterns
- Cross-file implications

## What subagent memory is

A subagent declaring `memory: <scope>` gets a persistent directory it can read from and write to across spawns. This is **distinct** from auto memory (Claude's running summary) and CLAUDE.md (user-written project rules). It is also distinct from a session — subagent memory persists between sessions for a given subagent.

The directory contains:
- `MEMORY.md` — the index file, loaded into context at every subagent spawn (first 200 lines / 25 KB)
- Optional topic files referenced from MEMORY.md

The subagent writes to its memory itself, using `Write` or `Edit` tools (which it must have in `tools:` for this to work).

## Scopes and paths

| Scope | Directory | Committed? |
|---|---|---|
| `project` | `.claude/agent-memory/<name>/` | Yes (intended to ship with repo) |
| `local` | `.claude/agent-memory-local/<name>/` | **No — must be gitignored** |
| `user` | `~/.claude/agent-memory/<name>/` | n/a (user's home) |

A `<name>` mismatch — subagent declares `memory: project` but the directory `.claude/agent-memory/<wrong-name>/` exists — is silently treated as no-memory. INFO; the missing directory is created lazily on first write.

## Loading behavior

At each subagent spawn:
1. Subagent runner reads `<memory-dir>/MEMORY.md` (first 200 lines / 25 KB).
2. The content is prepended to the subagent's system prompt.
3. Topic files are NOT auto-loaded; the subagent reads them on demand via `Read`.

The 200-line / 25 KB cap is silent — content past it is dropped without warning.

## Hygiene checks

### Credential safety
The same scanner as auto memory (`scan_memory_secrets.py`) runs on the subagent memory directory. Any AKIA-prefix, `ghp_`, `sk-ant-api03-`, `sk-proj-`, or `BEGIN PRIVATE KEY` pattern is BLOCKER (security_critical=true) and produces SECURITY-BLOCK on the verdict.

### Size
- MEMORY.md > 200 lines or > 25 KB → MAJOR (content past cap silently dropped)
- Topic file > 500 lines → MINOR (expensive to read)

### Machine-local paths
Absolute paths like `/home/...`, `/Users/...`, `C:\\Users\\...` in committed memory (`project` scope) → MAJOR. These will break on other machines.

### Orphan topic files
Files in `<memory-dir>/topics/` not cited from MEMORY.md → MINOR.

### Stale topic references
MEMORY.md cites a topic file that doesn't exist on disk → MINOR.

## Anti-patterns specific to subagent memory

(See `references/anti-patterns.md` for the full subagent anti-pattern list; the memory-specific ones are summarized here.)

- **SAM-1: Credential capture** — subagent learned a credential and wrote it to MEMORY.md. BLOCKER + SECURITY-BLOCK.
- **SAM-2: Project-scope memory with machine-local content** — `memory: project` is committed; absolute paths leak personal info. MAJOR.
- **SAM-3: Local-scope memory not gitignored** — `memory: local` declared, but `.claude/agent-memory-local/` isn't in `.gitignore`. MAJOR.
- **SAM-4: Disallowed write tools** — subagent has `memory: project` but `disallowedTools:` blocks Write/Edit. The subagent can never update its memory. BLOCKER (cross-file check X20).
- **SAM-5: Cross-subagent contamination** — `<name>` collision between two subagents using the same memory directory. The memory accumulates content from both. MAJOR.

## Cross-file implications

When auditing a subagent, several checks span beyond the single file:

| Check | What it catches |
|---|---|
| X13 | Subagent declares `memory: local` but `.gitignore` doesn't cover `.claude/agent-memory-local/` |
| X20 | Subagent has memory: but disallowedTools: blocks Write/Edit |
| X21 | Orphan agent-memory directories — no subagent declares memory at the discovered path |
| X23 | `.claude/agent-memory-local/` exists or is referenced but not in `.gitignore` |
| X24 | MEMORY.md committed (under `.claude/agent-memory/`) contains machine-local paths |

These run in the coordinator's cross-file pass, not in this skill alone.

## Diagnostic commands

```
/memory
```

In an interactive Claude Code session, shows what's loaded. Subagent memory loads only when the subagent is spawned, so this command reveals it only mid-task.

For static audit, the auditor reads the on-disk state and infers what would load — the actual runtime cap might differ slightly depending on the subagent's spawn-time context.
