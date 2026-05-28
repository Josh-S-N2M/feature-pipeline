---
name: auditing-cc-configs
description: >-
  Audits Claude Code configuration end-to-end — skills, slash commands,
  CLAUDE.md, rules, auto memory, subagents (and their memory), hooks,
  settings.json (all scopes), output styles, MCP servers. ALWAYS invoke
  when reviewing, auditing, evaluating, scoring, vetting, fixing,
  improving, or critiquing any part of a project's .claude/ tree or
  Claude Code configuration. Use when triaging "is my Claude Code setup
  correct?" or when a cc-critique subagent is asked to evaluate a
  blueprint. Produces a project-level report with verdict and prioritized
  fixes across 24 cross-file checks plus per-primitive audits. Report-only.
allowed-tools: Read Grep Glob Bash(python3 *)
pedagogical_sections:
  - path: references/cross-file-checks.md
    justification: "Cross-file-check reference documenting the X1-X12 cross-primitive audit patterns (negative examples)"
  - path: references/common-failures.md
    justification: "Common-failures catalog with negative-example fixtures the auditing-cc-configs scanners flag"
  - path: references/audit-rubric.md
    justification: "Audit-rubric reference catalog enumerating finding severities the auditor emits (scoring guide)"
  - path: references/triage-protocol.md
    justification: "Triage-protocol reference documenting how marker-bearing findings are demoted (scanner training fixture)"
  - path: references/pedagogical-marker-spec.md
    justification: "Pedagogical-marker spec reference documenting the marker format itself; contains anti-laundering examples"
  - path: references/additive-vs-override.md
    justification: "Additive-vs-override reference documenting the additive-settings anti-pattern auditor scanner detects"
  - path: assets/triage-prompt.txt
    justification: "Triage prompt template; contains negative-example credential strings used as anti-pattern training"
---

# Auditing Claude Code Configurations

This is the coordinator for the auditing-cc-configs skill family. It detects what's being audited, dispatches to the right sub-skill, runs cross-file pair checks, triages findings through an LLM judge, and writes a single report.

It does not modify any audited file. It writes one file: an audit report.

## The audit loop

For **project-level audits** (a directory with `.claude/`), Claude can run the entire 9-step loop in one shot using the project walker:

```bash
python3 ${CLAUDE_SKILL_DIR}/scripts/audit_project.py <project-root> [--with-runtime] [--managed] [--json]
```

The walker discovers every primitive, dispatches each to its sub-skill auditor, runs the 24 cross-file checks, computes the verdict, and writes a Markdown report to `<project-root>/project-audit-report.md`. Add `--json` for a structured sidecar.

For **single-target audits** (one file, e.g. just an SKILL.md), or when finer control is needed, follow the manual steps below.

### Manual step-by-step (when not using the walker)

Follow these steps in order. This is a standing instruction — keep working through it across turns even if context is summarized.

1. **Locate the target.** The user supplies a path. If the path is a directory containing `.claude/`, this is a project audit. If it's a single file, it's a single-target audit. If neither, stop and clarify.

2. **Run deterministic dispatch and per-primitive scans:**

   ```bash
   python3 ${CLAUDE_SKILL_DIR}/scripts/audit_target.py <path>
   ```

   For a project, this walks `.claude/`, the project root for CLAUDE.md, and `~/.claude/projects/<id>/memory/` for auto memory. Each file dispatches to its primitive auditor. Returns aggregated JSON with raw findings.

3. **Read flagged files.** For every finding with severity ≥ MAJOR, open the cited file and read the surrounding context. Form your own judgment before the script's severity becomes the report's.

