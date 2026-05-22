# Auto Memory Anti-Patterns

The 10 named anti-patterns specific to auto memory at `~/.claude/projects/<id>/memory/`. Use when scoring dimension 9 (auto-memory hygiene).
## Contents

- AM-1 through AM-10
- Detection map
- What good and bad auto memory look like


These are different from CLAUDE.md anti-patterns because auto memory is Claude-written, not user-written. The tone and structure are subject to different rules.

```audit-example -- anti-pattern catalog demonstrating scanner-flagged content; documents what the auditor scanner detects
This file is illustrative — it describes patterns the auditor detects.
```

## AM-1: The Log — MAJOR

Symptom: MEMORY.md is a chronological log of every action.

Why bad: Indices, not logs. The first 200 lines should be the most current summary, not the earliest history.

Fix: User invokes `/memory prune` to reset, then asks Claude to write a concise current-state summary.

## AM-2: Credential Capture — BLOCKER (security_critical)

Symptom: MEMORY.md contains "We use the GitHub token ghp_xxx..." or any literal credential value.

Why bad: Claude wrote the credential into a local file. If the user asked Claude to "remember" a credential, Claude should refuse — but if it didn't, the credential is now persisted to disk.

Fix: Delete the credential from MEMORY.md. Rotate it. Tell Claude not to remember credentials.

## AM-3: Stale Project File References — MINOR

Symptom: MEMORY.md cites a project file but the file was deleted/renamed. For example, a citation like the one shown here:

```audit-example -- anti-pattern catalog demonstrating scanner-flagged content; documents what the auditor scanner detects
We use the authentication helper in src/auth.py to validate JWTs.
```

If that file was renamed or moved, the citation is stale.

Why bad: Misleading. Future Claude reads MEMORY.md and tries to apply rules to a non-existent file.

Fix: User invokes `/memory edit` or asks Claude to rewrite MEMORY.md from current state.

## AM-4: Orphan Topic Files — MINOR

Symptom: a topic file exists in `memory/topics/` but is not cited from MEMORY.md. For example:

```audit-example -- anti-pattern catalog demonstrating scanner-flagged content; documents what the auditor scanner detects
File system:
  memory/MEMORY.md          (no reference to topics/api-changes.md)
  memory/topics/api-changes.md  (orphan)
```

Why bad: Topic file isn't loaded (it's read on-demand based on MEMORY.md citations). Effectively dead.

Fix: Either cite from MEMORY.md or delete.

## AM-5: Machine-Local Paths — MAJOR

Symptom: MEMORY.md contains `/home/alice/...`, `/Users/bob/...`, `C:\\Users\\...`.

Why bad: Useless on other machines. If MEMORY.md is ever shared (intentionally or accidentally), it breaks.

Fix: Rewrite citations as relative paths.

## AM-6: Oversized MEMORY.md — MAJOR

Symptom: MEMORY.md > 200 lines or > 25 KB.

Why bad: Content past the cap is silently dropped at session load. The most recent content (if appended) is likely lost.

Fix: User invokes `/memory prune` or rewrites the file under the cap. Move detailed content to `topics/` files.

## AM-7: Topic File Bloat — MINOR

Symptom: A single topic file > 500 lines.

Why bad: Claude must read the whole topic file when MEMORY.md cites it. Long topic files are expensive on-demand reads.

Fix: Split into multiple topic files.

## AM-8: Mixed Languages in Index — MINOR

Symptom: MEMORY.md alternates between English narrative and code snippets at high frequency.

Why bad: MEMORY.md should be index-density (summaries, citations, brief signposts). Long code snippets belong in topic files.

Fix: Move code to topic files; cite topic files from MEMORY.md.

## AM-9: Auto-memory Override of User Rules — MAJOR

Symptom: MEMORY.md contains "Always do X" where X contradicts a CLAUDE.md rule.

Why bad: Claude may have learned a workaround that contradicts the team's preferred approach. CLAUDE.md is canonical; MEMORY.md is local and per-machine.

Fix: User reviews MEMORY.md and either (a) revises the canonical project context file (if the auto-memory rule is correct) or (b) invokes `/memory edit` to remove the contradicting line.

## AM-10: Cross-project Bleed — MAJOR

Symptom: MEMORY.md references projects, files, or people not in the current project.

Why bad: Indicates either a project-id derivation bug, or that Claude has accidentally mixed contexts. Either way, the memory is wrong for this project.

Fix: User invokes `/memory prune` and asks Claude to rebuild from current state.

## Detection map

| Pattern | Detected by |
|---|---|
| AM-1 | content-quality heuristics (timestamp prefix, "I did X then Y then Z" structure) |
| AM-2 | `scripts/scan_memory_secrets.py` |
| AM-3 | `scripts/check_auto_memory.py` (path-citation cross-check) |
| AM-4 | `scripts/check_auto_memory.py` (orphan topic check) |
| AM-5 | `scripts/check_auto_memory.py` (path pattern check) |
| AM-6 | `scripts/check_auto_memory.py` (size/byte check) |
| AM-7 | `scripts/check_auto_memory.py` (per-file size check) |
| AM-8 | agent judgment after reading the file |
| AM-9 | cross-file check X19 (memory ↔ CLAUDE.md duplicate/contradict) |
| AM-10 | agent judgment after reading the file |

## What good auto memory looks like

A few dozen lines. Each section heading is a topic the project encountered. Each section is 3–8 lines summarizing what was learned, plus a citation to a topic file for detail. No credentials. No absolute paths. References that all resolve.

See the "Good MEMORY.md" section at the top of `examples/bad-memory-annotated.md`.

## What bad auto memory looks like

500-line chronological log. Mixed in are credentials, absolute paths, references to files that no longer exist, and contradictions with the team's CLAUDE.md.

See the "Bad MEMORY.md" section in `examples/bad-memory-annotated.md`.
