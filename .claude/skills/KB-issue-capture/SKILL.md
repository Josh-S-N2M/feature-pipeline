---
name: KB-issue-capture
description: Triggering discipline for outside-pipeline issue capture (Issues/<topic-slug>/<doctype>.md). Loaded at runtime by the issue-capture-author sub-agent (NOT auto-invoked by main Claude per F-001). Routes to the 4 references that carry the triage-criteria, approval-prompt rubric, non-pollution contract, and worked examples.
disable-model-invocation: true
allowed-tools: Read, Glob, Grep
---

# KB-issue-capture — Triggering Discipline for Outside-Pipeline Issue Capture

This skill is loaded **at runtime** by the `issue-capture-author` sub-agent (NOT auto-invoked by main Claude). Per F-001 + ADR-0051, capture-the-issue is a SLASH-COMMAND-INVOKED workflow only — main Claude must never auto-detect "I'm noticing X" and write under `Issues/`.

## Contents

- What this KB covers
- What this KB does NOT cover (structural codification → KB-documentation-criteria)
- References (4 files)
- When loaded
- Project firsts

## What this KB covers (triggering discipline)

This KB codifies the **WHEN and HOW** of outside-pipeline issue capture:

- **WHEN to capture** — triage criteria; the rubric for "is this an issue or just a thought?"
- **HOW to classify** — classification of a captured issue into one of 3 doctypes (register / analysis / proposal)
- **HOW to prompt** — wording of the user-facing approval prompt (4 archetypes: create, update, evolve, collision)
- **WHY the non-pollution contract exists** — the structural invariant that keeps the pipeline isolated from outside-pipeline captures
- **WORKED EXAMPLES** — 3 examples paired to the 4 migrated Issues files from Phase 3 (post-migration paths, post-rename doc_type values)

## What this KB does NOT cover

**Structural codification** lives in `KB-documentation-criteria` per ADR-0049. The split is load-semantic: templates are consumed by many pipeline agents (validator, reviewer, composer) that use `skills:` preload — they must NOT inherit `disable-model-invocation: true`. Keeping templates in KB-documentation-criteria preserves that loading path.

Content that lives in KB-documentation-criteria, NOT here:

- Doctype templates: `KB-documentation-criteria/references/templates/issue-register-template.md`, `issue-analysis-template.md`, `issue-proposal-template.md`
- Per-state companion-field spec: `KB-documentation-criteria/references/issue-doctypes-spec.md`
- 5-state lifecycle vocabulary: ADR-0050
- Universal-required frontmatter fields (feature_slug, id, version, status, generated, generated_by): ADR-0032

Do NOT inline structural assertions in this KB's references. When a discipline rule needs to reference a structural shape, cite the template by path only.

## References (4 files)

| Reference | Purpose | Loaded by |
|---|---|---|
| `references/triage-criteria.md` | Doctype classification rubric (register vs analysis vs proposal) | issue-capture-author step 3 (Triage) |
| `references/approval-prompt-rubric.md` | 4 AskUserQuestion archetypes (create / update / evolve / collision) per D-03 | issue-capture-author step 5 (Approval prompt) |
| `references/non-pollution-contract.md` | Structural invariant + pipeline-isolation rationale | shared-document-reviewer Gate 0 + issue-capture-author validation |
| `references/examples.md` | 3 worked examples paired to the 4 migrated Issues files | issue-capture-author when classifying ambiguous topics |

These 4 files are authored by T4.2 (plan anchor). This router cites them by path; it does not inline their content.

## When loaded

This KB is loaded **explicitly** at runtime by the `issue-capture-author` sub-agent via the Read tool (per ADR-0051 + F-003 invariant — the agent does NOT use `skills:` frontmatter preload, which Claude Code silently drops for sub-agents with `disable-model-invocation: true` per F-003). The sub-agent reads:

1. This SKILL.md (first; learns the router structure)
2. The 4 references (as needed, per workflow step)

Main Claude does NOT load this skill. Per F-001, the `disable-model-invocation: true` flag prevents description-match auto-loading.

The closest structural precedent in the codebase is `cc-critique` (CP-001): it also omits `skills:` from its frontmatter and discovers its KB at runtime. That is a structural precedent only — `issue-capture-author` is the first sub-agent to explicitly runtime-Read its discipline KB (project first 4 per Blueprint §Project Precedents Established).

## Project firsts (per Blueprint v3 §Background and Context > Project Precedents Established)

1. **`disable-model-invocation: true`** — this skill is among the first two project skills to declare this Claude Code frontmatter flag (alongside `capture-issue`). Per F-001, no existing SKILL.md in the codebase used this field before this feature run. Prevents description-match auto-loading by main Claude.
2. **Sub-agent runtime KB-load via Read tool** — companion to F-003 mitigation; `issue-capture-author` reads this KB at task start rather than via `skills:` preload (which Claude Code silently drops for sub-agents per F-003 silent-drop BLOCKER constraint). This is the first sub-agent in the project to use the runtime-Read-KB pattern.

## Cross-references

All ADR paths are canonical per ADR-0036:

- ADR-0051 (per-issue folder model): `adrs/ADR-0051-per-issue-folder-model.md`
- ADR-0052 (three doctypes preserved): `adrs/ADR-0052-three-doctypes-preserved.md`
- ADR-0046 (sibling-file evolution): `adrs/ADR-0046-add-new-sibling-file-evolution.md`
- ADR-0047 (three-layer enforcement — KB-issue-capture is Layer 1): `adrs/ADR-0047-three-layer-enforcement.md`
- ADR-0049 (structural-vs-discipline KB split): `adrs/ADR-0049-structural-vs-discipline-kb-split.md`
- ADR-0050 (5-state issues vocabulary): `adrs/ADR-0050-5-state-issues-vocabulary.md`
- `KB-documentation-criteria/SKILL.md` — sibling KB owning structural codification (templates + spec)
