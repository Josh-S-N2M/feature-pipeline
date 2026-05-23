---
id: ADR-0041
version: 1.0.1
status: Accepted
generated: 2026-05-23
generated_by: design-composer
supersedes: []
adrs_inherited: []
applies_to:
  - devcontainer-mcp-provisioning-r1
  - the .devcontainer/ surface (devcontainer.json features block, postCreate.sh)
  - future MCP server additions that need install paths
template_format: per KB-documentation-criteria ADR template v1.0
change_summary: >-
  Codifies hybrid install-mechanism: devcontainer Features for runtime managers
  (Node 20 LTS, Go); idempotent postCreateCommand script for per-server installs
  with sentinel-file-guarded re-run; binary download with SHA256 + GPG verify
  for Terraform MCP. No Dockerfile changes. Resolves D-0001 per Q-CC-8 ADR
  candidate #5; resolves codespaces I-DR-CS-001 (sentinel naming) and
  I-DR-CS-009 (sentinel/binary persistence).
---

# ADR-0041: Install-mechanism strategy — hybrid Features + idempotent postCreate + verified binary fetch

## Contents

- [x] Status
- [x] Context
- [x] Decision
- [x] Decision Details
- [x] Rationale
- [x] Options Considered
- [x] Consequences
- [x] Architecture Impact
- [x] Implementation Guidance
- [x] Related Information
- [x] Document History

## Status

Accepted — 2026-05-23

## Context

