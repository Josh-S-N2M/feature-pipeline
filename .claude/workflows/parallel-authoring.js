export const meta = {
  name: 'parallel-authoring',
  description: 'BUILD-TIME (post-freeze): author independent, schema-constrained code units in parallel, each verified against the corpus/smoke test as it lands. WRITES CODE — do not run during a write-freeze.',
  whenToUse: 'Plan WS-1b validators, WS-2 scaffolding, WS-4 KB bundles — independent units only, each targeting a DISTINCT path. NOT for sequential/stateful work (the orchestrator migration) or anything needing human design judgment per unit. Args: {units:[{name, target_path, spec, verify_cmd}]}.',
  phases: [
    { title: 'Author', detail: 'write each unit to its distinct target path' },
    { title: 'Verify', detail: 'corpus/smoke test each unit as it completes' },
  ],
}

const units = (args && args.units) || []
if (!units.length) { log('ERROR: pass {units:[{name, target_path, spec, verify_cmd}]}'); return { error: 'no units supplied' } }

// Units must target DISTINCT paths so parallel writes never conflict — hence no worktree isolation
// (worktree would strand the changes off the main tree). If two units share a file, split them or run sequentially.

const AUTHOR_SCHEMA = {
  type: 'object', additionalProperties: false,
  properties: {
    unit: { type: 'string' },
    status: { type: 'string', enum: ['authored', 'failed'] },
    files: { type: 'array', items: { type: 'string' } },
    note: { type: 'string' },
  },
  required: ['unit', 'status', 'files', 'note'],
}
const VERIFY_SCHEMA = {
  type: 'object', additionalProperties: false,
  properties: {
    unit: { type: 'string' },
    passed: { type: 'boolean' },
    output: { type: 'string' },
  },
  required: ['unit', 'passed', 'output'],
}

const results = await pipeline(
  units,
  (u) => agent(
    `Author this unit per its spec. Write ONLY within its target path. Follow the project's canonical-first discipline: read rules from .claude/canonical via canonical.py; define no hardcoded constants (CANON-1 must stay green). ` +
    `If you use serena symbol tools (e.g. rename_symbol / find_referencing_symbols — the project forbids find-and-replace renames), FIRST call mcp__serena__activate_project('feature-pipeline'); a fresh agent has no active serena project.\n\n` +
    `Unit: ${u.name}\nTarget path: ${u.target_path}\nSpec:\n${u.spec}`,
    { label: `author:${u.name}`, phase: 'Author', schema: AUTHOR_SCHEMA }
  ),
  (authored, u) => agent(
    `Verify the unit "${u.name}" by running: ${u.verify_cmd || 'the corpus regression + its smoke test'}. Report pass/fail with the relevant output. Do not edit the unit; verify only.`,
    { label: `verify:${u.name}`, phase: 'Verify', schema: VERIFY_SCHEMA }
  ).then(vr => ({ unit: u.name, authored, verify: vr }))
)

return { results: results.filter(Boolean) }
