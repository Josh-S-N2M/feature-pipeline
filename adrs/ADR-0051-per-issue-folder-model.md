---
id: ADR-0044
version: 1.0.0
status: Proposed
generated: 2026-05-23
generated_by: design-composer
supersedes: []
adrs_inherited: [ADR-0032]
applies_to:
  - issue-capture-mechanism-r1
  - Issues/ outside-pipeline issue surface (project-wide)
  - any future outside-pipeline issue capture
template_format: per KB-documentation-criteria ADR template v1.0
change_summary: >-
  Outside-pipeline issues are organized as one folder per topic at
  Issues/<topic-slug>/ with three fixed canonical doctype filenames
  (register.md, analysis.md, proposal.md). Doctype is encoded by filename;
  topic by folder name. Optional evidence/ and updates/ subdirectories are
  permitted for non-doctype artifacts.
---

# ADR-0044: Per-issue folder model for `Issues/`

## Contents

Section completion checklist — each box must be checked (including `N/A — out of scope` rows) before this document leaves draft. The reviewer's Gate 0 check uses this list as the structural-presence anchor.

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

The project has accumulated four empirically-authored `Issues/*.md` files in a flat (one-file-per-issue) layout: `Issues/register-devcontainer-mcp-provisioning-r1-deferrals.md`, `Issues/analysis-per-agent-design-evaluation-gap.md`, `Issues/analysis-adr-placement-rootcause.md`, `Issues/proposal-auditing-family-graduation-review.md` (codebase-analysis F-005, F-009). These four files demonstrate three structurally distinct body shapes (CP-004: register tabular; analysis TL;DR+evidence; proposal prose+adoption-guidance) and prove that real-world issue captures already evolve across doctypes (an analysis can mature into a proposal; a proposal can be informed by a prior register).

The flat layout has four observable failure modes:

1. **No natural place for sibling doctypes.** When an analysis at `Issues/analysis-foo.md` matures into a proposal, the flat layout has no obvious place for the proposal — either `Issues/proposal-foo.md` (parallel naming, no folder grouping) or some ad-hoc renaming. Neither is enforced.
2. **No natural place for supporting evidence.** The `agent-roster-impact-matrix.md` that informs `analysis-per-agent-design-evaluation-gap.md` currently lives at `working/feature/devcontainer-mcp-provisioning-r1/agent-roster-impact-matrix.md` — an unrelated feature's working directory — because the flat layout offers no `evidence/` subdirectory.
3. **Filename encodes both topic and doctype.** Renaming the doctype (e.g., `analysis-` → `analysis-`) implies a file move; the topic slug and the doctype prefix are conflated.
4. **No id-derivation rule that survives evolution.** The frontmatter `id: ANALYSIS-foo` works for one file but cannot be re-derived for a sibling `id: PROPOSAL-foo` without explicit knowledge that both files share the topic.

The proposal seed for this feature (`Issues/issue-capture-mechanism/proposal.md`) already anticipates the per-issue-folder model in its `companion_artifacts` list and demonstrates the canonical filename pattern (`Issues/<topic-slug>/proposal.md`). The PRD's FR-4 codifies the model. This ADR makes the architectural commitment explicit and ratifies the supporting decisions (canonical filenames, optional subdirectories, id-derivation rule).

## Decision

1. **One folder per topic.** Every captured issue lives under `Issues/<topic-slug>/`, where the folder name is the kebab-case, lowercase topic identifier.
2. **Three fixed canonical doctype filenames.** Inside a topic folder, the three doctype files use exactly these three filenames: `register.md`, `analysis.md`, `proposal.md`. No other names encode a doctype; no other names are validated as doctype files.
3. **Doctype encoded by filename; topic by folder name.** The two coordinates are orthogonal. Renaming a topic (folder) does not change the doctype encoding; adding a sibling doctype does not change the topic.
4. **Optional subdirectories `evidence/` and `updates/`.** A topic folder MAY contain these two subdirectories for non-doctype artifacts. Files inside `evidence/` and `updates/` are NOT validated as doctype files and MAY carry any frontmatter shape. They are explicitly excluded from FR-7's validator extension.
5. **id-derivation rule.** Frontmatter `id:` is derived from the path: `<UPPERCASE-DOCTYPE>-<kebab-topic-slug>`. E.g., `Issues/per-agent-design-evaluation-gap/analysis.md` → `id: ANALYSIS-per-agent-design-evaluation-gap`.
6. **No silent overwrite.** If a write target at `Issues/<topic-slug>/<doctype>.md` already exists, the issue-capture-author agent presents a re-prompt with three options (supersede / rename / cancel) per AC-NFR-5-a; the existing file is preserved unless the user explicitly selects supersede.

