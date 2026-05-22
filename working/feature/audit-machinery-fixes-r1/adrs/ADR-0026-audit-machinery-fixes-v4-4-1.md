---
id: ADR-0026
title: Audit-machinery fixes — closes ADR-0025 defects 2, 3, 4
status: accepted
date: 2026-05-21
deciders: [user, claude]
supersedes: []
superseded_by: []
related: [ADR-0023, ADR-0025]
---

# ADR-0026: Audit-machinery fixes shipped in v4.4.1

## Context

ADR-0025 captured four pipeline-machinery defects observed during the v4.4.0 (frontend-design-knowledge-r1) execution. This ADR documents the v4.4.1 fixes that close three of them (defects 2, 3, 4); defect 1 (pedagogical-marker backfill in existing platform KBs) carries forward as the recommended v4.5.0 scope.

The fixes are pure machinery — no KB content changes, no agent surface changes, no Blueprint changes. Pipeline structure unchanged. This is the reason for the PATCH version bump (v4.4.0 → v4.4.1), not MINOR.

A bonus finding surfaced during execution: when the BACKTICK_PATH cross-KB fix made cross-KB references resolve correctly, the auditor's depth-2-nesting check began flagging them. The depth-2 check is conceptually scoped to within-skill nesting; cross-KB references are inter-skill navigation. This required a fifth, smaller fix added in the same patch.

## What changed

### Fix 1: DE-2 regex hardened to require path-component context

**File:** `.claude/skills/auditing-skills/scripts/scan_security.py:57-66`

**Before:**

```python
("DE-2", CRITICAL,
 re.compile(r"(?i)(\.aws/credentials|\.ssh/id_(rsa|ed25519|ecdsa)|\.netrc|\.env(?!\w))"),
 "References a credential file (.aws/credentials, .ssh/id_*, .netrc, .env).",
 ...)
```

**After:**

```python
("DE-2", CRITICAL,
 re.compile(
     r"""(?ix)
     (?:^|(?<=[\s/~"'\(\[\\]))
     (\.aws/credentials | \.ssh/id_(?:rsa|ed25519|ecdsa) | \.netrc | \.env)
     (?!\w)
     """,
 ),
 "References a credential file (.aws/credentials, .ssh/id_*, .netrc, .env).",
 ...)
```

