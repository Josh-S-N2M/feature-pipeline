---
id: ADR-0010
version: 2.1.0
status: Accepted
generated: 2026-05-19
generated_by: finalize-reconciler (v4.3.0 naming-convention retroactive update per ADR-0019)
supersedes:
  - {id: ADR-0010, version: 1.0.0}
adrs_inherited:
  - ADR-0001 (orchestrator placement)
applies_to:
  - feature-pipeline (blueprint v3 and beyond)
  - synthesize pipeline (existing, retroactive fix)
template_format: per ADR.txt v1.0
---

# ADR-0010: Knowledge skill frontmatter must not combine `disable-model-invocation: true` with `skills:` preload

## Status

Accepted — 2026-05-12 (template-migrated from v1.0.0 of the same date)

## Context

Research round 2 surfaced a bug in both the existing synthesize pipeline and blueprint v2: every knowledge skill uses the frontmatter combination `user-invocable: false` AND `disable-model-invocation: true` AND expects the skill to be preloaded into sub-agents via the `skills:` field.

Per Anthropic's primary documentation (claim C-R2-0002):

> Skills that set `disable-model-invocation: true` cannot be preloaded into sub-agents because preloading uses the same skill set that Claude can invoke. If a listed skill is missing or disabled, Claude Code skips it and logs a warning.

This means: every knowledge skill in both pipelines is being silently dropped at sub-agent invocation time. The pipelines have been running with the *agent definitions* loading correctly but the *knowledge skills* failing to load.

The bug is severity-major. It affects the 6 existing synthesize-pipeline knowledge skills, the 12 new knowledge skills named in blueprint v2 §3.4, and the 13 user-named domain knowledge skills if implemented with the same pattern.

## Decision

**Correct frontmatter for pipeline knowledge skills:**

```yaml
---
name: <skill-name>-knowledge
description: |
  <Terse description, key-use-case-first, under 1500 chars total.>
  <When to use: enumerate trigger conditions.>
  <Not for: enumerate what this skill does NOT cover.>
user-invocable: false
---
```

**Required fields:** `name`, `description` (1536-char cap per entry; target 600-1000 chars), `user-invocable: false` (hides from `/` menu).

**Forbidden field for knowledge skills:** `disable-model-invocation: true` — MUST NOT be set. Setting it breaks subagent preload.

**Both pipelines affected; both get the fix.** Feature-pipeline (v3+) authors all new knowledge skills with correct frontmatter. Synthesize pipeline retroactively edits the 6 existing SKILL.md files to remove `disable-model-invocation: true`. Patch-version each pipeline (v1.x.0 → v1.x.1).

## Decision Details

| Item | Content |
|---|---|
| Decision | Knowledge skills MUST use `user-invocable: false` only — never combine with `disable-model-invocation: true`. Both pipelines get the frontmatter fix. |
| Why now | The bug silently breaks knowledge-skill loading in both pipelines today. Every feature-pipeline run since inception has been operating with knowledge skills absent from sub-agent contexts. Fix required before blueprint v3 ships with the same broken pattern. |
| Why this | Anthropic primary documentation (claim C-R2-0002) is unambiguous: `disable-model-invocation: true` prevents preload. The semantic distinction between the two fields (`user-invocable: false` for menu-hiding; `disable-model-invocation: true` for user-trigger-only-with-side-effects) is preserved by using each correctly. |
| Known unknowns | Whether removing `disable-model-invocation: true` causes spurious auto-invocations outside the pipeline (e.g., main session firing claim-extraction-knowledge on unrelated tasks); whether tightened descriptions sufficiently scope this. |
| Kill criteria | If 3+ instances of spurious auto-invocation of pipeline knowledge skills in non-pipeline contexts within a 30-day window cause user-facing problems, supersede with a different mechanism (e.g., `skillOverrides` "name-only" pattern from claim C-R2-0005, or wait for Anthropic to introduce a "preload-only" frontmatter flag). |

## Rationale

The semantic distinction the bug hides:

