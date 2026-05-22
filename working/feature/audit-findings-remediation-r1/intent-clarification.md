---
feature_slug: audit-findings-remediation-r1
version: 1.0.0
status: approved
approved_at: 2026-05-21T17:00:00Z
gate_passed: 1
scope_class: FULL
---

# Intent Clarification — audit-findings-remediation-r1

## User intent

> "For the next intent to turn into a PRD I want to address all the findings in the Audit."

Refined through clarifying exchange:

1. **Scope:** all 148 findings (77 BLOCKER + 42 MAJOR + 29 MINOR per the v4.5.0 final audit). No category exempt. ("if there is minor problems we should solve these as well")
2. **Markers OK but disciplined.** Pedagogical-marker disposition is the accepted approach for the false-positive categories, but markers must not become a default that silently swallows real broken links. ("we need to validate and ensure markers do not become a default to actually broken links. We can not silently fail.")
3. **Improve, don't suppress.** Where the auditor itself produces noise (e.g., the X9 MINORs), fix the auditor to produce higher-signal information; do not exempt or suppress findings. ("If what the auditor is providing is noisy lets fix the auditor to provide more value. However, we should not suppress the auditor but improve how it functions.")
4. **Sequencing belongs to downstream stages.** "Sequencing is for the feature pipeline to resolve." This intent document specifies WHAT must be true at acceptance; the Plan and Phase Validators stages decide ordering.

User signal type: continuation. Follows v4.5.0 (ADR-0028) which closed the pipeline skill-design gap; this feature returns to addressing the audit baseline that has accumulated across prior versions.

## Audit state at intent capture

| Severity | Count | Source |
|---|---|---|
| BLOCKER | 77 | v4.5.0 final audit (`/tmp/audit-for-prd.md`, 2026-05-21) |
| MAJOR | 42 | same |
| MINOR | 29 | same |
| **TOTAL** | **148** | |

Categorization (analysis performed during intent refinement):

| Cat | Count | Description | Root cause |
|---|---|---|---|
| A | 31 | Pedagogical false positives (curl\|sh, credential paths, env-var reads, base64 strings in body content) across KB-cc-platform, KB-codespaces-design, KB-codespaces-platform, KB-github-actions-platform | Existing platform KBs predate the pedagogical-marker discipline |
| B | 32 | Broken-link findings to pedagogical example paths (`.claude/CLAUDE.md`, `.devcontainer/devcontainer.json`, `.github/labeler.yml`) | Same as A — KBs reference example paths that exist in target-project repos but not in this one |
| C | 18 | Genuinely stale broken-link refs in non-active project skills (`skills/synthesize/*`, `report-composition-knowledge/output/*`) | Real defects |
| D | 29 | SA-2 sub-agent description lacks triggering language across 29 of 30 agents | Mass surface issue; descriptions don't include "use when" / "when reviewing" phrasing |
| E | 6 | Genuine agent tool/safety-language defects (wildcard shell tools in 3 agents; "bypass approval" phrasing in 3 others) | Real defects |
| F | 29 | X9 MINOR informational ("subagent preloads skills; verify each skill audit passes") | Auditor can't verify recursively; emits low-signal informational |

Categories A + B = 63 marker-discipline-eligible findings. Category C = 18 real-broken-link findings. Categories D + E = 35 sub-agent body/frontmatter findings. Category F = 29 auditor-signal-quality findings.

## Scope

In-scope (the entire 148):

