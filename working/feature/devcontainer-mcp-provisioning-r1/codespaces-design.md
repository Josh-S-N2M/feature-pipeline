---
id: codespaces-design-devcontainer-mcp-provisioning-r1
doc_type: per_layer_design_subsection
layer: codespaces
version: 1.0.1
status: draft
feature_slug: devcontainer-mcp-provisioning-r1
derived_from: working/feature/devcontainer-mcp-provisioning-r1/prd-v3.md
synthesis_source: working/feature/devcontainer-mcp-provisioning-r1/synthesis.md
codebase_analysis: working/feature/devcontainer-mcp-provisioning-r1/codebase-analysis.json
generated: 2026-05-23T00:00:00Z
generated_by: design-codespaces
---

# Codespaces Design — devcontainer-mcp-provisioning-r1

This is the per-layer Codespaces / Dev Environment subsection of the Blueprint, authored per Per-Layer Design discipline (KB-codespaces-design + KB-codespaces-platform). It owns the `.devcontainer/` surface: features, lifecycle hooks, Codespaces secrets wiring, install scripts, and the postStart readiness probe. The composer integrates this with the design-cc artifacts (`.mcp.json`, `KB-mcp-*`, `auditing-mcp` augmentation, `mcp-events.jsonl` schema).

## Layer Responsibility Scope

The Codespaces layer owns, for this feature:

