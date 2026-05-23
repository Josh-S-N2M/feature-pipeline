# Verify-at-Execution Log — devcontainer-mcp-provisioning-r1

Per Plan §H and tasks.json `verify_at_execution_tasks`. This file aggregates the seven §H verify-at-execution items (T0.1–T0.7) plus the §D-2 placeholder convention (T0.8), §D-4 Go pin (T0.9), and §OI-4 measurement (T4.7). Each section is authored by its owning task.

**Status:** initialized 2026-05-23T03:25:00Z by execute-orchestrator as Phase 0 dispatch substrate.

---

## §H-2 — Terraform MCP version pin (T0.1)

**Verified at:** 2026-05-23 (execution slot, single-agent-fallback mode)
**Source:** `https://api.github.com/repos/hashicorp/terraform-mcp-server/releases` and `https://releases.hashicorp.com/terraform-mcp-server/0.5.2/`.

**Decision: pin `TERRAFORM_MCP_VERSION=0.5.2`** (default per Plan §H-2 / tasks.json T0.1; latest stable as of 2026-05-23; published 2026-04-28).

**Release-tarball SHA256 (linux_amd64 — the architecture this devcontainer targets):**

```
d9e7c52ed7963444c6b4c65e9066f3163d700cb676a28dd418216885f37689ed  terraform-mcp-server_0.5.2_linux_amd64.zip
```

Other supported architectures from the same SHA256SUMS manifest, for the install script's optional arch-dispatch:

| Arch | SHA256 |
|---|---|
| linux_amd64 | `d9e7c52ed7963444c6b4c65e9066f3163d700cb676a28dd418216885f37689ed` |
| linux_arm64 | `8cc9065e53488ba9a93e69f41cc5669989189f7f40a556b27a45994fb695a994` |
| darwin_amd64 | `83ea101b2489ba1c2553ac5c50cbc595652cf06052528113ac41146d2361932d` |
| darwin_arm64 | `483bababb8e10ceeb4d8bcbb1728789c39f5e596ad0c6e09d6679c127d0b8fc9` |

**GPG verification-key fingerprint (HashiCorp well-known signing key):**

```
C874 011F 0AB4 0511 0D02 1055 3436 5D94 72D7 468F
```

Equivalent un-spaced form: `C874011F0AB405110D02105534365D9472D7468F`. Published at `https://www.hashicorp.com/security` and `https://apt.releases.hashicorp.com/gpg`.

**Verification artifacts T3.3 will reference:**

- Download URL: `https://releases.hashicorp.com/terraform-mcp-server/0.5.2/terraform-mcp-server_0.5.2_linux_amd64.zip`
- SHA256SUMS: `https://releases.hashicorp.com/terraform-mcp-server/0.5.2/terraform-mcp-server_0.5.2_SHA256SUMS`
- SHA256SUMS.sig: `https://releases.hashicorp.com/terraform-mcp-server/0.5.2/terraform-mcp-server_0.5.2_SHA256SUMS.sig`
- Public key file: `https://apt.releases.hashicorp.com/gpg`

**Informs:** T1.3 (`.devcontainer/versions.env` → `TERRAFORM_MCP_VERSION=0.5.2`); T3.3 (`.devcontainer/install/terraform-mcp.sh` — wget tarball + SHA256SUMS + SHA256SUMS.sig; `sha256sum -c`; `gpg --verify`).

**Recorded by:** execute-orchestrator (single-agent-fallback) at 2026-05-23T18:07 UTC.

---

## §H-1 — actionlint-mcp commit SHA selection (T0.2)

**Verified at:** 2026-05-23 (execution slot, single-agent-fallback mode).

### Verify-at-execution finding: upstream-identifier drift in design artifacts

The Plan §H-1 step, tasks.json T0.2, and `cc-dependencies.json` all refer to `github.com/2manymws/actionlint-mcp`. **That repository returns HTTP 404** at https://github.com/2manymws/actionlint-mcp (probed 2026-05-23T18:08 UTC). The org `2manymws` exists (bio: "HTTP middleware handlers and related packages for Go") but lists 7 public repos none of which match `actionlint-mcp`.

The **PRD-normative** identifier is **`hongkongkiwi/actionlint-mcp`** — this is the identifier carried in:

- `prd-v2.md` line 280: *"`hongkongkiwi/actionlint-mcp`"*
- `prd-v2.md` line 588: same
- `research-plan-v3.md` IN-013 and T-003: same
- `codebase-analysis.json` (consumer-mapping entries): `actionlint-mcp` (no org prefix)
- (Carried through `prd-v3.md` and `blueprint-v3.md` consistent with v2)

`github.com/hongkongkiwi/actionlint-mcp` resolves cleanly (probed same time). It is a functional MCP server: README declares `lint_workflow` + `check_all_workflows` tools; stdio transport via `mcp.json`; Go-built binary. Repository contents include `mcp.json`, `main.go`, `Dockerfile`, `install.sh`, releases per `.goreleaser.yml`. Confirms the design's intent.

**Conclusion:** The reference `2manymws/actionlint-mcp` in Plan §H-1 / tasks.json T0.2 / cc-dependencies.json is a propagation drift (a defect parallel to the earlier `design-cc.md` vs `design-claude-code.md` drift fixed at reconciliation cycle 2). The correct upstream is `hongkongkiwi/actionlint-mcp`. PRD remains authoritative.

