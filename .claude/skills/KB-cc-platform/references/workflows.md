# Workflows and best practices

The patterns that consistently produce good results with Claude Code, drawn from the official best-practices and common-workflows pages. Load this when advising on how to *use* Claude Code well — not just what it can do.

For mechanism details, see the other reference files. This is the playbook layer.

## Contents

- The single most important pattern: explore → plan → code
- Test-driven development
- Parallel sessions and worktrees
- Subagents for context isolation
- Multiple specialized agents
- Custom slash commands for repeatable workflows
- Model selection
- Cost management
- Common workflows
- Working with long sessions
- Pre-commit and CI integration
- Working from anywhere
- Anti-patterns to flag
- Where to find more

## The single most important pattern: explore → plan → code

The biggest quality lift comes from separating **discovery** from **execution**. Every nontrivial task should go through three phases:

1. **Explore.** Read code, run searches, understand the surrounding system. No edits.
2. **Plan.** Write down the approach. Identify risks, edge cases, ordering constraints.
3. **Code.** Implement the plan. Run tests. Verify.

Why it matters: when Claude jumps straight to editing, it tends to fix symptoms rather than causes, miss interactions with adjacent code, and need rework. Forcing the explore-and-plan steps gives the model time to load enough context that the implementation actually fits the system.

**How to enforce it.** Use **plan mode** for the discovery phase:

```bash
claude --permission-mode plan
```

Plan mode is read-only. Claude can read, search, run safe diagnostic commands, and produce a written plan but cannot edit anything. You review the plan, then switch to `default` or `acceptEdits` for implementation:

```
[in plan mode] Refactor the auth module to use OAuth2. Produce a migration plan with backward compatibility considerations.

[after reviewing the plan, Shift+Tab to switch mode]

Implement the OAuth flow from your plan. Write tests for the callback handler, run the test suite, and fix any failures.
```

You can return to plan mode mid-task whenever a tricky decision comes up.

For longer-form discussion: `https://code.claude.com/docs/en/best-practices.md` and `https://code.claude.com/docs/en/how-claude-code-works.md`.

## Test-driven development

Claude Code is unusually good at TDD because it can run tests in a loop and react to output. The pattern that works:

1. Describe the feature and the test you want
2. Have Claude write the test first, run it, confirm it fails for the right reason
3. Have Claude implement until the test passes
4. Have Claude refactor with the test as a safety net

```
Write a test for a function that parses ISO 8601 durations into seconds.
Run the test, confirm it fails, then implement the function and get it passing.
Add edge cases for negative durations and weeks.
```

This sequence works headlessly too:

```bash
claude -p "Write tests for the auth module, run them, and fix any failures" \
  --allowedTools "Bash,Read,Edit,Write" \
  --permission-mode acceptEdits
```

## Parallel sessions and worktrees

For independent tasks that should run side by side without polluting each other's context, use git worktrees:

```bash
claude --worktree    # Spawn a session in a fresh worktree
```

Each worktree is its own working directory backed by the same repository, so two sessions can edit different feature branches simultaneously without stepping on each other's files or context.

`.worktreeinclude` (project root, gitignore syntax) lists files to copy into each new worktree — `.env`, secrets, local config that gitignored files depend on. Without this, worktrees start as fresh checkouts and missing untracked files break local builds.

The Desktop app has a built-in parallel-sessions UI that uses worktrees under the hood. See `references/integrations.md` for desktop specifics.

## Subagents for context isolation

The single largest source of context bloat is reading lots of files to answer one question. The fix is a subagent.

When to delegate to a subagent:
- The work needs to read 10+ files but the main session only needs the conclusion
- You want a specialized worker with restricted tools (e.g. read-only reviewer)
- The work has a well-defined interface (input → output) that does not need ongoing dialogue
- Multiple things can run in parallel

When **not** to delegate:
- The main conversation will need the intermediate findings later
- The task is small enough that the spawn overhead is not worth it
- You need ongoing dialogue with the user during the work

Subagents inherit nothing from the main conversation by default — only what you pass in the prompt and what the subagent's `skills:` field preloads. Design the subagent's prompt and skill list to be self-sufficient.

