---
id: PhaseValidators-devcontainer-mcp-provisioning-r1
version: 1.0.1
status: draft
doc_type: PhaseValidators
feature_slug: devcontainer-mcp-provisioning-r1
derived_from:
  - working/feature/devcontainer-mcp-provisioning-r1/plan-v1.md
  - working/feature/devcontainer-mcp-provisioning-r1/blueprint-v3.md
  - working/feature/devcontainer-mcp-provisioning-r1/prd-v3.md
adrs_referenced:
  - ADR-0037
  - ADR-0039
  - ADR-0040
  - ADR-0041
  - ADR-0042
  - ADR-0043
phases_covered: 6
validators_total: 6
generated: 2026-05-23T00:00:00Z
generated_by: test-phase-validator-author
---

# Phase Validators: Devcontainer MCP Server Provisioning

## Overview

This document specifies the six per-phase validators (PV-0 through PV-5) that gate progression through the Plan v1 phases for `devcontainer-mcp-provisioning-r1`. Each validator operationalizes the corresponding Plan-phase Exit Criteria with scriptable pass criteria, severity rules, and automation hooks. Validators are consumed by humans and CI as Phase gates during execution; they are not verbal — every criterion specifies the concrete command, file path, or grep pattern that proves it.

**PV-5 is the consequential gate.** Per ADR-0043, the Phase 5 / orchestrator Gate-6 validator treats any BLOCKER finding from the augmented `auditing-mcp` skill as gate-blocking severity: the orchestrator halts and no operator-bypass is permitted. The PV-5 specification declares this hard-gate contract verbatim. ADR-0043's verbatim mandate is preserved in PV-5.C-HARDGATE below.

The validators inherit the Blueprint v3 acceptance criteria (AC-FR-*, AC-CC-*, AC-CS-*, AC-NFR-*, AC-X-*) — they verify that phase-scoped ACs hold at the live-state moment of phase completion. The validators do **not** invent new ACs.

## Severity Taxonomy

This document adopts the severity model used by the augmented `auditing-mcp` skill (10 OP rule families) and aligns the per-validator criterion severities to that model. Definitions:

| Severity | Definition | Effect on phase progression |
|---|---|---|
| `BLOCKER` | A failure that violates a load-bearing AC, an architectural invariant (e.g., C-0445 zero-`mcp__` invariant), a security posture (literal credential present, redaction bypassed), or the ADR-0043 hard-gate contract. | **Phase progression halts.** Remediation required; re-run validator; resume. |
| `MAJOR` | A failure that violates a non-load-bearing AC or surfaces operational risk (warm-cache regression, isolated probe failure with bypass path documented). | Surfaces to the operator; requires explicit deferral decision with rationale recorded in `verify-at-execution.md`. |
| `MINOR` | An advisory inconsistency (stale documentation cross-reference, suboptimal but functioning configuration). | Logged; does not block. |
| `NIT` | A style or hygiene observation. | Logged; does not block. |

**Hard-gate semantics for PV-5 (per ADR-0043).** At the Phase 5 / orchestrator Gate-6 invocation of the augmented `auditing-mcp` validator, **any BLOCKER finding** halts the orchestrator. No operator-bypass is permitted at the gate. The required path is: remediate the BLOCKER per the audit report → re-run the validator → orchestrator resumes Gate 6. MAJOR/MINOR/NIT findings at PV-5 remain advisory (logged; non-blocking). This semantic is codified in PV-5.C-HARDGATE; it is non-negotiable per ADR-0043 user-policy decision.

The exit-code convention used by `audit_mcp.py`:
- Exit 0 → no BLOCKER findings → validator passes
- Exit non-zero → at least one BLOCKER finding → validator fails (gate-blocking at PV-5)

---

## Validator: Phase 0 — Setup (Pre-install Verification + Environment Readiness)

### PV-0 Metadata

- **Phase reference**: Plan v1 §Phase 0 — Setup (Pre-install Verification + Environment Readiness)
- **Validator goal**: Prove all 7 verify-at-execution items (§H-1 through §H-7) are recorded with a YES/NO disposition in `working/feature/devcontainer-mcp-provisioning-r1/verify-at-execution.md`, and that the `.claude/runtime/` housekeeping (Q-CC-2) is committed; downstream phases consume stable inputs from these resolutions.
- **Plan-task references**: T0.1–T0.10
- **When run**: After T0.10 completes; before Phase 1 starts.
- **Prerequisites**: Blueprint v3 approved at Gate 4 (already met).
- **Expected duration**: < 1 minute (file-existence and grep assertions only).

### Pass Criteria

| ID | Description | Assertion | Source | Automation hook | Severity |
|---|---|---|---|---|---|
| PV-0.C1 | verify-at-execution.md exists | `test -f working/feature/devcontainer-mcp-provisioning-r1/verify-at-execution.md` exits 0 | Plan T0.1–T0.9 produce this log | Bash test in CI / manual | BLOCKER |
| PV-0.C2 | H-1 (actionlint-mcp commit SHA) recorded | `grep -E '^##+ *H-1' verify-at-execution.md` matches; the section records a 40-char SHA, commit date, subject | T0.2 | grep + regex check | BLOCKER |
| PV-0.C3 | H-2 (Terraform MCP version + SHA256 + GPG fingerprint) recorded | `grep -E '^##+ *H-2' verify-at-execution.md` matches; SHA256 (64-char hex) and GPG fingerprint present | T0.1 | grep + regex check | BLOCKER |
| PV-0.C4 | H-3 (mcp-openapi-schema staleness disposition) recorded with version + staleness annotation | `grep -E '^##+ *H-3' verify-at-execution.md` matches; `STALE_PACKAGE` annotation present OR new version selected | T0.3 | grep | BLOCKER |
| PV-0.C5 | H-4 (GitNexus `GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1` env-var smoke-test) — single HIGH forgetting-risk item — recorded with PASS evidence | `grep -E '^##+ *H-4' verify-at-execution.md` matches; the section shows exit-0 of the smoke command AND no C++ toolchain in process tree | T0.4 (load-bearing for AC-CS-9) | grep + manual evidence check | BLOCKER |
| PV-0.C6 | H-5 (Context7 v3.0.0 tool surface + canonical auth header) recorded | `grep -E '^##+ *H-5' verify-at-execution.md` matches; records the v3.0.0 two-tool surface verified per D-3.2 + D-3.2-completion investigation (`resolve-library-id` AND `query-docs`; npm `@upstash/context7-mcp` `dist-tags.latest` = 3.0.0 published 2026-05-22T16:20Z; tool surface stable across v1→v3 per T-005 v3.0.0); records canonical auth surface `CONTEXT7_API_KEY: <value>` header literal per GitHub README + SF-F3-AUTH-HEADER-1 resolution (NOT `Authorization: Bearer`); the verifier asserts no `ReplaceContentTool` framing remains (`! grep -E 'ReplaceContentTool' verify-at-execution.md` — confirmed contamination from Serena v1.2.0 CHANGELOG, not a Context7 tool at any version) AND no `Authorization: Bearer ${CONTEXT7_API_KEY}` active-use framing remains (`! grep -E 'Authorization.*Bearer.*CONTEXT7_API_KEY' verify-at-execution.md` — historical references describing the prior non-canonical form are permitted) | T0.5 / T-005 v3.0.0 | grep + negative-grep | BLOCKER |
| PV-0.C7 | H-6 (`claude mcp ping` CLI presence disposition) recorded | `grep -E '^##+ *H-6' verify-at-execution.md` matches; records `ping CLI available` OR `ping CLI absent` | T0.6 | grep | BLOCKER |
| PV-0.C8 | H-7 (Exa `--header` flag form support) recorded | `grep -E '^##+ *H-7' verify-at-execution.md` matches; records confirmed auth-flag form | T0.7 | grep | BLOCKER |
| PV-0.C9 | §D-2 placeholder convention recorded (`<PIN_TBD>`) | `grep -E '<PIN_TBD>' verify-at-execution.md` matches; canonical placeholder declared | T0.8 | grep | MAJOR |
| PV-0.C10 | §D-4 Go version pin recorded | `grep -E 'go.*1\.22' verify-at-execution.md` (or selected version) matches | T0.9 | grep | MAJOR |
| PV-0.C11 | `.claude/runtime/.gitkeep` committed | `git ls-files \| grep -E '^\.claude/runtime/\.gitkeep$'` returns the file | T0.10 | git command | BLOCKER |
| PV-0.C12 | `.claude/runtime/mcp-events.jsonl` is gitignored | `git check-ignore .claude/runtime/mcp-events.jsonl` exits 0 and returns the path | T0.10 | git command | BLOCKER |
| PV-0.C13 | No premature edits to Phase 1+ files | `git diff --stat <pre-phase-0-sha>..HEAD -- .mcp.json .devcontainer/versions.env .devcontainer/postCreate.sh .devcontainer/postStart.sh` returns no changes (those are Phase 1+) | Phase 0 is verification-only | git diff | MINOR |

