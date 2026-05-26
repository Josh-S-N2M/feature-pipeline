---
id: RP-pipeline-quickwins-hardening-r1
version: 1.0.0
status: draft
feature_slug: pipeline-quickwins-hardening-r1
doc_type: research-plan
derived_from: working/feature/pipeline-quickwins-hardening-r1/prd-v1.md
generated: 2026-05-25T00:00:00Z
generated_by: discovery-plan-author
---

# Research Plan: Pipeline Quick-Wins Hardening (Round 1)

## Contents

- [x] Feature reference
- [x] Information needs inventory
- [x] Codebase research scope
- [x] External research topics
- [x] Topics explicitly NOT researched
- [x] Estimated effort
- [x] Open questions for human resolution

## Feature reference

- **Feature slug**: `pipeline-quickwins-hardening-r1`
- **PRD path**: `working/feature/pipeline-quickwins-hardening-r1/prd-v1.md`
- **PRD version**: 0.2.0
- **PRD gate state**: approved at PRD Approval Gate (Gate 2) on 2026-05-25 with user token `gate1-approved-as-is-20260525T2218Z`; the PRD adopted Undetermined Item U-8 (concrete latency thresholds) as part of the gate-approval condition set.
- **Scope class**: MINOR (per PRD Product Policy Decisions).
- **Layers in scope** (per PRD Layer Scope): Claude Code / Project Filesystem; CI/CD (GitHub Actions); Codespaces / Devcontainer. The other six layers are out of scope.
- **Inherited ADRs in scope** (those that constrain or inform research scope):
  - ADR-0017 — reviewer-invocation discipline (context for FR-1).
  - ADR-0021 — Discovery-phase architecture (the KB-and-ADR-first protocol this plan implements).
  - ADR-0029 / ADR-0033 — no-silent-scope-changes principle (constrains how mechanisms surface diagnostics).
  - ADR-0037 — `mcp-events.jsonl` event surface (constraint for NFR-13 on FR-3/4/5).
  - ADR-0039 — credential-redaction posture (constraint for NFR-7/NFR-8 across all mechanisms).
  - ADR-0040 — Serena narrowed-always-on allowlist precedent (cited by NFR-15; no change required).
  - ADR-0041 — install-mechanism hybrid + per-server invocation taxonomy (the comparison target for FR-3).
  - ADR-0042 — `auditing-mcp` family graduation (FR-3 extends this family).
  - ADR-0043 — `auditing-mcp` Gate-6 hard gate (context for where FR-3 lands).
  - ADR-0044 — flatten-execution-dispatch (informs where the FR-2 self-check can live: parent orchestrator vs advisor agent).
- **Applicable KBs**:
  - KB-cc-platform / KB-cc-design — primitive selection, agent contract surface (FR-1, FR-2).
  - KB-mcp-platform / KB-mcp-design — the six MCP servers, `.mcp.json` shape, ADR-0041 cross-reference (FR-3, FR-5).
  - KB-github-actions-platform / KB-github-actions-design — workflow primitives, security non-negotiables, audit script (FR-5).
  - KB-codespaces-platform / KB-codespaces-design — devcontainer lifecycle hooks, `postCreate.sh` placement (FR-4).
  - KB-review-disciplines — severity taxonomy, verdict-to-issue mapping, Gate 0/1 procedure (FR-1).
  - KB-documentation-criteria — frontmatter conventions, EARS, deliverable-archive spec (FR-7 + diagnostic format).
  - auditing-mcp (skill) — existing OP-1..OP-10 rule structure, audit script entry point (FR-3 extends this).

## Information needs inventory

Each row is a fact a downstream sub-agent will need to make its decision. The five-way disposition triage (per the Discovery Planning discipline) is applied to each: covered-by-KB / covered-by-ADR / codebase-topic / designer-general-knowledge / external-research-topic. Per ADR-0021, external research is conditional on a documented gap.

### FR-1 (Verdict-vs-findings consistency check)

