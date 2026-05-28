---
id: PROPOSAL-auditing-family-graduation-review
doc_type: issue-proposal
status: wontfix-with-rationale
since: 2026-05-23
decided_at: 2026-05-27
wontfix_rationale: User declined to pursue further graduations during the 2026-05-27 unbiased-status review. Reasoning that stuck — the only sibling with a strong case for graduation (`auditing-mcp`) was graduated in `devcontainer-mcp-provisioning-r1`; `auditing-github-actions` and `auditing-codespaces` already sit outside the `auditing-cc-configs` family list. Three siblings the analysis labelled "Weak — stays in family" (auditing-skills, auditing-context-files, auditing-subagents, auditing-settings) do not warrant the structural-churn cost. The one ambiguous case (`auditing-hooks`) carries a security-distinct failure domain but has no active cross-feature reuse evidence; if such evidence surfaces later (e.g. a hook-only audit invocation outside the coordinator), a new Issue captures it then. The two "already distant" cases (`auditing-github-actions` formal confirmation, `auditing-codespaces` stub-fill placement) are best handled when the stub-fill itself is scheduled. No active cost, no forcing function — close.
version: 0.2.0
generated: 2026-05-23
generated_by: claude (orchestrator) — captured from Gate-4 decision in devcontainer-mcp-provisioning-r1
feature_slug: devcontainer-mcp-provisioning-r1
scope: pipeline-wide (not feature-scoped)
mode: report-only
companion_artifacts:
  - working/feature/devcontainer-mcp-provisioning-r1/blueprint-v2.md (OI-2 in §Open Items)
  - .claude/skills/auditing-cc-configs/SKILL.md (current family coordinator)
  - .claude/skills/auditing-mcp/SKILL.md (the first skill being graduated)
  - .claude/skills/auditing-shared/SKILL.md (existing cross-family utility home)
proposes_future_feature: auditing-family-structure-review-r1 (suggested slug)
---

# Proposal — Should the Other `auditing-*` Skills Also Graduate to Their Own Families?

## TL;DR