### Operational Checks

- Confirm `.claude/runtime/.gitkeep` is the only new tracked file under `.claude/runtime/` (no accidental commit of a real `mcp-events.jsonl`).
- Confirm `git status` after `echo '{}' > .claude/runtime/mcp-events.jsonl` shows no untracked addition (per T0.10 L2).

### Acceptance Tests Scheduled for This Phase

None — Phase 0 produces no user-visible behavior. AC verification is end-to-end at PV-5 (the verify-at-execution log resolutions inform Phase 1+ task work that satisfies the ACs).

### Failure Response

- BLOCKER failure → Phase 0 incomplete; halt before Phase 1. Re-execute the failing T0.x task; re-run PV-0.
- MAJOR failure → operator decides defer-or-fix; record in `verify-at-execution.md` with rationale.
- Rollback path (per Plan §Phase 0 Rollback): `git revert` the Phase 0 bootstrap commit; delete `verify-at-execution.md`. Zero downstream impact (Phase 0 produces only a log and `.gitkeep` + `.gitignore` entry).

### Automation Hook

A shell script (proposed path: `.claude/scripts/phase-validators/pv-0-setup.sh`) that:
1. Checks file existence of `verify-at-execution.md`.
2. Runs each `grep -E` assertion above; exit non-zero on first BLOCKER miss.
3. Runs `git check-ignore` and `git ls-files` for `.claude/runtime/` checks.
4. Emits a per-criterion PASS/FAIL summary to stdout.

---

## Validator: Phase 1 — Foundation: ADR Promotion + Schema Authoring + Versioning Substrate

### PV-1 Metadata

- **Phase reference**: Plan v1 §Phase 1 — Foundation: ADR Promotion + Schema Authoring + Versioning Substrate
- **Validator goal**: Prove the architectural substrate is staged — 7 newly authored ADRs are in canonical `adrs/` with `status: accepted`, ADR-0018 is superseded, ADR-0007 is relocated, `versions.env` carries 5 pinned entries, `devcontainer.json` Features block carries Node 20 LTS + Go pin + secret indirection + empty `forwardPorts`, and KB-codebase-research / discovery-codebase-researcher cite `schema_version: 1.1.0` and ADR-0038.
- **Plan-task references**: T1.1–T1.5
- **When run**: After T1.5 completes; before Phase 2 starts.
- **Prerequisites**: PV-0 passed.
- **Expected duration**: 1–2 minutes (file-existence, frontmatter parsing, grep assertions, `jq` parse of devcontainer.json, scratch `devcontainer build` validation if available).

### Pass Criteria

| ID | Description | Assertion | Source | Automation hook | Severity |
|---|---|---|---|---|---|
| PV-1.C1 | 7 newly authored ADRs exist in canonical `adrs/` | `ls /workspaces/feature-pipeline/adrs/ADR-{0037,0038,0039,0040,0041,0042,0043}-*.md` lists 7 files | T1.1 | bash glob | BLOCKER |
| PV-1.C2 | Each promoted ADR has `status: accepted` | For each of ADR-0037..0043: `yq '.status' <adr-path>` returns `Accepted` | T1.1 | yq loop | BLOCKER |
| PV-1.C3 | ADR-0038 frontmatter declares `supersedes: ADR-0018` | `yq '.supersedes' adrs/ADR-0038-*.md` contains `ADR-0018` | T1.1 | yq | BLOCKER |
| PV-1.C4 | ADR-0018 body carries supersession marker | `grep -E 'Superseded by ADR-0038' adrs/ADR-0018-*.md` | T1.2 | grep | BLOCKER |
| PV-1.C5 | ADR-0007 in canonical `adrs/` | `ls /workspaces/feature-pipeline/adrs/ADR-0007-*.md` returns a file | T1.2 | bash | BLOCKER |
| PV-1.C6 | No stale cross-references to `adrs-migrated/ADR-0007` | `git grep -E 'adrs-migrated/ADR-0007'` returns no hits | T1.2 | git grep | MAJOR |
| PV-1.C7 | `.devcontainer/versions.env` exists and parses | `test -f .devcontainer/versions.env && bash -n .devcontainer/versions.env` exits 0 | T1.3 | bash | BLOCKER |
| PV-1.C8 | versions.env carries 5 expected keys | `grep -E '^(SERENA_REF\|MCP_OPENAPI_SCHEMA_VERSION\|ACTIONLINT_MCP_SHA\|TERRAFORM_MCP_VERSION\|GITNEXUS_TAG)=' .devcontainer/versions.env` matches 5 lines | T1.3 | grep | BLOCKER |
| PV-1.C9 | versions.env contains no legacy placeholder strings | `! grep -E '<PIN_TAG>\|<TBD-per-ADR-' .devcontainer/versions.env` (no legacy placeholders; only `<PIN_TBD>` or real pins) | T1.3 | grep | BLOCKER |
| PV-1.C10 | devcontainer.json parses + Features block contains Node 20 + Go pin | `jq -e '.features["ghcr.io/devcontainers/features/node:1"].version == "20"' .devcontainer/devcontainer.json` AND `jq -e '.features["ghcr.io/devcontainers/features/go:1"]' .devcontainer/devcontainer.json` both return 0 | T1.4 | jq | BLOCKER |
| PV-1.C11 | devcontainer.json containerEnv carries 3 secret env-var indirections (no literal secrets) | `jq -e '.containerEnv.CONTEXT7_API_KEY == "${localEnv:CONTEXT7_API_KEY}"' .devcontainer/devcontainer.json` (and EXA_API_KEY, TFE_TOKEN) all return 0 | T1.4 | jq | BLOCKER |
| PV-1.C12 | devcontainer.json `forwardPorts` is empty array | `jq -e '.forwardPorts == []' .devcontainer/devcontainer.json` returns 0 | T1.4 | jq | BLOCKER |
| PV-1.C13 | devcontainer.json wires postCreateCommand + postStartCommand to forthcoming scripts | `jq -e '.postCreateCommand == ".devcontainer/postCreate.sh"' .devcontainer/devcontainer.json` AND postStartCommand likewise | T1.4 | jq | BLOCKER |
| PV-1.C14 | No Dockerfile reference modified | `git diff <pre-phase-1-sha>..HEAD -- .devcontainer/Dockerfile` returns no changes | T1.4 (preserves ADR-0041 / E-0081) | git diff | BLOCKER |
| PV-1.C15 | KB-codebase-research SKILL.md cites schema_version 1.1.0 and ADR-0038 | `grep -E 'schema_version:\s*1\.1\.0' .claude/skills/KB-codebase-research/SKILL.md` matches AND `grep -E 'ADR-0038' .claude/skills/KB-codebase-research/SKILL.md` matches; `! grep -E 'schema_version:\s*1\.0\.0' .claude/skills/KB-codebase-research/SKILL.md` | T1.5 | grep | BLOCKER |
| PV-1.C16 | discovery-codebase-researcher cites schema_version 1.1.0 and preserves 4 prose primary/fallback references | `grep -E 'schema_version:\s*1\.1\.0' .claude/agents/discovery-codebase-researcher.md` matches; OP-4 prose preservation pre-check (line-range presence of "primary" and "fallback" prose at lines 3, 20, 29, 156) holds | T1.5 | grep + line-range check | BLOCKER |

### Operational Checks

- `devcontainer build` (or equivalent local validation) runs against the modified `devcontainer.json` without yet requiring the lifecycle scripts (Features-only validation per T1.4 L2). If the local runner is unavailable, defer to PV-2 or PV-5 live verification.
- No Phase 2+ artifact (`.mcp.json`, `KB-mcp-platform/`, `KB-mcp-design/`, lifecycle scripts) has been created — Phase 1 is substrate-only.

### Acceptance Tests Scheduled for This Phase

None directly — Phase 1 satisfies AC preconditions; live AC verification (AC-CS-1 node/go presence; AC-CS-6 / AC-FR-5-a secret indirection) is at PV-5.

### Failure Response

- BLOCKER failure → halt before Phase 2. Re-execute the failing T1.x task; re-run PV-1.
- Rollback path (per Plan §Phase 1 Rollback): `git revert` Phase 1 commits in reverse order; ADR promotion is additive (revert removes the canonical copy, working-dir copies preserved); devcontainer.json revert restores prior Features block; versions.env revert deletes the file. No live Codespace impact until Phase 3 ships postCreate.sh.

### Automation Hook

A shell script (proposed path: `.claude/scripts/phase-validators/pv-1-foundation.sh`) that:
1. Asserts ADR file presence and `status: accepted` via `yq`.
2. Asserts ADR-0018 supersession + ADR-0007 relocation.
3. Parses `.devcontainer/devcontainer.json` with `jq` and asserts each containerEnv indirection + Features block + forwardPorts.
4. Greps versions.env for 5 expected keys and absence of legacy placeholders.
5. Greps KB-codebase-research + discovery-codebase-researcher for schema_version + ADR-0038 citations + 4-line prose preservation.

