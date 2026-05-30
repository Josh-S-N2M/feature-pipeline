export const meta = {
  name: 'design-review',
  description: 'FULL FORENSIC design-soundness review of the architecture + plan — every architectural item considered through the lens of "does the design follow our own architecture?". Enumerates and checks EVERY Part (I–X), EVERY rule (R1..Rn), EVERY anti-pattern (A1..An); plus an adversarial correctness red-team of the load-bearing mechanisms, a SCOPED credential check (credential-leak only — not enterprise zero-trust/compliance), and a workstream-DAG schedulability pass. Emits a coverage matrix (proving every item was considered) + prioritised confirmed defects. Report-only — surfaces candidates for a human to adjudicate; never edits, never certifies.',
  whenToUse: 'After document-critique (internal consistency) and before compliance-audit (code-vs-design). The "is the design sound AND self-consistent with its own rules/anti-patterns?" gate. Args: {arch, plan, batch} (defaults below).',
  phases: [
    { title: 'Inventory', detail: 'extract EVERY Part, rule, anti-pattern + mechanisms, credential surfaces, the DAG' },
    { title: 'Review', detail: 'check every item for adherence; red-team mechanisms; scoped credential probe; schedulability' },
    { title: 'Verify', detail: 'confirm each candidate defect is real (default: the design holds)' },
    { title: 'Synthesize', detail: 'coverage matrix + prioritised defects + schedulability summary' },
  ],
}

const ARCH = (args && args.arch) || 'governed-pipeline-architecture.md'
const PLAN = (args && args.plan) || 'implementation-plan.md'
const BATCH = (args && args.batch) || 4 // rules/anti-patterns per review agent (coverage stays total; this just controls fan-out)

// SCOPE GUARDRAIL — every credential probe inherits this verbatim.
const SECURITY_SCOPE =
  'SECURITY SCOPE — credentials ONLY, major issues ONLY. This is a PRIVATE, EXPERIMENTAL project that must stay flexible. ' +
  'IN scope: a secret/token/key in argv, a URL query, a committed file, a log line, the run-event JSONL, or MCP config; a credential not routed through env-block / Codespaces Secrets indirection; a credential written somewhere it could be committed or shipped to the observability backend. ' +
  'OUT of scope (do NOT flag): missing zero-trust, RBAC, encryption-at-rest, secret rotation, threat models beyond credential leakage, compliance frameworks (SOC2/ISO/GDPR), audit-immutability, network segmentation, supply-chain attestation. ' +
  'Over-engineering security here is itself a defect — it breaks our ability to iterate. Flag only a concrete credential-leak path, with file/line and the leak mechanism.'

const chunk = (arr, n) => { const out = []; for (let i = 0; i < arr.length; i += n) out.push(arr.slice(i, i + n)); return out }

// ---- schemas ---------------------------------------------------------------
const INVENTORY_SCHEMA = {
  type: 'object', additionalProperties: false,
  properties: {
    parts: { type: 'array', items: { type: 'object', additionalProperties: false,
      properties: { id: { type: 'string' }, title: { type: 'string' }, designs: { type: 'string' } }, required: ['id', 'title', 'designs'] } },
    rules: { type: 'array', items: { type: 'object', additionalProperties: false,
      properties: { id: { type: 'string' }, statement: { type: 'string' } }, required: ['id', 'statement'] } },
    antipatterns: { type: 'array', items: { type: 'object', additionalProperties: false,
      properties: { id: { type: 'string' }, statement: { type: 'string' } }, required: ['id', 'statement'] } },
    mechanisms: { type: 'array', items: { type: 'object', additionalProperties: false,
      properties: { name: { type: 'string' }, location: { type: 'string' }, claim: { type: 'string' } }, required: ['name', 'location', 'claim'] } },
    credential_surfaces: { type: 'array', items: { type: 'object', additionalProperties: false,
      properties: { name: { type: 'string' }, location: { type: 'string' } }, required: ['name', 'location'] } },
    workstreams: { type: 'array', items: { type: 'object', additionalProperties: false,
      properties: { id: { type: 'string' }, depends_on: { type: 'array', items: { type: 'string' } }, size: { type: 'string' } }, required: ['id', 'depends_on', 'size'] } },
  },
  required: ['parts', 'rules', 'antipatterns', 'mechanisms', 'credential_surfaces', 'workstreams'],
}

