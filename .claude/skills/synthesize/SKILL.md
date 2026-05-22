---
name: synthesize
description: Six-phase research-synthesis pipeline orchestrator. Discovers prior research reports under output/, runs a Confirmation Gate, then drives Extractor → Grapher → Critic → Framer → Substrate → Synthesizer as isolated sub-agent invocations communicating via JSON artifacts in working/synthesis/{run-id}/. Produces output/synthesis-{topic}/report.md plus per-decision ADRs. NOT for code review, single-document summarization, or meeting-notes summary — this is multi-source research synthesis with claim extraction, critique, decision frames, and ADR output.
user-invocable: true
pedagogical_sections:
  - path: references/task-08-replication-corpus/README.md
    justification: "Replication-corpus README documenting a real task-08 run; contains SHA-256 file fingerprints (64-char hex strings) that the auditor's OB-1 base64 detector matches against. The hashes are cryptographic provenance for the corpus files cited in the replication record, not encoded payloads."
---

# Synthesize Orchestrator

## Execution Contract

**Inputs accepted from caller:**
- `<topic>` (positional, required) — slug for the synthesis run
- `--resume <run-id>` (alternative, mutually exclusive with `<topic>`) — resume a previously-checkpointed run

**Outputs produced:**
- `output/synthesis-<topic>/report.md` — final synthesis report with citations
- `output/synthesis-<topic>/citations.md` — `claim_id → source_uri` registry
- `output/synthesis-<topic>/substrate-options.md` — appendix of native/adapter/substrate-change options per decision
- `output/synthesis-<topic>/adrs/ADR-NNN-<slug>.md` — one MADR-shaped ADR per architectural decision (when `params.include_adrs == true`)
- `working/synthesis/<run-id>/00-manifest.json` through `05-substrate-map.json` — phase artifacts (also `06-synthesis-draft.md`)
- `working/synthesis/<run-id>/checkpoint.json` — resume state

**Hard exclusions** (enforced unconditionally, reject the run if violated):
1. **No claim without `source_uri`.** Every claim emitted by Extractor must point to a path in `manifest.inputs.confirmed`.
2. **No architectural recommendation without three options enumerated.** Every decision in `04-decision-frames.json` must have a corresponding entry in `05-substrate-map.json` with all three options (`native`, `adapter`, `substrate_change`) populated — even when one or more is `"n/a"`.
3. **No recursion into `output/synthesis-*/`.** The discovery glob excludes this prefix; the recursion-safety validator rechecks before any source is sent to Extractor.

## Schemas

Phase artifacts conform to schemas under `references/schemas/`:

- `00-manifest.json` ↔ [`manifest.schema.json`](references/schemas/manifest.schema.json)
- `01-claims.json` ↔ [`claim.schema.json`](references/schemas/claim.schema.json) (validates each item in `claims` array)
- `02-graph.json` ↔ [`entity-graph.schema.json`](references/schemas/entity-graph.schema.json)
- `03-critique.json` ↔ [`critique.schema.json`](references/schemas/critique.schema.json)
- `04-decision-frames.json` ↔ [`decision-frame.schema.json`](references/schemas/decision-frame.schema.json)
- `05-substrate-map.json` ↔ [`substrate-mapping.schema.json`](references/schemas/substrate-mapping.schema.json)

Validation contract: see [`references/validators/json-schema-validator.md`](references/validators/json-schema-validator.md).

Worked accept/reject examples for the most-edited schemas: see [`references/schemas/examples/`](references/schemas/examples/) (`claim-valid.json`, `claim-invalid.json`, `manifest-valid.json`, `manifest-invalid.json`). Read these when authoring or debugging a phase artifact — the invalid examples show exactly which fields the Layer A validator rejects and why.

## Phase Invocation Table

| Phase | Sub-agent | Reads | Writes | Schema gate | Layer B gate |
|---|---|---|---|---|---|
| 1 — Extract | `synth-extractor` (per-source map, then deterministic merge) | manifest.inputs.confirmed | `working/synthesis/<run-id>/per-source/01-claims-<slug>.json` then merged `01-claims.json` | claim.schema.json | recursion-safety (orchestrator pre-input-scan + Extractor secondary check) |
| 2 — Graph | `synth-grapher` | `00-manifest.json`, `01-claims.json` | `02-graph.json` + `02-graph-summary.md` | entity-graph.schema.json | — |
| 3 — Critique | `synth-critic` (batched ~20 claims/invocation) | `00-manifest.json`, `02-graph.json`, source files (Grep selective) | `03-critique.json` + `03-verifications.md` | critique.schema.json | — |
| 4 — Frame | `synth-framer` | `00-manifest.json`, `02-graph.json`, `03-critique.json` | `04-decision-frames.json` | decision-frame.schema.json | invariant 5: exclude `unverifiable` claims unless dissent_evidence populated |
| 5 — Substrate | `synth-substrate` | `00-manifest.json`, `04-decision-frames.json`, substrate-registry-<target>.md | `05-substrate-map.json` | substrate-mapping.schema.json | three-option enumeration (B-3opt); registry staleness gate |
| 6 — Synthesize | `synth-synthesizer` (section-streamed, then per-decision ADR mode) | all upstream artifacts | `06-synthesis-draft.md` → `output/synthesis-<topic>/{report.md, citations.md, substrate-options.md, adrs/}` | — | citation invariant (B-cite); constraint propagation (B-constr) |

