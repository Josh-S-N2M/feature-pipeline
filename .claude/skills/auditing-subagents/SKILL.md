---
name: auditing-subagents
description: >-
  Audits Claude Code subagents — files at .claude/agents/[name].md or
  ~/.claude/agents/[name].md — and their persistent memory directories at
  .claude/agent-memory/, .claude/agent-memory-local/, ~/.claude/agent-memory/.
  ALWAYS invoke when reviewing, auditing, evaluating, scoring, vetting,
  fixing, or critiquing existing subagents, when checking a subagent before
  install, or when a sub-agent is asked to assess subagent quality. Validates
  frontmatter (tools, model alias, memory scope), description routing
  quality, body content, persistent memory hygiene including credential
  safety, and safety-model adherence. Report-only — does not modify.
allowed-tools: Read Grep Glob Bash(python3 *)
pedagogical_sections:
  - path: references/anti-patterns.md
    justification: "Subagent anti-pattern reference catalog documenting what the SA-1 through SA-12 scanners detect"
  - path: references/safety-model.md
    justification: "Subagent safety-model reference; documents bypass-approval and prompt-injection patterns the auditor scans for"
  - path: references/common-failures.md
    justification: "Subagent common-failures catalog with negative-example fixtures the auditing-subagents scanners flag"
  - path: examples/bad-subagent-annotated.md
    justification: "Bad-subagent annotated negative-example fixture; multiple anti-patterns illustrated for scanner training"
---

# Auditing Claude Code Subagents

Audits Claude Code subagent definitions and their persistent memory. Subagents are autonomous Claude instances delegated to handle specific tasks; their definition files use a *different* frontmatter schema from skills (`tools:` not `allowed-tools:`) — this is the most common confusion this skill addresses.

This skill is part of the **auditing-cc-configs** family. The shared rubric, severity weights, verdict thresholds, pedagogical-marker spec, and triage protocol live in the coordinator skill's `references/`. When standalone, this skill ships compatible copies.

It does not modify the audited subagent. It writes one file: an audit report.

## The audit loop

1. **Locate the target.** Either a subagent definition file (`.claude/agents/<name>.md` or `~/.claude/agents/<name>.md`) or a subagent memory directory (`.claude/agent-memory/<name>/`, etc.).

2. **Run deterministic checks:**

   ```bash
   python3 ${CLAUDE_SKILL_DIR}/scripts/audit_subagent.py <path>
   ```

3. **Apply verification step** — every script finding must be confirmed by reading the file before being promoted in the report.

4. **Run pedagogical-marker prefilter** if `pedagogical_sections:` is declared.

5. **Compute verdict and write report.**

## Routing table — dimensions

| # | Dimension | Reference |
|---|---|---|
| 1 | Frontmatter validity | `references/subagent-spec.md` |
| 2 | Description routing | `references/description-quality.md` |
| 3 | Tool scoping | `references/subagent-spec.md` |
| 4 | Body quality | `references/description-quality.md` |
| 5 | Memory configuration | `references/memory-spec.md` |
| 6 | Safety model adherence | `references/safety-model.md` |
| 7 | Anti-pattern absence | `references/anti-patterns.md` |
| 8 | Model selection | `references/subagent-spec.md` |
| 9 | Skills field cost | `references/subagent-spec.md` |
| 10 | Agent-fit | `references/description-quality.md` |

For cross-cutting symptoms, see `references/common-failures.md`.

## Critical: subagents use `tools:`, not `allowed-tools:`

The single most common mistake when auditing subagents is to flag `tools:` as wrong because that's the *skills* field. Subagents have their own schema — `tools:` is the correct field for them. Flagging it is a false positive. The auditor's frontmatter validator handles this via the `AUDIT_TARGET_TYPE=subagent` environment variable.

## Three memory concepts (subagents only own #3)

Claude Code uses "memory" for three different mechanisms. This skill audits only #3 — subagent persistent memory. The other two are audited by `auditing-context-files`.

| # | What | Audited by |
|---|---|---|
| 1 | CLAUDE.md / rules | auditing-context-files |
| 2 | Auto memory (`~/.claude/projects/<id>/memory/`) | auditing-context-files |
| 3 | Subagent persistent memory (`.claude/agent-memory[-local]/<name>/`) | This skill |

If asked to audit CLAUDE.md or auto memory, decline and route to `auditing-context-files`.

## Subagent memory scopes

Subagent memory has three possible scopes (declared by the subagent's frontmatter `memory:` field):

| Scope | Path | Committed? | Gitignored? |
|---|---|---|---|
| `project` | `.claude/agent-memory/<name>/` | yes | no |
| `local` | `.claude/agent-memory-local/<name>/` | no | **must be** |
| `user` | `~/.claude/agent-memory/<name>/` | n/a (user home) | n/a |

A subagent declaring `memory: local` without `.claude/agent-memory-local/` in `.gitignore` is a leak vector. Cross-file check X23 detects this.

## Severity meanings (v2)

- **BLOCKER** — subagent won't load, has security issue, or actively misbehaves. −12 per dim + −12 flat.
- **MAJOR** — works but degrades behavior.
- **MINOR** — deviates from best practice.
- **NIT** — taste or polish.

Verdict thresholds: PASS 95+, PASS-WITH-MINOR-FIXES 85–94, NEEDS-WORK 70–84, FAIL <70. SECURITY-BLOCK overrides on confirmed CRITICAL.

## Calibration examples

When in doubt, compare against:

- [`examples/good-subagent-annotated.md`](examples/good-subagent-annotated.md) — a subagent scoring 95+
- [`examples/bad-subagent-annotated.md`](examples/bad-subagent-annotated.md) — multiple issues, SECURITY-BLOCK

## Scope

In scope: `.claude/agents/<name>.md`, `~/.claude/agents/<name>.md`, subagent persistent memory at all three scopes.

Not in scope: skills (SKILL.md), CLAUDE.md, hooks, settings, MCP, output styles, slash commands. Route to the corresponding sibling skill.

## Report-only contract

This skill never modifies the audited subagent or its memory. The report contains fix suggestions, but applying them is the user's or another agent's job.
