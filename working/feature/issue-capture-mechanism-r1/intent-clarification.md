---
id: IC-issue-capture-mechanism-r1
doc_type: intent-clarification
version: 1.0.0
status: draft
feature_slug: issue-capture-mechanism-r1
scope_class: FULL
user_token: approved-2026-05-23T16:51:00Z
generated: 2026-05-23T00:00:00Z
generated_by: intake-intent-clarifier
derived_from: Issues/issue-capture-mechanism/proposal.md
companion_artifacts:
  - Issues/issue-capture-mechanism/proposal.md
  - /home/vscode/.claude/plans/i-am-noticing-as-reflective-wilkes.md
---

# Intent Clarification: Issue-Capture Mechanism (Outside-the-Pipeline)

## Contents

- [x] Purpose
- [x] Source
- [x] Initial Interpretation
- [x] Clarifying Questions and Answers
- [x] Clarified Intent
- [x] Scope Posture
- [x] Stakeholder Posture (Preliminary)
- [x] Success Posture (Preliminary)
- [x] Confirmation
- [x] Open Items (Pending PRD Authoring)

## Purpose

The first artifact in the feature-pipeline. It captures the user's intent before any
PRD or design work begins. It is NOT a requirements document and NOT a design document
— it is a structured record of what the user wants, with ambiguities surfaced and
resolved. It gates progression to PRD Authoring via the Intent Confirmation Gate.

This run is the dogfood test of a design decision encoded in its own source: the
captured issue-proposal at `Issues/issue-capture-mechanism/proposal.md` is being used
as `prior_context` for Stage 1 (Intent Clarification). Per that proposal's own design,
this clarifier reads the proposal body as authoritative prior context and elicits
ONLY what the proposal lacks — it does not re-litigate already-decided design.

## Source

> "I am noticing as I work on features within the feature pipeline issues arise that
> need to be documented for future feature consideration. It is important to not
> pollute the feature run unless it is material to the feature scope. However, it is
> also super important to capture at that moment with the evidence to ensure it does
> not get forgotten." — Josh-S-N2M, 2026-05-23 conversation.

Formal seed: `Issues/issue-capture-mechanism/proposal.md`
(`doc_type: issue-proposal`, `proposes_future_feature: issue-capture-mechanism-r1`).

Companion artifact (decided design): `/home/vscode/.claude/plans/i-am-noticing-as-reflective-wilkes.md`
— a ~400-line plan-mode design across architecture, naming, folder model, frontmatter,
approval prompt, hook script, lifecycle state machine, handoff design, verification.

## Initial Interpretation

The proposal + companion plan supply the substance: a new outside-pipeline mechanism
to capture out-of-current-scope issues without polluting the active feature run,
formed by a KB skill (`KB-issue-capture`), an entry-point skill (`capture-issue`
exposing `/capture-issue`), a non-pipeline agent (`issue-capture-author`), a
PreToolUse hook on `Task` for `subagent_type == issue-capture-author`, three new
issue-doctype templates under `KB-documentation-criteria`, an additive
`.claude/settings.json` patch, an extension to `validate_pipeline_frontmatter.py`,
and a per-issue folder model at `Issues/<topic-slug>/<doctype>.md` with fixed
doctype filenames. Layered approval enforcement (skill `disable-model-invocation`
+ agent-body `AskUserQuestion` + PreToolUse hook) is decided. The handoff back into
the pipeline is via the existing optional `prior_context` parameter at Stage 1 — no
new pipeline stage, no gate skip.

What this Stage 1 must still pin down is the boundary of r1: which capabilities ship
now versus deferred, the exhaustive 9-layer scope declaration (the proposal hints at
two layers but does not formally declare), the scope class per ADR-0023, and the
shape of the success criteria — i.e., the things downstream stages (PRD, per-layer
Design, Plan, Tests) need declared before they begin.

## Clarifying Questions and Answers

The proposal + plan already settle ~80% of the elicitation work normally done here.
The remaining ambiguities are surfaced below with **proposed defaults** derived from
the plan file and from internal consistency analysis. Per the Confirmation Gate
discipline, every row's "User Answer" is the proposed default; user explicit
confirmation at Gate 1 ratifies them. Any row the user rejects at the gate becomes
an Open Item and triggers re-elicitation before PRD Authoring begins.

