export const meta = {
  name: 'failure-mode-catalog',
  description: 'The COMPLETENESS review (the review family\'s missing member: consistency→completeness→soundness→code). Two jobs the research prescribes: (1) a COVERAGE scan of the rule/anti-pattern set against a concern taxonomy (arc42 crosscutting concepts + ISO 25010 + our project concerns) to surface MISSING concerns that conformance review structurally cannot catch — e.g. the KB-skill load/use gap; (2) an FMEA failure-modes catalog — for every rule (R*) and anti-pattern (A*), enumerate failure modes via software guidewords + misuse-case hunting, each mapped to what-good-looks-like + a detection mechanism. Report-only: emits the catalog + coverage gaps + proposed new-rule stubs for a human to fold in. Never edits.',
  whenToUse: 'After document-critique (consistency), BEFORE design-review (soundness) — soundness checks against the rules, so the rules must be complete first. Args: {arch, batch}.',
  phases: [
    { title: 'Inventory', detail: 'extract every rule, anti-pattern, and stated concern' },
    { title: 'Coverage', detail: 'map the concern taxonomy → flag concerns with no rule (gaps)' },
    { title: 'Enumerate', detail: 'FMEA per rule/AP: failure modes via guidewords + misuse-cases' },
    { title: 'Synthesize', detail: 'catalog + coverage gaps + new-rule stubs + completeness critic' },
  ],
}

const ARCH = (args && args.arch) || 'governed-pipeline-architecture.md'
const BATCH = (args && args.batch) || 4

// Software FMEA guidewords — the systematic enumeration prompt (SW-FMEA; no numeric RPN).
const GUIDEWORDS = 'non-execution (never runs) · untimely (runs too early/late/out-of-order) · incorrect-result · wrong-state-transition · stale-data · corrupted-or-missing-config · interface-mismatch (declared ≠ actual) · silent-degradation (fails without signal) · partial-completion (crash mid-step)'

// Concern taxonomy for the coverage scan — arc42 §8 crosscutting + ISO/IEC 25010 + this project's concerns.
// A concern NOT addressed by any rule/Part/decision is a COVERAGE gap (not a conformance violation).
const TAXONOMY = [
  // arc42 crosscutting concepts
  'persistence / durable state', 'error & exception handling', 'logging / tracing / observability',
  'configuration & secrets', 'communication / integration between components', 'concurrency & ordering',
  'session / context handling', 'build / test / deploy', 'security',
  // ISO/IEC 25010
  'reliability (maturity, fault tolerance, recoverability)', 'maintainability (modularity, analysability, modifiability, testability)',
  'compatibility / interoperability', 'performance efficiency (incl. token/context budget)', 'safety',
  // this project's specific concerns
  'KB / skill load+use governance — which knowledge loads into which agent in which context; declared vs loaded vs used',
  'tool / MCP lifecycle (registry, init, health, usage)',
  'pipeline-definition consistency — all pipelines (feature, execution, cc-critique, issue-capture) defined the same canonical way',
  'orchestration substrate — dynamic-workflow migration consistency across pipelines',
  'freshness / lineage of artifacts', 'crash recovery / replay / idempotency',
  'reviewer-gate / LLM-as-judge reliability', 'domain-pack lifecycle (add/remove/orphan)',
  'durable-knowledge governance (ADR index, decision graph, memory)', 'human oversight / escalation',
  'improvement loop / telemetry feedback', 'agent-to-context mapping (which agent runs with which skills/tools/KBs)',
]

const chunk = (a, n) => { const o = []; for (let i = 0; i < a.length; i += n) o.push(a.slice(i, i + n)); return o }

const INV_SCHEMA = {
  type: 'object', additionalProperties: false,
  properties: {
    rules: { type: 'array', items: { type: 'object', additionalProperties: false, properties: { id: { type: 'string' }, statement: { type: 'string' } }, required: ['id', 'statement'] } },
    antipatterns: { type: 'array', items: { type: 'object', additionalProperties: false, properties: { id: { type: 'string' }, statement: { type: 'string' } }, required: ['id', 'statement'] } },
  },
  required: ['rules', 'antipatterns'],
}

const COVERAGE_SCHEMA = {
  type: 'object', additionalProperties: false,
  properties: { results: { type: 'array', items: {
    type: 'object', additionalProperties: false,
    properties: {
      concern: { type: 'string' },
      addressed: { type: 'boolean', description: 'is this concern addressed by some rule / anti-pattern / Part / decision?' },
      addressed_by: { type: 'string', description: 'the rule/Part/decision id(s), or empty' },
      gap_severity: { type: 'string', enum: ['blocker', 'major', 'minor', 'none'] },
      proposed_rule_stub: { type: 'string', description: 'if a gap: a one-line proposed rule (what good looks like), else empty' },
    }, required: ['concern', 'addressed', 'addressed_by', 'gap_severity'] } } },
  required: ['results'],
}

const FMEA_SCHEMA = {
  type: 'object', additionalProperties: false,
  properties: { results: { type: 'array', items: {
    type: 'object', additionalProperties: false,
    properties: {
      origin: { type: 'string', description: 'the rule/AP id this failure mode is for' },
      failure_modes: { type: 'array', items: {
        type: 'object', additionalProperties: false,
        properties: {
          guideword: { type: 'string' },
          mode: { type: 'string', description: 'the concrete failure' },
          cause: { type: 'string' },
          effect: { type: 'string' },
          good_state: { type: 'string', description: 'what good looks like (preventive)' },
          detection: { type: 'string', description: 'how we catch it — a concrete check / validator / span / review gate' },
          priority: { type: 'string', enum: ['high', 'medium', 'low'] },
        }, required: ['guideword', 'mode', 'cause', 'effect', 'good_state', 'detection', 'priority'] } },
    }, required: ['origin', 'failure_modes'] } } },
  required: ['results'],
}