## Decision Details

| Item | Content |
|---|---|
| Decision | Issues/ uses a per-folder-per-topic model with three fixed canonical doctype filenames (register.md, analysis.md, proposal.md). |
| Why now | Four pre-migration flat files already exhibit the structural failure modes the folder model resolves; FR-8 migration of those four files is in scope this run; without an ADR, the model is implicit in the templates and the agent body. |
| Why this | Empirical precedent: the proposal seed (`Issues/issue-capture-mechanism/proposal.md`) already uses this layout; the three doctype shapes (CP-004) map cleanly to three fixed filenames; orthogonality of topic+doctype enables sibling-file evolution (ADR-0046) without flat-layout renames. |
| Known unknowns | (a) Whether future doctypes (beyond register/analysis/proposal) emerge; if so, an amendment ADR extends the fixed-filename set. (b) Whether `evidence/` and `updates/` ever need their own validator rules; current posture is "no validation" — amendable later. |
| Kill criteria | If a fourth doctype proves necessary and cannot be modeled cleanly within the fixed-filename set, an amendment ADR is required (not a supersession — the model would extend, not replace). If the orthogonal topic+doctype encoding ever forces awkward workarounds in real captures, revisit. |

## Rationale

Three load-bearing reasons the per-folder-per-topic model wins over the flat alternative:

1. **Sibling-doctype evolution is a real workflow.** Per ADR-0046 (add-new-sibling-file evolution), an issue maturing from analysis to proposal adds a new file alongside the older one. The flat layout has no natural sibling slot. The folder layout makes the relationship trivial: both files live in the same folder, named by their doctype.
2. **Evidence belongs near the issue.** The `agent-roster-impact-matrix.md` migration (FR-9) demonstrates the evidence-attachment use case. A per-issue `evidence/` subdirectory keeps supporting artifacts adjacent to the file that interprets them; a flat layout forces evidence to live in feature-pipeline working directories that may be cleaned periodically.
3. **id-derivation becomes mechanical.** With the orthogonal encoding, `id` is fully determined by the path. The validator (FR-7) can derive the expected `id` from the file's location and verify the frontmatter declaration matches — a structural correctness check the flat layout cannot mechanize.

The decision honors KB-cc-design Principle 5 (one source of truth — the doctype lives in the filename, not in the frontmatter doc_type field; the validator cross-checks the two for consistency) and KB-documentation-criteria Principle 1 (skill-localized knowledge — the template files codify the structural shape).

## Options Considered

### Option 1: Flat layout (status quo, pre-this-feature)

`Issues/<doctype>-<topic-slug>.md` — one file per issue, doctype as filename prefix.

**Pros:** Familiar; no migration cost; tooling sees flat directory.

**Cons:** No sibling-doctype slot (evolution requires either rename or parallel files with no grouping); no evidence-attachment surface; topic+doctype conflated in filename; observed failures in current 4-file corpus (the agent-roster-impact-matrix lives in an unrelated feature directory because flat layout offered no home).

### Option 2 (Selected): One folder per topic, three fixed canonical doctype filenames

`Issues/<topic-slug>/{register,analysis,proposal}.md` — folder by topic; fixed filename by doctype.

**Pros:** Sibling-doctype evolution is natural (just add another file in the same folder); evidence/updates subdirectories have a home; topic+doctype orthogonal; id-derivation mechanical; aligns with the proposal seed's actual layout.

**Cons:** Migration cost (4 files); validator must check doctype-filename consistency; the fixed filename set is closed (extending requires amendment ADR).

### Option 3: One folder per topic, doctype in frontmatter only (no fixed filename)

`Issues/<topic-slug>/<freely-named>.md` — folder by topic; doctype derived from `doc_type:` frontmatter.

**Pros:** More flexible naming.

**Cons:** Loses the bidirectional filename/doctype check; readers must open the file to know the doctype; tooling (validator, grep, agent body) cannot use filename as a dispatch signal. Rejected — flexibility here is not load-bearing.

## Consequences

### Positive Consequences

- Sibling-doctype evolution (per ADR-0046) becomes a structural pattern, not a workaround.
- Evidence and updates have a canonical home (`evidence/`, `updates/` subdirectories).
- `id` derivation is mechanical, validator-enforceable.
- Filename-collision detection is unambiguous: the validator and the agent body see the same canonical path shape.
- The empirical precedent (proposal seed) is normalized as the standard.

