# Claude Code Design Principles

The foundational principles a Claude Code Designer applies when authoring the `### Claude Code Design` subsection of the Blueprint.

## Contents

- Principle 1: Pick the lowest-cost primitive that does the job
- Principle 2: Path-gate everything that can be path-gated
- Principle 3: Enforce when safety-critical; instruct when guidance-critical
- Principle 4: Isolate with subagents only when isolation pays for itself
- Principle 5: One source of truth per piece of knowledge
- Principle 6: Permissions are the safety net, not the design
- Principle 7: Plugins for distribution, not for organization
- Principle 8: Migrate to skills; keep commands only for tiny one-shots
- Principle 9: Sub-agent reasoning configuration is intentional, not default
- Principle 10: Uniform rules over named exceptions — no carve-outs in canonical-placement rules

## Principle 1: Pick the lowest-cost primitive that does the job

Every primitive has a context cost. The Designer's first question is: what's the lowest-cost mechanism that gives the desired behavior?

| Primitive | Context cost on every request | Activation |
|---|---|---|
| Hook | Zero (runs outside the loop) | Lifecycle event (PreToolUse, PostToolUse, SessionStart, etc.) |
| `permissions.deny` rule | Zero | Tool invocation attempted |
| MCP tool schema | Zero (deferred) | Model decides to use the tool |
| Skill with `disable-model-invocation: true` | Zero | User invokes via `/skill-name` |
| Skill (model-invocable, default) | ~30-80 tokens (description) | Model matches description |
| Rule with `paths:` | Zero when paths don't match; full content when they do | Matching files enter context |
| Subagent (defined but not invoked) | Zero | Lead agent invokes it |
| Rule without `paths:` (unconditional) | Full content every request | Always |
| CLAUDE.md | Full content every request (additive across levels) | Always |

For "load only when relevant" knowledge → model-invocable skill or path-gated rule.
For "guarantee this happens" behavior → hook or `permissions.deny`.
For "always remember this" guidance → CLAUDE.md, but minimize line count; move references to skills.
For "isolate this work" → subagent.
For "connect to external service" → MCP server.

When two primitives could work, prefer the lower-cost one. CLAUDE.md is the heaviest because it loads in full every request — every line a primitive could replace is a line worth replacing.

## Principle 2: Path-gate everything that can be path-gated

Rules support `paths:` frontmatter: the rule only enters context when files matching the glob enter context. This is a free optimization for any file-specific guidance.

Convention enforcement scoped by file type:

```markdown
---
paths:
  - "**/*.test.ts"
  - "**/*.spec.ts"
---

# Test conventions

- Use Vitest, not Jest
- Mock external services at the module boundary
- Each test file has a top-level `describe()` matching the module name
```

This rule loads when test files enter context; otherwise it's invisible. A monorepo with 50 path-gated rules might never load more than 3 at once for any given task.

Anti-pattern: a single rule containing conventions for tests, API routes, migrations, and CSS. It loads in full when any of those files appear. Split by file domain.

The Designer documents the path-gating strategy in the per-layer subsection: which rule files cover what file domains, and how additions are kept scoped.

## Principle 3: Enforce when safety-critical; instruct when guidance-critical

CLAUDE.md and rules tell Claude what to do. The model usually follows but is not obligated to — context, conflicting instructions, or misinterpretation can break compliance.

Hooks and `permissions.deny` rules are enforced by Claude Code itself: the model can't bypass them.

| Behavior | Mechanism |
|---|---|
| "Run tests before committing" (convention) | Rule or CLAUDE.md |
| "Don't run `rm -rf` on the home directory" (safety) | `permissions.deny` rule |
| "Format every edited file" (deterministic side effect) | `PostToolUse` hook running prettier/gofmt/etc. |
| "Send a notification when a long task finishes" (operational) | `Stop` hook |
| "Block edits to `vendor/`" (safety) | `permissions.deny` matching the path |
| "Prefer Postgres patterns" (guidance) | Rule with `paths:` for SQL / migration files |
| "Always include a CHANGELOG entry for user-facing changes" (process) | Rule |
| "Never write to production secrets path" (safety) | Hook validating tool input + `permissions.deny` as backup |

The Designer documents, for each behavior in scope, whether it's enforced or instructed and why. Safety-critical behaviors must be enforced; layered defense is acceptable (hook + permission rule).

## Principle 4: Isolate with subagents only when isolation pays for itself

A subagent has its own context window. Calling a subagent costs the model invocation plus the subagent's setup; the return is a summary, not the raw work product.

Subagents pay off when:

- The work reads many files but the main conversation only needs the summary (research, codebase audit, dependency review).
- The work needs a different tool set than the lead agent has (a restricted-tools subagent for code review).
- The work has its own multi-step reasoning that would clutter the lead's context.
- Cross-session memory matters (subagent with `memory:` frontmatter).

Subagents are overkill when:

- The work fits in a few tool calls; the lead can do it directly.
- The work's output is the work itself (editing 3 files), not a summary.
- The work depends heavily on the conversation context the lead has built up.

The Designer documents, for each subagent in scope:

