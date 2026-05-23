---
id: research-note-T-003
topic: hongkongkiwi/actionlint-mcp MCP server
version: 1.0.0
status: draft
generated: 2026-05-23T00:00:00Z
generated_by: discovery-external-researcher
feature: devcontainer-mcp-provisioning-r1
research_plan_ref: /workspaces/feature-pipeline/working/feature/devcontainer-mcp-provisioning-r1/research-plan-v3.md
---

# T-003 — `hongkongkiwi/actionlint-mcp`

## Topic and question

**Topic:** `hongkongkiwi/actionlint-mcp` MCP server.

**Research question (verbatim):** Install / transport / tool surface / auth / version-pinning for `hongkongkiwi/actionlint-mcp`. Note the **dual-dependency wrinkle**: this MCP wraps the upstream `actionlint` binary (Go), so install must provide both the MCP wrapper AND the `actionlint` binary itself. Need install paths for both.

**KB-gap justification:** Vendor-specific; not covered in KB.

## Executive summary

The dual-dependency premise needs correction: `actionlint-mcp` does **not** shell out to an external `actionlint` binary. It imports `github.com/rhysd/actionlint` as a Go library and links it statically (pinned at `v1.7.7` in `go.mod` on `main`). At runtime only the single `actionlint-mcp` binary is required — no `actionlint` CLI, no `shellcheck`/`pyflakes` unless callers opt in via env vars.

However, the repository currently has **no tagged releases and no published release artifacts**, which breaks both the README's `install.sh` flow (it 404s when querying GitHub release assets) and any attempt to pin to a semver tag. For a no-Go-toolchain Debian-bookworm base image (`mcr.microsoft.com/devcontainers/python:1-3.11-bookworm`), this is a blocker: there is no maintainer-provided prebuilt Linux binary to download. Realistic provisioning options reduce to (a) installing a Go toolchain transiently to `go install ...@<commit-sha>`, (b) building from a Git checkout in a multi-stage manner, or (c) using the maintainer's Docker image (incompatible with the "no DinD" constraint). Transport is stdio. Tool surface is two tools (`lint_workflow`, `check_all_workflows`). No authentication.

## Findings

### F1 — `actionlint` is a Go-library dependency, not a runtime binary dependency

**Claim.** `actionlint-mcp` imports `github.com/rhysd/actionlint` as a Go module and uses its `NewLinter` API in-process; it does not invoke a separate `actionlint` executable. The dependency is therefore statically resolved at build time, not at runtime.

**Source.** `go.mod` and `main.go` at `github.com/hongkongkiwi/actionlint-mcp` (default branch `main`, fetched 2026-05-23). `go.mod` lists `github.com/rhysd/actionlint v1.7.7`; `main.go` contains `import "github.com/rhysd/actionlint"` and uses `actionlint.NewLinter(io.Discard, opts)` followed by `linter.Lint(filePath, content, nil)`.

**Quote (≤15 words).** "github.com/rhysd/actionlint v1.7.7" (from `go.mod`).

**Confidence.** High — primary source, examined directly.

**Caveats.** The `actionlint` version is whatever the MCP author has pinned in `go.mod`; consumers cannot independently upgrade it without rebuilding the MCP. As of inspection: pinned to `v1.7.7`, while upstream latest is `v1.7.12` (see F4). Optional features `shellcheck` and `pyflakes` *are* invoked as external binaries when configured (see F5).

### F2 — README's recommended install command depends on release assets that do not exist

**Claim.** The README advertises `curl -sSfL https://raw.githubusercontent.com/hongkongkiwi/actionlint-mcp/main/install.sh | sudo sh`. Inspection of `install.sh` shows it downloads from `https://github.com/hongkongkiwi/actionlint-mcp/releases/download/$VERSION/$FILENAME`, defaulting `$VERSION` to "latest" via the GitHub releases API. The repository's Releases page currently lists no releases ("There aren't any releases here"), so the script has no artifacts to download.

**Source.** `https://raw.githubusercontent.com/hongkongkiwi/actionlint-mcp/main/install.sh` and `https://github.com/hongkongkiwi/actionlint-mcp/releases` (fetched 2026-05-23).

**Quote (≤15 words).** "There aren't any releases here" (releases page).

**Confidence.** High — primary source.

**Caveats.** State may change; the maintainer could publish releases at any time. A Plan task should re-check the releases endpoint at execution time and fall back to source-build if still empty.

### F3 — `go install` is the only maintainer-documented install path that works today

**Claim.** Among the four install methods the README lists (install script, prebuilt binaries, `go install`, Docker), only `go install github.com/hongkongkiwi/actionlint-mcp@latest` does not depend on release assets. `go install` requires a Go toolchain at install time but produces a self-contained static binary that does not require Go at runtime.