### Negative Consequences

- One-time migration of 4 existing files (FR-8) plus the agent-roster-impact-matrix (FR-9). Mitigated by atomic `git mv` with frontmatter back-fill in one commit per file (per ADR-0048 D-13 sequencing).
- The fixed canonical filename set (`register.md`, `analysis.md`, `proposal.md`) is closed. Extending it requires an amendment ADR. Mitigation: deliberate constraint — the three doctypes are empirically grounded (CP-004) and surfacing a fourth is itself an architectural event.
- Any tooling that consumed flat `Issues/*.md` paths must update. Current observable consumer: the four files' own cross-references. Migration commit updates referrers in lockstep.

### Neutral Consequences

- The `Issues/` top-level structure becomes a directory of directories instead of a directory of files. Visually different; structurally neutral.
- `git log --follow` continues to work across the rename (verified by D-13 dry-run procedure in ADR-0048).

## Architecture Impact

1. **Layers affected.** Claude Code / Project Filesystem (the `Issues/` surface and the issue-capture-author agent that writes to it). Backend layer indirectly: the validator extension (FR-7) consumes the doctype-encoding rule to dispatch its new `issue` category branch.
2. **Components that change.**
   - `Issues/` directory structure — flat → per-folder-per-topic.
   - issue-capture-author agent body (in §Sub-Agent Patterns of the Blueprint) — writes to `Issues/<topic-slug>/<doctype>.md`, computes `id` from path.
   - validate_pipeline_frontmatter.py — the new `validate_issue_artifact` function checks that the frontmatter `id` matches the path-derived expectation.
3. **New dependencies introduced.** None at runtime. The rule is a discipline + structural convention.
4. **Architectural constraints added.** Any future outside-pipeline doctype must either (a) extend the fixed canonical filename set via an amendment ADR, or (b) live as a non-doctype artifact under `evidence/` or `updates/`.

## Implementation Guidance

**For issue-capture-author (CC layer).** Compute the write target as `Issues/<topic-slug>/<doctype>.md` from the (topic-slug, doctype) pair derived from classification (Blueprint §Mechanism Designs D-04). On filename collision, present the three-option re-prompt (Blueprint §Mechanism Designs D-03 archetype 3). Never write outside `Issues/` from this agent.

**For the validator extension (Backend layer).** In `validate_issue_artifact`, verify:
- The file path matches `Issues/<topic-slug>/<doctype>.md` where doctype ∈ {register, analysis, proposal}.
- Frontmatter `id:` matches `<UPPERCASE-DOCTYPE>-<kebab-topic-slug>` derived from the path.
- Files under `Issues/<topic-slug>/evidence/` and `Issues/<topic-slug>/updates/` are skipped (no doctype validation applied).

**For FR-8 / FR-9 migration.** Per ADR-0048, the migration commits are atomic `git mv` + frontmatter back-fill in one commit per file, with cross-references updated in the same commit.

No procedural detail beyond the above — step-by-step migration is a Plan-author concern.

## Related Information

- Related ADRs:
  - ADR-0045 (three doctypes preserved as distinct — the doctypes this model encodes)
  - ADR-0046 (add-new-sibling-file evolution pattern — operates on this model)
  - ADR-0047 (three-layer enforcement — the agent that writes into this model)
  - ADR-0048 (prior-context handoff — relies on `Issues/<topic>/proposal.md` paths)
  - ADR-0049 (structural-vs-discipline KB split — templates codifying this model live in KB-documentation-criteria)
  - ADR-0050 (5-state lifecycle vocabulary — applies to files in this model)
  - ADR-0032 (universal-required `feature_slug` — preserved on files in this model)
  - ADR-0005 (supersession discipline — `supersede` option in collision re-prompt honors this)
  - ADR-0036 (single-location ADR placement — applies to this ADR file)
- Referenced specs / docs: PRD §FR-4 (per-issue folder model); PRD §Product Policy Decisions row "Doctype preservation"; codebase-analysis F-005 (pre-migration files); CP-004 (three doctype body shapes); blueprint §Per-Issue Folder Model.
- Issues / PRs: `Issues/issue-capture-mechanism/proposal.md` (the seed proposal that anticipated this layout).
- Related KBs: KB-cc-design (Principles 1, 5); KB-documentation-criteria (template-only structural codification of the doctype shapes).
