# Audit Rubric

The master scoring rules. Read this once at the start of an audit, then keep it open as you work through the dimensions.

## Contents

- The 10 dimensions
- Severity weights
- Verdict thresholds
- How to score a dimension
- Tie-breakers and edge cases

## The 10 dimensions

| # | Dimension | What it measures | Reference file |
|---|---|---|---|
| 1 | Discoverability | Will Claude actually trigger this skill? | descriptions-and-triggering.md |
| 2 | Frontmatter validity | Does the YAML parse and obey field constraints? | frontmatter-spec.md |
| 3 | Token economy | Does every line in SKILL.md earn its recurring token cost? | content-quality.md |
| 4 | Progressive disclosure | Is content split appropriately, references one level deep? | progressive-disclosure.md |
| 5 | Instruction quality | Appropriate freedom level, consistent terms, concrete examples | content-quality.md |
| 6 | Workflow soundness | Multi-step tasks have steps and validators where appropriate | workflows-and-feedback.md |
| 7 | Script hygiene | Scripts handle errors, declare deps, no voodoo constants | scripts-and-code.md |
| 8 | Security posture | No injection patterns, no exfiltration, allowed-tools scoped | security-checklist.md |
| 9 | Anti-pattern absence | Free of the named anti-patterns | anti-patterns.md |
| 10 | Agent-fit | Written for the AI consumer, not as human prose | content-quality.md |

## Severity weights

Each dimension starts at 10 points. Findings deduct:

- **BLOCKER** — −12 per dimension (zeros the dim due to floor at 0) AND −12 flat penalty on total score
- **MAJOR** — −5
- **MINOR** — −2
- **NIT** — −0.5

A dimension cannot go below 0. Total cannot go below 0. Maximum total: 100.

**Calibration:** one BLOCKER drops a perfect 100 to 78 (NEEDS-WORK). Two BLOCKERs drop to 56 (FAIL). Three MAJORs spread across dimensions drop a 100 to 85 (PASS-WITH-MINOR-FIXES). Six MAJORs drop a 100 to 70 (NEEDS-WORK).

## Verdict thresholds (v2)

| Score | Verdict | Meaning |
|---|---|---|
| 95–100 | PASS | Production-ready, share freely |
| 85–94 | PASS-WITH-MINOR-FIXES | Usable; address minor findings when convenient |
| 70–84 | NEEDS-WORK | Significant fixes required before sharing |
| 50–69 | FAIL | Substantial rework needed |
| 0–49 | FAIL | Not usable as-is |
| any | SECURITY-BLOCK | Any confirmed CRITICAL security finding overrides score; do not install |

A single BLOCKER on dimension 2 (frontmatter) usually means the skill won't load at all — note this in the report header even if the score happens to land above 50.

## How to score a dimension

For each dimension:

1. Read the relevant reference file once.
2. Walk through its checks against the audited skill.
3. Record each finding (severity + location + what + fix).
4. **Apply the verification step**: open each cited file and confirm the property the script asserts holds. Drop false positives with a note.
5. **Run pedagogical-marker prefilter** when the skill declares `pedagogical_sections:`. Findings inside marked content get demoted per the spec.
6. **Compute via `scripts/audit_skill.py` + `verdict_compute.py`** rather than by hand — deterministic math avoids drift.

If a finding could fit in two dimensions, file it under the more specific one. Don't double-count. Example: a vague description that also lacks exclusion language belongs to dimension 1, not split between 1 and 9.

## Tie-breakers and edge cases

**Skill is intentionally tiny (one-liner reference content).** Dimensions 4, 6, 7 may be N/A. Score them as 10 (no deduction) and note `N/A` in the report rather than penalizing.

**Skill body is in a non-English language.** Don't penalize. Apply rubric criteria as best you can; flag any that can't be checked without language expertise.

**Skill uses `disable-model-invocation: true`.** Dimension 1 (discoverability) is partially N/A — Claude won't auto-trigger by design. Still check that the description is clear for users browsing `/skills`. Cap deduction at MAJOR.

**Skill is bundled by Anthropic** (e.g. `/simplify`, `/debug`). Audit normally but note the source in the report — Anthropic skills get the same scrutiny as third-party ones.

## What goes in the report header

- Path to audited skill
- Final score
- Verdict
- Critical security flags (if any)
- Date of audit
- Auditor (this skill's version)

The full template is in `assets/audit-report-template.md`.

## Last verified against

- `code.claude.com/docs/en/skills` — fetched 2026-05
- `docs.claude.com/en/docs/agents-and-tools/agent-skills/best-practices` — fetched 2026-05

When the spec changes, update this rubric and bump the date.
