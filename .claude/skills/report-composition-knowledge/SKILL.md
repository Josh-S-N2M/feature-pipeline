---
name: report-composition-knowledge
description: Knowledge skill loaded by synth-synthesizer. Carries the report skeleton, citation format, ADR template (MADR), tone calibration by audience_depth, and section-streaming guidance.
user-invocable: false
---

# Report Composition Knowledge

Loaded by `synth-synthesizer` via `skills: [report-composition-knowledge]`. Provides templates and rubrics for the final report, citation registry, ADR rendering, and tone calibration.

## Report skeleton

The final `output/synthesis-<topic>/report.md` follows this six-section structure, in order:

1. **Executive Summary** — 2–4 paragraphs. The headline conclusions and the strongest decisions. Tone calibrated to `audience_depth` (see below).
2. **Findings** — claim clusters organized by the entity-graph clusters. Each finding cites supporting claims.
3. **Decisions** — for each decision frame, a short prose framing + the recommended option. ADR-class decisions link to their ADR file.
4. **Constraints Honored** — explicit section listing every `manifest.constraints.hard_constraints[]` entry and how the recommendations honor it. Required even if the constraint is `[]`.
5. **Limitations** — every claim with `verdict == "unverifiable"`, every decision with `recommended_option: null`, every dissent_evidence pair (transparently surfaced as ongoing disagreement).
6. **Sources** — the manifest's `inputs.confirmed[]` list with one-line summaries.

## Citation format

Every assertion in the report ends in `[<source-name>](<source_uri>)`. The link's URI is the `claim.source_uri` from `01-claims.json`. The display name is the source's filename (e.g., `[ai-research-synthesis-report.md](output/ai-research-synthesis-report.md)`).

**Three rendered examples:**

1. The synthesis pipeline operates entirely on Claude Code primitives without external orchestration frameworks (citation: constraint-aware-synthesis.md, in pipeline output).
2. Citation invariant enforcement runs as an in-skill validator with a hook fallback for the production tenant (citation: ai-research-synthesis-report.md, in pipeline output).
3. The substrate registry is reviewed every 90 days to prevent staleness the substrate registry maintained by the synthesize skill (under `../synthesize/references/`).

**Anti-patterns:**
- Citation without `source_uri` (just a name) — reject in citation-presence validator.
- Citation pointing to a `source_uri` not in `manifest.inputs.confirmed` — reject (recursion-safety bleed-through).
- Multiple consecutive citations for one assertion (`[a](u1)[b](u2)`) — collapse to a single citation per assertion; if multiple sources support, list them in `citations.md` registry.

## ADR template (MADR-shaped, per Design §9 Q5)

Per-decision ADRs at `output/synthesis-<topic>/adrs/ADR-NNN-<slug>.md`:

```markdown
# ADR-NNN: <Title>

**Status:** Proposed | Accepted | Deprecated | Superseded by ADR-XXX
**Date:** YYYY-MM-DD
**Deciders:** <synthesis-pipeline run-id>

## Context

<Why this decision needs to be made now. Cites claim cluster.>

## Decision Drivers

<Bulleted list of what's important for this decision. RICE-shaped if architectural.>

## Considered Options

- **Option 1: Native** — <description from substrate-mapping>
- **Option 2: Adapter** — <description>
- **Option 3: Substrate change** — <description or "n/a">

## Decision Outcome

Chosen option: **<recommended_option>**, because <rationale from substrate-mapping>.

### Positive Consequences

<from option's benefits>

### Negative Consequences

<from option's loss_summary + cost>

## Validation

<How would we know this decision is wrong? What feedback signal triggers revisit?>

## Provenance

- Decision frame: D-NNNN (in 04-decision-frames.json)
- Claims supporting: C-NNNN, C-NNNN, ...
- Substrate registry version: <registry_version from 05-substrate-map.json>
- Synthesis run: <run-id>
```

`registry_version` in the provenance footer is critical — when the registry is updated, ADRs that referenced an old version can be flagged for review.

## Tone calibration by audience_depth

`manifest.constraints.audience_depth` ∈ {`executive`, `engineering`, `mixed`}. Tone affects Executive Summary, Findings prose framing, and Decision rationale wording — *not* the data sections (Citations, Sources, Limitations always render the same).

| Audience | Lead with | Word choice | Quantification |
|---|---|---|---|
| `executive` | The decision and its blast radius | Plain English; avoid jargon; spell out acronyms | Round numbers; ranges over precision |
| `engineering` | The technical mechanism | Domain vocabulary; assume familiarity with patterns | Precise numbers; preserve units |
| `mixed` | The decision *and* mechanism in one paragraph | Domain vocabulary with brief glosses | Precise where it matters; rounded where it doesn't |

**Three opening-paragraph examples (same Findings section, three tones):**

- *executive:* "Our synthesis identifies six architectural decisions central to the proposed system. Three are reversible (low risk to try); three are one-way doors that warrant careful review before commitment."
- *engineering:* "Six architectural decisions emerged from the claim corpus, partitioned by Bezos reversibility. Two-way: caching layer, retry budget, log aggregation. One-way: identity provider, data-residency boundary, observability vendor."
- *mixed:* "Six architectural decisions surfaced — three reversible (caching, retry budget, log aggregation) and three one-way doors (identity provider, data residency, observability vendor) that warrant heightened review."

## Section-streaming protocol

Per Design §4.11. The Synthesizer emits one section at a time, appending to `06-synthesis-draft.md` (working) and then to the final `output/synthesis-<topic>/report.md` after validators pass:

```
for section in [executive_summary, findings, decisions, constraints_honored, limitations, sources]:
    compose section using only the upstream-artifact slice relevant to that section
    append to 06-synthesis-draft.md
    free section-specific data from context (release the slice)
```

The agent's context never contains the entire report at once. This is what allows the Synthesizer to handle large corpora without saturation.

## Layer B validators (run before final write)

These are documented in the synth-synthesizer agent body but inherit from this skill's discipline:

- **Citation-presence (B-cite):** every assertion in the draft ends in `[name](uri)` resolving to a `claim.source_uri` in `01-claims.json`.
- **Constraint-propagation (B-constr):** every `decision.recommended_option` either honors `manifest.constraints.hard_constraints` or is surfaced in "Constraints Honored" with explicit acknowledgment of the conflict.

On validator failure: re-emit the violating section. After 2 reruns: `AskUserQuestion`.

## Per-decision ADR rendering (mode: render-adr)

When invoked with `mode: "render-adr"` (per Design §4.11 parallel ADR rendering), the Synthesizer reads only:
- The decision frame slice for `decision_id`.
- The substrate mapping slice for that `decision_id`.
- The cited claims (`decision.claim_cluster_ids`).

Renders one ADR file. Does NOT have access to the full corpus — context isolation per decision keeps token budgets bounded.

## See also

- `references/examples.md` — 3–5 sample report sections rendered for each tone
- `references/anti-patterns.md` — common Synthesizer mistakes (uncited assertion; mixed tones; missing Limitations)
