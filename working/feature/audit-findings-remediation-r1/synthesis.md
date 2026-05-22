---
feature_slug: audit-findings-remediation-r1
version: 1.0.0
status: complete
generated: 2026-05-21T18:25:00Z
generated_by: claude (acting as Stage 5 fan-in)
derived_from:
  - working/feature/audit-findings-remediation-r1/codebase-analysis.json (v1.0.0)
  - working/feature/audit-findings-remediation-r1/codebase-analysis-report.md (v1.0.0)
  - working/feature/audit-findings-remediation-r1/research-notes/T-001.md
  - working/feature/audit-findings-remediation-r1/prd-v1.md (v1.2.0, current)
  - working/feature/audit-findings-remediation-r1/adrs/ADR-0029-no-silent-scope-changes-principle.md
---

# Synthesis — audit-findings-remediation-r1

## Note on synthesis-machinery scope

The project's `synth-*` agent chain (synth-extractor → grapher → critic → framer → substrate → synthesizer) is built for multi-source research synthesis with claim-level CoVe verification and three-option substrate enumeration per architectural decision. That machinery applies to research-heavy features with many sources and contested claims.

This feature's research surface is small: one external research note (T-001), one codebase analysis, and the PRD/intent/ADR-0029 inputs. Running the full 6-agent claims-extraction chain would consume more context than it produces value. This synthesis fans in directly into structured findings + design implications + open questions for per-layer Design. **No scope deviation surfaced** — the recipe says "synth-* fan-in" without prescribing depth; lightweight fan-in is appropriate for the input size.

If a future feature run hits this same scale-mismatch, an ADR documenting the recipe's "scale-appropriate synthesis" implicit rule would be worth authoring. Not for this run.

## Source map