const ITEM_SCHEMA = {
  type: 'object', additionalProperties: false,
  properties: { results: { type: 'array', items: { type: 'object', additionalProperties: false,
    properties: {
      id: { type: 'string' }, kind: { type: 'string', enum: ['rule', 'antipattern'] },
      pass: { type: 'boolean', description: 'rule: honored+enforced by a real mechanism. antipattern: avoided everywhere.' },
      evidence: { type: 'string', description: 'the enforcing mechanism (rule) / where it is avoided, OR where it fails' },
      finding: { type: 'string', description: 'if pass=false, the concrete gap; else empty' },
      severity: { type: 'string', enum: ['blocker', 'major', 'minor', 'none'] },
    }, required: ['id', 'kind', 'pass', 'evidence', 'severity'] } } },
  required: ['results'],
}

const PART_SCHEMA = {
  type: 'object', additionalProperties: false,
  properties: {
    part: { type: 'string' }, sound: { type: 'boolean', description: 'no logic gap/contradiction in the mechanism it designs' },
    fully_realized: { type: 'boolean', description: 'every component it introduces has a plan home' },
    findings: { type: 'array', items: { type: 'string' } }, severity: { type: 'string', enum: ['blocker', 'major', 'minor', 'none'] },
  }, required: ['part', 'sound', 'fully_realized', 'findings', 'severity'],
}

const DEFECT_SCHEMA = {
  type: 'object', additionalProperties: false,
  properties: {
    target: { type: 'string' }, dimension: { type: 'string', enum: ['correctness', 'credential'] },
    broke: { type: 'boolean' }, scenario: { type: 'string' }, severity: { type: 'string', enum: ['blocker', 'major', 'minor', 'none'] },
    location: { type: 'string' }, fix_hint: { type: 'string' },
  }, required: ['target', 'dimension', 'broke', 'scenario', 'severity', 'location'],
}

const SCHED_SCHEMA = {
  type: 'object', additionalProperties: false,
  properties: {
    critical_path: { type: 'array', items: { type: 'string' } },
    forward_or_circular_edges: { type: 'array', items: { type: 'string' } },
    sizing_concerns: { type: 'array', items: { type: 'string' } }, summary: { type: 'string' },
  }, required: ['critical_path', 'forward_or_circular_edges', 'sizing_concerns', 'summary'],
}

const VERIFY_SCHEMA = { type: 'object', additionalProperties: false,
  properties: { real: { type: 'boolean' }, reason: { type: 'string' } }, required: ['real', 'reason'] }

// ---- 1. Inventory (COMPLETE enumeration — missing an item defeats the review) ----
phase('Inventory')
const inv = await agent(
  `Read ${ARCH} and ${PLAN}. Extract the COMPLETE architectural inventory — completeness is the whole point; missing any item defeats this forensic review.\n` +
  `- parts: EVERY Part (I through X) — id, title, and what it designs.\n` +
  `- rules: EVERY rule, verbatim — read the full rules table(s) (Part VIII cross-cutting disciplines + any per-part R-codes). Capture R1 through the highest R-number; do not summarise the set, list each.\n` +
  `- antipatterns: EVERY anti-pattern, verbatim — the anti-patterns table (A1 through the highest A-number). List each.\n` +
  `- mechanisms: the load-bearing design mechanisms whose correctness could plausibly be wrong (replay/idempotency, freshness invalidation, gate state machine, per-segment orchestration handoff, decision-graph supersession, etc.).\n` +
  `- credential_surfaces: every place a secret/token/key flows or could be written. ${SECURITY_SCOPE}\n` +
  `- workstreams: the plan's workstreams/segments with depends_on + size.\n` +
  `Read the actual files; be exhaustive on rules and anti-patterns especially.`,
  { label: 'inventory', phase: 'Inventory', schema: INVENTORY_SCHEMA }
)
log(`Inventory: ${inv.parts.length} parts · ${inv.rules.length} rules · ${inv.antipatterns.length} anti-patterns · ${inv.mechanisms.length} mechanisms · ${inv.credential_surfaces.length} credential surfaces`)

