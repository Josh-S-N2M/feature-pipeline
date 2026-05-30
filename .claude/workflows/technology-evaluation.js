export const meta = {
  name: 'technology-evaluation',
  description: 'The DECISION arm of the portfolio. Turns one open technology choice into a recorded, boundary-filtered, trade-off-scored decision with verified recent evidence and a built-in re-evaluation trigger. Report-only — drafts an ADR-shaped decision record, never writes it (freeze-safe) and never picks for you (human seam after Synthesize). Spec + rationale: technology-evaluation.DESIGN.md.',
  whenToUse: 'When a provisional/open technology choice needs deciding (or a fired re-evaluation trigger re-opens one). NOT for choices swappable behind a stable interface at low blast radius (those are plan-level picks). Args: {decision:{role, plan_home, incumbent, prior_candidates?}, profile?, candidate_seeds?, max_candidates?, max_verify?, today?}.',
  phases: [
    { title: 'Frame', detail: 'read the choice + canonical boundaries + rubric profile' },
    { title: 'Enumerate', detail: 'multi-angle candidate discovery (the option set moves)' },
    { title: 'Screen', detail: 'boundary screen — eliminate out-of-bounds before scoring' },
    { title: 'Score', detail: 'weighted, anchored rubric over survivors' },
    { title: 'Verify', detail: 'adversarially verify the top survivors\' load-bearing claims' },
    { title: 'Synthesize', detail: 'rank + draft the decision record + re-evaluation trigger' },
  ],
}

// ---- args -------------------------------------------------------------------
const decision = (args && args.decision) || {
  // Default = the observability-backend pilot (DESIGN §8).
  role: 'a self-hostable single-container OpenTelemetry backend with a durable local store, never on the critical path (artifact lineage is the freshness gate\'s in-git derived_from graph, not this backend — D-OBS-2)',
  plan_home: 'implementation-plan.md WS-4 (observability)',
  incumbent: 'Arize Phoenix (currently provisional in the plan, explicitly open to revision)',
  prior_candidates: [],
}
const PROFILE = (args && args.profile) || null // null → use evaluation-rubric.yaml active_profile
const SEEDS = (args && args.candidate_seeds) || []
const MAX_CANDIDATES = (args && args.max_candidates) || 8
const MAX_VERIFY = (args && args.max_verify) || 3
const TODAY = (args && args.today) || null // caller-supplied date string; scripts can't call Date()

const BOUNDARIES = '.claude/canonical/technology-boundaries.yaml'
const RUBRIC = '.claude/canonical/evaluation-rubric.yaml'

// ---- schemas (no oneOf/allOf/anyOf at top level) ----------------------------
const FRAME_SCHEMA = {
  type: 'object', additionalProperties: false,
  properties: {
    role: { type: 'string' },
    decision_class: { type: 'string', enum: ['one-way door', 'two-way door'] },
    binding_tbs: { type: 'array', items: { type: 'string' }, description: 'TB ids that apply to this decision kind' },
    active_profile: { type: 'string' },
    weights: { type: 'object', additionalProperties: { type: 'number' }, description: 'criterion id -> weight, from the active rubric profile' },
    notes: { type: 'string' },
  },
  required: ['role', 'decision_class', 'binding_tbs', 'active_profile', 'weights'],
}

const ENUM_SCHEMA = {
  type: 'object', additionalProperties: false,
  properties: {
    candidates: {
      type: 'array',
      items: {
        type: 'object', additionalProperties: false,
        properties: {
          name: { type: 'string' },
          url: { type: 'string' },
          last_release: { type: 'string', description: 'most recent release/version + rough date, as found' },
          license: { type: 'string' },
          one_line: { type: 'string' },
          discovered_via: { type: 'string' },
          dormant: { type: 'boolean', description: 'no release/commit in ~12 months AND not a deliberately-complete tool' },
          dormant_reason: { type: 'string' },
        },
        required: ['name', 'url', 'one_line', 'discovered_via', 'dormant'],
      },
    },
  },
  required: ['candidates'],
}

const SCREEN_SCHEMA = {
  type: 'object', additionalProperties: false,
  properties: {
    name: { type: 'string' },
    verdict: { type: 'string', enum: ['in_bounds', 'eliminated'] },
    failing_tb: { type: 'string', description: 'the first boundary it fails, or empty if in_bounds' },
    check_type: { type: 'string', description: 'mechanical | judgment | mixed (of the failing check), or empty' },
    evidence: { type: 'string' },
    reason: { type: 'string' },
    cost_flag: { type: 'string', description: 'TB1: if in_bounds but it needs a machine bigger than the 4-core/16 GB default, name the tier + $/hr cost here; else empty' },
  },
  required: ['name', 'verdict', 'failing_tb', 'evidence', 'reason', 'cost_flag'],
}

