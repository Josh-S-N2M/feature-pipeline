---
feature_slug: audit-findings-remediation-r1
version: 1.0.0
status: complete
generated: 2026-05-21T18:05:00Z
generated_by: claude (acting as discovery-codebase-researcher)
derived_from: working/feature/audit-findings-remediation-r1/research-plan.md
companion_data: codebase-analysis.json
---

# Codebase Analysis Report — audit-findings-remediation-r1

## Executive summary

Discovery resolved 10 of 10 codebase information needs (the 9 PRD-original ones + IN-013 added during execution per ADR-0029). **Two scope deviations surfaced**; one resolved via PRD amendment (FR-7-b tightened + FR-12 added in PRD v1.1.0), one pending user resolution (Category E bypass-approval findings are auditor false positives, not agent defects).

Key codebase findings:

- **3 copies of `pedagogical_marker_check.py`** exist (not 2 as PRD assumed) — driver of PRD amendment v1.1.0
- **X9 finding is a self-documented STUB** — FR-6 Stream 2 is straightforward replacement, smaller effort than estimated
- **Recursive-audit capability already exists** in `audit_project.py` — FR-6 Stream 2 wires it, doesn't invent it
- **SA-2 regex is over-narrow** vs project's description-writing style — strong evidence for option (ii) "tighten regex" over option (i) "rewrite 29 descriptions"
- **3 of 6 Category E findings are auditor false positives** (negative-instruction misreading) — changes the disposition character for FR-5
- **synthesize + report-composition-knowledge are ACTIVE skills** — Category C real-fix disposition confirmed
- **shared-document-reviewer has clean extension point** for FR-7-b enforcement

## Scope-deviation findings (per ADR-0029)

### SD-001 — Three pedagogical_marker_check.py copies (RESOLVED)

PRD assumed 2 copies; reality is 3. Each is invoked by a distinct audit dispatcher. Resolved via PRD amendment v1.1.0:
- FR-7-b tightened: enforcement applies uniformly across all three (or in the deduplicated shared module after FR-12)
- FR-12 added: deduplication of the three near-duplicate copies into a canonical implementation

Status: resolved 2026-05-21T17:55:00Z via path (a) PRD amendment.

### SD-002 — Category E bypass-approval BLOCKERs are auditor false positives (PENDING)

The 3 "Body instructs subagent to bypass approval/safety prompts" BLOCKERs fire on NEGATIVE instructions:
- `design-claude-code.md:98` — "You do NOT skip the permission policy"
- `finalize-reconciler.md:214` — "You do NOT skip the convergence check"
- `review-cross-artifact-auditor.md:177` — "You do NOT skip the convergence check"

The auditor regex `\b(ignore|bypass|skip|override)\b.{0,30}(approval|prompt|permission|safety|check)\b` (in `scan_subagent_body.py:38`) matches the verb+noun pair regardless of preceding negation. These are **guardrails, not bypass instructions** — the agents explicitly tell themselves NOT to skip the relevant checks.

**Disposition options:**
- (i) Reword the negative instructions to avoid the trigger words (less clear; teaches the wrong thing — guardrails should be loud, not euphemistic)
- (ii) Tighten the auditor regex to handle negation (better; fixes the same class for any future negative-instruction guardrail)
- (iii) Both — auditor fix + slight rewording (defense in depth)

**Resolution-path candidates per ADR-0029:**
- (a) **PRD amendment** — Category E character changes from "6 genuine agent defects" to "3 wildcard-shell agent defects + 3 auditor false positives." FR-5 ACs may need adjustment: AC-FR-5-b (zero bypass-approval BLOCKER findings) becomes satisfiable by the auditor regex fix instead of/in addition to agent edits. Estimated PRD revision: ~10 lines.
- (b) Defer the auditor regex fix to a follow-on; reword 3 agent bodies this run. Solves the immediate finding but trains future authors that guardrails must be cosmetically softened to pass audit — wrong incentive.
- (c) Reject the deviation; treat AC-FR-5-b literally and reword the bodies. Same problem as (b).

Recommended: **(a) with option (iii)** — amend FR-5 to permit auditor regex fix as one valid disposition path; per-layer Design picks whether to also reword. Most defensible per intent constraint 3 ("fix the auditor; improve, don't suppress").

Status: PENDING — awaiting user resolution.

## Per information-need findings

### IN-002 + IN-013 — Pedagogical marker triage (3-copy reality)

| Copy | LOC | Called by | Notable divergence |
|---|---|---|---|
| `auditing-cc-configs/scripts/pedagogical_marker_check.py` | 452 | `triage_with_judge.py`, tests | canonical baseline |
| `auditing-skills/scripts/pedagogical_marker_check.py` | 452 | `audit_skill.py` | comment diffs + `f.get("location") or f.get("where")` defensive backward-compat (real semantic difference; must be preserved per AC-FR-12-d) |
| `auditing-subagents/scripts/pedagogical_marker_check.py` | 452 | `audit_subagent.py` | comment diffs only (no semantic differences) |