---

## Validator: Phase 2 — Trifecta Skill Authoring (KB-mcp-platform + KB-mcp-design) + `.mcp.json`

### PV-2 Metadata

- **Phase reference**: Plan v1 §Phase 2 — Trifecta Skill Authoring (KB-mcp-platform + KB-mcp-design) + `.mcp.json`
- **Validator goal**: Prove the trifecta What/How halves are structurally compliant (lowercase-hyphenated names; sister cross-references; What-half has `assets/templates/`; How-half has exactly 2 references + NO `assets/`); the `mcp-events.jsonl` schema is housed in `KB-mcp-design/references/principles.md`; and `.mcp.json` carries exactly 7 named servers (no codebase-memory-mcp fallback per Gate-4 OI-1 closure) with env-var indirection throughout (zero literal credentials; no URL-query credential pattern; no argv credential pattern).
- **Plan-task references**: T2.1–T2.4
- **When run**: After T2.4 completes; before Phase 3 starts.
- **Prerequisites**: PV-1 passed.
- **Expected duration**: 1–2 minutes (file-existence, frontmatter parsing, `jq` queries on `.mcp.json`, grep sweeps for credential patterns).

### Pass Criteria

| ID | Description | Assertion | Source | Automation hook | Severity |
|---|---|---|---|---|---|
| PV-2.C1 | KB-mcp-platform SKILL.md exists with lowercase-hyphenated name | `yq '.name' .claude/skills/KB-mcp-platform/SKILL.md` returns `kb-mcp-platform` | T2.1 / AC-CC-8 | yq | BLOCKER |
| PV-2.C2 | KB-mcp-platform description carries sister cross-reference to KB-mcp-design | `yq '.description' .claude/skills/KB-mcp-platform/SKILL.md \| grep -E 'kb-mcp-design'` matches | T2.1 / AC-CC-8 universal trifecta convention | yq + grep | BLOCKER |
| PV-2.C3 | KB-mcp-platform has `pedagogical_sections:` block with one entry per references file, each justification naming a specific OP-rule or anti-pattern (per D-3 / I-DR-005) | `yq '.pedagogical_sections \| length' .claude/skills/KB-mcp-platform/SKILL.md` ≥ 7; each entry's `justification` contains `OP-[0-9]+` OR `anti-pattern` string | T2.1 + ADR-0030 | yq loop + grep | BLOCKER |
| PV-2.C4 | KB-mcp-platform references include the 7 mandated files | `ls .claude/skills/KB-mcp-platform/references/{gitnexus-and-fallback,seven-named-servers,lifecycle-hooks,credential-handling,mcp-events-jsonl,operator-runbook,troubleshooting}.md` all exist | T2.2 | bash glob | BLOCKER |
| PV-2.C5 | gitnexus-and-fallback.md names GitNexus + cites ADR-0007 + documents primary/fallback prose | `grep -E 'GitNexus' AND 'ADR-0007' AND 'primary' AND 'fallback'` all match | T2.2 / AC-CC-9 + AC-FR-11-d | grep | BLOCKER |
| PV-2.C6 | credential-handling.md cites ADR-0039 | `grep -E 'ADR-0039' .claude/skills/KB-mcp-platform/references/credential-handling.md` matches | T2.2 | grep | BLOCKER |
| PV-2.C7 | `assets/templates/mcp.json.tmpl` exists (What-half convention) | `test -f .claude/skills/KB-mcp-platform/assets/templates/mcp.json.tmpl` exits 0 | T2.2 / AC-CC-8 | bash | BLOCKER |
| PV-2.C8 | KB-mcp-design SKILL.md exists with lowercase-hyphenated name + sister cross-reference | `yq '.name' .claude/skills/KB-mcp-design/SKILL.md` returns `kb-mcp-design`; `yq '.description' ... \| grep -E 'kb-mcp-platform'` matches | T2.3 / AC-CC-8 | yq + grep | BLOCKER |
| PV-2.C9 | KB-mcp-design has exactly 2 references | `ls .claude/skills/KB-mcp-design/references/*.md \| wc -l` returns exactly `2`; files are `patterns-and-anti-patterns.md` + `principles.md` | T2.3 / AC-CC-8 How-half | bash | BLOCKER |
| PV-2.C10 | KB-mcp-design has NO `assets/` directory (How-half convention) | `! test -d .claude/skills/KB-mcp-design/assets` (directory absent) | T2.3 / AC-CC-8 | bash | BLOCKER |
| PV-2.C11 | `mcp-events.jsonl` schema housed in `principles.md` (per ADR-0037) | `grep -E '(readiness_probe\|tool_call_failure\|transport_error\|primary_degraded\|structured_failure)' .claude/skills/KB-mcp-design/references/principles.md` matches all 5 event types | T2.3 / AC-CC-7 / AC-CC-9 / ADR-0037 | grep loop | BLOCKER |
| PV-2.C12 | patterns-and-anti-patterns.md cites URL-embedded credentials + argv-leakage anti-patterns | `grep -E 'URL-embedded' AND 'argv'` both match | T2.3 | grep | BLOCKER |
| PV-2.C13 | `.mcp.json` exists at repo root | `test -f .mcp.json` exits 0 | T2.4 | bash | BLOCKER |
| PV-2.C14 | `.mcp.json` parses as JSON and contains exactly 7 mcpServers | `jq -e '.mcpServers \| keys \| length == 7' .mcp.json` returns 0 | T2.4 / AC-CC-1 / Gate-4 OI-1 closure | jq | BLOCKER |
| PV-2.C15 | `.mcp.json` keys are the 7 expected names | `jq -e '.mcpServers \| keys' .mcp.json` equals `["actionlint-mcp","context7","exa","gitnexus","mcp-openapi-schema","serena","terraform-mcp"]` (alphabetical) | T2.4 / AC-CC-1 | jq | BLOCKER |
| PV-2.C16 | NO `codebase-memory-mcp` entry anywhere in `.mcp.json` | `! jq -e '.mcpServers["codebase-memory-mcp"]' .mcp.json` (absent) | T2.4 / Gate-4 OI-1 closure | jq | BLOCKER |
| PV-2.C17 | context7 uses canonical CONTEXT7_API_KEY header env-var indirection (no URL-query credential) | `jq -e '.mcpServers.context7.headers.CONTEXT7_API_KEY' .mcp.json` returns `"${CONTEXT7_API_KEY}"` (canonical per GitHub README + T-005 v3.0.0 + SF-F3-AUTH-HEADER-1 resolution); `jq '.mcpServers.context7.url' .mcp.json` does NOT contain `apiKey=` or similar | T2.4 / ADR-0039 / OP-9 / SF-F3-AUTH-HEADER-1 | jq + grep | BLOCKER |
| PV-2.C18 | exa uses x-api-key header env-var indirection | `jq -e '.mcpServers.exa.headers["x-api-key"] == "${EXA_API_KEY}"' .mcp.json` returns 0; URL contains no credential param | T2.4 / ADR-0039 | jq | BLOCKER |
| PV-2.C19 | No `--api-key` / `--apikey` argv pattern in any entry's args | `jq -r '.mcpServers[] \| .args // [] \| .[]' .mcp.json \| grep -E -- '--api-?key'` returns no hits | T2.4 / OP-10 | jq + grep | BLOCKER |
| PV-2.C20 | gitnexus entry carries `GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1` env | `jq -e '.mcpServers.gitnexus.env.GITNEXUS_SKIP_OPTIONAL_GRAMMARS == "1"' .mcp.json` returns 0 | T2.4 / AC-CS-9 / AC-FR-11-d | jq | BLOCKER |
| PV-2.C21 | No literal credential-shape strings in `.mcp.json` | `! git grep -E '(AKIA\|ghp_\|sk_live_\|sk_test_\|-----BEGIN.*PRIVATE KEY)' -- .mcp.json` (no real credential shapes) | T2.4 / AC-CC-4 / AC-NFR-2-a | git grep | BLOCKER |

### Operational Checks

- The `.mcp.json` is at repo root (not in `.devcontainer/` or `working/`).
- env-block in `.mcp.json` aligns with the redaction allowlist SSOT per ADR-0039 (env-var names match what `containerEnv` declares in `devcontainer.json` from PV-1).

### Acceptance Tests Scheduled for This Phase

ACs whose verification preconditions are met at this phase but live-tested at PV-5: AC-CC-1 (7 named servers); AC-CC-8 (trifecta structural); AC-CC-9 (cross-reference + primary_degraded schema preserved); AC-FR-11-a/b (trifecta exists); AC-FR-11-d (cross-reference completeness); AC-CC-4 / AC-NFR-2-a (no literal credentials).

### Failure Response

