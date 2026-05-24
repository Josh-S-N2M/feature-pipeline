---
id: ANALYSIS-adr-placement-rootcause
doc_type: analysis
status: draft
generated: 2026-05-23
generated_by: claude (orchestrator) — manual analysis
feature_slug: devcontainer-mcp-provisioning-r1
scope: pipeline-wide (not feature-scoped)
mode: report-only
---

# Feature-Pipeline Analysis — ADR Placement: Dual-Location Drift & Phantom-Promotion Root Cause

## TL;DR

ADR-0036 (accepted 2026-05-22) **retired** the dual-location ADR convention and mandated a single canonical location at root `adrs/`. The amendment was applied to one file (`deliverable-archive-spec.md`) but **never propagated** to the four files that actually drive ADR placement and verification: the orchestrator `SKILL.md`, `design-composer.md`, `finalize-deliverable-packager.md`, and the DeliverableArchive check inside `shared-document-reviewer.md`. The current feature run (`devcontainer-mcp-provisioning-r1`) inherits this gap, writes 5 ADRs to `working/feature/<slug>/adrs/` only, and invents a fictitious "promotion at deliverable packaging time" step in its own Blueprint to bridge the contradiction. **No promotion mechanism exists anywhere in the codebase.** If the packager runs today, it will BLOCKER on missing root-level ADR copies because its spec was never updated.

The bug is **not** about whether single- or dual-location is correct (ADR-0036 already decided that). It is about a **partially-applied amendment** that leaves the pipeline in an inconsistent state with no defined steady-state behavior — which is exactly the staleness/drift failure mode you described.

---

## 1. Evidence — current ADR inventory

### 1.1 Three ADR roots exist

| Location | ADR count | Range | Status |
|---|---|---|---|
| [adrs/](../adrs/) | 26 | 0011–0036 | Canonical per ADR-0036 |
| [adrs-migrated/](../adrs-migrated/) | many | 0001–0018+ (multiple versions each) | Pre-naming-convention migration archive; **never relocated** |
| [working/feature/<slug>/adrs/](../working/feature/devcontainer-mcp-provisioning-r1/adrs/) (×5 features) | 12 | 0024, 0026, 0028, 0029, 0030, 0031, 0037–0041 | Feature-scoped; **status undefined** post ADR-0036 |

### 1.2 Duplication and drift already realized

| ADR ID | Root copy? | Feature copy? | Byte-identical? |
|---|---|---|---|
| ADR-0024 | yes | [frontend-design-knowledge-r1/adrs/](../working/feature/frontend-design-knowledge-r1/adrs/) | **NO — drifted** |
| ADR-0026 | yes | [audit-machinery-fixes-r1/adrs/](../working/feature/audit-machinery-fixes-r1/adrs/) | yes (clean copy) |
| ADR-0028 | yes | [pipeline-skill-design-fixes-r1/adrs/](../working/feature/pipeline-skill-design-fixes-r1/adrs/) | yes |
| ADR-0029 | yes | [audit-findings-remediation-r1/adrs/](../working/feature/audit-findings-remediation-r1/adrs/) | yes |
| ADR-0030 | yes | [audit-findings-remediation-r1/adrs/](../working/feature/audit-findings-remediation-r1/adrs/) | yes |
| ADR-0031 | yes | [audit-findings-remediation-r1/adrs/](../working/feature/audit-findings-remediation-r1/adrs/) | yes |
| ADR-0037–0041 | **NO** | [devcontainer-mcp-provisioning-r1/adrs/](adrs/) | n/a — root copies don't exist |

ADR-0024 has **already drifted** — same ADR ID, two different bodies, no validator detects diff. That is the failure mode you predicted, made real. The current run's ADRs (0037–0041) are an even worse state: the feature copy is the only copy, yet ADR-0036 says the root copy is canonical.

### 1.3 The current Blueprint's own statement is internally inconsistent

