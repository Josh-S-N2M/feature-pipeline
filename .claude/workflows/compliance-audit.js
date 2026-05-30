export const meta = {
  name: 'compliance-audit',
  description: 'Scans the CURRENT codebase against the finalized architecture + plan, flags what is non-compliant and needs refactoring, and proposes refactor tasks to fold into the plan. The "does the code match the design?" audit — the opposite direction from design-review ("is the design sound?"). Report-only — proposes tasks, never edits the code or the plan. Complements the auditing-* skills (which check generic Claude Code config) by checking conformance to THIS architecture.',
  whenToUse: 'After the architecture + plan pass document-critique (consistency) AND design-review (soundness) — auditing code against an unsound or inconsistent design just propagates the problem. Args: {arch, plan, root} (defaults below).',
  phases: [
    { title: 'Scope', detail: 'derive a compliance checklist (boundaries + decisions + structural rules) + the code areas to check' },
    { title: 'Audit', detail: 'check each rule against the actual code (parallel)' },
    { title: 'Verify', detail: 'confirm each non-compliance is real (not compliant-by-another-mechanism)' },
    { title: 'Synthesize', detail: 'prioritized non-compliance list → proposed refactor tasks for the plan' },
  ],
}

const ARCH = (args && args.arch) || 'governed-pipeline-architecture.md'
const PLAN = (args && args.plan) || 'implementation-plan.md'
const ROOT = (args && args.root) || '.'

const SERENA_NOTE = "If you use serena symbol tools, FIRST call mcp__serena__activate_project('feature-pipeline'); a fresh agent has no active serena project. Otherwise use Read / Grep / Glob / Bash (rg, ls)."

const SCOPE_SCHEMA = {
  type: 'object', additionalProperties: false,
  properties: {
    rules: {
      type: 'array', description: 'the compliance rules the codebase must satisfy, drawn from the architecture',
      items: {
        type: 'object', additionalProperties: false,
        properties: {
          id: { type: 'string', description: 'e.g. TB5, D-OBS-2, CANON-1, sole-dispatcher' },
          rule: { type: 'string', description: 'the conformance requirement in one line' },
          how_to_check: { type: 'string', description: 'concretely how to test the code against it (grep/read targets)' },
          area: { type: 'string', description: 'the code area/glob most relevant' },
        },
        required: ['id', 'rule', 'how_to_check', 'area'],
      },
    },
  },
  required: ['rules'],
}

const FINDING_SCHEMA = {
  type: 'object', additionalProperties: false,
  properties: {
    rule_id: { type: 'string' },
    findings: {
      type: 'array',
      items: {
        type: 'object', additionalProperties: false,
        properties: {
          file: { type: 'string' },
          line: { type: 'string' },
          noncompliant: { type: 'boolean' },
          evidence: { type: 'string', description: 'the actual code/config that violates the rule' },
          severity: { type: 'string', enum: ['blocker', 'major', 'minor', 'info'] },
          refactor: { type: 'string', description: 'what change brings it into compliance' },
        },
        required: ['file', 'line', 'noncompliant', 'evidence', 'severity', 'refactor'],
      },
    },
  },
  required: ['rule_id', 'findings'],
}

const VERIFY_SCHEMA = {
  type: 'object', additionalProperties: false,
  properties: { real: { type: 'boolean' }, reason: { type: 'string' } },
  required: ['real', 'reason'],
}

// ---- 1. Scope --------------------------------------------------------------
phase('Scope')
const scope = await agent(
  `Read ${ARCH} (esp. Appendix F technology boundaries TB1–TB11 and the Decisions register) and ${PLAN}. Derive a CONCRETE COMPLIANCE CHECKLIST: the rules the EXISTING codebase under ${ROOT} must satisfy to conform to this architecture. ` +
  `Cover: the technology boundaries (TB1–TB11); the load-bearing decisions (the contract-gated pattern, canonical-first / no inline rule copies [CANON-1], sole-dispatcher / no agent-spawns-actor, OTel-only observability [D-OBS-2], Dynamic-Workflows orchestration [D-ORCH-1], the freshness/lineage model, etc.); and structural rules (gates at the named seams, validators read canonical, credential indirection [TB10]). ` +
  `For each rule give: id, the one-line requirement, how_to_check concretely (grep/read targets), and the code area. Aim for ~12–20 high-value rules — the ones a real refactor would hinge on, not trivia. ${SERENA_NOTE}`,
  { label: 'scope', phase: 'Scope', schema: SCOPE_SCHEMA }
)
log(`${(scope.rules || []).length} compliance rules to audit`)

// ---- 2. Audit (parallel, one agent per rule) -------------------------------
phase('Audit')
const audited = await parallel((scope.rules || []).map(r => () =>
  agent(
    `Audit the codebase under ${ROOT} against ONE architecture-compliance rule. Find concrete non-compliance with file:line evidence — actual code/config that violates it, not hypotheticals. If the code is compliant, return an empty findings list (do not invent issues). For each violation give the file, line, the offending evidence, a severity, and the refactor that fixes it.\n\n` +
    `Rule ${r.id}: ${r.rule}\nHow to check: ${r.how_to_check}\nArea: ${r.area}\n\n${SERENA_NOTE}`,
    { label: `audit:${r.id}`, phase: 'Audit', schema: FINDING_SCHEMA }
  )
))
const rawFindings = audited.filter(Boolean).flatMap(a => (a.findings || []).filter(f => f.noncompliant).map(f => ({ ...f, rule_id: a.rule_id })))
log(`${rawFindings.length} candidate non-compliance findings to verify`)

// ---- 3. Verify (default: it is actually compliant) -------------------------
phase('Verify')
const verified = await parallel(rawFindings.map(f => () =>
  agent(
    `An audit flagged this as non-compliant with the architecture. Verify adversarially — DEFAULT to "actually compliant" (compliant by another mechanism, or the rule does not really apply here) unless you confirm the violation by reading the cited file:line. ${SERENA_NOTE}\n\nFinding: ${JSON.stringify(f)}\n\nIs it genuinely non-compliant and in need of refactor?`,
    { label: `verify:${f.rule_id}`, phase: 'Verify', schema: VERIFY_SCHEMA }
  ).then(v => ({ ...f, verified_real: v.real, verify_reason: v.reason }))
))
const confirmed = verified.filter(Boolean).filter(f => f.verified_real)

// ---- 4. Synthesize → proposed refactor tasks -------------------------------
phase('Synthesize')
const synthesis = await agent(
  `These architecture-compliance violations survived adversarial verification:\n${JSON.stringify(confirmed, null, 2)}\n\n` +
  `Produce: (1) a prioritised non-compliance summary (blocker → major → minor), grouped by rule/boundary, each with file:line + the refactor; (2) a set of **proposed refactor TASKS** ready to fold into the plan — each task: a title, the files it touches, the rule it satisfies, and a rough size (S/M/L). ` +
  `Report-only: PROPOSE the tasks, do not edit the plan or the code. Then a one-paragraph completeness note: which areas the audit could not reach and a human should check by hand. Under 900 words.`,
  { label: 'synthesize', phase: 'Synthesize' }
)

return { synthesis, confirmed_violations: confirmed, rules_checked: (scope.rules || []).length }
