---
id: ADR-0049
version: 1.0.0
status: Proposed
generated: 2026-05-23
generated_by: design-composer
supersedes: []
adrs_inherited: [ADR-0011, ADR-0020]
applies_to:
  - issue-capture-mechanism-r1
  - KB-documentation-criteria (3 new templates + 1 new spec + index update)
  - KB-issue-capture (new skill with discipline content)
template_format: per KB-documentation-criteria ADR template v1.0
change_summary: >-
  Structural codification (templates + frontmatter spec) for the three new
  issue doctypes lives in KB-documentation-criteria; triggering discipline
  (when-to-capture, classification rubric, approval-prompt rubric, examples)
  lives in KB-issue-capture. The two KBs have orthogonal responsibilities;
  templates carry no triggering rules; KB-issue-capture cites templates by
  reference. This split prevents duplication and drift across the two
  authoritative surfaces.
---

# ADR-0049: Structural-vs-discipline KB split inside `KB-documentation-criteria`

## Contents

- [x] Status
- [x] Context
- [x] Decision
- [x] Decision Details
- [x] Rationale
- [x] Options Considered
- [x] Consequences
- [x] Architecture Impact
- [x] Implementation Guidance
- [x] Related Information

## Status

Proposed — 2026-05-23 (issue-capture-mechanism-r1; pending Gate 4 user ratification)

## Context

The outside-pipeline issue-capture mechanism introduces two kinds of content that overlap on the same domain:

- **Structural codification.** Templates that codify the body shape of each doctype (CP-004's three observed shapes), a frontmatter spec that codifies the 5-state lifecycle and per-state companion fields (per ADR-0050), and an index update to KB-documentation-criteria's SKILL.md.
- **Triggering discipline.** When does the issue-capture-author classify a notice as `register` vs. `analysis` vs. `proposal`? What's the rubric for the AskUserQuestion's WHY/WHAT/WHERE prompt wording? How does the agent reason about evolution events?

The natural temptation is to colocate everything in one KB — either everything in `KB-documentation-criteria` (because that's where the templates already live per ADR-0011) or everything in `KB-issue-capture` (because that's the new skill the new agent uses). Both colocations have failure modes:

- **Everything in KB-documentation-criteria.** The KB's existing scope (per ADR-0020) is "documentation criteria" — structural templates, frontmatter conventions, EARS-format rules, the 9-layer taxonomy. Adding triggering discipline (when to capture, classification rubric) would extend the KB into "outside-pipeline workflow discipline," which is outside its stated charter. Future readers of KB-documentation-criteria would encounter content that doesn't match the SKILL.md's "what this KB is" framing.
- **Everything in KB-issue-capture.** The triggering discipline naturally belongs in this new KB. But the structural templates (the three doctype templates and the issue-doctypes-spec) are read by readers across the pipeline: `shared-document-reviewer` reads them at Gate 0 for Issues files; `design-composer` may cite them in any cross-cutting Fact Disposition Table; the agent that authors the file reads them at runtime. Putting the templates inside a `disable-model-invocation: true` skill (KB-issue-capture is one) would either force every consumer to do runtime Read/Glob or, worse, would cause the templates to be silently dropped from any sub-agent's `skills:` preload (per F-003 — the same constraint that forced the runtime KB-load pattern for issue-capture-author itself).

The split — templates + structural spec in `KB-documentation-criteria`; triggering discipline in `KB-issue-capture` — separates the concerns by their consumers and their loading semantics. Templates and the spec are read by many pipeline consumers (none of whom should be forced into runtime Read/Glob because of an unrelated discipline KB's `disable-model-invocation` flag); triggering discipline is read only by the issue-capture-author at runtime (which already does runtime Read/Glob per ADR-0047's Layer 1 + F-003 constraint).

PRD §FR-6 codifies the templates-in-KB-documentation-criteria placement. PRD §FR-14 codifies the index update there. The agent body's runtime KB-load (per ADR-0047) loads `KB-issue-capture/SKILL.md` and its references — but reads the templates from `KB-documentation-criteria` separately. This ADR makes the split explicit, names its scope discipline, and prevents duplicate content drift across the two KBs.

## Decision

1. **Structural codification lives in `KB-documentation-criteria`.** The three new templates (`issue-register-template.md`, `issue-analysis-template.md`, `issue-proposal-template.md`) and the new structural spec (`issue-doctypes-spec.md`) land under `KB-documentation-criteria/references/templates/` and `KB-documentation-criteria/references/` respectively. The SKILL.md index gains additive rows for these four files (FR-14).
2. **Triggering discipline lives in `KB-issue-capture`.** The when-to-capture rules, doctype classification rubric, approval-prompt rubric, and worked examples live in `KB-issue-capture/references/` (4 files: `non-pollution-contract.md`, `approval-prompt-rubric.md`, `triage-criteria.md`, `examples.md`).
3. **Templates are STRUCTURAL ONLY.** Per AC-FR-6-b, the templates do NOT include triggering discipline. A reader of `issue-analysis-template.md` sees: frontmatter shape, body skeleton, cross-link guidance — NOT "use this template when you've discovered a root cause." That rule lives in `KB-issue-capture/references/triage-criteria.md`.
4. **KB-issue-capture cites templates by reference.** When the triage-criteria rubric or the approval-prompt rubric needs to refer to a template (e.g., "the analysis template has a numbered evidence section"), it cites the template by path; it does NOT inline the structural content.
5. **Examples.md uses post-migration paths and post-rename doc_type values.** Per Blueprint §Mechanism Designs D-04, the three worked examples in `KB-issue-capture/references/examples.md` cite the four migrated files at their POST-migration paths with their POST-rename `doc_type` values. Examples.md MUST be authored AFTER the FR-8 migration (per ADR-0051) — or in the same atomic commit as the migration.
6. **The KB-documentation-criteria SKILL.md gains a "Where this KB is NOT used" bullet** pointing at KB-issue-capture for triggering discipline. Per FR-14, this is the single index entry that surfaces the split to future readers.

## Decision Details

| Item | Content |
|---|---|
| Decision | Structural codification (templates + spec) in KB-documentation-criteria; triggering discipline (when/how to capture, classification, prompt rubric, examples) in KB-issue-capture; templates are structural-only; KB-issue-capture cites templates by reference. |
| Why now | The two KBs land in this feature run; without an ADR, the split is implicit in the file placement and easily violated in future edits (e.g., a future contributor adding "when to use this template" guidance to the analysis-template.md). |
| Why this | Templates are read by many consumers (validator, reviewer, composer, agent) — none should be forced into runtime Read/Glob because of KB-issue-capture's `disable-model-invocation: true` flag. Triggering discipline is consumed only by the issue-capture-author (which already runtime-loads its KB per ADR-0047 / F-003). The split matches consumer surface and loading semantics. |
| Known unknowns | (a) If a fourth doctype emerges (per ADR-0051/ADR-0052 amendment), the structural template lives in KB-documentation-criteria; the triage criterion lives in KB-issue-capture; the split is preserved by construction. (b) Whether KB-issue-capture might absorb meta-discipline (e.g., a "when-to-evolve" rubric distinct from triage-criteria.md). Current posture: yes — any new discipline content lives in KB-issue-capture per this split. |
| Kill criteria | If contributors repeatedly add triggering content to the templates (or structural content to the KB-issue-capture discipline files) and the auditing-skills / cc-critique surface flags the drift more than three times in six months, revisit. The split would either need stronger structural enforcement (e.g., a validator rule that templates contain no when-to-use prose) or the two-KB model would be revised. |

## Rationale

Three load-bearing reasons the split wins over colocation:

1. **Consumer surface dictates loading semantics.** Templates are read by `shared-document-reviewer` at Gate 0 (the reviewer's `skills:` field includes KB-documentation-criteria; the reviewer needs the templates to load cleanly into context); by `design-composer` when composing Blueprints that cite templates; by the issue-capture-author at runtime; by any future audit-skill that walks the templates directory. All these consumers either use `skills:` preload (which requires the template's host KB to NOT have `disable-model-invocation: true`) or use runtime Read (which is agnostic). Putting templates in KB-issue-capture (which has `disable-model-invocation: true` per ADR-0047) would silently drop them from every consumer's preload (per F-003). Templates MUST live in a discipline-free KB.

2. **Triggering discipline is consumer-narrow.** Only the issue-capture-author needs the triage-criteria rubric, the approval-prompt rubric, and the examples. The agent already runtime-loads its KB (per ADR-0047). Adding this content to KB-documentation-criteria would force every documentation-criteria consumer to load triggering discipline they don't need (token cost on every load); colocating it in KB-issue-capture (the agent's own KB) keeps the token cost where the consumer is.

