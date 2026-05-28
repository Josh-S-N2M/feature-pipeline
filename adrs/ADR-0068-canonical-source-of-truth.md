---
id: ADR-0068
title: Canonical source of truth for shared vocabulary (.claude/canonical/) + audit consolidations
status: Accepted
date: 2026-05-27
supersedes: []
superseded_by: null
---

# ADR-0068 — Canonical source of truth for shared vocabulary

## Status

Accepted (2026-05-27).

## Context

A meta-audit conducted earlier on 2026-05-27 surfaced that the audit subsystem
had accumulated **189 module-level constants across 40 audit scripts**, with no
shared source of truth for shared concepts. Three constants were already
silently divergent:

- `SEVERITY_ORDER` — 3 definitions, one (in `auditing-github-actions/audit_workflow.py`) used dict shape instead of list and was missing `NIT` entirely
- `NAME_PATTERN` — 2 definitions, the skill validator allowed uppercase (post-2026-05-27 fix) while the subagent validator did not
- `KNOWN_TOOLS` — 2 definitions, one had the current Claude Code surface, the other was stale

Plus three structural issues:
- An advertised-but-unwired rule (OP-11 in `auditing-mcp/SKILL.md`)
- An orphan script (`auditing-context-files/scripts/cross_file_duplication.py`)
- Seven still-invoked subprocess calls to stubbed scanners (per ADR-0067)
- The X9 cascade rule produced 1-to-N noise amplification (28 of 28 baseline X9 fires were derivative of a single path-resolver false positive in `lint_references.py`)
- Four independent YAML frontmatter parsers (`split_frontmatter`) duplicated across audit families

The independent reviewer in Phase 5 of the meta-audit called the master gap "the audit doesn't audit itself" — every other class of defect flowed from this single structural absence.

The user's explicit constraint:

> Ensure if you create a "single source of truth" that this is then used by the entire part of the system. Not just auditors or we will then have drift again.

## Decision

Introduce `.claude/canonical/` as the project's single source of truth for shared vocabulary, with three layers:

1. **Layer 1 — Canonical data.** Eight YAML files under `.claude/canonical/`:
   `tools.yaml`, `hook-events.yaml`, `severity.yaml`, `naming.yaml`,
   `frontmatter-fields.yaml`, `doc-types.yaml`, `skill-thresholds.yaml`,
   `audit-rules.yaml` (plus `README.md`).

2. **Layer 2 — Python accessor.**
   `.claude/skills/auditing-shared/scripts/canonical.py` loads and caches the
   YAML and exposes typed accessors (`canonical.tools.KNOWN_TOOLS`,
   `canonical.severity.ORDER`, `canonical.naming.SKILL_NAME_PATTERN`, etc.).
   Every audit script that needs shared vocabulary imports from this module.

3. **Layer 3 — Drift enforcement.** A new audit rule, `CANON-1`, walks every
   Python file under `.claude/skills/auditing-*/scripts/` and emits a BLOCKER
   finding when a watched constant name (`KNOWN_TOOLS`, `VALID_EVENTS`,
   `SEVERITY_ORDER`, `NAME_PATTERN`, `RECOGNIZED_FIELDS`, etc.) is defined
   locally. The drift detector lives at
   `.claude/skills/auditing-shared/scripts/audit_canonical_drift.py`. It
   accepts derived-alias assignments (`KNOWN_TOOLS = _tools.KNOWN_TOOLS`) and
   only flags genuine inline redefinitions.

In the same change, address the meta-audit's other concrete findings:

- **X9 severity-floor model.** Cascades from FAIL-verdict child skills now
  apply a severity floor: child BLOCKER → parent MAJOR; child MAJOR → parent
  MINOR; child MINOR → drop. Cascades from PASS-verdict skills are
  suppressed entirely. Closes the 1-to-N noise amplification.

- **SK-broken-link severity tiering.** Broken refs in `references/` files
  emit MAJOR (not BLOCKER); broken refs in SKILL.md body still emit BLOCKER.
  Reflects that SKILL.md is load-bearing for routing while references are
  instructional.

