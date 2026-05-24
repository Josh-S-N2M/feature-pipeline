---
id: CBA-issue-capture-mechanism-r1
doc_type: codebase-analysis
version: 1.0.0
status: complete
feature_slug: issue-capture-mechanism-r1
derived_from: working/feature/issue-capture-mechanism-r1/research-plan.md
research_plan_user_token: approved-2026-05-23T18:48:00Z
generated: 2026-05-23T19:00:00Z
generated_by: discovery-codebase-researcher
companion_artifacts:
  - working/feature/issue-capture-mechanism-r1/codebase-analysis.json
  - working/feature/issue-capture-mechanism-r1/prd-v2.md
  - working/feature/issue-capture-mechanism-r1/research-plan.md
---

# Codebase Analysis Report — `issue-capture-mechanism-r1`

## Five most important things the Synthesis / Design stages should know

1. **This run introduces THREE firsts in the codebase.** No existing SKILL.md declares `disable-model-invocation: true`; no `.claude/hooks/` directory exists; no `"hooks"` block exists in `settings.json`. The two new skills (`KB-issue-capture`, `capture-issue`), the new hook script, and the new `hooks.PreToolUse` block in `settings.json` are all unprecedented in this project. Design must compose them from KB references alone — there is no in-project worked example to template against. (Findings F-001, F-002.)

