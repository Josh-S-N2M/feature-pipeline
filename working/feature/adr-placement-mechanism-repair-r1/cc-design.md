---
id: CC-DESIGN-adr-placement-mechanism-repair-r1
doc_type: per-layer-design
layer: claude-code
version: 1.0.0
status: draft
gate_passed: null
generated: 2026-05-24T18:50:00Z
generated_by: design-cc
feature_slug: adr-placement-mechanism-repair-r1
prd_version: 1.0.2
research_plan_version: 1.0.0
synthesis_version: 1.0.0
codebase_analysis_schema: v1.1.0
derived_from:
  - working/feature/adr-placement-mechanism-repair-r1/prd-v1.md
  - working/feature/adr-placement-mechanism-repair-r1/research-plan.md
  - working/feature/adr-placement-mechanism-repair-r1/synthesis.md
  - working/feature/adr-placement-mechanism-repair-r1/codebase-analysis.json
  - working/feature/adr-placement-mechanism-repair-r1/codebase-analysis-report.md
scope_class: FULL
layer_scope: ["claude-code"]
filename_workaround_note: "Output filename is cc-design.md per ADR-0019 Path-A reserved-word workaround; this design subsection is the Claude Code / Project Filesystem layer's contribution to the integrated Blueprint."
---

# Claude Code / Project Filesystem Design — ADR Placement Mechanism Repair

This per-layer design subsection produces the inputs the Design Composer will integrate into Blueprint §"Claude Code / Project Filesystem Design". The feature has a **single layer in scope** (CC); no other per-layer designers run; downstream Composition will lift this subsection essentially verbatim and add cross-cutting prose (Fact Disposition Table, ADRs, cross-layer Open Items — none of which the CC designer authors).

## 1. Layer responsibility scope

The Claude Code layer owns every artifact this feature touches. The substantive scope decomposes into seven primitive families:

| Family | What this feature changes |
|---|---|
| **Sub-agent files** (`.claude/agents/`) | 3 files edited (`finalize-deliverable-packager.md`, `shared-document-reviewer.md`, `design-composer.md`) — prose + tool-list edits, no new agents introduced |
| **Skill bodies** (`.claude/skills/<name>/SKILL.md`) | 1 SKILL.md edited (`recipe-feature-pipeline/SKILL.md`, line 273 area, parameter resolution) + 4 audit-targeted skills (`KB-documentation-criteria`, `KB-issue-capture`, `capture-issue`, `synthesize`) — prose + template-example edits |
| **Skill scripts** (`.claude/skills/auditing-shared/scripts/`) | 1 new script (`validate_adr_placement.py`) + 1 dispatch-list edit (`run_phase_checks.py`) + 1 smoke-test extension (`smoke_test_auditing_shared.py`) |
| **Hooks** (Claude Code lifecycle hooks) | None. The "execution-pipeline hook" surface in FR-10 is the existing `run_phase_checks.py` parallel-dispatch coordinator — an internal subprocess hook, NOT a Claude Code `settings.json` lifecycle hook |
| **CLAUDE.md / rules** | None. Per KB-cc-design Principle 5 (one-source-of-truth) and Principle 1 (lowest-cost primitive), the canonical-only ADR convention already lives in (a) ADR-0036 itself, (b) `KB-documentation-criteria/references/deliverable-archive-spec.md` post-amendment, (c) `KB-documentation-criteria/references/shared-conventions.md:302`. Adding a CLAUDE.md directive or unconditional rule would duplicate three existing sources and incur token cost on every request. The validator (FR-10) is the enforcement mechanism; no advisory CLAUDE.md/rule is needed. |
| **MCP servers** | None. The validator is pure Python stdlib. No external service. |
| **Plugins** | None. Per KB-cc-design Principle 7 (plugins-for-distribution-not-organization), the scope is repo-internal; nothing is being distributed cross-project. |

This is **a CC-internal repair feature**: no new primitives, only edits to existing ones plus one new script added to an existing canonical-helper home (`auditing-shared/scripts/`).

## 2. Inventory of CC primitives being modified or introduced

### 2.1 Sub-agents (modified — 3 files)

| Sub-agent | Path | Change kind | Reasoning model | Effort | Tools touched |
|---|---|---|---|---|---|
| `finalize-deliverable-packager` | `.claude/agents/finalize-deliverable-packager.md` | Modify (prose deletion + replacement; tool-list expansion) | unchanged (opus) | unchanged (medium) | **Tool-list change required** (see §5) |
| `shared-document-reviewer` | `.claude/agents/shared-document-reviewer.md` | Modify (prose deletion only) | unchanged | unchanged | none |
| `design-composer` | `.claude/agents/design-composer.md` | Modify (parameter-description rewrite at 3 sites) | unchanged (opus) | unchanged (xhigh) | none |

**Reasoning configuration: intentional, not default** (per KB-cc-design Principle 9). For each modified sub-agent, the existing `model:` and `effort:` choices remain correct after the edits — no reasoning-load shift is induced by this feature, so no model/effort change is recommended:
- `finalize-deliverable-packager` (opus / medium): packaging-stage gating is cross-cutting reconciliation but moderate-depth; opus/medium is correct.
- `shared-document-reviewer` (per its existing frontmatter; not changed by this feature): same.
- `design-composer` (opus / xhigh): cross-cutting Blueprint integration + ADR authoring is the canonical opus/xhigh case.

The `skills:` arrays for all three sub-agents are unchanged. (No new skill needs to be preloaded; the validator is invoked as a subprocess, not as a model-invocable skill.) The category-error of using `skills:` to express reasoning depth (SA-13) does not apply.

### 2.2 Skills (modified — 5 SKILL.md files + 2 reference files in KB-documentation-criteria)

| Skill | File | Change kind | Disposition basis |
|---|---|---|---|
| `recipe-feature-pipeline` | `.claude/skills/recipe-feature-pipeline/SKILL.md` | Modify (FR-3: parameter-list entry at line 273 acquires explicit canonical default + ADR-0036 citation; FR-10: Step 8 acquires the orchestrator-stage validator gate) | IN-005, IN-009, IN-012 |
| `KB-documentation-criteria` (discipline) | `references/disciplines/design-composition.md:36, :295` | Modify (replace feature-scoped path examples with canonical-root) | IN-011, IN-012 |
| `KB-documentation-criteria` (spec) | `references/deliverable-archive-spec.md:150` | Modify (remove or amend stale backward-compat clause) | IN-012 |
| `KB-documentation-criteria` (template) | `references/templates/issue-register-template.md:96, :99` | Modify (path-only refresh of example paths to canonical form) | IN-012 |
| `KB-issue-capture` | `.claude/skills/KB-issue-capture/SKILL.md:72` | Modify (path-only refresh of worked-example header) | IN-012 |
| `capture-issue` | `.claude/skills/capture-issue/SKILL.md:44` | Modify (path-only refresh) | IN-012 |
| `synthesize` | `.claude/skills/synthesize/SKILL.md:22, :240` | **Review-with-explicit-disposition** (NOT a straight edit) | IN-012 — see Q-CC-4 below |

