---
version: 2026-04-30.1
target: claude_code
maintained_by: synthesize skill
review_cadence: 90 days
---

# Substrate Registry: Claude Code

> **Purpose:** Catalog of available primitives in the Claude Code substrate. Consumed by `synth-substrate` (via `substrate-translation-knowledge` skill) when enumerating native / adapter / substrate-change options for each architectural decision in `04-decision-frames.json`.
>
> **Consumers:** `synth-substrate` agent reads this file at task start (loaded via `skills: [substrate-translation-knowledge]` per Design §4.12 footnote).
>
> **Staleness gate:** if the `version:` header date is more than 90 days older than the run's `started_at`, the Substrate phase refuses to emit and surfaces an `AskUserQuestion` to refresh the registry (Design §8 row).

---

## Contents

- Section 1 — Translation Table (research-pipeline patterns ↔ Claude Code primitives)
- Section 2 — Primitive Catalog (skills, sub-agents, hooks, MCP, slash commands, file-system layout, MEMORY, Tasks, AskUserQuestion, ExitPlanMode)
- Section 3 — Known Unmappable Patterns (declared cycles, typed state, deterministic replay, structured event bus)
- Section 4 — Naming Convention (multi-target deployments)
- Maintenance Discipline (review cadence, version bump, change log)

## Section 1 — Translation Table

The following table maps research-pipeline coordination patterns (drawn from the constraint-aware-synthesis source document §4) to their Claude Code substrate equivalents. Three patterns from the source do not translate cleanly and are recorded in Section 3.

| Coordination pattern | Claude Code primitive | Notes |
|---|---|---|
| Multi-agent orchestration with role specialization | Sub-agents via Task tool with `subagent_type` | Each role gets a dedicated `agents/<role>.md` file; parallelism via repeated Task invocations |
| Knowledge-grounded reasoning | Skills with `references/` directories | Knowledge skills carry taxonomies/rubrics; loaded by agents via `skills:` frontmatter |
| Structured artifact handoff between phases | File-system-as-state (working/ directory) | Each phase writes JSON/MD artifacts; downstream phases Read them; orchestrator never passes raw text through context |
| Iteration with bounded retry | Orchestrator-side counter (`params.max_iterations`) + `checkpoint.json` `retries.*` fields | Counter enforced by orchestrator; agents are stateless |
| Human-in-the-loop confirmation | `AskUserQuestion` interrupts | Three concurrent questions per Design §4.10 Confirmation Gate; cancellation = empty answers |
| Persistent observations across runs | `MEMORY.md` + `.memories/` (main agent + sub-agent memories) | Read-on-demand; append-only writes; routing rule per Design §4.6.2 |
| Progress surfacing during long runs | `TaskCreate` / `TaskUpdate` | One task per phase per run; the conversational chat does not replace this |
| Validation at phase boundaries | `PostToolUse` hooks ✅ (probe-pending) + in-skill validator fallback | Hook availability probe — Design §11 step 6 / task-23 |
| Run startup orientation | `SessionStart` hook ✅ (confirmed) + `MEMORY.md` autoload | Loads substrate-registry version banner into session context |
| Slash command entry | `commands/*.md` (≤30-line discipline) | the synthesize slash command is the entry point; mirrors the tell-microsoft-joke pattern |

## Section 2 — Primitive Catalog

### Skills

- **Authored knowledge skills** — `skills/<name>/SKILL.md` with `user-invocable: false, implicit: false` frontmatter; carry curated taxonomies, rubrics, examples, anti-patterns. Loaded by agents via `skills:` frontmatter list.
- **Orchestrator skill** — this skill's own SKILL.md carries the orchestration contract block, schemas reference, phase invocation table, hard exclusions, error-handling per phase.
- **Skill references** — `references/` subdirectory; supplemental files consulted on demand by the agent reading the skill (not loaded eagerly).

### Sub-agents (via Task tool)

- **Definition file** — `/mnt/user-config/.claude/agents/<name>.md` with frontmatter: `name`, `description`, `model`, `tools` (allowlist), `skills` (loaded at task start).
- **Invocation** — orchestrator calls `Task(subagent_type='<name>', description='...', prompt='...')`. Each invocation runs in an isolated context window per Design §4.11.
- **Context budget** — orchestrator passes file *paths*, not file *contents*; the sub-agent reads what it needs.

### Hooks (settings.json)

| Event | Status | Confirmed by |
|---|---|---|
| `SessionStart` | ✅ available | Design §4.7 |
| `PostToolUse` | ⚠️ probe-pending | task-23 (Design §11 step 6) |
| `PreToolUse` | ⚠️ probe-pending | task-23 |
| `Stop` | ⚠️ probe-pending | task-23 |
| `SubagentStop` | ⚠️ probe-pending | task-23 |