- The trigger (when does the lead invoke?).
- The tool set (`tools:` frontmatter).
- The skills the subagent needs (`skills:` frontmatter — note that subagents do NOT auto-load skills by description).
- The memory scope (project / user / local) if any.
- The expected output shape.

## Principle 5: One source of truth per piece of knowledge

A skill that captures "our error-handling patterns" and a CLAUDE.md section that captures "our error-handling patterns" are two sources of truth. They drift; the team can't tell which is authoritative.

The Designer's discipline:

- Each piece of knowledge lives in exactly one CC artifact.
- CLAUDE.md points to skills for depth: "See the `error-handling` skill for details."
- Skills don't re-summarize CLAUDE.md content.
- Rules and skills don't overlap: if a rule and a skill cover the same topic, merge them.

When refactoring, the Designer documents the consolidation plan in the per-layer subsection.

## Principle 6: Permissions are the safety net, not the design

Claude Code's permission model gates tools: `allow`, `ask`, `deny`. The Designer specifies the permission set for the project, but treats permissions as the safety net, not the primary control.

- **`allow`** for routine operations the team trusts (reading source files, running tests).
- **`ask`** for operations with meaningful consequences (running unknown shell commands, fetching external URLs, editing in unfamiliar directories). The default `ask` policy is sensible.
- **`deny`** for the specific operations that should NEVER happen (rm -rf /, accessing production credentials, modifying CI configuration without explicit acknowledgment).

The Designer documents:

- The permission mode (default-ask, default-allow, full-control mode for trusted users).
- The deny list (specific Bash patterns, specific file paths).
- The reasoning for any deviation from default-ask.

Anti-pattern: relying on permissions alone for safety-critical behavior. A deny rule may be removed by a team member without realizing. Layer with hooks for true safety.

## Principle 7: Plugins for distribution, not for organization

A plugin bundles skills, hooks, subagents, MCP server configurations, and slash commands into a unit installable across projects.

Plugins shine when:

- Multiple projects need the same configuration (an org-wide skill set, a shared subagent for code review, a reusable hook).
- The configuration is published (open-source, internal marketplace).
- Versioning matters (consumers pin to a known version).

Plugins are overkill when:

- The configuration is project-specific (no other project will use it).
- The team is one project and doesn't reuse.
- The overhead of plugin authoring (manifest, namespacing, distribution) exceeds the benefit.

For single-project configuration, commit the artifacts directly to `.claude/`. Plugin-ify when reuse appears.

The Designer documents the plugin packaging strategy when applicable: which artifacts are in the plugin; how versions are managed; how consumers install.

## Principle 8: Migrate to skills; keep commands only for tiny one-shots

Claude Code's slash commands (`.claude/commands/*.md`) are the older mechanism — still functional but superseded by skills with `disable-model-invocation: true` (which appear in `/skill-name` form just like commands).

Skills can:

- Bundle supporting files (`assets/`, `scripts/`, `references/`).
- Define `allowed-tools` for tighter scoping.
- Be packaged in plugins.
- Be auto-invoked by description match.

Commands cannot. They're single files; that's it.

The Designer's defaults:

- New invocable workflows → skill, not command.
- Existing commands worth keeping → migrate to skill. The conversion is mechanical (move the .md content into `skills/<name>/SKILL.md` with frontmatter).
- Commands worth keeping as-is → tiny one-shots (single bash invocation, simple prompt rewrite). The line where conversion is overhead-positive.