The 18-28 line pairwise diffs are mostly comment formatting (~15 lines per pair) plus the `location`/`where` field-name compat in the skills copy. Deduplication into a shared canonical module is straightforward; the backward-compat must be preserved (it serves real cross-module schema variance, not noise).

Related discovery: `scan_memory_secrets.py` exists identically in `auditing-context-files/` and `auditing-subagents/`. Pattern of duplicate-script-across-audit-skill-modules is broader than `pedagogical_marker_check.py`. AC-FR-12-e mandates the scan; Plan stage decides whether to absorb `scan_memory_secrets.py` into FR-12 or defer.

### IN-003 — Existing pedagogical markers inventory

**`pedagogical_sections:` frontmatter declarations** in 9 files: `auditing-cc-configs/SKILL.md`, all 5 other `auditing-*/SKILL.md` files, `KB-general-coding-principles/SKILL.md`, `auditing-subagents/SKILL.md`.

**`audit-example` fence wraps** in 10+ files across `auditing-cc-configs/references/`, `auditing-context-files/references/` (8 files), `auditing-context-files/examples/`.

**`<pedagogical-example>` HTML-tag form** unique to 2 files: `KB-visual-design/references/anti-slop.md`, `KB-visual-design/references/type-color-space.md`. This is the v4.4.0-shipped form FR-8 explicitly calls out.

FR-8 retroactive-upgrade scope is therefore: ALL markers in ALL 20+ files come up to FR-7-d standard (justification per marker). Larger than PRD-original framing suggested ("anti-slop.md") but covered by FR-8's wording ("All markers in the project at feature-end").

### IN-005 — X9 origin and data access

X9 emission lives at `auditing-cc-configs/scripts/cross_file_checks.py:622`, function `check_X9_subagent_skills_security_block`. Self-documents as STUB. At emission time, the function has access to the subagent file path + the parsed `skills:` list from frontmatter. It does NOT have access to per-skill audit results because the recursive audit has not been wired.

### IN-006 — Recursive audit capability

`audit_project.py` already does the heavy lifting:
- Line 26: `import subprocess`
- Lines 35-37: hard-coded paths to `audit_skill.py` and `audit_subagent.py`
- Lines 51+: `subprocess.run(...)` with timeout for dispatching per-skill audit

For FR-6 Stream 2, the X9 function can either (i) be moved/extended to invoke this dispatch directly for each subagent's preloaded skills, OR (ii) the dispatch can be refactored into a reusable utility that both `audit_project.py`'s main loop AND the new X9 check use. Per-layer Design picks; option (ii) is cleaner architecturally.

### IN-007 — SA-2 regex test

Tested TRIGGER_PATTERNS regex against 10 of 29 flagged descriptions. Zero matches. Sample:

| Agent | Description excerpt | Has trigger? | Why missed |
|---|---|---|---|
| `design-frontend.md` | "Authors the Frontend Design subsection of the Blueprint during per-layer Design..." | NO | "during X" not in regex |
| `plan-author.md` | "Authors the Implementation Plan at the Plan Authoring stage..." | NO | "at the X stage" not in regex |
| `intake-intent-clarifier.md` | "...Use at pipeline start, before PRD authoring..." | NO | "Use at" not in regex (only "use when"/"use for") |
| `review-architecture-auditor.md` | "At the Architecture Audit stage (after shared-document-reviewer passes the Blueprint)..." | NO | "At the X stage" not in regex |
| `synth-extractor.md` | "Extracts atomic, source-cited claims from a single source document. One invocation per..." | NO | "One invocation per" not in regex |

Patterns the regex misses (present in real descriptions): "At the X stage", "during X", "Use at", "One invocation per", "When [noun]" (not "when V-ing"), "after [predecessor]".

**Verdict for U-2:** Option (ii) tighten regex is the right call. Adding 4-6 more pattern alternatives covers the project's actual description-writing style without weakening real detection. Option (i) (29 description rewrites) treats the symptom, not the cause; future agents would face the same regex-mismatch issue. Plan stage decision but the codebase evidence points clearly.

### IN-008 — synthesize + report-composition-knowledge active status

Both skills are ACTIVE:
- `.claude/skills/synthesize/SKILL.md` — mtime May 19 2026; user-invocable orchestrator; full 6-phase pipeline
- `.claude/skills/report-composition-knowledge/SKILL.md` — mtime May 20 2026; declared as loaded by `synth-synthesizer` agent's `skills:` list

`synth-synthesizer.md` is one of the 30 pipeline agents and references both skills in its body. Neither skill is deprecated. The 18 Category C broken-link findings are real defects in active content; Plan stage authors the per-finding disposition (repair/delete/reauthor per AC-FR-3-b).

