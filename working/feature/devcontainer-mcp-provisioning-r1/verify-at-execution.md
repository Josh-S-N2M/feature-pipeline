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

---

## §H-6 — `claude mcp ping` CLI presence confirmation (T0.6)

<!-- T0.6: replace this comment block with section content -->

---

## §H-7 — Exa CLI --header flag support confirmation (T0.7)

<!-- T0.7: replace this comment block with section content -->

---

## §D-2 — Placeholder convention canonicalization (T0.8)

<!-- T0.8: replace this comment block with section content -->

---

## §D-4 — Go devcontainer Feature version pin (T0.9)

<!-- T0.9: replace this comment block with section content -->

---

## §OI-4 — Per-agent context-overhead measurement (T4.7)

<!-- T4.7: replace this comment block during Phase 4 -->