| # | Ambiguity | Question | User Answer (proposed; confirm at Gate 1) | Resolved? |
|---|---|---|---|---|
| 1 | Scope class per ADR-0023 | FULL / MINOR / PATCH? Multi-primitive new subsystem touches `.claude/agents/`, `.claude/skills/` (3 new skills), `.claude/hooks/` (new dir), `.claude/settings.json`, `KB-documentation-criteria/references/templates/` (3 new), `validate_pipeline_frontmatter.py`, plus 4 file migrations. | FULL — multi-primitive subsystem with multiple ADR-worthy decisions; matches precedent of `devcontainer-mcp-provisioning-r1` which ran FULL on comparable scope. | [x] |
| 2 | Update-mode scope (`/capture-issue --update <path>`) | The plan describes a 5-state lifecycle (`draft → open → adopted \| complete \| superseded \| wontfix-with-rationale`) and an `--update` invocation that transitions a file's state. Is update-mode in scope for r1 or deferred to r2? | IN scope for r1. The plan dedicates a "Lifecycle additions to the file list" subsection to update-mode and ties it to the canonical 5-state vocabulary. Deferring would leave the mechanism unable to close out a captured issue once the work is done — defeating audit-trail value. | [x] |
| 3 | Validator status vocabulary | The plan has an internal inconsistency: the "EDIT" file-list row says the validator recognises the analysis/log 3-state (`draft → complete \| superseded`), while the "Issue lifecycle" section defines a 5-state vocabulary. Which does the validator enforce for `Issues/*.md` files? | The 5-state vocabulary (`draft → open → adopted \| complete \| superseded \| wontfix-with-rationale`). Per the orchestrator's invocation note, this is the user-confirmed decision and parallels-but-distinct-from the intra-pipeline 4-state at `KB-review-disciplines/references/issue-lifecycle.md`. The plan's earlier "3-state" cell is stale wording to be corrected in Design. | [x] |
| 4 | Migration of `agent-roster-impact-matrix.md` | The plan flagged uncertainty about whether `working/feature/devcontainer-mcp-provisioning-r1/agent-roster-impact-matrix.md` should `git mv` into `Issues/per-agent-design-evaluation-gap/evidence/`. The file currently exists at the `working/feature/` path. | Move into `Issues/per-agent-design-evaluation-gap/evidence/` as a supporting artifact of that analysis. The file is the empirical evidence for the per-agent-design gap analysis; its current location couples it to a feature run it does not belong to. | [x] |
| 5 | Entry-skill argument shape | `/capture-issue <one-line hint>` accepts free-form `$ARGUMENTS`; `--update <path>` is an additional flag-style argument. Should `/capture-issue` enforce mutual exclusivity (free-form hint XOR `--update <path>`), or allow both? | Mutual exclusivity. Create-mode and update-mode are distinct workflows: create-mode classifies + drafts; update-mode reads-then-transitions. Mixing the two confuses the agent body's branching and the `AskUserQuestion` prompt shape. | [x] |
| 6 | Existing 4 files post-migration: do they need status back-fill beyond `version:` | The 4 existing `Issues/*.md` files currently lack `version:`. Plan back-fills `version: 0.1.0`. Do they also need a `status:` field set, given the new 5-state vocabulary the validator will enforce? | Yes — back-fill `status: open` on all 4 (they were created as the equivalent of "captured, not yet resolved"), plus the `since:` companion field set to the file's earliest known authoring timestamp. The validator extension MUST allow `version: 0.1.0` + `status: open` to validate cleanly post-migration. | [x] |
| 7 | Hook fail-open vs. fail-closed | If the PreToolUse hook script errors (e.g., missing dependency, malformed stdin JSON), should the `Task` spawn proceed (fail-open) or be blocked (fail-closed)? | Fail-open with stderr log. Blocking pipeline sub-agent spawns on a hook bug would break ~28 pipeline agents over an outside-pipeline safeguard. The agent-body `AskUserQuestion` (Layer 2) and `disable-model-invocation` (Layer 1) remain as defenses. Hook errors should surface for debugging without halting the orchestrator. | [x] |

## Clarified Intent

