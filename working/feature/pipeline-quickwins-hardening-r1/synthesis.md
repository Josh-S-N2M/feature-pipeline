---
id: synthesis-pipeline-quickwins-hardening-r1
version: 1.0.0
feature_slug: pipeline-quickwins-hardening-r1
doc_type: synthesis
stage: synthesis
step: composition
generated: 2026-05-26T00:00:00Z
generated_by: synth-synthesizer
audience_depth: medium
mode: implementation-strategy
derived_from:
  - working/feature/pipeline-quickwins-hardening-r1/synthesis/01-claims.json
  - working/feature/pipeline-quickwins-hardening-r1/synthesis/02-graph.json
  - working/feature/pipeline-quickwins-hardening-r1/synthesis/03-critique.json
  - working/feature/pipeline-quickwins-hardening-r1/synthesis/04-decision-frames.json
  - working/feature/pipeline-quickwins-hardening-r1/synthesis/05-substrate-map.json
  - working/feature/pipeline-quickwins-hardening-r1/prd-v1.md
  - working/feature/pipeline-quickwins-hardening-r1/codebase-analysis-report.md
citation_convention: "Inline references to verified-critique IDs (codebase-C-NNNN | t001-C-NNNN | t002-C-NNNN) point into synthesis/03-critique.json. Passthrough-unverified claims appear as background context and are flagged inline; they are not load-bearing."
---

# Synthesis — Pipeline Quick-Wins Hardening (Round 1)

## 1. Executive summary

This feature closes five mechanically bounded MCP-incident exposures plus two small process items, with one additional cross-cutting diagnostic requirement (FR-6) that runs through them all. The seven functional requirements are all MINOR-scope, locally blast-radius, two-way reversible, and individually exercisable. Discovery surfaced ten open design questions; framing collapsed them into ten implementation-grade decisions, none of which clear the ADR-worthiness bar (no one-way doors, no cross-team coordination, no above-service blast radius). Synthesis recommends one implementation strategy per decision, with explicit alternatives kept on the record and two carve-out / doc-silence exclusions flagged where they applied.

The shape of the work is roughly: three Claude Code surface changes (reviewer parity guard at FR-1, orchestrator dispatch self-check at FR-2, plus an audit-rule extension at FR-3), one devcontainer dry-run (FR-4), one greenfield GitHub Actions workflow (FR-5), one cross-cutting diagnostic shape (FR-6), and one deferral-register marker tightening (FR-7). The most consequential structural findings are: scope_class is read exactly once at line 350 of recipe-feature-pipeline/SKILL.md (FR-2 has to hoist or duplicate that read); ADR-0041 still carries a seven-row install-mechanism table while `.mcp.json` carries six servers (FR-3's day-one false-positive trigger); the canonical Claude Code docs are silent on `claude mcp list`'s exit-code contract, forcing FR-5 to use a different invocation path; and the GitNexus env-var contract at v1.6.5 is strict (`=== '1'`) and does not govern Swift despite README claims to the contrary.

Two decisions rest on judgment rather than verified evidence and are flagged for user confirmation: the PR-shape choice (single bundled vs sequenced — recommendation rests on coupling analysis) and the deferral-register placement (recommendation rests on audit-trail completeness). The remaining eight rest on verified critique evidence.

## 2. Constraints honored

These constraints come from the PRD (Product Policy Decisions table, Constraints subsection, and Won't-Have list) and from the orchestrator's framing for this synthesis run. Every recommendation below respects them; departures are surfaced explicitly.

- **MINOR scope class.** The PRD ratifies scope class MINOR. Every framed decision is component-blast-radius and two-way reversible, so the recommendations stay inside the scope class. No recommendation forces a scope-class upgrade. (Source: PRD §Product Policy Decisions row 1.)

- **Carve-out boundary.** The five named mechanisms (plus FR-6/FR-7) are the entirety of this run. The eight Won't-Have items listed in the PRD are deferred. The synthesis does not recommend opportunistic expansion into any of them. Where a decision would touch a deferred area (e.g., live MCP reachability), the recommendation stays inside the carve-out. (Source: PRD §Won't Have.)

- **No ADR-text mutations.** The feature explicitly carves out ADR edits. The recommendation for D-0005 (handling the deprecated mcp-openapi-schema row in FR-3) excludes "amend ADR-0041 to drop the row" not on engineering merit but as out-of-scope by carve-out — and so flagged in the decision substrate. The recommended in-rule deprecation marker convention is an annotation pattern that adds a marker token to a table row; it is not a decision-text rewrite, and it aligns with the project's existing append-only ADR posture (ADR-0005). (Sources: PRD §Won't Have; codebase-C-0110; codebase-C-0112.)

- **No further patching of the still-broken MCP servers.** The PRD policy is explicit: until this hardening lands, the broken MCP server files do not get touched, because doing so would clear the same paper gates the original incident cleared. No recommendation in this synthesis edits any MCP server's own source. (Source: PRD §Product Policy Decisions row 4.)

