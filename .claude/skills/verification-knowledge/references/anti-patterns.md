# Critic Anti-patterns

## 1. Rubber-stamping

Setting `verdict: verified` on every claim without doing CoVe.

**Discipline:** every claim gets verification questions and explicit answers. Even simple claims warrant 1–2 questions to confirm the source actually supports the assertion.

## 2. Whole-source re-reads

Reading entire source files to "verify context."

**Discipline:** Grep selective passages. If Grep can't find context, that's a signal the claim was poorly extracted — `verdict: unverifiable` with note.

## 3. Dissent-marking on unverifiable claims

When two claims conflict and one is unverifiable: marking dissent.

**Discipline:** dissent requires both claims to be independently verifiable on their own sources. Otherwise it's just one claim being wrong.

## 4. Auto-resolving disagreement

Choosing one side of a real dissent and downgrading the other.

**Discipline:** Critic surfaces dissent; Synthesizer reports both perspectives transparently. Critic does not arbitrate.

## 5. AskUserQuestion overuse

Escalating to user on every ambiguous claim.

**Discipline:** AskUserQuestion is reserved for irreconcilable conflicts in critical claims. Most ambiguity gets `verdict: unverifiable` and lands in the report's Limitations section.

## 6. Ignoring constraint flagging

Skipping the `violates_constraint` check.

**Discipline:** read `manifest.constraints.hard_constraints[]` at task start; check every claim. Constraint violations propagate to Framer and surface in the final report.