2. **The validator (`validate_pipeline_frontmatter.py`) has very high blast radius.** Five direct callers (shared-document-reviewer, execute-task-quality-handler, run_phase_checks.py, smoke_test_auditing_shared.py, settings.json permission entry) and transitively every artifact produced by every pipeline sub-agent (because shared-document-reviewer's Gate 0 runs the validator). NFR-8 (zero false positives / zero false negatives on existing doc_types) is structurally critical and demands a regression-test corpus baseline captured BEFORE the FR-7 extension is implemented. The cleanest extension shape: add a fourth `issue` category branch to `validate_pipeline_artifact`, preserving the existing `gated`/`analysis`/`adr` category dispatch (F-008, F-012, VE-003, VE-004).

3. **The pipeline-isolation invariant (FR-13) holds at zero-baseline.** Three independent literal greps (`KB-issue-capture`, `issue-capture-author`, `capture-issue`) across `.claude/agents/` and across the entire `.claude/` tree (excluding `working/` and `Issues/`) all return zero matches. AC-FR-13-a and AC-FR-13-b are currently satisfied; design must preserve them. test-acceptance-author can encode the grep as a direct acceptance assertion. (F-010, F-015; full grep commands and results captured under `pipeline_isolation_check` in the JSON.)

4. **A critical cross-file CC-platform constraint applies to the new agent.** Skills with `disable-model-invocation: true` CANNOT be preloaded into a sub-agent's `skills:` field — they are silently dropped per the Claude Code platform contract (documented at `.claude/skills/auditing-subagents/references/subagent-spec.md` line 110 and `.claude/skills/auditing-cc-configs/references/common-failures.md` lines 101-103, and enforced as a BLOCKER by `auditing-cc-configs/scripts/cross_file_checks.py` X3 check). The new `issue-capture-author` agent's frontmatter MUST NOT list `KB-issue-capture` or `capture-issue` in `skills:`; instead the agent body must Read/Glob the skill files at runtime. This is the closest structural template to `cc-critique.md` (which uses no `skills:` field at all). (F-003, CP-001.)

5. **doc_type drift exists in the four pre-migration `Issues/*.md` files.** They use `deferral-register`, `analysis`, and `proposal` as doc_type values — NOT the new canonical `issue-register`, `issue-analysis`, `issue-proposal` set that PRD FR-7 prescribes. ONLY `Issues/issue-capture-mechanism/proposal.md` (the seed for this run) uses the new canonical `issue-proposal`. FR-8 migration must back-fill `doc_type` AND `version: 0.1.0` AND `status: open` AND any per-state required companion fields in the same atomic `git mv` operation. The `proposes_future_feature:` field has two existing precedents and should be allowed (advisory, not enforced) on issue-proposal doc_type. (F-005, F-006, F-009, CP-003.)

---

## Group A — Edit Targets (Existing Artifacts the Feature Modifies)

Per-touch-point summary. Full evidence in the JSON `nodes[]` and `blast_radius[]` sections.

### `.claude/skills/auditing-shared/scripts/validate_pipeline_frontmatter.py` (FR-7)

422 lines of pure-stdlib Python (no PyYAML). Three doc-type categories — GATED (5 values), ANALYSIS (15 explicit + 6 suffix patterns), ADR (single). Per-category state vocabularies are constants at module top (lines 38-68). Dispatch is path-based at line 365-371 (`SKILL.md`/`/skills/` → skill validation; `/.claude/agents/` → agent validation; else → pipeline-artifact validation). Hand-rolled YAML parser tolerates inline lists, bullet lists, and pipe-folded text. Finding shape is a fixed dict (see VE-002). The cleanest FR-7 extension adds a fourth `issue` category inside `validate_pipeline_artifact`, branching on `doc_type.startswith('issue-')` to a new `validate_issue_artifact` function. Blast radius is the broadest of any touch point — every pipeline artifact transits this script through shared-document-reviewer's Gate 0.

### `.claude/agents/intake-intent-clarifier.md` (FR-11)

93 lines. Already declares `prior_context` as an optional input parameter (line 28) and accepts `raw_request` as either text or path (line 25). The recipe-feature-pipeline orchestrator already passes `prior_context` (line 145 of recipe SKILL.md). FR-11's ~15-line insertion is purely body-level — a new branch in §Procedure that detects `doc_type: issue-proposal` in `--raw-request` and treats the file body as authoritative prior context. NO signature change required. Blast radius: intake-prd-author consumes the agent's output; shared-document-reviewer reviews it; finalize-deliverable-packager reads its `scope_class:` frontmatter. The edit is additive (new branch, not replacement); cannot break existing behavior for non-issue-proposal raw requests.

### `.claude/skills/KB-documentation-criteria/references/templates/intent-clarification-template.md` (FR-12)

Already has a `## Source` section at lines 36-38. FR-12's ~5-line edit adds a sub-paragraph noting that when `--raw-request` is a path to a `doc_type: issue-proposal` file, the Source section MUST cite the proposal path verbatim (per AC-FR-10-a). Structurally additive; preserves the existing one-sentence guidance for non-proposal-seeded runs.

### `.claude/skills/recipe-feature-pipeline/SKILL.md` (FR-12)

414 lines. The `--raw-request <text-or-path>` flag is already documented (line 14). The orchestrator already passes `prior_context` through to intake-intent-clarifier (line 145). The body is purely human-readable — no orchestrator code parses it. The FR-12 edit is one bullet documenting the proposal-seed invocation pattern (`<feature-pipeline> <slug> --raw-request Issues/<topic>/proposal.md`). Hard exclusion #1 (no stage advance without gate pass) at line 41 confirms no new gates may be introduced.

### `.claude/skills/KB-documentation-criteria/SKILL.md` (FR-14)

140 lines. Three tables index references and templates: "What's in this KB" (Concern | Reference), "Canonical templates" (Document type | Template | Authored by), "Routing: which reference do I need?" (Caller | Reference). FR-14 adds three rows to the "Canonical templates" table (one per new template), one row to "What's in this KB" for `issue-doctypes-spec.md`, and a new bullet to "Where this KB is NOT used" pointing at `KB-issue-capture` for triggering discipline. All additive.

### `.claude/SETTINGS-NOTES.md` (FR-15)

30 lines. Current sections: Purpose, Permission policy, User authorization, Reserved future-extensibility, Why this file exists separately. FR-15 appends a note documenting the new hook policy and the user authorization timestamp for the additive settings.json change. No existing section needs alteration.

### `.claude/settings.json` (FR-3 / FR-15)

13 lines. Currently ONLY a `permissions.allow` array with 7 entries (all pinned `Bash(python3 .claude/skills/.../scripts/*.py:*)` shape). NO `hooks` block. The new content: (a) optionally an 8th allow entry if the hook script is invokable from Bash (likely not needed — hooks run via Claude Code's hook event mechanism, not via Bash); (b) a new top-level `hooks` object with a `PreToolUse` array matching `Task`. **This is the project's first hooks block.** auditing-settings will be the primary auditor.

### `.claude/agents/issue-capture-author.md` (NEW)

Does not exist yet. Closest structural template is `.claude/agents/cc-critique.md` (95 lines, non-pipeline). Recommended frontmatter shape from CP-001: tools as comma-separated string with scoped `Bash(...:*)` entries (or no Bash at all for the issue-capture agent — its tool list per PRD: Read, Grep, Glob, Write, AskUserQuestion), `model: opus`, `effort: high`, **NO `skills:` field** (per F-003, the new skills carry `disable-model-invocation: true` and would be silently dropped from a sub-agent's preload list — BLOCKER per `auditing-cc-configs/scripts/cross_file_checks.py` X3). The agent body must Read the skill files at runtime instead.

### `.claude/skills/KB-issue-capture/` (NEW)

Does not exist yet. KB structure per ADR-0020: `SKILL.md` + `references/*.md`. The PRD's seed proposal anticipates 4 reference files (triage criteria, approval-prompt rubric, examples, non-pollution contract). The SKILL.md will be the first in this project to declare `disable-model-invocation: true`.

### `.claude/skills/capture-issue/` (NEW)

Does not exist yet. Slash-command-style entry-point skill. Will be the second in this project (along with KB-issue-capture) to declare `disable-model-invocation: true`. Per KB-cc-design Principle 1, slash commands superseded by skills with this flag.

### `.claude/skills/KB-documentation-criteria/references/templates/` — 3 new templates + 1 spec (FR-6)

Templates land alongside existing 11 templates. The empirical precedent for each doctype lives in the four pre-migration Issues files (per CP-004): register → tabular columns (ID/Item/Source/Why deferred/Re-examination trigger/Forgetting risk); analysis → prose + numbered evidence sections; proposal → prose + adoption guidance. Templates codify STRUCTURE only (per FR-6 + PRD §Won't-Have item); triggering discipline lives in `KB-issue-capture`.

### `.claude/hooks/` + new hook script (NEW)

Directory does not exist. Hook script does not exist. **First hook in the project.** Per the PRD's Risks #5, this is a real concern. Design must compose from KB-cc-platform/extensions.md primary guidance + auditing-hooks safety patterns (4 reference files; no `examples/` subdirectory exists per F-007). Fail-open posture (NFR-2) and ~100ms fast-path discriminator (NFR-1) are load-bearing.

---

## Group B — Precedent References (READ-ONLY)

### `Issues/register-devcontainer-mcp-provisioning-r1-deferrals.md`

WHAT TO MIMIC: frontmatter (id=REGISTER-<slug>, doc_type=deferral-register currently — FR-8 migrates to issue-register, status=draft, feature_slug, scope, mode=report-only, companion_artifacts as YAML list); tabular body structure (ID/Item/Source/Why deferred/Re-examination trigger/Forgetting risk) for sweep-style deferral registers. Multi-section organization by category (A/B/C/...) preserved in template.

### `Issues/analysis-per-agent-design-evaluation-gap.md` and `Issues/analysis-adr-placement-rootcause.md`

WHAT TO MIMIC: frontmatter (id=ANALYSIS-<slug>, doc_type=analysis → FR-8 migrates to issue-analysis), body opens with TL;DR + numbered sections (1. Evidence ... with subsections 1.1, 1.2, 1.3...) presenting concrete file:line citations. Analysis is evidence-driven, not opinion-driven. Template should require a TL;DR section and an evidence section.

### `Issues/proposal-auditing-family-graduation-review.md`

WHAT TO MIMIC: frontmatter (id=PROPOSAL-<slug>, doc_type=proposal → FR-8 migrates to issue-proposal, `proposes_future_feature: <suggested-slug>` as optional advisory field), body sections include Precedent/Triggering event, Why this matters, Inputs the future feature should consider, Suggested slug, Scope hints, Adoption. The proposal doctype is the seed-for-a-future-feature-pipeline-run shape — it requires more structure than analysis (it must be self-contained enough for `intake-intent-clarifier` to consume as authoritative prior context).

### `Issues/issue-capture-mechanism/proposal.md`

WHAT TO MIMIC: already-canonical post-migration shape (`Issues/<topic-slug>/<doctype>.md`), uses the new doc_type: issue-proposal, declares proposes_future_feature, anticipates POST-migration paths in companion_artifacts. Excellent self-describing precedent for the proposal template — this file IS the worked example for PRD U-3 (one of three doctypes' worked examples).

### `.claude/skills/KB-documentation-criteria/references/shared-conventions.md`

WHAT TO MIMIC: frontmatter inheritance source. The new templates' frontmatter declares: id, version, status, generated, generated_by (universal); feature_slug, doc_type (ADR-0032 Change 1 + 4); plus issue-specific: scope, mode, companion_artifacts. The new 5-state vocabulary is a FOURTH category alongside the existing 3-tier (gated / analysis-log / adr).

### `.claude/skills/KB-review-disciplines/references/issue-lifecycle.md`

WHAT TO MIMIC: NOTHING (read-only; the new 5-state vocabulary is parallel-but-distinct). The verbatim 4-state vocabulary is captured in VE-001 of the JSON for the design-composer's ADR to cite. The two systems share three state-name STRINGS (open, superseded, wontfix-with-rationale) but operate on distinct entities with distinct ID prefixes — the ADR must make this distinction explicit.

### `.claude/skills/auditing-skills/references/frontmatter-spec.md`

WHAT TO MIMIC: authoritative on `disable-model-invocation: true` semantics (line 58 in field table). The new skills declare this flag exactly per the spec. Note the related gotcha (lines 71-75): SKILL.md uses `allowed-tools:`, .claude/agents/*.md uses `tools:` — the new agent's frontmatter must use the latter.

### `.claude/skills/auditing-shared/scripts/check_pipeline_discipline.py`, `detect_stubs.py`, `log_state_transition.py`

WHAT TO MIMIC: CLI shape (argparse with positional paths or stdin), output shape (JSON to stdout, finding dict with fixed 7 fields), exit-code policy (default 0 = observer-only; optional --strict or --exit-on-blocker for fail-fast), stderr discipline (`<script_name>: <reason>` prefix). FR-7's extension preserves this idiom — no PyYAML dependency, no new CLI flags beyond what argparse supports trivially.

### `.claude/agents/cc-critique.md`

WHAT TO MIMIC: structural template for the new `issue-capture-author` agent. 95 lines. Frontmatter shape: `tools` as comma-separated string with `Bash(...:*)` scoped entries, `model: opus`, `effort: high`, `permissionMode: default`, NO `skills:` field, NO `memory:` field. Body opens with role statement, then numbered workflow, then "What you do NOT do" section. NO TaskCreate/TaskUpdate calls (cc-critique doesn't use them; the issue-capture-author probably should for orchestrator visibility — design-claude-code decides).

### `.claude/agents/shared-document-reviewer.md`

WHAT TO MIMIC: NOTHING DIRECTLY (it's a much larger 715-line agent invoked at 5 pipeline gates). But useful comparison: it DOES declare `skills:` (comma-separated string: `KB-documentation-criteria, KB-general-coding-principles, KB-review-disciplines`) and DOES use `memory: project`. None of those three skills declares `disable-model-invocation: true`, so preloading is legal here. The issue-capture-author differs structurally because its target skills DO declare the flag — and the F-003 constraint applies.

---

## Group C — Platform / Configuration References

Reviewed for design-time use. Brief findings:

- **`.claude/skills/KB-cc-platform/references/extensions.md`** (line 220-304): Hook contract fully documented. `PreToolUse` event semantics, `permissionDecision` ∈ {allow, deny, ask}, matcher regex against tool name, `if:` for sub-discrimination, stdin JSON event payload, stdout JSON `hookSpecificOutput`. `${CLAUDE_PROJECT_DIR}` env var is the canonical path-prefix. **Caveat (F-016):** The KB documents the general hook contract but does NOT explicitly demonstrate `tool_input.subagent_type` inspection inside a Task-tool hook. PRD Assumption 2 treats this as a working assumption; design-claude-code may need to verify against live platform docs.

- **`.claude/skills/KB-cc-design/references/principles.md`** (line 162): Confirms that slash commands are superseded by skills with `disable-model-invocation: true`. Justifies the design choice of `capture-issue` as a skill (not a legacy `.claude/commands/` slash command).

- **`.claude/skills/auditing-hooks/references/`** (4 files: hook-spec.md, security-checklist.md, anti-patterns.md, common-failures.md): substantive design-time references. **Important correction (F-007):** the Research Plan's mention of `examples/good-hook-annotated.md` and `examples/bad-hook-annotated.md` is WRONG — those files do not exist. Design works from the 4 references plus the platform extensions.md guidance.

- **`.claude/skills/auditing-skills/references/frontmatter-spec.md`**: Authority for `disable-model-invocation: true`. Field is at line 58 in the recognized-fields table.

- **`.claude/skills/auditing-subagents/references/subagent-spec.md`** (line 110): The cross-file BLOCKER constraint (F-003) — `disable-model-invocation: true` skills cannot be preloaded into a sub-agent's `skills:` field.

- **`.claude/skills/auditing-cc-configs/scripts/cross_file_checks.py`** (line 410, X3 check): The corresponding deterministic audit that catches a sub-agent with a `disable-model-invocation: true` skill in its `skills:` field.

---

## Group D — Pipeline-Isolation Verification (HARD INVARIANT)

**VERDICT: PASS — zero-baseline confirmed.**

Three independent literal greps performed at 2026-05-23T18:55Z against HEAD commit cf48e5e:

```
$ grep -r "KB-issue-capture" /workspaces/feature-pipeline/.claude/agents/
# (no output — zero matches)

$ grep -r "issue-capture-author" /workspaces/feature-pipeline/.claude/agents/
# (no output — zero matches)

$ grep -r "capture-issue" /workspaces/feature-pipeline/.claude/agents/
# (no output — zero matches)

$ grep -r "KB-issue-capture\|issue-capture-author" /workspaces/feature-pipeline/ \
    --include="*.md" --include="*.json" --include="*.py" --include="*.sh" \
    --exclude-dir=working --exclude-dir=Issues --exclude-dir=.git
# (no output — zero matches across the entire .claude/ tree)
```

The greps use literal substring matching without anchoring, so prose mentions (e.g., in comments, example sections, "see also" references) are included in the zero count. Per the user's Gate 3 confirmation (Research Plan §Open Questions #3), prose mentions are disallowed; the zero-baseline therefore satisfies both AC-FR-13-a and AC-FR-13-b in their strictest reading.

The invariant is intact at run start. Design must preserve it post-merge. test-acceptance-author can encode the exact greps as direct acceptance assertions (the greps are deterministic, deterministic-output, and trivially executable).

---

## Group E — Out-of-scope Adjacent Findings

### Existing `.claude/hooks/` and existing `hooks` block in settings

**Result: NONE exists.** Both `ls .claude/hooks/` and `grep '"hooks"' .claude/settings.json` return empty. The new PreToolUse hook for this feature is the project's first. (F-002 — important for design-claude-code and cc-critique.)

### ADR-0008 location

**Result: lives at `adrs-migrated/ADR-0008-issue-ledger-scope.md`, NOT `adrs/`.** This is the drift captured in `Issues/analysis-adr-placement-rootcause.md`. Per PRD §Risks #2 and Research Plan §Open Questions #2, this run does NOT migrate ADR-0008. The 7-ADR slate authored this run lands in `adrs/` per ADR-0036. ADRs referencing ADR-0008 may cite it at its current `adrs-migrated/` path. (F-004.)

### Existing `Issues/<topic>/` folder model

**Result: ONLY `Issues/issue-capture-mechanism/` exists** (the seed proposal's home). The four pre-migration flat Issues files are still at `Issues/*.md`. The per-issue folder model is being introduced in this run; the seed proposal already anticipates it. No collisions, no orphan folders. (Noted in the JSON `nodes` for `issue.issue-capture-mechanism-proposal`.)

---

## Closing Notes for Downstream Stages

- **Synthesis**: the JSON's `findings[]` enumerates 16 items; the most consequential (F-001, F-002, F-003, F-005, F-010, F-012) should feature in the Fact Disposition Table.
- **per-layer Design (Claude Code)**: the JSON's `convention_patterns[]` (CP-001 through CP-007) prescribes the structural choices; F-001/F-002/F-003 establish the constraints that bind the design.
- **per-layer Design (Backend)**: the JSON's `validator_extension_surface` section enumerates the current enum sets, vocabularies, dispatch, finding shape, and per-state required-field rules; the recommended extension shape is documented there. NFR-8 regression-corpus baseline must be captured before the extension is implemented (Research Plan §Risks #3).
- **design-composer**: the 7-ADR slate (PRD U-10) should cite the verbatim 4-state vocabulary from VE-001 when authoring the ADR that distinguishes the 5-state Issues vocabulary from the intra-pipeline 4-state ledger. F-004 confirms ADR-0008's location and the non-migration policy.
- **test-acceptance-author**: F-010 and F-015 confirm the AC-FR-13-a/b grep returns zero — these can be encoded as direct acceptance tests with the exact grep commands.
- **review-architecture-auditor**: F-004 (ADR-0008 drift) is informational and explicitly out-of-scope; do not raise as a finding on this run.

Extraction method: direct Read/Grep/Glob (no GitNexus MCP available — `.mcp.json` absent at project root). All claims in this report are grounded in concrete file-and-line citations captured in the companion JSON. Confidence is HIGH for direct citations and MEDIUM for transitive blast-radius estimates (which are computed from textual patterns rather than a verified call graph).