**Reasoning vs. always-loaded cost**: All 7 of these are reference files (`references/`) or SKILL.md prose; none are model-invocable behavior changes. Per KB-cc-design Principle 1, this is the lowest-cost primitive — prose edits to existing skill content, no new skill scaffold, no new always-loaded rule.

### 2.3 New script (introduced — 1 file)

| Script | Path | Purpose | Dependencies |
|---|---|---|---|
| `validate_adr_placement.py` | `.claude/skills/auditing-shared/scripts/validate_adr_placement.py` | Scans repo for `ADR-*.md` files outside canonical `adrs/`; emits JSON findings; exit 0 = clean / exit 2 = block (per IN-010 canonical convention) | Python 3 stdlib only (`argparse`, `pathlib`, `json`, `sys`) — satisfies NFR-8 |

**Why this primitive (KB-cc-design Principle 1)**: a Python script in `auditing-shared/scripts/` is the canonical-helper-home pattern (ADR-0031 / ADR-0035 / ADR-0042). The alternatives considered and rejected:

- **Shell script** — lower dependency footprint, but Python stdlib is already in `auditing-shared/`'s allowed dependency set (NFR-8), and the JSON output contract is markedly easier in Python. Rejected.
- **Embedded Python module imported by family-coordinators** — would force every consuming surface (orchestrator, packager, execution-pipeline) to `import` rather than subprocess-dispatch, which is non-uniform with the existing pattern (every other audit helper is subprocess-dispatched via `run_phase_checks.py`). Rejected per IN-010 convention conformance.
- **Claude Code `settings.json` lifecycle hook (e.g., `PostToolUse`)** — would only fire when the model uses an edit tool, missing the case where ADRs land via `design-composer`'s Write tool but the orchestrator subsequently authors elsewhere; would also pollute every CC session in the repo with a hook that has no purpose outside this feature's enforcement context. Rejected (and noted as a deliberate design distinction: the "execution-pipeline hook" naming in PRD §FR-10-c is **NOT** a Claude Code lifecycle hook — it is the internal `run_phase_checks.py` subprocess hook, an orchestration-time check, not a tool-event hook).

### 2.4 Existing script (modified — 2 files)

| Script | Path | Change kind |
|---|---|---|
| `run_phase_checks.py` | `.claude/skills/auditing-shared/scripts/run_phase_checks.py` | Modify (add `validate_adr_placement.py` to the parallel-dispatch set at line ~39–44; one-line addition + the dimension rollup may need a new dimension or fold ADR-placement into the existing `validator` dimension) |
| `smoke_test_auditing_shared.py` | `.claude/skills/auditing-shared/scripts/smoke_test_auditing_shared.py` | Modify (add positive-path + negative-path smoke for `validate_adr_placement.py`) |

### 2.5 CLAUDE.md, rules, MCP servers, plugins, output styles

**None modified or introduced** for any of these. See §1 for the rationale (Principle 5 + Principle 1 + Principle 7).

## 3. Per-FR design table

Every FR carried in the PRD (FR-1 through FR-11; FR-7 superseded) is addressed below. The table commits the approach, names the affected files with stable line ranges where they are pinned by Discovery (IN-006 / IN-007), names the risk, and names the FR cross-dependency.

### FR-1 — Delete retired dual-location BLOCKER prose in packager

| Aspect | Decision |
|---|---|
| Approach | Replace the 8-line "### 3. ADR cross-location check" section at `finalize-deliverable-packager.md:56–63` with a new "### 3. ADR placement validator" section that subprocess-invokes `validate_adr_placement.py` and emits any returned findings as BLOCKERs in the same shape the prior dual-location BLOCKER used. The replacement preserves the section's procedural position (between §"2. Cross-reference with spec" and §"4. Invoke shared-document-reviewer") so downstream consumers of packager-report.json see no schema change beyond the finding-string text. |
| Files affected | `.claude/agents/finalize-deliverable-packager.md:56–63` (deletion + replacement); secondary: `.claude/agents/finalize-deliverable-packager.md` frontmatter `tools:` field (see §5 / Q-CC-5) |
| Risk | Low — IN-006 pinned the line range exactly; replacement is in-place. Risk is gated by Q-CC-5 (tools-list expansion). |
| Dependencies on other FRs | FR-10 (the validator must exist before the call-site references it); execution order ⇒ Phase 4 (validator) precedes the Phase-1 prose-replacement that calls it, OR the Phase-1 edit references the script-to-be-built and Phase 4 completes the wiring. Plan author chooses. |

### FR-2 — Delete contradictory dual-location BLOCKER prose in reviewer

| Aspect | Decision |
|---|---|
| Approach | Delete the contradictory single-line check at `shared-document-reviewer.md:349`. The post-ADR-0036 statement at `:470–472` becomes the sole canonical-only ADR-placement convention the reviewer carries. **Prose-only deletion; no replacement needed** because the reviewer does not own enforcement — that is the validator's job at FR-10. |
| Files affected | `.claude/agents/shared-document-reviewer.md:349` (deletion) |
| Risk | Low — IN-006 confirmed file-internal contradiction; deletion resolves it without introducing new behavior. Blast radius (per codebase-analysis.json `blast_radius[1]`) is medium because 28 sub-agents pass through the reviewer, but every one of those reviewer invocations has been suffering false BLOCKERs from line 349 since ADR-0036 accepted; deletion is a strict improvement. |
| Dependencies on other FRs | None. Independent edit. |

### FR-3 — Orchestrator `output_adrs_dir` default resolves to canonical root

| Aspect | Decision |
|---|---|
| Approach | At `recipe-feature-pipeline/SKILL.md:273`, modify the design-composer parameter-list entry from a bare `output_adrs_dir` token to an explicit-default form: `output_adrs_dir` — `default: "adrs/" per ADR-0036; canonical-root unless the caller explicitly overrides for testing.` The orchestrator's responsibility is **pass-through fidelity** (AC-FR-3-b): when the caller supplies a value, that value is passed unmodified; when the caller does not, the orchestrator passes `"adrs/"`. The orchestrator does NOT validate the value — that is design-composer's job + the validator's job. |
| Files affected | `.claude/skills/recipe-feature-pipeline/SKILL.md:273` (in-place edit on the parameter-list line) |
| Risk | Low — IN-005 confirmed no current explicit default; this codifies the intended behavior. Blast-radius (per `blast_radius[2]`) is high in transitive reach but low in risk because today design-composer interprets per-implementation. |
| Dependencies on other FRs | FR-4 (design-composer's parameter description must match the orchestrator's new default form); FR-5 (the parameter must remain in place, not be eliminated). |

### FR-4 — Design-composer parameter description carries canonical default + ADR-0036 reference

