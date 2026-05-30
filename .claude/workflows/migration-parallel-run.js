export const meta = {
  name: 'migration-parallel-run',
  description: 'BUILD-TIME (post-freeze): for each pipeline, run the prose path and the manifest-driven loop on the same replay, diff their decisions, and report cutover-readiness. THIN orchestration over the deterministic parallel_run_diff.py — justified only when iterating across MULTIPLE pipelines; for one pipeline, just run the script.',
  whenToUse: 'Plan WS-1f / close-out migration when there are multiple pipelines to cut over. NOT for a single pipeline, NOT during a write-freeze. Args: {pipelines:[...], diff_cmd?}.',
  phases: [
    { title: 'Diff', detail: 'parallel-run + decision diff per pipeline' },
  ],
}

const pipelines = (args && args.pipelines) || []
if (!pipelines.length) { log('ERROR: pass {pipelines:[...]}'); return { error: 'no pipelines supplied' } }
const diffCmd = (args && args.diff_cmd) || 'python3 .claude/skills/auditing-shared/scripts/parallel_run_diff.py'

const SCHEMA = {
  type: 'object', additionalProperties: false,
  properties: {
    pipeline: { type: 'string' },
    diff_empty: { type: 'boolean', description: 'true if prose path and manifest loop produced identical stage+gate decisions' },
    cutover_ready: { type: 'boolean' },
    detail: { type: 'string' },
  },
  required: ['pipeline', 'diff_empty', 'cutover_ready', 'detail'],
}

const results = await parallel(pipelines.map(p => () =>
  agent(
    `Run the parallel-run diff for pipeline "${p}": \`${diffCmd} --pipeline ${p}\`. ` +
    `Report whether the prose path and the manifest-driven loop produced identical stage + gate decisions (diff_empty), whether it is cutover_ready, and any divergences. ` +
    `Do NOT cut over — report only.`,
    { label: `diff:${p}`, phase: 'Diff', schema: SCHEMA }
  )
))

return { results: results.filter(Boolean) }
