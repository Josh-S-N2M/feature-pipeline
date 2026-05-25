---
id: Plan-devcontainer-mcp-provisioning-r1
version: 1.0.2
status: draft
doc_type: Plan
feature_slug: devcontainer-mcp-provisioning-r1
derived_from:
  - working/feature/devcontainer-mcp-provisioning-r1/prd-v3.md
  - working/feature/devcontainer-mcp-provisioning-r1/blueprint-v3.md
  - working/feature/devcontainer-mcp-provisioning-r1/codebase-analysis.json
adrs_referenced:
  - ADR-0005
  - ADR-0007
  - ADR-0018
  - ADR-0020
  - ADR-0022
  - ADR-0030
  - ADR-0031
  - ADR-0033
  - ADR-0036
  - ADR-0037
  - ADR-0038
  - ADR-0039
  - ADR-0040
  - ADR-0041
  - ADR-0042
  - ADR-0043
phases: 6
total_tasks: 39
generated: 2026-05-23T00:00:00Z
generated_by: plan-author
---

# Plan: Devcontainer MCP Server Provisioning

## Contents

Section completion checklist — each box must be checked (including `N/A — out of scope` rows) before this document leaves draft. The reviewer's Gate 0 check uses this list as the structural-presence anchor.

- [x] Purpose
- [x] Source
- [x] Phase 0 — Setup (Pre-install Verification + Environment Readiness)
- [x] Phase 1 — Foundation: ADR/Schema Authoring + Versioning Substrate
- [x] Phase 2 — Trifecta Skill Authoring (KB-mcp-platform + KB-mcp-design) + `.mcp.json`
- [x] Phase 3 — Devcontainer Lifecycle Scripts (postCreate, postStart, helper libs)
- [x] Phase 4 — Agent Allowlist Edits + auditing-mcp Augmentation + Family Graduation
- [x] Phase 5 — Rollout: Gate-6 Hard-Gate Wiring + End-to-End Verification + Cleanup
- [x] Cross-Phase Dependencies
- [x] Cross-Cutting Tasks (Security, Observability, Instrumentation)
- [x] L1/L2/L3 Verification Discipline
- [x] Acceptance Test Cross-Reference
- [x] Risks and Mitigation
- [x] Deferrals / Follow-ups
- [x] Estimation Methodology
- [x] Resourcing Posture
- [x] Open Items (Pending Cross-Artifact Audit)
- [x] Update History

## Purpose

This Plan decomposes the approved Blueprint v3 (`blueprint-v3.md`) into an executable, phase-and-task sequenced delivery for `devcontainer-mcp-provisioning-r1`. The Plan inherits all EARS-format Acceptance Criteria from Blueprint v3 (AC-FR-*, AC-CC-*, AC-CS-*, AC-NFR-*, AC-X-*); the Plan does not author new ACs. It enumerates the concrete files to create or modify, the order of operations, the L1/L2/L3 verification per task, the phase exit criteria that feed Phase Validators (authored downstream by `test-phase-validator`), and the AC-to-task mapping that `review-cross-artifact-auditor` will verify.

The Plan honors:

- **Blueprint v3 Implementation Plan §Required Implementation Order** (12 numbered items) as the spine of Phases 1–5
- **Gate-4 user closures**: OI-1 (7 servers no fallback), OI-2 (ADR-0042 graduation), OI-3 (ADR-0043 hard gate)
- **Deferral Register §H** (7 verify-at-execution items wired into Phase 0)
- **Deferral Register §D** (6 design-stage deferred items resolved at task time)
- **Deferral Register §O** (event-trigger discipline — the Plan does NOT invent calendar machinery for "post-ship" annotations)

The Plan is reviewed by `shared-document-reviewer` (Gate 0/1) and then by `review-cross-artifact-auditor` after acceptance-tests and phase-validators are authored.

## Source

- **Blueprint**: `working/feature/devcontainer-mcp-provisioning-r1/blueprint-v3.md` (v3.0.0, status: draft → approved at Gate 4)
- **PRD**: `working/feature/devcontainer-mcp-provisioning-r1/prd-v3.md` (v3.0.0)
- **Codebase Analysis**: `working/feature/devcontainer-mcp-provisioning-r1/codebase-analysis.json` (schema v1.1.0 per ADR-0038)
- **ADRs (authored in this feature)**: `adrs/ADR-0037` through `adrs/ADR-0043` (7 total)
- **Deferral Register**: `Issues/register-devcontainer-mcp-provisioning-r1-deferrals.md`
- **Agent Roster Impact Matrix**: `working/feature/devcontainer-mcp-provisioning-r1/agent-roster-impact-matrix.md` (closes Q-3)
- **Phase taxonomy used**: Phase 0 (Setup / Pre-install Verification + Environment Readiness); Phases 1–4 (Feature Delivery, ordered by Blueprint cross-layer sequencing); Phase 5 (Rollout / Verification / Cleanup). All Phases inherit Blueprint v3 EARS ACs.

### Layer Scope (inherited from Blueprint v3)

Only two of the 9 engineering layers are activated by this feature:

- [x] **Claude Code / Project Filesystem** — `.mcp.json` (NEW), 8 `tools:` allowlist edits, 2 new trifecta skills, `auditing-mcp` augmentation + family graduation, `mcp-events.jsonl` schema, `.gitignore` update, orchestrator Gate-6 wiring
- [x] **Dev Environment (Codespaces / Devcontainer)** — `devcontainer.json` (Features + containerEnv), `postCreate.sh`, `postStart.sh`, `install/terraform-mcp.sh`, `lib/mcp-ping.sh`, `lib/mcp-auth-probe.sh`, `versions.env`
- [ ] **Frontend / Backend / API / Query / Database / CI/CD / IaC** — N/A — out of scope per PRD-v3 and Blueprint-v3 Layer Scope

### MINOR-V3-001 disposition (Gate-4 reviewer carry-over)

The Gate-4 reviewer flagged `blueprint-v3.md:327` (AC-FR-11-c) as lacking the inline hard-gate qualifier that AC-CC-5 (line 329) and AC-NFR-2-c (line 339) carry explicitly. The Plan **adopts option (a)** from the orchestrator brief: treat AC-FR-11-c as PRD-inherited and let downstream enrichments carry the gate semantics. Rationale:

- AC-FR-11-c is verbatim PRD text; PRD ACs are not enriched in-place by the Blueprint (per PRD-authoring discipline)
- The hard-gate semantics are carried by AC-CC-5 (CC-refined) and AC-NFR-2-c (PRD-inherited; enumerated per I-DR-BP-005), both of which the Blueprint explicitly enriches
- The four cross-reference sites (lines 764, 1170, 1294, 1337) treat the triplet AC-FR-11-c + AC-CC-5 + AC-NFR-2-c as unified — the unified treatment is correct, but the source of the hard-gate qualifier lives on AC-CC-5 / AC-NFR-2-c, not AC-FR-11-c
- A v3.0.1 patch is NOT recommended at this stage; the semantics are unambiguous across the triplet

Plan tasks satisfying AC-FR-11-c (T4.4, T4.5, T5.1, T5.4) reference the unified triplet AC-FR-11-c + AC-CC-5 + AC-NFR-2-c so the hard-gate enforcement is anchored in the task-level verification, not on AC-FR-11-c text alone. T5.4 is the live-verification site (seeded-BLOCKER simulation exercises the hard gate end-to-end).

---

## Phase 0 — Setup (Pre-install Verification + Environment Readiness)

### Goal

Resolve the 7 verify-at-execution items (§H of the deferral register) and the placeholder normalization items (§D) so that all downstream task work has stable inputs (commit SHAs, version pins, env-var smoke-tests, CLI capability checks). Phase 0 produces no user-visible behavior; it produces a verified-input baseline.

### Scope

- Resolve §H-1 through §H-7 (verify-at-execution): pick / re-confirm pin values; smoke-test load-bearing env vars; confirm CLI capability for `claude mcp ping`
- Resolve §D-2 (placeholder normalization to `<PIN_TBD>`); §D-4 (Go feature version pin selection)
- Bootstrap the `.claude/runtime/` directory (resolution of Q-CC-2)

### Out of scope (deferred to later phases)

- Any `.mcp.json` writes (Phase 2)
- Any `devcontainer.json` Features-block edits (Phase 1)
- Any postCreate / postStart authoring (Phase 3)

### Prerequisites

- Blueprint v3 approved at Gate 4 (already met)
- All 7 ADRs in `working/feature/devcontainer-mcp-provisioning-r1/adrs/` exist (already met)

### Tasks

#### T0.1: Re-confirm Terraform MCP version pin (§H-2)

- **Layer:** Codespaces
- **Description:** Check the HashiCorp releases.hashicorp.com page for the latest stable Terraform MCP release. v0.5.2 was selected at design time; release cadence is active (0.5.0 Apr 1, 0.5.1 Apr 7, 0.5.2 Apr 28 — per H-2). If a newer minor is available and reviewed-stable, select it; otherwise keep v0.5.2. Record the SHA256 and the URL of the release tarball + SHA256SUMS + GPG signature files.
- **Dependencies:** none
- **Estimate:** S
- **Satisfies AC:** N/A — setup (informs T1.4 / T3.3)
- **L1 verification:** A `verify-at-execution.md` log file under `working/feature/devcontainer-mcp-provisioning-r1/` records the selected version, the SHA256 hex string, and the GPG verification key fingerprint.
- **L2 verification:** Manual: `wget`-ing the artifact + `sha256sum -c` succeeds; `gpg --verify` succeeds against HashiCorp's public key.
- **L3 verification:** N/A — setup; verified end-to-end at T3.3 L3.

#### T0.2: Select actionlint-mcp commit SHA (§H-1)

- **Layer:** Codespaces
- **Description:** Browse `github.com/hongkongkiwi/actionlint-mcp` and pick a commit SHA from the default branch. Criteria: pick a commit at least 14 days old to allow upstream-recovery from any near-tip regression; record commit SHA + commit date + first-line subject in the verify-at-execution log. Default pin per reconciliation cycle 3: `ACTIONLINT_MCP_SHA=7441fe042c995cbb1bb4b97fce71f9ed3b36d5ef` (HEAD of main on the corrected upstream, verified 2026-05-23). Note: the corrected repo has `main.go` at the repo root — there is no `cmd/actionlint-mcp` subpath; `go install` targets the repo root path. (Prior pipeline drafts referenced `2manymws/actionlint-mcp`; that org has no such repo per HTTP 404 verification — see reconciliation-log-cycle-3.md F1.)
- **Dependencies:** none
- **Estimate:** S
- **Satisfies AC:** N/A — setup (informs T3.2)
- **L1 verification:** The verify-at-execution log records the 40-char SHA, commit date, subject line.
- **L2 verification:** `go install github.com/hongkongkiwi/actionlint-mcp@<SHA>` succeeds in a scratch Go environment (no `/cmd/actionlint-mcp` subpath — `main.go` is at the repo root in the corrected upstream).
- **L3 verification:** N/A — setup; verified at T3.2 L3.

#### T0.3: Re-confirm mcp-openapi-schema staleness disposition (§H-3)

- **Layer:** Codespaces
- **Description:** Check `npmjs.com/package/mcp-openapi-schema` for any release since 2025-03-13 (single release at design time, 14+ months old). If unchanged, pin to `0.0.1` and add a `STALE_PACKAGE: review by next feature` annotation to the verify-at-execution log. If a new release exists, evaluate whether to bump (default: prefer the older 0.0.1 unless a CVE forces).
- **Dependencies:** none
- **Estimate:** S
- **Satisfies AC:** N/A — setup (informs T2.4 `.mcp.json` entry)
- **L1 verification:** Verify-at-execution log records the selected version + staleness annotation.
- **L2 verification:** `npx -y mcp-openapi-schema@<version>` exits 0 on a `--help`-like invocation in scratch Node environment.
- **L3 verification:** N/A — setup; verified at T3.1 L3 (post-postCreate `claude mcp list`).

#### T0.4: **HIGH-forgetting-risk** smoke-test GitNexus `GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1` env var (§H-4)

- **Layer:** Codespaces
- **Description:** This is the single HIGH forgetting-risk item per Deferral Register §L. Per reconciliation cycle 3 (F2): **GitNexus is distributed via npm, not via uv/PyPI** — prior pipeline drafts incorrectly used `uvx --from gitnexus@<TAG>` (a category error; gitnexus has never been published to PyPI). Correct install form: `npm install -g gitnexus@${GITNEXUS_TAG}` for persistent install (postCreate); `npx -y gitnexus@${GITNEXUS_TAG} mcp` for one-shot smoke-test / runtime. Default pin: `GITNEXUS_TAG=1.6.5` (latest stable on the npm registry, published 2026-05-16; verified 2026-05-23). In a scratch container, run `GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1 npx -y gitnexus@${GITNEXUS_TAG} mcp --help` (or equivalent help/version invocation). If the command exits 0 without invoking a C++ toolchain (no `cc`, no `g++`, no `cargo`, no `node-gyp` build invocation in process tree), the env var still works — under the npm install path, `GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1` suppresses npm's vendored tree-sitter grammar build (the heavy C++ step), same wrapping intent as before. Record success and the tag in the verify-at-execution log. If the env var is no longer respected (process tree shows a C++ toolchain invocation OR command fails), STOP and re-plan. **AC-CS-9 wrapping intent preserved**: AC-CS-9 says "cold-cache build doesn't need a C++ toolchain" — this remains satisfied because `GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1` is respected by the npm install (suppresses the npm-vendored tree-sitter grammar compile, the only C++ step in the install pipeline). Only the install mechanism changes; the semantic intent is intact. **Base-image prereq side effect (note here, plumbing deferred to design-composer / D-3.2)**: Node-LTS becomes a base-image prereq for gitnexus (was implicit before through the Node Feature for other servers; now load-bearing for gitnexus itself). The codespaces-design and tasks.json T3.4 (in design-composer's scope) will reflect this. T1.4 / T3.4 here continue to source Node 20 LTS from the Node devcontainer Feature wired in T1.4 — no Plan-level restructuring needed.
- **Dependencies:** none
- **Estimate:** S–M (scratch container provisioning is the long pole)
- **Satisfies AC:** N/A — setup (informs T3.2; **load-bearing for AC-CS-9**)
- **L1 verification:** Verify-at-execution log records pinned tag + env var smoke-test result.
- **L2 verification:** The recorded smoke-test command output in the log shows exit 0 AND no C++ toolchain invocation in process tree.
- **L3 verification:** AC-CS-9 passes in a real postCreate run (verified in Phase 5).

#### T0.5: Re-validate Context7 v3.0.0 tool surface + auth header (§H-5)