- **Strictness-over-ergonomics tiebreaker.** Where a check must err in one direction, the PRD says err toward strictness (more blocking). FR-1's recommended blocking set is `{BLOCKER}` only — narrower than the strict-leaning option of `{BLOCKER, MAJOR}`. The narrower set is recommended not because the maintainer asked for laxness, but because broadening to `{BLOCKER, MAJOR}` would retroactively turn every historical APPROVED-with-MAJOR-finding output into an inconsistency. That broadening is a scope expansion that needs its own decision, not a quickwin. The strictness tiebreaker is honored at the limit by deferring the broader catch surface to a future feature, not by adopting it silently here. (Source: PRD §Product Policy Decisions row 3.)

- **Existing-output backward compatibility (NFR-9, NFR-10).** The recommended FR-1 set (`{BLOCKER}` only) is chosen partly to honor NFR-9 — any pre-existing APPROVED-with-MAJOR-finding reviewer output the prior pipeline accepted continues to pass. The recommended FR-3 algorithm (canonicalize-then-string-equal) is chosen partly to honor NFR-10 — entries that already match ADR-0041 in canonicalized form do not produce findings, and the algorithm doesn't depend on env-state so the test fixture is stable. (Source: PRD §NFR-9, §NFR-10.)

- **No new credential surface (NFR-7, NFR-8).** No recommendation here introduces a new secret, token, or env-var dependency beyond what `.mcp.json` and ADR-0041 already establish. The FR-3 algorithm leaves `${VAR}` placeholders opaque (it does not resolve them against the running environment), which has the side benefit of never reading credential values into diagnostics. (Source: PRD §NFR-7, §NFR-8.)

- **MCP event surface (NFR-13).** The recommended FR-5 invocation (`claude --bare -p ... --output-format stream-json | jq ...`) consumes the `system/init` event documented in the Claude Code Agent SDK. It does not introduce new event types into `.claude/runtime/mcp-events.jsonl`. (Source: PRD §NFR-13; t002-C-0008.)

- **NFR-15 / ADR-0040 allowlists unchanged.** No recommendation adds a new sub-agent MCP allowlist or modifies an existing one. The work stays inside the existing allowlist precedents.

## 3. Decision substrate

Ten decisions framed; ten implementation strategies recommended. Each entry below summarizes the open question, the recommended option, the rejected alternatives with rejection rationale, and citations to the verified critique IDs that drive the choice. Where a decision has no verified-claim driver (D-0008, D-0009, D-0010), that is called out explicitly.

### D-0001 — FR-1's blocking-severity set and execution site

**The question.** Which severity tokens count as inconsistent with an APPROVED verdict, and does the check run inside each reviewer agent or in a downstream hook on the emitted JSON?

**Recommended.** Blocking set = `{BLOCKER}` only; check runs out-of-agent as a single hook on the emitted JSON, downstream of every reviewer that produces a verdict+findings pair. This closes the verified parity gap with one implementation surface rather than seven, and stays inside the deterministic severity-to-verdict mapping the codebase already documents but does not enforce. (Verified: codebase-C-0016, codebase-C-0017, codebase-C-0018, codebase-C-0019, codebase-C-0020.)

**Why narrower than `{BLOCKER, MAJOR}`.** Including MAJOR would broaden the definition of "inconsistent with APPROVED" beyond what today's deterministic mapping says. Every historical APPROVED-with-MAJOR-finding output would retroactively be inconsistent. That broadening is a scope expansion that warrants its own decision, not a quickwin. The strictness tiebreaker in PRD §Product Policy Decisions row 3 is honored by leaving the question open for a future feature rather than by silently adopting the broader set here. The PRD's NFR-9 (existing reviewer outputs the prior pipeline accepted must continue to pass) is also load-bearing here.

**Why out-of-agent rather than in-agent.** In-agent self-validation multiplies the implementation surface by the seven agents that emit verdict+findings shapes (`shared-document-reviewer`, `review-architecture-auditor`, `review-cross-artifact-auditor`, `execute-phase-quality-reviewer`, `execute-task-quality-handler`, `finalize-deliverable-packager`, `synth-critic`). Future reviewers added to the project would need the same edit. A single downstream hook gives the same guarantee at one-seventh the maintenance cost. The in-agent option is a legitimate alternative, not a straw-man — if the project later prefers per-agent self-discipline, that path stays open.