Build an outside-pipeline, user-invoked mechanism that captures issues noticed during
feature-pipeline runs without polluting those runs. The mechanism formalizes the
practice already empirically established by four ad-hoc files under `Issues/`: a KB
skill (`KB-issue-capture`) carries the triggering discipline; an entry-point skill
(`capture-issue`) exposes `/capture-issue` and `/capture-issue --update <path>`; a
non-pipeline agent (`issue-capture-author`) does the authoring; three new structural
templates under `KB-documentation-criteria` codify the register / analysis / proposal
doctypes (preserved as 3 distinct doctypes, not unified); `validate_pipeline_frontmatter.py`
is extended to recognize the new doc_types and the 5-state status vocabulary; and a
PreToolUse hook on `Task` adds an OS-level approval at the spawn boundary.

Enforcement is three-layered (`disable-model-invocation: true` on the KB skill +
mandatory `AskUserQuestion` Step D inside the agent body + PreToolUse hook on `Task`
discriminated by `subagent_type == issue-capture-author`). Folder model is per-issue:
`Issues/<topic-slug>/<doctype>.md` with fixed doctype filenames (`register.md`,
`analysis.md`, `proposal.md`). Issue evolution uses an add-new-sibling-file pattern
with bidirectional `escalates_from:` / `escalated_to:` cross-links — the older file
is NOT mutated when a new doctype is added beside it. The 5-state lifecycle (`draft
→ open → adopted | complete | superseded | wontfix-with-rationale`) parallels but is
distinct from the intra-pipeline 4-state ledger; the two never share IDs.

Handoff from a captured proposal back into the Feature Pipeline uses the existing
optional `prior_context` parameter at Stage 1 — no new pipeline stage, no gate skip.
The intent-clarifier reads the proposal's analysis as authoritative prior context and
elicits only what the proposal lacks (FRs, NFRs, EARS ACs, exhaustive 9-layer scope).
This Stage 1 run is itself the dogfood test of that handoff.

Migration of the 4 existing flat `Issues/*.md` files into the per-issue folder model
is in scope as a one-time event (`git mv` to preserve history), with `version: 0.1.0`
and `status: open` back-filled. Update-mode (`/capture-issue --update <path>`) ships
in r1 — without it, the 5-state lifecycle is unable to be traversed.

## Scope Posture

### What's in scope

- **New KB skill** `KB-issue-capture` at `.claude/skills/KB-issue-capture/SKILL.md`
  with `disable-model-invocation: true` and 4 reference files (`triage-criteria.md`,
  `approval-prompt-rubric.md`, `examples.md`, `non-pollution-contract.md`).
- **New entry-point skill** `capture-issue` at `.claude/skills/capture-issue/SKILL.md`
  exposing `/capture-issue <hint>` and `/capture-issue --update <path>` (mutually
  exclusive); `disable-model-invocation: true`; `allowed-tools: Task, AskUserQuestion`.
- **New non-pipeline agent** `issue-capture-author` at `.claude/agents/issue-capture-author.md`
  with `tools: Read, Grep, Glob, Write, AskUserQuestion`, `model: sonnet`,
  `skills: [KB-issue-capture]`; body mandates the 6-step workflow (parse → classify →
  draft → `AskUserQuestion` → write-on-approval → abandon-on-reject) plus the
  update-mode branch.
- **New PreToolUse hook script** at `.claude/hooks/intercept-issue-capture-agent.sh`
  (create `.claude/hooks/` directory). Discriminates by `subagent_type`; emits
  `permissionDecision: "ask"` for `issue-capture-author` spawns with a spawn-prompt
  preview, silent `allow` for all other `Task` spawns. Hook is read-only, fail-open
  on script error.
- **Additive `.claude/settings.json` patch** adding one permission entry
  (`Bash(.claude/hooks/intercept-issue-capture-agent.sh:*)`) and one
  `hooks.PreToolUse` block matching `Task`. Existing 7 allow entries untouched.
- **Three new structural templates** under `KB-documentation-criteria/references/templates/`:
  `issue-register-template.md`, `issue-analysis-template.md`, `issue-proposal-template.md`.
  Plus a structural-only spec `issue-doctypes-spec.md` (NO triggering discipline —
  that lives in `KB-issue-capture`).
- **Extension to `.claude/skills/auditing-shared/scripts/validate_pipeline_frontmatter.py`**
  to recognize the three new `doc_type` enum values (`issue-register`, `issue-analysis`,
  `issue-proposal`) and the 5-state status vocabulary (`draft → open → adopted |
  complete | superseded | wontfix-with-rationale`) with per-state required-companion-field
  rules. Backward-compatible: existing pipeline doc_types unaffected.