- **Layer:** Claude Code
- **Description:** Confirm Context7 v3.0.0 tool surface — two tools `resolve-library-id` and `query-docs` (per T-005 v3.0.0 WebFetch-verified). Confirm canonical auth surface (per ADR-0039 + GitHub README verbatim: `CONTEXT7_API_KEY: <value>` header literal — the README states "pass your API key via the `CONTEXT7_API_KEY` header"; URL-query form REJECTED by OP-9; argv `--api-key` REJECTED by OP-10; the prior `Authorization: Bearer ${CONTEXT7_API_KEY}` framing was non-canonical and has been corrected to canonical per SF-F3-AUTH-HEADER-1 user disposition). Record findings in verify-at-execution log; if v3.0.0 has been superseded by the time of execution, update allowlist plan for T4.1.
- **Dependencies:** none
- **Estimate:** S
- **Satisfies AC:** N/A — setup (informs T4.1 allowlist edits + T2.4 `.mcp.json` env-block)
- **L1 verification:** Verify-at-execution log records the tool name + auth-surface form for the pinned version.
- **L2 verification:** Cross-check against Context7's `mcp.context7.com/mcp` `tools/list` JSON-RPC response (manual curl with auth header).
- **L3 verification:** AC-CC-2 passes (the `mcp__context7__*` allowlist entries match the live server's tool names) — verified Phase 5.

#### T0.6: Confirm `claude mcp ping` CLI presence in pinned Claude Code Feature version (§H-6)

- **Layer:** Codespaces
- **Description:** Inspect the Claude Code Feature (`ghcr.io/anthropics/devcontainer-features/claude-code:1`) — run `claude mcp ping --help` in a scratch container. If the subcommand exists and exits 0 with usage, mark "ping CLI available" in verify-at-execution log; T3.4 `lib/mcp-ping.sh` will use `claude mcp ping`. If the subcommand is absent or non-zero, mark "ping CLI absent" and T3.4 falls back to direct JSON-RPC ping per ADR-0041 Implementation Guidance.
- **Dependencies:** none
- **Estimate:** S
- **Satisfies AC:** N/A — setup (informs T3.4)
- **L1 verification:** Verify-at-execution log records "ping CLI available" or "ping CLI absent".
- **L2 verification:** The scratch-container session output is captured in the log.
- **L3 verification:** N/A — setup.

#### T0.7: Confirm Exa CLI `--header` flag support (§H-7)

- **Layer:** Codespaces
- **Description:** Check the Exa MCP client documentation at the pinned version. Confirm that `--header "x-api-key: ${EXA_API_KEY}"` is supported and that `--api-key` (URL-query form per C-0259/C-0260/C-0280) is the rejected pattern. Record findings in verify-at-execution log. If `--header` is unsupported, document the alternative auth surface (likely Claude Code MCP server config `env` block with `${EXA_API_KEY}` direct, or `headers` block in `.mcp.json` per ADR-0039).
- **Dependencies:** none
- **Estimate:** S
- **Satisfies AC:** N/A — setup (informs T2.4 `.mcp.json` `exa` entry)
- **L1 verification:** Verify-at-execution log records the supported auth flag form.
- **L2 verification:** N/A (no scratch test required; documentation check suffices).
- **L3 verification:** AC-CC-4 passes (no literal credential present) and AC-CS-6 passes (env-var indirection works) — verified Phase 5.

#### T0.8: Normalize placeholder convention to `<PIN_TBD>` (§D-2)

- **Layer:** Claude Code
- **Description:** Establish the canonical placeholder string `<PIN_TBD>` (per I-DR-003) for `.mcp.json` and `versions.env` pre-pin sketches in this Plan. No code is written here; this is a project-convention decision. Document the convention in `verify-at-execution.md` so T1.3 / T2.4 use it consistently.
- **Dependencies:** none
- **Estimate:** S
- **Satisfies AC:** N/A — setup
- **L1 verification:** Verify-at-execution log records the canonical placeholder string.
- **L2 verification:** N/A.
- **L3 verification:** No `<PIN_TAG>` or `<TBD-per-ADR-0007-v2.2.0>` strings appear in any file authored by this Plan — verified by grep at Phase 5.

#### T0.9: Select Go devcontainer Feature version pin (§D-4)

- **Layer:** Codespaces
- **Description:** Decide on a specific Go major to pin in `devcontainer.json`'s Features block. Default: pin `version: "1.22"` (current LTS-equivalent; same era as Node 20 LTS pin per ADR-0041). Record the selected version in verify-at-execution log so T1.4 uses it.
- **Dependencies:** none
- **Estimate:** S
- **Satisfies AC:** N/A — setup (informs T1.4)
- **L1 verification:** Verify-at-execution log records the selected Go major.
- **L2 verification:** `go version` in a scratch container with that Feature pin returns the expected major.
- **L3 verification:** AC-CS-1 passes — verified Phase 5.

#### T0.10: Bootstrap `.claude/runtime/` directory + `.gitkeep` + `.gitignore` update (Q-CC-2 resolution)

- **Layer:** Claude Code
- **Description:** Create the empty directory `.claude/runtime/` with a `.gitkeep` placeholder so the directory exists in git. Add `.claude/runtime/mcp-events.jsonl` to `.gitignore` (the runtime file is per-Codespace; never committed). This is independent housekeeping per Blueprint Implementation Plan step 10.
- **Dependencies:** none
- **Estimate:** S
- **Satisfies AC:** AC-CC-4 (zero literal credentials — `.jsonl` is gitignored so no risk of accidental commit); contributes to AC-CC-6.
- **L1 verification:** `git ls-files | grep -E '^\.claude/runtime/\.gitkeep$'` returns the file; `git check-ignore .claude/runtime/mcp-events.jsonl` returns the path (ignored).
- **L2 verification:** `git status` after `echo '{}' > .claude/runtime/mcp-events.jsonl` shows no changes (ignored).
- **L3 verification:** `git grep "fake-test-credential"` after seeding a fake credential into `.claude/runtime/mcp-events.jsonl` returns nothing (file is ignored AND never tracked).

### Phase 0 Exit Criteria

- `verify-at-execution.md` exists under `working/feature/devcontainer-mcp-provisioning-r1/` with one section per H-1..H-7 + D-2 + D-4 resolution + Q-CC-2 bootstrap
- All seven verify-at-execution items in §H closed (recorded in the log with a YES/NO disposition); the single HIGH forgetting-risk item (H-4 GitNexus env-var smoke-test) closed with evidence
- `.claude/runtime/.gitkeep` committed; `.gitignore` updated; runtime JSONL is ignored
- No file under `.mcp.json` / `versions.env` / `.devcontainer/` modified yet (Phase 0 is verification-only; the substrate is Phase 1+)

Phase Validator (downstream): grep the log for closed entries; assert each H-1..H-7 has a recorded disposition; assert `.gitkeep` is present and `.gitignore` contains the runtime path.

### Phase 0 Rollback Path

Phase 0 produces only a log and the `.gitkeep` + `.gitignore` entry. Rollback = `git revert` the bootstrap commit; delete the verify-at-execution log. Zero downstream impact.

---

## Phase 1 — Foundation: ADR Promotion + Schema Authoring + Versioning Substrate

### Goal

Stage the architectural substrate (ADR promotion + relocation per ADR-0036/0038; `versions.env` pin file; `devcontainer.json` Features-block additions) so that Phase 2 (skill authoring + `.mcp.json`) and Phase 3 (lifecycle scripts) have a stable foundation. No skills authored yet; no `.mcp.json` yet.

### Scope

- Promote ADR-0037 through ADR-0043 from feature working dir to canonical `adrs/` (per ADR-0036 single-location); mark ADR-0018 superseded.
- Relocate ADR-0007 from `adrs-migrated/` to `adrs/` per ADR-0038 / ADR-0036 (Implementation Plan step 11).
- Author `.devcontainer/versions.env` with 5 OSS-local server pins (Serena, mcp-openapi-schema, actionlint-mcp, terraform-mcp, gitnexus).
- Author the `devcontainer.json` Features-block + `containerEnv` additions (Node 20 LTS, Go pin, secret indirection).
- Update KB-codebase-research + discovery-codebase-researcher to cite `schema_version: 1.1.0` and ADR-0038 (Implementation Plan step 12).

### Out of scope (deferred)

- `.mcp.json` (Phase 2)
- Skills (Phase 2)
- Lifecycle scripts (Phase 3)
- Agent allowlist edits (Phase 4)

### Prerequisites

- Phase 0 complete (verify-at-execution log closed; substrate ready for Go/Node Feature pin authoring + Terraform / actionlint / mcp-openapi / gitnexus pin authoring).

### Tasks

#### T1.1: Promote 7 newly authored ADRs to canonical `adrs/` location

- **Layer:** Claude Code
- **Description:** Copy ADR-0037 through ADR-0043 from `working/feature/devcontainer-mcp-provisioning-r1/adrs/` to `/workspaces/feature-pipeline/adrs/`. Per ADR-0036 single-canonical-ADR-location, both copies cannot drift; the working-dir copy is the authoring trace, the root `adrs/` copy is the canonical reference. (At deliverable packaging, the working-dir copies may be archived or removed — that's Phase 5 cleanup.) Update each ADR's `status:` frontmatter from `proposed` to `accepted`.
- **Dependencies:** none
- **Estimate:** S
- **Satisfies AC:** AC-CC-10 (precondition — ADR-0042 must exist in canonical location for the family-graduation task in Phase 4 to cite it); contributes to AC-FR-11-c by establishing ADR-0043 (hard-gate policy).
- **L1 verification:** `ls /workspaces/feature-pipeline/adrs/ADR-{0037,0038,0039,0040,0041,0042,0043}-*.md` lists 7 files.
- **L2 verification:** Each promoted ADR's frontmatter `status:` is `accepted`; each carries the correct `supersedes:` field (ADR-0038 supersedes ADR-0018; others have none).
- **L3 verification:** All seven ADRs are referenced by file path from the Plan, Blueprint, and downstream artifacts without 404s — grep-verified at Phase 5.

#### T1.2: Mark ADR-0018 v1.0.0 superseded; relocate ADR-0007 to canonical `adrs/`

- **Layer:** Claude Code
- **Description:** Edit `adrs/ADR-0018-codebase-analysis-schema.md` (or wherever it lives) to add `Status: Superseded by ADR-0038` in the body (per ADR-0005 append-only — the file is preserved). Move (`git mv`) `adrs-migrated/ADR-0007-code-graph-mcp-selection.md` → `adrs/ADR-0007-code-graph-mcp-selection.md` per ADR-0036. Update any internal cross-references that point to the old path.
- **Dependencies:** T1.1 (ADR-0038 must exist in canonical adrs/ before it can supersede ADR-0018).
- **Estimate:** S
- **Satisfies AC:** Contributes to AC-X-2 (canonical inventory disposition); housekeeping for Blueprint Implementation Plan steps 11 + 12.
- **L1 verification:** `ls /workspaces/feature-pipeline/adrs/ADR-0007-*.md` returns a file; `grep "Superseded by ADR-0038" .../ADR-0018-*.md` matches.
- **L2 verification:** `git log --follow adrs/ADR-0007-*.md` shows the rename was tracked (not delete+add).
- **L3 verification:** No grep hit for `adrs-migrated/ADR-0007` anywhere in the repo (cross-references updated) — Phase 5.

#### T1.3: Author `.devcontainer/versions.env`

- **Layer:** Codespaces
- **Description:** Create `.devcontainer/versions.env` with five pinned entries — one per OSS-local server:
  ```
  SERENA_REF=git+https://github.com/oraios/serena@<PIN_PRE_V1.3.0>  # ADR-0040
  MCP_OPENAPI_SCHEMA_VERSION=0.0.1                                   # ADR-0041, T0.3
  ACTIONLINT_MCP_SHA=7441fe042c995cbb1bb4b97fce71f9ed3b36d5ef        # ADR-0041, T0.2 (hongkongkiwi/actionlint-mcp HEAD of main verified 2026-05-23 per reconciliation-log-cycle-3.md F1)
  TERRAFORM_MCP_VERSION=<version from T0.1>                          # ADR-0041
  GITNEXUS_TAG=1.6.5                                                 # ADR-0007, T0.4 (npm registry, published 2026-05-16; verified 2026-05-23 per reconciliation-log-cycle-3.md F2 — npm install, NOT uvx/PyPI)
  ```
  Use the canonical `<PIN_TBD>` placeholder only where the verify-at-execution log instructs (e.g., Serena pre-v1.3.0 tag is a moving target — confirmed at install time). Per ADR-0041 D-0011 supply-chain reproducibility.
- **Dependencies:** T0.1, T0.2, T0.3, T0.4 (pin values from verify-at-execution log).
- **Estimate:** S
- **Satisfies AC:** AC-FR-1-a (precondition — install scripts need pin values); AC-CS-2 (sentinel naming uses these versions); AC-CS-8 (warm-cache reuse depends on pin stability).
- **L1 verification:** `bash -n .devcontainer/versions.env` parses (it's `KEY=VALUE` form; should not error).
- **L2 verification:** Each KEY is present; each VALUE is non-empty; no `<PIN_TAG>` or `<TBD-per-ADR-0007>` strings (only `<PIN_TBD>` or actual pin values).
- **L3 verification:** Sourced by `postCreate.sh` (T3.1) without error; AC-CS-2 passes — Phase 5.

#### T1.4: Edit `.devcontainer/devcontainer.json` — Features + containerEnv

- **Layer:** Codespaces
- **Description:** Modify `.devcontainer/devcontainer.json` to:
  - Add to Features block: `"ghcr.io/devcontainers/features/node:1": {"version": "20"}` (Node 20 LTS pin per ADR-0041)
  - Add to Features block: `"ghcr.io/devcontainers/features/go:1": {"version": "1.22"}` (Go pin per T0.9)
  - Preserve: `common-utils:2`, `github-cli:1`, `claude-code:1` (unchanged per Blueprint scope)
  - Add to `containerEnv`: `CONTEXT7_API_KEY: "${localEnv:CONTEXT7_API_KEY}"`, `EXA_API_KEY: "${localEnv:EXA_API_KEY}"`, `TFE_TOKEN: "${localEnv:TFE_TOKEN}"` (TFE_TOKEN optional per Blueprint External Resources Used)
  - Add `forwardPorts: []` (preserve AC-CS-7; explicit empty)
  - Add `postCreateCommand: ".devcontainer/postCreate.sh"` and `postStartCommand: ".devcontainer/postStart.sh"` references (the scripts are authored in Phase 3; the references can land now as forward declarations because devcontainer doesn't validate paths until rebuild)
  - Do NOT modify any Dockerfile reference (preserves ADR-0041 / E-0081 "no new Dockerfile work")
- **Dependencies:** T0.9 (Go pin); T1.3 (versions.env should exist so the Features block has a stable file to reference, though it doesn't directly source it).
- **Estimate:** M
- **Satisfies AC:** AC-CS-1 (Node 20 + Go present after Feature install); AC-CS-7 (forwardPorts empty); AC-CS-6 (secret indirection via containerEnv); AC-FR-5-a (env-var name only, no secret values committed).
- **L1 verification:** `jq . .devcontainer/devcontainer.json` parses without error; all required Feature entries present (grep).
- **L2 verification:** `devcontainer build` (or equivalent local validation) succeeds against the modified `devcontainer.json` without yet requiring the scripts (Features-only validation).
- **L3 verification:** A fresh Codespace rebuild lands with `node --version` returning `v20.*` and `go version` returning non-error (AC-CS-1 passes) — Phase 5.

#### T1.5: Update KB-codebase-research/SKILL.md + discovery-codebase-researcher.md schema_version bump

- **Layer:** Claude Code
- **Description:** Per Blueprint Implementation Plan step 12 + ADR-0038. Edit `.claude/skills/KB-codebase-research/SKILL.md` and `.claude/agents/discovery-codebase-researcher.md` to:
  - Update any `schema_version: 1.0.0` reference to `schema_version: 1.1.0`
  - Update any `ADR-0018` citation to also cite ADR-0038 (supersession trail)
  - Preserve the four prose primary/fallback references in `discovery-codebase-researcher.md` (lines 3, 20, 29, 156) verbatim — OP-4 audit rule depends on them being present
- **Dependencies:** T1.1 (ADR-0038 promoted).
- **Estimate:** S
- **Satisfies AC:** Contributes to AC-CC-9 (cross-reference completeness — ADR-0007 v2.2.0 cited correctly); AC-CC-4 indirectly (no credentials touched here).
- **L1 verification:** `grep -nE "schema_version:\s*1\.1\.0" .claude/skills/KB-codebase-research/SKILL.md .claude/agents/discovery-codebase-researcher.md` returns matches; no `schema_version: 1.0.0` remains.
- **L2 verification:** Both files mention ADR-0038 in addition to ADR-0018 (supersession trail visible).
- **L3 verification:** OP-4 audit rule (run in Phase 5) confirms the four prose primary/fallback references are still present.

### Phase 1 Exit Criteria

- All 7 newly authored ADRs (ADR-0037–ADR-0043) exist in `/workspaces/feature-pipeline/adrs/` with `status: accepted`
- ADR-0018 carries the superseded-by-ADR-0038 marker; ADR-0007 lives in `adrs/` not `adrs-migrated/`
- `.devcontainer/versions.env` exists with 5 pinned entries (no `<PIN_TAG>` or `<TBD-per-...>` legacy strings)
- `.devcontainer/devcontainer.json` Features block carries Node 20 LTS + Go pin; containerEnv carries the 3 secret env-var indirections; `forwardPorts: []`
- KB-codebase-research + discovery-codebase-researcher cite `schema_version: 1.1.0` and ADR-0038

Phase Validator: structural assertions (file paths exist; frontmatter fields correct; grep patterns match/don't-match).

### Phase 1 Rollback Path

- `git revert` Phase 1 commits in reverse order
- ADR promotion is additive; reverting removes the canonical copy (working-dir copies preserved)
- `devcontainer.json` revert restores prior Features block
- `versions.env` revert deletes the file
- No live Codespace impact until Phase 3 ships postCreate.sh; Phase 1 alone does not change runtime behavior

---

## Phase 2 — Trifecta Skill Authoring (KB-mcp-platform + KB-mcp-design) + `.mcp.json`

### Goal

Author the W/H/A trifecta halves (`KB-mcp-platform/` and `KB-mcp-design/`) per Blueprint Implementation Plan step 3, then author `.mcp.json` per Blueprint Implementation Plan step 4. The trifecta skills are authored BEFORE `.mcp.json` because `KB-mcp-design/references/principles.md` is the canonical home for the `mcp-events.jsonl` schema (per ADR-0037), which `postStart.sh` (Phase 3) consumes; and because `KB-mcp-platform/assets/templates/mcp.json` provides the canonical template for `.mcp.json`.

### Scope

- Author `KB-mcp-platform/` (trifecta What-half) with `SKILL.md`, ~7 `references/*.md` files, and `assets/templates/`
- Author `KB-mcp-design/` (trifecta How-half) with `SKILL.md` and exactly two `references/*.md` files (`patterns-and-anti-patterns.md` + `principles.md`); no `assets/`
- Honor §D-3 (pedagogical_sections justifications name the specific OP-rule and anti-pattern per entry — KB-github-actions-platform is the precedent)
- Author `.mcp.json` (NEW at repo root) with seven `mcpServers` entries per Gate-4 OI-1 closure (no fallback entry); use `<PIN_TBD>` placeholders that postCreate.sh substitutes from `versions.env` at install time (or that resolve via env-var indirection for remote HTTP servers)
- The env-block in `.mcp.json` is the SSOT for redaction allowlist per ADR-0039

### Out of scope (deferred)

- Lifecycle scripts (Phase 3)
- Agent allowlist edits (Phase 4)
- auditing-mcp augmentation (Phase 4)

### Prerequisites

- Phase 1 complete (ADRs promoted; versions.env exists; devcontainer.json Features block ready)

### Tasks

#### T2.1: Author `KB-mcp-platform/SKILL.md` frontmatter + body

- **Layer:** Claude Code
- **Description:** Create `.claude/skills/KB-mcp-platform/SKILL.md`. Frontmatter follows ADR-0020 (lowercase-hyphenated `name: kb-mcp-platform`) + ADR-0030 (`pedagogical_sections:` block with one entry per reference file, each carrying a justification naming the specific OP-rule and anti-pattern — per D-3 / I-DR-005 tightening). `description:` ends with the sister-cross-reference to KB-mcp-design per the universal trifecta convention. Body declares family membership in prose; cites GitNexus among covered servers per AC-FR-11-d.
- **Dependencies:** T1.1 (ADRs available for citation).
- **Estimate:** M
- **Satisfies AC:** AC-FR-11-a (KB-mcp-platform exists in trifecta shape); AC-CC-8 (trifecta structural conventions: lowercase-hyphenated name, sister cross-reference); AC-FR-11-d (cross-reference; names GitNexus).
- **L1 verification:** File exists; `yq` parses frontmatter; `name: kb-mcp-platform`; `description:` non-empty.
- **L2 verification:** `pedagogical_sections:` carries one entry per `references/*.md`; each entry's justification names a specific OP-rule (OP-1 through OP-10) or anti-pattern; sister cross-reference to KB-mcp-design present in description.
- **L3 verification:** Augmented `auditing-mcp` OP-7 trifecta-consistency rule passes against the live skill structure — Phase 5.

#### T2.2: Author `KB-mcp-platform/references/` (~7 reference files) + `assets/templates/`

- **Layer:** Claude Code
- **Description:** Create the reference files (one per pedagogical_section entry). Mandatory references per Blueprint §FR-11:
  - `references/gitnexus-and-fallback.md` (AC-CC-9: names GitNexus primary; cites ADR-0007 v2.2.0; documents codebase-memory-mcp fallback policy at the project level even though this feature does not provision it per Gate-4 OI-1 closure; preserves `primary_degraded` schema-level provision)
  - `references/seven-named-servers.md` (one section per server: Serena, mcp-openapi-schema, actionlint-mcp, terraform-mcp, gitnexus, context7, exa — what it is, when to use, how it's authenticated)
  - `references/lifecycle-hooks.md` (the runbook role per Referenced Specifications)
  - `references/credential-handling.md` (per ADR-0039 — env-block SSOT, redact-at-source, OP-9 URL-credential rejection, OP-10 argv-leakage rejection)
  - `references/mcp-events-jsonl.md` (event-surface user-facing description; the schema canonical home is in KB-mcp-design)
  - `references/operator-runbook.md` (operator workflow for failures, including the tail-MCP-logs command)
  - `references/troubleshooting.md` (failure modes + remediation pointers per FR-8-d)
  - Author `assets/templates/mcp.json.tmpl` — the seven-entry `.mcp.json` template T2.4 customizes
- **Dependencies:** T2.1 (SKILL.md must declare pedagogical_sections first).
- **Estimate:** L
- **Satisfies AC:** AC-FR-11-a; AC-CC-8 (`assets/templates/` exists as trifecta What-half convention); AC-CC-9 (gitnexus-and-fallback names GitNexus primary + cites ADR-0007 v2.2.0); AC-FR-11-d (cross-reference completeness).
- **L1 verification:** `ls .claude/skills/KB-mcp-platform/references/*.md` returns the named files; `ls .claude/skills/KB-mcp-platform/assets/templates/` returns at least `mcp.json.tmpl`.
- **L2 verification:** `references/gitnexus-and-fallback.md` contains the strings "GitNexus" and "ADR-0007" and "primary" and "fallback"; `references/credential-handling.md` cites ADR-0039.
- **L3 verification:** Augmented `auditing-mcp` OP-7 + OP-4 audit rules pass — Phase 5.

#### T2.3: Author `KB-mcp-design/SKILL.md` + 2 reference files (no assets)

- **Layer:** Claude Code
- **Description:** Create `.claude/skills/KB-mcp-design/SKILL.md` per ADR-0020 (lowercase-hyphenated `name: kb-mcp-design`) + ADR-0030 (`pedagogical_sections:` block — one entry per the 2 references). Body declares family membership in prose; sister cross-reference to KB-mcp-platform in description. Then create:
  - `references/patterns-and-anti-patterns.md` (the design-time pattern catalog; URL-embedded credentials anti-pattern from C-0259/C-0260 cited explicitly; argv-leakage from C-0094/E-0094)
  - `references/principles.md` — **the canonical home for the `mcp-events.jsonl` schema per ADR-0037**. Includes the JSON schema for: `readiness_probe`, `tool_call_failure`, `transport_error`, `primary_degraded` (forward-looking; not exercised in this feature per Gate-4 OI-1 closure), `structured_failure`. Per AC-CC-9, the `primary_degraded` schema is preserved as schema-level provision.
- **Dependencies:** T2.1 (sister-cross-reference target must exist), T1.1 (ADR-0037 available for citation).
- **Estimate:** L
- **Satisfies AC:** AC-FR-11-b (KB-mcp-design exists in trifecta shape); AC-CC-8 (design half = exactly 2 references, NO `assets/`); AC-CC-9 (`primary_degraded` schema preserved); AC-CC-7 schema definition (the `mcp-events.jsonl` schema is owned here, consumed by postStart.sh in Phase 3).
- **L1 verification:** `ls .claude/skills/KB-mcp-design/references/*.md` returns exactly 2 files; `! test -d .claude/skills/KB-mcp-design/assets` (no assets dir).
- **L2 verification:** `references/principles.md` contains JSON schema sections for `readiness_probe`, `tool_call_failure`, `transport_error`, `primary_degraded`, `structured_failure`. `patterns-and-anti-patterns.md` mentions URL-embedded credentials anti-pattern + argv-leakage anti-pattern.
- **L3 verification:** Augmented `auditing-mcp` OP-7 passes (trifecta-consistency); OP-6 redaction-integrity check uses the schema correctly — Phase 5.

#### T2.4: Author `.mcp.json` at repo root (7 entries; no fallback)

- **Layer:** Claude Code
- **Description:** Create `.mcp.json` at repo root with exactly **seven** `mcpServers` entries per Gate-4 OI-1 closure. Per ADR-0039 redact-at-source posture, each entry uses `env:` block for env-var indirection (not URL-query, not argv). Per ADR-0041 install posture, each entry's command/args refer to either an installed binary (5 OSS-local servers) or a remote HTTP endpoint (Context7, Exa):
  - `serena`: `command: "uvx"`, `args: ["--from", "${SERENA_REF}", "serena"]` per ADR-0040 narrow allowlist
  - `mcp-openapi-schema`: `command: "npx"`, `args: ["-y", "mcp-openapi-schema@${MCP_OPENAPI_SCHEMA_VERSION}"]`
  - `actionlint-mcp`: `command: "actionlint-mcp"` (installed to PATH by postCreate via `go install`)
  - `terraform-mcp`: `command: "terraform-mcp"` (installed to PATH by postCreate per ADR-0041)
  - `gitnexus`: `command: "npx"`, `args: ["-y", "gitnexus@${GITNEXUS_TAG}", "mcp"]`, `env: {"GITNEXUS_SKIP_OPTIONAL_GRAMMARS": "1"}` per AC-CS-9 (npm install path per reconciliation-log-cycle-3.md F2; the env-var still suppresses the npm-vendored tree-sitter C++ grammar build — wrapping intent of AC-CS-9 preserved)
  - `context7`: `transport: "http"`, `url: "https://mcp.context7.com/mcp"`, `headers: {"CONTEXT7_API_KEY": "${CONTEXT7_API_KEY}"}` per ADR-0039 + GitHub README canonical form (URL-query REJECTED; canonical header is the literal `CONTEXT7_API_KEY` header name per Upstash README quote in T-005 v3.0.0, not `Authorization: Bearer`)
  - `exa`: `transport: "http"`, `url: "https://mcp.exa.ai/mcp"`, `headers: {"x-api-key": "${EXA_API_KEY}"}` per ADR-0039 (T0.7 confirmed flag form)
  - **NO codebase-memory-mcp entry per Gate-4 OI-1 closure**
  - Per ADR-0041 / T0.8, `<PIN_TBD>` is the canonical placeholder if a pin isn't yet substituted (postCreate substitutes at install time).
- **Dependencies:** T2.2 (template at `KB-mcp-platform/assets/templates/mcp.json.tmpl`); T1.3 (env-var names from versions.env must be stable); T0.5 (Context7 auth surface confirmed); T0.7 (Exa flag form confirmed).
- **Estimate:** M
- **Satisfies AC:** AC-FR-1-a (precondition); AC-CC-1 (exactly 7 named servers); AC-FR-5-a + AC-CS-6 (env-var indirection); AC-X-2 (canonical inventory disposition — 7 entries no fallback); AC-CC-4 (no literal credentials — env-var names only); AC-CC-9 (no codebase-memory-mcp inline; but `primary_degraded` schema preserved in KB-mcp-design); AC-FR-2-b (tools callable from agents — `.mcp.json` registers them).
- **L1 verification:** `jq '.mcpServers | keys | length' .mcp.json` returns `7`; the keys are exactly `["actionlint-mcp", "context7", "exa", "gitnexus", "mcp-openapi-schema", "serena", "terraform-mcp"]` (alphabetical jq output).
- **L2 verification:** `jq -e '.mcpServers.context7.headers.CONTEXT7_API_KEY' .mcp.json` returns `"${CONTEXT7_API_KEY}"` (env-var indirection via canonical header name per GitHub README, not literal); `jq '.mcpServers.exa.url' .mcp.json` does NOT contain `apiKey` query param (OP-9); no entry has `--api-key` in args (OP-10); `jq '.mcpServers.gitnexus.env.GITNEXUS_SKIP_OPTIONAL_GRAMMARS' .mcp.json` returns `"1"`.
- **L3 verification:** `claude mcp list` after postCreate shows 7 entries (AC-CC-1); `git grep` for credential-shape patterns returns zero hits in `.mcp.json` (AC-CC-4); augmented `auditing-mcp` OP-1 / OP-2 / OP-8 / OP-9 / OP-10 pass — Phase 5.

### Phase 2 Exit Criteria

- `KB-mcp-platform/SKILL.md` + ~7 references + `assets/templates/mcp.json.tmpl` exist; trifecta What-half structural conventions met (AC-CC-8 What-half checks)
- `KB-mcp-design/SKILL.md` + exactly 2 references; no `assets/` directory; trifecta How-half structural conventions met (AC-CC-8 How-half checks); `mcp-events.jsonl` schema in `references/principles.md`
- `.mcp.json` exists at repo root with exactly 7 `mcpServers` entries; no fallback entry; no literal credentials (env-var indirection throughout); no URL-query credential pattern; no argv credential pattern
- Cross-reference between KB-mcp-platform and KB-mcp-design is explicit in both descriptions; both name GitNexus among covered servers (AC-FR-11-d)

Phase Validator: file-existence + frontmatter assertions; jq queries on `.mcp.json` for entry count and env-var indirection; grep for absence of literal credentials.

### Phase 2 Rollback Path

- `git revert` Phase 2 commits in reverse order
- Skills are additive; removing them does not affect existing skills (no inheritance)
- `.mcp.json` removal returns Claude Code to "no project-scope MCP servers" — preserves C-0462 (file absent) prior state
- Phase 1 substrate (devcontainer.json, ADRs) remains intact; Phase 3 / 4 can be re-authored after rollback
- No live Codespace runtime impact yet (Phase 3 scripts haven't shipped)

---

## Phase 3 — Devcontainer Lifecycle Scripts (postCreate, postStart, helper libs)

### Goal

Author the lifecycle scripts that install the 5 OSS-local servers (postCreate), probe all 7 registered servers (postStart), and provide the probe primitives (`lib/mcp-ping.sh`, `lib/mcp-auth-probe.sh`, `install/terraform-mcp.sh`). Per Blueprint Implementation Plan steps 5 + 6, these come AFTER `.mcp.json` exists (Phase 2) because postStart enumerates servers from `.mcp.json`, and after `versions.env` exists (Phase 1) because postCreate sources pin values from it.

### Scope

- `.devcontainer/lib/mcp-ping.sh` (per-server ping primitive; uses `claude mcp ping` if T0.6 confirmed, else direct JSON-RPC fallback)
- `.devcontainer/lib/mcp-auth-probe.sh` (Context7 + Exa supplementary auth probes; gated on `MCP_AUTH_PROBE=1` per D-0008)
- `.devcontainer/install/terraform-mcp.sh` (wget + SHA256SUMS + GPG verify per ADR-0041)
- `.devcontainer/postCreate.sh` (idempotent install with version-pinned sentinels + binary-presence check; 5 OSS-local servers)
- `.devcontainer/postStart.sh` (readiness probe; writes 7 `readiness_probe` records per cycle to `mcp-events.jsonl` per Gate-4 OI-1 closure)
- Per ADR-0039 redact-at-source: every write to `mcp-events.jsonl` passes through a redaction filter (env-block allowlist + HTTP-headers allowlist from `.mcp.json`); default-fail-closed if allowlist is empty (AC-NFR-2-d)

### Out of scope (deferred)

- Agent allowlist edits (Phase 4)
- auditing-mcp augmentation (Phase 4)
- Gate-6 hard-gate wiring (Phase 5)

### Prerequisites

- Phase 2 complete (`.mcp.json` + KB-mcp-design `principles.md` with `mcp-events.jsonl` schema exist; lifecycle scripts consume both)
- T0.6 (ping CLI presence) confirmed
- §D-6 (postAttach staleness threshold + on-demand command shape) resolved in T3.5 below

### Tasks

#### T3.1: Author `.devcontainer/lib/mcp-ping.sh`

- **Layer:** Codespaces
- **Description:** Bash script that takes one argument (server name from `.mcp.json` keys) and probes it. Behavior:
  - If T0.6 confirmed `claude mcp ping` exists, shell out to it (returns 0 on success, non-zero on transport/auth failure)
  - Else, parse `.mcp.json` for that server's command/url, then issue a direct JSON-RPC `ping` over stdio (for stdio servers) or HTTP POST (for Context7/Exa)
  - Output is a JSON object with fields: `server`, `result` (`pass`|`fail`), `failure_layer` (one of `transport`|`auth`|`startup`|`tool`|`config` — empty on pass), `latency_ms`, `message_redacted` (the error message with credentials redacted per ADR-0039)
  - On a `missing env-var` condition (e.g., `CONTEXT7_API_KEY` is unset at probe time), the script returns `result=fail`, `failure_layer=auth`, `message_redacted="missing env-var CONTEXT7_API_KEY"` per AC-X-1
- **Dependencies:** T0.6 (CLI presence), T2.3 (mcp-events.jsonl schema available for the output structure).
- **Estimate:** M
- **Satisfies AC:** AC-FR-1-b (per-server probe returns success); AC-FR-4-a (probe returns success); AC-FR-4-b (failure surfaces server name + input + error); AC-X-1 (missing env-var distinguishable failure mode).
- **L1 verification:** `bash -n .devcontainer/lib/mcp-ping.sh` parses; `shellcheck` returns no errors.
- **L2 verification:** `mcp-ping.sh nonexistent` (server not in `.mcp.json`) returns non-zero with a clear "unknown server" message; `mcp-ping.sh serena` against a stubbed local Serena returns `result=pass`.
- **L3 verification:** Inside a real Codespace post-Phase-3-ship, `mcp-ping.sh <each-of-7>` returns `result=pass` for all 7 — Phase 5.

#### T3.2: Author `.devcontainer/lib/mcp-auth-probe.sh`

- **Layer:** Codespaces
- **Description:** Bash helper that performs the supplementary auth probe for Context7 and Exa (the two remote-HTTP servers). Behavior:
  - Gated on `MCP_AUTH_PROBE` env var: `=1` runs; `=0` (or unset) short-circuits to "skipped"
  - For each of `context7` and `exa`, issues a documented low-cost authenticated call (e.g., `tools/list` JSON-RPC over HTTP with the auth header). A 401/403 → `failure_layer=auth`; a 200 with non-empty tools → pass; any other response → `failure_layer=transport`
  - Per ADR-0041 D-0008: postCreate runs with `MCP_AUTH_PROBE=1` (initial-install verify); postStart runs with `MCP_AUTH_PROBE=0` (every-attach probe; respects API quota — ping-only)
  - Per AC-X-1: if `CONTEXT7_API_KEY` or `EXA_API_KEY` is unset/empty, returns `result=fail`, `failure_layer=auth`, `message_redacted="missing env-var <NAME>"` — distinguishable from auth-with-key-rejected
- **Dependencies:** T3.1 (output-format alignment with `mcp-ping.sh`).
- **Estimate:** M
- **Satisfies AC:** AC-FR-1-b (per-server probe — supplementary for HTTP servers); AC-FR-5-b (unset credential → clearly named "missing credential" failure); AC-X-1 (env-var-absent distinguishable); AC-FR-9-b (tool-level error response includes server name, tool name, error).
- **L1 verification:** `bash -n .devcontainer/lib/mcp-auth-probe.sh` parses; `shellcheck` clean.
- **L2 verification:** With `MCP_AUTH_PROBE=0` and any state: returns "skipped" for both servers; with `MCP_AUTH_PROBE=1` and `CONTEXT7_API_KEY=""`: returns `failure_layer=auth`, `message_redacted="missing env-var CONTEXT7_API_KEY"`.
- **L3 verification:** AC-X-1 + AC-FR-5-b pass in a real Codespace with the secret intentionally unset — Phase 5.

#### T3.3: Author `.devcontainer/install/terraform-mcp.sh`

- **Layer:** Codespaces
- **Description:** Per ADR-0041 binary-fetch path:
  - `wget` the release tarball from `releases.hashicorp.com` at the version pinned in `versions.env`
  - `wget` the `SHA256SUMS` file
  - Verify SHA256 with `sha256sum -c` against the tarball
  - `wget` the `SHA256SUMS.sig` file
  - `gpg --verify SHA256SUMS.sig SHA256SUMS` against HashiCorp's well-known public key (script imports the key from the documented fingerprint; the key fingerprint is recorded in the verify-at-execution log per T0.1)
  - Untar to `/usr/local/bin/terraform-mcp`; `chmod +x`
  - Exit non-zero on any verification failure (per AC-CS-3 fail-fast)
- **Dependencies:** T0.1 (version + SHA256 + GPG key fingerprint from verify-at-execution log).
- **Estimate:** M
- **Satisfies AC:** AC-FR-1-a (binary present after install); AC-CS-3 (fail-fast on install failure); supply-chain reproducibility per ADR-0041 D-0011.
- **L1 verification:** `bash -n` parses; `shellcheck` clean.
- **L2 verification:** Run in a scratch container against the pinned version; the script exits 0; `terraform-mcp --version` returns the pinned version.
- **L3 verification:** Inside a real Codespace post-postCreate, `which terraform-mcp` returns a path and `terraform-mcp --version` returns the pinned version — Phase 5.

#### T3.4: Author `.devcontainer/postCreate.sh` (idempotent install of 5 OSS-local servers)

- **Layer:** Codespaces
- **Description:** Bash script invoked by `devcontainer.json`'s `postCreateCommand`. Per ADR-0041 hybrid install posture + sentinel-and-binary-presence pattern:
  - Source `.devcontainer/versions.env`
  - For each of the 5 OSS-local servers (serena, mcp-openapi-schema, actionlint-mcp, terraform-mcp, gitnexus), check `sentinel_present AND binary_present` (per AC-CS-2):
    - Sentinel: `/var/lib/devcontainer/sentinels/<server>@<version>.installed`
    - Binary presence: `command -v <expected-binary>` (or for uvx servers, `uvx --from <pin> <server> --help`)
  - If both present: skip ("already-satisfied")
  - If sentinel present but binary missing: re-install (recovers from sentinel-without-binary skew per OP-5)
  - On install: run the per-server install command:
    - serena: `uvx --from "${SERENA_REF}" serena --help` (uvx caches; `--help` confirms)
    - mcp-openapi-schema: `npx -y "mcp-openapi-schema@${MCP_OPENAPI_SCHEMA_VERSION}" --help`
    - actionlint-mcp: `go install "github.com/hongkongkiwi/actionlint-mcp@${ACTIONLINT_MCP_SHA}"` (no `/cmd/actionlint-mcp` subpath — `main.go` lives at the repo root in the corrected upstream per reconciliation-log-cycle-3.md F1)
    - terraform-mcp: invoke `.devcontainer/install/terraform-mcp.sh`
    - gitnexus: persistent install via `GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1 npm install -g "gitnexus@${GITNEXUS_TAG}"` followed by smoke-test `GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1 npx -y "gitnexus@${GITNEXUS_TAG}" mcp --help` (or equivalent help/version invocation) per AC-CS-9; postCreate fails if the smoke-test fails. (Install form corrected per reconciliation-log-cycle-3.md F2 — gitnexus is published on npm, not PyPI; the `GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1` env var still suppresses the npm-vendored tree-sitter C++ grammar build, preserving AC-CS-9's wrapping intent. Node 20 LTS comes from the Node devcontainer Feature wired in T1.4 — load-bearing prereq.)
  - On per-server install failure: print to stderr `INSTALL FAILED: <server>` and `exit 1` (AC-CS-3)
  - On install success: write the sentinel file; write a single `install_complete` event to `.claude/runtime/mcp-events.jsonl` (one record per server per install, redacted per ADR-0039)
  - At end of all installs: run `MCP_AUTH_PROBE=1 .devcontainer/lib/mcp-auth-probe.sh` to verify Context7 + Exa auth surfaces (the 2 remote HTTP servers)
  - Print a consolidated health-check summary line to stdout per AC-FR-8-a: `MCP health: <N>/7 connected` (counts on the ping output from T3.1 — but stdout summary at postCreate only; the per-server records go to mcp-events.jsonl by T3.5)
- **Dependencies:** T1.3 (versions.env), T1.4 (devcontainer.json wires postCreateCommand), T2.4 (.mcp.json registers what to install), T3.1 (ping primitive), T3.2 (auth probe), T3.3 (terraform install).
- **Estimate:** L
- **Satisfies AC:** AC-FR-1-a (servers installed + registered); AC-CS-2 (idempotence — sentinel + binary check); AC-CS-3 (fail-fast); AC-CS-8 (warm-cache short-circuit); AC-CS-9 (GitNexus skip-grammars smoke-test fails postCreate on failure); AC-FR-8-a (postCreate consolidated health-check output); AC-CS-1 indirectly (Node 20 + Go from Features are prerequisites).
- **L1 verification:** `bash -n .devcontainer/postCreate.sh` parses; `shellcheck` clean.
- **L2 verification:** Sentinel-and-binary check logic exercised in unit-style script tests: with sentinel-only, re-install runs; with both present, short-circuits.
- **L3 verification:** Cold-cache postCreate completes within NFR-1 ~10 min (AC-NFR-1-a + AC-CS-8); warm-cache re-run completes within ~2 min (AC-NFR-1-b + AC-CS-2 + AC-CS-8); `claude mcp list` after postCreate shows 7 connected (AC-CC-1) — Phase 5.

#### T3.5: Author `.devcontainer/postStart.sh` (readiness probe; 7 records per cycle) + resolve §D-6 postAttach surface

- **Layer:** Codespaces
- **Description:** Bash script invoked by `devcontainer.json`'s `postStartCommand`. Per AC-CS-4 / AC-CC-6 / Gate-4 OI-1 closure:
  - Enumerate the 7 servers from `.mcp.json` (`jq -r '.mcpServers | keys[]'`)
  - For each server: invoke `.devcontainer/lib/mcp-ping.sh <server>`; capture the JSON output; pass through the redaction filter (allowlist = env-block names + HTTP-headers allowlist from `.mcp.json`; default-fail-closed if allowlist is empty per ADR-0039 / AC-NFR-2-d); append exactly one `readiness_probe` record to `.claude/runtime/mcp-events.jsonl`
  - After all 7 probes: if any returned `fail`, emit a stderr banner `MCP readiness: <N-fail>/7 degraded — see .claude/runtime/mcp-events.jsonl` and `exit 0` (warn-and-continue per AC-CS-5)
  - If all passed: emit stderr banner `MCP readiness: 7/7 healthy` and `exit 0`
  - Per AC-CS-8 NFR-1: completion within ~15 s
  - **§D-6 postAttach resolution**: postAttach is NOT a separate script in this Plan; instead, AC-FR-8-c is satisfied by:
    - An on-demand command shape: `.devcontainer/lib/mcp-ping.sh all` (operator runs explicitly to refresh); this re-uses T3.1 with no additional script
    - The "staleness threshold" for postAttach surface is set to **5 minutes**: postAttach reads the most-recent `readiness_probe` block in `mcp-events.jsonl` (the 7 records emitted by the latest postStart); if those records are older than 5 minutes wall-clock, postAttach automatically re-runs `postStart.sh` (so postAttach reuses postStart, no separate script); else surfaces the cached result
    - This resolution is documented in `KB-mcp-platform/references/lifecycle-hooks.md` (authored in Phase 2)
- **Dependencies:** T2.3 (mcp-events.jsonl schema in KB-mcp-design), T2.4 (.mcp.json server enumeration), T3.1 (ping primitive), T3.4 (postCreate sentinel ensures binaries exist), T1.4 (devcontainer.json wires postStartCommand + the operator-on-demand command alias).
- **Estimate:** L
- **Satisfies AC:** AC-FR-1-a, AC-FR-1-b, AC-FR-1-c (probe failure surfaces server name + layer); AC-FR-8-b (postStart re-runs check); AC-FR-8-c (postAttach surface — per the §D-6 resolution above); AC-FR-8-d (failing layer + remediation hint); AC-FR-8-e (operator-invokable on demand); AC-CS-4 (exactly 7 readiness_probe records per cycle); AC-CS-5 (warn-and-continue with stderr banner); AC-CC-6 (7 records with result/failure_layer); AC-CS-8 (~15s probe time); AC-NFR-2-d (redact-at-source filter; default-fail-closed); AC-X-1 (missing env-var distinguishable in records); AC-FR-9-a (mid-run server failure structured record — postStart fires on session start, captures this); AC-FR-10-a/b/c (events captured at documented location; reconstructable; tail command via `tail -f .claude/runtime/mcp-events.jsonl`); AC-FR-10-d (redaction).
- **L1 verification:** `bash -n .devcontainer/postStart.sh` parses; `shellcheck` clean.
- **L2 verification:** Stubbed `mcp-ping.sh` return values exercise the all-pass / partial-fail paths; the script emits the correct stderr banner; the JSONL file shape parses as 7 JSON objects per cycle.
- **L3 verification:** Live Codespace postStart writes exactly 7 records (AC-CS-4 + AC-CC-6); a deliberately broken server's record carries `result=fail` and `failure_layer` (AC-FR-1-c); the stderr banner names the degraded count (AC-CS-5); the staleness-threshold logic re-fires postStart at attach if >5 minutes have elapsed (AC-FR-8-c) — Phase 5.

#### T3.6: Wire `.gitignore` for `.claude/runtime/mcp-events.jsonl`

- **Layer:** Claude Code
- **Description:** This was bootstrapped in T0.10 (the directory + `.gitkeep`). T3.6 verifies the `.gitignore` line is still present after Phase 1–3 churn and that no `mcp-events.jsonl` is in git history. (No new code; verification-only task to catch any regression introduced by Phase 1–3 edits to `.gitignore`.)
- **Dependencies:** T0.10, T3.5.
- **Estimate:** XS
- **Satisfies AC:** AC-CC-4 (no literal credentials in committed files); AC-NFR-2-a; AC-FR-10-d (redaction; the jsonl is also never committed).
- **L1 verification:** `git check-ignore .claude/runtime/mcp-events.jsonl` returns the path.
- **L2 verification:** `git log --all -- .claude/runtime/mcp-events.jsonl` returns nothing (never tracked).
- **L3 verification:** `git grep` for any credential-shape pattern across the working tree (including ignored files) returns zero hits — Phase 5.

### Phase 3 Exit Criteria

- `.devcontainer/lib/mcp-ping.sh`, `.devcontainer/lib/mcp-auth-probe.sh`, `.devcontainer/install/terraform-mcp.sh`, `.devcontainer/postCreate.sh`, `.devcontainer/postStart.sh` all exist; all `shellcheck`-clean
- postCreate idempotence pattern (sentinel + binary-presence) exercised in script-level unit tests
- postStart writes exactly 7 records per cycle (per Gate-4 OI-1 closure) into `.claude/runtime/mcp-events.jsonl`; redaction filter active per ADR-0039 / AC-NFR-2-d
- postAttach surface staleness threshold = 5 minutes (per §D-6 resolution); operator-on-demand command documented in `KB-mcp-platform/references/lifecycle-hooks.md`
- `.gitignore` still ignores `.claude/runtime/mcp-events.jsonl`; never tracked in history

Phase Validator: shellcheck clean for all 5 scripts; bash parse clean; redaction filter unit-tested with synthetic credential fixtures; sentinel + binary-presence pattern documented + tested.

### Phase 3 Rollback Path

- `git revert` Phase 3 commits in reverse order — restores Codespace to "no postCreate / postStart" state (lifecycle hooks no longer reference scripts; devcontainer.json's `postCreateCommand` / `postStartCommand` lines roll back too)
- Existing Codespaces continue running; no MCP wiring affected at the agent level (Phase 4 is still pending)
- Re-author can resume from Phase 3 cleanly — no destructive operations to roll back

---

## Phase 4 — Agent Allowlist Edits + auditing-mcp Augmentation + Family Graduation

### Goal

Wire the 8 consumer agents to use the registered MCP servers (per ADR-0040 5-agent Serena allowlist + base consumer-mapping; union = 8 unique). Augment the `auditing-mcp` skill with the 10 rule families (OP-1..OP-10) per Blueprint Implementation Plan step 8. Execute the 6 ADR-0042 family-graduation structural tasks. Per Blueprint sequencing, this runs AFTER `.mcp.json` exists (Phase 2) and AFTER lifecycle scripts exist (Phase 3) so the audit rules validate live state.

### Scope

- 8 of 36 `.claude/agents/*.md` edits (mcp__<server>__<tool> entries)
- 10 new audit rule families in `auditing-mcp/`: OP-1 (env-block coverage), OP-2 (consumer-mapping), OP-3 (zero-mcp__ preservation), OP-4 (primary/fallback prose), OP-5 (lifecycle completeness), OP-6 (runtime log redaction), OP-7 (trifecta consistency), OP-8 (GitNexus-specific), OP-9 (URL-credential rejection), OP-10 (argv-leakage absence)
- 6 audit scripts (new) + 2 existing extended (per Blueprint Skills table)
- The 6 ADR-0042 family-graduation structural tasks (per orchestrator brief)
- §OI-4 (per-agent context-overhead measurement) wired here as T4.7
- §OI-6 event-trigger discipline applied: the ADR-0040 Serena 5-agent allowlist entry on `design-codespaces` does NOT introduce calendar machinery; the event trigger is "when auditing-codespaces stub-fill is undertaken"

### Out of scope (deferred)

- Gate-6 orchestrator hard-gate wiring (Phase 5)
- End-to-end live verification (Phase 5)

### Prerequisites

- Phase 2 (.mcp.json + KB-mcp-platform + KB-mcp-design)
- Phase 3 (lifecycle scripts; the OP-5 audit reads devcontainer.json; OP-6 reads mcp-events.jsonl after at least one postStart cycle)
- ADR-0042 promoted (T1.1)

### Tasks

#### T4.1: Edit 8 agent files — add `mcp__<server>__<tool>` entries

- **Layer:** Claude Code
- **Description:** Per the consumer-mapping table in Blueprint §Claude Code Design + ADR-0040 5-agent Serena narrowing (union = 8 unique). Edit the `tools:` array in each agent's frontmatter to add the prescribed `mcp__<server>__<tool>` entries (and no others, per AC-CC-2):
  - `.claude/agents/design-api.md`: add `mcp__mcp-openapi-schema__*` tools
  - `.claude/agents/design-cicd.md`: add `mcp__actionlint-mcp__*` AND `mcp__serena__*` (Serena narrowing per ADR-0040)
  - `.claude/agents/design-iac.md`: add `mcp__terraform-mcp__*` tools
  - `.claude/agents/discovery-external-researcher.md`: add `mcp__context7__*` AND `mcp__exa__*` tools (Context7 names per T0.5 verified for v1.2.0 + rename to `ReplaceContentTool`)
  - `.claude/agents/discovery-codebase-researcher.md`: add `mcp__gitnexus__*` AND `mcp__serena__*` (Serena per ADR-0040)
  - `.claude/agents/review-architecture-auditor.md`: add `mcp__gitnexus__*` AND `mcp__serena__*` (Serena per ADR-0040)
  - `.claude/agents/design-claude-code.md`: add `mcp__serena__*` (per ADR-0040 net-new). Note: filename is `design-claude-code.md`; the agent frontmatter `name:` field is `design-cc` per the Path-A reserved-word workaround.
  - `.claude/agents/design-codespaces.md`: add `mcp__serena__*` (per ADR-0040 net-new; forward-looking on §OI-6 / ADR-0033 stub-fill — event trigger is the stub-fill itself, no calendar)
  - Verify per agent that `model:` / `effort:` / `skills:` fields are NOT touched (cc-design Principle 9 per ADR-0022).
  - **No `mcp__codebase-memory-mcp__*` entries anywhere per Gate-4 OI-1 closure.**
- **Dependencies:** T2.4 (.mcp.json server names must exist for allowlist entries to be valid); T0.5 (Context7 tool names confirmed).
- **Estimate:** M
- **Satisfies AC:** AC-FR-2-a (agents show MCP tool entries); AC-FR-2-b (tools callable); AC-CC-2 (prescribed entries; no others).
- **L1 verification:** For each of the 8 agents: `yq '.tools' <file>` returns an array; each prescribed `mcp__<server>__<tool>` entry is present.
- **L2 verification:** For each of the 8 agents: `yq '.model // .effort // .skills' <file>` is unchanged from pre-edit (Principle 9); spot-check a couple by diff.
- **L3 verification:** Running each agent (in a real Codespace post-Phase-5) successfully invokes one of its allowed MCP tools — Phase 5.

#### T4.2: Verify 28 non-consumer agents preserve zero `mcp__` entries (C-0445 invariant)

- **Layer:** Claude Code
- **Description:** No edits; verification only. After T4.1, run a grep sweep across the other 28 agent files: `for f in .claude/agents/*.md; do if echo "$f" | grep -vqE "(design-api|design-cicd|design-iac|discovery-external-researcher|discovery-codebase-researcher|review-architecture-auditor|design-cc|design-codespaces).md"; then grep -L 'mcp__' "$f" || echo "REGRESSION: $f"; fi; done` should produce no `REGRESSION:` lines.
- **Dependencies:** T4.1.
- **Estimate:** XS
- **Satisfies AC:** AC-CC-3 (zero `mcp__` entries on 28 non-consumer agents).
- **L1 verification:** The grep-sweep script (run inline) produces no `REGRESSION:` output.
- **L2 verification:** Same — automated via the sweep.
- **L3 verification:** auditing-mcp OP-3 rule passes when run end-to-end — Phase 5.

#### T4.3: Author 10 audit-rule scripts in `auditing-mcp/scripts/`

- **Layer:** Claude Code
- **Description:** Per Blueprint Skills table + Implementation Plan step 8. The augmented `auditing-mcp` has scripts (Python primary, per existing project precedent). Create or extend:
  - `audit_op1_env_block_coverage.py` — every `.mcp.json` server with credentials uses env-block indirection
  - `audit_op2_consumer_mapping.py` — every `mcp__<server>__<tool>` entry in any agent maps to a server registered in `.mcp.json`
  - `audit_op3_zero_mcp_invariant.py` — the 28 non-consumer agents carry zero `mcp__` entries
  - `audit_op4_primary_fallback_prose.py` — `discovery-codebase-researcher.md` lines 3, 20, 29, 156 contain the prose primary/fallback references (per Gate-4 OI-1 closure: this is a forward-looking schema-level provision; the rule still runs and still passes because the prose is preserved)
  - `audit_op5_lifecycle_completeness.py` — `devcontainer.json` carries `postCreateCommand` + `postStartCommand` referencing the scripts; the scripts exist; sentinel pattern present in postCreate.sh
  - `audit_op6_runtime_log_redaction.py` — synthetic credential strings (per `secrets-rubric.md`) seeded into a test `mcp-events.jsonl` file are correctly redacted by the redaction filter; default-fail-closed verified
  - `audit_op7_trifecta_consistency.py` — `KB-mcp-platform` ↔ `KB-mcp-design` cross-references present; both name GitNexus; structural conventions (lowercase-hyphenated name; sister cross-ref in description; design half = 2 refs no assets; platform half = many refs + assets/templates/)
  - `audit_op8_gitnexus.py` — `.mcp.json` gitnexus entry carries `GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1`; postCreate runs the smoke-test
  - `audit_op9_url_credential_rejection.py` — no `.mcp.json` entry's `url:` value contains a credential-shape pattern in query string (e.g., `exaApiKey=`)
  - `audit_op10_argv_leakage.py` — no `.mcp.json` entry's `args:` array contains `--api-key` or `--apikey` or similar (credential-shape literal in argv)
  - Top-level entry script: `scripts/audit_mcp.py` (extends existing) — orchestrates all 10 OP rules; supports `--with-runtime` flag that ALSO runs OP-6 against the live `.claude/runtime/mcp-events.jsonl`; produces a structured BLOCKER/MAJOR/MINOR severity report; non-zero exit on any BLOCKER finding (the hard-gate signal per ADR-0043)
- **Dependencies:** T2.4 (`.mcp.json` exists for OPs 1/2/4/8/9/10 to read); T3.4 + T3.5 (lifecycle scripts exist for OP-5 to read); T2.1 + T2.3 (skills exist for OP-7 to validate); T4.1 + T4.2 (agent edits + invariant checks for OPs 2 and 3).
- **Estimate:** L
- **Satisfies AC:** AC-FR-11-c (auditing-mcp augmented + GitNexus rules + runnable end-to-end); AC-CC-5 (rule families OP-1 through OP-10 run with zero BLOCKER findings — verified Phase 5); AC-NFR-2-c (zero BLOCKER findings at Gate 6).
- **L1 verification:** Each script file exists; `python -m py_compile <each>` succeeds; `audit_mcp.py --help` returns usage.
- **L2 verification:** Each OP script run in isolation against synthetic input fixtures (in `auditing-mcp/test-fixtures/`) returns the expected pass/fail result; the top-level `audit_mcp.py` aggregates correctly.
- **L3 verification:** `python .claude/skills/auditing-mcp/scripts/audit_mcp.py --with-runtime` returns exit 0 and zero BLOCKER findings against the live repo — Phase 5 (AC-CC-5 + AC-FR-11-c + AC-NFR-2-c).

#### T4.4: Update `auditing-mcp/SKILL.md` for family graduation (ADR-0042 graduation task 1 + 2)

- **Layer:** Claude Code
- **Description:** Per ADR-0042 / Gate-4 OI-2 closure, structural changes 1 and 2 from the orchestrator brief:
  1. Frontmatter: change `family: auditing-cc-configs` to `family: auditing-mcp` (own family-coordinator)
  2. Body: add `## Sub-skill family` section (initially empty — reserves the slot for future MCP-audit sub-skills per the coordinator pattern)
  Document the graduation rationale inline at the top of the body (summarizing ADR-0042 Decision in 1–2 sentences with cross-reference to the ADR).
- **Dependencies:** T1.1 (ADR-0042 in canonical `adrs/`).
- **Estimate:** S
- **Satisfies AC:** AC-CC-10 (family graduation structural complete — auditing-mcp side).
- **L1 verification:** `yq '.family' .claude/skills/auditing-mcp/SKILL.md` returns `auditing-mcp` (not `auditing-cc-configs`).
- **L2 verification:** `grep -E '^## Sub-skill family' .claude/skills/auditing-mcp/SKILL.md` matches; the section exists in the body.
- **L3 verification:** auditing-mcp OP-7 trifecta-consistency rule passes (structural assertions verify the frontmatter + body section per ADR-0042); structural test in Blueprint Verification §Per-Layer Test Strategy "family-graduation structural test" passes — Phase 5.

#### T4.5: Update `auditing-cc-configs/SKILL.md` — remove auditing-mcp from sub-skill family list (ADR-0042 task 3)

- **Layer:** Claude Code
- **Description:** Per ADR-0042 structural change 3: edit `.claude/skills/auditing-cc-configs/SKILL.md` lines 144–155 (approximate; verify line numbers at edit time). Remove the `auditing-mcp` row from the sub-skill family enumeration. Add inline rationale (1–2 sentences) noting the graduation per ADR-0042. Per ADR-0005, do NOT delete the historical fact; supplement with rationale.
- **Dependencies:** T1.1 (ADR-0042 referenceable).
- **Estimate:** S
- **Satisfies AC:** AC-CC-10 (auditing-cc-configs side of graduation complete).
- **L1 verification:** `grep -n 'auditing-mcp' .claude/skills/auditing-cc-configs/SKILL.md` does NOT match in the family-enumeration block (lines ~144–155).
- **L2 verification:** The inline graduation rationale is present with cross-reference to ADR-0042.
- **L3 verification:** auditing-mcp OP-7 + "family-graduation structural test" pass — Phase 5.

#### T4.6: Update `auditing-shared/SKILL.md` — add auditing-mcp as graduated-family consumer (ADR-0042 task 4) + Verify cross-file pair-check coverage (ADR-0042 task 5) + Update orchestrator-side singular→plural references (ADR-0042 task 6)

- **Layer:** Claude Code
- **Description:** Three sub-tasks bundled (cohesive change to ensure singular→plural / consumer-list drift is closed in one commit):
  - **(a)** Edit `.claude/skills/auditing-shared/SKILL.md`: the description was previously listing four consumers; add `auditing-mcp` as a now-independent family-coordinator consumer per ADR-0042.
  - **(b)** Inspect `auditing-cc-configs/references/cross-file-checks.md` for any MCP-relevant cross-file checks. If any exist (per orchestrator brief task 5), migrate them to `auditing-mcp/references/` (or document the migration choice inline if the check is genuinely cross-domain). Verify coverage is preserved end-to-end.
  - **(c)** Grep across `.claude/`, `Issues/`, `working/`, the orchestrator agent files, and the templates for any singular-form reference to "the auditing family" or "auditing-cc-configs family" that, post-graduation, must be plural ("the auditing families"). Update each occurrence with a brief inline rationale (cross-ref to ADR-0042).
- **Dependencies:** T4.4, T4.5 (graduation must be partially complete so the consumer-list update has a target).
- **Estimate:** M
- **Satisfies AC:** AC-CC-10 (auditing-shared side + ADR-0042 tasks 4/5/6 of the 6-step canonical graduation list).
- **L1 verification:** `yq '.description' .claude/skills/auditing-shared/SKILL.md` includes `auditing-mcp`; `grep -rE "the auditing famil(y|ies)" .claude/ Issues/ working/` returns updated phrasing in all hits.
- **L2 verification:** `auditing-cc-configs/references/cross-file-checks.md` migration choice documented inline; coverage preserved.
- **L3 verification:** auditing-mcp OP-7 + "family-graduation structural test" pass with zero family-list inconsistencies — Phase 5.

#### T4.7: §OI-4 — Per-agent context-overhead measurement

- **Layer:** Claude Code
- **Description:** Per Blueprint Open Items §OI-4 (still open; assigned to plan-author at implementation time). Measure the per-agent context overhead added by the 7 always-on MCP server registrations. Methodology:
  - For each of the 36 agents, capture a baseline token count of its session-startup context (before this feature ships, can be approximated from `.claude/agents/*.md` + skills + ADRs the agent loads)
  - Add the `.mcp.json` content's contribution: `.mcp.json` size in tokens (~one-time per session, not per-agent — but Claude Code loads it into every agent context)
  - Per cc-design Principle 1 (tool schemas deferred until invoked), do NOT count the per-tool schema cost; that defers to first invocation
  - Compare against PRD NFR-4 threshold ("tolerable envelope")
  - If a breach is detected: record in `verify-at-execution.md` with proposed re-scope (e.g., "downscoping to conditional activation per server"); halt Phase 4 pending user re-scoping decision
  - If within envelope: record the measurement (per-agent overhead in tokens) in `verify-at-execution.md` and close OI-4
- **Dependencies:** T2.4 (.mcp.json exists to measure), T4.1 (agent edits done so per-agent overhead is final).
- **Estimate:** M
- **Satisfies AC:** PRD NFR-4 (per-agent context overhead within tolerable envelope). No specific Blueprint AC ID; this is the OI-4 closure.
- **L1 verification:** `verify-at-execution.md` has a §OI-4 section with measured per-agent overhead numbers + comparison to PRD NFR-4.
- **L2 verification:** The measurement methodology + numbers are reproducible (the methodology is documented; numbers re-derivable).
- **L3 verification:** No re-scope filed against PRD NFR-4 by the time of Phase 5 — overhead within envelope (or the re-scope is closed by user decision before Phase 5 starts).

### Phase 4 Exit Criteria

- 8 of 36 agent files carry the prescribed `mcp__<server>__<tool>` entries per the consumer-mapping table; no others; `model:` / `effort:` / `skills:` fields unchanged
- 28 of 36 agent files preserve zero `mcp__` entries (C-0445)
- `auditing-mcp/scripts/` carries 10 OP scripts + the top-level `audit_mcp.py`; all `python -m py_compile`-clean; each OP passes against synthetic fixtures
- `auditing-mcp/SKILL.md` carries `family: auditing-mcp` frontmatter + `## Sub-skill family` body section
- `auditing-cc-configs/SKILL.md` no longer lists `auditing-mcp` in its sub-skill family enumeration
- `auditing-shared/SKILL.md` description lists `auditing-mcp` as a graduated-family consumer
- Cross-file pair-check coverage migration (if any) documented; orchestrator-side singular→plural references updated; OI-4 closed (measurement recorded, or re-scope filed)

Phase Validator: structural assertions (file-existence, frontmatter, body sections); `python -m py_compile` on each script; synthetic-fixture exercise of OP-6 redaction; grep for absence of `mcp__codebase-memory-mcp` anywhere.

### Phase 4 Rollback Path

- `git revert` Phase 4 commits in reverse order (T4.6 → T4.1)
- Agent file edits are additive (entries added to `tools:` arrays); revert removes them; C-0445 invariant restored for 28+8 = all 36
- auditing-mcp augmentation revert removes the OP scripts but preserves the underlying skill
- Family-graduation revert restores `family: auditing-cc-configs` and the auditing-cc-configs SKILL.md family list; safe one-way revert
- No live Codespace runtime impact (Phase 5 is what makes the Gate-6 hard-gate fire)

---

## Phase 5 — Rollout: Gate-6 Hard-Gate Wiring + End-to-End Verification + Cleanup

### Goal

Wire the orchestrator Gate-6 phase-validator so that any BLOCKER finding from augmented `auditing-mcp` halts the orchestrator per ADR-0043 (Blueprint Implementation Plan step 9). Execute the end-to-end smoke (fresh Codespace; postCreate; postStart; `claude mcp list`; `auditing-mcp --with-runtime`; cold-cache time check; warm-cache time check). Verify all ACs pass live. Cleanup: working-directory ADR copies + deliverable archive packaging.

### Declared Rollout Posture

**Per ADR-0043: auditing-mcp Gate-6 hard-gate writes as gate-blocking severity. Any BLOCKER finding from `auditing-mcp/scripts/audit_mcp.py --with-runtime` halts the orchestrator at Gate 6 with no operator-bypass; the required remediation path is fix-and-re-run.**

This declaration is consumed by `test-phase-validator-author` (downstream) when authoring the Gate-6 phase validator.

### Scope

- Author the orchestrator Gate-6 phase-validator entry (a script invocation specification + halt-on-non-zero semantics per ADR-0043) — the exact script form is wired by `test-phase-validator-author` downstream; this Plan declares the inputs and the contract
- Run end-to-end smoke on a fresh Codespace
- Verify each Blueprint AC live (cross-reference table at bottom — confirmation pass per the cross-artifact auditor's contract)
- Cleanup: working-directory ADR copies; deliverable archive packaging per `deliverable-archive-spec.md`
- §OI-5 (ADR-0007 content review post-relocation): file as a separate follow-up feature recommendation here, do not author content inside this feature
- §OI-6 event-trigger discipline: do NOT introduce calendar machinery for the design-codespaces Serena 90-day kill criterion (per §O posture). The event trigger is "when auditing-codespaces stub-fill is undertaken." Document the event trigger in the Rollout-completion notes.

### Out of scope (deferred indefinitely)

- CI smoke-test workflow (PRD Won't-Have B-1; future feature)
- Prebuild adoption (§D-5 / Q-CS-2; future feature; event trigger = "if a consuming feature reports rebuild-time complaints")
- Plugin packaging (§D-1 / Q-CC-7; future feature; event trigger = "if a sister project adopts MCP one-command install")
- ADR-0007 content review (§OI-5; recommended follow-up feature, surfaced below)
- Serena v1.3.0 migration (§E-4; future ADR amendment)
- Other `auditing-*` family graduation decisions (per ADR-0042 deferral; meta-feature `auditing-family-structure-review-r1` per `Issues/proposal-auditing-family-graduation-review.md`)

### Prerequisites

- Phases 0–4 complete
- A fresh Codespace available for the end-to-end smoke

### Tasks

#### T5.1: Declare orchestrator Gate-6 phase-validator inputs + hard-gate contract (per ADR-0043)

- **Layer:** Claude Code (orchestrator topology)
- **Description:** Author the contract that `test-phase-validator-author` will consume to wire the Gate-6 phase validator. The contract:
  - **Invocation**: `python .claude/skills/auditing-mcp/scripts/audit_mcp.py --with-runtime --severity-threshold BLOCKER`
  - **Inputs read**: `.mcp.json`, all 36 `.claude/agents/*.md`, `.claude/runtime/mcp-events.jsonl` (latest postStart cycle), `.devcontainer/devcontainer.json`, `.devcontainer/postCreate.sh`, `.devcontainer/postStart.sh`, KB-mcp-platform/SKILL.md, KB-mcp-design/SKILL.md, auditing-mcp/SKILL.md, auditing-cc-configs/SKILL.md, auditing-shared/SKILL.md
  - **Exit semantics**: exit 0 with no BLOCKER findings → orchestrator proceeds past Gate 6; exit non-zero (any BLOCKER finding) → orchestrator halts; operator remediates; re-runs Gate 6; resumes
  - **No operator-bypass**: per ADR-0043 Decision; the gate is hard
  - **Severity model**: BLOCKER is gate-blocking; MAJOR/MINOR are advisory (logged but non-blocking). Per ADR-0043 Decision Details Known Unknowns (a), the severity model is the only adjustment lever; if a rule fires BLOCKER too eagerly, demote at the rule definition.
- **Dependencies:** T4.3 (audit_mcp.py exists), T4.4–T4.6 (graduation complete so the audit-skill itself is internally consistent).
- **Estimate:** S (this is a contract declaration; the validator implementation is downstream `test-phase-validator-author`)
- **Satisfies AC:** AC-CC-5 (hard gate); AC-FR-11-c (runnable end-to-end at Gate 6); AC-NFR-2-c (hard gate at Gate 6).
- **L1 verification:** The contract is documented in this Plan (T5.1 body); cross-reference to ADR-0043 + the auditing-mcp scripts directory; ready for `test-phase-validator-author` consumption.
- **L2 verification:** `test-phase-validator-author` (downstream) authors the validator per this contract; no contract gaps surface during validator-authoring.
- **L3 verification:** Hard-gate semantics confirmed by the seeded-BLOCKER end-to-end test in T5.4: orchestrator halts on BLOCKER; resumes after remediation + re-run.

#### T5.2: End-to-end smoke — fresh Codespace rebuild (cold-cache)

- **Layer:** Codespaces + Claude Code
- **Description:** Open a fresh Codespace from the feature branch. Time the cold-cache build + lifecycle setup. Observe:
  - `devcontainer.json` Features install (Node 20, Go 1.22, common-utils, github-cli, claude-code) — clean
  - `postCreate.sh` runs; sentinels written; binaries on PATH; per-server `install_complete` events written to `mcp-events.jsonl`; AC-CS-9 GitNexus smoke-test passes; AC-CS-3 fail-fast not triggered
  - `postStart.sh` runs; 7 `readiness_probe` records appended to `mcp-events.jsonl`; AC-FR-1-c failure-naming surfaces if any server fails
  - `claude mcp list` returns 7 entries all `connected` (AC-CC-1, AC-FR-1-a)
  - Total cold-cache time measured against NFR-1 ~10 min target (AC-NFR-1-a + AC-CS-8); record number
- **Dependencies:** T1.4 (devcontainer.json), T3.4 (postCreate), T3.5 (postStart), T2.4 (.mcp.json).
- **Estimate:** M (smoke run is bounded; total wall-clock ~10–20 min)
- **Satisfies AC:** AC-FR-1-a, AC-FR-1-b, AC-CC-1, AC-CS-1, AC-CS-3, AC-CS-4, AC-CS-5, AC-CS-7, AC-CS-8, AC-CS-9, AC-CC-6, AC-NFR-1-a, AC-FR-8-a, AC-FR-8-b.
- **L1 verification:** Cold-cache smoke result recorded in `verify-at-execution.md` with wall-clock time + observations.
- **L2 verification:** Each AC above is individually confirmed (pass / fail) in the smoke result table.
- **L3 verification:** All ACs in scope for cold-cache smoke pass.

#### T5.3: End-to-end smoke — warm-cache rebuild

- **Layer:** Codespaces
- **Description:** On the same Codespace, trigger a rebuild (without sentinel deletion). Observe:
  - `postCreate.sh` short-circuits per AC-CS-2 (sentinel + binary present → already-satisfied for all 5 OSS-local servers)
  - Total warm-cache time within ~2 min target (AC-NFR-1-b + AC-CS-8)
  - `postStart.sh` re-runs; 7 fresh `readiness_probe` records (one new postStart cycle) appended to `mcp-events.jsonl`
- **Dependencies:** T5.2.
- **Estimate:** S
- **Satisfies AC:** AC-CS-2 (idempotence); AC-NFR-1-b (warm-cache ≤ ~2 min); AC-FR-8-b (postStart re-runs).
- **L1 verification:** Warm-cache smoke result recorded.
- **L2 verification:** Each AC confirmed pass.
- **L3 verification:** Live observation that warm-cache rebuild ≤ ~2 min wall-clock.

#### T5.4: End-to-end smoke — auditing-mcp + Gate-6 hard-gate

- **Layer:** Claude Code
- **Description:** Run `python .claude/skills/auditing-mcp/scripts/audit_mcp.py --with-runtime` against the live repo state post-T5.3. Observe:
  - Exit 0 with zero BLOCKER findings (AC-CC-5, AC-NFR-2-c)
  - All 10 OP rules report results; OP-6 redaction-integrity confirms no credential-shape strings in the live `mcp-events.jsonl`
  - Family-graduation structural test passes (AC-CC-10)
  - Trifecta consistency (OP-7) passes (AC-FR-11-d)
- Then exercise the hard-gate per ADR-0043:
  - Seed a fake BLOCKER finding (e.g., deliberately introduce a literal credential into a scratch test fixture path within auditing-mcp's monitored scope)
  - Re-run `audit_mcp.py --with-runtime` → exit non-zero
  - Confirm the orchestrator's Gate-6 phase-validator would halt (test-phase-validator-author's downstream validator may or may not be wired yet at this Plan stage; if not, simulate via `audit_mcp.py` exit code as the source of truth)
  - Remove the seeded BLOCKER; re-run → exit 0
- **Dependencies:** T4.3 (audit_mcp.py + 10 OPs), T5.2 (live repo state post-postCreate), T5.3 (warm-cache state + fresh mcp-events.jsonl), T5.1 (contract declared).
- **Estimate:** M
- **Satisfies AC:** AC-FR-11-a, AC-FR-11-b, AC-FR-11-c (runnable end-to-end), AC-CC-5 (zero BLOCKER), AC-CC-8 (trifecta structural), AC-CC-9 (cross-reference), AC-CC-10 (family graduation), AC-FR-11-d, AC-NFR-2-a (no literal credentials), AC-NFR-2-c (hard gate), AC-NFR-2-d (redaction filter active).
- **L1 verification:** `auditing-mcp` exit-code result recorded; seeded-BLOCKER simulation recorded.
- **L2 verification:** Each AC confirmed pass; the seeded-BLOCKER exercise confirms exit non-zero and remediation-then-re-run resumes.
- **L3 verification:** All AC-FR-11-* + AC-CC-* + AC-NFR-2-* ACs pass live.

#### T5.5: End-to-end smoke — failure-mode rehearsals

- **Layer:** Codespaces + Claude Code
- **Description:** Exercise the failure modes that have ACs:
  - **AC-X-1**: Unset `CONTEXT7_API_KEY` in the Codespace secrets surface; trigger postStart; confirm the `mcp-events.jsonl` record carries `result=fail`, `failure_layer=auth`, `message_redacted="missing env-var CONTEXT7_API_KEY"`; confirm stderr banner names the missing env-var
  - **AC-FR-5-b**: Same scenario as above; per-server probe of `context7` fails with "missing credential" failure
  - **AC-FR-1-c**: Deliberately break one server (e.g., shadow `terraform-mcp` binary off PATH); confirm `mcp-events.jsonl` and stderr banner name the specific server + the failure layer
  - **AC-FR-9-a/b/c**: Mid-run server failure → structured failure record appears in `mcp-events.jsonl`; tool-level error response includes server + tool name; healthy→unhealthy transition visible
  - **AC-FR-9-d**: No silent fallback (no `primary_degraded` event fires because no fallback is provisioned in this feature; the schema-level provision is preserved; OP-4 audit rule still finds the prose primary/fallback references)
- **Dependencies:** T5.2, T5.3, T5.4.
- **Estimate:** M
- **Satisfies AC:** AC-X-1, AC-FR-1-c, AC-FR-5-b, AC-FR-9-a, AC-FR-9-b, AC-FR-9-c, AC-FR-9-d, AC-CC-7 (schema-level provision; not exercised in this feature; the OP-4 prose check passes).
- **L1 verification:** Each failure-mode rehearsal recorded in `verify-at-execution.md` with observed output.
- **L2 verification:** Each AC confirmed pass.
- **L3 verification:** Failure-mode contracts exhibited live; restore-clean state after each rehearsal.

#### T5.6: §OI-5 — File ADR-0007 content review as separate follow-up feature recommendation

- **Layer:** Claude Code (housekeeping)
- **Description:** Per Open Items §OI-5 (still open). The Blueprint relocated ADR-0007 from `adrs-migrated/` to `adrs/` (T1.2); the content review of ADR-0007 v2.2.0 is an independent operational item. File a follow-up feature recommendation by appending a row to a Plan-output notes file `working/feature/devcontainer-mcp-provisioning-r1/follow-ups.md` proposing a future feature: `adr-0007-content-review-r1` — review ADR-0007's content correctness post-relocation; not in scope for this feature. Per §O posture, do NOT introduce a calendar trigger; the trigger is "next time ADR-0007 is touched by any feature."
- **Dependencies:** T1.2 (relocation done).
- **Estimate:** XS
- **Satisfies AC:** N/A — setup-housekeeping (closes OI-5).
- **L1 verification:** `working/feature/devcontainer-mcp-provisioning-r1/follow-ups.md` exists with an ADR-0007 review entry.
- **L2 verification:** The follow-up entry names the event trigger (next ADR-0007 touch) per §O.3.
- **L3 verification:** N/A.

#### T5.7: Deliverable archive packaging + cleanup

- **Layer:** Claude Code (housekeeping)
- **Description:** Per `references/deliverable-archive-spec.md`:
  - Archive the working-directory ADR copies (`working/feature/devcontainer-mcp-provisioning-r1/adrs/`) — they were authoring traces; the canonical copies in `/workspaces/feature-pipeline/adrs/` are the source of truth (per ADR-0036)
  - Stamp the deliverable archive with feature slug + version
  - Cross-check: every artifact mentioned in Blueprint §References exists at the canonical path
  - Confirm `verify-at-execution.md`, `follow-ups.md`, and the deferral register `Issues/register-devcontainer-mcp-provisioning-r1-deferrals.md` are all linked from the deliverable archive index
- **Dependencies:** T5.6, all prior Phase 5 tasks.
- **Estimate:** S
- **Satisfies AC:** N/A — setup-housekeeping.
- **L1 verification:** Deliverable archive index exists; cross-references valid.
- **L2 verification:** Manual scan of the archive index confirms completeness.
- **L3 verification:** Next pipeline run that consumes this feature's outputs (e.g., follow-up feature) can find every artifact at its canonical path.

### Phase 5 Exit Criteria

- Orchestrator Gate-6 phase-validator contract declared (T5.1); ready for `test-phase-validator-author` consumption
- Cold-cache + warm-cache smoke completed with measurements (T5.2, T5.3)
- `auditing-mcp --with-runtime` returns zero BLOCKER findings live (T5.4); seeded-BLOCKER hard-gate exercise confirms halt + remediation + re-run + resume cycle
- All failure-mode ACs exercised live (T5.5)
- §OI-5 filed as follow-up feature recommendation (T5.6)
- Deliverable archive packaged (T5.7)
- §OI-6 event-trigger discipline observed: no calendar machinery added; the 90-day kill criterion in ADR-0040 remains in the ADR as design-time documentation; the live event trigger is "when auditing-codespaces stub-fill is undertaken" (event-trigger per §O.3)
- **All Blueprint v3 ACs confirmed pass via the L3 verifications above** (cross-referenced in the AC Cross-Reference table)

Phase Validator: result tables in `verify-at-execution.md` for each smoke; `audit_mcp.py --with-runtime` exit 0; seeded-BLOCKER simulation result recorded; follow-up file + archive index assertions.

### Phase 5 Rollback Path

- This phase is verification + housekeeping; if a critical AC fails in Phase 5, surface as a `critical` cross-artifact issue and route to `finalize-reconciler` which may re-open earlier Phases for fixes
- If the hard-gate fires on a real BLOCKER (not the seeded test), follow the ADR-0043 path: remediate → re-run → resume; this is the designed operator workflow, not a Plan failure
- Deliverable archive is reversible (`git revert` if a packaging error is found)

---

## Cross-Phase Dependencies

The dependency graph below shows hard task-level dependencies. Tasks at the same level can run in parallel; tasks at later levels block until predecessor levels complete.

```
PHASE 0 (Setup — verify-at-execution + bootstrap)
  T0.1 ─┐
  T0.2 ─┤
  T0.3 ─┤
  T0.4 ─┤  (all 7 H-items + 2 D-items + 1 bootstrap)
  T0.5 ─┤  (these are independent — all parallel)
  T0.6 ─┤
  T0.7 ─┤
  T0.8 ─┤
  T0.9 ─┤
  T0.10─┘
        │
        ▼
PHASE 1 (Foundation — ADRs + substrate)
  T1.1 (ADR promotion)
   ├─► T1.2 (supersession + relocation)
   ├─► T1.3 (versions.env)              [needs T0.1, T0.2, T0.3, T0.4 from Phase 0]
   ├─► T1.4 (devcontainer.json edits)   [needs T0.9; benefits from T1.3]
   └─► T1.5 (KB-codebase-research bump)
        │
        ▼
PHASE 2 (Trifecta skills + .mcp.json)
  T2.1 (KB-mcp-platform SKILL.md)
    │ T1.1
    ▼
  T2.2 (KB-mcp-platform references + assets)
    │
    ▼
  T2.3 (KB-mcp-design SKILL.md + 2 refs)
    │ T2.1 (sister cross-ref), T1.1 (ADR-0037)
    ▼
  T2.4 (.mcp.json at repo root)         [needs T2.2 template, T1.3 env names, T0.5 + T0.7 auth surfaces]
        │
        ▼
PHASE 3 (Lifecycle scripts)
  T3.1 (mcp-ping.sh)                    [needs T0.6, T2.3]
  T3.2 (mcp-auth-probe.sh)              [needs T3.1]
  T3.3 (install/terraform-mcp.sh)       [needs T0.1]
  T3.4 (postCreate.sh)                  [needs T1.3, T1.4, T2.4, T3.1, T3.2, T3.3]
  T3.5 (postStart.sh + §D-6)            [needs T2.3, T2.4, T3.1, T3.4, T1.4]
  T3.6 (.gitignore verify)              [needs T0.10, T3.5]
        │
        ▼
PHASE 4 (Agent edits + auditing-mcp + family graduation)
  T4.1 (8 agent allowlists)             [needs T2.4, T0.5]
  T4.2 (28 agent invariant check)       [needs T4.1]
  T4.3 (10 OP scripts)                  [needs T2.4, T3.4, T3.5, T2.1, T2.3, T4.1, T4.2]
  T4.4 (auditing-mcp SKILL.md graduation) [needs T1.1]
  T4.5 (auditing-cc-configs family list update) [needs T1.1]
  T4.6 (auditing-shared + cross-file + singular→plural) [needs T4.4, T4.5]
  T4.7 (OI-4 context-overhead measurement) [needs T2.4, T4.1]
        │
        ▼
PHASE 5 (Rollout + verification + cleanup)
  T5.1 (Gate-6 contract declaration)    [needs T4.3, T4.4, T4.5, T4.6]
  T5.2 (cold-cache smoke)               [needs T1.4, T2.4, T3.4, T3.5]
  T5.3 (warm-cache smoke)               [needs T5.2]
  T5.4 (auditing-mcp + Gate-6 hard-gate exercise) [needs T4.3, T5.2, T5.3, T5.1]
  T5.5 (failure-mode rehearsals)        [needs T5.2, T5.3, T5.4]
  T5.6 (OI-5 follow-up file)            [needs T1.2]
  T5.7 (deliverable archive)            [needs T5.6, all prior Phase-5 tasks]
```

### Critical Path

Phase 0 ⇒ T1.1 ⇒ T2.1 ⇒ T2.2 ⇒ T2.3 ⇒ T2.4 ⇒ T3.1 ⇒ T3.4 ⇒ T3.5 ⇒ T4.3 ⇒ T5.2 ⇒ T5.4 ⇒ T5.7. This is the longest dependency chain; minimizing wall-clock time means parallelizing within each phase.

### Parallelization Opportunities

- **Phase 0**: all 10 tasks are independent — full parallelization (single-developer can serialize; multi-developer can split)
- **Phase 1**: T1.1, T1.3, T1.4, T1.5 can run in parallel after T1.2 (which only depends on T1.1)
- **Phase 2**: T2.1 → T2.2 must serialize; T2.3 can start in parallel with T2.2 (only depends on T2.1 frontmatter for sister cross-ref); T2.4 must wait for T2.2 (template)
- **Phase 3**: T3.1, T3.2 (after T3.1), T3.3 can parallelize; T3.4 + T3.5 serialize after them
- **Phase 4**: T4.1 + T4.2 serialize; T4.3 must wait for all upstream artifacts; T4.4 + T4.5 can parallelize; T4.6 must wait for T4.4 + T4.5; T4.7 can parallelize with T4.3–T4.6
- **Phase 5**: T5.2 → T5.3 → T5.4 → T5.5 serialize (each consumes the live state of the previous); T5.6 + T5.7 are housekeeping at the end

---

## Cross-Cutting Tasks (Security, Observability, Instrumentation)

These concerns are not tied to a single phase but are continuously honored. The Plan does not author new tasks here; instead, it cross-references the per-phase tasks that discharge each concern.

### Security (ADR-0039 redact-at-source posture)

- **No literal credentials in any committed file**: AC-CC-4 + AC-NFR-2-a; enforced by T2.4 (`.mcp.json` env-var indirection only); T4.1 (no credential in agent files); T3.6 (`.gitignore` includes runtime jsonl); T4.3 OP-9 (URL-credential rejection) + OP-10 (argv-leakage rejection)
- **Redaction filter at every write to `mcp-events.jsonl`**: AC-NFR-2-d; enforced by T3.5 (postStart.sh) + T3.4 (postCreate.sh) — each pipes through the env-block + HTTP-headers allowlist from `.mcp.json`; default-fail-closed if allowlist is empty
- **OWASP MCP01 Token Mismanagement (top-ranked MCP risk per C-0333)**: mitigated by ADR-0039 + T4.3 OP-6 audit rule
- **Codespaces secrets surface**: T1.4 `containerEnv` wiring; secrets flow Codespaces secret store → containerEnv → `${VAR}` substitution in `.mcp.json`; never written to any file

### Observability (ADR-0037 mcp-events.jsonl)

- **Event surface canonical home**: `KB-mcp-design/references/principles.md` (authored T2.3) — owns the schema
- **Writers**: T3.4 (postCreate `install_complete` events) + T3.5 (postStart 7 readiness_probe records per cycle) + future feature consumers
- **Schema-level provision for `primary_degraded`**: preserved per T2.3 even though no fallback registered in this feature (per Gate-4 OI-1 closure); the AC-CC-7 schema-level guarantee remains; OP-4 still validates the prose primary/fallback references in `discovery-codebase-researcher.md`
- **Operator surface**: tail command documented in `KB-mcp-platform/references/operator-runbook.md` (T2.2); stderr banner from postStart (T3.5) is the immediate-visibility surface

### Instrumentation (verify-at-execution log + OI-4 measurement)

- **`verify-at-execution.md`**: the Plan's running log for H-1..H-7 + D-2/D-4/D-6 + OI-4 results; lives at `working/feature/devcontainer-mcp-provisioning-r1/verify-at-execution.md`; persisted in the deliverable archive (T5.7)
- **OI-4 context-overhead measurement (T4.7)**: methodology documented; results in `verify-at-execution.md`; gate vs PRD NFR-4 envelope; if breached, plan-author opens downscoping re-scope

---

## L1/L2/L3 Verification Discipline

Every task above carries three verification criteria. The discipline:

- **L1 (cheapest):** Checkable in seconds. File-existence, frontmatter assertions, `bash -n` / `yq` / `jq` parse, `shellcheck`, `python -m py_compile`.
- **L2 (functional):** Checkable in minutes. Unit-style script tests, synthetic-fixture exercises, manual diff spot-checks.
- **L3 (integration):** Checkable in tens of minutes. End-to-end smoke (cold-cache, warm-cache); live `auditing-mcp --with-runtime`; live `claude mcp list`; failure-mode rehearsals; redaction-filter live exercise.

Most L3s in this Plan converge on the Phase 5 smoke (T5.2 through T5.5). Each task's L3 entry above references the specific Phase-5 task that confirms it. This is intentional: live verification is expensive; one well-instrumented smoke discharges most L3s.

Phase Validators (downstream, `test-phase-validator-author`) aggregate the L3s for each phase into a single phase-validator script per phase.

---

## Acceptance Test Cross-Reference

Per Blueprint v3 + KB-documentation-criteria Plan template, every AC maps to at least one task; every task either satisfies at least one AC or is explicitly setup-only.

### Functional ACs

| AC ID | Satisfied by task(s) |
|---|---|
| AC-FR-1-a (7 servers listed connected) | T1.3, T2.4, T3.3, T3.4, T5.2 |
| AC-FR-1-b (per-server probe returns success) | T3.1, T3.2, T5.2 |
| AC-FR-1-c (probe failure surfaces server + layer) | T3.1, T3.5, T5.5 |
| AC-CC-1 (exactly 7 mcpServers, all connected) | T2.4, T5.2 |
| AC-FR-2-a (agent files show MCP entries) | T4.1 |
| AC-FR-2-b (tools callable from agents) | T2.4, T4.1 |
| AC-CC-2 (prescribed entries; no others) | T4.1 |
| AC-CC-3 (28 non-consumer agents zero mcp__) | T4.2 |
| AC-FR-4-a (probe returns success) | T3.1, T3.2, T5.2 |
| AC-FR-4-b (probe failure surfaces server + input + error) | T3.1, T3.2, T5.5 |
| AC-FR-5-a (credentials by env-var name; no committed values) | T1.4, T2.4 |
| AC-FR-5-b (unset credential → clearly named missing-credential failure) | T3.1, T3.2, T5.5 |
| AC-X-1 (env-var absent distinguishable from auth-rejected) | T3.1, T3.2, T3.5, T5.5 |
| AC-CC-4 (zero literal credentials in committed files) | T2.4, T3.6, T4.1 |
| AC-CS-6 (containerEnv resolves env vars from Codespaces secrets) | T1.4 |
| AC-FR-8-a (postCreate consolidated health output) | T3.4, T5.2 |
| AC-FR-8-b (postStart re-runs check) | T3.5, T5.2, T5.3 |
| AC-FR-8-c (postAttach surface; staleness threshold) | T3.5 (§D-6 resolution) |
| AC-FR-8-d (failure surfaces server + layer + remediation hint) | T3.1, T3.5, T2.2 |
| AC-FR-8-e (operator-invokable on demand) | T3.5 (operator-on-demand command via mcp-ping.sh) |
| AC-CS-4 (exactly 7 readiness_probe records per postStart cycle) | T3.5, T5.2 |
| AC-CS-5 (warn-and-continue stderr banner + exit 0 on partial fail) | T3.5, T5.5 |
| AC-CC-6 (7 records with result/failure_layer) | T3.5, T5.2 |
| AC-FR-9-a (mid-run server failure surfaces structured record) | T3.5, T5.5 |
| AC-FR-9-b (tool-level error includes server + tool + error) | T3.1, T5.5 |
| AC-FR-9-c (healthy→unhealthy transition visible) | T3.5, T5.5 |
| AC-FR-9-d (no silent fallback; schema-level provision preserved) | T2.3, T4.3 (OP-4), T5.5 |
| AC-CC-7 (primary_degraded schema-level provision) | T2.3 (KB-mcp-design principles.md) |
| AC-FR-10-a (transport events captured at documented location) | T3.5, T2.2 |
| AC-FR-10-b (structured failure records reconstructable) | T2.3, T3.5 |
| AC-FR-10-c (tail MCP logs command makes per-server content readable) | T2.2 (operator runbook), T3.5 |
| AC-FR-10-d (credential values redacted per ADR-0039) | T3.4, T3.5, T4.3 (OP-6) |
| AC-FR-11-a (KB-mcp-platform exists in trifecta shape) | T2.1, T2.2, T5.4 |
| AC-FR-11-b (KB-mcp-design exists in trifecta shape) | T2.3, T5.4 |
| AC-FR-11-c (auditing-mcp augmented; GitNexus rules; runnable end-to-end; zero BLOCKER) | T4.3, T5.1, T5.4 |
| AC-FR-11-d (cross-reference; both name GitNexus) | T2.1, T2.2, T2.3, T5.4 |
| AC-CC-5 (auditing-mcp 10 OPs zero BLOCKER; hard gate per ADR-0043) | T4.3, T5.1, T5.4 |
| AC-CC-8 (trifecta structural conventions) | T2.1, T2.2, T2.3, T5.4 |
| AC-CC-9 (KB-mcp-platform gitnexus-and-fallback; cites ADR-0007 v2.2.0; preserves primary_degraded schema-level provision) | T2.2, T2.3 |
| AC-CC-10 (family graduation structural complete) | T4.4, T4.5, T4.6, T5.4 |

### Cross-Layer / Operational ACs

| AC ID | Satisfied by task(s) |
|---|---|
| AC-NFR-1-a (cold-cache build ≤ ~10 min) | T1.4, T3.4, T5.2 |
| AC-NFR-1-b (warm-cache rebuild reuses cached layers) | T3.4, T5.3 |
| AC-NFR-2-a (no literal credentials at any commit) | T2.4, T3.6, T4.1, T4.3 (OP-6/9/10) |
| AC-NFR-2-c (auditing-mcp zero BLOCKER at Gate 6; hard gate) | T4.3, T5.1, T5.4 |
| AC-NFR-2-d (redact-at-source filter at every jsonl write; default-fail-closed) | T3.4, T3.5, T4.3 (OP-6) |
| AC-CS-1 (Node 20 + Go on PATH after Feature install) | T0.9, T1.4, T5.2 |
| AC-CS-2 (re-invoking postCreate without sentinel deletion = already-satisfied) | T3.4, T5.3 |
| AC-CS-3 (fail-fast on per-server install failure) | T3.3, T3.4, T5.5 |
| AC-CS-7 (forwardPorts: []) | T1.4 |
| AC-CS-8 (cold-cache ≤ ~10 min; warm-cache ≤ ~2 min) | T3.4, T5.2, T5.3 |
| AC-CS-9 (GitNexus skip-grammars smoke-test fails postCreate on failure) | T0.4, T3.4, T5.2 |
| AC-X-2 (canonical inventory disposition: 7 entries, no fallback) | T2.4, T4.3 (OP-2/OP-3/OP-8) |

### Setup-only tasks (Phase 0; explicit N/A)

| Task | Why setup-only |
|---|---|
| T0.1–T0.7 | §H verify-at-execution items; inform downstream tasks but discharge no AC themselves |
| T0.8 | §D-2 placeholder normalization (project convention; no AC) |
| T0.9 | §D-4 Go pin selection (informs T1.4; no AC standalone) |
| T0.10 | Q-CC-2 `.claude/runtime/` bootstrap (precondition for AC-CC-4 + AC-CC-6; tagged setup because no behavior is shipped yet) |

### Phase 1 housekeeping tasks (explicit AC coverage on each)

T1.1, T1.2, T1.5 — each cited above under specific ACs. T1.3 + T1.4 contribute to multiple ACs (see AC-FR-1-a, AC-CS-1, AC-CS-6, etc.).

### Coverage gaps to surface

No AC orphaned (every AC above is satisfied by at least one task). No task orphaned (every task either satisfies an AC or is explicitly tagged Phase-0 setup or Phase-1/5 housekeeping with rationale).

---

## Risks and Mitigation

Mirrors Blueprint v3 Risks and Mitigation table with task-level mitigation pointers. Per §O event-trigger discipline, rows with calendar-shaped triggers are documented but NOT instrumented with calendar machinery.

| Risk | Layer | Impact | Probability | Mitigation (task pointer) | Event trigger (per §O) |
|---|---|---|---|---|---|
| Cold-cache build sits at upper bound of NFR-1 ~10 min | codespaces | Medium | Medium | T5.2 measures live; if 2× target breach (~20 min) sustained, prebuild adoption opens as follow-up feature | If a consuming feature reports rebuild-time complaints — that is the trigger (per §O.3) |
| GitNexus skip-grammars smoke-test fails on pinned tag (§H-4 HIGH risk) | codespaces | Medium | Medium | T0.4 (Phase 0 smoke-test) catches before any postCreate authoring; AC-CS-9 codifies the runtime fail-fast | Phase 0 task fires it now; no calendar |
| Stdio servers not auto-reconnected (C-0301) | claude-code | High (silent failure) | Low | T3.5 postStart + ADR-0037 event surface make failures operator-visible; T5.5 exercises | postStart cycle on every Codespace attach |
| Credential leak in mcp-events.jsonl despite redaction | claude-code | **CRITICAL** | Low | T4.3 OP-6; T5.4 hard-gate halts; ADR-0039 + AC-NFR-2-d | auditing-mcp on every Gate-6 run |
| ADR-0007 relocation surfaces deferred content questions | claude-code | Low | Low | T5.6 files §OI-5 as follow-up feature | Event trigger: next ADR-0007 touch |
| Per-agent context overhead with 7 always-on servers exceeds tolerable envelope (NFR-4) | claude-code | Medium | Medium-low | T4.7 measures live; if breach, downscoping re-scope opens | T4.7 fires it; no calendar |
| ADR-0040 5-agent Serena allowlist misses an agent that needs Serena | claude-code | Low (additive fix) | Low-medium | T4.3 OP-2 audit + Phase 5 smoke + operator feedback | Event trigger: first observation of "this agent could use Serena" in operator workflow |
| design-codespaces Serena entry sits unused (§OI-6) | claude-code | Low | Medium | T4.1 + T5.7 document the event trigger as "when auditing-codespaces stub-fill is undertaken" (per §O posture; no calendar) | auditing-codespaces stub-fill is the trigger |
| W/H/A trifecta drift over time | claude-code | Medium | Medium | T4.3 OP-7 trifecta-consistency audit; runs at every operator-invocation of auditing-mcp | OP-7 on every audit run |
| Plan-author misses sentinel/binary-persistence edge case | codespaces | Medium | Low | T3.4 implements binary-presence check; T4.3 OP-5 catches sentinel-without-binary | OP-5 on every audit run |
| OI-3 / Q-CC-9 — Gate-6 status | (cross) | Medium | n/a (policy) | T5.1 declares hard-gate contract per ADR-0043; T5.4 exercises | seeded-BLOCKER simulation at Gate 6 |
| auditing-mcp graduation creates orchestrator singular→plural drift | claude-code | Low-medium | Medium | T4.6 (c) sweeps for singular references | T4.6 fires it before Phase 5 |
| Over-broad BLOCKER severity halts orchestrator on low-stakes issues | claude-code | Medium (operator-friction) | Low-medium | T4.3 severity-model documented; demote to MAJOR at rule definition if proven over-eager | Routine review at maintenance windows is the event trigger (when a BLOCKER fires and is contested) |
| Helper scripts (mcp-ping.sh, mcp-auth-probe.sh) JSON-RPC bugs | codespaces | Medium | Low-medium | T3.1 + T3.2 shellcheck + script-level unit tests; T5.4 live exercise | Phase 5 smoke is the trigger |

---

## Deferrals / Follow-ups

Per the orchestrator brief, cross-reference the deferral register `Issues/register-devcontainer-mcp-provisioning-r1-deferrals.md` for context. Items the Plan punts to follow-up features (with event triggers, not calendar):

| Deferred item | Source | Why deferred | Event trigger |
|---|---|---|---|
| §D-1 (Q-CC-7) Plugin packaging | Deferral register §D | Artifacts are plugin-compatible-by-construction (T2.1–T2.3 honor the universal trifecta conventions); no plugin packaging work in this feature | A sister project adopts MCP one-command install |
| §D-5 (Q-CS-2) Prebuild adoption | Deferral register §D | NOT in scope this release; postCreate is not captured by prebuilds anyway | A consuming feature reports rebuild-time complaints |
| §OI-5 ADR-0007 content review post-relocation | Deferral register §A | Independent of relocation mechanics; content unchanged at v2.2.0 | Next feature that touches ADR-0007 — filed by T5.6 |
| §OI-6 design-codespaces Serena entry vs ADR-0033 stub-fill | Deferral register §A | Forward-looking allowlist entry; cost is one line | When auditing-codespaces stub is filled — event trigger per §O posture; no calendar |
| §E-4 Serena v1.3.0 migration | Deferral register §E | Pinned pre-v1.3.0 per ADR-0040 | A future feature that bumps the Serena pin (additive ADR amendment) |
| ADR-0042 follow-up — review other auditing-* siblings | `Issues/proposal-auditing-family-graduation-review.md` | OI-2 closure scope was auditing-mcp only | Meta-feature `auditing-family-structure-review-r1` proposed |
| §B-1 CI smoke-test for `claude mcp list` | PRD Won't-Have | CI/CD layer out-of-scope this feature | A feature explicitly activating the CI/CD layer for MCP drift detection |
| §G-1 Meta-feature `agent-roster-design-discipline-r1` | Saved-for-later memory pointer | User explicitly deferred at prior Gate 4 | Next time user reviews pipeline improvements; auto-memory will surface |

Per Deferral Register §O posture, no calendar machinery is invented. Each deferred item names its event trigger or accepts honest non-tracking.

---

## Estimation Methodology

T-shirt sizes (XS / S / M / L) used throughout. Rough mapping (informational only, not for velocity tracking):

| Size | Rough scope |
|---|---|
| XS | < 30 min — a single small edit, a `.gitignore` line, a verification script run |
| S | 1–3 hours — a small file authored, a single config edit, a verify-at-execution log entry |
| M | half-day — a script with shellcheck-clean discipline, a single agent-edit set, an end-to-end smoke |
| L | a day or more — a skill with multiple reference files, a multi-script audit-rule set, the postCreate.sh full implementation |

Estimates are not load-bearing; the dependency graph is. The size of L tasks (T2.2 KB-mcp-platform references, T2.3 KB-mcp-design body, T3.4 postCreate.sh, T3.5 postStart.sh, T4.3 audit scripts) suggests these are the tasks where splitting could happen if a downstream task-decomposer wants finer-grained units.

---

## Resourcing Posture

This feature is implementable by a single contributor with these capabilities:

- Bash + shellcheck discipline (for `.devcontainer/lib/*` scripts + postCreate / postStart)
- Python 3.11 (for `auditing-mcp/scripts/*.py`)
- Codespaces / devcontainer config (Features block, lifecycle hooks)
- Claude Code project conventions (skills frontmatter, agent files, KB-* references)

Tasks are independent enough that 2–3 contributors could parallelize within phases (per the Parallelization Opportunities section). The L3 verifications converge on a single Codespace smoke (T5.2 onward); this is a serial section.

---

## Open Items (Pending Cross-Artifact Audit)

Items surfaced by the plan-author that the Cross-Artifact Audit should verify against the Blueprint, Tests, and Phase Validators:

- **PA-OI-1**: The Plan declares the orchestrator Gate-6 phase-validator contract (T5.1) but does NOT author the validator script itself — that is `test-phase-validator-author`'s job. The cross-artifact auditor should confirm the downstream validator-author successfully consumes T5.1's contract.
- **PA-OI-2**: §D-6 postAttach staleness threshold is set to 5 minutes (T3.5). This was a plan-author judgment call; the Blueprint deferred the exact number. If the auditor or a future reviewer flags 5 minutes as wrong (too aggressive / too lax), the resolution is to amend T3.5 + the corresponding entry in `KB-mcp-platform/references/lifecycle-hooks.md`.
- **PA-OI-3**: T4.7 (OI-4 context-overhead measurement) discovers the per-agent overhead at implementation time. If it breaches PRD NFR-4, the re-scope path is to introduce conditional activation per server (not currently in scope). The cross-artifact auditor should confirm acceptance tests for NFR-4 (authored by `test-acceptance-author`) are aligned with T4.7's measurement methodology.
- **PA-OI-4**: AC-FR-11-c hard-gate qualifier — Plan adopted option (a) (treat as PRD-inherited; rely on AC-CC-5 + AC-NFR-2-c for the gate semantics). If `review-cross-artifact-auditor` finds this insufficient, option (b) (v3.0.1 patch) remains available; the Plan does not block on this.
- **PA-OI-5**: The Plan does NOT author the auditing-mcp test fixtures (`test-fixtures/` under `auditing-mcp/`). T4.3 mentions them; the actual fixture content (synthetic credential strings, malformed `.mcp.json` examples) is task-level detail that `test-acceptance-author` may author or that the contributor authors during T4.3 task execution. Cross-artifact auditor should flag if test-fixture coverage is unclear after acceptance-test authoring.

---

## Update History

| Version | Date | Author | Change |
|---|---|---|---|
| 1.0.2 | 2026-05-23 | plan-author (dispatch D-3.1, reconciliation cycle 3) | Supply-chain identifier corrections per reconciliation-log-cycle-3.md findings F1 + F2. **F1 (actionlint-mcp upstream rename)**: replaced wrong upstream `2manymws/actionlint-mcp` with corrected `hongkongkiwi/actionlint-mcp`; pinned `ACTIONLINT_MCP_SHA=7441fe042c995cbb1bb4b97fce71f9ed3b36d5ef` (HEAD of main, verified 2026-05-23); dropped non-existent `/cmd/actionlint-mcp` subpath — `main.go` is at repo root on the corrected upstream. Affects T0.2 (description + L2), T1.3 (versions.env entry), T3.4 (postCreate install line). **F2 (GitNexus install-method category error)**: replaced wrong `uvx --from gitnexus@<TAG>` (PyPI/uv form — gitnexus has never been on PyPI) with corrected `npm install -g gitnexus@${GITNEXUS_TAG}` for persistent install and `npx -y gitnexus@${GITNEXUS_TAG} mcp` for one-shot smoke-test; pinned `GITNEXUS_TAG=1.6.5` (npm registry, published 2026-05-16). Affects T0.4 (description), T1.3 (versions.env entry), T2.4 (.mcp.json gitnexus entry: `command:"npx"`, `args:["-y", "gitnexus@${GITNEXUS_TAG}", "mcp"]`), T3.4 (postCreate install + smoke-test). **AC-CS-9 wrapping intent preserved**: AC-CS-9 ("cold-cache build doesn't need a C++ toolchain") remains satisfied because `GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1` is respected by the npm install (suppresses npm-vendored tree-sitter grammar C++ build, the only heavy native step); only install mechanism changes, not the semantic intent. No task IDs renumbered, no AC re-mapped, no DAG restructured, no scope widened. F3 (Context7) is OUT of scope for D-3.1 (handled by D-3.2/D-3.3/D-3.4 after WebFetch investigation). Node-LTS base-image prereq side effect noted in T0.4 / T3.4 but base-image plumbing deferred to D-3.2 (design-composer's domain). |
| 1.0.1 | 2026-05-23 | orchestrator (direct mechanical-edit patch) | Patch-level reconciliation per architecture-audit cycle 2 (I-AA-001 + I-AA-002). Line 673 (T4.1 agent allowlist): `design-cc.md` → `design-claude-code.md` with Path-A note. No task ID changes, no AC re-mapping, no scope change. See reconciliation-log-cycle-2.md. |
| 1.0.0 | 2026-05-23 | plan-author | Initial Plan. Decomposes Blueprint v3 into 6 phases (Phase 0 Setup; Phases 1–4 Feature Delivery by Blueprint cross-layer sequencing; Phase 5 Rollout). 39 tasks total. Wires the 7 §H verify-at-execution items into Phase 0; the 6 ADR-0042 family-graduation tasks into Phase 4 (T4.4 + T4.5 + T4.6 covers steps 1–6); the ADR-0043 Gate-6 hard-gate contract into T5.1; the OI-4 context-overhead measurement into T4.7; the §D-6 postAttach staleness threshold (set to 5 min) into T3.5. MINOR-V3-001 dispositioned via option (a) — AC-FR-11-c treated as PRD-inherited; hard-gate semantics carried by AC-CC-5 + AC-NFR-2-c. §OI-5 filed as follow-up via T5.6. §OI-6 honored per §O event-trigger discipline (no calendar machinery; event trigger = auditing-codespaces stub-fill). |