- **`user-invocable: false`** hides the skill from the `/` menu. Does NOT prevent Claude from auto-invoking the skill when relevant, and does NOT prevent preloading into sub-agents.
- **`disable-model-invocation: true`** prevents Claude from auto-invoking the skill. Skill becomes user-trigger-only (via `/name`). **Also prevents preloading into sub-agents** because preloading uses the same enable-disable mechanism as model auto-invocation.

These are two distinct fields with distinct semantics. The pipeline's existing pattern combined them, intending "hidden from menu AND not auto-invoked AND preload-via-frontmatter." That intent is not realizable in current Claude Code — the third desire is mutually exclusive with the second.

The fix: drop `disable-model-invocation: true`. Knowledge skills become auto-invocable by Claude. Practical consequence: when a user invokes the synthesize skill manually, Claude could now auto-load `claim-extraction-knowledge` even outside the synthesize flow if a task context resembles claim extraction. Mostly harmless (skill is descriptive content; loading it does no harm) but skill descriptions can fire spuriously. Mitigation: write descriptions tightly with explicit scoping language.

## Options Considered

**Option 1: Keep `disable-model-invocation: true`; remove `skills:` preload from sub-agent definitions and rely on Claude discovering the skills via description-match.**
- Pros: preserves the user-trigger-only semantics.
- Cons: rejected — skill discovery via description is unreliable (claim C-R2-0009: naive tool catalogs degrade selection accuracy to 13%); pipeline depends on knowledge skills being PRESENT in sub-agent context, not on Claude getting lucky in discovery.

**Option 2: Switch to `context: fork` model for knowledge skills.** Anthropic supports `context: fork` for skills running in isolation as sub-agents.
- Pros: different mechanism not affected by the bug.
- Cons: rejected — different pattern (skill-as-sub-agent), not "knowledge skill loaded into existing sub-agent."

**Option 3: Wait for Anthropic to change the semantics** so that `disable-model-invocation: true` AND preload can coexist.
- Pros: would preserve current intent.
- Cons: rejected as not actionable — current platform behavior is what it is.

**Option 4: Add Layer-2 enforcement: the sub-agent's body instructs Claude to "read knowledge skill X content from /skills/<x>/SKILL.md".**
- Pros: works around the bug.
- Cons: rejected — defeats the purpose of `skills:` preload (which is to inject content at startup without runtime reads).

**Option 5 (Selected): Remove `disable-model-invocation: true` from knowledge-skill frontmatter; tighten descriptions; accept auto-invocability tradeoff.**
- Pros: correct fix per documentation; preserves the preload mechanism; one-line change per skill.
- Cons: knowledge skills become auto-invocable; some risk of spurious firing outside pipeline contexts; description budget consumption.

## Consequences

### Positive Consequences

- Knowledge skills actually load into sub-agents (current behavior: silently dropped). This is the entire reason for the discipline.
- Preflight verification (added per this ADR) prevents regression in user-authored skills.
- The semantic distinction between the two fields is preserved and used correctly.

### Negative Consequences

- **Existing pipeline knowledge skills are now AUTO-INVOCABLE by Claude.** When a user invokes the synthesize skill manually, Claude could now auto-load `claim-extraction-knowledge` even outside the synthesize flow if a task context resembles claim extraction. Mostly harmless but skill descriptions can fire spuriously. Mitigation: write descriptions tightly with explicit scoping.
- The 1% of context budget for skill descriptions (claim C-R2-0004) now includes these knowledge skills since they're discoverable. For pipelines with 12+ knowledge skills, consumes meaningful description budget. Mitigation: set `skillListingBudgetFraction` higher (e.g., 2%) in `.claude/settings.json` when the pipeline is installed, OR use `skillOverrides` to mark pipeline-internal skills as `name-only` in non-pipeline contexts.

### Neutral Consequences

- The synthesize pipeline must be patch-versioned to reflect this fix. The fix does not break any agent definitions, slash commands, or hooks — only frontmatter changes.

## Architecture Impact