## Step-by-step Orchestration

### Step 1 — Run-id allocation

Compute `run_id = <slug(topic)>-<UTC YYYYMMDD-HHMMSS>` deterministically. No LLM. Slug rule: lowercase ASCII, words joined by `-`, max 32 chars.

### Step 2 — Discovery

Glob: `output/**/*.md` with `output/synthesis-*/**` excluded. **Recursion-safety validator (Layer B):** the exclusion is applied before any path is added to `discovered`. If the exclusion fails for any reason, abort with explicit error — do not "best-effort" past this gate.

If `manifest.inputs.added_from_input` is non-empty (only after Confirmation Gate has run with `Other` answers), perform secondary scan of `input/**/*` for the user-specified files only. Do NOT default-include all of `input/`.

### Step 3 — Confirmation Gate (mandatory)

Required `AskUserQuestion` with three concurrent questions:

1. **Input set** — single-select: `Use all detected files`, `Exclude some`, `Add files from input/`, `Other (specify)`.
2. **Target substrate** — single-select: `Claude Code`, `Microsoft Azure`, `M365`, `Multi-substrate`, `Other (specify)`.
3. **Hard constraints** — multi-select with `Other` free-text: `None`, `Compliance-bound (e.g., SOC2, HIPAA)`, `Vendor-locked`, `Budget: no net-new services`, `Other`.

**Cancellation handling:** If the user dismisses the card (all answers empty), acknowledge and exit cleanly. Do NOT allocate working directory or run-id.

### Step 4 — Manifest write

Construct manifest object from gate answers per `manifest.schema.json`. Write to `working/synthesis/<run-id>/00-manifest.json`. Run Layer A validator (`json-schema-validator`); on failure, retry once with schema in prompt; on second failure, `AskUserQuestion`.

**Manifest is read-only thereafter** (invariant 3 of Design §7.1). No code path below this step writes to `00-manifest.json`.

### Step 5 — Substrate registry load

Read `references/substrate-registry.md` (single-substrate) or `references/substrate-registry-<target>.md` (when `manifest.constraints.target_substrate != "claude_code"`). Verify `version:` header is no more than 90 days older than `manifest.started_at` (registry staleness gate). On staleness, `AskUserQuestion` to refresh; do not proceed.

### Step 6 — Checkpoint write

Write initial `working/synthesis/<run-id>/checkpoint.json`:
```json
{
  "run_id": "<run-id>",
  "topic": "<topic>",
  "started_at": "<ISO 8601>",
  "last_completed_phase": null,
  "next_phase": "extractor",
  "phase_artifacts": {},
  "retries": { "extractor": 0, "framer": 0 },
  "params": { "max_iterations": 2, "include_adrs": true }
}
```

After each phase, update `last_completed_phase`, `next_phase`, `phase_artifacts.<phase>`. Atomic write (write to `.tmp`, rename).

### Step 7 — Phase invocation

For each phase, in order:

#### Extractor (per-source map step)

```
for source in manifest.inputs.confirmed:
    # >20K-token pre-split (deterministic word-count check; no LLM)
    if file_word_count(source) > 20000:
        split source into per-source/raw-splits/<slug>/<n>.md
        for each split: invoke Extractor on the split
    else:
        Task(
          subagent_type='synth-extractor',
          description=f'Extract claims from {source}',
          prompt={
            source_path: source,
            schema_ref: 'references/schemas/claim.schema.json',
            output_path: 'working/synthesis/<run-id>/per-source/01-claims-<slug>.json'
          }
        )
    Layer A validator on the per-source output. On failure: retry once with schema; second failure → AskUserQuestion.

# Deterministic merge (no LLM)
merge all per-source/01-claims-*.json into working/synthesis/<run-id>/01-claims.json
renumber claim ids if necessary to maintain global C-NNNN uniqueness
Layer A validator on merged file.
Update checkpoint.last_completed_phase = 'extractor'.
```

