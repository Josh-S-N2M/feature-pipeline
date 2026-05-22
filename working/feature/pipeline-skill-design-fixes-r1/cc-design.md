---
feature_slug: pipeline-skill-design-fixes-r1
version: 1.0.0
status: approved
derived_from: working/feature/pipeline-skill-design-fixes-r1/prd-v1.md
approved_at: 2026-05-21T05:10:00Z
---

# Per-layer Design — Claude Code (cc)

## Layer activation

Single layer: Claude Code (`.claude/agents/` + `.claude/skills/`). No other layer surfaces (Frontend, Backend, API, DB, IaC, GitHub Actions, Codespaces) participate in this feature; the deliverable archive concern is entirely internal to the pipeline tooling.

## Primitives produced

### New sub-agent: `finalize-deliverable-packager.md`

Location: `.claude/agents/finalize-deliverable-packager.md`

Format: matches existing finalize-* agent pattern (YAML frontmatter; markdown body).

Frontmatter:

```yaml
---
name: finalize-deliverable-packager
description: At the Deliverable Packaging stage (added in v4.5.0; runs after finalize-task-decomposer in the orchestrator's sequence), verifies that working/feature/<slug>/ contains the expected artifact set per the feature's declared scope class (FULL / MINOR / PATCH). Invokes shared-document-reviewer with doc_type DeliverableArchive for validation. Optionally produces a versioned handoff document draft (handoff/HANDOFF-v<X.Y.Z>.md) and continuation prompt draft (handoff/CONTINUE_PROMPT-v<X.Y.Z>.md). Emits a structured packager-report.json listing present + missing artifacts and the validator's verdict.
model: opus
effort: medium
tools: [Read, Glob, Grep, Write, Bash, TaskCreate, TaskUpdate]
skills: [KB-documentation-criteria, KB-review-disciplines]
memory: project
---
```

Body sections:

- `## Inputs accepted` — `feature_slug`, `scope_class`, `version_tag`, optional `prior_version_handoff_path`
- `## At task start` — read intent-clarification's `scope_class` field; read spec at `KB-documentation-criteria/references/deliverable-archive-spec.md`
- `## Procedure` — enumerate `working/feature/<slug>/`; compare against expected set; invoke `shared-document-reviewer` with `doc_type: DeliverableArchive`; assemble report
- `## Optional handoff drafting` — if `version_tag` provided, draft `HANDOFF-v<X.Y.Z>.md` and `CONTINUE_PROMPT-v<X.Y.Z>.md` using template from KB-documentation-criteria
- `## Outputs` — `working/feature/<slug>/packager-report.json` + optional handoff drafts
- `## Failure modes` — missing required artifact → BLOCKER; missing conditional → MAJOR with justification check; unexpected artifact → MINOR (forward-compatibility)
- `## Related agents` — `finalize-task-decomposer` (predecessor), `shared-document-reviewer` (invoked for validation)

### New KB reference: `deliverable-archive-spec.md`

Location: `.claude/skills/KB-documentation-criteria/references/deliverable-archive-spec.md`

Format: matches existing KB reference-file pattern (`## Contents` H2; prose + tables; concrete examples; cross-references).

Sections:

1. **What an archive contains by scope class** — tables for FULL / MINOR / PATCH
2. **Required vs conditional artifacts** — which artifacts are unconditionally required vs allowed-to-skip-with-justification
3. **Versioning convention** — how `prd-v<N>.md`, `blueprint-v<N>.md`, `plan-v<N>.md` versions relate (typically aligned, but reconciliation cycles can desync)
4. **ADR placement** — feature-scoped copies at `working/feature/<slug>/adrs/`; project-wide registry at `/adrs/`
5. **Handoff document convention** — `handoff/HANDOFF-v<X.Y.Z>.md` + `handoff/CONTINUE_PROMPT-v<X.Y.Z>.md`
6. **Patterns and anti-patterns** — clean archive vs partial archive vs orphan archive
7. **Cross-references** — ADR-0023 (scope-class taxonomy), ADR-0027 (gap discovery), ADR-0028 (this feature's closure)

### Edit: `recipe-feature-pipeline/SKILL.md`

Add new section after the "Execution Contract" section:

```markdown
## Working-directory precondition

**`cwd` MUST equal the repo root** — the directory containing the `.claude/` configuration tree. All `working/feature/<slug>/` paths in this orchestrator and downstream agents resolve relative to `cwd`. If planning happens in a separate workspace, the orchestrator's first action is to relocate to the repo root or abort.

**Rationale:** ADR-0027 documents the gap that motivated this precondition. Without it, planning artifacts can land in an ephemeral workspace and never reach the deliverable archive.

**Verification:** Stage 1 begins with a precondition check (see Stage 1 procedure). If the check fails, the orchestrator halts before invoking any sub-agent.
```

Plus extension to Stage 1's procedure:

```markdown
### Stage 1 — Intent Clarification

**0. Precondition check.** Verify `cwd / ".claude"` exists. If absent, halt with: "Orchestrator requires cwd == repo root. See ADR-0027."
1. (existing Stage 1 steps follow unchanged)
```

Plus extension to the stage sequence to add post-task-decomposition stage:

```markdown
### Stage 13 — Deliverable Packaging (new in v4.5.0)

After `finalize-task-decomposer` completes, invoke `finalize-deliverable-packager` with `feature_slug` and `scope_class` (from intent-clarification.md). The packager verifies archive completeness and emits `packager-report.json`. If the packager reports BLOCKER findings, surface to the human at the Final Approval Gate.
```

### Edit: `shared-document-reviewer.md`

Extend the `doc_type` taxonomy comment block:

```markdown
4. `doc_type` taxonomy extended with `DeliverableArchive` (v4.5.0 deliverable-archive validation per ADR-0028)
```

Add new section to the body documenting the DeliverableArchive procedure:

```markdown
## DeliverableArchive review

Invoked by `finalize-deliverable-packager` with `target_path: working/feature/<slug>/` and `scope_class: <FULL|MINOR|PATCH>`.

Procedure:

1. Read `KB-documentation-criteria/references/deliverable-archive-spec.md`.
2. Enumerate `working/feature/<slug>/` contents.
3. For each artifact in the spec's expected set for the declared scope class:
   - If unconditionally required AND missing → BLOCKER.
   - If conditional AND missing AND no justification in intent-clarification → MAJOR.
   - If unexpected (in archive but not in spec) → MINOR (forward-compat).
4. Emit findings in standard severity-tagged format.
```

## Dependencies

| Artifact | Depends on |
|---|---|
| `finalize-deliverable-packager.md` | `deliverable-archive-spec.md` (reads it); `shared-document-reviewer` (invokes it) |
| `deliverable-archive-spec.md` | None (standalone reference file) |
| Orchestrator edits | `finalize-deliverable-packager` exists; `deliverable-archive-spec.md` exists |
| `shared-document-reviewer` extension | `deliverable-archive-spec.md` exists |

Build order: spec → packager → reviewer extension → orchestrator edits → retroactive validation test.

## Open questions

None. ADR-0027 + this design fully specify the work.