### IN-009 — Category E genuine defects (per-file inspection)

**3 wildcard-shell MAJOR findings** (genuine defects):
- `discovery-codebase-researcher.md` — `tools: [Read, Glob, Grep, Bash, Write, TaskCreate, TaskUpdate]` — Bash declared unscoped
- `review-architecture-auditor.md` — same pattern
- `shared-document-reviewer.md` — `tools: Read, Grep, Glob, LS, Bash, TaskCreate, TaskUpdate, WebSearch` — same

Fix per agent: scope Bash to the specific commands actually used in the body (likely `Bash(git diff:*)` or similar; per-layer Design inspects bodies to determine scope).

**3 "bypass approval" BLOCKER findings** (per SD-002 above): auditor false positives, not agent defects. See scope-deviation section for resolution path.

### IN-011 — Audit report presentation

Report is 451 lines. Structure: top-level ## headers (Inventory, Summary, Skills, Subagents, Cross-file, How-to-read), per-file ### headers, findings grouped by severity within each file via `[BLOCKER]/[MAJOR]/[MINOR]` tags.

Presentation is adequate; finding-categorization is possible but manual. FR-10 P2 improvements that would meaningfully help: (i) summary table at top showing count-per-root-cause-category; (ii) optional "root-cause grouping" mode that re-groups findings by inferred category instead of by file.

Both are modest work (<2 hours each). Plan stage decides whether to include.

### IN-012 — shared-document-reviewer extensibility

`shared-document-reviewer.md` already has a clean doc_type extension pattern. Current types: `PRD`, `ADR`, `UISpec`, `DesignDoc`, `IntentClarification`, `Plan`, `DeliverableArchive`. Adding `PedagogicalMarkerJustification` is straightforward and matches the v4.5.0 extension pattern (DeliverableArchive added via the same mechanism).

**Architectural choice for FR-7-b enforcement** (per-layer Design decision):
- Option A: Add `PedagogicalMarkerJustification` doc_type to shared-document-reviewer; the validator runs during normal review cycles
- Option B: Keep FR-7-b enforcement entirely in `pedagogical_marker_check.py` (or its post-FR-12 deduplicated form)
- Option C: Both — auditor enforces at scan time; reviewer validates at gate time (defense in depth)

Both A and B work. C provides redundancy at modest extra cost. Per-layer Design picks.

## Conventions captured

1. **Agent tools declaration:** Both comma-separated and YAML flow-sequence parse correctly post-v4.5.0; comma-separated is project convention (23 of 30 agents).
2. **Cross-cutting spec location:** `.claude/skills/KB-documentation-criteria/references/`. Note: existing `pedagogical-marker-spec.md` actually lives in `auditing-cc-configs/references/`; the per-layer design for FR-7-a may want to either move it OR add a forward-pointer from KB-documentation-criteria.
3. **Subagent description style:** Project agents use "At the X stage, …", "during per-layer Design", "One invocation per …" — clearly delegation triggers but not in the SA-2 regex's current pattern set.
4. **Duplicate-script pattern:** `pedagogical_marker_check.py` (3 copies) is not unique; `scan_memory_secrets.py` is also duplicated. AC-FR-12-e mandates a wider scan.

## Risks identified during discovery

| Risk | Stage to address | Mitigation |
|---|---|---|
| Per-layer Design for FR-7 specifies a justification syntax that doesn't fit either frontmatter OR fence-wrap cleanly | per-layer Design | Use T-001's recommended forms — structured frontmatter + `--` separator for fences |
| FR-12 deduplication misses additional duplication patterns (e.g., `scan_memory_secrets.py`) | per-layer Design (AC-FR-12-e scan) | The scan is in scope; surfacing per ADR-0029 makes any additional findings explicit |
| SA-2 regex tightening overcorrects and misses real description-quality issues | Plan + Acceptance Tests | Test cases for the new regex must include both positive (current 29) AND negative (low-quality descriptions that SHOULD fire SA-2) cases |
| SD-002 resolution rewords negative instructions cosmetically instead of fixing the auditor | Pending user decision + Cross-Artifact Audit | Per ADR-0029, cosmetic rewording would be a silent fix of an auditor defect; Cross-Artifact Audit should flag this if it happens |

## Discovery completion checklist

- [x] All 9 codebase-topic IN-NNN resolved
- [x] All touch points enumerated with role + purpose
- [x] Blast radius mapped (pedagogical_marker_check dependents, X9 fan-out, audit invocations)
- [x] Conventions captured (4)
- [x] Findings documented (9)
- [x] Scope deviations surfaced per ADR-0029 (2: SD-001 resolved, SD-002 pending)
- [x] codebase-analysis.json companion data file authored