**Risks accepted.** The hook trusts each reviewer to emit faithfully (no agent-side tampering). The seven-agent inventory is enumerated above; a future reviewer with a different output shape would need to be registered with the hook explicitly. The verified failure mode (codebase-C-0018: APPROVED + severity:BLOCKER can structurally co-occur in `execute-task-quality-handler`'s contract today) is what justifies the cost of building the hook at all.

### D-0002 — FR-1's reviewer scope: include execute-task-quality-handler and finalize-deliverable-packager?

**The question.** Beyond the obvious core reviewers, does FR-1's parity guard cover `execute-task-quality-handler` (which emits APPROVED|NEEDS_REVISION|STUB_DETECTED|BLOCKER alongside a findings array) and `finalize-deliverable-packager` (which emits PASS|BLOCK|REVIEW with chained reviewer_findings)?

**Recommended.** Include `execute-task-quality-handler`. Exclude `finalize-deliverable-packager`. The execute-task agent is a verified strong candidate — the contradiction FR-1 targets is structurally possible in its contract today (codebase-C-0018). The packager is excluded because its findings are chained from a `shared-document-reviewer` invocation that already passes FR-1; re-checking would be redundant. (Verified: codebase-C-0016, codebase-C-0017, codebase-C-0018, codebase-C-0019, codebase-C-0020.)

**Why not include both.** "Defense-in-depth" against a hypothetical future refactor breaking the chained pass-through is the steel-man for including both — but FR-1 at the packager is cheap to add later if/when that refactor lands, and costly to maintain unnecessarily today. The chained-pass-through assumption is load-bearing and a known refactor-watch item; design-claude-code should flag it as such in the design output rather than spend redundant validation budget now.

**Why not exclude both.** That punts the genuine, verified gap in `execute-task-quality-handler`. The verification evidence (codebase-C-0018) is direct: the agent's contract syntactically allows APPROVED status alongside a severity:BLOCKER finding, and the agent file contains no verdict-vs-findings parity check today. Excluding it on the basis that the "obvious core" already covers the case would be wrong.

### D-0003 — FR-2's dispatch self-check location and the single-agent-fallback configuration surface

**The question.** Where does the orchestrator's dispatch self-check live (orchestrator-internal logic, a Claude Code hook, or a separate gate script), and how is "single-agent fallback configuration" identified — today it's implicit in `checkpoint.execution_mode='parent-driven-workaround'` rather than a named config surface.

**Recommended.** Hoist the `scope_class` read from line 350 of `recipe-feature-pipeline/SKILL.md` up to orchestrator entry. Run the self-check as orchestrator-internal logic on dispatch. Document `checkpoint.execution_mode='parent-driven-workaround'` as the named fallback-config surface — the value already exists; naming it canonicalizes it without changing behavior. Single read site, no duplication, no new file surface, and the check runs in the orchestrator that owns dispatch already. (Verified: codebase-C-0028, codebase-C-0029.)

**Citation precision.** codebase-C-0028 verifies the line number (350) and the single-read-site uniqueness — `scope_class` is read exactly once across the recipe. The claim text says "Stage 12 (Deliverable Packaging)" but the SKILL.md header at line 346 labels it "Stage 13 (Deliverable Packaging)". design-claude-code should cite the line number, not the stage number; the stage-label drift is cosmetic but real.

**Why not duplicate the read with a hook-based self-check.** Two read sites for one value invites divergence over time. The hook adds a separate failure path (hook misconfigured, hook silently skipped) that orchestrator-internal logic doesn't have. Defensive in a way that costs more than it saves at MINOR scope.

**Why not promote fallback to a new first-class config field via a gate script.** Heaviest option — new file surface, new config field, new invocation path. Useful only if the fallback-configuration surface is expected to grow (multiple fallback modes, complex predicates). Today it has one value. Premature factoring.

**Risks accepted.** Hoisting the `scope_class` read changes when the read happens; design-claude-code should run an impact audit (gitnexus_impact-style) on any downstream code that may implicitly have assumed late reading. Naming `parent-driven-workaround` as a first-class config canonicalizes a historical workaround; if that workaround was intended to remain temporary, this decision entrenches it — design-claude-code owns whether to renaming the value as part of the same edit.

### D-0004 — FR-3's parity algorithm

**The question.** How does the FR-3 audit compare `.mcp.json` against ADR-0041's per-server install-mechanism table? Two axes: exact-string vs canonicalized match shape, and string-equal vs resolve-and-compare for `${VAR}` env-var indirection.

**Recommended.** Canonicalize whitespace on both sides; leave `${VAR}` placeholders as opaque tokens that must match literally; compare with string equality after canonicalization. Simplest, reproducible across environments, doesn't depend on env state, stable test fixtures. Catches the parity drift FR-3 actually targets (rows present/absent, command verbs/flags) without coupling to the environment under test. (Verified: codebase-C-0038, codebase-C-0041.)

**Why not resolve-then-compare.** Expanding `${VAR}` against the running environment would couple the audit's correctness to where it runs — Codespaces, local, and Actions runner may have different variables set, producing different verdicts for identical files. Test fixtures become brittle. The drift it would additionally catch (different variable names that happen to resolve to the same value) is accepted as out-of-scope per the framer's risk note; FR-3 is targeted at structural rows and argv shape, not semantic resolution equivalence.

**Why not exact-string match without normalization.** Fragile to incidental whitespace, trailing newlines, ordering differences in either source. Generates false positives that overwhelm signal. Not viable for a parity audit intended to surface meaningful drift.

**Risks accepted.** ADR-0041 is currently at v1.0.1. If its table format changes (column order, separator, marker convention), the canonicalizer needs maintenance — this is a known refactor-watch item.

### D-0005 — Handling the deprecated mcp-openapi-schema row in FR-3

**The question.** ADR-0041 still lists mcp-openapi-schema as one of seven invocation rows (verified at ADR-0041 line 71); `.mcp.json` removed it on 2026-05-24 (verified — six servers remain). A naive symmetric-difference audit flags this as a day-one BLOCKER false positive.

**Recommended.** Add an in-rule deprecation-marker convention to ADR-0041's invocation table: rows tagged `[DEPRECATED]` (or an equivalent marker — design-cicd / design-claude-code picks the exact token) are treated by the FR-3 audit as expected-absent from `.mcp.json`. The marker is self-documenting at the source; FR-3 reads it. (Verified: codebase-C-0038, codebase-C-0041, codebase-C-0105, codebase-C-0110, codebase-C-0112. Single-sourced generalization: codebase-C-0111.)

**Why this matches the project's posture.** CLAUDE.md line 9 explicitly acknowledges mcp-openapi-schema's removal and frames KB-mcp-platform's seven-server reference as "a stale-doc issue, not an active server" — the same posture the recommended marker formalizes. The decision matches the project's already-demonstrated stale-doc tolerance and stays inside the feature's carve-out (no ADR-text mutations beyond the marker convention itself, which is an annotation pattern, not a decision-text edit). The in-rule marker also has better locality-of-truth than the script-side allowlist alternative.

**Why not an audit-script allowlist of expected-absent servers.** Inferior locality-of-truth: the deprecation marker would live in the audit script, not next to the row it annotates. A future reader of ADR-0041 sees the row and has no signal that the audit treats it specially. Allowlists drift silently. Not obviously worse on engineering merit (allowlists are a well-known pattern); rejected on locality grounds, which the project's stale-doc posture explicitly favors.

**Why not amend ADR-0041.** Excluded by the feature's carve-out (no ADR edits). Excluded as out-of-scope, not as rejected on merit. Also fights the project's append-only ADR posture (ADR-0005). Listed here for transparency.

**Calibration note on the supporting evidence.** codebase-C-0111 — the claim that the project has an "established pattern" of tolerating stale design-time docs — is downgraded to single_sourced in the critique. The pattern is established from N=1 observation (mcp-openapi-schema itself). The immediate decision still holds because the immediate case IS that observation, but design-claude-code should not over-generalize the posture without further evidence.

### D-0006 — FR-4's GitNexus dry-run exit-code contract and on-failure diagnostic

**The question.** What is the exit-code contract for the GitNexus install dry-run that asserts `GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1` is honored at the pinned v1.6.5 tag, and what does the on-failure diagnostic say?

**Recommended.** Exit 0 iff both signals hold for dart AND proto:
- Signal 1: a regex on stderr matches `GITNEXUS_SKIP_OPTIONAL_GRAMMARS.*[Ss]kip` (regex form rather than the full literal sentence, to respect drift-mode DM-1's literal-string fragility risk).
- Signal 3: the build artifacts under `node_modules/.../build/Release/` are absent.

Exit 1 otherwise. The diagnostic message names which signal failed (signal-1 stderr mismatch vs signal-3 artifact present), quotes the observed stderr fragment if signal 1 fails, names the pinned tag (v1.6.5), and gives a one-line remedial action (re-pin or open fix upstream). The dry-run asserts **nothing** about Swift via this env-var: at v1.6.5 the env-var governs only dart and proto, despite the upstream README's claim that it also covers Swift. Swift's non-build is governed by npm's optionalDependencies tolerance — a separate mechanism. (Verified: t001-C-0001, t001-C-0002, t001-C-0003, t001-C-0022, t001-C-0033, t001-C-0038.)

**Why the conjunction (signal 1 AND signal 3).** Signal 1 alone detects intent (the env-var was read and honored), but the warning text could be emitted while a future loosening of the strict `=== '1'` comparison silently lets the build proceed. Signal 3 alone detects outcome (no compiled grammar landed), but artifacts could be absent for unrelated reasons (e.g., grammar already cleaned by hand, env-var ignored entirely). The conjunction catches the "wrong-reason skip" case that singletons miss.

**Why the regex over the literal sentence.** t001-C-0040 (DM-1 drift mode) explicitly warns that literal-string assertions on stderr are brittle to upstream restyling of the warning. The regex `GITNEXUS_SKIP_OPTIONAL_GRAMMARS.*[Ss]kip` is targeted at the load-bearing tokens (env-var name plus the word "skip") and is robust to minor wording shifts.

**Why excluding Swift is non-negotiable.** Asserting on Swift via this env-var would be wrong per t001-C-0038 — the README/code divergence at v1.6.5 means the env-var does not govern Swift. The temptation to assert it (because the README says so) is exactly the failure mode the dry-run is meant to catch: trusting documentation over verified code-level behavior.

**Risks accepted.** Drift-mode DM-4: if upstream loosens the `=== '1'` comparison to truthy, signal-1 wording may still match while behavior subtly changes. Signal 3 absence is the load-bearing outcome check that catches this. Non-deterministic stderr ordering under load could foil simple regex matching — design-codespaces should ensure the regex is applied to the full stderr capture, not line-by-line in real time.

### D-0007 — FR-5's path triggers, execution environment, and MCP health-check invocation

**The question.** What file paths trigger the new CI workflow, what environment does the workflow run in (clean ubuntu-latest vs devcontainer image), and how does it check MCP server health — given that the canonical Claude Code docs are silent on the exit-code contract of `claude mcp list`?

**Recommended.**
- **Path triggers:** `.devcontainer/**`, `.mcp.json`, `adrs/ADR-0041*` (narrowly scoped to the file pattern, not all ADRs), `.claude/skills/auditing-mcp/**`.
- **Execution environment:** the project's devcontainer image (the same image developers run locally).
- **MCP health check:** `claude --bare -p "<noop>" --output-format stream-json | jq -c "select(.type==\"system\" and .subtype==\"init\") | .mcp_servers[] | select(.status != \"connected\")"` — the SDK-event path documented at code.claude.com. Non-empty jq output means at least one non-connected server; the job exits non-zero.

(Verified: t002-C-0001, t002-C-0002, t002-C-0008.)

**Why the devcontainer image rather than clean ubuntu-latest.** Closer to typical GitHub Actions practice would favor ubuntu-latest for faster cold-start, but it doesn't test what developers actually run. The whole point of the smoke is to catch devcontainer + MCP setup drift; running outside the devcontainer parallels the problem instead of testing it. The NFR-3 / NFR-4 latency cost of the devcontainer image build is a real tradeoff, but the smoke's value depends on environment fidelity. Codespaces designer owns the cost budget.

**Why not `claude mcp list` exit code.** Excluded — not on merit, but as actively unsafe. Verified t002-C-0008: a workflow depending on `claude mcp list`'s exit code is depending on undocumented behavior. The canonical docs document exit-code contracts for every sibling command (`claude auth status` returns 0/1; `claude daemon status` returns 1 if not running; `claude ultrareview` returns 0/1 with --json) but are silent on `claude mcp list` (t002-C-0001, t002-C-0002). The path shift to `claude --bare -p ... | jq` goes through the documented `system/init` event and the documented `McpServerStatus` enum, which is the only stable contract available today.

**Why narrow path triggers.** Over-inclusion (e.g., `adrs/**` broadly) would fire the workflow on unrelated ADR edits and erode signal. The narrow set covers exactly the files whose changes can plausibly break MCP server connectivity.

**Risks accepted.** The SDK-event path depends on stable `McpServerStatus` enum values across Claude Code versions; version pin discipline (the documented v2.1.64/.111/.121/.144 family) helps but isn't bulletproof. Running the workflow inside the devcontainer image adds image-build time on every trigger; design-codespaces budgets this against the NFR-4 five-minute ceiling.

### D-0008 — PR shape: single bundled vs sequenced

**The question.** Do the seven FRs ship as one bundled PR or as five sequenced PRs (one per FR group)?

**Recommended.** Single bundled PR. The seven FRs are tightly coupled at the implementation surface: FR-1 and FR-2 both touch the orchestrator; FR-3 and FR-5 both consume ADR-0041 and the `.mcp.json` table; FR-4 and FR-5 both touch the devcontainer smoke surface. Splitting introduces artificial dependency edges between PRs that would have to merge in a sequence anyway. For a MINOR-scope feature with a small reviewer pool, one PR is the lower-overhead path.

**No verified-claim driver.** This is a process/governance call. The recommendation rests on coupling analysis from the framer, not on evidence in the claim corpus. **Flagged for user confirmation** before commit — the user has previously expressed preferences on PR shape in adjacent contexts, but that preference is not in this corpus and should not be assumed.

**Why not five sequenced PRs.** Finer rollback granularity is real, but the FRs sequence rather than parallelize (each depends on the orchestration surface the previous one establishes). The reviewer pays the cost of five context switches for a benefit (per-FR rollback) that is rarely exercised. Legitimate process choice if review capacity is the binding constraint, which it isn't here.

**Why not the two-PR middle ground.** Splitting along review-gates vs infrastructure isn't load-bearing: FR-7 is a deferral-register marker (closer to housekeeping than to review-gating), so the conceptual boundary doesn't match any file-overlap pattern. Worse, FR-5 consumes ADR-0041 just like FR-3 — splitting them across two PRs forces ADR-0041's audit surface to be touched twice.

### D-0009 — Deferral-register update placement

**The question.** Does FR-7's deferral-register update (marking H-4 and B-1 adopted) land in the deliverable archive commit, as a separate housekeeping commit within the same PR, or in a follow-up PR?

**Recommended.** Include in the deliverable archive commit. The marker tightening IS part of the feature's quality-gates deliverable — FR-7 is one of the seven FRs the feature commits to. Separating it loses the audit trail; a future reader looking at the archive sees the feature's full scope in one commit.

**No verified-claim driver.** Pure process judgment. The blame-hygiene argument for separation is weak here because the register file is small and FR-7's scope is narrow (marker convention only).

**Why not a separate housekeeping commit.** Cleaner git blame on the register file, but fragments the feature's archival record across two commits in the same PR — the reviewer has to mentally reconstruct what the feature actually delivered. Legitimate if the register file were large and the marker change were one of many edits, which it isn't.

**Why not defer to a follow-up PR.** Risks the register update never landing — deferral-register debt is exactly the problem FR-7 exists to solve. Adding a deferral about the deferral register would be self-defeating.

### D-0010 — Concrete latency thresholds for NFR-1, NFR-2, NFR-3

**The question.** The PRD states latency targets qualitatively ("well under a small number of seconds"). U-8 asks for concrete numbers.

**Recommended.** Defer to the named designers, with explicit measurement methodology. design-claude-code owns NFR-1 (reviewer-validator overhead) and NFR-2 (MCP-audit parity-rule cost). design-codespaces owns NFR-3 (GitNexus dry-run cost). Each designer specifies: sample size, percentile (p50/p95/p99), environment (local Codespaces vs Actions runner), measurement window, and the rationale that justifies the chosen number against the verified workload.

**No verified-claim driver.** Setting a latency number without measuring is an anti-pattern — the number either over-constrains (causing false alarms) or under-constrains (NFR is meaningless). The named designers own these surfaces and have the empirical access to set them. Synthesis must not invent the numbers.

**Why not round-number placeholders.** Placeholders that don't reflect measurement become load-bearing through inertia — the next reader treats them as "the" threshold. Defer is the better default.

**Risks accepted.** Different environments (local Codespaces vs Actions runner) will hit different latency floors; thresholds must specify the environment they apply to.

## 4. Notable structural findings

These are the on-disk facts that the per-layer designers should treat as the verified ground truth for their respective decisions. All are independently verified in synthesis/03-critique.json.

- **`scope_class` is read exactly once, at line 350 of `.claude/skills/recipe-feature-pipeline/SKILL.md`.** A grep across the entire recipe returns only that line. The SKILL.md header at line 346 labels the containing step "Stage 13 (Deliverable Packaging)", though the PRD and some claim text say "Stage 12" — the line number is the authoritative citation; the stage number is a cosmetic drift. FR-2's recommendation is to hoist this read to orchestrator entry. (Verified: codebase-C-0028, codebase-C-0029.)

- **ADR-0041 carries seven invocation rows; `.mcp.json` carries six servers.** The seventh row in ADR-0041 (at line 71) reads: `mcp-openapi-schema | npx -y (Node ephemeral via npm cache) | npx -y "mcp-openapi-schema@${MCP_OPENAPI_SCHEMA_VERSION}" <spec-path>`. The live `.mcp.json` keys are exactly `actionlint-mcp`, `context7`, `exa`, `gitnexus`, `serena`, `terraform-mcp` — six servers; `mcp-openapi-schema` is absent. This divergence is FR-3's day-one BLOCKER false-positive trigger; D-0005 prescribes an in-rule deprecation marker as the resolution. (Verified: codebase-C-0038, codebase-C-0041, codebase-C-0105.)

- **CLAUDE.md line 9 frames this divergence as a stale-doc issue, not an active server.** Verbatim: "mcp-openapi-schema was removed 2026-05-24 (see .devcontainer/postCreate.sh#L16). The KB-mcp-platform skill still references it as one of seven — that's a stale-doc issue, not an active server." The project's existing posture toward stale design-time references is what makes the in-rule deprecation marker (D-0005's recommendation) coherent. (Verified: codebase-C-0110.)

- **The FR-4 sentinel inconsistency in postCreate.sh.** Line 5 of `.devcontainer/postCreate.sh` says "Installs the 5 OSS-local MCP servers" in the header comment; line 9 immediately corrects to "Servers installed here (4 — post-2026-05-24 postmortem; was 5)"; line 158 says "installing 4 OSS-local MCP servers". The "5" lingers in the high-level intro comment alongside the corrected "4". This is cosmetic-only and not load-bearing for any design decision, but design-codespaces should be aware of it when extending the post-create flow with the FR-4 dry-run. Note that the original claim cited line numbers 11 and 165; the actual lines are 5 and 158 — the cited numbers are ~6 lines stale, but the substance holds. (Verified: codebase-C-0103.)

- **The FR-5 path shift from `claude mcp list` to `claude --bare -p`.** The canonical Claude Code CLI docs are silent on the exit-code contract of `claude mcp list` (Finding 1 of the t-002 research note) and silent on its stdout format (Finding 2). Sibling commands document their exit codes: `claude auth status` (0/1), `claude daemon status` (1 if not running), `claude ultrareview` (0/1 with --json). The absence-by-contrast is structurally meaningful — a workflow depending on `claude mcp list`'s exit code is depending on undocumented behavior. The recommended substitute path (`claude --bare -p "<noop>" --output-format stream-json | jq ...`) goes through the documented `system/init` event and `McpServerStatus` enum. This is the only `supersedes` edge family in the entity graph. (Verified: t002-C-0001, t002-C-0002, t002-C-0008.)

- **The FR-1 reviewer-scope expansion: execute-task-quality-handler and finalize-deliverable-packager.** Both agents emit verdict + findings pairs and so are candidates for FR-1 coverage. `execute-task-quality-handler` (line 33 of its agent file) emits status `APPROVED | NEEDS_REVISION | STUB_DETECTED | BLOCKER` alongside a findings array with `domain`, `severity`, `source_activity`, `file_path`, `message` (the original claim mentioned `locator`; actual fields are `dispatch_hint` + `depth_level` — minor extraction inaccuracy). Crucially, nothing in the agent's contract today prevents APPROVED + severity:BLOCKER co-occurrence — the exact failure mode FR-1 targets is structurally possible. `finalize-deliverable-packager` (line 81 of its agent file) emits `PASS | BLOCK | REVIEW` with chained `reviewer_findings` from a `doc_type:DeliverableArchive` invocation of `shared-document-reviewer`; the upstream invocation already passes FR-1, making a second pass at the packager redundant. D-0002's recommendation reflects this asymmetry. (Verified: codebase-C-0016, codebase-C-0017, codebase-C-0018, codebase-C-0019, codebase-C-0020.)

- **The mcp-openapi-schema ADR-vs-`.mcp.json` divergence is the load-bearing example for the project's stale-doc posture.** It is conflicts_with three other entities in the graph: the live `.mcp.json` (6 servers), ADR-0041 (still names it), KB-mcp-platform (still references it as one of seven), and is the subject of CLAUDE.md's "stale-doc, not active server" framing. The conflicts_with chain across three claim-supported edges is what makes the in-rule deprecation marker (D-0005) the consistent design choice rather than a stylistic preference. (Verified: codebase-C-0038, codebase-C-0041, codebase-C-0105, codebase-C-0110.)

## 5. Limitations

Synthesis-level questions the framing could not resolve and that the per-layer designers should treat as either out-of-scope here, deferred to user confirmation, or empirically unverifiable from inside this run.

- **D-0008 (PR shape) rests on coupling analysis, not evidence.** No verified claim in the corpus addresses PR-shape choice. The bundled-PR recommendation is a process judgment about file-overlap coupling. The synthesizer flags this for user confirmation before commit. If the user prefers sequenced PRs for review-ergonomic reasons not captured in the corpus, the sequenced option is legitimate.

- **D-0009 (deferral-register placement) rests on audit-trail judgment.** No verified claim. The recommendation (include in deliverable archive) is process-grade.

- **D-0010 (concrete latency thresholds) cannot be set without measurement.** Synthesis must not invent numbers; the named designers own measurement.

- **Three open binary-check questions about Claude Code CLI flags would require running a local binary to resolve.** The t-002 research note establishes documentation silence on `claude mcp list`'s exit-code and stdout shape. The decisive disposition of the question — whether `claude mcp list` happens to return non-zero on disconnect — would require running the binary against a fixture `.mcp.json`. The synthesis treats this as unverifiable from inside an in-context corpus and uses the documented `claude --bare -p` SDK-event path instead. If a future feature wants to use `claude mcp list` directly, it should first commission a documentation-or-binary contract resolution; the current research note is explicit that the resolution is not inside the canonical docs as of the read date.

- **The single-sourced generalization at codebase-C-0111.** The claim that the project has an "established pattern" of tolerating stale design-time docs is downgraded to single_sourced in the critique. The pattern is established from N=1 (mcp-openapi-schema). The immediate D-0005 decision still holds because the immediate case IS the observation, but design-claude-code / design-cicd should not over-generalize the posture into other contexts without further evidence.

- **180 passthrough-unverified structural claims.** Per the orchestrator's pragmatic-scoping directive for a MINOR feature, 180 structural / file-path / line-number observations were not individually verified. They appear in the synthesis only as background context where the relevant entity already carries a verified claim. The per-layer designers should treat any reliance on a passthrough claim as a "verify before use" obligation. Notable examples that surface in the decision substrate above but are not individually verified: the seven-agent inventory enumerated in D-0001 (the names are from codebase entity E-0013..E-0023; the specific count and roster were not individually CoVe-checked); the line numbers for finalize-deliverable-packager's verdict shape (line 81 is verified; the surrounding context lines 50, 87, 122-125 cited in the chained-findings substantiation are not); the version-pin family documented for Claude Code (v2.1.64/.111/.121/.144) is from the t-002 note and not individually verified beyond the note's internal consistency.

- **No dissent findings.** The critique reports zero dissent_evidence pairs. Where there could have been dissent — the README-vs-code divergence on GitNexus Swift behavior (t001-C-0022/t001-C-0038) — the dissent is internal to the upstream project, not between this synthesis's sources, and is handled in the FR-4 design (the dry-run trusts the code, not the README).

- **No constraint violations.** Zero recommendations violate the PRD's hard constraints. The closest call is D-0005's in-rule deprecation marker (annotation pattern, not a decision-text rewrite — stays inside the no-ADR-edits carve-out by interpretation). design-cicd / design-claude-code should choose the marker token in a way that makes this interpretation defensible at review time.

## 6. Pointers to per-layer designer handoff

Each of the ten framed decisions is owned by exactly one per-layer designer (or by the cross-cutting design-composer). The orchestrator's handoff manifest should reflect this mapping verbatim.

**design-claude-code owns:**
- **D-0001** — FR-1's blocking-severity set + execution site (out-of-agent hook on emitted JSON; blocking set = `{BLOCKER}` only).
- **D-0002** — FR-1's reviewer-scope inclusion (include `execute-task-quality-handler`; exclude `finalize-deliverable-packager`).
- **D-0003** — FR-2's dispatch self-check location + single-agent-fallback config surface (hoist `scope_class` read to orchestrator entry; surface `checkpoint.execution_mode='parent-driven-workaround'` as the named fallback config).
- **D-0005** — FR-3's deprecated-row handling (in-rule deprecation-marker convention in ADR-0041; D-0005 has joint surface with design-cicd because the audit script that consumes the marker is shared, but the marker convention itself is a Claude Code artifact).

**design-codespaces owns:**
- **D-0006** — FR-4's GitNexus dry-run exit-code contract and on-failure diagnostic (signal-1 AND signal-3 conjunction; regex form; Swift excluded; NFR-3 threshold).

**design-cicd owns:**
- **D-0007** — FR-5's path triggers, execution environment, MCP health-check invocation (narrow path triggers, devcontainer image, `claude --bare -p ... | jq` SDK-event path).

**Cross-cutting / design-composer owns:**
- **D-0004** — FR-3's parity algorithm (canonicalize-then-string-equal). Cross-cutting because the algorithm lives in the `auditing-mcp` skill (Claude Code surface) but is consumed by FR-5's CI workflow (CI/CD surface). design-cicd and design-claude-code should jointly review the algorithm choice; design-composer is the integration owner.
- **D-0008** — PR shape (single bundled PR — flagged for user confirmation).
- **D-0009** — Deferral-register placement (include in deliverable archive commit).
- **D-0010** — Concrete latency thresholds for NFR-1/NFR-2 (design-claude-code measures) and NFR-3 (design-codespaces measures); design-composer reconciles the resulting numbers across the deliverable.

**Cross-cutting requirement that runs through every layer:** **FR-6 (actionable diagnostics)** is not a decision frame because it has no open question — every blocking diagnostic produced by FR-1..FR-5 must name the mechanism, the offending artifact path, the rule or contract violated, and a one-line remedial action. Every per-layer designer is responsible for honoring FR-6 in the diagnostic strings their layer's mechanism emits. The cross-cutting language should be consistent enough that design-composer can audit it as a single check at integration time.

---

### Appendix — citation register

Every verified critique ID cited above resolves to an entry in `synthesis/03-critique.json` with a `verdict` of `verified` or (for codebase-C-0111 only) `single_sourced`. The full mapping:

| Critique ID | Verdict | Used in |
|---|---|---|
| codebase-C-0016 | verified | D-0001, D-0002, §4 |
| codebase-C-0017 | verified | D-0001, D-0002, §4 (with calibration note: `locator` field claim is inaccurate) |
| codebase-C-0018 | verified | D-0001, D-0002, §4 (load-bearing — the verified contradiction-possibility in `execute-task-quality-handler`) |
| codebase-C-0019 | verified | D-0001, D-0002, §4 |
| codebase-C-0020 | verified | D-0001, D-0002, §4 |
| codebase-C-0028 | verified | D-0003, §4 (line 350 single-read-site; stage-label drift flagged) |
| codebase-C-0029 | verified | D-0003 |
| codebase-C-0038 | verified | D-0004, D-0005, §4 (.mcp.json has six servers) |
| codebase-C-0041 | verified | D-0004, D-0005, §4 (ADR-0041 line 71 still names mcp-openapi-schema) |
| codebase-C-0103 | verified (medium conf.) | §4 (FR-4 sentinel "5 vs 4" inconsistency; cited line numbers slightly stale) |
| codebase-C-0105 | verified | D-0005, §4 (day-one BLOCKER false-positive established) |
| codebase-C-0110 | verified | D-0005, §4 (CLAUDE.md line 9 stale-doc framing) |
| codebase-C-0111 | single_sourced | D-0005 (calibration: generalization from N=1; framer should not over-generalize) |
| codebase-C-0112 | verified | D-0005 (normative inference resting on C-0110/C-0111) |
| t001-C-0001 | verified | D-0006 (GITNEXUS_TAG=1.6.5 pin) |
| t001-C-0002 | verified | D-0006 (env-var contract scripts) |
| t001-C-0003 | verified | D-0006 (strict `=== '1'` comparison) |
| t001-C-0022 | verified | D-0006 (README/code Swift divergence) |
| t001-C-0033 | verified | D-0006 (signal-1 recommendation + DM-1 fragility) |
| t001-C-0038 | verified | D-0006 (no Swift assertions via env-var) |
| t002-C-0001 | verified | D-0007, §4 (docs silent on `claude mcp list` exit code) |
| t002-C-0002 | verified | D-0007, §4 (docs silent on `claude mcp list` stdout format) |
| t002-C-0008 | verified | D-0007, §4 (undocumented-behavior risk; FR-5 path shift) |

Passthrough-unverified claims (180 IDs in `synthesis/03-critique.json` under `passthrough_unverified.claim_ids_skipped`) are not cited as load-bearing premises anywhere in this synthesis. Where the synthesis text describes a structural fact that traces to a passthrough claim (e.g., the seven-agent inventory enumerated in D-0001), the text describes the fact as background context rather than as a load-bearing premise.
