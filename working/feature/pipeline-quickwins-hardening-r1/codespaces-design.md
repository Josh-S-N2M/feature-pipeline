---
id: codespaces-design-pipeline-quickwins-hardening-r1
version: 0.3.1
status: draft
feature_slug: pipeline-quickwins-hardening-r1
doc_type: per-layer-design
layer: codespaces
derived_from:
  - working/feature/pipeline-quickwins-hardening-r1/prd-v1.md
  - working/feature/pipeline-quickwins-hardening-r1/synthesis.md
  - working/feature/pipeline-quickwins-hardening-r1/codebase-analysis.json
  - working/feature/pipeline-quickwins-hardening-r1/research-notes/t-001-gitnexus-grammar-skip-contract.md
predecessor: working/feature/pipeline-quickwins-hardening-r1/codespaces-design.md@v0.2.0
generated: 2026-05-26T00:00:00Z
generated_by: design-codespaces
change_summary: >
  Hybrid reshape of FR-4 (per user direction at Gate-4 prep). Splits the single
  per-rebuild dry-run into three sub-mechanisms: FR-4a (sub-100ms static check
  in postCreate.sh top-level flow BEFORE install_gitnexus); FR-4b (opt-in
  behavioral calibration script with scratch-dir install, owned by Codespaces
  layer); FR-4c (CI wiring of FR-4b — weekly cron + on-versions.env-change,
  emits to mcp-events.jsonl per ADR-0037; OWNED BY DESIGN-CICD). The v0.2.0
  insertion site (inside install_gitnexus(), between postCreate.sh:142 and
  :143) is REJECTED — the chosen FR-4a site is top-level postCreate.sh between
  current lines 197 and 198 (after install_terraform_mcp, before
  install_gitnexus). Per-rebuild check is static-only (env-var, tag-pin,
  path-predictability); Signal 1 stderr regex and Signal 3 artifact-absence
  move to FR-4b. NFR-3 threshold tightens from <2s to <100ms p95 (static check
  has no cache-vs-no-cache semantics). Q-CS-1 reframed: immutable-tag assumption
  is no longer load-bearing; reframed question asks about observability
  (whether to surface a runtime banner if last calibration event is stale).
  v0.3.1 (2026-05-26) — prose-only correction per pipeline-quickwins-hardening-r1
  Architecture Audit cycle 1 finding I-AA-001 collateral repair: every reference
  to the three pre-existing mcp-events.jsonl event types now reads
  `install_complete / readiness_probe / structured_failure` (the on-disk
  vocabulary per ADR-0037 v1.0.2 and per audit_op7_events_schema.py); the
  v0.3.0 prose inherited the v1.0.0 / v1.0.1 ADR-0037 error and wrote
  `primary_degraded` in its place. primary_degraded is a boolean sub-field of
  structured_failure, not a top-level event type. No decision-content change.
---

# Codespaces Design — Pipeline Quick-Wins Hardening (Round 1)

## Layer responsibility scope

This subsection covers the FR-4 mechanism only. Everything else FR-* lives in other layers (Claude Code for FR-1 / FR-2 / FR-3 / FR-7; CI/CD for FR-5 plus FR-4c CI wiring; FR-6 is cross-cutting).

The v0.3.0 design splits FR-4 into three sub-mechanisms per user direction at Gate-4 prep:

- **FR-4a — per-rebuild static check** (Codespaces-owned). Runs on every container creation, sub-100 ms, verifies env-var set + tag pinned + expected artifact paths predictable. Static-shape question: "did someone delete the env-var, fat-finger the pin, or rename the artifact path?" Fail-closed: halts `postCreate.sh` before `install_gitnexus()` runs.
- **FR-4b — opt-in behavioral calibration** (Codespaces-owned). Standalone maintainer script at `.devcontainer/scripts/calibrate-gitnexus-grammar-skip.sh`. Performs the full upstream-behavioral check (scratch-dir install, Signal 1 stderr regex, Signal 3 artifact-absence, optional negative-assertion confirmation). Behavioral question: "has upstream's `GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1` actually been honored in the new tag?" Not invoked from `postCreate.sh`. Cost ~30 s when run.
- **FR-4c — CI wiring for FR-4b** (design-cicd-owned; documented here only for cross-layer traceability). Weekly cron + on-change-to `.devcontainer/versions.env`. Emits results to `mcp-events.jsonl` per ADR-0037 so the result is observable, not just a CI exit code.

The base image, the Dev Container Features set, the machine class, the lifecycle-hook surface, the persistence boundaries, the secrets model, and the port-forward declarations are all **inherited unchanged** from the prior `devcontainer-mcp-provisioning-r1` feature (per ADR-0041 v1.0.1). Per NFR-14, this run explicitly disclaims any other devcontainer-layer additions. Sections below document the inherited state so the reader has the full picture; the only design decisions originating in this run are FR-4a + FR-4b (plus the FR-4c handoff to design-cicd).

## Base mechanism

**Inherited (unchanged).** Custom Dockerfile via `build.dockerfile = "Dockerfile"` with `build.context = ".."` and a `PYTHON_VERSION=3.11` build arg. Not an image-based setup, not docker-compose. The Dockerfile already exists at `.devcontainer/Dockerfile` and carries apt-installed tooling (jq, ripgrep, bat, tree, less, shellcheck). This run does not modify the Dockerfile.

Rationale (per Principle 6, Features-for-known-tools-Dockerfile-for-unknowns; KB-codespaces-design/references/principles.md §Principle 6): the project legitimately needs a Dockerfile because the apt packages it carries (shellcheck for hook-script linting in particular) are not all available as Features, and pinning them at image-build time is the right discipline. Stays inside the carve-out.

## Tools installation strategy

**Inherited (unchanged).** Features registry entries already in place:

- `ghcr.io/devcontainers/features/common-utils:2` — pinned to version 2; non-zsh defaults; user `vscode`.
- `ghcr.io/devcontainers/features/github-cli:1` — `version: latest`. (Pin-by-major; the `latest` is the channel under the `:1` major-pin, not unbounded.)
- `ghcr.io/devcontainers/features/node:1` — `version: 20`. Provides the `npm` and `node` GitNexus depends on.
- `ghcr.io/devcontainers/features/go:1` — `version: 1.22`. Provides the `go` toolchain for `go install`-based actionlint-mcp.
- `ghcr.io/anthropics/devcontainer-features/claude-code:1` — provides the `claude` CLI in the container.

Plus four MCP servers installed by `postCreateCommand` per ADR-0041 v1.0.1: serena (uv tool install), actionlint-mcp (go install), terraform-mcp (binary + sha256 + gpg), gitnexus (npm install -g). No Features are added or removed by this run.