// ---- 1. Inventory ----------------------------------------------------------
phase('Inventory')
const inv = await agent(
  `Read ${ARCH}. Extract EVERY rule (R1..Rn, verbatim) and EVERY anti-pattern (A1..An, verbatim) from the cross-cutting-disciplines section + any per-part rules. Be exhaustive — list each with its id and statement. Completeness is the point.`,
  { label: 'inventory', phase: 'Inventory', schema: INV_SCHEMA }
)
log(`Inventory: ${inv.rules.length} rules, ${inv.antipatterns.length} anti-patterns`)

// ---- 2. Coverage scan (the COMPLETENESS review) ----------------------------
phase('Coverage')
const taxBatches = chunk(TAXONOMY, BATCH)
const coverageRaw = await parallel(taxBatches.map((b, i) => () =>
  agent(
    `COMPLETENESS / COVERAGE review (SEI doctrine: conformance asks "do we obey the rules"; completeness asks "is every CONCERN addressed by SOME rule/Part/decision"). For EACH concern below, read ${ARCH} and judge: is it addressed by a rule, anti-pattern, Part, or decision? Name what addresses it, or mark it a GAP with a severity and a proposed one-line rule stub (what good would look like). A concern can be real and obligatory yet have NO written rule — that is exactly the gap class we are hunting. Do not force-fit; if nothing addresses it, say so.\n\nConcerns:\n${JSON.stringify(b, null, 2)}\n\nRules + anti-patterns in scope:\n${JSON.stringify([...inv.rules.map(r => r.id), ...inv.antipatterns.map(a => a.id)])}`,
    { label: `coverage:${i + 1}`, phase: 'Coverage', schema: COVERAGE_SCHEMA }
  )
))
const coverage = coverageRaw.filter(Boolean).flatMap(x => x.results || [])
const gaps = coverage.filter(c => !c.addressed && c.gap_severity !== 'none')
log(`Coverage: ${coverage.length} concerns checked; ${gaps.length} gaps (missing concerns)`)

// ---- 3. Enumerate failure modes (FMEA) over every rule + anti-pattern ------
phase('Enumerate')
const items = [...inv.rules.map(r => ({ ...r, kind: 'rule' })), ...inv.antipatterns.map(a => ({ ...a, kind: 'anti-pattern' }))]
const itemBatches = chunk(items, BATCH)
const fmeaRaw = await parallel(itemBatches.map((b, i) => () =>
  agent(
    `FMEA — for EACH rule/anti-pattern below, enumerate its concrete FAILURE MODES. Work systematically through the guidewords (${GUIDEWORDS}) AND hunt MISUSE/ABUSE cases ("who or what would make this go wrong, deliberately or by neglect?") so you catch failures the rule's wording does not obviously imply — the research warns "no work is done on unimagined failures." For each failure mode give: guideword, the concrete mode, cause, effect, what-good-looks-like (preventive), a DETECTION mechanism (a real check / validator / run-event span / review gate — not "be careful"), and priority (high/medium/low). 2–5 modes per item; quality over volume; no bureaucratic filler. Read ${ARCH} for what each rule actually guarantees.\n\nItems:\n${JSON.stringify(b, null, 2)}`,
    { label: `fmea:${i + 1}`, phase: 'Enumerate', schema: FMEA_SCHEMA }
  )
))
const fmea = fmeaRaw.filter(Boolean).flatMap(x => x.results || [])
const totalModes = fmea.reduce((n, r) => n + (r.failure_modes || []).length, 0)
log(`FMEA: ${fmea.length} items, ${totalModes} failure modes enumerated`)

// ---- 4. Synthesize: catalog + coverage gaps + new-rule stubs + critic ------
phase('Synthesize')
const synthesis = await agent(
  `Assemble the foundation analysis.\n\nCOVERAGE GAPS (missing concerns — no rule addresses them):\n${JSON.stringify(gaps, null, 2)}\n\n` +
  `FMEA CATALOG (failure modes per rule/anti-pattern):\n${JSON.stringify(fmea, null, 2)}\n\n` +
  `Produce, under 1200 words:\n` +
  `1. COVERAGE REPORT — the missing concerns, severity-ranked, each with the proposed new-rule stub. Call out the KB/skill load-use concern explicitly (resolved or still a gap?).\n` +
  `2. PROPOSED NEW RULES / ANTI-PATTERNS — concrete stubs (id-less) the human should author to close the gaps.\n` +
  `3. CATALOG HEADLINES — the highest-priority failure modes across the set, grouped, each: rule → failure mode → detection. (The full catalog is the structured return; here surface the high-priority ones.)\n` +
  `4. COMPLETENESS CRITIC — what concern or failure class might STILL be missing that neither the taxonomy nor the rules covered? (the "unimagined failure" check, applied to ourselves).\n` +
  `Everything is candidate for a HUMAN to fold into the architecture's rule set + a canonical failure-modes catalog. Report-only.`,
  { label: 'synthesize', phase: 'Synthesize' }
)

return { synthesis, coverage_gaps: gaps, coverage_full: coverage, fmea_catalog: fmea,
  counts: { rules: inv.rules.length, antipatterns: inv.antipatterns.length, concerns: coverage.length, gaps: gaps.length, failure_modes: totalModes } }