// ---- 2. Review (forensic fan-out over EVERY item) --------------------------
phase('Review')
const ruleBatches = chunk(inv.rules, BATCH)
const apBatches = chunk(inv.antipatterns, BATCH)

const ruleThunks = ruleBatches.map((b, i) => () =>
  agent(
    `For EACH rule below, judge whether the DESIGN actually HONORS and ENFORCES it — is there a concrete mechanism that realizes the rule? Adversarially look for a rule that is stated but has no enforcing mechanism, or whose mechanism is bypassable/broken. pass=true ONLY if a real mechanism enforces it; cite that mechanism (or, if pass=false, the gap). Read ${ARCH}/${PLAN}.\n\nRules:\n${JSON.stringify(b, null, 2)}`,
    { label: `rules:${i + 1}`, phase: 'Review', schema: ITEM_SCHEMA }
  )
)
const apThunks = apBatches.map((b, i) => () =>
  agent(
    `For EACH anti-pattern below, judge whether the DESIGN AVOIDS it everywhere, or whether the design itself COMMITS it somewhere. pass=true ONLY if avoided; if the design falls into it, cite where + severity. Read ${ARCH}/${PLAN}.\n\nAnti-patterns:\n${JSON.stringify(b, null, 2)}`,
    { label: `antipatterns:${i + 1}`, phase: 'Review', schema: ITEM_SCHEMA }
  )
)
const partThunks = inv.parts.map(p => () =>
  agent(
    `Review this architecture Part for SOUNDNESS (no logic gap/contradiction in the mechanism it designs) and FULL REALIZATION (every component it introduces has a plan home in ${PLAN}). Read ${ARCH}/${PLAN}. List concrete findings; set sound/fully_realized accordingly.\n\nPart: ${JSON.stringify(p)}`,
    { label: `part:${p.id}`, phase: 'Review', schema: PART_SCHEMA }
  )
)
const mechThunks = inv.mechanisms.map(m => () =>
  agent(
    `Adversarially RED-TEAM this mechanism — try to BREAK it (race, double-apply, lost update, deadlock, unhandled crash/restart). Read ${ARCH}/${PLAN} for the described behavior.\n\nMechanism: ${JSON.stringify(m)}\n\nIf you construct a concrete break, broke=true with the step-by-step scenario + severity + fix. Else broke=false and say what you tried.`,
    { label: `mech:${m.name}`, phase: 'Review', schema: DEFECT_SCHEMA }
  )
)
const credThunks = inv.credential_surfaces.map(s => () =>
  agent(
    `Probe this surface for a CONCRETE CREDENTIAL-LEAK path. ${SECURITY_SCOPE}\n\nSurface: ${JSON.stringify(s)}\n\nRead the cited files; broke=true only for a concrete leak. A flag outside the credential scope is itself a wrong answer.`,
    { label: `cred:${s.name}`, phase: 'Review', schema: DEFECT_SCHEMA }
  )
)
const schedThunk = () =>
  agent(
    `Analyze the workstream DAG for SCHEDULABILITY:\n${JSON.stringify(inv.workstreams, null, 2)}\n\nFind the critical path; any forward/circular edge (consumer scheduled before producer); implausible sizing. Read ${PLAN} to confirm.`,
    { label: 'schedulability', phase: 'Review', schema: SCHED_SCHEMA }
  )

const reviewed = await parallel([...ruleThunks, ...apThunks, ...partThunks, ...mechThunks, ...credThunks, schedThunk])

// sort results by kind
const n = { r: ruleThunks.length, a: apThunks.length, p: partThunks.length, m: mechThunks.length, c: credThunks.length }
let k = 0
const ruleResults = reviewed.slice(k, k += n.r).filter(Boolean).flatMap(x => x.results || [])
const apResults = reviewed.slice(k, k += n.a).filter(Boolean).flatMap(x => x.results || [])
const partResults = reviewed.slice(k, k += n.p).filter(Boolean)
const mechResults = reviewed.slice(k, k += n.m).filter(Boolean)
const credResults = reviewed.slice(k, k += n.c).filter(Boolean)
const sched = reviewed[reviewed.length - 1]

