---
id: research-note-T-001
version: 1.0.0
status: draft
generated: 2026-05-25T00:00:00Z
generated_by: discovery-external-researcher
feature: pipeline-quickwins-hardening-r1
topic_id: T-001
pinned_tag: gitnexus@1.6.5
---

# T-001 — GitNexus optional-grammar-skip env-var contract

## Topic and question

**Topic name (verbatim):** GitNexus optional-grammar-skip env-var contract.

**Research question (verbatim):** At the GitNexus tag currently pinned in `.devcontainer/versions.env`, what specifically does `GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1` cause the install to do (and to NOT do — particularly the C++/tree-sitter toolchain path) — such that a dry-run can make a positive assertion that the contract still holds rather than relying on absence-of-error?

**Pinned tag (confirmed from `.devcontainer/versions.env` line 36):** `GITNEXUS_TAG=1.6.5` → npm `gitnexus@1.6.5`, GitHub tag `v1.6.5` on `abhigyanpatwari/GitNexus`.

## Executive summary

At `gitnexus@1.6.5` the env-var contract is implemented by **two explicit early-exit guards** in the package's `postinstall` hook (`scripts/build-tree-sitter-dart.cjs` and `scripts/build-tree-sitter-proto.cjs`). Both scripts perform a **strict `=== '1'` string comparison** against `process.env.GITNEXUS_SKIP_OPTIONAL_GRAMMARS`, and on match they `process.exit(0)` after a stable, prefixed warning to stderr. The contract is therefore observable in three positive ways at the same time: the prefixed log lines appear, the per-grammar compiled artifacts (`*_binding.node`) are absent under `node_modules/tree-sitter-{dart,proto}/build/Release/`, and `node-gyp rebuild` is never invoked. Two important nuances: (1) the README also lists `tree-sitter-swift` among the skipped grammars, but at v1.6.5 the postinstall hook only enumerates `build-tree-sitter-dart.cjs && build-tree-sitter-proto.cjs` — Swift's build is governed by **npm's intrinsic `optionalDependencies` failure-tolerance**, not by the env var; (2) the env var's strict-string semantics mean any value other than the literal `1` (e.g., `true`, `yes`, `01`) falls through to the rebuild — this is documented behavior, not a bug.

## Findings

### F-1 — The env-var guard lives in `scripts/build-tree-sitter-dart.cjs` lines 5–14

**Claim.** At tag `v1.6.5`, the `gitnexus/` package's `postinstall` hook is defined in `package.json` as `node scripts/build-tree-sitter-dart.cjs && node scripts/build-tree-sitter-proto.cjs`. The first script checks `process.env.GITNEXUS_SKIP_OPTIONAL_GRAMMARS === '1'` at line 9 and, on match, prints `[tree-sitter-dart] Skipping build (GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1). Dart parsing will be unavailable until reinstalled without the env var.` to stderr and `process.exit(0)` at line 13.

**Source.** `abhigyanpatwari/GitNexus` at tag `v1.6.5`, file `gitnexus/scripts/build-tree-sitter-dart.cjs`, lines 5–14. Raw file URL: `https://raw.githubusercontent.com/abhigyanpatwari/GitNexus/v1.6.5/gitnexus/scripts/build-tree-sitter-dart.cjs`.

**Quote (≤15 words).** "Strict `=== '1'` only — '=true', '=yes', '=0' (read as a string)" (comment, line 7).

**Confidence.** High — direct read of the upstream source at the pinned tag.

**Caveats.** Tag-pinned at v1.6.5; line numbers will drift on future versions. Future versions may rename the script or change the comparison.

### F-2 — The same guard pattern is repeated in `scripts/build-tree-sitter-proto.cjs` lines 28–34

**Claim.** The proto builder duplicates the strict `=== '1'` check at lines 28–34, prints `[tree-sitter-proto] Skipping build (GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1). Proto parsing will be unavailable until reinstalled without the env var.` and exits 0. This redundancy is by design: the two scripts run sequentially (`&&` chained in the `postinstall` line), so either one's failure or skip is independent.

**Source.** `abhigyanpatwari/GitNexus` at tag `v1.6.5`, file `gitnexus/scripts/build-tree-sitter-proto.cjs`, lines 28–34. Raw URL: `https://raw.githubusercontent.com/abhigyanpatwari/GitNexus/v1.6.5/gitnexus/scripts/build-tree-sitter-proto.cjs`.

**Confidence.** High — direct read of upstream source at the pinned tag.

**Caveats.** None at this tag. Future maintainers could factor the check into a shared helper; the dry-run must not assume the literal text.

### F-3 — Without the guard tripped, both scripts invoke `npx node-gyp rebuild`

