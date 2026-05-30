export const meta = {
  name: 'research-and-verify',
  description: 'Recency-filtered multi-angle research with adversarial citation verification; returns a consensus plus an explicit could-not-verify list. Read-only — never edits.',
  whenToUse: 'Before a non-trivial design recommendation, or before an ADR/document cites external sources. NOT for facts already in the repo (do a direct read) or settled stdlib questions. Pass {question:"..."} (and optionally {today:"...note about recency..."}).',
  phases: [
    { title: 'Sweep', detail: 'parallel angles: official / community / technical' },
    { title: 'Verify', detail: 'adversarially verify each load-bearing citation (default-distrust)' },
    { title: 'Synthesize', detail: 'consensus + confidence + could-not-verify list' },
  ],
}

const question = (args && args.question) || (typeof args === 'string' ? args : null)
if (!question) { log('ERROR: pass {question: "..."} as args'); return { error: 'no question supplied' } }
const recencyNote = (args && args.today) || 'Prioritise the most recent sources; label anything undated as foundational. Do NOT fabricate URLs or dates.'

const ANGLES = [
  { key: 'official', lens: 'official / primary sources (vendor docs, standards bodies, specs, official blogs)' },
  { key: 'community', lens: 'community sources (engineering blogs, conference talks, respected practitioners, OSS issues)' },
  { key: 'technical', lens: 'the precise technical mechanism / API / algorithm, with a concrete example' },
]

const FIND_SCHEMA = {
  type: 'object', additionalProperties: false,
  properties: {
    findings: {
      type: 'array',
      items: {
        type: 'object', additionalProperties: false,
        properties: {
          claim: { type: 'string' },
          source_title: { type: 'string' },
          source_url: { type: 'string' },
          source_date: { type: 'string', description: 'publisher-stated date, or "undated/foundational"' },
          load_bearing: { type: 'boolean', description: 'true if a recommendation would rest on this claim' },
        },
        required: ['claim', 'source_title', 'source_url', 'source_date', 'load_bearing'],
      },
    },
    notes: { type: 'string' },
  },
  required: ['findings', 'notes'],
}

phase('Sweep')
const swept = await parallel(ANGLES.map(a => () =>
  agent(
    `Research this question from the ${a.key} angle (${a.lens}).\n\nQuestion: "${question}".\n\n${recencyNote}\n\n` +
    `Use exa/web search and context7 where useful. Return findings with exact source title, URL, and publisher-stated date. ` +
    `Mark load_bearing=true for any claim a recommendation would actually rest on.`,
    { label: `sweep:${a.key}`, phase: 'Sweep', schema: FIND_SCHEMA }
  )
))

const allFindings = swept.filter(Boolean).flatMap(s => s.findings)
const loadBearing = allFindings.filter(f => f.load_bearing)
log(`swept ${allFindings.length} findings; ${loadBearing.length} load-bearing to verify`)

phase('Verify')
const VERDICT_SCHEMA = {
  type: 'object', additionalProperties: false,
  properties: {
    source_url: { type: 'string' },
    exists: { type: 'string', enum: ['confirmed', 'not-found', 'uncertain'] },
    date_plausible: { type: 'string', enum: ['yes', 'no', 'uncertain'] },
    supports_claim: { type: 'string', enum: ['yes', 'partial', 'no', 'uncertain'] },
    verdict: { type: 'string', enum: ['verified', 'unverified', 'refuted'] },
    note: { type: 'string' },
  },
  required: ['source_url', 'exists', 'date_plausible', 'supports_claim', 'verdict', 'note'],
}

const verified = await parallel(loadBearing.map(f => () =>
  agent(
    `Adversarially verify this citation. Default to "unverified" unless you can independently confirm it.\n\n` +
    `Claim: "${f.claim}"\nSource: "${f.source_title}" — ${f.source_url} (stated date: ${f.source_date}).\n\n` +
    `Check: does the URL resolve to a real page? is the date plausible (flag future or implausible dates)? does the page actually support the claim? ` +
    `Use web fetch/search. Return a verdict.`,
    { label: `verify:${f.source_url}`, phase: 'Verify', schema: VERDICT_SCHEMA }
  ).then(v => ({ ...f, verification: v }))
))

const v = verified.filter(Boolean)
const couldNotVerify = v.filter(x => x.verification.verdict !== 'verified')

phase('Synthesize')
const synthesis = await agent(
  `Synthesise a consensus answer to: "${question}".\n\nFindings (with verification):\n` +
  JSON.stringify(v, null, 2) +
  `\n\nProduce: (1) the consensus in plain English; (2) what is settled vs contested; (3) confidence per major claim, ` +
  `using ONLY verified citations as load-bearing; (4) an explicit "could-not-verify" list (the unverified/refuted citations — do not rely on them). ` +
  `Be honest about gaps. Under 600 words.`,
  { label: 'synthesize', phase: 'Synthesize' }
)

return { synthesis, could_not_verify: couldNotVerify, all_findings: allFindings }