#### Grapher

```
Task(synth-grapher, prompt={
  manifest_path: '00-manifest.json',
  claims_path: '01-claims.json',
  output_path: '02-graph.json',
  summary_path: '02-graph-summary.md'
})
Layer A validator on 02-graph.json.
Update checkpoint.
```

#### Critic (batched)

```
claims = read 01-claims.json
batch_size = 20
critique_batches = []
for i in range(0, len(claims), batch_size):
    batch = claims[i:i+batch_size]
    Task(synth-critic, prompt={
      manifest_path: '00-manifest.json',
      graph_path: '02-graph.json',
      claim_batch: batch,
      output_path: f'working/synthesis/<run-id>/per-batch/03-critique-batch-{i//batch_size}.json'
    })
critique_batches = read all per-batch files
merge into 03-critique.json (deterministic)
Layer A validator.

# Bounded retry decision (Critic-driven Extractor retry, task-13)
unverifiable_count = sum(1 for c in critiques if c.verdict == 'unverifiable' and not c.dissent_evidence)
if unverifiable_count / len(critiques) > 0.4 and checkpoint.retries.extractor < params.max_iterations:
    # Triggered by: widespread unverifiable claims that aren't dissent-marked
    checkpoint.retries.extractor += 1
    re-run Extractor with critic feedback in prompt
    re-run Critic on new claims
    # max_iterations cap is hard; do NOT loop after second failure — Synthesizer surfaces in Limitations
Update checkpoint.
```

#### Framer

```
Task(synth-framer, prompt={
  manifest_path: '00-manifest.json',
  graph_path: '02-graph.json',
  critique_path: '03-critique.json',
  output_path: '04-decision-frames.json'
})
Layer A validator.
Update checkpoint.
```

#### Substrate

```
Task(synth-substrate, prompt={
  manifest_path: '00-manifest.json',
  decision_frames_path: '04-decision-frames.json',
  registry_path: 'references/substrate-registry-<target>.md',  # selected per Step 5
  output_path: '05-substrate-map.json'
})
Layer A validator.
Layer B three-option enumeration check (B-3opt): every decision_id has all three option keys non-null.

# Bounded retry decision (Substrate-driven Framer retry, task-21)
ungrounded = sum(1 for d in decisions if d.recommended_option is None)
if ungrounded / len(decisions) > 0.3 and checkpoint.retries.framer < params.max_iterations:
    checkpoint.retries.framer += 1
    re-run Framer with substrate feedback in prompt
    re-run Substrate
Update checkpoint.
```

#### Synthesizer (section-streamed)

```
# Main report
Task(synth-synthesizer, prompt={
  mode: 'compose-report',
  manifest_path: '00-manifest.json',
  artifacts: ['01-claims.json', '02-graph.json', '04-decision-frames.json', '05-substrate-map.json'],
  draft_path: '06-synthesis-draft.md',
  final_path: 'output/synthesis-<topic>/report.md',
  ancillary: {
    citations_path: 'output/synthesis-<topic>/citations.md',
    substrate_options_path: 'output/synthesis-<topic>/substrate-options.md'
  }
})
# Synthesizer runs B-cite + B-constr validators in-skill before final write.
# On validator failure: re-emit violating section; after 2 reruns AskUserQuestion.

# Per-decision ADRs (conditional on params.include_adrs)
if params.include_adrs:
    for decision in decisions:
        Task(synth-synthesizer, prompt={
          mode: 'render-adr',
          decision_id: decision.id,
          decision_frame: <slice of 04>,
          substrate_mapping: <slice of 05>,
          output_path: 'output/synthesis-<topic>/adrs/ADR-<NNN>-<slug>.md'
        })
        # Each ADR invocation is fresh isolated context per Design §4.11

Update checkpoint.last_completed_phase = 'synthesizer'.
Update checkpoint.next_phase = null.
Emit completion notice via the Stop hook (configured in `hooks.json`) which appends `- <run-id> — completion notice <ISO-8601>` to `working/synthesis/run-index.md`.
```

### Step 8 — Resume handling (`--resume <run-id>`)

When invoked with `--resume`:

1. Read `working/synthesis/<run-id>/checkpoint.json`. If file missing, error: "no run with id `<run-id>`".
2. If `last_completed_phase == "synthesizer"`, output the completion notice from Design §7.1 invariant 6 (resume after completion) and exit. Do NOT re-run.
3. Otherwise, skip discovery + Confirmation Gate (manifest is read-only and remains canonical) + registry load (re-load to confirm staleness gate hasn't tripped since the prior partial run).
4. Resume from `next_phase`. Counters in `retries.*` are preserved (a partial run does not reset retry budgets).

### Step 9 — Error handling per phase

Per Design §4.2 step 8 + §8 failure modes:

- **Schema-violation** (Layer A failure): retry once with schema in prompt → AskUserQuestion on second failure.
- **Critic finds widespread unverifiable**: bounded retry (one Extractor re-run); on second failure, continue to Synthesizer which surfaces in Limitations section.
- **Substrate cannot map**: bounded retry (one Framer re-run); on second failure, continue with `recommended_option: null` decisions which Synthesizer surfaces in Limitations.
- **Single source >20K tokens**: pre-split before Extractor invocation (Step 7).
- **Synthesizer Limitations section**: lists every claim with `verdict == 'unverifiable'` and any decision with `recommended_option == null` — these are the documented gaps the report transparently surfaces.

## Runtime invariant scripts

The seven §7.1 invariants plus the Layer C smoke-run check have shippable Bash verifiers under [`references/verification-scripts/`](references/verification-scripts/). Run after a completed pipeline run as a final acceptance gate:

```bash
RUN_DIR=working/synthesis/<run-id>
OUT_DIR=output/synthesis-<topic>
bash references/verification-scripts/invariant-1-citation.sh         "$RUN_DIR" "$OUT_DIR"
bash references/verification-scripts/invariant-2-three-options.sh    "$RUN_DIR"
bash references/verification-scripts/invariant-3-manifest-readonly.sh "$RUN_DIR"
bash references/verification-scripts/invariant-4-constraint.sh        "$RUN_DIR" "$OUT_DIR"
bash references/verification-scripts/invariant-5-critic-integrity.sh  "$RUN_DIR" "$OUT_DIR"
bash references/verification-scripts/invariant-6-resume.sh            "$RUN_DIR"
bash references/verification-scripts/invariant-7-recursion.sh         "$RUN_DIR"
```

Each script exits 0 on pass and non-zero on fail with a single-line FAIL message naming the violated invariant. The orchestrator should invoke these at the end of Step 7 (Synthesizer) before declaring the run complete; they are the executable form of the §7.1 invariant battery referenced throughout this SKILL.md.

For Layer C (cross-run regression):

```bash
bash references/verification-scripts/smoke-run-diff.sh "$RUN_DIR"
```

Compares a fresh `01-claims.json` against the bundled `references/golden-corpus/01-claims.json` with ±10% citation-count tolerance and same-set source-URI requirement. Use after substantive changes to the Extractor prompt or the claim schema.

## Validation evidence

Two real-corpus replication runs ship with the skill as evidence the pipeline holds end-to-end on real input. When reasoning about whether a planned change preserves the design's invariants, read the README at references/golden-corpus/ and the README at references/task-08-replication-corpus/.

The golden-corpus directory is the small reference corpus used by the Layer C smoke-run-diff check — its 01-claims.json is the ground-truth output that fresh runs are diffed against (±10% citation count tolerance, same source-URI set, no schema violations).

The task-08-replication-corpus directory is a full Phase 1 → Phase 6 replication on a real 2-document corpus from 2026-05-01. It captures every phase artifact (00-manifest through 05-substrate-map JSON files plus the graph summary), the final-output directory containing the synthesis report, citations registry, substrate-options appendix, and all five MADR-shaped ADRs, plus the per-invariant pass/partial verdicts.

Both corpora are read-only references — do not write to them from a normal pipeline run.

## Memory

Persistent observations across runs use Claude Code's built-in memory features rather than custom paths:

- **Per-sub-agent memory** is configured via `memory: project` on each `synth-*` agent's frontmatter. Claude Code maintains `.claude/agent-memory/<agent-name>/MEMORY.md` automatically; the agent reads and appends to its own memory autonomously. See each agent's "Memory discipline" section for what's worth recording.
- **Cross-run main-agent observations** (conventions surfaced by user feedback, vocabulary norms) ride on Claude Code's auto-memory at `~/.claude/projects/<project>/memory/`.
- **Prior-runs index** (informational, append-only) — the Stop hook in hooks.json maintains a run-index file under the working/synthesis directory at runtime (not present in source). Format: one line per completed run, `- <run-id> — completion notice <ISO-8601>`.

This skill does not require or maintain any custom `.memories/` directory; that mechanism has been replaced by the platform features above.

## Hard exclusions (re-stated for emphasis)

- No claim without `source_uri` resolving to `manifest.inputs.confirmed`.
- No architectural recommendation without three options enumerated.
- No recursion into `output/synthesis-*/`.

If any agent attempts to bypass these, halt the run with explicit error.
