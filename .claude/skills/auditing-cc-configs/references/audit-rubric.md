# Audit Rubric (shared across the auditing-cc-configs family)

The master scoring rules. Read this once at the start of an audit, then keep it open as you work through the dimensions.

This rubric is shared across all seven skills in the family (auditing-cc-configs, auditing-skills, auditing-context-files, auditing-subagents, auditing-hooks, auditing-settings, auditing-mcp). Each sub-skill defines its own 10 dimensions appropriate to its primitive, but uses these severity weights and verdict thresholds.

## Contents

- The dimension model
- Severity weights (v2 tightened)
- Verdict thresholds (v2 tightened)
- How to score a dimension
- The cross-file overlay
- Tie-breakers and edge cases
- The verification step (non-negotiable)

## The dimension model

Each sub-skill scores its primitive against 10 dimensions. The dimensions vary by primitive (a hook doesn't have a "progressive disclosure" dimension; a CLAUDE.md doesn't have "frontmatter validity") but each one starts the same way:

- Each dimension starts at **10 points**.
- Findings deduct from the dimension's pool.
- The dimension floors at 0.
- The 10 dimension scores sum to **100 maximum** per audit target.

For a project audit (multiple targets across the .claude/ tree), each target gets its own per-target verdict and the project gets an aggregate verdict computed from a weighted average — see the coordinator's project-aggregation rules.

Sub-skills declare their dimensions in their own SKILL.md. For example:

- **auditing-skills**: discoverability, frontmatter validity, token economy, progressive disclosure, instruction quality, workflow soundness, script hygiene, security posture, anti-pattern absence, agent-fit.
- **auditing-context-files**: size/density, @-import integrity, content quality, anti-pattern absence, rules-scope correctness, security (credentials/secrets), staleness, structure, auto-memory hygiene, layering interactions.
- **auditing-subagents**: frontmatter validity, description routing, tool scoping, body quality, memory configuration, safety model adherence, anti-pattern absence, model selection, skills field cost, agent-fit.
- **auditing-hooks**: configuration validity, event-name correctness, script existence and hygiene, security posture, matcher quality, persistence vectors, idempotency, error handling, exit-code protocol adherence, anti-pattern absence.
- **auditing-settings**: schema validity, permission rule syntax, deny-baseline coverage, lockdown knobs, output-style validity, env block safety, file hygiene (gitignore), schema-field recognition, scope-correctness, anti-pattern absence.
- **auditing-mcp**: schema validity, transport security, credential handling, supply-chain hygiene, privilege scoping, toxic-combination absence, anti-pattern absence, typosquat risk, env expansion correctness, server name discipline.

Each sub-skill's own audit-rubric extension defines what each dimension means for that primitive.

## Severity weights (v2)

Findings deduct from the dimension they apply to. **BLOCKER additionally applies a flat penalty to the total score**, on top of zeroing its dimension. This is the mechanism that makes "one BLOCKER" decisively non-PASS, addressing the goal of tighter scoring.

| Severity | Per-dimension deduction | Additional total penalty | Notes |
|---|---|---|---|
| **BLOCKER** | −12 (floors dim at 0) | −12 from total | Confirmed CRITICAL produces SECURITY-BLOCK regardless of score. |
| **MAJOR** | −5 | none | Multiple MAJORs stack in dimension but cannot send it below 0. |
| **MINOR** | −2 | none | Stack normally. |
| **NIT** | −0.5 | none | Stack normally. |

Each dimension cannot go below 0. Total score cannot go below 0.

**Calibration:** one BLOCKER drops a perfect score to 78 (one dim 10→0 = −10, plus −12 total = 78 → NEEDS-WORK). Two BLOCKERs in different dimensions drop to 56 (−20 dims + −24 flat = 56 → FAIL). Three MAJORs in one dimension drop a 100 to 85 (dim 10→0 due to floor — only 10 absorbed, 5 deductions lost; total 90, but stacking across dims: 3 MAJORs in 3 dims = −15 = 85 → PASS-WITH-MINOR-FIXES). Six MAJORs spread across dimensions drop a 100 to 70 (NEEDS-WORK boundary). This is intentionally tight — "ok" doesn't earn PASS.

## Verdict thresholds (v2)

| Score | Verdict | Meaning |
|---|---|---|
| 95–100 | **PASS** | Production-ready, share freely. |
| 85–94 | **PASS-WITH-MINOR-FIXES** | Usable; address minor findings when convenient. |
| 70–84 | **NEEDS-WORK** | Significant fixes required before sharing or relying on. |
| 50–69 | **FAIL** | Substantial rework needed. |
| 0–49 | **FAIL** | Not usable as-is. |
| any | **SECURITY-BLOCK** | Any confirmed CRITICAL finding overrides score; do not install or invoke until reviewed by a human. |

A single BLOCKER on the dimension that determines whether the config loads at all (frontmatter validity for files with frontmatter; JSON parse for JSON files) usually means the primitive won't function — note this in the report header even if the score lands above 50.

## How to score a dimension

For each dimension:

