# Auto Memory Specification

Authoritative reference for Claude's auto-memory mechanism at `~/.claude/projects/<project-id>/memory/`. Use when scoring dimensions 6 (security), 7 (staleness), and 9 (auto-memory hygiene).
## Contents

- What auto memory is
- Storage location and project-id
- Loading behavior
- File hygiene checks
- Anti-patterns
- Per-worktree behavior


## Source

`code.claude.com/docs/en/memory#automatic-memory`, last verified 2026-05.

## What it is

Auto memory is Claude's own running summary of work done in a given project. Unlike CLAUDE.md (user-written, version-controlled), auto memory is **written by Claude itself** and stored locally per machine. Claude updates it when it finishes a task or when the user invokes `/memory save`.

## Storage location

```
~/.claude/projects/<project-id>/memory/
├── MEMORY.md           # The index — concise summary
└── topics/             # Optional topic files referenced from MEMORY.md
    ├── api-changes.md
    ├── architecture.md
    └── ...
```

The `<project-id>` is derived from the **git repo root path** (or the working directory if not in a git repo). Each worktree maps to its own project-id, so per-worktree auto memory is isolated.

## Loading behavior

At session start, Claude loads MEMORY.md into context — but only:

- The **first 200 lines** OR
- The **first 25 KB**, whichever comes first.

Topic files in `topics/` are **referenced** by MEMORY.md but **not auto-loaded**. Claude reads them on-demand if MEMORY.md cites them and the current task needs the detail.

## The `autoMemoryDirectory` setting

A user-scope setting in `~/.claude/settings.json`:

```json
{
  "autoMemoryDirectory": "~/my-custom-memory-location"
}
```

**This setting only takes effect at user scope.** Setting it in project or local settings.json is silently ignored. Cross-file check X22 catches this.

## File hygiene

### Size limits

| Condition | Severity |
|---|---|
| MEMORY.md > 200 lines or > 25 KB | MAJOR — content past the cap is silently dropped |
| MEMORY.md ≥ 195 lines | MINOR — approaching cap |
| Single topic file > 500 lines | MINOR — Claude may struggle to digest in one read |

### Credential safety

Auto memory is on disk and may be backed up, synced, or copied by the user. **Credentials must never appear in MEMORY.md or topic files.** The `scripts/scan_memory_secrets.py` script catches:

- AKIA-prefixed AWS access key IDs (non-EXAMPLE)
- `github_pat_…`, `ghp_…`, `gho_…` GitHub tokens
- `sk-ant-api03-…` Anthropic API keys
- `sk-proj-…` OpenAI keys
- SSH RSA/Ed25519/EC private key markers
- Generic password/secret patterns next to identifier patterns

Any match = BLOCKER, security_critical=true → SECURITY-BLOCK on the verdict.

### Machine-local paths

Absolute paths like `/home/alice/...`, `/Users/bob/...`, `C:\\Users\\carol\\...` are machine-local. If MEMORY.md is somehow committed (or shared), these break for other users. MAJOR.

### Orphan topic-file references

If MEMORY.md cites a topic-file path that doesn't exist on disk, the reference is stale. Example pattern:

```audit-example -- specification reference with anti-pattern examples demonstrating scanner-flagged content; documents what the auditor scanner detects
MEMORY.md says:    "See topics/api-changes.md for migration details."
On disk:           memory/topics/  (no api-changes.md)
```

Result: MINOR finding "stale topic reference."

A topic file that exists in `topics/` but no MEMORY.md citation → orphan. MINOR.

### Stale references to project files

If MEMORY.md cites a project source file but the file has been moved or deleted, the citation goes stale. Example pattern:

```audit-example -- specification reference with anti-pattern examples demonstrating scanner-flagged content; documents what the auditor scanner detects
MEMORY.md says:    "The auth helper at src/auth.py validates JWTs."
On disk:           src/auth/  (auth.py was split into multiple files)
```

Result: MINOR finding "stale project-file citation."

## Anti-patterns

See `references/auto-memory-antipatterns.md` for the 10 named anti-patterns (AM1–AM10).

## What good auto memory looks like

- MEMORY.md is a concise index — section headings, brief summaries, citations to topic files.
- Topic files cover one bounded topic each.
- No credentials, no machine-local paths.
- Stable references (topic-file paths exist, project-file citations resolve).
- Under 200 lines / 25KB.

## What bad auto memory looks like

- MEMORY.md is a 1000-line stream-of-consciousness log.
- Credentials embedded ("the GH token is ghp_xxx...").
- References to files that no longer exist.
- Topic files that nothing in MEMORY.md cites.

## Per-worktree behavior

Each git worktree gets its own project-id, so:

- `myproject/` and `myproject-feature-branch/` (worktree) have **separate** auto memories.
- This is the right behavior — they may have diverged context.
- But it means moving from one worktree to another loses the other's memory.

The auditor can detect multiple project-ids that share the same `git remote -v` origin and flag them as related (informational).

## Verification commands

```
/memory
```

Shows what auto memory loaded for the current session, including any byte/line truncation.

## Implementation note

The `scripts/check_auto_memory.py` script handles size checks, byte counts, topic-file orphan detection, and file-existence cross-checks. The `scripts/scan_memory_secrets.py` is the canonical credential scanner shared with `auditing-subagents` (for subagent persistent memory).
