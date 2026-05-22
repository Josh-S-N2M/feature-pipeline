---
name: auditing-skills
description: >-
  Audits any Claude Code skill (a directory containing SKILL.md) or slash
  command (a file in .claude/commands/) for conformance to Anthropic's
  authoring spec, security risks, and AI-readability. ALWAYS invoke when
  reviewing, auditing, evaluating, scoring, vetting, fixing, improving,
  comparing, or critiquing existing skills or slash commands, when checking
  a SKILL.md before install, when triaging "why isn't my skill triggering,"
  or when a sub-agent is asked to assess skill quality. Produces a
  standardized audit report with a 100-point score across 10 dimensions
  and concrete fix suggestions. Report-only — does not modify the target.
allowed-tools: Read Grep Glob Bash(python3 *)
pedagogical_sections:
  - path: references/anti-patterns.md
    justification: "Skill anti-pattern reference catalog documenting what the auditing-skills scanner detects as findings"
  - path: references/security-checklist.md
    justification: "Skill security checklist; enumerates credential exfiltration patterns the auditor scans skills for"
  - path: references/common-failures.md
    justification: "Skill common-failures catalog with negative-example fixtures the auditing-skills scanners flag"
  - path: references/scripts-and-code.md
    justification: "Scripts-and-code reference; documents unsafe code patterns in skill scripts the auditor flags"
  - path: references/content-quality.md
    justification: "Skill content-quality reference; documents low-quality SKILL.md patterns the auditor flags"
  - path: references/descriptions-and-triggering.md
    justification: "Skill descriptions+triggering reference; documents the SA-2-equivalent vague-description anti-patterns"
  - path: references/frontmatter-spec.md
    justification: "Skill frontmatter spec reference; contains anti-pattern examples of invalid frontmatter the auditor flags"
  - path: examples/bad-skill-annotated.md
    justification: "Bad-skill annotated negative-example fixture; multiple anti-patterns illustrated for scanner training"
---

# Auditing Claude Code Skills

This skill audits Claude Code skills (directories with SKILL.md) and slash commands (`.claude/commands/<name>.md`). It produces a standardized audit report with a 100-point score across 10 dimensions and concrete fix suggestions.

It does not modify the audited target. It writes one file: an audit report.

This skill is part of the **auditing-cc-configs** family. The shared rubric, severity weights, verdict thresholds, pedagogical-marker spec, and triage protocol live in the coordinator skill's `references/`. When `auditing-cc-configs` is installed alongside, this skill defers to it for shared rules. When standalone, this skill ships its own copies (kept in sync).

## The audit loop

Follow these steps in order. This is a standing instruction — keep working through them across turns even if context is summarized.

1. **Locate the skill.** The user supplies a path (e.g. `~/.claude/skills/some-skill/`). Confirm `SKILL.md` exists at that path. If it doesn't, the target isn't a skill — stop and say so.

2. **Run the deterministic checks.** Execute:

   ```bash
   python3 ${CLAUDE_SKILL_DIR}/scripts/audit_skill.py <path-to-skill>
   ```

   This produces JSON with frontmatter validity, reference integrity, security pattern hits, line counts, and orphaned files. Read the JSON. These checks catch the silent-failure class of problems (broken YAML, dead links, hidden injection patterns) more reliably than reading prose.

3. **Read the skill itself.** Open `SKILL.md`. Then open every file referenced from it. Then check `scripts/`, `assets/`, `examples/` for files the script flagged as orphaned.

4. **Verify each script-derived MAJOR or BLOCKER before promoting it.** The deterministic scripts are pattern-matchers; they give you a *location* and a *hypothesis*. Before any script finding makes it into the report at MAJOR or BLOCKER severity, open the cited file and ask: *does the property the script asserts actually hold here?* — not just *did the regex match?*

   Example: the link-integrity check might flag a backticked filesystem path like `.<dotdir>/settings.json` as a broken reference because it doesn't exist in the skill bundle. Open the file. If it's filesystem-path documentation about user projects, the property "this is a broken bundle reference" doesn't hold. Drop the finding and note the false-positive class in the report's Notes section.

   Example: the security scanner might flag a credential-shaped env var name (something like `$<API_KEY_NAME>`) in `references/security-checklist.md`. Open the file. If the credential string appears inside a deny-list example or a "what to look for" catalog, the property "this skill reads the credential" doesn't hold. Drop, note as pedagogical.

   Example: the TOC check might fire on a long file. Open the file. If the first 30 lines contain a heading-style index (under any of the recognized headings, or as a bullet list of cross-references), the property "navigable index is missing" doesn't hold. Drop.

   This step is non-optional. Skipping it produces reports with false-positive MAJOR/BLOCKERs that erode the audit's credibility. The script's job is to surface candidates; the agent's job is to confirm or refute the property each one asserts. When form (regex match) and function (the property being asserted) diverge, function wins.

