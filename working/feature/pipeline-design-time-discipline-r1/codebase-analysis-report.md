---
id: CAR-pipeline-design-time-discipline-r1
version: 1.0.0
status: draft
doc_type: codebase-analysis-report
feature_slug: pipeline-design-time-discipline-r1
companion_json: working/feature/pipeline-design-time-discipline-r1/codebase-analysis.json
inherited_from: working/feature/pipeline-cross-artifact-discipline-r1/codebase-analysis.json
inherited_from_generated_at: 2026-05-26T13:30:00Z
generated: 2026-05-26T17:30:00Z
generated_by: discovery-codebase-researcher
---

# Codebase Analysis Report — Pipeline Design-Time Discipline (R2a)

## Executive summary

This is a thin overlay over the parent run's codebase-analysis. The parent's `codebase-analysis.json` (generated 2026-05-26T13:30:00Z) covers the FR-1/6/7/8/9/10 touch points at full fidelity and is **inherited verbatim**. R2a's incremental work captured here: (a) the three newly-accepted ADRs (0059, 0061, 0063) that close parent OIs and pin R2a's mechanism contracts; (b) the consolidated severity-vocabularies snapshot the ADR-0061 bridge author ingests; (c) re-confirmation of grep targets bearing on R2a's FRs; (d) watch-item evidence for the six open OI-R2a-* questions. Five ADRs were added since the parent extraction; three are R2a-scope (0059/0061/0063) and two (0060/0062) are R2b-scope captured for context only.

## Inheritance disposition

| Section | Disposition | Note |
|---|---|---|
| Components | Inherited verbatim (15 components) + 5 new (3 R2a ADRs + 2 R2b ADRs for context) | Parent's full inventory of 21 components remains accurate at HEAD |
| Dependencies | Inherited verbatim (21 edges) + 6 new edges from the 3 R2a ADRs | New edges all add prescription / extension relationships |
| Blast radius | Inherited verbatim (7 entries) + 5 R2a-specific re-confirmations | Re-confirmations refine the parent's findings for FR-1/6/7/8/9/10 |
| Conventions | Inherited verbatim + severity-vocabularies snapshot extension | Bridge-author canonical data added |
| Known issues | Inherited verbatim (7 issues) | Issue #2 (severity-vocab divergence) is being closed by this run's bridge content |
| Mechanism dependency table | Inherited verbatim (11 rows) | R2a uses rows for FR-1/6/7/8/9/10; new ADRs augment those rows |

## Thin overlay findings

### 1. Delta-since-parent

