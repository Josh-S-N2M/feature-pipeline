# Golden Corpus Reference Artifacts

> **Purpose:** stored reference for Layer C smoke runs (task-27). Future runs of `/synthesize` against the same 2-document corpus must produce results within ±10% citation count and the same `decision.id` set as these references.

## Corpus

Two documents from `output/`, selected per Design §7.4 corpus-shape requirement (claims partially overlap so Grapher produces non-trivial unifications):

| File | Purpose |
|---|---|
| `output/constraint-aware-synthesis.md` | Synthesis-pipeline design notes |
| `output/ai-research-synthesis-report.md` | Background research summary |

Content hashes are computed by `verification-scripts/smoke-run-diff.sh` at runtime against the actual files in `output/`. If hashes drift (sources are edited), the smoke run produces a "corpus drift" warning rather than tolerance failure.

## Reference artifacts in this directory

- `00-manifest.json` — the manifest as written for the reference run
- `01-claims.json` — the merged claims output (Phase 1-only run; no Phase 2+ artifacts captured because the reference run halts at end of Phase 1 per task-08 protocol)

## Tolerance (per Design §7.2 Layer C / §4.9)

- Citation count within ±10% of reference (`len(claims)` deltas)
- Same set of `source_uri` values
- No schema violations on either side
- Bit-exact match is **explicitly NOT the criterion** — LLM non-determinism makes that infeasible

## Re-establishment

If a substrate change forces a new reference baseline:

1. Run `/synthesize golden-corpus` end-to-end against this corpus.
2. Verify all six §7.4 success criteria.
3. Copy the resulting `00-manifest.json` and `01-claims.json` to this directory, replacing the prior reference.
4. Document the substrate change in a Design Doc revision log entry.