**Disposition:** Use `hongkongkiwi/actionlint-mcp`. Surface this propagation finding to phase-quality-review for downstream-artifact correction (T1.3 doesn't embed the org path — it pins `ACTIONLINT_MCP_SHA` only — so versions.env is unaffected; T3.2/T3.4 install paths will need to point at the corrected upstream; this is a finding for the reconciler when Phase 0 quality review fires).

### Commit-SHA pin selection

Default branch: `main`. Commit list (per `api.github.com/repos/hongkongkiwi/actionlint-mcp/commits`):

| SHA (12-char) | Date | Age | Eligible (≥14d)? | Subject |
|---|---|---|---|---|
| `7441fe042c99` | 2025-08-11T05:01:15Z | 285 days | ELIGIBLE | Add comprehensive CI/CD pipeline with GitHub Actions |
| `851240887453` | 2025-08-10T17:37:20Z | 286 days | ELIGIBLE | Initial Commit |

**Decision: pin `ACTIONLINT_MCP_SHA=7441fe042c995cbb1bb4b97fce71f9ed3b36d5ef`** (12-char short: `7441fe042c99`). Confirmed by `api.github.com/repos/hongkongkiwi/actionlint-mcp/commits` 2026-05-23T18:10 UTC.

Both commits satisfy the ≥14-day staleness rule (the rule guards against transient repo-state). Selecting the newer (HEAD of `main`) maximizes test-coverage signals (the CI/CD pipeline commit landed AFTER initial commit).

**Caveat surfaced to phase-quality-review:** The repo has only 2 commits as of 2025-12-08 (last push). This is a low-activity supply-chain anchor — operationally consistent with the design's `STALE_PACKAGE`-tolerant posture (cf. §H-3 mcp-openapi-schema pattern), but worth recording.

**Install pattern (informs T3.2 / T3.4):** Plan referenced `go install` for actionlint-mcp. The README also offers a pre-built binary install via `curl -sSfL https://raw.githubusercontent.com/hongkongkiwi/actionlint-mcp/main/install.sh`. Per ADR-0041 supply-chain reproducibility, **prefer `go install github.com/hongkongkiwi/actionlint-mcp@7441fe042c99...`** with explicit SHA pin (avoids dependency on `install.sh` evolution).

**Informs:** T1.3 `versions.env` (`ACTIONLINT_MCP_SHA=7441fe042c99…`); T3.2 / T3.4 install paths (use `hongkongkiwi/` not `2manymws/`).

**Recorded by:** execute-orchestrator (single-agent-fallback) at 2026-05-23T18:09 UTC.

---

## §H-3 — mcp-openapi-schema staleness disposition (T0.3)

**Verified at:** 2026-05-23T18:10 UTC (execution slot).
**Source:** `https://registry.npmjs.org/mcp-openapi-schema`.

| Field | Value |
|---|---|
| Package name | `mcp-openapi-schema` |
| `dist-tags.latest` | `0.0.1` |
| First published | 2025-03-13T13:40:12.245Z |
| Last modified | 2025-03-13T13:40:12.649Z |
| Versions on registry | 1 (only `0.0.1`) |

**No releases after 2025-03-13.** The package remains exactly as the design described.

**Decision: pin `MCP_OPENAPI_SCHEMA_VERSION=0.0.1` with `STALE_PACKAGE` annotation per Plan §H-3.**

**Integrity material for T2.4 (.mcp.json) and T3.4 (postCreate install via `npx`):**

- Tarball: `https://registry.npmjs.org/mcp-openapi-schema/-/mcp-openapi-schema-0.0.1.tgz`
- shasum (SHA-1): `a812c0d8ce5614610d66bec41229b808af98cd48`
- integrity (SHA-512 SRI): `sha512-GyrnLOEBf85JXvXLpml4s2SGkcJ3Ixk32HwrM8LkuevVsBpnipntN4Bdm1iepzZoiVwWiIEOFPdWO+p17rz7RQ==`
- bin: `mcp-openapi-schema` → `index.mjs`
- fileCount: 5, unpackedSize: 31171 bytes

**STALE_PACKAGE annotation rationale:** unchanged since 2025-03-13 (over 13 months at execution slot 2026-05-23). The design's Q-3 closure preserves this server in the 7-entry inventory; the staleness is a known posture, not a defect.

**Informs:** T1.3 (`MCP_OPENAPI_SCHEMA_VERSION=0.0.1` + STALE_PACKAGE comment); T2.4 (`.mcp.json` entry uses `npx mcp-openapi-schema@0.0.1` with integrity check via package-lock).

**Recorded by:** execute-orchestrator (single-agent-fallback) at 2026-05-23T18:10 UTC.

---

## §H-4 — GitNexus GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1 smoke-test (T0.4)

> **HIGH forgetting-risk.** Load-bearing for AC-CS-9. STOP-and-re-plan failure handling per Plan §H-4.

**Verified at:** 2026-05-23T18:15 UTC (execution slot, single-agent-fallback mode).

### STOP-AND-RE-PLAN CONDITION — Category-error in design's install method

The design (Plan §H-4, tasks.json T0.4, cc-design.md line 140, blueprint-v3.md lines 161/855) specifies the GitNexus install method as:

```
GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1 uvx --from gitnexus@<TAG> gitnexus --help
```

**This is incorrect at a category level.** `uvx` is the Python (`uv`) tool installer. `gitnexus` is **not** a Python package — `https://pypi.org/pypi/gitnexus/json` returns HTTP 404. There is no `gitnexus` on PyPI under any spelling probed (`gitnexus`, `gitnexus-mcp`, `git-nexus`, `mcp-gitnexus` all 404).

GitNexus is a **TypeScript / Node.js** project distributed on **npm**:

- npm registry: `https://registry.npmjs.org/gitnexus` returns HTTP 200.
- Package metadata: `name: gitnexus`, `dist-tags.latest: 1.6.5` (published 2026-05-16T16:32:36 UTC), 51 stable releases, 339 total (including `1.6.6-rc.*` prereleases).
- Upstream repo `abhigyanpatwari/GitNexus` is TypeScript: `package.json` exists at repo root; no `pyproject.toml`, no `setup.py`, no `setup.cfg`. README's CLI install line is `npm install -g gitnexus` (verbatim).
- README's official line for the env-var: *"set `GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1` before `npm install -g gitnexus` to skip vendored grammar materialize/build (`tree-sitter-dart`, `tree-sitter-proto`, `tree-sitter-swift`). Dart/Proto/Swift files won't be parsed, but install completes in seconds without `python3`/`make`/`g++`. **Strict `=1` only** — any other value falls through to the rebuild."*
- README's recommended Claude Code wiring: `claude mcp add gitnexus -- npx -y gitnexus@latest mcp` (i.e., `npx`, not `uvx`).

The `GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1` env-var **is** still respected at execution slot 2026-05-23 — but it gates the **npm install** path, not a Python install path. The design's category was wrong; the env-var semantic is intact.

### Smoke-test result

The literal smoke-test as specified in Plan §H-4 (`uvx --from gitnexus@<TAG> gitnexus --help`) cannot succeed because `gitnexus` has no PyPI entry. In this devcontainer (`uvx`/`uv` not installed; no Docker available for a scratch container) the literal verification command also cannot be run.

A **functionally-equivalent** verification path would be:

```bash
GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1 npx -y gitnexus@1.6.5 --help
```

with verification that no C++ toolchain (`cc`, `g++`, `cargo`) enters the process tree. This was **not run** in this execution slot because the design's downstream `.mcp.json` / `versions.env` / `postCreate.sh` shape assumes `uvx`; re-running with `npx` would commit the orchestrator to a corrective form that the design has not approved.

### Latest stable version visible at execution slot

| Tag | Published | Prerelease? |
|---|---|---|
| `v1.6.5` (npm `1.6.5`) | 2026-05-16T16:32 UTC | No (npm `latest`) |
| `v1.6.4` (npm `1.6.4`) | 2026-05-10T08:03 UTC | No |
| `v1.6.6-rc.47` (npm `1.6.6-rc.47`) | 2026-05-23T08:11 UTC | Yes |

For pinning: **`GITNEXUS_TAG=1.6.5`** (latest stable) is the natural choice, but the pin form must be confirmed once the install-method correction is approved.

### Disposition

**Per Plan §H-4: STOP-and-re-plan.** The "env-var still respected" sub-condition checks out (the env-var works for npm), but the **install method itself is a category error** in the upstream design. Specifically:

- `versions.env` `GITNEXUS_TAG` semantic remains valid (just a version string).
- `cc-design.md` line 140 `command: "uvx"`, args `["--from", "git+https://github.com/abhigyanpatwari/GitNexus@<PIN_TAG>", "gitnexus", "serve"]` → must be `command: "npx"`, args `["-y", "gitnexus@${GITNEXUS_TAG}", "mcp"]` (per README's claude-code section).
- `postCreate.sh` (T3.4) install line for gitnexus must be `npm install -g gitnexus@${GITNEXUS_TAG}` (with `GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1` exported beforehand) — not `uvx`-based.
- Blueprint v3 §161/§855 install rows for gitnexus need correction.
- Plan §H-4 smoke-test command needs correction.

This finding is **load-bearing for AC-CS-9**: AC-CS-9 (per acceptance-tests.md, the GitNexus skip-grammars compliance check) currently presumes the `uvx` install. The AC's intent is "the cold-cache devcontainer build doesn't need a C++ toolchain because we skip optional grammars" — that intent is preserved under the `npm`-based install (the README explicitly documents this benefit) — but the AT test predicate referencing `uvx` must be updated.

**Recorded by:** execute-orchestrator (single-agent-fallback) at 2026-05-23T18:15 UTC.

### Phase 0 RE-VERIFY (post-cycle-3 reconciliation) — 2026-05-23T21:10 UTC

**Verified by orchestrator (parent recipe-feature-pipeline) using npm 11.13.0 + Node v24.16.0 in the current devcontainer.**

**Probe steps:**
1. `npm view gitnexus@1.6.5 dist.tarball name version` → confirmed package exists; tarball at `https://registry.npmjs.org/gitnexus/-/gitnexus-1.6.5.tgz`.
2. `export GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1 && npm install --prefix /tmp/gitnexus-smoke gitnexus@1.6.5` → exit 0; **57 seconds**; 287 packages added; no compile errors; only `npm warn deprecated boolean@3.2.0` (unrelated transitive).
3. `find /tmp/gitnexus-smoke/node_modules -name "*.node"` → all `.node` files live under `prebuilds/linux-x64/` (e.g., `tree-sitter/prebuilds/linux-x64/tree-sitter.node`, `tree-sitter-rust/prebuilds/linux-x64/tree-sitter-rust.node`, `tree-sitter-java/prebuilds/linux-x64/tree-sitter-java.node`). **Zero fresh compilation** during install (`find ... -newer` returned empty).
4. `grep -rn "GITNEXUS_SKIP_OPTIONAL_GRAMMARS" node_modules/gitnexus/` → confirmed env-var is read by `node_modules/gitnexus/dist/cli/optional-grammars.js` lines 6, 27, 85. The mechanism is gitnexus's postinstall script that skips OPTIONAL grammars (Dart/Proto/Swift per upstream README) when the env-var is set; the CORE grammars (Python, TypeScript, etc.) ship with `prebuilds/` for common architectures so they require no local compilation.
5. `timeout 3 /tmp/gitnexus-smoke/node_modules/.bin/gitnexus mcp < /dev/null` → MCP server started; emitted `{"level":40,"name":"gitnexus","msg":"GitNexus: No indexed repos yet. Run gitnexus analyze..."}`. Exit 124 (our `timeout` kill — server started successfully and was running until we killed it).
6. `/tmp/gitnexus-smoke/node_modules/.bin/gitnexus --version` → `1.6.5`.

**Result: PASS.** AC-CS-9 wrapping intent verified:

- On x86_64-linux Codespaces (the canonical target architecture), tree-sitter packages ship `prebuilds/linux-x64/*.node` so npm install requires no C++ toolchain run, even though `cc`/`g++`/`make` ARE present on this devcontainer (`/usr/bin/cc`, `/usr/bin/g++`, `/usr/bin/make` all installed by base Debian image).
- `GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1` is recognized and honored by gitnexus's postinstall script per the source code grep above. It skips OPTIONAL grammars (those without prebuilds for current arch); on x86_64-linux the optional set is small.
- On exotic architectures (e.g., arm64-linux without prebuild availability), if a tree-sitter package lacks a prebuild, gitnexus's postinstall WOULD attempt compilation; the env-var prevents that by skipping those optional grammars (with a runtime warning per `cliWarn` in `optional-grammars.js:85`).

**Acceptable to proceed to Phase 1+**: yes. The cycle-3 design corrections (uvx→npx; `npm install -g gitnexus@${GITNEXUS_TAG}` install form) are validated against actual upstream behavior. AC-CS-9 holds.

**Caveat for future reference:** the "no C++ toolchain at cold-cache" guarantee depends on tree-sitter prebuild availability for the host architecture. If a future Codespace targets an architecture without prebuilds, gitnexus would fall back to source builds for optional grammars — which the env-var skips. The env-var is the safety net; the prebuilds are the happy path.

---

## §H-5 — Context7 v3.0.0 tool surface + auth flag re-validation (T0.5)

> **REVISED** at reconciliation cycle 3 (D-3.2 / F3). The original H-5 framing referenced a non-existent **Context7 v1.2.0** with a fabricated `ReplaceContentTool` rename (contamination from Serena's v1.2.0 CHANGELOG). The corrected target version is **v3.0.0** (npm `@upstash/context7-mcp@3.0.0`, published 2026-05-22T16:20Z; current `dist-tags.latest` at execution slot 2026-05-23).

**Status:** stub — content-pending. Design-composer authored this stub during cycle-3 reconciliation to frame the v3.0.0 verification work; execute-orchestrator (or the operator running Phase 0 verify-at-execution) fills the section when execution resumes.

### What this section must record when filled

The execute-orchestrator (or operator) runs the live verification and records, with timestamps:

1. **Tool surface confirmation.** Live probe of `@upstash/context7-mcp@3.0.0` (e.g., `npx -y @upstash/context7-mcp@3.0.0 --help`, OR npm registry metadata fetch, OR `claude mcp ping context7` against the remote HTTP endpoint). Enumerate the **exact tool names** the server exposes at v3.0.0. The design-composer's cycle-3 reconciliation refresh of `research-notes/T-005-context7.md` (v2.0.0) anchors on a **two-tool surface** (`resolve-library-id` + `query-docs`) corroborated multi-source — the live probe confirms or refutes this.

2. **Auth-surface confirmation.** SF-F3-AUTH-HEADER-1 RESOLVED at cycle-3 D-3.2-completion: canonical form is `CONTEXT7_API_KEY: <value>` (literal header name) per GitHub README verbatim quote in T-005 v3.0.0 ("pass your API key via the `CONTEXT7_API_KEY` header"). Design artifacts patched to canonical form per user disposition. The live probe should:
   - Verify `CONTEXT7_API_KEY: <value>` header is accepted by the v3.0.0 hosted endpoint.
   - Confirm no fallback to `Authorization: Bearer ${CONTEXT7_API_KEY}` is required (the non-canonical form may or may not still work; cycle-3 chose the canonical form regardless).

   If the canonical form unexpectedly fails at probe time, surface as a new finding and re-evaluate.

3. **HTTP endpoint stability confirmation.** Confirm `https://mcp.context7.com/mcp` resolves and accepts the auth header. (Per T-005 v1.0.0 F1, the endpoint has been stable across v1→v3.)

4. **Stateful-session-state operator impact (OQ-T005-3 / SF-F3-RESIDUAL-2).** v3.0.0's release notes mention "Redis-backed session management." Briefly characterize whether a Codespace restart loses session state in a way that affects always-on use. If irrelevant (remote HTTP transport delegates session state to the vendor; local fallback only loses state if explicitly stopped), record that disposition.

### Sub-findings flagged by design-composer (cycle-3 refresh of T-005)

- **SF-F3-RESIDUAL-1 (cycle-3 → cycle-4):** Live WebFetch was NOT executed during cycle-3 reconciliation because the design-composer's `allowed-tools` set does not include WebFetch. The composer relied on T-005 v1.0.0 multi-source corroboration + the dispatch log's documented npm probe. Cycle-4 audit (or this §H-5 fill) provides the live verification.
- **SF-F3-RESIDUAL-2 (cycle-3 → cycle-4):** Redis-backed session-state operator-facing impact is OQ-T005-3 carried forward. Characterize when this §H-5 is filled; surface to cycle-4 audit if anything affects acceptance-tests semantics.
- **SF-F3-AUTH-HEADER-1 (RESOLVED at cycle-3 D-3.2-completion):** Canonical Context7 auth-header confirmed via orchestrator WebFetch — GitHub README verbatim: *"pass your API key via the `CONTEXT7_API_KEY` header"*. Per user disposition at cycle-3 D-3.2-completion, all design artifacts patched to use the canonical `CONTEXT7_API_KEY: <value>` header literal (NOT `Authorization: Bearer ${CONTEXT7_API_KEY}`). Cycle-4 audit verified consistency; cycle-4 mechanical-edit cleanup patched the remaining stale references in this §H-5 + PV-0.C6 + cc-design row 4 narrative. The live probe (when this §H-5 is filled at execution time) need only confirm the canonical header is accepted by the v3.0.0 endpoint.

### Disposition pending fill

Once filled, this section informs:
- **T2.4** (`.mcp.json` Context7 entry): confirm header name matches the v3.0.0 vendor-canonical form.
- **T4.1** (8 agent allowlist edits): confirm `discovery-external-researcher` Context7 tool entries `mcp__context7__resolve-library-id` + `mcp__context7__query-docs` match the live v3.0.0 tool surface verbatim.
- **PV-0.C6 / PV-4.C5** (phase-validators) re-anchoring per cycle-3 D-3.4.
- **acceptance-tests.md AC-CS-* / AT-* entries that name Context7 tools** per cycle-3 D-3.3.

**Recorded by:** design-composer (cycle-3 reconciliation, stub-only) at 2026-05-23T19:50 UTC. Stub authored; live verification deferred to execute-orchestrator Phase 0 re-run after cycle-3 dispatches complete.

### Live verification fill (cycle-3 D-3.2-completion + Phase 0 re-verify) — 2026-05-23T21:00 UTC

**Performed by:** orchestrator (parent recipe-feature-pipeline) using WebFetch + Bash curl.

**Verification matrix:**

| Item | Method | Result |
|---|---|---|
| v3.0.0 published reality | `curl https://registry.npmjs.org/@upstash/context7-mcp/latest` | **CONFIRMED** — `"version": "3.0.0"`, tarball SHA-256 `rwSFWlJe71q2FgJDfddg5Wh4+LCvEKP89bW6AKOl/hLgbRJiJLULbIXru79ubVAuIBdw5ncNHA0A2RPcHzc/Tg==`, _npmUser `fahreddin.ozcan` (verified Upstash maintainer), tarball at `https://registry.npmjs.org/@upstash/context7-mcp/-/context7-mcp-3.0.0.tgz` |
| Tool surface enumeration | GitHub `upstash/context7` README + npm-bundled CHANGELOG at `packages/mcp/CHANGELOG.md` | **CONFIRMED** — two tools: `resolve-library-id` AND `query-docs` (CHANGELOG v2.2.5: "on `query-docs`"; v2.2.4: "the `query-docs` MCP tool"). `get-library-docs` (D-3.2's in-repo conclusion) was WRONG; corrected to `query-docs` via 16-site patch across 8 files. |
| `ReplaceContentTool` claim | Cross-check vs Context7 CHANGELOG | **DEBUNKED** — does NOT exist in any Context7 version. The claim was contamination from Serena v1.2.0 CHANGELOG entry (per `research-notes/T-001-serena.md:82`). Cycle-3 D-3.2 retired this from active design. |
| Canonical auth header form | GitHub `upstash/context7` README quote | **CONFIRMED** — *"pass your API key via the `CONTEXT7_API_KEY` header"* (literal header name `CONTEXT7_API_KEY`, NOT `Authorization: Bearer`). SF-F3-AUTH-HEADER-1 RESOLVED per user disposition at cycle-3 D-3.2-completion; all design artifacts patched to canonical form. |
| HTTP endpoint stability | GitHub README + T-005 v1.0.0 F1 | **CONFIRMED stable** — `https://mcp.context7.com/mcp` documented for v3.0.0 (same endpoint as v1.x/v2.x per T-005). |
| v3.0.0 architectural change (Redis) | Context7 CHANGELOG v3.0.0 entry | "Convert the stateless MCP implementation to a stateful one using Redis for session management." **No design impact** for this feature — we use the hosted endpoint where Redis is Upstash's concern; we do NOT self-host the npm package. SF-F3-RESIDUAL-2 RESOLVED. |

**Disposition: PASS.** All three downstream consumers (T2.4 .mcp.json, T4.1 agent allowlist, PV-0.C6 / PV-4.C5 / PV-2.C17 validators) reflect verified v3.0.0 facts. The acceptance-tests.md AT entries are abstraction-level (server-name + env-var only) so they were NO-OP under cycle-3 D-3.3.

**At-execution probe still required**: when postCreate runs, T3.4 should still issue a JSON-RPC `tools/list` ping against `https://mcp.context7.com/mcp` with header `CONTEXT7_API_KEY: ${CONTEXT7_API_KEY}` and confirm the response includes exactly the two-tool surface. If the upstream evolves between now (2026-05-23) and the next execution slot, this probe detects the drift.

**Recorded by:** orchestrator (parent recipe-feature-pipeline; D-3.2-completion + Phase 0 re-verify drive).

---

## §H-6 — `claude mcp ping` CLI presence confirmation (T0.6)

**Verified by:** orchestrator (parent), 2026-05-23T21:15 UTC, in this devcontainer.

**Probe:**

```
$ claude --version
(version not captured; binary at /usr/local/share/nvm/versions/node/v24.16.0/bin/claude — Claude Code CLI present)

$ claude mcp ping --help
Usage: claude mcp [options] [command]
  Configure and manage MCP servers
  Commands:
    add ...
    add-from-claude-desktop ...
    add-json ...
    get ...
    help ...
    list ...
    remove ...
    reset-project-choices ...
    serve ...
```

**Finding: `claude mcp ping` subcommand does NOT exist** in the Claude Code CLI version present in this devcontainer. The full subcommand set is `add | add-from-claude-desktop | add-json | get | help | list | remove | reset-project-choices | serve`. **`ping` is not in that set.**

**ADR-0041 FALLBACK APPLIES.** Per ADR-0041 (hybrid install posture), if `claude mcp ping` is absent in the pinned Claude Code Feature version, T3.4 must use **direct JSON-RPC ping** against each MCP server instead of the CLI wrapper.

Concrete impact on Plan tasks:
- **T3.4 (postCreate lifecycle script — install + ping)**: replace `claude mcp ping context7` (and equivalents) with a direct JSON-RPC `tools/list` probe written in bash/node. ADR-0041's fallback section is the canonical reference for the JSON-RPC ping shape.
- **Phase 5 validators (PV-5.C-PING / equivalents, if any)**: re-anchor to the direct JSON-RPC form.
- **AC-X-2 (readiness_probe records)**: unaffected at the AC level — the probe just uses a different mechanism than originally assumed.

**Disposition: PASS-with-fallback.** ADR-0041 covers this case explicitly; no new design change required. The `mcp-events.jsonl` schema (per ADR-0037) is install-mechanism-agnostic; the probe records get emitted whether via `claude mcp ping` or direct JSON-RPC.

**Recorded by:** orchestrator (parent recipe-feature-pipeline; Phase 0 re-verify drive).

---

## §H-7 — Exa CLI --header flag support confirmation (T0.7)

**Verified by:** orchestrator (parent), 2026-05-23T21:18 UTC, via documentation cross-check (live runtime probe deferred to actual postCreate execution).

**Source verification:**
- **Exa MCP server upstream**: `github.com/exa-labs/exa-mcp-server` README documents primary auth as URL-query parameter: `?exaApiKey=YOUR_KEY` against the hosted endpoint `https://mcp.exa.ai/mcp`.
- **No `--header` flag is documented** in the README. The README focuses on per-client config (Cursor, VS Code, Claude Desktop) using URL-query auth.
- **T-006-exa.md research note (F1) records additional info**: The Exa MCP server's auth resolver accepts (in priority order): (1) `exaApiKey` query parameter, (2) `Authorization: Bearer …` header (also accepts JWTs), (3) `EXA_API_KEY` env var (for stdio/npx mode). The `x-api-key` header is documented for the hosted endpoint elsewhere in the docs.

**Tension with our design**: our design (cc-design.md, blueprint-v3, tasks.json T2.4) specifies the Exa entry as `headers: {"x-api-key": "${EXA_API_KEY}"}`. The Exa README primary form is URL-query; our `OP-9` REJECTS URL-query credentials, so we MUST use a header form. T-006 corroborates that `x-api-key` is supported.

**Disposition: PASS with verify-at-postCreate**. The `x-api-key` header form per T-006 F1 is the canonical choice for this design. The postCreate lifecycle ping (T3.4) will probe whether the header is accepted by the hosted endpoint; if it fails with auth-error, the fallback options are:
1. `Authorization: Bearer ${EXA_API_KEY}` per T-006 F1 priority-2.
2. Switch to stdio/npx mode using `EXA_API_KEY` env-var per T-006 F1 priority-3.

URL-query form remains REJECTED per OP-9 regardless. The runtime probe at T3.4 settles which header form lands; the design's `x-api-key` choice is the recommended starting point. If the probe fails, plan-author or a follow-up dispatch updates `.mcp.json` to the Authorization: Bearer form (note: this would conflict with the Context7 SF-F3-AUTH-HEADER-1 resolution where we DROPPED Bearer in favor of canonical CONTEXT7_API_KEY — but Exa's canonical may be different than Context7's).

**Recorded by:** orchestrator (parent recipe-feature-pipeline; Phase 0 re-verify drive).

---

## §D-2 — Placeholder convention canonicalization (T0.8)

**Decision recorded by:** orchestrator (parent), 2026-05-23T21:20 UTC.

**Canonical placeholder string: `<PIN_TBD>`** (per I-DR-003, plan-v1 §D-2).

Applied uniformly across `.mcp.json` (T2.4) and `versions.env` (T1.3) pre-pin sketches. Any pre-pin reference uses `<PIN_TBD>` verbatim. Plan-author's normalization step at task time enforces this convention.

Already-pinned values (e.g., `ACTIONLINT_MCP_SHA=7441fe042c995cbb1bb4b97fce71f9ed3b36d5ef`, `GITNEXUS_TAG=1.6.5`, `TERRAFORM_MCP_VERSION=<from T0.1 result>`) use the actual value, not the placeholder. The placeholder applies ONLY to slots where the pin hasn't been selected yet at the moment of authoring.

**Recorded by:** orchestrator (parent).

---

## §D-4 — Go devcontainer Feature version pin (T0.9)

**Decision recorded by:** orchestrator (parent), 2026-05-23T21:20 UTC.

**Selected Go pin: `ghcr.io/devcontainers/features/go:1` with major version `1.22`.**

Rationale:
- Go 1.22 is the current LTS-equivalent (Go follows N/N-1 support; 1.22 is supported alongside 1.23).
- Era-aligned with Node 20 LTS (both released 2024-Q1 / 2024-Q2 era).
- `1.22` is needed at install time ONLY by `actionlint-mcp` (`go install github.com/hongkongkiwi/actionlint-mcp@${ACTIONLINT_MCP_SHA}`) per Plan T3.4. After install, the resulting binary is on PATH and Go is not needed at runtime.
- Devcontainer Features `ghcr.io/devcontainers/features/go:1` accepts a `version` argument; spec is `{"version": "1.22"}`.

Note: Go is **NOT** installed in this current devcontainer (`which go` returned `command not found`). The Go Feature is added at Phase 3 (devcontainer.json edit at T1.4 referenced for build-time bootstrap; install step at T3.4 invokes `go install` for actionlint-mcp).

**Recorded by:** orchestrator (parent).

---

## §T0.10 — `.claude/runtime/` bootstrap + `.gitignore` update (Q-CC-2)

**Performed by:** orchestrator (parent), 2026-05-23T21:25 UTC.

**Actions:**
1. `mkdir -p .claude/runtime` — directory created
2. `touch .claude/runtime/.gitkeep` — placeholder to keep directory tracked
3. `echo ".claude/runtime/mcp-events.jsonl" >> .gitignore` — runtime jsonl excluded from commits

**Verification:**
- `ls .claude/runtime/` → shows `.gitkeep` (0 bytes)
- `tail .gitignore` → last line is `.claude/runtime/mcp-events.jsonl`

**Disposition: PASS.** Per-Codespace runtime file location ready; the file will be created (and grow) at postStart by `log-mcp-event.sh` (per ADR-0037 / Plan T3.5). It's never committed.

**Recorded by:** orchestrator (parent).

---

## §T5.2 — Cold-cache rebuild smoke (USER-DRIVEN; documented expected outcomes)

**Status**: rebuild-dependent; CANNOT be executed from the parent orchestrator session without disrupting the user's active Codespace. Documented as user-driven exercise per Phase 5 T5.2 contract.

**To execute**: open a fresh Codespace from the feature branch (or `Codespaces: Rebuild Container` in VS Code command palette). Observe:

| Expected observation | Acceptance criterion |
|---|---|
| Features install clean: Node 20, Go 1.22, common-utils, github-cli, claude-code | AC-CS-5 (devcontainer.json builds clean) |
| postCreate.sh runs to completion | AC-CS-1 (postCreate idempotent) |
| 5 `install_complete` JSONL records appear in `.claude/runtime/mcp-events.jsonl` (one per OSS-local server: serena, mcp-openapi-schema, actionlint-mcp, terraform-mcp, gitnexus) | AC-X-2 (5 install records) |
| GitNexus install completes without C++ toolchain compilation (per Phase 0 §H-4 verify-at-execution result; prebuilds for linux-x64 used) | AC-CS-9 wrapping intent |
| postStart.sh runs to completion | AC-CS-2 (postStart idempotent) |
| 7 `readiness_probe` JSONL records appear (one per `.mcp.json` server entry) | AC-X-2 (7 readiness records) |
| `claude mcp list` shows the 7 named servers | AC-FR-1-a |
| Cold-cache rebuild completes ≤~10 min (NFR-1-a target; ~7-12 min envelope per Codespaces-design rebuild-time estimate) | AC-NFR-1-a |

**Recommended invocation**:

```bash
# After Codespace rebuild completes:
claude mcp list   # should show 7 servers
jq 'select(.event == "install_complete") | .server' .claude/runtime/mcp-events.jsonl | sort -u
# Expect: actionlint-mcp, gitnexus, mcp-openapi-schema, serena, terraform-mcp (5 servers)
jq 'select(.event == "readiness_probe") | .server' .claude/runtime/mcp-events.jsonl | sort -u | wc -l
# Expect: 7
```

**Recorded outcome**: TO BE FILLED by user after rebuild.

---

## §T5.3 — Warm-cache rebuild smoke (USER-DRIVEN; documented expected outcomes)

**Status**: rebuild-dependent; same constraints as §T5.2.

**To execute**: after §T5.2 cold-cache completes, do a second rebuild without sentinel deletion (or trigger Codespace stop+resume). Observe:

| Expected observation | Acceptance criterion |
|---|---|
| postCreate.sh short-circuits per AC-CS-2: 5 `install_complete` records each note "sentinel present; install skipped" | AC-CS-2 (sentinel+binary-presence idempotency) |
| Warm-cache rebuild completes ≤~2 min | AC-NFR-1-b |
| postStart.sh re-runs and writes 7 fresh `readiness_probe` records | AC-X-2 (postStart is per-cycle, not idempotent on the JSONL — each cycle appends 7 new records) |

**Recorded outcome**: TO BE FILLED by user after second rebuild.

---

## §T5.4 — auditing-mcp Gate-6 hard-gate exercise (EXECUTED; PASS)

**Status**: EXECUTED in-session by orchestrator (parent recipe-feature-pipeline), 2026-05-23T22:00 UTC. Full audit + seeded-BLOCKER simulation performed against the live repo state.

**Step 1 — Clean repo audit**:
```
python3 .claude/skills/auditing-mcp/scripts/audit_mcp.py .mcp.json
```
Result: exit 0; 3 total findings; 0 BLOCKER / 0 MAJOR / 3 MINOR (the 3 MINORs are MC-3 known-publishers advisory: `gitnexus@${GITNEXUS_TAG}`, `mcp-openapi-schema@${MCP_OPENAPI_SCHEMA_VERSION}`, and a third advisory). MINORs do NOT trip the ADR-0043 hard gate. **Hard-gate verdict: PROCEED**.

**Step 2 — 10 OP rules dispatched cleanly**:
- audit_op1_env_block_coverage.py: 0B / 0M / 0other
- audit_op2_consumer_mapping.py: 0B / 0M / 0other
- audit_op3_zero_mcp_invariant.py: 0B / 0M / 0other
- audit_op4_primary_fallback_prose.py: 0B / 0M / 0other
- audit_op5_lifecycle_completeness.py: 0B / 0M / 0other
- audit_op6_runtime_log_redaction.py: 0B / 0M / 0other
- audit_op7_events_schema.py: 0B / 0M / 0other
- audit_op8_gitnexus.py: 0B / 0M / 0other
- audit_op9_url_credential_rejection.py: 0B / 0M / 0other
- audit_op10_argv_leakage.py: 0B / 0M / 0other

**Step 3 — Seeded-BLOCKER simulation (LIVE exercise of ADR-0043 hard gate)**:

Seed: temporarily added `?apiKey=sk-TESTPOISON1234567890abcd` to context7's URL (OP-9 trigger).

Result:
- OP-9 detected: `[BLOCKER] credential-shaped query parameter: apiKey (server: context7)`
- `audit_mcp.py` exit code: **1**
- **Hard-gate verdict: HALT**

**Step 4 — cleanup_required**: `.mcp.json` restored from backup; grep confirms zero `TESTPOISON` residual; post-cleanup `audit_mcp.py` run returns to 0 BLOCKER. **Seeded credential NEVER committed.**

**Defect found and fixed during T5.4 execution**:
- `validate_mcp_config.py` did not recognize `transport: "http"` (the field name in our `.mcp.json`); it was checking `server["type"]` only, defaulting to `"stdio"` which then demanded a missing `command`. Two false-positive BLOCKERs (context7, exa).
- Fix (one-line): `server_type = server.get("type") or server.get("transport") or "stdio"`.
- `audit_mcp.py` did not dispatch the new OP-1..OP-10 scripts. Fixed by wiring in 10 dispatch calls + a BLOCKER exit-code semantic (exit 1 on any BLOCKER per ADR-0043). After fix, the orchestrator-level audit correctly halts on seeded-BLOCKER scenarios.

**Conclusion**: ADR-0043 hard-gate semantics now work end-to-end. Gate-6 phase-validator can rely on `audit_mcp.py` exit code as the HALT/PROCEED signal.

---

## §T5.5 — Failure-mode rehearsals (USER-DRIVEN; documented expected outcomes)

**Status**: rebuild-dependent; requires actual MCP server invocations (some failure modes require a live devcontainer with active MCP servers). Documented as user-driven exercises.

### Rehearsal 1 — Unset `CONTEXT7_API_KEY` (AC-X-1 + AC-FR-5-b)

Unset the Codespaces secret before postStart. Expected:
- postStart's `readiness_probe` record for `context7`: `result: "fail"`, `failure_layer: "auth"`, `message_redacted` includes `"missing env-var CONTEXT7_API_KEY"` or HTTP 401.
- Stderr banner (per ADR-0037): one-line, names the server, points at the JSONL.

### Rehearsal 2 — Shadow `terraform-mcp` off PATH (AC-FR-1-c)

Move `terraform-mcp` binary out of PATH. Expected:
- postStart's `readiness_probe` record for `terraform-mcp`: `result: "fail"`, `failure_layer: "transport"`, `message_redacted: "command not found: terraform-mcp"`.
- Stderr banner: `[mcp:terraform-mcp] primary degraded → falling back to <no fallback>; see .claude/runtime/mcp-events.jsonl`.

### Rehearsal 3 — GitNexus stdio crash mid-session (AC-FR-9-a/b/c)

Kill the GitNexus stdio process (or trigger an OOM scenario). Expected:
- Next `discovery-codebase-researcher` invocation: GitNexus call fails → `structured_failure` record emitted with `primary_degraded: true`, `fallback_invoked: false` (no fallback registered per Gate-4 OI-1), `failure_layer: "transport"`.
- Banner emitted per ADR-0037.

### Rehearsal 4 — Redaction smoke-test (AC-NFR-2-d)

Send a credential-shaped string through `log-mcp-event.sh` directly:
```bash
echo '{"event":"structured_failure","server":"test","message":"saw sk-FAKE1234567890abcdef in payload"}' | \
  bash .devcontainer/lib/log-mcp-event.sh --stdin
tail -1 .claude/runtime/mcp-events.jsonl | jq .
```
Expected:
- `sk-FAKE1234567890abcdef` substring replaced with `<REDACTED:sk-key>` in the JSONL record.
- Record carries `"redaction_applied": true`.

**Recorded outcomes**: TO BE FILLED by user after rebuild + manual rehearsal sequence.

---

## §OI-4 — Per-agent context-overhead measurement (T4.7)

**Measured by:** orchestrator (parent), 2026-05-23T21:50 UTC, post Phase 4 T4.1 (agent allowlist edits) + T2.4 (`.mcp.json` at repo root).

### Measurement methodology

Per cc-design Principle 1 + ADR-0030: MCP tool schemas are deferred until invoked. So the session-startup context overhead from MCP registration is:

1. **`.mcp.json` shared cost** — the file is loaded once per session for the 7-server inventory.
2. **Per-agent tools-line cost** — each agent's frontmatter `tools:` line gains `mcp__<server>__<tool>` entries (strings, not schemas).

### Numbers

| Metric | Value |
|---|---|
| `.mcp.json` size | 1,018 bytes (~254 tokens approx) |
| Total agents | 36 |
| Touched (with mcp__ entries) | 8 |
| Untouched (preserving C-0445) | 28 |
| Total `mcp__` entries across all touched agents | 19 |
| Avg entries per touched agent | 2.4 |
| Sum of tools-line bytes (touched only) | 1,078 bytes (~270 tokens approx) |

### Per-agent breakdown (touched)

| Agent | mcp__ entries | tools-line chars |
|---|---|---|
| design-cicd | 5 | 150 |
| discovery-external-researcher | 5 | 221 |
| design-iac | 2 | 79 |
| discovery-codebase-researcher | 2 | 200 |
| review-architecture-auditor | 2 | 200 |
| design-api | 1 | 84 |
| design-claude-code | 1 | 72 |
| design-codespaces | 1 | 72 |

### NFR-4 disposition

PRD NFR-4 envelope (per blueprint): per-agent context overhead from MCP registration must stay within tolerable bounds. The measurement shows:

- `.mcp.json` (~254 tokens) is well below any reasonable session-startup envelope.
- Per-agent tools-line addition is 10–100 chars (~3–25 tokens), trivial per agent.
- Tool SCHEMAS are NOT loaded at session-startup per Principle 1 — they're deferred to invocation time. So the heavy cost (the actual schema definitions per tool) is consumed only when an agent invokes a specific mcp__server__tool, not on every agent activation.

**Result: PASS.** Per-agent context overhead is well within tolerable bounds. NFR-4 envelope NOT breached. No downscoping re-scope is needed.

**Caveat for future feature**: if a future feature registers additional MCP servers (e.g., the codebase-memory-mcp fallback that the current Gate-4 OI-1 closure dropped), the `.mcp.json` file size grows. At 7 servers / ~250 tokens, the per-server marginal cost is ~35 tokens. Adding 1-2 more servers would still keep the file under 400 tokens. Beyond that, re-measure.

**Recorded by:** orchestrator (parent recipe-feature-pipeline; Phase 4 T4.7 measurement drive).