3. **Drift is prevented by separation.** If both structural and triggering content lived in one KB, a future contributor might colocate them in the same file (e.g., "## When to use this template" inside `issue-analysis-template.md`). The validator (FR-7) would not catch this; auditing-skills would not catch this. The structural split — templates in one KB, discipline in another — makes the wrong placement physically obvious: a "when to use" section inside a template is a different file's content.

The decision honors ADR-0011 (KB-documentation-criteria's scope: structural templates and conventions) and ADR-0020 (KB consolidation: each KB has one responsibility). It extends the precedent set by KB-cc-design (discipline) vs. KB-cc-platform (platform facts) — two KBs with orthogonal responsibilities serving the same Claude Code layer.

## Options Considered

### Option 1: Everything in `KB-documentation-criteria`

All four templates, the spec, the triage criteria, the approval-prompt rubric, and the examples land in one KB.

**Pros:** Single discovery point; readers of one KB find everything.

**Cons:** Extends KB-documentation-criteria's scope beyond "documentation criteria" into "outside-pipeline workflow discipline"; SKILL.md framing diverges from the content; every consumer of KB-documentation-criteria pays the token cost of loading triggering discipline they don't need.

### Option 2: Everything in `KB-issue-capture`

All four templates + spec + discipline content land in the new KB.

**Pros:** Single discovery point for the feature; one KB owns one mechanism end-to-end.

**Cons:** Templates would inherit `disable-model-invocation: true` (since the KB carries the flag); F-003 silent-drop bug fires on every sub-agent that lists KB-issue-capture (and every sub-agent that incidentally loads the templates); `shared-document-reviewer` would need runtime Read/Glob to access templates at Gate 0 — this would be a regression from the current behavior.

### Option 3 (Selected): Split — templates + structural spec in `KB-documentation-criteria`; triggering discipline in `KB-issue-capture`

The two KBs have orthogonal responsibilities; cross-references by path.

**Pros:** Templates loadable by any consumer; triggering discipline scoped to the only consumer that needs it; matches the KB-cc-design ↔ KB-cc-platform precedent (discipline vs. platform); drift is prevented by physical separation; KB-documentation-criteria's scope and SKILL.md framing remain coherent.

**Cons:** Two KBs to maintain instead of one; readers must follow cross-references to see both halves. Mitigation: KB-documentation-criteria's SKILL.md FR-14 update includes a "Where this KB is NOT used" bullet pointing at KB-issue-capture; KB-issue-capture's SKILL.md routes to the templates by path.

## Consequences

### Positive Consequences

- Templates are loadable by every pipeline consumer that uses `skills:` preload (no F-003 silent-drop).
- Triggering discipline is scoped to its only consumer (issue-capture-author), keeping token cost localized.
- KB-documentation-criteria's scope and SKILL.md framing remain coherent ("structural codification only").
- Drift between structural and triggering content is prevented by physical separation; a "when to use" sentence inside a template is a different file's content, immediately obvious to a reader.
- The split establishes the same precedent the KB-cc-design ↔ KB-cc-platform pair set: two KBs with orthogonal responsibilities serving the same layer.

### Negative Consequences

- Two KBs to maintain for one feature. Mitigation: each KB's content is short; maintenance load is low.
- Readers seeking the full picture must follow one cross-reference. Mitigation: KB-documentation-criteria SKILL.md "Where this KB is NOT used" bullet (FR-14) surfaces the cross-reference at the discovery point.
- Future additions of triggering discipline MUST land in KB-issue-capture, not in templates. Drift requires enforcement. Mitigation: cc-critique pre-merge findings catch a "when to use" prose paragraph that sneaks into a template.

### Neutral Consequences

- The KB-documentation-criteria SKILL.md gains 4 additive rows (3 templates + 1 spec) plus 1 bullet (the cross-reference). No removals; no restructure.
- KB-issue-capture's 4 reference files (non-pollution-contract, approval-prompt-rubric, triage-criteria, examples) are the canonical discipline surface for the mechanism.

## Architecture Impact

1. **Layers affected.** Claude Code only.
2. **Components that change.**
   - `KB-documentation-criteria/references/templates/issue-register-template.md` — NEW.
   - `KB-documentation-criteria/references/templates/issue-analysis-template.md` — NEW.
   - `KB-documentation-criteria/references/templates/issue-proposal-template.md` — NEW.
   - `KB-documentation-criteria/references/issue-doctypes-spec.md` — NEW.
   - `KB-documentation-criteria/SKILL.md` — additive index update (FR-14).
   - `KB-issue-capture/SKILL.md` — NEW (with `disable-model-invocation: true` per ADR-0047).
   - `KB-issue-capture/references/non-pollution-contract.md` — NEW.
   - `KB-issue-capture/references/approval-prompt-rubric.md` — NEW (per Blueprint §Mechanism Designs D-03).
   - `KB-issue-capture/references/triage-criteria.md` — NEW.
   - `KB-issue-capture/references/examples.md` — NEW (per Blueprint §Mechanism Designs D-04, AFTER FR-8 migration).
3. **New dependencies introduced.** Cross-reference path from `KB-documentation-criteria/SKILL.md` to `KB-issue-capture` (one bullet in "Where this KB is NOT used"). Cross-reference path from `KB-issue-capture` references to the templates (by path).
4. **Architectural constraints added.** Any future outside-pipeline issue-capture content MUST respect the split. Structural codification → KB-documentation-criteria. Triggering discipline → KB-issue-capture. Templates remain structural-only.

## Implementation Guidance

**For template authors (CC layer).** Templates are structural-only. They document:
- Frontmatter shape (per ADR-0050 5-state lifecycle + ADR-0032 universal-required feature_slug).
- Body skeleton (per CP-004's three observed shapes).
- Cross-link guidance (per ADR-0046, when to add `escalates_from:` / `escalated_to:`).

Templates do NOT document:
- When to use this template (triage criteria — lives in KB-issue-capture).
- How the agent classifies (rubric — lives in KB-issue-capture).
- Approval-prompt wording (rubric — lives in KB-issue-capture).

**For KB-issue-capture authors (CC layer).** The four reference files codify the discipline:
- `non-pollution-contract.md` — why the mechanism exists; the four structural gaps it closes; the pipeline-isolation invariant; forward-reference to ADR-0047.
- `approval-prompt-rubric.md` — the four prompt archetypes (per Blueprint §Mechanism Designs D-03).
- `triage-criteria.md` — the doctype classification rubric.
- `examples.md` — three worked examples (one per doctype) using POST-migration paths (per Blueprint §Mechanism Designs D-04).

When KB-issue-capture content needs to reference a template's structural shape, it CITES the template by path; it does NOT inline the structural content.

**For the KB-documentation-criteria SKILL.md update (CC layer).** FR-14 additive update:
- Add 3 rows to the "Canonical templates" table for the three new templates.
- Add 1 row to the "What's in this KB" table for `issue-doctypes-spec.md`.
- Add 1 bullet to the "Where this KB is NOT used" list: "Triggering discipline for outside-pipeline issue capture (when to capture, doctype classification rubric) — lives in `KB-issue-capture`, NOT here."

**Drift prevention.** A reviewer (or cc-critique) seeing prose inside a template that says "use this template when…" should flag this as a discipline-in-structural-KB violation. The fix is to move the prose to `KB-issue-capture/references/triage-criteria.md`.

No procedural detail beyond the above — exact template body content lives in Blueprint §Templates and KB Edits.

## Related Information

- Related ADRs:
  - ADR-0051 (per-issue folder model — the filesystem layout the templates encode)
  - ADR-0052 (three doctypes preserved — the three templates this split codifies)
  - ADR-0046 (add-new-sibling evolution — cross-link fields documented in templates and triage rubric)
  - ADR-0047 (three-layer enforcement — KB-issue-capture is Layer 1's skill with `disable-model-invocation: true`)
  - ADR-0050 (5-state lifecycle — frontmatter shape documented in the structural spec)
  - ADR-0011 (KB-documentation-criteria scope — this ADR extends but does not violate)
  - ADR-0020 (KB consolidation discipline — one responsibility per KB; this split honors it)
- Referenced specs / docs: PRD §FR-6 (three new templates + one new spec, structural only); PRD §FR-14 (index update with the cross-reference bullet); PRD §AC-FR-6-b (templates do not include triggering discipline); Blueprint §Templates and KB Edits; codebase-analysis CP-004 (three doctype body shapes — the template content source); CP-007 (universal-required feature_slug per ADR-0032).
- Related KBs: KB-documentation-criteria (templates + structural conventions); KB-issue-capture (discipline + triage + examples — NEW); KB-cc-design ↔ KB-cc-platform precedent (the same KB-pair pattern).