const SCORE_SCHEMA = {
  type: 'object', additionalProperties: false,
  properties: {
    name: { type: 'string' },
    scores: {
      type: 'array',
      items: {
        type: 'object', additionalProperties: false,
        properties: {
          criterion: { type: 'string' },
          level: { type: 'integer', enum: [-1, 0, 1, 2, 3], description: '-1 = abstain' },
          reasoning: { type: 'string', description: 'chain-of-thought BEFORE the level' },
        },
        required: ['criterion', 'level', 'reasoning'],
      },
    },
  },
  required: ['name', 'scores'],
}

// ---- 1. Frame ---------------------------------------------------------------
phase('Frame')
const frame = await agent(
  `You are framing a technology DECISION for the feature-pipeline project. Read these files (use the Read tool):\n` +
  `- ${BOUNDARIES} — the technology boundaries (TB1..TB11) with per-boundary screen specs.\n` +
  `- ${RUBRIC} — the scoring rubric; use ${PROFILE ? `the "${PROFILE}" profile` : 'the active_profile'}.\n` +
  `- governed-pipeline-architecture.md (Appendix F for the boundary rationale) and implementation-plan.md (the plan home).\n\n` +
  `The decision under evaluation:\n${JSON.stringify(decision, null, 2)}\n\n` +
  `Produce the decision frame: restate the AGNOSTIC role (no vendor); classify it one-way vs two-way door (and note that reversibility decays — judge by the reversal-to-implementation cost ratio); list the binding_tbs — only the TB ids whose \`applies_to\` matches this decision's kind (this is a service-class decision unless the role says otherwise); name the active_profile and return its **EFFECTIVE** weights map: read the profile's base weights, then apply the \`decision_class_modifiers\` entry matching the door-type you classified (net-zero — the result must still sum to 100). Return the post-modifier weights. Keep notes short.`,
  { label: 'frame', phase: 'Frame', schema: FRAME_SCHEMA }
)

// ---- 2. Enumerate -----------------------------------------------------------
phase('Enumerate')
// Multi-angle discovery — each angle is blind to the others (DESIGN §4a). Seed
// with the incumbent + prior candidates so a re-run can diff against last time.
const ANGLES = [
  { key: 'registries', hint: 'official registries / awareness lists / "awesome-" lists for this category' },
  { key: 'alternatives', hint: `"alternatives to" comparisons against the incumbent (${decision.incumbent})` },
  { key: 'recent-releases', hint: 'tools with releases/changelogs in the last ~6-9 months (new entrants)' },
]
const enumResults = await parallel(ANGLES.map(a => () =>
  agent(
    `Discover current candidates for this role: "${frame.role}".\n` +
    `Search angle: ${a.hint}. Use exa/context7/WebSearch. The option set in this category MOVES — favour current sources.\n` +
    `Always include the incumbent (${decision.incumbent}) and these prior candidates if still live: ${JSON.stringify(decision.prior_candidates || [])}.\n` +
    `Also consider these seeds: ${JSON.stringify(SEEDS)}.\n` +
    `For each candidate return {name, url, last_release, license, one_line, discovered_via:"${a.key}", dormant, dormant_reason}. ` +
    `Set dormant=true ONLY if there's no release/commit in ~12 months AND it is not a deliberately-complete tool; give the reason. Do not pre-filter on boundaries — that's the next phase.`,
    { label: `enumerate:${a.key}`, phase: 'Enumerate', schema: ENUM_SCHEMA }
  )
))

// Merge + dedupe by normalized name; keep the richest record; log the dormant tail.
const byName = new Map()
for (const r of enumResults.filter(Boolean)) {
  for (const c of (r.candidates || [])) {
    const key = c.name.trim().toLowerCase()
    if (!byName.has(key)) byName.set(key, c)
    else { const e = byName.get(key); byName.set(key, { ...c, ...e, discovered_via: `${e.discovered_via}+${c.discovered_via}` }) }
  }
}
const all = [...byName.values()]
const dormant = all.filter(c => c.dormant)
const live = all.filter(c => !c.dormant)
if (dormant.length) log(`Set aside ${dormant.length} dormant: ${dormant.map(c => `${c.name} (${c.dormant_reason || 'no recent activity'})`).join('; ')}`)
// Cap with a LOGGED tail — never truncate silently (DESIGN §4a / portfolio "no silent caps").
let candidates = live
if (live.length > MAX_CANDIDATES) {
  candidates = live.slice(0, MAX_CANDIDATES)
  log(`Capped to ${MAX_CANDIDATES} candidates; set aside for this run: ${live.slice(MAX_CANDIDATES).map(c => c.name).join(', ')}`)
}
log(`${candidates.length} live candidates → boundary screen`)

