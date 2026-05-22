---
name: kb-cc-design
description: >-
  Design discipline for the Claude Code / Project Filesystem layer. Pairs with
  KB-cc-platform (the platform half). Covers when to choose each Claude Code
  primitive (CLAUDE.md vs. rule vs. skill vs. subagent vs. hook vs. MCP server
  vs. plugin vs. output style), how to evolve an existing configuration,
  context-cost discipline, isolation boundaries, and the per-layer designer's
  workflow for producing the Claude Code Design subsection of a Blueprint. Use
  when the feature touches anything inside .claude/, including custom slash
  commands, agents, skills, hooks, MCP integrations, or plugins.
allowed-tools: Read, Grep, Glob
pedagogical_sections:
  - path: references/patterns-and-anti-patterns.md
    justification: "Design-patterns reference for Claude Code; references canonical .claude/CLAUDE.md and agent-memory paths the auditor flags as broken (paths exist in target projects, not this meta-repo)"
---

# KB-cc-design — Claude Code Layer Design Discipline

Design discipline for the Claude Code / Project Filesystem layer. The per-layer Claude Code Designer (`design-cc`) loads this KB during per-layer Design to produce the `### Claude Code Design` subsection of the Blueprint. This is the **design half** of the cc skill pair — KB-cc-platform is the platform half (facts, configuration syntax, current-details lookup). Load both for design work; load just KB-cc-platform for syntax / reference questions.

## Contents

- When this KB is loaded
- The layer's responsibility
- Design decisions this layer owns
- Patterns and anti-patterns at a glance
- Interaction with other layers
- Surfacing architectural questions
- When to load each reference file

## When this KB is loaded

This KB is in scope when:

- A feature's PRD or Blueprint declares the **Claude Code / Project Filesystem** layer in scope (per `layer-taxonomy.md` in KB-documentation-criteria)
- A per-layer Designer is producing the Claude Code Design subsection of the Blueprint
- The change involves choosing between Claude Code primitives, NOT just modifying an existing one with known shape
- Plan Authoring produces tasks that introduce or refactor `.claude/` artifacts in a way that requires design judgment

Sub-agents that reference this KB (per Blueprint v4.3.1):

- `design-cc` (per-layer Design, when CC / Project Filesystem layer is in scope)
- `design-composer` (Design Composition, integrating CC design with cross-cutting concerns)
- `plan-author` (when tasks introduce new CC artifacts of non-trivial complexity)
- `shared-document-reviewer` (Gate 1 CC-specific checks)

This KB and KB-cc-platform are designed to load together — they overlap minimally. The design KB teaches discipline; the platform KB teaches facts.

## The layer's responsibility

The Claude Code layer owns how Claude Code is configured for this project: which primitives exist, how they're scoped, what they do. The Designer makes decisions about:

- **Primitive selection.** Of the seven extension primitives (CLAUDE.md, rules, skills, subagents, hooks, MCP servers, plugins) plus output styles, which one fits this need?
- **Scope choice.** Project-level (`.claude/`) or user-level (`~/.claude/`)? Plugin-distributed?
- **Context-cost trade-offs.** Every CLAUDE.md line, every always-loaded rule, every always-listed skill costs tokens on every request. The Designer weighs cost against benefit.
- **Isolation boundaries.** When does a workflow need its own subagent (fresh context window)? When does shared context across the conversation matter?
- **Determinism vs. instruction.** When does the behavior need to be guaranteed (hook, permission deny rule) vs. requested (instruction in CLAUDE.md or a skill)?
- **Sharing model.** What's committed to the repo (everyone gets it); what's user-specific; what's enterprise-managed.

The Claude Code Designer does NOT own:

- The platform facts (settings.json schema, hook event names, CLAUDE.md precedence rules). Those are in KB-cc-platform.
- Application-domain logic. A skill that captures "how to deploy our service" is a CC artifact; the deploy process itself is the Backend / IaC layer's concern.
- The CI/CD integration of Claude Code Actions. That's the CI/CD layer (`KB-github-actions-design`).

## Design decisions this layer owns

The CC Designer makes (or surfaces) these decisions:

| Decision | Forced if … |
|---|---|
| Which primitive solves the need | Any new CC artifact is being added |
| Scope (project / user / plugin) | A new artifact is being added |
| Always-loaded vs. on-demand | The artifact will impact context cost |
| Auto-invocable vs. user-invoked (skill) | New skill is being added |
| Restricted tool set (subagent) | New subagent is being added |
| Persistent agent memory (subagent) | New subagent needs across-run state |
| Enforced vs. instructed | Behavior is safety- or compliance-critical |
| Permission model | Mutating tools available; risks need to be bounded |
| Hooks vs. permissions for blocking behavior | Need to prevent specific commands/actions |
| MCP scope (local / project / user) | A new MCP server is being added |
| Plugin bundling | Multiple related artifacts are being distributed together |
| Migration path from old commands | Project has legacy `.claude/commands/*.md` |
| Refactoring CLAUDE.md | CLAUDE.md exceeds healthy size |