// candidate defects = any item that failed
const candidates = [
  ...ruleResults.filter(x => !x.pass).map(x => ({ source: `rule ${x.id}`, detail: x.finding || x.evidence, severity: x.severity, location: x.evidence })),
  ...apResults.filter(x => !x.pass).map(x => ({ source: `anti-pattern ${x.id}`, detail: x.finding || x.evidence, severity: x.severity, location: x.evidence })),
  ...partResults.filter(x => !x.sound || !x.fully_realized).map(x => ({ source: `${x.part}`, detail: (x.findings || []).join('; '), severity: x.severity, location: x.part })),
  ...mechResults.filter(x => x.broke && x.severity !== 'none').map(x => ({ source: `mechanism ${x.target}`, detail: x.scenario, severity: x.severity, location: x.location })),
  ...credResults.filter(x => x.broke && x.severity !== 'none').map(x => ({ source: `credential ${x.target}`, detail: x.scenario, severity: x.severity, location: x.location })),
].filter(c => c.detail)
log(`Coverage: ${ruleResults.length} rules, ${apResults.length} anti-patterns, ${partResults.length} parts checked → ${candidates.length} candidate defects to verify`)

// ---- 3. Verify (default: the design holds) ---------------------------------
phase('Verify')
const verified = await parallel(candidates.map(c => () =>
  agent(
    `A forensic design-review check flagged this against our own architecture. Verify adversarially — DEFAULT to "the design holds / the rule is enforced / the anti-pattern is avoided" unless the gap concretely stands when you re-read ${ARCH}/${PLAN} at the cited location.\n\nFlag: ${JSON.stringify(c)}\n\nIs it a real defect?`,
    { label: `verify:${c.source}`, phase: 'Verify', schema: VERIFY_SCHEMA }
  ).then(v => ({ ...c, verified_real: v.real, verify_reason: v.reason }))
))
const confirmed = verified.filter(Boolean).filter(c => c.verified_real)

// ---- 4. Synthesize (coverage matrix + prioritised defects) -----------------
phase('Synthesize')
const matrix = {
  rules: ruleResults.map(x => ({ id: x.id, verdict: x.pass ? 'OK' : `FINDING(${x.severity})` })),
  antipatterns: apResults.map(x => ({ id: x.id, verdict: x.pass ? 'OK' : `FINDING(${x.severity})` })),
  parts: partResults.map(x => ({ id: x.part, verdict: (x.sound && x.fully_realized) ? 'OK' : `FINDING(${x.severity})` })),
}
const synthesis = await agent(
  `This is a FULL FORENSIC design review against our own architecture.\n\n` +
  `COVERAGE MATRIX (every item considered):\n${JSON.stringify(matrix, null, 2)}\n\n` +
  `CONFIRMED DEFECTS (survived adversarial verification):\n${JSON.stringify(confirmed, null, 2)}\n\n` +
  `SCHEDULABILITY:\n${JSON.stringify(sched, null, 2)}\n\n` +
  `Produce: (1) a COVERAGE SUMMARY — confirm every Part, every rule (R*), every anti-pattern (A*) was checked, with the counts, and list any that came back as findings; this proves nothing was skipped. (2) A prioritised confirmed-defect list (blocker → major → minor), grouped by dimension: rule-not-enforced, anti-pattern-committed, part-unsound-or-unrealized, mechanism-correctness, credential-leak, schedulability — each with the concrete gap + a one-line fix + location. (3) A short schedulability note. ` +
  `Everything is a candidate for a HUMAN to adjudicate — this review surfaces risks, it does not certify. Keep credentials strictly to real leak paths (no zero-trust/compliance scope-creep).`,
  { label: 'synthesize', phase: 'Synthesize' }
)

return { synthesis, coverage_matrix: matrix, confirmed_defects: confirmed, schedulability: sched,
  counts: { parts: inv.parts.length, rules: inv.rules.length, antipatterns: inv.antipatterns.length } }