When migrating, the Designer documents the migration plan: which commands convert, in what order, and any breaking changes to the user invocation pattern (`/cmd` to `/skill` is identical from the user's view; the conversion is invisible).

## Principle 9: Sub-agent reasoning configuration is intentional, not default

Every sub-agent's reasoning capacity is determined by three independent frontmatter fields: `model:`, `effort:`, and `skills:`. They control different things, and the Designer makes each choice deliberately — not by inheriting whatever default the carry-in template happened to use.

- **`model:`** chooses which Claude model executes the sub-agent. `sonnet` is the default-bounded choice for well-scoped transformations (a sub-agent that does one thing and returns). `opus` is the choice for cross-cutting reconciliation, cross-family critique, multi-artifact arbitration, or any work where reasoning quality is the load-bearing input. `haiku` is for narrow, repetitive transformations where speed and cost dominate. `inherit` defers to the parent — useful only when the sub-agent's reasoning load truly matches the parent's session.
- **`effort:`** controls how eagerly the chosen model spends thinking tokens — `low` / `medium` / `high` / `xhigh` (Opus 4.7 only) / `max`. The Claude Code Agent SDK documents `high` as "deep reasoning." Effort is independent of model: a `sonnet` sub-agent with `effort: high` thinks more deeply within sonnet's class; an `opus` sub-agent with `effort: low` economizes on opus's default thoroughness. Pick `effort:` when the sub-agent's reasoning load warrants it, regardless of model.
- **`skills:`** preloads SKILL.md *content* into the sub-agent's context at spawn — domain knowledge, rubrics, taxonomies, protocols. The `skills:` array is **not** a reasoning-depth control.

The Designer's discipline:

- For each new or modified sub-agent in the design subsection, justify the `model:` choice (why this model and not another) and the `effort:` choice (when set explicitly). State the reasoning load.
- The `skills:` array contains domain knowledge only. Every entry resolves to an existing `SKILL.md` at a discoverable location. (The auditing-subagents skill's SA-13 check enforces this — missing skill references are BLOCKER.)
- Anti-pattern to avoid: using the `skills:` array to express reasoning-depth intent (e.g., a fictional `deep-reasoning` skill). This is a category error; Claude Code's skill loader silently skips missing references, and the sub-agent runs at default reasoning while the design document claims otherwise. Map "I want this sub-agent to reason deeply" to `model:` and/or `effort:`, not to `skills:`.

A worked example from this project: the feature-pipeline uses `model: opus` uniformly across all 30 sub-agents, with the reasoning gradient shaped by `effort:` instead of by model class. Five sub-agents — `design-composer`, `review-architecture-auditor`, `review-cross-artifact-auditor`, `synth-synthesizer`, and `finalize-task-decomposer` — use `effort: xhigh` (extended reasoning) because each is a terminal compositional or gatekeeping agent whose output either composes upstream work into a load-bearing artifact (Blueprint, synthesis report, tasks.json) or gates downstream stages against unrecoverable defects (cross-artifact audit, architecture audit). The other twenty-five sub-agents use `effort: high` (deep reasoning) — each does judgment-heavy work within a bounded single-stage scope. The pipeline's per-agent reasoning configuration is intentional throughout: every choice records "the highest quality output within the context the agent is required to fulfill" as the calibration target, with `effort:` as the documented intermediate lever above default and below `xhigh`.

## Principle 10: Uniform rules over named exceptions — no carve-outs in canonical-placement rules

When a canonical-placement rule exists for an artifact class (the project's precedent: ADR-0036 mandates `adrs/` for ADRs), every file in that class lives at the canonical location. No naming-convention, extension-based, or allowlist-based exception is permitted to evade the rule. Audit trails for migrations live in `git log` and in the per-feature `migration-log.md`, never as scattered breadcrumb files at the legacy location.

The triggering anti-pattern: the `adr-placement-mechanism-repair-r1` Plan + Blueprint specified `.tombstone` redirect files at the old ADR locations so the validator's `rglob('ADR-*.md')` would skip them. The extension was chosen *specifically to evade the uniform rule*. That is the carve-out shape this principle refuses. ADR-0056 retroactively retired the tombstone files and codifies the discipline going forward.

The Designer's discipline:

- When proposing a placement convention in the Blueprint, check whether any sub-decision introduces a carve-out shape:
  - An extension-based exception to a canonical-placement rule (smell — e.g., `*.tombstone`, `*.legacy`, `*.archived` at the legacy location).
  - An allowlist entry that exists to evade a uniform rule rather than integrate two systems (smell — see below for the legitimate-allowlist test).
  - A scattered breadcrumb pattern in the legacy location (smell — replace with `git log` + a canonical migration log).
  - A "treat X as not-really-a-Y" naming convention (smell — e.g., a file named after the artifact class but excluded from validation by extension).
- If any of these is proposed, restructure to eliminate the carve-out. Default question at design review: "can we remove this entirely?"

Legitimate distinctions that are NOT carve-outs (the discriminating test):

- **A recognized structural category with its own uniform internal rule.** Example: `adrs/superseded/` (codified by ADR-0005) has its own well-defined semantics — archived bodies of replaced ADRs, validated against the same field schema. It is a category, not an exception.
- **A cross-tool integration where two systems own distinct namespaces by design.** Example: the synthesize skill writes its outputs to `output/synthesis-*/adrs/`, and `--allowlist 'output/synthesis-*/adrs/'` integrates with that distinct namespace. The allowlist exists to bridge two systems whose namespaces are independent by design, not to evade a uniform rule that should have applied uniformly.

The test for "is this a legitimate distinction or a carve-out?": does it have a uniform internal rule, or is it a one-off escape valve? Legitimate distinctions have schemas, validators, and upgrade paths. Carve-outs exist to be ignored.

The cost framing (preserved from the user's durable feedback that triggered ADR-0056): each carve-out looks small at authoring time. The aggregate compounds — five carve-outs later, the validator's scan pattern is a maze of special cases, future readers must learn each exception before they can reason about the system, and the documentation must caveat the uniform rule everywhere it's stated. The Designer pays the long-tail tax of every exception they admit.

**Reviewer enforcement.** `shared-document-reviewer` at Gate 0/1 reviews of Plan / Blueprint documents flags any proposed carve-out shape and cites ADR-0056. Future updates to the auditor / reviewer machinery make this enforcement load-bearing rather than aspirational.

**Cross-references.** ADR-0056 (the canonical statement); ADR-0036 (the precedent canonical-placement rule); ADR-0005 (the `adrs/superseded/` category that demonstrates the "structural category with uniform rule" pattern); ADR-0054 (canonical-helper three-surface enforcement — the integration shape that ADR-0056 is consistent with).
