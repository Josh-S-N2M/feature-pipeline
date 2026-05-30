export const meta = {
  name: 'document-critique',
  description: 'Multi-lens, adversarially-verified conformance audit of the architecture + the plan. Report-only — never edits. Lenses: internal consistency, evidence traceability, category conflation, arch<->plan linkage, one-plan coherence, technology-boundary compatibility, citation-present-flagged (shallow), and (diff mode, when a prior version is supplied) concept loss.',
  whenToUse: 'After a substantive edit/reframe of the architecture or plan; before lifting a write-freeze; before authoring an ADR. NOT for typos or mid-authoring. Args: {arch, plan} paths (defaults below); {prior:{arch,plan}} enables diff mode.',
  phases: [
    { title: 'Review', detail: 'parallel lenses over the documents' },
    { title: 'Verify', detail: 'adversarially verify each finding (default-reject false positives)' },
    { title: 'Synthesize', detail: 'severity-rank + completeness critic' },
  ],
}

const ARCH = (args && args.arch) || 'governed-pipeline-architecture.md'
const PLAN = (args && args.plan) || 'implementation-plan.md'
const prior = (args && args.prior) || null // {arch: path, plan: path} — preserved prior versions for diff mode

const LENSES = [
  { key: 'internal-consistency', prompt: `Read ${ARCH} and ${PLAN}. Find internal-consistency defects: numbering gaps or duplicates (Parts, sections, R/A/D IDs, Figure IDs), dangling cross-references (a "§N" / "Part N" / "Appendix X" / "Dn" / "Vn" that does not resolve), and stale terminology (e.g. "two levels", "two plans", old filenames).` },
  { key: 'evidence-traceability', prompt: `Read ${ARCH}. Every PROBLEM and every metric should cite codebase evidence (path:line) or carry a Direct/Inferred label. Flag any problem asserted without evidence, and any metric not marked extrapolated.` },
  { key: 'category-conflation', prompt: `Read ${ARCH}. Probe for category conflations (the observability!=evals / memory!=learning!=decisions class): two distinct concepts merged under one term, or one governance regime wrongly shared across distinct functions. Flag each suspected conflation.` },
  { key: 'arch-plan-linkage', prompt: `Read ${ARCH} and ${PLAN}. Check bidirectional linkage EXHAUSTIVELY — do not spot-check.\n(a) ARCH->PLAN (orphan decisions): ENUMERATE EVERY decision in the architecture's Decisions register — D1..D18 AND every lettered-family entry (D-DOM-*, D-KN-*, D-TB-1, D-PF-1, D-OBS-*, D-RG-1, D-DR-1, D-ORCH-1, D-TOOL-1, D-IL-1, D-HO-1). Walk the list one by one; for each, find the realizing plan deliverable/workstream (the decision->workstream map PLUS the per-workstream Implements lines and deliverable rows). Flag EVERY decision with no realizing deliverable as an orphan. State how many decisions you enumerated, so coverage is auditable.\n(b) PLAN->ARCH: every plan workstream traces to a decision; every deliverable names the existing code it changes.\nList dangling links in both directions, naming the specific decision id / workstream.` },
  { key: 'one-plan-coherence', prompt: `Read ${PLAN}. It must be ONE coherent plan: no duplicated or competing content across workstreams; shared-asset edits (the drift sentinel, canonical) sequenced once; the warn->enforce flip described once. Flag duplication or competing sequencing.` },
  { key: 'boundary-compatibility', prompt: `Read ${ARCH} Appendix F (technology boundaries TB1-TB11) and ${PLAN}. Check: (a) the architecture names no vendor outside an architecturally-significant decision (flag vendor leakage); (b) every technology the plan names satisfies the TB-set (flag any out-of-bounds choice); (c) technology decisions are decision-referenced, not bare inline vendors.` },
  { key: 'citation-present-flagged', prompt: `Read ${ARCH} Appendix D. SHALLOW check only: does every external citation have a date (or "foundational"), and does the provenance caveat still apply? Flag undated/unflagged citations. Deep verification is the research-and-verify workflow's job, not this one — do NOT attempt it here.` },
]
if (prior) {
  LENSES.push({ key: 'no-loss-diff', prompt: `Compare the CURRENT ${ARCH} and ${PLAN} against the PRIOR versions at ${JSON.stringify(prior)}. Find load-bearing content present in the prior but missing or materially weakened now. Classify each: LOST-KEY (should be restored), COMPRESSED-OK, or SUPERSEDED.` })
}

const FINDING_SCHEMA = {
  type: 'object', additionalProperties: false,
  properties: {
    findings: {
      type: 'array',
      items: {
        type: 'object', additionalProperties: false,
        properties: {
          title: { type: 'string' },
          location: { type: 'string', description: 'doc + section/line' },
          severity: { type: 'string', enum: ['blocker', 'major', 'minor'] },
          detail: { type: 'string' },
        },
        required: ['title', 'location', 'severity', 'detail'],
      },
    },
  },
  required: ['findings'],
}

const VERIFY_SCHEMA = {
  type: 'object', additionalProperties: false,
  properties: { real: { type: 'boolean' }, reason: { type: 'string' } },
  required: ['real', 'reason'],
}

phase('Review')
// Pipeline (no barrier): each lens's findings start verifying as soon as that lens returns.
const reviewed = await pipeline(
  LENSES,
  (lensObj) => agent(
    `${lensObj.prompt}\n\nCite doc + section/line for every finding. To check a code path exists, Read it or Bash-grep it; if you use serena symbol tools, first call mcp__serena__activate_project('feature-pipeline'). Report findings only; do not propose rewrites.`,
    { label: `review:${lensObj.key}`, phase: 'Review', schema: FINDING_SCHEMA }
  ),
  (review, lensObj) => parallel((review ? review.findings : []).map(f => () =>
    agent(
      `Adversarially verify this critique finding — is it REAL, or a false positive? Default to "not real" unless you can confirm it by reading the cited location.\n\nFinding: ${JSON.stringify(f)}\n\nRead the cited doc/section and judge.`,
      { label: `verify:${lensObj.key}`, phase: 'Verify', schema: VERIFY_SCHEMA }
    ).then(vr => ({ ...f, lens: lensObj.key, verified_real: vr.real, verify_reason: vr.reason }))
  ))
)

const confirmed = reviewed.flat().filter(Boolean).filter(f => f.verified_real)

phase('Synthesize')
const synthesis = await agent(
  `These critique findings survived adversarial verification across ${LENSES.length} lenses:\n` +
  JSON.stringify(confirmed, null, 2) +
  `\n\nProduce a prioritised fix list (blocker -> major -> minor), de-duplicated, each with a one-line problem + one-line fix + which doc/section it touches. ` +
  `Then a completeness-critic paragraph: what lens or risk did we NOT cover that a human should check by hand? Under 700 words. ` +
  `Report-only — recommend fixes, do not apply them.`,
  { label: 'synthesize', phase: 'Synthesize' }
)

return { synthesis, confirmed_findings: confirmed }
