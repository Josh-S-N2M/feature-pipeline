---
id: ADR-0010
version: 1.0.0
status: Accepted
generated: 2026-05-12
generated_by: synth-designer (new ADR for blueprint v3)
supersedes: []
adrs_inherited:
  - ADR-0001 (orchestrator placement)
applies_to:
  - feature-pipeline (blueprint v3, forthcoming)
  - synthesize pipeline (existing, retroactive fix)
---

# ADR-0010: Knowledge skill frontmatter must not combine `disable-model-invocation: true` with `skills:` preload

## Status
Accepted — 2026-05-12

## Context

Research round 2 surfaced a bug in both the existing synthesize pipeline and blueprint v2: every knowledge skill uses the frontmatter combination `user-invocable: false` AND `disable-model-invocation: true` AND expects the skill to be preloaded into sub-agents via the `skills:` field.

Per Anthropic's primary documentation (claim C-R2-0002, source: https://code.claude.com/docs/en/sub-agents):

> Skills that set `disable-model-invocation: true` cannot be preloaded into sub-agents because preloading uses the same skill set that Claude can invoke. If a listed skill is missing or disabled, Claude Code skips it and logs a warning.

This means: every knowledge skill in both pipelines is being silently dropped at sub-agent invocation time. The pipelines have been running with the *agent definitions* loading correctly but the *knowledge skills* failing to load. The agents work because their instructions are in their own bodies; the knowledge-skill content that was supposed to ground their domain awareness is simply absent from their context.

This is a real, current bug. It affects:

- The 6 existing synthesize-pipeline knowledge skills (claim-extraction-knowledge, graph-building-knowledge, critique-knowledge, framing-knowledge, substrate-mapping-knowledge, report-composition-knowledge).
- All 12 new knowledge skills named in blueprint v2 §3.4 (intent-clarification-knowledge through task-decomposition-knowledge, plus document-conventions-knowledge).
- The 13 user-named domain knowledge skills if implemented with the same pattern.

The bug is severity-major: each affected skill silently loses its content at sub-agent load time. Sub-agents fall back to their own body content, which is necessarily shorter and less specific.

## The semantic distinction the bug hides

Per Anthropic documentation (claims C-R2-0002, C-R2-0003):

- **`user-invocable: false`** hides the skill from the `/` menu. It does NOT prevent Claude from auto-invoking the skill when relevant, and it does NOT prevent preloading into sub-agents. Suitable for "background knowledge skills that Claude should access contextually but are not intended as direct user commands."

- **`disable-model-invocation: true`** prevents Claude from auto-invoking the skill. The skill becomes user-trigger-only (via `/name`). This is for actions with side effects or controlled timing. **It also prevents preloading into sub-agents** because preloading uses the same enable-disable mechanism as model auto-invocation.

These were always two distinct fields with distinct semantics. The existing pipeline's pattern combined them, intending "hidden from menu AND not auto-invoked AND preload-via-frontmatter." That intent is not realizable in current Claude Code — the third desire is mutually exclusive with the second.

## Decision

### The correct frontmatter for pipeline knowledge skills

```yaml
---
name: <skill-name>-knowledge
description: |
  <Terse description, key-use-case-first, under 1500 chars total.>
  <When to use: enumerate trigger conditions.>
  <Not for: enumerate what this skill does NOT cover.>
user-invocable: false
---

<Skill body content.>
```

**Required fields:**
- `name`: skill identifier
- `description`: per claim C-R2-0004, capped at 1536 chars per entry; recommended target 600-1000 chars to leave budget for other skills
- `user-invocable: false`: hides from `/` menu (the original intent)

**Forbidden field for knowledge skills:**
- `disable-model-invocation: true` — MUST NOT be set. Setting it breaks subagent preload.

**Optional fields:**
- `allowed-tools`, `context`, `agent`, `when_to_use` — per Anthropic skill schema; use as appropriate.

### Two pipelines affected; both get the fix

