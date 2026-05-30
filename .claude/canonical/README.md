# `.claude/canonical/` — Single Source of Truth

This directory is the **single source of truth** for shared vocabulary the
audit subsystem and the rest of the project consume:

- Claude Code tool names
- Claude Code hook event names
- Severity vocabulary (and the ordinal / score-weight)
- Naming conventions for skills and sub-agents
- Recognized frontmatter fields by primitive type
- Doc-type and issue-state vocabularies
- Per-skill-class size thresholds
- The audit rule registry (including which rules are currently disabled and why)
- The engineering domain layers used by Layer Scope and per-layer Design

## Why this directory exists

Before this directory was created, the same concepts (e.g., `KNOWN_TOOLS`,
`SEVERITY_ORDER`, `NAME_PATTERN`) were duplicated as Python constants across
multiple audit scripts. Three were already silently divergent. See ADR-0068
for the full rationale.

## Consumption pattern

- **Python audit scripts** import from `auditing-shared/scripts/canonical.py`,
  which loads and caches the YAML from this directory. Do not redefine these
  constants locally.
- **Sub-agents, SKILL.md files, AGENTS.md** cite the canonical file by path
  when discussing tool surface, severity, naming, etc.
- **`settings.json`** is audited against `tools.yaml` (permission rules must
  reference real tools) and `hook-events.yaml` (hooks must use valid events).
- **The audit subsystem itself** is audited for inline drift — a Python
  script under `.claude/skills/auditing-*/scripts/` that defines its own
  `KNOWN_TOOLS = …` constant emits a BLOCKER finding.

## Updating canonical files

These files are version-controlled. To update:

1. Edit the YAML.
2. Bump the `version:` field at the top of the file.
3. Re-run the project audit (`python3 .claude/skills/auditing-cc-configs/scripts/audit_project.py .`).
4. If the audit surfaces any drift between the new canonical and the rest of
   the project (e.g., a sub-agent now references a tool that was removed), fix
   the dependent code.
5. Commit the YAML + dependent fixes together so the canonical change and its
   knock-on updates land atomically.

## File index

| File | Purpose |
|---|---|
| `tools.yaml` | Claude Code tool inventory (Read, Write, Bash, mcp__*, etc.) |
| `hook-events.yaml` | Claude Code hook event names (PreToolUse, SessionEnd, etc.) |
| `severity.yaml` | Finding severity vocabulary, ordinal, and score weight |
| `naming.yaml` | Skill / sub-agent / file name regex conventions |
| `frontmatter-fields.yaml` | Recognized frontmatter fields by primitive type |
| `doc-types.yaml` | Pipeline / ADR / Issue doc-type and state vocabularies |
| `skill-thresholds.yaml` | Per-skill-class size and TOC thresholds |
| `audit-rules.yaml` | Rule registry; which rules are disabled and why |
| `engineering-domain-layers.yaml` | The engineering layers used by Layer Scope + per-layer Design (prose companion: `KB-documentation-criteria/references/layer-taxonomy.md`) |
| `technology-boundaries.yaml` | Machine-checkable half of the architecture's technology boundaries (TB1–TB11) — the boundary screen + fitness-function binding (prose companion: `governed-pipeline-architecture.md` Appendix F) |
| `evaluation-rubric.yaml` | Weighted, calibrated rubric for the `technology-evaluation` workflow — profiles + criteria + anchors (prose companion: `.claude/workflows/technology-evaluation.DESIGN.md`) |

## Authority

When canonical and code disagree:

- If a Python audit script defines a constant that contradicts canonical:
  the script is wrong. Update the script to import from canonical.
- If a markdown doc cites a value that contradicts canonical: the doc is wrong.
  Update the doc.
- If canonical disagrees with Claude Code's actual platform behavior:
  canonical is wrong. Update canonical and bump its version.