1. Read the relevant reference file once.
2. Walk through its checks against the audited target.
3. Record each finding (severity + location + what + fix).
4. **Run the verification step** (see below) before promoting any script-derived MAJOR or BLOCKER.
5. **Run pedagogical-marker prefilter** on findings that match patterns in declared example content (see `pedagogical-marker-spec.md`).
6. **Run LLM-judge triage** on findings still ≥ MAJOR after prefilter (see `triage-protocol.md`). Judge can demote but cannot zero out CRITICAL.
7. Sum the deductions, subtract from 10, floor at 0.
8. Carry forward to the report.

If a finding could fit in two dimensions, file it under the more specific one. Don't double-count.

## The cross-file overlay

The coordinator runs **24 cross-file pair checks** (X1–X24) after all per-target audits complete. Their findings count toward the project-level verdict but are reported as their own section, not folded into any single target's dimension score.

Cross-file finding severities follow the same weights but the project-level aggregate score takes the **lower** of (a) the weighted average of per-target scores and (b) the score implied by the cross-file findings alone (each at −5 for MAJOR, −12 for BLOCKER, starting from 100). This prevents a clean per-target audit from hiding dangerous cross-file interactions.

## The verification step (non-negotiable)

The deterministic scripts in `scripts/` are pattern-matchers. They give you a *location* and a *hypothesis* — "this looks like a broken reference," "this looks like a credential pattern," "this looks like an oversized file." Before any script finding becomes a MAJOR or BLOCKER in the report, you must verify the property the script asserts actually holds.

**The test:** would a human reviewer, reading the cited file, agree that the property holds *here*?

- Script says "broken reference to `.<dotdir>/settings.json`." Open the file. Is this a bundle reference (broken) or filesystem-path documentation (fine)? If filesystem documentation, drop the finding.
- Script says "credential pattern in security-checklist.md." Open the file. Is this an active config that reads credentials (BLOCKER) or a documentation example of what to look for (pedagogical content; demote per pedagogical-marker rules)? If documentation, follow the pedagogical-marker spec.
- Script says "TOC missing." Open the file. Is there an in-file heading-style index (under "Contents", "Table of contents", "Index", or as a bullet list of cross-references in the first 30 lines)? If yes, drop.

Skipping the verification step produces reports with false-positive MAJOR/BLOCKERs that erode the audit's credibility. Pattern-matchers see *form*; the verification step checks *function*. When they diverge, function wins.

After verification, the LLM-judge triage layer runs on findings that still claim severity ≥ MAJOR. It applies asymmetric rules: CONFIRMED keeps the severity; PEDAGOGICAL demotes to INFO (and adds a "missing marker" finding if no marker was present); AMBIGUOUS demotes one notch and flags for human review. The judge cannot zero out a CRITICAL — maximum demotion for CRITICAL is one notch with mandatory human-review flag.

## Tie-breakers and edge cases

**Target is intentionally minimal (e.g. one-line CLAUDE.md, single-rule rules file).** Several dimensions may be N/A. Score them as 10 (no deduction) and note `N/A` in the report rather than penalizing.

**Target body is in a non-English language.** Don't penalize structural choices that may be language-dependent. Apply rubric criteria as best you can; flag any that can't be checked without language expertise.

**Skill uses `disable-model-invocation: true`.** Dimension related to auto-triggering is partially N/A — Claude won't auto-trigger by design. Still check that the description is clear for users browsing `/skills`. Cap related deductions at MAJOR.

**Target is bundled by Anthropic** (e.g. `/simplify`, `/debug`, official plugin). Audit normally but note the source in the report — Anthropic-bundled targets get the same scrutiny as third-party ones.

**Subagent uses `tools:` field (correct for subagents, wrong for skills).** This is a common carryover bug. When auditing a subagent, `tools:` is the correct field and `allowed-tools:` would be the wrong one — opposite of skills. Don't flag `tools:` as a finding on a subagent.

**Auto memory file `MEMORY.md` is written by Claude itself, not the user.** When auditing it, content-quality findings (aspirational language, no structure) apply differently — Claude's writing style is acceptable as long as the file is concise and the content is genuinely useful. Focus on size limits, credential safety, stale references, and orphan topic files rather than tone.

## What goes in the report header

- Path to audited target (or project root)
- Final score (per-target and project-level if applicable)
- Verdict
- Critical security flags (SECURITY-BLOCK or list of confirmed CRITICALs)
- Date of audit
- Auditor version (this skill's family version)
- Triage summary (counts: confirmed / pedagogical / ambiguous / never-triaged)
- Mode used (default / --managed / --with-runtime)

The full template is in `assets/audit-report-project.md` (for project audits) or `assets/audit-report-single.md` (for single-target audits).

## Last verified against

- `code.claude.com/docs/en/skills` — fetched 2026-05
- `code.claude.com/docs/en/memory` — fetched 2026-05
- `code.claude.com/docs/en/sub-agents` — fetched 2026-05
- `code.claude.com/docs/en/hooks` — fetched 2026-05
- `code.claude.com/docs/en/settings` — fetched 2026-05
- `code.claude.com/docs/en/mcp` — fetched 2026-05
- `docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices` — fetched 2026-05

When the spec changes, update this rubric and bump the date.