| Source | Type | Key contribution |
|---|---|---|
| `codebase-analysis.json` + report | Discovery (codebase) | 9 findings; 2 resolved scope deviations; touch points across 11 files |
| `research-notes/T-001.md` | Discovery (external) | 5-ecosystem suppression-discipline survey; 5 patterns to adopt, 4 to reject |
| `prd-v1.md` (v1.2.0) | Intent / requirements | 12 FRs (P1: FR-1 through FR-9, FR-12; P2: FR-10; P3: FR-11); 26+ ACs across all FRs; updated through 2 amendments |
| `intent-clarification.md` | Intent | 4 user constraints (markers OK if disciplined; fix auditor not suppress; sequencing is Plan's call; "1 could be major" → ADR-0029) |
| `ADR-0029` | Principle | No-silent-scope-changes — constrains every downstream stage |

## Decisions framed (carried to per-layer Design)

Each "decision" below is a place where per-layer Design must pick an option. The synthesis collects the options + their evidence; the per-layer designer (`design-claude-code`) writes the design subsection with documented rationale.

### D-1 — Mechanism α justification syntactic form

**Question:** What exact syntax do justifications take in (a) frontmatter and (b) fence-wrap form?

**Inputs:**
- T-001 patterns to adopt: structured frontmatter; `--` separator for fences; machine-parseable
- T-001 patterns to reject: bare-list form; legacy escape hatches; separate tracking files
- Existing convention (`pedagogical-marker-spec.md`): current frontmatter is `pedagogical_sections: [path1, path2]` (bare list — no justification slot); current fence form is ``` ```audit-example ``` (no separator slot)

**Options:**
- **(α-1) Structured frontmatter dict + `--` fence:**
  ```yaml
  pedagogical_sections:
    - path: references/foo.md
      justification: "Documents credential patterns the auditor should look for; not real credentials"
  ```
  Fence: ` ```audit-example -- credential-shaped string is illustrative `
- **(α-2) Inline JSON-shaped string in frontmatter + same fence:** more compact, less readable.
- **(α-3) Hybrid: frontmatter declares the file with justification; fence justifications optional unless triggering a specific finding-type.** More flexible but creates two discipline levels.

**Recommendation evidence:** T-001's primary citations + the project's existing fence pattern. (α-1) is the cleanest match.

### D-2 — Mechanism α enforcement location

**Question:** Where does the rejection-on-missing-justification check live?

**Options:**
- **(D2-A) In the deduplicated `pedagogical_marker_check.py`** (post-FR-12). The marker triage is already there; adding a justification-presence check is co-located.
- **(D2-B) In `shared-document-reviewer`** via a new `PedagogicalMarkerJustification` doc_type. Validation happens at review-cycle time.
- **(D2-C) Both** (defense in depth). Auditor enforces at scan time; reviewer validates at gate time.

**Evidence:** F-009 says shared-document-reviewer extension is clean; F-001/F-004 say `pedagogical_marker_check.py` deduplication makes auditor enforcement natural. T-001 says all 5 ecosystems put enforcement in the linter, not a separate reviewer.

**Recommendation:** (D2-A) primary, with (D2-B) optionally added if per-layer Design wants double-coverage. Pure-(D2-B) is weakest because it depends on review-cycle invocation; a marker file could be checked in without ever passing through review.

### D-3 — Mechanism α minimum justification content rule

**Question:** What makes a justification "non-boilerplate" — what's the rejection rule for low-effort justifications?

**Inputs:**
- T-001: must describe WHY (not WHAT — survives auditor refactoring); must name both pattern-type AND reason
- Intent constraint: "we can not silently fail" — boilerplate IS silent failure

**Options:**
- **(D3-X) Length-based:** justification must be ≥ N characters / ≥ M words. Easy to enforce, gameable.
- **(D3-Y) Banned-words-based:** rejects bare-word justifications ("pedagogical", "example", "documentation"). Easy to enforce, mostly-effective.
- **(D3-Z) Composite rule:** justification must (a) be ≥ 5 words AND (b) NOT consist solely of banned bare-words AND (c) reference either the content type ("credential patterns", "vulnerable URL examples", "intentional anti-pattern") OR the document role ("anti-laundering catalog", "negative-example reference"). Most defensible; per-layer Design picks the exact rubric.

**Recommendation:** (D3-Z). Rubric details land in mechanism-α spec authored under AC-FR-7-a.

### D-4 — FR-4 SA-2 disposition (Plan stage's U-2)

**Question:** Rewrite 29 descriptions vs tighten SA-2 regex?

**Evidence from F-005:** Tested current regex against 10 of 29 flagged descriptions. ZERO matches. Project uses "At the X stage", "during per-layer Design", "One invocation per", "Use at pipeline start" — all clearly delegation triggers, none matching the current 5 patterns.

**Options:**
- **(D4-i) Rewrite 29 descriptions** to use "Use when" / "When [V-ing]" phrasings. Treats symptom; future authors face same trap.
- **(D4-ii) Tighten regex** by adding pattern alternatives covering project conventions: `\bat the \w+ stage\b`, `\bduring \w+\b`, `\bone invocation per\b`, `\buse at\b`, `\bafter \w+\b`, `\bwhen \w+\b` (broader than "when V-ing"). Fixes root cause.
- **(D4-iii) Both** — tighten regex AND audit descriptions for genuine quality issues. Most thorough.

**Evidence weight:** F-005 is strong; the regex is genuinely too narrow. Strong recommendation for (D4-ii) or (D4-iii). Per-layer Design picks; if (D4-iii), the description audit becomes a small task per agent and Acceptance Tests must include negative tests (low-quality descriptions that SHOULD fire SA-2).

### D-5 — FR-5 bypass-approval disposition (per PRD v1.2.0 AC-FR-5-d)

**Question:** Regex fix vs reword vs both?

**Inputs:** PRD v1.2.0 explicitly permits all three; T-001 + intent constraint 3 favor regex fix.

**Recommendation:** Regex fix as primary disposition. Optional reword as secondary (e.g., if a body phrasing also happens to be improvable for readability, fix that too — but not solely to satisfy the auditor). The regex change: add a negation-aware lookbehind so the pattern doesn't fire when preceded within ~6 words by "do NOT", "must NOT", "never", "do not", "MUST NOT", etc.

### D-6 — FR-6 Stream 2 X9 reformulation

**Question:** What exactly does X9 emit after Stream 2 lands?

**Inputs:** F-003 (X9 is a self-documented stub); F-004 (recursive-audit capability already exists in `audit_project.py`).

**Options:**
- **(D6-A) Wire the recursive call**, replace the stub. After Stream 2: X9 emits a MINOR/MAJOR finding ONLY when a preloaded skill actually fails its own audit. The blanket "verify each" message goes away.
- **(D6-B) Reformulate as "skill not recently audited" check** — emit MINOR when the preloaded skill's last audit (cached) is older than N days. Different signal; useful only if audit caching is built (out of scope).
- **(D6-C) Both** — wire the recursive call AND add the cache-staleness check.

**Recommendation:** (D6-A). (D6-B) is its own feature and would expand scope. The X9 reformulation is improvement-not-suppression per intent constraint 3.

### D-7 — FR-12 deduplication architectural shape

**Question:** Where does the canonical `pedagogical_marker_check.py` live?

**Options:**
- **(D7-A) New shared module** at `.claude/skills/auditing-shared/pedagogical_marker_check.py` (new skill module just for shared utilities). Cleanest separation; introduces a new skill.
- **(D7-B) Designate one of the existing 3 as canonical** (e.g., `auditing-cc-configs/scripts/pedagogical_marker_check.py`); replace the other two with thin import shims (e.g., `from auditing_cc_configs.scripts.pedagogical_marker_check import *`). Smallest change; potentially fragile Python-import-path semantics across skill scripts.
- **(D7-C) Move to a top-level shared location** outside any individual skill (e.g., `.claude/lib/`). Cleanest path-wise but breaks the "scripts live with their skill" convention.

**Recommendation:** (D7-A). Aligns with the project's existing pattern (`auditing-skills`, `auditing-subagents`, `auditing-cc-configs` are sibling skill modules); a new sibling `auditing-shared` for utilities is consistent. Per-layer Design confirms.

### D-8 — Categorization-protocol document shape (FR-9)

**Question:** What does the categorization-protocol document look like?

**Inputs:** IN-010 disposition (designer-general-knowledge); T-001 provides anchor examples; this feature's 6-category disposition provides concrete calibration anchors.

**Outline candidate (for per-layer Design to refine):**
1. Decision tree for new findings (markerable vs real-defect; if markerable, which form of marker)
2. Calibration anchors: 6 categories from this feature, with the dispositions chosen
3. Escalation criteria (when to involve the user)
4. Reference to FR-7 (mechanism α) as the controlling constraint on marker dispositions
5. Reference to ADR-0029 (no-silent-scope-changes) — finding categorization itself is a stage decision that can surface deviations

## Cross-cutting design implications

### Single-layer feature (claude-code only) — what design-claude-code receives

Per PRD Layer Scope: only Claude Code / Project Filesystem layer is in scope. `design-claude-code` is the only per-layer designer activated for this feature. It will receive:

- All 7 source documents listed in the source map
- All 8 decisions (D-1 through D-8) framed above
- The "Conventions captured" section from `codebase-analysis-report.md`

### Architectural Q items for design-composer

These will surface in `claude-code-design.md` as `Q-CC-N` items per ADR-0016:

- **Q-CC-1:** Should the new marker-justification spec live in `KB-documentation-criteria/references/` (per convention) or extend the existing spec at `auditing-cc-configs/references/pedagogical-marker-spec.md` (per locality)? Recommendation: KB-documentation-criteria with a forward-pointer added to the existing spec.
- **Q-CC-2:** D-2's option (D2-A vs D2-C) — single enforcement point vs defense-in-depth. Design-composer arbitrates if `design-claude-code` doesn't pick.
- **Q-CC-3:** D-7's option (D7-A vs D7-B vs D7-C) — new shared skill module vs import-shim vs top-level lib. Design-composer arbitrates.
- **Q-CC-4:** Does the categorization-protocol document (D-8) live in `disciplines/` per FR-9-a, or in `references/` directly? Recommendation: `disciplines/` per the project's pattern of one-file-per-discipline.

### Open question for Plan stage (carried forward from PRD)

- **U-4** (PRD Undetermined): Where exactly do FR-6 Stream 1 verification records live? Plausibles:
  - (U4-a) Feature dir: `working/feature/audit-findings-remediation-r1/x9-verification/<agent>-<skill>.md` — visible in this feature's deliverable; doesn't accumulate cross-feature
  - (U4-b) A new top-level `audits/` directory — persists across features; new convention
  - (U4-c) Appended to existing audit handoff documents — least invasive; lowest discoverability

  Recommendation: (U4-a) for this feature; queue ADR for whether a permanent audits/ directory is warranted (out of scope here).

## Surfaced for cross-artifact audit

Items that the Cross-Artifact Audit stage should check, per ADR-0029 (audit stages check upstream artifacts for unsurfaced deviations):

1. **D-5 boundary case:** If per-layer Design chooses "reword only" disposition for AC-FR-5-b without the auditor regex fix, Cross-Artifact Audit should flag — that's the "cosmetic guardrail softening" the synthesis explicitly warns against. Not a hard violation but a soft warning.
2. **FR-7-b uniform enforcement:** After FR-12 deduplication, only ONE `pedagogical_marker_check.py` should remain (canonical) plus thin shims OR an import refactor. If Cross-Artifact Audit finds three independent implementations still exist post-feature, that's a BLOCKER (FR-12 not satisfied → FR-7-b not satisfiable).
3. **No silent boilerplate justifications:** AC-FR-7-d says "every marker added shall pass FR-7's discipline check." Cross-Artifact Audit should sample-check the actual added markers (not just count them) to confirm justifications are substantive per D-3.

## Synthesis completion checklist

- [x] All Discovery outputs fanned in
- [x] 8 design decisions framed (D-1 through D-8) with options + evidence
- [x] Cross-cutting implications for `design-claude-code` documented
- [x] 4 Q-CC-N items pre-staged for `design-composer`
- [x] Plan-stage open question (U-4) carried forward with recommendation
- [x] 3 items flagged for Cross-Artifact Audit per ADR-0029
- [x] No new scope deviations surfaced (SD-001 + SD-002 already resolved upstream)