**Claim.** When the env-var is NOT set (or is set to any non-`'1'` value), `build-tree-sitter-dart.cjs` reaches line 39 and executes `execSync('npx node-gyp rebuild', { cwd: dartDir, stdio: 'pipe', timeout: 180000 })`. `build-tree-sitter-proto.cjs` does the equivalent at line 68. `node-gyp rebuild` is the C++-toolchain entry point that fans out to `python3`, `make`, and `g++` (or platform equivalents).

**Source.** `gitnexus/scripts/build-tree-sitter-dart.cjs` line 39, and `gitnexus/scripts/build-tree-sitter-proto.cjs` line 68, both at tag `v1.6.5`.

**Quote (≤15 words).** *(One quote per source already used in F-1; this finding paraphrases.)*

**Confidence.** High — direct read.

**Caveats.** `node-gyp` itself dispatches to platform toolchains; the literal binaries observed (`cc`, `g++`, `make`, `python3`) depend on the host. Absence of `node-gyp` in the process tree is itself a strong positive signal.

### F-4 — Swift handling is governed by npm's `optionalDependencies` tolerance, NOT by the env var, at v1.6.5

**Claim.** `gitnexus@1.6.5`'s `package.json` lists `tree-sitter-dart`, `tree-sitter-kotlin`, `tree-sitter-proto`, and `tree-sitter-swift` under `optionalDependencies`. The `postinstall` script in `package.json` only references the dart and proto builders — there is no `build-tree-sitter-swift.cjs` invocation in the hook line. The README's "Faster install" section states the env-var skips Dart/Proto/Swift, but at v1.6.5 the Swift outcome is independent: npm's intrinsic behavior for `optionalDependencies` is to tolerate prebuild/install failures silently, so `tree-sitter-swift`'s build will already proceed to failure-tolerated-skip on a host without a working C++ toolchain regardless of the env var. (Upstream issue #1024, opened 2026-04-22, documents exactly this: `tree-sitter-swift@0.6.0`'s `binding.gyp` is malformed and never compiles successfully; the in-tree workaround `scripts/patch-tree-sitter-swift.cjs` is referenced but is NOT invoked by the v1.6.5 postinstall hook.)

**Source.** Upstream `package.json` at `https://raw.githubusercontent.com/abhigyanpatwari/GitNexus/v1.6.5/gitnexus/package.json` (postinstall and optionalDependencies fields). README at `https://raw.githubusercontent.com/abhigyanpatwari/GitNexus/main/README.md` (Environment variables section). Issue #1024 at `https://github.com/abhigyanpatwari/GitNexus/issues/1024` (closed as not-planned; opened by user `zenprocess` 2026-04-22).

**Quote (≤15 words).** "postinstall: node scripts/build-tree-sitter-dart.cjs && node scripts/build-tree-sitter-proto.cjs" — `package.json`, scripts field at v1.6.5.

**Confidence.** High for the script-list (read directly); medium for the inference about Swift's npm-side behavior (Swift binding is not explicitly proved to be unbuilt in the dry-run; it's documented as failure-tolerated by issue #1024 and by npm's optionalDependencies contract).

**Caveats.** The README and the actual postinstall hook **diverge on Swift**. The README claims the env var skips Swift; the code claims it skips Dart + Proto. A dry-run that asserts "Swift was not built because GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1" would be technically false even though Swift typically IS unbuilt for the unrelated reason above. The dry-run should assert what the env var actually gates (Dart + Proto) and treat Swift as a separate concern.

### F-5 — Per-grammar artifacts have known on-disk paths that are absent when the guard trips

**Claim.** When the dart guard trips, the path `<global node_modules root>/gitnexus/node_modules/tree-sitter-dart/build/Release/tree_sitter_dart_binding.node` is never created (because `node-gyp rebuild` never runs). The dart script computes this exact path at line 17. The proto equivalent is `<...>/tree-sitter-proto/build/Release/tree_sitter_proto_binding.node`. These are positive-assertion targets: a dry-run can stat these paths and verify their non-existence.

**Source.** `gitnexus/scripts/build-tree-sitter-dart.cjs` line 17 (path construction), and the symmetric path in `build-tree-sitter-proto.cjs`.

**Confidence.** High — paths are computed by the build script and emitted by `node-gyp` per `node-gyp`'s deterministic output layout.

**Caveats.** The literal path under `<global node_modules root>` depends on the npm prefix (e.g., `/usr/local/lib/node_modules/...` vs `~/.nvm/versions/node/<v>/lib/node_modules/...`). The dry-run must derive the location from `npm root -g` rather than hard-coding.

### F-6 — Documented purpose: "no C++ toolchain needed" — the env-var's contract is about toolchain abstinence, not just speed

**Claim.** The README explicitly frames the env-var as a toolchain-abstinence flag, not merely a speedup. Skipping the Dart and Proto rebuilds eliminates the only places `gitnexus@1.6.5`'s postinstall would invoke `node-gyp rebuild`, which is the entry point that transitively requires `python3`, `make`, and `g++`.

**Source.** README at `https://raw.githubusercontent.com/abhigyanpatwari/GitNexus/main/README.md`, "Quick Start" and "Environment variables" sections (line-anchored at `main` since the README at v1.6.5 carries the same documentation).

**Quote (≤15 words).** "set `GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1` … skip vendored grammar materialize/build" (README, Quick Start).

**Confidence.** High — direct read of upstream README.

**Caveats.** README and CHANGELOG at v1.6.5 don't enumerate the env var (the CHANGELOG entry for v1.6.5 covers Docker-runtime image, ca-certificates, duckdb installer — not grammar gating, which was introduced earlier and is stable at this tag). README on `main` is authoritative for current text; the env-var has been a stable contract since prior tags.

## Synthesis (analyst judgment — explicitly flagged)

The contract is observable through **three independent positive signals** plus a negative one. A dry-run that asserts all four is forward-stable against most plausible drift modes:

1. **Stderr signal (positive).** Each builder emits a prefixed warning containing the literal substring `GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1`. The prefixes `[tree-sitter-dart]` and `[tree-sitter-proto]` are stable. Asserting BOTH prefixes appear is a positive, idempotent test.
2. **Process-tree signal (negative-as-positive).** `node-gyp` is never invoked. The dry-run can capture the process tree (e.g., via `strace -f -e trace=execve` or by polling `pgrep`) and assert no descendant of the `npm install` process has argv starting with `node-gyp` or descends to `cc1plus` / `g++`. This is the absence assertion the topic warns about — defensible only when paired with assertions 1 and 3.
3. **Artifact-absence signal (positive).** After install, `npm root -g`/`gitnexus/node_modules/tree-sitter-dart/build/Release/tree_sitter_dart_binding.node` does NOT exist; same for the proto path. This is positive because the dry-run is asserting a known path is absent — different from "no error occurred."
4. **Wall-clock signal (positive, weak).** The install completes in seconds rather than minutes. Useful as a sanity check but not load-bearing: future versions might cache the prebuilt `.node` files or add unrelated slow steps. Recommend NOT making this the only positive assertion.

**Strongest combination:** assert (1) prefix appears in stderr AND (3) artifact path is absent. (1) alone is too literal-string-fragile across upstream changes; (3) alone could be true for other reasons (the optional dep itself was rejected by npm). Both together pin down that the guard ran AND prevented the artifact.

**On Swift.** The dry-run should NOT assert anything about Swift via this env-var. The README is misleading at v1.6.5 (script-level reality only covers Dart and Proto). If Swift coverage matters to the dry-run, treat it as a separate observation: "tree-sitter-swift's binding.gyp is malformed at the pinned tag; its build is failure-tolerated by npm regardless of env-var state per upstream issue #1024."

## Acceptance-criteria check

### AC-1 — Specific code path / install step the env-var gates, with file/line citation

**Disposition: satisfied.**

- `package.json` at `https://raw.githubusercontent.com/abhigyanpatwari/GitNexus/v1.6.5/gitnexus/package.json`, scripts field: `"postinstall": "node scripts/build-tree-sitter-dart.cjs && node scripts/build-tree-sitter-proto.cjs"`.
- `scripts/build-tree-sitter-dart.cjs` lines 5–14 — strict-string env-var guard with `process.exit(0)`.
- `scripts/build-tree-sitter-proto.cjs` lines 28–34 — symmetric guard.
- Both at tag `v1.6.5`.

### AC-2 — At least two observable signals, ≥1 positive

**Disposition: satisfied. Four signals identified; three are positive.**

1. **Positive — stderr substring.** Both `[tree-sitter-dart] Skipping build (GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1)` and `[tree-sitter-proto] Skipping build (GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1)` appear in the install output.
2. **Positive — known-path absence.** `${npm_root_g}/gitnexus/node_modules/tree-sitter-dart/build/Release/tree_sitter_dart_binding.node` is absent; same for the proto path. (Positive in the sense that the dry-run asserts a specific known path; not "an error didn't occur.")
3. **Negative — process-tree.** No `node-gyp` / `cc1plus` / `g++` descendant of the install process. Use as corroboration, not as sole assertion.
4. **Positive — wall-clock bound.** Install completes well under the "rebuild" baseline (typically <30s on a clean prefix at the pinned tag vs. minutes). Weak signal, defensible only as corroboration.

**Recommended dry-run combination:** assert (1) AND (2). That pair is forward-stable against the most likely drift modes (see AC-3 / Drift modes).

### AC-3 — At least one drift mode

**Disposition: satisfied. Four drift modes identified.**

- **DM-1 (most likely).** Upstream factors the env-var check into a shared helper or shifts the literal warning text. The exact log substring `[tree-sitter-dart] Skipping build (GITNEXUS_SKIP_OPTIONAL_GRAMMARS=1)` changes — dry-runs that pattern-match on the full sentence break, but those that pattern-match on the env-var name + a "Skipping" verb still pass. Mitigation: regex on `GITNEXUS_SKIP_OPTIONAL_GRAMMARS.*[Ss]kip` rather than the full literal.
- **DM-2 (medium likelihood).** Upstream adds a third optional grammar (e.g., Kotlin, currently in `optionalDependencies` but with no postinstall builder) and forgets to gate it on the env var. The contract silently degrades: env-var honored for Dart/Proto, but a new grammar builds anyway. Mitigation: enumerate the postinstall script set at install time and warn if it grows.
- **DM-3 (medium likelihood, drift toward removal).** Upstream removes `tree-sitter-dart` or `tree-sitter-proto` entirely (per the same pattern as issue #1024's Swift removal proposal). The builder script vanishes; the env-var becomes silently meaningless. Mitigation: assert that at least one of the two known scripts exists at the pinned tag before invoking install, otherwise the env-var contract is hollow.
- **DM-4 (low likelihood, latent).** Upstream loosens the comparison from `=== '1'` to truthy-checking. Currently anything other than literal `'1'` falls through to rebuild; if loosened, `=true` etc. would skip. Not destructive to the dry-run's positive assertions, but changes the contract's edge behavior. Mitigation: assert the negative — set the env-var to `0` AND verify the artifact IS built — as a calibration step.

## Open questions

- **Q-1 — Does `tree-sitter-kotlin` ship a prebuild?** v1.6.5's `optionalDependencies` includes Kotlin, but no `build-tree-sitter-kotlin.cjs` is referenced in the postinstall. Whether Kotlin's upstream tarball is prebuilt-binary-shipping (so no toolchain needed) or relies on npm's lifecycle scripts to rebuild — not determined from the sources read. Out of scope for the dry-run's env-var-contract question, but worth flagging for KB-mcp-platform completeness.
- **Q-2 — Is the README scheduled to be reconciled with code on Swift?** Issue #1024 (closed not-planned) suggests no near-term removal of `tree-sitter-swift` from optionalDependencies, but the README's claim that the env-var skips Swift remains inaccurate at v1.6.5. Whether maintainers consider this an upstream docs bug or intentional simplification is unclear from the sources.

## Source list

1. **upstream package.json at the pinned tag** — `https://raw.githubusercontent.com/abhigyanpatwari/GitNexus/v1.6.5/gitnexus/package.json` — defines the `postinstall` hook and `optionalDependencies` set. Read 2026-05-25.
2. **upstream `build-tree-sitter-dart.cjs` at the pinned tag** — `https://raw.githubusercontent.com/abhigyanpatwari/GitNexus/v1.6.5/gitnexus/scripts/build-tree-sitter-dart.cjs` — lines 5–14 contain the strict-string env-var guard. Read 2026-05-25.
3. **upstream `build-tree-sitter-proto.cjs` at the pinned tag** — `https://raw.githubusercontent.com/abhigyanpatwari/GitNexus/v1.6.5/gitnexus/scripts/build-tree-sitter-proto.cjs` — lines 28–34 contain the symmetric guard. Read 2026-05-25.
4. **upstream README** — `https://raw.githubusercontent.com/abhigyanpatwari/GitNexus/main/README.md` — "Quick Start" and "Environment variables" sections document the env var's intent. Read 2026-05-25. (Note: README is on `main`; the documented contract is stable at v1.6.5 per directory listing of `gitnexus/README.md` at that tag.)
5. **upstream CHANGELOG at the pinned tag** — `https://raw.githubusercontent.com/abhigyanpatwari/GitNexus/v1.6.5/gitnexus/CHANGELOG.md` — v1.6.5 entry (Docker runtime image, ca-certificates, duckdb installer); env-var gating is not new in this release and is therefore not re-mentioned here. Read 2026-05-25.
6. **upstream issue #1024** — `https://github.com/abhigyanpatwari/GitNexus/issues/1024` — "Drop tree-sitter-swift — fails to build on Debian/musl…"; opened 2026-04-22 by `zenprocess`, closed not-planned. Documents that tree-sitter-swift@0.6.0's binding.gyp is malformed and that the in-tree `patch-tree-sitter-swift.cjs` is a workaround. Read 2026-05-25.
7. **upstream repo file listing at the pinned tag** — `https://github.com/abhigyanpatwari/GitNexus/tree/v1.6.5/gitnexus` — confirms presence of `scripts/`, `vendor/`, `.npmignore`, and the `gitnexus/` sub-package layout. Read 2026-05-25.