- **Shared frontmatter parser.** `auditing-shared/scripts/frontmatter.py`
  provides one canonical `split_frontmatter` + `parse_simple_yaml_fields`.
  Five prior copies (in `validate_frontmatter.py`,
  `validate_subagent_frontmatter.py`, `scan_subagent_body.py`,
  `analyze_subagent.py`, `validate_output_styles.py`) now forward to it.

- **Orphan removed.** `auditing-context-files/scripts/cross_file_duplication.py`
  deleted (no caller, no SKILL.md reference).

- **OP-11 removed.** `auditing-mcp/scripts/audit_op11_adr_parity.py` and its
  SKILL.md advertisement deleted. The script existed but was never wired into
  the dispatch loop. Per the project's post-`mcp-openapi-schema`-removal state
  (5-server canonical set), the ADR-0041 parity check is no longer needed.

- **Stub call sites inlined.** Seven still-invoked subprocess calls to
  scanners disabled by ADR-0067 are now inline `{"findings": []}`
  assignments. Saves ~350-700ms per audit run.

## Architecture

```
Layer 1 — Canonical data       .claude/canonical/*.yaml
Layer 2 — Python accessor      auditing-shared/canonical.py
Layer 3 — Audit consumers      import canonical (no inline lists)
Layer 4 — Markdown consumers   cite .claude/canonical/*.yaml by path
Layer 5 — Drift enforcement    CANON-1 BLOCKER on inline redefinition
```

The SSOT is **enforced by audit**. This is what makes it single across the
project, not just the audit subsystem. A future agent author who tries to
redefine `KNOWN_TOOLS = {...}` in a new script will get a BLOCKER finding from
CANON-1 the next time the audit runs.

## Consequences

**Intended (positive):**

- Single point of truth for tool inventory, severity vocabulary, naming
  patterns, frontmatter fields, doc-type vocabularies, skill thresholds, and
  the audit rule registry. Adding a new tool, hook event, or doc-type is a
  one-file change to YAML.

- Drift cannot return silently. CANON-1 is BLOCKER-severity.

- The audit baseline is now `score 100 / verdict PASS` after the dust settles
  — every finding the audit emits going forward is signal, not auditor
  defect.

- ADR-0067's disabled-rule list is documented in `audit-rules.yaml` (not
  just buried in a stub comment in 13 files).

**Accepted (negative):**

- The audit scripts now have a hard runtime dependency on PyYAML. The
  project's runtime ships with it; the bootstrap raises a clear error if
  missing.

- Adding a new tool / event / state requires editing the canonical YAML AND
  bumping the canonical file's `version:` field. There is no auto-update
  mechanism from the upstream Claude Code platform docs. (This is the
  intended trade-off: explicit, version-controlled snapshots vs. silent
  freshness.)

**Reversibility:** HIGH. All migrations are mechanical (replace inline
constant with import). The canonical files are additive. Git revert of
any single migration commit restores the prior local constant. The
`CANON-1` audit can be disabled by setting `status: disabled` on its
entry in `audit-rules.yaml` if a structural reason to allow local
redefinition emerges.

## Verification

After this ADR's changes were applied:

- `python3 .claude/skills/auditing-shared/scripts/audit_canonical_drift.py`
  → 0 findings (no inline redefinitions remain in scope).
- `python3 .claude/skills/auditing-cc-configs/scripts/audit_project.py .`
  → score 100/100, verdict PASS, 0 findings.
- All five `split_frontmatter` consumer scripts run their existing
  audit-time paths unchanged (forwarder pattern preserves behavior).

## Cross-references

- `ADR-0067` — security-check removal (sibling cleanup from the same session)
- `ADR-0066` — gitnexus removal
- `.claude/canonical/README.md` — operator guide for canonical files
- `Issues/direct-counterfactual-repair/analysis.md` — the counterfactual
  test that surfaced the audit-bug-vs-project-defect ratio empirically
