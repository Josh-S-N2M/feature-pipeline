export const meta = {
  name: 'decouple-evidence',
  description: 'Plans the refactor of governed-pipeline-architecture.md into a TIMELESS, codebase-agnostic principles document — stripping every reference to THIS repo (path:line citations, file/script/agent names, run/slug names, repo-specific counts, the evidence map, "Evidenced in" columns, worked examples that name real runs) — WITHOUT losing information we need. The core discipline: separate the EVIDENCE (which moves out) from the DESIGN CLAIM it supports (which stays, restated abstractly). Report-only: emits a per-section refactor playbook + the extracted-evidence content (relocated to the plan or a new evidence file) + a NO-LOSS attestation. Does NOT rewrite the doc (that is a single-context pass, for one coherent voice).',
  whenToUse: 'When the architecture must become portable / principle-only and the evidence must be decoupled without information loss. Args: {arch, plan, evidence_target}.',
  phases: [
    { title: 'Scan', detail: 'per section: find every repo-reference/evidence item + its design claim + a disposition' },
    { title: 'NoLoss', detail: 'adversarially verify each disposition preserves the information' },
    { title: 'Synthesize', detail: 'refactor playbook + extracted-evidence content + no-loss attestation' },
  ],
}

const ARCH = (args && args.arch) || 'governed-pipeline-architecture.md'
const PLAN = (args && args.plan) || 'implementation-plan.md'
// where decoupled evidence should land: 'plan' (the repo-specific doc) | 'evidence-file' (a new architecture-evidence.md) | 'either' (let the workflow recommend per item)
const EVIDENCE_TARGET = (args && args.evidence_target) || 'either'

// Fan-out unit = one architecture section. Each agent greps/reads its own section.
const SECTIONS = [
  'Part I — The Problems', 'Part II — The Principle and the Substrate',
  'Part III — Reliability I (Contract-Gated Pipeline)', 'Part IV — Reliability II (Freshness Gate)',
  'Part V — Reliability III (Observability)', 'Part VI — Extensibility (Domain-Pack)',
  'Part VII — Durable Knowledge Governance', 'Part VIII — Cross-Cutting Disciplines (rules + anti-patterns)',
  'Part IX — Adoption', 'Part X — Application (worked example, metrics, rollout)',
  'Appendix A — Evidence map', 'Appendix B — Trade-offs', 'Appendix C — Decisions',
  'Appendix D — Sources & references', 'Appendix E — Visual index', 'Appendix F — Technology Boundaries',
]

// What counts as a repo-reference / evidence item to strip:
const STRIP_CRITERIA =
  'STRIP these (they tie the doc to THIS repo): (a) code citations — any path, path:line, or named file/script/agent/skill of the actual codebase (e.g. `canonical.py:34`, `recipe-feature-pipeline/SKILL.md`, `.devcontainer/Dockerfile`); (b) named runs/slugs (e.g. "execution-pipeline-design-r1"); (c) repo-specific COUNTS/metrics ("72 instances", "68 ADRs", "~1,470 cross-refs", "14 past runs"); (d) the evidence map (Appendix A) and any "Evidenced in" / evidence column; (e) worked examples that narrate a specific real run; (f) ADR-number citations used as evidence (e.g. "per ADR-0045") where they assert a repo fact. ' +
  'KEEP (do NOT strip): internal cross-references (§N, Part N, Rn, An, Dn, TBn, figure ids) — these are intra-document structure, not codebase; and the abstract DESIGN CLAIM each evidence item supports.'

const SCAN_SCHEMA = {
  type: 'object', additionalProperties: false,
  properties: { items: { type: 'array', items: {
    type: 'object', additionalProperties: false,
    properties: {
      locator: { type: 'string', description: 'section + line/anchor' },
      excerpt: { type: 'string', description: 'the repo-reference/evidence text, verbatim-ish' },
      type: { type: 'string', enum: ['code_citation', 'named_run', 'repo_metric', 'evidence_map', 'evidenced_in_column', 'worked_example', 'adr_as_evidence'] },
      design_claim: { type: 'string', description: 'the abstract design point this evidence supports (the thing we must NOT lose)' },
      action: { type: 'string', enum: ['strip_keep_claim', 'relocate_to_plan', 'relocate_to_evidence_file', 'discard_with_rationale'] },
      restatement: { type: 'string', description: 'if strip_keep_claim: the abstract sentence that replaces the cited one (no repo specifics)' },
      target_note: { type: 'string', description: 'if relocate: what lands where; if discard: why it is safe to lose' },
    }, required: ['locator', 'excerpt', 'type', 'design_claim', 'action'] } } },
  required: ['items'],
}

const NOLOSS_SCHEMA = {
  type: 'object', additionalProperties: false,
  properties: { preserved: { type: 'boolean', description: 'is the design information preserved after this disposition?' },
    loss: { type: 'string', description: 'if not preserved: what information would be lost and how to fix the disposition' } },
  required: ['preserved', 'loss'],
}

