---
name: auditing-codespaces
description: >-
  STUB SKILL — reserved for the future Codespaces audit machinery. Returns
  the canonical `{"stub": true, "findings": []}` payload per AC-FR-8-b +
  Q-CC-4. ALWAYS invoke (or at least register as the audit target) when
  reviewing, auditing, evaluating, scoring, vetting, or critiquing
  `.devcontainer/` configuration; the stub state is what the downstream
  consumer must surface. When real audit logic is authored in a follow-on
  feature, this skill will be populated to match the structure of the
  sibling `auditing-github-actions` skill. Report-only.
allowed-tools: Read, Grep, Glob, Bash(python3 *)
---

# Auditing GitHub Codespaces — STUB

This skill is the audit half of the cc-style three-way split for
GitHub Codespaces, but currently ships in **stub state** per AC-FR-8-b +
Q-CC-4 (Blueprint § Q-CC-N Arbitration).

The sibling skills are:

- `KB-codespaces-platform` — platform knowledge (schema, lifecycle hooks,
  features, prebuilds)
- `KB-codespaces-design` — design discipline (image vs. Dockerfile vs.
  compose; when to prebuild; lifecycle-hook placement)
- `auditing-codespaces` — **this skill, currently a stub** — will host
  the Codespaces audit machinery when authored

## Why a stub

Per Q-CC-4 resolution: no audit scripts currently exist under
`KB-codespaces-platform/scripts/` (the place GitHub-Actions audits lived
before their relocation). Authoring net-new audit machinery for
Codespaces is **NOT in scope** for the `execution-pipeline-design-r1`
feature run that established the three-way-split symmetry. This skill
ships as a stub so that:

1. The structural pattern is symmetric across audit families (cc, gha,
   codespaces) — downstream agents and the
   `run_phase_checks.py` coordinator can dispatch uniformly.
2. The stub-vs-real distinction is **explicit and surfaced** per ADR-0033
   stub-vs-real surfacing. The downstream phase-quality-reviewer treats
   the stub's `{"stub": true, "findings": []}` output as "not measured"
   rather than "measured zero" — this prevents silent false-clean
   reporting.
3. When real audit logic is authored in a follow-on feature, only this
   skill's body and `scripts/audit_codespaces.py` need to be filled in;
   the surrounding integration is already in place.

## Contents

- `SKILL.md` — this file
- `scripts/audit_codespaces.py` — stub implementation (emits
  `{"stub": true, "findings": []}`)

## When to invoke

- The coordinator (`run_phase_checks.py`) invokes this script as part of
  the audit dimension; the stub's canonical output is what surfaces.
- Direct invocation by a sub-agent works too; the output is the same
  regardless of caller.

## Stub contract

The stub MUST emit exactly:

```json
{"stub": true, "findings": []}
```

The `"stub": true` field is the load-bearing signal — downstream
consumers (especially `execute-phase-quality-reviewer`) MUST treat this
as "not measured" rather than "0 findings" per Q-CC-4 + ADR-0033.

## When real audit logic is authored

The follow-on feature run that populates this skill should:

1. Replace the stub script's body with real audit logic.
2. Remove the `"stub": true` field from the output (or set it to `false`).
3. Update this SKILL.md `description:` to match the
   `auditing-github-actions` pattern (drop "STUB SKILL" prefix; describe
   what is actually audited).
4. Add a `references/` directory if curated content (e.g., canonical
   `devcontainer.json` patterns) becomes part of the skill.
5. Bump the audits-dimension `stub_count` semantics in
   `run_phase_checks.py` to no longer treat this skill specially.

## See also

- `auditing-shared` — canonical helpers, finding schema, severity taxonomy
- `auditing-github-actions` — sibling pattern (post-extraction; the
  reference for what this skill becomes when populated)
- `auditing-cc-configs` — sibling pattern (pre-existing reference for
  three-way-split discipline)
- `KB-codespaces-platform` — platform-knowledge half
- `KB-codespaces-design` — design-discipline half
