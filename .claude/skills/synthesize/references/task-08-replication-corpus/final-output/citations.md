# Citations Registry

Run: `task-08-replication-20260501-021500`

Total claims in corpus: 53 | Claims cited in report or ADRs: 53


## Cited claims

| Claim ID | Source URI | Source provenance | Verdict | Snippet |
|---|---|---|---|---|
| C-0001 | [synthesis-pipeline-technical-design.md](/mnt/user-data/uploads/synthesis-pipeline-technical-design.md) | internal | verified | The synthesis pipeline realizes six phases — Extractor, Grap... |
| C-0002 | [synthesis-pipeline-technical-design.md](/mnt/user-data/uploads/synthesis-pipeline-technical-design.md) | internal | verified | Long-running, deterministic, multi-tenant production executi... |
| C-0003 | [synthesis-pipeline-technical-design.md](/mnt/user-data/uploads/synthesis-pipeline-technical-design.md) | internal | verified | Deterministic replay is out of scope because Claude Code is ... |
| C-0004 | [synthesis-pipeline-technical-design.md](/mnt/user-data/uploads/synthesis-pipeline-technical-design.md) | internal | verified | The slash command /synthesize is a thin entry point that cap... |
| C-0005 | [synthesis-pipeline-technical-design.md](/mnt/user-data/uploads/synthesis-pipeline-technical-design.md) | internal | verified | The slash command pattern matches tell-microsoft-joke.md at ... |
| C-0006 | [synthesis-pipeline-technical-design.md](/mnt/user-data/uploads/synthesis-pipeline-technical-design.md) | internal | verified | On invocation, the orchestrator derives a run-id of the form... |
| C-0007 | [synthesis-pipeline-technical-design.md](/mnt/user-data/uploads/synthesis-pipeline-technical-design.md) | internal | verified | Input discovery uses Glob output/**/*.md for prior research ... |
| C-0008 | [synthesis-pipeline-technical-design.md](/mnt/user-data/uploads/synthesis-pipeline-technical-design.md) | internal | verified | The Confirmation Gate is a required AskUserQuestion interrup... |
| C-0009 | [synthesis-pipeline-technical-design.md](/mnt/user-data/uploads/synthesis-pipeline-technical-design.md) | internal | verified | If the user dismisses the Confirmation Gate card with empty ... |
| C-0010 | [synthesis-pipeline-technical-design.md](/mnt/user-data/uploads/synthesis-pipeline-technical-design.md) | internal | verified | Confirmed inputs and constraints are persisted to working/sy... |
| C-0011 | [synthesis-pipeline-technical-design.md](/mnt/user-data/uploads/synthesis-pipeline-technical-design.md) | internal | verified | The orchestrator passes only the run-id and the previous-pha... |
| C-0012 | [synthesis-pipeline-technical-design.md](/mnt/user-data/uploads/synthesis-pipeline-technical-design.md) | internal | verified | On --resume <run-id>, the orchestrator reads checkpoint.json... |
| C-0013 | [synthesis-pipeline-technical-design.md](/mnt/user-data/uploads/synthesis-pipeline-technical-design.md) | internal | verified | The orchestrator allows at most one Critic-driven retry of E... |
| C-0014 | [synthesis-pipeline-technical-design.md](/mnt/user-data/uploads/synthesis-pipeline-technical-design.md) | internal | single_sourced | User-defined agents are placed at /mnt/user-config/.claude/a... |
| C-0015 | [synthesis-pipeline-technical-design.md](/mnt/user-data/uploads/synthesis-pipeline-technical-design.md) | internal | verified | The synth-extractor agent's tool allowlist is Read, Glob, Gr... |
| C-0016 | [synthesis-pipeline-technical-design.md](/mnt/user-data/uploads/synthesis-pipeline-technical-design.md) | internal | verified | The synth-synthesizer agent cannot fetch sources; its tool a... |
| C-0017 | [synthesis-pipeline-technical-design.md](/mnt/user-data/uploads/synthesis-pipeline-technical-design.md) | internal | verified | The substrate registry is version-pinned with a header such ... |
| C-0018 | [synthesis-pipeline-technical-design.md](/mnt/user-data/uploads/synthesis-pipeline-technical-design.md) | internal | verified | The Substrate agent refuses to emit recommendations if the s... |
| C-0019 | [synthesis-pipeline-technical-design.md](/mnt/user-data/uploads/synthesis-pipeline-technical-design.md) | internal | verified | The input scan is output/**/*.md minus output/synthesis-*/**... |
| C-0020 | [synthesis-pipeline-technical-design.md](/mnt/user-data/uploads/synthesis-pipeline-technical-design.md) | internal | verified | The pipeline uses two memory tiers: a main-agent orchestrato... |
| C-0021 | [synthesis-pipeline-technical-design.md](/mnt/user-data/uploads/synthesis-pipeline-technical-design.md) | internal | single_sourced | Sub-agents do not have a native automatically-loaded memory ... |
| C-0022 | [synthesis-pipeline-technical-design.md](/mnt/user-data/uploads/synthesis-pipeline-technical-design.md) | internal | verified | Knowledge skills are loaded only when the agent reads them, ... |
| C-0023 | [synthesis-pipeline-technical-design.md](/mnt/user-data/uploads/synthesis-pipeline-technical-design.md) | internal | verified | Knowledge skills hold curated taxonomies and rubrics that ra... |
| C-0024 | [synthesis-pipeline-technical-design.md](/mnt/user-data/uploads/synthesis-pipeline-technical-design.md) | internal | verified | The recommended authoring order is to author knowledge skill... |
| C-0025 | [synthesis-pipeline-technical-design.md](/mnt/user-data/uploads/synthesis-pipeline-technical-design.md) | internal | verified | Each Claim record carries an assumed_substrate field that le... |
| C-0026 | [synthesis-pipeline-technical-design.md](/mnt/user-data/uploads/synthesis-pipeline-technical-design.md) | internal | verified | Critic verdicts take one of four values: verified, unverifia... |
| C-0027 | [synthesis-pipeline-technical-design.md](/mnt/user-data/uploads/synthesis-pipeline-technical-design.md) | internal | verified | DecisionFrame's blast_radius takes one of four values: compo... |
| C-0028 | [technical-designer.md](/mnt/user-data/uploads/technical-designer.md) | internal | verified | The Standards Identification Gate must be performed before a... |
| C-0029 | [technical-designer.md](/mnt/user-data/uploads/technical-designer.md) | internal | verified | Project standards are classified as Explicit (documented) or... |
| C-0030 | [technical-designer.md](/mnt/user-data/uploads/technical-designer.md) | internal | verified | Implicit standards require user confirmation before design p... |
| C-0031 | [technical-designer.md](/mnt/user-data/uploads/technical-designer.md) | internal | verified | Quality assurance mechanisms are recorded in the Design Doc ... |
| C-0032 | [technical-designer.md](/mnt/user-data/uploads/technical-designer.md) | internal | verified | Existing Code Investigation must be performed before Design ... |
| C-0033 | [technical-designer.md](/mnt/user-data/uploads/technical-designer.md) | internal | verified | Similar functionality search uses domain, responsibilities, ... |
| C-0034 | [technical-designer.md](/mnt/user-data/uploads/technical-designer.md) | internal | verified | When similar functionality is found, the existing implementa... |
| C-0035 | [technical-designer.md](/mnt/user-data/uploads/technical-designer.md) | internal | verified | When similar functionality is technical debt, an ADR improve... |
| C-0036 | [technical-designer.md](/mnt/user-data/uploads/technical-designer.md) | internal | verified | Investigation results are always included in the Existing Co... |
| C-0037 | [technical-designer.md](/mnt/user-data/uploads/technical-designer.md) | internal | verified | The Fact Disposition Table is the single mechanism that bind... |
| C-0038 | [technical-designer.md](/mnt/user-data/uploads/technical-designer.md) | internal | verified | Each Fact Disposition Table row carries one of four disposit... |
| C-0039 | [technical-designer.md](/mnt/user-data/uploads/technical-designer.md) | internal | verified | When all four reuse-vs-new criteria are satisfied, the exist... |
| C-0040 | [technical-designer.md](/mnt/user-data/uploads/technical-designer.md) | internal | verified | When 3 or more reuse-vs-new criteria fail, a new structure i... |
| C-0041 | [technical-designer.md](/mnt/user-data/uploads/technical-designer.md) | internal | verified | The Agreement Checklist must be performed at the beginning o... |
| C-0042 | [technical-designer.md](/mnt/user-data/uploads/technical-designer.md) | internal | verified | Implementation approach selection runs Phase 1-4 of the impl... |
| C-0043 | [technical-designer.md](/mnt/user-data/uploads/technical-designer.md) | internal | verified | Vertical Slice means complete by feature unit with minimal e... |
| C-0044 | [technical-designer.md](/mnt/user-data/uploads/technical-designer.md) | internal | verified | Horizontal Slice means implementation by layer with importan... |
| C-0045 | [technical-designer.md](/mnt/user-data/uploads/technical-designer.md) | internal | verified | Verification Strategy must include target comparison, method... |
| C-0046 | [technical-designer.md](/mnt/user-data/uploads/technical-designer.md) | internal | verified | An early verification point defines the first thing to verif... |
| C-0047 | [technical-designer.md](/mnt/user-data/uploads/technical-designer.md) | internal | verified | For replacements or modifications, the early verification po... |
| C-0048 | [technical-designer.md](/mnt/user-data/uploads/technical-designer.md) | internal | verified | ADRs include decisions, rationale, and principled guidelines... |
| C-0049 | [technical-designer.md](/mnt/user-data/uploads/technical-designer.md) | internal | verified | ADRs exclude schedules, implementation procedures, and speci... |
| C-0050 | [technical-designer.md](/mnt/user-data/uploads/technical-designer.md) | internal | verified | ADR option comparison requires a minimum of 3 options. |
| C-0051 | [technical-designer.md](/mnt/user-data/uploads/technical-designer.md) | internal | verified | Architecture and data flow diagrams are mandatory in Design ... |
| C-0052 | [technical-designer.md](/mnt/user-data/uploads/technical-designer.md) | internal | verified | Acceptance criteria must be written in testable format with ... |
| C-0053 | [technical-designer.md](/mnt/user-data/uploads/technical-designer.md) | internal | verified | Output comparison method specifies identical input, expected... |

## Uncited claims (in corpus but not surfaced in report)

Total uncited: 0. Uncited claims do not violate the citation invariant — they were extracted but did not enter the surfaced findings or decisions for the `narrow` scope.