// ---- 3. Boundary screen (hard gate, before any scoring) ---------------------
phase('Screen')
const screened = await parallel(candidates.map(c => () =>
  agent(
    `Screen this candidate against the project's technology boundaries — an ELIMINATION filter that runs BEFORE scoring.\n` +
    `Read ${BOUNDARIES}. Check the candidate against ONLY these binding boundaries: ${JSON.stringify(frame.binding_tbs)}.\n` +
    `For each, use the boundary's \`screen.signal\` to judge. RULE: for a hard boundary, if you cannot CONFIRM in-bounds from evidence (docs/repo/license), eliminate it (on_uncertainty: eliminate) and say so. Cite the evidence you read (a URL or a fact).\n` +
    `TB1 NUANCE (important): single-container + no-docker-compose/k8s/multi-node is STRUCTURAL — eliminate on those at any size. But footprint is a TUNABLE COST DIAL: the default machine is 4-core/16 GB, resizable to 64–128 GB at proportional $/hr. Do NOT eliminate a single-container tool just for needing more than 16 GB — mark it in_bounds and put the required tier + $/hr in cost_flag. Only eliminate on size if it exceeds the largest tier (128 GB).\n\n` +
    `Candidate: ${JSON.stringify(c)}\n\n` +
    `Return in_bounds (with cost_flag if it needs a bigger-than-default machine), or eliminated with the FIRST failing TB id, its check_type, the evidence, and a one-line reason. Set cost_flag to "" when the default machine suffices.`,
    { label: `screen:${c.name}`, phase: 'Screen', schema: SCREEN_SCHEMA }
  )
))
const eliminations = screened.filter(Boolean).filter(s => s.verdict === 'eliminated')
const survivors = candidates.filter(c => {
  const s = screened.find(x => x && x.name === c.name)
  return s && s.verdict === 'in_bounds'
})
log(`${survivors.length} in-bounds, ${eliminations.length} eliminated (${eliminations.map(e => `${e.name}→${e.failing_tb}`).join(', ') || 'none'})`)
// TB1 tunable-budget: in-bounds candidates that need a bigger-than-default machine carry a cost flag (not an elimination).
const costFlags = screened.filter(Boolean).filter(s => s.verdict === 'in_bounds' && s.cost_flag).map(s => ({ name: s.name, cost_flag: s.cost_flag }))
if (costFlags.length) log(`Cost-flagged (in-bounds, bigger machine): ${costFlags.map(c => `${c.name} — ${c.cost_flag}`).join('; ')}`)

// ---- 4. Score (survivors only) ----------------------------------------------
phase('Score')
const scored = await parallel(survivors.map(c => () =>
  agent(
    `Score this candidate on the project's evaluation rubric. Read ${RUBRIC} (use ${PROFILE ? `the "${PROFILE}" profile` : 'the active_profile'}).\n` +
    `For EACH criterion: write your chain-of-thought FIRST, then pick a level using that criterion's anchors (0=fails intent, 1=partial, 2=meets cleanly, 3=best-in-class). Use level -1 to ABSTAIN when you genuinely cannot judge — do not guess a number.\n` +
    `CRITICAL for capability_fit: score against OUR written questions (gate pass/fail counts, judge stability, cycle-time-over-runs, trace=run/span=step), NOT general feature breadth. A broad general-purpose tool that does not answer THESE scores LOW; a narrow tool purpose-built for THESE scores HIGH. Score against evidence, not vendor feature lists.\n\n` +
    `Candidate: ${JSON.stringify(c)}\n\nRole being filled: "${frame.role}". Cite evidence where you can (Read/Bash/web).`,
    { label: `score:${c.name}`, phase: 'Score', schema: SCORE_SCHEMA }
  ).then(sc => {
    // Deterministic weighted total from frame.weights, normalized over scored (non-abstained) weight.
    let num = 0, den = 0
    for (const s of sc.scores) {
      const w = frame.weights[s.criterion] || 0
      if (s.level >= 0) { num += s.level * w; den += w }
    }
    const total = den ? Math.round((num / (3 * den)) * 1000) / 10 : 0
    return { ...sc, weighted_total: total, abstained: sc.scores.filter(s => s.level < 0).map(s => s.criterion) }
  })
))
const ranked = scored.filter(Boolean).sort((a, b) => b.weighted_total - a.weighted_total)
log(`Ranked: ${ranked.map(r => `${r.name} ${r.weighted_total}`).join(' · ') || 'none'}`)
// Decision rule: too-close-to-call band (methodology research). Top-two gap < 10 → judgment, not the number.
const topGap = ranked.length >= 2 ? Math.round((ranked[0].weighted_total - ranked[1].weighted_total) * 10) / 10 : null
const tooClose = topGap !== null && topGap < 10
if (tooClose) log(`Top-two gap ${topGap} < 10 → TOO CLOSE TO CALL (route to judgment, not the raw number)`)