- BLOCKER failure → halt before Phase 3. Re-execute failing T2.x task; re-run PV-2.
- Rollback path (per Plan §Phase 2 Rollback): `git revert` Phase 2 commits in reverse order; skills are additive; `.mcp.json` removal returns Claude Code to "no project-scope MCP servers" (preserves C-0462 prior state). Phase 1 substrate remains intact.

### Automation Hook

A shell script (proposed path: `.claude/scripts/phase-validators/pv-2-trifecta-mcpjson.sh`) that:
1. Parses skill frontmatter with `yq`; asserts names + cross-references + pedagogical_sections.
2. Counts references files for KB-mcp-design (exactly 2) and KB-mcp-platform (≥7).
3. Asserts `! test -d KB-mcp-design/assets` (How-half discipline).
4. Greps `principles.md` for the 5 event types.
5. Runs `jq` on `.mcp.json` for entry count, key set, header indirection, gitnexus env, codebase-memory-mcp absence.
6. Runs `git grep` for credential-shape patterns scoped to `.mcp.json`.

---

## Validator: Phase 3 — Devcontainer Lifecycle Scripts (postCreate, postStart, helper libs)

### PV-3 Metadata

- **Phase reference**: Plan v1 §Phase 3 — Devcontainer Lifecycle Scripts (postCreate, postStart, helper libs)
- **Validator goal**: Prove the 5 lifecycle scripts exist, are `shellcheck`-clean, and pass script-level unit tests for: idempotent sentinel + binary-presence pattern (postCreate); redaction filter active with default-fail-closed posture (postStart); exactly 7 `readiness_probe` records emitted per cycle to `.claude/runtime/mcp-events.jsonl`. The `.gitignore` invariant for `mcp-events.jsonl` is preserved through Phase 1–3 churn. **Live ACs (e.g., AC-CS-9 GitNexus smoke test exit-non-zero) are exercised live at PV-5; PV-3 covers scriptable static + unit-level checks.**
- **Plan-task references**: T3.1–T3.6
- **When run**: After T3.6 completes; before Phase 4 starts.
- **Prerequisites**: PV-2 passed.
- **Expected duration**: 2–4 minutes (shellcheck + bash parse + script-level unit fixtures + grep).

### Pass Criteria

| ID | Description | Assertion | Source | Automation hook | Severity |
|---|---|---|---|---|---|
| PV-3.C1 | 5 lifecycle scripts exist | `test -f .devcontainer/lib/mcp-ping.sh` AND `mcp-auth-probe.sh` AND `install/terraform-mcp.sh` AND `postCreate.sh` AND `postStart.sh` (all 5 exist) | T3.1–T3.5 | bash | BLOCKER |
| PV-3.C2 | All 5 scripts bash-parse-clean | `bash -n` on each returns 0 | T3.1–T3.5 L1 | bash loop | BLOCKER |
| PV-3.C3 | All 5 scripts shellcheck-clean | `shellcheck` exits 0 on each (or only severity ≤ info) | T3.1–T3.5 L1 | shellcheck loop | BLOCKER |
| PV-3.C4 | mcp-ping.sh handles unknown server | `bash .devcontainer/lib/mcp-ping.sh nonexistent-server` returns non-zero with "unknown server" message | T3.1 L2 | bash unit | BLOCKER |
| PV-3.C5 | mcp-auth-probe.sh respects MCP_AUTH_PROBE gate | `MCP_AUTH_PROBE=0 bash .devcontainer/lib/mcp-auth-probe.sh` returns `skipped` for both servers; `MCP_AUTH_PROBE=1` with empty `CONTEXT7_API_KEY=""` returns `failure_layer=auth`, `message_redacted="missing env-var CONTEXT7_API_KEY"` | T3.2 L2 / AC-X-1 / AC-FR-5-b | bash unit | BLOCKER |
| PV-3.C6 | postCreate.sh sentinel-and-binary-presence pattern unit-tested | A script-level unit fixture exercises: (a) both present → skip; (b) sentinel-only → re-install; (c) both absent → install + sentinel-write | T3.4 L2 / AC-CS-2 / OP-5 | unit fixture | BLOCKER |
| PV-3.C7 | postCreate.sh sources versions.env | `grep -E 'source.*versions\.env' .devcontainer/postCreate.sh` matches | T3.4 | grep | BLOCKER |
| PV-3.C8 | postCreate.sh contains AC-CS-3 fail-fast on install failure | `grep -E '(exit 1\|INSTALL FAILED)' .devcontainer/postCreate.sh` matches | T3.4 / AC-CS-3 | grep | BLOCKER |
| PV-3.C9 | postCreate.sh exercises AC-CS-9 GitNexus smoke test | `grep -E 'GITNEXUS_SKIP_OPTIONAL_GRAMMARS' .devcontainer/postCreate.sh` matches AND the smoke-test failure path exits non-zero | T3.4 / AC-CS-9 | grep | BLOCKER |
| PV-3.C10 | postCreate.sh emits AC-FR-8-a health-check summary line | `grep -E 'MCP health' .devcontainer/postCreate.sh` matches | T3.4 / AC-FR-8-a | grep | BLOCKER |
| PV-3.C11 | postStart.sh enumerates 7 servers from `.mcp.json` | `grep -E 'jq.*mcpServers.*keys' .devcontainer/postStart.sh` matches; the loop iterates over all 7 | T3.5 / AC-CS-4 | grep | BLOCKER |
| PV-3.C12 | postStart.sh redaction filter present | Unit fixture: feeding a synthetic credential-shape string through the filter strips it; default-fail-closed behavior verified (empty allowlist → fail) | T3.5 / ADR-0039 / AC-NFR-2-d | unit fixture | BLOCKER |
| PV-3.C13 | postStart.sh emits exactly 7 readiness_probe records per cycle | Unit fixture: stub `mcp-ping.sh` returning pass for all 7; postStart writes exactly 7 JSON objects to a captured file path | T3.5 / AC-CS-4 / AC-CC-6 | unit fixture | BLOCKER |
| PV-3.C14 | postStart.sh emits warn-and-continue stderr banner (AC-CS-5) | Unit fixture: stub `mcp-ping.sh` returning 1-pass-6-fail; postStart's stderr contains `MCP readiness: 6/7 degraded` AND exits 0 (warn-and-continue) | T3.5 / AC-CS-5 | unit fixture | BLOCKER |
| PV-3.C15 | postStart completion within ~15s envelope (unit-level synthetic) | Unit fixture: with 7 ping calls stubbed to ≤2s each, total wall-clock < 15s | T3.5 / AC-CS-8 | unit fixture | MAJOR |
| PV-3.C16 | postAttach staleness threshold = 5 minutes documented | `grep -E '5 ?minutes?\|300' .claude/skills/KB-mcp-platform/references/lifecycle-hooks.md` matches | T3.5 / §D-6 resolution / AC-FR-8-c | grep | MAJOR |
| PV-3.C17 | terraform-mcp.sh exit-non-zero on SHA256 or GPG verify failure (fail-fast) | Unit fixture: corrupt SHA256SUMS → script exits non-zero | T3.3 / AC-CS-3 / ADR-0041 D-0011 | unit fixture | BLOCKER |
| PV-3.C18 | `.gitignore` still ignores `.claude/runtime/mcp-events.jsonl` | `git check-ignore .claude/runtime/mcp-events.jsonl` exits 0 | T3.6 | git | BLOCKER |
| PV-3.C19 | `mcp-events.jsonl` never tracked in history | `git log --all -- .claude/runtime/mcp-events.jsonl` returns no commits | T3.6 / AC-NFR-2-a | git | BLOCKER |
| PV-3.C20 | No credential-shape pattern in working tree (deeper sweep) | `git grep -E '(AKIA[0-9A-Z]{16}\|ghp_[A-Za-z0-9]{36}\|sk_live_[A-Za-z0-9]{24}\|-----BEGIN.*PRIVATE KEY)'` returns no hits | T3.6 / AC-CC-4 | git grep | BLOCKER |

### Operational Checks

- The redaction filter's allowlist SSOT is read from `.mcp.json` env-block + headers — confirm the postStart code reads from `.mcp.json` (not an inline duplicate).
- Synthetic credential test fixtures live under `auditing-mcp/test-fixtures/` (or equivalent) — proposed to be authored alongside PV-3 verification scripts.

### Acceptance Tests Scheduled for This Phase

Live-tested at PV-5 (cold-cache + warm-cache + failure-mode rehearsals): AC-FR-1-a/b/c (server install + probe + failure surfacing), AC-FR-8-a/b/c/d/e (health-check + postStart re-run + postAttach + remediation hint + on-demand invocation), AC-FR-9-a/b/c/d (mid-run failure + tool error + healthy→unhealthy + no silent fallback), AC-FR-10-a/b/c/d (event surface), AC-CS-1/2/3/4/5/7/8/9, AC-CC-6, AC-NFR-1-a/b, AC-NFR-2-d, AC-X-1.