// ---- 1. Scan (fan-out per section) -----------------------------------------
phase('Scan')
const scanned = await parallel(SECTIONS.map(s => () =>
  agent(
    `You are planning a refactor of ${ARCH} into a TIMELESS, codebase-agnostic principles document. Work ONLY on this section: "${s}". Read it (grep its heading in ${ARCH}, then read the section).\n\n` +
    `${STRIP_CRITERIA}\n\n` +
    `For EVERY repo-reference / evidence item in this section, return an entry: its locator, the excerpt, the type, the DESIGN CLAIM it supports (critical — this is what must survive), and a disposition:\n` +
    `- strip_keep_claim — the design point stays but the citation goes; give the abstract restatement (a sentence with NO repo specifics) that replaces it.\n` +
    `- relocate_to_plan — the evidence is repo-specific motivation/provenance the PLAN needs (the plan is the repo-specific, brownfield doc); say what moves.\n` +
    `- relocate_to_evidence_file — provenance worth keeping but not in the principles doc nor the plan; goes to a new architecture-evidence.md.\n` +
    `- discard_with_rationale — genuinely loses nothing; justify.\n` +
    `Default to strip_keep_claim or relocate; discard ONLY when truly lossless. Evidence target preference: ${EVIDENCE_TARGET}. Be exhaustive for this section — a missed citation defeats the refactor.`,
    { label: `scan:${s.slice(0, 18)}`, phase: 'Scan', schema: SCAN_SCHEMA }
  )
))
const items = scanned.filter(Boolean).flatMap(x => x.items || [])
log(`Scan: ${items.length} repo-reference/evidence items across ${SECTIONS.length} sections`)

// ---- 2. No-loss verify (adversarial, batched ~6/agent to bound fan-out) ----
phase('NoLoss')
const chunk = (a, n) => { const o = []; for (let i = 0; i < a.length; i += n) o.push(a.slice(i, i + n)); return o }
const NOLOSS_BATCH = {
  type: 'object', additionalProperties: false,
  properties: { results: { type: 'array', items: {
    type: 'object', additionalProperties: false,
    properties: { locator: { type: 'string' }, preserved: { type: 'boolean' }, loss: { type: 'string' } },
    required: ['locator', 'preserved', 'loss'] } } },
  required: ['results'],
}
const verifiedBatches = await parallel(chunk(items, 6).map((b, i) => () =>
  agent(
    `Adversarially check these refactor dispositions (stripping repo-references from ${ARCH} while preserving design information). RULE: the abstract DESIGN CLAIM must survive (restated in the principles doc); repo-specific evidence worth keeping must land in the plan or an evidence file; only pure citations vanish. For EACH item, be skeptical — would applying it LOSE information a reader needs (a rationale, a constraint, a "why")? Return per-item {locator, preserved, loss}.\n\nDispositions:\n${JSON.stringify(b, null, 2)}`,
    { label: `noloss:${i + 1}`, phase: 'NoLoss', schema: NOLOSS_BATCH }
  )
))
const verdictByLoc = {}
for (const vb of verifiedBatches.filter(Boolean)) for (const r of (vb.results || [])) verdictByLoc[r.locator] = r
const verified = items.map(it => ({ ...it, preserved: verdictByLoc[it.locator]?.preserved ?? true, loss: verdictByLoc[it.locator]?.loss || '' }))
const lossy = verified.filter(v => !v.preserved)
log(`No-loss: ${lossy.length} dispositions flagged as losing information (need a better disposition)`)

// ---- 3. Synthesize: playbook + extracted evidence + attestation ------------
phase('Synthesize')
const byType = {}
for (const v of verified.filter(Boolean)) byType[v.type] = (byType[v.type] || 0) + 1
const synthesis = await agent(
  `Assemble the evidence-decoupling refactor plan for ${ARCH}.\n\n` +
  `All dispositions (with no-loss verdicts):\n${JSON.stringify(verified.filter(Boolean), null, 2)}\n\n` +
  `Counts by type: ${JSON.stringify(byType)}. Dispositions flagged lossy: ${lossy.length}.\n\n` +
  `Produce:\n` +
  `1. REFACTOR PLAYBOOK — grouped by section, the concrete edits: what to strip, and for each strip the abstract restatement to put in its place (so the rewrite is mechanical and the design claim survives).\n` +
  `2. EXTRACTED-EVIDENCE CONTENT — the items relocating to the plan vs to a new architecture-evidence.md, written out ready to paste (so nothing is lost in transit). Recommend ONE target if the input said 'either'.\n` +
  `3. NO-LOSS ATTESTATION — confirm every design claim survives (restated or relocated); list any item still flagged lossy and how to fix its disposition. The refactor is NOT safe to apply until that list is empty.\n` +
  `4. RISK NOTE — what the rewrite must watch (e.g. the plan's traceability spine currently pairs architecture-evidence with plan change-targets — if evidence leaves the architecture, that spine must be re-pointed at the relocated evidence). Under 1000 words. Report-only.`,
  { label: 'synthesize', phase: 'Synthesize' }
)

return { synthesis, dispositions: verified.filter(Boolean), lossy, counts: { items: items.length, lossy: lossy.length, by_type: byType } }
