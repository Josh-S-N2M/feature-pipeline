---
name: disable-model-invocation-skills-test-pattern
description: When a feature uses `disable-model-invocation: true` skills paired with a sub-agent that runtime-loads them, the canonical acceptance-test pattern is a verbatim `grep -E '^skills:'` against the agent file returning zero matches — this is a load-bearing F-003 BLOCKER mitigation per `.claude/skills/auditing-subagents/references/subagent-spec.md` line 110.
metadata:
  type: feedback
---

**Rule.** When authoring acceptance tests for a feature that introduces:
- One or more skills with `disable-model-invocation: true` in their SKILL.md frontmatter, AND
- A sub-agent that loads those skills at runtime (Read/Glob, not via `skills:` preload),

include a structural test that runs a verbatim `grep -E '^skills:' .claude/agents/<agent-name>.md` and asserts zero matches. Cross-link this test to the agent-authoring task's L1 verification (the Plan author should already have this as a load-bearing exit criterion).

**Why:** Per `.claude/skills/auditing-subagents/references/subagent-spec.md` line 110 (F-003 in the issue-capture-mechanism-r1 codebase-analysis): if a `disable-model-invocation: true` skill appears in a sub-agent's `skills:` frontmatter preload, Claude Code SILENTLY drops the skill from the agent's preload — the agent then has no error message but is functionally broken (its KB is not loaded). This is a BLOCKER class defect that produces no observable error at agent-start, only a quiet behavioral failure during execution. A frontmatter-level grep is the cheapest and most direct mitigation; `auditing-subagents` cross_file_checks X3 also enforces it at audit time, but the verbatim grep at acceptance-test layer provides defense-in-depth.

**How to apply:**
- Add an AT-NNN test of type "structural (grep)" with the verbatim grep command.
- Phrase the expected outcome as "exit code 1 (no matches)" — any match is a BLOCKER.
- Cross-reference the test to the Plan's Phase Validator (which should run the same grep at phase-exit).
- If the feature has multiple such runtime-loaded skills + agents, add one grep test per agent.
- The test belongs in the "structural" category, not "unit" — it is checking a project-level invariant, not function behavior.

See `working/feature/issue-capture-mechanism-r1/acceptance-tests.md` AT-068 for the canonical realization on the `issue-capture-author` sub-agent.