5. **Score each dimension.** For each of the 10 dimensions in the rubric, read the relevant reference file, apply its criteria, and record findings. Use the routing table below to pick the right reference.

6. **Compose findings.** Each finding has: dimension number, severity (BLOCKER / MAJOR / MINOR / NIT), location (file + line if known), what's wrong, and a concrete fix suggestion. "Improve description" is not a fix; "replace description with: …" is.

7. **Compute the verdict.** Use the scoring rules in `references/audit-rubric.md`.

8. **Write the report.** Use `assets/audit-report-template.md` as the skeleton. Save as `audit-report-<skill-name>.md` in the current working directory.

   For long audits, copy `assets/audit-checklist.md` into your working response and check off items as you finish them — it helps survive context summaries.

9. **Halt on security blocks.** If `scripts/scan_security.py` returned any CRITICAL pattern hit *that survived the verification step in step 4*, the verdict is `SECURITY-BLOCK` regardless of other dimensions. Surface this immediately at the top of the report and recommend the user not install or invoke the skill until reviewed by a human.

## Routing table

When auditing each dimension, read the corresponding reference file. Each file is focused — read only what you need.

| # | Dimension | Reference file |
|---|---|---|
| 1 | Discoverability | `references/descriptions-and-triggering.md` |
| 2 | Frontmatter validity | `references/frontmatter-spec.md` |
| 3 | Token economy | `references/content-quality.md` |
| 4 | Progressive disclosure | `references/progressive-disclosure.md` |
| 5 | Instruction quality | `references/content-quality.md` |
| 6 | Workflow soundness | `references/workflows-and-feedback.md` |
| 7 | Script hygiene | `references/scripts-and-code.md` |
| 8 | Security posture | `references/security-checklist.md` |
| 9 | Anti-pattern absence | `references/anti-patterns.md` |
| 10 | Agent-fit | `references/content-quality.md` |

For the master scoring rules and verdict thresholds, see `references/audit-rubric.md`.

For symptoms that don't fit a single dimension (silent triggering failures, YAML traps, token-budget overflow), see `references/common-failures.md`.

## When in doubt about a finding

Read the calibration examples:

- `examples/good-skill-annotated.md` — a small skill that scores 95/100 with annotations on what makes it good
- `examples/bad-skill-annotated.md` — a small skill that scores 35/100 with annotations on each problem

If the audited skill does what `examples/good-skill-annotated.md` does, that's not a finding. If it does what `examples/bad-skill-annotated.md` does, that is.

## Report-only contract

This skill never modifies the audited skill. The audit report contains fix suggestions, but applying them is the user's or another agent's job. Do not Edit, Write, or rewrite files inside the audited skill directory under any circumstance. The only file this skill produces is the audit report in the current working directory.

## Severity meanings (v2)

- **BLOCKER** — the skill is broken or dangerous. Won't load, won't trigger, or has a security issue. Verdict cannot be PASS. Each BLOCKER zeros one dimension AND applies a flat −12 penalty to the total. Confirmed CRITICAL produces SECURITY-BLOCK regardless of score.
- **MAJOR** — the skill works but has a problem that meaningfully degrades behavior (vague description, bloated body, orphan files, missing exclusions). −5 from the dimension.
- **MINOR** — the skill works fine but deviates from spec or best practice. −2.
- **NIT** — taste or polish. −0.5.

Verdict thresholds: PASS 95+, PASS-WITH-MINOR-FIXES 85–94, NEEDS-WORK 70–84, FAIL <70.

## Scope of "target"

This skill audits two target types:

1. **Skills** — a directory with `SKILL.md` containing YAML frontmatter and Markdown body, optionally with `references/`, `scripts/`, and `assets/`. Spec: `code.claude.com/docs/en/skills` and `docs.claude.com/en/docs/agents-and-tools/agent-skills`.

2. **Slash commands** — `.claude/commands/<name>.md` (project) or `~/.claude/commands/<name>.md` (user). Same frontmatter shape as skills but no `references/`/`scripts/` subdirectory. The body becomes the prompt template invoked by `/<name>`.

Not in scope: `.claude/agents/*.md` subagents (different field set — `tools:` not `allowed-tools:`), settings, hooks, MCP servers, CLAUDE.md, memory. Route those to the corresponding sibling skill in the auditing-cc-configs family.