## Lifecycle-hook placement table

Existing flow + the two new steps. New rows are bold.

| Setup step | Hook | Captured by prebuild? | Why this hook |
|---|---|---|---|
| Apt packages (jq, ripgrep, bat, tree, less, shellcheck) | Dockerfile RUN (image-build-time) | n/a (baked into image) | Tools that don't change between rebuilds; Principle 6. |
| Features installs (common-utils, github-cli, node@20, go@1.22, claude-code) | Features layer (pre-postCreate) | Yes (Features are captured) | Versioned installers per Principle 6. |
| `onCreateCommand` — `claude --version && python3 --version && node --version && go version && gh --version` | `onCreateCommand` | Yes | Tool-presence sanity check, content-independent — captured by prebuild (Principle 2; KB-codespaces-design/references/principles.md §Principle 2). |
| **FR-4a — static contract check (env-var set, tag pinned, expected artifact paths predictable)** | **`postCreateCommand` top-level flow in `.devcontainer/postCreate.sh`, BETWEEN current line 197 (`install_terraform_mcp || …`) and current line 198 (`install_gitnexus || …`)** | **No** (would run inside prebuild if prebuilds existed; runs equally cheaply on cache-hit and cache-miss rebuilds, so prebuild capture does not matter for FR-4a's semantics) | **Per-rebuild static-shape question; sub-100 ms; fail-closed BEFORE `install_gitnexus()` runs so a broken pin / missing env-var / unpredictable artifact path never gets the chance to silently install the wrong shape.** |
| MCP server installs (serena, actionlint-mcp, terraform-mcp, gitnexus) | `postCreateCommand` (`postCreate.sh`) | No | Already at `postCreateCommand` per ADR-0041 §4; this run doesn't change placement. Sentinel-and-binary-on-PATH guard keeps idempotency. |
| `gitnexus_post_install_warm` (existing, postCreate.sh:201) | `postCreateCommand` | No | Inherited; sits AFTER `install_gitnexus` at line 201. FR-4a's insertion at line 197/198 does NOT collide. |
| HTTP auth probes (context7, exa) | `postCreateCommand` end (`postCreate.sh`) | No | Probes need live network and credentials; not capturable. |
| **FR-4b — behavioral calibration script** | **NOT in any lifecycle hook. Standalone script at `.devcontainer/scripts/calibrate-gitnexus-grammar-skip.sh`; invoked manually by a maintainer OR by CI (FR-4c, design-cicd-owned).** | **n/a** | **Behavioral question costs ~30 s of npm time. Out-of-band of the per-rebuild flow per user direction: "doubling the GitNexus step on cache-miss rebuilds for a check that only fires when upstream has actually drifted gets nothing back for most rebuilds."** |
| Anything started or warmed per session | `postStartCommand` (`postStart.sh`) | No | Inherited; not touched by this run. |

The three positions (line 197 `install_terraform_mcp`, the FR-4a static check, line 198 `install_gitnexus`) form an ordered triple — `install_terraform_mcp` and `install_gitnexus` are independent installs adjacent in the script today, and FR-4a inserts between them. The line numbers 197 and 198 are the live `.devcontainer/postCreate.sh` numbers at the time of this design (per Read of postCreate.sh at 2026-05-26); Plan Authoring should treat them as anchors, not absolutes.

## Prebuild strategy

**Inherited (unchanged): no prebuilds configured.** This run does not introduce one. Rationale: the existing post-create flow is bounded by the MCP-server install times (serena via uv, actionlint-mcp via go install, terraform-mcp binary download, gitnexus via npm) plus the new FR-4a static check (sub-100 ms — negligible); the maintainer's typical rebuild cadence is low. Per Principle 4 and the explicit NFR-14 disclaimer, adding a prebuild here would be over-engineering. Surface as Q-CS-4 (below) for the design-composer to confirm against any org-wide policy.

If a prebuild is added in a future run, neither FR-4a nor FR-4b need to move:

- FR-4a sits at `postCreateCommand` (uncaptured) — it would still run on every rebuild post-prebuild, which is exactly the semantics it needs (the static check is a per-rebuild question; whether the snapshot froze the artifact paths matters less than whether the env-var is set in the current shell).
- FR-4b is out-of-band of the lifecycle entirely — prebuilds simply don't see it.

## Persistence boundaries

**Inherited (unchanged).** Per Principle 3 (KB-codespaces-design/references/principles.md §Principle 3):

- `/workspaces/feature-pipeline` (the repo mount) — survives rebuild. Source, generated audit artifacts under `.claude/runtime/`, MCP event log `.claude/runtime/mcp-events.jsonl`, install sentinels under `.claude/runtime/.install-sentinel-<server>-<version>`.
- Image-managed dirs (`/usr/local/bin/serena`, `~/go/bin/actionlint-mcp`, `/usr/local/lib/node_modules/gitnexus/...`, the `claude` CLI) — ephemeral, rebuilt from the Dockerfile or postCreate steps on rebuild.
- Sentinels (under `.claude/runtime/`) — survive rebuild because `.claude/runtime/` is under the workspace mount.

FR-4 implications:

- **FR-4a (per-rebuild static check)** creates **no** artifacts under the workspace. It does not write a sentinel, does not write a marker, does not cache state. It either passes (silently green-light into `install_gitnexus()`) or emits one `structured_failure` event into `.claude/runtime/mcp-events.jsonl` and halts.
- **FR-4b (calibration script)** creates a scratch directory via `mktemp -d` and cleans it up before exit. It emits exactly one event per run into `.claude/runtime/mcp-events.jsonl` (the only persistent artifact it leaves). No sentinel, no cache.

**Sentinel-inconsistency resolution (per Codebase Analysis known-issues row 2).** Two sentinel conventions already coexist in this project: ADR-0041's canonical `<server>@<version>.installed` under `.claude/runtime/install-sentinels/` and the live `postCreate.sh`'s `.install-sentinel-<server>-<version>` directly under `.claude/runtime/`. Per the synthesis "do NOT introduce a third sentinel format" directive, both FR-4a and FR-4b are **sentinel-less**. Neither creates a new sentinel and neither consults one of its own. The existing `install_gitnexus()` sentinel is unchanged; FR-4a sits BEFORE that function and FR-4b is out-of-band. That keeps the carve-out narrow (we don't touch the existing inconsistency; we don't add to it).

## Machine class

**Inherited (unchanged).** `hostRequirements.cpus: 4`, `memory: "8gb"`, `storage: "32gb"` per `devcontainer.json`. Per Principle 4 (KB-codespaces-design/references/principles.md §Principle 4), 4-core is right-sized for a Codespace that runs Node + Go + Python + Claude Code concurrently for a single maintainer. FR-4a's sub-100 ms static check adds negligible wall-clock; FR-4b runs out-of-band and is bounded by ~30 s when invoked. This run does not change the machine class.

## Secrets and config

**Inherited (unchanged).** Per Principle 5 (KB-codespaces-design/references/principles.md §Principle 5) and NFR-7:

- `CONTEXT7_API_KEY`, `EXA_API_KEY`, `TFE_TOKEN` are passed through from local env via `containerEnv.${localEnv:...}` per ADR-0039 / ADR-0041. They are Codespaces user secrets (per-user); the repo doesn't ship them.
- `GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1`, `SERENA_VERSION`, `ACTIONLINT_MCP_SHA`, `GITNEXUS_TAG`, `TERRAFORM_MCP_VERSION` are non-secret config; they live in `devcontainer.json` `containerEnv` and `.devcontainer/versions.env`.
- No new secret is introduced by FR-4a or FR-4b. FR-4a reads `GITNEXUS_SKIP_OPTIONAL_GRAMMARS` (env) and `GITNEXUS_TAG` (env, sourced from versions.env). FR-4b reads the same plus does a transient `npm install -g` into a scratch dir.

Per NFR-8, both mechanisms' diagnostics emit env-var **names** (`GITNEXUS_SKIP_OPTIONAL_GRAMMARS`, `GITNEXUS_TAG`), never values that could be credentials. The two env vars FR-4 reads are not credentials, but the rule of thumb is enforced uniformly anyway.

## Port forwarding

**Inherited (unchanged).** `forwardPorts: []` — no ports forwarded. None of the MCP servers in this project listen on a TCP port; the four OSS-local ones use stdio transport via `command + args`, and the two HTTP ones (context7, exa) are outbound to hosted endpoints. Neither FR-4a nor FR-4b adds a port. Per Principle 7 (KB-codespaces-design/references/principles.md §Principle 7), the explicit empty list signals intent: this codespace is not a server-running environment.

## Multi-container topology

**N/A.** Single-container (custom Dockerfile, not docker-compose). FR-4 does not change that.

## Dotfiles support

**Inherited (unchanged).** Neither encouraged nor restricted by this run. The repo's `.devcontainer` does not configure dotfiles; that's a per-user Codespaces setting and is out of this feature's scope.

## Monorepo positioning

**N/A.** Single-component repo; the canonical `.devcontainer/` lives at repo root.

## Idle timeout and retention

**Inherited (unchanged).** No override in `devcontainer.json`; uses the org/user defaults (30 min idle, 30 day retention per Codespaces defaults — subject to any org-level policy that overrides them). FR-4 doesn't touch this.

## Org-level policy alignment

The project today is single-maintainer; no org-level Codespaces policy is in evidence in `.devcontainer/`. If an org-level base-image or machine-class policy lands in a future run, both FR-4a (a small additive block in `postCreate.sh`) and FR-4b (a standalone script under `.devcontainer/scripts/`) are forward-compatible — neither depends on any image or machine-class choice. Surface as Q-CS-4 (below) if the design-composer has visibility into a pending org policy this designer doesn't.

## FR-4a — per-rebuild static check

### Insertion site

`.devcontainer/postCreate.sh`, **top-level flow, BETWEEN current line 197 (`install_terraform_mcp || emit_degraded_banner "terraform-mcp" "<no fallback>"`) and current line 198 (`install_gitnexus || emit_degraded_banner "gitnexus" "<no fallback>"`)**. The check is a discrete block executed at top-level; it does NOT live inside `install_gitnexus()`. Rationale:

- The check must run BEFORE `install_gitnexus` so a broken pin / missing env-var / unpredictable artifact path halts the install before it executes (fail-closed; NFR-6). Running inside the function (the v0.2.0 design) couples the check's runtime to the install's runtime, but the per-rebuild question is static-shape — it can be answered with no install at all.
- The check runs equally cheaply on cache-hit and cache-miss paths because it never invokes `npm install -g`. There is no cache-vs-no-cache semantics for FR-4a; it is purely a `grep` / `stat` / read against the current shell's environment and `versions.env`.
- The existing `gitnexus_post_install_warm` helper sits AFTER `install_gitnexus` at line 201; the three positions (197, FR-4a, 198, 199, 200, 201) form a non-colliding ordered sequence.
- The check is at top-level (not inside a function) so its failure halts `postCreate.sh` via `set -euo pipefail` directly, with no `|| emit_degraded_banner` warn-and-continue masking (per NFR-6 fail-closed posture: drift in the GitNexus contract is exactly the case where a degraded banner is the WRONG default; halting forces the maintainer to confront the failure).

### Positive-assertion contract (static-only)

The per-rebuild check is **static-only**. It does NOT install, does NOT capture stderr, does NOT inspect post-install filesystem state. The Signal 1 stderr regex and Signal 3 artifact-absence checks from v0.2.0 are NO LONGER part of the per-rebuild flow — they move to FR-4b (the calibration script). The per-rebuild check asserts only:

- **Sub-assertion A1 (env-var set).** `$GITNEXUS_SKIP_OPTIONAL_GRAMMARS` is set in the current shell environment AND equals the literal string `1`. Rationale: this is the env-var the install path will read; if it's unset or set to anything else, the install will not skip the optional grammars. (At v1.6.5 the upstream code does a strict `=== '1'` check per T-001 F-1; future tags may loosen this — see FR-4b's negative-assertion confirmation for the behavioral check.)
- **Sub-assertion A2 (tag pinned).** `$GITNEXUS_TAG` is set in the current shell environment AND non-empty AND matches a recognized semver-or-tag format (regex: `^v?[0-9]+\.[0-9]+\.[0-9]+(-[A-Za-z0-9.-]+)?$` — accepts `1.6.5`, `v1.6.5`, `1.6.5-rc1`). Rationale: `npm install -g gitnexus@${GITNEXUS_TAG}` with an empty or malformed `GITNEXUS_TAG` either installs `gitnexus@latest` (silent drift) or fails with an opaque npm error — both are worse than halting here.
- **Sub-assertion A3 (versions.env source).** `$GITNEXUS_TAG` matches the value declared in `.devcontainer/versions.env` for the key `GITNEXUS_TAG`. Rationale: catches the case where `versions.env` was edited but the export didn't propagate (e.g., a maintainer ran `vim versions.env` but forgot to re-source it before testing). The check reads `versions.env` via `grep '^GITNEXUS_TAG=' .devcontainer/versions.env | cut -d= -f2` and compares.
- **Sub-assertion A4 (artifact paths predictable).** `npm root -g` returns a non-empty path AND `dirname "$(npm root -g)"` is writable by the current user. The expected per-grammar artifact paths can be predicted as `$(npm root -g)/gitnexus/node_modules/tree-sitter-(dart|proto)/build/Release/tree_sitter_(dart|proto)_binding.node` — these are the paths FR-4b will check absence of. Rationale: catches the case where `npm root -g` is misconfigured (e.g., a user-prefix-override that points to a path the install can't write to), which would silently misroute the artifact paths and make any future FR-4b assertion meaningless.

**Swift exclusion (per T-001 F-4).** No sub-assertion about Swift. At v1.6.5 the env-var governs only Dart and Proto; Swift's non-build is governed by npm's `optionalDependencies` failure tolerance independently. Asserting on Swift would be technically false. This is the same exclusion v0.2.0 enforced; the design preserves it.

Pass = A1 AND A2 AND A3 AND A4. Fail = any one fails. Wall-clock budget: sub-100 ms p95 (grep / stat / read; no install, no network) — see NFR-3 acceptance criterion below.

### Failure mode (fail-closed)

On failure, FR-4a:

1. Emits a `structured_failure` event via `log_mcp_event` (existing helper; ADR-0037 schema, NFR-13 honored) whose `note:` field names FR-4a, the failing sub-assertion (A1 / A2 / A3 / A4), the observed value (or the value's absence), and a one-line remedial hint.
2. Emits a plain-text operator diagnostic to stderr per the existing dual-stream convention.
3. Returns non-zero at the script level — because the check is at top-level (not inside a function with `|| emit_degraded_banner`), `set -euo pipefail` halts `postCreate.sh` immediately. The codespace creation fails-closed; the maintainer must fix the static-shape issue (re-set the env-var, fix the pin, fix `versions.env`, fix `npm root -g`) before re-rebuilding.

### Diagnostic message text (honors FR-6)

**Signal identifier token set (fixed).** Four tokens are defined for FR-4a:

- `signal-a1-env-var-unset-or-wrong` — `$GITNEXUS_SKIP_OPTIONAL_GRAMMARS` is not set, or is set but not equal to `1`.
- `signal-a2-tag-pin-malformed` — `$GITNEXUS_TAG` is unset, empty, or does not match the recognized format.
- `signal-a3-versions-env-mismatch` — `$GITNEXUS_TAG` does not match the value in `.devcontainer/versions.env`.
- `signal-a4-artifact-paths-unpredictable` — `npm root -g` returned empty, OR its parent is not writable.

Both the plain-text stream and the structured JSONL event use the same token verbatim.

**Plain-text operator diagnostic (stderr):**

```
[postCreate] FR-4a GitNexus static contract check FAILED:
  signal: <signal-a1-env-var-unset-or-wrong | signal-a2-tag-pin-malformed | signal-a3-versions-env-mismatch | signal-a4-artifact-paths-unpredictable>
  observed: <quoted observed value or "<unset>">
  expected: <expected shape>
  remedial: <one-line>
```

**Structured JSONL event (via `log_mcp_event`):**

```json
{
  "event": "structured_failure",
  "timestamp": "<iso8601>",
  "server": "gitnexus",
  "install_method": "static-check",
  "version": "<GITNEXUS_TAG or '<unset>'>",
  "duration_ms": <n>,
  "status": "failed",
  "note": "FR-4a static contract check failed: signal=<token>; observed=<short-quote>; expected=<short-quote>; remedial=<one-line>"
}
```

The `structured_failure` event type already exists per ADR-0037; no new event type is introduced (NFR-13 honored). The `note:` field encodes the four FR-6 elements: mechanism name (FR-4a), offending artifact (the env-var / pin / versions.env / npm root), rule violated (one of the four fixed signal tokens), remedial action.

## FR-4b — opt-in behavioral calibration script

### Path and contract

Script at `.devcontainer/scripts/calibrate-gitnexus-grammar-skip.sh`. Standalone — NOT invoked from `postCreate.sh`. Invoked by:

- The maintainer manually (`bash .devcontainer/scripts/calibrate-gitnexus-grammar-skip.sh`) when bumping `GITNEXUS_TAG` and wanting to verify the env-var contract still holds.
- CI per FR-4c (weekly cron + on-change-to `.devcontainer/versions.env`) — wiring owned by `design-cicd`.

**Script contract (fixed by this design; Plan Authoring fills in line-level implementation):**

1. **Takes no arguments.** No flags, no positional args. Behavior is fixed by the script's body.
2. **Reads `GITNEXUS_TAG`** from `.devcontainer/versions.env` (via `source` or grep+cut). Errors out if unset / empty.
3. **Creates a scratch directory** via `mktemp -d`. Sets `npm config set prefix "${scratch}/npm-global"` (scoped to the script's subshell) so the install does not perturb the codespace's global npm state.
4. **Installs gitnexus into the scratch dir** with `GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1`: `GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1 npm install -g "gitnexus@${GITNEXUS_TAG}" 2> "${scratch}/stderr.log"`. Captures stderr to a file (not redirected to `/dev/null`).
5. **Asserts Signal 1 (stderr regex match per grammar).** The captured stderr matches `\[tree-sitter-(dart|proto)\] Skipping build \(GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1\)` AT LEAST ONCE for each of `dart` and `proto` (per T-001 F-1 + F-2 + AC-2). The regex form (not literal-string match) is per drift-mode DM-1 (T-001) — robust to minor wording shifts in upstream's warning text. Per-grammar capture is what lets the assertion simultaneously verify both grammars in one regex pass.
6. **Asserts Signal 3 (artifact-path absence).** After the install completes (exit 0), the paths `${scratch}/npm-global/lib/node_modules/gitnexus/node_modules/tree-sitter-dart/build/Release/tree_sitter_dart_binding.node` and `.../tree-sitter-proto/build/Release/tree_sitter_proto_binding.node` do NOT exist (per T-001 F-5 + AC-2). The location is derived from the scratch prefix, not hard-coded.
7. **Optional negative-assertion confirmation (calibration-of-the-calibration; per T-001 DM-4).** Re-installs into a second scratch directory with `GITNEXUS_SKIP_OPTIONAL_GRAMMARS=0` and asserts the artifacts ARE built. This defends against the failure mode where the env-var contract is silently disabled at the pinned tag (i.e., the install is skipping regardless of the env-var, which a `=1` check would not catch). The negative-assertion is **enabled by default** in the script; a maintainer can edit the script to disable it only for a short-cycle check. Rationale: the user's trap-avoidance direction — "the script must be easy to run and observable, or it will quietly stop running" — means the script should do the strongest check it can per invocation, not gate parts behind flags.
8. **Emits exactly one event per run** to `.claude/runtime/mcp-events.jsonl` via `log_mcp_event`. Event shape (per ADR-0037 v1.0.2 + ADR-0058 — see "event shape" below):

   ```json
   {
     "event": "calibration_result",
     "timestamp": "<iso8601>",
     "server": "gitnexus",
     "mechanism": "fr-4b-gitnexus-grammar-skip",
     "version": "<GITNEXUS_TAG>",
     "duration_ms": <n>,
     "outcome": "pass | fail | drift_detected",
     "signals": {
       "signal_1_stderr_match_dart": "pass | fail",
       "signal_1_stderr_match_proto": "pass | fail",
       "signal_3_artifact_absence_dart": "pass | fail",
       "signal_3_artifact_absence_proto": "pass | fail",
       "negative_assertion_artifacts_built": "pass | fail | skipped"
     },
     "note": "<one-line summary; remedial hint on fail>"
   }
   ```

9. **Cleans up the scratch directories** via `trap 'rm -rf "${scratch}" "${scratch2:-}"' EXIT`.
10. **Returns 0 on pass, non-zero on any signal failure.** Exit code is the secondary observability channel; the `mcp-events.jsonl` event is the primary.

### Event shape — `calibration_result` or `structured_failure`?

This design proposes a new `event` value `calibration_result` on the existing event-type vocabulary. There are two interpretations:

- **Interpretation A (recommended):** `calibration_result` is a NEW event-type value (`"event": "calibration_result"`) — not just a new field on an existing event. This requires the ADR-0037 vocabulary to admit a fourth value beyond `install_complete` / `readiness_probe` / `structured_failure` (the three pre-existing types per the on-disk vocabulary, as corrected in ADR-0037 v1.0.2). NFR-13 says "no new event types" under a strict reading; this is a deviation the composer must reconcile.
- **Interpretation B (fallback if NFR-13 is read strictly):** Use the existing `structured_failure` event-type for fail/drift_detected outcomes and `install_complete` for pass outcomes (the calibration "installs" — into a scratch dir — and the pass outcome is genuinely an install completion plus contract verification). Pack the `signals` map into the existing `note:` free-text field as a JSON-stringified blob. [v0.3.1 prose correction: v0.3.0 described Interpretation B as packing into `primary_degraded` for pass outcomes; the on-disk vocabulary per ADR-0037 v1.0.2 is `install_complete`, not `primary_degraded` (which is a boolean sub-field of `structured_failure`).]

**Q-CS-1 (REFRAMED)** explicitly asks the composer to pick between A and B. Recommended: A (clearer semantics; FR-4c's CI workflow and any downstream analytics can `jq '.event == "calibration_result"'` cleanly). If the composer reads NFR-13 strictly, fallback to B.

### Trap-avoidance (per user direction)

The user warned: "The trap to avoid with option 3: opt-in scratch script has to be easy to run and observable, or it will quietly stop running. Wire it into CI on a schedule + on any change to versions.env, and emit results to the same mcp-events.jsonl event surface per ADR-0037. If it ends up as a maintainer-only shell script that nobody invokes for six months, option 3 degrades silently into option 1."

This design defeats the trap with three load-bearing mechanisms:

1. **Event emission, not silent exit code.** The script writes a `calibration_result` event to `mcp-events.jsonl` regardless of pass/fail. The result is queryable (`jq 'select(.mechanism == "fr-4b-gitnexus-grammar-skip")' .claude/runtime/mcp-events.jsonl`), graphable, and CI-consumable. Silent-exit-code-only would be the failure mode the user named.
2. **CI scheduling (FR-4c, design-cicd-owned).** Weekly cron + on-change-to `.devcontainer/versions.env`. Removes the dependency on a human maintainer remembering to run the script. Design-cicd owns the wiring; this design states the CI dependency and the event-emission requirement.
3. **Optional runtime banner if last calibration event is stale (Q-CS-1's second half).** Currently NOT in the design — surfaced as Q-CS-1 for the composer to decide. The runtime banner would read the last `calibration_result` event from `mcp-events.jsonl` at `postCreate.sh` time and, if no event has been recorded in the last N weeks (e.g., 4), emit a `degraded` warning. This is a belt-and-suspenders defense against the script "quietly stopping running" if CI is disabled or broken. The composer chooses whether to add this; the design is forward-compatible with adding it later.

### Swift exclusion (preserved from v0.2.0)

The calibration script asserts NOTHING about Swift via this env-var. At v1.6.5 the env-var governs only dart and proto; Swift's non-build is governed by npm's `optionalDependencies` failure tolerance independently (T-001 F-4). This is documented in a comment at the head of the calibration script so a future maintainer reading it sees the rationale without re-reading T-001.

## FR-4c — CI wiring for the calibration script (design-cicd-owned; cross-layer handoff)

This sub-mechanism is **owned by `design-cicd`** in a parallel revision. Documented here only for cross-layer traceability. The Codespaces-layer contract that design-cicd's wiring must honor:

- The script lives at `.devcontainer/scripts/calibrate-gitnexus-grammar-skip.sh`.
- The script's contract is documented in the FR-4b section above.
- The script emits one event per run to `.claude/runtime/mcp-events.jsonl` (in-repo path; CI must persist the artifact or read it before the runner cleans up).
- The script's exit code is the secondary observability channel; the primary is the event.
- CI's two triggers: weekly cron AND on-change-to-`.devcontainer/versions.env`.
- CI must NOT bundle the calibration into the main FR-5 workflow's hot path — calibration is out-of-band by design.

design-cicd's design will spec the YAML for the workflow, the trigger paths, the artifact persistence, and how failures are surfaced (notification mechanism, PR comment, etc.).

## Acceptance criteria contribution

Per the EARS-format discipline:

- **AC-CS-FR-4a-1 (static-check sub-assertions):** When `.devcontainer/postCreate.sh` reaches the FR-4a block (between current line 197 and line 198), the system shall assert (A1) `$GITNEXUS_SKIP_OPTIONAL_GRAMMARS` equals the literal string `1`, AND (A2) `$GITNEXUS_TAG` matches `^v?[0-9]+\.[0-9]+\.[0-9]+(-[A-Za-z0-9.-]+)?$`, AND (A3) `$GITNEXUS_TAG` matches the value in `.devcontainer/versions.env`, AND (A4) `npm root -g` returns a non-empty path whose parent is writable.

- **AC-CS-FR-4a-2 (runs on every rebuild, equally cheaply):** When the codespace is created or rebuilt, the system shall execute the FR-4a static check on both cache-hit and cache-miss paths with no measurable cost difference between the two (since the check never invokes `npm install -g` and never depends on the gitnexus sentinel's presence).

- **AC-CS-FR-4a-3 (fail-closed before `install_gitnexus`):** If any of A1 / A2 / A3 / A4 fails, the system shall (i) emit a `structured_failure` event via `log_mcp_event` whose `note:` field names FR-4a, the failing sub-assertion, the observed value, and a one-line remedial hint, (ii) emit a plain-text operator diagnostic to stderr, and (iii) cause `postCreate.sh` to exit non-zero via `set -euo pipefail` BEFORE `install_gitnexus` is invoked.

- **AC-CS-FR-4a-4 (no Swift assertion):** The system shall not assert any condition about `tree-sitter-swift`'s build outcome as a function of `GITNEXUS_SKIP_OPTIONAL_GRAMMARS`, on the basis that at `gitnexus@1.6.5` the env-var does not govern Swift (per T-001 F-4).

- **AC-CS-FR-4a-5 (sentinel-less):** The FR-4a static check shall create no sentinel file and consult no sentinel of its own; its outcome is encoded only in the `structured_failure` event record (on fail) or in the silent green-light into `install_gitnexus` (on pass).

- **AC-CS-FR-4b-1 (calibration script contract):** When the maintainer or CI invokes `.devcontainer/scripts/calibrate-gitnexus-grammar-skip.sh` with no arguments, the system shall (i) read `GITNEXUS_TAG` from `.devcontainer/versions.env`, (ii) create a scratch directory via `mktemp -d`, (iii) install `gitnexus@${GITNEXUS_TAG}` into the scratch directory with `GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1` and stderr captured, (iv) assert Signal 1 (per-grammar stderr regex match for dart AND proto), (v) assert Signal 3 (artifact-path absence for both grammars), (vi) run the optional negative-assertion confirmation with `GITNEXUS_SKIP_OPTIONAL_GRAMMARS=0` in a second scratch dir and assert the artifacts ARE built (enabled by default), (vii) emit exactly one event to `.claude/runtime/mcp-events.jsonl` whose payload includes the `signals` map per the design's specified shape, and (viii) clean up the scratch directories before exit.

- **AC-CS-FR-4b-2 (event emission is the primary observability channel):** The calibration script shall emit one event per run to `.claude/runtime/mcp-events.jsonl` regardless of pass/fail/drift_detected outcome; the script's exit code shall be the secondary channel (0 on pass, non-zero on any signal failure).

- **AC-CS-FR-4b-3 (not invoked from postCreate.sh):** The system shall NOT invoke `.devcontainer/scripts/calibrate-gitnexus-grammar-skip.sh` from any path of `.devcontainer/postCreate.sh`. (The script's invocation is exclusively manual-by-maintainer OR via CI per FR-4c.)

- **AC-CS-FR-4b-4 (no Swift assertion):** The calibration script shall not assert any condition about `tree-sitter-swift`'s build outcome as a function of `GITNEXUS_SKIP_OPTIONAL_GRAMMARS`, on the basis stated in AC-CS-FR-4a-4.

- **AC-CS-FR-4c-1 (CI wiring is design-cicd-owned):** The CI workflow that schedules and triggers `.devcontainer/scripts/calibrate-gitnexus-grammar-skip.sh` shall be specified by the `design-cicd` layer's design document, not by this layer. (Cross-layer traceability anchor; see also the `provides_to: cicd` row in codespaces-dependencies.json.)

- **AC-CS-NFR-3-a (FR-4a static-check overhead bounded — REVISED):** When the FR-4a static check (sub-assertions A1 + A2 + A3 + A4 + event emission) runs on the Codespace's configured `hostRequirements.cpus: 4` machine class, the system shall complete the static check in under 100 milliseconds at p95 measured over 10 consecutive rebuilds. The measurement basis is rebuilds (any kind — cache-hit, cache-miss, fresh codespace) because FR-4a runs equally on all paths; there is no cache-vs-no-cache semantics.

- **AC-CS-NFR-3-b (FR-4b calibration script wall-clock — INFORMATIONAL):** When the calibration script is invoked manually or by CI, the system shall complete the full script (both scratch-dir installs + signal assertions + event emission + cleanup) in under 60 seconds wall-clock. NFR-3 does not constrain FR-4b's wall-clock (it does not run per-rebuild); this AC is documented for budget transparency only and is the maintainer's planning anchor for CI scheduling.

- **AC-CS-NFR-13-a (no new event types — REVISED in v0.3.0; PROSE-CORRECTED in v0.3.1):** When FR-4a emits a diagnostic, the system shall emit only events of types already defined in the `mcp-events.jsonl` schema per ADR-0037 v1.0.2 (`install_complete`, `readiness_probe`, `structured_failure`). When FR-4b emits a calibration result, the system shall use either (a) the new `calibration_result` event-type value (interpretation A; subject to Q-CS-1 composer confirmation that NFR-13 admits this extension; resolved in favor of A via ADR-0058) OR (b) the existing `install_complete` / `structured_failure` event-types with the `signals` map JSON-stringified into the `note:` field (interpretation B; strict NFR-13 read; rejected at composer arbitration).

- **AC-CS-NFR-7-a (no new credential surface):** Neither FR-4a nor FR-4b shall require any new environment variable, token, or credential beyond `GITNEXUS_TAG` (non-secret) and `GITNEXUS_SKIP_OPTIONAL_GRAMMARS` (non-secret).

- **AC-CS-NFR-8-a (no credential values in diagnostics):** Both FR-4a and FR-4b shall name the env-var key (`GITNEXUS_SKIP_OPTIONAL_GRAMMARS`) and the pinned tag (`GITNEXUS_TAG`), and shall not include the value of any environment variable identified as a credential carrier.

- **AC-CS-NFR-14-a (no other devcontainer-layer additions):** This feature shall add only (i) the FR-4a static-check block to the existing `postCreate.sh` between current line 197 and line 198 AND (ii) the new standalone script at `.devcontainer/scripts/calibrate-gitnexus-grammar-skip.sh`. No Features change, no Dockerfile change, no machine-class change, no port change, no prebuild adoption.

## Dependencies on other layers

- **Claude Code layer (FR-1 / FR-2 / FR-3 / FR-7).** Independent of FR-4. Neither FR-4a nor FR-4b produces an artifact those mechanisms care about. The only shared substrate is `.claude/runtime/mcp-events.jsonl` — and both mechanisms honor NFR-13 (FR-4a uses only existing event types; FR-4b's `calibration_result` extension is gated on Q-CS-1).

- **CI/CD layer (FR-5 + FR-4c).** FR-5's CI workflow runs against the devcontainer image (per synthesis D-0007). If FR-4a halts the install on a CI runner, FR-5's workflow's image-build step fails before claude is invoked, surfacing the static-shape drift in CI output. FR-4c (CI wiring of the FR-4b calibration script — weekly cron + on-change-to-`versions.env`) is owned by design-cicd; this design states the cross-layer handoff contract (script path, event-emission requirement, trigger paths).

- **Cross-cutting (FR-6 actionable diagnostics).** Both FR-4a's and FR-4b's diagnostics conform to FR-6's four-element template: mechanism name (FR-4a or FR-4b), offending artifact (env-var / pin / versions.env / npm root for FR-4a; the env-var contract at `GITNEXUS_TAG` for FR-4b), rule violated (one of the four FR-4a tokens OR one of the FR-4b signals), remedial hint. The structured `note:` field encodes all four. The dual-stream convention adopted here (plain-text echo + structured JSONL via `log_mcp_event`) is documented as the FR-4 instance; design-composer should verify this is the same dual-stream shape that the other named mechanisms surfacing diagnostics (notably FR-3 and FR-5) adopt.

- **No dependency on IaC layer.** No cloud auth needed in the codespace for either FR-4a or FR-4b.

- **No dependency on Frontend / Backend / API / Query / Database layers** — all out of scope per the PRD's Layer Scope.

## Architectural questions for Composer

- **Q-CS-1 (REFRAMED).** The v0.2.0 Q-CS-1 was about the immutable-upstream-tag assumption (whether a cached-rebuild path could safely skip the dry-run on the basis that npm tarballs are immutable in practice). The v0.3.0 design dissolves that question — FR-4a is static-only and runs on every rebuild equally cheaply, so there is no cached-vs-non-cached semantics for the per-rebuild check; FR-4b is out-of-band and CI-scheduled, so it does not depend on cache semantics either. The reframed Q-CS-1 has two sub-questions:
  - **Q-CS-1a (event-type extension; v0.3.1 prose-corrected).** Does NFR-13's "no new event types" admit a new `event:` value `calibration_result` for FR-4b's emission (interpretation A), or must FR-4b reuse the existing `install_complete` / `structured_failure` values (the on-disk vocabulary per ADR-0037 v1.0.2) with the `signals` map JSON-stringified into the `note:` field (interpretation B)? Recommended: A. Trade-off: A gives clean `jq` filtering for downstream consumers (FR-4c CI, future analytics) but extends the vocabulary; B preserves NFR-13 strictly but couples the calibration signal into a free-text field that downstream consumers must JSON-parse.
  - **Q-CS-1b (runtime staleness banner).** Should `postCreate.sh` read the last `calibration_result` event from `mcp-events.jsonl` at FR-4a-adjacent time and emit a `degraded` warning if no event has been recorded in the last N weeks (e.g., 4)? This is the belt-and-suspenders defense against the "calibration script quietly stops running" failure mode the user named. Adding the banner means a small amount of extra logic at `postCreate.sh` runtime; not adding it means the only observability channel is CI's own alerting (per FR-4c, design-cicd-owned). Recommended: yes, add the banner — the cost is ~10 lines of shell + one `jq` invocation per rebuild, and it directly defeats the user's named trap. Defer to composer.

- **Q-CS-2.** The dry-run is sentinel-less by design, per the synthesis directive against introducing a third sentinel format. The existing two-sentinel inconsistency (ADR-0041 canonical vs the live `postCreate.sh` form) remains untouched by this feature. The composer may want to surface this as a deferred issue (a follow-on cleanup) so future readers know the inconsistency was intentionally not resolved here. Recommended: yes, surface as a deferred row in `Issues/devcontainer-mcp-provisioning-r1-deferrals/register.md` if a row doesn't already exist; explicit-defer beats silent-defer. (Unchanged from v0.2.0.)

- **Q-CS-3.** The "5 vs 4 servers" cosmetic inconsistency in `postCreate.sh`'s head-comment (codebase-analysis known-issue row 3 — line 5 says "5 OSS-local MCP servers"; line 9 corrects to "(4 — post-2026-05-24 postmortem; was 5)"; line 158 says "4") is adjacent to FR-4's insertion site but not load-bearing for the design. The composer may want to fix the stray "5" in the FR-4 commit as a one-line housekeeping edit, or defer. Recommended: fix the stray "5" in line 5 of `postCreate.sh` in the same commit; it costs nothing and removes a future-reader hazard. (Unchanged from v0.2.0.)

- **Q-CS-4.** No prebuild is adopted by this run (per NFR-14 carve-out). If the composer has visibility into a pending org-level Codespaces policy that mandates prebuilds, surface here; otherwise the no-prebuild posture is forward-compatible with future adoption — both FR-4a (at `postCreateCommand`, uncaptured) and FR-4b (out-of-band of lifecycle) sit where prebuilds don't see them. (Unchanged from v0.2.0.)

- **Q-CS-5.** The U-6 PR-shape question (single bundled PR vs five sequenced) is cross-cutting and owned by design-composer per synthesis D-0008. From the Codespaces layer's view, the v0.3.0 change is larger than v0.2.0 (one helper function modification became one new top-level block + one new standalone script + a cross-layer handoff to design-cicd for FR-4c) but still single-file-plus-one-new-file; could ship in either PR shape with no Codespaces-layer impact. The synthesis flagged D-0008 for user confirmation. Defer to composer. (Unchanged from v0.2.0; restated for v0.3.0 scope.)

## Open items

- The calibration script (`.devcontainer/scripts/calibrate-gitnexus-grammar-skip.sh`) implementation (exact bash idiom for the per-grammar regex match, the `npm config set prefix` invocation under the script's subshell, the trap-based scratch-dir cleanup) is specified by contract above but not specified to the line. design-codespaces leaves the implementation detail to Plan Authoring; the contract (no arguments + reads versions.env + mktemp scratch + Signal 1 + Signal 3 + optional negative-assertion + event emission + cleanup) is fixed by AC-CS-FR-4b-1.

- The exact regex test for FR-4b — using `grep -E` with the regex string vs `bash`'s `[[ =~ ]]` operator — is an implementation detail. Plan Authoring picks; the assertion's behavior (match at least once for each of dart and proto) is fixed.

- The "10 consecutive rebuilds" sample-size for AC-CS-NFR-3-a is a measurement choice. If the test-author judges that 5 rebuilds are sufficient for a stable p95 (or that the assertion is fast enough that the threshold is uncontroversial), the sample size can be reduced; the 100-millisecond ceiling is the load-bearing number.

- Q-CS-1a's interpretation (A: new `calibration_result` event-type vs B: reuse `install_complete` / `structured_failure` with stringified `signals` in `note:` — v0.3.1 prose-corrected; v0.3.0 wrote `primary_degraded` here, which is a boolean sub-field of `structured_failure` rather than a distinct event type per ADR-0037 v1.0.2) is composer-decision. If the composer picks B, AC-CS-NFR-13-a's second sentence simplifies to "shall emit only events of types already defined" and the `signals` map's JSON-stringification idiom moves into the calibration script's implementation. If A, ADR-0037 may need a v-bump to formally admit the fourth event-type value (resolved in favor of A via ADR-0058 at composer arbitration).

- Q-CS-1b's staleness-banner question (yes/no/threshold-N) is composer-decision. If yes, Plan Authoring spec'd lines: read last `calibration_result` event timestamp from `mcp-events.jsonl`; compare to now - N weeks; if older, echo a `degraded` plain-text banner to stderr. No event emission for the banner itself (banners are already a logged-at-rebuild observability surface per existing convention).

## Citations

- **PRD §FR-4 + AC-FR-4-a/b/c** for the FR-4 acceptance contract.
- **PRD §NFR-3** for the latency budget (U-8 resolved at AC-CS-NFR-3-a; tighter threshold than v0.2.0 because the per-rebuild check is now static-only).
- **PRD §NFR-6** for fail-closed-on-internal-error posture (honored by FR-4a halting `postCreate.sh` via `set -euo pipefail` on static-check failure).
- **PRD §NFR-7/NFR-8** for credential discipline (AC-CS-NFR-7-a, AC-CS-NFR-8-a).
- **PRD §NFR-13** for the existing-event-types-only constraint (AC-CS-NFR-13-a; FR-4b's `calibration_result` extension is gated on Q-CS-1a).
- **PRD §NFR-14** for the no-other-devcontainer-layer-additions disclaimer (AC-CS-NFR-14-a).
- **PRD §U-4 / §U-8** for the resolved exit-code contract (FR-4a fail-closed via `set -euo pipefail`; FR-4b non-zero on signal failure) and the resolved latency threshold (100 ms for FR-4a; 60 s informational for FR-4b).
- **Synthesis §3 D-0006** for the Signal-1-AND-Signal-3 conjunction recommendation, the regex-over-literal recommendation, and the no-Swift-assertion rationale. (Now drives FR-4b's contract, not FR-4a's per-rebuild check.)
- **Synthesis §4** for the sentinel inconsistency structural finding and the "do not introduce a third sentinel format" directive.
- **T-001 F-1 / F-2** for the strict `=== '1'` env-var guard at `scripts/build-tree-sitter-dart.cjs` lines 5-14 and `scripts/build-tree-sitter-proto.cjs` lines 28-34 at `v1.6.5`. (Drives FR-4b's Signal 1 regex; informs FR-4a's A1 sub-assertion.)
- **T-001 F-3** for `npx node-gyp rebuild` invocation when the guard does not trip. (Drives FR-4b's optional negative-assertion path.)
- **T-001 F-4** for the Swift-vs-env-var divergence (README claims Swift coverage; v1.6.5 code only covers Dart + Proto; Swift is governed by npm `optionalDependencies` tolerance independently). (Drives no-Swift-assertion in both FR-4a and FR-4b.)
- **T-001 F-5** for the per-grammar artifact paths under `$(npm root -g)/gitnexus/node_modules/tree-sitter-{dart,proto}/build/Release/`. (Drives FR-4a's A4 sub-assertion and FR-4b's Signal 3 check.)
- **T-001 AC-3 DM-1** for the regex-over-literal mitigation against upstream wording drift. (Applies to FR-4b's Signal 1.)
- **T-001 AC-3 DM-4** for the calibration-check mitigation against future `=== '1'` loosening (drives FR-4b's optional negative-assertion confirmation, enabled-by-default).
- **T-001 Q-2** notes that issue #1024 is closed not-planned; the README-vs-code Swift divergence is therefore expected to persist; the design's no-Swift-assertion stance is forward-stable.
- **User direction at Gate-4 prep (2026-05-26).** The hybrid (option 3) split into FR-4a (per-rebuild static) + FR-4b (opt-in behavioral) + FR-4c (CI wiring, design-cicd-owned) is per verbatim user recommendation. The trap-avoidance discipline (event emission > exit code; CI scheduling > maintainer memory; optional runtime banner) is per the user's named warning about option 3 degrading into option 1 if the calibration script becomes maintainer-only-and-uninvoked.
- **Codebase Analysis components.`.devcontainer/postCreate.sh`** for the insertion site (FR-4a sits between current line 197 `install_terraform_mcp || …` and current line 198 `install_gitnexus || …`; the existing `gitnexus_post_install_warm` at line 201 does not collide), the `log_mcp_event` helper, the `set -euo pipefail` posture at script top.
- **Codebase Analysis conventions.codespaces** for the diagnostic dual-stream (plain-text echo + structured JSONL via `log_mcp_event`) discipline.
- **Codebase Analysis known_issues row 2** for the two-sentinel-format inconsistency (resolution: do not add a third — both FR-4a and FR-4b are sentinel-less).
- **Codebase Analysis known_issues row 3** for the "5 vs 4" cosmetic head-comment inconsistency (Q-CS-3).
- **ADR-0037** (v1.0.2 — the v0.3.1 codespaces-design refers to the corrected on-disk vocabulary) for the `mcp-events.jsonl` event schema (`install_complete`, `readiness_probe`, `structured_failure`). FR-4a emits only these. FR-4b proposes `calibration_result` as a new event-type value; resolved in favor of admission via ADR-0058 at composer arbitration.
- **ADR-0041 v1.0.1** for the existing MCP install placement at `postCreateCommand` (FR-4a sits inside this hook at top-level; FR-4b is out-of-band).
- **KB-codespaces-design principles.md** — Principle 1 (lifecycle hook strict order; FR-4a placement honors), Principle 2 (prebuilds capture some hooks not others; FR-4a's no-cache-vs-no-cache semantics make this principle non-load-bearing here), Principle 3 (only `/workspaces` persists; both FR-4a and FR-4b are sentinel-less), Principle 4 (machine class right-sizing; unchanged), Principle 5 (Codespaces Secrets discipline; no new secrets), Principle 6 (Features vs Dockerfile; unchanged), Principle 7 (port-forward explicit; unchanged), Principle 8 (dev env ≠ prod env; FR-4b's scratch-dir install is the discipline at work).
