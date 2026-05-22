# Continuation prompt — feature-pipeline v4.5.0

You are resuming a multi-session project for `feature-pipeline`. The current canonical artifact is **v4.5.0**.

## State summary

v4.5.0 is a MINOR bump over v4.4.2. Three skill-design fixes (closes ADR-0027) plus one auditor parser fix (addendum to ADR-0028) plus the resulting baseline reduction.

| What changed | Closes |
|---|---|
| `cwd == repo-root` precondition added to recipe-feature-pipeline | ADR-0027 Issue 1 |
| `finalize-deliverable-packager` new agent at Stage 13 | ADR-0027 Issue 2 |
| `shared-document-reviewer` extended with `DeliverableArchive` doc_type | ADR-0027 Issue 3 |
| `parse_tools_from_frontmatter` handles YAML flow-sequence (`[A, B]`) | (bonus during closeout) |

**Baseline reduction:** BLOCKER 77 → 77 (no change); MAJOR 70 → **42 (-28)**; MINOR 29 → 29.

The MAJOR drop came entirely from the auditor parser fix — 28 latent false positives cleared across the 27 existing agents.

## ⚠️ What's still open

- **ADR-0025 defect 1** (pedagogical-marker backfill) — ~25 BLOCKERs remain attributable. v4.5.1 or v4.6.0 scope.
- **One pre-existing genuine MAJOR** in `review-cross-artifact-auditor.md` (Bash body-reference without declaration). ~5 min fix; absorb into any later run.
- **Stage 13 retroactive run** against v4.4.0/v4.4.1/v4.4.2 archives — optional one-off discipline-validation pass before next feature.

## What's next — three threads, revised priority

**Thread 1: Formalized execution pipeline** (user's originally-stated priority). **Now unblocked** — ADR-0027 is closed; Stage 13 ensures planning artifacts land in canonical location automatically.

**Thread 2: v4.5.1 / v4.6.0 marker backfill.** Address ADR-0025 defect 1.

**Thread 3: Small cleanups.** `review-cross-artifact-auditor.md` Bash fix; Stage 13 retroactive pass against older archives.

**Recommended ordering:** Thread 1 first. The reason ADR-0027 was prioritized over Thread 1 was that Thread 1 would have inherited and compounded the gap. That gap is now closed.

## Files to read first

1. `handoff/HANDOFF-v4.5.0.md` — this version's handoff
2. `adrs/ADR-0028-skill-design-fixes-v4-5-0.md` — what changed and why (includes parser-fix addendum)
3. `.claude/skills/KB-documentation-criteria/references/deliverable-archive-spec.md` — the new spec defining expected artifact sets per scope class
4. `.claude/agents/finalize-deliverable-packager.md` — the new Stage 13 agent

## Discipline reminders

- Per **ADR-0005**: never edit prior versions in place; reconcile via a new version.
- Per **ADR-0023**: PATCH-scope features may skip stages; the deliverable-archive spec formalizes which stages are conditional.
- Per **ADR-0027** (now closed by ADR-0028): planning artifacts MUST land at `working/feature/<slug>/` in the repo. Orchestrator now enforces this via Stage 1 precondition; Stage 13 validates it.
- Per the parser-fix addendum: agent `tools:` may use either comma-separated or YAML flow-sequence syntax; both parse correctly. Comma-separated remains the project convention.