Designers do NOT author ADRs (per FR-5). Cross-cutting CC decisions (canonical skill-vs-command policy, plugin governance) surface as open items.

## Patterns and anti-patterns at a glance

The full discipline lives in `references/principles.md` and `references/patterns-and-anti-patterns.md`. Quick reference:

**Patterns to favor:**

- **Pick the lowest-cost primitive that does the job.** Hooks cost zero context; deferred MCP tool schemas cost zero until invoked; skills with `disable-model-invocation: true` cost zero until invoked; user-loaded skills cost only their description per request; CLAUDE.md costs every line every request.
- **Path-gate rules.** Rules with `paths:` load only when matching files enter context, vs. unconditional rules that load every session.
- **Isolate context with subagents.** When work reads many files but only the summary matters, a subagent reads-and-summarizes without polluting the main context.
- **Enforce when safety-critical; instruct when guidance-critical.** Hooks and `permissions.deny` are enforced by Claude Code regardless of the model's decision. CLAUDE.md and rules are followed-usually-but-not-guaranteed.
- **Bundle related primitives in plugins** for cross-project distribution.
- **Migrate `commands/*.md` to `skills/<name>/SKILL.md`.** Skills can bundle supporting files; single-file commands cannot.
- **Configure sub-agent reasoning intentionally.** Pick `model:` and (where warranted) `effort:` per sub-agent based on the reasoning load. `skills:` is for domain knowledge only — never for reasoning-depth control.

**Anti-patterns to flag:**

- **A 500-line CLAUDE.md.** Every line costs tokens every request. Move reference material to skills.
- **Unconditional rule for file-specific guidance.** Rules without `paths:` load every session even when the relevant files aren't in scope.
- **Subagent for work that fits in 50KB of context.** Subagents have setup cost; small jobs don't recoup it.
- **Hook for non-deterministic guidance.** Hooks are shell scripts; they don't reason. If the desired behavior depends on context (e.g., "ask user when X"), a hook is the wrong tool.
- **Skill duplicating CLAUDE.md.** Two sources of truth drift.
- **Plugin distributing single skill.** The packaging overhead exceeds the benefit; just commit the skill.
- **Sub-agent `skills:` array used to express reasoning depth** (e.g., `skills: [deep-reasoning, …]`). Category error — `deep-reasoning` is treated as a literal skill identifier; missing references load silently as nothing. Map reasoning-depth intent to `model:` and `effort:` fields.

## Interaction with other layers

```
[CC layer] ──configures──► The Claude Code session the developer uses
     │
     ├──can-invoke──► CI/CD (claude-code-action in GitHub Actions)
     │
     └──can-invoke──► MCP servers ──► external services
```

The CC Designer's responsibility:

- **CI/CD** — Claude Code can run in CI via `claude-code-action`. The CC Designer documents which skills / agents are usable from CI (those need `allowed-tools` scoped appropriately). The CI/CD Designer integrates.
- **Backend / Frontend / Query / Database / IaC** — these layers don't directly interact with CC, but the project's CC configuration (skills, agents, hooks) often EMBEDS knowledge from these layers. A "backend-conventions" skill captures Backend layer norms. The CC Designer ensures the embedding stays current as the layers evolve (skill content is a maintenance burden).
- **MCP servers** — external services Claude Code connects to. The CC Designer documents the server scope and the security implications.

## Surfacing architectural questions

```markdown
## Architectural Questions for Composer

- **Q-CC-1**: Should we adopt a project-wide plugin to bundle our four custom skills + three subagents + two hooks? Currently each lives independently in `.claude/`. The choice affects the developer-onboarding flow (a plugin can be installed with one command vs. per-file copies) and the cross-project share-ability. Evidence: 3 sister projects could benefit from the same configuration. Options: (a) author and publish a plugin; (b) keep flat structure and use a setup script; (c) status quo (each developer copies what they need). Recommended: (a). Defer to composer.
```

## When to load each reference file

| Load this file | When the task involves |
|---|---|
| `references/principles.md` | Authoring or reviewing a CC Design subsection — covers the foundational principles (cost-conscious selection, path-gating, enforce-vs-instruct, isolation via subagents, plugin packaging, sub-agent reasoning configuration) |
| `references/patterns-and-anti-patterns.md` | Choosing between primitives, refactoring CLAUDE.md, migrating from commands, scoping permissions — covers common design patterns with when-to-use and the anti-patterns reviewers should flag |