- **One-time migration of 4 existing flat `Issues/*.md` files** into the per-issue
  folder model via `git mv` (history preserved). Back-fill `version: 0.1.0` and
  `status: open` (with `since:` companion field) on all four.
- **Migration of `working/feature/devcontainer-mcp-provisioning-r1/agent-roster-impact-matrix.md`**
  into `Issues/per-agent-design-evaluation-gap/evidence/` as supporting evidence.
- **Small edits to support the handoff design**:
  - `.claude/agents/intake-intent-clarifier.md` — add a "Proposal-as-prior-context"
    sub-section so future runs can detect `doc_type: issue-proposal` in
    `--raw-request` and treat the body as authoritative prior context. (~15 lines)
  - `.claude/skills/KB-documentation-criteria/references/templates/intent-clarification-template.md`
    — clarify the `Source` section so it cites a proposal path verbatim when one
    seeds the run. (~5 lines)
  - `.claude/skills/recipe-feature-pipeline/SKILL.md` — one bullet documenting the
    proposal-seed invocation pattern. NOT a new stage; documents existing parameter
    shape applied to the new artifact type. (~5 lines)
- **Index update to `.claude/skills/KB-documentation-criteria/SKILL.md`** (additive
  rows for the 3 new templates and the new spec; one bullet under "Where this KB is
  NOT used" stating triggering discipline lives in `KB-issue-capture`). No removals,
  no restructure.
- **Append-only note in `.claude/SETTINGS-NOTES.md`** documenting the hook policy
  and the user authorization for the additive `settings.json` change.
- **ADR authorship** by Design Composition (Stage 5) for the load-bearing decisions
  (per-issue folder model, three-doctypes-preserved, add-new-file evolution pattern,
  three-layer enforcement, prior-context handoff design, structural-vs-discipline
  split inside `KB-documentation-criteria`, 5-state vocabulary).

### What's NOT in scope (explicitly excluded)

- **A new intra-pipeline issue mechanism.** The existing `working/feature/<slug>/issues-ledger.json`
  (per ADR-0008) remains the sole intra-pipeline issue tracker. `Issues/*.md` and
  the ledger never share IDs and never cross-reference each other automatically.
- **A UI surface beyond the slash command** — no web view, no dashboard, no listing
  command. Discoverability is the `Issues/` directory itself.
- **Automated cross-linking between `Issues/*.md` and intra-pipeline ledger entries.**
  The two systems are deliberately separate per the decision rubric in the plan.
- **A scheduled/automated sweep** to back-fill or re-classify older `Issues/*.md`
  files. Migration of the existing 4 is a one-time event; ongoing files use the
  folder model from creation.
- **Slack / webhook / email / external notification integration.**
- **Any pipeline sub-agent invoking `issue-capture-author` or loading `KB-issue-capture`.**
  This is the load-bearing invariant. No edit to any `.claude/agents/{intake,
  discovery,design,plan,test,review,finalize,execute,synth}-*.md` file.
- **New CLAUDE.md or `.claude/rules/` directory** at repo root — skill-localised
  knowledge per KB-cc-design Principle 1.
- **Edit to `recipe-feature-pipeline/SKILL.md`** beyond documenting the proposal-seed
  invocation pattern. No new pipeline stage. No new gate. No bypass path.
- **Mutation of an older doctype file when a sibling doctype is added** (e.g., when
  `analysis.md` evolves to need a `proposal.md`, the analysis file remains at its
  current `status:`; only `escalated_to:` is added). The bidirectional cross-link
  IS treated as a single approved transaction (one `AskUserQuestion`, two writes).
- **Severity vocabulary on `Issues/*.md` files** — issues are captured for memory,
  not triaged for blockage. Severity is intra-pipeline ledger territory only.
- **Deletion of any `Issues/*.md` file** including terminal-state ones. Terminal
  states preserve the audit trail.

### What's undecided (deferred to PRD or later)

- **Hook script's exact stdin/stdout contract** — JSON schema details, exit-code
  protocol, log destination (stderr vs. project-relative file). Per `auditing-hooks`
  conventions. Resolve in CC-layer design.
- **The exact text of the `AskUserQuestion` approval prompt template** — the plan
  sketches the WHY/WHAT/WHERE shape; final wording (especially edge-case prompts for
  filename collisions and update-mode OLD→NEW diff rendering) lands in the
  `approval-prompt-rubric.md` reference file at design time.
- **Examples for `KB-issue-capture/references/examples.md`** — three worked examples
  to be reverse-engineered from the 4 existing files in `Issues/`. Specific pairing
  (which existing file demonstrates which doctype) is a design-stage choice.
- **Frontmatter field set for the 5 terminal states** — the plan tables the required
  companion fields per state; whether any are optional vs. mandatory and the validator's
  enforcement strictness is finalized at PRD/Blueprint.
- **`auditing-hooks` / `auditing-skills` / `auditing-subagents` / `auditing-settings`
  pre-merge findings** — likely surface (missing exit-code documentation, allowed-tools
  scoping, description routing, additive-change phrasing). Resolve in Phase
  Quality Review / cc-critique pass.
- **Whether the `proposes_future_feature:` slug in a proposal's frontmatter is
  validator-enforced** (presence, format) or advisory. Resolve at PRD.
- **Test strategy for the hook script** — unit test (`bash` test harness) vs. shellcheck
  vs. golden-file dry-run vs. integration test via `Task` invocation. Resolve at
  Plan-authoring / acceptance-test authoring.
- **Idempotency of update-mode writes** — if the user re-runs `/capture-issue
  --update <path>` with the same proposed transition, the write should be a no-op
  with explicit user notification. Mechanism is decision-pending.

## Stakeholder Posture (Preliminary)

- **Primary — Josh-S-N2M (issue-capture invoker / user):** wants a low-friction
  `/capture-issue` that does not pollute active feature runs, with clear WHY/WHAT/WHERE
  approval at every transition; wants the captured files to survive feature archival
  and remain in `Issues/` as a project-lifetime record.
- **Secondary — feature-pipeline orchestrator (`recipe-feature-pipeline`):** wants
  the new mechanism to not perturb the 6 mandatory human gates, the ~28 pipeline
  sub-agents, or the per-stage artifact contracts; wants the
  `validate_pipeline_frontmatter.py` extension to be backward-compatible.
- **Secondary — `intake-intent-clarifier` (this agent, in future runs):** wants the
  proposal-as-prior-context detection to be unambiguous (`doc_type: issue-proposal`
  in frontmatter) and the source-citation discipline encoded in the template.
- **Explicit non-stakeholders (by design) — pipeline sub-agents:** no agent under
  `.claude/agents/{intake,discovery,design,plan,test,review,finalize,execute,synth}-*.md`
  should load `KB-issue-capture` or invoke `issue-capture-author`. The three-layer
  enforcement is the structural guarantee.
- **Cross-cutting — `cc-critique` and the `auditing-*` skills:** the new
  agent / skills / hook / settings additions must pass cc-critique with at most
  PASS-WITH-MINOR-FIXES. Cosmetic fixes (header documentation, idempotency notes)
  are acceptable; structural findings are not.

## Success Posture (Preliminary)

The mechanism is "done" when (a) a fresh `/capture-issue "..."` invocation spawns
`issue-capture-author` through the hook (which presents `permissionDecision: "ask"`
with a spawn-prompt preview), the agent classifies the doctype, drafts the file,
presents an `AskUserQuestion` with the WHY/WHAT/WHERE structure, and writes exactly
one file under `Issues/<topic-slug>/<doctype>.md` on user approval; (b) `/capture-issue
--update <path>` reads an existing file, drafts the proposed lifecycle transition,
presents an OLD→NEW preview, and writes only on approval; (c) the three-layer
enforcement test passes (no pipeline sub-agent can reach the mechanism — grep checks
return empty; hook fires on `subagent_type == issue-capture-author` and silently
allows other spawns); (d) `python3 .claude/skills/auditing-shared/scripts/validate_pipeline_frontmatter.py
Issues/` returns clean on all 4 migrated files plus any newly created files; (e) the
migration to per-issue folders preserves git history (`git log --follow` resolves
all 4); (f) `cc-critique` returns PASS or PASS-WITH-MINOR-FIXES; (g) every approved
write is preceded by exactly one `AskUserQuestion`, and reject paths leave zero
files written.

## Confirmation

Before the orchestrator proceeds to PRD Authoring, the user confirms this document.
The confirmation token will be recorded in frontmatter (`user_token`) and captured
by the orchestrator's `AskUserQuestion` at the Intent Confirmation Gate. The
proposed defaults recorded in §"Clarifying Questions and Answers" become binding
on confirmation; any rejected default re-opens that row before PRD authoring begins.

## Open Items (Pending PRD Authoring)

The following items are surfaced for the PRD author's attention. They are NOT
re-elicited here because either (a) the proposal/plan already supplies the structural
answer and the PRD's job is to formalize it as FRs/NFRs/EARS ACs, or (b) the
ambiguity is genuinely design-stage, not intent-stage.

### Functional capabilities to formalize as FRs

The PRD will derive numbered FRs from the in-scope items above. Seed list (not yet
PRD-formatted; the PRD author may renumber / split / combine):

- Create-mode invocation: `/capture-issue <hint>` → spawn agent → classify → draft
  → approve via `AskUserQuestion` → write exactly one file.
- Update-mode invocation: `/capture-issue --update <path>` → read → classify
  transition → present OLD→NEW preview → write on approval.
- Three-layer approval enforcement (skill flag + agent body + PreToolUse hook).
- Per-issue folder model + add-new-sibling-file evolution with bidirectional cross-links.
- Three structural templates (register / analysis / proposal) under `KB-documentation-criteria`.
- Validator extension recognising 3 new `doc_type` values + 5-state vocabulary with
  per-state required companion fields.
- One-time migration of 4 existing `Issues/*.md` files; back-fill `version: 0.1.0`
  + `status: open` + `since:`; preserve git history.
- Migration of `agent-roster-impact-matrix.md` into per-issue-folder evidence.
- Source-citation discipline: when a feature-pipeline run is seeded by an
  `Issues/<topic>/proposal.md`, the run's `intent-clarification.md` cites that
  proposal verbatim in its `Source` section.
- Pipeline isolation invariant (no pipeline sub-agent loads the new KB or invokes
  the new agent).

### Non-functional concerns to formalize as NFRs

- **Backward compatibility** of `validate_pipeline_frontmatter.py`: zero false
  positives or false negatives on the existing pipeline doc_types after extension.
- **Hook performance**: hook fires on every `Task` spawn; per-spawn overhead must
  not measurably perturb pipeline runs. Discriminator path (`subagent_type` check
  → silent `allow`) is the fast path.
- **Hook reliability**: fail-open behavior on script errors with stderr logging.
- **Prompt-injection resistance**: agent body's `AskUserQuestion` Step D is the
  in-context guard against a manipulated `$ARGUMENTS` driving an unintended write.
- **Idempotency**: re-running `/capture-issue --update <path>` with no change must
  be a no-op (no duplicate writes, no spurious approval prompt).
- **No silent overwrite**: filename collision in create-mode forces a re-prompt
  with `supersede / rename / cancel` options (per the non-pollution contract).
- **Audit-trail preservation**: terminal-state files are never deleted; supersession
  uses the established frontmatter discipline (`superseded_by_issue_id:`).
- **Observability**: every write logs the file path + the user's selected option
  to a destination consistent with project conventions (decided at design).

### Acceptance criteria to formalize in EARS at PRD time

Seed bullets (the PRD will render these in proper `WHEN <trigger> THE SYSTEM SHALL
<response>` format and tag them to FRs):

- WHEN the user invokes `/capture-issue <hint>` THE SYSTEM SHALL spawn the
  `issue-capture-author` agent via `Task` and SHALL trigger the PreToolUse hook
  before the spawn completes.
- WHEN the PreToolUse hook receives `tool_input.subagent_type ==
  "issue-capture-author"` THE SYSTEM SHALL emit `permissionDecision: "ask"` with the
  spawn-prompt preview.
- WHEN the PreToolUse hook receives any other `tool_input.subagent_type` THE SYSTEM
  SHALL emit `permissionDecision: "allow"` silently (no additional user prompt).
- WHEN `issue-capture-author` is invoked in create-mode THE SYSTEM SHALL present
  exactly one `AskUserQuestion` with the WHY/WHAT/WHERE shape and the 4 fixed
  options (Approve / Approve-with-edits / Change-doctype / Cancel) before any Write.
- WHEN the user selects Cancel THE SYSTEM SHALL NOT write any file.
- WHEN the user selects Approve THE SYSTEM SHALL write exactly one file at
  `Issues/<topic-slug>/<doctype>.md` (creating the topic folder if absent) and
  SHALL report the path.
- WHEN `issue-capture-author` is invoked in update-mode with `--update <path>` THE
  SYSTEM SHALL read the existing file, draft a transition, present an OLD→NEW
  `AskUserQuestion`, and write only on approval.
- WHEN an issue evolves to a new doctype (e.g., `analysis` → `proposal`) THE SYSTEM
  SHALL add a new sibling file with `escalates_from:` set AND SHALL add
  `escalated_to:` to the existing file's frontmatter, both within a single approved
  transaction.
- WHEN `validate_pipeline_frontmatter.py` is run against `Issues/` THE SYSTEM SHALL
  pass on all 4 migrated files plus all new-format captures.
- WHEN any pipeline sub-agent attempts to load `KB-issue-capture` or spawn
  `issue-capture-author` THE SYSTEM SHALL prevent the action via the three-layer
  enforcement (skill flag, hook, agent body).
- WHEN a feature-pipeline run is seeded by an `Issues/<topic>/proposal.md` THE
  SYSTEM SHALL cite that proposal verbatim in the run's `intent-clarification.md`
  `Source` section.
- WHEN `cc-critique` is run against the new components THE SYSTEM SHALL return
  PASS or PASS-WITH-MINOR-FIXES (zero BLOCKER findings).

### Exhaustive 9-layer scope declaration

Per KB-documentation-criteria 9-layer taxonomy:

| # | Layer | Disposition | Rationale |
|---|---|---|---|
| 1 | Claude Code / Project Filesystem | **IN scope (primary)** | Touches `.claude/agents/` (new agent), `.claude/skills/` (2 new skills + 1 KB edit), `.claude/hooks/` (new dir + script), `.claude/settings.json` (additive), `KB-documentation-criteria/references/templates/` (3 new), `KB-documentation-criteria/references/` (new spec), `.claude/SETTINGS-NOTES.md` (append). Bulk of the work. |
| 2 | Frontend | **OUT of scope** | No UI surface beyond the slash command, which is CC-layer. |
| 3 | Backend | **IN scope (secondary)** | Extension to `.claude/skills/auditing-shared/scripts/validate_pipeline_frontmatter.py` (Python script) — tooling/infra logic, not a service, but lives in the backend layer per the taxonomy. |
| 4 | API | **OUT of scope** | No HTTP/GraphQL/RPC contract changes. |
| 5 | Query / Data Access | **OUT of scope** | No ORM, no repository, no query layer. |
| 6 | Database | **OUT of scope** | No schema, no migrations. The `Issues/` directory and frontmatter are not a database. |
| 7 | CI/CD (GitHub Actions) | **OUT of scope** | No workflow / job / action changes. (If the validator extension benefits from CI invocation, that may surface as a Discovery finding; intent-stage default is OUT.) |
| 8 | Infrastructure as Code | **OUT of scope** | No Terraform / Pulumi / CDK / CloudFormation changes. |
| 9 | Dev Environment (Codespaces / Devcontainer) | **OUT of scope** | No `devcontainer.json`, prebuild, port, or lifecycle script changes. |

Layers 1 and 3 are the only activated layers. Per-layer Design will produce
`claude-code-design.md` (primary) and `backend-design.md` (focused on the validator
extension). The other 7 per-layer Design subsections are explicitly `N/A — out of
scope`.

### Other open items for PRD / Discovery / Design attention

- Resolve the 8 "What's undecided" items above (hook stdin/stdout, approval-prompt
  exact text, examples-pairing, frontmatter strictness, audit findings, validator
  enforcement of `proposes_future_feature:`, hook test strategy, update-mode
  idempotency).
- ADR slate: per the proposal, ~7 ADR-worthy decisions are pending. Design
  Composition (Stage 5) will author them. Tentative subjects: per-issue folder
  model; three-doctypes-preserved; add-new-file evolution pattern; three-layer
  enforcement; prior-context handoff; structural-vs-discipline KB split; 5-state
  vocabulary distinct from intra-pipeline 4-state.
- Cross-reference: this run's Plan-stage should pre-stage the `auditing-hooks` /
  `auditing-skills` / `auditing-subagents` / `auditing-settings` checks as L1/L2/L3
  verification, given the new components fall in each auditor's scope.
- Bootstrap note: this very `intent-clarification.md` is itself the first product
  of the proposal-as-prior-context handoff design. Its successful Gate 1 approval
  is empirical evidence that the design works; its rejection would itself be a
  finding worth capturing as an `Issues/<topic>/analysis.md` (post-mechanism).