4. **Verify each script-derived MAJOR or BLOCKER before promoting it.** The deterministic scripts are pattern-matchers; they give you a *location* and a *hypothesis*. Before any script finding makes it into the report at MAJOR or BLOCKER severity, ask: *does the property the script asserts actually hold here?* — not just *did the regex match?*

   Example: the link-integrity check might flag a backticked filesystem path like `.<dotdir>/settings.json` as a broken reference because it doesn't exist in the skill bundle. Open the file. If it's filesystem-path documentation about user projects, the property "this is a broken bundle reference" doesn't hold. Drop the finding and note the false-positive class in the report's Notes section.

   Example: the security scanner might flag a credential-shaped env var name (something like `$<API_KEY_NAME>`) in a security-checklist reference. Open the file. If the credential string appears inside a deny-list example or a "what to look for" catalog, the property "this skill reads the credential" doesn't hold. Drop, note as pedagogical.

   Example: the TOC check might fire on a long file. Open the file. If the first 30 lines contain a heading-style index (under any of the recognized headings, or as a bullet list of cross-references), the property "navigable index is missing" doesn't hold. Drop.

   This step is non-optional. Skipping it produces reports with false-positive MAJOR/BLOCKERs that erode the audit's credibility. The script's job is to surface candidates; your job is to confirm or refute the property each one asserts. When form (regex match) and function (the property being asserted) diverge, function wins.

5. **Run cross-file pair checks:**

   ```bash
   python3 ${CLAUDE_SKILL_DIR}/scripts/cross_file_checks.py <path>
   ```

   Returns findings from the 24 cross-file pair checks (see `references/cross-file-checks.md`).

6. **Apply pedagogical-marker prefilter:**

   ```bash
   python3 ${CLAUDE_SKILL_DIR}/scripts/pedagogical_marker_check.py <path> <findings.json>
   ```

   Findings inside declared pedagogical sections get demoted to INFO. Findings outside but pattern-matching dangerous content get *escalated* (anti-laundering — see `references/pedagogical-marker-spec.md`).

7. **Run LLM-judge triage on remaining findings ≥ MAJOR:**

   ```bash
   python3 ${CLAUDE_SKILL_DIR}/scripts/triage_with_judge.py <findings.json>
   ```

   The judge cannot zero out CRITICAL findings — maximum is one-notch demotion with human-review flag. See `references/triage-protocol.md`.

8. **Compute the verdict:**

   ```bash
   python3 ${CLAUDE_SKILL_DIR}/scripts/verdict_compute.py <findings.json>
   ```

   Score floors at 0, ceilings at 100. Verdict thresholds: PASS 95+, PASS-WITH-MINOR-FIXES 85–94, NEEDS-WORK 70–84, FAIL <70. SECURITY-BLOCK overrides on any confirmed CRITICAL.

9. **Write the report.** Use `assets/audit-report-project.md` for project audits, `assets/audit-report-single.md` for single-target. Save as `audit-report-<target-name>.md` in the current working directory.

   For long audits, copy `assets/audit-checklist.md` into your working response and check off items as you finish them — it helps survive context summaries.

## Dispatch table

```
Target type                                         Routes to
──────────────────────────────────────────────────  ──────────────────────────────────────
Directory with .claude/ subdir                      PROJECT_AUDIT (this coordinator walks)
Directory containing SKILL.md                       auditing-skills
SKILL.md file                                       auditing-skills
File at .claude/commands/<name>.md                  auditing-skills (slash command variant)
CLAUDE.md, CLAUDE.local.md, .claude/CLAUDE.md       auditing-context-files
File under .claude/rules/                           auditing-context-files
File under ~/.claude/projects/<id>/memory/          auditing-context-files (auto memory)
File under .claude/agents/                          auditing-subagents
MEMORY.md under .claude/agent-memory[-local]/       auditing-subagents (subagent memory)
settings.json, settings.local.json                  auditing-settings
managed-settings.json                               auditing-settings (managed mode)
File under .claude/output-styles/                   auditing-settings
hooks.json or hooks block in settings              auditing-hooks
File under .claude/hooks/                           auditing-hooks (hook script)
.mcp.json, ~/.claude.json                           auditing-mcp
```

## Routing table — references

| When you need to... | Read this |
|---|---|
| Score a dimension | `references/audit-rubric.md` |
| Decide if a finding survives triage | `references/triage-protocol.md` |
| Interpret pedagogical markers | `references/pedagogical-marker-spec.md` |
| Understand a cross-file finding | `references/cross-file-checks.md` |
| Understand precedence between primitives | `references/additive-vs-override.md` |
| Diagnose silent failures | `references/common-failures.md` |

