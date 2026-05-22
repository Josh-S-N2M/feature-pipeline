---
id: ADR-0022
version: 1.0.0
status: Accepted
generated: 2026-05-20
accepted: 2026-05-20
generated_by: meta-blueprint maintainer (Phase 2 implementation session, post Batch 8 4-layer fix)
supersedes: []
adrs_inherited:
  - ADR-0009 (rationale brief 3-layer discipline — sub-agent reasoning-load justification fits naturally into the rationale brief)
  - ADR-0019 (naming convention — sub-agents named per the pipeline's role/stage prefix scheme are the subjects of this ADR)
  - ADR-0020 (KB structure — this ADR's discipline lives in KB-cc-platform + KB-cc-design)
applies_to:
  - feature-pipeline blueprint v4.3.1 (and forward)
  - all 30 sub-agents under .claude/agents/
  - design-claude-code Phase 2 design-subsection authoring
  - auditing-subagents skill enforcement (SA-13)
template_format: per ADR.txt v1.0
---

# ADR-0022: Sub-agent reasoning configuration is intentional and audited

## Status

Accepted — 2026-05-20

## Context

During Batch 8 of Phase 2 implementation (May 2026), a pipeline-wide audit surfaced that the 6 synth-* sub-agents carried in from the predecessor synthesize sub-pipeline all referenced a `deep-reasoning` skill in their frontmatter `skills:` arrays:

```yaml
# Example: .claude/agents/synth-critic.md (pre-fix)
skills: [deep-reasoning, verification-knowledge]
```

No `SKILL.md` exists at `.claude/skills/deep-reasoning/SKILL.md` or any other discoverable location. Six `*-knowledge` KBs (`verification-knowledge`, `claim-extraction-knowledge`, `decision-framing-knowledge`, `entity-graph-knowledge`, `substrate-translation-knowledge`, `report-composition-knowledge`) further documented the broken loader pattern in their opening sentences ("Loaded by `synth-X` via `skills: [deep-reasoning, X-knowledge]`"), propagating the lie across 12 files total.

Investigation via the Context7 MCP against `/anthropics/claude-code` and `/ericbuess/claude-code-docs` revealed two relevant facts from the Claude Code Agent SDK documentation:

1. **The `skills:` field preloads SKILL.md *content*.** Per the official `AgentDefinition` dataclass and the sub-agents documentation: "The `skills` field allows preloading skill content into a subagent's context at startup, providing domain knowledge without runtime discovery. This injects the full content of listed skills." Missing references are silently skipped at load time — the sub-agent claims a capability it doesn't have, and runs without complaint.

2. **The documented reasoning-depth control is a separate `effort:` field.** The Claude Code Agent SDK defines `EffortLevel = Literal["low", "medium", "high", "xhigh", "max"]`, where `"high"` is documented as "deep reasoning" and `"xhigh"` as "extended reasoning (Opus 4.7 only; falls back to `high` on other models)." The `effort:` field is independent of `model:` — it controls how eagerly the chosen model spends thinking tokens.

The original synthesize-pipeline author appears to have conflated `effort:` (the reasoning-depth knob) with `skills:` (the SKILL.md preload mechanism). The category error survived the carry-in audit (Batch 1, May 19) because the audit policy in `auditing-subagents/references/subagent-spec.md` already stated the rule — "Each skill must actually exist in a discoverable location → otherwise BLOCKER" — but no script in `auditing-subagents/scripts/` implemented the check. The audit ran clean while broken references persisted across 12 files.

The defect is structurally minor (the pipeline operated correctly because Claude Code silently skipped the missing reference and the substantive reasoning rubrics live in the `*-knowledge` KBs anyway), but it surfaces three larger questions:

- How should sub-agent reasoning capability be configured?
- How is that configuration enforced?
- How is the discipline propagated to all future sub-agent authors?

This ADR records the answers and the mechanisms now in place.

## Decision

Three independent commitments, each addressing one question above.

### Commitment 1 — Reasoning configuration is an intentional triplet

Every sub-agent's reasoning capability is determined by three independent frontmatter fields. Sub-agent authors make each choice deliberately, not by inheriting whatever default the carry-in template happened to use.

| Field | Controls | Values |
|---|---|---|
| `model:` | Which Claude model executes the sub-agent | `sonnet` (default-bounded), `opus` (cross-cutting reasoning), `haiku` (narrow repetitive), `inherit` (defer to parent), or a full model ID |
| `effort:` | How eagerly the chosen model spends thinking tokens (independent of model) | `low`, `medium`, `high` (deep reasoning), `xhigh` (Opus 4.7 only), `max` |
| `skills:` | Domain knowledge preloaded as SKILL.md content (not a reasoning knob) | List of skill names that must resolve to existing `.claude/skills/<name>/SKILL.md` files |

The mapping of design intent to fields:

- "This sub-agent must reason across many artifacts" → set `model: opus`. Examples in this pipeline: `design-composer` (cross-layer reconciliation), `review-cross-artifact-auditor` (CMC posture).
- "This sub-agent must reason deeply within its scope but the scope is bounded" → keep `model: sonnet`, optionally add `effort: high`. The pipeline currently does not use `effort:` explicitly; the reasoning gradient is shaped entirely by the `model:` split.
- "This sub-agent needs domain rubrics / protocols / taxonomies loaded" → add the relevant skill to `skills:`. Verify the SKILL.md exists.

The mapping of NON-intent to fields:

- Wanting deep reasoning does NOT mean adding `skills: [deep-reasoning]` or any similar pseudo-skill. The `skills:` array is not a reasoning-depth control. This is a category error.

### Commitment 2 — Enforcement at audit time

The `auditing-subagents` skill enforces existence of every `skills:` reference. The check is **SA-13** in `references/anti-patterns.md`, implemented in `scripts/validate_subagent_frontmatter.py`. The check walks up the directory tree from the sub-agent file to find `.claude/skills/<name>/SKILL.md` (project-scope), falling back to `~/.claude/skills/<name>/SKILL.md` (user-scope). A missing reference emits **BLOCKER**.

The `effort:` field is also added to the validator's `RECOGNIZED_FIELDS` and documented as an optional reasoning-configuration field in `auditing-subagents/references/subagent-spec.md`.

### Commitment 3 — Discipline propagated to design-time

Two design-time KBs encode the discipline so it applies to all future sub-agent authoring through `design-claude-code` (the CC-layer design sub-agent):

- **KB-cc-platform** (`references/extensions.md`): documents the three-field semantics with a "Reasoning configuration: `model:`, `effort:`, and `skills:` are distinct knobs" subsection. The deep-reasoning trap is named explicitly.
- **KB-cc-design** (`references/principles.md` Principle 9; `references/patterns-and-anti-patterns.md` Reasoning-configured subagent pattern + 2 anti-pattern table rows; `SKILL.md` quick reference): codifies the discipline with worked examples (architecture-reviewer with `model: opus` + `effort: high`).

`design-claude-code`'s Phase 2 Subagent-patterns bullet now explicitly requires, for each new or modified sub-agent in a feature-pipeline design subsection: justification of the `model:` choice, justification of the `effort:` choice when set, and confirmation that every `skills:` entry resolves to an existing SKILL.md.

## Decision Details

| Item | Content |
|---|---|
| Decision | Sub-agent reasoning configuration is intentional. Three independent fields (`model:`, `effort:`, `skills:`) each chosen deliberately per sub-agent's role. Enforcement: auditing-subagents SA-13 (BLOCKER on missing skill reference). Discipline: KB-cc-design Principle 9 + design-claude-code Phase 2 requirement. |
| Why now | The carry-in defect was latent for at least one prior session round; the audit policy declared the rule but no script enforced it; without this ADR the same class of defect can recur on every new sub-agent. v4.3 surfaces this before the pipeline begins production use. |
| Why three fields, not one | The Claude Code Agent SDK documents them as independent. `model:` chooses the model class; `effort:` tunes token-spending within that class; `skills:` preloads SKILL.md content. Collapsing them into one knob loses precision and forces over-provisioning (e.g., using opus when sonnet + effort:high would have been cheaper). |
| Why "intentional" rather than "minimal" | The pipeline uses `model: opus` uniformly across all 30 sub-agents and shapes its reasoning gradient via `effort:` instead — `effort: xhigh` for 5 terminal compositional / gatekeeping agents and `effort: high` for the other 25. "Intentional" captures the calibration target: highest reasoning quality within each agent's role-defined context, with `effort:` chosen per agent rather than inherited. |
| Known unknowns | (a) Whether the `xhigh` vs `high` split (5 vs 25) is empirically right; first 3+ feature runs will calibrate. Specifically, whether per-layer designers benefit from xhigh in cases involving novel layers (e.g., a feature touching a layer with sparse prior KB content). (b) Whether `cc-critique` — a carried-in audit utility outside the feature pipeline — warrants the same opus+high configuration as feature-pipeline agents. Currently uniform with Tier B for cross-agent symmetry. |
| Kill criteria | If 3+ feature runs produce sub-agent outputs of insufficient reasoning quality at the chosen `model:`/`effort:` levels, the discipline should be revisited (specifically: empirically calibrate which sub-agents benefit from opus or from `effort: high`). A follow-up ADR would record the empirical findings. |

## Rationale

**Three knobs are documented; collapsing them loses precision.** The Claude Code Agent SDK explicitly documents three independent fields with three independent semantics. The deep-reasoning defect was precisely a collapse of two of them (`effort:` and `skills:`) into one. An ADR that recommended "always use opus for deep reasoning" would similarly collapse `model:` and `effort:` into one knob, losing the ability to economize on sonnet+effort:high when full opus is unnecessary.

**Carry-in audit gaps surface latent defects.** The deep-reasoning defect was latent since the synthesize pipeline's original authoring. The Batch 1 carry-in audit signed off the 6 `*-knowledge` KBs and the 6 synth-* sub-agents as "complete" without catching the broken reference. The audit policy in `subagent-spec.md` declared the rule; the implementation in `audit_subagent.py` did not. The general lesson: declared audit policies are not sufficient without implemented checks. SA-13 closes one specific gap; future carry-in audits should systematically verify that every declared policy has a corresponding implementation.

**Design-time propagation prevents recurrence.** Adding SA-13 catches the defect when it already exists. Adding Principle 9 to KB-cc-design prevents the defect from being created in the first place — design-claude-code reads KB-cc-design when authoring CC-layer design subsections, so every future sub-agent design subsection must justify its reasoning configuration. The two mechanisms are complementary: design-time discipline is the primary defense, audit-time enforcement is the safety net.

**The pipeline's current configuration: uniform opus, effort-shaped gradient.** Under the operating direction "best model with the best mode for the highest quality output within the context the agent fulfills," the pipeline uses `model: opus` for all 30 sub-agents and shapes the reasoning gradient via `effort:`. Five terminal compositional / gatekeeping agents use `effort: xhigh` (extended reasoning, Opus 4.7); the remaining twenty-five use `effort: high` (deep reasoning). The discipline asks for justification per agent; the calibration target is per-agent role fulfillment.

## Consequences

### Positive

- Future sub-agent authors must justify `model:`/`effort:`/`skills:` choices in the design subsection, surfacing the design reasoning rather than burying it.
- Broken skill references are caught at audit time (BLOCKER), eliminating the silent-skip failure mode.
- The discipline is encoded in three places (KB-cc-platform facts, KB-cc-design discipline, design-claude-code procedure) and enforced in one (auditing-subagents SA-13), giving belt-and-suspenders coverage.
- The deep-reasoning defect class is named explicitly in three KBs and one anti-pattern catalog, making it discoverable by future contributors who might attempt the same conflation.
- Cost economics improve: sub-agents that don't need opus can be confidently kept on sonnet, with `effort:` available as a cheaper escalation lever before going to opus.

### Negative

- Design subsections grow slightly: each new sub-agent now requires justification of three fields rather than implicit defaults. The marginal cost is small (one-to-two sentences per field per sub-agent) and surfaces decisions that would otherwise be implicit.
- The validator's SA-13 check has a small runtime cost per sub-agent audit (filesystem checks for each `skills:` entry). Negligible in practice.
- This ADR introduces a discipline that did not exist in v4.2 and prior; pre-v4.3 sub-agents authored without the discipline must be retrofitted if their configurations are revisited. (The 6 synth-* sub-agents have already been retrofitted as part of the Batch 8 4-layer fix.)

### Neutral

- The pipeline's current sub-agent count and model: distribution are unchanged by this ADR. It records what's already true (deliberate gradient) and enforces continuity going forward.
- The `effort:` field is now available for use but is not currently used by any pipeline sub-agent. Whether to introduce explicit `effort:` configuration is left as a future design decision (see Open Questions below).

## Implementation Guidance

The four-layer implementation that precipitated this ADR is the implementation guidance:

**Layer 1 — Synthesize sub-pipeline cleanup.** Removed `deep-reasoning` from 6 synth-* sub-agent frontmatters and 6 `*-knowledge` KB opening sentences. Verified via project-wide grep: zero remaining `deep-reasoning` references in active configuration. Documentary references (in the auditing-subagents anti-pattern catalog, KB-cc-design anti-pattern table, and KB-cc-platform extensions documentation) are intentional teaching content.

**Layer 2 — auditing-subagents tooling.**
- `scripts/validate_subagent_frontmatter.py` — added SA-13 skills-existence check; added `effort` to `RECOGNIZED_FIELDS` so the validator doesn't fire false-positive MINOR "unrecognized field" warnings.
- `references/anti-patterns.md` — added SA-13 entry (symptom/why-bad/fix); updated Contents from "12 named" to "13 named"; added detection-map row.
- `references/subagent-spec.md` — updated Contents to include `effort field`; added `effort` to optional-fields list; added dedicated `effort field` section with the EffortLevel literal table; updated skills-field audit rules to reference SA-13 by ID; added the "do NOT use skills: for reasoning depth" guidance.

**Layer 3 — Design KBs.**
- KB-cc-platform `references/extensions.md` — subagent frontmatter example now shows `effort: high`; new "Reasoning configuration: `model:`, `effort:`, and `skills:` are distinct knobs" subsection explains the trap.
- KB-cc-design `references/principles.md` — appended Principle 9 with worked example referencing `design-composer` and `review-cross-artifact-auditor`; updated Contents.
- KB-cc-design `SKILL.md` — added "Configure sub-agent reasoning intentionally" pattern and the deep-reasoning anti-pattern to quick reference.
- KB-cc-design `references/patterns-and-anti-patterns.md` — added "Reasoning-configured subagent" pattern with `architecture-reviewer` worked example (`model: opus` + `effort: high`); added 2 anti-pattern rows.

**Layer 4 — design-claude-code procedure.** `.claude/agents/design-claude-code.md` Phase 2 Subagent-patterns bullet expanded to require explicit `model:`/`effort:`/`skills:` justification per KB-cc-design Principle 9, plus existence-confirmation for every `skills:` entry.

**State.json** — Batch 8 post-signoff amendment records all four layers; new carried-forward discipline added ("sub-agent reasoning configuration must be intentional").

For all future sub-agent additions or modifications, the discipline applies prospectively. The discipline is self-policing through design-claude-code's procedure plus auditing-subagents SA-13.

## Related Decisions

- ADR-0009 (rationale brief 3-layer discipline) — sub-agent reasoning-load justification fits the rationale-brief shape naturally; future feature-pipeline runs should include reasoning-configuration justification in the rationale brief when introducing new sub-agents.
- ADR-0019 (naming convention) — sub-agents named per the role/stage prefix scheme are the subjects of this ADR; no naming changes here.
- ADR-0020 (KB structure) — this ADR's discipline lives in two of the KBs defined there (KB-cc-platform facts, KB-cc-design discipline).
- (No ADR conflict.) ADRs 0001-0021 do not constrain sub-agent reasoning configuration; this ADR fills the unspecified design space rather than overriding existing decisions.

## Open Questions

- **Empirical calibration of the xhigh/high split.** The 5-vs-25 tier split is a design-time judgment. First 3+ feature-pipeline production runs may reveal that specific Tier B sub-agents benefit from xhigh in particular feature contexts (e.g., a per-layer designer working on a layer with sparse prior KB content), or that a Tier A sub-agent could economize. A follow-up ADR may record the empirical calibration.
- **Whether the carry-in audit discipline should be strengthened more broadly.** SA-13 closes one specific gap (skills-existence). Other audit policies in `subagent-spec.md` (e.g., total preloaded skill body under ~5,000 tokens) may have similar policy-vs-implementation gaps. A systematic audit of declared-vs-implemented policies across all auditing-* skills is worth doing as a separate exercise. Deferred to follow-up.
- **`cc-critique` placement.** Currently in Tier B (opus + high) for cross-agent symmetry inside `.claude/agents/`. cc-critique is a carried-in audit utility (runs auditing-cc-configs scripts and summarizes findings), not a feature-pipeline agent. Its work is procedural summary, not judgment-heavy reasoning. Defensible either way; promotion-by-symmetry preserved here.