### Failure Response

- BLOCKER failure → halt before Phase 4. Re-execute the failing T3.x task; re-run PV-3.
- Rollback path (per Plan §Phase 3 Rollback): `git revert` Phase 3 commits in reverse order; existing Codespaces continue running; no MCP wiring affected at the agent level (Phase 4 still pending). Re-author can resume cleanly.

### Automation Hook

A shell script (proposed path: `.claude/scripts/phase-validators/pv-3-lifecycle-scripts.sh`) that:
1. Runs `bash -n` and `shellcheck` on each of the 5 scripts.
2. Invokes the script-level unit fixtures for: postCreate sentinel-and-binary cases (skip / re-install / fresh-install); postStart all-pass and partial-fail cases; redaction filter with synthetic credentials; terraform-mcp.sh corrupt-SHA256 case; mcp-auth-probe.sh MCP_AUTH_PROBE gate cases.
3. Runs grep assertions for AC-CS-3 fail-fast presence, AC-CS-9 GitNexus smoke-test invocation, AC-FR-8-a banner.
4. Verifies `.gitignore` discipline via `git check-ignore` and `git log`.
5. Runs `git grep` for credential-shape patterns across the entire working tree.

---

## Validator: Phase 4 — Agent Allowlist Edits + auditing-mcp Augmentation + Family Graduation

### PV-4 Metadata

- **Phase reference**: Plan v1 §Phase 4 — Agent Allowlist Edits + auditing-mcp Augmentation + Family Graduation
- **Validator goal**: Prove (a) 8 of 36 agent files carry the prescribed `mcp__<server>__<tool>` entries per ADR-0040 (and no others); (b) 28 of 36 agent files preserve zero `mcp__` entries (C-0445 invariant); (c) `auditing-mcp/scripts/` carries the 10 OP scripts (OP-1..OP-10) + top-level `audit_mcp.py`, all `py_compile`-clean and exercise-passing against synthetic fixtures; (d) the 6 ADR-0042 family-graduation structural changes are present in `auditing-mcp/SKILL.md`, `auditing-cc-configs/SKILL.md`, `auditing-shared/SKILL.md`, with singular→plural references updated; (e) §OI-4 per-agent context-overhead measurement is recorded in `verify-at-execution.md`.
- **Plan-task references**: T4.1–T4.7
- **When run**: After T4.7 completes; before Phase 5 starts.
- **Prerequisites**: PV-3 passed.
- **Expected duration**: 3–5 minutes (yq frontmatter checks across 36 agents, python compile + fixture exercise on 10 OP scripts, grep sweep).

### Pass Criteria

| ID | Description | Assertion | Source | Automation hook | Severity |
|---|---|---|---|---|---|
| PV-4.C1 | The 8 consumer agents each carry the prescribed `mcp__<server>__<tool>` entries | For each consumer agent (design-api, design-cicd, design-iac, discovery-external-researcher, discovery-codebase-researcher, review-architecture-auditor, design-cc, design-codespaces): `yq '.tools' <agent>` is an array; the prescribed `mcp__<server>__*` entries are present | T4.1 / AC-FR-2-a / AC-CC-2 | yq loop | BLOCKER |
| PV-4.C2 | Consumer agents do NOT carry `mcp__codebase-memory-mcp__*` entries | `! grep -E 'mcp__codebase-memory-mcp' .claude/agents/*.md` (absent anywhere) | T4.1 / Gate-4 OI-1 closure | grep | BLOCKER |
| PV-4.C3 | The 28 non-consumer agents preserve zero `mcp__` entries (C-0445) | Grep sweep: of all `.claude/agents/*.md` NOT in the 8-consumer list, none contain any `mcp__` substring in the frontmatter `tools:` array | T4.2 / AC-CC-3 | grep sweep | BLOCKER |
| PV-4.C4 | Consumer agents' `model:` / `effort:` / `skills:` fields unchanged (cc-design Principle 9) | For each consumer agent: `yq '.model, .effort, .skills' <agent>` equals pre-Phase-4 snapshot (diff comparison) | T4.1 L2 / ADR-0022 Principle 9 | yq + diff | BLOCKER |
| PV-4.C5 | Context7 allowlist names the v3.0.0 two-tool surface per T0.5 verification | `grep -E 'mcp__context7__resolve-library-id' .claude/agents/discovery-external-researcher.md` matches AND `grep -E 'mcp__context7__query-docs' .claude/agents/discovery-external-researcher.md` matches (the two tools stable across v1→v3 per T-005 v2.0.0 F3 and D-3.2 verification); AND `! grep -E 'mcp__context7__ReplaceContent' .claude/agents/discovery-external-researcher.md` (the `ReplaceContentTool` claim was contamination from Serena v1.2.0 CHANGELOG — not a Context7 tool at any version, including v3.0.0) | T4.1 / T0.5 / AC-CC-2 / T-005 v2.0.0 F3 | grep + negative-grep | BLOCKER |
| PV-4.C6 | The 10 OP audit scripts exist in `auditing-mcp/scripts/` | `ls .claude/skills/auditing-mcp/scripts/audit_op{1,2,3,4,5,6,7,8,9,10}_*.py` returns 10 files | T4.3 | bash | BLOCKER |
| PV-4.C7 | Top-level `audit_mcp.py` exists | `test -f .claude/skills/auditing-mcp/scripts/audit_mcp.py` exits 0 | T4.3 | bash | BLOCKER |
| PV-4.C8 | All 11 scripts `py_compile`-clean | For each: `python -m py_compile <script>` exits 0 | T4.3 L1 | python loop | BLOCKER |
| PV-4.C9 | `audit_mcp.py --help` returns usage; supports `--with-runtime` flag | `python audit_mcp.py --help \| grep -E '--with-runtime'` matches | T4.3 / ADR-0043 invocation contract | python | BLOCKER |
| PV-4.C10 | Each OP script exercise-passes against synthetic fixture | For each OP-N: `python audit_op<N>_*.py --fixture <fixture-dir>` exits 0 against a known-passing fixture; exits non-zero against a known-failing fixture | T4.3 L2 | fixture loop | BLOCKER |
| PV-4.C11 | OP-6 redaction-integrity script handles synthetic credentials | `audit_op6_runtime_log_redaction.py` against a fixture mcp-events.jsonl with seeded credential-shape strings returns BLOCKER if not redacted; PASS if redacted; default-fail-closed if allowlist empty | T4.3 / ADR-0039 / OP-6 | fixture | BLOCKER |
| PV-4.C12 | `auditing-mcp/SKILL.md` frontmatter declares `family: auditing-mcp` | `yq '.family' .claude/skills/auditing-mcp/SKILL.md` returns `auditing-mcp` (not `auditing-cc-configs`) | T4.4 / ADR-0042 task 1 / AC-CC-10 | yq | BLOCKER |
| PV-4.C13 | `auditing-mcp/SKILL.md` body carries `## Sub-skill family` section | `grep -E '^## Sub-skill family' .claude/skills/auditing-mcp/SKILL.md` matches | T4.4 / ADR-0042 task 2 / AC-CC-10 | grep | BLOCKER |
| PV-4.C14 | `auditing-mcp/SKILL.md` body cites ADR-0042 graduation rationale | `grep -E 'ADR-0042' .claude/skills/auditing-mcp/SKILL.md` matches | T4.4 | grep | BLOCKER |
| PV-4.C15 | `auditing-cc-configs/SKILL.md` no longer lists `auditing-mcp` in sub-skill family enumeration | In the family-enumeration block (lines ~144–155): `grep -E 'auditing-mcp' <range>` returns no hits as a sub-skill row (but ADR-0042 graduation-rationale reference may be present) | T4.5 / ADR-0042 task 3 / AC-CC-10 | grep + line-range | BLOCKER |
| PV-4.C16 | `auditing-shared/SKILL.md` description lists `auditing-mcp` as graduated-family consumer | `yq '.description' .claude/skills/auditing-shared/SKILL.md \| grep -E 'auditing-mcp'` matches | T4.6 / ADR-0042 task 4 | yq + grep | BLOCKER |
| PV-4.C17 | Singular→plural references updated across `.claude/`, `Issues/`, `working/` | `grep -rE 'the auditing famil(y\|ies)' .claude/ Issues/ working/` returns matches consistent with post-graduation plurality; no stale singular form survives where graduation requires plural | T4.6 / ADR-0042 task 6 | grep sweep | MAJOR |
| PV-4.C18 | Cross-file pair-check coverage preserved or migrated | If `auditing-cc-configs/references/cross-file-checks.md` had MCP-relevant checks, they are migrated to `auditing-mcp/references/` OR an inline rationale documents the migration choice | T4.6 / ADR-0042 task 5 | manual review + grep | MAJOR |
| PV-4.C19 | §OI-4 per-agent context-overhead measurement recorded | `verify-at-execution.md` contains a `## OI-4` section with per-agent overhead numbers + PRD NFR-4 comparison | T4.7 / PRD NFR-4 | grep | BLOCKER |
| PV-4.C20 | OI-4 conclusion: within envelope OR re-scope filed | The OI-4 section in `verify-at-execution.md` records EITHER "within envelope" with measurements OR "re-scope filed" with cross-reference to a user decision | T4.7 / PRD NFR-4 | grep | BLOCKER |

