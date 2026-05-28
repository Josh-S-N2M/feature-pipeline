# Claude Code Configuration Audit — feature-pipeline

**Audited:** `/workspaces/feature-pipeline`
**Score:** 100/100
**Verdict:** PASS

## Inventory

- skills: 44
- context files: 1
- subagents: 37
- subagent memory dirs: 22
- hook scripts: 2
- settings files: 1
- output styles: 0
- MCP configs: 1

## Summary

Total findings: 14

## Cross-file checks

- **[INFO] ?** — .claude/agents/design-composer.md enumerates 7/9 members of the canonical 'engineering-domain-layers' vocabulary but references the canonical source — treated as a derived view.
  - *Fix:* OK as a derived/functional view because it points back to .claude/canonical/engineering-domain-layers.yaml. Keep the reference; do not let the inline list drift from canonical.
- **[INFO] ?** — .claude/agents/issue-capture-author.md enumerates 6/6 members of the canonical 'issue-states' vocabulary but references the canonical source — treated as a derived view.
  - *Fix:* OK as a derived/functional view because it points back to .claude/canonical/doc-types.yaml. Keep the reference; do not let the inline list drift from canonical.
- **[INFO] ?** — .claude/skills/KB-cc-platform/references/extensions.md enumerates 9/13 members of the canonical 'hook-events' vocabulary but references the canonical source — treated as a derived view.
  - *Fix:* OK as a derived/functional view because it points back to .claude/canonical/hook-events.yaml. Keep the reference; do not let the inline list drift from canonical.
- **[INFO] ?** — .claude/skills/KB-documentation-criteria/references/deliverable-archive-spec.md enumerates 9/13 members of the canonical 'gated-doc-types' vocabulary but references the canonical source — treated as a derived view.
  - *Fix:* OK as a derived/functional view because it points back to .claude/canonical/doc-types.yaml. Keep the reference; do not let the inline list drift from canonical.
- **[INFO] ?** — .claude/skills/KB-documentation-criteria/references/templates/blueprint-template.md enumerates 6/9 members of the canonical 'engineering-domain-layers' vocabulary but references the canonical source — treated as a derived view.
  - *Fix:* OK as a derived/functional view because it points back to .claude/canonical/engineering-domain-layers.yaml. Keep the reference; do not let the inline list drift from canonical.
- **[INFO] ?** — .claude/skills/KB-documentation-criteria/references/templates/issue-analysis-template.md enumerates 6/6 members of the canonical 'issue-states' vocabulary but references the canonical source — treated as a derived view.
  - *Fix:* OK as a derived/functional view because it points back to .claude/canonical/doc-types.yaml. Keep the reference; do not let the inline list drift from canonical.
- **[INFO] ?** — .claude/skills/KB-documentation-criteria/references/templates/issue-proposal-template.md enumerates 6/6 members of the canonical 'issue-states' vocabulary but references the canonical source — treated as a derived view.
  - *Fix:* OK as a derived/functional view because it points back to .claude/canonical/doc-types.yaml. Keep the reference; do not let the inline list drift from canonical.
- **[INFO] ?** — .claude/skills/KB-documentation-criteria/references/templates/issue-register-template.md enumerates 6/6 members of the canonical 'issue-states' vocabulary but references the canonical source — treated as a derived view.
  - *Fix:* OK as a derived/functional view because it points back to .claude/canonical/doc-types.yaml. Keep the reference; do not let the inline list drift from canonical.
- **[INFO] ?** — .claude/skills/KB-issue-capture/references/non-pollution-contract.md enumerates 6/6 members of the canonical 'issue-states' vocabulary but references the canonical source — treated as a derived view.
  - *Fix:* OK as a derived/functional view because it points back to .claude/canonical/doc-types.yaml. Keep the reference; do not let the inline list drift from canonical.
- **[INFO] ?** — .claude/skills/auditing-cc-configs/SKILL.md enumerates 5/5 members of the canonical 'severity' vocabulary but references the canonical source — treated as a derived view.
  - *Fix:* OK as a derived/functional view because it points back to .claude/canonical/severity.yaml. Keep the reference; do not let the inline list drift from canonical.
- **[INFO] ?** — .claude/skills/auditing-cc-configs/references/audit-rubric.md enumerates 5/5 members of the canonical 'severity' vocabulary but references the canonical source — treated as a derived view.
  - *Fix:* OK as a derived/functional view because it points back to .claude/canonical/severity.yaml. Keep the reference; do not let the inline list drift from canonical.
- **[INFO] ?** — .claude/skills/auditing-cc-configs/references/cross-file-checks.md enumerates 5/5 members of the canonical 'severity' vocabulary but references the canonical source — treated as a derived view.
  - *Fix:* OK as a derived/functional view because it points back to .claude/canonical/severity.yaml. Keep the reference; do not let the inline list drift from canonical.
- **[INFO] ?** — .claude/skills/auditing-hooks/SKILL.md enumerates 9/13 members of the canonical 'hook-events' vocabulary but references the canonical source — treated as a derived view.
  - *Fix:* OK as a derived/functional view because it points back to .claude/canonical/hook-events.yaml. Keep the reference; do not let the inline list drift from canonical.
- **[INFO] ?** — .claude/skills/recipe-feature-pipeline/SKILL.md enumerates 10/13 members of the canonical 'gated-doc-types' vocabulary but references the canonical source — treated as a derived view.
  - *Fix:* OK as a derived/functional view because it points back to .claude/canonical/doc-types.yaml. Keep the reference; do not let the inline list drift from canonical.

## How to read this report

Severity meanings:

- **BLOCKER** — file won't load, security issue, or breaks core functionality. Fix before shipping.
- **MAJOR** — works but degrades behavior or security.
- **MINOR** — deviates from best practice.
- **NIT** — taste or polish.

Verdict bands: PASS≥95 · PASS-WITH-MINOR-FIXES 85–94 · NEEDS-WORK 70–84 · FAIL<70. SECURITY-BLOCK overrides on confirmed CRITICAL.


Report-only: this audit does not modify any audited file.