For subagent design details: `references/extensions.md` section 4.

## Multiple specialized agents

A real Claude Code setup typically has several subagents, each with a clear specialty:

| Agent | Role | Tool access |
|---|---|---|
| `code-reviewer` | Reviews diffs for correctness, security, maintainability | Read-only (`Read, Grep, Glob`) |
| `test-runner` | Runs and analyzes test suites | `Bash, Read, Grep` |
| `security-auditor` | Scans for vulnerabilities | Read-only |
| `refactor-planner` | Produces refactor plans without executing them | Read-only |
| `doc-writer` | Updates docs to match code changes | `Read, Edit, Write` |

The lead agent decides which to invoke. Restrict tools (`tools:` frontmatter) so agents that should not edit anything literally cannot. This is enforcement, not suggestion.

## Custom slash commands for repeatable workflows

Anything you do more than twice should probably be a skill (or a single-file command) with a `/<name>` trigger. Common ones teams build:

| Skill | Purpose |
|---|---|
| `/review` | Run the team's code review checklist on the current diff |
| `/deploy` | Build, run tests, deploy to staging (often `disable-model-invocation: true`) |
| `/fix-issue <number>` | Fetch GitHub issue, investigate, fix, write tests, summarize |
| `/audit` | Spawn security, performance, and style subagents in parallel |
| `/release-notes` | Diff the last release tag, draft release notes |
| `/db-query <question>` | Use MCP database tools to answer a question with grounded data |

The `!`<cmd>`` bash injection pattern lets a skill ground itself in current state:

```markdown
---
description: Investigate and fix a GitHub issue
argument-hint: <issue-number>
---

!`gh issue view $ARGUMENTS`

Investigate the issue above. Trace to root cause, implement the fix, write tests, summarize what you changed and why.
```

For skill design: `references/extensions.md` section 3.

## Model selection

Claude Code supports multiple models. The right choice depends on cost, speed, and capability needs.

| Alias | When to use |
|---|---|
| `opus` | Hardest tasks: large refactors, complex debugging, architecture work |
| `sonnet` | The everyday default. Fast and capable for most coding work |
| `haiku` | Simple tasks, cheap orchestration, high-volume scripted work |
| `opusplan` | Hybrid: opus for planning phases, switches to a faster model for execution |

Set per-session with `--model`, per-project with `model` in `settings.json`, per-skill with `model:` frontmatter, per-subagent with `model:` frontmatter.

**Fast mode** (`/fast` or `--fast`) speeds up Opus responses with a different inference path. Useful when iterating quickly. Toggle per-session.

For details: `https://code.claude.com/docs/en/model-config.md` and `https://code.claude.com/docs/en/fast-mode.md`.

## Cost management

Token costs add up fast in long sessions and parallel agent setups. Tactics that work:

- **`/context` early and often** to see what is consuming tokens
- **`/compact`** to summarize older messages when the window fills
- **Subagents for heavy reads** — their context is isolated and discarded after the summary returns
- **`disable-model-invocation: true`** on skills with side effects so their content does not load proactively
- **MCP tool search** (on by default) keeps idle MCP tool schemas out of context
- **Path-gated rules** instead of unconditional rules
- **CLAUDE.md under 200 lines** — the same content as path-gated rules costs less
- **Smaller models** for orchestration agents that route work
- **`--max-turns`** in headless mode to bound runaway loops
- **Pre-processing hooks** (e.g. UserPromptSubmit) that inject only the right context based on the prompt

For deeper coverage: `https://code.claude.com/docs/en/costs.md`.

## Common workflows

Patterns that come up over and over.

**Onboarding to a new codebase:**
```
Read the README and main entry point. Map the high-level architecture.
Then read the auth module specifically — I need to understand how sessions work.
Produce a one-page architecture summary.
```
Run in plan mode. The output becomes the basis of the project's CLAUDE.md or a memory file.

**Fixing a bug from an error message:**
```
[paste error]
Trace this through the codebase, identify the root cause, and propose a fix.
```
Plan mode for the trace, then switch to implement.