### Operational Checks

- Pre-flight: snapshot of the 8 consumer agents' `model:` / `effort:` / `skills:` fields taken before T4.1 begins (used by PV-4.C4 for diff verification).
- The 10 OP test fixtures (synthetic passing + failing) live under `.claude/skills/auditing-mcp/test-fixtures/` and are committed alongside the OP scripts.

### Acceptance Tests Scheduled for This Phase

ACs whose preconditions are met at this phase but live-tested at PV-5: AC-FR-2-a/b (agent allowlist + invocation); AC-CC-2 (prescribed entries; no others); AC-CC-3 (28-agent invariant); AC-CC-10 (family graduation); AC-FR-11-c (auditing-mcp augmented + runnable end-to-end) — note: full live AC-FR-11-c + AC-CC-5 + AC-NFR-2-c verification is at PV-5 with the hard-gate exercise.

### Failure Response

- BLOCKER failure → halt before Phase 5. Re-execute the failing T4.x task; re-run PV-4.
- Rollback path (per Plan §Phase 4 Rollback): `git revert` Phase 4 commits in reverse order; agent file edits are additive; auditing-mcp augmentation revert removes OP scripts but preserves the underlying skill; family-graduation revert restores `family: auditing-cc-configs`; C-0445 invariant restored across all 36.

### Automation Hook

A shell script (proposed path: `.claude/scripts/phase-validators/pv-4-allowlist-augmentation-graduation.sh`) that:
1. Loops `yq '.tools' <agent>` over all 36 agents; asserts the 8 consumer set has prescribed entries; asserts the 28 non-consumer set has zero `mcp__` entries.
2. Diffs `model:` / `effort:` / `skills:` per consumer agent against the pre-Phase-4 snapshot.
3. Runs `python -m py_compile` over the 11 audit scripts; runs each OP against its synthetic passing + failing fixture.
4. Asserts `yq` frontmatter (auditing-mcp `family:`) + grep for body sections + ADR-0042 references.
5. Greps for singular→plural reference correctness across `.claude/`, `Issues/`, `working/`.
6. Greps `verify-at-execution.md` for the §OI-4 section and a within-envelope OR re-scope marker.

---

## Validator: Phase 5 — Rollout: Gate-6 Hard-Gate Wiring + End-to-End Verification + Cleanup

### PV-5 Metadata

- **Phase reference**: Plan v1 §Phase 5 — Rollout: Gate-6 Hard-Gate Wiring + End-to-End Verification + Cleanup
- **Validator goal**: Prove (a) end-to-end smoke on a fresh Codespace passes with `claude mcp list` returning 7 connected entries and NFR-1 cold-cache (~10 min) + warm-cache (~2 min) targets met; (b) **the augmented `auditing-mcp --with-runtime` returns exit 0 with zero BLOCKER findings against live state, AND a seeded-BLOCKER simulation exercises the hard-gate path per ADR-0043**; (c) failure-mode rehearsals (AC-X-1 missing env-var, AC-FR-1-c broken server, AC-FR-9-a/b/c mid-run failure) all surface the documented structured records; (d) §OI-5 ADR-0007 content-review follow-up is filed; (e) deliverable archive packaged per `deliverable-archive-spec.md`. **This validator is the orchestrator Gate-6 hard gate. Per ADR-0043, any BLOCKER finding halts the orchestrator; no operator-bypass is permitted.**
- **Plan-task references**: T5.1–T5.7
- **When run**: After T5.7 completes; this is the orchestrator Gate-6 step.
- **Prerequisites**: PV-0..PV-4 all passed; fresh Codespace available for live smoke.
- **Expected duration**: 30–60 minutes (cold-cache Codespace rebuild ~10–20 min; warm-cache ~2 min; auditing-mcp run ~1–2 min; seeded-BLOCKER exercise ~5 min; failure-mode rehearsals ~10–15 min).

### Gate-Blocking Declaration (per ADR-0043)

**PV-5.C-HARDGATE — Hard-gate contract (verbatim per ADR-0043 Decision).** Any BLOCKER finding from `python .claude/skills/auditing-mcp/scripts/audit_mcp.py --with-runtime` halts the orchestrator at Gate 6. **No operator-bypass is permitted at the gate.** The required remediation path is: remediate the BLOCKER per the audit report → re-run the validator → orchestrator resumes Gate 6 (operator-resumable per ADR-0043 Decision Details Known Unknowns (b)). MAJOR / MINOR / NIT severity findings are advisory and do not gate.

ADR-0043 user rationale preserved verbatim: *"I agree hard gate. MCPs can cause a lot of problems if they are not stable and the system fails silently or the devcontainer and docker fail."*

This declaration is the single load-bearing semantic of PV-5; it overrides any operator preference at runtime. Implementing scripts MUST emit `exit "$audit_exit_code"` on non-zero per ADR-0043 Implementation Guidance pseudo-code.

### Pass Criteria

