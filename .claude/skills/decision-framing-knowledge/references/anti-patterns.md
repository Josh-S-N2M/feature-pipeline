# Framer Anti-patterns

## 1. Misclassifying implementation as architectural

Routing a "use library Z" decision into ADR territory because it touches multiple services.

**Discipline:** apply the 2-of-3 rule (one_way + blast_radius≥service + cross-team). "Use library Z" rarely qualifies — most library choices are reversible.

## 2. Missing Wardley stage

Leaving `wardley_stage` empty or guessing without source signal.

**Discipline:** infer from claims. If no claim signals stage, default to `custom` and note in `risks`: "Wardley stage inferred from absence of signal."

## 3. RICE without source-cited evidence

Assigning `reach: 1000` because "feels like a lot of users."

**Discipline:** reach numbers cite the claim that supports them. If no claim supports a quantification, drop or downgrade.

## 4. Including unverifiable claims (invariant 5 violation)

Claim has `verdict: unverifiable` and no `dissent_evidence`; you include in `claim_cluster_ids` anyway.

**Discipline:** invariant 5 of §7.1 is hard. Exclude. The Synthesizer surfaces unverifiable claims in Limitations, where they can be re-examined.

## 5. Conflating two decisions

Decision frame combines "what auth provider" + "what auth library" into one decision.

**Discipline:** if the two questions could be answered independently, they are two decisions.

## 6. Over-broad scope

Producing 25 decision frames when scope is `narrow`.

**Discipline:** respect manifest scope. `narrow` → 3–5; `broad` → 8–15; `exploratory` → 15–25.