**Feature-pipeline (blueprint v3, forthcoming):** all 12 new knowledge skills + 13 domain knowledge skills authored with the correct frontmatter. ADR-0010 is inherited.

**Synthesize pipeline (existing, retroactive fix):** the 6 existing knowledge skills (`claim-extraction-knowledge`, `graph-building-knowledge`, `critique-knowledge`, `framing-knowledge`, `substrate-mapping-knowledge`, `report-composition-knowledge`) need a one-line frontmatter edit: remove `disable-model-invocation: true`.

The synthesize pipeline's correction is a small, mechanical change. It can be applied without re-running the audit or re-publishing the pipeline as a package. Recommended sequence:

1. Edit each of the 6 SKILL.md files: remove the `disable-model-invocation: true` line from frontmatter.
2. Verify the `skills:` references in sub-agent definitions (`synth-extractor`, etc.) still match. They should — only the knowledge-skill frontmatter changed.
3. Re-run the existing audit pipeline (auditing-skills toolkit) against the synthesize pipeline to confirm no regressions.
4. Update the synthesize pipeline's version (v1.x.0 → v1.x.1 patch).

For the feature-pipeline, this ADR is a pre-implementation decision: every new knowledge skill is authored correctly from the start.

### Semantic verification check

After the fix, the pipeline's preflight stage should include a verification:

```
For each sub-agent definition file in .claude/agents/:
  For each skill in the agent's `skills:` field:
    Read .claude/skills/<skill>/SKILL.md frontmatter
    If frontmatter has `disable-model-invocation: true`:
      FAIL preflight with clear error: "<skill> has disable-model-invocation: true which prevents preload; remove the line."
```

This catches the bug in any future skill or in any user-installed skill that violates the convention.

## Consequences

**Positive:**

- Knowledge skills actually load into sub-agents (current behavior: silently dropped). This is the entire reason for the discipline.
- Preflight verification prevents regression in user-authored skills.
- The semantic distinction between the two fields (`user-invocable: false` for hidden-from-menu; `disable-model-invocation: true` for user-trigger-only-with-side-effects) is preserved and used correctly.

**Negative:**

- **Existing pipeline knowledge skills are now AUTO-INVOCABLE by Claude.** Setting only `user-invocable: false` means Claude CAN auto-invoke the skill when its description matches a task context — even in a main session, not just in sub-agents that preload it. This is a behavior change from the previous (broken) state.
  - In practice: when a user invokes the synthesize skill manually, Claude could now auto-load `claim-extraction-knowledge` even outside the synthesize flow if a task context resembles claim extraction. This is mostly harmless (the skill is descriptive content; loading it does no harm) but it does mean the skill descriptions can fire spuriously.
  - Mitigation: write descriptions tightly — `description:` should clearly scope to "Internal knowledge for the synthesize pipeline's <X> stage. Loaded by sub-agents in that pipeline; should not be invoked standalone." The 1536-char cap is sufficient for this scoping.
- The 1% of context budget for skill descriptions (claim C-R2-0004) now includes these knowledge skills since they're discoverable. For pipelines with 12+ knowledge skills, this consumes meaningful description budget. Mitigation: set `skillListingBudgetFraction` higher (e.g., 2%) in `.claude/settings.json` when the pipeline is installed, OR use `skillOverrides` to mark pipeline-internal skills as `name-only` in non-pipeline contexts.

**Neutral:**

- The synthesize pipeline must be patch-versioned to reflect this fix. The fix does not break any agent definitions, slash commands, or hooks — only frontmatter changes.

## Alternatives considered

**Keep `disable-model-invocation: true`; remove `skills:` preload from sub-agent definitions and rely on Claude discovering the skills via description-match.** Considered. Rejected because skill discovery via description is unreliable (claim C-R2-0009: naive tool catalogs degrade selection accuracy to 13%). The pipeline depends on knowledge skills being PRESENT in sub-agent context, not on Claude getting lucky in discovery. Preload is the correct mechanism; the fix is to remove the field that breaks preload.

