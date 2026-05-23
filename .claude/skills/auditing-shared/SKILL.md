---
name: auditing-shared
description: Canonical home for utilities shared across the auditing-* skill families (auditing-cc-configs, auditing-skills, auditing-subagents, auditing-context-files, and — as of ADR-0042 in devcontainer-mcp-provisioning-r1 — auditing-mcp as an independent graduated family). Hosts the single implementation of cross-audit-module helpers. Not user-invocable; loaded by the audit-module skills via subprocess dispatch. Established by ADR-0031 in v4.6.0; extended to support graduated auditing-mcp family per ADR-0042.
user-invocable: false
allowed-tools: Read, Grep, Glob, Bash(python3:*)
---

# auditing-shared

Canonical implementation home for utilities shared across the auditing-* skill families. Per ADR-0031, eliminates the 3-copy duplication of `pedagogical_marker_check.py` (and similar future duplications) that accumulated through v4.4.x. Per ADR-0042 (devcontainer-mcp-provisioning-r1, Gate-4 OI-2 closure), the consumer set extended from 4 sub-skills of auditing-cc-configs to 5 family coordinators: auditing-cc-configs (with its 5 remaining sub-skills) AND auditing-mcp (now its own family-coordinator).

## Contents

- `scripts/pedagogical_marker_check.py` — Canonical mechanism-α enforcement (per ADR-0030 + `KB-documentation-criteria/references/pedagogical-marker-justification-spec.md`). Replaces 3 prior copies in auditing-cc-configs, auditing-skills, auditing-subagents.
- `scripts/scan_memory_secrets.py` — Canonical credential-string scanner for context files (CLAUDE.md, MEMORY.md, agent-memory). Replaces 2 prior copies in auditing-context-files, auditing-subagents (per Plan §P4.2 / AC-FR-12-e).

## How to invoke

Audit modules dispatch via subprocess:

```bash
python3 scripts/pedagogical_marker_check.py <target-path> [options]
```

See `pedagogical-marker-justification-spec.md` for the spec the script enforces.

## Why this skill exists

ADR-0031 records the rationale. Brief: three independent copies of the same parser/validator drifted across versions; v4.5.0's audit noted them as a duplication finding. Mechanism α (ADR-0030) requires a single canonical implementation so the discipline is enforced uniformly. This skill is that single home.

## What does NOT belong here

- Audit-module-specific logic (e.g., subagent-specific bypass-approval check belongs in auditing-subagents).
- Skills-as-runnable user invocations (this skill is library-only; user-invocable: false).
- Anything that would create a circular dependency between auditing-shared and an auditing-* module.