| ID | Description | Assertion | Source | Automation hook | Severity |
|---|---|---|---|---|---|
| **PV-5.C-HARDGATE** | **Augmented `auditing-mcp --with-runtime` reports zero BLOCKER findings against live post-Phase-4 state** | `python .claude/skills/auditing-mcp/scripts/audit_mcp.py --with-runtime --severity-threshold BLOCKER` exits 0; the produced report shows 0 BLOCKER findings across OP-1..OP-10 | T5.4 / ADR-0043 / AC-CC-5 / AC-FR-11-c / AC-NFR-2-c | python; orchestrator halts on non-zero per ADR-0043 | **BLOCKER (GATE-BLOCKING)** |
| PV-5.C-HARDGATE-EXERCISE | Seeded-BLOCKER simulation confirms hard-gate halt + remediation + resume cycle | (1) Seed a synthetic BLOCKER (e.g., a fake credential-shape string in a scratch fixture path within auditing-mcp's monitored scope); (2) re-run `audit_mcp.py --with-runtime` → exit non-zero; (3) confirm orchestrator's Gate-6 phase-validator halts; (4) remove seeded BLOCKER; (5) re-run → exit 0; (6) orchestrator resumes | T5.4 / ADR-0043 | manual + python | **BLOCKER (GATE-BLOCKING)** |
| PV-5.C1 | Fresh Codespace cold-cache rebuild — Features install clean | Node 20, Go 1.22, common-utils, github-cli, claude-code Features all install without error | T5.2 / AC-CS-1 | live observation | BLOCKER |
| PV-5.C2 | Cold-cache postCreate.sh completes within ~10 min | Wall-clock time recorded in `verify-at-execution.md`; ≤ NFR-1-a target | T5.2 / AC-NFR-1-a / AC-CS-8 | live timing | BLOCKER |
| PV-5.C3 | Cold-cache: AC-CS-9 GitNexus smoke-test passes | postCreate.sh stdout shows GitNexus smoke-test exit 0; no C++ toolchain invoked | T5.2 / AC-CS-9 | live observation | BLOCKER |
| PV-5.C4 | Cold-cache: `claude mcp list` returns 7 connected entries | `claude mcp list` output contains exactly 7 entries, each with `status: connected` | T5.2 / AC-CC-1 / AC-FR-1-a | live command | BLOCKER |
| PV-5.C5 | Cold-cache: `mcp-events.jsonl` contains 7 readiness_probe + N install_complete records | `jq -s 'group_by(.event_type) \| map({type: .[0].event_type, count: length})' .claude/runtime/mcp-events.jsonl` shows 7 readiness_probe + 5 install_complete | T5.2 / AC-CS-4 / AC-CC-6 | jq | BLOCKER |
| PV-5.C6 | Warm-cache rebuild: postCreate short-circuits per AC-CS-2 | Wall-clock ≤ ~2 min; postCreate stdout shows "already-satisfied" for all 5 OSS-local servers | T5.3 / AC-CS-2 / AC-NFR-1-b / AC-CS-8 | live timing | BLOCKER |
| PV-5.C7 | Warm-cache: postStart re-runs and writes fresh 7 readiness_probe records | The `mcp-events.jsonl` gains exactly 7 new readiness_probe records (latest postStart cycle) | T5.3 / AC-FR-8-b / AC-CS-4 | jq | BLOCKER |
| PV-5.C8 | AC-X-1 failure-mode rehearsal: missing env-var produces distinguishable failure | With `CONTEXT7_API_KEY` unset, postStart-emitted `mcp-events.jsonl` record for `context7` has `result=fail`, `failure_layer=auth`, `message_redacted="missing env-var CONTEXT7_API_KEY"` | T5.5 / AC-X-1 / AC-FR-5-b | live + jq | BLOCKER |
| PV-5.C9 | AC-FR-1-c failure-mode rehearsal: broken server surfaces name + layer | Shadow `terraform-mcp` off PATH; postStart record for `terraform-mcp` has `result=fail`, names the server + failure_layer; stderr banner names the server | T5.5 / AC-FR-1-c / AC-FR-4-a/b | live + jq | BLOCKER |
| PV-5.C10 | AC-FR-9-a/b/c mid-run failure → structured failure record + healthy→unhealthy visible | A deliberately-killed stdio server produces a `structured_failure` (or `tool_call_failure`) record; the next postStart cycle shows healthy→unhealthy transition | T5.5 / AC-FR-9-a/b/c | live + jq | BLOCKER |
| PV-5.C11 | AC-FR-9-d no silent fallback: no `primary_degraded` event fires in this feature | `jq 'select(.event_type == "primary_degraded")' .claude/runtime/mcp-events.jsonl` returns no records (schema-level provision preserved; not exercised) | T5.5 / AC-FR-9-d / AC-CC-9 | jq | BLOCKER |
| PV-5.C12 | AC-FR-10-a/b/c/d event surface live | The `.claude/runtime/mcp-events.jsonl` is at the documented path; each record carries timestamp + structured fields; redaction filter active (no credential-shape strings in any record); operator-tail command (`tail -f .claude/runtime/mcp-events.jsonl`) works | T5.5 / AC-FR-10-a/b/c/d | jq + tail | BLOCKER |
| PV-5.C13 | OP-6 redaction-integrity check: no credential-shape strings in live mcp-events.jsonl | `git grep -E '(AKIA[0-9A-Z]{16}\|ghp_\|sk_live_)' .claude/runtime/mcp-events.jsonl` (or equivalent rg over the live file, since gitignored) returns no hits | T5.4 / AC-NFR-2-a / AC-NFR-2-d / OP-6 | rg | BLOCKER |
| PV-5.C14 | OP-7 trifecta-consistency: KB-mcp-platform ↔ KB-mcp-design cross-references intact live | `audit_op7_trifecta_consistency.py` exits 0 | T5.4 / AC-CC-8 / AC-FR-11-d | python | BLOCKER |
| PV-5.C15 | OP-3 zero-mcp invariant: 28 non-consumer agents preserve invariant live | `audit_op3_zero_mcp_invariant.py` exits 0 | T5.4 / AC-CC-3 / C-0445 | python | BLOCKER |
| PV-5.C16 | Family-graduation structural test passes live | The graduation structural test (per Blueprint Verification §Per-Layer Test Strategy) confirms `auditing-mcp/SKILL.md` family + sub-skill section + `auditing-cc-configs` removal + `auditing-shared` consumer list | T5.4 / AC-CC-10 | structural test | BLOCKER |
| PV-5.C17 | Orchestrator Gate-6 phase-validator contract is declared and consumable | T5.1 contract is recorded in the Plan; this PV-5 specification operationalizes it; the orchestrator's Gate-6 invocation is wired to `audit_mcp.py --with-runtime` with exit-non-zero → halt | T5.1 / ADR-0043 Implementation Guidance | contract + cross-reference | BLOCKER |
| PV-5.C18 | §OI-5 ADR-0007 content-review follow-up filed (no calendar trigger) | `working/feature/devcontainer-mcp-provisioning-r1/follow-ups.md` exists; contains an ADR-0007 review entry naming the event trigger ("next time ADR-0007 is touched") | T5.6 / §OI-5 / §O.3 | grep | MAJOR |
| PV-5.C19 | §OI-6 event-trigger discipline preserved: no calendar machinery introduced | `! grep -rE '(90-day\|quarterly review\|sunset.*by [0-9]{4}-)' working/feature/devcontainer-mcp-provisioning-r1/follow-ups.md` (no time-based triggers) — event triggers only | T5.7 / §OI-6 / §O posture | grep | MAJOR |
| PV-5.C20 | Deliverable archive packaged | The archive index exists per `deliverable-archive-spec.md`; cross-references valid; working-directory ADR copies archived; canonical adrs/ copies preserved as SSOT | T5.7 | manual review | MAJOR |
| PV-5.C21 | NFR per-agent context-overhead within envelope | OI-4 measurement recorded at PV-4 still valid; no breach has surfaced during live smoke | T4.7 / PRD NFR-4 | grep verify-at-execution.md | MAJOR |

### Operational Checks

- **Live state verified**: every PV-5.Cn that names "live" runs against an actual fresh Codespace, not a mock; results recorded in `verify-at-execution.md` with timestamps.
- **Seeded-BLOCKER cleanup**: PV-5.C-HARDGATE-EXERCISE must end with the seeded BLOCKER removed AND `audit_mcp.py --with-runtime` re-confirmed exit 0. Failure to clean up the seed leaves the working tree in a non-shippable state.
- **Restore-clean state after failure-mode rehearsals**: AC-X-1, AC-FR-1-c, AC-FR-9-a/b/c rehearsals each restore the working state before the next runs.

### Acceptance Tests Scheduled for This Phase

The full set of Blueprint v3 ACs (live verification):
- **AC-FR-1-a/b/c**: server install + per-server probe + failure surfacing
- **AC-FR-2-a/b**: 8 agents show MCP tool entries + tools callable
- **AC-FR-4-a/b**: probe returns success + failure surface
- **AC-FR-5-a/b**: env-var indirection + missing-credential failure
- **AC-FR-8-a/b/c/d/e**: postCreate health-check + postStart re-run + postAttach + remediation hint + on-demand invoke
- **AC-FR-9-a/b/c/d**: mid-run failure + tool error + healthy→unhealthy + no silent fallback
- **AC-FR-10-a/b/c/d**: event surface (location + reconstructable + tail + redaction)
- **AC-FR-11-a/b/c/d**: KB-mcp-platform + KB-mcp-design + auditing-mcp augmented + cross-reference completeness
- **AC-CC-1**: 7 named servers in `.mcp.json`
- **AC-CC-2**: prescribed `mcp__*` entries; no others
- **AC-CC-3**: 28-agent zero-mcp invariant
- **AC-CC-4**: no literal credentials anywhere
- **AC-CC-5**: zero BLOCKER findings from auditing-mcp (HARD GATE)
- **AC-CC-6**: 7 records with result/failure_layer per cycle
- **AC-CC-7**: structured_failure schema-level provision (forward-looking)
- **AC-CC-8**: trifecta structural conventions
- **AC-CC-9**: cross-reference + primary_degraded schema preserved
- **AC-CC-10**: family graduation structural
- **AC-CS-1**: Node 20 + Go present after Features
- **AC-CS-2**: idempotence (sentinel + binary)
- **AC-CS-3**: fail-fast on install failure
- **AC-CS-4**: 7 readiness_probe records per cycle
- **AC-CS-5**: warn-and-continue stderr banner
- **AC-CS-6**: secret env-var indirection
- **AC-CS-7**: forwardPorts empty
- **AC-CS-8**: cold ~10 min / warm ~2 min / probe ~15 s envelopes
- **AC-CS-9**: GitNexus skip-grammars smoke-test fails postCreate on failure
- **AC-NFR-1-a/b**: cold-cache + warm-cache time targets
- **AC-NFR-2-a/c/d**: no literal credentials + hard gate + redaction filter
- **AC-X-1**: missing env-var distinguishable
- **AC-X-2**: canonical inventory disposition (7 entries no fallback)

### Failure Response

- **BLOCKER failure on PV-5.C-HARDGATE or PV-5.C-HARDGATE-EXERCISE** → orchestrator halts at Gate 6 (per ADR-0043). Operator remediates BLOCKER per audit report; re-runs `audit_mcp.py --with-runtime`; orchestrator resumes Gate 6 from the resume-point.
- **BLOCKER failure on any other PV-5.Cn** → halt rollout. Re-execute the relevant T5.x task; re-run PV-5.
- **MAJOR failure** → operator decides defer-or-fix; record rationale in `verify-at-execution.md`.
- Rollback path (per Plan §Phase 5 Rollback if invoked): in extremis, `git revert` Phase 5 commits in reverse order — the contract declaration is documentation-only; smoke-test rollback is restoring a clean Codespace; cleanup rollback unstages the archive. Live Codespaces remain operational (no destructive operations).

### Automation Hook

A shell script (proposed path: `.claude/scripts/phase-validators/pv-5-rollout-gate6.sh`) that:
1. **First and load-bearing**: invokes `python .claude/skills/auditing-mcp/scripts/audit_mcp.py --with-runtime --severity-threshold BLOCKER`; on exit non-zero, **exits the validator with the same non-zero code** (per ADR-0043 Implementation Guidance — orchestrator halts).
2. Captures cold-cache and warm-cache wall-clock measurements from `verify-at-execution.md`; asserts they meet NFR-1 envelopes.
3. Parses `.claude/runtime/mcp-events.jsonl` with `jq` to confirm 7 readiness_probe records per cycle + per-record structure.
4. Runs the seeded-BLOCKER hard-gate exercise programmatically: seed → re-run → assert non-zero → cleanup → re-run → assert 0.
5. Runs failure-mode rehearsal verifications (AC-X-1, AC-FR-1-c, AC-FR-9-a/b/c) — these may require manual orchestration of the failure (unset env-var, shadow binary) with the validator confirming the resulting jsonl records.
6. Greps `working/feature/devcontainer-mcp-provisioning-r1/follow-ups.md` for the OI-5 entry; greps for absence of time-based triggers (OI-6 discipline).
7. Validates the deliverable archive index per `deliverable-archive-spec.md`.

**Exit-code contract**: this validator's exit code is the orchestrator's Gate-6 signal. Exit 0 → orchestrator proceeds past Gate 6. Exit non-zero → orchestrator halts. Per ADR-0043, this is non-negotiable.

---

## Cross-validator Concerns

### Validator Dependency Graph

```
PV-0 (Setup)
  └→ PV-1 (Foundation: ADRs + versions.env + devcontainer.json)
        └→ PV-2 (Trifecta + .mcp.json)
              └→ PV-3 (Lifecycle scripts)
                    └→ PV-4 (Agent allowlist + auditing-mcp augmentation + graduation)
                          └→ PV-5 (Rollout: Gate-6 hard gate)
```

Strict linear dependency: PV-N requires PV-(N-1) passed. No phase overlap. This matches the Plan's phase-sequence and the Blueprint §Implementation Plan ordering.

### Critical-Path Validator

**PV-5 is the critical-path validator.** Its failure most delays the feature (orchestrator halt, remediation, re-run). Within PV-5, **PV-5.C-HARDGATE** (the augmented `auditing-mcp --with-runtime` zero-BLOCKER assertion) is the single load-bearing criterion; all other PV-5 criteria are bounded by the audit-skill's own discipline and the live-state verification of ACs that already passed structural/unit checks at PV-2..PV-4.

### Parallelizable Validator Checks (within a phase)

| Phase | Parallelizable criteria |
|---|---|
| PV-1 | C1–C6 (ADR file presence/status/supersession) ∥ C7–C9 (versions.env) ∥ C10–C14 (devcontainer.json) ∥ C15–C16 (KB-codebase-research updates) |
| PV-2 | C1–C7 (KB-mcp-platform) ∥ C8–C12 (KB-mcp-design) ∥ C13–C21 (`.mcp.json`) |
| PV-3 | Per-script lint+parse runs (5 scripts in parallel); unit-fixture runs serially (shared fixture-state risk) |
| PV-4 | OP-1..OP-10 audit-script exercise runs (10 in parallel) ∥ 36-agent yq-tools sweep |
| PV-5 | After cold-cache smoke (serial), the auditing-mcp run + failure-mode rehearsals can interleave; the seeded-BLOCKER exercise MUST be serial w.r.t. the baseline audit run |

### Shared Validator Infrastructure

- **`verify-at-execution.md`**: shared log file under `working/feature/devcontainer-mcp-provisioning-r1/` consumed by PV-0, PV-4 (§OI-4 measurement), PV-5 (smoke measurements + failure-mode rehearsal results).
- **`.claude/runtime/mcp-events.jsonl`**: live event surface (per ADR-0037) consumed by PV-3 (script-level unit fixtures) and PV-5 (live observation). Gitignored; never committed.
- **`.claude/skills/auditing-mcp/test-fixtures/`**: synthetic passing + failing fixtures consumed by PV-4 (OP-N exercise) and PV-5 (seeded-BLOCKER hard-gate exercise).
- **Pre-Phase-4 snapshot of consumer-agent `model:` / `effort:` / `skills:` fields**: taken before T4.1 begins; consumed by PV-4.C4 (Principle 9 invariant).

### Observability Hooks (per ADR-0037)

Every validator that reads or writes lifecycle state interacts with the canonical event surface `mcp-events.jsonl`:

- PV-3 verifies the schema (defined in `KB-mcp-design/references/principles.md`) is honored by postStart's emission code (via script-level unit fixtures).
- PV-5 verifies the event-surface live (location + structure + redaction + tail-command) per AC-FR-10-a/b/c/d.
- The Gate-6 audit (`audit_mcp.py --with-runtime`) reads the latest postStart cycle's records from the same file.

The `mcp-events.jsonl` schema canonical home is `KB-mcp-design/references/principles.md` (per ADR-0037). Any future schema change must update that file first; PV-3 and PV-5 then re-verify.

### Cross-cutting Security Checks (apply across phases)

| Check | Phases enforcing |
|---|---|
| No literal credential in committed files | PV-1.C11 (devcontainer.json indirection), PV-2.C21 (`.mcp.json` grep), PV-3.C20 (working-tree sweep), PV-5.C13 (live mcp-events.jsonl) |
| Redaction filter active + default-fail-closed | PV-3.C12 (script-level unit fixture), PV-4.C11 (OP-6 fixture), PV-5.C13 (live verification per OP-6 + ADR-0039) |
| No URL-query credential pattern (OP-9) | PV-2.C17 (.mcp.json structure), PV-4.C10 (OP-9 fixture), PV-5.C-HARDGATE (live audit) |
| No argv credential pattern (OP-10) | PV-2.C19 (.mcp.json args sweep), PV-4.C10 (OP-10 fixture), PV-5.C-HARDGATE (live audit) |
| C-0445 zero-mcp invariant on 28 non-consumer agents | PV-4.C3, PV-5.C15 (live audit OP-3) |
| ADR-0043 hard-gate semantics | PV-5.C-HARDGATE (the gate itself), PV-5.C-HARDGATE-EXERCISE (the live exercise) |

### Validator Runbook

A human operator triggering, monitoring, and interpreting validator results during a real execution:

1. **Trigger**: at the end of each Plan phase, the operator (or orchestrator) invokes the corresponding `pv-N-*.sh` script.
2. **Monitor**: stdout shows per-criterion PASS/FAIL; failing criteria are tagged with their severity (BLOCKER/MAJOR/MINOR).
3. **Interpret**:
   - All BLOCKER PASS → phase complete; proceed to the next phase.
   - Any BLOCKER FAIL → halt; remediate per the failure's Plan-task reference; re-run the validator.
   - MAJOR FAIL → operator decision: defer (record in `verify-at-execution.md` with rationale) or fix.
   - MINOR/NIT FAIL → log; non-blocking.
4. **PV-5-specific (orchestrator Gate 6)**: the validator's exit code IS the orchestrator's Gate-6 signal. Per ADR-0043, the orchestrator halts on non-zero with no operator-bypass. The operator's only recourse is remediate-and-re-run.

---

## Document History

- **v1.0.0 — 2026-05-23** — Initial authoring by `test-phase-validator-author`. Six validators (PV-0 through PV-5) authored from approved Plan v1, Blueprint v3, PRD v3. PV-5 declares the ADR-0043 hard-gate contract verbatim; PV-5.C-HARDGATE and PV-5.C-HARDGATE-EXERCISE are the gate-blocking criteria; all other PV-5 criteria are BLOCKER but bounded by phase-scoped AC verification. Cross-validator dependency graph is strict linear (no overlap).
- **v1.0.1 — 2026-05-23** — Focused in-place amendment by `test-phase-validator-author` per cycle-3 reconciliation dispatch **D-3.4** (see `reconciliation-log-cycle-3.md`). **Finding F3 (Context7 v3.0.0 re-anchoring)** applied at PV-0.C6 (line 73) and PV-4.C5 (line 307): the v1.2.0/`ReplaceContentTool` framing is removed and replaced with the v3.0.0-verified two-tool surface (`resolve-library-id`, `query-docs`), per D-3.2's investigation consolidated in `research-notes/T-005-context7.md` v2.0.0 (npm `@upstash/context7-mcp` `dist-tags.latest` = 3.0.0 published 2026-05-22T16:20Z; tool surface stable across v1→v3; `ReplaceContentTool` confirmed as contamination from Serena v1.2.0 CHANGELOG, not a Context7 tool at any version). Negative-grep assertions added to prevent regression. Severity rules (BLOCKER) and gate-blocking semantics unchanged. **Out of scope and preserved verbatim**: F1 + F2 (PVs unchanged — install-command-agnostic for actionlint-mcp / gitnexus on AC-CS-9 axis); SF-F3-AUTH-HEADER-1 (`Authorization: Bearer` framing preserved at PV-0.C6, PV-2.C17, PV-5.C8 — deferred to cycle-4 audit per T-005 v2.0.0); ADR-0043 hard-gate declaration in PV-5 (PV-5.C-HARDGATE and PV-5.C-HARDGATE-EXERCISE untouched).