**Components that change:**
- All knowledge skill SKILL.md files (across both pipelines): frontmatter line removed.
- All knowledge skill descriptions: tightened with explicit scoping language to mitigate spurious auto-invocation.
- Preflight stage (Stage 0): new verification step scans sub-agent skills references against skill frontmatter; fails preflight on `disable-model-invocation: true` + `skills:` reference combination.
- `KB-documentation-criteria` skill (per ADR-0011, canonical document skill): documents this convention so future skill authors follow it.

**New dependencies introduced:**
- Preflight depends on being able to read skill frontmatter.

**Architectural constraints added:**
- Knowledge skills MUST NOT set `disable-model-invocation: true`.
- Knowledge skill descriptions MUST scope to pipeline-internal use with explicit "internal knowledge for the <X> pipeline's <Y> stage" language.
- Preflight MUST verify the convention.

**Architectural constraints removed:**
- The pre-fix combination (`user-invocable: false` + `disable-model-invocation: true` + `skills:` preload) is forbidden.

## Implementation Guidance

### For the synthesize pipeline (existing)

- [ ] Edit each of the 6 SKILL.md files: remove `disable-model-invocation: true` from frontmatter.
- [ ] Re-tighten `description:` text: scope to internal pipeline use, target 600-1000 chars.
- [ ] Verify the `skills:` references in sub-agent definitions still match (they should — only frontmatter changed).
- [ ] Re-run the existing audit pipeline (auditing-skills toolkit); confirm no regressions.
- [ ] Patch-version the pipeline (vN.N.X → vN.N.X+1).

### For the feature-pipeline (blueprint v3+)

- [ ] Author all new knowledge skills with the correct frontmatter from the start.
- [ ] Add preflight verification step that scans sub-agent skills references against skill frontmatter.
- [ ] Document the convention in `KB-documentation-criteria` (per ADR-0011).

### Preflight verification pseudocode

```
For each sub-agent definition file in .claude/agents/:
  For each skill in the agent's `skills:` field:
    Read .claude/skills/<skill>/SKILL.md frontmatter
    If frontmatter has `disable-model-invocation: true`:
      FAIL preflight with clear error: "<skill> has disable-model-invocation: true which prevents preload; remove the line."
```

## Related Information

- Original ADR-0010 v1.0.0: preserved at `ADR-0010-knowledge-skill-frontmatter-correction-pre-template-migration.md` per ADR-0014.
- ADR-0001: orchestrator placement (knowledge skills loaded by sub-agents the orchestrator invokes).
- ADR-0011: KB-documentation-criteria — documents the convention for future skill authors.
- Claims: C-R2-0002 (Anthropic primary doc on disable-model-invocation), C-R2-0003 (user-invocable: false semantics), C-R2-0004 (description budget), C-R2-0005 (skillListingBudgetFraction and skillOverrides), C-R2-0009 (tool catalog accuracy degradation).

## Cross-stage supersession marker

`cross_stage_supersession: true` for the synthesize pipeline. This ADR mandates a retroactive change to artifacts in another pipeline (the synthesize pipeline's knowledge-skill frontmatter). The synthesize pipeline's existing knowledge skills are NOT individually rewritten (they remain valid as content); only their frontmatter is patched. `traceability.json` should record:

```
- synthesize pipeline knowledge skills (v1.x.0) → v1.x.1
  Reason: ADR-0010 frontmatter correction
  Mechanism: removed `disable-model-invocation: true` from 6 SKILL.md files
  Content changes: none — frontmatter only
```

## v4.3.0 retroactive naming-convention update

Per ADR-0019, all sub-agent, knowledge skill, and orchestrator skill references in this ADR have been updated to the v4.3.0 naming convention (phase-prefixed sub-agents, KB-prefixed knowledge skills, recipe-prefixed orchestrator, shared-prefixed cross-phase sub-agents). The pre-update version is preserved at `ADR-0010-knowledge-skill-frontmatter-correction-pre-naming-convention.md`. The decision recorded in this ADR is unchanged; only entity names are updated for cross-document consistency.