// ---- 5. Verify the top survivors' load-bearing claims -----------------------
phase('Verify')
const topN = ranked.slice(0, MAX_VERIFY)
let verification = { note: 'no survivors to verify', findings: [] }
if (topN.length) {
  // Nested research-and-verify (one level deep) — a SINGLE consolidated run over
  // the top survivors' load-bearing maturity/recency/license claims (cost cap).
  const question =
    `For each of these candidates for "${frame.role}", verify the load-bearing claims that drive a technology decision — ` +
    `current maintenance status & release recency, real-world adoption, license, and standard-shape (OTLP / OTel GenAI semconv) support. ` +
    `Flag anything you cannot confirm.\nCandidates: ${topN.map(t => t.name).join(', ')}.`
  try {
    verification = await workflow('research-and-verify', TODAY ? { question, today: TODAY } : { question })
  } catch (e) {
    log(`research-and-verify unavailable (${String(e).slice(0, 80)}) — falling back to inline verification`)
    verification = await parallel(topN.map(t => () =>
      agent(
        `Adversarially verify the load-bearing claims behind "${t.name}" as a choice for "${frame.role}": ` +
        `maintenance/recency, adoption, license, and OTLP / OTel GenAI semconv support. Default to "unconfirmed" unless you can confirm it from a current source. List confirmed vs could-not-verify.`,
        { label: `verify:${t.name}`, phase: 'Verify' }
      ).then(text => ({ name: t.name, verification: text }))
    )).then(arr => ({ note: 'inline fallback', findings: arr.filter(Boolean) }))
  }
}

// ---- 6. Synthesize the draft decision record (REPORT-ONLY, no write) --------
phase('Synthesize')
const draft = await agent(
  `Write a DRAFT decision record (ADR-shaped) for this technology choice. REPORT-ONLY — output the markdown as your answer; do NOT write any file (a write-freeze is in effect; the ADR is created later).\n\n` +
  `Use the template in .claude/workflows/technology-evaluation.DESIGN.md §7, and the re-evaluation-trigger conventions in §7a (the trigger MUST be observable and name its check mechanism; default horizon for AI-infra is 6 months).\n\n` +
  `Frame:\n${JSON.stringify(frame, null, 2)}\n\n` +
  `Boundary eliminations:\n${JSON.stringify(eliminations, null, 2)}\n\n` +
  `Cost flags (in-bounds, but need a machine bigger than the 4-core/16 GB default — factor the $/hr into the decision, do NOT treat as disqualifying):\n${JSON.stringify(costFlags, null, 2)}\n\n` +
  `Scored survivors (ranked, weighted_total normalized to 100):\n${JSON.stringify(ranked, null, 2)}\n\n` +
  `Verification of the top survivors:\n${JSON.stringify(verification, null, 2)}\n\n` +
  `Top-two weighted gap: ${topGap === null ? 'n/a' : topGap} (too-close-to-call band = 10). ${tooClose ? 'This gap is UNDER 10 — by the decision rules you MUST NOT crown a numeric winner; present the top contenders as TOO CLOSE TO CALL and frame the choice as a judgment call between them.' : 'The leader clears the band; the numeric ranking stands.'}\n\n` +
  `The decision is the boundary-clean candidate with the highest weighted score (unless too-close-to-call applies, per above); name the runner-up and the swap path; propose the re-evaluation trigger (prefer a CI-enforced signal over a bare date). Run a one-line sensitivity check: would shifting the top-weighted criterion ±10% flip the ranking? Be explicit about what we accept and give up. End with a one-paragraph note on what a human should sanity-check by hand before this is ratified.`,
  { label: 'synthesize', phase: 'Synthesize' }
)

return {
  frame,
  candidates: { live: candidates.length, dormant: dormant.map(c => c.name) },
  eliminations,
  cost_flags: costFlags,
  ranked,
  verification,
  draft_decision_record: draft,
}