**Behavior change.** Matched credential references now require path-component context — preceded by start-of-string, whitespace, `/`, `~`, or quote-like characters (`"`, `'`, `(`, `[`, `\`). The lookahead `(?!\w)` is preserved (rejects `.envFile`, `.environment`, etc.) but the additional `.` exclusion is dropped so legitimate variants like `.env.local` still match.

**Effect.** Eliminates 18 BLOCKER false-positives across the project — instances of `process.env.X`, `inputs.env == ...`, `context.env.X`, etc. that were over-matching the original substring search. Real credential references (e.g., `Read(~/.aws/credentials)`, `cat .env`, `["~/.aws/credentials"]`) continue to match.

**Validation.** A 14-case test (8 true-positive, 6 false-positive) was run against both old and new regex. The old version matched 4 of 6 false positives (`process.env.PORT`, `process.env.NODE_ENV`, `inputs.env == 'prod'`, `context.env.api_key`); the new version matches 0 of 6 while preserving all 8 true positives.

### Fix 2: BACKTICK_PATH cross-KB reference resolution

**File:** `.claude/skills/auditing-skills/scripts/lint_references.py:105-128`

**Behavior change.** When the `normalize()` function encounters a referenced path starting with `KB-`, it now tries to resolve it against the project's skills root (`<skill_dir>.parent`) before falling back to skill_dir-relative or owner-file-relative resolution.

**Effect.** Cross-KB references like `` `KB-storybook-platform/references/story-format.md` `` (in `KB-component-architecture-design/references/patterns.md`) now resolve to `.claude/skills/KB-storybook-platform/references/story-format.md`, where the target actually exists. No more spurious BLOCKER findings for the project's canonical KB-cross-reference convention.

**Effect on v4.4.0 workaround.** The 16 cross-KB references previously rewritten as workaround (`` `KB-X` (specifically references/Y.md) ``) were reverted to the natural form (`` `KB-X/references/Y.md` ``). The auditor now resolves them correctly.

### Fix 3: deductions_by_severity uses final_severity

**File:** `.claude/skills/auditing-cc-configs/scripts/verdict_compute.py:133-145`

**Before:** `deductions_by_severity()` read raw `severity` field, ignoring any `final_severity` set by the pedagogical-marker pre-triage layer. This produced JSON summary counts that diverged from the markdown report's `## Summary` section by the number of findings that were demoted in pre-triage.

**After:** `deductions_by_severity()` reads `final_severity` with `severity` as fallback — the same logic the markdown report uses at line 333.

**Effect.** JSON summary now matches the markdown report's `## Summary`. AC-FR-5-b verification can rely on JSON summary counts; line-text comparison is no longer the only authoritative measure.

### Fix 4 (bonus, discovered during testing): depth-2 nesting check scoped to within-skill

**File:** `.claude/skills/auditing-skills/scripts/lint_references.py:193-209`

**Background.** After fix 2 made cross-KB references resolve, the auditor's depth-2-nesting check (which flags reference files linking to other reference files NOT also linked from SKILL.md) began firing on cross-KB references. This was a false positive — the depth-2 check is conceptually scoped to intra-skill nesting (where partial-read of a deeply-linked file is a concern); inter-skill navigation has different ergonomics.

**Behavior change.** The depth-2 check now checks if the resolved target is within `skill_dir` before flagging. Cross-KB references (resolved outside skill_dir) are skipped.

**Effect.** Eliminates 16 false-positive MAJOR findings introduced by fix 2's resolution. Without this, fix 2 would have traded BLOCKERs for MAJORs at 1:1 ratio.

## Validation: v4.4.0 baseline vs v4.4.1

| Severity | v4.4.0 baseline | v4.4.1 final | Delta |
|---|---|---|---|
| BLOCKER | 95 | **77** | **-18** |
| MAJOR | 71 | **69** | **-2** |
| MINOR | 28 | 28 | 0 |

**Summary alignment.** v4.4.0 JSON summary said BLOCKER 97 / MAJOR 69 (diverging from line count 95 / 71). v4.4.1 JSON summary says BLOCKER 77 / MAJOR 69, matching line count 77 / 69 exactly. **Defect 4 closed.**

**v4.4.0 workarounds reverted.**

- The two `process.env.X` patterns that were rewritten as `process['env']['X']` in v4.4.0 (in KB-design-system-design/references/governance.md and KB-storybook-platform/references/composition.md) are restored to the natural dot-notation form. No DE-2 false-match.
- The 16 cross-KB references that were rewritten from `` `KB-X/references/Y.md` `` to `` `KB-X` (specifically references/Y.md) `` are restored to the natural backticked-full-path form. No BACKTICK_PATH resolution failure.

Both workarounds are gone; the machinery handles the natural authoring patterns.

## What remains open

**Defect 1 from ADR-0025** (pedagogical false-positives in existing platform KBs) is partially mitigated by fix 1 — the DE-2 regex hardening eliminated ~18 of the ~43 security-scanner false positives. The remaining ~25 are real pedagogical content (legitimate mentions of `.env`, `.aws/credentials`, `~/.ssh/id_*` in `KB-cc-platform`, `KB-codespaces-platform`, `KB-github-actions-platform`, etc.) that need the full marker discipline: `pedagogical_sections:` declarations in the relevant SKILL.md frontmatters AND `audit-example` fence wrapping of dangerous-looking code blocks.

Recommended scope for **v4.5.0**: a marker-backfill feature run. Estimated work: 6-10 platform KB files; frontmatter declarations + per-block fence rewrapping. Net effect on baseline: another ~25 BLOCKERs should drop to INFO, leaving a much smaller baseline of genuinely-broken references.

## Consequences

**Carried-forward conventions.**

- New authoring may use `process.env.X` (dot notation) freely in code examples; no workaround needed.
- New authoring may use `` `KB-X/references/Y.md` `` (backticked full path) for cross-KB references; the auditor resolves correctly.
- AC-FR-5-b verification may use the JSON summary's `deductions_by_severity` directly; line-text comparison is no longer required.

**Other:**

- The depth-2-nesting check is now slightly less strict (skips cross-KB targets). Intra-skill depth-2 nesting is still flagged.
- No agent / KB content / Blueprint structure changes were made in v4.4.1. The pipeline's user-facing surface is unchanged.

## Notes

The bonus fix 4 (depth-2 exemption) is exactly the kind of follow-on issue that surfaces only when a fix is exercised end-to-end. It's a small reminder that the auditor's checks interact: tightening one can expose tension in another. Future machinery work should expect similar small follow-ons.

Defect 1 was always the largest scope of ADR-0025; the v4.5.0 deferral is deliberate rather than oversight. Backfilling markers in existing KBs requires reading each file's content carefully and choosing wrap boundaries — work that doesn't compress well.
