# Report Composition Anti-patterns

## 1. Uncited assertions

"OAuth 2.0 is the dominant standard for service-to-service auth." — no citation.

**Discipline:** every assertion ends with `[name](source_uri)`. B-cite validator catches this.

## 2. Mixed tones across sections

Executive Summary in `engineering` voice, Findings in `executive` voice.

**Discipline:** tone is set once at top of report from `manifest.constraints.audience_depth`; consistent throughout prose sections.

## 3. Missing Limitations section when unverifiable claims exist

Critic produced 4 unverifiable verdicts; report has no Limitations section.

**Discipline:** Limitations is mandatory whenever ANY claim has `verdict: unverifiable` (without dissent_evidence) OR any decision has `recommended_option: null`. If neither is true, Limitations section reads "No unverifiable claims; all decisions have recommended options."

## 4. Constraints Honored omitted when constraints empty

`manifest.constraints.hard_constraints: []`; you skip the Constraints Honored section.

**Discipline:** section is mandatory regardless. Empty case: "No hard constraints declared by run manifest."

## 5. Multiple consecutive citations for one assertion


```text
"OAuth 2.0 is the standard [a](u1)[b](u2)[c](u3)."
```

(Anti-pattern: multiple consecutive citations for one assertion.)

**Discipline:** one citation per assertion. If multiple sources support, list them all in `citations.md` registry; report uses the most authoritative single citation.

## 6. ADR provenance footer missing registry_version

ADR doesn't record which substrate-registry version informed the decision.

**Discipline:** every ADR provenance footer includes `Substrate registry version: <X>`. When the registry updates, ADRs referencing the old version can be flagged for review.

## 7. Streaming violation: composing whole report before write

Drafting all six sections in context, then writing in one shot.

**Discipline:** section-by-section streaming. Append each section to `06-synthesis-draft.md`, free section data, move on. Especially critical at scale.