For probe-pending events, `synthesize` skill ships **in-skill fallbacks** (Layer A schema validators in agent bodies; Layer B citation/constraint/recursion/three-option validators in orchestrator and `synth-synthesizer`). If the probe (task-23) confirms availability, fallbacks remain in place per Design §4.7 robustness principle.

### MCP servers

Available for external integrations. Synthesize skill does not currently declare MCP server requirements — all I/O is to the local file system.

### Scheduled prompts

`SetupScheduledPrompt` is available for recurring runs. Out of scope for this initial implementation per Design §9 Q4 (deferred).

### Slash commands

`commands/<name>.md` — ≤30-line discipline. Entry point that loads and executes a target skill. the synthesize slash command is this pipeline's entry point.

### File-system layout (per Design §4.5)

```
output/                     # human-readable artifacts; read-only consumption + write of synthesis outputs
  synthesis-<topic>/        # synthesis run outputs (excluded from input scan to prevent recursion)
    report.md
    citations.md
    substrate-options.md
    adrs/
      ADR-001-<slug>.md
input/                      # user-supplied inputs; secondary scan when added_from_input populated
working/synthesis/<run-id>/ # phase-artifact storage; ephemeral but checkpointable
  00-manifest.json
  01-claims.json
  02-graph.json
  03-critique.json
  04-decision-frames.json
  05-substrate-map.json
  checkpoint.json
.memories/                  # append-only persistent observations
  synthesis-*.md            # main-agent memory entries
  agents/<agent-name>/      # sub-agent memory directories
```

### MEMORY.md / .memories/

- **`MEMORY.md`** — autoloaded at session start. Contains pointers to `.memories/synthesis-*.md` files.
- **`.memories/synthesis-*.md`** — main-agent persistent observations (substrate registry pointer, conventions, prior-runs index, knowledge-skills index).
- **`.memories/agents/<name>/`** — per-sub-agent memory; agent reads ≤1–2K tokens at task start; agent appends a single bullet at task end *only if* a non-obvious learning emerged.

### TaskCreate / TaskUpdate

Surface long-running pipeline progress to the user. One TaskCreate per pipeline run with sub-task updates per phase. Sub-agents call `TaskUpdate` from inside their bodies.

### AskUserQuestion

Mandatory at the Confirmation Gate (Design §4.2 step 3). Optional escalation paths in Critic (`when a critical claim has irreconcilable conflicts`) and Substrate (`when all three options viable`) phases.

### ExitPlanMode

Available; not currently used by `synthesize` skill (this pipeline is implementation, not planning).

## Section 3 — Known Unmappable Patterns

The following coordination patterns do **not** translate cleanly to Claude Code primitives. They are surfaced for transparency and feed into the "honest gaps" table in Design Doc §6.

1. **Declared cycles** — graph frameworks support `cycle: bool` declarations on edges; Claude Code's primitive set does not. Workaround: orchestrator-side counter with explicit termination condition (used for Critic-driven Extractor retry and Substrate-driven Framer retry).

2. **Typed state schemas at the framework level** — frameworks like LangGraph type-check state transitions at compile time. Claude Code uses file-system-as-state, with JSON Schema validators (Layer A) running at phase boundaries. Equivalent correctness, later detection.

3. **Deterministic replay** — frameworks support replay from a state snapshot for testing. Claude Code's checkpoint.json supports resume but not replay (LLM non-determinism). Verification strategy compensates: Layer C smoke runs use ±10% tolerance rather than bit-exact match (Design §7.2).

4. **Structured event bus** — pub/sub over coordination events. Claude Code has hooks (event-on-tool-use) but not generic pub/sub. Out of scope for this pipeline.

## Section 4 — Naming Convention (multi-target deployments)

This registry file is named `substrate-registry.md` for **single-substrate** deployments (the default; this file's `target: claude_code` declares the substrate).

For **multi-substrate** deployments (where one tenant runs synthesis pipelines targeting multiple substrates), additional registry files are added with the convention `substrate-registry-<target>.md` where `<target>` matches `manifest.constraints.target_substrate` values per Design §5.6 (e.g., `substrate-registry-microsoft-azure.md`, `substrate-registry-m365.md`).

The orchestrator (per task-05) selects the correct registry file at run start: it reads `manifest.constraints.target_substrate`, then loads `references/substrate-registry-<target>.md` if present, falling back to `references/substrate-registry.md` if no `<target>`-specific file exists.

This convention closes Document Reviewer issue I015 (latent §4.4/§4.3/§4.5 inconsistency in the design doc).

## Maintenance Discipline

- **Review cadence:** every 90 days, or whenever Claude Code adds/removes a primitive that materially changes the catalog.
- **Version bump:** `version: YYYY-MM-DD.<n>` on every meaningful update; staleness gate compares this date to the run's `started_at`.
- **Change log:** record material changes inline at the top of the next section to be edited (no separate change-log file).