- `.devcontainer/devcontainer.json` — features block updates (Go added; Node pinned), `containerEnv` wiring for three Codespaces secrets, `postCreateCommand` and `postStartCommand` declarations.
- `.devcontainer/Dockerfile` — **NO CHANGES** per synthesis D-0001 (hybrid posture; constraint #13 historical fragility).
- `.devcontainer/postCreate.sh` (NEW) — idempotent install + first-run verify script for the seven MCP servers.
- `.devcontainer/postStart.sh` (NEW) — readiness probe (MCP JSON-RPC `ping`) writing `readiness_probe` records to `.claude/runtime/mcp-events.jsonl`.
- Per-server install commands (six of seven; Context7 + Exa have no install — remote HTTP).
- GitNexus skip-grammars smoke-test at install time (partially-verified per synthesis Critic batch 1 → C-0388/C-0411).

The Codespaces layer does NOT own:

- `.mcp.json` — design-cc owns (consumes secrets the codespace exposes; reads them by env-var name).
- The mcp-events.jsonl schema — design-cc owns (KB-mcp-design `principles.md`).
- The redaction allowlist code-site — design-composer reconciles (env-var SSOT is cc-owned; the boundary where the filter runs is a cross-layer call).
- Agent allowlist edits, KB-mcp-* authoring, auditing-mcp augmentation — design-cc owns.

## Base Mechanism

**Image-based with Features layered.** Current base is `mcr.microsoft.com/devcontainers/python:1-3.11-bookworm` (per codebase-analysis-report and Dockerfile line 2). This base is retained — synthesis D-0001 rejects `dockerfile_bake_everything` (constraint #13 Yarn-key history E-0081) and synthesis recommendation 9.2 explicitly says "No new project Dockerfile work."

Rationale (per KB-codespaces-design Principle 6 — Features for known tools; Dockerfile for unknowns): runtime managers (Node, Go) are well-known and have first-party Features; the seven MCP servers are project-specific installers and belong in a lifecycle script, not a Dockerfile layer (which would force rebuild on every server change). The hybrid posture honors synthesis constraints #1, #2, #4, #13.

## Tools Installation Strategy

Three-tier strategy per synthesis D-0001 + D-0003 + Principle 6:

| Tier | Mechanism | Used for |
|---|---|---|
| Runtime managers | Devcontainer Features (ghcr.io/...) | Node LTS (D-0003), Go (constraint #2), github-cli (existing), claude-code (existing) |
| OS utilities | Existing Dockerfile RUN (no change) | ripgrep, jq, bat, tree, less |
| MCP servers | `postCreateCommand` idempotent script | The six install-required servers (Context7 and Exa are remote-HTTP, no install) |

### Features block changes (devcontainer.json)

**Add:**

- `ghcr.io/devcontainers/features/go:1` — Go toolchain for `actionlint-mcp` `go install` (constraint #2; actionlint-mcp has no tagged releases per C-0133, so `go install <repo>@<commit-sha>` is the only deterministic path). **Cycle-3 D-3.2 F1 note:** the upstream identifier is `hongkongkiwi/actionlint-mcp` (was `2manymws/actionlint-mcp` — repo 404; corrected); main.go at repo root, so install path drops the `/cmd/actionlint-mcp` subpath.

**Modify:**

- `ghcr.io/devcontainers/features/node:1` — change `version: "lts"` → `version: "20"` to satisfy synthesis D-0003 ("explicit Node LTS major pin"). Node 20 is the current LTS major as of execution date. **Cycle-3 D-3.2 F2 note:** Node-LTS-on-PATH is now load-bearing for the **GitNexus install path** as well — F2 corrected the GitNexus install mechanism from `uvx`-based (Python; PyPI 404) to `npm install -g gitnexus@${GITNEXUS_TAG}` / `npx -y gitnexus@${GITNEXUS_TAG} mcp`. The Node 20 Feature was already present for `npx mcp-openapi-schema` and the Claude Code session itself; the GitNexus install is now a third consumer. No new base-image dep introduced — the Node Feature is reused.

**Preserve (no change):**

- `ghcr.io/devcontainers/features/common-utils:2` (major-pinned).
- `ghcr.io/devcontainers/features/github-cli:1` (preserve current `version: "latest"`; not in scope to repin in this feature).
- `ghcr.io/anthropics/devcontainer-features/claude-code:1` (major-pinned; required for `claude mcp list` acceptance gate).

**Not adopted:**

- No NodeSource apt approach (D-0003 `dockerfile_apt_nodesource` rejected; constraint #13).
- No `nvm` (D-0003 `nvm_postcreate` rejected — single LTS, not multi-version).
- No Docker-in-Docker feature (constraint #3; Terraform MCP must use pre-built binary, not Docker per C-0193).

## Lifecycle-Hook Placement Table

Per synthesis D-0004 (`layered_postcreate_install_poststart_probe`) and KB-codespaces-design Principle 1.

| Hook | Used | Setup task | Captured by prebuilds? | Justification |
|---|---|---|---|---|
| `initializeCommand` | NO | — | n/a | No host-side pre-flight required. |
| `onCreateCommand` | KEEP EXISTING | `claude --version && python3 --version && node --version && gh --version` | YES | Tool-presence verification; existing one-shot. Already runs before workspace mount — too early for stdio MCP installs that may reference repo paths (per synthesis D-0004 "too early for stdio servers needing project mount"). |
| `updateContentCommand` | NO | — | (Yes) | No content-dependent dependency-install task in scope. The seven MCP installs are project-config-dependent (read `.mcp.json` paths), not lockfile-dependent — they belong in `postCreate` per D-0004. |
| `postCreateCommand` | **NEW** | Run `.devcontainer/postCreate.sh` — idempotent install + first-run verify for the seven servers | NO | One-shot install at create time. Idempotent (sentinel-file guarded per Q-CS-5) so re-runs on rebuild are safe. Not captured by prebuilds, but that is correct: the install touches `.claude/runtime/` (in workspace) and writes per-rebuild verification output. The runtime managers (Node, Go) ARE captured by prebuilds because they live in Features. |
| `postStartCommand` | **NEW** | Run `.devcontainer/postStart.sh` — readiness probe (MCP JSON-RPC `ping`) for the seven servers; append `readiness_probe` records to `.claude/runtime/mcp-events.jsonl` | n/a | Every start (creation, resume, rebuild) needs a fresh readiness check. HTTP servers (Context7, Exa) may have changed availability while stopped; stdio servers need to confirm Claude Code can spawn them. Time budget ~2s (7 pings + 2 optional auth-probes). |
| `postAttachCommand` | NO | — | n/a | Synthesis D-0004 leaves this unused. KB-codespaces-design Principle 1: long-running setup in postAttach is an anti-pattern (runs every terminal attach). Operator-on-demand health-check (AC-FR-8-e) is satisfied by a documented script invocation, not by tying it to attach. |

**Anti-pattern explicitly avoided** (per KB-codespaces-design): the seven MCP installs are NOT placed in `postStartCommand`. Per synthesis D-0004 `single_poststart_only` rejection — "conflates two failure modes; risks masking install-time failures when postStart re-run silently passes."

### postCreate.sh outline

```bash
#!/usr/bin/env bash
# .devcontainer/postCreate.sh
# Idempotent install of the seven MCP servers. Re-run-safe via sentinel files
# under .claude/runtime/install-sentinels/<server>.installed.
set -euo pipefail

SENTINEL_DIR=".claude/runtime/install-sentinels"
mkdir -p "$SENTINEL_DIR"

# Tier 1: uv (Astral) — required for Serena uvx invocation (C-0005)
if ! command -v uv >/dev/null 2>&1; then
  pip install --user uv
fi
which uv  # smoke-test (synthesis 9.3 verification)

# Tier 2: per-server installs (only Serena, mcp-openapi-schema, actionlint-mcp,
# terraform-mcp, gitnexus need install steps; Context7 and Exa are remote-HTTP).

install_serena()           { uvx --from "git+https://github.com/oraios/serena@${SERENA_TAG}" --help >/dev/null; }
install_openapi_schema()   { npx -y "mcp-openapi-schema@${OPENAPI_SCHEMA_VERSION}" --help >/dev/null || true; }
install_actionlint_mcp()   { go install "github.com/hongkongkiwi/actionlint-mcp@${ACTIONLINT_MCP_SHA}"; }   # upstream identifier corrected at cycle-3 reconciliation D-3.2 F1; main.go at repo root, no /cmd/... subpath
install_terraform_mcp()    {
  # wget pre-built binary → sha256sum -c → GPG verify → place on PATH
  # (HashiCorp public key; synthesis C-0157/C-0190/C-0193)
  bash .devcontainer/install/terraform-mcp.sh "${TERRAFORM_MCP_VERSION}"
}
install_gitnexus()         {
  # Smoke-test required: confirm GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1 works on
  # pinned tag (synthesis C-0388/C-0411 partially_verified-medium).
  # Install-mechanism corrected at cycle-3 reconciliation D-3.2 F2 (was uvx —
  # GitNexus is npm-only TypeScript, not PyPI). Persistent install via
  # npm install -g; ephemeral smoke-test via npx. The env-var is exported
  # BEFORE npm install runs and suppresses npm's vendored tree-sitter
  # grammar build → no C++ toolchain at cold-cache (AC-CS-9 wrapping intent
  # preserved across mechanism change). Prereq: Node.js LTS on PATH (provided
  # by node:1@20 Feature; verified by AC-CS-1).
  export GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1
  npm install -g "gitnexus@${GITNEXUS_TAG}"
  npx -y "gitnexus@${GITNEXUS_TAG}" --help >/dev/null
}

for server in serena openapi_schema actionlint_mcp terraform_mcp gitnexus; do
  sentinel="$SENTINEL_DIR/${server}.installed"
  if [[ -f "$sentinel" ]]; then
    echo "[postCreate] ${server}: already installed (sentinel present)"
    continue
  fi
  if "install_${server}"; then
    touch "$sentinel"
    echo "[postCreate] ${server}: installed OK"
  else
    echo "[postCreate] ${server}: FAILED — see above" >&2
    exit 1   # fail postCreate fast; operator sees the failing server immediately
  fi
done

# Tier 3: first-run verify (one-shot ping all seven via Claude Code's MCP host).
# Reuse the same primitive postStart.sh uses; failure is non-fatal here because
# postStart will re-probe on first start and produce the AC-FR-1-c surface.
.devcontainer/postStart.sh --first-run || true

echo "[postCreate] complete"
```

Notes:

- Pinned versions (`SERENA_TAG`, `OPENAPI_SCHEMA_VERSION`, `ACTIONLINT_MCP_SHA`, `TERRAFORM_MCP_VERSION`, `GITNEXUS_TAG`) live in `.devcontainer/versions.env` (single file, sourced by the script). This is the per-server pin table from synthesis D-0011.
- The script is **fail-fast** on install failure (per synthesis 9.2: "fail postCreate if smoke-test fails"). The operator sees the specific failing server in the postCreate output (AC-FR-1-c surface).
- Sentinel-file idempotence is the recommended baseline per Q-CS-5. Alternative (no-sentinel re-run on every rebuild) is recorded in Q-CS-5 for composer arbitration.

### postStart.sh outline

```bash
#!/usr/bin/env bash
# .devcontainer/postStart.sh
# Fast readiness probe (MCP JSON-RPC ping) for the seven servers.
# Appends one record per server to .claude/runtime/mcp-events.jsonl.
set -uo pipefail   # NOT -e: probe failures are recorded, not fatal (see Q-CS-3)

EVENTS_FILE=".claude/runtime/mcp-events.jsonl"
mkdir -p "$(dirname "$EVENTS_FILE")"

# Servers and their transports (single source of truth for the probe; mirrors .mcp.json)
declare -A SERVERS=(
  [serena]=stdio
  [mcp-openapi-schema]=stdio
  [actionlint-mcp]=stdio
  [terraform-mcp]=stdio
  [gitnexus]=stdio
  [context7]=http
  [exa]=http
)

degraded_count=0
for server in "${!SERVERS[@]}"; do
  transport="${SERVERS[$server]}"
  # JSON-RPC ping primitive (MCP spec, C-0290 verbatim Anthropic).
  # Implementation invokes `claude mcp ping <server>` if available (Q-CS-7),
  # else falls back to direct JSON-RPC over the transport.
  start_ns=$(date +%s%N)
  if probe_result=$(.devcontainer/lib/mcp-ping.sh "$server" "$transport" 2>&1); then
    result="pass"
  else
    result="fail"
    degraded_count=$((degraded_count + 1))
  fi
  latency_ms=$(( ($(date +%s%N) - start_ns) / 1000000 ))

  # Append readiness_probe event (schema owned by KB-mcp-design; see Q-CS-8).
  jq -nc \
    --arg ts "$(date -u +%Y-%m-%dT%H:%M:%SZ)" \
    --arg server "$server" \
    --arg probe_method "ping" \
    --argjson latency_ms "$latency_ms" \
    --arg result "$result" \
    '{ts:$ts, event:"readiness_probe", server:$server, probe_method:$probe_method, latency_ms:$latency_ms, result:$result}' \
    >> "$EVENTS_FILE"
done

# Optional authenticated probes (Context7, Exa) gated on MCP_AUTH_PROBE=1
# to respect API quotas (synthesis D-0008).
if [[ "${MCP_AUTH_PROBE:-0}" == "1" ]]; then
  .devcontainer/lib/mcp-auth-probe.sh context7 resolve-library-id  >> "$EVENTS_FILE" || true
  .devcontainer/lib/mcp-auth-probe.sh exa       web_search_exa     >> "$EVENTS_FILE" || true
fi

# Stderr banner (operator-visible per AC-FR-8-a).
if (( degraded_count > 0 )); then
  echo "[postStart] MCP readiness: ${degraded_count}/7 server(s) degraded — see ${EVENTS_FILE}" >&2
else
  echo "[postStart] MCP readiness: 7/7 healthy"
fi

# Exit 0 always (warn-and-continue per Q-CS-3 recommendation).
exit 0
```

Notes:

- The script writes structured JSONL the operator (and future tooling) can parse. The event-shape (`readiness_probe` record fields) is owned by design-cc and documented in `KB-mcp-design/references/principles.md` — this script consumes that contract.
- **Warn-and-continue** is the recommended posture per Q-CS-3: failing postStart on a degraded probe would block every Codespace start every time any HTTP server has a transient blip. AC-FR-8-d requires the failure be surfaced; it does NOT require the lifecycle hook to fail. The structured record + stderr banner satisfy AC-FR-8-a + AC-FR-8-d.
- Time budget per synthesis 9.2: ~2s for 7 pings + 2 optional auth-probes.

## Prebuild Strategy

**Decision: prebuilds NOT adopted in this release. Default cold build only.**

Rationale (per KB-codespaces-design Principle 2):

1. The expensive work is in Features (Node, Go) which the base image + Features cache reasonably across rebuilds. Synthesis 9.2 explicitly notes prebuild contents would cache `go install`, uvx cache for Serena, and npm cache for mcp-openapi-schema — but these caches are not currently load-bearing on the NFR-1 cold-cache budget (~10 min target).
2. Prebuilds DON'T capture `postCreateCommand` (the seven MCP installs land there per D-0004) — so the perceived win of prebuild for "MCP server readiness on attach" is structurally unavailable.
3. The PRD's NFR-1 envelope is bounded by cold-cache (~10 min) and warm-cache (~2 min); the design-codespaces estimate (see §"Rebuild-time estimate" below) fits within both.
4. Adding prebuilds would consume separate org compute budget and require branch-coverage decisions that are out of scope for this release.

Surfaced as Q-CS-2 for composer arbitration if cold-start time becomes a felt constraint post-ship.

## Persistence Boundaries

Per KB-codespaces-design Principle 3:

| Path | Persistence | Purpose |
|---|---|---|
| `/workspaces/<repo>/` | Survives rebuild | Source tree (default mount). |
| `/workspaces/<repo>/.claude/runtime/mcp-events.jsonl` | Survives rebuild | The durable runtime log surface (FR-10). Lives in workspace so log history is not lost on rebuild. |
| `/workspaces/<repo>/.claude/runtime/install-sentinels/` | Survives rebuild | Idempotence sentinels (Q-CS-5 recommended posture). On rebuild, the sentinels survive, so re-run of postCreate is a no-op unless a sentinel is deleted (operator-driven rebuild). **Note:** if version pins change, the install script must invalidate stale sentinels (encoded as `<server>@<version>.installed`). |
| `~/.cache/uv/`, `~/go/`, `~/.npm/` | Ephemeral on rebuild | Tool caches outside `/workspaces`. Lost on rebuild — re-populated by Features + postCreate. Acceptable: Features re-prime caches; postCreate is idempotent. |
| Installed binaries on `$PATH` (`actionlint-mcp`, `terraform-mcp`, `uv`, `serena` via uvx) | Ephemeral on rebuild | Re-installed by postCreate. The sentinel files + version pins ensure deterministic re-install. |

**Anti-pattern explicitly avoided**: storing the MCP install binaries under `/workspaces/.bin/` to survive rebuild. Synthesis D-0001 keeps install in `postCreateCommand` (re-run on rebuild); putting binaries in `/workspaces` would invert the cleanliness of the workspace tree and create rebuild non-determinism if the operator hand-edited a binary.

## Machine Class

**Default: existing `hostRequirements` (4 cpus / 8gb / 32gb) — no change.**

Per KB-codespaces-design Principle 4: the project is markdown-dominant (73.8% per synthesis constraint #8), running Python audit scripts + Claude Code session + at most 6 stdio MCP server processes concurrently. The MCP server processes are mostly idle (started-on-demand by Claude Code) and lightweight. Existing 4-core / 8GB is appropriate; no upgrade required for the seven-server surface.

Override mechanism: per-user override available via the Codespaces UI; project default stays in `devcontainer.json`. Honors KB-codespaces-design Principle 4 ("Don't over-provision 'to be safe.'").

## Secrets and Config

Per KB-codespaces-design Principle 5 + synthesis constraint #9 + AC-NFR-2-a/-b.

### Codespaces Secrets (operator-provisioned, repo-scope or user-scope)

| Env var | Required by | Synthesis source |
|---|---|---|
| `CONTEXT7_API_KEY` | Context7 remote HTTP MCP (`CONTEXT7_API_KEY` header) | T-005, C-0208 |
| `EXA_API_KEY` | Exa remote HTTP MCP (`x-api-key` header) | T-006, C-0284 |
| `TFE_TOKEN` | Terraform MCP — OPTIONAL (only required for Terraform Cloud/Enterprise; local-only operation works unauthenticated) | T-004, NFR-2-a |

### Wiring (devcontainer.json `containerEnv`)

```jsonc
"containerEnv": {
  "EDITOR": "code --wait",
  "PAGER": "less -R",
  "CONTEXT7_API_KEY": "${localEnv:CONTEXT7_API_KEY}",
  "EXA_API_KEY":      "${localEnv:EXA_API_KEY}",
  "TFE_TOKEN":        "${localEnv:TFE_TOKEN}"
}
```

The `${localEnv:NAME}` form pulls from the Codespace's host env (which the Codespaces secrets store populates) and injects into the container env. `.mcp.json` references these env vars by name (`${CONTEXT7_API_KEY}`, etc.) — design-cc owns that side of the wiring.

**Codespaces vs runArgs:** `containerEnv` is preferred over `runArgs: ["--env", "..."]` because `containerEnv` is the idiomatic devcontainer-spec field; `runArgs` is Codespaces-host-implementation-specific and harder to audit. Surfaced as Q-CS-4 if the composer wants to revisit.

### Non-secret config (in repo)

- Version pins (`SERENA_TAG`, `OPENAPI_SCHEMA_VERSION`, etc.) in `.devcontainer/versions.env`. Non-secret; tracked in git.
- Feature pin overrides in `devcontainer.json`. Non-secret; tracked in git.

### Anti-patterns explicitly avoided (AC-NFR-2-a/-b, AC-FR-5-a)

- No `.env` file committed.
- No secret value in `devcontainer.json`, `Dockerfile`, `postCreate.sh`, `postStart.sh`, or `versions.env`.
- No `--header "x-api-key: <literal>"` form in the install scripts.
- Exa's URL-query-param `exaApiKey` form is **rejected at .mcp.json validation time** (design-cc enforces; constraint #10 / synthesis D-0007 E-0095) — the codespaces layer cooperates by never constructing a URL with embedded credential in postCreate/postStart.

### Fallback when a secret is absent

- Context7 / Exa: per AC-FR-5-b, the affected server's probe shall fail with a clearly-named "missing credential" failure. `.devcontainer/postStart.sh` ping will fail; the structured `readiness_probe` event records `result=fail` with the server name. design-cc's `.mcp.json` should produce a clearer "missing CONTEXT7_API_KEY" message at session start (design-cc concern).
- `TFE_TOKEN` absent: Terraform MCP runs in local-only mode (no Terraform Cloud features). Acceptable degradation; not a probe failure.

## Port Forwarding

**No ports forwarded** (consistent with current `"forwardPorts": []`).

The seven MCP servers communicate over stdio (5) or remote HTTPS (2). None listens on a local TCP port the operator or browser needs to reach. KB-codespaces-design Principle 7 requires explicit declaration: `forwardPorts: []` and an empty `portsAttributes` declare that intent.

If a future MCP server adopts a local-HTTP transport (e.g., a future Terraform MCP HTTP mode), the Designer at that time adds a `forwardPorts` entry with `visibility: "private"` (default). Out of scope here.

## Multi-Container Topology

**Single-container. No docker-compose.**

The seven servers run as stdio child processes spawned by Claude Code (5) or as remote HTTPS endpoints (2). There is no local DB, queue, or sidecar to host. Adding docker-compose would inflate startup time without benefit (KB-codespaces-design anti-pattern: "Multi-container compose for a service the developer doesn't run locally").

## Dotfiles Support

No change from current state. The repo neither encourages nor restricts dotfiles. The seven-server install is in `postCreate.sh` (runs after the dotfiles install hook if any), so dotfiles cannot break MCP install ordering.

## Monorepo Positioning

Not applicable. The project has a single `.devcontainer/` at the root; no per-component containers.

## Idle Timeout and Retention

No change from defaults. Synthesis does not call for an override.

## Org-Level Policy Alignment

Project base image (`mcr.microsoft.com/devcontainers/python`) is org-allowed (already in use). Adding the Go Feature is consistent with existing Features. No org policy interaction beyond what already exists.

## Acceptance Criteria Contribution (EARS)

The Codespaces layer contributes these acceptance criteria to the Blueprint's AC section. All use EARS form.

- **AC-CS-1 (Features present):** When the Codespace finishes its Feature install, the system shall have Node 20 (LTS major) and Go (any feature-default version) on PATH; `node --version` shall return a `v20.*` string and `go version` shall return a non-error response.
- **AC-CS-2 (postCreate idempotence):** If `.devcontainer/postCreate.sh` is invoked a second time on the same Codespace without intervening sentinel deletion, then the system shall observe each per-server install as already-satisfied (sentinel present) and shall complete in well under the cold-cache time of the first run (sentinel short-circuit).
- **AC-CS-3 (postCreate fail-fast):** If any per-server install step fails inside `postCreate.sh`, then the system shall surface the failing server name on the operator's terminal and shall exit non-zero, halting the lifecycle.
- **AC-CS-4 (postStart probe):** When the `postStartCommand` runs, the system shall append exactly one `readiness_probe` JSONL record per registered server to `.claude/runtime/mcp-events.jsonl` (seven records on a healthy run), with fields `{ts, event:"readiness_probe", server, probe_method:"ping", latency_ms, result:"pass"|"fail"}` per the schema owned by design-cc (`KB-mcp-design/references/principles.md`).
- **AC-CS-5 (postStart warn-and-continue):** If one or more probes returns `fail`, then the system shall write the corresponding JSONL records, emit a stderr banner naming the degraded count, AND exit 0 (warn-and-continue posture per Q-CS-3). The lifecycle shall not be blocked by a degraded MCP surface.
- **AC-CS-6 (Codespaces secrets wiring):** When `.mcp.json` references `${CONTEXT7_API_KEY}`, `${EXA_API_KEY}`, or `${TFE_TOKEN}`, the system shall resolve those env vars from the operator's Codespaces secrets via the `containerEnv` mapping; no secret value shall appear in any committed file (AC-NFR-2-a).
- **AC-CS-7 (No port forwarding):** When the Codespace starts, the system shall have `forwardPorts: []` and no port forwarded by default. Any future MCP server requiring a forwarded port shall add an explicit `forwardPorts` entry with `visibility: "private"` (KB-codespaces-design Principle 7).
- **AC-CS-8 (Rebuild-time envelope):** When the Codespace is built from a clean cache, the system shall complete devcontainer build + Features + `postCreateCommand` within approximately 10 minutes (PRD NFR-1 cold-cache target). When rebuilt from a warm cache, the system shall complete in approximately 2 minutes (PRD NFR-1 warm-cache target).
- **AC-CS-9 (GitNexus skip-grammars smoke-test):** When `postCreate.sh` runs the GitNexus install step, the system shall export `GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1` BEFORE invoking the install, then run `npm install -g gitnexus@${GITNEXUS_TAG}` for the persistent install and `npx -y gitnexus@${GITNEXUS_TAG} --help` for the ephemeral smoke-test, and shall fail postCreate if either step returns a non-zero exit (smoke-test required per synthesis C-0388/C-0411 partially_verified-medium). **AC SEMANTIC INTENT PRESERVED across the cycle-3 D-3.2 F2 install-mechanism correction**: the env-var suppresses npm's vendored tree-sitter grammar build, so the cold-cache install completes without a C++ toolchain (`cc`/`g++`/`cargo`) on PATH — install-command-agnostic on the AC-CS-9 axis. Prereq: Node-LTS on PATH at postCreate time (provided by the `ghcr.io/devcontainers/features/node:1@20` Feature; verified by AC-CS-1).

## Dependencies on Other Layers

| Other layer | Direction | Contract |
|---|---|---|
| design-cc (Claude Code / Project Filesystem) | depends_on (this layer consumes) | `.mcp.json` schema (which env vars to reference; which transport per server). `mcp-events.jsonl` schema for `readiness_probe` record shape (KB-mcp-design `principles.md`). |
| design-cc | provides_to | `containerEnv` populates the three env vars `.mcp.json` reads. `postCreate.sh` installs the binaries `.mcp.json` references. `postStart.sh` writes `readiness_probe` records into the shared jsonl. |
| design-composer | depends_on (this layer consumes) | Reconciliation of where the credential-redaction filter runs at the log boundary (synthesis 9.3 item 2 sub-decision — design-codespaces' postStart writes stderr, so the redaction filter at the stderr-capture boundary needs a code-site decision the composer arbitrates). |
| IaC, Backend, Frontend, API, Query, Database, CI/CD | (none) | Out of scope this feature. |

## Architectural Questions for Composer (Q-CS-N)

- **Q-CS-1 (onCreate vs postCreate split for install):** The recommended posture (synthesis D-0004) places all seven installs in `postCreateCommand`. An alternative is to split: long-running base setup (uv install, Go-toolchain prime) in `onCreateCommand` so prebuilds (if later adopted) capture it; project-mount-dependent steps remain in `postCreateCommand`. The synthesis explicitly notes `onCreateCommand` is "too early for stdio servers needing project mount" — but only some of the seven need workspace mount at install time (actionlint-mcp and terraform-mcp install standalone binaries; uvx-based servers are workspace-agnostic at install). **Recommended: keep all installs in postCreate for simplicity and homogeneity; revisit only if prebuilds are adopted (Q-CS-2).** Defer to composer.

- **Q-CS-2 (Prebuild adoption):** This release does NOT adopt Codespaces prebuilds. The recommendation is to revisit post-ship if cold-cache rebuild routinely exceeds ~10 min (NFR-1 target) in operator usage. The choice affects: org compute budget; which lifecycle hooks would need to move from postCreate to onCreate/updateContent to be captured. **Recommended: defer; do not adopt in this release.** Defer to composer.

- **Q-CS-3 (postStart probe failure handling — fail vs warn-and-continue):** The recommended posture is **warn-and-continue**: write the structured `readiness_probe` record with `result=fail`, emit a stderr banner, exit 0. Rationale: a degraded HTTP server (Context7 / Exa upstream blip) should not block Codespace start; AC-FR-8-d requires the failure be surfaced, not that the lifecycle fail. Alternative (fail postStart) would force operator intervention for every transient SaaS hiccup. **Recommended: warn-and-continue (AC-CS-5).** Defer to composer.

- **Q-CS-4 (containerEnv vs runArgs --env for secret injection):** Recommended is `containerEnv` with `${localEnv:NAME}` indirection — devcontainer-spec-canonical, idempotent, auditable. `runArgs: ["--env", "NAME=${localEnv:NAME}"]` works but is Codespaces-host-implementation-detail. **Recommended: containerEnv.** Defer to composer.

- **Q-CS-5 (Idempotence mechanism — sentinel files vs unconditional re-run):** Recommended is **sentinel-file-guarded re-run** under `.claude/runtime/install-sentinels/<server>@<version>.installed`. Version-pinned sentinel names ensure stale sentinels invalidate on pin change. Alternative (unconditional re-run on every rebuild) is simpler but adds ~30s-2min to every rebuild; net loses on the NFR-1 warm-cache budget. **Recommended: sentinel-file-guarded.** Defer to composer.

- **Q-CS-6 (Go-feature installation of actionlint-mcp vs multi-stage Dockerfile):** Recommended is **Go Feature + `go install` in postCreate**. Multi-stage Dockerfile would force a Dockerfile change (D-0001 rejects), would prevent operator-driven pin bump without rebuild, and would not save substantial time (Go install of one binary is <30s). **Recommended: Go feature + postCreate `go install`.** Defer to composer.

- **Q-CS-7 (Probe primitive — `claude mcp ping` vs direct JSON-RPC):** Recommended is to **prefer `claude mcp ping <server>` if Claude Code CLI exposes it; fall back to direct JSON-RPC over the transport** (D-0008 rejects `claude mcp list` parsing as brittle). Whether `claude mcp ping` exists in the pinned Claude Code version is a verify-at-execution item. **Recommended: `claude mcp ping` preferred; JSON-RPC fallback.** Defer to composer. **Verify at execution time** with the pinned Claude Code Feature version.

- **Q-CS-8 (mcp-events.jsonl schema ownership across layer boundary):** The schema (`{ts, event, server, ...}`) is owned by design-cc (`KB-mcp-design/references/principles.md`). The codespaces layer's `postStart.sh` writes records using that schema. Cross-layer cooperation requires the schema be authored before postStart.sh is finalized — surfaced as a sequencing dependency, not a substantive disagreement. **Recommended: design-cc authors the schema first; codespaces consumes.** Defer to composer for sequencing.

## Rebuild-Time Estimate

Per PRD NFR-1 (cold ≤ ~10 min; warm ≤ ~2 min):

| Phase | Cold-cache estimate | Warm-cache estimate | Notes |
|---|---|---|---|
| Base image pull + Dockerfile layers | 2–3 min | <30s | Base image and Dockerfile RUN layers cached (Yarn-key fix + utility install). |
| Features (common-utils, github-cli, Node 20, Go, claude-code) | 3–5 min | <30s | Go feature adds ~1–2 min vs current state. |
| `onCreateCommand` (version checks) | <5s | <5s | Unchanged. |
| `postCreateCommand` (`postCreate.sh`) | 2–4 min | <10s (sentinels short-circuit) | `go install actionlint-mcp` ~30s; `wget`+verify Terraform MCP ~30s; `uvx --help` warmups ~10–20s each. |
| `postStartCommand` (`postStart.sh`) | ~2s | ~2s | 7 pings + optional 2 auth-probes. |
| **Total cold-cache** | **~7–12 min** | — | Within NFR-1 envelope; closer to upper bound if any uvx prime takes longer than expected. |
| **Total warm-cache** | — | **~1–2 min** | Within NFR-1 envelope. |

**Risk:** the cold-cache estimate sits near the upper bound of NFR-1. If the Codespace habitually rebuilds cold (e.g., operator regularly trashes-and-recreates), the estimate could spill. Mitigation deferred to Q-CS-2 (prebuild adoption post-ship).

## Open Items

- **OI-CS-1:** GitNexus install pin form (synthesis D-0011 says "exact tag per ADR-0007 v2.2.0"). Concrete `GITNEXUS_TAG` value is set at execution time; the design only commits to the form. Smoke-test failure mode is fail-postCreate (AC-CS-9).
- **OI-CS-2:** actionlint-mcp commit SHA is set at execution time (C-0133 "verify at execution"). The design commits to the pin form (`go install <repo>@<sha>`), not the specific SHA.
- **OI-CS-3:** Terraform MCP version (`TERRAFORM_MCP_VERSION`) — synthesis suggests `0.5.2`; verify-at-execution per C-0158.
- **OI-CS-4:** Exa `--header` CLI form vs `.mcp.json` header — affects design-cc, not design-codespaces (the codespaces layer only wires the env var); listed here for completeness.
- **OI-CS-5:** Whether `claude mcp ping` exists in the pinned Claude Code Feature version (Q-CS-7 verify-at-execution).

## Provenance

- PRD: `working/feature/devcontainer-mcp-provisioning-r1/prd-v3.md` (v3.0.0)
- Synthesis: `working/feature/devcontainer-mcp-provisioning-r1/synthesis.md` (sections 8 constraints; 9.2 design-codespaces handoff)
- Codebase analysis: `working/feature/devcontainer-mcp-provisioning-r1/codebase-analysis.json` (commit cf48e5e)
- Discipline: KB-codespaces-design (principles + patterns-and-anti-patterns); KB-codespaces-platform (devcontainer.json schema + lifecycle hooks)
- Decision frames consumed: D-0001, D-0003, D-0004, D-0007 (cooperation), D-0008, D-0011 (per-server pin table), D-0013 (no codespaces impact)
- Constraints honored: #1, #2, #3, #4, #9, #10, #11, #13 (synthesis §8)