**Switch to `context: fork` model for knowledge skills.** Anthropic supports `context: fork` for skills that run in isolation as sub-agents. Considered. Rejected because that's a different pattern (skill-as-sub-agent), not "knowledge skill loaded into an existing sub-agent." The two patterns serve different purposes; this ADR addresses the latter.

**Wait for Anthropic to change the semantics** so that `disable-model-invocation: true` AND preload can coexist. Considered. Rejected as not actionable — the current platform behavior is what it is; the pipeline must adapt.

**Add Layer-2 enforcement: the sub-agent's body instructs Claude to "read knowledge skill X content from /skills/<x>/SKILL.md".** Considered. Workable but defeats the purpose of `skills:` preload (which is to inject content at startup without runtime reads). Rejected as a workaround when the proper fix is removing the offending frontmatter line.

## Implementation checklist

For the synthesize pipeline (existing):

- [ ] Edit `.claude/skills/claim-extraction-knowledge/SKILL.md`: remove `disable-model-invocation: true`
- [ ] Edit `.claude/skills/graph-building-knowledge/SKILL.md`: same
- [ ] Edit `.claude/skills/critique-knowledge/SKILL.md`: same
- [ ] Edit `.claude/skills/framing-knowledge/SKILL.md`: same
- [ ] Edit `.claude/skills/substrate-mapping-knowledge/SKILL.md`: same
- [ ] Edit `.claude/skills/report-composition-knowledge/SKILL.md`: same
- [ ] Re-tighten `description:` text in each: scope to internal pipeline use, target 600-1000 chars
- [ ] Re-run auditing-skills against the pipeline; confirm no regressions
- [ ] Patch-version the pipeline (vN.N.X → vN.N.X+1)

For the feature-pipeline (blueprint v3, forthcoming):

- [ ] Author all 12 new knowledge skills + 13 domain stub skills with the correct frontmatter from the start
- [ ] Add preflight verification step that scans sub-agent skills references against skill frontmatter
- [ ] Document the convention in `document-conventions-knowledge` itself so future skill authors follow it

For both pipelines:

- [ ] Reference this ADR in each affected knowledge skill's commit message
- [ ] Confirm `traceability.json` records the supersession (synthesize pipeline) and the new authoring rule (feature-pipeline)

## Evidence

- **C-R2-0002:** Anthropic primary documentation that `disable-model-invocation: true` prevents subagent preload. Source: https://code.claude.com/docs/en/sub-agents. Verified.
- **C-R2-0003:** `user-invocable: false` is the correct field for hidden-from-menu background knowledge skills. Source: https://code.claude.com/docs/en/slash-commands. Verified.
- **C-R2-0004:** Skill description budget at 1% of context window, 8000-char fallback, 1536-char per-entry cap. Source: https://code.claude.com/docs/en/slash-commands. Verified.
- **C-R2-0005:** `skillListingBudgetFraction` setting and `skillOverrides` "name-only" mechanism for managing description budget. Verified.
- **C-R2-0009:** Naive tool catalogs degrade selection accuracy to 13% (Anthropic RAG-MCP research). Justifies preferring preload over discovery.

## Substrate registry version

v1.5 (2026-05-12)

## Cross-stage supersession marker

`cross_stage_supersession: true` for the synthesize pipeline. This ADR mandates a retroactive change to artifacts in another pipeline (the synthesize pipeline's knowledge-skill frontmatter), which is the cross-stage supersession pattern per blueprint v2 §3.9. The synthesize pipeline's existing knowledge skills are NOT individually rewritten (they remain valid as content); only their frontmatter is patched. `traceability.json` should record:

```
- synthesize pipeline knowledge skills (v1.x.0) → v1.x.1
  Reason: ADR-0010 frontmatter correction
  Mechanism: removed `disable-model-invocation: true` from 6 SKILL.md files
  Content changes: none — frontmatter only
```

For the feature-pipeline (blueprint v3, forthcoming), this is a pre-implementation decision and does not constitute supersession of any prior artifact.