**Refactoring across many files:**
```
[in plan mode] We need to rename `getUserById` to `findUser` everywhere it appears,
and change the signature to return null instead of throwing on miss. Plan the migration.
```
Review the plan. Switch modes. Execute. Run tests.

**Adding a feature with tests:**
```
Add a /export endpoint that returns the user's data as JSON. Write the test first,
get it failing for the right reason, implement until it passes, then add edge cases
for unauthenticated users and rate limiting.
```

**Reviewing a pull request:**
```bash
git checkout pr-branch
claude "Review this branch against main. Focus on security, error handling, and tests."
```
Or via GitHub Actions for automated PR review (covered in your separate GitHub Actions skill).

**Triage and dependency updates:**
```
Run npm outdated. For each major-version update, check the changelog and tell me
which are safe to update and which need code changes. Update the safe ones and
run the test suite.
```

For more workflow examples: `https://code.claude.com/docs/en/common-workflows.md`.

## Working with long sessions

Long sessions degrade as the context fills. Strategies in order of preference:

1. **`/compact`** — summarizes older messages, keeps the recent thread intact
2. **Spawn subagents** for self-contained pieces of work to keep them out of the main context
3. **End and resume with a summary** — wrap up the session with a written summary, start fresh, paste the summary
4. **Use checkpoints to roll back** when an edit loop went wrong, without losing the conversation context that explains what was being attempted

For checkpoint mechanics: `references/cli-and-headless.md`.

## Pre-commit and CI integration

For lightweight automation, use `claude -p` in scripts. For heavier integration:

- **Pre-commit hooks** — `claude -p "Lint this diff and suggest fixes" --allowedTools Read --output-format json`, then act on the JSON
- **CI** — covered in your separate GitHub Actions skill
- **Hooks (lifecycle)** — for in-session automation: format on edit, run tests on stop, etc. See `references/extensions.md` section 5.

## Working from anywhere

Claude Code sessions are not tied to one surface. Useful handoffs:

| Scenario | Tool |
|---|---|
| Step away from desk, continue on phone | Remote Control |
| Long task you want to run while away | Web (claude.ai/code) or iOS app |
| Started locally, want to continue mobile | `claude --teleport` on the receiving end |
| Switch terminal session to visual diff review | `/desktop` |
| Trigger Claude from Slack mention | Slack integration |
| Push external events into a session | Channels (MCP-based) |

For details: `references/integrations.md`.

## Anti-patterns to flag

When reviewing setups, watch for these:

| Smell | Fix |
|---|---|
| CLAUDE.md over 300 lines | Move topic-scoped content to `.claude/rules/`, reference content to skills |
| Skill with vague description ("Helps with stuff") | Rewrite description to name explicit triggers ("Use whenever the user mentions X, Y, Z") |
| Subagent that needs main session's context | Pass the context in the spawn prompt, or preload skills explicitly |
| Same task done by hand repeatedly | Make it a skill |
| Hooks doing what permissions could do | Move static rules to `permissions.deny` — simpler |
| Permissions doing what hooks should | Move dynamic logic to a PreToolUse hook |
| MCP server connected but unused | Disconnect — schemas may not load (deferred), but server processes still run |
| `bypassPermissions` outside a sandbox | Almost always wrong; reach for sandboxed mode instead |
| Multiple agents with overlapping descriptions | Tighten descriptions or merge agents |
| `disable-model-invocation: true` missing on side-effect skills | Add it; otherwise Claude may run the skill autonomously |

## Where to find more

- Best practices (canonical) — `https://code.claude.com/docs/en/best-practices.md`
- How Claude Code works — `https://code.claude.com/docs/en/how-claude-code-works.md`
- Common workflows — `https://code.claude.com/docs/en/common-workflows.md`
- Cost management — `https://code.claude.com/docs/en/costs.md`
- Model configuration — `https://code.claude.com/docs/en/model-config.md`
- Agent teams (parallel coordinated sessions) — `https://code.claude.com/docs/en/agent-teams.md`