1. **Categories A + B (63 findings):** disposition via pedagogical-marker discipline. Markers must carry inline justification per the discipline below.
2. **Category C (18 findings):** disposition via real fix (delete stale ref, repair link, or rewrite to backticked plain text where the path is genuinely just an example with no resolvable target).
3. **Category D (29 SA-2 findings):** disposition via real fix (rewrite agent descriptions to include explicit triggering language per the auditor's SA-2 check; OR demonstrate that the SA-2 regex itself is too narrow and tighten it — judgment call to Plan stage).
4. **Category E (6 findings):** disposition via real fix per agent (declare tools properly; remove or reword "bypass approval" phrasing).
5. **Category F (29 X9 findings):** TWO-STREAM disposition.
   - **Stream 1 (verification):** run `auditing-skills` against each preloaded skill referenced by each X9-flagged agent. Document the audit pass for each. The X9 findings are valid signals; verification is the real work.
   - **Stream 2 (auditor improvement):** extend the auditor so it can perform the recursive skill check itself, OR redesign the X9 finding to surface higher-signal information (e.g., "skill X has not been audited within N days" rather than the current blanket "verify each preloaded skill"). The auditor's signal quality should be a deliverable.

Constraints (apply across all categories):

6. **Marker discipline — mechanism α.** Every pedagogical-marker addition (frontmatter `pedagogical_sections:` entry OR `audit-example` fence wrap) MUST carry an inline justification — a comment or annotation naming WHY the path/pattern is pedagogical. Format and exact mechanism to be specified in the Blueprint. The auditor MUST reject markers that lack justification (treat as if the marker were absent → original finding stands).
7. **Retroactive application of mechanism α.** Markers already shipped in prior versions (notably `KB-visual-design/references/anti-slop.md` which uses `<pedagogical-example>` HTML-tag markers without inline justifications) MUST be brought up to the new standard. v4.4.0's shipped markers are in-scope.
8. **Process for finding categorization in future.** A repeatable process for distinguishing categories A/B (markerable) from C (real defect) MUST be documented. The current classification was done manually during this intent refinement; a future feature run should be able to follow a documented protocol without re-litigating the false-positive question.
9. **No silent suppression.** No new auditor exemptions, no findings dropped from the report, no severity downgrades except where the marker discipline applies. If a finding's signal quality is the issue, the fix is in the auditor's logic; if a finding's accuracy is the issue, the fix is in the audited content.

Out-of-scope:

- Pre-existing genuine MAJOR `Body references tools ['Bash'] not in declared 'tools:' list` in `review-cross-artifact-auditor.md`. This was identified during v4.5.0 closeout but is not in the 148 count above (it appears in the v4.5.0 audit as the one remaining genuine MAJOR). May ride along but is not a primary scope item.
- Adding new KB content. This feature is remediation, not authoring.
- Changing the agent or pipeline-stage topology (no ADR-0027-class architectural change).

## Acceptance signal

- Post-feature audit reports zero BLOCKER findings.
- Post-feature audit reports zero MAJOR findings (modulo the one pre-existing `Bash` declaration noted out-of-scope).
- Post-feature audit MINOR count strictly decreases (X9 reformulation should reduce or replace the 29 X9 findings with higher-signal output).
- Every marker added has an inline justification per mechanism α.
- The auditor rejects markers lacking justification (verified by a deliberate negative test: a marker added without justification produces a BLOCKER).
- Each Category F preloaded skill has documented audit verification.
- A "finding categorization protocol" document is added to `KB-documentation-criteria/references/disciplines/` enabling future runs to dispose of new findings without re-relitigating category questions.

## Discovery shortcut

This is FULL-scope work. The 13-stage pipeline applies in full:

- Intent Clarification (this document)
- PRD Authoring
- Discovery Planning + Research (the auditor's source code needs investigation for the Category F auditor-improvement stream; categorization protocol needs review against prior pedagogical-marker work)
- Synthesis
- Per-layer Design (likely 1-2 layers active: `design-claude-code` for agent edits + KB content edits; `design-cicd` if Category F auditor improvement touches CI hooks)
- Design Composition (Blueprint authoring)
- Architecture Audit
- Plan Authoring
- Acceptance Test Authoring
- Phase Validator Authoring
- Cross-Artifact Audit
- Reconciliation
- Task Decomposition
- Deliverable Packaging (Stage 13; new in v4.5.0 — first feature run to exercise it natively)

No stage shortcuts justified for this feature.

## Notes for downstream stages

**For PRD:** Translate the scope items above into EARS-format acceptance criteria. Note the four user-stated constraints (numbered 1-4 in "User intent" above) carry the priority signal — they shape WHAT acceptable looks like, not just what to deliver. The mechanism-α discipline is the most consequential single decision in this feature; the PRD should make it a first-class AC, not a footnote.

**For Discovery:** The auditor's current `parse_tools_from_frontmatter` was fixed in v4.5.0 (handles YAML flow-sequence). When extending the auditor for X9 reformulation, the same script's conventions are the existing baseline. The deliverable-archive-spec (v4.5.0) is the relevant spec example for any new marker-justification spec.

**For Per-layer Design:** The marker-discipline mechanism (mechanism α) needs concrete spec — what exactly does an "inline justification" look like in frontmatter and in fence form? Several plausible forms exist; the design must pick one. Likely candidates:
- `pedagogical_sections: [{ path: "references/foo.md", justification: "..." }]` (structured frontmatter)
- `<!-- audit-example: justification text -->\n```...```` (per-block inline)
- A separate `audit-justifications.md` per skill (heavier; probably not)

**For Plan:** Sequencing is explicitly delegated to this stage per user constraint 4. Categories have natural dependencies — mechanism-α spec must land before retroactive marker rework (constraint 7); auditor's marker-rejection check must land before any new markers are added — but ordering within those constraints is the Plan's call.

**For Cross-Artifact Audit:** Watch for tension between constraint 9 (no silent suppression) and Category F Stream 2 (auditor improvement). Reformulating X9 is improvement, not suppression — but the line is fine and should be checked.