## Sub-skill family

This coordinator dispatches to five sibling skills (all installable individually):

- **auditing-skills** — SKILL.md files, slash commands
- **auditing-context-files** — CLAUDE.md, rules, auto memory
- **auditing-subagents** — agent files, subagent persistent memory
- **auditing-hooks** — hook configuration and hook scripts
- **auditing-settings** — settings.json (all scopes), output styles

If a sub-skill is missing from the user's install, the coordinator skips that primitive type and notes it in the report ("auditing-X not installed; primitive Y skipped").

**Note on auditing-mcp**: previously a sub-skill of this family, graduated to its own family-coordinator status per ADR-0042 (cycle-3 reconciliation, devcontainer-mcp-provisioning-r1 Gate-4 OI-2 closure). MCP failure-domain (silent-failure, devcontainer/docker breakage, supply-chain compromise) is operationally distinct from `.claude/`-config correctness; `auditing-mcp` now coordinates its own family at `.claude/skills/auditing-mcp/`. Project-wide audits SHOULD invoke both `auditing-cc-configs` AND `auditing-mcp` separately; the two families are now peers under the `auditing-shared` utility home (per ADR-0031). Per ADR-0005 append-only supersession discipline, this section documents the graduation rather than deleting the historical fact that `auditing-mcp` was once enumerated here.

## Verdict thresholds (v2 — tightened)

> **Canonical source.** Severity weights and verdict bands are maintained in [`.claude/canonical/severity.yaml`](../../canonical/severity.yaml) (loaded by `canonical.py`; `verdict_compute.py` computes from it). The values below mirror that file — if they disagree, the YAML wins. Per KB-cc-design Principle 11, do not duplicate the severity enumeration without a reference back to canonical.

| Score | Verdict |
|---|---|
| 95–100 | PASS |
| 85–94 | PASS-WITH-MINOR-FIXES |
| 70–84 | NEEDS-WORK |
| 50–69 | FAIL |
| 0–49 | FAIL |
| any | SECURITY-BLOCK (overrides) |

Severity weights (per canonical): BLOCKER −12, MAJOR −5, MINOR −1, NIT −0.5, INFO 0. Score floors at 0 per dimension. One BLOCKER drops a perfect score to 88 (PASS-WITH-MINOR-FIXES); two BLOCKERs to 76 (NEEDS-WORK); three to 64 (FAIL).

## Severity meanings

- **BLOCKER** — the configuration is broken or dangerous. Won't load, won't trigger, security issue, or filesystem-level breakage. Verdict cannot be PASS.
- **MAJOR** — works but has a problem that meaningfully degrades behavior.
- **MINOR** — works fine but deviates from spec or best practice.
- **NIT** — taste or polish.

## Modes

- **Default** — full audit including content-quality dimensions and LLM-judge triage.
- **`--managed`** — lint-only. Skips judgment-heavy checks. Used for enterprise managed-policy validation.
- **`--with-runtime`** — adds MCP runtime audit. Requires network egress; user approves per-run.

## Report-only contract

This skill never modifies the audited configuration. The report contains fix suggestions, but applying them is the user's or another agent's job. Do not Edit, Write, or rewrite files inside the audited tree under any circumstance. The only file this skill produces is the audit report in the current working directory.

## Skill listing budget

If installing the full family user-wide, raise the listing budget to prevent description truncation:

```
export SLASH_COMMAND_TOOL_CHAR_BUDGET=30000
```

Or mark sub-skills as `"name-only"` in settings. When invoked via cc-critique subagent, this doesn't apply — the subagent preloads via `skills:` field, bypassing the user-session budget.

## Three memory concepts

Claude Code uses "memory" for three distinct mechanisms. The auditor keeps them separate. See `references/common-failures.md` for the mental model and routing.

| # | Concept | Written by | Audited by |
|---|---|---|---|
| 1 | CLAUDE.md / rules | User | auditing-context-files |
| 2 | Auto memory (`~/.claude/projects/<id>/memory/`) | Claude | auditing-context-files |
| 3 | Subagent memory (`.claude/agent-memory/<name>/`) | Subagent | auditing-subagents |
