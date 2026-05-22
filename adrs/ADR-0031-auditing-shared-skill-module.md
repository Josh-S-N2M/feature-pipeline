---
id: ADR-0031
title: auditing-shared skill module — canonical home for audit utilities
status: accepted
date: 2026-05-21
deciders: [user, claude]
supersedes: []
superseded_by: []
related: [ADR-0029, ADR-0030, ADR-0025, ADR-0026, ADR-0028]
authored_during: audit-findings-remediation-r1 (Stage 7 Design Composition)
---

# ADR-0031: `auditing-shared` skill module — canonical home for audit utilities

## Context

Discovery Stage 4 of the `audit-findings-remediation-r1` feature surfaced (per ADR-0029) that the project has **three near-duplicate copies** of `pedagogical_marker_check.py`:

- `auditing-cc-configs/scripts/pedagogical_marker_check.py` — called by `triage_with_judge.py`
- `auditing-skills/scripts/pedagogical_marker_check.py` — called by `audit_skill.py`
- `auditing-subagents/scripts/pedagogical_marker_check.py` — called by `audit_subagent.py`

The 18-28 line pairwise diffs are mostly comment formatting plus one defensive backward-compat (`f.get("location") or f.get("where")`) in the `auditing-skills` copy. Three copies arose from the project's convention that each skill module is self-contained — when the marker triage logic was needed in three audit dispatchers, three copies were the path of least resistance.

The same pattern exists for `scan_memory_secrets.py` (identical in `auditing-context-files/` and `auditing-subagents/`). AC-FR-12-e of the feature's PRD requires a scan for additional similar duplications.

Three copies make uniform enforcement structurally fragile. ADR-0030 (mechanism α) requires the marker-justification check to apply uniformly across all audit paths; without a single canonical implementation, "uniform" requires triplicate edits and the discipline drifts whenever the copies diverge.

## Decision

Establish a new sibling skill module `auditing-shared` at `.claude/skills/auditing-shared/` as the canonical home for audit utility scripts shared across the audit family.

### Initial module contents

```
.claude/skills/auditing-shared/
  SKILL.md                                # describes module role; not directly invocable
  scripts/
    pedagogical_marker_check.py           # canonical (union of 3 prior copies + mechanism-α justification check)
    scan_memory_secrets.py                # canonical (identical to 2 prior copies)
```

### Canonical implementation rules