| Aspect | Decision |
|---|---|
| Approach | Three in-place edits in `design-composer.md` at the IN-007-pinned lines: |
| | - **Line 48** (Inputs section): change `output_adrs_dir — directory where any new ADRs you author land.` to `output_adrs_dir — directory where any new ADRs you author land. Default: "adrs/" (canonical-root) per ADR-0036. Override only for test fixtures (see §"Test override" below).` |
| | - **Line 129** (Phase 4 procedure): unchanged in form — the directive `Write to output_adrs_dir/ADR-<NNNN>.md` continues to apply; the resolution semantics now flow from the new line-48 default. |
| | - **Line 187** (Output section): unchanged in form — the output contract `output_adrs_dir/ADR-<NNNN>.md — one file per new ADR` continues to apply. |
| | Add a new short subsection (3–6 lines) titled **"Test override for `output_adrs_dir`"** documenting the override surface: callers wanting a non-canonical write path (test fixtures, negative-path harnesses) pass `output_adrs_dir` explicitly; the orchestrator passes it through unmodified; design-composer writes to the supplied path; the FR-10 validator (which runs at three independent surfaces) will flag any non-canonical placement, so the override is only safe for fixtures that are NOT subsequently validator-scanned. |
| Files affected | `.claude/agents/design-composer.md:48` (text expansion); `.claude/agents/design-composer.md:129, :187` (no edit); new subsection (insertion at end of "Inputs" or as a new "## Test override" — Design Composer to position) |
| Risk | Low — IN-007 confirmed line ranges exactly; prose-only edits. |
| Dependencies on other FRs | FR-3 (orchestrator and composer descriptions must agree); FR-5 (parameter not eliminated); FR-10 (the test-override prose references the validator-at-3-surfaces enforcement, so the validator must exist for the prose to be accurate). |

### FR-5 — `output_adrs_dir` remains a parameter with documented test-only override

| Aspect | Decision |
|---|---|
| Approach | No code change beyond FR-3 + FR-4. This FR codifies a non-deletion: the parameter is **NOT** eliminated. The Design captures the elimination-rejection rationale: eliminating `output_adrs_dir` would break the ability to negative-path-test the FR-10 validator (the negative-path test fixture in §5 of Plan Phase 6 needs to write an ADR to a non-canonical location to confirm all three enforcement surfaces block). |
| Files affected | None directly; this FR is satisfied by FR-3 + FR-4 (which retain the parameter). |
| Risk | None — non-deletion is the trivial path. |
| Dependencies on other FRs | FR-3, FR-4. |

### FR-6 — Blueprint documents migration disposition