| Need ID | Description | Downstream consumer(s) | Disposition |
|---|---|---|---|
| IN-001 | What is the current verdict/findings output shape (JSON schema, severity tokens, file path conventions) emitted by `shared-document-reviewer`, `review-architecture-auditor`, `review-cross-artifact-auditor`, and `execute-phase-quality-reviewer`? | design-claude-code (chooses in-agent vs out-of-agent check site; closes A-4 + U-1) | `codebase-topic` |
| IN-002 | What does the project's canonical severity taxonomy say is "blocking" — which severity tokens correspond to a critical/blocking finding, and what verdicts are "approving"? | design-claude-code (defines the blocking-severity set for U-1) | `covered-by-KB:KB-review-disciplines:references/severity-taxonomy.md` |
| IN-003 | What is the existing Gate 0/1 reviewer procedure and how does it currently couple verdicts to severities? | design-claude-code (places the new check inside or alongside the existing procedure) | `covered-by-KB:KB-review-disciplines:references/gate-0-1-procedure.md` |
| IN-004 | What are the consumers of the reviewer output today (which orchestrator stage, which downstream agent reads the verdict) — needed to choose between in-agent self-check vs out-of-agent gate? | design-claude-code | `codebase-topic` |
| IN-005 | Which Claude Code primitive (hook, skill, sub-agent step, plain orchestrator code) should host an output-shape validator, given context-cost and enforce-vs-instruct discipline? | design-claude-code (closes U-1's "in-agent vs out-of-agent" sub-question) | `covered-by-KB:KB-cc-design:references/patterns-and-anti-patterns.md` |

### FR-2 (Orchestrator dispatch self-check refuses FULL-scope + single-agent-fallback)

| Need ID | Description | Downstream consumer(s) | Disposition |
|---|---|---|---|
| IN-006 | How does the feature-pipeline orchestrator currently dispatch per-stage agents — what's the configuration surface, where is "per-stage agent choice" expressed, where (if anywhere) is "single-agent fallback" identifiable? | design-claude-code (closes A-5 + U-2) | `codebase-topic` |
| IN-007 | How does the orchestrator currently learn the feature's scope class (MINOR / FULL / PATCH), and where in the dispatch flow is the earliest correct point to place a self-check? | design-claude-code | `codebase-topic` |
| IN-008 | Is there an existing hook / gate / skill point the self-check should attach to (vs introducing a new one) — given ADR-0044's flatten posture? | design-claude-code | `covered-by-ADR:ADR-0044` |
| IN-009 | What's the canonical "enforce vs instruct" choice for a refuse-to-dispatch behavior — hook with non-zero exit, permission-deny rule, or orchestrator-internal logic? | design-claude-code | `covered-by-KB:KB-cc-design:references/principles.md` |

### FR-3 (`.mcp.json` ↔ ADR-0041 parity audit rule)

| Need ID | Description | Downstream consumer(s) | Disposition |
|---|---|---|---|
| IN-010 | What invocation form does ADR-0041 prescribe for each of the six currently-registered servers (argv strings, env-var indirection, sentinel paths)? | design-claude-code (the parity comparison target; closes A-1) | `covered-by-ADR:ADR-0041` |
| IN-011 | What is the current shape of `.mcp.json` — the live invocation form for each server (argv, env block, transport, headers)? | design-claude-code | `codebase-topic` |
| IN-012 | How is the existing `auditing-mcp` skill organized — where do OP rules live, what's the audit-script entry-point, what's the established convention for adding an OP rule? | design-claude-code (where FR-3 lands as a new rule) | `codebase-topic` |
| IN-013 | What canonicalization rules already exist for env-var indirection in the audit ruleset (OP-9 URL-credential rejection, OP-10 argv-leakage) that the FR-3 comparison should be consistent with? | design-claude-code (closes U-3 normalization sub-question) | `covered-by-KB:KB-mcp-design:references/principles.md` |
| IN-014 | What does ADR-0042/ADR-0043 say about the gate at which `auditing-mcp` runs, so the new rule's blocking-finding behavior is consistent? | design-claude-code | `covered-by-ADR:ADR-0042` (family graduation) + `covered-by-ADR:ADR-0043` (Gate-6 hard gate) |
| IN-015 | What comparison-algorithm choice (exact-string vs canonicalized form) does the project already use elsewhere for invocation-form-equality checks (if any)? | design-claude-code | `codebase-topic` |

### FR-4 (GitNexus install dry-run in devcontainer post-create)

| Need ID | Description | Downstream consumer(s) | Disposition |
|---|---|---|---|
| IN-016 | What is the current shape of `.devcontainer/postCreate.sh` — the GitNexus install commands, the env-var export, the sentinel pattern, the exit-code conventions? | design-codespaces (closes A-2 + U-4) | `codebase-topic` |
| IN-017 | What is the pinned GitNexus tag in `.devcontainer/versions.env`, and what's the precedent for "drift detected, halt with diagnostic" behavior in this script? | design-codespaces | `codebase-topic` |
| IN-018 | Where in the lifecycle hooks (`onCreateCommand` / `postCreateCommand` / `postStartCommand`) should the dry-run live — given prebuild-capture posture and ADR-0041's existing placement? | design-codespaces | `covered-by-KB:KB-codespaces-design:references/principles.md` + `covered-by-ADR:ADR-0041` |
| IN-019 | What is the `GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1` env-var contract supposed to do at the pinned GitNexus tag — what positive assertion should the dry-run make to detect contract breakage (not just absence-of-error)? | design-codespaces (the positive-assertion shape directly closes the FR-4 risk row about silent dry-run passes) | `external-research-topic:T-001` |
| IN-020 | What's the project's existing convention for shell-script diagnostic messages on dry-run failure (NFR-6 fail-closed-on-internal-error)? | design-codespaces (closes U-4 diagnostic message text) | `codebase-topic` |

### FR-5 (CI workflow for `claude mcp list` connectivity smoke)

| Need ID | Description | Downstream consumer(s) | Disposition |
|---|---|---|---|
| IN-021 | What is the existing `.github/workflows/` directory and existing GitHub Actions discipline in this project (workflows, naming, runner choice, secret model)? | design-cicd (closes baseline for U-5) | `codebase-topic` |
| IN-022 | What are the non-negotiable security rules for adding a new workflow (SHA-pinning, least-privilege `permissions:`, OIDC, secret scoping)? | design-cicd | `covered-by-KB:KB-github-actions-platform:references/security.md` + `covered-by-KB:KB-github-actions-design:references/principles.md` |
| IN-023 | What event-trigger patterns and path-filter mechanics does GitHub Actions offer (`pull_request.paths`, branch filters), and how should the FR-5 path-trigger set be expressed? | design-cicd (closes U-5 path-trigger set) | `covered-by-KB:KB-github-actions-platform:references/events-and-triggers.md` |
| IN-024 | What is the exit-code and output-format contract of `claude mcp list` — does it return non-zero on any non-connected server, and is the per-server connectivity status surfaced in stdout/stderr in a parseable form? | design-cicd (closes A-3 + the FR-5 risk row about misreading "non-connected"; load-bearing for the workflow's pass/fail logic) | `external-research-topic:T-002` |
| IN-025 | Which execution environment is appropriate — clean GitHub-hosted runner with `claude` CLI installed inline, vs. running against the PR's devcontainer image? Trade-offs in NFR-4 runtime budget vs fidelity to the devcontainer's MCP state? | design-cicd (closes U-5 environment choice) | `covered-by-KB:KB-github-actions-design:references/patterns-and-anti-patterns.md` + `designer-general-knowledge` (the trade-off itself is a standard "fidelity vs runtime" workflow design call) |
| IN-026 | What is the existing project's convention for installing the `claude` CLI in a GitHub Actions runner, if any (devcontainer install precedents in `.devcontainer/postCreate.sh`, version pins in `versions.env`)? | design-cicd | `codebase-topic` |

### FR-6 (Actionable diagnostics) and FR-7 (Deferral-register update)

| Need ID | Description | Downstream consumer(s) | Disposition |
|---|---|---|---|
| IN-027 | What's the existing diagnostic-format precedent across the four affected reviewer agents, the `auditing-mcp` script outputs, and the post-create shell scripts — so FR-6's "mechanism name + offending path + rule + remedial hint" template can be consistent with what's already in flight? | design-composer (cross-cutting FR-6 enforcement); each per-layer designer applies | `codebase-topic` |
| IN-028 | What is the current state of `Issues/devcontainer-mcp-provisioning-r1-deferrals/register.md` — the row format, the adopted-by field, the deferral-row-update convention from prior features? | design-claude-code (closes U-7) | `codebase-topic` |
| IN-029 | What is the canonical deliverable-archive layout (FR-7's "deliverable archive vs separate housekeeping commit" decision touches this)? | design-composer | `covered-by-KB:KB-documentation-criteria:references/deliverable-archive-spec.md` |

### Cross-cutting (NFR-13 event-surface compatibility, NFR-15 allowlist preservation)

| Need ID | Description | Downstream consumer(s) | Disposition |
|---|---|---|---|
| IN-030 | Does the `.claude/runtime/mcp-events.jsonl` event surface have an existing schema that the FR-3/4/5 diagnostics must not perturb, and what event types are already defined? | design-claude-code, design-codespaces, design-cicd (NFR-13 acceptance) | `covered-by-KB:KB-mcp-platform:references/mcp-events-jsonl.md` + `covered-by-ADR:ADR-0037` |
| IN-031 | Does the existing MCP-server allowlist (per ADR-0040) need any change to accommodate any new mechanism? | design-claude-code (NFR-15 acceptance) | `covered-by-ADR:ADR-0040` (precedent confirms no change required for this MINOR-scope feature) |

## Codebase research scope

This section is the contract with `discovery-codebase-researcher`. Per the Discovery Planning discipline, codebase research is always non-empty; for this feature it is the dominant research mode because the artifact under modification *is* the project's own pipeline machinery.

### Touch points

- `.claude/agents/shared-document-reviewer.md` — reviewer agent contract (FR-1).
- `.claude/agents/review-architecture-auditor.md` — reviewer agent contract (FR-1).
- `.claude/agents/review-cross-artifact-auditor.md` — reviewer agent contract (FR-1).
- `.claude/agents/execute-phase-quality-reviewer.md` — reviewer agent contract (FR-1; also emits a verdict-shaped output).
- `.claude/agents/execute-orchestrator.md` — orchestrator state-machine reference (FR-2 self-check candidate site).
- `.claude/skills/recipe-feature-pipeline/SKILL.md` (and any associated dispatch logic) — the actual parent orchestrator per ADR-0044 (FR-2 self-check candidate site).
- `.claude/skills/auditing-mcp/SKILL.md` and `.claude/skills/auditing-mcp/scripts/audit_mcp.py` plus the existing `audit_op*.py` scripts — host for the new FR-3 rule.
- `.claude/skills/auditing-mcp/references/` (mcp-spec, anti-patterns, etc.) — for placement of FR-3's prescription-vs-realization rationale.
- `.mcp.json` (project root) — the live artifact compared by FR-3 and probed by FR-5.
- `.devcontainer/postCreate.sh` — host for the FR-4 dry-run.
- `.devcontainer/versions.env` — the pinned GitNexus tag (FR-4 reads).
- `.devcontainer/Dockerfile` — adjacent context (FR-4 confirms no Dockerfile change required per ADR-0041's "no new Dockerfile" posture).
- `.devcontainer/lib/log-mcp-event.sh` — diagnostic-emission helper (FR-4 + NFR-13 compatibility).
- `.github/workflows/` — currently empty; FR-5 introduces the first workflow. Researcher should confirm absence and report the empty state.
- `Issues/devcontainer-mcp-provisioning-r1-deferrals/register.md` — FR-7 target artifact (current row format, the H-4 and B-1 entries).
- `Issues/cross-artifact-divergence-detection-gap/proposal.md` — seed issue-proposal (status `adopted` per ADR-0048; researcher should confirm).
- `adrs/ADR-0041-install-mechanism-hybrid.md` — FR-3 comparison target (researcher pulls the per-server invocation table into a structured form so design-claude-code can compare).

### Blast-radius questions

Per ADR-0018, blast-radius captured in `codebase-analysis.json`'s `blast_radius` section.

- **For each reviewer agent file** (the four named in touch-points): which orchestrator stages invoke it, and which downstream consumers parse its output? 1-hop callers; 3-hop reachability via `recipe-feature-pipeline/SKILL.md`'s dispatch.
- **For `execute-orchestrator.md` + `recipe-feature-pipeline/SKILL.md`**: what stages of the pipeline run the dispatch loop, and where is the scope-class read? 3-hop reachability into the per-stage agents.
- **For `auditing-mcp/SKILL.md`**: which sub-agents preload this skill, and which Gate runs the audit (per ADR-0043 Gate-6)? 1-hop.
- **For `.devcontainer/postCreate.sh`**: what tests / smokes / events does it emit today (the existing `install_complete` JSONL records per ADR-0037), so FR-4's dry-run insertion preserves them?
- **For `.mcp.json`**: which agents have `mcp__*__*` allowlist entries that depend on the server set in this file (per ADR-0040)? Needed to confirm NFR-15 (no allowlist changes required).

### Convention discovery

Per-layer conventions the design must respect:

- **Claude Code layer**: reviewer-agent frontmatter shape (the `tools:`, `skills:`, `model:`, `effort:` fields); the established Gate 0/1 procedure's place in agent body templates; sub-agent reasoning-configuration conventions per ADR-0022; the `TaskCreate` / `TaskUpdate` discipline; the established convention for "report-only" vs "enforcing" agents.
- **`auditing-mcp` skill convention**: how OP-1..OP-10 rules are named, where their detection scripts live, how the audit-script aggregates findings, how findings are serialized (JSON format, severity labels), and how the skill's `references/` documents the rule rationale.
- **Devcontainer layer**: sentinel naming (per ADR-0041's `<server>@<version>.installed` convention); `log_mcp_event` helper usage; `set -euo pipefail` posture; the convention for emitting one diagnostic line per install vs structured JSONL.
- **CI/CD layer**: this is a greenfield workflow directory. The convention is established by KB-github-actions-{platform,design} non-negotiables (SHA-pin, least-privilege permissions, no untrusted input interpolation, OIDC where applicable, concurrency on deploy workflows — though FR-5 is not a deploy workflow). The researcher should confirm absence of any `.github/workflows/` precedent in this project, so the designer chooses the workflow's shape from scratch.

### Specific queries or grep targets

- For FR-1: `rg -n 'verdict' .claude/agents/{shared-document-reviewer,review-architecture-auditor,review-cross-artifact-auditor,execute-phase-quality-reviewer}.md` — find the verdict-emission contract in each reviewer's body.
- For FR-1: locate any JSON-schema or schema-prose for reviewer-output JSON; check `KB-review-disciplines/references/` and `auditing-shared` (per ADR-0031, the shared rubric lives there).
- **For FR-1 (scope-completeness sweep — per Gate-3 user direction):** scan the full `.claude/agents/` inventory for *any* agent whose contract emits a verdict-plus-findings pair, beyond the four named in the PRD. Queries: `rg -nl 'verdict.*:' .claude/agents/` followed by per-hit inspection of the agent's output contract. Also check for less-obvious patterns: `rg -n 'findings.*\[\]|findings.*:' .claude/agents/`. If any additional reviewer-shaped agents are found, surface them in the codebase-analysis report as a `scope_completeness_finding` so design-claude-code can update FR-1's scope (and the PRD if needed) before the parity rule is authored. The intent doc framing ("any reviewer that emits a verdict+findings pair") is binding; the four PRD-named agents are illustrative, not exhaustive.
- **For FR-3 (deprecated-row confirmation — per Gate-3 user direction):** confirm via git history that `mcp-openapi-schema` was removed from `.mcp.json` and the devcontainer's `postCreate.sh` server set on 2026-05-24 (commit `c53631b` captures the KB-mcp 7→6 transition; prior commit removed the server). Once confirmed, surface for design-claude-code's consumption: ADR-0041's invocation table still lists this server, so FR-3's parity-rule design must handle deprecated ADR rows (either by recognizing a status marker on the ADR row, by amending ADR-0041 to remove the deprecated row, or by another mechanism the designer chooses). This is a design decision routed via U-3, not new external research.
- For FR-2: `rg -n 'scope_class|SCOPE_CLASS|FULL|MINOR' .claude/skills/recipe-feature-pipeline/` — find the scope-class consumption point.
- For FR-2: `rg -n 'single.?agent|fallback' .claude/skills/recipe-feature-pipeline/ .claude/agents/execute-orchestrator.md` — find any existing "single-agent fallback" language.
- For FR-3: read `.claude/skills/auditing-mcp/scripts/audit_op*.py` to inventory how an existing OP rule is structured (entrypoint signature, finding-emission convention, severity assignment).
- For FR-3: structured-extract the per-server invocation table from ADR-0041 (the table in Section 1 of Decision) into a JSON-shaped artifact for design-claude-code to consume.
- For FR-4: `rg -n 'GITNEXUS_SKIP_OPTIONAL_GRAMMARS|gitnexus' .devcontainer/postCreate.sh .devcontainer/versions.env adrs/ADR-0041-install-mechanism-hybrid.md` — find every existing reference to the contract and the pin.
- For FR-5: confirm `.github/workflows/` is empty (`ls .github/workflows/ 2>/dev/null`); confirm absence of any `claude mcp list` precedent (`rg -n 'claude mcp list' .` — full-tree, expect zero hits outside the PRD/IC).
- For FR-7: `cat Issues/devcontainer-mcp-provisioning-r1-deferrals/register.md` — read the H-4 and B-1 rows and the register's row-update convention.

## External research topics

Per ADR-0021 and the Discovery Planning discipline, external research is conditional on documented KB gaps. The default budget is 6 topics; this plan proposes **2 topics** — a positive design state, not a gap. The remaining information needs are resolved by the KBs and ADRs above or by codebase research.

### T-001: GitNexus `GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1` contract — positive-assertion shape at the pinned tag

- **Topic ID**: T-001
- **Name**: GitNexus optional-grammar-skip env-var contract.
- **Research question**: At the GitNexus tag currently pinned in `.devcontainer/versions.env`, what specifically does `GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1` cause the install to do (and to NOT do — particularly the C++/tree-sitter toolchain path) — such that a dry-run can make a positive assertion that the contract still holds rather than relying on absence-of-error?
- **KB gap justification**: KB-mcp-platform documents the env-var's existence (`npx -y gitnexus@${GITNEXUS_TAG} mcp` with `GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1`) and notes its load-bearing role in suppressing the C++ toolchain build (ADR-0041 v1.0.1 cycle-3 D-3.2 F2 makes the same statement). However, neither the KB nor ADR-0041 pin down the **observable signal** of the env-var honoring its contract — i.e., what does a successful skip look like in install output / process tree / file-system state, distinct from a no-op? This is precisely the positive-assertion FR-4's risk row demands. The question cannot be answered by reading the KB alone; the answer lives in GitNexus's upstream source at the pinned tag. It is not `designer-general-knowledge` because the answer is specific to a particular upstream project at a particular pin, not industry-standard knowledge a competent designer would carry. It is not `codebase-topic` because the answer depends on GitNexus's upstream behavior, not this project's code.
- **Acceptance criteria**:
  - Identifies the specific code path / install step in GitNexus at the pinned tag that the env-var gates (file/line citation, or "documented in upstream README/CHANGELOG section X" citation).
  - Names at least two observable signals that the dry-run can assert (e.g., "process tree contains no `cc` / `g++` / `tree-sitter-cli` invocation"; "no `*.so` artifact is produced under `node_modules/gitnexus/...`"; "the install completes within N seconds"). At least one must be a positive assertion (something IS present) rather than absence (something is NOT present), to defend against the contract being silently disabled.
  - Names at least one drift mode — i.e., what an upstream change at a future tag could plausibly break the contract through, so the dry-run is forward-compatible.
- **Source constraints**: GitNexus upstream repository at the pinned tag (the npm package and the GitHub repo it derives from); upstream changelog / release notes; the upstream README. If those are silent, GitNexus issue tracker for any historical bug or PR that introduced or modified the env-var behavior. No third-party tutorials or blog posts.

### T-002: `claude mcp list` CLI — exit-code semantics and output format

- **Topic ID**: T-002
- **Name**: Claude Code `claude mcp list` CLI contract.
- **Research question**: What is the documented exit-code and output-format contract of `claude mcp list` — specifically, does it return non-zero when any registered MCP server is non-connected, and is per-server connection status (connected vs not-connected) emitted in stdout/stderr in a stable, parseable form that a GitHub Actions workflow can grep / jq?
- **KB gap justification**: KB-cc-platform documents the existence of Claude Code's CLI primitives and the `mcp` family of commands, and notes that `/mcp` (the slash command, in-session) shows connected servers and per-server token cost. The KB does NOT, however, pin down the **`claude mcp list`** sub-command's exit-code contract or its output format outside an interactive session. The KB's source-of-truth lookup chain (Context7 with library ID `/websites/code_claude`, fallback to `web_fetch` on `https://code.claude.com/docs/en/cli-reference.md`) is the established way to verify this kind of CLI specific. The PRD's FR-5 makes the workflow's pass/fail logic depend on this contract, and the FR-5 risk row explicitly flags the failure mode where the workflow silently passes when it shouldn't because the contract was misread. This is not `designer-general-knowledge` — Claude Code's CLI is actively evolving and the KB explicitly warns that memory may be stale. It is not `codebase-topic` because the contract lives in the upstream CLI, not the project's code.
- **Acceptance criteria**:
  - Cites the canonical Claude Code documentation page (URL + section heading) describing `claude mcp list` exit-code behavior. If the page is silent on exit-code, says so explicitly and cites the next-best authority (CLI help text from a current binary, source if open).
  - Names the output format (plain text? JSON? table? `--json` flag available?) and gives a parseable-form example.
  - Identifies the exact string or status token used to indicate a non-connected server, so the workflow can match it deterministically.
  - Notes any version-skew risk (e.g., "this contract is stable since Claude Code vX.Y.Z" or "the JSON output mode was added in version Z and may not be present in older runners"), so the designer can pin the Claude Code version in the workflow if needed.
- **Source constraints**: Canonical Anthropic Claude Code documentation only (`https://code.claude.com/docs/`; pages `cli-reference`, `mcp`, `headless`). Context7 library `/websites/code_claude` is the preferred fetch route. If the docs are silent on a specific point, the next-best authority is the `claude --help` and `claude mcp --help` output text from a current binary. No third-party blog posts; no community wiki.

## Topics explicitly NOT researched

Per ADR-0021 and the Discovery Planning discipline, every information need with a non-`external-research-topic` disposition is recorded here for audit. This list is intentionally long: most of this feature's information needs are resolved by the existing KB/ADR corpus and the codebase itself.

| Need ID | Resolving artifact | Resolution summary |
|---|---|---|
| IN-002 | `KB-review-disciplines/references/severity-taxonomy.md` (v1.0.0) | Three severity values (`critical`, `important`, `recommended`); the file states explicitly which verdicts pair with which severity counts. The "blocking-severity set" U-1 asks about is exactly the `critical` row (with the score-to-verdict mapping table). Designer-claude-code reads this directly. |
| IN-003 | `KB-review-disciplines/references/gate-0-1-procedure.md` | Canonical Gate 0 (structural) + Gate 1 (quality) procedure that all five reviewer-invocation points run; the FR-1 check naturally extends Gate 0 (structural-shape consistency) rather than Gate 1 (substantive). |
| IN-005 | `KB-cc-design/references/patterns-and-anti-patterns.md` | The "enforce vs instruct" guidance, plus "hooks cost zero context; deferred MCP tool schemas cost zero until invoked" cost-discipline, plus the explicit anti-pattern "skill duplicating CLAUDE.md" — together they constrain U-1's "in-agent vs out-of-agent" choice. |
| IN-008 | ADR-0044 (flatten-execution-dispatch-hierarchy) v1.0 | Establishes that the parent `recipe-feature-pipeline` orchestrator directly dispatches execution-side specialists (not `execute-orchestrator`). The FR-2 self-check belongs in the parent orchestrator (or as a pre-dispatch hook), not in the advisor agent. |
| IN-009 | `KB-cc-design/references/principles.md` | Enforce-vs-instruct principle: behaviors that must be guaranteed (refusing dispatch is one such) belong in hooks / permission-deny rules, not CLAUDE.md instructions. The principle directly constrains U-2's implementation site. |
| IN-010 | ADR-0041 v1.0.1 (install-mechanism hybrid) | Section 1 "Decision" contains the canonical per-server install-mechanism table that names the invocation form for each of Serena / actionlint-mcp / terraform-mcp / GitNexus / Context7 / Exa (mcp-openapi-schema row remains in the ADR but is historically deprecated per the 2026-05-24 postmortem; design-claude-code should treat it as removed when running parity). This is the comparison target for FR-3. |
| IN-013 | `KB-mcp-design/references/principles.md` | Eight canonical principles including #1 "env-block indirection only — never URL-query, never argv" and the OP-9/OP-10 anti-patterns. These define how env-var indirection is *already* canonicalized for audit purposes; FR-3's normalization rules must compose with them. |
| IN-014 | ADR-0042 (auditing-mcp-family-graduation) + ADR-0043 (auditing-mcp-Gate-6-hard-gate) | `auditing-mcp` is now its own family (no longer under `auditing-cc-configs`) and runs at Gate 6 as a hard gate. The new FR-3 rule's blocking-finding behavior therefore inherits the Gate-6 hard-gate semantics; no separate gate-discipline decision is required. |
| IN-018 | `KB-codespaces-design/references/principles.md` + ADR-0041 v1.0.1 §4 | The KB establishes lifecycle-hook placement principles ("right hook for right cost"); ADR-0041 §4 codifies that all MCP installs (including GitNexus) land in `postCreateCommand`. The FR-4 dry-run sits just upstream of the GitNexus install step in `postCreate.sh` — natural placement, no new architectural choice required. |
| IN-022 | `KB-github-actions-platform/references/security.md` + `KB-github-actions-design/references/principles.md` | KB-github-actions-platform's "five non-negotiables" (SHA-pin third-party actions; least-privilege permissions; never interpolate untrusted input into `run:`; OIDC over long-lived keys; concurrency on deploy workflows) cover every security-discipline question FR-5 raises. KB-github-actions-design's principles add the CI-vs-CD separation guidance (FR-5 is CI). |
| IN-023 | `KB-github-actions-platform/references/events-and-triggers.md` | Documents `pull_request.paths`, branch filters, and the gotchas around `pull_request_target` vs `pull_request`. The path-trigger set in U-5 is expressed via `pull_request.paths`; no novel mechanic needed. |
| IN-025 (partial) | `KB-github-actions-design/references/patterns-and-anti-patterns.md` (KB coverage of "matrix vs separate jobs", "runner choice", "self-hosted vs hosted runners") + `designer-general-knowledge` (fidelity-vs-runtime trade-off itself) | The KB covers runner-choice patterns; the trade-off between "clean container with claude installed inline" and "PR devcontainer image" is a standard CI fidelity-vs-runtime call a competent CI designer makes by weighing NFR-4 (5-minute budget) against the value of probing in the same image MCP servers actually run in. The designer documents the rationale in the CI/CD Design subsection per the `designer-general-knowledge` disposition rule. |
| IN-029 | `KB-documentation-criteria/references/deliverable-archive-spec.md` | The deliverable-archive spec documents what artifacts the archive collects; the U-7 question ("housekeeping commit vs archive entry") reduces to a placement check against this spec. |
| IN-030 | `KB-mcp-platform/references/mcp-events-jsonl.md` + ADR-0037 | The event-surface schema documents the three event types (`install_complete`, `readiness_probe`, `structured_failure`) and the redaction-at-source posture. NFR-13 is satisfied by FR-3/4/5 emitting only events of these existing types (or no new events at all). |
| IN-031 | ADR-0040 (Serena narrowed-always-on; 5-agent allowlist precedent) | ADR-0040 establishes the precedent and the existing allowlist; the FR-1..FR-5 mechanisms do not introduce a new MCP server or change which sub-agents need MCP access. NFR-15 is satisfied without amendment. |

## Estimated effort

- **Codebase research effort**: **medium**. The codebase touch-points are concentrated (the four reviewer agents, the parent orchestrator skill, the `auditing-mcp` skill, `postCreate.sh`, ADR-0041, and a few `Issues/` artifacts), but several of them require structured extraction (the reviewer-output shape per FR-1, the orchestrator's scope-class consumption point per FR-2, the ADR-0041 invocation table per FR-3). The researcher should expect to spend more time on structured extraction than on graph traversal — the blast-radius questions here are tightly bounded (this is a self-contained MINOR feature on the pipeline machinery itself).
- **External research topic count**: **2 of 6 budget**.
- **Estimated wall-clock**: small-to-medium. Codebase research is a single invocation; the two external topics fan out in parallel (≤6 in parallel per ADR-0021). Estimated 1-2 hours of researcher wall-clock total, dominated by codebase structured-extraction.

## Open questions for human resolution

The following are genuine ambiguities or budget questions the Research Plan cannot resolve without input. They surface at the Research Plan Approval Gate.

1. **Is the 2-topic external research scope right, or should anything else become external research?** The plan's KB/ADR-first analysis lands 29 of 31 information needs on existing artifacts or codebase facts. A skeptical reviewer might ask whether the FR-3 comparison algorithm (U-3) deserves external research into "best practices for invocation-form-equivalence checks" rather than `designer-general-knowledge`. The plan's posture is that this is a project-specific call shaped by KB-mcp-design's existing normalization principles (IN-013), not a generic problem with industry-standard solutions — but the user may disagree.

2. **Should T-001 (GitNexus contract) be deferred to design-codespaces' inline verification** (the validation owner for A-2 is already `design-codespaces`, and the assumption-validation step inspects the pinned tag), rather than a separate external-research topic? The argument for keeping it as research: the positive-assertion shape is the key risk-mitigation lever for the "silent dry-run pass" failure mode FR-4's risk row names, and packaging that as an external-research deliverable forces a written, citable result the designer can re-read rather than a one-shot inspection. The argument for folding it in: the designer is going to read GitNexus's source anyway, so the topic is parallel work. The plan's default is to keep it as T-001 because the citation discipline matters; the user may prefer the consolidated path.

3. **Should the `execute-phase-quality-reviewer` agent be in FR-1's scope?** The PRD names three reviewers explicitly (`shared-document-reviewer`, `review-architecture-auditor`, `review-cross-artifact-auditor`) in the Stakeholder Inventory; the IC's Clarified Intent §1 says "Applies to the phase-quality reviewer and any other reviewer that emits a verdict+findings pair." The plan includes `execute-phase-quality-reviewer` in the touch points and IN-001 because its output also shapes orchestrator behavior. If the user intended FR-1 to be limited to the three named reviewers only, the touch-point list narrows; design-claude-code's contract decision becomes correspondingly narrower. This question is best resolved at the Research Plan Approval Gate, before the researcher invests in extracting the fourth agent's output shape.

4. **Coverage of `mcp-openapi-schema` in FR-3's parity check.** The 2026-05-24 postmortem removed `mcp-openapi-schema` from `.mcp.json` (six active servers, not seven); ADR-0041's table still lists it for historical continuity. Should FR-3 surface that row as a "missing-from-`.mcp.json`" blocking finding under AC-FR-3-c (which would fire on a previously-decided removal), or should the audit rule treat ADR-0041 entries with a documented removal marker as not-required-in-`.mcp.json`? This is a design call but worth flagging now because the natural reading of AC-FR-3-c gives a false-positive on day one. design-claude-code can take it under U-3 if the user prefers; otherwise the user may want to amend ADR-0041 (out of this feature's scope per the carve-out posture) or accept the day-one false positive and allowlist it.
