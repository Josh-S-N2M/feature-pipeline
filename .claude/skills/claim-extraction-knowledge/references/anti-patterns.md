# Claim Extraction Anti-patterns

## 1. Compound claims

`{"text": "Service X has 99.99% uptime, supports OAuth 2.0, and runs in 14 regions."}` — three claims masquerading as one.

**Discipline:** one assertion per claim. Split on commas, "and", "while", "with".

## 2. Citation drop

Empty `source_uri`, or set to a generic value like "internal".

**Discipline:** every claim has a real `source_uri` pointing to a manifest-confirmed file.

## 3. Inference beyond source

Source: "Service X averages 50ms latency in our benchmark"; you write "Service X is the fastest service in its category."

**Discipline:** verbatim or close-paraphrase only.

## 4. Marketing rhetoric

"Service X is industry-leading and best-in-class." Non-assertion; no verifiable content.

**Discipline:** drop marketing flourishes.

## 5. Provenance/type confusion

Tagging a regulator-commissioned vendor whitepaper as `source_provenance: vendor` instead of `regulator`.

**Discipline:** `source_type` = document genre; `source_provenance` = authorship context.

## 6. Pronoun resolution failure

"It supports OAuth 2.0." — claim is ambiguous in isolation.

**Discipline:** resolve pronouns to the referent in the claim text.

## 7. Filename date overriding content date

Filename `report-20240315.md`; content says "Last updated: 2024-09-22"; you set `date: "2024-03-15"`.

**Discipline:** stated content date wins. Filename is fallback only.

## 8. Inferring entities

Populating `entities` array with invented entity ids.

**Discipline:** `entities: []` always. Grapher populates back-pointers in Phase 2.

## 9. Reading the wrong file (recursion safety)

Source path matches `output/synthesis-*/`; you extract anyway.

**Discipline:** check prefix before reading. Refuse with explicit error (B-recur invariant 7).