| Aspect | Decision |
|---|---|
| Approach | This FR is owned by the Design Composer (it requires authoring the Blueprint's migration-disposition section). The CC designer's contribution is the **migration-map structure** that the Composer lifts: the 6-category taxonomy (duplicate-identical / duplicate-divergent / numbering-collision / feature-scoped-only / legacy-archive-final-collision / legacy-archive-non-final) and the per-category disposition. Discovery's `codebase-analysis.json` `migration_map` section is the authoritative input; the Blueprint reproduces it in human-readable table form. No CC primitive change. |
| Files affected | None at CC layer; the Blueprint at `working/feature/<slug>/blueprint-v<N>.md` is the deliverable target (Composer authors). |
| Risk | None at CC layer. |
| Dependencies on other FRs | All of FR-8a/b/c/d (the migration the Blueprint documents). |

### FR-7 — SUPERSEDED

Slot retained for traceability. No CC primitive change.

### FR-8 — Migration of duplicated, divergent, feature-scoped, and legacy-archive ADRs

The CC-design contribution is the **migration-mechanism design** — what tools, what command shapes, what verification steps. The Plan owns the per-task decomposition; the CC design names the mechanics.

#### FR-8a — Dedupe (12 byte-identical duplicates)

| Aspect | Decision |
|---|---|
| Approach | Per-ADR: re-run `diff -q adrs/ADR-NNNN-*.md working/feature/<slug>/adrs/ADR-NNNN-*.md` (re-verify byte-equality at edit time per Assumption A2); if empty diff, `git rm working/feature/<slug>/adrs/ADR-NNNN-*.md`; commit per-ADR (one ADR per Plan task per NFR-1). The canonical file's history is the authoritative history; no `git mv` needed for dedupe (the canonical file stays; the duplicate is deleted). |
| Files affected | 12 files deleted from 4 feature folders (per `migration_map.category_FR_8a`). |
| Risk | Low — per-task byte-equality re-check catches the (very unlikely) case where one of the duplicates was modified between Discovery and execution. |
| Dependencies | None blocking; runs after Phase 1 operator edits to avoid co-mingling with prose changes. |

#### FR-8b — Reconciliation (3 cases — but ONLY 1 is actually divergent body)

| Aspect | Decision |
|---|---|
| Approach | **Discovery IN-002 reframed this FR entirely.** ADR-0024 is a status-lift (only frontmatter `status:` differs; Accepted canonical wins; delete feature-scoped copy; **no rejected-body archival needed because no body content is lost** — this is functionally a dedupe with a status-precedence rule, not a divergent-body reconciliation). ADR-0044 and ADR-0045 are **numbering collisions**, NOT divergent bodies — see FR-8b-renumber below. |
| Sub-action ADR-0024 | `diff` confirms only line-3 frontmatter diff; delete `working/feature/frontend-design-knowledge-r1/adrs/ADR-0024-*.md`; canonical remains; commit. The Blueprint's "divergent-body archival" prose collapses to "the rejected version was a status-lift, not a body diff; no archival." |
| Sub-action ADR-0044 / ADR-0045 (**numbering-collision sub-FR, here called FR-8b-renumber**) | Two distinct decisions accidentally share each ID. Resolution per D1 / Q-CC-1: re-number the feature-scoped variants to the next-available IDs **after Phase 2d completes** (because Phase 2d consolidates 18 archive IDs into canonical and may shift the next-available number). Default lean: feature ADR-0044-per-issue-folder-model → canonical ADR-0051; feature ADR-0045-three-doctypes-preserved → canonical ADR-0052. Each renumbered ADR carries a frontmatter `original_id: ADR-0044` provenance field. The renumber + relocate uses `git mv` (NFR-5). All references update via FR-9 sweep. |
| Files affected | ADR-0024: 1 file deleted. ADR-0044 / 0045: 2 files renamed via `git mv` + frontmatter edit + reference sweep. |
| Risk | Medium for renumber: the FR-9 sweep must catch every reference to the **feature-scoped** ADR-0044 / 0045 IDs and update them to the new canonical IDs. Discovery's IN-008 inventory (223 + 145 references; most prose) is the input. The path-form subset (14 hits) is mechanical; the prose-form subset is path-only, NOT semantic (per FR-9b). |
| Dependencies | FR-8d MUST complete before FR-8b-renumber (next-available number is computed post-Phase-2d). |

#### FR-8c — Relocation (5 truly feature-scoped ADRs: ADR-0046 through ADR-0050)

| Aspect | Decision |
|---|---|
| Approach | Per ADR: `git mv working/feature/issue-capture-mechanism-r1/adrs/ADR-NNNN-*.md adrs/ADR-NNNN-*.md` (preserves history per NFR-5). Leave a redirect note at the originating folder per OI-5 / Q-CC-2 default (`.tombstone` extension per D6 Option C — see Q-CC-2). |
| Files affected | 5 ADRs moved; 5 redirect notes created. |
| Risk | Low — `git mv` is reversible; canonical destination is empty for these IDs (verified — canonical's highest ID is currently 0045 per IN-002). |
| Dependencies | None blocking; runs in Phase 2c. |

#### FR-8d — Consolidate `adrs-migrated/` legacy archive (47 files)

| Aspect | Decision (per gate-binding D2: archive wins for 8 collisions) |
|---|---|
| Approach | The 47-file archive contains 18 distinct ADR IDs (0001–0018). Sub-actions: |
| | (i) **For IDs 0001–0010 (no canonical collision)**: `git mv adrs-migrated/ADR-NNNN-final*.md adrs/ADR-NNNN-<slug>.md` (history-preserving rename to canonical); `git rm` for the matching `-pre-naming-convention` and `-pre-template-migration` variants (Git history preserves them per NFR-5). |
| | (ii) **For IDs 0011–0017 (8 collisions; archive v2.0.0 wins over canonical v1.0.0)**: Archive the stale canonical body to `adrs/superseded/ADR-NNNN-pre-consolidation-canonical.md` with provenance footer; then `git mv adrs-migrated/ADR-NNNN-final*.md adrs/ADR-NNNN-<slug>.md` (replacing the stale canonical). New canonical's frontmatter gains `superseded_by_consolidation: true` + `superseded_canonical_archived_to: adrs/superseded/ADR-NNNN-pre-consolidation-canonical.md`. Delete `-pre-naming-convention` and `-pre-template-migration` variants. |
| | (iii) **For ID 0018 (collision, canonical newer due to ADR-0038 supersession marker)**: canonical wins; archive's final variant is deleted; archive's `-pre-*` variants deleted. |
| | (iv) **For ID 0007 (no archive final variant; canonical exists)**: archive's `-pre-naming`, `-v1-pre-template`, `-v1-superseded`, `-v2-pre-template` variants all deleted; canonical untouched. |
| | After all sub-actions complete: `adrs-migrated/` directory is empty; `git rm -r adrs-migrated/`. |
| Files affected | 17 final-variants `git mv`ed to canonical; 29 pre-* variants deleted; 8 stale canonical bodies archived to `adrs/superseded/`; 1 directory removed. |
| Risk | Highest sub-phase risk (per `blast_radius[8]`): the 8 archive-wins collisions require frontmatter rewrites + supersession archival. Each is one atomic Plan task (NFR-1). |
| Dependencies | Must precede FR-8b-renumber (next-available ID for renumber depends on the post-FR-8d canonical state). Must precede FR-9 (cross-reference sweep includes the new `adrs/superseded/` paths). |

### FR-9 — Cross-reference sweep

| Aspect | Decision |
|---|---|
| Approach | Use the **D5 Option B extended pattern set** (per Discovery IN-008 / Synthesis D5): the IN-008 grep-pattern floor from the Research Plan **plus** the three additional edge cases Discovery validated (Mermaid Person()/Node() ADR references — verified absent; frontmatter `supersedes:` / `superseded_by:` / `related:` / `subsumes:` / `pairs_synthesis_decisions:` arrays — all bare-ID, not path-form, so not in path-only sweep scope; prose `see ADR-NNNN` / `per ADR-NNNN` — not path-form, not in sweep scope). The actionable path-form subset is **14 references** to feature-scoped paths + **18 references** to `adrs-migrated/` paths = 32 total mechanical edits. Per FR-9b: path-only; no semantic prose changes. |
| Files affected | 14 + 18 = 32 reference sites across `Issues/**/*.md`, `working/feature/*/*.md`, `.claude/skills/**/*.md`, `adrs/ADR-0036-*.md` (the ADR-0036 reference at line 107 is a rejected-option *illustrative* mention — per FR-9 finding, NO change needed because it's a rejected-symlink example, not a real cross-reference). |
| Risk | Medium — false-negative risk per NFR-3 is the failure mode (sweep misses a reference form). Mitigation: Phase 6 re-runs the extended pattern set; zero matches expected (excluding redirect notes per FR-8c and audit-trail files). |
| Dependencies | Must follow FR-8a/b/c/d (paths to rewrite must be known post-migration). |

### FR-10 — ADR-location validator and three-surface enforcement

The single largest CC-design item. Decomposed into validator design + per-surface integration.

#### FR-10 (a) — Validator script design

| Aspect | Decision |
|---|---|
| File | `.claude/skills/auditing-shared/scripts/validate_adr_placement.py` (per OI-3 default; per D4 Option A) |
| Input contract | Positional arg: `[scan_path]` (default `.` = repo root, honoring ADR-0027 cwd precondition). Optional flag: `--allowlist <comma-separated-paths>` (see Q-CC-3 for arg-vs-config-file resolution). |
| Algorithm | `pathlib.Path(scan_path).rglob("ADR-*.md")` → for each match, check whether its parent directory is `adrs/` (exact match relative to scan root) or `adrs/superseded/` (allowed sub-tree per FR-8b archival convention) or in the explicit allowlist. Any non-conforming match → finding. |
| Output contract | JSON to stdout. Shape: `{"validator": "validate_adr_placement", "verdict": "PASS" \| "BLOCK", "findings": [{"path": "...", "category": "feature-scoped" \| "legacy-archive" \| "unexpected-location", "remediation_hint": "..."}], "scan_path": "...", "elapsed_ms": N}`. |
| Exit codes | 0 = `verdict: PASS` (no findings). 2 = `verdict: BLOCK` (one or more findings). Per IN-010 canonical convention. Non-canonical non-zero treated as error by `run_phase_checks.py`. |
| Dependencies | Python 3 stdlib only: `argparse`, `pathlib`, `json`, `sys`, `time`. Satisfies NFR-8. |
| Latency budget | < 5s per NFR-2. `rglob` over a repo this size (~few thousand files) completes in <1s on Codespace; safely under budget. Validator emits `elapsed_ms` so latency is observable in CI/audit. |
| Allowlist policy (post-FR-8d) | Empty by default. The only legitimate non-canonical location is `adrs/superseded/` (a subdirectory of canonical), which is hard-coded into the algorithm rather than configured as allowlist (it is a structural exception, not a contingent one). See Q-CC-3 / Q-CC-6 for the temporal allowlist question during mid-migration phases. |
| Why this is the lowest-cost primitive (Principle 1) | A 60–100-line Python script using existing `auditing-shared/scripts/` conventions reuses the canonical-helper-home pattern (ADR-0031 / ADR-0035 / ADR-0042); zero new dependency footprint; zero new SKILL or new agent introduced; the three consumers reach it via the existing subprocess-dispatch pattern. |

#### FR-10 (b) — Orchestrator stage-gate surface (per IN-009-a)

| Aspect | Decision |
|---|---|
| Integration point | `recipe-feature-pipeline/SKILL.md` Step 8 (Design Composition), inserted **between** the design-composer return and the shared-document-reviewer invocation. Procedural shape: after design-composer writes ADRs, the orchestrator invokes `validate_adr_placement.py` as a subprocess; on `exit 2` the orchestrator halts the stage and surfaces the validator's JSON findings to the user as a `BLOCKER`. On `exit 0` the orchestrator proceeds to invoke `shared-document-reviewer`. |
| Why between composer-return and reviewer-invocation | The validator is a mechanical pre-reviewer check (cheaper than the reviewer; deterministic; no LLM context cost). Placing it before reviewer means the reviewer never sees a malformed placement. Placing it after reviewer would waste reviewer cycles on placements the validator would immediately reject. |
| Allowlist at this surface | Empty by default. (During this feature's own execution, the validator is not yet wired at this point — bootstrapping concern noted in §6.) |
| Failure mode | `exit 2` → orchestrator halts Step 8; surfaces findings via existing `AskUserQuestion` channel; does NOT auto-revert (revert is a Plan execution responsibility, not an orchestrator responsibility). |
| Distinct purpose vs. surfaces (b) and (c) per NFR-6 | Catches **author-time** violations before any reviewer or downstream artifact touches the ADR. |

#### FR-10 (c) — Execution-pipeline hook surface (per IN-009-b)

| Aspect | Decision |
|---|---|
| Integration point | Add `validate_adr_placement.py` to the parallel-dispatch set in `auditing-shared/scripts/run_phase_checks.py` (line ~39–44 dispatch block). `execute-phase-quality-reviewer` already invokes `run_phase_checks.py` at line 18 + 54; adding the validator to the dispatch set wires it in with **zero new hook surface introduced**. |
| Dimension rollup | `run_phase_checks.py` aggregates per-check JSON outputs into a 5-dimensional verdict (tests, audits, validator, discipline, scope_deviations). The new validator's findings fold into the `validator` dimension (extending the existing `validate_pipeline_frontmatter.py` dimension). The Composer may wish to consider whether the ADR-placement validator deserves its own dimension — see Q-CC-7. |
| Allowlist at this surface | Same as surface (b) — empty by default. The `run_phase_checks.py` invocation runs on every phase; persistent allowlist drift would be a red flag. |
| Distinct purpose vs. surfaces (a) and (c) per NFR-6 | Catches **runtime** violations during a feature's execution (e.g., an `execute-task-code-producer` task that erroneously writes a feature-scoped ADR). |

#### FR-10 (d) — Packager surface (per IN-009-c)

| Aspect | Decision |
|---|---|
| Integration point | Replace the deleted FR-1 prose at `finalize-deliverable-packager.md:56–63` with a subprocess call to `validate_adr_placement.py`. The replacement section's name: "### 3. ADR placement validator." Behavior: subprocess-invoke; on `exit 2` raise a BLOCKER finding with the validator's JSON shape lifted into `packager-report.json`'s `findings[]` array; on `exit 0` no finding. |
| Tool prerequisite | The packager's existing `tools:` frontmatter is `Read, Glob, Grep, Write, TaskCreate, TaskUpdate` — **no `Bash` or subprocess capability**. This is a blocker for direct subprocess invocation from the packager. Two resolutions, surfaced as Q-CC-5: (i) add `Bash` to the packager's `tools:` (smallest possible expansion: `Bash(python3 .claude/skills/auditing-shared/scripts/validate_adr_placement.py)` if permission-scoping allows); (ii) keep the packager tool-restricted and have the orchestrator invoke the validator on the packager's behalf, passing the result into the packager's input. Decision deferred to Q-CC-5 — Design Composer to arbitrate. |
| Allowlist at this surface | Same as (a)/(b) — empty by default. |
| Distinct purpose vs. surfaces (a) and (b) per NFR-6 | Catches **finalize-time** violations as the last line of defense before Gate 6; pairs with the existing `DeliverableArchive` reviewer dispatch. |

#### Three-surface enforcement non-redundancy proof (NFR-6)

The three surfaces catch distinct failure windows:

| Surface | Catches violations introduced by … |
|---|---|
| (a) Orchestrator Step 8 | `design-composer` (the only ADR-authoring sub-agent) at author time |
| (b) Execution-pipeline `run_phase_checks.py` | `execute-task-code-producer` or any other execution-phase write during the per-feature plan execution |
| (c) Packager Step 14 | Any artifact present in `working/feature/<slug>/` at finalize time that bypassed (a) and (b) — defense in depth |

All three invoke the same script with the same default allowlist (empty). The script's `-` separator and JSON output shape are uniform, so the three integration points are non-contradictory by construction (one source of truth).

### FR-11 — Skill audit and remediation

The skill-audit table (per Discovery IN-011 / IN-012) drives this FR. Discovery confirmed 8 file-level findings clustering into 4 skill families; 5 skill families (10 auditing-* skills, KB-review-disciplines, KB-task-decomposition, all per-layer KB-* design/platform skills, 6 synthesize-class knowledge skills) are **CLEAN** — no FR-11 finding.

| Skill family | File(s) | Disposition | Remediation |
|---|---|---|---|
| `recipe-feature-pipeline` | `SKILL.md:273` | update-with-fix | FR-3 (already covered) |
| `KB-documentation-criteria` | `references/disciplines/design-composition.md:36` | update-with-fix | Replace `working/feature/<slug>/adrs/ADR-NNNN-<slug>.md` with `adrs/ADR-NNNN-<slug>.md per ADR-0036` |
| `KB-documentation-criteria` | `references/disciplines/design-composition.md:295` | update-with-fix | Same substitution as line 36 |
| `KB-documentation-criteria` | `references/deliverable-archive-spec.md:150` | review-with-likely-update | Remove the backward-compat clause OR amend to "after the adr-placement-mechanism-repair-r1 feature ships (2026-05-24), all such directories have been migrated; the validator no longer needs an allowlist." Recommend remove (cleaner; consistent with FR-10's empty-allowlist post-condition). |
| `KB-documentation-criteria` | `references/deliverable-archive-spec.md:140, :144, :164, :181` | no-change | These are the post-ADR-0036 canonical-only statements; correct as-is. |
| `KB-documentation-criteria` | `references/shared-conventions.md:302` | no-change | Already aligned with ADR-0036. |
| `KB-documentation-criteria` | `references/templates/issue-register-template.md:96, :99` | update-with-fix (path-only) | Rewrite example paths from `working/feature/issue-capture-mechanism-r1/adrs/ADR-0046-*` and `ADR-0050-*` to canonical `adrs/ADR-0046-*` and `adrs/ADR-0050-*` form (or use generic `<slug>/<id>` template placeholders). |
| `KB-issue-capture` | `SKILL.md:72` | update-with-fix (path-only) | Rewrite worked-example header from `All ADR paths are relative to working/feature/issue-capture-mechanism-r1/adrs/` to canonical-path-form examples. |
| `capture-issue` | `SKILL.md:44` | update-with-fix (path-only) | Same pattern as `KB-issue-capture`. |
| `synthesize` | `SKILL.md:22, :240` | **review-with-explicit-disposition** | Q-CC-4 — synthesize's ADR-output is a different output target (`output/synthesis-<topic>/adrs/`) not in the feature-pipeline ADR space. Design Composer arbitrates whether (a) the validator allowlists `output/synthesis-*/adrs/`, (b) synthesize re-targets to canonical `adrs/`, (c) synthesize's ADR-emission is deprecated. Default expectation: (a) with explicit allowlist entry per FR-10 AC-FR-10-f. |

**8 file-level updates total** (per AC-NFR-4-a; no TBD findings). The Phase 5 Plan tasks are one per row above with disposition `update-with-fix`.

## 4. Cross-primitive interactions

### 4.1 How the three FR-10 enforcement surfaces invoke the validator (contract ratification)

Per Discovery IN-010, the `auditing-shared/scripts/` convention is:

| Aspect | Convention | The FR-10 validator conforms |
|---|---|---|
| CLI shape | Positional args, optional flags | `validate_adr_placement.py [scan_path] [--allowlist ...]` ✓ |
| Dependencies | Python stdlib only | `argparse`, `pathlib`, `json`, `sys`, `time` ✓ |
| Exit codes | 0 = clean, 2 = canonical-blocker-present, other non-zero = error | 0 / 2 / (any non-zero from unhandled exception) ✓ |
| Output format | JSON to stdout, structured | JSON with `verdict`, `findings`, `scan_path`, `elapsed_ms` ✓ |
| Subprocess dispatch | `subprocess.run(args, capture_output=True, text=True, timeout=120)` | 120s timeout is safely > the 5s NFR-2 budget ✓ |

The three surfaces invoke the validator identically (same script, same default args, same exit-code semantics). The only inter-surface difference is **how the failure is surfaced**: (a) orchestrator surfaces via `AskUserQuestion`; (b) `run_phase_checks.py` rolls into the 5-dimensional verdict; (c) packager folds into `packager-report.json` findings.

### 4.2 Migration phase-ordering (FR-8 sub-phases × 6 feature folders × 8 archive collisions)

The four sub-migrations have a non-trivial dependency order driven by FR-8b-renumber's need to know the post-FR-8d next-available ID:

```
Phase 2a (dedupe 12 byte-identicals, 4 folders) ─┐
Phase 2c (relocate 5 feature-scoped, 1 folder) ──┼─► (all 3 can run in parallel; no shared targets)
Phase 2d (consolidate 47 archive files) ─────────┘
                                                  │
                                                  ▼
Phase 2b (reconcile 3 cases):
  ADR-0024 status-lift dedupe (independent — can run with 2a) ──► canonical untouched
  ADR-0044 renumber (depends on Phase 2d completion)  ───────────► next-available canonical ID
  ADR-0045 renumber (depends on Phase 2d completion)  ───────────► next-available canonical ID
                                                  │
                                                  ▼
Phase 3 (cross-reference sweep, 14 + 18 = 32 references)
```

The CC design's recommendation to the Plan: Phase 2b sub-tasks split into 2b-status-lift (parallel with 2a) and 2b-renumber (sequenced after 2d). The Plan author owns the per-task decomposition; this CC design names the dependency graph.

### 4.3 Cross-reference sweep mechanics (FR-9 + NFR-3)

The 32 path-form references are sweep-able with Edit tool calls (per the IN-027 designer-general-knowledge note in Research Plan). The verification-at-Phase-6 mechanism: re-run the D5 Option B extended pattern set (the IN-008 grep set + the 3 edge cases Discovery validated); expect zero matches for former feature-scoped paths (excluding redirect notes per FR-8c and audit-trail files per Plan-defined audit-trail directories).

## 5. Tool restrictions and permissions

### 5.1 `finalize-deliverable-packager` tools-list expansion (per Q-CC-5)

The packager's current `tools:` is `Read, Glob, Grep, Write, TaskCreate, TaskUpdate` — no subprocess capability. FR-10 (d) requires the packager to invoke `validate_adr_placement.py`. Two design paths:

**Option Q-CC-5-A**: Add `Bash` to the packager's `tools:` frontmatter, ideally scoped: `Bash(python3 .claude/skills/auditing-shared/scripts/validate_adr_placement.py:*)`. Per KB-cc-platform's permissions model (allow/ask/deny), this is the smallest possible grant; permission policy is captured in `.claude/settings.json` rather than in the agent's tools list, so the tools-list change is `Bash`, with the settings.json allowlist constraining what `Bash` may invoke.

**Option Q-CC-5-B**: Keep the packager tool-restricted. Move the validator-invocation responsibility to the orchestrator — at Step 14, before invoking the packager, the orchestrator runs the validator subprocess and passes the JSON output to the packager as an input parameter; the packager folds it into `packager-report.json`. This preserves the packager's restricted tool surface at the cost of placing yet-another responsibility in the orchestrator Step 14.

Recommended: **Option Q-CC-5-A** (add `Bash`, narrowly scoped). Rationale: the packager already owns the `packager-report.json` shape; pushing validator invocation upstream would split responsibility across two agents for one output. The smallest tool grant + the narrowest settings.json allowlist entry is the lowest-cost change. Composer arbitrates.

### 5.2 `.claude/settings.json` permission-policy entries

If Q-CC-5-A is selected, the `allow` list in `.claude/settings.json` requires (one of):
- `Bash(python3 .claude/skills/auditing-shared/scripts/validate_adr_placement.py*)` — narrow form
- `Bash(python3 .claude/skills/auditing-shared/scripts/*.py:*)` — broader (covers any future auditing-shared script invoked by any agent)

Recommended: the narrow form. The broader form is convenient but lowers safety-net specificity (per KB-cc-design Principle 6: permissions-as-safety-net).

No new `deny` entries are required; the canonical-only policy is enforced by the validator's algorithm, not by a `permissions.deny` rule. (A `deny` rule could theoretically block writes to `working/feature/*/adrs/`, but it would have to be very specifically scoped — the orchestrator does write other artifacts to `working/feature/<slug>/` — and the validator-based enforcement covers the same case while being inspectable and reportable. Per Principle 1 + Principle 6: the validator is the lower-cost mechanism for this case.)

## 6. Bootstrapping note (this feature's own execution)

During execution of THIS feature (`adr-placement-mechanism-repair-r1`), the FR-10 validator does not yet exist at Phase 1 / 2 / 3, and the orchestrator surface (FR-10-b) at Step 8 is itself the file this feature edits. **The validator cannot enforce on this feature's own pipeline run.** The Plan should specify:

- The validator is authored at Phase 4 (after Phase 1 operator edits, after Phase 2 migrations, after Phase 3 sweep).
- The validator's first **self-test** runs at Phase 6 verification (post-feature; AC-OP-3 surface).
- The validator is wired into the three surfaces at Phase 4 (validator scaffold) + Phase 5 (skill-audit consequence: the orchestrator SKILL edit in FR-3 needs the FR-10 Step-8 gate text added to the same SKILL.md, ideally as the same edit pass).

The first feature to benefit from the new enforcement is the **next** feature-pipeline run after this one ships. The acceptance test for AC-US-1-a / AC-US-1-b / AC-OP-1 / AC-OP-4 is therefore run as a Phase 6 negative-path harness that simulates a future pipeline run (writes a contrived ADR to a feature-scoped path, runs the validator manually at all three surfaces, confirms all three block).

## 7. Acceptance criteria contribution (EARS, CC-layer)

These are the CC-layer-specific ACs the Composer should integrate into the Blueprint. (PRD already carries AC-US-N and AC-FR-N forms; the additions below are CC-design-specific ACs surfacing from §2–§6 above.)

- **AC-CC-1 (Validator script structure)**: When `validate_adr_placement.py` is invoked with no args on the post-feature repository state, the system shall return exit code 0 with JSON `{"verdict": "PASS", "findings": []}` and `elapsed_ms < 5000`.
- **AC-CC-2 (Validator script negative path)**: Where a test fixture writes `ADR-9999-fixture.md` to `working/feature/test-fixture/adrs/`, the system shall return exit code 2 with `verdict: BLOCK` and a `findings[]` entry citing the offending path and category `feature-scoped`.
- **AC-CC-3 (auditing-shared dispatch integration)**: When `run_phase_checks.py` is invoked after this feature ships, the system shall include `validate_adr_placement` in its dispatch set and fold its findings into the `validator` dimension (or a dedicated `adr_placement` dimension per Q-CC-7).
- **AC-CC-4 (Packager tool grant)**: Where Q-CC-5 resolves to Option A, the system shall list `Bash` in `.claude/agents/finalize-deliverable-packager.md` frontmatter `tools:` field, and `.claude/settings.json` shall contain a narrow allow-list entry permitting `python3 .claude/skills/auditing-shared/scripts/validate_adr_placement.py`.
- **AC-CC-5 (Orchestrator stage-gate integration)**: When `recipe-feature-pipeline/SKILL.md` Step 8 is read after this feature ships, the system shall describe the validator subprocess invocation between design-composer return and shared-document-reviewer invocation, with the failure-handling text matching the orchestrator's existing BLOCKER-surfacing pattern.
- **AC-CC-6 (No CLAUDE.md addition)**: When this feature ships, the system shall not add a CLAUDE.md entry, rule, output style, MCP server, or plugin (per §1 Principle 5 + Principle 1 + Principle 7).
- **AC-CC-7 (Skill audit completeness)**: When the Blueprint's skill-audit subsection is read, the system shall enumerate the 8 file-level findings per §3 FR-11 (each carrying a disposition: update-with-fix, no-change, or review-with-explicit-disposition) and shall mark 5 skill families as confirmed-clean.

## 8. Dependencies on other layers

**None.** This is a CC-only feature per PRD `layer_scope: ["claude-code"]`. The Plan, the Tests, the Acceptance Criteria all stay within the CC layer.

The single nearest-adjacent layer is **CI/CD (GitHub Actions)** — if any CI workflow invoked Claude Code or the validator from GitHub Actions, that would need designer attention. **Codebase analysis confirms no such CI invocation exists** (no `.github/workflows/*.yml` invokes the validator or any auditing-shared script). The validator runs locally (in Codespace, during the pipeline) and at the three CC-internal surfaces; no CI integration is needed.

## 9. Architectural Questions for Composer

Each question carries evidence, options, and a recommended default. The Composer arbitrates and either ratifies the default (no ADR needed) or authors an ADR to capture the cross-cutting decision (per FR-5: design-composer is the sole ADR author).

### Q-CC-1 — Final re-numbering scheme for ADR-0044 / ADR-0045 (synthesis D1)

**Evidence**: Discovery IN-002 confirmed the two ADRs are numbering collisions, not divergent bodies. Synthesis D1 documented three options.

**Options**:
- A: Re-number feature-scoped variants to next-available IDs **immediately** (ADR-0051, ADR-0052). Risk: collides if Phase 2d adds canonical entries with the same IDs.
- B: Re-number with a higher offset (e.g., ADR-0060, ADR-0061) to leave room. Risk: numbering-monotonicity violation; future-author confusion.
- C: Compute next-available number **post-Phase-2d**, after the 18 archive ADRs consolidate. Risk: serializes the migration phases.

**Recommended**: **C** (per Synthesis D1 recommendation). Phase 2d completes before Phase 2b-renumber; the next-available canonical ID is computed deterministically. Composer should author an ADR documenting the algorithm (max-ID + 1 + provenance frontmatter) so future contributors do not re-derive.

### Q-CC-2 — Default redirect-note extension for relocated feature-scoped ADRs (synthesis D6)

**Evidence**: Discovery's `convention.redirect_note_precedent` finding: no prior Plan in the repo creates a redirect note. OI-5 lists 4 options.

**Options**:
- A: One-line markdown file at `working/feature/<slug>/adrs/ADR-NNNN.md` (`.md` extension) — **trips the FR-10 validator** because the validator's algorithm finds any `ADR-*.md` outside canonical as a violation.
- B: Delete the originating file entirely (no redirect) — loses traceability; future readers of the originating folder do not learn the relocation happened.
- C: `.tombstone` file with non-`.md` extension at `working/feature/<slug>/adrs/ADR-NNNN.tombstone` — bypasses validator allowlist concern; clean separation.
- D: Symlink — was rejected in ADR-0036:107 (illustrative example).

**Recommended**: **C** (per Synthesis D6 recommendation). The `.tombstone` extension is unambiguous, doesn't trigger the validator's `ADR-*.md` rglob, and provides redirect traceability. The Composer may wish to define a 2–3-line tombstone-file template (header, target path, ADR-of-relocation-rationale citation).

### Q-CC-3 — Validator allowlist mechanism: per-invocation arg vs. config-file

**Evidence**: The validator's algorithm permits an `--allowlist` flag (per §3 FR-10 design). Mid-migration phases (Phase 2 in-flight) may legitimately have non-canonical ADRs present; an empty allowlist would block. Two mechanism options:

**Options**:
- A: Per-invocation CLI flag (`--allowlist working/feature/foo/adrs,working/feature/bar/adrs`) — explicit at every call site; auditable in the orchestrator's invocation; ephemeral.
- B: Per-config-file (`.claude/skills/auditing-shared/config/adr_placement_allowlist.json`) — central; can carry rationale per entry; risk of stale entries persisting.

**Recommended**: **A** (per-invocation CLI flag), with the empty-default semantics. Rationale: the allowlist is **almost always empty** (post-FR-8d, no legitimate non-canonical placement exists except `adrs/superseded/` which is structural-not-contingent and hard-coded). The CLI flag mechanism makes any allowlist usage visible at the call site (orchestrator / run_phase_checks / packager); config-file allowlist invites silent drift. Mid-migration usage of the flag (Phase 2 in-flight) is scoped to a single human-invoked call, not a persistent state.

### Q-CC-4 — Synthesize skill's ADR-output disposition (FR-11)

**Evidence**: Discovery IN-012 confirmed `synthesize/SKILL.md:22, :240` write ADRs at `output/synthesis-<topic>/adrs/ADR-NNN-<slug>.md` — a fundamentally different output target than the feature pipeline.

**Options**:
- A: Validator allowlists `output/synthesis-*/adrs/` paths (per FR-10 AC-FR-10-f explicit enumeration).
- B: synthesize re-targets ADR output to canonical `adrs/` — large scope expansion; conflates two distinct doctype spaces.
- C: synthesize deprecates ADR-emission entirely — removes a capability; unscoped consequence.

**Recommended**: **A**. The synthesize skill's output is for synthesis-pass research artifacts, not pipeline-governance ADRs; the two should remain separate. The validator allowlist entry must be explicitly enumerated in the Blueprint per AC-FR-10-f. Composer arbitrates whether to hard-code the `output/synthesis-*/adrs/` exception into the validator algorithm (treating it as structural-not-contingent, similar to `adrs/superseded/`) or to express it via the `--allowlist` flag at the run_phase_checks dispatch site.

### Q-CC-5 — Packager tools-list expansion vs. orchestrator-side validator invocation

See §5.1 above. **Recommended: Option A** (add narrowly-scoped `Bash` to packager tools + matching settings.json allow-list entry).

### Q-CC-6 — Mid-migration validator allowlist policy

**Evidence**: During Phase 2 of this feature's own execution, feature-scoped ADRs still exist at the locations they are being migrated FROM. If the FR-10 validator is wired into `run_phase_checks.py` during Phase 4, and Phase 5 invokes `run_phase_checks.py` (it should, per the execution-pipeline pattern), the validator would block on the still-in-flight `adrs/superseded/` archival pass for Phase 2b.

**Options**:
- A: Wire the validator at Phase 4 with an explicit non-empty allowlist for the in-flight feature folders; sunset the allowlist at Phase 5 (skill-audit edits include removing the allowlist entry).
- B: Wire the validator at Phase 5 (after all migration completes); skip Phase 4 wiring.
- C: Wire the validator at Phase 4 with empty allowlist; accept that Phase 5's `run_phase_checks.py` invocations will surface BLOCKERs that are then dispositioned as "expected during this feature's own bootstrapping" in the per-phase reconciliation log.

**Recommended**: **B** (wire at Phase 5). Rationale: Phase 4 (validator authoring) and Phase 5 (validator wiring into the three surfaces) are conceptually separable phases; this is the cleanest decoupling and avoids the mid-migration allowlist-then-sunset complexity. The Plan author should sequence: Phase 4 = author the script + smoke tests + run-against-current-repo (which WILL find findings; that's correct); Phase 5 = wire into surfaces only after Phase 2 + 3 complete and the script's output on the repo is empty. This makes Phase 5's wiring a no-op-on-current-state edit and naturally enforces from the next feature-pipeline run forward.

### Q-CC-7 — Validator dimension placement in `run_phase_checks.py`

**Evidence**: `run_phase_checks.py` aggregates findings into 5 dimensions (tests, audits, validator, discipline, scope_deviations). The ADR-placement validator could fold into the existing `validator` dimension (sibling of `validate_pipeline_frontmatter.py`) or warrant its own dimension.

**Options**:
- A: Fold into `validator` dimension — minimal change to `run_phase_checks.py`; consistent with the "validator" dimension name pattern.
- B: New `adr_placement` dimension — explicit; surfaces ADR-placement findings as a distinct rollup; aligns with the FR-10 "three-surface enforcement" emphasis on this being a load-bearing distinct concern.

**Recommended**: **A** (fold). The dimension granularity is a rollup-design decision in `run_phase_checks.py`, not a substantive one; folding keeps the dimension count stable and avoids surfacing this single validator as architecturally distinct from `validate_pipeline_frontmatter.py`. Composer may wish to ratify or override.

## 10. Open items (carried into Composer reconciliation)

The PRD's 5 Open Items map to this design as follows:

| PRD Open Item | Disposition in CC design |
|---|---|
| OI-1 (divergent-body archival format) | Resolved at design level (per Synthesis D3 recommendation Option A: `adrs/superseded/<id>-feature-scoped-body.md`). Composer ratifies. |
| OI-3 (validator implementation surface) | Resolved at design level (per Synthesis D4 recommendation Option A: Python script under `auditing-shared/scripts/`). Composer ratifies. |
| OI-4 (cross-reference inventory completeness) | Resolved at design level (per Synthesis D5 recommendation Option B: extended pattern set). Composer ratifies. |
| OI-5 (redirect-note format) | Surfaced as Q-CC-2 (Composer arbitrates the `.tombstone` extension decision). |
| OI-2 (gate-resolved earlier; `adrs-migrated/` consolidation) | Already binding; no design-level action required. |

The 7 Q-CC-N questions surfaced in §9 are the architectural questions requiring Composer arbitration. None require external research; all are CC-internal design decisions.

## 11. Provenance

- **Authored by**: `design-cc` sub-agent, run ID `adr-placement-mechanism-repair-r1-20260524-183201`, 2026-05-24.
- **PRD basis**: `prd-v1.md` v1.0.2 (Gate 2 approved 2026-05-24T19:10:00Z).
- **Research Plan basis**: `research-plan.md` v1.0.0 (Gate 3 approved 2026-05-24T19:20:00Z).
- **Synthesis basis**: `synthesis.md` v1.0.0 (streamlined mode; 0 external research topics).
- **Codebase analysis basis**: `codebase-analysis.json` v1.1.0 schema + `codebase-analysis-report.md`.
- **Authoritative discipline**: `KB-cc-design/SKILL.md` + `KB-cc-design/references/principles.md` + `KB-cc-design/references/patterns-and-anti-patterns.md`.
- **Authoritative platform**: `KB-cc-platform/SKILL.md` + (no reference files loaded — body sufficed for this design's primitive selection).
- **Authoritative template**: `KB-documentation-criteria/references/templates/blueprint-template.md` §"Claude Code / Project Filesystem Design".
- **Output filename**: `cc-design.md` per ADR-0019 Path-A reserved-word workaround (the agent name `design-cc` cannot contain `claude`; the design subsection is the Claude Code layer's contribution to the Blueprint).
