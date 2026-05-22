# Common Failures — Context Files

Cross-cutting failure modes that don't fit a single dimension. This is the routing-to-coordinator reference; for the full mental model, see the coordinator skill's `references/common-failures.md`.
## Contents

- The three memory concepts
- Loading-order surprises
- Diagnostic flow for missing rules
- Auto memory vs CLAUDE.md conflicts
- Diagnostic commands


## The three memory concepts

Claude Code uses "memory" for three different mechanisms. The auditor keeps them separate:

| # | Concept | Written by | Location | Audited by |
|---|---|---|---|---|
| 1 | CLAUDE.md / rules | User | Project / `.claude/rules/` / user home | This skill |
| 2 | Auto memory | Claude | `~/.claude/projects/<id>/memory/` | This skill |
| 3 | Subagent persistent memory | Subagent | `.claude/agent-memory[-local]/` | `auditing-subagents` |

Confusion between #1 and #2 is common. Symptoms:

- "I edited MEMORY.md and Claude still got it wrong" — they edited auto memory, but the rule belongs in the canonical project context file (which is version-controlled and shared).
- "Why is Claude making the same mistake again?" — auto memory may not be current; the canonical context file may need the rule.
- "I want to share memory with my team" — only CLAUDE.md is shareable; auto memory is per-machine.

## Loading-order surprises

Files load in this order (additively for CLAUDE.md, conditional for rules, loaded-once-per-session for auto-memory):

1. `~/.claude/CLAUDE.md` (user-global)
2. `<project>/CLAUDE.md`
3. `<project>/.claude/CLAUDE.md`
4. `<project>/CLAUDE.local.md`
5. Matching `.claude/rules/*.md` (per task)
6. `~/.claude/projects/<id>/memory/MEMORY.md` (first 200 lines / 25 KB)
7. Managed `claudeMd:` injection (if set)

Layer 4 must be in `.gitignore`. Layer 5 is conditional. Layer 6 is local-only.

## The "Claude isn't following my CLAUDE.md" diagnostic flow

1. Run `/memory` inside Claude Code. Does CLAUDE.md show up in the loaded list?
   - **No:** parse error, BOM, or location mismatch. Run `validate_frontmatter.py` analog.
   - **Yes, but content is wrong:** check for contradictions, aspirational language.
2. Is the relevant rule actually in CLAUDE.md, or is it in `MEMORY.md`?
   - If in MEMORY.md only, it may have been silently pruned past the 200-line cap.
3. Check `.claude/rules/`. Is there a rule with a `paths:` glob that overrides CLAUDE.md content?

## When auto memory disagrees with CLAUDE.md

CLAUDE.md is canonical. If auto memory says X but CLAUDE.md says not-X, Claude is likely to follow CLAUDE.md when CLAUDE.md is more specific, but may follow auto memory when the rule was learned through recent task experience. This is non-deterministic and a known failure mode.

Audit MAJOR with note "auto memory rule may contradict CLAUDE.md; user should reconcile."

## The "missing import" silent failure

`@docs/architecture.md` resolves to a missing file → empty include, no error. Claude proceeds with empty content where the user thought it had the architecture document. The audit detects this with `validate_at_imports.py`.

## The "wrong project-id" puzzle

A worktree of the same git repo gets a different project-id. The user's auto memory from `main` worktree isn't available in the `feature-x` worktree. This is by design (worktrees may have diverged) but surprises users.

Audit: if multiple project-id directories exist under `~/.claude/projects/` for the same git remote, note as INFO ("multiple worktrees detected, each with separate auto memory").

## Diagnostic commands

| Command | Surfaces |
|---|---|
| `/memory` | What's actually loaded |
| `/memory edit` | Open MEMORY.md for editing |
| `/memory prune` | Reset auto memory |
| `/doctor` | Configuration parse errors, missing files |