- **Agent count unchanged**: 37 `.claude/agents/*.md` files at HEAD; parent reported 37; delta = 0.
- **Five ADRs added since parent extraction**: ADR-0059, ADR-0060, ADR-0061, ADR-0062, ADR-0063. Of these, three are R2a-scope inherited (0059, 0061, 0063) and two are R2b-scope captured for completeness (0060 cross-file invariants for FR-3, 0062 MCP tool-surface drift for FR-5).
- **Files with no content drift since parent**: `KB-review-disciplines/severity-taxonomy.md` (still pre-bridge content, awaiting this run's authoring), `auditing-cc-configs/scripts/verdict_compute.py` (severity weights unchanged), `KB-cc-design/references/principles.md` (Principle 9 text unchanged at line 182).
- **Out-of-scope mtime touches**: one agent-memory file under `.claude/agent-memory/discovery-external-researcher/` (ephemeral).

### 2. Inherited ADR content shape

**ADR-0059** (FR-1 prescription extractor): canonical form is `adrs/ADR-NNNN-<slug>.prescriptions.yaml` sibling companion. Companion is OPTIONAL — ADRs without machine-checkable prescriptions have no companion; auditor no-ops per AC-FR-1-b. Schema v1.0.0 fields: `target_path`, `assertion.kind`, `severity_floor`. Initial `assertion.kind` vocabulary: `regex_present`, `regex_not_present`, `jsonpath_equals`, `jsonpath_count`, `file_exists`, `file_not_exists`, `substring_present`, `substring_absent`. New linter prescribed at `auditing-shared/scripts/validate_adr_prescriptions.py`.

**ADR-0061** (severity vocabulary bridge): preserves trifecta (auditor/reviewer/PV); hosts bridge at `KB-review-disciplines/references/severity-taxonomy.md`. NFR-8 four-field shape `{rule, target, divergence, next_action}` co-locates with the bridge. Optional translator at `auditing-shared/scripts/translate_severity.py`.

**ADR-0063** (Blocks-X marker grammar): canonical form `<!-- BLOCKS: <stage-slug>-completion -->`. Parser regex: `<!--\s*BLOCKS:\s*([a-z0-9-]+)-completion(?:\s+—\s+[^\n]*)?\s*-->`. Three reserved `transition_name` values: `BLOCKS_X_RESOLVED`, `BLOCKS_X_DEFERRED_WITH_OI`, `BLOCKS_X_FALSE_POSITIVE` (no schema evolution required per ADR-0044 v1 free-string invariant). Grammar spec prescribed at new file `.claude/skills/KB-documentation-criteria/references/blocks-x-marker-grammar.md`.

### 3. Severity-vocabulary canonical numbers (for ADR-0061 bridge author)

This is the load-bearing input for design-composer's bridge content under ADR-0061.

**Verdict-compute canonical weights** (`auditing-cc-configs/scripts/verdict_compute.py:54-58`):

| Severity | Per-finding weight | Additional flat penalty |
|---|---|---|
| BLOCKER | -12 | -12 (per BLOCKER on top — total -24) |
| MAJOR | -5 | 0 |
| MINOR | -2 | 0 |
| NIT | -0.5 | 0 |
| INFO | 0 | 0 |

Verdict threshold tuple includes `(85, "PASS-WITH-MINOR-FIXES")` (verdict_compute.py:64). Full thresholds: PASS 95+, PASS-WITH-MINOR-FIXES 85–94, NEEDS-WORK 70–84, FAIL <70.

**Iteration-delta weights** (`review-cross-artifact-auditor.md:93` — DIFFERENT set, used for delta across review iterations):

| Severity | Delta weight |
|---|---|
| BLOCKER | 10 |
| MAJOR | 3 |
| MINOR | 1 |
| INFO | 0 |

The bridge table SHOULD document both weight sets exist; collapsing them silently would obscure iteration-delta semantics. Surfaced as Open Question #2.

**Intra-auditor vocabulary divergence**: `auditing-mcp/SKILL.md` uses `BLOCKER/MAJOR/MINOR/NIT` (no INFO); `review-architecture-auditor.md` and `review-cross-artifact-auditor.md` use `BLOCKER/MAJOR/MINOR/INFO` (no NIT). `verdict_compute.py` canonical superset accepts both NIT and INFO as distinct values. Bridge author preserves both per ADR-0061's "document non-monotonic edges, don't collapse them" guidance.

**Reviewer-discipline vocabulary** (verbatim from `KB-review-disciplines/references/severity-taxonomy.md`):

- `critical` — blocks acceptance; architecturally wrong, security-breaking, contract violation, or fundamentally infeasible. Cannot be deferred.
- `important` — should be fixed before approval but isn't architecturally fatal. Degrades the score. Deferrable only with explicit user approval + ledger entry.
- `recommended` — improvement suggestion. Non-blocking.

Verdict mapping in that file: any `critical` → needs_revision; `important` only + consistency>80 + completeness>75 → approved_with_conditions; only `recommended` + consistency>90 + completeness>85 → approved; many critical → rejected.

**PV vocabulary**: `blocking` / `warning` / `informational` (inlined in `test-phase-validator-author.md` Phase 2; not in KB-task-decomposition per parent Known Issue 3).

**Non-monotonic edges the bridge must document explicitly**:

| Edge | Auditor side | Reviewer / PV side | Translation note |
|---|---|---|---|
| NIT ↔ recommended | -0.5 weight; "taste" framing | non-blocking; "improvement" framing | NIT → recommended safe; reverse loses actionability |
| MAJOR ↔ {blocking, warning} | -5 weight; conditional_pass if no BLOCKER | depends on PV invariant blocking-class | default MAJOR → blocking; downgrade to warning only with per-finding rationale |
| NIT vs INFO (intra-auditor) | NIT -0.5 in auditing-mcp; INFO 0 in arch/cross auditors | n/a | bridge preserves distinction: NIT = taste/style; INFO = neutral observation |

### 4. R2a-specific blast-radius re-confirmations

- **Principle 9 cross-refs (FR-8)**: TWO sites at HEAD — `principles.md:15` (TOC) + `principles.md:182` (heading) + `design-claude-code.md:56` (verbatim citation: "Reasoning configuration is intentional, not default (per KB-cc-design Principle 9): explicitly justify the model: choice..."). Parent count of cross-references stands. AC-FR-8-b mutual cross-reference: FR-8 rewords Principle 9 → updates body at `principles.md:182` → coordinated update at `design-claude-code.md:56` so the cited text matches the new active framing AND cross-references FR-6's matrix discipline.
- **review-architecture-auditor consumers (FR-1)**: unchanged from parent. FR-1's `checks_performed[]` addition of `'design_realization'` and `issues[].category` addition of `'design_realization'` are additive; no consumer indexes into fixed shape. NFR-8 four-field shape additions safe across the 12 known downstream consumers.
- **auditing-subagents rule sites (FR-10)**: ZERO existing rules predicate on "feature working directory shape". FR-10 ADDS the first such rule. New script must accept feature-slug as parameter (new shape vs. existing auditing-subagents scripts which take `.claude/agents/<file>.md`).
- **KB-task-decomposition PV-author consumers (FR-7)**: KB-task-decomposition is NOT a natural attachment point — only consumer is `finalize-task-decomposer` (per the KB's own SKILL.md:24); PV-author rubric is inlined in `test-phase-validator-author.md` Phase 2. Recommended attachment for FR-7 Skill-Coverage Decisions section: KB-documentation-criteria/references/templates/ (new section template) embedded in existing synthesis / blueprint / cc-design templates.
- **KB-review-disciplines consumers (ADR-0061 bridge)**: 20 agents load KB-review-disciplines at HEAD. Bridge content additions are automatically visible to all of them — no separate propagation work needed.

### 5. Watch-item evidence for OI-R2a-1..6

| OI | Status | Key evidence |
|---|---|---|
| OI-R2a-1 (FR-6 trigger evaluator) | HIGH suitability | Parent IN-014 confirms table-shaped FR-7 output is mechanically parseable |
| OI-R2a-2 (auditing-skills reverse-check) | Not investigated this run | Carried as Blueprint Open Question per PRD policy |
| OI-R2a-3 (FR-9 marker-parser host) | No existing parser; recommend `auditing-shared/scripts/parse_blocks_x_markers.py` | Grep for `BLOCKS:` / `<!-- BLOCKS` across all candidate hosts returns zero matches |
| OI-R2a-4 (FR-7 artifact location) | No precedent of standalone artifact; embedded section lower-irreversibility | `find working/feature/ -name 'skill-coverage*'` returns zero matches |
| OI-R2a-5 (FR-10 rule realization) | No existing predicate on feature-working-directory; ADD new rule (not extend) | Grep for `working/feature` / `working-directory` in auditing-subagents/ returns zero matches |
| OI-R2a-6 (bridge sequencing) | No collision; bridge content additions are purely additive | `git diff --stat` on `severity-taxonomy.md` returns empty |

### 6. Skill-coverage dogfood inputs (FR-7 self-application)

Pre-survey for the six new domain concepts FR-7 self-applies to:

| Concept | Covering skill | Decision |
|---|---|---|
| Design-realization audit (FR-1) | KB-review-disciplines (Lens 4 in `architecture-audit.md`) | existing-skill |
| Agent-roster impact matrix (FR-6) | KB-cc-design + KB-documentation-criteria (new template file) | existing-skill |
| Skill-coverage decision check (FR-7) | KB-documentation-criteria (new section template; embedded per OI-R2a-4) | existing-skill + new-template-file |
| Principle 9 active reframing (FR-8) | KB-cc-design (in-place rewrite) | existing-skill |
| Blocks-X marker grammar (FR-9) | KB-documentation-criteria (new reference file per ADR-0063) | existing-skill + new-reference-file |
| Matrix-missing audit rule (FR-10) | auditing-subagents (new SA-NN + new script) | existing-skill |

All 6 concepts land in existing skills — the strongest possible inheritance posture. FR-7's self-applied skill-coverage table is a 6-row all-existing-skill decision.

## Deltas downstream stages should know

1. **Three load-bearing ADRs added since parent**. FR-1's prescription-extractor (ADR-0059), FR-9's marker grammar (ADR-0063), and severity-bridge host (ADR-0061) are PINNED. Synthesis must frame against the canonical ADR text rather than against parent PRD prose.
2. **Severity vocabulary trifecta is canonical**. Five FRs across R2a + R2b emit findings consumed across all three vocabularies. The bridge content this run authors at `severity-taxonomy.md` is the load-bearing reconciliation surface.
3. **PV-author rubric is in the agent prompt, not the KB**. The parent's correction (parent Known Issue 3) stands — FR-7's natural attachment surface is KB-documentation-criteria/references/templates/, not KB-task-decomposition.
4. **All R2a FRs land in existing skills**. No propose-new-skill signal in the dogfood pass. New files are added within existing skill directories (one new template file, one new reference file, one new script, plus in-place edits to two existing files).
5. **Iteration-delta weights ≠ verdict-compute weights**. Two distinct severity-weight sets exist in the codebase. Bridge author must explicitly document both; collapsing would lose semantic information (Open Question #2).

## Open questions for human resolution

See `codebase-analysis.json` `open_questions_for_human[]`. Three items:

1. FR-7 Skill-Coverage Decisions section location (embedded vs standalone) — carried as Blueprint Open Question per PRD policy.
2. Bridge table documents both verdict-compute weights AND iteration-delta weights — bridge-content authoring decision the composer must make explicitly.
3. FR-1 audit mechanism scope — companion-file predicates only, or extended to catch stale-doc drift (the audit_op2_consumer_mapping.py exemplar)?

---

*End of report. JSON companion at `working/feature/pipeline-design-time-discipline-r1/codebase-analysis.json` is the canonical artifact for downstream consumers; this report is the human-readable summary.*