**Source.** README at `github.com/hongkongkiwi/actionlint-mcp` (fetched 2026-05-23). Cross-referenced against the Go modules documentation behavior of `go install` for pinning a module at a commit or pseudo-version.

**Quote (≤15 words).** "go install github.com/hongkongkiwi/actionlint-mcp@latest" (README).

**Confidence.** High for the maintainer claim; high for the Go-toolchain-required interpretation.

**Caveats.** The target devcontainer base image (`mcr.microsoft.com/devcontainers/python:1-3.11-bookworm`) ships no Go toolchain. Provisioning therefore requires either (a) `apt-get install -y golang-go` (Debian-bookworm ships Go 1.19, which may or may not satisfy `go.mod`'s `go` directive — verify), (b) installing Go via the official devcontainer Go feature, or (c) a multi-stage build outside the Plan's stated single-image scope. Verification step: `cat go.mod | grep '^go '` to confirm minimum Go version.

### F4 — Underlying `actionlint` binary (only if needed standalone) installs via maintainer-provided download script

**Claim.** Although `actionlint-mcp` does not need an external `actionlint` binary, if the Plan separately wants `actionlint` as a CLI (for direct use, pre-commit hooks, or CI parity), `rhysd/actionlint` provides a no-Go-toolchain install via `bash <(curl https://raw.githubusercontent.com/rhysd/actionlint/main/scripts/download-actionlint.bash) <VERSION>`. The script accepts an optional positional version argument (e.g., `1.7.12`) and downloads from the GitHub Releases tarball pattern `https://github.com/rhysd/actionlint/releases/download/v<VERSION>/actionlint_<VERSION>_linux_amd64.tar.gz`. Latest stable as of 2026-03-30 is `v1.7.12`.

**Source.** `https://github.com/rhysd/actionlint/blob/main/docs/install.md` and the rhysd/actionlint releases page (fetched 2026-05-23).

**Quote (≤15 words).** "bash <(curl https://raw.githubusercontent.com/rhysd/actionlint/main/scripts/download-actionlint.bash) 1.6.17" (install docs).

**Confidence.** High — primary source, well-established release process.

**Caveats.** This binary is **optional** for `actionlint-mcp`'s operation. Installing it adds a second concern (drift between the version statically linked into the MCP and the version installed as CLI). Recommend installing only if the Plan explicitly needs the CLI.

### F5 — Transport is stdio; tool surface is two tools; no authentication

**Claim.** `actionlint-mcp` runs as a stdio MCP server invoked directly by the client (e.g., Claude Desktop launches `/usr/local/bin/actionlint-mcp` with no transport flags). It exposes exactly two tools: `lint_workflow` (parameters: `file_path` or `content` — lints a single workflow file or inline YAML) and `check_all_workflows` (parameter: optional `directory`, default `.github/workflows`). No authentication is required or accepted. Optional env vars `SHELLCHECK_COMMAND` and `PYFLAKES_COMMAND` let callers point the linter at external shellcheck/pyflakes binaries for deeper checks.

**Source.** README at `github.com/hongkongkiwi/actionlint-mcp` and the `lobehub.com/mcp/hongkongkiwi-actionlint-mcp` listing (third-party community reference, fetched 2026-05-23).

**Quote (≤15 words).** `"command": "/usr/local/bin/actionlint-mcp"` (README sample config).

**Confidence.** High for transport/tools/auth (confirmed by README sample config and lobehub listing); medium for the exact tool parameter schema (only the README is authoritative — schema may evolve).

**Caveats.** If the devcontainer wants shellcheck/pyflakes coverage, install `shellcheck` and `pyflakes` via apt (`apt-get install -y shellcheck` and `pip install pyflakes`) and set the env vars in the MCP client config. The MCP itself does not bundle them.

### F6 — Licensing is MIT

**Claim.** Both `hongkongkiwi/actionlint-mcp` and `rhysd/actionlint` are MIT-licensed.

**Source.** README footer of `actionlint-mcp` and standard repository LICENSE files (fetched 2026-05-23).

**Quote (≤15 words).** Not quoted (boilerplate license attribution).

**Confidence.** High.

**Caveats.** None.

## Synthesis (analysis)

Three actionable observations for the Plan author, marked explicitly as judgment:

1. **The "dual-dependency wrinkle" in the Research Plan is a false alarm.** Because `actionlint` is statically linked into `actionlint-mcp` at build time, the runtime image needs exactly one binary: `actionlint-mcp`. No separate `actionlint` binary, no Go toolchain at runtime. Plan task wording that assumes "install both" should be revised.

2. **The single hard constraint is "no maintainer-published Linux binary exists today."** This eliminates the README's headline install path on a no-Go base image. The pragmatic choices, in decreasing order of operational simplicity:
   - **(a) Multi-stage devcontainer build** (Go builder stage → copy compiled binary into the Python runtime stage). Clean, reproducible, no Go toolchain in the final image. Requires Dockerfile changes; the Plan must confirm this is in scope.
   - **(b) Transient Go install in postCreate** (`apt-get install -y golang-go && go install github.com/hongkongkiwi/actionlint-mcp@<commit-sha> && apt-get remove -y golang-go`). Single-image, but adds ~600 MB during install and depends on Debian-bookworm's Go version satisfying `go.mod`. Verify `go.mod`'s `go` directive first.
   - **(c) Wait for / request upstream releases.** Lowest-effort once available; not actionable today.
   - **(d) Vendor a pre-built binary into the repo.** Discouraged: violates "authoritative source" hygiene and creates a maintenance burden.

3. **Version-pinning must be by commit SHA, not semver tag.** Because no tags exist, `go install github.com/hongkongkiwi/actionlint-mcp@<commit-sha>` (or `@<pseudo-version>`) is the only deterministic pin available. Document the chosen SHA in the Blueprint and the Plan; treat moves of `main` as supply-chain events requiring re-review. Optionally also pin Go modules with `GOFLAGS=-mod=mod` plus checksums via `go.sum` if the source-build approach is chosen.

## Acceptance-criteria check

| Criterion | Disposition | Reasoning |
|---|---|---|
| Install command for the MCP wrapper | **Satisfied with caveats.** README's `install.sh` is broken today (F2). The recommended actionable install is `go install github.com/hongkongkiwi/actionlint-mcp@<commit-sha>` from a Go builder stage or a transient `golang-go` apt install (F3, Synthesis #2). |
| Install command for `actionlint` binary on Debian-bookworm without Go toolchain | **Satisfied but reframed.** No separate `actionlint` binary is needed for `actionlint-mcp` to function (F1). If the Plan also wants the CLI independently, use `bash <(curl https://raw.githubusercontent.com/rhysd/actionlint/main/scripts/download-actionlint.bash) 1.7.12` (F4). |
| Transport recommendation | **Satisfied.** stdio (F5). |
| Tool surface | **Satisfied.** `lint_workflow`, `check_all_workflows` (F5). |
| Auth (likely none) | **Satisfied.** No authentication required (F5). |
| Version-pinning for BOTH the wrapper AND the binary | **Partially satisfied.** Wrapper: by Git commit SHA only (no tags exist — F2/F3/Synthesis #3). Underlying actionlint library: pinned in MCP's `go.mod` at `v1.7.7` (F1). Standalone CLI (if installed): pinnable by `vX.Y.Z` tag via download script (F4). |
| ≥3 independent reputable sources | **Satisfied.** (1) `hongkongkiwi/actionlint-mcp` repo (primary, including README, `install.sh`, `go.mod`, `main.go`, releases page). (2) `rhysd/actionlint` repo and docs (upstream library/CLI, primary). (3) `lobehub.com/mcp/hongkongkiwi-actionlint-mcp` listing (third-party community reference). |

## Open questions

1. **Will the maintainer publish tagged releases?** Filing or watching an issue may be worth a footnote in the Plan. Until then, SHA pinning is mandatory.
2. **Does Debian-bookworm's `golang-go` (Go 1.19) satisfy `actionlint-mcp`'s `go.mod` minimum?** Verify at execution time with `go mod download` against the chosen commit. If not, use the Go feature/golang.org tarball install path instead of apt.
3. **Does the Plan want the standalone `actionlint` CLI in addition to the MCP?** If pre-commit hooks or CI workflows in this repo invoke `actionlint` directly, yes; otherwise, no — keep the image lean.
4. **Are shellcheck and pyflakes in scope for richer linting?** F5 documents the integration points but the Plan should make this an explicit yes/no.

## Source list

1. **hongkongkiwi/actionlint-mcp** — `https://github.com/hongkongkiwi/actionlint-mcp` (README, `install.sh`, `go.mod`, `main.go`, Releases tab). Maintainer: hongkongkiwi. License: MIT. Default branch `main`. Fetched 2026-05-23.
2. **rhysd/actionlint** — `https://github.com/rhysd/actionlint` and `https://github.com/rhysd/actionlint/blob/main/docs/install.md`. Maintainer: rhysd (Linda_pp). License: MIT. Latest stable: v1.7.12 (2026-03-30). Fetched 2026-05-23.
3. **Lobehub MCP marketplace listing** — `https://lobehub.com/mcp/hongkongkiwi-actionlint-mcp` (redirects to `https://market.lobehub.com/s/plugins/hongkongkiwi-actionlint-mcp`). Third-party MCP server directory. Fetched 2026-05-23.