1. **Single source of truth.** Each utility lives in exactly one file under `auditing-shared/scripts/`. The pre-existing copies in sibling skills are either DELETED (preferred) or replaced with thin shims that re-export from the canonical.
2. **Backward-compatibility preserved.** Where a copy carried a real semantic difference (e.g., the `location`/`where` field-name compat in `auditing-skills`), that compat IS preserved in the canonical implementation. Comment-only differences are collapsed.
3. **Subprocess invocation pattern unchanged.** Audit dispatchers continue to invoke audit modules via subprocess (per `audit_project.py`'s existing pattern). The canonical script's location is the contract, not its Python import name. Dispatchers reference the canonical filesystem path.
4. **No new behavior in the merge.** AC-FR-12-c of the feature's PRD requires audit-output equivalence pre- and post-deduplication, modulo the new mechanism-α check from ADR-0030.

### Module discoverability

`auditing-shared/SKILL.md` declares:

- **Role:** utility module housing scripts shared across `auditing-*` audit family
- **Not directly invocable:** users do not invoke `auditing-shared` skills; it's a code-organization module
- **Stability commitment:** scripts here are imported by other auditing skills' scripts; breaking changes require coordinated updates to all callers

The SKILL.md does NOT include `pedagogical_sections:` frontmatter — the file has no pedagogical content. (Per ADR-0030, that's the right reason to omit it; per FR-7-d, every marker added needs justification, and adding an empty marker just to satisfy a convention would itself be a discipline violation.)

### Future growth

Items naturally landing in `auditing-shared` over time:

- Any additional duplicate script identified by AC-FR-12-e scan
- New shared regex utilities (e.g., the negation-aware bypass-approval helper from FR-5)
- Shared JSON schemas (if audit-output formats need a single source)

Items that should NOT land here:

- Skill-specific logic (e.g., `analyze_subagent.py`'s SA-2 regex is subagent-specific — stays in `auditing-subagents`)
- Skill-specific configuration
- Test fixtures (those live with the audit module they test)

The discriminator is reuse: code used by 2+ audit modules belongs in `auditing-shared`; code used by exactly 1 stays with its module.

## Consequences

### Positive

- **Single point of enforcement for mechanism α** (and any future cross-cutting audit check). ADR-0030's uniform-enforcement requirement becomes structurally guaranteed, not maintained-by-discipline.
- **Drift prevention.** When the canonical changes, all callers see the change. No more "we fixed it in cc-configs but forgot the subagents copy."
- **Smaller surface area.** Two duplicate-set deletions (~900 lines of duplicated Python become ~500 lines canonical).
- **Pattern for future.** Future audit work that needs shared utilities has an obvious home; no precedent-setting required.

### Negative

- **New skill module** adds one entry to the skill list. Minor inventory overhead.
- **Python import semantics** for skill-internal scripts vary; the subprocess invocation pattern works (dispatch resolves filesystem paths), but in-process imports across skill modules require explicit path manipulation. Implementation detail; per-layer Design notes the issue.
- **Migration cost** for the deduplication itself (~28 dependency-graph items in `cc-dependencies.json`'s DG-2 group). Bounded; in scope for FR-12.

### Forward implications

- **Auditor stability:** Once `auditing-shared/scripts/pedagogical_marker_check.py` is the canonical, mechanism α's enforcement consistency is automatic. Any future feature run touching marker triage edits one file, not three.
- **AC-FR-12-e scan** may surface 1-2 more duplications. Per ADR-0029, surface each; Plan stage decides whether to absorb into this feature or defer.
- **Skill-discovery hygiene:** `auditing-shared/SKILL.md` will be loaded into auditing-* dispatch context if Claude scans the skill registry; SKILL.md must be small and clearly marked as a utility module to avoid confusion.

## Alternatives considered

### Alternative 1 — Designate one of the 3 existing copies as canonical; replace the other 2 with thin import shims (D7-B)

Smallest possible change. The chosen canonical's existing call site is unchanged; the other 2 call sites import + re-export.

**Rejected** because:
- Python's import-path semantics across skill-script subprocess invocations are fragile. Each subprocess invocation has its own `sys.path`; resolving `from auditing_cc_configs.scripts.pedagogical_marker_check import ...` reliably requires either PYTHONPATH manipulation or invocation-time `sys.path.insert` — both add brittle ceremony.
- Locality is misleading: the "canonical" copy is in a skill named after a specific audit target (`cc-configs`), but the canonical is used by audit-skills and audit-subagents too. The naming creates the false impression that the cc-configs audit owns the logic.
- Future shared utilities have no obvious home — every new shared script repeats the "pick a host skill" debate.

### Alternative 2 — Top-level `.claude/lib/` for shared utilities (D7-C)

Move shared scripts to `.claude/lib/pedagogical_marker_check.py` etc. Cleanest path-wise.

**Rejected** because:
- Breaks the project's "code lives with its skill" convention. Every other audit script is at `.claude/skills/<skill>/scripts/`; introducing `.claude/lib/` adds a second pattern.
- Skill modules are the project's unit of cohesion + discoverability. A scripts-only directory outside the skill-module structure has no SKILL.md, no description, no role declaration. Discoverability suffers.
- Future audit consumers (and the human maintainer) have to know about TWO places shared audit code might live (`auditing-shared/` vs `lib/`) — increases cognitive load.

### Alternative 3 — Keep the 3 copies; introduce a sync mechanism (CI check, pre-commit hook)

Add a sync check that fails if the 3 copies diverge.

**Rejected** because:
- Sync is a discipline, not a structural property. Disciplines drift; structures don't.
- Adds complexity (the sync check itself is new code) without removing the underlying duplication.
- The project has no CI hooks for audits currently; adding a CI hook just for this sync would be the first such hook and would set precedent.

### Alternative 4 — Defer deduplication; just propagate mechanism-α to all 3 copies in parallel

Skip FR-12 entirely; add the mechanism-α justification check to all 3 existing copies independently.

**Rejected** because:
- Surfaced as SD-001 during Discovery and resolved via PRD v1.1.0 amendment with explicit user input. Path (a) — PRD amendment — was chosen specifically because deferring would create ongoing maintenance burden.
- The mechanism-α enforcement is the new check whose uniformity matters most. Triplicating it at introduction means every future change has the same triplication risk.

Selected: Alternative 0 (this ADR) — new `auditing-shared` sibling skill module. Aligns with the project's sibling-skill convention; provides obvious home for future shared utilities; one-time cost.

## Notes

The `auditing-shared` naming follows the project's convention (`auditing-cc-configs`, `auditing-context-files`, `auditing-mcp`, etc.). The `-shared` suffix is informal but clear; if a future ADR renames it for consistency with a more formal convention, that's a discoverable change.

The decision to make `auditing-shared/SKILL.md` non-pedagogical (no `pedagogical_sections:` frontmatter) is intentional and called out because the file genuinely has no pedagogical content. Adding an empty marker just to "fill in" the convention would itself violate ADR-0030's discipline — markers without substance are exactly what mechanism α rejects.

This ADR + ADR-0030 together discharge the cross-cutting design decisions for `audit-findings-remediation-r1`. The Blueprint references both as authored deliverables.
