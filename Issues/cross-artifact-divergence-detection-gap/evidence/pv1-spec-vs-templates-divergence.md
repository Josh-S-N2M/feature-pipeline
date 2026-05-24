# PV-1 spec-vs-templates §7 divergence — captured 2026-05-24

This file is **non-validated evidence** (lives under `Issues/<topic>/evidence/` per
`issue-doctypes-spec.md` §2.3). It records the PV-1-specific data point that the parent
analysis.md cites as one of its two evidence threads.

Captured from the in-flight remediation applied during `issue-capture-mechanism-r1` Phase 1
human post-phase review. Cross-references:

- Per-task record: `working/feature/issue-capture-mechanism-r1/per-task-execution-result-task-009.json`
  → `post_phase_remediations[0]`
- Commit: `7b56248` (fix(issue-capture-r1): spec §7 ID-derivation + frontmatter polish)
- Sibling evidence: `evidence/mcp-postmortem-2026-05-24/` (parent-pattern reference)

## What happened

Phase 1 of `issue-capture-mechanism-r1` shipped:

- 3 templates (`issue-register-template.md`, `issue-analysis-template.md`,
  `issue-proposal-template.md`) under `.claude/skills/KB-documentation-criteria/references/templates/`
- 1 canonical structural spec (`issue-doctypes-spec.md`) under
  `.claude/skills/KB-documentation-criteria/references/`
- 1 additive index update to `KB-documentation-criteria/SKILL.md`

The Phase 1 validator (PV-1) reported PASS across all 5 dimensions. Per-task verdicts
were all APPROVED. Phase-quality verdict was PASS.

Post-phase human review surfaced one defect: the spec's §7 ID-derivation rule chose the
LONG-form interpretation of ADR-0050 §Decision §7's ambiguous `<UPPERCASE-DOCTYPE>`
phrasing, while all 3 templates AND all 5 pre-existing empirical precedents in `Issues/`
use the SHORT form.

| Source | ID format example |
|---|---|
| Spec §7 (pre-fix) | `ISSUE-ANALYSIS-foo`, `ISSUE-REGISTER-foo`, `ISSUE-PROPOSAL-foo` |
| Register template (`id:` placeholder) | `REGISTER-<kebab-topic-slug>` |
| Analysis template (`id:` placeholder) | `ANALYSIS-<kebab-topic-slug>` |
| Proposal template (`id:` placeholder) | `PROPOSAL-<kebab-topic-slug>` |
| Empirical: `Issues/analysis-adr-placement-rootcause.md` | `ANALYSIS-adr-placement-rootcause` |
| Empirical: `Issues/register-devcontainer-mcp-provisioning-r1-deferrals.md` | `REGISTER-devcontainer-mcp-provisioning-r1-deferrals` |
| Empirical: `Issues/proposal-auditing-family-graduation-review.md` | `PROPOSAL-auditing-family-graduation-review` |
| Empirical: `Issues/issue-capture-mechanism/proposal.md` | `PROPOSAL-issue-capture-mechanism` |
| Empirical: `Issues/analysis-per-agent-design-evaluation-gap.md` | `ANALYSIS-per-agent-design-evaluation-gap` |

The spec was the outlier — against 3 templates AND 5 empirical precedents — yet PV-1
returned PASS.

## What PV-1 actually checks

| Check | What it verifies | Cross-artifact? |
|---|---|---|
| PV-1.C1 | All 4 new files exist at canonical paths | No (per-file existence) |
| PV-1.C2 | All 4 new files have parseable YAML frontmatter | No (per-file parse) |
| PV-1.C3 | Spec §4 per-state companion-field table byte-matches the **Blueprint** authoritative table | Yes, but only against Blueprint — not against templates |
| PV-1.C4 | None of the 4 new files contains triggering discipline | No (per-file grep) |
| PV-1.C5 | SKILL.md updated additively with 4 new index entries | No (single-file diff check) |
| PV-1.C6 | Optional Gate 0 shared-document-reviewer pass | Per-file structural review |

No check asks: **"do the spec's structural prescriptions match the templates' structural prescriptions, and do both match the empirical precedents?"** That cross-file invariant has no enforcement.

## The blast radius if the defect had shipped unfixed

Phase 2 task T2.1 populates the validator's `ISSUE_PER_STATE_REQUIRED_FIELDS` constant
*from the spec*. If T2.1 derived the ID-prefix rule from spec §7's long-form, the validator
would have:

1. Rejected every existing `Issues/*` file with a `blocker` ID-mismatch finding (their IDs
   use the short form).
2. Rejected the 4 files Phase 3 migrates (they preserve short-form IDs from the precedents).
3. Rejected files produced by the Phase 4 agent (it reads both the spec and the templates;
   runtime conflict on which form to write).

The fix was a ~20-line edit to spec §7 + 3-line frontmatter cleanup, applied pre-Phase-2.
Captured in commit `7b56248` and in the per-task record's `post_phase_remediations[]`
field.

## Why PV-1 didn't catch it

The PV-1 validator set is structured around *per-file* checks plus *spec-vs-Blueprint*
checks (C3). There is no *spec-vs-templates* check, and no *spec-vs-empirical-precedents*
check. The cross-reference exists implicitly in human judgment but has no automated
enforcement.

This is the local instance of a broader pattern catalogued in
`evidence/mcp-postmortem-2026-05-24/02-pipeline-trace.md` §"Cross-cutting pattern
observations" → Pattern P3: *"the current audit dimensions stop at 'the design artifacts
are internally consistent'."*

For the analytical synthesis of the broader pattern (PV-1 gap + MCP postmortem as
instances of the same systemic issue), see the parent `analysis.md`.
