---
name: auditing-context-files
description: >-
  Audits Claude Code context files — CLAUDE.md, CLAUDE.local.md, .claude/rules/
  files, and auto memory at ~/.claude/projects/[project-id]/memory/. ALWAYS
  invoke when reviewing, auditing, evaluating, scoring, vetting, fixing, or
  critiquing these files, when triaging "Claude isn't following my
  instructions," or when a sub-agent is asked to assess context-file quality.
  Validates @-imports (depth, cycles), content quality, anti-patterns, rules
  paths globs, auto memory size/freshness, and credential safety. Produces a
  standardized audit report with 100-point score across 10 dimensions and
  concrete fixes. Report-only — does not modify the audited files.
allowed-tools: Read Grep Glob Bash(python3 *)
pedagogical_sections:
  - path: references/anti-patterns.md
    justification: "Anti-pattern catalog documenting CLAUDE.md content the auditing-context-files scanner flags"
  - path: references/auto-memory-antipatterns.md
    justification: "Auto-memory anti-pattern reference catalog; documents what the AM-1 through AM-3 scanners detect"
  - path: references/content-quality.md
    justification: "Content-quality reference documenting low-quality CLAUDE.md patterns the auditor flags"
  - path: references/common-failures.md
    justification: "Common-failures catalog with negative-example fixtures the auditing-context-files scanners flag"
  - path: references/claude-md-spec.md
    justification: "CLAUDE.md spec reference; contains anti-pattern catalog illustrating what the auditor detects"
  - path: references/auto-memory-spec.md
    justification: "Auto-memory spec reference; documents credential patterns the scan_memory_secrets scanner detects"
  - path: examples/bad-claude-md-annotated.md
    justification: "Bad-CLAUDE.md annotated negative-example fixture; multiple anti-patterns documented for scanner training"
  - path: examples/bad-memory-annotated.md
    justification: "Bad-memory annotated negative-example fixture; multiple anti-patterns documented for AM-* scanner training"
---

# Auditing Context Files

Audits the three classes of files that load into Claude Code's context on every session start:

1. **CLAUDE.md** and **CLAUDE.local.md** — user-written project instructions
2. **`.claude/rules/*.md`** — user-written conditional rules
3. **Auto memory** at `~/.claude/projects/<project-id>/memory/` — Claude-written summaries

This skill is part of the **auditing-cc-configs** family. The shared rubric, severity weights, and verdict thresholds live in the coordinator skill's `references/`. When the coordinator is installed alongside, this skill defers to it; when standalone, this skill ships its own copies (kept in sync).

It does not modify the audited files. It writes one file: an audit report.

## The audit loop

1. **Locate the target.** Either a single context file or a project containing `.claude/` plus optionally the auto-memory directory.

2. **Run deterministic checks:**

   ```bash
   python3 ${CLAUDE_SKILL_DIR}/scripts/audit_context_file.py <path>
   ```

   Dispatches by file type: CLAUDE.md → content quality + @-import resolution; rules/ → paths glob validation; auto memory → size + secrets + staleness.

3. **Apply verification step** — script findings must be confirmed against the file before being promoted to the report (see the audit rubric in the coordinator skill).

4. **Run pedagogical-marker prefilter** if the target declares `pedagogical_sections:`.

5. **Compute verdict and write report.**

## Routing table — dimensions

| # | Dimension | Reference |
|---|---|---|
| 1 | Size & density | `references/claude-md-spec.md` |
| 2 | @-import integrity | `references/claude-md-spec.md` |
| 3 | Content quality | `references/content-quality.md` |
| 4 | Anti-pattern absence | `references/anti-patterns.md` |
| 5 | Rules scope correctness | `references/rules-spec.md` |
| 6 | Security (credentials/secrets) | `references/auto-memory-spec.md`, `references/common-failures.md` |
| 7 | Staleness | `references/content-quality.md` |
| 8 | Structure | `references/claude-md-spec.md` |
| 9 | Auto-memory hygiene | `references/auto-memory-spec.md`, `references/auto-memory-antipatterns.md` |
| 10 | Layering interactions | `references/common-failures.md` |

For symptoms not fitting a single dimension, see `references/common-failures.md`.

## Three context-file types

This skill audits three file classes with different rules. The dispatcher picks the right rule set.

### CLAUDE.md / CLAUDE.local.md / .claude/CLAUDE.md

User-written. Loaded every session. Subject to the 200-line guideline, @-import depth ≤ 5, and the 15 named anti-patterns. CLAUDE.local.md must be in .gitignore.

### .claude/rules/*.md

Conditional rules — load when `paths:` frontmatter glob matches files in the current task. Subject to glob validation, scope-correctness checks, and content-quality checks.

### Auto memory at ~/.claude/projects/<project-id>/memory/

Claude-written. Loaded every session up to 200 lines / 25KB. Per-project, per-worktree. The MEMORY.md is the index; topic files are referenced from it. Subject to size limits, credential scanning, staleness (orphan topic refs), and machine-local-path checks.

The `<project-id>` is derived from the git repo root path (or working directory if no git). For audit purposes, the auditor computes this from the project's filesystem state.

## Severity meanings (v2)

- **BLOCKER** — file is broken (parse fail), dangerous (secrets in MEMORY.md), or makes Claude actively misbehave. Verdict cannot be PASS. −12 per dim + −12 flat.
- **MAJOR** — works but degrades behavior (CLAUDE.md over 200 lines, stale auto-memory topic refs). −5.
- **MINOR** — deviates from best practice. −2.
- **NIT** — taste or polish. −0.5.

Verdict thresholds: PASS 95+, PASS-WITH-MINOR-FIXES 85–94, NEEDS-WORK 70–84, FAIL <70. SECURITY-BLOCK on confirmed CRITICAL.

## Scope

In scope: CLAUDE.md, CLAUDE.local.md, .claude/CLAUDE.md, .claude/rules/*.md, ~/.claude/projects/<id>/memory/MEMORY.md, ~/.claude/projects/<id>/memory/topics/*.md.

Not in scope: subagent persistent memory at `.claude/agent-memory/*` (route to `auditing-subagents`). settings.json, hooks, MCP, output styles, skills, slash commands (route to their respective sibling skills).

## Calibration examples

When in doubt about whether a finding is real, compare against:

- [`examples/good-claude-md-annotated.md`](examples/good-claude-md-annotated.md) — a CLAUDE.md that scores 95+
- [`examples/bad-claude-md-annotated.md`](examples/bad-claude-md-annotated.md) — a CLAUDE.md with embedded credentials and contradictions (SECURITY-BLOCK)
- [`examples/bad-memory-annotated.md`](examples/bad-memory-annotated.md) — auto memory examples (good and bad)

If the audited file does what the good example does, that's not a finding. If it does what the bad examples do, it is.

## Report-only contract

This skill never modifies the audited files. The report contains fix suggestions, but applying them is the user's or another agent's job.
