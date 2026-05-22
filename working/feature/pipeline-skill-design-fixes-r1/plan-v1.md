---
feature_slug: pipeline-skill-design-fixes-r1
version: 1.0.0
status: approved
derived_from: working/feature/pipeline-skill-design-fixes-r1/blueprint-v1.md
approved_at: 2026-05-21T05:20:00Z
gate_passed: 4
---

# Plan — pipeline-skill-design-fixes-r1

## Tasks in execution order

| ID | Task | Deliverable | AC |
|---|---|---|---|
| T-1 | Author `deliverable-archive-spec.md` reference file | new file | AC-8, AC-9 |
| T-2 | Author `finalize-deliverable-packager.md` sub-agent | new file | AC-3, AC-4 |
| T-3 | Edit `recipe-feature-pipeline/SKILL.md`: add precondition section | edit | AC-1, AC-2 |
| T-4 | Edit `recipe-feature-pipeline/SKILL.md`: add Stage 13 to sequence | edit | AC-5 |
| T-5 | Edit `shared-document-reviewer.md`: add `DeliverableArchive` doc_type + procedure | edit | AC-6, AC-7 |
| T-6 | Retroactive validation: run validator against v4.4.2 archives | (manual exercise) | AC-10, AC-11 |
| T-7 | Author ADR-0028 closing ADR-0027 | new file | AC-12 |
| T-8 | Author HANDOFF-v4.5.0.md + CONTINUE_PROMPT-v4.5.0.md | new files | — |
| T-9 | Run cc-audit; verify no NEW BLOCKERs vs v4.4.2 baseline | (verification) | — |
| T-10 | Package v4.5.0 zip; present to user | deliverable | — |

## Dependencies

```
T-1 (spec) → T-2 (packager reads spec) → T-5 (reviewer reads spec)
T-1 → T-3, T-4 (orchestrator references packager + spec)
T-2, T-5 → T-6 (validator runs)
T-6 → T-7 (ADR documents validation evidence)
T-7 → T-8 (handoff references ADR)
T-8 → T-9 → T-10
```

Critical path: T-1 → T-2 → T-5 → T-6 → T-7 → T-8 → T-9 → T-10. No parallelism opportunity at this scope (each task is small and the dependencies are linear).

## Validation gates

See `phase-validators.md`.