The `devcontainer-mcp-provisioning-r1` feature, at Gate 4, decided to **graduate `auditing-mcp` from the `auditing-cc-configs` family into its own `auditing-mcp` family** (OI-2 Path A — overriding the design-composer's "minimum convention change" Path B recommendation). This is the first time a sub-skill in that family has been promoted to coordinator status, and it sets a precedent: *if `auditing-mcp` warrants its own family, do the other six sub-skills warrant the same?*

The question is **not** "should we graduate them all" — graduating everything dissolves the coordinator pattern entirely, which would be a different (and more expensive) decision. The question is **which subset warrants graduation**, on what criteria, and what does the resulting structure look like.

**This proposal does not answer the question.** It captures the question for a future pipeline run — `auditing-family-structure-review-r1` (suggested slug) — and documents the inputs that run should consider so it doesn't start cold.

---

## 1. Precedent — what `devcontainer-mcp-provisioning-r1` decided

### 1.1 The decision

Gate-4 user decision on OI-2 (per checkpoint.json and the user's verbatim Gate-4 response):

> "graduate and then write an issue on whether we need to look at github codespace and the others in an issue report under Issues/ for future consideration of a pipeline run"

Composer's pre-decision recommendation had been **Path B** ("stay in `auditing-cc-configs` family — minimum convention change"). The user chose **Path A** (graduate). The user's stated reasoning, paired with their OI-3 hard-gate decision, treats MCP as a distinct enough risk surface to deserve its own coordinator (silent MCP failures break devcontainer/docker — *not* a `.claude/`-config-correctness concern, which is what `auditing-cc-configs` covers).

### 1.2 Why this precedent matters for the other sub-skills

The current family structure (per `auditing-cc-configs/SKILL.md` lines 144–153) is:

```
auditing-cc-configs  (coordinator)
├── auditing-skills          — SKILL.md files, slash commands
├── auditing-context-files   — CLAUDE.md, rules, auto memory
├── auditing-subagents       — agent files, subagent persistent memory
├── auditing-hooks           — hook configuration and hook scripts
├── auditing-settings        — settings.json (all scopes), output styles
└── auditing-mcp             — .mcp.json, optional runtime audit  ← GRADUATING
```

Plus two siblings that **already sit outside** the family coordinator:

- `auditing-github-actions` — workflow security pinning, OIDC, secrets discipline
- `auditing-codespaces` — STUB skill, reserved for devcontainer audit machinery

Plus one **shared-utility** home that supports the family but is not itself audited:

- `auditing-shared` — cross-audit-module helpers (per ADR-0031)

If `auditing-mcp` is conceptually distant enough from "Claude Code project config correctness" to warrant graduation, the same argument plausibly applies to several siblings — but with different strength per sibling.

---

## 2. Per-skill candidate analysis (inputs for the future run)

The future pipeline run should evaluate each candidate against three criteria:

- **Distance from "Claude Code config correctness" mission** — does this sub-skill audit something materially different from "is this `.claude/` directory well-formed"? (The further the distance, the stronger the case for graduation.)
- **Failure-domain blast radius** — does a BLOCKER from this skill affect the same blast radius as a `.claude/` misconfiguration, or a different one (devcontainer breakage, CI failure, secret leak, etc.)?
- **Cross-feature reuse pattern** — is this skill invoked outside `auditing-cc-configs` coordinator dispatch (i.e., do feature pipelines call it directly)?

| Sub-skill | Distance from cc-config mission | Failure-domain blast radius | Cross-feature reuse | Initial-pass case for graduation |
|---|---|---|---|---|
| **auditing-skills** | Same domain — SKILL.md correctness *is* `.claude/` correctness | Same: skill won't trigger / loads broken | Tightly coupled to coordinator | **Weak** — stays in family |
| **auditing-context-files** | Same domain — CLAUDE.md / rules / memory *is* `.claude/` correctness | Same: Claude ignores rules / context bloat | Tightly coupled | **Weak** — stays in family |
| **auditing-subagents** | Same domain — agent files *are* `.claude/agents/*.md` | Same: agent misroutes / memory leaks | Tightly coupled | **Weak** — stays in family |
| **auditing-hooks** | Adjacent — hooks fire shell scripts (CVE-class risk) | Distinct: arbitrary code execution at hook events | Some — hook-only audits exist | **Medium** — graduation plausible on security-distinct-domain grounds |
| **auditing-settings** | Same domain — settings.json *is* `.claude/` config | Same: permission-rule misconfig, env leak | Tightly coupled | **Weak** — stays in family |
| **auditing-mcp** | Distant — MCP servers are external processes with their own protocol, credentials, supply-chain | Distinct: devcontainer/docker breakage, supply-chain compromise | Yes — invoked directly per `devcontainer-mcp-provisioning-r1` | **Strong** — **graduated in r1** (this feature) |
| **auditing-github-actions** | Already separate — CI/CD workflow security | Distinct: pipeline compromise, OIDC misuse | Yes — workflow-only audits | **Already de-facto graduated** (sits outside `auditing-cc-configs` family list today) — formal status should be confirmed |
| **auditing-codespaces** (STUB) | Distant — devcontainer.json + lifecycle hooks are runtime environment, not `.claude/` config | Distinct: dev-env breakage, secrets-in-image | Will be invoked directly when filled (per ADR-0033) | **Strong** — when the stub is filled, graduation is the obvious posture; mirrors `auditing-mcp` |

### Read

- **Three "tightly coupled to coordinator" siblings** (`auditing-skills`, `auditing-context-files`, `auditing-subagents`, `auditing-settings`) — initial-pass read is **stay in family**. The coordinator's mission ("is this `.claude/` directory well-formed") matches their mission exactly. Graduating them would dissolve the coordinator pattern.
- **One ambiguous case** (`auditing-hooks`) — same family today, but the failure domain (arbitrary code execution at hook events) is materially distinct from "config correctness." The future run should decide on either security-distinct-domain grounds or cross-feature-reuse evidence.
- **Two "already distant" cases** (`auditing-github-actions`, `auditing-codespaces`) — these already sit outside the `auditing-cc-configs` family list in the coordinator's `## Sub-skill family` section. Their formal status is "siblings of the family coordinator, not members." The future run should:
  - Confirm `auditing-github-actions` is a fully-graduated family in its own right (or document why not).
  - Plan, at `auditing-codespaces` stub-fill time, to graduate it directly into its own family rather than slotting it under `auditing-cc-configs` (mirroring `auditing-mcp` r1 precedent).

---

## 3. What "graduation" actually entails

For the future run to size the work, here is what `auditing-mcp` graduation will involve in `devcontainer-mcp-provisioning-r1` (per Blueprint v3 — being authored now):

1. **Frontmatter change** — `auditing-mcp/SKILL.md` frontmatter `family` field changes from `auditing-cc-configs` to `auditing-mcp`.
2. **Coordinator role declaration** — `auditing-mcp/SKILL.md` body adds a `## Sub-skill family` section (even if empty initially) and the "coordinator dispatches to" pattern.
3. **`auditing-cc-configs` coordinator update** — remove `auditing-mcp` from its `## Sub-skill family` section (lines 144–153); document the graduation rationale inline.
4. **`auditing-shared` ADR-0031 cross-ref update** — its description currently lists "auditing-cc-configs, auditing-skills, auditing-subagents, auditing-context-files" as consumers; add `auditing-mcp` as a now-independent family-coordinator consumer (and any others that graduate in the future run).
5. **Cross-file pair-check coverage** — `auditing-cc-configs/references/cross-file-checks.md` (if it exists) may have MCP-relevant checks that now belong in the new `auditing-mcp` family's coverage list; verify and migrate as appropriate.
6. **Discovery / orchestration impact** — the feature-pipeline orchestrator's references to "the auditing family" need to handle multiple families cleanly (singular → plural convention drift).

This is **bounded but non-trivial work per graduated skill** — and item 6 (orchestrator-side) is paid once regardless of how many skills graduate, so the marginal cost of graduating two more (e.g., `auditing-hooks` + future-`auditing-codespaces`) on the same future run is smaller than graduating them in three separate runs.

---

## 4. Recommended scope for the future pipeline run

Suggested feature slug: **`auditing-family-structure-review-r1`**.

Suggested in-scope:

- Audit the current family structure (the 7-row table above) and produce a per-skill graduation decision with rationale.
- Define a **graduation criteria rubric** (formalize the three criteria in §2 or replace with a better-grounded set) so future audit-skills additions have a clear placement decision.
- Author the structural changes for any skills the run decides to graduate (frontmatter, coordinator sections, shared-utility cross-refs, orchestrator updates).
- Document the `auditing-codespaces`-stub-fill posture so when that stub is filled (per ADR-0033), the family-placement decision is pre-made.

Suggested out-of-scope:

- Re-evaluating `auditing-mcp`'s graduation (it is decided in `devcontainer-mcp-provisioning-r1`; the future run inherits this as given).
- Dissolving the `auditing-cc-configs` coordinator entirely (a more expensive decision; if the future run concludes most siblings should graduate, that conclusion can trigger a separate follow-up).
- Modifying the `auditing-shared` utility's API surface (per ADR-0031, this is the shared-utility home; structural changes there are a separate concern).

Suggested gating considerations for the future run:

- **Reviewer scrutiny on coordinator pattern erosion** — if graduating one more sibling (say `auditing-hooks`) leaves the coordinator with only three sub-skills, the pattern is at risk of becoming purely vestigial. The future run should explicitly decide what the minimum useful coordinator size is, or accept dissolution as the eventual end state.
- **Cross-feature reuse evidence** — the strongest case for graduation is "this skill is already invoked directly by features outside the coordinator's mission." The future run should grep the feature-pipeline run history for direct invocations of each sub-skill and weight accordingly.

---

## 5. Why this lives here (not in `working/feature/devcontainer-mcp-provisioning-r1/`)

Per user feedback memory `feedback_artifact_placement.md`: artifacts that are *pipeline-wide* in scope (i.e., not produced by or consumed by the feature run itself) belong in `Issues/`, not in `working/feature/<slug>/`. This proposal:

- Is **triggered by** the `devcontainer-mcp-provisioning-r1` Gate-4 decision (OI-2).
- Is **not consumed by** that feature's plan-author, test-author, or task-decomposer (the feature scope ends at graduating `auditing-mcp` only).
- Is **a proposal for a future pipeline run** — exactly the case `Issues/` exists for, alongside the two existing analysis reports.

The companion artifact list in this proposal's frontmatter cross-references the feature run's blueprint so a future reader can trace the precedent back to its origin without that feature's working directory being load-bearing for this proposal's interpretation.

---

## 6. Cross-references

- **Precedent decision**: `working/feature/devcontainer-mcp-provisioning-r1/blueprint-v2.md` §Open Items — OI-2 disposition (Path A, user override at Gate 4).
- **Existing family coordinator**: `.claude/skills/auditing-cc-configs/SKILL.md` lines 144–153.
- **Existing graduated-sibling precedent**: `.claude/skills/auditing-github-actions/SKILL.md` and `.claude/skills/auditing-codespaces/SKILL.md` already sit outside the `auditing-cc-configs` family list.
- **Shared-utility convention**: `.claude/skills/auditing-shared/SKILL.md` and ADR-0031 (which formalized the cross-audit-module utility pattern).
- **Pipeline gap context** (separate but related): `Issues/analysis-per-agent-design-evaluation-gap.md` — why structural decisions like this are easy to miss in design without an explicit demand-driven sweep.