Synthesis D-0001 frames install-path discipline as **architectural, two-way reversible, service blast-radius** (RICE reach=7, impact=3.0). The decision is loaded by the project's Yarn-key Dockerfile failure history (E-0081 / claim verified in codebase-analysis: stale apt-key forced the existing Dockerfile to a fragile workaround) and by the base image's runtime gaps (no Node, no Go, no Docker-in-Docker — constraints #1-4 from synthesis §8).

Per-layer Design surfaced this at Q-CC-8 (synthesis §7 ADR candidate #5). Per FR-5, the composer authors. The candidate is listed as "optional" in the cc dependencies sidecar — "Composer-authored if judged ADR-worthy." The composer's judgment: **YES, ADR-worthy.** The "no new project Dockerfile beyond what already exists" posture is a load-bearing repo-discipline decision that future MCP additions will inherit; codifying it in an ADR prevents re-litigation.

The codespaces-design review surfaced four important issues directly downstream of this decision:
- **I-DR-CS-001 (important):** sentinel naming inconsistency — version-pinned (per Persistence Boundaries) vs unversioned (per postCreate.sh outline). Must be reconciled before plan-author.
- **I-DR-CS-002 (important):** lifecycle-table rationale inconsistency (workspace-mount argument applies only to a subset of installs; full rationale is contingent on prebuild deferral).
- **I-DR-CS-009 (recommended-but-real-failure-mode):** sentinels persist (in /workspaces) but installed binaries don't — sentinel-present + binary-absent state is a real failure mode on rebuild.
- **Q-CS-5 / Q-CS-6:** idempotence mechanism (sentinel) and actionlint-mcp install path (Go feature vs Dockerfile) — both have recommended postures from codespaces-design.

This ADR resolves all five within the install-mechanism decision frame.

## Decision

1. **Hybrid install posture.** Devcontainer Features for runtime managers; postCreateCommand script for per-server installs; no new Dockerfile work.
   - Features (added/modified to `devcontainer.json`):
     - `ghcr.io/devcontainers/features/node:1` with `version: "20"` (LTS major pin per D-0003).
     - `ghcr.io/devcontainers/features/go:1` (new — for actionlint-mcp's `go install`).
   - Features (preserved):
     - `ghcr.io/devcontainers/features/common-utils:2`, `github-cli:1`, `claude-code:1`.
   - Per-server installs in `.devcontainer/postCreate.sh` (NEW) — idempotent, sentinel-guarded, fail-fast on per-server failure.
   - **Per-server install-mechanism taxonomy** (extended at v1.0.1 cycle-3 reconciliation D-3.2 F2 to document the npm/npx path explicitly for GitNexus):

     | Server | Mechanism | Form |
     |---|---|---|
     | Serena | `uvx --from` (Python; uv-managed; ephemeral) | `uvx --from "git+https://github.com/oraios/serena@${SERENA_REF}" serena start-mcp-server` |
     | mcp-openapi-schema | `npx -y` (Node ephemeral via npm cache) | `npx -y "mcp-openapi-schema@${MCP_OPENAPI_SCHEMA_VERSION}" <spec-path>` |
     | actionlint-mcp | `go install` (Go-built binary on PATH) | `go install "github.com/hongkongkiwi/actionlint-mcp@${ACTIONLINT_MCP_SHA}"` (upstream identifier corrected at cycle-3 D-3.2 F1 — was 2manymws/...) |
     | terraform-mcp | binary `wget` + SHA256 + GPG verify | see `.devcontainer/install/terraform-mcp.sh` |
     | **gitnexus** | **`npm install -g` (persistent) + `npx -y` (MCP server invocation in .mcp.json)** | **Persistent install in postCreate.sh: `npm install -g "gitnexus@${GITNEXUS_TAG}"`. MCP server invocation in .mcp.json: `npx -y "gitnexus@${GITNEXUS_TAG}" mcp`. Smoke-test in postCreate.sh: `npx -y "gitnexus@${GITNEXUS_TAG}" --help`. `GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1` MUST be exported before `npm install -g` to suppress npm's vendored tree-sitter grammar build. Added at v1.0.1 per cycle-3 D-3.2 F2 — was `uvx --from gitnexus@<TAG>` which assumed PyPI publication that does not exist (GitNexus is npm-only TypeScript). AC-CS-9 wrapping intent is preserved: the env-var still does the same load-bearing work (no C++ toolchain at cold-cache); only the install mechanism changes from Python (uvx, hypothetical) to Node (npm/npx, real).** |
     | Context7 | no install (remote HTTP) | `https://mcp.context7.com/mcp` via `.mcp.json` `type: http` |
     | Exa | no install (remote HTTP) | `https://mcp.exa.ai/mcp` via `.mcp.json` `type: http` |
   - **Per-server install-mechanism prereqs.** Node-LTS on PATH is now load-bearing for THREE install paths (was two before cycle-3 D-3.2 F2): `mcp-openapi-schema` (`npx`), `gitnexus` (`npm install -g` + `npx`), and the Claude Code session itself. The `node:1@20` Feature provides this; no new base-image dep introduced.
   - Terraform MCP install uses a **binary download + SHA256SUMS + GPG verify** flow against HashiCorp's published key (D-0001 explicit per C-0157 / C-0190 / C-0193).

2. **Sentinel naming = `<server>@<version>.installed`** (resolves I-DR-CS-001 in favor of the version-pinned form from Persistence Boundaries). The unversioned form in the postCreate.sh outline is the bug; the version-pinned form is the canonical convention. When `<version>` is a commit SHA (actionlint-mcp per D-0011), the sentinel name is `<server>@<sha-prefix>.installed` (first 12 chars). Sentinels live under `.claude/runtime/install-sentinels/`.

3. **Sentinel + binary-presence check (resolves I-DR-CS-009).** The postCreate install function for each server SHALL, before honoring the sentinel as proof-of-installed, also verify binary presence (e.g., `command -v actionlint-mcp >/dev/null` for compiled binaries; `uvx --from <pin> <server> --help` smoke-test for uvx-resolved servers). If sentinel-present AND binary-missing, the script treats the state as "sentinel stale" and re-installs, then refreshes the sentinel. This eliminates the failure mode where rebuild loses binaries but preserves sentinels.

4. **Lifecycle placement rationale (resolves I-DR-CS-002).** All seven MCP installs land in `postCreateCommand`. The rationale is: (a) `postCreateCommand` is the only hook that runs after both base-image and Features have provisioned (so Node 20 and Go are available); (b) `postCreateCommand` is idempotent-safe via sentinels; (c) `postCreateCommand` is NOT captured by prebuilds — but per ADR-0041 codified posture, **prebuilds are not adopted in this release** (Q-CS-2 deferred). If prebuilds are later adopted, this ADR may need a follow-up to move the workspace-agnostic subset (uv prime, Go toolchain prime, actionlint-mcp install, Terraform binary fetch) into `onCreateCommand` for prebuild capture.

5. **`auditing-mcp` augmentation rule OP-5 (lifecycle health-check completeness)** validates that `devcontainer.json` `postStartCommand` covers all registered servers per `.mcp.json`. The cross-layer audit gives plan-author a concrete contract.

## Decision Details

| Item | Content |
|---|---|
| Decision | Hybrid Features+postCreate install; no Dockerfile changes; version-pinned sentinels with binary-presence check; Terraform MCP via SHA256+GPG-verified binary. |
| Why now | The "no Dockerfile" posture must be codified before plan-author commits to a postCreate.sh shape. Sentinel-naming and persistence reconciliation (I-DR-CS-001 / I-DR-CS-009) block plan-author. |
| Why this | Honors E-0081 history (avoid Dockerfile baked-everything); uses ghcr Features for the well-known runtimes; uses postCreate for the project-specific installs where idempotence + sentinel-guarded re-run is cheap. Version-pinned sentinels make pin-bump invalidation self-evident; binary-presence check defends against the sentinel-survives-rebuild failure mode. |
| Known unknowns | (a) Whether the `claude mcp ping` primitive exists in the pinned Claude Code Feature version (OI-CS-5 verify-at-execution; D-0008 fallback to direct JSON-RPC). (b) Whether cold-cache build time at ~7-12 min (codespaces estimate) stays under the NFR-1 ~10 min target across operator workloads — monitored post-ship; if it slips, prebuild adoption (Q-CS-2) is the natural follow-up. (c) Whether the Go Feature should pin a specific Go version (I-DR-CS-007 recommendation) — the composer's call: defer to plan-author; the Go feature-default is acceptable per constraint #2 (any Go available). |
| Kill criteria | If the cold-cache build routinely exceeds 2× NFR-1 target (~20 min), descope: drop a server, change the install path, or adopt prebuilds. PRD Rollout Plan codifies this as a kill criterion already; this ADR composes with that. |

## Rationale

Synthesis D-0001 recommended `hybrid_features_plus_postcreate` and explicitly rejected three alternatives (Dockerfile-bake, features-only, postCreate-for-everything). The composer agrees and adopts. Resolving the four codespaces review issues within the same ADR is efficient and gives plan-author a single contract for install-mechanism choices.

The version-pinned-sentinel + binary-presence-check posture is the only one that survives the synthesis principles: sentinel-presence MUST imply installation-ready (else the audit at OP-5 is vacuous). The simpler "no sentinel, unconditional re-run" alternative loses the NFR-1 warm-cache budget; the simpler "unversioned sentinel" alternative leaks the pin-bump bug (I-DR-CS-001 evidence).

## Options Considered

### Option 1: Hybrid Features + idempotent postCreate + verified binary fetch (selected)

**Pros:** Reuses well-known Features where they exist; keeps per-server complexity in postCreate where idempotence is natural; no Dockerfile churn; Terraform's GPG-verify path is supply-chain safety.

**Cons:** PostCreate isn't captured by prebuilds; cold-cache builds re-do MCP installs. Mitigated by the warm-cache sentinel short-circuit + the fact that prebuilds are deferred.

### Option 2: Dockerfile-bake everything

**Pros:** All installs cached in image layers.

**Cons:** Re-litigates the E-0081 stale-apt-key burnt history; mixed package managers inflate Dockerfile complexity; pin-bumps force a Dockerfile rebuild path that the team has demonstrated fragility on.

### Option 3: Features-only

**Pros:** Declarative.

**Cons:** No upstream Features exist for 6 of 7 MCP servers; authoring + maintaining 7 Feature repos is grossly disproportionate.

### Option 4: postCreate-for-everything (including runtimes)

**Pros:** Single mechanism.

**Cons:** Re-invents what `ghcr.io/devcontainers/features/node` and `/go` provide; loses ghcr versioning; adds postCreate runtime.

## Consequences

### Positive Consequences

- Avoids re-litigation of the E-0081 Dockerfile failure history.
- Per-server install logic is co-located in one idempotent script; pin changes touch one file (`.devcontainer/versions.env`).
- Sentinel-naming + binary-presence-check eliminates the I-DR-CS-009 rebuild failure mode.
- Terraform MCP's supply-chain safety is explicit (SHA256+GPG verify is hard to skip if codified in the install script).
- The augmented `auditing-mcp` rule OP-5 can audit lifecycle completeness against `.mcp.json` as a single static check.

### Negative Consequences

- Cold-cache builds incur the per-server install time (synthesis estimate ~2-4 min for postCreate). Mitigated by warm-cache sentinel short-circuit; not mitigated by prebuilds (deferred).
- Plan-author must sequence the Go Feature add + the actionlint-mcp install (the install runs `go install` which depends on Go being available — Feature order matters).
- The Terraform MCP install script (`.devcontainer/install/terraform-mcp.sh`) is non-trivial code-surface; the GPG verify is security-critical and must be reviewed at plan-author/code time.

### Neutral Consequences

- The base image (`mcr.microsoft.com/devcontainers/python:1-3.11-bookworm`) is preserved; constraint #1 honored.
- The fail-fast posture in postCreate (synthesis 9.2: "fail postCreate if smoke-test fails") aligns with AC-FR-1-c and AC-CS-3.

## Architecture Impact

1. **Layers affected.** Dev Environment / Codespaces (owns devcontainer.json, postCreate.sh, install/terraform-mcp.sh); Claude Code / Project Filesystem (the augmented `auditing-mcp` rule OP-5 validates the lifecycle).
2. **Components that change.**
   - `.devcontainer/devcontainer.json` — features block additions (Node 20 LTS pin; Go).
   - `.devcontainer/postCreate.sh` (NEW) — idempotent install with version-pinned sentinels + binary-presence check.
   - `.devcontainer/install/terraform-mcp.sh` (NEW) — wget + SHA256SUMS + GPG verify (HashiCorp public key) → install to PATH.
   - `.devcontainer/versions.env` (NEW) — per-server pin table (SERENA_TAG, OPENAPI_SCHEMA_VERSION, ACTIONLINT_MCP_SHA, TERRAFORM_MCP_VERSION, GITNEXUS_TAG).
   - `.devcontainer/lib/mcp-ping.sh` + `mcp-auth-probe.sh` (NEW) — probe helper scripts called from postStart.sh (resolves I-DR-CS-005).
   - `auditing-mcp` augmentation rule OP-5 (lifecycle completeness) — validates devcontainer.json against .mcp.json.
3. **New dependencies introduced.** Go Feature; Node 20 LTS pin (was `lts` floating); HashiCorp GPG key (downloaded at install time, not baked).
4. **Architectural constraints added.** No new project Dockerfile work. Sentinel naming convention is `<server>@<version>.installed`. Binary-presence check is required before honoring any sentinel.

## Implementation Guidance

**Sentinel canonical form:**
```
.claude/runtime/install-sentinels/<server>@<version>.installed
```
Where `<version>` is the value of the corresponding pin variable in `.devcontainer/versions.env` (e.g., `serena@v1.2.5.installed`, `actionlint-mcp@a3b9c8d12345.installed` for a commit SHA prefix).

**Binary-presence check (illustrative; plan-author refines):**

```bash
# Pseudo-code; real script lives in postCreate.sh
check_installed() {
  local server="$1"
  local version="$2"
  local sentinel="$SENTINEL_DIR/${server}@${version}.installed"
  [[ -f "$sentinel" ]] || return 1                # no sentinel: not installed
  # Sentinel-present: also verify binary is reachable
  case "$server" in
    serena)            uvx --from "git+https://github.com/oraios/serena@${version}" --help >/dev/null 2>&1 ;;
    actionlint-mcp)    command -v actionlint-mcp >/dev/null 2>&1 ;;
    terraform-mcp)     command -v terraform-mcp >/dev/null 2>&1 ;;
    gitnexus)          GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1 npx -y "gitnexus@${version}" --help >/dev/null 2>&1 ;;   # install-mechanism corrected at v1.0.1 cycle-3 D-3.2 F2 (was uvx; GitNexus is npm-only)
    # ... etc
  esac
}
```

If `check_installed` returns 0, skip install. If sentinel-present but binary-absent (return 1 from the binary check), delete sentinel + re-install + refresh sentinel.

**Helper-script contracts (resolves I-DR-CS-005).** `.devcontainer/lib/mcp-ping.sh <server> <transport>` returns 0 on probe pass, non-zero on probe fail. `.devcontainer/lib/mcp-auth-probe.sh <server> <tool>` returns the probe outcome plus appends a `readiness_probe` record to `mcp-events.jsonl` (per ADR-0037 schema). Both scripts are project-local; plan-author writes them; this ADR fixes the contract shape.

**Terraform MCP supply-chain:**
1. `wget` the release archive from `releases.hashicorp.com/...` (URL pattern per HashiCorp public docs).
2. `wget` the SHA256SUMS file and the GPG signature.
3. `gpg --verify SHA256SUMS.sig SHA256SUMS` against the HashiCorp public key (key download is a one-time cost; key fingerprint is committed in install script for verification).
4. `sha256sum -c SHA256SUMS --ignore-missing` on the release archive.
5. Extract and install to a `$PATH` location.
Any failure → exit non-zero → postCreate fail-fast (AC-CS-3).

**Go Feature version:** the composer's call: defer specific Go version pin to plan-author (I-DR-CS-007 marked as recommended, not blocking). The Go Feature default is acceptable for `go install <repo>@<sha>` of a single binary (actionlint-mcp).

**No procedural detail.** Step-by-step sequencing of feature additions, script authoring, and audit-rule activation lives in the Plan.

## Related Information

- Related ADRs: ADR-0037 (mcp-events.jsonl event surface — written by postStart, install-surfaced separately by postCreate), ADR-0039 (credential redaction — postCreate.sh must not surface credentials; install commands use `${VAR}` env-references), ADR-0040 (Serena posture — SERENA_TAG pin lives in `versions.env`).
- Referenced specs / docs: synthesis.md §3 D-0001, §3 D-0004, §3 D-0011, §4 per-server matrix, §7 ADR candidate #5; codespaces-design.md (Base Mechanism, Tools Installation Strategy, Lifecycle-Hook Placement Table, postCreate.sh outline, Persistence Boundaries); cc-design.md (the .mcp.json reads what postCreate installs).
- Issues / PRs: I-DR-CS-001 (sentinel naming — resolved here), I-DR-CS-002 (lifecycle-table rationale — resolved here in Decision item 4), I-DR-CS-005 (helper-script contracts — resolved here in Implementation Guidance), I-DR-CS-006 (terraform-mcp.sh ownership — resolved here in Architecture Impact / Implementation Guidance), I-DR-CS-009 (sentinel/binary persistence — resolved here in Decision item 3).
- Related KBs: KB-codespaces-design (hybrid install-mechanism Principle 6), KB-codespaces-platform (devcontainer.json schema, lifecycle hooks), KB-mcp-platform/`install-mechanisms.md` (per-server install paths).

## Document History

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2026-05-23 | 1.0.0 | Initial ADR-0041. Hybrid install posture (Features + idempotent postCreate + verified binary fetch); sentinel naming `<server>@<version>.installed`; binary-presence check; resolves Q-CS-5, Q-CS-6, I-DR-CS-001, I-DR-CS-002, I-DR-CS-005, I-DR-CS-006, I-DR-CS-009. | design-composer |
| 2026-05-23 | 1.0.1 | **Cycle-3 reconciliation (D-3.2 F2).** Extended the Decision item 1 install-mechanism documentation to include an explicit **per-server install-mechanism taxonomy table** with a dedicated row for the GitNexus npm/npx install path (was implicit via prior text references to `uvx` form, which was a category error — GitNexus is npm-only TypeScript, not Python/PyPI). The taxonomy table now documents seven rows (one per MCP server) and one additional Node-LTS-on-PATH prereq row. Updated the `check_installed` example for `gitnexus` from `uvx --from "gitnexus@${version}"` to `npx -y "gitnexus@${version}"` with `GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1` env-var exported. **AC-CS-9 wrapping intent preserved across the mechanism change**: the env-var continues to do the same load-bearing work (suppresses npm's vendored tree-sitter grammar build under the corrected npm path, was claimed to suppress a Python C-extension build that never actually existed under the previous uvx framing); the verify-at-execution check (T0.4) — assert no `cc`/`g++`/`cargo` in the install-process tree — remains install-command-agnostic. **F1 corrections also propagated** to the taxonomy table's actionlint-mcp row (`hongkongkiwi/actionlint-mcp`, no `/cmd/...` subpath). No Status change (still Accepted); no Decision item retracted; v1.0.0 content preserved verbatim per ADR-0005 append-only discipline. | design-composer (focused multi-artifact amendment per cycle-3 dispatch D-3.2) |