[blueprint-v2.md:1226](../working/feature/devcontainer-mcp-provisioning-r1/blueprint-v2.md#L1226) — the design-composer wrote:

> "ADRs authored in this Blueprint (in `working/feature/devcontainer-mcp-provisioning-r1/adrs/`; promoted to `/workspaces/feature-pipeline/adrs/` at deliverable packaging time per ADR-0036)"

This phrase **misrepresents ADR-0036**. The ADR text (lines 73–79, 158–164) prescribes: write the ADR **once at `adrs/`**, do **not** create a feature-scoped directory, **no promotion step exists**. The Blueprint invents a "promoted at packaging time" rule that has no implementation anywhere.

---

## 2. Root cause — the amendment was applied in one file and forgotten in four

ADR-0036 was authored at Gate-6 of `execution-pipeline-design-r1` (2026-05-22). The user accepted "Option 3: amend the spec." The spec amendment landed in [deliverable-archive-spec.md](../.claude/skills/KB-documentation-criteria/references/deliverable-archive-spec.md) §"ADR placement convention" (lines 136–150) and §"Patterns and anti-patterns" (line 164). **It was not propagated to the operational agent/orchestrator files that govern the actual write and verify steps.** Evidence per [grep across .claude/](../.claude/): only 5 files reference ADR-0036; the three pipeline operators are not among them.

### 2.1 Causal site 1 — orchestrator never updated

[.claude/skills/recipe-feature-pipeline/SKILL.md:17-28](../.claude/skills/recipe-feature-pipeline/SKILL.md#L17-L28)

> **Outputs produced (under `working/feature/<slug>/`):**
> | Path | Source agent | Stage |
> | `blueprint-v<N>.md` + `adrs/ADR-<NNNN>.md` (×0..M) | design-composer | Design Composition |

The table header roots **every** path under `working/feature/<slug>/`. The `adrs/ADR-<NNNN>.md` entry, read literally, resolves to `working/feature/<slug>/adrs/ADR-<NNNN>.md` — feature-scoped, in direct contradiction to ADR-0036.

[.claude/skills/recipe-feature-pipeline/SKILL.md:228](../.claude/skills/recipe-feature-pipeline/SKILL.md#L228) — the dispatch step for design-composer:

> `prd_path, per_layer_designs_dir, per_layer_dependencies_dir, codebase_analysis_path, research_notes_dir, synthesis_path, rationale_brief_path, existing_adrs_dir, output_blueprint_path, **output_adrs_dir**, slug`

`output_adrs_dir` is **parameterized**, not pinned. The orchestrator's instructions never tell the runtime what concrete value to pass. The default in convention (everything under `working/feature/<slug>/`) computes to the feature-scoped path. There is no statement like "for ADRs specifically, `output_adrs_dir = adrs/` (project root)."

### 2.2 Causal site 2 — design-composer never updated

[.claude/agents/design-composer.md:48](../.claude/agents/design-composer.md#L48):
> `output_adrs_dir` — directory where any new ADRs you author land.

[.claude/agents/design-composer.md:129](../.claude/agents/design-composer.md#L129):
> Write to `output_adrs_dir/ADR-<NNNN>.md`. Use the next available ADR number (read existing ADRs to find the highest, increment).

The agent dutifully writes wherever `output_adrs_dir` points. No invariant check ("if `output_adrs_dir != adrs/`, refuse to write"). No reference to ADR-0036. When the current feature run's orchestrator passed `working/feature/<slug>/adrs/` (because that's the convention default), the agent complied — and the misreading of ADR-0036 in blueprint-v2 line 1226 followed because the composer was rationalizing the contradiction between (a) where it had just written and (b) what ADR-0036 (which is in its inherited-ADR set, [blueprint-v2.md:35](../working/feature/devcontainer-mcp-provisioning-r1/blueprint-v2.md#L35)) says.

### 2.3 Causal site 3 — packager still enforces dual-location BLOCKER

[.claude/agents/finalize-deliverable-packager.md:56-63](../.claude/agents/finalize-deliverable-packager.md#L56-L63):

> **3. ADR cross-location check**
> For each ADR ID listed in Blueprint's `adrs_authored`:
> - Verify `working/feature/<slug>/adrs/ADR-NNNN-<slug>.md` exists → **BLOCKER if missing**.
> - Verify `adrs/ADR-NNNN-<title>.md` exists in project registry → **BLOCKER if missing**.

This is the **retired** pre-ADR-0036 check, still in force. If the packager runs against the current feature, it BLOCKERS on the second line (root copies don't exist). If a future feature obeys ADR-0036 and writes only to root, it BLOCKERS on the first line. **Either compliance path fails.**

### 2.4 Causal site 4 — shared-document-reviewer internally contradicts itself

The reviewer's DeliverableArchive doc_type handler still runs the retired check:

[.claude/agents/shared-document-reviewer.md:349](../.claude/agents/shared-document-reviewer.md#L349):
> 6. ADR cross-location check: for each ADR ID in Blueprint's `adrs_authored:` frontmatter, verify presence at both `working/feature/<slug>/adrs/ADR-NNNN-<slug>.md` AND `adrs/ADR-NNNN-<title>.md` (matched by ID). **Missing at either → BLOCKER.**

…while the same file 123 lines later correctly states the post-ADR-0036 rule:

[.claude/agents/shared-document-reviewer.md:470-472](../.claude/agents/shared-document-reviewer.md#L470-L472):
> ### ADR placement (per ADR-0036)
> When reviewing ADRs, expect a single canonical location: `adrs/ADR-NNNN-<slug>.md` at project root. **Do NOT flag absence of a `working/feature/<slug>/adrs/` mirror copy — that convention is retired.**

A file that contradicts itself in two procedures — depending on which check the runtime invokes first, the verdict differs.

### 2.5 No promotion machinery exists

A `grep -rln -iE "adr.*promot|promote.*adr|copy.*adr|cp.*adrs" /workspaces/feature-pipeline/.claude/` returns only [deliverable-archive-spec.md](../.claude/skills/KB-documentation-criteria/references/deliverable-archive-spec.md) — and there the term appears only in the **superseded** Pattern that ADR-0036 retired. No script, no hook, no agent step copies files from `working/feature/<slug>/adrs/` to `adrs/`. The eight scripts in [auditing-shared/scripts/](../.claude/skills/auditing-shared/scripts/) handle stub detection, frontmatter validation, phase quality, pedagogical-marker checks, secrets scan, smoke test, state-transition logging, and pipeline discipline — none touch ADRs. The `handoff/` directory contains versioned `HANDOFF-vX.Y.Z.md` notes; it does not contain ADRs.

The "promoted at deliverable packaging time" phrase the current Blueprint invented at [blueprint-v2.md:1226](../working/feature/devcontainer-mcp-provisioning-r1/blueprint-v2.md#L1226) describes a step that has no implementation, no agent owner, and no trigger. It is a **phantom step**.

---

## 3. Why this produces the staleness mechanism you described

You asked whether ADRs that are never promoted go stale (no longer apply after the feature pipeline completes). The answer is yes, by **four** distinct mechanisms — all rooted in the same partial-amendment cause:

1. **Authoritative-state drift.** An ADR authored at status `Accepted` is a project-wide constraint. While it sits only at `working/feature/<slug>/adrs/`, downstream features and audits that consult root `adrs/` cannot see it. They proceed as if the constraint does not exist. The constraint becomes silently invalid as the codebase moves on. (Already realized for ADR-0024 — root copy and feature copy carry different content; whichever a reader picks determines the project rule.)

2. **Supersession invisibility.** ADR-0038 in the current run declares `supersedes: ADR-0018 v1.0.0`. Until ADR-0038 reaches root `adrs/`, root readers still see ADR-0018 as live. The supersession is effective only inside the feature directory — i.e., not at all for cross-feature consumers. This is the staleness-via-silence failure.

3. **Numbering-collision risk.** Design-composer assigns ADR numbers by reading "existing ADRs to find the highest" ([design-composer.md:129](../.claude/agents/design-composer.md#L129)). The composer needs `existing_adrs_dir` to point at the canonical pool. If two parallel feature runs both look at root, they collide on N. If one looks at root and the other at a feature dir, they collide differently. ADR-0036 implicitly requires root as the single numbering authority, but the orchestrator never specifies this; the current feature happens to have picked 0037–0041 by reading root (which ended at 0036), but this is luck, not enforcement.

4. **Phantom-promotion blocks closure.** Because the Blueprint claims a promotion step that no agent performs, the feature can never legitimately "close": (a) the packager's BLOCKER check at line 61 fires (root copies missing), or (b) if the packager check is patched to ignore root, the Blueprint is now describing a non-existent step, and downstream features that inherit this Blueprint inherit the misreading. Closure is gated by a step that doesn't exist.

A second-order staleness mechanism — the [adrs-migrated/](../adrs-migrated/) directory — sits orthogonally. ADRs 0001–0010 (and earlier versions of 0011–0018) live there exclusively. [blueprint-v2.md:379](../working/feature/devcontainer-mcp-provisioning-r1/blueprint-v2.md#L379) notes "ADR-0007 currently lives in `adrs-migrated/`; ADR-0038 relocates per ADR-0036" — meaning even before ADR-0036, the canonical-single-location rule was already violated for the legacy ADRs. This is a separate issue but stems from the same family of problems: amendments and reorganizations that touch one file and leave others behind.

---

## 4. Where the bug sits, structurally

The bug is **not** in any one of the four out-of-sync files individually. It sits in the **process** that ratified ADR-0036 without producing a mechanical change-list. ADR-0036 itself says (line 134, "Files amended"):

> - `.claude/skills/KB-documentation-criteria/references/deliverable-archive-spec.md` — §ADR placement convention rewritten; Pattern at the original line 157 rewritten; cross-reference to this ADR added.

…and (line 138, "Files created"):

> - `adrs/ADR-0036-single-location-adr-placement.md` (this file).

That list is **incomplete**. The ADR did not enumerate `design-composer.md`, `finalize-deliverable-packager.md`, `shared-document-reviewer.md`, or `recipe-feature-pipeline/SKILL.md` as files requiring amendment — even though all four contain ADR-placement logic. The Architecture Impact section was authored against the spec text alone; the operational agents that **enforce** the spec were not enumerated in blast-radius.

This is the diagnostic for the underlying class of bug: an ADR's "Architecture Impact / Files amended" section is treated as ground truth for what needs to change. If that list is incomplete, downstream operators silently keep enforcing the old rule. There is no cross-reference check (e.g., "find every file mentioning the old convention and confirm each has been updated or explicitly grandfathered"). Per the precedent of [ADR-0031](../adrs/ADR-0031-auditing-shared-skill-module.md) (canonical-helper-home) and [ADR-0032](../adrs/ADR-0032-conventions-canonicalization.md) (conventions canonicalization), the discipline exists to centralize one rule in one place; it was not exercised when amending the ADR placement rule.

---

## 5. Open questions for the user / when to assess promotion

You asked specifically: "When should ADRs be promoted to root to prevent staleness once the pipeline completes?" The current pipeline does not answer this because ADR-0036 deliberately removed promotion as a concept (single-location-from-authoring). But the **operational state** of the pipeline still implies promotion is needed. Two coherent end-states exist; the pipeline currently inhabits neither:

| End-state | What it would require | Pros | Cons |
|---|---|---|---|
| **A. ADR-0036 honored — single-location from authoring** | Orchestrator + design-composer write directly to root `adrs/`; packager + reviewer check root only; no feature-scoped `adrs/` directory ever exists | Zero drift risk; matches ADR-0036 as written; simplest validator | All in-flight feature runs (including this one) need their feature-scoped ADRs **moved**, not copied, to root; existing pre-ADR-0036 feature copies become inert historical artifacts (already specified by ADR-0036 §Consequences) |
| **B. Restore dual-location with mandatory promotion step** | Add a real `promote_adrs` step to `finalize-deliverable-packager`; restore the cp-style pattern; validator diffs the two copies; ADR-0036 is itself superseded | Feature archives become self-contained again | Reintroduces the drift-risk class that ADR-0036 was authored to eliminate; the Gate-6 BLOCKER that motivated ADR-0036 recurs as a real risk |

When to assess the promotion question (or its absence) is therefore a question of which end-state the project wants. Per ADR-0036's selection criteria (cost-benefit analysis at scale; ADR semantics as cross-feature artifacts), **A is the chosen end-state**. The bug is that the pipeline never finished moving to it.

For the current run specifically, three orphan-state risks exist if no end-state is selected before Gate-6:

1. **Gate-6 will fail.** [finalize-deliverable-packager.md:61](../.claude/agents/finalize-deliverable-packager.md#L61) and [shared-document-reviewer.md:349](../.claude/agents/shared-document-reviewer.md#L349) both BLOCKER on missing root copies of ADR-0037..0041.

2. **ADR-0038 (codebase-analysis schema v1.1.0 supersedes ADR-0018)** is invisible to root-readers. Any future feature that consumes `codebase-analysis.json` and reads the schema ADR at root sees v1.0.0 as live, contradicting the in-flight feature's claim. This is the staleness-via-silence case.

3. **The misreading at [blueprint-v2.md:1226](../working/feature/devcontainer-mcp-provisioning-r1/blueprint-v2.md#L1226)** will be inherited into the Plan, Acceptance Tests, and Phase Validators downstream — each of which will reference "ADRs promoted at packaging" as if it were a real step. Future readers of those artifacts will look for a promotion log that does not exist.

---

## 6. Recommended assessment framing (no fixes proposed)

The user asked for a root-cause report, not a fix. What follows is a **classification of the issue** to inform whichever remediation path you select, not a prescription:

- **Issue class:** Partial-amendment defect. ADR-0036 was ratified but its Architecture Impact section did not enumerate the four operational files (orchestrator, design-composer, packager, reviewer) that implement the old convention. The amendment thus changed the rule book but left the enforcers in their prior state.
- **Severity:** BLOCKER for any feature run reaching Gate-6 under the current rule set. Current feature (`devcontainer-mcp-provisioning-r1`) is the second feature to reach this state (the first, `execution-pipeline-design-r1`, surfaced it as the original Gate-6 BLOCKER that motivated ADR-0036 itself — the ADR closed the spec gap but not the operator gap).
- **Detection cost:** Zero — pinpoint check is `grep -L 'ADR-0036' .claude/skills/recipe-feature-pipeline/SKILL.md .claude/agents/design-composer.md .claude/agents/finalize-deliverable-packager.md` plus a `diff -r adrs/ working/feature/*/adrs/` to enumerate drift.
- **Containment scope:** Five files (the four operator files above + the in-Blueprint misreading in blueprint-v2). Plus N feature directories with feature-scoped `adrs/` that need a disposition (move-to-root + remove-feature-dir per ADR-0036 §Consequences "pre-amendment archives are not retroactively cleaned" — but the current feature is **post**-amendment, so it does need cleanup).
- **Reversibility:** High. Moving ADRs is a file operation; the contents are unchanged. The orchestrator/composer/packager/reviewer can be re-aligned with surgical edits; no schema break.
- **Adjacent gap surfaced (not the user's question, but flagged):** The `adrs-migrated/` directory holds 18+ ADRs (0001–0018) that root readers don't see at canonical paths. Single-location-from-authoring (end-state A) implies these should also live at root `adrs/`; that did not happen during the prior migration. This is a separate ADR placement question worth resolving in the same pass.

---

## 7. Source citations (file:line)

Primary evidence:

- [adrs/ADR-0036-single-location-adr-placement.md](../adrs/ADR-0036-single-location-adr-placement.md) — the amendment ratified 2026-05-22
- [.claude/skills/KB-documentation-criteria/references/deliverable-archive-spec.md:136-164](../.claude/skills/KB-documentation-criteria/references/deliverable-archive-spec.md#L136-L164) — the **only** correctly-updated file
- [.claude/skills/recipe-feature-pipeline/SKILL.md:17-28](../.claude/skills/recipe-feature-pipeline/SKILL.md#L17-L28) and [:228](../.claude/skills/recipe-feature-pipeline/SKILL.md#L228) — orchestrator outputs table + dispatch parameters; not updated
- [.claude/agents/design-composer.md:48](../.claude/agents/design-composer.md#L48), [:129](../.claude/agents/design-composer.md#L129), [:187](../.claude/agents/design-composer.md#L187) — `output_adrs_dir` parameter; not updated
- [.claude/agents/finalize-deliverable-packager.md:56-63](../.claude/agents/finalize-deliverable-packager.md#L56-L63) — retired dual-location BLOCKER check still active
- [.claude/agents/shared-document-reviewer.md:349](../.claude/agents/shared-document-reviewer.md#L349) vs [:470-472](../.claude/agents/shared-document-reviewer.md#L470-L472) — internal contradiction
- [working/feature/devcontainer-mcp-provisioning-r1/blueprint-v2.md:1226](../working/feature/devcontainer-mcp-provisioning-r1/blueprint-v2.md#L1226) — Blueprint's misreading ("promoted ... per ADR-0036") + [:379](../working/feature/devcontainer-mcp-provisioning-r1/blueprint-v2.md#L379) ("ADR-0007 currently in adrs-migrated/")
- `diff -q adrs/ADR-0024-*.md working/feature/frontend-design-knowledge-r1/adrs/ADR-0024-*.md` — drift already realized (files differ)

Promotion machinery search (returned empty):

- `grep -rln -iE "adr.*promot|promote.*adr|copy.*adr|cp.*adrs" .claude/` — no script, no hook, no agent step. Only the superseded Pattern text in `deliverable-archive-spec.md`.
- [.claude/skills/auditing-shared/scripts/](../.claude/skills/auditing-shared/scripts/) — 8 scripts; none operate on ADR files.
- [handoff/](../handoff/) — contains versioned project handoff notes; no ADR copies, no promotion log.

---

## 8. What this report does NOT do

This is a report-only analysis per your instruction. It does not:

- Move any ADR file.
- Edit `recipe-feature-pipeline/SKILL.md`, `design-composer.md`, `finalize-deliverable-packager.md`, or `shared-document-reviewer.md`.
- Author a follow-up ADR to supersede ADR-0036 or amend it.
- Modify the current feature's Blueprint to remove the misreading at line 1226.
- Decide between end-state A (ADR-0036 honored) and end-state B (restore dual-location with promotion).

Those are downstream decisions for the user. The report establishes only the root cause and the staleness mechanisms that follow from it.

---

## 9. Gate-6 disposition update (added 2026-05-23, `devcontainer-mcp-provisioning-r1` run)

**Status this report's gap was confirmed:** the `devcontainer-mcp-provisioning-r1` run's `finalize-deliverable-packager` surfaced **PKG-BLOCKER-001** at Gate 6 — the 7 ADRs authored this run (ADR-0037..ADR-0043) exist only at the feature-scoped `working/feature/<slug>/adrs/` location, not at canonical `adrs/`. `tasks.json` references canonical paths that do not resolve.

This is the exact failure mode this analysis predicted in §1.

**User disposition at Gate 6** (verbatim recorded via AskUserQuestion): chose "**Defer to a pipeline-fix follow-up feature**" — accept the BLOCKER as a known issue this run; address the pipeline-wide promotion mechanism in its own feature; Gate 6 ships with documented BLOCKER waiver.

**Implications for this run:**
- `devcontainer-mcp-provisioning-r1` ships at Gate 6 with one documented, user-accepted BLOCKER (PKG-BLOCKER-001).
- The 7 ADRs remain accessible from the feature working directory for any human reader; downstream automated consumers (including the execution-pipeline that consumes `tasks.json`) will find the canonical `adrs/` paths unresolvable.
- The execution-pipeline must either (a) be patched to also look in the feature-scoped fallback location, or (b) wait for the pipeline-fix feature to land before consuming this `tasks.json`.

**Recommended follow-up feature** (slug suggestion): **`adr-placement-mechanism-repair-r1`**. Scope per §6/§7 of this analysis — end-state A (honor ADR-0036 with a real promotion machinery) is the preferred direction unless the user revisits the decision. Suggested fix targets enumerated in §1: `recipe-feature-pipeline/SKILL.md`, `design-composer.md`, `finalize-deliverable-packager.md`, `shared-document-reviewer.md`, plus a new promotion step at deliverable packaging time that copies ADRs from `working/feature/<slug>/adrs/` to canonical `adrs/` and verifies cross-reference integrity.

**The 26 ADRs at canonical `adrs/` (0011–0036) plus the 12 feature-scoped ADRs (in 5 features' working dirs) form the steady-state inventory this follow-up feature must reconcile.**

---

## 10. Update from `execute-orchestrator-dispatch-mechanism-repair-r1` run (2026-05-24)

The pipeline run for `execute-orchestrator-dispatch-mechanism-repair-r1` exercised the inverse placement disposition: the user ratified ADR-0036-canonical (root `adrs/` only, no feature-scoped copy) at the feature's Gate-7 ADR-placement question, and design-composer wrote ADR-0044 and ADR-0045 to `/workspaces/feature-pipeline/adrs/` directly.

**What this run revealed that this analysis (authored 2026-05-23) did not fully capture:**

1. **The deliverable-archive-spec is in fact fully amended per ADR-0036.** `KB-documentation-criteria/references/deliverable-archive-spec.md` §"ADR placement convention" (lines 136–150) + §"Patterns and anti-patterns" Pattern (line 162) are unambiguous: "ADRs live in exactly one canonical location" + "Do NOT create feature-scoped duplicate copies." Pre-ADR-0036 archives with feature-scoped `adrs/` directories are explicitly grandfathered ("validator ignores those directories; presence or absence is not a finding"). The analysis's §2.3 framing that "Both compliance paths fail" was therefore overstated — the canonical-only path is fully spec-conformant.

2. **The packager AGENT showed runtime discretion to defer to the spec.** When `finalize-deliverable-packager` ran for this feature, it read the current spec, recognized the amendment, and PASSED the canonical-only placement (verdict: PASS; 25/25 artifacts present; 0 BLOCKER). The packager's status report explicitly noted: "the current spec ... is fully amended per ADR-0036 ... No dual-location requirement remains."

3. **The agent FILE TEXTS still carry the unamended check.** `.claude/agents/finalize-deliverable-packager.md` lines 56–63 + `.claude/agents/shared-document-reviewer.md` line 349 still contain the retired dual-location BLOCKER check (as this analysis correctly observed). The reviewer file even contradicts itself (line 349 vs. line 472 — both retired-check AND amended-check coexist). So the partial-amendment framing remains technically correct for the file texts, but the practical effect (Gate-6 BLOCKER firing on every run) is mitigated by the packager agent's runtime discretion to defer to the spec — which is fragile (it depends on the packager actually reading the spec each run).

4. **The orchestrator + design-composer default behavior is still un-amended.** When `output_adrs_dir` is not explicitly overridden by the parent orchestrator, the convention default still computes to `working/feature/<slug>/adrs/` (feature-scoped). This run worked only because the parent orchestrator explicitly passed `output_adrs_dir=/workspaces/feature-pipeline/adrs/` after the user's Gate-7 ratification. Without the explicit override, the next feature run would write to feature-scoped again — and then trigger the original devcontainer-mcp-provisioning-r1 BLOCKER (canonical-required-but-absent).

### Re-scope of the proposed follow-on feature

Based on the above, the follow-on feature **`adr-placement-mechanism-repair-r1`** is SMALLER than this analysis (and the devcontainer-mcp-provisioning-r1 Gate-6 disposition) originally framed:

| Original §6 framing | Revised scope (post-2026-05-24) |
|---|---|
| 4 operator files need amendment | 2 operator file TEXTS need amendment: `finalize-deliverable-packager.md:56–63` + `shared-document-reviewer.md:349` (delete the retired dual-location BLOCKER text). Spec already amended. |
| Need to author a promotion mechanism | NOT needed. Canonical-only is the chosen end-state per ADR-0036; no promotion mechanism exists or should exist. |
| Need to migrate existing feature-scoped ADRs to canonical | OPTIONAL hygiene; not blocking. The spec grandfathers pre-amendment archives. |
| Need orchestrator + design-composer default change | Yes — change the default for `output_adrs_dir` from feature-scoped to canonical-root. Surgical (1-2 lines in `recipe-feature-pipeline/SKILL.md` + matching default in `design-composer.md`). |

**Revised scope_class for the follow-on:** MINOR (was previously framed as FULL). Estimated 4–6 hours of work, not the 2–3 days originally implied by the FULL framing.

### Updated outstanding gap

The single sentence summary of the remaining gap as of 2026-05-24:

> The deliverable-archive spec is amended per ADR-0036; the packager agent has runtime discretion to defer to the spec; but the packager + reviewer agent FILE TEXTS still contain retired dual-location check prose that should be deleted, and orchestrator + design-composer defaults for `output_adrs_dir` should change from feature-scoped to canonical-root so future runs don't depend on explicit operator override.

This is materially smaller than the original §6 framing. The `execute-orchestrator-dispatch-mechanism-repair-r1` run is the empirical demonstration: a feature can ship cleanly through Gate 6 with canonical-only ADRs today, provided the operator explicitly opts into ADR-0036 disposition at Gate 7.


